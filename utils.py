#---------------------------------------------------------------------------------
# Author: Zhang
# Date: 2024/09/09
# FOR PERSONAL USE ONLY.
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# IMPORT REQUIRED PACKAGES HERE

import json
import asyncio
import aiohttp

import pandas as pd

# END OF PACKAGE IMPORT
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# DEFINE CLASS HERE
    
class Const:
    """
    Const is a class designed to simulate constant values in Python.

    This class allows for the definition of constants that cannot be modified
    once they are set. It also enforces that constant names must be in uppercase.
    Attempting to change the value of an existing constant or using a lowercase
    name will raise an exception.

    Attributes:
        None

    Methods:
        __setattr__(name, value): Assigns a value to a constant and raises an error 
                                  if the constant already exists or if the name is 
                                  not in uppercase.
    """
    class ConstError(TypeError):
        """Exception raised when attempting to modify a constant."""
        pass

    class ConstCaseError(ConstError):
        """Exception raised when a constant name is not all uppercase."""
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            # Raise an error if trying to change an existing constant
            raise self.ConstError(f"Cannot change constant '{name}'")
        if not name.isupper():
            # Raise an error if the constant name is not in uppercase
            raise self.ConstCaseError(f"Constant name '{name}' must be uppercase")

        # Set the constant
        self.__dict__[name] = value


