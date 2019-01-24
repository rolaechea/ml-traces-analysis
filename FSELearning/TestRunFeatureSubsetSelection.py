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



    
import MLSettings
import VariabilityModel
import InfluenceModels
#import BinaryOption
#import FeatureWrapper
import FeatureSubsetSelection

if __name__ == "__main__":
    """
    Checks that learning works on a toy example consisting of 8 features.    
    
    Learnt model should be:
        root, --- 40
        ref_1 and 60
        deblock   -20
    """
    
    vmX264 = VariabilityModel.generateX264VariabilityModel()
    
    print ("{0} options by default. ".format(len(vmX264.binaryOptions)))
    
    InfModelX264 = InfluenceModels.InfluenceModel(vmX264)

    TmpMLSettings = MLSettings.MLSettings()
    
    TmpMLSettings.useBackward = False
    
    TmpMLSettings.numberOfRounds = 10
    
    tmpSubsetSelection =    FeatureSubsetSelection.FeatureSubsetSelection(InfModelX264, TmpMLSettings)
    
    print("Feature subset selection sent as initial features {0}".format( str([x.name for x in tmpSubsetSelection.initialFeatures])))
    print("Feature subset selection sent as strictly mandatory features {0}".format( str([x.name for x in tmpSubsetSelection.strictlyMandatoryFeatures])))
    
    # Correct testing.
    lstLearningX264, lstValidationX264 = VariabilityModel.generateLearningAndValidationSetX264(vmX264)
    
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
        print("Test Passed. Identified Correct Constant Values")
    else:
        print("Test Fao;ed. Identified Incorrect Constant Values")
        mapBinaries = [(x.name,y.Constant) for x,y in tmpSubsetSelection.infModel.binaryOptionsInfluence.items()]
        print (mapBinaries)
#    print("Interactions")
#    print([[y.name for y in x.binaryOptions] for x in tmpSubsetSelection.infModel.interactionInfluence])
    
    