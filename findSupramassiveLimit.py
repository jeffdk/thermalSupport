
from eosDriver import eosDriver, getTRollFunc, kentaDataTofLogRhoFit1, kentaDataTofLogRhoFit2
from datasetManager import cstDataset
from maxMassOrigFiles.sqlPlotRoutines import nearValueFilter

shedDb = '/home/jeff/work/rotNSruns/shedRuns4-24-13.db'
shenEosTableFilename = '/home/jeff/work/HShenEOS_rho220_temp180_ye65_version_1.1_20120817.h5'
ls220EosTableFilename = '/home/jeff/work/LS220_234r_136t_50y_analmu_20091212_SVNr26.h5'
shen = eosDriver(shenEosTableFilename)
ls220 = eosDriver(ls220EosTableFilename)

theEos = ls220

eosName = 'LS220'
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
    thisSet = cstDataset(script, eosName, ye, shedDb)
    c = thisSet.dbConn.cursor()
    c.execute("SELECT MAX(baryMass) FROM models")
    mb = c.fetchall()[0][0]
    c.execute("SELECT MAX(gravMass) FROM models WHERE ToverW<0.25")
    mg_max = c.fetchall()[0][0]
    filt = nearValueFilter('baryMass', mb, 1e-7)
    #print filt
    c.execute("SELECT edMax,baryMass,gravMass,arealR,rpoe,omega_c,ToverW FROM models WHERE "
              + " AND ".join(filt))
    values = c.fetchall()[0]
    mg_at_maxMb = values[2]
    rhob = theEos.rhobFromEnergyDensityWithTofRho(values[0], ye, tempFuncsDict[script])
    print eosText + " " + script + "   ",
    print "& %2.3f & %2.3f & %2.3f & %2.3f & %2.3f & %2.3f & %2.3f\\\\" \
          % (rhob/1.e15, values[1], values[2], values[3], values[4], values[5]/1000.0, values[6])
    #print 'MG FRACDIFF: ', (mg_max - mg_at_maxMb)/mg_max
    del thisSet