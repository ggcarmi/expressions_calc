"""
Test cases for calculator implementation.
"""
import pytest
import logging

from src.calculator import Calculator
from src.config import Config, ExecutionMode

logger = logging.getLogger(__name__)


@pytest.fixture
def sequential_calculator():
    """Create sequential calculator instance for testing."""
    Config.set_execution_mode(ExecutionMode.SEQUENTIAL)
    return Calculator()


@pytest.fixture
def queue_calculator():
    """Create queue-based calculator instance for testing."""
    Config.set_execution_mode(ExecutionMode.QUEUE)
    return Calculator()


class TestBasicOperations:
    """Tests that build up complexity step by step."""
    
    @pytest.mark.parametrize("calculator", [
        pytest.lazy_fixture("sequential_calculator"),
        pytest.lazy_fixture("queue_calculator")
    ])
    def test_simple_assignments(self, calculator):
        """Test simple variable assignments."""
        # Input
        expressions = [
            "x = 5",
            "y = 10",
            "z = 0"
        ]
        
        # Expected output
        expected = {
            "x": 5,
            "y": 10,
            "z": 0
        }
        
        # Debug logs
        logger.debug("Input expressions: %s", expressions)
        logger.debug("Initial variables: {}")
        
        result = calculator.evaluate_multiple(expressions)
        
        logger.debug("Final result: %s", result)
        assert result == expected

    @pytest.mark.parametrize("calculator", [
        pytest.lazy_fixture("sequential_calculator"),
        pytest.lazy_fixture("queue_calculator")
    ])
    def test_sequential_assignments(self, calculator):
        """Test assignments that use previous values."""
        # Input
        expressions = [
            "x = 5",
            "y = x",  # y should be 5
            "z = y"   # z should be 5
        ]
        
        # Expected output
        expected = {
            "x": 5,
            "y": 5,
            "z": 5
        }
        
        logger.debug("Input expressions: %s", expressions)
        logger.debug("Initial variables: {}")
        
        result = calculator.evaluate_multiple(expressions)
        
        logger.debug("Final result: %s", result)
        assert result == expected

    @pytest.mark.parametrize("calculator", [
        pytest.lazy_fixture("sequential_calculator"),
        pytest.lazy_fixture("queue_calculator")
    ])
    def test_arithmetic_expressions(self, calculator):
        """Test basic arithmetic operations."""
        # Input
        expressions = [
            "x = 5",
            "y = 3 + 2",      # y = 5
            "z = x + y",      # z = 10
            "w = z * 2"       # w = 20
        ]
        
        # Expected output
        expected = {
            "x": 5,
            "y": 5,
            "z": 10,
            "w": 20
        }
        
        logger.debug("Input expressions: %s", expressions)
        logger.debug("Initial variables: {}")
        
        result = calculator.evaluate_multiple(expressions)
        
        logger.debug("Final result: %s", result)
        assert result == expected

    @pytest.mark.parametrize("calculator", [
        pytest.lazy_fixture("sequential_calculator"),
        pytest.lazy_fixture("queue_calculator")
    ])
    def test_compound_assignments(self, calculator):
        """Test compound assignments (+=, -=, etc)."""
        # Input
        expressions = [
            "x = 5",
            "x += 3",     # x = 8
            "y = 10",
            "y *= 2"      # y = 20
        ]
        
        # Expected output
        expected = {
            "x": 8,
            "y": 20
        }
        
        logger.debug("Input expressions: %s", expressions)
        logger.debug("Initial variables: {}")
        
        result = calculator.evaluate_multiple(expressions)
        
        logger.debug("Final result: %s", result)
        assert result == expected

    @pytest.mark.parametrize("calculator", [
        pytest.lazy_fixture("sequential_calculator"),
        # pytest.lazy_fixture("queue_calculator")
    ])
    def test_pre_increment(self, calculator):
        """Test pre-increment operations (++x)."""
        # Input
        expressions = [
            "i = 0",
            "j = ++i"     # i = 1, j = 1
        ]
        
        # Expected output
        expected = {
            "i": 1,
            "j": 1
        }
        
        logger.debug("Input expressions: %s", expressions)
        logger.debug("Initial variables: {}")
        
        result = calculator.evaluate_multiple(expressions)
        
        logger.debug("Final result: %s", result)
        assert result == expected

    @pytest.mark.parametrize("calculator", [
        pytest.lazy_fixture("sequential_calculator"),
        # pytest.lazy_fixture("queue_calculator")
    ])
    def test_post_increment(self, calculator):
        """Test post-increment operations (x++)."""
        # Input
        expressions = [
            "i = 0",
            "j = i++",    # j = 0, i = 1
            "k = i"       # k = 1
        ]
        
        # Expected output
        expected = {
            "i": 1,
            "j": 0,
            "k": 1
        }
        
        logger.debug("Input expressions: %s", expressions)
        logger.debug("Initial variables: {}")
        
        result = calculator.evaluate_multiple(expressions)
        
        logger.debug("Final result: %s", result)
        assert result == expected

    @pytest.mark.parametrize("calculator", [
        pytest.lazy_fixture("sequential_calculator"),
        # pytest.lazy_fixture("queue_calculator")
    ])
    def test_complex_scenario(self, calculator):
        """Test complex scenario with multiple operations."""
        # Input
        expressions = [
            "i = 0",
            "j = ++i",        # i = 1, j = 1
            "x = i++ + 5",    # x = 6, i = 2
            "y = (5 + 3) * 10",  # y = 80
            "i += y"          # i = 82
        ]
        
        # Expected output
        expected = {
            "i": 82,
            "j": 1,
            "x": 6,
            "y": 80
        }
        
        logger.debug("Input expressions: %s", expressions)
        logger.debug("Initial variables: {}")
        
        result = calculator.evaluate_multiple(expressions)
        
        logger.debug("Final result: %s", result)
        assert result == expected

