#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 16:03:51 2018

@author: rafaelolaechea
"""
import sys

from pickleFacade import loadObjectFromPickle, saveObjectToPickleFile
from ParseTrace import  getAllTransitionsIdsList

from sklearn.preprocessing import  StandardScaler
from RegressorsUtils import  getBestMethodPerTransition,  crateRegressorWrapperFromTuple
from TransitionDictionaryManipulations import extractLinearArrayTimeTakenForSingleTransition

from RegressorsUtils import getXBitmapsForRegression

import itertools


def FitTrainDataFroRegressor(theRegressor, trainOrderedConfs, trainDataset):
    """
    Given a regressor wrapper (already initialized), fit the data (including storing  the scaler in the  regressor)
    """
    YSet = extractLinearArrayTimeTakenForSingleTransition(trainDataset, theRegressor.getTransitionId())

    SingleYList = list(itertools.chain.from_iterable(YSet))

    YLocalScaler =   StandardScaler()
     
    YLocalScaler.fit([[target] for target in  SingleYList])

    SingleYScaledList = YLocalScaler.transform ([[aY] for aY in SingleYList])

    XBitmaps = getXBitmapsForRegression(trainOrderedConfs, YSet, theRegressor.getUseSquareX())
    
    theRegressor.setScaler(YLocalScaler)
    
    theRegressor.getRegressor().fit(XBitmaps, SingleYScaledList)
                
    
if __name__ == "__main__":
    if   len(sys.argv) > 4:
        
        sampleTrainFilename = sys.argv[1]
                
        confTrainFilename = sys.argv[2]
                
        CvResultsFilename = sys.argv[3]

        RegressorOutputFilename = sys.argv[4]        

    else:
        print("Incorrect usage -  requires 4 filenames parameters: train data set," \
              "train configurations, results of CV,  output of regressor list")
        exit(0)
    
    bestRegressorPerTransition = getBestMethodPerTransition(CvResultsFilename)
    
    trainDataset, trainOrderedConfs  = loadObjectFromPickle(sampleTrainFilename), \
        loadObjectFromPickle(confTrainFilename)
        
    listTransitionToSample = getAllTransitionsIdsList()
    
    # As we don't yet have sampling ratios for 27.
    if 27 not in listTransitionToSample:
        listTransitionToSample.append(27)
    
    RegressorList = []
    for transitionId in listTransitionToSample:
         newRegressor = crateRegressorWrapperFromTuple(transitionId, bestRegressorPerTransition[transitionId])

         FitTrainDataFroRegressor(newRegressor, trainOrderedConfs, trainDataset)
         
         RegressorList.append(newRegressor)
    
    saveObjectToPickleFile(RegressorOutputFilename, RegressorList)