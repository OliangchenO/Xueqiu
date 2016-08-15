#-*-coding=utf-8-*-
__author__ = 'rocky'
import scrapy

class XueQiuSpider(scrapy.Spider):

    name = "xueqiu"
    allowed_domains = ["xueqiu.com"]
    start_urls = ["http://xueqiu.com/8255849716"]

    def parse(self, response):
        print "*" * 10
        print response.url
