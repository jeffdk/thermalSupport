import numpy
import operator
from plotUtilsForPaper import latexField
from sqlUtils import queryDBGivenParams
from matplotlib import pyplot as plt


class tempPrescription(object):
    prescriptionParameters = ('T', 'rollMid', 'rollScale', 'eosTmin',
                              'fixedTarget', 'fixedQuantity')
    paramsSet = False
    def __init__(self, name, symbol, linestyle=None, linecolor=None):
        """
        Params dict are the values corresponding to this eosPrescription
        """
        assert isinstance(name, str)
        self.name = name
        self.symbol = symbol
        self.linestyle = linestyle
        self.linecolor = linecolor

    def setParameters(self, paramsDict):
        assert all([key in paramsDict for key in self.prescriptionParameters]), \
            "Must specify all eosPrescription related parameters!"
        self.paramsDict = paramsDict
        self.paramsSet = True

def getScriptsDb():
    """
    Function which defines all the possible eosPrescription databases
    Database is a list of eosPrescription objects
    """
    database = []
    nonesDict = dict([(key, str(None)) for key in tempPrescription.prescriptionParameters])

    plateau10 = tempPrescription("c30p10", 'h')
    plateau10.setParameters(nonesDict)
    database.append(plateau10)

    plateau5 = tempPrescription("c30p5", 'p')
    plateau5dict = nonesDict.copy()
    plateau5dict['eosTmin'] = 5.0
    plateau5.setParameters(plateau5dict)
    database.append(plateau5)

    c40p0 = tempPrescription(r"c40p0", '^')
    c40p0dict = nonesDict.copy()
    c40p0dict.update({'T': 40.,
                      'rollMid': 14.18,
                      'rollScale': 0.5,
                      'eosTmin': 0.01})
    c40p0.setParameters(c40p0dict)
    database.append(c40p0)

    c30p0 = tempPrescription(r"c30p0", 's')
    c30p0dict = nonesDict.copy()
    c30p0dict.update({'T': 30.,
                      'rollMid': 14.055,
                      'rollScale': 0.375,
                      'eosTmin': 0.01})
    c30p0.setParameters(c30p0dict)
    database.append(c30p0)

    c20p0 = tempPrescription(r"c20p0", 'v')
    c20p0dict = nonesDict.copy()
    c20p0dict.update({'T': 20.,
                      'rollMid': 13.93,
                      'rollScale': 0.25,
                      'eosTmin': 0.01})
    c20p0.setParameters(c20p0dict)
    database.append(c20p0)

    cold = tempPrescription("cold", '*')
    coldDict = nonesDict.copy()
    coldDict.update({'T': 0.01,
                     'rollMid': 14.0,
                     'rollScale': 0.5,
                     'eosTmin': 0.01})
    cold.setParameters(coldDict)
    database.append(cold)


    rolloff_m14_s05_T40 = tempPrescription(r"$\mathrm{Roll}^{\mathrm{mid}=14}_{\mathrm{scale}=.5}$ T=40", '^', ':')
    rolloff_m14_s05_T40dict = nonesDict.copy()
    rolloff_m14_s05_T40dict.update({'T': 40.,
                                    'rollMid': 14.0,
                                    'rollScale': 0.5,
                                    'eosTmin': 0.01})
    rolloff_m14_s05_T40.setParameters(rolloff_m14_s05_T40dict)
    database.append(rolloff_m14_s05_T40)

    rolloff_m14_s05_T20 = tempPrescription("$\mathrm{Roll}^{\mathrm{mid}=14}_{\mathrm{scale}=.5}$  T=20", 'v', '-.')
    rolloff_m14_s05_T20dict = nonesDict.copy()
    rolloff_m14_s05_T20dict.update({'T': 20.,
                                    'rollMid': 14.0,
                                    'rollScale': 0.5,
                                    'eosTmin': 0.01})
    rolloff_m14_s05_T20.setParameters(rolloff_m14_s05_T20dict)
    database.append(rolloff_m14_s05_T20)

    rolloff_m135_s05_T20 = tempPrescription("Roll mid=13.5 scale=.5  T=20", '1', '-.')
    rolloff_m135_s05_T20dict = nonesDict.copy()
    rolloff_m135_s05_T20dict.update({'T': 20.,
                                    'rollMid': 13.5,
                                    'rollScale': 0.5,
                                    'eosTmin': 0.01})
    rolloff_m135_s05_T20.setParameters(rolloff_m135_s05_T20dict)
    database.append(rolloff_m135_s05_T20)

    rolloff_m135_s05_T40 = tempPrescription("Roll mid=13.5 scale=.5  T=40", '2', '-.')
    rolloff_m135_s05_T40dict = nonesDict.copy()
    rolloff_m135_s05_T40dict.update({'T': 40.,
                                    'rollMid': 13.5,
                                    'rollScale': 0.5,
                                    'eosTmin': 0.01})
    rolloff_m135_s05_T40.setParameters(rolloff_m135_s05_T40dict)
    database.append(rolloff_m135_s05_T40)

    rolloff_m14_s025_T40 = tempPrescription("Roll mid=14 scale=.25  T=40", '3', ':')
    rolloff_m14_s025_T40dict = nonesDict.copy()
    rolloff_m14_s025_T40dict.update({'T': 40.,
                                    'rollMid': 14.0,
                                    'rollScale': 0.25,
                                    'eosTmin': 0.01})
    rolloff_m14_s025_T40.setParameters(rolloff_m14_s025_T40dict)
    database.append(rolloff_m14_s025_T40)

    rolloff_m14_s025_T20 = tempPrescription("Roll mid=14 scale=.25  T=20", '4', '-.')
    rolloff_m14_s025_T20dict = nonesDict.copy()
    rolloff_m14_s025_T20dict.update({'T': 20.,
                                    'rollMid': 14.0,
                                    'rollScale': 0.25,
                                    'eosTmin': 0.01})
    rolloff_m14_s025_T20.setParameters(rolloff_m14_s025_T20dict)
    database.append(rolloff_m14_s025_T20)


    entropyS05 = tempPrescription("Fixed Entropy S = 0.5", "_", '-')
    entropyS05dict = nonesDict.copy()
    entropyS05dict.update({'fixedQuantity': 'entropy',
                           'fixedTarget': 0.5})
    entropyS05.setParameters(entropyS05dict)
    database.append(entropyS05)

    entropyS1 = tempPrescription("Fixed Entropy S = 1.0", "|", '-')
    entropyS1dict = nonesDict.copy()
    entropyS1dict.update({'fixedQuantity': 'entropy',
                          'fixedTarget': 1.0})
    entropyS1.setParameters(entropyS1dict)
    database.append(entropyS1)

    entropyS2 = tempPrescription("Fixed Entropy S = 2.0", "d", '-')
    entropyS2dict = nonesDict.copy()
    entropyS2dict.update({'fixedQuantity': 'entropy',
                          'fixedTarget': 2.0})
    entropyS2.setParameters(entropyS2dict)
    database.append(entropyS2)

    entropyS3 = tempPrescription("Fixed Entropy S = 3.0", "D", '-')
    entropyS3dict = nonesDict.copy()
    entropyS3dict.update({'fixedQuantity': 'entropy',
                          'fixedTarget': 3.0})
    entropyS3.setParameters(entropyS3dict)
    database.append(entropyS3)


    #check every script in the database is set fully
    for script in database:
        assert isinstance(script, tempPrescription), \
            "Uhhh %s is not an eosPrescription object" % script
        assert script.paramsSet, \
            "Script parameters are not defined for script: %s" % script.name
    return database


