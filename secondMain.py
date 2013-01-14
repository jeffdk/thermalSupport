

import sys
from maxMassSurfPlotter import surfacePlotter
from modelGeneration import runIDToDate, modelGenerator
import parseFiles
import os
import sqlite3
from minimizeAlgorithm import *
import numpy as np
from trackRecorder import trackPlotter

sys.path.append('./maxMassOrigFiles/')
#noinspection PyUnresolvedReferences
from sqlPlotRoutines import sequencePlot
MPL_ON = False
if MPL_ON:
    from matplotlib import pyplot as plt
    from matplotlib import cm
    from mpl_toolkits.mplot3d import Axes3D
MYAVI_ON = True
if MYAVI_ON:
    import mayavi.mlab as mlab

from pickleHack import *
__author__ = 'jeff'


location_MakeEosFile = "/home/jeff/spec/Hydro/EquationOfState/Executables/MakeRotNSeosfile"
location_RotNS       = "/home/jeff/work/RotNS/RotNS"
specEosOptions       = "Tabulated(filename= /home/jeff/work/HS_Tabulated.dat )"
locationForRuns      = "/home/jeff/work/rotNSruns"
databaseFile         = '/home/jeff/work/rotNSruns/stepDown_models.db'

dbfileList=['/home/jeff/work/rotNSruns/tester30.0.step.' + str(i) +'.db' for i in [0.5,1.0,2.0]]

dbfileList=['/home/jeff/work/rotNSruns/jan12.30.0.s0.25.cb.db',
            '/home/jeff/work/rotNSruns/jan12.30.0.s0.5.cb.db',
            '/home/jeff/work/rotNSruns/jan12.30.0.s1.cb.db']
#dbfileList=['/home/jeff/work/rotNSruns/tester30.0.db']
dbfileList=['/home/jeff/work/rotNSruns/jan12.30.0.s1.cb.db',
            '/home/jeff/work/rotNSruns/jan10.30.0.db']


TasString = "31.2222222222222"

splotter = surfacePlotter("/home/jeff/work/rotNSruns/mass-shed-models.db", ('a','edMax'), 'rpoe')

splotter.plotWithCondition(" T < 32 AND T > 29 ")
#mlab.show()
plotter=trackPlotter(dbfileList,"track",("a","edMax","rpoe","baryMass","RedMax"))
plotter.trackPlotter(("a","edMax","rpoe"),('ToverW','baryMass','J'),True)

splotter.dbConnection.close()

#dbfileList=['/home/jeff/work/rotNSruns/stepDown_models.db']
#plotter2=trackPlotter(dbfileList,"track",("baryMass","RedMax"))
#plotter2.trackPlotter(("a","edMax","rpoe"))
exit()

databaseExists =os.path.isfile(databaseFile)
connection=sqlite3.connect(databaseFile)

c=connection.cursor()
if not databaseExists:
    print "WARNING, DB FILE NOT PREVIOUSLY FOUND AT: "
    print databaseFile
    print "CREATING NEW ONE..."
    c.execute("CREATE TABLE models" + parseFiles.columnsString)
connection.commit()


hsModels = modelGenerator(location_RotNS,location_MakeEosFile,specEosOptions,locationForRuns,30)


##Test sequence plot
#sequencePlot(["edMax","baryMass"],c,["ToverW < .5","RedMax >= 0."],"ToverW")#,"models",marker='+')


###############################
# TEST BASIS & FIRST DERIV
vectors=[[1,0,0,0],
         [0,1,0.,0],
         [0,0,1,0],
         [0,0,0,1]]
b=basis( array(vectors) )
v2=[(1,1.,1.,1),

    (0,0,0.,1.)]

new = removeSubspace(b,array(v2))
print "b with subspace v2 removed:",new
#b2=basis( array(v2)  )
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
p0=(30.0,1.0,1.0,0.6)
#p0=(30.50089376,   0.55406129,   1.10895734,   0.65099777)
#p0=(31.02882031,0.18161429,1.17609837,0.62054172)

