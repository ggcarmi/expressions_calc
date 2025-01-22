"""
Expression execution strategies.
"""
from abc import ABC, abstractmethod
from multiprocessing import Queue, Process, cpu_count, Lock, Manager
from typing import Dict, List, Set, Optional
import queue
import logging

from .evaluator import EvaluationStrategy, EvaluatorFactory
from .logger import executor_logger as logger, dependency_logger as dep_logger
from .dependency_graph import DependencyGraph
from .config import Config, ExecutionMode

# Set up logging
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)
dep_logger.setLevel(logging.INFO)


class ExpressionExecutor(ABC):
    """Base class for expression executors."""
    
    def __init__(self, strategy: EvaluationStrategy):
        """Initialize with evaluation strategy."""
        self.evaluator = EvaluatorFactory.create_evaluator(strategy)
        
    @abstractmethod
    def execute(self, expressions: List[str]) -> Dict[str, int]:
        """Execute expressions using specific strategy."""
        pass


class SequentialExecutor(ExpressionExecutor):
    """Executor that processes expressions sequentially."""

    def __init__(self, strategy: EvaluationStrategy):
        self.strategy = strategy
        self.evaluator = EvaluatorFactory.create_evaluator(strategy)

    def execute(self, expressions: List[str]) -> Dict[str, int]:
        """Execute expressions sequentially."""
        if not expressions:
            return {}

        logger.info("Starting sequential execution of %d expressions", len(expressions))

        variables = {}
        results = {}

        for expr in expressions:
            try:
                logger.debug(f"Executing: {expr}, current variables: {variables}")
                var, val = self.evaluator.evaluate(expr, variables)

                results.update(variables)

                logger.debug(f"After execution: var={var}, val={val}, variables={variables}, results={results}")
            except Exception as e:
                logger.error("Error executing expression %s: %s", expr, str(e))
                raise

        return results


class QueueBasedExecutor(ExpressionExecutor):
    """Executor that uses topological sorting to manage execution order based on dependencies."""

    def __init__(self, strategy: EvaluationStrategy):
        super().__init__(strategy)
        self.num_workers = cpu_count()
        self.strategy = strategy

        # Initialize multiprocessing resources
        self.manager = Manager()
        self.shared_variables = self.manager.dict()
        self.work_queue = Queue()
        self.result_queue = Queue()
        self.state_lock = Lock()

    def __del__(self):
        """Cleanup resources."""
        try:
            self.manager.shutdown()
        except:
            pass

    @staticmethod
    def worker_process(strategy, work_queue, result_queue, state_lock, shared_variables):
        """
        Steps:
            1. Create an evaluator instance using the provided strategy.
            2. Continuously process expressions from the work queue until it is empty.
            3. For each expression:
               a. Retrieve the expression from the work queue.
               b. Acquire the state lock and copy the current shared variables.
               c. Evaluate the expression using the evaluator.
               d. If evaluation is successful, put the result in the result queue.
               e. If evaluation fails, log the error and put the error in the result queue.
            4. Handle any unexpected errors during processing.
        """
        evaluator = EvaluatorFactory.create_evaluator(strategy)

        while True:
            try:
                try:
                    expr = work_queue.get_nowait()
                except queue.Empty:
                    break

                logger.debug(f"Worker processing: {expr}")

                with state_lock:
                    current_vars = dict(shared_variables)

                try:
                    var, value = evaluator.evaluate(expr, current_vars)
                    if var is not None:
                        result_queue.put((var, value))
                        logger.debug(f"Worker completed: {var} = {value}")
                except Exception as e:
                    logger.error(f"Worker failed on '{expr}': {str(e)}")
                    result_queue.put(('error', (expr, str(e))))
                    break

            except Exception as e:
                logger.error(f"Worker process error: {str(e)}")
                break

    def execute(self, expressions: List[str]) -> Dict[str, int]:
        """Execute expressions using topological sorting to manage dependencies."""
        if not expressions:
            return {}

        try:
            # Clear previous state
            self.shared_variables.clear()
            
            logger.info("\n=== Starting Queue-Based Parallel Execution ===")
            logger.info("Input expressions (%d):", len(expressions))
            for i, expr in enumerate(expressions, 1):
                logger.info("%d. %s", i, expr)
            
            # Build dependency graph and get levels
            dependency_graph = DependencyGraph(expressions)
            
            logger.debug("\nDependency Analysis:")
            for expr, deps in dependency_graph.graph.items():
                logger.debug("'%s' depends on: %s", expr, sorted(list(deps)) if deps else "none")

            # Process each level in parallel, but wait for level completion
            level_groups = dependency_graph.get_expression_levels()
            for level, level_expressions in sorted(level_groups.items()):
                logger.debug(f"\nProcessing level {level} expressions: {level_expressions}")
                
                # Start worker processes for this level
                num_workers = min(self.num_workers, len(level_expressions))
                logger.debug(f"Starting {num_workers} workers for level {level}")
                
                processes = []
                for _ in range(num_workers):
                    p = Process(target=self.worker_process,
                                args=(self.strategy, self.work_queue, self.result_queue, self.state_lock, self.shared_variables))
                    p.start()
                    processes.append(p)

                # Queue all expressions for this level
                for expr in level_expressions:
                    self.work_queue.put(expr)

                # Collect results for this level
                errors = []
                completed = 0
                expected = len(level_expressions)
                level_results = []  # Collect all results before applying

                while completed < expected:
                    try:
                        var, value = self.result_queue.get(timeout=10)
                        if var == 'error':
                            errors.append(value)
                            break
                        level_results.append((var, value))
                        logger.info(f"Level {level} - Result ready: {var} = {value}")
                        completed += 1
                    except queue.Empty:
                        logger.warning(f"Timeout waiting for level {level} results")
                        break

                # Wait for level's processes to complete - before moving on to the next level of expressions
                for p in processes:
                    p.join(timeout=5)
                    if p.is_alive():
                        p.terminate()

                # Check for level errors
                if errors:
                    raise RuntimeError(f"Errors during level {level} execution: {errors}")

                # Apply all results atomically
                with self.state_lock:
                    for var, value in level_results:
                        self.shared_variables[var] = value
                    logger.info(f"Level {level} state: {dict(self.shared_variables)}")

                logger.info(f"Completed level {level}")

            logger.info("\nParallel execution complete")
            logger.info("Final results: %s", dict(self.shared_variables))
            return dict(self.shared_variables)

        except Exception as e:
            logger.error("Parallel execution failed: %s", str(e))
            raise

    def _get_target(self, expr: str) -> str:
        """Helper to get target variable from expression."""
        return expr.split('=')[0].strip()


class ExecutorFactory:
    """Factory for creating executors."""
    
    @staticmethod
    def create_executor(strategy: EvaluationStrategy = EvaluationStrategy.AST) -> ExpressionExecutor:
        """Create an executor based on current configuration."""
        mode = Config.get_execution_mode()
        logger.info(f"Creating executor for mode: {mode}")
        
        if mode == ExecutionMode.QUEUE:
            logger.info("Creating queue-based parallel executor")
            return QueueBasedExecutor(strategy)
        else:
            logger.info("Creating sequential executor")
            return SequentialExecutor(strategy)
