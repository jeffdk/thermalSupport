import sys
import sqlite3
from matplotlib import rcParams
from scriptPlotstyleDatabase import symbolFromDBentry, manyScriptSequencePlot
from sqlUtils import queryDBGivenParams

rcParams['legend.frameon'] = False

sys.path.append('./maxMassOrigFiles/')
#noinspection PyUnresolvedReferences
from sqlPlotRoutines import sequencePlot, equalsFiltersFromDict


databaseFile = '/home/jeff/work/rotNSruns/allRuns3-22-13.db'
connectionTov=sqlite3.connect(databaseFile)
c=connectionTov.cursor()
#
prescriptionParameters = ('T', 'rollMid', 'rollScale', 'eosTmin', 'fixedTarget', 'fixedQuantity')

paramsDict = dict([(key, str(None)) for key in prescriptionParameters])
#paramsDict['eosTmin'] = 5.0
symbolFromDBentry(paramsDict)
manyScriptSequencePlot(["a", "edMax"], c, ("eos='HShenEOS'", "fixedQuantity='None'", "ye=.15"), "arealR",
                       grid=True,  title="", vmax=40, vmin=12)

#exit()

paramsDict['eos'] = 'HShenEOS'
paramsDict['ye'] = 0.15
#paramsDict['edMax'] = 704166666600000.0
paramsDict['a'] = 1.0
#paramsDict['rpoe'] = 0.7272727272727
colorVar = "arealR"
xaxisVar = "rpoe"
yaxisVar = "gravMass"#"MAX(gravMass)"
vmax = 25
vmin = 10.0

# c.execute("SELECT DISTINCT edMax FROM models WHERE edMax < 7.3e14 AND edMax > 5.8e14")
# grid = c.fetchall()
#
# for ed in grid:
#     print ed
#     paramsDict['edMax'] = ed[0]
#     filters = equalsFiltersFromDict(paramsDict,1e-1) #+ ("arealR<20",)
#     print filters
#     manyScriptSequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, grid=True, suppressShow=True, title="",
#                  s=50, vmax=vmax, vmin=vmin)
#
#
# manyScriptSequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, grid=True, suppressShow=True, title="",
#                  s=50, vmax=vmax, vmin=vmin ) #,vmax=3e15, vmin=1e14)
#
#
#
#
# #filters += ("arealR<60",)
#
#
# #manyScriptSequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, grid=True, suppressShow=True, title="", s=50, vmin=14, vmax=30)
#
# #paramsDict['ye'] = 'BetaEq'
# #del paramsDict['fixedTarget']
# #del paramsDict['fixedQuantity']
#
# for ed in grid:
#
#     paramsDict['T'] = 40.0
#     paramsDict['rollMid'] = 14.0
#     paramsDict['rollScale'] = 0.5
#     paramsDict['eosTmin'] = 0.01
#     paramsDict['edMax'] = ed[0]
#     filters = equalsFiltersFromDict(paramsDict, 1e-1)
#
#     manyScriptSequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, suppressShow=True, grid=True, marker='^',
#                  vmin=vmin, vmax=vmax, s=50)
#
# manyScriptSequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, grid=True, suppressShow=False, marker='^',
#              s=50, vmax=vmax, vmin=vmin, title="a = " + str(paramsDict['a']) ) #,vmax=3e15, vmin=1e14)
filters = equalsFiltersFromDict(paramsDict, 1e-1)

manyScriptSequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, vmin=vmin, vmax=vmax,
                       grid=True, suppressShow=True, title="")

paramsDict['eosTmin'] = 5.0

filters = equalsFiltersFromDict(paramsDict)

manyScriptSequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, grid=True, vmin=vmin, vmax=vmax,
                       suppressShow=True, title="")


paramsDict['T'] = 40.0
paramsDict['rollMid'] = 14.0
paramsDict['rollScale'] = 0.5
paramsDict['eosTmin'] = 0.01
#paramsDict['edMax'] = 0.7
filters = equalsFiltersFromDict(paramsDict)

manyScriptSequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, suppressShow=True, vmin=vmin, vmax=vmax,
                       grid=True)

#manyScriptSequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, grid=True, suppressShow=False, marker='^',
#             s=50, vmax=vmax, vmin=vmin, title="a = " + str(paramsDict['a']) ) #,vmax=3e15, vmin=1e14)



paramsDict['T'] = 0.5
paramsDict['rollMid'] = 14.0
paramsDict['rollScale'] = 0.5
paramsDict['eosTmin'] = 0.01

filters = equalsFiltersFromDict(paramsDict)

manyScriptSequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, suppressShow=True, vmin=vmin, vmax=vmax,
                       grid=True)

paramsDict['T'] = 20.0
paramsDict['rollMid'] = 14.0
paramsDict['rollScale'] = 0.5
paramsDict['eosTmin'] = 0.01

filters = equalsFiltersFromDict(paramsDict)

manyScriptSequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, grid=True, vmin=vmin, vmax=vmax,
             title="a = " + str(paramsDict['a']))


exit()