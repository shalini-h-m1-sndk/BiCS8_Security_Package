"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : ConfigSD_UT015_GlobalSetVHSHostFreq.st3
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : ConfigSD_UT015_GlobalSetVHSHostFreq.py
# CVF PLAYLIST SCRIPT            : None
# CVF SCRIPT                     : ConfigSD_UT015_GlobalSetVHSHostFreq.py
# DESCRIPTION                    : Module to set the very high host frequency
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 19/09/2022
################################################################################
"""

# SDDVT - Dependent TestCases

# SDDVT - Common Interface for Testcase
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


class globalSetVeryHSHostFreq(customize_log):
    """
    class for setting Very High Host Frequency
    """

    def __init__(self, VTFContainer):
        """
        Name        :  __init__
        Description : Constructor for Class globalSetVeryHSHostFreq
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
        Name : Run
        Description: To set the very High Host Frequency
        This is a configuration script and can be executed as indivual script also.
        if needed, function can be copied directly.
        Step 1: Get the value of 'globalVHSHostFreq'
        Step 2: Set frequency as 'globalVHSHostFreq'
        Step 3: Get the value of 'globalRandom'
        Step 4: Set Host frequency based on value of 'globalRandom'
        If any of the steps fail, exception is handled in CTF and test will fail.
        """

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set the Very High Host Frequency (e.g. lightning)")

        # et the value of 'globalVHSHostFreq'
        globalVHSHostFreq = int(self.__config.get('globalVHSHostFreq'))  # Frequency value in KHz

        # setting the frequency with tuning
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Calling SetFreqWithTuning......\n")
        self.__sdCmdObj.SetFreqWithTuning(Freq = globalVHSHostFreq)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Host Frequency set to %d KHz" % globalVHSHostFreq)

        # Get the value of globalRandom
        globalRandom = self.__config.get('globalRandom')

        # Set Host frequency based on value of globalRandom
        if (globalRandom == 'Freq'):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalRandom value is %s" % globalRandom)
            Frequency = random.randint(0, (globalVHSHostFreq - 70000)) + 70000  # Frequency in KHz
            self.__sdCmdObj.SetFreqWithTuning(Freq = Frequency)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Host Frequency set to %d KHz" % Frequency)
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalRandom value is %s" % globalRandom)

        return 0
