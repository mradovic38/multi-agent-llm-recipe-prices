from sql_tables import ProductSQL, SearchHistory
from database_manager import DatabaseManager

from typing import Optional, List, Dict, Any
from tabulate import tabulate
from datetime import datetime

class DatabaseDisplay:
    def __init__(self, database_url: str = "sqlite:///products.db"):
        self.db_manager = DatabaseManager(database_url)
        
        # Define available columns with their display names and formatting functions
        self.product_columns = {
            'search_term': {
                'display': 'Search Term',
                'format': lambda x: x
            },
            'product_name': {
                'display': 'Product Name',
                'format': lambda x: x
            },
            'url': {
                'display': 'URL',
                'format': lambda x: x
            },
            'price': {
                'display': 'Price',
                'format': lambda x: float(x)
            },
            'unit': {
                'display': 'Unit',
                'format': lambda x: x
            },
            'package_size': {
                'display': 'Package',
                'format': lambda x: float(x)
            },
            'promo': {
                'display': 'Promo',
                'format': lambda x: f"{x*100:.1f}%" if x is not None else "N/A"
            },
            'contains_allergens': {
                'display': 'Contains',
                'format': lambda x: x or "None"
            },
            'does_not_contain_allergens': {
                'display': 'Does Not Contain',
                'format': lambda x: x or "None"
            }
        }

        self.history_columns = {
            'search_term': {
                'display': 'Search Term',
                'format': lambda x: x
            },
            'last_searched': {
                'display': 'Last Searched',
                'format': lambda x: x.strftime('%Y-%m-%d %H:%M:%S')
            },
            'days_ago': {
                'display': 'Days Ago',
                'format': lambda x: f"{x} days"
            }
        }

    def display_products(self, 
                        columns: Optional[List[str]] = None, 
                        search_term: Optional[str] = None,
                        sort_by: Optional[str] = None,
                        reverse: bool = False) -> None:
        """
        Display products in a formatted table.
        
        Args:
            columns: List of column names to display. If None, displays all columns.
            search_term: Optional filter for specific search term.
            sort_by: Column name to sort by.
            reverse: Sort in descending order if True.
        """
        # Validate and prepare columns
        if columns:
            invalid_cols = [col for col in columns if col not in self.product_columns]
            if invalid_cols:
                raise ValueError(f"Invalid columns: {', '.join(invalid_cols)}. "
                               f"Available columns: {', '.join(self.product_columns.keys())}")
        else:
            columns = list(self.product_columns.keys())

        with self.db_manager.session_scope() as session:
            # Build query
            query = session.query(ProductSQL)
            if search_term:
                query = query.filter(ProductSQL.search_term == search_term)
            
            # Apply sorting
            if sort_by:
                if sort_by not in self.product_columns:
                    raise ValueError(f"Invalid sort column: {sort_by}")
                sort_col = getattr(ProductSQL, sort_by)
                query = query.order_by(sort_col.desc() if reverse else sort_col)

            products = query.all()

            if not products:
                print("No products found in database.")
                return

            # Prepare headers and formatting functions
            headers = [self.product_columns[col]['display'] for col in columns]
            formatters = [self.product_columns[col]['format'] for col in columns]

            # Prepare rows
            rows = []
            for product in products:
                row = []
                for col, formatter in zip(columns, formatters):
                    value = getattr(product, col)
                    row.append(formatter(value))
                rows.append(row)

            print("\n=== Products in Database ===")
            print(tabulate(rows, headers=headers, tablefmt='grid'))
            print(f"Total products: {len(products)}")

    def display_search_history(self, columns: Optional[List[str]] = None) -> None:
        """
        Display search history in a formatted table.
        
        Args:
            columns: List of column names to display. If None, displays all columns.
        """
        if columns:
            invalid_cols = [col for col in columns if col not in self.history_columns]
            if invalid_cols:
                raise ValueError(f"Invalid columns: {', '.join(invalid_cols)}. "
                               f"Available columns: {', '.join(self.history_columns.keys())}")
        else:
            columns = list(self.history_columns.keys())

        with self.db_manager.session_scope() as session:
            history = session.query(SearchHistory).all()

            if not history:
                print("No search history found in database.")
                return

            headers = [self.history_columns[col]['display'] for col in columns]
            now = datetime.now()

            rows = []
            for h in history:
                row = []
                for col in columns:
                    if col == 'days_ago':
                        value = (now - h.last_searched).days
                    else:
                        value = getattr(h, col)
                    row.append(self.history_columns[col]['format'](value))
                rows.append(row)

            print("\n=== Search History ===")
            print(tabulate(rows, headers=headers, tablefmt='grid'))
            print(f"Total searches: {len(history)}")

    def get_available_columns(self) -> Dict[str, List[str]]:
        """Return available columns for both products and search history."""
        return {
            'products': list(self.product_columns.keys()),
            'search_history': list(self.history_columns.keys())
        }


# Example usage
def main():
    display = DatabaseDisplay()
    
    # Show available columns
    columns = display.get_available_columns()
    print("Available product columns:", columns['products'])
    print("Available history columns:", columns['search_history'])

    # Display products with selected columns
    display.display_products(columns=['product_name', 'price', 'promo'])
    
    # Display products sorted by price
    display.display_products(
        columns=['search_term','product_name', 'price', 'unit', 'package_size'],
        sort_by='price',
        reverse=True
    )
    
    # Display search history with selected columns
    display.display_search_history(columns=['search_term', 'days_ago'])

if __name__ == "__main__":
    main()