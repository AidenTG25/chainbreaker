"""
cicflow_parser.py - Parse raw CICFlow CSV rows from Kafka.
"""

from datetime import datetime
from typing import Any


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def parse_network_flow_row(row: dict[str, Any]) -> dict[str, Any] | None:
    """
    Convert one raw CSV row dict into the normalized flow shape used downstream.

    Required exact input columns:
        "Source IP"
        "Destination IP"
        "Protocol_name"
        "label"
        "subLabel"
    """
    src_ip = _clean(row.get("Source IP"))
    dst_ip = _clean(row.get("Destination IP"))

    if not src_ip or not dst_ip:
        return None

    return {
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "protocol": _clean(row.get("Protocol_name")),
        "label": _clean(row.get("label")),
        "sublabel": _clean(row.get("subLabel")),
        "timestamp": _clean(row.get("timestamp")) or datetime.utcnow().isoformat(),
        "props": dict(row),
    }


def normalize_column_name(col: str) -> str:
    aliases = {
        "Source IP": "src_ip",
        "Destination IP": "dst_ip",
        "Protocol_name": "protocol",
        "label": "label",
        "subLabel": "sublabel",
    }
    cleaned = col.strip()
    return aliases.get(cleaned, cleaned.replace(" ", "_").replace(".", "_").lower())
