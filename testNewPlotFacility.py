
from datasetManager import cstDataset, cstSequence

sourceDb = '/home/jeff/work/rotNSruns/allRuns3-25-13.db'

c30p0 = cstDataset("c30p0", "HShenEOS", 0.1, sourceDb)

thisSeq = cstSequence(c30p0, {'a': 0.0, 'rpoe': 1.0})
print "dur"
print "dur"

thisSeq = cstSequence(c30p0, {'a': 1.0, 'edMax': 323076923000000.})

thisSeq = cstSequence(c30p0, {'rpoe': 1.0, 'edMax': 323076923000000.})