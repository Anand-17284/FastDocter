import os
from dataclasses import dataclass, field


DEFAULT_HOST = "localhost"
DEFAULT_PORT = 5432
DEFAULT_DATABASE = "fastdoctor"
DEFAULT_USER = "postgres"
DEFAULT_CONNECT_TIMEOUT = 5
MAX_CONNECT_TIMEOUT = 30


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    database: str
    user: str
    password: str | None = field(repr=False)
    schema: str | None
    connect_timeout: int

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        try:
            port = int(os.getenv("PGPORT", str(DEFAULT_PORT)))
            requested_timeout = int(
                os.getenv("PGCONNECT_TIMEOUT", str(DEFAULT_CONNECT_TIMEOUT))
            )
        except ValueError:
            raise ValueError(
                "PGPORT and PGCONNECT_TIMEOUT must be integers"
            ) from None

        if port < 1 or port > 65535:
            raise ValueError("PGPORT must be between 1 and 65535")
        if requested_timeout < 1:
            raise ValueError("PGCONNECT_TIMEOUT must be at least 1 second")

        return cls(
            host=os.getenv("PGHOST", DEFAULT_HOST),
            port=port,
            database=os.getenv("PGDATABASE", DEFAULT_DATABASE),
            user=os.getenv("PGUSER", DEFAULT_USER),
            password=os.getenv("PGPASSWORD"),
            schema=os.getenv("PGSCHEMA"),
            connect_timeout=min(requested_timeout, MAX_CONNECT_TIMEOUT),
        )

    def psycopg_kwargs(self) -> dict[str, str | int | None]:
        return {
            "host": self.host,
            "port": self.port,
            "dbname": self.database,
            "user": self.user,
            "password": self.password,
            "connect_timeout": self.connect_timeout,
        }
