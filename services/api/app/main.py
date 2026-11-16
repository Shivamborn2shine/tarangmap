from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import UPLOAD_DIR
from .database import Base, SessionLocal, engine
from .routers import devices, exports, health, observations, projects, sessions
from .seed import seed_demo_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="TARANG API",
    description="Telecommunication Analysis, Radio Assessment & Network Geomapping (v1)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(projects.router)
app.include_router(devices.router)
app.include_router(sessions.router)
app.include_router(observations.router)
app.include_router(exports.router)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "samples"
if SAMPLES_DIR.exists():
    app.mount("/samples", StaticFiles(directory=str(SAMPLES_DIR)), name="samples")
