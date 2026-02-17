from argparse import ArgumentParser
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def load_example_module():
    path = Path(__file__).resolve().parents[1] / "examples" / "generic_make.py"
    spec = spec_from_file_location("generic_make_example", path)
    module = module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_no_flag_sets_same_destination_false():
    mod = load_example_module()
    parser = ArgumentParser()
    mod.add_flag(parser, "debug")

    debug_args = parser.parse_args(["--debug"])
    assert debug_args.debug is True

    no_debug_args = parser.parse_args(["--no-debug"])
    assert no_debug_args.debug is False
    assert not hasattr(no_debug_args, "no_debug")
