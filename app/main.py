import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import settings

# Configurar logging DEBUG temporariamente
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("app").setLevel(logging.DEBUG)
from app.core.ws_manager import ws_manager
from app.db import init_db
from app.db.migrations.migration_v1_13 import run as migration_v1_13
from app.db.migrations.migration_v1_20 import run as migration_v1_20
from app.db.migrations.migration_v1_30 import run as migration_v1_30
from app.db.migrations.migration_v1_35 import run as migration_v1_35
from app.db.migrations.migration_v1_40 import run as migration_v1_40
from app.api.v1.auth import router as auth_router
from app.api.v1.export import router as export_router
from app.api.v1.faces import router as faces_router
from app.api.v1.health import router as health_router
from app.api.v1.upload import router as upload_router
from app.api.v1.videos import router as videos_router
from app.api.v1.people import router as people_router
from app.api.v1.timeline import router as timeline_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.search import router as search_router
from app.api.v1.employees import router as employees_router
from app.api.v1.ws import router as ws_router


from app.core.model_downloader import ensure_models_downloaded


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_models_downloaded()
    init_db()
    migration_v1_13()
    migration_v1_20()
    migration_v1_30()
    migration_v1_35()
    migration_v1_40()
    ws_manager.set_loop(asyncio.get_event_loop())
    yield



app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DOCS_ENABLED else None,
    redoc_url="/redoc" if settings.DOCS_ENABLED else None,
)


@app.middleware("http")
async def security_headers_middleware(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' data: blob:; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com"
    )
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(export_router, prefix=settings.API_V1_PREFIX)
app.include_router(health_router, prefix=settings.API_V1_PREFIX)
app.include_router(upload_router, prefix=settings.API_V1_PREFIX)
app.include_router(videos_router, prefix=settings.API_V1_PREFIX)
app.include_router(people_router, prefix=settings.API_V1_PREFIX)
app.include_router(timeline_router, prefix=settings.API_V1_PREFIX)
app.include_router(employees_router, prefix=settings.API_V1_PREFIX)
app.include_router(faces_router, prefix=settings.API_V1_PREFIX)
app.include_router(alerts_router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics_router, prefix=settings.API_V1_PREFIX)
app.include_router(search_router, prefix=settings.API_V1_PREFIX)
app.include_router(ws_router, prefix=settings.API_V1_PREFIX)
