import MySQLdb as mysql
from dbSetting import host, user, password, dbname

def getConnection():
    return mysql.connect(host, user, password, dbname, charset='utf8')

