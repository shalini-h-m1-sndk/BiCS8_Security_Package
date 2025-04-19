"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                :
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : CMD20_TC006_SequenceWriteUntilEndOfMemoryRandomTests.py
# DESCRIPTION                    : The purpose of this test case is to test the flow:
                                        1. CMD20 Sequence write until end of memory - Main Flow
                                        2. CMD20 Sequence write until end of memory - Random Tests
# PRERQUISTE                     :
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=CMD20_TC006_SequenceWriteUntilEndOfMemoryRandomTests --isModel=false --enable_console_log=1 --adapter=0
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
import CMD20_UT02_GetSequence as GetSequence
import CMD20_UT03_Write as Write
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
class CMD20_TC006_SequenceWriteUntilEndOfMemoryRandomTests(customize_log):
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
        self.__cmd20variables = LoadCMD20_Variables.CMD20_UT01_LoadCMD20_Variables(self.vtfContainer)
        self.__cmd20Write = Write.CMD20_UT03_Write(self.vtfContainer)
        self.__allowedCmds = AllowedCommands.CMD20_UT04_AllowedCommands(self.vtfContainer)
        self.__getSequence = GetSequence.CMD20_UT02_GetSequence(self.vtfContainer)


    # Testcase logic - Starts
    def Run(self):
        """
        Name : Run
         # Call globalInitCard
         # Call Cmd20Variables
         # Intialize Needed values from Cmd20Variables
         # CMD20 Sequence write until end of memory - Main Flow
         # Create DIR
         # Call Script Utility_CMD20_Write
         # Call Script Utility_AllowedCommands
         # Start Recording
         # Call Utility_CMD20_GetSequence, Commented as All Steps in this utility are Commented
         # Perform Multiple Write and Read with random value
                select Random = rand%5
                # if Random value '0'
                # if Random value '1'
                # Update CI
                # if Random value '2'
                # if Random value '3'
                # if Random value '4'
        """

        # Call globalInitCard
        self.__sdCmdObj.DoBasicInit()

        # Call Cmd20Variables
        cmd20variables = self.__cmd20variables.Run()

        ### Main Flow ###
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD20 Sequence write until end of memory - Main Flow.\n")
        for i in range(0, 50):

            # Create DIR
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

            # Call Script Utility_CMD20_Write
            WriteType = 1
            self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = cmd20variables)

            cmd20variables["AllowedCommand"] = 0

            # Call Script Utility_AllowedCommands
            self.__allowedCmds.Run(AllowedCommand = cmd20variables["AllowedCommand"])

            # Start Recording
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING, TimeOut = 1000)

            # Call Utility_CMD20_GetSequence
            cmd20variables["ExpectSequence"] = 1
            self.__getSequence.Run(cmd20variables["ExpectSequence"])

            cmd20variables['RuStartBlock'] = cmd20variables['Lba_of_first_AU']

            # Perform Multiple Write and Read with random value
            Loops = random.randrange(0, (512 + 1))

            for j in range(0, Loops):
                Random = random.randrange(0, 5)

                # if Random value '0'
                if Random == 0:

                    StartLBA = cmd20variables['RuStartBlock']
                    BlockCount = cmd20variables['RU']
                    self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

                    # Call Utility_CMD20_GetSequence
                    self.__getSequence.Run(cmd20variables['ExpectSequence'])

                    self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

                    cmd20variables['RuStartBlock'] = cmd20variables['RuStartBlock'] + cmd20variables['RU']

                # if Random value '1'
                if Random == 1 :
                    # Update CI
                    self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)

                    StartLBA = cmd20variables['CiStartBlock']
                    BlockCount = 0x1
                    self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_CONST)

                    # Call Utility_CMD20_GetSequence
                    self.__getSequence.Run(cmd20variables["ExpectSequence"])

                    self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_CONST)

                    cmd20variables['CiStartBlock'] = cmd20variables['CiStartBlock'] + 1
                    if cmd20variables['CiStartBlock'] > self.__cardMaxLba - 1 :
                        cmd20variables['CiStartBlock'] = cmd20variables['CiStartBlock'] - 1

                # if Random value '2'
                if Random == 2:

                    StartLBA = cmd20variables['FatRandomAddress']
                    BlockCount = cmd20variables['FatUpdateFatSize']
                    self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

                    # Call Utility_CMD20_GetSequence
                    self.__getSequence.Run(cmd20variables["ExpectSequence"])

                    self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

                    cmd20variables['FatRandomAddress'] = cmd20variables['FatRandomAddress'] + cmd20variables['FatUpdateFatSize']

                # if Random value '3'
                if Random == 3:

                    StartLBA = cmd20variables['BitmapRandomAddress']
                    BlockCount = cmd20variables['FatUpdateBitmapSize']
                    self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

                    # Call Utility_CMD20_GetSequence
                    self.__getSequence.Run(cmd20variables["ExpectSequence"])

                    self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

                    cmd20variables['BitmapRandomAddress'] = cmd20variables['BitmapRandomAddress'] + cmd20variables['FatUpdateBitmapSize']

                # if Random value '4'
                if Random == 4:

                    StartLBA = cmd20variables['FatRandomAddress']
                    BlockCount = 0x1
                    self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

                    # Call Utility_CMD20_GetSequence
                    self.__getSequence.Run(cmd20variables["ExpectSequence"])

                    self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

                    cmd20variables['FatRandomAddress'] = cmd20variables['FatRandomAddress'] + 1
        return 0
    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_CMD20_TC006_SequenceWriteUntilEndOfMemoryRandomTests(self):
        obj = CMD20_TC006_SequenceWriteUntilEndOfMemoryRandomTests(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
