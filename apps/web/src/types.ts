export type SignalTier = 'Strong' | 'Good' | 'Fair' | 'Weak' | 'Unavailable';

export interface Project {
  id: string;
  name: string;
  description?: string | null;
  map_mode: 'indoor' | 'outdoor' | 'hybrid';
  created_at: string;
  session_count: number;
  observation_count: number;
}

export interface Floorplan {
  id: string;
  project_id: string;
  name: string;
  image_uri: string;
  width_px: number;
  height_px: number;
  scale_m_per_px?: number | null;
}

export interface SurveySession {
  id: string;
  project_id: string;
  device_id: string;
  device_model?: string | null;
  device_platform?: string | null;
  name: string;
  map_mode: 'indoor' | 'outdoor' | 'hybrid';
  status: 'recording' | 'paused' | 'finished';
  started_at: string;
  ended_at?: string | null;
  observation_count: number;
}

export interface Observation {
  schema_version: 1;
  id: string;
  session_id: string;
  device_id: string;
  kind: 'wifi' | 'cellular' | 'active_test';
  technology: 'wifi' | 'lte' | 'nr' | 'unknown';
  observed_at: string;
  recorded_at: string;
  metric_source: string;
  freshness_ms: number;
  missing_reason?: string | null;
  location_kind: 'indoor' | 'outdoor' | 'unknown';
  room_label?: string | null;
  x_norm?: number | null;
  y_norm?: number | null;
  lat?: number | null;
  lon?: number | null;
  gps_accuracy_m?: number | null;
  signal_tier: SignalTier;
  primary_metric_label: string;
  wifi?: {
    ssid?: string | null;
    bssid_hash?: string | null;
    frequency_mhz?: number | null;
    band?: string | null;
    channel?: number | null;
    rssi_dbm?: number | null;
    quality_percent?: number | null;
    rx_mbps?: number | null;
    tx_mbps?: number | null;
    radio_type?: string | null;
  } | null;
  cellular?: {
    operator_name?: string | null;
    tech?: string | null;
    registered: boolean;
    rsrp_dbm?: number | null;
    rsrq_db?: number | null;
    sinr_db?: number | null;
    ss_rsrp_dbm?: number | null;
    ss_rsrq_db?: number | null;
    ss_sinr_db?: number | null;
    pci?: number | null;
    tac?: number | null;
    band?: string | null;
  } | null;
  active_test?: {
    endpoint: string;
    latency_ms?: number | null;
    jitter_ms?: number | null;
    packet_loss_pct?: number | null;
  } | null;
}

export interface ProjectSummary {
  project_id: string;
  project_name: string;
  total_observations: number;
  measured_areas_count: number;
  typical_wifi_rssi_dbm: number | null;
  typical_wifi_quality_pct: number | null;
  typical_lte_rsrp_dbm: number | null;
  typical_nr_ss_rsrp_dbm: number | null;
  uncertain_gps_count: number;
  wifi_tier_distribution: Record<string, number>;
  cellular_tier_distribution: Record<string, number>;
  weak_spots: Array<{
    area: string;
    metric: string;
    median_value: number;
    unit: string;
    tier: string;
    sample_count: number;
    confidence: string;
  }>;
  recommendations: Array<{
    rule: string;
    title: string;
    finding: string;
    evidence: string;
    confidence: string;
    suggested_test: string;
  }>;
}

export interface WindowsCapabilities {
  platform: string;
  collector_mode: string;
  adapter_available: boolean;
  adapter_name?: string | null;
  adapter_description?: string | null;
  os_version?: string | null;
  capabilities: {
    wifi_quality_percent: boolean;
    wifi_rssi_dbm: boolean;
    wifi_band_channel: boolean;
    active_tcp_probe: boolean;
    cellular_radio: boolean;
    gps: boolean;
  };
  notes: string;
}

export interface WindowsLiveScan {
  available: boolean;
  observed_at: string;
  adapter_name?: string | null;
  adapter_description?: string | null;
  state: string;
  ssid?: string | null;
  band?: string | null;
  channel?: number | null;
  frequency_mhz?: number | null;
  radio_type?: string | null;
  quality_percent?: number | null;
  rssi_dbm?: number | null;
  rssi_supported?: boolean;
  rx_mbps?: number | null;
  tx_mbps?: number | null;
  missing_reason?: string | null;
}
