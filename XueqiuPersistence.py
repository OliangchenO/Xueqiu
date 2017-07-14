# -*-coding=utf-8-*-
#抓取雪球的收藏文章
from numpy.f2py.auxfuncs import throw_error
from numpy import rank
__author__ = 'liache'
from _ast import Str
from _datetime import date, datetime
import requests,http.cookiejar,re,json,time
import pandas as pd
import urllib.request
from urllib import parse
from toolkit import Toolkit
from lxml import etree
import http.client
from bs4 import BeautifulSoup
import easytrader
import math
import dataset

def request(url, cookie=''):
    ret = parse.urlparse(url)    # Parse input URL
    if ret.scheme == 'http':
        conn = http.client.HTTPConnection(ret.netloc)
    elif ret.scheme == 'https':
        conn = http.client.HTTPSConnection(ret.netloc)
    url = ret.path
    if ret.query: url += '?' + ret.query
    if ret.fragment: url += '#' + ret.fragment
    if not url: url = '/'
    conn.request(method='GET', url=url , headers={'Cookie': cookie})
    return conn.getresponse()

def holdinfo_save(holdInfo):
    table = db['CubeHolding']
    cube_symbol = holdInfo["cube_symbol"]
    stock_symbol = holdInfo["stock_symbol"]
    res = table.find_one(cube_symbol=cube_symbol,stock_symbol=stock_symbol)
    if res == None:
        holdInfo["save_date"] = today
        holdInfo["update_date"] = today
        table.insert(holdInfo)
        print(holdInfo)
    else:
        holdInfo["update_date"]=today
        table.update(holdInfo,['stock_code','cube_symbol','save_date'])

def cubelist_save(TopestCube):
    table = db['CubeList']
    symbol = TopestCube["symbol"]
    orderType = TopestCube["orderType"]
    res = table.find_one(symbol=symbol,orderType=orderType)
    if res == None:
        TopestCube["save_date"] = today
        TopestCube["update_date"]=today
        table.insert(TopestCube)
    else:
        TopestCube["update_date"]=today
        table.update(TopestCube,['symbol','orderType'])
    
def stock_weight_save(stock_weight):
    table = db['StockWeight']
    res = table.find_one(update_date=today)
    if res == None:
        stock_weight["save_date"] = today
        stock_weight["update_date"]=today
        table.insert(stock_weight)
    else:
        stock_weight["update_date"]=today
        table.update(stock_weight, ["update_date"])
    for weight in table.find(update_date=today):
        print(weight)    
 
def operating_record_save(operating_record):
    table = db['OperatingRecord']
    res = table.find_one(operate_date=today,stock_code=operating_record["stock_code"])
    if res == None:
        table.insert(operating_record)
    else:
        table.update(operating_record, ["stock_code","operate_date"])
  
def get_cube_hold(cube_symbol):
    table = db['CubeHolding']
    req = urllib.request.Request(cube_hold_url+cube_symbol,headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:33.0) Gecko/20100101 Firefox/33.0',
                'cookie':cookie
               })
    soup = urllib.request.urlopen(req).read().decode('utf-8')
    soup = BeautifulSoup(soup, 'lxml')
    script = soup.find('script', text=re.compile('SNB\.cubeInfo'))
    json_text = re.search(r'^\s*SNB\.cubeInfo\s*=\s*({.*?})\s*;\s*$',
                      script.string, flags=re.DOTALL | re.MULTILINE).group(1)
    data = json.loads(json_text)
    for holdInfo in data["view_rebalancing"]["holdings"]:
        holdInfo["cube_symbol"] = cube_symbol
        holdinfo_save(holdInfo)

def get_cube_list(category,count,orderType):
    url=cube_list_url+"?category="+category+"&count="+count+"&market=cn&profit="+orderType
    data = request(url,cookie)
    jsonObj = json.loads(data.read())
    rank = 1
    for TopestCube in jsonObj["list"]:
        created_at = TopestCube["created_at"]
        ltime=time.localtime(created_at/1000.0) 
        created_at_str=time.strftime("%Y-%m-%d", ltime)
        TopestCube["created_at"] = created_at_str
        updated_at = TopestCube["updated_at"]
        ltime=time.localtime(updated_at/1000.0) 
        updated_at_str=time.strftime("%Y-%m-%d", ltime)
        TopestCube["updated_at"] = updated_at_str
        TopestCube["category"] = category
        TopestCube["orderType"] = orderType
        TopestCube["Rank"] = rank
        del(TopestCube["style"],TopestCube["description"],TopestCube["owner"])
        cubelist_save(TopestCube)
        rank = rank + 1
    
