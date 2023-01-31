import ast
from enum import Enum, unique
import sys
from typing import Any, Generator, List, Optional, Tuple, Type

__version__ = "0.2.0"


@unique
class ErrorType(Enum):
    DGC1001 = "DGC1001"
    DGC1002 = "DGC1002"


ERR_MSGS = {
    ErrorType.DGC1001: "missing default argument when chaining dict.get()",
    ErrorType.DGC1002: "invalid default argument when chaining dict.get()",
}


def call_position(call: ast.Call) -> Tuple[int, Optional[int]]:
    if sys.version_info < (3, 8):
        return call.lineno, call.col_offset  # pragma: no coverage
    return call.lineno, call.end_col_offset  # pragma: no coverage


class GetChainingChecker:
    name = "flake8-get-chaining"
    version = __version__

    def __init__(self, tree: ast.AST) -> None:
        self._tree = tree

    def run(self) -> Generator[Tuple[int, Optional[int], str, Type[Any]], None, None]:
        visitor = GetChainingVisitor()
        visitor.visit(self._tree)

        for err, lineno, col in visitor.issues:
            yield lineno, col, f"{err.value} {ERR_MSGS[err]}", type(self)


class GetChainingVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.issues: List[Tuple[ErrorType, int, Optional[int]]] = []

    def visit_Call(self, node: ast.Call) -> Any:

        if not isinstance(node.func, ast.Attribute) or node.func.attr != "get":
            return self.generic_visit(node)

        get_call = node.func.value
        if (
            not isinstance(get_call, ast.Call)
            or not isinstance(get_call.func, ast.Attribute)
            or get_call.func.attr != "get"
        ):
            return self.generic_visit(node)

        if len(get_call.args) > 1:
            arg = get_call.args[1]
            if not isinstance(arg, ast.Dict) and not (
                isinstance(arg, ast.Name) and arg.id.isidentifier()
            ):
                self.issues.append((ErrorType.DGC1002, *call_position(get_call)))
        elif get_call.keywords:
            for kw in get_call.keywords:
                if kw.arg == "default":
                    if not isinstance(kw.value, ast.Dict) and not (
                        isinstance(kw.value, ast.Name) and kw.value.id.isidentifier()
                    ):
                        self.issues.append(
                            (ErrorType.DGC1002, *call_position(get_call))
                        )
                    return self.generic_visit(node)
            self.issues.append((ErrorType.DGC1001, *call_position(get_call)))
        else:
            self.issues.append((ErrorType.DGC1001, *call_position(get_call)))
        return self.generic_visit(node)
