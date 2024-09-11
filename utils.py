#---------------------------------------------------------------------------------
# Author: Zhang
# Date: 2024/09/09
# FOR PERSONAL USE ONLY.
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# IMPORT REQUIRED PACKAGES HERE

import json
import asyncio
import aiohttp

import pandas as pd

# END OF PACKAGE IMPORT
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# DEFINE CLASS HERE
    
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


# an async version of StockFetcher. 
# by requesting the information for each stock at the same time, the exectuing time will be shorten.
class AsyncStockFetcher:
    def __init__(self, stock_list, interest_info_idxs, thresholds, urls) -> None:
        self.__stock_list = stock_list
        self.__interest_info_idxs = interest_info_idxs
        self.__thresholds = thresholds
        self.__urls = urls
        self.__all_data = []

        self.results = pd.DataFrame()

    async def __fetch_stock_data(self, session, stock_code):
        url = self.__urls['search']['prefix'] + str(stock_code) + self.__urls['search']['suffix']
        async with session.get(url, allow_redirects=True) as response:
            if 300 <= response.status < 400:
                print(f'Warning: Request for stock {stock_code} was redirected.')
                return None
            elif response.status == 403:
                print(f"Warning: Request for stock {stock_code} was blocked by a firewall.")
                return None
            elif response.status == 200:
                text = await response.text()
                if self.__urls['firewallWarning']['text'] in text:
                    print(f"Warning: Request for stock {stock_code} was blocked by a firewall.")
                    return None
                information = json.loads(text)
                raw_data = information['data'][stock_code]['qt'][stock_code]

                selected_data = [raw_data[val['index']] for val in list(self.__interest_info_idxs.values())]
                selected_data[0] = stock_code
                selected_data[1:] = list(map(float, selected_data[1:]))
                return selected_data
            return None

    async def seak_data(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for stockCode in self.__stock_list:
                tasks.append(self.__fetch_stock_data(session, stockCode))
            results = await asyncio.gather(*tasks)
            self.__all_data = [res for res in results if res is not None]

    def filter_data(self):
        self.results = pd.DataFrame(self.__all_data, columns=list(self.__interest_info_idxs.keys()))
        for k, v in self.__thresholds.items():
            expression = str(v['lower']) + r'<=' + str(k) + r'<' + str(v['upper'])
            self.results.query(expression, inplace=True)

    def save_data(self, save_path):
        self.results.to_csv(save_path, index=False)

# END OF CLASS DEFINITION
#---------------------------------------------------------------------------------

# END OF FILE
#---------------------------------------------------------------------------------
