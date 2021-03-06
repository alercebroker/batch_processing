from pyspark.sql.functions import explode, col, struct, lit, array, split, dense_rank, desc
from pyspark.sql import Window

from .generic import TableData

class ProbabilityTableData(TableData):
    def select(self, column_list, version, classifier_name):
        cols_p = [
                c for (c, t) in self.dataframe.dtypes if (c not in ["oid"] and t in ['float', 'double'])  
        ]
        new_cols = explode(array([struct(lit(c).alias("key"), col(c).alias("value")) for c in cols_p])).alias("new_cols")
        df = (
                self.dataframe.dropDuplicates().select(
                    ["oid"] + [new_cols]).select(["oid"] + ["new_cols.key", "new_cols.value"]
                )
                .withColumn("classifier_version", lit(version))
                .withColumn("class_name", (split(col("key"), "_").getItem(0)))
                .withColumn("probability",(col("value")))
            )
        df = df.withColumn("classifier_name", lit(classifier_name))
        df = df.withColumn("ranking", dense_rank().over(Window.partitionBy("oid").orderBy(desc("probability"))))
        df = df.drop("key").drop("value")
        sel_prob = df.select(column_list)
        return sel_prob