#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 13:54:13 2018

@author: rafaelolaechea
"""
import pickle 

def saveObjectToPickleFile(OutputFilename, objectToSave):
    pkl_file = open(OutputFilename, 'wb')
    
    pickle.dump(objectToSave, pkl_file, pickle.HIGHEST_PROTOCOL)
    
    pkl_file.close()
    

    
def loadObjectFromPickle(InputFilename):
    """
    Given a filename for pkl file containing assesment, load it and return it.
    """

        
    pkl_file = open(InputFilename, 'rb')
    
    objectFromPickle = pickle.load(pkl_file)        
           
    pkl_file.close()  
    
    return objectFromPickle
