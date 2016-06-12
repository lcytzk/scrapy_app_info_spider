from scrapy.spiders import CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from bs4 import BeautifulSoup
from scrapy.http import FormRequest
from dataanalysis.items import AppItem
from dataanalysis.wandoujiaApi import WdjApiService
from dataanalysis import dbconnection

def parser360(html):
    res = []
    soup = BeautifulSoup(html)
    for s in soup.find_all('script'):
        fields = s.get_text().split(',')
        for field in fields:
            index = field.find('pname')
            if index >= 0:
                res.append(field.split(':')[1].strip()[1:-1])
    res.append(soup.find(id='app-name').span.get_text())
    tags = soup.find('div', class_='app-tags')
    if tags == None:
        res.append('')
        return res
    tagRes = []
    for tag in tags.find_all('a'):
        tagRes.append(tag.get_text())
    res.append(','.join(tagRes))
    return res

def loadPackageids():
    db = dbconnection.getConnection()
    cur = db.cursor()
    sql = '''
        select packageid from app_info_detail where source='360'
    '''
    cur.execute(sql)
    rows = cur.fetchall()
    packages = set()
    for row in rows:
        packages.add(row[0])
    cur.close()
    db.close()
    return packages

packageids = loadPackageids()

class T360Spider(CrawlSpider):
    name = "360"
    allowed_domains = ["zhushou.360.cn"]
    start_urls = [
        "http://zhushou.360.cn/",
        'http://zhushou.360.cn/game',
        'http://zhushou.360.cn/soft',
    ]
    rules = [
        Rule(LinkExtractor(allow=(
                    'http://zhushou.360.cn/detail/index/soft_id/([0-9]*)',
                )
            ),
            callback='parse_360',
            follow=False
        ),
        Rule(LinkExtractor(allow=(
                    'http://zhushou.360.cn/list/index/cid/([0-9]*)$',
                )
            ),
            follow=True
        ),
        Rule(LinkExtractor(allow=(
                    'http://zhushou.360.cn/list/index/cid/([0-9]*)/(.*)'
                )
            ),
            callback='parseAndAddNewUrl',
            follow=True
        ),
    ]

    def parse_360(self, response):
        packageid = response.url.split('/')[-1]
        if packageid not in packageids:
            info = parser360(response.body)
            if info == None:
                return
            packageids.add(packageid)
            app = AppItem()
            app['packageName'] = info[0]
            app['title'] = info[1].encode('utf8')
            app['tag'] = info[2].encode('utf8')
            app['source'] = '360'
            app['packageId'] = packageid
            return app

    def parseAndAddNewUrl(self, response):
        if response.url.find('page') > 0:
            fields = response.url.split('=')
            page = int(fields[-1])
            if page < 50:
                fields[-1] = str(page+1)
            yield FormRequest('='.join(fields), callback=self.parse)


    def isPackage(self, package):
        try:
            int(package)
            return True
        except:
            return False

    def closed(self, reason):
        self.waitAllFinish()

    def waitAllFinish(self):
        WdjApiService.wait()





