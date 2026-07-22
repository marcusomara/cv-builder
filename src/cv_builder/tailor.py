"""Evidence-preserving CV tailoring and reports."""

from __future__ import annotations

import re
from dataclasses import dataclass

from cv_builder.models import (
    JobSpec,
    MasterCV,
    TailoredBullet,
    TailoredCV,
    TailoredExperience,
    TailoredProject,
    TailoringRules,
)


def _terms(job: JobSpec) -> set[str]:
    values = job.required_skills + job.desirable_skills + job.keywords
    return {
        word.casefold()
        for value in values
        for word in re.findall(r"[\w+#./-]+", value)
        if len(word) > 2
    }


def _score(text: str, terms: set[str]) -> int:
    lower = text.casefold()
    return sum(3 if " " in term else 1 for term in terms if term in lower)


def tailor(master: MasterCV, job: JobSpec, rules: TailoringRules) -> TailoredCV:
    terms = _terms(job)
    experiences: list[TailoredExperience] = []
    for item in master.experience:
        ranked = sorted(
            enumerate(item.bullets), key=lambda pair: (-_score(pair[1].text, terms), pair[0])
        )
        chosen = [bullet for _, bullet in ranked[: rules.maximum_bullets_per_experience]]
        experiences.append(
            TailoredExperience(
                id=item.id,
                employer=item.employer,
                role=item.role,
                start_date=item.start_date,
                end_date=item.end_date,
                location=item.location,
                bullets=[TailoredBullet(text=b.text, source_id=b.id) for b in chosen],
            )
        )
    projects = [
        TailoredProject(
            id=project.id,
            name=project.name,
            description=project.description,
            bullets=[TailoredBullet(text=b.text, source_id=b.id) for b in project.bullets],
        )
        for project in master.projects
    ]
    skills = sorted(
        master.skills, key=lambda skill: (-_score(skill, terms), master.skills.index(skill))
    )
    return TailoredCV(
        personal=master.personal,
        profile=master.profile,
        experience=experiences,
        projects=projects,
        education=master.education,
        skills=skills,
        achievements=master.achievements,
    )


@dataclass(frozen=True)
class ChangeSummary:
    removed: list[str]
    added: list[str]
    changed: list[str]
    emphasised_skills: list[str]
    reordered_sections: list[str]


def compare(master: MasterCV, tailored: TailoredCV, job: JobSpec | None = None) -> ChangeSummary:
    master_bullets = {b.id: b.text for e in master.experience for b in e.bullets}
    master_bullets.update({b.id: b.text for p in master.projects for b in p.bullets})
    tailored_bullets = {b.source_id: b.text for e in tailored.experience for b in e.bullets}
    tailored_bullets.update({b.source_id: b.text for p in tailored.projects for b in p.bullets})
    removed = [
        f"{key}: {text}" for key, text in master_bullets.items() if key not in tailored_bullets
    ]
    added = [
        f"{key}: {text}" for key, text in tailored_bullets.items() if key not in master_bullets
    ]
    changed = [
        f"{key}: {master_bullets[key]} → {text}"
        for key, text in tailored_bullets.items()
        if key in master_bullets and text != master_bullets[key]
    ]
    wanted = _terms(job) if job else set()
    emphasised = [skill for skill in tailored.skills if _score(skill, wanted) > 0]
    return ChangeSummary(removed, added, changed, emphasised, [])


def change_report(summary: ChangeSummary) -> str:
    def section(title: str, items: list[str]) -> str:
        body = "\n".join(f"- {item}" for item in items) if items else "- None"
        return f"## {title}\n\n{body}"

    return (
        "# CV change report\n\n"
        + "\n\n".join(
            (
                section("Bullets removed", summary.removed),
                section("Bullets added", summary.added),
                section("Wording changed", summary.changed),
                section("Skills emphasised", summary.emphasised_skills),
                section("Sections reordered", summary.reordered_sections),
            )
        )
        + "\n"
    )


def ats_report(master: MasterCV, tailored: TailoredCV, job: JobSpec) -> str:
    cv_text = " ".join(
        [
            tailored.profile,
            *tailored.skills,
            *(b.text for e in tailored.experience for b in e.bullets),
        ]
    ).casefold()
    requirements = list(dict.fromkeys(job.required_skills + job.desirable_skills))
    matched = [item for item in requirements if item.casefold() in cv_text]
    missing = [item for item in job.required_skills if item.casefold() not in cv_text]
    weaknesses = ["Required skill not evidenced: " + item for item in missing]
    recommendations = (
        ["Do not add missing skills unless the master CV can evidence them."]
        if missing
        else ["All extracted required skills are evidenced in the tailored CV."]
    )

    def lines(items: list[str]) -> str:
        return "\n".join(f"- {item}" for item in items) if items else "- None"

    return (
        "# ATS report\n\n## Keywords matched\n\n"
        + lines(matched)
        + "\n\n## Missing requirements\n\n"
        + lines(missing)
        + "\n\n## Potential weaknesses\n\n"
        + lines(weaknesses)
        + "\n\n## Recommendations\n\n"
        + lines(recommendations)
        + "\n"
    )
