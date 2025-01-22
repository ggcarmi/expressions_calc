import pytest
from src.expression_simplifier import ExpressionSimplifier


class TestExpressionSimplifier:
    def test_pre_increment(self):
        expression = "j = ++i"
        expected = ["i = i + 1", "j = i"]
        result = ExpressionSimplifier.simplify(expression)
        assert result == expected

    def test_post_increment(self):
        expression = "j = i++ + 5"
        expected = ["j = i + 5", "i = i + 1"]
        result = ExpressionSimplifier.simplify(expression)
        assert result == expected

    def test_compound_assignment(self):
        expression = "x += 1"
        expected = ["x = x + 1"]
        result = ExpressionSimplifier.simplify(expression)
        assert result == expected

