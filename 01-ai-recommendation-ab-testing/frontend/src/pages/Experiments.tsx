import { useEffect, useState } from "react";
import { createExperiment, getExperiments } from "../api/client";
import type { Experiment } from "../api/types";

export default function Experiments() {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    getExperiments().then(setExperiments);
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const exp = await createExperiment({
      name,
      description: description || undefined,
    });
    setExperiments((prev) => [exp, ...prev]);
    setName("");
    setDescription("");
    setShowForm(false);
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>Experiments</h2>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary">
          {showForm ? "Cancel" : "New Experiment"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="exp-form">
          <div className="form-group">
            <label>Experiment Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              placeholder="e.g. CF vs DL v1"
            />
          </div>
          <div className="form-group">
            <label>Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the experiment..."
            />
          </div>
          <button type="submit" className="btn-primary">
            Create Experiment
          </button>
        </form>
      )}

      <div className="experiments-list">
        {experiments.map((exp) => (
          <div key={exp.id} className={`exp-card ${exp.status}`}>
            <div className="exp-card-header">
              <h3>{exp.name}</h3>
              <span className={`status-badge ${exp.status}`}>
                {exp.status}
              </span>
            </div>
            {exp.description && <p>{exp.description}</p>}
            <div className="exp-details">
              <span>Variant A: {exp.variant_a_label}</span>
              <span>Variant B: {exp.variant_b_label}</span>
              <span>Traffic Split: {exp.traffic_split * 100}% /{" "}
                {(1 - exp.traffic_split) * 100}%</span>
            </div>
          </div>
        ))}
        {experiments.length === 0 && (
          <p className="empty-state">
            No experiments yet. Create one to get started.
          </p>
        )}
      </div>
    </div>
  );
}
