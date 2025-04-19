"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : ABORT_TC001_10K_PowerLossTest.st3
# SCRIPTER SCRIPT                : ABORT_UT10_10KPL_PerformDynamicAreasWrites.st3
# CVF CALL ALL SCRIPT            : ABORT_TC001_10K_PowerLossTest.py
# CVF SCRIPT                     : ABORT_UT10_10KPL_PerformDynamicAreasWrites.py
# DESCRIPTION                    : The purpose of this utility script is to:
                                       - Perform the dynamic areas writes by the specific algorithm and size
                                       - Update the old, new and old / new sections inside each area after each write
                                       - Each Loops should be performed in ~40secs
# PRERQUISTE                     : ABORT_UT05_10KPL_UpdateSectionsAddresses.py
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 27/06/2022
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
import SDDVT.SD.SpecDVT.Aborts_PowerLoss_10K.Utils.ABORT_UT05_10KPL_UpdateSectionsAddresses as updateSectionUtil

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


class ABORT_UT10_10KPL_PerformDynamicAreasWrites(customize_log):
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
        self.__updateSectionUtil = updateSectionUtil.ABORT_UT05_10KPL_UpdateSectionsAddresses(self.vtfContainer)


    def BLOCK_SWITCH_DATA_TYPES(self, ABORT_global_vars):
        if ABORT_global_vars["Area1NewDataType"] == ABORT_global_vars["origDataType"]:
            ABORT_global_vars["Area1NewDataType"] = ABORT_global_vars["altDataType"]
            ABORT_global_vars["Area1OldDataType"] = ABORT_global_vars["origDataType"]
            ABORT_global_vars["Area2NewDataType"] = ABORT_global_vars["altDataType"]
            ABORT_global_vars["Area2OldDataType"] = ABORT_global_vars["origDataType"]
        else:
            ABORT_global_vars["Area1OldDataType"] = ABORT_global_vars["altDataType"]
            ABORT_global_vars["Area1NewDataType"] = ABORT_global_vars["origDataType"]
            ABORT_global_vars["Area2OldDataType"] = ABORT_global_vars["altDataType"]
            ABORT_global_vars["Area2NewDataType"] = ABORT_global_vars["origDataType"]

    def Run(self, ABORT_global_vars, rewriteAbortWriteFlag = 0):

        # Variable Declaration
        newVarName = "LABEL_ALGORITHM_" + str(ABORT_global_vars["currentWriteAlgorithm"])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "setLabel = %s\n" % newVarName)

        if newVarName == "LABEL_ALGORITHM_0":   # [SEQUENTIAL ALGORITHM] (finish Area1 by seq. chunks > jump to Area2 > finish Area2 by seq. chunks  jump to Area1 > ...)

            ############################################## ALGORITHM_0(SEQUENTIAL ALGORITHM) Start ##############################################
            self.LABEL_ALGORITHM = True
            while self.LABEL_ALGORITHM:  # LABEL_ALGORITHM_0
                if rewriteAbortWriteFlag == 1:
                    newVarName = "Area" + str(ABORT_global_vars['currentAreaID']) + "OldNewDataStartAddress"
                    dynVarName = "Area" + str(ABORT_global_vars['currentAreaID']) + "NewDataStartAddress"
                    dynVarName = ABORT_global_vars[newVarName]
                    newVarName = "Area" + str(ABORT_global_vars['currentAreaID']) + "OldNewDataEndAddress"
                    dynVarName = "Area" + str(ABORT_global_vars['currentAreaID']) + "NewataEndAddress"
                    dynVarName = ABORT_global_vars[newVarName]
                else:
                    newVarName = "Area" + str(ABORT_global_vars['currentAreaID']) + "StartAddress"
                    dynVarName = "Area" + str(ABORT_global_vars['currentAreaID']) + "NewDataStartAddress"
                    dynVarName = ABORT_global_vars[newVarName]
                    newVarName = "Area" + str(ABORT_global_vars['currentAreaID']) + "NewDataStartAddress"
                    dynVarName = "Area" + str(ABORT_global_vars['currentAreaID']) + "NewDataEndAddress"
                    dynVarName = ABORT_global_vars[newVarName] + ABORT_global_vars["currentWriteChunkSize"] - 1

                    # Variable Declaration
                    rewriteAbortWriteFlag = 1

                # Variable Declaration
                newVarName = "LABEL_ALGO0_AREA" + str(ABORT_global_vars['currentAreaID'])

                if newVarName == "LABEL_ALGO0_AREA1":
                    while True: # Label LABEL_ALGO0_AREA1
                        ABORT_global_vars['currentAreaID'] = 1
                        ABORT_global_vars["totalNumOfChunks"] = ABORT_global_vars["totalNumOfChunks"] - 1

                        if ABORT_global_vars["totalNumOfChunks"] == 0:  # Go to label LABEL_END_ALGORITHM
                            self.LABEL_ALGORITHM = False
                            break

                        StartLBA = ABORT_global_vars['Area1NewDataStartAddress']
                        EndLBA = ABORT_global_vars['Area1NewDataEndAddress']
                        BlockCount = self.__sdCmdObj.calculate_blockcount(StartLBA, EndLBA)

                        self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = ABORT_global_vars['Area1NewDataType'])

                        ABORT_global_vars['Area1NewDataStartAddress'] = ABORT_global_vars['Area1NewDataStartAddress'] + ABORT_global_vars["currentWriteChunkSize"]
                        ABORT_global_vars['Area1NewDataEndAddress'] = ABORT_global_vars['Area1NewDataEndAddress'] + ABORT_global_vars["currentWriteChunkSize"]

                        if ABORT_global_vars['Area1NewDataEndAddress'] <= ABORT_global_vars['Area1EndAddress']:
                            continue
                        else:
                            ABORT_global_vars['Area2NewDataStartAddress'] = ABORT_global_vars['Area2StartAddress']
                            ABORT_global_vars['Area2NewDataEndAddress'] = ABORT_global_vars['Area2NewDataStartAddress'] + ABORT_global_vars["currentWriteChunkSize"] - 1
                            newVarName = "LABEL_ALGO0_AREA2"
                            break

                    if (self.LABEL_ALGORITHM == False):
                        break

                if newVarName == "LABEL_ALGO0_AREA2":
                    while True: # Label LABEL_ALGO0_AREA2
                        ABORT_global_vars['currentAreaID'] = 2
                        ABORT_global_vars["totalNumOfChunks"] = ABORT_global_vars["totalNumOfChunks"] - 1

                        if ABORT_global_vars["totalNumOfChunks"] == 0:
                            self.LABEL_ALGORITHM = False
                            break

                        StartLBA = ABORT_global_vars['Area2NewDataStartAddress']
                        EndLBA = ABORT_global_vars['Area2NewDataEndAddress']
                        BlockCount = self.__sdCmdObj.calculate_blockcount(StartLBA, EndLBA)

                        self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = ABORT_global_vars['Area2NewDataType'])

                        ABORT_global_vars['Area2NewDataStartAddress'] = ABORT_global_vars['Area2NewDataStartAddress'] + ABORT_global_vars["currentWriteChunkSize"]
                        ABORT_global_vars['Area2NewDataEndAddress'] = ABORT_global_vars['Area2NewDataEndAddress'] + ABORT_global_vars["currentWriteChunkSize"]

                        if ABORT_global_vars['Area2NewDataEndAddress'] <= ABORT_global_vars['Area2EndAddress']:
                            continue
                        else:
                            break

                    if (self.LABEL_ALGORITHM == False):
                        break

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Both Area1 and Area2 are written")
                ABORT_global_vars['currentAreaID'] = 1
                rewriteAbortWriteFlag = 0

                self.BLOCK_SWITCH_DATA_TYPES(ABORT_global_vars)
            ############################################## ALGORITHM_0(SEQUENTIAL ALGORITHM) End ##############################################

        elif newVarName == "LABEL_ALGORITHM_1": # [SWAP ALGORITHM] (Area1 1st chunk > Area2 1st chunk > Area1 2nd chunk > Area2 2nd chunk > ... > End area1 and 2 >  jump to Area1 > ...)

            ############################################## ALGORITHM_1(SWAP ALGORITHM) Start ##############################################
            self.LABEL_ALGORITHM = True
            while self.LABEL_ALGORITHM:  # LABEL_ALGORITHM_1
                if rewriteAbortWriteFlag == 1:
                    if ABORT_global_vars['currentAreaID'] == 1:
                        ABORT_global_vars['Area1NewDataStartAddress'] = ABORT_global_vars['Area1OldNewDataStartAddress']
                        ABORT_global_vars['Area1NewDataEndAddress'] = ABORT_global_vars['Area1OldNewDataEndAddress']
                        ABORT_global_vars['Area2NewDataStartAddress'] = ABORT_global_vars['Area2NewDataEndAddress'] - ABORT_global_vars["currentWriteChunkSize"] + 1
                    if ABORT_global_vars['currentAreaID'] == 2:
                        ABORT_global_vars['Area2NewDataStartAddress'] = ABORT_global_vars['Area2OldNewDataStartAddress']
                        ABORT_global_vars['Area2NewDataEndAddress'] = ABORT_global_vars['Area2OldNewDataEndAddress']
                        ABORT_global_vars['Area1NewDataStartAddress'] = ABORT_global_vars['Area1NewDataEndAddress'] - ABORT_global_vars["currentWriteChunkSize"] + 1
                else:
                    ABORT_global_vars['Area1NewDataStartAddress'] = ABORT_global_vars['Area1StartAddress']
                    ABORT_global_vars['Area1NewDataEndAddress'] = ABORT_global_vars['Area1NewDataStartAddress'] + ABORT_global_vars["currentWriteChunkSize"] - 1
                    ABORT_global_vars['Area2NewDataStartAddress'] = ABORT_global_vars['Area2StartAddress']
                    ABORT_global_vars['Area2NewDataEndAddress'] = ABORT_global_vars['Area2NewDataStartAddress'] + ABORT_global_vars["currentWriteChunkSize"] - 1
                    rewriteAbortWriteFlag = 1

                newVarName = "LABEL_ALGO1_AREA" + str(ABORT_global_vars['currentAreaID'])

                def LABEL_ALGO1_AREA1():
                    LABEL_ALGO1_AREA1_Loop = True
                    while LABEL_ALGO1_AREA1_Loop:
                        ABORT_global_vars['currentAreaID'] = 1
                        ABORT_global_vars["totalNumOfChunks"] = ABORT_global_vars["totalNumOfChunks"] - 1

                        if ABORT_global_vars["totalNumOfChunks"] == 0:  # Go to label LABEL_END_ALGORITHM
                            self.LABEL_ALGORITHM = False
                            break

                        StartLBA = ABORT_global_vars['Area1NewDataStartAddress']
                        EndLBA = ABORT_global_vars['Area1NewDataEndAddress']
                        BlockCount = self.__sdCmdObj.calculate_blockcount(StartLBA, EndLBA)
                        self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = ABORT_global_vars['Area1NewDataType'])

                        self.LABEL_ALGORITHM, LABEL_ALGO1_AREA1_Loop = LABEL_ALGO1_AREA2()

                def LABEL_ALGO1_AREA2():
                    ABORT_global_vars['currentAreaID'] = 2
                    ABORT_global_vars["totalNumOfChunks"] = ABORT_global_vars["totalNumOfChunks"] - 1

                    if ABORT_global_vars["totalNumOfChunks"] == 0:
                        return False, False # self.LABEL_ALGORITHM, LABEL_ALGO1_AREA1_Loop

                    StartLBA = ABORT_global_vars['Area2NewDataStartAddress']
                    EndLBA = ABORT_global_vars['Area2NewDataEndAddress']
                    BlockCount = self.__sdCmdObj.calculate_blockcount(StartLBA, EndLBA)
                    self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = ABORT_global_vars['Area2NewDataType'])

                    ABORT_global_vars['Area1NewDataStartAddress'] = ABORT_global_vars['Area1NewDataStartAddress'] + ABORT_global_vars["currentWriteChunkSize"]
                    ABORT_global_vars['Area1NewDataEndAddress'] = ABORT_global_vars['Area1NewDataEndAddress'] + ABORT_global_vars["currentWriteChunkSize"]
                    ABORT_global_vars['Area2NewDataStartAddress'] = ABORT_global_vars['Area2NewDataStartAddress'] + ABORT_global_vars["currentWriteChunkSize"]
                    ABORT_global_vars['Area2NewDataEndAddress'] = ABORT_global_vars['Area2NewDataEndAddress'] + ABORT_global_vars["currentWriteChunkSize"]

                    if (ABORT_global_vars['Area2NewDataEndAddress'] <= ABORT_global_vars['Area2EndAddress']) and (ABORT_global_vars['Area1NewDataEndAddress'] <= ABORT_global_vars['Area1EndAddress']):
                        return True, True # self.LABEL_ALGORITHM, LABEL_ALGO1_AREA1_Loop
                    else:
                        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Both Areas are written")
                        return True, False # self.LABEL_ALGORITHM, LABEL_ALGO1_AREA1_Loop

                if newVarName == "LABEL_ALGO1_AREA1":
                    LABEL_ALGO1_AREA1()

                elif newVarName == "LABEL_ALGO1_AREA2":
                    self.LABEL_ALGORITHM, LABEL_ALGO1_AREA1_Loop = LABEL_ALGO1_AREA2()
                    if LABEL_ALGO1_AREA1_Loop:
                        LABEL_ALGO1_AREA1()


                if (self.LABEL_ALGORITHM == False):
                    break

                ABORT_global_vars["currentAreaID"] = 1

                if ABORT_global_vars['Area1NewDataEndAddress'] < ABORT_global_vars['Area1EndAddress']:

                    StartLBA = ABORT_global_vars['Area1NewDataEndAddress']
                    EndLBA = ABORT_global_vars['Area1EndAddress']
                    BlockCount = self.__sdCmdObj.calculate_blockcount(StartLBA, EndLBA)
                    self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = ABORT_global_vars['Area1NewDataType'])

                if ABORT_global_vars['Area2NewDataEndAddress'] < ABORT_global_vars['Area2EndAddress']:

                    StartLBA = ABORT_global_vars['Area2NewDataEndAddress']
                    EndLBA = ABORT_global_vars['Area2EndAddress']
                    BlockCount = self.__sdCmdObj.calculate_blockcount(StartLBA, EndLBA)
                    self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = ABORT_global_vars['Area2NewDataType'])

                rewriteAbortWriteFlag = 0
                self.BLOCK_SWITCH_DATA_TYPES(ABORT_global_vars)
            ############################################## ALGORITHM_1(SWAP ALGORITHM) End ##############################################

        elif newVarName == "LABEL_ALGORITHM_2": # [RANDOM ALGORITHM] (Write random chunk size to any aligned to size address on any Area)

            ############################################## ALGORITHM_2(RANDOM ALGORITHM) Start ##############################################
            while (old_div((ABORT_global_vars["totalNumOfChunks"] * 2), 3)):
                randomAreaID = 1 + random.randrange(0, 2)
                randomDataType = random.randrange(0, 2)

                if randomDataType == 0:
                    currentWriteDataType = ABORT_global_vars["origDataType"]
                else:
                    currentWriteDataType = ABORT_global_vars["altDataType"]

                newVarName = "Area" + str(randomAreaID) + "StartAddress"
                currentAreaStartAddress = ABORT_global_vars[newVarName]
                newVarName = "Area" + str(randomAreaID) + "EndAddress"
                currentAreaEndAddress = ABORT_global_vars[newVarName]
                newVarName = "Area" + str(randomAreaID) + "_Size"
                currentAreaSize = ABORT_global_vars[newVarName]

                currentWriteStartAddress = currentAreaStartAddress + (random.randrange(0, (old_div(currentAreaSize, ABORT_global_vars["currentWriteChunkSize"]))) * ABORT_global_vars["currentWriteChunkSize"])
                currentWriteEndAddress = currentWriteStartAddress + ABORT_global_vars["currentWriteChunkSize"] - 1

                StartLBA = currentWriteStartAddress
                EndLBA = currentWriteEndAddress
                BlockCount = self.__sdCmdObj.calculate_blockcount(StartLBA, EndLBA)

                self.__dvtLib.WriteWithFPGAPattern(StartLba = StartLBA, blockCount = BlockCount, pattern = currentWriteDataType)

            ABORT_global_vars["currentAbortDataType"] = currentWriteDataType
            newVarName = "Area" + str(randomAreaID) + "StartAddress"
            currentAreaStartAddress = ABORT_global_vars[newVarName]
            newVarName = "Area" + str(randomAreaID) + "EndAddress"
            currentAreaEndAddress = ABORT_global_vars[newVarName]
            newVarName = "Area" + str(randomAreaID) + "_Size"
            currentAreaSize = ABORT_global_vars[newVarName]

            ABORT_global_vars["currentAbortStartAddress"] = currentAreaStartAddress + (random.randrange(0, (old_div(currentAreaSize, ABORT_global_vars["currentWriteChunkSize"]))) * ABORT_global_vars["currentWriteChunkSize"])
            ABORT_global_vars["currentAbortEndAddress"] = ABORT_global_vars["currentAbortStartAddress"] + ABORT_global_vars["currentWriteChunkSize"] - 1
            ABORT_global_vars["currentAbortSize"] = ABORT_global_vars["currentAbortEndAddress"] - ABORT_global_vars["currentAbortStartAddress"] + 1
            ############################################## ALGORITHM_2(RANDOM ALGORITHM) End ##############################################

        else:
            raise ValidationError.ParametersError(self.fn, "Value of parameter currentWriteAlgorithm should be one of the following (0, 1, 2), because of only three algorithms are present in ABORT10K_11")

        # SET_LABEL: LABEL_END_ALGORITHM
        if (ABORT_global_vars["currentWriteAlgorithm"] != 2):
            ABORT_global_vars = self.__updateSectionUtil.Run(ABORT_global_vars)

        return ABORT_global_vars


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_ABORT_UT10_10KPL_PerformDynamicAreasWrites(self):
        obj = ABORT_UT10_10KPL_PerformDynamicAreasWrites(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
