"""Loads and validates config.yaml.

See config.example.yaml for the schema and openspec/changes/species-tagging-cli-v1/design.md
for the reasoning behind it. Config is the only thing that changes between
machines/deployments (host, model, region, threshold) — everything else is code.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Union

import yaml

# Required fields, per cli-reporting spec's "Missing required field" scenario.
_REQUIRED_TOP_LEVEL = ["backend", "ollama", "region_context", "min_confidence"]
_REQUIRED_OLLAMA = ["host", "active_model", "models_to_test"]
_VALID_CONFIDENCE_LEVELS = ("low", "medium", "high")
# Safe default if a config omits num_ctx — matches what testing showed fixes the
# default-2048 context-truncation bug without assuming headroom a smaller machine
# (e.g. the 3060 box) may not have. Machines with more RAM/VRAM can raise it.
_DEFAULT_NUM_CTX = 8192


class ConfigError(Exception):
    """Raised for a missing, invalid, or unreadable config.yaml.

    Callers should catch this, print the message, and exit non-zero rather than crash.
    """


@dataclass
class OllamaConfig:
    host: str
    active_model: str
    models_to_test: list
    num_ctx: int = _DEFAULT_NUM_CTX


@dataclass
class Config:
    backend: str
    ollama: OllamaConfig
    region_context: str
    min_confidence: str


def load_config(path: Union[str, Path]) -> Config:
    """Load and validate config.yaml at `path`.

    Raises ConfigError with a clear message if the file is missing/unreadable,
    isn't valid YAML, or is missing a required field.
    """
    config_path = Path(path)
    try:
        raw_text = config_path.read_text()
    except OSError as exc:
        raise ConfigError(f"could not read config file '{path}': {exc}") from exc

    try:
        data = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise ConfigError(f"config file '{path}' is not valid YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError(f"config file '{path}' must be a YAML mapping")

    for field_name in _REQUIRED_TOP_LEVEL:
        if not data.get(field_name):
            raise ConfigError(f"config is missing required field: '{field_name}'")

    ollama_data = data["ollama"]
    if not isinstance(ollama_data, dict):
        raise ConfigError("config field 'ollama' must be a mapping")
    for field_name in _REQUIRED_OLLAMA:
        if not ollama_data.get(field_name):
            raise ConfigError(f"config is missing required field: 'ollama.{field_name}'")

    if data["min_confidence"] not in _VALID_CONFIDENCE_LEVELS:
        raise ConfigError(
            "config field 'min_confidence' must be one of "
            f"{_VALID_CONFIDENCE_LEVELS}, got: {data['min_confidence']!r}"
        )

    num_ctx = ollama_data.get("num_ctx", _DEFAULT_NUM_CTX)
    if not isinstance(num_ctx, int) or isinstance(num_ctx, bool) or num_ctx <= 0:
        raise ConfigError(f"config field 'ollama.num_ctx' must be a positive integer, got: {num_ctx!r}")

    return Config(
        backend=data["backend"],
        ollama=OllamaConfig(
            host=ollama_data["host"],
            active_model=ollama_data["active_model"],
            models_to_test=ollama_data["models_to_test"],
            num_ctx=num_ctx,
        ),
        region_context=data["region_context"],
        min_confidence=data["min_confidence"],
    )
