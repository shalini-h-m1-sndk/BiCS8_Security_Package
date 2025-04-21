"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                :
# CVF CALL ALL SCRIPT            : CMD23_CA01_SDMode.xml
# CVF SCRIPT                     : CMD23_TC009_StateTest.py
# DESCRIPTION                    :
# PRERQUISTE                     : [ConfigSD_UT003_GlobalInitSDCard, ConfigSD_UT007_GlobalSetBusMode, CMD23_UT06_CMD23Write,
                                   CMD23_UT08_LoadCMD23_Variables,CMD23_UT09_LoadLocal_Variables ]
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=CMD23_TC009_StateTest --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Sushmitha P.S
# REVIEWED BY                    : Sivagurunathan
# DATE                           : 28-Jun-2024
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
import time
from inspect import currentframe, getframeinfo

# Dependent Utilities
import CMD23_UT08_LoadCMD23_Variables as LoadCMD23Variables
import CMD23_UT09_LoadLocal_Variables as LoadLocalVariables
import CMD23_UT06_CMD23Write as CMD23Write

# Global Variables
import SDDVT.Config_SD.ConfigSD_UT003_GlobalInitSDCard as globalInitSDCard
import SDDVT.Config_SD.ConfigSD_UT007_GlobalSetBusMode as globalSetBusMode

