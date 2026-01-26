import pytest

from ezbuild import Environment, Language, SafeBuildError, safe_execute


def test_safe_execute_valid_build_file() -> None:
    build_code = """env = Environment()
myapp = env.Program(
    name='myapp',
    languages=[Language.C],
    sources=['main.c'],
)"""

    namespace = {"Environment": Environment, "Language": Language}
    result = safe_execute(build_code, namespace)

    assert "env" in result
    assert "myapp" in result


def test_safe_execute_multiple_targets() -> None:
    build_code = """env = Environment()
myapp = env.Program(
    name='myapp',
    languages=[Language.C],
    sources=['main.c'],
)
mylib = env.StaticLibrary(
    name='mylib',
    languages=[Language.C],
    sources=['lib.c'],
)"""

    namespace = {"Environment": Environment, "Language": Language}
    result = safe_execute(build_code, namespace)

    assert "env" in result
    assert "myapp" in result
    assert "mylib" in result


def test_safe_execute_shared_library() -> None:
    build_code = """env = Environment()
mylib = env.SharedLibrary(
    name='mylib',
    languages=[Language.CXX],
    sources=['lib.cpp'],
)"""

    namespace = {"Environment": Environment, "Language": Language}
    result = safe_execute(build_code, namespace)

    assert "env" in result
    assert "mylib" in result


def test_safe_execute_with_dependencies() -> None:
    build_code = """env = Environment()
mylib = env.StaticLibrary(
    name='mylib',
    languages=[Language.C],
    sources=['lib.c'],
)
myapp = env.Program(
    name='myapp',
    languages=[Language.C],
    sources=['main.c'],
    dependencies=['mylib'],
)"""

    namespace = {"Environment": Environment, "Language": Language}
    result = safe_execute(build_code, namespace)

    assert "env" in result
    assert "mylib" in result
    assert "myapp" in result


def test_safe_execute_syntax_error() -> None:
    build_code = """env = Environment(
    # Missing closing parenthesis"""

    namespace = {"Environment": Environment, "Language": Language}

    with pytest.raises(SafeBuildError, match=r"Syntax error in build\.ezbuild"):
        safe_execute(build_code, namespace)


def test_safe_execute_import_blocked() -> None:
    build_code = """import os
env = Environment()"""

    namespace = {"Environment": Environment, "Language": Language}

    with pytest.raises(SafeBuildError, match="Imports are not allowed"):
        safe_execute(build_code, namespace)


def test_safe_execute_from_import_blocked() -> None:
    build_code = """from os import path
env = Environment()"""

    namespace = {"Environment": Environment, "Language": Language}

    with pytest.raises(SafeBuildError, match="Imports are not allowed"):
        safe_execute(build_code, namespace)


def test_safe_execute_exec_blocked() -> None:
    build_code = """exec('print("hello")')"""

    namespace = {"Environment": Environment, "Language": Language}

    with pytest.raises(SafeBuildError, match="Calling exec\\(\\) is not allowed"):
        safe_execute(build_code, namespace)


def test_safe_execute_eval_blocked() -> None:
    build_code = """eval('1 + 1')"""

    namespace = {"Environment": Environment, "Language": Language}

    with pytest.raises(SafeBuildError, match="Calling eval\\(\\) is not allowed"):
        safe_execute(build_code, namespace)


def test_safe_execute_compile_blocked() -> None:
    build_code = """compile('print(1)', 'test', 'exec')"""

    namespace = {"Environment": Environment, "Language": Language}

    with pytest.raises(SafeBuildError, match="Calling compile\\(\\) is not allowed"):
        safe_execute(build_code, namespace)


def test_safe_execute_open_blocked() -> None:
    build_code = """open('/etc/passwd')"""

    namespace = {"Environment": Environment, "Language": Language}

    with pytest.raises(SafeBuildError, match="Calling open\\(\\) is not allowed"):
        safe_execute(build_code, namespace)


def test_safe_execute_exit_blocked() -> None:
    build_code = """exit()"""

    namespace = {"Environment": Environment, "Language": Language}

    with pytest.raises(SafeBuildError, match="Calling exit\\(\\) is not allowed"):
        safe_execute(build_code, namespace)


