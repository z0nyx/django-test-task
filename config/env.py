import os
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


TRUE_VALUES = {"1", "true", "yes", "on"}
POSTGRES_SCHEMES = {"postgres", "postgresql"}


def load_environment_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        normalized_key = key.strip()
        normalized_value = value.strip()

        if normalized_value and normalized_value[0] in {"'", '"'} and normalized_value.endswith(normalized_value[0]):
            normalized_value = normalized_value[1:-1]

        os.environ.setdefault(normalized_key, normalized_value)


def environment(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def boolean_env(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in TRUE_VALUES


def integer_env(name: str, default: int = 0) -> int:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    return int(value)


def csv_env(name: str, default: str = "") -> list[str]:
    value = os.environ.get(name, default)
    return [part.strip() for part in value.split(",") if part.strip()]


def database_config(base_dir: Path) -> dict:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": base_dir / "db.sqlite3",
        }

    parsed_url = urlparse(database_url)

    if parsed_url.scheme in POSTGRES_SCHEMES:
        config = {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": unquote(parsed_url.path.lstrip("/")),
            "USER": unquote(parsed_url.username or ""),
            "PASSWORD": unquote(parsed_url.password or ""),
            "HOST": parsed_url.hostname or "",
            "PORT": parsed_url.port or "",
        }

        query = parse_qs(parsed_url.query)
        ssl_mode = query.get("sslmode", [""])[0]
        if ssl_mode:
            config["OPTIONS"] = {"sslmode": ssl_mode}

        return config

    if parsed_url.scheme == "sqlite":
        raw_path = unquote(parsed_url.path)
        if not raw_path:
            database_name = base_dir / "db.sqlite3"
        elif raw_path.startswith("//"):
            database_name = Path(raw_path[1:])
        elif raw_path.startswith("/"):
            database_name = base_dir / raw_path.lstrip("/")
        else:
            database_name = base_dir / raw_path

        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": database_name,
        }

    raise ValueError("Unsupported DATABASE_URL scheme")
