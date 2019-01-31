#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 18:05:46 2019

@author: rafaelolaechea


LearningRound currentModel


this.strictlyMandatoryFeatures.Add(new Feature(infModel.Vm.Root.Name,infModel.Vm));

...
            LearningRound current = new LearningRound();  ---> current.featureSet  == EMPTY
            
            if (this.strictlyMandatoryFeatures.Count > 0)
                current.FeatureSet.AddRange(this.strictlyMandatoryFeatures);
                

currentModel == CURRENT

{currentModel.FEATURESET == ROOT }

            //Go through each feature of the initial set and combine them with the already present features to build new candidates
            List<Feature> candidates = new List<Feature>();
            
            
            foreach (Feature basicFeature in this.initialFeatures)
                candidates.AddRange(generateCandidates(currentModel.FeatureSet, basicFeature));


"""
import random

    
from  FSELearning import MLSettings
from  FSELearning import  VariabilityModel
from  FSELearning import InfluenceModels
from  FSELearning import Configuration
from  FSELearning import BinaryOption
from  FSELearning import FeatureSubsetSelection


from FSELearning.VariabilityModelUtilities import createChildOption


    

# Test that generate Candidates is working properly.
    
def generateX264VariabilityModel():
    """
    Hard code generation of X264 Var model.
    
    NOTES
    -----
    Will later transform to load from XML.

    Parameters.    
    """
    vmX264 = VariabilityModel.VariabilityModel("x264_model")

# Reference frames.

    createChildOption(vmX264, "ref_1")
    
    createChildOption(vmX264, "ref_2")

    createChildOption(vmX264, "ref_3")

# BFRAMES.
    createChildOption(vmX264, "bframes_1")

    createChildOption(vmX264, "bframes_2")

    createChildOption(vmX264, "bframes_3")
    
# Deblocl
    createChildOption(vmX264, "deblock")    
    
    return vmX264

def generateLearningAndValidationSetX264(vmX264):    
    """
    Generates (say 5) learning and validation configurations to to test FeatureSubsetSelection 
    
    """
    lstLearningMeasurements = []    
    lstValidationsMeasurements = []
    
    tmpRoot = vmX264.getBinaryOption("root")
    
    random.seed(2000)
   
    count = 0
    for i in range(1,4):
        for j in range(1,4):
            for k in range(0,2):
                refOptionToUse = vmX264.getBinaryOption("ref_" + str(i))
                bframeOptionToUse = vmX264.getBinaryOption("bframes_" + str(j))
                if k == 0:
                    useDeblockOption = True
                    deblockOptionToUse = vmX264.getBinaryOption("deblock")
                else:
                    useDeblockOption = False 
                count = count + 1
                
                if useDeblockOption:
                    dctCurrent = {tmpRoot:BinaryOption.BINARY_VALUE_SELECTED , refOptionToUse:BinaryOption.BINARY_VALUE_SELECTED, bframeOptionToUse:BinaryOption.BINARY_VALUE_SELECTED, deblockOptionToUse:BinaryOption.BINARY_VALUE_SELECTED } 
                else:
                    dctCurrent = {tmpRoot:BinaryOption.BINARY_VALUE_SELECTED, refOptionToUse: BinaryOption.BINARY_VALUE_SELECTED, bframeOptionToUse : BinaryOption.BINARY_VALUE_SELECTED}
                
                if i == 1:
                    if k == 1:
                        measuredNFP = 100.0
                    else:
                        measuredNFP = 80
                else:
                    if k == 1:
                        measuredNFP = 40
                    else:
                        measuredNFP = 20
                    
                tmpCurrentConfiguration = Configuration.Configuration(dctCurrent, measuredNFP)
                
                tmpChoice = random.choice([0, 1])
                if (tmpChoice  == 0):
                    lstLearningMeasurements.append(tmpCurrentConfiguration)
                else:
                    lstValidationsMeasurements.append(tmpCurrentConfiguration)
                    
    return lstLearningMeasurements, lstValidationsMeasurements


if __name__ == "__main__":
    """
    Checks that learning works on a toy example consisting of 8 features.    
    
    Learnt model should be:
        root, --- 40
        ref_1 and 60
        deblock   -20
    """
    
    vmX264 = generateX264VariabilityModel()
    
    print ("{0} options by default. ".format(len(vmX264.binaryOptions)))
    
    InfModelX264 = InfluenceModels.InfluenceModel(vmX264)

    TmpMLSettings = MLSettings.MLSettings()
    
    TmpMLSettings.useBackward = True
    
    TmpMLSettings.numberOfRounds = 10
    
    tmpSubsetSelection =    FeatureSubsetSelection.FeatureSubsetSelection(InfModelX264, TmpMLSettings)
    
#    print("Feature subset selection sent as initial features {0}".format( str([x.name for x in tmpSubsetSelection.initialFeatures])))
#    print("Feature subset selection sent as strictly mandatory features {0}".format( str([x.name for x in tmpSubsetSelection.strictlyMandatoryFeatures])))
    
    # Correct testing.
    lstLearningX264, lstValidationX264 = generateLearningAndValidationSetX264(vmX264)
    
    tmpSubsetSelection.setLearningSet(lstLearningX264)
    
    tmpSubsetSelection.setValidationSet(lstLearningX264)
    
    tmpSubsetSelection.learn()    
    
    print("Learned Completed.")
    
#    print("Selected Features")    
#    print([x.name for x in tmpSubsetSelection.infModel.binaryOptionsInfluence])
    
    if "root" in  [x.name for x in tmpSubsetSelection.infModel.binaryOptionsInfluence] and \
       "ref_1" in [x.name for x in tmpSubsetSelection.infModel.binaryOptionsInfluence] and \
       "deblock" in [x.name for x in tmpSubsetSelection.infModel.binaryOptionsInfluence]:
           print ("Test Passed Correctly identified as primary features root, ref_1, and deblock" )
    else:
        print ("Test Failed. Did not  identify as primary features root, ref_1, and deblock" )
    
    desiredVals = {'root': 40.0, 'ref_1': 60.0, 'deblock': -20.0, }

    TestPassed = True
    for desiredKeyName  in desiredVals.keys():
        foundCurrentDesiredItem = False
        for x,y in tmpSubsetSelection.infModel.binaryOptionsInfluence.items():
            if x.name == desiredKeyName and abs(desiredVals[desiredKeyName]-y.Constant) < 0.1:
                foundCurrentDesiredItem = True
        if foundCurrentDesiredItem == False:
            TestPassed = False
    if TestPassed:
        print("Test Passed. Identified Correct Constant Values:")
    else:
        print("Test Failed. Identified Incorrect Constant Values:")
    
    mapBinaries = [(x.name,y.Constant) for x,y in tmpSubsetSelection.infModel.binaryOptionsInfluence.items()]
    print (mapBinaries)
#    print("Interactions")
#    print([[y.name for y in x.binaryOptions] for x in tmpSubsetSelection.infModel.interactionInfluence])
    
    