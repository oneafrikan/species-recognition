"""Unit tests for config.py validation.

Covers cli-reporting spec's "Valid config" / "Missing required field"
scenarios (task 7.2).
"""

import pytest

from species_tag.config import Config, ConfigError, load_config

VALID_YAML = """
backend: ollama
ollama:
  host: http://localhost:11434
  active_model: llama3.2-vision
  models_to_test:
    - llama3.2-vision
    - llava
region_context: "Southern African safari wildlife"
min_confidence: medium
"""


def _write(tmp_path, text, name="config.yaml"):
    path = tmp_path / name
    path.write_text(text)
    return path


def test_valid_config_loads(tmp_path):
    path = _write(tmp_path, VALID_YAML)
    config = load_config(path)
    assert isinstance(config, Config)
    assert config.backend == "ollama"
    assert config.ollama.host == "http://localhost:11434"
    assert config.ollama.active_model == "llama3.2-vision"
    assert config.ollama.models_to_test == ["llama3.2-vision", "llava"]
    assert config.region_context == "Southern African safari wildlife"
    assert config.min_confidence == "medium"


def test_missing_file_errors_clearly():
    with pytest.raises(ConfigError):
        load_config("/nonexistent/config.yaml")


def test_not_yaml_mapping_errors(tmp_path):
    path = _write(tmp_path, "- just\n- a\n- list\n")
    with pytest.raises(ConfigError):
        load_config(path)


@pytest.mark.parametrize(
    "missing_field",
    ["backend", "ollama", "region_context", "min_confidence"],
)
def test_missing_top_level_required_field_errors(tmp_path, missing_field):
    data = {
        "backend": "ollama",
        "ollama": {
            "host": "http://localhost:11434",
            "active_model": "llama3.2-vision",
            "models_to_test": ["llama3.2-vision"],
        },
        "region_context": "test region",
        "min_confidence": "medium",
    }
    del data[missing_field]
    # Build minimal YAML by hand, including only the fields still in `data`.
    lines = []
    if "backend" in data:
        lines.append(f"backend: {data['backend']}")
    if "ollama" in data:
        lines.append("ollama:")
        lines.append(f"  host: {data['ollama']['host']}")
        lines.append(f"  active_model: {data['ollama']['active_model']}")
        lines.append("  models_to_test:")
        lines.append("    - llama3.2-vision")
    if "region_context" in data:
        lines.append(f"region_context: {data['region_context']}")
    if "min_confidence" in data:
        lines.append(f"min_confidence: {data['min_confidence']}")
    path = _write(tmp_path, "\n".join(lines))

    with pytest.raises(ConfigError, match=missing_field):
        load_config(path)


@pytest.mark.parametrize("missing_field", ["host", "active_model", "models_to_test"])
def test_missing_nested_ollama_field_errors(tmp_path, missing_field):
    ollama_fields = {
        "host": "http://localhost:11434",
        "active_model": "llama3.2-vision",
    }
    lines = ["backend: ollama", "ollama:"]
    if missing_field != "host":
        lines.append(f"  host: {ollama_fields['host']}")
    if missing_field != "active_model":
        lines.append(f"  active_model: {ollama_fields['active_model']}")
    if missing_field != "models_to_test":
        lines.append("  models_to_test:")
        lines.append("    - llama3.2-vision")
    lines.append('region_context: "test region"')
    lines.append("min_confidence: medium")
    path = _write(tmp_path, "\n".join(lines))

    with pytest.raises(ConfigError, match=f"ollama.{missing_field}"):
        load_config(path)


def test_invalid_min_confidence_errors(tmp_path):
    path = _write(
        tmp_path,
        VALID_YAML.replace("min_confidence: medium", "min_confidence: extreme"),
    )
    with pytest.raises(ConfigError, match="min_confidence"):
        load_config(path)
