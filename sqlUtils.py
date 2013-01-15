#!/usr/bin/python
from copy import deepcopy
import sqlite3

def getColumnHeaders(tableName,cursor):
    
    result=""
    for info in cursor.execute("PRAGMA table_info(%s)"%tableName):
        result += str(info[1]) + ", "

    return result[:-2]


def dictFromRow(row, columnHeaders):
    headerList=columnHeaders.split(',')

    if not (len(row)==len(headerList)):
        exit("error in dictFromRow; row and column headers not of same size!")

    result = {}
    for i in range(len(row)):
        result[headerList[i]]=row[i]

    return result

def queryDBGivenParams(paramsDesired,inGivenParams,sqliteCursor,tableName,
                       customFilters=(), extraOpts=""):
    """
    Runs: SELECT paramsDesired  WHERE givenParams.keys() == givenParams[key] AND customFilters FROM tableName+extraOpts
    """
    if not isinstance(customFilters,tuple):
        assert isinstance(customFilters,str)
        customFilters= [customFilters]
    if isinstance(paramsDesired,str):
        paramsDesired=[paramsDesired]
    else:
        assert isinstance(paramsDesired,list)
        assert isinstance(paramsDesired[0],str)
    assert isinstance(sqliteCursor,sqlite3.Cursor)
    givenParams=deepcopy(inGivenParams)
    #Must convert units  from input units (CGS/1e15) to output units (CGS)
    if 'edMax' in givenParams:
        givenParams['edMax']=givenParams['edMax'] * 1e15

    query = "SELECT " + ", ".join(paramsDesired) + " FROM " + tableName
    if givenParams or customFilters:
        query += " WHERE "
    if givenParams:
        query += " AND ".join( ["%s='%s'" % (key,value) for (key,value) in givenParams.items()] )
        if customFilters:
            query += " AND "
    if customFilters:
        query += " AND ".join(customFilters)
    if extraOpts:
        query += extraOpts

    print query
    sqliteCursor.execute(query)
    listResult  =sqliteCursor.fetchall()
    return listResult