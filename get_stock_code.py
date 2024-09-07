import requests
from bs4 import BeautifulSoup
import pandas as pd

def stock_prefix(stockCode:str) -> str:
    if stockCode.find(r'60', 0, 3) == 0:
        return r'sh'
    elif stockCode.find(r'688', 0, 4) == 0:
        return r'sh'
    elif stockCode.find(r'900', 0, 4) == 0:
        return r'sh'
    elif stockCode.find(r'00', 0, 3) == 0:
        return r'sz'
    elif stockCode.find(r'300', 0, 4) == 0:
        return r'sz'
    elif stockCode.find(r'200', 0, 4) == 0:
        return r'sz'
    return r'None'

url = f'http://www.haiguitouzi.com/doc/intro_stock_list.php'

resp = requests.get(url=url)
soup = BeautifulSoup(resp.text, 'html.parser')

tableAnchor = soup.find(name='table', attrs={'class': 'layui-table'})

stockCodeList = []
for tr in tableAnchor.find_all(name='tr')[1:]:
    for td in tr.find_all(name='td'):
        stockCodeList.append(td.text[:6])



fullCodeList = []
for stockCode in stockCodeList:
    # print(stockCode)
    prefix = stock_prefix(stockCode=stockCode)
    if prefix == r'None':
        continue
    else:
        full = prefix + stockCode
        fullCodeList.append(full)

print(len(fullCodeList))
df = pd.DataFrame(fullCodeList)
df.to_csv(r'./stock_code.csv', header=False, index=False)
