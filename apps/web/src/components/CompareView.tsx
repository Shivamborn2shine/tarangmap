import { useEffect, useState } from 'react';
import { AlertTriangle, Download, GitCompare } from 'lucide-react';
import { TarangClient } from '../api';
import { Observation, Project, SurveySession } from '../types';

interface CompareViewProps {
  client: TarangClient;
  project: Project | null;
  sessions: SurveySession[];
  observations: Observation[];
}

export function CompareView({ client, project, sessions, observations }: CompareViewProps) {
  const [sessionA, setSessionA] = useState<string>(sessions[0]?.id || '');
  const [sessionB, setSessionB] = useState<string>(sessions[1]?.id || sessions[0]?.id || '');
  const [compareData, setCompareData] = useState<any | null>(null);
  const [redact, setRedact] = useState(true);

  useEffect(() => {
    if (sessions.length >= 1 && !sessionA) setSessionA(sessions[0].id);
    if (sessions.length >= 2 && !sessionB) setSessionB(sessions[1].id);
  }, [sessions, sessionA, sessionB]);

  useEffect(() => {
    if (!sessionA || !sessionB) return;
    client.compareSessions(sessionA, sessionB).then(setCompareData).catch(() => {});
  }, [client, sessionA, sessionB]);

  const handleDownload = (format: 'csv' | 'json') => {
    if (!project) return;
    const url = client.exportUrl(project.id, format, redact);
    if (url) {
      window.open(url, '_blank');
      return;
    }
    // Client-side export in Demo Mode
    const content =
      format === 'json'
        ? JSON.stringify(
            { schema_version: 1, project_id: project.id, redacted: redact, observations },
            null,
            2
          )
        : [
            'id,session_id,kind,technology,observed_at,signal_tier,primary_metric,room_label',
            ...observations.map(
              (o) =>
                `${o.id},${o.session_id},${o.kind},${o.technology},${o.observed_at},${o.signal_tier},"${o.primary_metric_label}","${o.room_label || ''}"`
            ),
          ].join('\n');

    const blob = new Blob([content], { type: format === 'json' ? 'application/json' : 'text/csv' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `tarang-${project.id.slice(0, 8)}.${format}`;
    a.click();
  };

  return (
    <div className="space-y-5">
      {/* Session Comparison */}
      <div className="rounded-2xl border border-[#D9E2EC] bg-white p-5 shadow-sm">
        <div className="flex items-center gap-2">
          <GitCompare className="h-5 w-5 text-[#087F8C]" />
          <h3 className="text-base font-semibold text-[#102A43]">Compare Survey Sessions</h3>
        </div>
        <p className="mt-1 text-xs text-[#627D98]">
          Select two sessions to compare compatible metrics. Hardware and band differences are flagged automatically.
        </p>

        {sessions.length < 2 ? (
          <div className="mt-4 rounded-xl bg-[#F7FAFC] p-4 text-xs text-[#486581]">
            Record at least two sessions in this project to compare them side by side.
          </div>
        ) : (
          <>
            <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
              <select
                aria-label="Session A"
                value={sessionA}
                onChange={(e) => setSessionA(e.target.value)}
                className="min-h-[44px] rounded-xl border border-[#CBD5E1] bg-white px-3 text-sm text-[#102A43]"
              >
                {sessions.map((s) => (
                  <option key={s.id} value={s.id}>
                    A: {s.name}
                  </option>
                ))}
              </select>
              <select
                aria-label="Session B"
                value={sessionB}
                onChange={(e) => setSessionB(e.target.value)}
                className="min-h-[44px] rounded-xl border border-[#CBD5E1] bg-white px-3 text-sm text-[#102A43]"
              >
                {sessions.map((s) => (
                  <option key={s.id} value={s.id}>
                    B: {s.name}
                  </option>
                ))}
              </select>
            </div>

            {compareData && (
              <div className="mt-4 space-y-4">
                {compareData.caveats?.length > 0 && (
                  <div className="space-y-1.5 rounded-xl border border-[#F2DBA8] bg-[#FCF5E6] p-3.5 text-xs text-[#8C610B]">
                    <div className="flex items-center gap-1.5 font-semibold">
                      <AlertTriangle className="h-4 w-4" />
                      Comparison Caveats
                    </div>
                    {compareData.caveats.map((c: string, idx: number) => (
                      <p key={idx}>• {c}</p>
                    ))}
                  </div>
                )}

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  {[compareData.session_a, compareData.session_b].map((s, idx) => (
                    <div key={idx} className="rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] p-4">
                      <div className="text-xs font-semibold uppercase text-[#087F8C]">
                        Session {idx === 0 ? 'A' : 'B'}
                      </div>
                      <div className="mt-1 font-semibold text-[#102A43]">{s.name}</div>
                      <div className="text-xs text-[#627D98]">{s.device || 'Unknown device'}</div>
                      <dl className="mt-3 space-y-1.5 text-xs">
                        <div className="flex justify-between">
                          <dt className="text-[#627D98]">Samples</dt>
                          <dd className="tabular-nums font-semibold">{s.stats?.count ?? 0}</dd>
                        </div>
                        <div className="flex justify-between">
                          <dt className="text-[#627D98]">Wi-Fi RSSI Median</dt>
                          <dd className="tabular-nums font-semibold">
                            {s.stats?.wifi_rssi_median_dbm != null
                              ? `${s.stats.wifi_rssi_median_dbm} dBm`
                              : 'N/A'}
                          </dd>
                        </div>
                        <div className="flex justify-between">
                          <dt className="text-[#627D98]">Bands</dt>
                          <dd className="font-semibold">
                            {s.stats?.bands?.join(', ') || 'N/A'}
                          </dd>
                        </div>
                      </dl>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Export & Privacy */}
      <div className="rounded-2xl border border-[#D9E2EC] bg-white p-5 shadow-sm">
        <h3 className="text-base font-semibold text-[#102A43]">Export Survey Data</h3>
        <p className="mt-1 text-xs text-[#627D98]">
          Download raw observations in CSV or canonical JSON (`schema_version=1`).
        </p>

        <label className="mt-4 flex cursor-pointer items-center gap-2.5 text-sm text-[#102A43]">
          <input
            type="checkbox"
            checked={redact}
            onChange={(e) => setRedact(e.target.checked)}
            className="h-4 w-4 rounded border-[#CBD5E1] text-[#087F8C]"
          />
          <span>Redact sensitive SSIDs &amp; precise outdoor GPS coordinates</span>
        </label>

        <div className="mt-4 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={() => handleDownload('csv')}
            className="inline-flex min-h-[44px] items-center gap-2 rounded-xl bg-[#087F8C] px-5 text-sm font-semibold text-white hover:bg-[#066974]"
          >
            <Download className="h-4 w-4" />
            Export CSV
          </button>
          <button
            type="button"
            onClick={() => handleDownload('json')}
            className="inline-flex min-h-[44px] items-center gap-2 rounded-xl border border-[#CBD5E1] bg-white px-5 text-sm font-semibold text-[#102A43] hover:bg-[#F0F4F8]"
          >
            <Download className="h-4 w-4" />
            Export JSON
          </button>
        </div>
      </div>
    </div>
  );
}
