"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : UHS_SD3_UT02_Reset.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : UHS_SD3_UT02_Reset.py
# DESCRIPTION                    : Reset Utility
# PRERQUISTE                     : UHS_SD3_UT03_Successful_Verify.py, UHS_SD3_UT04_SuccessfulVerify_MaxVoltage.py
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
    from builtins import str
    from builtins import *

# SDDVT - Dependent TestCases
import UHS_SD3_UT03_Successful_Verify as Successful_Verify
import UHS_SD3_UT04_SuccessfulVerify_MaxVoltage as SuccessfulVerify_MaxVoltage

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
class UHS_SD3_UT02_Reset(customize_log):
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
        self.__Successful_Verify = Successful_Verify.UHS_SD3_UT03_Successful_Verify(self.vtfContainer)
        self.__SuccessfulVerify_MaxVoltage = SuccessfulVerify_MaxVoltage.UHS_SD3_UT04_SuccessfulVerify_MaxVoltage(self.vtfContainer)


    # Testcase Utility Logic - Starts
    def Run(self, LocalVariables):

        RANDOM_BLOCK = 0x0
        SendFirstOCR = LocalVariables['SendOCR']
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SendFirstOCR : %d"%SendFirstOCR)

        SendNextOCR = LocalVariables['SendOCR']
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SendNextOCR : %d"%SendNextOCR)

        globalSpeedMode = self.__config.get('globalSpeedMode')
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalSpeedMode : %s"%globalSpeedMode)

        globalPowerUp = self.__config.get('globalPowerUp')
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalPowerUp : %s"%globalPowerUp)

        # if SetPower = 1, Set No Power, Power
        if LocalVariables['SetPower'] == 1:
            sdcmdWrap.SetPower(0)

            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 400 #For VDDH
            sdVolt.maxVoltage = 3800 # 3.8 V
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 62.5 Hz
            statusReg = 0
            bVddfValue = gvar.PowerSupply.VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            bVddfValue = gvar.PowerSupply.VDDF
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            sdcmdWrap.SetPower(1)

            # Variable not used as per scriptor
            LocalVariables["UHS_MODE"] = 'LS_POWER_CYCLE'

        # Reset Card as per ProtocolMode
        if LocalVariables['ProtocolMode'] == 1 :
            self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.Sd, ocr = LocalVariables['SendOCR'], cardSlot=0x1,
                                sendCmd8=LocalVariables['SendCMD8'], initInfo=None, rca=0x0, time = 0x0,
                                sendCMD0 = LocalVariables['SendCMD0'], bHighCapacity=False, bSendCMD58=False,
                                version=0x0, VOLA=0x1, cmdPattern=0xAA, reserved=0x0, expOCRVal=LocalVariables['ExpectOCR'])

        if LocalVariables['ProtocolMode'] == 2 :
            try:
                self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.Sd, ocr = LocalVariables['SendOCR'], cardSlot=0x1,
                                    sendCmd8=LocalVariables['SendCMD8'], initInfo=None, rca=0x0, time = 0x0,
                                    sendCMD0 = LocalVariables['SendCMD0'], bHighCapacity=False, bSendCMD58=False,
                                    version=0x0, VOLA=0x1, cmdPattern=0xAA, reserved=0x0, expOCRVal=LocalVariables['ExpectOCR'])
            except ValidationError.CVFGenericExceptions as exc:
                # TOBEDONE: Yet to find out which one is the expected error whether "CARD_IS_NOT_RESPONDING" or "CARD_IS_NOT_READY"
                self.__dvtLib.Expected_Failure_Check(exc, "CARD_IS_NOT_READY", "Reset")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_READY error not occurred")

        if LocalVariables['Identification'] == 1:
            if LocalVariables['ProtocolMode'] == 1:
                if LocalVariables['UHS'] == 1:
                    if LocalVariables['SEND_CMD11'] == 1:

                        #SwitchVolt_CMD11
                        self.__dvtLib.SwitchVolt_CMD11()

                    #Identification
                    self.__dvtLib.Identification()

                    #Select Card
                    self.__dvtLib.SelectCard()

                    # Set BusWidth = 4
                    self.__dvtLib.SetBusWidth(busWidth=4)

                    # Variable Declaration for support
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VS_Flag========================%s" % str(LocalVariables['VS_FLAG']))
                    supported = LocalVariables["listData"]
                    supported[1] = supported[1] & (0xBFFF | (0x4000 * LocalVariables['VS_FLAG']))
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "supported========================%s" % str(supported))

                    if RANDOM_BLOCK == 0:

                        #Call Switch Command for check mode / Check,Expected Status Available
                        mode = gvar.CMD6.CHECK
                        arglist = [0x0,0xF,0xF,0xF,0xF,0xF]
                        blockSize = 0x40
                        switched = [0x0,0x0,0x0,0x0,0x0,0x0]
                        responseCompare = True #compare True
                        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for match To Value

                        self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                        responseCompare=responseCompare,
                                                        compareConsumption=consumption,compareValue=100,
                                                        compareSupported=supported,
                                                        comparedSwitched=switched)

                        #Call Switch Command for switch mode / Switch,Expected Status Available
                        mode = gvar.CMD6.SWITCH
                        arglist = [0x0,0xF,0xF,0xF,0xF,0xF]
                        blockSize = 0x40
                        switched = [0x0,0x0,0x0,0x0,0x0,0x0]
                        responseCompare = True #compare true
                        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for match To Value

                        self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                        responseCompare=responseCompare,
                                                        compareConsumption=consumption,compareValue=100,
                                                        compareSupported=supported,
                                                        comparedSwitched=switched)

                        #Set Frequency to 25000 KHz
                        self.__sdCmdObj.SetFrequency(25000) #Passed in KHz

                        #Call Switch Command for check mode / Check,Expected Status Available
                        mode = gvar.CMD6.CHECK
                        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
                        blockSize = 0x40
                        switched = [0x0,0x0,0x0,0x0,0x0,0x0]
                        responseCompare = True #compare True
                        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for match To Value

                        self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                        responseCompare=responseCompare,
                                                        compareConsumption=consumption,compareValue=100,
                                                        compareSupported=supported,
                                                        comparedSwitched=switched)

                        # Variable not used as per scriptor
                        LocalVariables["UHS_MODE"] = 'SDR12'

                        #Set Volt
                        sdVolt = sdcmdWrap.SVoltage()
                        sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
                        sdVolt.voltage = 3300 # 3.30 V
                        sdVolt.maxCurrent = 250 #For VDDH
                        sdVolt.maxVoltage = 3300
                        sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 62.5 Hz
                        statusReg = 0
                        bVddfValue = gvar.PowerSupply.VDDH
                        self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

                        if ((LocalVariables['CARD_CAPACITY'] >= 64) and (LocalVariables['SendOCR'] == LocalVariables['HcsXpcS18r111'])):
                            # Set Volt
                            sdVolt = sdcmdWrap.SVoltage()
                            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
                            sdVolt.voltage = 3300 # 3.30 V
                            sdVolt.maxCurrent = 250 #For VDDH
                            sdVolt.maxVoltage = 3300
                            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 62.5 Hz
                            statusReg = 0
                            bVddfValue = gvar.PowerSupply.VDDH
                            self.__dvtLib.setVolt(sdVolt, statusReg,bVddfValue)

                    elif RANDOM_BLOCK == 1:
                        #Call Switch Command for check mode / Check,Expected Status Available
                        mode = gvar.CMD6.CHECK
                        arglist = [0x1,0xF,0xF,0xF,0xF,0xF]
                        blockSize = 0x40
                        switched = [0x1,0x0,0x0,0x0,0x0,0x0]
                        responseCompare = True #compare True
                        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for match To Value

                        self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                        responseCompare=responseCompare,
                                                        compareConsumption=consumption,compareValue=200,
                                                        compareSupported=supported,
                                                        comparedSwitched=switched)

                        #Call Switch Command for switch mode / Switch,Expected Status Available
                        mode = gvar.CMD6.SWITCH
                        arglist = [0x1,0xF,0xF,0xF,0xF,0xF]
                        blockSize = 0x40
                        switched = [0x1,0x0,0x0,0x0,0x0,0x0]
                        responseCompare = True #compare true
                        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for match To Value

                        self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                        responseCompare=responseCompare,
                                                        compareConsumption=consumption,compareValue=200,
                                                        compareSupported=supported,
                                                        comparedSwitched=switched)

                        #Set Frequency to 50000 KHz
                        self.__sdCmdObj.SetFrequency(50000) #Passed in KHz

                        #Call Switch Command for check mode / Check,Expected Status Available
                        mode = gvar.CMD6.CHECK
                        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
                        blockSize = 0x40
                        switched = [0x1,0x0,0x0,0x0,0x0,0x0]
                        responseCompare = True #compare True
                        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for match To Value

                        self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                        responseCompare=responseCompare,
                                                        compareConsumption=consumption,compareValue=200,
                                                        compareSupported=supported,
                                                        comparedSwitched=switched)

                        # Variable not used as per scriptor
                        LocalVariables["UHS_MODE"] = 'SDR25'

                        #Set Volt
                        sdVolt = sdcmdWrap.SVoltage()
                        sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
                        sdVolt.voltage = 3300 # 3.30 V
                        sdVolt.maxCurrent = 250 #For VDDH
                        sdVolt.maxVoltage = 3300 # 3.3 V
                        sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 62.5 Hz
                        statusReg = 0
                        bVddfValue = gvar.PowerSupply.VDDH
                        self.__dvtLib.setVolt(sdVolt, statusReg,bVddfValue)

                    elif RANDOM_BLOCK ==2:
                        #Call Switch Command for check mode / Check,Expected Status Available
                        mode = gvar.CMD6.CHECK
                        arglist = [0x2,0xF,0xF,0x1,0xF,0xF]
                        blockSize = 0x40
                        swicthed = [0x2,0x0,0x0,0x1,0x0,0x0]
                        responseCompare = True #compare True
                        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for match To Value

                        self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                        responseCompare=responseCompare,
                                                        compareConsumption=consumption,compareValue=250,
                                                        compareSupported=supported,
                                                        comparedSwitched=switched)

                        #Call Switch Command for switch mode / Switch,Expected Status Available
                        mode = gvar.CMD6.SWITCH
                        arglist = [0x2,0xF,0xF,0x1,0xF,0xF]
                        blockSize = 0x40
                        switched = [0x2,0x0,0x0,0x1,0x0,0x0]
                        responseCompare = True #compare true
                        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for match To Value

                        self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                        responseCompare=responseCompare,
                                                        compareConsumption=consumption,compareValue=250,
                                                        compareSupported=supported,
                                                        comparedSwitched=switched)

                        #Set Frequency to 100000 KHz
                        self.__sdCmdObj.SetFrequency(100000) #Passed in KHz

                        #Get Frequency
                        self.__sdCmdObj.GetFrequency()

                        #Call Switch Command for check mode / Check,Expected Status Available
                        mode = gvar.CMD6.CHECK
                        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
                        blockSize = 0x40
                        switched = [0x2,0x0,0x0,0x1,0x0,0x0]
                        responseCompare = True #compare True
                        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for match To Value

                        self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                        responseCompare=responseCompare,
                                                        compareConsumption=consumption,compareValue=250,
                                                        compareSupported=supported,
                                                        comparedSwitched=switched)

                        numOfCmd = random.randrange(0, 40) + 1
                        timeOut = 150
                        bufErr = ServiceWrap.Buffer.CreateBuffer(1, 0)
                        self.__dvtLib.SEND_TUNING_PATTERN(numOfCmd, timeOut, bufErr)

                        # Variable not used as per scriptor
                        LocalVariables["UHS_MODE"] = 'SDR50'

                        #Set Volt
                        sdVolt = sdcmdWrap.SVoltage()
                        sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
                        sdVolt.voltage = 3300 # 3.30 V
                        sdVolt.maxCurrent = 300 #For VDDH
                        sdVolt.maxVoltage = 3300
                        sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 62.5 Hz
                        statusReg = 0
                        bVddfValue = gvar.PowerSupply.VDDH
                        self.__dvtLib.setVolt(sdVolt, statusReg,bVddfValue)

                    elif RANDOM_BLOCK == 3:
                        #Call Switch Command for check mode / Check,Expected Status Available
                        mode = gvar.CMD6.CHECK
                        arglist = [0x4,0xF,0xF,0x1,0xF,0xF]
                        blockSize = 0x40
                        switched = [0x4,0x0,0x0,0x1,0x0,0x0]
                        responseCompare = True #compare True
                        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for match To Value

                        self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                        responseCompare=responseCompare,
                                                        compareConsumption=consumption,compareValue=250,
                                                        compareSupported=supported,
                                                        comparedSwitched=switched)

                        #Call Switch Command for switch mode / Switch,Expected Status Available
                        mode = gvar.CMD6.SWITCH
                        arglist = [0x4,0xF,0xF,0xF,0xF,0xF]
                        blockSize = 0x40
                        switched = [0x4,0x0,0x0,0x1,0x0,0x0]
                        responseCompare = True #compare true
                        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for match To Value

                        self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                        responseCompare=responseCompare,
                                                        compareConsumption=consumption,compareValue=250,
                                                        compareSupported=supported,
                                                        comparedSwitched=switched)

                        #Set Frequency to 50000 KHz
                        self.__sdCmdObj.SetFrequency(50000) #Passed in KHz

                        #Call Switch Command for check mode / Check,Expected Status Available
                        mode = gvar.CMD6.CHECK
                        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
                        blockSize = 0x40
                        switched = [0x4,0x0,0x0,0x1,0x0,0x0]
                        responseCompare = True #compare True
                        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for match To Value

                        self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                        responseCompare=responseCompare,
                                                        compareConsumption=consumption,compareValue=250,
                                                        compareSupported=supported,
                                                        comparedSwitched=switched)

                        # Variable not used as per scriptor
                        LocalVariables["UHS_MODE"] = 'DDR50'

                        #Set Volt
                        sdVolt = sdcmdWrap.SVoltage()
                        sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
                        sdVolt.voltage = 3300 # 3.30 V
                        sdVolt.maxCurrent = 250 #For VDDH
                        sdVolt.maxVoltage = 3300 # 3.3 V
                        sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 62.5 Hz
                        statusReg = 0
                        bVddfValue = gvar.PowerSupply.VDDH
                        self.__dvtLib.setVolt(sdVolt, statusReg,bVddfValue)

                    elif RANDOM_BLOCK ==4:
                        #Call Switch Command for check mode / Check,Expected Status Available
                        mode = gvar.CMD6.CHECK
                        arglist = [0x3,0xF,0x1,0x1,0xF,0xF]
                        blockSize = 0x40
                        switched = [0x3,0x0,0x1,0x1,0x0,0x0]
                        responseCompare = True #compare True
                        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for match To Value

                        self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                        responseCompare=responseCompare,
                                                        compareConsumption=consumption,compareValue=250,
                                                        compareSupported=supported,
                                                        comparedSwitched=switched)

                        #Call Switch Command for switch mode / Switch,Expected Status Available
                        mode = gvar.CMD6.SWITCH
                        arglist = [0x3,0xF,0x1,0x1,0xF,0xF]
                        blockSize = 0x40
                        switched = [0x3,0x0,0x1,0x1,0x0,0x0]
                        responseCompare = True #compare true
                        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for match To Value

                        self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                        responseCompare=responseCompare,
                                                        compareConsumption=consumption,compareValue=250,
                                                        compareSupported=supported,
                                                        comparedSwitched=switched)

                        #Set Frequency to 200000 KHz
                        self.__sdCmdObj.SetFrequency(200000) #Passed in KHz

                        #Get Frequency
                        self.__sdCmdObj.GetFrequency()

                        #Call Switch Command for check mode / Check,Expected Status Available
                        mode = gvar.CMD6.CHECK
                        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
                        blockSize = 0x40
                        switched = [0x3,0x0,0x1,0x1,0x0,0x0]
                        responseCompare = True #compare True
                        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for match To Value

                        self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                        responseCompare=responseCompare,
                                                        compareConsumption=consumption,compareValue=250,
                                                        compareSupported=supported,
                                                        comparedSwitched=switched)

                        numOfCmd = random.randrange(0, 40) + 1
                        timeOut = 150
                        bufErr = ServiceWrap.Buffer.CreateBuffer(1,0)
                        self.__dvtLib.SEND_TUNING_PATTERN(numOfCmd, timeOut, bufErr)

                        # Variable not used as per scriptor
                        LocalVariables["UHS_MODE"] = 'SDR104'

                        #Set Volt
                        sdVolt = sdcmdWrap.SVoltage()
                        sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
                        sdVolt.voltage = 3300 # 3.30 V
                        sdVolt.maxCurrent = 400 #For VDDH
                        sdVolt.maxVoltage = 3300
                        sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 62.5 Hz
                        statusReg = 0
                        bVddfValue = gvar.PowerSupply.VDDH
                        self.__dvtLib.setVolt(sdVolt, statusReg,bVddfValue)

                    # Get CSD Values
                    CSD_Reg_Values= self.__sdCmdObj.GET_CSD_VALUES()
                    self.__sdCmdObj.Cmd7()

                    # Get SD Status
                    GET_Sd_Status = self.__dvtLib.GetSDStatus()
                else:

                    #Identification
                    self.__dvtLib.Identification()

                    # Get CSD Values
                    CSD_Reg_Values= self.__sdCmdObj.GET_CSD_VALUES()
                    self.__sdCmdObj.Cmd7()

                    if LocalVariables['SendACMD6'] == 0:
                        # Set BusWidth = 1
                        self.__dvtLib.SetBusWidth(busWidth=1) #set bus width to 1
                    if LocalVariables['SendACMD6'] == 1:
                        # Set BusWidth = 4
                        self.__dvtLib.SetBusWidth(busWidth=4) #set bus width to 4

                    #Variable not sure
                    if LocalVariables['Turn_HS_ON'] == 1:

                        supported= [0x8003,(0xC001 & (0xBFFF | (0x4000 * LocalVariables['VS_FLAG']))),0x8001,0x8001,0x8001,0x8001]

                        #Call Switch Command for switch mode / Switch,Expected Status Available
                        mode = gvar.CMD6.SWITCH
                        arglist = [0x1,0xF,0xF,0xF,0xF,0xF]
                        blockSize = 0x40
                        switched = [0x1,0x0,0x0,0x0,0x0,0x0]
                        responseCompare = True #compare true
                        consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR #for Not Error
                        self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                                     responseCompare=responseCompare,
                                                                     compareConsumption=consumption,
                                                                     compareSupported=supported,
                                                                     comparedSwitched=switched)

                        #Call Switch Command for check mode / Switch,Expected Status Available
                        mode = gvar.CMD6.CHECK
                        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
                        blockSize = 0x40
                        swicthed = [0x1,0x0,0x0,0x0,0x0,0x0]
                        responseCompare = True #compare true
                        consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR #for Not Error
                        self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                                        responseCompare=responseCompare,
                                                        compareConsumption=consumption,
                                                        compareSupported=supported,
                                                        comparedSwitched=swicthed)

                        # Variable not used as per scriptor
                        LocalVariables["UHS_MODE"] = 'LEGACY_HS'

                    #Set Volt
                    sdVolt = sdcmdWrap.SVoltage()
                    sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
                    sdVolt.voltage = 3300 # 3.30 V
                    sdVolt.maxCurrent = 250 #For VDDH
                    sdVolt.maxVoltage = 3300 # 3.3 V
                    sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 62.5 Hz
                    statusReg = 0
                    bVddfValue = gvar.PowerSupply.VDDH
                    self.__dvtLib.setVolt(sdVolt, statusReg,bVddfValue)

                    if ((LocalVariables['CARD_CAPACITY'] >= 64) and (LocalVariables['SendOCR'] == LocalVariables['HcsXpcS18r111']) and (LocalVariables['Turn_HS_ON'] == 0)):
                        #Set Volt
                        sdVolt = sdcmdWrap.SVoltage()
                        sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
                        sdVolt.voltage = 3300 # 3.30 V
                        sdVolt.maxCurrent =  250 #For VDDH
                        sdVolt.maxVoltage = 3300
                        sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 62.5 Hz
                        statusReg = 0
                        bVddfValue = gvar.PowerSupply.VDDH
                        self.__dvtLib.setVolt(sdVolt, statusReg,bVddfValue)

                    #Call script Utility_Successful_Verify_MaxVoltage
                    self.__SuccessfulVerify_MaxVoltage.Run()

        if LocalVariables['VerifyType'] == 1:
            RANDOM_BLOCK =self.__Successful_Verify.Run()
        elif LocalVariables['VerifyType'] == 3:
            self.__SuccessfulVerify_MaxVoltage.Run()

        return 0



    # Testcase Utility Logic - Ends
# Testcase Utility Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_UHS_SD3_UT02_Reset(self):
        obj = UHS_SD3_UT02_Reset(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
