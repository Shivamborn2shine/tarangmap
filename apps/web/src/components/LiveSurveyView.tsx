import { useEffect, useRef, useState } from 'react';
import {
  Activity,
  ChevronDown,
  ChevronUp,
  MapPin,
  Pause,
  Play,
  RotateCcw,
  Square,
  Wifi,
} from 'lucide-react';
import { TarangClient } from '../api';
import { SignalTier, WindowsLiveScan } from '../types';
import { SignalBadge, tierColorHex } from './SignalBadge';

interface MarkedPoint {
  id: string;
  x_norm: number;
  y_norm: number;
  room_label: string;
  tier: SignalTier;
  label: string;
  observed_at: string;
}

interface LiveSurveyViewProps {
  client: TarangClient;
  sessionName: string;
  mapMode: 'indoor' | 'outdoor';
  initialRoom: string;
  onFinish: (samplesCount: number) => void;
}

const ROOMS = ['Living Room', 'Study', 'Hallway', 'Kitchen & Dining', 'Master Bedroom', 'Balcony'];

function classifyQuality(q?: number | null, rssi?: number | null): SignalTier {
  if (rssi !== null && rssi !== undefined) {
    if (rssi >= -55) return 'Strong';
    if (rssi >= -67) return 'Good';
    if (rssi >= -75) return 'Fair';
    return 'Weak';
  }
  if (q !== null && q !== undefined) {
    if (q >= 80) return 'Strong';
    if (q >= 60) return 'Good';
    if (q >= 40) return 'Fair';
    return 'Weak';
  }
  return 'Unavailable';
}

