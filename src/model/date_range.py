from dataclasses import dataclass
from datetime import date


@dataclass
class DateRange:
    start: date
    end: date