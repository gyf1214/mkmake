import os.path as path
from typing import TextIO

from .c import CProject


class TestProject(CProject):
    __test__ = False

    def __init__(self, root_path: str, **kwargs):
        super().__init__(
            root_path,
            output_name='test', output_type=CProject.OutputType.BINARY,
            **kwargs)

        self.test_command = kwargs['test_command']
        self.test_files = kwargs.get('test_files', [])
        self.private_depends = kwargs.get('private_depends', [])
        self.test_path = path.join(self.build_root, 'tests')
        self.test_output = path.join(self.test_path, 'summary.out')

    def inject_depends(self, projects):
        super().inject_depends(projects)

        for name in self.private_depends:
            if name not in self.depends_proj:
                raise ValueError(
                    f"Unknown private dependency '{name}', "
                    f"must also be listed in depends"
                )
            dep = self.depends_proj[name]
            assert isinstance(dep, CProject), "Depends not a CProject"

            self.all_includes.append(dep.internal_path)
            for key, value in dep.internals.items():
                if key not in self.all_deps:
                    self.all_deps[key] = value

    def write_target(self, fout: TextIO):
        super().write_target(fout)

        files = [
            self.get_path(path.join(self.root_path, file))
            for file in self.test_files
        ]

        fout.write(
            f"\ntest: all {' '.join(files)}\n"
            f"\t@echo RUN test\n"
            f"\trm -fr {self.test_path}\n"
            f"\t{self.test_command.format(*files)}\n"
        )
        self.phonies.append('test')
