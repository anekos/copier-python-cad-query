# CadQuery project convention (anekos)

New CadQuery projects live under `~/forge/cad/CadQuery/{project-name}/` as uv-managed,
src-layout packages with a click CLI. Model code goes in `main.py` (pydantic `Param` +
`build()`), CLI wiring in `__init__.py`. Match this layout exactly unless told otherwise.

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
        ├── __init__.py       # click CLI
        └── main.py           # Param model + build()
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
    "pre-commit>=4.6.1",
    "pydantic>=2.13.4",
    "pytest>=9.1.1",
    "ruff>=0.16.1",
]

[tool.mypy]
mypy_path = "src"
explicit_package_bases = true
```

All dependencies (including cadquery) go in the `dev` dependency-group; `dependencies` stays empty.

## src/{package_name}/main.py — model code

```python
import cadquery as cq
from click_cadquery.git import version_number as ver
from pydantic import BaseModel


class Param(BaseModel):
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
```

- Every dimension that might change becomes a `Param` field with a default.
- `filename` embeds `version_number()` (commit count from git — the repo must have
  at least one commit) plus the parameter values.
- `build()` is pure: takes `Param`, returns the `Workplane`; no I/O.

## src/{package_name}/__init__.py — CLI

```python
from pathlib import Path

import click
from cadquery import vis
from click_cadquery import define_options

from .main import Param, build

TypePath = click.types.Path(path_type=Path)


@click.group(context_settings={"show_default": True})
@click.pass_context
def main(ctx: click.Context) -> None:
    pass


@main.command(name="build")
@define_options(Param)
def command_build(output: Path | None, param: Param, show: bool) -> None:
    print("Build with:", param)

    result = build(param)

    dist = Path("dist")
    dist.mkdir(exist_ok=True)
    result.export(str(output if output else dist / param.filename))
    if show:
        vis.show(result)
```

`@define_options(Param)` (from click-cadquery) turns each `Param` field into a
`--width`-style click option and injects `output` / `param` / `show` into the function.

## Makefile

```make
.PHONY: watch
watch:
	axe src/**/*.py -- uv run {project-name} -- build --show

.PHONY: build
build:
	axe src/**/*.py -- uv run {project-name} -- build
```

(`axe` is a file-watcher; the `build` target rebuilds on every source change.)

## Setup and daily commands

Run everything from the project root — `dist/` is created relative to the CWD.

```bash
git init && git add -A && git commit -m "init"   # version_number() needs a commit
uv sync                                          # creates .venv from the dev group
uv run {project-name} build                      # export to dist/v{N}-....stl
uv run {project-name} build --width 120 --show   # override params, open viewer
uv run mypy src && uv run ruff check src         # lint before committing
```

Agents verifying a model non-interactively: run `uv run {project-name} build`
(never `--show`; `vis.show` opens a GUI) and check the exported file in `dist/`,
or import `build(Param())` directly and inspect `val().Volume()` / `BoundingBox()`.