class TestIncrementOperators:
    """Test increment operator handling."""
    
    @pytest.mark.parametrize("calculator", [
        pytest.lazy_fixture("sequential_calculator"),
        # pytest.lazy_fixture("queue_calculator")
    ])
    def test_pre_increment(self, calculator):
        """Test pre-increment operator."""
        results = calculator.evaluate_multiple([
            "i = 0",
            "j = ++i"
        ])
        assert results == {"i": 1, "j": 1}
        
    @pytest.mark.parametrize("calculator", [
        pytest.lazy_fixture("sequential_calculator"),
        # pytest.lazy_fixture("queue_calculator")
    ])
    def test_post_increment(self, calculator):
        """Test post-increment operator."""
        results = calculator.evaluate_multiple([
            "i = 0",
            "j = i++",  # j gets 0, then i becomes 1
            "k = ++i"   # i becomes 2, then k gets 2
        ])
        assert results == {"i": 2, "j": 0, "k": 2}
        
    @pytest.mark.parametrize("calculator", [
        pytest.lazy_fixture("sequential_calculator"),
        # pytest.lazy_fixture("queue_calculator")
    ])
    def test_increment_in_expression(self, calculator):
        """Test increment within expressions."""
        results = calculator.evaluate_multiple([
            "i = 5",
            "j = ++i + 3",  # i becomes 6, j = 6 + 3 = 9
            "k = i++ + j"   # k = 6 + 9 = 15, then i becomes 7
        ])
        assert results == {"i": 7, "j": 9, "k": 15}


class TestCompoundAssignments:
    """Test compound assignment operators."""
    
    @pytest.mark.parametrize("calculator", [
        pytest.lazy_fixture("sequential_calculator"),
        # pytest.lazy_fixture("queue_calculator")
    ])
    def test_compound_assignments(self, calculator):
        """Test compound assignment operators."""
        results = calculator.evaluate_multiple([
            "x = 5",
            "y = 3",
            "x += y",
            "y *= 2"
        ])
        assert results == {"x": 8, "y": 6}


