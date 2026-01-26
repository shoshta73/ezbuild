# ezbuild

> Simple Build System

![Python Version](https://img.shields.io/badge/python-3.14%2B-blue)
![License](https://img.shields.io/badge/license-BSD--3--Clause-blue)
![Status](https://img.shields.io/badge/status-development-yellow)

## Installation

> [!CAUTION]
> global installation is strongly discouraged, but it is possible to install ezbuild globally

### Using pip and venv

```bash
python3 -m venv .venv
source .venv/bin/activate
echo "ezbuild" >> requirements.txt
pip install -r requirements.txt
```

### using uv

```bash
uv venv
echo "ezbuild" >> requirements.txt
pip install -r requirements.txt
```

### Global installation

#### Using pip

> [!IMPORTANT]
> DO NOT RUN PIP AS ROOT
> see this for more information: <https://github.com/pypa/pip/pull/9394>

```bash
pip install ezbuild
```

#### Using pipx

```bash
pipx install ezbuild
```

#### using uv

```bash
uv tool install ezbuild
```

## Status

This project is in active development and is not yet stable, but

> [!CAUTION]
> It is usable for building C and C++ projects. Note that some basic features are not yet implemented (e.g., compiler/linker flags, C/C++ version specifications).

## Changelog

For a detailed history of changes, see the [CHANGELOG](./CHANGELOG.md).

## License

ezbuild is licensed under the [BSD-3-Clause](https://opensource.org/licenses/BSD-3-Clause) license,
for more information see the [LICENSE](./LICENSE) file.
