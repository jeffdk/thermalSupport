#!/usr/bin/python

__author__ = 'jeff'



class modelGenerator():
    rotNS_location=""
    makeEOSfile_location=""
    requestQueue=[]
    def __init__(self,rotNS_location,makeEOSfile_location):
        self.rotNS_location=rotNS_location
        self.makeEOSfile_location=makeEOSfile_location


    def runModel(self, inputParams):
        runParams, eosParams=inputParams