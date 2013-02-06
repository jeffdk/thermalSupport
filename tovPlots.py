
import sys
import sqlite3
import matplotlib.pyplot as mpl
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import numpy
from sqlUtils import queryDBGivenParams

sys.path.append('./maxMassOrigFiles/')
#noinspection PyUnresolvedReferences
from sqlPlotRoutines import sequencePlot

font = {'family' : 'normal',
        'size'   : 26}

matplotlib.rc('font', **font)

databaseFile         = '/home/jeff/work/rotNSruns/hs-TOV.db'
connectionhs=sqlite3.connect(databaseFile)
chs=connectionhs.cursor()

databaseFile         = '/home/jeff/work/rotNSruns/ls-TOV.db'
connectionls=sqlite3.connect(databaseFile)
cls=connectionls.cursor()

databaseFile         = '/home/jeff/work/rotNSruns/spec-gam2-tov.db'
connectiongam2=sqlite3.connect(databaseFile)
cgam2=connectiongam2.cursor()
xaxis = "edMax"
yaxis = "gravMass"
filt = "arealR<100"
#sequencePlot([xaxis,yaxis],cls,("T=0.5",filt),orderBy='edMax',
#    suppressShow=True)

#sequencePlot([xaxis,yaxis],chs,("T=0.5",filt),orderBy='edMax',
#    suppressShow=True)


databaseFile         = '/home/jeff/work/rotNSruns/hs-TOV-new.db'
connectionhs=sqlite3.connect(databaseFile)
chs=connectionhs.cursor()

databaseFile         = '/home/jeff/work/rotNSruns/ls-TOV-new.db'
connectionls=sqlite3.connect(databaseFile)
cls=connectionls.cursor()

#sequencePlot([xaxis,yaxis],cls,("T=0.5",filt),orderBy='edMax',
#    suppressShow=True)

#sequencePlot([xaxis,yaxis],chs,("T=0.5",filt),orderBy='edMax',
#    suppressShow=True)


#sequencePlot([xaxis,yaxis],cgam2,("T=0.0",filt),orderBy='edMax',grid=True,
#    title="Blue - LS220   Green - HS   Red - Gamma=2")
chs.execute("SELECT DISTINCT T FROM MODELS")
Ts=chs.fetchall()
print "TS: ", Ts

for T in Ts:
    sequencePlot([xaxis,yaxis],chs,
        (filt,"T>%s" % (T[0] -.01), "T<%s" % (T[0] +.01)),
        orderBy='edMax',
        suppressShow=True,grid=True,title="HS EOS",
        c=matplotlib.pyplot.cm.jet(T[0]/40.0))

sequencePlot([xaxis,yaxis],chs,
        (filt,),
        orderBy='edMax', colorBy="T",
        suppressShow=False,grid=True,title="HS EOS",
        s=0.01)