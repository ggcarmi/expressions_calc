"""
Expression evaluation strategies.
"""
import ast
import re
import logging
from enum import Enum
from typing import Dict, Tuple
from .expression_simplifier import ExpressionSimplifier

logger = logging.getLogger(__name__)


class EvaluationStrategy(Enum):
    """Available evaluation strategies."""
    AST = "ast"
    REGEX = "regex"


class ExpressionEvaluator:
    """Base class for expression evaluators."""
    
    def evaluate(self, expression: str, variables: Dict[str, int]) -> Tuple[str, int]:
        """Evaluate expression and return (variable_name, value)."""
        raise NotImplementedError


class ASTEvaluator(ExpressionEvaluator):
    """Evaluates expressions With Tree - using Python's AST."""
    
    def evaluate(self, expression: str, variables: Dict[str, int]) -> Tuple[str, int]:
        """Evaluate expression using AST parsing."""
        simplified_expressions = ExpressionSimplifier.simplify(expression)
        logger.debug(f"Evaluating simplified expressions: {simplified_expressions}")
        
        last_var = None
        last_val = None
        
        for expr in simplified_expressions:
            var, val = self._evaluate_single_expression(expr, variables)
            logger.debug(f"After '{expr}': {var} = {val}, variables = {variables}")
            
            if var is not None:
                last_var = var
                last_val = val
                variables[var] = val
        
        return last_var, last_val

    def _evaluate_single_expression(self, expression: str, variables: Dict[str, int]) -> Tuple[str, int]:
        """Evaluate a single simplified expression."""
        logger.debug(f"Evaluating single expression: '{expression}'")
        try:
            tree = ast.parse(expression)
            if not isinstance(tree.body[0], ast.Assign):
                return None, None
                
            # Get target variable name
            target = tree.body[0].targets[0].id
            value_node = tree.body[0].value
            
            # Handle simple number assignment (i = 0)
            if isinstance(value_node, (ast.Num, ast.Constant)):  # Support both Num and Constant
                value = value_node.n if isinstance(value_node, ast.Num) else value_node.value
                variables[target] = value  # Important: store in variables
                logger.debug(f"Simple assignment: {target} = {value}")
                return target, value
                
            # Handle variable assignment (x = y)
            if isinstance(value_node, ast.Name):
                if value_node.id not in variables:
                    raise NameError(f"Variable '{value_node.id}' is not defined")
                value = variables[value_node.id]
                variables[target] = value  # Important: store in variables
                return target, value
                
            # Handle arithmetic expressions (x = y + 1)
            if isinstance(value_node, ast.BinOp):
                value = self._evaluate_node(value_node, variables)
                variables[target] = value  # Important: store in variables
                return target, value
                
            raise ValueError(f"Unsupported assignment: {expression}")
            
        except SyntaxError as e:
            raise ValueError(f"Invalid expression syntax: {expression}") from e

    def _evaluate_node(self, node: ast.AST, variables: Dict[str, int]) -> int:
        """Evaluate an AST node."""
        if isinstance(node, ast.Name):
            if node.id not in variables:
                raise NameError(f"Variable '{node.id}' is not defined")
            return variables[node.id]
        
        if isinstance(node, (ast.Num, ast.Constant)):  # Support both Num (old) and Constant (new)
            return node.n if isinstance(node, ast.Num) else node.value
        
        if isinstance(node, ast.BinOp):
            left = self._evaluate_node(node.left, variables)
            right = self._evaluate_node(node.right, variables)
            
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left // right
            
        raise ValueError(f"Unsupported operation: {type(node).__name__}")


class RegexEvaluator(ExpressionEvaluator):
    """Evaluates expressions using regex pattern matching."""
    
    def evaluate(self, expression: str, variables: Dict[str, int]) -> Tuple[str, int]:
        """Evaluate expression using regex patterns."""
        # First, simplify the expression
        simplified_expressions = ExpressionSimplifier.simplify(expression)
        
        # Evaluate each simplified expression in order
        result = None
        last_var = None
        
        # Process all simplified expressions
        for expr in simplified_expressions:
            var, val = self._evaluate_single_expression(expr, variables)
            if var is not None and val is not None:
                last_var = var
                result = val
                variables[var] = val  # Ensure variable is stored
            
        return last_var, result

    def _evaluate_single_expression(self, expression: str, variables: Dict[str, int]) -> Tuple[str, int]:
        """Evaluate a single simplified expression."""
        logger.debug(f"Evaluating single expression: '{expression}'")
        if '=' not in expression:
            return None, None
            
        target, value_expr = expression.split('=')
        target = target.strip()
        value_expr = value_expr.strip()
        
        # Handle simple assignment of number
        if value_expr.isdigit():
            value = int(value_expr)
            variables[target] = value
            return target, value
            
        # Handle simple variable assignment
        if value_expr.isidentifier():
            if value_expr not in variables:
                raise NameError(f"Variable '{value_expr}' is not defined")
            value = variables[value_expr]
            variables[target] = value
            return target, value
            
        # Handle arithmetic expressions
        match = re.match(r'(\w+|\d+)\s*([+\-*/])\s*(\w+|\d+)', value_expr)
        if match:
            left, op, right = match.groups()
            
            # Evaluate left operand
            if left.isdigit():
                left_val = int(left)
            elif left in variables:
                left_val = variables[left]
            else:
                raise NameError(f"Variable '{left}' is not defined")
                
            # Evaluate right operand
            if right.isdigit():
                right_val = int(right)
            elif right in variables:
                right_val = variables[right]
            else:
                raise NameError(f"Variable '{right}' is not defined")
                
            # Perform operation
            if op == '+':
                value = left_val + right_val
            elif op == '-':
                value = left_val - right_val
            elif op == '*':
                value = left_val * right_val
            elif op == '/':
                value = left_val // right_val
                
            variables[target] = value
            return target, value
            
        raise ValueError(f"Invalid expression syntax: {expression}")


class EvaluatorFactory:
    """Factory for creating evaluators."""
    
    @staticmethod
    def create_evaluator(strategy: EvaluationStrategy) -> ExpressionEvaluator:
        """Create an evaluator based on the specified strategy."""
        if strategy == EvaluationStrategy.AST:
            return ASTEvaluator()
        elif strategy == EvaluationStrategy.REGEX:
            return RegexEvaluator()
        else:
            raise ValueError(f"Unknown evaluation strategy: {strategy}")
