#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  9 17:34:38 2019

@author: rafaelolaechea
"""

from InfluenceFunction import InfluenceFunction

class FeatureWrapper(InfluenceFunction):
    """
    Feature Wrapper used in FSE paper
       
    Notes
    -----   
        Inherits from InfluenceFunction ,  --- IEquatable<Feature>, IComparer<Feature>.        
        Verified that Sven's   Constructor public Feature(Feature original, Feature toAdd, VariabilityModel vm) is dead code.
    
        Note that member variable wellFormedExpression is inherited from Influence Function
        
    """    
    def __init__(self, name, VariabilityModel):
        
        self.parent = None
        self.name = name
        self.Constant = 0
        
#        self.XOffset = -1
        
    def evalOnConfiguration(self, aConfiguration):
        pass
    
    def isRoot(self):
        return self.name == "root"    
    

    
    def getParentFeature(self):
        return self.parent

    def __eq__(self, other):
        """
        Compares two features based on the components of the functions.
        
        Parameters
        ----------        
        other : object
        The object to comare with.
        
        Returns
        -------
        True if both features represents the same configuration option combination, false otherwise.
        
        
        Notes
        -----
            Counts how many times each --part-- is present in each --Feature--.
        """
        pass
   
    def compare(self):
        pass
    
    def GetHashCode(self):
        pass
    
    def initHashCode(self):
        pass
    
    def getVariabilityModel(self):
        return self.VariabilityModel
    

"""
            Feature other = (Feature) obj;

            string[] thisFuntion = this.wellFormedExpression.Split('*');
            string[] otherFunction = other.wellFormedExpression.Split('*');

            if (thisFuntion.Length != otherFunction.Length)
                return false;

            Dictionary<string, int> thisParts = new Dictionary<string, int>();
            foreach (string part in thisFuntion)
            {
                if (thisParts.ContainsKey(part))
                {
                    int value = thisParts[part] + 1;
                    thisParts.Remove(part);
                    thisParts.Add(part, value);
                }
                else
                {
                    thisParts.Add(part, 1);
                }
            }


            foreach (string part in otherFunction)
            {
                if (thisParts.ContainsKey(part))
                {
                    int remainingNumber = thisParts[part] - 1;
                    thisParts.Remove(part);
                    if (remainingNumber > 0)
                    {
                        thisParts.Add(part, remainingNumber);
                    }

                }
                else
                {
                    return false;
                }
            }

            if (thisParts.Count > 0)
                return false;

""" 


#    def isBasicFeature(self):
#        return self.isBasic 
    
#    def getXOffset(self):
#        """
#        Used when mapping to 'original features'
#        """
#        return self.XOffset