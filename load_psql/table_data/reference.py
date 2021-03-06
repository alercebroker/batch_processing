from .generic import TableData
from pyspark.sql import Window
from pyspark.sql.functions import col
from pyspark.sql.functions import min as spark_min
from pyspark.sql.types import IntegerType, LongType


class ReferenceTableData(TableData):
    def select(self, column_list, tt_det):

        tmp_cols = [
            "i.rfid",
            "objectId",
            "candid",
            "i.fid",
            "i.rcid",
            "i.field",
            "i.magnr",
            "i.sigmagnr",
            "i.chinr",
            "i.sharpnr",
            "i.ranr",
            "i.decnr",
            "i.jdstartref",
            "i.jdendref",
            "i.nframesref",
        ]

        tt_ref = tt_det.select(tmp_cols)
        obj_rfid_cid_window = Window.partitionBy("objectId", "rfid").orderBy("candid")

        tt_ref_min = (
            tt_ref.withColumn(
                "auxcandid",
                spark_min(col("candid")).over(obj_rfid_cid_window),
            )
            .withColumn("i.jdstartref", tt_ref["i.jdstartref"] - 2400000.5)
            .withColumn("i.jdendref", tt_ref["i.jdendref"] - 2400000.5)
            .withColumn("candid", col("candid").cast(LongType()))
            .withColumnRenamed("i.jdstartref", "mjdstartref")
            .withColumnRenamed("i.jdendref", "mjdendref")
            .where(col("candid") == col("auxcandid"))
            .fillna(
                {
                    "rfid": -9999,
                    "mjdstartref": -9999,
                    "mjdendref": -9999,
                    "nframesref": -9999,
                }
            )
            .select(
                *[
                    col(c).cast(IntegerType())
                    if c in ["rfid", "nframesref"]
                    else col(c)
                    for c in column_list
                ]
            )
        )

        return tt_ref_min
