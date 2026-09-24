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


def ensure_schema_compatibility():
    """
    Ensures that extended profile and registration columns exist in the trainees table.
    Works for both SQLite and MySQL without breaking existing databases.
    """
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        if db_type == 'sqlite':
            cursor.execute("PRAGMA table_info(trainees)")
            existing = [row[1] for row in cursor.fetchall()]
            needed = [
                ('country', "VARCHAR(100) DEFAULT 'India'"),
                ('state', "VARCHAR(100) DEFAULT 'Maharashtra'"),
                ('city', "VARCHAR(100)"),
                ('highest_education', "VARCHAR(100)"),
                ('field_of_study', "VARCHAR(150)"),
                ('institution', "VARCHAR(200)"),
                ('graduation_year', "INTEGER"),
                ('identity_token', "VARCHAR(100)"),
                ('identity_verified', "INTEGER DEFAULT 0"),
                ('certificate_verified', "INTEGER DEFAULT 0"),
                ('certificate_verified_at', "TIMESTAMP"),
                ('communication_consent', "INTEGER DEFAULT 1")
            ]
            for col_name, col_type in needed:
                if col_name not in existing:
                    cursor.execute(f"ALTER TABLE trainees ADD COLUMN {col_name} {col_type}")
            conn.commit()
        else:
            for col_name, col_type in [
                ('country', "VARCHAR(100) DEFAULT 'India'"),
                ('state', "VARCHAR(100) DEFAULT 'Maharashtra'"),
                ('city', "VARCHAR(100)"),
                ('highest_education', "VARCHAR(100)"),
                ('field_of_study', "VARCHAR(150)"),
                ('institution', "VARCHAR(200)"),
                ('graduation_year', "INT"),
                ('identity_token', "VARCHAR(100)"),
                ('identity_verified', "TINYINT DEFAULT 0"),
                ('certificate_verified', "TINYINT DEFAULT 0"),
                ('certificate_verified_at', "TIMESTAMP NULL"),
                ('communication_consent', "TINYINT DEFAULT 1")
            ]:
                try:
                    cursor.execute(f"ALTER TABLE trainees ADD COLUMN {col_name} {col_type}")
                except Exception:
                    pass
        cursor.close()
        conn.close()
    except Exception as e:
        # Ignore if tables do not exist yet before init_db
        pass
