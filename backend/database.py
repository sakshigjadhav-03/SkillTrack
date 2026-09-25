import os
import sqlite3
from pathlib import Path
from backend.config import Config

try:
    import pymysql
    import pymysql.cursors
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False


def get_db_connection():
    """
    Returns a database connection based on Config.
    If MySQL is requested but unavailable, falls back gracefully to SQLite.
    """
    if not Config.USE_SQLITE and PYMYSQL_AVAILABLE:
        try:
            connection = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            return connection, 'mysql'
        except Exception as e:
            print(f"[SkillTrack DB Warning] Could not connect to MySQL ({e}). Falling back to SQLite.")

    # SQLite connection
    db_path = Path(Config.SQLITE_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn, 'sqlite'


_schema_ensured = False

def ensure_schema():
    """Ensures required columns exist in tables without breaking existing data."""
    global _schema_ensured
    if _schema_ensured:
        return
    try:
        conn, db_type = get_db_connection()
        if db_type == 'sqlite':
            cur = conn.cursor()
            
            # Check training_providers columns
            tp_info = cur.execute("PRAGMA table_info(training_providers)").fetchall()
            tp_cols = [c[1] for c in tp_info]
            if tp_cols:
                if 'authorized_person' not in tp_cols:
                    cur.execute("ALTER TABLE training_providers ADD COLUMN authorized_person VARCHAR(150)")
                if 'address' not in tp_cols:
                    cur.execute("ALTER TABLE training_providers ADD COLUMN address TEXT")
                if 'state' not in tp_cols:
                    cur.execute("ALTER TABLE training_providers ADD COLUMN state VARCHAR(100) DEFAULT 'Maharashtra'")
                if 'verification_status' not in tp_cols:
                    cur.execute("ALTER TABLE training_providers ADD COLUMN verification_status VARCHAR(20) DEFAULT 'verified'")

                cur.execute("UPDATE training_providers SET verification_status = 'verified' WHERE verification_status IS NULL")
                cur.execute("UPDATE training_providers SET state = 'Maharashtra' WHERE state IS NULL")
                cur.execute("UPDATE training_providers SET authorized_person = 'Center Director' WHERE authorized_person IS NULL")

            # Check employers columns
            emp_info = cur.execute("PRAGMA table_info(employers)").fetchall()
            emp_cols = [c[1] for c in emp_info]
            if emp_cols:
                if 'address' not in emp_cols:
                    cur.execute("ALTER TABLE employers ADD COLUMN address TEXT")
                if 'state' not in emp_cols:
                    cur.execute("ALTER TABLE employers ADD COLUMN state VARCHAR(100) DEFAULT 'Maharashtra'")
                if 'registration_id' not in emp_cols:
                    cur.execute("ALTER TABLE employers ADD COLUMN registration_id VARCHAR(100)")
                if 'verification_status' not in emp_cols:
                    cur.execute("ALTER TABLE employers ADD COLUMN verification_status VARCHAR(20) DEFAULT 'verified'")

                cur.execute("UPDATE employers SET verification_status = 'verified' WHERE verification_status IS NULL")
                cur.execute("UPDATE employers SET state = 'Maharashtra' WHERE state IS NULL")
                cur.execute("UPDATE employers SET registration_id = 'GST-27AAACT1234F' WHERE registration_id IS NULL")

            conn.commit()
            cur.close()
        conn.close()
        _schema_ensured = True
    except Exception as e:
        print(f"[SkillTrack DB Warning] ensure_schema error: {e}")


def _normalize_query(query: str, db_type: str) -> str:
    """
    Normalizes SQL queries between MySQL (%s parameter placeholder)
    and SQLite (? parameter placeholder).
    """
    if db_type == 'sqlite':
        return query.replace('%s', '?')
    elif db_type == 'mysql':
        return query.replace('?', '%s')
    return query


def query_db(query, args=(), one=False):
    """
    Executes a SELECT query and returns results as dict or list of dicts.
    """
    conn, db_type = get_db_connection()
    normalized_query = _normalize_query(query, db_type)
    try:
        cursor = conn.cursor()
        cursor.execute(normalized_query, args)
        if db_type == 'sqlite':
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
        else:
            result = cursor.fetchall()
        cursor.close()
        return (result[0] if result else None) if one else result
    finally:
        conn.close()


def execute_db(query, args=()):
    """
    Executes an INSERT, UPDATE, or DELETE query.
    Returns a dict with 'lastrowid' and 'rowcount'.
    """
    conn, db_type = get_db_connection()
    normalized_query = _normalize_query(query, db_type)
    try:
        cursor = conn.cursor()
        cursor.execute(normalized_query, args)
        if db_type == 'sqlite':
            conn.commit()
        lastrowid = cursor.lastrowid
        rowcount = cursor.rowcount
        cursor.close()
        return {'lastrowid': lastrowid, 'rowcount': rowcount}
    finally:
        conn.close()


def execute_script(sql_script: str):
    """
    Executes multiple SQL statements from a script.
    """
    conn, db_type = get_db_connection()
    try:
        if db_type == 'sqlite':
            # Adapt MySQL-specific syntax if present
            adapted_script = (
                sql_script
                .replace("AUTO_INCREMENT", "AUTOINCREMENT")
                .replace("ENGINE=InnoDB DEFAULT CHARSET=utf8mb4", "")
                .replace("INT AUTOINCREMENT", "INTEGER PRIMARY KEY AUTOINCREMENT")
                .replace("BIGINT AUTOINCREMENT", "INTEGER PRIMARY KEY AUTOINCREMENT")
            )
            conn.executescript(adapted_script)
            conn.commit()
        else:
            with conn.cursor() as cursor:
                for statement in sql_script.split(';'):
                    stmt = statement.strip()
                    if stmt:
                        cursor.execute(stmt)
            conn.commit()
    finally:
        conn.close()
