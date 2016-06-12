from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy.http import FormRequest

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


def parseAndAddNewUrl(response):
    if response.url.find('page') > 0:
        fields = response.url.split('=')
        page = int(fields[-1])
        if page < 50:
            fields[-1] = str(page+1)
        yield FormRequest('='.join(fields), callback=self.parse)

