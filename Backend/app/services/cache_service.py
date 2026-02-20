"""
Service de cache Redis pour EcoLearn AI.

Fournit un wrapper autour de redis-py avec :
- Connexion pool avec health check
- Serialisation/deserialisation JSON automatique
- TTL configurable par cle
- Invalidation par prefixe (pattern)
- Decorateur @cached pour les fonctions
- Metriques (hits, misses, taille)
"""

import json
import logging
import functools
from typing import Any, Optional, Callable
from datetime import timedelta

import redis
from redis.exceptions import ConnectionError, TimeoutError, RedisError

from app.config import settings

logger = logging.getLogger(__name__)

# ── Pool de connexions Redis ───────────────────────────────────
_pool: Optional[redis.ConnectionPool] = None
_client: Optional[redis.Redis] = None

# Compteurs de metriques internes
_stats = {"hits": 0, "misses": 0, "errors": 0, "sets": 0, "deletes": 0}

# Prefixe global pour toutes les cles (isolation multi-app)
KEY_PREFIX = "ecolearnai:"

# TTL par defaut (secondes)
DEFAULT_TTL = 300  # 5 minutes


# ══════════════════════════════════════════════════════════
#  INITIALISATION / FERMETURE
# ══════════════════════════════════════════════════════════

def init_redis() -> bool:
    """
    Initialise le pool de connexions Redis.
    Retourne True si la connexion est etablie, False sinon.
    """
    global _pool, _client
    try:
        _pool = redis.ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD or None,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
            decode_responses=True,  # Retourne des str au lieu de bytes
            health_check_interval=30,
        )
        _client = redis.Redis(connection_pool=_pool)
        # Test de connexion
        _client.ping()
        logger.info("Redis : connexion etablie (%s:%s db=%s)",
                     settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)
        return True
    except (ConnectionError, TimeoutError) as e:
        logger.warning("Redis : connexion echouee - %s (le cache sera desactive)", str(e))
        _client = None
        return False
    except Exception as e:
        logger.error("Redis : erreur inattendue - %s", str(e))
        _client = None
        return False


def close_redis():
    """Ferme proprement la connexion Redis."""
    global _client, _pool
    if _client:
        try:
            _client.close()
        except Exception:
            pass
    if _pool:
        try:
            _pool.disconnect()
        except Exception:
            pass
    _client = None
    _pool = None
    logger.info("Redis : connexion fermee")


def get_redis() -> Optional[redis.Redis]:
    """Retourne le client Redis (ou None si non disponible)."""
    return _client


def is_available() -> bool:
    """Verifie si Redis est disponible."""
    if not _client:
        return False
    try:
        return _client.ping()
    except (ConnectionError, TimeoutError, RedisError):
        return False


# ══════════════════════════════════════════════════════════
#  OPERATIONS CRUD CACHE
# ══════════════════════════════════════════════════════════

def _make_key(key: str) -> str:
    """Ajoute le prefixe global a la cle."""
    return f"{KEY_PREFIX}{key}"


def cache_get(key: str) -> Optional[Any]:
    """
    Recupere une valeur du cache.
    Retourne None si la cle n'existe pas ou si Redis est indisponible.
    """
    if not _client:
        return None
    try:
        raw = _client.get(_make_key(key))
        if raw is None:
            _stats["misses"] += 1
            return None
        _stats["hits"] += 1
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        _stats["hits"] += 1
        return raw
    except (ConnectionError, TimeoutError) as e:
        _stats["errors"] += 1
        logger.warning("Redis GET erreur: %s", str(e))
        return None


def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """
    Stocke une valeur dans le cache.
    ttl : duree de vie en secondes (defaut: DEFAULT_TTL)
    """
    if not _client:
        return False
    try:
        serialized = json.dumps(value, default=str, ensure_ascii=False)
        expire = ttl if ttl is not None else DEFAULT_TTL
        _client.setex(_make_key(key), expire, serialized)
        _stats["sets"] += 1
        return True
    except (ConnectionError, TimeoutError, TypeError) as e:
        _stats["errors"] += 1
        logger.warning("Redis SET erreur: %s", str(e))
        return False


