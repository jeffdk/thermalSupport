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
          'cold': 'm',
          'c30p5': 'c',
          'c30p10': 'k'}

symbols = {'c30p0': 's',
           'c20p0': 'v',
           'c40p0': '^',
           'c30p5': 'p',
           'c30p10': 'H'}


#############################################################
# W/Mg vs T/W for diff scripts a = 0.6 w T/W < 0.25 threshold
#############################################################
xVar = 'ToverW'
yVar = None
xLabel = latexField(xVar)
a = 0.6
slicer = {'a': a, 'rpoe': 'min'}

filters = ('ToverW<0.25',)
for script, c in colors.items():

    thisSet = cstDataset(script, "HShenEOS", ye, sourceDb)
    thisSeq = cstSequence(thisSet, slicer, filters)
    thisPlot = thisSeq.getSeqPlot([xVar], ['gravPotW', 'gravMass'], filters,
                                  ycolFunc=lambda a, b: a / b)
    plt.plot(*thisPlot, label=script, c=c)
    del thisSet
plt.xlabel(xLabel)
plt.ylabel("$W/M_g$")
plt.legend(loc=2)
plt.axes().annotate(r"HShen \," + r"$\tilde{A}=$" + str(a), xy=(.17, 0.36), fontsize=20)
plt.show()
shen_cold = cstDataset("cold", "HShenEOS", ye, sourceDb)
#############################################################
# W/Mg vs T/W for cold: w T/W < 0.25 threshold
#############################################################
xVar = 'ToverW'
yVar = None
xLabel = latexField(xVar)
a = 1.0


thisSet = shen_cold
filters = ('ToverW<0.25',)

for a in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
    slicer = {'a': a, 'rpoe': 'min'}
    thisSeq = cstSequence(thisSet, slicer, filters)
    thisPlot = thisSeq.getSeqPlot([xVar], ['gravPotW', 'gravMass'], filters,
                                  ycolFunc=lambda a, b: a / b)
    plt.plot(*thisPlot, label=r"$\tilde{A}=$" + str(a))
plt.xlabel(xLabel)
plt.ylabel("$W/M_g$")
plt.legend(loc=2)
plt.axes().annotate(r"cold \, HShen", xy=(.025, 0.1), fontsize=20)
plt.show()

#############################################################
# Mgrav vs edMax for cold: ToverW thresholds
#############################################################
a = 1.0
slicer = {'a': a, 'rpoe': 'min'}
xVar = 'edMax'
yVar = 'gravMass'
xLabel = latexField(xVar)
yLabel = latexField(yVar)

thisSet = shen_cold
ToverWcuts = [0.25, 0.20, 0.15]
colorList = ['b', 'g', 'r']
for i, cut in enumerate(ToverWcuts):
    a = 1.0
    slicer = {'a': a, 'rpoe': 'min'}
    filters = ('ToverW<' + str(cut),)
    thisSeq = cstSequence(thisSet, slicer, filters)
    thisPlot = thisSeq.getSeqPlot([xVar], [yVar], filters)
    plt.plot(*thisPlot, label="Max $T/|W|=$ " + str(cut) + r" $\tilde{A}=$" + str(a),
             lw=2, ls='-', c=colorList[i])

    a = 0.8
    slicer = {'a': a, 'rpoe': 'min'}
    thisSeq = cstSequence(thisSet, slicer, filters)
    thisPlot = thisSeq.getSeqPlot([xVar], [yVar], filters)
    plt.plot(*thisPlot, label="Max $T/|W|=$ " + str(cut) + r" $\tilde{A}=$" + str(a),
             lw=2, ls='--', c=colorList[i])

    a = 0.6
    slicer = {'a': a, 'rpoe': 'min'}
    thisSeq = cstSequence(thisSet, slicer, filters)
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