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

def generatePerfumeTracesAutonomoose(configurationId):
    """
    Extract a transe for a single Autonomoose configuration (or list of Autonomoose configurations.) 
    
    
    TODO  -- how to partition an Autonomoose trace into "mini" traces.
    """       
    allTraces =   loadObjectFromPickle(getSingleFilenameWithAllTraces())
    
    FirsTraceForConfiguration = allTraces[configurationId][0]
    
    print (type(FirsTraceForConfiguration))
    



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
    

 

        
    
