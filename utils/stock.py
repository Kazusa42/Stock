#---------------------------------------------------------------------------------
# Author: Zhang
# FOR PERSONAL USE ONLY.
# 
# Create Date: 2024/09/09
# Last Updata on: 2024/10/02
#
# FILE: stock.py
# Description: core codes
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------


import asyncio
import aiohttp
import unicodedata
import json
import os

from datetime import datetime

import pandas as pd


class AsyncStockFetcher:
    """
    AsyncStockFetcher is a class designed to asynchronously fetch, filter, and save stock data.

    This class takes a list of stock codes, retrieves the relevant data from specified URLs,
    filters the data based on predefined thresholds, and allows for saving the filtered data
    to a CSV file.

    Attributes:
        stock_list (list): A list of stock codes to fetch data for.
        interest_info_idxs (dict): A dictionary mapping column names to their respective indexes 
                                   in the retrieved data.
        urls (dict): A dictionary containing URL prefixes, suffixes, and firewall warning texts.

    Methods:
        fetch_data(): Fetch data for all stocks in the list asynchronously.
        save_data(save_path): Save the filtered data to a CSV file.
    """
    def __init__(self, stock_list, urls, interest_info_idxs, progress_callback=None) -> None:
        self._urls = urls

        self._all_raw_data = []
        self.stock_list = stock_list
        self.interest_info_idxs = interest_info_idxs
        self.df = pd.DataFrame()

        # Callback function
        self.progress_callback = progress_callback
        self.total_stocks = len(stock_list)

    # CORE FUNCTION
    async def _fetch_stock_data(self, session, stock_code: str, semaphore: asyncio.Semaphore, retry_limit=3):
        """ Fetch stock data for a given stock code asynchronously. """
        url = f"{self._urls['request']['prefix']}{stock_code}{self._urls['request']['suffix']}"
        # using semaphores to control concurrency
        async with semaphore:
            retries = 0
            while retries < retry_limit:
                try:
                    async with session.get(url, headers=self._urls['request']['headers'], allow_redirects=True) as response:
                        if 300 <= response.status < 400:
                            print(f'Warning: Request for stock {stock_code} was redirected.')
                            return None
                        elif response.status == 403:
                            print(f"Warning: Request for stock {stock_code} was blocked by a firewall.")
                            return None
                        elif response.status == 200:
                            text = await response.text()
                            if self._urls['firewallWarning']['text'] in text:
                                print(f"Warning: Request for stock {stock_code} was blocked by a firewall.")
                                return None
                            
                            try:
                                information = json.loads(text)['data'][stock_code]['qt'][stock_code]
                                # only remain data with interest
                                raw_data = [information[idx['index']] for idx in self.interest_info_idxs.values()]
                                
                                # ***************************************************************************************************
                                # PRE-PROCESSING OF RAW DATA
                                # THIS PART OF CODE IS FRAGILE

                                # stock code w/o prefix is placed at the 2nd place of raw data list
                                # so the sub index of stock_code is 2 (sub index starts from 0)
                                raw_data[1] = stock_code
                                # all original value in raw data is string
                                # map all number-type data into float type
                                raw_data[2:] = [float(item) if item.replace('.', '', 1).isdigit() else item for item in raw_data[2:]]

                                # END OF PRE-PROCESSING OF RAW DATA
                                # ***************************************************************************************************

                                return raw_data
                            except (KeyError, ValueError, json.JSONDecodeError) as e:
                                print(f"Error processing data for stock {stock_code}: {e}")
                                return None
                        else:
                            print(f"Error: Request for stock {stock_code} failed with status {response.status}.")
                            return None
                except aiohttp.ClientError as e:
                    print(f"Client error: {e}")
                    retries += 1
                    await asyncio.sleep(2 ** retries)  # Exponential backoff
                    continue  # retry
            return None

    async def fetch_data(self) -> int:
        """Fetch data for all stocks in the list asynchronously and update progress."""
        fetched_count = 0  # number of stocks processed (get response)
        max_concurrent_requests = 5  # maximum concurrency of requests
        semaphore = asyncio.Semaphore(max_concurrent_requests)  # limiting the number of concurrent requests with semaphores

        async with aiohttp.ClientSession() as session:
            task_list = []
            for stock_code in self.stock_list:
                task = self._fetch_stock_data(session, stock_code, semaphore)
                task_list.append(task)
            
            # gather results and update progress after each task finishes
            for result in asyncio.as_completed(task_list):
                fetched_data = await result

                if fetched_data:
                    self._all_raw_data.append(fetched_data)
                else:
                    return 1
                
                # update the number of stocks which already received response
                fetched_count += 1

                if self.progress_callback:
                    progress = fetched_count / self.total_stocks * 100
                    self.progress_callback(progress)
        return 0

    def save_data(self, save_dir: str):
        """
        Save the filtered data to a CSV file.

        Args:
            save_dir (str): The directory path to save data.
        """

        # check if the directory exits, if not exits then create one
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        save_path = os.path.join(save_dir, f"{datetime.now().strftime('%Y_%m_%d_%H_%M')}_raw.csv")
        try:
            self.df = pd.DataFrame(self._all_raw_data, columns=self.interest_info_idxs.keys())
            self.df.to_csv(save_path, index=False, encoding='utf-8-sig')
        except Exception as e:
            print(f"Error saving data: {e}")


