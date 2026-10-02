import React from 'react';
import { Droplet, Zap, ShieldAlert, CheckCircle2, AlertTriangle, XCircle, MapPin, Gauge } from 'lucide-react';

export default function ScoreCard({ site }) {
  if (!site) {
    return (
      <div className="glass-panel p-6 rounded-xl flex items-center justify-center text-slate-500 min-h-[220px]">
        Select a site to view composite assessment
      </div>
    );
  }

  const compositeScore = site.composite_score || 0;
  const waterScore = site.water_score || 0;
  const powerScore = site.power_score || 0;
  const tierColor = site.tier_color || '#10B981';
  const tierBadge = site.tier_badge || 'VIABLE';
  const tier = site.tier || 'VIABLE / RECOMMENDED';

  // Tier Icon
  const renderTierIcon = () => {
    if (compositeScore >= 75.0) {
      return <CheckCircle2 className="w-5 h-5 text-emerald-400" />;
    } else if (compositeScore >= 50.0) {
      return <AlertTriangle className="w-5 h-5 text-amber-400" />;
    } else {
      return <XCircle className="w-5 h-5 text-rose-400" />;
    }
  };

  return (
    <div className="glass-panel p-6 rounded-xl border border-slate-800 shadow-xl relative overflow-hidden">
      {/* Background glow based on tier */}
      <div 
        className="absolute -top-24 -right-24 w-60 h-60 rounded-full blur-3xl opacity-20 pointer-events-none"
        style={{ background: tierColor }}
      />

      {/* Header with Site Name and Badge */}
      <div className="flex flex-wrap items-start justify-between gap-3 mb-6">
        <div>
          <div className="flex items-center gap-1.5 text-xs text-slate-400 font-mono mb-1">
            <MapPin className="w-3.5 h-3.5 text-cyan-400" />
            <span>{site.district}, {site.state}</span>
            <span className="text-slate-600">•</span>
            <span>Elev: {site.elevation_m}m</span>
          </div>
          <h2 className="text-2xl font-bold font-display text-white tracking-tight">
            {site.site_name}
          </h2>
        </div>

        {/* Status Badge */}
        <div 
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-full border text-xs font-bold tracking-wide shadow-sm"
          style={{ 
            backgroundColor: `${tierColor}18`, 
            borderColor: `${tierColor}44`,
            color: tierColor 
          }}
        >
          {renderTierIcon()}
          <span>{tier}</span>
        </div>
      </div>

      {/* Primary Score Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
        
        {/* Composite Gauge Box */}
        <div className="glass-panel-elevated p-5 rounded-xl border border-slate-700/60 flex flex-col items-center justify-center text-center relative">
          <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400 mb-1 flex items-center gap-1">
            <Gauge className="w-3.5 h-3.5 text-cyan-400" />
            Composite Site Score
          </div>
          
          <div className="relative my-2 flex items-baseline justify-center">
            <span 
              className="text-5xl font-black font-display tracking-tight"
              style={{ color: tierColor }}
            >
              {compositeScore.toFixed(1)}
            </span>
            <span className="text-slate-500 font-mono text-sm ml-1">/100</span>
          </div>

          <div className="text-[11px] text-slate-400 font-mono">
            45% Water • 55% Power
          </div>
        </div>

        {/* 7-Model Water Engine Score */}
        <div className="glass-panel p-4 rounded-xl border border-sky-900/30 flex flex-col justify-between h-full hover:border-sky-500/40 transition-colors">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/20">
                <Droplet className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm font-semibold text-white">7-Model Water Engine</div>
                <div className="text-[11px] text-slate-400 font-mono">CGWA Hydrological Baseline</div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold font-display text-sky-400">
                {waterScore.toFixed(1)}
              </div>
              <div className="text-[10px] text-slate-500 font-mono">Weight: 45%</div>
            </div>
          </div>

          <div className="mt-3">
            <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
              <div 
                className="bg-sky-400 h-2 rounded-full transition-all duration-700"
                style={{ width: `${Math.min(100, Math.max(0, waterScore))}%` }}
              />
            </div>
            <div className="flex justify-between text-[11px] text-slate-400 font-mono mt-1.5">
              <span>Status: {site.water_assessment?.stress_flag_triggered ? '⚠️ Stress Flagged' : 'Normal'}</span>
              <span>7 Sub-models</span>
            </div>
          </div>
        </div>

        {/* 4-Metric Power Grid Score */}
        <div className="glass-panel p-4 rounded-xl border border-amber-900/30 flex flex-col justify-between h-full hover:border-amber-500/40 transition-colors">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
                <Zap className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm font-semibold text-white">Electrical Grid Pipeline</div>
                <div className="text-[11px] text-slate-400 font-mono">CEA Transmission Planning</div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold font-display text-amber-400">
                {powerScore.toFixed(1)}
              </div>
              <div className="text-[10px] text-slate-500 font-mono">Weight: 55%</div>
            </div>
          </div>

          <div className="mt-3">
            <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
              <div 
                className="bg-amber-400 h-2 rounded-full transition-all duration-700"
                style={{ width: `${Math.min(100, Math.max(0, powerScore))}%` }}
              />
            </div>
            <div className="flex justify-between text-[11px] text-slate-400 font-mono mt-1.5">
              <span>Target Load: {site.proposed_it_load_mw} MW</span>
              <span>4 Metrics</span>
            </div>
          </div>
        </div>

      </div>

      {/* Target Infrastructure Spec footer */}
      <div className="mt-4 pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between text-xs text-slate-400 font-mono">
        <div className="flex items-center gap-4">
          <span>Target AI Load: <strong className="text-slate-200">{site.proposed_it_load_mw} MW</strong></span>
          <span>•</span>
          <span>Lat/Lon: <strong className="text-slate-200">{site.latitude.toFixed(4)}, {site.longitude.toFixed(4)}</strong></span>
        </div>
        <div className="text-[11px] text-slate-500">
          SuperIndia.ai Engine v1.0 • Deterministic CGWA/CEA Architecture
        </div>
      </div>
    </div>
  );
}
