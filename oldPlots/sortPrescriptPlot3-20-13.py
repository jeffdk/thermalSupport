import sys
import sqlite3
from matplotlib import rcParams
from scriptPlotstyleDatabase import symbolFromDBentry, manyScriptSequencePlot, getScriptsDb, scriptFromScriptName
from sqlUtils import queryDBGivenParams

rcParams['legend.frameon'] = False

sys.path.append('./maxMassOrigFiles/')
#noinspection PyUnresolvedReferences
from sqlPlotRoutines import sequencePlot, equalsFiltersFromDict


databaseFile = '/home/jeff/work/rotNSruns/allRuns3-24-13.db'
connectionTov=sqlite3.connect(databaseFile)
c=connectionTov.cursor()
#
prescriptionParameters = ('T', 'rollMid', 'rollScale', 'eosTmin', 'fixedTarget', 'fixedQuantity')

paramsDict = dict([(key, str(None)) for key in prescriptionParameters])
#paramsDict['eosTmin'] = 5.0
symbolFromDBentry(paramsDict)
manyScriptSequencePlot(["a", "gravMass"], c, ("eos='HShenEOS'", "ye=.1"), "arealR", "gravMass",
                       grid=True,  title="", vmax=40, vmin=12)

#exit()
c.execute("SELECT DISTINCT edMax FROM models")
print c.fetchall()

paramsDict['eos'] = 'LS220'
paramsDict['ye'] = 0.1
paramsDict['edMax'] = 694871794800000.0
paramsDict['a'] = 0.0
#paramsDict['rpoe'] = 0.7272727272727
colorVar = "arealR"
xaxisVar = "rpoe"
yaxisVar = "gravMass"#"MAX(gravMass)"
vmax = 25
vmin = 10.0
filters = equalsFiltersFromDict(paramsDict, 1e-1)

manyScriptSequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, vmin=vmin, vmax=vmax,
                       grid=True, suppressShow=True, title="")

paramsDict['eosTmin'] = 5.0

filters = equalsFiltersFromDict(paramsDict)

manyScriptSequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, grid=True, vmin=vmin, vmax=vmax,
                       suppressShow=True, title="")


paramsDict.update(scriptFromScriptName("c40p0").paramsDict)
filters = equalsFiltersFromDict(paramsDict)

manyScriptSequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, suppressShow=True, vmin=vmin, vmax=vmax,
                       grid=True)

#manyScriptSequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, grid=True, suppressShow=False, marker='^',
#             s=50, vmax=vmax, vmin=vmin, title="a = " + str(paramsDict['a']) ) #,vmax=3e15, vmin=1e14)

paramsDict.update(scriptFromScriptName("cold").paramsDict)
filters = equalsFiltersFromDict(paramsDict)

manyScriptSequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, suppressShow=True, vmin=vmin, vmax=vmax,
                       grid=True)

paramsDict.update(scriptFromScriptName("c20p0").paramsDict)
filters = equalsFiltersFromDict(paramsDict)

manyScriptSequencePlot([xaxisVar, yaxisVar], c, filters, colorVar, grid=True, vmin=vmin, vmax=vmax,
             title="a = " + str(paramsDict['a']))


exit()