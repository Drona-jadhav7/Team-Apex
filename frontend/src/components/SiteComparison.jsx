import React from 'react';
import { BarChart3, Trophy, ArrowRight, ShieldAlert, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';

export default function SiteComparison({ sites = [], selectedSite = null, onSelectSite }) {
  if (!sites || sites.length === 0) return null;

  // Sort sites descending by composite score
  const sortedSites = [...sites].sort((a, b) => (b.composite_score || 0) - (a.composite_score || 0));
  const topSite = sortedSites[0];

  const getTierBadgeClass = (tierBadge) => {
    switch (tierBadge) {
      case 'VIABLE':
        return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
      case 'CONDITIONAL':
        return 'bg-amber-500/15 text-amber-400 border-amber-500/30';
      case 'UNVIABLE':
        return 'bg-rose-500/15 text-rose-400 border-rose-500/30';
      default:
        return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  return (
    <div className="glass-panel p-6 rounded-xl border border-slate-800 shadow-xl space-y-5">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div>
          <h3 className="text-lg font-bold font-display text-white flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-cyan-400" />
            National AI Infrastructure Multi-Site Audit Matrix
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Comparative evaluation across 5 strategic hubs ranked by deterministic composite viability.
          </p>
        </div>

        {topSite && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-950/30 border border-emerald-500/30 text-xs">
            <Trophy className="w-4 h-4 text-emerald-400" />
            <span className="text-slate-300">Top Ranked:</span>
            <strong className="text-emerald-300 font-semibold">{topSite.site_name}</strong>
            <span className="font-mono text-emerald-400">({topSite.composite_score.toFixed(1)})</span>
          </div>
        )}
      </div>

      {/* Comparison Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 font-mono text-[11px] uppercase tracking-wider bg-slate-900/60">
              <th className="py-3 px-3">Rank</th>
              <th className="py-3 px-3">Candidate Hub</th>
              <th className="py-3 px-3">State / District</th>
              <th className="py-3 px-3">Composite Score</th>
              <th className="py-3 px-3">Classification</th>
              <th className="py-3 px-3">Water Score (45%)</th>
              <th className="py-3 px-3">Power Score (55%)</th>
              <th className="py-3 px-3">Risk Flags</th>
              <th className="py-3 px-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {sortedSites.map((site, index) => {
              const isSelected = selectedSite && selectedSite.site_id === site.site_id;
              const rank = index + 1;
              const hasFlags = site.risk_flags && site.risk_flags.length > 0;

              return (
                <tr 
                  key={site.site_id || index}
                  onClick={() => onSelectSite && onSelectSite(site)}
                  className={`cursor-pointer transition-colors ${
                    isSelected 
                      ? 'bg-cyan-950/30 text-white font-medium' 
                      : 'hover:bg-slate-900/40 text-slate-300'
                  }`}
                >
                  {/* Rank */}
                  <td className="py-3 px-3 font-mono font-bold">
                    <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs ${
                      rank === 1 ? 'bg-amber-400/20 text-amber-300 border border-amber-400/40' : 'bg-slate-800 text-slate-400'
                    }`}>
                      {rank}
                    </span>
                  </td>

                  {/* Hub Name */}
                  <td className="py-3 px-3">
                    <div className="font-semibold text-white font-display text-sm">
                      {site.site_name}
                    </div>
                    <div className="text-[10px] text-slate-500 font-mono">
                      Elev: {site.elevation_m}m • Load: {site.proposed_it_load_mw}MW
                    </div>
                  </td>

                  {/* State */}
                  <td className="py-3 px-3 font-mono text-[11px] text-slate-400">
                    {site.state}
                  </td>

                  {/* Composite Score */}
                  <td className="py-3 px-3">
                    <div className="flex items-center gap-2">
                      <span 
                        className="font-bold font-display text-sm"
                        style={{ color: site.tier_color || '#10B981' }}
                      >
                        {site.composite_score.toFixed(1)}
                      </span>
                      <div className="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                        <div 
                          className="h-1.5 rounded-full"
                          style={{ 
                            width: `${site.composite_score}%`, 
                            backgroundColor: site.tier_color || '#10B981' 
                          }}
                        />
                      </div>
                    </div>
                  </td>

                  {/* Tier Badge */}
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono border ${getTierBadgeClass(site.tier_badge)}`}>
                      {site.tier_badge}
                    </span>
                  </td>

                  {/* Water Score */}
                  <td className="py-3 px-3 font-mono">
                    <span className="text-sky-400 font-bold">{site.water_score.toFixed(1)}</span>
                    <span className="text-[10px] text-slate-500 ml-1">/100</span>
                  </td>

                  {/* Power Score */}
                  <td className="py-3 px-3 font-mono">
                    <span className="text-amber-400 font-bold">{site.power_score.toFixed(1)}</span>
                    <span className="text-[10px] text-slate-500 ml-1">/100</span>
                  </td>

                  {/* Flags */}
                  <td className="py-3 px-3">
                    {hasFlags ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono bg-rose-500/20 text-rose-300 border border-rose-500/30">
                        <ShieldAlert className="w-3 h-3" />
                        {site.risk_flags.length} flag{site.risk_flags.length > 1 ? 's' : ''}
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-[10px] font-mono text-emerald-400">
                        <CheckCircle2 className="w-3 h-3" />
                        Nominal
                      </span>
                    )}
                  </td>

                  {/* Action */}
                  <td className="py-3 px-3 text-right">
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectSite && onSelectSite(site);
                      }}
                      className={`px-2.5 py-1 rounded text-[11px] font-mono transition-colors inline-flex items-center gap-1 ${
                        isSelected 
                          ? 'bg-cyan-500 text-slate-950 font-bold' 
                          : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white'
                      }`}
                    >
                      {isSelected ? 'Active' : 'Inspect'}
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
