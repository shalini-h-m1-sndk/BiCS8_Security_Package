"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : HCSD_V2_TC005_1_1_1_4.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : HCSD_V2_TC005_1_1_1_4.py
# DESCRIPTION                    : Module to Test Reserved Field in Soft Reset, Power Cycle Reset, Power Cycle & CMD0() Reset.
# PRERQUISTE                     : HCSD_V2_TC020_ResetHighCapacityCardWithDefultValuesInCMD8.py, HCSD_V2_UT01_AddressForWriteRead.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=HCSD_V2_TC005_1_1_1_4 --isModel=false --enable_console_log=1 --adapter=0
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
import HCSD_V2_TC020_ResetHighCapacityCardWithDefultValuesInCMD8 as ResetHighCapacityCardWithDefultValuesInCMD8
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
class HCSD_V2_TC005_1_1_1_4(customize_log):
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
        self.__ResetHighCapacityCardWithDefultValuesInCMD8 = ResetHighCapacityCardWithDefultValuesInCMD8.HCSD_V2_TC020_ResetHighCapacityCardWithDefultValuesInCMD8(self.vtfContainer)
        self.__AddressForWriteRead = AddressForWriteRead.HCSD_V2_UT01_AddressForWriteRead(self.vtfContainer)


    # Testcase Utility Logic - Starts
    def Run(self):
        """
        Name : Run
        """

        # Call ResetHighCapacityCardWithDefultValuesInCMD8 - All Reset Sequences with Defult values in CMD8
        globalProjectConfVar = self.__ResetHighCapacityCardWithDefultValuesInCMD8.Run()

        globalVOLAValue = int(globalProjectConfVar['globalVOLAValue'])
        configPatternFiledInCMD8 = int(globalProjectConfVar['configPatternFiledInCMD8'])
        globalOCRArgValue = int(self.__config.get('globalOCRArgValue'))
        globalOCRResValue = int(self.__config.get('globalOCRResValue'))

        #***Test Reserved Field in Soft Reset***
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Test Reserved Field in Soft Reset***")

        # Run ReservedChange1_SD_HIGH for 101 times
        for ReservedChange1_SD_HIGH in range(0, 101):   # Reserved check in Soft Reset - Random options
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Loop ReservedChange1_SD_HIGH count is 101, Current iteration is %s" % ReservedChange1_SD_HIGH)

            # Variable Declaration Operation
            Rsv4 = random.randrange(0, 16)
            Reserved12 = random.randrange(0, 4096)
            Reserved4 = random.randrange(0, 16)
            globalOCRResValue = (globalOCRResValue & 0xFEFFFFFF)    # S18A=0

            # Creating and Filling Buffer with Reserve Bit setting
            initInfo = ServiceWrap.Buffer.CreateBuffer(1, 0x00)
            initInfo.Fill(value = 0)
            initInfo.SetFourBytes(0, 1) # HighCapacity
            initInfo.SetFourBytes(4, 0) # SendCmd58
            initInfo.SetByte(8, 0) # Version
            initInfo.SetByte(9, globalVOLAValue)  # VOLA
            initInfo.SetByte(10, configPatternFiledInCMD8) # CMDPattern
            initInfo.SetByte(12, Rsv4)  # Reserved
            initInfo.SetTwoBytes(13, Reserved12)    # Reserved
            initInfo.SetByte(15, Reserved4) # Reserved

            # Reset and identification of the card
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RESET card and IDENTIFICATION of the card")

            self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=globalOCRArgValue, cardSlot=0x1, sendCmd8=True,
                                initInfo=initInfo, rca=0x0, time=0x0, sendCMD0=0x1, expOCRVal=globalOCRResValue)

            globalOCRResValue = (globalOCRResValue | 0x1000000) # S18A=1

            # Identification of the card
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification of the card")
            self.__dvtLib.Identification()

            # Set buswidth
            self.__dvtLib.SetBusWidth(busWidth = 4)

            # Call AddressForWriteRead - Write & Read random address with random blockcount
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : AddressForWriteRead")
            self.__AddressForWriteRead.Run()

        #***Test Reserved Field in Power Cycle Reset***
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "****Test Reserved Field in Power Cycle Reset***")

        # Run ReservedChange2_SD_HIGH for 101 times
        for ReservedChange2_SD_HIGH in range(101):  # Reserved check in Power Cycle  Reset - Random options
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Loop ReservedChange2_SD_HIGH count is 101, Current iteration is %s" % ReservedChange2_SD_HIGH)

            # Variable Declaration Operation
            cmd8_arg = ((globalVOLAValue << 8) | configPatternFiledInCMD8)
            cmd8_resp = ((globalVOLAValue << 8) | configPatternFiledInCMD8)
            reserve = ((random.randrange(0, 1048576) << 12))
            arg = (cmd8_arg | reserve)

            # Power Off and On
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)

            # Set frequency to 300 KHz
            self.__GlobalSetResetFreq.Run()

            # Set RCA
            self.__sdCmdObj.SetrelativeCardAddress()
            sdcmdWrap.SetCardRCA(0)

            # Run Cmd8
            last_resp = self.__sdCmdObj.Cmd8(argVal = arg)
            last_resp = ((last_resp.GetOneByteToInt(3) << 8) | last_resp.GetOneByteToInt(4))    # Bitwise or operation with the response to get the first bit of 2nd byte
            if (last_resp != cmd8_resp):
                # CMD 8 Responce is incorect - Reserve is incorrect!
                raise ValidationError.TestFailError(self.fn, "CMD 8 Responce is incorect - Reserve is incorrect!")

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

            # Adjust drivers to HC card
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set card as high capacity")
            self.__dvtLib.SetCardCap(hiCap=True)    # Adjust drivers to HC card

            # SET SD Mode
            # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SET SD Mode")
            # self.__dvtLib.SetSdMmcCardMode(CardMode=2, SetMode=True)  # Commenting out this line as this SDDVT package is only for SD.

            # SwitchVolt (CMD11): to 1.8 v
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SwitchVolt (CMD11): to 1.8 v, timeToClockOff=0 ms, clockOffPeriod=5 ms")
            self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)

            # Identification of the card
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "IDENTIFICATION : SD card")
            self.__dvtLib.Identification()
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Identification Test Completed\n")

            # Set bus width as 4
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set bus width as 4")
            self.__dvtLib.SetBusWidth(busWidth = 4)

            # Call globalSetLSHostFreq
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetLSHostFreq")
            self.__globalSetLSHostFreq.Run()

            # Call AddressForWriteRead - Write & Read random address with random blockcount
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : AddressForWriteRead")
            self.__AddressForWriteRead.Run()

        #***Test Reserved Field in Power Cycle & CMD0 Reset***
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Test Reserved Field in Power Cycle & CMD0 Reset***")

        # Run ReservedChange3_SD_HIGH for 101 times
        for ReservedChange3_SD_HIGH in range(101):  # Reserved check in Power Cycle & CMD 0 Reset - Random options
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Loop ReservedChange3_SD_HIGH count is 101, Current iteration is %s" % ReservedChange3_SD_HIGH)

            # Variable Declaration Operation
            Rsv4 = random.randrange(0, 16)
            Reserved12 = random.randrange(0, 4096)
            Reserved4 = random.randrange(0, 16)

            # Power Off and On
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)

            # Creating and Filling Buffer with Reserve Bit setting
            initInfo = ServiceWrap.Buffer.CreateBuffer(1, 0x00)
            initInfo.Fill(value = 0)
            initInfo.SetFourBytes(0, 1) # HighCapacity
            initInfo.SetFourBytes(4, 0) # SendCmd58
            initInfo.SetByte(8, 0)  # Version
            initInfo.SetByte(9, globalVOLAValue)    # VOLA
            initInfo.SetByte(10, configPatternFiledInCMD8)  # CMDPattern
            initInfo.SetByte(12, Rsv4)  # Reserved
            initInfo.SetTwoBytes(13, Reserved12)    # Reserved
            initInfo.SetByte(15, Reserved4) # Reserved

            # Reset card
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RESET card and IDENTIFICATION of the card")
            self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=globalOCRArgValue, cardSlot=0x1, sendCmd8=True,
                                initInfo=initInfo, rca=0x0, time=0x0, sendCMD0=0x1, expOCRVal=globalOCRResValue)

            # SwitchVolt (CMD11): to 1.8 v
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SwitchVolt (CMD11): to 1.8 v, timeToClockOff=0 ms, clockOffPeriod=5 ms")
            self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)

            # Identification of the card
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification of the card")
            self.__dvtLib.Identification()

            # Set bus width as 4
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set bus width as 4")
            self.__dvtLib.SetBusWidth(busWidth = 4)

            # Call AddressForWriteRead - Write & Read random address with random blockcount
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
    def test_HCSD_V2_TC005_1_1_1_4(self):
        obj = HCSD_V2_TC005_1_1_1_4(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
