"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : ABORT_TC001_10K_PowerLossTest.st3
# SCRIPTER SCRIPT                : ABORT_UT03_10KPL_GetChunkSizeAndAlgorithm.st3
# CVF CALL ALL SCRIPT            : ABORT_TC001_10K_PowerLossTest.py
# CVF SCRIPT                     : ABORT_UT03_10KPL_GetChunkSizeAndAlgorithm.py
# DESCRIPTION                    : The purpose of this utility script is to
                                - Add all the test cases of the test (algorithm and size) attributes
                                - Algorithms (example - sequential, swap, ...)
                                - Sizes (example - 512bytes, 4KBytes, ...)
                                - Define the number of test cases to be tested.
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


class ABORT_UT03_10KPL_GetChunkSizeAndAlgorithm(customize_log):
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


    def Run(self, ret = 0):
        #Empty Dictionary
        TC_Size =  {}
        TC_Algorithm = {}

        # Variable Declaration
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Initialize the variables")

        TC_Size['TC0_Size'] = 1
        TC_Algorithm['TC0_Algorithm'] = 0

        TC_Size['TC1_Size'] = 8
        TC_Algorithm['TC1_Algorithm'] = 0

        TC_Size['TC2_Size'] = 128
        TC_Algorithm['TC2_Algorithm'] = 0

        TC_Size['TC3_Size'] = 512
        TC_Algorithm['TC3_Algorithm'] = 0

        TC_Size['TC4_Size'] = 1
        TC_Algorithm['TC4_Algorithm'] = 1

        TC_Size['TC5_Size'] = 128
        TC_Algorithm['TC5_Algorithm'] = 1

        TC_Size['TC6_Size'] = 8
        TC_Algorithm['TC6_Algorithm'] = 2

        numofTCs = 7
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Total Number of Testcases: %d" % numofTCs)

        if ret:
            return TC_Size, TC_Algorithm, numofTCs
        for key, value in TC_Size:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TestCase List:")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s : %d" % (key, value))

        for key, value in TC_Algorithm:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TestCase Algorithm Value:")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s : %d" % (key, value))

        return 0

# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_ABORT_UT03_10KPL_GetChunkSizeAndAlgorithm(self):
        obj = ABORT_UT03_10KPL_GetChunkSizeAndAlgorithm(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
