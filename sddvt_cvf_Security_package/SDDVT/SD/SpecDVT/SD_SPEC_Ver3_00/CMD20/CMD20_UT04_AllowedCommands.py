"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : CMD20_CA01_SDMode.st3
# SCRIPTER SCRIPT                : CMD20_UT04_AllowedCommands.st3
# CVF CALL ALL SCRIPT            : CMD20_CA01_SDMode.py
# CVF SCRIPT                     : CMD20_UT04_AllowedCommands.py
# DESCRIPTION                    : The purpose of this test is to assure that CMD20 with reserved bits should not break the sequence
# PRERQUISTE                     : CMD20_UT01_LoadCMD20_Variables.py, CMD20_UT03_Write.py, CMD20_UT09_CMD20_ReadVerify.py
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
import CMD20_UT01_LoadCMD20_Variables as LoadCMD20Variables
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
class CMD20_UT04_AllowedCommands(customize_log):
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
        self.__cmd20Variables = LoadCMD20Variables.CMD20_UT01_LoadCMD20_Variables(self.vtfContainer)

    # Testcase Utility Logic - Starts
    def Run(self, AllowedCommand = 0, Cmd20Variables = None):
        """
        Name : Run

        AllowedCommand = 0:
            STEP 1 : # Call Utility_CMD20_Write
            STEP 2 : # Call Utility_CMD20_ReadVerify
        AllowedCommand = 1:
            STEP 3 : # Do Single Write from Lba_of_first_AU to 0x100
            STEP 4 : # Do Single Read from Lba_of_first_AU to 0x100
        AllowedCommand = 2:
            STEP 5 : # Call Utility_CMD20_ReadVerify
            STEP 6 : # Do Single Write from Lba_of_first_AU to 0x100
        AllowedCommand = 2:
            STEP 7 : Call Utility_CMD20_Write
            STEP 8 : Call Utility_CMD20_ReadVerify
            STEP 9 : Enable Temp.WP
            STEP 10 : Call Utility_CMD20_ReadVerify
            STEP 11 : Enable Not Temp.WP
            STEP 12 :  Call Utility_CMD20_Write, DataType 2
            STEP 13 :  Call Utility_CMD20_ReadVerify
        AllowedCommand = 4:
            STEP 14 :  GET CID
            STEP 15 :  GET CSD
            STEP 16 :  GET SCR
            STEP 17 :  GET SD STATUS
        AllowedCommand = 5:
            STEP 18 : CALL Script Utility_CMD20_Write
            STEP 19 : ACMD-22
            STEP 20 : Call Script Utility_CMD20_ReadVerify
        AllowedCommand == 6:
            STEP 21 : Check for globalCPRM == 'Secure', Yes
            STEP 22 : GET SD STATUS
            STEP 23 : Secure Write from startLba = 0 to Transfer Length = 0x10, Selector 0
            STEP 24 : Secure Read, from startLba = 0 to Transfer Length = 0x10, Selector 0
            STEP 25 : SECURE READ MKB, Selector 0
            STEP 26 : Secure Erase, from startLba = 0 to Transfer Length = 0x10, Selector 0
            STEP 27 : Secure Read from startLba = 0 to Transfer Length = 0x10, Selector 0
            STEP 28 : Check for globalCPRM == 'Secure', no
            STEP 29 :  Do Single Write from Lba_of_first_AU to 0x100
        """
        if (Cmd20Variables == None):
            Cmd20Variables = self.__cmd20Variables.Run()

        Lba_of_first_AU = Cmd20Variables['Lba_of_first_AU']

        if AllowedCommand == 0:

            # Call Utility_CMD20_Write
            WriteType = 12
            StartBlock = Lba_of_first_AU
            BlockCount = 0x100
            BlockSize = 0x200
            DataType = 1
            self.__cmd20Write.Run(WriteType, StartBlock, BlockCount, DataType, cmd20variables = Cmd20Variables)

            # Call Utility_CMD20_ReadVerify
            self.__cmd20ReadVerify.Run(StartBlock = StartBlock, BlockCount = BlockCount, DataType = DataType)

        if AllowedCommand == 1:

            BlockCount = 0x100

            # Single Write from Lba_of_first_AU to 0x100
            self.__dvtLib.WriteWithFPGAPattern(StartLba = Lba_of_first_AU, blockCount = BlockCount, SingleWrite = True, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

            # Single Read from Lba_of_first_AU to 0x100
            self.__dvtLib.ReadWithFPGAPattern(StartLba = Lba_of_first_AU, blockCount = BlockCount, SingleRead = True, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

        if AllowedCommand == 2:

            # Single Write from Lba_of_first_AU to 0x100
            self.__cmd20ReadVerify.Run(StartBlock = Lba_of_first_AU, BlockCount = 0x100, DataType = 0)

        if AllowedCommand == 3:

            # Call Utility_CMD20_Write
            self.__cmd20Write.Run(cmd20variables = Cmd20Variables)

            # Call Utility_CMD20_ReadVerify
            self.__cmd20ReadVerify.Run()

            # Enable Temp.WP
            self.__sdCmdObj.PutCardInWriteProtectMode(wpMode = "TMP_WRITE_PROTECT")

            # Do Multiple Write from Lba_of_first_AU
            BlockCount = 0x100

            try:
                self.__dvtLib.WriteWithFPGAPattern(StartLba = Lba_of_first_AU, blockCount = BlockCount, pattern = gvar.GlobalConstants.PATTERN_CONST)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, "CARD_ILLEGAL_CMD", "WriteWithFPGAPattern")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected 'CARD_ILLEGAL_CMD' error is not occured for WriteWithFPGAPattern")

            # Call Utility_CMD20_ReadVerify
            try:
                self.__cmd20ReadVerify.Run(StartBlock=Lba_of_first_AU, BlockCount=BlockCount, DataType=0, BlockSize=0x200)
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, "CARD_COMPARE_ERROR", "ReadWithFPGAPattern")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_COMPARE_ERROR is not occured")

            # Disable Temp.WP
            self.__sdCmdObj.RemoveCardFromWriteProtectMode(wpMode = "TMP_WRITE_PROTECT")

            # Call Utility_CMD20_Write, DataType 2
            self.__cmd20Write.Run(WriteType = 0, StartBlock = 0x0, BlockCount = 0x1, DataType = gvar.GlobalConstants.PATTERN_INCREMENTAL, cmd20variables = Cmd20Variables)

            # Call Utility_CMD20_ReadVerify
            self.__cmd20ReadVerify.Run(StartBlock=0x0, BlockCount = 0x1, DataType = gvar.GlobalConstants.PATTERN_INCREMENTAL)

        if AllowedCommand == 4:

            # GET CID
            self.__sdCmdObj.GetCID()

            # GET CSD
            self.__sdCmdObj.GetCSD()

            # GET SCR
            self.__sdCmdObj.GetSCRRegisterEntry()

            # GET SD STATUS
            self.__dvtLib.GetSDStatus()

        if AllowedCommand == 5:

            # CALL Script Utility_CMD20_Write
            self.__cmd20Write.Run(WriteType = 0, StartBlock = 0x0, BlockCount = 0x1, DataType = 1, cmd20variables = Cmd20Variables)

            # ACMD-22
            self.__sdCmdObj.ACmd22()

            # Call Script Utility_CMD20_ReadVerify
            self.__cmd20ReadVerify.Run(StartBlock = 0x4000, BlockCount = 0x100, DataType = 1)

        if AllowedCommand == 6:

            # Check for globalCPRM == 'Secure', Yes
            if self.__config.get('globalCPRM') == 'Secure':

                SRW_CARD_SLOT = 1

                # GET SD STATUS
                self.__dvtLib.GetSDStatus()

                # Secure Write from startLba = 0 to BlockCount = 0x10, Selector 0

                Selector = 0
                Signature = False
                BlockCount = 0x10
                StartBlock = 0
                authentication = True
                writeDataBuffer = ServiceWrap.Buffer.CreateBuffer(0x10)
                ExpectedDataBuffer = ServiceWrap.Buffer.CreateBuffer(0x10)
                self.__sdCmdObj.BufferFilling(writeDataBuffer, gvar.GlobalConstants.PATTERN_CONST)
                self.__sdCmdObj.SecureEnable(True)
                self.__sdCmdObj.SetSelector(0)

                self.__dvtLib.SecureWrite(cardslot = SRW_CARD_SLOT, StartBlock = StartBlock, BlockCount = BlockCount,
                                          writeDataBuffer = writeDataBuffer, selectorValue = Selector,
                                          enableSignature = Signature, authentication = authentication)

                # Secure Read, from startLba = 0 to Transfer Length = 0x10, Selector 0
                self.__dvtLib.SecureRead(cardslot = SRW_CARD_SLOT, StartBlock = StartBlock, BlockCount = BlockCount,
                                         ExpectedDataBuffer = ExpectedDataBuffer, selectorValue = Selector, authentication = authentication)

                # SECURE READ MKB, Selector 0
                BlockCount = 0x80
                StartBlock = 0x0

                try:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Secure Read MKB: 0x%X, BlockCount: 0x%X, Pattern:0x%X\n" % (StartBlock,BlockCount))
                    self.__dvtLib.ReadMKBFile(cardslot = SRW_CARD_SLOT, BlockCount = BlockCount, StartBlock = StartBlock, selector = 0)
                except ValidationError.CVFGenericExceptions as exc:
                    # TOBEDONE: Yet to find out the exact expected exception
                    self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Read MKB file:[%d] with startBlkAddr:0x%X ---- FAILED as Expected\n" % (Selector, StartBlock))
                else:
                    raise ValidationError.TestFailError(self.fn, "Read MKB file:[%d] with startBlkAddr:0x%X ---- Failed with unexpected error\n" % (Selector, StartBlock))

                # Secure Erase, from startLba = 0 to Transfer Length = 0x10, Selector 0
                StartBlock = 0x0
                BlockCount = 0x10
                self.__dvtLib.SecureErase(cardslot = SRW_CARD_SLOT, StartBlock = StartBlock, BlockCount = BlockCount,
                                          selectorValue = Selector, authentication = authentication)

                # Secure Read from startLba = 0 to Transfer Length = 0x10, Selector 0
                ExpectedDataBuffer.Fill(0x00)
                self.__dvtLib.SecureRead(cardslot = SRW_CARD_SLOT, StartBlock = StartBlock, BlockCount = BlockCount,
                                         ExpectedDataBuffer = ExpectedDataBuffer, selectorValue = Selector, authentication = authentication)

            else:
                # Single Write from Lba_of_first_AU to 0x100
                startLba = Lba_of_first_AU
                BlockCount = 0x100

                self.__dvtLib.ReadWithFPGAPattern(StartLba = Lba_of_first_AU, blockCount = BlockCount, SingleRead = True, pattern = gvar.GlobalConstants.PATTERN_INCREMENTAL)

        return 0
    # Testcase Utility Logic - Ends
# Testcase Utility Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_CMD20_UT04_AllowedCommands(self):
        obj = CMD20_UT04_AllowedCommands(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
