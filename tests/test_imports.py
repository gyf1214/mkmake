import mkmake
from mkmake.projects import CProject, TestProject, YYProject


def test_public_imports_exist():
    assert mkmake.make_projects
    assert CProject
    assert YYProject
    assert TestProject


def test_testproject_is_not_collectible_by_pytest():
    assert getattr(TestProject, "__test__", True) is False
