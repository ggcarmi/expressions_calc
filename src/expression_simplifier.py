# This module will simplify complex expressions to simple form

import re
import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Expression:
    """Represents a parsed expression."""
    target: str
    operator: Optional[str]
    value: str
    original: str

    def __str__(self):
        return self.original

class ExpressionHandler(ABC):
    """Base class for expression handlers.

    How it works?
    if the current handler can process the expression, it does so and stops further processing.
    If the current handler cannot process the expression, it passes the expression to the next handler in the chain.
    This approach ensures that each handler gets a chance to process the expression in sequence,
    and the first handler that can process it will handle it,
    preventing unnecessary processing by subsequent handlers.
    """
    
    def __init__(self):
        self._next_handler: Optional[ExpressionHandler] = None
    
    def set_next(self, handler: 'ExpressionHandler') -> 'ExpressionHandler':
        """Set the next handler in the chain."""
        self._next_handler = handler
        return handler
    
    def process_expression(self, expression: Expression) -> List[str]:
        """Process the expression through the chain of handlers."""

        logger.debug(f"\nTrying handler: {self.__class__.__name__}")
        result = self.handle(expression)
        if result:
            logger.debug(f"{self.__class__.__name__} handled it -> {result}")
            return result
        if self._next_handler:
            logger.debug(f"{self.__class__.__name__} passing to next handler")
            return self._next_handler.process_expression(expression)
        logger.debug(f"{self.__class__.__name__} couldn't handle it, no next handler")
        return []
    
    @abstractmethod
    def handle(self, expression: Expression) -> List[str]:
        """Handle the expression if possible."""
        pass

class SimpleAssignmentHandler(ExpressionHandler):
    """Handles simple assignments like 'x = 5' or 'y = z'."""
    
    def handle(self, expression: Expression) -> List[str]:
        if '++' not in expression.value and not any(op in expression.original for op in ['+=', '-=', '*=', '/=']):
            logger.debug(f"Found simple assignment")
            return [expression.original]
        return []

class PreIncrementHandler(ExpressionHandler):
    """Handles pre-increment operations like 'x = ++y' or 'x = ++y + ++z'."""
    
    def handle(self, expression: Expression) -> List[str]:
        if not expression.value.startswith('++'):
            return []
            
        logger.debug(f"PreIncrementHandler checking: value='{expression.value}', target='{expression.target}'")
        
        # Replace all ++i with i and collect increments
        value = expression.value
        logger.debug(f"Starting value manipulation: '{value}'")
        pre_increments = []
        
        # Handle all pre-increments (++i)
        while '++' in value:
            pre_match = re.search(r'\+\+(\w+)', value)
            if not pre_match:
                break
                
            var = pre_match.group(1)
            # Replace ++i with just i in the expression
            value = value[:pre_match.start()] + var + value[pre_match.end():]
            logger.debug(f"Pre-increment: var='{var}', new_value='{value}'")
            pre_increments.append(f"{var} = {var} + 1")
            
        # Combine all expressions in the correct order
        result = []
        result.extend(pre_increments)                    # First do all pre-increments
        result.append(f"{expression.target} = {value}")  # Then evaluate the expression
        
        logger.debug(f"Generated expressions: {result}")
        return result

class PostIncrementHandler(ExpressionHandler):
    """Handles post-increment operations like 'x = y++'."""
    
    def handle(self, expression: Expression) -> List[str]:
        if expression.value.endswith('++'):
            var = expression.value[:-2].strip()
            logger.debug(f"Found post-increment: var='{var}'")
            result = [
                f"{expression.target} = {var}",  # First assign
                f"{var} = {var} + 1"      # Then increment
            ]
            return result
        return []

class CompoundAssignmentHandler(ExpressionHandler):
    """Handles compound assignments like 'x += 1'."""
    
    def handle(self, expression: Expression) -> List[str]:
        if expression.operator in ['+=', '-=', '*=', '/=']:
            op = expression.operator[0]
            logger.debug(f"Found compound assignment with operator '{op}'")
            result = [f"{expression.target} = {expression.target} {op} {expression.value}"]
            return result
        return []

