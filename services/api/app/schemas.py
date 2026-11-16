from datetime import datetime
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, field_validator


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: Optional[str] = None
    map_mode: Literal["indoor", "outdoor", "hybrid"] = "indoor"


class ProjectOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    map_mode: str
    created_at: datetime
    session_count: int = 0
    observation_count: int = 0


class FloorplanOut(BaseModel):
    id: str
    project_id: str
    name: str
    image_uri: str
    width_px: int
    height_px: int
    scale_m_per_px: Optional[float] = None
    created_at: datetime


class DeviceRegister(BaseModel):
    id: Optional[str] = None
    platform: Literal["android", "windows", "web_demo"]
    model: str = Field(min_length=1, max_length=120)
    os_version: str = Field(min_length=1, max_length=64)
    capabilities: dict[str, Any] = Field(default_factory=dict)


class DeviceOut(BaseModel):
    id: str
    platform: str
    model: str
    os_version: str
    capabilities: dict[str, Any]
    created_at: datetime


class SessionCreate(BaseModel):
    project_id: str
    device_id: str
    name: str = Field(min_length=1, max_length=160)
    map_mode: Literal["indoor", "outdoor", "hybrid"] = "indoor"
    settings: dict[str, Any] = Field(default_factory=dict)


class SessionPatch(BaseModel):
    status: Optional[Literal["recording", "paused", "finished"]] = None
    name: Optional[str] = None


class SessionOut(BaseModel):
    id: str
    project_id: str
    device_id: str
    device_model: Optional[str] = None
    device_platform: Optional[str] = None
    name: str
    map_mode: str
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    settings: dict[str, Any] = Field(default_factory=dict)
    observation_count: int = 0


class WifiPayload(BaseModel):
    ssid: Optional[str] = None
    bssid_hash: Optional[str] = None
    frequency_mhz: Optional[int] = None
    band: Optional[str] = None
    channel: Optional[int] = None
    rssi_dbm: Optional[int] = Field(default=None, ge=-120, le=0)
    quality_percent: Optional[int] = Field(default=None, ge=0, le=100)
    rx_mbps: Optional[float] = None
    tx_mbps: Optional[float] = None
    radio_type: Optional[str] = None


class CellularPayload(BaseModel):
    operator_name: Optional[str] = None
    tech: Optional[str] = None
    registered: bool = True
    rsrp_dbm: Optional[int] = None
    rsrq_db: Optional[int] = None
    sinr_db: Optional[int] = None
    ss_rsrp_dbm: Optional[int] = None
    ss_rsrq_db: Optional[int] = None
    ss_sinr_db: Optional[int] = None
    pci: Optional[int] = None
    tac: Optional[int] = None
    band: Optional[str] = None


class ActiveTestPayload(BaseModel):
    endpoint: str
    latency_ms: Optional[float] = None
    jitter_ms: Optional[float] = None
    packet_loss_pct: Optional[float] = None
    download_mbps: Optional[float] = None
    upload_mbps: Optional[float] = None
    bytes_used: Optional[int] = None


class ObservationIn(BaseModel):
    schema_version: Literal[1] = 1
    id: str
    session_id: str
    device_id: str
    kind: Literal["wifi", "cellular", "active_test"]
    technology: Literal["wifi", "lte", "nr", "unknown"]
    observed_at: datetime
    recorded_at: datetime
    metric_source: str
    freshness_ms: int = Field(ge=0)
    missing_reason: Optional[str] = None
    location_kind: Literal["indoor", "outdoor", "unknown"]
    room_label: Optional[str] = None
    x_norm: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    y_norm: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    lat: Optional[float] = Field(default=None, ge=-90.0, le=90.0)
    lon: Optional[float] = Field(default=None, ge=-180.0, le=180.0)
    gps_accuracy_m: Optional[float] = Field(default=None, ge=0.0)
    wifi: Optional[WifiPayload] = None
    cellular: Optional[CellularPayload] = None
    active_test: Optional[ActiveTestPayload] = None


class ObservationOut(ObservationIn):
    received_at: datetime
    signal_tier: str
    primary_metric_label: str


class BatchIngestRequest(BaseModel):
    batch_id: str
    device_id: str
    observations: list[ObservationIn]

    @field_validator("observations")
    @classmethod
    def check_batch_limit(cls, v: list[ObservationIn]) -> list[ObservationIn]:
        if len(v) > 500:
            raise ValueError("Batch limit is 500 observations per request")
        return v


class BatchItemResult(BaseModel):
    id: str
    status: Literal["accepted", "duplicate", "rejected"]
    reason: Optional[str] = None


class BatchIngestResponse(BaseModel):
    batch_id: str
    accepted: int
    duplicate: int
    rejected: int
    items: list[BatchItemResult]
