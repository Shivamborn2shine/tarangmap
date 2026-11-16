import {
  DEMO_FLOORPLANS,
  DEMO_OBSERVATIONS,
  DEMO_PROJECTS,
  DEMO_SESSIONS,
  DEMO_SUMMARY_INDOOR,
} from './demoData';
import {
  Floorplan,
  Observation,
  Project,
  ProjectSummary,
  SurveySession,
  WindowsCapabilities,
  WindowsLiveScan,
} from './types';

export interface BackendConnection {
  mode: 'live' | 'demo';
  baseUrl: string;
  hasWindowsCollector: boolean;
}

const DEFAULT_LOCAL_COLLECTOR = 'http://127.0.0.1:8765';

export async function detectBackend(): Promise<BackendConnection> {
  const params = new URLSearchParams(window.location.search);
  const queryApi = params.get('api');
  if (queryApi) {
    localStorage.setItem('tarang_api_url', queryApi);
  }

  const candidates = [
    queryApi,
    localStorage.getItem('tarang_api_url'),
    window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost'
      ? window.location.origin
      : null,
    DEFAULT_LOCAL_COLLECTOR,
  ].filter(Boolean) as string[];

  for (const url of candidates) {
    try {
      const ctrl = new AbortController();
      const timer = setTimeout(() => ctrl.abort(), 1200);
      const res = await fetch(`${url.replace(/\/$/, '')}/health`, { signal: ctrl.signal });
      clearTimeout(timer);
      if (res.ok) {
        let hasWin = false;
        try {
          const wRes = await fetch(`${url.replace(/\/$/, '')}/api/v1/windows/capabilities`);
          hasWin = wRes.ok;
        } catch {
          hasWin = false;
        }
        return { mode: 'live', baseUrl: url.replace(/\/$/, ''), hasWindowsCollector: hasWin };
      }
    } catch {
      // try next candidate
    }
  }

  return { mode: 'demo', baseUrl: '', hasWindowsCollector: false };
}

export class TarangClient {
  constructor(public conn: BackendConnection) {}

  async getProjects(): Promise<Project[]> {
    if (this.conn.mode === 'demo') return DEMO_PROJECTS;
    const r = await fetch(`${this.conn.baseUrl}/api/v1/projects`);
    return r.json();
  }

