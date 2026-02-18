from mkmake.projects import CProject
from mkmake import make_projects


def test_c_project_writes_makefile(tmp_path):
    root = tmp_path / "generic"
    (root / "src").mkdir(parents=True)
    (root / "include").mkdir(parents=True)
    (root / "src" / "x.c").write_text("int x(void){return 1;}\n")
    (root / "include" / "x.h").write_text("#pragma once\nint x(void);\n")

    p = CProject(
        str(root),
        output_name="libgeneric.a",
        output_type=CProject.OutputType.STATIC,
    )
    p.scan_sources()
    p.inject_depends({})
    p.scan_deps()
    p.make()

    mk = (root / "target" / "Makefile").read_text()
    assert "default : all" in mk
    assert "libgeneric.a" in mk


def test_lib_includes_are_appended_after_project_and_dependency_includes(tmp_path):
    dep1 = tmp_path / "dep1"
    dep2 = tmp_path / "dep2"
    app = tmp_path / "app"
    ext = tmp_path / "ext"

    for root in [dep1, dep2, app]:
        (root / "src").mkdir(parents=True)
        (root / "include").mkdir(parents=True)
        (root / "src" / "x.c").write_text("int x(void){return 0;}\n")
        (root / "include" / "x.h").write_text("#pragma once\n")

    ext.mkdir(parents=True)

    projects = {
        "dep1": CProject(
            str(dep1),
            output_name="libdep1.a",
            output_type=CProject.OutputType.STATIC,
        ),
        "dep2": CProject(
            str(dep2),
            output_name="libdep2.a",
            output_type=CProject.OutputType.STATIC,
        ),
        "app": CProject(
            str(app),
            output_name="app",
            output_type=CProject.OutputType.BINARY,
            depends=["dep1", "dep2"],
            lib_includes=[str(ext)],
        ),
    }

    make_projects(projects)

    mk = (app / "target" / "Makefile").read_text()
    cflags = [line for line in mk.splitlines() if line.startswith("CFLAGS=")][0]

    expected = [
        "-Iinclude",
        "-Isrc/include",
        f"-I{(dep1 / 'target' / 'include').as_posix()}",
        f"-I{(dep2 / 'target' / 'include').as_posix()}",
        f"-I{ext.as_posix()}",
    ]

    indices = [cflags.index(flag) for flag in expected]
    assert indices == sorted(indices)
