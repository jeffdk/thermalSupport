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

sourceDb = '/home/jeff/work/rotNSruns/allRuns3-25-13.db'
#sourceDb = '/home/jeff/work/rotNSruns/vdenseBetaEqOnlyMoreC.db'
shedDb = '/home/jeff/work/rotNSruns/shedRuns4-24-13.db'
shenEosTableFilename = '/home/jeff/work/HShenEOS_rho220_temp180_ye65_version_1.1_20120817.h5'
ls220EosTableFilename = '/home/jeff/work/LS220_234r_136t_50y_analmu_20091212_SVNr26.h5'

eosName = 'LS220'
#eosName = 'LS220'
#theEos = eosDriver(ls220EosTableFilename)
ye = 'BetaEq'

xVar = 'omega_c'
yVar = 'baryMass'


tovSlice = {'a': 0.0, 'rpoe': 1.0}
uniformMaxRotSlice = {'a': 0.0, 'rpoe': 'min'}
ls220Slice = {'edMax': 2.0333333333e+15, 'a': 0.0}
shenSlice = {'edMax': 1.3641025641e+15, 'a': 0.0}
theSlice = shenSlice
#  theSlice = ls220Slice
filters = ()
#shenSlice = {'edMax': 1.0003737283e+15, 'a': 0.0}
#ls220Slice = {'edMax': 1.2153846153e+15, 'a': 0.0}

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

lineWidths = {'c30p0': 2,
              'c20p0': 2,
              'c40p0': 2,
              'c30p5': 3,
              'c30p10': 4,
              'cold': 2}

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
filters = ('edMax>2e14',)
#coldTovSet = cstDataset('cold', eosName, ye, sourceDb)
#coldTovSeq = cstSequence(coldTovSet, theSlice, filters)
#coldTovPlot = \
#    coldTovSeq.getSeqPlot([xVar], [yVar], filters)
#plt.semilogx(*coldTovPlot, c=colors['cold'], ls='--',  label="TOV")
#del coldTovSet
for script in colors.keys():
    thisSet = cstDataset(script, eosName, ye, sourceDb)
    thisSet.addEntriesFromDb(shedDb)
    thisSeq = cstSequence(thisSet, theSlice, filters)

    mgPlot = thisSeq.getSeqPlot([xVar], ['gravMass'], filters, xcolFunc=lambda x: x/1000.0)
    mbPlot = thisSeq.getSeqPlot([xVar], ['baryMass'], filters, xcolFunc=lambda x: x/1000.0)
    labelKwarg = {'label': script}
    plt.plot(*mgPlot, c=colors[script],  ms=8, lw=lineWidths[script],
             markeredgecolor=colors[script])
    plt.plot(*mbPlot, c=colors[script],  ms=8, lw=lineWidths[script],
             markeredgecolor=colors[script], dashes=(20, 5))
    del thisSet
    thisSet = cstDataset(script, eosName, ye, shedDb)
    thisSeq = cstSequence(thisSet, theSlice, filters)

    mgPlot = thisSeq.getSeqPlot([xVar], ['gravMass'], filters, xcolFunc=lambda x: x/1000.0)
    mbPlot = thisSeq.getSeqPlot([xVar], ['baryMass'], filters, xcolFunc=lambda x: x/1000.0)
    plt.plot(*mgPlot, c=colors[script], marker=symbols[script], ms=10, lw=lineWidths[script],
             **labelKwarg)
    plt.plot(*mbPlot, c=colors[script], marker=symbols[script], ms=10, lw=lineWidths[script],
             dashes=(20, 5))
    del thisSet

plt.xlabel(r"$\Omega_c$ [$10^3$ rad s$^{-1}$]", labelpad=10)
#plt.axes().yaxis.set_minor_formatter(matplotlib.pyplot.FormatStrFormatter('%.0f'))
#plt.axes().yaxis.set_major_formatter(matplotlib.pyplot.FormatStrFormatter('%.0f'))
plt.ylabel("$M_\mathrm{b,g} \,\, [M_\odot]$", labelpad=5)
#removeExponentialNotationOnAxis('y')
plt.legend(loc=2)
plt.minorticks_on()
if eosName == "HShenEOS":
    eosName = "HShen"

textPos = (0.4, 0.8)
plt.annotate(eosName, textPos, xytext=textPos, xycoords='axes fraction', textcoords='axes fraction',
             fontsize=26)
plt.xlim(2, 9)
plt.show()