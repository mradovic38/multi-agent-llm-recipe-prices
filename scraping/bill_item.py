from dataclasses import dataclass, field
from decimal import Decimal

from typing import Optional, List

@dataclass
class BillItem:
    search_term: str
    product_name: str
    url: str
    price: Decimal
    unit: str
    package_size: float
    amount: int
    price_for_amount: Decimal
    promo: Optional[float] = 0
    contains_allergens: Optional[List[str]] = field(default_factory=list)
    does_not_contain_allergens: Optional[List[str]] = field(default_factory=list)
    
    def __post_init__(self):
        if self.contains_allergens is None:
            self.contains_allergens = []
        if self.does_not_contain_allergens is None:
            self.does_not_contain_allergens = [] 