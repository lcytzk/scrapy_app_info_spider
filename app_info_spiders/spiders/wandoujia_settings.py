from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

allowed_domains = ["wandoujia.com"]
start_urls = [
    "http://www.wandoujia.com/apps",
]
rules = [
    Rule(LinkExtractor(allow=(
            'http://www.wandoujia.com/apps/(\w+\\..*)',
            'http://www.wandoujia.com/top/(.*)', \
        ),
        deny=('http://www.wandoujia.com/apps/(.*)/(.*)')), callback='parse_wandoujia', follow=False
    ),
    Rule(LinkExtractor(allow=(
            'http://www.wandoujia.com/category/([0-9_]*)$',
        )),
        follow=True
    ),
]
