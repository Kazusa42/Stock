# -*- coding:utf-8 -*-
# !/usr/bin/env python
#---------------------------------------------------------------------------------
# Author: Zhang
# FOR PERSONAL USE ONLY.
#
# Create Date: 2024/09/09
# Last Update on: 2024/10/03
#
# FILE: component.py
# Description: Basic classes are defined here
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# IMPORT REQUIRED PACKAGES HERE

import json

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
    

