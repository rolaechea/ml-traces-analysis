#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 12:00:41 2018

@author: rafaelolaechea
"""
import sys

import numpy as np

from sklearn.preprocessing import  StandardScaler

import MLConstants
from ConfigurationUtilities import generateBitsetForOneConfiguration, transformFeatureBitmapsToIncludeSquares, mean_absolute_error_and_stdev_eff
from ParseTrace import  sumTimeTakenPerTransitionFromConfigurationAndRep
from pickleFacade import loadObjectFromPickle





def print_help():
    """
    Print statements explaining how program is used.
    
    Program reads through a list of test traces and predicts execution time based on execution counts, versus actual times. 
    
    """
    print("python AnalyzerRQ2.py regressors.pkl testConf.pkl")
    print("regressors.pkl pickled file containing one regressor for each transition.")
    print("regressors.pkl pickled file containing an array of test configurations on which to evalaute the regressors.")
    
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


def getRegressorToTransitionIdMapping(regressorsArray):
    i = 0
    transitionToRegressorMapping = {}
    for aRegressor in regressorsArray:
        transitionToRegressorMapping[aRegressor.getTransitionId()] = i
        i = i + 1     
    return transitionToRegressorMapping


def predictTimeTakenForTrace():
    """
    Predicts the time to execute a trace on a specific product based on the execution counts and a set of regressors
    
    Returns - Number    
    """

def getPredictionsForTransitionsOnConfigurationList(testConfigurationsList, regressorsArray, transitionToRegressorMapping):
    """
    Given a regressor and a a transitions, returns a predictions for the execution time of that transitions.
    """
    XBitmaps =  [generateBitsetForOneConfiguration(aConf) for aConf in testConfigurationsList]
    
    tmpRegressor =   regressorsArray[transitionToRegressorMapping[transitionId]]
    
    if tmpRegressor.getUseSquareX():
        XBitmaps = transformFeatureBitmapsToIncludeSquares(XBitmaps)
            
    PredictedTransitionArray =  tmpRegressor.getScaler().inverse_transform(tmpRegressor.getRegressor().predict(XBitmaps))
    
    if tmpRegressor.isLasso():
        PredictedTransitionArray = np.array([[y] for y in PredictedTransitionArray]) # Fixing lasso returned vals.

    return PredictedTransitionArray
        

        
    



if __name__ == "__main__":
    if   len(sys.argv) > 2:
        
        regressorInputFilename = sys.argv[1]
        
        testConfFilename = sys.argv[2]                                
        
    else:    
        
        print_help()
        
        exit(0)
    
    regressorsArray, testConfigurationsList = loadObjectFromPickle(regressorInputFilename), loadObjectFromPickle(testConfFilename)

    transitionToRegressorMapping =  getRegressorToTransitionIdMapping(regressorsArray)


        
    transitionToConfArrayTimeTaken = {}    
    
    for transitionId  in transitionToRegressorMapping.keys():
        
        transitionToConfArrayTimeTaken[transitionId] = getPredictionsForTransitionsOnConfigurationList(testConfigurationsList, \
                                      regressorsArray, transitionToRegressorMapping)

        
    listActualTimes = []
    listPredictedTimes = []
    
    print("Configuration_Id, Actual Execution Time, Predicted Execution Time")
    
    for aConfId, offsetIndex  in zip(testConfigurationsList, range(0, len(testConfigurationsList))):

        timeTameknDict = sumTimeTakenPerTransitionFromConfigurationAndRep(aConfId,  1)
        
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

                   