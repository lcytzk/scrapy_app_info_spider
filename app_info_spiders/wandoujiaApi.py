#!/usr/bin/env python
import sys
import json
import threading, Queue
import urllib2
import md5
from datetime import datetime
import dbconnection
import MySQLdb as mysql
import time

ID = ''
KEY = ''

MAX_REQUEST = 403
NO_APP = 404
OTHER_ERROR = 0

URL = 'http://api.wandoujia.com/v1/apps/%s?id=%s&timestamp=%s&token=%s'

DB = dbconnection.getConnection()
CUR = DB.cursor()

def getUrl(packageName):
    timestamp = getTimestamp()
    token = getMd5(ID + KEY + timestamp)
    return URL % (packageName, ID, timestamp, token)

def getTimestamp():
    t = datetime.now()
    return '%s%d' % (t.strftime('%m%d%H%M%S'), t.microsecond/1000)

def getMd5(original):
    m = md5.new()
    m.update(original)
    return m.hexdigest()

def getResult(url):
    try:
        return urllib2.urlopen(url, timeout=3).read()
    except urllib2.HTTPError as e:
        return e.getcode()
    except:
        return OTHER_ERROR

def getPackageInfo(packageName):
    return getResult(getUrl(packageName))

def persistPackageInfo(packageName, jsonStr):
    if jsonStr == MAX_REQUEST:
        print >> sys.stderr, \
            'Fail here index: %d. Success number: %d. Wait for an hour' % (i, count)
    elif jsonStr == NO_APP:
        print >> sys.stderr, 'No such app? %s' % name
    elif jsonStr == OTHER_ERROR:
        print >> sys.stderr, 'other error? %s' % name
    else:
        saveJson(packageName, jsonStr)
        saveDetail(packageName, jsonStr)

def saveJson(packageName, jsonStr):
    sql = '''
    insert into app_info_wandoujia values('{0}', '{1}')
    '''.format(packageName, jsonStr)
    executeSql(sql)

def saveDetail(packageName, jsonStr):
    j = json.loads(jsonStr, encoding="utf-8")
    tag = ','.join([t['tag'] for t in j['tags']]).encode('utf-8')
    cate = ','.join([t['name'] for t in j['categories']]).encode('utf-8')
    tmp = tag + "," + cate
    sql = '''
        insert into app_info_detail (packageName, title, source, tag)
        values ('{0}', "{1}", '{2}', '{3}')
    '''.format(packageName, j['title'].encode('utf8'), 'wandoujia', tmp)
    executeSql(sql)

def executeSql(sql):
    global DB, CUR
    try:
        CUR.execute(sql)
        DB.commit()
    except mysql.Error as err:
        print err
        if err[0] == 2006:
            print 'renew connection'
            DB = dbconnection.getConnection()
            CUR = DB.cursor()
            executeSql(sql)

class WdjApiTask:

    def __init__(self, packageName):
        self.packageName = packageName

    def run(self):
        WdjApiService.jsonQueue.put(PersistTask(self.packageName, getPackageInfo(self.packageName)))

class PersistTask:

    def __init__(self, packageName, jsonStr):
        self.packageName = packageName
        self.jsonStr = jsonStr

    def run(self):
        persistPackageInfo(self.packageName, self.jsonStr)


class Executor(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.stop = False

    def setTask(self, task):
        self.task = task

    def getNextTask(self):
        try:
            self.task = self.queue.get(timeout=3)
        except:
            self.task = None

    def run(self):
        while not self.stop:
            self.getNextTask()
            try:
                if self.task != None:
                    self.task.run()
            except Exception as e:
                print >> sys.stderr, e
        print 'finished'

    def stopTask(self):
        self.stop = True

TASK_NUM = 10

class WdjApiService:

    queue = Queue.Queue()
    jsonQueue = Queue.Queue()
    executors = [Executor(queue) for i in range(TASK_NUM)]
    executors.append(Executor(jsonQueue))
    closed = False

    for exe in executors:
        exe.start()

    @staticmethod
    def schedule(packageName):
        if not WdjApiService.closed:
            WdjApiService.queue.put(WdjApiTask(packageName))

    @staticmethod
    def wait():
        print 'wait for finish'
        WdjApiService.closed = True
        for executor in WdjApiService.executors:
            executor.stopTask()
        for executor in WdjApiService.executors:
            executor.join()

if __name__ == '__main__':
    WdjApiService.schedule('com.tencent.mm')
    time.sleep(10)


