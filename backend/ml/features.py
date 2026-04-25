"""
features.py — Single source of truth for feature definitions.

Both train.py and inference.py import from here so column sets
are never out of sync between training and serving.
"""

# ── Columns to NEVER use as features ─────────────────────────────────────────
# IDs, IPs, MACs, raw timestamps, and target-adjacent labels.
DROP_COLUMNS: list[str] = [
    "ts",
    "Source IP",
    "Destination IP",
    "Source Port",
    "Destination Port",
    "Protocol Type",    # numeric proto code — redundant with one-hot Protocol_name
    "Protocol_name",    # string version — already one-hot encoded in the data
    "MAC",
    # Target columns — never leak into features
    "label",
    "subLabel",
    "subLabelCat",
]

TARGET_COLUMN: str = "subLabelCat"

# ── Feature groups (documentation & selection control) ────────────────────────

FLOW_METRICS: list[str] = [
    "flow_duration",
    "Header_Length",
    "Duration",
    "Rate",
    "Srate",
    "Drate",
    "flow_idle_time",
    "flow_active_time",
]

TCP_FLAGS: list[str] = [
    "fin_flag_number",
    "syn_flag_number",
    "rst_flag_number",
    "psh_flag_number",
    "ack_flag_number",
    "urg_flag_number",
    "ece_flag_number",
    "cwr_flag_number",
]

FLAG_COUNTS: list[str] = [
    "ack_count",
    "syn_count",
    "fin_count",
    "urg_count",
    "rst_count",
]

DURATION_STATS: list[str] = [
    "max_duration",
    "min_duration",
    "sum_duration",
    "average_duration",
    "std_duration",
]

PROTOCOL_INDICATORS: list[str] = [
    "CoAP",
    "HTTP",
    "HTTPS",
    "DNS",
    "Telnet",
    "SMTP",
    "SSH",
    "IRC",
    "TCP",
    "UDP",
    "DHCP",
    "ARP",
    "ICMP",
    "IGMP",
    "IPv",
    "LLC",
]

PACKET_STATS: list[str] = [
    "Tot sum",
    "Min",
    "Max",
    "AVG",
    "Std",
    "Tot size",
    "IAT",
    "Number",
]

STATISTICAL_FEATURES: list[str] = [
    "Magnitue",     # dataset typo — keep as-is to match raw column name
    "Radius",
    "Covariance",
    "Variance",
    "Weight",
]

NETWORK_META: list[str] = [
    "DS status",
    "Fragments",
    "Sequence number",
    "Protocol Version",
]

# ── Master feature list (used by both train and inference) ────────────────────
FEATURE_COLUMNS: list[str] = (
    FLOW_METRICS
    + TCP_FLAGS
    + FLAG_COUNTS
    + DURATION_STATS
    + PROTOCOL_INDICATORS
    + PACKET_STATS
    + STATISTICAL_FEATURES
    + NETWORK_META
)

# ── Label normalization ───────────────────────────────────────────────────────
BENIGN_LABEL: str = "BenignTraffic"


def normalize_label(raw_value) -> str:
    """
    Normalize subLabelCat values.

    The dataset has two representations of benign traffic:
      - integer 0  (phase1)
      - string "0" (phase2 artifact)

    Everything else is a genuine attack category string.
    """
    if raw_value is None:
        return BENIGN_LABEL
    s = str(raw_value).strip()
    if s in ("0", "", "nan"):
        return BENIGN_LABEL
    return s
