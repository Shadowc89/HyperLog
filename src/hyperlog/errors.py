from __future__ import annotations

import logging
import os
import re
import threading
import traceback
import uuid

from logging.handlers import RotatingFileHandler
from pathlib import Path
from types import TracebackType

_LOGGER: logging.Logger | None = None
_LOG_FILE: Path | None = None
_LOCK = threading.RLock()

_LOGGER_NAME = "hyperlog.errors"
_MAX_LOG_SIZE = 5 * 1024 * 1024
_BACKUP_COUNT = 5


def _redact(text: str) -> str:
    """Redact common secret values before writing logs."""
    patterns = [
        re.compile(r"""(?ix)
            \b(
                bot[_-]?token |
                api[_-]?key |
                password |
                passwd |
                secret |
                authorization |
                access[_-]?token |
                refresh[_-]?token
            )\b
            (\s*[:=]\s*)
            (["']?)[^\s,;'"&]+
            """),
        re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+"),
    ]

    for pattern in patterns:
        if pattern.pattern.startswith("(?i)"):
            text = pattern.sub("Bearer <REDACTED>", text)
        else:
            text = pattern.sub(r"\1\2<REDACTED>", text)

    return text


def _get_logger() -> logging.Logger:
    """Initialize the logger once, safely across threads."""
    global _LOGGER, _LOG_FILE

    with _LOCK:
        if _LOGGER is not None:
            return _LOGGER

        log_dir = Path(
            os.getenv(
                "HYPERLOG_LOG_DIR",
                str(Path.cwd() / "logs"),
            )
        ).expanduser()

        log_dir.mkdir(parents=True, exist_ok=True)

        _LOG_FILE = log_dir / "errors.log"

        logger = logging.getLogger(_LOGGER_NAME)
        logger.setLevel(logging.ERROR)
        logger.propagate = False

        # Avoid duplicate handlers after repeated initialization.
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s\n%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler = RotatingFileHandler(
            _LOG_FILE,
            maxBytes=_MAX_LOG_SIZE,
            backupCount=_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        _LOGGER = logger
        return logger


def log_exception(
    error: BaseException,
    *,
    context: str | None = None,
) -> str:
    """
    Record an exception and return its unique error ID.

    This function records the error but does not suppress,
    re-raise, or otherwise handle the exception for the caller.
    """
    if not isinstance(error, BaseException):
        raise TypeError("error must be an exception instance")

    error_id = f"HL-{uuid.uuid4().hex[:12].upper()}"

    tb: TracebackType | None = error.__traceback__
    frames = traceback.extract_tb(tb) if tb else []

    if frames:
        # The last frame is the immediate location where the
        # exception was raised.
        frame = frames[-1]
        filename = frame.filename
        function = frame.name
        line = frame.lineno
    else:
        filename = "<unknown>"
        function = "<unknown>"
        line = 0

    message = str(error) or "<no error message>"

    if tb is not None:
        full_traceback = "".join(
            traceback.format_exception(
                type(error),
                error,
                tb,
            )
        )
    else:
        full_traceback = "Traceback unavailable: exception has no traceback."

    details = [
        "=" * 72,
        f"Error ID: {error_id}",
        f"Exception: {type(error).__name__}",
        f"Message: {message}",
        f"File: {filename}",
        f"Function: {function}",
        f"Line: {line}",
    ]

    if context:
        details.append(f"Context: {context}")

    details.extend(
        [
            "",
            "Full Traceback:",
            full_traceback.rstrip(),
            "=" * 72,
        ]
    )

    report = _redact("\n".join(details))

    # Logging normally should not change the application's
    # exception handling behavior.
    try:
        _get_logger().error("%s", report)
    except OSError:
        # Do not silently claim the log was saved. If logging
        # fails, emit a minimal fallback to stderr.
        import sys

        print(
            f"HyperLog could not write the log file. " f"Error ID: {error_id}",
            file=sys.stderr,
        )
        print(report, file=sys.stderr)

    return error_id


def get_log_file() -> Path:
    """Return the configured log file path."""
    _get_logger()

    if _LOG_FILE is None:
        raise RuntimeError("HyperLog logger was not initialized")

    return _LOG_FILE


def reset_logger() -> None:
    """
    Close and remove this logger's handlers.

    Intended for tests or controlled application shutdown.
    The next logging call will initialize it again.
    """
    global _LOGGER, _LOG_FILE

    with _LOCK:
        logger = logging.getLogger(_LOGGER_NAME)

        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

        _LOGGER = None
        _LOG_FILE = None
