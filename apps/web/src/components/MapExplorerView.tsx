import { useMemo, useState } from 'react';
import { Layers, List, Map as MapIcon, MapPin, ShieldAlert } from 'lucide-react';
import { Floorplan, Observation, Project, SurveySession } from '../types';
import { SignalBadge, tierColorHex } from './SignalBadge';

interface MapExplorerViewProps {
  project: Project | null;
  floorplans: Floorplan[];
  sessions: SurveySession[];
  observations: Observation[];
}

export function MapExplorerView({
  project,
  floorplans,
  sessions,
  observations,
}: MapExplorerViewProps) {
  const [kindFilter, setKindFilter] = useState<'all' | 'wifi' | 'cellular'>('all');
  const [sessionFilter, setSessionFilter] = useState<string>('all');
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [listMode, setListMode] = useState(false);
  const [selectedObs, setSelectedObs] = useState<Observation | null>(null);

  const filtered = useMemo(() => {
    return observations.filter((o) => {
      if (kindFilter !== 'all' && o.kind !== kindFilter) return false;
      if (sessionFilter !== 'all' && o.session_id !== sessionFilter) return false;
      return true;
    });
  }, [observations, kindFilter, sessionFilter]);

  const indoorObs = filtered.filter(
    (o) => o.location_kind === 'indoor' && o.x_norm != null && o.y_norm != null
  );
  const outdoorObs = filtered.filter(
    (o) => o.location_kind === 'outdoor' && o.lat != null && o.lon != null
  );

  const isOutdoor = project?.map_mode === 'outdoor' || (indoorObs.length === 0 && outdoorObs.length > 0);
  const floorplanUri = floorplans[0]?.image_uri || '/samples/demo-indoor-floorplan.svg';

  // Compute bounding box for outdoor coordinate projection on offline-safe SVG grid
  const outdoorBounds = useMemo(() => {
    if (outdoorObs.length === 0) return { minLat: 0, maxLat: 1, minLon: 0, maxLon: 1 };
    const lats = outdoorObs.map((o) => o.lat!);
    const lons = outdoorObs.map((o) => o.lon!);
    const padLat = Math.max(0.0005, (Math.max(...lats) - Math.min(...lats)) * 0.2);
    const padLon = Math.max(0.0005, (Math.max(...lons) - Math.min(...lons)) * 0.2);
    return {
      minLat: Math.min(...lats) - padLat,
      maxLat: Math.max(...lats) + padLat,
      minLon: Math.min(...lons) - padLon,
      maxLon: Math.max(...lons) + padLon,
    };
  }, [outdoorObs]);

  return (
    <div className="space-y-4">
      {/* Filter strip */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-[#D9E2EC] bg-white p-4">
        <div className="flex flex-wrap items-center gap-2">
          {(['all', 'wifi', 'cellular'] as const).map((k) => (
            <button
              key={k}
              type="button"
              onClick={() => setKindFilter(k)}
              className={`min-h-[40px] rounded-xl px-3.5 text-xs font-semibold capitalize transition ${
                kindFilter === k
                  ? 'bg-[#087F8C] text-white'
                  : 'bg-[#F0F4F8] text-[#334E68] hover:bg-[#E2E8F0]'
              }`}
            >
              {k === 'all' ? 'All Radios' : k === 'wifi' ? 'Wi-Fi' : 'Cellular (LTE/5G)'}
            </button>
          ))}

          <select
            aria-label="Filter by session"
            value={sessionFilter}
            onChange={(e) => setSessionFilter(e.target.value)}
            className="min-h-[40px] rounded-xl border border-[#CBD5E1] bg-white px-3 text-xs font-medium text-[#102A43]"
          >
            <option value="all">All Sessions ({sessions.length})</option>
            {sessions.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2">
          {!listMode && (
            <button
              type="button"
              onClick={() => setShowHeatmap((h) => !h)}
              className={`inline-flex min-h-[40px] items-center gap-1.5 rounded-xl border px-3 text-xs font-semibold ${
                showHeatmap
                  ? 'border-[#087F8C] bg-[#E6F6F7] text-[#087F8C]'
                  : 'border-[#CBD5E1] bg-white text-[#334E68]'
              }`}
            >
              <Layers className="h-4 w-4" />
              {showHeatmap ? 'Estimated Heatmap (On)' : 'Measured Points'}
            </button>
          )}
          <button
            type="button"
            onClick={() => setListMode((l) => !l)}
            className="inline-flex min-h-[40px] items-center gap-1.5 rounded-xl border border-[#CBD5E1] bg-white px-3 text-xs font-semibold text-[#102A43] hover:bg-[#F0F4F8]"
          >
            {listMode ? <MapIcon className="h-4 w-4" /> : <List className="h-4 w-4" />}
            {listMode ? 'Map View' : 'List View'}
          </button>
        </div>
      </div>

      {/* Legend (Color + Text + Units) */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-[#D9E2EC] bg-white px-4 py-2.5 text-xs">
        <div className="flex flex-wrap items-center gap-3">
          <span className="font-semibold text-[#102A43]">Legend:</span>
          <SignalBadge tier="Strong" /> <span className="text-[#627D98]">Wi-Fi ≥ -55 dBm / RSRP ≥ -85</span>
          <SignalBadge tier="Good" /> <span className="text-[#627D98]">-56 to -67 dBm</span>
          <SignalBadge tier="Fair" /> <span className="text-[#627D98]">-68 to -75 dBm</span>
          <SignalBadge tier="Weak" /> <span className="text-[#627D98]">&lt; -75 dBm</span>
        </div>
        <span className="text-[#627D98]">{filtered.length} observations shown</span>
      </div>

      {listMode ? (
        <div className="overflow-x-auto rounded-2xl border border-[#D9E2EC] bg-white shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-[#E2E8F0] bg-[#F8FAFC] text-xs font-semibold uppercase text-[#486581]">
              <tr>
                <th className="px-4 py-3">Signal</th>
                <th className="px-4 py-3">Measured Value</th>
                <th className="px-4 py-3">Location</th>
                <th className="px-4 py-3">Source</th>
                <th className="px-4 py-3">Observed</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2E8F0]">
              {filtered.map((o) => (
                <tr key={o.id} className="hover:bg-[#F7FAFC]">
                  <td className="px-4 py-3">
                    <SignalBadge tier={o.signal_tier} />
                  </td>
                  <td className="tabular-nums px-4 py-3 font-medium text-[#102A43]">
                    {o.primary_metric_label}
                  </td>
                  <td className="px-4 py-3 text-xs text-[#486581]">
                    {o.location_kind === 'indoor'
                      ? o.room_label || 'Indoor point'
                      : o.lat != null
                      ? `${o.lat.toFixed(4)}, ${o.lon?.toFixed(4)} (±${o.gps_accuracy_m?.toFixed(0) ?? '?'}m)`
                      : 'Unknown'}
                  </td>
                  <td className="px-4 py-3 text-xs text-[#627D98]">{o.metric_source}</td>
                  <td className="tabular-nums px-4 py-3 text-xs text-[#627D98]">
                    {new Date(o.observed_at).toLocaleTimeString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div className="lg:col-span-2 rounded-2xl border border-[#D9E2EC] bg-white p-4 shadow-sm">
            {!isOutdoor ? (
              <div className="relative overflow-hidden rounded-xl border border-[#CBD5E1] bg-[#F8FAFC]">
                <img src={floorplanUri} alt="Survey floor plan" className="block w-full select-none" />

                {/* Bounded local heatmap halos only around measured points */}
                {showHeatmap &&
                  indoorObs.map((o) => (
                    <div
                      key={`hm-${o.id}`}
                      style={{
                        left: `${(o.x_norm || 0) * 100}%`,
                        top: `${(o.y_norm || 0) * 100}%`,
                        background: `radial-gradient(circle, ${tierColorHex(o.signal_tier)}55 0%, transparent 70%)`,
                      }}
                      className="pointer-events-none absolute h-28 w-28 -translate-x-1/2 -translate-y-1/2 rounded-full"
                    />
                  ))}

                {indoorObs.map((o) => (
                  <button
                    key={o.id}
                    type="button"
                    onClick={() => setSelectedObs(o)}
                    aria-label={`${o.room_label || 'Point'}: ${o.signal_tier} ${o.primary_metric_label}`}
                    style={{
                      left: `${(o.x_norm || 0) * 100}%`,
                      top: `${(o.y_norm || 0) * 100}%`,
                      backgroundColor: tierColorHex(o.signal_tier),
                    }}
                    className={`absolute h-5 w-5 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white shadow transition hover:scale-125 ${
                      selectedObs?.id === o.id ? 'ring-2 ring-[#102A43]' : ''
                    }`}
                  />
                ))}
              </div>
            ) : (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs text-[#486581]">
                  <span>Outdoor GPS Coordinate Grid (Offline-Resilient Fallback)</span>
                  <span>Points with GPS &gt; 20m flagged as uncertain</span>
                </div>
                <div className="relative h-[420px] w-full overflow-hidden rounded-xl border border-[#CBD5E1] bg-[#F0F4F8]">
                  <svg className="h-full w-full" viewBox="0 0 800 420">
                    {/* Subtle coordinate grid */}
                    {[1, 2, 3, 4].map((i) => (
                      <line key={`h-${i}`} x1="0" y1={i * 84} x2="800" y2={i * 84} stroke="#D9E2EC" strokeDasharray="4 4" />
                    ))}
                    {[1, 2, 3, 4, 5, 6, 7].map((i) => (
                      <line key={`v-${i}`} x1={i * 100} y1="0" x2={i * 100} y2="420" stroke="#D9E2EC" strokeDasharray="4 4" />
                    ))}
                    {outdoorObs.map((o) => {
                      const x =
                        ((o.lon! - outdoorBounds.minLon) /
                          (outdoorBounds.maxLon - outdoorBounds.minLon)) *
                        800;
                      const y =
                        420 -
                        ((o.lat! - outdoorBounds.minLat) /
                          (outdoorBounds.maxLat - outdoorBounds.minLat)) *
                          420;
                      const uncertain = (o.gps_accuracy_m || 0) > 20;
                      return (
                        <g key={o.id} onClick={() => setSelectedObs(o)} className="cursor-pointer">
                          <circle
                            cx={x}
                            cy={y}
                            r={Math.min(34, Math.max(10, (o.gps_accuracy_m || 8) * 1.1))}
                            fill={tierColorHex(o.signal_tier)}
                            fillOpacity={0.18}
                            stroke={uncertain ? '#D99C26' : 'none'}
                            strokeDasharray="3 3"
                          />
                          <circle
                            cx={x}
                            cy={y}
                            r={8}
                            fill={tierColorHex(o.signal_tier)}
                            stroke="#FFFFFF"
                            strokeWidth="2"
                          />
                        </g>
                      );
                    })}
                  </svg>
                </div>
              </div>
            )}
          </div>

          {/* Point Inspector */}
          <div className="rounded-2xl border border-[#D9E2EC] bg-white p-5 shadow-sm">
            <h3 className="text-sm font-semibold text-[#102A43]">Point Inspector</h3>
            {selectedObs ? (
              <div className="mt-4 space-y-3 text-sm">
                <SignalBadge tier={selectedObs.signal_tier} size="lg" />
                <div className="tabular-nums text-2xl font-bold text-[#102A43]">
                  {selectedObs.primary_metric_label}
                </div>

                {selectedObs.gps_accuracy_m != null && selectedObs.gps_accuracy_m > 20 && (
                  <div className="flex items-start gap-2 rounded-xl bg-[#FCF5E6] p-3 text-xs text-[#9C6B0E]">
                    <ShieldAlert className="h-4 w-4 shrink-0" />
                    <span>
                      Low GPS confidence (±{selectedObs.gps_accuracy_m.toFixed(1)} m). Excluded from confident heatmap interpolation.
                    </span>
                  </div>
                )}

                <dl className="space-y-2 border-t border-[#E2E8F0] pt-3 text-xs">
                  <div className="flex justify-between">
                    <dt className="text-[#627D98]">Location</dt>
                    <dd className="font-medium text-[#102A43]">
                      {selectedObs.room_label ||
                        (selectedObs.lat != null
                          ? `${selectedObs.lat.toFixed(5)}, ${selectedObs.lon?.toFixed(5)}`
                          : 'Unknown')}
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-[#627D98]">Source</dt>
                    <dd className="font-medium text-[#102A43]">{selectedObs.metric_source}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-[#627D98]">Freshness</dt>
                    <dd className="tabular-nums font-medium text-[#102A43]">
                      {(selectedObs.freshness_ms / 1000).toFixed(1)}s
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-[#627D98]">Observed at</dt>
                    <dd className="tabular-nums font-medium text-[#102A43]">
                      {new Date(selectedObs.observed_at).toLocaleString()}
                    </dd>
                  </div>
                </dl>
              </div>
            ) : (
              <div className="mt-8 flex flex-col items-center text-center text-xs text-[#627D98]">
                <MapPin className="mb-2 h-8 w-8 text-[#9FB3C8]" />
                Tap any measured point on the map to inspect raw metrics, freshness, and source.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
