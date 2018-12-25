#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 12:00:41 2018

@author: rafaelolaechea
"""
import sys

import numpy as np



import MLConstants

from ConfigurationUtilities import generateBitsetForOneConfiguration, transformFeatureBitmapsToIncludeSquares, mean_absolute_error_and_stdev_eff

from ParseTrace import  sumTimeTakenPerTransitionFromConfigurationAndRep, setBaseTracesSourceFolder, getSingleFilenameWithAllTraces

from pickleFacade import loadObjectFromPickle

from AutonomooseTraces import generateBitsetForOneConfigurationAutonomoose, getOverallRealTimeForASingleTraceAutonomoose


def print_help():
    """
    Print statements explaining how program is used.
    
    Program reads through a list of test traces and predicts execution time based on execution counts, versus actual times. 
    
    """
    print("python AnalyzerRQ2.py SubjecySystem regressors.pkl testConf.pkl")
    print("SubjecySystem either autonomoose or x264")
    print("regressors.pkl pickled file containing one regressor for each transition.")
    print("testConf.pkl pickled file containing an array of test configurations on which to evalaute the regressors.")
    
    
def check_accuracy_for_overall_time_prediction():
    """
    Check if we can analyze how long will a certain task take based on our counts
    """
    pass

def showTimeTaken(configurationId):
    """
    Given a configuration, list how much it took to execute each one based on two metrics:
        a. Add upp all transitions
        b. JSON file information.        
    """
    pass

def predictTimeTakenForTrace():
    """
    Predicts the time to execute a trace on a specific product based on the execution counts and a set of regressors
    
    Returns - Number    
    """
    pass



def getRegressorToTransitionIdMapping(regressorsArray):
    i = 0
    transitionToRegressorMapping = {}
    for aRegressor in regressorsArray:
        transitionToRegressorMapping[aRegressor.getTransitionId()] = i
        i = i + 1     
    return transitionToRegressorMapping



def getPredictionsForTransitionsOnConfigurationList(testConfigurationsList, regressorsArray, transitionToRegressorMapping,  transitionId, ConfigurationBitmapGenerator=generateBitsetForOneConfiguration):
    """
    Given a regressor and a  transition mapping, returns a predictions for the execution time of that transitions.
    """    
    XBitmaps =  [ConfigurationBitmapGenerator(aConf) for aConf in testConfigurationsList]
        
    tmpRegressor =   regressorsArray[transitionToRegressorMapping[transitionId]]

    CurrentRegressor = tmpRegressor.getRegressor() 
    
    if tmpRegressor.getUseSquareX():
        XBitmaps = transformFeatureBitmapsToIncludeSquares(XBitmaps)
    
    RawPredictions = CurrentRegressor.predict(XBitmaps)
    
    PredictedTransitionArray =  tmpRegressor.getScaler().inverse_transform(RawPredictions)
    
    if tmpRegressor.isLasso():
        PredictedTransitionArray = np.array([[y] for y in PredictedTransitionArray]) # Fixing lasso returned vals.

    return PredictedTransitionArray
        

        
    

MIN_NUM_ARGUMENTS = 4

def parseRuntimeParemeters(inputParameters):
    
    if  len(inputParameters) > MIN_NUM_ARGUMENTS:

        SubjectSystem = inputParameters[1]
         
        if SubjectSystem not in MLConstants.lstSubjectSystems:
             
            print ("Subject systems must be one of {0}".format(", ".join(MLConstants.lstSubjectSystems)))
             
            exit()
            
        TraceSourceFolder = inputParameters[2]

        regressorInputFilename = inputParameters[3]
        
        testConfFilename = inputParameters[4]                                
        
    else:    
        
        print_help()
        
        exit(0) 
        
    return SubjectSystem,   TraceSourceFolder, regressorInputFilename, testConfFilename

def analyzeOverallExecutionTimesX264(regressorsArray, testConfigurationsList, transitionToRegressorMapping, transitionToConfArrayTimeTaken):
    """
    Calculate time taken for each execution in confs that are part of test set.
    """            
    listActualTimes = []
    listPredictedTimes = []
        
    for aConfId, offsetIndex  in zip(testConfigurationsList, range(0, len(testConfigurationsList))):
    
        for repetitionId in range(0, 10):
            timeTameknDict = sumTimeTakenPerTransitionFromConfigurationAndRep(aConfId,  repetitionId)
            
            timeTakenByTraceAddition = sum([timeTameknDict[x][MLConstants.tupleTimeOffset] for x in timeTameknDict.keys()])
            
            predictedTimeTaken = 0
            
            for foundTransitionId in timeTameknDict.keys():
                if foundTransitionId in transitionToRegressorMapping.keys():
                    predictedTimeTaken = predictedTimeTaken + (transitionToConfArrayTimeTaken[foundTransitionId][offsetIndex]*timeTameknDict[foundTransitionId][MLConstants.tupleCountOffset])
        
                
            print("{0},{1},{2}".format(aConfId, timeTakenByTraceAddition, predictedTimeTaken[0]))
    
            listActualTimes.append(timeTakenByTraceAddition)
    
            listPredictedTimes.append(predictedTimeTaken)
    
    npActualTimes = np.array([np.array([x]) for x in listActualTimes])
    npPredictedTimes = np.array(listPredictedTimes)
        
    meanMAE, stdMAE = mean_absolute_error_and_stdev_eff(npActualTimes, npPredictedTimes)
 
    print("Mean_MAE,MAE_STDEV")
    
    print("{0},{1}".format(meanMAE, stdMAE))


def analyzeOverallExecutionTimesAutonomoose(regressorsArray, testConfigurationsList, transitionToRegressorMapping, transitionToConfArrayTimeTaken):
    """
    Autonomoose all traces are in a single file.
    
    Calculate execution time for first trace of  autonomoose
    """
    listActualTimes = []
    listPredictedTimes = []
    
    allTraces =    loadObjectFromPickle(getSingleFilenameWithAllTraces())
            
#    print (len(testConfigurationsList))
    
    
    for aConfId, offsetIndex  in zip(testConfigurationsList, range(0, len(testConfigurationsList))):
        #print("Computing for Configuration {0} with offset Index = {1}".format(aConfId, offsetIndex))
        
        for repetitionId in range(0, 10):
            CurrentExecutionTrace = allTraces[aConfId][repetitionId]
            
            actualExecutionTime = getOverallRealTimeForASingleTraceAutonomoose(CurrentExecutionTrace, aConfId)
    

        
            transitionsCounts = CurrentExecutionTrace.getPerTransitionCounts()
            
            #print(transitionsCounts)
  
            predictedTimeTaken = 0.0
            
            for aTransitionId in transitionsCounts.keys():
                predictedTimeTaken = predictedTimeTaken + transitionsCounts[aTransitionId] * transitionToConfArrayTimeTaken[aTransitionId][offsetIndex]
            
            if not (type(predictedTimeTaken) == float):
                print("{0},{1},{2}".format(aConfId, actualExecutionTime, predictedTimeTaken[0]))
            else:
                
                print("{0},{1},{2}".format(aConfId, actualExecutionTime, predictedTimeTaken))                

            listActualTimes.append(actualExecutionTime)
        
            listPredictedTimes.append(predictedTimeTaken)            

    npActualTimes = np.array([np.array([x]) for x in listActualTimes])
    npPredictedTimes = np.array(listPredictedTimes)
        
    meanMAE, stdMAE = mean_absolute_error_and_stdev_eff(npActualTimes, npPredictedTimes)
 

    print("Mean_MAE,MAE_STDEV")
    
    if meanMAE.shape==(1,):
        print("{0},{1}".format(meanMAE[0], stdMAE[0])) 
    else:
        print("{0},{1}".format(meanMAE, stdMAE))    
    
    

    

if __name__ == "__main__":

    SubjectSystem, TraceSourceFolder, regressorInputFilename, testConfFilename = parseRuntimeParemeters(sys.argv)
    
    setBaseTracesSourceFolder(TraceSourceFolder)
    
    regressorsArray, testConfigurationsList = loadObjectFromPickle(regressorInputFilename), loadObjectFromPickle(testConfFilename)

    transitionToRegressorMapping =  getRegressorToTransitionIdMapping(regressorsArray)

    transitionToConfArrayTimeTaken = {}

   
    
    for transitionId  in transitionToRegressorMapping.keys():      
        if SubjectSystem == MLConstants.x264Name:
            transitionToConfArrayTimeTaken[transitionId] = getPredictionsForTransitionsOnConfigurationList(testConfigurationsList, \
                                      regressorsArray, transitionToRegressorMapping, transitionId)
        else:
            transitionToConfArrayTimeTaken[transitionId] = getPredictionsForTransitionsOnConfigurationList(testConfigurationsList, \
                                      regressorsArray, transitionToRegressorMapping, transitionId, generateBitsetForOneConfigurationAutonomoose)
            
    
    print("Configuration_Id, Actual Execution Time, Predicted Execution Time")
        
    if SubjectSystem == MLConstants.x264Name:

        analyzeOverallExecutionTimesX264(regressorsArray, testConfigurationsList, transitionToRegressorMapping, transitionToConfArrayTimeTaken)

    else:
        
        analyzeOverallExecutionTimesAutonomoose(regressorsArray, testConfigurationsList, transitionToRegressorMapping, transitionToConfArrayTimeTaken)
                   