def cache_delete(key: str) -> bool:
    """Supprime une cle du cache."""
    if not _client:
        return False
    try:
        _client.delete(_make_key(key))
        _stats["deletes"] += 1
        return True
    except (ConnectionError, TimeoutError) as e:
        _stats["errors"] += 1
        logger.warning("Redis DEL erreur: %s", str(e))
        return False


def cache_delete_pattern(pattern: str) -> int:
    """
    Supprime toutes les cles correspondant au pattern.
    Ex : cache_delete_pattern("plans:*") supprime toutes les cles plans:*
    Retourne le nombre de cles supprimees.
    """
    if not _client:
        return 0
    try:
        full_pattern = _make_key(pattern)
        keys = list(_client.scan_iter(match=full_pattern, count=200))
        if keys:
            deleted = _client.delete(*keys)
            _stats["deletes"] += deleted
            return deleted
        return 0
    except (ConnectionError, TimeoutError) as e:
        _stats["errors"] += 1
        logger.warning("Redis DEL PATTERN erreur: %s", str(e))
        return 0


def cache_exists(key: str) -> bool:
    """Verifie si une cle existe dans le cache."""
    if not _client:
        return False
    try:
        return bool(_client.exists(_make_key(key)))
    except (ConnectionError, TimeoutError):
        return False


def cache_ttl(key: str) -> int:
    """Retourne le TTL restant en secondes (-1 = pas de TTL, -2 = cle inexistante)."""
    if not _client:
        return -2
    try:
        return _client.ttl(_make_key(key))
    except (ConnectionError, TimeoutError):
        return -2


# ══════════════════════════════════════════════════════════
#  CACHE SPECIALISE (OTP, Sessions, Plans)
# ══════════════════════════════════════════════════════════

# ── Cache OTP (anti brute-force) ──
def cache_otp_attempt(user_id: str) -> int:
    """
    Incremente le compteur de tentatives OTP pour un utilisateur.
    Expire apres 15 minutes. Retourne le nombre de tentatives.
    """
    if not _client:
        return 0
    key = _make_key(f"otp_attempts:{user_id}")
    try:
        pipe = _client.pipeline()
        pipe.incr(key)
        pipe.expire(key, 900)  # 15 minutes
        results = pipe.execute()
        return results[0]
    except (ConnectionError, TimeoutError):
        return 0


def cache_otp_is_blocked(user_id: str, max_attempts: int = 5) -> bool:
    """Verifie si un utilisateur a depasse le nombre max de tentatives OTP."""
    if not _client:
        return False
    try:
        count = _client.get(_make_key(f"otp_attempts:{user_id}"))
        return int(count or 0) >= max_attempts
    except (ConnectionError, TimeoutError):
        return False


# ── Cache Plans d'abonnement ──
PLANS_CACHE_KEY = "plans:active"
PLANS_TTL = 600  # 10 minutes


def cache_get_plans() -> Optional[list]:
    """Recupere la liste des plans actifs depuis le cache."""
    return cache_get(PLANS_CACHE_KEY)


def cache_set_plans(plans: list):
    """Met en cache la liste des plans actifs."""
    cache_set(PLANS_CACHE_KEY, plans, ttl=PLANS_TTL)


def cache_invalidate_plans():
    """Invalide le cache des plans (apres modification admin)."""
    cache_delete(PLANS_CACHE_KEY)
    cache_delete_pattern("plans:*")


# ── Cache Dashboard Admin ──
ADMIN_DASHBOARD_KEY = "admin:dashboard"
ADMIN_DASHBOARD_TTL = 120  # 2 minutes


def cache_get_admin_dashboard() -> Optional[dict]:
    return cache_get(ADMIN_DASHBOARD_KEY)


