# ML Detection Pipeline

## Feature Extraction

Each network flow is converted to a 71-dimensional feature vector:
- **64 CICFlowMeter features** from the standard feature set
- **7 derived features**: bytes_per_packet, packets_per_sec, fwd_ratio, syn_ratio, ack_ratio, packet_size_variance_ratio, iat_cv

## Model Ensemble

Three complementary models vote on each flow:

| Model | Strength | Weight |
|-------|----------|--------|
| Random Forest | Stable, interpretable multi-class | 0.4 |
| XGBoost | High accuracy on structured data | 0.4 |
| Isolation Forest | Zero-day / novel attacks | 0.2 |

Combined confidence = weighted sum of model votes. If combined confidence < 0.65, flow is classified as BENIGN.

## Kill Chain Stage Mapping

| CICAPT-IIoT Label | Kill Chain Stage |
|-------------------|-----------------|
| BruteForce | Initial_Access |
| Mirai | Initial_Access |
| PortScan | Discovery |
| Backdoor | Persistence |
| C2 | Command_and_Control |
| LateralMovement | Lateral_Movement |
| CredentialTheft | Credential_Access |
| Ransomware | Exfiltration |
| Evasion | Defense_Evasion |
| DDoS/DoS | Denial_of_Service |

## Detection Thresholds

| Parameter | Value |
|-----------|-------|
| RF confidence threshold | 0.70 |
| XGB confidence threshold | 0.70 |
| IF contamination | 0.01 |
| IF score threshold | 0.15 |
| Ensemble vote threshold | 0.65 |
