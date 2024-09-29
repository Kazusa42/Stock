import os
import pandas as pd
import asyncio

from datetime import datetime

from utils import AsyncStockFetcher, Const, JsonDataProcessor, StockFilter
from stock import get_output_directory

# Mock data for testing

Const.REGION_CODE = 'CN'

# Define the paths for the configuration JSON file and the stock codes CSV file
Const.CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
Const.STOCKCODE_FILE = os.path.join(os.path.dirname(__file__), 'stock_code.csv')

# Define the path for the output CSV file
output_directory = get_output_directory()
Const.RESULT_FILE = os.path.join(output_directory, f"{datetime.now().strftime('%Y-%m-%d_%H_%M')}_raw_stock_info.csv")

# Test save path
save_path = 'test_raw_data.csv'

# Mock progress callback to print progress updates
def progress_callback(progress):
    print(f"Progress: {progress:.2f}%")


df = pd.read_csv(Const.STOCKCODE_FILE, header=None)
stock_code_list = df[df.columns[0]].values.tolist()

# Process the JSON configuration file to extract necessary parameters
processor = JsonDataProcessor()
interest_info_idxs, thresholds, urls = processor.split_json_to_dicts(Const.CONFIG_FILE, Const.REGION_CODE)

# Test function for AsyncStockFetcher
async def test_async_stock_fetcher():
    # Initialize the fetcher
    fetcher = AsyncStockFetcher(stock_code_list, urls, progress_callback=progress_callback)
    
    # Run the fetcher to get data
    await fetcher.fetch_data()

    # Save the raw data to CSV
    fetcher.save_data(save_path)

    # Check if the CSV file was created
    if os.path.exists(save_path):
        print(f"Test passed: File {save_path} created successfully.")
        
        # Load the data and inspect it
        df = pd.read_csv(save_path)
        print(f"Loaded data:\n{df.head()}")
        
        # Optionally, add more checks to verify the content
        if not df.empty:
            print(f"Test passed: Data saved successfully with {len(df)} rows.")
        else:
            print(f"Test failed: No data saved to {save_path}.")
    else:
        print(f"Test failed: File {save_path} was not created.")

#------------------------------------------------------------------------------------------------
# test code for stockfilter class

# Mock data to simulate raw stock data saved by AsyncStockFetcher

# Test save path
raw_data_path = 'test_raw_data.csv'
filtered_data_path = 'test_filtered_data.csv'

# Step 2: Test StockFilter functionality
def test_stock_filter():
    # Initialize the StockFilter class
    filterer = StockFilter(interest_info_idxs, thresholds)
    
    # Load the raw data
    raw_df = filterer.load_data(raw_data_path)
    
    # Test if the data is loaded correctly
    if not raw_df.empty:
        print("Test passed: Raw data loaded successfully.")
        print(f"Loaded data:\n{raw_df}")
    else:
        print("Test failed: Raw data not loaded correctly.")
        return
    
    # Step 3: Test column filtering
    filtered_columns_df = filterer.filter_interested_value(raw_df)
    expected_columns = list(interest_info_idxs.keys())
    
    # Check if the filtered columns match the expected columns
    if list(filtered_columns_df.columns) == expected_columns:
        print("Test passed: Columns filtered successfully.")
        print(f"Filtered columns:\n{filtered_columns_df}")
    else:
        print(f"Test failed: Columns not filtered correctly. Got {list(filtered_columns_df.columns)}")

    # Step 4: Test row filtering based on thresholds
    filterer.filter_stock(filtered_columns_df)
    
    # Check if rows are filtered based on price thresholds
    filtered_rows_df = filterer.results
    if not filtered_rows_df.empty:
        print("Test passed: Rows filtered successfully.")
        print(f"Filtered rows:\n{filtered_rows_df}")
    else:
        print("Test failed: Rows not filtered correctly.")
    
    # Save the filtered data
    filterer.save_filtered_data(filtered_data_path)
    
    # Step 5: Verify the filtered data was saved correctly
    if os.path.exists(filtered_data_path):
        print(f"Test passed: Filtered data saved to {filtered_data_path}.")
        df = pd.read_csv(filtered_data_path)
        print(f"Loaded filtered data:\n{df}")
    else:
        print(f"Test failed: Filtered data not saved.")


# Main test entry point
if __name__ == '__main__':
    # Run the async test function
    # asyncio.run(test_async_stock_fetcher())

    # Clean up the test file
    """if os.path.exists(save_path):
        os.remove(save_path)
        print(f"Test file {save_path} removed.")"""
    
    # Run the stock filter tests
    test_stock_filter()
    
    # Clean up the test files
    """if os.path.exists(filtered_data_path):
        os.remove(filtered_data_path)
        print(f"Test file {filtered_data_path} removed.")"""
