"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : None
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : OneGBWriteRead_by_Single_Block_Cmd.py
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : OneGBWriteRead_by_Single_Block_Cmd.py
# DESCRIPTION                    : To execute one GB write and read by legacy write/read command
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=OneGBWriteRead_by_Single_Block_Cmd --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 11-Jan-2023
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
import time
import os
import sys
from inspect import currentframe, getframeinfo

# Global Variables


# Testcase Class - Begins
class OneGBWriteRead_by_Single_Block_Cmd(TestCase.TestCase, customize_log):
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
        self.EndBlockAddr = self.__sdCmdObj.calculate_endLba(self.StartBlockAddr, self.NumBlocks)
        self.writeDataBuffer = ServiceWrap.Buffer.CreateBuffer(1, 0x0)
        self.ReadDataBuffer = ServiceWrap.Buffer.CreateBuffer(1, 0x0)
        self.writeDataBuffer = self.__sdCmdObj.BufferFilling(self.writeDataBuffer, Pattern = gvar.GlobalConstants.PATTERN_ALL_ONE)


    # Testcase logic - Starts

    def LegacyWrite(self):
        """
        Function to write one GB of data
        """

        StartTime = time.time()

        for StartLBA, BlockCount in self.__sdCmdObj.Data_Trans_Breakup(self.StartBlockAddr, self.EndBlockAddr, maxTransfer = 1):
            try:
                self.__sdCmdObj.Cmd24(startLbaAddress = StartLBA, writeDataBuffer = self.writeDataBuffer)
            except ValidationError.CVFGenericExceptions as exc:
                raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

        EndTime = time.time()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "One GB legacy write is done in %s seconds" % (EndTime - StartTime))


    def LegacyRead(self):
        """
        Function to read one GB of data
        """

        StartTime = time.time()

        for StartLBA, BlockCount in self.__sdCmdObj.Data_Trans_Breakup(self.StartBlockAddr, self.EndBlockAddr, maxTransfer = 1):
            self.ReadDataBuffer.Fill(0x00)
            try:
                self.__sdCmdObj.Cmd17(startLbaAddress = StartLBA, readDataBuffer = self.ReadDataBuffer)
                self.__sdCmdObj.Compare(readBuffer = self.ReadDataBuffer, writeBuffer = self.writeDataBuffer)
            except ValidationError.CVFGenericExceptions as exc:
                raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

        EndTime = time.time()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "One GB legacy read is done in %s seconds" % (EndTime - StartTime))


    def Run(self):
        """
        Name : Run
        """

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Calling LegacySingleWrite")
        self.LegacyWrite()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Calling LegacySingleRead")
        self.LegacyRead()

    # Testcase logic - Ends


    # CVF Hook Function: [Testcase Should start with "test_"]
    def test_OneGBWriteRead_by_Single_Block_Cmd(self):  # [Same in xml tag: <Test name="test_OneGBWriteRead_by_Single_Block_Cmd">]
        # Initialize the SD card
        self.__sdCmdObj.DoBasicInit()

        # Calling Testcase logic
        self.Run()

# Testcase Class - Ends