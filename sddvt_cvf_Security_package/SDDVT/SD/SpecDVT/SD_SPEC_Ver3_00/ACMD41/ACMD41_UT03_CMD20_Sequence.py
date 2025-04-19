"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : Utility_CMD20_Sequence
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : ACMD41_UT03_CMD20_Sequence.py
# DESCRIPTION                    :
# PRERQUISTE                     :
# STANDALONE EXECUTION           : No. It is an utility script.
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : Nov-2022
# UPDATED BY                     : Sushmitha P.S
# UPDATED DATE                   : 29-Jun-2024
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
import ACMD41_UT04_CMD20_Write as CMD20Write
import ACMD41_UT02_CMD20_GetSequence as CMD20GetSequence

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
class ACMD41_UT03_CMD20_Sequence(customize_log):
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
        self.__Cmd20Write = CMD20Write.ACMD41_UT04_CMD20_Write(self.vtfContainer)
        self.__GetSequence = CMD20GetSequence.ACMD41_UT02_CMD20_GetSequence(self.vtfContainer)

    # Testcase Utility Logic - Starts

    def Run(self,cmd20variables):
        """
        Name : Run
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Utility Execution Started " + "-" * 20 + "\n")
        # Speed Class Create DIR
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

        # Write and Read of type 1
        WriteType = 1
        self.__Cmd20Write.Run( WriteType = WriteType,cmd20variables=cmd20variables)

        #  Speed Class Start Recording
        self.__dvtLib.SpeedClassControl(SpeedClassControl=sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING,TimeOut=1000)
        # Use get sequence script for expected sequence type 2
        cmd20variables['ExpectSequence'] = 1
        self.__GetSequence.Run(cmd20variables['ExpectSequence'])

        # Write RU + Sequence
        WriteType = 2
        self.__Cmd20Write.Run( WriteType = WriteType,cmd20variables=cmd20variables)

        # Speed Class Update CI
        self.__dvtLib.SpeedClassControl(SpeedClassControl=sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut=10)

        # Write CI  + Sequence
        WriteType = 3
        self.__Cmd20Write.Run( WriteType = WriteType,cmd20variables=cmd20variables)

        # Write FAT(FAT) + Sequence
        WriteType = 4
        self.__Cmd20Write.Run( WriteType = WriteType,cmd20variables=cmd20variables)

        # Write FAT(DIR) + Sequence
        WriteType = 5
        self.__Cmd20Write.Run( WriteType = WriteType,cmd20variables=cmd20variables)

        # Write FAT(BITMAP) + Sequence
        WriteType = 6
        self.__Cmd20Write.Run( WriteType = WriteType,cmd20variables=cmd20variables)

        # Write RU + Sequence
        WriteType = 2
        self.__Cmd20Write.Run( WriteType = WriteType,cmd20variables=cmd20variables)

        return 0

    #End of Run function
#End of CMD20Sequence

# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_ACMD41_UT03_CMD20_Sequence(self):
        obj = ACMD41_UT03_CMD20_Sequence(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
