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

    db = None

    if not os.path.exists(comps.Const.RAW_DATA_DIR):
        os.makedirs(comps.Const.RAW_DATA_DIR)

    if len(os.listdir(comps.Const.RAW_DATA_DIR)) == 0:
        print("No previous data detected. Start fetching new data by default...")
        time.sleep(0.5)
        db = await funcs.async_fetch_raw_data(fetcher, comps.Const.RAW_DATA_DIR)
    else:
        latest_file = os.listdir(comps.Const.DATABASE_PATH)[-1]
        user_input = input(f"Previous data detected. Load data from latest file {latest_file}? (y/n): ").lower().strip()
        if user_input == 'y':
            print(f'Loading data from {latest_file}...')
            pass
        elif user_input == 'n':
            print('Start to fetch new data...')
            db = await funcs.async_fetch_raw_data(fetcher, comps.Const.RAW_DATA_DIR)
        else:
            print("Invalid input, fetching new data by default...")
            db = await funcs.async_fetch_raw_data(fetcher, comps.Const.RAW_DATA_DIR)

    while True:
        user_input = input(">command: ").lower().strip()
        if user_input == 'exit':
            print("Exiting...")
            break
        elif user_input.startswith('show'):
            search_code_list = user_input.split(' ')[1:]
            pass
        elif user_input.startswith('get_raw_data'):
            db = await funcs.async_fetch_raw_data(fetcher, comps.Const.RAW_DATA_DIR)
        else:
            pass


if __name__ == '__main__':
    asyncio.run(main())