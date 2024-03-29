from airflow.contrib.operators.ssh_operator import SSHOperator
from airflow.models import Variable
from airflow.providers.sftp.sensors.sftp import SFTPSensor
from airflow.sensors.sql import SqlSensor
from airflow.models.connection import Connection
from airflow import settings

from urllib.parse import urlparse
from utils import get_aws_credentials, get_tables_to_process

import os
import json


def get_cat_command(vars, table):
    output = vars["outputs"][table]
    if output[-1] == "/":
        command = f"cat {output}*.csv | wc -l"
    else:
        command = f"cat {output}/*.csv | wc -l"

    return command


def psql_populate_db_config(vars):
    session = settings.Session()
    conn = session.query(Connection).filter(Connection.conn_id == "ztf_db").first()
    parsed = urlparse(conn.get_uri())
    vars["db"]["user"] = parsed.username
    vars["db"]["password"] = parsed.password
    vars["db"]["host"] = parsed.hostname
    vars["db"]["port"] = parsed.port
    vars["db"]["dbname"] = parsed.path[1:]


def get_create_csv_tasks(dag):
    psql_load_vars = Variable.get("load_psql_config", deserialize_json=True)
    aws_access_key, aws_secret_access_key, aws_session_token = get_aws_credentials(
        "aws_connection"
    )
    execute_create_csv = SSHOperator(
        task_id="launch_create_csv",
        ssh_conn_id="reuna_connection",
        command="reuna_create_csv_template.sh",
        environment={
            "AWS_ACCESS_KEY_ID": aws_access_key,
            "AWS_SECRET_ACCESS_KEY": aws_secret_access_key,
            "AWS_SESSION_TOKEN": aws_session_token,
        },
        params={
            "virtualenv": psql_load_vars.get("virtualenv", False),
            "vars": json.dumps(psql_load_vars),
            "aws_access_key": aws_access_key,
            "aws_secret_access_key": aws_secret_access_key,
            "aws_session_token": aws_session_token,
        },
        dag=dag,
    )

    tables = get_tables_to_process(psql_load_vars)
    sensors = []
    for table in tables.keys():
        success_path = os.path.join(psql_load_vars["outputs"][table], "_SUCCESS")
        create_csv_sensor = SFTPSensor(
            task_id=f"check_{table}_csv_created",
            sftp_conn_id="reuna_ftp_connection",
            path=success_path,
            dag=dag,
        )
        sensors.append(create_csv_sensor)
        execute_create_csv >> create_csv_sensor

    return [execute_create_csv, *sensors]


def get_psql_copy_csv_tasks(dag):
    psql_load_vars = Variable.get("load_psql_config", deserialize_json=True)
    psql_populate_db_config(psql_load_vars)
    aws_access_key, aws_secret_access_key, aws_session_token = get_aws_credentials(
        "aws_connection"
    )
    execute_copy_csv = SSHOperator(
        task_id="launch_psql_copy_csv",
        ssh_conn_id="reuna_connection",
        command="reuna_copy_csv_template.sh",
        environment={
            "AWS_ACCESS_KEY_ID": aws_access_key,
            "AWS_SECRET_ACCESS_KEY": aws_secret_access_key,
            "AWS_SESSION_TOKEN": aws_session_token,
        },
        params={
            "virtualenv": psql_load_vars.get("virtualenv", False),
            "vars": json.dumps(psql_load_vars),
            "aws_access_key": aws_access_key,
            "aws_secret_access_key": aws_secret_access_key,
            "aws_session_token": aws_session_token,
        },
        dag=dag,
    )
    tables = get_tables_to_process(psql_load_vars)
    sql_count_tasks = []
    csv_count_tasks = []
    for table in tables:
        cat_command = get_cat_command(psql_load_vars, table)
        count_csv_tuples = SSHOperator(
            task_id=f"count_csv_tuples_{table}",
            ssh_conn_id="reuna_connection",
            command=cat_command,
            do_xcom_push=True,
            dag=dag,
        )
        csv_count_tasks.append(count_csv_tuples)
        count_psql_tuples = SqlSensor(
            task_id=f"count_sql_tuples_{table}",
            conn_id="ztf_db",
            sql="sql_count_command.sql",
            params={"table": table, "task_name": f"count_csv_tuples_{table}"},
            fail_on_empty=False,
            timeout=60 * 60,
            dag=dag,
        )
        sql_count_tasks.append(count_psql_tuples)
        execute_copy_csv >> count_csv_tuples >> count_psql_tuples


def get_process_csv_tasks(dag):
    psql_load_vars = Variable.get("load_psql_config", deserialize_json=True)
    psql_populate_db_config(psql_load_vars)
    aws_access_key, aws_secret_access_key, aws_session_token = get_aws_credentials(
        "aws_connection"
    )
    execute_process_csv = SSHOperator(
        task_id="launch_process_csv",
        ssh_conn_id="reuna_connection",
        command="reuna_process_csv_template.sh",
        environment={
            "AWS_ACCESS_KEY_ID": aws_access_key,
            "AWS_SECRET_ACCESS_KEY": aws_secret_access_key,
            "AWS_SESSION_TOKEN": aws_session_token,
        },
        params={
            "virtualenv": psql_load_vars.get("virtualenv", False),
            "vars": json.dumps(psql_load_vars),
            "aws_access_key": aws_access_key,
            "aws_secret_access_key": aws_secret_access_key,
            "aws_session_token": aws_session_token,
        },
        dag=dag,
    )

    tables = get_tables_to_process(psql_load_vars)
    for table in tables.keys():
        success_path = os.path.join(psql_load_vars["outputs"][table], "_SUCCESS")
        create_csv_sensor = SFTPSensor(
            task_id=f"check_{table}_csv_created",
            sftp_conn_id="reuna_ftp_connection",
            path=success_path,
            dag=dag,
        )
        execute_process_csv >> create_csv_sensor

        cat_command = get_cat_command(psql_load_vars, table)
        count_csv_tuples = SSHOperator(
            task_id=f"count_csv_tuples_{table}",
            ssh_conn_id="reuna_connection",
            command=cat_command,
            do_xcom_push=True,
            dag=dag,
        )
        count_psql_tuples = SqlSensor(
            task_id=f"count_sql_tuples_{table}",
            conn_id="ztf_db",
            sql="sql_count_command.sql",
            parameters={"table": table},
            fail_on_empty=False,
            timeout=60 * 60,
            dag=dag,
        )
        create_csv_sensor >> count_csv_tuples >> count_psql_tuples
