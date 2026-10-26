"""Test für get_bearer_token: PAT hat Vorrang, sonst CLI-OAuth."""

import json
from unittest.mock import patch

from src.core import config


def test_pat_wins_when_set():
    with patch.object(config.settings, "DATABRICKS_TOKEN", "dapi_test"):
        assert config.get_bearer_token() == "dapi_test"
        assert config.get_api_headers()["Authorization"] == "Bearer dapi_test"


def test_falls_back_to_cli_oauth_when_pat_empty():
    completed = type("R", (), {"returncode": 0, "stdout": json.dumps({"access_token": "oauth_tok"}), "stderr": ""})
    with patch.object(config.settings, "DATABRICKS_TOKEN", ""):
        with patch.object(config.subprocess, "run", return_value=completed) as run:
            assert config.get_bearer_token() == "oauth_tok"
        assert "--profile" in run.call_args[0][0]


def test_raises_with_hint_when_cli_fails():
    completed = type("R", (), {"returncode": 1, "stdout": "", "stderr": "not logged in"})
    with patch.object(config.settings, "DATABRICKS_TOKEN", ""):
        with patch.object(config.subprocess, "run", return_value=completed):
            try:
                config.get_bearer_token()
            except RuntimeError as e:
                assert "databricks auth login" in str(e)
            else:
                raise AssertionError("expected RuntimeError")


if __name__ == "__main__":
    test_pat_wins_when_set()
    test_falls_back_to_cli_oauth_when_pat_empty()
    test_raises_with_hint_when_cli_fails()
    print("ok")
