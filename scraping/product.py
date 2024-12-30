from dataclasses import dataclass
from decimal import Decimal

@dataclass
class Product:
    product_name: str
    price: Decimal
    unit_price: Decimal
    unit: str
    package_size: str
    promo: float