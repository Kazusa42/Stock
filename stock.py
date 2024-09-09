#---------------------------------------------------------------------------------
# Author: Zhang
# Date: 2024/09/09
# FOR PERSONAL USE ONLY.
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# IMPORT REQUIRED PACKAGES HERE

import warnings
import json
import requests
import asyncio

import pandas as pd

from pathlib import Path
from datetime import datetime

from utils import StockFetcher, AsyncStockFetcher, Interval, Const

# END OF PACKAGE IMPORT
#---------------------------------------------------------------------------------

warnings.simplefilter(action=r'ignore', category=FutureWarning)

#---------------------------------------------------------------------------------
# FUNCTIONS DEFINE

def seq_routine(infoDict, threDict, stockCodeList, savedir):
    fetcher = StockFetcher(infoDict=infoDict,
                          threDict=threDict,
                          stockList=stockCodeList)
    
    fetcher.seak_data()    # get all stock information
    fetcher.data_filter()  # filter stocks according to thresholds

    # print(seaker.df)
    # save interset stock inforamtion to file
    fetcher.save_data(savedir=savedir)


async def async_routine(infoDict, threDict, stockCodeList, savedir):
    fetcher = AsyncStockFetcher(infoDict=infoDict,
                                threDict=threDict,
                                stockList=stockCodeList)
    
    await fetcher.seak_data()  # get all stock information
    fetcher.filter_data()      # filter stocks according to thresholds

    fetcher.save_data(savedir=savedir)

# END OF FUNCTIONS DEFINE
#---------------------------------------------------------------------------------


if __name__ == r'__main__':
    #---------------------------------------------------------------------------------
    # CONST VARIABLES ARE DEFINED HERE
    # THESE VARIABLE SHOULD NOT BE MODIFIED WITHOUT AUTHOR'S PREMISSION

    # if run unit test
    # this variable should only be True when in development mode
    Const.IF_RUN_UNITTEST = False

    # if use async to speed up information retrieval
    # by enabling async, it will reduce the script execution time
    # but it is possible that useful information cannot be captured
    Const.ENABLE_ASYNC = True

    # the index of where the corresponding information is stored
    Const.INFO_DICT = {
        r'stockCode': 2,
        r'currPrice': 3,
        r'prevClosedPrice': 4,
        r'openPrice': 5,
        r'increase': 32,
        r'highest': 33,
        r'lowest': 34,
        r'turnOverRate': 38,
        r'ampRate': 43,
        r'tmCap': 44,
    }

    # thresholds used to filter data
    Const.THRE_DICT = {
        # r'ampRate': Interval(3, 6),        # ampRate: +3%~+6%
        r'turnOverRate': Interval(5, 10),  # turnOverRate: +5%~+10%
        r'tmCap': Interval(50, 120),       # tradableMarketCap: 50~120
        r'increase': Interval(3, 5)        # increase: +3%~+5%
    }

    # the file which contains all stock code
    Const.STOCKCODE_FILE = str(Path(__file__).resolve().parent) + r'/stock_code.csv'

    # the file which contains all stock code that meets all requirements (threshold)
    Const.RESULT_FILE = str(Path(__file__).resolve().parent) + \
        f'/interest_stock/{str(datetime.now().strftime('%Y-%m-%d_%H_%M'))}_interest_stock.csv'

    # END OF CONST VARIABLES DEFIN
    #---------------------------------------------------------------------------------

    #---------------------------------------------------------------------------------
    # UNIT TEST, FOR DEVELOPMENT ONLY
    if Const.IF_RUN_UNITTEST:
        stockCode = r'sh500013'  # test stock code
        url = f'http://ifzq.gtimg.cn/appstock/app/kline/mkline?param={stockCode},m1,,10'
        resp = json.loads(requests.get(url).content)

        print(resp['data'][stockCode]['qt'][stockCode])
        for k, v in Const.INFO_DICT.items():
            print(k, end=': ')
            print(resp['data'][stockCode]['qt'][stockCode][v])

    # END OF UNIT TEST
    #---------------------------------------------------------------------------------

    #---------------------------------------------------------------------------------
    # MAIN ROUTINE

    # read stock_code.csv file to get all stock codes and store them into a list
    df = pd.read_csv(Const.STOCKCODE_FILE, header=None)
    stockCodeList = df[df.columns[0]].values.tolist()
    # print(len(stockCodeList))

    if Const.ENABLE_ASYNC:
        asyncio.run(async_routine(infoDict=Const.INFO_DICT,
                                  threDict=Const.THRE_DICT,
                                  stockCodeList=stockCodeList,
                                  savedir=Const.RESULT_FILE))
    
    else:
        seq_routine(infoDict=Const.INFO_DICT,
                    threDict=Const.THRE_DICT,
                    stockCodeList=stockCodeList,
                    savedir=Const.RESULT_FILE)
    

    # END OF MAIN ROUTINE
    #---------------------------------------------------------------------------------

    # END OF FILE
    #---------------------------------------------------------------------------------