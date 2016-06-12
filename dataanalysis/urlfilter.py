#!/usr/bin/env python

from scrapy.dupefilters import RFPDupeFilter
from localSetting import task
from filterSetting import getPersistFilter
import dbconnection

class URLFilter(RFPDupeFilter):

    def __init__(self, path, debug):
        RFPDupeFilter.__init__(self, path, debug)
        self.db = dbconnection.getConnection()
        self.cur = self.db.cursor()
        self.task = task
        self.urls = self.loadFromDB()
        self.filter = getPersistFilter(self.task)

    def request_seen(self, request):
        if request.url in self.urls:
            return True
        self.urls.add(request.url)
        self.persistUrl(request.url)

    def loadFromDB(self):
        sql = '''
            select url from url_record where source='{0}'
        '''.format(self.task)
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        urls = set()
        for row in rows:
            urls.add(row[0])
        return urls

    def persistUrl(self, url):
        if self.filter(url):
            return
        sql = '''
            insert into url_record(source, url) values('{0}', '{1}')
        '''.format(self.task, url)
        self.cur.execute(sql)
        self.db.commit()
