"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : HCSPI_V2_TC075_1_1_2_15c.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : HCSPI_V2_TC075_1_1_2_15c.py
# DESCRIPTION                    : Module to implement Cmd8, Cmd58 with or without power cycle in SPI mode
# PRERQUISTE                     : HCSPI_V2_UT001_Set_SPI_Mode_To_Drivers.py, HCSPI_V2_UT003_Get_last_response.py, HCSPI_V2_UT004_AddressForWriteRead.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=HCSPI_V2_TC075_1_1_2_15c --isModel=false --enable_console_log=1 --adapter=0
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
    from builtins import range
    from builtins import *

# SDDVT - Dependent TestCases
import HCSPI_V2_UT001_Set_SPI_Mode_To_Drivers as Set_SPI_Mode_To_Drivers
import HCSPI_V2_UT003_Get_last_response as Get_last_response
import HCSPI_V2_UT004_AddressForWriteRead as AddressForWriteRead

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
import SDDVT.Config_SD.ConfigSD_UT011_GlobalSetLSHostFreq as GlobalSetLSHostFreq
import SDDVT.Config_SD.ConfigSD_UT006_GlobalSetVolt as GlobalSetVolt

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


# Testcase Class - Begins
class HCSPI_V2_TC075_1_1_2_15c(customize_log):
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
        self.__globalSetLSHostFreq = GlobalSetLSHostFreq.globalSetLSHostFreq(self.vtfContainer)
        self.__globalSetVolt = GlobalSetVolt.globalSetVolt(self.vtfContainer)
        self.__Set_SPI_Mode_To_Drivers = Set_SPI_Mode_To_Drivers.HCSPI_V2_UT001_Set_SPI_Mode_To_Drivers(self.vtfContainer)
        self.__Get_last_response = Get_last_response.HCSPI_V2_UT003_Get_last_response(self.vtfContainer)
        self.__AddressForWriteRead = AddressForWriteRead.HCSPI_V2_UT004_AddressForWriteRead(self.vtfContainer)


    # Testcase logic - Starts
    def Run(self, globalProjectConfVar = None):
        """
        Name : Run
        Description : This test is to implement CMD8, CMD58 sequence with or without power cycle in SPI mode.
        Note: This script is not individual script.
              commands are used from DvtCommonLib.py because it requires the buffer return values from command.
              globalProjectConfVar : globalpretestingsettings module object to pass from call all file.
        """

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TEST SCRIPT IS STARTED.")

        if globalProjectConfVar == None:
            # Initialize the card
            globalProjectConfVar = self.__sdCmdObj.DoBasicInit()

        # Call Script ConfigSD_UT006_GlobalSetVolt.py
        self.__globalSetVolt.Run(globalProjectConfVar)

        # Call Script HCSPI_V2_UT001_Set_SPI_Mode_To_Drivers.py
        self.__Set_SPI_Mode_To_Drivers.Run()

        # Variable declarations
        index = random.randrange(0, 4) + 1
        globalVOLAValue = int(globalProjectConfVar['globalVOLAValue'])
        configPatternFiledInCMD8 = int(globalProjectConfVar['configPatternFiledInCMD8']) # from gloabalPreTestingSettings.py
        cmd8_arg = (globalVOLAValue << 8) | (configPatternFiledInCMD8)
        globalOCRArgSPIValue = int(self.__config.get('globalOCRArgSPIValue'))
        cmd1_a41arg = globalOCRArgSPIValue
        Yvarible = 1 # it is used in loop to execute conditional code (variable name is as per Scripter)
        cmd8_flag = 0
        globalCardVoltage = self.__config.get('globalCardVoltage')
        globalOCRResValue = int(self.__config.get('globalOCRResValue'))
        last_resp = ServiceWrap.Buffer.CreateBuffer(1, 0x00)              # variable to store the command response
        globalResetTO = int(self.__config.get('globalResetTO'))

        # Set Label Ydef1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "----------- CMD8 before CMD58 ---------")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "----------- Set Label Ydef1 ---------")

        # Label Ydef1 is started
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "LABEL Ydef1 execution is started.")

        # Issue CMD0 with argument 0
        self.__sdCmdObj.Cmd0()

        # Issue command CMD8 with argument cmd8_Arg
        self.__sdCmdObj.Cmd8(cmd8_arg)

        # Call Script HCSPI_V2_UT003_Get_last_response.py
        last_cmd_response = self.__Get_last_response.Run()

        # Compare last_cmd_response and Cmd8_arg
        if (last_cmd_response != cmd8_arg):
            raise ValidationError.TestFailError(self.fn, "Card does not support voltage range Or Incorrect response")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card supports voltage range.")

        # Issue command - CMD58 with argument as 0
        self.__sdCmdObj.Cmd58_SPI()

        # Call Script HCSPI_V2_UT003_Get_last_response.py
        last_cmd_response = self.__Get_last_response.Run()

        # Based on globalCardVoltage value, compare last_cmd_response values with globalOCRResValue
        if (globalCardVoltage == "LV"):
            if ((last_cmd_response != (globalOCRResValue & 0x00ff8080)) & (last_cmd_response != (globalOCRResValue & 0x40ff8080))):
                raise ValidationError.TestFailError(self.fn, "Card does not support voltage range.")

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card supports voltage range.")
        else:
            if ((last_cmd_response != (globalOCRResValue & 0x00ff8000)) & (last_cmd_response != (globalOCRResValue & 0x40ff8000))):
                raise ValidationError.TestFailError(self.fn, "Card does not support voltage range.")

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card supports voltage range.")

        # Issue Cmd55-with argument 0, Cmd41 - with argument as cmd1_a41arg
        self.__sdCmdObj.Cmd55()
        self.__sdCmdObj.ACmd41_SPI(cmd1_a41arg)

        # Issue CMD8 with argument as cmd8_arg
        try:
            self.__sdCmdObj.Cmd8(cmd8_arg)
        except ValidationError.CVFGenericExceptions as exc:
            self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_ILLEGAL_CMD", Operation_Name = "CMD8")
        else:
            raise ValidationError.TestFailError(self.fn, "Expected CARD_ILLEGAL_CMD failure is not occured")

        # Issue Cmd0 with argument 0
        self.__sdCmdObj.Cmd0()

        # Variable declaration
        index = random.randrange(0, 4) + 1

        # Loop for index times - Issue Cmd8 and check response
        for loop in range(0, index):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Loop count is %s, Current iteration is %s" % (index, (loop + 1)))

            # Issue Cmd8 with argument cmd8_Arg
            self.__sdCmdObj.Cmd8(cmd8_arg)

            # Call Script HCSPI_V2_UT003_Get_last_response.py
            last_cmd_response = self.__Get_last_response.Run()

            #Compare last_cmd_response and Cmd8_arg
            if (last_cmd_response != cmd8_arg):
                raise ValidationError.TestFailError(self.fn, "Incorrect command response.")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Correct command response.")

        # Issue Cmd58 with argument 0
        self.__sdCmdObj.Cmd58_SPI()

        # Call script HCSPI_V2_UT003_Get_last_response.py
        last_cmd_response = self.__Get_last_response.Run()

        # Based on globalCardVoltage value, compare last_cmd_response values with globalOCRResValue
        if (globalCardVoltage == "LV"):
            if ((last_cmd_response != (globalOCRResValue & 0x00ff8080)) & (last_cmd_response != (globalOCRResValue & 0x40ff8080))):
                raise ValidationError.TestFailError(self.fn, "Card does not support voltage range.")

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card supports voltage range.")
        else:
            if ((last_cmd_response != (globalOCRResValue & 0x00ff8000)) & (last_cmd_response != (globalOCRResValue & 0x40ff8000))):
                raise ValidationError.TestFailError(self.fn, "Card does not support voltage range.")

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card supports voltage range.")

        # Issue Cmd55-with argument 0, Cmd41 - with argument as cmd1_a41arg
        self.__sdCmdObj.Cmd55()
        self.__sdCmdObj.ACmd41_SPI(cmd1_a41arg)

        # Issue CMD8 with argument as cmd8_arg
        try:
            self.__sdCmdObj.Cmd8(cmd8_arg)
        except ValidationError.CVFGenericExceptions as exc:
            self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_ILLEGAL_CMD", Operation_Name = "CMD8")
        else:
            raise ValidationError.TestFailError(self.fn, "Expected CARD_ILLEGAL_CMD failure is not occured")

        # Card Reset in SDinSPI mode and compare with expected_ocr value
        globalOCRResValue = int(self.__config.get('globalOCRResValue'))
        self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.SD_IN_SPI, ocr=0x40000000, cardSlot=0x1, sendCmd8=True, initInfo=None,
                            rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True, bSendCMD58=True, version=0, VOLA=0x1,
                            cmdPattern=0xAA, reserved=0x0, expOCRVal=globalOCRResValue, sendCMD1 = True)

        # Call Script ConfigSD_UT011_GlobalSetLSHostFreq.py
        self.__globalSetLSHostFreq.Run()

        # Call Script HCSPI_V2_UT004_AddressForWriteRead.py - Write & Read random address with random blockcount
        self.__AddressForWriteRead.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "--------------- LABEL Ydef1 execution is completed--------------------.")

        # TAG: ********* CMD8 before CMD58 with Power Cycle *********
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "********* CMD8 before CMD58 with Power Cycle *********")

        # Code for section "CMD8 before CMD58 with Power Cycle" is started

        # Power off and on
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        # Call Script HCSPI_V2_UT001_Set_SPI_Mode_To_Drivers.py
        self.__Set_SPI_Mode_To_Drivers.Run()

        # Issue CMD0 with argument as 0
        self.__sdCmdObj.Cmd0()

        # Issue command CMD8 with argument cmd8_arg
        self.__sdCmdObj.Cmd8(cmd8_arg)

        # Call Script HCSPI_V2_UT003_Get_last_response.py
        last_cmd_response = self.__Get_last_response.Run()

        # Compare last_cmd_response and Cmd8_arg
        if (last_cmd_response != cmd8_arg):
            raise ValidationError.TestFailError(self.fn, "Card does not support voltage range.")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card supports voltage range.")

        # Issue command - CMD58
        self.__sdCmdObj.Cmd58_SPI()

        # Call Script HCSPI_V2_UT003_Get_last_response.py
        last_cmd_response = self.__Get_last_response.Run()

        # Based on globalCardVoltage value, compare last_cmd_response and globalOCRResValue
        if (globalCardVoltage == "LV"):
            if ((last_cmd_response != (globalOCRResValue & 0x00ff8080)) & (last_cmd_response != (globalOCRResValue & 0x40ff8080))):
                raise ValidationError.TestFailError(self.fn, "Card does not support voltage range.")

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card supports voltage range.")
        else:
            if ((last_cmd_response != (globalOCRResValue & 0x00ff8000)) & (last_cmd_response != (globalOCRResValue & 0x40ff8000))):
                raise ValidationError.TestFailError(self.fn, "Card does not support voltage range.")

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card supports voltage range.")

        # Issue Cmd55-with argument 0, Cmd41 - with argument as cmd1_a41arg
        self.__sdCmdObj.Cmd55()
        self.__sdCmdObj.ACmd41_SPI(cmd1_a41arg)

        # Issue CMD8 with argument as cmd8_arg
        try:
            self.__sdCmdObj.Cmd8(cmd8_arg)
        except ValidationError.CVFGenericExceptions as exc:
            self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_ILLEGAL_CMD", Operation_Name = "CMD8")
        else:
            raise ValidationError.TestFailError(self.fn, "Expected CARD_ILLEGAL_CMD failure is not occured")

        # Power off and on
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        # Call Script HCSPI_V2_UT001_Set_SPI_Mode_To_Drivers.py
        self.__Set_SPI_Mode_To_Drivers.Run()

        # Issue Cmd0 with argument 0
        self.__sdCmdObj.Cmd0()

        # Variable declaration
        index = random.randrange(0, 4) + 1

        # Loop for index times - Issue Cmd8 and check response
        for loop in range(0, index):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Loop count is %s, Current iteration is %s" % (index, (loop + 1)))

            # Issue Cmd8 with argument cmd8_Arg
            self.__sdCmdObj.Cmd8(cmd8_arg)

            # Call Script HCSPI_V2_UT003_Get_last_response.py
            last_cmd_response = self.__Get_last_response.Run()

            #Compare last_cmd_response and Cmd8_arg
            if (last_cmd_response != cmd8_arg):
                raise ValidationError.TestFailError(self.fn, "Incorrect command response.")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Correct command response.")

        # Issue Cmd58 with argument 0
        self.__sdCmdObj.Cmd58_SPI()

        # Call script HCSPI_V2_UT003_Get_last_response.py
        last_cmd_response = self.__Get_last_response.Run()

        # Based on globalCardVoltage value, compare last_cmd_response values with globalOCRResValue
        if (globalCardVoltage == "LV"):
            if ((last_cmd_response != (globalOCRResValue & 0x00ff8080)) & (last_cmd_response != (globalOCRResValue & 0x40ff8080))):
                raise ValidationError.TestFailError(self.fn, "Card does not support voltage range.")

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card supports voltage range.")
        else:
            if ((last_cmd_response != (globalOCRResValue & 0x00ff8000)) & (last_cmd_response != (globalOCRResValue & 0x40ff8000))):
                raise ValidationError.TestFailError(self.fn, "Card does not support voltage range.")

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card supports voltage range.")

        # Issue Cmd55-with argument 0, Cmd41 - with argument as cmd1_a41arg
        self.__sdCmdObj.Cmd55()
        self.__sdCmdObj.ACmd41_SPI(cmd1_a41arg)

        # Issue CMD8 with argument as cmd8_arg
        try:
            self.__sdCmdObj.Cmd8(cmd8_arg)
        except ValidationError.CVFGenericExceptions as exc:
            self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_ILLEGAL_CMD", Operation_Name = "CMD8")
        else:
            raise ValidationError.TestFailError(self.fn, "Expected CARD_ILLEGAL_CMD failure is not occured")

        # Card Reset in SDinSPI mode and compare with expected_ocr value
        globalOCRResValue = int(self.__config.get('globalOCRResValue'))
        self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.SD_IN_SPI, ocr=0x40000000, cardSlot=0x1, sendCmd8=True, initInfo=None,
                            rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True, bSendCMD58=True, version=0, VOLA=0x1,
                            cmdPattern=0xAA, reserved=0x0, expOCRVal=globalOCRResValue, sendCMD1 = True)

        # Call Script ConfigSD_UT011_GlobalSetLSHostFreq.py
        self.__globalSetLSHostFreq.Run()

        # Call Script HCSPI_V2_UT004_AddressForWriteRead.py - Write & Read random address with random blockcount
        self.__AddressForWriteRead.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-------------CMD8 before CMD58 with Power Cycle completed ----------.")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TEST SCRIPT EXECUTION IS COMPLETED.")

        return 0
    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_HCSPI_V2_TC075_1_1_2_15c(self):
        obj = HCSPI_V2_TC075_1_1_2_15c(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
