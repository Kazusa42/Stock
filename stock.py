#---------------------------------------------------------------------------------
# Author: Zhang
# Date: 2024/09/09
# FOR PERSONAL USE ONLY.
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# IMPORT REQUIRED PACKAGES HERE

import warnings
import asyncio
import os
import sys

import pandas as pd

from datetime import datetime

from utils import AsyncStockFetcher, Const, JsonDataProcessor

# END OF PACKAGE IMPORT
#---------------------------------------------------------------------------------

warnings.simplefilter(action=r'ignore', category=FutureWarning)

#---------------------------------------------------------------------------------
# FUNCTIONS DEFINE

def get_output_directory(output_dir_name=r'interest_stock') -> str:
    """
    Get the base directory of the current executable or script 
    and ensure the existence of an output folder.
    
    Returns:
        str: The path to the output directory.
    """
    
    # Determine if the script is running from a packaged executable or in development mode
    if getattr(sys, 'frozen', False):
        # The application is running from a packaged executable
        base_dir = os.path.dirname(sys.executable)
    else:
        # The application is running in a development environment (script mode)
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # Create the output directory within the base directory if it doesn't exist
    output_dir = os.path.join(base_dir, output_dir_name)
    os.makedirs(output_dir, exist_ok=True)  # This will create the directory if it doesn't exist

    return output_dir



async def async_routine(stock_code_path: str, config_path: str, region_code: str, save_path: str):
    """
    A coroutine to asynchronously fetch and process stock data, then save the results to a CSV file.

    This routine reads a list of stock codes from a CSV file, processes a JSON configuration file 
    to extract necessary parameters, fetches stock data asynchronously, filters the data based 
    on specified thresholds, and saves the filtered data to a CSV file.

    Args:
        stock_code_path (str): The file path to the CSV file containing stock codes.
        config_path (str): The file path to the JSON configuration file.
        region_code (str): The region code used to select data from the JSON file.
        save_path (str): The file path to save the filtered stock data as a CSV file.
    """

    # Load stock codes from the CSV file into a list
    df = pd.read_csv(stock_code_path, header=None)
    stock_code_list = df[df.columns[0]].values.tolist()

    # Process the JSON configuration file to extract necessary parameters
    processor = JsonDataProcessor()
    interest_info_idxs, thresholds, urls = processor.split_json_to_dicts(config_path, region_code)

    # Initialize the AsyncStockFetcher with the stock codes and configuration parameters
    fetcher = AsyncStockFetcher(
        stock_list=stock_code_list,
        interest_info_idxs=interest_info_idxs,
        thresholds=thresholds,
        urls=urls
    )

    # Asynchronously fetch the stock data
    await fetcher.fetch_data()
    
    # Filter the fetched data based on thresholds
    fetcher.filter_data()

    # Save the filtered data to a CSV file
    fetcher.save_data(save_path)


# END OF FUNCTIONS DEFINE
#---------------------------------------------------------------------------------


if __name__ == '__main__':
    #---------------------------------------------------------------------------------
    # CONST VARIABLES ARE DEFINED HERE
    # THESE VARIABLES SHOULD NOT BE MODIFIED WITHOUT AUTHOR'S PERMISSION
    
    # Setting up the region code, which is used to extract specific data from the config file
    Const.REGION_CODE = r'CN'

    # Path to the configuration JSON file
    Const.CONFIG_FILE = str(os.path.dirname(__file__) + '/config.json')

    # Path to the CSV file containing all stock codes
    Const.STOCKCODE_FILE = str(os.path.dirname(__file__) + '/stock_code.csv')

    # Path to the output CSV file that will contain stock codes meeting all requirements (thresholds)
    curr_dir = get_output_directory()
    Const.RESULT_FILE =  curr_dir + f"/{datetime.now().strftime('%Y-%m-%d_%H_%M')}_interest_stock.csv"

    # END OF CONST VARIABLES DEFINITION
    #---------------------------------------------------------------------------------

    #---------------------------------------------------------------------------------
    # MAIN ROUTINE

    # Run the asynchronous routine to fetch, filter, and save stock data
    asyncio.run(async_routine(
        stock_code_path=Const.STOCKCODE_FILE,
        config_path=Const.CONFIG_FILE,
        region_code=Const.REGION_CODE,
        save_path=Const.RESULT_FILE
    ))

    # END OF MAIN ROUTINE
    #---------------------------------------------------------------------------------

    # END OF FILE
    #---------------------------------------------------------------------------------