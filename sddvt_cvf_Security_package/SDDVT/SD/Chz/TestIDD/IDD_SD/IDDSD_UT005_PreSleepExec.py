"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : IDDSD_UT005_PreSleepExec.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : IDDSD_UT005_PreSleepExec.py
# DESCRIPTION                    : Presleep mode for default card intilization.
# PRERQUISTE                     : IDDSD_UT004_InitCard.py
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
import IDDSD_UT004_InitCard as IDD_InitCard

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
class IDDSD_UT005_PreSleepExec(customize_log):
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
        self.__IDD_InitCard = IDD_InitCard.IDDSD_UT004_InitCard(self.vtfContainer)


    # Testcase logic - Starts
    def Run(self,globalParameters=None):

        """
        For presleep mode in HS mode
        """

        IDD_PreSleepExe =  int(globalParameters["IDD_PreSleepExe"])

        if IDD_PreSleepExe == 0: #Reset
            self.__IDD_InitCard.Run(globalParameters)

        elif IDD_PreSleepExe == 1: #Reset and Read 1 Block
            self.__IDD_InitCard.Run(globalParameters)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SingleRead from Lba: 0x%X with blockcount: 0x%X "%(0,1))
            self.__dvtLib.ReadWithFPGAPattern(StartLba = 0x0, blockCount  = 0x1, pattern = gvar.GlobalConstants.PATTERN_ALL_ZERO, SingleRead = True)

        elif IDD_PreSleepExe == 2: #Reset and Read 2 Block
            self.__IDD_InitCard.Run(globalParameters)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "MultipleRead from Lba: 0x%X with blockcount: 0x%X "%(0,2))
            self.__dvtLib.ReadWithFPGAPattern(StartLba = 0x0, blockCount  = 0x2, pattern = gvar.GlobalConstants.PATTERN_ALL_ZERO)

        elif IDD_PreSleepExe == 3: #Reset and Write 1 Block
            self.__IDD_InitCard.Run(globalParameters)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SingleWrite from Lba: 0x%X with blockcount: 0x%X "%(0,1))
            self.__dvtLib.WriteWithFPGAPattern(StartLba = 0x0, blockCount  = 0x1, pattern = gvar.GlobalConstants.PATTERN_ALL_ZERO, SingleWrite = True)

        elif IDD_PreSleepExe == 4: #Reset and Write 2 Block
            self.__IDD_InitCard.Run(globalParameters)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "MultipleWrite from Lba: 0x%X with blockcount: 0x%X "%(0,2))
            self.__dvtLib.WriteWithFPGAPattern(StartLba = 0x0, blockCount  = 0x2, pattern = gvar.GlobalConstants.PATTERN_ALL_ZERO)
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "No Reset\n")

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
    def test_IDDSD_UT005_PreSleepExec(self):
        obj = IDDSD_UT005_PreSleepExec(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
