from dataclasses import dataclass
from datetime import datetime

@dataclass
class PasswordEntry:
    service: str
    username: str
    encrypted_password: bytes
    created_at: datetime = None  # Será populado pelo banco