import sys
from modelGeneration import runIDToDate

sys.path.append('./maxMassOrigFiles/')
#noinspection PyUnresolvedReferences
from sqlPlotRoutines import sequencePlot
import parseFiles
import os
import sqlite3
from matplotlib import pyplot as plt
from minimizeAlgorithm import *
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

__author__ = 'jeff'

print runIDToDate('2753073.37704')

databaseFile         = '/home/jeff/work/rotNSruns/models.db'

databaseExists =os.path.isfile(databaseFile)
connection=sqlite3.connect(databaseFile)

c=connection.cursor()
if not databaseExists:
    print "WARNING, DB FILE NOT PREVIOUSLY FOUND AT: "
    print databaseFile
    print "CREATING NEW ONE..."
    c.execute("CREATE TABLE models" + parseFiles.columnsString)
connection.commit()


##Test sequence plot
#sequencePlot(["edMax","baryMass"],c,["ToverW < .5","RedMax >= 0."],"ToverW")#,"models",marker='+')


###############################
# TEST BASIS & FIRST DERIV
vectors=[[1,0,0,0],
         [0,1,0.,0],
         [0,0,1,0],
         [0,0,0,1]]
b=basis( array(vectors) )
v2=[(1,1.),
    (1,-1.0001)]
b2=basis( array(v2)  )
#
###############################


###############################
# TEST STENCIL & FIRST DERIV
stenci = fdStencil(1, [5])

firstDeriv=deriv(dim=1, order=1, step=0.1,stencil=stenci,
                 coeffs=array([1,-8,0,8,-1])/12.,
                 name="5ptFirstDeriv")

#print firstDeriv
#
#firstDeriv.setupPoints(0.3)
#
#print firstDeriv.getPoints()
#firstDeriv.setStep(0.2)
#print firstDeriv.getPoints()
#
###############################

exit()
###############################
# TEST plotting and stepDown function
def func(a,T):
    return -3*(a*a + T*T/2. -a*T/2.) + (a*a*a*a*.7 + T*T*T*T*.34)



p0=(0.5,0.5)

delta=(.2,.2)

p1=stepDown(func,p0,delta)

xs=[]
ys=[]
zs=[]
for i in [p0,p1]:
    xs.append(i[0])
    ys.append(i[1])
    zs.append(func(i[0], i[1]))
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')


aas=linspace(-2., 2., 50)
Ts=linspace(-2., 2., 50)

X,Y=meshgrid(aas, Ts)

Z = func(X,Y)

ax.plot_wireframe(X, Y, Z, rstride=5, cstride=5, cmap=cm.YlGnBu_r)
ax.scatter(xs, ys, zs, s=100, color='r', marker='^')

#plt.show()
#
###############################


connection.commit()
connection.close()

exit()