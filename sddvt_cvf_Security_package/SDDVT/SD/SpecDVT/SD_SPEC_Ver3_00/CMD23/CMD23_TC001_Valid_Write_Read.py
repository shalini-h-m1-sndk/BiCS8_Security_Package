"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                :
# CVF CALL ALL SCRIPT            : CMD23_CA01_SDMode.xml
# CVF SCRIPT                     : CMD23_TC001_Valid_Write_Read.py
# DESCRIPTION                    :
# PRERQUISTE                     : [CMD23_UT08_LoadCMD23_Variables, CMD23_UT09_LoadLocal_Variables, CMD23_UT06_CMD23Write, CMD23_UT10_Reset]
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=CMD23_TC001_Valid_Write_Read --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Sushmitha P.S
# REVIEWED BY                    : Sivagurunathan
# DATE                           : 28-Jun-2024
################################################################################
"""

# Python future modules for python3 forward compatibility
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    from builtins import *
from past.utils import old_div

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

# Dependent Utilities
import CMD23_UT08_LoadCMD23_Variables as LoadCMD23Variables
import CMD23_UT09_LoadLocal_Variables as LoadLocalVariables
import CMD23_UT06_CMD23Write as CMD23Write
import CMD23_UT10_Reset as UtilityReset

# Global Variables

# Testcase Class - Begins
class CMD23_TC001_Valid_Write_Read(TestCase.TestCase, customize_log):
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
        self.__LoadCMD23Variables = LoadCMD23Variables.CMD23_UT08_LoadCMD23_Variables(self.vtfContainer)
        self.__LoadLocal_Variables = LoadLocalVariables.CMD23_UT09_LoadLocal_Variables(self.vtfContainer)
        self.__Utility_CMD23Write = CMD23Write.CMD23_UT06_CMD23Write(self.vtfContainer)
        self.__ResetUtil = UtilityReset.CMD23_UT10_Reset(self.vtfContainer)

    # Testcase logic - Starts

    def Run(self, ret = 0):
        """
        Purpose: The purpose of this test case is to test the  valid  CMD23 write scenarios without stop transmition.
        """

        #Call Script globalInitCard
        globalProjectValues = self.__sdCmdObj.DoBasicInit()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Execution Started " + "-" * 20 + "\n")

        #CALL Utility_LoadCMD23_Variables script
        cmd23Variables = self.__LoadCMD23Variables.Run( ret = 1)

        #CALL Utility_LoadLocal_Variables script
        localVariables  = self.__LoadLocal_Variables.Run( globalProjectValues, ret = 1)

        # Empty Dictionary to retrieve values from Utility
        g_localVars = {}

        # Get values from Utility LoadLocal_Variables
        g_localVars["Identification"] = localVariables['Identification']
        g_localVars["ProtocolMode"] = localVariables['ProtocolMode']
        g_localVars["VerifyType"]   = localVariables['VerifyType']
        g_localVars["SetPower"]     = localVariables["SetPower"]
        g_localVars["SendCMD0"]     = localVariables["SendCMD0"]
        g_localVars["SendCMD8"]     = localVariables["SendCMD8"]

        g_localVars["CMD23StartBlock"] = cmd23Variables["CMD23StartBlock"]
        g_localVars["CMD23BlockCount"] = cmd23Variables["CMD23BlockCount"]
        g_localVars["CMD23DataType"]   = cmd23Variables ["CMD23DataType"]
        g_localVars["CMD23VerifyWriteFlag"]   = cmd23Variables ["CMD23VerifyWriteFlag"]
        g_localVars["PredefineNumBlkFlag"]   = cmd23Variables ["PredefineNumBlkFlag"]
        g_localVars["PredefinedNumOfBlkCnt"] = cmd23Variables['PredefinedNumOfBlkCnt']
        g_localVars["IgnorePredefinedBlockCnt"] =  cmd23Variables['IgnorePredefinedBlockCnt']

        # Initialize Variables
        g_localVars["CMD23DataType"] = 1
        g_localVars["CMD23StartBlock"] = 0
        g_localVars["MaxLba"] = self.__cardMaxLba
        g_localVars["CMD23BlockCount"] = g_localVars["MaxLba"]
        g_localVars["SetPower"]= 1
        g_localVars["SendCMD0"] = 1
        g_localVars["SendCMD8"] = 1

        #Call Utility_CMDlocalVariables23_Write
        blkCountCMD23 = self.__Utility_CMD23Write.Run(g_localVars["CMD23StartBlock"], g_localVars["CMD23BlockCount"],
                                                      g_localVars["PredefinedNumOfBlkCnt"], g_localVars["CMD23DataType"], usePreDefBlkCount =  True)
        g_localVars["blkCountCMD23"] = blkCountCMD23

        # Call Utility Reset
        self.__ResetUtil.Run(globalProjectValues, g_localVars["ProtocolMode"], g_localVars["Identification"],
                             g_localVars["VerifyType"], g_localVars["SetPower"], g_localVars["SendCMD8"], g_localVars["SendCMD0"] )

        # Do Multiple Read from CMD23StartBlock to CMD23BlockCount
        self.__dvtLib.ReadWithFPGAPattern(g_localVars["CMD23StartBlock"], g_localVars["blkCountCMD23"], pattern= g_localVars["CMD23DataType"],usePreDefBlkCount = True)

        # Do Erase from 0 to MaxLba
        U = g_localVars["MaxLba"]
        EndLba = self.__sdCmdObj.calculate_endLba(startLba = 0x0, blockcount = U)
        self.__dvtLib.Erase(StartLba = 0x0, EndLba = EndLba , directCardAPI = True)

        # Declare LoopCounter = 0
        LoopCounter = 0

        # Set Label Loop
        while LoopCounter < 100:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*" * 10 + "Loop count %d is started" %LoopCounter +  "*" * 10)

            # Set CMD23StartBlock as per RandomStartAddress(rand%3 + 1) value
            RandomStartAddress = random.randrange(0,3) + 1
            if RandomStartAddress == 1:
                g_localVars["CMD23StartBlock"] = 0
            if RandomStartAddress == 2:
                g_localVars["CMD23StartBlock"] = random.randrange(0, old_div(U,2))
            if RandomStartAddress == 3:
                    g_localVars["CMD23StartBlock"] = old_div(U,2)

            #Set CMD23BlockCoun as per RandomBlockCount(rand%2 + 1) value
            RandomBlockCount = random.randrange(0,2) + 1
            if RandomBlockCount == 1:
                RandomBlockCountLargeSize =  random.randrange(0, 10) + 1
                if RandomBlockCountLargeSize  == 5:
                    g_localVars["CMD23BlockCount"] = random.randrange(0xFFFF)
                else:
                    g_localVars["CMD23BlockCount"] = 0xFFFF
            if RandomBlockCount == 2:
                g_localVars["CMD23BlockCount"] = 1

            #Set Reset method parameters
            RandomReset =random.randrange(0,3) + 1
            if RandomReset == 1:
                g_localVars["SetPower"]= 1
                g_localVars["SendCMD0"] = 1
                g_localVars["SendCMD8"] = 1
            if RandomReset == 2:
                g_localVars["SetPower"]= 1
                g_localVars["SendCMD0"] = 0
                g_localVars["SendCMD8"] = 1
            if RandomReset == 3:
                g_localVars["SetPower"]= 0
                g_localVars["SendCMD0"] = 1
                g_localVars["SendCMD8"] = 1

            #Call Utility_CMD23_Write
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call Utility_CMD23_Write script")
            blkCountCMD23 = self.__Utility_CMD23Write.Run( g_localVars["CMD23StartBlock"],  g_localVars["CMD23BlockCount"],
                                                          g_localVars["PredefinedNumOfBlkCnt"], g_localVars["CMD23DataType"], usePreDefBlkCount = True)
            g_localVars["blkCountCMD23"] = blkCountCMD23

            #Call Utility_Reset
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call Utility_Reset script")
            self.__ResetUtil.Run( globalProjectValues, g_localVars["ProtocolMode"], g_localVars["Identification"],
                                 g_localVars["VerifyType"], g_localVars["SetPower"], g_localVars["SendCMD8"], g_localVars["SendCMD0"])

            #Do Multiple Read from CMD23StartBlock to CMD23BlockCount
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Performing Multiple Read operation")
            self.__dvtLib.ReadWithFPGAPattern(g_localVars["CMD23StartBlock"], g_localVars["blkCountCMD23"], pattern=g_localVars["CMD23DataType"],usePreDefBlkCount = True)

            #Do Erase from CMD23StartBlock to CMD23BlockCount
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Erasing Data")
            BlockCount=g_localVars["blkCountCMD23"]
            EndLba = self.__sdCmdObj.calculate_endLba(startLba = g_localVars["CMD23StartBlock"], blockcount = BlockCount)
            self.__dvtLib.Erase( StartLba=g_localVars["CMD23StartBlock"],EndLba = EndLba, directCardAPI=True)

            #Do Multiple Read from CMD23StartBlock to CMD23BlockCount
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Performing Multiple Read operation")
            self.__dvtLib.ReadWithFPGAPattern(g_localVars["CMD23StartBlock"], g_localVars["blkCountCMD23"], pattern=0, usePreDefBlkCount = True)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*" * 10 + "Loop count %d is Completed" %LoopCounter +  "*" * 10)
            LoopCounter = LoopCounter + 1

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + " Execution Completed " + "-" * 20 + "\n")
        return 0
    #End of Run function
#End of CMD23ValidWriteRead

    # CVF Hook Function: [Testcase Should start with "test_"]
    def test_CMD23_TC001_Valid_Write_Read(self):  # [Same in xml tag: <Test name="test_CMD23_TC001_Valid_Write_Read">]

        # Calling Testcase logic
        self.Run()

# Testcase Class - Ends