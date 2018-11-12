
import json
import numpy as np

from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import train_test_split
from sklearn      import tree

import matplotlib.pyplot as plt
import numpy as np


from sklearn.linear_model import RidgeCV, LassoCV

# times = [ x[i] for i in range(2304)]
#clf = tree.DecisionTreeRegressor(max_depth=2)
#clf = clf.fit(X, Y)

__totalConfigurations__ = 2304

__numberMultiTargets__ = 25
__constantRidgeRegression_ = 1


__predictorNames = ("REF_FRAMES_3", 
                    "REF_FRAMES_9",
                    "REF_FRAMES_15",
                    "BFRAMES_0",
                    "BFRAMES_1",
                    "BFRAMES_9",
                    "PSUB8",
                    "PSUB16",
                    "I4",  
                    "DEBLOCK",
                    "MIXED_REFS",
                    "WEIGHTED_PREDICTION",
                    "PSKIP",
                    "CAVLC",)
                


__responseNames = ("reading_raw_image",
"buffering_and_slice_init",
"E_INTRA_ANALYSE",
"E_PROBE_B_SKIP",
"E_ANALYSE_INTER_P16x16",
"E_ANALYSE_B",
"E_INTRA_ANALYSE_CHROMA",
"E_REFINE_QPEL",
"E_ANALYSE_INTER_P8x8",
"E_INTRA_ANALYSE_V2",
"E_ANALYSE_INTER_P16x16",
"E_PREDICT_MV_SKIP",
"E_REFINE_QPEL_V2",
"E_ANALYSE_INTER_P16x8",
"E_ANALYSE_INTER_P8x16",
"E_REFINE_QPEL_V3",
"E_ANALYSE_INTER_P16x8_V2",
"E_ANALYSE_SUB8",
"E_INTRA_ANALYSE_v2",
"frame_analysis_remainder",
"frame_encode",
"write_mb_entropy_coding",
"slice_all_mb_loop_remainder",
"references_and_entropy_model_update_and_psnr",
"writing_encoded_nal_to_file",)

alphaRange = (0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 20.0, 30.0, 40.0, 50.0, 100.0, 200.0, \
                                    400.0, 800.0, 1600.0, 3200.0, 6400.0, 12000.0, 18000.0, 24000.0, 48000.0, \
                                    100.0*1000.0, 100.0*10000.0, 1000.0*10000.0 )
#
#
# SvenApel Regression
#
#


def stdev_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)

    return np.std(np.abs((y_true - y_pred) / y_true)) * 100


def mean_absolute_percentage_error(y_true, y_pred): 

    y_true, y_pred = np.array(y_true), np.array(y_pred)

    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def transformFeaturesToIncludeSquares(X):
    transformedX = []
    for originalFeatureSet in X: 
        Squares = []
        for a in originalFeatureSet:
            for b in originalFeatureSet:
                Squares.extend([a*b])
#                for c in  originalFeatureSet:
#                    Squares.extend([a*b*c])
        jointFeatureSet =  originalFeatureSet + Squares
        transformedX.extend([jointFeatureSet])
    return transformedX

def getPredictorAndTargetValues():
    dctConfTargetMapping = loadConfigurationToTargetMapping()
    dctConfPredictorBitmap =  generateConfigurationBitset()
    
    Targets = [ dctConfTargetMapping[i] for i in range (__totalConfigurations__)]
    Predictors = [dctConfPredictorBitmap[i] for i in range (__totalConfigurations__)] 

    return     (Predictors, Targets)

def getPredictorAndMultiTargetValues():
    dctConfTargetMapping = loadConfigurationToTargetMapping(MultiTarget = True)
    dctConfPredictorBitmap =  generateConfigurationBitset()
    
    MultiTargets = [ dctConfTargetMapping[i] for i in range (__totalConfigurations__)]
    Predictors = [dctConfPredictorBitmap[i] for i in range (__totalConfigurations__)] 

    return     (Predictors, MultiTargets)    



def runRidgeRegressionChained(X, Y, numberConfigurations=400, standarize=True):
        for i in range(1):
            X_train, X_test, Y_train, Y_test = train_test_split(X, Y, train_size=numberConfigurations, \
                    test_size=(__totalConfigurations__-numberConfigurations))
            
            EstimatorList = []
            for j in range(__numberMultiTargets__):
                EstimatorList.extend([RidgeCV(alphas=alphaRange, store_cv_values=True)])
                
                Jth_Y_train = [x[j] for x  in Y_train]
                
                EstimatorList[j].fit(X_train, Jth_Y_train)                
                print(" J = " + str(j) + " Intercept  " + str(EstimatorList[j].intercept_) + " Alpha " + str(EstimatorList[j].alpha_))      

            print (" Will learn using X + vector results as features ")
        
            Extended_TrainX = []
            
            for x_Item in X_train:
