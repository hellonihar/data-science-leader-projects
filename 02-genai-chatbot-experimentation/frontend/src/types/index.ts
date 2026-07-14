export interface Experiment {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'active' | 'archived';
  traffic_split: number;
  model_a: string;
  model_b: string;
  created_at: string;
  updated_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  experiment_id: string | null;
  created_at: string;
}

export interface MessageItem {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  variant: 'A' | 'B' | null;
  latency_ms: number | null;
  created_at: string;
}

export interface ConversationDetail {
  id: string;
  title: string;
  experiment_id: string | null;
  created_at: string;
  messages: MessageItem[];
}

export interface FeedbackPayload {
  message_id: string;
  rating?: number;
  thumbs_up?: boolean;
}

export interface ChunkInfo {
  id: string;
  content: string;
  score: number;
}

export interface ChatResponse {
  conversation_id: string;
  message_id: string;
  variant: string;
  content: string;
  latency_ms: number;
  retrieved_chunks: ChunkInfo[];
}

export interface DynamicSetting {
  id: string;
  key: string;
  value: string;
  value_type: 'str' | 'int' | 'float' | 'bool';
  label: string;
  description: string;
  category: string;
  min_value?: number;
  max_value?: number;
  current_value?: string;
}

export interface ExperimentMetrics {
  experiment_id: string;
  experiment_name: string;
  experiment_status: string;
  metrics: Record<string, VariantMetrics>;
  statistical_significance: Record<string, unknown>;
}

export interface VariantMetrics {
  message_count: number;
  resolution_rate: number;
  resolved_count: number;
  total_rated: number;
  avg_rating: number;
  avg_hallucination_score: number;
  avg_latency_ms: number;
  p95_latency_ms: number;
  avg_token_count: number;
}

export interface AuditEntry {
  id: string;
  action: string;
  entity_type: string;
  entity_id: string | null;
  details: string | null;
  created_at: string;
}

export interface FairnessMetrics {
  metrics_by_variant: Record<string, { total_messages: number; avg_rating: number; rated_count: number }>;
  fairness_gap: number;
}

export interface TransparencyInfo {
  message_id: string;
  variant: string | null;
  content_preview: string;
  latency_ms: number | null;
  token_count: number | null;
  created_at: string;
  retrieved_chunks?: { id: string; filename: string; content_preview: string }[];
  prompt_template?: string;
}
