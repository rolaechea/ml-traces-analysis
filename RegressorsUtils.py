#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 16:01:30 2018

@author: rafaelolaechea
"""

from sklearn.linear_model import LinearRegression, Ridge, Lasso

from ConfigurationUtilities import generateBitsetForOneConfiguration, transformFeatureBitmapsToIncludeSquares

import MLConstants

import numpy as np

class TransitionRegressorWrappper:
    def __init__(self, transitionId, useSquareX, regressor):
         
        self.transitionId = transitionId
         
        self.useSquareX = useSquareX
   
        self.regressor = regressor
        
    def getTransitionId(self):
        
        return self.transitionId

    def getUseSquareX(self):
        
        return self.useSquareX
    
    def setScaler(self, scaler):
        
        self.scaler = scaler

    def getScaler(self):
        
        return self.scaler
    
    def getRegressor(self):
        
        return self.regressor
    
    def getRegressionType(self):
        if (type(self.regressor) == LinearRegression):
            
            return MLConstants.simpleRegression
        
        elif (type(self.regressor) == Ridge):
            
            return MLConstants.ridgeRegression
        
        elif (type(self.regressor) == Lasso):
            return MLConstants.lassoRegression




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


def crateRegressorWrapperFromTuple(transitionId, aTuple):
    """
    Given  (RegressionType, InputIsSquares, alphaParameterOffset), creates a corresponding TransitionRegressorWrappper
    """

    if aTuple[0] == MLConstants.simpleRegression:
        aRegressor = LinearRegression()
    elif aTuple[0] == MLConstants.ridgeRegression:
        aRegressor = Ridge(alpha=MLConstants.alphaValues[int(aTuple[2])])
    elif aTuple[0] == MLConstants.lassoRegression:
        aRegressor = Lasso(alpha=MLConstants.alphaValues[int(aTuple[2])])
       
    newTrans = TransitionRegressorWrappper(transitionId, aTuple[1], aRegressor)
    
    return newTrans
    
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
       
       RegressionType = {"Linear": MLConstants.simpleRegression , "Ridge" : MLConstants.ridgeRegression, "Lasso": MLConstants.lassoRegression }[RegressionType]
       InputIsSquares =  InputType == "Squares"

       alphaParameterOffset = int(alphaParameterOffset)
       
       dictRegressionTypes[transitionId] = (RegressionType, InputIsSquares, alphaParameterOffset)
    return dictRegressionTypes
