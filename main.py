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
databaseFile         = '/home/jeff/work/rotNSruns/stepDown_models.db'
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
    #TODO: FINISH THE HELP TEXT FOR REST OF COMMANDLINE ARGS
    #TODO: AND JESUS CHRIST CLEAN THIS UP
    globalOptions.add_argument('-rollMid')
    globalOptions.add_argument('-rollScale')

    runModels_parser = parser.add_argument_group('Options for Run Models mode')
    runModels_parser.add_argument('-a1')
    runModels_parser.add_argument('-a2')
    runModels_parser.add_argument('-a-steps')
    runModels_parser.add_argument('-a', help='Value for a if not doing a range')
    runModels_parser.add_argument('-T1')
    runModels_parser.add_argument('-T2')
    runModels_parser.add_argument('-T-steps')
    runModels_parser.add_argument('-T', help='Value for T if not doing a range')
    runModels_parser.add_argument('-edMax')
    runModels_parser.add_argument('-edMin')
    runModels_parser.add_argument('-ed-steps')
    runModels_parser.add_argument('-ed', help='Value for ed if not doing a range')
    runModels_parser.add_argument('-rpoe1')
    runModels_parser.add_argument('-rpoe2')
    runModels_parser.add_argument('-rpoe-steps')
    runModels_parser.add_argument('-rpoe', help='Value for rpoe if not doing a range')

    evolve_parser    = parser.add_argument_group('Options for quasi-equilibrium evolutionary sequence mode')
    evolve_parser.add_argument('-p0')
    evolve_parser.add_argument('-p0-string')
    evolve_parser.add_argument('-deltas')
    evolve_parser.add_argument('-descendVar', default="ToverW")
    evolve_parser.add_argument('-fixedVars')


    args = parser.parse_args()
    connection = parseGlobalArgumentsAndReturnDBConnection(args)

    #Now we have all information to create our modelGenerator object
    modelGen=modelGenerator(location_RotNS,location_MakeEosFile,specEosOptions,locationForRuns,ROTNS_RUNTYPE)

    runMode = args.mode
    print "Run mode: %s" % runMode
    if runMode == 'runmodels':

        print "Not implemented yet"

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




    print location_MakeEosFile, location_RotNS, specEosOptions, locationForRuns, databaseFile, ROTNS_RUNTYPE


    #Clean up
    connection.commit()
    connection.close()
    return 0


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