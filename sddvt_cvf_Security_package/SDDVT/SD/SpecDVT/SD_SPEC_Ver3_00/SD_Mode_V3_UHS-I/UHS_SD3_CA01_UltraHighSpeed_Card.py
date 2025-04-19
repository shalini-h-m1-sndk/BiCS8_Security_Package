"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : UHS_SD3_CA01_UltraHighSpeed_Card.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : UHS_SD3_CA01_UltraHighSpeed_Card.py
# DESCRIPTION                    : Module to implement CallAll_UHS-I for the Specified Modules
# PRERQUISTE                     : All the required testcases
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=UHS_SD3_CA01_UltraHighSpeed_Card --isModel=false --enable_console_log=1 --adapter=0
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
import random
import os
import sys
import time
from inspect import currentframe, getframeinfo

# Global Variables


# Testcase Class - Begins
class UHS_SD3_CA01_UltraHighSpeed_Card(customize_log):
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
        self.__scripts = ["SD3UHS104_DVT_SD3_00_3_4_1_1_3_SDSC_NOT__SUPPORTED","UHS_SD3_TC002_CMD8_Mandatory",
                          "UHS_SD3_TC003_CMD11_State_Test","UHS_SD3_TC004_CMD19_State_Test",
                          "UHS_SD3_TC005_Init_Error_Test","SD3UHS109_DVT_SD3_00_UHS_LOCK_UNLOCK_TEST",
                          "UHS_SD3_TC006_UHSModes_Random_Test_Overcurrent","UHS_SD3_TC007_Reset_RandomTest"]


    # Testcase logic - Starts
    def Run(self):

        # Initialize the SD card
        self.__sdCmdObj.DoBasicInit()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call script globalInitCard STARTED")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call script globalInitCard COMPLETED")

        self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Started Running \\SD\\SpecDVT\\SD_SPEC_Ver3_00\\UHS-1 Scripts\n")

        ScriptsStatus = 0
        for scripts in self.__scripts:

            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#" * 40)
            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Started Running script %s "%scripts)
            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#" * 40)

            try:#For Script runtime failure

                try: #for Import Error
                    scriptsToRun = __import__(scripts,globals(),locals(),None)
                except ValidationError.CVFExceptionTypes as exc:
                    exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                    self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed to Import script %s with error %s "%(scripts,exc))
                    self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#" * 40)
                    ScriptsStatus +=1
                    continue

                #start running the script after import
                testProcedureObj     = scriptsToRun.TestProcedure(self.vtfContainer)
                testProcedureObj.RunTestProcedure()

                self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#" * 40)
                self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Finished Running script %s "%scripts)
                self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#" * 40)

            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed Running script %s with error %s "%(scriptsToRun,exc))
                self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#" * 40)
                ScriptsStatus +=1

        if ScriptsStatus > 0: #For reporting any failure in script running
            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#" * 40)
            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "The Script %s has %d error on running "%(self.__class__,ScriptsStatus))
            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#" * 40)
            raise ValidationError.TestFailError(self.fn, "The Script %s has %d error on running "%(self.__class__,ScriptsStatus))

        self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Running SD.SpecDVT.SD_SPEC_Ver3_00.UHS-1 Scripts\n")

        return 0
    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_UHS_SD3_CA01_UltraHighSpeed_Card(self):
        obj = UHS_SD3_CA01_UltraHighSpeed_Card(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