#                print (x_Item)
                Y_VectorForX = [EstimatorList[j].predict([x_Item])[0] for j in range(0, __numberMultiTargets__)]
#                print (Y_VectorForX)
#                print (x_Item)
                conjoinedXAndVector = x_Item + Y_VectorForX
 #               print (conjoinedXAndVector)
                Extended_TrainX.append(conjoinedXAndVector)
            
            
            # Normalize X's && do ridge regression.            
            NewEstimator = RidgeCV(alphas=alphaRange, store_cv_values=True, normalize=True)
            
            Y_TrainGlobal = [sum(a) for a in Y_train]
            
            NewEstimator.fit(Extended_TrainX, Y_TrainGlobal)

            print(" Fitted -- X + PredictedRegression to Y_TrainGlobal ")
            Extended_TestX = []
            for x_Item in X_test:
                Y_VectorForX = [EstimatorList[j].predict([x_Item])[0] for j in range(0, __numberMultiTargets__)]
                conjoinedXAndVector = x_Item + Y_VectorForX
                Extended_TestX.append(conjoinedXAndVector)
            
            PredictedYTest = NewEstimator.predict(Extended_TestX)
            
            
            MAPEError = mean_absolute_percentage_error([sum(a) for a in Y_test], PredictedYTest)
            print (" MAPE " + str(MAPEError) + " Absolute Av. Error " + str(mean_absolute_error([sum(a) for a in Y_test], PredictedYTest))+ \
                   " mean (Y_test)) " + str(np.mean([sum(a) for a in Y_test])) + " mean (Y_Estimate)) " + str(np.mean(PredictedYTest))) 
            
def runRidgeRegressionTargetByTarget(X, Y, numberConfigurations=400, centerResponse=True, RegressionType=1, \
                                     silentCoef=False, onlyReturnMape=False):
    
        for i in range(1):
            X_train, X_test, Y_train, Y_test = train_test_split(X, Y, train_size=numberConfigurations, \
                    test_size=(__totalConfigurations__-numberConfigurations))

            meanTargets = [np.mean([x[i] for x in Y_train]) for i in range(0, __numberMultiTargets__)]
            Y_trainStandarized =  [[x[i]-  meanTargets[i] for i in range(0, __numberMultiTargets__)] for x in Y_train]    
            
            AccumulatedY_TestEstimate = []
            for j in range(__numberMultiTargets__):
                
                if RegressionType == __constantRidgeRegression_:
                    estimator = RidgeCV(alphas=alphaRange, store_cv_values=True, normalize=True)
                else:
                    estimator = LassoCV(alphas=alphaRange[6:], max_iter=10000, normalize=True)
#                estimator = LassoCV(alphas=alphaRange[6:], max_iter=10000)

                if centerResponse:
                    Jth_Y_train = [x[j] for x  in Y_trainStandarized]
                else:
                    Jth_Y_train = [x[j] for x  in Y_train]
                                       
                estimator.fit(X_train, Jth_Y_train)
                
                Y_testEstimate = estimator.predict(X_test)
                
                if centerResponse:
                    Y_testEstimate = [x + meanTargets[j] for x in Y_testEstimate] 

                Jth_Y_test = [x[j] for x  in Y_test]
                
                if AccumulatedY_TestEstimate == []:
                    AccumulatedY_TestEstimate = Y_testEstimate
                else:
                    AccumulatedY_TestEstimate = [a + b for a,b in zip(AccumulatedY_TestEstimate, Y_testEstimate)]
            
                MeanLocalError =  mean_absolute_error(Jth_Y_test, Y_testEstimate)
                
                Jth_Y_PredictTrain = estimator.predict(X_train)
                
                MeanLocalErrorTrain = mean_absolute_error(Jth_Y_train, Jth_Y_PredictTrain)
#                MeanLocalPercentageError  = mean_absolute_percentage_error(Jth_Y_test, Y_testEstimate)
                
                if not silentCoef and not onlyReturnMape:
