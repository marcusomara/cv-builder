from cv_builder.job import analyse_job
from cv_builder.render import generate_typst, render
from cv_builder.tailor import tailor


def test_generates_two_page_typst(master, rules, project_root, tmp_path) -> None:  # type: ignore[no-untyped-def]
    cv = tailor(master, analyse_job("Senior Engineer — Acme\nPython Kafka Kubernetes"), rules)
    source = generate_typst(cv, project_root / "templates/senior-engineer.typ")
    assert source.count("#pagebreak()") == 1
    assert "Gresham Technologies" in source
    assert "kafka-platform" not in source
    typ_path, pdf_path = render(
        cv, tmp_path, project_root / "templates/senior-engineer.typ", compile_output=False
    )
    assert typ_path.exists()
    assert not pdf_path.exists()
