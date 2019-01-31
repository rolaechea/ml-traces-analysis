#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 15:59:49 2019

@author: rafaelolaechea

Analyze RQ2 for X264 -- Sven Apels Code.
"""
import sys


# Current hack until sorting out proper imports.
sys.path.append("/Users/rafaelolaechea/phd-work/Section 3 - Learning/AnalyzeTracesCodebase/")

import InfluenceModels, MLSettings
import FeatureSubsetSelection

import MLConstants
from VariabilityModelUtilities import generateFullX264VariabilityModel
from pickleFacade import loadObjectFromPickle





MIN_NUM_ARGUMENTS = 4

def print_help():
    print("AnalyzeRQ2WithFSE.py -- reimplments FSE paper of Sven Apel to compare answers for RQ2")
    print("Incorrect Arguments -- requires X arguments")
    
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


def transformToFSEFormat(lstConfIds):
    """
    Transform a listin of configurations ids from the bitmap format to the FSE format.
    
    Parameters:
    -----------
    lstConfIds : List of integer ids.        
    """
    return []


def loadResults(lstTransformedConfigurations, lstOriginalConfsIds, dctConfIdToResult):
    """
    Include NFP value into transformed configuration.
    """
    
def analyzeX264FSE(trainConfigurationList, testConfigurationsList, traceExecutionTimesSummaries):
    """
    Analyze x264 executions using FSE paper.
    """
    
     
    print(str(trainConfigurationList))

    print (len(traceExecutionTimesSummaries))

    print (traceExecutionTimesSummaries))
    for repId in range(1, 11):
        
        print (len(traceExecutionTimesSummaries[(repId-1)*10: repId*10]))
    exit(0)
    
    vmX264 = generateFullX264VariabilityModel()
    
    lstFSETrainConfigurationListing = transformToFSEFormat(trainConfigurationList)

    InfModelX264 = InfluenceModels.InfluenceModel(vmX264)

    TmpMLSettings = MLSettings.MLSettings()
    
    TmpMLSettings.useBackward = True
    
    tmpSubsetSelection =    FeatureSubsetSelection.FeatureSubsetSelection(InfModelX264, TmpMLSettings)
    
    tmpSubsetSelection.setLearningSet(lstFSETrainConfigurationListing)
    
    tmpSubsetSelection.setValidationSet(lstFSETrainConfigurationListing)
                                         # Following FSE paper, Learning set is resued as 'validation set'.
    print("Performing Learning")
    
    tmpSubsetSelection.learn()    
    
    print("Completed Learning")
    
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
        
