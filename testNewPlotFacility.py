import matplotlib.pyplot as plt
from datasetManager import cstDataset, cstSequence, reduceTwoSeqPlots

sourceDb = '/home/jeff/work/rotNSruns/allRuns3-25-13.db'

c40p0 = cstDataset("c40p0", "HShenEOS", 0.1, sourceDb)
c0p0 = cstDataset("cold", "HShenEOS", 0.1, sourceDb)

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