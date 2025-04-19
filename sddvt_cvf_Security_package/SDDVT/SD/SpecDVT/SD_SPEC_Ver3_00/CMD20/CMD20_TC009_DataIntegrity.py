"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT        : CMD20_CA01_SDMode.st3
# SCRIPTER SCRIPT               : CMD20_TC009_DataIntegrity.st3
# CVF CALL ALL SCRIPT           : CMD20_CA01_SDMode.py
# CVF SCRIPT                    : CMD20_TC009_DataIntegrity.py
# DESCRIPTION                   : The purpose of this test case is to test the flow:
                                        1. Data Integrity after multiple SCC commands
# PRERQUISTE                    : CMD20_UT01_LoadCMD20_Variables.py, CMD20_UT02_GetSequence.py, CMD20_UT07_LoadLocal_Variables.py
# STANDALONE EXECUTION          : Yes
# TEST ARGUMENTS                : --test=CMD20_TC009_DataIntegrity --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                   : None
# DATE                          : Nov-2022
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
import CMD20_UT02_GetSequence as CMD20GetSequence
import CMD20_UT07_LoadLocal_Variables as LocalVariables

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
class CMD20_TC009_DataIntegrity(customize_log):
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
        self.ExpectSequence = 0
        self.y = 0
        self.z = 0
        self.zz = 0
        self.x = 0
        self.RU_IN_AU = 0


    # Testcase logic - Starts
    def WriteRU(self):
        # SetLabel: WriteRU

        StartLBA = self.xx
        BlockCount = self.__cmd20variables['RU']
        # Perform Multiple Write and Read from RuStartBlock to RU no.of Blocks
        self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)
        self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

        self.xx += self.__cmd20variables['RU']
        self.RU_IN_AU -= 1

        if self.RU_IN_AU == 0:
            self.x = 0

        if self.x == 1:
            self.WriteRU()

    def WriteBitMap(self):

        StartLBA = self.zz
        BlockCount = 0x20

        # SetLabel: WriteBitmap
        # Perform Multiple Write and Read from BitmapStartAddress to 20 Blocks
        self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

        # Perform Multiple Read
        self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

        self.zz += 32
        self.xx = self.__cmd20variables['RuStartBlock']

        # Call Script Utility_CMD20_GetSequence
        self.__getSequence.Run(self.ExpectSequence)

        self.x = 1
        self.RU_IN_AU = old_div(self.__cmd20variables['AU'], self.__cmd20variables['RU'])

    def WriteFAT(self):

        StartLBA = self.z
        BlockCount = 0x20

        # SetLabel: WriteFAT
        # Perform Multiple Write
        self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

        # Perform Multiple Read
        self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

        self.z += 32
        self.zz = self.__cmd20variables['BitmapStartAddress']

        # Call Script Utility_CMD20_GetSequence
        self.__getSequence.Run(self.ExpectSequence)

    def WriteCI(self):
        # Set Label : WriteCI

        # Update CI
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)

        StartLBA = self.y
        BlockCount = 0x1
        self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

        self.y += 1
        self.z = self.__cmd20variables['FatStartAdress']

        # Call Script Utility_CMD20_GetSequence
        self.__getSequence.Run(self.ExpectSequence)


    def WriteDIR(self):
        # SET LABEL : WriteDIR

        # Multiple Write from self.y with 0x1 blocks
        StartLBA = self.y
        BlockCount = 0x1
        self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

        self.y += 1

        # Start Recording
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING, TimeOut = 1000)

        self.ExpectSequence = 1

        # Call Script Utility_CMD20_GetSequence
        self.__getSequence.Run(self.ExpectSequence)

    def ReadVerify(self):
        pass

    def Run(self):
        """
        Name : Run

        # Call : globalInitCard
        # Load Variables from the Script Utility_Load_LocalVariables
        # Load CMD20 Specific variables from the Script Utility_CMD20_Variables
        # Intialize variables required for Steps
        # Multiple Write from 0x0 to 'AU'
        # Multiple Read from 0x0 to 'AU'
        # Create DIR
        # SET LABEL : WriteDIR
        # Multiple Write from self.y to 0x1 blocks
        # Start Recording
        # Set Label : WriteCI
        # Update CI
        # Perform MultipleWrite from self.y to 0x1 blocks
        # SetLabel: WriteFAT
            # Perform Multiple Write
            # Perform Multiple Read
        # SetLabel: WriteBitmap
        # Perform Multiple Write and Read from BitmapStartAddress  to 20 Blocks
        # SetLabel: WriteRU
        # Perform Multiple Write and Read from RuStartBlock  to RU no.of Blocks
        """

        # Initialize the SD card
        self.__sdCmdObj.DoBasicInit()

        # Load Variables from the Script Utility_Load_LocalVariables
        self.__localVariables = LocalVariables.CMD20_UT07_LoadLocal_Variables(self.vtfContainer).Run(ret = 1)

        # Load Cmd20 variables from Utility_LoadCMD20_Variables
        self.__cmd20variables = LoadCMD20_Variables.CMD20_UT01_LoadCMD20_Variables(self.vtfContainer).Run()

        # Intialize variables required for Steps
        U = self.__cardMaxLba
        RU_IN_AU = old_div(self.__cmd20variables['AU'], self.__cmd20variables['RU'])
        NUM_OF_LOOPS = old_div(U, self.__cmd20variables['AU'])

        StartLBA = 0x0
        BlockCount = self.__cmd20variables['AU']

        # Multiple Write from 0x0 with blockCount 'AU'
        self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

        # Multiple Read from 0x0 with blockCount 'AU'
        self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

        # Create DIR
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

        self.y = self.__cmd20variables['Lba_of_first_AU']

        # Label : WriteDIR
        self.WriteDIR()

        # Label : WriteCI
        self.WriteCI()

        # Label : WriteFAT
        self.WriteFAT()

        # Label : WriteBitMap()
        self.WriteBitMap()

        # Label : WriteRU
        self.WriteRU()

        # 1. Read Verify during the sequence
        # 2. Read Verify out of the sequence
        # 3. Read Verify after soft reset
        # 4. Read Verify after power cycle

        self.ReadVerify()

        NUM_OF_LOOPS = NUM_OF_LOOPS - 1
        while NUM_OF_LOOPS:
            self.WriteCI()
            self.WriteFAT()
            self.WriteBitMap()
            self.WriteRU()
            self.ReadVerify()
            NUM_OF_LOOPS = NUM_OF_LOOPS - 1

        StartLBA = 0x0
        BlockCount = self.__cmd20variables['AU']
        self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

        self.ExpectSequence = 0

        # Call Script Utility_CMD20_GetSequence
        self.__getSequence.Run(self.ExpectSequence)
        self.ReadVerify()

        self.__localVariables['SendOCR'] = self.__localVariables['HcsXpcS18r110']
        self.__localVariables['ExpectOCR'] = self.__localVariables['ReadyCcs18a110']
        self.__localVariables['ProtocolMode'] = 1
        self.__localVariables['VerifyType'] = 0
        self.__localVariables['SetPower'] = 0
        self.__localVariables['SendCMD0'] = 1
        self.__localVariables['SendCMD8'] = 1

        self.__sdCmdObj.DoBasicInit()
        self.ReadVerify()

        self.__localVariables['SetPower'] = 1
        self.__sdCmdObj.DoBasicInit()
        self.ReadVerify()
        return 0
    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_CMD20_TC009_DataIntegrity(self):
        obj = CMD20_TC009_DataIntegrity(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
