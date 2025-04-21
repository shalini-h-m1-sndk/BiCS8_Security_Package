"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : ABORT_TC001_10K_PowerLossTest.st3
# SCRIPTER SCRIPT                : ABORT_UT08_10KPL_ReadVerifyDynamicAreas.st3
# CVF CALL ALL SCRIPT            : ABORT_TC001_10K_PowerLossTest.py
# CVF SCRIPT                     : ABORT_UT08_10KPL_ReadVerifyDynamicAreas.py
# DESCRIPTION                    : The purpose of this utility script is to perform Read and Verify data on card.
                                   Note: This script has a depenency on JIRA##5914 CTISW-5914 [Information required about API VERIFY RELIABLE WRITE ]
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 27/06/2022
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


class ABORT_UT08_10KPL_ReadVerifyDynamicAreas(customize_log):
    """
    class for Defining Write operation that can be used by
    Main scripts
    """
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
        # self.__ErrorManager = self.vtfContainer.device_session.GetErrorManager()

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

        ###### Customize Log ######
        self.fn = os.path.basename(getframeinfo(currentframe()).filename)
        customize_log.__init__(self, self.__TF)

        ##### Testcase Specific Variables #####


    def Run(self, ABORT_global_vars):
        # Verify Area1 data
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#### Verify Area1 data ####")

        if ABORT_global_vars['Area1OldDataStartAddress'] != -1: # If there is an "Old" data section
            StartLBA =  ABORT_global_vars['Area1OldDataStartAddress']
            EndLBA = ABORT_global_vars['Area1OldDataEndAddress']
            BlockCount = self.__sdCmdObj.calculate_blockcount(StartLBA, EndLBA)
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = ABORT_global_vars['Area1OldDataType'])

        if (ABORT_global_vars['testArea1VerMode'] != 4) and (ABORT_global_vars['currentAreaID'] == 1):  # If aborted ("Old/New" section) section should be verified
            StartLBA =  ABORT_global_vars['Area1OldNewDataStartAddress']
            EndLBA = ABORT_global_vars['Area1OldNewDataEndAddress']
            BlockCount = self.__sdCmdObj.calculate_blockcount(StartLBA, EndLBA)
            self.__sdCmdObj.VerifyReliableWrite(StartLBA, BlockCount, Pattern = ABORT_global_vars['Area1NewDataType'])

        if ABORT_global_vars['Area1NewDataStartAddress'] != -1: # If there is a "New" data section
            StartLBA =  ABORT_global_vars['Area1NewDataStartAddress']
            EndLBA = ABORT_global_vars['Area1NewDataEndAddress']
            BlockCount = self.__sdCmdObj.calculate_blockcount(StartLBA, EndLBA)
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = ABORT_global_vars['Area1NewDataType'])

        # Verify Area2 data
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#### Verify Area2 data ####")

        if ABORT_global_vars['Area2OldDataStartAddress'] != -1: # If there is an "Old" data section
            StartLBA =  ABORT_global_vars['Area2OldDataStartAddress']
            EndLBA = ABORT_global_vars['Area2OldDataEndAddress']
            BlockCount = self.__sdCmdObj.calculate_blockcount(StartLBA, EndLBA)
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = ABORT_global_vars['Area2OldDataType'])

        if (ABORT_global_vars['testArea2VerMode'] != 4) and (ABORT_global_vars['currentAreaID'] == 2):  # If aborted ("Old/New" section) section should be verified
            StartLBA =  ABORT_global_vars['Area2OldNewDataStartAddress']
            EndLBA = ABORT_global_vars['Area2OldNewDataEndAddress']
            BlockCount = self.__sdCmdObj.calculate_blockcount(StartLBA, EndLBA)
            self.__sdCmdObj.VerifyReliableWrite(StartLBA, BlockCount, Pattern = ABORT_global_vars['Area2NewDataType'])

        if ABORT_global_vars['Area2NewDataStartAddress'] !=  -1:    # If there is a "New" data section
            StartLBA =  ABORT_global_vars['Area2NewDataStartAddress']
            EndLBA = ABORT_global_vars['Area2NewDataEndAddress']
            BlockCount = self.__sdCmdObj.calculate_blockcount(StartLBA, EndLBA)
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = ABORT_global_vars['Area2NewDataType'])

        return 0

# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_ABORT_UT08_10KPL_ReadVerifyDynamicAreas(self):
        obj = ABORT_UT08_10KPL_ReadVerifyDynamicAreas(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
