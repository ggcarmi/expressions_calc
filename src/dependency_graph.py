# This module will handle the creation of a dependency graph for expressions

from collections import defaultdict
from typing import List, Dict, Set

from .errors import CyclicDependencyError, UndefinedVariableError

class DependencyGraph:
    def __init__(self, expressions: List[str]):
        self.expressions = expressions
        self.graph = defaultdict(set)  # target -> dependencies
        self.in_degree = defaultdict(int)  # number of dependencies for each target
        self.variables = set()
        self.build_graph()

    def build_graph(self):
        """Builds a dependency graph from expressions."""
        # First pass: collect all defined variables
        for expr in self.expressions:
            target = self._get_target(expr)
            self.variables.add(target)
            self.graph[target]  # Ensure target exists in graph

        # Second pass: build dependencies
        for expr in self.expressions:
            target = self._get_target(expr)
            dependencies = self._get_dependencies(expr)
            for dep in dependencies:
                if dep not in self.variables:
                    raise UndefinedVariableError(f"Undefined variable '{dep}' used in expression '{expr}'")
                self.graph[target].add(dep)  # target depends on dep
                self.in_degree[target] += 1   # increment target's in-degree for each dependency

    def _get_target(self, expr: str) -> str:
        """Extracts the target variable from an expression."""
        return expr.split('=')[0].strip()

    def _get_dependencies(self, expr: str) -> Set[str]:
        """Extracts dependencies from an expression."""
        # Split into left and right sides
        parts = expr.split('=', 1)
        target = parts[0].strip()
        deps = set()
        
        # Handle compound assignments (+=, -=, *=, /=)
        if len(target.split()) > 1:  # Like 'x +=' or 'x *='
            target = target.split()[0]
            deps.add(target)  # Target is also a dependency
        
        if len(parts) > 1:
            right_side = parts[1].strip()
            
            # Handle pre-increment (++x)
            if right_side.startswith('++') or right_side.startswith('--'):
                var = right_side[2:].strip()
                deps.add(var)
                
            # Handle post-increment (x++)
            elif right_side.endswith('++') or right_side.endswith('--'):
                var = right_side[:-2].strip()
                deps.add(var)
                
            # Handle all other variables in expression
            for part in right_side.split():
                # Skip operators and numbers
                if part in {'+', '-', '*', '/', '(', ')', '++', '--'} or part.isdigit():
                    continue
                # Remove any trailing operators
                part = part.rstrip('+-*/')
                # If it's an identifier (variable name)
                if part.isidentifier():
                    deps.add(part)
        
        return deps

    def topological_sort(self) -> List[str]:
        """Performs a topological sort on the dependency graph."""
        in_degree = self.in_degree.copy()
        sorted_expressions = []
        
        # Find all expressions with no dependencies
        zero_in_degree = [expr for expr in self.expressions if in_degree[self._get_target(expr)] == 0]
        
        while zero_in_degree:
            current = zero_in_degree.pop()
            sorted_expressions.append(current)
            current_target = self._get_target(current)
            
            # Find all expressions that depend on current
            for expr in self.expressions:
                target = self._get_target(expr)
                # If this expression depends on current_target
                if current_target in self.graph[target]:
                    in_degree[target] -= 1
                    if in_degree[target] == 0:
                        zero_in_degree.append(expr)

        if len(sorted_expressions) != len(self.expressions):
            raise CyclicDependencyError("Cyclic dependency detected")

        return sorted_expressions

    def get_expression_levels(self) -> Dict[int, List[str]]:
        """Group expressions by dependency levels.
        Level 0: No dependencies
        Level n: Depends on expressions from previous levels
        """
        sorted_expressions = self.topological_sort()
        level_groups = defaultdict(list)
        current_level = 0
        current_level_expressions = []
        
        for expr in sorted_expressions:
            target = self._get_target(expr)
            deps = self.graph[target]
            # Check if expression depends on anything in current level
            if any(self._get_target(dep) in [self._get_target(e) for e in current_level_expressions] for dep in deps):
                # If it does, start a new level
                if current_level_expressions:
                    level_groups[current_level] = current_level_expressions
                    current_level += 1
                    current_level_expressions = []
            current_level_expressions.append(expr)
        
        # Add remaining expressions
        if current_level_expressions:
            level_groups[current_level] = current_level_expressions
            
        return level_groups
