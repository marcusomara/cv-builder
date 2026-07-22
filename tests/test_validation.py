from cv_builder.models import TailoredBullet
from cv_builder.tailor import tailor
from cv_builder.validation import validate_claims


def test_generated_cv_is_valid(master, rules) -> None:  # type: ignore[no-untyped-def]
    from cv_builder.job import analyse_job

    cv = tailor(master, analyse_job("Senior Engineer — Acme\nBuild Python services."), rules)
    assert validate_claims(master, cv, rules) == []


def test_rejects_unsupported_claim(master, rules) -> None:  # type: ignore[no-untyped-def]
    from cv_builder.job import analyse_job

    cv = tailor(master, analyse_job("Engineer — Acme\nBuild software."), rules)
    cv.experience[0].bullets[0] = TailoredBullet(
        text="Built RAG systems.", source_id="kafka-platform"
    )
    assert "Unsupported wording for kafka-platform" in validate_claims(master, cv, rules)


def test_rejects_changed_employer(master, rules) -> None:  # type: ignore[no-untyped-def]
    from cv_builder.job import analyse_job

    cv = tailor(master, analyse_job("Engineer — Acme\nBuild software."), rules)
    cv.experience[0].employer = "Different Ltd"
    assert "Employer changed for gresham" in validate_claims(master, cv, rules)
