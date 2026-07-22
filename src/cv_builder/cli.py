"""Command-line interface."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Annotated

import typer

from cv_builder.io import load_yaml, write_json
from cv_builder.job import analyse_job, load_job
from cv_builder.models import MasterCV, TailoredCV, TailoringRules
from cv_builder.render import render as render_cv
from cv_builder.service import build as build_cv
from cv_builder.tailor import change_report, compare
from cv_builder.validation import require_valid, validate_claims

app = typer.Typer(help="Build factual, job-specific CVs locally.", no_args_is_help=True)
ROOT = Path.cwd()
MASTER = ROOT / "data/master-cv.yaml"
RULES = ROOT / "config/tailoring-rules.yaml"
TEMPLATE = ROOT / "templates/senior-engineer.typ"


def _input(job: Path | None, html: Path | None, url: str | None, stdin: bool) -> str:
    stdin_text = sys.stdin.read() if stdin else None
    return load_job(text_path=job, html_path=html, url=url, stdin_text=stdin_text)


@app.command()
def build(
    job: Annotated[Path | None, typer.Option("--job", help="Plain-text job description.")] = None,
    html: Annotated[Path | None, typer.Option("--html", help="HTML job description.")] = None,
    url: Annotated[str | None, typer.Option("--url", help="Job advert URL.")] = None,
    stdin: Annotated[
        bool, typer.Option("--stdin", help="Read job text from standard input.")
    ] = False,
    master: Annotated[Path, typer.Option(help="Master CV YAML.")] = MASTER,
    output: Annotated[Path, typer.Option(help="Output root.")] = ROOT / "output",
) -> None:
    """Analyse a job, tailor and validate the CV, then produce reports and PDF."""
    try:
        spec = analyse_job(_input(job, html, url, stdin))
        destination = build_cv(master, RULES, TEMPLATE, output, spec)
    except (OSError, ValueError, RuntimeError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"Built {destination}")


@app.command()
def analyse(
    job: Annotated[Path | None, typer.Option("--job")] = None,
    html: Annotated[Path | None, typer.Option("--html")] = None,
    url: Annotated[str | None, typer.Option("--url")] = None,
    stdin: Annotated[bool, typer.Option("--stdin")] = False,
    output: Annotated[Path | None, typer.Option(help="Optional JSON output path.")] = None,
) -> None:
    """Normalise a job advert into a JobSpec."""
    try:
        spec = analyse_job(_input(job, html, url, stdin))
    except (OSError, ValueError, RuntimeError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    if output:
        write_json(output, spec)
    typer.echo(json.dumps(spec.model_dump(mode="json"), indent=2, ensure_ascii=False))


@app.command("validate")
def validate_command(
    tailored: Annotated[Path, typer.Argument(help="Tailored CV YAML.")],
    master: Annotated[Path, typer.Option(help="Master CV YAML.")] = MASTER,
) -> None:
    """Check every tailored claim against the master CV."""
    errors = validate_claims(
        load_yaml(master, MasterCV),
        load_yaml(tailored, TailoredCV),
        load_yaml(RULES, TailoringRules),
    )
    if errors:
        typer.echo("\n".join(f"ERROR: {error}" for error in errors), err=True)
        raise typer.Exit(1)
    typer.echo("Validation passed")


@app.command()
def render(
    tailored: Annotated[Path, typer.Argument(help="Tailored CV YAML.")],
    master: Annotated[Path, typer.Option(help="Master CV YAML.")] = MASTER,
    output: Annotated[Path | None, typer.Option(help="Output directory.")] = None,
) -> None:
    """Validate and render tailored YAML with Typst."""
    cv = load_yaml(tailored, TailoredCV)
    source = load_yaml(master, MasterCV)
    rules = load_yaml(RULES, TailoringRules)
    try:
        require_valid(source, cv, rules)
        _, pdf = render_cv(cv, output or tailored.parent, TEMPLATE)
    except (OSError, ValueError, RuntimeError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"Rendered {pdf}")


@app.command("diff")
def diff_command(
    tailored: Annotated[Path, typer.Argument(help="Tailored CV YAML.")],
    master: Annotated[Path, typer.Option(help="Master CV YAML.")] = MASTER,
) -> None:
    """Describe differences from the master CV."""
    typer.echo(change_report(compare(load_yaml(master, MasterCV), load_yaml(tailored, TailoredCV))))


@app.command()
def check() -> None:
    """Check project data, configuration and local tools."""
    failures: list[str] = []
    for path, model in ((MASTER, MasterCV), (RULES, TailoringRules)):
        try:
            load_yaml(path, model)
            typer.echo(f"OK    {path}")
        except (OSError, ValueError) as exc:
            failures.append(f"FAIL  {path}: {exc}")
    if TEMPLATE.exists():
        typer.echo(f"OK    {TEMPLATE}")
    else:
        failures.append(f"FAIL  missing {TEMPLATE}")
    if shutil.which("typst"):
        typer.echo("OK    Typst")
    else:
        failures.append("FAIL  Typst executable not found")
    if failures:
        typer.echo("\n".join(failures), err=True)
        raise typer.Exit(1)
    typer.echo("All checks passed")


if __name__ == "__main__":
    app()
