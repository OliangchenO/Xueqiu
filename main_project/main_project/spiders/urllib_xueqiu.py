#-*-coding=utf-8-*-
__author__ = 'Rocky'
import urllib2,urllib
class Myurllib2():
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
        self.header = {"User-Agent": self.user_agent,
                       'Host':'xueqiu.com',
                       'Cookie':'s=2ca2126gi2; bid=a8ec0ec01035c8be5606c595aed718d4_ijwlsvec; webp=0; xq_a_token=b5c9d7e0742fac29b4f6a8fb9bb9bd20eb617836; xq_r_token=2f136054f09ada370c42c4c825b9603e8f98ca15; u=1733473480; xq_token_expire=Fri%20Aug%2019%202016%2013%3A07%3A21%20GMT%2B0800%20(CST); xq_is_login=1; __utmt=1; snbim_minify=true; Hm_lvt_1db88642e346389874251b5a1eded6e3=1469423225,1469604174,1470328717,1471071812; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1471076148; __utma=1.1916182507.1453128479.1471071812.1471076083.18; __utmb=1.6.9.1471076153043; __utmc=1; __utmz=1.1453128479.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'

}
        #self.url="http://xueqiu.com/8255849716"
        self.url="http://xueqiu.com/v4/statuses/user_timeline.json?user_id=8255849716&page=2&type=&_=1471076456698"


    def getContent(self,url=""):
        url=self.url
        #http://xueqiu.com/8255849716
        post_data={'user_id':'8255849716','page':'3','_':'1471076456698'}
        data=urllib.urlencode(post_data)
        req = urllib2.Request(url,data=data,headers=self.header)
        resp = urllib2.urlopen(req)
        content = resp.read()
        return content


obj=Myurllib2()
content=obj.getContent()
print content