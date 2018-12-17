#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 16:37:41 2018


Assees the learnt functions for each transition.
 We asses the accuracy of  a regressor learnt on the traininig set, with data from the test set.


@author: rafaelolaechea
"""


import sys
import numpy as np



from sklearn.preprocessing import  StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso

import MLConstants

from MLConstants import alphaValues
from pickleFacade import loadObjectFromPickle

from ParseTrace import  getAllTransitionsIdsList

from ConfigurationUtilities import   mean_absolute_error_and_stdev_eff

from RegressorsUtils import getBestMethodPerTransition, getXBitmapsForRegression

from TransitionDictionaryManipulations import  extractLinearArrayTimeTakenForSingleTransition

from AutonomooseTraces import getListOfAvailableTransitionsAutonomoose, getSetOfExecutionTimesAutonomoose



def learnRegressorFromDataset(regressorTypeToLearn, transitionId, YSet, confsList):
    """
    Calculates the regressor that CV found to be the best using all the data from training
    """    
    RegressionType = regressorTypeToLearn[0]
    UseSquares = regressorTypeToLearn[1]
    AlphaIndex = regressorTypeToLearn[2]
    

    
    SingleYList = []
    [ SingleYList.extend(YBag) for YBag in YSet]

    YLocalScaler =   StandardScaler()
     
    YLocalScaler.fit([[target] for target in  SingleYList])

    SingleYScaledList = YLocalScaler.transform ([[aY] for aY in SingleYList])

    XBitmaps = getXBitmapsForRegression(confsList, YSet, UseSquares)
    
    if  RegressionType == MLConstants.simpleRegression:
        Regressor = LinearRegression()
    elif RegressionType == MLConstants.ridgeRegression:
        Regressor = Ridge(alpha=alphaValues[AlphaIndex])
    elif RegressionType == MLConstants.lassoRegression:
        Regressor =  Lasso(alpha=alphaValues[AlphaIndex])
    
    Regressor.fit(XBitmaps, SingleYScaledList)
    
    YPredicted = YLocalScaler.inverse_transform(Regressor.predict(XBitmaps))

    YOriginalArray = np.array(SingleYList) 
    YOriginalArray.resize((len(SingleYList), 1))

    # Standarize as Lasso returns array of different shape than linear and ridge regression.    
    if RegressionType == MLConstants.lassoRegression:
        YPredicted.resize( (len(SingleYList), 1))
        
    MAPEYTrain, MAPEStdTrain = mean_absolute_error_and_stdev_eff(YOriginalArray, YPredicted)
          
    return Regressor, UseSquares, RegressionType == MLConstants.lassoRegression, YLocalScaler, YLocalScaler.mean_,  np.sqrt(YLocalScaler.var_), MAPEYTrain, MAPEStdTrain


def calculateTestErrors(Regressor, RegressorUseSquares, RegressorIsLasso,  YLocalScaler, transitionId, YSet, testOrderedConfs):
    """
    given a regressor function, calculates the error of such regressor on the test sets.
    Computes MAE_Test and MAE_Test std. dev across products.
    """    
    SingleYList = []
    [ SingleYList.extend(YBag) for YBag in YSet]    
    
    YTestOriginalArray = np.array(SingleYList); YTestOriginalArray.resize((len(SingleYList), 1))
    
    XBitmaps = getXBitmapsForRegression(testOrderedConfs, YSet, RegressorUseSquares)

    YTestPredicted = YLocalScaler.inverse_transform(Regressor.predict(XBitmaps))
    
#    print("Shape Y_TestOriginal {0}".format( YTestOriginalArray.shape))
    if RegressorIsLasso:
        YTestPredicted.resize( (len(SingleYList), 1))        
    
#    print("Shape Y_TestPredicted {0}".format( YTestPredicted.shape))
    MAPEYTest, MAEYStdDevTest = mean_absolute_error_and_stdev_eff(YTestOriginalArray, YTestPredicted)
    
               
    return np.mean(YTestOriginalArray), np.std(YTestOriginalArray), MAPEYTest, MAEYStdDevTest

    
def assessLearntRegressor():
    pass


def parseRuntimeParemeters(inputParameters):
    """
    Parses command-line arguments.
    If incorrect arguments, then prints error message and exit.  
    
    Arguments 
        Subject System -- autonomoose or x264
    """
    if   len(inputParameters) > 6:

        SubjectSystem = inputParameters[1]
         
        if SubjectSystem not in MLConstants.lstSubjectSystems:
             print ("Subject systems must be one of {0}".format(", ".join(MLConstants.lstSubjectSystems)))
             
             exit() 
             
        trainDatasetFilename = inputParameters[2]
        
        trainConfFilename =  inputParameters[3]
        
        CvResultsFilename = inputParameters[4]
        
        testDatasetFilename = inputParameters[5] 
        
        testConfFilename =  inputParameters[6]
    else:
        print("Incorrect usage -  requires 6 filenames parameters: Subject System, train data set," \
              "train configurations, results of CV, test dataset, test configurations")
        exit(0)
        
    return  SubjectSystem, trainDatasetFilename, trainConfFilename, CvResultsFilename, testDatasetFilename, testConfFilename

        
if __name__ == "__main__":

    SubjectSystem, trainDatasetFilename, trainConfFilename, CvResultsFilename, testDatasetFilename, testConfFilename = parseRuntimeParemeters(sys.argv)
    
    bestRegressorPerTransition = getBestMethodPerTransition(CvResultsFilename)

    testDataset, testOrderedConfs, trainDataset, trainOrderedConfs = loadObjectFromPickle(testDatasetFilename), \
        loadObjectFromPickle(testConfFilename), loadObjectFromPickle(trainDatasetFilename),  loadObjectFromPickle(trainConfFilename)

    if SubjectSystem == MLConstants.x264Name:    

        transitionIdList = getAllTransitionsIdsList()

    else:
        # Autonomoose 
        transitionIdList = getListOfAvailableTransitionsAutonomoose(trainDataset)


        
    print ("Transition Id, YMean_Train, Y_Std_Train, MAE_Train, MAE_Std_Train, YMean_Test, Y_Std_Test, MAE_Test, MAE_Std_Test")
    for transitionId in transitionIdList:
        if (not (transitionId in bestRegressorPerTransition.keys())):
            continue
            
        if SubjectSystem == MLConstants.x264Name:
             YSetTrain = extractLinearArrayTimeTakenForSingleTransition(trainDataset, transitionId)
        else:
            YSetTrain = getSetOfExecutionTimesAutonomoose(trainDataset, transitionId, trainOrderedConfs)

             
        Regressor, RegressorUseSquares, RegressorIsLasso, YLocalScaler, YMeanTrain, YStdTrain, MAPEYTrain, MAPEStdTrain =  learnRegressorFromDataset(bestRegressorPerTransition[transitionId], \
                                                                                                                                            transitionId, YSetTrain, trainOrderedConfs )    
        if SubjectSystem == MLConstants.x264Name:
             YSetTest = extractLinearArrayTimeTakenForSingleTransition(testDataset, transitionId)
        else:
             YSetTest = getSetOfExecutionTimesAutonomoose(testDataset, transitionId, testOrderedConfs)


        YMeanTest,YStdTest, MAPEYTest, MAEYStdDevTest = calculateTestErrors(Regressor, RegressorUseSquares, RegressorIsLasso, YLocalScaler, transitionId, YSetTest, testOrderedConfs)
         
        print("{0},{1},{2},{3},{4},{5},{6},{7},{8}".format(transitionId, YMeanTrain[0], YStdTrain[0], MAPEYTrain, MAPEStdTrain, YMeanTest, YStdTest,  MAPEYTest, MAEYStdDevTest))
