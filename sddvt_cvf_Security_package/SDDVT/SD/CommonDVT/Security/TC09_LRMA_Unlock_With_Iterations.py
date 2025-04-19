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
# CVF SCRIPT                     : TC09_LRMA_Unlock_With_Iterations.py
# DESCRIPTION                    : Perform LRMA Unlock with different iteration number.
# PRERQUISTE                     :
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=TC09_LRMA_Unlock_With_Iterations.py --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR                         : Shalini HM
# REVIEWED BY                    : None
# DATE                           : 03-dec-2024
################################################################################
"""


# SDDVT - Dependent TestCases
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


DEVICESTATES = { 0x0 : 'DEVELOPMENT', 0x1: 'LOCKED', 0x2 : 'BRMA', 0x3: 'Unlock'}

class TC09_LRMA_Unlock_With_Iterations(customize_log):

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
        self.protocolName = self.__dvtLib.switchProtocol(ScriptName=self.__testName)

        ###### Customize Log ######
        self.fn = os.path.basename(getframeinfo(currentframe()).filename)
        customize_log.__init__(self, self.__TF)
        self.__DeviceState = "Locked"
        self.__Challenge = None
        self.__Transientstate = None

        #### Testcase based ##########
        self.RMAutils = SecurityUtils.RMAUtilities(self.vtfContainer)
        self.__SecurityErrorCodes = Security_ErrorCodes.ErrorCodes()

    def Run(self):
        """
        Executes the test.
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*" * 80)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Issue Diag to check Device State")

        state = self.RMAutils.GetDeviceState(signed=True)
        
        # if the device state is unlocked move card to lock state        
        if state == "Locked":
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name,  "card is in locked state")
            #self.RMAutils.DoPowerCycle()
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name,  "Moving the card to locked state")
            self.RMAutils.MoveToLock()

        # Get Device challenge for LRMA Unlock
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name,  "Get GDC for LRMA Unlock")
        self.__Challenge = self.RMAutils.GetDeviceChallenge(rma='LRMA', signed=True)

        # Unlock command with iteration count 9999

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name,  "Issue Unlock command with iteration count 9999")

        try:
            status = self.RMAutils.UnlockCard("LRMA", self.__Challenge, iterations=9999)
            if status != 0:
                ErrorCodes = str(hex(status))
                error_message = self.__SecurityErrorCodes.CheckError(ErrorCodes)
                if ErrorCodes == "0x6000204":                
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 
                                 f"Unlock unsuccessfull. Error Code: {ErrorCodes}, Message: {error_message}")
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Unlock unsuccessfull as expected,RSA signature verification failed for KDF(PRMA/LRMA)")
                    self.vtfContainer.CleanPendingExceptions()
                else:
                    raise ValidationError.TestFailError(self.fn,f"unlock unsuccessfull. Error Code: {ErrorCodes}, Message: {error_message}")                
            else:
                raise ValidationError.TestFailError(self.fn, "Unlock successful which is not expected.")
        except:
            raise ValidationError.TestFailError(self.fn, "Unlock CMD failed")          


        # Unlock Command with iteration count 10000
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name,  "Issue Unlock command with iteration count 10000")
        try:
            status = self.RMAutils.UnlockCard("LRMA", self.__Challenge, iterations=10000)
            if status != 0:
                ErrorCodes = str(hex(status))
                error_message = self.__SecurityErrorCodes.CheckError(ErrorCodes)
                if ErrorCodes == "0x6000204":                
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 
                                 f"Unlock unsuccessfull. Error Code: {ErrorCodes}, Message: {error_message}")
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Unlock unsuccessfull as expected,RSA signature verification failed for KDF(PRMA/LRMA)")
                    self.vtfContainer.CleanPendingExceptions()
                else:
                    raise ValidationError.TestFailError(self.fn,f"unlock unsuccessfull. Error Code: {ErrorCodes}, Message: {error_message}")                
            else:
                raise ValidationError.TestFailError(self.fn, "Unlock successful which is not expected.")
        except:
            raise ValidationError.TestFailError(self.fn, "Unlock CMD failed")        
            

        # Get device Challenge for LRMA Unlock
        self.__Challenge = self.RMAutils.GetDeviceChallenge(rma='LRMA', signed=True)

        # Unlock Command with iteration count 10000
        try:
            self.RMAutils.UnlockCard("LRMA", self.__Challenge, iterations=10000)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "LRMA Unlock successful.")
        except:
            raise ValidationError.TestFailError(self.fn, "Unlock CMD failed.")

# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_TC09_LRMA_Unlock_With_Iterations(self):
        obj = TC09_LRMA_Unlock_With_Iterations(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends