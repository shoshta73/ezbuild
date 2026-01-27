from pathlib import Path
from typing import Annotated

from typer import Argument, Option, prompt

from ezbuild import Language
from ezbuild.log import debug, info


def init(
    language: Annotated[
        str | None, Option("--language", "-l", help="Language which is used")
    ] = None,
    name: Annotated[
        str | None, Argument(help="Name of the project to initialize")
    ] = None,
) -> tuple[int, str]:
    """Initialize a new project."""

    cwd = Path.cwd()
    if any(cwd.iterdir()):
        return 1, f"Directory {cwd.name} is not empty"

    name = prompt("Project name", type=str, default=cwd.name) if name is None else name

    if language is None:
        lang = prompt("Language which is used", type=Language, default=Language.C)
    elif language not in ["c", "cxx", "c++", "cc", "cpp"]:
        return 2, f"Unsupported language: {language}"
    else:
        lang = Language.CXX if language in ["cxx", "c++", "cc", "cpp"] else Language.C

    info(f"Using {name} as the project name")
    info(f"Using {lang.name} as the language")

    debug("Writing build.ezbuild")
    with (cwd / "build.ezbuild").open("w") as f:
        f.write(f"""env = Environment()

{name} = env.Program(
    name='{name}',
    languages=[Language.{lang.name}],
    sources=['{name}.{lang.value}'],
)
""")

        info("Wrote build.ezbuild")

    if lang == Language.C:
        debug(f"Writing {name}.c")
        with (cwd / f"{name}.c").open("w") as f:
            f.write("""#include <stdio.h>

int main() {
    printf("Hello, World!\\n");
    return 0;
}
""")

        info(f"Wrote {name}.c")
    elif lang == Language.CXX:
        debug(f"Writing {name}.cxx")
        with (cwd / f"{name}.cxx").open("w") as f:
            f.write("""#include <iostream>

int main() {
    std::cout << "Hello, World!\\n";
    return 0;
}
""")
        info(f"Wrote {name}.cxx")

    return 0, ""
