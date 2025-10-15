from dataclasses import dataclass
from .date_range import DateRange


@dataclass
class APIParams:
    fundo: int
    cartilla: int
    cultivo: int
    fechas: DateRange
    ruc_empresa: str
