"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : HCSPI_V2_TC100_OCRvaluesWithCMD0DV_B.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : HCSPI_V2_TC100_OCRvaluesWithCMD0DV_B.py
# DESCRIPTION                    : Module to implement Cmd8, Cmd58 with or without power cycle in SPI mode
# PRERQUISTE                     : HCSPI_V2_UT001_Set_SPI_Mode_To_Drivers.py, HCSPI_V2_UT003_Get_last_response.py, HCSPI_V2_UT004_AddressForWriteRead.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=HCSPI_V2_TC100_OCRvaluesWithCMD0DV_B --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : Nov-2022
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
import SDDVT.Config_SD.ConfigSD_UT012_GlobalSetResetFreq as GlobalSetResetFreq

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
class HCSPI_V2_TC100_OCRvaluesWithCMD0DV_B(customize_log):
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
        self.__GlobalSetResetFreq = GlobalSetResetFreq.globalSetResetFreq(self.vtfContainer)
        self.__globalSetLSHostFreq = GlobalSetLSHostFreq.globalSetLSHostFreq(self.vtfContainer)
        self.__globalSetVolt = GlobalSetVolt.globalSetVolt(self.vtfContainer)
        self.__Set_SPI_Mode_To_Drivers = Set_SPI_Mode_To_Drivers.HCSPI_V2_UT001_Set_SPI_Mode_To_Drivers(self.vtfContainer)
        self.__Get_last_response = Get_last_response.HCSPI_V2_UT003_Get_last_response(self.vtfContainer)
        self.__AddressForWriteRead = AddressForWriteRead.HCSPI_V2_UT004_AddressForWriteRead(self.vtfContainer)


    # Testcase logic - Starts
    def Run(self, globalProjectConfVar = None):
        """
        Name : Run
        Description : This test is to perform Single commands in SPI mode.
        Note: This script does not have initialization step, therefore will not execute as individual script.
              commands are used from DvtCommonLib.py because it requires the buffer return values from command.
              globalProjectConfVar : globalpretestingsettings module object to pass from parent script.
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TEST SCRIPT IS STARTED.")

        if globalProjectConfVar == None:
            # Initialize the card
            globalProjectConfVar = self.__sdCmdObj.DoBasicInit()

        # Call Script Config_SD.ConfigSD_UT006_GlobalSetVolt.py
        self.__globalSetVolt.Run(globalProjectConfVar)

        # Call Script HCSPI_V2_UT001_Set_SPI_Mode_To_Drivers.py
        self.__Set_SPI_Mode_To_Drivers.Run()

        # Variable declarations
        globalVOLAValue = int(globalProjectConfVar['globalVOLAValue'])
        configPatternFiledInCMD8 = int(globalProjectConfVar['configPatternFiledInCMD8']) # from gloabalPreTestingSettings.py
        cmd8_arg = (globalVOLAValue << 8) | (configPatternFiledInCMD8)

        globalOCRArgSPIValue = int(self.__config.get('globalOCRArgSPIValue'))
        cmd1_a41arg = globalOCRArgSPIValue

        index = random.randrange(0, 4) + 1

        for loop_count in range(0, 2):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Main loop count is 2, Current iteration is %s" % (loop_count + 1))

            # Run label_Case_1 and Call Block_main - cmd1/cmd41 argument = globalOCRArgSPIValue
            for label_Case_1 in range(0, (index + 1)):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "label_Case_1 loop count is %s, Current iteration is %s" % ((index + 1), (label_Case_1 + 1)))

                cmd1_a41arg = globalOCRArgSPIValue
                if (loop_count == 1):
                    cmd1_a41arg &= 0xBFFFFFFF

                # Call Block_main
                self.Block_main(cmd1_a41arg, cmd8_arg, globalProjectConfVar, loop_count)

            index = random.randrange(0, 4) + 1

            # Run label_Case_2 and Call Block_main - cmd1/cmd41 argument = Random
            for label_Case_2 in range(0, (index + 1)):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "label_Case_2 loop count is %s, Current iteration is %s" % ((index + 1), (label_Case_2 + 1)))

                cmd1_a41arg = random.randrange(0, 4294967295) | 0x40000000
                if (loop_count == 1):
                    cmd1_a41arg &= 0xBFFFFFFF

                # Call Block_main
                self.Block_main(cmd1_a41arg, cmd8_arg, globalProjectConfVar, loop_count)

            index = random.randrange(0, 4) + 1

            # Run label_Case_3 and Call Block_main - cmd1/cmd41 argument = 40FF8000
            for label_Case_3 in range(0, (index + 1)):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "label_Case_3 loop count is %s, Current iteration is %s" % ((index + 1), (label_Case_3 + 1)))

                cmd1_a41arg = 0x40FF8000
                if (loop_count == 1):
                    cmd1_a41arg &= 0xBFFFFFFF

                # Call Block_main
                self.Block_main(cmd1_a41arg, cmd8_arg, globalProjectConfVar, loop_count)

            index = random.randrange(0, 4) + 1

            # Run label_Case_4 and Call Block_main - cmd1/cmd41 argument = 40FF8080
            for label_Case_4 in range(0, (index + 1)):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "label_Case_4 loop count is %s, Current iteration is %s" % ((index + 1), (label_Case_4 + 1)))

                cmd1_a41arg = 0x40FF8080
                if (loop_count == 1):
                    cmd1_a41arg &= 0xBFFFFFFF

                # Call Block_main
                self.Block_main(cmd1_a41arg, cmd8_arg, globalProjectConfVar, loop_count)

            index = random.randrange(0, 4) + 1

            # Run label_Case_5 and Call Block_main - cmd1/cmd41 argument = 40000080
            for label_Case_5 in range(0, (index + 1)):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "label_Case_5 loop count is %s, Current iteration is %s" % ((index + 1), (label_Case_5 + 1)))

                cmd1_a41arg = 0x40000080
                if (loop_count == 1):
                    cmd1_a41arg &= 0xBFFFFFFF

                # Call Block_main
                self.Block_main(cmd1_a41arg, cmd8_arg, globalProjectConfVar, loop_count)

            index = random.randrange(0, 4) + 1

            # Run label_Case_6 and Call Block_main - cmd1/cmd41 argument = FFFFFFFF
            for label_Case_6 in range(0, (index + 1)):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "label_Case_6 loop count is %s, Current iteration is %s" % ((index + 1), (label_Case_6 + 1)))

                cmd1_a41arg = 0xFFFFFFFF
                if (loop_count == 1):
                    cmd1_a41arg &= 0xBFFFFFFF

                # Call Block_main
                self.Block_main(cmd1_a41arg, cmd8_arg, globalProjectConfVar, loop_count)

        #End of script
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TEST SCRIPT EXECUTION IS COMPLETED\n.")

        return 0

    def Block_main(self, cmd1_a41arg, cmd8_arg, globalProjectConfVar, loop_count):

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Block_main is started.")

        # Variable declarations
        globalVOLAValue = int(globalProjectConfVar['globalVOLAValue'])
        configPatternFiledInCMD8 = int(globalProjectConfVar['configPatternFiledInCMD8'])
        globalResetTO = int(self.__config.get('globalResetTO'))
        globalOCRResValue = int(self.__config.get('globalOCRResValue'))

        # Issue Command - CMD0 with argument 0
        self.__sdCmdObj.Cmd0() # default argument is 0

        # Issue command - CMD58, with argument 0
        self.__sdCmdObj.Cmd58_SPI()     # default argument is 0

        # Call script HCSPI_V2_UT003_Get_last_response.py
        last_cmd_response = self.__Get_last_response.Run()

        # Compare value of last_cmd_response with globalOCRResValue variation
        if ((last_cmd_response != (globalOCRResValue & 0x00ff8000)) & (last_cmd_response != (globalOCRResValue & 0x40ff8000))):
            raise ValidationError.TestFailError(self.fn, "Card does not support voltage range.")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card supports voltage range.")

        # Issue Command 8
        self.__sdCmdObj.Cmd8(cmd8_arg)

        # Call script HCSPI_V2_UT003_Get_last_response.py
        last_cmd_response = self.__Get_last_response.Run()

        # Compare last_cmd_response and Cmd8_arg
        if (last_cmd_response != cmd8_arg):
            raise ValidationError.TestFailError(self.fn, "Card does not support voltage range! --- Or incorrect response")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card supports voltage range! --- Or correct response")

        # Issue command - CMD58,
        self.__sdCmdObj.Cmd58_SPI()

        # Call script HCSPI_V2_UT003_Get_last_response.py
        last_cmd_response = self.__Get_last_response.Run()

        if ((last_cmd_response != (globalOCRResValue & 0x00ff8000)) & (last_cmd_response != (globalOCRResValue & 0x40ff8000))):
            raise ValidationError.TestFailError(self.fn, "Card does not support voltage range.")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card supports voltage range.")

        # Run the loop for value globalResetTO or last_resp == 0
        for loop in range(0, globalResetTO):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Loop count is %s, Current iteration is %s" % (globalResetTO, (loop + 1)))

            self.__sdCmdObj.Cmd55()
            last_resp = self.__sdCmdObj.ACmd41_SPI(cmd1_a41arg)

            # Exit condition
            if (last_resp.GetOneByteToInt(1) == 0):
                break   # Exit if last_resp is equal to 0

        # Issue command - CMD58
        if loop_count == 1:
            try:
                self.__sdCmdObj.Cmd58_SPI()
            except ValidationError.CVFGenericExceptions as exc:
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_ILLEGAL_CMD", Operation_Name = "Cmd58_SPI")
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_ILLEGAL_CMD failure is not occured")
        else:
            self.__sdCmdObj.Cmd58_SPI()

        # Call script HCSPI_V2_UT003_Get_last_response.py
        last_cmd_response = self.__Get_last_response.Run()

        if ((cmd1_a41arg & 0x40000000) != 0):
            if (last_cmd_response != globalOCRResValue):
                # Card does not support voltage range! --- OR card did not complete init
                raise ValidationError.TestFailError(self.fn, "Card does not support voltage range! --- OR card did not complete init")

            # Call Script ConfigSD_UT011_GlobalSetLSHostFreq.py
            self.__globalSetLSHostFreq.Run()

            # Call Script HCSPI_V2_UT004_AddressForWriteRead.py - Write & Read random address with random blockcount
            self.__AddressForWriteRead.Run()

            # Set frequency to 300 KHz
            self.__GlobalSetResetFreq.Run()

        else:
            if ((last_resp.GetTwoBytesToInt(offset = 0) & 0x5) != 5):
                raise ValidationError.TestFailError(self.fn,  "Card does not support voltage range!")

            # Card Reset in SDinSPI mode and compare with expected_ocr value
            globalOCRResValue = int(self.__config.get('globalOCRResValue'))
            self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.SD_IN_SPI, ocr=0xFF8000, cardSlot=0x1, sendCmd8=True,
                                initInfo=None, rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True,
                                bSendCMD58=True, version=0, VOLA=globalVOLAValue, cmdPattern=configPatternFiledInCMD8, reserved=0x0,
                                expOCRVal=globalOCRResValue, sendCMD1 = True)

            # Call Script ConfigSD_UT011_GlobalSetLSHostFreq.py
            self.__globalSetLSHostFreq.Run()

            # Call Script HCSPI_V2_UT004_AddressForWriteRead.py - Write & Read random address with random blockcount
            self.__AddressForWriteRead.Run()

            # Set frequency to 300 KHz
            self.__GlobalSetResetFreq.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Block_main is started.")

    #End of block Block_main()

    # Testcase Logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_HCSPI_V2_TC100_OCRvaluesWithCMD0DV_B(self):
        obj = HCSPI_V2_TC100_OCRvaluesWithCMD0DV_B(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
