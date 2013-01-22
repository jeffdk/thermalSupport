
import sys
import sqlite3
import matplotlib.pyplot as mpl
from mpl_toolkits.mplot3d import Axes3D
import numpy
from sqlUtils import queryDBGivenParams

sys.path.append('./maxMassOrigFiles/')
#noinspection PyUnresolvedReferences
from sqlPlotRoutines import sequencePlot


databaseFile         = '/home/jeff/work/rotNSruns/rpoe-sequence.db'
connection=sqlite3.connect(databaseFile)
c=connection.cursor()

#sequencePlot(["edMax","baryMass"],c,("rpoe=.66"),"T",
#             grid=True,title="Sekiguichi-like Models A=1.0, rpoe=.66")

connection.close()
del connection

databaseFile = '/home/jeff/work/rotNSruns/rpoe-sequence.db'
connectionTov=sqlite3.connect(databaseFile)
cTov=connectionTov.cursor()

#sequencePlot(["edMax","baryMass"],cTov,(),"T",grid=True,title="TOV Models for Shen_14.0_0.5")

#Find energy density of maximum mass as function of variables
plotVar = 'max'
plot3d  = False

def edOfMaxMass(filters,connection):
    c=connection.cursor()
    answer={'max':-1.e10,'edMax':0.0,'RedMax':False}
    values = queryDBGivenParams("gravMass,edMax,RedMax,rpoe",(),c,"models",filters)
    for max,edMax,RedMax,rpoe in values:
        if max > answer['max']:
            answer['max']=max
            answer['edMax']=edMax
            answer['RedMax']=RedMax
            answer['rpoe'] =rpoe
    return answer


resultTov=[]
for T in cTov.execute("SELECT DISTINCT T FROM models"):
    T=T[0]
    answer = edOfMaxMass( ("T>%s" % (T -.01), "T<%s" % (T +.01))  ,connectionTov)
    resultTov.append((-.10,T,answer[plotVar]))
    #sequencePlot(["rpoe","gravMass"],cTov,("T>%s" % (T -.01), "T<%s" % (T +.01)), grid=True,
    #title="",suppressShow=True,c=mpl.cm.jet(T/40.))


databaseFile         = '/home/jeff/work/rotNSruns/rpoe-sequence.db'
#databaseFile         = '/home/jeff/work/rotNSruns/christian-request.db'
connection=sqlite3.connect(databaseFile)
c=connection.cursor()
avalue=0.7
#sequencePlot(["rpoe","baryMass"],c, ("a>%s" % (avalue-.001), "a<%s" % (avalue+.001), "RedMax=0."),"T",grid=True)
#exit()
c.execute("SELECT DISTINCT T,rpoe FROM models")
grid = c.fetchall()

c.execute("SELECT DISTINCT T FROM MODELS")
Ts=c.fetchall()

c.execute("SELECT DISTINCT rpoe FROM MODELS")
rpoes=c.fetchall()


resultS =[]
resultT =[]
linePlot =[]
lastT = 0.0
count = -1
for T,rpoe in grid:
    print rpoe,T
    answer = edOfMaxMass(  ("a>%s" % (avalue -.01), "a<%s" % (avalue +.01),
    "rpoe>%s" % (rpoe-.001), "rpoe<%s" % (rpoe+.001),
    "T>%s" % (T -.01), "T<%s" % (T +.01))  ,connection)
    if not T == lastT:
        linePlot.append([])
        lastT = T
        count +=1

    linePlot[count].append((1.0-answer['rpoe'],T,answer[plotVar]))
    if answer['RedMax'] > 0:
        resultT.append((1.0-answer['rpoe'],T,answer[plotVar]))
    else:
        resultS.append((1.0-answer['rpoe'],T,answer[plotVar]))


for plot in linePlot:
    plot = zip(*plot)
    mpl.plot(plot[0],plot[2],c=mpl.cm.jet(plot[1][0]/40.0))

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

mpl.scatter(resultS[0],resultS[2],c=resultS[1],s=30,marker='o')
mpl.scatter(resultT[0],resultT[2],c=resultT[1],s=30,marker='^')
#mpl.scatter(resultTov[0],resultTov[2],c=resultTov[1],s=40,marker='s')
colorLegend=mpl.colorbar()
colorLegend.set_label("Model Temperature (MeV)")
mpl.grid(True)
mpl.xlabel("1.0 - Rp/Re ")
if plotVar=="edMax":
    mpl.ylabel("Maximum energy density of model with largest mass")
if plotVar=="max":
    mpl.ylabel("Gravitational mass of model with largest mass")
mpl.title("Properties of model with largest mass Shen_14_0.5, a="+str(avalue))
mpl.show()