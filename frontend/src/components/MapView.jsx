import React, { useEffect, useRef } from 'react';
import L from 'leaflet';

export default function MapView({ sites = [], selectedSite = null, onSelectSite, onMapClick }) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersLayerRef = useRef(null);

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current) return;
    if (mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [20.5937, 78.9629], // Center of India
      zoom: 5,
      minZoom: 4,
      maxZoom: 18,
      zoomControl: false,
    });

    // Dark sleek CartoDB tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://carto.com/">CARTO</a> &copy; OpenStreetMap',
      subdomains: 'abcd',
      maxZoom: 20,
    }).addTo(map);

    // Zoom control at bottom right
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    const markersLayer = L.layerGroup().addTo(map);
    markersLayerRef.current = markersLayer;
    mapInstanceRef.current = map;

    // Optional click on map to evaluate custom location
    map.on('click', (e) => {
      if (onMapClick) {
        onMapClick({ lat: e.latlng.lat, lon: e.latlng.lng });
      }
    });

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update Markers
  useEffect(() => {
    const map = mapInstanceRef.current;
    const markersLayer = markersLayerRef.current;
    if (!map || !markersLayer) return;

    markersLayer.clearLayers();

    sites.forEach((site) => {
      const isSelected = selectedSite && selectedSite.site_id === site.site_id;
      const score = site.composite_score || 0;
      const color = site.tier_color || '#10B981';

      // Custom sleek SVG marker
      const customIcon = L.divIcon({
        className: 'custom-map-marker',
        html: `
          <div style="position: relative; display: flex; flex-direction: column; align-items: center; cursor: pointer; transform: translate(-50%, -100%);">
            <div style="
              background: #0B111A; 
              border: 2px solid ${color}; 
              color: #FFFFFF; 
              border-radius: 9999px; 
              padding: 4px 8px; 
              font-family: 'Space Grotesk', monospace; 
              font-size: 11px; 
              font-weight: 700; 
              display: flex; 
              align-items: center; 
              gap: 4px;
              box-shadow: 0 4px 14px ${color}66;
              ${isSelected ? `box-shadow: 0 0 25px ${color}; transform: scale(1.15);` : ''}
              transition: all 0.2s ease-in-out;
            ">
              <span style="width: 8px; height: 8px; border-radius: 50%; background: ${color}; display: inline-block;"></span>
              <span>${score.toFixed(1)}</span>
            </div>
            <div style="
              width: 2px; 
              height: 10px; 
              background: ${color}; 
              margin-top: -1px;
            "></div>
            <div style="
              width: 8px; 
              height: 8px; 
              background: ${color}; 
              border-radius: 50%; 
              opacity: 0.8;
              box-shadow: 0 0 10px ${color};
            "></div>
          </div>
        `,
        iconSize: [0, 0],
      });

      const marker = L.marker([site.latitude, site.longitude], { icon: customIcon });

      const popupHtml = `
        <div style="font-family: 'Inter', sans-serif; font-size: 13px; color: #F1F5F9; min-width: 200px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span style="font-size: 10px; text-transform: uppercase; color: #94A3B8; font-weight: 600;">${site.state}</span>
            <span style="background: ${color}22; color: ${color}; border: 1px solid ${color}44; border-radius: 4px; padding: 2px 6px; font-size: 10px; font-weight: 700;">
              ${site.tier_badge || 'VIABLE'}
            </span>
          </div>
          <div style="font-size: 14px; font-weight: 700; color: #FFFFFF; margin-bottom: 8px; font-family: 'Space Grotesk', sans-serif;">
            ${site.site_name}
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 8px; background: rgba(0,0,0,0.3); padding: 6px; border-radius: 6px;">
            <div>
              <div style="font-size: 10px; color: #94A3B8;">Water Score</div>
              <div style="font-size: 13px; font-weight: 700; color: #38BDF8;">${(site.water_score || 0).toFixed(1)}</div>
            </div>
            <div>
              <div style="font-size: 10px; color: #94A3B8;">Power Score</div>
              <div style="font-size: 13px; font-weight: 700; color: #FBBF24;">${(site.power_score || 0).toFixed(1)}</div>
            </div>
          </div>
          ${site.risk_flags && site.risk_flags.length > 0 ? `
            <div style="color: #FB7185; font-size: 11px; margin-bottom: 8px;">
              ⚠️ ${site.risk_flags.length} active risk flag${site.risk_flags.length > 1 ? 's' : ''}
            </div>
          ` : ''}
          <div style="font-size: 11px; color: #94A3B8; margin-top: 4px;">
            Coords: ${site.latitude.toFixed(4)}, ${site.longitude.toFixed(4)}
          </div>
        </div>
      `;

      marker.bindPopup(popupHtml);

      marker.on('click', () => {
        if (onSelectSite) {
          onSelectSite(site);
        }
      });

      markersLayer.addLayer(marker);
    });

    // Fly to selected site
    if (selectedSite && selectedSite.latitude && selectedSite.longitude) {
      map.flyTo([selectedSite.latitude, selectedSite.longitude], 10, {
        animate: true,
        duration: 1.2,
      });
    }
  }, [sites, selectedSite]);

  return (
    <div className="relative w-full h-full min-h-[420px] rounded-xl overflow-hidden border border-slate-800 shadow-2xl">
      <div ref={mapContainerRef} className="w-full h-full" />
      
      {/* Map Header Overlay */}
      <div className="absolute top-3 left-3 z-[1000] pointer-events-none">
        <div className="glass-panel px-3 py-1.5 rounded-lg flex items-center gap-2 border border-slate-700/60 shadow-lg pointer-events-auto">
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse"></span>
          <span className="text-xs font-semibold text-slate-200 tracking-wider font-display uppercase">
            National AI Grid Topology
          </span>
          <span className="text-[11px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded font-mono">
            {sites.length} Active Hubs
          </span>
        </div>
      </div>

      {/* Map Legend Overlay */}
      <div className="absolute bottom-3 left-3 z-[1000] pointer-events-auto">
        <div className="glass-panel p-2.5 rounded-lg border border-slate-800 text-[11px] flex flex-col gap-1.5 shadow-xl">
          <div className="text-[10px] uppercase font-mono text-slate-400 font-semibold tracking-wider">
            Site Classification Tiers
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]"></span>
            <span className="text-slate-300 font-medium">Viable (≥ 75.0)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#F59E0B]"></span>
            <span className="text-slate-300 font-medium">Conditional (50.0 - 74.9)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#EF4444]"></span>
            <span className="text-slate-300 font-medium">Unviable (&lt; 50.0)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
