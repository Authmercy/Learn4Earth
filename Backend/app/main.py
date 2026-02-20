import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.routers import auth, users, subscriptions, payments, learning, carbon, dashboard, admin, monitoring, chatbot, videos
from app.services.progression_service import seed_achievements
from app.services import cache_service
from app.services.backup_service import start_backup_scheduler, stop_backup_scheduler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Actions au demarrage et a l'arret de l'application."""
    # ── Startup ──

    # 1. Creer les tables manquantes
    from sqlalchemy import inspect as sa_inspect, text
    try:
        inspector = sa_inspect(engine)
        existing_tables = set(inspector.get_table_names())
        tables_to_create = [
            table for name, table in Base.metadata.tables.items()
            if name not in existing_tables
        ]
        if tables_to_create:
            Base.metadata.create_all(bind=engine, tables=tables_to_create)
            logger.info("Tables creees : %s", [t.name for t in tables_to_create])
        else:
            logger.info("Toutes les tables existent deja.")
    except Exception as e:
        logger.warning("create_all : %s", e)

    # 2. Migrations manuelles : ajouter les colonnes manquantes
    _migrations = [
        "ALTER TABLE `users` ADD COLUMN `free_courses_remaining` INT NULL DEFAULT 5",
    ]
    with engine.connect() as conn:
        for sql in _migrations:
            try:
                conn.execute(text(sql))
                conn.commit()
                logger.info("Migration OK : %s", sql[:60])
            except Exception:
                pass  # Colonne existe deja, on ignore

    # 2. Initialiser les badges
    db = SessionLocal()
    try:
        seed_achievements(db)
    finally:
        db.close()

    # 2. Initialiser Redis (cache)
    redis_ok = cache_service.init_redis()
    if redis_ok:
        logger.info("Redis : cache actif")
    else:
        logger.warning("Redis : cache desactive (l'application fonctionne sans cache)")

    # 3. Demarrer le planificateur de backup (cron)
    if settings.BACKUP_ENABLED:
        start_backup_scheduler()
        logger.info("Backup scheduler : actif (chaque jour a %02d:%02d UTC)",
                     settings.BACKUP_CRON_HOUR, settings.BACKUP_CRON_MINUTE)

    yield

    # ── Shutdown ──
    # 1. Arreter le planificateur de backup
    stop_backup_scheduler()

    # 2. Fermer Redis
    cache_service.close_redis()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=(
        "API de la plateforme EcoLearn AI - Apprentissage personnalise, "
        "intelligent et ecologique. Parcours adaptatifs generes par IA, "
        "suivi d'empreinte carbone et compensation ecologique."
    ),
    docs_url="/docs",
    redoc_url=None,  # Desactive le redoc par defaut, on cree notre propre page
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics middleware
if settings.PROMETHEUS_ENABLED:
    try:
        from prometheus_fastapi_instrumentator import Instrumentator
        instrumentator = Instrumentator(
            should_group_status_codes=True,
            should_ignore_untemplated=True,
            should_respect_env_var=False,
            excluded_handlers=["/metrics", "/health"],
            env_var_name="ENABLE_METRICS",
        )
        instrumentator.instrument(app).expose(app, endpoint="/metrics", tags=["Prometheus"])
        logger.info("Prometheus : metriques actives sur /metrics")
    except ImportError:
        logger.warning("Prometheus : prometheus-fastapi-instrumentator non installe")

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(subscriptions.router)
app.include_router(payments.router)
app.include_router(learning.router)
app.include_router(carbon.router)
app.include_router(dashboard.router)
app.include_router(admin.router)
app.include_router(monitoring.router)
app.include_router(chatbot.router)
app.include_router(videos.router)


@app.get("/redoc", include_in_schema=False)
def custom_redoc():
    """Page ReDoc avec version fixe du JS (pas de CDN @next instable)."""
    from fastapi.responses import HTMLResponse
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>EcoLearn AI - Documentation API</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        <style>body { margin: 0; padding: 0; }</style>
    </head>
    <body>
        <div id="redoc-container"></div>
        <script src="https://cdn.jsdelivr.net/npm/redoc@2.1.5/bundles/redoc.standalone.js"></script>
        <script>
            Redoc.init('/openapi.json', {
                scrollYOffset: 0,
                hideDownloadButton: false,
                expandResponses: "200,201",
                pathInMiddlePanel: true,
                theme: {
                    colors: {
                        primary: { main: '#2e7d32' }
                    },
                    typography: {
                        fontSize: '15px',
                        fontFamily: 'Roboto, sans-serif',
                    },
                    sidebar: {
                        backgroundColor: '#fafafa',
                        width: '260px'
                    }
                }
            }, document.getElementById('redoc-container'));
        </script>
    </body>
    </html>
    """)


@app.get("/", tags=["Root"])
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "status": "running",
        "docs": "/docs",
        "description": "Plateforme d'apprentissage en ligne intelligente et ecologique",
    }


@app.get("/health", tags=["Health"])
def health_check():
    redis_status = "up" if cache_service.is_available() else "down"
    return {
        "status": "healthy",
        "cache": redis_status,
        "backup_enabled": settings.BACKUP_ENABLED,
    }
