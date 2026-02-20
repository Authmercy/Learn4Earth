"""
Service de backup automatique (cron) pour EcoLearn AI.

Replique les donnees de la base principale vers une base de backup
chaque jour a 1h du matin (configurable via BACKUP_CRON_HOUR/MINUTE).

Fonctionnement :
1. Se connecte a la base principale (DATABASE_URL)
2. Lit toutes les tables
3. Ecrit les donnees dans la base de backup (BACKUP_DATABASE_URL)
4. Journalise chaque operation avec timestamps et metriques
5. En cas d'echec, envoie une alerte par email/log

La base de backup est une copie complete (truncate + insert).
"""

import logging
import time
from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, MetaData, text, inspect
from sqlalchemy.orm import sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

# ── Historique des backups ──
_backup_history: list = []
_max_history = 30  # Garder les 30 derniers backups

# ── Statut courant ──
_current_status = {
    "last_run": None,
    "last_status": "never_run",
    "last_duration_seconds": 0,
    "last_tables_copied": 0,
    "last_rows_copied": 0,
    "last_error": None,
    "next_run": None,
    "total_runs": 0,
    "total_successes": 0,
    "total_failures": 0,
}

# Tables a repliquer (dans l'ordre pour respecter les FK logiques)
TABLES_TO_BACKUP = [
    "subscription_plans",
    "achievements",
    "users",
    "subscriptions",
    "payments",
    "learning_paths",
    "learning_sessions",
    "carbon_footprints",
    "eco_compensations",
    "user_achievements",
]


def get_backup_status() -> dict:
    """Retourne le statut courant du systeme de backup."""
    return dict(_current_status)


def get_backup_history() -> list:
    """Retourne l'historique des 30 derniers backups."""
    return list(_backup_history)


def run_backup() -> dict:
    """
    Execute la replication complete de la base principale vers la base de backup.

    Processus :
    1. Connexion aux deux bases
    2. Pour chaque table :
       a. Truncate dans la base backup
       b. SELECT * depuis la base principale
       c. INSERT par lots de 500 lignes dans la base backup
    3. Journalisation du resultat

    Retourne un dict avec le resume de l'operation.
    """
    start_time = time.time()
    run_timestamp = datetime.utcnow()
    _current_status["last_run"] = run_timestamp.isoformat()
    _current_status["last_status"] = "running"
    _current_status["total_runs"] += 1

    logger.info("=" * 60)
    logger.info("BACKUP : Demarrage de la replication - %s", run_timestamp.isoformat())
    logger.info("=" * 60)

    result = {
        "timestamp": run_timestamp.isoformat(),
        "status": "pending",
        "tables": {},
        "total_rows": 0,
        "duration_seconds": 0,
        "error": None,
    }

    # ── Creer les engines ──
    try:
        source_engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={"connect_timeout": 30},
        )
        backup_engine = create_engine(
            settings.BACKUP_DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={"connect_timeout": 30},
        )
    except Exception as e:
        error_msg = f"Erreur de connexion : {str(e)}"
        logger.error("BACKUP ECHEC : %s", error_msg)
        _record_failure(result, error_msg, start_time)
        return result

    # ── Verifier la connexion a la base source ──
    try:
        with source_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("BACKUP : Connexion base source OK")
    except Exception as e:
        error_msg = f"Base source inaccessible : {str(e)}"
        logger.error("BACKUP ECHEC : %s", error_msg)
        _record_failure(result, error_msg, start_time)
        return result

    # ── Verifier/creer la base de backup ──
    try:
        with backup_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("BACKUP : Connexion base backup OK")
    except Exception as e:
        error_msg = f"Base backup inaccessible : {str(e)}"
        logger.error("BACKUP ECHEC : %s", error_msg)
        _record_failure(result, error_msg, start_time)
        return result

    # ── Synchroniser le schema (creer les tables si elles n'existent pas) ──
    try:
        _sync_schema(source_engine, backup_engine)
        logger.info("BACKUP : Schema synchronise")
    except Exception as e:
        logger.warning("BACKUP : Erreur sync schema (non bloquante) - %s", str(e))

    # ── Repliquer chaque table ──
    SourceSession = sessionmaker(bind=source_engine)
    BackupSession = sessionmaker(bind=backup_engine)

    total_rows = 0
    tables_done = 0

    for table_name in TABLES_TO_BACKUP:
        table_start = time.time()
        try:
            rows_copied = _replicate_table(
                source_engine, backup_engine,
                SourceSession, BackupSession,
                table_name,
            )
            table_duration = round(time.time() - table_start, 2)
            total_rows += rows_copied
            tables_done += 1
            result["tables"][table_name] = {
                "status": "ok",
                "rows": rows_copied,
                "duration_seconds": table_duration,
            }
            logger.info("BACKUP : Table %-25s -> %6d lignes (%ss)",
                        table_name, rows_copied, table_duration)
        except Exception as e:
            table_duration = round(time.time() - table_start, 2)
            error_msg = str(e)
            result["tables"][table_name] = {
                "status": "error",
                "error": error_msg,
                "duration_seconds": table_duration,
            }
            logger.error("BACKUP : Table %s ECHEC - %s", table_name, error_msg)

    # ── Resultat final ──
    duration = round(time.time() - start_time, 2)
    result["total_rows"] = total_rows
    result["duration_seconds"] = duration

    failed_tables = [t for t, v in result["tables"].items() if v["status"] == "error"]
    if failed_tables:
        result["status"] = "partial"
        result["error"] = f"Tables en echec : {', '.join(failed_tables)}"
        logger.warning("BACKUP PARTIEL : %d/%d tables, %d lignes, %ss",
                        tables_done, len(TABLES_TO_BACKUP), total_rows, duration)
    else:
        result["status"] = "success"
        logger.info("BACKUP SUCCES : %d tables, %d lignes, %ss",
                     tables_done, total_rows, duration)

    # ── Mettre a jour le statut global ──
    _current_status["last_status"] = result["status"]
    _current_status["last_duration_seconds"] = duration
    _current_status["last_tables_copied"] = tables_done
    _current_status["last_rows_copied"] = total_rows
    _current_status["last_error"] = result.get("error")
    if result["status"] == "success":
        _current_status["total_successes"] += 1
    else:
        _current_status["total_failures"] += 1

    # ── Ajouter a l'historique ──
    _backup_history.insert(0, {
        "timestamp": run_timestamp.isoformat(),
        "status": result["status"],
        "tables": tables_done,
        "rows": total_rows,
        "duration": duration,
        "error": result.get("error"),
    })
    if len(_backup_history) > _max_history:
        _backup_history.pop()

    # ── Envoyer notification si echec ──
    if result["status"] != "success":
        _notify_backup_failure(result)

    # Fermer les engines
    source_engine.dispose()
    backup_engine.dispose()

    logger.info("=" * 60)
    return result


