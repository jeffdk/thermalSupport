from eosDriver import eosDriver, getTRollFunc, kentaDataTofLogRhoFit1, kentaDataTofLogRhoFit2
import matplotlib
import matplotlib.pyplot as plt
import numpy
from datasetManager import cstDataset, cstSequence, reduceTwoSeqPlots
from maxMassOrigFiles.sqlPlotRoutines import equalsFiltersFromDict
from plotUtilsForPaper import latexField, fixExponentialAxes, removeExponentialNotationOnAxis
import plot_defaults
#basics
myfig = plt.figure(figsize=(10, 8))
myfig.subplots_adjust(left=0.124)
myfig.subplots_adjust(bottom=0.14)
myfig.subplots_adjust(top=0.967)
myfig.subplots_adjust(right=0.97)

sourceDb = '/home/jeff/work/rotNSruns/vdenseBetaEqOnly.db'
tovSourceDb = '/home/jeff/work/rotNSruns/allRuns3-25-13.db'
shenEosTableFilename = '/home/jeff/work/HShenEOS_rho220_temp180_ye65_version_1.1_20120817.h5'
ls220EosTableFilename = '/home/jeff/work/LS220_234r_136t_50y_analmu_20091212_SVNr26.h5'

eosName = 'LS220'
theEos = eosDriver(ls220EosTableFilename)
ye = 'BetaEq'
#yeForInversion = 0.1

xVar = 'edMax'
yVars = ['gravMass']
xLabel = r"$\rho_{b,\mathrm{max}}$ [g/cm$^3$]"
xLabel = r"$E_\mathrm{max}$"
yLabel = "$M_g/M_\odot$"
#yLabel = "$J/M^2$"
yFunc = lambda x: x

a = 1.0

tovSlice = {'a': 0.0, 'rpoe': 1.0}
uniformMaxRotSlice = {'a': 0.0, 'rpoe': 'min'}
theMaxRotSlice = {'a': a, 'rpoe': 'min'}
filters = ()


colors = {'c30p0': 'g',
          'c20p0': 'b',
          'c40p0': 'r',
          'cold': 'm',
          'c30p5': 'c',
          'c30p10': 'k'}

symbols = {'c30p0': 's',
           'c20p0': 'v',
           'c40p0': '^',
           'c30p5': 'p',
           'c30p10': 'H',
           'cold': '*'}
scriptsList = ['c40p0', 'c30p0', 'c20p0', 'cold']
cXXp0_params = [(40.0, 14.18, 0.5,), (30.0, 14.055, 0.375),  (20.0, 13.93, 0.25)]
tempFuncs = [getTRollFunc(params[0], 0.01, params[1], params[2]) for params in cXXp0_params]
tempFuncs.append(kentaDataTofLogRhoFit1())
tempFuncs.append(kentaDataTofLogRhoFit2())
tempFuncs.append(lambda x: 0.01)
tempFuncsDict = {scriptsList[i]: tempFuncs[i] for i in range(len(scriptsList))}


#############################################################
# First plot
#############################################################
filters = ('edMax>2.0e14', 'ToverW<0.25', 'baryMass<2.6')
plotList = []
# coldTovSet = cstDataset('cold', eosName, ye, sourceDb)
# coldTovSeq = cstSequence(coldTovSet, tovSlice, filters)
# theEos.resetCachedBetaEqYeVsRhobs(tempFuncsDict['cold'], 13.5, 16.0)
# coldTovPlot = \
#     coldTovSeq.getSeqPlot([xVar], yVars, filters, \
#       xcolFunc=lambda x: theEos.rhobFromEnergyDensityWithTofRho(x, ye, tempFuncsDict['cold']),
#       ycolFunc=yFunc)
# plot = plt.semilogx(*coldTovPlot, c=colors['cold'], ls='-.',  label="TOV")
# del coldTovSet
for script in scriptsList:
    xFunc = lambda x: theEos.rhobFromEnergyDensityWithTofRho(x, ye, tempFuncsDict[script])
    xFunc = lambda x: x
    thisSet = cstDataset(script, eosName, ye, sourceDb)
    thisSeq = cstSequence(thisSet, theMaxRotSlice, filters)
    #cursor = thisSeq.dbConn.cursor()
    #cursor.execute("SELECT rpoe FROM models")
    #print cursor.fetchall()
    eds = []
    plotVars = []
    for rpoe in numpy.arange(0.64, 1.0, 0.04):
        ed = thisSet.getSecInstabilitySeq(a, rpoe, 1e15, 3e15)
        setCursor = thisSet.dbConn.cursor()
        ptDict = {'a': a, 'rpoe': rpoe, 'edMax': ed}
        pointFilters = equalsFiltersFromDict(ptDict)
        query = "WHERE " + " AND ".join(pointFilters)
        setCursor.execute("SELECT " + ','.join(yVars) + " FROM models " + query)
        answer = yFunc(*setCursor.fetchall()[0])
        eds.append(xFunc(ed))
        plotVars.append(answer)
    plt.scatter(eds, plotVars, marker=symbols[script], c=colors[script], s=50)
    theEos.resetCachedBetaEqYeVsRhobs(tempFuncsDict[script], 13.5, 16.0)

    thisPlot = thisSeq.getSeqPlot([xVar], yVars, filters, \
      xcolFunc=xFunc,
      ycolFunc=yFunc)
    plt.plot(*thisPlot, c=colors[script],  label=script)
    plotList.append([thisPlot, colors[script], '-'])
    del thisSet

    tovSet = cstDataset(script, eosName, ye, sourceDb)
    tovSeq = cstSequence(tovSet, uniformMaxRotSlice, filters)
    tovPlot = \
    tovSeq.getSeqPlot([xVar], yVars, filters, \
    xcolFunc=xFunc,
    ycolFunc=yFunc)
    plt.semilogx(*tovPlot, c=colors[script], ls='--')
    plotList.append([tovPlot, colors[script], '--'])
    del tovSet

plt.xlabel(xLabel)
#plt.axes().yaxis.set_minor_formatter(matplotlib.pyplot.FormatStrFormatter('%.0f'))
#plt.axes().yaxis.set_major_formatter(matplotlib.pyplot.FormatStrFormatter('%.0f'))
plt.ylabel(yLabel, labelpad=5)
#removeExponentialNotationOnAxis('y')
plt.text(10 **15, 1.6, eosName, fontsize=26)
plt.title("a=%s  and $T/|W|<0.25$" % a)
plt.legend(loc=4)

plt.show()