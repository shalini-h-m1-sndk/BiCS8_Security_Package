"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : HCSPI_V2_UT002_SPIResetUtility.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : HCSPI_V2_UT002_SPIResetUtility.py
# DESCRIPTION                    : Module to utility script to reset card in SPI mode
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 30-May-2024
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


# Testcase Utility Class - Begins
class HCSPI_V2_UT002_SPIResetUtility(customize_log):
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


    # Testcase utility logic - Starts
    def Run(self):
        """
        Name : Run
        Description : This test is a utility script to reset card in SPI mode
        Note: This script does not have initialization step, therefore will not execute as individual script.
              commands are used from DvtCommonLib.py because it requires the buffer return values from command.
        """

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TEST SCRIPT IS STARTED.")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*********Power Cycle Reset & CMD0 Reset*********")

        # Power off and on
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        # SET RCA
        self.__sdCmdObj.SetrelativeCardAddress()
        sdcmdWrap.SetCardRCA(0)

        # Set SD in spi card mode
        #self.__dvtLib.SetSdMmcCardMode(CardMode=3, SetMode=True)

        # Set Intial,Read,Write Time out
        otherTimeout = int(self.__config.get('globalResetTO'))
        writeTimeout = int(self.__config.get('globalWriteTO'))
        readTimeout = int(self.__config.get('globalReadTO'))

        self.__dvtLib.SetTimeOut(otherTimeout, writeTimeout, readTimeout)

        # Card Reset in SDinSPI mode and compare with expected_ocr value
        globalOCRArgSPIValue = int(self.__config.get('globalOCRArgSPIValue'))
        self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.SD_IN_SPI, ocr=globalOCRArgSPIValue, cardSlot=0x1, sendCmd8=True,
                            initInfo=None, rca=0x0, time=0x0, sendCMD0=0x1, sendCMD1 = True, bHighCapacity=True,
                            bSendCMD58=False, version=0, VOLA=0x1, cmdPattern=0xAA, reserved=0x0)

        # Set Card to High capacity, Adjust driver to HC card
        self.__dvtLib.SetCardCap(hiCap=True)

        # Run Card info
        self.__dvtLib.CardInfo()

        # Logical Write/Logical Read from 0x0 to StartAddress+0x10
        # StartAddress = 0x0
        # SectorCount = 0x10
        # tempBuffer = ServiceWrap.Buffer.CreateBuffer(0x10,0)
        # tempBuffer.FillRandom()
        # self.__dvtLib.LogicalWrite(StartAddress, SectorCount, tempBuffer)

        #Logical Read from StartAddress to StartAddress+0x1000 with data type as Random pattern
        # self.__dvtLib.LogicalRead(StartAddress, SectorCount, tempBuffer, compare = True)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TEST SCRIPT EXECUTION IS COMPLETED\n.")

        return 0
    # Testcase utility logic - Ends
# Testcase Utility Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_HCSPI_V2_UT002_SPIResetUtility(self):
        obj = HCSPI_V2_UT002_SPIResetUtility(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
