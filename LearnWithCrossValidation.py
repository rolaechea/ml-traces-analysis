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
from ConfigurationUtilities  import mean_absolute_error_eff


# Error 27 incorrectly excluded
excludedTransitions = (16, 17, 22,26, 29, 30,31, 32)


MIN_NUM_ARGUMENTS = 5
K_VALUE = 5


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


def printOutputHeader():
    """
    print a header of the  CSV output.
    """
    print("Transition Id, Linear MAPE Average Train , Linear MAPE Average Validation,RMS_T,RMS_V, Linear Squares MAPE Average Train , Linear Squares MAPE Average Validation,RMS_T, RMS_V, Average Y, {0}, {1}, {2}, {3}, {4}".format(\
      ','.join(["Ridge_Train_"+str(alpha)+", Ridge_Validation__"+str(alpha)+",RMS_T,RMS_V" for alpha in alphaValues]),
      ','.join(["Ridge_Square_Train_"+str(alpha)+", Ridge_Square_Validation__"+str(alpha)+",RMS_T,RMS_V" for alpha in alphaValues]), \
      ','.join(["Lasso_Train_"+str(alpha)+", Lasso_Validation_"+str(alpha)+",RMS_T,RMS_V"  for alpha in alphaValues]),\
      ','.join(["Lasso_Square_Train_"+str(alpha)+", Lasso_Square_Validation__"+str(alpha)+",RMS_T,RMS_V"  for alpha in alphaValues]), \
      "Best Method, Supplemental Best Method Index"))
    

