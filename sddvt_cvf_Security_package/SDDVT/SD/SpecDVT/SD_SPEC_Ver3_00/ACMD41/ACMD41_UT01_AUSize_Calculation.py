"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : ACMD41_UT01_AUSize_Calculation.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : ACMD41_UT01_AUSize_Calculation.py
# DESCRIPTION                    :
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=ACMD41_UT01_AUSize_Calculation --isModel=false --enable_console_log=1 --adapter=0
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
class ACMD41_UT01_AUSize_Calculation(customize_log):
    def __init__ (self,VTFContainer):
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
        self.CVFTestFactory = FactoryMethod.CVFTestFactory().GetProtocolLib()
        self.__TF = self.CVFTestFactory.TestFixture
        self.__ErrorManager = self.vtfContainer.device_session.GetErrorManager()
        self.currCfg = Configuration.ConfigurationManagerInitializer.ConfigurationManager.currentConfiguration

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


    # Testcase logic - Starts

    def Run(self, ret = 0):
        """
        Name : Run
        Description : this script is to check for Allocation Unit (AU) size in SD STATUS
        #keeping this for test purpose
        # Set bus width to 1
        # verify that bus width is set to 1
        # Check for AU_Size and assign the Value for AU_Size

        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Utility Execution Started " + "-" * 20 + "\n")
        #It is an utility script, Enable Step 1 if need to run as an individual script.

        #Get SD status structure
        ACMD13 = sdcmdWrap.SDStatus()
        self.SD_Status = ACMD13

        # Check for AU_Size and assign the Value for AU_Size
        AU_Size = ACMD13.objSDStatusRegister.ui64UHSAuSize
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "AU Size is %d" %AU_Size)

        if AU_Size == 1 :
            AU = 2 * 16
        if AU_Size == 2 :
            AU = 2 * 32
        if AU_Size == 3 :
            AU = 2 * 64
        if AU_Size == 4 :
            AU = 2 * 128
        if AU_Size == 5 :
            AU = 2 * 256
        if AU_Size == 6 :
            AU = 2 * 512
        if AU_Size == 7 :
            AU = 2 * 1024 * 1
        if AU_Size == 8 :
            AU = 2 * 1024 * 2
        if AU_Size == 9 :
            AU = 2 * 1024 * 4
        if AU_Size == 0xA :
            AU = 2 * 1024 * 8
        if AU_Size == 0xB :
            AU = 2 * 1024 * 12
        if AU_Size == 0xC :
            AU = 2 * 1024 * 16
        if AU_Size == 0xD :
            AU = 2 * 1024 * 24
        if AU_Size == 0xE :
            AU = 2 * 1024 * 32
        if AU_Size == 0xF :
            AU = 2 * 1024 * 64

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "AU Value is %d" % AU)

        if (ret==1):
            return AU

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Utility Execution Completed " + "-" * 20 + "\n")
        return 0
    #End of Run function
#End of AuSizeCalculation

class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    def test_ACMD41_UT01_AUSize_Calculation(self):  # [Same in xml tag: <Test name="test_ACMD41_UT01_AUSize_Calculation">]
        obj=ACMD41_UT01_AUSize_Calculation(self.vtfContainer)
        obj.Run(ret = 1)

# Testcase Class - Ends