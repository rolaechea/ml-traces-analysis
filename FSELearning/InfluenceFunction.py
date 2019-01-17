#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 13:42:15 2019

@author: rafaelolaechea
"""

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
        
        self.parseExpressionToPolishNotation(expression)  # creates wellFormedExpression
        
        self.participatingBoolOptions = set() #HashSet.
        
        self.numberOfParticipatingFeatures = 0
        
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
        """
        
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
        
        while (counter < len(self.expressionArray) ):
            curr = self.expressionArray[counter]
            counter = counter + 1
            
            dblStack = []
            
            if (not (self.isOperatorEval(curr))):
                dblStack.append(self.getValueOfToken(config, curr, self.varModel))
            else:
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
        """
        pass
    
        strQueue = []
        strStack = []
        
        expression = self._createWellFormedExpression(expression).strip()
        self.wellFormedExpression = expression
        
        expr = expression.split(" ")
        
        i = 0
        while (i <= len(expr)):
            token = expr[i]
            
            if (self._isOperator(token)):
                pass
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
                pass
            elif token == "[":
                pass
            elif token == "{":
                pass            
            elif token == "<":
                pass
            elif token == ")":
                pass
            elif token == "]":
                pass

            # Token is number or a feature which has a value
            # features existing in the function but not in the feature model, have to be accepted too
            self.tokenIsAFeatureOrNumber(token, self.varModel);
            queue.Enqueue(token);
               
            i = i + 1
    
"""
            Queue<string> queue = new Queue<string>();
            Stack<string> stack = new Stack<string>();

            expression = createWellFormedExpression(expression).Trim();
            this.wellFormedExpression = expression;
            string[] expr = expression.Split(' ');

            for (int i = 0; i < expr.Length; i++)
            {
                string token = expr[i];

                
                if (InfluenceFunction.isOperator(token))
                {
                    if (stack.Count > 0)
                    {
                        while (stack.Count > 0 && InfluenceFunction.isOperator(stack.Peek()) && InfluenceFunction.operatorHasGreaterPrecedence(stack.Peek(), token))
                        {
                            queue.Enqueue(stack.Pop());
                        }
                    }
                    stack.Push(token);
                    continue;
                }
                else if (token.Equals("("))
                    stack.Push(token);
                else if (token.Equals("["))
                    stack.Push(token);
                else if (token.Equals("{"))
                    stack.Push(token);
                else if (token.Equals("<"))
                    stack.Push(token);
                
                else if (token.Equals(")"))
                {
                    while (!stack.Peek().Equals("("))
                    {
                        queue.Enqueue(stack.Pop());
                    }
                    stack.Pop();
                    continue;
                }

                else if (token.Equals("]"))
                {
                    while (!stack.Peek().Equals("["))
                    {
                        queue.Enqueue(stack.Pop());
                    }
                    queue.Enqueue("]");
                    stack.Pop();
                    continue;
                }
                // token is number or a feature which has a value
                // features existing in the function but not in the feature model, have to be accepted too
               tokenIsAFeatureOrNumber(token, this.varModel);
               queue.Enqueue(token);
               
            }

            // stack abbauen
            while (stack.Count > 0)
            {
                queue.Enqueue(stack.Pop());
            }
            expressionArray = queue.ToArray();
"""    
    
    
    
    def _createWellFormedExpression(self,  expression):
        """
        Adds a whitespace before and after each special character (+,*,[,],....) and replaces each two pair of whitespaces with a single whitespace
        
        Returns
        -------
        A string with all replacements done.
        
        Notes
        -----
        No need for     replaceDifferentLogParts(expression) and replaceLogAndClosingBracket as we don't use logs.
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
    
    def _tokenIsAFeatureOrNumber(self):
        """
        TODO
        """