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

Copyright (c) 2026 Hyper Source

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.