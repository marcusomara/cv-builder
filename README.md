# CV Builder

CV Builder is a local, deterministic tool for producing job-specific CVs from one structured
master CV. It extracts a vacancy into a validated `JobSpec`, ranks existing evidence by relevance,
validates every selected claim, generates audit reports, and renders a black-and-white two-page PDF
with Typst.

It does not call an AI service. Automatic tailoring selects and reorders source material without
paraphrasing it. This conservative design makes the most important guarantee enforceable: generated
experience cannot silently drift beyond the master CV.

## Requirements and installation

- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- [Typst](https://typst.app/docs/) available as `typst` on `PATH`

From the repository root:

```shell
uv sync
uv run cv check
```

`uv sync` creates an isolated environment and installs both application and development
dependencies. CV Builder has no database, daemon, container, account, or network dependency. The
`--url` input is the sole feature that accesses the network, to download the supplied advert.

Before real use, replace the example identity and work history in `data/master-cv.yaml`. Treat that
file as the only source of truth and retain stable bullet IDs when editing wording.

## Typical workflows

Build from plain text, HTML, a URL, or standard input:

```shell
uv run cv build --job jobs/example.txt
uv run cv build --html jobs/acme.html
uv run cv build --url 'https://example.com/jobs/123'
pbpaste | uv run cv build --stdin
```

Each invocation accepts exactly one input. The normalised title and company determine the output
directory, for example `output/example-ltd-senior-software-engineer/`.

Inspect individual stages:

```shell
uv run cv analyse --job jobs/example.txt --output jobs/example.json
uv run cv validate output/example-ltd-senior-software-engineer/tailored-cv.yaml
uv run cv render output/example-ltd-senior-software-engineer/tailored-cv.yaml
uv run cv diff output/example-ltd-senior-software-engineer/tailored-cv.yaml
uv run cv check
```

`render` always validates first. A failed claim check exits non-zero and no PDF compilation occurs.

## Pipeline

1. Text, HTML, URL content, or stdin is reduced to clean text.
2. The analyser extracts title, company, responsibilities, skills, keywords, seniority, and industry
   into a Pydantic `JobSpec`. Extraction is deliberately conservative and deterministic.
3. Master bullets are scored against the extracted vocabulary. Relevant bullets and skills move
   first, subject to `config/tailoring-rules.yaml` limits.
4. Each tailored bullet carries the stable `source_id` of the master bullet it reproduces.
5. Validation resolves each ID, requires identical claim text, preserves employers and dates,
   rejects unknown skills, enforces length/count limits, and rejects forbidden buzzwords.
6. Reports and tailored YAML are written, Typst source is generated, and Typst compiles the PDF.

The strict identical-wording rule is intentional. A person may edit the master CV to improve a
claim once, then all future outputs inherit the reviewed wording. An extension using a trusted local
language model could add constrained rewriting later, but it should retain the same fail-closed
validation boundary.

## Output contract

Every successful build produces:

```text
output/company-role/
├── ats-report.md          # matched terms, gaps, weaknesses, recommendations
├── change-report.md       # removals, additions, wording, emphasis, ordering
├── cv.pdf                 # final application document
├── cv.typ                 # inspectable Typst source
├── job-analysis.json      # normalised JobSpec
└── tailored-cv.yaml       # validated rendering input with source IDs
```

Typst uses a deliberately restrained A4 template: excellent system typography, no graphics, no
icons, no sidebars, and one explicit page break. Experience occupies page one; skills, projects,
education, and achievements occupy page two. Keeping the configured bullet limits appropriate to
the master CV prevents content overflow. After materially expanding the master CV, compile and
visually inspect one representative output before changing the limits.

## Repository layout

```text
config/              Tailoring and safety policy
data/                Structured master CV
jobs/                Local vacancy inputs
output/              Generated, git-ignored applications
prompts/             Policy text for future local-model adapters
templates/           Typst templates
src/cv_builder/      Domain models, pipeline, validation, rendering, CLI
tests/               Job, validation, rendering, and CLI tests
```

The modules are intentionally separated at stable boundaries. Input adapters produce `JobSpec`;
tailoring consumes domain models; validation has no filesystem dependency; rendering consumes only
validated `TailoredCV`. This makes future Google Docs or LinkedIn importers, multiple templates,
cover letters, company prompt packs, and translated presentation layers additive rather than
cross-cutting. Network-based integrations should remain optional and never replace local YAML as the
source of truth.

## Development

Run the complete quality gate:

```shell
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

See `AGENTS.md` for the factual-integrity and contribution rules. In particular, tests and
validation are mandatory before rendering changes are accepted.

