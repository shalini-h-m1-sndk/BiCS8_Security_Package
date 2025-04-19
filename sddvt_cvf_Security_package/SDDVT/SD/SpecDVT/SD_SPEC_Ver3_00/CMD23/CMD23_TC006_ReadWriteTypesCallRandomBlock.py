"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                :
# CVF CALL ALL SCRIPT            : CMD23_CA01_SDMode.xml
# CVF SCRIPT                     : CMD23_TC006_ReadWriteTypesCallRandomBlock.py
# DESCRIPTION                    :
# PRERQUISTE                     : CMD23_UT03_CMD20_GetSequence, CMD23_UT05_CMD20Write, CMD23_UT06_CMD23Write,
                                    CMD23_UT07_LoadCMD20_Variables, CMD23_UT08_LoadCMD23_Variables, CMD23_UT09_LoadLocal_Variables,
                                    CMD23_UT10_Reset
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=CMD23_TC006_ReadWriteTypesCallRandomBlock --isModel=false --enable_console_log=1 --adapter=0
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
import CMD23_UT03_CMD20_GetSequence as CMD20GetSequence
import CMD23_UT06_CMD23Write as CMD23Write
import CMD23_UT07_LoadCMD20_Variables as LoadCMD20Variables
import CMD23_UT08_LoadCMD23_Variables as LoadCMD23Variables
import CMD23_UT09_LoadLocal_Variables as LoadLocalVariables
import CMD23_UT10_Reset as UtilityReset

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

