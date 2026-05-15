"""Human-readable descriptions of cron expressions."""

from cronforge.parser import CronExpression, CronParseError

DAY_NAMES = [
    "Sunday", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday"
]

MONTH_NAMES = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]


class HumanizerError(Exception):
    """Raised when humanization fails."""


def _describe_field(value: str, field_name: str, names: list[str] | None = None) -> str:
    """Return a human-readable description of a single cron field value."""
    if value == "*":
        return f"every {field_name}"

    if value.startswith("*/"):
        step = value[2:]
        return f"every {step} {field_name}s"

    if "-" in value and "/" in value:
        range_part, step = value.split("/")
        start, end = range_part.split("-")
        if names:
            start = names[int(start)] if start.isdigit() else start
            end = names[int(end)] if end.isdigit() else end
        return f"every {step} {field_name}s from {start} through {end}"

    if "-" in value:
        start, end = value.split("-")
        if names:
            start = names[int(start)] if start.isdigit() else start
            end = names[int(end)] if end.isdigit() else end
        return f"{field_name}s {start} through {end}"

    if "," in value:
        parts = value.split(",")
        if names:
            parts = [names[int(p)] if p.isdigit() else p for p in parts]
        return f"{field_name}s {', '.join(parts[:-1])} and {parts[-1]}"

    if names and value.isdigit():
        return names[int(value)]

    return f"{field_name} {value}"


def humanize(expression: str) -> str:
    """Convert a cron expression string into a human-readable sentence."""
    try:
        cron = CronExpression(expression)
    except CronParseError as e:
        raise HumanizerError(f"Invalid cron expression: {e}") from e

    fields = str(cron).split()
    minute, hour, dom, month, dow = fields

    parts = []

    if minute == "*" and hour == "*":
        parts.append("every minute")
    elif minute.startswith("*/") and hour == "*":
        parts.append(_describe_field(minute, "minute"))
    else:
        min_desc = _describe_field(minute, "minute")
        hr_desc = _describe_field(hour, "hour")
        parts.append(f"at {min_desc} past {hr_desc}")

    if dom != "*":
        parts.append(f"on day {_describe_field(dom, 'day-of-month')} of the month")

    if month != "*":
        parts.append(f"in {_describe_field(month, 'month', MONTH_NAMES)}")

    if dow != "*":
        parts.append(f"on {_describe_field(dow, 'weekday', DAY_NAMES)}")

    return ", ".join(parts)
