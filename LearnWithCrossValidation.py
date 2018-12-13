#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 16:14:54 2018

@author: rafaelolaechea
"""
import sys

import numpy as np

from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error

import MLConstants
from MLConstants import alphaValues

from ResponsesManipulations import getScaledYForProductSet, getFlattenedXAndDependents, \
getFlattenedOnlyYForProductSet
from pickleFacade import loadObjectFromPickle

from TransitionDictionaryManipulations import extractLinearArrayTimeTakenForSingleTransition, calculatePerTransitionsCounts

from ConfigurationUtilities  import mean_absolute_error_eff, generateBitsetForOneConfiguration

from PrintingCrossValidationResults import printCrossValidationResults, printOutputHeader

from AutonomooseTraces import getListOfAvailableTransitionsAutonomoose, getSetOfExecutionTimesAutonomoose, generateBitsetForOneConfigurationAutonomoose


# Error 27 incorrectly excluded
excludedTransitions = (16, 17, 22,26, 29, 30,31, 32)


MIN_NUM_ARGUMENTS = 3
K_VALUE = 5

class XAndYForASingleCVRun(object):
    def __init__(self, train_index, test_index,  trainingSetConfigurations, YSet, generateBitsetForOneConfigurationRoutine):
        
        self.train_index = train_index

        self.test_index = test_index

        self.trainingSetConfigurations = trainingSetConfigurations

        self.YSet = YSet
        
        self.generateBitsetForOneConfigurationRoutine = generateBitsetForOneConfigurationRoutine
        
    def calculateTrainAndTestXAndY(self):
        """
        Sets the following variables that are used for cross validating / model selection.

                YTrainOriginal                
                YTrainScaledValues

                YScaler
                
                XTrainRepeated
                XTrainSquareRepeated
                
                XTest
                YTest
                
        Returns false if we must skip current CV iteratino either to no Y values in train or test set.
        """
        self.YTrainScaledValues, self.YScaler, self.TrainHasYVals = getScaledYForProductSet(self.train_index, self.YSet)
        
        if self.TrainHasYVals == False:
            return False

        self.YTrainOriginal = self.YScaler.inverse_transform(self.YTrainScaledValues) # Extract corresponding Y original original through back transformation from scaled Y
        
        self.XTrainRepeated, self.XTrainSquareRepeated = getFlattenedXAndDependents(self.train_index, self.trainingSetConfigurations, self.YSet, self.generateBitsetForOneConfigurationRoutine)

#        assert(len(YTrainScaledValues)==len(XTrainRepeated))
#        assert(len(YTrainScaledValues)==len(XTrainSquareRepeated))

        self.XTest, self.XTestSquares = getFlattenedXAndDependents(self.test_index, self.trainingSetConfigurations, self.YSet, self.generateBitsetForOneConfigurationRoutine)
        
        if len(self.XTest) == 0:
            return False # No Y Values in test indices so must skip.
        
        self.YTest = getFlattenedOnlyYForProductSet(self.test_index, self.YSet)
        
        return True
    
    def initializeLinearRegressorArrays(self):
        """
        Sets arrays to be able to execute linear regressions:
            allLinear Estimators + two generic X train arrays.
        """
        self.allLinearEsimators =  [LinearRegression(), LinearRegression()]
        
        self.allLinearXTrain = [self.XTrainRepeated, self.XTrainSquareRepeated]
        
        self.allLinearXTest = [self.XTest, self.XTestSquares]


    def initializeRegularizedRegressors(self, alphaValue):
        """
        Sets arrays for reg. regresion. 
        Assumes XTrain and XtrainSquare already set.
        """
        self.allRidgeEstimators = [Ridge(alpha=alphaValue), Ridge(alpha=alphaValue), Lasso(alpha=alphaValue), Lasso(alpha=alphaValue)]        
            

    def learnRegularizedRegressorsAndStoreErrors(self, index, alphaIndex, wrapperParamsStats):
        """
        Executes each regularized linear regression stored in allRidgeEstimators, and stores its corresponding errors.
        """
        
        self.allRidgeEstimators[index].fit(self.allLinearXTrain[index%2], self.YTrainScaledValues)
        
        YTrainRidgePredicted = self.YScaler.inverse_transform(self.allRidgeEstimators[index].predict(self.allLinearXTrain[index%2]))

        if index >= 2:
            YTrainRidgePredicted = np.array([[y] for y in YTrainRidgePredicted])
        
        MAPETrain = mean_absolute_error_eff(self.YTrainOriginal, YTrainRidgePredicted)
        RMSTrain  = mean_squared_error(self.YTrainOriginal, YTrainRidgePredicted)

        wrapperParamsStats.alphasMapeTrain[alphaIndex][index].append(MAPETrain)
        wrapperParamsStats.alphasRMSTrain[alphaIndex][index].append(RMSTrain)

        YTestRidgePredicted =  self.YScaler.inverse_transform(self.allRidgeEstimators[index].predict(self.allLinearXTest[index%2]))

        if index >= 2:
            YTestRidgePredicted = np.array([[y] for y in YTestRidgePredicted])
                           
        MAPEValidation = mean_absolute_error_eff(self.YTest, YTestRidgePredicted)
        RMSValidation = mean_squared_error(self.YTest, YTestRidgePredicted)

        wrapperParamsStats.alphasMapeValidation[alphaIndex][index].append(MAPEValidation)
        wrapperParamsStats.alphasRMSValidation[alphaIndex][index].append(RMSValidation)        
        
        
    def learnLinearRegressionAndStoreErrors(self, index, wrapperParamsStats):
        """
        Executes a Linear Regression (either with features, or with feature and squares) and saves the errors in terms of Mean Absolute Error, and Root Mean Square Error both validation and train.
        
        Input wrapperParamsStats: A AccumlatedStatisticsAndParamConstants object where to store the errors.
        """
        self.allLinearEsimators[index].fit(self.allLinearXTrain[index], self.YTrainScaledValues)
        
        YTrainPredicted = self.YScaler.inverse_transform(self.allLinearEsimators[index].predict(self.allLinearXTrain[index]))

        
        MAPETrain = mean_absolute_error_eff(self.YTrainOriginal, YTrainPredicted)
        RMSTrain =  mean_squared_error(self.YTrainOriginal, YTrainPredicted)


        wrapperParamsStats.MAPETrainList[index].append(MAPETrain)
        wrapperParamsStats.RMSTrainList[index].append(RMSTrain)

        #
        # Based on test set                
        YTestPredicted = self.YScaler.inverse_transform(self.allLinearEsimators[index].predict(self.allLinearXTest[index]))  

        # Transform Ytest to np array for performance reasons.
        self.YTest = np.array(self.YTest)
                        
        MAPEValidation = mean_absolute_error_eff(self.YTest, YTestPredicted)
        RMSValidation  =  mean_squared_error(self.YTest, YTestPredicted)

        wrapperParamsStats.MAPEValidationList[index].append(MAPEValidation)
        wrapperParamsStats.RMSValidationList[index].append(RMSValidation)
        
    
class AccumlatedStatisticsAndParamConstants(object):
    """
    Set of constants arrays (e.g. alpha values) to be used in Cross Validation.
    Also list of perf. statistics RMS, Mean absolute Error, etc for usage in Cross Validation
    """
    def __init__(self):
        self.MAPETrainList = [[], []]
        self.MAPEValidationList = [[], []]

        self.RMSTrainList =[[], []]
        self.RMSValidationList =[[], []]

        self.alphasMapeTrain = [[[],[],[],[]] for x in alphaValues]        
        self.alphasMapeValidation = [[[],[],[],[]]  for x in alphaValues]

        self.alphasRMSTrain = [[[],[],[],[]] for x in alphaValues]
        self.alphasRMSValidation = [[[],[],[],[]]  for x in alphaValues]
        
    
    
def parseRuntimeParemeters(inputParameters):
    """
    Parses command-line arguments.
    If incorrect arguments, then prints error message and exit.  
    
    Arguments 
        Subject System -- autonomoose or x264
        Conf. Filename PKL File
        Execution times for All Confs -- File.        
    """
    if  len(inputParameters) > MIN_NUM_ARGUMENTS:

        SubjectSystem = inputParameters[1]
         
        if SubjectSystem not in MLConstants.lstSubjectSystems:
             
            print ("Subject systems must be one of {0}".format(", ".join(MLConstants.lstSubjectSystems)))
             
            exit()
        
        confFilename = sys.argv[2]
        
        inputFilename = sys.argv[3]           
    else:
        
        print(" Incorrect Usage. Requires three parameters: Subject System, traininig configurations pkl filename, filename dataset with transitions timing information")
        
        exit()        
        
    return SubjectSystem, confFilename, inputFilename




def learnAndCrossValidateForATransitionGeneric(transitionId, trainingSetConfigurations, kf, YSet, generateBitsetForOneConfigurationRoutine ):
        """
        Perform cross validation to obtain traininig and validation errors for a group of regressor functions
        
        
        Input Parameters Requirements/Preconditions:
            transition id - a numeric id of a transition.

            trainingSetConfigurations --- a list of configurations.
                        
            kf -- a cross validator object.
            
            YSet -- a set of values that is an array of executions times of transition id in configurations listed in trainingSetConfigurations            
            
        Dependencies Requirements:
            A class AccumlatedStatisticsAndParamConstants that includes listing of RMS Values, Regressors, etc.

            A function getScaledYForProductSet that
                Input:
                    A set of indices referring to positions of confs in the array trainingSetConfigurations, 
                    YSet -- List of Arrays of Execution Times on each Conf.
                
                Returns as output
                    A sequence scaled Y Values, a scaler, and a boolean whether there are corresponding Y values for the given transition id.    
            
        """
        wrapperParamsStats = AccumlatedStatisticsAndParamConstants()

        for train_index, test_index in kf.split(trainingSetConfigurations):
                
            CVInputsAndOutputsContainer = XAndYForASingleCVRun(train_index, test_index, trainingSetConfigurations, YSet, generateBitsetForOneConfigurationRoutine)
            
            tmpRetVal =  CVInputsAndOutputsContainer.calculateTrainAndTestXAndY()
            
            if tmpRetVal == False:
                continue
            
            CVInputsAndOutputsContainer.initializeLinearRegressorArrays()

            
            #
            # Linear Regression with feature variables = Features and Features + Features^2.
            for index in range(0, len(CVInputsAndOutputsContainer.allLinearEsimators)):

                CVInputsAndOutputsContainer.learnLinearRegressionAndStoreErrors(index, wrapperParamsStats)
            
            #
            # Iteration thorugh alpha values.
            for alphaValue, alphaIndex in zip(alphaValues, range(0, len(alphaValues))):
                
                
                CVInputsAndOutputsContainer.initializeRegularizedRegressors(alphaValue)
                
                
                for index in range(0, len(CVInputsAndOutputsContainer.allRidgeEstimators)):
                    CVInputsAndOutputsContainer.learnRegularizedRegressorsAndStoreErrors(index, alphaIndex, wrapperParamsStats)
    
        if len(wrapperParamsStats.MAPETrainList[0]) > 0  and len(wrapperParamsStats.MAPEValidationList[0]) > 0:
            printCrossValidationResults(wrapperParamsStats, transitionId, YSet)
            


def learnFromTraininingSetX264(trainingSetConfigurations, transitionArrayOfDictionary):
    """
    Performs cross validation on data for X264.
    """
    
    kf = KFold(n_splits=K_VALUE, shuffle=True)
    
    allCounts = calculatePerTransitionsCounts(transitionArrayOfDictionary)
    
    listTransitionsToSample = [tmpTransition for tmpTransition in allCounts.keys() if tmpTransition not in excludedTransitions]    
    
    for transitionId in listTransitionsToSample:
        YSet = extractLinearArrayTimeTakenForSingleTransition(transitionArrayOfDictionary, transitionId)

        learnAndCrossValidateForATransitionGeneric(transitionId, trainingSetConfigurations,  kf, YSet, generateBitsetForOneConfiguration)
        



def learnFromTraininingSetAutonomoose(trainingSetConfigurations, transitionData):
    """
    Inputs:
        trainingSetConfigurations
        transitionData
    Outputs:
        CSV output including info about training and validation error MAE and RMS.
    Other Function Dependencies:
        
    """    
    kf = KFold(n_splits=K_VALUE, shuffle=True)
    
    listTransitionsToSample = getListOfAvailableTransitionsAutonomoose(transitionData)
        
    for transitionId in listTransitionsToSample:
        
        YSet = getSetOfExecutionTimesAutonomoose(transitionData, transitionId, trainingSetConfigurations)
        
        learnAndCrossValidateForATransitionGeneric(transitionId, trainingSetConfigurations, kf, YSet, generateBitsetForOneConfigurationAutonomoose)
        
    
    
    
if __name__ == "__main__":
        
    SubjectSystem, confFilename, inputFilename =  parseRuntimeParemeters(sys.argv)

    trainingSetConfigurations =loadObjectFromPickle(confFilename) 
    
    transitionArrayOfDictionary = loadObjectFromPickle(inputFilename)

    assert(len(trainingSetConfigurations)==len(transitionArrayOfDictionary))
    
    printOutputHeader()
    
       
    if SubjectSystem == MLConstants.x264Name:
        
        learnFromTraininingSetX264(trainingSetConfigurations, transitionArrayOfDictionary)
        
    elif SubjectSystem == MLConstants.autonomooseName:

        learnFromTraininingSetAutonomoose(trainingSetConfigurations, transitionArrayOfDictionary)        
                 
    
 