def learnAndCrossValidateForATransitionGeneric(transitionId, trainingSetConfigurations, transitionArrayOfDictionary, kf, YSet ):
        """
        Perform cross validation to obtain traininig and validation errors for a group of regressor functions
        """
        

        wrapperParamsStats = AccumlatedStatisticsAndParamConstants()

        for train_index, test_index in kf.split(trainingSetConfigurations):
            
            YTrainScaledValues, YScaler, TrainHasYVals = getScaledYForProductSet(train_index, YSet)
            
            if TrainHasYVals == False:
                continue
            
            YTrainOriginal = YScaler.inverse_transform(YTrainScaledValues) # Extract corresponding Y original original through back transformation from scaled Y
            
            XTrainRepeated, XTrainSquareRepeated = getFlattenedXAndDependents(train_index, trainingSetConfigurations, YSet)

            assert(len(YTrainScaledValues)==len(XTrainRepeated))
            assert(len(YTrainScaledValues)==len(XTrainSquareRepeated))

            XTest, XTestSquares = getFlattenedXAndDependents(test_index, trainingSetConfigurations, YSet)
            
            if len(XTest) == 0:
                continue # No Y Values in test indices so must skip.
            
            YTest = getFlattenedOnlyYForProductSet(test_index, YSet)
            

            allLinearEsimators =  [LinearRegression(), LinearRegression()]
            allLinearXTrain = [XTrainRepeated, XTrainSquareRepeated]
            allLinearXTest = [XTest, XTestSquares]
            
            for index in range(0, len(allLinearEsimators)):

                allLinearEsimators[index].fit(allLinearXTrain[index], YTrainScaledValues)
                
                YTrainPredicted = YScaler.inverse_transform(allLinearEsimators[index].predict(allLinearXTrain[index]))

                
                MAPETrain = mean_absolute_error_eff(YTrainOriginal, YTrainPredicted)
                RMSTrain =  mean_squared_error(YTrainOriginal, YTrainPredicted)


                wrapperParamsStats.MAPETrainList[index].append(MAPETrain)
                wrapperParamsStats.RMSTrainList[index].append(RMSTrain)

                #
                # Based on test set                
                YTestPredicted = YScaler.inverse_transform(allLinearEsimators[index].predict(allLinearXTest[index]))  

                # Transform Ytest to np array for performance reasons.
                YTest = np.array(YTest)
                                
                MAPEValidation = mean_absolute_error_eff(YTest, YTestPredicted)
                RMSValidation  =  mean_squared_error(YTest, YTestPredicted)

                wrapperParamsStats.MAPEValidationList[index].append(MAPEValidation)
                wrapperParamsStats.RMSValidationList[index].append(RMSValidation)


            for alphaValue, alphaIndex in zip(alphaValues, range(0, len(alphaValues))):
                
                allRidgeEstimators = [Ridge(alpha=alphaValue), Ridge(alpha=alphaValue), Lasso(alpha=alphaValue), Lasso(alpha=alphaValue)]
                
                for index in range(0, len(allRidgeEstimators)):
                        
                    allRidgeEstimators[index].fit(allLinearXTrain[index%2], YTrainScaledValues)
                    
                    YTrainRidgePredicted = YScaler.inverse_transform(allRidgeEstimators[index].predict(allLinearXTrain[index%2]))

                    if index >= 2:
                        YTrainRidgePredicted = np.array([[y] for y in YTrainRidgePredicted])
                    
                    MAPETrain = mean_absolute_error_eff(YTrainOriginal, YTrainRidgePredicted)
                    RMSTrain  = mean_squared_error(YTrainOriginal, YTrainRidgePredicted)

                    wrapperParamsStats.alphasMapeTrain[alphaIndex][index].append(MAPETrain)
                    wrapperParamsStats.alphasRMSTrain[alphaIndex][index].append(RMSTrain)

                    YTestRidgePredicted =  YScaler.inverse_transform(allRidgeEstimators[index].predict(allLinearXTest[index%2]))

                    if index >= 2:
                        YTestRidgePredicted = np.array([[y] for y in YTestRidgePredicted])
                                       
                    MAPEValidation = mean_absolute_error_eff(YTest, YTestRidgePredicted)
                    RMSValidation = mean_squared_error(YTest, YTestRidgePredicted)

                    wrapperParamsStats.alphasMapeValidation[alphaIndex][index].append(MAPEValidation)
                    wrapperParamsStats.alphasRMSValidation[alphaIndex][index].append(RMSValidation)

            
        if len(wrapperParamsStats.MAPETrainList[0]) > 0  and len(wrapperParamsStats.MAPEValidationList[0]) > 0:                 
            FullSingleYList = []; [ FullSingleYList.extend(aYBag) for aYBag in YSet]; 
            AverageY =  np.mean(FullSingleYList)

            # Extracting Ridge information.
            RidgeSingleTrainMape = [np.mean(aMapePairList[0]) for aMapePairList in wrapperParamsStats.alphasMapeTrain]
            RidgeSingleValidationMape = [np.mean(aMapePairList[0]) for aMapePairList in wrapperParamsStats.alphasMapeValidation]

            RidgeSingleTrainRMS = [np.mean(aMapePairList[0]) for aMapePairList in wrapperParamsStats.alphasRMSTrain]
            RidgeSingleValidationRMS= [np.mean(aMapePairList[0]) for aMapePairList in wrapperParamsStats.alphasRMSValidation]            
            
            JointSingleRidgeStrArray = [str(a)+","+str(b)+","+str(c)+","+str(d) for a,b,c,d in zip(RidgeSingleTrainMape, RidgeSingleValidationMape, RidgeSingleTrainRMS, RidgeSingleValidationRMS)]

            
            RidgeSquareTrainMape = [np.mean(aMapePairList[1]) for aMapePairList in wrapperParamsStats.alphasMapeTrain]
            RidgeSquareValidationMape = [np.mean(aMapePairList[1]) for aMapePairList in wrapperParamsStats.alphasMapeValidation]

            RidgeSquareTrainRMS = [np.mean(aMapePairList[1]) for aMapePairList in wrapperParamsStats.alphasRMSTrain]
            RidgeSquareValidationRMS = [np.mean(aMapePairList[1]) for aMapePairList in wrapperParamsStats.alphasRMSValidation]

            
            JointSquareRidgeStrArray = [str(a)+","+str(b)+","+str(c)+","+str(d) for a,b,c,d in zip(RidgeSquareTrainMape, RidgeSquareValidationMape, RidgeSquareTrainRMS, RidgeSquareValidationRMS)]

