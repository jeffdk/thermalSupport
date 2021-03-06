"""
Main function for thermal support quasi-evolution sequence code

Note: sqlite database table name is always 'models'
      use a different database file if you want another set

Jeff Kaplan <jeffkaplan@caltech.edu>
"""
import argparse
import ast
import os
import sqlite3
from eosDriver import eosDriver
import numpy
from modelGeneration import modelGenerator
import parseFiles
import consts
from minimizeAlgorithm import *
from pickleHack import *

#Below are default run setup arguments.  They can be easily changed with command line args
location_RotNS = "/home/jeff/work/RotNS/RotNS"
locationForRuns = "/home/jeff/work/rotNSruns"
databaseFile = '/home/jeff/work/rotNSruns/tester.db'
ROTNS_RUNTYPE = 30   # 30 is 'one model' sequence, designed to generate just one model
eosPrescription = \
    {'type': 'tableFromEosDriver',
     'sc.orgTableFile': '/home/jeff/work/LS220_234r_136t_50y_analmu_20091212_SVNr26.h5',
     'prescriptionName': 'isothermal',
     'ye': 0.15,
     'rollMid': 14.0,
     'rollScale': 0.5,
     'eosTmin': 0.01}
#DEPRECATED default run setup arguments
#location_MakeEosFile = "/home/jeff/spec/Hydro/EquationOfState/Executables/MakeRotNSeosfile"
#specEosOptions       = "Tabulated(filename= /home/jeff/work/HS_Tabulated.dat )"