class StockDatabase:
    def __init__(self, raw_data: pd.DataFrame, keyword=r'stockCode'):
        """
        Initialize the StockDatabase with raw stock data.

        Parameters:
        raw_data (pd.DataFrame): A DataFrame where each row represents stock information.
                                 The DataFrame should have at least the following columns:
                                 ['Stock Code', 'Stock Name', 'Price', 'Volume', ...]
        """
        self.raw_data = raw_data
        self._keyword = keyword

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
        filtered_data = self.raw_data[self.raw_data[self._keyword].isin(stock_codes)]
        
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

    def update(self, new_data: pd.DataFrame):
        """
        Update the raw_data with new stock data.

        Parameters:
        new_data (pd.DataFrame): A new DataFrame to replace the existing raw_data.
                                 The DataFrame should have the same structure as the original raw_data,
                                 including a 'Stock Code' column.
        """
        print(f"Stock information is updated on {datetime.now().strftime('%Y-%m-%d %H:%M')}.")
        self.raw_data = new_data

    def filter_stocks(self, thresholds: dict) -> list:
        """
        Filter stocks based on the provided threshold conditions using DataFrame.query()
        and return the list of stock codes that meet the filtering criteria.

        Parameters:
        thresholds (dict): A dictionary where the key is the stock metric (column name) to filter by,
                        and the value is another dictionary with 'lower', 'upper', and 'valid' keys.

        Returns:
        list: A list of stock codes that meet the filtering criteria.
        """
        # Initialize an empty list to hold query conditions
        query_conditions = []

        # Build query conditions with 'and'
        for metric, condition in thresholds.items():
            lower = condition.get('lower', float('-inf'))
            upper = condition.get('upper', float('inf'))
            # create the query condition for current metric
            query_conditions.append(f"{lower} <= {metric} <= {upper}")

        # combine al query conditions with 'and'
        query_str = ' and '.join(query_conditions)

        # if there are no valid conditions, return all stock codes
        # this will work when threshold is empty
        if not query_str:
            return self.raw_data[self._keyword].tolist()
        
        # use DataFrame.query() to filter the data
        filtered_data = self.raw_data.query(query_str)
        return filtered_data[self._keyword].tolist()

    
# END OF CLASS DEFINITION
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# UNIT TEST, DEVELOPMENT USE ONLY
# RUN THE BLOW CODE TO PRINT RAW DATA STRUCTURE

if __name__ == '__main__':

    import requests
    import json

    stock_code = "sz000011"
    url = f"http://ifzq.gtimg.cn/appstock/app/kline/mkline?param={stock_code},m1,,10"
    
    response = requests.get(url, allow_redirects=True)
    information = json.loads(response.content)
    raw_data = information['data'][stock_code]['qt'][stock_code]
    print(raw_data)

# END OF UNIT TEST
#---------------------------------------------------------------------------------

# END OF FILE
#---------------------------------------------------------------------------------