from pathlib import Path

from typer.testing import CliRunner

from cv_builder.cli import app

runner = CliRunner()


def test_analyse_command(tmp_path: Path) -> None:
    job = tmp_path / "job.txt"
    job.write_text("Senior Engineer — Acme\nBuild Python services.", encoding="utf-8")
    result = runner.invoke(app, ["analyse", "--job", str(job)])
    assert result.exit_code == 0
    assert '"company": "Acme"' in result.stdout


def test_analyse_requires_one_source() -> None:
    result = runner.invoke(app, ["analyse"])
    assert result.exit_code == 1
    assert "exactly one" in result.output
