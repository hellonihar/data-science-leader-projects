import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { Experiment } from '../types';

export default function ExperimentsPage() {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [trafficSplit, setTrafficSplit] = useState(0.5);

  useEffect(() => {
    loadExperiments();
  }, []);

  const loadExperiments = async () => {
    try {
      setExperiments(await api.listExperiments());
    } catch {}
  };

  const handleCreate = async () => {
    try {
      await api.createExperiment({ name, description, traffic_split: trafficSplit });
      setShowForm(false);
      setName('');
      setDescription('');
      setTrafficSplit(0.5);
      loadExperiments();
    } catch {}
  };

  const handleStatusChange = async (id: string, status: string) => {
    try {
      await api.updateExperiment(id, { status } as Partial<Experiment>);
      loadExperiments();
    } catch {}
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Experiments</h1>
        <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'New Experiment'}
        </button>
      </div>

      {showForm && (
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 mb-6">
          <h2 className="text-lg font-semibold mb-4">Create Experiment</h2>
          <div className="space-y-3">
            <input
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm"
              placeholder="Experiment name"
              value={name}
              onChange={e => setName(e.target.value)}
            />
            <textarea
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm"
              placeholder="Description (optional)"
              value={description}
              onChange={e => setDescription(e.target.value)}
              rows={2}
            />
            <div>
              <label className="text-sm text-gray-400">Traffic Split (A: {Math.round(trafficSplit * 100)}% / B: {Math.round((1 - trafficSplit) * 100)}%)</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                className="w-full"
                value={trafficSplit}
                onChange={e => setTrafficSplit(parseFloat(e.target.value))}
              />
            </div>
            <button className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded text-sm" onClick={handleCreate}>
              Create
            </button>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {experiments.length === 0 && (
          <p className="text-gray-500 text-center py-8">No experiments yet. Create one to get started.</p>
        )}
        {experiments.map(e => (
          <div key={e.id} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-semibold">{e.name}</h3>
                {e.description && <p className="text-sm text-gray-400 mt-1">{e.description}</p>}
              </div>
              <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                e.status === 'active' ? 'bg-green-600' :
                e.status === 'archived' ? 'bg-gray-600' :
                'bg-yellow-600'
              }`}>
                {e.status}
              </span>
            </div>
            <div className="flex gap-4 mt-3 text-sm text-gray-400">
              <span>Split: A {Math.round(e.traffic_split * 100)}% / B {Math.round((1 - e.traffic_split) * 100)}%</span>
              <span>Model A: {e.model_a}</span>
              <span>Model B: {e.model_b}</span>
            </div>
            <div className="flex gap-2 mt-3">
              {e.status === 'draft' && (
                <button className="bg-green-600 hover:bg-green-700 px-3 py-1 rounded text-xs" onClick={() => handleStatusChange(e.id, 'active')}>
                  Activate
                </button>
              )}
              {e.status === 'active' && (
                <button className="bg-yellow-600 hover:bg-yellow-700 px-3 py-1 rounded text-xs" onClick={() => handleStatusChange(e.id, 'archived')}>
                  Archive
                </button>
              )}
              {e.status === 'archived' && (
                <button className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-xs" onClick={() => handleStatusChange(e.id, 'draft')}>
                  Reopen
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
