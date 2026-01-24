import json

from ezbuild.compile_command import CompileCommand


def test_default_values() -> None:
    cmd = CompileCommand()
    assert cmd.directory == ""
    assert cmd.command == ""
    assert cmd.file == ""
    assert cmd.output == ""


def test_custom_values() -> None:
    cmd = CompileCommand(
        directory="/build",
        command="gcc -c main.c",
        file="main.c",
        output="main.o",
    )
    assert cmd.directory == "/build"
    assert cmd.command == "gcc -c main.c"
    assert cmd.file == "main.c"
    assert cmd.output == "main.o"


def test_partial_values() -> None:
    cmd = CompileCommand(directory="/build", file="main.c")
    assert cmd.directory == "/build"
    assert cmd.command == ""
    assert cmd.file == "main.c"
    assert cmd.output == ""


def test_directory_setter() -> None:
    cmd = CompileCommand()
    cmd.directory = "/new/path"
    assert cmd.directory == "/new/path"
    assert cmd["directory"] == "/new/path"


def test_command_setter() -> None:
    cmd = CompileCommand()
    cmd.command = "clang++ -c file.cpp"
    assert cmd.command == "clang++ -c file.cpp"
    assert cmd["command"] == "clang++ -c file.cpp"


def test_file_setter() -> None:
    cmd = CompileCommand()
    cmd.file = "source.cpp"
    assert cmd.file == "source.cpp"
    assert cmd["file"] == "source.cpp"


def test_output_setter() -> None:
    cmd = CompileCommand()
    cmd.output = "source.o"
    assert cmd.output == "source.o"
    assert cmd["output"] == "source.o"


def test_dict_access() -> None:
    cmd = CompileCommand(directory="/build", command="gcc main.c")
    assert cmd["directory"] == "/build"
    assert cmd["command"] == "gcc main.c"


def test_dict_keys() -> None:
    cmd = CompileCommand()
    assert set(cmd.keys()) == {"directory", "command", "file", "output"}


def test_dict_values() -> None:
    cmd = CompileCommand(
        directory="/build",
        command="gcc main.c",
        file="main.c",
        output="main.o",
    )
    assert list(cmd.values()) == ["/build", "gcc main.c", "main.c", "main.o"]


def test_json_serialization() -> None:
    cmd = CompileCommand(
        directory="/build",
        command="gcc -c main.c",
        file="main.c",
        output="main.o",
    )
    json_str = json.dumps(cmd)
    parsed = json.loads(json_str)
    assert parsed == {
        "directory": "/build",
        "command": "gcc -c main.c",
        "file": "main.c",
        "output": "main.o",
    }


def test_iteration() -> None:
    cmd = CompileCommand()
    keys = list(cmd)
    assert set(keys) == {"directory", "command", "file", "output"}


def test_len() -> None:
    cmd = CompileCommand()
    assert len(cmd) == 4
