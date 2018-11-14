#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 14:19:19 2018

@author: rafaelolaechea
"""
import sys
import numpy as np

#from sklearn.linear_model import RidgeCV, LassoCV
from sklearn.linear_model import LinearRegression, Ridge

from ParseTrace import extractTransitionToBagOfTimesDictionaryFromTraceFile,  getArrayOfDictTransitionIdsToValueSet

from ConfigurationUtilities import generateBitsetForOneConfiguration, transformFeatureBitmapsToIncludeSquares, \
mean_absolute_error, getAllPossibleIds, transformBitsetToIncludeFeatureCubes

from sklearn.model_selection import train_test_split

from sklearn.preprocessing import  StandardScaler
from sklearn.model_selection import KFold

AlphaList = [0.1, 0.5, 1.0, 2.0]


def getFlattenedAndReadyXAndY(test_index, X, Y, includeSquaredX=False, includeCubedX=False):
    """
    Same idea as getScaledXAndY, but don't scale neither X nor Y.
    Just extract Xs and flatten expand Xs. Same with Ys
    """
    YArrayOfBags = [Y[xIndex] for xIndex in test_index ]
    XArrayOfBitmaps = [generateBitsetForOneConfiguration(X[xIndex]) for xIndex in test_index]
    
    # Flatten Target Values and make a single list of arrays of size 1
    SingleYList = []
    [ SingleYList.extend(YBag) for YBag in YArrayOfBags]    
    ReadyY = [[aY] for aY in SingleYList]
    
    # Expand each configuration by # associated transitions
    XBitmapsRepeated = np.repeat(XArrayOfBitmaps, [len(YBag) for YBag  in YArrayOfBags], axis=0)
    
    if includeSquaredX:
       XBitmapsSquared  = transformFeatureBitmapsToIncludeSquares(XArrayOfBitmaps)
       
       XBitmapsSquaredRepeated = np.repeat(XBitmapsSquared, [len(YBag) for YBag  in YArrayOfBags], axis=0)

       if includeCubedX:
           XBitmapsCubed  = transformBitsetToIncludeFeatureCubes(XArrayOfBitmaps)

           XBitmapCubedRepeated = np.repeat(XBitmapsCubed, [len(YBag) for YBag  in YArrayOfBags], axis=0)

           return (XBitmapsRepeated, XBitmapsSquaredRepeated, XBitmapCubedRepeated,  ReadyY)
           
       else:
           return (XBitmapsRepeated, XBitmapsSquaredRepeated, ReadyY)
    else:
        
       return (XBitmapsRepeated, ReadyY)
    
def getScaledXAndY(train_index, X, Y, includeSquaredX=False, includeCubedX=False):
        """
        Given a list of indices of configurations, A list of configurations in X , A list of training time execution bags.
        #, and X, YBAgs,
        returns a list of scaled X (multiplied by # of executed in that product) and scaled Y.
        # Requires size of train index == size of Y.
        # Requires Max(train_index) < size(X)
        # Requires Min(train_index) >= 0
        # Depends on  generateBitsetForOneConfiguration
        
        Fourth return value is True if succeded, false if Y had no elements so failed.:

        """        
        # Perform Basic Conversions
        
        YTrainArrayOfBags = [Y[xIndex] for xIndex in train_index ]          
        XTrainArrayofConfigurationBitmaps = [generateBitsetForOneConfiguration(X[xIndex]) for xIndex in train_index]

        #Standarization of Target Values
        YTrainScaler =   StandardScaler()

        # Flattening Target Values
        SingleYList = []
        [ SingleYList.extend(YBag) for YBag in YTrainArrayOfBags]
                
        # Fitting Standard Sclaer
        if len(SingleYList) == 0:
            # No Y Values so can't scale nor extract Y.
            if includeSquaredX and (not includeCubedX):
                return (None, None, None, None, False)
            elif includeSquaredX and  includeCubedX:
                return (None, None, None, None, None, False)                
            else:
                return (None, None, None, False)        
        YTrainScaler.fit([[target] for target in  SingleYList])
        
        #Applied Y Scaler        
        SingleScaledY = YTrainScaler.transform ([[aY] for aY in SingleYList])
        
        # Expand each configuration by # associated transitions
        XTrainBitmapsRepeated = np.repeat(XTrainArrayofConfigurationBitmaps, [len(YBag) for YBag  in YTrainArrayOfBags], axis=0)
        
        if includeSquaredX:
            XTrainSquared = transformFeatureBitmapsToIncludeSquares(XTrainArrayofConfigurationBitmaps)
            
            XTrainSquaredBitmapsRepeated = np.repeat(XTrainSquared, [len(YBag) for YBag  in YTrainArrayOfBags], axis=0)
            
            if includeCubedX:
                XTrainCubed = transformBitsetToIncludeFeatureCubes(XTrainArrayofConfigurationBitmaps)
                
                XTrainCubedBitmapsRepeated = np.repeat(XTrainCubed, [len(YBag) for YBag  in YTrainArrayOfBags], axis=0)
                
                return (XTrainBitmapsRepeated, XTrainSquaredBitmapsRepeated, XTrainCubedBitmapsRepeated,  SingleScaledY, YTrainScaler, True) 
            else:
                return (XTrainBitmapsRepeated, XTrainSquaredBitmapsRepeated,  SingleScaledY, YTrainScaler, True)        
        else:
            return (XTrainBitmapsRepeated, SingleScaledY, YTrainScaler, True)        
            


def getXValuesForATransition(DictionaryArray, transitionId):
    """
    get a set of xvalues from the  bags.
    """
    

def regularRegressionOnConfigurations(X, Y, TransitionIdForPrinting, IncludeSquares=False, IncludeCubes=False, IncludeRidgeRegression=False):
    """
    Input X Array of Configuration Values of size N
    Input Y Array of bags of time taken values of Size N, where Y(i) corressponds to list of time takens for Configuration X(i)
    Calculates a simple Linear regression from X to Y
    Calculates Both  Average Training  Error and Average Validation Error for Linear Regression (Later will add  Regularized Linear Regression).
    
        #   0. Extract Corresponding Ys --- > to array of Bags.       
        #   1. Convert X indices to  ---> Array of bitmaps
        #   2. Expand X, and Expand Ys, X_i multiplites by size of bag Y_i
        #   3. Standarize and Center Expanded Xs (either custom centering or standard centering)
        #   5. Standarize Expanded Ys    
    
    """
    KValue = 8
    kf = KFold(n_splits=KValue, shuffle=True)
    
    partitionIndex = 0
    MAPETrainList = []
    MAPEValidationList = []
    MAPETrainListWithSquares = []
    MAPEValidationListWithSquares = []  
    MAPETrainListWithCubes = []
    MAPEValidationListWithCubes = []  
    
    alphaValuesList = [0.5, 1.0, 1.5, 2.0, 10.0, 15.0]
    
    for train_index, test_index in kf.split(X):

        partitionIndex = partitionIndex + 1
        
        print ("PartitionIndex {0} ".format(partitionIndex))

        if IncludeSquares and (not IncludeCubes):
            XReady, XSquaredReady, YReadyScaled, YTrainScaler, hasYValues = getScaledXAndY(train_index, X, Y, True, False)
        elif IncludeSquares and IncludeCubes:
            XReady, XSquaredReady, XCubedReady, YReadyScaled, YTrainScaler, hasYValues = getScaledXAndY(train_index, X, Y, True, True)
        else:
            XReady, YReadyScaled, YTrainScaler, hasYValues = getScaledXAndY(train_index, X, Y, False, False)            
        
        if hasYValues == False:                      
            continue # No Y Values in training indices so we must skip this cross validation round


        if IncludeSquares and (not IncludeCubes):
            XTest, XTestSquares, YTest = getFlattenedAndReadyXAndY(test_index, X, Y, True, False)
        elif IncludeSquares and IncludeCubes:
            XTest, XTestSquares, XTestCubes, YTest = getFlattenedAndReadyXAndY(test_index, X, Y, True, True)
        else:
            XTest, YTest = getFlattenedAndReadyXAndY(test_index, X, Y, False, False)
            
        if len(XTest) == 0:
            continue  # No Y Values in test indices so must skip.


        # Perform Basic Linear Regression.
                        
        regEstimator  = LinearRegression()

        regEstimator.fit(XReady, YReadyScaled)
                
        YTrainPredicted = regEstimator.predict(XReady)
        
        YTrainPredictedRescaled = YTrainScaler.inverse_transform(YTrainPredicted)
        
        YTrainOriginal = YTrainScaler.inverse_transform(YReadyScaled)

        MAPETrain = mean_absolute_error(YTrainOriginal, YTrainPredictedRescaled)
        
        YTestPredictedRescaled = YTrainScaler.inverse_transform(regEstimator.predict(XTest))        
        
        MAPEValidation =  mean_absolute_error(YTest, YTestPredictedRescaled)
        
        MAPETrainList.append(MAPETrain)
        
        MAPEValidationList.append(MAPEValidation)
        
        if IncludeSquares:
            print ("Length of XTrain Squares {0} ".format(len(XSquaredReady)))
            print ("Length of XTest Squares {0} ".format(len(XTestSquares)))            
            # Perform Linear Regression With Squares.
            regSquareEstimator  = LinearRegression()
            
            regSquareEstimator =  regSquareEstimator.fit(XSquaredReady, YReadyScaled)
            
            YTrainPredictedWithSquares =  regSquareEstimator.predict(XSquaredReady)
            
            YTrainPredictedWithSquaresRescaled =  YTrainScaler.inverse_transform(YTrainPredictedWithSquares)
            
            MAPETrainWithSquares = mean_absolute_error(YTrainOriginal, YTrainPredictedWithSquaresRescaled)
            
            YTestPredictedRescaledWithSquares = YTrainScaler.inverse_transform(regSquareEstimator.predict(XTestSquares))        
            
            MAPEValidationWithSquares =  mean_absolute_error(YTest, YTestPredictedRescaledWithSquares)
            
            MAPETrainListWithSquares.append(MAPETrainWithSquares)
            
            MAPEValidationListWithSquares.append(MAPEValidationWithSquares)
            
            if IncludeCubes:
                # Perform Linear Regression With Squares.
                print ("Length of XTrain Cubes {0} ".format(len(XCubedReady)))

                print ("Length of XTest Cubess {0} ".format(len(XTestCubes)))
                regCubeEstimator  = LinearRegression()
                
                regCubeEstimator =  regCubeEstimator.fit(XCubedReady, YReadyScaled)
                
                YTrainPredictedWithCubes =  regCubeEstimator.predict(XCubedReady)
                
                YTrainPredictedWithCubesRescaled =  YTrainScaler.inverse_transform(YTrainPredictedWithCubes)
                
                MAPETrainWithCubes = mean_absolute_error(YTrainOriginal, YTrainPredictedWithCubesRescaled)
                
                YTestPredictedRescaledWithCubes = YTrainScaler.inverse_transform(regCubeEstimator.predict(XTestCubes))        
                
                MAPEValidationWithCubes =  mean_absolute_error(YTest, YTestPredictedRescaledWithCubes)
                
                MAPETrainListWithCubes.append(MAPETrainWithCubes)
                
                MAPEValidationListWithCubes.append(MAPEValidationWithCubes)                    
            
#        if IncludeRidgeRegression:   
#            for currentAlpha in  alphaValuesList:
#                print ("Analyze with Ridge Regression Parameter alpha={0} ".format(currentAlpha))                
                
                
    if len(MAPETrainList) > 0  and len(MAPEValidationList) > 0: 
        FullSingleYList = []
        [ FullSingleYList.extend(YBag) for YBag in Y]
        AverageY =  np.mean(FullSingleYList)
        if IncludeSquares and (not IncludeCubes):        
            print ("{0}, \t\t  {1}, \t\t {2}, \t\t {3}, \t\t {4}, \t\t {5}, \t\t {6} ".format(TransitionIdForPrinting, np.mean(MAPETrainList), np.mean(MAPEValidationList), np.mean(MAPETrainListWithSquares), np.mean(MAPEValidationListWithSquares),  sum([len(a) for a in Y]), AverageY))      
        elif IncludeSquares and IncludeCubes:
           print ("{0}, \t\t  {1}, \t\t {2}, \t\t {3}, \t\t {4}, \t\t {5}, \t\t {6}, \t\t {7}, \t\t {8} ".format(TransitionIdForPrinting, np.mean(MAPETrainList), np.mean(MAPEValidationList), \
                  np.mean(MAPETrainListWithSquares), np.mean(MAPEValidationListWithSquares),   np.mean(MAPETrainListWithCubes), np.mean(MAPEValidationListWithCubes), sum([len(a) for a in Y]), AverageY))                  
        else:
            print ("{0}, \t\t  {1}, \t\t {2}, \t\t {3}, \t\t {4} ".format(TransitionIdForPrinting, np.mean(MAPETrainList), np.mean(MAPEValidationList), sum([len(a) for a in Y]), AverageY))        

    
             
                    
if __name__ == "__main__":
    

    # Read command line parameters
    if  len(sys.argv) > 1:
         # First parameter is size of training set
         TrainingConfSize = int(sys.argv[1])
    else:        
        TrainingConfSize = 32

    if len(sys.argv) > 2 and sys.argv[2] == "easy":
       transitionRange = [4,6,7,8,9,13,22,23,27,31,34]
    elif len(sys.argv) > 2:
        transitionRange = [int(sys.argv[2])]
    else:
       transitionRange = range(4,35)
    
    print ("Analyzed Transitions, {0} ".format(transitionRange))
    
    TraininingSetConfigruationIds = train_test_split(getAllPossibleIds(), getAllPossibleIds(), train_size=TrainingConfSize, test_size=(2304-TrainingConfSize))[0]
    
    print("Training Set Configuration Ids, {0}: ".format(TraininingSetConfigruationIds))
    
    ArrayOfDictTransitionIdsToValueSet = getArrayOfDictTransitionIdsToValueSet(TraininingSetConfigruationIds, verbose=True)
    
    # Now perform Linear Regression on each transition selected
    
    print("TransitionId, \t\t Average Training Error, \t\t Average Validation Error,  Optional - Average Training Error With Squares,  Optional - Average Validation Error With Squares,  # of Y Items, Average Y")


    for transitionId in transitionRange:

        X_Train = []
        Y_Train = []   
        confIndex = 0
        
        for configurationId in TraininingSetConfigruationIds:
            
            X_Train.append(configurationId)
    
            if transitionId in ArrayOfDictTransitionIdsToValueSet[confIndex].keys():
                YVals = ArrayOfDictTransitionIdsToValueSet[confIndex][transitionId]
            else:
                YVals = []
    
            Y_Train.append(YVals)            
                   
            confIndex = confIndex +      1
        #
        # Reg. Regression.
        #
        regularRegressionOnConfigurations(X_Train, Y_Train, transitionId, IncludeSquares=True, IncludeCubes=True)
