"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : Utility_Set_Freq_Volt_Timeout.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : CMD23_UT12_SetFreq_Volt_Timeout.py
# DESCRIPTION                    :
# PRERQUISTE                     :
# STANDALONE EXECUTION           : No. It is an utility script.
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 25-Nov-2022
# UPDATED BY                     : Sushmitha P.S
# UPDATED DATE                   : 30-May-2024
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
class CMD23_UT12_SetFreq_Volt_Timeout(customize_log):
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

    def Run(self):
        """
        Name : Run
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Utility Execution Started " + "-" * 20 + "\n")
        # Set Frequency to 'globalLSHostFreq'
        globalLSHostFreq = int(self.__config.get('globalLSHostFreq'))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'globalLSHostFreq: %d' % globalLSHostFreq)
        self.__sdCmdObj.SetFrequency(Freq = globalLSHostFreq)

        # Set Voltage 3.30 V , PowerSupply: Flash
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Volt: 3.30")
        globalVDDFMaxCurrent = self.__config.get('globalVDDFMaxCurrent')
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalVDDFMaxCurrent : %d, PowerSupply: VDDF"%int(globalVDDFMaxCurrent))

        sdFlashVoltage = sdcmdWrap.SVoltage()
        sdFlashVoltage.voltage = 3300
        sdFlashVoltage.maxVoltage = 3800
        globalVDDFMaxCurrent = self.__config.get('globalVDDFMaxCurrent')
        sdFlashVoltage.maxCurrent = int(globalVDDFMaxCurrent)
        sdFlashVoltage.regionSelect = sdcmdWrap.REGION_SELECT_PARTIAL_1V8
        sdFlashVoltage.actualVoltage = 0
        sdFlashVoltage.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ

        self.__dvtLib.setVolt(sdVolt = sdFlashVoltage, statusReg = 0, powerSupp = gvar.PowerSupply.VDDF)  # True for Flash

        # Set voltage to globalHostVoltage, Power supplier Host
        globalHostVoltage              = self.__config.get('globalHostVoltage')
        globalVDDHMaxCurrent           = self.__config.get('globalVDDHMaxCurrent')
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Volt: %d"%int(globalHostVoltage))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalVDDHMaxCurrent : %d, PowerSupply: VDDH"%int(globalVDDHMaxCurrent))
        sdFlashVoltage.voltage          = int(globalHostVoltage)
        sdFlashVoltage.maxCurrent       = int(globalVDDHMaxCurrent)

        self.__dvtLib.setVolt(sdVolt=sdFlashVoltage,statusReg=0,powerSupp=gvar.PowerSupply.VDDH)

        # Set Time Out
        self.__dvtLib.SetTimeOut(int(self.__config.get('globalResetTO')),
                                         int(self.__config.get('globalWriteTO')),
                                         int(self.__config.get('globalReadTO')))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Utility Execution Completed " + "-" * 20 + "\n")
        return 0

    # Testcase Utility Logic - Ends

# Testcase Utility Class - Ends