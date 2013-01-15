
import sys
import sqlite3
import matplotlib.pyplot as mpl
#from mpl_toolkits.mplot3d import Axes3D
import numpy
from sqlUtils import queryDBGivenParams

sys.path.append('./maxMassOrigFiles/')
#noinspection PyUnresolvedReferences
from sqlPlotRoutines import sequencePlot


databaseFile         = '/home/jeff/work/rotNSruns/sekiguchi-models.db'
connection=sqlite3.connect(databaseFile)
c=connection.cursor()

#sequencePlot(["edMax","baryMass"],c,("rpoe=.66"),"T",
#             grid=True,title="Sekiguichi-like Models A=1.0, rpoe=.66")

connection.close()
del connection


#Find energy density of maximum mass as function of variables

def edOfMaxMass(filters,connection):
    c=connection.cursor()
    answer={'max':-1.e10,'edMax':0.0,'RedMax':False}
    values = queryDBGivenParams("gravMass,edMax,RedMax",(),c,"models",filters)
    for max,edMax,RedMax in values:
        if max > answer['max']:
            answer['max']=max
            answer['edMax']=edMax
            answer['RedMax']=RedMax
    return answer


databaseFile         = '/home/jeff/work/rotNSruns/mass-shed-models.db'
connection=sqlite3.connect(databaseFile)
c=connection.cursor()

c.execute("SELECT DISTINCT a,T FROM models")
grid = c.fetchall()

c.execute("SELECT DISTINCT T FROM MODELS")
Ts=c.fetchall()

c.execute("SELECT DISTINCT a FROM MODELS")
ahs=c.fetchall()


resultS =[]
resultT =[]
for a,T in grid:
    print a,T
    answer = edOfMaxMass( ("a>%s" % (a-.001), "a<%s" % (a+.001),
                           "T>%s" % (T -.01), "T<%s" % (T +.01))  ,connection)
    plotVar = 'edMax'
    if answer['RedMax'] > 0:
        resultT.append((a,T,answer[plotVar]))
    else:
        resultS.append((a,T,answer[plotVar]))


#points = zip(*grid)
#xs, ys = numpy.meshgrid(points[0],points[1])

resultS=zip(*resultS)
resultT=zip(*resultT)

#fig=mpl.figure()
#ax = fig.add_subplot(111)
mpl.scatter(resultS[0],resultS[2],c=resultS[1],s=40,marker='o')
mpl.scatter(resultT[0],resultT[2],c=resultT[1],s=40,marker='^')
colorLegend=mpl.colorbar()
colorLegend.set_label("Model Temperature (MeV)")
mpl.grid(True)
mpl.xlabel("Differential rotation parameter A")
mpl.ylabel("Maximum energy density of model with largest mass")
mpl.title("Properties of model with largest mass Shen_14_0.5")
mpl.show()