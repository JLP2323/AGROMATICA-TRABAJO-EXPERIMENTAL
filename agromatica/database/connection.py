"""
database/connection.py
----------------------
Context Manager seguro para conexiones PostgreSQL.
- Gestión automática de rollback ante excepciones.
- Pool de conexiones via SQLAlchemy Engine.
- Cursor como context manager, garantizando cierre limpio.
"""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator, Optional

import psycopg2
import psycopg2.extras
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.pool import QueuePool

from agromatica.config import get_settings

logger = logging.getLogger(__name__)

_engine: Optional[Engine] = None


def _get_engine() -> Engine:
    """
    Retorna (o crea) el engine SQLAlchemy singleton con pool de conexiones.
    Se reutiliza a lo largo del ciclo de vida de la aplicación.
    """
    global _engine
    if _engine is None:
        cfg = get_settings().db
        _engine = create_engine(
            cfg.sqlalchemy_url,
            poolclass=QueuePool,
            pool_size=cfg.pool_size,
            max_overflow=cfg.pool_max_overflow,
            pool_timeout=cfg.pool_timeout,
            pool_recycle=cfg.pool_recycle,
            pool_pre_ping=True,          # verifica conexiones muertas
            echo=False,
        )
        logger.info("SQLAlchemy Engine inicializado. Pool size=%d", cfg.pool_size)
    return _engine


def dispose_engine() -> None:
    """Cierra todas las conexiones del pool (útil en tests o apagado limpio)."""
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
        logger.info("Engine SQLAlchemy eliminado del pool.")


@contextmanager
def get_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """
    Context manager que provee una conexión psycopg2 con manejo completo
    de transacciones y rollback automático en caso de error.

    Uso:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT ...")
                rows = cur.fetchall()
    """
    cfg = get_settings().db
    conn: Optional[psycopg2.extensions.connection] = None
    try:
        conn = psycopg2.connect(
            host=cfg.host,
            port=cfg.port,
            dbname=cfg.name,
            user=cfg.user,
            password=cfg.password,
            connect_timeout=10,
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
        logger.debug("Conexión psycopg2 abierta.")
        yield conn
        conn.commit()
        logger.debug("Transacción confirmada (commit).")
    except psycopg2.Error as exc:
        if conn and not conn.closed:
            conn.rollback()
            logger.warning("Rollback ejecutado: %s", exc)
        raise
    finally:
        if conn and not conn.closed:
            conn.close()
            logger.debug("Conexión psycopg2 cerrada.")


def check_connection() -> tuple[bool, str]:
    """
    Verifica la conectividad a la base de datos.

    Returns:
        Tupla (éxito: bool, mensaje: str) con el estado de la conexión.
    """
    try:
        engine = _get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
        return True, f"✅ Conectado · {version}"
    except Exception as exc:  # noqa: BLE001
        msg = f"❌ Sin conexión: {exc}"
        logger.error(msg)
        return False, msg


def get_sqlalchemy_engine() -> Engine:
    """Expone el engine para uso con pandas.read_sql()."""
    return _get_engine()