class CMD23_TC006_ReadWriteTypesCallRandomBlock(TestCase.TestCase, customize_log):
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
        self.__LoadCMD20Variables = LoadCMD20Variables.CMD23_UT07_LoadCMD20_Variables(self.vtfContainer)
        self.__LoadLocal_Variables = LoadLocalVariables.CMD23_UT09_LoadLocal_Variables(self.vtfContainer)
        self.__Utility_CMD23Write = CMD23Write.CMD23_UT06_CMD23Write(self.vtfContainer)
        self.__getSequence = CMD20GetSequence.CMD23_UT03_CMD20_GetSequence(self.vtfContainer)
        self.__ResetUtil = UtilityReset.CMD23_UT10_Reset(self.vtfContainer)

    # Testcase logic - Starts
    def Run(self, ret = 0):
        """
        Name : Run
        STEP 1 : Call Script globalInitCard
        STEP 2 : Initialize Variables
        """
        # Call Script globalInitCard
        globalProjectValues = self.__sdCmdObj.DoBasicInit()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Execution Started " + "-" * 20 + "\n")

        # CALL Utility_LoadCMD23_Variables script
        cmd23Variables = self.__LoadCMD23Variables.Run( ret = 1)

        #Call Utility Utility_LoadCMD20_Variables
        cmd20Variables = self.__LoadCMD20Variables.Run()

        # CALL Utility_LoadLocal_Variables script
        localVariables  = self.__LoadLocal_Variables.Run(globalProjectValues, ret = 1 )

        #Create dictionary for local variables being used here
        g_localVars = {}
        g_localVars["MaxLba"] = self.__cardMaxLba
        U = g_localVars["MaxLba"]

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
        g_localVars['FillSectionWithZero'] = cmd23Variables['FillSectionWithZero']

        # Variable Declaration for LoopCounter
        LoopCounter = 0

        # Set Label Loop
        while LoopCounter < 100:

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*" * 10 + "Loop count %d is started" %LoopCounter +  "*" * 10)

            #  Set CMD23StartBlock as per RandomStartAddress(rand%3 + 1) value
            RandomStartAddress = random.randrange(0,3) + 1
            if RandomStartAddress == 1:
                g_localVars["CMD23StartBlock"] = 0
            if RandomStartAddress == 2:
                g_localVars["CMD23StartBlock"] = (random.randrange(0, (old_div(U,2))))
            if RandomStartAddress == 3:
                g_localVars["CMD23StartBlock"] = old_div(U,2)

            # Set CMD23BlockCoun as per RandomStopTranBlockCount
            RandomBlockCount = random.randrange(0, 2) + 1
            if RandomBlockCount  == 1:
                RandomBlockCountLargeSize = random.randrange(0, 10) + 1
                if RandomBlockCountLargeSize  == 5:
                    g_localVars["CMD23BlockCount"] = random.randrange(0, (0xFFFF))
                else:
                    g_localVars["CMD23BlockCount"] = 0xFFFF

            if RandomBlockCount  == 2:
                g_localVars["CMD23BlockCount"] = 1

            # Initialize Variables
            RandomReset = random.randrange(0, 3) + 1
            if RandomReset == 1:
                g_localVars["SetPower"] = 1
                g_localVars["SendCMD0"] = 1
                g_localVars["SendCMD8"] = 1

            if RandomReset == 2:
                g_localVars["SetPower"] = 1
                g_localVars["SendCMD0"] = 0
                g_localVars["SendCMD8"] = 1

            if RandomReset == 3:
                g_localVars["SetPower"] = 0
                g_localVars["SendCMD0"] = 1
                g_localVars["SendCMD8"] = 1

            # Variable Declaration Operation for RandomBlock
            RandomBlock=  random.randrange(0, 5) + 1
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Random Block is %d " % RandomBlock)

            # Single Write/Read 20%
            if RandomBlock == 1:

                self.__dvtLib.WriteWithFPGAPattern(StartLba = g_localVars["CMD23StartBlock"],
                                                   blockCount = 0x1,
                                                   pattern=g_localVars["CMD23DataType"],
                                                   SingleWrite=True)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "######### Completed WRITE Operation")

                self.__dvtLib.ReadWithFPGAPattern(StartLba = g_localVars["CMD23StartBlock"],
                                                  blockCount = 0x1,
                                                  pattern=g_localVars["CMD23DataType"],
                                                  SingleRead=True)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "########## Completed Read Operation")

                self.__dvtLib.WriteWithFPGAPattern(StartLba = g_localVars["CMD23StartBlock"],
                                                   blockCount = 0x1,
                                                   pattern=0,
                                                   SingleWrite=True)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "######### Completed WRITE Operation")

                self.__dvtLib.ReadWithFPGAPattern(StartLba = g_localVars["CMD23StartBlock"],
                                                  blockCount = 0x1,
                                                  pattern=0,
                                                  SingleRead=True)

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "########## Completed Read Operation")

            # Multiple Write/Read without CMD23 20%
            if RandomBlock == 2:

                self.__dvtLib.WriteWithFPGAPattern(StartLba = g_localVars["CMD23StartBlock"],
                                                   blockCount = g_localVars["CMD23BlockCount"],
                                                   pattern=g_localVars["CMD23DataType"])

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#########Completed WRITE Operation")

                self.__dvtLib.ReadWithFPGAPattern(StartLba = g_localVars["CMD23StartBlock"],
                                                  blockCount = g_localVars["CMD23BlockCount"],
                                                  pattern= g_localVars["CMD23DataType"])
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#########Completed Read Operation")

                self.__dvtLib.WriteWithFPGAPattern(StartLba = g_localVars["CMD23StartBlock"],
                                                   blockCount = g_localVars["CMD23BlockCount"],
                                                   pattern=0)

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#########Completed WRITE Operation")

                self.__dvtLib.ReadWithFPGAPattern(StartLba = g_localVars["CMD23StartBlock"],
                                                  blockCount = g_localVars["CMD23BlockCount"],
                                                  pattern=0)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#########Completed Read Operation")

            # Multiple Write/Read with CMD23  without Stop transmission 20%
            if RandomBlock == 3:
                g_localVars["FillSectionWithZero"] = 1
                g_localVars["PredefineNumBlkFlag"] = 1
                g_localVars["IgnorePredefinedBlockCnt"] =1

                # Call Utility_CMD23_Write
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call Utility_CMD23_Write script")
                blkCountCMD23 = self.__Utility_CMD23Write.Run(  g_localVars["CMD23StartBlock"],  g_localVars["CMD23BlockCount"],
                                                              g_localVars["PredefinedNumOfBlkCnt"], g_localVars["CMD23DataType"], usePreDefBlkCount = True)
                g_localVars["blkCountCMD23"] = blkCountCMD23

            # Multiple Write /Read with CMD23 with Stop Transmission < Block count 20%
            if RandomBlock == 4:
                g_localVars["FillSectionWithZero"] = 1
                g_localVars["PredefineNumBlkFlag"] = 1
                g_localVars["IgnorePredefinedBlockCnt"] =0
                g_localVars["PredefinedNumOfBlkCnt"] = random.randrange(0, (0xFFFF))
                g_localVars["CMD23BlockCount"] = random.randrange(0,  (g_localVars["PredefinedNumOfBlkCnt"])) +1

                # Call Utility_CMD23_Write
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call Utility_CMD23_Write script")
                blkCountCMD23 = self.__Utility_CMD23Write.Run(  g_localVars["CMD23StartBlock"],  g_localVars["CMD23BlockCount"],
                                                              g_localVars["PredefinedNumOfBlkCnt"], g_localVars["CMD23DataType"], usePreDefBlkCount = True)
                g_localVars["blkCountCMD23"] = blkCountCMD23

            # Random Reset 2% /CMD20 Write 18%
            if RandomBlock == 5:
                RandomReset = random.randrange(0, 10) + 1
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RandomReset is %d" %RandomReset)
                if RandomReset == 5:

                    # Call Utility_Reset
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call Utility_Reset script")
                    self.__ResetUtil.Run( globalProjectValues, g_localVars["ProtocolMode"], g_localVars["Identification"],
                                         g_localVars["VerifyType"], g_localVars["SetPower"], g_localVars["SendCMD8"], g_localVars["SendCMD0"])
                else:
                    # Create DIR
                    self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

                    self.__dvtLib.WriteWithFPGAPattern(StartLba = cmd20Variables['DIRconstAddress'], blockCount = 0x1, pattern=0)
                    self.__dvtLib.ReadWithFPGAPattern(StartLba = cmd20Variables['DIRconstAddress'], blockCount = 0x1, pattern=0)

                    # Speed Class Start Recording
                    self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING, TimeOut = 1000 )
                    RuStartBlock = cmd20Variables['RuStartBlock']
                    BlockCount = cmd20Variables['RU']

                    self.__dvtLib.WriteWithFPGAPattern(StartLba = RuStartBlock, blockCount = BlockCount, pattern=0)

                    self.__dvtLib.ReadWithFPGAPattern(StartLba = RuStartBlock, blockCount = BlockCount, pattern=0)

                    # Variable Declaration
                    ExpectSequence = 1
                    # Call Utility_CMD20_GetSequence
                    self.__getSequence.Run( ExpectSequence = 1)

                 #   End of IF-Else loop
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*" * 10 + "Loop count %d is Completed" %LoopCounter +  "*" * 10)
            LoopCounter = LoopCounter + 1

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + " Execution Completed " + "-" * 20 + "\n")
        return 0

    #End of Run function
    # Testcase logic - Ends

    # CVF Hook Function: [Testcase Should start with "test_"]
    def test_CMD23_TC006_ReadWriteTypesCallRandomBlock(self):  # [Same in xml tag: <Test name="test_CMD23_TC006_ReadWriteTypesCallRandomBlock">]

        # Calling Testcase logic
        self.Run()

# Testcase Class - Ends