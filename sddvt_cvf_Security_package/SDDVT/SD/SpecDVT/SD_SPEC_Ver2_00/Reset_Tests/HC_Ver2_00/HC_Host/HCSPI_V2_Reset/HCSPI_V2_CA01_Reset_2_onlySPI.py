"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : HCSPI_V2_CA01_Reset_2_onlySPI.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : HCSPI_V2_CA01_Reset_2_onlySPI.py
# DESCRIPTION                    : Module to call specified scripts in SPI mode
# PRERQUISTE                     : All the SPI sub scripts
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=HCSPI_V2_CA01_Reset_2_onlySPI --isModel=false --enable_console_log=1 --adapter=0
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
import importlib
import random
import os
import sys
import time
from inspect import currentframe, getframeinfo

# Global Variables


# Testcase Class - Begins
class HCSPI_V2_CA01_Reset_2_onlySPI(customize_log):
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
        self.__scripts = ["HCSPI_V2_UT002_SPIResetUtility", "HCSPI_V2_TC097_OCRvaluesInPowerCycleWithCMD0DV_A",
                          "HCSPI_V2_TC098_OCRvaluesInPowerCycleWithCMD0DV_B", "HCSPI_V2_TC099_OCRvaluesWithCMD0DV_A",
                          "HCSPI_V2_TC100_OCRvaluesWithCMD0DV_B", "HCSPI_V2_TC001_1_1_2_1a",
                          "HCSPI_V2_TC002_1_1_2_1b", "HCSPI_V2_TC003_1_1_2_1c", "HCSPI_V2_TC004_1_1_2_1d",
                          "HCSPI_V2_TC005_1_1_2_2_1a", "HCSPI_V2_TC006_1_1_2_2_1b", "HCSPI_V2_TC007_1_1_2_2_1c",
                          "HCSPI_V2_TC008_1_1_2_2_1d", "HCSPI_V2_TC009_1_1_2_2_2a", "HCSPI_V2_TC010_1_1_2_2_2b",
                          "HCSPI_V2_TC011_1_1_2_2_2c", "HCSPI_V2_TC012_1_1_2_2_2d", "HCSPI_V2_TC013_1_1_2_2_3a",
                          "HCSPI_V2_TC014_1_1_2_2_3b", "HCSPI_V2_TC015_1_1_2_2_3c", "HCSPI_V2_TC016_1_1_2_2_3d",
                          "HCSPI_V2_TC017_1_1_2_2_4a", "HCSPI_V2_TC018_1_1_2_2_4b", "HCSPI_V2_TC019_1_1_2_2_4c",
                          "HCSPI_V2_TC020_1_1_2_2_4d", "HCSPI_V2_TC021_1_1_2_3a", "HCSPI_V2_TC022_1_1_2_3b",
                          "HCSPI_V2_TC023_1_1_2_4a", "HCSPI_V2_TC024_1_1_2_4b", "HCSPI_V2_TC025_1_1_2_4c",
                          "HCSPI_V2_TC026_1_1_2_4d", "HCSPI_V2_TC027_1_1_2_5a", "HCSPI_V2_TC028_1_1_2_5b",
                          "HCSPI_V2_TC029_1_1_2_5c", "HCSPI_V2_TC030_1_1_2_5d", "HCSPI_V2_TC031_1_1_2_6a",
                          "HCSPI_V2_TC032_1_1_2_6b", "HCSPI_V2_TC033_1_1_2_6c", "HCSPI_V2_TC034_1_1_2_6d",
                          "HCSPI_V2_TC035_1_1_2_7_1a", "HCSPI_V2_TC036_1_1_2_7_1b", "HCSPI_V2_TC037_1_1_2_7_1c",
                          "HCSPI_V2_TC038_1_1_2_7_1d", "HCSPI_V2_TC039_1_1_2_7_2a", "HCSPI_V2_TC040_1_1_2_7_2b",
                          "HCSPI_V2_TC041_1_1_2_7_2c", "HCSPI_V2_TC042_1_1_2_7_2d", "HCSPI_V2_TC043_1_1_2_10_1a",
                          "HCSPI_V2_TC044_1_1_2_10_1b", "HCSPI_V2_TC045_1_1_2_10_1c", "HCSPI_V2_TC046_1_1_2_10_1d",
                          "HCSPI_V2_TC047_1_1_2_10_2a", "HCSPI_V2_TC048_1_1_2_10_2b", "HCSPI_V2_TC049_1_1_2_10_2c",
                          "HCSPI_V2_TC050_1_1_2_10_2d", "HCSPI_V2_TC051_1_1_2_10_3a", "HCSPI_V2_TC052_1_1_2_10_3b",
                          "HCSPI_V2_TC053_1_1_2_10_3c", "HCSPI_V2_TC054_1_1_2_10_3d", "HCSPI_V2_TC055_1_1_2_11a",
                          "HCSPI_V2_TC056_1_1_2_11b", "HCSPI_V2_TC057_1_1_2_11c", "HCSPI_V2_TC058_1_1_2_11d",
                          "HCSPI_V2_TC059_1_1_2_12a", "HCSPI_V2_TC060_1_1_2_12b", "HCSPI_V2_TC061_1_1_2_12c",
                          "HCSPI_V2_TC062_1_1_2_12d", "HCSPI_V2_TC063_1_1_2_13a", "HCSPI_V2_TC064_1_1_2_13b",
                          "HCSPI_V2_TC065_1_1_2_13c", "HCSPI_V2_TC066_1_1_2_13d", "HCSPI_V2_TC067_1_1_2_14_1a",
                          "HCSPI_V2_TC068_1_1_2_14_1b", "HCSPI_V2_TC069_1_1_2_14_2a", "HCSPI_V2_TC070_1_1_2_14_2b",
                          "HCSPI_V2_TC071_1_1_2_14_2c", "HCSPI_V2_TC072_1_1_2_14_2d", "HCSPI_V2_TC073_1_1_2_15a",
                          "HCSPI_V2_TC074_1_1_2_15b", "HCSPI_V2_TC075_1_1_2_15c", "HCSPI_V2_TC076_1_1_2_15d",
                          "HCSPI_V2_TC077_1_1_2_16_1a", "HCSPI_V2_TC078_1_1_2_16_1b", "HCSPI_V2_TC079_1_1_2_16_1c",
                          "HCSPI_V2_TC080_1_1_2_16_1d", "HCSPI_V2_TC081_1_1_2_16_2a", "HCSPI_V2_TC082_1_1_2_16_2b",
                          "HCSPI_V2_TC083_1_1_2_16_2c", "HCSPI_V2_TC084_1_1_2_16_2d", "HCSPI_V2_TC085_1_1_2_16_3a",
                          "HCSPI_V2_TC086_1_1_2_16_3b", "HCSPI_V2_TC087_1_1_2_16_3c", "HCSPI_V2_TC088_1_1_2_16_3d",
                          "HCSPI_V2_TC089_1_1_2_17a", "HCSPI_V2_TC090_1_1_2_17b", "HCSPI_V2_TC091_1_1_2_17c",
                          "HCSPI_V2_TC092_1_1_2_17d", "HCSPI_V2_TC093_1_1_2_18a", "HCSPI_V2_TC094_1_1_2_18b",
                          "HCSPI_V2_TC095_1_1_2_18c", "HCSPI_V2_TC096_1_1_2_18d"
                          ]


    # Testcase logic - Starts
    def Run(self):
        """
        Name : Run
        Description : This script is to run specified scripts. These called scripts are used to Call All Script to run the imported scripts in SPI mode
        """

        # Initialize the SD card
        globalProjectConfVar = self.__sdCmdObj.DoBasicInit()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL ALL SCRIPT IS STARTED.")

        ScriptsStatus = {}
        for script in self.__scripts:

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s" % ("#" * 40))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Started running script %s " % script)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s\n" % ("#" * 40))

            try:
                try:
                    scriptToRun = importlib.import_module(script)
                except ValidationError.CVFGenericExceptions as exc: # To ignore the failure of one script for the execution of consecutive scripts
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed to import script %s. The error occurred is: %s" % (script, exc.GetInternalErrorMessage()))
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s\n" % ("#" * 40))
                    ScriptsStatus[script] = exc.GetInternalErrorMessage()
                    continue
                except ImportError as exc: # To ignore the failure of one script for the execution of consecutive scripts
                    if hasattr(exc, "message"):
                        importErrString = exc.message
                    elif hasattr(exc, "msg"):
                        importErrString = exc.msg
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed to import script %s. The error occurred is: %s" % (script, importErrString))
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s\n" % ("#" * 40))
                    ScriptsStatus[script] = importErrString
                    continue

                # Start running the script after import
                Creating_Obj = "ScriptObj = scriptToRun.%s(self.vtfContainer)" % script
                exec(Creating_Obj)
                if script == "HCSPI_V2_UT002_SPIResetUtility":
                    ScriptObj.Run() # ScriptObj is defined in the python build-in exec method.
                else:
                    ScriptObj.Run(globalProjectConfVar) # ScriptObj is defined in the python build-in exec method.

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s" % ("#" * 40))
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Finished Running script %s " % script)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s\n" % ("#" * 40))

            except ValidationError.CVFGenericExceptions as exc: # To ignore the failure of one script for the execution of consecutive scripts
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed running script %s. The error occurred is: %s " % (script, exc.GetInternalErrorMessage()))
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s\n" % ("#" * 40))
                ScriptsStatus[script] = exc.GetInternalErrorMessage()
                self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure

            except Exception as exc: # To ignore the failure of one script for the execution of consecutive scripts
                if hasattr(exc, "message"):
                    errstring = exc.message
                elif hasattr(exc, "msg"):
                    errstring = exc.msg
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed running script %s. The error occurred is: %s " % (script, errstring))
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s\n" % ("#" * 40))
                ScriptsStatus[script] = errstring

        number_of_script_failures = len(list(ScriptsStatus.keys()))
        if number_of_script_failures > 0:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s" % ("#" * 40))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call all script %s has %d script failures" % (self.__class__, number_of_script_failures))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s\n" % ("#" * 40))

            for script, error in list(ScriptsStatus.items()):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Script %s is failed with error: %s\n" % (script, error))
            raise ValidationError.TestFailError(self.fn, "Call all script is failed")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CALL ALL SCRIPT IS COMPLETED.")
        return 0
    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_HCSPI_V2_CA01_Reset_2_onlySPI(self):
        obj = HCSPI_V2_CA01_Reset_2_onlySPI(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
