import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { AlertTriangle, Lightbulb, ShieldCheck } from 'lucide-react';
import { Observation, ProjectSummary } from '../types';
import { SignalBadge, tierColorHex } from './SignalBadge';

interface AnalyticsViewProps {
  summary: ProjectSummary | null;
  observations: Observation[];
}

export function AnalyticsView({ summary, observations }: AnalyticsViewProps) {
  if (!summary) {
    return (
      <div className="rounded-2xl border border-[#D9E2EC] bg-white p-8 text-center text-sm text-[#627D98]">
        Loading project analytics…
      </div>
    );
  }

  const tierData = (['Strong', 'Good', 'Fair', 'Weak'] as const).map((tier) => ({
    tier,
    wifi: summary.wifi_tier_distribution[tier] || 0,
    cellular: summary.cellular_tier_distribution[tier] || 0,
  }));

  const wifiSeries = observations
    .filter((o) => o.kind === 'wifi' && o.wifi?.rssi_dbm != null)
    .slice(0, 20)
    .map((o, i) => ({
      idx: i + 1,
      room: o.room_label || `Pt ${i + 1}`,
      rssi: o.wifi!.rssi_dbm!,
    }));

  return (
    <div className="space-y-5">
      {/* KPI strip */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-2xl border border-[#D9E2EC] bg-white p-5 shadow-sm">
          <div className="text-xs font-medium text-[#627D98]">Potential Weak Spots</div>
          <div className="tabular-nums mt-1 text-3xl font-bold text-[#102A43]">
            {summary.weak_spots.length}
          </div>
          <p className="mt-1 text-xs text-[#486581]">
            Across {summary.measured_areas_count} measured areas
          </p>
        </div>

        <div className="rounded-2xl border border-[#D9E2EC] bg-white p-5 shadow-sm">
          <div className="text-xs font-medium text-[#627D98]">Typical Wi-Fi RSSI</div>
          <div className="tabular-nums mt-1 text-3xl font-bold text-[#102A43]">
            {summary.typical_wifi_rssi_dbm != null ? `${summary.typical_wifi_rssi_dbm} dBm` : 'N/A'}
          </div>
          <p className="mt-1 text-xs text-[#486581]">
            {summary.typical_wifi_quality_pct != null
              ? `Windows quality median: ${summary.typical_wifi_quality_pct}%`
              : 'Median across observed Wi-Fi points'}
          </p>
        </div>

        <div className="rounded-2xl border border-[#D9E2EC] bg-white p-5 shadow-sm">
          <div className="text-xs font-medium text-[#627D98]">Typical Cellular (5G / LTE)</div>
          <div className="tabular-nums mt-1 text-3xl font-bold text-[#102A43]">
            {summary.typical_nr_ss_rsrp_dbm != null
              ? `${summary.typical_nr_ss_rsrp_dbm} dBm`
              : summary.typical_lte_rsrp_dbm != null
              ? `${summary.typical_lte_rsrp_dbm} dBm`
              : 'Unavailable'}
          </div>
          <p className="mt-1 text-xs text-[#486581]">
            {summary.typical_nr_ss_rsrp_dbm != null ? '5G NR SS-RSRP median' : 'LTE RSRP median'}
          </p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border border-[#D9E2EC] bg-white p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-[#102A43]">Signal Quality Distribution</h3>
          <p className="text-xs text-[#627D98]">Count of observations by radio-specific tier</p>
          <div className="mt-4 h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={tierData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                <XAxis dataKey="tier" tick={{ fontSize: 12, fill: '#486581' }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: '#486581' }} />
                <Tooltip />
                <Bar dataKey="wifi" name="Wi-Fi" radius={[6, 6, 0, 0]}>
                  {tierData.map((d) => (
                    <Cell key={d.tier} fill={tierColorHex(d.tier)} />
                  ))}
                </Bar>
                <Bar dataKey="cellular" name="Cellular" fill="#3978CF" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-2xl border border-[#D9E2EC] bg-white p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-[#102A43]">Wi-Fi RSSI by Room / Sequence</h3>
          <p className="text-xs text-[#627D98]">Closer to 0 dBm indicates stronger received signal</p>
          <div className="mt-4 h-56">
            {wifiSeries.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={wifiSeries}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                  <XAxis dataKey="room" tick={{ fontSize: 10, fill: '#486581' }} />
                  <YAxis domain={[-100, -30]} tick={{ fontSize: 12, fill: '#486581' }} />
                  <Tooltip />
                  <Bar dataKey="rssi" name="RSSI (dBm)" fill="#087F8C" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-xs text-[#627D98]">
                No Wi-Fi RSSI dBm samples in this project yet.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Weak Spots */}
      {summary.weak_spots.length > 0 && (
        <div className="rounded-2xl border border-[#D9E2EC] bg-white p-5 shadow-sm">
          <h3 className="flex items-center gap-2 text-sm font-semibold text-[#102A43]">
            <AlertTriangle className="h-4 w-4 text-[#D99C26]" />
            Flagged Areas
          </h3>
          <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
            {summary.weak_spots.map((w) => (
              <div
                key={w.area}
                className="flex items-center justify-between rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] p-3.5"
              >
                <div>
                  <div className="font-semibold text-[#102A43]">{w.area}</div>
                  <div className="text-xs text-[#627D98]">
                    {w.sample_count} samples • Confidence: {w.confidence}
                  </div>
                </div>
                <div className="text-right">
                  <SignalBadge tier={w.tier as any} />
                  <div className="tabular-nums mt-1 text-xs font-semibold text-[#102A43]">
                    {w.median_value} {w.unit}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Rules-Based Recommendations */}
      <div className="space-y-3">
        <h3 className="flex items-center gap-2 text-sm font-semibold text-[#102A43]">
          <Lightbulb className="h-4 w-4 text-[#087F8C]" />
          Grounded Optimization Insights
        </h3>
        {summary.recommendations.map((rec, i) => (
          <div key={i} className="rounded-2xl border border-[#D9E2EC] bg-white p-5 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="text-sm font-semibold text-[#102A43]">{rec.title}</span>
              <span className="inline-flex items-center gap-1 rounded-full bg-[#F0F4F8] px-2.5 py-0.5 text-xs font-medium text-[#334E68]">
                <ShieldCheck className="h-3.5 w-3.5 text-[#087F8C]" />
                {rec.rule} • {rec.confidence}
              </span>
            </div>
            <p className="mt-2 text-sm text-[#334E68]">{rec.finding}</p>
            <p className="mt-1 text-xs text-[#627D98]">
              <strong>Evidence:</strong> {rec.evidence}
            </p>
            <div className="mt-3 rounded-xl bg-[#E6F6F7]/60 px-3.5 py-2.5 text-xs text-[#102A43]">
              <strong>Suggested next test:</strong> {rec.suggested_test}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
