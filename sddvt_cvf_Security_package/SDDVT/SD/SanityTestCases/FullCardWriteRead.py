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
# CVF SCRIPT                     : FullCardWriteRead.py
# DESCRIPTION                    : To validate pattern gen API
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=FullCardWriteRead --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    :
# DATE                           : 08-Sep-2023
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
import PatternGen
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
class FullCardWriteRead(TestCase.TestCase, customize_log):
    """
    TestName:
        FullCardWriteRead

    Purpose: To validate pattern gen API

    Setup:
        1. Initialize card

    TestFlow:

    Expected:
    """

    # Act as a Constructor
    def setUp(self):
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
        self.patternGen = PatternGen.PatternGen(self.vtfContainer, writePattern = sdcmdWrap.Pattern.ALL_ZERO,
                                           doLatency = True, doIddMeasurment = True, doCompare = True, enable_logging = True)

    # Testcase logic - Starts
    def LegacyWrite(self):
        pattern = sdcmdWrap.Pattern.INCREMENTAL
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Pattern used for write is %s" % pattern)
        try:
            self.patternGen.SetPattern(pattern = pattern)
            self.patternGen.MultipleWrite(address = 0x0, blockCount = self.__cardMaxLba)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Data writtern successfully")

    def LegacyRead(self):
        pattern = sdcmdWrap.Pattern.ALL_ONE
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Pattern used for read is %s" % pattern)
        try:
            self.patternGen.SetPattern(pattern = pattern)
            self.patternGen.MultipleRead(address = 0x0, blockCount = self.__cardMaxLba)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            errstring = exc.GetFailureDescription()
            if errstring.find("CARD_COMPARE_ERROR") != -1:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card is reporting expected 'CARD_COMPARE_ERROR' for pattern gen read\n")
                self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure
            else:
                raise ValidationError.TestFailError(self.fn, "Expected error is 'CARD_COMPARE_ERROR' for pattern gen read. But error occured is - %s" % errorString)
        else:
            raise ValidationError.TestFailError(self.fn, "Expected 'CARD_COMPARE_ERROR' is not reported by card for pattern gen read")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Data read successfully")


    def Run(self):
        """
        Name : Run
        """

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Calling LegacyWrite")
        self.LegacyWrite()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Calling LegacyRead")
        self.LegacyRead()

    # Testcase logic - Ends

    # CVF Hook Function: [Testcase Should start with "test_"]
    def test_FullCardWriteRead(self):  # [Same in xml tag: <Test name="test_FullCardWriteRead">]
        # Initialize the SD card
        self.__sdCmdObj.DoBasicInit()

        # Calling Testcase logic
        self.Run()

# Testcase Class - Ends