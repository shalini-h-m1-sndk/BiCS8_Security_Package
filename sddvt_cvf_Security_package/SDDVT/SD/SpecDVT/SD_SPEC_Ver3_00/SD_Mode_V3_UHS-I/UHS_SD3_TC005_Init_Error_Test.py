"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : UHS_SD3_TC005_Init_Error_Test.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : UHS_SD3_TC005_Init_Error_Test.py
# DESCRIPTION                    : Reset Utility
# PRERQUISTE                     : UHS_SD3_UT01_LoadLocal_Variables.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=UHS_SD3_TC005_Init_Error_Test --isModel=false --enable_console_log=1 --adapter=0
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
    from builtins import str
    from builtins import range
    from builtins import *

# SDDVT - Dependent TestCases
import UHS_SD3_UT01_LoadLocal_Variables as LoadLocalVariables

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


# Testcase Class - Begins
class UHS_SD3_TC005_Init_Error_Test(customize_log):
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
        self.__LoadLocal_Variables = LoadLocalVariables.UHS_SD3_UT01_LoadLocal_Variables(self.vtfContainer)


    # Testcase logic - Starts
    def UHS_RESET(self, LocalVariables):
        LocalVariables['SendCMD0'] = random.randrange(0, 2)
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        # Do card Reset
        self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=LocalVariables['HcsXpcS18r101'], cardSlot=0x1, sendCmd8=True,
                            initInfo=None, rca=0x0, time=0x0, sendCMD0=LocalVariables['SendCMD0'], bHighCapacity=True,
                            bSendCMD58=False, version=0x0, VOLA=1, cmdPattern=0xAA, reserved=0x0,
                            expOCRVal=LocalVariables['ReadyCcs18a111'])

        # SwitchVolt_CMD11
        self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)  # CMD11 - Host switched to 1.8

        # Identify Card
        self.__dvtLib.Identification()

        # Select card
        self.__sdCmdObj.Cmd7()

        # Set BusWidth = 4
        self.__dvtLib.SetBusWidth(busWidth = 4)

        supported= LocalVariables["listData"]
        supported[1] = supported[1] & ((0x4000 * LocalVariables['VS_FLAG']) + 0xBFFF)

        if LocalVariables['RANDOM_UHS_MODE'] == 0:
            LocalVariables['UHS_MODE'] = 0x0

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.CHECK
            arglist = [LocalVariables['UHS_MODE'],0xF,0xF,0xF,0xF,0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR
            self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.SWITCH
            arglist = [LocalVariables['UHS_MODE'],0xF,0xF,0xF,0xF,0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR
            self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

            # Set SET_FREQ = rand%15000 + 10000
            SET_FREQ = random.randrange(0, 15000) + 10000

            self.__sdCmdObj.SetFrequency(SET_FREQ)

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.CHECK
            arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR
            self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

            # Set Voltage.
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300  #3.3V
            sdVolt.maxCurrent = 100 # 100 mA
            sdVolt.maxVoltage = 3800 # 3.8 V
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 625Hz
            statusReg = 0
            bVddhValue = gvar.PowerSupply.VDDH #for VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddhValue)

            if ((LocalVariables['CARD_CAPACITY'] >= 64) and (LocalVariables['SendOCR'] == LocalVariables['HcsXpcS18r111'])):
                # Set Voltage.
                sdVolt = sdcmdWrap.SVoltage()
                sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
                sdVolt.voltage = 3300  #3.3V
                sdVolt.maxCurrent = 150 # 150 mA
                sdVolt.maxVoltage = 3800 # 3.8 V
                sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 625Hz
                statusReg = 0
                bVddhValue = gvar.PowerSupply.VDDH #for VDDH
                self.__dvtLib.setVolt(sdVolt, statusReg, bVddhValue)

        if LocalVariables['RANDOM_UHS_MODE'] == 1:
            LocalVariables['UHS_MODE'] = 0x1

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.CHECK
            arglist = [LocalVariables['UHS_MODE'],0xF,0xF,0xF,0xF,0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR
            self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.SWITCH
            arglist = [LocalVariables['UHS_MODE'],0xF,0xF,0xF,0xF,0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR
            self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

            # Set_FREQ = rand%25000 + 25000
            SET_FREQ = random.randrange(0, 25000) + 25000

            self.__sdCmdObj.SetFrequency(SET_FREQ)

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.CHECK
            arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR
            self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

            # Set Voltage.
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300  #3.3V
            sdVolt.maxCurrent = 200 # 200 mA
            sdVolt.maxVoltage = 3800 # 3.8 V
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 625Hz
            statusReg = 0
            bVddhValue = gvar.PowerSupply.VDDH #for VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddhValue)

        if LocalVariables['RANDOM_UHS_MODE'] == 2:
            LocalVariables['UHS_MODE'] = 0x2    # SDR50

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.CHECK
            arglist = [LocalVariables['UHS_MODE'],0xF,0xF,0x1,0xF,0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x1,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR

            self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.SWITCH
            arglist = [LocalVariables['UHS_MODE'],0xF,0xF,0x1,0xF,0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x1,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR

            self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

            # Set_FREQ = rand%30000 + 70000
            SET_FREQ = random.randrange(0, 30000) + 70000

            self.__sdCmdObj.SetFrequency(SET_FREQ)

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.CHECK
            arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x1,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR
            self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

            # Set Voltage.
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300  #3.3V
            sdVolt.maxCurrent = 250 # 250 mA
            sdVolt.maxVoltage = 3800 # 3.8 V
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 625Hz
            statusReg = 0
            bVddhValue = gvar.PowerSupply.VDDH #for VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddhValue)

        if LocalVariables['RANDOM_UHS_MODE'] == 3:
            LocalVariables['UHS_MODE'] = 0x4

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.CHECK
            arglist = [LocalVariables['UHS_MODE'],0xF,0xF,0x1,0xF,0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x1,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR
            self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.SWITCH
            arglist = [LocalVariables['UHS_MODE'],0xF,0xF,0x1,0xF,0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x1,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR
            self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

            # Set_FREQ = rand%25000 + 25000
            SET_FREQ = random.randrange(0, 25000) + 25000

            self.__sdCmdObj.SetFrequency(SET_FREQ)

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.CHECK
            arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x1,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR
            self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

            # Set Voltage.
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300  #3.3V
            sdVolt.maxCurrent = 250 # 250 mA
            sdVolt.maxVoltage = 3800 # 3.8 V
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 625Hz
            statusReg = 0
            bVddhValue = gvar.PowerSupply.VDDH #for VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddhValue)

        if LocalVariables['RANDOM_UHS_MODE'] == 4:
            if ((supported[0] & 0x8) != 0):
                LocalVariables['UHS_MODE'] = 0x3

                # Call Switch Command for check mode / Check, Expected Status Available
                mode = gvar.CMD6.CHECK
                arglist = [LocalVariables['UHS_MODE'],0xF,0x1,0x1,0xF,0xF]
                blockSize = 0x40
                switched = [LocalVariables['UHS_MODE'],0x0,0x1,0x1,0x0,0x0]
                responseCompare = True #compare True
                consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR
                self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                responseCompare=responseCompare,
                                                compareConsumption=consumption,
                                                compareSupported=supported,
                                                comparedSwitched=switched)

                # Call Switch Command for check mode / Check, Expected Status Available
                mode = gvar.CMD6.SWITCH
                arglist = [LocalVariables['UHS_MODE'],0xF,0x1,0x1,0xF,0xF]
                blockSize = 0x40
                switched = [LocalVariables['UHS_MODE'],0x0,0x1,0x1,0x0,0x0]
                responseCompare = True #compare True
                consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR
                self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                responseCompare=responseCompare,
                                                compareConsumption=consumption,
                                                compareSupported=supported,
                                                comparedSwitched=switched)

                # Set_FREQ = rand%2
                SET_FREQ = random.randrange(0, 2)

                if SET_FREQ == 0:
                    SET_FREQ = 200000
                else:
                    SET_FREQ = 150000

                self.__sdCmdObj.SetFrequency(SET_FREQ)

                # Call Switch Command for check mode / Check, Expected Status Available
                mode = gvar.CMD6.CHECK
                arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
                blockSize = 0x40
                switched = [LocalVariables['UHS_MODE'],0x0,0x1,0x1,0x0,0x0]
                responseCompare = True #compare True
                consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR
                self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                responseCompare=responseCompare,
                                                compareConsumption=consumption,
                                                compareSupported=supported,
                                                comparedSwitched=switched)

                # Send tuning pattern
                numOfCmd = random.randrange(0, 40) + 1
                timeOut = 150
                bufferError = ServiceWrap.Buffer.CreateBuffer(1, 0)
                self.__dvtLib.SEND_TUNING_PATTERN(numOfCmd, timeOut, bufferError)

                # Set Voltage.
                sdVolt = sdcmdWrap.SVoltage()
                sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
                sdVolt.voltage = 3300  #3.3V
                sdVolt.maxCurrent = 400 # 400 mA
                sdVolt.maxVoltage = 3800 # 3.8 V
                sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 625Hz
                statusReg = 0
                bVddhValue = gvar.PowerSupply.VDDH #for VDDH
                self.__dvtLib.setVolt(sdVolt, statusReg, bVddhValue)
    # End Block UHS_RESET


    def UHS_SOFT_RESET(self, LocalVariables):
        # Do card Reset - S18R = RANDOM S18A = 0
        self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=LocalVariables['S18R'], cardSlot=0x1, sendCmd8=True,
                            initInfo=None, rca=0x0, time=0x0, sendCMD0=0x1,
                            bHighCapacity=True, bSendCMD58=False, version=0x0, VOLA=1, cmdPattern=0xAA,
                            reserved=0x0, expOCRVal=LocalVariables['ReadyCcs18a110'])

        if LocalVariables['SEND_CMD11'] == 1:
            # SwitchVolt_CMD11
            self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)  # CMD11 - Host switched to 1.8

        # Identify Card
        self.__dvtLib.Identification()

        # Select card
        self.__sdCmdObj.Cmd7()

        if LocalVariables['SendACMD6'] == 1:
            # Set BusWidth = 4
            self.__dvtLib.SetBusWidth(busWidth = 4)
    # End Block UHS_SOFT_RESET


    def Run(self):
        # Initialize the SD card
        self.__sdCmdObj.DoBasicInit()

        # Call Utility_LoadLocal_Variables
        LocalVariables = self.__LoadLocal_Variables.Run()

        for loop in range(0, 10):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Loop for 10 times, Current iteration is %s\n" % (loop + 1))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "UHS-I reset + power cycle\n")

            LocalVariables['RANDOM_UHS_MODE'] = 2
            self.UHS_RESET(LocalVariables)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "UHS-I reset (no power cycle)\n")

            #Tag Block RANDOM_UHS_MODE
            LocalVariables['RANDOM_S18R'] = random.randrange(0, 2)

            if LocalVariables['RANDOM_S18R'] == 0:
                LocalVariables['S18R'] = LocalVariables['HcsXpcS18r100']
            if LocalVariables['RANDOM_S18R'] == 1:
                LocalVariables['S18R'] = LocalVariables['HcsXpcS18r101']

            LocalVariables['SEND_CMD11'] = 0
            LocalVariables['SendACMD6'] = 1
            self.UHS_SOFT_RESET(LocalVariables)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Error oriented tests - Without S18R\n")

            LocalVariables['SendCMD0'] = random.randrange(0, 2)
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)

            # Do card Reset
            self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=LocalVariables['HcsXpcS18r100'], cardSlot=0x1,
                                sendCmd8=True, initInfo=None, rca=0x0, time=0x0, sendCMD0=LocalVariables['SendCMD0'],
                                bHighCapacity=True, bSendCMD58=False, version=0x0, VOLA=1, cmdPattern=0xAA,
                                reserved=0x0, expOCRVal=LocalVariables['ReadyCcs18a110'])

            # SwitchVolt_CMD11
            try:
                self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "SwitchVolt_CMD11")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING error not occurred")

            # Identify Card
            try:
                self.__dvtLib.Identification()
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, "CARD_ILLEGAL_CMD", "Identification")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_ILLEGAL_CMD error not occurred")

            # Select card
            self.__sdCmdObj.Cmd7()

            # Set BusWidth = 4
            self.__dvtLib.SetBusWidth(busWidth = 4)

            LocalVariables['UHS_MODE'] = 0x2    # SDR50
            SET_FREQ = random.randrange(0, 30000) + 70000

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.SWITCH
            arglist = [LocalVariables['UHS_MODE'],0xF,0xF,0xF,0xF,0xF]
            blockSize = 0x40
            supported = [0x8003,(0xC001 & ((0x4000 * LocalVariables['VS_FLAG']) + 0xBFFF)),0x8001,0x8001,0x8001,0x8001]
            switched = [0xF,0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR
            try:
                self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                responseCompare=responseCompare,
                                                compareConsumption=consumption,
                                                compareSupported=supported,
                                                comparedSwitched=switched)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_ERROR", Operation_Name = "CardSwitchCommand")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_ERROR error didn't occur!!")

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.CHECK
            arglist = [LocalVariables['UHS_MODE'],0xF,0xF,0xF,0xF,0xF]
            blockSize = 0x40
            supported = [0x8003,(0xC001 & ((0x4000 * LocalVariables['VS_FLAG']) + 0xBFFF)),0x8001,0x8001,0x8001,0x8001]
            switched = [0xF,0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR
            try:
                self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                responseCompare=responseCompare,
                                                compareConsumption=consumption,
                                                compareSupported=supported,
                                                comparedSwitched=switched)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_ERROR", Operation_Name = "CardSwitchCommand")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_ERROR error didn't occur!!")

            # Send tuning pattern
            numOfCmd = random.randrange(0, 40) + 1
            Timeout = 150
            bufErr = ServiceWrap.Buffer.CreateBuffer(1, 0x00)
            try:
                self.__dvtLib.SEND_TUNING_PATTERN(numOfCmd=numOfCmd, timeOut=Timeout, bufErr = bufErr)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, "CARD_ILLEGAL_CMD", "SEND_TUNING_PATTERN")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_ILLEGAL_CMD error not occurred")

            LocalVariables['RANDOM_UHS_MODE'] = 2
            self.UHS_RESET(LocalVariables)  # UHS RESET + SWITCH TO SDR50

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Error oriented tests - Without CMD11\n")

            LocalVariables['SendCMD0'] = random.randrange(0, 2)
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)

            # Do card Reset
            self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=LocalVariables['HcsXpcS18r101'], cardSlot=0x1,
                                sendCmd8=True, initInfo=None, rca=0x0, time=0x0, sendCMD0=LocalVariables['SendCMD0'], bHighCapacity=True,
                                bSendCMD58=False, version=0x0, VOLA=1, cmdPattern=0xAA, reserved=0x0,
                                expOCRVal=LocalVariables['ReadyCcs18a111'])

            # Identify Card
            self.__dvtLib.Identification()

            # Select card
            self.__sdCmdObj.Cmd7()

            # Set BusWidth = 4
            self.__dvtLib.SetBusWidth(busWidth = 4)

            LocalVariables['UHS_MODE'] = 0x2    # SDR50
            SET_FREQ = random.randrange(0, 30000) + 70000

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.SWITCH
            arglist = [LocalVariables['UHS_MODE'],0xF,0xF,0xF,0xF,0xF]
            blockSize = 0x40
            supported = [0x8003,(0xC001 & ((0x4000 * LocalVariables['VS_FLAG']) + 0xBFFF)),0x8001,0x8001,0x8001,0x8001]
            switched = [0xF,0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR
            try:
                self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                responseCompare=responseCompare,
                                                compareConsumption=consumption,
                                                compareSupported=supported,
                                                comparedSwitched=switched)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_ERROR", Operation_Name = "CardSwitchCommand")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_ERROR error didn't occur!!")

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.CHECK
            arglist = [LocalVariables['UHS_MODE'],0xF,0xF,0xF,0xF,0xF]
            blockSize = 0x40
            supported = [0x8003,(0xC001 & ((0x4000 * LocalVariables['VS_FLAG']) + 0xBFFF)),0x8001,0x8001,0x8001,0x8001]
            switched = [0xF,0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR
            try:
                self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                responseCompare=responseCompare,
                                                compareConsumption=consumption,
                                                compareSupported=supported,
                                                comparedSwitched=switched)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_ERROR", Operation_Name = "CardSwitchCommand")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_ERROR error didn't occur!!")

            # Send tuning pattern
            numOfCmd = random.randrange(0, 40) + 1
            Timeout = 150
            bufErr = ServiceWrap.Buffer.CreateBuffer(1, 0x00)
            try:
                self.__dvtLib.SEND_TUNING_PATTERN(numOfCmd=numOfCmd, timeOut=Timeout, bufErr = bufErr)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, "CARD_ILLEGAL_CMD", "SEND_TUNING_PATTERN")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_ILLEGAL_CMD error not occurred")

            LocalVariables['RANDOM_UHS_MODE'] = 2

            self.UHS_RESET(LocalVariables)  # UHS RESET + SWITCH TO SDR50

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Error oriented tests - Send CMD11 twice\n")

            LocalVariables['SendCMD0'] = random.randrange(0, 2)
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)

            # Do card Reset
            self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=LocalVariables['HcsXpcS18r101'], cardSlot=0x1, sendCmd8=True,
                                initInfo=None, rca=0x0, time=0x0, sendCMD0=LocalVariables['SendCMD0'], bHighCapacity=True,
                                bSendCMD58=False, version=0x0, VOLA=1, cmdPattern=0xAA, reserved=0x0,
                                expOCRVal=LocalVariables['ReadyCcs18a111'])

            # SwitchVolt_CMD11
            self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)  # CMD11 - Host switched to 1.8

            # SwitchVolt_CMD11
            try:
                self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_RESPONDING", "SwitchVolt_CMD11")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING error not occurred")

            # Identify Card
            try:
                self.__dvtLib.Identification()
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, "CARD_ILLEGAL_CMD", "Identification")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_ILLEGAL_CMD error not occurred")


            # Select card
            self.__sdCmdObj.Cmd7()

            # Set BusWidth = 4
            self.__dvtLib.SetBusWidth(busWidth = 4)

            LocalVariables['UHS_MODE'] = 0x2    # SDR50
            SET_FREQ = random.randrange(0, 30000) + 70000

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VS_Flag========================%s" % str(LocalVariables['VS_FLAG']))
            supported= LocalVariables["listData"]
            supported[1] = supported[1] & ((0x4000 * LocalVariables['VS_FLAG']) + 0xBFFF)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "supported========================%s" % str(supported))

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.SWITCH
            arglist = [LocalVariables['UHS_MODE'],0xF,0xF,0xF,0xF,0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR

            self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

            self.__sdCmdObj.SetFrequency(SET_FREQ)

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.CHECK
            arglist = [LocalVariables['UHS_MODE'],0xF,0xF,0xF,0xF,0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR
            self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

            # Send tuning pattern
            numOfCmd = random.randrange(0, 40) + 1
            timeOut = 150
            bufferError = ServiceWrap.Buffer.CreateBuffer(1, 0)
            self.__dvtLib.SEND_TUNING_PATTERN(numOfCmd, timeOut, bufferError)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Error oriented tests - Without ACMD6 (Soft Reset before ACMD6)\n")
            LocalVariables['SendCMD0'] = random.randrange(0,  2)

            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)

            # Do card Reset
            self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=LocalVariables['HcsXpcS18r101'], cardSlot=0x1, sendCmd8=True,
                                initInfo=None, rca=0x0, time=0x0, sendCMD0=LocalVariables['SendCMD0'], bHighCapacity=True,
                                bSendCMD58=False, version=0x0, VOLA=1, cmdPattern=0xAA, reserved=0x0,
                                expOCRVal=LocalVariables['ReadyCcs18a111'])

            # SwitchVolt_CMD11
            self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)

            # Identify Card
            self.__dvtLib.Identification()

            # Select card
            self.__sdCmdObj.Cmd7()

            LocalVariables['UHS_MODE'] = 0x2    # SDR50
            SET_FREQ = random.randrange(0, 30000) + 70000

            # Do card Reset
            self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=LocalVariables['HcsXpcS18r101'], cardSlot=0x1, sendCmd8=True,
                                initInfo=None, rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True, bSendCMD58=False,
                                version=0x0, VOLA=1, cmdPattern=0xAA, reserved=0x0, expOCRVal=LocalVariables['ReadyCcs18a110'])

            # Identify Card
            self.__dvtLib.Identification()

            # Select card
            self.__sdCmdObj.Cmd7()

            # Set BusWidth = 4
            self.__dvtLib.SetBusWidth(busWidth = 4)

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.SWITCH
            arglist = [LocalVariables['UHS_MODE'],0xF,0xF,0xF,0xF,0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR
            self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

            self.__sdCmdObj.SetFrequency(SET_FREQ)

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.CHECK
            arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR
            self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

            # Send tuning pattern
            numOfCmd = random.randrange(0, 40) + 1
            timeOut = 150
            bufferError = ServiceWrap.Buffer.CreateBuffer(1,0)
            self.__dvtLib.SEND_TUNING_PATTERN(numOfCmd, timeOut, bufferError)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Error oriented tests - out of UHS-1 mode in illegal way\n")

            for loop1 in range(0, 5):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Loop for 5 times, Current iteration is %s\n" % (loop1 + 1))

                LocalVariables['RANDOM_UHS_MODE'] = 0
                self.UHS_RESET(LocalVariables)
                LocalVariables['S18R'] = LocalVariables['HcsXpcS18r100']

                SET_S18R1 = 2
                while SET_S18R1 > 0:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SET_S18R1 loop for 2 times, Current iteration is(In reverse order) %s\n" % SET_S18R1)

                    LocalVariables['SEND_CMD11']  = 0
                    LocalVariables['SendACMD6'] = 1
                    self.UHS_SOFT_RESET(LocalVariables)
                    self.UHS_RESET(LocalVariables)

                    LocalVariables['SendACMD6'] = 0
                    self.UHS_SOFT_RESET(LocalVariables)
                    self.UHS_RESET(LocalVariables)

                    LocalVariables['SEND_CMD11']  = 1
                    LocalVariables['SendACMD6'] = 1
                    self.UHS_SOFT_RESET(LocalVariables)
                    self.UHS_RESET(LocalVariables)

                    LocalVariables['SendACMD6'] = 0
                    self.UHS_SOFT_RESET(LocalVariables)
                    self.UHS_RESET(LocalVariables)

                    LocalVariables['S18R'] = LocalVariables['HcsXpcS18r101']
                    SET_S18R1 = SET_S18R1 - 1

                LocalVariables['RANDOM_UHS_MODE'] += 1

        return 0

    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_UHS_SD3_TC005_Init_Error_Test(self):
        obj = UHS_SD3_TC005_Init_Error_Test(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