class JsonDataProcessor:
    """
    A class to process JSON data by filtering valid entries and extracting specific dictionaries.

    Methods:
        filter_valid(nested_dict): Filters a dictionary to include only items where the 'valid' key is True.
        split_json_to_dicts(json_file_path, region_code): Loads a JSON file and extracts specific dictionaries
                                                         based on the region code, returning only valid items.
    """

    @staticmethod
    def filter_valid(nested_dict: dict) -> dict:
        """
        Filter a dictionary to only include items where the 'valid' key is True.

        Args:
            nested_dict (dict): A dictionary potentially containing a 'valid' key in its nested dictionaries.

        Returns:
            dict: A filtered dictionary containing only the valid items.
        """
        return {key: value for key, value in nested_dict.items() if value.get('valid')}

    def split_json_to_dicts(self, json_file_path: str, region_code: str):
        """
        Load a JSON file and extract specific dictionaries based on region code.

        Args:
            json_file_path (str): The file path to the JSON file.
            region_code (str): The region code used to select data from the JSON file.

        Returns:
            tuple: A tuple containing three dictionaries: interest_info_idxs, thresholds, and urls,
                   each filtered to include only valid items.
        """
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file).get(region_code, {})

        if not data:
            raise ValueError(f"No data found for region code: {region_code}")

        # Extract dictionaries and filter out invalid entries
        dicts_list = [val for val in data.values()]

        if len(dicts_list) < 3:
            raise ValueError("Expected at least three dictionaries in the JSON data.")

        interest_info_idxs = self.filter_valid(dicts_list[0])
        thresholds = self.filter_valid(dicts_list[1])
        urls = self.filter_valid(dicts_list[2])

        return interest_info_idxs, thresholds, urls
    

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
        thresholds (dict): A dictionary containing the filtering thresholds for the stock data.
        urls (dict): A dictionary containing URL prefixes, suffixes, and firewall warning texts.

    Methods:
        fetch_data(): Fetch data for all stocks in the list asynchronously.
        filter_data(): Filter the fetched stock data based on defined thresholds.
        save_data(save_path): Save the filtered data to a CSV file.
    """
    def __init__(self, stock_list, urls, progress_callback=None) -> None:
        self._stock_list = stock_list
        self._urls = urls
        self._all_raw_data = []

        # Callback function
        self.progress_callback = progress_callback
        self.total_stocks = len(stock_list)
    
    """ FOR DEVELOPMENT ONLY """
    # THIS PART OF CODE SHOULD NEVER BE VIWED BY USER
    # THE ONLY USAGE OF THIS FUNCTION IS TO CHECK THE RAW DATA STRUCTURE
    @property
    def _unit_test(self):
        
        _test_stock_code = self._stock_list[0]
        _test_url = f"{self._urls['request']['prefix']}{_test_stock_code}{self._urls['request']['suffix']}"

        import requests
        _test_response = requests.get(url=_test_url, headers=self._urls['request']['headers'], allow_redirects=True)
        _test_raw_data = json.loads(_test_response.content)
        print(_test_raw_data['data'][_test_stock_code]['qt'][_test_stock_code])

    @classmethod
    def run_unit_test(cls, test_code_list, test_urls):
        _test_tester = cls(
            stock_list=test_code_list,
            urls=test_urls,
        )
        _test_tester._unit_test
    """ END OF DEVELOPMENT CODE """

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
                                information = json.loads(text)
                                raw_data = information['data'][stock_code]['qt'][stock_code]
                                
                                # ***************************************************************************************************
                                # PRE-PROCESSING OF RAW DATA
                                # THIS PART OF CODE IS FRAGILE

                                # stock code w/o prefix is placed at the 3rd place of raw data list
                                # so the sub index of stock_code is 2 (sub index starts from 0)
                                raw_data[2] = stock_code
                                # all original value in raw data is string
                                # map all number-type data into float type
                                raw_data[3:] = [float(item) if item.replace('.', '', 1).isdigit() else item for item in raw_data[3:]]

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

    async def fetch_data(self):
        """Fetch data for all stocks in the list asynchronously and update progress."""
        fetched_count = 0  # number of stocks processed (get response)
        max_concurrent_requests = 5  # maximum concurrency of requests
        semaphore = asyncio.Semaphore(max_concurrent_requests)  # limiting the number of concurrent requests with semaphores

        async with aiohttp.ClientSession() as session:
            task_list = []
            for stock_code in self._stock_list:
                task = self._fetch_stock_data(session, stock_code, semaphore)
                task_list.append(task)
            
            # gather results and update progress after each task finishes
            for result in asyncio.as_completed(task_list):
                fetched_data = await result
                if fetched_data:
                    self._all_raw_data.append(fetched_data)
                
                # update the number of stocks which already received response
                fetched_count += 1

                if self.progress_callback:
                    progress = fetched_count / self.total_stocks * 100
                    self.progress_callback(progress)

    def save_data(self, save_path: str):
        """Save the filtered data to a CSV file."""
        try:
            df = pd.DataFrame(self._all_raw_data)
            df.to_csv(save_path, index=False, header=None, encoding='utf-8-sig')
        except Exception as e:
            print(f"Error saving data: {e}")


class StockFilter:
    """
    StockFilter reads raw stock data from CSV, filters columns based on interest_info_idxs, 
    and filters rows based on thresholds.
    """
    def __init__(self, interest_info_idxs, thresholds) -> None:
        self._interest_info_idxs = interest_info_idxs
        self._thresholds = thresholds
        self.results = pd.DataFrame()
    
    def load_data(self, raw_data_path: str):
        """Load the raw stock data from a CSV file into a pandas DataFrame."""
        try:
            df = pd.read_csv(raw_data_path)
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()

    def filter_interested_value(self, df: pd.DataFrame):
        """Filter the DataFrame to keep only the columns of interest."""
        columns_to_keep = [idx['index'] for idx in self._interest_info_idxs.values()]
        filtered_df = df[columns_to_keep]
        filtered_df.columns = self._interest_info_idxs.keys()
        return filtered_df

    def filter_stock(self, df: pd.DataFrame):
        """Filter rows in the DataFrame based on predefined thresholds."""
        self.results = df.copy()
        for key, threshold in self._thresholds.items():
            expression = f"{threshold['lower']} <= {key} < {threshold['upper']}"
            self.results.query(expression, inplace=True)

    def save_filtered_data(self, save_path: str):
        """Save the filtered data to a CSV file."""
        try:
            self.results.to_csv(save_path, index=False, encoding='utf-8-sig')
            print(f"Filtered data successfully saved to {save_path}")
        except Exception as e:
            print(f"Error saving filtered data: {e}")

    
# END OF CLASS DEFINITION
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# UNIT TEST, DEVELOPMENT USE ONLY
# RUN THE BLOW CODE TO PRINT RAW DATA STRUCTURE

if __name__ == '__main__':

    import os
    Const.CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
    
    processor = JsonDataProcessor()
    _, _, urls = processor.split_json_to_dicts(Const.CONFIG_FILE, 'CN')
    
    AsyncStockFetcher.run_unit_test(
        test_code_list=['sh603233'], 
        test_urls=urls
    )

# END OF UNIT TEST
#---------------------------------------------------------------------------------

# END OF FILE
#---------------------------------------------------------------------------------