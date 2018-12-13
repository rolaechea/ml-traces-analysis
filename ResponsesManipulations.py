#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 16:26:24 2018

@author: rafaelolaechea
"""
import numpy as np

from sklearn.preprocessing import  StandardScaler

from ConfigurationUtilities import generateBitsetForOneConfiguration, transformFeatureBitmapsToIncludeSquares





def getFlattenedXAndDependents(productIndices, XList, Ylist, GenerateConfiguration=generateBitsetForOneConfiguration):
    """
    Returns a list of bitmaps for Xlist from the configurations that are in XList indexed by product indices.
    Returns Squares X too.
    """
    YLocalArrayOfBags = [Ylist[xIndex] for xIndex in productIndices ]
    
    XBitmaps = [GenerateConfiguration(XList[xIndex]) for xIndex in productIndices]
    
    XBitmapsRepeated = np.repeat(XBitmaps, [len(YBag) for YBag  in YLocalArrayOfBags], axis=0)
    
    XBitmapsSquared = transformFeatureBitmapsToIncludeSquares(XBitmaps)
            
    XBitmapsSquaredRepeated = np.repeat(XBitmapsSquared, [len(YBag) for YBag  in YLocalArrayOfBags], axis=0)
           
    return XBitmapsRepeated, XBitmapsSquaredRepeated 
    
    
    
def getScaledYForProductSet(productIndices, YValsListOfLists):
    """
    Input:
        List of X indices represernting set of products
        List of ordered Y bags           
    returns a list of lists of sclaed Y vectors, a scaler for Y (if there is a Y for set of products given), and boolean whether there is a Y in set of products given
    """
    YLocalArrayOfBags = [YValsListOfLists[xIndex] for xIndex in productIndices]
    
    SingleYList = []
    
    [ SingleYList.extend(YBag) for YBag in YLocalArrayOfBags]
    
    if len(SingleYList) == 0:
    
        return None, None, False
    
    YLocalScaler =   StandardScaler()
     
    YLocalScaler.fit([[target] for target in  SingleYList])
        
    SingleYScaledList = YLocalScaler.transform ([[aY] for aY in SingleYList])
        
    return (SingleYScaledList, YLocalScaler, True)    
     
def getFlattenedOnlyYForProductSet(productIndices, YValsListOfLists):
    """
    Returns a list of flattened Y products that are part of productIndices
    i.e. a List of lists of size 1.
    """
    YLocalArrayOfBags = [YValsListOfLists[xIndex] for xIndex in productIndices]

    
    SingleYList = []
    [ SingleYList.extend(YBag) for YBag in YLocalArrayOfBags]    

    YListOfLists = [[target] for target in SingleYList]
    
    return YListOfLists


    