"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : ACMD41_UT09_ResetSingleCommand.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : ACMD41_UT09_ResetSingleCommand.py
# DESCRIPTION                    : The purpose of this test is to assure reset single command.
# PRERQUISTE                     : ACMD41_TC005_HSC_XPC_S18A_AllScenarios.py
# STANDALONE EXECUTION           : No. It is an utility script.
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 30-May-2024
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
import ACMD41_TC005_HSC_XPC_S18A_AllScenarios as HSC_XPC_S18A_AllScenarios

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
class ACMD41_UT09_ResetSingleCommand(customize_log):
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
        self.allcard_loop = HSC_XPC_S18A_AllScenarios.ACMD41_TC005_HSC_XPC_S18A_AllScenarios(self.vtfContainer)


    # Testcase logic - Starts
    def Run(self, localVariables):
        """
        Name : Run
        """

        ProtocolMode = localVariables['ProtocolMode']
        SendCMD0 = localVariables['SendCMD0']
        SendCMD8 = localVariables['SendCMD8']

        # Step 1: call block SetMode
        self.SetMode(ProtocolMode)

        # Get globalResetFreq from config
        globalResetFreq = int(self.__config.get('globalResetFreq'))

        # Step 2: Set Frequency globalResetFreq
        self.__sdCmdObj.SetFrequency(globalResetFreq)

        # Step 3: Call script ACMD41Loops_AllCards_AllModes_HSC_XPC_S18A_AllScenarios
        self.allcard_loop.Run()

        # Step 4: checking condition SendCMD0 == 1
        if(SendCMD0 == 1):
            # Step 5: 1: CMD 0 - Issue Command
            self.__sdCmdObj.Cmd0()

        # Step 6: Checking condition SendCMD8 == 1
        if(SendCMD8 == 1):
            # Step 7: 1: CMD 8 - Issue command with argument = 0x1AA
            self.__sdCmdObj.Cmd8(arg = 0x1AA)

        # Step 8: 2 : Issue command cmd55
        self.__sdCmdObj.Cmd55(True)

        SendFirstOCR = localVariables['SendFirstOCR']

        # Step 9: 3 : Issue command ACMD41 = SendFirstOCR
        self.__sdCmdObj.ACmd41(argVal = SendFirstOCR)

        # Get globalLSHostFreq from config
        globalLSHostFreq = int(self.__config.get('globalLSHostFreq'))

        # Step 10: 4 : Set Frequency globalLSHostFreq
        self.__sdCmdObj.SetFrequency(globalLSHostFreq)

        # Step 11: 5 : call block SetMode
        self.SetMode(ProtocolMode)

        return 0

    def SetMode(self, ProtocolMode):

        # Step 12: Checking condition ((ProtocolMode == 1) | (ProtocolMode == 2))
        if((ProtocolMode == 1) or (ProtocolMode == 2)):

            # Step 13: 1: Set SD MMC MODE, in SD = 2
            self.__dvtLib.SetSdMmcCardMode(CardMode = sdcmdWrap.CARD_MODE.Sd, SetMode = True)

            # Step 14: 2: Set card hi cap #ignore this
            self.__dvtLib.SetCardCap(hiCap = True)

        # Step 15: Checking condition ((ProtocolMode == 3) | (ProtocolMode == 4))
        if((ProtocolMode == 3) or (ProtocolMode == 4)):

            # Step 16: 1 : HW Reset, performing host reset
            self.__dvtLib.HWReset(HostReset=True)

            # Step 17: 1: Set SD MMC MODE, in SD in SPI = 3
            self.__dvtLib.SetSdMmcCardMode(CardMode = sdcmdWrap.CARD_MODE.SD_IN_SPI, SetMode = True)

            # Step 18: 3: Set SPI mode , set cardMode = True for SPI mode.
            self.__dvtLib.SetCardMode(CardMode = True)

            # Step 19: 4: Set card hi cap # ignore this
            self.__dvtLib.SetCardCap(hiCap = True)

        return 0
    # Testcase Utility Logic - Ends
# Testcase Utility Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_ACMD41_UT09_ResetSingleCommand(self):
        obj = ACMD41_UT09_ResetSingleCommand(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends