import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

export const graphApi = {
  getHosts: (limit = 100) => api.get(`/graph/hosts?limit=${limit}`),
  getHost: (ip: string) => api.get(`/graph/hosts/${ip}`),
  getEvents: (limit = 100) => api.get(`/graph/events?limit=${limit}`),
  getStages: () => api.get('/graph/stages'),
  getEdges: (limit = 500) => api.get(`/graph/edges?limit=${limit}`),
  getSnapshot: () => api.get('/graph/snapshot'),
};

export const forensicsApi = {
  getTimeline: (limit = 200) => api.get(`/forensics/timeline?limit=${limit}`),
  getHostTimeline: (ip: string) => api.get(`/forensics/timeline/${ip}`),
  getBlastRadius: () => api.get('/forensics/blast-radius'),
  getAffectedAssets: () => api.get('/forensics/affected-assets'),
  getKillChainSummary: () => api.get('/forensics/kill-chain-summary'),
  getAttackPath: (alertId: string) => api.get(`/forensics/attack-path/${alertId}`),
  getReport: (alertId?: string) => api.get('/forensics/report', { params: alertId ? { alert_id: alertId } : {} }),
  getHostReport: (ip: string) => api.get(`/forensics/report/host/${ip}`),
};

export const alertsApi = {
  getAlerts: (params?: { status?: string; severity?: string; limit?: number }) =>
    api.get('/alerts', { params }),
  getAlert: (id: string) => api.get(`/alerts/${id}`),
};

export const mlApi = {
  getStatus: () => api.get('/ml/status'),
  setModel: (model: string) => api.post(`/ml/set-model/${model}`),
};

export const agentApi = {
  getActions: (limit = 50) => api.get(`/agent/actions?limit=${limit}`),
  getStatus: () => api.get('/agent/status'),
};

export default api;
