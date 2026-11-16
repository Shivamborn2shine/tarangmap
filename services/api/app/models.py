from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True)
    name = Column(String(160), nullable=False)
    description = Column(Text, nullable=True)
    map_mode = Column(String(24), nullable=False, default="indoor")  # indoor | outdoor | hybrid
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    floorplans = relationship("Floorplan", back_populates="project", cascade="all, delete-orphan")
    sessions = relationship("SurveySession", back_populates="project", cascade="all, delete-orphan")


class Floorplan(Base):
    __tablename__ = "floorplans"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(120), nullable=False, default="Ground Floor")
    image_uri = Column(Text, nullable=False)
    width_px = Column(Integer, nullable=False, default=1000)
    height_px = Column(Integer, nullable=False, default=640)
    scale_m_per_px = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    project = relationship("Project", back_populates="floorplans")


class Device(Base):
    __tablename__ = "devices"

    id = Column(String(36), primary_key=True)
    platform = Column(String(32), nullable=False)  # android | windows | web_demo
    model = Column(String(120), nullable=False)
    os_version = Column(String(64), nullable=False)
    capabilities_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    sessions = relationship("SurveySession", back_populates="device")


class SurveySession(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id = Column(String(36), ForeignKey("devices.id"), nullable=False, index=True)
    name = Column(String(160), nullable=False)
    map_mode = Column(String(24), nullable=False, default="indoor")
    status = Column(String(24), nullable=False, default="recording")  # recording | paused | finished
    started_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    settings_json = Column(Text, nullable=False, default="{}")

    project = relationship("Project", back_populates="sessions")
    device = relationship("Device", back_populates="sessions")
    observations = relationship("Observation", back_populates="session", cascade="all, delete-orphan")


class Observation(Base):
    __tablename__ = "observations"

    id = Column(String(36), primary_key=True)
    schema_version = Column(Integer, nullable=False, default=1)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id = Column(String(36), ForeignKey("devices.id"), nullable=False, index=True)
    kind = Column(String(24), nullable=False)  # wifi | cellular | active_test
    technology = Column(String(24), nullable=False)  # wifi | lte | nr | unknown
    observed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    received_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    metric_source = Column(String(80), nullable=False)
    freshness_ms = Column(Integer, nullable=False, default=0)
    missing_reason = Column(String(120), nullable=True)

    location_kind = Column(String(24), nullable=False, default="unknown")  # indoor | outdoor | unknown
    room_label = Column(String(80), nullable=True)
    x_norm = Column(Float, nullable=True)
    y_norm = Column(Float, nullable=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    gps_accuracy_m = Column(Float, nullable=True)

    session = relationship("SurveySession", back_populates="observations")
    wifi = relationship("WifiObservation", uselist=False, back_populates="observation", cascade="all, delete-orphan")
    cellular = relationship("CellObservation", uselist=False, back_populates="observation", cascade="all, delete-orphan")
    active_test = relationship("ActiveTest", uselist=False, back_populates="observation", cascade="all, delete-orphan")


class WifiObservation(Base):
    __tablename__ = "wifi_observations"

    observation_id = Column(String(36), ForeignKey("observations.id", ondelete="CASCADE"), primary_key=True)
    ssid = Column(String(64), nullable=True)
    bssid_hash = Column(String(64), nullable=True, index=True)
    frequency_mhz = Column(Integer, nullable=True)
    band = Column(String(16), nullable=True)
    channel = Column(Integer, nullable=True)
    rssi_dbm = Column(Integer, nullable=True)
    quality_percent = Column(Integer, nullable=True)
    rx_mbps = Column(Float, nullable=True)
    tx_mbps = Column(Float, nullable=True)
    radio_type = Column(String(32), nullable=True)

    observation = relationship("Observation", back_populates="wifi")


class CellObservation(Base):
    __tablename__ = "cell_observations"

    observation_id = Column(String(36), ForeignKey("observations.id", ondelete="CASCADE"), primary_key=True)
    operator_name = Column(String(64), nullable=True)
    tech = Column(String(16), nullable=True)
    registered = Column(Boolean, nullable=False, default=True)
    rsrp_dbm = Column(Integer, nullable=True)
    rsrq_db = Column(Integer, nullable=True)
    sinr_db = Column(Integer, nullable=True)
    ss_rsrp_dbm = Column(Integer, nullable=True)
    ss_rsrq_db = Column(Integer, nullable=True)
    ss_sinr_db = Column(Integer, nullable=True)
    pci = Column(Integer, nullable=True)
    tac = Column(Integer, nullable=True)
    band = Column(String(32), nullable=True)

    observation = relationship("Observation", back_populates="cellular")


class ActiveTest(Base):
    __tablename__ = "active_tests"

    observation_id = Column(String(36), ForeignKey("observations.id", ondelete="CASCADE"), primary_key=True)
    endpoint = Column(String(120), nullable=False)
    latency_ms = Column(Float, nullable=True)
    jitter_ms = Column(Float, nullable=True)
    packet_loss_pct = Column(Float, nullable=True)
    download_mbps = Column(Float, nullable=True)
    upload_mbps = Column(Float, nullable=True)
    bytes_used = Column(Integer, nullable=True)

    observation = relationship("Observation", back_populates="active_test")


class SyncBatch(Base):
    __tablename__ = "sync_batches"

    id = Column(String(36), primary_key=True)
    device_id = Column(String(36), nullable=False, index=True)
    received_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    accepted_count = Column(Integer, nullable=False, default=0)
    duplicate_count = Column(Integer, nullable=False, default=0)
    rejected_count = Column(Integer, nullable=False, default=0)
