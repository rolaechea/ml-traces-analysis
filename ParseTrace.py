#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 10:51:56 2018

@author: rafaelolaechea
"""



__TraceDirectory__ = "../FullTraces/akiyo/"
__ComputedTraceFilename__ = "traceName.txt"

__BaseTraceFilename__ = "conf-%d-rep-%d-timing.txt"






def getTestSetSamplingRatiosDict():
    """
    Assuming test size testSetSize= 2304-460
    """
    dictRet = {4: 0.08902, 5:0.00023,  6:0.09038, 7:0.09038, \
               8:0.09008, 9:0.01369, 10:0.00147, 11:0.00061, 12:0.00050, \
               13:0.01263, 14:0.00090, 15:0.00110, 18:0.00050, 19:0.00261,\
               20:0.00337, 21:0.00131, 23:0.01540, 24:0.00679, 25:0.00679,\
               27:0.01214, 28:0.00050, 33:0.00023, 34:0.01214 }
    
    return dictRet
    
    
                             
def getAllTransitionsIdsList():
    """
    Returns a list of all transitions for which we measure the timing information.
    """
    return [x for x in getTestSetSamplingRatiosDict().keys() ]

 
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


def sumTimeTakenPerTransitionFromConfigurationAndRep(configurationId, repId):
    
    traceFilename = getFilenameFromConfigurationAndRepetition(configurationId, repId)

    fTrace = open(traceFilename, 'r')

    dictTransitionTimeTotalTimeTaken = {}
    
    for line in fTrace:
#            print (line.rstrip())
        transitionId, timeTaken = line.rstrip().split(":")
    
        existintTimeTakenList = dictTransitionTimeTotalTimeTaken.get(int(transitionId))
        
        # Add time if transition already exists, otherwise insert time.
        if existintTimeTakenList==None:
            dictTransitionTimeTotalTimeTaken[int(transitionId)] = (1, int(timeTaken))
        else:
            dictTransitionTimeTotalTimeTaken[int(transitionId)] =  (dictTransitionTimeTotalTimeTaken[int(transitionId)][0] + 1 , dictTransitionTimeTotalTimeTaken[int(transitionId)][1] + int(timeTaken))

    fTrace.close()
    
    return dictTransitionTimeTotalTimeTaken
            

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


        
        

    
