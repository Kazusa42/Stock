import os
import pandas as pd
import asyncio

from datetime import datetime

from utils.component import Const, JsonDataProcessor

# Mock data for testing

Const.REGION_CODE = 'CN'

"""# Define the paths for the configuration JSON file and the stock codes CSV file
Const.CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
Const.STOCKCODE_FILE = os.path.join(os.path.dirname(__file__), 'stock_code.csv')

# Define the path for the output CSV file
Const.RESULT_FILE = os.path.join(output_directory, f"{datetime.now().strftime('%Y-%m-%d_%H_%M')}_raw_stock_info.csv")

# Test save path
save_path = 'test_raw_data.csv'

# Mock progress callback to print progress updates
def progress_callback(progress):
    import sys
    sys.stdout.flush()
    print(f"Progress: {progress:.2f}%", end='\r')


df = pd.read_csv(Const.STOCKCODE_FILE, header=None)
stock_code_list = df[df.columns[0]].values.tolist()[:100]

# Process the JSON configuration file to extract necessary parameters
processor = JsonDataProcessor()
interest_info_idxs, thresholds, urls = processor.split_json_to_dicts(Const.CONFIG_FILE, Const.REGION_CODE)

# Test function for AsyncStockFetcher
async def test_async_stock_fetcher():
    # Initialize the fetcher
    fetcher = AsyncStockFetcher(stock_code_list, urls, interest_info_idxs, progress_callback=progress_callback)
    
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
        print(f"Test failed: File {save_path} was not created.")"""


# Main test entry point
if __name__ == '__main__':
    # Run the async test function
    # asyncio.run(test_async_stock_fetcher())
    Const.STOCKCODE_FILE = os.path.join(os.path.dirname(__file__), 'stock_code.csv')
    print(datetime.now().strftime('%Y-%m-%d %H:%M'))

    # Clean up the test file
    """if os.path.exists(save_path):
        os.remove(save_path)
        print(f"Test file {save_path} removed.")"""
    
    # Run the stock filter tests
    # test_stock_filter()
    
    # Clean up the test files
    """if os.path.exists(filtered_data_path):
        os.remove(filtered_data_path)
        print(f"Test file {filtered_data_path} removed.")"""
"""    stock_code = "sz000011"
    url = f"http://ifzq.gtimg.cn/appstock/app/kline/mkline?param={stock_code},m1,,10"

    params = {
        'fields': "f1, f2, f3",
    }
    
    import requests
    import json

    response = requests.get(url, allow_redirects=True, params=params)
    text = response.content
    information = json.loads(text)
    raw_data = information['data'][stock_code]['qt'][stock_code]
    print(raw_data)
"""