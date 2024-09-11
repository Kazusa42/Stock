#---------------------------------------------------------------------------------
# Author: Zhang
# Date: 2024/09/09
# FOR PERSONAL USE ONLY.
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# IMPORT REQUIRED PACKAGES HERE

import warnings
import asyncio
import threading
import json

import pandas as pd
import tkinter as tk

from tkinter import messagebox
from pathlib import Path
from datetime import datetime

from utils import AsyncStockFetcher, Const

# END OF PACKAGE IMPORT
#---------------------------------------------------------------------------------

warnings.simplefilter(action=r'ignore', category=FutureWarning)

#---------------------------------------------------------------------------------
# FUNCTIONS DEFINE

def filter_valid(nested_dict) -> dict:
    filtered_dict = {key: value for key, value in nested_dict.items() if value.get('valid')}
    return filtered_dict

def split_json_to_dicts(json_file_path, region_code):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)[region_code]
    dicts_list = [val for val in data.values()]

    # only remain valied values
    interest_info_idxs = filter_valid(dicts_list[0])
    thresholds = filter_valid(dicts_list[1])
    urls = filter_valid(dicts_list[2])

    return interest_info_idxs, thresholds, urls

async def async_routine(stock_code_path, config_path, region_code, save_path):
    df = pd.read_csv(stock_code_path, header=None)
    stock_code_list = df[df.columns[0]].values.tolist()

    interest_info_idxs, thresholds, urls = split_json_to_dicts(config_path, region_code)

    fetcher = AsyncStockFetcher(
        stock_list=stock_code_list,
        interest_info_idxs=interest_info_idxs,
        thresholds=thresholds,
        urls=urls
    )

    await fetcher.seak_data()
    fetcher.filter_data()

    fetcher.save_data(save_path)
    messagebox.showinfo("Info", "Stock data fetched successfully.")


def run_async_routine(stock_code_path, config_path, region_code, save_path):
    asyncio.run(async_routine(
        stock_code_path=stock_code_path,
        config_path=config_path,
        region_code=region_code,
        save_path=save_path
    ))
    start_button.config(state=tk.NORMAL)


def on_start_button_click():
    start_button.config(state=tk.DISABLED)
    threading.Thread(
        target=run_async_routine,
        args=(Const.STOCKCODE_FILE, Const.CONFIG_FILE, Const.REGION_CODE, Const.RESULT_FILE,)
    ).start()

# END OF FUNCTIONS DEFINE
#---------------------------------------------------------------------------------


if __name__ == r'__main__':
    #---------------------------------------------------------------------------------
    # CONST VARIABLES ARE DEFINED HERE
    # THESE VARIABLE SHOULD NOT BE MODIFIED WITHOUT AUTHOR'S PREMISSION

    Const.REGION_CODE = r'CN'

    # config file path
    Const.CONFIG_FILE = str(Path(__file__).resolve().parent) + r'/config.json'

    # the file which contains all stock code
    Const.STOCKCODE_FILE = str(Path(__file__).resolve().parent) + r'/stock_code.csv'

    # the file which contains all stock code that meets all requirements (threshold)
    Const.RESULT_FILE = str(Path(__file__).resolve().parent) + \
        f'/interest_stock/{str(datetime.now().strftime('%Y-%m-%d_%H_%M'))}_interest_stock.csv'

    # END OF CONST VARIABLES DEFIN
    #---------------------------------------------------------------------------------

    #---------------------------------------------------------------------------------
    # MAIN ROUTINE

    """asyncio.run(async_routine(
        stock_code_path=Const.STOCKCODE_FILE,
        config_path=Const.CONFIG_FILE,
        region_code=Const.REGION_CODE,
        save_path=Const.RESULT_FILE
    ))"""
    root = tk.Tk()
    root.title('Async stock fetcher')
    root.geometry("300x150")

    title_label = tk.Label(root, text='Stock data fetcher', font=("Arial", 16))
    title_label.pack(pady=20)

    start_button = tk.Button(root, text='Start', font=("Arial", 16), command=on_start_button_click)
    start_button.pack(pady=10)

    root.mainloop()

    # END OF MAIN ROUTINE
    #---------------------------------------------------------------------------------

    # END OF FILE
    #---------------------------------------------------------------------------------