"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : ABORT_TC001_10K_PowerLossTest.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : ABORT_TC001_10K_PowerLossTest.py
# DESCRIPTION                    : The purpose of this test case is to test:
                                       - Valid behavior of card after 10K Power Loss Resets
                                       - Data integrity inside the aborted multiple write and outside of it
                                       - Two Dynamic areas (reads+writes) and one static area (write once and read verify sequentially)
                                       - Dynamic areas data is checked after each Power Loss Reset
                                       - Verified algorithms / size:
                                           Test case 0: Sequential write with 512-byte access size.
                                           Test case 1: Sequential write with 4KByte access size.
                                           Test case 2: Sequential write with 64KByte access size.
                                           Test case 3: Sequential write with 256KByte access size.
                                           Test case 4: Swap write with 512-byte access size.
                                           Test case 5: Swap write with 64kByte access size.
                                           Test case 6: Random write with 4kByte access size.
                                   NOTE: TOBEDONE : This script has dependency on CTF bug[5914 and 6016] (CTISW-5914:Information required about
                                           API VERIFY RELIABLE WRITE and CTISW-6016: CMD23 fails with Illegal Command Error]) and the CVF JIRA CVF-16550.
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 29/06/2022
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
    from builtins import str
    from builtins import *
from past.utils import old_div

# SDDVT - Dependent TestCases
from Utils import ABORT_UT01_10KPL_PowerLossInsideCMD as powerLossInsidecmdUtil
from Utils import ABORT_UT03_10KPL_GetChunkSizeAndAlgorithm as getChunkSizeAndAlgorithmUtil
from Utils import ABORT_UT04_10KPL_GetWriteSizeSimulationFor40Secs as writeSizeSimulationUtil
from Utils import ABORT_UT06_10KPL_InitParams as initParamsUtil
from Utils import ABORT_UT07_10KPL_MapAreas as mapAreasUtil
from Utils import ABORT_UT08_10KPL_ReadVerifyDynamicAreas as readVerifyUtil
# from Utils import ABORT_UT09_10KPL_PartitionAccess as PartitionAccessUtil  # For only eMMC cards
from Utils import ABORT_UT10_10KPL_PerformDynamicAreasWrites as performDynamicAreaWriteUtil

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


