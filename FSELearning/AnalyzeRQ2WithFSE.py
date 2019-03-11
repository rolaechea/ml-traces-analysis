#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 15:59:49 2019

@author: rafaelolaechea

Analyze RQ2 for X264 -- Sven Apels Code.
"""
import sys
import numpy as np

# Current hack until sorting out proper imports.
#sys.path.append("/Users/rafaelolaechea/phd-work/Section 3 - Learning/AnalyzeTracesCodebase/")



import MLConstants
from ConfigurationUtilities import mean_absolute_error_and_stdev_eff
from pickleFacade import loadObjectFromPickle
from ParseTrace import setBaseTracesSourceFolder, getSingleFilenameWithAllTraces


from FSELearning import InfluenceModels, MLSettings
from FSELearning  import FeatureSubsetSelection

from FSELearning.VariabilityModelUtilities import generateFullX264VariabilityModel,\
 transformSingleConfigurationToX264FSE, generateFullAutonomooseVariabilityModel, transformSingleConfigurationToAutonomooseFSE

from ConfigurationUtilities import generateBitsetForOneConfiguration
from AutonomooseTraces import generateBitsetForOneConfigurationAutonomoose, getOverallRealTimeForASingleTraceAutonomoose

X264_RANGE_START = 1
X264_RANGE_END = 11

MIN_NUM_ARGUMENTS = 3

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
        
        traceSummarizedTimesFilenameOrDirectoryName = inputParameters[4]

        
    else:    
        
        print_help()
        
        exit(0) 
        
    return SubjectSystem,   trainConfFilename, testConfFilename, traceSummarizedTimesFilenameOrDirectoryName


def transformToFSEFormat(lstConfIds, vm, ConfigurationIdToBitsetTransformer=generateBitsetForOneConfiguration, BitsetToFseTransformer=transformSingleConfigurationToX264FSE):
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
        bitsetConf = ConfigurationIdToBitsetTransformer(xConfiguration)
        #print("{0} :  {1}".format(xConfiguration, bitsetConf))
        lstTransformedList.append(BitsetToFseTransformer(xConfiguration, bitsetConf, vm))
        
    return lstTransformedList





def printInfluenceModel(tmpSubsetSelection):
    """
    Output each feature that is part of Influence model and each interaction.
    """
    mapBinaries = [(x.name,y.Constant) for x,y in tmpSubsetSelection.infModel.binaryOptionsInfluence.items()]
    print (mapBinaries)

    mapInfluence = [([z.name for z in x.binaryOptions],y.Constant) for x,y in tmpSubsetSelection.infModel.interactionInfluence.items()]
    print (mapInfluence)
        

def setNFPValuesForConfigurationList(lstFSEConfigurations, lseConfigurationsIdsList, traceExecutionTimesSummaries ):
    """
    Sets the NFP values for a list of FSE configurations from the traceExecutionTimesSummaries and configurationIds
    
    No return value, operates through side-effects
    """
    indexOffset = 0    
    for configurationId in lseConfigurationsIdsList:
        sumTimes = 0.0
        for repId in range(X264_RANGE_START, X264_RANGE_END):
            sumTimes +=     traceExecutionTimesSummaries[(configurationId, repId)]
        averageTimes = sumTimes / (X264_RANGE_END-X264_RANGE_START)
        lstFSEConfigurations[indexOffset].setNfpValue(averageTimes)
        indexOffset += 1

def setNFPValuesForConfigurationListAutonomoose(lstFSETrainConfigurationListing, trainConfigurationList, allTraces):
    """
    Clone of previous function
    """
    indexOffset = 0
    
    for aConfId in trainConfigurationList:
        sumTimes = 0.0
        for repetitionId in range(0, 10):
            
            CurrentExecutionTrace = allTraces[aConfId][repetitionId]
            
            sumTimes += getOverallRealTimeForASingleTraceAutonomoose(CurrentExecutionTrace, aConfId)
            
        averageTimes = sumTimes / 10.0 
        
        lstFSETrainConfigurationListing[indexOffset].setNfpValue(averageTimes)

        indexOffset += 1

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
    vmX264 = generateFullX264VariabilityModel()

    InfModelX264 = InfluenceModels.InfluenceModel(vmX264)
      
    TmpMLSettings = MLSettings.MLSettings()
    
    TmpMLSettings.useBackward = True
    
    lstFSETrainConfigurationListing = transformToFSEFormat(trainConfigurationList, vmX264)


    # Set average values for each configuration
    setNFPValuesForConfigurationList(lstFSETrainConfigurationListing, trainConfigurationList, traceExecutionTimesSummaries )

#    print (lstFSETrainConfigurationListing[0].getNfpValue())
#    for repId in range(X264_RANGE_START, X264_RANGE_END):
#        print (traceExecutionTimesSummaries[(trainConfigurationList[0], repId)])
#    #print(lstFSETrainConfigurationListing)
    
    
    tmpSubsetSelection =    FeatureSubsetSelection.FeatureSubsetSelection(InfModelX264, TmpMLSettings)
    
    tmpSubsetSelection.setLearningSet(lstFSETrainConfigurationListing)
    
    tmpSubsetSelection.setValidationSet(lstFSETrainConfigurationListing)  # Following FSE paper, Learning set is resued as 'validation set'.
                                        
    tmpSubsetSelection.learn()    
    
    showInfluenceModel = False    
    
    if showInfluenceModel:
        printInfluenceModel(tmpSubsetSelection)
    
    lstFSETestConfigurationListing = transformToFSEFormat(testConfigurationsList, vmX264)
    
    setNFPValuesForConfigurationList(lstFSETestConfigurationListing, testConfigurationsList, traceExecutionTimesSummaries )


    averagingTestSet = False
    
    if averagingTestSet == True:
        
        lstMeasuredValues = [x.getNfpValue() for x in lstFSETestConfigurationListing]
    
        lstEstimatedValues = [tmpSubsetSelection.infModel.estimate(x) for x in lstFSETestConfigurationListing]
            
        
        showVerboseDebugging = False
        if showVerboseDebugging:
            for indexOffset in range(5):
                print ("Configuration {0}".format(testConfigurationsList[indexOffset]))
                print ("Configuration wrt Options {0}".format([x.name for x in lstFSETestConfigurationListing[indexOffset].dctBinaryOptionValues.keys()]))
                print ("Measured Value {0}".format(lstMeasuredValues[indexOffset]))
                print ("Estimated Value {0}".format(lstEstimatedValues[indexOffset]))
    else:
        lstEstimatedValues = [tmpSubsetSelection.infModel.estimate(x) for x in lstFSETestConfigurationListing]
        
        lstMeasuredValues = []
        for aConfId in testConfigurationsList:
            for repetitionId in range(1, 11):
                
                executedTimes =   traceExecutionTimesSummaries[(aConfId, repetitionId)]
                
                lstMeasuredValues.append(executedTimes)

        tmpLstEstimatedValues = []
        for estimatedVal in lstEstimatedValues:
            for i in range(0, 10):
                tmpLstEstimatedValues.append(estimatedVal)

        lstEstimatedValues = tmpLstEstimatedValues        

    lstMeasuredValuesNp = np.array(lstMeasuredValues)
    lstEstimatedValuesNp = np.array(lstEstimatedValues)
 
    MAETestMean, MAETestStd = mean_absolute_error_and_stdev_eff(lstMeasuredValuesNp, lstEstimatedValuesNp)
    MEANTestVal = np.mean(lstMeasuredValuesNp)
    
    NormalizedMae =   100* (  MAETestMean /         MEANTestVal)

    print("MAE_TEST_MEAN, MAE_TEST_STD, MEAN_TEST, NOMRALIZED_MAE (%) ")
    print("{0},\t {1},\t {2},\t {3}".format(MAETestMean, MAETestStd, MEANTestVal, NormalizedMae))
    
     

def analyzeAutonomooseFSE(trainConfigurationList, testConfigurationsList):
    """
    Analyze execution time of autonomooose

    Parameters
    -----------
    traceExecutionTimesSummaries : Dictionary
    Maps tuples (confId, repetitionId) to execution time (microseconds)       

    trainConfigurationList : List of integers    
    testConfigurationsList : List of integers
    
    Notes
    ------
    
    1. Open all tracess files.
    
    BooleanOptions = [("BEHAVIOR", 4 ), \
                      ("OCCUPANCY", 2),
                      ("WAYPOINTS", 1)]

        Behavior Planner
        Occupancy or Mockupancy Planner
        Waypoints Collection
        Dyn. Object Tracking
        Dyn. Car Tracking.
        Dyn. Person Tracking
        
        
    TODO - REFACTOR to join it into analyzeX264FSE -- strategy pattern.
        
    """
    allTraces =    loadObjectFromPickle(getSingleFilenameWithAllTraces())
       
    vmAutonomoose = generateFullAutonomooseVariabilityModel()

    InfModelAutonomoose = InfluenceModels.InfluenceModel(vmAutonomoose)
      
    TmpMLSettings = MLSettings.MLSettings()
    
    TmpMLSettings.useBackward = True

    
    lstFSETrainConfigurationListing = transformToFSEFormat(trainConfigurationList, vmAutonomoose, \
        ConfigurationIdToBitsetTransformer=generateBitsetForOneConfigurationAutonomoose, \
        BitsetToFseTransformer=transformSingleConfigurationToAutonomooseFSE)   
    
    
    setNFPValuesForConfigurationListAutonomoose(lstFSETrainConfigurationListing, trainConfigurationList, allTraces)

    tmpSubsetSelection =    FeatureSubsetSelection.FeatureSubsetSelection(InfModelAutonomoose, TmpMLSettings)
    
    tmpSubsetSelection.setLearningSet(lstFSETrainConfigurationListing)
    
    tmpSubsetSelection.setValidationSet(lstFSETrainConfigurationListing)  # Following FSE paper, Learning set is resued as -- 'validation set' --
                                        
    tmpSubsetSelection.learn()    
    
    showInfluenceModel = False    
    
    if showInfluenceModel:
        printInfluenceModel(tmpSubsetSelection)
    
    lstFSETestConfigurationListing = transformToFSEFormat(testConfigurationsList, vmAutonomoose, \
        ConfigurationIdToBitsetTransformer=generateBitsetForOneConfigurationAutonomoose, \
        BitsetToFseTransformer=transformSingleConfigurationToAutonomooseFSE)
    
    
    #
    #
    #
    # CALCULATING NMAE WITHOUT USING AVERAGING.
    
    averagingTestSet = False
    
    if averagingTestSet == True:
        setNFPValuesForConfigurationListAutonomoose(lstFSETestConfigurationListing, testConfigurationsList, allTraces)
        
        lstMeasuredValues = [x.getNfpValue() for x in lstFSETestConfigurationListing]
        
    
        lstEstimatedValues = [tmpSubsetSelection.infModel.estimate(x) for x in lstFSETestConfigurationListing]
    else:
        lstMeasuredValues = []
        for aConfId in testConfigurationsList:
            for repetitionId in range(0, 10):
                
                executedTimes =  getOverallRealTimeForASingleTraceAutonomoose(allTraces[aConfId][repetitionId], aConfId)
                
                lstMeasuredValues.append(executedTimes)
        
        lstEstimatedValues = [tmpSubsetSelection.infModel.estimate(x) for x in lstFSETestConfigurationListing]
        
        tmpLstEstimatedValues = []
        for estimatedVal in lstEstimatedValues:
            for i in range(0, 10):
                tmpLstEstimatedValues.append(estimatedVal)

        lstEstimatedValues = tmpLstEstimatedValues
                

    lstMeasuredValuesNp = np.array(lstMeasuredValues)
    lstEstimatedValuesNp = np.array(lstEstimatedValues)
 
    MAETestMean, MAETestStd = mean_absolute_error_and_stdev_eff(lstMeasuredValuesNp, lstEstimatedValuesNp)
    MEANTestVal = np.mean(lstMeasuredValuesNp)
    
    NormalizedMae =   100* (  MAETestMean /         MEANTestVal)

    print("MAE_TEST_MEAN, MAE_TEST_STD, MEAN_TEST, NOMRALIZED_MAE (%) ")
    print("{0},\t {1},\t {2},\t {3}".format(MAETestMean, MAETestStd, MEANTestVal, NormalizedMae))
    
          
if __name__ == "__main__":
    """
    Execute FSE paper for X264 / Autonomooose.    
    
    
    Testing --
    
    akiyo/traceExecutionTimesForAll.pkl
    
    """
    SubjectSystem, trainConfFilename, testConfFilename, traceSummarizedTimesFilenameOrDirectoryName = parseRuntimeParemeters(sys.argv)
    
    trainConfigurationList, testConfigurationsList = loadObjectFromPickle(trainConfFilename), \
        loadObjectFromPickle(testConfFilename)
    
    if SubjectSystem == MLConstants.x264Name:
            
        traceExecutionTimesSummaries =  loadObjectFromPickle(traceSummarizedTimesFilenameOrDirectoryName)
        
        analyzeX264FSE(trainConfigurationList, testConfigurationsList, traceExecutionTimesSummaries)
        
    else:
        #traceSummarizedTimesFilenameOrDirectoryName "../FullTraces/autonomooseFirst/"

        setBaseTracesSourceFolder(traceSummarizedTimesFilenameOrDirectoryName)
        
        analyzeAutonomooseFSE(trainConfigurationList, testConfigurationsList)  

        
