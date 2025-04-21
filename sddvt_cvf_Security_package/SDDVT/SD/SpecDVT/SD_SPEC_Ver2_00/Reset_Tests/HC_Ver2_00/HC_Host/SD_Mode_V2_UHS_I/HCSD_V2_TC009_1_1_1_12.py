"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : HCSD_V2_TC009_1_1_1_12.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : HCSD_V2_TC009_1_1_1_12.py
# DESCRIPTION                    : Module to Test mismatch VOLA during Soft Reset, after Power Cycle Reset and after Power Cycle & CMD0 Reset.
# PRERQUISTE                     : HCSD_V2_UT01_AddressForWriteRead.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=HCSD_V2_TC009_1_1_1_12 --isModel=false --enable_console_log=1 --adapter=0
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
import SDDVT.Config_SD.ConfigSD_UT014_GlobalSetTO as GlobalSetTO
import SDDVT.Config_SD.ConfigSD_UT006_GlobalSetVolt as GlobalSetVolt
import SDDVT.Config_SD.ConfigSD_UT008_GlobalSetBusyTO as GlobalSetBusyTO
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
class HCSD_V2_TC009_1_1_1_12(customize_log):
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
        self.__globalSetTO = GlobalSetTO.globalSetTO(self.vtfContainer)
        self.__globalSetBusyTO = GlobalSetBusyTO.globalSetBusyTO(self.vtfContainer)
        self.__globalSetVolt = GlobalSetVolt.globalSetVolt(self.vtfContainer)
        self.__AddressForWriteRead = AddressForWriteRead.HCSD_V2_UT01_AddressForWriteRead(self.vtfContainer)


    # Testcase Utility Logic - Starts
    def block1_1_1_12(self, VOLAvalue, globalVOLAValue, configPatternFiledInCMD8, globalProjectConfVar):

        globalOCRArgValue = int(self.__config.get('globalOCRArgValue'))
        globalOCRResValue = int(self.__config.get('globalOCRResValue'))
        globalCardRCA = int(globalProjectConfVar['globalCardRCA'])

        CMDs8Flag = 0
        for FlagForMultipleCMD8s in range(0, 2):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FlagForMultipleCMD8s loop count is 16. Current iteration is %s" % (FlagForMultipleCMD8s + 1))

            #***Test mismatch VOLA in Soft Reset***
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Test mismatch VOLA in Soft Reset**")

            # Call globalSetBusyTO.st3
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetBusyTO")
            self.__globalSetBusyTO.Run()

            # Set frequency to 300 KHz
            self.__GlobalSetResetFreq.Run()

            # Set RCA
            self.__sdCmdObj.SetrelativeCardAddress()
            sdcmdWrap.SetCardRCA(0)

            index = random.randrange(0, 4) + 1
            pattern = random.randrange(0, 256)
            reserve = (random.randrange(0, 1048576))
            arg = (VOLAvalue << 8)
            exp = ((globalVOLAValue << 8) | pattern)
            arg_correct = ((globalVOLAValue << 8 | pattern) | (reserve << 12))
            arg = ((arg | pattern) | (reserve << 12))

            # Run Cmd0, Cmd8
            self.__sdCmdObj.Cmd0()

            if (CMDs8Flag == 0):
                #Call globalSetBusyTO.st3
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetBusyTO")
                self.__globalSetBusyTO.Run()
                try:
                    self.__sdCmdObj.Cmd8(argVal = arg)
                except ValidationError.CVFGenericExceptions as exc:
                    self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "Cmd8")
                else:
                    raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING error not occurred")
            else:
                for Random_CMD8_Number1_SD_HIGH in range(0, index): # Repeat CMD 8 random number of iterations
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Random_CMD8_Number1_SD_HIGH loop count is %s. Current iteration is %s" % ((index + 1), (Random_CMD8_Number1_SD_HIGH + 1)))

                    last_resp = self.__sdCmdObj.Cmd8(argVal=arg_correct)
                    last_resp = ((last_resp.GetOneByteToInt(3) << 8) | last_resp.GetOneByteToInt(4))    # Bitwise or operation with the response to get the first bit of 2nd byte
                    if (last_resp != exp):
                        # CMD8 Responce is incorrect!
                        raise ValidationError.TestFailError(self.fn, "CMD8 Responce is incorrect!")

                #Call globalSetBusyTO
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetBusyTO")
                self.__globalSetBusyTO.Run()

                #single cmd 8
                try:
                    self.__sdCmdObj.Cmd8(argVal = arg)
                except ValidationError.CVFGenericExceptions as exc:
                    self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "Cmd8")
                else:
                    raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING error not occurred")
            #else end

            # Run globalSetTO
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetTO")
            self.__globalSetTO.Run()

            globalOCRResValue = (globalOCRResValue & 0xFEFFFFFF)    # S18A=0

            # Reset the card
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RESET card and IDENTIFICATION of the card")
            self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=globalOCRArgValue, cardSlot=globalCardRCA, sendCmd8=True,
                                initInfo=None, rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True,
                                bSendCMD58=False, version=0x0, VOLA=globalVOLAValue, cmdPattern=configPatternFiledInCMD8,
                                reserved=0x0, expOCRVal=globalOCRResValue)

            globalOCRResValue = (globalOCRResValue | 0x1000000)

            # set High Capacity of the card
            self.__dvtLib.SetCardCap(hiCap=True)    # Adjust drivers to HC card

            # Set card mode as SD
            # self.__dvtLib.SetSdMmcCardMode(CardMode=2)    # Commenting out this line as this SDDVT package is only for SD.

            # Identification of the card
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification of the card")
            self.__dvtLib.Identification()

            # Set bus width as 4
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set bus width as 4")
            self.__dvtLib.SetBusWidth(busWidth = 4)

            # Run AddressForWriteRead - Write & Read random address with random blockcount
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : AddressForWriteRead")
            self.__AddressForWriteRead.Run()

            #***Test mismatch VOLA in Power Cycle Reset***
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Test mismatch VOLA in Power Cycle Reset***")

            # Call globalSetBusyTO.st3
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetBusyTO")
            self.__globalSetBusyTO.Run()

            # Set frequency to 300 KHz
            self.__GlobalSetResetFreq.Run()

            # Set RCA
            self.__sdCmdObj.SetrelativeCardAddress()
            sdcmdWrap.SetCardRCA(0)

            index = random.randrange(0, 4) + 1
            pattern = random.randrange(0, 256)
            reserve = (random.randrange(0, 1048576))
            arg = (VOLAvalue << 8)
            exp = ((globalVOLAValue << 8) | pattern)
            arg_correct = ((globalVOLAValue << 8 | pattern) | (reserve << 12))
            arg = ((arg | pattern) | (reserve << 12))

            # Power Off and On
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)

            # Set frequency to 300 KHz
            self.__GlobalSetResetFreq.Run()

            # Run Cmd8
            if (CMDs8Flag == 0):
                #Call globalSetBusyTO.st3
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetBusyTO")
                self.__globalSetBusyTO.Run()

                #single cmd 8
                try:
                    self.__sdCmdObj.Cmd8(argVal = arg)
                except ValidationError.CVFGenericExceptions as exc:
                    self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "Cmd8")
                else:
                    raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING error not occurred")
            else:
                for Random_CMD8_Number2_SD_HIGH in range(0, index): # Repeat CMD 8 random number of iterations
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Random_CMD8_Number2_SD_HIGH loop count is %s. Current iteration is %s" % ((index + 1), (Random_CMD8_Number2_SD_HIGH + 1)))

                    #single cmd 8
                    last_resp = self.__sdCmdObj.Cmd8(argVal = arg_correct)
                    last_resp = ((last_resp.GetOneByteToInt(3) << 8) | last_resp.GetOneByteToInt(4))    # Bitwise or operation with the response to get the first bit of 2nd byte
                    if (last_resp != exp):
                        # CMD8 Responce is incorrect!
                        raise ValidationError.TestFailError(self.fn, "CMD8 Responce is incorrect!")

                #Call globalSetBusyTO.st3
                self.__globalSetBusyTO.Run()

                #single cmd 8
                try:
                    self.__sdCmdObj.Cmd8(argVal = arg)
                except ValidationError.CVFGenericExceptions as exc:
                    self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "Cmd8")
                else:
                    raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING error not occurred")

            # Run globalSetTO
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetTO")
            self.__globalSetTO.Run()

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RESET card and IDENTIFICATION of the card")
            self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=globalOCRArgValue, cardSlot=globalCardRCA, sendCmd8=True,
                                initInfo=None, rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True, bSendCMD58=False,
                                version=0x0, VOLA=globalVOLAValue, cmdPattern=configPatternFiledInCMD8, reserved=0x0,
                                expOCRVal=globalOCRResValue)

            # set High Capacity of the card
            self.__dvtLib.SetCardCap(hiCap=True)    # Adjust drivers to HC card

            # Set card mode as SD
            # self.__dvtLib.SetSdMmcCardMode(CardMode=2)    # Commenting out this line as this SDDVT package is only for SD.

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

            #***Test mismatch VOLA in Power Cycle & CMD 0 Reset***
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Test mismatch VOLA in Power Cycle & CMD 0 Reset***\n")

            # Call globalSetBusyTO.st3
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetBusyTO")
            self.__globalSetBusyTO.Run()

            # Set frequency to 300 KHz
            self.__GlobalSetResetFreq.Run()

            # Set RCA
            self.__sdCmdObj.SetrelativeCardAddress()
            sdcmdWrap.SetCardRCA(0)

            index = random.randrange(0, 4) + 1
            pattern = random.randrange(0, 256)
            reserve = (random.randrange(0, 1048576))
            arg = (VOLAvalue << 8)
            exp = ((globalVOLAValue << 8) | pattern)
            arg_correct = ((globalVOLAValue << 8 | pattern) | (reserve << 12))
            arg = ((arg | pattern) | (reserve << 12))

            # Power Off and On
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)

            # Set frequency to 300 KHz
            self.__GlobalSetResetFreq.Run()

            # Run cmd0, cmd8
            self.__sdCmdObj.Cmd0()

            if (CMDs8Flag == 0):
                #Call globalSetBusyTO.st3
                self.__globalSetBusyTO.Run()

                #single cmd 8
                try:
                    self.__sdCmdObj.Cmd8(argVal = arg)
                except ValidationError.CVFGenericExceptions as exc:
                    self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "Cmd8")
                else:
                    raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING error not occurred")
            else:
                for Random_CMD8_Number3_SD_HIGH in range(0, index):
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Random_CMD8_Number3_SD_HIGH loop count is %s. Current iteration is %s" % ((index + 1), (Random_CMD8_Number3_SD_HIGH + 1)))

                    last_resp = self.__sdCmdObj.Cmd8(argVal = arg_correct)
                    last_resp = ((last_resp.GetOneByteToInt(3) << 8) | last_resp.GetOneByteToInt(4))    # Bitwise or operation with the response to get the first bit of 2nd byte
                    if (last_resp != exp):
                        # CMD8 Responce is incorrect!
                        raise ValidationError.TestFailError(self.fn, "CMD8 Responce is incorrect!")

                #Call globalSetBusyTO.st3
                self.__globalSetBusyTO.Run()

                #single cmd 8
                try:
                    self.__sdCmdObj.Cmd8(argVal = arg)
                except ValidationError.CVFGenericExceptions as exc:
                    self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "Cmd8")
                else:
                    raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING error not occurred")

            # Run globalSetTO
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetTO")
            self.__globalSetTO.Run()

            # Reset the card
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RESET card and IDENTIFICATION of the card")
            self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=globalOCRArgValue, cardSlot=globalCardRCA, sendCmd8=True,
                                initInfo=None, rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True, bSendCMD58=False,
                                version=0x0, VOLA=globalVOLAValue, cmdPattern=configPatternFiledInCMD8, reserved=0x0,
                                expOCRVal=globalOCRResValue)

            # set High Capacity of the card
            self.__dvtLib.SetCardCap(hiCap=True)    # Adjust drivers to HC card

            # Set card mode as SD
            # self.__dvtLib.SetSdMmcCardMode(CardMode=2)    # Commenting out this line as this SDDVT package is only for SD.

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

            # Increment the CMDs8Flag by 1
            CMDs8Flag = CMDs8Flag + 1


    def Run(self):
        """
        Name : Run
        """

        # Initialize the SD card
        globalProjectConfVar = self.__sdCmdObj.DoBasicInit()

        globalVOLAValue = int(globalProjectConfVar['globalVOLAValue'])
        configPatternFiledInCMD8 = int(globalProjectConfVar['configPatternFiledInCMD8'])
        globalCardVoltage = (self.__config.get('globalCardVoltage'))

        # Run globalSetTO
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetTO")
        self.__globalSetTO.Run()

        # Run globalSetVolt
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetVolt")
        self.__globalSetVolt.Run(globalProjectConfVar)

        VOLAvalue = 0

        # Run VOLAmismatch loop for 15 times , depending on the condition globalCardVoltage HV or LV, call block 1_1_1_12
        for VOLAmismatch in range(0, 16):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VOLAmismatch loop count is 16. Current iteration is %s" % (VOLAmismatch + 1))

            #set globalCardVoltage as HV
            if ((globalCardVoltage == "HV") and (VOLAvalue != globalVOLAValue)) or ((globalCardVoltage == "LV") and ((VOLAvalue != 1) and (VOLAvalue != 2))):
                #call block 1_1_1_12
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "call block 1_1_1_12")
                self.block1_1_1_12(VOLAvalue, globalVOLAValue, configPatternFiledInCMD8, globalProjectConfVar)
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Testcase requirement is not fullfilled. Hence not running the testcase")

            VOLAvalue = VOLAvalue + 1

        return 0

    # Testcase Utility Logic - Ends
# Testcase Utility Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_HCSD_V2_TC009_1_1_1_12(self):
        obj = HCSD_V2_TC009_1_1_1_12(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
