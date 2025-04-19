"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : ACMD41_UT07_Load_LocalVariables.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : ACMD41_UT07_Load_LocalVariables.py
# DESCRIPTION                    : Read required variables from params file
# PRERQUISTE                     : ACMD41_UT11_SetFreq_Volt_Timeout.py
# STANDALONE EXECUTION           : No. It is an utility script.
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : Nov-2022
################################################################################
"""

# Python future modules for python3 forward compatibility
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    from builtins import *

# SDDVT - Dependent TestCases
import ACMD41_UT11_SetFreq_Volt_Timeout as SetFreqVoltTimeOut

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


# Testcase Utility Class - Begins
class ACMD41_UT07_Load_LocalVariables(customize_log):
    def __init__(self, VTFContainer):
        """
        1) Creating CVF objects
        2) Loading General Variables
        3) Loading testcase specific XML variables [If any variable is added in the xml, it needs to be loaded here]
        4) Creating SDDVT objects
        5) Check and Switch to SD Protocol
        6) Customize Log base class Object Initialization
        7) Declare the Testcase Specific Variables
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

        ###### Check and Switch to SD Protocol ######
        self.protocolName = self.__dvtLib.switchProtocol(ScriptName = self.__testName)

        ###### Customize Log ######
        self.fn = os.path.basename(getframeinfo(currentframe()).filename)
        customize_log.__init__(self, self.__TF)

        ###### Testcase Specific Variables ######
        self.__setFreqVoltTO = SetFreqVoltTimeOut.ACMD41_UT11_SetFreq_Volt_Timeout(self.vtfContainer)


    # Testcase Utility Logic - Starts
    def Run(self, ret = 0):
        """
        Name : Run
        """
        # Call Script Utility_Set_Freq_Volt_Timeout
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call to Set_Freq_Volt_Timeout routine. \n")
        self.__setFreqVoltTO.Run()

        # Read values into LocalVariables dictionary
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Populate the local variables.\n")
        LocalVariables = {}

        GlobalOCRArgValue = int(self.__config.get('globalOCRArgValue'))
        GlobalOCRResValue = int(self.__config.get('globalOCRResValue'))

        LocalVariables['SendOCR'] = GlobalOCRArgValue
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SendOCR: %d" % LocalVariables['SendOCR'])

        LocalVariables['ExpectOCR'] = GlobalOCRResValue
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ExpectOCR: %d" % LocalVariables['ExpectOCR'])

        LocalVariables['SendFirstOCR'] = GlobalOCRArgValue
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SendFirstOCR: %d" % LocalVariables['SendFirstOCR'])

        LocalVariables['SendNextOCR'] = GlobalOCRArgValue
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SendNextOCR: %d" % LocalVariables['SendNextOCR'])

        LocalVariables['SingleCommand'] = 0
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SingleCommand: %d" % LocalVariables['SingleCommand'])

        # SingleCommandTestType: 1 = ReverseXpcS18r, 2 = ReverseXPC, 3 = ReverseS18R, 4 = ReverseHCS, 5 = RandomXpcS18r
        LocalVariables['SingleCommandTestType'] = 1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SingleCommandTestType: %d" % LocalVariables['SingleCommandTestType'])

        LocalVariables['Identification'] = 1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification: %d" % LocalVariables['Identification'])

        # ProtocolMode: 1 = SD OK, 2 = SD Error, 3 = SPI OK, 4 = SPI Error
        LocalVariables['ProtocolMode'] = 1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ProtocolMode: %d" % LocalVariables['ProtocolMode'])

        # VerifyType:   1 = Utility_Successful_Verify.st3, 2 = Utility_Failure_Verify.st3, 3 = Utility_Successful_Verify_MaxVoltage.st3
        LocalVariables['VerifyType'] = 0
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VerifyType: %d" % LocalVariables['VerifyType'])

        LocalVariables['SendCMD0'] = 1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SendCMD0: %d" % LocalVariables['SendCMD0'])

        LocalVariables['SendCMD8'] = 1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SendCMD8: %d" % LocalVariables['SendCMD8'])

        LocalVariables['SendCMD58'] = 1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SendCMD58: %d" % LocalVariables['SendCMD58'])

        LocalVariables['SetPower'] = 1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SetPower: %d" % LocalVariables['SetPower'])

        LocalVariables['HcsXpcS18r000'] = (((GlobalOCRArgValue & 0xBFFFFFFF) & 0xEFFFFFFF) & 0xFEFFFFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HcsXpcS18r000: %d" % LocalVariables['HcsXpcS18r000'])

        LocalVariables['HcsXpcS18r001'] = (((GlobalOCRArgValue & 0xBFFFFFFF) & 0xEFFFFFFF) | 0x1000000)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HcsXpcS18r001: %d" % LocalVariables['HcsXpcS18r001'])

        LocalVariables['HcsXpcS18r010'] = (((GlobalOCRArgValue & 0xBFFFFFFF) | 0x10000000) & 0xFEFFFFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HcsXpcS18r010: %d" % LocalVariables['HcsXpcS18r010'])

        LocalVariables['HcsXpcS18r011'] = (((GlobalOCRArgValue & 0xBFFFFFFF) | 0x10000000) | 0x1000000)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HcsXpcS18r011: %d" % LocalVariables['HcsXpcS18r011'])

        LocalVariables['HcsXpcS18r100'] = (((GlobalOCRArgValue | 0x40000000) & 0xEFFFFFFF) & 0xFEFFFFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HcsXpcS18r100: %d" % LocalVariables['HcsXpcS18r100'])

        LocalVariables['HcsXpcS18r101'] = (((GlobalOCRArgValue | 0x40000000) & 0xEFFFFFFF) | 0x1000000)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HcsXpcS18r101: %d" % LocalVariables['HcsXpcS18r101'])

        LocalVariables['HcsXpcS18r110'] = (((GlobalOCRArgValue| 0x40000000) | 0x10000000) & 0xFEFFFFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HcsXpcS18r110: %d" % LocalVariables['HcsXpcS18r110'])

        LocalVariables['HcsXpcS18r111'] = (((GlobalOCRArgValue | 0x40000000) | 0x10000000) | 0x1000000)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HcsXpcS18r111: %d" % LocalVariables['HcsXpcS18r111'])

        LocalVariables['ReadyCcs18a000'] = (((GlobalOCRResValue & 0x7FFFFFFF) & 0xBFFFFFFF) & 0xFEFFFFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ReadyCcs18a000: %d" % LocalVariables['ReadyCcs18a000'])

        LocalVariables['ReadyCcs18a001'] = (((GlobalOCRResValue & 0x7FFFFFFF) & 0xBFFFFFFF) | 0x1000000)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ReadyCcs18a001: %d" % LocalVariables['ReadyCcs18a001'])

        LocalVariables['ReadyCcs18a010'] = (((GlobalOCRResValue & 0x7FFFFFFF) | 0x40000000) & 0xFEFFFFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ReadyCcs18a010: %d" % LocalVariables['ReadyCcs18a010'])

        LocalVariables['ReadyCcs18a011'] = (((GlobalOCRResValue & 0x7FFFFFFF) | 0x40000000) | 0x1000000)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ReadyCcs18a011: %d" % LocalVariables['ReadyCcs18a011'])

        LocalVariables['ReadyCcs18a100'] = (((GlobalOCRResValue | 0x80000000) & 0xBFFFFFFF) & 0xFEFFFFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ReadyCcs18a100: %d" % LocalVariables['ReadyCcs18a100'])

        LocalVariables['ReadyCcs18a101'] = (((GlobalOCRResValue | 0x80000000) & 0xBFFFFFFF) | 0x1000000)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ReadyCcs18a101: %d" % LocalVariables['ReadyCcs18a101'])

        LocalVariables['ReadyCcs18a110'] = (((GlobalOCRResValue | 0x80000000) | 0x40000000) & 0xFEFFFFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ReadyCcs18a110: %d" % LocalVariables['ReadyCcs18a110'])

        LocalVariables['ReadyCcs18a111'] = (((GlobalOCRResValue | 0x80000000) | 0x40000000) | 0x1000000)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ReadyCcs18a111: %d" % LocalVariables['ReadyCcs18a111'])

        if ret:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Exit from LoadLocalVariables Routine.\n")
            return LocalVariables
        return 0
    # Testcase Utility Logic - Ends
# Testcase Utility Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_ACMD41_UT07_Load_LocalVariables(self):
        obj = ACMD41_UT07_Load_LocalVariables(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