def main():
    parser = argparse.ArgumentParser(
        epilog="If you get a 'too few arguments' error, remember you must "
               "specify the mode by passing either 'runmodels' or 'evolve'")

    parser.add_argument('mode', choices=['runmodels', 'evolve'])

    globalOptions = parser.add_argument_group(
        'Global options.  Optional.  Applies to all run modes')

    globalOptions.add_argument("-RotNS-exec",
                               help="Location of RotNS executable. "
                               "default: '%s'" % location_RotNS,
                               default=location_RotNS)

    globalOptions.add_argument("-location-for-runs",
                               help="Directory where code will do"
                                    " it's many RotNS runs. "
                               "default: '%s'" % locationForRuns,
                               default=locationForRuns)

    globalOptions.add_argument("-database-file",
                               help="sqlite3 database file to commit"
                                    " run results to. "
                               "default: '%s'" % databaseFile,
                               default=databaseFile)

    globalOptions.add_argument("-RotNS-runtype",
                               help="RotNS 'RunType'. Supported values are "
                                    "30 (one-model) and "
                                    "3  (mass-shed)  Must be integer. "
                               "default: %s" % ROTNS_RUNTYPE,
                               type=int,
                               default=ROTNS_RUNTYPE)

    globalOptions.add_argument("-eosPrescription",
                               help="Dictionary defining EOS prescriptions. "
                                    "See TODO FIX ME for examples."
                               "default: %s" % eosPrescription,
                               type=str,
                               default=eosPrescription)

    globalOptions.add_argument("-setRhoBaryons",
                               help="All ed arguments specified are assumed "
                                    "to be baryon density values. Uses the"
                                    "EOS prescription to convert the inputs "
                                    "to energy density for running RotNS",
                               action="store_true")

    runModels_parser = parser.add_argument_group(
        'Options for Run Models mode (all floats)')
    #TODO: JESUS CHRIST CLEAN THIS UP
    runModels_parser.add_argument('-a1', type=float,
        help='Start value for range in differential rotation parameter a')
    runModels_parser.add_argument('-a2', type=float,
        help='End value for range in differential rotation parameter a'  )
    runModels_parser.add_argument('-a-steps', type=int,
        help='Number of steps for range in differential rotation parameter a' )
    runModels_parser.add_argument('-a', type=float,
        help='Value for a if not doing a range')
    runModels_parser.add_argument('-T1' , type=float,
        help='Start value for range in Temperature parameter T')
    runModels_parser.add_argument('-T2' , type=float,
        help='End value for range in Temperature parameter T')
    runModels_parser.add_argument('-T-steps', type=int,
        help='Number of steps for range in Temperature parameter T')
    runModels_parser.add_argument('-T', type=float,
        help='Value for T if not doing a range')
    runModels_parser.add_argument('-edMin', type=float,
         help='Start value for range in maximum energy density parameter')
    runModels_parser.add_argument('-edMax' , type=float,
        help='End value for range in maximum energy density parameter')
    runModels_parser.add_argument('-ed-steps', type=int,
        help='Number of steps for range in maximum energy density parameter')
    runModels_parser.add_argument('-ed', type=float,
        help='Value for ed if not doing a range')
    runModels_parser.add_argument('-rpoe1', type=float,
        help='Start value for range in polar/equatorial radius parameter rpoe')
    runModels_parser.add_argument('-rpoe2', type=float,
        help='End value for range in polar/equatorial radius parameter rpoe')
    runModels_parser.add_argument('-rpoe-steps', type=int,
        help='Number of steps for range in polar/equatorial parameter rpoe')
    runModels_parser.add_argument('-rpoe', type=float,
        help='Value for rpoe if not doing a range')

    evolve_parser    = parser.add_argument_group('Options for quasi-equilibrium evolutionary sequence mode \n'
                                                 '  Note: p0, -p0-string, -deltas must have same number of entries')
    evolve_parser.add_argument('-p0', help="Python tuple for starting point, e.g.: \"(30.0,1.0,1.0,0.6)\"")
    evolve_parser.add_argument('-p0-string', help="Variable names tuple for starting point"
                                                  ", e.g.: \"('T','a','edMax','rpoe')\" " )
    evolve_parser.add_argument('-deltas',   help="Initial stepsize tuple for variables, e.g. \"(0.3,.01,.01,.01)\" ")
    evolve_parser.add_argument('-descendVar', help="Variable name to evolve along steepest descent "
                                                   "e.g.: (and default:  \"ToverW\"", default="ToverW ")
    evolve_parser.add_argument('-fixedVars', help="Tuple of dependent variable names to fixed for descent. i.e. "
                                                  "Take steps perpendicular to their gradient, "
                                                  "e.g.: \"('J','baryMass')\"" )
    evolve_parser.add_argument('-fixedParams',  type=str, help="Set if you want to fix parameters for the evolution"
                                                               "Format is list(tuples) in ('param',value) pairs e.g:\n"
                                                               "\"[('a',1.0),('T',10.0)]\"")
    evolve_parser.add_argument('-max-steps', type=int, help="Set the number of steps for the evolution."
                                                            "Default: 0   (a setup test run)",
                                                            default=0)
    evolve_parser.add_argument('-changeBasis', type=bool, help="Set to True to enable adjusting the basis "
                                                               "each step to split into fixed and non-fixed subspace"
                                                               "Defalt: False", default = False)
    args = parser.parse_args()

    ###################################################################
    # Command line arguments parsed!  Next, setup model generator
    ###################################################################

    connection = parseGlobalArgumentsAndReturnDBConnection(args)

    #Now we have all information to create our modelGenerator object
    modelGen = modelGenerator(location_RotNS, eosPrescription, locationForRuns, ROTNS_RUNTYPE)

    #as well as our run parameters dictionary template
    runParametersTemplate = {}

    print "EOS prescription: ", eosPrescription
    runMode = args.mode
    print "Run mode: %s" % runMode
    if runMode == 'runmodels':

        #Get parameter ranges to run

        T_range = rangeFromParams(args.T1,args.T2,args.T_steps,args.T,"T")
        a_range = rangeFromParams(args.a1,args.a2,args.a_steps,args.a,"a")
        ed_range = rangeFromParams(args.edMin,args.edMax,args.ed_steps,args.ed,"energy density")

        rpoe_range = [1.0]
        if ROTNS_RUNTYPE == 3:
            print "WARNING, RPOE PARAMETERS NOT PARSED FOR MASS SHED SEQUENCE!!"
            print "Also note, rotns does it's own logspacing of points in density space."
            print
            assert not args.setRhoBaryons, "Can't specify rho baryons internal to RotNS!"
            assert len(ed_range) > 1, "Must specify a density range with at least 2 steps for Mass-Shed run type!"
            runParametersTemplate.update({'edMax':ed_range[-1],
                                          'edMin':ed_range[0],
                                          'Nsteps':len(ed_range),
                                          'rpoe': rpoe_range[0]} )
            parametersList =[populateParamsDict(runParametersTemplate,a,T) for a in a_range for T in T_range ]
        else:
            if args.setRhoBaryons:
                #If you need to do this you can expand the list comprehension below
                assert len(T_range) == 1,\
                    "Cannot specify multiple temperatures if you are setting densities " \
                    "via baryon density instead of energy densities!"
                ed_range = convertRhoBaryToEnergyDense(ed_range, eosPrescription, T_range[0])
            rpoe_range = rangeFromParams(args.rpoe1,args.rpoe2,args.rpoe_steps,args.rpoe,"rpoe")
            parametersList=[ populateParamsDict(runParametersTemplate, a, T, ed, rpoe)
                            for a in a_range
                            for T in T_range
                            for ed in ed_range
                            for rpoe in rpoe_range
                            ]
        #parametersList=[]
        print "/======================== RUNNING RUN MODELS WITH =============================="
        print "|"
        print "|   eosPrescription:  %s" % niceDictPrint(eosPrescription)
        print "|   a_range:          %s" % str(a_range)
        print "|   T_range:          %s" % str(T_range)
        print "|   ed_range:         %s" % str(ed_range)
        print "|   rpoe_range:       %s" % str(rpoe_range)
        print "|"
        print "|   location_RotNS:   %s" % location_RotNS
        print "|   locationForRuns:  %s" % locationForRuns
        print "|   databaseFile:     %s" % databaseFile
        print "|"
        print "\==============================================================================="
        modelGen.generateModels(modelGen.runRotNS,parametersList,connection)
        #Setup run params dictionary

        print T_range

    if runMode == 'evolve':
        assert not args.setRhoBaryons, "setRhoBaryons option not supported in evolve mode!"
        assert args.p0, "Selected evolve mode but no p0 specified!"
        assert args.p0_string, "Selected evolve mode but no p0-string specified!"
        assert args.deltas, "Selected evolve mode but no deltas specified!"

        p0 = ast.literal_eval( args.p0 )
        assert isinstance(p0, tuple)

        #TODO: add -rollMid and -rollScale to this list
        rotNS_independentVariables=('T','a','rpoe','edMax')
        p0variables = ast.literal_eval( args.p0_string )
        assert isinstance(p0variables, tuple)
        for var in p0variables:
            assert var in rotNS_independentVariables, "You specified %s in your p0-string, but it is not" \
                                                      "a valid RotNS independent variable. " \
                                                      "Choose from: %s" % (var,rotNS_independentVariables)

        deltas =  ast.literal_eval( args.deltas)
        assert isinstance(deltas, tuple)
        deltas = array(deltas)
        assert len(p0) == len(p0variables) and len(p0) == len(deltas), \
               "Lengths of evolution tuples must be the same! Re-examine your -p0, -p0-string, & -delats options"

        fixedVars=()
        #TODO: check if fixedVars actually are proper RotNS output variables
        if not args.fixedVars == None:
            fixedVars = ast.literal_eval(args.fixedVars)
        assert isinstance(fixedVars,tuple)

        descendVar = args.descendVar

        evolveDim= len(p0)

        #just generates basis with ones along diagonal
        initialBasisVectors = numpy.diag( numpy.ones(evolveDim) )
        initialBasis = basis(initialBasisVectors,p0variables)
        #TODO add options for specifying different derivative stencils
        #right now hard code 5pt first deriv stencil
        theStencil = fdStencil(1, [5])

        firstDeriv=deriv(dim=1, order=1, step=0.1, stencil=theStencil,
                         coeffs=array([1,-8,0,8,-1])/12.,  name="5ptFirstDeriv")

        stationaryParams = runParametersTemplate.copy()
        fixedParams = []
        if args.fixedParams:
            fixedParams = ast.literal_eval( args.fixedParams)
            print fixedParams
            assert isinstance(fixedParams,list) and isinstance(fixedParams[0],tuple), \
                                             " You have incorrectly specified your -fixedParams argument." \
                                             " Read the help text (-h) and try again! "
            for pair in fixedParams:
                param,value=pair
                stationaryParams[param]=value
                assert not param in p0variables,  "Can't list param '%s' in your p0 variables if you are fixing " \
                                                  "param !%s'!" % (param,param)
                assert param in rotNS_independentVariables, "fixedParam '%s' must be a valid RotNS independent" \
                                                            "variable!  Choose from:" \
                                                            " %s" % (param,rotNS_independentVariables)

        assert len(fixedParams) + len(p0) == len(rotNS_independentVariables), \
                                             "You have left out a RotNS independent variable when specifying your " \
                                             "-p0-string and -fixedParams.  " \
                                             "Must use all of  %s" % str(rotNS_independentVariables)

        assert len(fixedParams) + len(fixedVars) < len(rotNS_independentVariables), \
                                            "Specified too many fixed vars Must be less than # of independent vars"

        print "/======================== RUNNING STEEPEST DESCENT WITH ========================"
        print "|"
        print "|   descendVar:       %s" % descendVar
        print "|   fixedVars:        %s" % str(fixedVars)
        print "|   free parameters:  %s" % str(initialBasis.axesNames)
        print "|   p0:               %s" % str(p0)
        print "|   deltas:           %s" % str(deltas)
        print "|   stationaryParams: %s" % stationaryParams
        print "|   max steps:        %s" % args.max_steps
        print "|   firstDeriv name:  %s" % firstDeriv.name
        print "|   changeBasis:      %s" % args.changeBasis
        print "|"
        print "\==============================================================================="
        steepestDescent(descendVar,fixedVars,initialBasis,firstDeriv,p0,
                        deltas,connection, modelGen,stationaryParams,args.max_steps,args.changeBasis)





    #Clean up
    connection.commit()
    connection.close()
    return 0

