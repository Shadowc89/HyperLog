import asyncio
import logging
import re
import secrets
import time

from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


# 1. Generate secure IDs
def generate_id(length: int = 32) -> str:
    if length < 1:
        raise ValueError("length must be positive")

    return secrets.token_hex((length + 1) // 2)[:length]


# 2. Clean text
def clean_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    return re.sub(r"\s+", " ", text).strip()


# 3. Retry synchronous operations
def retry(
    func: Callable[[], T],
    attempts: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (ConnectionError, TimeoutError),
) -> T:
    if attempts < 1:
        raise ValueError("attempts must be at least 1")

    if delay < 0:
        raise ValueError("delay cannot be negative")

    for attempt in range(attempts):
        try:
            return func()
        except exceptions:
            if attempt == attempts - 1:
                raise

            time.sleep(delay)

    raise RuntimeError("Unexpected retry state")


# 4. Retry asynchronous operations
async def async_retry(
    func: Callable,
    attempts: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (ConnectionError, TimeoutError),
):
    if attempts < 1:
        raise ValueError("attempts must be at least 1")

    if delay < 0:
        raise ValueError("delay cannot be negative")

    for attempt in range(attempts):
        try:
            return await func()
        except exceptions:
            if attempt == attempts - 1:
                raise

            await asyncio.sleep(delay)

    raise RuntimeError("Unexpected retry state")


# 5. Configure logging
def setup_logging(
    name: str = "hyperlog",
    file: str = "hyperlog.log",
    level: int = logging.INFO,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console = logging.StreamHandler()
        console.setFormatter(formatter)

        logger.addHandler(console)

        if file:
            file_handler = logging.FileHandler(
                file,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger
