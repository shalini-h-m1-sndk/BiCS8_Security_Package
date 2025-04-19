"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : HCSPI_V2_UT004_AddressForWriteRead.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : HCSPI_V2_UT004_AddressForWriteRead.py
# DESCRIPTION                    : Module to Write, Read in SPI mode
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
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


# Testcase Utility Class - Begins
class HCSPI_V2_UT004_AddressForWriteRead(customize_log):
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


    # Testcase utility logic - Starts
    def Run(self):
        """
        Name : Run
        Description : This test is Write , Read in SPI mode.
        This script is dependent script, It will not execute as individual script since no initialization is included.
        """

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TEST SCRIPT IS STARTED.")

        # Get CSD and verify SD card
        CSD_Values = self.__sdCmdObj.GET_CSD_VALUES()

        # Card Info - Serial number, MaxLba , Card capacity, card secure mode information
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***************CARD INFO************")
        self.__dvtLib.CardInfo()

        # Variable declarations,
        cap = self.__cardMaxLba
        capTmp = cap - 0x1000 - 0x5
        StartAddress = random.randrange(0x0, capTmp) + 0x1
        globalFlashType = self.__config.get('globalFlashType')

        # Perform Write/Read operation based on the value of 'globalFlashType'
        if (globalFlashType == 'ROM') : # In case of ROM cards, Pre Loaded Incremental Type of Data in SD ROM Cards
            # Multiple read
            self.__dvtLib.ReadWithFPGAPattern(StartAddress, blockCount = 0x1000, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)
        else:   # In case of Card is not in ROM mode, Hermon3 SD SPEC 2.0 High & Low Capacity cards type (Hermon3, Tripoli, Combo)

            # Multiple write
            self.__dvtLib.WriteWithFPGAPattern(StartAddress, blockCount = 0x1000, pattern = gvar.GlobalConstants.PATTERN_CONST)

            # Multiple read
            self.__dvtLib.ReadWithFPGAPattern(StartAddress, blockCount = 0x1000, pattern = gvar.GlobalConstants.PATTERN_CONST)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TEST SCRIPT IS COMPLETED.")

        return 0

    # Testcase utility logic - Ends
# Testcase Utility Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_HCSPI_V2_UT004_AddressForWriteRead(self):
        obj = HCSPI_V2_UT004_AddressForWriteRead(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