def populateParamsDict(runParamsTemplate, a,T,ed=None,rpoe=None):
    newDict={}
    newDict.update( {'a':a})
    newDict.update( {'T':T})
    if ed:
        newDict.update( {'edMax':ed})
    if not rpoe == None:
        newDict.update({'rpoe':rpoe})
    newDict.update( runParamsTemplate)
    return newDict

def rangeFromParams(start,end,steps,fixedValue,paramName):

    result = None
    if not fixedValue == None:
        assert (start==None and end==None and steps ==None),\
            "Cannot specify range AND a fixed value for parameter: %s" %paramName
        result = array([fixedValue])
    else:
        assert not (start==None or end==None or steps ==None),\
        "If specifing a range, you must specify ALL of start, end and steps for parameter: %s" %paramName
        result = linspace(start,end,steps)
    return result


def flattenDictOfOptions(input):
    assert isinstance(input, dict)

    currentTuple =()

    for thisTuple in input.values():
        newTuple = ()
        for thisEntry in thisTuple:
            if isinstance(thisEntry, dict):
                thisEntry = flattenDictOfOptions(thisEntry)
                newTuple += thisEntry
            else:
                newTuple += (thisEntry,)
        currentTuple += newTuple

    #print currentTuple
    return currentTuple

def niceDictPrint(input):
    assert isinstance(input, dict)
    string = "\n|   \t{ "
    for key, value in input.iteritems():
        string += "\n|   \t '%s':  %s" % (key, str(value))
    string += "\n|   \t}"
    return string

