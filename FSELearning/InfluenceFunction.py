#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 13:42:15 2019

@author: rafaelolaechea
"""
import BinaryOption
from collections import deque


class InfluenceFunction(object):
    """

    Notes
    -----
        Members -- 
        wellFormedExpression describnig the influence function
    """
    def __init__(self,  expression, varModel):
        """
        Creates an influence function based on the expression and variabilty model provided.
        
        Parameters
        ----------
        expression : str        
        A function consisting of numbers, operators and configuration-option names.
        
        varModel: VariabilityModel
        The variability model of the configuration options.
        """
        self.varModel = varModel

        self.wellFormedExpression = ""
        
        self.expressionArray = []
        
        self.participatingBoolOptions = set() #HashSet transformed to list.

        self.numberOfParticipatingFeatures = 0
        
        self.parseExpressionToPolishNotation(expression)  # creates wellFormedExpression

        
    def combineFunctions(self, left,  right):
        """
        This method creates an influence function that is the combination of the left and the right functions, requires both to be defined over the same variability model. 
        
        Returns
        -------
        The combination of the two influence functions.
        """
        
    def getNumberOfParticipatingOptions(self):
        """
        Counts the number of configuration options participating in the function. If an option apears multiple times in the function, it is counted multiple times.
        
        TODO.
        """
        return self.numberOfParticipatingFeatures
        
    def getNumberOfDistinctParticipatingOptions(self):
        """
        Counts the number of different configuration options participating in the function. Mutliple occurrences of an option are ignored.
        """
        
    
    def evaluate(self, config):
        """
        Evaluates the influence function with the given configuration

        Parameters
        ----------
        Configuration : Configuration
        
        Returns
        -------
        The value of the influence function for the configuration
        
        Notes
        -----
        For some uknown reasone noise was inserted.
        """
        return self._evaluationOfRPN(config)
    
    def _evaluationOfRPN(self, config):
        """
        Evaluates Influence Function on Configuration.
        
        Parameters
        ----------
        Configuration : Configuration
        
        Returns
        -------
        The value of the influence function for the configuration        
        """
        counter = 0
        
#         Stack<double> stack = new Stack<double>();
        
        if (len(self.expressionArray) == 0):
            return 1.0
        
#        print("Will execute loop for {0} in  _evaluationOfRPN".format(str(self.expressionArray)))

        dblStack = [] # Fixed, before I  had dblStack inside loop.

        while (counter < len(self.expressionArray) ):
            curr = self.expressionArray[counter]
#            print("Processing {0}".format(curr))
            counter = counter + 1
            
            
            
            if (not (self._isOperatorEval(curr))):
#                print("\t\tAppending curr = {0} to dbldblStack as its not isOperatorEval".format(curr))
                dblStack.append(self._getValueOfToken(config, curr, self.varModel))
            else:
#                print("\t\t processing curr = {0} that returned isOperatorEval(curr) == true".format(curr))
                if curr == "+":
                        rightHandSide = dblStack.pop()
                        if (len(dblStack) == 0):
                            dblStack.append(rightHandSide)
                        leftHandSide = dblStack.pop()
                        dblStack.append(leftHandSide + rightHandSide)
                        
                if curr == "*":
                        rightHandSide = dblStack.pop()
                        leftHandSide = dblStack.pop()  
                        dblStack.append(leftHandSide * rightHandSide)
                
        return dblStack.pop()
#           /// <summary>
#        /// This method creates an influence function that is the combination of the left and the right functions. Both funtions should
#        /// be defined over the same variability model. 
#        /// </summary>
#        /// <param name="left">The first summand of the new influence function.</param>
#        /// <param name="right">The second summand of the new influence function.</param>
#        /// <returns>The combination of the two influence functions.</returns>
#        public static InfluenceFunction combineFunctions(InfluenceFunction left, InfluenceFunction right)
        
    
    def containsParent(self, featureToAdd):
        pass
    
    
    def validConfig(self, config):
        """
        check whether all options in the influence function are also selected in the configuration. 
        
        Parameters
        ----------
        config: Configuration
        """
        pass
    
    def parseExpressionToPolishNotation(self, expression):
        """
        Creates expression in wellFormedExpression member variable
        
        Notes
        -----
        
        Expected Input Values.
        
        Side Effects
        
        Fills wellFormedExpression and Expression Array  
        
        TODO
        """
        print ("Parsing Expression {0}".format(expression))
    
        strQueue = deque([])
        strStack = []
        
        expression = self._createWellFormedExpression(expression).strip()
        
        self.wellFormedExpression = expression
        
        expr = expression.split(" ")
        
#        print("Split Expr is " + str(expr))
        
        i = 0
        while (i < len(expr)):
            
            token = expr[i]
            
            if (self._isOperator(token)):
                if (len(strStack) > 0):
                    # strStack[-1] == strStack.PEEK
                    while( (len(strStack) > 0) and self._isOperator(strStack[-1]) and self._operatorHasGreaterPrecedence(strStack[-1], token) ):
                        strQueue.append(strStack.pop())
                    pass
                
                strStack.append(token)
                i = i + 1
                continue
 #                  if (stack.Count > 0)
 #                   {
 #                       while (stack.Count > 0 && InfluenceFunction.isOperator(stack.Peek()) && InfluenceFunction.operatorHasGreaterPrecedence(stack.Peek(), token))
 #                       {
 #                           queue.Enqueue(stack.Pop());
 #                       }
 #                   }
 #                   stack.Push(token);
 #                   continue;
            elif token == "(":
                strStack.append(token)
            elif token == "[":
                strStack.append(token)
            elif token == "{":
                 strStack.append(token)            
            elif token == "<":
                 strStack.append(token)
            elif token == "(":
                while (not (strStack[-1] == "(")):
                    strQueue.append(strStack.pop())
                strStack.pop()
                i = i + 1
                continue
            elif token == "]":
                while (not (strStack[-1] == "[")):
                    strQueue.append(strStack.pop())
                strQueue.append("]");
                strStack.pop()
                i = i + 1                 

                        
            # Token is number or a feature which has a value
            # features existing in the function but not in the feature model, have to be accepted too
            self._tokenIsAFeatureOrNumber(token);

            strQueue.append(token)
               
            i = i + 1
        
        while(len(strStack) > 0):
            strQueue.append(strStack.pop())
        
        self.expressionArray = list(strQueue)


    def _createWellFormedExpression(self,  expression):
        """
        Adds a whitespace before and after each special character (+,*,[,],....) and replaces each two pair of whitespaces with a single whitespace
        
        Returns
        -------
        A string with all replacements done.
        
        Notes
        -----
        No need for  replaceDifferentLogParts(expression) and replaceLogAndClosingBracket as we don't use logs.
        """
        while (expression.find(" ") != -1):
            expression = expression.replace(" ", "")

        expression = expression.replace("\n", " ")
        expression = expression.replace("\t", " ")

        expression = expression.replace("+", " + ")
        expression = expression.replace("*", " * ")

        expression = expression.replace("(", " ( ")
        expression = expression.replace(")", " ) ")

        expression = expression.replace("[", " [ ")
        expression = expression.replace("]", " ] ")
            
        while (expression.find("  ") != -1):
            expression = expression.replace("  ", " ")
        
        return expression
    
    def _tokenIsAFeatureOrNumber(self, token):
        """
        Adds the feature/option corresponding to the token to the list of Options involved in the influence function and updates  numberOfParticipatingFeatures    
        
        Parameters
        ----------
        token : string
        Name of a feature or a number/double.
        
        Returns
        -------
        True if token correctly parsed.
        

        """
        token = token.strip()
        
        isFloat = True
        try:
            tmpVal = float(token)
        except ValueError:
            isFloat = False
        
        if isFloat:
             # just a number so ignore.
            return True
        
        # Will now parse a string.
        binOption = self.varModel.getBinaryOption(token);
        if (not (binOption == None)):
            if (not (binOption in self.participatingBoolOptions)):
                self.participatingBoolOptions.add(binOption)
                
            self.numberOfParticipatingFeatures = self.numberOfParticipatingFeatures + 1 
            return True
        
        return False
    
    
    def _isOperatorEval(self, token):
        """
        Check if token corresponds to an 'eval' operator  
        
        Paramters
        ---------
        token : string
        """
        token = token.strip()

        if (token == "+"):
            return True

        if (token == "*"):
            return True

        if (token == "]"):
            return True

        return False
        
    def _isOperator(self, token):
        """
        Check if token corresponds to an operator (*, or  +)

        Paramters
        ---------
        token : string        
        """
        token = token.strip()
            
        if(token == "+"):
            return True

        if(token == "*"):
            return True
    
        return False
    
    def _getValueOfToken(self, config, token, theVarModel):
        """
        Computes the value of given token
        Paramters
        ---------
        config: Configuration
        token: string
        theVarModel : Variability Model             
        """       


        token = token.strip()
        
        try:
            tmpVal = float(token)
            return tmpVal
        except ValueError:
            pass
        

        tmpBinOption = theVarModel.getBinaryOption(token)
        
        if (not (tmpBinOption==None)):
             if(token == "base"): # don't really know why --- presume dead code from SVEN's.
                 return 1.0
             
             if (tmpBinOption in config.dctBinaryOptionValues.keys() and \
                 config.dctBinaryOptionValues[tmpBinOption] == BinaryOption.BINARY_VALUE_SELECTED):
                 return 1.0
             else:
                 for aBinOption in config.dctBinaryOptionValues.keys():
                     if(aBinOption.name == tmpBinOption.name):
                         return 1.0

        # Otherwise return 0.0        
        return 0.0
    
    def ToString(self):
        """
        Represent a --Feature Wrapper / Influence function -- as a string.

        TODO        
        """
        tmpRet = self.wellFormedExpression
        
        return tmpRet
    
    def getStringRepresentation(self):

        return self.ToString()
    

    def _operatorHasGreaterPrecedence(self, thisToken,  otherToken):

        thisToken = thisToken.strip()
        
        otherToken = otherToken.split()

        if thisToken == "*" and otherToken == "+":
            return True
        else:
            return False
        