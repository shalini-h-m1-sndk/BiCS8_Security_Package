"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : CMD20_CA01_SDMode.st3
# SCRIPTER SCRIPT                : CMD20_TC005_SequenceWriteUntilEndOfMemoryMainFlow.st3
# CVF CALL ALL SCRIPT            : CMD20_CA01_SDMode.py
# CVF SCRIPT                     : CMD20_TC005_SequenceWriteUntilEndOfMemoryMainFlow.py
# DESCRIPTION                    : CMD20 Sequence write until end of memory - Main Flow
# PRERQUISTE                     : CMD20_UT01_LoadCMD20_Variables.py, CMD20_UT02_GetSequence.py, CMD20_UT03_Write.py, CMD20_UT04_AllowedCommands.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=CMD20_TC005_SequenceWriteUntilEndOfMemoryMainFlow --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : Nov-2022
################################################################################
"""

# Python future modules for python3 forward compatibility
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    from builtins import *
from past.utils import old_div

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
class CMD20_TC005_SequenceWriteUntilEndOfMemoryMainFlow(customize_log):
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
        """

        # Initialize the SD card
        self.__sdCmdObj.DoBasicInit()

        # Load CMD20 Variables
        CMD20Variables = self.__cmd20variables.Run()

        CMD20Variables['RuSequence'] = 1

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD20 Sequence write until end of memory - Main Flow.\n")

        # Create DIR
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

        # CAll script Utility_CMD20_Write, WriteType  = 1
        WriteType = 1
        self.__cmd20Write.Run(WriteType = WriteType, cmd20variables = CMD20Variables)

        # CAll script Utility_AllowedCommands, AllowedCommand = 0
        CMD20Variables["AllowedCommand"] = 0
        self.__allowedCmds.Run(AllowedCommand = CMD20Variables["AllowedCommand"])

        # Start Recording
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING, TimeOut = 1000)

        # Call Utility_CMD20_GetSequence as ExpectSequence
        CMD20Variables["ExpectSequence"] = 1
        self.__getSequence.Run(CMD20Variables["ExpectSequence"])

        CMD20Variables["RuStartBlock"] = CMD20Variables['Lba_of_first_AU']

        Flag = 0

        # Recordble User Area
        while not Flag:

            StartLBA = CMD20Variables["RuStartBlock"]
            BlockCount = (random.randrange(0, (old_div(CMD20Variables['AU'], CMD20Variables['RU']))) + 1) * CMD20Variables['RU']

            # Multiple Write from RuStartBlk to BlockCount
            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            # Call Utility_CMD20_GetSequence as ExpectSequence
            self.__getSequence.Run(CMD20Variables["ExpectSequence"])

            # Multiple Read from RuStartBlk to BlockCount
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            CMD20Variables['RuStartBlock'] = CMD20Variables["RuStartBlock"] + BlockCount

            # Update CI
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)

            # Multiple Write from CiStartBlock to 0x1
            StartLBA = CMD20Variables['CiStartBlock']
            BlockCount = 0x1
            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_CONST)

            # Call Utility_CMD20_GetSequence as ExpectSequence
            self.__getSequence.Run(CMD20Variables["ExpectSequence"])

            # Multiple Read from CiStartBlock to 0x1
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_CONST)

            CMD20Variables['CiStartBlock'] = CMD20Variables['CiStartBlock'] + 1

            if CMD20Variables['CiStartBlock'] > (self.__cardMaxLba - 1):
                CMD20Variables['CiStartBlock'] = CMD20Variables['CiStartBlock'] - 1

            StartLBA = CMD20Variables['FatRandomAddress']
            BlockCount = CMD20Variables['FatUpdateFatSize']
            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            # Call Utility_CMD20_GetSequence as ExpectSequence
            self.__getSequence.Run(CMD20Variables["ExpectSequence"])

            # Multiple READ from FatRandomAddress to FatUpdateFatSize
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            CMD20Variables['FatRandomAddress'] = CMD20Variables['FatRandomAddress'] + CMD20Variables['FatUpdateFatSize']

            # Multiple Write from BitmapRandomAddress to FatUpdateBitmapSize
            StartLBA = CMD20Variables['BitmapRandomAddress']
            BlockCount = CMD20Variables['FatUpdateBitmapSize']
            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            # Call Utility_CMD20_GetSequence as ExpectSequence
            self.__getSequence.Run(CMD20Variables["ExpectSequence"])

            # Multiple READ from BitmapRandomAddress to FatUpdateBitmapSize
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            CMD20Variables['BitmapRandomAddress'] = CMD20Variables['BitmapRandomAddress'] + CMD20Variables['FatUpdateBitmapSize']

            # Multiple Write from FatRandomAddress to 0x1
            StartLBA = CMD20Variables['FatRandomAddress']
            BlockCount = 0x1
            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            # Call Utility_CMD20_GetSequence as ExpectSequence
            self.__getSequence.Run(CMD20Variables["ExpectSequence"])

            # Multiple READ from FatRandomAddress to 0x1
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            CMD20Variables['FatRandomAddress'] = CMD20Variables['FatRandomAddress'] + 1

            if CMD20Variables['RuStartBlock'] > (self.__cardMaxLba - CMD20Variables['AU']):
                Flag = 1

        return 0
    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_CMD20_TC005_SequenceWriteUntilEndOfMemoryMainFlow(self):
        obj = CMD20_TC005_SequenceWriteUntilEndOfMemoryMainFlow(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
