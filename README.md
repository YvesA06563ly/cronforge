# cronforge

> Human-readable cron expression builder and validator with timezone-aware scheduling previews.

---

## Installation

```bash
pip install cronforge
```

---

## Usage

```python
from cronforge import CronBuilder, preview

# Build a cron expression using plain language
cron = (
    CronBuilder()
    .every("weekday")
    .at("09:30")
    .in_timezone("America/New_York")
    .build()
)

print(cron.expression)
# → "30 9 * * 1-5"

print(cron.describe())
# → "At 09:30 AM, Monday through Friday (America/New_York)"

# Preview the next 5 scheduled runs
for run in preview(cron, count=5):
    print(run)
# → 2024-11-18 09:30:00 EST
# → 2024-11-19 09:30:00 EST
# → ...

# Validate an existing expression
from cronforge import validate

result = validate("*/5 * * * *")
print(result.valid)        # True
print(result.description)  # "Every 5 minutes"

# Preview from a specific start time
from datetime import datetime
from zoneinfo import ZoneInfo

start = datetime(2024, 12, 1, 0, 0, tzinfo=ZoneInfo("America/Chicago"))
for run in preview(cron, count=3, start=start):
    print(run)
# → 2024-12-02 09:30:00 CST
# → 2024-12-03 09:30:00 CST
# → 2024-12-04 09:30:00 CST
```

---

## Features

- Fluent builder API for constructing cron expressions
- Human-readable descriptions for any valid cron string
- Timezone-aware scheduling previews using `zoneinfo`
- Validates expressions and surfaces meaningful error messages
- Preview scheduled runs from a custom start datetime

---

## License

This project is licensed under the [MIT License](LICENSE).
