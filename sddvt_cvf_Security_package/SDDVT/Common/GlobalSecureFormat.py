"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : globalSecureFormat.st3
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : GlobalSecureFormat.py
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : GlobalSecureFormat.py
# DESCRIPTION                    : Module to implement the functionality of global secure format
# PRERQUISTE                     : Card is not locked, Card in not write protected
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 08-Sep-2022
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
    from builtins import range
    from builtins import *

# SDDVT - Common Interface for Testcase
import SDDVT.Common.DvtCommonLib as DvtCommonLib

# SDDVT - SD Specification and commands related Interface
import SDDVT.Common.SDCommandLib as SDCommandLib
import SDDVT.Common.DvtLogger as DVTLogger

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
MAX_MKB_FILES = 16


class GlobalSecureFormat(customize_log):
    """
    Class for common methods used in DVT test cases
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

        ##### Testcase Specific Variables #####
        self.__dvtlogger = DVTLogger.DvtLogger(self.vtfContainer)
        self.__genBuffer = ServiceWrap.Buffer.CreateBuffer(0x28)


    def __SetVoltage(self, voltage):
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Setting voltage to: %d" % voltage)
        try:
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_PARTIAL_1V8
            sdVolt.voltage = int(voltage * 1000)
            sdVolt.maxCurrent = 250
            sdVolt.maxVoltage = 3800 # 3.8 V
            sdVolt.actualVoltage = 0
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ

            self.__dvtLib.setVolt(sdVolt, statusReg = 0, powerSupp = gvar.PowerSupply.VDDH)

        except ValidationError.CVFGenericExceptions as exc:
            raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

    def __IgnoreCPRMLabel(self):
        """
        IgnoreCPRMLabel Method runs all operations required for GlobalSecureFormat.st3
        """

        # Set timeout for the values of configBusyResetTO, configBusyResetTO, configBusyWriteTO
        configBusytReadTO = int(self.__config.get('configBusyReadTO'))
        configBusyResetTO = int(self.__config.get('configBusyResetTO'))
        configBusyWriteTO = int(self.__config.get('configBusyWriteTO'))
        self.__dvtLib.SetTimeOut(configBusyResetTO, configBusyWriteTO, configBusytReadTO)

        # Power Off and On
        sdcmdWrap.SetPower(0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power is off")
        sdcmdWrap.SetPower(1)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power is on")

        # Set voltage 3.3
        self.__SetVoltage(voltage = 3.3)

        # Run INITCARD
        self.__sdCmdObj.INITCARD()

        # Run M-CONF
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "############ M-CONF #########")
        self.__dvtlogger.getMConfData()
        m_conf_Buffer = self.__sdCmdObj.GetMConf()

        # Buffer manipulate
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Buffer manipulate to get controller_ID")
        controller_ID = m_conf_Buffer.GetOneByteToInt(offset = 0x8)

        # Card info
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Info")
        self.__dvtLib.CardInfo()

        # Identify drive - Must get capacity from ID
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identify drive")
        self.__dvtLib.GetIdentifyDrive()

        # Write production file
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Write production file")
        self.__dvtLib.WriteProductionFile()

        # Write Hidden System file
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Write Hidden System file")
        CVF_PATH = os.getenv('SANDISK_CTF_HOME_X64')
        if not CVF_PATH:
            raise ValidationError.VtfGeneralError("Failed to Read CVF Path using SANDISK_CTF_HOME_X64 Env Variable")
        path = CVF_PATH + r"\Security\Km.bin"
        self.__dvtLib.WriteHiddenSystemFile(FilePath = path)

        # Check controller_ID > 0x20
        if (controller_ID > 0x20):
            # Indicate Secure format process
            self.__sdCmdObj.SecureFormatProcess()

        # write all 16 MKB files
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Write all 16 MKB files")
        for selector in range(0, MAX_MKB_FILES):
            self.__dvtLib.WriteMKB(selector)

        # set timeout for values 3000 mSec
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SET Timout values")
        self.__dvtLib.SetTimeOut(OtherTO = 3000, WriteTO = 3000, ReadTO = 3000)

        # Do card initialization
        self.__sdCmdObj.DoBasicInit()

    def Run(self):
        # Check for globalSpecVer and run IgnoreCPRMLabel()
        if self.__config.get('globalSpecVer') == 'eSD2.10':
            self.__IgnoreCPRMLabel()
            return 0

        # Check for globalCPRM is NonSecure
        if self.__config.get('globalCPRM') == 'NonSecure':
            return 0

        self.__IgnoreCPRMLabel()
        return 0
