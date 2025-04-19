"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : ConfigSD_UT009_GlobalSetHSHostFreq.st3
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : ConfigSD_UT009_GlobalSetHSHostFreq.py
# CVF PLAYLIST SCRIPT            : None
# CVF SCRIPT                     : ConfigSD_UT009_GlobalSetHSHostFreq.py
# DESCRIPTION                    : Module to set HS host frequency
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 21/06/2022
################################################################################
"""
from __future__ import division

# SDDVT - Dependent TestCases

# SDDVT - Common Interface for Testcase
from past.utils import old_div
import SDDVT.Common.DvtCommonLib as DvtCommonLib

# SDDVT - SD Specification and commands related Interface
import SDDVT.Common.SDCommandLib as SDCommandLib

# SDDVT - Error Utils
import SDDVT.Common.ErrorCodes as ErrorCodes

# SDDVT - Configuration Data
import SDDVT.Common.getconfig as getconfig
import SDDVT.Common.GlobalConstants as gvar
from SDDVT.Common.customize_log import customize_log

# CVF Packages
import SDCommandWrapper as sdcmdWrap
import CTFServiceWrapper as ServiceWrap
import Protocol.SD.Basic.TestCase as TestCase
import Core.Configuration as Configuration
import Core.ValidationError as ValidationError
import Validation.CVFTestFactory as FactoryMethod

# Python Build-in Modules
import random
import os
import sys
from inspect import currentframe, getframeinfo

# Global Variables


class globalSetHSHostFreq(customize_log):
    """
    class for setting LS Host frequency
    """

    def __init__(self, VTFContainer):
        """
        Name        :  __init__
        Description : Constructor for Class globalSetHSHostFreq
        Arguments   :
           VTFContainer : The VTFContainer used for running the test
        """

        ###### Creating CVF objects ######
        self.vtfContainer = VTFContainer
        self.currCfg = Configuration.ConfigurationManagerInitializer.ConfigurationManager.currentConfiguration
        self.CVFTestFactory = FactoryMethod.CVFTestFactory().GetProtocolLib()
        self.__TF = self.CVFTestFactory.TestFixture
        self.__ErrorManager = self.vtfContainer.device_session.GetErrorManager()

        ###### Loading General Variables ######
        self.__testName = self.vtfContainer.GetTestName()

        ###### Loading testcase specific XML variables ######
        self.testLoop = self.currCfg.variation.testloop
        self.StartBlockAddr = self.currCfg.variation.startlba
        self.NumBlocks = self.currCfg.variation.blockcount
        self.lbaAlignment = self.currCfg.variation.lbaalignment

        ###### Creating SDDVT objects ######
        self.__config = getconfig.getconfig()
        self.__dvtLib = DvtCommonLib.DvtCommonLib(self.vtfContainer)
        self.__sdCmdObj = SDCommandLib.SdCommandClass(self.vtfContainer)
        self.__errorCodes = ErrorCodes.ErrorCodes()
        self.__cardMaxLba = self.__sdCmdObj.MaxLba()

        ###### Customize Log: ######
        self.fn = os.path.basename(getframeinfo(currentframe()).filename)
        customize_log.__init__(self, self.__TF)

        ##### Testcase Specific Variables #####


    def Run(self):
        """
        Name: Run
        Description: To Set the Host Frequency when switching to High Speed mode
        This is a configuration script and can be executed as indivual script also.
        if needed, function can be copied directly.
        Step 1: Get the value of 'globalHSHostFreq', 'globalRandom'
        Step 2: Set the host frequency
        Step 3: Set host frequency based on the value of 'globalRandom'
            if globalRandom == 'Freq'
            Frequency = rand%(globalHSHostFreq - 25000) + 25000
        """

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set the Host Frequency when switching to High Speed mode")
        # Get the value of 'globalHSHostFreq', 'globalRandom'
        try:
            globalHSHostFreq = int(self.__config.get('globalHSHostFreq'))           # value in KHz
            globalRandom = self.__config.get('globalRandom')
        except:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed to get values from config file.")
            raise ValidationError.TestFailError(self.fn, "Failed to get values from config file.")

        # Set the host frequency
        if(globalHSHostFreq != 0):
            sdcmdWrap.SDRSetFrequency(freq = globalHSHostFreq * 1000)               # frequency in Hz
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Host Frequency set to %d MHz" % (old_div(globalHSHostFreq, 1000)))
        else:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Frequency value is ZERO. Not expected.")
            raise ValidationError.TestFailError(self.fn, "Frequency value is ZERO. Not expected.")

        # Set host frequency based on the value of 'globalRandom'
        if (globalRandom == 'Freq'):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalRandom value is %s" % globalRandom)
            Frequency = random.randrange(0, (globalHSHostFreq - 25000)) + 25000
            sdcmdWrap.SDRSetFrequency(freq = Frequency * 1000)                      # Frequency in Hz
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Host Frequency set to %d MHz" % (old_div(Frequency, 1000)))
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalRandom value is %s" % globalRandom)

        return 0
