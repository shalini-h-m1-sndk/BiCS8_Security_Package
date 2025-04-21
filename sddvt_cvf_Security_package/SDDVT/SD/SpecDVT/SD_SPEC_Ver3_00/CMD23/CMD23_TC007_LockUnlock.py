"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                :
# CVF CALL ALL SCRIPT            : CMD23_CA01_SDMode.xml
# CVF SCRIPT                     : CMD23_TC007_LockUnlock.py
# DESCRIPTION                    :
# PRERQUISTE                     : [CMD23_UT06_CMD23Write, CMD23_UT08_LoadCMD23_Variables, CMD23_UT09_LoadLocal_Variables]
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=CMD23_TC007_LockUnlock --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Sushmitha P.S
# REVIEWED BY                    : Sivagurunathan
# DATE                           : 18-Jun-2024
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

# Dependent utilities
import CMD23_UT08_LoadCMD23_Variables as LoadCMD23Variables
import CMD23_UT09_LoadLocal_Variables as LoadLocalVariables
import CMD23_UT06_CMD23Write as CMD23Write

# Testcase Class - Begins
class CMD23_TC007_LockUnlock(TestCase.TestCase, customize_log):
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

        ###### Customize Log ######
        self.fn = os.path.basename(getframeinfo(currentframe()).filename)
        customize_log.__init__(self, self.__TF)

        ###### Testcase Specific Variables ######
        self.__LoadCMD23Variables = LoadCMD23Variables.CMD23_UT08_LoadCMD23_Variables(self.vtfContainer)
        self.__LoadLocal_Variables = LoadLocalVariables.CMD23_UT09_LoadLocal_Variables(self.vtfContainer)
        self.__Utility_CMD23Write = CMD23Write.CMD23_UT06_CMD23Write(self.vtfContainer)

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

        SendOCR = int(globalProjectValues['globalOCRArgValue'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SendOCR : %d"%SendOCR)

        ExpectOCR = int(globalProjectValues['globalOCRResValue'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ExpectOCR : %s"%ExpectOCR)

        # CALL Utility_LoadLocal_Variables script
        localVariables  = self.__LoadLocal_Variables.Run( globalProjectValues, ret = 1)

        # CALL Utility_LoadCMD23_Variables script
        cmd23Variables = self.__LoadCMD23Variables.Run( ret = 1)

        # Initialize Variables
        g_localVars = {}
        g_localVars["MaxLba"] = self.__cardMaxLba
        g_localVars["CMD23StartBlock"] = cmd23Variables["CMD23StartBlock"]
        g_localVars["CMD23BlockCount"] = cmd23Variables["CMD23BlockCount"]
        g_localVars["CMD23DataType"]   = cmd23Variables ["CMD23DataType"]
        g_localVars["CMD23VerifyWriteFlag"]   = cmd23Variables ["CMD23VerifyWriteFlag"]
        g_localVars["PredefineNumBlkFlag"]   = cmd23Variables ["PredefineNumBlkFlag"]
        g_localVars["PredefinedNumOfBlkCnt"] = cmd23Variables['PredefinedNumOfBlkCnt']
        g_localVars["IgnorePredefinedBlockCnt"] =  cmd23Variables['IgnorePredefinedBlockCnt']
        g_localVars['FillSectionWithZero'] = cmd23Variables['FillSectionWithZero']

        # Get values from Utility LoadLocal_Variables
        g_localVars["Identification"] = localVariables['Identification']
        g_localVars["ProtocolMode"] = localVariables['ProtocolMode']
        g_localVars["VerifyType"]   = localVariables['VerifyType']
        g_localVars["SetPower"]     = localVariables["SetPower"]
        g_localVars["SendCMD0"]     = localVariables["SendCMD0"]
        g_localVars["SendCMD8"]     = localVariables["SendCMD8"]


        # Declare LoopCounter = 0
        LoopCounter = 0

        U = g_localVars["MaxLba"]

        # Set Label Loop
        while LoopCounter < 100:
            # Set CMD23StartBlock
            g_localVars["CMD23StartBlock"] = random.randrange(0, old_div(U,2))

            g_localVars["CMD23BlockCount"] =  random.randrange(0, 100) + 1

            # Set Reset method parameters
            RandomReset =random.randrange(0,2) + 1
            if RandomReset == 1:
                g_localVars["SetPower"] = 1
                g_localVars["SendCMD0"] = 1
                g_localVars["SendCMD8"] = 1

            if RandomReset == 2:
                g_localVars["SetPower"] = 1
                g_localVars["SendCMD0"] = 0
                g_localVars["SendCMD8"] = 1

            # Call Utility_CMD23_Write
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call Utility_CMD23_Write script")
            blkCountCMD23 = self.__Utility_CMD23Write.Run( g_localVars["CMD23StartBlock"],  g_localVars["CMD23BlockCount"],
                                                          g_localVars["PredefinedNumOfBlkCnt"], g_localVars["CMD23DataType"], usePreDefBlkCount = True)

            g_localVars["blkCountCMD23"] = blkCountCMD23

            # Send LockUnlock Command
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set the password to Card")
            self.__dvtLib.Lock_unlock(setPassword=1,oldPassword="123456",blockLength = 0x200)

            # Check card is Ready for Data and unlocked state
            self.__dvtLib.Check_Trans_NotLocked()

            # Call Utility_CMD23_Write
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call Utility_CMD23_Write script")

            blkCountCMD23 = self.__Utility_CMD23Write.Run(  g_localVars["CMD23StartBlock"],  g_localVars["CMD23BlockCount"],
                                                          g_localVars["PredefinedNumOfBlkCnt"], g_localVars["CMD23DataType"], usePreDefBlkCount = True)

            # Reset Block will lock the card after soft reset since password is Set
            self.resetBlock(g_localVars, SendOCR, ExpectOCR)

            # Check Card is in Trans State, Ready for Data and Locked
            self.__dvtLib.Check_Trans_Locked()

            # Single Command, Cmd23
            try:
                self.__dvtLib.SingleCommand(OPCode=23, Argument = 0x2, ResponseType=sdcmdWrap.TYPE_RESP._R1, DataTransfer=sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_IS_NOT_RESPONDING" , Operation_Name = "SingleCommand")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING  failure is not occured")

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "---------------------Tag 1-------------------")

            try:
                status = self.__sdCmdObj.GetCardStatus()
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception =  "CARD_ILLEGAL_CMD", Operation_Name = "SingleCommand")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_ILLEGAL_CMD  failure is not occured")

            # Unlock the card but retain the password
            self.__dvtLib.Lock_unlock(oldPassword="123456")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "card is unlocked as Expected\n")

            # Check card is in TransState and unlocked
            self.__dvtLib.Check_Trans_NotLocked()

            # Call Utility_CMD23_Write
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call Utility_CMD23_Write script")

            blkCountCMD23 = self.__Utility_CMD23Write.Run(  g_localVars["CMD23StartBlock"],  g_localVars["CMD23BlockCount"],
                                                          g_localVars["PredefinedNumOfBlkCnt"], g_localVars["CMD23DataType"], usePreDefBlkCount = True)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "---------------------Tag 2-------------------")

            # Lock the card using ACMD42
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Run Lock/Unlock Cmd to lock the card")
            self.__dvtLib.Lock_unlock(lock=1, oldPassword="123456", blockLength = 0x200)

            #Check Card is in Trans State, Ready for Data and Locked
            self.__dvtLib.Check_Trans_Locked()

            # Single Command, Cmd23
            try:
                self.__dvtLib.SingleCommand(OPCode=23, Argument = 0x2, ResponseType=sdcmdWrap.TYPE_RESP._R1, DataTransfer=sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_IS_NOT_RESPONDING" , Operation_Name = "SingleCommand")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING  failure is not occured")

            # Get Card Status and Verify Trans State
            try:
                status = self.__sdCmdObj.GetCardStatus()
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception =  "CARD_ILLEGAL_CMD", Operation_Name = "SingleCommand")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_ILLEGAL_CMD  failure is not occured")

            # Unlock the Card and retain the Password
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Run Lock/Unlock Cmd to unlock the card")
            self.__dvtLib.Lock_unlock(lock =0,oldPassword="123456")

            # Check card is Ready for Data and unlocked State
            self.__dvtLib.Check_Trans_NotLocked()

            # Call Utility_CMD23_Write
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call Utility_CMD23_Write script")

            blkCountCMD23 = self.__Utility_CMD23Write.Run(  g_localVars["CMD23StartBlock"],  g_localVars["CMD23BlockCount"],
                                                          g_localVars["PredefinedNumOfBlkCnt"], g_localVars["CMD23DataType"], usePreDefBlkCount = True)

            # Check card is Ready for Data and unlocked State
            self.__dvtLib.Check_Trans_NotLocked()

            # Call Utility_CMD23_Write
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call Utility_CMD23_Write script")

            blkCountCMD23 = self.__Utility_CMD23Write.Run(  g_localVars["CMD23StartBlock"],  g_localVars["CMD23BlockCount"],
                                                          g_localVars["PredefinedNumOfBlkCnt"], g_localVars["CMD23DataType"], usePreDefBlkCount = True)

            # Reset Block will Lock the Card since password is setted previously.
            self.resetBlock(g_localVars, SendOCR, ExpectOCR)

            # Single Command, Cmd23
            try:
                self.__dvtLib.SingleCommand(OPCode=23, Argument = 0x2, ResponseType=sdcmdWrap.TYPE_RESP._R1, DataTransfer=sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_IS_NOT_RESPONDING", Operation_Name = "SingleCommand")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING  failure is not occured")

            try:
                status = self.__sdCmdObj.GetCardStatus()
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception =  "CARD_ILLEGAL_CMD", Operation_Name = "SingleCommand")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_ILLEGAL_CMD  failure is not occured")

            # Unlock the card by clearing the Password
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Run Lock/Unlock Cmd to unlock the card")
            self.__dvtLib.Lock_unlock(clearPassword = 1, oldPassword="123456")

            # Check card is in Trans State and unlocked
            self.__dvtLib.Check_Trans_NotLocked()

            # Call Utility_CMD23_Write
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call Utility_CMD23_Write script")

            blkCountCMD23 = self.__Utility_CMD23Write.Run(  g_localVars["CMD23StartBlock"],  g_localVars["CMD23BlockCount"],
                                                          g_localVars["PredefinedNumOfBlkCnt"], g_localVars["CMD23DataType"], usePreDefBlkCount = True)
            g_localVars["blkCountCMD23"] = blkCountCMD23

            # Reset Block will not Locked the card since setted password is cleared
            self.resetBlock(g_localVars, SendOCR, ExpectOCR)

            # Do Multiple Read from CMD23StartBlock to CMD23BlockCount
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Performing Multiple Read operation")

            self.__dvtLib.ReadWithFPGAPattern(g_localVars["CMD23StartBlock"], g_localVars["blkCountCMD23"], pattern=g_localVars["CMD23DataType"], usePreDefBlkCount = True)

            # Do Erase from CMD23StartBlock to CMD23BlockCount
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Erasing Data")
            BlockCount=g_localVars["blkCountCMD23"]
            EndLba = self.__sdCmdObj.calculate_endLba(startLba = g_localVars["CMD23StartBlock"], blockcount = BlockCount)
            self.__dvtLib.Erase(StartLba=g_localVars["CMD23StartBlock"], EndLba = EndLba, directCardAPI=True)

            # Do Multiple Read from CMD23StartBlock to CMD23BlockCount
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Performing Multiple Read operation")

            self.__dvtLib.ReadWithFPGAPattern(g_localVars["CMD23StartBlock"], g_localVars["blkCountCMD23"], pattern=0, usePreDefBlkCount = True)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*" * 10 + "Loop count %d is Completed" %LoopCounter +  "*" * 10)
            LoopCounter = LoopCounter + 1

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + " Execution Completed " + "-" * 20 + "\n")
        return 0

    #End of Run function
#End of CMD23LockUnlock

    # Block Defination
    def resetBlock(self, g_localVars, SendOCR, ExpectOCR):
        if g_localVars["SetPower"] == 1:
            # Set No Power, Power
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)
            # RESET card
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RESET card")
            self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=SendOCR, cardSlot=1, sendCmd8=True,
                               initInfo=None, rca=0x0,
                               time=0x0, sendCMD0=0x1,
                               bHighCapacity=False,
                               bSendCMD58=False,
                               version=0x0, VOLA=0x1,
                               cmdPattern=0xAA,
                               reserved=0x0,
                               expOCRVal=ExpectOCR)

            # Identification of the card
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification of the card")
            self.__dvtLib.Identification()

            #Select Card
            self.__sdCmdObj.Cmd7()

        #End of resetBlock

    # Testcase logic - Ends

    # CVF Hook Function: [Testcase Should start with "test_"]
    def test_CMD23_TC007_LockUnlock(self):  # [Same in xml tag: <Test name="test_CMD23_TC007_LockUnlock">]

        # Calling Testcase logic
        self.Run()

# Testcase Class - Ends