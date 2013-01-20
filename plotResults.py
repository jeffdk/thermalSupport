
import sys
import sqlite3
import matplotlib.pyplot as mpl
from mpl_toolkits.mplot3d import Axes3D
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

databaseFile = '/home/jeff/work/rotNSruns/hotTov.db'
connectionTov=sqlite3.connect(databaseFile)
cTov=connectionTov.cursor()

sequencePlot(["edMax","baryMass"],cTov,(),"T",grid=True,title="TOV Models for Shen_14.0_0.5")

#Find energy density of maximum mass as function of variables
plotVar = 'edMax'
plot3d  = True
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


resultTov=[]
for T in cTov.execute("SELECT DISTINCT T FROM models"):
    T=T[0]
    answer = edOfMaxMass( ("T>%s" % (T -.01), "T<%s" % (T +.01))  ,connectionTov)
    resultTov.append((-.10,T,answer[plotVar]))



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

    if answer['RedMax'] > 0:
        resultT.append((a,T,answer[plotVar]))
    else:
        resultS.append((a,T,answer[plotVar]))


#points = zip(*grid)
#xs, ys = numpy.meshgrid(points[0],points[1])

resultS=zip(*resultS)
resultT=zip(*resultT)
resultTov=zip(*resultTov)

if plot3d:
    fig=mpl.figure()
    ax = fig.add_subplot(111,projection='3d')
    print resultS
    ax.scatter(resultS[0],resultS[1],resultS[2],color='b',marker='o',label="Spheroid")
    ax.scatter(*resultT,color='r',marker='^', label="toroid")
    ax.scatter(*resultTov,color='g',marker='s', label="tov")
    ax.set_xlabel("Differential rotation parameter A (-.1 is TOV)")
    ax.set_ylabel("Temperature (MeV)")
    if plotVar=="edMax":
        ax.set_zlabel("Maximum energy density of model with largest mass")
    if plotVar=="max":
        ax.set_zlabel("Gravitational mass of model with largest mass")
    handles,labels = ax.get_legend_handles_labels()
    #mpl.legend(["Spheroid","Toroid","TOV"])

    mpl.show()
    exit()

mpl.scatter(resultS[0],resultS[2],c=resultS[1],s=40,marker='o')
mpl.scatter(resultT[0],resultT[2],c=resultT[1],s=40,marker='^')
mpl.scatter(resultTov[0],resultTov[2],c=resultTov[1],s=40,marker='s')
colorLegend=mpl.colorbar()
colorLegend.set_label("Model Temperature (MeV)")
mpl.grid(True)
mpl.xlabel("Differential rotation parameter A")
if plotVar=="edMax":
    mpl.ylabel("Maximum energy density of model with largest mass")
if plotVar=="max":
    mpl.ylabel("Gravitational mass of model with largest mass")
mpl.title("Properties of model with largest mass Shen_14_0.5")
mpl.show()