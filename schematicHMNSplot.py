from eosDriver import eosDriver, getTRollFunc
import matplotlib
import matplotlib.pyplot as plt
import numpy
from datasetManager import cstDataset, cstSequence
import plot_defaults


sourceDb = '/home/jeff/work/rotNSruns/vdenseBetaEqOnlyMoreA.db'
tovSourceDb = '/home/jeff/work/rotNSruns/allRuns3-25-13.db'
shenEosTableFilename = '/home/jeff/work/HShenEOS_rho220_temp180_ye65_version_1.1_20120817.h5'

eosName = 'HShenEOS'
theEos = eosDriver(shenEosTableFilename)

tovSlice = {'a': 0.0, 'rpoe': 1.0}
uniformMaxRotSlice = {'a': 0.0, 'rpoe': 'min'}
diffMaxRotSlice = {'a': 1.0, 'rpoe': 'min'}
a8 = {'a': 0.8, 'rpoe': 'min'}
a7 = {'a': 0.7, 'rpoe': 'min'}
a6 = {'a': 0.6, 'rpoe': 'min'}
a5 = {'a': 0.5, 'rpoe': 'min'}
a4 = {'a': 0.4, 'rpoe': 'min'}

colors = {'c30p0': 'g',
          'c20p0': 'b',
          'c40p0': 'r',
          'cold': 'k',
          'c30p5': 'c',
          'c30p10': 'm'}

scripts = ['cold', 'c20p0', 'c40p0']
params40 = (40.0, 14.18, 0.5,)
params20 = (20.0, 13.93, 0.25,)
tFuncs = [lambda x: 0.01,
          getTRollFunc(params20[0], 0.01, params20[1], params20[2]),
          getTRollFunc(params40[0], 0.01, params40[1], params40[2])]
ye = 'BetaEq'

for i, script in enumerate(scripts):

    tempFunc = tFuncs[i]
    theEos.resetCachedBetaEqYeVsRhobs(tempFunc, 13.5, 16.0)

    xFunc = lambda x: theEos.rhobFromEnergyDensityWithTofRho(x, ye, tempFunc)
    #xFunc = lambda x: x
    filters = ('ToverW<0.25',)

    thisSet = cstDataset(script, eosName, ye, sourceDb)
    dashList = [(None, None), (25, 4), (13, 5), (20, 4, 10, 6), (10, 3, 5, 5)]
    # (20, 5, 10, 5, 5, 10)]
    dashList = dashList[::-1]
    for j, slicer in enumerate([tovSlice, uniformMaxRotSlice, a4, a5, diffMaxRotSlice]):
        thisSeq = cstSequence(thisSet, slicer, filters)

        thisPlot = thisSeq.getSeqPlot(['edMax'], ['gravMass', 'baryMass'], filters, xcolFunc=xFunc,
                                      ycolFunc=lambda x, y: x)

        plt.semilogx(*thisPlot, c=colors[script], dashes=dashList[j])

    del thisSet

plt.minorticks_on()
plt.show()