# Testcase Class - Begins
class CMD23_TC009_StateTest(TestCase.TestCase, customize_log):
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
        self.__globalInitSDCard = globalInitSDCard.globalInitSDCard(self.vtfContainer)
        self.__globalSetBusMode = globalSetBusMode.GlobalSetBusMode(self.vtfContainer)

        self.__LoadCMD23Variables = LoadCMD23Variables.CMD23_UT08_LoadCMD23_Variables(self.vtfContainer)
        self.__LoadLocal_Variables = LoadLocalVariables.CMD23_UT09_LoadLocal_Variables(self.vtfContainer)
        self.__Utility_CMD23Write = CMD23Write.CMD23_UT06_CMD23Write(self.vtfContainer)

    # Testcase logic - Starts

    def Run(self):
        """
        Name : Run
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Execution Started " + "-" * 20 + "\n")

        # Call script globalInitCard
        globalProjectValues = self.__sdCmdObj.DoBasicInit()

        globalOCRArgValue = int(globalProjectValues['globalOCRArgValue'])

        # CALL Utility_LoadCMD23_Variables script
        cmd23Variables = self.__LoadCMD23Variables.Run( ret = 1)

        # CALL Utility_LoadLocal_Variables script
        localVariables  = self.__LoadLocal_Variables.Run( globalProjectValues, ret = 1)

        g_localVars = {}
        g_localVars["MaxLba"] = self.__cardMaxLba
        U  = g_localVars["MaxLba"]

        idle_state_loop = 0
        while idle_state_loop < 6:
            #Test CMD23 in Idle state
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Test CMD23 in Idle state with loop %d\n" %idle_state_loop)

            # Set (no)Power, Power
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)

            # SingleCommand, Cmd 0
            self.__sdCmdObj.Cmd0()

            try:
                self.__dvtLib.SingleCommand(OPCode=23, Argument = 0x2, ResponseType=sdcmdWrap.TYPE_RESP._R1, DataTransfer=sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_IS_NOT_RESPONDING", Operation_Name = "SingleCommand")
                idle_state_loop = idle_state_loop + 1
                continue
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING failure is not occured")

        ready_state_loop = 0
        while ready_state_loop < 6:
            #Test CMD23 in Ready state
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Test CMD23 in Ready state with loop %d\n" % ready_state_loop)

            # Set (no)Power, Power
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)

            # SPECIAL MODES
            self.__dvtLib.SetSpecialModes(5, True) #5 = Init, set = True

            # SingleCommand, Cmd 0
            self.__sdCmdObj.Cmd0()

            # Single Command, Cmd 55
            self.__sdCmdObj.Cmd55(setRCA=True)

            # Single Command, Cmd41
            self.__sdCmdObj.ACmd41(argVal=globalOCRArgValue)

            # Single Command, Cmd 55
            self.__sdCmdObj.Cmd55()

            # Single Command, Cmd41
            self.__sdCmdObj.ACmd41(argVal=globalOCRArgValue)

            try:
                self.__dvtLib.SingleCommand(OPCode=23, Argument = 0x2, ResponseType=sdcmdWrap.TYPE_RESP._R1, DataTransfer=sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_IS_NOT_RESPONDING", Operation_Name = "SingleCommand")
                ready_state_loop = ready_state_loop + 1
                continue
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING failure is not occured")

        identification_loop = 0
        while identification_loop < 6:
            #Test CMD23 in Identification state
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Test CMD23 in Identification state with loop %d\n" % identification_loop)

            # Set No Power, Power
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)

            # Call globalInitCard
            self.__globalInitSDCard.Run(globalProjectValues)

            # Single Command, Cmd2
            self.__sdCmdObj.Cmd2()

            # SingleCommand, Cmd 23
            try:
                self.__dvtLib.SingleCommand(OPCode=23, Argument = 0x2, ResponseType=sdcmdWrap.TYPE_RESP._R1, DataTransfer=sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_IS_NOT_RESPONDING", Operation_Name = "SingleCommand")
                identification_loop = identification_loop + 1
                continue
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING failure is not occured")

        standby_state_loop = 0
        while standby_state_loop < 6:
            ########Test CMD23 in Standby state
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Test CMD23 in StandBy state with loop %d\n" % standby_state_loop)

            # Set No Power, Power
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)

            # Call globalInitCard
            self.__globalInitSDCard.Run(globalProjectValues)

            # Identify Card, Exceutes from Step 19
            self.__dvtLib.Identification()

            # Check SD Status, See that Card is in Stby Mode
            self.__sdCmdObj.GetCardStatus()

            # SingleCommand, Cmd 23
            try:
                self.__dvtLib.SingleCommand(OPCode=23, Argument = 0x2, ResponseType=sdcmdWrap.TYPE_RESP._R1, DataTransfer=sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_IS_NOT_RESPONDING", Operation_Name = "SingleCommand")
                standby_state_loop = standby_state_loop + 1
                continue
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING failure is not occured")

        transfer_state_loop = 0
        while transfer_state_loop < 6:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Test CMD23 in Transfer state with loop %d\n" % transfer_state_loop)

            # Set No Power, Power
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)

            # Call globalInitCard
            self.__globalInitSDCard.Run(globalProjectValues)

            # Identify Card, Exceutes from Step 19
            self.__dvtLib.Identification()

            # Check SD Status, See that Card is in Stby Mode
            #self.__sdCmdObj.GetCardStatus()

            self.__sdCmdObj.Cmd7()

            # Get Card Status and Verify Trans State
            self.__dvtLib.Check_Card_Trans_State(Trans= 1)

            #Call Utility_CMD23_Write
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call Utility_CMD23_Write script")

            g_localVars = {}
            g_localVars["MaxLba"] = self.__cardMaxLba
            g_localVars["CMD23StartBlock"] = cmd23Variables["CMD23StartBlock"]
            g_localVars["CMD23BlockCount"] = cmd23Variables["CMD23BlockCount"]
            g_localVars["CMD23DataType"]   = cmd23Variables ["CMD23DataType"]
            g_localVars["CMD23VerifyWriteFlag"]   = cmd23Variables ["CMD23VerifyWriteFlag"]
            g_localVars["PredefineNumBlkFlag"]   = cmd23Variables ["PredefineNumBlkFlag"]
            g_localVars["PredefinedNumOfBlkCnt"] = cmd23Variables['PredefinedNumOfBlkCnt']
            g_localVars["IgnorePredefinedBlockCnt"] =  cmd23Variables['IgnorePredefinedBlockCnt']
            blkCountCMD23 = self.__Utility_CMD23Write.Run(g_localVars["CMD23StartBlock"],  g_localVars["CMD23BlockCount"],
                                                            g_localVars["PredefinedNumOfBlkCnt"], g_localVars["CMD23DataType"],usePreDefBlkCount= True)

            transfer_state_loop = transfer_state_loop + 1

        program_state_loop = 0

        while program_state_loop < 6:

            ########Test CMD23 in Program state
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Test CMD23 in Programm state with loop %d\n" % program_state_loop)

            #Put the card in Program state

            # Call globalInitCard
            globalProjectValues = self.__sdCmdObj.DoBasicInit()

            # Select Card
            #Card is already selected. Hence no need to send "self.__sdCmdObj.Cmd7()" cmd.

            # Get Card Status and Verify Trans State
            #self.__dvtLib.Check_Card_Trans_State(Trans= 1)

            # Single Command, Cmd32
            self.__sdCmdObj.Cmd32(StartLBA = 0)

            # Single Command, Cmd33
            self.__sdCmdObj.Cmd33(EndLBA = U - 1)

            # Single Command, Cmd38
            status = self.__sdCmdObj.Cmd38(expectPrgState = True)

            if status.count("CURRENT_STATE:Prg") > 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card is in Programmed state\n")
            else:
                raise ValidationError.TestFailError(self.fn, "Card not in Programmed state\n")

            # Check the CMD23 status
            try:
                self.__dvtLib.SingleCommand(OPCode=23, Argument = 0x2, ResponseType=sdcmdWrap.TYPE_RESP._R1, DataTransfer=sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_IS_NOT_RESPONDING", Operation_Name = "SingleCommand")
                program_state_loop = program_state_loop + 1
                continue
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING failure is not occured")

        disable_state_loop =0
        while disable_state_loop < 6:
            ########Test CMD23 in Deselect state
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Test CMD23 in Disbale state with loop %d\n" % disable_state_loop)

            # Call globalInitCard
            globalProjectValues = self.__sdCmdObj.DoBasicInit()

            # Select Card
             #Card is already selected. Hence no need to send "self.__sdCmdObj.Cmd7()" cmd.

            # Get Card Status and Verify Trans State
            self.__dvtLib.Check_Card_Trans_State(Trans=1)

            # Call globalSetBusModee
            self.__globalSetBusMode.Run(globalProjectValues)

            # Select Card
             #Card is already selected. Hence no need to send "self.__sdCmdObj.Cmd7()" cmd.

            # Single Command, Cmd32
            self.__sdCmdObj.Cmd32(StartLBA = 0)
            # Single Command, Cmd33
            self.__sdCmdObj.Cmd33(EndLBA = U - 1)

            # Single Command, Cmd38
            self.__sdCmdObj.Cmd38(expectPrgState = True)

            # Move card from prg state to dis state
            try:
                self.__sdCmdObj.Cmd7(True)
            except ValidationError.CVFGenericExceptions as exc:
                raise ValidationError.TestFailError(self.fn, "Expected as card cannot be addressed in prg state\n")

            # Verify for Dis state
            if self.__sdCmdObj.GetCardStatus().count("CURRENT_STATE:Dis") > 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card is in Dis state \n")
            else:
                raise ValidationError.TestFailError(self.fn, "Card not in Dis state \n")

            # Delay 5000ms = 5 sec
            time.sleep(5)

            # Single Command, Cmd23
            try:
                self.__dvtLib.SingleCommand(OPCode=23, Argument = 0x2, ResponseType=sdcmdWrap.TYPE_RESP._R1, DataTransfer=sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_IS_NOT_RESPONDING", Operation_Name = "SingleCommand")
                disable_state_loop = disable_state_loop + 1
                continue
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING failure is not occured")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + " Execution Completed " + "-" * 20 + "\n")
        return 0 # END_OF_SCRIPT

    # CVF Hook Function: [Testcase Should start with "test_"]
    def test_CMD23_TC009_StateTest(self):  # [Same in xml tag: <Test name="test_CMD23_TC009_StateTest">]

        # Calling Testcase logic
        self.Run()

# Testcase Class - Ends