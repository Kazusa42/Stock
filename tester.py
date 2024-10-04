import pandas as pd
import unicodedata

class StockDatabase:
    def __init__(self, raw_data: pd.DataFrame):
        """
        Initialize the StockDatabase with raw stock data.

        Parameters:
        raw_data (pd.DataFrame): A DataFrame where each row represents stock information.
                                 The DataFrame should have at least the following columns:
                                 ['Stock Code', 'Stock Name', 'Price', 'Volume', ...]
        """
        self.raw_data = raw_data

    def _get_display_width(self, text: str) -> int:
        """
        Calculate the display width of a string, considering the different widths of Chinese and English characters.

        Parameters:
        text (str): The input string.

        Returns:
        int: The display width of the string.
        """
        width = 0
        for char in text:
            if unicodedata.east_asian_width(char) in ('F', 'W'):
                width += 2  # Full-width or wide character (like Chinese)
            else:
                width += 1  # Regular-width character (like English)
        return width

    def _format_cell(self, text: str, width: int) -> str:
        """
        Format a cell's content by right-aligning it according to its display width.

        Parameters:
        text (str): The text to format.
        width (int): The target display width for the cell.

        Returns:
        str: The formatted text, right-aligned.
        """
        text_width = self._get_display_width(text)
        padding = width - text_width
        return ' ' * padding + text

    def show_stock_info(self, stock_codes: list):
        """
        Display stock information in a table format for the given stock codes.

        Parameters:
        stock_codes (list): A list of stock codes to display information for.
        """
        # Filter the DataFrame to include only rows with the specified stock codes
        filtered_data = self.raw_data[self.raw_data['stockCode'].isin(stock_codes)]
        
        if filtered_data.empty:
            print("No matching stock found.")
            return

        # Extract column headers and the data to be displayed
        columns = filtered_data.columns.tolist()
        data = filtered_data.values.tolist()

        # Determine the display width of each column for formatting
        col_widths = [max(self._get_display_width(str(val)) for val in [col] + list(filtered_data[col])) for col in columns]

        # Generate table border based on column widths
        border = '+' + '+'.join(['-' * (w + 2) for w in col_widths]) + '+'

        # Function to format each row with right-aligned text
        def format_row(row):
            return '|' + '|'.join([f' {self._format_cell(str(val), w)} ' for val, w in zip(row, col_widths)]) + '|'

        # Print table header
        print(border)
        print(format_row(columns))
        print(border)

        # Print each row of stock information
        for row in data:
            print(format_row(row))
        
        # Print table bottom border
        print(border)

# Example usage:
# Assuming you have a DataFrame 'raw_data' with stock information
# raw_data = pd.read_csv(r'C:\Users\a5149517\Desktop\Stock-main\raw_data\2024_10_04_11_11_raw.csv')
"""

db = StockDatabase(raw_data)
db.show_stock_info(['sh688517', 'sh600180'])"""

def test_prase_command(user_input: str):
    return user_input.split(' ')[1:]

user_input = input('command:').lower().strip()
print(test_prase_command(user_input))

