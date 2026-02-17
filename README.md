# mkmake

[![PyPI version](https://img.shields.io/pypi/v/mkmake.svg)](https://pypi.org/project/mkmake/)

`mkmake` is a Python package for generating Makefiles for multiple related C projects from code.

## Installation

```bash
pip install mkmake
```

## Features

- Generate project and meta Makefiles from Python project definitions.
- Model mixed project types with a shared API (`CProject`, `YYProject`, `TestProject`).
- Discover and wire header dependencies for C projects.
- Inject dependency include paths and library linkage across project boundaries.
- Configure build variants through `debug` and `test` generation flags.

## Quick Start

```python
from mkmake import make_projects
from mkmake.projects import CProject, TestProject, YYProject
```

Define projects in a dictionary, then call `make_projects(...)` with build flags:

```python
projects = {
    "core": CProject("core", output_name="libcore.a"),
    "parser": YYProject("parser", output_name="libparser.a", depends=["core"]),
    "tests": TestProject("tests", test_command="python3 {0} {1}", depends=["core", "parser"]),
}
make_projects(projects, debug=True, test=True)
```

Full usage example: `examples/generic_make.py`

## Limitations

- package-only API surface
- no CLI in package code
