import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class SafeBuildError(Exception):
    pass


_SAFE_BUILTINS = {
    "None": None,
    "True": True,
    "False": False,
    "bool": bool,
    "int": int,
    "float": float,
    "str": str,
    "list": list,
    "tuple": tuple,
    "dict": dict,
    "set": set,
    "frozenset": frozenset,
    "bytes": bytes,
    "bytearray": bytearray,
    "complex": complex,
    "object": object,
    "type": type,
    "isinstance": isinstance,
    "issubclass": issubclass,
    "callable": callable,
    "len": len,
    "range": range,
    "enumerate": enumerate,
    "zip": zip,
    "map": map,
    "filter": filter,
    "reversed": reversed,
    "sorted": sorted,
    "any": any,
    "all": all,
    "sum": sum,
    "max": max,
    "min": min,
    "abs": abs,
    "round": round,
    "divmod": divmod,
    "pow": pow,
    "ord": ord,
    "chr": chr,
    "bin": bin,
    "hex": hex,
    "oct": oct,
    "ascii": ascii,
    "slice": slice,
    "iter": iter,
    "next": next,
    "hasattr": hasattr,
    "getattr": getattr,
    "setattr": setattr,
    "delattr": delattr,
    "id": id,
    "hash": hash,
    "repr": repr,
    "Exception": Exception,
    "TypeError": TypeError,
    "ValueError": ValueError,
    "KeyError": KeyError,
    "IndexError": IndexError,
    "AttributeError": AttributeError,
}


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

    byte_code = compile(tree, filename, mode="exec")

    restricted_namespace = {
        "__builtins__": _SAFE_BUILTINS,
        **namespace,
    }

    exec(byte_code, restricted_namespace)

    return restricted_namespace