def sort_by_value(d):
    items=d.items()
    backitems=[[v[1],v[0]] for v in items]
    backitems.sort(reverse=True)
    return [ backitems[i][1] for i in range(0,len(backitems))]

def storedata(category,count,orderType):
    stock_weight = {}
    cubelistTable = db['CubeList']
    cubeholeTable = db['CubeHolding']
    if cubelistTable.find_one(orderType=orderType,category=category,update_date=today) == None:
        get_cube_list(category,count,orderType)
    else:
        cubelist=cubelistTable.find(orderType=orderType,category=category,update_date=today, order_by='Rank')
        for cube in cubelist:
            cube_weight = cube["annualized_gain_rate"]/100
            if cubeholeTable.find_one(cube_symbol=cube["symbol"],update_date=today) == None:
                get_cube_hold(cube["symbol"])
            else:
                for stock in cubeholeTable.find(cube_symbol=cube["symbol"],update_date=today):
                    if stock['stock_name']+stock['stock_symbol'] in stock_weight.keys(): 
                        stock_weight[stock["stock_name"]+stock["stock_symbol"]] += stock["weight"]*cube_weight
                    else:
                        stock_weight[stock["stock_name"]+stock["stock_symbol"]] = stock["weight"]*cube_weight
    stock_weight_save(stock_weight)
    return stock_weight

def xueqiu_adjust_weight(category,count,orderType):
    
    if db.get_table("OperatingRecord").find_one(operate_date=today)==None:
        stock_weight=storedata(category,count,orderType)
        print(stock_weight)
        del(stock_weight["update_date"])
        sorted_stock = sort_by_value(stock_weight)[:5]
        print(sorted_stock)
        user = easytrader.use('xq')
        user.prepare('xq.json')
        for holding_stock in user.get_position():
            operating_record = {}
            if holding_stock['stock_name']+holding_stock['stock_code'] in sorted_stock:
                pass
            else:
#               user.adjust_weight(holding_stock['stock_code'][6:],0)
                print("卖出:"+holding_stock['stock_name']+holding_stock['stock_code'])
                operating_record["stock_code"]=holding_stock["stock_code"]
                operating_record["stock_name"]=holding_stock["stock_name"]
                operating_record["weight"]=0
                operating_record["operate"]="清仓"
                operating_record["operate_date"]=today
                operating_record_save(operating_record)
        totol_weight = 0.0
        adjust_weight = {}
        for i in range(5):
            totol_weight +=stock_weight[sorted_stock[i]]
        for i in range(5):
            operating_record = {}
            weight = stock_weight[sorted_stock[i]]/totol_weight*100
            adjust_weight[sorted_stock[i]]= weight
#             user.adjust_weight(sorted_stock[i][-6:],math.floor(weight))
            operating_record["stock_code"]=sorted_stock[i][-8:]
            operating_record["stock_name"]=sorted_stock[i][:-8]
            operating_record["weight"]=math.floor(weight)
            operating_record["operate"]="调仓"
            operating_record["operate_date"]=today
            print('雪球调仓成功，买入：'+sorted_stock[i]+", 仓位："+str(math.floor(weight)))
            operating_record_save(operating_record)
    else:
        for operate in db.get_table("OperatingRecord").find(operate_date=today):
            print(operate)
    
today = datetime.now().strftime("%Y-%m-%d")
db = db = dataset.connect('sqlite:///Xueqiu.db')
cookie = "xq_a_token=cee27ba564aeda64291f3368cb6f197f52271fde; xq_r_token=ed7cdf6fdfff2c92adddcba4a65a31c5ec494660;"
# session.cookies.save()
cube_list_url="https://xueqiu.com/cubes/discover/rank/cube/list.json"
cube_hold_url="https://xueqiu.com/P/"
# db.get_table("OperatingRecord").drop()
xueqiu_adjust_weight("14", "100", "annualized_gain_rate")
# select_new_stock()