def scriptFromScriptName(name):
    assert isinstance(name, str)
    database = getScriptsDb()

    answer = None
    for script in database:
        if name == script.name:
            answer = script
    assert answer is not None, "Couldn't find entry matching name: %s" % name
    return answer


def symbolFromDBentry(paramsDict):

    assert all([key in paramsDict for key in tempPrescription.prescriptionParameters]), \
        "Must specify all eosPrescription related parameters!"

    database = getScriptsDb()

    symbol = None
    name = None

    for script in database:
        #print paramsDict
        #print script.paramsDict
        if paramsDict == script.paramsDict:
            #print "Match for: ", script.name
            symbol = script.symbol
            name = script.name
    assert symbol is not None, "Couldn't find entry matching paramsDict!"
    return symbol, name

def getLinestyle(eos, ye):
    """
    Defines database for what linestyle to plot with
    """
    if eos == 'HShenEOS' and ye == .1:
        return '-'
    if eos == 'HShenEOS' and ye == 'BetaEq':
        return '--'
    if eos == 'LS220' and ye == .1:
        return ':'
    if eos == 'LS220' and ye == 'BetaEq':
        return '-.'
    assert False, "Ye and EOS combination not found in getLinestyle"


def manyScriptSequencePlot(plotFields, sqliteCursor, filters=(), colorBy=None, maxPlot=None,
                           grid=False, title="", orderBy=None, forceColorbar=False,
                           suppressShow=False, legendList=[], vmax=None, vmin=None,
                           loc=0, minRpoeOnly=False,
                           **mplKwargs):
    """
    Version of sequence plot for plotting huge amount of data
    assumes tablename is models
    if maxPlot plots maximum value of quantity for sequence only
    """
    orderBy = plotFields[0] + ',' + ','.join(tempPrescription.prescriptionParameters) + ",eos,ye,edMax"
    #orderBy = 'rpoe'+','+ ','.join(eosPrescription.prescriptionParameters) + ",eos,ye,edMax"
