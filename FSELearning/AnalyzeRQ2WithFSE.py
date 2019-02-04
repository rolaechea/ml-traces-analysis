#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 15:59:49 2019

@author: rafaelolaechea

Analyze RQ2 for X264 -- Sven Apels Code.
"""
import sys


# Current hack until sorting out proper imports.
#sys.path.append("/Users/rafaelolaechea/phd-work/Section 3 - Learning/AnalyzeTracesCodebase/")


import MLConstants

from pickleFacade import loadObjectFromPickle


from FSELearning import InfluenceModels, MLSettings
from FSELearning  import FeatureSubsetSelection
from FSELearning.VariabilityModelUtilities import generateFullX264VariabilityModel, transformSingleConfigurationToX264FSE

from ConfigurationUtilities import generateBitsetForOneConfiguration

X264_RANGE_START = 1
X264_RANGE_END = 11

MIN_NUM_ARGUMENTS = 4

def print_help():
    print("AnalyzeRQ2WithFSE.py -- reimplments FSE paper of Sven Apel to compare answers for RQ2")
    print("Incorrect Arguments -- requires {0} arguments".format(MIN_NUM_ARGUMENTS))
    
def parseRuntimeParemeters(inputParameters):
    """
    Parse inputParameters
    Parses the following parameters:
        Subject System (x264 or Autonomoose)
        train set filename.
        test set filename.
        traces summary of times pkl file.        
    Returns
    -------
    Returns parsed values as a tuple.    
    """
    
    if  len(inputParameters) > MIN_NUM_ARGUMENTS:

        SubjectSystem = inputParameters[1]
         
        if SubjectSystem not in MLConstants.lstSubjectSystems:
             
            print ("Subject systems must be one of {0}".format(", ".join(MLConstants.lstSubjectSystems)))
             
            exit()

        trainConfFilename = inputParameters[2]
        
        testConfFilename = inputParameters[3]   
            
        traceSummarizedTimes = inputParameters[4]

        
    else:    
        
        print_help()
        
        exit(0) 
        
    return SubjectSystem,   trainConfFilename, testConfFilename, traceSummarizedTimes


def transformToFSEFormat(lstConfIds, vm):
    """
    Transform a listin of configurations ids from the bitmap format to the FSE format.
    
    Parameters:
    -----------
    lstConfIds : List of integer ids.      
    
    Returns
    -------
    List of Equivalent X264 Configurations.
    
    """
#    print ("lstConfIds Transforming {0}".format(str(lstConfIds[0:5])))

    lstTransformedList = []
    for xConfiguration in lstConfIds:#[0:5]:
        bitsetConf = generateBitsetForOneConfiguration(xConfiguration)
        #print("{0} :  {1}".format(xConfiguration, bitsetConf))
        lstTransformedList.append(transformSingleConfigurationToX264FSE(xConfiguration, bitsetConf, vm))
        
    return lstTransformedList


def loadResults(lstTransformedConfigurations, lstOriginalConfsIds, dctConfIdToResult):
    """
    Include NFP value into transformed configuration.
    """
    
def analyzeX264FSE(trainConfigurationList, testConfigurationsList, traceExecutionTimesSummaries):
    """
    Analyze x264 executions using FSE paper.

    Parameters
    -----------
    traceExecutionTimesSummaries : Dictionary
    Maps tuples (confId, repetitionId) to execution time (microseconds)       

    trainConfigurationList : List of integers    
    testConfigurationsList : List of integers
    """
    
    dctTraceExecutedTimesKeys = [x for x in traceExecutionTimesSummaries.keys()]
     
    vmX264 = generateFullX264VariabilityModel()

    InfModelX264 = InfluenceModels.InfluenceModel(vmX264)
      
    TmpMLSettings = MLSettings.MLSettings()
    
    TmpMLSettings.useBackward = True
    
    lstFSETrainConfigurationListing = transformToFSEFormat(trainConfigurationList, vmX264)


    # Set average values for each configuration
    indexOffset = 0    
    for configurationId in trainConfigurationList:
        sumTimes = 0.0
        for repId in range(X264_RANGE_START, X264_RANGE_END):
            sumTimes +=     traceExecutionTimesSummaries[(configurationId, repId)]
        averageTimes = sumTimes / (X264_RANGE_END-X264_RANGE_START)
        lstFSETrainConfigurationListing[indexOffset].setNfpValue(averageTimes)
        indexOffset += 1

#    print (lstFSETrainConfigurationListing[0].getNfpValue())
#    for repId in range(X264_RANGE_START, X264_RANGE_END):
#        print (traceExecutionTimesSummaries[(trainConfigurationList[0], repId)])
#    #print(lstFSETrainConfigurationListing)
    
    
    tmpSubsetSelection =    FeatureSubsetSelection.FeatureSubsetSelection(InfModelX264, TmpMLSettings)
    
    tmpSubsetSelection.setLearningSet(lstFSETrainConfigurationListing)
    
    tmpSubsetSelection.setValidationSet(lstFSETrainConfigurationListing)
                                         # Following FSE paper, Learning set is resued as 'validation set'.

    tmpSubsetSelection.learn()    
    
    print("Completed Learning")

    mapBinaries = [(x.name,y.Constant) for x,y in tmpSubsetSelection.infModel.binaryOptionsInfluence.items()]
    print (mapBinaries)

    mapInfluence = [([z.name for z in x.binaryOptions],y.Constant) for x,y in tmpSubsetSelection.infModel.interactionInfluence.items()]
    print (mapInfluence)

    
if __name__ == "__main__":
    """
    Execute FSE paper for X264 / Autonomooose.    
    
    
    Testing --
    
    akiyo/traceExecutionTimesForAll.pkl
    
    """
    SubjectSystem, trainConfFilename, testConfFilename, traceSummarizedTimesFilename = parseRuntimeParemeters(sys.argv)
    
    trainConfigurationList, testConfigurationsList, traceExecutionTimesSummaries = loadObjectFromPickle(trainConfFilename), \
        loadObjectFromPickle(testConfFilename), loadObjectFromPickle(traceSummarizedTimesFilename)
    
    if SubjectSystem == MLConstants.x264Name:
    
        analyzeX264FSE(trainConfigurationList, testConfigurationsList, traceExecutionTimesSummaries)
        
    else:
        
        raise NotImplementedError()
        
