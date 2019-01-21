#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 16:56:26 2019

@author: rafaelolaechea
"""

class Configuration(object):    
    def __init__(self, binarySelection, measuremement):
        """
        Creates a configuration with the given set an binary and numeric features selected, not existing ones take default values.
        
        Parameters
        ----------
        
        ...
        
        
                    /// <summary>
        /// Constructor to create a new configuration based on selected binary options.
        /// </summary>
        /// <param name="binaryConfig">A set of SELECTED binary configuration options</param>
        public Configuration(List<BinaryOption> binaryConfig)
        {
            foreach (BinaryOption opt in binaryConfig)
            {
                binaryOptions.Add(opt, BinaryOption.BinaryValue.Selected);
            }
            identifier = generateIdentifier(DEFAULT_SEPARATOR);
        """
        
        #Binary options of this configuration. 
        # For each option it is stored whether the option is selceted or deselected in this configuration.
        self.dctBinaryOptionValues = binarySelection
        self.nfpValue  = measuremement
        
        
        self.identifier = self.generateIdentifier(",")
        
        
    def generateIdentifier( separator):
        """
        Returns the identifier describing the choice of binary configuration options
        
        
        Notes
        -----
        

            // sort binary features by name
            var binarySelection = binaryOptions.Keys.ToList();
            binarySelection.Sort();

            // sort numeric features by name
            var numericSelection = numericOptions.Keys.ToList();
            numericSelection.Sort();

            StringBuilder sb = new StringBuilder();

            foreach (BinaryOption binary in binarySelection)
            {
                if(binaryOptions[binary].Equals(BinaryOption.BinaryValue.Selected))
                    sb.Append(binary.Name+ separator);
            }

            foreach (NumericOption numeric in numericSelection)
            {
                sb.Append(numeric.Name +"="+ numericOptions[numeric] + separator);
            }
            


            return sb.ToString();        
        
        """
        return ""
    

    def getNfpValue(self):
        return self.nfpValue
    
"""
        /// <summary>
        /// Compares one configuration with an other configuration. The identifiers of the configurations are used in the comparison. 
        /// </summary>
        /// <param name="other">Configuration to compare</param>
        /// <returns>States whether the two configurations desribes the same configuration option selection.</returns>
        public int CompareTo(Configuration other)
        {
            return this.identifier.CompareTo(other.identifier);
        }
"""
    def setNfpValue(self):
        pass