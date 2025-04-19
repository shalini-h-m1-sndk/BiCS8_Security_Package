"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                :
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : SD3CMD2321_Utility_Reset.py
# DESCRIPTION                    :
# PRERQUISTE                     : [CMD23_UT09_LoadLocal_Variables,CMD23_UT11_SetBusMode_SpeedMode,
                                    CMD23_UT13_Successful_Verify, CMD23_UT14_Successful_Verify_MaxVoltage]
# STANDALONE EXECUTION           : No. It is an utility script.
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sushmitha P.S
# REVIEWED BY                    : Sivagurunathan
# DATE                           : 29-May-2024
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
from inspect import currentframe, getframeinfo

# Dependent Utilities
import CMD23_UT09_LoadLocal_Variables as LoadLocalVariables
import CMD23_UT11_SetBusMode_SpeedMode as SetBusModeSpeedMode
import CMD23_UT13_Successful_Verify as SuccessfulVerify
import CMD23_UT14_Successful_Verify_MaxVoltage as SuccessfulVerifyMaxVoltage

# Global Variables

# Testcase Utility Class - Begins

class CMD23_UT10_Reset(customize_log):
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
        self.__LoadLocal_Variables = LoadLocalVariables.CMD23_UT09_LoadLocal_Variables(self.vtfContainer)
        self.__SetBusModeSpeedMode = SetBusModeSpeedMode.CMD23_UT11_SetBusMode_SpeedMode(self.vtfContainer)
        self.__SuccessfulVerify = SuccessfulVerify.CMD23_UT13_Successful_Verify(self.vtfContainer)
        self.__SuccessfulVerifyMaxVoltage = SuccessfulVerifyMaxVoltage.CMD23_UT14_Successful_Verify_MaxVoltage(self.vtfContainer)

    # Testcase Utility Logic - Starts

    def Run(self, globalProjectValues, ProtocolMode = 0, Identification = 0, VerifyType = 0, SetPower = 0, SendCMD8 = 1, SendCMD0 = 1):
        """
        Name : Run
            # STEP 1 : Variable Declarations
            # STEP 2 : if SetPower = 1, Set No Power, Power
            # STEP 3 : Reset Card as per ProtocolMode
            # STEP 4 : Switch Voltage CMD11 as per globalSpeedMode with globalPowrUp
            # STEP 5 : Do Identification based on Identification Type
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Utility Execution Started " + "-" * 20 + "\n")
        # Variable Declarations
        localVariables  = self.__LoadLocal_Variables.Run( globalProjectValues, ret = 1)
        SendOCR         = localVariables['SendOCR']
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SendOCR : %d"%SendOCR)

        SendFirstOCR    = SendOCR
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SendFirstOCR : %d"%SendFirstOCR)

        SendNextOCR     = SendOCR
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SendNextOCR : %d"%SendNextOCR)

        SendOCR = int(globalProjectValues['globalOCRArgValue'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SendOCR : %d"%SendOCR)

        ExpectOCR = int(globalProjectValues['globalOCRResValue'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ExpectOCR : %s"%ExpectOCR)

       # globalSpeedMode  = globalProjectValues['temp_globalSpeedMode']
        globalSpeedMode = globalProjectValues['globalSpeedMode']
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalSpeedMode : %s"%globalSpeedMode)

        globalPowerUp   = globalProjectValues['globalPowerUp']
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalPowerUp : %s"%globalPowerUp)


        # if SetPower = 1, Set Power OFF and Power ON
        if SetPower == 1:
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)
        else:
            SendOCR = (SendOCR  & 0xFEFFFFFF)
            ExpectOCR = (ExpectOCR  & 0xFEFFFFFF)

        # Reset Card as per ProtocolMode
        if ProtocolMode == 1 :
            self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.Sd, SendOCR, cardSlot=0x1, sendCmd8=SendCMD8,
                                initInfo=None, rca=0x0, time = 0x0, sendCMD0=SendCMD0, bHighCapacity=False,
                                bSendCMD58=True, version=0x0, VOLA=0x1, cmdPattern=0xAA,
                                reserved=0x0, expOCRVal=ExpectOCR)
        if ProtocolMode == 2 :
            self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.Sd, SendOCR, cardSlot=0x1, sendCmd8=SendCMD8,
                                initInfo=None, rca=0x0, time = 0x0, sendCMD0=SendCMD0, bHighCapacity=False,
                                bSendCMD58=False, version=0x0, VOLA=0x1, cmdPattern=0xAA,
                                reserved=0x0, expOCRVal=ExpectOCR)
        if ProtocolMode == 3 :
            self.__dvtLib.enableACMD41()
            self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.SD_IN_SPI, SendOCR, cardSlot=0x1, sendCmd8=SendCMD8,
                                initInfo=None, rca=0x0, time = 0x0, sendCMD0=SendCMD0, bHighCapacity=True,
                                bSendCMD58=True, version=0x0, VOLA=0x1, cmdPattern=0xAA,
                                reserved=0x0, expOCRVal=ExpectOCR)
        if ProtocolMode == 4 :
            self.__dvtLib.enableACMD41()
            self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.SD_IN_SPI, SendOCR, cardSlot=0x1, sendCmd8=SendCMD8,
                                initInfo=None, rca=0x0, time = 0x0, sendCMD0=SendCMD0, bHighCapacity=False,
                                bSendCMD58=True, version=0x0, VOLA=0x1, cmdPattern=0xAA,
                                reserved=0x0, expOCRVal=ExpectOCR)

        # Switch Voltage CMD11 as per globalSpeedMode with globalPowrUp
        if (((globalSpeedMode == 'SDR12') or (globalSpeedMode == 'SDR25') or (globalSpeedMode == 'SDR50') or (globalSpeedMode == 'SDR104') or (globalSpeedMode == 'DDR50')) and ((globalPowerUp == 'powerCycle') or (globalPowerUp == 'powerCycleNoCMD0'))) :
            if SetPower == 1:

               # SwitchVolt (CMD11): to 1.8 v
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SwitchVolt (CMD11): to 1.8 v, timeToClockOff=0 ms, clockOffPeriod=5 ms")
                self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)


        # Do Identification based on Identification Type
        if Identification == 1:
            if ProtocolMode == 1 :
                self.__dvtLib.Identification()
                self.__sdCmdObj.GetCSD()
                # Call Utility_Set_BusMode_SpeedMode
                self.__SetBusModeSpeedMode.Run( globalProjectValues)

        # Do Write and Read Verification based on VerifyType
        if VerifyType ==  1 :
            # Call Utility_Successful_Verify
            self.__SuccessfulVerify.Run()
        if VerifyType == 3 :
            # Utility_Successful_Verify_MaxVoltage
            self.__SuccessfulVerifyMaxVoltage.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Utility Execution Completed " + "-" * 20 + "\n")
        return 0

    #End of Run function
#End of ResetUtil


    # Testcase Utility Logic - Ends

# Testcase Utility Class - Ends