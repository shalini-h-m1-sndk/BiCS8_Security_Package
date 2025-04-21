"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : CMD20_CA01_SDMode.st3
# SCRIPTER SCRIPT                : CMD20_TC001_ReservedBitsTest.st3
# CVF CALL ALL SCRIPT            : CMD20_CA01_SDMode.py
# CVF SCRIPT                     : CMD20_TC001_ReservedBitsTest.py
# DESCRIPTION                    : The purpose of this test is to assure that CMD20 with reserved bits should not break the sequence
# PRERQUISTE                     : CMD20_UT01_LoadCMD20_Variables.py, CMD20_UT02_GetSequence.py, CMD20_UT03_Write.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=CMD20_TC001_ReservedBitsTest --isModel=false --enable_console_log=1 --adapter=0
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
    from builtins import range
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


# Testcase Class - Begins
class CMD20_TC001_ReservedBitsTest(customize_log):
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


    # Testcase logic - Starts
    def ReservedBitsTest(self, ReservedBit, cmd20variables):

        # Use reserved Bit
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl routine with Argument:%d\n" % ReservedBit)
        self.__dvtLib.SpeedClassControl(SpeedClassCommandDescription = ReservedBit)

        # Create DIR, Argument 0x1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl routine with Argument:0x1.\n")
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

        # Get CMD20GetSequence
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20GetSequence routine.\n")
        self.__getSequence.Run(self.__cmd20variables["ExpectSequence"])

        # Use reserved Bit
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl routine with Argument:%d\n" % ReservedBit)
        self.__dvtLib.SpeedClassControl(SpeedClassCommandDescription = ReservedBit)

        # Write DIR+Sequence
        WriteType = 1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write routine with WriteType:%d.\n" % WriteType)
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # Use Reserved Bit
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl routine with Argument:%d\n" % ReservedBit)
        self.__dvtLib.SpeedClassControl(SpeedClassCommandDescription = ReservedBit)

        # Start Recording
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl routine with Argument:0\n")
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING, TimeOut = 1000)

        # Get CMD20GetSequence
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20GetSequence routine.\n")
        self.__getSequence.Run(self.__cmd20variables["ExpectSequence"])

        # Use Reserved Bit
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl routine with Argument:%d\n" % ReservedBit)
        self.__dvtLib.SpeedClassControl(SpeedClassCommandDescription = ReservedBit)

        # Write RU+Sequence
        WriteType = 2
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write routine with WriteType:%d.\n" % WriteType)
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # Use Reserved Bit
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl routine with Argument:%d\n" % ReservedBit)
        self.__dvtLib.SpeedClassControl(SpeedClassCommandDescription = ReservedBit)

        # Update CI
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl routine with Argument:0x4\n")
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)

        # Write CI + Sequence
        WriteType = 3
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write routine with WriteType:%d.\n" % WriteType)
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # Use Reserved Bit
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl routine with Argument:%d\n" % ReservedBit)
        self.__dvtLib.SpeedClassControl(SpeedClassCommandDescription = ReservedBit)

        # Write FAT(FAT) + Sequence
        WriteType = 4
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write routine with WriteType:%d.\n" % WriteType)
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # Write FAT (DIR) + Sequence
        WriteType = 5
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write routine with WriteType:%d.\n" % WriteType)
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # Write FAT(BITMAP) + Sequece
        WriteType = 6
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write routine with WriteType:%d.\n" % WriteType)
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # Use Reserved Bit
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl routine with Argument:%d\n" % ReservedBit)
        self.__dvtLib.SpeedClassControl(SpeedClassCommandDescription = ReservedBit)

        # Write RU+Sequence
        WriteType = 2
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write routine with WriteType:%d.\n" % WriteType)
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])


    def Run(self):
        """
        Name : Run
        """

        # Initialize the SD card
        self.__sdCmdObj.DoBasicInit()

        # Call Script LoadCmd20Variables Utility Script
        self.__cmd20variables = LoadCMD20_Variables.CMD20_UT01_LoadCMD20_Variables(self.vtfContainer).Run()

        self.__cmd20variables["ExpectSequence"] = 1
        for ReservedBit in range(0x2, 0x10, 0x1):
            if ReservedBit == 0x4:
                continue
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Reserved Bit : 0x%X" % ReservedBit)
            self.ReservedBitsTest(ReservedBit, self.__cmd20variables)

        return 0
    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_CMD20_TC001_ReservedBitsTest(self):
        obj = CMD20_TC001_ReservedBitsTest(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
