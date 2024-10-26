from dataclasses import dataclass
from os import environ

from dotenv import load_dotenv
from sqlalchemy import URL

load_dotenv()


@dataclass
class DatabaseConfig:
    name: str | None = environ.get("DB_NAME")
    user: str | None = environ.get("DB_USER")
    password: str | None = environ.get("DB_PASS", None)
    port: int = int(environ.get("DB_PORT", 5432))
    host: str = environ.get("DB_HOST", "db")

    driver: str = "asyncpg"
    database_system: str = "postgresql"

    def __post_init__(self):
        required_vars = ["name", "user", "password", "port", "host"]

        for var in required_vars:
            value = getattr(self, var)
            if value is None:
                raise ValueError(f"Environment variable for {var} is not set")

    def build_connection_str(self, test_db: bool = False) -> str:
        return URL.create(
            drivername=f"{self.database_system}+{self.driver}",
            username=self.user,
            database=self.name,
            password=self.password,
            port=self.port if not test_db else 5433,
            host=self.host,
        ).render_as_string(hide_password=False)


@dataclass
class LoggerConfig:
    host: str = environ.get("ELASTICSEARCH_HOST")
    port: int = environ.get("ELASTICSEARCH_PORT")

    @property
    def url(self) -> str:
        return f'http://{self.host}:{self.port}'


@dataclass
class WidgetsServer:
    host: str = environ.get("WIDGETS_SERVER_HOST")
    port: str = environ.get("WIDGETS_SERVER_PORT")

    @property
    def url(self) -> str:
        return f'http://{self.host}:{self.port}'


@dataclass
class Widget:
    client_id: str = environ.get("CLIENT_ID")


@dataclass
class Configuration:
    developer_name = environ.get("DEVELOPER_NAME")
    debug = bool(environ.get("DEBUG"))
    db = DatabaseConfig()
    logger = LoggerConfig()
    widget = Widget()
    widgets_server = WidgetsServer()


conf = Configuration()
