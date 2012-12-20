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
import numpy
from modelGeneration import modelGenerator
import parseFiles
from minimizeAlgorithm import *

#Below are default run setup arguments.  They can be easily changed with command line args
location_MakeEosFile = "/home/jeff/spec/Hydro/EquationOfState/Executables/MakeRotNSeosfile"
location_RotNS       = "/home/jeff/work/RotNS/RotNS"
specEosOptions       = "Tabulated(filename= /home/jeff/work/HS_Tabulated.dat )"
locationForRuns      = "/home/jeff/work/rotNSruns"
databaseFile         = '/home/jeff/work/rotNSruns/tester.db'
ROTNS_RUNTYPE        = 30   #30 is 'one model' sequence, designed to generate just one model

def main():
    parser = argparse.ArgumentParser(epilog="If you get 'too few arguments' error, remember you must "
                                            "specify the mode by passing either 'runmodels' or 'evolve'")
    parser.add_argument('mode', choices=['runmodels','evolve'])

    globalOptions = parser.add_argument_group('Global options.  Optional.  Applies to all run modes')
    globalOptions.add_argument("-MakeEosFile-exec",  help="Location of MakeRotNSeosfile executable. "
                                                   "default: '%s'" %location_MakeEosFile,
                                                   default = location_MakeEosFile )
    globalOptions.add_argument("-RotNS-exec",        help="Location of RotNS executable. "
                                                   "default: '%s'" % location_RotNS,
                                                   default = location_RotNS)
    globalOptions.add_argument("-eos-opts",          help="Option passed to MakeRotNSeosfile. Format is a SpEC "
                                                   "EOS input file option. "
                                                   "default: '%s'" % specEosOptions,
                                                   default = specEosOptions)
    globalOptions.add_argument("-location-for-runs", help="Directory where code will it's many RotNS runs. "
                                                   "default: '%s'" % locationForRuns,
                                                   default = locationForRuns)
    globalOptions.add_argument("-database-file",     help="sqlite3 database file to commit run results to. "
                                                   "default: '%s'" % databaseFile,
                                                   default = databaseFile )
    globalOptions.add_argument("-RotNS-runtype",     help="RotNS 'RunType'. Supported values are 30 (one-model)"
                                                   "and 3 (mass-shed) Must be integer "
                                                   "default: %s" % ROTNS_RUNTYPE,
                                                   type = int,
                                                   default = ROTNS_RUNTYPE)

    #TODO: JESUS CHRIST CLEAN THIS UP
    globalOptions.add_argument('-rollMid', type=float, help="Temperature roll-off midpoint in log10(density-cgs)"
                                                            "Default: 14.0",
                                                            default=14.0)
    globalOptions.add_argument('-rollScale', type=float, help="Temperature roll-off scale in log10(density-cgs)"
                                                              "Default: 0.5",
                                                              default=0.5)

    runModels_parser = parser.add_argument_group('Options for Run Models mode (all floats)')
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
    evolve_parser.add_argument('-deltas',   help="Initial stepsize tuple for variables, e.g. \"(0.3,.01,.01,.01)\"")
    evolve_parser.add_argument('-descendVar', help="Variable name to evolve along steepest descent"
                                                   "e.g.: (and default:  \"ToverW\"", default="ToverW")
    evolve_parser.add_argument('-fixedVars', help="Tuple of variable names to hold fixed for descent."
                                                  "e.g.: \"('J','baryMass')\"" )


    args = parser.parse_args()
    connection = parseGlobalArgumentsAndReturnDBConnection(args)

    #Now we have all information to create our modelGenerator object
    modelGen=modelGenerator(location_RotNS,location_MakeEosFile,specEosOptions,locationForRuns,ROTNS_RUNTYPE)

    #as well as our run parameters dictionary template
    runParametersTemplate={'rollMid':args.rollMid,
                           'rollScale':args.rollScale}


    runMode = args.mode
    print "Run mode: %s" % runMode
    if runMode == 'runmodels':

        #Get parameter ranges to run

        T_range = rangeFromParams(args.T1,args.T2,args.T_steps,args.T,"T")
        a_range = rangeFromParams(args.a1,args.a2,args.a_steps,args.a,"a")
        ed_range = rangeFromParams(args.edMin,args.edMax,args.ed_steps,args.ed,"energy density")

        rpoe_range = [1.0]
        parametersList=[]
        if ROTNS_RUNTYPE == 3:
            print "WARNING, RPOE PARAMETERS NOT PARSED FOR MASS SHED SEQUENCE!!"
            print "Also note, rotns does it's own logspacing of points in density space."
            print
            assert len(ed_range) > 1, "Must specify a density range with at least 2 steps for Mass-Shed run type!"
            runParametersTemplate.update({'edMax':ed_range[-1],
                                          'edMin':ed_range[0],
                                          'Nsteps':len(ed_range),
                                          'rpoe': rpoe_range[0]} )
            parametersList =[populateParamsDict(runParametersTemplate,a,T) for a in a_range for T in T_range ]
        else:
            rpoe_range = rangeFromParams(args.rpoe1,args.rpoe2,args.rpoe_steps,args.rpoe,"rpoe")
            parametersList=[ populateParamsDict(runParametersTemplate, a, T, ed, rpoe)
                            for a in a_range
                            for T in T_range
                            for ed in ed_range
                            for rpoe in rpoe_range
                            ]
        parametersList=[]
        modelGen.generateModels(modelGen.runRotNS,parametersList,connection)
        #Setup run params dictionary

        print T_range

    if runMode == 'evolve':

        p0 = ast.literal_eval( args.p0 )
        assert isinstance(p0, tuple)

        p0variables = ast.literal_eval( args.p0_string )
        assert isinstance(p0variables, tuple)

        deltas =  ast.literal_eval( args.deltas)
        assert isinstance(deltas, tuple)
        deltas = array(deltas)
        assert len(p0) == len(p0variables) and len(p0) == len(deltas), \
               "Lengths of evolution tuples must be the same! Re-examine your -p0, -p0-string, & -delats options"

        fixedVars=()
        if args.fixedVars:
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

        #TODO generalize stationary params
        stationaryParams = {'rollMid':14.0,
                            'rollScale' :  0.5
                            }

        #TODO allow max steps input parameter
        steepestDescent("ToverW",("baryMass","J"),initialBasis,firstDeriv,p0,
                        deltas,connection, modelGen,stationaryParams,0)





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
    if rpoe:
        newDict.update({'rpoe':rpoe})
    newDict.update( runParamsTemplate)
    return newDict

