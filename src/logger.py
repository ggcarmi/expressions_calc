"""
Logging configuration for calculator.
"""
import logging
import sys


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Set up a logger with the specified name and level."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Create loggers for different components
calculator_logger = setup_logger("calculator")
executor_logger = setup_logger("executor")
evaluator_logger = setup_logger("evaluator")
dependency_logger = setup_logger("dependency")
