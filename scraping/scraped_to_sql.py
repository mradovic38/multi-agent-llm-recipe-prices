from product import Product

from sqlalchemy import create_engine, Column, Integer, String, Numeric, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import List, Optional
from decimal import Decimal


Base = declarative_base()

class ProductSQL(Base):
    """SQLAlchemy model for product data."""
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    search_term = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    unit = Column(String, nullable=False)
    package_size = Column(String, nullable=False)
    promo = Column(Float, nullable=True)
    contains_allergens = Column(String, nullable=True)
    does_not_contain_allergens = Column(String, nullable=True)

    def __repr__(self):
        return f"""<Product(search_term={self.search_term}, product_name={self.product_name}, price={self.price}, 
        unit_price={self.unit_price}, unit={self.unit}, package_size={self.package_size}, promo={self.promo}, 
        contains_allergens=[{self.contains_allergens}], does_not_contain_allergens=[{self.does_not_contain_allergens}])>"""


class ScrapedToSqlConverter:
    """Handles database operations and conversion of scraped data to SQL format."""
    
    def __init__(self, database_url: str = "sqlite:///products.db"):
        """Initialize the converter with database connection."""
        self.database_url = database_url
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def product_to_sql(self, product: Product) -> ProductSQL:
        """Convert a Product dataclass instance to a ProductSQL instance."""
        return ProductSQL(
            search_term=product.search_term,
            product_name=product.product_name,
            price=product.price,
            unit_price=product.unit_price,
            unit=product.unit,
            package_size=product.package_size,
            promo=product.promo,
            contains_allergens=",".join(product.contains_allergens) if product.contains_allergens else "",
            does_not_contain_allergens=",".join(product.does_not_contain_allergens) if product.does_not_contain_allergens else ""
        )

    def bulk_insert_from_products(self, products: List[Product], batch_size: int = 1000) -> None:
        """
        Insert multiple Product dataclass instances into the database in batches.
        
        Args:
            products: List of Product dataclass instances
            batch_size: Number of records to insert at once (default: 1000)
        """
        session = self.Session()
        try:
            # Convert Product instances to ProductSQL instances
            sql_products = [self.product_to_sql(product) for product in products]
            
            # Insert in batches
            for i in range(0, len(sql_products), batch_size):
                batch = sql_products[i:i + batch_size]
                session.add_all(batch)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_all_products(self) -> List[ProductSQL]:
        """Retrieve all products from the database."""
        session = self.Session()
        try:
            return session.query(ProductSQL).all()
        finally:
            session.close()

    def get_product_by_name(self, product_name: str) -> Optional[ProductSQL]:
        """Retrieve a product by its name."""
        session = self.Session()
        try:
            return session.query(ProductSQL).filter(ProductSQL.product_name == product_name).first()
        finally:
            session.close()


# Example usage:
if __name__ == "__main__":
    # Initialize the converter
    converter = ScrapedToSqlConverter()
    
    # Example list of Product instances
    products_list = [
        Product(
            search_term="mleko",
            product_name="sveze mleko moja kravica",
            price=Decimal("145"),
            unit_price=Decimal("0.45"),
            unit="L",
            package_size="1.45L",
            promo=None,
            contains_allergens=["mleko"],
            does_not_contain_allergens=["lupina", "slačica", "celer"]
        ),
        Product(
            search_term="jogurt",
            product_name="jogurt natural",
            price=Decimal("299.99"),
            unit_price=Decimal("0.60"),
            unit="L",
            package_size="500ml",
            promo=None,
            contains_allergens=["mleko"],
            does_not_contain_allergens=["lupina", "slačica"]
        )
    ]
    
    # Bulk insert the products
    converter.bulk_insert_from_products(products_list)
    
    # Verify the insertion
    all_products = converter.get_all_products()
    for product in all_products:
        print(product)