# Lasso Best            
            LassoSingleTrainMape = [np.mean(aMapePairList[2]) for aMapePairList in wrapperParamsStats.alphasMapeTrain]
            LassoSingleValidationMape = [np.mean(aMapePairList[2]) for aMapePairList in wrapperParamsStats.alphasMapeValidation]            

            LassoSingleTrainRMS = [np.mean(aMapePairList[2]) for aMapePairList in wrapperParamsStats.alphasRMSTrain]
            LassoSingleValidationRMS = [np.mean(aMapePairList[2]) for aMapePairList in wrapperParamsStats.alphasRMSValidation]

            JointSingleLassoStrArray = [str(a)+","+str(b)+","+str(c)+","+str(d)  for a,b,c,d in zip(LassoSingleTrainMape, LassoSingleValidationMape, LassoSingleTrainRMS, LassoSingleValidationRMS)]

            LassoSquareTrainMape = [np.mean(aMapePairList[3]) for aMapePairList in wrapperParamsStats.alphasMapeTrain]
            LassoSquareValidationMape = [np.mean(aMapePairList[3]) for aMapePairList in wrapperParamsStats.alphasMapeValidation]

            LassoSquareTrainRMS = [np.mean(aMapePairList[3]) for aMapePairList in wrapperParamsStats.alphasRMSTrain]
            LassoSquareValidationRMS = [np.mean(aMapePairList[3]) for aMapePairList in wrapperParamsStats.alphasRMSValidation]

            JointSquareLassoStrArray = [str(a)+","+str(b)+","+str(c)+","+str(d) for a,b,c,d in zip(LassoSquareTrainMape, LassoSquareValidationMape, LassoSquareTrainRMS, LassoSquareValidationRMS)]
            
            BestSingleRidgeValidation = np.argmin(RidgeSingleValidationMape)   
            BestSquareRidgeValidation = np.argmin(RidgeSquareValidationMape)
            
            BestSingleLassoValidation = np.argmin(LassoSingleValidationMape)
            BestSquareLassoValidation = np.argmin(LassoSquareValidationMape)

            SingleLinearMapeValidation =   np.mean(wrapperParamsStats.MAPEValidationList[0])
            SingleLinearRMSValidation = np.mean(wrapperParamsStats.RMSValidationList[0])

            SquareLinearMapeValidation =   np.mean(wrapperParamsStats.MAPEValidationList[1])
            SquareLinearRMSValidation = np.mean(wrapperParamsStats.RMSValidationList[1])

            BestMethodIndex = np.argmin([SingleLinearMapeValidation, SquareLinearMapeValidation, RidgeSingleValidationMape[BestSingleRidgeValidation], \
                       RidgeSquareValidationMape[BestSquareRidgeValidation], LassoSingleValidationMape[BestSingleLassoValidation], \
                       LassoSquareValidationMape[BestSquareLassoValidation]])
            
            BestMethodName = ["Linear_Simple", "Linear_Squares", "Ridge_Simple", "Ridge_Squares", "Lasso_Simple", "Lasso_Squares"][BestMethodIndex]
            if BestMethodIndex == 2: 
                SupplementalBestMethodIndex = BestSingleRidgeValidation
            elif BestMethodIndex == 3:
                SupplementalBestMethodIndex = BestSquareRidgeValidation
            elif BestMethodIndex == 4:
                SupplementalBestMethodIndex = BestSingleLassoValidation
            elif BestMethodIndex == 5:
                SupplementalBestMethodIndex = BestSquareLassoValidation
            else:
                SupplementalBestMethodIndex = 0
                
            print("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15}".format(transitionId, np.mean(wrapperParamsStats.MAPETrainList[0]), SingleLinearMapeValidation, \
                   SingleLinearRMSValidation, np.mean(wrapperParamsStats.RMSTrainList[1]), np.mean(wrapperParamsStats.MAPETrainList[1]), SquareLinearMapeValidation, np.mean(wrapperParamsStats.RMSTrainList[0]), SquareLinearRMSValidation, AverageY, \
                   ','.join(JointSingleRidgeStrArray), ','.join(JointSquareRidgeStrArray), \
                   ','.join(JointSingleLassoStrArray), ','.join(JointSquareLassoStrArray), \
                   BestMethodName, SupplementalBestMethodIndex))

def learnFromTraininingSetX264(trainingSetConfigurations, transitionArrayOfDictionary):

    kf = KFold(n_splits=K_VALUE, shuffle=True)
    
    allCounts = calculatePerTransitionsCounts(transitionArrayOfDictionary)
    
    listTransitionsToSample = [tmpTransition for tmpTransition in allCounts.keys() if tmpTransition not in excludedTransitions]    
    
    for transitionId in listTransitionsToSample:
        YSet = extractLinearArrayTimeTakenForSingleTransition(transitionArrayOfDictionary, transitionId)
        
        learnAndCrossValidateForATransitionGeneric(transitionId, trainingSetConfigurations, transitionArrayOfDictionary, kf, YSet)
        

def learnFromTraininingSetAutonomoose(trainingSetConfigurations, transitionArrayOfDictionary):
    
    kf = KFold(n_splits=K_VALUE, shuffle=True)
    
    listTransitionsToSample = [3]
    
    for transitionId in listTransitionsToSample:
        
        YSet = extractLinearArrayTimeTakenForSingleTransition(transitionArrayOfDictionary, transitionId)
        
        learnAndCrossValidateForATransitionGeneric(transitionId, trainingSetConfigurations, transitionArrayOfDictionary, kf, YSet)
        
    
    
    
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
                 
    
 