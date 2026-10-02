import React, { useState } from 'react';
import { X, Play, Sliders, Droplet, Zap, MapPin } from 'lucide-react';

export default function CustomSiteModal({ isOpen, onClose, onAssessCustomSite }) {
  if (!isOpen) return null;

  const [formData, setFormData] = useState({
    site_name: 'Custom Greenfield Data Center',
    state: 'Maharashtra',
    district: 'Pune / Chakan',
    latitude: 18.7520,
    longitude: 73.8560,
    elevation_m: 640.0,
    proposed_it_load_mw: 50.0,
    water_params: {
      groundwater_extraction_pct: 75.0,
      water_quality_tds: 480.0,
      demand_stress_score: 55.0,
      data_center_demand_mld: 1.5,
      local_aquifer_stress_pct: 65.0,
      industrial_density_index: 60.0,
      stp_distance_km: 4.5,
      tertiary_supply_mld: 20.0,
      assured_supply_mld: 2.5,
      on_site_storage_hours: 48.0,
      elevation_m: 640.0,
      drought_risk_index: 30.0,
      flood_zone_risk: 15.0,
    },
    power_params: {
      substation_distance_km: 2.5,
      voltage_class_kv: 220.0,
      spare_mva_margin: 70.0,
      proposed_it_load_mw: 50.0,
      renewable_open_access_score: 75.0,
    },
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onAssessCustomSite(formData);
      onClose();
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[2000] flex items-center justify-center bg-black/75 backdrop-blur-md p-4 overflow-y-auto">
      <div className="glass-panel-elevated w-full max-w-3xl rounded-2xl border border-slate-700/80 p-6 my-8 shadow-2xl relative">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Sliders className="w-5 h-5 text-cyan-400" />
            <h3 className="text-lg font-bold font-display text-white">
              Greenfield AI Compute Site Simulator
            </h3>
          </div>
          <button 
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="space-y-6 mt-4">
          
          {/* General Parameters */}
          <div className="space-y-3">
            <div className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-cyan-400" />
              General Geographic Telemetry
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="text-[11px] text-slate-400">Site Name</label>
                <input 
                  type="text" 
                  value={formData.site_name}
                  onChange={(e) => setFormData({...formData, site_name: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:border-cyan-500 outline-none"
                  required
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400">State</label>
                <input 
                  type="text" 
                  value={formData.state}
                  onChange={(e) => setFormData({...formData, state: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:border-cyan-500 outline-none"
                  required
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400">District / Region</label>
                <input 
                  type="text" 
                  value={formData.district}
                  onChange={(e) => setFormData({...formData, district: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:border-cyan-500 outline-none"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div>
                <label className="text-[11px] text-slate-400">Latitude</label>
                <input 
                  type="number" step="0.0001"
                  value={formData.latitude}
                  onChange={(e) => setFormData({...formData, latitude: parseFloat(e.target.value)})}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:border-cyan-500 outline-none font-mono"
                  required
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400">Longitude</label>
                <input 
                  type="number" step="0.0001"
                  value={formData.longitude}
                  onChange={(e) => setFormData({...formData, longitude: parseFloat(e.target.value)})}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:border-cyan-500 outline-none font-mono"
                  required
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400">Ground Elevation (m)</label>
                <input 
                  type="number" step="0.1"
                  value={formData.elevation_m}
                  onChange={(e) => {
                    const elev = parseFloat(e.target.value);
                    setFormData({
                      ...formData, 
                      elevation_m: elev,
                      water_params: {...formData.water_params, elevation_m: elev}
                    });
                  }}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:border-cyan-500 outline-none font-mono"
                  required
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400">Target IT Load (MW)</label>
                <input 
                  type="number" step="1"
                  value={formData.proposed_it_load_mw}
                  onChange={(e) => {
                    const mw = parseFloat(e.target.value);
                    setFormData({
                      ...formData, 
                      proposed_it_load_mw: mw,
                      power_params: {...formData.power_params, proposed_it_load_mw: mw}
                    });
                  }}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:border-cyan-500 outline-none font-mono"
                  required
                />
              </div>
            </div>
          </div>

          {/* Water Engine Inputs */}
          <div className="space-y-3 pt-3 border-t border-slate-800">
            <div className="text-xs font-mono uppercase tracking-wider text-sky-400 font-semibold flex items-center gap-1.5">
              <Droplet className="w-3.5 h-3.5" />
              7-Model CGWA Water Parameters
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div>
                <label className="text-[11px] text-slate-400">CGWA GW Extraction %</label>
                <input 
                  type="number" step="1"
                  value={formData.water_params.groundwater_extraction_pct}
                  onChange={(e) => setFormData({
                    ...formData,
                    water_params: {...formData.water_params, groundwater_extraction_pct: parseFloat(e.target.value)}
                  })}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:border-sky-500 outline-none font-mono"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400">Water Quality TDS (mg/L)</label>
                <input 
                  type="number" step="10"
                  value={formData.water_params.water_quality_tds}
                  onChange={(e) => setFormData({
                    ...formData,
                    water_params: {...formData.water_params, water_quality_tds: parseFloat(e.target.value)}
                  })}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:border-sky-500 outline-none font-mono"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400">Demand Stress Score (0-100)</label>
                <input 
                  type="number" step="1"
                  value={formData.water_params.demand_stress_score}
                  onChange={(e) => setFormData({
                    ...formData,
                    water_params: {...formData.water_params, demand_stress_score: parseFloat(e.target.value)}
                  })}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:border-sky-500 outline-none font-mono"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400">STP Distance (km)</label>
                <input 
                  type="number" step="0.1"
                  value={formData.water_params.stp_distance_km}
                  onChange={(e) => setFormData({
                    ...formData,
                    water_params: {...formData.water_params, stp_distance_km: parseFloat(e.target.value)}
                  })}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:border-sky-500 outline-none font-mono"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div>
                <label className="text-[11px] text-slate-400">Assured Supply (MLD)</label>
                <input 
                  type="number" step="0.1"
                  value={formData.water_params.assured_supply_mld}
                  onChange={(e) => setFormData({
                    ...formData,
                    water_params: {...formData.water_params, assured_supply_mld: parseFloat(e.target.value)}
                  })}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:border-sky-500 outline-none font-mono"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400">On-site Storage (Hours)</label>
                <input 
                  type="number" step="1"
                  value={formData.water_params.on_site_storage_hours}
                  onChange={(e) => setFormData({
                    ...formData,
                    water_params: {...formData.water_params, on_site_storage_hours: parseFloat(e.target.value)}
                  })}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:border-sky-500 outline-none font-mono"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400">Tertiary Recycled MLD</label>
                <input 
                  type="number" step="0.5"
                  value={formData.water_params.tertiary_supply_mld}
                  onChange={(e) => setFormData({
                    ...formData,
                    water_params: {...formData.water_params, tertiary_supply_mld: parseFloat(e.target.value)}
                  })}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:border-sky-500 outline-none font-mono"
                />
              </div>
            </div>
          </div>

          {/* Power Module Inputs */}
          <div className="space-y-3 pt-3 border-t border-slate-800">
            <div className="text-xs font-mono uppercase tracking-wider text-amber-400 font-semibold flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5" />
              4-Metric CEA Electrical Grid Parameters
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div>
                <label className="text-[11px] text-slate-400">Substation Distance (km)</label>
                <input 
                  type="number" step="0.1"
                  value={formData.power_params.substation_distance_km}
                  onChange={(e) => setFormData({
                    ...formData,
                    power_params: {...formData.power_params, substation_distance_km: parseFloat(e.target.value)}
                  })}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:border-amber-500 outline-none font-mono"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400">Voltage Class (kV)</label>
                <select 
                  value={formData.power_params.voltage_class_kv}
                  onChange={(e) => setFormData({
                    ...formData,
                    power_params: {...formData.power_params, voltage_class_kv: parseFloat(e.target.value)}
                  })}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:border-amber-500 outline-none font-mono"
                >
                  <option value={400.0}>400 kV (EHV Bulk)</option>
                  <option value={220.0}>220 kV (Hyperscale)</option>
                  <option value={132.0}>132 kV (Standard)</option>
                  <option value={66.0}>66 kV (Medium)</option>
                  <option value={33.0}>33 kV (Light)</option>
                  <option value={11.0}>11 kV (Distribution)</option>
                </select>
              </div>
              <div>
                <label className="text-[11px] text-slate-400">Spare MVA Margin</label>
                <input 
                  type="number" step="5"
                  value={formData.power_params.spare_mva_margin}
                  onChange={(e) => setFormData({
                    ...formData,
                    power_params: {...formData.power_params, spare_mva_margin: parseFloat(e.target.value)}
                  })}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:border-amber-500 outline-none font-mono"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400">Renewable Open Access (0-100)</label>
                <input 
                  type="number" step="1"
                  value={formData.power_params.renewable_open_access_score}
                  onChange={(e) => setFormData({
                    ...formData,
                    power_params: {...formData.power_params, renewable_open_access_score: parseFloat(e.target.value)}
                  })}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:border-amber-500 outline-none font-mono"
                />
              </div>
            </div>
          </div>

          {/* Action buttons */}
          <div className="pt-4 border-t border-slate-800 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-xs font-mono text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex items-center gap-2 px-5 py-2 rounded-lg text-xs font-mono font-bold text-slate-950 bg-cyan-400 hover:bg-cyan-300 transition-colors shadow-lg shadow-cyan-500/20"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              {isSubmitting ? 'Evaluating...' : 'Run Deterministic Assessment'}
            </button>
          </div>

        </form>
      </div>
    </div>
  );
}
