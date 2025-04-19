"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : UHS_SD3_TC003_CMD11_State_Test.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : UHS_SD3_TC003_CMD11_State_Test.py
# DESCRIPTION                    : Reset Utility
# PRERQUISTE                     : UHS_SD3_UT02_Reset.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=UHS_SD3_TC003_CMD11_State_Test --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : Nov-2022
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
    from builtins import range
    from builtins import *

# SDDVT - Dependent TestCases
import UHS_SD3_UT02_Reset as ResetUtil

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
import SDDVT.Config_SD.ConfigSD_UT003_GlobalInitSDCard as GlobalInitSDCard
import SDDVT.Config_SD.ConfigSD_UT007_GlobalSetBusMode as GlobalSetBusMode

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
class UHS_SD3_TC003_CMD11_State_Test(customize_log):
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
        self.__globalInitSDCard = GlobalInitSDCard.globalInitSDCard(self.vtfContainer)
        self.__globalSetBusMode = GlobalSetBusMode.GlobalSetBusMode(self.vtfContainer)
        self.__UtilityReset = ResetUtil.UHS_SD3_UT02_Reset(self.vtfContainer)


    # Testcase logic - Starts
    def Run(self):

        # Initialize the SD card
        globalProjectConfVar = self.__sdCmdObj.DoBasicInit()

        U = self.__cardMaxLba

        # Set label IDLE_STATE
        for Loop in range(0, 6):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "IDLE_STATE loop count is 6. Current iteration is %s" % (Loop + 1))

            #Set Power off
            sdcmdWrap.SetPower(0)

            #Set Power On
            sdcmdWrap.SetPower(1)

            # BASIC COMMAND FPGA RESET
            self.__dvtLib.BasicCommandFPGAReset(False)

            # CMD 0 - Issue Command
            self.__sdCmdObj.Cmd0()

            # CMD 11 - Issue Command
            self.__sdCmdObj.Cmd11(ForceSwitch = True)

        # Set label READY_STATE
        for Loop in range(0, 6):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "READY_STATE loop count is 6. Current iteration is %s" % (Loop + 1))

            #Set Power off
            sdcmdWrap.SetPower(0)

            #Set Power On
            sdcmdWrap.SetPower(1)

            #Reset
            globalOCRResValue = int(globalProjectConfVar['globalOCRResValue'])
            self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.Sd, ocr = 0x41FF8000, cardSlot=0x1, sendCmd8=True,
                                initInfo=None, rca=0x0, time = 0x0, sendCMD0 = True, bHighCapacity=True,
                                bSendCMD58=False, version=0x0, VOLA=0x1, cmdPattern=0xAA, reserved=0x0,
                                expOCRVal=globalOCRResValue)

            #SwitchVolt_CMD11
            try:
                self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)
            except ValidationError.CVFGenericExceptions as exc:
                self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Switch Volt to 1.8V is expected since S1.8A=0 but tried to switch and remains in 3.3V")
                raise ValidationError.TestFailError(self.fn, "Switch Volt to 1.8V is expected since S1.8A=0 but tried to switch and remains in 3.3V")

        # Set label IDENT_STATE
        for Loop in range(0, 6):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "IDENT_STATE loop count is 6. Current iteration is %s" % (Loop + 1))

            #Set Power off
            sdcmdWrap.SetPower(0)

            #Set Power On
            sdcmdWrap.SetPower(1)

            self.__globalInitSDCard.Run(globalProjectConfVar)

            #Call Cmd 2
            self.__sdCmdObj.Cmd2()

            #Call Cmd 11
            self.__sdCmdObj.Cmd11(ForceSwitch=True)

        # Set label STBY_STATE
        for Loop in range(0, 6):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "STBY_STATE loop count is 6. Current iteration is %s" % (Loop + 1))

            # Power On, OFF and Call globalInitSDCard
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)
            self.__globalInitSDCard.Run(globalProjectConfVar)

            # Card Identification
            self.__dvtLib.Identification()

            # Get status
            self.__dvtLib.CardStatus_Check({gvar.Card_Status_Fields.CURRENT_STATE_Stby : 1, gvar.Card_Status_Fields.READY_FOR_DATA : 1},
                                           "Card is in stand-by state and ready for data", "Card is not in stand-by state and ready for data")

            #Call Cmd 11
            self.__sdCmdObj.Cmd11(ForceSwitch=True)

        # Set label TRAN_STATE
        for Loop in range(0, 6):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TRAN_STATE loop count is 6. Current iteration is %s" % (Loop + 1))

            # Power On, OFF and Call globalInitSDCard
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)

            self.__globalInitSDCard.Run(globalProjectConfVar)

            # Card Identification
            self.__dvtLib.Identification()

            # Select card
            self.__dvtLib.SelectCard()

            # Get status
            self.__dvtLib.CardStatus_Check({gvar.Card_Status_Fields.CURRENT_STATE_Tran : 1, gvar.Card_Status_Fields.READY_FOR_DATA : 1},
                                           "Card is in trans state and ready for data", "Card is not in trans state and ready for data")

            #Call Cmd 11
            self.__sdCmdObj.Cmd11(ForceSwitch=True)

            try:
                self.__sdCmdObj.GetCardStatus()
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, "CARD_ILLEGAL_CMD", "CMD13")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_ILLEGAL_CMD error not occurred")

        # Set label GO_PRG_STATE
        for Loop in range(0, 6):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "GO_PRG_STATE loop count is 6. Current iteration is %s" % (Loop + 1))

            # Call globalInitCard
            globalProjectConfVar = self.__sdCmdObj.DoBasicInit()

            # Get card status
            self.__sdCmdObj.GetCardStatus()

            self.__dvtLib.SelectCard()

            # Single Command, Cmd32
            self.__sdCmdObj.Cmd32(StartLBA = 0x0)

            # Single Command, Cmd33
            self.__sdCmdObj.Cmd33(EndLBA = U-0x1)

            # Single Command, Cmd38
            self.__sdCmdObj.Cmd38(expectPrgState = True)

            # Get Status and check for card ready
            self.__dvtLib.CardStatus_Check({gvar.Card_Status_Fields.CURRENT_STATE_Prg : 1}, "Card is in programming state", "Card is not in programming state")

            #Call Cmd 11
            self.__sdCmdObj.Cmd11(ForceSwitch=True)

            try:
                self.__sdCmdObj.GetCardStatus()
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, "CARD_ILLEGAL_CMD", "CMD13")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_ILLEGAL_CMD error not occurred")

        # Set label GO_DIS_STATE
        for Loop in range(0, 6):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "GO_DIS_STATE loop count is 6. Current iteration is %s" % (Loop + 1))

            # Call globalInitCard
            globalProjectConfVar = self.__sdCmdObj.DoBasicInit()

            self.__dvtLib.SelectCard()

            # Get card status
            self.__sdCmdObj.GetCardStatus()

            # Call script globalSetBusMode
            self.__globalSetBusMode.Run(globalProjectConfVar)

            self.__dvtLib.SelectCard()

            # Single Command, Cmd32
            self.__sdCmdObj.Cmd32(StartLBA = 0x0)

            # Single Command, Cmd33
            self.__sdCmdObj.Cmd33(EndLBA = U-0x1)

            # Single Command, Cmd38
            self.__sdCmdObj.Cmd38(expectPrgState = True)

            #Call Cmd 7
            try:
                self.__sdCmdObj.Cmd7(deSelect = True)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "CMD7")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected 'CARD_IS_NOT_RESPONDING' error is not occured for CMD7")

            # Verify for Dis state
            self.__dvtLib.CardStatus_Check(Expected_Status = {"CURRENT_STATE:Dis": 1}, Pass_case = "Card is in Dis state", Fail_case = "Card is not in Dis state")

            # Wait for 2 seconds
            time.sleep(2)

            #Call Cmd 11
            self.__sdCmdObj.Cmd11(ForceSwitch=True)

        return 0
    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_UHS_SD3_TC003_CMD11_State_Test(self):
        obj = UHS_SD3_TC003_CMD11_State_Test(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
