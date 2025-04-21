"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : None
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : None
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : customize_log.py
# DESCRIPTION                    : This is the utility file for controlling logs
# PRERQUISTE                     : CVF objects should be created.
#                                  self.__TF = self.CVFTestFactory.TestFixture has to be
#                                  passed while creating the customize_log object.
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR                         : Arockiaraj JAI
# REVIEWED BY                    : None
# DATE                           : 15-Aug-2022
################################################################################
"""

# Python future modules for python3 forward compatibility
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    from builtins import *
from past.utils import old_div

# SDDVT - Configuration Data
from SDDVT.Common.generic_log_msg import gen_log_msg
from SDDVT.Common.std_log_format import std_log_format

# CVF Packages
import Core.Configuration as Configuration

# Python Build-in Modules
import os
import sys
import re
import math
from inspect import currentframe, getframeinfo

# Global Variables


# Customize log Class - Begins
class customize_log(std_log_format, gen_log_msg):
    def __init__(self, tf, fatal=None, error=None, warn=None, info=None, debug=None, noise=None, with_fn=None, with_ln=None, with_func=None):

        ###### CVFTestFactory TestFixture Object ######
        self.__TF = tf

        ###### Customize Log ######
        self.fatal = fatal if fatal != None else self.currCfg.variation.fatal
        self.error = error if error != None else self.currCfg.variation.err
        self.warn = warn if warn != None else self.currCfg.variation.warn
        self.info = info if info != None else self.currCfg.variation.info
        self.debug =  debug if debug != None else self.currCfg.variation.dbg
        self.noise = noise  if noise != None else self.currCfg.variation.noise
        self.with_fn = with_fn if with_fn != None else self.currCfg.variation.with_fn
        self.with_ln = with_ln if with_ln != None else self.currCfg.variation.with_ln
        self.with_func = with_func if with_func != None else self.currCfg.variation.with_func

        #self.__TF.logger.Info ("Base Constructor-Invoked...")

    def runtimeChangeLogLevel(self):
        #Load the variable at runtime

        RunTimeLogLevelFile = os.path.join(Configuration.ConfigurationManagerInitializer.ConfigurationManager.currentConfiguration.system.TestsDir, r"SDDVT\Common\RunTimeLogLevel.txt")
        runTimeLogLevelFileHandle = open(RunTimeLogLevelFile)
        runTimeLogLevelFileHandle_content = runTimeLogLevelFileHandle.readlines()

        for line in runTimeLogLevelFileHandle_content:
            line=line.strip("\n")
            #self.__TF.logger.Info (line)
            if "fatal=" in line:
                self.fatal = eval(line.split("=")[-1])
                #self.__TF.logger.Info ("self.fatal %s" %self.fatal)
            elif "err=" in line:
                self.error = eval(line.split("=")[-1])
                #self.__TF.logger.Info ("self.error %s" %self.error)
            elif "warn=" in line:
                self.error = eval(line.split("=")[-1])
                #self.__TF.logger.Info ("self.error %s" %self.error)
            elif "info=" in line:
                self.info = eval(line.split("=")[-1])
                #self.__TF.logger.Info ("self.info %s" %self.info)
            elif "dbg=" in line:
                self.debug = eval(line.split("=")[-1])
                #self.__TF.logger.Info ("self.debug %s" %self.debug)
            elif "noise=" in line:
                self.noise = eval(line.split("=")[-1])
                #self.__TF.logger.Info ("self.noise %s" %self.noise)
            elif "with_fn=" in line:
                self.with_fn = eval(line.split("=")[-1])
                #self.__TF.logger.Info ("self.with_fn %s" %self.with_fn)
            elif "with_ln=" in line:
                self.with_ln = eval(line.split("=")[-1])
                #self.__TF.logger.Info ("self.with_ln %s" %self.with_ln)
            elif "with_func=" in line:
                self.with_func = eval(line.split("=")[-1])
                #self.__TF.logger.Info("self.with_func %s" %self.with_func)
            #elif(not (line and line.strip())):
            elif (line == "\n") or (line.isspace()):
                pass
                #self.__TF.logger.Info ("Empty String" + line)
            else:
                self.__TF.logger.Error ("Invalid Runlevel" + line)

    def __convert_str(self, fn, ln, func, var):
        """
        Function Name: __convert_str
        Description: Converting/merging all the given inputs
        Function Arguments: fn - filename, ln - line number, func - function name, var - variables
        Return: None
        """
        if var == None:
            var = " "

        if self.with_fn == True and self.with_ln == True and self.with_func == True:
            return "%s:%d [%s]> %s" % (fn, ln, func, var)
        elif self.with_fn == True and self.with_ln == True and self.with_func == False:
            return "%s:%d> %s" % (fn, ln, var)
        elif self.with_fn == True and self.with_ln == False and self.with_func == True:
            return "%s [%s]> %s" % (fn, func, var)
        elif self.with_fn == False and self.with_ln == True and self.with_func == True:
            return ":%d [%s]> %s" % (ln, func, var)
        elif self.with_fn == True:
            return "%s> %s" % (fn, var)
        elif self.with_ln == True:
            return "Ln:%d> %s" % (ln, var)
        elif self.with_func == True:
            return "[%s]> %s" % (func, var)
        else:
            return "%s" % (var)

    def fatalLog(self, fn, ln, func, var=None, fp=None):
        log = self.__convert_str(fn, ln, func, var)
        if(self.fatal == True):
            self.__TF.logger.Fatal(log)
        if(fp != None):
            fp.write(log+"\n")

    def errorLog(self, fn, ln, func, var=None, fp=None):
        log = self.__convert_str(fn, ln, func, var)
        if(self.error == True):
            self.__TF.logger.Error(log)
        if(fp != None):
            fp.write(log+"\n")

    def warningLog(self, fn, ln, func, var=None, fp=None):
        log = self.__convert_str(fn, ln, func, var)
        if(self.warn == True):
            self.__TF.logger.Warning(log)
        if(fp != None):
            fp.write(log+"\n")

    def infoLog(self, fn, ln, func, var=None, fp=None):
        log = self.__convert_str(fn, ln, func, var)
        if(self.info == True):
            self.__TF.logger.Info(log)
        if(fp != None):
            fp.write(log+"\n")

    def debugLog(self, fn, ln, func, var=None, fp=None):
        log = self.__convert_str(fn, ln, func, var)
        if(self.debug == True):
            self.__TF.logger.Debug(log)
        if(fp != None):
            fp.write(log+"\n")

    def noiseLog(self, fn, ln, func, var=None, fp=None):
        tag_fn = "[NOISE]: "+fn
        log = self.__convert_str(tag_fn, ln, func, var)
        if(self.noise == True):
            self.__TF.logger.Info(log)
        if(fp != None):
            fp.write(log+"\n")

    def NoSignInfoLog(self, var, fp=None):
        self.__TF.logger.Info(var)
        if(fp != None):
            fp.write(var+"\n")

    def blankLine(self, fp=None):
        self.__TF.logger.Info("")
        if(fp != None):
            fp.write("")

    def HashLineWithArg(self, string_name, fp=None):
        log = "\t\t\t\t######################### %s #########################" % string_name
        self.__TF.logger.Info(log)
        if(fp != None):
            fp.write(log+"\n")

    def StarLine80(self, fp=None):
        log = "*"*80
        self.__TF.logger.Info(log)
        if(fp != None):
            fp.write(log+"\n")

    def HashLine(self, n, fp=None):
        log = "#"*n
        self.__TF.logger.Info(log)
        if(fp != None):
            fp.write(log+"\n")

    def StarLine(self, n, fp=None):
        log = "*"*n
        self.__TF.logger.Info(log)
        if(fp != None):
            fp.write(log+"\n")


    #Ex: ****** Text ******
    #Ex:        Text        (if char=' ')
    def centerTextLine(self, char, text, lenOfLine, fp=None):
        spaceBeforeAndAfterText = 1
        length = len(text)
        left   = int((old_div((lenOfLine-length),2))-spaceBeforeAndAfterText)
        right   = int(math.ceil((old_div((lenOfLine-length),2)))-spaceBeforeAndAfterText)
        log = char*int(left)+' '+text+' '+char*int(right)
        self.__TF.logger.Info(log)
        if(fp != None):
            fp.write(log+"\n")

# Customize log Class - Ends
