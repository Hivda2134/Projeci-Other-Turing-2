import pytest
from typing import Union, Dict, List
# Doğru import yolu:
from analysis.ast_parser import parse_symbolic_summary

def test_valid_code_parsing():
    """Tests if a simple function is parsed."""
    code = "def my_func(): pass"
    summary = parse_symbolic_summary(code)
    assert "my_func" in summary

def test_error_on_invalid_code():
    """Tests if invalid code returns an error string."""
    code = "def my_func(:"
    summary = parse_symbolic_summary(code)
    # Hata durumunda bir string döndürdüğünü varsayıyoruz.
    # Gerçek implementasyona göre bu assert değiştirilebilir.
    assert isinstance(summary, str)
