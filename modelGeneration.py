#!/usr/bin/python
import multiprocessing
import os
import random
import subprocess
import datetime
import numpy.random
import time
import writeParametersFile

__author__ = 'jeff'
def calculate(func, args):
    result = func(*args)
    return '%s says that %s%s = %s' %\
           (multiprocessing.current_process().name, func.__name__, args, result)
def calculateStar(args):
    return calculate(*args)
def tester( dog,cat):
    print dog, cat
    secs = 1 # random.random()
    time.sleep(secs)
    return secs

class modelGenerator(object):
    rotNS_location = ""
    makeEosFile_location = ""
    specEosOptions = ""
    rotNS_resolutionParams={} #Default is Ns = 800, Nu = 800, Nl = 30
    rotNS_EosType = "PP"      #eos PP causes RotNS to look for EOS/EOS.PP
    requestQueue=[]
    rotNS_numSteps = 20       # number of steps to get to target RPOEGoal
    default_Tmin   = 0.5      # default tmin for MakeRotNSeosfile
    num_cpus = multiprocessing.cpu_count()
    def __init__(self,rotNS_location,makeEosFile_location,
                 specEosOptions, rotNS_resolutionParams=(800,800,30)):
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

        assert isinstance(rotNS_resolutionParams, tuple)
        self.rotNS_resolutionParams['Ns']=rotNS_resolutionParams[0]
        self.rotNS_resolutionParams['Nu']=rotNS_resolutionParams[1]
        self.rotNS_resolutionParams['Nl']=rotNS_resolutionParams[2]


    def hardDelete(self,runID):

        assert isinstance(runID, str)
        if '/' in runID:
            exit("You GONE DUN TRYIN TO ERASE A NON LOCAL DIRECTORY!!")
        subprocess.call(["rm", "-rf", runID])

    def generateModels(self, f, listOfInputParams):


        PROCESSES = self.num_cpus
        print 'Creating pool with %d processes\n' % PROCESSES
        pool = multiprocessing.Pool(PROCESSES)
        print 'pool = %s' % pool
        print

        task_queue = multiprocessing.JoinableQueue()
        def f_init(q):
            f.q = q

        TASKS = []
        for inputParams in listOfInputParams:
            #runID is seconds elapsed since my 28th birthday
            runID = str( (datetime.datetime.now() - datetime.datetime(2012,11,11)).total_seconds())
            print (runID,  inputParams,runID )
            TASKS.append( (f,  ( inputParams,runID) )  )

        start = datetime.datetime.now()
        print TASKS
        result = pool.imap_unordered(calculateStar, TASKS)

        for i in result:
            print i

        print "DIFFERENCE: ", datetime.datetime.now()- start

        #results = [pool.apply(f, args) for args in argList]
        #print results

def runOneModel(generatorObject, inputParams, runID):
    assert isinstance(inputParams, dict)
    #30 is run-type for running one model
    rotNS_params = {'RunType':30,
                    'EOS':generatorObject.rotNS_EosType,
                    'Nsteps':generatorObject.rotNS_numSteps}
    #Add resolution information
    rotNS_params.update(generatorObject.rotNS_resolutionParams)
    runName = "oneModel"

    os.mkdir(runID)
    os.chdir(runID)

    ####
    # Do EOS generation here
    subprocess.call(["cp", generatorObject.makeEosFile_location, "./"])

    makeEosFileArgs={'-eos-opts'     : generatorObject.specEosOptions,
                     '-roll-midpoint': inputParams['roll-midpoint'],
                     '-roll-scale'   : inputParams['roll-scale'],
                     '-roll-tmin'    : generatorObject.default_Tmin,
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

    subprocess.call(["cp", generatorObject.rotNS_location, "./"])
    subprocess.call("./RotNS < Parameters.input",shell=True)
    os.chdir("../")