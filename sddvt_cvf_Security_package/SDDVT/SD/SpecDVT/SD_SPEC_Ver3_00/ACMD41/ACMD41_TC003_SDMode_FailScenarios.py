"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : ACMD41_TC003_SDMode_FailScenarios.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : ACMD41_TC003_SDMode_FailScenarios.py
# DESCRIPTION                    : The purpose of this test is to assure SD Mode FailScenarios
# PRERQUISTE                     : ACMD41_UT07_Load_LocalVariables.py, ACMD41_UT08_Reset.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=ACMD41_TC003_SDMode_FailScenarios --isModel=false --enable_console_log=1 --adapter=0
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
import ACMD41_UT07_Load_LocalVariables as LoadLocalVariables
import ACMD41_UT08_Reset as UtilityReset

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


# Testcase Class - Begins
class ACMD41_TC003_SDMode_FailScenarios(customize_log):
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
        self.__LoadLocal_Variables = LoadLocalVariables.ACMD41_UT07_Load_LocalVariables(self.vtfContainer)
        self.__ResetUtil = UtilityReset.ACMD41_UT08_Reset(self.vtfContainer)


    # Testcase Logic - Starts
    def FailureScenarious(self, globalProjectConfVar, localVariables):
        localVariables['SendOCR'] = localVariables['HcsXpcS18r000']

        # Call script reset utility
        self.__ResetUtil.Run(globalProjectConfVar, localVariables)

        localVariables['SendOCR'] = localVariables['HcsXpcS18r001']

        # Call script reset utility
        self.__ResetUtil.Run(globalProjectConfVar, localVariables)

        localVariables['SendOCR'] = localVariables['HcsXpcS18r010']

        # Call script reset utility
        self.__ResetUtil.Run(globalProjectConfVar, localVariables)

        localVariables['SendOCR'] = localVariables['HcsXpcS18r011']

        return 0

    def NoCMD8(self, globalProjectConfVar, localVariables):
        localVariables['SendOCR'] = localVariables['HcsXpcS18r000']

        # Call script reset utility
        self.__ResetUtil.Run(globalProjectConfVar, localVariables)

        localVariables['SendOCR'] = localVariables['HcsXpcS18r001']

        # Call script reset utility
        self.__ResetUtil.Run(globalProjectConfVar, localVariables)

        localVariables['SendOCR'] = localVariables['HcsXpcS18r010']

        # Call script reset utility
        self.__ResetUtil.Run(globalProjectConfVar, localVariables)

        localVariables['SendOCR'] = localVariables['HcsXpcS18r011']

        # Call script reset utility
        self.__ResetUtil.Run(globalProjectConfVar, localVariables)

        localVariables['SendOCR'] = localVariables['HcsXpcS18r100']

        # Call script reset utility
        self.__ResetUtil.Run(globalProjectConfVar, localVariables)

        localVariables['SendOCR'] = localVariables['HcsXpcS18r101']

        # Call script reset utility
        self.__ResetUtil.Run(globalProjectConfVar, localVariables)

        localVariables['SendOCR'] = localVariables['HcsXpcS18r110']

        # Call script reset utility
        self.__ResetUtil.Run(globalProjectConfVar, localVariables)

        localVariables['SendOCR'] = localVariables['HcsXpcS18r111']
        return 0

    def Run(self):
        """
        Name : Run
        """
        globalProjectConfVar = self.__sdCmdObj.DoBasicInit()

        # Load Variables from the Script Utility_Load_LocalVariables
        localVariables = self.__LoadLocal_Variables.Run(ret = 1)

        # Variable declaration
        localVariables['ProtocolMode'] = 2
        localVariables['VerifyType'] = 2
        localVariables['SendOCR'] = localVariables['HcsXpcS18r000']
        localVariables['ExpectOCR'] = localVariables['ReadyCcs18a000']
        localVariables['SetPower'] = 1
        localVariables['SendCMD0'] = 1
        localVariables['SendCMD8'] = 1

        # Call block FailureScenarious
        self.FailureScenarious(globalProjectConfVar, localVariables)

        localVariables['SendCMD0'] = 0

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "3.1.1.9.2")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power On-> CMD8 -> ACMD41 -> Card Is Busy")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HSC=0 S18R=Y XPC=Z  Failure Scenario")

        # Call block FailureScenarious
        self.FailureScenarious(globalProjectConfVar, localVariables)

        localVariables['SetPower'] = 0
        localVariables['SendCMD0'] = 1

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "3.1.1.9.3")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD0 -> CMD8 -> ACMD41 -> Card Is Busy")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HSC=0 S18R=Y XPC=Z  Failure Scenario")

        # Call block FailureScenarious
        self.FailureScenarious( globalProjectConfVar, localVariables)

        localVariables['SetPower'] = 1
        localVariables['SendCMD8'] = 0

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "3.1.1.9.4")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power On ->CMD0-> ACMD41 -> Card Is Busy")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HSC=X S18R=Y XPC=Z  Failure Scenario")

        # Call block NoCMD8
        self.NoCMD8(globalProjectConfVar, localVariables)

        localVariables['SendCMD0'] = 0

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "3.1.1.9.5")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power On-> ACMD41 -> Card Is Busy")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HSC=X S18R=Y XPC=Z  Failure Scenario")

        # Call block NoCMD8
        self.NoCMD8(globalProjectConfVar, localVariables)

        localVariables['SetPower'] = 0
        localVariables['SendCMD0'] = 1

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "3.1.1.9.6")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD0-> ACMD41 -> Card Is Busy")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HSC=X S18R=Y XPC=Z  Failure Scenario")

        # Call block NoCMD8
        self.NoCMD8(globalProjectConfVar, localVariables)

        return 0
    # Testcase Logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_ACMD41_TC003_SDMode_FailScenarios(self):
        obj = ACMD41_TC003_SDMode_FailScenarios(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
