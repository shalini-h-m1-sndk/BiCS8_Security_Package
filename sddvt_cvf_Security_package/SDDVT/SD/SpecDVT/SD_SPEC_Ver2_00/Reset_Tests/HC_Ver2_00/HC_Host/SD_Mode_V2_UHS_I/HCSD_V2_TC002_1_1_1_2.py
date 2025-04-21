"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : HCSD_V2_TC002_1_1_1_2.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : HCSD_V2_TC002_1_1_1_2.py
# DESCRIPTION                    : Test CMD 8's out of sequence during Soft Reset, Power Cycle Reset, Power Cycle & CMD 0 Reset.
# PRERQUISTE                     : HCSD_V2_UT01_AddressForWriteRead.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=HCSD_V2_TC002_1_1_1_2 --isModel=false --enable_console_log=1 --adapter=0
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
import SDDVT.Config_SD.ConfigSD_UT013_GlobalSetSpeedMode as GlobalSetSpeedMode
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
class HCSD_V2_TC002_1_1_1_2(customize_log):
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
        self.__globalSetSpeedMode = GlobalSetSpeedMode.globalSetSpeedMode(self.vtfContainer)
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

        # Get the Global PreTest Settings values
        globalVOLAValue = int(globalProjectConfVar['globalVOLAValue'])
        configPatternFiledInCMD8 = int(globalProjectConfVar['configPatternFiledInCMD8'])
        globalOCRArgValue = int(globalProjectConfVar['globalOCRArgValue'])
        globalOCRResValue = int(globalProjectConfVar['globalOCRResValue'])

        # Run globalSetTO
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetTO")
        self.__globalSetTO.Run()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalSetTO CALL got Completed\n")

        # Run globalSetVolt
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetVolt")
        self.__globalSetVolt.Run(globalProjectConfVar)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalSetVolt CALL got Completed\n")

        # Set frequency to 300 KHz
        self.__GlobalSetResetFreq.Run()

        #***Test CMD 8's out of sequence during Soft Reset***
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Test CMD 8's out of sequence during Soft Reset***")

        # Variable declaration cmd8_arg needs to be passed in cmd8()
        cmd8_arg = ((globalVOLAValue << 8) | configPatternFiledInCMD8)

        # SET RCA
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SET RCA")
        self.__sdCmdObj.SetrelativeCardAddress()
        sdcmdWrap.SetCardRCA(0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "setting of RCA value completed\n")

        # Run cmd0, cmd8, cmd55, acmd41
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Run cmd0, cmd8, cmd55, acmd41")

        index = random.randrange(0, 4) + 1

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL: BasicCommandFPGAReset Begins")
        self.__dvtLib.BasicCommandFPGAReset(False)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL: BasicCommandFPGAReset Completed\n")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Run Cmd0()")
        self.__sdCmdObj.Cmd0()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd0() Execution successfull\n")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RUNNING Cmd8, Cmd55, ACmd41")

        for Repeat1_CMD8_SD_HIGH in range(0, index):    # Reapet CMD8 random number of iterations
            last_resp = self.__sdCmdObj.Cmd8(argVal = cmd8_arg)
            last_resp = ((last_resp.GetOneByteToInt(3) << 8) | last_resp.GetOneByteToInt(4))    # Bitwise or operation with the response to get the first bit of 2nd byte
            if (last_resp != cmd8_arg):
                # CMD8 Responce is incorrect!
                raise ValidationError.TestFailError(self.fn, "CMD8 Responce is incorrect!")

        last_resp = 0
        # Run loop Cmd55 and Acmd41 till the condition ((last_resp & 0x80) != 0x0) returns False
        while True:
            self.__sdCmdObj.Cmd55(setRCA=True)
            last_resp = self.__sdCmdObj.ACmd41(argVal=globalOCRArgValue, computedarg=True)
            if (last_resp & 0x80) != 0x0: # 0x80(BusyBit) is considered instead of 0x80000000
                break

        # CCS=0x40 is considered instead of 0x40000000
        CCS = 0x40
        if ((last_resp & CCS) == 0x0):
            raise ValidationError.TestFailError(self.fn, "CCS Bit = 0 in ACMD41 Responce - Expected value of 1!")

        # set High Capacity of the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set High Capacity of the card")
        self.__dvtLib.SetCardCap(hiCap=True)    # Adjust drivers to HC card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Setting Capacity of the card Completed\n")

        # Set card mode as SD
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set card mode as SD")
        # self.__dvtLib.SetSdMmcCardMode(CardMode=2)    # Commenting out this line as this SDDVT package is only for SD.
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card mode got Changed to SD\n")

        # Identification of the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Identification Test begins")
        self.__dvtLib.Identification()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Identification Test Completed\n")

        # Set bus width as 4
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set bus width as 4")
        self.__dvtLib.SetBusWidth(busWidth = 4)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card bus width got set to 4\n")

        # Run globalSetLSHostFreq, globalSetSpeedMode
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetResetFreq")
        self.__globalSetLSHostFreq.Run()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalSetResetFreq CALL got Completed\n")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetSpeedMode")
        self.__globalSetSpeedMode.Run(globalProjectConfVar)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetSpeedMode CALL Completed\n")

        # Write & Read random address with random blockcount
        # Run AddressForWriteRead
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : AddressForWriteRead")
        self.__AddressForWriteRead.Run()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "AddressForWriteRead CALL Completed\n")

        #***Test CMD 8's out of sequence during Power Cycle Reset***
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Test CMD 8's out of sequence during Power Cycle Reset***")

        index = random.randrange(0, 4) + 1

        # POWER : OFF and ON
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL: BasicCommandFPGAReset Begins")
        self.__dvtLib.BasicCommandFPGAReset(False)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL: BasicCommandFPGAReset Completed\n")

        # Set frequency to 300 KHz
        self.__GlobalSetResetFreq.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set RCA value")
        self.__sdCmdObj.SetrelativeCardAddress()
        sdcmdWrap.SetCardRCA(0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RCA value got set\n")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RUNNING Cmd8, Cmd55, ACmd41")
        for Repeat2_CMD8_SD_HIGH in range(index):
            last_resp = self.__sdCmdObj.Cmd8(argVal = cmd8_arg)
            last_resp = ((last_resp.GetOneByteToInt(3) << 8) | last_resp.GetOneByteToInt(4))    # Bitwise or operation with the response to get the first bit of 2nd byte
            if (last_resp != cmd8_arg):
                # CMD8 Responce is incorrect!
                raise ValidationError.TestFailError(self.fn, "CMD8 Responce is incorrect!")

        last_resp = 0
        # Run loop Cmd55 and Acmd41 till the condition ((last_resp & 0x80) != 0x0) returns False
        while True:
            self.__sdCmdObj.Cmd55(setRCA=True)
            last_resp = self.__sdCmdObj.ACmd41(argVal=globalOCRArgValue, computedarg=True)
            if (last_resp & 0x80) != 0x0: # 0x80(BusyBit) is considered instead of 0x80000000
                break

        # CCS=0x40 is considered instead of 0x40000000
        CCS = 0x40
        if ((last_resp & CCS) == 0x0):
            raise ValidationError.TestFailError(self.fn, "CCS Bit = 0 in ACMD41 Responce - Expected value of 1!")

        # set High Capacity of the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set High Capacity of the card")
        self.__dvtLib.SetCardCap(hiCap=True)    # Adjust drivers to HC card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Setting up of Card Capacity Completed\n")

        # Set card mode as SD
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set card mode as SD")
        # self.__dvtLib.SetSdMmcCardMode(CardMode=2)    # Commenting out this line as this SDDVT package is only for SD.
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card mode got Changed to SD\n")

        # SwitchVolt (CMD11): to 1.8 v
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SwitchVolt (CMD11): to 1.8 v, timeToClockOff=0 ms, clockOffPeriod=5 ms")
        self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)

        # Identification of the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification of the card Begins")
        self.__dvtLib.Identification()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification Test got Completed\n")

        # Set bus width as 4
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set bus width as 4")
        self.__dvtLib.SetBusWidth(busWidth = 4)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus width as got changed to 4\n")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetLSHostFreq")
        self.__globalSetLSHostFreq.Run()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetLSHostFreq Completed\n")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetSpeedMode")
        self.__globalSetSpeedMode.Run(globalProjectConfVar)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalSetSpeedMode CALL Completed\n")

        # Write & Read random address with random blockcount
        # Run AddressForWriteRead
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : AddressForWriteRead")
        self.__AddressForWriteRead.Run()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "AddressForWriteRead CALL Completed\n")

        #***Test Sequential of CMD8's during Power Cycle & CMD0 Reset***
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Test Sequential of CMD8's during Power Cycle & CMD0 Reset***")
        index = random.randrange(0, 4) + 1

        # POWER : OFF and ON

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL: BasicCommandFPGAReset Begins")
        self.__dvtLib.BasicCommandFPGAReset(False)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL: BasicCommandFPGAReset Completed\n")

        # Set frequency to 300 KHz
        self.__GlobalSetResetFreq.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set RCA value")
        self.__sdCmdObj.SetrelativeCardAddress()
        sdcmdWrap.SetCardRCA(0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RCA value got set\n")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Run Cmd0()")
        self.__sdCmdObj.Cmd0()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd0() Execution successfull\n")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RUNNING Cmd8, Cmd55, ACmd41")
        for Repeat3_CMD8_SD_HIGH in range(index):   # Repeat CMD8 random number of iterations
            last_resp = self.__sdCmdObj.Cmd8(argVal = cmd8_arg)
            last_resp = ((last_resp.GetOneByteToInt(3) << 8) | last_resp.GetOneByteToInt(4))    # Bitwise or operation with the response to get the first bit of 2nd byte
            if (last_resp != cmd8_arg):
                # CMD8 Responce is incorrect!
                raise ValidationError.TestFailError(self.fn, "CMD8 Responce is incorrect!")

        last_resp = 0
        # Run loop Cmd55 and Acmd41 till the condition ((last_resp & 0x80) != 0x0) returns False
        while True:
            self.__sdCmdObj.Cmd55(setRCA=True)
            last_resp = self.__sdCmdObj.ACmd41(argVal=globalOCRArgValue, computedarg=True)
            if (last_resp & 0x80) != 0x0: # 0x80(BusyBit) is considered instead of 0x80000000
                break

        # CCS=0x40 is considered instead of 0x40000000
        CCS = 0x40
        if ((last_resp & CCS) == 0x0):
            raise ValidationError.TestFailError(self.fn, "CCS Bit = 0 in ACMD41 Responce - Expected value of 1!")

        # set High Capacity of the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set High Capacity of the card")
        self.__dvtLib.SetCardCap(hiCap=True)    # Adjust drivers to HC card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Setting Card Capacity was successful\n")

        # Set card mode as SD
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set card mode as SD")
        # self.__dvtLib.SetSdMmcCardMode(CardMode=2)    # Commenting out this line as this SDDVT package is only for SD.
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "card mode got set to SD successfully\n")

        # SwitchVolt (CMD11): to 1.8 v
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SwitchVolt (CMD11): to 1.8 v, timeToClockOff=0 ms, clockOffPeriod=5 ms")
        self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)

        # Identification of the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification of the card begins")
        self.__dvtLib.Identification()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Identification Test Completed\n")

        # Set bus width as 4
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set bus width as 4")
        self.__dvtLib.SetBusWidth(busWidth = 4)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Setting card bus width to 4 Completed\n")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetLSHostFreq")
        self.__globalSetLSHostFreq.Run()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetLSHostFreq CALL Completed\n")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL: globalSetSpeedMode")
        self.__globalSetSpeedMode.Run(globalProjectConfVar)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalSetSpeedMode CALL Completed\n")

        # Write & Read random address with random blockcount
        # Run AddressForWriteRead
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
    def test_HCSD_V2_TC002_1_1_1_2(self):
        obj = HCSD_V2_TC002_1_1_1_2(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
