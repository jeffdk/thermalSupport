import sqlite3
import parseFiles
from scriptPlotstyleDatabase import tempPrescription, scriptFromScriptName
from sqlUtils import queryDBGivenParams


class cstDataset(object):
    """
    A cstDataset contains all run data for a given eos, ye and
     temperature prescription
    """
    def __init__(self, tempScriptName, eosName, ye, dbFilename=None):

        self.tempScript = scriptFromScriptName(tempScriptName)
        self.eosName = eosName
        self.ye = ye
        self.paramsDict = self.tempScript.paramsDict
        self.paramsDict.update({'eos': self.eosName, 'ye': self.ye})
        #print self.paramsDict

        self.dbConn = sqlite3.connect(':memory:')
        cursor = self.dbConn.cursor()
        cursor.execute("CREATE TABLE models " + parseFiles.columnsString)
        self.dbConn.commit()

        if dbFilename is not None:
            self.addEntriesFromDb(dbFilename)
            pass

    def addEntriesFromDb(self, dbFilename):
        cursor = self.dbConn.cursor()
        query = "WHERE " + " AND ".join(["%s='%s'" % (key, value) for (key, value)
                                         in self.paramsDict.items()])
        cursor.execute("ATTACH '" + dbFilename + "' AS toMerge")
        cursor.execute("INSERT INTO models SELECT * FROM toMerge.models " + query)
        self.dbConn.commit()

        cursor.execute("SELECT count(*) FROM toMerge.models " + query)

        print "Added %s entries" % cursor.fetchone()
