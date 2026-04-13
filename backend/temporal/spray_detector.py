from pyspark.sql import functions as F
from pyspark.sql.types import StringType

from backend.temporal.spark_aggregator import SparkAggregator
from backend.utils.config import config
from backend.utils.logger import setup_logger

logger = setup_logger("spray_detector")


class SprayDetector:
    def __init__(self, aggregator: SparkAggregator):
        self.aggregator = aggregator
        self.thresholds = config.get_section("spark").get("spray_detection", {})

    def detect_password_spraying(self, df):
        unique_targets = self.thresholds.get("unique_targets_threshold", 5)
        unique_users = self.thresholds.get("unique_users_threshold", 3)
        failed_auth = self.thresholds.get("failed_auth_threshold", 10)

        return (
            df.withWatermark("timestamp", "5 minutes")
            .groupBy("src_ip", "window")
            .agg(
                F.countDistinct("dst_ip").alias("unique_target_ips"),
                F.countDistinct("dst_port").alias("unique_target_ports"),
                F.count("*").alias("attempt_count"),
                F.sum(F.when(F.col("rst_flag_count") > 0, 1).otherwise(0)).alias("failed_auth_count"),
            )
            .filter(
                (F.col("unique_target_ips") >= unique_targets) &
                (F.col("attempt_count") >= failed_auth)
            )
        )

    def detect_distributed_attack(self, df):
        min_sources = config.get_nested("spark", "coordinated", "min_source_count", default=3)
        min_targets = config.get_nested("spark", "coordinated", "min_target_count", default=2)

        return (
            df.withWatermark("timestamp", "10 minutes")
            .groupBy("dst_ip", "window")
            .agg(
                F.countDistinct("src_ip").alias("unique_source_ips"),
                F.count("*").alias("total_flows"),
                F.avg("fwd_packets").alias("avg_packets"),
            )
            .filter(
                (F.col("unique_source_ips") >= min_sources) &
                (F.col("total_flows") >= min_sources * 5)
            )
        )

    def generate_spray_features(self, df):
        return (
            df.withWatermark("timestamp", "5 minutes")
            .groupBy("src_ip")
            .agg(
                F.countDistinct("dst_ip").alias("spray_unique_targets"),
                F.count("*").alias("spray_total_attempts"),
                F.max("syn_flag_count").alias("spray_max_syn_ratio"),
            )
            .withColumn(
                "spray_score",
                F.col("spray_unique_targets") * F.col("spray_total_attempts") / 100.0
            )
        )
