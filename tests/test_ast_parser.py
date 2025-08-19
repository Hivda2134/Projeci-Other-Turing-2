
import textwrap
import pytest
from analysis.ast_parser import parse_symbolic_summary

def test_parse_symbolic_summary_basic():
    src = textwrap.dedent(
        '''
        """
        Module doc for greetings.
        """
        import os
        import sys as system
        from collections import defaultdict as dd, Counter

        class Greeter:
            """Say hello to people."""
            def greet(self, name: str) -> str:
                """Return a greeting."""
                print("log")
                return f"Hello, {name}"

        def add(a: int, b: int) -> int:
            """Add two numbers.""" 
            return a + b

        def main():
            """Main entry point."""
            user = "World"
            x, y = 1, 2
            with open("tmp.txt", "w") as fh:
                fh.write("hi")
            total = add(1, 2)
            print(total)
            flag: bool = True
            count = 0
        '''
    )
    summary = parse_symbolic_summary(src)
    assert "error" not in summary
    assert "Greeter" in summary["class_names"]
    assert "greet" in summary["method_names"]
    assert "add" in summary["function_names"]
    vars_ = set(summary["variable_names"])
    assert {"user", "x", "y", "fh", "total", "flag", "count"} <= vars_
    assert {"name", "a", "b"} <= set(summary["param_names"])
    hints = summary["type_hints"]
    assert any(h in hints for h in ("str", "int", "bool"))
    assert "os" in summary["imports"]
    assert "collections.defaultdict" in summary["from_imports"]
    assert "system" in summary["import_aliases"]
    docs = " ".join(summary["docstrings"]) + " " + summary["module_doc"]
    assert "Say hello to people." in docs
    calls = set(summary["calls"])
    se_calls = set(summary["side_effect_calls"])
    assert {"print", "open"}.issubset(calls)
    assert {"print", "open"}.issubset(se_calls)
    m = summary["metrics"]
    assert m["num_functions"] >= 2
    assert m["num_classes"] == 1
    assert m["num_side_effect_calls"] >= 2

def test_syntax_error_is_handled_gracefully():
    bad_src = "def oops(:\n  pass\n"
    summary = parse_symbolic_summary(bad_src)
    assert "error" in summary
    assert summary.get("function_names") == []

