#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 11:52:33 2019

@author: rafaelolaechea

Generes a JSON file that includes for each configuration and repetition,
    a.) Overall Time Taken (from sum).
    b.) Counts per transition.
    c.) per transition time taken.

Facilitates faster execution of Analyzer RQ2.py
"""
import sys


import MLConstants
import pickleFacade
from ParseTrace import  setBaseTracesSourceFolder, sumTimeTakenPerTransitionFromConfigurationAndRep


def print_help():
    """
    Print statements explaining how program is used.
    
    Program generates a json summary from a set of traces. 
    
    """
    print("python RQ2HelperExecutionCountsAndOverralTime.py SubjecySystem traceSourceFolder JsonOuptutFilename")
    print("SubjecySystem either autonomoose or x264")
    print("traceSourceFolder source folder where executions are stored")
    print("Filename where to store pickle summary of execution traces (overal time summary)")
    print("Filename where to store pickle summary of execution traces (per-transition count (0) and time (1)  summary)")
    
MIN_NUM_ARGUMENTS = 4

def parseRuntimeParemeters(inputParameters):
    """
    Parse the parameters from command line.
    
    The following parameters are suported:
        Subject System (x264 or Autonomoose).
        Trace sources folder.        
        Output Destination of pklOutput file.

    Returns
    ------    
    Parsed values as a tuple.    
    """
    if len(inputParameters ) > MIN_NUM_ARGUMENTS:
        SubjectSystem = inputParameters[1]
         
        if SubjectSystem not in MLConstants.lstSubjectSystems:
             
            print ("Subject systems must be one of {0}".format(", ".join(MLConstants.lstSubjectSystems)))
             
            exit()
            
        TraceSourceFolder = inputParameters[2]

        pklOuptputFilename = inputParameters[3]
        
        pklOuptputPerTransitionFilename = inputParameters[4]        
    else:
        
        print_help()
        exit(0)
    return SubjectSystem, TraceSourceFolder, pklOuptputFilename, pklOuptputPerTransitionFilename


def summarizeTracesX264(pklOuptputFilename, pklOuptputPerTransitionFilename):
    """
    Read all traces from the source folder (already set) and summarize their overall execution time, # of counts per transition, and total time per transition.


    Creates two PKL Files. First one is dictionary mapping confId, repetitionId to overal execution time. 
    Second one is Chained Dictionary mapping Conf -- > rep --> transitionId --> (Count, TimeTakenTotal)
    
    Parameters
    ----------
    pklOutput : string
    Filename where to store results.
    """
    allConfigurationsIds = range(0, 2304)
    
    dctAllTracesExecutionTimes = {}
    dctConfTodctRepTodctTransitionToTimes = {}

    for aConfId in allConfigurationsIds:
        print("Summarizing Configuration {0}".format(aConfId))
        dctConfTodctRepTodctTransitionToTimes[aConfId] = {}
        for repetitionId in range(1, 11):

            dctTransitionToTimeTamekn = sumTimeTakenPerTransitionFromConfigurationAndRep(aConfId,  repetitionId)
            
            timeTakenByTraceAddition = sum([dctTransitionToTimeTamekn[x][MLConstants.tupleTimeOffset] for x in dctTransitionToTimeTamekn.keys()])
            
            dctAllTracesExecutionTimes[(aConfId, repetitionId)] = timeTakenByTraceAddition
             
            dctConfTodctRepTodctTransitionToTimes[aConfId][repetitionId] = dctTransitionToTimeTamekn
#            print(timeTakenByTraceAddition)
    
#    print (dctAllTracesExecutionTimes.keys())
#    print (dctConfTodctRepTodctTransitionToTimes.keys())
    
    pickleFacade.saveObjectToPickleFile(pklOuptputFilename, dctAllTracesExecutionTimes)
    pickleFacade.saveObjectToPickleFile(pklOuptputPerTransitionFilename, dctConfTodctRepTodctTransitionToTimes)
    
if __name__ == "__main__":
    SubjectSystem, TraceSourceFolder, pklOuptputFilename, pklOuptputPerTransitionFilename  = parseRuntimeParemeters(sys.argv)    

    setBaseTracesSourceFolder(TraceSourceFolder)


    if SubjectSystem == MLConstants.x264Name:

        summarizeTracesX264(pklOuptputFilename, pklOuptputPerTransitionFilename)

    else:
        
        print (" Summaries not implemented for Autonomooose yet")
        exit(0)