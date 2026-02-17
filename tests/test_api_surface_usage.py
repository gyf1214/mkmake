from mkmake import make_projects
from mkmake.projects import CProject, TestProject, YYProject


def test_api_surface_available():
    assert CProject.OutputType.STATIC
    assert YYProject
    assert TestProject
    assert callable(make_projects)