#print orderBy
    size = 40
    plotLines = False
    #filters = ("ye=0.15",)
    filters += ("arealR < 100",)
    tableName = "models"
    if colorBy is None:
        colorBy = "arealR"
    getFields = plotFields[:]  # x-points 0, y-points 1
    getFields.append(colorBy)  # colorBy 2
    if orderBy is None:
        orderBy = plotFields[0]

    for key in tempPrescription.prescriptionParameters:
        getFields.append(key)   # script parameters 3-8
    getFields.append('RedMax')  # RedMax 9
    getFields.append('ye')      # ye 10
    getFields.append('eos')     # eos 11
    if maxPlot is not None:
        getFields.append(maxPlot)  # maxPlot 12
    if minRpoeOnly:
        getFields.append('runID')    # runIDcol
        runIDcol = len(getFields) - 1
        getFields.append('lineNum')  # lineNumcol
        lineNumcol = len(getFields) - 1
        orderBy = 'runID,lineNum,' + orderBy

    points = queryDBGivenParams(getFields, [], sqliteCursor,
                                tableName, filters, " ORDER BY " + orderBy)
    assert points, "No points returned for query with filters: %s" % str(filters)
    currentSymbol = ""
    previousSymbol = ""
    previousName = ""
    currentName = ""
    currentPoints = []
    currentToroidPoints = []
    currentEos = None
    currentYe = None
    previousEos = None
    previousYe = None
    previousPoint = None
    if vmax is None:
        vmax = max([point[2] for point in points])
    if vmin is None:
        vmin = min([point[2] for point in points])

    #print vmin, vmax
    for i, point in enumerate(points):
        #print point
        currentYe = point[10]
        currentEos = point[11]
        prescriptDict = dict()
        #print currentSymbol, previousSymbol
        for j, scriptParam in enumerate(point[3:3 + 6 ]):
            prescriptDict[tempPrescription.prescriptionParameters[j]] = scriptParam
        #print prescriptDict
        currentSymbol, currentName = symbolFromDBentry(prescriptDict)
        ax = plt.gca()
        handles, labels = ax.get_legend_handles_labels()
        #print currentName, labels
        if currentName in labels:
            currentName = None
            previousName = None
        if currentSymbol == previousSymbol and currentEos == previousEos and currentYe == previousYe:
            currentPoints.append(point)
            if point[9] > 0.0:
                #print "TOROIZZLE"
                currentToroidPoints.append(point)
        elif not previousSymbol == "" and not currentPoints == []:
            if minRpoeOnly:
                currentPoints = reduceToMinRpoeOnly(currentPoints, runIDcol, lineNumcol)
            if maxPlot is not None:
                currentPoints = [getPointWithMaxOfCol(currentPoints, 12)]
                if currentPoints[0][9] == 0.0:
                    #print "antigotcha "
                    currentToroidPoints = []
                else:
                    currentToroidPoints = [getPointWithMaxOfCol(currentToroidPoints, 12)]
            currentPoints = zip(*currentPoints)
            print currentPoints
            plt.scatter(*currentPoints[:2], c=currentPoints[2], marker=previousSymbol, label=previousName,
                        vmax=vmax, vmin=vmin, s=size, **mplKwargs)
            if plotLines:
                plt.plot(*currentPoints[:2], ls=getLinestyle(previousEos, previousYe), c='k', lw=.5)
            currentPoints = []
            #legendList.append(currentName)
            if not currentToroidPoints == []:
                currentToroidPoints = zip(*currentToroidPoints)
                #below line sets circle color to black
                currentToroidPoints[2] = [(0., 0., 0.) for _ in currentToroidPoints[2]]
                plt.scatter(*currentToroidPoints[:2], c=currentToroidPoints[2],
                            marker='o', facecolor='none', s=size * 2,
                            vmax=vmax, vmin=vmin, **mplKwargs)
                currentToroidPoints = []
        previousSymbol = currentSymbol
        previousEos = currentEos
        previousYe = currentYe
        previousName = currentName
        previousPoint = point
        #symbolList.append(symbolFromDBentry(prescriptDict))
    print "Done with loop"
    #Don't forget to plot the last set!
    #print getPointWithMaxOfCol(currentPoints, 12)
    if minRpoeOnly:
        currentPoints = reduceToMinRpoeOnly(currentPoints, runIDcol, lineNumcol)
    if maxPlot is not None:
        currentPoints = [getPointWithMaxOfCol(currentPoints, 12)]
        if currentPoints[0][9] == 0.0:
            currentToroidPoints = []
    currentPoints = zip(*currentPoints)
    plt.scatter(*currentPoints[:2], c=currentPoints[2], marker=previousSymbol, label=previousName,
                vmax=vmax, vmin=vmin, s=size, **mplKwargs)
    if plotLines:
        plt.plot(*currentPoints[:2], ls=getLinestyle(previousEos, previousYe), c='k', lw=.5)
    #legendList.append(currentName)
    #Set colorbar before doing toroidal points because toroidal points have black coloring
    if colorBy and not suppressShow:
        colorLegend = plt.colorbar()
        colorLegend.set_label(latexField(colorBy))
    if forceColorbar:
        colorLegend = plt.colorbar()
        colorLegend.set_label(latexField(colorBy))
    if not currentToroidPoints == []:
        if maxPlot is not None:
            currentToroidPoints = [getPointWithMaxOfCol(currentToroidPoints, 12)]
        currentToroidPoints = zip(*currentToroidPoints)
        #print "dur", currentToroidPoints
        #below line sets circle color to black
        currentToroidPoints[2] = [(0., 0., 0.) for _ in currentToroidPoints[2]]
        plt.scatter(*currentToroidPoints[:2], c=currentToroidPoints[2],
                    marker='o', facecolor='none', s=size * 2,
                    vmax=vmax, vmin=vmin, **mplKwargs)


    plt.title(title)
    plt.grid(grid)

    #axis.set_xlabel(getFields[0])
    #axis.set_ylabel(getFields[1])
    plt.xlabel(latexField(getFields[0]))
    plt.ylabel(latexField(getFields[1]))
    print "Plotting %i entries" % len(points)

    if not suppressShow:
        #ax = plt.gca()
        #handles, labels = ax.get_legend_handles_labels()
        plt.legend(loc=loc)
        plt.show()
        legendList = []

