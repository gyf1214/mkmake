import mkmake
from mkmake.projects import CProject, TestProject, YYProject


def test_public_imports_exist():
    assert mkmake.make_projects
    assert CProject
    assert YYProject
    assert TestProject
