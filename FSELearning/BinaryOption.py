    #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 14 11:00:22 2019

@author: rafaelolaechea
"""

BINARY_VALUE_SELECTED = 1
BINARY_VALUE_DESELECTED = 2


"""
Supposed to inherit from ConfigurationOption.cs.

But we don't have 


    public abstract class ConfigurationOption : IComparable<ConfigurationOption>
    {
        private String name = "";

        public String Name
        {
            get { return name; }
            set {
                if (!value.All(Char.IsLetter))
                    this.name = removeInvalidChars(value);
                else
                    this.name = value;
                }
        }

        private String outputString = "";

        /// <summary>
        /// Textual representation of the configuration to use it as an parameter/configuration option of a customizable system. 
        /// </summary>
        public String OutputString
        {
            get { return outputString; }
            set { outputString = value; }
        }

        private String prefix = "";

        /// <summary>
        /// Prefix may be required when printing a configuration (e.g., "-")
        /// </summary>
        public String Prefix
        {
            get { return prefix; }
            set { prefix = value; }
        }

        private String postfix = "";

        /// <summary>
        /// Postfix may be required when printing a configuration
        /// </summary>
        public String Postfix
        {
            get { return postfix; }
            set { postfix = value; }
        }

        private List<List<ConfigurationOption>> implied_Options = new List<List<ConfigurationOption>>();
        private List<List<String>> implied_Options_names = new List<List<String>>();

        /// <summary>
        /// List, in which the current option implies one and/or a combination of other options
        /// </summary>
        public List<List<ConfigurationOption>> Implied_Options
        {
            get { return implied_Options; }
            set { implied_Options = value; }
        }

        private List<List<ConfigurationOption>> excluded_Options = new List<List<ConfigurationOption>>();
        private List<List<String>> excluded_Options_names = new List<List<string>>();
 
        /// <summary>
        /// List, in which the current option excludes the selection of one and/or a combination of other options
        /// </summary>
        public List<List<ConfigurationOption>> Excluded_Options
        {
            get { return excluded_Options; }
            set { excluded_Options = value; }
        }

        private VariabilityModel vm = null;

        private ConfigurationOption parent = null;
        private String parentName = "";

        /// <summary>
        /// This options implies the selection of its parent (hence, it is also present in the implied_Options field
        /// </summary>
        public ConfigurationOption Parent
        {
            get { return parent; }
            set { parent = value; }
        }
        

        private List<ConfigurationOption> children = new List<ConfigurationOption>();
        private List<String> children_names = new List<String>();

        /// <summary>
        /// This option's child options. These are not necessarily implied.
        /// </summary>
        internal List<ConfigurationOption> Children
        {
            get { return children; }
            set { children = value; }
        }



        public ConfigurationOption(VariabilityModel vm, String name)
        {
            this.vm = vm;
            if (!name.All(Char.IsLetter))
                this.name = removeInvalidChars(name);
            else
                this.name = name;
        }

        public int CompareTo(ConfigurationOption other)
        {
            return this.name.CompareTo(other.name);
        }



...

        /// </summary>
        internal void init()
        {
            this.parent = vm.getBinaryOption(parentName);
            foreach (var name in this.children_names)
            {
                ConfigurationOption c = vm.getBinaryOption(name);
                if(c == null)
                    c = vm.getNumericOption(name);
                if(c == null)
                    continue;
                this.children.Add(c);
            }

            foreach (var imply_names in this.implied_Options_names)
            {
                List<ConfigurationOption> optionImplies = new List<ConfigurationOption>();
                foreach (var optName in imply_names)
                {
                    ConfigurationOption c = vm.getBinaryOption(optName);
                    if (c == null)
                        c = vm.getNumericOption(optName);
                    if (c == null)
                        continue;
                    optionImplies.Add(c);
                }
                this.implied_Options.Add(optionImplies);
            }

            foreach (var exclud_names in this.excluded_Options_names)
            {
                List<ConfigurationOption> excImplies = new List<ConfigurationOption>();
                foreach (var optName in exclud_names)
                {
                    ConfigurationOption c = vm.getBinaryOption(optName);
                    if (c == null)
                        c = vm.getNumericOption(optName);
                    if (c == null)
                        continue;
                    excImplies.Add(c);
                }
                this.excluded_Options.Add(excImplies);
            }
        }
...
        /// <summary>
        /// Checks whether the given option is an ancestor of the current option (recursive method).
        /// </summary>
        /// <param name="optionToCompare">The configuration option that might be an ancestor.</param>
        /// <returns>True if it is an ancestor, false otherwise</returns>
        public bool isAncestor(ConfigurationOption optionToCompare)
        {
            if (this.Parent != null)
            {
                if (this.Parent == optionToCompare)
                    return true;
                else
                    return this.Parent.isAncestor(optionToCompare);
            }
            return false;
        }

        private String removeInvalidChars(string s)
        {
            StringBuilder sb = new StringBuilder();
            foreach (char c in s)
            {
                if (!Char.IsLetter(c))
                    continue;
                else
                    sb.Append(c);
            }
            return sb.ToString();
        }

        public override string ToString()
        {
            return this.Name;
        }



Configuration
    Stores children names
    but also children objects from VM.
    
    
    public ConfigurationOption(VariabilityModel vm, String name)


"""


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
        In python is based on < operator. 
        

        Parameters
        ----------        
        otherOption : ConfigurationOption            
        """
        return self.name == self.name
        
    def __gt__(self, otherOption):
        """
        Implements compareTo operator by using < comparison --- enables sorting.
        """
        return self.name < otherOption.name
    
    
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
        whether we represent a root option
        """
        return self.name == "root"