class ComplexIncrementHandler(ExpressionHandler):
    """Handles increments within expressions like 'x = ++y + z + ++w' or 'x = y++ + z + w++'."""
    
    def handle(self, expression: Expression) -> List[str]:
        if '++' not in expression.value:
            logger.debug("No '++' found in expression")
            return []
            
        logger.debug(f"ComplexIncrementHandler checking: value='{expression.value}', target='{expression.target}'")
        
        # First replace all ++i with i and collect pre-increments
        value = expression.value
        logger.debug(f"Starting value manipulation: '{value}'")
        pre_increments = []
        post_increments = []
        
        # Handle all pre-increments first (++i)
        while '++' in value:
            pre_match = re.search(r'\+\+(\w+)', value)
            if not pre_match:
                break
                
            var = pre_match.group(1)
            # Replace ++i with just i in the expression
            value = value[:pre_match.start()] + var + value[pre_match.end():]
            logger.debug(f"Pre-increment: var='{var}', new_value='{value}'")
            pre_increments.append(f"{var} = {var} + 1")
            
        # Then handle all post-increments (i++)
        while '++' in value:
            post_match = re.search(r'(\w+)\+\+', value)
            if not post_match:
                break
                
            var = post_match.group(1)
            # Replace i++ with just i in the expression
            value = value[:post_match.start()] + var + value[post_match.end():]
            logger.debug(f"Post-increment: var='{var}', new_value='{value}'")
            post_increments.append(f"{var} = {var} + 1")
            
        # Combine all expressions in the correct order
        result = []
        result.extend(pre_increments)                    # First do all pre-increments
        result.append(f"{expression.target} = {value}")  # Then evaluate the expression
        result.extend(post_increments)                   # Finally do all post-increments
        
        logger.debug(f"Generated expressions: {result}")
        return result

class ExpressionSimplifier:
    """Simplifies complex expressions into simpler sub-expressions using Chain of Responsibility pattern."""

    def __init__(self):
        # Build the chain of handlers
        self.handler = SimpleAssignmentHandler()
        self.handler.set_next(PreIncrementHandler())\
                   .set_next(PostIncrementHandler())\
                   .set_next(CompoundAssignmentHandler())\
                   .set_next(ComplexIncrementHandler())
    
    @staticmethod
    def parse_expression(expression: str) -> Expression:
        """Parse an expression into its components."""
        logger.debug(f"\nParsing expression: '{expression}'")
        
        # Handle compound assignments (+=, -=, *=, /=)
        compound_match = re.match(r'(\w+)\s*(\+=|-=|\*=|/=)\s*(.+)', expression)
        if compound_match:
            target, operator, value = compound_match.groups()
            result = Expression(target.strip(), operator, value.strip(), expression)
            logger.debug(f"Parsed compound assignment: {result}")
            return result
        
        # Handle regular assignments
        if '=' in expression:
            target, value = expression.split('=', 1)
            result = Expression(target.strip(), None, value.strip(), expression)
            logger.debug(f"Parsed regular assignment: {result}")
            return result
            
        logger.debug(f"Invalid expression format: {expression}")
        raise ValueError(f"Invalid expression format: {expression}")
    
    @staticmethod
    def simplify(expression: str) -> List[str]:
        """Simplify an expression into a list of sub-expressions."""
        logger.debug(f"\n=== Starting simplification of: '{expression}' ===")
        
        try:
            parsed = ExpressionSimplifier.parse_expression(expression)
            logger.debug(f"Parsed into: {parsed}")
            
            simplifier = ExpressionSimplifier()
            result = simplifier.handler.process_expression(parsed)
            
            logger.debug(f"=== Final simplified expressions: {result} ===\n")
            return result
        except Exception as e:
            logger.error(f"Error simplifying expression '{expression}': {str(e)}")
            raise
