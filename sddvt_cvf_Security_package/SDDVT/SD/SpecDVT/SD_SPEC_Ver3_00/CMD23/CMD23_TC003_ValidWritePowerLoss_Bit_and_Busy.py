"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                :
# CVF CALL ALL SCRIPT            : CMD23_CA01_SDMode.xml
# CVF SCRIPT                     : CMD23_TC003_ValidWritePowerLoss_Bit_and_Busy.py
# DESCRIPTION                    :
# PRERQUISTE                     : [CMD23_UT08_LoadCMD23_Variables, CMD23_UT09_LoadLocal_Variables, CMD23_UT06_CMD23Write, CMD23_UT10_Reset]
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=CMD23_TC003_ValidWritePowerLoss_Bit_and_Busy --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Sushmitha P.S
# REVIEWED BY                    : Sivagurunathan
# DATE                           : 29-May-2024
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
class CMD23_TC003_ValidWritePowerLoss_Bit_and_Busy(TestCase.TestCase, customize_log):
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
        Name : Run

        Purpose: 1. Predefined write with power loss(bit exact or busy time) | Choose a random bit from 53-4117
                2. Predefined write wit power loss (busy time) | choose a random time (msec) from 150-current global write T.O
        STEP 1 : Call Script globalInitCard
        STEP 2 : Initialize Variables
        """
        # Call Script globalInitCard
        globalProjectValues = self.__sdCmdObj.DoBasicInit()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Execution Started " + "-" * 20 + "\n")

        # CALL Utility_LoadCMD23_Variables script
        cmd23Variables = self.__LoadCMD23Variables.Run( ret = 1)

        # CALL Utility_LoadLocal_Variables script
        localVariables  = self.__LoadLocal_Variables.Run( globalProjectValues, ret = 1)

        # Create dictionary for local variables being used here
        g_localVars = {}

        # Variable Declaration for LoopCounter
        g_localVars["IgnorePredefinedBlockCnt"]= 0
        LoopCounter = 0

        g_localVars["MaxLba"] = self.__cardMaxLba
        U = g_localVars["MaxLba"]

        # Get values from Utility LoadLocal_Variables
        g_localVars["Identification"] = localVariables['Identification']
        g_localVars["ProtocolMode"] = localVariables['ProtocolMode']
        g_localVars["VerifyType"]   = localVariables['VerifyType']

        g_localVars["PredefinedNumOfBlkCnt"] = cmd23Variables['PredefinedNumOfBlkCnt']

        while LoopCounter < 100:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*" * 10 + "Loop count %d is started" %LoopCounter +  "*" * 10)

            # Set CMD23StartBlock as per RandomStartAddress(rand%3 + 1) value
            RandomStartAddress = random.randrange(0,3) + 1
            if RandomStartAddress == 1:
                g_localVars["CMD23StartBlock"] = 0
            if RandomStartAddress == 2:
                g_localVars["CMD23StartBlock"] = random.randrange(0, (old_div(U,2)))
            if RandomStartAddress == 3:
                    g_localVars["CMD23StartBlock"] = old_div(U,2)

            # Set CMD23BlockCoun as per RandomBlockCount(rand%2 + 1) value
            RandomBlockCount = random.randrange(0,2) + 1
            if RandomBlockCount == 1:
                g_localVars["PredefinedNumOfBlkCnt"] = random.randrange(0, 0xFFFF) + 1

            if RandomBlockCount == 2:
                g_localVars["PredefinedNumOfBlkCnt"] = 1
                g_localVars["CMD23BlockCount"] = 1

            # Set CMD23BlockCoun as per RandomStopTranBlockCount
            RandomStopTranBlockCount = random.randrange(0, 2) + 1
            if RandomStopTranBlockCount  == 1:
                g_localVars["CMD23BlockCount"] = g_localVars["PredefinedNumOfBlkCnt"]

            if RandomStopTranBlockCount  == 2:
                g_localVars["CMD23BlockCount"] = random.randrange(0, g_localVars["PredefinedNumOfBlkCnt"]) + 1

            # Initialize Variables
            RandomReset = random.randrange(0, 3)  + 1
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

            RandomPowerLoss  = random.randrange(0, 2)
            randomStopBit = 53 + (random.randint(0, 4064))
            globalWriteTimeOut = int(self.__config.get('globalWriteTO'))
            randomStopTime = 150 + (random.randrange(0, ((globalWriteTimeOut-150))))

            if RandomPowerLoss == 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple Write with Random PowerLoss 0 is called")
                # PySReadWriteParams
                RWParams = sdcmdWrap.PySReadWriteParams()
                RWParams.cardSlot = 1
                RWParams.dataAddress = g_localVars["CMD23StartBlock"]
                RWParams.countBlk = g_localVars["CMD23BlockCount"]
                RWParams.actualBlk = g_localVars["CMD23BlockCount"]
                RWParams.blockLen = 0x200   # 512

                # PySPerfReadWriteParams
                PRWParams = sdcmdWrap.PySPerfReadWriteParams()
                PRWParams.p = sdcmdWrap.Pattern.ANY_WORD
                PRWParams.anyWord = 0

                # PySEnhancedCmdData
                EnhcdCmdData = sdcmdWrap.PySEnhancedCmdData()
                EnhcdCmdData.CmdInvokingFormatSecondCmd = sdcmdWrap.ECmdInvokingFormat.BIT_EXACT_POSITION
                EnhcdCmdData.AbortNRCVal = 7
                EnhcdCmdData.AbortBitPosInBlock = 0x0
                EnhcdCmdData.AbortBusy = 0x0
                EnhcdCmdData.AbortIdle = 0x0
                EnhcdCmdData.bCreatePowerCycle = True

                EnhcdCmdData.CmdSequenceSize = sdcmdWrap.ECmdSequenceSize.TWO_CMD_SEQ
                SecondCmd = sdcmdWrap.PySCmdInfo()
                SecondCmd.command = sdcmdWrap._CARD_COMMAND_.POWER_LOSS   # 255
                SecondCmd.res = sdcmdWrap.SD_RESPONSE_TYPE.NO_RESPONSE
                EnhcdCmdData.pSecondCmd = SecondCmd

                EnhcdCmdData.EnancedOpTimeUnits = sdcmdWrap.EEnancedOpTimeUnits.MILI_SECOND
                EnhcdCmdData.pThirdCmdParams = None

                CMD23Obj = sdcmdWrap.Command23 ()

                CMD23Obj.usePreDefBlkCount = True
                CMD23Obj.isUserDefinedArgument = False
                CMD23Obj.userDefinedArgument = 0
                CMD23Obj.numberOfBlocks = g_localVars["PredefinedNumOfBlkCnt"]
                CMD23Obj.contextId = 0
                CMD23Obj.isReliableWrite = False
                CMD23Obj.isPacked = False

                try:
                    sdcmdWrap.EnhancedWriteMultiBlock(PyRWParams = RWParams, cmd = sdcmdWrap._CARD_COMMAND_._WRITE_MULTIPLE_BLOCK,
                                                      UsePatternGen = True, PyPrefRWParams = PRWParams, cmd23 = CMD23Obj,
                                                      PyEnhcdCmdData = EnhcdCmdData, buf = None)
                except ValidationError.CVFExceptionTypes as exc:
                    exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                    self.__sdCmdObj.ErrorPrint(exc)
                    raise ValidationError.TestFailError(self.fn, exc.GetFailureDescription())

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple write with Random PowerLoss 0 is completed")

            if RandomPowerLoss == 1:
                # Multiple Write on PowerLoss
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple Write with Random PowerLoss 1 is called")

                RWParams = sdcmdWrap.PySReadWriteParams()
                RWParams.cardSlot = 1
                RWParams.dataAddress = g_localVars["CMD23StartBlock"]
                RWParams.countBlk = g_localVars["CMD23BlockCount"]
                RWParams.actualBlk = g_localVars["CMD23BlockCount"]
                RWParams.blockLen = 0x200   # 512

                # PySPerfReadWriteParams
                PRWParams = sdcmdWrap.PySPerfReadWriteParams()
                PRWParams.p = sdcmdWrap.Pattern.ANY_WORD
                PRWParams.anyWord = 0

                # PySEnhancedCmdData
                EnhcdCmdData = sdcmdWrap.PySEnhancedCmdData()
                EnhcdCmdData.CmdInvokingFormatSecondCmd = sdcmdWrap.ECmdInvokingFormat.BUSY_TIME
                EnhcdCmdData.AbortNRCVal = 7
                EnhcdCmdData.AbortBitPosInBlock = 0x0
                EnhcdCmdData.AbortBusy = 0x0
                EnhcdCmdData.AbortIdle = 0x0
                EnhcdCmdData.bCreatePowerCycle = True

                EnhcdCmdData.CmdSequenceSize = sdcmdWrap.ECmdSequenceSize.TWO_CMD_SEQ
                SecondCmd = sdcmdWrap.PySCmdInfo()
                SecondCmd.command = sdcmdWrap._CARD_COMMAND_.POWER_LOSS   # 255
                SecondCmd.res = sdcmdWrap.SD_RESPONSE_TYPE.NO_RESPONSE
                EnhcdCmdData.pSecondCmd = SecondCmd

                EnhcdCmdData.EnancedOpTimeUnits = sdcmdWrap.EEnancedOpTimeUnits.MILI_SECOND
                EnhcdCmdData.pThirdCmdParams = None

                CMD23Obj = sdcmdWrap.Command23 ()
                CMD23Obj.usePreDefBlkCount = True
                CMD23Obj.isUserDefinedArgument = False
                CMD23Obj.userDefinedArgument = 0
                CMD23Obj.numberOfBlocks = g_localVars["PredefinedNumOfBlkCnt"]
                CMD23Obj.contextId = 0
                CMD23Obj.isReliableWrite = False
                CMD23Obj.isPacked = False

                try:
                    sdcmdWrap.EnhancedWriteMultiBlock(PyRWParams = RWParams, cmd = sdcmdWrap._CARD_COMMAND_._WRITE_MULTIPLE_BLOCK,
                                                      UsePatternGen = True, PyPrefRWParams = PRWParams,cmd23 = CMD23Obj,
                                                      PyEnhcdCmdData = EnhcdCmdData, buf = None)
                except ValidationError.CVFExceptionTypes as exc:
                    exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                    self.__sdCmdObj.ErrorPrint(exc)
                    raise ValidationError.TestFailError(self.fn, exc.GetFailureDescription())
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple write with Random PowerLoss 1 is completed")

            sdcmdWrap.SetPower(1)

            g_localVars["SetPower"] = 1

            # Call Utility_Reset
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call Utility_Reset script")
            self.__ResetUtil.Run( globalProjectValues, g_localVars["ProtocolMode"], g_localVars["Identification"],
                                 g_localVars["VerifyType"], g_localVars["SetPower"], g_localVars["SendCMD8"], g_localVars["SendCMD0"])

            # Do Multiple Write from CMD23StartBlock to CMD23BlockCount
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Performing Multiple Write operation")

            try:
                self.__sdCmdObj.VerifyReliableWrite(StartLBA = g_localVars["CMD23StartBlock"], BlockCount = g_localVars["CMD23BlockCount"], Pattern = 0)
                #sdcmdWrap.EnhancedWriteMultiBlock(usePreDefBlkCount = False, reliableWrite = True, PreDefBlkCount = 0)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                raise ValidationError.TestFailError(self.fn, exc.GetFailureDescription())
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple Write with reliable verify compledted")

            # Do Erase from CMD23StartBlock to CMD23BlockCount
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Erasing Data")
            BlockCount = g_localVars["CMD23BlockCount"]
            EndLba = self.__sdCmdObj.calculate_endLba(startLba = g_localVars["CMD23StartBlock"], blockcount = BlockCount)
            self.__dvtLib.Erase( StartLba=g_localVars["CMD23StartBlock"], EndLba = EndLba, directCardAPI=True)

            # Do Multiple Read from CMD23StartBlock to CMD23BlockCount
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Performing Multiple Read operation")

            self.__dvtLib.ReadWithFPGAPattern(g_localVars["CMD23StartBlock"], g_localVars["CMD23BlockCount"], pattern=0,usePreDefBlkCount = True)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*" * 10 + "Loop count %d is Completed" %LoopCounter +  "*" * 10)
            LoopCounter = LoopCounter + 1

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + " Execution Completed " + "-" * 20 + "\n")
        return 0

    #End of Run function
#End of CMD23ValidWriteReadWthStopTran

    # Testcase logic - Ends

    # CVF Hook Function: [Testcase Should start with "test_"]
    def test_CMD23_TC003_ValidWritePowerLoss_Bit_and_Busy(self):  # [Same in xml tag: <Test name="test_CMD23_TC003_ValidWritePowerLoss_Bit_and_Busy">]

        # Calling Testcase logic
        self.Run()

# Testcase Class - Ends