#                    printIntermediateResultsByResponseVariable()
                    print ("\n\n")
                    print(" J = " + str(j) + " Intercept  " + str(estimator.intercept_) + " Alpha " + str(estimator.alpha_) + \
                          " Sum of Error / Bias " + str(MeanLocalError) + " ... Ave.(Y_test) " + str(np.mean(Jth_Y_test)) \
                          + " StdDev(Y_test) " + str(np.std(Jth_Y_test)) +  " ... Ave.(Y_train) " + str(np.mean(Jth_Y_train)) + " ...  MAPE (Y_test) " + str(100.0*MeanLocalError/ np.mean(Jth_Y_test)) \
                          + "MAPE (Y_train) " + str(100.0*MeanLocalErrorTrain/ np.mean(Jth_Y_train)) )
                    
                    print ("Response " + __responseNames[j])
     
                    for i, inputName  in enumerate(__predictorNames):
                        if estimator.coef_[i] > 10.0 or estimator.coef_[i] < -10.0:
                            print (inputName + " : " + str(estimator.coef_[i] ))
                        
                    print (estimator.coef_)
            
            MeanError = mean_absolute_error([sum(x) for x in Y_test], AccumulatedY_TestEstimate)
            MAPEError = mean_absolute_percentage_error([sum(x) for x in Y_test], AccumulatedY_TestEstimate)
            
            if onlyReturnMape:
                return MAPEError
            else:

                    print ("MAPE " + str(MAPEError) +"% Mean Absolute  Error: " + str(MeanError) + " Mean (Y) = " + str(np.mean([sum(x) for x in Y_test])) \
                           + " Stdev "  +  str(np.std([sum(x) for x in Y_test])))
            

            

def runRidgeRegression(X, Y, numberConfigurations=100, centerResponse=True, onlyReturnMape=False, RegressionType=1 ):
    
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, train_size=numberConfigurations, \
        test_size=(__totalConfigurations__-numberConfigurations))

    meanTarget = np.mean(Y_train)
        
    if centerResponse:
        Y_train =  [ (Target-meanTarget) for Target in Y_train]    
    
    #
    # Run Cross Validation Ridge Regression.
    #
    if RegressionType == __constantRidgeRegression_:
        estimator = RidgeCV(alphas=alphaRange, store_cv_values=True, normalize=True)
    else:
        estimator = LassoCV(alphas=alphaRange[6:], max_iter=10000, normalize=True)    
   
    estimator.fit(X_train, Y_train)
    
    Y_testEstimate = estimator.predict(X_test)    
    
    if centerResponse:        
       Y_testEstimate = [(Target+meanTarget) for Target in Y_testEstimate]
                         
    meanMape = mean_absolute_percentage_error(Y_test, Y_testEstimate)




    if onlyReturnMape:
        return meanMape
    else:
        print ("Mean Absolute Percente Error: " + str(meanMape) )

    
def runCartTreeOnX264(X, Y, numberConfigurations=81, MultiTarget=False):   

    arrayMape = []
    arrayMapeStdev = []
    for i in range(100):
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, train_size=numberConfigurations, \
            test_size=(__totalConfigurations__-numberConfigurations))
        
        if numberConfigurations <= 100:

            min_bucket = int(numberConfigurations/10 + 0.5)
        
            min_split = 2 * min_bucket

        else:
      
            min_split = int(numberConfigurations/10 + 0.5)

            min_bucket = int(min_split/2)                        
            
        clf = tree.DecisionTreeRegressor(min_samples_leaf=min_bucket, min_samples_split=min_split)
            
        clf = clf.fit(X_train, Y_train)
            
            
        Y_testEstimate = clf.predict(X_test) 

        if MultiTarget:
            Y_test, Y_testEstimate = [sum(x) for x in Y_test], [sum(x) for x in Y_testEstimate]
        
         
        meanAbsolutePercenteError = mean_absolute_percentage_error(Y_test, Y_testEstimate)
        stdevmeanAbsolutePercenteError = stdev_absolute_percentage_error(Y_test, Y_testEstimate)
        
        arrayMape.extend([meanAbsolutePercenteError])
        arrayMapeStdev.extend([stdevmeanAbsolutePercenteError])
        
    meanMape = np.mean(np.array(arrayMape))
    stdevMape = np.std(np.array(arrayMape))
    singleRunStdev = np.mean(np.array(arrayMapeStdev))
    
    print ("Mean Absolute Error: " + str(meanMape) + " with across runs stdev =  " + str(stdevMape) + ", single run stdev " + str(singleRunStdev))

    
#        print ("Mean Absolute Error: " + str(meanAbsolutePercenteError) + " Min Bucket = " + str(min_bucket) + " Min Split = " + str(min_split))
        
        
    # Report Average Fault Rate, and Standard Deviation.
    
#    Integrated script
    

