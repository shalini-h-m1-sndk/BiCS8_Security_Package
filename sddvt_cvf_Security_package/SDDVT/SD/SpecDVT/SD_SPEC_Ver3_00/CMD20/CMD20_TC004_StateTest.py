"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : CMD20_CA01_SDMode.st3
# SCRIPTER SCRIPT                : CMD20_TC004_StateTest.st3
# CVF CALL ALL SCRIPT            : CMD20_CA01_SDMode.py
# CVF SCRIPT                     : CMD20_TC004_StateTest.py
# DESCRIPTION                    : The purpose of this test case is to assure that CMD20 is valid only in transfare state
# PRERQUISTE                     : CMD20_UT01_LoadCMD20_Variables.py, CMD20_UT02_GetSequence.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=CMD20_TC004_StateTest --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : Nov-2022
# UPDATED BY                     : Sushmitha P.S
# UPDATED DATE                   : 20-Jun-2024
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
import CMD20_UT01_LoadCMD20_Variables as LoadCMD20Variables
import CMD20_UT02_GetSequence as CMD20GetSequence

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
import SDDVT.Config_SD.ConfigSD_UT003_GlobalInitSDCard as globalInitSDCard
import SDDVT.Config_SD.ConfigSD_UT007_GlobalSetBusMode as globalSetBusMode

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
class CMD20_TC004_StateTest(customize_log):
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
        self.__globalInitSDCard = globalInitSDCard.globalInitSDCard(self.vtfContainer)
        self.__globalSetBusMode = globalSetBusMode.GlobalSetBusMode(self.vtfContainer)
        self.__LoadCMD20Variables = LoadCMD20Variables.CMD20_UT01_LoadCMD20_Variables(self.vtfContainer)
        self.__GetSequence = CMD20GetSequence.CMD20_UT02_GetSequence(self.vtfContainer)


    # Testcase logic - Starts
    def Run(self):
        """
        Name : Run
        Description: Assure that CMD20 is valid only in transfare state


        # Call script globalInitCard
        # Call Script LoadCmd20Variables Utility Script

        #########CMD20 Test in IDLE state#################
        # Power OFf, Power On
        # BASIC COMMAND FPGA RESET
        # SingleCommand, Cmd 0
        # SingleCommand, Cmd 20

        #########CMD20 Test in Ready state#################
        # Power OFf, Power On
        # SingleCommand, Cmd 0
        # Single Command, Cmd 55
        # ACMD41 with OCR
        # Single Command, Cmd 55
        # ACMD41
        # SingleCommand, Cmd 20

        #########CMD20 Test in Identification state#################
        # Power Off, Power On
        # Call globalInitCard
        # Single Command, Cmd2
        # SingleCommand, Cmd 20

        #########CMD20 Test in Standby state#################
        # Power Off and On
        # Call globalInitCard
        # Identify Card
        # Check SD Status, See that Card is in Stby Mode
        # SingleCommand, Cmd 20
        # Expect Sequence = 1, Call GetSequence

        #########CMD20 Test in Program state#################

        # Power Off and On
        # Call globalInitCard
        # Identify Card
        # Select Card
        # check Status, whether card is in Tran State
        # Expect Sequence =1, Call GetSequence
        # Call globalInitCard
        # check Status, whether card is in Tran State
        # Single Command, Cmd7
        # Single Command, Cmd32
        # Single Command, Cmd33
        # Single Command, Cmd38
        # Get Status
        # SingleCommand, Cmd 20

        #########CMD20 Test in Disable  state#################
        # Call globalInitCard
        # Select Card
        # Get Status
        # Call globalSetBusMode
        # Single Command, Cmd7
        # Single Command, Cmd32
        # Single Command, Cmd33
        # Single Command, Cmd38
        # Single Command, Cmd7
        # Single Command, Cmd13
        # Delay 5000ms
        # Single Command, Cmd20
        """

        # Initialize the SD card
        globalProjectValues = self.__sdCmdObj.DoBasicInit()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-"* 20 + " Execution Started "+ "-"* 20 + "\n")

        globalOCRArgValue = int(globalProjectValues['globalOCRArgValue'])

        U  = self.__cardMaxLba

        # Call Script LoadCmd20Variables Utility Script
        cmd20Variables = self.__LoadCMD20Variables.Run()

        idle_state_loop = 0
        while idle_state_loop < 5:
            #Test CMD20 in Idle state
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Test CMD20 in Idle state with loop %d\n"%idle_state_loop)

            # Set (no)Power, Power
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)

            # BASIC COMMAND FPGA RESET
            self.__dvtLib.BasicCommandFPGAReset(False)

            # SingleCommand, CMD0
            self.__sdCmdObj.Cmd0()

            try:
                self.__dvtLib.SingleCommand(OPCode=20, Argument = 0x1, ResponseType=sdcmdWrap.TYPE_RESP._R1, DataTransfer=sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_IS_NOT_RESPONDING", Operation_Name = "SingleCommand")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING failure is not occured")

            idle_state_loop = idle_state_loop + 1

        ready_state_loop = 0
        while ready_state_loop < 5:

            # Test CMD23 in Ready state
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Test CMD20 in Ready state with loop %d\n"% ready_state_loop)

            # Set (no)Power, Power
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)

            # BASIC COMMAND FPGA RESET
            self.__dvtLib.BasicCommandFPGAReset(False)

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
                self.__dvtLib.SingleCommand(OPCode=20, Argument = 0x1, ResponseType=sdcmdWrap.TYPE_RESP._R1, DataTransfer=sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_IS_NOT_RESPONDING", Operation_Name = "SingleCommand")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING failure is not occured")

            ready_state_loop = ready_state_loop + 1

        identification_loop = 0
        while identification_loop < 5:
            #Test CMD23 in Identification state
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Test CMD20 in Identification state with loop %d\n"% identification_loop)

            # Set No Power, Power
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)

            # Call globalInitCard
            self.__globalInitSDCard.Run(globalProjectValues)

            # Single Command, Cmd2
            self.__sdCmdObj.Cmd2()

            # SingleCommand, CMD20
            try:
                self.__dvtLib.SingleCommand(OPCode=20, Argument = 0x1, ResponseType=sdcmdWrap.TYPE_RESP._R1, DataTransfer=sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_IS_NOT_RESPONDING", Operation_Name = "SingleCommand")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING failure is not occured")

            identification_loop = identification_loop + 1

        standby_state_loop = 0
        while standby_state_loop < 5:
            ########Test CMD23 in Standby state
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Test CMD20 in StandBy state with loop %d\n"% standby_state_loop)

            # Set No Power, Power
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)

            # Call globalInitCard
            self.__globalInitSDCard.Run(globalProjectValues)

            # Identify Card, Exceutes from Step 19
            self.__dvtLib.Identification()

            # Check SD Status, See that Card is in Stby Mode
            self.__sdCmdObj.GetCardStatus()

            # SingleCommand, Cmd 20
            try:
                self.__dvtLib.SingleCommand(OPCode=20, Argument = 0x1, ResponseType=sdcmdWrap.TYPE_RESP._R1, DataTransfer=sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_IS_NOT_RESPONDING", Operation_Name = "SingleCommand")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING failure is not occured")

            # Call GetSequence Utility
            cmd20Variables["ExpectSequence"] = 1
            self.__GetSequence.Run(ExpectSequence = cmd20Variables["ExpectSequence"])
            standby_state_loop = standby_state_loop + 1

        transfer_state_loop = 0
        while transfer_state_loop < 5:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Test CMD20 in Transfer state with loop %d\n"% transfer_state_loop)

            # Set No Power, Power
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)

            # Call globalInitCard
            self.__globalInitSDCard.Run(globalProjectValues)

            # Identify Card, Exceutes from Step 19
            self.__dvtLib.Identification()

            # Check SD Status, See that Card is in Stby Mode
            self.__sdCmdObj.GetCardStatus()

            self.__sdCmdObj.Cmd7()

            # Get Card Status and Verify Trans State
            self.__dvtLib.Check_Card_Trans_State(Trans = 1)

            cmd20Variables["ExpectSequence"] = 1
            self.__GetSequence.Run(ExpectSequence = cmd20Variables["ExpectSequence"])
            transfer_state_loop = transfer_state_loop + 1

        program_state_loop = 0
        while program_state_loop < 5:

            ########Test CMD23 in Program state
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Test CMD20 in Programm state with loop %d\n"% program_state_loop)

            # Call globalInitCard
            globalProjectValues = self.__sdCmdObj.DoBasicInit()

            # Get Card Status and Verify Trans State
            self.__dvtLib.Check_Card_Trans_State(Trans = 1)

            # Single Command, Cmd32
            self.__sdCmdObj.Cmd32(StartLBA = 0)

            # Single Command, Cmd33
            self.__sdCmdObj.Cmd33(EndLBA = U - 1)

            # Single Command, Cmd38
            status = self.__sdCmdObj.Cmd38(expectPrgState = True)

            if status.count("CURRENT_STATE:Prg") > 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card is in Programming state\n")
            else:
                raise ValidationError.TestFailError(self.fn, "Card is not in Programming state\n")

            # Check the CMD23 status
            try:
                self.__dvtLib.SingleCommand(OPCode=20, Argument = 0x1, ResponseType=sdcmdWrap.TYPE_RESP._R1, DataTransfer=sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_IS_NOT_RESPONDING", Operation_Name = "SingleCommand")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING failure is not occured")

            program_state_loop = program_state_loop + 1

        disconnect_state_loop =0
        while disconnect_state_loop < 5:
            ########Test CMD23 in disconnect state
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Test CMD20 in disconnect state with loop %d\n"% disconnect_state_loop)

            # Call globalInitCard
            globalProjectValues = self.__sdCmdObj.DoBasicInit()

            # Select Card
            # Card is already selected. Hence no need to send "self.__sdCmdObj.Cmd7()"cmd.

            # Get Card Status and Verify Trans State
            self.__dvtLib.Check_Card_Trans_State(Trans = 1)

            # Call globalSetBusModee
            self.__globalSetBusMode.Run(globalProjectValues)

            # Select Card
            # Card is already selected. Hence no need to send "self.__sdCmdObj.Cmd7()"cmd.

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
                raise ValidationError.TestFailError(self.fn, "Expected as card can not be addressed in prg state\n")

            # Verify for Dis state
            if self.__sdCmdObj.GetCardStatus().count("CURRENT_STATE:Dis") > 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card is in Dis state\n")
            else:
                raise ValidationError.TestFailError(self.fn, "Card not in Dis state\n")

            # Delay 2000ms = 2 sec
            time.sleep(2)

            # Single Command, Cmd23
            try:
                self.__dvtLib.SingleCommand(OPCode=20, Argument = 0x1, ResponseType=sdcmdWrap.TYPE_RESP._R1, DataTransfer=sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_IS_NOT_RESPONDING", Operation_Name = "SingleCommand")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING failure is not occured")

            disconnect_state_loop = disconnect_state_loop + 1

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-"* 20 + "Execution Completed "+ "-"* 20 + "\n")
        return 0
    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_CMD20_TC004_StateTest(self):
        obj = CMD20_TC004_StateTest(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
