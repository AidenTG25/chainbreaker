import pytest
import numpy as np
from backend.ml.feature_extractor import extract_features, derive_features, flow_to_vector


def test_extract_features():
    flow = {
        "duration": 1000,
        "fwd_packets": 5,
        "bwd_packets": 3,
        "fwd_bytes": 500,
        "bwd_bytes": 300,
        "flow_bytes_per_sec": 800,
        "flow_packets_per_sec": 8,
        "fwd_packet_len_max": 100,
        "fwd_packet_len_min": 50,
        "fwd_packet_len_mean": 75,
        "fwd_packet_len_std": 20,
        "bwd_packet_len_max": 80,
        "bwd_packet_len_min": 30,
        "bwd_packet_len_mean": 55,
        "bwd_packet_len_std": 15,
        "flow_iat_mean": 100,
        "flow_iat_std": 50,
        "flow_iat_max": 200,
        "flow_iat_min": 10,
        "fwd_iat_total": 500,
        "fwd_iat_mean": 100,
        "fwd_iat_std": 30,
        "fwd_iat_max": 150,
        "fwd_iat_min": 20,
        "bwd_iat_total": 300,
        "bwd_iat_mean": 75,
        "bwd_iat_std": 25,
        "bwd_iat_max": 120,
        "bwd_iat_min": 15,
        "fwd_psh_flags": 0,
        "bwd_psh_flags": 0,
        "fwd_urg_flags": 0,
        "bwd_urg_flags": 0,
        "fwd_header_len": 40,
        "bwd_header_len": 40,
        "fwd_packets_per_sec": 5,
        "bwd_packets_per_sec": 3,
        "min_packet_len": 40,
        "max_packet_len": 100,
        "packet_len_mean": 70,
        "packet_len_std": 25,
        "packet_len_variance": 625,
        "syn_flag_count": 1,
        "rst_flag_count": 0,
        "ack_flag_count": 8,
        "urg_flag_count": 0,
        "cwe_flag_count": 0,
        "ece_flag_count": 0,
        "down_up_ratio": 1.5,
        "avg_packet_size": 70,
        "avg_fwd_seg_size": 75,
        "avg_bwd_seg_size": 55,
        "subflow_fwd_packets": 5,
        "subflow_fwd_bytes": 500,
        "subflow_bwd_packets": 3,
        "subflow_bwd_bytes": 300,
        "init_win_bytes_fwd": 8192,
        "init_win_bytes_bwd": 65535,
        "active_mean": 0,
        "active_std": 0,
        "active_max": 0,
        "active_min": 0,
        "idle_mean": 0,
        "idle_std": 0,
        "idle_max": 0,
        "idle_min": 0,
    }
    features = extract_features(flow)
    assert isinstance(features, np.ndarray)
    assert features.shape[0] == 64
    assert not np.any(np.isnan(features))


def test_derive_features():
    base = np.ones(64)
    base[3] = 500
    base[4] = 300
    base[33] = 8
    base[41] = 1
    base[43] = 8
    derived = derive_features(base)
    assert derived.shape[0] == 7
    assert derived[0] == 100.0
    assert derived[2] == pytest.approx(0.625, rel=0.01)


def test_flow_to_vector():
    flow = {
        "duration": 1000, "fwd_packets": 5, "bwd_packets": 3,
        "fwd_bytes": 500, "bwd_bytes": 300, "flow_bytes_per_sec": 800,
        "flow_packets_per_sec": 8, "fwd_packet_len_max": 100,
        "fwd_packet_len_min": 50, "fwd_packet_len_mean": 75,
        "fwd_packet_len_std": 20, "bwd_packet_len_max": 80,
        "bwd_packet_len_min": 30, "bwd_packet_len_mean": 55,
        "bwd_packet_len_std": 15, "flow_iat_mean": 100,
        "flow_iat_std": 50, "flow_iat_max": 200, "flow_iat_min": 10,
        "fwd_iat_total": 500, "fwd_iat_mean": 100, "fwd_iat_std": 30,
        "fwd_iat_max": 150, "fwd_iat_min": 20, "bwd_iat_total": 300,
        "bwd_iat_mean": 75, "bwd_iat_std": 25, "bwd_iat_max": 120,
        "bwd_iat_min": 15, "fwd_psh_flags": 0, "bwd_psh_flags": 0,
        "fwd_urg_flags": 0, "bwd_urg_flags": 0, "fwd_header_len": 40,
        "bwd_header_len": 40, "fwd_packets_per_sec": 5,
        "bwd_packets_per_sec": 3, "min_packet_len": 40,
        "max_packet_len": 100, "packet_len_mean": 70,
        "packet_len_std": 25, "packet_len_variance": 625,
        "syn_flag_count": 1, "rst_flag_count": 0, "ack_flag_count": 8,
        "urg_flag_count": 0, "cwe_flag_count": 0, "ece_flag_count": 0,
        "down_up_ratio": 1.5, "avg_packet_size": 70,
        "avg_fwd_seg_size": 75, "avg_bwd_seg_size": 55,
        "subflow_fwd_packets": 5, "subflow_fwd_bytes": 500,
        "subflow_bwd_packets": 3, "subflow_bwd_bytes": 300,
        "init_win_bytes_fwd": 8192, "init_win_bytes_bwd": 65535,
        "active_mean": 0, "active_std": 0, "active_max": 0, "active_min": 0,
        "idle_mean": 0, "idle_std": 0, "idle_max": 0, "idle_min": 0,
    }
    vector = flow_to_vector(flow)
    assert vector.shape[0] == 71
