

import glob
import os
import sqlite3
from parseFiles import *


databaseFile         = '/home/jeff/work/rotNSruns/stiffness-test-alt.db'
connection=sqlite3.connect(databaseFile)
c=connection.cursor()
#c.execute("CREATE TABLE models" + columnsString)
currentDirectory=os.getcwd()
os.chdir("/home/jeff/work/rotNSruns/")

directoryBase="6002247.*"
eosBase="Gam3"
nonOutputRunParameters=[{}]
nonOutputRunParameters[0]['eos']=eosBase
nonOutputRunParameters[0]['rollMid']=14.0
nonOutputRunParameters[0]['rollScale']=0.5
nonOutputRunParameters[0]['T']=0.5


dirNames=glob.glob(directoryBase)

for thisDir in dirNames:
    file = glob.glob(thisDir +"/"+ eosBase + "*")

    #We must get a from the parameters file
    paramsFile=open( thisDir +"/"+ "Parameters.input")
    for line in paramsFile.readlines():
        if "Rotfunc" in line:
            a=float(line.split(":")[1])
    print "A is: ", a
    nonOutputRunParameters[0]['a']=a

    entries = parseCstFileList(file,nonOutputRunParameters)

    parseEntriesIntoDB(entries,c,"models",3,thisDir)
    connection.commit()
    paramsFile.close()
    print file

connection.close()
