"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : ABORT_TC001_10K_PowerLossTest.st3
# SCRIPTER SCRIPT                : ABORT_UT07_10KPL_MapAreas.st3
# CVF CALL ALL SCRIPT            : ABORT_TC001_10K_PowerLossTest.py
# CVF SCRIPT                     : ABORT_UT07_10KPL_MapAreas.py
# DESCRIPTION                    : The purpose of this script is to Generate mapping of Areas / Sections by inputs.
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : Jun-2022
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


class ABORT_UT07_10KPL_MapAreas(customize_log):
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


    def Run(self, ABORT_global_vars, ret = 0):
        """
        Definitions:
        -------------------
        AREA - 3 parts of the partition (start + end + between) at a defined size which will function
                    as 2 dynamic (start + end) areas and 1 (between) static area.

        SECTION - a specific part within an area, this size will be written using the defined chunk size
                        and each Area will be divided into the following 3 sections (or less):

                        1. 'New' - part of the area which is written in a new data type
                        2. 'Old' - part of the area which was previously written with the old data type
                        3. 'New/Old' - part of the area which was aborted during the write and can
                                                consist old/new data type per sector
        Purpose:
        ---------------
        - Generate mapping of Areas/Sections by inputs
        - Per section save the following:
                    1. Begin and End Addresses
                    2. Old and New Data types

        Inputs:
        ------------
        'Area1_Size', 'Area2_Size' (in sectors)
        'origDataType'

        Outputs:
        ---------------
        """
        #Empty Dictionary
        mapAreaUtilValues = {}

        # Map test Area1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Initialize the variables for Map test Area1")
        mapAreaUtilValues['Area1StartAddress'] = ABORT_global_vars["origWriteStartAddress"]
        mapAreaUtilValues['Area1EndAddress'] = mapAreaUtilValues['Area1StartAddress'] + ABORT_global_vars["Area1_Size"] - 1
        mapAreaUtilValues['Area1OldDataStartAddress'] = mapAreaUtilValues['Area1StartAddress']
        mapAreaUtilValues['Area1OldDataEndAddress'] = mapAreaUtilValues['Area1EndAddress']
        mapAreaUtilValues['Area1NewDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
        mapAreaUtilValues['Area1NewDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
        mapAreaUtilValues['Area1OldNewDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
        mapAreaUtilValues['Area1OldNewDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable

        # Map test Area2
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Initialize the variables for Map test Area2")
        mapAreaUtilValues['Area2StartAddress'] = ABORT_global_vars["origWriteEndAddress"] - ABORT_global_vars["Area2_Size"] + 1
        mapAreaUtilValues['Area2EndAddress'] = ABORT_global_vars["origWriteEndAddress"]
        mapAreaUtilValues['Area2OldDataStartAddress'] = mapAreaUtilValues['Area2StartAddress']
        mapAreaUtilValues['Area2OldDataEndAddress'] = mapAreaUtilValues['Area2EndAddress']
        mapAreaUtilValues['Area2NewDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
        mapAreaUtilValues['Area2NewDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
        mapAreaUtilValues['Area2OldNewDataStartAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable
        mapAreaUtilValues['Area2OldNewDataEndAddress'] = 0xFFFFFFFF    # In Scripter, If tring to assign -1 to a variable then 0xFFFFFFFF will be assigned to the variable

        if ret:
            return mapAreaUtilValues
        for key, value in mapAreaUtilValues:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PRE Defined mapAreaUtilValues:")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s : %d" % (key, value))

        return 0

# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_ABORT_UT07_10KPL_MapAreas(self):
        obj = ABORT_UT07_10KPL_MapAreas(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
