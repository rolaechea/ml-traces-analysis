#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 12:00:41 2018

@author: rafaelolaechea
"""
import sys
import random
import numpy as np

from sklearn.preprocessing import  StandardScaler

from ConfigurationUtilities import generateBitsetForOneConfiguration, transformFeatureBitmapsToIncludeSquares, mean_absolute_error_and_stdev_eff
from ParseTrace import  loadObjectFromPickle, sumTimeTakenPerTransitionFromConfigurationAndRep






def print_help():
    """
    Print statements explaining how program is used.
    
    Program reads through a list of test traces and predicts execution time based on execution counts, versus actual times. 
    
    """
    print("python AnalyzerRQ2.py regressors.pkl testConf.pkl")
    
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
def getRegressorToTransitionIdMapping(regressorsArray):
    i = 0
    transitionToRegressorMapping = {}
    for aRegressor in regressorsArray:
        transitionToRegressorMapping[aRegressor.getTransitionId()] = i
        i = i + 1     
    return transitionToRegressorMapping

#numTracesToPredictOverallTime = 20

tupleCountOffset = 0
tupleTimeOffset = 1
# Transition 27 has been ignored for some reason starting at testing.

if __name__ == "__main__":
    if   len(sys.argv) > 2:
        
        regressorInputFilename = sys.argv[1]
        
        testConfFilename = sys.argv[2]                                
        
    else:    
        
        print_help()
        
        exit(0)
    
    regressorsArray, testConfigurationsList = loadObjectFromPickle(regressorInputFilename), loadObjectFromPickle(testConfFilename)

    subsetConfigurationsToCheck  = testConfigurationsList #= random.sample(testConfigurationsList, numTracesToPredictOverallTime)

    transitionToRegressorMapping =  getRegressorToTransitionIdMapping(regressorsArray)
    
    transitionToConfArrayTimeTaken = {}

    for transitionId  in transitionToRegressorMapping.keys():
        XBitmaps =  [generateBitsetForOneConfiguration(aConf) for aConf in subsetConfigurationsToCheck]
        
        tmpRegressor =   regressorsArray[transitionToRegressorMapping[transitionId]]
        
        if tmpRegressor.getUseSquareX():
            XBitmaps = transformFeatureBitmapsToIncludeSquares(XBitmaps)
                
        PredictedTransitionArray =  tmpRegressor.getScaler().inverse_transform(tmpRegressor.getRegressor().predict(XBitmaps))
        
        if tmpRegressor.isLasso():
            PredictedTransitionArray = np.array([[y] for y in PredictedTransitionArray]) # Fixing lasso returned vals.
        
        transitionToConfArrayTimeTaken[transitionId] = PredictedTransitionArray

        
    listActualTimes = []
    listPredictedTimes = []
    
    print("Configuration_Id, Actual Execution Time, Predicted Execution Time")
    for aConfId, offsetIndex  in zip(subsetConfigurationsToCheck, range(0, len(subsetConfigurationsToCheck))):
        timeTameknDict = sumTimeTakenPerTransitionFromConfigurationAndRep(aConfId,1)
        
        timeTakenByTraceAddition = sum([timeTameknDict[x][tupleTimeOffset] for x in timeTameknDict.keys()])
        
        predictedTimeTaken = 0
        
        for foundTransitionId in timeTameknDict.keys():
            if foundTransitionId in transitionToRegressorMapping.keys():
                predictedTimeTaken = predictedTimeTaken + (transitionToConfArrayTimeTaken[foundTransitionId][offsetIndex]*timeTameknDict[foundTransitionId][tupleCountOffset])
        

                
        print("{0},{1},{2}".format(aConfId, timeTakenByTraceAddition, predictedTimeTaken[0]))
        listActualTimes.append(timeTakenByTraceAddition)
        listPredictedTimes.append(predictedTimeTaken)
    
    npActualTimes = np.array([np.array([x]) for x in listActualTimes])
    npPredictedTimes = np.array(listPredictedTimes)
        
    meanMAE, stdMAE = mean_absolute_error_and_stdev_eff(npActualTimes, npPredictedTimes)
    print("Mean_MAE,MAE_STDEV")
    
    print("{0},{1}".format(meanMAE, stdMAE))

                   