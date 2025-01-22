# Advanced Calculator

## TLDR
This is a high-performance calculator that supports parallel execution of arithmetic expressions with advanced variable handling. It provides flexible execution modes and intelligent expression processing for complex computational tasks.

**Quick Start:** `docker build -t calculator . && docker run calculator`

## Features

- Arithmetic expression evaluation with variable support
- Multiple execution modes:
  - Sequential execution
  - Queue-based parallel execution
- Smart dependency analysis for optimal parallelization
- Support for:
  - Basic arithmetic operations (+, -, *, /)
  - Pre/post increment operations (++x, x++)
  - Compound assignments (+=, -=, *=, /=)
- Logging for debugging
- Test coverage

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd calculator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```python
from src.calculator import Calculator
from src.config import Config, ExecutionMode

# Create a calculator with queue-based execution
config = Config(execution_mode=ExecutionMode.QUEUE)
calc = Calculator(config=config)

# Evaluate single expression
result = calc.evaluate("x = 1 + 2")

# Evaluate multiple expressions
expressions = [
    "x = 1",
    "y = 2",
    "z = x + y"
]
results = calc.evaluate_multiple(expressions)
```

## Execution Modes

The application now supports two execution modes:

1. **Sequential Execution**: Processes expressions one at a time in the order they are provided.

2. **Queue-Based Execution**: Utilizes a queue to dynamically manage and execute expressions based on their dependencies. This mode allows for parallel execution where possible, ensuring that dependent expressions are executed in the correct order.

### Configuration

The execution mode can be configured in the `Config` class. The available modes are `SEQUENTIAL` and `QUEUE`.

### Running the Application

To run the application in a specific mode, update the configuration settings in `config.py`:

```python
from src.config import Config, ExecutionMode

Config.set_execution_mode(ExecutionMode.QUEUE)  # or ExecutionMode.SEQUENTIAL
```

### Testing

The tests have been updated to reflect the changes in execution strategy. Ensure that all tests pass by running:

```bash
pytest tests/
```

## Queue Executor

The Queue Executor is designed to efficiently execute a list of expressions by utilizing a dependency graph to determine the correct execution order. It supports parallel execution of independent expressions, leveraging multiple CPU cores for improved performance.

### Features
- **Dependency Graph**: Automatically builds a dependency graph to manage execution order, ensuring correct handling of variable dependencies.
- **Topological Sort**: Uses topological sorting to determine the execution order of expressions based on their dependencies.
- **Parallel Execution**: Executes independent expressions in parallel using Python's multiprocessing module.
- **Logging**: Provides detailed logs and debug logs to track execution flow and diagnose issues.

### Usage
To use the Queue Executor, initialize it with a desired evaluation strategy and pass a list of expressions to the `execute` method. The executor will return a dictionary of evaluated variable results.

```python
from src.executor import QueueBasedExecutor
from src.evaluator import EvaluationStrategy

expressions = [
    "x = 5",
    "y = x + 2",
    "z = x * 2",
    "w = y + z"
]

executor = QueueBasedExecutor(EvaluationStrategy.AST)
results = executor.execute(expressions)
print(results)  # Output: {'x': 5, 'y': 7, 'z': 10, 'w': 17}
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_calculator.py

# Run with verbose output
pytest -v

# Run with logging output
pytest -v --log-cli-level=DEBUG
```

### Running with Docker

You can run the calculator application and its tests using Docker. This ensures a consistent environment and simplifies dependencies management.

#### Docker Installation

1. Build the Docker image:
```bash
docker build -t expressions-calculator .
```

2. Run the Docker container:
```bash
docker run -it expressions-calculator
```

### Project Structure

```
calculator/
├── src/
│   ├── calculator.py     # Main calculator class
│   ├── config.py         # Configuration management
│   ├── evaluator.py      # Expression evaluation
│   ├── executor.py       # Execution strategies
│   └── logger.py         # Logging configuration
├── tests/
│   ├── test_calculator.py
│   ├── test_evaluator.py
│   └── test_queue_executor.py
├── requirements.txt
└── README.md
