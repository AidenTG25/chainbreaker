from pyspark.sql import functions as F
from pyspark.sql.window import Window

from backend.temporal.spark_aggregator import SparkAggregator
from backend.utils.logger import setup_logger

logger = setup_logger("feature_generator")


class TemporalFeatureGenerator:
    def __init__(self, aggregator: SparkAggregator):
        self.aggregator = aggregator

    def generate_cross_flow_features(self, df):
        window_ip = Window.partitionBy("src_ip").orderBy("timestamp").rangeBetween(-300, 0)
        window_port = Window.partitionBy("dst_ip", "dst_port").orderBy("timestamp").rangeBetween(-300, 0)

        return df.withColumns({
            "rolling_flow_count": F.count("*").over(window_ip),
            "rolling_dst_count": F.countDistinct("dst_ip").over(window_ip),
            "rolling_bytes": F.sum("fwd_bytes").over(window_ip) + F.sum("bwd_bytes").over(window_ip),
            "port_connection_rate": F.count("*").over(window_port),
        })

    def generate_protocol_features(self, df):
        return (
            df.groupBy("src_ip", "protocol")
            .agg(
                F.count("*").alias("proto_flow_count"),
                F.avg("duration").alias("proto_avg_duration"),
                F.sum("fwd_bytes").alias("proto_total_bytes"),
            )
        )

    def generate_temporal_risk_score(self, df):
        return (
            df.withColumn(
                "risk_score",
                (
                    F.when(F.col("syn_flag_count") > 10, 0.3)
                    .when(F.col("rst_flag_count") > 5, 0.5)
                    .when(F.col("duration") < 1.0, 0.2)
                    .otherwise(0.0)
                ) +
                (
                    F.when(F.col("flow_bytes_per_sec") > 10000, 0.3)
                    .otherwise(0.0)
                )
            )
        )
