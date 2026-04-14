"""
logger.py — Standard library logging wrapper.

Returns a stdlib logging.Logger so that log calls (logger.info, logger.error,
logger.warning, logger.debug) work identically everywhere, with zero external
dependencies (no structlog, no PrintLogger).

All existing callers require no changes:
    from backend.utils.logger import setup_logger
    logger = setup_logger("my_module")
    logger.info("msg", key=value)   ← keyword args are silently dropped
                                       by stdlib, which is fine
"""

import logging
import sys
from pathlib import Path


def setup_logger(name: str = "chainbreaker", level: str = "INFO") -> logging.Logger:
    """
    Return a configured stdlib Logger for the given name.

    Creates the logs/ directory and attaches a StreamHandler (stdout) if the
    logger has no handlers yet, so repeated calls are idempotent.
    """
    Path("logs").mkdir(exist_ok=True)

    logger = logging.getLogger(name)

    # Set level only if not already configured by a parent
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    if not logger.level:
        logger.setLevel(numeric_level)

    # Avoid duplicate handlers on repeated calls
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(numeric_level)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
