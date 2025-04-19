"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : UHS_SD3_TC001_Reset_Main_Flow.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : UHS_SD3_TC001_Reset_Main_Flow.py
# DESCRIPTION                    : Reset Utility
# PRERQUISTE                     : UHS_SD3_UT01_LoadLocal_Variables.py, UHS_SD3_UT02_Reset.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=UHS_SD3_TC001_Reset_Main_Flow --isModel=false --enable_console_log=1 --adapter=0
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
class UHS_SD3_TC001_Reset_Main_Flow(customize_log):
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
    def Run(self):

        # Initialize the SD card
        self.__sdCmdObj.DoBasicInit()

        # Call Utility_LoadLocal_Variables
        LocalVariables = self.__LoadLocal_Variables.Run()

        # Set Loop for 50 Times
        for MainLoop in range(0, 50):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Main loop count is 50. Current iteration is %s" % (MainLoop + 1))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "3.4.1.1.1 Main Flow - UHS Card and Host\nStart Reset\nSend ACMD41\nCMD11\nComplete UHS Reset\nVerify\nRepeat the test with XPC-=1\nPerform soft reset and repeat the test")

            # Variable Declarations
            LocalVariables['SendOCR'] = LocalVariables['HcsXpcS18r111']

            LocalVariables['ExpectOCR'] =LocalVariables['ReadyCcs18a111']

            # Set ProtocolMode
            LocalVariables['ProtocolMode'] =1
            LocalVariables['UHS']=1
            LocalVariables['SEND_CMD11'] = 1
            LocalVariables['VerifyType'] = 3
            LocalVariables['SetPower'] =1
            LocalVariables['SendCMD0'] =1
            LocalVariables['SendCMD8'] =1

            for ResetOuterLoop in range(0, 2):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ResetOuterLoop count is 2. Current iteration is %s" % (ResetOuterLoop + 1))

                for ResetInnerLoop in range(0, 2):
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ResetInnerLoop count is 2. Current iteration is %s" % (ResetInnerLoop + 1))

                    # Utility_Reset
                    self.__UtilityReset.Run(LocalVariables)

                    LocalVariables['SendOCR'] = LocalVariables['HcsXpcS18r101']

                LocalVariables['SetPower'] =0
                LocalVariables['ExpectOCR'] =LocalVariables['ReadyCcs18a110']

                LocalVariables['SEND_CMD11']=0

            LocalVariables['ExpectOCR'] =LocalVariables['ReadyCcs18a111']

        return 0
    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_UHS_SD3_TC001_Reset_Main_Flow(self):
        obj = UHS_SD3_TC001_Reset_Main_Flow(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
