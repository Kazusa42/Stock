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

from datetime import datetime

import utils.functions as funcs
import utils.component as comps
import utils.stock as stock


async def main():
    comps.Const.CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
    comps.Const.STOCKCODE_FILE = os.path.join(os.path.dirname(__file__), 'stock_code.csv')


    comps.Const.DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database')
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

    if len(os.listdir(comps.Const.DATABASE_PATH)) == 0:
        print("Database is now empty. Start to fetch new data...")
        save_path = os.path.join(comps.Const.DATABASE_PATH, f"{datetime.now().strftime('%Y_%m_%d_%H_%M')}_raw_stock_info.csv")
        db = await funcs.async_fetch_raw_data(fetcher, save_path)
    else:
        latest = os.listdir(comps.Const.DATABASE_PATH)[-1]
        user_input = input(f"Load data from latest file {latest}? (y/n): ").lower().strip()
        if user_input == 'y':
            print(f'Loading data from {latest}...')
            pass
        elif user_input == 'n':
            print('Start to fetch new data...')
            save_path = os.path.join(comps.Const.DATABASE_PATH, f"{datetime.now().strftime('%Y_%m_%d_%H_%M')}_raw_stock_info.csv")
            db = await funcs.async_fetch_raw_data(fetcher, save_path)
        else:
            print("Invalid input, fetching new data by default...")
            db = await funcs.async_fetch_raw_data(fetcher, save_path)
    print('\n')
    while True:
        user_input = input(">command: ").lower().strip()
        if user_input == 'exit':
            print("Exiting...")
            break
        elif user_input.startswith('show'):
            funcs.show_stock_info(db, user_input[-6:])
        elif user_input.startswith('get_raw_data'):
            save_path = os.path.join(comps.Const.DATABASE_PATH, f"{datetime.now().strftime('%Y_%m_%d_%H_%M')}_raw_stock_info.csv")
            db = await funcs.async_fetch_raw_data(fetcher, save_path)
        else:
            pass


if __name__ == '__main__':
    asyncio.run(main())