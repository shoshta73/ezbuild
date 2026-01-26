import subprocess
from shutil import which
from sys import platform
from typing import TYPE_CHECKING

from ezbuild.log import debug, error

if TYPE_CHECKING:
    from ezbuild.environment import SystemLibrary


def is_available() -> bool:
    """Check if pkg-config is installed (Unix only)."""
    if platform not in ["linux", "darwin"]:
        return False

    return which("pkg-config") is not None


def query_package(package: str) -> SystemLibrary:
    """Query pkg-config for compile and link flags."""
    from ezbuild.environment import SystemLibrary

    if not is_available():
        error("pkg-config is not available")
        raise RuntimeError("pkg-config is not available")

    debug(f"Querying pkg-config for {package}")

    try:
        cflags_result = subprocess.run(
            ["pkg-config", "--cflags", package],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        error(f"pkg-config --cflags {package} failed")
        error(f"Error: {e.stderr.decode()}")
        raise RuntimeError(f"pkg-config: package '{package}' not found") from e

    try:
        libs_result = subprocess.run(
            ["pkg-config", "--libs", package],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        error(f"pkg-config --libs {package} failed")
        error(f"Error: {e.stderr.decode()}")
        raise RuntimeError(f"pkg-config: package '{package}' not found") from e

    compile_flags = cflags_result.stdout.decode().strip().split()
    link_flags = libs_result.stdout.decode().strip().split()

    debug(f"Compile flags for {package}: {compile_flags}")
    debug(f"Link flags for {package}: {link_flags}")

    return SystemLibrary(
        name=package,
        compile_flags=compile_flags,
        link_flags=link_flags,
    )


def query_multiple_packages(packages: list[str]) -> dict[str, SystemLibrary]:
    """Query multiple packages at once."""
    system_libs: dict[str, SystemLibrary] = {}

    for package in packages:
        if package not in system_libs:
            system_libs[package] = query_package(package)

    return system_libs
