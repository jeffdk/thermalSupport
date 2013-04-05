import os
import sqlite3
import sys
from maxMassOrigFiles.sqlPlotRoutines import equalsFiltersFromDict
import parseFiles
from scriptPlotstyleDatabase import tempPrescription, scriptFromScriptName
from sqlUtils import queryDBGivenParams


class cstDataset(object):
    """
    A cstDataset contains all run data for a given eos, ye and
     temperature prescription
    Creates a temporary database on disk to manage the db
    Note we do this so that cstSequence can attach this database when
    it populates it's own table (which uses :memory:)
     (The issue is you cannot use :memory: if you wish to refer to the
      database later)
    """
    def __init__(self, tempScriptName, eosName, ye, dbFilename=None):

        self.tempScript = scriptFromScriptName(tempScriptName)
        self.eosName = eosName
        self.ye = ye
        self.paramsDict = self.tempScript.paramsDict
        self.name = tempScriptName + eosName + str(ye).replace('.', '')
        self.dbName = "_tempDB_" + self.name + ".db"
        self.paramsDict.update({'eos': self.eosName, 'ye': self.ye})
        #print self.paramsDict

        self.dbConn = sqlite3.connect(self.dbName)
        cursor = self.dbConn.cursor()
        cursor.execute("CREATE TABLE models " + parseFiles.columnsString)
        self.dbConn.commit()

        if dbFilename is not None:
            self.addEntriesFromDb(dbFilename)
            pass

    def __del__(self):
        self.dbConn.close()
        os.remove(self.dbName)

    def addEntriesFromDb(self, dbFilename):
        cursor = self.dbConn.cursor()
        query = "WHERE " + " AND ".join(["%s='%s'" % (key, value) for (key, value)
                                         in self.paramsDict.items()])
        cursor.execute("ATTACH '" + dbFilename + "' AS toMerge")
        cursor.execute("INSERT INTO models SELECT * FROM toMerge.models " + query)
        self.dbConn.commit()

        cursor.execute("SELECT count(*) FROM models")

        print "Added %s entries to cstDataset '%s'" % (cursor.fetchone()[0], self.name)


class cstSequence(object):
    """
    A cstSequence is a subset of a cstDataset for use in plotting.
    Two of the three CST independent variables ('a', 'edMax', 'rpoe') are fixed
    and the sequence is parametrized by (aka ordered by) the third
    """

    indVars = ('a', 'edMax', 'rpoe')

    def __init__(self, inputCstDataset, fixedIndVarsDict):
        """
        Takes fixedIndVarsDict, and sets the parameter to the indVar
        not in the dict.
        """
        #todo ADD MIN RPOE SUPPORT
        assert isinstance(inputCstDataset, cstDataset)
        assert all([key in self.indVars for key in fixedIndVarsDict.keys()]), \
            "Not all keys in fixedIndVarsDict are proper indVars"
        assert len(fixedIndVarsDict) == 2, "Must fix 2 indVars!"

        self.orderByVar = [indVar for indVar in self.indVars if indVar not in fixedIndVarsDict][0]

        sliceFilters = equalsFiltersFromDict(fixedIndVarsDict, tolerance=1e-3)
        query = "WHERE " + " AND ".join(sliceFilters) + " ORDER BY " + self.orderByVar

        self.dbConn = sqlite3.connect(':memory:')
        cursor = self.dbConn.cursor()
        cursor.execute("CREATE TABLE models " + parseFiles.columnsString)
        print query
        cursor.execute("ATTACH '" + inputCstDataset.dbName + "' AS toMerge")
        cursor.execute("INSERT INTO models SELECT * FROM toMerge.models " + query)
        self.dbConn.commit()

        for i in cursor.execute("SELECT * FROM models"):
            print i

        cursor.execute("SELECT count(*) FROM models")
        print "Sliced %s entries into cstSequence '%s' from cstDataset '%s'"\
              % (cursor.fetchone()[0], str(fixedIndVarsDict), inputCstDataset.name)

    def getSeqPlot(self, xcolVars, ycolVars, filters=(), colorVars=None,
                   xcolFunc=lambda x: x, ycolFunc=lambda x:x, colorVarsFunc=lambda x: x):
        pass
