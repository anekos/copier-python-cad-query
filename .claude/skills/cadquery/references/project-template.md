# CadQuery project convention (anekos)

New CadQuery projects live under `~/forge/cad/CadQuery/{project-name}/` as uv-managed,
src-layout packages with a click CLI. Model code (a `click_cadquery.BuildParam` subclass
+ pure `build()`) and CLI wiring (`click_cadquery.define_app`) both live in `__init__.py`.
Match this layout exactly unless told otherwise.

## Layout

```
{project-name}/               # kebab-case
├── .git/                     # REQUIRED — version_number() reads git history
├── .gitignore                # include: .venv/, dist/, __pycache__/
├── .python-version           # "3.13"
├── .pre-commit-config.yaml   # mypy, ruff format/check, pytest on pre-push
├── Makefile
├── pyproject.toml
├── README.md
└── src/
    └── {package_name}/       # snake_case
        └── __init__.py       # Param model + build() + CLI (main)
```

## pyproject.toml

```toml
[project]
name = "{project-name}"
version = "0.1.0"
description = ""
readme = "README.md"
authors = [
    { name = "anekos", email = "anekos@snca.net" }
]
requires-python = ">=3.13"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project.scripts]
{project-name} = "{package_name}:main"

[tool.hatch.build.targets.wheel]
packages = ["src/{package_name}"]

[dependency-groups]
dev = [
    "cadquery>=2.8.0",
    "click>=8.4.2",
    "click-cadquery>=0.2.0",
    "mypy>=2.3.0",
    "pydantic>=2.13.4",
    "pytest>=9.1.1",
    "ruff>=0.16.1",
]

[tool.mypy]
mypy_path = "src"
explicit_package_bases = true
```

All dependencies (including cadquery) go in the `dev` dependency-group; `dependencies`
stays empty. `pre-commit` is not listed here — the copier template installs it via a
post-generation task, and `make setup` runs `pre-commit install`.

## src/{package_name}/__init__.py — model + CLI

```python
import cadquery as cq
from click_cadquery import BuildParam, define_app
from click_cadquery.git import version_number as ver


class Param(BuildParam):
    width: int = 100
    height: int = 100
    depth: int = 100
    thickness: float = 2.0

    @property
    def filename(self) -> str:
        return f"v{ver()}-{self.width}w{self.height}h{self.depth}d{self.thickness}t.stl"


def build(param: Param) -> cq.Workplane:
    result = cq.Workplane("XY")
    # ... model here ...
    return result


main = define_app(Param, build)
```

- Every dimension that might change becomes a `Param` field with a default.
- `filename` embeds `version_number()` (commit count from git — the repo must have
  at least one commit) plus the parameter values.
- `build()` is pure: takes `Param`, returns the `Workplane`; no I/O.
- `define_app(Param, build)` (from click-cadquery) builds the CLI: a `build` command with
  options generated from `Param`'s fields (plus `output` argument, `--show`, `--screenshot`),
  and an `interactive` command that prompts for each field one at a time. The result must
  stay bound to `main` — `pyproject.toml`'s `project.scripts` points at `{package_name}:main`.

## Makefile

```make
.PHONY: interactive
interactive:
	uv run {project-name} -- interactive

.PHONY: build
build:
	axe src/**/*.py -- uv run {project-name} -- build

.PHONY: watch
watch:
	axe src/**/*.py -- uv run {project-name} -- build --show

.PHONY: setup
setup:
	uv sync
	uv run pre-commit install
```

(`axe` is a file-watcher; `build` rebuilds on every source change, `watch` does the same
but also opens/refreshes the viewer via `--show`.)

## Setup and daily commands

Run everything from the project root — `dist/` is created relative to the CWD.

```bash
git init && git add -A && git commit -m "init"   # version_number() needs a commit
make setup                                       # uv sync + pre-commit install
uv run {project-name} build                      # export to dist/v{N}-....stl
uv run {project-name} build --width 120 --show   # override params, open viewer
uv run {project-name} interactive                # prompt for each Param field, then build
uv run mypy src && uv run ruff check src         # lint before committing
```

Agents verifying a model non-interactively: run `uv run {project-name} build`
(never `--show`; `vis.show` opens a GUI) — `--screenshot` is fine, it just saves a PNG
next to the output — and check the exported file in `dist/`, or import `build(Param())`
directly and inspect `val().Volume()` / `BoundingBox()`.
