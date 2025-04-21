"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : HCSD_V2_TC010_1_1_1_14.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : HCSD_V2_TC010_1_1_1_14.py
# DESCRIPTION                    : Module to Test Skip CMD8 during Soft Reset, after Power Cycle Reset and after Power Cycle & CMD0 Reset.
# PRERQUISTE                     : HCSD_V2_UT01_AddressForWriteRead.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=HCSD_V2_TC010_1_1_1_14 --isModel=false --enable_console_log=1 --adapter=0
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
import SDDVT.Config_SD.ConfigSD_UT003_GlobalInitSDCard as GlobalInitSDCard
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
class HCSD_V2_TC010_1_1_1_14(customize_log):
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
        self.__globalInitSDCard = GlobalInitSDCard.globalInitSDCard(self.vtfContainer)
        self.__globalSetTO = GlobalSetTO.globalSetTO(self.vtfContainer)
        self.__globalSetBusyTO = GlobalSetBusyTO.globalSetBusyTO(self.vtfContainer)
        self.__globalSetVolt = GlobalSetVolt.globalSetVolt(self.vtfContainer)
        self.__AddressForWriteRead = AddressForWriteRead.HCSD_V2_UT01_AddressForWriteRead(self.vtfContainer)


    # Testcase Utility Logic - Starts
    def Run(self):
        """
        Name : Run
        """

        # Initialize the SD card
        globalProjectConfVar = self.__sdCmdObj.DoBasicInit()

        # Power Off and on
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        # Get the Global PreTest Settings values
        globalVOLAValue = int(globalProjectConfVar['globalVOLAValue'])
        configPatternFiledInCMD8 = int(globalProjectConfVar['configPatternFiledInCMD8'])
        globalOCRArgValue = int(globalProjectConfVar['globalOCRArgValue'])
        globalOCRResValue = int(globalProjectConfVar['globalOCRResValue'])
        globalCardRCA = int(globalProjectConfVar['globalCardRCA'])

        # Variable Declaration Operation.
        globalOCRResValue = (globalOCRResValue | 0x1000000)

        # CALL : globalInitSDCard
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalInitSDCard")
        self.__globalInitSDCard.Run(globalProjectConfVar)

        # Identification of the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification of the card")
        self.__dvtLib.Identification()

        # Set bus width as 4
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set bus width as 4")
        self.__dvtLib.SetBusWidth(busWidth = 4)

        # CALL : globalSetTO
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetTO")
        self.__globalSetTO.Run()

        # CALL : globalSetVolt
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetVolt")
        self.__globalSetVolt.Run(globalProjectConfVar)

        # Tag:***Skip CMD 8 during Soft Reset***
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Skip CMD 8 during Soft Reset***")

        # Run globalSetBusyTO
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetBusyTO")
        self.__globalSetBusyTO.Run()

        globalCardVoltage  = (self.__config.get('globalCardVoltage'))

        # Run RESET card
        if (globalCardVoltage == "HV"):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RESET card without CMD 8 and IDENTIFICATION of the card")

            #set SD mode includes in ResetCard
            try:    # Soft Reset without CMD 8
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RESET card")
                self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=globalOCRArgValue, cardSlot=globalCardRCA, sendCmd8=False,
                                    initInfo=None, rca=0x0, time=0x00, sendCMD0=0x1, bHighCapacity=True, bSendCMD58=False,
                                    version=0x0, VOLA=0x1, cmdPattern=0xAA, reserved=0x0, expOCRVal=0xFF8000)
            except ValidationError.CVFGenericExceptions as exc:
                # TOBEDONE: YetTo find out the expected exception
                self.__dvtLib.Expected_Failure_Check(exc, "", "Reset")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected  error not occurred")

            # Set card mode as SD
            # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set card mode as SD")
            # self.__dvtLib.SetSdMmcCardMode(CardMode=2)    # Commenting out this line as this SDDVT package is only for SD.

            # CALL : globalSetTO
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetTO")
            self.__globalSetTO.Run()

            # Variable Declaration Operation
            globalOCRResValue = (globalOCRResValue & 0xFEFFFFFF)    # S18A=0

            # RESET card
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RESET card")
            self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=globalOCRArgValue, cardSlot=globalCardRCA, sendCmd8=True,
                                initInfo=None, rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True, bSendCMD58=False,
                                version=0x0, VOLA=globalVOLAValue, cmdPattern=configPatternFiledInCMD8, reserved=0x0,
                                expOCRVal=globalOCRResValue)

            # Identification of the card
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification of the card")
            self.__dvtLib.Identification()

            # Set bus width as 4
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set bus width as 4")
            self.__dvtLib.SetBusWidth(busWidth = 4)

         # End of IF Loop

        # Run AddressForWriteRead - Write & Read random address with random blockcount
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : AddressForWriteRead")
        self.__AddressForWriteRead.Run()

        # ***Skip CMD 8 during Power Cycle Reset***
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Skip CMD 8 during Power Cycle Reset***")

        # Power Off and On
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        # Set frequency to 300 KHz
        self.__GlobalSetResetFreq.Run()

        # Run globalSetBusyTO
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetBusyTO")
        self.__globalSetBusyTO.Run()

        # Run cmd55() and acmd41
        if (globalCardVoltage == "HV"):

            # 0x80 is considered instead of  0x80000000 as to set the busy bit in ACmd41 structure
            busyBit= 0x80
            last_resp = 0

            # Set Label:PowerCycle
            configResetTOCounter = int(globalProjectConfVar['configResetTOCounter'])
            for PowerCycle in range(0, (configResetTOCounter + 1)):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PowerCycle loop count is %s. Current iteration is %s" % ((configResetTOCounter + 1), (PowerCycle + 1)))

                self.__sdCmdObj.Cmd55(setRCA=True)
                last_resp = self.__sdCmdObj.ACmd41(argVal=globalOCRArgValue, computedarg=True)
                time.sleep(0.001)   # 1 milli second

            if ((last_resp & busyBit) != 0x00): # Expected - Card did not complete it's initilization!
                raise ValidationError.TestFailError(self.fn, "Card entered Ready State without CMD8")

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetTO")
            self.__globalSetTO.Run()

            # Variable Declaration Operation
            globalOCRResValue = (globalOCRResValue | 0x1000000)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RESET card with CMD 8 and IDENTIFICATION of the card")
            # RESET card
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RESET card")
            self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=globalOCRArgValue, cardSlot=globalCardRCA, sendCmd8=True,
                                initInfo=None, rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True, bSendCMD58=False,
                                version=0x0, VOLA=globalVOLAValue, cmdPattern=configPatternFiledInCMD8, reserved=0x0,
                                expOCRVal=globalOCRResValue)

            # Set card mode as SD
            # self.__dvtLib.SetSdMmcCardMode(CardMode=2)    # Commenting out this line as this SDDVT package is only for SD.

            # SwitchVolt (CMD11): to 1.8 v
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SwitchVolt (CMD11): to 1.8 v, timeToClockOff=0 ms, clockOffPeriod=5 ms")
            self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)

            # Identification of the card
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification of the card")
            self.__dvtLib.Identification()

            #SStep g:et bus width as 4
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set bus width as 4")
            self.__dvtLib.SetBusWidth(busWidth = 4)
        # End of IF Loop

        # Run AddressForWriteRead - Write & Read random address with random blockcount
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : AddressForWriteRead")
        self.__AddressForWriteRead.Run()

        #***Skip CMD 8 during Power Cycle & CMD 0 Reset***
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***Skip CMD8 during Power Cycle & CMD0 Reset***")

        # Run globalSetBusyTO
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetBusyTO")
        self.__globalSetBusyTO.Run()

        # Power Off and On
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER : OFF and ON")
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        # Run globalSetBusyTO
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetBusyTO")
        self.__globalSetBusyTO.Run()

       # Run RESET card
        if (globalCardVoltage == "HV"):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RESET card without CMD 8 and IDENTIFICATION of the card")

            #set SD mode includes in ResetCard
            try:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RESET card")
                self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=globalOCRArgValue, cardSlot=globalCardRCA, sendCmd8=False,
                                    initInfo=None, rca=0x0, time=0x00, sendCMD0=0x1, bHighCapacity=True, bSendCMD58=False,
                                    version=0x0, VOLA=globalVOLAValue, cmdPattern=configPatternFiledInCMD8, reserved=0x0,
                                    expOCRVal=0xFF8000)
            except ValidationError.CVFGenericExceptions as exc:
                # TOBEDONE: YetTo find out the expected exception
                self.__dvtLib.Expected_Failure_Check(exc, "", "Reset")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected  error not occurred")

            # Set card mode as SD
            # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set card mode as SD")
            # self.__dvtLib.SetSdMmcCardMode(CardMode=2)    # Commenting out this line as this SDDVT package is only for SD.

            # CALL : globalSetTO
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL : globalSetTO")
            self.__globalSetTO.Run()

            globalOCRResValue = int(globalProjectConfVar['globalOCRResValue'])

            # RESET card
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RESET card")
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
        # End of IF Loop

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
    def test_HCSD_V2_TC010_1_1_1_14(self):
        obj = HCSD_V2_TC010_1_1_1_14(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