def test_safe_execute_quit_blocked() -> None:
    build_code = """quit()"""

    namespace = {"Environment": Environment, "Language": Language}

    with pytest.raises(SafeBuildError, match="Calling quit\\(\\) is not allowed"):
        safe_execute(build_code, namespace)


def test_safe_execute_function_definition_blocked() -> None:
    build_code = """def my_function():
    pass"""

    namespace = {"Environment": Environment, "Language": Language}

    with pytest.raises(SafeBuildError, match="Function definitions are not allowed"):
        safe_execute(build_code, namespace)


def test_safe_execute_class_definition_blocked() -> None:
    build_code = """class MyClass:
    pass"""

    namespace = {"Environment": Environment, "Language": Language}

    with pytest.raises(SafeBuildError, match="Class definitions are not allowed"):
        safe_execute(build_code, namespace)


def test_safe_execute_dunder_assignment_blocked() -> None:
    build_code = """__builtins__ = {}"""

    namespace = {"Environment": Environment, "Language": Language}

    with pytest.raises(
        SafeBuildError, match="Assigning to __builtins__ is not allowed"
    ):
        safe_execute(build_code, namespace)


def test_safe_execute_custom_dunder_assignment_blocked() -> None:
    build_code = """__custom__ = 123"""

    namespace = {"Environment": Environment, "Language": Language}

    with pytest.raises(SafeBuildError, match="Assigning to __custom__ is not allowed"):
        safe_execute(build_code, namespace)


def test_safe_execute_list_and_dict_allowed() -> None:
    build_code = """sources_list = ['main.c', 'utils.c']
sources_dict = {'main': 'main.c', 'utils': 'utils.c'}
env = Environment()"""

    namespace = {"Environment": Environment, "Language": Language}
    result = safe_execute(build_code, namespace)

    assert "sources_list" in result
    assert "sources_dict" in result
    assert "env" in result


def test_safe_execute_constant_allowed() -> None:
    build_code = """my_string = "hello"
my_int = 42
my_bool = True
env = Environment()"""

    namespace = {"Environment": Environment, "Language": Language}
    result = safe_execute(build_code, namespace)

    assert "my_string" in result
    assert "my_int" in result
    assert "my_bool" in result
    assert "env" in result


def test_safe_execute_empty_file() -> None:
    build_code = ""

    namespace = {"Environment": Environment, "Language": Language}
    result = safe_execute(build_code, namespace)

    assert "Environment" in result
    assert "Language" in result


def test_safe_execute_preserves_namespace() -> None:
    build_code = """env = Environment()
myapp = env.Program(
    name='myapp',
    languages=[Language.C],
    sources=['main.c'],
)"""

    def custom_func() -> str:
        return "test"

    namespace = {
        "Environment": Environment,
        "Language": Language,
        "custom_func": custom_func,
    }
    result = safe_execute(build_code, namespace)

    assert "Environment" in result
    assert "Language" in result
    assert "custom_func" in result
    assert "env" in result
    assert "myapp" in result


def test_safe_execute_multiline_string() -> None:
    build_code = """env = Environment()
myapp = env.Program(
    name='myapp',
    languages=[Language.C],
    sources=[
        'main.c',
        'utils.c',
        'lib.c',
    ],
)"""

    namespace = {"Environment": Environment, "Language": Language}
    result = safe_execute(build_code, namespace)

    assert "env" in result
    assert "myapp" in result


@pytest.mark.parametrize(
    "lang_value,expected_enum",
    [
        ("Language.C", Language.C),
        ("Language.CXX", Language.CXX),
    ],
)
def test_safe_execute_language_enum(
    lang_value: str, expected_enum: type[Language]
) -> None:
    build_code = f"""env = Environment()
myapp = env.Program(
    name='myapp',
    languages=[{lang_value}],
    sources=['main.c'],
)"""

    namespace = {"Environment": Environment, "Language": Language}
    result = safe_execute(build_code, namespace)

    assert "myapp" in result
