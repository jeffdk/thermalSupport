
import sqlite3
import matplotlib
from numpy import *
from matplotlib import pyplot as mpl
from mpl_toolkits.mplot3d import Axes3D 
import math


# if data(partitionField) > partition value, plot with dashed
#TODO: Fix hard coding of this
from sqlUtils import queryDBGivenParams

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
    query += " WHERE eos=?  AND tprofile=? AND a=? AND T=? ORDER BY edMax"
    
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


    for i in range(numLineSegments):
        mpl.plot(lineXs[i],lineYs[i],linestyle='-',color=color)
    for i in range(numDashSegments):
        mpl.plot(dashXs[i],dashYs[i],linestyle='--',color=color)
    mpl.plot(allXs,allYs,marker='.',color=color,linestyle='')
    mpl.title("sequence: " + str(sequence))
    mpl.show()
    
    return


def sequencePlot(plotFields, sqliteCursor, filters=(), colorBy=None, tableName="models",
                 grid=True, title="", suppressShow=False, orderBy=None, forceColorbar=False,
                 **mplKwargs):
    """
    plotFields:        2-list, fields to plot
    sqliteCursor:      sqlite3.connection.cursor object for database
    filters:           list of strings for sqlite WHERE filters
    colorBy:           table field to color the points by
    tableName:         name of database table accessible from sqliteCursor
    mplKwargs:         keyword arguments passed on to matplotlib plotting function

    Note:  If colorBy is set, plots a scatter plot instead of regular plot!
           Remember to adjust mplKwargs accordingly in this case
    """
    getFields = plotFields[:]
    if colorBy:
        getFields.append(colorBy)
    if orderBy is None:
        orderBy = plotFields[0]
    points = queryDBGivenParams(getFields, [], sqliteCursor,
                                tableName, filters, " ORDER BY " + orderBy)

    #fig = mpl.figure()
    #axis = fig.add_subplot(111)
    mpl.title(title)
    mpl.grid(grid)
    if colorBy:
        mpl.scatter(*zip(*points)[:2], c=zip(*points)[-1], **mplKwargs)
    else:
        mpl.plot(*zip(*points)[:2], **mplKwargs)

    #axis.set_xlabel(getFields[0])
    #axis.set_ylabel(getFields[1])
    mpl.xlabel(getFields[0])
    mpl.ylabel(getFields[1])
    if colorBy and not suppressShow:
        colorLegend = mpl.colorbar()
        colorLegend.set_label(colorBy)
    if forceColorbar:
        colorLegend = mpl.colorbar()
        colorLegend.set_label(colorBy)
    print "Plotting %i entries" % len(points)
    if not suppressShow:
        mpl.show()


def nearValueFilter(field, value, tolerance=1e-3):
    """
    Generates a filter tuple for selecting entries with
    field = value +/-  value * tolerance
    """
    result = ()
    if value == 0.0:
        result = (field + "=0.0",)
    if value > 0.0:
        result = (field + ">%s" % (value - value * tolerance),
                  field + "<%s" % (value + value * tolerance))
    return result

def equalsFiltersFromDict(theDict, tolerance=1e-3):
    """
    From dictionary, return filters which match values given for
    use in sequencePlot.  Uses nearValueFilter to set floating point values
    """
    assert isinstance(theDict, dict)

    result = ()
    for key, value in theDict.iteritems():

        if value is None:
            result += (key + "='None'",)
        elif isinstance(value, str) or isinstance(value, unicode):
            result += (key + "='%s'" % value,)
        elif isinstance(value, int):
            result += (key + "=%s" % value,)
        elif isinstance( value, float):
            result += nearValueFilter(key, value, tolerance)
        else:
            print "Bad value type: ", type(value), value
            assert False, "There should only be None, str, int, or float in the database!"

    return result #+ ("rpoe<0.75", "rpoe>0.7")

