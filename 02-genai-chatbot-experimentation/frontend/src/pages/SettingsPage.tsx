import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { DynamicSetting } from '../types';
import { RotateCcw, Save } from 'lucide-react';

const CATEGORIES = [
  { id: 'hallucination', label: 'Hallucination Scoring', color: 'bg-purple-600' },
  { id: 'rag', label: 'RAG Pipeline', color: 'bg-blue-600' },
  { id: 'llm', label: 'LLM Configuration', color: 'bg-green-600' },
  { id: 'analytics', label: 'Analytics & Statistics', color: 'bg-yellow-600' },
  { id: 'experiment', label: 'Experiment Defaults', color: 'bg-red-600' },
];

export default function SettingsPage() {
  const [settings, setSettings] = useState<DynamicSetting[]>([]);
  const [activeCategory, setActiveCategory] = useState<string>('hallucination');
  const [editingValues, setEditingValues] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState<Record<string, boolean>>({});
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadSettings();
  }, [activeCategory]);

  const loadSettings = async () => {
    try {
      const data = await api.listSettings(activeCategory);
      setSettings(data);
      const values: Record<string, string> = {};
      data.forEach(s => { values[s.key] = s.current_value || s.value; });
      setEditingValues(values);
    } catch {}
  };

  const handleSave = async (key: string) => {
    setSaving(prev => ({ ...prev, [key]: true }));
    try {
      await api.updateSetting(key, editingValues[key]);
      setMessage(`Saved ${key}`);
      loadSettings();
    } catch {
      setMessage(`Failed to save ${key}`);
    }
    setSaving(prev => ({ ...prev, [key]: false }));
    setTimeout(() => setMessage(''), 3000);
  };

  const handleReset = async (key: string) => {
    try {
      await api.resetSetting(key);
      setMessage(`Reset ${key} to default`);
      loadSettings();
    } catch {
      setMessage(`Failed to reset ${key}`);
    }
    setTimeout(() => setMessage(''), 3000);
  };

  const handleResetCategory = async () => {
    try {
      const result = await api.resetCategory(activeCategory);
      setMessage(result.message);
      loadSettings();
    } catch {
      setMessage(`Failed to reset category`);
    }
    setTimeout(() => setMessage(''), 3000);
  };

  const renderValueEditor = (setting: DynamicSetting) => {
    const val = editingValues[setting.key] ?? '';
    const isBool = setting.value_type === 'bool';

    if (isBool) {
      return (
        <select
          className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm min-w-[120px]"
          value={val}
          onChange={e => setEditingValues(prev => ({ ...prev, [setting.key]: e.target.value }))}
        >
          <option value="true">Enabled</option>
          <option value="false">Disabled</option>
        </select>
      );
    }

    if (setting.min_value !== undefined && setting.max_value !== undefined && setting.value_type === 'float') {
      const numVal = parseFloat(val) || 0;
      return (
        <div className="flex items-center gap-3">
          <input
            type="range"
            min={setting.min_value}
            max={setting.max_value}
            step="0.01"
            className="w-40"
            value={numVal}
            onChange={e => setEditingValues(prev => ({ ...prev, [setting.key]: e.target.value }))}
          />
          <span className="text-sm font-mono w-16 text-right">{numVal.toFixed(3)}</span>
        </div>
      );
    }

    if (setting.min_value !== undefined && setting.max_value !== undefined && setting.value_type === 'int') {
      const intVal = parseInt(val) || 0;
      return (
        <div className="flex items-center gap-3">
          <input
            type="range"
            min={setting.min_value}
            max={setting.max_value}
            step="1"
            className="w-40"
            value={intVal}
            onChange={e => setEditingValues(prev => ({ ...prev, [setting.key]: e.target.value }))}
          />
          <span className="text-sm font-mono w-16 text-right">{intVal}</span>
        </div>
      );
    }

    return (
      <input
        className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm font-mono min-w-[200px]"
        value={val}
        onChange={e => setEditingValues(prev => ({ ...prev, [setting.key]: e.target.value }))}
      />
    );
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">System Settings</h1>
        <button
          className="bg-red-700 hover:bg-red-800 text-white px-3 py-1.5 rounded text-xs"
          onClick={handleResetCategory}
        >
          Reset All in Category
        </button>
      </div>

      {message && (
        <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-3 mb-4">
          <p className="text-sm text-blue-400">{message}</p>
        </div>
      )}

      <div className="flex gap-2 mb-6 flex-wrap">
        {CATEGORIES.map(cat => (
          <button
            key={cat.id}
            className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
              activeCategory === cat.id
                ? `${cat.color} text-white`
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
            onClick={() => setActiveCategory(cat.id)}
          >
            {cat.label}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {settings.length === 0 && (
          <p className="text-gray-500 text-center py-8">No settings in this category.</p>
        )}
        {settings.map(setting => (
          <div key={setting.key} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-semibold">{setting.label}</h3>
                <p className="text-xs text-gray-500 mt-0.5">{setting.description}</p>
                <p className="text-xs text-gray-600 mt-1 font-mono">Key: {setting.key}</p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {renderValueEditor(setting)}
                <button
                  className="p-2 rounded hover:bg-gray-700 text-gray-400 hover:text-white transition-colors"
                  onClick={() => handleSave(setting.key)}
                  title="Save"
                >
                  {saving[setting.key] ? <span className="text-xs">...</span> : <Save size={16} />}
                </button>
                <button
                  className="p-2 rounded hover:bg-gray-700 text-gray-500 hover:text-yellow-400 transition-colors"
                  onClick={() => handleReset(setting.key)}
                  title="Reset to default"
                >
                  <RotateCcw size={14} />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
