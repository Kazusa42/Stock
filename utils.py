#---------------------------------------------------------------------------------
# Author: Zhang
# Date: 2024/09/09
# FOR PERSONAL USE ONLY.
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# IMPORT REQUIRED PACKAGES HERE

import requests
import json
import asyncio
import aiohttp

import pandas as pd
import numpy as np

from tqdm import tqdm

# END OF PACKAGE IMPORT
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# DEFINE CLASS HERE

class Interval:
    def __init__(self, lower, upper) -> None:
        self.__lower = lower
        self.__upper = upper

    def get_lower(self):
        return self.__lower
    
    def get_upper(self):
        return self.__upper
    

class Const(object):
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

# a sequential version of StockFetcher
# sequentially request information for each stock.
class StockFetcher:
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

            resp = requests.get(url)
            if resp.status_code == 403:
                print(f"Warning: Request for stock {stockCode} was blocked by a firewall.")
                return None
            elif 300 <= resp.status_code < 400:
                print(f'Warning: Request for stock {stockCode} was redirected.')
                return None
            elif resp.status_code == 200:
                if 'window.location.href="https://waf.tencent.com/501page.html' in resp.content.decode():
                    print(f"Warning: Request for stock {stockCode} was blocked by a firewall.")
                    return None

                text = json.loads(resp.content)
                rawData = text['data'][stockCode]['qt'][stockCode]

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


# an async version of StockFetcher. 
# by requesting the information for each stock at the same time, the exectuing time will be shorten.
class AsyncStockFetcher:
    def __init__(self, infoDict, threDict, stockList: list) -> None:
        self.__infoDict = infoDict
        self.__therDict = threDict
        self.__stockList = stockList
        self.__data = []

        self.df = pd.DataFrame()

    async def fetch_stock_data(self, session, stockCode):
        url = f'http://ifzq.gtimg.cn/appstock/app/kline/mkline?param={stockCode},m1,,10'
        async with session.get(url, allow_redirects=True) as response:
            if 300 <= response.status < 400:
                print(f'Warning: Request for stock {stockCode} was redirected.')
                return None

            elif response.status == 403:
                print(f"Warning: Request for stock {stockCode} was blocked by a firewall.")
                return None
                
            elif response.status == 200:
                info = await response.text()

                if 'window.location.href="https://waf.tencent.com/501page.html' in info:
                    print(f"Warning: Request for stock {stockCode} was blocked by a firewall.")
                    return None

                infoDict = json.loads(info)
                rawData = infoDict['data'][stockCode]['qt'][stockCode]

                selectedData = [rawData[i] for i in list(self.__infoDict.values())]
                selectedData[0] = stockCode
                selectedData[1:] = list(map(float, selectedData[1:]))

                return selectedData      
            return None

    async def seak_data(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for stockCode in self.__stockList:
                tasks.append(self.fetch_stock_data(session, stockCode))
            results = await asyncio.gather(*tasks)
            
            self.__data = [res for res in results if res is not None]

    def filter_data(self):
        self.df = pd.DataFrame(self.__data, columns=list(self.__infoDict.keys()))
        for k, v in self.__therDict.items():
            expr = str(v.get_lower()) + r' <= ' + str(k) + r' <= ' + str(v.get_upper())
            self.df.query(expr=expr, inplace=True)

    def save_data(self, savedir):
        self.df.to_csv(savedir, index=False)

# END OF CLASS DEFINITION
#---------------------------------------------------------------------------------

# END OF FILE
#---------------------------------------------------------------------------------
