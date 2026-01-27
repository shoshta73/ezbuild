import re
import sys
from pathlib import Path

PYPROJECT_PATH = Path(__file__).parent.parent / "pyproject.toml"
INIT_PATH = Path(__file__).parent.parent / "src" / "ezbuild" / "__init__.py"


def get_current_version():
    """Read current version from pyproject.toml."""
    content = PYPROJECT_PATH.read_text()
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        print("Error: Could not find version in pyproject.toml")
        sys.exit(1)
    return match.group(1)


def parse_version(version_str):
    """Parse semver string into (major, minor, patch) tuple."""
    parts = version_str.split(".")
    if len(parts) != 3:
        print(f"Error: Invalid version format: {version_str}")
        sys.exit(1)
    return int(parts[0]), int(parts[1]), int(parts[2])


def bump_version(major, minor, patch, bump_type):
    """Bump version based on type."""
    if bump_type == "major":
        return major + 1, 0, 0
    elif bump_type == "minor":
        return major, minor + 1, 0
    elif bump_type == "patch":
        return major, minor, patch + 1
    else:
        print(f"Error: Unknown bump type: {bump_type}")
        sys.exit(1)


def update_pyproject(old_version, new_version):
    """Update version in pyproject.toml."""
    content = PYPROJECT_PATH.read_text()
    content = re.sub(
        rf'^version\s*=\s*"{re.escape(old_version)}"',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE,
    )
    PYPROJECT_PATH.write_text(content)


def update_init(old_version, new_version):
    """Update __version__ in __init__.py."""
    content = INIT_PATH.read_text()
    content = re.sub(
        rf'^__version__\s*=\s*"{re.escape(old_version)}"',
        f'__version__ = "{new_version}"',
        content,
        flags=re.MULTILINE,
    )
    INIT_PATH.write_text(content)


def main():
    if len(sys.argv) < 2:
        print("Usage: python version.py <major|minor|patch>")
        sys.exit(1)

    bump_type = sys.argv[1]
    if bump_type not in ("major", "minor", "patch"):
        print("Usage: python version.py <major|minor|patch>")
        sys.exit(1)

    old_version = get_current_version()
    major, minor, patch = parse_version(old_version)
    new_major, new_minor, new_patch = bump_version(major, minor, patch, bump_type)
    new_version = f"{new_major}.{new_minor}.{new_patch}"

    print(f"Bumping version: {old_version} -> {new_version}")

    update_pyproject(old_version, new_version)
    update_init(old_version, new_version)

    print("Updated pyproject.toml and src/ezbuild/__init__.py")


if __name__ == "__main__":
    main()
