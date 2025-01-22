"""
Configuration management for calculator.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ExecutionMode(Enum):
    """Available execution modes."""
    SEQUENTIAL = "sequential"
    QUEUE = "queue"


class EvaluatorMode(Enum):
    """Available evaluator modes."""
    AST = "ast"
    REGEX = "regex"


class Config:
    """Configuration settings for the calculator application."""

    DEFAULT_EXECUTION_MODE = ExecutionMode.SEQUENTIAL
    DEFAULT_EVALUATOR = EvaluatorMode.AST
    NUM_WORKERS = None  # None means use cpu_count()
    TIMEOUT = 5  # Timeout in seconds for queue-based execution

    # Class variable to track current execution mode
    execution_mode = ExecutionMode.SEQUENTIAL  # Default mode

    _config: Optional['Config'] = None

    @staticmethod
    def get_execution_mode() -> ExecutionMode:
        """Get current execution mode."""
        return Config.execution_mode

    @staticmethod
    def set_execution_mode(mode: ExecutionMode):
        """Set the execution mode."""
        if not isinstance(mode, ExecutionMode):
            raise ValueError(f"Invalid execution mode: {mode}")
        Config.execution_mode = mode

    @staticmethod
    def get_evaluator() -> EvaluatorMode:
        """Retrieve the current evaluator option."""
        return Config.DEFAULT_EVALUATOR

    @staticmethod
    def set_evaluator(evaluator: EvaluatorMode):
        """Set the evaluator option."""
        if evaluator not in EvaluatorMode:
            raise ValueError("Invalid evaluator option")
        Config.DEFAULT_EVALUATOR = evaluator

    @classmethod
    def get_config(cls) -> 'Config':
        """Get current configuration."""
        if cls._config is None:
            cls._config = Config()
        return cls._config

    @classmethod
    def set_config(cls, config: 'Config'):
        """Set new configuration."""
        cls._config = config
