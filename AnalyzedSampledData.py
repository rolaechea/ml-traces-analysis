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


from ResponsesManipulations import getScaledYForProductSet, getFlattenedXAndDependents, \
getFlattenedOnlyYForProductSet

from TransitionDictionaryManipulations import extractLinearArrayTimeTakenForSingleTransition, calculatePerTransitionsCounts
from ConfigurationUtilities  import mean_absolute_error, mean_absolute_error_eff


excludedTransitions = (16, 17, 22,26, 27, 29, 30,31, 32)

alphaValuesList =  [0.001, 0.01, 0.1, 1.0, 10.0] # [0.1, 1.0, 10.0]
trainingSetConfigurations = [81,1383,2044,1913,872,711,171,112,448,195,1232,117,467,25,159,387,1056,1082,2174,1102,1178,1127,1077,548,322,530,1560,207,476,1655,227,687,1868,385,1810,849,1900,1274,1116,839,523,1789,1886,971,260,421,118,1675,1646,401,614,235,1032,1509,1320,1680,2006,1771,1216,295,2196,492,747,1165,1154,2222,2133,1057,237,542,715,1444,1052,2090,197,1199,735,1976,99,2269,1074,2046,2097,491,495,546,1447,1401,2226,1182,1650,972,1473,2260,2205,951,478,1145,283,1282,1368,1991,1272,2034,416,214,609,224,1079,850,1776,2,642,1140,821,758,220,1876,1477,1649,713,1203,352,148,1357,2149,522,2146,234,643,299,142,739,311,2184,453,1221,1236,180,22,1459,1562,30,1523,1065,265,863,1911,2190,1572,1665,604,1076,2272,727,1467,1258,459,1925,1840,901,115,60,1860,2178,2264,447,1851,2130,729,497,1179,305,1667,164,1895,415,388,1910,824,83,465,1626,1440,1978,316,1081,1785,314,1123,1376,967,473,2132,1703,1915,655,738,1042,2259,165,392,1584,1487,408,1247,1442,1327,1693,1623,2183,441,2031,2185,2070,1352,254,1504,354,1831,1075,1713,5,1839,1070,1735,963,1318,431,2066]

if __name__ == "__main__":
    if   len(sys.argv) > 2:
        confFilename = sys.argv[1]
        
        inputFilename = sys.argv[2]        
                                               
    else:
  
        print(" Invalid Usage. Requires filename of pre downsampled and conjoined array of dictionary of transitions x times for N configurations".format(sys.argv[0]))
        exit(0)        


    pkl_ConfFile = open(confFilename, 'rb')

    trainingSetConfigurations = pickle.load(pkl_ConfFile)        

    pkl_ConfFile.close() 
    
    pkl_file = open(inputFilename, 'rb')

    transitionArrayOfDictionary = pickle.load(pkl_file)        

    pkl_file.close()    
    
    assert(len(trainingSetConfigurations)==len(transitionArrayOfDictionary))
    
    
#    alphaValuesList = [0.5, 1.0, 1.5, 2.0, 10.0, 15.0]
    
    KValue = 5
    kf = KFold(n_splits=KValue, shuffle=True)
    
    allCounts = calculatePerTransitionsCounts(transitionArrayOfDictionary)
    
    
#    print(allCounts)
# , Linear Triplets MAPE Average Train, Linear Triplets MAPE Average Validation"    
    print("Transition Id, Linear MAPE Average Train , Linear MAPE Average Validation,RMS_T,RMS_V, Linear Squares MAPE Average Train , Linear Squares MAPE Average Validation,RMS_T, RMS_V, Average Y, {0}, {1}, {2}, {3}, {4}".format(\
          ','.join(["Ridge_Train_"+str(alpha)+", Ridge_Validation__"+str(alpha)+",RMS_T,RMS_V" for alpha in alphaValuesList]),
          ','.join(["Ridge_Square_Train_"+str(alpha)+", Ridge_Square_Validation__"+str(alpha)+",RMS_T,RMS_V" for alpha in alphaValuesList]), \
          ','.join(["Lasso_Train_"+str(alpha)+", Lasso_Validation_"+str(alpha)+",RMS_T,RMS_V"  for alpha in alphaValuesList]),\
          ','.join(["Lasso_Square_Train_"+str(alpha)+", Lasso_Square_Validation__"+str(alpha)+",RMS_T,RMS_V"  for alpha in alphaValuesList]), \
          "Best Method, Supplemental Best Method Index"))
    
    for transitionId in [tmpTransition for tmpTransition in allCounts.keys() if tmpTransition not in excludedTransitions]:

        YSet = extractLinearArrayTimeTakenForSingleTransition(transitionArrayOfDictionary, transitionId)

        MAPETrainList = [[], []]
        MAPEValidationList = [[], []]

        RMSTrainList =[[], []]
        RMSValidationList =[[], []]

