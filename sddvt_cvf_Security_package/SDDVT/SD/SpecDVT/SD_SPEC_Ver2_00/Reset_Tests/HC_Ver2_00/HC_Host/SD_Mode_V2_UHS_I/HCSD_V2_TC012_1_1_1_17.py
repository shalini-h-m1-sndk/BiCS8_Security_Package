"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : HCSD_V2_TC012_1_1_1_17.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : HCSD_V2_TC012_1_1_1_17.py
# DESCRIPTION                    : Module to Test Quary mode during Soft Reset, after Power Cycle Reset and after Power Cycle & CMD0 Reset.
# PRERQUISTE                     : HCSD_V2_UT01_AddressForWriteRead.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=HCSD_V2_TC012_1_1_1_17 --isModel=false --enable_console_log=1 --adapter=0
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
class HCSD_V2_TC012_1_1_1_17(customize_log):
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

        # Get the Global PreTest Settings values
        globalVOLAValue = int(globalProjectConfVar['globalVOLAValue'])
        configPatternFiledInCMD8 = int(globalProjectConfVar['configPatternFiledInCMD8'])
        configResetTOCounter = int(globalProjectConfVar["configResetTOCounter"])
        globalCardVoltage = (self.__config.get('globalCardVoltage'))

        # Run globalSetTO
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetTO to SetTime out Values")
        self.__globalSetTO.Run()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalSetTO CALL got Completed\n")

        # Run globalSetVolt
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetVolt")
        self.__globalSetVolt.Run(globalProjectConfVar)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalSetVolt CALL got Completed\n")

        #cmd8_arg needs to be passed in cmd8()
        cmd8_arg = ((globalVOLAValue << 8) | configPatternFiledInCMD8)
        exp = (globalVOLAValue << 8 | configPatternFiledInCMD8)

        #***Test Quary mode  during soft Reset***
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Test Quary mode during soft Reset***")

        # Run cmd0, cmd8, cmd55, acmd41
        self.__sdCmdObj.Cmd0()

        # Set frequency to 300 KHz
        self.__GlobalSetResetFreq.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SET RCA")
        self.__sdCmdObj.SetrelativeCardAddress()
        sdcmdWrap.SetCardRCA(0)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "setting of RCA value completed\n")

        last_resp = self.__sdCmdObj.Cmd8(argVal=cmd8_arg)
        last_resp = ((last_resp.GetOneByteToInt(3) << 8) | last_resp.GetOneByteToInt(4))    # Bitwise or operation with the response to get the first bit of 2nd byte
        if (last_resp != exp):
            #CMD8 Response is incorrect!
            raise ValidationError.TestFailError(self.fn, "CMD8 Response is incorrect!")

        self.__sdCmdObj.Cmd55(setRCA=True)
        last_resp = self.__sdCmdObj.ACmd41(1, 0, 1, argVal=0x40000000,diffResp =True)

        # globalCardVoltage set as HV
        if (globalCardVoltage == "HV"):
            if ((last_resp & 0x00FFFFFF) != 0xFF8000):
                raise ValidationError.TestFailError(self.fn, "HV Card Response to Quary mode incorrect value!")

        # Loop 1st level: BusyBit1-- run cmd55, acmd41
        for BusyBit1 in range(0, (configResetTOCounter + 1)):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "BusyBit1 loop count is %s. Current iteration is %s" % ((configResetTOCounter + 1), (BusyBit1 + 1)))

            self.__sdCmdObj.Cmd55(setRCA=True)
            if (globalCardVoltage == "HV"):
                last_resp = self.__sdCmdObj.ACmd41(argVal=0xFF8000,computedarg=True)

            if (globalCardVoltage == "LV"):
                last_resp = self.__sdCmdObj.ACmd41(argVal=0xFF8080,computedarg=True)

            time.sleep(0.001)   # 1 milli second
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Iteration Ends for BusyBit1 counter\n")

        # 0x80 is considered instead of  0x80000000 as to set the busy bit in ACmd41 structure
        if ((last_resp & 0x80) != 0):   # Expected - Card did not complete it's initilization!
            raise ValidationError.TestFailError(self.fn, "Card entered Ready State without HCS Bit = 1 in the first ACMD 41")

        # Identification
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification Test Starts")
        try:
            self.__dvtLib.Identification()
        except ValidationError.CVFGenericExceptions as exc:
            self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "Identification")
        else:
            raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING error not occurred")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification Test got Completed\n")

        #***Test Quary mode during Power Cycle Reset***
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Test Quary mode during Power Cycle Reset***")

        # Power Off and On
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        # Set frequency to 300 KHz
        self.__GlobalSetResetFreq.Run()

        # Run Cmd0
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd0() Excution Started")
        self.__sdCmdObj.Cmd0()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd0() Excution Completed\n")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set RCA value")
        self.__sdCmdObj.SetrelativeCardAddress()
        sdcmdWrap.SetCardRCA(0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RCA value got set\n")

        # Run Cmd8, Cmd55 and acmd41 and check its response.
        last_resp = self.__sdCmdObj.Cmd8(argVal = cmd8_arg)
        last_resp = ((last_resp.GetOneByteToInt(3) << 8) | last_resp.GetOneByteToInt(4))    # Bitwise or operation with the response to get the first bit of 2nd byte
        if (last_resp != exp):
            #CMD8 Response is incorrect!
            raise ValidationError.TestFailError(self.fn, "CMD8 Response is incorrect!")

        last_resp = 0
        self.__sdCmdObj.Cmd55(setRCA=True)
        last_resp = self.__sdCmdObj.ACmd41(argVal=0x40000000,diffResp =True)    # Quary mode

        # globalCardVoltage set as HV
        if (globalCardVoltage == "HV"):
            if ((last_resp & 0x00FFFFFF) != 0xFF8000):
                raise ValidationError.TestFailError(self.fn, "HV Card Response to Quary mode incorrect value!")

        # Loop Second Level: BusyBit2
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Iteration of BusyBit2 counter begins\n")
        for BusyBit2 in range(0, (configResetTOCounter + 1)):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "BusyBit2 loop count is %s. Current iteration is %s" % ((configResetTOCounter + 1), (BusyBit2 + 1)))

            self.__sdCmdObj.Cmd55(setRCA=True)
            if (globalCardVoltage == "HV"):
                last_resp = self.__sdCmdObj.ACmd41(argVal=0xFF8000,computedarg=True)

            if (globalCardVoltage == "LV"):
                last_resp = self.__sdCmdObj.ACmd41(argVal=0xFF8080,computedarg=True)

            time.sleep(0.001)   # 1 milli second
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Iteration of BusyBit2 counter Completed\n")

        if ((last_resp & 0x80) != 0):   # Expected - Card did not complete it's initilization!
            raise ValidationError.TestFailError(self.fn, "Card entered Ready State without HCS Bit = 1 in the first ACMD 41")

        # SwitchVolt (CMD11): to 1.8 v
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SwitchVolt (CMD11): to 1.8 v, timeToClockOff=0 ms, clockOffPeriod=5 ms")
        try:
            self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)
        except ValidationError.CVFGenericExceptions as exc:
            self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "SwitchVolt_CMD11")
        else:
            raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING error not occurred")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SwitchVolt (CMD11) Execution Completed\n")

        # Identification
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Identification Test begins")
        try:
            self.__dvtLib.Identification()
        except ValidationError.CVFGenericExceptions as exc:
            self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "Identification")
        else:
            raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING error not occurred")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Identification Test Completed\n")

        #***Test Quary mode during Power Cycle & CMD0 Reset***
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Test Quary mode during Power Cycle & CMD0 Reset***")

        # Power Off and On
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        # Set frequency to 300 KHz
        self.__GlobalSetResetFreq.Run()

        self.__sdCmdObj.SetrelativeCardAddress()
        sdcmdWrap.SetCardRCA(0)

        # Run cmd8, cmd55, acmd41
        last_resp = self.__sdCmdObj.Cmd8(argVal = cmd8_arg)
        last_resp = ((last_resp.GetOneByteToInt(3) << 8) | last_resp.GetOneByteToInt(4))    # Bitwise or operation with the response to get the first bit of 2nd byte
        if (last_resp != exp):
            #CMD8 Response is incorrect!
            raise ValidationError.TestFailError(self.fn, "CMD8 Response is incorrect!")

        self.__sdCmdObj.Cmd55(setRCA=True)
        last_resp = self.__sdCmdObj.ACmd41(argVal=0x40000000, diffResp =True)

        #globalCardVoltage set as HV
        if (globalCardVoltage == "HV"):

            if ((last_resp & 0x00FFFFFF) != 0xFF8000):
                raise ValidationError.TestFailError(self.fn, "HV Card Response to Quary mode incorrect value!")

        # Loop Third Level: BusyBit3
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Iteration of BusyBit3 counter begins\n")
        for BusyBit3 in range(0, (configResetTOCounter + 1)):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "BusyBit3 loop count is %s. Current iteration is %s" % ((configResetTOCounter + 1), (BusyBit3 + 1)))

            self.__sdCmdObj.Cmd55(setRCA=True)
            if (globalCardVoltage == "HV"):
                last_resp = self.__sdCmdObj.ACmd41(argVal=0x40FF8000,computedarg=True)

            if (globalCardVoltage == "LV"):
                last_resp = self.__sdCmdObj.ACmd41(argVal=0x40FF8080,computedarg=True)

            time.sleep(0.001)   # 1 milli second

            if (((last_resp & 0x80) != 0)):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Expected - Card did not complete it's initilization!")
            else:
                break

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Iteration of BusyBit3 counter Completed\n")

        # SwitchVolt (CMD11): to 1.8 v
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SwitchVolt (CMD11): to 1.8 v, timeToClockOff=0 ms, clockOffPeriod=5 ms")
        try:
            self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)
        except ValidationError.CVFGenericExceptions as exc:
            self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "SwitchVolt_CMD11")
        else:
            raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING error not occurred")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SwitchVolt (CMD11) Execution Completed\n")

        # identification
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Identification Test begins")
        try:
            self.__dvtLib.Identification()
        except ValidationError.CVFGenericExceptions as exc:
            self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "Identification")
        else:
            raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING error not occurred")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Identification Test Completed\n")

        return 0

    # Testcase Utility Logic - Ends
# Testcase Utility Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_HCSD_V2_TC012_1_1_1_17(self):
        obj = HCSD_V2_TC012_1_1_1_17(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
