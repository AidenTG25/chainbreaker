from prometheus_client import Counter, Gauge, Histogram


class Metrics:
    flows_processed = Counter(
        "chainbreaker_flows_processed_total", "Total network flows processed"
    )
    ml_predictions = Counter(
        "chainbreaker_ml_predictions_total",
        "ML predictions made",
        ["stage", "model"],
    )
    graph_nodes_created = Counter(
        "chainbreaker_graph_nodes_created_total", "Neo4j nodes created", ["node_type"]
    )
    graph_edges_created = Counter(
        "chainbreaker_graph_edges_created_total", "Neo4j edges created", ["edge_type"]
    )
    kafka_messages_consumed = Counter(
        "chainbreaker_kafka_messages_consumed_total", "Kafka messages consumed"
    )
    alerts_generated = Counter(
        "chainbreaker_alerts_generated_total", "Security alerts generated", ["severity"]
    )
    rl_actions_taken = Counter(
        "chainbreaker_rl_actions_taken_total", "RL agent actions", ["action", "stage"]
    )
    containment_success = Counter(
        "chainbreaker_containment_success_total", "Successful stage containment", ["stage"]
    )
    containment_failure = Counter(
        "chainbreaker_containment_failure_total", "Failed stage containment", ["stage"]
    )

    active_hosts = Gauge(
        "chainbreaker_active_hosts", "Number of active hosts in graph"
    )
    compromised_hosts = Gauge(
        "chainbreaker_compromised_hosts", "Number of compromised hosts"
    )
    ml_confidence = Histogram(
        "chainbreaker_ml_confidence", "ML prediction confidence", ["stage"]
    )
    flow_processing_time = Histogram(
        "chainbreaker_flow_processing_seconds", "Flow processing time"
    )
