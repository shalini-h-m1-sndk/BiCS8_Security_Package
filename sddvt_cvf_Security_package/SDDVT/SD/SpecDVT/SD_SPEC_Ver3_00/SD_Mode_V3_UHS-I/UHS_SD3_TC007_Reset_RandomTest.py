"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : UHS_SD3_TC007_Reset_RandomTest.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : UHS_SD3_TC007_Reset_RandomTest.py
# DESCRIPTION                    : The purpose of this test UHS reset random test.
# PRERQUISTE                     : UHS_SD3_UT01_LoadLocal_Variables.py, UHS_SD3_UT02_Reset.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=UHS_SD3_TC007_Reset_RandomTest --isModel=false --enable_console_log=1 --adapter=0
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
    from builtins import range
    from builtins import *

# SDDVT - Dependent TestCases
import UHS_SD3_UT01_LoadLocal_Variables as LocalVariables
import UHS_SD3_UT02_Reset as ResetUtil

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
import SDDVT.Config_SD.ConfigSD_UT005_GlobalPreTestingSettings as globalPreTestingSettings

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
import time
from inspect import currentframe, getframeinfo

# Global Variables


# Testcase Class - Begins
class UHS_SD3_TC007_Reset_RandomTest(customize_log):
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
        self.__globalPreTestSettingsObj = globalPreTestingSettings.globalPreTestingSettings(self.vtfContainer)
        self.__LoadLocal_Variables = LocalVariables.UHS_SD3_UT01_LoadLocal_Variables(self.vtfContainer)
        self.__UtilityReset = ResetUtil.UHS_SD3_UT02_Reset(self.vtfContainer)


    # Testcase logic - Starts
    def RANDOM_UHS_RESET(self, LocalVariables):

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Block: RANDOM_UHS_RESET", self.__fp)

        RANDOM_BLOCK_1 = random.randrange(0, 3) # Random UHS Reset

        if RANDOM_BLOCK_1 == 0: # UHS ->Power Cycle

            LocalVariables['SetPower'] = 1
            LocalVariables['SendCMD0'] = 0
            xxx = 0

            self.RANDOM_RESET_TYPE(LocalVariables)

        if RANDOM_BLOCK_1 == 1: # UHS ->Power Cycle -> CMD0

            LocalVariables['SetPower'] = 1
            LocalVariables['SendCMD0'] = 1
            xxx = 1

            self.RANDOM_RESET_TYPE(LocalVariables)

        if RANDOM_BLOCK_1 == 2: # UHS -> CMD0

            LocalVariables['SetPower'] = 0
            LocalVariables['SendCMD0'] = 1
            xxx = 2

            self.S18R0_RAND_XPC(LocalVariables)

        yyy = xxx

    def RANDOM_LEGACY_RESET(self, LocalVariables):

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Block: RANDOM_LEGACY_RESET", self.__fp)

        RANDOM_BLOCK_2 = random.randrange(0, 3) # Random Legacy Reset

        if RANDOM_BLOCK_2 == 0: # Legacy -> Power Cycle

            LocalVariables['SetPower'] = 1
            LocalVariables['SendCMD0'] = 0
            xxx = 3

            self.RANDOM_RESET_TYPE(LocalVariables)

        if RANDOM_BLOCK_2 == 1: # Legacy -> Power Cycle -> CMD0

            LocalVariables['SetPower'] = 1
            LocalVariables['SendCMD0'] = 1
            xxx = 4

            self.RANDOM_RESET_TYPE(LocalVariables)

        if RANDOM_BLOCK_2 == 2: # Legacy -> CMD0

            LocalVariables['SetPower'] = 0
            LocalVariables['SendCMD0'] = 1
            xxx = 5

            self.COMPLETE_LEGACY_RESET(LocalVariables)

        yyy = xxx

    def RANDOM_RESET_TYPE(self, LocalVariables):

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Block: RANDOM_RESET_TYPE", self.__fp)

        RANDOM_BLOCK_3 = random.randrange(0, 2)

        if RANDOM_BLOCK_3 == 0: # UHS RESET
            self.S18R1_RAND_XPC(LocalVariables)

        if RANDOM_BLOCK_3 == 1: # LEGACY RESET
            self.COMPLETE_LEGACY_RESET(LocalVariables)

    def COMPLETE_UHS_RESET(self, LocalVariables):

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Block: COMPLETE_UHS_RESET", self.__fp)

        LocalVariables['SendACMD6'] = 1

        RANDOM_BLOCK_M = random.randrange(0, 2)

        if RANDOM_BLOCK_M == 0:
            # Call Utility_Reset
            self.__UtilityReset.Run(LocalVariables)

        if RANDOM_BLOCK_M == 1: # Error Cases
            RANDOM_BLOCK_4 = random.randrange(0, 2)

            if RANDOM_BLOCK_4 == 0:
                # Reset card
                self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=LocalVariables['SendOCR'], cardSlot=0x1,
                                    sendCmd8=LocalVariables['SendCMD8'], initInfo=None, rca=0x0, time=0x0,
                                    sendCMD0=LocalVariables['SendCMD0'], bHighCapacity=False, bSendCMD58=False,
                                    version=0x0, VOLA=0x1, cmdPattern=0xAA, reserved=0x0, expOCRVal=LocalVariables['ExpectOCR'])

                if (LocalVariables['ExpectOCR'] & 0x1000000) == 0x1000000:
                    # SwitchVolt_CMD11 to 1.8V
                    self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)
                else:
                    # SwitchVolt_CMD11 to 1.8V
                    try:
                        self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)
                    except ValidationError.CVFGenericExceptions as exc:
                        self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "SwitchVolt_CMD11")
                    else:
                        raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING error not occurred")

            if RANDOM_BLOCK_4 == 1:

                self.FailScenarious(LocalVariables)

                # Reset card
                try:
                    self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=LocalVariables['SendOCR'], cardSlot=0x1, sendCmd8=LocalVariables['SendCMD8'],
                                    initInfo=None, rca=0x0, time=0x0, sendCMD0=LocalVariables['SendCMD0'], bHighCapacity=False, bSendCMD58=False, version=0x0,
                                    VOLA=0x1, cmdPattern=0xAA, reserved=0x0, expOCRVal=LocalVariables['ExpectOCR'])
                except ValidationError.CVFGenericExceptions as exc:
                    self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_READY", "SwitchVolt_CMD11")
                else:
                    raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_READY error not occurred")

    def COMPLETE_LEGACY_RESET(self, LocalVariables):

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Block: COMPLETE_LEGACY_RESET", self.__fp)

        LocalVariables['UHS'] = 0   # Legacy
        LocalVariables['SEND_CMD11'] = 0    # Don't Send CMD 11
        RANDOM_BLOCK_5 = random.randrange(0, 2) # HSC=1 XPC=X S18R=0

        if RANDOM_BLOCK_5 == 0:

            LocalVariables['SendOCR'] = LocalVariables['HcsXpcS18r110'] # HSC=1 XPC=1 S18R=0
            LocalVariables['ExpectOCR'] = LocalVariables['ReadyCcs18a110']  # Ready Bit = 1 HSC=1 S18R=0

        if RANDOM_BLOCK_5 == 1:
            LocalVariables['SendOCR'] = LocalVariables['HcsXpcS18r110'] # HSC=1 XPC=0 S18R=0
            LocalVariables['ExpectOCR'] = LocalVariables['ReadyCcs18a110']  # Ready Bit = 1 HSC=1 S18R=0

        RANDOM_BLOCK_6 = random.randrange(0, 2)
        if RANDOM_BLOCK_6 == 0:
            LocalVariables['SendACMD6'] = 0
        if RANDOM_BLOCK_6 == 1:
            LocalVariables['SendACMD6'] = 1

        RANDOM_BLOCK_7 = random.randrange(0, 2)
        if RANDOM_BLOCK_7 == 0:
            LocalVariables['Turn_HS_ON'] = 0
        if RANDOM_BLOCK_7 == 1:
            LocalVariables['Turn_HS_ON'] = 1

        # Call Utility_Reset
        self.__UtilityReset.Run(LocalVariables)


    def S18R1_RAND_XPC(self, LocalVariables):

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Block: S18R1_RAND_XPC", self.__fp)

        RANDOM_BLOCK_8 = random.randrange(0, 2) # HSC=1 XPC=X S18R=1

        if RANDOM_BLOCK_8 == 0:
            LocalVariables['SendOCR'] = LocalVariables['HcsXpcS18r111']
            LocalVariables['ExpectOCR'] = LocalVariables['ReadyCcs18a111']

        if RANDOM_BLOCK_8 == 1:
            LocalVariables['SendOCR'] = LocalVariables['HcsXpcS18r111']
            LocalVariables['ExpectOCR'] = LocalVariables['ReadyCcs18a111']

        RANDOM_BLOCK_9 = random.randrange(0, 2)

        if RANDOM_BLOCK_9  == 0:
            LocalVariables['SEND_CMD11'] = 1
            self.RANDOM_UHS_RESET(LocalVariables)

        if RANDOM_BLOCK_9 == 1:
            LocalVariables['SEND_CMD11'] = 0
            self.COMPLETE_LEGACY_RESET(LocalVariables)


    def S18R0_RAND_XPC(self, LocalVariables):

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Block: S18R0_RAND_XPC", self.__fp)

        RANDOM_BLOCK_10 = random.randrange(0, 2)

        if RANDOM_BLOCK_10 == 0:
            LocalVariables['SendOCR'] = LocalVariables['HcsXpcS18r110'] # HSC=1 XPC=1 S18R=0
            LocalVariables['ExpectOCR'] = LocalVariables['ReadyCcs18a110']  # Ready Bit = 1 HSC=1 S18R=0
            LocalVariables['SEND_CMD11'] = 0

            self.COMPLETE_UHS_RESET(LocalVariables)

        if RANDOM_BLOCK_10 == 1:
            LocalVariables['SendOCR'] = LocalVariables['HcsXpcS18r110'] # HSC=1 XPC=0 S18R=0
            LocalVariables['ExpectOCR'] = LocalVariables['ReadyCcs18a110']  # Ready Bit = 1 HSC=1 S18R=0
            LocalVariables['SEND_CMD11'] = 0    # Don't Send CMD 11

            self.COMPLETE_UHS_RESET(LocalVariables)

        if RANDOM_BLOCK_10 == 2:
            LocalVariables['SendOCR'] = LocalVariables['HcsXpcS18r111'] # HSC=1 XPC=1 S18R=1
            LocalVariables['ExpectOCR'] = LocalVariables['ReadyCcs18a111']  # Ready Bit = 1 HSC=1 S18R=1
            LocalVariables['SEND_CMD11'] = 0    # Don't Send CMD 11

            self.COMPLETE_UHS_RESET(LocalVariables)

        if RANDOM_BLOCK_10 == 3:

            LocalVariables['SendOCR'] = LocalVariables['HcsXpcS18r111'] # HSC=1 XPC=0 S18R=1
            LocalVariables['ExpectOCR'] = LocalVariables['ReadyCcs18a111']  # Ready Bit = 1 HSC=1 S18R=1
            LocalVariables['SEND_CMD11'] = 0    # Don't Send CMD 11

            self.COMPLETE_UHS_RESET(LocalVariables)


    def FailScenarious(self, LocalVariables):

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Block: FailScenarious", self.__fp)

        RANDOM_BLOCK_11 = random.randrange(0, 4)

        if RANDOM_BLOCK_11 == 0:
            LocalVariables['SendOCR'] = LocalVariables['HcsXpcS18r000'] # HCS = 0  XPC = 0 S18R = 0

        if RANDOM_BLOCK_11 == 1:
            LocalVariables['SendOCR'] = LocalVariables['HcsXpcS18r001'] # HCS = 0  XPC = 0 S18R = 1

        if RANDOM_BLOCK_11 == 2:
            LocalVariables['SendOCR'] = LocalVariables['HcsXpcS18r010'] # HCS = 0  XPC = 1 S18R = 0

        if RANDOM_BLOCK_11 == 3:
            LocalVariables['SendOCR'] = LocalVariables['HcsXpcS18r011'] # HCS = 0  XPC = 1 S18R = 1

    def Run(self):
        """
        Name : Run
        """

        # Global values from globalPreTestingSettings file
        self.__globalPreTestSettingsObj.Run()

        # Call Utility_LoadLocal_Variables
        LocalVariables = self.__LoadLocal_Variables.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PREREQUISITES")

        # Variable declaration
        LocalVariables['ProtocolMode'] = 1
        LocalVariables['UHS'] = 1
        LocalVariables['SEND_CMD11'] = 1
        LocalVariables['VerifyType'] = 1
        LocalVariables['SetPower'] = 1
        LocalVariables['SendCMD0'] = 1
        LocalVariables['SendCMD8'] = 1
        LocalVariables['SendOCR'] = LocalVariables['HcsXpcS18r111']
        LocalVariables['ExpectOCR'] = LocalVariables['ReadyCcs18a111']

        # Call Utility_Reset
        self.__UtilityReset.Run(LocalVariables)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "START RANDOM TEST")

        LogFolder = self.vtfContainer.cfg_manager.currentConfiguration.system.Logger.get_logFolder()
        LoopFlowLogFile = "%s\\LoopFlowLog_%s.txt" % (LogFolder, self.fn)
        self.__fp = open(LoopFlowLogFile, "w")

        for loop in range(0, 500):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Loop count is 500. Current iteration is %s\n" % (loop + 1), self.__fp)

            if LocalVariables['UHS'] == 0:
                self.RANDOM_LEGACY_RESET(LocalVariables)

            if LocalVariables['UHS'] == 1:
                self.RANDOM_UHS_RESET(LocalVariables)

        self.__fp.close()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "END OF SCRIPT")
        return 0

    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_UHS_SD3_TC007_Reset_RandomTest(self):
        obj = UHS_SD3_TC007_Reset_RandomTest(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
