import { useState } from "react";
import { getRecommendations } from "../api/client";
import type { RecommendationResponse } from "../api/types";

export default function Recommendations() {
  const [userId, setUserId] = useState("a1b2c3d4-...");
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleGetRecs = async () => {
    setLoading(true);
    try {
      const data = await getRecommendations(userId, 10);
      setResult(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <h2>Recommendations Demo</h2>

      <div className="recs-controls">
        <div className="form-group">
          <label>User ID</label>
          <input
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="Enter user UUID"
          />
        </div>
        <button
          onClick={handleGetRecs}
          disabled={loading}
          className="btn-primary"
        >
          {loading ? "Loading..." : "Get Recommendations"}
        </button>
      </div>

      {result && (
        <div className="recs-result">
          <div className="recs-meta">
            <span className="badge">Model: {result.model}</span>
            <span className="badge">Variant: {result.variant}</span>
            {result.experiment_id && (
              <span className="badge">
                Experiment: {result.experiment_id.slice(0, 8)}...
              </span>
            )}
          </div>

          <table className="recs-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Item</th>
                <th>Category</th>
                <th>Price</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {result.recommendations.map((item, i) => (
                <tr key={item.item_id}>
                  <td>{i + 1}</td>
                  <td>{item.name}</td>
                  <td>{item.category}</td>
                  <td>${item.price.toFixed(2)}</td>
                  <td>{item.score.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
