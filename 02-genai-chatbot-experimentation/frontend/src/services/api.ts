const API_BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`API error ${res.status}: ${err}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  // Chat
  chat: (body: { user_id: string; experiment_id: string; message: string; conversation_id?: string }) =>
    request<import('../types').ChatResponse>('/chat', { method: 'POST', body: JSON.stringify(body) }),

  listConversations: (userId: string) =>
    request<import('../types').Conversation[]>(`/chat/conversations?user_id=${userId}`),

  getConversation: (id: string) =>
    request<import('../types').ConversationDetail>(`/chat/conversations/${id}`),

  deleteConversation: (id: string) =>
    request<void>(`/chat/conversations/${id}`, { method: 'DELETE' }),

  // Feedback
  submitFeedback: (body: import('../types').FeedbackPayload) =>
    request<void>('/feedback', { method: 'POST', body: JSON.stringify(body) }),

  // Experiments
  listExperiments: () =>
    request<import('../types').Experiment[]>('/experiments'),

  createExperiment: (body: { name: string; description?: string; traffic_split?: number }) =>
    request<import('../types').Experiment>('/experiments', { method: 'POST', body: JSON.stringify(body) }),

  getExperiment: (id: string) =>
    request<import('../types').Experiment>(`/experiments/${id}`),

  updateExperiment: (id: string, body: Partial<import('../types').Experiment>) =>
    request<import('../types').Experiment>(`/experiments/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),

  // Documents
  uploadDocument: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return request<{ filename: string; chunks_count: number; message: string }>('/documents/upload', { method: 'POST', body: form });
  },

  listDocuments: () =>
    request<{ filename: string; metadata: Record<string, unknown> }[]>('/documents'),

  deleteDocument: (id: string) =>
    request<void>(`/documents/${id}`, { method: 'DELETE' }),

  // Analytics
  getExperimentMetrics: (id: string) =>
    request<import('../types').ExperimentMetrics>(`/analytics/experiments/${id}`),

  getHallucinationDistribution: () =>
    request<{ distribution: Record<string, number> }>('/analytics/hallucination'),

  getLatencyComparison: () =>
    request<Record<string, { avg_ms: number; median_ms: number; p95_ms: number; count: number }>>('/analytics/latency'),

  // Governance
  getFairnessMetrics: () =>
    request<import('../types').FairnessMetrics>('/governance/fairness'),

  getAuditLog: () =>
    request<import('../types').AuditEntry[]>('/governance/audit'),

  getTransparency: (messageId: string) =>
    request<import('../types').TransparencyInfo>(`/governance/transparency/${messageId}`),

  // Settings
  listSettings: (category?: string) =>
    request<import('../types').DynamicSetting[]>(`/settings${category ? `?category=${category}` : ''}`),

  getSetting: (key: string) =>
    request<import('../types').DynamicSetting>(`/settings/${key}`),

  updateSetting: (key: string, value: string) =>
    request<import('../types').DynamicSetting>(`/settings/${key}`, { method: 'PUT', body: JSON.stringify({ value }) }),

  resetSetting: (key: string) =>
    request<import('../types').DynamicSetting>(`/settings/reset/${key}`, { method: 'POST' }),

  resetCategory: (category: string) =>
    request<{ message: string }>('/settings/reset-category', { method: 'POST', body: JSON.stringify({ category }) }),
};
