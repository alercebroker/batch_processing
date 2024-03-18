from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType, FloatType, DoubleType

fp_hist_schema = StructType([
    StructField("field", IntegerType(), True),
    StructField("rcid", IntegerType(), True),
    StructField("fid", IntegerType(), False),
    StructField("pid", LongType(), False),
    StructField("rfid", LongType(), False),
    StructField("sciinpseeing", FloatType(), True),
    StructField("scibckgnd", FloatType(), True),
    StructField("scisigpix", FloatType(), True),
    StructField("magzpsci", FloatType(), True),
    StructField("magzpsciunc", FloatType(), True),
    StructField("magzpscirms", FloatType(), True),
    StructField("clrcoeff", FloatType(), True),
    StructField("clrcounc", FloatType(), True),
    StructField("exptime", FloatType(), True),
    StructField("adpctdif1", FloatType(), True),
    StructField("adpctdif2", FloatType(), True),
    StructField("diffmaglim", FloatType(), True),
    StructField("programid", IntegerType(), False),
    StructField("jd", DoubleType(), False),
    StructField("forcediffimflux", FloatType(), True),
    StructField("forcediffimfluxunc", FloatType(), True),
    StructField("procstatus", StringType(), True),
    StructField("distnr", FloatType(), True),
    StructField("ranr", DoubleType(), False),
    StructField("decnr", DoubleType(), False),
    StructField("magnr", FloatType(), True),
    StructField("sigmagnr", FloatType(), True),
    StructField("chinr", FloatType(), True),
    StructField("sharpnr", FloatType(), True)
])