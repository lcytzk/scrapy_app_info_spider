from scrapy.contrib.spiders import CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from bs4 import BeautifulSoup

def parser(html):
    res = []
    soup = BeautifulSoup(html)
    res.append(soup.find(id='appSoftName').get_text().strip().split('(')[0])
    tags = soup.find('div', class_='detail_tip')
    tagRes = []
    for tag in tags.find_all('a')[1:]:
        tagRes.append(tag.get_text())
    res.append(','.join(tagRes))
    return res


def loadPackageNames():
    pass

packageNames = loadPackageNames()

class HiapkSpider(CrawlSpider):
    name = "hiapk"
    allowed_domains = ["apk.hiapk.com"]
    start_urls = [
        "http://apk.hiapk.com/",
    ]
    rules = [
        Rule(LinkExtractor(allow=(), deny=(
            '(.*)\\.apk',
            '(.*)/appdown/(.*)',
            )),
            callback='my_parse',
            follow=True
        ),
    ]

    def my_parse(self, response):
        if not response.url.startswith('http://apk.hiapk.com/appinfo/'):
            return
        packageName = response.url.split('/')[-1]
        if not self.isPackage(packageName):
            return
        if packageName not in packageNames:
            info = parser(response.body)
            packageNames.add(packageName)
            self.writeDetail(packageName, info)

    def isPackage(self, name):
        return name.find('.') >= 0 and name.find('?') < 0

    def writeDetail(self, name, info):
        pass





