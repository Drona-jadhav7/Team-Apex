import React, { useState } from 'react';
import { Droplet, Zap, AlertTriangle, Info, CheckCircle2 } from 'lucide-react';

export default function ExplainabilityPanel({ site }) {
  const [activeTab, setActiveTab] = useState('water'); // 'water' | 'power' | 'all'

  if (!site) return null;

  const waterMetrics = site.water_assessment?.sub_metrics || [];
  const powerMetrics = site.power_assessment?.sub_metrics || [];

  const getScoreColor = (score, isFlagged) => {
    if (isFlagged || score < 50) return '#EF4444'; // Red
    if (score < 75) return '#F59E0B'; // Amber
    return '#10B981'; // Emerald
  };

  const renderMetricCard = (metric, domainColor = 'sky') => {
    const isFlagged = metric.flagged || false;
    const scoreColor = getScoreColor(metric.score, isFlagged);

    return (
      <div 
        key={metric.key} 
        className={`p-3.5 rounded-lg border transition-all ${
          isFlagged 
            ? 'bg-rose-950/20 border-rose-500/40' 
            : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
        }`}
      >
        <div className="flex flex-wrap items-center justify-between gap-2 mb-1.5">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-white tracking-wide">
              {metric.name}
            </span>
            <span className="text-[10px] font-mono bg-slate-800 text-slate-400 px-2 py-0.5 rounded">
              wt: {(metric.weight * 100).toFixed(0)}%
            </span>
            {isFlagged && (
              <span className="flex items-center gap-1 text-[10px] font-bold font-mono px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
                <AlertTriangle className="w-3 h-3" />
                STRESS FLAG
              </span>
            )}
          </div>

          <div className="flex items-center gap-3">
            <span className="text-[11px] font-mono text-slate-400">
              Contribution: <strong className="text-slate-200">{metric.weighted_score.toFixed(1)} pts</strong>
            </span>
            <span 
              className="text-base font-bold font-display"
              style={{ color: scoreColor }}
            >
              {metric.score.toFixed(1)}
              <span className="text-xs text-slate-500 font-mono">/100</span>
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-slate-800/80 rounded-full h-2 mb-2 overflow-hidden">
          <div 
            className="h-2 rounded-full transition-all duration-500"
            style={{ 
              width: `${Math.min(100, Math.max(0, metric.score))}%`,
              backgroundColor: scoreColor,
            }}
          />
        </div>

        {/* Details & Category */}
        <div className="flex flex-wrap items-start justify-between gap-2 text-xs">
          <span className="text-slate-300 flex-1">
            {metric.details}
          </span>
          <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-slate-800/90 text-slate-300 border border-slate-700/60 shrink-0">
            {metric.category}
          </span>
        </div>
      </div>
    );
  };

  return (
    <div className="glass-panel p-6 rounded-xl border border-slate-800 shadow-xl">
      {/* Header and Filter Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-800">
        <div>
          <h3 className="text-lg font-bold font-display text-white flex items-center gap-2">
            <Info className="w-5 h-5 text-cyan-400" />
            Deterministic Granular Explainability (7+4 Engine)
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Transparent breakdown of individual CGWA water sub-models and CEA electrical transmission metrics.
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center p-1 bg-slate-900 rounded-lg border border-slate-800 text-xs font-medium">
          <button
            onClick={() => setActiveTab('water')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
              activeTab === 'water' 
                ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40 shadow-sm' 
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Droplet className="w-3.5 h-3.5" />
            7 Water Sub-models
          </button>
          <button
            onClick={() => setActiveTab('power')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
              activeTab === 'power' 
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm' 
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Zap className="w-3.5 h-3.5" />
            4 Power Metrics
          </button>
          <button
            onClick={() => setActiveTab('all')}
            className={`px-3 py-1.5 rounded-md transition-all ${
              activeTab === 'all' 
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm' 
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            All 11 Metrics
          </button>
        </div>
      </div>

      {/* Water Sub-models Section */}
      {(activeTab === 'water' || activeTab === 'all') && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-sky-400"></span>
              <h4 className="text-sm font-semibold uppercase tracking-wider font-mono text-sky-400">
                7-Model Water Engine (CGWA Thresholds)
              </h4>
            </div>
            <span className="text-xs font-mono text-slate-400">
              Score: <strong className="text-sky-300">{site.water_score.toFixed(1)}</strong> / 100
            </span>
          </div>

          <div className="grid grid-cols-1 gap-2.5">
            {waterMetrics.map((m) => renderMetricCard(m, 'sky'))}
          </div>
        </div>
      )}

      {/* Power Sub-models Section */}
      {(activeTab === 'power' || activeTab === 'all') && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-400"></span>
              <h4 className="text-sm font-semibold uppercase tracking-wider font-mono text-amber-400">
                4-Metric Electrical Grid Pipeline (CEA Planning)
              </h4>
            </div>
            <span className="text-xs font-mono text-slate-400">
              Score: <strong className="text-amber-300">{site.power_score.toFixed(1)}</strong> / 100
            </span>
          </div>

          <div className="grid grid-cols-1 gap-2.5">
            {powerMetrics.map((m) => renderMetricCard(m, 'amber'))}
          </div>
        </div>
      )}
    </div>
  );
}
