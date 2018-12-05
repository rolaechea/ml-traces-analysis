#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 16:14:54 2018

@author: rafaelolaechea
"""
import sys

import pickle
import numpy as np

from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error

from MLConstants import alphaValues
from ResponsesManipulations import getScaledYForProductSet, getFlattenedXAndDependents, \
getFlattenedOnlyYForProductSet
from pickleFacade import loadObjectFromPickle

from TransitionDictionaryManipulations import extractLinearArrayTimeTakenForSingleTransition, calculatePerTransitionsCounts
from ConfigurationUtilities  import mean_absolute_error_eff


# Error 27 incorrectly excluded
excludedTransitions = (16, 17, 22,26, 29, 30,31, 32)


if __name__ == "__main__":
    sampleSingleTransition = False
    singleTransitionToSample = 0
    outputHeader = True
    
    if   len(sys.argv) > 2:
        confFilename = sys.argv[1]
        
        inputFilename = sys.argv[2]        

        if len(sys.argv) > 3:
            sampleSingleTransition = True
            singleTransitionToSample = int(sys.argv[3])
            
            outputHeader = False            
    else:
  
        print(" Invalid Usage. Requires filename of pre downsampled and conjoined array of dictionary of transitions x times for N configurations".format(sys.argv[0]))
        exit(0)        


    trainingSetConfigurations =loadObjectFromPickle(confFilename) 
    
    transitionArrayOfDictionary = loadObjectFromPickle(inputFilename)

    assert(len(trainingSetConfigurations)==len(transitionArrayOfDictionary))
    
    KValue = 5
    kf = KFold(n_splits=KValue, shuffle=True)
    
    allCounts = calculatePerTransitionsCounts(transitionArrayOfDictionary)    
    
    if outputHeader:
        print("Transition Id, Linear MAPE Average Train , Linear MAPE Average Validation,RMS_T,RMS_V, Linear Squares MAPE Average Train , Linear Squares MAPE Average Validation,RMS_T, RMS_V, Average Y, {0}, {1}, {2}, {3}, {4}".format(\
          ','.join(["Ridge_Train_"+str(alpha)+", Ridge_Validation__"+str(alpha)+",RMS_T,RMS_V" for alpha in alphaValues]),
          ','.join(["Ridge_Square_Train_"+str(alpha)+", Ridge_Square_Validation__"+str(alpha)+",RMS_T,RMS_V" for alpha in alphaValues]), \
          ','.join(["Lasso_Train_"+str(alpha)+", Lasso_Validation_"+str(alpha)+",RMS_T,RMS_V"  for alpha in alphaValues]),\
          ','.join(["Lasso_Square_Train_"+str(alpha)+", Lasso_Square_Validation__"+str(alpha)+",RMS_T,RMS_V"  for alpha in alphaValues]), \
          "Best Method, Supplemental Best Method Index"))
    
    if sampleSingleTransition == True:
        listTransitionsToSample = [singleTransitionToSample]
    else:
        listTransitionsToSample = [tmpTransition for tmpTransition in allCounts.keys() if tmpTransition not in excludedTransitions]        

    
    for transitionId in listTransitionsToSample:

        YSet = extractLinearArrayTimeTakenForSingleTransition(transitionArrayOfDictionary, transitionId)

        MAPETrainList = [[], []]
        MAPEValidationList = [[], []]

        RMSTrainList =[[], []]
        RMSValidationList =[[], []]

        alphasMapeTrain = [[[],[],[],[]] for x in alphaValues]        
        alphasMapeValidation = [[[],[],[],[]]  for x in alphaValues]

        alphasRMSTrain = [[[],[],[],[]] for x in alphaValues]
        alphasRMSValidation = [[[],[],[],[]]  for x in alphaValues]

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


                MAPETrainList[index].append(MAPETrain)
                RMSTrainList[index].append(RMSTrain)

                #
                # Based on test set                
                YTestPredicted = YScaler.inverse_transform(allLinearEsimators[index].predict(allLinearXTest[index]))  

                # Transform Ytest to np array for performance reasons.
                YTest = np.array(YTest)
                                
                MAPEValidation = mean_absolute_error_eff(YTest, YTestPredicted)
                RMSValidation  =  mean_squared_error(YTest, YTestPredicted)

                MAPEValidationList[index].append(MAPEValidation)
                RMSValidationList[index].append(RMSValidation)


            for alphaValue, alphaIndex in zip(alphaValues, range(0, len(alphaValues))):
                
                allRidgeEstimators = [Ridge(alpha=alphaValue), Ridge(alpha=alphaValue), Lasso(alpha=alphaValue), Lasso(alpha=alphaValue)]
                
                for index in range(0, len(allRidgeEstimators)):
                        
                    allRidgeEstimators[index].fit(allLinearXTrain[index%2], YTrainScaledValues)
                    
                    YTrainRidgePredicted = YScaler.inverse_transform(allRidgeEstimators[index].predict(allLinearXTrain[index%2]))

                    if index >= 2:
                        YTrainRidgePredicted = np.array([[y] for y in YTrainRidgePredicted])
                    
                    MAPETrain = mean_absolute_error_eff(YTrainOriginal, YTrainRidgePredicted)
                    RMSTrain  = mean_squared_error(YTrainOriginal, YTrainRidgePredicted)

                    alphasMapeTrain[alphaIndex][index].append(MAPETrain)
                    alphasRMSTrain[alphaIndex][index].append(RMSTrain)

                    YTestRidgePredicted =  YScaler.inverse_transform(allRidgeEstimators[index].predict(allLinearXTest[index%2]))

                    if index >= 2:
                        YTestRidgePredicted = np.array([[y] for y in YTestRidgePredicted])
                                       
                    MAPEValidation = mean_absolute_error_eff(YTest, YTestRidgePredicted)
                    RMSValidation = mean_squared_error(YTest, YTestRidgePredicted)

                    alphasMapeValidation[alphaIndex][index].append(MAPEValidation)
                    alphasRMSValidation[alphaIndex][index].append(RMSValidation)

            
        if len(MAPETrainList[0]) > 0  and len(MAPEValidationList[0]) > 0:                 
            FullSingleYList = []; [ FullSingleYList.extend(aYBag) for aYBag in YSet]; 
            AverageY =  np.mean(FullSingleYList)

            # Extracting Ridge information.
            RidgeSingleTrainMape = [np.mean(aMapePairList[0]) for aMapePairList in alphasMapeTrain]
            RidgeSingleValidationMape = [np.mean(aMapePairList[0]) for aMapePairList in alphasMapeValidation]

            RidgeSingleTrainRMS = [np.mean(aMapePairList[0]) for aMapePairList in alphasRMSTrain]
            RidgeSingleValidationRMS= [np.mean(aMapePairList[0]) for aMapePairList in alphasRMSValidation]            
            
            JointSingleRidgeStrArray = [str(a)+","+str(b)+","+str(c)+","+str(d) for a,b,c,d in zip(RidgeSingleTrainMape, RidgeSingleValidationMape, RidgeSingleTrainRMS, RidgeSingleValidationRMS)]

            
            RidgeSquareTrainMape = [np.mean(aMapePairList[1]) for aMapePairList in alphasMapeTrain]
            RidgeSquareValidationMape = [np.mean(aMapePairList[1]) for aMapePairList in alphasMapeValidation]

            RidgeSquareTrainRMS = [np.mean(aMapePairList[1]) for aMapePairList in alphasRMSTrain]
            RidgeSquareValidationRMS = [np.mean(aMapePairList[1]) for aMapePairList in alphasRMSValidation]

            
            JointSquareRidgeStrArray = [str(a)+","+str(b)+","+str(c)+","+str(d) for a,b,c,d in zip(RidgeSquareTrainMape, RidgeSquareValidationMape, RidgeSquareTrainRMS, RidgeSquareValidationRMS)]

# Lasso Best            
            LassoSingleTrainMape = [np.mean(aMapePairList[2]) for aMapePairList in alphasMapeTrain]
            LassoSingleValidationMape = [np.mean(aMapePairList[2]) for aMapePairList in alphasMapeValidation]            

            LassoSingleTrainRMS = [np.mean(aMapePairList[2]) for aMapePairList in alphasRMSTrain]
            LassoSingleValidationRMS = [np.mean(aMapePairList[2]) for aMapePairList in alphasRMSValidation]

            JointSingleLassoStrArray = [str(a)+","+str(b)+","+str(c)+","+str(d)  for a,b,c,d in zip(LassoSingleTrainMape, LassoSingleValidationMape, LassoSingleTrainRMS, LassoSingleValidationRMS)]

            LassoSquareTrainMape = [np.mean(aMapePairList[3]) for aMapePairList in alphasMapeTrain]
            LassoSquareValidationMape = [np.mean(aMapePairList[3]) for aMapePairList in alphasMapeValidation]

            LassoSquareTrainRMS = [np.mean(aMapePairList[3]) for aMapePairList in alphasRMSTrain]
            LassoSquareValidationRMS = [np.mean(aMapePairList[3]) for aMapePairList in alphasRMSValidation]

            JointSquareLassoStrArray = [str(a)+","+str(b)+","+str(c)+","+str(d) for a,b,c,d in zip(LassoSquareTrainMape, LassoSquareValidationMape, LassoSquareTrainRMS, LassoSquareValidationRMS)]
            
            BestSingleRidgeValidation = np.argmin(RidgeSingleValidationMape)   
            BestSquareRidgeValidation = np.argmin(RidgeSquareValidationMape)
            
            BestSingleLassoValidation = np.argmin(LassoSingleValidationMape)
            BestSquareLassoValidation = np.argmin(LassoSquareValidationMape)

            SingleLinearMapeValidation =   np.mean(MAPEValidationList[0])
            SingleLinearRMSValidation = np.mean(RMSValidationList[0])

            SquareLinearMapeValidation =   np.mean(MAPEValidationList[1])
            SquareLinearRMSValidation = np.mean(RMSValidationList[1])

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
                
            print("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15}".format(transitionId, np.mean(MAPETrainList[0]), SingleLinearMapeValidation, \
                   SingleLinearRMSValidation, np.mean(RMSTrainList[1]), np.mean(MAPETrainList[1]), SquareLinearMapeValidation, np.mean(RMSTrainList[0]), SquareLinearRMSValidation, AverageY, \
                   ','.join(JointSingleRidgeStrArray), ','.join(JointSquareRidgeStrArray), \
                   ','.join(JointSingleLassoStrArray), ','.join(JointSquareLassoStrArray), \
                   BestMethodName, SupplementalBestMethodIndex))
