"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : HCSD_V2_TC007_1_1_1_8.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : HCSD_V2_TC007_1_1_1_8.py
# DESCRIPTION                    : Test CCS Bit default value with CMD0() and without CMD0()
# PRERQUISTE                     : HCSD_V2_UT01_AddressForWriteRead.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=HCSD_V2_TC007_1_1_1_8 --isModel=false --enable_console_log=1 --adapter=0
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
class HCSD_V2_TC007_1_1_1_8(customize_log):
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

        # Get global Pre-Setting values
        configPatternFiledInCMD8 = int(globalProjectConfVar["configPatternFiledInCMD8"])
        globalVOLAValue = int(globalProjectConfVar["globalVOLAValue"])

        # Run globalSetTO
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetTO")
        self.__globalSetTO.Run()

        # Run globalSetVolt
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetVolt")
        self.__globalSetVolt.Run(globalProjectConfVar)

        # Run globalSetLSHostFreq
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetLSHostFreq")
        self.__globalSetLSHostFreq.Run()

        cmd8_arg = ((globalVOLAValue << 8) | configPatternFiledInCMD8)
        exp = (globalVOLAValue << 8 | configPatternFiledInCMD8)
        globalOCRArgValue = int(self.__config.get("globalOCRArgValue"))
        globalOCRResValue = int(self.__config.get("globalOCRResValue"))
        globalCardRCA = int(globalProjectConfVar['globalCardRCA'])

        #***Test CCS Bit default value with CMD0***
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Test CCS Bit default value with CMD0***")

        # Power off and on
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        # Reset the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RESET card the card")
        self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=globalOCRArgValue, cardSlot=globalCardRCA, sendCmd8=True,
                            initInfo=None, rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True, bSendCMD58=False,
                            version=0x0, VOLA=globalVOLAValue, cmdPattern=configPatternFiledInCMD8, reserved=0,
                            expOCRVal=globalOCRResValue)

        # Identification of the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification of the card")
        self.__dvtLib.Identification()

        # Power Off and On
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        # Set frequency to 300 KHz
        self.__GlobalSetResetFreq.Run()

        # Set RCA
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : SetrelativeCardAddress")
        self.__sdCmdObj.SetrelativeCardAddress()
        sdcmdWrap.SetCardRCA(0)

        # Run cmd0, Cmd8, Cmd55, ACmd41
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RUNNING Cmd0, Cmd8, Cmd55, ACmd41")

        self.__sdCmdObj.Cmd0()

        last_resp = self.__sdCmdObj.Cmd8(argVal = cmd8_arg)
        last_resp = ((last_resp.GetOneByteToInt(3) << 8) | last_resp.GetOneByteToInt(4))    # Bitwise or operation with the response to get the first bit of 2nd byte
        if (last_resp != exp):
            # CMD8 Responce is incorrect!
            raise ValidationError.TestFailError(self.fn, "CMD 8 Responce is incorect - VOLA is incorrect!")

        self.__sdCmdObj.Cmd55(setRCA=True)
        last_resp = self.__sdCmdObj.ACmd41(argVal=globalOCRArgValue, computedarg = True)

        # CCS=0x40 is considered instead of 0x40000000
        CCS = 0x40
        if ((last_resp & CCS) != 0x0):
            raise ValidationError.TestFailError(self.fn, "CCS Bit in ACMD 41 Responce is not a default value!")

        # Run loop Cmd55 and Acmd41 till the condition ((last_resp & 0x80) != 0x0) returns False
        while True:
            self.__sdCmdObj.Cmd55(setRCA=True)
            last_resp = self.__sdCmdObj.ACmd41(argVal=globalOCRArgValue, computedarg=True)
            if (last_resp & 0x80) != 0x0: # 0x80(BusyBit) is considered instead of 0x80000000
                break

        # CCS=0x40 is considered instead of 0x40000000
        CCS = 0x40
        if ((last_resp & CCS) == 0x0):  # Verify CCS Bit = 1
            raise ValidationError.TestFailError(self.fn, "CCS Bit = 0 - Low Capacity card!")

        # Set card as high capacity
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set card as high capacity")
        self.__dvtLib.SetCardCap(hiCap=True)    # Adjust drivers to HC card

        # SET SD Mode
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SET SD Mode")
        # self.__dvtLib.SetSdMmcCardMode(CardMode=2, SetMode=True)  # Commenting out this line as this SDDVT package is only for SD.

        # Identification of card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "IDENTIFICATION : SD card")
        self.__dvtLib.Identification()

        # Run globalSetLSHostFreq
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetLSHostFreq")
        self.__globalSetLSHostFreq.Run()

        # Run AddressForWriteRead - Write & Read random address with random blockcount
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : AddressForWriteRead")
        self.__AddressForWriteRead.Run()

        #***Test CCS Bit default value without CMD0***
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Test CCS Bit default value without CMD0***")

        # Power Off and On
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        # Reset the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RESET card and IDENTIFICATION of the card")
        self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=globalOCRArgValue, cardSlot=globalCardRCA, sendCmd8=True,
                            initInfo=None, rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True, bSendCMD58=False,
                            version=0x0, VOLA=globalVOLAValue, cmdPattern=configPatternFiledInCMD8, reserved=0,
                            expOCRVal=globalOCRResValue)

        # Identification of the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification of the card")
        self.__dvtLib.Identification()

        # Power Off and On
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        # Set frequency to 300 KHz
        self.__GlobalSetResetFreq.Run()

        # Set RCA
        self.__sdCmdObj.SetrelativeCardAddress()
        sdcmdWrap.SetCardRCA(0)

        # Run Cmd8, cmd55 and acmd41
        last_resp = self.__sdCmdObj.Cmd8(argVal = cmd8_arg)
        last_resp = ((last_resp.GetOneByteToInt(3) << 8) | last_resp.GetOneByteToInt(4))    # Bitwise or operation with the response to get the first bit of 2nd byte
        if (last_resp != exp):
            # CMD8 Responce is incorrect!
            raise ValidationError.TestFailError(self.fn, "CMD 8 Responce is incorect - VOLA is incorrect!")

        self.__sdCmdObj.Cmd55(setRCA=True)
        last_resp = self.__sdCmdObj.ACmd41(argVal=globalOCRArgValue)

        # CCS=0x40 is considered instead of 0x40000000
        CCS = 0x40
        if ((last_resp & CCS) != 0x0):  # Verify CCS Bit = 0 in the first ACMD 41
            raise ValidationError.TestFailError(self.fn, "CCS Bit in ACMD 41 Responce is not a default value!")

        # Run loop Cmd55 and Acmd41 till the condition ((last_resp & 0x80) != 0x0) returns False
        while True:
            self.__sdCmdObj.Cmd55(setRCA=True)
            last_resp = self.__sdCmdObj.ACmd41(argVal=globalOCRArgValue, computedarg=True)
            if (last_resp & 0x80) != 0x0: # 0x80(BusyBit) is considered instead of 0x80000000
                break

        # CCS=0x40 is considered instead of 0x40000000
        CCS = 0x40
        if ((last_resp & CCS) == 0x0):  # Verify CCS Bit = 1
            raise ValidationError.TestFailError(self.fn, "CCS Bit = 0 - Low Capacity card!")

        # Set card as high capacity
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set card as high capacity")
        self.__dvtLib.SetCardCap(hiCap=True)    # Adjust drivers to HC card

        # SET SD Mode
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SET SD Mode")
        # self.__dvtLib.SetSdMmcCardMode(CardMode=2, SetMode=True)  # Commenting out this line as this SDDVT package is only for SD.

        # Identification of the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "IDENTIFICATION : SD card")
        self.__dvtLib.Identification()

        # Run globalSetLSHostFreq
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetLSHostFreq")
        self.__globalSetLSHostFreq.Run()

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
    def test_HCSD_V2_TC007_1_1_1_8(self):
        obj = HCSD_V2_TC007_1_1_1_8(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
