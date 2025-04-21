"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : HCSD_V2_TC014_1_1_1_20a.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : HCSD_V2_TC014_1_1_1_20a.py
# DESCRIPTION                    : Module to Test CMD 55 Before CMD8 during Soft Reset, Power Cycle Reset, during Power Cycle & CMD 0 Reset
# PRERQUISTE                     : HCSD_V2_UT01_AddressForWriteRead.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=HCSD_V2_TC014_1_1_1_20a --isModel=false --enable_console_log=1 --adapter=0
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
import SDDVT.Config_SD.ConfigSD_UT005_GlobalPreTestingSettings as globalPreTestingSettings
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
class HCSD_V2_TC014_1_1_1_20a(customize_log):
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
        self.__globalPreTestSettingsObj = globalPreTestingSettings.globalPreTestingSettings(self.vtfContainer)
        self.__globalSetLSHostFreq = GlobalSetLSHostFreq.globalSetLSHostFreq(self.vtfContainer)
        self.__globalSetTO = GlobalSetTO.globalSetTO(self.vtfContainer)
        self.__globalSetVolt = GlobalSetVolt.globalSetVolt(self.vtfContainer)
        self.__AddressForWriteRead = AddressForWriteRead.HCSD_V2_UT01_AddressForWriteRead(self.vtfContainer)


    # Testcase Utility Logic - Starts
    def Run(self):
        """
        Name : Run
        """

        # Global values from globalPreTestingSettings file
        globalProjectConfVar = self.__globalPreTestSettingsObj.Run()

        # Get the Global PreTest Settings values
        globalVOLAValue = int(globalProjectConfVar['globalVOLAValue'])
        globalOCRArgValue = int(globalProjectConfVar['globalOCRArgValue'])

        # Run globalSetTO
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetTO")
        self.__globalSetTO.Run()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalSetTO CALL Completed\n")

        # Run globalSetVolt
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetVolt")
        self.__globalSetVolt.Run(globalProjectConfVar)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalSetVolt CALL Completed\n")

        #***Test CMD55 Before CMD8 during Soft Reset***
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Test CMD55 Before CMD8 during Soft Reset***")

        # Set frequency to 300 KHz
        self.__GlobalSetResetFreq.Run()

        # SET RCA
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SET RCA")
        self.__sdCmdObj.SetrelativeCardAddress()
        sdcmdWrap.SetCardRCA(0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "setting of RCA value completed\n")

        # Run cmd0()
        self.__sdCmdObj.Cmd0()

        # Variable Declaration Operation
        pattern = random.randrange(0, 256)
        reserve = random.randrange(0, 1048576)
        arg = (((globalVOLAValue << 8) | pattern) | (reserve << 12))
        exp = ((globalVOLAValue << 8) | pattern)

        # Run cmd55()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RUNNING Cmd55()")
        self.__sdCmdObj.Cmd55(setRCA=True)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd55() Execution completed\n")

        # Run cmd8()
        last_resp = self.__sdCmdObj.Cmd8(argVal = arg)
        last_resp = ((last_resp.GetOneByteToInt(3) << 8) | last_resp.GetOneByteToInt(4))    # Bitwise or operation with the response to get the first bit of 2nd byte
        if (last_resp != exp):
            # CMD8 Responce is incorrect!
            raise ValidationError.TestFailError(self.fn, "CMD8 Responce is incorrect!")

        # Run loop Cmd55 and Acmd41 till the condition ((last_resp & 0x80) != 0x0) returns False
        while True: # Set lable R_1
            self.__sdCmdObj.Cmd55(setRCA=True)
            last_resp = self.__sdCmdObj.ACmd41(argVal=globalOCRArgValue, computedarg=True)
            if (last_resp & 0x80) != 0x0: # 0x80(BusyBit) is considered instead of 0x80000000
                break

        # CCS=0x40 is considered instead of 0x40000000
        CCS = 0x40
        if ((last_resp & CCS) == 0x0):  # Verify CCS Bit = 1 in ACMD 41 Responce
            raise ValidationError.TestFailError(self.fn, "CCS Bit = 0 in ACMD41 Responce - Expected value of 1!")

        # set High Capacity of the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set High Capacity of the card")
        self.__dvtLib.SetCardCap(hiCap=True)    # Adjust drivers to HC card

        # Set card mode as SD
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set card mode as SD")
        # self.__dvtLib.SetSdMmcCardMode(CardMode=2)    # Commenting out this line as this SDDVT package is only for SD.

        # Identification of the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification of the card")
        self.__dvtLib.Identification()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Identification completed\n")

        # Run globalSetLSHostFreq
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetLSHostFreq")
        self.__globalSetLSHostFreq.Run()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalSetLSHostFreq CALL got Completed\n")

        # Run AddressForWriteRead - Write & Read random address with random blockcount
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : AddressForWriteRead")
        self.__AddressForWriteRead.Run()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "AddressForWriteRead CALL Completed")

        #***Test CMD55 Before CMD8 during Power Cycle Reset***
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Test CMD55 Before CMD8 during Power Cycle Reset***")

        # POWER : OFF and ON
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        # Set frequency to 300 KHz
        self.__GlobalSetResetFreq.Run()

        # Set RCA
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SET RCA")
        self.__sdCmdObj.SetrelativeCardAddress()
        sdcmdWrap.SetCardRCA(0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "setting of RCA value completed\n")

        # Run cmd55()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RUNNING Cmd55()")
        self.__sdCmdObj.Cmd55(setRCA=True)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd55() Execution completed\n")

        # Variable Declaration Operation
        pattern = random.randrange(0, 256)
        reserve = random.randrange(0, 1048576)
        arg = (((globalVOLAValue << 8) | pattern) | (reserve << 12))
        exp = ((globalVOLAValue << 8) | pattern)

        # Run cmd8()
        last_resp = self.__sdCmdObj.Cmd8(argVal = arg)
        last_resp = ((last_resp.GetOneByteToInt(3) << 8) | last_resp.GetOneByteToInt(4))    # Bitwise or operation with the response to get the first bit of 2nd byte
        if (last_resp != exp):
            # CMD8 Responce is incorrect!
            raise ValidationError.TestFailError(self.fn, "CMD8 Responce is incorrect!")

        # Run loop Cmd55 and Acmd41 till the condition ((last_resp & 0x80) != 0x0) returns False
        while True: # Set lable R2
            self.__sdCmdObj.Cmd55(setRCA=True)
            last_resp = self.__sdCmdObj.ACmd41(argVal=globalOCRArgValue, computedarg=True)
            if (last_resp & 0x80) != 0x0: # 0x80(BusyBit) is considered instead of 0x80000000
                break

        # CCS=0x40 is considered instead of 0x40000000
        CCS = 0x40
        if ((last_resp & CCS) == 0x0):  # Verify CCS Bit = 1 in ACMD 41 Responce
            raise ValidationError.TestFailError(self.fn, "CCS Bit = 0 in ACMD41 Responce - Expected value of 1!")

        # set High Capacity of the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set High Capacity of the card")
        self.__dvtLib.SetCardCap(hiCap=True)    # Adjust drivers to HC card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Capacity got changed to High Capacity\n")

        # Set card mode as SD
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set card mode as SD")
        # self.__dvtLib.SetSdMmcCardMode(CardMode=2)    # Commenting out this line as this SDDVT package is only for SD.
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card mode got changed to SD\n")

        # Identification of the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Identification Test begins")
        self.__dvtLib.Identification()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Identification Test Completed\n")

        # Run globalSetLSHostFreq
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetLSHostFreq")
        self.__globalSetLSHostFreq.Run()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetLSHostFreq CALL Completed\n")

        # Run AddressForWriteRead - Write & Read random address with random blockcount
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : AddressForWriteRead")
        self.__AddressForWriteRead.Run()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "AddressForWriteRead CALL Completed")

        #***Test CMD55 Before CMD8 during Power Cycle & CMD0 Reset***
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Test CMD55 Before CMD8 during Power Cycle & CMD0 Reset***")

        # POWER : OFF and ON
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        # Set frequency to 300 KHz
        self.__GlobalSetResetFreq.Run()

        # Set RCA
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SET RCA")
        self.__sdCmdObj.SetrelativeCardAddress()
        sdcmdWrap.SetCardRCA(0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "setting of RCA value completed\n")

        # Run cmd0()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RUNNING Cmd55()")
        self.__sdCmdObj.Cmd0()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd55() Execution completed\n")

        # Variable Declaration Operation
        pattern = random.randrange(0, 256)
        reserve = random.randrange(0, 1048576)
        arg = (((globalVOLAValue << 8) | pattern) | (reserve << 12))
        exp = ((globalVOLAValue << 8) | pattern)

        # Run cmd55()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RUNNING Cmd55()")
        self.__sdCmdObj.Cmd55(setRCA=True)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd55() Execution completed\n")

        # Run cmd8()
        last_resp = self.__sdCmdObj.Cmd8(argVal = arg)
        last_resp = ((last_resp.GetOneByteToInt(3) << 8) | last_resp.GetOneByteToInt(4))    # Bitwise or operation with the response to get the first bit of 2nd byte
        if (last_resp != exp):
            # CMD8 Responce is incorrect!
            raise ValidationError.TestFailError(self.fn, "CMD8 Responce is incorrect!")

        # Run loop Cmd55 and Acmd41 till the condition ((last_resp & 0x80) != 0x0) returns False
        while True: # Set lable R3
            self.__sdCmdObj.Cmd55(setRCA=True)
            last_resp = self.__sdCmdObj.ACmd41(argVal=globalOCRArgValue, computedarg=True)
            if (last_resp & 0x80) != 0x0: # 0x80(BusyBit) is considered instead of 0x80000000
                break

        # CCS=0x40 is considered instead of 0x40000000
        CCS = 0x40
        if ((last_resp & CCS) == 0x0):  # Verify CCS Bit = 1 in ACMD 41 Responce
            raise ValidationError.TestFailError(self.fn, "CCS Bit = 0 in ACMD41 Responce - Expected value of 1!")

        # set High Capacity of the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set High Capacity of the card")
        self.__dvtLib.SetCardCap(hiCap=True)    # Adjust drivers to HC card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Capacity got changed to High Capacity\n")

        # Set card mode as SD
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set card mode as SD")
        # self.__dvtLib.SetSdMmcCardMode(CardMode=2)    # Commenting out this line as this SDDVT package is only for SD.
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card mode got changed to SD\n")

        # Identification of the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Identification Test begins")
        self.__dvtLib.Identification()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Identification Test Completed\n")

        # Run globalSetLSHostFreq
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetLSHostFreq")
        self.__globalSetLSHostFreq.Run()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetLSHostFreq CALL Completed\n")

        # Run AddressForWriteRead - Write & Read random address with random blockcount
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : AddressForWriteRead")
        self.__AddressForWriteRead.Run()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "AddressForWriteRead CALL Completed")

        return 0

    # Testcase Utility Logic - Ends
# Testcase Utility Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_HCSD_V2_TC014_1_1_1_20a(self):
        obj = HCSD_V2_TC014_1_1_1_20a(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
