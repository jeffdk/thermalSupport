import writeParametersFile
from modelGeneration import modelGenerator

__author__ = 'jeff'

argList= [] #[ (x,y) for x in range(4) for y in range(4)]
#hsModels.runOneModel(runParams,"blah")
#hsModels.hardDelete("blah")
#func = hsModels.tester
#hsModels.generateModels(func,argList)

###############################
# TEST writeParametersFile
params=['RunType','EOS','Ns','Nu','Nl','InitE','FinalE','Nsteps','RunName','RotInvA','RPOEGoal']
paramDict={}
for i in params:
    paramDict[i]='dog'
writeParametersFile.writeFile(paramDict,'outFile.input')
#
###############################
