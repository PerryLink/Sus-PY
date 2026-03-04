"""Safe Python code for testing."""
import json
import math
from datetime import datetime


def calculate_sum(numbers):
    """Calculate sum of numbers."""
    return sum(numbers)


def format_date(date):
    """Format date as string."""
    return date.strftime("%Y-%m-%d")


if __name__ == "__main__":
    data = {"name": "test", "value": 42}
    print(json.dumps(data))
    print(calculate_sum([1, 2, 3, 4, 5]))
    print(format_date(datetime.now()))
