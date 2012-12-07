#!/usr/bin/python
import re

__author__ = 'jeff'


paramsFileString = '''Run type (1 for M_b-1) : __RunType__
                   EOS : __EOS__
       Radial Res. N_s : __Ns__
      Angular Res. N_u : __Nu__
     Orthog. Poly. N_l : __Nl__
Initial Cent E Density : __InitE__
  Final Cent E Density : __FinalE__
       Number of steps : __Nsteps__
        Data File Name : __RunName__.log
        Rotfunc        : __RotInvA__
        dumpdata       : vestigial_dump
        rpoe_goal      : __RPOEGoal__
'''

def writeFile(paramsDict,fileName):
    outputString=paramsFileString
    listOfReplacements=['RunType','EOS','Ns','Nu','Nl','InitE','FinalE',
                       'Nsteps','RunName','RotInvA','RPOEGoal']
    for replace in listOfReplacements:
        outputString = re.sub('__'+replace+'__',str(paramsDict[replace]),outputString)

    outFile=open(fileName,'w')
    outFile.write(outputString)
    outFile.close()
