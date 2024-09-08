import warnings
import json
import requests
import asyncio

import pandas as pd

from pathlib import Path
from datetime import date

from utils import StockFetcher, AsyncStockFetcher, interval, const

warnings.simplefilter(action=r'ignore', category=FutureWarning)


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


if __name__ == r'__main__':
    #---------------------------------------------------------------------------------
    # CONST VARIABLES ARE DEFINED HERE
    # THESE VARIABLE SHOULD NOT BE MODIFIED WITHOUT AUTHOR'S PREMISSION

    # if run unit test
    # this variable should only be True when in development mode
    const.IF_RUN_UNITTEST = False

    # if use async to speed up information retrieval
    # by enabling async, it will reduce the script execution time
    # but it is possible that useful information cannot be captured
    const.ENABLE_ASYNC = True

    # the index of where the corresponding information is stored
    const.INFO_DICT = {
        r'stockCode': 2,
        r'closePrice': 3,
        r'prevClosePrice': 4,
        r'openPrice': 5,
        r'highest': 33,
        r'lowest': 34,
        r'turnOverRate': 38,
        r'ampRate': 43,
        r'tmCap': 44,
    }

    # thresholds used to filter data
    const.THRE_DICT = {
        r'ampRate': interval(3, 6),        # ampRate: +3~+6%
        r'turnOverRate': interval(5, 10),  # turnOverRate: +5%~+10%
        r'tmCap': interval(50, 120),       # tradableMarketCap: 50~120
    }

    # the file which contains all stock code
    const.STOCKCODE_FILE = str(Path(__file__).resolve().parent) + r'/stock_code.csv'

    # the file which contains all stock code that meets all requirements (threshold)
    const.RESULT_FILE = str(Path(__file__).resolve().parent) + f'/{str(date.today())}_interest_stock.csv'

    # END OF CONST VARIABLES DEFIN
    #---------------------------------------------------------------------------------

    #---------------------------------------------------------------------------------
    # UNIT TEST, FOR DEVELOPMENT ONLY
    if const.IF_RUN_UNITTEST:
        stockCode = r'sh500013'  # test stock code
        url = f'http://ifzq.gtimg.cn/appstock/app/kline/mkline?param={stockCode},m1,,10'
        resp = json.loads(requests.get(url).content)

        print(resp['data'][stockCode]['qt'][stockCode])
        for k, v in const.INFO_DICT.items():
            print(k, end=': ')
            print(resp['data'][stockCode]['qt'][stockCode][v])

    # END OF UNIT TEST
    #---------------------------------------------------------------------------------

    #---------------------------------------------------------------------------------
    # MAIN ROUTINE

    # read stock_code.csv file to get all stock codes and store them into a list
    df = pd.read_csv(const.STOCKCODE_FILE, header=None)
    stockCodeList = df[df.columns[0]].values.tolist()
    # print(len(stockCodeList))

    if const.ENABLE_ASYNC:
        asyncio.run(async_routine(infoDict=const.INFO_DICT,
                                  threDict=const.THRE_DICT,
                                  stockCodeList=stockCodeList,
                                  savedir=const.RESULT_FILE))
    
    else:
        seq_routine(infoDict=const.INFO_DICT,
                    threDict=const.THRE_DICT,
                    stockCodeList=stockCodeList,
                    savedir=const.RESULT_FILE)
    

    # END OF MAIN ROUTINE
    #---------------------------------------------------------------------------------

    # END OF FILE
    #---------------------------------------------------------------------------------