delta=array((0.3,0.01,0.005,0.01)) * 1.
stationaryParams = {'rollMid':14.0,
                    'rollScale' :  0.5
                    }
pointlist, funcNamesList,gradientDictList,fixedSubspaceList,\
            projectedGradientList, normAfterProjectionList = \
steepestDescent("ToverW",("baryMass","J"),b,firstDeriv,p0,delta,connection,hsModels,stationaryParams,50)



print pointlist
print
print funcNamesList
print
print gradientDictList
print
print fixedSubspaceList
print
print projectedGradientList
print
print normAfterProjectionList

print len(pointlist[:-1])
print
print len(funcNamesList)
print
print len(gradientDictList)
print
print len(fixedSubspaceList)
print
print len(projectedGradientList)
print
print len(normAfterProjectionList)

xs,ys,zs,us,vs,ws= ([] for i in range(6))
baryX,baryY,baryZ,jx,jy,jz, tx,ty,tz = ([] for i in range(9))
for i,points in enumerate(pointlist[:-1]):
    xs.append(points[1])
    ys.append(points[2])
    zs.append(points[3])

    us.append(-projectedGradientList[i][1])
    vs.append(-projectedGradientList[i][2])
    ws.append(-projectedGradientList[i][3])

    baryX.append(gradientDictList[i]['baryMass'][1])
    baryY.append(gradientDictList[i]['baryMass'][2])
    baryZ.append(gradientDictList[i]['baryMass'][3])

    jx.append(gradientDictList[i]['J'][1])
    jy.append(gradientDictList[i]['J'][2])
    jz.append(gradientDictList[i]['J'][3])

    tx.append(gradientDictList[i]['ToverW'][1])
    ty.append(gradientDictList[i]['ToverW'][2])
    tz.append(gradientDictList[i]['ToverW'][3])

f=mlab.figure(bgcolor=(.5,.5,.5))


j=mlab.quiver3d(xs,ys,zs,jx,jy,jz, scale_factor=.002,color=(1,0,0),name='J')
m=mlab.quiver3d(xs,ys,zs,baryX,baryY,baryZ, scale_factor=.013,color=(0,0,1),name='Mb')
t=mlab.quiver3d(xs,ys,zs,tx,ty,tz, scale_factor=.1,color=(0,1,0),name='T/W')
pt=mlab.quiver3d(xs,ys,zs,us,vs,ws, scale_factor=.01,color=(1,1,1),name='projT/W')
mlab.text(.01,.2,'J   ',color=(1,0,0),width=0.1)
mlab.text(.01,.4,'Mb  ',color=(0,0,1),width=0.1)
mlab.text(.01,.5,'T/W ',color=(0,1,0),width=0.1)
mlab.text(.01,.6,'-projT/W',color=(1,1,1),width=0.1)
mlab.title("Gradients along track")


mlab.axes(color=(.7,.7,.7),xlabel='a')
mlab.xlabel('a')
mlab.ylabel('edMax')
mlab.zlabel('rpoe')

mlab.show()

exit()
###############################
# TEST plotting and stepDown function
def func(a,T):
    return -2*(a*a + T*T/2. -a*T/2.) + (a*a*a*a*.7 + T*T*T*T*.34)



p0=(.10,.10,.15)
p1=(.30,.20,.10)

xs=[]
ys=[]
zs=[]
for i in [p0,p1]:
    xs.append(i[0])
    ys.append(i[1])
    zs.append(func(i[0], i[1]))



aas=linspace(-1.8, 1.8, 50)
Ts=linspace(-1.8, 1.8, 50)

Y,X=meshgrid(aas, Ts)

Z = func(X,Y)

if MPL_ON:
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_wireframe(X, Y, Z, rstride=5, cstride=5, cmap=cm.YlGnBu_r)
    ax.scatter(xs, ys, zs, s=100, color='r', marker='^')
    plt.show()
    exit()
#
###############################
if MYAVI_ON:
    mlab.points3d(xs,ys,zs,color=(1,0,0.5))
    s = mlab.surf(X,Y,func)
    mlab.show()

    connection.commit()
    connection.close()

exit()
