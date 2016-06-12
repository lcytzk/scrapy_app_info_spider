from scrapy.spiders import CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from app_info_spiders.items import AppItem
from app_info_spiders.wandoujiaApi import WdjApiService
from app_info_spiders import dbconnection

def loadPackages():
    db = dbconnection.getConnection()
    cur = db.cursor()
    sql = '''
        select packageName from app_info_detail where source='wandoujia'
    '''
    cur.execute(sql)
    rows = cur.fetchall()
    packages = set()
    for row in rows:
        packages.add(row[0])
    cur.close()
    db.close()
    return packages

packages = loadPackages()

class wandoujiaSpider(CrawlSpider):
    name = "wandoujia"
    allowed_domains = ["wandoujia.com"]
    start_urls = [
        "http://www.wandoujia.com/apps",
    ]
    rules = [
        Rule(LinkExtractor(allow=(
                'http://www.wandoujia.com/apps/(\w+\\..*)',
#               'http://www.wandoujia.com/top/(.*)', \
            ),
            deny=('http://www.wandoujia.com/apps/(.*)/(.*)')), callback='parse_wandoujia', follow=False
        ),
        Rule(LinkExtractor(allow=(
                'http://www.wandoujia.com/category/([0-9_]*)$',
            )),
            follow=True
        ),
    ]

    def parse_wandoujia(self, response):
        package = response.url.split('/')[-1]
        if not self.isPackage(package):
            return
        if package not in packages:
            packages.add(package)
            app = AppItem()
            app['packageName'] = package
            app['source'] = 'wandoujia'
            return app

    def isPackage(self, package):
        return package.find('.') >= 0 and package.find('%') < 0 and package.find('?') < 0

    def closed(self, reason):
        self.waitAllFinish()

    def waitAllFinish(self):
        WdjApiService.wait()