def _replicate_table(
    source_engine, backup_engine,
    SourceSession, BackupSession,
    table_name: str,
) -> int:
    """
    Replique une table de la source vers le backup.
    Truncate + Insert par lots de 500.
    Retourne le nombre de lignes copiees.
    """
    batch_size = 500

    # Lire les donnees source
    with source_engine.connect() as src_conn:
        rows = src_conn.execute(text(f"SELECT * FROM {table_name}")).fetchall()
        if not rows:
            # Truncate la table backup meme si vide (coherence)
            with backup_engine.connect() as bkp_conn:
                bkp_conn.execute(text(f"DELETE FROM {table_name}"))
                bkp_conn.commit()
            return 0

        # Recuperer les noms de colonnes
        columns = src_conn.execute(text(f"SELECT * FROM {table_name} LIMIT 0")).keys()
        col_names = list(columns)

    # Truncate la table backup
    with backup_engine.connect() as bkp_conn:
        bkp_conn.execute(text(f"SET FOREIGN_KEY_CHECKS = 0"))
        bkp_conn.execute(text(f"DELETE FROM {table_name}"))
        bkp_conn.commit()

    # Inserer par lots
    total = 0
    with backup_engine.connect() as bkp_conn:
        bkp_conn.execute(text(f"SET FOREIGN_KEY_CHECKS = 0"))

        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            # Construire l'INSERT avec des parametres nommes
            placeholders = ", ".join([f":{c}" for c in col_names])
            col_list = ", ".join([f"`{c}`" for c in col_names])
            insert_sql = text(f"INSERT INTO {table_name} ({col_list}) VALUES ({placeholders})")

            params = []
            for row in batch:
                row_dict = {}
                for idx, col in enumerate(col_names):
                    val = row[idx]
                    # Convertir les types non serialisables
                    if isinstance(val, bytes):
                        val = val.decode("utf-8", errors="replace")
                    row_dict[col] = val
                params.append(row_dict)

            bkp_conn.execute(insert_sql, params)
            total += len(batch)

        bkp_conn.execute(text(f"SET FOREIGN_KEY_CHECKS = 1"))
        bkp_conn.commit()

    return total


