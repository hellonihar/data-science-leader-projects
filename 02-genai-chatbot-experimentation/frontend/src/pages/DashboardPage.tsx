import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, CartesianGrid } from 'recharts';
import { api } from '../services/api';
import type { Experiment, ExperimentMetrics, VariantMetrics } from '../types';

export default function DashboardPage() {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [selectedId, setSelectedId] = useState<string>('');
  const [metrics, setMetrics] = useState<ExperimentMetrics | null>(null);
  const [halluDist, setHalluDist] = useState<Record<string, number>>({});
  const [latencyData, setLatencyData] = useState<Record<string, { avg_ms: number; median_ms: number; p95_ms: number; count: number }>>({});

  useEffect(() => {
    api.listExperiments().then(setExperiments).catch(() => {});
    api.getHallucinationDistribution().then(d => setHalluDist(d.distribution)).catch(() => {});
    api.getLatencyComparison().then(setLatencyData).catch(() => {});
  }, []);

  useEffect(() => {
    if (selectedId) {
      api.getExperimentMetrics(selectedId).then(setMetrics).catch(() => {});
    }
  }, [selectedId]);

  const buildComparisonChart = (key: keyof VariantMetrics, label: string) => {
    if (!metrics) return [];
    return Object.entries(metrics.metrics).map(([v, m]) => ({
      variant: `Variant ${v}`,
      [label]: m[key],
    }));
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Analytics Dashboard</h1>

      <div className="mb-6">
        <select
          className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm w-full max-w-md"
          value={selectedId}
          onChange={e => setSelectedId(e.target.value)}
        >
          <option value="">Select experiment...</option>
          {experiments.map(e => (
            <option key={e.id} value={e.id}>{e.name} ({e.status})</option>
          ))}
        </select>
      </div>

      {metrics && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(metrics.metrics).map(([variant, m]) => (
              <div key={variant} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <h3 className="text-sm text-gray-400 mb-1">Variant {variant}</h3>
                <p className="text-2xl font-bold">{(m.resolution_rate * 100).toFixed(1)}%</p>
                <p className="text-xs text-gray-500">Resolution Rate</p>
                <div className="mt-2 text-xs text-gray-400 space-y-1">
                  <p>Messages: {m.message_count}</p>
                  <p>Avg Hallu: {m.avg_hallucination_score.toFixed(3)}</p>
                  <p>P95 Latency: {m.p95_latency_ms}ms</p>
                  <p>Avg Rating: {m.avg_rating.toFixed(2)}</p>
                  <p>Avg Tokens: {m.avg_token_count}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h2 className="text-lg font-semibold mb-4">Head-to-Head Comparison</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-400 mb-2">Resolution Rate</p>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={buildComparisonChart('resolution_rate', 'Rate')}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="variant" stroke="#9CA3AF" />
                    <YAxis stroke="#9CA3AF" domain={[0, 1]} />
                    <Tooltip />
                    <Bar dataKey="Rate" fill="#3B82F6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div>
                <p className="text-sm text-gray-400 mb-2">Avg Hallucination Score</p>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={buildComparisonChart('avg_hallucination_score', 'Score')}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="variant" stroke="#9CA3AF" />
                    <YAxis stroke="#9CA3AF" domain={[0, 1]} />
                    <Tooltip />
                    <Bar dataKey="Score" fill="#10B981" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {metrics.statistical_significance?.resolution_rate && (
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h2 className="text-lg font-semibold mb-2">Statistical Significance</h2>
              <pre className="text-sm text-gray-400">
                {JSON.stringify(metrics.statistical_significance, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}

      {!selectedId && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h2 className="text-lg font-semibold mb-4">Hallucination Distribution (All Experiments)</h2>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={Object.entries(halluDist).map(([k, v]) => ({ category: k, count: v }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="category" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip />
                <Bar dataKey="count" fill="#8B5CF6" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h2 className="text-lg font-semibold mb-4">Latency Comparison (All Experiments)</h2>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={Object.entries(latencyData).map(([k, v]) => ({ variant: `Variant ${k}`, ...v }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="variant" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip />
                <Legend />
                <Bar dataKey="avg_ms" fill="#3B82F6" name="Avg (ms)" />
                <Bar dataKey="p95_ms" fill="#F59E0B" name="P95 (ms)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
