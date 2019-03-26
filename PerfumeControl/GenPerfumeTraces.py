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


def countAutonomooseLoops(configurationId, tmpTransList):
    """
    Extract loops offsets and size. 
    Returns a list with them as tuples offset, size.
    
    """    
    START_LOOP_MARKER_ID = AutonomooseTraces.enumLocalizerTransition
    
    i  = 0
    initializedCurrentLoop = False
   

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


    return      lstLoopStartAndSize

def generatePerfumeTracesAutonomoose(configurationId):
    """
    Extract a transe for a single Autonomoose configuration (or list of Autonomoose configurations.) 
    
    
    TODO  -- how to partition an Autonomoose trace into "mini" traces.
    """       
    allTraces =   loadObjectFromPickle(getSingleFilenameWithAllTraces())
    
    AutonomooseTraceForConfiguration = allTraces[configurationId][0]
    
    tmpTransList = AutonomooseTraceForConfiguration.getTransitionList()
    
    
    lstLoopStartAndSize =  countAutonomooseLoops(configurationId, tmpTransList)
    
    
    print ("Number of Loops {0}".format(len(lstLoopStartAndSize)))  
    
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
        
    configurationId = int(args.configurationId)
    
    if MLConstants.x264Name == subjectSystem:    
    

    
        generatePerfumeTracesX264(configurationId)
    
    else:
        generatePerfumeTracesAutonomoose(configurationId)
    

 

        
    
