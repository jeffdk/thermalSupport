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
databaseFile         = '/home/jeff/work/rotNSruns/shed_models.db'

databaseExists =os.path.isfile(databaseFile)
connection=sqlite3.connect(databaseFile)

c=connection.cursor()
if not databaseExists:
    print "WARNING, DB FILE NOT PREVIOUSLY FOUND AT: "
    print databaseFile
    print "CREATING NEW ONE..."
    c.execute("CREATE TABLE models" + parseFiles.columnsString)
connection.commit()


hsModels = modelGenerator(location_RotNS,location_MakeEosFile,specEosOptions,locationForRuns,3)
runParams = {'edMin':0.3,
             'edMax':4.0,
             'a':1.0,
             'rpoe':1.0,
             'rollMid':14.0,
             'rollScale' :  0.5,
             'T' : 10.0 }
def update(runParamz, ed, a=0.0, T=0.5):
    newDict={}
    runParamz.update( {'a':a})
    runParamz.update( {'T':T})
    runParamz.update( {'edMax':ed})
    newDict.update( runParamz)
    return newDict

edMaxVals =  linspace(0.1,4.0, 21)
aVals =      linspace(0.0,1.0, 6)
tempVals =   concatenate( (array([0.5]), linspace(10.,50.,5) ) )
print edMaxVals
print aVals
print tempVals

#paramsList=[  update(runParams,x) for x in [1.11] ]
paramsList=[runParams]
print len(paramsList),paramsList

func = hsModels.runRotNS
hsModels.generateModels(func,paramsList,connection)


connection.commit()
connection.close()

exit()

