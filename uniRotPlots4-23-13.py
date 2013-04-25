from eosDriver import eosDriver, getTRollFunc, kentaDataTofLogRhoFit1, kentaDataTofLogRhoFit2
import matplotlib
import matplotlib.pyplot as plt
import numpy
from datasetManager import cstDataset, cstSequence, reduceTwoSeqPlots
from plotUtilsForPaper import latexField, fixExponentialAxes, removeExponentialNotationOnAxis
import plot_defaults
#basics
myfig = plt.figure(figsize=(10, 8))
myfig.subplots_adjust(left=0.124)
myfig.subplots_adjust(bottom=0.14)
myfig.subplots_adjust(top=0.967)
myfig.subplots_adjust(right=0.97)

sourceDb = '/home/jeff/work/rotNSruns/shedRuns4-24-13.db'

shenEosTableFilename = '/home/jeff/work/HShenEOS_rho220_temp180_ye65_version_1.1_20120817.h5'
ls220EosTableFilename = '/home/jeff/work/LS220_234r_136t_50y_analmu_20091212_SVNr26.h5'

eosName = 'LS220'
theEos = eosDriver(ls220EosTableFilename)
ye = 'BetaEq'
#yeForInversion = 0.1

xVar = 'edMax'
yVars = ['gravMass']
yFunc = lambda x: x

tovSlice = {'a': 0.0, 'rpoe': 1.0}
uniformMaxRotSlice = {'a': 0.0, 'rpoe': 'min'}
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
scriptsList = ['c40p0', 'c30p0', 'c20p0', 'c30p10', 'c30p5', 'cold']
cXXp0_params = [(40.0, 14.18, 0.5,), (30.0, 14.055, 0.375),  (20.0, 13.93, 0.25)]
tempFuncs = [getTRollFunc(params[0], 0.01, params[1], params[2]) for params in cXXp0_params]
tempFuncs.append(kentaDataTofLogRhoFit1())
tempFuncs.append(kentaDataTofLogRhoFit2())
tempFuncs.append(lambda x: 0.01)
tempFuncsDict = {scriptsList[i]: tempFuncs[i] for i in range(len(scriptsList))}


#############################################################
# First plot: Just Shen, frac diffs
#############################################################
filters = ('edMax>2e14', 'ToverW<0.25')
coldTovSet = cstDataset('cold', eosName, ye, sourceDb)
coldTovSeq = cstSequence(coldTovSet, tovSlice, filters)
theEos.resetCachedBetaEqYeVsRhobs(tempFuncsDict['cold'], 14.0, 16.0)
coldTovPlot = \
    coldTovSeq.getSeqPlot([xVar], yVars, filters, \
      xcolFunc=lambda x: theEos.rhobFromEnergyDensityWithTofRho(x, ye, tempFuncsDict['cold']),
      ycolFunc=yFunc)
plt.semilogx(*coldTovPlot, c=colors['cold'], ls='--',  label="TOV")
del coldTovSet
for script in colors.keys():
    thisSet = cstDataset(script, eosName, ye, sourceDb)
    thisSeq = cstSequence(thisSet, uniformMaxRotSlice, filters)

    theEos.resetCachedBetaEqYeVsRhobs(tempFuncsDict[script], 14.0, 16.0)

    thisPlot = thisSeq.getSeqPlot([xVar], yVars, filters, \
      xcolFunc=lambda x: theEos.rhobFromEnergyDensityWithTofRho(x, ye, tempFuncsDict[script]),
      ycolFunc=yFunc)

    plt.plot(*thisPlot, c=colors[script], marker=symbols[script],  label=script)
    
    #tovSet = cstDataset(script, eosName, ye, sourceDb)
    # tovSeq = cstSequence(thisSet, tovSlice, filters)
    # tovPlot = \
    #   tovSeq.getSeqPlot([xVar], yVars, filters, \
    #     xcolFunc=lambda x: theEos.rhobFromEnergyDensityWithTofRho(x, ye, tempFuncsDict[script]),
    #     ycolFunc=yFunc)
    # plt.plot(*tovPlot, c=colors[script], ls='--')

plt.xlabel(r"$\rho_{b,\mathrm{max}}$ [g/cm$^3$]")
#plt.axes().yaxis.set_minor_formatter(matplotlib.pyplot.FormatStrFormatter('%.0f'))
#plt.axes().yaxis.set_major_formatter(matplotlib.pyplot.FormatStrFormatter('%.0f'))
plt.ylabel("$M_b/M_\odot$", labelpad=5)
#removeExponentialNotationOnAxis('y')
plt.legend(loc=2)
plt.text(10 **15.1, 1.6, eosName, fontsize=26)
plt.show()