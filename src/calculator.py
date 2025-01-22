"""
Calculator implementation that supports arithmetic operations and variable assignments.
"""
from typing import Dict, List, Optional

from .evaluator import EvaluationStrategy
from .executor import ExecutorFactory


class Calculator:
    """Calculator - main class for the app"""
    
    def __init__(self, strategy: EvaluationStrategy = EvaluationStrategy.AST):
        """Initialize calculator with specified evaluation strategy."""
        self.executor = ExecutorFactory.create_executor(strategy=strategy)
        
    def evaluate(self, expression: str) -> Optional[int]:
        """Evaluate a single expression."""
        result = self.evaluate_multiple([expression])
        return next(iter(result.values())) if result else None
        
    def evaluate_multiple(self, expressions: List[str]) -> Dict[str, int]:
        """Evaluate multiple expressions, handling dependencies between them."""
        return self.executor.execute(expressions)
