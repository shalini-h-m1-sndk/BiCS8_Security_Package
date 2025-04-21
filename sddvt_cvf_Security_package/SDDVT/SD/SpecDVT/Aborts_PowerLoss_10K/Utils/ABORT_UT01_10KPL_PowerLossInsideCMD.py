"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : ABORT_TC001_10K_PowerLossTest.st3
# SCRIPTER SCRIPT                : ABORT_UT01_10KPL_PowerLossInsideCMD.st3
# CVF CALL ALL SCRIPT            : ABORT_TC001_10K_PowerLossTest.py
# CVF SCRIPT                     : ABORT_UT01_10KPL_PowerLossInsideCMD.py
# DESCRIPTION                    : The purpose of this utility script is to:
                                       -- Perform power loss inside write CMD
                                       -- The power loss phase (before / during data or busy clk) and bit are randomized
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 29/06/2022
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
import time
from inspect import currentframe, getframeinfo

# Global Variables


class ABORT_UT01_10KPL_PowerLossInsideCMD(customize_log):
    """
    class for Defining Write operation that can be used by
    Main scripts
    """
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
        # self.__ErrorManager = self.vtfContainer.device_session.GetErrorManager()

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

        ###### Customize Log ######
        self.fn = os.path.basename(getframeinfo(currentframe()).filename)
        customize_log.__init__(self, self.__TF)

        ##### Testcase Specific Variables #####


    def Run(self, ABORT_global_vars):

        # Variable Declaration
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Initialize the variables")

        currentInsideCMDPLPhase = random.randrange(0, 4)    # [currentInsideCMDPLPhase - on which phase inside CMD the PL will occur] { 0-Before Data, 1-During Data, 2-Busy CLK 3-Busy Time Out }

        # Perform Write Operation in Stop Trans mode based on currentInsideCMDPLPhase value.
        if (currentInsideCMDPLPhase == 0):  # [ If the random PL phase is 'Before Data' ]
            currentPLBit = ABORT_global_vars['beforeDataMinBit'] + random.randrange(0, (ABORT_global_vars['beforeDataMaxBit'] - ABORT_global_vars['beforeDataMinBit'] + 1))

            # Multiple write on PowerLoss
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple write with power loss called")

            # PySReadWriteParams
            RWParams = sdcmdWrap.PySReadWriteParams()
            RWParams.cardSlot = 1
            RWParams.dataAddress = ABORT_global_vars["currentAbortStartAddress"]
            # Workaround: When the countBlk/actualBlk is 0, Scripter_Directive/CTF_API sends 1 but not CVF. So, added work around.
            RWParams.countBlk = 0x1
            RWParams.actualBlk = 0x1
            RWParams.blockLen = 0x200   # 512

            # PySPerfReadWriteParams
            PRWParams = sdcmdWrap.PySPerfReadWriteParams()
            PRWParams.p = ABORT_global_vars["currentAbortDataType"]

            # PySEnhancedCmdData
            EnhcdCmdData = sdcmdWrap.PySEnhancedCmdData()
            EnhcdCmdData.CmdInvokingFormatSecondCmd = sdcmdWrap.ECmdInvokingFormat.NRC   # Enum value is 1
            EnhcdCmdData.AbortNRCVal = currentPLBit
            EnhcdCmdData.AbortBitPosInBlock = 0x0
            EnhcdCmdData.AbortBusy = 0x0
            EnhcdCmdData.AbortIdle = 0x0
            EnhcdCmdData.bCreatePowerCycle = True

            EnhcdCmdData.CmdSequenceSize = sdcmdWrap.ECmdSequenceSize.TWO_CMD_SEQ
            SecondCmd = sdcmdWrap.PySCmdInfo()
            SecondCmd.command = sdcmdWrap._CARD_COMMAND_.POWER_LOSS   # 255
            SecondCmd.res = sdcmdWrap.SD_RESPONSE_TYPE.NO_RESPONSE
            EnhcdCmdData.pSecondCmd = SecondCmd

            EnhcdCmdData.EnancedOpTimeUnits = sdcmdWrap.EEnancedOpTimeUnits.MILI_SECOND
            EnhcdCmdData.pThirdCmdParams = None

            try:
                sdcmdWrap.EnhancedWriteMultiBlock(PyRWParams = RWParams, cmd = sdcmdWrap._CARD_COMMAND_._WRITE_MULTIPLE_BLOCK,
                                                  UsePatternGen = True, PyPrefRWParams = PRWParams,
                                                  PyEnhcdCmdData = EnhcdCmdData, buf = None)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                raise ValidationError.TestFailError(self.fn, "Multiple write with PowerLoss failed. Exception is - %s" % exc.GetFailureDescription())

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple write with PowerLoss completed")

        if (currentInsideCMDPLPhase == 1):  # If the random PL phase is 'During Data'
            currentPLBit = ABORT_global_vars['duringDataMinBit'] + random.randrange(0, (ABORT_global_vars['duringDataMaxBit'] - ABORT_global_vars['duringDataMinBit'] + 1))

            # Multiple write on PowerLoss
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple write with power loss called")

            # PySReadWriteParams
            RWParams = sdcmdWrap.PySReadWriteParams()
            RWParams.cardSlot = 1
            RWParams.dataAddress = ABORT_global_vars["currentAbortStartAddress"]
            RWParams.countBlk = ABORT_global_vars["currentAbortSize"]
            RWParams.actualBlk = ABORT_global_vars["currentAbortSize"]
            RWParams.blockLen = 0x200   # 512

            # PySPerfReadWriteParams
            PRWParams = sdcmdWrap.PySPerfReadWriteParams()
            PRWParams.p = ABORT_global_vars["currentAbortDataType"]

            # PySEnhancedCmdData
            EnhcdCmdData = sdcmdWrap.PySEnhancedCmdData()
            EnhcdCmdData.CmdInvokingFormatSecondCmd = sdcmdWrap.ECmdInvokingFormat.BIT_EXACT_POSITION    # Enum value is 2
            EnhcdCmdData.AbortNRCVal = 0x0
            EnhcdCmdData.AbortBitPosInBlock = currentPLBit
            EnhcdCmdData.AbortBusy = 0x0
            EnhcdCmdData.AbortIdle = 0x0
            EnhcdCmdData.bCreatePowerCycle = True

            EnhcdCmdData.CmdSequenceSize = sdcmdWrap.ECmdSequenceSize.TWO_CMD_SEQ
            SecondCmd = sdcmdWrap.PySCmdInfo()
            SecondCmd.command = sdcmdWrap._CARD_COMMAND_.POWER_LOSS   # 255
            SecondCmd.res = sdcmdWrap.SD_RESPONSE_TYPE.NO_RESPONSE
            EnhcdCmdData.pSecondCmd = SecondCmd

            EnhcdCmdData.EnancedOpTimeUnits = sdcmdWrap.EEnancedOpTimeUnits.MILI_SECOND
            EnhcdCmdData.pThirdCmdParams = None

            try:
                sdcmdWrap.EnhancedWriteMultiBlock(PyRWParams = RWParams, cmd = sdcmdWrap._CARD_COMMAND_._WRITE_MULTIPLE_BLOCK,
                                                  UsePatternGen = True, PyPrefRWParams = PRWParams,
                                                  PyEnhcdCmdData = EnhcdCmdData, buf = None)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                raise ValidationError.TestFailError(self.fn, "Multiple write with PowerLoss failed. Exception is - %s" % exc.GetFailureDescription())

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple write with PowerLoss completed")

        if (currentInsideCMDPLPhase == 2):  # If the random PL phase is 'Busy CLK'
            currentPLBit = ABORT_global_vars['busyCLKMinBit'] + random.randrange(0, (ABORT_global_vars['busyCLKMaxBit'] - ABORT_global_vars['busyCLKMinBit'] + 1))

            # Multiple write on PowerLoss
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple write with power loss called")

            # PySReadWriteParams
            RWParams = sdcmdWrap.PySReadWriteParams()
            RWParams.cardSlot = 1
            RWParams.dataAddress = ABORT_global_vars["currentAbortStartAddress"]
            RWParams.countBlk = ABORT_global_vars["currentAbortSize"]
            RWParams.actualBlk = ABORT_global_vars["currentAbortSize"]
            RWParams.blockLen = 0x200   # 512

            # PySPerfReadWriteParams
            PRWParams = sdcmdWrap.PySPerfReadWriteParams()
            PRWParams.p = ABORT_global_vars["currentAbortDataType"]

            # PySEnhancedCmdData
            EnhcdCmdData = sdcmdWrap.PySEnhancedCmdData()
            EnhcdCmdData.CmdInvokingFormatSecondCmd = sdcmdWrap.ECmdInvokingFormat.BUSY_CLOCK   # Enum value is 3
            EnhcdCmdData.AbortNRCVal = 0x0
            EnhcdCmdData.AbortBitPosInBlock = 0x0
            EnhcdCmdData.AbortBusy = currentPLBit
            EnhcdCmdData.AbortIdle = 0x0
            EnhcdCmdData.bCreatePowerCycle = True

            EnhcdCmdData.CmdSequenceSize = sdcmdWrap.ECmdSequenceSize.TWO_CMD_SEQ
            SecondCmd = sdcmdWrap.PySCmdInfo()
            SecondCmd.command = sdcmdWrap._CARD_COMMAND_.POWER_LOSS   # 255
            SecondCmd.res = sdcmdWrap.SD_RESPONSE_TYPE.NO_RESPONSE
            EnhcdCmdData.pSecondCmd = SecondCmd

            EnhcdCmdData.EnancedOpTimeUnits = sdcmdWrap.EEnancedOpTimeUnits.MILI_SECOND
            EnhcdCmdData.pThirdCmdParams = None

            try:
                sdcmdWrap.EnhancedWriteMultiBlock(PyRWParams = RWParams, cmd = sdcmdWrap._CARD_COMMAND_._WRITE_MULTIPLE_BLOCK,
                                                  UsePatternGen = True, PyPrefRWParams = PRWParams,
                                                  PyEnhcdCmdData = EnhcdCmdData, buf = None)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                raise ValidationError.TestFailError(self.fn, "Multiple write with PowerLoss failed. Exception is - %s" % exc.GetFailureDescription())

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple write with PowerLoss completed")

        if (currentInsideCMDPLPhase == 3):  # If the random PL phase is 'Busy Time Out'
            currentBusyTO = ABORT_global_vars['busyTOMin'] + (random.randrange(0, (ABORT_global_vars['busyTOMax'] - ABORT_global_vars['busyTOMin'] + 1)))

            # Multiple write on PowerLoss
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple write with power loss called")

            # PySReadWriteParams
            RWParams = sdcmdWrap.PySReadWriteParams()
            RWParams.cardSlot = 1
            RWParams.dataAddress = ABORT_global_vars["currentAbortStartAddress"]
            RWParams.countBlk = ABORT_global_vars["currentAbortSize"]
            RWParams.actualBlk = ABORT_global_vars["currentAbortSize"]
            RWParams.blockLen = 0x200   # 512

            # PySPerfReadWriteParams
            PRWParams = sdcmdWrap.PySPerfReadWriteParams()
            PRWParams.p = ABORT_global_vars["currentAbortDataType"]

            # PySEnhancedCmdData
            EnhcdCmdData = sdcmdWrap.PySEnhancedCmdData()
            EnhcdCmdData.CmdInvokingFormatSecondCmd = sdcmdWrap.ECmdInvokingFormat.BUSY_TIME_OUT    # Enum value is 7
            EnhcdCmdData.AbortNRCVal = 0x0
            EnhcdCmdData.AbortBitPosInBlock = 0x0
            EnhcdCmdData.AbortBusy = currentBusyTO
            EnhcdCmdData.AbortIdle = 0x0
            EnhcdCmdData.bCreatePowerCycle = True

            EnhcdCmdData.CmdSequenceSize = sdcmdWrap.ECmdSequenceSize.TWO_CMD_SEQ
            SecondCmd = sdcmdWrap.PySCmdInfo()
            SecondCmd.command = sdcmdWrap._CARD_COMMAND_.POWER_LOSS   # 255
            SecondCmd.res = sdcmdWrap.SD_RESPONSE_TYPE.NO_RESPONSE
            EnhcdCmdData.pSecondCmd = SecondCmd

            EnhcdCmdData.EnancedOpTimeUnits = ABORT_global_vars["busyTOTimeUnits"]
            EnhcdCmdData.pThirdCmdParams = None

            try:
                sdcmdWrap.EnhancedWriteMultiBlock(PyRWParams = RWParams, cmd = sdcmdWrap._CARD_COMMAND_._WRITE_MULTIPLE_BLOCK,
                                                  UsePatternGen = True, PyPrefRWParams = PRWParams,
                                                  PyEnhcdCmdData = EnhcdCmdData, buf = None)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                raise ValidationError.TestFailError(self.fn, "Multiple write with PowerLoss failed. Exception is - %s" % exc.GetFailureDescription())

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple write with PowerLoss completed")

        return 0

# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_ABORT_UT01_10KPL_PowerLossInsideCMD(self):
        obj = ABORT_UT01_10KPL_PowerLossInsideCMD(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
