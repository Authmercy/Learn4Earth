"""
Router de monitoring et sante du systeme.

Endpoints :
- /api/monitoring/health        : Sante globale (backend, DB, Redis, AI)
- /api/monitoring/system        : Metriques systeme (CPU, RAM, disque)
- /api/monitoring/redis         : Statistiques Redis detaillees
- /api/monitoring/database      : Etat de la base de donnees
- /api/monitoring/backup        : Statut du dernier backup
- /api/monitoring/cache/flush   : Vider le cache (admin)
"""

import platform
import logging
from datetime import datetime

import psutil
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.services import cache_service
from app.utils.security import get_current_admin

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])

# Timestamp de demarrage
_start_time = datetime.utcnow()


# ══════════════════════════════════════════════════════════
#  HEALTH CHECK GLOBAL
# ══════════════════════════════════════════════════════════

@router.get("/health")
def health_check_detailed(db: Session = Depends(get_db)):
    """
    Verification de sante detaillee de tous les composants.
    Retourne un statut global + le detail par composant.
    """
    checks = {}
    overall = "healthy"

    # ── Backend ──
    uptime_seconds = (datetime.utcnow() - _start_time).total_seconds()
    checks["backend"] = {
        "status": "up",
        "uptime_seconds": round(uptime_seconds, 0),
        "uptime_human": _format_uptime(uptime_seconds),
        "version": settings.PROJECT_VERSION,
        "python": platform.python_version(),
    }

    # ── Base de donnees MySQL ──
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        db_version = db.execute(text("SELECT VERSION()")).scalar()
        checks["database"] = {
            "status": "up",
            "engine": "MySQL",
            "version": db_version,
            "host": settings.DATABASE_URL.split("@")[1].split("/")[0] if "@" in settings.DATABASE_URL else "unknown",
        }
    except Exception as e:
        checks["database"] = {"status": "down", "error": str(e)}
        overall = "degraded"

    # ── Redis ──
    if cache_service.is_available():
        redis_stats = cache_service.get_cache_stats()
        checks["redis"] = {
            "status": "up",
            "host": f"{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            "keys": redis_stats.get("ecolearnai_keys", 0),
            "memory": redis_stats.get("memory", {}),
        }
    else:
        checks["redis"] = {
            "status": "down",
            "host": f"{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            "note": "Le cache est desactive, l'application fonctionne sans cache.",
        }
        if overall == "healthy":
            overall = "degraded"

    # ── AI Service ──
    try:
        import httpx
        ai_resp = httpx.get(f"{settings.AI_SERVICE_URL}/health", timeout=3)
        if ai_resp.status_code == 200:
            checks["ai_service"] = {"status": "up", "url": settings.AI_SERVICE_URL}
        else:
            checks["ai_service"] = {"status": "degraded", "http_code": ai_resp.status_code}
            if overall == "healthy":
                overall = "degraded"
    except Exception:
        checks["ai_service"] = {"status": "unreachable", "url": settings.AI_SERVICE_URL}
        if overall == "healthy":
            overall = "degraded"

    # ── Backup DB ──
    if settings.BACKUP_ENABLED:
        from app.services.backup_service import get_backup_status
        backup_info = get_backup_status()
        checks["backup"] = backup_info
    else:
        checks["backup"] = {"status": "disabled"}

    return {
        "status": overall,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks,
    }


# ══════════════════════════════════════════════════════════
#  METRIQUES SYSTEME (CPU, RAM, Disque)
# ══════════════════════════════════════════════════════════

@router.get("/system")
def system_metrics(admin: User = Depends(get_current_admin)):
    """
    Metriques systeme en temps reel.
    Reserve aux administrateurs.
    """
    # CPU
    cpu_percent = psutil.cpu_percent(interval=0.5)
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()

    # Memoire RAM
    mem = psutil.virtual_memory()

    # Disque
    disk = psutil.disk_usage("/")

    # Reseau
    net = psutil.net_io_counters()

    # Processus Python
    process = psutil.Process()
    proc_mem = process.memory_info()

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu": {
            "percent": cpu_percent,
            "count": cpu_count,
            "frequency_mhz": round(cpu_freq.current, 0) if cpu_freq else None,
        },
        "memory": {
            "total_gb": round(mem.total / (1024 ** 3), 2),
            "available_gb": round(mem.available / (1024 ** 3), 2),
            "used_gb": round(mem.used / (1024 ** 3), 2),
            "percent": mem.percent,
        },
        "disk": {
            "total_gb": round(disk.total / (1024 ** 3), 2),
            "used_gb": round(disk.used / (1024 ** 3), 2),
            "free_gb": round(disk.free / (1024 ** 3), 2),
            "percent": disk.percent,
        },
        "network": {
            "bytes_sent_mb": round(net.bytes_sent / (1024 ** 2), 2),
            "bytes_recv_mb": round(net.bytes_recv / (1024 ** 2), 2),
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
        },
        "process": {
            "pid": process.pid,
            "memory_rss_mb": round(proc_mem.rss / (1024 ** 2), 2),
            "memory_vms_mb": round(proc_mem.vms / (1024 ** 2), 2),
            "threads": process.num_threads(),
            "cpu_percent": process.cpu_percent(),
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
    }


