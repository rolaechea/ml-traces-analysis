#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 16:14:54 2018

@author: rafaelolaechea
"""
import sys
import time
import pickle
import numpy as np

from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.model_selection import KFold


from ResponsesManipulations import getScaledYForProductSet, getFlattenedXAndDependents, \
getFlattenedOnlyYForProductSet

from TransitionDictionaryManipulations import extractLinearArrayTimeTakenForSingleTransition, calculatePerTransitionsCounts
from ConfigurationUtilities  import mean_absolute_error



alphaValuesList =  [0.001, 0.01, 0.1, 1.0]
trainingSetConfigurations = [81,1383,2044,1913,872,711,171,112,448,195,1232,117,467,25,159,387,1056,1082,2174,1102,1178,1127,1077,548,322,530,1560,207,476,1655,227,687,1868,385,1810,849,1900,1274,1116,839,523,1789,1886,971,260,421,118,1675,1646,401,614,235,1032,1509,1320,1680,2006,1771,1216,295,2196,492,747,1165,1154,2222,2133,1057,237,542,715,1444,1052,2090,197,1199,735,1976,99,2269,1074,2046,2097,491,495,546,1447,1401,2226,1182,1650,972,1473,2260,2205,951,478,1145,283,1282,1368,1991,1272,2034,416,214,609,224,1079,850,1776,2,642,1140,821,758,220,1876,1477,1649,713,1203,352,148,1357,2149,522,2146,234,643,299,142,739,311,2184,453,1221,1236,180,22,1459,1562,30,1523,1065,265,863,1911,2190,1572,1665,604,1076,2272,727,1467,1258,459,1925,1840,901,115,60,1860,2178,2264,447,1851,2130,729,497,1179,305,1667,164,1895,415,388,1910,824,83,465,1626,1440,1978,316,1081,1785,314,1123,1376,967,473,2132,1703,1915,655,738,1042,2259,165,392,1584,1487,408,1247,1442,1327,1693,1623,2183,441,2031,2185,2070,1352,254,1504,354,1831,1075,1713,5,1839,1070,1735,963,1318,431,2066]

if __name__ == "__main__":
    if   len(sys.argv) > 2:
        inputFilename = sys.argv[1]
        
        confFilename = sys.argv[2]
                                
        pkl_ConfFile = open(confFilename, 'rb')

        trainingSetConfigurations = pickle.load(pkl_ConfFile)        

        pkl_ConfFile.close() 
        
    else:
        print(" Invalid Usage. Requires filename of pre downsampled and conjoined array of dictionary of transitions x times for N configurations".format(sys.argv[0]))
        exit(0)        
    
    pkl_file = open(inputFilename, 'rb')

    transitionArrayOfDictionary = pickle.load(pkl_file)        

    pkl_file.close()    
    
#    print("Checking correct trainingSetConfigurations length")

    assert(len(trainingSetConfigurations)==len(transitionArrayOfDictionary))

    
    
    KValue = 5
    kf = KFold(n_splits=KValue, shuffle=True)
    
    allCounts = calculatePerTransitionsCounts(transitionArrayOfDictionary)

#    print(allCounts)

    print("Transition Id, Average Y, {0}, {1}, {2}".format(\
          ','.join(["Lasso_Train_"+str(alpha)+", Lasso_Validation__"+str(alpha) for alpha in alphaValuesList]),\
          ','.join(["Lasso_Square_Train_"+str(alpha)+", Lasso_Square_Validation__"+str(alpha) for alpha in alphaValuesList]), "Best Method, Supplemental Best Method Index"))
    
    for transitionId in [7]: #allCounts.keys():
        if transitionId in (27, 31):
            continue
        YSet = extractLinearArrayTimeTakenForSingleTransition(transitionArrayOfDictionary, transitionId)

        MAPETrainList = [[], []]
        MAPEValidationList = [[], []]
        
#        print ("Size of Yset ", len(YSet))
#        print ("Starting KF for transition {0} ".format(transitionId))
        alphasMapeTrain = [[[],[]] for x in alphaValuesList]
        alphasMapeValidation = [[[],[]]  for x in alphaValuesList]

        for train_index, test_index in kf.split(trainingSetConfigurations):
#            print("at KF \n")
            YTrainScaledValues, YScaler, TrainHasYVals = getScaledYForProductSet(train_index, YSet)
            
            if TrainHasYVals == False:
                continue
            
            YTrainOriginal = YScaler.inverse_transform(YTrainScaledValues) # Extract corresponding Y original original through back transformation from scaled Y
            
#            print ("YtrainOriginal[0] ={0}".format(YTrainOriginal[0]))

            XTrainRepeated, XTrainSquareRepeated = getFlattenedXAndDependents(train_index, trainingSetConfigurations, YSet)

#            print ("XtrainRepeated[0] ={0}".format(XTrainRepeated[0]))

#            print("Checking correct XTrainRepeated and XTrainSquareRepeated length")
            assert(len(YTrainScaledValues)==len(XTrainRepeated))
            assert(len(YTrainScaledValues)==len(XTrainSquareRepeated))
#            print("Good correct XTrainRepeated and XTrainSquareRepeated length")

            XTest, XTestSquares = getFlattenedXAndDependents(test_index, trainingSetConfigurations, YSet)
            
            if len(XTest) == 0:
#                print ("Skipping as XTest Lenght = 0")
                continue # No Y Values in test indices so must skip.
            
            YTest = getFlattenedOnlyYForProductSet(test_index, YSet)
            

            allLinearXTrain = [XTrainRepeated, XTrainSquareRepeated]
            allLinearXTest = [XTest, XTestSquares]
            
 
            for alphaValue, alphaIndex in zip(alphaValuesList, range(0, len(alphaValuesList))):
                
                allLassoEstimators = [Lasso(alpha=alphaValue), Lasso(alpha=alphaValue)]
                
                for index in range(0, len(allLassoEstimators)):
                    print("Lasso {0} with |x|={1}, |y|={2}, alpha = {3}".format(index, len(allLinearXTrain[index]), len(YTrainScaledValues), alphaValue))
                    
                    allLassoEstimators[index].fit(allLinearXTrain[index], YTrainScaledValues)

#                    print("Completed Lasso {0}".format(index))
                    
#                    print("Getinng inverse {0}".format(allLinearXTrain[index][0]))

                    YTrainRidgePredicted = YScaler.inverse_transform(allLassoEstimators[index].predict(allLinearXTrain[index]))

#                    print ("YTrainPredicted[0]={}, YTrainPredicted[1]={}".format(YTrainRidgePredicted[0], YTrainRidgePredicted[1]))
                    
                    YTrainRidgePredicted = [[y] for y in YTrainRidgePredicted]

#                    print ("Post Processed YTrainPredicted[0]={}, YTrainPredicted[1]={}".format(YTrainRidgePredicted[0], YTrainRidgePredicted[1]))


#                    print("Invereted Y Train  {0}, will compute MAE from YTrainOriginal={1} and YTrainRidgePredicted{2}".format(index, len(YTrainOriginal), len(YTrainRidgePredicted)))                    

                    MAPETrain = mean_absolute_error(YTrainOriginal, YTrainRidgePredicted)

#                    print("MAE Train {0}".format(index))                    
                    
                    alphasMapeTrain[alphaIndex][index].append(MAPETrain)

#                    print("Appended MAE Train {0}".format(index))                    
                    
                    YTestRidgePredicted =  YScaler.inverse_transform(allLassoEstimators[index].predict(allLinearXTest[index]))

                    YTestRidgePredicted = [[y] for y in YTestRidgePredicted]

#                    print("Y Test Lasso {0}".format(index))                    
                    
                    
                    MAPEValidation = mean_absolute_error(YTest, YTestRidgePredicted)

#                    print("Y Validation LLasso {0}".format(index))         
           
                    print (" Will append MAPE Validation = {0} ".format(MAPEValidation))

                    print(" Before alphasMapeValidation[{0}][{1}] === {2}".format(alphaIndex, index, alphasMapeValidation[alphaIndex][index]))
                    
                    alphasMapeValidation[alphaIndex][index].append(MAPEValidation)
                    
                    print(" After alphasMapeValidation[{0}][{1}] === {2}".format(alphaIndex, index, alphasMapeValidation[alphaIndex][index]))

#                    print("Reloop LLasso {0}".format(index))                    
#                print("Single Alpha Loop")
#            print("Single KF Loop")

        print("Completed KF")
        print("alphasMapeValidation: << {0} >> ".format(alphasMapeValidation))
        if len(alphasMapeValidation[0][0]) > 0  :                 
            FullSingleYList = []; [ FullSingleYList.extend(aYBag) for aYBag in YSet]; 
            AverageY =  np.mean(FullSingleYList)

            # Extracting Ridge information.
            RidgeSingleTrainMape = [np.mean(aMapePairList[0]) for aMapePairList in alphasMapeTrain]
            RidgeSingleValidationMape = [np.mean(aMapePairList[0]) for aMapePairList in alphasMapeValidation]
            
            JointSingleRidgeStrArray = [str(a)+","+str(b) for a,b in zip(RidgeSingleTrainMape, RidgeSingleValidationMape)]
            
            RidgeSquareTrainMape = [np.mean(aMapePairList[1]) for aMapePairList in alphasMapeTrain]
            RidgeSquareValidationMape = [np.mean(aMapePairList[1]) for aMapePairList in alphasMapeValidation]
            
            JointSquareRidgeStrArray = [str(c)+","+str(d) for c,d in zip(RidgeSquareTrainMape, RidgeSquareValidationMape)]
            
            BestSingleRidgeValidation = np.argmin(RidgeSingleValidationMape)   
            BestSquareRidgeValidation = np.argmin(RidgeSquareValidationMape)
                        
            BestMethodIndex = np.argmin([RidgeSingleValidationMape[BestSingleRidgeValidation], \
                       RidgeSquareValidationMape[BestSquareRidgeValidation]])
            
            BestMethodName = ["Lasso_Simple", "Lasso_Squares"][BestMethodIndex]
            if BestMethodIndex == 0:
                SupplementalBestMethodIndex = BestSingleRidgeValidation
            else:
                SupplementalBestMethodIndex = BestSquareRidgeValidation
                
            print("{0},{1},{2},{3},{4},{5}".format(transitionId, AverageY, \
                   ','.join(JointSingleRidgeStrArray), ','.join(JointSquareRidgeStrArray), \
                   BestMethodName, SupplementalBestMethodIndex))
            
            
            
            
        
