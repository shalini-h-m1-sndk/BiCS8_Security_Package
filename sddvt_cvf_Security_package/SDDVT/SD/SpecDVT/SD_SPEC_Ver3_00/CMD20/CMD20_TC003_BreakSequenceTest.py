"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : CMD20_CA01_SDMode.st3
# SCRIPTER SCRIPT                : CMD20_TC003_BreakSequenceTest.st3
# CVF CALL ALL SCRIPT            : CMD20_CA01_SDMode.py
# CVF SCRIPT                     : CMD20_TC003_BreakSequenceTest.py
# DESCRIPTION                    : The purpose of this test case is to test the flow:
                                        1. Break sequence between create DIR and start recording
                                        2. Break sequence after start recording
                                        3. Break sequence by replacing valid CMD20 arg with reserved bits
                                        4. After Start Recording - Create DIR
                                        5. Breaks the sequence, but starts new one and it is successfully completed
# PRERQUISTE                     :
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=CMD20_TC003_BreakSequenceTest --isModel=false --enable_console_log=1 --adapter=0
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
import CMD20_UT04_AllowedCommands as AllowedCommands
import CMD20_UT05_NotAllowedCommands as NotAllowedCommands

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
class CMD20_TC003_BreakSequenceTest(customize_log):
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
        self.__NotAllowedCommands = NotAllowedCommands.CMD20_UT05_NotAllowedCommands(self.vtfContainer)
        self.__Counter = 0
        self.__BreakType = 1
        self.__JumpSequence = 0
        self.__WriteType = 0


    # Testcase logic - Starts
    def NotAllowComandTest(self):
        """
        STEP 1 : Create DIR
        STEP 2 : Call Script Utility_CMD20_Write, WriteType = 1
        STEP 3 : Start Recording
        STEP 4 : Create DIR
        STEP 5 : Call Script Utility_CMD20_Write, WriteType = 1
        STEP 6 : Start Recording
        STEP 7 : Create DIR
        STEP 8 :  Call Script Utility_CMD20_Write, WriteType = 1
        STEP 9 :  Call Script Utility_CMD20_Write, WriteType = 7
        STEP 10 : Start Recording
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "NotAllowedCommandTest \n")
        # Create DIR
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

        # Call Script Utility_CMD20_Write
        self.__WriteType = 1
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])
        self.__NotAllowedCommands.Run(NotAllowedCommand = self.__cmd20variables["NotAllowedCommand"], CMD20Variables = self.__cmd20variables)

        # Start Recording
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING, TimeOut = 1000)

        self.__cmd20variables["ExpectSequence"] = 1

        # Get Sequence
        self.__getSequence.Run(self.__cmd20variables["ExpectSequence"])

        # Create DIR
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

        # Call Script Utility_CMD20_Write
        self.__WriteType = 1
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])
        self.__allowedCmds.Run(AllowedCommand = self.__cmd20variables["AllowedCommand"], Cmd20Variables = self.__cmd20variables)
        self.__NotAllowedCommands.Run(NotAllowedCommand = self.__cmd20variables["NotAllowedCommand"], CMD20Variables = self.__cmd20variables)

        # Start Recording
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING, TimeOut = 1000)

        self.__cmd20variables["ExpectSequence"] = 1
        # Get Sequence
        self.__getSequence.Run(self.__cmd20variables["ExpectSequence"])

        # Create DIR
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

        # Call Script Utility_CMD20_Write
        self.__WriteType = 1
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])
        self.__allowedCmds.Run(Cmd20Variables = self.__cmd20variables)

        # Call Script Utility_CMD20_Write
        self.__WriteType = 7
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])
        self.__NotAllowedCommands.Run(NotAllowedCommand = 0, CMD20Variables = self.__cmd20variables)

        # Start Recording
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING, TimeOut = 1000)

        self.__cmd20variables["ExpectSequence"] = 1
        # Get Sequence
        self.__getSequence.Run(self.__cmd20variables["ExpectSequence"])

    def SequenceBreak(self):
        """
        Check Sequence Break
        Counter = 0:
            BreakType = 1 :
                STEP 1 : Create DIR
            BreakType = 2 :
                STEP 2 : Call Script Utility_CMD20_Write, WriteType = 7
            BreakType = 3 :
                STEP 3 : Call Script Utility_CMD20_Write, WriteType = 8
            BreakType = 4:
                STEP 4: Call Script Utility_CMD20_Write, WriteType = 9
            BreakType = 5:
                STEP 5 : Call Script Utility_CMD20_Write, WriteType = 10
            BreakType = 6:
                STEP 6 : Call Script Utility_CMD20_Write, WriteType = 11
            BreakType = 7:
                STEP 7 : Call Script Utility_CMD20_Write, WriteType = 3
            BreakType = 8:
                STEP 8 : Update CI
                STEP 9:  Call Script Utility_CMD20_Write, WriteType = 2
            BreakType = 9:
                STEP 10 :  Call Script Utility_CMD20_Write, WriteType = 13
            BreakType == 10:
                STEP 11 : Call Script Utility_CMD20_Write, WriteType = 12
             BreakType  == 11:
                STEP 12: Call Script Utility_CMD20_Write, WriteType = 13
            BreakType == 12 :
                STEP 13 : Call Script Utility_CMD20_Write, WriteType = 13
                STEP 14 : Call Script Utility_CMD20_Write, WriteType = 13

        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SequenceBreak Call with values: Counter:%d, BreakType:%d\n" % (self.__Counter,self.__BreakType))

        self.__cmd20variables["ExpectSequence"] = 0
        if self.__Counter == 0:

            if self.__BreakType == 1:
                # Create DIR
                self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

            elif self.__BreakType == 2:
                # Call Script Utility_CMD20_Write
                self.__WriteType = 7
                self.__cmd20variables["ExpectSequence"] = 0
                self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            elif self.__BreakType == 3:
                # Call Script Utility_CMD20_Write
                self.__WriteType = 8
                self.__cmd20variables["ExpectSequence"] = 0
                self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            elif self.__BreakType == 4:
                # Call Script Utility_CMD20_Write
                self.__WriteType = 9
                self.__cmd20variables["ExpectSequence"] = 0
                self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            elif self.__BreakType == 5:
                # Call Script Utility_CMD20_Write
                self.__WriteType = 10
                self.__cmd20variables["ExpectSequence"] = 0
                self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            elif self.__BreakType == 6:
                # Call Script Utility_CMD20_Write
                self.__WriteType = 11
                self.__cmd20variables["ExpectSequence"] = 0
                self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            elif self.__BreakType == 7:
                # Call Script Utility_CMD20_Write
                self.__WriteType = 3
                self.__cmd20variables["ExpectSequence"] = 0

            elif self.__BreakType == 8:
                # Update CI
                self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)
                # Call Script Utility_CMD20_Write
                self.__WriteType = 2
                self.__cmd20variables["ExpectSequence"] = 0
                self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            elif self.__BreakType == 9:
                # Call Script Utility_CMD20_Write
                self.__WriteType = 13
                self.__cmd20variables["ExpectSequence"] = 0
                self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            elif self.__BreakType == 10:
                # Call Script Utility_CMD20_Write
                self.__WriteType = 12
                StartBlock = 0x0
                BlockCount = 0x1
                BlockSize  = 0x200
                DataType = 1
                self.__cmd20variables["ExpectSequence"] = 0
                self.__cmd20Write.Run(self.__WriteType, StartBlock, BlockCount, DataType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            elif self.__BreakType  == 11:

                StartLBA = self.__cardMaxLba
                BlockCount = self.__cmd20variables['RU']
                self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

                # Call Script Utility_CMD20_Write
                self.__cmd20variables["ExpectSequence"] = 0
                self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            elif self.__BreakType == 12 :

                StartLBA = self.__cardMaxLba - self.__cmd20variables["AU"]
                BlockCount = self.__cmd20variables['AU']
                self.__dvtLib.WriteWithFPGAPattern(StartLba =StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

                # Call Script Utility_CMD20_Write
                self.__cmd20variables["ExpectSequence"] = 1
                self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

                StartLBA = self.__cardMaxLba
                BlockCount = self.__cmd20variables['RU']
                self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

                # Call Script Utility_CMD20_Write
                self.__cmd20variables["ExpectSequence"] = 0
                self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            self.__Counter = self.__Counter + 1
            self.__cmd20variables["ExpectSequence"] = 1
            self.__JumpSequence = 1
            return

    def Sequence(self):

        while True:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Sequence Call with values: Counter:%d\n" % (self.__Counter))

            # Create DIR
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

            self.__WriteType = 1
            self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])
            self.__allowedCmds.Run(AllowedCommand = self.__cmd20variables["AllowedCommand"], Cmd20Variables = self.__cmd20variables)

            if self.__cmd20variables["AllowedCommand"] == 0:
                self.__WriteType = 12   # If AllowedCommand is 0, then WriteType would have been modified to 12 in CMD20_UT04_AllowedCommands.py file

            # Start Recording
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING, TimeOut = 1000)

            if self.__Counter == 0:
                self.SequenceBreak()

            self.__JumpSequence += 1

            if self.__JumpSequence == 1:
               continue

            # Call Script Utility_CMD20_Write
            self.__WriteType = 2
            self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            if self.__Counter == 1:
                self.SequenceBreak()

            if self.__JumpSequence == 1:
               continue

            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)

            # Call Script Utility_CMD20_Write
            self.__WriteType = 3
            self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            if self.__Counter == 2:
                self.SequenceBreak()

            if self.__JumpSequence == 1:
               continue

            # Call Script Utility_CMD20_Write
            self.__WriteType = 4
            self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            # Call Script Utility_CMD20_Write
            self.__WriteType = 5
            self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            # Call Script Utility_CMD20_Write
            self.__WriteType = 6
            self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            if self.__Counter == 3:
                self.SequenceBreak()

            if self.__JumpSequence == 1:
               continue

            # Call Script Utility_CMD20_Write
            self.__WriteType = 2
            self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            if self.__Counter == 4:
                self.SequenceBreak()

            if self.__JumpSequence == 1:
               continue

            if self.__BreakType < 13:
                self.__BreakType += 1
                continue

            break

        return 0 # END_OF_Sequence

    def Run(self):
        """
        Name : Run
        STEP 1 : Call script globalInitCard
        STEP 2 : Call Script LoadCmd20Variables Utility Script
        STEP 3 : Break sequence between Create DIR and Start Recording
        STEP 4 :  Break sequence After Start Recording
        STEP 5 : SET LABEL : Sequence
            STEP 5a: Create DIR
            STEP 5b : perform Write types

        STEP 6 : Using Argument 0x2
        Perform Write Types

        STEP 7: UpdateCI
        Perform Write Types

        STEP 8: CreateDIR
        Perform Write Types

        STEP 9: CreateDIR, Use Manual Argument
        Perform Write Types

        STEP 10:  UpdateCI, Use Manual Argument
        Perform Write Types

        STEP 11:  CreateDIR
        Perform Write Types

        STEP 12 :  Create DIR

        STEP 13 : After Start Recording - Create DIR Breaks the sequence, but starts new one
                  and it is successfully completed
        for 5 times :
            STEP 13a :  Create DIR
            Perform Write Types

        STEP 14 :  Create DIR
        Perform Write Types
        STEP 15 :   Start Recording
        Perform Write Types
        STEP 16 :  Update CI
        Perform Write Types
        """

        # Initialize the SD card
        self.__sdCmdObj.DoBasicInit()

        # Call LoadCmd20Variables Utility Script
        self.__cmd20variables = LoadCMD20_Variables.CMD20_UT01_LoadCMD20_Variables(self.vtfContainer).Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Break sequence between Create DIR and Start Recording.\n")
        self.__Counter = 0

        # This loop currently executes only once in Scripter
        while self.__Counter < 1:
            self.__cmd20variables['NotAllowedCommand'] = self.__Counter
            self.NotAllowComandTest()
            self.__Counter = self.__Counter + 1

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Break sequence after start recording.\n")
        self.__Counter = 0
        self.__BreakType = 1
        self.__cmd20variables["ExpectSequence"] = 1

        self.Sequence()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Break sequence by replacing valid CMD20 arg with reserved bits.\n")

        # Using Argument 0x2
        self.__dvtLib.SpeedClassControl(SpeedClassCommandDescription = 0x2)

        self.__cmd20variables["ExpectSequence"] = 0
        # Call Script Utility_CMD20_Write
        self.__WriteType = 1
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])
        self.__allowedCmds.Run(AllowedCommand = self.__cmd20variables["AllowedCommand"], Cmd20Variables = self.__cmd20variables)

        if self.__cmd20variables["AllowedCommand"] == 0:
            self.__WriteType = 12   # If AllowedCommand is 0, then WriteType would have been modified to 12 in CMD20_UT04_AllowedCommands.py file

        # Start Recording
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING, TimeOut = 1000)

        self.__cmd20variables["ExpectSequence"] = 1
        # GetSequence
        self.__getSequence.Run(self.__cmd20variables["ExpectSequence"])

        # Call Script Utility_CMD20_Write
        self.__WriteType = 2
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # UpdateCI
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)

        # Call Script Utility_CMD20_Write - Expect Write CI out of sequence
        self.__WriteType = 3
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # Call Script Utility_CMD20_Write - Expect Write FAT(FAT) Out ofsequence
        self.__WriteType = 4
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # Call Script Utility_CMD20_Write - Expect Write FAT (DIR) out of sequence
        self.__WriteType = 5
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # Call Script Utility_CMD20_Write - Expect Write FAT(BITMAP) out of sequence
        self.__WriteType = 6
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # Call Script Utility_CMD20_Write - Expect Write RU out of sequence
        self.__WriteType = 2
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        self.__cmd20variables["ExpectSequence"] = 1
        # CreateDIR
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

        # Call Script Utility_CMD20_Write
        self.__WriteType = 1
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])
        self.__allowedCmds.Run(AllowedCommand=None, Cmd20Variables = self.__cmd20variables)

        # CreateDIR, Use Manual Argument
        self.__dvtLib.SpeedClassControl(SpeedClassCommandDescription = 0x2)

        # Call Script Utility_CMD20_Write - Expect Write RU out of sequence
        self.__WriteType = 2
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # UpdateCI, Use Manual Argument
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)

        # Call Script Utility_CMD20_Write - Write CI expect out of sequence
        self.__WriteType = 3
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # Call Script Utility_CMD20_Write - Expect Write FAT(FAT) Out ofsequence
        self.__WriteType = 4
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # Call Script Utility_CMD20_Write - Expect Write FAT (DIR) out of sequence
        self.__WriteType = 5
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # Call Script Utility_CMD20_Write  - Expect Write FAT(BITMAP) out of sequence
        self.__WriteType = 6
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # Call Script Utility_CMD20_Write - Expect Write RU out of sequence
        self.__WriteType = 2
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        self.__cmd20variables["ExpectSequence"] = 1
        # CreateDIR
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

        # Call Script Utility_CMD20_Write
        self.__WriteType = 1
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])
        self.__allowedCmds.Run(AllowedCommand = self.__cmd20variables["AllowedCommand"], Cmd20Variables = self.__cmd20variables)

        # Start Recording
        self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING, TimeOut = 1000)

        # Call Script Utility_CMD20_Write - Write DIR
        self.__WriteType = 1
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # Call Script Utility_CMD20_Write  - Write RU
        self.__WriteType = 2
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # Use manual Argument
        self.__dvtLib.SpeedClassControl(SpeedClassControl = 0x2)

        self.__cmd20variables["ExpectSequence"] = 0
        # Call Script Utility_CMD20_Write
        self.__WriteType = 3
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # Call Script Utility_CMD20_Write
        self.__WriteType = 4
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # Call Script Utility_CMD20_Write
        self.__WriteType = 5
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # Call Script Utility_CMD20_Write
        self.__WriteType = 6
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        # Call Script Utility_CMD20_Write
        self.__WriteType = 2
        self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

        self.__cmd20variables["ExpectSequence"] = 1

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "After Start Recording - Create DIR Breaks the sequence, but starts new one and it is successfully completed")
        self.__Counter = 0

        for i in range(0, 5):
            # Create DIR
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

            # Call Script Utility_CMD20_Write
            self.__WriteType = 1
            self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])
            self.__allowedCmds.Run(AllowedCommand = self.__cmd20variables["AllowedCommand"], Cmd20Variables = self.__cmd20variables)

            # Start Recording
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING, TimeOut = 1000)

            self.__cmd20variables["ExpectSequence"] = 1
            # Get Sequence
            self.__getSequence.Run(self.__cmd20variables["ExpectSequence"])

            if self.__Counter > 0:
                # Call Script Utility_CMD20_Write
                self.__WriteType = 2
                self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            if self.__Counter > 1:
                # Update CI
                self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)

                # Call Script Utility_CMD20_Write
                self.__WriteType = 3
                self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            if self.__Counter > 2:
                # Call Script Utility_CMD20_Write
                self.__WriteType = 4
                self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

                # Call Script Utility_CMD20_Write
                self.__WriteType = 5
                self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

                # Call Script Utility_CMD20_Write
                self.__WriteType = 6
                self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            if self.__Counter > 3:
                # Call Script Utility_CMD20_Write
                self.__WriteType = 2
                self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            # Create DIR
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

            self.__cmd20variables["ExpectSequence"] = 1
            #call GetSequence
            self.__getSequence.Run(self.__cmd20variables["ExpectSequence"])

            # Call Script Utility_CMD20_Write
            self.__WriteType = 1
            self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])
            self.__allowedCmds.Run(AllowedCommand = self.__cmd20variables["AllowedCommand"], Cmd20Variables = self.__cmd20variables)

            # Start Recording
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING, TimeOut = 1000)

            self.__cmd20variables["ExpectSequence"] = 1
            # Get Sequence
            self.__getSequence.Run(self.__cmd20variables["ExpectSequence"])

            # Call Script Utility_CMD20_Write
            self.__WriteType = 2
            self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            # Update CI
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)
            # Call Script Utility_CMD20_Write
            self.__WriteType = 3
            self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            # Call Script Utility_CMD20_Write
            self.__WriteType = 4
            self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            # Call Script Utility_CMD20_Write
            self.__WriteType = 5
            self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            # Call Script Utility_CMD20_Write
            self.__WriteType = 6
            self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            # Call Script Utility_CMD20_Write
            self.__WriteType = 2
            self.__cmd20Write.Run(WriteType = self.__WriteType, cmd20variables = self.__cmd20variables, ExpectSequence = self.__cmd20variables["ExpectSequence"])

            self.__Counter += 1

        return 0
    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_CMD20_TC003_BreakSequenceTest(self):
        obj = CMD20_TC003_BreakSequenceTest(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