# Testcase Class - Begins
class ABORT_TC001_10K_PowerLossTest(customize_log):
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

        self.__initParamsUtil = initParamsUtil.ABORT_UT06_10KPL_InitParams(self.vtfContainer)
        self.__mapAreasUtil = mapAreasUtil.ABORT_UT07_10KPL_MapAreas(self.vtfContainer)
        self.__writeSizeSimulationUtil = writeSizeSimulationUtil.ABORT_UT04_10KPL_GetWriteSizeSimulationFor40Secs(self.vtfContainer)
        self.__performDynamicAreaWriteUtil = performDynamicAreaWriteUtil.ABORT_UT10_10KPL_PerformDynamicAreasWrites(self.vtfContainer)
        self.__powerLossInsidecmdUtil = powerLossInsidecmdUtil.ABORT_UT01_10KPL_PowerLossInsideCMD(self.vtfContainer)
        #self.__partitionAccessUtil = PartitionAccessUtil.ABORT_UT09_10KPL_PartitionAccess(self.vtfContainer)
        self.__readVerifyUtil = readVerifyUtil.ABORT_UT08_10KPL_ReadVerifyDynamicAreas(self.vtfContainer)
        self.__getChunkSizeAndAlgorithmUtil = getChunkSizeAndAlgorithmUtil.ABORT_UT03_10KPL_GetChunkSizeAndAlgorithm(self.vtfContainer)

        ##### Check and Switch to SD Protocol #####
        self.protocolName = self.__dvtLib.switchProtocol(ScriptName = self.__testName)

        ###### Customize Log ######
        self.fn = os.path.basename(getframeinfo(currentframe()).filename)
        customize_log.__init__(self, self.__TF)

        ##### Testcase Specific Variables #####


    def Run(self):

        ABORT_global_vars = {}

        # Call Utilites Script
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Test Case Execution Started")
        initParamValues, globalProjectConfVar, TC_Size, TC_Algorithm, numofTCs = self.__initParamsUtil.Run(ret = 1)

        ABORT_global_vars.update(initParamValues)
        ABORT_global_vars.update(TC_Size)
        ABORT_global_vars.update(TC_Algorithm)

        # TOBEDONE: Start Abort Hit Count
        # raise ValidationError.TestFailError(self.fn, "Yet to implement CVF API Start Abort Hit Count")
        # values for abort hit count

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Write the card Fully")

        ABORT_global_vars["origDataType"] = 1 + random.randrange(0, 4)

        # Set Label: LABEL_CHANGE_DATA_TYPE
        ABORT_global_vars["altDataType"] = 1 + random.randrange(0, 4)
        while (ABORT_global_vars["origDataType"] == ABORT_global_vars["altDataType"]):
            ABORT_global_vars["altDataType"] = 1 + random.randrange(0, 4)

        # Variable Declaration Operation
        if ABORT_global_vars["origDataType"] == 4:
            ABORT_global_vars["origDataType"] = 10

        # Variable Declaration Operation
        if ABORT_global_vars["altDataType"] == 4:
            ABORT_global_vars["altDataType"] = 10

        # Variable Declaration Operation
        ABORT_global_vars["origWriteStartAddress"] = 0
        ABORT_global_vars["origWriteEndAddress"] = ABORT_global_vars["origWriteStartAddress"] + ABORT_global_vars['currentPartSize'] - 1    # Address of Max LBA

        # TOBEDONE: SETTINGS
        # raise ValidationError.TestFailError(self.fn, "Yet to implement CVF API SETTINGS")

        # Multiple Write Operation
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple block Write with origWriteStartAddress: 0x%X, origWriteEndAddress: 0x%X, Pattern: %s"
                     % (ABORT_global_vars["origWriteStartAddress"], ABORT_global_vars["origWriteEndAddress"], ABORT_global_vars["origDataType"]))
        BlockCount = self.__sdCmdObj.calculate_blockcount(ABORT_global_vars["origWriteStartAddress"], ABORT_global_vars["origWriteEndAddress"])
        self.__dvtLib.WriteWithFPGAPattern(StartLba = ABORT_global_vars["origWriteStartAddress"], blockCount = BlockCount, pattern = ABORT_global_vars["origDataType"])

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Convert Areas from MB into sectors")

        # Variable Declaration Operation
        ABORT_global_vars["Area1_Size"] = old_div(ABORT_global_vars["Area1_Size"] * 1024 * 1024, 512)
        ABORT_global_vars["Area2_Size"] = old_div(ABORT_global_vars["Area2_Size"] * 1024 * 1024, 512)

        # Variable Declaration Operation
        # Mapping Static Area (between Area1 and Area2
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Map Static Area (between Area1 and Area2)")

        StaticAreaStartAddress = ABORT_global_vars["origWriteStartAddress"] + ABORT_global_vars["Area1_Size"]
        StaticAreaEndAddress = ABORT_global_vars["origWriteEndAddress"] - ABORT_global_vars["Area2_Size"]
        StaticAreaBlockCount = self.__sdCmdObj.calculate_blockcount(StaticAreaStartAddress, StaticAreaEndAddress)
        StaticAreaSize = StaticAreaEndAddress - StaticAreaStartAddress + 1
        StaticAreaVerifyChunkSize = old_div(StaticAreaSize, ABORT_global_vars['numOfPLsLeft'])
        StaticAreaDataType = ABORT_global_vars["origDataType"]
        StaticAreaVerifyStartAddress = StaticAreaStartAddress
        StaticAreaVerifyEndAddress = StaticAreaVerifyStartAddress + StaticAreaVerifyChunkSize - 1
        StaticAreaVerifyBlockCount = self.__sdCmdObj.calculate_blockcount(StaticAreaVerifyStartAddress, StaticAreaVerifyEndAddress)

        #TestCase to be tested
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Current Test Case ID to be tested")
        ABORT_global_vars['currentTCID'] = 0
        ABORT_global_vars['currentAreaID'] = 1
        ABORT_global_vars['Area1OldDataType'] = ABORT_global_vars["origDataType"]
        ABORT_global_vars['Area1NewDataType'] = ABORT_global_vars["altDataType"]
        ABORT_global_vars['Area2OldDataType'] = ABORT_global_vars["origDataType"]
        ABORT_global_vars['Area2NewDataType'] = ABORT_global_vars["altDataType"]

        # LABEL CHANGE_SIZE_ALGORITHM
        while True:

            # Call Script ABORT_UT07_10KPL_MapAreas
            mapAreaValues = self.__mapAreasUtil.Run(ABORT_global_vars, ret = 1)
            ABORT_global_vars.update(mapAreaValues)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "mapAreaValues - %s" % mapAreaValues)

            newVarName = "TC" + str(ABORT_global_vars['currentTCID']) + "_Size"
            ABORT_global_vars["currentWriteChunkSize"] = ABORT_global_vars[newVarName]
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "currentWriteChunkSize = %d\n" % ABORT_global_vars["currentWriteChunkSize"])

            newVarName = "TC" + str(ABORT_global_vars['currentTCID']) + "_Algorithm"
            ABORT_global_vars["currentWriteAlgorithm"] = ABORT_global_vars[newVarName]
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "currentWriteAlgorithm = %d\n" % ABORT_global_vars["currentWriteAlgorithm"])

            # Get write size simulation for 40 seconds before abort
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Get write size simulation for 40 seconds before abort")

            # Call Script ABORT_UT04_10KPL_GetWriteSizeSimulationFor40Secs
            writeSizeToTriggerAbort, totalNumOfChunks = self.__writeSizeSimulationUtil.Run(ABORT_global_vars["currentWriteChunkSize"], ret = 1)
            ABORT_global_vars["writeSizeToTriggerAbort"] = writeSizeToTriggerAbort
            ABORT_global_vars["totalNumOfChunks"] = totalNumOfChunks
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "writeChunkSize: %d, writeSizeToTriggerAbort: %d, totalNumOfChunks: %d"
                         % (ABORT_global_vars["currentWriteChunkSize"], ABORT_global_vars["writeSizeToTriggerAbort"], ABORT_global_vars["totalNumOfChunks"]))

            # Perform the dynamic areas writes (w / o abort)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Perform the dynamic areas writes (w / o abort)")
            # Call Script : ABORT_UT10_10KPL_PerformDynamicAreasWrites.py
            ABORT_global_vars = self.__performDynamicAreaWriteUtil.Run(ABORT_global_vars)

            # Perform the abort on write
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Perform the abort on write")

            # Variable Declaration Operation
            currentPLPhase = 0

            if (ABORT_global_vars["currentWriteAlgorithm"] != 2):   # If NOT random writes algorithm + abort

                # Variable Declaration Operation
                currentPLPhase = random.randrange(0, 10)    # currentPLPhase - on which phase (inside/between CMDs) the PL will occur (by the weights on init params script)

                newVarName = "Area" + str(ABORT_global_vars['currentAreaID']) + "OldNewDataStartAddress"    # Get write abort start address
                ABORT_global_vars["currentAbortStartAddress"] = ABORT_global_vars[newVarName]
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "currentAbortStartAddress = %d\n" % ABORT_global_vars["currentAbortStartAddress"])

                newVarName = "Area" + str(ABORT_global_vars['currentAreaID']) + "OldNewDataEndAddress"  # Get write abort end address
                ABORT_global_vars["currentAbortEndAddress"] = ABORT_global_vars[newVarName]
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "currentAbortEndAddress = %d\n" % ABORT_global_vars["currentAbortEndAddress"])

                newVarName = "Area" + str(ABORT_global_vars['currentAreaID']) + "NewDataType"   # Get write abort data type
                ABORT_global_vars["currentAbortDataType"] = ABORT_global_vars[newVarName]
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "currentAbortDataType = %d\n" % ABORT_global_vars["currentAbortDataType"])

                ABORT_global_vars["currentAbortSize"] = ABORT_global_vars["currentAbortEndAddress"] - ABORT_global_vars["currentAbortStartAddress"] + 1 # Get write abort size
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "currentAbortSize = %d\n" % ABORT_global_vars["currentAbortSize"])

            # Call script ABORT_UT01_10KPL_PowerLossInsideCMD.py
            if ((currentPLPhase >= 0) and (currentPLPhase < ABORT_global_vars['insideCMDPLWeight'])):   # If the random PL phase is inside the CMD
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Calling script ABORT_UT01_10KPL_PowerLossInsideCMD.py")
                self.__powerLossInsidecmdUtil.Run(ABORT_global_vars)

                # Perform delay before power on
                delay = ABORT_global_vars['delayBeforePowerOn']

                time.sleep(old_div(delay, 1000))    # delay is in millisecond, It is divided by 1000 to convert into sec.

                # Variable Declaration
                tempGlobalPowerUp = globalProjectConfVar['globalPowerUp']
                globalProjectConfVar['globalPowerUp'] = "powerCycle"

                # call Script DoBasicInit
                globalProjectConfVar = self.__sdCmdObj.DoBasicInit()

                globalProjectConfVar['globalPowerUp'] = tempGlobalPowerUp

            else:
                # Perform delay before power on
                delay = ABORT_global_vars['delayBetweenCMDPL']

                time.sleep(old_div(delay, 1000))    # delay is in millisecond, It is divided by 1000 to convert into sec.

                # Variable Declaration
                tempGlobalPowerUp = globalProjectConfVar['globalPowerUp']
                globalProjectConfVar['globalPowerUp'] = "powerCycle"

                # call Script DoBasicInit
                globalProjectConfVar = self.__sdCmdObj.DoBasicInit()

                globalProjectConfVar['globalPowerUp'] = tempGlobalPowerUp

                # Multiple Write Operation
                StartLBA = ABORT_global_vars["currentAbortStartAddress"]
                EndLBA = ABORT_global_vars["currentAbortEndAddress"]
                BlockCount = self.__sdCmdObj.calculate_blockcount(StartLBA, EndLBA)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple block Write with StartLba: 0x%X, BlockCount: 0x%X, Pattern:0x%X\n"
                             % (StartLBA, BlockCount, ABORT_global_vars["currentAbortDataType"]))
                self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = ABORT_global_vars["currentAbortDataType"])

            # Variable Declaration
            ABORT_global_vars['numOfPLsLeft'] = ABORT_global_vars['numOfPLsLeft'] - 1

            if ABORT_global_vars['numOfPLsLeft'] == 0:
                break

            # Variable Declaration
            ABORT_global_vars['numOfPerformedPLs'] = ABORT_global_vars['numOfPerformedPLs'] + 1

            # Check for Protocol mode
            # Not handled eMMC. This package is only for SD.
            # if globalProjectConfVar['globalProtocolMode'] != "SD":
            #     # Call Script: ABORT_UT09_10KPL_PartitionAccess.py
            #     currentPartionSize = self.__partitionAccessUtil.Run(ABORT_global_vars['partitionID'])

            # Perform Data Verification of the dynamic areas
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Perform Data Verification of the dynamic areas")

            if (ABORT_global_vars["currentWriteAlgorithm"] != 2):   # If NOT random writes algorithm + abort
                # Call script ABORT_UT08_10KPL_ReadVerifyDynamicAreas.py
                self.__readVerifyUtil.Run(ABORT_global_vars)
            else:   # If random writes algorithm -> compare to two data types each sector
                StartLBA = ABORT_global_vars["Area1StartAddress"]
                EndLBA = ABORT_global_vars["Area1EndAddress"]
                BlockCount = self.__sdCmdObj.calculate_blockcount(StartLBA, EndLBA)
                self.__sdCmdObj.VerifyReliableWrite(StartLBA, BlockCount, Pattern = ABORT_global_vars['Area1NewDataType'])  # Verify Area1

                StartLBA = ABORT_global_vars["Area2StartAddress"]
                EndLBA = ABORT_global_vars["Area2EndAddress"]
                BlockCount = self.__sdCmdObj.calculate_blockcount(StartLBA, EndLBA)
                self.__sdCmdObj.VerifyReliableWrite(StartLBA, BlockCount, Pattern = ABORT_global_vars['Area2NewDataType'])  # Verify Area2

            # Perform Data Verification of the static area using Multiple Read
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Perform Data Verification of the static area")

            self.__dvtLib.ReadWithFPGAPattern(StartLba = StaticAreaVerifyStartAddress, blockCount = StaticAreaVerifyBlockCount, pattern = ABORT_global_vars["origDataType"])

            # Variable Declaration
            StaticAreaVerifyStartAddress = StaticAreaVerifyStartAddress + StaticAreaVerifyChunkSize
            StaticAreaVerifyEndAddress = StaticAreaVerifyEndAddress + StaticAreaVerifyChunkSize

            # Complete write of data type until end of Areas using script ABORT10K_02_Util_AreaWriteCompletion.py
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Complete write of data type until end of Areas")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Loop Control (each loop = write abort of the specific algorithm / size")

            # Varible Declaration
            ABORT_global_vars['currentTCID'] = ABORT_global_vars['currentTCID'] + 1
            ABORT_global_vars['currentAreaID'] = 1
            rewriteAbortWriteFlag = 0

            if ABORT_global_vars['currentTCID'] >= numofTCs:
                ABORT_global_vars['currentTCID'] = 0

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Perform final Data Verification of the whole static area")

        # Perform Multiple Read
        self.__dvtLib.ReadWithFPGAPattern(StartLba = StaticAreaStartAddress, blockCount = StaticAreaBlockCount, pattern = ABORT_global_vars["origDataType"])

        # Report No.Of Abort Attempts
        numOfAbortAttempts = ABORT_global_vars['numOfPerformedPLs']
        numOfAbortHits = ABORT_global_vars['numOfPerformedPLs']
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "numOfAbortAttempts = %d, numOfAbortHits = %d" % (numOfAbortAttempts, numOfAbortHits))

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Test Case Execution Completed")
        return 0


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_ABORT_TC001_10K_PowerLossTest(self):
        obj = ABORT_TC001_10K_PowerLossTest(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
