"""Utilities to load pymrkt configuration."""

from pathlib import Path
from typing import Any, Dict

import yaml

CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"


def _load_config() -> Dict[str, Any]:
    """Return configuration dictionary from ``config.yaml``."""
    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except FileNotFoundError:
        return {}


def get_lock_minutes() -> int:
    """Return the ``lock_minutes`` setting from the configuration file."""
    cfg = _load_config()
    return int(cfg.get("lock_minutes", 15))



def get_server_host() -> str:
    """Return the API server host from the configuration file."""
    cfg = _load_config()
    server = cfg.get("server", {})
    return str(server.get("host", "127.0.0.1"))


def get_server_port() -> int:
    """Return the API server port from the configuration file."""
    cfg = _load_config()
    server = cfg.get("server", {})
    return int(server.get("port", 8000))


__all__ = [
    "get_lock_minutes",
    "get_server_host",
    "get_server_port",
]

