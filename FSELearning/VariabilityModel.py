#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 15:41:13 2019

@author: rafaelolaechea
"""
from BinaryOption import BinaryOption

    
class VariabilityModel(object):
    pass

    def __init__(self, name):
        """
        Central model to store all configuration options and their constraints.
        """
        self.name  = name
                
        self.binaryOptions = []
                
        self.root = BinaryOption(self, "root")
        
        self.binaryOptions.append(self.root) 
        
    
    def addConfigurationOption(self, newOption):
        """
        Adds a configuration option to the variability model.
        
        Checks whether an option with the same name already exists and whether invalid characters are within the name
        
        Parameters
        ----------
        The option to be added to the variability model.
        """
        
    def initOptions(self):
        """
        After loading all options, we can replace the names for children, the parent, etc. with the actual objects
        """
        
    def getBinaryOption(self, name):
        """
        Searches for a binary option with the given name
        
        Returns
        -------
        
        Either the binary option with the given name or None if not found
        """
        
    def configurationIsValid(self, ConfigurationC):
        """
        Determine whether ConfigurationC violates any constraints or not.
        """
        pass
    
    def getRoot(self):
        """
        Returns the BinaryOption representing root.
        """
        return self.root
    
    
def generateX264VariabilityModel():
    """
    Hard code generation of X264 Var model.
    
    NOTES
    -----
    Will later transform to load from XML.
    
    """