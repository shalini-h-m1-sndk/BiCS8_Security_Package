"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : CMD20_CA01_SDMode.st3
# SCRIPTER SCRIPT                : CMD20_UT06_Sequence.st3
# CVF CALL ALL SCRIPT            : CMD20_CA01_SDMode.py
# CVF SCRIPT                     : CMD20_UT06_Sequence.py
# DESCRIPTION                    : The purpose of this test is: CMD20 commands execution in sequence
# PRERQUISTE                     : CMD20_UT02_GetSequence.py, CMD20_UT03_Write.py
# STANDALONE EXECUTION           : No. It is an utility script.
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : Nov-2022
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
import CMD20_UT01_LoadCMD20_Variables as LoadCMD20_Variables
import CMD20_UT02_GetSequence as CMD20GetSequence
import CMD20_UT03_Write as CMD20Write

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
class CMD20_UT06_Sequence(customize_log):
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
        self.__getSequence = CMD20GetSequence.CMD20_UT02_GetSequence(self.vtfContainer)
        self.__cmd20Write = CMD20Write.CMD20_UT03_Write(self.vtfContainer)

    # Testcase Utility Logic - Starts
    def Run(self, cmd20variables = None, ret = 0):
        """
        Name : Run
        """
        if not ret:
            # If running as Individual script Card initialization required
            self.__sdCmdObj.DoBasicInit()

        if cmd20variables == None:
            # Call Script LoadCmd20Variables Utility Script
            cmd20variables = LoadCMD20_Variables.CMD20_UT01_LoadCMD20_Variables(self.vtfContainer).Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Execution of CMD20 Commands in sequence\n")

        # Speed Class Create DIR
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

        # Use the utility CMD20_UT03_Write for performing
        # Write and Read of type 1
        WriteType = 1
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = cmd20variables)

        # Start Recording
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING, TimeOut = 1000)

        #  Use getsequence script for expected sequence type 2
        cmd20variables["ExpectSequence"] = 1
        self.__getSequence.Run(cmd20variables["ExpectSequence"])

        # Use the utility CMD20_UT03_Write for performing
        # Write and Read of type 2
        WriteType  = 2
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = cmd20variables)

        # Update CI
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)

        # Use the utility CMD20_UT03_Write for performing
        # Write and Read of type 3
        WriteType = 3
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = cmd20variables)

        # Use the utility CMD20_UT03_Write for performing
        # Write and Read of type 4
        WriteType = 4
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = cmd20variables)

        # Use the utility CMD20_UT03_Write for performing
        # Write and Read of type 5
        WriteType = 5
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = cmd20variables)

        # Use the utility CMD20_UT03_Write for performing
        # Write and Read of type 6
        WriteType = 6
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = cmd20variables)

        # Use the utility CMD20_UT03_Write for performing
        # Write and Read of type 2
        WriteType = 2
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = cmd20variables)

        return 0
    # Testcase Utility Logic - Ends
# Testcase Utility Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_CMD20_UT06_Sequence(self):
        obj = CMD20_UT06_Sequence(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
