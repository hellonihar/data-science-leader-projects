export interface RecommendationItem {
  item_id: string;
  name: string;
  category: string;
  price: number;
  score: number;
}

export interface RecommendationResponse {
  user_id: string;
  variant: string;
  experiment_id: string | null;
  recommendations: RecommendationItem[];
  model: string;
}

export interface Experiment {
  id: string;
  name: string;
  description: string | null;
  status: string;
  traffic_split: number;
  variant_a_label: string;
  variant_b_label: string;
  start_date: string | null;
  end_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface ExperimentCreate {
  name: string;
  description?: string;
  traffic_split?: number;
  variant_a_label?: string;
  variant_b_label?: string;
}

export interface VariantMetrics {
  variant: string;
  total_users: number;
  total_impressions: number;
  total_clicks: number;
  total_conversions: number;
  total_revenue: number;
  ctr: number;
  conversion_rate: number;
  revenue_per_user: number;
}

export interface ExperimentAnalytics {
  experiment_id: string;
  experiment_name: string;
  status: string;
  variants: VariantMetrics[];
  winner: string | null;
  p_value: number | null;
  significant: boolean | null;
  revenue_lift: number | null;
  ctr_lift: number | null;
  updated_at: string | null;
}
