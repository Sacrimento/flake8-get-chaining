import ast
import sys
from typing import List

import pytest

from get_chaining import ERR_MSG, GetChainingChecker

EXPECTED_ERR_MSG = f"DGC1001 {ERR_MSG}"


def _gl(line_col):
    if sys.version_info < (3, 8):
        return "1:0"  # pragma: no coverage
    return line_col  # pragma: no coverage


def _results(code: str) -> List[str]:
    tree = ast.parse(code)
    checker = GetChainingChecker(tree)
    return [f"{line}:{col} {msg}" for line, col, msg, _ in checker.run()]


@pytest.mark.parametrize(
    "inp",
    [
        "",
        'test.do("nothing")',
        'test.get("test")',
        "attr.get",
        "notadict.get()",
    ],
)
def test_no_chaining(inp):
    assert not _results(inp)


@pytest.mark.parametrize(
    "inp",
    [
        'test.get("test", {}).get("test")',
        'test.get("test", default={}).get("test")',
        'test.get("test", test).get("test")',
        'test.get("test", default=test).get("test")',
    ],
)
def test_valid_chaining(inp):
    assert not _results(inp)


@pytest.mark.parametrize(
    "inp, errs",
    [
        ('test.get("test").get("test")', [f"{_gl('1:16')} {EXPECTED_ERR_MSG}"]),
        ('test.get("test", None).get("test")', [f"{_gl('1:22')} {EXPECTED_ERR_MSG}"]),
        (
            'test.get("test", default=None).get("test")',
            [f"{_gl('1:30')} {EXPECTED_ERR_MSG}"],
        ),
        (
            'test.get("test", test=None).get("test")',
            [f"{_gl('1:27')} {EXPECTED_ERR_MSG}"],
        ),
        (
            'test.get("test", {}).get("test").get("test")',
            [f"{_gl('1:32')} {EXPECTED_ERR_MSG}"],
        ),
        (
            'test.get("test").get("test").get("test")',
            [f"{_gl('1:28')} {EXPECTED_ERR_MSG}", f"{_gl('1:16')} {EXPECTED_ERR_MSG}"],
        ),
    ],
)
def test_invalid_chaining(inp, errs):
    assert _results(inp) == errs
