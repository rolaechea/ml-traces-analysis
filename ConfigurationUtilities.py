#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 13:05:54 2018

@author: rafaelolaechea
"""
import numpy as np


def getAllPossibleIds():
    """
    Get a set of configuration ids from which the training/test set will be selected.
    """
    return range(0, 2304)       

def mean_absolute_error_and_stdev_eff(y_true, y_pred):
    """
    Requires two arrays of equal dimensions but its much faster than mean_absolute_error.
    Returns mean absolute error and standard deviaiton of absolute error.
    """
    
    tmpMAE = np.abs(y_true - y_pred)
    
    return np.mean(tmpMAE), np.std(tmpMAE)

def mean_absolute_error_eff(y_true, y_pred):
    """
    Requires two arrays of equal dimensions but its much faster than mean_absolute_error.
    """
    return np.mean(np.abs(y_true - y_pred))

def mean_absolute_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)

    return np.mean(np.abs(y_true - y_pred))

def transformFeatureBitmapsToIncludeSquares(X):
    """
    Given a vector of bitmaps representing examples x_0, .... x_n
    Creates a corresponding vector of bitmaps including all possible square combinations X_i * x_J where i < j ordered by i and then j.    
    """
    transformedX = []
    for originalFeatureSet in X: 
        Squares = []
        for a, indexA in zip(originalFeatureSet, range(0, len(originalFeatureSet))):
            for b in originalFeatureSet[indexA+1:]:
                Squares.extend([a*b])
        jointFeatureSet =  originalFeatureSet + Squares
        transformedX.extend([jointFeatureSet])
        
    return transformedX


    
def transformBitsetToIncludeFeatureCubes(X):
    """
  Given a vector of bitmaps representing examples x_0, .... x_n
    Creates a corresponding vector of bitmaps including all possible square combinations X_i * x_J where i < j ordered by i and then j,
    and all possible triplets combinations X_i * X_J * X_K with i < j < k
    """
    transformedX = []
    for originalFeatureSet in X: 
        Squares = []
        for a, indexA in zip(originalFeatureSet, range(0, len(originalFeatureSet))):
            for b in originalFeatureSet[indexA+1:]:
                Squares.extend([a*b])
        
        startSquaresIndex = 0
        
        # Add cubes, note x_i will only multiply pairs x_j * xK if j>i and k > j.        
        Triplets = []
        for a, indexA in zip(originalFeatureSet, range(0, len(originalFeatureSet))):
            startSquaresIndex = startSquaresIndex + len(originalFeatureSet[indexA+1:])
            for b  in Squares[startSquaresIndex:]:
                Triplets.extend([a*b])
                

        jointFeatureSet =  originalFeatureSet + Squares + Triplets
        transformedX.extend([jointFeatureSet])
        
    return transformedX

def testTransformCubeAndSquaresTransformations():
    """
    Check both squares and triplets additions to feature set work as expected.    
    """
    testInput = [[0, 1, 1]]
    
    assert ( [[0, 1, 1, 0, 0, 1, 0]] ==    transformBitsetToIncludeFeatureCubes(testInput) )
    
    assert ( [[0, 1, 1, 0, 0, 1]] ==    transformFeatureBitmapsToIncludeSquares(testInput) )

    print("Test Passed")
    

def generateBitsetForOneConfiguration(configurationId):
    """
    Given a configuration id 
    """
    ConfigurationOptions = [("REF_FRAMES", 768, [3, 9, 15], "--ref",  [[1,0,0], [0, 1,0], [0,0,1]]), ("BFRAMES", 256, [0, 1, 9], "-b", [[1,0,0], [0, 1,0], [0,0,1]])] 
    AnalysisConfigurations = [("PSUB8",128, "psub8x8"), ("PSUB16",64, "psub16x16"), ("I4", 32, "i4x4")]    
    BooleanOptions = [("DEBLOCK", 16, [" --nf", ""]), \
                      ("MIXED_REFS", 8, ["", " --mixed-refs"]), \
                      ("WEIGHTED_PREDICTION", 4, ["", " --weightb"]), \
                      ("PSKIP", 2, [" --no-fast-pskip", ""]),
                  ("CAVLC", 1, [" --cabac", ""])]
    
    i = configurationId
    confBitmap = []
    
    for (name, divisor, lookupVals, cmdName, bitmapArray) in ConfigurationOptions:
         confBitmap.extend(bitmapArray[int(i/divisor)])
         subtractValue = int(i/divisor)*divisor
         i = i - subtractValue
    
    for (name, divisor, cmdName) in  AnalysisConfigurations:
        if int(i/divisor) > 0:
            confBitmap.extend([1])
        else:
            confBitmap.extend([0])
        subtractValue = int(i/divisor)*divisor                
        i = i - subtractValue
    
    for (name, divisor, lookupValue) in BooleanOptions:
        if int(i/divisor) > 0:
            confBitmap.extend([1])
        else:
            confBitmap.extend([0])

        subtractValue = int(i/divisor)*divisor
        i = i - subtractValue

    return confBitmap
    

def generateConfigurationBitset():
    """
    Generates a bitset of size N for all configurations of X264 in a list.
    """
    __totalConfigurations__ = 2304
    confDict = {}



    for configurationId in range(__totalConfigurations__):
        confDict[configurationId] = generateBitsetForOneConfiguration[configurationId]

    return confDict




