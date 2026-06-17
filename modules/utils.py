from datetime import datetime


def parse_positive_float(value, default=0.0):
    try:
        number = float(value)
        return number if number >= 0 else default
    except (TypeError, ValueError):
        return default


def validate_category_value(value, allowed_values):
    return value in allowed_values


def parse_iso_date(value):
    try:
        return datetime.fromisoformat(value).date().isoformat()
    except (TypeError, ValueError):
        return datetime.utcnow().date().isoformat()


def positive_float_or_none(value):
    try:
        number = float(value)
        return number if number >= 0 else None
    except (TypeError, ValueError):
        return None
