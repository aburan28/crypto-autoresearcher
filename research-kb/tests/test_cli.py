import json
import stat

from typer.testing import CliRunner

from research_kb.cli import app


def test_documented_token_commands_never_print_secret(tmp_path):
    runner = CliRunner()
    secret_file = tmp_path / "client.token"
    result = runner.invoke(
        app,
        [
            "--home",
            str(tmp_path / "state"),
            "token",
            "create",
            "--client",
            "codex-cloud",
            "--output",
            str(secret_file),
        ],
    )
    assert result.exit_code == 0, result.output
    secret = secret_file.read_text().strip()
    assert len(secret) >= 40
    assert secret not in result.output
    assert stat.S_IMODE(secret_file.stat().st_mode) == 0o600
    auth = tmp_path / "state/auth.json"
    assert secret not in auth.read_text()
    assert "codex-cloud" in json.loads(auth.read_text())["tokens"]
    revoked = runner.invoke(
        app, ["--home", str(tmp_path / "state"), "token", "revoke", "--client", "codex-cloud"]
    )
    assert revoked.exit_code == 0
    assert "codex-cloud" not in json.loads(auth.read_text())["tokens"]
