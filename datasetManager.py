import os
import sqlite3
import numpy
from maxMassOrigFiles.sqlPlotRoutines import equalsFiltersFromDict
import parseFiles
from scriptPlotstyleDatabase import scriptFromScriptName
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

    #todo add support to remove duplicates
    def __init__(self, inputCstDataset, fixedIndVarsDict, filters=()):
        """
        Takes fixedIndVarsDict, and sets the parameter to the indVar
        not in the dict.
        filters only used for special case of selecting min rpoe
        """
        assert isinstance(inputCstDataset, cstDataset)
        assert all([key in self.indVars for key in fixedIndVarsDict.keys()]), \
            "Not all keys in fixedIndVarsDict are proper indVars"
        assert len(fixedIndVarsDict) == 2, "Must fix 2 indVars!"

        self.orderByVar = [indVar for indVar in self.indVars if indVar not in fixedIndVarsDict][0]

        copyOfInputDict = fixedIndVarsDict.copy()

        #Handle special case of selecting rpoe min
        restrictToRpoeMin = False
        if 'rpoe' in copyOfInputDict:
            if copyOfInputDict['rpoe'] == 'min':
                #delete it so we filter out nothing; do the rpoe min filtering later
                del copyOfInputDict['rpoe']
                restrictToRpoeMin = True

        sliceFilters = equalsFiltersFromDict(copyOfInputDict, tolerance=1e-3)
        query = "WHERE " + " AND ".join(sliceFilters) + " ORDER BY " + self.orderByVar

        self.dbConn = sqlite3.connect(':memory:')
        cursor = self.dbConn.cursor()
        cursor.execute("CREATE TABLE models " + parseFiles.columnsString)

        cursor.execute("ATTACH '" + inputCstDataset.dbName + "' AS toMerge")
        cursor.execute("INSERT INTO models SELECT DISTINCT * FROM toMerge.models " + query)
        self.dbConn.commit()

        if restrictToRpoeMin:
            # min rpoe occurs at the max run number for a given runID
            # method: for each runID, find the max lineNum (satisfying the filters!)
            # then, for that runID, delete entries that don't have that lineNum
            cursor.execute("SELECT DISTINCT runID FROM models")
            runIDs = cursor.fetchall()
            #print  len(runIDs), runIDs
            filtersString = ""
            if filters:
                filtersString = " AND " + " AND ".join(filters)
            #print filtersString
            for runID in runIDs:
                runID = runID[0]
                cursor.execute("SELECT MAX(lineNum) FROM models WHERE runID='" + runID + "'"
                               + filtersString)
                maxLineNum = cursor.fetchone()[0]
                #print runID, maxLineNum
                #if filters have filtered out all values, maxLineNum is None,
                # and the following query will fail, so lets just move on
                if maxLineNum is None:
                    continue
                # runType 3 means mass-shed sequence, so all rpoes are min!
                # so don't delete anything
                cursor.execute("DELETE FROM models WHERE runID='" + runID
                               + "' AND lineNum!=" + str(maxLineNum)
                               + " AND runType!=3")

        #for i in cursor.execute("SELECT * FROM models"):
        #    print i

        cursor.execute("SELECT count(*) FROM models")
        print "Sliced %s entries into cstSequence '%s' from cstDataset '%s'"\
              % (cursor.fetchone()[0], str(fixedIndVarsDict), inputCstDataset.name)

    def getSeqPlot(self, xcolVars, ycolVars, filters=(), colorVars=None,
                   xcolFunc=lambda x: x, ycolFunc=lambda x: x, colorVarsFunc=lambda x: x):
        """
        Selects data from the sequence for use in plotting.
        Will filter data if requested. Functions are for doing calculations with data.
        Returns numpy array of [xcol, ycol] or if colorVars, [xcol, ycol, colorCol]
        """
        answer = None
        if colorVars is not None:
            xs = self.getColumnData(xcolVars, xcolFunc, filters)
            ys = self.getColumnData(ycolVars, ycolFunc, filters)
            cs = self.getColumnData(colorVars, colorVarsFunc, filters)
            assert len(xs) == len(ys) and len(ys) == len(cs), \
                "Uh oh, columns not equal length; something very bad has happened"
            answer = numpy.array([xs, ys, cs])
        else:
            xs = self.getColumnData(xcolVars, xcolFunc, filters)
            ys = self.getColumnData(ycolVars, ycolFunc, filters)
            assert len(xs) == len(ys), \
                "Uh oh, columns not equal length; something very bad has happened"
            answer = numpy.array([xs, ys])
        #print answer
        return answer

    def getColumnData(self, colVars, colFunction, filters=()):

        rawData = queryDBGivenParams(colVars, [], self.dbConn.cursor(), 'models', filters,
                                     " ORDER BY " + self.orderByVar)
        #print rawData
        # light todo: add try catch to check num args
        rawData = [colFunction(*entry) for entry in rawData]
        #print rawData
        return rawData


#todo add colorVar support or rethink this function
def reduceTwoSeqPlots(seqA, seqB, func, tolerance=1e-5):
    """
    Takes two sets of output from getSeqPlot, and computes func on
    the entries in the ycol.  Only adds entry if xcols are within tol of each other
    ORDER MATTERS: x points used are seqA's x points!
    """

    newXs = []
    newYs = []
    for i, xpoint in enumerate(seqA[0]):
        for j, xpointSeqB in enumerate(seqB[0]):
            if abs(xpoint - xpointSeqB) < tolerance:
                newXs.append(xpoint)
                newYs.append(func(seqA[1][i], seqB[1][j]))
                #found match, so break
                break

    return numpy.array([newXs, newYs])