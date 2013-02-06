

import sys
import sqlite3
import matplotlib
matplotlib.use( 'WXAgg' )
import matplotlib.pyplot as mpl
from mpl_toolkits.mplot3d import Axes3D
import numpy
from sqlUtils import queryDBGivenParams, getColumnHeaders

sys.path.append('./maxMassOrigFiles/')
#noinspection PyUnresolvedReferences
from sqlPlotRoutines import sequencePlot, nearValueFilter
font = {'size'   : 8}


matplotlib.rc('font', **font)



databaseFile         = '/home/jeff/work/rotNSruns/macroRun.db'
connection=sqlite3.connect(databaseFile)
c=connection.cursor()
c.execute("SELECT DISTINCT T FROM MODELS")
Ts=c.fetchall()
print "TS: ", Ts
c.execute("SELECT DISTINCT edMax FROM MODELS ORDER BY edMax")
edMaxes=c.fetchall()
print edMaxes

T=0.5
filtersT = nearValueFilter("T",T,0.001)#("T>%s" % (T -.01), "T<%s" % (T +.01))
a=0.7
filtersA = nearValueFilter("a",a,0.001) #("a>%s" % (a -.001), "a<%s" % (a +.001))
filtersEd = ("edMax>1.5e14",)# nearValueFilter("edMax",528787878700000.0,0.001 )
filters=filtersA+filtersT+filtersEd



fields=getColumnHeaders("models",c)
fields=fields.split(', ')
colorByField="edMax"
print fields
fieldList=['omega_c', 'J', 'gravMass', 'edMax', 'baryMass', 'ToverW', 'arealR',
           'VoverC', 'omg_c_over_Omg_c', 'rpoe', 'Z_p', 'Z_b', 'Z_f', 'h_direct',
           'h_retro', 'e_over_m', 'shed', 'RedMax', 'propRe', 'coordRadE', 'rotT',
           'gravPotW', 'propM']

for xaxis in fieldList:
    mpl.figure()
    for i,field in enumerate(fieldList):
        mpl.subplot(4,6,i+1)
        sequencePlot([xaxis,field],c,filters,colorBy=colorByField,suppressShow=True,edgecolors='none',s=5)
    mpl.subplot(4,6,24)
    mpl.tight_layout(pad=1.05,h_pad=0.1,w_pad=0.1)
    mpl.subplots_adjust(left=0.04, bottom=0.04, right=0.98, top=0.98, wspace=0.05)
    fig=mpl.gcf()
    fig.set_size_inches(24,13.5)

    sequencePlot([xaxis,"ToverW"],c,filters,colorBy=colorByField,suppressShow=True,forceColorbar=True)
    fig.savefig("plots/cb-"+colorByField+"-"+xaxis+"VS-a"+str(a)+"-T"+str(T) +".png")
    fig.clf()

exit()

filters=("RedMax=0",) + filtersT
valuesS = queryDBGivenParams("a,edMax,rpoe,RedMax",(),c,"models",filters)
print "Got spheroids, ", len(valuesS)
filters=("RedMax>0",) + filtersT
valuesT = queryDBGivenParams("a,edMax,rpoe,RedMax",(),c,"models",filters)
print "Got toroids, ", len(valuesT)

#print valuesT[:10]
#print valuesS[:10]

valuesS=zip(*valuesS)
valuesT=zip(*valuesT)

#print valuesT[0]

fig=mpl.figure()
ax = fig.add_subplot(111,projection='3d')

#ax.scatter(*valuesT,color='r',marker='.',s=1, label="toroid")
#ax.scatter(valuesS[0],valuesS[1],valuesS[2],color='g',marker='.', s=1, label="tov")

vectCm=numpy.frompyfunc(matplotlib.pyplot.cm.jet,1,4)
valuesT[3] = vectCm(numpy.array(valuesT[3]))
valuesT[3] = zip(*valuesT[3])
ax.scatter(valuesT[0],valuesT[1],valuesT[2], color=valuesT[3],#color='b',
    marker='.', label="toroid") #markersize=10,linestyle='None',
ax.plot3D(valuesS[0],valuesS[1],valuesS[2],color='w',marker='.', markersize=1,
linestyle='None', label="tov")
mpl.show()
