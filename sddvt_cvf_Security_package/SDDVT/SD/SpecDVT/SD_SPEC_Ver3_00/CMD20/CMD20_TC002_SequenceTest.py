"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : CMD20_CA01_SDMode.st3
# SCRIPTER SCRIPT                : CMD20_TC002_SequenceTest.st3
# CVF CALL ALL SCRIPT            : CMD20_CA01_SDMode.py
# CVF SCRIPT                     : CMD20_TC002_SequenceTest.py
# DESCRIPTION                    : The purpose of this test case is to test the flow:
                                        1. All legal combinations of CMD20
                                        2. Sequence Allowed Commands
# PRERQUISTE                     : CMD20_UT01_LoadCMD20_Variables.py, CMD20_UT02_GetSequence.py, CMD20_UT03_Write.py, CMD20_UT04_AllowedCommands.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=CMD20_TC002_SequenceTest --isModel=false --enable_console_log=1 --adapter=0
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
import CMD20_UT04_AllowedCommands as AllowedCommands

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
class CMD20_TC002_SequenceTest(customize_log):
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
        self.__allowedCmds = AllowedCommands.CMD20_UT04_AllowedCommands(self.vtfContainer)

    # Testcase logic - Starts
    def AllowComandTest(self):
        """
        Testing Allowed Multiple Write and Read types

        # CreateDIR
        # Call Script Utility_CMD20_Write, WriteType = 1
        # Call Script Utility_AllowedCommands
        # Start Recording
        # GetSequence
        # Call Script Utility_CMD20_Write, WriteType = 2
        # UpdateCI
        # Call Script Utility_CMD20_Write, WriteType = 3
        # Call Script Utility_CMD20_Write, WriteType = 4
        # Call Script Utility_CMD20_Write, WriteType = 5
        # Call Script Utility_CMD20_Write, WriteType = 6
        # Call Script Utility_CMD20_Write, WriteType = 2
        """

        # CreateDIR
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

        # Call Script Utility_CMD20_Write
        WriteType = 1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

        # Call Script Utility_AllowedCommands
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call AllowedCommand API with WriteType: %d\n" % WriteType)
        self.__allowedCmds.Run(AllowedCommand = self.__cmd20variables['NotAllowedCommand'], Cmd20Variables = self.__cmd20variables)

        # Start Recording
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl API with Argument: 0x0\n")
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING, TimeOut = 1000)

        # Call Script Utility CMD20GetSequence
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20GetSequence routine.\n")
        self.__getSequence.Run(self.__cmd20variables["ExpectSequence"])

        # Call Script Utility_CMD20_Write
        WriteType = 2
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

        #UpdateCI
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl API with Argument: 0x4\n")
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)

        # Write CI + Sequence
        WriteType = 3
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

        # Wrte FAT(FAT) + Sequence
        WriteType = 4
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

        # Wrte FAT(DIR) + Sequence
        WriteType = 5
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

        # Wrte FAT(BITMAP) + Sequence
        WriteType = 6
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

        # Wrte RU + Sequence
        WriteType = 2
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)


    def FatUpdate(self, Counter):
        """
        FatUpdate Method for different values of Counter
        Counter = 0
            # Call Script Utility_CMD20_Write, WriteType = 4
            # Call Script Utility_CMD20_Write, WriteType = 6
            # Call Script Utility_CMD20_Write, WriteType = 5
        Counter = 1
            # Call Script Utility_CMD20_Write, WriteType = 4
            # Call Script Utility_CMD20_Write, WriteType = 5
            # Call Script Utility_CMD20_Write, WriteType = 6
        Counter = 2:
            # Call Script Utility_CMD20_Write,  WriteType = 5
            # Call Script Utility_CMD20_Write, WriteType = 4
            # Call Script Utility_CMD20_Write, WriteType = 6
        Counter = 3:
            # Call Script Utility_CMD20_Write, WriteType = 5
            # Call Script Utility_CMD20_Write,  WriteType = 6
            # Call Script Utility_CMD20_Write,  WriteType = 4
       Counter == 4:
            # Call Script Utility_CMD20_Write,  WriteType = 6
            # Call Script Utility_CMD20_Write,  WriteType = 5
            # Call Script Utility_CMD20_Write,  WriteType = 4

        Counter == 5:
            # Call Script Utility_CMD20_Write,  WriteType = 6
            # Call Script Utility_CMD20_Write,  WriteType = 4
            # Call Script Utility_CMD20_Write,  WriteType = 5
        """

        if Counter == 0:
            # Write FAT(FAT) + sequence
            WriteType = 4
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Write FAT(BITMAP) + sequence
            WriteType = 6
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Write FAT(DIR) + sequence
            WriteType = 5
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

        if Counter == 1:

            # Write FAT(FAT) + sequence
            WriteType = 4
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Write FAT(DIR) + sequence
            WriteType = 5
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Write FAT(BITMAP) + sequence
            WriteType = 6
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

        if Counter == 2:

            # Write FAT(DIR) + sequence
            WriteType = 5
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Write FAT(FAT) + sequence
            WriteType = 4
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Write FAT(BITMAP) + sequence
            WriteType = 6
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

        if Counter == 3:

            # Write FAT(DIR) + sequence
            WriteType = 5
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Write FAT(BITMAP) + sequence
            WriteType = 6
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Write FAT(FAT) + sequence
            WriteType = 4
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

        if Counter == 4:

            # Write FAT(BITMAP) + sequence
            WriteType = 6
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Write FAT(DIR) + sequence
            WriteType = 5
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Write FAT(FAT) + sequence
            WriteType = 4
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

        if Counter == 5:

            # Write FAT(BITMAP) + sequence
            WriteType = 6
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Write FAT(FAT) + sequence
            WriteType = 4
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Write FAT(DIR) + sequence
            WriteType = 5
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)


    def BeforeStartRecording(self, Counter):
        """
        Method for Testing Multiple W/R before Start Recording
        for different values of the Counter
        Counter = 0:
            # Call Script Utility_CMD20_Write,  WriteType = 1
            # Call Script Utility_Allowed_Command, AllowedCommand=None
            # Call Script Utility_CMD20_Write,  WriteType = 7
        Counter = 1:
            # Call Script Utility_CMD20_Write,  WriteType = 1
            # Call Script Utility_CMD20_Write,  WriteType = 7
            # Call Script Utility_Allowed_Command, AllowedCommand=None

        Counter = 2:
            # Call Script Utility_CMD20_Write,  WriteType = 7
            # Call Script Utility_CMD20_Write,  WriteType = 1
            # Call Script Utility_Allowed_Command, AllowedCommand=None

        Counter == 3:
            # Call Script Utility_CMD20_Write,  WriteType = 7
            # Call Script Utility_Allowed_Command, AllowedCommand=None
            # Call Script Utility_CMD20_Write,  WriteType = 1

        Counter == 4:
            # Call Script Utility_Allowed_Command, AllowedCommand=None
            # Call Script Utility_CMD20_Write,  WriteType = 7
            # Call Script Utility_CMD20_Write,  WriteType = 1

        Counter == 5:
            # Call Script Utility_Allowed_Command, AllowedCommand=None
            # Call Script Utility_CMD20_Write, WriteType = 1
            # Call Script Utility_CMD20_Write,  WriteType = 7
        """

        if Counter == 0:
            # Write DIR + Sequence
            WriteType = 1
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Call Script Utility_Allowed_Commands
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call AllowedCommand routine.\n")
            self.__allowedCmds.Run(AllowedCommand = Counter, Cmd20Variables = self.__cmd20variables)

            # Other Write + Sequence
            WriteType = 7
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

        if Counter == 1:

            # Write DIR + Sequence
            WriteType = 1
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Other Write + Sequence
            WriteType = 7
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Call Script Utility_Allowed_Commands
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call AllowedCommand routine. \n")
            self.__allowedCmds.Run(AllowedCommand = Counter, Cmd20Variables = self.__cmd20variables)

        if Counter == 2:

            # Call Script Utility_CMD20_Write
            WriteType = 7
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Write DIR + Sequence
            WriteType = 1
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Call Script Utility_Allowed_Commands
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call AllowedCommand routine. \n")
            self.__allowedCmds.Run(AllowedCommand = Counter, Cmd20Variables = self.__cmd20variables)

        if Counter == 3:

            # Call Script Utility_CMD20_Write
            WriteType = 7
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Call Script Utility_Allowed_Commands
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call AllowedCommand routine. \n")
            self.__allowedCmds.Run(AllowedCommand = Counter, Cmd20Variables = self.__cmd20variables)

            # Write DIR + Sequence
            WriteType = 1
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

        if Counter == 4:

            # Call Script Utility_Allowed_Commands
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call AllowedCommand routine. \n")
            self.__allowedCmds.Run(AllowedCommand = Counter, Cmd20Variables = self.__cmd20variables)

            # Call Script Utility_CMD20_Write
            WriteType = 7
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Write DIR + Sequence
            WriteType = 1
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

        if Counter == 5:

            # Call Script Utility_Allowed_Commands
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call AllowedCommand routine. \n")
            self.__allowedCmds.Run(AllowedCommand = Counter, Cmd20Variables = self.__cmd20variables)

            # Write DIR + Sequence
            WriteType = 1
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Call Script Utility_CMD20_Write
            WriteType = 7
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)


    def AfterStartRecording(self, Counter):
        """
        Method for Testing Multiple Write and Read after Start Recording
        of different Counter Values
        Counter == 0:
            # Update CI
            # Call Script Utility_CMD20_Write,  WriteType = 3
            # Call Script Utility_CMD20_Write,  WriteType = 4
            # Call Script Utility_CMD20_Write,  WriteType = 5
            # Call Script Utility_CMD20_Write,  WriteType = 6
            # Call Script Utility_CMD20_Write,  WriteType = 2

        Counter == 1:
            # Update CI
            # Call Script Utility_CMD20_Write,  WriteType = 3
            # Call Script Utility_CMD20_Write,  WriteType = 2
            # Call Script Utility_CMD20_Write,  WriteType = 4
            # Call Script Utility_CMD20_Write,  WriteType = 5
            # Call Script Utility_CMD20_Write,  WriteType = 6
        Counter == 2:
            # Call Script Utility_CMD20_Write,  WriteType = 2
            # Update CI
            # Call Script Utility_CMD20_Write,  WriteType = 3
            # Call Script Utility_CMD20_Write,  WriteType = 4
            # Call Script Utility_CMD20_Write,  WriteType = 5
            # Call Script Utility_CMD20_Write,  WriteType = 6

        Counter == 3:
            # Call Script Utility_CMD20_Write,  WriteType = 2
            # Call Script Utility_CMD20_Write,  WriteType = 4
            # Call Script Utility_CMD20_Write,  WriteType = 5
            # Call Script Utility_CMD20_Write,  WriteType = 6
            # Update CI
            # Call Script Utility_CMD20_Write,  WriteType = 3
        Counter == 4:
            # Call Script Utility_CMD20_Write,  WriteType = 4
            # Call Script Utility_CMD20_Write,  WriteType = 5
            # Call Script Utility_CMD20_Write,  WriteType = 6
            #STEP 28 Call Script Utility_CMD20_Write,  WriteType = 2
            # Update CI
            # Call Script Utility_CMD20_Write,  WriteType = 3

        Counter == 5:
            # Call Script Utility_CMD20_Write, WriteType = 4
            # Call Script Utility_CMD20_Write, WriteType = 5
            # Call Script Utility_CMD20_Write, WriteType = 6
            # Update CI
            # Call Script Utility_CMD20_Write, WriteType = 3
            # Call Script Utility_CMD20_Write, WriteType = 2
        """

        if Counter == 0:
            # Update CI
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl API with Argument: 0x4\n")
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)

            # Write CI + Sequence
            WriteType = 3
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Write FAT(FAT) + Sequence
            WriteType = 4
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Write FAT(DIR) + Sequence
            WriteType = 5
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Write FAT(BITMAP) + Sequence
            WriteType = 6
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Write RU + Sequence
            WriteType = 2
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

        if Counter == 1:

            #Update CI
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)

            # Update CI+Sequence
            WriteType = 3
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Update RU + Sequence
            WriteType = 2
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Update FAT(FAT) + Sequence
            WriteType = 4
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Update FAT(DIR) + Sequence
            WriteType = 5
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Update FAT(BITMAP) + Sequence
            WriteType = 6
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

        if Counter == 2:

            # Write RU + Sequence
            WriteType = 2
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            #Update CI
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)

            # Write CI + Sequence
            WriteType = 3
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Update FAT(FAT) + Sequence
            WriteType = 4
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Update FAT(DIR) + Sequence
            WriteType = 5
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Update FAT(BITMAP) + Sequence
            WriteType = 6
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

        if Counter == 3:

            # Write RU + Sequence
            WriteType = 2
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Update FAT(FAT) + Sequence
            WriteType = 4
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Update FAT(DIR) + Sequence
            WriteType = 5
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Update FAT(BITMAP) + Sequence
            WriteType = 6
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            #Update CI
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)

            # Write CI + Sequence
            WriteType = 3
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

        if Counter == 4:

            # Update FAT(FAT) + Sequence
            WriteType = 4
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Update FAT(DIR) + Sequence
            WriteType = 5
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Update FAT(BITMAP) + Sequence
            WriteType = 6
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Write RU + Sequence
            WriteType = 2
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            #Update CI
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)

            # Write CI + Sequence
            WriteType = 3
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

        if Counter == 5:

            # Update FAT(FAT) + Sequence
            WriteType = 4
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Update FAT(DIR) + Sequence
            WriteType = 5
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Update FAT(BITMAP) + Sequence
            WriteType = 6
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            #Update CI
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)

            # Write CI + Sequence
            WriteType = 3
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Write RU + Sequence
            WriteType = 2
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)


    def Run(self):
        """
        Name : Run

        # Call script globalInitCard
        # Call Script LoadCmd20Variables Utility Script
        # All legal combinations of CMD20 Sequence Allowed Commands
        # All legal combinations of CMD20 Sequence FAT Update
                # Create DIR
                # Call Script Utility_CMD20_Write, Write Type = 2
                # Call Script Utility_CMD20_Write
                # Call Script Utility_CMD20_Write
        # All legal combinations of CMD20 Sequence Between Create Dir and Start Recording
                # Create DIR
                # Call Script Utility_CMD20_Write
                # Call Script Utility_CMD20_Write, WriteType = 3
                # Call Script Utility_CMD20_Write, WriteType = 4
                # Call Script Utility_CMD20_Write, WriteType = 5
                # Call Script Utility_CMD20_Write, WriteType = 6
                # Call Script Utility_CMD20_Write, WriteType = 2
        # All legal combinations of CMD20 Sequence After Start Recording
                # Create DIR
                # Call Script Utility_CMD20_Write, WriteType = 1
                # Call Script Utility_CMD20_Write, WriteType = 2
        """

        # Initialize the SD card
        self.__sdCmdObj.DoBasicInit()

        # Call LoadCmd20Variables Utility Script
        self.__cmd20variables = LoadCMD20_Variables.CMD20_UT01_LoadCMD20_Variables(self.vtfContainer).Run()

        # All legal combinations of CMD20 Sequence Allowed Commands
        Random = random.randrange(0, 2)

        Counter = 0
        #Note: In the Scripter this loop executes only once instead of 7
        while Counter < 1:
            self.__cmd20variables['NotAllowedCommand'] = Counter
            self.AllowComandTest()
            Counter = Counter + 1

        # All legal combinations of CMD20 Sequence FAT Update
        Counter = 0
        #Note: In the scripter this loop executes only once instead of 6
        while Counter < 1:

            # Create DIR
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl API with Argument: 0x1\n")
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

            WriteType = 1
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call AllowedCommand API\n")
            self.__allowedCmds.Run(AllowedCommand = Counter, Cmd20Variables = self.__cmd20variables)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl API with Argument: 0x0\n")
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING, TimeOut = 1000)

            # Call Script Utility_CMD20_GetSequence
            self.__getSequence.Run(self.__cmd20variables["ExpectSequence"])

            # Call Script Utility_CMD20_Write
            WriteType = 2
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            if Random == 1:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl API with Argument: 0x4\n")
                self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)

                # Call Script Utility_CMD20_Write
                WriteType = 3
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
                self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            self.FatUpdate(Counter)

            # Call Script Utility_CMD20_Write
            WriteType = 2
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            Counter = Counter + 1

        # All legal combinations of CMD20 Sequence Between Create Dir and Start Recording
        Counter = 0
        # Note: In the scripter this loop executes only once instead of 6
        while Counter < 1:

            # Create DIR
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl API with Argument: 0x1\n")
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

            # Call Script Utility_CMD20_GetSequence
            self.__getSequence.Run(self.__cmd20variables["ExpectSequence"])

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call BeforeStartRecording routine with Counter Value: %d\n" % (Counter))
            self.BeforeStartRecording(Counter)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl API with Argument: 0x0\n")
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING, TimeOut = 1000)

            # Call Script Utility_CMD20_GetSequence
            self.__getSequence.Run(self.__cmd20variables["ExpectSequence"])

            # Call Script Utility_CMD20_Write
            WriteType = 2
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            if Random == 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl API with Argument: 0x4\n")
                self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)

                # Call Script Utility_CMD20_Write
                WriteType = 3
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
                self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Call Script Utility_CMD20_Write
            WriteType = 4
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Call Script Utility_CMD20_Write
            WriteType = 5
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Call Script Utility_CMD20_Write
            WriteType = 6
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            # Call Script Utility_CMD20_Write
            WriteType = 2
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            Counter = Counter + 1

        # All legal combinations of CMD20 Sequence After Start Recording
        Counter = 0
        # Note: In the scripter this loop executes only once instead of 6
        while Counter < 1:

            # Create DIR
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl API with Argument: 0x1\n")
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

            # Get Sequence
            self.__getSequence.Run(self.__cmd20variables["ExpectSequence"])

            # Call Script Utility_CMD20_Write
            WriteType = 1
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call AllowedCommand API \n")
            self.__allowedCmds.Run(AllowedCommand = Counter, Cmd20Variables = self.__cmd20variables)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call SpeedClassControl API with Argument: 0x0\n")
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING, TimeOut = 1000)

            # Get Sequence
            self.__getSequence.Run(self.__cmd20variables["ExpectSequence"])

            # Call Script Utility_CMD20_Write
            WriteType = 2
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call CMD20Write API with WriteType: %d\n" % WriteType)
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = self.__cmd20variables)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call AfterStartRecording routine with Counter Value: %d\n" % (Counter))
            self.AfterStartRecording(Counter)

            Counter = Counter + 1
        return 0
    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_CMD20_TC002_SequenceTest(self):
        obj = CMD20_TC002_SequenceTest(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
