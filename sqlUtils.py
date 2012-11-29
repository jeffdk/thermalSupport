#!/usr/bin/python
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
