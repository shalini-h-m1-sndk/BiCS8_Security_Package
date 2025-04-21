"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : ConfigSD_UT014_GlobalSetTO.st3
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : ConfigSD_UT014_GlobalSetTO.py
# CVF PLAYLIST SCRIPT            : None
# CVF SCRIPT                     : ConfigSD_UT014_GlobalSetTO.py
# DESCRIPTION                    : Module to set card time out values
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 19/09/2022
################################################################################
"""

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


class globalSetTO(customize_log):
    """
    class for setting Card Time Out values
    """

    def __init__(self, VTFContainer):
        """
        Name        : __init__
        Description : Constructor for Class globalSetTO
        Arguments   :
           VTFContainer : VTFContainer used for running the test
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

        ###### Customize Log: ######
        self.fn = os.path.basename(getframeinfo(currentframe()).filename)
        customize_log.__init__(self, self.__TF)

        ##### Testcase Specific Variables #####


    def Run(self):
        """
        Name: Run
        This is a configuration script and can be executed as indivual script also.
        if needed, function can be copied directly.
        Description: Set the Card Time Out values
        Step 1: Get the value of variables 'globalResetTO', 'globalReadTO', & 'globalWriteTO'
        Step 2: Set the Time out values
        Arguments:
            globalResetTO,   The reset timeout(hard)
            globalWriteTO,   The write timeout(hard)
            globalReadTO,    The read timeout(hard)
        """

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Card Time Out values")

        # Get the value of variables 'globalResetTO', 'globalReadTO', & 'globalWriteTO'
        globalResetTO = int(self.__config.get('globalResetTO'))
        globalReadTO = int(self.__config.get('globalReadTO'))
        globalWriteTO = int(self.__config.get('globalWriteTO'))

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Values are globalResetTO: %s, globalWriteTO: %s, globalReadTO: %s"
                              % (globalResetTO, globalWriteTO, globalReadTO))

        # Set the Time out values, If script fails, Exception is handled in CTF(Not sure in CVF) and script will fail.
        sdcmdWrap.CardSetTimeout(resetTO = globalResetTO, busyTO = globalWriteTO, readTO = globalReadTO)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Time Out values are set\n")

        return 0
