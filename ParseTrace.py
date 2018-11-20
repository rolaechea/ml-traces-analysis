#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 10:51:56 2018

@author: rafaelolaechea
"""


import numpy as np

import pickle 

__TraceDirectory__ = "../FullTraces/akiyo/"
__ComputedTraceFilename__ = "traceName.txt"

__BaseTraceFilename__ = "conf-%d-rep-%d-timing.txt"


__trainingSetSize__ = 2304

__numberTransitions__ = 35

__transitionIds__ = [2,3,4,6,7,8, 9 ] 
# And 34 13, 31, 33, 5, 7, 4, 11, 14, 18, 30, 10, 16, 19, 17, 20, 32]

__currentRep__ = 1


def getSamplingRatiosDict():
    """
    Sampling Ratios for transitions 4 ... 34.
    """
    dictRet = {4: 0.07125, 5:0.00018,  6:0.07234, 7:0.07234, \
               8:0.07210, 9:0.01096, 10:0.00063, 11:0.00049, 12:0.00025, \
               13:0.01011, 14:0.00038, 15:0.00042, 18:0.00040, 19:0.00113,\
               20:0.00145, 21:0.00050, 23:0.00300, 24:0.00260, 25:0.00260,\
               28:0.00025, 33:0.00018, 34:0.00228 }
    
    return dictRet

                             
def saveObjectToPickleFile(OutputFilename, objectToSave):
    pkl_file = open(OutputFilename, 'wb')
    
    pickle.dump(objectToSave, pkl_file, pickle.HIGHEST_PROTOCOL)
    
    pkl_file.close()
    

    
def loadObjectFromPickle(InputFilename):
    """
    Given a filename for pkl file containing assesment, load it and return it.
    """

        
    pkl_file = open(InputFilename, 'rb')
    
    objectFromPickle = pickle.load(pkl_file)        
           
    pkl_file.close()  
    
    return objectFromPickle

 
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


def getTransitionToBagOfTimesForAllRepsForAProduct(configurationId):
    """
    Extracts all transitions of a set of files traceFilename rep_1 ... rep_n  for given configuration  into a single conf.  
    """
    __dictTransitionToTimesBag__ = {}
    for repId in range(1,11):  
        traceFilename = getFilenameFromConfigurationAndRepetition(configurationId, repId)
        fTrace = open(traceFilename, 'r')
        for line in fTrace:
            transitionId, timeTaken = line.rstrip().split(":")
                
            existintTimeTakenList = __dictTransitionToTimesBag__.get(int(transitionId))
        
            if existintTimeTakenList==None:
                __dictTransitionToTimesBag__[int(transitionId)] = [int(timeTaken)]
            else:
                __dictTransitionToTimesBag__[int(transitionId)].append(int(timeTaken))
        fTrace.close()
    return __dictTransitionToTimesBag__
    
def extractTransitionToBagOfTimesDictionaryFromTraceFile(traceFilename, filterTransition=False, TransitionsToFilter=0):
    """
    Inputs -- Filename
    Output -- Dictionary of Transition Ids to Time taken
    """
    __dictTransitionToTimesBag__ = {}
    
    fTrace = open(traceFilename, 'r')

    for line in fTrace:
#            print (line.rstrip())
        transitionId, timeTaken = line.rstrip().split(":")
        
        if filterTransition and (int(transitionId)  not in TransitionsToFilter):
            # skkip transition
            continue 
        existintTimeTakenList = __dictTransitionToTimesBag__.get(int(transitionId))
        
        if existintTimeTakenList==None:
            __dictTransitionToTimesBag__[int(transitionId)] = [int(timeTaken)]
        else:
            __dictTransitionToTimesBag__[int(transitionId)].append(int(timeTaken))
        
#    print ([(x, len(y), np.mean(y)) for x,y in   __dictTransitionToTimesBag__.items()])
    fTrace.close()
    
    return     __dictTransitionToTimesBag__



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


        
        

    