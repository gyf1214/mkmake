from typing import Iterable, TextIO
import os.path as path

from .c import CProject


class YYProject(CProject):
    LEX_RULE = (
        "\t@echo LEX $<\n"
        "\tmkdir -p $(dir $@)\n"
        "\t$(LEX) $(LEXFLAGS) -o $@ $<\n"
    )

    def __init__(self, root_path: str, **kwargs):
        super().__init__(root_path, **kwargs)
        self.grammar_path = path.join(self.source_path, 'yy')
        self.generated_path = path.join(self.build_root, 'generated-src')
        self.generated_obj_path = path.join(self.obj_path, 'generated')

        self.all_includes.append(self.generated_path)

    def generate_key(self, keys: Iterable[str], suffix: str, new_suffix: str):
        for key in keys:
            yield key.replace(suffix, new_suffix)

    def scan_sources(self):
        super().scan_sources()

        self.generated_srcs = {}

        print("Scan lex files...")
        self.lex_files = self.scan_files([self.grammar_path], ['l'])

        lex_sources = {
            key.replace('.l', '.yy.c'): key
            for key in self.lex_files.keys()
        }

        print(f"Found {len(self.lex_files)} lex files.")

        print("Scan yacc files...")
        self.yy_files = self.scan_files([self.grammar_path], ['y'])

        yy_sources = {
            key.replace('.y', '.tab.c'): key
            for key in self.yy_files.keys()
        }
        yy_headers = {
            key: path.join(self.generated_path, key)
            for key in self.generate_key(self.yy_files, '.y', '.tab.h')
        }

        print(f"Found {len(self.yy_files)} yacc files.")

        self.safe_update(self.all_deps, yy_headers)
        self.safe_update(self.all_sources, self.lex_files)
        self.safe_update(self.all_sources, self.yy_files)
        self.safe_update(self.generated_srcs, lex_sources)
        self.safe_update(self.generated_srcs, yy_sources)

    def write_prelude(self, fout: TextIO):
        super().write_prelude(fout)

        print("Write yy prelude")
        fout.write(
            f"LEX=flex\n"
            f"LEXFLAGS=\n\n"
            f"YACC=bison\n"
            f"YACCFLAGS=-v\n\n"
        )

    def write_rules(self, fout: TextIO):
        super().write_rules(fout)

        self.write_rule(
            fout,
            f"{self.grammar_path}/%.l",
            f"{self.generated_path}/%.yy.c",
            YYProject.LEX_RULE
        )

        for key, source in self.yy_files.items():
            c_source = path.join(
                self.generated_path, key.replace('.y', '.tab.c'))
            c_header = path.join(
                self.generated_path, key.replace('.y', '.tab.h'))

            source = self.get_path(source)
            c_source = self.get_path(c_source)
            c_header = self.get_path(c_header)

            fout.write(
                f"{c_source} {c_header} &: {source}\n"
                "\t@echo YACC $<\n"
                "\tmkdir -p $(dir $@)\n"
                f"\t$(YACC) $(YACCFLAGS) --defines={c_header} -o {c_source} $<\n\n"
            )

        self.write_rule(
            fout,
            f"{self.generated_path}/%.c",
            f"{self.generated_obj_path}/%.o",
            CProject.C_RULE
        )

    def write_deps(self, fout: TextIO):
        super().write_deps(fout)

        print(f"generated_srcs={self.generated_srcs}")
        for generated_key, key in self.generated_srcs.items():
            target = CProject.SUFFIX_RE.sub('.o', generated_key)
            target = path.join(self.generated_obj_path, target)
            target = self.get_path(target)

            source = path.join(self.generated_path, generated_key)
            source = self.get_path(source)

            deps = self.deps[key]
            deps = [
                self.get_path(self.all_deps[key])
                for key in deps
            ]

            self.objs.append(target)
            fout.write(f"{target} : {source} {' '.join(deps)}\n")

    def clean_targets(self):
        yield from super().clean_targets()
        yield self.generated_path
