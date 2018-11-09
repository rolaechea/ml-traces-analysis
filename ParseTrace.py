#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 10:51:56 2018

@author: rafaelolaechea
"""


import numpy as np

__TraceDirectory__ = "../PartialDataset/"
__ComputedTraceFilename__ = "traceName.txt"

__BaseTraceFilename__ = "conf-%d-rep-%d-timing.txt"


__trainingSetSize__ = 2000

__numberTransitions__ = 35

__transitionIds__ = [8, 6, 9, 13, 31, 33, 5, 7, 4, 11, 14, 18, 30, 10, 16, 19, 17, 20, 32]

__currentRep__ = 1

def getAllTransitionIds():
    """"
    Returns a list of all transition identifiers
    """"
    return __transitionIds__

def getFilenameFromConfigurationAndRepetition(configuration, repetition=__currentRep__):
    """
    Returns a resolved filename based on given configuration and repetition
    """
    tmpTraceFilename = __TraceDirectory__ + __BaseTraceFilename__ % (configuration, __currentRep__)

    return tmpTraceFilename

def extractTransitionToBagOfTimesDictionaryFromTraceFile(traceFilename):
    """
    Inputs -- File or list of lines ??
    Output -- Dictionary of Transition Ids to Time taken
    """
    __dictTransitionToTimesBag__ = {}
    
    fTrace = open(__ComputedTraceFilename__, 'r')

    for line in fTrace:
#            print (line.rstrip())
        transitionId, timeTaken = line.rstrip().split(":")
        
        existintTimeTakenList = __dictTransitionToTimesBag__.get(int(transitionId))
        
        if existintTimeTakenList==None:
            __dictTransitionToTimesBag__[int(transitionId)] = [int(timeTaken)]
        else:
            __dictTransitionToTimesBag__[int(transitionId)].append(int(timeTaken))
        
    print ([(x, len(y)) for x,y in   __dictTransitionToTimesBag__.items()])
    
    fTrace.close()
    
    
    return __dictTransitionToTimesBag__

if __name__ == "__main__":
    
    print ("File that reads a trace and parses it for further processing \n")

    for indexFile in range(1, 50):
        __ComputedTraceFilename__ = getFilenameFromConfigurationAndRepetition(indexFile)    
        
        extractTransitionToBagOfTimesDictionaryFromTraceFile(__ComputedTraceFilename__)
        
        print ("Finished Parsing %s " % (__ComputedTraceFilename__,))

    