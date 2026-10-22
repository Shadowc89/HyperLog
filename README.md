# Hyperlog

Reusable Python utilities developed by Hyper Source.

## Features

- Detailed exception logging.
- Unique error identifiers.
- Full traceback recording.
- Automatic log file creation.
- Log rotation.
- Common secret redaction.
- Support for synchronous and asynchronous application errors.

## Installation

```bash
pip install hyperlog
```

## Quick Start

```python
from hyperlog import log_exception

try:
    int("invalid")
except ValueError as error:
    error_id = log_exception(
        error,
        context="Input validation",
    )
    print(f"Error ID: {error_id}")
```

## License

MIT License.
