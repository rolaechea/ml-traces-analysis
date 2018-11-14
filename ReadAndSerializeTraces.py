#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 10:54:51 2018

@author: rafaelolaechea
"""
import sys
import pickle



from ParseTrace import getFilenameFromConfigurationAndRepetition, extractTransitionToBagOfTimesDictionaryFromTraceFile


if __name__ == "__main__":
    if  len(sys.argv) > 1:
         # First parameter is size of training set
         FilesList = [int(configurationId) for  configurationId in (sys.argv[1].split(','))]
    else:        
        print(" Invalid Usage  - requires a list of configuration ids as first argument")
        exit(0)

    ArrayOfDictTransitionIdsToValueSet = []    
    for configurationId in FilesList:
        for repId in range(1,11):            
            traceFilename = getFilenameFromConfigurationAndRepetition(configurationId, repId)
            
            print("Parsing Configuration {0} repetition {1} trace Filename {2}".format(configurationId, repId, traceFilename))
            AllFilteredTransitions = extractTransitionToBagOfTimesDictionaryFromTraceFile(traceFilename, filterTransition=True, TransitionsToFilter=frozenset([4,6,7,8,9,13,22,23,27,31,34]))
            print (" Num Transitions {0} - Num elements {1} ".format(len(AllFilteredTransitions.keys()), sum([len(x) for x in AllFilteredTransitions.values()])))
#            print("Transitions which executed {0}".format(AllFilteredTransitions.values()))
            ArrayOfDictTransitionIdsToValueSet.append(AllFilteredTransitions)
           

    output = open('unsampled-transitions.pkl', 'wb')
    pickle.dump(ArrayOfDictTransitionIdsToValueSet, output, pickle.HIGHEST_PROTOCOL)
    
    output.close()
    # Serialize reading
