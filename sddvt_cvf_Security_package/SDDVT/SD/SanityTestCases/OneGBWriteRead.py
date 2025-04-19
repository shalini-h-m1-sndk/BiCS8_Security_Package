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
# CVF SCRIPT                     : OneGBWriteRead.py
# DESCRIPTION                    : To check one GB write and read for testing purpose.
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=OneGBWriteRead --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Arockiaraj JAI
# REVIEWED BY                    :
# DATE                           : 23-Dec-2022
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
class OneGBWriteRead(TestCase.TestCase, customize_log):
    """
    TestName:
        OneGBWriteRead
    Purpose:
        Test to check one GB write and read for sanity purpose.
    Setup:
        1. Initialize card
    TestFlow:
        1. One GB write using pattern generation API
        2. One GB read using pattern generation API
    Expected:
        One GB write and read with given data pattern should be completed
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


    # Testcase logic - Starts
    def LegacyWrite(self, StartBlockAddr, NumBlocks, Pattern):

        try:
            self.__sdCmdObj.Cmd25WithPatternCompare(StartBlockAddr, NumBlocks, Pattern)
            # writeDataBuffer = ServiceWrap.Buffer.CreateBuffer(NumBlocks, 0x0)
            # writeDataBuffer = self.__sdCmdObj.BufferFilling(writeDataBuffer, Pattern = Pattern)
            # self.__sdCmdObj.Cmd25(startLbaAddress = StartBlockAddr, transferLen = NumBlocks, writeDataBuffer = writeDataBuffer)
        except ValidationError.CVFGenericExceptions as exc:
            raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_DATA_WRITTERN)

    def LegacyRead(self, StartBlockAddr, NumBlocks, Pattern):

        try:
            self.__sdCmdObj.Cmd18WithPatternCompare(StartBlockAddr, NumBlocks, Pattern)
            # ReadDataBuffer = ServiceWrap.Buffer.CreateBuffer(NumBlocks)
            # ReadDataBuffer = self.__sdCmdObj.BufferFilling(ReadDataBuffer, Pattern=Pattern)
            # self.__sdCmdObj.Cmd18(startLbaAddress = StartBlockAddr, transferLen = NumBlocks, readDataBuffer = ReadDataBuffer)
        except ValidationError.CVFGenericExceptions as exc:
            raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Data read successfully")


    def Run(self):
        """
        Name : Run
        """

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Calling LegacyWrite")
        self.LegacyWrite(0x0, 0x200000, 5)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Calling LegacyRead")
        self.LegacyRead(0x0, 0x200000, 5)

    # Testcase logic - Ends

    # CVF Hook Function: [Testcase Should start with "test_"]
    def test_OneGBWriteRead(self):  # [Same in xml tag: <Test name="test_OneGBWriteRead">]
        # Initialize the SD card
        self.__sdCmdObj.DoBasicInit()

        # Calling Testcase logic
        self.Run()

# Testcase Class - Ends