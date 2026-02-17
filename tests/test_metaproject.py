import pytest

from mkmake import make_projects
from mkmake.projects import CProject


def test_make_projects_writes_meta_makefile(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    for root in [a, b]:
        (root / "src").mkdir(parents=True)
        (root / "include").mkdir(parents=True)
        (root / "src" / "x.c").write_text("int x(void){return 0;}\n")
        (root / "include" / "x.h").write_text("#pragma once\n")

    projects = {
        "a": CProject(
            str(a),
            output_name="liba.a",
            output_type=CProject.OutputType.STATIC,
        ),
        "b": CProject(
            str(b),
            output_name="libb.a",
            output_type=CProject.OutputType.STATIC,
            depends=["a"],
        ),
    }

    make_projects(projects)
    meta = (tmp_path / "target" / "Projects.mk").read_text()
    assert "all-all : a b" in meta


def test_make_projects_rejects_cycles(tmp_path):
    a = CProject(
        str(tmp_path / "a"),
        output_name="liba.a",
        output_type=CProject.OutputType.STATIC,
        depends=["b"],
    )
    b = CProject(
        str(tmp_path / "b"),
        output_name="libb.a",
        output_type=CProject.OutputType.STATIC,
        depends=["a"],
    )

    with pytest.raises(ValueError):
        make_projects({"a": a, "b": b})
