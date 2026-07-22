"""Typst source generation and PDF compilation."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from cv_builder.models import TailoredCV


class RenderError(RuntimeError):
    """Raised when Typst rendering cannot complete."""


def escape(value: str) -> str:
    replacements = {
        "\\": "\\\\",
        "#": "\\#",
        "[": "\\[",
        "]": "\\]",
        "$": "\\$",
        "*": "\\*",
        "_": "\\_",
        "@": "\\@",
    }
    return "".join(replacements.get(char, char) for char in value)


def _heading(title: str) -> str:
    return f"== {escape(title)}"


def _bullets(values: list[str]) -> str:
    return "\n".join(f"- {escape(value)}" for value in values)


def _header(cv: TailoredCV) -> str:
    personal = cv.personal
    contacts = [personal.email]
    contacts.extend(value for value in (personal.phone, personal.location) if value)
    contacts.extend(link.url for link in personal.links)
    return (
        f'#align(center)[\n#set text(size: 20pt, weight: "bold")\n{escape(personal.name)}\n'
        f'#v(2pt)\n#set text(size: 8.5pt, weight: "regular")\n{escape("  •  ".join(contacts))}\n]\n'
        f"#v(5pt)\n{escape(cv.profile)}\n"
    )


def generate_typst(cv: TailoredCV, template_path: Path) -> str:
    experience_parts = [_heading("Experience")]
    for item in cv.experience:
        location = f" · {item.location}" if item.location else ""
        meta = f"{item.start_date}–{item.end_date}{location}"
        title = f"{item.role} — {item.employer}"
        bullets = _bullets([bullet.text for bullet in item.bullets])
        experience_parts.append(f'#entry("{escape(title)}", "{escape(meta)}")[\n{bullets}\n]')
    page_two: list[str] = []
    if cv.skills:
        page_two.extend((_heading("Technical skills"), escape(" • ".join(cv.skills))))
    if cv.projects:
        page_two.append(_heading("Projects"))
        for project in cv.projects:
            content = escape(project.description)
            if project.bullets:
                content += "\n" + _bullets([b.text for b in project.bullets])
            page_two.append(f'#entry("{escape(project.name)}", "")[\n{content}\n]')
    if cv.education:
        page_two.append(_heading("Education"))
        for education in cv.education:
            title = f"{education.qualification} — {education.institution}"
            dates = escape(education.start_date + "–" + education.end_date)
            page_two.append(f'#entry("{escape(title)}", "{dates}")[]')
    if cv.achievements:
        page_two.extend(
            (_heading("Achievements"), _bullets([item.text for item in cv.achievements]))
        )
    template = template_path.read_text(encoding="utf-8")
    return (
        template.replace("%%HEADER%%", _header(cv))
        .replace("%%PAGE_ONE%%", "\n".join(experience_parts))
        .replace("%%PAGE_TWO%%", "\n".join(page_two))
    )


def compile_pdf(typ_path: Path, pdf_path: Path) -> None:
    executable = shutil.which("typst")
    if executable is None:
        raise RenderError(
            "Typst is not installed. Install it from the Typst documentation "
            "or your package manager."
        )
    result = subprocess.run(
        [executable, "compile", str(typ_path), str(pdf_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RenderError(f"Typst compilation failed:\n{result.stderr.strip()}")


def render(
    cv: TailoredCV, output_dir: Path, template_path: Path, *, compile_output: bool = True
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    typ_path = output_dir / "cv.typ"
    pdf_path = output_dir / "cv.pdf"
    typ_path.write_text(generate_typst(cv, template_path), encoding="utf-8")
    if compile_output:
        compile_pdf(typ_path, pdf_path)
    return typ_path, pdf_path
