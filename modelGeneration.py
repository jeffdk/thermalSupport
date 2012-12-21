"""
 Defines class and helper functions for generating RotNS runs
"""
import glob
import multiprocessing
import os
import random
import sqlite3
import subprocess
import datetime
import time
from parseFiles import parseCstFileList, parseEntriesIntoDB
from sqlUtils import queryDBGivenParams
import writeParametersFile

__author__ = 'jeff'
def calculate(func, args):
    result = func(*args)
#    print '%s says that %s%s = %s' %\
#           (multiprocessing.current_process().name, func.__name__, args, result)
    print "Multiprocessing %s has returned a result for %s" %\
        (multiprocessing.current_process().name, func.__name__)
    return result
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
    num_cpus = multiprocessing.cpu_count()
    locationForRuns=""
    tableName = "models"
    cleanUpRuns = True
    runType = 30
    def __init__(self,rotNS_location,makeEosFile_location,
                 specEosOptions,locationForRuns, runType=30, tableName="models",
                 rotNS_resolutionParams=(800,800,30)):
        """
        rotNS_location:         string
        makeEosFile_location:   string
        specEosOptions:         string
        locationForRuns:        string   work directory to do RotNS runs in
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

        assert isinstance(runType, int)
        self.runType=runType

        assert isinstance(tableName, str)
        self.tableName=tableName
        
    def runRotNS(self, inputParams, runID):
        assert isinstance(inputParams, dict)

        rotNS_params = {'RunType':self.runType,
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
                         '-roll-midpoint': inputParams['rollMid'],
                         '-roll-scale'   : inputParams['rollScale'],
                         '-roll-tmin'    : self.default_Tmin,
                         '-roll-tmax'    : inputParams['T'] }
        argList=[str(arg) for item in makeEosFileArgs.items() for arg in item ]

        subprocess.call(["./MakeRotNSeosfile"] + argList )
        
        subprocess.call(["mkdir", "EOS"])
        subprocess.call(["cp", "output.EOS", "EOS/EOS.PP"])

        rotNS_params.update({'RunName':runName,
                             'RotInvA':inputParams['a'],
                             'RPOEGoal':inputParams['rpoe'] })
        #Sets the density parameters differently depending on run type
        rotNS_params = self.setDensityRange(inputParams,rotNS_params)
        writeParametersFile.writeFile(rotNS_params,'Parameters.input')

        subprocess.call(["cp", self.rotNS_location, "./"])
        print "MakeRotNSeosfile done!  Now running  RotNs, runID: ", runID
        subprocess.call("./RotNS < Parameters.input > run.log ", shell=True)
        nonOutputParams=inputParams.copy()
        nonOutputParams['eos']=self.getEosName()
        entries = parseCstFileList([runName],[nonOutputParams])

        if self.cleanUpRuns:
            cleanUpAfterRun()

        os.chdir("../")
        #print entries, runID
        return entries,runID

    def setDensityRange(self,inputParams, rotNS_params):
        """
        :rtype : dict rotNS_params
        """
        maxEnergyDensity = inputParams['edMax']
        # 30 is runType 'one model' and only uses the final energy density!
        if self.runType == 30:
            rotNS_params.update({'InitE':maxEnergyDensity*1.1,
                                 'FinalE':maxEnergyDensity })
        # 3 is runType 'mass-shed' and calculates mass shedding sequences at a variety of densities
        if self.runType == 3 :
            minEnergyDensity = inputParams['edMin']
            #we may also want to set the number of steps
            if 'Nsteps' in inputParams:
                self.rotNS_numSteps = inputParams['Nsteps']
            rotNS_params.update({'InitE':minEnergyDensity,
                                 'FinalE':maxEnergyDensity,
                                 'Nsteps':self.rotNS_numSteps})
        return rotNS_params

    def tester(self, dog,cat):
        """tester is for working out how to use multithreading via multiprocess"""
        print dog, cat
        secs = 1 + 1.* random.random()
        time.sleep(secs)
        return secs

    def hardDelete(self,runID):
        """USE WITH CAUTION: runs rm -rf in current directory on its argument!"""
        assert isinstance(runID, str)
        if '/' in runID:
            exit("You GONE DUN TRYIN TO ERASE A NON LOCAL DIRECTORY!!")
        subprocess.call(["rm", "-rf", runID])

    def generateModels(self, f, listOfInputParams,sqliteConnection):
        assert isinstance(sqliteConnection,sqlite3.Connection)
        currentDirectory=os.getcwd()
        os.chdir(self.locationForRuns)
        PROCESSES = self.num_cpus
        print 'Creating pool with %d processes\n' % PROCESSES
        pool = multiprocessing.Pool(PROCESSES)
        print 'pool = %s' % pool
        print
        cursor = sqliteConnection.cursor()
        TASKS = []
        ids = []
        for inputParams in listOfInputParams:
            
            #If we are provided it, override Nsteps
            #TODO: fix bad way of setting Nsteps!
            if 'Nsteps' in inputParams:
                self.rotNS_numSteps= inputParams['Nsteps']
                del inputParams['Nsteps']
            existingRunID = self.checkIfRunExistsInDB(inputParams,cursor)
            if existingRunID:
                continue

            runID = generateRunID() 
        
            if runID in ids:
                print "runID collision!"
                time.sleep(0.01)
                runID = generateRunID()
            ids.append(runID)

            #print runID
            TASKS.append( (f,  ( inputParams,runID) )  )
        print "Now queued %s runs for multithreaded execution..." %str(len(ids))
        start = datetime.datetime.now()
        result = pool.imap_unordered(calculateStar, TASKS)

        for i in result:
            #print i 
            entries, runID = i
            if entries:
                parseEntriesIntoDB(entries, cursor,self.tableName,self.runType,runID=runID)
            else: 
                print "ERROR FOR LAST MODEL, RUNID: ",  runID
        pool.close()
        pool.join()
        sqliteConnection.commit()
        print "DIFFERENCE: ", datetime.datetime.now()- start
        
        del pool

        os.chdir(currentDirectory)

    def checkIfRunExistsInDB(self,inputParams,cursor):
        myParams = inputParams.copy()
        myParams['eos'] = self.getEosName()

        #edMin not relevant for run type one model
        #TODO: modify checkIfRunExistsInDB to work properly with mass shed sequences!
        if self.runType == 30 and 'edMin' in myParams:
            del myParams['edMin']
        elif self.runType ==3 and  'edMin' in myParams:
            del myParams['edMin']
        elif self.runType ==3 and  'Nsteps' in myParams:
            del myParams['Nsteps']

        listResult =queryDBGivenParams('runID',myParams,cursor,self.tableName)

        if listResult:
            if len(listResult) > 1 or len(listResult[0]) > 1:
                print "Wow, this entry: "
                print inputParams
                print "exists more than once in the database! Should not be possible..."
                #raise AssertionError
            result = listResult[0][0]
            print "----WARNING!----"
            print "  Parameters: "
            print inputParams
            print " Have already been run, run ID: ", result
            print

        return listResult

    def determineRunName(self, inputParams):
        result = ""
        result += self.getEosName()
        result += '_mid'
        result += str(inputParams['rollMid'])[:3]
        result += '_scale'
        result += str(inputParams['rollScale'])[:3]
        result += '_a'
        result += str(inputParams['a'])[:3]
        result += '_T'
        result += str(inputParams['T'])[:3]
        result = result[:32]   #RotNS wont write an output file with > 30 chars
        return result

    def getEosName(self):
        #following line gets the EOS table name by getting the string
        # AFTER the last / and before the first _
        return self.specEosOptions.split('/')[-1].split('_')[0]
#END class modelGenerator

def generateRunID():
   #runID is seconds elapsed since my 28th birthday=
    runID = str( (datetime.datetime.now() 
                  - datetime.datetime(2012,11,11)).total_seconds())
    return runID

def runIDToDate(runID):
    return datetime.datetime(2012,11,11) + datetime.timedelta( seconds=float(runID) )


def cleanUpAfterRun():
    print('Cleaning up in dir ' + os.getcwd() +'... ')
    outdataToDelete=glob.glob("outdata*")
    subprocess.call(["rm"] + outdataToDelete)
    subprocess.call(["rm",  "output.EOS"])
    subprocess.call(["rm",  "RotNS.state"])
    subprocess.call(["rm",  "RotNS"])
    subprocess.call(["rm",  "MakeRotNSeosfile"])
