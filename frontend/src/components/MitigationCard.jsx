import React from 'react';
import { ShieldAlert, Wrench, FileText, CheckCircle2, AlertOctagon, Terminal } from 'lucide-react';

export default function MitigationCard({ site }) {
  if (!site) return null;

  const riskFlags = site.risk_flags || [];
  const mandates = site.engineering_mandates || [];
  const diagnostics = site.diagnostics || [];
  const hasRisks = riskFlags.length > 0;

  return (
    <div className="glass-panel p-6 rounded-xl border border-slate-800 shadow-xl space-y-6">
      
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div>
          <h3 className="text-lg font-bold font-display text-white flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-rose-400" />
            Automated Diagnostic & Engineering Mitigation Engine
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Rule-based engineering mandates triggered by CGWA extraction boundaries and CEA reliability criteria.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {hasRisks ? (
            <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold font-mono bg-rose-500/15 text-rose-300 border border-rose-500/30">
              <AlertOctagon className="w-3.5 h-3.5" />
              {riskFlags.length} Risk Flag{riskFlags.length > 1 ? 's' : ''} Fired
            </span>
          ) : (
            <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold font-mono bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Zero Critical Flags (Nominal)
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Risk Flags Column */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-rose-400 font-semibold">
            <AlertOctagon className="w-4 h-4" />
            Active Regulatory & Physical Risk Flags
          </div>

          {riskFlags.length === 0 ? (
            <div className="p-4 rounded-lg bg-emerald-950/20 border border-emerald-800/40 text-emerald-300 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
              <span>Site meets all baseline environmental, aquifer extraction, and grid proximity criteria without triggering primary risk flags.</span>
            </div>
          ) : (
            <div className="space-y-2">
              {riskFlags.map((flag, idx) => (
                <div 
                  key={idx}
                  className="p-3 rounded-lg bg-rose-950/30 border border-rose-500/40 text-xs flex items-start gap-2.5 text-rose-200"
                >
                  <span className="mt-0.5 w-2 h-2 rounded-full bg-rose-400 shrink-0 animate-ping"></span>
                  <div className="font-medium">
                    {flag}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Engineering Mandates Column */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-amber-400 font-semibold">
            <Wrench className="w-4 h-4" />
            Compulsory Engineering Mitigation Mandates
          </div>

          <div className="space-y-2">
            {mandates.map((mandate, idx) => (
              <div 
                key={idx}
                className="p-3 rounded-lg bg-amber-950/25 border border-amber-600/40 text-xs text-amber-200 flex items-start gap-2.5"
              >
                <span className="font-mono text-amber-400 font-bold shrink-0">{idx + 1}.</span>
                <span className="leading-relaxed">{mandate}</span>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Engineering Diagnostic Logs Console */}
      <div className="mt-4 pt-4 border-t border-slate-800">
        <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-cyan-400 mb-2">
          <Terminal className="w-3.5 h-3.5" />
          Deterministic System Diagnostics & Rule Logs
        </div>
        <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-300 space-y-1.5 max-h-48 overflow-y-auto">
          {diagnostics.map((diag, idx) => (
            <div key={idx} className="flex items-start gap-2">
              <span className="text-cyan-500 shrink-0">›</span>
              <span className="text-slate-300">{diag}</span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
