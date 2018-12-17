#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 16:03:51 2018

@author: rafaelolaechea
"""
import sys
import itertools


from sklearn.preprocessing import  StandardScaler


from pickleFacade import loadObjectFromPickle, saveObjectToPickleFile
from ParseTrace import  getAllTransitionsIdsList

from RegressorsUtils import  getBestMethodPerTransition,  crateRegressorWrapperFromTuple
from TransitionDictionaryManipulations import extractLinearArrayTimeTakenForSingleTransition

from RegressorsUtils import getXBitmapsForRegression


import MLConstants

from AutonomooseTraces import getListOfAvailableTransitionsAutonomoose, getSetOfExecutionTimesAutonomoose

def FitTrainDataFroRegressor(theRegressor, trainOrderedConfs, YSet):
    """
    Given a regressor wrapper (already initialized), fit the data (including storing  the scaler in the  regressor)
    """    
    SingleYList = list(itertools.chain.from_iterable(YSet))

    YLocalScaler =   StandardScaler()
     
    YLocalScaler.fit([[target] for target in  SingleYList])

    SingleYScaledList = YLocalScaler.transform ([[aY] for aY in SingleYList])

    XBitmaps = getXBitmapsForRegression(trainOrderedConfs, YSet, theRegressor.getUseSquareX())
    
    theRegressor.setScaler(YLocalScaler)
    
    theRegressor.getRegressor().fit(XBitmaps, SingleYScaledList)
                

MIN_NUM_ARGUMENTS = 5

def parseRuntimeParemeters(inputParameters):
    """
    Parses command-line arguments.
    If incorrect arguments, then prints error message and exit.  
    
    Arguments 
        Subject System -- autonomoose or x264
      
    """
    if  len(inputParameters) > MIN_NUM_ARGUMENTS:

        SubjectSystem = inputParameters[1]
         
        if SubjectSystem not in MLConstants.lstSubjectSystems:
             
            print ("Subject systems must be one of {0}".format(", ".join(MLConstants.lstSubjectSystems)))
             
            exit()
        
        sampleTrainFilename = sys.argv[2]
        
        confTrainFilename = sys.argv[3]       
        
        CVResultsFilename = sys.argv[4]
        
        RegressorOutputFilename = sys.argv[5]
    else:
        print (len(inputParameters))
        
        print(" Incorrect Usage. Requires five parameters: Subject System, sampleTrainFilename, confTrainFilename, CvResultsFilenamem, RegressorOutputFilename")
        
        exit()        
        
    return SubjectSystem, sampleTrainFilename, confTrainFilename, CVResultsFilename, RegressorOutputFilename


if __name__ == "__main__":

    SubjectSystem, sampleTrainFilename, confTrainFilename, CVResultsFilename, RegressorOutputFilename = parseRuntimeParemeters(sys.argv)
    
    bestRegressorPerTransition = getBestMethodPerTransition(CVResultsFilename)
    
    trainDataset, trainOrderedConfs  = loadObjectFromPickle(sampleTrainFilename), \
        loadObjectFromPickle(confTrainFilename)
        
    if SubjectSystem == MLConstants.x264Name:
 
        listTransitionToSample = getAllTransitionsIdsList()
        
    elif SubjectSystem == MLConstants.autonomooseName:
        
        listTransitionToSample = getListOfAvailableTransitionsAutonomoose(trainDataset)
        
    RegressorList = []
    for transitionId in listTransitionToSample:
        if transitionId in bestRegressorPerTransition.keys():
            newRegressor = crateRegressorWrapperFromTuple(transitionId, bestRegressorPerTransition[transitionId])
        else:
            continue
        
        if SubjectSystem == MLConstants.x264Name:
             
            YSet = extractLinearArrayTimeTakenForSingleTransition(trainDataset, newRegressor.getTransitionId())
             
        else:
             
            YSet = getSetOfExecutionTimesAutonomoose(trainDataset, newRegressor.getTransitionId(), trainOrderedConfs)
             
        FitTrainDataFroRegressor(newRegressor, trainOrderedConfs, YSet)
         
        RegressorList.append(newRegressor)
    
    saveObjectToPickleFile(RegressorOutputFilename, RegressorList)
