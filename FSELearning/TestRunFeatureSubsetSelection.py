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
    
    print("Feature subset selection has as initial features {0}".format( str([x.name for x in tmpSubsetSelection.initialFeatures])))
    print("Feature subset selection has as strictly mandatory features {0}".format( str([x.name for x in tmpSubsetSelection.strictlyMandatoryFeatures])))
    
    # Correct testing.
    lstLearningX264, lstValidationX264 = VariabilityModel.generateLearningAndValidationSetX264(vmX264)
    
    tmpSubsetSelection.setLearningSet(lstLearningX264)
    
    tmpSubsetSelection.setValidationSet(lstLearningX264)
    
    tmpSubsetSelection.learn()    
    
    print("Learned Succeded --- kind of.")
    
    