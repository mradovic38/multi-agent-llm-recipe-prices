from .sql_tables import Base, ProductHelper

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import Generator


class DatabaseManager:
    def __init__(self, database_url: str = "sqlite:///products.db"):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionFactory = sessionmaker(bind=self.engine)

    @contextmanager
    def session_scope(self) -> Generator:
        """Provide a transactional scope around a series of operations."""
        session = self.SessionFactory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def reinitialize_product_helper(self):
        """Drop and recreate the product_helper table."""
        ProductHelper.__table__.drop(self.engine, checkfirst=True)  # Drop table if it exists
        ProductHelper.__table__.create(self.engine)  # Recreate the table