def _sync_schema(source_engine, backup_engine):
    """
    Synchronise le schema : cree les tables manquantes dans la base backup.
    Utilise les metadonnees de SQLAlchemy pour refleter le schema source.
    """
    meta = MetaData()
    meta.reflect(bind=source_engine)

    # Verifier quelles tables existent deja dans le backup
    backup_inspector = inspect(backup_engine)
    existing_tables = backup_inspector.get_table_names()

    for table_name, table in meta.tables.items():
        if table_name not in existing_tables:
            logger.info("BACKUP SCHEMA : Creation table manquante '%s'", table_name)
            table.create(bind=backup_engine, checkfirst=True)


def _record_failure(result: dict, error_msg: str, start_time: float):
    """Enregistre un echec de backup."""
    duration = round(time.time() - start_time, 2)
    result["status"] = "failed"
    result["error"] = error_msg
    result["duration_seconds"] = duration

    _current_status["last_status"] = "failed"
    _current_status["last_duration_seconds"] = duration
    _current_status["last_error"] = error_msg
    _current_status["total_failures"] += 1

    _backup_history.insert(0, {
        "timestamp": result["timestamp"],
        "status": "failed",
        "tables": 0,
        "rows": 0,
        "duration": duration,
        "error": error_msg,
    })
    if len(_backup_history) > _max_history:
        _backup_history.pop()

    _notify_backup_failure(result)


def _notify_backup_failure(result: dict):
    """Envoie une notification en cas d'echec du backup."""
    try:
        from app.services.email_service import send_email
        subject = f"[ALERTE] EcoLearn AI - Echec backup {result['timestamp']}"
        body = (
            f"Le backup automatique a echoue.\n\n"
            f"Statut : {result['status']}\n"
            f"Erreur : {result.get('error', 'N/A')}\n"
            f"Duree : {result.get('duration_seconds', 0)}s\n"
            f"Tables : {len(result.get('tables', {}))}\n"
            f"Lignes : {result.get('total_rows', 0)}\n\n"
            f"Verifiez la base de backup et les logs immediatement."
        )
        send_email(
            to_email=settings.EMAIL_HOST_USER,
            subject=subject,
            body=body,
        )
    except Exception as e:
        logger.error("BACKUP : Impossible d'envoyer l'alerte email - %s", str(e))


# ══════════════════════════════════════════════════════════
#  SCHEDULER (APScheduler)
# ══════════════════════════════════════════════════════════

_scheduler = None


def start_backup_scheduler():
    """
    Demarre le planificateur de backup.
    Execute run_backup() chaque jour a BACKUP_CRON_HOUR:BACKUP_CRON_MINUTE.
    """
    global _scheduler

    if not settings.BACKUP_ENABLED:
        logger.info("BACKUP : Planificateur desactive (BACKUP_ENABLED=false)")
        return

    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger

        _scheduler = BackgroundScheduler(
            job_defaults={"coalesce": True, "max_instances": 1}
        )

        trigger = CronTrigger(
            hour=settings.BACKUP_CRON_HOUR,
            minute=settings.BACKUP_CRON_MINUTE,
            timezone="UTC",
        )

        _scheduler.add_job(
            run_backup,
            trigger=trigger,
            id="daily_backup",
            name="Replication quotidienne vers base de backup",
            replace_existing=True,
        )

        _scheduler.start()

        # Mettre a jour le prochain run
        job = _scheduler.get_job("daily_backup")
        if job and job.next_run_time:
            _current_status["next_run"] = job.next_run_time.isoformat()

        logger.info(
            "BACKUP : Planificateur demarre - backup chaque jour a %02d:%02d UTC",
            settings.BACKUP_CRON_HOUR,
            settings.BACKUP_CRON_MINUTE,
        )
    except Exception as e:
        logger.error("BACKUP : Erreur demarrage planificateur - %s", str(e))


def stop_backup_scheduler():
    """Arrete proprement le planificateur."""
    global _scheduler
    if _scheduler:
        try:
            _scheduler.shutdown(wait=False)
            logger.info("BACKUP : Planificateur arrete")
        except Exception:
            pass
        _scheduler = None
