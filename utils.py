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


import json

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
    def __init__(self, stock_list, interest_info_idxs, thresholds, urls) -> None:
        self._stock_list = stock_list
        self._interest_info_idxs = interest_info_idxs
        self._thresholds = thresholds
        self._urls = urls
        self._all_data = []

        # Initialize an empty DataFrame to store the results
        self.results = pd.DataFrame()

    async def _fetch_stock_data(self, session, stock_code: str):
        """Fetch stock data for a given stock code asynchronously."""
        url = f"{self._urls['search']['prefix']}{stock_code}{self._urls['search']['suffix']}"
        async with session.get(url, allow_redirects=True) as response:
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

                    selected_data = [raw_data[idx['index']] for idx in self._interest_info_idxs.values()]
                    selected_data[0] = stock_code
                    selected_data[1:] = list(map(float, selected_data[1:]))
                    return selected_data
                except (KeyError, ValueError, json.JSONDecodeError) as e:
                    print(f"Error processing data for stock {stock_code}: {e}")
                    return None
            else:
                print(f"Error: Request for stock {stock_code} failed with status {response.status}.")
                return None

    async def fetch_data(self):
        """Fetch data for all stocks in the list asynchronously."""
        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_stock_data(session, stock_code) for stock_code in self._stock_list]
            results = await asyncio.gather(*tasks)
            self._all_data = [res for res in results if res is not None]

    def filter_data(self):
        """Filter the fetched stock data based on defined thresholds."""
        self.results = pd.DataFrame(self._all_data, columns=list(self._interest_info_idxs.keys()))
        for key, threshold in self._thresholds.items():
            expression = f"{threshold['lower']} <= {key} < {threshold['upper']}"
            self.results.query(expression, inplace=True)

    def save_data(self, save_path: str):
        """Save the filtered data to a CSV file."""
        self.results.to_csv(save_path, index=False)

# END OF CLASS DEFINITION
#---------------------------------------------------------------------------------

# END OF FILE
#---------------------------------------------------------------------------------