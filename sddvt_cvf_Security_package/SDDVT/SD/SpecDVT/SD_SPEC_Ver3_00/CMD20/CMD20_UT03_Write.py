"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : CMD20_CA01_SDMode.st3
# SCRIPTER SCRIPT                : CMD20_UT03_Write.st3
# CVF CALL ALL SCRIPT            : CMD20_CA01_SDMode.py
# CVF SCRIPT                     : CMD20_UT03_Write.py
# DESCRIPTION                    : The purpose of this test is to check the read and writes to the card.
# PRERQUISTE                     : CMD20_UT01_LoadCMD20_Variables.py, CMD20_UT02_GetSequence.py
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
import CMD20_UT02_GetSequence as Cmd20GetSequence

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
class CMD20_UT03_Write(customize_log):
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
        self.__getSequence = Cmd20GetSequence.CMD20_UT02_GetSequence(self.vtfContainer)

    # Testcase Utility Logic - Starts
    def Run(self, WriteType = 0, StartBlock = 0x0, BlockCount = 0x1, DataType = 1, CiSequence = 0, ret = 0,
            RuSequence = 1, cmd20variables = None, ExpectSequence = 0):
        """
        Name : Run
        """
        if (cmd20variables == None):
            cmd20variables = LoadCMD20_Variables.CMD20_UT01_LoadCMD20_Variables(self.vtfContainer).Run()

        Random = random.randrange(0, 2)

        U = self.__cardMaxLba

        if WriteType == 1:

            # Start LBA
            StartLBA = cmd20variables['DIRconstAddress']

            # Block Count
            NumOfBlocks = 1

            if Random == 0:
                self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)
                self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            if Random == 1:
                self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, SingleWrite = True, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)
                self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, SingleRead = True, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

        if WriteType == 2:

            # Start LBA
            StartLBA = cmd20variables['RuStartBlock']

            # Block Count
            NumOfBlocks = cmd20variables['RU']

            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            # Call Script Utility CMD20GetSequence
            self.__getSequence.Run(cmd20variables["ExpectSequence"])

            if RuSequence == 1:
                cmd20variables['RuStartBlock'] = cmd20variables['RuStartBlock'] + cmd20variables['RU']

            if RuSequence == 0:
                if cmd20variables['RuStartBlock'] % cmd20variables['AU'] == 0:
                    rand = random.randrange(0, (cmd20variables['NumOfAU'] - 1))
                    cmd20variables['RuStartBlock'] = (rand * cmd20variables['AU']) + cmd20variables['Lba_of_first_AU']
                    cmd20variables['RUStartBlockRead'] = cmd20variables['RuStartBlock']
                else:
                    cmd20variables['RuStartBlock'] = cmd20variables['RuStartBlock'] + cmd20variables['RU']

            # Call Script Utility_CMD20_GetSequence
            self.__getSequence.Run(cmd20variables["ExpectSequence"])

        if WriteType == 3:

            # Start LBA
            StartLBA = cmd20variables['CiStartBlock']

            # Block Count
            NumOfBlocks = 1

            if Random == 0:
                self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_CONST)
                self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_CONST)

            if Random == 1:
                self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, SingleWrite = True, pattern = gvar.GlobalConstants.PATTERN_CONST)
                self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, SingleRead = True, pattern = gvar.GlobalConstants.PATTERN_CONST)

            # Call Script Utility_CMD20_GetSequence
            self.__getSequence.Run(cmd20variables["ExpectSequence"])

            cmd20variables['CiStartBlock'] = cmd20variables['CiStartBlock'] + 1
            if cmd20variables['CiStartBlock'] > U  - 1:
                cmd20variables['CiStartBlock'] = cmd20variables['CiStartBlock'] - 1

            # Call Script Utility_CMD20_GetSequence
            self.__getSequence.Run(cmd20variables["ExpectSequence"])

        if WriteType == 4:

            # Start LBA
            StartLBA = cmd20variables['FatRandomAddress']

            # Block Count
            NumOfBlocks = cmd20variables['FatUpdateFatSize']

            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            cmd20variables['FatRandomAddress'] = cmd20variables['FatRandomAddress'] + cmd20variables['FatUpdateFatSize']

            # Call Script Utility_CMD20_GetSequence
            self.__getSequence.Run(cmd20variables["ExpectSequence"])

        if WriteType == 5:

            # Start LBA
            StartLBA = cmd20variables['FatRandomAddress']

            # Block Count
            NumOfBlocks = 1

            if Random == 0:
                self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)
                self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            if Random == 1:
                self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, SingleWrite = True, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)
                self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, SingleRead = True, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            # Call Script Utility_CMD20_GetSequence
            self.__getSequence.Run(cmd20variables["ExpectSequence"])

            cmd20variables['FatRandomAddress'] = cmd20variables['FatRandomAddress'] + 1

            # Call Script Utility_CMD20_GetSequence
            self.__getSequence.Run(cmd20variables["ExpectSequence"])

        if WriteType == 6:

            # Start LBA
            StartLBA = cmd20variables['BitmapRandomAddress']

            # Block Count
            NumOfBlocks = cmd20variables['FatUpdateBitmapSize']

            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            cmd20variables['BitmapRandomAddress'] = cmd20variables['BitmapRandomAddress'] + cmd20variables['FatUpdateBitmapSize']

            # Call Script Utility_CMD20_GetSequence
            self.__getSequence.Run(cmd20variables["ExpectSequence"])

        if WriteType == 7:

            rand = random.randrange(0, U - cmd20variables['Lba_of_first_AU'] - cmd20variables['RU'])
            RandomAddress = rand + cmd20variables['Lba_of_first_AU']

            # Start LBA
            StartLBA = RandomAddress

            # Block Count
            NumOfBlocks = cmd20variables['RU']

            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

        if WriteType == 8:

            # Start LBA
            StartLBA = cmd20variables['RuStartBlock']

            # Block Count
            NumOfBlocks = random.randrange(0, cmd20variables['RU'] - 1) + 1

            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

        if WriteType == 9:

            # Start LBA
            StartLBA = cmd20variables['BitmapRandomAddress']

            # Block Count
            NumOfBlocks = 0x22

            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

        if WriteType == 10:

            # Start LBA
            StartLBA = cmd20variables['FatRandomAddress']

            # Block Count
            NumOfBlocks = 0x33

            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

        if WriteType == 11:

            # Start LBA
            StartLBA = cmd20variables['FatRandomAddress']

            # Block Count
            NumOfBlocks = 2

            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

        if WriteType == 12:

            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartBlock, blockCount = BlockCount, pattern = DataType)
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartBlock, blockCount = BlockCount, pattern = DataType)

        if WriteType == 13:

            # Start LBA
            StartLBA = cmd20variables['CiStartBlock']

            # Block Count
            NumOfBlocks = 2

            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_CONST)
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_CONST)

        if WriteType == 14:

            # Start LBA
            StartLBA = cmd20variables['RuStartBlock']

            # Block Count
            NumOfBlocks = cmd20variables['RU']

            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_CONST)
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_CONST)

            # Call Script Utility_CMD20_GetSequence
            self.__getSequence.Run(cmd20variables["ExpectSequence"])

            cmd20variables['RuStartBlock'] = cmd20variables['RuStartBlock'] + cmd20variables['RU']
            if cmd20variables['RuStartBlock'] > U - cmd20variables['RU']:
                cmd20variables['RuStartBlock'] = cmd20variables['RuStartBlock'] - cmd20variables['AU']

            # Call Script Utility_CMD20_GetSequence
            self.__getSequence.Run(cmd20variables["ExpectSequence"])

        if WriteType == 15:

            # Start LBA
            StartLBA = cmd20variables['CiStartBlock']

            # Block Count
            NumOfBlocks = 1

            self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)
            self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = NumOfBlocks, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            # Call Script Utility_CMD20_GetSequence
            self.__getSequence.Run(cmd20variables["ExpectSequence"])

            if CiSequence == 1:
                cmd20variables['CiStartBlock'] = cmd20variables['CiStartBlock'] + 1

            if CiSequence == 0:
                if cmd20variables['CiStartBlock'] % cmd20variables['AU'] == 0:
                    rand = random.randrange(0, (cmd20variables['NumOfAU'] - 1))
                    cmd20variables['CiStartBlock'] = (rand * cmd20variables['AU']) + cmd20variables['Lba_of_first_AU']
                    cmd20variables['CiStartBlockRead'] = cmd20variables['CiStartBlock']
                else:
                    cmd20variables['CiStartBlock'] = cmd20variables['CiStartBlock'] + 1

            # Call Script Utility_CMD20_GetSequence
            self.__getSequence.Run(cmd20variables["ExpectSequence"])

        return 0
    # Testcase Utility Logic - Ends
# Testcase Utility Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_CMD20_UT03_Write(self):
        obj = CMD20_UT03_Write(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
