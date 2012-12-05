#!/usr/bin/python


import os
import sqlite3
import re
from matplotlib import pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from numpy import *
from minimizeAlgorithm import *
from modelGeneration import modelGenerator
import writeParametersFile


location_MakeEosFile = "/home/jeff/spec/Hydro/EquationOfState/Executables/MakeRotNSeosfile"
location_RotNS       = "/home/jeff/work/RotNS/RotNS"
specEosOptions       = "Tabulated(filename= /home/jeff/work/HS_Tabulated.dat )"

hsModels = modelGenerator(location_RotNS,location_MakeEosFile,specEosOptions)



###############################
# TEST STENCIL & FIRST DERIV
stenci = fdStencil(1, [5])



firstDeriv=deriv(dim=1, order=1, step=0.1,stencil=stenci,
                 coeffs=array([1,-8,0,8,-1])/12.,
                 name="5ptFirstDeriv")


print firstDeriv

firstDeriv.setupPoints(0.3)

print firstDeriv.getPoints()
firstDeriv.setStep(0.2)
print firstDeriv.getPoints()
#
###############################


###############################
# TEST writeParametersFile
params=['EOS','Ns','Nu','Nl','InitE','FinalE','Nsteps','RunName','RotInvA','RPOEGoal']
paramDict={}
for i in params:
    paramDict[i]='dog'
writeParametersFile.writeFile(paramDict,'outFile.input')
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

plt.show()
#
###############################