"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : Utility_CMD20_Write
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : ACMD41_UT04_CMD20_Write.py
# DESCRIPTION                    :
# PRERQUISTE                     :
# STANDALONE EXECUTION           : No. It is an utility script.
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 30-May-2024
# UPDATED BY                     : Sushmitha P.S
# UPDATED DATE                   : 29-Jun-2024
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
import ACMD41_UT02_CMD20_GetSequence as CMD20GetSequence

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
class ACMD41_UT04_CMD20_Write(customize_log):
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
        self.__GetSequence = CMD20GetSequence.ACMD41_UT02_CMD20_GetSequence(self.vtfContainer)


    # Testcase logic - Starts

    def Run(self, WriteType = 0, StartBlock = 0x0, BlockCount = 0x1, DataType = 1, usePreDefBlkCount = False,
            CiSequence = 0, ret = 0, RuSequence = 1, cmd20variables = None,ExpectSequence = 0):

        """
        Name : Run
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Utility Execution Started " + "-" * 20 + "\n")
        Random = random.randrange(0,2)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "The Random value is %d " %Random)

        U = self.__cardMaxLba
        if WriteType == 1:
            if Random == 0: # Multi Write
                self.__dvtLib.WriteWithFPGAPattern(StartLba =cmd20variables['DIRconstAddress'], blockCount = 0x1, SingleWrite = False, pattern=2)
                self.__dvtLib.ReadWithFPGAPattern(StartLba =cmd20variables['DIRconstAddress'], blockCount = 0x1, SingleRead = False, pattern=2)

            if Random == 1:  # Single Write
                self.__dvtLib.WriteWithFPGAPattern(StartLba = cmd20variables['FatRandomAddress'], blockCount = 0x1, SingleWrite = True, pattern=2)
                self.__dvtLib.ReadWithFPGAPattern(StartLba = cmd20variables['FatRandomAddress'], blockCount = 0x1, SingleRead = True, pattern=2)

        #Check WriteType condition = 2
        if WriteType == 2:
            AU = cmd20variables['AU']
            self.__dvtLib.WriteWithFPGAPattern(StartLba =cmd20variables['RuStartBlock'], blockCount = cmd20variables['RU'], pattern=2)
            self.__dvtLib.ReadWithFPGAPattern(StartLba =cmd20variables['RuStartBlock'], blockCount = cmd20variables['RU'], pattern=2)
            self.__GetSequence.Run(ExpectSequence)

            if RuSequence == 1:
                cmd20variables['RuStartBlock'] = cmd20variables['RuStartBlock']  + cmd20variables['RU']

            if RuSequence == 0:
                if cmd20variables['RuStartBlock'] % AU == 0:
                    rand = random.randrange(0,((cmd20variables['NumOfAU']-1) * AU))
                    cmd20variables['RuStartBlock'] = rand + cmd20variables['Lba_of_first_AU']
                    cmd20variables['RUStartBlockRead'] = cmd20variables['RuStartBlock']
                else:
                    cmd20variables['RuStartBlock'] = cmd20variables['RuStartBlock']  + cmd20variables['RU']
            self.__GetSequence.Run(ExpectSequence)

        #Check WriteType condition = 3
        if WriteType == 3:
            if Random == 0: # Multiple Write/Read
                self.__dvtLib.WriteWithFPGAPattern(StartLba =cmd20variables['CiStartBlock'], blockCount = 0x1, pattern=4)
                self.__dvtLib.ReadWithFPGAPattern(StartLba =cmd20variables['CiStartBlock'], blockCount = 0x1, pattern=4)
                self.__GetSequence.Run(cmd20variables["ExpectSequence"])

            if Random == 1: # Single Write/Read
                self.__dvtLib.WriteWithFPGAPattern(StartLba = cmd20variables['CiStartBlock'], blockCount = 0x1, SingleWrite = True, pattern=4)
                self.__dvtLib.ReadWithFPGAPattern(StartLba = cmd20variables['CiStartBlock'], blockCount = 0x1, SingleRead = True, pattern=4)
                self.__GetSequence.Run( cmd20variables["ExpectSequence"])

            cmd20variables['CiStartBlock'] = cmd20variables['CiStartBlock'] + 1
            if cmd20variables['CiStartBlock'] > U  - 1:
                cmd20variables['CiStartBlock'] = cmd20variables['CiStartBlock'] - 1
            self.__GetSequence.Run( cmd20variables["ExpectSequence"])

        #Check WriteType condition = 4
        if WriteType == 4:

            self.__dvtLib.WriteWithFPGAPattern(StartLba =cmd20variables['FatRandomAddress'], blockCount = cmd20variables['FatUpdateFatSize'], pattern=2)
            self.__dvtLib.ReadWithFPGAPattern(StartLba =cmd20variables['FatRandomAddress'], blockCount = cmd20variables['FatUpdateFatSize'], pattern=2)

            cmd20variables['FatRandomAddress'] = cmd20variables['FatRandomAddress'] + cmd20variables['FatUpdateFatSize']
            self.__GetSequence.Run( cmd20variables["ExpectSequence"])

        # Check WriteType condition = 5
        if WriteType == 5:
            if Random == 0:
                self.__dvtLib.WriteWithFPGAPattern(StartLba =cmd20variables['FatRandomAddress'], blockCount = 0x1, pattern=2)
                self.__dvtLib.ReadWithFPGAPattern(StartLba =cmd20variables['FatRandomAddress'], blockCount = 0x1, pattern=2)
                self.__GetSequence.Run( cmd20variables["ExpectSequence"])

            if Random == 1:
                self.__dvtLib.WriteWithFPGAPattern(StartLba = cmd20variables['FatRandomAddress'], blockCount = 0x1, SingleWrite = True, pattern=2)
                self.__dvtLib.ReadWithFPGAPattern(StartLba = cmd20variables['FatRandomAddress'], blockCount = 0x1, SingleRead = True, pattern=2)
                self.__GetSequence.Run( cmd20variables["ExpectSequence"])
            cmd20variables['FatRandomAddress'] = cmd20variables['FatRandomAddress'] + 1

            # Call Script Utility_CMD20_GetSequence
            self.__GetSequence.Run(cmd20variables["ExpectSequence"])

        # Check WriteType condition = 6
        if WriteType == 6:
            self.__dvtLib.WriteWithFPGAPattern(StartLba =cmd20variables['BitmapRandomAddress'], blockCount = cmd20variables['FatUpdateBitmapSize'], pattern=2)
            self.__dvtLib.ReadWithFPGAPattern(StartLba =cmd20variables['BitmapRandomAddress'], blockCount = cmd20variables['FatUpdateBitmapSize'], pattern=2)
            cmd20variables['BitmapRandomAddress'] = cmd20variables['BitmapRandomAddress'] + cmd20variables['FatUpdateBitmapSize']
            self.__GetSequence.Run(cmd20variables["ExpectSequence"])

        # Check WriteType condition = 7
        if WriteType == 7 :
            rand = random.randrange(0,U - cmd20variables['Lba_of_first_AU'] - cmd20variables['RU'])
            RandomAddress = rand + cmd20variables['Lba_of_first_AU']
            self.__dvtLib.WriteWithFPGAPattern(StartLba =RandomAddress, blockCount = cmd20variables['RU'], pattern=2)
            self.__dvtLib.ReadWithFPGAPattern(StartLba =RandomAddress, blockCount = cmd20variables['RU'], pattern=2)

        #Check WriteType condition = 8
        if WriteType == 8:
            rand = random.randrange(0,cmd20variables['RU'] - 1)
            BlockCount = rand + 1

            self.__dvtLib.WriteWithFPGAPattern(StartLba =cmd20variables['RuStartBlock'], blockCount = BlockCount, pattern=2)
            self.__dvtLib.ReadWithFPGAPattern(StartLba =cmd20variables['RuStartBlock'], blockCount = BlockCount, pattern=2)

        #Check WriteType condition = 9
        if WriteType == 9:
            self.__dvtLib.WriteWithFPGAPattern(StartLba =cmd20variables['BitmapRandomAddress'], blockCount = 0x22, pattern=2)
            self.__dvtLib.ReadWithFPGAPattern(StartLba =cmd20variables['BitmapRandomAddress'], blockCount = 0x22, pattern=2)

        # Check WriteType condition = 10
        if WriteType == 10:
            self.__dvtLib.WriteWithFPGAPattern(StartLba =cmd20variables['FatRandomAddress'], blockCount = 0x33, pattern=2)
            self.__dvtLib.ReadWithFPGAPattern(StartLba =cmd20variables['FatRandomAddress'], blockCount = 0x33, pattern=2)

        # Check WriteType condition = 11
        if WriteType == 11:
            self.__dvtLib.WriteWithFPGAPattern(StartLba =cmd20variables['FatRandomAddress'], blockCount = 0x2, pattern=2)
            self.__dvtLib.ReadWithFPGAPattern(StartLba =cmd20variables['FatRandomAddress'], blockCount = 0x2, pattern=2)

        #Check WriteType condition = 12
        if WriteType == 12:
            self.__dvtLib.WriteWithFPGAPattern(StartLba =StartBlock, blockCount = BlockCount, pattern=DataType)
            self.__dvtLib.ReadWithFPGAPattern(StartLba =StartBlock, blockCount = BlockCount, pattern=DataType)

        # Check WriteType condition = 13
        if WriteType == 13:
            self.__dvtLib.WriteWithFPGAPattern(StartLba =cmd20variables['CiStartBlock'], blockCount = 0x2, pattern=4)
            self.__dvtLib.ReadWithFPGAPattern(StartLba =cmd20variables['CiStartBlock'], blockCount = 0x2, pattern=4)

        # Step 15: Check WriteType condition = 14
        if WriteType == 14:
            self.__dvtLib.WriteWithFPGAPattern(StartLba =cmd20variables['RuStartBlock'], blockCount = cmd20variables['RU'], pattern=4)
            self.__dvtLib.ReadWithFPGAPattern(StartLba =cmd20variables['RuStartBlock'], blockCount = cmd20variables['RU'], pattern=4)
            self.__GetSequence.Run(ExpectSequence).Run( cmd20variables["ExpectSequence"])

            cmd20variables['RuStartBlock'] = cmd20variables['RuStartBlock']  + cmd20variables['RU']
            if cmd20variables['RuStartBlock'] > U - cmd20variables['RU']:
                cmd20variables['RuStartBlock'] = cmd20variables['RuStartBlock'] - cmd20variables['AU']
            self.__GetSequence.Run(ExpectSequence).Run(cmd20variables["ExpectSequence"])


        # Check WriteType condition = 15
        if WriteType == 15:
            AU = cmd20variables['AU']
            self.__dvtLib.WriteWithFPGAPattern(StartLba =cmd20variables['CiStartBlock'], blockCount = 0x1, pattern=2)
            self.__dvtLib.ReadWithFPGAPattern(StartLba =cmd20variables['CiStartBlock'], blockCount = 0x1, pattern=2)
            self.__GetSequence.Run(cmd20variables["ExpectSequence"])

            if CiSequence == 1:
                cmd20variables['CiStartBlock'] = cmd20variables['CiStartBlock']  + 1
            if CiSequence == 0:
                if cmd20variables['CiStartBlock']% AU == 0:
                    rand = random.randrange(0, (cmd20variables['NumOfAU'] - 1))
                    cmd20variables['CiStartBlock'] = (rand * cmd20variables['AU']) + cmd20variables['Lba_of_first_AU']
                    cmd20variables['CiStartBlockRead'] = cmd20variables['CiStartBlock']
                else:
                    cmd20variables['CiStartBlock'] = cmd20variables['CiStartBlock']  + 1
            self.__GetSequence.Run( cmd20variables["ExpectSequence"])


        return 0

    #End of Run function
#End of CMD20Write

# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_ACMD41_UT04_CMD20_Write(self):
        obj = ACMD41_UT04_CMD20_Write(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends