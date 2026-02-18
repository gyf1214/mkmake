import pytest

from mkmake import make_projects
from mkmake.projects import CProject, TestProject


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


def test_testproject_can_opt_in_private_headers_from_dependency(tmp_path):
    core = tmp_path / "core"
    test_root = tmp_path / "test"

    (core / "src" / "include").mkdir(parents=True)
    (core / "include").mkdir(parents=True)
    (core / "src" / "core.c").write_text(
        '#include "core_pub.h"\n'
        '#include "core_priv.h"\n'
        "int core(void){return 0;}\n"
    )
    (core / "include" / "core_pub.h").write_text("#pragma once\n")
    (core / "src" / "include" / "core_priv.h").write_text("#pragma once\n")

    (test_root / "src").mkdir(parents=True)
    (test_root / "include").mkdir(parents=True)
    (test_root / "src" / "main.c").write_text(
        '#include "core_priv.h"\n'
        "int main(void){return 0;}\n"
    )
    (test_root / "include" / "main.h").write_text("#pragma once\n")

    projects = {
        "core": CProject(
            str(core),
            output_name="libcore.a",
            output_type=CProject.OutputType.STATIC,
        ),
        "test": TestProject(
            str(test_root),
            test_command="python3 -c 'print(0)'",
            depends=["core"],
            private_depends=["core"],
        ),
    }

    make_projects(projects)
    mk = (test_root / "target" / "Makefile").read_text()
    assert f"-I{(core / 'src' / 'include').as_posix()}" in mk
    assert f"{(core / 'src' / 'include' / 'core_priv.h').as_posix()}" in mk


def test_private_header_name_collision_keeps_local_dependency_authoritative(tmp_path):
    core = tmp_path / "core"
    test_root = tmp_path / "test"

    (core / "src" / "include").mkdir(parents=True)
    (core / "include").mkdir(parents=True)
    (core / "src" / "core.c").write_text("int core(void){return 0;}\n")
    (core / "include" / "core_pub.h").write_text("#pragma once\n")
    (core / "src" / "include" / "x.h").write_text("#pragma once\n")

    (test_root / "src").mkdir(parents=True)
    (test_root / "include").mkdir(parents=True)
    (test_root / "include" / "x.h").write_text("#pragma once\n")
    (test_root / "src" / "main.c").write_text(
        '#include "x.h"\n'
        "int main(void){return 0;}\n"
    )

    projects = {
        "core": CProject(
            str(core),
            output_name="libcore.a",
            output_type=CProject.OutputType.STATIC,
        ),
        "test": TestProject(
            str(test_root),
            test_command="python3 -c 'print(0)'",
            depends=["core"],
            private_depends=["core"],
        ),
    }

    make_projects(projects)
    mk = (test_root / "target" / "Makefile").read_text()
    assert "target/obj/main.o : src/main.c include/x.h" in mk
    assert f"{(core / 'src' / 'include' / 'x.h').as_posix()}" not in mk


def test_private_header_opt_in_keeps_transitive_dependency_expansion(tmp_path):
    core = tmp_path / "core"
    test_root = tmp_path / "test"

    (core / "src" / "include").mkdir(parents=True)
    (core / "include").mkdir(parents=True)
    (core / "src" / "core.c").write_text(
        '#include "core_priv.h"\n'
        "int core(void){return 0;}\n"
    )
    (core / "src" / "include" / "core_priv.h").write_text(
        '#pragma once\n'
        '#include "core_pub.h"\n'
    )
    (core / "include" / "core_pub.h").write_text("#pragma once\n")

    (test_root / "src").mkdir(parents=True)
    (test_root / "include").mkdir(parents=True)
    (test_root / "src" / "main.c").write_text(
        '#include "core_priv.h"\n'
        "int main(void){return 0;}\n"
    )
    (test_root / "include" / "main.h").write_text("#pragma once\n")

    projects = {
        "core": CProject(
            str(core),
            output_name="libcore.a",
            output_type=CProject.OutputType.STATIC,
        ),
        "test": TestProject(
            str(test_root),
            test_command="python3 -c 'print(0)'",
            depends=["core"],
            private_depends=["core"],
        ),
    }

    make_projects(projects)
    mk = (test_root / "target" / "Makefile").read_text()
    assert f"{(core / 'src' / 'include' / 'core_priv.h').as_posix()}" in mk
    assert f"{(core / 'target' / 'include' / 'core_pub.h').as_posix()}" in mk
