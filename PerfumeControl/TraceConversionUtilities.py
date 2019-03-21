#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 13:02:21 2019

@author: rafaelolaechea
"""

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
    fTrace = open(filename, 'r')

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
  
    
def getNumberTracesToSample(numberTraces):
    """
    We can't pass all traces to perfume as it can not handle them.
    """
    if numberTraces <= 10:
        numTracesToSample = numberTraces
    elif numberTraces <= 100:
        numTracesToSample = 10 + int(0.125*(numberTraces-10))
    elif numberTraces <= 1000:
        numTracesToSample = 21 + int(0.025*(numberTraces-110))
    elif numberTraces <= 10000: 
        numTracesToSample = 45 + int(0.00225*(numberTraces-1110))
    else:
        numTracesToSample = 65 + +int(0.0000625*(numberTraces-11110))
        
    return numTracesToSample

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