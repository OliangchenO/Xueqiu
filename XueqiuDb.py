# -*-coding=utf-8-*-
#抓取雪球的收藏文章
from _ast import Str
from _datetime import date
__author__ = 'liache'
import requests,http.cookiejar,re,json,time
import pandas as pd
import urllib.request
from urllib import parse
from toolkit import Toolkit
from lxml import etree
import http.client
from bs4 import BeautifulSoup
from jtc import Json
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

def xueqiu_login_url():
    xueqiu_login_url='https://xueqiu.com/snowman/login'
    agent = 'Mozilla/5.0 (Windows NT 5.1; rv:33.0) Gecko/20100101 Firefox/33.0'
    headers = {'Host': 'xueqiu.com',
           'Referer': 'https://xueqiu.com/',
           'Origin':'https://xueqiu.com',
           'User-Agent': agent}
    account=Toolkit.getUserData('data.cfg')
    data={'username':account['snowball_user'],'password':account['snowball_password']}
    s=session.post(xueqiu_login_url,data=data,headers=headers)
 
def get_xueqiu_hold(cube_symbol,cube_weight):
    cubeholding = {}
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
    for d in data["view_rebalancing"]["holdings"]:
        if d['stock_name'] in projects.keys():
            projects[d['stock_name']] += d['weight']*cube_weight        
        else:
            projects[d['stock_name']]= d['weight']*cube_weight
    for d in data["view_rebalancing"]["holdings"]:
        if d['stock_name'] in cubeholding.keys():
            cubeholding[d['stock_name']] += d['weight']*cube_weight        
        else:
            cubeholding[d['stock_name']]= d['weight']*cube_weight
    print("组合："+cube_symbol+"权重："+str(cube_weight))
    print(cubeholding)
    print("-------------------------------------------------------------")
    
def get_xueqiu_cube_list(category,count,orderby):
    url=cube_list_url+"?category="+category+"&count="+count+"&market=cn&profit="+orderby
    data = request(url,cookie)
    jsonObj = json.loads(data.read())
    if category == 14:
        cubetable = db.create_table('HighScoreCube', primary_id='id', primary_type='Integer')
    else:
        cubetable = db.create_table('MostProfitCube', primary_id='id', primary_type='Integer')
    dictCub = {}
    print(jsonObj["list"])
    print(cubetable)
    dictCub = {k: v for dct in jsonObj["list"] for k, v in dct.items()}
    print(dictCub)
    cubetable.insert(dictCub)
    result = db.query('SELECT * FROM MostProfitCube')
    for row in result:
        print(row['id'])
#     for TopestCube in jsonObj["list"]:
#         daily_gain = TopestCube["daily_gain"]
#         monthly_gain = TopestCube["monthly_gain"]
#         annualized_gain_rate = TopestCube["annualized_gain_rate"]
#         total_gain = TopestCube["total_gain"]
#         symbol = TopestCube["symbol"]
#         get_xueqiu_hold(symbol, total_gain/100)
#     print("-------------------------------------------------------------")
#     print(projects)
#     print("-------------------------------------------------------------")
#     print(sort_by_value(projects))

def sort_by_value(d):
    items=d.items()
    backitems=[[v[1],v[0]] for v in items]
    backitems.sort()
    return [ backitems[i][1] for i in range(0,len(backitems))]

def searchFromDb():
    db = TinyDB('data/db_Cube')
    table = db.table('Cube')
    for row in table:
        get_xueqiu_hold(row.get('symbol'),row.get('annualized_gain_rate')/(100))

def calculate():
    db = TinyDB('data/db_holding.json')
    for cube_symbol in db.tables():
        HoldingTable = db.table(cube_symbol)
        for row in HoldingTable:
            
            print(row)
        
def download():
    stock_se = pd.Series()
    from_se = pd.Series()
    to_se = pd.Series()
    from_w_se = pd.Series()
    to_w_se = pd.Series()
    cash_se = pd.Series()
    price_se = pd.Series()
    df = pd.DataFrame()
    for page in range(1,19):
        symbol = "ZH003851"
        url = "https://xueqiu.com/cubes/rebalancing/history.json?cube_symbol="+symbol+"&count=50&page="
        cookie = "xq_a_token=d4cae93eb5b67871c8ee5ef2bd80813fc65ba34a; xq_r_token=a6cddf77f7d8a04010ec94ca7a39618ff09f5921;"
        data = request(url+str(page),cookie)
        jsonObj = json.loads(data.read())
        for rebalance in jsonObj["list"]:
            if rebalance["status"] == "success":
                items = rebalance["rebalancing_histories"]
                cash = rebalance["cash_value"]
                for item in items:
                    timeStp = item["updated_at"]
                    ltime=time.localtime(timeStp/1000.0) 
                    timeStr=time.strftime("%Y-%m-%d %H:%M:%S", ltime)
                    prev_value = item["prev_net_value"]
                    stock = item["stock_symbol"]
                    value = item["net_value"]
                    weight = item["weight"]
                    prev_weight = item["prev_weight_adjusted"]
                    price = item["price"]
                    cash_se[timeStr] = cash
                    # rebalance_type = ""
                    if prev_value is None and value > 0:
                        # rebalance_type = "BUY"
                        from_se[timeStr] = 0
                        from_w_se[timeStr] = 0
                    else:
                        from_se[timeStr] = prev_value
                        from_w_se[timeStr] = prev_weight

                    to_w_se[timeStr] = weight   
                    to_se[timeStr] = value
                    stock_se[timeStr] = stock
                    price_se[timeStr] = price
            else:
                print (rebalance["status"])
    df["stock"] = stock_se
    df["from"] = from_se
    df["to"] = to_se
    df["from_w"] = from_w_se
    df["to_w"] = to_w_se
    df["cash"] = cash_se
    df["price"] = price_se
    df.to_csv("data.csv")
#     print (df.head(20))


# update_cookie()
session = requests.session()
session.cookies = http.cookiejar.LWPCookieJar(filename="cookies")
try:
    session.cookies.load(ignore_discard=True)
except:
    print ("Cookie can't load")
 

projects = {}
db = dataset.connect('sqlite:///:memory:')
cookie = "xq_a_token=d4cae93eb5b67871c8ee5ef2bd80813fc65ba34a; xq_r_token=a6cddf77f7d8a04010ec94ca7a39618ff09f5921;"
# session.cookies.save()
cube_list_url="https://xueqiu.com/cubes/discover/rank/cube/list.json"
cube_hold_url="https://xueqiu.com/P/"
get_xueqiu_cube_list("14","100","annualized_gain_rate")