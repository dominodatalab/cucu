"""
Database connection management for cucu.
"""

import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import duckdb

from cucu import logger
from cucu.config import CONFIG



# Global connection pool for database access
_connection_pool = None
_connection_pool_lock = threading.Lock()
_local_connections = threading.local()


def init_database() -> str:
    """
    Initialize the database if it's enabled.

    Returns:
        The path to the database file, or None if database is disabled
    """

    # Ensure results directory exists
    os.makedirs(results_dir, exist_ok=True)

    # Set the database file path
    db_file = os.path.join(results_dir, "results.db")
    CONFIG["DATABASE_FILE"] = db_file

    logger.info(f"Initializing database at {db_file}")

    # Create the database file if it doesn't exist
    conn = duckdb.connect(db_file)
    conn.close()

    # Initialize the connection pool
    get_connection_pool()

    return db_file


def close_database() -> None:
    """
    Close all database connections and clean up resources.
    """
    global _connection_pool

    if _connection_pool is None:
        return

    with _connection_pool_lock:
        if _connection_pool is not None:
            logger.debug("Shutting down database connection pool")
            _connection_pool.shutdown(wait=True)
            _connection_pool = None


def get_connection_pool() -> ThreadPoolExecutor:
    """
    Get or create the database connection pool.

    Returns:
        A ThreadPoolExecutor for database operations
    """
    global _connection_pool

    if not CONFIG["DATABASE_ENABLED"]:
        return None

    if _connection_pool is None:
        with _connection_pool_lock:
            if _connection_pool is None:
                # Create a new connection pool with a reasonable number of workers
                max_workers = min(32, (os.cpu_count() or 4) * 4)
                _connection_pool = ThreadPoolExecutor(
                    max_workers=max_workers,
                    thread_name_prefix="db-worker",
                )
                logger.debug(
                    f"Created database connection pool with {max_workers} workers"
                )

    return _connection_pool


def get_connection(
    timeout: Optional[float] = None,
) -> duckdb.DuckDBPyConnection:
    """
    Get a database connection from the pool.

    Args:
        timeout: Timeout in seconds, or None to use the default

    Returns:
        A DuckDB connection
    """
    if not CONFIG["DATABASE_ENABLED"] or CONFIG["DATABASE_FILE"] is None:
        return None

    # Use thread-local connections to avoid concurrent access issues
    if not hasattr(_local_connections, "conn"):
        db_file = CONFIG["DATABASE_FILE"]
        retry_count = CONFIG["DATABASE_RETRY_COUNT"]
        timeout = timeout or CONFIG["DATABASE_CONNECTION_TIMEOUT"]

        for attempt in range(retry_count):
            try:
                logger.debug(f"Opening database connection to {db_file}")
                conn = duckdb.connect(db_file)
                _local_connections.conn = conn
                break
            except Exception as e:
                logger.warning(
                    f"Failed to connect to database (attempt {attempt+1}/{retry_count}): {str(e)}"
                )
                if attempt == retry_count - 1:
                    raise
                time.sleep(0.5)

    return _local_connections.conn
