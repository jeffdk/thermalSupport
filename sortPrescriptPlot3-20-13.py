import sys
import sqlite3
import matplotlib.pyplot as mpl
from scriptPlotstyleDatabase import symbolFromDBentry
from sqlUtils import queryDBGivenParams



sys.path.append('./maxMassOrigFiles/')
#noinspection PyUnresolvedReferences
from sqlPlotRoutines import sequencePlot, equalsFiltersFromDict


databaseFile = '/home/jeff/work/rotNSruns/allRuns3-20-13.db'
connectionTov=sqlite3.connect(databaseFile)
c=connectionTov.cursor()
#
prescriptionParameters = ('T', 'rollMid', 'rollScale', 'eosTmin', 'fixedTarget', 'fixedQuantity')

paramsDict = dict([(key, None) for key in prescriptionParameters])
#paramsDict['eosTmin'] = 5.0
symbolFromDBentry(paramsDict)

exit()

paramsDict['eos'] = 'HShenEOS'
paramsDict['ye'] = 0.15
paramsDict['edMax'] = 704166666600000.0
paramsDict['a'] = 0.6
#paramsDict['rpoe'] = 0.7272727272727
colorVar = "omega_c"
xaxisVar = "rpoe"
yaxisVar = "gravMass"
#paramsDict['RedMax'] = 0.0
vmax = 10000
vmin = 0.0

# c.execute("SELECT DISTINCT edMax FROM models WHERE edMax < 7.3e14 AND edMax > 5.8e14")
# grid = c.fetchall()
#
# for ed in grid:
#     print ed
#     paramsDict['edMax'] = ed[0]
#     filters = equalsFiltersFromDict(paramsDict,1e-1) #+ ("arealR<20",)
#     print filters
#     sequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, grid=True, suppressShow=True, title="",
#                  s=50, vmax=vmax, vmin=vmin)
#
#
# sequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, grid=True, suppressShow=True, title="",
#                  s=50, vmax=vmax, vmin=vmin ) #,vmax=3e15, vmin=1e14)
#
#
#
#
# #filters += ("arealR<60",)
#
#
# #sequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, grid=True, suppressShow=True, title="", s=50, vmin=14, vmax=30)
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
#     sequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, suppressShow=True, grid=True, marker='^',
#                  vmin=vmin, vmax=vmax, s=50)
#
# sequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, grid=True, suppressShow=False, marker='^',
#              s=50, vmax=vmax, vmin=vmin, title="a = " + str(paramsDict['a']) ) #,vmax=3e15, vmin=1e14)
filters = equalsFiltersFromDict(paramsDict)

sequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, grid=True, suppressShow=True, title="",
                 s=50, vmax=vmax, vmin=vmin ) #,vmax=3e15, vmin=1e14)

paramsDict['T'] = 40.0
paramsDict['rollMid'] = 14.0
paramsDict['rollScale'] = 0.5
paramsDict['eosTmin'] = 0.01
#paramsDict['edMax'] = 0.7
filters = equalsFiltersFromDict(paramsDict, 1e-1)

sequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, suppressShow=True, grid=True, marker='^',
                 vmin=vmin, vmax=vmax, s=50)

sequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, grid=True, suppressShow=False, marker='^',
             s=50, vmax=vmax, vmin=vmin, title="a = " + str(paramsDict['a']) ) #,vmax=3e15, vmin=1e14)

exit()
exit()
paramsDict['T'] = 0.5
paramsDict['rollMid'] = 14.0
paramsDict['rollScale'] = 0.5
paramsDict['eosTmin'] = 0.01

filters = equalsFiltersFromDict(paramsDict)

sequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, suppressShow=True, grid=True, marker='*',
             vmin=vmin, vmax=vmax,
             s=50)

paramsDict['T'] = 20.0
paramsDict['rollMid'] = 14.0
paramsDict['rollScale'] = 0.5
paramsDict['eosTmin'] = 0.01

filters = equalsFiltersFromDict(paramsDict)

sequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, grid=True, marker='s',
             s=50, vmin=vmin, vmax=vmax,
             title="a = " + str(paramsDict['a']))


exit()