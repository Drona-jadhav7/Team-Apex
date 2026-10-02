import React, { useState, useEffect } from 'react';
import { 
  Zap, 
  Droplet, 
  Activity, 
  Server, 
  PlusCircle, 
  RefreshCw, 
  Cpu, 
  ShieldCheck, 
  ExternalLink,
  Layers,
  Terminal
} from 'lucide-react';

import MapView from './components/MapView';
import ScoreCard from './components/ScoreCard';
import ExplainabilityPanel from './components/ExplainabilityPanel';
import MitigationCard from './components/MitigationCard';
import SiteComparison from './components/SiteComparison';
import CustomSiteModal from './components/CustomSiteModal';

import { fetchBenchmarkSites, assessCustomSite, checkApiHealth } from './services/api';

export default function App() {
  const [sites, setSites] = useState([]);
  const [selectedSite, setSelectedSite] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [apiOnline, setApiOnline] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Load benchmark sites on mount
  const loadSites = async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const health = await checkApiHealth();
      setApiOnline(health.status === 'healthy');

      const data = await fetchBenchmarkSites();
      setSites(data);
      if (data && data.length > 0) {
        setSelectedSite(data[0]); // Default to first hub (Navi Mumbai)
      }
    } catch (err) {
      console.error('Failed to load sites:', err);
      setErrorMsg('Failed to communicate with SuperIndia.ai backend. Please ensure uvicorn is running on port 8000.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSites();
  }, []);

  // Handle custom site assessment
  const handleAssessCustomSite = async (customPayload) => {
    try {
      const assessment = await assessCustomSite(customPayload);
      // Prepend to sites list and select it
      setSites((prev) => [assessment, ...prev.filter(s => s.site_id !== assessment.site_id)]);
      setSelectedSite(assessment);
    } catch (err) {
      alert(`Assessment failed: ${err.response?.data?.detail || err.message}`);
      throw err;
    }
  };

  return (
    <div className="min-h-screen bg-[#070A0F] text-slate-100 flex flex-col font-sans">
      
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-[1500] border-b border-slate-800 bg-[#0B111A]/90 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
          
          {/* Brand */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 border border-cyan-400/40">
              <Cpu className="w-5 h-5 text-slate-950 font-bold" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold font-display tracking-tight text-white">
                  SuperIndia<span className="text-cyan-400">.ai</span>
                </h1>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800/60 uppercase font-semibold">
                  v1.0 Proto
                </span>
              </div>
              <div className="text-[11px] text-slate-400 font-mono hidden sm:block">
                National AI Infrastructure & Geospatial Decision Intelligence
              </div>
            </div>
          </div>

          {/* Quick Hub Switcher */}
          <div className="hidden lg:flex items-center gap-1.5 bg-slate-900/80 p-1 rounded-lg border border-slate-800">
            {sites.slice(0, 5).map((s) => {
              const active = selectedSite?.site_id === s.site_id;
              return (
                <button
                  key={s.site_id}
                  onClick={() => setSelectedSite(s)}
                  className={`px-2.5 py-1 rounded text-xs font-mono transition-all ${
                    active 
                      ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold' 
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {s.site_name.split(' - ')[0]}
                </button>
              );
            })}
          </div>

          {/* Actions & Status */}
          <div className="flex items-center gap-3">
            {/* Status indicator */}
            <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] font-mono">
              <span className={`w-2 h-2 rounded-full ${apiOnline ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'}`}></span>
              <span className="text-slate-300">{apiOnline ? 'CGWA/CEA Online' : 'Connecting...'}</span>
            </div>

            {/* Refresh */}
            <button
              onClick={loadSites}
              title="Refresh Telemetry"
              className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
            </button>

            {/* Simulate Button */}
            <button
              onClick={() => setIsModalOpen(true)}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono font-bold bg-cyan-500 hover:bg-cyan-400 text-slate-950 transition-colors shadow-lg shadow-cyan-500/20"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Simulate Site</span>
            </button>
          </div>

        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        
        {/* Banner Alert if error */}
        {errorMsg && (
          <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 text-rose-200 text-xs flex items-center justify-between">
            <span>{errorMsg}</span>
            <button onClick={loadSites} className="underline font-mono">Retry</button>
          </div>
        )}

        {/* Top Analytical Section: Map & Selected Site Gauge */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          
          {/* Geospatial Map View (7 cols) */}
          <div className="lg:col-span-7 h-[460px] flex flex-col">
            <MapView 
              sites={sites} 
              selectedSite={selectedSite} 
              onSelectSite={(site) => setSelectedSite(site)} 
            />
          </div>

          {/* Active Site Score Gauge & Metadata (5 cols) */}
          <div className="lg:col-span-5 flex flex-col">
            <ScoreCard site={selectedSite} />
          </div>

        </div>

        {/* Explainability Breakdown (7 Water sub-models + 4 Power metrics) */}
        {selectedSite && (
          <ExplainabilityPanel site={selectedSite} />
        )}

        {/* Mitigation & Engineering Mandates */}
        {selectedSite && (
          <MitigationCard site={selectedSite} />
        )}

        {/* Multi-Site Audit & Comparison Matrix */}
        <SiteComparison 
          sites={sites} 
          selectedSite={selectedSite} 
          onSelectSite={(site) => setSelectedSite(site)} 
        />

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-[#070A0F] py-6 text-center text-xs text-slate-500 font-mono">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div>
            <strong>SuperIndia.ai</strong> • Hack in Hills Manali 2026 (AI Systems & National Infrastructure Track)
          </div>
          <div className="text-[11px] text-slate-600">
            One model → one responsibility → domain aggregator → composite site assessment.
          </div>
        </div>
      </footer>

      {/* Greenfield Simulator Modal */}
      <CustomSiteModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onAssessCustomSite={handleAssessCustomSite}
      />

    </div>
  );
}
