from dataclasses import dataclass, field
from decimal import Decimal

from typing import Optional, List

@dataclass
class Ingredient:
    name: str
    amount: float
    unit: str