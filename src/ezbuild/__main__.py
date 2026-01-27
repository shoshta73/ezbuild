import json
import subprocess
from importlib.metadata import version
from pathlib import Path
from typing import Annotated

import typer

from ezbuild import (
    CompileCommand,
    CyclicDependencyError,
    DepTree,
    Environment,
    Language,
    Program,
    SafeBuildError,
    SharedLibrary,
    StaticLibrary,
    SystemLibrary,
    Target,
    commands,
    log,
    pkg_config,
    safe_execute,
    utils,
)

cli: typer.Typer = typer.Typer()


def version_callback(value: bool) -> None:
    if value:
        print(f"ezbuild {version('ezbuild')}")
        raise typer.Exit


@cli.command()
def init(
    language: Annotated[
        str | None, typer.Option("--language", "-l", help="Language which is used")
    ] = None,
    name: Annotated[
        str | None, typer.Argument(help="Name of the project to initialize")
    ] = None,
) -> None:
    """Initialize a new project."""
    exit_code, message = commands.init(language=language, name=name)
    if exit_code != 0:
        log.error(message)
    raise typer.Exit(exit_code)


@cli.command()
def build(
    name: Annotated[
        str | None, typer.Argument(help="Name of the project to initialize")
    ] = None,
) -> None:
    """Build the project."""
    cwd = Path.cwd()
    build_dir = cwd / "build"
    bin_dir = build_dir / "bin"
    lib_dir = build_dir / "lib"
    compile_commands: list[CompileCommand] = []

    if not (cwd / "build.ezbuild").exists():
        log.error("build.ezbuild does not exist")
        raise typer.Exit

    log.debug("Reading build.ezbuild")

    with Path.open(cwd / "build.ezbuild", "r") as f:
        build_ezbuild = f.read()

    namespace: dict[str, object] = {
        "Environment": Environment,
        "Language": Language,
    }
    log.debug("Executing build.ezbuild")
    try:
        namespace = safe_execute(build_ezbuild, namespace)
    except SafeBuildError as e:
        log.error(f"Build file validation failed: {e}")
        raise typer.Exit(1) from e

    build_env: Environment | None = None
    targets: dict[str, Target] = {}

    for var_name, value in namespace.items():
        if isinstance(value, Environment):
            log.info(f"Found environment: {var_name}")
            build_env = value

        if isinstance(value, Program):
            log.info(f"Found program target: {var_name}")
            targets[var_name] = value

        if isinstance(value, StaticLibrary):
            log.info(f"Found static library target: {var_name}")
            targets[var_name] = value

        if isinstance(value, SharedLibrary):
            log.info(f"Found shared library target: {var_name}")
            targets[var_name] = value

    if build_env is None:
        log.error("No build environment found")
        raise typer.Exit(1)

    if len(targets) == 0:
        log.error("No targets found")
        raise typer.Exit(1)

    utils.fs.create_dir_if_not_exists(build_dir)

    try:
        dep_tree = DepTree(targets)
        build_order = dep_tree.get_build_order()
    except CyclicDependencyError as e:
        log.error(str(e))
        raise typer.Exit(1) from e

    build_artifacts: dict[str, Path] = {}

    # Resolve system dependencies
    system_libs: dict[str, SystemLibrary] = {}
    for target in build_order:
        for sys_dep in target.system_dependencies:
            if sys_dep not in system_libs:
                system_libs[sys_dep] = pkg_config.query_package(sys_dep)

    for target in build_order:
        log.info(f"Building {target.name}")
        if isinstance(target, Program):
            log.debug(f"Building program {target.name}")

            if Language.C in target.languages:
                build_env.ensure_cc()
                build_env.ensure_ccld()

            if Language.CXX in target.languages:
                build_env.ensure_cc()
                build_env.ensure_cxx()
                build_env.ensure_ccld()
                build_env.ensure_cxxld()

            int_dir = build_dir / target.name
            utils.fs.create_dir_if_not_exists(int_dir)

            local_compile_commands: list[CompileCommand] = []
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
                    log.cc(f"{compile_command.file}")

                elif source_path.suffix in [".cpp", ".cxx", ".cc"]:
                    compile_flags: list[str] = []
                    for sys_dep in target.system_dependencies:
                        compile_flags.extend(system_libs[sys_dep].compile_flags)

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
                    log.cxx(f"{compile_command.file}")

                cmd_list = compile_command.command.split()
                result = subprocess.run(cmd_list, capture_output=True)
                if result.returncode != 0:
                    log.error("Compilation failed")
                    log.debug(f"Error: {result.stderr.decode()}")

                    raise typer.Exit

                local_compile_commands.append(compile_command)

            utils.fs.create_dir_if_not_exists(bin_dir)

            # Collect dependency libraries
            dep_libs: list[str] = []
            for dep in target.dependencies:
                if dep in build_artifacts:
                    dep_libs.append(str(build_artifacts[dep]))

            # Collect system library link flags
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
                log.cxxld(f"{bin_dir / target.name}")

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
                log.ccld(f"{bin_dir / target.name}")

            result = subprocess.run(cmd_list, capture_output=True)

            if result.returncode != 0:
                log.error("Linking failed")
                log.debug(f"Error: {result.stderr.decode()}")
                raise typer.Exit

            build_artifacts[target.name] = bin_dir / target.name
            compile_commands.extend(local_compile_commands)

        if isinstance(target, StaticLibrary):
            log.debug(f"Building static library {target.name}")

            if Language.C in target.languages:
                build_env.ensure_cc()

            if Language.CXX in target.languages:
                build_env.ensure_cc()
                build_env.ensure_cxx()

            build_env.ensure_ar()
            build_env.ensure_ranlib()

            int_dir = build_dir / target.name
            utils.fs.create_dir_if_not_exists(int_dir)

            local_compile_commands: list[CompileCommand] = []
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
                    log.cc(f"{compile_command.file}")

                elif source_path.suffix in [".cpp", ".cxx", ".cc"]:
                    compile_flags: list[str] = []
                    for sys_dep in target.system_dependencies:
                        compile_flags.extend(system_libs[sys_dep].compile_flags)

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
                    log.cxx(f"{compile_command.file}")

                cmd_list = compile_command.command.split()
                result = subprocess.run(cmd_list, capture_output=True)
                if result.returncode != 0:
                    log.error("Compilation failed")
                    log.debug(f"Error: {result.stderr.decode()}")

                    raise typer.Exit

                local_compile_commands.append(compile_command)

            utils.fs.create_dir_if_not_exists(lib_dir)
            cmd_list = [
                build_env["AR"],
                "-rc",
                str(lib_dir / f"{target.name}.a"),
                *[
                    local_compile_command.output
                    for local_compile_command in local_compile_commands
                ],
            ]

            log.ar(f"{lib_dir / f'{target.name}.a'}")
            result = subprocess.run(cmd_list, capture_output=True)

            if result.returncode != 0:
                log.error("Archiving failed")
                log.debug(f"Error: {result.stderr.decode()}")
                raise typer.Exit

            cmd_list = [
                build_env["RANLIB"],
                str(lib_dir / f"{target.name}.a"),
            ]

            log.ranlib(f"{lib_dir / f'{target.name}.a'}")
            result = subprocess.run(cmd_list, capture_output=True)

            if result.returncode != 0:
                log.error("Ranlib failed")
                log.debug(f"Error: {result.stderr.decode()}")
                raise typer.Exit

            build_artifacts[target.name] = lib_dir / f"{target.name}.a"
            compile_commands.extend(local_compile_commands)

        if isinstance(target, SharedLibrary):
            log.debug(f"Building shared library {target.name}")

            if Language.C in target.languages:
                build_env.ensure_cc()
                build_env.ensure_ccld()

            if Language.CXX in target.languages:
                build_env.ensure_cc()
                build_env.ensure_cxx()
                build_env.ensure_ccld()
                build_env.ensure_cxxld()

            int_dir = build_dir / target.name
            utils.fs.create_dir_if_not_exists(int_dir)

            local_compile_commands: list[CompileCommand] = []
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
                    log.cc(f"{compile_command.file}")
                elif source_path.suffix in [".cpp", ".cxx", ".cc"]:
                    compile_flags: list[str] = []
                    for sys_dep in target.system_dependencies:
                        compile_flags.extend(system_libs[sys_dep].compile_flags)

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
                    log.cxx(f"{compile_command.file}")

                cmd_list = compile_command.command.split()
                result = subprocess.run(cmd_list, capture_output=True)
                if result.returncode != 0:
                    log.error("Compilation failed")
                    log.debug(f"Error: {result.stderr.decode()}")

                    raise typer.Exit

                local_compile_commands.append(compile_command)

            utils.fs.create_dir_if_not_exists(lib_dir)

            # Collect dependency libraries
            dep_libs: list[str] = []
            for dep in target.dependencies:
                if dep in build_artifacts:
                    dep_libs.append(str(build_artifacts[dep]))

            # Collect system library link flags
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
                log.cxxld(f"{lib_dir / f'{target.name}.so'}")
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
                log.ccld(f"{lib_dir / f'{target.name}.so'}")

            result = subprocess.run(cmd_list, capture_output=True)

            if result.returncode != 0:
                log.error("Linking failed")
                log.debug(f"Error: {result.stderr.decode()}")
                raise typer.Exit

            build_artifacts[target.name] = lib_dir / f"{target.name}.so"
            compile_commands.extend(local_compile_commands)

    log.debug("Writing compile_commands.json")

    with Path.open(build_dir / "compile_commands.json", "w") as f:
        f.write(json.dumps(compile_commands, indent=2))
        log.info("Wrote compile_commands.json")


@cli.command()
def run(
    name: Annotated[str, typer.Argument(help="Name of the project to initialize")],
) -> None:
    """Run the project."""
    cwd = Path.cwd()
    build_dir = cwd / "build"
    bin_dir = build_dir / "bin"

    if not (bin_dir / name).exists():
        build(name=name)

    cmd = f"{bin_dir / name}"
    log.debug(f"Running {cmd}")
    result = subprocess.run([str(bin_dir / name)])

    if result.returncode != 0:
        log.error("Running failed")
        log.debug(f"Error: {result.stderr.decode()}")
        raise typer.Exit


@cli.command()
def clean():
    """Clean the project."""
    commands.clean()


@cli.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", "-V", callback=version_callback, is_eager=True),
    ] = False,
) -> None:
    """Simple Build System."""
    if ctx.invoked_subcommand is None:
        build()


if __name__ == "__main__":
    cli()
