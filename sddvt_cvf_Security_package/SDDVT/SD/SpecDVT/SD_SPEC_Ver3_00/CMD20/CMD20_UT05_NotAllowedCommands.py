"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : CMD20_CA01_SDMode.st3
# SCRIPTER SCRIPT                : CMD20_UT05_NotAllowedCommands.st3
# CVF CALL ALL SCRIPT            : CMD20_CA01_SDMode.py
# CVF SCRIPT                     : CMD20_UT05_NotAllowedCommands.py
# DESCRIPTION                    : The purpose of this test is to assure that CMD20 with reserved bits should not break the sequence
# PRERQUISTE                     : CMD20_UT03_Write.py, CMD20_UT09_CMD20_ReadVerify.py
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
import CMD20_UT03_Write as CMD20Write
import CMD20_UT09_CMD20_ReadVerify as CMD20ReadVerify

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
class CMD20_UT05_NotAllowedCommands(customize_log):
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
        self.__cmd20Write = CMD20Write.CMD20_UT03_Write(self.vtfContainer)
        self.__cmd20ReadVerify = CMD20ReadVerify.CMD20_UT09_CMD20_ReadVerify(self.vtfContainer)


    # Testcase Utility Logic - Starts
    def Run(self, NotAllowedCommand = 2, CMD20Variables = None):
        """
        Name : Run
        """
        # This is supposed to call from another script (BreakSequenceTest) with Different values of 'Not Allowed Command' Variable.
        #  This script can not be run individually
        # Check Switch Command. The following test used for to check after certain Speed Class Control Sequence
        # After a specified Speed Class Control, We may have to call the
        # following commands from other scripts

        if NotAllowedCommand == 0:
            mode = gvar.CMD6.CHECK
            blocksize = 0x40
            arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
            supported = [0x0,0x0,0x0,0x0,0x0,0x0]
            switched = [0x0,0x0,0x0,0x0,0x0,0x0]
            compare = [0,0,0,0,0,0] #allows for which and all values to be compared
            responseCompare = False #compare true
            consumption = gvar.CMD6.CONSUMPTION_NONE
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call Card Switch command routine\n")
            self.__dvtLib.CardSwitchCommand(mode=mode, arginlist=arglist,blocksize = blocksize,
                                            responseCompare=responseCompare,
                                            compare=compare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)


        if NotAllowedCommand == 1:
            # Perform LOCK_UNLOCK Test. The following test used for to check Speed Class Control Sequence
            # After Certain Speed Class Control Sequence, We may have to call the
            # following commands from other scripts

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call Card Lock command\n")
            self.__dvtLib.Lock_unlock(setPassword = 1, lock = 1, oldPassword = "123456", blockLength = 0x8)

            StartLBA = 0x0
            BlockCount = 0x1

            try:
                self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_ALL_ZERO)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, "CARD_ILLEGAL_CMD", "WriteWithFPGAPattern")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected 'CARD_ILLEGAL_CMD' error is not occured for WriteWithFPGAPattern")

            try:
                self.__dvtLib.ReadWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_ALL_ZERO)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, "CARD_ILLEGAL_CMD", "ReadWithFPGAPattern")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected 'CARD_ILLEGAL_CMD' error is not occured for ReadWithFPGAPattern")

            self.__dvtLib.Lock_unlock(clearPassword = 1, oldPassword = "123456", blockLength = 0x8)

            WriteType = 8
            Lba_of_first_AU = CMD20Variables['Lba_of_first_AU']
            BlockCount = 0x100
            BlockSize = 0x200
            DataType = gvar.GlobalConstants.PATTERN_ALL_ONE
            self.__cmd20Write.Run(WriteType = WriteType, StartBlock = Lba_of_first_AU, BlockCount = BlockCount, DataType = DataType)
            self.__cmd20ReadVerify.Run(StartBlock = Lba_of_first_AU, BlockCount = BlockCount, DataType = DataType)

        # Perform Minimum Erase Test. The following test used for to check Speed Class Control Sequence
        # After Certain Speed Class Control Sequence, We may have to call the
        # following commands from other scripts

        if NotAllowedCommand == 2:
            StartLba = 0x0
            BlockCount = 0x10
            EndLba = self.__sdCmdObj.calculate_endLba(StartLba, BlockCount)
            self.__dvtLib.Erase(StartLba, EndLba)

        return 0
    # Testcase Utility Logic - Ends
# Testcase Utility Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_CMD20_UT05_NotAllowedCommands(self):
        obj = CMD20_UT05_NotAllowedCommands(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
