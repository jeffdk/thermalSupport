#!/usr/bin/python

import os
import sqlite3
import re
from numpy import *
from matplotlib import pyplot as mpl
from mpl_toolkits.mplot3d import Axes3D 
import math


# if data(partitionField) > partition value, plot with dashed

plotFields="edMax,gravMass"
#sequence = ('HS','roll12.5',1.0,0.5)


def partitionPlot(partitionField, partitionValue,c,sequence,color):
    lineXs=[]
    lineYs=[]
    dashXs=[]
    dashYs=[]

    allXs=[]
    allYs=[]
    query = "SELECT " + plotFields + "," + partitionField + " FROM models "
    #query += " WHERE " + partitionField + " > " + str(partitionValue)
    query += " WHERE eos=?  AND tprofile=? AND a=? AND temp=? ORDER BY edMax"
    
    numLineSegments=0
    numDashSegments=0
    c.execute(query,sequence)
    row = c.fetchone()
    print query
    lastx = row[0]
    lasty = row[1]
    lastp = row[2]
    allXs.append(lastx)
    allYs.append(lasty)

    if lastp < partitionValue:
        lineXs.append([])
        lineYs.append([])
        lineXs[0].append(lastx)
        lineYs[0].append(lasty)
        numLineSegments+=1
    else:
        dashXs.append([])
        dashYs.append([])
        dashXs[0].append(lastx)
        dashYs[0].append(lasty)
        numDashSegments+=1

    for row in c.fetchall():
        x = row[0]
        y = row[1]
        p = row[2]
        if p < partitionValue and lastp < partitionValue:
            lineXs[numLineSegments -1].append(x)
            lineYs[numLineSegments -1].append(y)
        elif p > partitionValue and lastp > partitionValue:
            dashXs[numDashSegments -1].append(x)
            dashYs[numDashSegments -1].append(y)
        elif  p < partitionValue and lastp > partitionValue:
            lineXs.append([])
            lineYs.append([])
            numLineSegments+=1
            lineXs[numLineSegments -1].append(x)
            lineYs[numLineSegments -1].append(y)
        elif  p > partitionValue and lastp < partitionValue:
            dashXs.append([])
            dashYs.append([])
            numDashSegments+=1
            dashXs[numDashSegments -1].append(x)
            dashYs[numDashSegments -1].append(y)

        lastx=x
        lasty=y
        lastp=p
        allXs.append(lastx)
        allYs.append(lasty)
        
 #       lineXs.append(row[0])
 #       lineYs.append(row[1])

#    query = "SELECT " + plotFields + " FROM models "
#    query += " WHERE " + partitionField + " < " + str(partitionValue)
#    query += " AND eos=?  AND tprofile=? AND a=? AND temp=? ORDER BY edMax"
    
#    for row in c.execute(query,sequence):
#        dashXs.append(row[0])
#        dashYs.append(row[1])
    
    #print lineXs
    #print lineYs

    for i in range(numLineSegments):
        mpl.plot(lineXs[i],lineYs[i],linestyle='-',color=color)
    for i in range(numDashSegments):
        mpl.plot(dashXs[i],dashYs[i],linestyle='--',color=color)
    mpl.plot(allXs,allYs,marker='.',color=color,linestyle='')
    mpl.title("sequence: " + str(sequence))
    mpl.show()
    
    quit
