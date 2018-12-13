#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 14:46:59 2018

@author: rafaelolaechea
"""
import numpy as np

import MLConstants
from MLConstants import alphaValues

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
    

def printCrossValidationResults(wrapperParamsStats, transitionId, YSet):
    """
        Inputs 
            wrapperParamsStats -- to calculate stats.
            YSet -- just to get mean value.
    """
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