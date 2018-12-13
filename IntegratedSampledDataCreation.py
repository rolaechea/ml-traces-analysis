#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 22:05:10 2018

@author: rafaelolaechea
"""
import sys



from pickleFacade import saveObjectToPickleFile, loadObjectFromPickle

from ParseTrace import getFilenameFromConfigurationAndRepetition, extractTransitionToBagOfTimesDictionaryFromTraceFile, \
setBaseTracesSourceFolder, getSingleFilenameWithAllTraces

from TransitionDictionaryManipulations import conjoinRepetedDictionaries, calculatePerTransitionsCounts, addCountDictionaries, \
downSampleToNewMaxExecutions

import MLConstants

from ConfigurationUtilities import getAllPossibleIds
from sklearn.model_selection import train_test_split
from subprocess import call

temporaryFilenameTemplate = "tmpFile_{0}.pkl"


MIN_NUM_ARGUMENTS = 5
NUM_TEMPORARY_PARTS = 23
NUM_REPETITIONS_PER_TRACE = 10




def parseRuntimeParemeters(inputParameters):
    """
    Parses command-line arguments.
    If incorrect arguments, then prints error message and exit.  
    
    Arguments 
        Subject System -- autonomoose or x264
        
        
    """
    verboseDebug = False
    TraceSourceFolder = ""
    
    if  len(inputParameters) > MIN_NUM_ARGUMENTS:
         # First parameter is size of training set, 2nd is name of configurationFile
         SubjectSystem = inputParameters[1]
         
         if SubjectSystem not in MLConstants.lstSubjectSystems:
             print ("Subject systems must be one of {0}".format(", ".join(MLConstants.lstSubjectSystems)))
             
             exit()
             
         TraceSourceFolder = inputParameters[2]
             
         TrainingConfSize = int(inputParameters[3])
         
         TrainingConfFilename = inputParameters[4]
         
         OutputFilename = inputParameters[5]
         
         if len(inputParameters) > (MIN_NUM_ARGUMENTS+1) and inputParameters[6] == "debug":
             verboseDebug = True
    else:        
        
        print(" Incorrect Usage. Requires three parameters: # of configurations in train. size, file to save training set ids, file to save filtered dataset and optional debug parameter")
        exit()
    
    return SubjectSystem, TraceSourceFolder, TrainingConfSize,  TrainingConfFilename, OutputFilename, verboseDebug



def extractAndSampleBySectionsFromTraces(TrainingSetConfigurations, TrainingConfSize,TrainingConfFilename, OutputFilenamem, verboseDebug):
    """
    Generate a file that includes up to 500 000 executions of each transition for each configuraiton in TrainingSetConfigurations.
    """
    if  verboseDebug:
        # free only exists in linux
        print("Memory Information at Program Launch ")
        call(["free", "-h"])
        
    globalCounts = {}

    for outerPart in range(0, NUM_TEMPORARY_PARTS):

        transitionArrayOfDictionary = []    

        smallSet = TrainingSetConfigurations[outerPart*20:(outerPart*20)+20]

        if verboseDebug:
            print("At subloop {0}, memory status :".format(outerPart))
            call(["free", "-h"])        

        for configurationId in smallSet:
 
            for repId in range(1, NUM_REPETITIONS_PER_TRACE+1):            

                traceFilename = getFilenameFromConfigurationAndRepetition(configurationId, repId)

                AllTransitions = extractTransitionToBagOfTimesDictionaryFromTraceFile(traceFilename )

                transitionArrayOfDictionary.append(AllTransitions)
        
        if verboseDebug:
            print("Possible Peak subloop memory at loop  {0}".format(outerPart))
            call(["free", "-h"])
        
        mergedDictionary  = conjoinRepetedDictionaries(transitionArrayOfDictionary)

        transitionArrayOfDictionary = []
        
        if verboseDebug:
            print("Possible Peak subloop memory at loop  {0}".format(outerPart))
            call(["free", "-h"])
                                
        allCounts = calculatePerTransitionsCounts(mergedDictionary)

        if verboseDebug:
            print (allCounts)

        addCountDictionaries(globalCounts, allCounts)

        if verboseDebug:
            print("Will save Dict of length = {0}".format(len(mergedDictionary)))
        
        saveObjectToPickleFile(temporaryFilenameTemplate.format(outerPart), mergedDictionary)       

        transitionArrayOfDictionary = [] 
        AllTransitions = []
        mergedDictionary = []
        allCounts = {}
        
        if verboseDebug:
            print("Memory After Clean Up")
            call(["free", "-h"])
    
    
    if verboseDebug:
        print("Completed")
        print ("globalCounts: {0}".format(globalCounts))
    
    if verboseDebug:
        print("Final Memory Before Shutdown")
        call(["free", "-h"])

    
    GlobalTmpFinalArray = []      
    for outerIndex in range(0, NUM_TEMPORARY_PARTS):
        if verboseDebug:
            print("Memory Start Loading Loop at {0}".format(outerIndex))
            call(["free", "-h"])         
        
        unsampledMergedDictArray = loadObjectFromPickle(temporaryFilenameTemplate.format(outerIndex))
        
        if verboseDebug:
            print("Loading Memory Peak I at {0}".format(outerIndex))
            call(["free", "-h"])        
        
        TmpFinalArrayDict = downSampleToNewMaxExecutions(unsampledMergedDictArray, actualCountsDictionary=globalCounts)

        if verboseDebug:
            print("Loading Memory Peak II at {0}".format(outerIndex))
            call(["free", "-h"])
        
        unsampledMergedDictArray = []
        
        GlobalTmpFinalArray.extend(TmpFinalArrayDict)
        
        TmpFinalArrayDict = []
        
        if verboseDebug:
            print("Reloading Memory Final at {0}".format(outerIndex))
            call(["free", "-h"])
    
    if verboseDebug:
         print("Saving Final Dictionary of length {0}".format(len(GlobalTmpFinalArray)))
         
    saveObjectToPickleFile(OutputFilename, GlobalTmpFinalArray)    


def extractTracesFromSinglePKL(TrainingSetConfigurations, TrainingConfSize, TrainingConfFilename, OutputFilenamem, verboseDebug):
    """    
    Receive Encoding of traces for each  configuration    
    """
    
    allTracesAutonomoose = loadObjectFromPickle(getSingleFilenameWithAllTraces())
    
    GlobalTmpArray = []
    
    for configurationId in TrainingSetConfigurations:        
        print ("Processing {0}".format(configurationId))
#        print ("Configuration {0}, Number of Traces {1} ".format(configurationId, len(allTracesAutonomoose[configurationId])))
        
        lstAllTracesForConf  = allTracesAutonomoose[configurationId]
        
        dctTransitionsToExecutions = {}
        
        for anAutonomoseExecutionTrace in lstAllTracesForConf:
            #Each trace is AutonomooseTraces.ExecutionTraceAutonomoose
            anAutonomoseExecutionTrace.addExecutedTransitionsToDictionary(dctTransitionsToExecutions)
        
#            print ("After processing an  execution of type {0}, we have a dicitonary with {1} elements".format(type(anAutonomoseExecutionTrace), \                   
#                   sum([len(dctTransitionsToExecutions[x]) for x in dctTransitionsToExecutions.keys()])))
        
        print (dctTransitionsToExecutions.keys())
        
        GlobalTmpArray.append(dctTransitionsToExecutions)
        
    saveObjectToPickleFile(OutputFilename, GlobalTmpArray)

if __name__ == "__main__":
    
    
    
    SubjectSystem, TraceSourceFolder, TrainingConfSize,  TrainingConfFilename, OutputFilename, verboseDebug = parseRuntimeParemeters(sys.argv)
    
    setBaseTracesSourceFolder(TraceSourceFolder)

    if SubjectSystem == MLConstants.x264Name:
        
        TestsetConfigurationSize = 2304-TrainingConfSize

        TrainingSetConfigurations = train_test_split(getAllPossibleIds(MLConstants.x264Id), getAllPossibleIds(MLConstants.x264Id),\
                                                                                                      train_size=TrainingConfSize, test_size=TestsetConfigurationSize)[0]        
    elif SubjectSystem == MLConstants.autonomooseName:

        TestsetConfigurationSize = 32-TrainingConfSize
            
        TrainingSetConfigurations = train_test_split(getAllPossibleIds(MLConstants.autonomooseId), getAllPossibleIds(MLConstants.autonomooseId),\
                                                 train_size=TrainingConfSize, test_size=TestsetConfigurationSize)[0]
       
    saveObjectToPickleFile(TrainingConfFilename, TrainingSetConfigurations)

    if SubjectSystem == MLConstants.x264Name:
        
        extractAndSampleBySectionsFromTraces(TrainingSetConfigurations, TrainingConfSize,TrainingConfFilename, OutputFilename, verboseDebug)
        
    elif SubjectSystem == MLConstants.autonomooseName:
        
        extractTracesFromSinglePKL(TrainingSetConfigurations, TrainingConfSize,TrainingConfFilename, OutputFilename, verboseDebug)
        
