#!/usr/bin/python
import multiprocessing
import os
import random
import sqlite3
import subprocess
import datetime
import numpy.random
import time
from parseFiles import parseCstFileList
import writeParametersFile

__author__ = 'jeff'
def calculate(func, args):
    result = func(*args)
    #print "calculate, args: ", args
    return '%s says that %s%s = %s' %\
           (multiprocessing.current_process().name, func.__name__, args, result)
def calculateStar(args):
    #print "calculateStar, args: ", args
    return calculate(*args)


class modelGenerator(object):
    rotNS_location = ""
    makeEosFile_location = ""
    specEosOptions = ""
    rotNS_resolutionParams={} #Default is Ns = 800, Nu = 800, Nl = 30
    rotNS_EosType = "PP"      #eos PP causes RotNS to look for EOS/EOS.PP
    requestQueue=[]
    rotNS_numSteps = 20       # number of steps to get to target RPOEGoal
    default_Tmin   = 0.5      # default tmin for MakeRotNSeosfile
    num_cpus = 2 #multiprocessing.cpu_count()
    locationForRuns=""
    def __init__(self,rotNS_location,makeEosFile_location,
                 specEosOptions,locationForRuns, sqliteCursor, rotNS_resolutionParams=(800,800,30)):
        """
        rotNS_location:         string
        makeEosFile_location:   string
        specEosOptions:         string
        rotNS_resolutionParams: tuple in (Ns,Nu,Nl) format
        """
        assert isinstance(rotNS_location, str)
        self.rotNS_location=rotNS_location
        assert isinstance(makeEosFile_location, str)
        self.makeEosFile_location=makeEosFile_location
        assert isinstance(specEosOptions, str)
        self.specEosOptions=specEosOptions
        assert isinstance(locationForRuns, str)
        self.locationForRuns=locationForRuns

        assert isinstance(rotNS_resolutionParams, tuple)
        self.rotNS_resolutionParams['Ns']=rotNS_resolutionParams[0]
        self.rotNS_resolutionParams['Nu']=rotNS_resolutionParams[1]
        self.rotNS_resolutionParams['Nl']=rotNS_resolutionParams[2]

        assert isinstance(sqliteCursor, sqlite3.Cursor)
        self.sqliteCursor=sqliteCursor
        
    def runOneModel(self, inputParams, runID):
        assert isinstance(inputParams, dict)
        #30 is run-type for running one model
        rotNS_params = {'RunType':30,
                        'EOS':self.rotNS_EosType,
                        'Nsteps':self.rotNS_numSteps}
        #Add resolution information
        rotNS_params.update(self.rotNS_resolutionParams)
        runName = self.determineRunName(inputParams)
        
        os.mkdir(runID)
        os.chdir(runID)
        
        ####
        # Do EOS generation here
        subprocess.call(["cp", self.makeEosFile_location, "./"])
        
        makeEosFileArgs={'-eos-opts'     : self.specEosOptions,
                         '-roll-midpoint': inputParams['roll-midpoint'],
                         '-roll-scale'   : inputParams['roll-scale'],
                         '-roll-tmin'    : self.default_Tmin,
                         '-roll-tmax'    : inputParams['T'] }
        argList=[str(arg) for item in makeEosFileArgs.items() for arg in item ]

        subprocess.call(["./MakeRotNSeosfile"] + argList )
        
        subprocess.call(["mkdir", "EOS"])
        subprocess.call(["cp", "output.EOS", "EOS/EOS.PP"])

        centralEnergyDensity = inputParams['CED']
        rotNS_params.update({'InitE':centralEnergyDensity*1.1,
                             'FinalE':centralEnergyDensity })
        rotNS_params.update({'RunName':runName,
                             'RotInvA':inputParams['a'],
                             'RPOEGoal':inputParams['rpoe'] })

        writeParametersFile.writeFile(rotNS_params,'Parameters.input')

        subprocess.call(["cp", self.rotNS_location, "./"])
        print "MakeRotNSeosfile done!  Now running  RotNs, runID: ", runID
        subprocess.call("./RotNS < Parameters.input > run.log ", shell=True)
        val = parseCstFileList([runName],self.sqliteConnection)
        os.chdir("../")
        return val

    def tester(self, dog,cat):
        print dog, cat
        secs = 1#2* random.random()
        time.sleep(secs)
        return secs

    def hardDelete(self,runID):

        assert isinstance(runID, str)
        if '/' in runID:
            exit("You GONE DUN TRYIN TO ERASE A NON LOCAL DIRECTORY!!")
        subprocess.call(["rm", "-rf", runID])

    def generateModels(self, f, listOfInputParams):
        currentDirectory=os.getcwd()
        os.chdir(self.locationForRuns)
        PROCESSES = self.num_cpus
        print 'Creating pool with %d processes\n' % PROCESSES
        pool = multiprocessing.Pool(PROCESSES)
        print 'pool = %s' % pool
        print

        TASKS, TASKS2 = [],[]
        for inputParams in listOfInputParams:
            #runID is seconds elapsed since my 28th birthday
            runID = str( (datetime.datetime.now() - datetime.datetime(2012,11,11)).total_seconds())
            #print (runID,  inputParams,runID )
            TASKS.append( (f,  ( inputParams,runID) )  )
            TASKS2.append(   ( inputParams,runID) )
        start = datetime.datetime.now()
        #        print TASKS2
        result = pool.imap_unordered(calculateStar, TASKS)
        #result = pool.imap_unordered(f, TASKS2)
        for i in result:
            print i
        pool.close()
        pool.join()
        print "DIFFERENCE: ", datetime.datetime.now()- start

        os.chdir(currentDirectory)



    def determineRunName(self, inputParams):
        result = ""
        #following line gets the EOS table name
        result += self.specEosOptions.split('/')[-1].split('_')[0]
        result += '_mid'
        result += str(inputParams['roll-midpoint'])
        result += '_scale'
        result += str(inputParams['roll-scale'])
        result += '_a'
        result += str(inputParams['a'])
        result += '_T'
        result += str(inputParams['T'])
        return result


