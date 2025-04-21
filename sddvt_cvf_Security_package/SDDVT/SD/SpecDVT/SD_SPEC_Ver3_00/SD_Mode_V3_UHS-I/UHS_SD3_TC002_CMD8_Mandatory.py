"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : UHS_SD3_TC002_CMD8_Mandatory.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : UHS_SD3_TC002_CMD8_Mandatory.py
# DESCRIPTION                    : Reset Utility
# PRERQUISTE                     : UHS_SD3_UT01_LoadLocal_Variables.py, UHS_SD3_UT02_Reset.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=UHS_SD3_TC002_CMD8_Mandatory --isModel=false --enable_console_log=1 --adapter=0
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
import UHS_SD3_UT01_LoadLocal_Variables as LoadLocalVariables
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
class UHS_SD3_TC002_CMD8_Mandatory(customize_log):
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
        self.__LoadLocal_Variables = LoadLocalVariables.UHS_SD3_UT01_LoadLocal_Variables(self.vtfContainer)
        self.__UtilityReset = ResetUtil.UHS_SD3_UT02_Reset(self.vtfContainer)


    # Testcase logic - Starts
    def NoCMD8(self, LocalVariables):

        LocalVariables['SendOCR'] = LocalVariables['HcsXpcS18r000'] # HCS = 0, XPC = 0, S18R = 0
        self.__UtilityReset.Run(LocalVariables)

        LocalVariables['SendOCR'] = LocalVariables["HcsXpcS18r001"] # HCS = 0, XPC = 0, S18R = 1
        self.__UtilityReset.Run(LocalVariables)

        LocalVariables['SendOCR'] = LocalVariables["HcsXpcS18r010"] # HCS = 0, XPC = 1, S18R = 0
        self.__UtilityReset.Run(LocalVariables)

        LocalVariables['SendOCR'] = LocalVariables["HcsXpcS18r011"] # HCS = 0, XPC = 1, S18R = 1
        self.__UtilityReset.Run(LocalVariables)

        LocalVariables['SendOCR'] = LocalVariables["HcsXpcS18r100"] # HCS = 1, XPC = 0, S18R = 0
        self.__UtilityReset.Run(LocalVariables)

        LocalVariables['SendOCR'] = LocalVariables["HcsXpcS18r101"] # HCS = 1, XPC = 0, S18R = 1
        self.__UtilityReset.Run(LocalVariables)

        LocalVariables['SendOCR'] = LocalVariables["HcsXpcS18r110"] # HCS = 1, XPC = 1, S18R = 0
        self.__UtilityReset.Run(LocalVariables)

        LocalVariables['SendOCR'] = LocalVariables["HcsXpcS18r111"] # HCS = 1, XPC = 1, S18R = 1
        return 0

    def Run(self):

        # Initialize the SD card
        self.__sdCmdObj.DoBasicInit()

        # Call Utility_LoadLocal_Variables
        LocalVariables = self.__LoadLocal_Variables.Run()

        # Set Loop for 20 times
        for Loop in range(0, 20):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Loop count is 20. Current iteration is %s" % (Loop + 1))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "3.4.1.1.4 Without CMD8 Card returns busy\nStart Reset\nSend ACMD41\nRepeat (Main Flow) make sure card not dead\nVerify\nRepeat the test with all combinations of HSC & XPC & S18R\nRepeat the test with all reset types")

            #Variables declaration
            LocalVariables['ProtocolMode'] = 2  # 2=SD Error
            LocalVariables['VerifyType'] = 2
            LocalVariables['SendOCR'] = LocalVariables["HcsXpcS18r000"]
            LocalVariables['ExpectOCR'] = LocalVariables["ReadyCcs18a000"]
            LocalVariables['SetPower'] = 1
            LocalVariables['SendCMD0'] = 1
            LocalVariables['SendCMD8'] = 0
            self.NoCMD8(LocalVariables) # (Without CMD8) Power On ->CMD0-> ACMD41->Card Is Busy
            LocalVariables['SendCMD0'] = 0
            self.NoCMD8(LocalVariables) # (Without CMD8) Power On -> ACMD41->Card Is Busy
            LocalVariables['SetPower'] = 0
            LocalVariables['SendCMD0'] = 1
            self.NoCMD8(LocalVariables) # (Without CMD8) CMD0-> ACMD41->Card Is Busy
        return 0

    #-----------------------------------End of Script-----------------------------------#
    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_UHS_SD3_TC002_CMD8_Mandatory(self):
        obj = UHS_SD3_TC002_CMD8_Mandatory(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
