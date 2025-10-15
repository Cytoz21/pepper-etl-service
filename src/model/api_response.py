from dataclasses import dataclass


@dataclass
class APIResponse:
    content: bytes
    filename: str | None
    content_type: str | None