# ══════════════════════════════════════════════════════════
#  REDIS DETAILLE
# ══════════════════════════════════════════════════════════

@router.get("/redis")
def redis_details(admin: User = Depends(get_current_admin)):
    """Statistiques Redis detaillees. Reserve aux administrateurs."""
    stats = cache_service.get_cache_stats()
    stats["config"] = {
        "host": settings.REDIS_HOST,
        "port": settings.REDIS_PORT,
        "db": settings.REDIS_DB,
        "max_connections": settings.REDIS_MAX_CONNECTIONS,
        "key_prefix": cache_service.KEY_PREFIX,
        "default_ttl": cache_service.DEFAULT_TTL,
    }
    return stats


# ══════════════════════════════════════════════════════════
#  DATABASE DETAILLE
# ══════════════════════════════════════════════════════════

@router.get("/database")
def database_details(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Informations detaillees sur la base de donnees. Reserve aux administrateurs."""
    try:
        version = db.execute(text("SELECT VERSION()")).scalar()

        # Taille des tables
        tables_raw = db.execute(text("""
            SELECT
                TABLE_NAME,
                TABLE_ROWS,
                ROUND(DATA_LENGTH / 1024 / 1024, 2) AS data_mb,
                ROUND(INDEX_LENGTH / 1024 / 1024, 2) AS index_mb,
                ENGINE
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = 'ecolearnai_db'
            ORDER BY DATA_LENGTH DESC
        """)).fetchall()

        tables = [
            {
                "table": row[0],
                "rows": row[1],
                "data_mb": float(row[2]) if row[2] else 0,
                "index_mb": float(row[3]) if row[3] else 0,
                "engine": row[4],
            }
            for row in tables_raw
        ]

        total_data = sum(t["data_mb"] for t in tables)
        total_index = sum(t["index_mb"] for t in tables)

        # Connexions
        connections = db.execute(text("SHOW STATUS LIKE 'Threads_connected'")).fetchone()
        max_conn = db.execute(text("SHOW VARIABLES LIKE 'max_connections'")).fetchone()

        # Variables NDB si disponibles
        ndb_status = None
        try:
            ndb_raw = db.execute(text("SHOW STATUS LIKE 'Ndb_%'")).fetchall()
            if ndb_raw:
                ndb_status = {row[0]: row[1] for row in ndb_raw[:20]}
        except Exception:
            pass

        return {
            "version": version,
            "host": settings.DATABASE_URL.split("@")[1].split("/")[0] if "@" in settings.DATABASE_URL else "unknown",
            "database": "ecolearnai_db",
            "tables": tables,
            "total_data_mb": round(total_data, 2),
            "total_index_mb": round(total_index, 2),
            "total_size_mb": round(total_data + total_index, 2),
            "connections": {
                "current": int(connections[1]) if connections else 0,
                "max": int(max_conn[1]) if max_conn else 0,
            },
            "ndb_cluster": ndb_status,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de donnees : {str(e)}")


# ══════════════════════════════════════════════════════════
#  STATUT BACKUP
# ══════════════════════════════════════════════════════════

@router.get("/backup")
def backup_status(admin: User = Depends(get_current_admin)):
    """Statut du systeme de backup automatique."""
    from app.services.backup_service import get_backup_status, get_backup_history
    return {
        "enabled": settings.BACKUP_ENABLED,
        "schedule": f"Chaque jour a {settings.BACKUP_CRON_HOUR:02d}:{settings.BACKUP_CRON_MINUTE:02d} UTC",
        "backup_db": settings.BACKUP_DATABASE_URL.split("@")[1].split("?")[0] if "@" in settings.BACKUP_DATABASE_URL else "non configure",
        "current_status": get_backup_status(),
        "history": get_backup_history(),
    }


# ══════════════════════════════════════════════════════════
#  ADMIN : FLUSH CACHE
# ══════════════════════════════════════════════════════════

@router.post("/cache/flush")
def flush_cache(admin: User = Depends(get_current_admin)):
    """Vider entierement le cache Redis. Reserve aux administrateurs."""
    success = cache_service.flush_all_cache()
    if success:
        return {"message": "Cache Redis vide avec succes.", "status": "flushed"}
    return {"message": "Redis non disponible ou erreur.", "status": "error"}


# ══════════════════════════════════════════════════════════
#  UTILITAIRES
# ══════════════════════════════════════════════════════════

def _format_uptime(seconds: float) -> str:
    """Formate un nombre de secondes en chaine lisible."""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    parts = []
    if days > 0:
        parts.append(f"{days}j")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return " ".join(parts)
