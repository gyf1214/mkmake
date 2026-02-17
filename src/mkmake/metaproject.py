from typing import Dict, List, Set
import os
import os.path as path

from .projects import CProject


def _sort_projects(
    name: str,
    projects: Dict[str, CProject],
    ordered: List[str],
    visiting: Set[str],
    visited: Set[str],
) -> None:
    if name in visited:
        return
    if name in visiting:
        raise ValueError(f"Dependency cycle detected at project '{name}'")
    if name not in projects:
        raise ValueError(f"Unknown project dependency '{name}'")

    visiting.add(name)
    proj = projects[name]
    for child in proj.depends:
        _sort_projects(child, projects, ordered, visiting, visited)
    visiting.remove(name)

    visited.add(name)
    ordered.append(name)


def make_projects(projects: Dict[str, CProject], **kwargs) -> None:
    if not projects:
        return

    common_root = path.commonpath([proj.root_path for proj in projects.values()])
    target_root = path.join(common_root, "target")
    os.makedirs(target_root, exist_ok=True)

    ordered_names: List[str] = []
    visiting: Set[str] = set()
    visited: Set[str] = set()
    for name in projects:
        _sort_projects(name, projects, ordered_names, visiting, visited)

    ordered_projects = [(name, projects[name]) for name in ordered_names]

    for _, proj in ordered_projects:
        for key, value in kwargs.items():
            if value is not None:
                setattr(proj, key, value)

    for _, proj in ordered_projects:
        proj.scan_sources()

    for _, proj in ordered_projects:
        proj.inject_depends(projects)
        proj.scan_deps()

    for _, proj in ordered_projects:
        proj.make()

    meta_makefile = path.join(target_root, "Projects.mk")
    with open(meta_makefile, "w") as fout:
        phonies = ["default", "all-all", "clean-all", "rebuild-all"]
        fout.write("default : all-all\n")
        for name, proj in ordered_projects:
            fout.write(
                f"############ Project {name} ############\n"
                f"{name} : {' '.join(proj.depends)}\n"
                f"\t@echo Project {name}\n"
                f"\t$(MAKE) -C {proj.root_path} -f {proj.makefile}\n\n"
            )
            phonies.append(name)

            for word in proj.phonies:
                target = f"{word}-{name}"
                fout.write(
                    f"{target} : \n"
                    f"\t@echo Project {name} {word}\n"
                    f"\t$(MAKE) -C {proj.root_path} -f {proj.makefile} {word}\n\n"
                )
                phonies.append(target)

        fout.write(
            f"all-all : {' '.join(ordered_names)}\n"
            f"clean-all : {' '.join(f'clean-{name}' for name in ordered_names)}\n"
            "rebuild-all : clean-all all-all\n"
        )
        fout.write(f".PHONY : {' '.join(phonies)}\n")
