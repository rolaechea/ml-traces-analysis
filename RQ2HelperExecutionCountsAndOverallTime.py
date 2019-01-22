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
from ParseTrace import  setBaseTracesSourceFolder, sumTimeTakenPerTransitionFromConfigurationAndRep

def print_help():
    """
    Print statements explaining how program is used.
    
    Program generates a json summary from a set of traces. 
    
    """
    print("python RQ2HelperExecutionCountsAndOverralTime.py SubjecySystem traceSourceFolder JsonOuptutFilename")
    print("SubjecySystem either autonomoose or x264")
    print("traceSourceFolder source folder where executions are stored")
    print("Filename where to store json summary of execution traces.")

MIN_NUM_ARGUMENTS = 3

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
        
    else:
        
        print_help()
        exit(0)
    return SubjectSystem, TraceSourceFolder, pklOuptputFilename


def summarizeTracesX264(pklOutput):
    """
    Read all traces from the source folder (already set) and summarize their overall execution time, # of counts per transition, and total time per transition.

    Parameters
    ----------
    pklOutput : string
    Filename where to store results.
    """
    allConfigurationsIds = range(0, 2)
    
    dctAllTracesExecutionTimes = {}
    dctConfTodctRepTodctTransitionToTimes = {}

    for aConfId in allConfigurationsIds:
        print("Summarizing Configuration {0}".format(aConfId))
        dctConfTodctRepTodctTransitionToTimes[aConfId] = {}
        for repetitionId in range(1, 5):

            dctTransitionToTimeTamekn = sumTimeTakenPerTransitionFromConfigurationAndRep(aConfId,  repetitionId)
            
            timeTakenByTraceAddition = sum([dctTransitionToTimeTamekn[x][MLConstants.tupleTimeOffset] for x in dctTransitionToTimeTamekn.keys()])
            
            dctAllTracesExecutionTimes[(aConfId, repetitionId)] = timeTakenByTraceAddition
             
            dctConfTodctRepTodctTransitionToTimes[aConfId][repetitionId] = dctTransitionToTimeTamekn
#            print(timeTakenByTraceAddition)
    
    print (dctAllTracesExecutionTimes.keys())
    print (dctConfTodctRepTodctTransitionToTimes.keys())
    
if __name__ == "__main__":
    SubjectSystem, TraceSourceFolder, pklOuptputFilename  = parseRuntimeParemeters(sys.argv)    

    setBaseTracesSourceFolder(TraceSourceFolder)


    if SubjectSystem == MLConstants.x264Name:

        summarizeTracesX264(pklOuptputFilename)

    else:
        
        print (" Summaries not implemented for Autonomooose yet")
        exit(0)