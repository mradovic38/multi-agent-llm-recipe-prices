from sqlalchemy import Column, Integer, String, Numeric, Float, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class ProductHelper(Base):
    __tablename__ = 'product_helper'
    id = Column(Integer, primary_key=True, autoincrement=True)
    search_term = Column(String, nullable=False)
    product_name = Column(String, nullable=False, unique=True)
    url = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    unit = Column(String, nullable=False)
    package_size = Column(Float, nullable=False)
    promo = Column(Float, nullable=False)
    contains_allergens = Column(String, nullable=True)
    does_not_contain_allergens = Column(String, nullable=True)
    amount = Column(Integer)
    price_for_amount = Column(Float)

class ProductSQL(Base):
    """SQLAlchemy model for product data."""
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    search_term = Column(String, nullable=False)
    product_name = Column(String, nullable=False, unique=True)
    url = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    unit = Column(String, nullable=False)
    package_size = Column(Float, nullable=False)
    promo = Column(Float, nullable=False)
    contains_allergens = Column(String, nullable=True)
    does_not_contain_allergens = Column(String, nullable=True)
    
    def __repr__(self):
        return (f"<Product(search_term={self.search_term}, product_name={self.product_name}, "
                f"price={self.price}, unit={self.unit}, "
                f"package_size={self.package_size}, promo={self.promo}, "
                f"contains_allergens=[{self.contains_allergens}], "
                f"does_not_contain_allergens=[{self.does_not_contain_allergens}]"
                f"url: {self.url})>")


class SearchHistory(Base):
    """Track search terms and their last search timestamp."""
    __tablename__ = 'search_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    search_term = Column(String, unique=True, nullable=False)
    last_searched = Column(DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<SearchHistory(search_term={self.search_term}, last_searched={self.last_searched})>"