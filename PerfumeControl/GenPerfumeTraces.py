#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  8 15:25:50 2019

@author: rafaelolaechea
"""

import numpy as np

import argparse

import MLConstants

from pickleFacade import loadObjectFromPickle

from ParseTrace import setBaseTracesSourceFolder, getFilenameFromConfigurationAndRepetition, getSingleFilenameWithAllTraces

from PerfumeControl.TraceConversionUtilities import extractTracesAfterReadingFrames, \
 getNumberTracesToSample, printSingleTracePerfumeFormat
 
import AutonomooseTraces
from AutonomooseTraces import IsRealTransitionForGivenConf
    
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

 
def generatePerfumeTracesX264(configurationId):
    """
    Extract a trace for a single X264 configuration
    """
    traceFilename = getFilenameFromConfigurationAndRepetition(configurationId, 1)
       
    tracesCounts, tracesTimes, collectedTimedTraces, tracesPositions = extractTracesAfterReadingFrames(traceFilename)

    traceId = 1
    for aTrace in tracesCounts.keys():
        
        numTracesToSample = 0
        
        numberTraces =  len(tracesPositions[aTrace])
        
        
        numTracesToSample = getNumberTracesToSample(numberTraces)
         
        
        lstPositions  = tracesPositions[aTrace]
        
        if len(lstPositions) > numTracesToSample:
            chosen = np.random.choice(lstPositions, size=numTracesToSample, replace=False, )
        else:
            chosen = lstPositions
        
        for tracePosition in chosen:
            printSingleTracePerfumeFormat (collectedTimedTraces[tracePosition], traceId)
            traceId = traceId + 1


def countAndPrintAutonomooseLoops(configurationId, tmpTransList, filenameToOutputTo=""):
    """
    Extract loops offsets and size. 
    Returns a list with them as tuples offset, size.
    
    """    
    START_LOOP_MARKER_ID = AutonomooseTraces.enumLocalizerTransition
    
    i  = 0
    initializedCurrentLoop = False
   
    fdOutput = open(filenameToOutputTo, "w")

    # Iterates through trace keeping current loop.
    #Each time START of loop is encounetered adds offset and size of current loop. 
    # Clears Current loop. 
    # Trailing loop must be later added.
    lstLoopStartAndSize = []
    while (i < len(tmpTransList)):
        aTransition = tmpTransList[i]
        
        if IsRealTransitionForGivenConf(aTransition.getTransitionId(), configurationId) and \
            START_LOOP_MARKER_ID == aTransition.getTransitionId() : 
               if initializedCurrentLoop == False:
                   initializedCurrentLoop = True
               else:
                   lstLoopStartAndSize.append((currentTransitionOffset, currentTransitionSize))               
               currentTransitionOffset = i
               currentTransitionSize = 1               
        else:
               currentTransitionSize = currentTransitionSize + 1
        i = i +1           
    lstLoopStartAndSize.append((currentTransitionOffset, currentTransitionSize))


    chosenLoops = [x for x in range(0, len(lstLoopStartAndSize))]#np.random.choice(range(0, len(lstLoopStartAndSize)), size=400, replace=False, )
    
    for aLoopIndex in chosenLoops:
        print("initial, 0", file=fdOutput)
        aLoopOffsetStart, aLoopOffsetSize =  lstLoopStartAndSize[aLoopIndex]
        aLoopOffsetEnd = aLoopOffsetStart + aLoopOffsetSize
        AccumulatedTimeInLoop = 0
        tmpTransSplit = tmpTransList[aLoopOffsetStart:aLoopOffsetEnd]
        for anAutonomooseTransition in tmpTransSplit:
            if IsRealTransitionForGivenConf(anAutonomooseTransition.getTransitionId(), configurationId):
                AccumulatedTimeInLoop =  AccumulatedTimeInLoop  + anAutonomooseTransition.getTimeTaken()
                print ("T_{0}, {1}".format(anAutonomooseTransition.getTransitionId(),AccumulatedTimeInLoop), file=fdOutput)
        print("END_TRACE", file=fdOutput)
    
    fdOutput.close()    
    return      lstLoopStartAndSize

def generatePerfumeTracesAutonomoose(LstConfigurationIds, sourceFolder):
    """
    Extract a transe for a single Autonomoose configuration (or list of Autonomoose configurations.) 
    
    
    TODO  -- how to partition an Autonomoose trace into "mini" traces.
    """       
    
            
        
    if sourceFolder.find("First") != -1:
        tmpTraceShorthand = "first"
    elif sourceFolder.find("Second") != -1:
        tmpTraceShorthand = "second"
    else:
        tmpTraceShorthand = "third"
        
    allTraces =   loadObjectFromPickle(getSingleFilenameWithAllTraces())
        
    for configurationId in LstConfigurationIds:
        AutonomooseTraceForConfiguration = allTraces[configurationId][0]
    
        tmpTransList = AutonomooseTraceForConfiguration.getTransitionList()
    

        
        filenameToOutputTo = "PerfumeControl/Traces/autonomoose_{0}_configuration_{1}".format(tmpTraceShorthand, configurationId)
        
        countAndPrintAutonomooseLoops(configurationId, tmpTransList, filenameToOutputTo)
    
    
#    print ("Number of Loops {0}".format(len(lstLoopStartAndSize)))      
#    print("Pending Loop = {0},{1}".format(currentTransitionOffset, currentTransitionSize))
#    print("FInal Transition  Id = {0}".format(tmpTransList[-1].getTransitionId()))
#    
#    print([x.getTransitionId() for x in tmpTransList[0:71]])
#
#    print("Pending")    
#    print([x.getTransitionId() for x in tmpTransList[currentTransitionOffset:currentTransitionOffset+currentTransitionSize]])    



if __name__ == "__main__":
    """
    Extracting set of traces for a single product.
    """
    args = parseArguments()
       
    subjectSystem = args.subjectSystem

    setBaseTracesSourceFolder(args.sourceFolder)
        
    
    
    if MLConstants.x264Name == subjectSystem:    
        configurationId = int(args.configurationId)
    
        generatePerfumeTracesX264(configurationId)
    
    else:
        LstConfigurationIds = [int(x) for x in args.configurationId.split(",")]
        
        generatePerfumeTracesAutonomoose(LstConfigurationIds, args.sourceFolder)
    

 

        
    
