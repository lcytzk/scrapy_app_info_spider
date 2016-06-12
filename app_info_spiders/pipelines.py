# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import dbconnection
from wandoujiaApi import WdjApiService

class AppInfoPipeline(object):

    def __init__(self):
        self.db = dbconnection.getConnection()
        self.cur = self.db.cursor()

    def process_item(self, item, spider):
        if item['source'] == 'wandoujia':
            self.fetchInfoForWdj(item['packageName'])
            return item
        sql = '''
            insert into app_info_detail (packageName, packageid, title, source, tag)
            values ('{0}', {1}, "{2}", '{3}', '{4}')
        '''.format(item['packageName'], item['packageId'], item['title'], item['source'], item['tag'])
        self.cur.execute(sql)
        self.db.commit()
        return item

    def fetchInfoForWdj(self, packageName):
        WdjApiService.schedule(packageName)

    def __del__(self):
        self.cur.close()
        self.db.close()
