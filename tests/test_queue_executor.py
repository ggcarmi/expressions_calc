"""
Tests for queue-based executor.
"""
import pytest
import logging
import unittest

from src.calculator import Calculator
from src.config import Config, ExecutionMode
from src.evaluator import EvaluationStrategy
from src.logger import setup_logger
from src.executor import QueueBasedExecutor
from src.dependency_graph import CyclicDependencyError, UndefinedVariableError

# Set up test logger
logger = setup_logger("test_queue_executor")

@pytest.fixture
def queue_calculator():
    """Create queue-based calculator instance for testing."""
    Config.set_execution_mode(ExecutionMode.QUEUE)
    return Calculator()

class TestQueueExecutor:
    """Test queue-based execution scenarios."""
    
    def test_concurrent_expressions(self, queue_calculator):
        """Test concurrent execution of independent expressions."""
        # Create a large number of independent expressions
        expressions = [f"x{i} = {i}" for i in range(100)]
        expected = {f"x{i}": i for i in range(100)}
        
        logger.info("Testing concurrent expressions:")
        logger.info(f"Input expressions: {expressions}")
        logger.info(f"Expected output: {expected}")
        
        # Execute them all
        results = queue_calculator.evaluate_multiple(expressions)
        logger.info(f"Actual output: {results}")
        
        # Verify results
        assert results == expected
        
    def test_mixed_dependencies(self, queue_calculator):
        """Test mixed independent and dependent expressions."""
        expressions = [
            "base = 10",
            "scale = 2",
            *[f"x{i} = {i} * scale" for i in range(5)],  # Depends on scale
            *[f"y{i} = base + {i}" for i in range(5)],   # Depends on base
            *[f"z{i} = {i}" for i in range(5)]           # Independent
        ]
        
        logger.info("Testing mixed dependencies:")
        logger.info(f"Input expressions: {expressions}")
        
        results = queue_calculator.evaluate_multiple(expressions)
        logger.info(f"Actual output: {results}")
        
        # Build and log expected results
        expected = {"base": 10, "scale": 2}
        expected.update({f"x{i}": i * 2 for i in range(5)})
        expected.update({f"y{i}": 10 + i for i in range(5)})
        expected.update({f"z{i}": i for i in range(5)})
        logger.info(f"Expected output: {expected}")
        
        # Verify results
        assert results == expected
            
    def test_chain_dependencies(self, queue_calculator):
        """Test long chain of dependencies."""
        expressions = [
            "x0 = 1",
            *[f"x{i} = x{i-1} * 2" for i in range(1, 10)]  # Each depends on previous
        ]
        
        logger.info("Testing chain dependencies:")
        logger.info(f"Input expressions: {expressions}")
        
        results = queue_calculator.evaluate_multiple(expressions)
        logger.info(f"Actual output: {results}")
        
        # Verify results (powers of 2)
        expected = {f"x{i}": 2**i for i in range(10)}
        logger.info(f"Expected output: {expected}")
        assert results == expected
        
    def test_complex_dependencies(self, queue_calculator):
        """Test complex dependency patterns."""
        expressions = [
            # Base values
            "a = 1",
            "b = 2",
            "c = 3",
            
            # First level dependencies
            "x = a + b",      # Depends on a, b
            "y = b + c",      # Depends on b, c
            "z = a + c",      # Depends on a, c
            
            # Second level dependencies
            "p = x + y",      # Depends on x, y
            "q = y + z",      # Depends on y, z
            "r = x + z",      # Depends on x, z
            
            # Final level
            "result = p + q + r"  # Depends on p, q, r
        ]
        
        logger.info("Testing complex dependencies:")
        logger.info(f"Input expressions: {expressions}")
        
        results = queue_calculator.evaluate_multiple(expressions)
        logger.info(f"Actual output: {results}")
        
        # Build and log expected results
        expected = {
            "a": 1, "b": 2, "c": 3,
            "x": 3, "y": 5, "z": 4,
            "p": 8, "q": 9, "r": 7,
            "result": 24
        }
        logger.info(f"Expected output: {expected}")
        assert results == expected


if __name__ == '__main__':
    unittest.main()
