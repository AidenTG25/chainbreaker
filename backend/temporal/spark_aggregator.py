from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

from backend.utils.config import config
from backend.utils.logger import setup_logger

logger = setup_logger("spark_aggregator")


def create_spark_session() -> SparkSession:
    spark_cfg = config.get_section("spark").get("spark", {})
    return (
        SparkSession.builder
        .master(config.get("spark.master", "local[*]"))
        .appName(config.get("spark.app_name", "ChainBreaker-Temporal"))
        .config("spark.driver.memory", spark_cfg.get("driver_memory", "2g"))
        .config("spark.executor.memory", spark_cfg.get("executor_memory", "2g"))
        .config("spark.shuffle.partitions", spark_cfg.get("shuffle_partitions", 8))
        .getOrCreate()
    )


FLOW_SCHEMA = StructType([
    StructField("flow_id", StringType(), True),
    StructField("src_ip", StringType(), True),
    StructField("src_port", IntegerType(), True),
    StructField("dst_ip", StringType(), True),
    StructField("dst_port", IntegerType(), True),
    StructField("protocol", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("duration", DoubleType(), True),
    StructField("fwd_packets", IntegerType(), True),
    StructField("bwd_packets", IntegerType(), True),
    StructField("fwd_bytes", IntegerType(), True),
    StructField("bwd_bytes", IntegerType(), True),
    StructField("flow_bytes_per_sec", DoubleType(), True),
    StructField("flow_packets_per_sec", DoubleType(), True),
    StructField("syn_flag_count", IntegerType(), True),
    StructField("ack_flag_count", IntegerType(), True),
    StructField("rst_flag_count", IntegerType(), True),
])


class SparkAggregator:
    def __init__(self):
        self.spark = create_spark_session()
        self.spark.sparkContext.setLogLevel("WARN")
        logger.info("spark_session_created")

    def aggregate_flows(self, df):
        window_spec = Window.partitionBy("src_ip", "dst_ip", "dst_port").orderBy("timestamp")
        return (
            df.withWatermark("timestamp", "5 minutes")
            .groupBy("src_ip", "dst_ip", "dst_port", "protocol")
            .agg(
                F.count("*").alias("flow_count"),
                F.sum("fwd_packets").alias("total_fwd_packets"),
                F.sum("bwd_packets").alias("total_bwd_packets"),
                F.sum("fwd_bytes").alias("total_fwd_bytes"),
                F.sum("bwd_bytes").alias("total_bwd_bytes"),
                F.max("flow_bytes_per_sec").alias("max_bytes_per_sec"),
                F.avg("duration").alias("avg_duration"),
                F.countDistinct("src_ip").alias("unique_sources"),
            )
        )

    def detect_port_scan_pattern(self, df):
        window_ip = Window.partitionBy("src_ip")
        return (
            df.withWatermark("timestamp", "10 minutes")
            .groupBy("src_ip", "window")
            .agg(
                F.countDistinct("dst_ip").alias("unique_dst_ips"),
                F.countDistinct("dst_port").alias("unique_dst_ports"),
                F.count("*").alias("total_connections"),
            )
            .filter(F.col("unique_dst_ports") >= config.get_nested("spark", "coordinated", "port_scan_threshold", default=20))
        )

    def stop(self):
        self.spark.stop()
        logger.info("spark_session_stopped")
