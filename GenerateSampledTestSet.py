#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 16:46:02 2018

@author: rafaelolaechea
"""
import sys


from pickleFacade import loadObjectFromPickle, saveObjectToPickleFile

from ParseTrace import getTransitionToBagOfTimesForAllRepsForAProduct, getTestSetSamplingRatiosDict, \
setBaseTracesSourceFolder, getSingleFilenameWithAllTraces

from TransitionDictionaryManipulations import downSampleSingleDictionary
import MLConstants



def getComplementSet(confSet, totalEleements=2304):
    complementSet = []
    for x in range(totalEleements):
        if x not in confSet:
            complementSet.append(x)
    return complementSet


MIN_NUM_ARGUMENTS = 4
  
def parseRuntimeParemeters(inputParameters):
    """
    Parses command-line arguments.
    If incorrect arguments, then prints error message and exit.  
    
    Arguments 
        Subject System -- autonomoose or x264
        
        
    """
#    x.py conf_train.pkl  sampled_assesment_pkl  test_conf   
    useDifferentialSamplingExtra = False
    useDifferentialSampling = False
    preExistingSampledConfsFilename= ""
    preExistingSampledDatasetFilename= ""
    preExistingSampledConfsFilenameExtra= ""
    preExistingSampledDatasetFilenameExtra = ""
    TraceSourceFolder = ""
    

    if   len(inputParameters) > 4:

        SubjectSystem = inputParameters[1]
         
        if SubjectSystem not in MLConstants.lstSubjectSystems:
             print ("Subject systems must be one of {0}".format(", ".join(MLConstants.lstSubjectSystems)))
             
             exit()        
        
        currentParamIndex = 1
        
        if SubjectSystem == MLConstants.autonomooseName:
            
            TraceSourceFolder = inputParameters[2]
            
            currentParamIndex = currentParamIndex + 1
            
        confTrainFilename = inputParameters[currentParamIndex + 1]        

        assesmentConfsFilename = inputParameters[currentParamIndex + 2]
        
        assesmentSampledFilename = inputParameters[currentParamIndex + 3]
        
        if len(inputParameters) > (currentParamIndex+4):
            
            useDifferentialSampling = True
            
            preExistingSampledConfsFilename = inputParameters[currentParamIndex + 4]
            
            preExistingSampledDatasetFilename =  inputParameters[currentParamIndex + 5]

        if len(inputParameters) > (currentParamIndex + 6):
            useDifferentialSamplingExtra = True

            preExistingSampledConfsFilenameExtra = inputParameters[currentParamIndex + 6]

            preExistingSampledDatasetFilenameExtra =  inputParameters[currentParamIndex + 7]        
    else:

        print("Incorrect usage -  requires >= 4/5 filenames parameters: Subject System, (Trace Folder for Moose), train conf pkl, test conf pkl, and test conf sampled,  . Optional 2 (or 4)  more for differential sampling, preceeded by subjectName and optional baseName for moose ")
        exit(0)

    return SubjectSystem, TraceSourceFolder, confTrainFilename, assesmentConfsFilename, assesmentSampledFilename, \
        useDifferentialSampling, preExistingSampledConfsFilename, preExistingSampledDatasetFilename, useDifferentialSamplingExtra, preExistingSampledConfsFilenameExtra, \
        preExistingSampledDatasetFilenameExtra        
        
      
if __name__ == "__main__":

    SubjectSystem, TraceSourceFolder, confTrainFilename, assesmentConfsFilename, assesmentSampledFilename, \
        useDifferentialSampling, preExistingSampledConfsFilename, preExistingSampledDatasetFilename, useDifferentialSamplingExtra, preExistingSampledConfsFilenameExtra, \
        preExistingSampledDatasetFilenameExtra = parseRuntimeParemeters(sys.argv)
        
    confsTrain = loadObjectFromPickle(confTrainFilename)
    
    if SubjectSystem == MLConstants.x264Name:

        confsTest = getComplementSet(confsTrain)    

         # X264 only preprocessing.       
        dictRatios = getTestSetSamplingRatiosDict()    
        
        if useDifferentialSampling:
            
            ConfsAleadySampled = loadObjectFromPickle(preExistingSampledConfsFilename)
            
            DatasetAlreadySampled = loadObjectFromPickle(preExistingSampledDatasetFilename)
        
        if useDifferentialSamplingExtra:
    
            ConfsAleadySampledExtra = loadObjectFromPickle(preExistingSampledConfsFilenameExtra)
    
            DatasetAlreadySampledExtra = loadObjectFromPickle(preExistingSampledDatasetFilenameExtra)            
        
    else:
        setBaseTracesSourceFolder(TraceSourceFolder)
        
        allTracesAutonomoose = loadObjectFromPickle(getSingleFilenameWithAllTraces())
                
        confsTest = getComplementSet(confsTrain, totalEleements=MLConstants.AutonomooseConfCount)

        
        
    saveObjectToPickleFile(assesmentConfsFilename, confsTest)
    

    


    DictionaryArray = []
    counter = 0
    
    for confId in confsTest:
        if SubjectSystem == MLConstants.x264Name:
            if counter % 10 == 0:
                print ("Sampling  {0} out of {1}".format(counter, len(confsTest)))
                
            if (useDifferentialSampling and confId in ConfsAleadySampled):
                
                indexOfConfid = ConfsAleadySampled.index(confId)
                
                DictionaryArray.append(DatasetAlreadySampled[indexOfConfid])
    
            elif  (useDifferentialSamplingExtra and confId in ConfsAleadySampledExtra):
    
                indexOfConfid = ConfsAleadySampledExtra.index(confId)
    
                DictionaryArray.append(DatasetAlreadySampledExtra[indexOfConfid])
                
            else:
    
                tmpDict = getTransitionToBagOfTimesForAllRepsForAProduct(confId)        
            
                sampledDict = downSampleSingleDictionary(tmpDict, dictRatios)
            
                DictionaryArray.append(sampledDict)
        else:
            # Extracting Autonomoose test data for given configuration
            
            lstAllTracesForConf  = allTracesAutonomoose[confId]
            
            dctTransitionsToExecutions = {}

            for anAutonomoseExecutionTrace in lstAllTracesForConf:
                #Each trace is AutonomooseTraces.ExecutionTraceAutonomoose
                anAutonomoseExecutionTrace.addExecutedTransitionsToDictionary(dctTransitionsToExecutions)
            
            DictionaryArray.append(dctTransitionsToExecutions)
                        
            
        counter = counter + 1            

    saveObjectToPickleFile(assesmentSampledFilename, DictionaryArray)
    

    
