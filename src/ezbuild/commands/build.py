import json
from pathlib import Path
from shlex import split
from subprocess import run
from typing import TYPE_CHECKING, Annotated

from typer import Argument

from ezbuild import pkg_config
from ezbuild.compile_command import CompileCommand
from ezbuild.dep_tree import CyclicDependencyError, DepTree
from ezbuild.environment import (
    Environment,
    Program,
    SharedLibrary,
    StaticLibrary,
    SystemLibrary,
)
from ezbuild.language import Language
from ezbuild.log import ar, cc, ccld, cxx, cxxld, debug, info, ranlib
from ezbuild.safe_exec import SafeBuildError, safe_execute
from ezbuild.utils import fs

if TYPE_CHECKING:
    from ezbuild.dep_tree import Target


def _format_define(define: str) -> str:
    if " " in define:
        return f'"-D{define}"'
    return f"-D{define}"


def _collect_public_defines(target: Target, targets: dict[str, Target]) -> list[str]:
    """
    Collect all public defines from the target's dependencies.
    Uses BFS to traverse the dependency tree.
    """
    public_defines: list[str] = []
    visited: set[str] = set()
    queue: list[str] = [dep for dep in target.dependencies if dep in targets]

    while queue:
        dep_name = queue.pop(0)
        if dep_name in visited:
            continue
        visited.add(dep_name)

        dep_target = targets[dep_name]
        public_defines.extend(dep_target.public_defines)

        for trans_dep in dep_target.dependencies:
            if trans_dep in targets and trans_dep not in visited:
                queue.append(trans_dep)

    return public_defines


