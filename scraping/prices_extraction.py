from scraper import Scraper
from database_manager import DatabaseManager

from sqlalchemy import text

class PriceExtractor():
    def __init__(self, db_url="sqlite:///products.db"):
        self.db_manager = DatabaseManager(db_url)
        
    def execute_query(self, query:str='SELECT * FROM products'):
        with self.db_manager.session_scope() as session:
            result = session.execute(text(query))
            rows = result.fetchall()
            return rows


if __name__=='__main__':
    pe = PriceExtractor()
    rows = pe.execute_query()
    print(rows)
