from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

from batch_processing import ParquetReader
from utils.wizard import id_generator
from utils.database import oid_query, conesearch_query

RADIUS = 1.5

class SortingHatBatch():
    
    def __init__(self) -> None:
        
        # Create Spark session
        spark = (
            SparkSession.builder.appName("ZTFUtils")
            .master("local")
            .config("spark.executor.memory", "4g")
            .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.1")
            .getOrCreate()
        )
        
        # Initialize ParquetReader
        config_path = "/home/edipizarro/alerce/batch_processing/configs/read.config.json"
        parquet_reader = ParquetReader(config_path)
        parquet_reader.register_spark_session(spark)

        mongo_connection = None

        # Start df_generator
        self.df_generator = parquet_reader.get_df_generator()

    def by_row_function(self, mongo_connection):
        def _row_process(ra, dec, oid):
            conection = mongo_connection
            
            # FIND AID BY OID
            aid = oid_query(conection, oid)

            # if config require it find aid by conesearch
            if self.config.get("run_conesearch", False) and not aid:
                aid = conesearch_query(conection, ra, dec, RADIUS)

            # if aid was not found create a new one
            if not aid:
                aid = id_generator(ra, dec)

            return aid

        return _row_process

    def process(self):
        # Loop through all df in df_generator
        iterator_udf = udf(self.by_row_function(self.mongo_connection), StringType) # maybe needs to be defined with lamda

        generator_is_empty = False
        while not(generator_is_empty, StringType):
            try:
                df = next(self.df_generator)
                # run the by colum function
                df.withColumn("aid", iterator_udf(df.ra, df.re, df.oid)).collect()
                print(df.select("objectId").count())

            except StopIteration:
                generator_is_empty = True
                print("All parquets read succesfully")
