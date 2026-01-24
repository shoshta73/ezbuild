import json
import subprocess
from importlib.metadata import version
from pathlib import Path
from shutil import rmtree
from typing import Annotated

import typer

from ezbuild import CompileCommand, Environment, Language, log, utils

cli: typer.Typer = typer.Typer()


def version_callback(value: bool) -> None:
    if value:
        print(f"ezbuild {version('ezbuild')}")
        raise typer.Exit


@cli.command()
def init(
    name: Annotated[
        str | None, typer.Argument(help="Name of the project to initialize")
    ] = None,
) -> None:
    """Initialize a new project."""
    cwd = Path.cwd()
    if name is None:
        name = cwd.name

    log.info(f'Using "{name}" (name of current directory) as the project name')
    log.info(f'Using "{name}" as name of the executable to build')

    if any(cwd.iterdir()):
        log.error(f'Directory "{name}" is not empty')

    log.debug("Writing build.ezbuild")
    with Path.open(cwd / "build.ezbuild", "w") as f:
        f.write(f"""env = Environment()

{name} = env.Program(
    name='{name}',
    sources=['{name}.c'],
)
""")
        log.info("Wrote build.ezbuild")

    log.debug(f" Writing {name}.c")
    with Path.open(cwd / f"{name}.c", "w") as f:
        f.write("""#include <stdio.h>\n

int main() {
    printf("Hello, World!\\n");
    return 0;
}
""")
        log.info(f"Wrote {name}.c")


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
    exec(build_ezbuild, namespace)

    for var_name, value in namespace.items():
        if isinstance(value, Environment):
            log.info(f"Found environment: {var_name}")

            if (
                len(value.programs) == 0
                and len(value.static_libraries) == 0
                and len(value.shared_libraries) == 0
            ):
                log.error(f"Environment {var_name} has no buid targets")
                raise typer.Exit

            log.debug(f"Found {len(value.programs)} programs in environment {var_name}")
            utils.fs.create_dir_if_not_exists(build_dir)

            for program in value.programs:
                log.info(f"Building program {program.name}")

                if Language.C in program.languages:
                    value.ensure_cc()
                    value.ensure_ccld()

                if Language.CXX in program.languages:
                    value.ensure_cc()
                    value.ensure_cxx()
                    value.ensure_ccld()
                    value.ensure_cxxld()

                int_dir = build_dir / program.name
                utils.fs.create_dir_if_not_exists(int_dir)

                local_compile_commands: list[CompileCommand] = []
                for source in program.sources:
                    source_path = cwd / source
                    _temp = int_dir / source
                    compile_command = CompileCommand()
                    compile_command.directory = str(int_dir)
                    compile_command.file = str(cwd / source)
                    compile_command.output = str(
                        _temp.parent / ((int_dir / source).name + ".o")
                    )

                    if source_path.suffix == ".c":
                        compile_command.command = " ".join(
                            [
                                value["CC"],
                                "-c",
                                "-o",
                                compile_command.output,
                                compile_command.file,
                            ]
                        )
                        log.cc(f"{compile_command.file}")

                    elif source_path.suffix in [".cpp", ".cxx", ".cc"]:
                        compile_command.command = " ".join(
                            [
                                value["CXX"],
                                "-c",
                                "-o",
                                compile_command.output,
                                compile_command.file,
                            ]
                        )
                        log.cxx(f"{compile_command.file}")

                    result = subprocess.run(
                        compile_command.command, shell=True, capture_output=True
                    )
                    if result.returncode != 0:
                        log.error("Compilation failed")
                        log.debug(f"Error: {result.stderr.decode()}")

                        raise typer.Exit

                    local_compile_commands.append(compile_command)

                utils.fs.create_dir_if_not_exists(bin_dir)
                if Language.CXX in program.languages:
                    cmd = " ".join(
                        [
                            value["CXXLD"],
                            "-o",
                            str(bin_dir / program.name),
                            *[
                                local_compile_command.output
                                for local_compile_command in local_compile_commands
                            ],
                        ]
                    )
                    log.cxxld(f"{bin_dir / program.name}")

                else:
                    cmd = " ".join(
                        [
                            value["CCLD"],
                            "-o",
                            str(bin_dir / program.name),
                            *[
                                local_compile_command.output
                                for local_compile_command in local_compile_commands
                            ],
                        ]
                    )
                    log.ccld(f"{bin_dir / program.name}")

                result = subprocess.run(cmd, shell=True, capture_output=True)

                if result.returncode != 0:
                    log.error("Linking failed")
                    log.debug(f"Error: {result.stderr.decode()}")
                    raise typer.Exit

                compile_commands.extend(local_compile_commands)

            for static_library in value.static_libraries:
                log.info(f"Building static library {static_library.name}")

                if Language.C in static_library.languages:
                    value.ensure_cc()

                if Language.CXX in static_library.languages:
                    value.ensure_cc()
                    value.ensure_cxx()

                value.ensure_ar()
                value.ensure_ranlib()

                int_dir = build_dir / static_library.name
                utils.fs.create_dir_if_not_exists(int_dir)

                local_compile_commands: list[CompileCommand] = []
                for source in static_library.sources:
                    source_path = cwd / source
                    _temp = int_dir / source
                    compile_command = CompileCommand()
                    compile_command.directory = str(int_dir)
                    compile_command.file = str(cwd / source)
                    compile_command.output = str(
                        _temp.parent / ((int_dir / source).name + ".o")
                    )
                    if source_path.suffix == ".c":
                        compile_command.command = " ".join(
                            [
                                value["CC"],
                                "-c",
                                "-o",
                                compile_command.output,
                                compile_command.file,
                            ]
                        )
                        log.cc(f"{compile_command.file}")

                    elif source_path.suffix in [".cpp", ".cxx", ".cc"]:
                        compile_command.command = " ".join(
                            [
                                value["CXX"],
                                "-c",
                                "-o",
                                compile_command.output,
                                compile_command.file,
                            ]
                        )
                        log.cxx(f"{compile_command.file}")

                    result = subprocess.run(
                        compile_command.command, shell=True, capture_output=True
                    )
                    if result.returncode != 0:
                        log.error("Compilation failed")
                        log.debug(f"Error: {result.stderr.decode()}")

                        raise typer.Exit

                    local_compile_commands.append(compile_command)

                utils.fs.create_dir_if_not_exists(lib_dir)
                cmd = " ".join(
                    [
                        value["AR"],
                        "-rc",
                        str(lib_dir / f"{static_library.name}.a"),
                        *[
                            local_compile_command.output
                            for local_compile_command in local_compile_commands
                        ],
                    ]
                )

                log.ar(f"{lib_dir / f'{static_library.name}.a'}")
                result = subprocess.run(cmd, shell=True, capture_output=True)

                if result.returncode != 0:
                    log.error("Archiving failed")
                    log.debug(f"Error: {result.stderr.decode()}")
                    raise typer.Exit

                cmd = " ".join(
                    [
                        value["RANLIB"],
                        str(lib_dir / f"{static_library.name}.a"),
                    ]
                )

                log.ranlib(f"{lib_dir / f'{static_library.name}.a'}")
                result = subprocess.run(cmd, shell=True, capture_output=True)

                if result.returncode != 0:
                    log.error("Ranlib failed")
                    log.debug(f"Error: {result.stderr.decode()}")
                    raise typer.Exit

                compile_commands.extend(local_compile_commands)

            for shared_library in value.shared_libraries:
                log.info(f"Building shared library {shared_library.name}")

                if Language.C in shared_library.languages:
                    value.ensure_cc()
                    value.ensure_ccld()

                if Language.CXX in shared_library.languages:
                    value.ensure_cc()
                    value.ensure_cxx()
                    value.ensure_ccld()
                    value.ensure_cxxld()

                int_dir = build_dir / shared_library.name
                utils.fs.create_dir_if_not_exists(int_dir)

                local_compile_commands: list[CompileCommand] = []
                for source in shared_library.sources:
                    source_path = cwd / source
                    _temp = int_dir / source
                    compile_command = CompileCommand()
                    compile_command.directory = str(int_dir)
                    compile_command.file = str(cwd / source)
                    compile_command.output = str(
                        _temp.parent / ((int_dir / source).name + ".o")
                    )

                    if source_path.suffix == ".c":
                        compile_command.command = " ".join(
                            [
                                value["CC"],
                                "-fPIC",
                                "-c",
                                "-o",
                                compile_command.output,
                                compile_command.file,
                            ]
                        )
                        log.cc(f"{compile_command.file}")
                    elif source_path.suffix in [".cpp", ".cxx", ".cc"]:
                        compile_command.command = " ".join(
                            [
                                value["CXX"],
                                "-fPIC",
                                "-c",
                                "-o",
                                compile_command.output,
                                compile_command.file,
                            ]
                        )
                        log.cxx(f"{compile_command.file}")

                    result = subprocess.run(
                        compile_command.command, shell=True, capture_output=True
                    )
                    if result.returncode != 0:
                        log.error("Compilation failed")
                        log.debug(f"Error: {result.stderr.decode()}")

                        raise typer.Exit

                    local_compile_commands.append(compile_command)

                utils.fs.create_dir_if_not_exists(lib_dir)

                if Language.CXX in shared_library.languages:
                    cmd = " ".join(
                        [
                            value["CXXLD"],
                            "-shared",
                            "-o",
                            str(lib_dir / f"{shared_library.name}.so"),
                            *[
                                local_compile_command.output
                                for local_compile_command in local_compile_commands
                            ],
                        ]
                    )
                    log.cxxld(f"{lib_dir / f'{shared_library.name}.so'}")
                else:
                    cmd = " ".join(
                        [
                            value["CCLD"],
                            "-shared",
                            "-o",
                            str(lib_dir / f"{shared_library.name}.so"),
                            *[
                                local_compile_command.output
                                for local_compile_command in local_compile_commands
                            ],
                        ]
                    )
                    log.ccld(f"{lib_dir / f'{shared_library.name}.so'}")

                result = subprocess.run(cmd, shell=True, capture_output=True)

                if result.returncode != 0:
                    log.error("Linking failed")
                    log.debug(f"Error: {result.stderr.decode()}")
                    raise typer.Exit

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
    result = subprocess.run(cmd, shell=True)

    if result.returncode != 0:
        log.error("Running failed")
        log.debug(f"Error: {result.stderr.decode()}")
        raise typer.Exit


@cli.command()
def clean():
    """Clean the project."""
    cwd = Path.cwd()
    build_dir = cwd / "build"
    if not build_dir.exists():
        log.info("Nothing to clean")
        raise typer.Exit(0)

    log.info("Cleaning build directory")
    rmtree(build_dir)
    log.info("Cleaned build directory")


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
