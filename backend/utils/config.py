import os
from pathlib import Path
from typing import Any

import yaml


class Config:
    _instance = None
    _configs: dict[str, dict[str, Any]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_all()
        return cls._instance

    def _load_all(self) -> None:
        config_dir = Path(__file__).parent.parent.parent / "config"
        for yaml_file in config_dir.glob("*.yaml"):
            name = yaml_file.stem
            with open(yaml_file, "r") as f:
                self._configs[name] = yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        section, _, field = key.partition(".")
        if section not in self._configs:
            return default
        value = self._configs[section]
        for part in field.split(".") if field else []:
            if isinstance(value, dict):
                value = value.get(part, default)
            else:
                return default
        return value if value is not None else default

    def get_section(self, section: str) -> dict[str, Any]:
        return self._configs.get(section, {})

    def get_nested(self, section: str, *keys: str, default: Any = None) -> Any:
        value = self._configs.get(section, {})
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value if value is not None else default


config = Config()
