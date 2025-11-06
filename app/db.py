import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

connect_args = {}
engine = None

if DATABASE_URL.startswith("sqlitecloud://"):
    # Usar el driver sqlitecloud vía creator y envolver la conexión para compatibilidad
    try:
        import sqlitecloud  # type: ignore
    except ImportError as e:
        raise RuntimeError("Falta el paquete 'sqlitecloud'. Instálalo con: pip install sqlitecloud") from e

    class SQLiteCloudCompatConnection:
        def __init__(self, conn):
            self._conn = conn

        # SQLAlchemy intenta registrar funciones con 'deterministic' (pysqlite);
        # el driver sqlitecloud puede no soportar ese kw. Ignoramos kwargs.
        def create_function(self, name, num_params, func, *args, **kwargs):
            try:
                return self._conn.create_function(name, num_params, func)
            except Exception:
                return None

        def cursor(self, *args, **kwargs):
            return self._conn.cursor(*args, **kwargs)

        def commit(self):
            return self._conn.commit()

        def rollback(self):
            return self._conn.rollback()

        def close(self):
            return self._conn.close()

        def __getattr__(self, name):
            return getattr(self._conn, name)

    engine = create_engine(
        "sqlite://",  # Dialecto sqlite, conexión provista por creator
        echo=False,
        future=True,
        creator=lambda: SQLiteCloudCompatConnection(sqlitecloud.connect(DATABASE_URL)),
    )
else:
    if DATABASE_URL.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)

# Asegurar FKs en SQLite/SQLiteCloud
if engine.dialect.name == "sqlite":
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        except Exception:
            pass

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)