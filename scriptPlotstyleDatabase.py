import numpy
from sqlUtils import queryDBGivenParams
from matplotlib import pyplot as plt

class eosPrescription(object):
    prescriptionParameters = ('T', 'rollMid', 'rollScale', 'eosTmin',
                              'fixedTarget', 'fixedQuantity')
    paramsSet = False
    def __init__(self, name, symbol, linestyle, linecolor=None):
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
    nonesDict = dict([(key, None) for key in eosPrescription.prescriptionParameters])

    plateau10 = eosPrescription("Plateau 10 MeV", 'o', '-')
    plateau10.setParameters(nonesDict)
    database.append(plateau10)

    plateau5 = eosPrescription("Plateau 5 MeV", 'p', '--')
    plateau5dict = nonesDict.copy()
    plateau5dict['eosTmin'] = 5.0
    plateau5.setParameters(plateau5dict)
    database.append(plateau5)

    rolloff_m14_s05_T40 = eosPrescription("Rolloff mid=14 scale=.5  T=40", '^', ':')
    rolloff_m14_s05_T40dict = nonesDict.copy()
    rolloff_m14_s05_T40dict.update({'T': 40,
                                    'rollMid': 14.0,
                                    'rollScale': 0.5,
                                    'eosTmin': 0.01})
    rolloff_m14_s05_T40.setParameters(rolloff_m14_s05_T40dict)
    database.append(rolloff_m14_s05_T40)

    rolloff_m14_s05_T20 = eosPrescription("Rolloff mid=14 scale=.5  T=20", 's', '-.')
    rolloff_m14_s05_T20dict = nonesDict.copy()
    rolloff_m14_s05_T20dict.update({'T': 20,
                                    'rollMid': 14.0,
                                    'rollScale': 0.5,
                                    'eosTmin': 0.01})
    rolloff_m14_s05_T20.setParameters(rolloff_m14_s05_T20dict)
    database.append(rolloff_m14_s05_T20)

    cold = eosPrescription("Cold (T=0.5 MeV)", '*', None) #need fix none!
    coldDict = nonesDict.copy()
    coldDict.update({'T': 0.5,
                     'rollMid': 14.0,
                     'rollScale': 0.5,
                     'eosTmin': 0.01})
    cold.setParameters(coldDict)
    database.append(cold)


    #check every script in the database is set fully
    for script in database:
        assert isinstance(script, eosPrescription), \
            "Uhhh %s is not an eosPrescription object" % script
        assert script.paramsSet, \
            "Script parameters are not defined for script: %s" % script.name
    return database

def symbolFromDBentry(paramsDict):

    assert all([key in paramsDict for key in eosPrescription.prescriptionParameters]), \
        "Must specify all eosPrescription related parameters!"

    database = getScriptsDb()

    symbol = None

    for script in database:
        if paramsDict == script.paramsDict:
            print "Match for: ", script.name
            symbol = script.symbol

    assert symbol is not None, "Couldn't find entry matching paramsDict!"
    return symbol

def manyScriptSequencePlot(plotFields, sqliteCursor, filters=(), colorBy=None,
                           grid=True, title="", orderBy=None, forceColorbar=False,
                           **mplKwargs):
    """
    Version of sequence plot for plotting huge amount of data
    assumes tablename is models

    """
    filters = ("ye=0.15",)
    tableName = "models"
    if colorBy is None:
        colorBy = "arealR"
    getFields = plotFields[:]
    getFields.append(colorBy)
    if orderBy is None:
        orderBy = plotFields[0]

    for key in eosPrescription.prescriptionParameters:
        getFields.append(key)
    getFields.append('RedMax')

    points = queryDBGivenParams(getFields, [], sqliteCursor,
                                tableName, filters, " ORDER BY " + orderBy)
    for i, point in enumerate(points):
        prescriptDict = None

    points = zip(*points)
    points = numpy.array(points)
    print points[:, 3:]
    #fig = plt.figure()
    #axis = fig.add_subplot(111)
    plt.title(title)
    plt.grid(grid)
    if colorBy:
        plt.scatter(*points[:2], c=points[2], **mplKwargs)
    else:
        plt.plot(*points[:2], **mplKwargs)

    #axis.set_xlabel(getFields[0])
    #axis.set_ylabel(getFields[1])
    plt.xlabel(getFields[0])
    plt.ylabel(getFields[1])
    if colorBy:
        colorLegend = plt.colorbar()
        colorLegend.set_label(colorBy)
    if forceColorbar:
        colorLegend = plt.colorbar()
        colorLegend.set_label(colorBy)
    print "Plotting %i entries" % len(points)

    plt.show()