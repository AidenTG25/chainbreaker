from datetime import datetime
from typing import Any


COLUMN_ALIASES = {
    "Source IP": "src_ip",
    "Destination IP": "dst_ip", 
    "Source Port": "src_port",
    "Destination Port": "dst_port",
    "Protocol Type": "protocol_type",
    "Protocol_name": "protocol",
    "ts": "timestamp",
    "flow_duration": "duration",
    "Duration": "duration",
    "Rate": "rate",
    "Srate": "srate",
    "Drate": "drate",
    "fin_flag_number": "fin_flag_count",
    "syn_flag_number": "syn_flag_count",
    "rst_flag_number": "rst_flag_count",
    "psh_flag_number": "psh_flag_count",
    "ack_flag_number": "ack_flag_count",
    "urg_flag_number": "urg_flag_count",
    "ece_flag_number": "ece_flag_count",
    "cwr_flag_number": "cwr_flag_count",
    "ack_count": "ack_count",
    "syn_count": "syn_count",
    "fin_count": "fin_count",
    "urg_count": "urg_count",
    "rst_count": "rst_count",
    "max_duration": "max_duration",
    "min_duration": "min_duration",
    "sum_duration": "sum_duration",
    "average_duration": "avg_duration",
    "std_duration": "std_duration",
    "Tot sum": "total_bytes",
    "Tot size": "total_size",
    "IAT": "iat",
    "Number": "number",
    "Magnitue": "magnitude",
    "Radius": "radius",
    "Covariance": "covariance",
    "Variance": "variance",
    "Weight": "weight",
    "DS status": "ds_status",
    "label": "label",
    "subLabel": "sublabel",
    "subLabelCat": "sublabel_cat",
    "flow_idle_time": "flow_idle_time",
    "flow_active_time": "flow_active_time",
    "Header_Length": "header_length",
    "Protocol Version": "protocol_version",
    "Fragments": "fragments",
    "Sequence number": "sequence_number",
}


def normalize_column_name(col: str) -> str:
    return COLUMN_ALIASES.get(col.strip(), col.strip().replace(" ", "_").replace(".", "_"))


def parse_network_flow_row(row: dict[str, Any]) -> dict[str, Any]:
    flow = {}
    for key, value in row.items():
        normalized_key = normalize_column_name(key)
        if normalized_key in ["src_ip", "dst_ip"]:
            flow[normalized_key] = str(value).strip()
        elif normalized_key in ["src_port", "dst_port"]:
            try:
                flow[normalized_key] = int(float(value)) if value else 0
            except (ValueError, TypeError):
                flow[normalized_key] = 0
        elif normalized_key in ["timestamp", "ts"]:
            ts = str(value).strip()
            if ts:
                try:
                    flow["timestamp"] = datetime.fromisoformat(ts).isoformat()
                except (ValueError, TypeError):
                    try:
                        flow["timestamp"] = datetime.fromtimestamp(float(ts)).isoformat()
                    except (ValueError, TypeError):
                        flow["timestamp"] = datetime.utcnow().isoformat()
            else:
                flow["timestamp"] = datetime.utcnow().isoformat()
        elif normalized_key in ["duration", "rate", "srate", "drate"]:
            try:
                flow[normalized_key] = float(value) if value else 0.0
            except (ValueError, TypeError):
                flow[normalized_key] = 0.0
        elif normalized_key in ["fin_flag_count", "syn_flag_count", "rst_flag_count", 
                              "psh_flag_count", "ack_flag_count", "urg_flag_count",
                              "ece_flag_count", "cwr_flag_count", "ack_count", "syn_count",
                              "fin_count", "urg_count", "rst_count"]:
            try:
                flow[normalized_key] = int(float(value)) if value else 0
            except (ValueError, TypeError):
                flow[normalized_key] = 0
        else:
            flow[normalized_key] = value
    if not flow.get("src_ip"):
        flow["src_ip"] = flow.get("Source IP", "")
    if not flow.get("dst_ip"):
        flow["dst_ip"] = flow.get("Destination IP", "")
    if not flow.get("protocol"):
        flow["protocol"] = flow.get("Protocol_name", "TCP")
    if not flow.get("label"):
        flow["label"] = str(row.get("label", "BENIGN")).strip()
    if not flow.get("sublabel"):
        flow["sublabel"] = str(row.get("subLabel", "")).strip()
    flow["label"] = flow.get("label", "BENIGN")
    return flow