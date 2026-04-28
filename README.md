# crontab-lint

A static analysis tool for validating and explaining crontab expressions with human-readable output.

---

## Installation

```bash
pip install crontab-lint
```

Or install from source:

```bash
git clone https://github.com/yourname/crontab-lint.git && cd crontab-lint && pip install .
```

---

## Usage

Validate a crontab expression directly from the command line:

```bash
$ crontab-lint "*/5 * * * *"
✔ Valid expression
  Schedule: Every 5 minutes
  Next runs: 2024-01-15 10:05, 10:10, 10:15, 10:20, 10:25
```

Lint an entire crontab file:

```bash
$ crontab-lint --file /etc/cron.d/myjobs
Line 3: ✔  "0 9 * * 1-5"  →  At 09:00, Monday through Friday
Line 7: ✗  "60 * * * *"   →  Error: minute field out of range (0-59)
```

Use it in Python:

```python
from crontab_lint import validate

result = validate("0 9 * * 1-5")
print(result.description)  # "At 09:00, Monday through Friday"
print(result.is_valid)     # True
```

---

## Features

- Validates crontab field ranges and syntax
- Generates plain-English descriptions of schedules
- Shows upcoming run times
- Supports special strings (`@daily`, `@reboot`, etc.)
- Exit codes suitable for CI pipelines

---

## License

MIT © [yourname](https://github.com/yourname)