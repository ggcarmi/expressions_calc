import logging

def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Set specific loggers to DEBUG level
    logging.getLogger('src.expression_simplifier').setLevel(logging.DEBUG)
    logging.getLogger('src.evaluator').setLevel(logging.DEBUG) 