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

def createX264VM():
    """
    Creatre variability model for X264
    """
    return None

if __name__ == "__main__":
    
    tmpDefaultMLSettings = MLSettings.MLSettings()    
    
    varMod =  VariabilityModel.VariabilityModel("testModel_1")    
    
    binOp1 =  BinaryOption.BinaryOption(varMod, "binOpt1")
    
    print ("Created a tmpDefaultMLSettings and a varMod with a feature of name {0}".format(varMod.getRoot().name ))
    
    varMod.addConfigurationOption(binOp1)
    
    
"""

            VariabilityModel varMod = new VariabilityModel("testModel_1");

            // -------------------- BINARY OPTIONS ----------------
            BinaryOption binOp1 = new BinaryOption(varMod, "binOpt1");
            binOp1.Optional = false;
            binOp1.Prefix = "--";
            varMod.addConfigurationOption(binOp1);


            BinaryOption binOp2 = new BinaryOption(varMod, "binOpt2");
            binOp2.Optional = true;
            binOp2.Prefix = "-?";
            binOp2.Postfix = "kg";
            binOp2.Parent = binOp1;
            binOp2.OutputString = "binOpt2";
            varMod.addConfigurationOption(binOp2);

            BinaryOption binOp3 = new BinaryOption(varMod, "binOpt3");
            binOp3.Optional = true;
            binOp3.Prefix = "";
            binOp3.Postfix = "";
            binOp3.Parent = binOp1;
            List<List<ConfigurationOption>> exclude = new List<List<ConfigurationOption>>();
            List<ConfigurationOption> subExclude = new List<ConfigurationOption>();
            subExclude.Add(binOp2);
            exclude.Add(subExclude);
            binOp3.Excluded_Options = exclude;
            varMod.addConfigurationOption(binOp3);


            BinaryOption binOp4 = new BinaryOption(varMod, "binOpt4");
            binOp4.Optional = true;
            binOp4.Prefix = "4_";
            binOp4.Postfix = "_4";
            binOp4.Parent = binOp1;
            List<List<ConfigurationOption>> implied = new List<List<ConfigurationOption>>();
            List<ConfigurationOption> subimplied = new List<ConfigurationOption>();
            subimplied.Add(binOp2);
            implied.Add(subimplied);
            binOp4.Implied_Options = implied;
            varMod.addConfigurationOption(binOp4);

            // -------------------- NUMERIC OPTIONS ----------------

            NumericOption numOpt1 = new NumericOption(varMod, "numOpt1");
            numOpt1.DefaultValue = 0.0;
            numOpt1.Prefix = "num1-";
            numOpt1.Postfix = "--";
            numOpt1.Min_value = 0;
            numOpt1.Max_value = 10;
            numOpt1.StepFunction = new InfluenceFunction("n + 2");
            varMod.addConfigurationOption(numOpt1);

            NumericOption numOpt2 = new NumericOption(varMod, "numOpt2");
            numOpt2.DefaultValue = 0.8;
            numOpt2.Prefix = "";
            numOpt2.Postfix = "";
            numOpt2.Min_value = 0.1;
            numOpt2.Max_value = 5;
            numOpt2.StepFunction = new InfluenceFunction("n * 2");
            varMod.addConfigurationOption(numOpt2);


            return varMod;
"""