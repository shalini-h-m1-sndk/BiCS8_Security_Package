"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : CMD20_CA01_SDMode.st3
# SCRIPTER SCRIPT                : CMD20_TC008_SequenceWriteUntilEndOfMemoryMainFlowReplaceRUandCIwrite.st3
# CVF CALL ALL SCRIPT            : CMD20_CA01_SDMode.py
# CVF SCRIPT                     : CMD20_TC008_SequenceWriteUntilEndOfMemoryMainFlowReplaceRUandCIwrite.py
# DESCRIPTION                    : The purpose of this test case is to test the flow:
                                        1. CMD20 Sequence write until end of memory - Main Flow
                                        2. CMD20 Sequence write until end of memory - Random Tests
# PRERQUISTE                     : CMD20_UT01_LoadCMD20_Variables.py, CMD20_UT02_GetSequence.py, CMD20_UT03_Write.py, CMD20_UT04_AllowedCommands.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=CMD20_TC008_SequenceWriteUntilEndOfMemoryMainFlowReplaceRUandCIwrite --isModel=false --enable_console_log=1 --adapter=0
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
    from builtins import range
    from builtins import *
from past.utils import old_div

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
class CMD20_TC008_SequenceWriteUntilEndOfMemoryMainFlowReplaceRUandCIwrite(customize_log):
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
        self.__getSequence = CMD20GetSequence.CMD20_UT02_GetSequence(self.vtfContainer)
        self.__cmd20Write = CMD20Write.CMD20_UT03_Write(self.vtfContainer)
        self.__allowedCmds = AllowedCommands.CMD20_UT04_AllowedCommands(self.vtfContainer)

    # Testcase logic - Starts

    def Run(self):
        """
        Name : Run

        STEP 1 : Call global init card
        STEP 2 : Load Cmd20 variables from Utility_LoadCMD20_Variables
        STEP 3 : Variable declarations
        STEP 4 : CreateDIR
        STEP 5 : GetSequence call with ExpectSequence = 1
        STEP 6 : Call CMD20 write with writetype = 1
        STEP 7 : Call AllowedCommands Utility with AllowedCommands = 0
        STEP 8 : Start recodring
        STEP 9 : GetSequence call with ExpectSequence = 1
        STEP 10: Start the loop for (AU/RU)*8
        STEP 11: Perform MultipleWrite & Read from RuStartBlock to RU
        STEP 12 : Update RUStartBlock variable
        STEP 13 : SCC: Update CI
        STEP 14 : Do Multiple Write and Read for CiStartBlock
        STEP 15 : Update CiStartBlock
        STEP 16 : Do Multiple Write and Read for FatRandomAddress to FatUpdateFatSize
        STEP 17 : Update FatRandomAddress variable
        STEP 18 : Do Multiple Write and Read for BitmapRandomAddress to FatUpdateBitmapSize
        STEP 19 : Update BitmapRandomAddress
        STEP 20 : Do Multiple Write and Read for FatRandomAddress to 0x1 Blocks
        STEP 21 : Update FatRandomAddress variable
        STEP 22 : Get in Speed Class mode
        STEP 23 : Loop  of Step 10 ends
        """

        # Initialize the SD card
        self.__sdCmdObj.DoBasicInit()

        # Load Cmd20 variables from Utility_LoadCMD20_Variables
        CMD20Variables = self.__cmd20variables.Run()

        # Variable declarations
        RuStartBlock = CMD20Variables['RuStartBlock']
        AU = CMD20Variables['AU']
        RU = CMD20Variables['RU']
        NumOfAU = CMD20Variables['NumOfAU']
        Lba_of_first_AU = CMD20Variables['Lba_of_first_AU']
        CiStartBlock = CMD20Variables['CiStartBlock']
        FatRandomAddress = CMD20Variables['FatRandomAddress']
        FatUpdateFatSize = CMD20Variables['FatUpdateFatSize']
        BitmapRandomAddress = CMD20Variables['BitmapRandomAddress']
        FatUpdateBitmapSize = CMD20Variables['FatUpdateBitmapSize']
        U = self.__cardMaxLba

        temp = RuStartBlock
        RuStartBlock = CiStartBlock

        if temp > (old_div(U, 2)):
            CiStartBlock = (temp - (10 * AU))

        if temp < (old_div(U, 2)):
            CiStartBlock = temp

        # Create DIR
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

        # Call GetSequence Utility
        CMD20Variables["ExpectSequence"] = 1
        self.__getSequence.Run(ExpectSequence = CMD20Variables["ExpectSequence"])

        # Call Utility_CMD20_Write, With WriteType = 1
        self.__cmd20Write.Run(WriteType = 1, cmd20variables = CMD20Variables, ExpectSequence = CMD20Variables["ExpectSequence"])

        # Call Utility_AllowedCommands Script
        self.__allowedCmds.Run(AllowedCommand = 0, Cmd20Variables = CMD20Variables)

        # Start Recording
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING, TimeOut = 1000)

        # Call GetSequence Utility
        self.__getSequence.Run(ExpectSequence = CMD20Variables["ExpectSequence"])

        # Start Loop for (AU / RU) * 8
        LOOPS = (old_div(AU, RU)) * 8

        for Loop in range(0, LOOPS):
            StartLBA = RuStartBlock
            BlockCount = RU

            # Multiple Write and Read from RUStartBlock to RU blocks
            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_CONST)
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_CONST)

            # Update RUStartBlock variable
            RuStartBlock = RuStartBlock + RU

            if RuStartBlock > (U - RU):
                RuStartBlock = RuStartBlock - AU

            # Update CI
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)

            StartLBA = CiStartBlock
            BlockCount = 1

            # Multiple Write and Read for CiStartBlock
            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            # Update CiStartBlock variable
            CiStartBlock = CiStartBlock + 1

            # Multiple Write and Read for FatRandomAddress to FatUpdateFatSize
            StartLBA = FatRandomAddress
            BlockCount = FatUpdateFatSize

            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            # Update FatRandomAddress variable
            FatRandomAddress = FatRandomAddress + FatUpdateFatSize

            # Multiple Write and Read for BitmapRandomAddress to FatUpdateBitmapSize
            StartLBA = BitmapRandomAddress
            BlockCount = FatUpdateBitmapSize

            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            # Update BitmapRandomAddress variable
            BitmapRandomAddress = BitmapRandomAddress + FatUpdateBitmapSize

            # Multiple Write and Read for FatRandomAddress to 0x1 Blocks
            StartLBA = FatRandomAddress
            BlockCount = 1

            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            # Update FatRandomAddress variable
            FatRandomAddress = FatRandomAddress + 1

            # Get in SpeedClass mode
            self.__dvtLib.GetInSpeedClassMode()

        return 0
    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_CMD20_TC008_SequenceWriteUntilEndOfMemoryMainFlowReplaceRUandCIwrite(self):
        obj = CMD20_TC008_SequenceWriteUntilEndOfMemoryMainFlowReplaceRUandCIwrite(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