  async createProject(name: string, mapMode: 'indoor' | 'outdoor' | 'hybrid', description?: string): Promise<Project> {
    if (this.conn.mode === 'demo') {
      const p: Project = {
        id: crypto.randomUUID(),
        name,
        description,
        map_mode: mapMode,
        created_at: new Date().toISOString(),
        session_count: 0,
        observation_count: 0,
      };
      DEMO_PROJECTS.unshift(p);
      return p;
    }
    const r = await fetch(`${this.conn.baseUrl}/api/v1/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, map_mode: mapMode, description }),
    });
    return r.json();
  }

  async getFloorplans(projectId: string): Promise<Floorplan[]> {
    if (this.conn.mode === 'demo') return DEMO_FLOORPLANS[projectId] || [];
    const r = await fetch(`${this.conn.baseUrl}/api/v1/projects/${projectId}/floorplans`);
    return r.json();
  }

  async getSessions(projectId?: string): Promise<SurveySession[]> {
    if (this.conn.mode === 'demo') {
      return projectId ? DEMO_SESSIONS.filter((s) => s.project_id === projectId) : DEMO_SESSIONS;
    }
    const q = projectId ? `?project_id=${encodeURIComponent(projectId)}` : '';
    const r = await fetch(`${this.conn.baseUrl}/api/v1/sessions${q}`);
    return r.json();
  }

  async getProjectObservations(projectId: string): Promise<Observation[]> {
    if (this.conn.mode === 'demo') {
      const sIds = new Set(DEMO_SESSIONS.filter((s) => s.project_id === projectId).map((s) => s.id));
      return DEMO_OBSERVATIONS.filter((o) => sIds.has(o.session_id));
    }
    const r = await fetch(`${this.conn.baseUrl}/api/v1/projects/${projectId}/observations`);
    return r.json();
  }

  async getProjectSummary(projectId: string): Promise<ProjectSummary> {
    if (this.conn.mode === 'demo') {
      if (projectId === DEMO_SUMMARY_INDOOR.project_id) return DEMO_SUMMARY_INDOOR;
      const obs = await this.getProjectObservations(projectId);
      return {
        ...DEMO_SUMMARY_INDOOR,
        project_id: projectId,
        project_name: DEMO_PROJECTS.find((p) => p.id === projectId)?.name || 'Survey Project',
        total_observations: obs.length,
        weak_spots: [],
      };
    }
    const r = await fetch(`${this.conn.baseUrl}/api/v1/projects/${projectId}/summary`);
    return r.json();
  }

  async getWindowsCapabilities(): Promise<WindowsCapabilities | null> {
    if (!this.conn.hasWindowsCollector) return null;
    const r = await fetch(`${this.conn.baseUrl}/api/v1/windows/capabilities`);
    return r.ok ? r.json() : null;
  }

  async getWindowsLiveScan(includeNearby = false): Promise<{ interface: WindowsLiveScan; nearby_networks: any[] } | null> {
    if (!this.conn.hasWindowsCollector) return null;
    const r = await fetch(`${this.conn.baseUrl}/api/v1/windows/live-scan?include_nearby=${includeNearby}`, {
      cache: 'no-store',
    });
    return r.ok ? r.json() : null;
  }

  async getCollectorStatus(): Promise<any | null> {
    if (!this.conn.hasWindowsCollector) return null;
    const r = await fetch(`${this.conn.baseUrl}/api/v1/windows/collector/status`);
    return r.ok ? r.json() : null;
  }

  async startWindowsCollector(payload: {
    project_id?: string;
    session_name: string;
    room_label: string;
    x_norm: number;
    y_norm: number;
  }): Promise<any> {
    const r = await fetch(`${this.conn.baseUrl}/api/v1/windows/collector/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return r.json();
  }

  async updateWindowsMarker(room_label: string, x_norm: number, y_norm: number): Promise<any> {
    const r = await fetch(`${this.conn.baseUrl}/api/v1/windows/collector/marker`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ room_label, x_norm, y_norm }),
    });
    return r.json();
  }

  async stopWindowsCollector(): Promise<any> {
    const r = await fetch(`${this.conn.baseUrl}/api/v1/windows/collector/stop`, { method: 'POST' });
    return r.json();
  }

  async runActiveProbe(): Promise<any> {
    if (!this.conn.hasWindowsCollector) {
      return { endpoint: '1.1.1.1:443 (Simulated)', latency_ms: 24.6, jitter_ms: 3.1, packet_loss_pct: 0 };
    }
    const r = await fetch(`${this.conn.baseUrl}/api/v1/windows/active-probe`, { method: 'POST' });
    return r.json();
  }

  async runSpeedTest(): Promise<any> {
    if (!this.conn.hasWindowsCollector) {
      return {
        endpoint: 'speed.cloudflare.com (Simulated)',
        download_mbps: 29.8,
        upload_mbps: 18.4,
        bytes_used: 0,
        error: null,
      };
    }
    const r = await fetch(`${this.conn.baseUrl}/api/v1/windows/speed-test`, { method: 'POST' });
    return r.json();
  }

  async compareSessions(sessionA: string, sessionB: string): Promise<any> {
    if (this.conn.mode === 'demo') {
      const sa = DEMO_SESSIONS.find((s) => s.id === sessionA);
      const sb = DEMO_SESSIONS.find((s) => s.id === sessionB);
      return {
        session_a: { id: sessionA, name: sa?.name, device: sa?.device_model, stats: { count: 24, wifi_rssi_median_dbm: -64, bands: ['5 GHz'] } },
        session_b: { id: sessionB, name: sb?.name, device: sb?.device_model, stats: { count: 5, wifi_rssi_median_dbm: -61, wifi_quality_median_pct: 74, bands: ['2.4 GHz'] } },
        caveats: [
          'Different hardware used (Pixel 8 vs ThinkPad / MediaTek Wi-Fi 6). Antenna gain and radio calibration may differ.',
          'Different Wi-Fi bands observed (5 GHz vs 2.4 GHz).',
        ],
      };
    }
    const r = await fetch(`${this.conn.baseUrl}/api/v1/compare?session_a=${encodeURIComponent(sessionA)}&session_b=${encodeURIComponent(sessionB)}`);
    return r.json();
  }

  exportUrl(projectId: string, format: 'csv' | 'json', redact = true): string {
    if (this.conn.mode === 'live') {
      return `${this.conn.baseUrl}/api/v1/projects/${projectId}/export?format=${format}&redact=${redact}`;
    }
    return '';
  }
}
