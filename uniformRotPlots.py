import sys
import sqlite3
from matplotlib import rcParams
from scriptPlotstyleDatabase import manyScriptSequencePlot
import matplotlib.pyplot as plt
import plot_defaults

rcParams['legend.frameon'] = False

sys.path.append('./maxMassOrigFiles/')
#noinspection PyUnresolvedReferences
from sqlPlotRoutines import sequencePlot, equalsFiltersFromDict


databaseFile = '/home/jeff/work/rotNSruns/allRuns3-24-13.db'
connectionTov = sqlite3.connect(databaseFile)
c = connectionTov.cursor()

filters = equalsFiltersFromDict({'ye': .1, 'a': 0.0, 'eos': 'HShenEOS'})

manyScriptSequencePlot(["rpoe", "edMax"], c, filters, "omega_c", "gravMass",
                       title="",  suppressShow=True, minRpoeOnly=False, vmax=1e4, vmin=0,)
plt.legend(loc=4)
#plt.xlim([0.0, 3.e15])
#plt.ylim([0.0, 3.0])
plt.show()