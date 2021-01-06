from load_psql.table_data import TableData
from pyspark.sql import DataFrame, DataFrameReader, SparkSession
from .table_columns import (
    det_col,
    obj_col,
    non_col,
    ss_col,
    qua_col,
    mag_col,
    ps1_col,
    gaia_col,
    ref_col,
    xch_col,
)
from pyspark.sql.functions import (
    col,
    lit,
)
from pyspark.sql.types import IntegerType


class DetectionTableData(TableData):
    def select(self, tt_det: DataFrame, step_id: str) -> DataFrame:
        data_det = (
            tt_det.select(
                "i.aimage",
                "i.aimagerat",
                "i.bimage",
                "i.bimagerat",
                "i.candid",
                "i.chinr",
                "i.chipsf",
                "i.classtar",
                "i.corrected",
                "i.dec",
                "i.decnr",
                "i.diffmaglim",
                "i.distnr",
                "i.distpsnr1",
                "i.distpsnr2",
                "i.distpsnr3",
                "i.dubious",
                "i.elong",
                "i.fid",
                "i.field",
                "i.fwhm",
                tt_det["i.isdiffpos"].cast(IntegerType()),
                "i.jdendhist",
                "i.jdendref",
                "i.jdstarthist",
                "i.jdstartref",
                "i.magap",
                "i.magapbig",
                "i.magdiff",
                "i.magfromlim",
                "i.magnr",
                "i.magpsf",
                "i.magpsf_corr",
                "i.mindtoedge",
                "i.mjd",
                "i.nbad",
                "i.ncovhist",
                "i.ndethist",
                "i.nframesref",
                "i.nid",
                "i.nmtchps",
                "i.nneg",
                "i.objectId",
                "i.objectidps1",
                "i.objectidps2",
                "i.objectidps3",
                "i.parent_candid",
                "i.pdiffimfilename",
                "i.pid",
                "i.programid",
                "i.programpi",
                "i.ra",
                "i.ranr",
                "i.rb",
                "i.rcid",
                "i.rfid",
                "i.scorr",
                "i.seeratio",
                "i.sgmag1",
                "i.sgmag2",
                "i.sgmag3",
                "i.sgscore1",
                "i.sgscore2",
                "i.sgscore3",
                "i.sharpnr",
                "i.sigmagap",
                "i.sigmagapbig",
                "i.sigmagnr",
                "i.sigmapsf",
                "i.sigmapsf_corr",
                "i.sigmapsf_corr_ext",
                "i.simag1",
                "i.simag2",
                "i.simag3",
                "i.sky",
                "i.srmag1",
                "i.srmag2",
                "i.srmag3",
                "i.ssdistnr",
                "i.ssmagnr",
                "i.ssnamenr",
                "i.sumrat",
                "i.szmag1",
                "i.szmag2",
                "i.szmag3",
                "i.tblid",
                "i.tooflag",
                "i.xpos",
                "i.ypos",
                "i.rbversion",
                "i.drb",
                "i.drbversion",
            )
            .withColumn("has_stamp", col("parent_candid") == 0)
            .withColumn("step_id_corr", lit(step_id))
        )

        data_det = data_det.fillna("", "rbversion")
        data_det = data_det.fillna("", "drbversion")

        sel_det = data_det.select(*[col(c) for c in det_col])
        return sel_det

    def save(self, output_dir, n_partitions, max_records_per_file, mode, selected=None, *args, **kwargs):
        # logging.info("Writing detections")
        sel_det = selected or self.dataframe
        sel_det.coalesce(n_partitions).write.option(
            "maxRecordsPerFile", max_records_per_file
        ).mode(mode).csv(output_dir, emptyValue="")
