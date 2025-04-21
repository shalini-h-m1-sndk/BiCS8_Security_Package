"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                :
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     :
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : TC020_CheckDebugPinsAccess.py
# DESCRIPTION                    : Debug Pins Access after Secure Lock and Unlock state
# PRERQUISTE                     :
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=TC020_CheckDebugPinsAccess.py --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR                         : Shalini HM
# REVIEWED BY                    : None
# DATE                           : 17-02-2025
################################################################################
"""

# SDDVT - Dependent TestCases
from builtins import str
import SecurityUtils
import DiagnosticLib
import Security_ErrorCodes as Security_ErrorCodes

# SDDVT - Common Interface for Testcase
import SDDVT.Common.DvtCommonLib as DvtCommonLib

# SDDVT - SD Specification and commands related Interface
import SDDVT.Common.SDCommandLib as SDCommandLib

# SDDVT - CQ Utils
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
import struct
import re

import Utils



# Global Variables

DEVICESTATES = { 0x0 : 'DEVELOPMENT', 0x1: 'LOCKED', 0x2 : 'BRMA', 0x3: 'Unlock'}

class TC020_CheckDebugPinsAccess(customize_log):
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
        self.__DeviceState= "Locked"
        self.__Challenge=None
        self.__Transientstate =None

        #### Testcase based ##########
        self.RMAutils = SecurityUtils.RMAUtilities(self.vtfContainer)
        self.__SecurityErrorCodes = Security_ErrorCodes.ErrorCodes()

    def Run(self):
        """
        Executes the test.
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name,  "*" * 80)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name,  "Issue Diag to check Device State")

        state = self.RMAutils.GetDeviceState(signed=True)


        # if the device state is unlocked move card to lock state

        # Check the JTAG and ATB when Card is in Lock state(Should be disabled)

        if state == "Locked":
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name,  "card is in locked state")
            self.RMAutils.DoPowerCycle()
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name,  "Moving the card to locked state")
            try:
                self.RMAutils.MoveToLock()
            except:
                self.vtfContainer.CleanPendingExceptions()
            state = self.RMAutils.GetDeviceState(signed=True)
            if state == "Locked":
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name,  "Moved the card to locked state")

        # Get Device challenge for PRMA Unlock
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name,  "Issue Diag to get GDC for PRMA Unlock")
        self.__Challenge=self.RMAutils.GetDeviceChallenge(rma='PRMA', signed=True)

        # Unlock command
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name,  "Issue Diag to Unlock the card")
        self.RMAutils.UnlockCard("PRMA", self.__Challenge)

        # Check the JTAG and ATB when Card is in PRMA UnLock state(should be enabled)




# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_TC020_CheckDebugPinsAccess(self):
        obj = TC020_CheckDebugPinsAccess(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends