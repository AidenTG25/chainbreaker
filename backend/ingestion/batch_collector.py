import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any


class BatchCollector:
    def __init__(self, window_seconds: int = 60):
        self.window_seconds = window_seconds
        self.flows: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.flow_keys: dict[str, str] = {}
        self._lock = asyncio.Lock()

    def _make_key(self, flow: dict[str, Any]) -> str:
        src = flow.get("src_ip", "")
        dst = flow.get("dst_ip", "")
        sport = flow.get("src_port", 0)
        dport = flow.get("dst_port", 0)
        proto = flow.get("protocol", "")
        return f"{src}:{sport}->{dst}:{dport}:{proto}"

    def add(self, flow: dict[str, Any]) -> None:
        key = self._make_key(flow)
        ts_str = flow.get("timestamp", datetime.utcnow().isoformat())
        try:
            ts = datetime.fromisoformat(ts_str)
        except (ValueError, TypeError):
            ts = datetime.utcnow()
        window_start = ts.replace(second=ts.second // 10 * 10, microsecond=0)
        window_key = f"{key}@{window_start.isoformat()}"
        self.flows[window_key].append(flow)
        self.flow_keys[window_key] = key

    async def get_batches(self) -> dict[str, list[dict[str, Any]]]:
        async with self._lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(seconds=self.window_seconds)
            expired_keys = []
            for key in list(self.flows.keys()):
                try:
                    window_str = key.split("@")[1]
                    window_time = datetime.fromisoformat(window_str)
                    if window_time < cutoff:
                        expired_keys.append(key)
                except (IndexError, ValueError):
                    expired_keys.append(key)
            for key in expired_keys:
                del self.flows[key]
                if key in self.flow_keys:
                    del self.flow_keys[key]
            return dict(self.flows)

    async def aggregate_window(self, window_key: str) -> dict[str, Any]:
        flows = self.flows.get(window_key, [])
        if not flows:
            return {}
        aggregated = {
            "window_key": window_key,
            "flow_count": len(flows),
            "src_ip": flows[0].get("src_ip"),
            "dst_ip": flows[0].get("dst_ip"),
            "src_port": flows[0].get("src_port"),
            "dst_port": flows[0].get("dst_port"),
            "protocol": flows[0].get("protocol"),
            "total_fwd_packets": sum(f.get("fwd_packets", 0) for f in flows),
            "total_bwd_packets": sum(f.get("bwd_packets", 0) for f in flows),
            "total_fwd_bytes": sum(f.get("fwd_bytes", 0) for f in flows),
            "total_bwd_bytes": sum(f.get("bwd_bytes", 0) for f in flows),
            "avg_flow_duration": sum(f.get("duration", 0) for f in flows) / len(flows),
            "max_flow_bytes_per_sec": max((f.get("flow_bytes_per_sec", 0) for f in flows), default=0),
            "unique_ports": len(set(f.get("dst_port", 0) for f in flows)),
            "syn_ratio": sum(f.get("syn_flag_count", 0) for f in flows) / max(sum(f.get("total_packets", 1) for f in flows), 1),
            "ack_ratio": sum(f.get("ack_flag_count", 0) for f in flows) / max(sum(f.get("total_packets", 1) for f in flows), 1),
            "timestamp": flows[0].get("timestamp"),
        }
        return aggregated