def rangeFromParams(start,end,steps,fixedValue,paramName):

    result = None
    if fixedValue:
        assert (start==None and end==None and steps ==None),\
            "Cannot specify range AND a fixed value for parameter: %s" %paramName
        result = array([fixedValue])
    else:
        assert not (start==None or end==None or steps ==None),\
        "If specifing a range, you must specify ALL of start, end and steps for parameter: %s" %paramName
        result = linspace(start,end,steps)
    return result


def parseGlobalArgumentsAndReturnDBConnection(args):
    global location_MakeEosFile, location_RotNS, specEosOptions, locationForRuns, databaseFile, ROTNS_RUNTYPE

    location_MakeEosFile = args.MakeEosFile_exec
    assert os.path.isfile(location_MakeEosFile), "Cannot find MakeRotNSeosfile exec: %s" % location_MakeEosFile

    location_RotNS       = args.RotNS_exec
    assert os.path.isfile(location_RotNS),       "Cannot find RotNS exec: %s" % location_RotNS

    specEosOptions       = args.eos_opts

    locationForRuns      = args.location_for_runs
    assert os.path.exists(locationForRuns),      "Path specified for RotNS runs doesn't exist! %s" % locationForRuns

    databaseFile         = args.database_file
    databaseExists=os.path.isfile(databaseFile)
    connection = sqlite3.connect(databaseFile)
    cursor = connection.cursor()
    if not databaseExists:
            print "WARNING, DB FILE NOT PREVIOUSLY FOUND AT: "
            print databaseFile
            print "CREATING NEW ONE..."
            cursor.execute("CREATE TABLE models" + parseFiles.columnsString)
    connection.commit()

    ROTNS_RUNTYPE        = args.RotNS_runtype
    assert ROTNS_RUNTYPE == 3 or ROTNS_RUNTYPE == 30, "Only supported RotNS RunTypes are 3 and 30!"

    return connection



if __name__ == "__main__":
    main()