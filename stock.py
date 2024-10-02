import asyncio
import aiohttp

import pandas as pd


class AsyncStockFetcher:
    """
    AsyncStockFetcher is a class designed to asynchronously fetch, filter, and save stock data.

    This class takes a list of stock codes, retrieves the relevant data from specified URLs,
    filters the data based on predefined thresholds, and allows for saving the filtered data
    to a CSV file.

    Attributes:
        stock_list (list): A list of stock codes to fetch data for.
        interest_info_idxs (dict): A dictionary mapping column names to their respective indexes 
                                   in the retrieved data.
        thresholds (dict): A dictionary containing the filtering thresholds for the stock data.
        urls (dict): A dictionary containing URL prefixes, suffixes, and firewall warning texts.

    Methods:
        fetch_data(): Fetch data for all stocks in the list asynchronously.
        filter_data(): Filter the fetched stock data based on defined thresholds.
        save_data(save_path): Save the filtered data to a CSV file.
    """
    def __init__(self, stock_list, urls, interest_info_idxs, progress_callback=None) -> None:
        self._stock_list = stock_list
        self._interest_info_idxs = interest_info_idxs
        self._urls = urls
        self._all_raw_data = []

        # Callback function
        self.progress_callback = progress_callback
        self.total_stocks = len(stock_list)

    # CORE FUNCTION
    async def _fetch_stock_data(self, session, stock_code: str, semaphore: asyncio.Semaphore, retry_limit=3):
        """ Fetch stock data for a given stock code asynchronously. """
        url = f"{self._urls['request']['prefix']}{stock_code}{self._urls['request']['suffix']}"
        # using semaphores to control concurrency
        async with semaphore:
            retries = 0
            while retries < retry_limit:
                try:
                    async with session.get(url, headers=self._urls['request']['headers'], allow_redirects=True) as response:
                        if 300 <= response.status < 400:
                            print(f'Warning: Request for stock {stock_code} was redirected.')
                            return None
                        elif response.status == 403:
                            print(f"Warning: Request for stock {stock_code} was blocked by a firewall.")
                            return None
                        elif response.status == 200:
                            text = await response.text()
                            if self._urls['firewallWarning']['text'] in text:
                                print(f"Warning: Request for stock {stock_code} was blocked by a firewall.")
                                return None
                            
                            try:
                                information = json.loads(text)['data'][stock_code]['qt'][stock_code]
                                # only remain data with interest
                                raw_data = [information[idx['index']] for idx in self._interest_info_idxs.values()]
                                
                                # ***************************************************************************************************
                                # PRE-PROCESSING OF RAW DATA
                                # THIS PART OF CODE IS FRAGILE

                                # stock code w/o prefix is placed at the 2nd place of raw data list
                                # so the sub index of stock_code is 2 (sub index starts from 0)
                                raw_data[1] = stock_code
                                # all original value in raw data is string
                                # map all number-type data into float type
                                raw_data[2:] = [float(item) if item.replace('.', '', 1).isdigit() else item for item in raw_data[2:]]

                                # END OF PRE-PROCESSING OF RAW DATA
                                # ***************************************************************************************************

                                return raw_data
                            except (KeyError, ValueError, json.JSONDecodeError) as e:
                                print(f"Error processing data for stock {stock_code}: {e}")
                                return None
                        else:
                            print(f"Error: Request for stock {stock_code} failed with status {response.status}.")
                            return None
                except aiohttp.ClientError as e:
                    print(f"Client error: {e}")
                    retries += 1
                    await asyncio.sleep(2 ** retries)  # Exponential backoff
                    continue  # retry
            return None

    async def fetch_data(self):
        """Fetch data for all stocks in the list asynchronously and update progress."""
        fetched_count = 0  # number of stocks processed (get response)
        max_concurrent_requests = 5  # maximum concurrency of requests
        semaphore = asyncio.Semaphore(max_concurrent_requests)  # limiting the number of concurrent requests with semaphores

        async with aiohttp.ClientSession() as session:
            task_list = []
            for stock_code in self._stock_list:
                task = self._fetch_stock_data(session, stock_code, semaphore)
                task_list.append(task)
            
            # gather results and update progress after each task finishes
            for result in asyncio.as_completed(task_list):
                fetched_data = await result
                if fetched_data:
                    self._all_raw_data.append(fetched_data)
                
                # update the number of stocks which already received response
                fetched_count += 1

                if self.progress_callback:
                    progress = fetched_count / self.total_stocks * 100
                    self.progress_callback(progress)

    def save_data(self, save_path: str):
        """Save the filtered data to a CSV file."""
        try:
            df = pd.DataFrame(self._all_raw_data, columns=self._interest_info_idxs.keys())
            df.to_csv(save_path, index=False, header=None, encoding='utf-8-sig')
        except Exception as e:
            print(f"Error saving data: {e}")

    
# END OF CLASS DEFINITION
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# UNIT TEST, DEVELOPMENT USE ONLY
# RUN THE BLOW CODE TO PRINT RAW DATA STRUCTURE

if __name__ == '__main__':

    import requests
    import json

    stock_code = "sz000011"
    url = f"http://ifzq.gtimg.cn/appstock/app/kline/mkline?param={stock_code},m1,,10"
    
    response = requests.get(url, allow_redirects=True)
    information = json.loads(response.content)
    raw_data = information['data'][stock_code]['qt'][stock_code]
    print(raw_data)

# END OF UNIT TEST
#---------------------------------------------------------------------------------

# END OF FILE
#---------------------------------------------------------------------------------