#!/usr/bin/python
import os
import subprocess
import writeParametersFile

__author__ = 'jeff'



class modelGenerator():
    rotNS_location = ""
    makeEosFile_location = ""
    specEosOptions = ""
    rotNS_resolutionParams={} #Default is Ns = 800, Nu = 800, Nl = 30
    rotNS_EosType = "PP"      #eos PP causes RotNS to look for EOS/EOS.PP
    requestQueue=[]
    rotNS_numSteps = 20       # number of steps to get to target RPOEGoal
    default_Tmin   = 0.5      # default tmin for MakeRotNSeosfile
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

    def runOneModel(self, inputParams, runID):
        assert isinstance(inputParams, dict)
        #30 is run-type for running one model
        rotNS_params = {'RunType':30, 'EOS':self.rotNS_EosType,'Nsteps':self.rotNS_numSteps}
        #Add resolution information
        rotNS_params.update(self.rotNS_resolutionParams)
        runName = "oneModel"

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
        subprocess.call("./RotNS < Parameters.input",shell=True)
        os.chdir("../")
    def hardDelete(self,runID):

        assert isinstance(runID, str)
        if '/' in runID:
            exit("You GONE DUN TRYIN TO ERASE A NON LOCAL DIRECTORY!!")
        subprocess.call(["rm", "-rf", runID])