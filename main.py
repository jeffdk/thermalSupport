#!/usr/bin/python

import os
import sys
sys.path.append('./maxMassOrigFiles/')
#noinspection PyUnresolvedReferences
from sqlPlotRoutines import sequencePlot
import sqlite3
from matplotlib import pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from numpy import *
from minimizeAlgorithm import *
import parseFiles
from modelGeneration import modelGenerator
import writeParametersFile
from pickleHack import *

location_MakeEosFile = "/home/jeff/spec/Hydro/EquationOfState/Executables/MakeRotNSeosfile"
location_RotNS       = "/home/jeff/work/RotNS/RotNS"
specEosOptions       = "Tabulated(filename= /home/jeff/work/HS_Tabulated.dat )"
locationForRuns      = "/home/jeff/work/rotNSruns"
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


hsModels = modelGenerator(location_RotNS,location_MakeEosFile,specEosOptions,locationForRuns,c)
runParams = {'edMax':0.3325,
             'a':1.0,
             'rpoe':1.0,
             'rollMid':14.0,
             'rollScale' :  0.5,
             'T' : 10.0 }
runParams2 = {'edMax':0.462,
             'a':1.0,
             'rpoe':0.5,
             'rollMid':14.0,
             'rollScale' :  0.5,
             'T' : 10.0 }
def update(runParamz, ed, a, T):
    newDict={}
    runParamz.update( {'a':a})
    runParamz.update( {'T':T})
    runParamz.update( {'edMax':ed})
    newDict.update( runParamz)
    return newDict
print hsModels.determineRunName(runParams2)
edMaxVals =  linspace(0.1,4.0, 21)
aVals =      linspace(0.0,1.0, 6)
tempVals =   concatenate( (array([0.5]), linspace(10.,50.,5) ) )
print edMaxVals
print aVals
print tempVals

paramsList=[  update(runParams2,x,a,T) for x in edMaxVals for a in aVals for T in tempVals  ]
print len(paramsList),paramsList
exit()
func = hsModels.runOneModel
hsModels.generateModels(func,paramsList)

sequencePlot(["edMax","baryMass"],c,["ToverW < .5","a > 0."])

connection.commit()
connection.close()

exit()
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
