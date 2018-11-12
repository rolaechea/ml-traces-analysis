#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 10:51:56 2018

@author: rafaelolaechea
"""


import numpy as np

__TraceDirectory__ = "../FullTraces/akiyo/"
__ComputedTraceFilename__ = "traceName.txt"

__BaseTraceFilename__ = "conf-%d-rep-%d-timing.txt"


__trainingSetSize__ = 2304

__numberTransitions__ = 35

__transitionIds__ = [2,3,4,6,7,8, 9 ] 
# And 34 13, 31, 33, 5, 7, 4, 11, 14, 18, 30, 10, 16, 19, 17, 20, 32]

__currentRep__ = 1


def getAllTransitionIds():
    """
    Returns a list of all transition identifiers
    """
    return __transitionIds__


def getFilenameFromConfigurationAndRepetition(configuration, repetition):
    """
    Returns a resolved filename based on given configuration and repetition
    """
    tmpTraceFilename = __TraceDirectory__ + __BaseTraceFilename__ % (configuration, repetition)

    return tmpTraceFilename


def extractTransitionToBagOfTimesDictionaryFromTraceFile(traceFilename):
    """
    Inputs -- File or list of lines ??
    Output -- Dictionary of Transition Ids to Time taken
    """
    __dictTransitionToTimesBag__ = {}
    
    fTrace = open(traceFilename, 'r')

    for line in fTrace:
#            print (line.rstrip())
        transitionId, timeTaken = line.rstrip().split(":")
        
        existintTimeTakenList = __dictTransitionToTimesBag__.get(int(transitionId))
        
        if existintTimeTakenList==None:
            __dictTransitionToTimesBag__[int(transitionId)] = [int(timeTaken)]
        else:
            __dictTransitionToTimesBag__[int(transitionId)].append(int(timeTaken))
        
#    print ([(x, len(y), np.mean(y)) for x,y in   __dictTransitionToTimesBag__.items()])

    return     __dictTransitionToTimesBag__

    fTrace.close()
    
    
    return __dictTransitionToTimesBag__


def getArrayOfDictTransitionIdsToValueSet(ListProductIds, verbose=True):
    """
    Parse N files corresponding to selected product ids and create an array of size N that has
    for each product/conf a dictionary Transition Id to values.    
    """
    ArrayOfDictTransitionIdsToValueSet = []
    
    counterLoop = 0
    
    for indexFile in ListProductIds:

        if counterLoop % 10 == 0 and verbose:
            print ("Parsing File  # {0}".format(counterLoop))
            
        __ComputedTraceFilename__ = getFilenameFromConfigurationAndRepetition(indexFile, 1)    
        
        ArrayOfDictTransitionIdsToValueSet.append(extractTransitionToBagOfTimesDictionaryFromTraceFile(__ComputedTraceFilename__))
        
        counterLoop = counterLoop + 1 

    return ArrayOfDictTransitionIdsToValueSet


        
        

    