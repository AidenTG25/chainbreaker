# Neo4j Visualization Guide — ChainBreaker Flow Graph

## Quick Start

Open Neo4j Browser at **http://localhost:7474** and connect with:
- Username: `neo4j`
- Password: `chainbreaker`

---

## Node Styling (Neo4j Browser)

Apply these styles in the Neo4j Browser style panel (click a node label → edit color/size):

| Node Label | Color | Size | Caption Property |
|---|---|---|---|
| **Host** | `#4A90D9` (blue) | 80px (large) | `ip` |
| **Flow** | `#AAAAAA` (grey) | 20px (small) | `flow_id` |
| **Protocol** | `#27AE60` (green) | 40px (medium) | `name` |
| **Attack** | `#E74C3C` (red) | 60px (large) | `label` |

### Neo4j Browser GraSS Stylesheet

Paste this into **Settings → Graph Stylesheet** (Neo4j Browser):

```css
node.Host {
  color: #4A90D9;
  border-color: #2C5F9E;
  text-color-internal: #FFFFFF;
  font-size: 12px;
  diameter: 80px;
  caption: '{ip}';
}

node.Flow {
  color: #AAAAAA;
  border-color: #888888;
  text-color-internal: #333333;
  font-size: 8px;
  diameter: 20px;
  caption: '{flow_id}';
}

node.Protocol {
  color: #27AE60;
  border-color: #1E8449;
  text-color-internal: #FFFFFF;
  font-size: 11px;
  diameter: 40px;
  caption: '{name}';
}

node.Attack {
  color: #E74C3C;
  border-color: #C0392B;
  text-color-internal: #FFFFFF;
  font-size: 11px;
  diameter: 60px;
  caption: '{label}';
}
```

---

## Relationship Styling

| Relationship | Color | Width | Description |
|---|---|---|---|
| `INITIATED` | `#888888` (grey) | 1px | Source host → Flow |
| `TARGETS` | `#888888` (grey) | 1px | Flow → Destination host |
| `COMMUNICATES_WITH` | `#CCCCCC` (light grey) | 1px | Host-to-host summary |
| `USES_PROTOCOL` | `#27AE60` (green) | 2px | Flow → Protocol |
| `HAS_ATTACK_TYPE` | `#E74C3C` (red) | 3px | Flow → Attack type |
| `PREDICTED_AS` | `#F39C12` (orange) | 2px | ML prediction (future) |

```css
relationship.COMMUNICATES_WITH {
  color: #CCCCCC;
  shaft-width: 1px;
  font-size: 8px;
  text-color-external: #999999;
  caption: 'comm';
}

relationship.HAS_ATTACK_TYPE {
  color: #E74C3C;
  shaft-width: 3px;
  font-size: 9px;
  text-color-external: #E74C3C;
  caption: 'attack';
}

relationship.USES_PROTOCOL {
  color: #27AE60;
  shaft-width: 2px;
  font-size: 8px;
  text-color-external: #27AE60;
  caption: 'protocol';
}

relationship.INITIATED {
  color: #888888;
  shaft-width: 1px;
}

relationship.TARGETS {
  color: #888888;
  shaft-width: 1px;
}
```

---

## Essential Cypher Queries

### 1. Full Flow Graph (Start Here)

See the complete flow-centric pattern:

```cypher
MATCH (src:Host)-[:INITIATED]->(f:Flow)-[:TARGETS]->(dst:Host)
OPTIONAL MATCH (f)-[:USES_PROTOCOL]->(p:Protocol)
OPTIONAL MATCH (f)-[:HAS_ATTACK_TYPE]->(a:Attack)
RETURN src, f, dst, p, a
LIMIT 50
```

### 2. Attack Flows Only

Show only malicious flows with their attack classifications:

```cypher
MATCH (src:Host)-[:INITIATED]->(f:Flow)-[:TARGETS]->(dst:Host)
WHERE f.label <> 'BenignTraffic'
MATCH (f)-[:HAS_ATTACK_TYPE]->(a:Attack)
OPTIONAL MATCH (f)-[:USES_PROTOCOL]->(p:Protocol)
RETURN src, f, dst, a, p
LIMIT 100
```

### 3. Attack Path Trace (Host A → Host B)

Trace all attack flows between two specific hosts:

```cypher
MATCH path = (src:Host {ip: $srcIp})-[:INITIATED]->(f:Flow)-[:TARGETS]->(dst:Host {ip: $dstIp})
WHERE f.label <> 'BenignTraffic'
MATCH (f)-[:HAS_ATTACK_TYPE]->(a:Attack)
RETURN path, a
ORDER BY f.ts
```

### 4. Most Attacked Hosts (Top 10)

Find hosts receiving the most attack flows:

