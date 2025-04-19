"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : HCSD_V2_TC013_1_1_1_18.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : HCSD_V2_TC013_1_1_1_18.py
# DESCRIPTION                    : Module to Test OCR values In Power Cycle HV
# PRERQUISTE                     : HCSD_V2_UT01_AddressForWriteRead.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=HCSD_V2_TC013_1_1_1_18 --isModel=false --enable_console_log=1 --adapter=0
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
    from builtins import *

# SDDVT - Dependent TestCases
import HCSD_V2_UT01_AddressForWriteRead as AddressForWriteRead

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
import SDDVT.Config_SD.ConfigSD_UT011_GlobalSetLSHostFreq as GlobalSetLSHostFreq
import SDDVT.Config_SD.ConfigSD_UT014_GlobalSetTO as GlobalSetTO
import SDDVT.Config_SD.ConfigSD_UT006_GlobalSetVolt as GlobalSetVolt
import SDDVT.Config_SD.ConfigSD_UT012_GlobalSetResetFreq as GlobalSetResetFreq

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

# Testcase Utility Class - Begins
class HCSD_V2_TC013_1_1_1_18(customize_log):
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
        self.__GlobalSetResetFreq = GlobalSetResetFreq.globalSetResetFreq(self.vtfContainer)
        self.__globalSetLSHostFreq = GlobalSetLSHostFreq.globalSetLSHostFreq(self.vtfContainer)
        self.__globalSetTO = GlobalSetTO.globalSetTO(self.vtfContainer)
        self.__globalSetVolt = GlobalSetVolt.globalSetVolt(self.vtfContainer)
        self.__AddressForWriteRead = AddressForWriteRead.HCSD_V2_UT01_AddressForWriteRead(self.vtfContainer)


    # Testcase Utility Logic - Starts
    def Run(self):
        """
        Name : Run
        """

        # Initialize the SD card
        globalProjectConfVar = self.__sdCmdObj.DoBasicInit()

        configPatternFiledInCMD8 = int(globalProjectConfVar["configPatternFiledInCMD8"])
        globalVOLAValue = int(globalProjectConfVar["globalVOLAValue"])
        globalCardRCA = int(globalProjectConfVar['globalCardRCA'])

        # Run globalSetTO
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetTO")
        self.__globalSetTO.Run()

        # Run globalSetVolt
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetVolt")
        self.__globalSetVolt.Run(globalProjectConfVar)

        globalOCRArgValue = int(self.__config.get("globalOCRArgValue"))
        globalOCRResValue = int(self.__config.get("globalOCRResValue"))
        globalCardVoltage = (self.__config.get('globalCardVoltage'))

        cmd8_arg = (globalVOLAValue << 8) | (configPatternFiledInCMD8)

        # *********Soft Reset*********
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*********Soft Reset*********")

        #***Reserved Bits: 24-29 = Random ; OCR Bits: 15-23 = 0xFF8 ; Reserved Bits: 8-14 = Random; Reserved Bit: 7 = 0/1;  Reserved Bits: 0-6 = Random***
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Reserved Bits: 24-29 = Random ; OCR Bits: 15-23 = 0xFF8 ; Reserved Bits: 8-14 = Random; Reserved Bit: 7 = 0/1;  Reserved Bits: 0-6 = Random***")

        Reserved0_6 = random.randrange(0, 128)
        Reserved8_14 = (random.randrange(0, 128)) << 8
        Ocr15_23 = (0x1FF) << 15
        Reserved24_29 = (random.randrange(0, 64)) << 24
        BusyHCS30_31 = 1 << 30  # HCS Bit = 1  --> High Capacity card

        Reserved7 = 0
        if (globalCardVoltage == "LV"):
            Reserved7 = (1) << 7

        ocr = (Reserved0_6 | Reserved7 | Reserved8_14 | Ocr15_23 | Reserved24_29 | BusyHCS30_31)

        # RESET card to verify card is in Inactive state.
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "To verify card is in Inactive state.")
        try:
            self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=ocr, cardSlot=globalCardRCA, sendCmd8=True, initInfo=None,
                                rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True, bSendCMD58=False, version=0x0,
                                VOLA=globalVOLAValue, cmdPattern=configPatternFiledInCMD8, reserved=0x0,
                                expOCRVal=None)
        except ValidationError.CVFGenericExceptions as exc:
            self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "Reset")
        else:
            raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING error not occurred")

        # Verify card moved to Inactiv state - Soft Reset with valid OCR did not reset the card!
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Verify card moved to Inactiv state - Soft Reset with valid OCR did not reset the card!")
        try:
            self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=globalOCRArgValue, cardSlot=globalCardRCA, sendCmd8=True,
                                initInfo=None, rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True, bSendCMD58=False,
                                version=0x0, VOLA=globalVOLAValue, cmdPattern=configPatternFiledInCMD8, reserved=0x0,
                                expOCRVal=None)
        except ValidationError.CVFGenericExceptions as exc:
            self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "Reset")
        else:
            raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING error not occurred")

        # Power Off and On
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        # Reset card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RESET card and IDENTIFICATION of the card")
        self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=globalOCRArgValue, cardSlot=globalCardRCA, sendCmd8=True,
                            initInfo=None, rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True, bSendCMD58=False,
                            version=0x0, VOLA=globalVOLAValue, cmdPattern=configPatternFiledInCMD8, reserved=0x0,
                            expOCRVal=globalOCRResValue)

        # SwitchVolt (CMD11): to 1.8 v
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SwitchVolt (CMD11): to 1.8 v, timeToClockOff=0 ms, clockOffPeriod=5 ms")
        self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)

        # Identification of the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification of the card")
        self.__dvtLib.Identification()

        # Set bus width as 4
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set bus width as 4")
        self.__dvtLib.SetBusWidth(busWidth = 4)

        # Run AddressForWriteRead - Write & Read random address with random blockcount
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : AddressForWriteRead")
        self.__AddressForWriteRead.Run()

        # *********Power Cycle Reset*********
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*********Power Cycle Reset*********")

        # Power Off and On
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        # Set frequency to 300 KHz
        self.__GlobalSetResetFreq.Run()

        # Set RCA
        self.__sdCmdObj.SetrelativeCardAddress()
        sdcmdWrap.SetCardRCA(0)

        self.__sdCmdObj.Cmd8(argVal = cmd8_arg)

        #***Reserved Bits: 24-29 = Random ; OCR Bits: 15-23 = 0xFF8 ; Reserved Bits: 8-14 = Random; Reserved Bit: 7 = 0;  Reserved Bits: 0-6 = Random***
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Reserved Bits: 24-29 = Random ; OCR Bits: 15-23 = 0xFF8 ; Reserved Bits: 8-14 = Random; Reserved Bit: 7 = 0;  Reserved Bits: 0-6 = Random***")

        Reserved0_6 = random.randrange(0, 128)
        Reserved8_14 = (random.randrange(0, 128)) << 8
        Ocr15_23 = (0x1FF) << 15
        Reserved24_29 = (random.randrange(0, 64)) << 24
        BusyHCS30_31 = 1 << 30  # HCS Bit = 1  --> High Capacity card

        Reserved7 = 0
        if (globalCardVoltage == "LV"):
            Reserved7 = (1) << 7

        ocr = (Reserved0_6 | Reserved7 | Reserved8_14 | Ocr15_23 | Reserved24_29 | BusyHCS30_31)

        self.__sdCmdObj.Cmd55(setRCA=True)
        try:
            last_resp = self.__sdCmdObj.ACmd41(argVal=ocr, computedarg=True)
        except ValidationError.CVFGenericExceptions as exc:
            self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "ACmd41")
        else:
            raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING error not occurred")

        # RESET card to verify card is in Inactive state.
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "To verify card is in Inactive state.")
        try:
            self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=globalOCRArgValue, cardSlot=globalCardRCA, sendCmd8=True, initInfo=None,
                                rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True, bSendCMD58=False, version=0x0,
                                VOLA=globalVOLAValue, cmdPattern=configPatternFiledInCMD8, reserved=0x0,
                                expOCRVal=None)
        except ValidationError.CVFGenericExceptions as exc:
            self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "Reset")
        else:
            raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING error not occurred")

        # Power Off and On
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        # Set frequency to 300 KHz
        self.__GlobalSetResetFreq.Run()

        # Set RCA
        self.__sdCmdObj.SetrelativeCardAddress()
        sdcmdWrap.SetCardRCA(0)

        # Run cmd8
        last_resp = self.__sdCmdObj.Cmd8(argVal = 0x1AA)

        # Run loop Cmd55 and Acmd41 till the condition ((last_resp & 0x80) != 0x0) returns False
        while True: # Set lable R_1
            self.__sdCmdObj.Cmd55(setRCA=True)
            last_resp = self.__sdCmdObj.ACmd41(argVal=globalOCRArgValue, computedarg=True)
            if (last_resp & 0x80) != 0x0: # 0x80(BusyBit) is considered instead of 0x80000000
                break

        # CCS=0x40 is considered instead of 0x40000000
        CCS = 0x40
        if ((last_resp & CCS) == 0x0):  # Verify CCS Bit = 1 in ACMD 41 Responce
            raise ValidationError.TestFailError(self.fn, "CCS Bit = 0 in ACMD 41 Responce - Expected value of  1!")

        # Set card as high capacity
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set card as high capacity")
        self.__dvtLib.SetCardCap(hiCap=True)    # Adjust drivers to HC card

        # SET SD Mode
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SET SD Mode")
        # self.__dvtLib.SetSdMmcCardMode(CardMode=2, SetMode=True)  # Commenting out this line as this SDDVT package is only for SD.

        # SwitchVolt (CMD11): to 1.8 v
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SwitchVolt (CMD11): to 1.8 v, timeToClockOff=0 ms, clockOffPeriod=5 ms")
        self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)

        # Identification of the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification of the card")
        self.__dvtLib.Identification()

        # Set bus width as 4
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set bus width as 4")
        self.__dvtLib.SetBusWidth(busWidth = 4)

        # Run globalSetLSHostFreq
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetLSHostFreq")
        self.__globalSetLSHostFreq.Run()

        # Run AddressForWriteRead - Write & Read random address with random blockcount
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : AddressForWriteRead")
        self.__AddressForWriteRead.Run()

        # *********Power Cycle & CMD0 Reset*********
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*********Power Cycle & CMD0 Reset*********")

        # Power Off and On
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        #***Reserved Bits: 24-29 = Random ; OCR Bits: 15-23 = 0xFF8 ; Reserved Bits: 8-14 = Random; Reserved Bit: 7 = 0;  Reserved Bits: 0-6 = Random***
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Reserved Bits: 24-29 = Random ; OCR Bits: 15-23 = 0xFF8 ; Reserved Bits: 8-14 = Random; Reserved Bit: 7 = 0;  Reserved Bits: 0-6 = Random***")

        Reserved0_6 = random.randrange(0, 128)
        Reserved8_14 = (random.randrange(0, 128)) << 8
        Ocr15_23 = (0x1FF) << 15
        Reserved24_29 = (random.randrange(0, 64)) << 24
        BusyHCS30_31 = 1 << 30

        Reserved7 = 0
        if (globalCardVoltage == "LV"):
            Reserved7 = (1) << 7

        ocr = (Reserved0_6 | Reserved7 | Reserved8_14 | Ocr15_23 | Reserved24_29 | BusyHCS30_31)

        # Reset the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RESET card and IDENTIFICATION of the card")
        try:
            self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=ocr, cardSlot=globalCardRCA, sendCmd8=True,
                                initInfo=None, rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True, bSendCMD58=False,
                                version=0x0, VOLA=globalVOLAValue, cmdPattern=configPatternFiledInCMD8, reserved=0x0,
                                expOCRVal=None)
        except ValidationError.CVFGenericExceptions as exc:
            self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "Reset")
        else:
            raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING error not occurred")

        # Verify card moved to Inactive state - Soft Reset with valid OCR did not reset the card!
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RESET card and IDENTIFICATION of the card")
        try:
            self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=globalOCRArgValue, cardSlot=globalCardRCA, sendCmd8=True,
                                initInfo=None, rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True, bSendCMD58=False,
                                version=0x0, VOLA=globalVOLAValue, cmdPattern=configPatternFiledInCMD8, reserved=0x0,
                                expOCRVal=None)
        except ValidationError.CVFGenericExceptions as exc:
            self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "Reset")
        else:
            raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING error not occurred")

        # Power Off and On
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        # Reset the card
        self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=globalOCRArgValue, cardSlot=globalCardRCA, sendCmd8=True,
                            initInfo=None, rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True, bSendCMD58=False,
                            version=0x0, VOLA=globalVOLAValue, cmdPattern=configPatternFiledInCMD8, reserved=0x0,
                            expOCRVal=globalOCRResValue)

        # SwitchVolt (CMD11): to 1.8 v
        self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)

        # Identification
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "IDENTIFICATION : SD card")
        self.__dvtLib.Identification()

        # Set bus width as 1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set bus width as 1")
        self.__dvtLib.SetBusWidth(busWidth = 1)

        # Run AddressForWriteRead - Write & Read random address with random blockcount
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : AddressForWriteRead")
        self.__AddressForWriteRead.Run()

        return 0

    # Testcase Utility Logic - Ends
# Testcase Utility Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_HCSD_V2_TC013_1_1_1_18(self):
        obj = HCSD_V2_TC013_1_1_1_18(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
