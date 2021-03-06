from abc import ABC, abstractmethod
from load_psql.table_data import (
    DetectionTableData,
    ObjectTableData,
    NonDetectionTableData,
    SSTableData,
    DataQualityTableData,
    MagstatsTableData,
    PS1TableData,
    GaiaTableData,
    ReferenceTableData,
    AllwiseTableData,
    XmatchTableData,
    FeatureTableData,
    ProbabilityTableData
)
from pyspark.sql import SparkSession, DataFrame
import glob
import psycopg2
from multiprocessing import Pool, cpu_count
from pathlib import Path


def execute_copy(file, config, table_name):
    # logging.info(f"Copying {file}")
    con = psycopg2.connect(**config)
    fileName = open(file)
    cursor = con.cursor()
    cursor.copy_from(fileName, table_name, sep=",", null="")
    con.commit()
    con.close()
    fileName.close()


class CSVLoader(ABC):
    def __init__(self, source: str, read_args: dict):
        self.source = source
        self.read_args = read_args

    @abstractmethod
    def create_table_data(self, spark_session, source: str, read_args: dict):
        pass

    def save_csv(
        self,
        spark_session: SparkSession,
        output_path: str,
        n_partitions: int,
        max_records_per_file: int,
        mode: str,
        column_list: list,
        *args,
        **kwargs,
    ) -> None:
        tabledata = self.create_table_data(spark_session, self.source, self.read_args)
        selected_data = tabledata.select(column_list=column_list, *args, **kwargs)
        tabledata.save(
            output_dir=output_path,
            selected=selected_data,
            n_partitions=n_partitions,
            max_records_per_file=max_records_per_file,
            mode=mode,
        )

    @classmethod
    def psql_load_csv(cls, csv_path: str, config: dict, table_name: str) -> None:
        names = glob.glob(csv_path + "/*")
        with Pool(cpu_count()) as p:
            p.starmap(execute_copy, [(file, config, table_name) for file in names])


class DetectionsCSVLoader(CSVLoader):
    def create_table_data(
        self, spark_session: SparkSession, source: str, read_args: dict
    ) -> DetectionTableData:
        return DetectionTableData(spark_session, source=source, read_args=read_args)


class ObjectsCSVLoader(CSVLoader):
    def create_table_data(
        self, spark_session: SparkSession, source: str, read_args: dict
    ):
        return ObjectTableData(spark_session, source, read_args)


class NonDetectionsCSVLoader(CSVLoader):
    def create_table_data(
        self, spark_session: SparkSession, source: str, read_args: dict
    ):
        return NonDetectionTableData(spark_session, source, read_args)


class SSCSVLoader(CSVLoader):
    def create_table_data(
        self, spark_session: SparkSession, source: str, read_args: dict
    ):
        return SSTableData(spark_session, source, read_args)


class DataQualityCSVLoader(CSVLoader):
    def create_table_data(
        self, spark_session: SparkSession, source: str, read_args: dict
    ):
        return DataQualityTableData(spark_session, source, read_args)


class MagstatsCSVLoader(CSVLoader):
    def create_table_data(
        self, spark_session: SparkSession, source: str, read_args: dict
    ):
        return MagstatsTableData(spark_session, source, read_args)


class PS1CSVLoader(CSVLoader):
    def create_table_data(
        self, spark_session: SparkSession, source: str, read_args: dict
    ):
        return PS1TableData(spark_session, source, read_args)


class GaiaCSVLoader(CSVLoader):
    def create_table_data(
        self, spark_session: SparkSession, source: str, read_args: dict
    ):
        return GaiaTableData(spark_session, source, read_args)


class ReferenceCSVLoader(CSVLoader):
    def create_table_data(
        self, spark_session: SparkSession, source: str, read_args: dict
    ):
        return ReferenceTableData(spark_session, source, read_args)


class AllwiseCSVLoader(CSVLoader):
    def create_table_data(
        self, spark_session: SparkSession, source: str, read_args: dict
    ):
        return AllwiseTableData(spark_session, source, read_args)


class XmatchCSVLoader(CSVLoader):
    def create_table_data(
        self, spark_session: SparkSession, source: str, read_args: dict
    ):
        return XmatchTableData(spark_session, source, read_args)


class FeatureCSVLoader(CSVLoader):
    def create_table_data(
        self, spark_session: SparkSession, source: str, read_args: dict
    ):
        return FeatureTableData(spark_session, source, read_args)

class ProbabilityCSVLoader(CSVLoader):
    def create_table_data(
        self, spark_session: SparkSession, source: str, read_args: dict
    ):
        return ProbabilityTableData(spark_session, source, read_args)