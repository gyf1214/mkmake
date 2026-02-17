from argparse import ArgumentParser

from mkmake import make_projects
from mkmake.projects import CProject, TestProject, YYProject


def add_flag(parser: ArgumentParser, flag: str) -> None:
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(f"-{flag}", f"--{flag}", dest=flag, action="store_true")
    group.add_argument(f"-no-{flag}", f"--no-{flag}", dest=flag, action="store_false")


def parse_args():
    parser = ArgumentParser()
    add_flag(parser, "debug")
    add_flag(parser, "test")
    return parser.parse_args()


def main(args) -> None:
    projects = {
        "generic": CProject(
            "generic",
            output_name="libgeneric.a",
            output_type=CProject.OutputType.STATIC,
            std="gnu99",
        ),
        "parser": YYProject(
            "parser",
            output_name="libparser.a",
            output_type=CProject.OutputType.STATIC,
            std="gnu99",
            depends=["generic"],
        ),
        "test": TestProject(
            "test",
            test_command="python3 {0} {1}",
            test_files=["tests/run.py", "tests/tests.json"],
            std="gnu99",
            depends=["generic", "parser"],
        ),
    }
    make_projects(projects, debug=args.debug, test=args.test)


if __name__ == "__main__":
    main(parse_args())