def parseGlobalArgumentsAndReturnDBConnection(args):
    global eosPrescription, location_RotNS, locationForRuns, databaseFile, ROTNS_RUNTYPE

    eosPrescription = ast.literal_eval(args.eosPrescription)
    assert isinstance(eosPrescription, dict), \
        "eosPrescription argument is not a valid dictionary!"
    #print type(prescriptDict), prescriptDict
    for key in eosPrescription.keys():
        # type is the key for the eosPrescriptionType itself
        assert key in ('type',) + flattenDictOfOptions(modelGenerator.eosPrescriptionTypes),\
            "%s is not a valid key for any eosPrescription! " \
            "See modelGenerator.eosPrescriptionTypes" % key

    location_RotNS = args.RotNS_exec
    assert os.path.isfile(location_RotNS), \
        "Cannot find RotNS exec: %s" % location_RotNS

    locationForRuns = args.location_for_runs
    assert os.path.exists(locationForRuns), \
        "Path specified for RotNS runs doesn't exist! %s" % locationForRuns

    databaseFile = args.database_file
    databaseExists = os.path.isfile(databaseFile)
    connection = sqlite3.connect(databaseFile)
    cursor = connection.cursor()
    if not databaseExists:
            print "WARNING, DB FILE NOT PREVIOUSLY FOUND AT: "
            print databaseFile
            print "CREATING NEW ONE..."
            cursor.execute("CREATE TABLE models" + parseFiles.columnsString)
    connection.commit()

    ROTNS_RUNTYPE = args.RotNS_runtype
    assert ROTNS_RUNTYPE == 3 or ROTNS_RUNTYPE == 30, "Only supported RotNS RunTypes are 3 and 30!"

    return connection


