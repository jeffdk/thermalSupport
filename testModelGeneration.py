from eosDriver import kentaDataTofLogRhoFit1
from modelGeneration import modelGenerator
import sqlite3
import os
import parseFiles
from pickleHack import *


#Below are default run setup arguments.
location_MakeEosFile = "/home/jeff/spec/Hydro/EquationOfState/Executables/MakeRotNSeosfile"
location_RotNS       = "/home/jeff/work/RotNS/RotNS"
specEosOptions       = "Tabulated(filename= /home/jeff/work/LS220_Tabulated.dat )"
locationForRuns      = "/home/jeff/work/rotNSruns"
databaseFile         = '/home/jeff/work/rotNSruns/tester.db'
ROTNS_RUNTYPE        = 30   # 30 is 'one model' sequence, designed to generate just one model

databaseExists = os.path.isfile(databaseFile)
connection = sqlite3.connect(databaseFile)
cursor = connection.cursor()
if not databaseExists:
    print "WARNING, DB FILE NOT PREVIOUSLY FOUND AT: "
    print databaseFile
    print "CREATING NEW ONE..."
    cursor.execute("CREATE TABLE models" + parseFiles.columnsString)
connection.commit()

eosPrescription = {'type': 'tableFromSpEC',
                   'makeEosFile_location': location_MakeEosFile,
                   'specEosOptions': specEosOptions,
                   'ye': 0.12}

eosPrescription = \
     {'type': 'tableFromEosDriver',
      'sc.orgTableFile': '/home/jeff/work/LS220_234r_136t_50y_analmu_20091212_SVNr26.h5',
      'prescriptionName': 'isothermal',
      'ye': 0.12,
      'rollMid': 14.0,
      'rollScale': 0.5,
      'eosTmin': 0.01}
eosPrescription = \
     {'type': 'tableFromEosDriver',
      'sc.orgTableFile': '/home/jeff/work/LS220_234r_136t_50y_analmu_20091212_SVNr26.h5',
      'prescriptionName': 'fixedQuantity',
      'quantity': 'entropy',
      'target': 1.0,
      'ye': 'BetaEq'}
eosPrescription = \
     {'type': 'tableFromEosDriver',
      'sc.orgTableFile': '/home/jeff/work/HShenEOS_rho220_temp180_ye65_version_1.1_20120817.h5',
      'prescriptionName': 'isothermal',
      'ye': 0.1,
      'rollMid': 14.055,
      'rollScale': 0.375,
      'eosTmin': 0.01}
# eosPrescription = \
#      {'type': 'tableFromEosDriver',
#       'sc.orgTableFile': '/home/jeff/work/HShenEOS_rho220_temp180_ye65_version_1.1_20120817.h5',
#       'prescriptionName': 'manual',
#       'ye': 0.1,
#       'funcTofLogRho': 'kentaDataTofLogRhoFit1'}
modelGen = modelGenerator(location_RotNS, eosPrescription, locationForRuns, ROTNS_RUNTYPE)

runParametersTemplate = {'rollMid': 14.055,
                         'rollScale': 0.375,
                         'eosTmin': 0.01, 'T': 0.01}

#modelGen.generateEosTable(runParametersTemplate)

thisRunParameters = {'edMax': 0.3,
                     'edMin': 0.3,
                     'a': 0.8,
                     'rpoe': .30}
thisRunParameters2 = {'edMax': 0.6,
                     'edMin': 0.6,
                     'a': 0.0,
                     'rpoe': 1.0}
thisRunParameters.update(runParametersTemplate)

modelGen.generateModels(modelGen.runRotNS, [thisRunParameters], connection)

connection.close()