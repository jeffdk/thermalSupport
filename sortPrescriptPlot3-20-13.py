__author__ = 'jeff'
import sys
import sqlite3
import matplotlib.pyplot as mpl
from sqlUtils import queryDBGivenParams



sys.path.append('./maxMassOrigFiles/')
#noinspection PyUnresolvedReferences
from sqlPlotRoutines import sequencePlot


databaseFile = '/home/jeff/work/rotNSruns/allRuns3-20-13.db'
connectionTov=sqlite3.connect(databaseFile)
cTov=connectionTov.cursor()
filters = ("T='None'", "rollMid='None'", "rollScale='None'", "eosTmin='None'",
           "fixedTarget='None'", "fixedQuantity='None'", "ye=0.15", "eos='HShenEOS'",
           "arealR<60")
sequencePlot(["edMax","baryMass"],cTov,filters,"a",grid=True, title="")


exit()