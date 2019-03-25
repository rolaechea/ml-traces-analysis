#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 14:40:55 2019

@author: rafaelolaechea
"""
import argparse

import MLConstants

from pickleFacade import loadObjectFromPickle

from AnalyzerRQ2 import getRegressorToTransitionIdMapping


from ConfigurationUtilities import generateBitsetForOneConfiguration, transformFeatureBitmapsToIncludeSquares

def parseArguments():
    """
    Returns an args object with parsed argument or throws an error and exit.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("subjectSystem")
    
    

    parser.add_argument("regressorInputFilename", help="filename of learnt regressor to use")

    parser.add_argument("configurationId", help="configuration whose transition execution time will be estimated")
    
    parser.add_argument("transitionId", help="Transition Id of transition's execution time to estimate")

    args = parser.parse_args()

    if args.subjectSystem not in MLConstants.lstSubjectSystems:
         
        print ("Subject systems must be one of {0}".format(", ".join(MLConstants.lstSubjectSystems)))
         
        exit(0)
            
    return args

if __name__ == "__main__":
    """
    Prints the prediction for a given subject system, regressor, videofile and transition id.    
    """
    args = parseArguments()
    
    SubjectSystem =  args.subjectSystem
    
    regressorInputFilename = args.regressorInputFilename
    
    configurationId = int(args.configurationId)
    
    transitionId = int(args.transitionId)
    
    regressorsArray = loadObjectFromPickle(regressorInputFilename)
       
    transitionToRegressorMapping =  getRegressorToTransitionIdMapping(regressorsArray)
       
    regressorWrapperForSelectedTransition =  regressorsArray[transitionToRegressorMapping[transitionId]]

    transitionToConfArrayTimeTaken = {}

    if SubjectSystem == MLConstants.x264Name:

        configurationInBitset = generateBitsetForOneConfiguration(configurationId)
        
       
    else:
        
        print ("Not yet implemented for Autonomoose.")
        
        exit(0)        

    if regressorWrapperForSelectedTransition.getUseSquareX():
        
        configurationInBitset = transformFeatureBitmapsToIncludeSquares([configurationInBitset])[0]

    skRegressor = regressorWrapperForSelectedTransition.getRegressor()
        
    RawPrediction = skRegressor.predict([configurationInBitset])

    PredictedTransitionExecutionTime =  regressorWrapperForSelectedTransition.getScaler().inverse_transform(RawPrediction)[0]
    
    if  not regressorWrapperForSelectedTransition.isLasso():
        PredictedTransitionExecutionTime = PredictedTransitionExecutionTime[0]    
    
    print(PredictedTransitionExecutionTime)

    