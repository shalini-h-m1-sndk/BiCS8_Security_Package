"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : UHS_SD3_UT01_LoadLocal_Variables.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : UHS_SD3_UT01_LoadLocal_Variables.py
# DESCRIPTION                    : Load the variables for the main scripts
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : No. It is an utility script.
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : Nov-2022
################################################################################
"""

# Python future modules for python3 forward compatibility
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    from builtins import *
from past.utils import old_div

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
import time
from inspect import currentframe, getframeinfo

# Global Variables
OCR_VAL1 = 0x80000000
OCR_VAL2 = 0x40000000
OCR_VAL3 = 0x10000000

# Testcase Utility Class - Begins
class UHS_SD3_UT01_LoadLocal_Variables(customize_log):
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


    # Testcase Utility Logic - Starts
    def compare(self, CMD6):
        FUNC1 = CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup1
        FUNC2 = CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup2
        FUNC3 = CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup3
        FUNC4 = CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup4
        FUNC5 = CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup5
        FUNC6 = CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup6
        return [FUNC1, FUNC2, FUNC3, FUNC4, FUNC5, FUNC6]


    def Run(self):
        """
        Name : Run
        """

        #Call globalInitCard.st3
        globalprojectConfig = self.__sdCmdObj.DoBasicInit()

        # Set Power off
        sdcmdWrap.SetPower(0)

        # Set Volt
        sdVolt = sdcmdWrap.SVoltage()
        sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
        sdVolt.voltage = 3300 # 3.30 V
        sdVolt.maxCurrent = 200 #For VDDH
        sdVolt.maxVoltage = 3800 # 3.8 V
        sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 62.5 Hz
        statusReg = 0
        self.__dvtLib.setVolt(sdVolt, statusReg, gvar.PowerSupply.VDDH)

        sdVolt.maxCurrent = 400 #For VDDF
        self.__dvtLib.setVolt(sdVolt, statusReg, gvar.PowerSupply.VDDF)

        sdcmdWrap.SetPower(1)

        globalOCRArgValue = int(globalprojectConfig['globalOCRArgValue'])
        globalOCRArgValue_Temp = int(((globalOCRArgValue | 0x40000000) & 0xEFFFFFFF) | 0x1000000)
        globalOCRResValue = int(globalprojectConfig['globalOCRResValue'])
        globalOCRResValue_Temp = int(((globalOCRResValue | 0x80000000) | 0x40000000) | 0x1000000)
        mode = sdcmdWrap.CARD_MODE.Sd

        #RESET and Identification with ocr =globalOCRResValue
        self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=globalOCRArgValue_Temp, cardSlot=0x1, sendCmd8=True, initInfo=None,
                            rca=0x0, time = 0x0, sendCMD0 = 0x1, bHighCapacity=True, bSendCMD58=False,
                            version=0x0, VOLA=0x1, cmdPattern=0xAA, reserved=0x0, expOCRVal=globalOCRResValue_Temp)

        #SwitchVolt_CMD11
        self.__dvtLib.SwitchVolt_CMD11()

        #Identification
        self.__dvtLib.Identification()

        # Select card
        self.__dvtLib.SelectCard()

        # Set BusWidth = 4
        self.__dvtLib.SetBusWidth(busWidth=4)

        #Call Switch Command for check mode / Check,Expected Status Available
        mode = gvar.CMD6.CHECK
        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
        blockSize = 0x40
        CMD6 =self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,responseCompare=False)

        #Call Switch Command for check mode / Check,Expected Status Available
        mode = gvar.CMD6.CHECK
        arglist = [0x0,0xF,0xF,0xF,0xF,0xF]
        blockSize = 0x40
        supported = self.compare(CMD6)
        swicthed = [0x0,0x0,0x0,0x0,0x0,0x0]
        responseCompare = True #compare true
        consumption = gvar.CMD6.CONSUMPTION_NONE
        CMD6=self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                             responseCompare=responseCompare,
                                             compareConsumption=consumption,
                                             compareSupported=supported,
                                             comparedSwitched=swicthed)

        #Call Switch Command for switch mode / Check,Expected Status Available
        mode = gvar.CMD6.SWITCH
        arglist = [0x0,0xF,0xF,0xF,0xF,0xF]
        blockSize = 0x40
        supported = self.compare(CMD6)
        swicthed = [0x0,0x0,0x0,0x0,0x0,0x0]
        responseCompare = True #compare true
        consumption = gvar.CMD6.CONSUMPTION_NONE
        CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist, blocksize=blockSize,
                                               responseCompare=responseCompare,
                                               compareConsumption=consumption,
                                               compareSupported=supported,
                                               comparedSwitched=swicthed)

        #Set Frequency to 25000 KHz
        self.__sdCmdObj.SetFrequency(25000) #Passed in KHz

        #Call Switch Command for check mode / Check,Expected Status Available
        mode = gvar.CMD6.CHECK
        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
        blockSize = 0x40
        supported = self.compare(CMD6)
        swicthed = [0x0,0x0,0x0,0x0,0x0,0x0]
        responseCompare = True #compare true
        consumption = gvar.CMD6.CONSUMPTION_NONE
        CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize=blockSize,
                                               responseCompare=responseCompare,
                                               compareConsumption=consumption,
                                               compareSupported=supported,
                                               comparedSwitched=swicthed)

        # Variable Declaration
        LocalVariables = {}
        LocalVariables['UHS_MODE'] = 'SDR12'

        # Set Volt
        sdVolt = sdcmdWrap.SVoltage()
        sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
        sdVolt.voltage = 3300 # 3.30 V
        sdVolt.maxCurrent =100 #For VDDH
        sdVolt.maxVoltage = 3300
        sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 62.5 Hz
        statusReg = 0
        self.__dvtLib.setVolt(sdVolt, statusReg, gvar.PowerSupply.VDDH)

        LocalVariables['Turn_HS_ON'] = 0
        LocalVariables['VS_FLAG'] = globalprojectConfig["VS_Flag"]

        if (CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup1 & 0x10) != 0:
            LocalVariables['RANDOM_MODES'] = 5  # support UHS-104
        else:
            LocalVariables['RANDOM_MODES'] = 4

        LocalVariables['UHS'] = 1
        LocalVariables['RANDOM_UHS_MODE'] = 2
        LocalVariables['SendACMD6'] = 1
        LocalVariables['SEND_CMD11'] = 1
        LocalVariables['SendOCR'] = globalprojectConfig['globalOCRArgValue']
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SendOCR: %d" % LocalVariables['SendOCR'])
        LocalVariables['ExpectOCR'] = globalprojectConfig['globalOCRResValue']
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ExcpectOCR: %d" % LocalVariables['ExpectOCR'])
        LocalVariables['SendFirstOCR'] = globalprojectConfig['globalOCRArgValue']
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SendFirstOCR: %d" % LocalVariables['SendFirstOCR'])
        LocalVariables['SendNextOCR'] = globalprojectConfig['globalOCRArgValue']
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SendNextOCR: %d" % LocalVariables['SendNextOCR'])
        LocalVariables['SingleCommand'] = 0
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SingleCommand: %d" % LocalVariables['SingleCommand'])
        # SingleCommandTestType: 1 = ReverseXpcS18r, 2 = ReverseXPC, 3 = ReverseS18R, 4 = ReverseHCS, 5 = RandomXpcS18r
        LocalVariables['SingleCommandTestType'] = 1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SingleCommandTestType: %d" % LocalVariables['SingleCommandTestType'])
        LocalVariables['Identification'] = 1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification: %d" % LocalVariables['Identification'])
        # ProtocolMode: 1 = SD OK, 2 = SD Error, 3 = SPI OK, 4 = SPI Error
        LocalVariables['ProtocolMode'] = 1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ProtocolMode: %d" % LocalVariables['ProtocolMode'])
        # VerifyType:   1 = Utility_Successful_Verify.st3, 2 = Utility_Failure_Verify.st3, 3 = Utility_Successful_Verify_MaxVoltage.st3
        LocalVariables['VerifyType'] = 0
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VerifyType: %d" % LocalVariables['VerifyType'])
        LocalVariables['SendCMD0'] = 1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SendCMD0: %d" % LocalVariables['SendCMD0'])
        LocalVariables['SendCMD8'] = 1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SendCMD8: %d" % LocalVariables['SendCMD8'])
        LocalVariables['SendCMD58'] = 1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SendCMD58: %d" % LocalVariables['SendCMD58'])
        LocalVariables['SetPower'] = 1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SetPower: %d" % LocalVariables['SetPower'])

        LocalVariables['HcsXpcS18r000'] = (((globalprojectConfig['globalOCRArgValue'] & 0xBFFFFFFF) & 0xEFFFFFFF) & 0xFEFFFFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HcsXpcS18r000: %d" % LocalVariables['HcsXpcS18r000'])
        LocalVariables['HcsXpcS18r001'] = (((globalprojectConfig['globalOCRArgValue'] & 0xBFFFFFFF) & 0xEFFFFFFF) | 0x1000000)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HcsXpcS18r001: %d" % LocalVariables['HcsXpcS18r001'])
        LocalVariables['HcsXpcS18r010'] = (((globalprojectConfig['globalOCRArgValue'] & 0xBFFFFFFF) | 0x10000000) & 0xFEFFFFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HcsXpcS18r010: %d" % LocalVariables['HcsXpcS18r010'])
        LocalVariables['HcsXpcS18r011'] = (((globalprojectConfig['globalOCRArgValue'] & 0xBFFFFFFF) | 0x10000000) | 0x1000000)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HcsXpcS18r011: %d" % LocalVariables['HcsXpcS18r011'])
        LocalVariables['HcsXpcS18r100'] = (((globalprojectConfig['globalOCRArgValue'] | 0x40000000) & 0xEFFFFFFF) & 0xFEFFFFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HcsXpcS18r100: %d" % LocalVariables['HcsXpcS18r100'])
        LocalVariables['HcsXpcS18r101'] = (((globalprojectConfig['globalOCRArgValue'] | 0x40000000) & 0xEFFFFFFF) | 0x1000000)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HcsXpcS18r101: %d" % LocalVariables['HcsXpcS18r101'])
        LocalVariables['HcsXpcS18r110'] = (((globalprojectConfig['globalOCRArgValue'] | 0x40000000) | 0x10000000) & 0xFEFFFFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HcsXpcS18r110: %d" % LocalVariables['HcsXpcS18r110'])
        LocalVariables['HcsXpcS18r111'] = (((globalprojectConfig['globalOCRArgValue'] | 0x40000000) | 0x10000000) | 0x1000000)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HcsXpcS18r111: %d" % LocalVariables['HcsXpcS18r111'])
        LocalVariables['ReadyCcs18a000'] = (((globalprojectConfig['globalOCRResValue'] & 0x7FFFFFFF) & 0xBFFFFFFF) & 0xFEFFFFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ReadyCcs18a000: %d" % LocalVariables['ReadyCcs18a000'])
        LocalVariables['ReadyCcs18a001'] = (((globalprojectConfig['globalOCRResValue'] & 0x7FFFFFFF) & 0xBFFFFFFF) | 0x1000000)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ReadyCcs18a001: %d" % LocalVariables['ReadyCcs18a001'])
        LocalVariables['ReadyCcs18a010'] = (((globalprojectConfig['globalOCRResValue'] & 0x7FFFFFFF) | 0x40000000) & 0xFEFFFFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ReadyCcs18a010: %d" % LocalVariables['ReadyCcs18a010'])
        LocalVariables['ReadyCcs18a011'] = (((globalprojectConfig['globalOCRResValue'] & 0x7FFFFFFF) | 0x40000000) | 0x1000000)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ReadyCcs18a011: %d" % LocalVariables['ReadyCcs18a011'])
        LocalVariables['ReadyCcs18a100'] = (((globalprojectConfig['globalOCRResValue'] | 0x80000000) & 0xBFFFFFFF) & 0xFEFFFFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ReadyCcs18a100: %d" % LocalVariables['ReadyCcs18a100'])
        LocalVariables['ReadyCcs18a101'] = (((globalprojectConfig['globalOCRResValue'] | 0x80000000) & 0xBFFFFFFF) | 0x1000000)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ReadyCcs18a101: %d" % LocalVariables['ReadyCcs18a101'])
        LocalVariables['ReadyCcs18a110'] = (((globalprojectConfig['globalOCRResValue'] | 0x80000000) | 0x40000000) & 0xFEFFFFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ReadyCcs18a110: %d" % LocalVariables['ReadyCcs18a110'])
        LocalVariables['ReadyCcs18a111'] = (((globalprojectConfig['globalOCRResValue'] | 0x80000000) | 0x40000000) | 0x1000000)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ReadyCcs18a111: %d" % LocalVariables['ReadyCcs18a111'])

        LocalVariables['RANDOM_S18R'] = random.randint(0, 3)
        LocalVariables['S18R'] = LocalVariables['HcsXpcS18r100']
        LocalVariables['UNLOCK_TYPE'] = 0
        LocalVariables['POWER_CYCLE'] = 1
        LocalVariables['LOCKED'] = 0
        LocalVariables['UHS_DRIVE'] =0x0
        LocalVariables['UHS_CURRENT'] =0x0
        LocalVariables['SWITCH_CONSUMPTION'] =100
        LocalVariables['CHECK_CONSUMPTION'] =100
        LocalVariables['TRANSFER_RATE']=0x32
        LocalVariables['MAX_CURRENT']=100

        #==========================GET CARD CAPACITY=====================================#######
        # GET CARD CAPACITY
        U = float(self.__cardMaxLba)
        CARD_CAPACITY = float(0)
        APPROX_CARD_CAP = float(old_div(old_div(U,1000000)*512,1000))
        if ((APPROX_CARD_CAP > 0.8) and (APPROX_CARD_CAP < 1.2)):
            CARD_CAPACITY = float(1)
        if ((APPROX_CARD_CAP > 1.8) and (APPROX_CARD_CAP < 2.2)):
            CARD_CAPACITY = float(2)
        if ((APPROX_CARD_CAP > 3.6) and (APPROX_CARD_CAP < 4.4)):
            CARD_CAPACITY = float(4)
        if ((APPROX_CARD_CAP > 7) and (APPROX_CARD_CAP < 9)):
            CARD_CAPACITY = float(8)
        if ((APPROX_CARD_CAP > 14) and (APPROX_CARD_CAP < 18)):
            CARD_CAPACITY = float(16)
        if ((APPROX_CARD_CAP > 28) and (APPROX_CARD_CAP < 36)):
            CARD_CAPACITY = float(32)
        if ((APPROX_CARD_CAP > 56) and (APPROX_CARD_CAP < 72)):
            CARD_CAPACITY = float(64)
        if (APPROX_CARD_CAP > 72):
            CARD_CAPACITY = float(128)

        if (APPROX_CARD_CAP == float(0)):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Test Failed - Failed to calculate the Card Capacity.")
            raise ValidationError.TestFailError(self.fn, "Test Failed - Failed to calculate the Card Capacity.")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Capacity is : %f GB" % CARD_CAPACITY)
        LocalVariables['CARD_CAPACITY'] = CARD_CAPACITY

        if ((CARD_CAPACITY >= 64) and (LocalVariables['SendOCR'] == LocalVariables['HcsXpcS18r111'])):
            # Set Volt
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 150 #For VDDH
            sdVolt.maxVoltage = 3300
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 62.5 Hz
            statusReg = 0
            self.__dvtLib.setVolt(sdVolt, statusReg, gvar.PowerSupply.VDDH)

        LocalVariables["listData"] = supported
        return LocalVariables

    # Testcase Utility Logic - Ends
# Testcase Utility Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_UHS_SD3_UT01_LoadLocal_Variables(self):
        obj = UHS_SD3_UT01_LoadLocal_Variables(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