def generateConfigurationBitset():
    confDict = {}

    ConfigurationOptions = [("REF_FRAMES", 768, [3, 9, 15], "--ref",  [[1,0,0], [0, 1,0], [0,0,1]]), ("BFRAMES", 256, [0, 1, 9], "-b", [[1,0,0], [0, 1,0], [0,0,1]])] 
    AnalysisConfigurations = [("PSUB8",128, "psub8x8"), ("PSUB16",64, "psub16x16"), ("I4", 32, "i4x4")]    
    BooleanOptions = [("DEBLOCK", 16, [" --nf", ""]), \
                      ("MIXED_REFS", 8, ["", " --mixed-refs"]), \
                      ("WEIGHTED_PREDICTION", 4, ["", " --weightb"]), \
                      ("PSKIP", 2, [" --no-fast-pskip", ""]),
                  ("CAVLC", 1, [" --cabac", ""])]

    for configurationId in range(__totalConfigurations__):
        i = configurationId
        confBitmap = []
        
        for (name, divisor, lookupVals, cmdName, bitmapArray) in ConfigurationOptions:
             confBitmap.extend(bitmapArray[int(i/divisor)])
             subtractValue = int(i/divisor)*divisor
             i = i - subtractValue
        
        for (name, divisor, cmdName) in  AnalysisConfigurations:
            if int(i/divisor) > 0:
                confBitmap.extend([1])
            else:
                confBitmap.extend([0])
            subtractValue = int(i/divisor)*divisor                
            i = i - subtractValue
        
        for (name, divisor, lookupValue) in BooleanOptions:
            if int(i/divisor) > 0:
                confBitmap.extend([1])
            else:
                confBitmap.extend([0])

            subtractValue = int(i/divisor)*divisor
            i = i - subtractValue

        confDict[configurationId] = confBitmap

    return confDict


def getTimeVectorFromDictionary(dictRun):
    list_pre_transitions = ["reading_raw_image", "buffering_and_slice_init"]
    ALWAYS_ZERO_EVENTS = ["E_RET_PROBE_B_SKIP_F", "E_RET_PROBE_B_SKIP_T", "E_ANALYSE_START_SUB8", "E_FINISH"]
    list_post_transitions_1 = ["frame_encode", "write_mb_entropy_coding"]
    list_post_transitions_2 = ["references_and_entropy_model_update_and_psnr", "writing_encoded_nal_to_file"]
    startDetailIndex = 2
    
    Y = []
    
    for name in list_pre_transitions:    
        Y.extend([dictRun[name]])

    
    for singleTransition in dictRun["transitions"]:
        if singleTransition['event'] not in ALWAYS_ZERO_EVENTS:    
            Y.extend([singleTransition['time']])

    frame_analysis_remainder = dictRun['frame_analysis'] - sum(Y[startDetailIndex:])
    
    Y.extend([frame_analysis_remainder])
    
    for name in list_post_transitions_1:
        Y.extend([dictRun[name]])
    
    slice_all_mb_loop_remainder = dictRun['slice_all_mb_loop']-sum(Y[startDetailIndex:])
    
    Y.extend([slice_all_mb_loop_remainder])
    
    for name in list_post_transitions_2:
        Y.extend([dictRun[name]])
       
    return Y

def loadDictionaryFromFile(completeFilename="/Users/rafaelolaechea/phd-work/Section 3 - Learning/subject-systems/x264-no-asm/testDataset-2/conf-1-rep-1-timing-akiyo.json"):
    jsonFp = open(completeFilename, 'r') ; 
    dictConf = json.load(jsonFp) ; 
    jsonFp.close();
    return dictConf
        

def loadConfigurationToTargetMapping(basepath="/Users/rafaelolaechea/phd-work/Section 3 - Learning/subject-systems/x264-no-asm/testDataset-2/",\
                                     MultiTarget=False):
    dctConfigurationToTime = {}
    for confId in range(__totalConfigurations__):
        
        totalTime = 0
        
        for repetition in range(1,10):
            
            completePath = basepath + 'conf-' + str(confId) + '-rep-' + str(repetition) + '-timing-akiyo.json'
            
            dictConf = loadDictionaryFromFile(completePath)
            
            if MultiTarget ==  True:
                timeTakenVector = getTimeVectorFromDictionary(dictConf)
                if repetition == 1:
                    targetTotal = timeTakenVector
                else:
                    targetTotal = [ x + y for x,y in zip(targetTotal, timeTakenVector)]
                    
            totalTime = totalTime + dictConf['total_time_in_ms']
            
         
        if MultiTarget == True:
            averageTimeMultiTarget = [x/9.0 for x in targetTotal]            
            dctConfigurationToTime[confId] = averageTimeMultiTarget
        else:
            averageTime = totalTime / 9.0
            dctConfigurationToTime[confId] = averageTime 
            
    return dctConfigurationToTime
