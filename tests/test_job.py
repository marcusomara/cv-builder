from cv_builder.job import analyse_job, html_to_text


def test_extracts_job_fields_and_classifies_desirable_skills() -> None:
    spec = analyse_job(
        "Senior Engineer — Acme Ltd\n"
        "Build Python services and operate Kubernetes. PostgreSQL is required. "
        "Kafka experience is desirable."
    )
    assert spec.title == "Senior Engineer"
    assert spec.company == "Acme Ltd"
    assert spec.seniority == "senior"
    assert "Python" in spec.required_skills
    assert "Kafka" in spec.desirable_skills
    assert spec.responsibilities


def test_html_removes_non_content() -> None:
    text = html_to_text("<main><h1>Engineer</h1><p>Build APIs.</p></main><script>ignore()</script>")
    assert "Engineer" in text
    assert "Build APIs" in text
    assert "ignore" not in text
