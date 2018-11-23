#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 16:03:51 2018

@author: rafaelolaechea
"""
import sys

from ParseTrace import loadObjectFromPickle, getSamplingRatiosDict, saveObjectToPickleFile

from sklearn.preprocessing import  StandardScaler
from RegressorsUtils import  getBestMethodPerTransition,  crateRegressorWrapperFromTuple
from TransitionDictionaryManipulations import extractLinearArrayTimeTakenForSingleTransition

from RegressorsUtils import getXBitmapsForRegression

def FitTrainDataFroRegressor(theRegressor, trainOrderedConfs, trainDataset):
    """
    Given a regressor wrapper (already initialized), fit the data (including setting the scaler appropiately for regressor)
    """
    YSet = extractLinearArrayTimeTakenForSingleTransition(trainDataset, theRegressor.getTransitionId())
    SingleYList = []
    [ SingleYList.extend(YBag) for YBag in YSet]  

    YLocalScaler =   StandardScaler()
     
    YLocalScaler.fit([[target] for target in  SingleYList])

    SingleYScaledList = YLocalScaler.transform ([[aY] for aY in SingleYList])

    XBitmaps = getXBitmapsForRegression(trainOrderedConfs, YSet, theRegressor.getUseSquareX())
    
    theRegressor.setScaler(YLocalScaler)
    
#    print("Ready to Fit Regressor  for Transition {0}, |X|= {1}, |Y| = {2} ".format(theRegressor.getTransitionId(), len(XBitmaps), len(SingleYScaledList)))
    
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
    
    dictRatios =  getSamplingRatiosDict()
    
    RegressorList = []
    for transitionId in dictRatios.keys():
         newRegressor = crateRegressorWrapperFromTuple(transitionId, bestRegressorPerTransition[transitionId])# TransitionRegressorWrappper(transitionId, bestRegressorPerTransition[transitionId][1], None)

         FitTrainDataFroRegressor(newRegressor, trainOrderedConfs, trainDataset)
#         print (newRegressor.getScaler().mean_)
#         print (newRegressor.getTransitionId())
#         print (newRegressor.getUseSquareX())        
         RegressorList.append(newRegressor)
    
    saveObjectToPickleFile(RegressorOutputFilename, RegressorList)