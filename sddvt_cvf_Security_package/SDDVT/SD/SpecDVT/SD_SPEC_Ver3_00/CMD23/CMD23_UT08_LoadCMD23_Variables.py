"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                :
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : CMD23_UT08_LoadCMD23_Variables.py
# DESCRIPTION                    :
# PRERQUISTE                     :
# STANDALONE EXECUTION           : No. It is an utility script.
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sushmitha P.S
# REVIEWED BY                    : Sivagurunathan
# DATE                           : 05-Jun-2024
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

# Testcase Utility Class - Begins

class CMD23_UT08_LoadCMD23_Variables(customize_log):
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

    # Testcase Utility Logic - Starts

    def Run(self, ret = 0):
        """
        Name : Run
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Utility Execution Started " + "-" * 20 + "\n")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Defined Variables for CMD23 command ")
        CMD23Variables = {}
        CMD23Variables['PredefineNumBlkFlag']       = 1
        CMD23Variables['IgnorePredefinedBlockCnt']  = 1
        CMD23Variables['PredefinedNumOfBlkCnt']     = 1
        CMD23Variables['CMD23StartBlock']           = 0
        CMD23Variables['CMD23BlockCount']           = 1
        CMD23Variables['CMD23DataType']             = 1
        CMD23Variables['CMD23VerifyWriteFlag']      = 0

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FillSectionWithZero = 0: Write utility will fill the tested section with datatype 0 after the test")

        CMD23Variables['FillSectionWithZero']      = 0
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Internal vars in case of PredefineNumBlkFlag = 1")

        CMD23Variables['WrongDataTypeError']       = 0

        if ret:
            return CMD23Variables
        for key, value in CMD23Variables:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PRE Defined CMD23 Variables:")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s : %d" %(key, value))

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Utility Execution Completed " + "-" * 20 + "\n")
        return 0

    #End of Run function
#End of LoadCMD23Variables


    # Testcase Utility Logic - Ends

# Testcase Utility Class - Ends