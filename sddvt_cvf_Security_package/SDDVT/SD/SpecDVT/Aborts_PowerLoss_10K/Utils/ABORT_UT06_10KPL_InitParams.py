"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : ABORT_TC001_10K_PowerLossTest.st3
# SCRIPTER SCRIPT                : ABORT_UT06_10KPL_InitParams.st3
# CVF CALL ALL SCRIPT            : ABORT_TC001_10K_PowerLossTest.py
# CVF SCRIPT                     : ABORT_UT06_10KPL_InitParams.py
# DESCRIPTION                    : The purpose of this utility script is to Define the common parameters for the specific scripts package.
# PRERQUISTE                     : [ABORT_UT09_10KPL_PartitionAccess.py, ABORT_UT03_10KPL_GetChunkSizeAndAlgorithm.py]
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
import SDDVT.SD.SpecDVT.Aborts_PowerLoss_10K.Utils.ABORT_UT09_10KPL_PartitionAccess as partitionAccessUtil
import SDDVT.SD.SpecDVT.Aborts_PowerLoss_10K.Utils.ABORT_UT03_10KPL_GetChunkSizeAndAlgorithm as getChunkSizeAndAlgorithmUtil

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


class ABORT_UT06_10KPL_InitParams(customize_log):
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
        #self.__partitionAccessUtil = partitionAccessUtil.ABORT_UT09_10KPL_PartitionAccess(self.vtfContainer)
        self.__getChunkSizeAndAlgorithmUtil = getChunkSizeAndAlgorithmUtil.ABORT_UT03_10KPL_GetChunkSizeAndAlgorithm(self.vtfContainer)


    def Run(self, ret = 0):
        # call Script DoBasicInit
        globalProjectConfVar = self.__sdCmdObj.DoBasicInit()

        initParamValues = {}
        globalPowerUp = globalProjectConfVar['globalPowerUp']
        initParamValues['globalPowerUp'] = globalPowerUp

        #Call script ABORT_UT03_10KPL_GetChunkSizeAndAlgorithm
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Get the chunk size and algorithm")
        TC_Size, TC_Algorithm, numofTCs = self.__getChunkSizeAndAlgorithmUtil.Run(1)    # Here no use of calling this utility

        # variable Declaration
        initParamValues['numOfPerformedPLs'] = 0
        initParamValues['numOfPLsLeft'] = 10000

        # Check for Protocol mode
        # Not handled eMMC. This package is only for SD.
        # if globalProjectConfVar['globalProtocolMode'] != 'SD':
        #     initParamValues['partitionID'] = 0
        #     #Call Script ABORT_UT09_10KPL_PartitionAccess.py
        #     partitionSize = self.__partitionAccessUtil.Run(initParamValues['partitionID'])

        # variable Declaration based on globalFlashEnum
        #
        initParamValues['currentPartSize'] = self.__cardMaxLba
        globalFlashEnum = self.__config.get('globalFlashEnum')
        if globalFlashEnum == 'eX3memory':
            initParamValues['Area1_Size'] = 4
            initParamValues['Area2_Size'] = 4

        if globalFlashEnum == 'X2memory':
            initParamValues['Area1_Size'] = 16
            initParamValues['Area2_Size'] = 16

        if globalProjectConfVar['globalProtocolMode'] == 'SD':
            initParamValues['Area1_Size'] = 4
            initParamValues['Area2_Size'] = 4

        # Test Area 1 Verification
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "== == ==   Test Area 1 Verification   == ====")
        if (globalProjectConfVar['globalProtocolMode'] == 'SD'):
            initParamValues['testArea1VerMode'] = 4
        else:
            initParamValues['testArea1VerMode'] = 3

        # Test Area 2 Verification
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "== == ==   Test Area 2 Verification   == ====")
        if (globalProjectConfVar['globalProtocolMode'] == 'SD'):
            initParamValues['testArea2VerMode'] = 4
        else:
            initParamValues['testArea2VerMode'] = 3

        # General Power Loss definitions
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "== == ==    General Power Loss definitions   == ====")
        #  variable Declaration
        initParamValues['powerLossMode'] = 1
        initParamValues['betweenCMDPLWeight'] = 2
        initParamValues['insideCMDPLWeight'] = 10 - initParamValues['betweenCMDPLWeight']

        # Abort timings limits
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "== == ==    Abort timings limits   == == ==")
        initParamValues['beforeDataMinBit'] = 7
        initParamValues['beforeDataMaxBit'] = 1000000
        initParamValues['duringDataMinBit'] = 20
        initParamValues['duringDataMaxBit'] = 4130
        initParamValues['busyCLKMinBit'] = 1
        initParamValues['busyCLKMaxBit'] = 1000000
        initParamValues['busyTOTimeUnits'] = 3
        initParamValues['busyTOMin'] = 1
        initParamValues['busyTOMax'] = 2500
        initParamValues['delayBetweenCMDPL'] = 5
        initParamValues['delayBeforePowerOn'] = 10000

        # Debug Mode
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "== == ==    Debug Mode   == ====")
        initParamValues['verifyWritesFlag'] = 1

        if ret:
            return initParamValues, globalProjectConfVar, TC_Size, TC_Algorithm, numofTCs
        for key, value in initParamValues:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PRE Defined initParamValues :")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s : %d" % (key, value))

        return 0


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_ABORT_UT06_10KPL_InitParams(self):
        obj = ABORT_UT06_10KPL_InitParams(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
