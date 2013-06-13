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
myfig.subplots_adjust(left=0.15)
myfig.subplots_adjust(bottom=0.14)
myfig.subplots_adjust(top=0.967)
myfig.subplots_adjust(right=0.96)

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
xLabel = r"$\rho_{\mathrm{b,max}}$ [$10^{15}$ g cm$^{-3}$]"
#xLabel = r"$E_\mathrm{max}$"
yLabel = "$M_\mathrm{g} \,[M_\odot]$"
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
mbLimit = 2.63
filters = ('edMax>2.0e14', 'baryMass<%s' % mbLimit)

aList = [0.0, 0.3, 0.6, 0.9, 1.1]
aList = [0.0, 1.1]
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
scriptsList = ['c40p0',  'cold']
cXXp0_params = [(40.0, 14.18, 0.5,)]  # , (30.0, 14.055, 0.375),  (20.0, 13.93, 0.25)]
tempFuncs = [getTRollFunc(params[0], 0.01, params[1], params[2]) for params in cXXp0_params]
#tempFuncs.append(kentaDataTofLogRhoFit1())
# tempFuncs.append(kentaDataTofLogRhoFit2())
tempFuncs.append(lambda x: 0.01)
tempFuncsDict = {scriptsList[i]: tempFuncs[i] for i in range(len(scriptsList))}
scriptsList = ['c40p0']

#############################################################
# First plot the curves
#############################################################
cacheMin = 14.0   # expected minimum log10(rhob) in runs
cacheMax = 15.6   # expected maximum log10(rhob) in runs
plotList = []

for script in scriptsList:
#    break
    #xFunc = lambda x: theEos.rhobFromEnergyDensityWithTofRho(x, ye, tempFuncsDict[script])
    #xFunc = lambda x: x
    if script == 'c30p10':
        thisSet = cstDataset(script, eosName, ye, '/home/jeff/work/rotNSruns/svdense30p10A.db')
    else:
        thisSet = cstDataset(script, eosName, ye, sourceDb)
    theEos.resetCachedBetaEqYeVsRhobs(tempFuncsDict[script], cacheMin, cacheMax)
    theEos.resetCachedRhobVsEds(tempFuncsDict[script], ye, cacheMin, cacheMax)
    xFunc = lambda x: theEos.rhobFromEdCached(x)/1.0e15

    for i, a in enumerate(aList):
        theMaxRotSlice.update({'a': a})

        thisSeq = cstSequence(thisSet, theMaxRotSlice, filters)

        thisPlot = thisSeq.getSeqPlot([xVar], yVars, filters,
                                      xcolFunc=xFunc,
                                      ycolFunc=yFunc)
        kwargs = {}
        if script == 'cold':
             kwargs = {'label': "$\\tilde{A}=%s$" % a}

        plert, = plt.plot(*thisPlot, c=colors[script],
                              dashes=dashList[i], lw=2.0*(2 + i)/3.0, **kwargs)
    plotList.append(plert)
    del thisSet
#############################################################
# Then plot the turning point annotations
#############################################################
plt.minorticks_on()

mb29tps = {'c40p0': {'1.1': [(1e-2, 1.05, 1.05,), (2.565, 2.565, 0)],
                     '0.0': [(1e-2, 1.260, 1.260), (2.560, 2.560, 0)]},
           'cold': {'1.1': [(1e-2, 1.055, 1.055,), (2.523, 2.523, 0)],
                    '0.0': [(1e-2, 1.28, 1.28), (2.518, 2.518, 0)]}}
if eosName == 'LS220':
    mb29tps = {'c40p0': {'1.1': [(1e-2, 1.8, 1.8,), (2.565, 2.565, 0)],
                     '0.0': [(1e-2, 1.260, 1.260), (2.560, 2.560, 0)]},
           'cold': {'1.1': [(1e-2, 1.8, 1.8,), (2.523, 2.523, 0)],
                    '0.0': [(1e-2, 1.28, 1.28), (2.518, 2.518, 0)]}}
plt.plot(*mb29tps['c40p0']['1.1'], c='b', lw=3)
plt.plot(*mb29tps['c40p0']['0.0'], c='b', lw=3)

plt.plot(*mb29tps['cold']['1.1'], c='b', lw=3, dashes=(20,5))
plt.plot(*mb29tps['cold']['0.0'], c='b', lw=3, dashes=(20,5))



#plt.ylim([1.1, 4.15])
locator = matplotlib.ticker.FixedLocator([0.5, 1.05, 1.30, 2.0])
plt.gca().xaxis.set_major_locator(locator)
plt.xlim([.5, 2.0])

plt.xlabel(xLabel, labelpad=6)
plt.ylabel(yLabel, labelpad=5)

limitString = "$\,\,\,M_\mathrm{b}<%s$" % mbLimit

if eosName == "HShenEOS":
    eosName = "HShen"
    plt.ylim([2.51, 2.655])
else:
    plt.ylim([2.24, 2.34])
    plt.xlim([1.0, 2.5])

plt.text(.75, 2.605, eosName, fontsize=26)

legend1 = plt.legend(loc=1, handlelength=3, labelspacing=0.2)
removeExponentialNotationOnAxis('x')
legend2 = plt.legend(plotList, scriptsList, loc=9, labelspacing=0.5)
plt.gca().add_artist(legend1)
plt.show()