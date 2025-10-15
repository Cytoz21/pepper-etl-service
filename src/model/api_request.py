from dataclasses import dataclass


@dataclass
class APIRequest:
    url: str
    params: dict[str, str]
    headers: dict[str, str]