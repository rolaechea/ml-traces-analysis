#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  9 17:33:15 2019

@author: rafaelolaechea
"""
import math
import numpy as np
from sklearn.linear_model import LinearRegression

from FeatureWrapper import FeatureWrapper
from LearningRound import LearningRound
from Interaction import Interaction
import MLSettings




class FeatureSubsetSelection(object):
    """
    Executes an adapted forward feature selectino procedure.
    
    Notes
    ----- 
    Depends on   
    """
    def __init__(self, infModel, tmpMLSettings):
        """      
        Constructor of the learning class. It reads all configuration options and generates candidates for possible influences (i.e., features).
        Parameters
        ----------
        infModel  : InfluenceModels           
            The influence model which will later hold all determined influences and contains the variability model from which we derive all configuration options.
        """
        self.infModel = infModel
        self.ML_Settings = tmpMLSettings
        
        self.learningHistory = []
        self.hierachyLevel = 1
        self.currentRound = None
        
        
        self.initialFeatures = []
        self.strictlyMandatoryFeatures = []
        self.badFeatures = {}
        
        self.learningSet = []
        self.validationSet = []
        self.Y_learning, self.Y_validation = [], []
        
        self.DM_columnsCache = {}
        
        
        for optFeature in self.infModel.vm.getBinaryOptions():
            if not (optFeature.isRoot()):   
                self.initialFeatures.append(FeatureWrapper(optFeature.name, self.infModel.vm))
            
        self.strictlyMandatoryFeatures.append(FeatureWrapper(self.infModel.vm.getRoot().name, self.infModel.vm))


    def isAllInformationAvailableForLearning(self):
        """
        Checks whether all information is available to start learning.
        
        Requires at a minimum that the learning and validation set have been initialized.
        
        Returns
        -------        
        True if both learningSet and validationSet are not empty.
        """
        if (len(self.learningSet) == 0 or len(self.validationSet)==0):
            return False
        
        return True

    def updateInfluenceModel(self):
        """
        Updates the influence model based on the results of the current learning round.
        
        Extracts lowest validation error from all rounds upt to current learning round. 
        Extracts all determined features with their influences       
        Inserts boolean and interaction influences
        
        Notes
        ------        
        Require influence model to have methods: 
            BinaryOptionsInfluence
            InteractionInfluence
            
        Requires learningHistory to be an iterable of Learning Rounds.
        
        Cleared Learning with updating Influence model.
        """
        self.infModel.clearBinaryOptionsInfluence()
        self.infModel.clearInteractionInfluence()
        
        bestRound = None
        lowestError = float("inf")

        # Choose the best round from seen rounds.        
        for LRound in self.learningHistory:
            if LRound.validationError <  lowestError:
                lowestError = LRound.validationError
                bestRound = LRound
        
        #  Update dictionaries InteractionInfluence and BinaryOptionsInfluence in Influence model.
        print("Updating Influence model on bestRoundFeature = {0}".format(str([(x.ToString(), x.Constant) for x in bestRound.featureSet])))
        for f in bestRound.featureSet:
            if len(f.participatingBoolOptions) == 1 and f.getNumberOfParticipatingOptions() == 1:
                # Single Boolean Influence
                self.infModel.BinaryOptionsInfluence[f.participatingBoolOptions[0]] = f
                continue
             
            NewInteraction = Interaction(f)
            self.infModel.InteractionInfluence[NewInteraction] = f
            
         
    def getFeatureSet(self):
        """
        Returns set of Features currently selected.
        """
        return self.featureSet    
            
    def performForwardStep(self, currentLearningRound):
        """
        Makes one further step in learning. That is, it adds one feature to the currentLearningRound
        
        Parameters
        ----------
        currentLearningRound: LearningRound
        Comprises a list of features determined as important influencing factors so far.
        
        Returns
        -------
        Returns a new model (i.e. learning round) with an additional feature.
        
        
        Notes
        -----
            Directly depends on generateCandidates, and through generateCandidates on FeatureWrapper.
        """
        minimalRoundError = float("inf")
        minimalErrorModel = []

        
        #Go through each feature of the initial set and combine them with the already present features to build new candidates
        candidates = []
        for aBasicFeature in self.initialFeatures:
            candidates.extend(self.generateCandidates(currentLearningRound.featureSet, aBasicFeature))
            
        dctErrorOfFeature = {}
        bestCandidate = None
        
        for aCandidateFeature in candidates:
            
            if (aCandidateFeature in self.badFeatures.keys() and self.badFeatures[aCandidateFeature] > 0):
                self.badFeatures[aCandidateFeature] -= 1
                continue
            
            if (aCandidateFeature in dctErrorOfFeature.keys()):
                continue
            
            newModel = self.copyCombinationFeatures(currentLearningRound.featureSet)
            newModel.append(aCandidateFeature)
        
            if (not self.fitModel(newModel)):
                continue
            
            
            errorOfModel, temp = self.computeModelError(newModel)

            dctErrorOfFeature[aCandidateFeature] = temp
            
            if errorOfModel < minimalRoundError:                
                    minimalRoundError = errorOfModel
                    minimalErrorModel = newModel
                    bestCandidate = aCandidateFeature                # dead code from SVEN, prob. for debugging.
                
        
        errorTrain, relativeErrorTrain = self.computeLearningError(minimalErrorModel)
        errorEval, relativeErrorEval   = self.computeValidationError(minimalErrorModel)
        
        self.addFeaturesToIgnore(dctErrorOfFeature)

        #LearningRound newRound = new LearningRound(minimalErrorModel, 
        #                                   computeLearningError(minimalErrorModel, out relativeErrorTrain),
        #                                   computeValidationError(minimalErrorModel, out relativeErrorEval), 
        #                                   currentModel.round + 1);
        newRound = LearningRound(minimalErrorModel, errorTrain, errorEval,  currentLearningRound.roundNum + 1)

        newRound.learningError_relative = relativeErrorTrain
        newRound.validationError_relative = relativeErrorEval
        
        return newRound
        

    def generateCandidates(self, currentModel,  basicFeature):
        """
        Returns a set of Candidate Features
    
        The method generates a list of candidates to be added to the current model. 
        These candidates are later fitted using regression and rated for their accuracy in estimating the values of the validation set.
        The basicFeatures comes from the pool of initial features (e.g., all configuration options of the variability model or predefined combinations of options).
        Further candidates are combinations of the basic feature with features already present in the model. 
        That is, we generate candidates as representatives of interactions or higher polynomial functions.

    
        Parameters
        ----------
        
        currentModel: List of Features where each feature is FeatureWrapper object        
        The model containing the features found so far. These features are combined with the basic feature.
        
        basicFeature: Feature
        The feature for which we generate new candidates.
        
        Returns
        -------
        Returns a list of candidates that can be added to the current model. Each candidate is of type .
        
        Notes
        -----
        Possible Features are:
            ExistingFeatures Cross Product X_i, but filtering out repeated features.

                        
        Requires equality/compares of FeatureWrapper equalTo/CompareTo in C# correspond __eq__/__ne__ in python, which must be implemented in FeatureWrapper       
        """        
        listOfCandidates = []


        #   if basicFeature is not part of current model, then add it.       
        if basicFeature not in currentModel:
            listOfCandidates.append(basicFeature)
    
        for aFeature in currentModel:
            # Do not generate interactions beyond desired feature size.
            #    if (this.ML_Settings.limitFeatureSize && (feature.getNumberOfParticipatingOptions() == this.ML_Settings.featureSizeTrehold))
            #        continue;
            if self.ML_Settings.limitFeatureSize and (aFeature.getNumberOfParticipatingOptions() == self.ML_Settings.featureSizeTrehold):
                continue
            
            # Exclude interactions with the root option and interactions of a binart feature with itself.       
            
            # We do not want to generate interactions with the root option
            #                if ((feature.participatingNumOptions.Count == 0 && feature.participatingBoolOptions.Count == 1 && feature.participatingBoolOptions.ElementAt(0) == infModel.Vm.Root)
            #                    || basicFeature.participatingNumOptions.Count == 0 && basicFeature.participatingBoolOptions.Count == 1 && basicFeature.participatingBoolOptions.ElementAt(0) == infModel.Vm.Root)
            #                    continue;            
            if ( (aFeature.getNumberOfParticipatingOptions() == 1) and \
                list(aFeature.participatingBoolOptions)[0]  == self.infModel.vm.getRoot()):                
                continue            
            
            # Exclude Binary times the same binary 
            isFeatureMultiplyingByItself = False
            if ( (aFeature.getNumberOfParticipatingOptions() > 0)):
                
                
                for eachBinOption in basicFeature.participatingBoolOptions:
                     if (eachBinOption in aFeature.participatingBoolOptions):
                         isFeatureMultiplyingByItself = True
                         break
                # Exits inner forloop.
            
            # Exclude Binary times the same binary, achieved via goto in Sven's code.
            # Only add a new feature when isFeatureMultiplyingByItself == False and its not already in the list of candidates.
            if not isFeatureMultiplyingByItself:
               #Feature newCandidate = new Feature(feature.ToString() + " * " + basicFeature.ToString(), basicFeature.getVariabilityModel());
               newCandidate = FeatureWrapper(aFeature.getStringRepresentation() + " * " + basicFeature.getStringRepresentation(), \
                                             basicFeature.getVariabilityModel())
               # if (!currentModel.Contains(newCandidate))
               #     listOfCandidates.Add(newCandidate);      
               if newCandidate not in currentModel:
                   listOfCandidates.append(newCandidate)
      
        
#        print ("Will return the following list of candidates {0}".format(str([x.name for x in listOfCandidates])))
        return listOfCandidates        
    
    
    def learn(self):
        """
        Performs learning using an adapted feature-selection algorithm.
        
        Learning is done in rounds, in which each round adds an additional feature (i.e., configuration option or interaction) to the current model containing all influences.
        Abort criteria is derived from ML_Settings class, such as number of rounds, minimum error, etc.        

        """    
        if not self.isAllInformationAvailableForLearning():
            return
        
        currentLearningRound = LearningRound()

        if len(self.strictlyMandatoryFeatures) > 0:
            
            currentLearningRound.featureSet.extend(self.strictlyMandatoryFeatures)
            
        oldRoundError = float("inf")
        
        stayInLoop = True
        
        #return
       
        # Perform forward steps until reaching saturation.
        while(stayInLoop):
            oldRoundError = currentLearningRound.validationError
            
            currentLearningRound = self.performForwardStep(currentLearningRound);
   
            # Dead code from SVEN.     
            if currentLearningRound == None:
                return
            
            self.learningHistory.append(currentLearningRound)
                        
            if self.ML_Settings.useBackward:
                
                currentLearningRound = self.performBackwardStep(currentLearningRound)
                
                self.learningHistory.append(currentLearningRound)

            
            stayInLoop =  not (self.abortLearning(currentLearningRound, oldRoundError))
        # End While
        print ("Learning History size = {0}".format(len(self.learningHistory)))
        self.updateInfluenceModel()

    def copyCombinationFeatures(self, oldFeatureList):
        """
        This method creates new list of newly created feature objects.
        
        It acts akin to a deep copy of list oldFeatureList.
        
        Parameters
        -----------
        oldFeatureList:  list of features        
        Features that need to be copied
        
        Returns
        -------
        A  list of newly created FeatureWrapper objects
        """
        resultList = []
        if oldFeatureList == []:
            return resultList
        
        for aFeatureSubset in oldFeatureList:
             resultList.append(FeatureWrapper(aFeatureSubset.ToString(), aFeatureSubset.getVariabilityModel()))   
            
        return resultList
        
    
    def fitModel(self, newModel):
        """
        Fit a new model to the learning set.
        
        Parameters
        ----------        
        newModel: List of LearningFeatures
        
        Returns
        -------
        False if the fitting found no further influence or NumberOfElements == 0, True otherwise.
        
        Notes
        -----
        Builds a matrix representing learning set with selected feature. Solves for weights for that matrix versus Y_Learning set.     
        
        Parameters
        ----------     
        featureSet : List of Features
        """
        if len(newModel) == 0 or self.learningSet == 0:
            return False
    
        # Create Matrix where each row represents a configuratino of the learning set. 
        # This is done by transposing columns representing values of each feature across the learning set.        
        rowsOfFeatureValueList = []
        for eachFeature in newModel:
#            print ("Creating a tmpFeatureColumn for feature {0}".format(eachFeature.name))
            tmpFeatureColumn = self.createSingleFeatureValuesList(eachFeature)
#            print("Received tmpFeatureColumn = {0}".format(str( tmpFeatureColumn)))
            rowsOfFeatureValueList.append(tmpFeatureColumn)
            
        rowsOfFeatureValueList = np.array(rowsOfFeatureValueList).T.tolist()            


        # Execute Regression.
        theLinearRegressor =  LinearRegression(fit_intercept=False) 
        # fit_intercept is set to False to follow Sven's impl. as the root parameters acts as anchors to create intercept weights.
        #
        #
        # TODO -- pasing Ready to Perform Regression, 
        # rowsOfFeatureValueList = [[None, None], [None, None], [None, None], [None, None], [None, None], [None, None], [None, None], [None, None], [None, None]]
        print("Ready to Perform Regression, rowsOfFeatureValueList = {0}".format(str(rowsOfFeatureValueList)))
        theLinearRegressor.fit(rowsOfFeatureValueList, self.Y_learning)


        # Store weights.
        for i in range(0, len(theLinearRegressor.coef_)):
            newModel[i].Constant = theLinearRegressor.coef_[i]
       
        # Store respective constants for each feature. 
        if (newModel[len(theLinearRegressor.coef_) - 1].Constant == 0):
            # Following Sven's Implementatno but should probably check some sort of distance from 0.
            return False
        
        return True

    def setLearningSet(self, measurements):
        """
        Sets lists of configurations and measured performance values for learning.

        Converts a List of configurations with its measured value (we take the non-functional property of the global state) into a a learning matrix.
        
        Parameters
        ----------
        measurements : List of Configuration Objects.
        The configurations containing the measured values
        
        Notes
        -----
        Assumes set of chosen features is -- frozen --.
        
        
        1. Adds ConfigurationObjects to LearningSet List
        2. Adds measured value to Y_Learning (list of doubles)
        3. Removes from Initial Features, the features that are always present or always absent.        
        """
        
        # Copy configurations to learning set, and values of configurations to Y learning.
        for aConfiguration in measurements:
            self.learningSet.append(aConfiguration)
            val = aConfiguration.getNfpValue()
            self.Y_learning.append(val)
        
        # Remove features that are either always present or always absent.
        tmpFeaturesToRemove = []
        for eachInitialFeature in self.initialFeatures:

            columnOfFeaturePresence = self.createSingleFeatureValuesList(eachInitialFeature)            
            
            countNbFeatureSelections, countNbFeatureDeselections = 0, 0
            
            for aVal in columnOfFeaturePresence:
                if aVal == 1:
                    countNbFeatureSelections += 1
                if aVal == 0:
                    countNbFeatureDeselections += 1
                if countNbFeatureSelections > 0 and countNbFeatureDeselections > 0:
                    break
                
            # If a feature is all selected or all deselected, then add to features to remove.            
            if (countNbFeatureSelections == len(self.learningSet)):
                tmpFeaturesToRemove.append(eachInitialFeature)

            if (countNbFeatureDeselections == len(self.learningSet)):
                tmpFeaturesToRemove.append(eachInitialFeature)

        #End for eachInitialFeature in self.initialFeatures:                          

        for aFeatureToRemove in tmpFeaturesToRemove:
            # Remove aFeatureToRemove if it exists in initial features.
            if aFeatureToRemove in self.initialFeatures:
                self.initialFeatures.remove(aFeatureToRemove)
                    

    
    def setValidationSet(self, measurements):
        """
        Sets lists of configurations and measured performance values for evaluation/validation.
         
        Converts the given configurations into a validation matrix used to compute the error for a learned model.

        Parameters
        ----------
        measurements : List of Configuration Objects.

        Notes
        -----
        
        Same as setLearningSet but with validationSet but no feature removal.
        """
        for aConfiguration in measurements:
            self.validationSet.append(aConfiguration)
            val = aConfiguration.getNfpValue()
            self.Y_validation.append(val)        
        
    def abortLearning(self, currentLearningRound,  oldRoundError):
        """
        This methods checks whether the learning procedure should be aborted. For this decision, it uses parameters of ML settings, such as the number of rounds

        Parameters
        ----------
        currentLearningRound : LearningRound.        

        
        NOTES
        -----
            TimeSpan diff = DateTime.Now - this.startTime;
            if (current.round > 30 && diff.Minutes > 60)
                return true;
            if (abortDueError(current))
                return true;
            if (current.validationError + this.ML_Settings.minImprovementPerRound > oldRoundError)
            {
                if (this.ML_Settings.withHierarchy)
                {
                    hierachyLevel++;
                    return false;
                }
                else
                    return true;
            }
            return false;
        """
        if (currentLearningRound.roundNum >= self.ML_Settings.numberOfRounds):
                return True
        return False

    def estimate(self, currentModel, aConfiguration):
        """
        Creates an estimate for the given configuration based on the given model.
        
        Parameters
        ----------
        currentModel : list of Features
        aConfiguration: a specific configuration
        
        Returns
        -------
        The estimate.        
        """
        prediction = 0
        for i in range(0, len(currentModel)):
            if(currentModel[i].validConfig(aConfiguration)):
                prediction += currentModel[i].evalOnConfiguration(aConfiguration) * currentModel[i].Constant
    
        return prediction
    

    def computeLearningError(self, currentModel):
        """
        Computes the error of the current model for all configurations in the learning set
                
        Parameters
        ----------
        currentModel: List of FeatureWrapper Objects        
        The features that have been fitted so far 
        
        Returns 
        -------
        The mean error of the validation set. It depends on the parameters in ML settings which loss function is used. Also the relative error.
        """        
        return self.computeError(currentModel, self.validationSet)
        #                                   computeLearningError(minimalErrorModel, out relativeErrorTrain),


    def computeValidationError(self, currentModel):
        """
        Computes the error of the current model for all configurations in the validation set.
        
        Parameters
        ----------
        currentModel: List of FeatureWrapper Objects        
        The features that have been fitted so far 

        Returns
        --------

        A tuple consisting of the mean error of the validation set and the relative error. It depends on the parameters in ML settings which loss function is used        
        """
        return self.computeError(currentModel, self.validationSet)


    def computeModelError(self, currentModel):
        """
        Computes the general error for the current model. It depends on the parameters of ML settings which loss function and whether cross validation is used.
        
        Parameters
        ----------
        currentModel : List of feature objects.
               
        Returns
        -------
        The error depending on the configured loss function (e.g., relative, least squares, absolute), and the relative error.         
        """
        if self.ML_Settings.crossValidation:
            return self.computeValidationError(currentModel)
        else:
        
            tmpMainErrorLearning, tmpRelativeErrorLearning = self.computeLearningError(currentModel)
            
            tmpMainErrorValidation, tmpRelativeErrorValidation = self.computeLearningError(currentModel)

            return ( ( tmpMainErrorLearning + tmpMainErrorValidation ) / 2,  ( tmpMainErrorValidation + tmpRelativeErrorValidation ) / 2)

        
    def computeError(self, currentModel, configs):
        """        
        Computes the error for the given configuration set based on the given model
        
        It queries the ML settings to used the configured loss function and uses stored measured values.
        
        Parameters
        ----------
        currentModel : List of features.
        configs: List of Configurations
        
        Returns
        -------
        Tuple of error and relativerror. Error is based on the configured loss function.
        """
        error_sum = 0
        relativeError = 0
        skips = 0
        
        for eachConfiguration in configs:
            estimatedValue = self.estimate(currentModel, eachConfiguration)
            
            realValue = eachConfiguration.getNfpValue()
            
            if (realValue < 1):
                # Ignore cases where real value is close to zero.
                skips = skips + 1
                continue
            else:
                    er =  abs(100 - ((estimatedValue * 100) / realValue))
                    relativeError = relativeError + er
                    
                # Other cases.
            
            error = 0
            
            if self.ML_Settings.lossFunction == MLSettings.RELATIVE:
                if (realValue < 1):
                    # following sven
                    error = abs(((2 * (realValue - estimatedValue) / (realValue + estimatedValue)) - 1) * 100)
                else:
                    error = abs(100 - ((estimatedValue * 100) / realValue))
                    
            elif  self.ML_Settings.lossFunction == MLSettings.LEASTSQUARES:
                
                error = math.pow(realValue - estimatedValue, 2)                
                
            elif self.ML_Settings.lossFunction == MLSettings.ABSOLUTE:

                error = abs(realValue - estimatedValue)
                
   
            error_sum = error_sum + error
            
        relativeError = relativeError / (len(configs) - skips)
        
        return ( (error_sum / (len(configs) - skips)), relativeError)

    
    
    def createSingleFeatureValuesList(self, theFeature):
        """
        Creates the columns for a single feature - adapted from create data matrix.
        Uses cache.

        Parameters
        ----------        
        theFeature:  a Feature 
        (originall supposedly)

        Returns
        -------
        A list representing the values of the feature for the configurations of the learning set.        
 
        Notes
        -----
        Adapted from createDataMatrix and generateDM_column                   
        """
#        print("theFeature " + str(theFeature))
        if theFeature in self.DM_columnsCache.keys():            
            # Return soted column vector             
#            print(" The feature {0} is  in cache ".format(theFeature.name))
            return self.DM_columnsCache[theFeature]

        else:
#            print(" The feature {0} not in cache ".format(theFeature.name))
            # Create column vector and store in cache. 
            columnVector = [0 for x in range(len(self.learningSet))]
            
#            print("ColumnVector set to {0}".format(str(columnVector)))
            
            i = 0
            for eachConfiguration in self.learningSet:
                if (theFeature.isValidConfig(eachConfiguration)):
                    # Missing Implementation evalOnConfiguration
                    columnVector[i] = theFeature.evalOnConfiguration(eachConfiguration)
                i += 1
            
            self.DM_columnsCache[theFeature] =  columnVector
            
            return columnVector
        
    def addFeaturesToIgnore(self, dctErrorOfCandidates):
        """
        Keep track of which features to ignore.
        
        We do not want to consider candidates in the next X rounds that showed no or 
        only a slight improvment in accuracy relative to all other candidates
        
        Parameters
        ----------        
        dctErrorOfCandidates : Dictionary
        The Dictionary containing all candidate features with their fitted error rate

        """
        
        keyValueList = list(dctErrorOfCandidates.items())
        
        # sort by fitted error rate.
        keyValueList.sort(key=lambda elem: elem[1])
        
        minNumberToKeep = 5
        
        i =  len(keyValueList) - 1
        while( i > ( len(keyValueList) / 2 )):
            if i <= minNumberToKeep:
                return
            # keyValueList[i][0] === keyValueList[i].KEY 
            if (keyValueList[i][0] in self.badFeatures.keys()):
                self.badFeatures[keyValueList[i][0]] = 3
            else:
                # could remove else as python doesn't distinguish syntax between dict update and insert.
                self.badFeatures[keyValueList[i][0]] = 3       

            i = i - 1
   
    def performBackwardStep(self, current):
        """
        Removes already learned features from the model if they have only a small impact on the prediction accuracy. 
        
        This should help keeping the model simple, reducing the danger of overfitting, and leaving local optima.
        
        Parameters
        ----------
        current: LearningRound
        The current learning round that we will attemp to simplify.
        
        Returns
        -------
        A new model that might be smaller than the original one and might have a slightly worse prediction accuracy.        
        """
        if (current.roundNum < 3 or len(current.featureSet) < 2):
            return current
        
        abort = False
        tmpFeatureSet = self.copyCombination(current.featureSet);
        while(not abort):
                roundError = float("inf")
                toRemove = None
        
                for deletionCandidate in tmpFeatureSet:
                    tempSet = self.copyCombination(tmpFeatureSet);
                    tempSet.remove(deletionCandidate)
                    
                    error, relativeError = self.computeModelError(tempSet)
                    
                    if ( (error - self.ML_Settings.backwardErrorDelta) < current.validationError and error < roundError):
                        roundError = error
                        toRemove = deletionCandidate                        
                    
                if not (toRemove == None):
                    tmpFeatureSet.remove(toRemove)
                    
                if len(tmpFeatureSet)<= 2:
                    abort = True
                        
        current.featureSet = tmpFeatureSet
        return current