export function LiveSurveyView({
  client,
  sessionName,
  mapMode,
  initialRoom,
  onFinish,
}: LiveSurveyViewProps) {
  const [paused, setPaused] = useState(false);
  const [elapsedSec, setElapsedSec] = useState(0);
  const [roomLabel, setRoomLabel] = useState(initialRoom);
  const [markerPos, setMarkerPos] = useState<{ x: number; y: number }>({ x: 0.42, y: 0.25 });
  const [points, setPoints] = useState<MarkedPoint[]>([]);
  const [showMoreMetrics, setShowMoreMetrics] = useState(false);
  const [liveScan, setLiveScan] = useState<WindowsLiveScan | null>(null);
  const [activeProbe, setActiveProbe] = useState<any | null>(null);
  const [freshSeconds, setFreshSeconds] = useState(1);
  const imgRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (paused) return;
    const t = setInterval(() => {
      setElapsedSec((s) => s + 1);
      setFreshSeconds((f) => f + 1);
    }, 1000);
    return () => clearInterval(t);
  }, [paused]);

  useEffect(() => {
    let active = true;
    const poll = async () => {
      if (paused) return;
      if (client.conn.hasWindowsCollector) {
        const res = await client.getWindowsLiveScan(false);
        if (active && res?.interface) {
          setLiveScan(res.interface);
          setFreshSeconds(0);
        }
      } else if (active) {
        // Simulated gentle walk reading for browser-only demo mode
        const rssi = -54 - Math.round((markerPos.x * 20 + markerPos.y * 12) % 28);
        setLiveScan({
          available: true,
          observed_at: new Date().toISOString(),
          state: 'connected',
          ssid: 'TarangHome_5G (Demo)',
          band: '5 GHz',
          channel: 36,
          frequency_mhz: 5180,
          radio_type: '802.11ax',
          rssi_dbm: rssi,
          rssi_supported: true,
          quality_percent: Math.max(25, Math.min(98, 100 + rssi)),
          rx_mbps: 390,
          tx_mbps: 325,
        });
        setFreshSeconds(0);
      }
    };
    poll();
    const interval = setInterval(poll, 4500);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [client, paused, markerPos.x, markerPos.y]);

  const currentTier = classifyQuality(liveScan?.quality_percent, liveScan?.rssi_dbm);
  const primaryText =
    liveScan?.rssi_dbm !== null && liveScan?.rssi_dbm !== undefined
      ? `${liveScan.rssi_dbm} dBm Wi-Fi RSSI`
      : liveScan?.quality_percent !== null && liveScan?.quality_percent !== undefined
      ? `${liveScan.quality_percent}% signal quality`
      : 'Waiting for radio reading';

  const recordPoint = async (x: number, y: number) => {
    setMarkerPos({ x, y });
    if (client.conn.hasWindowsCollector) {
      await client.updateWindowsMarker(roomLabel, x, y).catch(() => {});
    }
    const pt: MarkedPoint = {
      id: crypto.randomUUID(),
      x_norm: x,
      y_norm: y,
      room_label: roomLabel,
      tier: currentTier,
      label: primaryText,
      observed_at: new Date().toISOString(),
    };
    setPoints((prev) => [...prev, pt]);
  };

  const handleFloorplanClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!imgRef.current) return;
    const rect = imgRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const y = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));
    recordPoint(x, y);
  };

  const handleUndo = () => {
    setPoints((prev) => prev.slice(0, -1));
  };

  const handleFinish = async () => {
    if (client.conn.hasWindowsCollector) {
      await client.stopWindowsCollector().catch(() => {});
    }
    onFinish(points.length);
  };

  const mins = String(Math.floor(elapsedSec / 60)).padStart(2, '0');
  const secs = String(elapsedSec % 60).padStart(2, '0');

  return (
    <div className="space-y-4 pb-24 sm:pb-6">
      {/* Top status bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 rounded-2xl border border-[#D9E2EC] bg-white px-4 py-3">
        <div>
          <h2 className="text-base font-semibold text-[#102A43]">{sessionName}</h2>
          <p className="text-xs text-[#486581]">
            {mapMode === 'indoor' ? `Indoor Floor Plan • ${roomLabel}` : 'Outdoor GPS Walk'}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="tabular-nums text-sm font-semibold text-[#102A43]">
            {mins}:{secs}
          </span>
          <span
            className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ${
              paused
                ? 'bg-[#FCF5E6] text-[#B47D14]'
                : 'bg-[#E6F4EE] text-[#168A5B]'
            }`}
          >
            <span className={`h-2 w-2 rounded-full ${paused ? 'bg-[#D99C26]' : 'bg-[#168A5B]'}`} />
            {paused ? 'Paused' : 'Recording'}
          </span>
        </div>
      </div>

      {/* Hero Signal Card (Glanceable) */}
      <div className="rounded-2xl border border-[#D9E2EC] bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2.5">
              <SignalBadge tier={currentTier} size="lg" />
              <span className="text-xs text-[#627D98]">updated {freshSeconds}s ago</span>
            </div>
            <div className="tabular-nums mt-3 text-3xl font-bold tracking-tight text-[#102A43]">
              {primaryText}
            </div>
            <p className="mt-1 text-sm text-[#486581]">
              {liveScan?.ssid ? `${liveScan.ssid}` : 'Not connected'}
              {liveScan?.band ? ` • ${liveScan.band}` : ''}
              {liveScan?.channel ? ` (Ch ${liveScan.channel})` : ''}
              {liveScan?.quality_percent != null && liveScan?.rssi_dbm != null
                ? ` • ${liveScan.quality_percent}% quality`
                : ''}
            </p>
          </div>

          <div className="flex flex-col items-end gap-2">
            <span className="rounded-lg bg-[#F0F4F8] px-2.5 py-1 text-xs font-medium text-[#334E68]">
              {points.length} marked points
            </span>
            <button
              type="button"
              onClick={async () => {
                const res = await client.runActiveProbe();
                setActiveProbe(res);
              }}
              className="inline-flex min-h-[38px] items-center gap-1.5 rounded-xl border border-[#CBD5E1] px-3 text-xs font-medium text-[#102A43] hover:bg-[#F0F4F8]"
            >
              <Activity className="h-3.5 w-3.5 text-[#087F8C]" />
              Run Latency Probe
            </button>
          </div>
        </div>

        {activeProbe && (
          <div className="mt-3 rounded-xl bg-[#F7FAFC] px-3.5 py-2 text-xs text-[#334E68]">
            Active probe ({activeProbe.endpoint}):{' '}
            <strong className="tabular-nums">
              {activeProbe.latency_ms != null ? `${activeProbe.latency_ms} ms` : 'Timed out'}
            </strong>
            {activeProbe.jitter_ms != null ? ` • jitter ${activeProbe.jitter_ms} ms` : ''}
            {activeProbe.packet_loss_pct != null ? ` • ${activeProbe.packet_loss_pct}% loss` : ''}
          </div>
        )}

        <button
          type="button"
          onClick={() => setShowMoreMetrics((v) => !v)}
          className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-[#087F8C] hover:underline"
        >
          {showMoreMetrics ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          {showMoreMetrics ? 'Hide engineering details' : 'More metrics'}
        </button>

        {showMoreMetrics && (
          <div className="mt-3 grid grid-cols-2 gap-3 border-t border-[#E2E8F0] pt-3 text-xs sm:grid-cols-4">
            <div>
              <div className="text-[#627D98]">Radio Type</div>
              <div className="font-semibold text-[#102A43]">{liveScan?.radio_type || 'N/A'}</div>
            </div>
            <div>
              <div className="text-[#627D98]">Link Speed (Rx/Tx)</div>
              <div className="tabular-nums font-semibold text-[#102A43]">
                {liveScan?.rx_mbps ? `${liveScan.rx_mbps} / ${liveScan.tx_mbps} Mbps` : 'N/A'}
              </div>
            </div>
            <div>
              <div className="text-[#627D98]">Frequency</div>
              <div className="tabular-nums font-semibold text-[#102A43]">
                {liveScan?.frequency_mhz ? `${liveScan.frequency_mhz} MHz` : 'N/A'}
              </div>
            </div>
            <div>
              <div className="text-[#627D98]">Cellular Radio</div>
              <div className="font-semibold text-[#486581]">Unavailable on Laptop</div>
            </div>
          </div>
        )}
      </div>

      {/* Indoor Floor Plan Tap Marker */}
      <div className="rounded-2xl border border-[#D9E2EC] bg-white p-4 shadow-sm">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <div>
            <h3 className="text-sm font-semibold text-[#102A43]">
              Tap floor plan where you are standing
            </h3>
            <p className="text-xs text-[#627D98]">
              Update room label and tap the map when you move to keep indoor coordinates honest.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <select
              aria-label="Current room label"
              value={roomLabel}
              onChange={(e) => setRoomLabel(e.target.value)}
              className="min-h-[40px] rounded-xl border border-[#CBD5E1] bg-white px-3 text-xs font-medium text-[#102A43]"
            >
              {ROOMS.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={handleUndo}
              disabled={points.length === 0}
              className="inline-flex min-h-[40px] items-center gap-1 rounded-xl border border-[#CBD5E1] px-3 text-xs font-medium text-[#334E68] disabled:opacity-40"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              Undo
            </button>
          </div>
        </div>

        <div
          ref={imgRef}
          onClick={handleFloorplanClick}
          role="button"
          tabIndex={0}
          aria-label="Interactive apartment floor plan. Click or tap to mark your position."
          className="relative w-full cursor-crosshair overflow-hidden rounded-xl border border-[#CBD5E1] bg-[#F8FAFC]"
        >
          <img
            src="/samples/demo-indoor-floorplan.svg"
            alt="Apartment floor plan"
            className="block w-full select-none"
            draggable={false}
          />
          {points.map((pt) => (
            <div
              key={pt.id}
              title={`${pt.room_label}: ${pt.label}`}
              style={{
                left: `${pt.x_norm * 100}%`,
                top: `${pt.y_norm * 100}%`,
                backgroundColor: tierColorHex(pt.tier),
              }}
              className="absolute h-4 w-4 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white shadow"
            />
          ))}
          <div
            style={{ left: `${markerPos.x * 100}%`, top: `${markerPos.y * 100}%` }}
            className="pointer-events-none absolute -translate-x-1/2 -translate-y-1/2"
          >
            <span className="flex h-7 w-7 items-center justify-center rounded-full border-2 border-white bg-[#087F8C] text-white shadow-md">
              <MapPin className="h-4 w-4" />
            </span>
          </div>
        </div>
      </div>

      {/* Sticky Thumb-Friendly Bottom Controls */}
      <div className="fixed bottom-16 left-0 right-0 z-30 border-t border-[#D9E2EC] bg-white/95 px-4 py-3 backdrop-blur sm:static sm:rounded-2xl sm:border">
        <div className="mx-auto flex max-w-3xl items-center justify-between gap-2">
          <button
            type="button"
            onClick={() => recordPoint(markerPos.x, markerPos.y)}
            className="flex min-h-[48px] flex-1 items-center justify-center gap-2 rounded-xl bg-[#EAF2FC] px-4 text-sm font-semibold text-[#102A43] hover:bg-[#D6E6FA]"
          >
            <Wifi className="h-4 w-4 text-[#3978CF]" />
            Mark Here
          </button>
          <button
            type="button"
            onClick={() => setPaused((p) => !p)}
            className="flex min-h-[48px] items-center justify-center gap-2 rounded-xl border border-[#CBD5E1] bg-white px-4 text-sm font-semibold text-[#102A43] hover:bg-[#F0F4F8]"
          >
            {paused ? <Play className="h-4 w-4 text-[#168A5B]" /> : <Pause className="h-4 w-4 text-[#D99C26]" />}
            {paused ? 'Resume' : 'Pause'}
          </button>
          <button
            type="button"
            onClick={handleFinish}
            className="flex min-h-[48px] flex-1 items-center justify-center gap-2 rounded-xl bg-[#087F8C] px-5 text-sm font-semibold text-white hover:bg-[#066974]"
          >
            <Square className="h-4 w-4 fill-current" />
            Finish
          </button>
        </div>
      </div>
    </div>
  );
}