def build(
    name: Annotated[str | None, Argument(help="Name of the project to build")] = None,
) -> tuple[int, str]:
    """Build the project."""

    cwd = Path.cwd()
    build_file = cwd / "build.ezbuild"
    build_dir = cwd / "build"
    bin_dir = build_dir / "bin"
    lib_dir = build_dir / "lib"
    compile_commands: list[CompileCommand] = []

    if not build_file.exists():
        return 1, "build.ezbuild does not exist"

    debug("Reading build.ezbuild")
    with Path.open(cwd / "build.ezbuild", "r") as f:
        build_ezbuild = f.read()

    namespace: dict[str, object] = {
        "Environment": Environment,
        "Language": Language,
        "Program": Program,
        "StaticLibrary": StaticLibrary,
        "SharedLibrary": SharedLibrary,
    }

    try:
        result_namespace = safe_execute(build_ezbuild, namespace)
    except SafeBuildError as e:
        return 2, f"Build file validation failed: {e}"

    build_env: Environment | None = None
    targets: dict[str, Target] = {}

    for var_name, value in result_namespace.items():
        if isinstance(value, Environment):
            info(f"Found environment: {var_name}")
            build_env = value

        if isinstance(value, Program):
            info(f"Found program target: {var_name}")
            targets[var_name] = value

        if isinstance(value, StaticLibrary):
            info(f"Found static library target: {var_name}")
            targets[var_name] = value

        if isinstance(value, SharedLibrary):
            info(f"Found shared library target: {var_name}")
            targets[var_name] = value

    if build_env is None:
        return 3, "No build environment found"

    if len(targets) == 0:
        return 4, "No targets found"

    fs.create_dir_if_not_exists(build_dir)

    try:
        dep_tree = DepTree(targets)
        build_order = dep_tree.get_build_order()
    except CyclicDependencyError as e:
        return 5, f"Cyclic dependency error: {e}"

    build_artifacts: dict[str, Path] = {}

    system_libs: dict[str, SystemLibrary] = {}
    for target in build_order:
        for sys_dep in target.system_dependencies:
            if sys_dep not in system_libs:
                system_libs[sys_dep] = pkg_config.query_package(sys_dep)

    for target in build_order:
        info(f"Building {target.name}")

        if isinstance(target, Program):
            debug(f"Building program {target.name}")

            if Language.C in target.languages:
                build_env.ensure_cc()
                build_env.ensure_ccld()

            if Language.CXX in target.languages:
                build_env.ensure_cc()
                build_env.ensure_cxx()
                build_env.ensure_ccld()
                build_env.ensure_cxxld()

            int_dir = build_dir / target.name
            fs.create_dir_if_not_exists(int_dir)

            local_compile_commands: list[CompileCommand] = []
            public_defines = _collect_public_defines(target, targets)
            all_defines = target.defines + target.public_defines + public_defines

            for source in target.sources:
                source_path = cwd / source
                _temp = int_dir / source
                compile_command = CompileCommand()
                compile_command.directory = str(int_dir)
                compile_command.file = str(cwd / source)
                compile_command.output = str(
                    _temp.parent / ((int_dir / source).name + ".o")
                )

                if source_path.suffix == ".c":
                    compile_flags: list[str] = []
                    for sys_dep in target.system_dependencies:
                        compile_flags.extend(system_libs[sys_dep].compile_flags)

                    for define in all_defines:
                        compile_flags.append(_format_define(define))

                    compile_command.command = " ".join(
                        [
                            build_env["CC"],
                            *compile_flags,
                            "-c",
                            "-o",
                            compile_command.output,
                            compile_command.file,
                        ]
                    )
                    cc(f"{compile_command.file}")

                elif source_path.suffix in [".cpp", ".cxx", ".cc"]:
                    compile_flags: list[str] = []
                    for sys_dep in target.system_dependencies:
                        compile_flags.extend(system_libs[sys_dep].compile_flags)

                    for define in all_defines:
                        compile_flags.append(_format_define(define))

                    compile_command.command = " ".join(
                        [
                            build_env["CXX"],
                            *compile_flags,
                            "-c",
                            "-o",
                            compile_command.output,
                            compile_command.file,
                        ]
                    )
                    cxx(f"{compile_command.file}")

                cmd_list = split(compile_command.command)
                result = run(cmd_list, capture_output=True)
                if result.returncode != 0:
                    return 6, f"Compilation failed: {result.stderr.decode()}"

                local_compile_commands.append(compile_command)

            fs.create_dir_if_not_exists(bin_dir)

            dep_libs: list[str] = []
            for dep in target.dependencies:
                if dep in build_artifacts:
                    dep_libs.append(str(build_artifacts[dep]))

            link_flags: list[str] = []
            for sys_dep in target.system_dependencies:
                link_flags.extend(system_libs[sys_dep].link_flags)

            if Language.CXX in target.languages:
                cmd_list = [
                    build_env["CXXLD"],
                    "-o",
                    str(bin_dir / target.name),
                    *[
                        local_compile_command.output
                        for local_compile_command in local_compile_commands
                    ],
                    *dep_libs,
                    *link_flags,
                ]
                cxxld(f"{bin_dir / target.name}")

            else:
                cmd_list = [
                    build_env["CCLD"],
                    "-o",
                    str(bin_dir / target.name),
                    *[
                        local_compile_command.output
                        for local_compile_command in local_compile_commands
                    ],
                    *dep_libs,
                    *link_flags,
                ]
                ccld(f"{bin_dir / target.name}")

            result = run(cmd_list, capture_output=True)
            if result.returncode != 0:
                return 7, f"Linking failed: {result.stderr.decode()}"

            build_artifacts[target.name] = bin_dir / target.name
            compile_commands.extend(local_compile_commands)

        if isinstance(target, StaticLibrary):
            debug(f"Building static library {target.name}")

            if Language.C in target.languages:
                build_env.ensure_cc()

            if Language.CXX in target.languages:
                build_env.ensure_cc()
                build_env.ensure_cxx()

            build_env.ensure_ar()
            build_env.ensure_ranlib()

            int_dir = build_dir / target.name
            fs.create_dir_if_not_exists(int_dir)
            local_compile_commands: list[CompileCommand] = []
            public_defines = _collect_public_defines(target, targets)
            all_defines = target.defines + target.public_defines + public_defines
            for source in target.sources:
                source_path = cwd / source
                _temp = int_dir / source
                compile_command = CompileCommand()
                compile_command.directory = str(int_dir)
                compile_command.file = str(cwd / source)
                compile_command.output = str(
                    _temp.parent / ((int_dir / source).name + ".o")
                )

                if source_path.suffix == ".c":
                    compile_flags: list[str] = []
                    for sys_dep in target.system_dependencies:
                        compile_flags.extend(system_libs[sys_dep].compile_flags)

                    for define in all_defines:
                        compile_flags.append(_format_define(define))

                    compile_command.command = " ".join(
                        [
                            build_env["CC"],
                            *compile_flags,
                            "-c",
                            "-o",
                            compile_command.output,
                            compile_command.file,
                        ]
                    )
                    cc(f"{compile_command.file}")

                elif source_path.suffix in [".cpp", ".cxx", ".cc"]:
                    compile_flags: list[str] = []
                    for sys_dep in target.system_dependencies:
                        compile_flags.extend(system_libs[sys_dep].compile_flags)

                    for define in all_defines:
                        compile_flags.append(_format_define(define))

                    compile_command.command = " ".join(
                        [
                            build_env["CXX"],
                            *compile_flags,
                            "-c",
                            "-o",
                            compile_command.output,
                            compile_command.file,
                        ]
                    )
                    cxx(f"{compile_command.file}")

                cmd_list = split(compile_command.command)
                result = run(cmd_list, capture_output=True)
                if result.returncode != 0:
                    return 6, f"Compilation failed: {result.stderr.decode()}"

                local_compile_commands.append(compile_command)

            fs.create_dir_if_not_exists(lib_dir)
            cmd_list = [
                build_env["AR"],
                "-rc",
                str(lib_dir / f"{target.name}.a"),
                *[
                    local_compile_command.output
                    for local_compile_command in local_compile_commands
                ],
            ]

            ar(f"{lib_dir / f'{target.name}.a'}")
            result = run(cmd_list, capture_output=True)

            if result.returncode != 0:
                return 8, f"Archiving failed: {result.stderr.decode()}"

            cmd_list = [
                build_env["RANLIB"],
                str(lib_dir / f"{target.name}.a"),
            ]

            ranlib(f"{lib_dir / f'{target.name}.a'}")
            result = run(cmd_list, capture_output=True)

            if result.returncode != 0:
                return 9, f"Ranlib failed: {result.stderr.decode()}"

            build_artifacts[target.name] = lib_dir / f"{target.name}.a"
            compile_commands.extend(local_compile_commands)

        if isinstance(target, SharedLibrary):
            debug(f"Building shared library {target.name}")

            if Language.C in target.languages:
                build_env.ensure_cc()
                build_env.ensure_ccld()

            if Language.CXX in target.languages:
                build_env.ensure_cc()
                build_env.ensure_cxx()
                build_env.ensure_ccld()
                build_env.ensure_cxxld()

            int_dir = build_dir / target.name
            fs.create_dir_if_not_exists(int_dir)

            local_compile_commands: list[CompileCommand] = []
            public_defines = _collect_public_defines(target, targets)
            all_defines = target.defines + target.public_defines + public_defines
            for source in target.sources:
                source_path = cwd / source
                _temp = int_dir / source
                compile_command = CompileCommand()
                compile_command.directory = str(int_dir)
                compile_command.file = str(cwd / source)
                compile_command.output = str(
                    _temp.parent / ((int_dir / source).name + ".o")
                )

                if source_path.suffix == ".c":
                    compile_flags: list[str] = []
                    for sys_dep in target.system_dependencies:
                        compile_flags.extend(system_libs[sys_dep].compile_flags)

                    for define in all_defines:
                        compile_flags.append(_format_define(define))

                    compile_command.command = " ".join(
                        [
                            build_env["CC"],
                            *compile_flags,
                            "-fPIC",
                            "-c",
                            "-o",
                            compile_command.output,
                            compile_command.file,
                        ]
                    )
                    cc(f"{compile_command.file}")
                elif source_path.suffix in [".cpp", ".cxx", ".cc"]:
                    compile_flags: list[str] = []
                    for sys_dep in target.system_dependencies:
                        compile_flags.extend(system_libs[sys_dep].compile_flags)

                    for define in all_defines:
                        compile_flags.append(_format_define(define))

                    compile_command.command = " ".join(
                        [
                            build_env["CXX"],
                            *compile_flags,
                            "-fPIC",
                            "-c",
                            "-o",
                            compile_command.output,
                            compile_command.file,
                        ]
                    )
                    cxx(f"{compile_command.file}")

                cmd_list = split(compile_command.command)
                result = run(cmd_list, capture_output=True)
                if result.returncode != 0:
                    return 6, f"Compilation failed: {result.stderr.decode()}"

                local_compile_commands.append(compile_command)

            fs.create_dir_if_not_exists(lib_dir)

            dep_libs: list[str] = []
            for dep in target.dependencies:
                if dep in build_artifacts:
                    dep_libs.append(str(build_artifacts[dep]))

            link_flags: list[str] = []
            for sys_dep in target.system_dependencies:
                link_flags.extend(system_libs[sys_dep].link_flags)

            if Language.CXX in target.languages:
                cmd_list = [
                    build_env["CXXLD"],
                    "-shared",
                    "-o",
                    str(lib_dir / f"{target.name}.so"),
                    *[
                        local_compile_command.output
                        for local_compile_command in local_compile_commands
                    ],
                    *dep_libs,
                    *link_flags,
                ]
                cxxld(f"{lib_dir / f'{target.name}.so'}")
            else:
                cmd_list = [
                    build_env["CCLD"],
                    "-shared",
                    "-o",
                    str(lib_dir / f"{target.name}.so"),
                    *[
                        local_compile_command.output
                        for local_compile_command in local_compile_commands
                    ],
                    *dep_libs,
                    *link_flags,
                ]
                ccld(f"{lib_dir / f'{target.name}.so'}")

            result = run(cmd_list, capture_output=True)

            if result.returncode != 0:
                return 7, f"Linking failed: {result.stderr.decode()}"

            build_artifacts[target.name] = lib_dir / f"{target.name}.so"
            compile_commands.extend(local_compile_commands)

    debug("Writing compile_commands.json")

    with Path.open(build_dir / "compile_commands.json", "w") as f:
        f.write(json.dumps(compile_commands, indent=2))
        info("Wrote compile_commands.json")

    return 0, ""
