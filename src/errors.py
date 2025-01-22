class DependencyError(Exception):
    """Base class for dependency-related errors."""
    pass

class CyclicDependencyError(DependencyError):
    """Raised when a cyclic dependency is detected."""
    pass

class UndefinedVariableError(DependencyError):
    """Raised when an undefined variable is used in an expression."""
    pass