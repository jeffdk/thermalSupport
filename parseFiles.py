#!/usr/bin/python

import os
from numpy import *

#  Omega_c    cJ/GMs^2    M/Ms       Eps_c      Mo/Ms      T/W        R_c        v/c     omg_c/Omg_c     rp       Z_p        Z_b        Z_f      h-direct   h-retro     e/m       Shed        RedMax     PradE     CoordRadE     RotT        GravPotW     PropM 
columnsString=''' (eos text, eosPrescription text,
              rollMid real, rollScale real,eosTmin real, T real,
              ye real, fixedQuantity text, fixedTarget real,
              a real,
              omega_c real,  J real, gravMass real, edMax real, baryMass real,
              ToverW real, arealR real, VoverC real, omg_c_over_Omg_c real,
              rpoe real,  Z_p real, Z_b real, Z_f real,  h_direct real,
              h_retro real, e_over_m real, shed real,  RedMax real,
              propRe real, coordRadE real, rotT real,
              gravPotW real, propM real,
              runType int, runID text, lineNum int) '''

#
def parseCstDataDirectoryIntoDB(dataDirName, sqliteCursor,tableName,runType):

    files = os.listdir(dataDirName)
    cwd = os.getcwd()
    os.chdir(dataDirName)
    entries=parseCstFileList(files)
    os.chdir(cwd)
    parseEntriesIntoDB(entries,sqliteCursor,tableName,runType)

def parseCstFileList(files,nonOutputRunParameters=()):
    #print "Processing " + str(len(files)) + " files: ", files
    #print " in current dir: ", os.getcwd()
    entries=[]
    for ind,file in enumerate(files):
        nonOutputParams = []

        print "nonOutputRunParameters[ind]: ", nonOutputRunParameters[ind]
        #ORDER MUST BE SAME AS IN COLUMNSTRING!
        nonOutputParams.append(nonOutputRunParameters[ind]['eos'])
        nonOutputParams.append(nonOutputRunParameters[ind]['eosPrescription'])
        nonOutputParams.append(nonOutputRunParameters[ind]['rollMid'])
        nonOutputParams.append(nonOutputRunParameters[ind]['rollScale'])
        nonOutputParams.append(nonOutputRunParameters[ind]['eosTmin'])
        nonOutputParams.append(nonOutputRunParameters[ind]['T'])
        nonOutputParams.append(nonOutputRunParameters[ind]['ye'])
        nonOutputParams.append(str(nonOutputRunParameters[ind]['fixedQuantity']))
        nonOutputParams.append(nonOutputRunParameters[ind]['fixedTarget'])
        nonOutputParams.append(nonOutputRunParameters[ind]['a'])
        fileHandle = open(file, 'r')
        #dump first 3 lines of comments
        fileHandle.readline(); fileHandle.readline(); fileHandle.readline()
        fileIsEmpty = True
#        print "before lines loop"
        for line in fileHandle:
            fileIsEmpty = False
            entry = line.split()
            for i in range(len(entry)):
                entry[i]=float(entry[i])

        #tack on data from the filename
            entry = nonOutputParams + entry

            nanFlag=0
            #remove entries with nans
            for i in range(len(entry)):
                if isinstance(entry[i],float):
                       if math.isnan(float(entry[i])):
                           nanFlag=1
            if nanFlag:
                print "ERROR, NAN IN FOLLOWING MODEL ENTRY:"
                print entry
                print "SKIPPING ADDITION OF THIS ENTRY!"
            else:
                entries.append(entry)
        if fileIsEmpty:
            print "WARNING, FILE: ", os.getcwd(), file, " CONTAINS NO DATA"

                
        fileHandle.close()
#    print "Entries processed: ", entries
    return entries


def parseEntriesIntoDB(entries, sqliteCursor, tableName, runType, runID):
    for i, entry in enumerate(entries):
        lineNum = i + 1
        entry.append(runType)
        entry.append(runID)
        entry.append(lineNum)
        #print "this entry: ", entry
        print "query: ", "INSERT INTO "+tableName+" VALUES "  + str(tuple(entry))
        sqliteCursor.execute("INSERT INTO "+tableName+" VALUES "
                                          + str(tuple(entry)) )
