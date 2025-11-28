from dataclasses import dataclass

@dataclass
class Fundo:
    name: str
    code: str

    def __str__(self):
        return self.name

@dataclass
class Cartilla:
    name: str
    code: int

    def __str__(self):
        return f"{self.code} - {self.name}"
