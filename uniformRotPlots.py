import sys
import sqlite3
from matplotlib import rcParams
from plotUtilsForPaper import latexField
from scriptPlotstyleDatabase import manyScriptSequencePlot
import matplotlib.pyplot as plt
import plot_defaults

rcParams['legend.frameon'] = False

sys.path.append('./maxMassOrigFiles/')
#noinspection PyUnresolvedReferences
from sqlPlotRoutines import sequencePlot, equalsFiltersFromDict


databaseFile = '/home/jeff/work/rotNSruns/allRuns3-25-13.db'
connectionTov = sqlite3.connect(databaseFile)
c = connectionTov.cursor()

filters = equalsFiltersFromDict({'ye': .1, 'eos': 'HShenEOS', 'a': 0.0, 'T': 0.01})
colorVar = "omega_c"
manyScriptSequencePlot(["edMax", "gravMass"], c, filters, colorVar, "gravMass",
                       suppressShow=True, minRpoeOnly=True, vmax=1e4, vmin=0,)
filters = equalsFiltersFromDict({'ye': .1, 'a': 0.0, 'eos': 'HShenEOS'})
manyScriptSequencePlot(["edMax", "gravMass"], c, filters , colorVar, "gravMass",
                       suppressShow=True, vmax=5000, vmin=0,)

colorLegend = plt.colorbar()
colorLegend.set_label(latexField(colorVar))
plt.legend(loc=4)
#plt.xlim([0.0, 3.e15])
#plt.ylim([0.0, 3.0])
plt.show()

exit()
#Below are not actually uniform rotation plots
a=1.0

filters = equalsFiltersFromDict({'ye': 0.1, 'eos': 'LS220', 'a': a,
                                 'T': 0.01, 'eosTmin': 0.01})
colorVar = "ToverW"


manyScriptSequencePlot(["edMax", "gravMass"], c, filters, colorVar,
                       suppressShow=True, forceColorbar=True,
                       vmax=.3, vmin=0.,)

#manyScriptSequencePlot(["edMax", "gravMass"], c, filters , colorVar, "gravMass",
#                       suppressShow=True, vmax=40, vmin=10,)

#colorLegend = plt.colorbar()
#colorLegend.set_label(latexField(colorVar))
plt.title("a=%s" % a)
plt.legend(loc=4)
plt.xlim([0.0, 3.e15])
plt.ylim([0.5, 3.5])
plt.show()