#        print ("Size of Yset ", len(YSet))
        alphasMapeTrain = [[[],[],[],[]] for x in alphaValuesList]        
        alphasMapeValidation = [[[],[],[],[]]  for x in alphaValuesList]

        alphasRMSTrain = [[[],[],[],[]] for x in alphaValuesList]
        alphasRMSValidation = [[[],[],[],[]]  for x in alphaValuesList]

        for train_index, test_index in kf.split(trainingSetConfigurations):
#            print ("AT cross validaiton iteration ")
            YTrainScaledValues, YScaler, TrainHasYVals = getScaledYForProductSet(train_index, YSet)
            
            if TrainHasYVals == False:
#                print ("Skipping as TrainHasYVals is False")                
                continue
            
            YTrainOriginal = YScaler.inverse_transform(YTrainScaledValues) # Extract corresponding Y original original through back transformation from scaled Y

#            print ("YtrainOriginal[0] ={0}".format(YTrainOriginal[0]))
            
            XTrainRepeated, XTrainSquareRepeated = getFlattenedXAndDependents(train_index, trainingSetConfigurations, YSet)

#            print ("XtrainRepeated[0] ={0}".format(XTrainRepeated[0]))

            assert(len(YTrainScaledValues)==len(XTrainRepeated))
            assert(len(YTrainScaledValues)==len(XTrainSquareRepeated))

            XTest, XTestSquares = getFlattenedXAndDependents(test_index, trainingSetConfigurations, YSet)
            
            if len(XTest) == 0:
#                print ("Skipping as XTest Lenght = 0")
                continue # No Y Values in test indices so must skip.
            
            YTest = getFlattenedOnlyYForProductSet(test_index, YSet)
            

            allLinearEsimators =  [LinearRegression(), LinearRegression()]
            allLinearXTrain = [XTrainRepeated, XTrainSquareRepeated]
            allLinearXTest = [XTest, XTestSquares]
            
            for index in range(0, len(allLinearEsimators)):

                allLinearEsimators[index].fit(allLinearXTrain[index], YTrainScaledValues)
                
                YTrainPredicted = YScaler.inverse_transform(allLinearEsimators[index].predict(allLinearXTrain[index]))

#                print("Linear YtrainPredicted[0]={0}".format(YTrainPredicted[0]))

                

                
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


            for alphaValue, alphaIndex in zip(alphaValuesList, range(0, len(alphaValuesList))):
                
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
                                       
                    MAPEValidation = mean_absolute_error(YTest, YTestRidgePredicted)
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
#            print("Size RidgeSingleTrainMape {0} ".format(len(RidgeSingleTrainMape)))          
#            print("Size RidgeSingleValidationMape {0} ", len(RidgeSingleValidationMape))
            
            JointSingleRidgeStrArray = [str(a)+","+str(b)+","+str(c)+","+str(d) for a,b,c,d in zip(RidgeSingleTrainMape, RidgeSingleValidationMape, RidgeSingleTrainRMS, RidgeSingleValidationRMS)]
#            print("Size of JointSingleRidge Ridge {0}", len(JointSingleRidgeStrArray))
            
            RidgeSquareTrainMape = [np.mean(aMapePairList[1]) for aMapePairList in alphasMapeTrain]
            RidgeSquareValidationMape = [np.mean(aMapePairList[1]) for aMapePairList in alphasMapeValidation]

            RidgeSquareTrainRMS = [np.mean(aMapePairList[1]) for aMapePairList in alphasRMSTrain]
            RidgeSquareValidationRMS = [np.mean(aMapePairList[1]) for aMapePairList in alphasRMSValidation]

            
#            print("Size RidgeSingleTrainMape {0} ", len(RidgeSquareTrainMape))            
#            print("Size RidgeSingleValidationMape {0} ", len(RidgeSquareValidationMape))            
            JointSquareRidgeStrArray = [str(a)+","+str(b)+","+str(c)+","+str(d) for a,b,c,d in zip(RidgeSquareTrainMape, RidgeSquareValidationMape, RidgeSquareTrainRMS, RidgeSquareValidationRMS)]
#            print("Size of Joint Square Ridge {0}", len(JointSquareRidgeStrArray))

#
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
            
            
            
            
        
