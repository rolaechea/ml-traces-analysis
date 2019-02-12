#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  8 15:25:50 2019

@author: rafaelolaechea
"""

import numpy as np

import argparse


from ParseTrace import setBaseTracesSourceFolder, getFilenameFromConfigurationAndRepetition



    
def parseArguments():
    """
    Returns an args object with parsed argument or throws an error and exit.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("subjectSystem")

    parser.add_argument("sourceFolder", help="folder from which full traces should be read")

    parser.add_argument("configurationId", help="configuration whose traces will be analysed")
    
    args = parser.parse_args()

    return args



def extractTracesAfterReadingFrames(filename):
    """
    Extracts the traces of events that happen after a frame starts being analyzed.
    
    
    Parameters
    ----------
    filename: String
    
    
    Returns
    -------
    Dictionary with all traces seen, and how many times each trace was seen.
    
    Notes
    -----
    
    Traces starts after seeing 8 followed by a 6.
    
    From the WFTS for X264 we know 
    
    8
    6
    Trace
    ...
    FINISH_ID (29,30,31,32)
    
    """
    fTrace = open(traceFilename, 'r')

    inTrace = False
    FinalTraceSignal = [29, 30, 31, 32]
    
    currentTrace = []
    currentTimedTrace = []
    
    tracesCounts = {}    
    tracesTimes = {}    
    uniqueTraces = set()
    tracesPositions = {}
    
    collectedTimedTraces = []    
    for line in fTrace:
        transitionId, timeTaken = line.rstrip().split(":")

        transitionId = int(transitionId)

        if transitionId == 8:
           inTrace = False

           prevIsEight = True
           
           continue
        elif transitionId == 6 and prevIsEight==True:

           currentTrace =[]

           currentTimedTrace = []

           currentTraceTimeTaken = 0
           
           inTrace = True
           
           prevIsEight = False
           continue
        else:
           prevIsEight = False
        
        if inTrace:
            if transitionId not in FinalTraceSignal:      
                currentTrace.append(transitionId) #, int(timeTaken)))
                currentTraceTimeTaken = currentTraceTimeTaken + int(timeTaken)
                currentTimedTrace.append( (transitionId, int(timeTaken)))
            else:
                uniqueTraces.add(tuple(currentTrace))
                
                if tuple(currentTrace) in tracesCounts.keys():
                    tracesCounts[tuple(currentTrace)] = tracesCounts[tuple(currentTrace)] + 1
                    tracesTimes[tuple(currentTrace)] = tracesTimes[tuple(currentTrace)] + int(currentTraceTimeTaken)
                    tracesPositions[tuple(currentTrace)].append(len(collectedTimedTraces))
                else:
                    tracesCounts[tuple(currentTrace)] =  1
                    tracesTimes[tuple(currentTrace)] = int(currentTraceTimeTaken)
                    tracesPositions[tuple(currentTrace)] = [len(collectedTimedTraces)]
                    
                #print("Adding Trace {0} ".format(currentTrace))
                collectedTimedTraces.append(currentTimedTrace)
                currentTrace = []
                currentTimedTrace = []
    
    fTrace.close()
    

    return tracesCounts, tracesTimes, collectedTimedTraces, tracesPositions
    

def printSingleTracePerfumeFormat(trace, traceId):
    """
    Prints a trace in format requested by Perfume.
    """
 #   print((trace, traceId))
    
    print("initial, 0 ")
    
    accumulatedTime = 0 
    for transitionid, time in trace:
        accumulatedTime = accumulatedTime + time 
        print("t_{0}, {1} ".format(transitionid, accumulatedTime))   
#        print("t_{0}, {1} , trace_{2} ".format(transitionid, accumulatedTime, traceId))
    print ("END_TRACE")
        
if __name__ == "__main__":
    """
    Extracting set of traces for a single product.
    """
    args = parseArguments()
    
    setBaseTracesSourceFolder(args.sourceFolder)
    
    configurationId = int(args.configurationId)

    traceFilename = getFilenameFromConfigurationAndRepetition(configurationId, 1)
       
    tracesCounts, tracesTimes, collectedTimedTraces, tracesPositions = extractTracesAfterReadingFrames(traceFilename)

    traceId = 1
    for aTrace in tracesCounts.keys():
        
        numTracesToSample = 0
        numberTraces =  len(tracesPositions[aTrace])
        if numberTraces <= 10:
            numTracesToSample = numberTraces
        elif numberTraces <= 100:
            numTracesToSample = 10 + int(0.5*(numberTraces-10))
        elif numberTraces <= 1000:
            numTracesToSample = 55 + int(0.25*(numberTraces-110))
        elif numberTraces <= 10000:
            numTracesToSample = 222 + int(0.0625*(numberTraces-1110))
        else:
            numTracesToSample = 777 + +int(0.000625*(numberTraces-11110))            
        
        lstPositions  = tracesPositions[aTrace]
        
        if len(lstPositions) > numTracesToSample:
            #print ("Will sample {} from {}".format(numTracesToSample, len(lstPositions)))
            chosen = np.random.choice(lstPositions, size=numTracesToSample, replace=False, )
            #print ("chosen were {0}".format(str(chosen)))
            #if len(lstPositions) <= 20:
            #    print("All were {0}".format(str(lstPositions)))
        else:
            chosen = lstPositions
        
        for tracePosition in chosen:
            printSingleTracePerfumeFormat (collectedTimedTraces[tracePosition], traceId)
            traceId = traceId + 1

        
    
