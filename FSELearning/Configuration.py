#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 16:56:26 2019

@author: rafaelolaechea
"""
from . import BinaryOption

class Configuration(object):    
    def __init__(self, binarySelection, measuremement):
        """
        Creates a configuration with the given set an binary and numeric features selected, 
        not existing ones take default values (aka FALSE).
        
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
        
        
    def generateIdentifier(self, separator):
        """
        Returns the identifier describing the choice of binary configuration options
        
        
        Notes
        -----
        identifier is (optionName followed by separator)* for all options that are selected from dctBinaryOptionValues dictionary.
        """
        
        tmpLstBinaryOptions = [x for x in self.dctBinaryOptionValues.keys()]
        tmpLstBinaryOptions.sort()
        
        sbIdentifier= ""
        for eachBinaryOption in tmpLstBinaryOptions:
            if self.dctBinaryOptionValues[eachBinaryOption] == BinaryOption.BINARY_VALUE_SELECTED:
                sbIdentifier +=   eachBinaryOption.name + separator

        return sbIdentifier
    
    def getNfpValue(self):
        return self.nfpValue    

    def setNfpValue(self, newNFPVal):
        self.nfpValue = newNFPVal
    
   
#        /// <summary>
#        /// Compares one configuration with an other configuration. The identifiers of the configurations are used in the comparison. 
#        /// </summary>
#        /// <param name="other">Configuration to compare</param>
#        /// <returns>States whether the two configurations desribes the same configuration option selection.</returns>
#        public int CompareTo(Configuration other)
#        {
#            return this.identifier.CompareTo(other.identifier);
#        }
# 