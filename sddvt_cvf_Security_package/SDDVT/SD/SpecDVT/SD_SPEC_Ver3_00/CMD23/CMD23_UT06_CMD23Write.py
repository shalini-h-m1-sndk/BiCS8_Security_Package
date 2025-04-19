"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                :
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : CMD23_UT06_CMD23Write.py
# DESCRIPTION                    :
# PRERQUISTE                     :
# STANDALONE EXECUTION           : No. It is an utility script.
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sushmitha P.S
# REVIEWED BY                    : Sivagurunathan
# DATE                           : 29-May-2024
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
from inspect import currentframe, getframeinfo

# Global Variables

# Testcase Utility Class - Begins

class CMD23_UT06_CMD23Write(customize_log):
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

    # Testcase Utility Logic - Starts

    def Run(self, CMD23StartBlock, CMD23BlockCount, PredefinedNumOfBlkCnt, CMD23DataType, usePreDefBlkCount = False):

        """
        Name : Run
            # STEP 1 : Define the No.of Blocks to be written
            # STEP 2 : Do Multiple Write from CMD23StartBlock to CMD23BlockCount
            # STEP 3 : Verify block count with ACMD-22
            # STEP 4 : Do Multiple Read from CMD23StartBlock to CMD23BlockCount
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Utility Execution Started " + "-" * 20 + "\n")
        # Define the No.of Blocks to be written
        if CMD23BlockCount > PredefinedNumOfBlkCnt:
            CMD23BlockCount = PredefinedNumOfBlkCnt

        #  Do Multiple Write from CMD23StartBlock to CMD23BlockCount
        BlockCount = CMD23BlockCount
        StartLBA = CMD23StartBlock

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Perform Multiple Write Operation")
        self.__dvtLib.WriteWithFPGAPattern(StartLba =StartLBA, blockCount = BlockCount, pattern=CMD23DataType ,usePreDefBlkCount = usePreDefBlkCount)

        # Verify block count with ACMD-22
        ACMD22 = self.__sdCmdObj.ACmd22()
        BlockCount = ACMD22.numberOfWrittenBlocks
        if (BlockCount != CMD23BlockCount) :
            raise ValidationError.TestFailError(self.fn, "Num. of blocks Written: {} doesn't match with CMD23BlockCount: {}".format(BlockCount, CMD23BlockCount))

        # Do Multiple Read from CMD23StartBlock to CMD23BlockCount
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Perform Multiple Read Operation")
        self.__dvtLib.ReadWithFPGAPattern(StartLba =StartLBA, blockCount = BlockCount, pattern= CMD23DataType, usePreDefBlkCount = usePreDefBlkCount)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Utility Execution Completed " + "-" * 20 + "\n")
        return CMD23BlockCount

    #End of Run function
#End of CMD23Write


    # Testcase Utility Logic - Ends

# Testcase Utility Class - Ends