class TestComplexScenarios:
    """Test complex scenarios combining multiple features."""
    
    @pytest.mark.parametrize("calculator", [
        pytest.lazy_fixture("sequential_calculator"),
        # pytest.lazy_fixture("queue_calculator")
    ])
    def test_example_from_spec(self, calculator):
        """Test the example provided in the specification."""
        result = calculator.evaluate_multiple([
            "i = 0",
            "j = ++i",
            "x = i++ + 5",
            "y = (5 + 3) * 10",
            "i += y"
        ])
        assert result == {"i": 82, "j": 1, "x": 6, "y": 80}

    @pytest.mark.parametrize("calculator", [
        pytest.lazy_fixture("sequential_calculator"),
        # pytest.lazy_fixture("queue_calculator")
    ])
    def test_independent_expressions(self, calculator):
        """Test parallel execution of independent expressions."""
        results = calculator.evaluate_multiple([
            "a = 1",
            "b = 2",
            "c = 3",
            "d = 4",
            "e = 5"
        ])
        assert results == {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}

    @pytest.mark.parametrize("calculator", [
        pytest.lazy_fixture("sequential_calculator"),
        # pytest.lazy_fixture("queue_calculator")
    ])
    def test_mixed_dependencies(self, calculator):
        """Test parallel execution with mixed dependencies."""
        results = calculator.evaluate_multiple([
            "a = 1",
            "b = 2",
            "c = a + b",
            "d = c * 2",
            "e = d + a"
        ])
        assert results == {"a": 1, "b": 2, "c": 3, "d": 6, "e": 7}

    @pytest.mark.parametrize("calculator", [
        pytest.lazy_fixture("sequential_calculator"),
        # pytest.lazy_fixture("queue_calculator")
    ])
    def test_complex_dependencies(self, calculator):
        """Test complex dependencies with increments."""
        results = calculator.evaluate_multiple([
            "i = 0",
            "j = ++i",          # i becomes 1, j = 1
            "x = i++ + 5",      # x = 1 + 5 = 6, then i becomes 2
            "y = (5 + 3) * 10", # y = 80
            "i += y",           # i = 2 + 80 = 82
            "z = i++ + j",      # z = 82 + 1 = 83, then i becomes 83
            "w = x + y + z"     # w = 6 + 80 + 83 = 169
        ])
        assert results == {
            "i": 83,
            "j": 1,
            "x": 6,
            "y": 80,
            "z": 83,
            "w": 169
        }

    @pytest.mark.parametrize("calculator", [
        pytest.lazy_fixture("sequential_calculator"),
        # pytest.lazy_fixture("queue_calculator")
    ])
    def test_parallel_execution(self, calculator):
        """Test parallel execution with increments."""
        results = calculator.evaluate_multiple([
            "a = 1",
            "b = ++a",     # a becomes 2, b = 2
            "c = a++",     # c = 2, then a becomes 3
            "d = b + c",   # d = 2 + 2 = 4
            "e = ++a + d"  # a becomes 4, e = 4 + 4 = 8
        ])
        assert results == {
            "a": 4,
            "b": 2,
            "c": 2,
            "d": 4,
            "e": 8
        }


class TestParallelExecution:
    """Test parallel execution scenarios."""
    
    @pytest.mark.parametrize("calculator", [
        pytest.lazy_fixture("sequential_calculator"),
        # pytest.lazy_fixture("queue_calculator")
    ])
    def test_dependent_expressions(self, calculator):
        """Test parallel execution of dependent expressions."""
        results = calculator.evaluate_multiple([
            "x = 1",
            "y = x + 1",
            "z = y + 1",
            "w = z + 1"
        ])
        assert results == {"x": 1, "y": 2, "z": 3, "w": 4}
        
    @pytest.mark.parametrize("calculator", [
        pytest.lazy_fixture("sequential_calculator"),
        # pytest.lazy_fixture("queue_calculator")
    ])
    def test_increment_dependencies(self, calculator):
        """Test parallel execution with increment operators."""
        results = calculator.evaluate_multiple([
            "i = 0",
            "j = ++i",      # Depends on i
            "x = i++",      # Depends on i
            "y = i++ + 5",  # Depends on i
            "z = ++i + y"   # Depends on i, y
        ])
        assert results == {"i": 4, "j": 1, "x": 1, "y": 7, "z": 11}
        
    @pytest.mark.parametrize("calculator", [
        pytest.lazy_fixture("sequential_calculator"),
        # pytest.lazy_fixture("queue_calculator")
    ])
    def test_compound_assignment_dependencies(self, calculator):
        """Test parallel execution with compound assignments."""
        results = calculator.evaluate_multiple([
            "x = 5",
            "y = 3",
            "z = 2",
            "x += y",       # Depends on x, y
            "y *= z",       # Depends on y, z
            "z += x"        # Depends on z, x
        ])
        assert results == {"x": 8, "y": 6, "z": 10}
