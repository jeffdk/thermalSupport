
import sys
import sqlite3
sys.path.append('./maxMassOrigFiles/')
#noinspection PyUnresolvedReferences
from sqlPlotRoutines import sequencePlot


databaseFile         = '/home/jeff/work/rotNSruns/sekiguchi-models.db'
connection=sqlite3.connect(databaseFile)
c=connection.cursor()

sequencePlot(["edMax","baryMass"],c,("rpoe=.66"),"T",
             grid=True,title="Sekiguichi-like Models A=1.0, rpoe=.66")