#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  8 15:25:50 2019

@author: rafaelolaechea
"""

import numpy as np

import argparse


from ParseTrace import setBaseTracesSourceFolder, getFilenameFromConfigurationAndRepetition

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
        
        
        numTracesToSample = getNumberTracesToSample(numberTraces)
         
        
        lstPositions  = tracesPositions[aTrace]
        
        if len(lstPositions) > numTracesToSample:
            chosen = np.random.choice(lstPositions, size=numTracesToSample, replace=False, )
        else:
            chosen = lstPositions
        
        for tracePosition in chosen:
            printSingleTracePerfumeFormat (collectedTimedTraces[tracePosition], traceId)
            traceId = traceId + 1

        
    
