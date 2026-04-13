import pytest
from backend.ingestion.cicflow_parser import parse_cicflow_csv_row


def test_parse_cicflow_row():
    row = {
        "Flow.ID": "abc123",
        "Src.IP": "192.168.1.10",
        "Src.Port": "443",
        "Dst.IP": "192.168.1.20",
        "Dst.Port": "8080",
        "Protocol": "TCP",
        "Timestamp": "2024-07-15T10:30:00",
        "Flow.Duration": "1000",
        "Total.Fwd.Packets": "5",
        "Total.Backward.Packets": "3",
        "Total.Length.of.Fwd.Packets": "500",
        "Total.Length.of.Bwd.Packets": "300",
        "Flow.Bytes.s": "800",
        "Flow.Packets.s": "8",
        "Label": "BENIGN",
    }
    flow = parse_cicflow_csv_row(row)
    assert flow["src_ip"] == "192.168.1.10"
    assert flow["dst_ip"] == "192.168.1.20"
    assert flow["src_port"] == 443
    assert flow["dst_port"] == 8080
    assert flow["protocol"] == "TCP"
    assert flow["label"] == "BENIGN"
    assert flow["fwd_packets"] == 5


def test_parse_row_with_missing_fields():
    row = {"Src.IP": "10.0.0.1", "Dst.IP": "10.0.0.2"}
    flow = parse_cicflow_csv_row(row)
    assert flow["src_ip"] == "10.0.0.1"
    assert flow["dst_ip"] == "10.0.0.2"
    assert flow["src_port"] == 0
    assert flow["label"] == "BENIGN"
