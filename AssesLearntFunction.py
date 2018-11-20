#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 16:37:41 2018

@author: rafaelolaechea
"""


import numpy as np
import sys


from sklearn.preprocessing import  StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso


from ParseTrace import getTransitionToBagOfTimesForAllRepsForAProduct, getSamplingRatiosDict, loadObjectFromPickle
from ConfigurationUtilities import generateBitsetForOneConfiguration, transformFeatureBitmapsToIncludeSquares, \
 mean_absolute_error, mean_absolute_error_eff, mean_absolute_error_and_stdev_eff


from TransitionDictionaryManipulations import downSampleSingleDictionary, calculatePerTransitionsCounts, \
extractLinearArrayTimeTakenForSingleTransition

alphaValues = [0.001, 0.01, 0.1, 1.0, 10.0]


simpleRegression =0
ridgeRegression  = 1
lassoRegression = 2







def getXBitmapsForRegression(confsList, YSet, UseSquares):        
    """
    Generate array of bitmamps of confs given and repeat them according to number of Y's in each element of YSet.
    Precondition: |YBag| == |YSet|
    """
    XBitmaps = [generateBitsetForOneConfiguration(confId) for confId in confsList]

    if UseSquares:
        XBitmaps = transformFeatureBitmapsToIncludeSquares(XBitmaps)

    XBitmaps = np.repeat(XBitmaps, [len(YBag) for YBag  in YSet], axis=0)
    
    return XBitmaps

def getBestMethodPerTransition(CvResultsFilename):
    """
    Return a dictionary mapping a transition to a tuple  integer/enum representing best method 
    (Linear, Squares, RidgeLinear, RidgeSquares, LassoSimple, Lasso Squares)  and alpha value (or 0 if not applicable)
    """
    
    fd = open(CvResultsFilename, "r")
    dictRegressionTypes = {}
    for line in fd.readlines()[1:]:
       transitionId, textMethodType, alphaParameterOffset = line.split(",")
       
       transitionId = int(transitionId)
       RegressionType, InputType = textMethodType.split("_")
       
       RegressionType = {"Linear": simpleRegression , "Ridge" : ridgeRegression, "Lasso": lassoRegression }[RegressionType]
       InputIsSquares =  InputType == "Squares"

       alphaParameterOffset = int(alphaParameterOffset)
       
       dictRegressionTypes[transitionId] = (RegressionType, InputIsSquares, alphaParameterOffset)
    return dictRegressionTypes


def learnRegressorFromDataset(regressorTypeToLearn, transitionId, datasetArrayDict, confsList):
    """
    Calculates the regressor that CV found to be the best using all the data from training
    """    
    RegressionType = regressorTypeToLearn[0]
    UseSquares = regressorTypeToLearn[1]
    AlphaIndex = regressorTypeToLearn[2]
    
    YSet = extractLinearArrayTimeTakenForSingleTransition(datasetArrayDict, transitionId)
    
    SingleYList = []
    [ SingleYList.extend(YBag) for YBag in YSet]

    YLocalScaler =   StandardScaler()
     
    YLocalScaler.fit([[target] for target in  SingleYList])

    SingleYScaledList = YLocalScaler.transform ([[aY] for aY in SingleYList])

    XBitmaps = getXBitmapsForRegression(confsList, YSet, UseSquares)


#    print ("Transition {0} has  {1} configruations,  a total of {2} y values,  a mean of {3} and a std. dev. of {4}. Conf 0 includes {5} repetitions of y, length of X is {6}".format(transitionId, \
#           len(YSet), len(SingleYList), YLocalScaler.mean_, np.sqrt(YLocalScaler.var_), len(YSet[0]), len(XBitmaps)))
    
    if  RegressionType == simpleRegression:
        Regressor = LinearRegression()
    elif RegressionType == ridgeRegression:
        Regressor = Ridge(alpha=alphaValues[AlphaIndex])
    elif RegressionType == lassoRegression:
        Regressor =  Lasso(alpha=alphaValues[AlphaIndex])
    
    Regressor.fit(XBitmaps, SingleYScaledList)
    
    YPredicted = YLocalScaler.inverse_transform(Regressor.predict(XBitmaps))


   

    YOriginalArray = np.array(SingleYList) ; YOriginalArray.resize((len(SingleYList), 1))

    # Standarize as Lasso returns array of different shape than linear and ridge regression.    
    if RegressionType == lassoRegression:
        YPredicted.resize( (len(SingleYList), 1))
        

    MAPEYTrain, MAPEStdTrain = mean_absolute_error_and_stdev_eff(YOriginalArray, YPredicted)
    
#    print("Y E_Train : {0}".format(MAPEYTrain))
      
    return Regressor, UseSquares, RegressionType == lassoRegression, YLocalScaler, YLocalScaler.mean_,  np.sqrt(YLocalScaler.var_), MAPEYTrain, MAPEStdTrain


def calculateTestErrors(Regressor, RegressorUseSquares, RegressorIsLasso,  YLocalScaler, transitionId, testDataset, testOrderedConfs):
    """
    given a regressor function, calculates the error of such regressor on the test sets.
    Computes MAE_Test and MAE_Test std. dev across products.
    """
    YSet = extractLinearArrayTimeTakenForSingleTransition(testDataset, transitionId)
    
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


if __name__ == "__main__":


#    x.py sampled.pkl conf_train.pkl cv_best.csv assesmentInput.pkl test_confs.pkl    
    if   len(sys.argv) > 5:
        
        sampleTrainFilename = sys.argv[1]
        
        
        confTrainFilename = sys.argv[2]
        
        
        CvResultsFilename = sys.argv[3]
        
        AssementInputFilename = sys.argv[4]
        
        confsTestFilename = sys.argv[5]
        
    else:
        print("Incorrect usage -  requires 5 filenames parameters: train data set," \
              "train configurations, results of CV, test datasetm, test configurations")
        exit(0)
    
    dictRatios =  getSamplingRatiosDict()

    bestRegressorPerTransition = getBestMethodPerTransition(CvResultsFilename)

    testDataset, testOrderedConfs, trainDataset, trainOrderedConfs = loadObjectFromPickle(AssementInputFilename), \
        loadObjectFromPickle(confsTestFilename), loadObjectFromPickle(sampleTrainFilename),  loadObjectFromPickle(confTrainFilename)

        
    print ("Transition Id, YMean_Train, Y_Std_Train, MAE_Train, MAE_Std_Train, YMean_Test, Y_Std_Test, MAE_Test, MAE_Std_Test")
    for transitionId in dictRatios:
         
        Regressor, RegressorUseSquares, RegressorIsLasso, YLocalScaler, YMeanTrain, YStdTrain, MAPEYTrain, MAPEStdTrain =  learnRegressorFromDataset(bestRegressorPerTransition[transitionId], transitionId, trainDataset, trainOrderedConfs )    

        YMeanTest,YStdTest, MAPEYTest, MAEYStdDevTest = calculateTestErrors(Regressor, RegressorUseSquares, RegressorIsLasso, YLocalScaler, transitionId, testDataset, testOrderedConfs)
         
        print("{0},{1},{2},{3},{4},{5},{6},{7},{8}".format(transitionId, YMeanTrain[0], YStdTrain[0], MAPEYTrain, MAPEStdTrain, YMeanTest, YStdTest,  MAPEYTest, MAEYStdDevTest))
    


        
            
    