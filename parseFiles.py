#!/usr/bin/python

import os
import sqlite3
from numpy import *

#  Omega_c    cJ/GMs^2    M/Ms       Eps_c      Mo/Ms      T/W        R_c        v/c     omg_c/Omg_c     rp       Z_p        Z_b        Z_f      h-direct   h-retro     e/m  Shed RedMax
columnsString=''' (eos text, tprofile text, a real, temp real, 
              omega_c real,  J real, gravMass real, edMax real, baryMass real,
              ToverW real, arealR real, VoverC real, omg_c_over_Omg_c real,
              rpoe real,  Z_p real,  h_direct real,
              h_retro real, e_over_m real, shed real, 
              RedMax real, propRe real) '''

def parseCstDataDirectory(dataDirName, sqliteCursor,tableName="models"):


    files=os.listdir(dataDirName)

    print "Processing " + str(len(files)) + " files "

    for file in files:
    
    #first extract parameter information contained in filename
        noSuffix=file.split('.log')[0]
        #print noSuffix

        filenameData=noSuffix.split('_')
        #remove a and T identifiers and make floats
        filenameData[2]=float(filenameData[2][1:])
        filenameData[3]=float(filenameData[3][1:])

        fileHandle=open(dataDirName+file,'r')  
        #dump first 3 lines of comments
        fileHandle.readline(); fileHandle.readline(); fileHandle.readline();

        for line in fileHandle:
            entry = line.split()
            #print entry
            #HACK OUT BROKEN Z_b & Z_f entry
            # only occurs sometimes, so if it is not present, we take otu BOTH
            # entries
            if(len(entry)>18):
                takeOutVal=13
            else:
                takeOutVal=12
            tmp   = entry[takeOutVal:]
            entry = entry[0:11]
            entry = entry + tmp
            #make data floats
            for i in range(len(entry)):
                entry[i]=float(entry[i])

        #tack on data from the filename   
            entry = filenameData+ entry

            nanFlag=0
            #remove entries with nans
            for i in range(len(entry)):
                if(isinstance(entry[i],float)):
                       if math.isnan(float(entry[i])):
                           nanFlag=1
            if nanFlag:
                print "ERROR, NAN IN FOLLOWING MODEL ENTRY:"
                print entry
                print "SKIPPING ADDITION OF THIS ENTRY!"
            else:
                sqliteCursor.execute("INSERT INTO "+tableName+" VALUES" 
                                     + str(tuple(entry)) )


        fileHandle.close()
