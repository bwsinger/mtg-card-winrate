from dataclasses import dataclass, field
from typing import Optional
import json_fix

@dataclass
class MTGCard:
    name: str
    quantity: int

    def __json__(self):
        return self.__dict__
