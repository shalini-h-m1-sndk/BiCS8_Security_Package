"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : ConfigSD_UT007_GlobalSetBusMode.st3
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : ConfigSD_UT007_GlobalSetBusMode.py
# CVF PLAYLIST SCRIPT            : None
# CVF SCRIPT                     : ConfigSD_UT007_GlobalSetBusMode.py
# DESCRIPTION                    : Module to set bus width for card
# PRERQUISTE                     : ConfigSD_UT005_GlobalPreTestingSettings.py
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 20/06/2022
################################################################################
"""

# SDDVT - Dependent TestCases
import SDDVT.Config_SD.ConfigSD_UT005_GlobalPreTestingSettings as globalPreTestingSettings

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


class GlobalSetBusMode(customize_log):
    def __init__(self, VTFContainer):
        """
        Name        : __init__
        Description : Constructor for Class GlobalSetBusMode
        Arguments   :
           VTFContainer : The VTFContainer used for running the test
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


    def Run(self, globalProjectConfVar = None):
        """
        Name: Run
        Description: This test is used for Random Password.

        Steps Used:
        # Check for globalCardType = SD, globalBusMode = 1 and globalProtocolMode != SDinSPI
                  Set Bus Width to 1
                  Get Sd Status and Verify Bus Width for 1
        # Check for globalCardType = SD, globalBusMode = 4 and globalProtocolMode != SDinSPI
                  Set Bus Width to 4
                  Get Sd Status and Verify Bus Width for 4
        """

        # Check for globalCardType = SD, globalBusMode = 1 and globalProtocolMode != SDinSPI
        if(globalProjectConfVar != None):
            globalCardType = globalProjectConfVar['globalCardType']
        else:   # For Backward compatbility
            globalProjectConfVar = globalPreTestingSettings.globalPreTestingSettings(self.vtfContainer).Run()
            globalCardType = globalProjectConfVar['globalCardType']

        globalBusMode = globalProjectConfVar['globalBusMode']

        if((globalCardType == "SD") and (globalBusMode == "Single") and (globalProjectConfVar['globalProtocolMode'] != "SDinSPI")):

            # Set the bus Width to One
            try:
                self.__dvtLib.SetBusWidth(busWidth = 1)
                self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus width is set to One")
            except ValidationError.CVFGenericExceptions as exc:
                self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus width is not set to One, which is not Expected")
                raise ValidationError.TestFailError(self.fn, "Bus width is not set to One")

            # Get the Sd status and Verify for Bus Width
            ACMD13 = self.__dvtLib.GetSDStatus()

            if  ACMD13.objSDStatusRegister.ui64DatBusWidth == 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus width is set to One and Verified")
            else:
                self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus width is not set to One, which is not Expected")

        # Check for globalCardType = SD,globalBusMode = 4 and globalProtocolMode!= SDinSPI
        elif((globalCardType == "SD") and (globalBusMode == "Four") and (globalProjectConfVar['globalProtocolMode'] != "SDinSPI")):

            #Set the bus Width to Four
            try:
                self.__dvtLib.SetBusWidth(busWidth = 4)
                self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus width is set to Four")
            except ValidationError.CVFGenericExceptions as exc:
                self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus width is not set to Four, which is not Expected")
                raise ValidationError.TestFailError(self.fn, "Bus width is not set to Four")

            # Get the Sd status and Verify for Bus Width
            ACMD13 = self.__dvtLib.GetSDStatus()

            if  ACMD13.objSDStatusRegister.ui64DatBusWidth == 2:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus width is set to Four and Verified")
            else:
                self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus width is not set to Four, which is not Expected")

        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Not Setting the Bus Width !!!")

        return 0
