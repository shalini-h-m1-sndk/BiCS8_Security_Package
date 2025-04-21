"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                :
# CVF CALL ALL SCRIPT            : CMD23_CA01_SDMode.xml
# CVF SCRIPT                     : CMD23_TC008_CMD20RandomTestUsingCMD23.py
# DESCRIPTION                    :
# PRERQUISTE                     : [CMD23_UT01_AllowedCommands,CMD23_UT03_CMD20_GetSequence,CMD23_UT05_CMD20Write
                                    CMD23_UT07_LoadCMD20_Variables, CMD23_UT08_LoadCMD23_Variables]
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=CMD23_TC008_CMD20RandomTestUsingCMD23 --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Sushmitha P.S
# REVIEWED BY                    : Sivagurunathan
# DATE                           : 28-Jun-2024
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

# Dependent Utilities
import CMD23_UT05_CMD20Write as CMD20Write
import CMD23_UT03_CMD20_GetSequence as CMD20GetSequence
import CMD23_UT07_LoadCMD20_Variables as LoadCMD20Variables
import CMD23_UT08_LoadCMD23_Variables as LoadCMD23Variables
import CMD23_UT01_AllowedCommands as AllowedCommands

# Global Variables
# Testcase Class - Begins
class CMD23_TC008_CMD20RandomTestUsingCMD23(TestCase.TestCase, customize_log):
    # Act as a Constructor
    def setUp(self):
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
        self.__LoadCMD20Variables = LoadCMD20Variables.CMD23_UT07_LoadCMD20_Variables(self.vtfContainer)
        self.__LoadCMD23Variables =  LoadCMD23Variables.CMD23_UT08_LoadCMD23_Variables(self.vtfContainer)
        self.__GetSequence = CMD20GetSequence.CMD23_UT03_CMD20_GetSequence(self.vtfContainer)
        self.__CMD20Write = CMD20Write.CMD23_UT05_CMD20Write(self.vtfContainer)
        self.__AllowedCMDs = AllowedCommands.CMD23_UT01_AllowedCommands(self.vtfContainer)

    # Testcase logic - Starts

    def Run(self):
        """
        Name : Run
        #"""
        # Call globalInit Card
        globalProjectValues = self.__sdCmdObj.DoBasicInit()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Execution Started " + "-" * 20 + "\n")

        # CALL Utility_LoadCMD23_Variables script
        cmd23Variables = self.__LoadCMD23Variables.Run( ret = 1)

        #Call Utility Utility_LoadCMD20_Variables
        cmd20Variables = self.__LoadCMD20Variables.Run()

        # Variable Declaration
        RuSequence = 1

        LoopCounter = 0
        # Set Label Loop
        while LoopCounter < 50:

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*" * 10 + "Loop count %d is started" %LoopCounter +  "*" * 10)
            # Create DIR
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_DIR, TimeOut = 10)

            # Call GetSequence Utility
            ExpectSequence = 1
            self.__GetSequence.Run(ExpectSequence=ExpectSequence)

            # Call Utility_CMD20_Write, With WriteType = 1
            self.__CMD20Write.Run(WriteType=1,cmd20variables=cmd20Variables,ExpectSequence=ExpectSequence)

            # Call Utility_AllowedCommands Script
            self.__AllowedCMDs.Run(AllowedCommand=0, Cmd20Variables=cmd20Variables)

            # Start Recording
            self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.START_RECORDING, TimeOut = 1000)

            # Call GetSequence Utility
            self.__GetSequence.Run(ExpectSequence=ExpectSequence)

            # Initialize the values as these values are defined in : CMD23_UT07_LoadCMD20_Variables.py
            RuStartBlock = cmd20Variables['Lba_of_first_AU']

            #AU = cmd20Variables['AU']
            RU = cmd20Variables['RU']
            #NumOfAU = cmd20Variables['NumOfAU']
            Lba_of_first_AU = cmd20Variables['Lba_of_first_AU']
            CiStartBlock = cmd20Variables['CiStartBlock']
            FatRandomAddress = cmd20Variables['FatRandomAddress']
            FatUpdateFatSize = cmd20Variables['FatUpdateFatSize']
            BitmapRandomAddress = cmd20Variables['BitmapRandomAddress']
            FatUpdateBitmapSize = cmd20Variables['FatUpdateBitmapSize']

            U = self.__cardMaxLba
            # Set Label Loop2
            LoopCounter2 =0
            LoopCounterMax = random.randrange(0,512)
            while LoopCounter2 < LoopCounterMax:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*" * 10 + "Loop count2 %d is started" %LoopCounter2 +  "*" * 10)
                Random = random.randrange(0, 5)
                if Random == 0:
                    BlockCount = RU
                    StartLBA = RuStartBlock
                    #Incremental
                    DataType = sdcmdWrap.Pattern.INCREMENTAL

                    # Do Multiple Write and Read from RUStartBlock to RU blocks
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple block Write with StartLba: 0x%X, BlockCount: 0x%X, Pattern:0x%X\n"%(StartLBA,BlockCount,DataType))
                    self.__dvtLib.WriteWithFPGAPattern(StartLba =StartLBA, blockCount = BlockCount, SingleWrite =  False, pattern=DataType, usePreDefBlkCount = True)

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple block Read with StartLba: 0x%X, BlockCount: 0x%X, Pattern:0x%X\n"%(StartLBA,BlockCount,DataType))
                    self.__dvtLib.ReadWithFPGAPattern(StartLba =StartLBA, blockCount = BlockCount, SingleRead =  False, pattern=DataType, usePreDefBlkCount = True)

                    # Update RUStartBlock variable
                    RuStartBlock = RuStartBlock + RU

                if Random == 1:
                    # Update CI
                    self.__dvtLib.SpeedClassControl(SpeedClassControl = sdcmdWrap.SPEED_CLASS_ENUM.UPDATE_CI, TimeOut = 10)
                    BlockCount = 1
                    StartLBA = CiStartBlock
                    #Constant
                    DataType = sdcmdWrap.Pattern.CONST

                    # Do Multiple Write and Read for CiStartBlock
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple block Write with StartLba: 0x%X, BlockCount: 0x%X, Pattern:0x%X\n"%(StartLBA,BlockCount,DataType))
                    self.__dvtLib.WriteWithFPGAPattern(StartLba =StartLBA, blockCount = BlockCount, SingleWrite =  False, pattern=DataType, usePreDefBlkCount = True)

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple block Read with StartLba: 0x%X, BlockCount: 0x%X, Pattern:0x%X\n"%(StartLBA,BlockCount,DataType))
                    self.__dvtLib.ReadWithFPGAPattern(StartLba =StartLBA, blockCount = BlockCount, SingleRead =  False, pattern=DataType, usePreDefBlkCount = True)

                    # Update CiStartBlock variable
                    CiStartBlock = CiStartBlock + 1

                    if CiStartBlock > U - 1:
                        CiStartBlock = CiStartBlock - 1

                if Random == 2:
                    BlockCount = FatUpdateFatSize
                    StartLBA = FatRandomAddress
                    #Incremental
                    DataType = sdcmdWrap.Pattern.INCREMENTAL

                    # Do Multiple Write and Read for FatRandomAddress to FatUpdateFatSize
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple block Write with StartLba: 0x%X, BlockCount: 0x%X, Pattern:0x%X\n"%(StartLBA,BlockCount,DataType))
                    self.__dvtLib.WriteWithFPGAPattern(StartLba =StartLBA, blockCount = BlockCount, SingleWrite =  False, pattern=DataType, usePreDefBlkCount = True)

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple block Read with StartLba: 0x%X, BlockCount: 0x%X, Pattern:0x%X\n"%(StartLBA,BlockCount,DataType))
                    self.__dvtLib.ReadWithFPGAPattern(StartLba =StartLBA, blockCount = BlockCount, SingleRead =  False, pattern=DataType, usePreDefBlkCount = True)

                    # Update FatRandomAddress variable
                    FatRandomAddress = FatRandomAddress + FatUpdateFatSize

                if Random == 3:
                    BlockCount = FatUpdateBitmapSize
                    StartLBA = BitmapRandomAddress
                    #Incremental
                    DataType =  sdcmdWrap.Pattern.INCREMENTAL

                    # Do Multiple Write and Read for BitmapRandomAddress to FatUpdateBitmapSize
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple block Write with StartLba: 0x%X, BlockCount: 0x%X, Pattern:0x%X\n"%(StartLBA,BlockCount,DataType))
                    self.__dvtLib.WriteWithFPGAPattern(StartLba =StartLBA, blockCount = BlockCount, SingleWrite =  False, pattern=DataType, usePreDefBlkCount = True)

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple block Read with StartLba: 0x%X, BlockCount: 0x%X, Pattern:0x%X\n"%(StartLBA,BlockCount,DataType))
                    self.__dvtLib.ReadWithFPGAPattern(StartLba =StartLBA, blockCount = BlockCount, SingleRead =  False, pattern=DataType, usePreDefBlkCount = True)

                    # Update BitmapRandomAddress variable
                    BitmapRandomAddress = BitmapRandomAddress + FatUpdateBitmapSize

                if Random == 4:
                    BlockCount = 1
                    StartLBA = FatRandomAddress
                    #Incremental
                    DataType =  sdcmdWrap.Pattern.INCREMENTAL

                    # Do Multiple Write and Read for FatRandomAddress to 0x1 Blocks
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple block Write with StartLba: 0x%X, BlockCount: 0x%X, Pattern:0x%X\n"%(StartLBA,BlockCount,DataType))
                    self.__dvtLib.WriteWithFPGAPattern(StartLba =StartLBA, blockCount = BlockCount, SingleWrite =  False, pattern=DataType, usePreDefBlkCount = True)

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple block Read with StartLba: 0x%X, BlockCount: 0x%X, Pattern:0x%X\n"%(StartLBA,BlockCount,DataType))
                    self.__dvtLib.ReadWithFPGAPattern(StartLba =StartLBA, blockCount = BlockCount, SingleRead =  False, pattern=DataType, usePreDefBlkCount = True)

                    # Update FatRandomAddress variable
                    FatRandomAddress = FatRandomAddress + 1

                # Get in SpeedClass mode
                self.__dvtLib.GetInSpeedClassMode()

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*" * 10 + "Loop count2 %d is Completed" %LoopCounter2 +  "*" * 10)
                LoopCounter2 = LoopCounter2 + 1
                #End of Loop2

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*" * 10 + "Loop count %d is Completed" %LoopCounter +  "*" * 10)
            LoopCounter = LoopCounter + 1
            #End of Loop1

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + " Execution Completed " + "-" * 20 + "\n")
        return 0
    #End of Run function
#End of CMD23_CMD20RandomTestUsingCMD23


    # Testcase logic - Ends

    # CVF Hook Function: [Testcase Should start with "test_"]
    def test_CMD23_TC008_CMD20RandomTestUsingCMD23(self):  # [Same in xml tag: <Test name="test_CMD23_TC008_CMD20RandomTestUsingCMD23">]

        # Calling Testcase logic
        self.Run()

# Testcase Class - Ends