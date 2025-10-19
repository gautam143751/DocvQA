from __future__ import annotations

import yaml
from docvqa.config.loader import load_config


def test_load_config_with_env_override(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    with config_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(
            {
                "dataset": {"path": "assets/samples"},
                "extractor": {
                    "provider": "llm",
                    "llm": {
                        "api_base": "https://example.com/v1/chat/completions",
                        "api_key": "test-key",
                        "model": "gpt-test",
                    },
                },
                "storage": {"provider": "local_json"},
            },
            handle,
        )

    monkeypatch.setenv("DOCVQA_DATASET_LIMIT", "5")

    app_config = load_config(config_path)
    assert app_config.dataset.limit == 5
    assert app_config.dataset.path.name == "samples"
    assert app_config.extractor.provider.value == "llm"
