import { useEffect, useMemo, useState } from 'react';
import {
  BarChart3,
  CheckCircle2,
  GitCompare,
  Home,
  Laptop,
  Map as MapIcon,
  Plus,
  Radio,
  RefreshCw,
  Wifi,
} from 'lucide-react';
import { BackendConnection, TarangClient, detectBackend } from './api';
import { AnalyticsView } from './components/AnalyticsView';
import { CompareView } from './components/CompareView';
import { LiveSurveyView } from './components/LiveSurveyView';
import { MapExplorerView } from './components/MapExplorerView';
import { SignalBadge } from './components/SignalBadge';
import { SurveyWizardModal } from './components/SurveyWizardModal';
import {
  Floorplan,
  Observation,
  Project,
  ProjectSummary,
  SurveySession,
  WindowsCapabilities,
  WindowsLiveScan,
} from './types';

type Tab = 'overview' | 'survey' | 'map' | 'analytics' | 'compare';

export function App() {
  const [conn, setConn] = useState<BackendConnection>({
    mode: 'demo',
    baseUrl: '',
    hasWindowsCollector: false,
  });
  const client = useMemo(() => new TarangClient(conn), [conn]);

  const [tab, setTab] = useState<Tab>('overview');
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeProjectId, setActiveProjectId] = useState<string>('');
  const [floorplans, setFloorplans] = useState<Floorplan[]>([]);
  const [sessions, setSessions] = useState<SurveySession[]>([]);
  const [observations, setObservations] = useState<Observation[]>([]);
  const [summary, setSummary] = useState<ProjectSummary | null>(null);

  const [winCaps, setWinCaps] = useState<WindowsCapabilities | null>(null);
  const [winScan, setWinScan] = useState<WindowsLiveScan | null>(null);

  const [wizardOpen, setWizardOpen] = useState(false);
  const [liveConfig, setLiveConfig] = useState<{
    sessionName: string;
    mapMode: 'indoor' | 'outdoor';
    roomLabel: string;
  } | null>(null);
  const [finishedBanner, setFinishedBanner] = useState<number | null>(null);

  const refreshConnection = async () => {
    const detected = await detectBackend();
    setConn(detected);
  };

  useEffect(() => {
    refreshConnection();
  }, []);

  useEffect(() => {
    client.getProjects().then((list) => {
      setProjects(list);
      if (list.length > 0 && !activeProjectId) {
        setActiveProjectId(list[0].id);
      }
    });

    if (conn.hasWindowsCollector) {
      client.getWindowsCapabilities().then(setWinCaps);
      client.getWindowsLiveScan(false).then((res) => setWinScan(res?.interface || null));
    }
  }, [client, conn.hasWindowsCollector]);

  useEffect(() => {
    if (!activeProjectId) return;
    Promise.all([
      client.getFloorplans(activeProjectId),
      client.getSessions(activeProjectId),
      client.getProjectObservations(activeProjectId),
      client.getProjectSummary(activeProjectId),
    ]).then(([fps, sess, obs, sum]) => {
      setFloorplans(fps);
      setSessions(sess);
      setObservations(obs);
      setSummary(sum);
    });
  }, [client, activeProjectId]);

  const activeProject = projects.find((p) => p.id === activeProjectId) || null;

  const handleStartSurvey = async (cfg: {
    sessionName: string;
    mapMode: 'indoor' | 'outdoor';
    measureWhat: 'wifi' | 'cellular' | 'both';
    roomLabel: string;
  }) => {
    setWizardOpen(false);
    setFinishedBanner(null);
    if (conn.hasWindowsCollector) {
      await client
        .startWindowsCollector({
          project_id: activeProjectId || undefined,
          session_name: cfg.sessionName,
          room_label: cfg.roomLabel,
          x_norm: 0.42,
          y_norm: 0.25,
        })
        .catch(() => {});
    }
    setLiveConfig({
      sessionName: cfg.sessionName,
      mapMode: cfg.mapMode,
      roomLabel: cfg.roomLabel,
    });
    setTab('survey');
  };

  const handleFinishSurvey = (count: number) => {
    setLiveConfig(null);
    setFinishedBanner(count);
    setTab('overview');
    if (activeProjectId) {
      client.getProjectObservations(activeProjectId).then(setObservations);
      client.getSessions(activeProjectId).then(setSessions);
      client.getProjectSummary(activeProjectId).then(setSummary);
    }
  };

  const navItems: Array<{ id: Tab; label: string; Icon: typeof Home }> = [
    { id: 'overview', label: 'Overview', Icon: Home },
    { id: 'survey', label: 'Survey', Icon: Radio },
    { id: 'map', label: 'Map Explorer', Icon: MapIcon },
    { id: 'analytics', label: 'Insights', Icon: BarChart3 },
    { id: 'compare', label: 'Compare & Export', Icon: GitCompare },
  ];

  return (
    <div className="min-h-screen bg-[#F7FAFC] text-[#102A43] lg:flex">
      {/* Desktop Slim Sidebar */}
      <aside className="hidden lg:flex lg:w-64 lg:shrink-0 lg:flex-col lg:border-r lg:border-[#E2E8F0] lg:bg-white lg:p-5">
        <div className="flex items-center gap-2.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#087F8C] text-white">
            <Wifi className="h-5 w-5" />
          </div>
          <div>
            <div className="text-base font-bold tracking-tight text-[#102A43]">TARANG</div>
            <div className="text-[11px] text-[#627D98]">Mapping the Invisible</div>
          </div>
        </div>

        <nav className="mt-8 flex-1 space-y-1.5" aria-label="Primary navigation">
          {navItems.map(({ id, label, Icon }) => (
            <button
              key={id}
              type="button"
              onClick={() => setTab(id)}
              className={`flex min-h-[44px] w-full items-center gap-3 rounded-xl px-3.5 text-sm font-medium transition ${
                tab === id
                  ? 'bg-[#E6F6F7] text-[#087F8C]'
                  : 'text-[#486581] hover:bg-[#F0F4F8] hover:text-[#102A43]'
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{label}</span>
            </button>
          ))}
        </nav>

        <div className="rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] p-3 text-xs">
          <div className="font-semibold text-[#102A43]">
            {conn.hasWindowsCollector
              ? 'Laptop Collector Connected'
              : conn.mode === 'live'
              ? 'Local API Connected'
              : 'Local-First Demo Mode'}
          </div>
          <p className="mt-1 text-[11px] text-[#627D98]">
            {conn.mode === 'live'
              ? conn.baseUrl
              : 'Running standalone in browser. Launch TARANG-Laptop on port 8765 for live Wi-Fi.'}
          </p>
          <button
            type="button"
            onClick={refreshConnection}
            className="mt-2 inline-flex items-center gap-1 text-[11px] font-semibold text-[#087F8C] hover:underline"
          >
            <RefreshCw className="h-3 w-3" />
            Reconnect local collector
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 pb-20 lg:pb-8">
        {/* Top Header */}
        <header className="border-b border-[#E2E8F0] bg-white px-4 py-3 sm:px-6">
          <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <span className="text-lg font-bold text-[#102A43] lg:hidden">TARANG</span>
              <select
                aria-label="Select survey project"
                value={activeProjectId}
                onChange={(e) => setActiveProjectId(e.target.value)}
                className="min-h-[40px] max-w-[260px] truncate rounded-xl border border-[#CBD5E1] bg-white px-3 text-xs font-semibold text-[#102A43] sm:max-w-sm sm:text-sm"
              >
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2.5">
              <span
                className={`hidden items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium sm:inline-flex ${
                  conn.hasWindowsCollector
                    ? 'bg-[#E6F4EE] text-[#168A5B]'
                    : 'bg-[#F0F4F8] text-[#486581]'
                }`}
              >
                <Laptop className="h-3.5 w-3.5" />
                {conn.hasWindowsCollector ? 'Laptop Live' : 'Demo Dataset'}
              </span>
              <button
                type="button"
                onClick={() => setWizardOpen(true)}
                className="inline-flex min-h-[44px] items-center gap-2 rounded-xl bg-[#087F8C] px-4 text-sm font-semibold text-white hover:bg-[#066974]"
              >
                <Plus className="h-4 w-4" />
                Start Survey
              </button>
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-6xl p-4 sm:p-6">
          {finishedBanner !== null && (
            <div className="mb-5 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-[#B7E1CD] bg-[#E6F4EE] px-5 py-4 text-sm text-[#102A43]">
              <div className="flex items-center gap-2.5">
                <CheckCircle2 className="h-5 w-5 text-[#168A5B]" />
                <span>
                  <strong>Survey saved.</strong> {finishedBanner} marked points recorded locally.
                </span>
              </div>
              <button
                type="button"
                onClick={() => setTab('map')}
                className="min-h-[40px] rounded-xl bg-[#168A5B] px-4 text-xs font-semibold text-white"
              >
                View Coverage Map
              </button>
            </div>
          )}

          {tab === 'overview' && (
            <div className="space-y-6">
              {/* Hero Welcome Card */}
              <section className="rounded-2xl border border-[#D9E2EC] bg-white p-6 shadow-sm">
                <div className="flex flex-col justify-between gap-5 md:flex-row md:items-center">
                  <div className="max-w-xl">
                    <p className="text-xs font-semibold uppercase tracking-wider text-[#087F8C]">
                      Telecommunication Analysis, Radio Assessment &amp; Network Geomapping
                    </p>
                    <h1 className="mt-1 text-2xl font-bold tracking-tight text-[#102A43] sm:text-3xl">
                      See your network clearly.
                    </h1>
                    <p className="mt-2 text-sm text-[#486581]">
                      Walk through rooms or outdoor paths, tag real Wi-Fi and cellular measurements,
                      and spot weak coverage without guesswork.
                    </p>
                    <div className="mt-5 flex flex-wrap gap-3">
                      <button
                        type="button"
                        onClick={() => setWizardOpen(true)}
                        className="min-h-[44px] rounded-xl bg-[#087F8C] px-5 text-sm font-semibold text-white hover:bg-[#066974]"
                      >
                        Start a Survey
                      </button>
                      <button
                        type="button"
                        onClick={() => setTab('map')}
                        className="min-h-[44px] rounded-xl border border-[#CBD5E1] bg-white px-5 text-sm font-semibold text-[#102A43] hover:bg-[#F0F4F8]"
                      >
                        Explore Map ({observations.length} points)
                      </button>
                    </div>
                  </div>

                  {/* Windows Hybrid Collector Card */}
                  <div className="w-full rounded-2xl border border-[#E2E8F0] bg-[#F8FAFC] p-4 md:w-80">
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-2 text-xs font-semibold text-[#102A43]">
                        <Laptop className="h-4 w-4 text-[#087F8C]" />
                        Windows Laptop Collector
                      </span>
                      <SignalBadge
                        tier={
                          winScan?.quality_percent != null
                            ? winScan.quality_percent >= 80
                              ? 'Strong'
                              : winScan.quality_percent >= 60
                              ? 'Good'
                              : 'Fair'
                            : 'Unavailable'
                        }
                      />
                    </div>
                    {conn.hasWindowsCollector && winScan ? (
                      <div className="mt-3 space-y-1 text-xs text-[#486581]">
                        <div className="tabular-nums text-lg font-bold text-[#102A43]">
                          {winScan.quality_percent != null ? `${winScan.quality_percent}% quality` : 'Disconnected'}
                          {winScan.rssi_dbm != null ? ` (${winScan.rssi_dbm} dBm)` : ''}
                        </div>
                        <div>
                          {winScan.ssid || 'No SSID'} • {winScan.band || 'N/A'}
                        </div>
                        <div className="truncate text-[11px] text-[#627D98]">
                          {winCaps?.adapter_description}
                        </div>
                      </div>
                    ) : (
                      <p className="mt-2 text-xs text-[#627D98]">
                        Run <code className="rounded bg-[#E2E8F0] px-1">START_TARANG_LAPTOP.bat</code>{' '}
                        on Windows to stream live adapter telemetry to <code className="rounded bg-[#E2E8F0] px-1">127.0.0.1:8765</code>.
                      </p>
                    )}
                  </div>
                </div>
              </section>

              <AnalyticsView summary={summary} observations={observations} />
            </div>
          )}

          {tab === 'survey' && (
            <LiveSurveyView
              client={client}
              sessionName={liveConfig?.sessionName || 'Quick Indoor Walk'}
              mapMode={liveConfig?.mapMode || 'indoor'}
              initialRoom={liveConfig?.roomLabel || 'Living Room'}
              onFinish={handleFinishSurvey}
            />
          )}

          {tab === 'map' && (
            <MapExplorerView
              project={activeProject}
              floorplans={floorplans}
              sessions={sessions}
              observations={observations}
            />
          )}

          {tab === 'analytics' && <AnalyticsView summary={summary} observations={observations} />}

          {tab === 'compare' && (
            <CompareView
              client={client}
              project={activeProject}
              sessions={sessions}
              observations={observations}
            />
          )}
        </main>
      </div>

      {/* Mobile Bottom Navigation */}
      <nav
        className="fixed bottom-0 left-0 right-0 z-40 flex border-t border-[#E2E8F0] bg-white lg:hidden"
        aria-label="Mobile navigation"
      >
        {navItems.map(({ id, label, Icon }) => (
          <button
            key={id}
            type="button"
            onClick={() => setTab(id)}
            className={`flex min-h-[56px] flex-1 flex-col items-center justify-center gap-0.5 text-[11px] font-medium ${
              tab === id ? 'text-[#087F8C]' : 'text-[#627D98]'
            }`}
          >
            <Icon className="h-5 w-5" />
            <span>{label.split(' ')[0]}</span>
          </button>
        ))}
      </nav>

      <SurveyWizardModal
        open={wizardOpen}
        hasWindowsCollector={conn.hasWindowsCollector}
        onClose={() => setWizardOpen(false)}
        onStart={handleStartSurvey}
      />
    </div>
  );
}

export default App;
