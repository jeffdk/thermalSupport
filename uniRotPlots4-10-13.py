import matplotlib
import matplotlib.pyplot as plt
import numpy
from datasetManager import cstDataset, cstSequence, reduceTwoSeqPlots
from plotUtilsForPaper import latexField, fixExponentialAxes, removeExponentialNotationOnAxis
import plot_defaults

sourceDb = '/home/jeff/work/rotNSruns/allRuns3-25-13.db'
ye = 0.1

# shen_c40p0 = cstDataset("c40p0", "HShenEOS", ye, sourceDb)
# shen_c30p0 = cstDataset("c30p0", "HShenEOS", ye, sourceDb)
# shen_c20p0 = cstDataset("c20p0", "HShenEOS", ye, sourceDb)
# shen_c30p10 = cstDataset("c30p10", "HShenEOS", ye, sourceDb)
# shen_c30p5 = cstDataset("c30p5", "HShenEOS", ye, sourceDb)
shen_cold = cstDataset("cold", "HShenEOS", ye, sourceDb)

# ls220_c40p0 = cstDataset("c40p0", "LS220", ye, sourceDb)
# ls220_c30p0 = cstDataset("c30p0", "LS220", ye, sourceDb)
# ls220_c20p0 = cstDataset("c20p0", "LS220", ye, sourceDb)
# ls220_c30p10 = cstDataset("c30p10", "LS220", ye, sourceDb)
# ls220_c30p5 = cstDataset("c30p5", "LS220", ye, sourceDb)
ls220_cold = cstDataset("cold", "LS220", ye, sourceDb)

tovSlice = {'a': 0.0, 'rpoe': 1.0}
uniformMaxRotSlice = {'a': 0.0, 'rpoe': 'min'}

xVar = 'edMax'
xLabel = latexField(xVar)

yVar = 'gravMass'
yLabel = latexField(yVar)

filters = ()

tovLS220 = cstSequence(ls220_cold, tovSlice, filters)
tovShen = cstSequence(shen_cold, tovSlice, filters)
rotLS220 = cstSequence(ls220_cold, uniformMaxRotSlice, filters)
rotShen = cstSequence(shen_cold, uniformMaxRotSlice, filters)

#############################################################
# First plot: LS and Shen, just cold
#############################################################
thisPlot = tovLS220.getSeqPlot([xVar], [yVar], filters)
plt.plot(*thisPlot, c='k', ls='-', label='LS220 TOV')

thisPlot = tovShen.getSeqPlot([xVar], [yVar], filters)
plt.plot(*thisPlot, c='b', ls='-', label='HShen TOV')

thisPlot = rotLS220.getSeqPlot([xVar], [yVar], filters)
plt.plot(*thisPlot, c='k', ls='--', label='LS220 Max $\Omega$')

thisPlot = rotShen.getSeqPlot([xVar], [yVar], filters)
plt.plot(*thisPlot, c='b', ls='--', label='HShen Max $\Omega$')

plt.xlabel(xLabel)
plt.ylabel(yLabel)
fixExponentialAxes()
plt.legend(loc=4)
plt.show()

colors = {'c30p0': 'g',
          'c20p0': 'b',
          'c40p0': 'r',
          #'cold': 'm',
          'c30p5': 'c',
          'c30p10': 'k'}

symbols = {'c30p0': 's',
           'c20p0': 'v',
           'c40p0': '^',
           'c30p5': 'p',
           'c30p10': 'H'}
#############################################################
# First plot: Just Shen, frac diffs
#############################################################
filters = ('arealR<100',)
baseline = cstSequence(shen_cold, uniformMaxRotSlice, filters).getSeqPlot([xVar], [yVar], filters)

for script in colors.keys():
    thisSet = cstDataset(script, "HShenEOS", ye, sourceDb)
    thisSeq = cstSequence(thisSet, uniformMaxRotSlice, filters)
    thisPlot = thisSeq.getSeqPlot([xVar], [yVar], filters)

    result = reduceTwoSeqPlots(baseline, thisPlot, lambda a, b: 100 * b / a)

    plt.loglog(*result, c=colors[script],  label=script)

plt.loglog([1.e14, 3.e15], [100., 100.], ls=':', linewidth=1, c='k')
plt.xlabel(xLabel)
plt.axes().yaxis.set_minor_formatter(matplotlib.pyplot.FormatStrFormatter('%.0f'))
plt.axes().yaxis.set_major_formatter(matplotlib.pyplot.FormatStrFormatter('%.0f'))
plt.ylabel("$M_g$/$M_g(\mathrm{cold}),\, \%$", labelpad=5)
removeExponentialNotationOnAxis('y')
plt.legend()
plt.show()