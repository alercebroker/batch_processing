from .generic import TableData
from pyspark.sql.functions import col, countDistinct
from pyspark.sql.functions import min as spark_min
from pyspark.sql.types import LongType, IntegerType


class PS1TableData(TableData):
    def select(self, column_list, obj_cid_window):
        # logging.info("Processing ps1")
        column_list.remove("objectId")
        column_list.remove("unique1")
        column_list.remove("unique2")
        column_list.remove("unique3")

        self.dataframe = self.dataframe.where(col("has_stamp"))
        tt_ps1 = self.dataframe.select(
            "objectId",
            *[
                col(c).cast(LongType())
                if c in ["candid", "objectidps1", "objectidps2", "objectidps3"]
                else col(c)
                for c in column_list
            ],
        )

        tt_ps1_min = (
            tt_ps1.withColumn(
                "mincandid", spark_min(col("candid")).over(obj_cid_window)
            )
            .where(col("candid") == col("mincandid")).select("objectId", *column_list)
        )

        data_ps1 = (
            tt_ps1_min.alias("i")
            .join(tt_ps1.alias("c"), "objectId", "inner")
            .withColumn("unique1", col("i.objectidps1") == col("c.objectidps1"))
            .withColumn("unique2", col("i.objectidps2") == col("c.objectidps2"))
            .withColumn("unique3", col("i.objectidps3") == col("c.objectidps3"))
            .select(
                "objectId",
                *[col("i." + c).alias(c) for c in column_list],
                "unique1",
                "unique2",
                "unique3"
            )
            .fillna({"nmtchps": 0})
        )

        column_list.remove("candid")
        column_list_cast = []
        gr_ps1 = (
            data_ps1.groupBy("objectId", "candid", *column_list)
            .agg(
                countDistinct("unique1").alias("count1"),
                countDistinct("unique2").alias("count2"),
                countDistinct("unique3").alias("count3"),
            )
            .withColumn("unique1", col("count1") == 1)
            .withColumn("unique2", col("count2") == 1)
            .withColumn("unique3", col("count3") == 1)
            .withColumn("nmtchps", col("nmtchps").cast(IntegerType()))
            .drop("count1")
            .drop("count2")
            .drop("count3")
            .dropDuplicates(["objectId", "candid"])
        )

        return gr_ps1
