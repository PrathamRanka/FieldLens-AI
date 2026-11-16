import psycopg
from psycopg.rows import dict_row
from .config import settings

def connect():
    conn = psycopg.connect(settings.database_url, password=settings.db_password or None, row_factory=dict_row)
    from pgvector.psycopg import register_vector
    register_vector(conn)
    return conn

def init_db():
    # Install the pgvector extension before registering its adapter on normal connections.
    with psycopg.connect(settings.database_url, password=settings.db_password or None, row_factory=dict_row) as conn:
        with open("sql/init.sql", encoding="utf-8") as f:
            conn.execute(f.read())
