"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : ABORT_TC001_10K_PowerLossTest.st3
# SCRIPTER SCRIPT                : ABORT_UT05_10KPL_UpdateSectionsAddresses.st3
# CVF CALL ALL SCRIPT            : ABORT_TC001_10K_PowerLossTest.py
# CVF SCRIPT                     : ABORT_UT05_10KPL_UpdateSectionsAddresses.py
# DESCRIPTION                    : The purpose of this utility script is to:
                                       - Update addresses of the 'Old', 'Old / New', and 'New' sections
                                       - Update by input (algorithm, chunk size and current write addresses and area)
                                       - The update is used for later abort and data verification
                                       - The 'Old / New' addresses will be used for abort and the next write transaction
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 27/06/2022
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


class ABORT_UT05_10KPL_UpdateSectionsAddresses(customize_log):
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

        # SEQUENTIAL ALGORITHM
        if ABORT_global_vars["currentWriteAlgorithm"] == 0:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SEQUENTIAL ALGORITHM")

            if (ABORT_global_vars['currentAreaID'] == 1):   # Abort in Area1
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Update Area1 Addresses")
                ABORT_global_vars['Area1OldNewDataStartAddress'] = ABORT_global_vars['Area1NewDataStartAddress']
                ABORT_global_vars['Area1OldNewDataEndAddress'] = ABORT_global_vars['Area1NewDataEndAddress']

                if ABORT_global_vars['Area1NewDataStartAddress'] == ABORT_global_vars['Area1StartAddress']: # In case the current chunk is the first chunk on the Area (no new data written)
                    ABORT_global_vars['Area1NewDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
                    ABORT_global_vars['Area1NewDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
                else:
                    ABORT_global_vars['Area1NewDataStartAddress'] = ABORT_global_vars['Area1StartAddress']
                    ABORT_global_vars['Area1NewDataEndAddress'] = ABORT_global_vars['Area1NewDataEndAddress'] - ABORT_global_vars["currentWriteChunkSize"]

                if ABORT_global_vars['Area1OldNewDataEndAddress'] == ABORT_global_vars['Area1EndAddress']:  # In case the current chunck is the last chunck on the Area (no old data written)
                    ABORT_global_vars['Area1OldDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable  # Update the old data type addresses
                    ABORT_global_vars['Area1OldDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
                else:
                    ABORT_global_vars['Area1OldDataStartAddress'] = ABORT_global_vars['Area1OldNewDataEndAddress'] + 1
                    ABORT_global_vars['Area1OldDataEndAddress'] = ABORT_global_vars['Area1EndAddress']

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Update Area2 Addresses")
                ABORT_global_vars['Area2NewDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable  # Update the new data type addresses
                ABORT_global_vars['Area2NewDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
                ABORT_global_vars['Area2OldNewDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable   # Update the old/new data type addresses
                ABORT_global_vars['Area2OldNewDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
                ABORT_global_vars['Area2OldDataStartAddress'] = ABORT_global_vars['Area2StartAddress']  # Update the old data type addresses
                ABORT_global_vars['Area2OldDataEndAddress'] = ABORT_global_vars['Area2EndAddress']

            if (ABORT_global_vars['currentAreaID'] == 2):   # Abort in Area2
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Update Area2 Addresses")
                ABORT_global_vars['Area2OldNewDataStartAddress'] = ABORT_global_vars['Area2NewDataStartAddress']    # Update the old/new data type addresses
                ABORT_global_vars['Area2OldNewDataEndAddress'] = ABORT_global_vars['Area2NewDataEndAddress']

                if ABORT_global_vars['Area2NewDataStartAddress'] == ABORT_global_vars['Area2StartAddress']: # In case the current chunk is the first chunk on the Area (no new data written)
                    ABORT_global_vars['Area2NewDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable  # Update the new data type addresses
                    ABORT_global_vars['Area2NewDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
                else:
                    ABORT_global_vars['Area2NewDataStartAddress'] = ABORT_global_vars['Area2StartAddress']  # Update the new data type addresses
                    ABORT_global_vars['Area2NewDataEndAddress'] = ABORT_global_vars['Area2NewDataEndAddress'] - ABORT_global_vars["currentWriteChunkSize"]

                if ABORT_global_vars['Area2OldNewDataEndAddress'] == ABORT_global_vars['Area2EndAddress']:  # In case the current chunk is the last chunk on the Area (no old data written)
                    ABORT_global_vars['Area2OldDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable  # Update the old data type addresses
                    ABORT_global_vars['Area2OldDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
                else:
                    ABORT_global_vars['Area2OldDataStartAddress'] = ABORT_global_vars['Area2OldNewDataEndAddress'] + 1  # Update the old data type addresses
                    ABORT_global_vars['Area2OldDataEndAddress'] = ABORT_global_vars['Area2EndAddress']

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Update Area1 Addresses")
                ABORT_global_vars['Area1NewDataStartAddress'] = ABORT_global_vars['Area1StartAddress']  # Update the new data type addresses
                ABORT_global_vars['Area1NewDataEndAddress'] = ABORT_global_vars['Area1EndAddress']
                ABORT_global_vars['Area1OldNewDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable   # Update the old/new data type addresses
                ABORT_global_vars['Area1OldNewDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
                ABORT_global_vars['Area1OldDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable  # Update the old data type addresses
                ABORT_global_vars['Area1OldDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable

        # SWAP ALGORITHM
        if ABORT_global_vars["currentWriteAlgorithm"] == 1:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SWAP ALGORITHM")

            if (ABORT_global_vars['currentAreaID'] == 1):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Update Area1 Addresses")
                ABORT_global_vars['Area1OldNewDataStartAddress'] = ABORT_global_vars['Area1NewDataStartAddress']    # Update the old/new data type addresses
                ABORT_global_vars['Area1OldNewDataEndAddress'] = ABORT_global_vars['Area1NewDataEndAddress']

                if ABORT_global_vars['Area1NewDataStartAddress'] == ABORT_global_vars['Area1StartAddress']: # In case the current chunk is the first chunk on the Area (no new data written)
                    ABORT_global_vars['Area1NewDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable  # Update the new data type addresses
                    ABORT_global_vars['Area1NewDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
                else:
                    ABORT_global_vars['Area1NewDataStartAddress'] = ABORT_global_vars['Area1StartAddress']  # Update the new data type addresses
                    ABORT_global_vars['Area1NewDataEndAddress'] = ABORT_global_vars['Area1NewDataEndAddress'] - ABORT_global_vars["currentWriteChunkSize"]

                if ABORT_global_vars['Area1OldNewDataEndAddress'] == ABORT_global_vars['Area1EndAddress']:  # In case the current chunk is the last chunk on the Area (no old data written)
                    ABORT_global_vars['Area1OldDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable  # Update the old data type addresses
                    ABORT_global_vars['Area1OldDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
                else:
                    ABORT_global_vars['Area1OldDataStartAddress'] = ABORT_global_vars['Area1OldNewDataEndAddress'] + 1  # Update the old data type addresses
                    ABORT_global_vars['Area1OldDataEndAddress'] = ABORT_global_vars['Area1EndAddress']

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Update Area2 Addresses")

                if ABORT_global_vars['Area1NewDataStartAddress'] == 0xFFFFFFFF:    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable # In case the current chunk is the first chunk on the other Area (no new data written)
                    ABORT_global_vars['Area2NewDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable  # Update the new data type addresses
                    ABORT_global_vars['Area2NewDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable

                else:
                    ABORT_global_vars['Area2NewDataStartAddress'] = ABORT_global_vars['Area2StartAddress']  # Update the new data type addresses
                    ABORT_global_vars['Area2NewDataEndAddress'] = ABORT_global_vars['Area2NewDataEndAddress'] - ABORT_global_vars["currentWriteChunkSize"]

                ABORT_global_vars['Area2OldNewDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable   # Update the old/new data type addresses
                ABORT_global_vars['Area2OldNewDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
                ABORT_global_vars['Area2OldDataStartAddress'] = ABORT_global_vars['Area2NewDataEndAddress'] + 1 # Update the old data type addresses
                ABORT_global_vars['Area2OldDataEndAddress'] = ABORT_global_vars['Area2EndAddress']

            if (ABORT_global_vars['currentAreaID'] == 2):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Update Area2 Addresses")
                ABORT_global_vars['Area2OldNewDataStartAddress'] = ABORT_global_vars['Area2NewDataStartAddress']    # Update the old/new data type addresses
                ABORT_global_vars['Area2OldNewDataEndAddress'] = ABORT_global_vars['Area2NewDataEndAddress']

                if ABORT_global_vars['Area2NewDataStartAddress'] == ABORT_global_vars['Area2StartAddress']: # In case the current chunk is the first chunk on the Area (no new data written)
                    ABORT_global_vars['Area2NewDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable  # Update the new data type addresses
                    ABORT_global_vars['Area2NewDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
                else:
                    ABORT_global_vars['Area2NewDataStartAddress'] = ABORT_global_vars['Area2StartAddress']  # Update the new data type addresses
                    ABORT_global_vars['Area2NewDataEndAddress'] = ABORT_global_vars['Area2NewDataEndAddress'] - ABORT_global_vars["currentWriteChunkSize"]

                if ABORT_global_vars['Area2OldNewDataEndAddress'] == ABORT_global_vars['Area2EndAddress']:  # In case the current chunk is the last chunk on the Area (no old data written)
                    ABORT_global_vars['Area2OldDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable  # Update the old data type addresses
                    ABORT_global_vars['Area2OldDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
                else:
                    ABORT_global_vars['Area2OldDataStartAddress'] = ABORT_global_vars['Area2OldNewDataEndAddress'] + 1  # Update the old data type addresses
                    ABORT_global_vars['Area2OldDataEndAddress'] = ABORT_global_vars['Area2EndAddress']

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Update Area1 Addresses")
                ABORT_global_vars['Area1NewDataStartAddress'] = ABORT_global_vars['Area1StartAddress']  # Update the new data type addresses
                ABORT_global_vars['Area1NewDataEndAddress'] = ABORT_global_vars['Area1NewDataEndAddress']
                ABORT_global_vars['Area1OldNewDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable   # Update the old/new data type addresses
                ABORT_global_vars['Area1OldNewDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable

                if ABORT_global_vars['Area2OldDataStartAddress'] == 0xFFFFFFFF:    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable # In case the current chunk is the last chunk on the other Area (no new data written)
                    ABORT_global_vars['Area1OldDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable  # Update the old data type addresses
                    ABORT_global_vars['Area1OldDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
                else:
                    ABORT_global_vars['Area1OldDataStartAddress'] = ABORT_global_vars['Area1NewDataEndAddress'] + 1
                    ABORT_global_vars['Area1OldDataEndAddress'] = ABORT_global_vars['Area1EndAddress']

        # RANDOM ALGORITHM
        if ABORT_global_vars["currentWriteAlgorithm"] == 2:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RANDOM ALGORITHM")

            # Variable Declaration
            ABORT_global_vars['Area1NewDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable  # Update the new data type addresses
            ABORT_global_vars['Area1NewDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
            ABORT_global_vars['Area1OldDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable  # Update the old data type addresses
            ABORT_global_vars['Area1OldDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
            ABORT_global_vars['Area1OldNewDataStartAddress'] = ABORT_global_vars['Area1StartAddress']   # Update the old/new data type addresses
            ABORT_global_vars['Area1OldNewDataEndAddress'] = ABORT_global_vars['Area1EndAddress']
            ABORT_global_vars['Area2NewDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable  # Update the new data type addresses
            ABORT_global_vars['Area2NewDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
            ABORT_global_vars['Area2OldNewDataStartAddress'] = ABORT_global_vars['Area2StartAddress']   # Update the old/new data type addresses
            ABORT_global_vars['Area2OldNewDataEndAddress'] = ABORT_global_vars['Area2EndAddress']
            ABORT_global_vars['Area2OldDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable  # Update the old data type addresses
            ABORT_global_vars['Area2OldDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed execution of updateSectionUtil Utility")
        return ABORT_global_vars


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_ABORT_UT05_10KPL_UpdateSectionsAddresses(self):
        obj = ABORT_UT05_10KPL_UpdateSectionsAddresses(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
