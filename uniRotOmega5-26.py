from consts import CGS_C
from eosDriver import eosDriver, getTRollFunc, kentaDataTofLogRhoFit1, kentaDataTofLogRhoFit2
import matplotlib
from matplotlib import rcParams
import matplotlib.pyplot as plt
import numpy
from datasetManager import cstDataset, cstSequence, reduceTwoSeqPlots
from maxMassOrigFiles.sqlPlotRoutines import nearValueFilter
from plotUtilsForPaper import latexField, fixExponentialAxes, removeExponentialNotationOnAxis, fixScientificNotation
import plot_defaults
#basics


sourceDb = '/home/jeff/work/rotNSruns/allRuns3-25-13.db'
#sourceDb = '/home/jeff/work/rotNSruns/vdenseBetaEqOnlyMoreC.db'
sourceDb = '/home/jeff/work/rotNSruns/omegaRuns5-21A.db'
shedDb = '/home/jeff/work/rotNSruns/shedRuns4-24-13.db'
shenEosTableFilename = '/home/jeff/work/HShenEOS_rho220_temp180_ye65_version_1.1_20120817.h5'
ls220EosTableFilename = '/home/jeff/work/LS220_234r_136t_50y_analmu_20091212_SVNr26.h5'
rcParams['figure.subplot.left'] = 0.135
rcParams['figure.subplot.right'] = 0.88
rcParams['figure.subplot.bottom'] = 0.13
rcParams['figure.subplot.top'] = 0.98

eosName = 'HShenEOS'
#eosName = 'LS220'

ye = 'BetaEq'

xVar = 'omega_c'
yVar = 'baryMass'

a = 0.0
rhobShen = 1.15789947555e+15
rhobLS220 = 1.76316840586e+15
#rhobLS220 = 1.02632152932e+15
#rhobLS220 = 7.10528763335e+14
tovSlice = {'a': a, 'rpoe': 1.0}
uniformMaxRotSlice = {'a': a, 'rpoe': 'min'}
ls220Slice = {'edMax': 2.0333333333e+15, 'a': a}
shenSlice = {'edMax': 1.3641025641e+15, 'a': a}
theSlice = shenSlice
theSlice = ls220Slice
filters = ()
toroidSymbols = False  # if false, plot one symbol at end of sequence

if eosName == 'LS220':
    rhob = rhobLS220
    theEos = eosDriver(ls220EosTableFilename)
else:
    rhob = rhobShen
    theEos = eosDriver(shenEosTableFilename)

edFunc = lambda x, q: numpy.power(10.0, x) \
        * (1.0 + (numpy.power(10.0, q) - theEos.energy_shift) / CGS_C**2)
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

mgShift = 0.0
mgYfunc = lambda x: x + mgShift
#############################################################
# First plot: Just Shen, frac diffs
#############################################################
markerSize = 6
edgeColor = 'k'
fig = plt.figure()
ax_mb = fig.add_subplot(111)
ax_mg = ax_mb.twinx()
for script in colors.keys():

    thisSet = cstDataset(script, eosName, ye, sourceDb)

    temp = tempFuncsDict[script](numpy.log10(rhob))
    theEos.setBetaEqState({'rho': rhob, 'temp': temp})
    ed = edFunc(numpy.log10(rhob), theEos.query('logenergy'))
    theSlice = {'edMax': ed, 'a': a}

    print script, theEos.rhobFromEnergyDensityWithTofRho(1.4818029819e+15, ye, tempFuncsDict[script])

    thisSeq = cstSequence(thisSet, theSlice, filters)

    mgPlot = thisSeq.getSeqPlot([xVar], ['gravMass'], filters, xcolFunc=lambda x: x/1000.0,
                                ycolFunc=mgYfunc)
    mbPlot = thisSeq.getSeqPlot([xVar], ['baryMass'], filters, xcolFunc=lambda x: x/1000.0)
    labelKwarg = {'label': script}
    ax_mg.plot(*mgPlot, c=colors[script],  ms=8, lw=lineWidths[script],
             markeredgecolor=colors[script])
    ax_mb.plot(*mbPlot, c=colors[script],  ms=8, lw=lineWidths[script],
             markeredgecolor=colors[script], dashes=(20, 5))
    del thisSet
    thisSet = cstDataset(script, eosName, ye, sourceDb)
    
    if toroidSymbols:
        filters = ('RedMax>0.0',)
        markerSize = 6
        edgeColor = colors[script]
    else: 
        filters = nearValueFilter('edMax', ed)
        print filters
        theSlice = {'a': a, 'rpoe': 'min'}
        markerSize = 8
        edgeColor = 'k'
    thisSeq = cstSequence(thisSet, theSlice, filters)
    mbToroid = thisSeq.getSeqPlot([xVar], ['baryMass'], filters, xcolFunc=lambda x: x/1000.0)
    mgToroid = thisSeq.getSeqPlot([xVar], ['gravMass'], filters, xcolFunc=lambda x: x/1000.0,
                                  ycolFunc=mgYfunc)
    #print mbToroid
    ax_mg.plot(*mgToroid, c=colors[script], marker=symbols[script], ms=markerSize,
             lw=lineWidths[script], markeredgecolor=edgeColor, zorder=4,
             **labelKwarg)
    ax_mb.plot(*mbToroid, c=colors[script], marker=symbols[script], ms=markerSize+1,
             lw=lineWidths[script], dashes=(20, 5), markeredgecolor=edgeColor, zorder=4)
    filters = ()
    del thisSet

ax_mb.set_xlabel(r"$\Omega_c$ [$10^3$ rad s$^{-1}$]", labelpad=10)
#plt.axes().yaxis.set_minor_formatter(matplotlib.pyplot.FormatStrFormatter('%.0f'))
#plt.axes().yaxis.set_major_formatter(matplotlib.pyplot.FormatStrFormatter('%.0f'))
ax_mg.set_ylabel("$M_\mathrm{g} \,\, [M_\odot]$", labelpad=5)
ax_mb.set_ylabel("$M_\mathrm{b} \,\, [M_\odot]$", labelpad=5)
#removeExponentialNotationOnAxis('y')
ax_mg.legend(loc=2)
ax_mb.minorticks_on()
ax_mg.minorticks_on()
mb_ylims = [2.37, 2.84]
mg_ylims = [2.09, 2.55]
xlims = [5, 11]
if eosName == "HShenEOS":
    eosName = "HShen"
    mb_ylims = [2.401, 3.1]
    mg_ylims = [2.21, 2.9]
    xlims = [2, 9]

ax_mb.set_ylim(mb_ylims)
ax_mb.set_xlim(xlims)
ax_mg.set_ylim(mg_ylims)
textPos = (0.45, 0.06)
plt.annotate("$\\rho_\mathrm{b, max}=\,$%s $\,$ g cm$^{-3}$" % fixScientificNotation(rhob),
             textPos, xytext=textPos, xycoords='axes fraction', textcoords='axes fraction',
             fontsize=22)
textPos = (0.66, 0.16)
plt.annotate(eosName + "  $\,\,\\tilde{A}=%s\,\,$" % a,
             textPos, xytext=textPos, xycoords='axes fraction', textcoords='axes fraction',
             fontsize=22)

textPos = (0.75, 0.38)
plt.annotate("$M_\mathrm{g}$",
             textPos, xytext=textPos, xycoords='axes fraction', textcoords='axes fraction',
             fontsize=26)
textPos = (0.4, 0.55)
plt.annotate("$M_\mathrm{b}$",
             textPos, xytext=textPos, xycoords='axes fraction', textcoords='axes fraction',
             fontsize=26)

plt.show()