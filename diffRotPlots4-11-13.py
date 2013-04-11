import matplotlib
import matplotlib.pyplot as plt
import numpy
from datasetManager import cstDataset, cstSequence, reduceTwoSeqPlots
from plotUtilsForPaper import latexField, fixExponentialAxes, removeExponentialNotationOnAxis
import plot_defaults

sourceDb = '/home/jeff/work/rotNSruns/allRuns3-25-13.db'
ye = 0.1

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

shen_cold = cstDataset("cold", "HShenEOS", ye, sourceDb)

a = 1.0

slicer = {'a': a, 'rpoe': 'min'}
xVar = 'edMax'
yVar = 'gravMass'
xLabel = latexField(xVar)
yLabel = latexField(yVar)

#############################################################
# First plot: Mgrav vs edMax for cold
#############################################################
ToverWcuts = [0.25, 0.20, 0.15]
colorList = ['b', 'g', 'r']
for i, cut in enumerate(ToverWcuts):
    a = 1.0
    slicer = {'a': a, 'rpoe': 'min'}
    filters = ('ToverW<' + str(cut),)
    thisSeq = cstSequence(shen_cold, slicer, filters)
    thisPlot = thisSeq.getSeqPlot([xVar], [yVar], filters)
    plt.plot(*thisPlot, label="Max $T/|W|=$ " + str(cut) + r" $\tilde{A}=$" + str(a),
             lw=2, ls='-', c=colorList[i])

    a = 0.8
    slicer = {'a': a, 'rpoe': 'min'}
    thisSeq = cstSequence(shen_cold, slicer, filters)
    thisPlot = thisSeq.getSeqPlot([xVar], [yVar], filters)
    plt.plot(*thisPlot, label="Max $T/|W|=$ " + str(cut) + r" $\tilde{A}=$" + str(a),
             lw=2, ls='--', c=colorList[i])

    a = 0.6
    slicer = {'a': a, 'rpoe': 'min'}
    thisSeq = cstSequence(shen_cold, slicer, filters)
    thisPlot = thisSeq.getSeqPlot([xVar], [yVar], filters)
    plt.plot(*thisPlot, label="Max $T/|W|=$ " + str(cut) + r" $\tilde{A}=$" + str(a),
             lw=2, ls=':', c=colorList[i])

plt.xlabel(xLabel)
plt.ylabel(yLabel)
fixExponentialAxes()
plt.xlim([1e14, 1e15])
plt.ylim([0.5, 3.5])
matplotlib.rc('legend', fontsize=16)
plt.axes().annotate(r"cold \, HShen", xy=(10 ** 14.2, 3.2), fontsize=20)
plt.legend(loc=4)
plt.show()