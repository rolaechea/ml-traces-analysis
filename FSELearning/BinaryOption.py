#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 14 11:00:22 2019

@author: rafaelolaechea
"""

BINARY_VALUE_SELECTED = 1
BINARY_VALUE_DESELECTED = 2

class BinaryOption(object):
    """
    Represents a feature that is optional or mandatory (only root mandatory).
    
    
    Notes
    -----
    
    getFeatures
    
    """
    def __init__(self, vm, name):
        """
        Constructor that sets optional false and  default value  to selected
        """
        self.name = name
        self.vm = vm
        
        self.children = []
        self.parent = None
        
        self.optional = False
        self.defaultValue = BINARY_VALUE_SELECTED 
        
    def initialize(self):
        """
        Replaces the names for parent, children, etc. with their actual objects of the variability model
        """
        
    def isAncestor(self, optionToCompare):
        """
        Checks whether the given option is an ancestor of the current option (recursive method).
        
        Parameters
        ----------        
        optionToCompare : ConfigurationOption                
        """
    
    def CompareTo(self, otherOption):
        """
        Compare to other option by name

        Parameters
        ----------        
        otherOption : ConfigurationOption            
        """
        return self.name == self.name
        

    def isAlternativeGroup(self, excludedOptions):
        """
        Checks whether the given list of options have the same parent to decide if they all form an alternative group
        
        Parameters
        ----------        
        excludedOption : List of Configuration Options
        

        Returns
        -------
        True if they are alternatives (same parent option), false otherwise        
        """
        pass
    
    
    def hasAlternatives(self):
        """
        Checks whether this binary option has alternative options meaning that there are other binary options with the same parents, but cannot be present in the same configuration as this option.
        
        Returns
        -------
        True if it has alternative options, false otherwise
        """
        pass
    
    def collectAlternativeOptions(self):
        """
        Collects all options that are excluded by this option and that have the same parent
        
        Returns
        -------
        The list of alternative options        
        """
        pass
        
    def getNonAlternativeExlcudedOptions(self):
        """
        Collects all options that are excluded by this option, but do not have the same parent
        
        Returns
        -------
        The list of cross-tree excluded options.
        """
        pass
    
    def isRoot(self):
        """
        whether we represent a root.
        """
        return self.name == "root"