def cache_set_admin_dashboard(data: dict):
    cache_set(ADMIN_DASHBOARD_KEY, data, ttl=ADMIN_DASHBOARD_TTL)


def cache_invalidate_admin_dashboard():
    cache_delete(ADMIN_DASHBOARD_KEY)


# ── Cache User Dashboard ──
def cache_get_user_dashboard(user_id: str) -> Optional[dict]:
    return cache_get(f"dashboard:user:{user_id}")


def cache_set_user_dashboard(user_id: str, data: dict):
    cache_set(f"dashboard:user:{user_id}", data, ttl=180)  # 3 minutes


def cache_invalidate_user_dashboard(user_id: str):
    cache_delete(f"dashboard:user:{user_id}")


# ── Rate Limiting ──
def cache_rate_limit(identifier: str, window_seconds: int = 60, max_requests: int = 60) -> bool:
    """
    Limiteur de debit simple.
    Retourne True si la requete est autorisee, False si bloquee.
    """
    if not _client:
        return True  # Pas de Redis = pas de limite
    key = _make_key(f"ratelimit:{identifier}")
    try:
        pipe = _client.pipeline()
        pipe.incr(key)
        pipe.expire(key, window_seconds)
        results = pipe.execute()
        return results[0] <= max_requests
    except (ConnectionError, TimeoutError):
        return True


# ══════════════════════════════════════════════════════════
#  DECORATEUR @cached
# ══════════════════════════════════════════════════════════

def cached(key_prefix: str, ttl: int = DEFAULT_TTL):
    """
    Decorateur pour mettre en cache le resultat d'une fonction.

    Usage:
        @cached("plans:all", ttl=600)
        def get_all_plans(db):
            return db.query(Plan).all()
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Construire la cle cache a partir des arguments
            cache_key = f"{key_prefix}:{hash(str(args) + str(sorted(kwargs.items())))}"
            # Tenter de lire depuis le cache
            result = cache_get(cache_key)
            if result is not None:
                return result
            # Executer la fonction et mettre en cache
            result = func(*args, **kwargs)
            if result is not None:
                cache_set(cache_key, result, ttl=ttl)
            return result
        return wrapper
    return decorator


# ══════════════════════════════════════════════════════════
#  METRIQUES ET INFORMATIONS
# ══════════════════════════════════════════════════════════

def get_cache_stats() -> dict:
    """Retourne les statistiques du cache."""
    info = {"available": is_available(), "stats": dict(_stats)}
    if _client and is_available():
        try:
            redis_info = _client.info(section="memory")
            info["memory"] = {
                "used_memory_human": redis_info.get("used_memory_human", "N/A"),
                "used_memory_peak_human": redis_info.get("used_memory_peak_human", "N/A"),
                "maxmemory_human": redis_info.get("maxmemory_human", "0B"),
            }
            redis_stats = _client.info(section="stats")
            info["redis_stats"] = {
                "connected_clients": _client.info("clients").get("connected_clients", 0),
                "total_commands_processed": redis_stats.get("total_commands_processed", 0),
                "keyspace_hits": redis_stats.get("keyspace_hits", 0),
                "keyspace_misses": redis_stats.get("keyspace_misses", 0),
                "evicted_keys": redis_stats.get("evicted_keys", 0),
            }
            # Nombre de cles EcoLearnAI
            keys_count = 0
            for k in _client.scan_iter(match=f"{KEY_PREFIX}*", count=500):
                keys_count += 1
            info["ecolearnai_keys"] = keys_count
        except Exception as e:
            info["error"] = str(e)
    return info


def flush_all_cache() -> bool:
    """Supprime toutes les cles EcoLearnAI du cache (pas flush global)."""
    if not _client:
        return False
    try:
        deleted = cache_delete_pattern("*")
        logger.info("Redis : %d cles EcoLearnAI supprimees", deleted)
        return True
    except Exception as e:
        logger.error("Redis flush erreur: %s", str(e))
        return False