```cypher
MATCH (f:Flow)-[:TARGETS]->(h:Host)
WHERE f.label <> 'BenignTraffic'
WITH h, count(f) AS attack_count, collect(DISTINCT f.label) AS attack_types
RETURN h.ip AS victim_ip,
       attack_count,
       attack_types,
       size(attack_types) AS unique_attack_types
ORDER BY attack_count DESC
LIMIT 10
```

### 5. Most Active Attackers (Top 10)

Find hosts initiating the most attack flows:

```cypher
MATCH (h:Host)-[:INITIATED]->(f:Flow)
WHERE f.label <> 'BenignTraffic'
WITH h, count(f) AS attack_count,
     collect(DISTINCT f.label) AS attack_types,
     count(DISTINCT f.dst_ip) AS unique_targets
RETURN h.ip AS attacker_ip,
       attack_count,
       unique_targets,
       attack_types
ORDER BY attack_count DESC
LIMIT 10
```

### 6. Protocol Distribution

See which protocols are used in attacks vs benign traffic:

```cypher
MATCH (f:Flow)-[:USES_PROTOCOL]->(p:Protocol)
WITH p.name AS protocol,
     count(f) AS total_flows,
     count(CASE WHEN f.label <> 'BenignTraffic' THEN 1 END) AS attack_flows
RETURN protocol, total_flows, attack_flows,
       round(toFloat(attack_flows) / total_flows * 100, 1) AS attack_pct
ORDER BY total_flows DESC
```

### 7. Attack Type Breakdown

Get counts per attack type:

```cypher
MATCH (a:Attack)<-[:HAS_ATTACK_TYPE]-(f:Flow)
WITH a.label AS attack, a.subLabel AS sub_attack,
     count(f) AS flow_count,
     count(DISTINCT f.src_ip) AS unique_sources,
     count(DISTINCT f.dst_ip) AS unique_targets
RETURN attack, sub_attack, flow_count, unique_sources, unique_targets
ORDER BY flow_count DESC
```

### 8. Communication Clusters

Find dense host communication clusters:

```cypher
MATCH (h1:Host)-[c:COMMUNICATES_WITH]->(h2:Host)
WHERE c.flow_count > 10
RETURN h1, c, h2
ORDER BY c.flow_count DESC
LIMIT 100
```

### 9. Timeline of Attacks on a Host

Show attack timeline for a specific victim host:

```cypher
MATCH (f:Flow)-[:TARGETS]->(h:Host {ip: $targetIp})
WHERE f.label <> 'BenignTraffic'
MATCH (src:Host)-[:INITIATED]->(f)
OPTIONAL MATCH (f)-[:HAS_ATTACK_TYPE]->(a:Attack)
RETURN f.ts AS timestamp,
       src.ip AS attacker,
       f.label AS attack_label,
       f.sublabel AS sub_label,
       f.protocol AS protocol,
       a.subLabelCat AS category
ORDER BY f.ts ASC
```

### 10. Graph Stats Dashboard

Get overall graph statistics:

```cypher
CALL {
  MATCH (h:Host) RETURN 'Hosts' AS label, count(h) AS count
  UNION ALL
  MATCH (f:Flow) RETURN 'Flows' AS label, count(f) AS count
  UNION ALL
  MATCH (f:Flow) WHERE f.label <> 'BenignTraffic'
  RETURN 'Attack Flows' AS label, count(f) AS count
  UNION ALL
  MATCH (p:Protocol) RETURN 'Protocols' AS label, count(p) AS count
  UNION ALL
  MATCH (a:Attack) RETURN 'Attack Types' AS label, count(a) AS count
}
RETURN label, count
```

---

## Neo4j Bloom (Optional)

If using Neo4j Bloom for interactive exploration:

### Search Phrases
- `Show all hosts` → `MATCH (h:Host) RETURN h`
- `Show attacks` → `MATCH (a:Attack) RETURN a`
- `Find flows from {ip}` → `MATCH (h:Host {ip: $ip})-[:INITIATED]->(f:Flow) RETURN h, f`

### Perspective Setup
1. Create a new perspective called **"ChainBreaker Flow Graph"**
2. Add all node labels: `Host`, `Flow`, `Protocol`, `Attack`
3. Set node colors as described in the styling table above
4. Set relationship colors as described in the relationship table
5. Enable property panels for `Flow` nodes to see all numeric features

---

## ML Integration (Future)

When ML predictions are added, use this query to explore predicted attacks:

```cypher
MATCH (f:Flow)-[:PREDICTED_AS]->(a:Attack)
WHERE f.confidence_score > 0.8
MATCH (src:Host)-[:INITIATED]->(f)-[:TARGETS]->(dst:Host)
RETURN src.ip AS source, dst.ip AS target,
       a.label AS predicted_attack,
       f.confidence_score AS confidence,
       f.predicted_label AS model_label
ORDER BY f.confidence_score DESC
LIMIT 50
```
