import ast
import sys
from typing import List

import pytest

from get_chaining import ERR_MSGS, ErrorType, GetChainingChecker


def _gl(line_col):
    if sys.version_info < (3, 8):
        return "1:0"  # pragma: no coverage
    return line_col  # pragma: no coverage


def _err_msg(error_type: ErrorType):
    return f"{error_type.value} {ERR_MSGS[error_type]}"


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
        "attr.get().get",
        "attr.get.get()",
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
    "inp, err_pos",
    [
        ('test.get("test").get("test")', "1:16"),
        ('test.get("test", {}).get("test").get("test")', "1:32"),
        ('test.get("test").get("test", {}).get("test")', "1:16"),
        ('test.get("test", default={}).get("test").get("test")', "1:40"),
        ('test.get("test").get("test", default={}).get("test")', "1:16"),
        ('test.get("test", test=None).get("test")', "1:27"),
    ],
)
def test_DGC1001(inp, err_pos):
    assert _results(inp) == [f"{_gl(err_pos)} {_err_msg(ErrorType.DGC1001)}"]


@pytest.mark.parametrize(
    "inp, err_pos",
    [
        ('test.get("test", default=None).get("test")', "1:30"),
        ('test.get("test", None).get("test")', "1:22"),
        ('test.get("test", None, default=None).get("test")', "1:36"),
        ('test.get("test", test=foo, default=None).get("test")', "1:40"),
        ('test.get("test", {}).get("test", default=None).get("test")', "1:46"),
        ('test.get("test", default=None).get("test", {}).get("test")', "1:30"),
        ('test.get("test", default={}).get("test", None).get("test")', "1:46"),
        ('test.get("test", None).get("test", default={}).get("test")', "1:22"),
    ],
)
def test_DGC1002(inp, err_pos):
    assert _results(inp) == [f"{_gl(err_pos)} {_err_msg(ErrorType.DGC1002)}"]


@pytest.mark.parametrize(
    "inp, errs",
    [
        (
            'test.get("test").get("test").get("test")',
            [
                f"{_gl('1:28')} {_err_msg(ErrorType.DGC1001)}",
                f"{_gl('1:16')} {_err_msg(ErrorType.DGC1001)}",
            ],
        ),
        (
            'test.get("test", default=None).get("test", None).get("test")',
            [
                f"{_gl('1:48')} {_err_msg(ErrorType.DGC1002)}",
                f"{_gl('1:30')} {_err_msg(ErrorType.DGC1002)}",
            ],
        ),
        (
            'test.get("test").get("test", None).get("test")',
            [
                f"{_gl('1:34')} {_err_msg(ErrorType.DGC1002)}",
                f"{_gl('1:16')} {_err_msg(ErrorType.DGC1001)}",
            ],
        ),
        (
            'test.get("test", default=None).get("test").get("test")',
            [
                f"{_gl('1:42')} {_err_msg(ErrorType.DGC1001)}",
                f"{_gl('1:30')} {_err_msg(ErrorType.DGC1002)}",
            ],
        ),
    ],
)
def test_multiple_invalid_chaining(inp, errs):
    assert _results(inp) == errs
