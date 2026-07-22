"""Job input loading and conservative, deterministic extraction."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from cv_builder.models import JobSpec

SKILLS = (
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "Go",
    "Rust",
    "C++",
    "C#",
    ".NET",
    "AWS",
    "Azure",
    "GCP",
    "Kafka",
    "RabbitMQ",
    "Kubernetes",
    "Docker",
    "PostgreSQL",
    "MySQL",
    "Redis",
    "Terraform",
    "REST APIs",
    "GraphQL",
    "CI/CD",
    "Observability",
    "Distributed systems",
    "Machine learning",
    "Artificial intelligence",
    "React",
    "Django",
)
INDUSTRIES = {
    "financial": "financial services",
    "fintech": "financial technology",
    "healthcare": "healthcare",
    "retail": "retail",
    "government": "public sector",
    "education": "education",
    "insurance": "insurance",
}
ACTION_WORDS = (
    "build",
    "design",
    "develop",
    "deliver",
    "lead",
    "mentor",
    "operate",
    "improve",
    "own",
)
STOP_WORDS = {
    "and",
    "the",
    "with",
    "for",
    "that",
    "this",
    "from",
    "your",
    "will",
    "you",
    "our",
    "are",
    "have",
    "has",
    "into",
    "using",
    "work",
    "role",
    "team",
    "looking",
    "experience",
}


def html_to_text(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html, "html.parser")
    for node in soup(["script", "style", "noscript"]):
        node.decompose()
    return "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())


def fetch_url(url: str) -> str:
    with httpx.Client(follow_redirects=True, timeout=20.0) as client:
        response = client.get(url, headers={"User-Agent": "cv-builder/0.1"})
        response.raise_for_status()
    return html_to_text(response.text)


def load_job(
    *,
    text_path: Path | None = None,
    html_path: Path | None = None,
    url: str | None = None,
    stdin_text: str | None = None,
) -> str:
    sources = [
        text_path is not None,
        html_path is not None,
        url is not None,
        stdin_text is not None,
    ]
    if sum(sources) != 1:
        raise ValueError("Provide exactly one of --job, --html, --url, or --stdin")
    if text_path:
        return text_path.read_text(encoding="utf-8")
    if html_path:
        return html_to_text(html_path.read_text(encoding="utf-8"))
    if url:
        return fetch_url(url)
    return stdin_text or ""


def _title_company(lines: list[str]) -> tuple[str, str]:
    first = lines[0] if lines else "Unknown role"
    for separator in (" — ", " – ", " at ", " | ", " - "):
        if separator in first:
            title, company = first.split(separator, 1)
            return title.strip(), company.strip()
    title = first if len(first) <= 100 else "Unknown role"
    return title, "Unknown company"


def analyse_job(text: str) -> JobSpec:
    clean = re.sub(r"[ \t]+", " ", text).strip()
    if not clean:
        raise ValueError("The job description is empty")
    lines = [line.strip(" •\t-") for line in clean.splitlines() if line.strip()]
    title, company = _title_company(lines)
    lower = clean.casefold()
    found_skills = [
        skill
        for skill in SKILLS
        if re.search(rf"(?<!\w){re.escape(skill.casefold())}(?!\w)", lower)
    ]
    desirable_markers = ("desirable", "preferred", "nice to have", "bonus")
    required: list[str] = []
    desirable: list[str] = []
    sentences = re.split(r"(?<=[.!?])\s+|\n+", clean)
    for skill in found_skills:
        contexts = [
            sentence.casefold() for sentence in sentences if skill.casefold() in sentence.casefold()
        ]
        target = (
            desirable
            if any(marker in context for context in contexts for marker in desirable_markers)
            else required
        )
        target.append(skill)
    responsibilities = [
        sentence.strip(" •-")
        for sentence in sentences
        if any(re.search(rf"\b{word}\w*\b", sentence, re.I) for word in ACTION_WORDS)
    ][:12]
    words = re.findall(r"[A-Za-z][A-Za-z0-9+#./-]{2,}", clean)
    counts = Counter(word.casefold() for word in words if word.casefold() not in STOP_WORDS)
    frequent = [word for word, count in counts.most_common(20) if count >= 2]
    keywords = list(dict.fromkeys(found_skills + frequent))[:20]
    seniority = next(
        (
            level
            for level in ("principal", "staff", "lead", "senior", "junior", "graduate")
            if level in f"{title} {clean[:500]}".casefold()
        ),
        "unspecified",
    )
    industry = next((name for marker, name in INDUSTRIES.items() if marker in lower), "unspecified")
    return JobSpec(
        title=title,
        company=company,
        description=clean,
        responsibilities=responsibilities,
        required_skills=required,
        desirable_skills=desirable,
        keywords=keywords,
        seniority=seniority,
        industry=industry,
    )
