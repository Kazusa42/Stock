#---------------------------------------------------------------------------------
# Author: Zhang
# Date: 2024/09/09
# FOR PERSONAL USE ONLY.
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# IMPORT REQUIRED PACKAGES HERE

import warnings
import asyncio

import pandas as pd

from pathlib import Path
from datetime import datetime

from utils import AsyncStockFetcher, Const, JsonDictProcessor

# END OF PACKAGE IMPORT
#---------------------------------------------------------------------------------

warnings.simplefilter(action=r'ignore', category=FutureWarning)

#---------------------------------------------------------------------------------
# FUNCTIONS DEFINE

async def async_routine(stock_code_path, config_path, region_code, save_path):
    df = pd.read_csv(stock_code_path, header=None)
    stock_code_list = df[df.columns[0]].values.tolist()

    proc = JsonDictProcessor(config_path)
    proc.split_json_to_dicts(region_code)
    valid_dicts = proc.filter_valid_entries()

    interest_info_idxs = valid_dicts[0]
    thresholds = valid_dicts[1]
    urls = valid_dicts[2]

    fetcher = AsyncStockFetcher(
        stock_list=stock_code_list,
        interest_info_idxs=interest_info_idxs,
        thresholds=thresholds,
        urls=urls
    )

    await fetcher.seak_data()
    fetcher.filter_data()

    fetcher.save_data(save_path)

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