"""Factual integrity validation."""

from __future__ import annotations

from cv_builder.models import MasterCV, TailoredCV, TailoringRules


class ClaimValidationError(ValueError):
    """Raised when a tailored CV is not supported by its master CV."""


def validate_claims(master: MasterCV, tailored: TailoredCV, rules: TailoringRules) -> list[str]:
    errors: list[str] = []
    master_experiences = {item.id: item for item in master.experience}
    source_bullets = {
        bullet.id: bullet.text for item in master.experience for bullet in item.bullets
    }
    source_bullets.update(
        {bullet.id: bullet.text for item in master.projects for bullet in item.bullets}
    )
    for item in tailored.experience:
        source = master_experiences.get(item.id)
        if source is None:
            errors.append(f"Unknown experience: {item.id}")
            continue
        if rules.preserve_employers and item.employer != source.employer:
            errors.append(f"Employer changed for {item.id}")
        if rules.preserve_dates and (item.start_date, item.end_date) != (
            source.start_date,
            source.end_date,
        ):
            errors.append(f"Dates changed for {item.id}")
        if len(item.bullets) > rules.maximum_bullets_per_experience:
            errors.append(f"Too many bullets for {item.id}")
        for bullet in item.bullets:
            original = source_bullets.get(bullet.source_id)
            if original is None:
                errors.append(f"Unsupported source_id: {bullet.source_id}")
            elif bullet.text != original:
                errors.append(f"Unsupported wording for {bullet.source_id}")
            if len(bullet.text) > rules.maximum_bullet_length:
                errors.append(f"Bullet {bullet.source_id} exceeds maximum length")
    for project in tailored.projects:
        for bullet in project.bullets:
            original = source_bullets.get(bullet.source_id)
            if original is None or bullet.text != original:
                errors.append(f"Unsupported project claim: {bullet.source_id}")
    master_skills = {skill.casefold() for skill in master.skills}
    for skill in tailored.skills:
        if skill.casefold() not in master_skills:
            errors.append(f"Invented skill: {skill}")
    for word in rules.forbidden_buzzwords:
        if word.casefold() in tailored.model_dump_json().casefold():
            errors.append(f"Forbidden buzzword: {word}")
    return errors


def require_valid(master: MasterCV, tailored: TailoredCV, rules: TailoringRules) -> None:
    errors = validate_claims(master, tailored, rules)
    if errors:
        raise ClaimValidationError("Claim validation failed:\n- " + "\n- ".join(errors))
