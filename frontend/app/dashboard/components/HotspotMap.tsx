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
    return (
      <div className="w-full h-[400px] bg-surface-800 rounded-xl flex flex-col items-center justify-center border border-slate-700/50 p-6 text-center mt-6">
        <MapPin className="w-12 h-12 text-slate-600 mb-4" />
        <h3 className="text-white font-semibold mb-2">Google Maps Integration Ready</h3>
        <p className="text-sm text-slate-400 mb-4 max-w-sm">
          Add your Google Maps API Key to <code className="text-brand-400">.env.local</code> to see live citizen hotspots here.
        </p>
        <div className="w-full max-w-xs h-32 bg-slate-900/50 rounded-lg overflow-hidden relative">
           <div className="absolute top-1/2 left-1/4 w-12 h-12 bg-red-500/40 rounded-full blur-xl animate-pulse" />
           <div className="absolute top-1/3 left-2/3 w-16 h-16 bg-brand-500/30 rounded-full blur-xl animate-pulse" />
        </div>
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
