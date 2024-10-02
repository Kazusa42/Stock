# -*- coding:utf-8 -*-
# !/usr/bin/env python
#---------------------------------------------------------------------------------
# Author: Zhang
# FOR PERSONAL USE ONLY.
#
# Create Date: 2024/09/09
# Last Update on: 2024/10/03
#
# FILE: functions.py
# Description: functions which will be used in main loop are defined here
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# IMPORT REQUIRED PACKAGES HERE

import warnings
import os
import sys
import platform

import pandas as pd

from datetime import datetime

from .component import JsonDataProcessor
from .stock import AsyncStockFetcher

# END OF PACKAGE IMPORT
#---------------------------------------------------------------------------------

warnings.simplefilter(action=r'ignore', category=FutureWarning)

#---------------------------------------------------------------------------------
# DEFINE GLOBAL VARIABLES HERE

# default output directory name
_output_dir_name = 'interest_stock'

# END OF GLOBAL VARIABLES' DEFINITION
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# DEFINE FUNCTIONS HERE

def clear_console():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


def progress_callback(progress):
    import sys
    sys.stdout.flush()
    print(f"Progress: {progress:.2f}%", end='\r')


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

    if os.path.isabs(_output_dir_name):
        output_dir = _output_dir_name
    else:
        output_dir = os.path.join(base_dir, _output_dir_name)

    # Create the output directory within the base directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    return output_dir


def show_start_menu():
    clear_console()
    print(f'# ------------------------------------------------------------------------ #')
    print(f'# Stock information fetcher')
    print(f'# Author: Kazusa')
    print(f'# FOR PERSONAL USE ONLY')
    print(f'#')
    print(f'# Project created on: 2024/09/09')
    print(f"# Executing date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f'#')
    print(f'# --------------------------- COMMAND LIST ------------------------------- #')
    print(f'#')
    print(f'#   get_raw_data:         Start to fetch all stock information')
    print(f'#   show [stock_code]:    Displaying information about a specified stock ')
    print(f'#')
    print(f'# ------------------------------------------------------------------------ #')


def initial_program(stock_code_file: str, config_file: str, region_code: str) -> AsyncStockFetcher:
    """
    Initializes the stock fetching program by reading stock codes from a CSV file,
    processing the configuration JSON, and creating an AsyncStockFetcher instance.

    Args:
        stock_code_file (str): Path to the CSV file containing stock codes.
        config_file (str): Path to the JSON configuration file.
        region_code (str): The region code to filter relevant configuration data.

    Returns:
        AsyncStockFetcher: Initialized asynchronous stock fetcher ready to fetch data.
    """
    show_start_menu()
    try:
        # Read stock codes from the CSV file
        df = pd.read_csv(stock_code_file, header=None)
        stock_code_list = df[df.columns[0]].values.tolist()

        # Process the configuration JSON
        processor = JsonDataProcessor()
        interest_info_idxs, thresholds, urls = processor.split_json_to_dicts(config_file, region_code)

        return stock_code_list, interest_info_idxs, thresholds, urls
    except Exception as e:
        print(f"An unexpected error occurred - {e}")


def stocks_list_to_dict(stocks_list) -> dict:
    """
    Convert a 2D list of stock data into a dictionary.
    
    :param stocks_list: list of lists, where each row contains stock information, and the second element is the stock code.
    :return: dict, where the key is the stock code, and the value is the remaining stock information.
    """
    stocks_dict = {}
    for row in stocks_list:
        stock_code = row[1]  # The second element is the stock code
        stock_info = row[:1] + row[2:]  # All information except the stock code
        stocks_dict[stock_code] = stock_info
    return stocks_dict


async def async_fetch_raw_data(fetcher: AsyncStockFetcher, save_path: str) -> dict:
    """
    A coroutine to asynchronously fetch and process stock data, then save the results to a CSV file.

    This routine reads a list of stock codes from a CSV file, processes a JSON configuration file 
    to extract necessary parameters, fetches stock data asynchronously, filters the data based 
    on specified thresholds, and saves the filtered data to a CSV file.

    Args:
        fetcher (AsyncStockFetcher): The instance of a AsyncStockFetcher class, used to fetch raw data
        save_path (str): The file path to save the filtered stock data as a CSV file.
    """

    # Asynchronously fetch the stock data
    await fetcher.fetch_data()

    # Save the filtered data to a CSV file
    fetcher.save_data(save_path)

    db = stocks_list_to_dict(fetcher.all_raw_data)
    return db

def show_stock_info(db: dict, stock_code: str):
    print(f"{stock_code}: {db[stock_code]}")