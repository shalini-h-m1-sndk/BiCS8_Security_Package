"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : ACMD41_TC005_HSC_XPC_S18A_AllScenarios.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : ACMD41_TC005_HSC_XPC_S18A_AllScenarios.py
# DESCRIPTION                    : The purpose of this test is to run loop ACMD41 in all card, all modes with all scenarios.
# PRERQUISTE                     : ACMD41_UT02_CMD20_GetSequence.py, ACMD41_UT06_LoadCMD20_Variables.py, ACMD41_UT07_Load_LocalVariables.py,
                                   ACMD41_UT10_Set_BusSpeedMode.py, ACMD41_UT14_UHSReset.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=ACMD41_TC005_HSC_XPC_S18A_AllScenarios --isModel=false --enable_console_log=1 --adapter=0
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
import ACMD41_UT02_CMD20_GetSequence as cmd20_getseq
import ACMD41_UT06_LoadCMD20_Variables as LoadCMD20Variables
import ACMD41_UT07_Load_LocalVariables as LoadLocalVariables
import ACMD41_UT10_Set_BusSpeedMode as SetBusModeSpeedMode
import ACMD41_UT14_UHSReset as UHSReset

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

# Global Variables


# Testcase Class - Begins
class ACMD41_TC005_HSC_XPC_S18A_AllScenarios(customize_log):
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
        self.__LoadCMD20Variables = LoadCMD20Variables.ACMD41_UT06_LoadCMD20_Variables(self.vtfContainer)
        self.__cmd20getseq = cmd20_getseq.ACMD41_UT02_CMD20_GetSequence(self.vtfContainer)
        self.__localvariables = LoadLocalVariables.ACMD41_UT07_Load_LocalVariables(self.vtfContainer)
        self.__UHSReset = UHSReset.ACMD41_UT14_UHSReset(self.vtfContainer)
        self.__SetBusModeSpeedMode= SetBusModeSpeedMode.ACMD41_UT10_Set_BusSpeedMode(self.vtfContainer)


    # Testcase Logic - Starts
    def Run(self):
        """
        Name : Run
        """
        globalProjectConfVar = self.__sdCmdObj.DoBasicInit()

        # Load Variables from the Script Utility_Load_LocalVariables
        localVariables = self.__localvariables.Run(ret = 1)

        # Load CMD20 Specific variables from the Script Utility_CMD20_Variables
        cmd20variables = self.__LoadCMD20Variables.Run()

        # Variable declaration
        SetPower = 1
        SendCMD0 = 1
        SendCMD8 = 1
        Index = 0
        ReceivedOCR_LastAfterPC = 0 # Set to 0 as per scritper.

        # Loops 8 times as per Scripter.
        for i in range(0, 8):

            # Check condition index = 0
            if(Index % 4 == 0):
                localVariables["SendOCR"] = localVariables['HcsXpcS18r100']
                localVariables["ExpectOCR"] = localVariables['ReadyCcs18a110']

            # Check condition index = 1
            if(Index % 4 == 1):
                localVariables["SendOCR"] = localVariables['HcsXpcS18r101']
                localVariables["ExpectOCR"] = localVariables['ReadyCcs18a111']

            # Check condition index = 2
            if(Index % 4 == 2):
                localVariables["SendOCR"] = localVariables['HcsXpcS18r110']
                localVariables["ExpectOCR"] = localVariables['ReadyCcs18a110']

            # Check condition index = 3
            if(Index % 4 == 3):
                localVariables["SendOCR"] = localVariables['HcsXpcS18r111']
                localVariables["ExpectOCR"] = localVariables['ReadyCcs18a111']

            # Set SD MMC MODE, in SD = 2
            # sdcmdWrap.WriteRegister(regAddress = 0x0043, regValue = 0x0002)
            self.__dvtLib.SetSdMmcCardMode(CardMode = sdcmdWrap.CARD_MODE.Sd, SetMode = True)

            # Set Frequency 300KHz
            self.__sdCmdObj.SetFrequency(Freq = 300)

            # Set Power OFF and Power ON
            if (SetPower == 1):
                sdcmdWrap.SetPower(0)
                sdcmdWrap.SetPower(1)

                #  BASIC COMMAND FPGA RESET
                self.__dvtLib.BasicCommandFPGAReset(value = False)

                localVariables["ExpectOCR"] = localVariables["ExpectOCR"] | (0x01000000 & localVariables["SendOCR"])

            # Check condition SendCMD0 = 1
            if (SendCMD0 == 1):

                # CMD 0 - Issue Command
                self.__sdCmdObj.Cmd0()

                # SPECIAL MODES - 5 = Init, setMode = True
                self.__dvtLib.SetSpecialModes(5, True)
                # sdcmdWrap.WriteRegister(regAddress = 0x0043, regValue = 0x0002)

            # Step 17: 9: Check condition SendCMD8 = 1
            if(SendCMD8 == 1):

                cmd8_arg = 0x1AA

                # Issue command cmd8 = 0x1AA
                self.__sdCmdObj.Cmd8(cmd8_arg)

                #  Issue command cmd55
                self.__sdCmdObj.Cmd55(True)

                # Issue command ACMD41 = localVariables["SendOCR"], computedarg=True for making Acmd41 as default cmd.
                self.__sdCmdObj.ACmd41(argVal = localVariables["SendOCR"], computedarg = True)

            # while loop : SetRndOCR
            while True:

                # Variable declaration
                rnd_and = (((random.randrange(0, 128) | 0x2E) << 24) | 0x80FFFFFF)
                rnd_or = ((random.randrange(0, 128) & 0x51) << 24)
                localVariables["SendOCR_"] = ((localVariables["SendOCR"] & rnd_and) | rnd_or)

                # Check loop break condition
                if (localVariables["SendOCR_"] != localVariables["SendOCR"]):
                    break

            # Reset card in SD mode
            ReceivedOCR = self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.Sd, localVariables["SendOCR_"], cardSlot=0x1, sendCmd8=False,
                            initInfo=None, rca=0x0, time = 0x0, sendCMD0 = 0x0, bHighCapacity=False,
                            bSendCMD58=False, reserved=0x0, expOCRVal = localVariables['ExpectOCR'])

            # Set card hi cap
            self.__dvtLib.SetCardCap(hiCap=True)

            # Check condition to call script Utility_UHS_Reset
            if((ReceivedOCR[0] == localVariables['ReadyCcs18a111'] and SetPower == 1) or (ReceivedOCR_LastAfterPC == localVariables['ReadyCcs18a111'] and SetPower == 0)):

                # call Utility_UHS_Reset script
                self.__UHSReset.Run(globalProjectConfVar, localVariables)

            else:
                # Identification
                self.__dvtLib.Identification()

                #  GET CSD
                self.__sdCmdObj.GetCSD()

                # Get configuration parameter
                globalSpeedMode_Temp = ''

                # If condition to call SetBusModeSpeedMode utility.
                if((globalProjectConfVar["globalSpeedMode"] == 'SDR12') or (globalProjectConfVar["globalSpeedMode"] == 'SDR25') or (globalProjectConfVar["globalSpeedMode"] == 'SDR50') or (globalProjectConfVar["globalSpeedMode"] == 'SDR104') or (globalProjectConfVar["globalSpeedMode"] == 'DDR50') or (globalProjectConfVar["globalSpeedMode"] == 'RandomSDR12_LS') or (globalProjectConfVar["globalSpeedMode"] == 'RandomSDR25_DDR50_HS')):

                    globalSpeedMode_Temp = globalProjectConfVar["globalSpeedMode"]
                    globalProjectConfVar["globalSpeedMode"] = 'HS'

                # Call to utility script SetBusModeSpeedMode
                self.__SetBusModeSpeedMode.Run(globalProjectConfVar)

                # If condition to set globalSpeedMode = globalSpeedMode_Temp
                if((globalSpeedMode_Temp == 'SDR12') or (globalSpeedMode_Temp == 'SDR25') or (globalSpeedMode_Temp == 'SDR50') or (globalSpeedMode_Temp == 'SDR104') or (globalSpeedMode_Temp == 'DDR50') or (globalSpeedMode_Temp == 'RandomSDR12_LS') or (globalSpeedMode_Temp == 'RandomSDR25_DDR50_HS')):

                    globalProjectConfVar["globalSpeedMode"] = globalSpeedMode_Temp
                    globalSpeedMode_Temp = 'Z'

                # Set voltage = 3.3V, Max current = 100mA, A2D Rate : 62.5 Hz
                sdvoltage = sdcmdWrap.SVoltage()
                sdvoltage.voltage = 3300
                sdvoltage.maxCurrent = 100
                sdvoltage.maxVoltage = 3300
                sdvoltage.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ
                sdvoltage.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8

                self.__dvtLib.setVolt(sdVolt=sdvoltage,statusReg=0,powerSupp=gvar.PowerSupply.VDDH)

                # Condition to set voltage
                if(localVariables["SendOCR"] == localVariables['HcsXpcS18r111']):

                    # Set voltage = 3.3V, Max current = 150mA, A2D Rate : 62.5 Hz
                    sdvoltage.maxCurrent = 150
                    self.__dvtLib.setVolt(sdVolt=sdvoltage,statusReg=0,powerSupp=gvar.PowerSupply.VDDH)

            # checking condition SetPower == 1
            if(SetPower == 1):
                ReceivedOCR_LastAfterPC = ReceivedOCR[0]

            # Call Script Utility CMD20GetSequence
            self.__cmd20getseq.Run(cmd20variables['ExpectSequence'])

            Index = Index + 1
        return 0
    # Testcase Logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_ACMD41_TC005_HSC_XPC_S18A_AllScenarios(self):
        obj = ACMD41_TC005_HSC_XPC_S18A_AllScenarios(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
