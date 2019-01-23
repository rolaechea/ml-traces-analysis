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

        Verified that Sven's  Constructor public Feature(Feature original, Feature toAdd, VariabilityModel vm) is dead code.
        Verified that related member variable hashcode and method initHashCode are dead code.
    
        Note that member variable wellFormedExpression is inherited from Influence Function
        
    FeatureWrapper shall have a member well formed Expression (TODO)
    
        
    """    
    def __init__(self, name, VariabilityModel):
        
#        self.parent = None
        self.name = name
        self.Constant = 0         
        super(FeatureWrapper, self).__init__(self.name, VariabilityModel)
        
    def evalOnConfiguration(self, aConfiguration):
        """
        Report the value of the feature in aConfiguration.
        
        TODO -- Recurse until evaluating binary values.
        """
        pass
    
    def isRoot(self):
        return self.name == "root"    
    
#    def getParentFeature(self):
#        return self.parent

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
            
            Note that based on the logic implemented in SVEN APEL's code it is not conmutative.
            
            That is A * B would be split into ["A ", " B"] , B * A would be split into ["B ", " A"] so they wouldn't be considered equal.
        """
        if not (type(other) is FeatureWrapper):
            
            return False
        
        # Assume both self and other are of type of FeatureWrapper\        
        thisFunctionStrArray = self.wellFormedExpression.split("*")
        otherFunctionStrArray = other.wellFormedExpression.split("*")
        
        if not(len(thisFunctionStrArray) == len(otherFunctionStrArray)):
            return False
        
        thisPartsStrToIntDct = {}
        
#        print ( "Has same size of str array, thisFunctionStrArray = {0},  otherFunctionStrArray = {1} ".format(\
#               str(thisFunctionStrArray), str(otherFunctionStrArray)))
        
         # Count of Ocurrence of parts in self.
        for aPart in thisFunctionStrArray:
            if aPart in thisPartsStrToIntDct.keys():
                thisPartsStrToIntDct[aPart] = thisPartsStrToIntDct[aPart] + 1
            else:
                thisPartsStrToIntDct[aPart] = 1
#        print ("Got as thisPartsStrToIntDct == {0}".format(str(thisPartsStrToIntDct)))
        
         # Check if exact same number of parts exist in other
        for aPart in otherFunctionStrArray:
#            print ("iterating to remove {0}".format(aPart))
            if aPart  in thisPartsStrToIntDct.keys():
                remainingNumber = thisPartsStrToIntDct[aPart] - 1
                if (remainingNumber > 0):
                    thisPartsStrToIntDct[aPart] = remainingNumber
                else:
                    del thisPartsStrToIntDct[aPart]
            else:
#                print ("{0} not in keys {1}".format(aPart, str(thisPartsStrToIntDct.keys())))
                return False
        
        if len (thisPartsStrToIntDct) > 0:
            return False
        
        return True

   
    def __hash__(self):
        """
        Corresponds to GetHashCode in C# implementation.
        """
        return self.name.__hash__()
    
    def getVariabilityModel(self):
        return self.varModel

    def isValidConfig(self, aConf):
        """
        TODO understand what does isvalid config wrt to CONF for a feature mean.
        """
        return True


        