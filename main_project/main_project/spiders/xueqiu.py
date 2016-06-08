import scrapy


class DmozSpider(scrapy.spiders.Spider):
    name = "xueqiu"
    allowed_domains = ["xueqiu.com"]
    start_urls = ["https://xueqiu.com/8255849716"]


'''
name="30daydo"
allowed_domains=["30daydo.com"]
start_urls=["http://30daydo.com"]
'''


def parse(self, response):
    print "*" * 10
    print response.body
