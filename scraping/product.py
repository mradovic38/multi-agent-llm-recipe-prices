from dataclasses import dataclass
from decimal import Decimal

from typing import Optional

@dataclass
class Product:
    product_name: str
    price: Decimal
    unit_price: Decimal
    unit: str
    package_size: str
    promo: Optional[float] = None