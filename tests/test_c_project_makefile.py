from mkmake.projects import CProject


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
