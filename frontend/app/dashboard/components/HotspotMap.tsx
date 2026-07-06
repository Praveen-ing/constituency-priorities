"use client";

import { useEffect, useRef, useState } from "react";
import { Loader } from "@googlemaps/js-api-loader";
import { MapPin } from "lucide-react";
import type { Priority } from "../page";

interface SubmissionLocation {
  lat: number;
  lng: number;
}

interface Props {
  priority: Priority | null;
}

const DARK_MAP_STYLE = [
  { elementType: "geometry", stylers: [{ color: "#242f3e" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#242f3e" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#746855" }] },
  {
    featureType: "administrative.locality",
    elementType: "labels.text.fill",
    stylers: [{ color: "#d59563" }],
  },
  {
    featureType: "poi",
    elementType: "labels.text.fill",
    stylers: [{ color: "#d59563" }],
  },
  {
    featureType: "poi.park",
    elementType: "geometry",
    stylers: [{ color: "#263c3f" }],
  },
  {
    featureType: "road",
    elementType: "geometry",
    stylers: [{ color: "#38414e" }],
  },
  {
    featureType: "water",
    elementType: "geometry",
    stylers: [{ color: "#17263c" }],
  },
];

export default function HotspotMap({ priority }: Props) {
  const mapRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<google.maps.Map | null>(null);
  const [heatmapLayer, setHeatmapLayer] = useState<google.maps.visualization.HeatmapLayer | null>(null);
  const [error, setError] = useState<string | null>(null);

  const apiKey = process.env.NEXT_PUBLIC_MAPS_API_KEY;

  // Initialize Map
  useEffect(() => {
    if (!apiKey || apiKey === "your_google_maps_api_key") {
      setError("Mock Mode");
      return;
    }

    const loader = new Loader({
      apiKey,
      version: "weekly",
      libraries: ["visualization"],
    });

    loader.load().then((google) => {
      if (mapRef.current) {
        const m = new google.maps.Map(mapRef.current, {
          center: { lat: 17.3850, lng: 78.4867 }, // Hyderabad default
          zoom: 12,
          styles: DARK_MAP_STYLE,
          disableDefaultUI: true,
          zoomControl: true,
        });

        // @ts-expect-error: @types/google.maps visualization types are sometimes incomplete
        const hl = new google.maps.visualization.HeatmapLayer({
          data: [],
          map: m,
          radius: 40,
          opacity: 0.8,
          gradient: [
            "rgba(0, 255, 255, 0)",
            "rgba(0, 255, 255, 1)",
            "rgba(0, 191, 255, 1)",
            "rgba(0, 127, 255, 1)",
            "rgba(0, 63, 255, 1)",
            "rgba(0, 0, 255, 1)",
            "rgba(0, 0, 223, 1)",
            "rgba(0, 0, 191, 1)",
            "rgba(0, 0, 159, 1)",
            "rgba(0, 0, 127, 1)",
            "rgba(63, 0, 91, 1)",
            "rgba(127, 0, 63, 1)",
            "rgba(191, 0, 31, 1)",
            "rgba(255, 0, 0, 1)"
          ],
        });

        setMap(m);
        setHeatmapLayer(hl);
      }
    }).catch(e => {
      console.error("Maps load error", e);
      setError("Failed to load map");
    });
  }, [apiKey]);

  // Update Data when Priority changes
  useEffect(() => {
    if (!priority) return;

    const fetchMocks = async () => {
      try {
        const res = await fetch("/mock_submissions.json");
        if (res.ok) {
          const all: any[] = await res.json();
          const filtered = all.filter(
            (s) => s.theme === priority.theme_id && s.ward_id === priority.ward_id
          );
          
          if (map && heatmapLayer && window.google) {
            const heatmapData = filtered.map(s => new google.maps.LatLng(s.lat, s.lng));
            // @ts-expect-error: setData is missing in some versions of @types/google.maps
            heatmapLayer.setData(heatmapData);
            
            // Re-center map if there are points
            if (heatmapData.length > 0) {
              const bounds = new google.maps.LatLngBounds();
              heatmapData.forEach(p => bounds.extend(p));
              map.fitBounds(bounds);
              // Prevent zooming in too close
              const listener = google.maps.event.addListener(map, "idle", () => { 
                if (map.getZoom()! > 15) map.setZoom(15); 
                google.maps.event.removeListener(listener); 
              });
            }
          }
        }
      } catch (err) {
        console.error("Failed to load map data", err);
      }
    };

    fetchMocks();
  }, [priority, map, heatmapLayer]);

  if (error === "Mock Mode") {
    // Ward positions for the SVG mock — each corresponds to a real ward in the DB
    const wardPositions: Record<string, { x: number; y: number; label: string }> = {
      rajapuram:   { x: 80,  y: 90,  label: "Rajapuram" },
      old_city:    { x: 180, y: 150, label: "Old City" },
      green_valley:{ x: 280, y: 80,  label: "Green Valley" },
      riverside:   { x: 310, y: 170, label: "Riverside" },
      new_market:  { x: 150, y: 220, label: "New Market" },
      gachibowli:  { x: 260, y: 230, label: "Gachibowli" },
    };
    const activeWard = priority ? wardPositions[priority.ward_id] : null;
    const urgencyColor = priority && priority.gap_score > 0.7 ? "#ef4444" : priority && priority.gap_score > 0.5 ? "#f97316" : "#34d399";

    return (
      <div className="w-full rounded-xl overflow-hidden relative mt-6 border border-slate-700 bg-[#0d1829]">
        <div className="absolute top-3 left-3 bg-surface-900/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700/50 z-10">
          <div className="text-xs font-semibold text-brand-400 uppercase tracking-wider mb-0.5">Hotspot Map</div>
          <div className="text-white font-medium text-sm">{priority?.theme_label || "Select a priority"}</div>
        </div>
        <div className="absolute top-3 right-3 text-xs text-slate-500 bg-surface-900/80 px-2 py-1 rounded z-10">
          Connect Google Maps API for live heatmap
        </div>
        <svg viewBox="0 0 400 300" className="w-full h-[320px]" xmlns="http://www.w3.org/2000/svg">
          {/* Grid background */}
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e3a5f" strokeWidth="0.5" />
            </pattern>
            <radialGradient id="hotspot" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor={urgencyColor} stopOpacity="0.5" />
              <stop offset="100%" stopColor={urgencyColor} stopOpacity="0" />
            </radialGradient>
          </defs>
          <rect width="400" height="300" fill="url(#grid)" />
          {/* Road lines */}
          <line x1="0" y1="150" x2="400" y2="150" stroke="#1e4080" strokeWidth="2" />
          <line x1="200" y1="0" x2="200" y2="300" stroke="#1e4080" strokeWidth="2" />
          <line x1="0" y1="75" x2="400" y2="200" stroke="#1a3060" strokeWidth="1.5" />
          <line x1="100" y1="0" x2="350" y2="300" stroke="#1a3060" strokeWidth="1.5" />
          {/* All ward dots */}
          {Object.entries(wardPositions).map(([id, pos]) => (
            <g key={id}>
              <circle cx={pos.x} cy={pos.y} r="5" fill="#1e3a5f" stroke="#2d5a9e" strokeWidth="1.5" />
              <text x={pos.x + 8} y={pos.y + 4} fontSize="8" fill="#4a6fa5" fontFamily="sans-serif">{pos.label}</text>
            </g>
          ))}
          {/* Active ward highlight */}
          {activeWard && (
            <g>
              <circle cx={activeWard.x} cy={activeWard.y} r="50" fill="url(#hotspot)" />
              <circle cx={activeWard.x} cy={activeWard.y} r="25" fill={urgencyColor} fillOpacity="0.15" />
              <circle cx={activeWard.x} cy={activeWard.y} r="8" fill={urgencyColor} fillOpacity="0.9" />
              <circle cx={activeWard.x} cy={activeWard.y} r="8" fill={urgencyColor}>
                <animate attributeName="r" values="8;18;8" dur="2s" repeatCount="indefinite" />
                <animate attributeName="fill-opacity" values="0.9;0;0.9" dur="2s" repeatCount="indefinite" />
              </circle>
              <text x={activeWard.x} y={activeWard.y - 15} textAnchor="middle" fontSize="9" fill="white" fontWeight="bold" fontFamily="sans-serif">
                {activeWard.label}
              </text>
            </g>
          )}
        </svg>
      </div>
    );
  }

  return (
    <div className="w-full h-[400px] rounded-xl overflow-hidden relative mt-6 border border-slate-700">
      <div ref={mapRef} className="w-full h-full" />
      {/* Overlay to show what is being mapped */}
      {priority && (
        <div className="absolute top-4 left-4 bg-surface-900/90 backdrop-blur-md px-4 py-2 rounded-lg border border-slate-700/50 shadow-xl">
          <div className="text-xs font-semibold text-brand-400 uppercase tracking-wider mb-0.5">Heatmap Layer</div>
          <div className="text-white font-medium text-sm">{priority.theme_label} Hotspots</div>
        </div>
      )}
    </div>
  );
}
