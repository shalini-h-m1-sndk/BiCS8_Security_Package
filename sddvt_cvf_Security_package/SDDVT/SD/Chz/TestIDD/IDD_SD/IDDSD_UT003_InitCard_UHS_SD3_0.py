"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : IDDSD_UT003_InitCard_UHS_SD3_0.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : IDDSD_UT003_InitCard_UHS_SD3_0.py
# DESCRIPTION                    : For Card Intilization into UHS mode
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : No
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 30-May-2024
# UPDATED BY                     : Sushmitha P.S
# UPDATED DATE                   : 29-Aug-2024
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
class IDDSD_UT003_InitCard_UHS_SD3_0(customize_log):
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

    # Testcase logic - Starts
    def Run(self,globalParameters=None):

        """
        Intialize crad to UHS mode
        """

        #SDXC settings
        self.__sdCmdObj.Set_SDXC_SETTINGS(Set_XPC_bit = int(globalParameters["XPC_enable"]), Send_CMD11_in_the_next_card_init = int(globalParameters["SendCmd11_in_Init"]))

        #Settings to use pattern generator for read and writes

        sdcmdWrap.SetPower(0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power is OFF\n")

        self.__dvtLib.SwitchHostVoltageRegion() #Default switches to 3.3

        self.__sdCmdObj.SetFrequency(20000)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Frequency completed\n")

        self.__dvtLib.SetTimeOut(int(globalParameters["IDD_InitTimeout"]),int(globalParameters["IDD_WriteTimeout"]),int(globalParameters["IDD_ReadTimeout"]))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Timeout completed\n")

        sdcmdWrap.SetPower(1)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power is On\n")

        #SDXC settings
        self.__sdCmdObj.Set_SDXC_SETTINGS(Set_XPC_bit = int(globalParameters["XPC_enable"]), Send_CMD11_in_the_next_card_init = int(globalParameters["SendCmd11_in_Init"]))

        self.__sdCmdObj.INITCARD()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Init completed\n")

        #Set Bus Width
        if int(globalParameters["IDD_BusWidth"]) == 2:
            self.__dvtLib.SetBusWidth(busWidth=0x4)
        else:
            raise ValidationError.TestFailError(self.fn, "Illegal Bus width")

        #Switch Command
        responseBuff = self.__dvtLib.CardSwitchCommand(mode=gvar.CMD6.CHECK, arginlist=[0xF,0xF,0xF,0xF,0xF,0xF],
                                       blocksize=0x40,
                                       responseCompare=False,
                                       compareConsumption=None
                                       )

        responseSupportedG1 = responseBuff.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup1
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
        self.__dvtLib.CardSwitchCommand(mode=gvar.CMD6.CHECK, arginlist=[0xF,0xF,0xF,0xF,0xF,0xF],
                                       blocksize=0x40,
                                       responseCompare=True,
                                       compareConsumption=None,
                                       compare=[1,0,0,1,0,0],
                                       compareSupported=[responseSupportedG1,0x0,0x0,responseSupportedG4,0x0,0x0],
                                       comparedSwitched=[int(globalParameters["globalSpeedMode_Value"]),0x0,0x0,int(globalParameters["UHSCurrentLimit"]),0x0,0x0])

        #Set Frequency
        self.__sdCmdObj.SetFrequency(int(globalParameters["IDD_Frequency"]))
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
    def test_IDDSD_UT003_InitCard_UHS_SD3_0(self):
        obj = IDDSD_UT003_InitCard_UHS_SD3_0(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
