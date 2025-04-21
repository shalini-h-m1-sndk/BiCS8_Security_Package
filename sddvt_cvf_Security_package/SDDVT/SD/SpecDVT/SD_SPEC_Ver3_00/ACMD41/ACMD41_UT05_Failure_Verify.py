"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : Utility_Failure_Verify.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : ACMD41_UT05_Failure_Verify.py
# DESCRIPTION                    :
# PRERQUISTE                     :
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=ACMD41_UT05_Failure_Verify --isModel=false --enable_console_log=1 --adapter=0
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
class ACMD41_UT05_Failure_Verify(customize_log):
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


    # Testcase logic - Starts

    def Run(self, localVariables):
        """
        Name : Run
        """
        globalOCRArgValue = int(self.__config.get('globalOCRArgValue'))
        globalOCRResValue = int(self.__config.get('globalOCRResValue'))

        ProtocolMode = localVariables['ProtocolMode']

        #Check condition ProtocolMode == 4
        if ProtocolMode == 4 :

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "OCR : %d"% int(self.__config.get('globalOCRArgValue')))
            #  Reset card, SD in SPI mode
            self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.SD_IN_SPI, ocr = 0, cardSlot=0x1,
                            sendCmd8=True, initInfo=None, rca=0x0, time = 0x0, sendCMD0 = 0x1, bHighCapacity=True,
                            bSendCMD58=True,version=0x0, VOLA=0x1, cmdPattern=0xAA, reserved=0x0, expOCRVal=globalOCRResValue)

        # Check condition ProtocolMode == 2
        if ProtocolMode == 2 :

            # Reset card, SD mode.
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "OCR : %d"% int(self.__config.get('globalOCRArgValue')))
            Expected_OCR = self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.Sd, ocr = globalOCRArgValue, cardSlot=0x1,
                                sendCmd8=True, initInfo=None, rca=0x0, time = 0x0, sendCMD0 = 0x1, bHighCapacity=False,
                                bSendCMD58=True, version=0x0, VOLA=0x1, cmdPattern=0xAA, reserved=0x0, expOCRVal=globalOCRResValue)

        return 0


    #End of Run function
#End of FailureVerify

class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    def test_ACMD41_UT05_Failure_Verify(self):  # [Same in xml tag: <Test name="test_ACMD41_UT05_Failure_Verify">]
        obj=ACMD41_UT05_Failure_Verify(self.vtfContainer)
        obj.Run()

# Testcase Class - Ends