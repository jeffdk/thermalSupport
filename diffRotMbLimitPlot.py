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
myfig.subplots_adjust(left=0.14)
myfig.subplots_adjust(bottom=0.14)
myfig.subplots_adjust(top=0.967)
myfig.subplots_adjust(right=0.98)

sourceDb = '/home/jeff/work/rotNSruns/vdenseBetaEqOnlyMoreA.db'
sourceDb = '/home/jeff/work/rotNSruns/svdenseBetaEqNotDoneA.db'
tovSourceDb = '/home/jeff/work/rotNSruns/allRuns3-25-13.db'
shenEosTableFilename = '/home/jeff/work/HShenEOS_rho220_temp180_ye65_version_1.1_20120817.h5'
ls220EosTableFilename = '/home/jeff/work/LS220_234r_136t_50y_analmu_20091212_SVNr26.h5'

eosName = 'HShenEOS'
theEos = eosDriver(shenEosTableFilename)
ye = 'BetaEq'

xVar = 'edMax'
yVars = ['gravMass', 'J']
xLabel = r"$\rho_{b,\mathrm{max}}$ [g/cm$^3$]"
#xLabel = r"$E_\mathrm{max}$"
yLabel = "$M_g [M_\odot]$"
#yLabel = "T - W"
#yLabel = "$J/M^2$"
#yLabel = "$r_{p/e}$"
#yLabel = "$\Omega_c$"
yFunc = lambda x,y: x

a = 1.0

tovSlice = {'a': 0.0, 'rpoe': 1.0}
uniformMaxRotSlice = {'a': 0.0, 'rpoe': 'min'}
theMaxRotSlice = {'a': a, 'rpoe': 'min'}
mbLimit = 3.9
mbLimit = 2.9
filters = ('edMax>2.0e14', 'baryMass<%s' % mbLimit)

aList = [0.0, 0.3, 0.6, 0.9, 1.1]
#aList = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
dashList = ['_', ':', '-.', '--', '-', '--', '-.', ':', '_', ':', '-.']
dashList = [(None, None), (25, 4), (13, 5), (20, 4, 10, 6), (10, 3, 5, 5)]
dashList = dashList[::-1]
colors = {'c30p0': 'g',
          'c20p0': 'b',
          'c40p0': 'r',
          'cold': 'k',
          'c30p5': 'c',
          'c30p10': 'm'}

symbols = {'c30p0': 's',
           'c20p0': 'v',
           'c40p0': '^',
           'c30p5': 'p',
           'c30p10': 'H',
           'cold': '*'}
scriptsList = ['c40p0', 'c30p10', 'cold']
cXXp0_params = [(40.0, 14.18, 0.5,)]  # , (30.0, 14.055, 0.375),  (20.0, 13.93, 0.25)]
tempFuncs = [getTRollFunc(params[0], 0.01, params[1], params[2]) for params in cXXp0_params]
tempFuncs.append(kentaDataTofLogRhoFit1())
# tempFuncs.append(kentaDataTofLogRhoFit2())
tempFuncs.append(lambda x: 0.01)
tempFuncsDict = {scriptsList[i]: tempFuncs[i] for i in range(len(scriptsList))}


#############################################################
# First plot
#############################################################
cacheMin = 14.0   # expected minimum log10(rhob) in runs
cacheMax = 15.6   # expected maximum log10(rhob) in runs
plotList = []
# coldTovSet = cstDataset('cold', eosName, ye, sourceDb)
# coldTovSeq = cstSequence(coldTovSet, tovSlice, filters)
# #theEos.resetCachedBetaEqYeVsRhobs(tempFuncsDict['cold'], cacheMin, cacheMax)
# theEos.resetCachedRhobVsEds(tempFuncsDict['cold'], ye, cacheMin, cacheMax)
# xFunc = lambda x: theEos.rhobFromEnergyDensityWithTofRho(x, ye, tempFuncsDict['cold'])
# xFunc = lambda x: x
# coldTovPlot = \
#     coldTovSeq.getSeqPlot([xVar], yVars, filters, \
#       xcolFunc=xFunc,
#       ycolFunc=yFunc)
# plot = plt.semilogx(*coldTovPlot, c=colors['cold'], ls='--', dashes=plot_defaults.longDashes,
#                     label="TOV")
# del coldTovSet
for script in scriptsList:
    #xFunc = lambda x: theEos.rhobFromEnergyDensityWithTofRho(x, ye, tempFuncsDict[script])
    #xFunc = lambda x: x
    if script == 'c30p10':
        thisSet = cstDataset(script, eosName, ye, '/home/jeff/work/rotNSruns/svdense30p10A.db')
    else:
        thisSet = cstDataset(script, eosName, ye, sourceDb)
    theEos.resetCachedBetaEqYeVsRhobs(tempFuncsDict[script], cacheMin, cacheMax)
    theEos.resetCachedRhobVsEds(tempFuncsDict[script], ye, cacheMin, cacheMax)
    xFunc = lambda x: theEos.rhobFromEdCached(x)

    for i, a in enumerate(aList):
        theMaxRotSlice.update({'a': a})

        thisSeq = cstSequence(thisSet, theMaxRotSlice, filters)

        thisPlot = thisSeq.getSeqPlot([xVar], yVars, filters,
                                      xcolFunc=xFunc,
                                      ycolFunc=yFunc)
        kwargs = {}
        if script == 'cold':
             kwargs = {'label': "$\\tilde{A}=%s$" % a}

        plert, = plt.semilogx(*thisPlot, c=colors[script],
                              dashes=dashList[i], lw=2.0*(2 + i)/3.0, **kwargs)
    plotList.append(plert)
    del thisSet


plt.xlabel(xLabel)
#plt.axes().yaxis.set_minor_formatter(matplotlib.pyplot.FormatStrFormatter('%.0f'))
#plt.axes().yaxis.set_major_formatter(matplotlib.pyplot.FormatStrFormatter('%.0f'))
plt.ylabel(yLabel, labelpad=5)
#removeExponentialNotationOnAxis('y')
if eosName == "HShenEOS":
    eosName = "HShen,   $\,\,M_\mathrm{b}<%s$" % mbLimit
plt.text(0.7e15, 2.62, eosName, fontsize=26)
#plt.title("a=%s  and $T/|W|<0.25$" % a)
legend1 = plt.legend(loc=1, handlelength=3, labelspacing=0.2)

legend2 = plt.legend(plotList, scriptsList, loc=9, labelspacing=0.5)
plt.gca().add_artist(legend1)
plt.show()