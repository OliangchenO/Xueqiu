# -*-coding=utf-8-*-
__author__ = 'Rocky'
import requests,time
from lxml import etree
def check_strategy():
    header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'}
    Status_Code=200
    base_url='https://xueqiu.com/strategy/'
    for i in range(100):
        url=base_url+str(i)
        resp=requests.get(url,headers=header)
        if resp.status_code==200:
            print '%d has strategy' %i
            content=resp.text
            tree=etree.HTML(content)
            all_contnet=tree.xpath('//div[@class="detail-bd"]')
            print tree.xpath('//title/text()')[0]
            for i in all_contnet:
                print i.xpath('string(.)')

        time.sleep(10)



def main():
    check_strategy()

if __name__=='__main__':
    main()