#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 16:00:29 2019

@author: rafaelolaechea


Start Learning Command.

                        InfluenceModel infMod = new InfluenceModel(GlobalState.varModel, GlobalState.currentNFP);

                        List<Configuration> configurations_Learning = new List<Configuration>();

                        List<Configuration> configurations_Validation = new List<Configuration>();
                        
                        ....
                        
                           //List<List<BinaryOption>> availableBinary 
                            configurations_Learning = GlobalState.getAvailableBinary(exp.BinarySelections_Learning, exp.NumericSelection_Learning);
                            //configurations_Learning = GlobalState.getMeasuredConfigs(Configuration.getConfigurations(availableBinary, exp.NumericSelection_Learning));
                            configurations_Learning = configurations_Learning.Distinct().ToList();

                            configurations_Validation = GlobalState.getMeasuredConfigs(Configuration.getConfigurations(exp.BinarySelections_Validation, exp.NumericSelection_Validation));
                            configurations_Validation = configurations_Validation.Distinct().ToList();

                        ...
                    
                        exp.learning = new FeatureSubsetSelection(infMod, exp.mlSettings);
                        exp.learning.setLearningSet(configurations_Learning);
                        exp.learning.setValidationSet(configurations_Validation);
                        exp.learning.learn();



addConfiguration

Configuration config

        /// <summary>
        /// Adds a configration to the global state. 
        /// </summary>
        /// <param name="config">An configuration of the variability model.</param>
        public static void addConfiguration(Configuration config)
        {
            GlobalState.allMeasurements.add(config);
        }
        
Result Database

    public class ResultDB
    {

        private List<Configuration> configurations = new List<Configuration>();

        public List<Configuration> Configurations
        {
            get { return configurations; }
            set { configurations = value; }
        }


        public void add(Configuration configuration)
        {
            this.configurations.Add(configuration);
        }

        

"""
import MLSettings
import VariabilityModel
import BinaryOption

import FeatureWrapper

def createX264VM():
    """
    Creatre variability model for X264
    """
    return None

if __name__ == "__main__":
    
    tmpDefaultMLSettings = MLSettings.MLSettings()    
    
    varMod =  VariabilityModel.VariabilityModel("testModel_1")    

    # Only has root.    
    print ("Created a tmpDefaultMLSettings and a varMod with a feature of name {0}. In Total has {1} objects ".format(\
           varMod.getRoot().name, len(varMod.getBinaryOptions())))    
    
    binOp1 =  BinaryOption.BinaryOption(varMod, "binOpt1")
    
    binOp1.optional = True
    
    binOp1.Parent = varMod.getRoot()
    
    varMod.addConfigurationOption(binOp1)
   

    # Only has root and binary option 1.
    print ("Created a tmpDefaultMLSettings and a varMod with a feature of name {0}. In Total has {1} objects ".format(\
           varMod.getRoot().name, len(varMod.getBinaryOptions())))
    
    binOp2 =  BinaryOption.BinaryOption(varMod, "binOp2")
    
    binOp2.optional = True
    
    binOp2.Parent = binOp1
    
    varMod.addConfigurationOption(binOp2)
    
    print ("Created a tmpDefaultMLSettings and a varMod with a feature of name {0}. In Total has {1} objects ".format(\
           varMod.getRoot().name, len(varMod.getBinaryOptions())))    
    
    newFeature = FeatureWrapper.FeatureWrapper("binOpt1", varMod)
    
    tmpDct = {}
    
    tmpDct[newFeature] = 10
    newDuplicateFeature = FeatureWrapper.FeatureWrapper("binOpt1", varMod)

    UnDuplicateFeature = FeatureWrapper.FeatureWrapper("binOp2*binOpt1", varMod)    
    
    print(newFeature == newDuplicateFeature)
    print(newFeature == UnDuplicateFeature)
    
    print("expressionArray newFeature  == " +str(newFeature.expressionArray))

    print("expressionArray UnDuplicateFeature binOp2*binOpt1 ::  == " +str(UnDuplicateFeature.expressionArray))
    
    UnDuplicateDuplicateFeature = FeatureWrapper.FeatureWrapper("binOpt1 * binOp2", varMod)
    
    print(UnDuplicateDuplicateFeature == UnDuplicateFeature)
    
    print( "Before Modified dct  {0}".format(str(tmpDct)))
    
    print( "NewFeature Duplicate in dct keys {0}".format(newDuplicateFeature in tmpDct.keys()))
    
    tmpDct[newDuplicateFeature] = 20
    
    print( "Modified dct  {0}".format(str(tmpDct)))
    