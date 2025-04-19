"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : HCSD_V2_CA01_CallAllReset1_UHS.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : HCSD_V2_CA01_CallAllReset1_UHS.py
# DESCRIPTION                    : Module to run all the scripts of SD_Mode_V2_UHS_I
# PRERQUISTE                     : All the sub scripts
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=HCSD_V2_CA01_CallAllReset1_UHS --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 30-May-2024
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
import HCSD_V2_TC001_1_1_1_1 as HCSD_V2_TC001_1_1_1_1
import HCSD_V2_TC002_1_1_1_2 as HCSD_V2_TC002_1_1_1_2
import HCSD_V2_TC003_1_1_1_2a as HCSD_V2_TC003_1_1_1_2a
import HCSD_V2_TC004_1_1_1_3 as HCSD_V2_TC004_1_1_1_3
import HCSD_V2_TC005_1_1_1_4 as HCSD_V2_TC005_1_1_1_4
import HCSD_V2_TC006_1_1_1_5 as HCSD_V2_TC006_1_1_1_5
import HCSD_V2_TC007_1_1_1_8 as HCSD_V2_TC007_1_1_1_8
import HCSD_V2_TC008_1_1_1_10 as HCSD_V2_TC008_1_1_1_10
import HCSD_V2_TC009_1_1_1_12 as HCSD_V2_TC009_1_1_1_12
import HCSD_V2_TC010_1_1_1_14 as HCSD_V2_TC010_1_1_1_14
import HCSD_V2_TC011_1_1_1_14a as HCSD_V2_TC011_1_1_1_14a
import HCSD_V2_TC012_1_1_1_17 as HCSD_V2_TC012_1_1_1_17
import HCSD_V2_TC013_1_1_1_18 as HCSD_V2_TC013_1_1_1_18
import HCSD_V2_TC014_1_1_1_20a as HCSD_V2_TC014_1_1_1_20a
import HCSD_V2_TC015_1_1_1_20b as HCSD_V2_TC015_1_1_1_20b
import HCSD_V2_TC016_1_1_1_20c as HCSD_V2_TC016_1_1_1_20c
import HCSD_V2_TC017_OCRValuesInHighCapacityCardOverHighCapacityHost as OCRValuesInHighCapacityCardOverHighCapacityHost
import HCSD_V2_TC018_OCRvaluesInPowerCycleHV as OCRvaluesInPowerCycleHV
import HCSD_V2_TC019_OCRvaluesInPowerCycleWithCMD0HV as OCRvaluesInPowerCycleWithCMD0HV
import HCSD_V2_TC020_ResetHighCapacityCardWithDefultValuesInCMD8 as ResetHighCapacityCardWithDefultValuesInCMD8


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
class HCSD_V2_CA01_CallAllReset1_UHS(customize_log):
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
        self.__OCRValuesInHighCapacityCardOverHighCapacityHost = OCRValuesInHighCapacityCardOverHighCapacityHost.HCSD_V2_TC017_OCRValuesInHighCapacityCardOverHighCapacityHost(self.vtfContainer)
        self.__OCRvaluesInPowerCycleHV = OCRvaluesInPowerCycleHV.HCSD_V2_TC018_OCRvaluesInPowerCycleHV(self.vtfContainer)
        self.__OCRvaluesInPowerCycleWithCMD0HV = OCRvaluesInPowerCycleWithCMD0HV.HCSD_V2_TC019_OCRvaluesInPowerCycleWithCMD0HV(self.vtfContainer)
        self.__ResetHighCapacityCardWithDefultValuesInCMD8 = ResetHighCapacityCardWithDefultValuesInCMD8.HCSD_V2_TC020_ResetHighCapacityCardWithDefultValuesInCMD8(self.vtfContainer)
        self.__HCSD_V2_TC001_1_1_1_1 = HCSD_V2_TC001_1_1_1_1.HCSD_V2_TC001_1_1_1_1(self.vtfContainer)
        self.__HCSD_V2_TC002_1_1_1_2 = HCSD_V2_TC002_1_1_1_2.HCSD_V2_TC002_1_1_1_2(self.vtfContainer)
        self.__HCSD_V2_TC003_1_1_1_2a = HCSD_V2_TC003_1_1_1_2a.HCSD_V2_TC003_1_1_1_2a(self.vtfContainer)
        self.__HCSD_V2_TC004_1_1_1_3 = HCSD_V2_TC004_1_1_1_3.HCSD_V2_TC004_1_1_1_3(self.vtfContainer)
        self.__HCSD_V2_TC005_1_1_1_4 = HCSD_V2_TC005_1_1_1_4.HCSD_V2_TC005_1_1_1_4(self.vtfContainer)
        self.__HCSD_V2_TC006_1_1_1_5 = HCSD_V2_TC006_1_1_1_5.HCSD_V2_TC006_1_1_1_5(self.vtfContainer)
        self.__HCSD_V2_TC007_1_1_1_8 = HCSD_V2_TC007_1_1_1_8.HCSD_V2_TC007_1_1_1_8(self.vtfContainer)
        self.__HCSD_V2_TC008_1_1_1_10 = HCSD_V2_TC008_1_1_1_10.HCSD_V2_TC008_1_1_1_10(self.vtfContainer)
        self.__HCSD_V2_TC009_1_1_1_12 = HCSD_V2_TC009_1_1_1_12.HCSD_V2_TC009_1_1_1_12(self.vtfContainer)
        self.__HCSD_V2_TC010_1_1_1_14 = HCSD_V2_TC010_1_1_1_14.HCSD_V2_TC010_1_1_1_14(self.vtfContainer)
        self.__HCSD_V2_TC011_1_1_1_14a = HCSD_V2_TC011_1_1_1_14a.HCSD_V2_TC011_1_1_1_14a(self.vtfContainer)
        self.__HCSD_V2_TC012_1_1_1_17 = HCSD_V2_TC012_1_1_1_17.HCSD_V2_TC012_1_1_1_17(self.vtfContainer)
        self.__HCSD_V2_TC013_1_1_1_18 = HCSD_V2_TC013_1_1_1_18.HCSD_V2_TC013_1_1_1_18(self.vtfContainer)
        self.__HCSD_V2_TC014_1_1_1_20a = HCSD_V2_TC014_1_1_1_20a.HCSD_V2_TC014_1_1_1_20a(self.vtfContainer)
        self.__HCSD_V2_TC015_1_1_1_20b = HCSD_V2_TC015_1_1_1_20b.HCSD_V2_TC015_1_1_1_20b(self.vtfContainer)
        self.__HCSD_V2_TC016_1_1_1_20c = HCSD_V2_TC016_1_1_1_20c.HCSD_V2_TC016_1_1_1_20c(self.vtfContainer)


    # Testcase logic - Starts
    def Run(self):
        """
        Name : Run
        """

        #call all scripts
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##########CALL : HCSD_V2_TC017_OCRValuesInHighCapacityCardOverHighCapacityHost ##########")
        self.__OCRValuesInHighCapacityCardOverHighCapacityHost.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##########CALL : HCSD_V2_TC018_OCRvaluesInPowerCycleHV  ##########")
        self.__OCRvaluesInPowerCycleHV.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##########CALL : HCSD_V2_TC019_OCRvaluesInPowerCycleWithCMD0HV ##########")
        self.__OCRvaluesInPowerCycleWithCMD0HV.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##########CALL : HCSD_V2_TC020_ResetHighCapacityCardWithDefultValuesInCMD8 ##########")
        self.__ResetHighCapacityCardWithDefultValuesInCMD8.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##########CALL : HCSD_V2_TC001_1_1_1_1 ##########")
        self.__HCSD_V2_TC001_1_1_1_1.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##########CALL : HCSD_V2_TC002_1_1_1_2  ##########")
        self.__HCSD_V2_TC002_1_1_1_2.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##########CALL : HCSD_V2_TC003_1_1_1_2a ##########")
        self.__HCSD_V2_TC003_1_1_1_2a.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##########CALL : HCSD_V2_TC004_1_1_1_3 ##########")
        self.__HCSD_V2_TC004_1_1_1_3.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##########CALL : HCSD_V2_TC005_1_1_1_4 ##########")
        self.__HCSD_V2_TC005_1_1_1_4.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##########CALL : HCSD_V2_TC006_1_1_1_5 ##########")
        self.__HCSD_V2_TC006_1_1_1_5.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##########CALL : HCSD_V2_TC007_1_1_1_8 ##########")
        self.__HCSD_V2_TC007_1_1_1_8.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##########CALL : HCSD_V2_TC008_1_1_1_10 ##########")
        self.__HCSD_V2_TC008_1_1_1_10.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##########CALL : HCSD_V2_TC009_1_1_1_12 ##########")
        self.__HCSD_V2_TC009_1_1_1_12.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##########CALL : HCSD_V2_TC010_1_1_1_14 ##########")
        self.__HCSD_V2_TC010_1_1_1_14.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##########CALL : HCSD_V2_TC011_1_1_1_14a ##########")
        self.__HCSD_V2_TC011_1_1_1_14a.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##########CALL : HCSD_V2_TC012_1_1_1_17 ##########")
        self.__HCSD_V2_TC012_1_1_1_17.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##########CALL : HCSD_V2_TC013_1_1_1_18 ##########")
        self.__HCSD_V2_TC013_1_1_1_18.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##########CALL : HCSD_V2_TC014_1_1_1_20a ##########")
        self.__HCSD_V2_TC014_1_1_1_20a.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##########CALL : HCSD_V2_TC015_1_1_1_20b ##########")
        self.__HCSD_V2_TC015_1_1_1_20b.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##########CALL : HCSD_V2_TC016_1_1_1_20c ##########")
        self.__HCSD_V2_TC016_1_1_1_20c.Run()

        return 0
    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_HCSD_V2_CA01_CallAllReset1_UHS(self):
        obj = HCSD_V2_CA01_CallAllReset1_UHS(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
