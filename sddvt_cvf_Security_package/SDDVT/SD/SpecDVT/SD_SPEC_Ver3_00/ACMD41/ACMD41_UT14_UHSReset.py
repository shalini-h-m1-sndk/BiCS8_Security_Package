"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : ACMD41_UT14_UHSReset.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : ACMD41_UT14_UHSReset.py
# DESCRIPTION                    : The purpose of this test is to do reset UHS
# PRERQUISTE                     : ACMD41_UT07_Load_LocalVariables.py
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
import ACMD41_UT07_Load_LocalVariables as LoadLocalVariables

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


# Testcase Utility Class - Begins
class ACMD41_UT14_UHSReset(customize_log):
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
        self.__LoadLocal_Variables = LoadLocalVariables.ACMD41_UT07_Load_LocalVariables(self.vtfContainer)


    # Testcase Utility Logic - Starts
    def Run(self, globalProjectConfVar = None ,localVariables = None, SetPower = 1):
        """
        Name : Run
        """

        if localVariables == None:
            localVariables = self.__LoadLocal_Variables.Run(ret=1)

        U = self.__sdCmdObj.MaxLba()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "GET CARD CAPACITY ")

        # Step 1: Variable declaration
        UHS = 1
        SendACMD6 = 1
        SEND_CMD11 = 1
        CARD_CAPACITY = 0
        APPROX_CARD_CAP = old_div(old_div(U,1000000)*512,1000)

        # Nested if condition to select card capacity based on APPROX_CARD_CAP value
        if (APPROX_CARD_CAP > 0.8) and (APPROX_CARD_CAP < 1.2):
            CARD_CAPACITY = 1

        if (APPROX_CARD_CAP > 1.8) and (APPROX_CARD_CAP < 2.2):
            CARD_CAPACITY = 2

        if (APPROX_CARD_CAP > 3.6) and (APPROX_CARD_CAP < 4.4):
            CARD_CAPACITY = 4

        if (APPROX_CARD_CAP > 7) and (APPROX_CARD_CAP < 9):
            CARD_CAPACITY = 8

        if (APPROX_CARD_CAP > 14) and (APPROX_CARD_CAP < 18):
            CARD_CAPACITY = 16

        if (APPROX_CARD_CAP > 28) and (APPROX_CARD_CAP < 36):
            CARD_CAPACITY = 32

        if (APPROX_CARD_CAP > 56) and (APPROX_CARD_CAP < 72):
            CARD_CAPACITY = 64

        if APPROX_CARD_CAP >  72 and (APPROX_CARD_CAP < 130):
            CARD_CAPACITY = 128

        if (APPROX_CARD_CAP > 130) and (APPROX_CARD_CAP < 265):
            CARD_CAPACITY = 256

        if (APPROX_CARD_CAP > 265) and (APPROX_CARD_CAP < 410):
            CARD_CAPACITY = 400

        if (APPROX_CARD_CAP > 410) and (APPROX_CARD_CAP < 520):
            CARD_CAPACITY = 512

        if (APPROX_CARD_CAP > 520) and (APPROX_CARD_CAP < 1050):
            CARD_CAPACITY = 1024

        if APPROX_CARD_CAP == 0:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed to calculate the card capacity")
            raise ValidationError.TestFailError(self.fn, "Failed to calculate the card capacity")

        # Checking condition SetPower = 1
        if SetPower == 1:
            # CMD11(True, 0, 5) # Switch to 1.8v, Time to clock off = 5mSec
            self.__dvtLib.SwitchVolt_CMD11()

        # Card identification
        self.__dvtLib.Identification()

        # Select Card
        self.__sdCmdObj.Cmd7()

        # Set bus width = 4
        self.__dvtLib.SetBusWidth(busWidth = 0x4)

        # Switch card mode
        mode = gvar.CMD6.CHECK #for check
        blocksize = 0x40
        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
        supported = [0x0,0x0,0x0,0x0,0x0,0x0]
        switched = [0x0,0x0,0x0,0x0,0x0,0x0]
        responseCompare = True #compare False
        consumption = gvar.CMD6.CONSUMPTION_NONE
        CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist, blocksize = blocksize,
                                               responseCompare=responseCompare,
                                               compareConsumption=consumption,
                                               compare=[0, 0, 0, 0, 0, 0],
                                               compareSupported=supported,
                                               comparedSwitched=switched)

        FUNC1 = CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup1
        FUNC2 = CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup2
        FUNC3 = CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup3
        FUNC4 = CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup4
        FUNC5 = CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup5
        FUNC6 = CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup6

        if FUNC1 > 0x8017:
            RANDOM_MODES = 5
        else:
            RANDOM_MODES = 4
        RANDOM_BLOCK = random.randrange(0, RANDOM_MODES)

        # VS_Flag = globalProjectConfVar["VS_Flag"]
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VS_Flag========================%s"%(str(VS_Flag)))
        # FUNC2 = (FUNC2 & (0xBFFF | (0x4000 * VS_Flag )))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "supported========================%s"%(str(supported)))

        if RANDOM_BLOCK == 0:
            # Switch card command
            mode = gvar.CMD6.CHECK
            blocksize = 0x40
            arglist = [0x0,0xF,0xF,0xF,0xF,0xF]
            supported = [FUNC1,FUNC2,FUNC3,FUNC4,FUNC5,FUNC6]
            switched = [0x0,0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE
            compareValue = 100
            CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist, blocksize = blocksize,
                                                   responseCompare=responseCompare,
                                                   compareConsumption=consumption, compareValue=compareValue,
                                                   compareSupported=supported,
                                                   comparedSwitched=switched)

            mode = gvar.CMD6.SWITCH #for switch
            blocksize = 0x40
            arglist = [0x0,0xF,0xF,0xF,0xF,0xF]
            supported = [FUNC1,FUNC2,FUNC3,FUNC4,FUNC5,FUNC6]
            switched = [0x0,0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE
            compareValue= 100
            CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist, blocksize = blocksize,
                                                           responseCompare=responseCompare,
                                                           compareConsumption=consumption, compareValue=compareValue,
                                                           compareSupported=supported,
                                                           comparedSwitched=switched)


            # Set Frequency to 25000, Passed in KHz
            self.__sdCmdObj.SetFrequency(25000)

            # Switch card command, mode = gvar.CMD6.CHECK
            mode = gvar.CMD6.CHECK #for check
            blocksize = 0x40
            arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
            supported = [FUNC1,FUNC2,FUNC3,FUNC4,FUNC5,FUNC6]
            switched = [0x0,0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE
            compareValue= 100
            CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist, blocksize = blocksize,
                                                   responseCompare=responseCompare,
                                                   compareConsumption=consumption, compareValue=compareValue,
                                                   compareSupported=supported,
                                                   comparedSwitched=switched)
            UHS_MODE = 'SDR12'


            # Set voltage = 3.3V, Max current = 100mA, A2D Rate : 62.5 Hz
            sdvoltage = sdcmdWrap.SVoltage()
            sdvoltage.voltage = 3300
            sdvoltage.maxCurrent = 100
            sdvoltage.maxVoltage = 3300
            sdvoltage.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ
            sdvoltage.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8

            self.__dvtLib.setVolt(sdVolt=sdvoltage,statusReg=0,powerSupp=gvar.PowerSupply.VDDH)

            if (CARD_CAPACITY >= 64) and (localVariables["SendOCR"] == localVariables['HcsXpcS18r111']):

                #  Set voltage = 3.3V, Max current = 150mA, A2D Rate : 62.5 Hz
                sdvoltage.maxCurrent = 150
                self.__dvtLib.setVolt(sdVolt=sdvoltage,statusReg=0,powerSupp=gvar.PowerSupply.VDDH)

        # Condition checking for RANDOM_BLOCK = 1
        if RANDOM_BLOCK == 1:

            # Switch card command, mode = gvar.CMD6.CHECK
            mode = gvar.CMD6.CHECK #for check
            blocksize = 0x40
            arglist = [0x1,0xF,0xF,0xF,0xF,0xF]
            supported = [FUNC1,FUNC2,FUNC3,FUNC4,FUNC5,FUNC6]
            switched = [0x1,0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE
            compareValue= 200
            CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist, blocksize = blocksize,
                                                   responseCompare=responseCompare,
                                                   compareConsumption=consumption, compareValue=compareValue,
                                                   compareSupported=supported,
                                                   comparedSwitched=switched)

            # Switch card command, mode = gvar.CMD6.SWITCH
            mode = gvar.CMD6.SWITCH #for Switch
            blocksize = 0x40
            arglist = [0x1,0xF,0xF,0xF,0xF,0xF]
            supported = [FUNC1,FUNC2,FUNC3,FUNC4,FUNC5,FUNC6]
            switched = [0x1,0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE
            compareValue= 200
            CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist, blocksize = blocksize,
                                                   responseCompare=responseCompare,
                                                   compareConsumption=consumption, compareValue=compareValue,
                                                   compareSupported=supported,
                                                   comparedSwitched=switched)


            # Set Frequency to 50000, Passed in KHz
            self.__sdCmdObj.SetFrequency(50000)

            # Switch card command, mode = gvar.CMD6.CHECK
            mode = gvar.CMD6.CHECK #for check
            blocksize = 0x40
            arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
            supported = [FUNC1,FUNC2,FUNC3,FUNC4,FUNC5,FUNC6]
            switched = [0x1,0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE
            compareValue= 200
            CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist, blocksize = blocksize,
                                                   responseCompare=responseCompare,
                                                   compareConsumption=consumption, compareValue=compareValue,
                                                   compareSupported=supported,
                                                   comparedSwitched=switched)
            UHS_MODE = 'SDR25'

            # Set voltage = 3.3V, Max current = 200mA, A2D Rate : 62.5 Hz
            sdvoltage = sdcmdWrap.SVoltage()
            sdvoltage.voltage = 3300
            sdvoltage.maxCurrent = 200
            sdvoltage.maxVoltage = 3300
            sdvoltage.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ
            sdvoltage.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8

            self.__dvtLib.setVolt(sdVolt=sdvoltage,statusReg=0,powerSupp=gvar.PowerSupply.VDDH) #changed to VDDH

        #  Condition checking for RANDOM_BLOCK = 2
        if RANDOM_BLOCK == 2:

            # Switch card command, mode = gvar.CMD6.CHECK
            mode = gvar.CMD6.CHECK #for check
            blocksize = 0x40
            arglist = [0x2,0xF,0xF,0xF,0xF,0xF]
            supported = [FUNC1,FUNC2,FUNC3,FUNC4,FUNC5,FUNC6]
            switched = [0x2,0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE
            compareValue = 250
            CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist, blocksize = blocksize,
                                                   responseCompare=responseCompare,
                                                   compareConsumption=consumption, compareValue=compareValue,
                                                   compareSupported=supported,
                                                   comparedSwitched=switched)

            # Switch card command, mode = gvar.CMD6.SWITCH
            mode = gvar.CMD6.SWITCH #for Switch
            blocksize = 0x40
            arglist = [0x2,0xF,0xF,0xF,0xF,0xF]
            supported = [FUNC1,FUNC2,FUNC3,FUNC4,FUNC5,FUNC6]
            switched = [0x2,0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE
            compareValue= 200
            CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist, blocksize = blocksize,
                                                   responseCompare=responseCompare,
                                                   compareConsumption=consumption, compareValue=compareValue,
                                                   compareSupported=supported,
                                                   comparedSwitched=switched)

            # Set Frequency to 100000, Passed in KHz
            self.__sdCmdObj.SetFrequency(100000)

            # Get Freq 0
            self.__sdCmdObj.GetFrequency()

            # Switch card command, mode = gvar.CMD6.CHECK
            mode = gvar.CMD6.CHECK #for Check
            blocksize = 0x40
            arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
            supported = [FUNC1,FUNC2,FUNC3,FUNC4,FUNC5,FUNC6]
            switched = [0x2,0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE
            compareValue = 250
            CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist, blocksize = blocksize,
                                                   responseCompare=responseCompare,
                                                   compareConsumption=consumption, compareValue=compareValue,
                                                   compareSupported=supported,
                                                   comparedSwitched=switched)

            # Send tuning pattern
            numOfCmd = random.randrange(0, 40) + 1
            timeOut = 150
            bufferError = ServiceWrap.Buffer.CreateBuffer(1,0)
            self.__dvtLib.SEND_TUNING_PATTERN(numOfCmd, timeOut, bufferError)

            UHS_MODE = 'SDR50'

            # Set voltage = 3.3V, Max current = 400mA, A2D Rate : 62.5 Hz
            sdvoltage = sdcmdWrap.SVoltage()
            sdvoltage.voltage = 3300
            sdvoltage.maxCurrent = 400
            sdvoltage.maxVoltage = 3300
            sdvoltage.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ
            sdvoltage.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8

            self.__dvtLib.setVolt(sdVolt = sdvoltage, statusReg = 0, powerSupp = gvar.PowerSupply.VDDH)

        #  Condition checking for RANDOM_BLOCK = 3
        if RANDOM_BLOCK == 3:

            # Switch card command, mode = gvar.CMD6.CHECK
            mode = gvar.CMD6.CHECK #for Check
            blocksize = 0x40
            arglist = [0x4,0xF,0xF,0xF,0xF,0xF]
            supported = [FUNC1,FUNC2,FUNC3,FUNC4,FUNC5,FUNC6]
            switched = [0x4,0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE
            compareValue= 250
            CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist, blocksize = blocksize,
                                                   responseCompare=responseCompare,
                                                   compareConsumption=consumption, compareValue=compareValue,
                                                   compareSupported=supported,
                                                   comparedSwitched=switched)

            # Switch card command, mode = gvar.CMD6.SWITCH
            mode = gvar.CMD6.SWITCH #for Switch
            blocksize = 0x40
            arglist = [0x4,0xF,0xF,0xF,0xF,0xF]
            supported = [FUNC1,FUNC2,FUNC3,FUNC4,FUNC5,FUNC6]
            switched = [0x4,0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE
            compareValue= 200
            CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist, blocksize = blocksize,
                                                   responseCompare=responseCompare,
                                                   compareConsumption=consumption, compareValue=compareValue,
                                                   compareSupported=supported,
                                                   comparedSwitched=switched)

            # Set Frequency to 50000, Passed in KHz
            self.__sdCmdObj.SetFrequency(50000)

            # Switch card command, mode = gvar.CMD6.CHECK
            mode = gvar.CMD6.CHECK #for Check
            blocksize = 0x40
            arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
            supported = [FUNC1,FUNC2,FUNC3,FUNC4,FUNC5,FUNC6]
            switched = [0x4,0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE
            compareValue= 250
            CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist, blocksize = blocksize,
                                                   responseCompare=responseCompare,
                                                   compareConsumption=consumption, compareValue=compareValue,
                                                   compareSupported=supported,
                                                   comparedSwitched=switched)

            UHS_MODE = 'DDR50'

            # Set voltage = 3.3V, Max current = 400mA, A2D Rate : 62.5 Hz
            sdvoltage = sdcmdWrap.SVoltage()
            sdvoltage.voltage = 3300
            sdvoltage.maxCurrent = 400
            sdvoltage.maxVoltage = 3300
            sdvoltage.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ
            sdvoltage.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8

            self.__dvtLib.setVolt(sdVolt=sdvoltage,statusReg=0,powerSupp=gvar.PowerSupply.VDDH)


        # Condition checking for RANDOM_BLOCK = 4
        if RANDOM_BLOCK == 4:

            # Switch card command, mode = gvar.CMD6.CHECK
            mode = gvar.CMD6.CHECK #for Check
            blocksize = 0x40
            arglist = [0x3,0xF,0xF,0xF,0xF,0xF]
            supported = [FUNC1,FUNC2,FUNC3,FUNC4,FUNC5,FUNC6]
            switched = [0x3,0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE
            compareValue= 250
            CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist, blocksize = blocksize,
                                                   responseCompare=responseCompare,
                                                   compareConsumption=consumption, compareValue=compareValue,
                                                   compareSupported=supported,
                                                   comparedSwitched=switched)

            # Switch card command, mode = gvar.CMD6.SWITCH
            mode = gvar.CMD6.SWITCH #for Switch
            blocksize = 0x40
            arglist = [0x3,0xF,0xF,0xF,0xF,0xF]
            supported = [FUNC1,FUNC2,FUNC3,FUNC4,FUNC5,FUNC6]
            switched = [0x3,0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE
            compareValue= 200
            CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist, blocksize = blocksize,
                                                   responseCompare=responseCompare,
                                                   compareConsumption=consumption, compareValue=compareValue,
                                                   compareSupported=supported,
                                                   comparedSwitched=switched)

            # Set Frequency to 200000, Passed in KHz
            self.__sdCmdObj.SetFrequency(200000)

            # Get Freq 0
            self.__sdCmdObj.GetFrequency()

            # Switch card command, mode = gvar.CMD6.CHECK
            mode = gvar.CMD6.CHECK #for Check
            blocksize = 0x40
            arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
            supported = [FUNC1,FUNC2,FUNC3,FUNC4,FUNC5,FUNC6]
            switched = [0x3,0x0,0x0,0x0,0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE
            compareValue= 250
            CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist, blocksize = blocksize,
                                                   responseCompare=responseCompare,
                                                   compareConsumption=consumption, compareValue=compareValue,
                                                   compareSupported=supported,
                                                   comparedSwitched=switched)

            # Send tuning pattern
            numOfCmd = random.randrange(0, 40) + 1
            timeOut = 150
            bufferError = ServiceWrap.Buffer.CreateBuffer(1, 0x0)
            self.__dvtLib.SEND_TUNING_PATTERN(numOfCmd, timeOut, bufferError)

            UHS_MODE = 'SDR104'

            # Set voltage = 3.3V, Max current = 400mA, A2D Rate : 62.5 Hz
            sdvoltage = sdcmdWrap.SVoltage()
            sdvoltage.voltage = 3300
            sdvoltage.maxCurrent = 400
            sdvoltage.maxVoltage = 3300
            sdvoltage.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ
            sdvoltage.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8

            self.__dvtLib.setVolt(sdVolt=sdvoltage,statusReg=0,powerSupp=gvar.PowerSupply.VDDH) #

        # GET CSD
        self.__sdCmdObj.GET_CSD_VALUES()
        self.__sdCmdObj.Cmd7() # to get the card in trans state

        # GET SD STATUS
        self.__dvtLib.GetSDStatus()

        return 0
    # Testcase Utility Logic - Ends
# Testcase Utility Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_ACMD41_UT14_UHSReset(self):
        obj = ACMD41_UT14_UHSReset(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