def getPointWithMaxOfCol(array, col):
    assert len(array), "Empty array passed!"
    assert len(array[0]) > col, "Points don't have %s entries in array!"  % col

    max = -1e300
    answerPoint = None
    for point in array:
        #print point
        if point[col] > max:
            max = point[col]
            answerPoint = point
    #print "DURANSER"
    #print answerPoint
    assert answerPoint is not None, "Answer is None... something is wrong"
    return answerPoint

def reduceToMinRpoeOnly(array, runIDcol, lineNumcol):
    """
    Effectively reduce the result to mass-shed sequence with low resolution
    Since
    """

    assert len(array), "Empty array passed!"
    assert len(array[0]) > lineNumcol, "Points don't have %s entries in array!" % lineNumcol

    result = []
    maxlineNum = -1
    thisRunIDanswer = []
    previousRunID = array[0][runIDcol]
    previousPoint = []

    for point in array:
        if point[runIDcol] == previousRunID:
            if point[lineNumcol] > maxlineNum:
                maxlineNum = point[lineNumcol]
                thisRunIDanswer = point
            else:
                print "WARNIGN SHOULD NEVER BE HERE!"
        else:
            maxlineNum = -1
            result.append(thisRunIDanswer)
            #thisRunIDanswer = []
        previousRunID = point[runIDcol]
        previousPoint = point
    result.append(thisRunIDanswer)
    #print result
    return result
