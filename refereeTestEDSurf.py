

from consts import CGS_C, CGS_MSUN
from eosDriver import eosDriver, getTRollFunc, kentaDataTofLogRhoFit1, kentaDataTofLogRhoFit2
import matplotlib
import matplotlib.pyplot as plt
import numpy
from datasetManager import cstDataset, cstSequence

sourceBase = '/home/jeff/work/rotNSruns/refReportsOneMod.db'
source6  = '/home/jeff/work/rotNSruns/refReportsOneMod_surf6.db'

source = source6

filters = ()

theSet = cstDataset("c30p10", "LS220", "BetaEq", source)

theSeq = cstSequence(theSet, {'a': 0.0, 'rpoe': 'min'}, filters)

toPlot = theSeq.getSeqPlot('edMax', 'baryMass', filters)

print toPlot

#otherSet = cstDataset("c30p10", "LS220", "BetaEq", source6)


## EOS convert density

ls220EosTableFilename = '/home/jeff/work/LS220_234r_136t_50y_analmu_20091212_SVNr26.h5'

theEos = eosDriver(ls220EosTableFilename)
print theEos.rhobFromEnergyDensityWithTofRho(1.0e15, "BetaEq", kentaDataTofLogRhoFit1())
