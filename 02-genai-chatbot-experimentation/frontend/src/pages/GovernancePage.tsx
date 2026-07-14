import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { FairnessMetrics, AuditEntry } from '../types';

export default function GovernancePage() {
  const [fairness, setFairness] = useState<FairnessMetrics | null>(null);
  const [auditLog, setAuditLog] = useState<AuditEntry[]>([]);
  const [messageId, setMessageId] = useState('');
  const [transparency, setTransparency] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    api.getFairnessMetrics().then(setFairness).catch(() => {});
    api.getAuditLog().then(setAuditLog).catch(() => {});
  }, []);

  const handleTransparency = async () => {
    if (!messageId) return;
    try {
      setTransparency(await api.getTransparency(messageId));
    } catch {
      setTransparency({ error: 'Message not found' });
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Governance Dashboard</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h2 className="text-lg font-semibold mb-4">Fairness Metrics</h2>
          {fairness ? (
            <div>
              <div className="mb-3">
                <p className="text-sm text-gray-400">Fairness Gap</p>
                <p className={`text-xl font-bold ${fairness.fairness_gap > 0.5 ? 'text-red-400' : 'text-green-400'}`}>
                  {fairness.fairness_gap.toFixed(4)}
                </p>
              </div>
              <div className="space-y-2">
                {Object.entries(fairness.metrics_by_variant).map(([v, m]) => (
                  <div key={v} className="bg-gray-700/50 rounded p-3">
                    <p className="text-sm font-semibold">Variant {v}</p>
                    <p className="text-xs text-gray-400">Messages: {m.total_messages} | Avg Rating: {m.avg_rating.toFixed(2)} | Rated: {m.rated_count}</p>
                  </div>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-3">{fairness.note}</p>
            </div>
          ) : (
            <p className="text-gray-500 text-sm">Loading...</p>
          )}
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h2 className="text-lg font-semibold mb-4">Transparency Lookup</h2>
          <div className="flex gap-2 mb-3">
            <input
              className="flex-1 bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm"
              placeholder="Enter message ID"
              value={messageId}
              onChange={e => setMessageId(e.target.value)}
            />
            <button className="bg-blue-600 hover:bg-blue-700 px-3 py-2 rounded text-sm" onClick={handleTransparency}>
              Lookup
            </button>
          </div>
          {transparency && (
            <pre className="text-xs text-gray-400 bg-gray-700/50 rounded p-3 overflow-auto max-h-60">
              {JSON.stringify(transparency, null, 2)}
            </pre>
          )}
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h2 className="text-lg font-semibold mb-4">Audit Trail</h2>
        {auditLog.length === 0 ? (
          <p className="text-gray-500 text-sm">No audit entries yet.</p>
        ) : (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {auditLog.map(entry => (
              <div key={entry.id} className="bg-gray-700/50 rounded p-3 text-sm">
                <div className="flex gap-2 items-center">
                  <span className="bg-gray-600 px-2 py-0.5 rounded text-xs font-mono">{entry.action}</span>
                  <span className="text-gray-400 text-xs">{entry.entity_type}</span>
                  {entry.entity_id && <span className="text-gray-500 text-xs font-mono">{entry.entity_id.slice(0, 8)}...</span>}
                  <span className="text-gray-500 text-xs ml-auto">{new Date(entry.created_at).toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
