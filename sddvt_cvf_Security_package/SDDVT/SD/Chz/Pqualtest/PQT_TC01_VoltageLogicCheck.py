"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : PQT_TC01_VoltageLogicCheck.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : PQT_TC01_VoltageLogicCheck.py
# DESCRIPTION                    : For issuing Power Cycle.
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=PQT_TC01_VoltageLogicCheck --isModel=false --enable_console_log=1 --adapter=0
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
class PQT_TC01_VoltageLogicCheck(customize_log):
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
        This Script enforce some logic to voltage that were asigned to Test
        V1, V2 , V3, V4 three voltages that suggested  are checked against  max votage value &   min value
        """

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Execution started\n")

        if globalParameters == None:
            raise ValidationError.TestFailError(self.fn, "GlobalParameters value in None")

        if (int(globalParameters["max_voltage"]) < globalParameters["Voltage_1"]) + (int(globalParameters["min_voltage"]) > globalParameters["Voltage_1"]) :
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Voltage_1 out of range %d "%globalParameters["Voltage_1"])
            raise ValidationError.TestFailError(self.fn, "Voltage_1 out of range %d "%globalParameters["Voltage_1"])

        if (int(globalParameters["max_voltage"]) < globalParameters["Voltage_2"])+ (int(globalParameters["min_voltage"]) > globalParameters["Voltage_2"] ):
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Voltage_2 out of range %d "%globalParameters["Voltage_2"])
            raise ValidationError.TestFailError(self.fn, "Voltage_2 out of range %d "%globalParameters["Voltage_2"])

        if (int(globalParameters["max_voltage"]) < globalParameters["Voltage_3"])+ (int(globalParameters["min_voltage"]) > globalParameters["Voltage_3"]):
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Voltage_3 out of range %d "%globalParameters["Voltage_3"])
            raise ValidationError.TestFailError(self.fn, "Voltage_3 out of range %d "%globalParameters["Voltage_3"])

        if (int(globalParameters["max_voltage"]) < globalParameters["Voltage_4"] ) + (int(globalParameters["min_voltage"]) > globalParameters["Voltage_4"]):
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Voltage_4 out of range %d "%globalParameters["Voltage_4"])
            raise ValidationError.TestFailError(self.fn, "Voltage_4 out of range %d "%globalParameters["Voltage_4"])

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Voltage range accepted\n")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Execution completed\n")

        return 0
    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_PQT_TC01_VoltageLogicCheck(self):
        obj = PQT_TC01_VoltageLogicCheck(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
