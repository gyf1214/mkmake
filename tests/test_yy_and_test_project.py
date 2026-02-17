from mkmake.projects import CProject, TestProject, YYProject


def test_yy_project_generates_rules(tmp_path):
    root = tmp_path / "parser"
    (root / "src" / "yy").mkdir(parents=True)
    (root / "include").mkdir(parents=True)
    (root / "src" / "yy" / "lexer.l").write_text("%%\n")
    (root / "src" / "yy" / "parser.y").write_text("%%\n")

    p = YYProject(
        str(root),
        output_name="libparser.a",
        output_type=CProject.OutputType.STATIC,
    )
    p.scan_sources()
    p.inject_depends({})
    p.scan_deps()
    p.make()

    mk = (root / "target" / "Makefile").read_text()
    assert "LEX=flex" in mk
    assert "YACC=bison" in mk


def test_testproject_adds_test_target(tmp_path):
    root = tmp_path / "test"
    (root / "src").mkdir(parents=True)
    (root / "include").mkdir(parents=True)
    (root / "tests").mkdir(parents=True)
    (root / "src" / "main.c").write_text("int main(void){return 0;}\n")
    (root / "include" / "main.h").write_text("#pragma once\n")
    (root / "tests" / "run.py").write_text("print('ok')\n")
    (root / "tests" / "tests.json").write_text("{}\n")

    p = TestProject(
        str(root),
        test_command="python3 {0} {1}",
        test_files=["tests/run.py", "tests/tests.json"],
    )
    p.scan_sources()
    p.inject_depends({})
    p.scan_deps()
    p.make()

    mk = (root / "target" / "Makefile").read_text()
    assert "test: all" in mk
