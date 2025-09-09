import pytest
from typing import Dict, List

from analysis.ast_parser import parse_symbolic_summary

def test_valid_code_parsing():
    code = "def my_func(): pass"
    summary = parse_symbolic_summary(code)
    assert "my_func" in summary.get("function_names", [])

def test_error_on_invalid_code():
    code = "def my_func(:"
    summary = parse_symbolic_summary(code)
    assert isinstance(summary.get("error"), str)
