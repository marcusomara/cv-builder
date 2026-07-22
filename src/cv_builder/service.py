"""Application-level build orchestration."""

from __future__ import annotations

import re
from pathlib import Path

from cv_builder.io import load_yaml, write_json, write_yaml
from cv_builder.models import JobSpec, MasterCV, TailoringRules
from cv_builder.render import render
from cv_builder.tailor import ats_report, change_report, compare, tailor
from cv_builder.validation import require_valid


def slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return result or "unknown"


def build(
    master_path: Path,
    rules_path: Path,
    template_path: Path,
    output_root: Path,
    job: JobSpec,
    *,
    compile_output: bool = True,
) -> Path:
    master = load_yaml(master_path, MasterCV)
    rules = load_yaml(rules_path, TailoringRules)
    tailored = tailor(master, job, rules)
    require_valid(master, tailored, rules)
    destination = output_root / f"{slug(job.company)}-{slug(job.title)}"
    destination.mkdir(parents=True, exist_ok=True)
    write_yaml(destination / "tailored-cv.yaml", tailored)
    write_json(destination / "job-analysis.json", job)
    (destination / "change-report.md").write_text(
        change_report(compare(master, tailored, job)), encoding="utf-8"
    )
    (destination / "ats-report.md").write_text(ats_report(master, tailored, job), encoding="utf-8")
    render(tailored, destination, template_path, compile_output=compile_output)
    return destination
