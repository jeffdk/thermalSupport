import matplotlib.pyplot as plt
from datasetManager import cstDataset, cstSequence, reduceTwoSeqPlots
import numpy

sourceDb = '/home/jeff/work/rotNSruns/vdenseBetaEqOnly.db'

ye = 'BetaEq'
eosTable = 'LS220'
#c40p0 = cstDataset("c40p0", eosTable, 'BetaEq', sourceDb)
c0p0 = cstDataset("cold", eosTable, 'BetaEq', sourceDb)

point = {'a': 1., 'rpoe': 0.38, 'edMax': 595697963600000.}

print numpy.linalg.det(c0p0.gradientsAtPoint(['J', 'baryMass'], point))

c0p0.getSecInstabilitySeq(0.0, 0.7, 1e15, 3e15)

exit()

sliceDict = {'a': 1.0, 'rpoe': 'min'}
filters = ()  # ('ToverW<.12', 'RedMax=0.0')#('ToverW>0.1',)

thisSeq40 = cstSequence(c40p0, sliceDict, filters)

thisSeq0 = cstSequence(c0p0, sliceDict, filters)

#thisSeq.getColumnData(['J', 'gravMass'], lambda j, m: j / (m * m), ('ToverW<.25',))
#
# guy40 = thisSeq40.getSeqPlot(['rpoe'], ['J', 'gravMass'], filters,
#                              ycolFunc=lambda j, m: j / (m * m))
# guy0 = thisSeq0.getSeqPlot(['rpoe'], ['J', 'gravMass'], filters,
#                            ycolFunc=lambda j, m: j / (m * m))
guy40 = thisSeq40.getSeqPlot(['edMax'], ['gravMass'], filters,
                             ycolFunc=lambda j: j)
guy0 = thisSeq0.getSeqPlot(['edMax'], ['gravMass'], filters,
                           ycolFunc=lambda j: j)
result = reduceTwoSeqPlots(guy0, guy40, lambda a, b: b / a - 1.0)

print result

plt.plot(*result)
plt.show()


#thisSeq = cstSequence(c30p0, {'rpoe': 1.0, 'edMax': 323076923000000.})