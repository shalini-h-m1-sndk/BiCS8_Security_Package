"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : HCSPI_V2_TC038_1_1_2_7_1d.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : HCSPI_V2_TC038_1_1_2_7_1d.py
# DESCRIPTION                    : Module to implement Cmd8, Cmd58 with or without power cycle in SPI mode
# PRERQUISTE                     : HCSPI_V2_UT001_Set_SPI_Mode_To_Drivers.py, HCSPI_V2_UT003_Get_last_response.py, HCSPI_V2_UT004_AddressForWriteRead.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=HCSPI_V2_TC038_1_1_2_7_1d --isModel=false --enable_console_log=1 --adapter=0
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


# Testcase Class - Begins
class HCSPI_V2_TC038_1_1_2_7_1d(customize_log):
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
              globalProjectConfVar : globalpretestingsettings module object to pass from call all file.
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
        globalOCRArgSPIValue = int(self.__config.get('globalOCRArgSPIValue'))
        cmd1_a41arg = globalOCRArgSPIValue
        VOLAvalue = 0
        globalCardVoltage = self.__config.get('globalCardVoltage')

        # Set Label VOLAmismatch
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "----------- Set Label VOLAmismatch ---------")

        # Run the loop for Label VOLAmismatch 16 times (as per Scripter value for loop)
        LabelLoopSize = 16
        for loopnumber in range(0, LabelLoopSize):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "LABEL VOLAmismatch total loop is %s, Current iteration is %s." % (LabelLoopSize, (loopnumber + 1)))
            # check for value globalCardVoltage, if it is HV or LV.
            if(globalCardVoltage == "HV"):
                if (VOLAvalue == 1):
                    # Call block - function Block_mismatchCommandRun()
                    self.Block_mismatchCommandRun(VOLAvalue, cmd1_a41arg)
            elif (globalCardVoltage == "LV"):
                if VOLAvalue not in (1, 2):
                    # Call block - function Block_mismatchCommandRun()
                    self.Block_mismatchCommandRun(VOLAvalue, cmd1_a41arg)
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalCardVoltage value is neither HV nor LV, please check the config file.")


            # Increment in VOLAvalue variable for loop (Label VOLAmismatch loop will run again)
            VOLAvalue += 1
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "LABEL VOLAmismatch - Loop: %d execution is completed \n." % (loopnumber + 1))
        #End of Current loop

        # End of script
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TEST SCRIPT EXECUTION IS COMPLETED\n.")

        return 0

    def Block_mismatchCommandRun(self, VOLAValue, cmd1_a41arg):
        #TAG *********  CMD8 before CMD58 **************
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "----------- CMD8 before CMD58 ---------")

        # Variable declaration
        Yvarible = 1 #This variable is used to iterate through loop and select the condition
        globalOCRResValue = int(self.__config.get('globalOCRResValue'))

        # Set Label Ydef1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "----------- Set Label Ydef1 ---------")

        # Run the loop for Label Ydef1 three times (as per Scripter value for loop)
        LoopSize = 3
        for Loop in range(0, LoopSize):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "LABEL Ydef1 execution is started.")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Loop Ydef1 count is 3, Current iteration is %s" % (Loop + 1))

            # Issue Command - CMD0 with argument 0
            self.__sdCmdObj.Cmd0()

            # Issue command - CMD58 with argument 0
            self.__sdCmdObj.Cmd58_SPI()

            # Call script HCSPI_V2_UT003_Get_last_response.py, to get the buffer manipulated value
            last_cmd_response = self.__Get_last_response.Run()

            # Compare value of last_cmd_response and globalOCRResValue variant
            if ((last_cmd_response != (globalOCRResValue & 0x00ff8000)) & (last_cmd_response != (globalOCRResValue & 0x40ff8000))):
                raise ValidationError.TestFailError(self.fn, "Card does not support voltage range.")

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card supports voltage range.")

            # Variable declarations, required for command arguments
            reserve = random.randrange(0, 65536)
            pattern = random.randrange(0, 256)
            cmd8_arg = int((VOLAValue << 8) | (pattern) | (reserve << 12))
            cmd8_exp_resp = (VOLAValue << 8) | (pattern)
            last_cmd_response = 0 # for variable initialization

            # Issue command - CMD8 with argument cmd8_arg
            self.__sdCmdObj.Cmd8(cmd8_arg)

            # Call script HCSPI_V2_UT003_Get_last_response.py to get the buffer manipulated value
            last_cmd_response = self.__Get_last_response.Run()

            # Compare last_cmd_response  and cmd8_exp_resp
            if (last_cmd_response != cmd8_exp_resp):
                raise ValidationError.TestFailError(self.fn, "Incorrect CMD8 response")

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Correct Cmd8 response")

            # Call function Block_1_1_2_7_1d_main()
            self.Block_1_1_2_7_1d_main(Yvarible, cmd1_a41arg)

            # Increase the value of Yvarible by 1
            Yvarible += 1
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "LABEL Ydef1 execution is completed.")
        #End of Current loop

        # TAG: ********* CMD8 before CMD58 during Power Cycle & CMD0 Reset*********
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "********* CMD8 before CMD58 during Power Cycle & CMD0 Reset*********")

        # Variable declaration, and Label Ydef2
        Yvarible = 1  #This variable is used to iterate through loop and select the condition
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "----------- Set Label Ydef2 ---------")

        # Run the loop for Label Ydef2 three times (as per Scripter value for loop)
        LoopSize = 3
        for Loop in range(0, LoopSize):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "LABEL Ydef2 execution is started.")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Loop Ydef2 count is 3, Current iteration is %s" % (Loop + 1))

            # Power off and on
            sdcmdWrap.SetPower(0)
            sdcmdWrap.SetPower(1)

            # Call Script HCSPI_V2_UT001_Set_SPI_Mode_To_Drivers.py
            self.__Set_SPI_Mode_To_Drivers.Run()

            # Issue Command - CMD0 with argument 0
            self.__sdCmdObj.Cmd0()

            # Issue command - CMD58 with argument 0
            self.__sdCmdObj.Cmd58_SPI()

            # Call script HCSPI_V2_UT003_Get_last_response.py to get the buffer manipulated value
            last_cmd_response = self.__Get_last_response.Run()

            # Compare value of last_cmd_response and globalOCRResValue variant
            if ((last_cmd_response != (globalOCRResValue & 0x00ff8000)) & (last_cmd_response != (globalOCRResValue & 0x40ff8000))):
                raise ValidationError.TestFailError(self.fn, "Card does not support voltage range.")

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card supports voltage range.")

            # Variable declaration, required for commdands argument
            reserve = random.randrange(0, 65536)
            pattern = random.randrange(0, 256)
            cmd8_arg = int((VOLAValue << 8) | (pattern) | (reserve << 12))
            cmd8_exp_resp = (VOLAValue << 8) | (pattern)
            last_cmd_response = 0 # for variable initialization

            # Issue command - CMD8 with argument cmd8_arg
            self.__sdCmdObj.Cmd8(cmd8_arg)

            # Call script HCSPI_V2_UT003_Get_last_response.py to get the buffer manipulated value
            last_cmd_response = self.__Get_last_response.Run()

            # Compare last_cmd_response  and cmd8_exp_resp
            if (last_cmd_response != cmd8_exp_resp):
                raise ValidationError.TestFailError(self.fn, "Incorrect CMD8 response")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Correct CMD8 response")

            # Call function Block_1_1_2_7_1d_main()
            self.Block_1_1_2_7_1d_main(Yvarible, cmd1_a41arg)

            # Increase the value of Yvarible by 1
            Yvarible += 1
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "LABEL Ydef2 execution is completed.")
            #End of Current loop Ydef2


    def Block_1_1_2_7_1d_main(self, Yvarible, cmd1_a41arg):
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "--- Block_1_1_2_7_1d_main is started ---.")
        last_resp = ServiceWrap.Buffer.CreateBuffer(1, 0x00)

        globalResetTO = int(self.__config.get('globalResetTO'))
        globalOCRResValue = int(self.__config.get('globalOCRResValue'))

        # Check for Yvariable value and Run the loop for value globalResetTO or last_resp == 0
        if Yvarible == 1:
            for loop in range(0, globalResetTO):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Loop count is %s, Current iteration is %s" % (globalResetTO, (loop + 1)))

                # Issue Command 55 with argument 0
                self.__sdCmdObj.Cmd55()

                # Issue Cmd41 with argument cmd1_a41arg
                last_resp = self.__sdCmdObj.ACmd41_SPI(cmd1_a41arg)
                time.sleep(0.001)   # 1 milli second

                # Exit condition
                if (last_resp.GetOneByteToInt(1) == 0):
                    break   # Exit if last_resp is equal to 0

        elif Yvarible == 2:
            # Check for Yvariable == 2 value and Run the loop for value globalResetTO or last_resp == 0
            self.__sdCmdObj.Cmd55()
            last_resp = self.__sdCmdObj.ACmd41_SPI(cmd1_a41arg)   # issue command 41 with argument cmd1_a41arg
            last_response = last_resp.GetTwoBytesToInt(offset = 0)
            if (last_response != 0x100):
                raise ValidationError.TestFailError(self.fn, "Last response is not equal to 0x100")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Last response is equal to 0x100.")

            for loop in range(0, globalResetTO):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Loop count is %s, Current iteration is %s" % (globalResetTO, (loop + 1)))

                self.__sdCmdObj.Cmd55()
                last_resp = self.__sdCmdObj.ACmd41_SPI(0x00)      # issue command 41 with argument 0
                time.sleep(0.001)   # 1 milli second

                # Exit condition
                if (last_resp.GetOneByteToInt(1) == 0):
                    break   # Exit if last_resp is equal to 0

        elif Yvarible == 3:
            # Check for Yvariable == 3 value and Run the loop for value globalResetTO or last_resp == 0
            self.__sdCmdObj.Cmd55()
            last_resp = self.__sdCmdObj.ACmd41_SPI(cmd1_a41arg)   # issue command 41 with argument cmd1_a41arg
            last_response = last_resp.GetTwoBytesToInt(offset = 0)
            if (last_response != 0x100):
                raise ValidationError.TestFailError(self.fn, "Last response is not equal to 0x100")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Last response is equal to 0x100.")

            for loop in range(0, globalResetTO):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Loop count is %s, Current iteration is %s" % (globalResetTO, (loop + 1)))

                bit = random.randrange(0, 2)
                ARG = bit << 30
                self.__sdCmdObj.Cmd55()
                last_resp = self.__sdCmdObj.ACmd41_SPI(ARG)     # issue command 41 with argument ARG
                time.sleep(0.001)   # 1 milli second

                # Exit condition
                if (last_resp.GetOneByteToInt(1) == 0):
                    break   # Exit if last_resp is equal to 0

            Yvarible = 1

        # Issue Command 1 with argument cmd1_a41arg and check last_resp value (card is in Idle state or not)
        last_resp = self.__sdCmdObj.Cmd1(cmd1_a41arg)
        if (last_resp.GetTwoBytesToInt(offset = 0) != 0x0):
            raise ValidationError.TestFailError(self.fn, "Expected card in non-idle state --> instead card is in idle state")

        # Card Reset in SDinSPI mode and compare with expected_ocr value
        globalOCRResValue = int(self.__config.get('globalOCRResValue'))
        self.__dvtLib.Reset(sdcmdWrap.CARD_MODE.SD_IN_SPI, ocr=16744448, cardSlot=0x1, sendCmd8=True,
                            initInfo=None, rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True,
                            bSendCMD58=True, version=0, VOLA=0x1, cmdPattern=0xAA, reserved=0x0,
                            expOCRVal=globalOCRResValue, sendCMD1 = True)

        # Call Script ConfigSD_UT011_GlobalSetLSHostFreq.py
        self.__globalSetLSHostFreq.Run()

        # Call Script HCSPI_V2_UT004_AddressForWriteRead.py - Write & Read random address with random blockcount
        self.__AddressForWriteRead.Run()

        # Set frequency to 300 KHz
        self.__GlobalSetResetFreq.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "--- Block_1_1_2_7_1d_main is completed ---.\n")

    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_HCSPI_V2_TC038_1_1_2_7_1d(self):
        obj = HCSPI_V2_TC038_1_1_2_7_1d(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
