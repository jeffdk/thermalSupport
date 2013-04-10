import matplotlib.pyplot as plt
from datasetManager import cstDataset, cstSequence, reduceTwoSeqPlots
from plotUtilsForPaper import latexField, fixExponentialAxes
import plot_defaults

sourceDb = '/home/jeff/work/rotNSruns/allRuns3-25-13.db'

shen_c40p0 = cstDataset("c40p0", "HShenEOS", 0.1, sourceDb)
shen_c30p0 = cstDataset("c30p0", "HShenEOS", 0.1, sourceDb)
shen_c20p0 = cstDataset("c20p0", "HShenEOS", 0.1, sourceDb)
shen_c30p10 = cstDataset("c30p10", "HShenEOS", 0.1, sourceDb)
shen_c30p5 = cstDataset("c30p5", "HShenEOS", 0.1, sourceDb)
shen_cold = cstDataset("cold", "HShenEOS", 0.1, sourceDb)

ls220_c40p0 = cstDataset("c40p0", "LS220", 0.1, sourceDb)
ls220_c30p0 = cstDataset("c30p0", "LS220", 0.1, sourceDb)
ls220_c20p0 = cstDataset("c20p0", "LS220", 0.1, sourceDb)
ls220_c30p10 = cstDataset("c30p10", "LS220", 0.1, sourceDb)
ls220_c30p5 = cstDataset("c30p5", "LS220", 0.1, sourceDb)
ls220_cold = cstDataset("cold", "LS220", 0.1, sourceDb)

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
