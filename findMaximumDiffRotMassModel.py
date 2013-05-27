
from eosDriver import eosDriver, getTRollFunc, kentaDataTofLogRhoFit1, kentaDataTofLogRhoFit2
from datasetManager import cstDataset
from maxMassOrigFiles.sqlPlotRoutines import nearValueFilter

shedDb = '/home/jeff/work/rotNSruns/shedRuns4-24-13.db'
sourceDb = '/home/jeff/work/rotNSruns/vdenseBetaEqD5-26.db'
c30p10Db = '/home/jeff/work/rotNSruns/svdense30p10A.db'
shedDb = sourceDb
shenEosTableFilename = '/home/jeff/work/HShenEOS_rho220_temp180_ye65_version_1.1_20120817.h5'
ls220EosTableFilename = '/home/jeff/work/LS220_234r_136t_50y_analmu_20091212_SVNr26.h5'
shen = eosDriver(shenEosTableFilename)
ls220 = eosDriver(ls220EosTableFilename)

theEos = ls220

eosName = 'HShenEOS'
ye = 'BetaEq'

eosText = eosName
if eosName == 'HShenEOS':
    eosText = 'HShen'
    theEos = shen


scriptsList = ['c40p0', 'c30p10', 'c30p5', 'c30p0', 'c20p0', 'cold']
cXXp0_params = [(40.0, 14.18, 0.5,), (30.0, 14.055, 0.375),  (20.0, 13.93, 0.25)]
tempFuncs = [getTRollFunc(params[0], 0.01, params[1], params[2]) for params in cXXp0_params]
tempFuncs.append(kentaDataTofLogRhoFit1())
tempFuncs.append(kentaDataTofLogRhoFit2())
tempFuncs.append(lambda x: 0.01)
tempFuncsDict = {scriptsList[i]: tempFuncs[i] for i in range(len(scriptsList))}


scriptsList = scriptsList[::-1]
for script in scriptsList:
    if script == 'c30p10':
        thisSet = cstDataset(script, eosName, ye, c30p10Db)
    else:
        thisSet = cstDataset(script, eosName, ye, shedDb)
    c = thisSet.dbConn.cursor()
    c.execute("SELECT MAX(baryMass) FROM models WHERE ToverW<0.25")
    mb = c.fetchall()[0][0]
    filt = nearValueFilter('baryMass', mb, 1e-7) + ('ToverW<0.25',)
    #print filt
    c.execute("SELECT edMax,gravMass,baryMass,arealR,rpoe,a,omega_c,ToverW FROM models WHERE "
              + " AND ".join(filt))
    values = c.fetchall()[0]
    rhob = theEos.rhobFromEnergyDensityWithTofRho(values[0], ye, tempFuncsDict[script])
    print eosText + " " + script + "   ",
    print "& %2.3f & %2.3f & %2.3f & %2.3f & %2.3f & %1.1f & %2.3f & %2.3f\\\\" \
          % (rhob/1.e15, values[1], values[2], values[3], values[4],
             values[5], values[6]/1000.0, values[7])
    del thisSet