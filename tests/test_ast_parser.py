import pytest
from typing import Union, Dict, List
# Bu import yolu, projemizin yapısına göre ayarlanmalıdır.
# Eğer 'analysis' bir paket ise bu çalışacaktır.
try:
    from analysis.ast_parser import parse_symbolic_summary
except ImportError:
    # Alternatif yol, eğer doğrudan scripts'ten çağrılıyorsa
    from scripts.ast_parser import parse_symbolic_summary

def test_parse_valid_function():
    """
    Tests if a simple function definition is parsed correctly.
    """
    code = """
def my_function(a: int, b: str) -> bool:
    return True
"""
    summary = parse_symbolic_summary(code)
    assert isinstance(summary, dict)
    assert "my_function" in summary
    assert summary["my_function"] == ["int", "str"]

def test_parse_class_with_methods():
    """
    Tests if a class with methods is parsed correctly.
    """
    code = """
class MyClass:
    def method_one(self):
        pass
    def method_two(self, x: float):
        pass
"""
    summary = parse_symbolic_summary(code)
    assert isinstance(summary, dict)
    assert "MyClass.method_one" in summary
    assert "MyClass.method_two" in summary
    assert summary["MyClass.method_two"] == ["float"]

def test_parse_invalid_code_returns_error_string():
    """
    Tests if invalid Python code returns an error string.
    """
    code = "def my_function(:"
    summary = parse_symbolic_summary(code)
    assert isinstance(summary, str)
    assert "Error" in summary

def test_empty_code_returns_empty_dict():
    """
    Tests if empty code returns an empty dictionary.
    """
    code = ""
    summary = parse_symbolic_summary(code)
    assert summary == {}
