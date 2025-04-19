"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : ACMD41_UT08_Reset.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : ACMD41_UT08_Reset.py
# DESCRIPTION                    : The purpose of this test is to assure reset
# PRERQUISTE                     : ACMD41_UT05_Failure_Verify.py, ACMD41_UT09_ResetSingleCommand.py, ACMD41_UT10_Set_BusSpeedMode.py,
                                   ACMD41_UT12_Successful_Verify.py, ACMD41_UT13_Successful_Verify_MaxVoltage.py, ACMD41_UT14_UHSReset.py
# STANDALONE EXECUTION           : No. It is an utility script.
# TEST ARGUMENTS                 : None
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
import ACMD41_UT05_Failure_Verify as FailureVerify
import ACMD41_UT09_ResetSingleCommand as ResetSingleCommand
import ACMD41_UT10_Set_BusSpeedMode as SetBusModeSpeedMode
import ACMD41_UT12_Successful_Verify as SuccessVerify
import ACMD41_UT13_Successful_Verify_MaxVoltage as SuccessVerifyMaxVoltage
import ACMD41_UT14_UHSReset as UHS_Reset

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
class ACMD41_UT08_Reset(customize_log):
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
        self.__UHSReset= UHS_Reset.ACMD41_UT14_UHSReset(self.vtfContainer)
        self.__ResetSingleCommand = ResetSingleCommand.ACMD41_UT09_ResetSingleCommand(self.vtfContainer)
        self.__SetBusModeSpeedMode = SetBusModeSpeedMode.ACMD41_UT10_Set_BusSpeedMode(self.vtfContainer)
        self.__FailureVerify = FailureVerify.ACMD41_UT05_Failure_Verify(self.vtfContainer)
        self.__SuccessVerify = SuccessVerify.ACMD41_UT12_Successful_Verify(self.vtfContainer)
        self.__SuccessVerifyMaxVoltage = SuccessVerifyMaxVoltage.ACMD41_UT13_Successful_Verify_MaxVoltage(self.vtfContainer)

    # Testcase Utility Logic - Starts
    def Run(self, globalProjectConfVar, localVariables):
        """
        Name : Run
        """
        # Load local variables
        SendFirstOCR = localVariables['SendOCR']
        SendNextOCR = localVariables['SendOCR']

        # if SetPower = 1, Set Power OFF and Power ON
        if localVariables['SetPower'] == 1:
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)
            localVariables['ExpectOCR'] = localVariables['ExpectOCR'] | (0x01000000 & localVariables['SendOCR'])

        # Checking condition ProtocolMode == 1
        if localVariables['ProtocolMode'] == 1:

            # Checking condition localVariables['SingleCommand'] == 1
            if localVariables['SingleCommand'] == 1:

                # call script Utility_ResetSingleCommand
                self.__ResetSingleCommand.Run(localVariables)

                # Reset card in SD mode
                ReceivedOCR = self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.Sd, ocr = SendNextOCR, cardSlot=0x1, bSendCMD58=False,
                                sendCmd8=False, initInfo=None, rca=0x0, time = 0x0, sendCMD0 = False, bHighCapacity=False,
                                version=0x0, VOLA=0x1, cmdPattern=0xAA, reserved=0x0, expOCRVal=localVariables['ExpectOCR'])
                localVariables['ExpectOCR'] = localVariables['ExpectOCR'] & 0xFEFFFFFF

                # Checking condition SetPower == 1
                if localVariables['SetPower'] == 1:
                    ReceivedOCR_LastAfterPC = ReceivedOCR[0]
            else:
                time.sleep(5)

            # Reset card in SD mode
            ReceivedOCR = self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.Sd, ocr = localVariables['SendOCR'], cardSlot=0x1, bSendCMD58=False,
                            sendCmd8=localVariables['SendCMD8'], initInfo=None, rca=0x0, time = 0x0, sendCMD0 = localVariables['SendCMD0'], bHighCapacity=True,
                            version=0x0, VOLA=0x1, cmdPattern=0xAA, reserved=0x0, expOCRVal=localVariables['ExpectOCR'])
            localVariables['ExpectOCR'] = localVariables['ExpectOCR'] & 0xFEFFFFFF

            if localVariables['SetPower'] == 1:
                ReceivedOCR_LastAfterPC = ReceivedOCR[0]

        if localVariables['ProtocolMode'] == 2:
            if localVariables['SingleCommand'] == 1:

                #call script Utility_ResetSingleCommand
                self.__ResetSingleCommand.Run(localVariables)

                #Reset card in SD mode
                ReceivedOCR = self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.Sd, ocr = SendNextOCR, cardSlot=0x1, bSendCMD58=False,
                                sendCmd8=False, initInfo=None, rca=0x0, time = 0x0, sendCMD0 = False, bHighCapacity=False,
                                version=0x0, VOLA=0x1, cmdPattern=0xAA, reserved=0x0, expOCRVal=localVariables['ExpectOCR'])
                localVariables['ExpectOCR'] = localVariables['ExpectOCR'] & 0xFEFFFFFF
                if localVariables['SetPower'] == 1:
                    ReceivedOCR_LastAfterPC = ReceivedOCR[0]
            else:
                try:
                    ReceivedOCR = self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.Sd, ocr = localVariables['SendOCR'], cardSlot=0x1, bSendCMD58=False,
                                sendCmd8=localVariables['SendCMD8'], initInfo=None, rca=0x0, time = 0x0, sendCMD0 = localVariables['SendCMD0'], bHighCapacity=True,
                                version=0x0, VOLA=0x1, cmdPattern=0xAA, reserved=0x0, expOCRVal=localVariables['ExpectOCR'])
                except ValidationError.CVFGenericExceptions as exc:
                    self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_IS_NOT_READY", Operation_Name = "Reset")
                else:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Expected error didn't occur!!")

            localVariables['ExpectOCR'] = localVariables['ExpectOCR'] & 0xFEFFFFFF
            if localVariables['SetPower'] == 1:
                ReceivedOCR_LastAfterPC = ReceivedOCR[0]

        if localVariables['ProtocolMode'] == 3:
            if localVariables['SingleCommand'] == 1:

                # call script Utility_ResetSingleCommand
                self.__ResetSingleCommand.Run(localVariables)
                localVariables['ExpectOCR'] = localVariables['ExpectOCR'] & 0xFEFFFFFF
                self.__dvtLib.enableACMD41()

                # Reset card in SPI mode (In Scripter based on CMD8 values ignored)
                ReceivedOCR = self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.SD_IN_SPI, ocr = SendNextOCR, cardSlot=0x1, bSendCMD58=False,
                                sendCmd8=False, initInfo=None, rca=0x0, time = 0x0, sendCMD0 = 0x1, bHighCapacity=True,
                                version=0x0, VOLA=0x1, cmdPattern=0xAA, reserved=0x0, expOCRVal=localVariables['ExpectOCR'])

                if localVariables['SetPower'] == 1:
                    ReceivedOCR_LastAfterPC = ReceivedOCR[0]
            else:
                localVariables['ExpectOCR'] = localVariables['ExpectOCR'] & 0xFEFFFFFF

            # Enable ACMD41 # part of the reset directive
            self.__dvtLib.enableACMD41()

            # Reset card in SD mode
            ReceivedOCR = self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.SD_IN_SPI, ocr = localVariables['SendOCR'], cardSlot=0x1, bSendCMD58=localVariables["SendCMD58"],
                            sendCmd8=True, initInfo=None, rca=0x0, time = 0x0, sendCMD0 = 0x1, bHighCapacity=True,
                            version=0x0, VOLA=0x1, cmdPattern=0xAA, reserved=0x0, expOCRVal=localVariables['ExpectOCR'])

            if localVariables['SetPower'] == 1:
                ReceivedOCR_LastAfterPC = ReceivedOCR[0]

        if localVariables['ProtocolMode'] == 4:
            if localVariables['SingleCommand'] == 1:
                self.__ResetSingleCommand.Run(localVariables)
                self.__dvtLib.enableACMD41()

                # Reset card in SD mode
                ReceivedOCR = self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.SD_IN_SPI, ocr = SendNextOCR, cardSlot=0x1, bSendCMD58=localVariables["SendCMD58"],
                                sendCmd8=False, initInfo=None, rca=0x0, time = 0x0, sendCMD0 = False, bHighCapacity=False,
                                version=0x0, VOLA=0x1, cmdPattern=0xAA, reserved=0x0, expOCRVal=localVariables['ExpectOCR'])
                localVariables['ExpectOCR'] = localVariables['ExpectOCR'] & 0xFEFFFFFF
                if localVariables['SetPower'] == 1:
                    ReceivedOCR_LastAfterPC = ReceivedOCR[0]
            else:
                self.__dvtLib.enableACMD41()
                # Reset card in SD mode
                ReceivedOCR = self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.SD_IN_SPI, ocr = localVariables['SendOCR'], cardSlot=0x1, bSendCMD58=localVariables["SendCMD58"],
                                sendCmd8=True, initInfo=None, rca=0x0, time = 0x0, sendCMD0 = 0x1, bHighCapacity=True,
                                version=0x0, VOLA=0x1, cmdPattern=0xAA, reserved=0x0, expOCRVal=localVariables['ExpectOCR'])
            localVariables['ExpectOCR'] = localVariables['ExpectOCR'] & 0xFEFFFFFF
            if localVariables['SetPower'] == 1:
                ReceivedOCR_LastAfterPC = ReceivedOCR[0]

        if localVariables['Identification'] == 1:
            if localVariables['ProtocolMode'] == 1:

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "localVariables['ReadyCcs18a111'] = %d" %(localVariables['ReadyCcs18a111']))
                # Checking condition for UHS reset.
                if (ReceivedOCR[0] == localVariables['ReadyCcs18a111'] and localVariables['SetPower'] == 1 ) or (ReceivedOCR_LastAfterPC == localVariables['ReadyCcs18a111'] and localVariables['SetPower'] == 0 ):
                    self.__UHSReset.Run(globalProjectConfVar, localVariables,localVariables['SetPower'])
                else:
                    self.__dvtLib.Identification()
                    self.__sdCmdObj.GetCSD()
                    if ((globalProjectConfVar['globalSpeedMode'] == 'SDR12') or (globalProjectConfVar['globalSpeedMode'] == 'SDR25') or (globalProjectConfVar['globalSpeedMode'] == 'SDR50')
                        or (globalProjectConfVar['globalSpeedMode'] == 'SDR104') or (globalProjectConfVar['globalSpeedMode'] == 'DDR50') or (globalProjectConfVar['globalSpeedMode'] == 'RandomSDR12_LS') or (globalSpeedMode == 'RandomSDR25_DDR50_HS')):

                        globalSpeedMode_Temp = globalProjectConfVar['globalSpeedMode']
                        globalProjectConfVar['globalSpeedMode'] = 'HS'

                    # Call to utility script SetBusModeSpeedMode
                    self.__SetBusModeSpeedMode.Run(globalProjectConfVar)

                    #If condition to set globalSpeedMode = globalSpeedMode_Temp
                    if((globalSpeedMode_Temp == 'SDR12') or (globalSpeedMode_Temp == 'SDR25') or (globalSpeedMode_Temp == 'SDR50') or (globalSpeedMode_Temp == 'SDR104') or (globalSpeedMode_Temp == 'DDR50') or (globalSpeedMode_Temp == 'RandomSDR12_LS') or (globalSpeedMode_Temp == 'RandomSDR25_DDR50_HS')):

                        globalProjectConfVar['globalSpeedMode'] = globalSpeedMode_Temp
                        globalSpeedMode_Temp = 'Z'

                    # Step 53: 1.2.6 : Set voltage = 3.3V, Max current = 100mA, A2D Rate : 62.5 Hz
                    sdVoltage = sdcmdWrap.SVoltage()
                    sdVoltage.voltage = 3300
                    sdVoltage.maxCurrent = 100
                    sdVoltage.maxVoltage = 3300
                    sdVoltage.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ
                    sdVoltage.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8

                    self.__dvtLib.setVolt(sdVolt=sdVoltage,statusReg=0,powerSupp=gvar.PowerSupply.VDDH)

                    # Checking condition to set voltage with ax current = 150mA
                    if localVariables['SendOCR'] == localVariables['HcsXpcS18r111']:

                        # Set voltage = 3.3V, Max current = 150mA, A2D Rate : 62.5 Hz
                        sdVoltage.maxCurrent = 150
                        self.__dvtLib.setVolt(sdVolt=sdVoltage,statusReg=0,powerSupp=gvar.PowerSupply.VDDH)

        if localVariables['VerifyType'] ==  1 :
            self.__SuccessVerify.Run()

        if localVariables['VerifyType'] ==  2 :
            self.__FailureVerify.Run(localVariables)

        if localVariables['VerifyType'] == 3 :
            self.__SuccessVerifyMaxVoltage.Run()

        return 0
    # Testcase Utility Logic - Ends
# Testcase Utility Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_ACMD41_UT08_Reset(self):
        obj = ACMD41_UT08_Reset(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends