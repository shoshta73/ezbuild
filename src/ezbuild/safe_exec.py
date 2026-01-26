import ast
from typing import TYPE_CHECKING

from RestrictedPython import compile_restricted, safe_builtins

if TYPE_CHECKING:
    from typing import Any


class SafeBuildError(Exception):
    pass


def _validate_ast(node: ast.AST) -> None:
    allowed_nodes = {
        ast.Module,
        ast.Expr,
        ast.Assign,
        ast.Call,
        ast.Name,
        ast.Constant,
        ast.List,
        ast.Dict,
        ast.keyword,
        ast.Attribute,
    }

    for child in ast.walk(node):
        child_type = type(child)

        if child_type not in allowed_nodes:
            if child_type in (ast.Import, ast.ImportFrom):
                raise SafeBuildError("Imports are not allowed in build.ezbuild")
            if child_type == ast.FunctionDef:
                raise SafeBuildError(
                    "Function definitions are not allowed in build.ezbuild"
                )
            if child_type == ast.ClassDef:
                raise SafeBuildError(
                    "Class definitions are not allowed in build.ezbuild"
                )

        if (
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Name)
            and child.func.id
            in {
                "exec",
                "eval",
                "compile",
                "open",
                "__import__",
                "exit",
                "quit",
            }
        ):
            raise SafeBuildError(f"Calling {child.func.id}() is not allowed")

        if (
            isinstance(child, ast.Name)
            and isinstance(child.ctx, ast.Store)
            and child.id.startswith("__")
            and child.id.endswith("__")
        ):
            raise SafeBuildError(f"Assigning to {child.id} is not allowed")


def safe_execute(
    build_code: str,
    namespace: dict[str, Any],
    filename: str = "build.ezbuild",
) -> dict[str, Any]:
    try:
        tree = ast.parse(build_code, filename)
    except SyntaxError as e:
        raise SafeBuildError(f"Syntax error in build.ezbuild: {e}") from e

    _validate_ast(tree)

    byte_code = compile_restricted(build_code, filename=filename, mode="exec")

    if byte_code is None:
        raise SafeBuildError("RestrictedPython compilation failed")

    restricted_namespace = {
        "__builtins__": safe_builtins,
        **namespace,
    }

    exec(byte_code, restricted_namespace)

    return restricted_namespace
