"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : IDDSD_UT001_InitCardSimple.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : IDDSD_UT001_InitCardSimple.py
# DESCRIPTION                    : For default Intilization in High Speed.
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
class IDDSD_UT001_InitCardSimple(customize_log):
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
    def Run(self,globalParameters = None):

        """
        Does default card intilization
        """

        sdcmdWrap.SetPower(0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power is OFF\n")

        self.__sdCmdObj.SetFrequency(20000)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Frequency completed\n")

        #Set SD Voltage to 3.3V
        sdVoltage = sdcmdWrap.SVoltage()
        sdVoltage.voltage = 3300    # 3V
        sdVoltage.maxCurrent = 250
        sdVoltage.maxVoltage = 3800 # 3.8V
        sdVoltage.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ
        sdVoltage.actualVoltage = 0
        self.__dvtLib.setVolt(sdVoltage, statusReg = 0, powerSupp = gvar.PowerSupply.VDDH)  # False for host
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Voltage of host completed\n")

        sdcmdWrap.SetPower(1)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power is On\n")

        self.__dvtLib.SetTimeOut(int(globalParameters["IDD_InitTimeout"]),int(globalParameters["IDD_WriteTimeout"]),int(globalParameters["IDD_ReadTimeout"]))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Timeout completed\n")

        #Intilize card
        self.__dvtLib.initCard()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Init completed\n")

        if globalParameters["IDD_CardType"] == "SD":
            self.__sdCmdObj.GET_CSD_VALUES()

        if globalParameters["IDD_CardType"] == "MMC":
            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Get CSD for MMC\n")
            self.__sdCmdObj.GET_CSD_VALUES()

        self.__sdCmdObj.GET_CID_VALUES()

        if globalParameters["IDD_SpeedMode"] == "HS":
            self.__dvtLib.setHighSpeed(sdcmdWrap.HIGH_SPEED_MODE.SWITCH_HIGH_SPEED, sdcmdWrap.SD_CURRENT_LIMIT.CURRENT_NO_INFLUENCE)

        #Set Bus Width
        if int(globalParameters["IDD_BusWidth"]) == 2:
            self.__dvtLib.SetBusWidth(busWidth=0x4)
        if int(globalParameters["IDD_BusWidth"]) == 0:
            self.__dvtLib.SetBusWidth(busWidth=0x1)

        #Set Frequency to 20 Mhz
        self.__sdCmdObj.SetFrequency(Freq=25000)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Frequency completed\n")

        #Get card speed mode
        self.__dvtLib.GetCardTransferMode()

        #Get Card Info
        self.__dvtLib.CardInfo()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Execution Completed\n")

        return
    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_IDDSD_UT001_InitCardSimple(self):
        obj = IDDSD_UT001_InitCardSimple(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
