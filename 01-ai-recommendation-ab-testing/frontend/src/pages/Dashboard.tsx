import { useEffect, useState } from "react";
import { getExperiments, getExperimentAnalytics } from "../api/client";
import type { Experiment, ExperimentAnalytics } from "../api/types";
import MetricsCard from "../components/MetricsCard";
import ExperimentChart from "../components/ExperimentChart";

export default function Dashboard() {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [analytics, setAnalytics] = useState<ExperimentAnalytics | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    getExperiments().then(setExperiments);
  }, []);

  useEffect(() => {
    if (selectedId) {
      getExperimentAnalytics(selectedId).then(setAnalytics);
    }
  }, [selectedId]);



  return (
    <div className="page">
      <h2>Analytics Dashboard</h2>

      <div className="metrics-grid">
        <MetricsCard title="Total Experiments" value={experiments.length} />
        <MetricsCard
          title="Active Experiments"
          value={experiments.filter((e) => e.status === "active").length}
          highlight
        />
        {analytics?.winner && (
          <MetricsCard
            title="Current Winner"
            value={`Variant ${analytics.winner}`}
            subtitle={
              analytics.significant
                ? "Statistically significant"
                : "Not yet significant"
            }
            highlight={!!analytics.significant}
          />
        )}
        {analytics?.p_value !== null && analytics?.p_value !== undefined && (
          <MetricsCard
            title="P-Value"
            value={analytics.p_value.toFixed(6)}
            subtitle={
              analytics.significant ? "Significant (p < 0.05)" : "Not significant"
            }
          />
        )}
      </div>

      {analytics && analytics.variants.length > 0 && (
        <div className="section">
          <h3>Experiment: {analytics.experiment_name}</h3>
          <div className="variants-table">
            <table>
              <thead>
                <tr>
                  <th>Metric</th>
                  {analytics.variants.map((v) => (
                    <th key={v.variant}>Variant {v.variant}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Impressions</td>
                  {analytics.variants.map((v) => (
                    <td key={v.variant}>{v.total_impressions}</td>
                  ))}
                </tr>
                <tr>
                  <td>Clicks</td>
                  {analytics.variants.map((v) => (
                    <td key={v.variant}>{v.total_clicks}</td>
                  ))}
                </tr>
                <tr>
                  <td>CTR</td>
                  {analytics.variants.map((v) => (
                    <td key={v.variant}>{(v.ctr * 100).toFixed(2)}%</td>
                  ))}
                </tr>
                <tr>
                  <td>Conversion Rate</td>
                  {analytics.variants.map((v) => (
                    <td key={v.variant}>
                      {(v.conversion_rate * 100).toFixed(2)}%
                    </td>
                  ))}
                </tr>
                <tr>
                  <td>Revenue</td>
                  {analytics.variants.map((v) => (
                    <td key={v.variant}>${v.total_revenue.toFixed(2)}</td>
                  ))}
                </tr>
                <tr>
                  <td>Revenue / User</td>
                  {analytics.variants.map((v) => (
                    <td key={v.variant}>${v.revenue_per_user.toFixed(2)}</td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
          <div className="section">
            <h4>Visual Comparison</h4>
            <ExperimentChart variants={analytics.variants} />
          </div>
          {analytics.ctr_lift !== null && (
            <div className="lift-badge">
              CTR Lift: {(analytics.ctr_lift * 100).toFixed(2)}% &nbsp;|&nbsp;
              Revenue Lift:{" "}
              {((analytics.revenue_lift ?? 0) * 100).toFixed(2)}%
            </div>
          )}
        </div>
      )}

      {!selectedId && experiments.length > 0 && (
        <div className="section">
          <h3>Select an experiment to view analytics</h3>
          <div className="experiment-list">
            {experiments.map((exp) => (
              <button
                key={exp.id}
                onClick={() => setSelectedId(exp.id)}
                className={`exp-btn ${exp.status}`}
              >
                {exp.name} ({exp.status})
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
