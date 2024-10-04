# -*- coding:utf-8 -*-
# !/usr/bin/env python
#---------------------------------------------------------------------------------
# Author: Zhang
# FOR PERSONAL USE ONLY.
#
# Create Date: 2024/10/02
# Last Update on: 2024/10/03
#
# FILE: main.py
# Description: main loop entry of the project
#---------------------------------------------------------------------------------

import os
import asyncio
import time
import pandas as pd

from datetime import datetime

import utils.functions as funcs
import utils.component as comps
import utils.stock as stock


async def main():
    comps.Const.CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
    comps.Const.STOCKCODE_FILE = os.path.join(os.path.dirname(__file__), 'stock_code.csv')


    comps.Const.RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), 'raw_data')
    comps.Const.REGION_CODE = 'CN'


    stock_code_list, interest_info_idxs, thresholds, urls = funcs.initial_program(
        stock_code_file=comps.Const.STOCKCODE_FILE,
        config_file=comps.Const.CONFIG_FILE,
        region_code=comps.Const.REGION_CODE
    )

    fetcher = stock.AsyncStockFetcher(
        stock_list=stock_code_list,
        urls=urls,
        interest_info_idxs=interest_info_idxs,
        progress_callback=funcs.progress_callback
    )

    raw_data = None

    if not os.path.exists(comps.Const.RAW_DATA_DIR):
        os.makedirs(comps.Const.RAW_DATA_DIR)

    if len(os.listdir(comps.Const.RAW_DATA_DIR)) == 0:
        print("No previous data detected. Start fetching new data by default...")
        time.sleep(0.5)
        await funcs.async_fetch_raw_data(fetcher, comps.Const.RAW_DATA_DIR)
        raw_data = fetcher.df
    else:
        latest_file_name = os.listdir(comps.Const.RAW_DATA_DIR)[-1]
        user_input = input(f"Previous data detected. Load data from latest file {latest_file_name}? (y/n): ").lower().strip()
        if user_input == 'y':
            print(f'Data loaded from {latest_file_name}.')
            latest_file_path = os.path.join(comps.Const.RAW_DATA_DIR, latest_file_name)
            raw_data = pd.read_csv(latest_file_path)
            pass
        elif user_input == 'n':
            print('Start to fetch new data...')
            await funcs.async_fetch_raw_data(fetcher, comps.Const.RAW_DATA_DIR)
            raw_data = fetcher.df
        else:
            print("Invalid input, fetching new data by default...")
            await funcs.async_fetch_raw_data(fetcher, comps.Const.RAW_DATA_DIR)
            raw_data = fetcher.df

    db = stock.StockDatabase(raw_data=raw_data)

    while True:
        user_input = input("Waiting for command: ").lower().strip()
        if user_input == 'exit':
            print("Exiting...")
            break
        elif user_input.startswith('show'):
            search_code_list = user_input.split(' ')[1:]
            db.show_stock_info(search_code_list)
        elif user_input.startswith('update'):
            await funcs.async_fetch_raw_data(fetcher, comps.Const.RAW_DATA_DIR)
            db.update(new_data=fetcher.df)
        else:
            pass


if __name__ == '__main__':
    asyncio.run(main())