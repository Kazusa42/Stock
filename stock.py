import requests
import json
import warnings

import pandas as pd
import numpy as np

from pathlib import Path
from datetime import date
from tqdm import tqdm

warnings.simplefilter(action=r'ignore', category=FutureWarning)


class interval:
    def __init__(self, lower, upper) -> None:
        self.__lower = lower
        self.__upper = upper

    def get_lower(self):
        return self.__lower
    
    def get_upper(self):
        return self.__upper
    

class const(object):
    class ConstError(TypeError): 
        pass
    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, name, value):
        if self.__dict__.has_key(name):
            raise self.ConstError("can't change const.%s" % name)
        if not name.isupper():
            raise self.ConstCaseError("const name '%s' is not all uppercase" % name)

        self.__dict__[name] = value


class AStockInfoSeaker:
    def __init__(self, infoDict, threDict, stockList: list) -> None:
        self.__infoDict = infoDict
        self.__stockList = stockList
        self.__therDict = threDict

        self.df = pd.DataFrame(np.zeros((len(self.__stockList), len(self.__infoDict))),
                               columns=list(self.__infoDict.keys()))
        
    def seak_data(self):
        for idx in tqdm(range(len(self.__stockList))):
            stockCode = self.__stockList[idx]
            # print(stockCode)
            url = f'http://ifzq.gtimg.cn/appstock/app/kline/mkline?param={stockCode},m1,,10'

            resp = json.loads(requests.get(url).content)
            rawData = resp['data'][stockCode]['qt'][stockCode]

            if len(rawData) == 0:
                raise ValueError('Invaild stock code: {stockCode}.')
            else:
                data = [rawData[i] for i in list(self.__infoDict.values())]
                data[0] = stockCode
                data[1:] = list(map(float, data[1:]))
                self.df.loc[idx] = data

    def data_filter(self):
        for k, v in self.__therDict.items():
            expr = str(v.get_lower()) + r' <= ' + str(k) + r' <= ' + str(v.get_upper())
            self.df.query(expr=expr, inplace=True)
            

    def save_data(self, savedir):
        self.df.to_csv(savedir, index=False)


if __name__ == r'__main__':
    #---------------------------------------------------------------------------------
    # CONST VARIABLES ARE DEFINED HERE
    # THESE VARIABLE SHOULD NOT BE MODIFIED WITHOUT AUTHOR'S PREMISSION

    # if run unit test
    # this variable should only be True when in development mode
    const.IF_RUN_UNITTEST = False

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

    # create a AStockInfoSeaker instance
    seaker = AStockInfoSeaker(infoDict=const.INFO_DICT,
                              threDict=const.THRE_DICT,
                              stockList=stockCodeList)
    
    seaker.seak_data()    # get all stock information
    seaker.data_filter()  # filter stocks according to thresholds

    # print(seaker.df)
    # save interset stock inforamtion to file
    seaker.save_data(savedir=const.RESULT_FILE)

    # END OF MAIN ROUTINE
    #---------------------------------------------------------------------------------

    # END OF FILE
    #---------------------------------------------------------------------------------