#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  9 17:33:15 2019

@author: rafaelolaechea
"""
import numpy as np
from sklearn.linear_model import LinearRegression

from FeatureWrapper import FeatureWrapper
from LearningRound import LearningRound
from Interaction import Interaction





class FeatureSubsetSelection(object):
    """
    Executes an adapted forward feature selectino procedure.
    
    Notes
    ----- 
    Depends on   
    """
    def __init__(self, infModel):
        """      
        Constructor of the learning class. It reads all configuration options and generates candidates for possible influences (i.e., features).
        Parameters
        ----------
        infModel  : InfluenceModels           
            The influence model which will later hold all determined influences and contains the variability model from which we derive all configuration options.
        """
        self.infModel = infModel
        self.MLSettings = None
        
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
        for f in bestRound.FeatureSet:
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
        return self.FeatureSet    
            
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
            candidates.extend(self.generateCandidates(currentLearningRound.FeatureSet, aBasicFeature))

        dctErrorOfFeature = {}
        bestCandidate = None
        
        for aCandidateFeature in candidates:
            
            if (aCandidateFeature in self.badFeatures.keys() and self.badFeatures[aCandidateFeature] > 0):
                self.badFeatures[aCandidateFeature] -= 1
                continue
            
            if (aCandidateFeature in dctErrorOfFeature.keys()):
                continue
            
            newModel = self.copyCombinationFeatures(currentLearningRound.FeatureSet)
            newModel.append(aCandidateFeature)
        
            if (not self.fitModel(newModel)):
                continue
            
            
            errorOfModel, temp = self.computeModelError(newModel)

            dctErrorOfFeature.append(aCandidateFeature, temp)
            
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
            #    if (this.MLsettings.limitFeatureSize && (feature.getNumberOfParticipatingOptions() == this.MLsettings.featureSizeTrehold))
            #        continue;
            if self.MLsettings.limitFeatureSize and (aFeature.getNumberOfParticipatingOptions() == self.MLsettings.featureSizeTrehold):
                continue
            
            # Exclude interactions with the root option and interactions of a binart feature with itself.       
            
            # We do not want to generate interactions with the root option
            #                if ((feature.participatingNumOptions.Count == 0 && feature.participatingBoolOptions.Count == 1 && feature.participatingBoolOptions.ElementAt(0) == infModel.Vm.Root)
            #                    || basicFeature.participatingNumOptions.Count == 0 && basicFeature.participatingBoolOptions.Count == 1 && basicFeature.participatingBoolOptions.ElementAt(0) == infModel.Vm.Root)
            #                    continue;            
            if ( (aFeature.getNumberOfParticipatingOptions() == 1) and \
                aFeature.participatingBoolOptions[0]  == self.infModel.vm.getRoot()):                
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
            
            currentLearningRound.FeatureSet.extend(self.strictlyMandatoryFeatures)
            
        oldRoundError = float("inf")
        
        stayInLoop = True
        
        
        # Perform forward steps until reaching saturation.
        while(stayInLoop):
            oldRoundError = currentLearningRound.validationError
            
            currentLearningRound = self.performForwardStep(currentLearningRound);

            if currentLearningRound == None:
                return
            
            self.learningHistory.append(currentLearningRound)
            
            if self.MLSettings.useBackward:
                
                currentLearningRound = self.performBackwardStep(currentLearningRound)
                
                self.learningHistory.append(currentLearningRound)


            stayInLoop =  not (self.abortLearning(currentLearningRound, oldRoundError))
        # End While
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
            tmpFeatureColumn = self.createSingleFeatureValuesList(eachFeature)
            rowsOfFeatureValueList.append(tmpFeatureColumn)
            
        rowsOfFeatureValueList = np.array(rowsOfFeatureValueList).T.tolist()            


        # Execute Regression.
        theLinearRegressor =  LinearRegression(fit_intercept=False) 
        # fit_intercept is set to False to follow Sven's impl. as the root parameters acts as anchors to create intercept weights.
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
            val = aConfiguration.getNFPValue()
            self.Y_learning.append(val)
        
        # Remove features that are either always present or always absent.
        tmpFeaturesToRemove = []
        for eachInitialFeature in self.initialFeatures:
            
            tmpSingleFeatureList = []
            
            tmpSingleFeatureList.append(eachInitialFeature)
            
            columnOfFeaturePresence = self.createSingleFeatureValuesList(tmpSingleFeatureList)            
            
            countNbFeatureSelections, countNbFeatureDeselections = 0
            
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
            val = aConfiguration.getNFPValue()
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
            if (current.validationError + this.MLsettings.minImprovementPerRound > oldRoundError)
            {
                if (this.MLsettings.withHierarchy)
                {
                    hierachyLevel++;
                    return false;
                }
                else
                    return true;
            }
            return false;
        """
        if (currentLearningRound.round >= self.MLsettings.numberOfRounds):
                return True
        return False


    def computeLearningError(self, minimalErrorModel):
        """
        TODO
        """        
        pass
        #                                   computeLearningError(minimalErrorModel, out relativeErrorTrain),


    def computeValidationError(self, minimalErrorModel):
        """
        TODO
        """
        pass
        #                                   computeValidationError(minimalErrorModel, out relativeErrorEval), 

    def computeModelError(self):
        """
        Computes the error of a specific model.
        
        Returns
        -------
        
        TODO
        """
        pass     
        
    def computeError(self, currentModel, configs):
        """
        TODO
        /// <summary>
        /// This methods computes the error for the given configuration based on the given model. 
        // It queries the ML settings to used the configured loss function.
        /// As the actual value, it uses the non-functional property stored in the global model -- i.e. true NFP. 
        // If this is not available in the configuration, it uses the default NFP of the configuration.
        /// </summary>
        /// <param name="currentModel">The model containing all fitted features.</param>
        /// <param name="configs">The configuration for which the error should be computed. 
                    It contains also the actually measured value.</param>
        /// <returns>The error depending on the configured loss function (e.g., relative, least squares, absolute).</returns>
      
        public double computeError(List<Feature> currentModel, List<Configuration> configs, out double relativeError)        
        
        """
        pass
    
    
    
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
        if theFeature in self.DM_columnsCache.keys():            
            # Return soted column vector             
            return self.DM_columnsCache[theFeature]

        else:
            # Create column vector and store in cache. 
            columnVector = [0 for x in range(len(self.learningSet))]
            i = 0
            for eachConfiguration in self.learningSet:
                if (theFeature.isValidConfig(eachConfiguration)):
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
        if (current.roundNum < 3 or len(current.FeatureSet) < 2):
            return current
        
        abort = False
        tmpFeatureSet = self.copyCombination(current.FeatureSet);
        while(not abort):
                roundError = float("inf")
                toRemove = None
        
                for deletionCandidate in tmpFeatureSet:
                    tempSet = self.copyCombination(tmpFeatureSet);
                    tempSet.remove(deletionCandidate)
                    
                    error, relativeError = self.computeModelError(tempSet)
                    
                    if ( (error - self.MLsettings.backwardErrorDelta) < current.validationError and error < roundError):
                        roundError = error
                        toRemove = deletionCandidate                        
                    
                if not (toRemove == None):
                    tmpFeatureSet.remove(toRemove)
                    
                if len(tmpFeatureSet)<= 2:
                    abort = True
                        
        current.FeatureSet = tmpFeatureSet
        return current