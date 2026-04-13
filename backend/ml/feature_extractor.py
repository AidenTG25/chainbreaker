from typing import Any
import numpy as np


FEATURE_MAPPING = {
    "duration": ["duration", "flow_duration", "Duration"],
    "fwd_packets": ["fwd_packets"],
    "bwd_packets": ["bwd_packets"],
    "fwd_bytes": ["fwd_bytes", "Tot sum"],
    "bwd_bytes": ["bwd_bytes"],
    "fwd_packet_len_max": ["fwd_packet_len_max", "Max"],
    "fwd_packet_len_min": ["fwd_packet_len_min", "Min"],
    "fwd_packet_len_mean": ["fwd_packet_len_mean", "AVG"],
    "fwd_packet_len_std": ["fwd_packet_len_std", "Std"],
    "bwd_packet_len_max": ["bwd_packet_len_max"],
    "bwd_packet_len_min": ["bwd_packet_len_min"],
    "bwd_packet_len_mean": ["bwd_packet_len_mean"],
    "bwd_packet_len_std": ["bwd_packet_len_std"],
    "flow_bytes_per_sec": ["flow_bytes_per_sec", "Rate", "Drate"],
    "flow_packets_per_sec": ["flow_packets_per_sec", "srate"],
    "flow_iat_mean": ["flow_iat_mean", "IAT"],
    "flow_iat_std": ["flow_iat_std"],
    "flow_iat_max": ["flow_iat_max", "max_duration"],
    "flow_iat_min": ["flow_iat_min", "min_duration"],
    "fwd_iat_total": ["fwd_iat_total", "sum_duration"],
    "fwd_iat_mean": ["fwd_iat_mean", "average_duration"],
    "fwd_iat_std": ["fwd_iat_std", "std_duration"],
    "fwd_iat_max": ["fwd_iat_max"],
    "fwd_iat_min": ["fwd_iat_min"],
    "bwd_iat_total": ["bwd_iat_total"],
    "bwd_iat_mean": ["bwd_iat_mean"],
    "bwd_iat_std": ["bwd_iat_std"],
    "bwd_iat_max": ["bwd_iat_max"],
    "bwd_iat_min": ["bwd_iat_min"],
    "fwd_psh_flags": ["fwd_psh_flags", "psh_flag_count"],
    "bwd_psh_flags": ["bwd_psh_flags"],
    "fwd_urg_flags": ["fwd_urg_flags", "urg_flag_count"],
    "bwd_urg_flags": ["bwd_urg_flags"],
    "fwd_header_len": ["fwd_header_len", "Header_Length"],
    "bwd_header_len": ["bwd_header_len"],
    "fwd_packets_per_sec": ["fwd_packets_per_sec"],
    "bwd_packets_per_sec": ["bwd_packets_per_sec"],
    "min_packet_len": ["min_packet_len", "Min"],
    "max_packet_len": ["max_packet_len", "Max"],
    "packet_len_mean": ["packet_len_mean", "AVG"],
    "packet_len_std": ["packet_len_std", "Std"],
    "packet_len_variance": ["packet_len_variance", "Variance"],
    "syn_flag_count": ["syn_flag_count", "syn_flag_number"],
    "rst_flag_count": ["rst_flag_count", "rst_flag_number"],
    "ack_flag_count": ["ack_flag_count", "ack_flag_number", "ack_count"],
    "urg_flag_count": ["urg_flag_count", "urg_flag_number"],
    "cwe_flag_count": ["cwe_flag_count"],
    "ece_flag_count": ["ece_flag_count", "ece_flag_number"],
    "down_up_ratio": ["down_up_ratio"],
    "avg_packet_size": ["avg_packet_size", "Tot size"],
    "avg_fwd_seg_size": ["avg_fwd_seg_size"],
    "avg_bwd_seg_size": ["avg_bwd_seg_size"],
    "subflow_fwd_packets": ["subflow_fwd_packets"],
    "subflow_fwd_bytes": ["subflow_fwd_bytes"],
    "subflow_bwd_packets": ["subflow_bwd_packets"],
    "subflow_bwd_bytes": ["subflow_bwd_bytes"],
    "init_win_bytes_fwd": ["init_win_bytes_fwd"],
    "init_win_bytes_bwd": ["init_win_bytes_bwd"],
    "active_mean": ["active_mean", "flow_active_time"],
    "active_std": ["active_std"],
    "active_max": ["active_max"],
    "active_min": ["active_min"],
    "idle_mean": ["idle_mean", "flow_idle_time"],
    "idle_std": ["idle_std"],
    "idle_max": ["idle_max"],
    "idle_min": ["idle_min"],
}


def _get_value(flow: dict[str, Any], keys: list[str]) -> float:
    for key in keys:
        val = flow.get(key)
        if val is not None and val != "":
            try:
                return float(val)
            except (ValueError, TypeError):
                continue
    return 0.0


def extract_features(flow: dict[str, Any]) -> np.ndarray:
    feature_names = list(FEATURE_MAPPING.keys())
    values = []
    for name in feature_names:
        val = _get_value(flow, FEATURE_MAPPING[name])
        values.append(val)
    return np.array(values, dtype=np.float32)


def derive_features(features: np.ndarray) -> np.ndarray:
    fwd_bytes_idx = 3
    bwd_bytes_idx = 4
    total_packets_idx = 33
    syn_idx = 41
    ack_idx = 43
    duration_idx = 0
    
    derived = []
    total_bytes = features[fwd_bytes_idx] + features[bwd_bytes_idx]
    total_packets = features[1] + features[2] if len(features) > 2 else 0
    
    bytes_per_packet = total_bytes / max(total_packets, 1)
    derived.append(bytes_per_packet)
    
    packets_per_sec = total_packets / max(features[duration_idx], 1e-6)
    derived.append(packets_per_sec)
    
    fwd_ratio = features[fwd_bytes_idx] / max(total_bytes, 1)
    derived.append(fwd_ratio)
    
    syn_count = _get_syn_count(features)
    syn_ratio = syn_count / max(total_packets, 1)
    derived.append(syn_ratio)
    
    ack_count = _get_ack_count(features)
    ack_ratio = ack_count / max(total_packets, 1)
    derived.append(ack_ratio)
    
    if len(features) > 39:
        packet_len_mean = features[39]
        packet_len_std = features[40]
        variance_ratio = packet_len_std / max(packet_len_mean, 1e-6) if packet_len_mean > 0 else 0
    else:
        variance_ratio = 0
    derived.append(variance_ratio)
    
    if len(features) > 15:
        iat_mean = features[15]
        iat_std = features[16]
        iat_cv = iat_std / max(abs(iat_mean), 1e-6) if iat_mean != 0 else 0
    else:
        iat_cv = 0
    derived.append(iat_cv)
    
    return np.array(derived, dtype=np.float32)


def _get_syn_count(features: np.ndarray) -> float:
    if len(features) > 41:
        return features[41]
    return 0.0


def _get_ack_count(features: np.ndarray) -> float:
    if len(features) > 43:
        return features[43]
    return 0.0


def flow_to_vector(flow: dict[str, Any]) -> np.ndarray:
    base = extract_features(flow)
    derived = derive_features(base)
    result = np.concatenate([base, derived])
    result = np.nan_to_num(result, nan=0.0, posinf=0.0, neginf=0.0)
    return result