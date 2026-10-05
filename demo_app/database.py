from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from fastdoctor.database import DatabaseConfig


DATABASE_CONFIG = DatabaseConfig.from_env()
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=DATABASE_CONFIG.user,
    password=DATABASE_CONFIG.password,
    host=DATABASE_CONFIG.host,
    port=DATABASE_CONFIG.port,
    database=DATABASE_CONFIG.database,
)


engine = create_engine(
    DATABASE_URL,
    connect_args={"connect_timeout": DATABASE_CONFIG.connect_timeout},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