def convertRhoBaryToEnergyDense(rhos, eosPrescription, T=None):
    assert isinstance(eosPrescription, dict)
    # method here is to process each part of the eosPrescription, and
    # eventually reduce it to parameters just required for tempPrescription
    eosScript = deepcopy(eosPrescription)

    assert eosScript['type'] == 'tableFromEosDriver', \
        "Convert to energy density from rho_b is only supported for eosDriver tables"
    del eosScript['type']

    theEos = eosDriver(eosScript['sc.orgTableFile'])
    del eosScript['sc.orgTableFile']

    assert 'ye' in eosScript, "Convert to enegry density requires a ye in eosPrescription"
    ye = eosScript['ye']
    del eosScript['ye']
    if ye == 'BetaEq':
        ye = None

    #prescriptionName only used to set temperature if necessary
    if eosScript['prescriptionName'] == 'isothermal':
        eosScript['T'] = T
    del eosScript['prescriptionName']

    if isinstance(rhos, float):
        rhos = [rhos]

    eds = []
    for rho in rhos:
        rho *= 1.e15  # fix units
        tempOfLog10Rhob = theEos.tempOfLog10RhobFuncFromPrescription(eosScript, ye)

        temp = tempOfLog10Rhob(numpy.log10(rho))

        if ye is None and temp is not None:
            theEos.setBetaEqState({'rho': rho, 'temp': temp})
        elif ye is None and temp is None:
            quantity = eosScript['quantity']
            target = eosScript['target']
            theEos.setConstQuantityAndBetaEqState({'rho': rho},
                                                  quantity,
                                                  target)
        elif ye == 'NuFull':
            theEos.setNuFullBetaEqState({'rho': rho, 'temp': temp})
        else:
            theEos.setState({'rho': rho, 'temp': temp, 'ye': ye})
        logeps = theEos.query('logenergy')
        eps = (numpy.power(10.0, logeps) - theEos.energy_shift) \
            * consts.AGEO_ERG / consts.AGEO_GRAM

        totalEnergyDensity = rho * (1.0 + eps)
        eds.append(totalEnergyDensity / 1.e15)
    del theEos
    return eds

if __name__ == "__main__":
    main()
