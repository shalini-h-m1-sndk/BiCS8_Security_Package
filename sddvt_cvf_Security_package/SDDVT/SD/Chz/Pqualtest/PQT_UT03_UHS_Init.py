"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : PQT_UT03_UHS_Init.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : PQT_UT03_UHS_Init.py
# DESCRIPTION                    : For Card Intilization into UHS mode.
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=PQT_UT03_UHS_Init --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 30-May-2024
# UPDATED BY                     : Shalini HM
# UPDATED DATE                   : 31-Jul-2024
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
import time
from inspect import currentframe, getframeinfo

# Global Variables


# Testcase Class - Begins
class PQT_UT03_UHS_Init(customize_log):
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
        #self.__sdVoltage           = sdcmdWrap.SVoltage()


    # Testcase logic - Starts
    def Run(self,globalParameters=None):
        """
        PQT_UT03_UHS_Init using pattern generator
        """

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Default Intilization started\n")

        sdcmdWrap.SetPower(0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power is OFF\n")

        #Set SD Voltage to 3.0V
        statusReg = 0
        sdVolt = sdcmdWrap.SVoltage()
        sdVolt.voltage = int(globalParameters["Volt"])
        sdVolt.maxCurrent = int(globalParameters["VDDH_Max_current"])
        sdVolt.maxVoltage= 3800
        sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ
        sdVolt.actualVoltage = 0
        self.__dvtLib.setVolt(sdVolt,statusReg,False) #Set VDDH
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VDDH Voltage set to host completed\n")


        if int(globalParameters["VDDF_enable"]) == 1:
            #Set SD Voltage to 3.0V
            statusReg = 0
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.voltage = int(globalParameters["Volt"])
            sdVolt.maxCurrent = int(globalParameters["VDDH_Max_current"])
            sdVolt.maxVoltage= 3800
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ
            sdVolt.actualVoltage = 0
            self.__dvtLib.setVolt(sdVolt,statusReg,True) #Set VDDF
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VDDF Voltage set to host completed\n")

        self.__sdCmdObj.SetFrequency(20000)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Frequency completed\n")

        self.__dvtLib.SetTimeOut(int(globalParameters["Init_TO"]),int(globalParameters["Write_TO"]),int(globalParameters["Read_TO"]))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Timeout completed\n")

        sdcmdWrap.SetPower(1)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power is On\n")

        #SDXC settings
        self.__sdCmdObj.Set_SDXC_SETTINGS(int(globalParameters['XPC_enable']),int(globalParameters["SendCmd11_in_Init"]))

        self.__dvtLib.initCard()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Init completed\n")

        #Get card Info
        self.__dvtLib.CardInfo()

        if (int(globalParameters["bus_width"]) == 0) or (int(globalParameters["bus_width"]) == 2) or (int(globalParameters["bus_width"]) == 3):
            self.__dvtLib.SetBusWidth(busWidth = 4)
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Illegal Bus width\n")
            raise ValidationError.TestFailError(self.fn, "Illegal Bus width\n")

        #Switch Command
        responseBuff = self.__dvtLib.CardSwitchCommand(mode=False, arginlist=[0xF,0xF,0xF,0xF,0xF,0xF],
                                            blocksize=0x40,
                                            responseCompare=False,
                                            compareConsumption=None)

        responseSupportedG1 = responseBuff.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup1
        responseSupportedG3 = responseBuff.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup3
        responseSupportedG4 = responseBuff.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup4

        #Set HighSpeed
        speedMode = int(globalParameters["globalSpeedMode_Value"])
        currentLimit = int(globalParameters["UHSCurrentLimit"])
        if speedMode == 0:
            speedModeToSet = sdcmdWrap.HIGH_SPEED_MODE.SWITCH_LOW_SPEED
        elif speedMode == 1:
            speedModeToSet = sdcmdWrap.HIGH_SPEED_MODE.SWITCH_HIGH_SPEED
        elif speedMode == 2:
            speedModeToSet = sdcmdWrap.HIGH_SPEED_MODE.SWITCH_SDR50
        elif speedMode == 3:
            speedModeToSet = sdcmdWrap.HIGH_SPEED_MODE.SWITCH_SDR104
        elif speedMode == 4:
            speedModeToSet = sdcmdWrap.HIGH_SPEED_MODE.SWITCH_DDR50
        else:
            raise ValidationError.TestFailError(self.fn, "globalSpeedMode_Value not accepted")

        if currentLimit == 0:
            currentLimitToSet = sdcmdWrap.SD_CURRENT_LIMIT.CURRENT_LIMIT_200mA
        elif currentLimit == 1:
            currentLimitToSet = sdcmdWrap.SD_CURRENT_LIMIT.CURRENT_LIMIT_400mA
        elif currentLimit == 2:
            currentLimitToSet = sdcmdWrap.SD_CURRENT_LIMIT.CURRENT_LIMIT_600mA
        elif currentLimit == 3:
            currentLimitToSet = sdcmdWrap.SD_CURRENT_LIMIT.CURRENT_LIMIT_800mA
        elif currentLimit == 4:
            currentLimitToSet = sdcmdWrap.SD_CURRENT_LIMIT.CURRENT_NO_INFLUENCE
        else:
            raise ValidationError.TestFailError(self.fn, "global UHSCurrentLimit value not accepted")

        self.__dvtLib.setHighSpeed(speedModeToSet,currentLimitToSet)

        #Switch Command
        self.__dvtLib.CardSwitchCommand(mode=False, arginlist=[0xF,0xF,0xF,0xF,0xF,0xF],
                                       blocksize=0x40,
                                       responseCompare=True,
                                       compareConsumption=None,
                                       compare=[0,0,0,0,0,0],
                                       compareSupported=[responseSupportedG1,0x0,responseSupportedG3,responseSupportedG4,0x0,0x0],
                                       comparedSwitched=[int(globalParameters["globalSpeedMode_Value"]),0x0,0x0,int(globalParameters["UHSCurrentLimit"]),0x0,0x0])


        #Set Frequency to 50 Mhz
        self.__sdCmdObj.SetFrequency(int(globalParameters["Freq"]))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Frequency completed\n")

        #Get CardInfo
        self.__dvtLib.CardInfo()

        #Get card speed mode
        self.__dvtLib.GetCardTransferMode()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Execution Completed\n")

        return 0
    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_PQT_UT03_UHS_Init(self):
        obj = PQT_UT03_UHS_Init(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
