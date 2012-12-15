#!/usr/bin/python

import os
import sys
sys.path.append('./maxMassOrigFiles/')
#noinspection PyUnresolvedReferences
from sqlPlotRoutines import sequencePlot
import sqlite3
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

#unc = hsModels.runOneModel
#hsModels.generateModels(func,paramsList)


connection.commit()
connection.close()

exit()

