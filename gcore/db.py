import sqlite3
from .filesys import exRm

class DatabaseManager(object):
    def __init__(self, db, remove):
        dbFname = db+'.db'
        self.sqlFile = None
        if remove:
            exRm(dbFname)
        self.conn = sqlite3.connect(dbFname)
        self.conn.text_factory = str
        self.conn.row_factory = lambda cursor, row: row[0]
        self.conn.execute('pragma foreign_keys = on')
        self.conn.commit()
        self.cur = self.conn.cursor()

    def readSql(self,file):
        self.instF = open(file,'r')
        self.instSQL = ''
        for l in self.instF:
            self.instSQL = self.instSQL+l
        return self.instSQL

    def query(self,q,fo=False):
        if q.count(';') > 1:
            self.cur.executescript(q)
        elif q.count(';') <= 1 and fo == False:
            self.cur.execute(q)
        else:
            self.foq = self.cur.execute(q)
        self.conn.commit()
        return self.foq.fetchone() if fo else list(self.cur)

    def index(self,tableName,field):
        iQuery = ""
        for i in field:
            idxQuery = "CREATE INDEX idx_"+i+"_"+tableName+" ON "+tableName+" ("+i+" ASC);"
            iQuery = iQuery + idxQuery+'\n'
        iQuery = iQuery[:-1]
        self.query(iQuery)
        return iQuery

    def __del__(self):
        self.conn.close()
