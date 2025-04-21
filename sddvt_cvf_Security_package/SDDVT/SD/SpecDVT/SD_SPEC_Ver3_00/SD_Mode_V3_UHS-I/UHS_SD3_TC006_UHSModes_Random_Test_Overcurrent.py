"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : UHS_SD3_TC006_UHSModes_Random_Test_Overcurrent.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : UHS_SD3_TC006_UHSModes_Random_Test_Overcurrent.py
# DESCRIPTION                    : The purpose of this test case is to test over current random test in UHS mode.
# PRERQUISTE                     : UHS_SD3_UT01_LoadLocal_Variables.py, UHS_SD3_UT03_Successful_Verify.py, UHS_SD3_UT04_SuccessfulVerify_MaxVoltage.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=UHS_SD3_TC006_UHSModes_Random_Test_Overcurrent --isModel=false --enable_console_log=1 --adapter=0
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
    from builtins import str
    from builtins import range
    from builtins import *

# SDDVT - Dependent TestCases
import UHS_SD3_UT01_LoadLocal_Variables as LoadLocalVariables
import UHS_SD3_UT03_Successful_Verify as Successful_Verify
import UHS_SD3_UT04_SuccessfulVerify_MaxVoltage as SuccessfulVerify_MaxVoltage

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
import SDDVT.Config_SD.ConfigSD_UT005_GlobalPreTestingSettings as globalPreTestingSettings

# CVF Packages
import PatternGen
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
class UHS_SD3_TC006_UHSModes_Random_Test_Overcurrent(customize_log):
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
        self.__globalPreTestSettingsObj = globalPreTestingSettings.globalPreTestingSettings(self.vtfContainer)
        self.__LoadLocal_Variables = LoadLocalVariables.UHS_SD3_UT01_LoadLocal_Variables(self.vtfContainer)
        self.__Successful_Verify = Successful_Verify.UHS_SD3_UT03_Successful_Verify(self.vtfContainer)
        self.__SuccessfulVerify_MaxVoltage = SuccessfulVerify_MaxVoltage.UHS_SD3_UT04_SuccessfulVerify_MaxVoltage(self.vtfContainer)


    # Testcase logic - Starts
    def block_1(self, LocalVariables):

        LocalVariables['SendCMD0'] = random.randrange(0, 2)

        # Poweroff
        sdcmdWrap.SetPower(0)

        # Set Volt
        sdVolt = sdcmdWrap.SVoltage()
        sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
        sdVolt.voltage = 3300 # 3.30 V
        sdVolt.maxCurrent = 200 #For VDDH
        sdVolt.maxVoltage = 3800
        sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ # 250 Hz
        statusReg = 0
        bVddfValue = gvar.PowerSupply.VDDH
        self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

        LocalVariables['MAX_CURRENT'] = 200

        # Poweron
        sdcmdWrap.SetPower(1)

        # Do card Reset
        self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=LocalVariables['HcsXpcS18r111'], cardSlot=0x1, sendCmd8=True,
                            initInfo=None, rca=0x0, time=0x0, sendCMD0=LocalVariables['SendCMD0'], bHighCapacity=True,
                            bSendCMD58=False, version=0x0, VOLA=1, cmdPattern=0xAA, reserved=0x0,
                            expOCRVal=LocalVariables['ReadyCcs18a111'])

        # SwitchVolt_CMD11
        self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)

        # Identify Card
        self.__dvtLib.Identification()

        # Select card
        self.__sdCmdObj.Cmd7()

        # Set BusWidth = 4
        self.__dvtLib.SetBusWidth(busWidth=4)

        # Variable Declaration
        LocalVariables["UHS_MODE_EX"] = LocalVariables['UHS_MODE']
        LocalVariables['UHS_MODE'] = 0

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Block_1\n")

    # End of block_1
    def block_2(self, LocalVariables):
        LocalVariables['RANDOM_S18R'] = random.randrange(0, 2)
        if LocalVariables['RANDOM_S18R'] == 0:
            LocalVariables['RANDOM_S18R'] = LocalVariables['HcsXpcS18r110']
        if LocalVariables['RANDOM_S18R'] == 1:
            LocalVariables['RANDOM_S18R'] = LocalVariables['HcsXpcS18r101']

        # Do card Reset
        self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=LocalVariables['RANDOM_S18R'], cardSlot=0x1, sendCmd8=True,
                            initInfo=None, rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True, bSendCMD58=False,
                            version=0x0, VOLA=1, cmdPattern=0xAA, reserved=0x0, expOCRVal=LocalVariables['ReadyCcs18a110'])


        # Identify Card
        self.__dvtLib.Identification()

        # Select card
        self.__sdCmdObj.Cmd7()

        # Set BusWidth = 4
        self.__dvtLib.SetBusWidth(busWidth=4)

        # Variable Declaration
        LocalVariables["UHS_MODE_EX"] = LocalVariables['UHS_MODE']
        LocalVariables['UHS_MODE'] = 0

        # Switch command
        # Variable Declaration for support
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VS_Flag========================%s"% str(LocalVariables['VS_FLAG']))
        supported = LocalVariables["listData"]
        supported[1] = supported[1] & ((0x4000 * LocalVariables['VS_FLAG']) + 0xBFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "supported========================%s"% str(supported))

        # Call Switch Command for check mode / Check, Expected Status Available
        mode = gvar.CMD6.CHECK
        blockSize = 0x40
        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
        switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x0,0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_NONE
        self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                        responseCompare=responseCompare,
                                        compareConsumption=consumption,
                                        compareSupported=supported,
                                        comparedSwitched=switched)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Block_2\n")
        # End of block_2

    def block_3(self, LocalVariables):
        if ((LocalVariables['UHS_MODE'] == 0x2) or (LocalVariables['UHS_MODE'] == 0x3)):
            #Send tuning pattern
            numOfCmd = random.randrange(0, 40) + 1
            timeOut = 150
            bufferError = ServiceWrap.Buffer.CreateBuffer(1, 0)
            self.__dvtLib.SEND_TUNING_PATTERN(numOfCmd, timeOut, bufferError)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Block_3\n")
        # End of block_3

    def block_4(self, LocalVariables):
        # Variable Declaration
        LocalVariables['RANDOM_UHS_MODE'] = random.randrange(0, LocalVariables['RANDOM_MODES'])

        if LocalVariables['RANDOM_UHS_MODE'] == 0:
            LocalVariables['UHS_MODE'] = 0x0
            LocalVariables['UHS_DRIVE'] = 0x0
            LocalVariables['UHS_CURRENT'] = 0x0
            LocalVariables['SWITCH_CONSUMPTION'] = 100
            LocalVariables['CHECK_CONSUMPTION'] = 100
            SET_FREQ = random.randrange(0, 15000) + 10000
            LocalVariables['TRANSFER_RATE'] = 0x32

            # Set Volt - over current change
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 200 #For VDDH
            sdVolt.maxVoltage = 3800
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ # 250 Hz
            statusReg = 0
            bVddfValue = gvar.PowerSupply.VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            LocalVariables['MAX_CURRENT'] = 200 # over current change

            if ((LocalVariables['CARD_CAPACITY'] >= 64) and (LocalVariables['SendOCR'] == LocalVariables['HcsXpcS18r111'])):
                # Set Volt
                sdVolt = sdcmdWrap.SVoltage()
                sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
                sdVolt.voltage = 3300 # 3.30 V
                sdVolt.maxCurrent = 150 #For VDDH
                sdVolt.maxVoltage = 3300
                sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 62.5 Hz
                statusReg = 0
                bVddfValue = gvar.PowerSupply.VDDH
                self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

                LocalVariables['MAX_CURRENT'] = 150

        if LocalVariables['RANDOM_UHS_MODE'] == 1:
            LocalVariables['UHS_MODE'] = 0x1
            LocalVariables['UHS_DRIVE'] = 0x0
            LocalVariables['UHS_CURRENT'] = 0x0
            LocalVariables['SWITCH_CONSUMPTION'] = 200
            LocalVariables['CHECK_CONSUMPTION'] = 200
            SET_FREQ = random.randrange(0, 25000) + 25000
            LocalVariables['TRANSFER_RATE'] = 0x5A

            # Set Volt - over current change
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 200 #For VDDH
            sdVolt.maxVoltage = 3800
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ
            statusReg = 0
            bVddfValue = gvar.PowerSupply.VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            LocalVariables['MAX_CURRENT'] = 200 # over current change

        if LocalVariables['RANDOM_UHS_MODE'] == 2:
            LocalVariables['UHS_MODE'] = 0x2
            LocalVariables['UHS_DRIVE'] = 0x0
            LocalVariables['UHS_CURRENT'] = 0x1
            LocalVariables['SWITCH_CONSUMPTION'] = 250
            LocalVariables['CHECK_CONSUMPTION'] = 250
            SET_FREQ = random.randrange(0, 30000) + 70000
            LocalVariables['TRANSFER_RATE'] = 0xB

            # Set Volt - over current change
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 250 #For VDDH
            sdVolt.maxVoltage = 3800
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ
            statusReg = 0
            bVddfValue = gvar.PowerSupply.VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            LocalVariables['MAX_CURRENT'] = 250 # over current change

        if LocalVariables['RANDOM_UHS_MODE'] == 3:
            LocalVariables['UHS_MODE'] = 0x4
            LocalVariables['UHS_DRIVE'] = 0x0
            LocalVariables['UHS_CURRENT'] = 0x1
            LocalVariables['SWITCH_CONSUMPTION'] = 250
            LocalVariables['CHECK_CONSUMPTION'] = 250
            SET_FREQ = random.randrange(0, 25000) + 25000
            LocalVariables['TRANSFER_RATE'] = 0xB

            # Set Volt - over current change
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 250 #For VDDH
            sdVolt.maxVoltage = 3800
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ
            statusReg = 0
            bVddfValue = gvar.PowerSupply.VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            LocalVariables['MAX_CURRENT'] = 250 # over current change

        if LocalVariables['RANDOM_UHS_MODE'] == 4:
            LocalVariables['UHS_MODE'] = 0x3
            LocalVariables['UHS_DRIVE'] = 0x1
            LocalVariables['UHS_CURRENT'] = 0x1
            LocalVariables['SWITCH_CONSUMPTION'] = 250
            LocalVariables['CHECK_CONSUMPTION'] = 250
            SET_FREQ = random.randrange(0, 2)   # SET_FREQ = 200MHz / 150MHz
            if SET_FREQ == 0:
                SET_FREQ = 200000
            else:
                SET_FREQ = 150000

            LocalVariables['TRANSFER_RATE'] = 0x2B

            # Set Volt - over current change
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 280 #For VDDH
            sdVolt.maxVoltage = 3800
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ
            statusReg = 0
            bVddfValue = gvar.PowerSupply.VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            LocalVariables['MAX_CURRENT'] = 280 # over current change

        if LocalVariables['UHS_MODE'] == 0x0:
            # Set Frequency
            self.__sdCmdObj.SetFrequency(SET_FREQ)

        # Switch Command
        # Variable Declaration for support
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VS_Flag========================%s"% str(LocalVariables['VS_FLAG']))
        supported = LocalVariables["listData"]
        supported[1] = supported[1] & ((0x4000 * LocalVariables['VS_FLAG']) + 0xBFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "supported========================%s"% str(supported))

        # Call Switch Command for check mode / Check, Expected Status Available
        mode = gvar.CMD6.SWITCH
        arglist = [LocalVariables['UHS_MODE'],0xF,LocalVariables['UHS_DRIVE'],LocalVariables['UHS_CURRENT'],0xF,0xF]
        blockSize = 0x40
        switched = [LocalVariables['UHS_MODE'],0x0,LocalVariables['UHS_DRIVE'],LocalVariables['UHS_CURRENT'],0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for Match to Value = 2
        self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                        responseCompare=responseCompare,
                                        compareConsumption=consumption,
                                        compareValue=LocalVariables['SWITCH_CONSUMPTION'],
                                        compareSupported=supported,
                                        comparedSwitched=switched)
        # set Frequency
        self.__sdCmdObj.SetFrequency(SET_FREQ)

        # Call Switch Command for check mode / Check, Expected Status Available
        mode = gvar.CMD6.CHECK
        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
        blockSize = 0x40
        switched = [LocalVariables['UHS_MODE'],0x0,LocalVariables['UHS_DRIVE'],LocalVariables['UHS_CURRENT'],0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for Match to Value = 2
        self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                        responseCompare=responseCompare,
                                        compareConsumption=consumption,
                                        compareValue=LocalVariables['CHECK_CONSUMPTION'],
                                        compareSupported=supported,
                                        comparedSwitched=switched)


        # Get CSD Values
        csd_value = self.__sdCmdObj.GET_CSD_VALUES()

        if LocalVariables["TRANSFER_RATE"] != int(csd_value["TRAN_SPEED"].lower(), 16):
            raise ValidationError.TestFailError(self.fn, "Transfer speed not matched. Expected is %s, Read from card is %s" % (LocalVariables["TRANSFER_RATE"], csd_value["TRAN_SPEED"].lower()))

        # Select card
        self.__sdCmdObj.Cmd7()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Block block_4")
    # End of Block block_4

    def block_5(self, LocalVariables):
        # Variable Declaration
        LocalVariables['RANDOM_UHS_MODE'] = random.randrange(0, LocalVariables['RANDOM_MODES'])
        if LocalVariables['RANDOM_UHS_MODE'] == 0:
            LocalVariables['UHS_MODE'] = 0x0
            LocalVariables['UHS_DRIVE'] = 0x0
            LocalVariables['UHS_CURRENT'] = 0x0
            LocalVariables['SWITCH_CONSUMPTION'] = 100
            LocalVariables['CHECK_CONSUMPTION'] = 100
            SET_FREQ = random.randrange(0, 15000) + 10000
            LocalVariables['TRANSFER_RATE'] = 0x32

            # Set Volt
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 200 #For VDDH
            sdVolt.maxVoltage = 3800
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ # 250 Hz
            statusReg = 0
            bVddfValue = gvar.PowerSupply.VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            LocalVariables['MAX_CURRENT'] = 200

            if ((LocalVariables['CARD_CAPACITY'] >= 64) and (LocalVariables['SendOCR'] == LocalVariables['HcsXpcS18r111'])):
                # Set Volt
                sdVolt = sdcmdWrap.SVoltage()
                sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
                sdVolt.voltage = 3300 # 3.30 V
                sdVolt.maxCurrent = 150 #For VDDH
                sdVolt.maxVoltage = 3300
                sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 62.5 Hz
                statusReg = 0
                bVddfValue = gvar.PowerSupply.VDDH
                self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

                LocalVariables['MAX_CURRENT'] = 150

        if LocalVariables['RANDOM_UHS_MODE'] == 1:
            LocalVariables['UHS_MODE'] = 0x1
            LocalVariables['UHS_DRIVE'] = 0x0
            LocalVariables['UHS_CURRENT'] = 0x0
            LocalVariables['SWITCH_CONSUMPTION'] = 200
            LocalVariables['CHECK_CONSUMPTION'] = 200
            #Set SET_FREQ = rand%25000 + 25000
            SET_FREQ = random.randrange(0, 25000) + 25000
            LocalVariables['TRANSFER_RATE'] = 0x5A

            # Set Volt - over current change
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 200 #For VDDH
            sdVolt.maxVoltage = 3800
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ
            statusReg = 0
            bVddfValue = gvar.PowerSupply.VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            LocalVariables['MAX_CURRENT'] = 200 # over current change

        if LocalVariables['RANDOM_UHS_MODE'] == 2:
            LocalVariables['UHS_MODE'] = 0x2
            LocalVariables['UHS_DRIVE'] = 0x0
            LocalVariables['UHS_CURRENT'] = 0x1
            LocalVariables['SWITCH_CONSUMPTION'] = 250
            LocalVariables['CHECK_CONSUMPTION'] = 250
            SET_FREQ = random.randrange(0, 30000) + 70000
            LocalVariables['TRANSFER_RATE'] = 0xB

            # Set Volt - over current change
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 250 #For VDDH
            sdVolt.maxVoltage = 3800
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ
            statusReg = 0
            bVddfValue = gvar.PowerSupply.VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            LocalVariables['MAX_CURRENT'] = 250 # over current change

        if LocalVariables['RANDOM_UHS_MODE'] == 3:
            LocalVariables['UHS_MODE'] = 0x4
            LocalVariables['UHS_DRIVE'] = 0x0
            LocalVariables['UHS_CURRENT'] = 0x1
            LocalVariables['SWITCH_CONSUMPTION'] = 250
            LocalVariables['CHECK_CONSUMPTION'] = 250
            SET_FREQ = random.randrange(0, 25000) + 25000
            LocalVariables['TRANSFER_RATE'] = 0xB

            # Set Volt - over current change
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 250 #For VDDH
            sdVolt.maxVoltage = 3800
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ
            statusReg = 0
            bVddfValue = gvar.PowerSupply.VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            LocalVariables['MAX_CURRENT'] = 250 # over current change

        if LocalVariables['RANDOM_UHS_MODE'] == 4:
            LocalVariables['UHS_MODE'] = 0x3
            LocalVariables['UHS_DRIVE'] = 0x1
            LocalVariables['UHS_CURRENT'] = 0x1
            LocalVariables['SWITCH_CONSUMPTION'] = 250
            LocalVariables['CHECK_CONSUMPTION'] = 250

            SET_FREQ = random.randrange(0, 2)
            if SET_FREQ == 0:
                SET_FREQ = 200000
            else:
                SET_FREQ = 150000

            LocalVariables['TRANSFER_RATE'] = 0x2B

            # Set Volt
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 280 #For VDDH
            sdVolt.maxVoltage = 3800
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ
            statusReg = 0
            bVddfValue = gvar.PowerSupply.VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            LocalVariables['MAX_CURRENT'] = 280

        # Variable Declaration
        LocalVariables['DRIVER_STRENGTH'] = LocalVariables['UHS_DRIVE']

        if LocalVariables['UHS_MODE'] == 0x0:
            # Set Frequency
            self.__sdCmdObj.SetFrequency(SET_FREQ)

        # Switch Command
        # Variable Declaration for support
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VS_Flag========================%s"% str(LocalVariables['VS_FLAG']))
        supported = LocalVariables["listData"]
        supported[1] = supported[1] & ((0x4000 * LocalVariables['VS_FLAG']) + 0xBFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "supported========================%s"% str(supported))

        # Call Switch Command for check mode / Check, Expected Status Available
        mode = gvar.CMD6.SWITCH
        arglist = [LocalVariables['UHS_MODE'],0xF,LocalVariables['DRIVER_STRENGTH'],LocalVariables['UHS_CURRENT'],0xF,0xF]
        blockSize = 0x40
        switched = [LocalVariables['UHS_MODE'],0x0,LocalVariables['UHS_DRIVE'],LocalVariables['UHS_CURRENT'],0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for Match to Value = 2
        self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                        responseCompare=responseCompare,
                                        compareConsumption=consumption,
                                        compareValue=LocalVariables['SWITCH_CONSUMPTION'],
                                        compareSupported=supported,
                                        comparedSwitched=switched)
        # set Frequency
        self.__sdCmdObj.SetFrequency(SET_FREQ)

        # Call Switch Command for check mode / Check, Expected Status Available
        mode = gvar.CMD6.CHECK
        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
        blockSize = 0x40
        switched = [LocalVariables['UHS_MODE'],0x0,LocalVariables['UHS_DRIVE'],LocalVariables['UHS_CURRENT'],0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for Match to Value = 2
        self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                        responseCompare=responseCompare,
                                        compareConsumption=consumption,
                                        compareValue=LocalVariables['CHECK_CONSUMPTION'],
                                        compareSupported=supported,
                                        comparedSwitched=switched)

        # Get CSD Values
        csd_value = self.__sdCmdObj.GET_CSD_VALUES()
        if LocalVariables["TRANSFER_RATE"] != int(csd_value["TRAN_SPEED"].lower(), 16):
            raise ValidationError.TestFailError(self.fn, "Transfer speed not matched. Expected is %s, Read from card is %s" % (LocalVariables["TRANSFER_RATE"], csd_value["TRAN_SPEED"].lower()))

        # Select card
        self.__sdCmdObj.Cmd7()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Block block_5")
    # End Block block_5

    def block_6(self, LocalVariables):
        # Variable Declaration
        LocalVariables['RANDOM_UHS_MODE'] = random.randrange(0, LocalVariables['RANDOM_MODES'])
        if LocalVariables['RANDOM_UHS_MODE'] == 0:
            LocalVariables['UHS_MODE'] = 0x0
            LocalVariables['UHS_DRIVE'] = 0x0
            LocalVariables['UHS_CURRENT'] = 0x0
            LocalVariables['SWITCH_CONSUMPTION'] = 100
            LocalVariables['CHECK_CONSUMPTION'] = 100
            SET_FREQ = random.randrange(0, 15000) + 10000
            LocalVariables['TRANSFER_RATE'] = 0x32

            # Set Volt
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 200 #For VDDH
            sdVolt.maxVoltage = 3800
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ # 250 Hz
            statusReg = 0
            bVddfValue = gvar.PowerSupply.VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            LocalVariables['MAX_CURRENT'] = 200

            if ((LocalVariables['CARD_CAPACITY'] >= 64) and (LocalVariables['SendOCR'] == LocalVariables['HcsXpcS18r111'])):
                # Set Volt
                sdVolt = sdcmdWrap.SVoltage()
                sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
                sdVolt.voltage = 3300 # 3.30 V
                sdVolt.maxCurrent = 150 #For VDDH
                sdVolt.maxVoltage = 3300
                sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 62.5 Hz
                statusReg = 0
                bVddfValue = gvar.PowerSupply.VDDH
                self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

                LocalVariables['MAX_CURRENT'] = 150

        if LocalVariables['RANDOM_UHS_MODE'] == 1:
            LocalVariables['UHS_MODE'] = 0x1
            LocalVariables['UHS_DRIVE'] = 0x0
            LocalVariables['UHS_CURRENT'] = 0x0
            LocalVariables['SWITCH_CONSUMPTION'] = 200
            LocalVariables['CHECK_CONSUMPTION'] = 200
            SET_FREQ = random.randrange(0, 25000) + 25000
            LocalVariables['TRANSFER_RATE'] = 0x5A

            # Set Volt - over current change
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 200 #For VDDH
            sdVolt.maxVoltage = 3800
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ
            statusReg = 0
            bVddfValue = gvar.PowerSupply.VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            LocalVariables['MAX_CURRENT'] = 200 # over current change

        if LocalVariables['RANDOM_UHS_MODE'] == 2:
            LocalVariables['UHS_MODE'] = 0x2
            LocalVariables['UHS_DRIVE'] = 0x0
            LocalVariables['UHS_CURRENT'] = 0x1
            LocalVariables['SWITCH_CONSUMPTION'] = 250
            LocalVariables['CHECK_CONSUMPTION'] = 250
            SET_FREQ = random.randrange(0, 30000) + 70000
            LocalVariables['TRANSFER_RATE'] = 0xB

            # Set Volt
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 250 #For VDDH
            sdVolt.maxVoltage = 3800
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ
            statusReg = 0
            bVddfValue = gvar.PowerSupply.VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            LocalVariables['MAX_CURRENT'] = 250

        if LocalVariables['RANDOM_UHS_MODE'] == 3:  # DDR50
            LocalVariables['UHS_MODE'] = 0x4
            LocalVariables['UHS_DRIVE'] = 0x0
            LocalVariables['UHS_CURRENT'] = 0x1
            LocalVariables['SWITCH_CONSUMPTION'] = 250
            LocalVariables['CHECK_CONSUMPTION'] = 250
            SET_FREQ = random.randrange(0, 25000) + 25000
            LocalVariables['TRANSFER_RATE'] = 0xB

            supported = LocalVariables["listData"]

            if (supported[3] >= 0x8003):    # sync the host only if card is set
                # Set Volt
                sdVolt = sdcmdWrap.SVoltage()
                sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
                sdVolt.voltage = 3300 # 3.30 V
                sdVolt.maxCurrent = 250 #For VDDH
                sdVolt.maxVoltage = 3300
                sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 62.5 Hz
                statusReg = 0
                bVddfValue = gvar.PowerSupply.VDDH
                self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            LocalVariables['MAX_CURRENT'] = 250 # SDR25

        if LocalVariables['RANDOM_UHS_MODE'] == 4:  # SDR104
            LocalVariables['UHS_MODE'] = 0x3
            LocalVariables['UHS_DRIVE'] = 0x1
            LocalVariables['UHS_CURRENT'] = 0x1
            LocalVariables['SWITCH_CONSUMPTION'] = 250
            LocalVariables['CHECK_CONSUMPTION'] = 250
            SET_FREQ = random.randrange(0, 2)
            if SET_FREQ == 0:
                SET_FREQ = 200000
            else:
                SET_FREQ = 150000

            LocalVariables['TRANSFER_RATE'] = 0x2B

            # Set Volt - over current change
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 280 #For VDDH
            sdVolt.maxVoltage = 3800
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ
            statusReg = 0
            bVddfValue = gvar.PowerSupply.VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            LocalVariables['MAX_CURRENT'] = 280 # over current change

        if LocalVariables['UHS_MODE'] < 2:
            LocalVariables['CURRENT_LIMIT'] = 0x0

        if LocalVariables['UHS_MODE'] >= 0x2:
            LocalVariables['RANDOM_CURRENT_LIMIT'] = random.randrange(0, 2)

            if LocalVariables['RANDOM_CURRENT_LIMIT'] == 0:
                LocalVariables['CURRENT_LIMIT'] = 0x0
                LocalVariables['SWITCH_CONSUMPTION'] = 200

            if LocalVariables['RANDOM_CURRENT_LIMIT'] == 1:
                LocalVariables['CURRENT_LIMIT'] = 0x1
                LocalVariables['SWITCH_CONSUMPTION'] = 250

                # Set Volt
                sdVolt = sdcmdWrap.SVoltage()
                sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
                sdVolt.voltage = 3300 # 3.30 V
                sdVolt.maxCurrent = 250 #For VDDH
                sdVolt.maxVoltage = 3300
                sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 62.5 Hz
                statusReg = 0
                bVddfValue = gvar.PowerSupply.VDDH
                self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

                LocalVariables['MAX_CURRENT'] = 250

        if LocalVariables['UHS_MODE'] == 0x0:
            # Set Frequency
            self.__sdCmdObj.SetFrequency(SET_FREQ)

        # Switch Command
        # Variable Declaration for support
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VS_Flag========================%s"% str(LocalVariables['VS_FLAG']))
        supported = LocalVariables["listData"]
        supported[1] = supported[1] & ((0x4000 * LocalVariables['VS_FLAG']) + 0xBFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "supported========================%s"% str(supported))

        # Call Switch Command for check mode / Check, Expected Status Available
        mode = gvar.CMD6.SWITCH
        arglist = [LocalVariables['UHS_MODE'],0xF,LocalVariables['UHS_DRIVE'],LocalVariables['CURRENT_LIMIT'],0xF,0xF]
        blockSize = 0x40
        switched = [LocalVariables['UHS_MODE'],0x0,LocalVariables['UHS_DRIVE'],LocalVariables['CURRENT_LIMIT'],0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for Match to Value = 2
        self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                        responseCompare=responseCompare,
                                        compareConsumption=consumption,
                                        compareValue=LocalVariables['SWITCH_CONSUMPTION'],
                                        compareSupported=supported,
                                        comparedSwitched=switched)
        # set Frequency
        self.__sdCmdObj.SetFrequency(SET_FREQ)

        # Call Switch Command for check mode / Check, Expected Status Available
        mode = gvar.CMD6.CHECK
        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
        blockSize = 0x40
        switched = [LocalVariables['UHS_MODE'],0x0,LocalVariables['UHS_DRIVE'],LocalVariables['CURRENT_LIMIT'],0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for Match to Value = 2
        self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                        responseCompare=responseCompare,
                                        compareConsumption=consumption,
                                        compareValue=LocalVariables['CHECK_CONSUMPTION'],
                                        compareSupported=supported,
                                        comparedSwitched=switched)

        # Get CSD Values
        csd_value = self.__sdCmdObj.GET_CSD_VALUES()
        if LocalVariables["TRANSFER_RATE"] != int(csd_value["TRAN_SPEED"].lower(), 16):
            raise ValidationError.TestFailError(self.fn, "Transfer speed not matched. Expected is %s, Read from card is %s" % (LocalVariables["TRANSFER_RATE"], csd_value["TRAN_SPEED"].lower()))

        # Select card
        self.__sdCmdObj.Cmd7()

        # Call Utility_Successful_Verify
        self.__Successful_Verify.Run()

        # Call Script Utility_Successful_Verify_MaxVoltage
        self.__SuccessfulVerify_MaxVoltage.Run()

        # Call Block block_1
        self.block_1(LocalVariables)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Block block_6")
    # End Block block_6

    def block_7(self, LocalVariables):
        # Variable Declaration
        LocalVariables['RANDOM_UHS_MODE'] = random.randrange(0, LocalVariables['RANDOM_MODES'])
        if LocalVariables['RANDOM_UHS_MODE'] == 0:  # SDR12
            LocalVariables['UHS_MODE'] = 0x0
            LocalVariables['UHS_DRIVE'] = 0x0
            LocalVariables['UHS_CURRENT'] = 0x0
            LocalVariables['SWITCH_CONSUMPTION'] = 100
            LocalVariables['CHECK_CONSUMPTION'] = 100
            SET_FREQ = random.randrange(0, 15000) + 10000
            LocalVariables['TRANSFER_RATE'] = 0x32

            # Set Volt
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 200 #For VDDH
            sdVolt.maxVoltage = 3800
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ # 250 Hz
            statusReg = 0
            bVddfValue = gvar.PowerSupply.VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            LocalVariables['MAX_CURRENT'] = 200

            if ((LocalVariables['CARD_CAPACITY'] >= 64) and (LocalVariables['SendOCR'] == LocalVariables['HcsXpcS18r111'])):
                # Set Volt
                sdVolt = sdcmdWrap.SVoltage()
                sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
                sdVolt.voltage = 3300 # 3.30 V
                sdVolt.maxCurrent = 150 #For VDDH
                sdVolt.maxVoltage = 3300
                sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 62.5 Hz
                statusReg = 0
                bVddfValue = gvar.PowerSupply.VDDH
                self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

                LocalVariables['MAX_CURRENT'] = 150

        if LocalVariables['RANDOM_UHS_MODE'] == 1:
            LocalVariables['UHS_MODE'] = 0x1
            LocalVariables['UHS_DRIVE'] = 0x0
            LocalVariables['UHS_CURRENT'] = 0x0
            LocalVariables['SWITCH_CONSUMPTION'] = 200
            LocalVariables['CHECK_CONSUMPTION'] = 200
            SET_FREQ = random.randrange(0, 25000) + 25000
            LocalVariables['TRANSFER_RATE'] = 0x5A

            # Set Volt
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 200 #For VDDH
            sdVolt.maxVoltage = 3800
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ
            statusReg = 0
            bVddfValue = gvar.PowerSupply.VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            LocalVariables['MAX_CURRENT'] = 200

        if LocalVariables['RANDOM_UHS_MODE'] == 2:
            LocalVariables['UHS_MODE'] = 0x2
            LocalVariables['UHS_DRIVE'] = 0x0
            LocalVariables['UHS_CURRENT'] = 0x1
            LocalVariables['SWITCH_CONSUMPTION'] = 250
            LocalVariables['CHECK_CONSUMPTION'] = 250
            SET_FREQ = random.randrange(0, 30000)+ 70000
            LocalVariables['TRANSFER_RATE'] = 0xB

            # Set Volt
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 250 #For VDDH
            sdVolt.maxVoltage = 3800
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ
            statusReg = 0
            bVddfValue = gvar.PowerSupply.VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            LocalVariables['MAX_CURRENT'] = 250

        if LocalVariables['RANDOM_UHS_MODE'] == 3:  # DDR50
            LocalVariables['UHS_MODE'] = 0x4
            LocalVariables['UHS_DRIVE'] = 0x0
            LocalVariables['UHS_CURRENT'] = 0x1
            LocalVariables['SWITCH_CONSUMPTION'] = 250
            LocalVariables['CHECK_CONSUMPTION'] = 250
            SET_FREQ = random.randrange(0, 25000) + 25000

            LocalVariables['TRANSFER_RATE'] = 0xB

            # Set Volt
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 250 #For VDDH
            sdVolt.maxVoltage = 3300
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 62.5 Hz
            statusReg = 0
            bVddfValue = gvar.PowerSupply.VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            LocalVariables['MAX_CURRENT'] = 250

        if LocalVariables['RANDOM_UHS_MODE'] == 4:  # SDR104
            LocalVariables['UHS_MODE'] = 0x3
            LocalVariables['UHS_DRIVE'] = 0x1
            LocalVariables['UHS_CURRENT'] = 0x1
            LocalVariables['SWITCH_CONSUMPTION'] = 250
            LocalVariables['CHECK_CONSUMPTION'] = 250
            SET_FREQ = random.randrange(0, 2)
            if SET_FREQ == 0:
                SET_FREQ = 200000
            else:
                SET_FREQ = 150000

            LocalVariables['TRANSFER_RATE'] = 0x2B

            # Set Volt
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.maxCurrent = 280 #For VDDH
            sdVolt.maxVoltage = 3800
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ
            statusReg = 0
            bVddfValue = gvar.PowerSupply.VDDH
            self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

            LocalVariables['MAX_CURRENT'] = 280

        if LocalVariables['UHS_MODE'] < 2:
            LocalVariables['CURRENT_LIMIT'] = 0x0

        if LocalVariables['UHS_MODE'] >= 0x2:
            LocalVariables['RANDOM_CURRENT_LIMIT'] = random.randrange(0, 2)

            if LocalVariables['RANDOM_CURRENT_LIMIT'] == 0:
                LocalVariables['CURRENT_LIMIT'] = 0x0
                LocalVariables['SWITCH_CONSUMPTION'] = 200

            if LocalVariables['RANDOM_CURRENT_LIMIT'] == 1:
                LocalVariables['CURRENT_LIMIT'] = 0x1
                LocalVariables['SWITCH_CONSUMPTION'] = 250
                # Set Volt
                sdVolt = sdcmdWrap.SVoltage()
                sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
                sdVolt.voltage = 3300 # 3.30 V
                sdVolt.maxCurrent = 250 #For VDDH
                sdVolt.maxVoltage = 3300
                sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ # 62.5 Hz
                statusReg = 0
                bVddfValue = gvar.PowerSupply.VDDH
                self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

                LocalVariables['MAX_CURRENT'] = 250

        # Variable Declaration
        LocalVariables['DRIVER_STRENGTH'] = LocalVariables['UHS_DRIVE']

        if LocalVariables['UHS_MODE'] == 0x0:
            # Set Frequency
            self.__sdCmdObj.SetFrequency(SET_FREQ)

        # Switch Command
        # Variable Declaration for support
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VS_Flag========================%s"% str(LocalVariables['VS_FLAG']))
        supported = LocalVariables["listData"]
        supported[1] = supported[1] & ((0x4000 * LocalVariables['VS_FLAG']) + 0xBFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "supported========================%s"% str(supported))

        # Call Switch Command for check mode / Check, Expected Status Available
        mode = gvar.CMD6.SWITCH
        arglist = [LocalVariables['UHS_MODE'],0xF,LocalVariables['DRIVER_STRENGTH'],LocalVariables['CURRENT_LIMIT'],0xF,0xF]
        blockSize = 0x40
        switched = [LocalVariables['UHS_MODE'],0x0,LocalVariables['UHS_DRIVE'],LocalVariables['CURRENT_LIMIT'],0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for Match to Value = 2
        self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                        responseCompare=responseCompare,
                                        compareConsumption=consumption,
                                        compareValue=LocalVariables['SWITCH_CONSUMPTION'],
                                        compareSupported=supported,
                                        comparedSwitched=switched)
        # set Frequency
        self.__sdCmdObj.SetFrequency(SET_FREQ)

        # Call Switch Command for check mode / Check, Expected Status Available
        mode = gvar.CMD6.CHECK
        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
        blockSize = 0x40
        switched = [LocalVariables['UHS_MODE'],0x0,LocalVariables['UHS_DRIVE'],LocalVariables['CURRENT_LIMIT'],0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE #for Match to Value = 2
        self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                        responseCompare=responseCompare,
                                        compareConsumption=consumption,
                                        compareValue=LocalVariables['CHECK_CONSUMPTION'],
                                        compareSupported=supported,
                                        comparedSwitched=switched)

        # Get CSD Values
        csd_value = self.__sdCmdObj.GET_CSD_VALUES()
        if LocalVariables["TRANSFER_RATE"] != int(csd_value["TRAN_SPEED"].lower(), 16):
            raise ValidationError.TestFailError(self.fn, "Transfer speed not matched. Expected is %s, Read from card is %s" % (LocalVariables["TRANSFER_RATE"], csd_value["TRAN_SPEED"].lower()))

        # Select card
        self.__sdCmdObj.Cmd7()

        # Call Utility_Successful_Verify
        self.__Successful_Verify.Run()

        # Call Script Utility_Successful_Verify_MaxVoltage
        self.__SuccessfulVerify_MaxVoltage.Run()

        # Call Block block_1
        self.block_1(LocalVariables)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Block block_7")
    # End Block block_7

    def block_8(self, LocalVariables):
        LocalVariables['RAND_UHS_MODE'] = random.randrange(0, 9) + 5

        # Switch Command
        # Variable Declaration for support
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VS_Flag========================%s"% str(LocalVariables['VS_FLAG']))
        supported = LocalVariables["listData"]
        supported[1] = supported[1] & ((0x4000 * LocalVariables['VS_FLAG']) + 0xBFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "supported========================%s"% str(supported))

        # Call Switch Command for check mode / Check, Expected Status Available
        mode = gvar.CMD6.CHECK
        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
        blockSize = 0x40
        switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x0,0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR #Not Error = 1
        CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                               responseCompare=responseCompare,
                                               compareConsumption=consumption,
                                               compare=[1,1,0,0,1,1],
                                               compareSupported=supported,
                                               comparedSwitched=switched)

        LocalVariables['DRIVER'] = CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup3
        LocalVariables['CURRENT'] = CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup4

        # Call Switch Command for Switch mode / Check, Expected Status Available
        mode = gvar.CMD6.SWITCH
        arglist = [LocalVariables['RAND_UHS_MODE'],0xF,0xF,0xF,0xF,0xF]
        blockSize = 0x40
        switched = [0xF,0x0,LocalVariables['DRIVER'],LocalVariables['CURRENT'],0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_ERROR #for Error
        self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                        responseCompare=responseCompare,
                                        compareConsumption=consumption,
                                        compareSupported=supported,
                                        comparedSwitched=switched)

        # Call Switch Command for check mode / Check, Expected Status Available
        mode = gvar.CMD6.CHECK
        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
        blockSize = 0x40
        switched = [LocalVariables['UHS_MODE'],0x0,LocalVariables['DRIVER'],LocalVariables['CURRENT'],0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR #for Not Error
        self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                        responseCompare=responseCompare,
                                        compareConsumption=consumption,
                                        compareSupported=supported,
                                        comparedSwitched=switched)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Block block_8")

    def block_9(self, LocalVariables):

        LocalVariables['DRIVER_STRENGTH'] = random.randrange(0, 10) + 4

        # Switch Command
        # Variable Declaration for support
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VS_Flag========================%s"% str(LocalVariables['VS_FLAG']))
        supported = LocalVariables["listData"]
        supported[1] = supported[1] & ((0x4000 * LocalVariables['VS_FLAG']) + 0xBFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "supported========================%s"% str(supported))

        # Call Switch Command for check mode / Check, Expected Status Available
        mode = gvar.CMD6.CHECK
        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
        blockSize = 0x40
        switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x0,0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR #for Not  Error
        CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                               responseCompare=responseCompare,
                                               compareConsumption=consumption,
                                               compare=[1,1,0,0,1,1],
                                               compareSupported=supported,
                                               comparedSwitched=switched)

        LocalVariables['DRIVER'] = CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup3
        LocalVariables['CURRENT'] = CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup4

        # Call Switch Command for Switch mode / Check, Expected Status Available
        mode = gvar.CMD6.SWITCH
        arglist = [0xF,0xF,LocalVariables['DRIVER_STRENGTH'],0xF,0xF,0xF]
        blockSize = 0x40
        switched = [LocalVariables['UHS_MODE'],0x0,0xF,LocalVariables['CURRENT'],0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_ERROR #for Error
        self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                        responseCompare=responseCompare,
                                        compareConsumption=consumption,
                                        compareSupported=supported,
                                        comparedSwitched=switched)

        # Call Switch Command for check mode / Check, Expected Status Available
        mode = gvar.CMD6.CHECK
        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
        blockSize = 0x40
        switched = [LocalVariables['UHS_MODE'],0x0,LocalVariables['DRIVER'],LocalVariables['CURRENT'],0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR #for Not Error
        self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                        responseCompare=responseCompare,
                                        compareConsumption=consumption,
                                        compareSupported=supported,
                                        comparedSwitched=switched)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Block block_9")
    #End of block_9

    def block_10(self, LocalVariables):

        LocalVariables['CURRENT_LIMIT'] = random.randrange(0, 10) + 4

        # Switch Command
        # Variable Declaration for support
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VS_Flag========================%s"% str(LocalVariables['VS_FLAG']))
        supported = LocalVariables["listData"]
        supported[1] = supported[1] & ((0x4000 * LocalVariables['VS_FLAG']) + 0xBFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "supported========================%s"% str(supported))

        # Call Switch Command for check mode / Check, Expected Status Available
        mode = gvar.CMD6.CHECK
        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
        blockSize = 0x40
        switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x0,0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR #for Not  Error
        CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                               responseCompare=responseCompare,
                                               compareConsumption=consumption,compare=[1,1,0,0,1,1],
                                               compareSupported=supported,
                                               comparedSwitched=switched)

        LocalVariables['DRIVER'] = CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup3
        LocalVariables['CURRENT'] = CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup4

        # Call Switch Command for Switch mode / Check, Expected Status Available
        mode = gvar.CMD6.SWITCH
        arglist = [0x0,0xF,0xF,LocalVariables['CURRENT_LIMIT'],0xF,0xF]
        blockSize = 0x40
        switched = [LocalVariables['UHS_MODE'],0x0,LocalVariables['DRIVER'],0xF,0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_ERROR #for Error
        self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                        responseCompare=responseCompare,
                                        compareConsumption=consumption,
                                        compareSupported=supported,
                                        comparedSwitched=switched)

        # Call Switch Command for check mode / Check, Expected Status Available
        mode = gvar.CMD6.CHECK
        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
        blockSize = 0x40
        switched = [LocalVariables['UHS_MODE'],0x0,LocalVariables['DRIVER'],LocalVariables['CURRENT'],0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR #for Not Error
        self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                        responseCompare=responseCompare,
                                        compareConsumption=consumption,
                                        compareSupported=supported,
                                        comparedSwitched=switched)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Block block_10")
    #End of block_10

    def block_11(self, LocalVariables):

        LocalVariables['RAND_UHS_MODE'] = random.randrange(0, 9) + 5
        LocalVariables['DRIVER_STRENGTH'] = random.randrange(0, 10) + 4
        LocalVariables['CURRENT_LIMIT'] = random.randrange(0, 10) + 4

        # Switch Command
        # Variable Declaration for support
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VS_Flag========================%s"% str(LocalVariables['VS_FLAG']))
        supported = LocalVariables["listData"]
        supported[1] = supported[1] & ((0x4000 * LocalVariables['VS_FLAG']) + 0xBFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "supported========================%s"% str(supported))

        # Call Switch Command for check mode / Check, Expected Status Available
        mode = gvar.CMD6.CHECK
        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
        blockSize = 0x40
        switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x0,0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR #for Not  Error
        CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                               responseCompare=responseCompare,
                                               compareConsumption=consumption,
                                               compare=[1,1,0,0,1,1],
                                               compareSupported=supported,
                                               comparedSwitched=switched)

        LocalVariables['DRIVER'] = CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup3
        LocalVariables['CURRENT'] = CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup4

        # Call Switch Command for Switch mode / Check, Expected Status Available
        mode = gvar.CMD6.SWITCH
        arglist = [LocalVariables['RAND_UHS_MODE'],0xF,LocalVariables['DRIVER_STRENGTH'],LocalVariables['CURRENT_LIMIT'],0xF,0xF]
        blockSize = 0x40
        switched = [0xF,0x0,0xF,0xF,0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_ERROR #for Error
        self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                        responseCompare=responseCompare,
                                        compareConsumption=consumption,
                                        compareSupported=supported,
                                        comparedSwitched=switched)

        # Call Switch Command for check mode / Check, Expected Status Available
        mode = gvar.CMD6.CHECK
        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
        blockSize = 0x40
        switched = [LocalVariables['UHS_MODE'],0x0,LocalVariables['DRIVER'],LocalVariables['CURRENT'],0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR #for Not Error
        self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                        responseCompare=responseCompare,
                                        compareConsumption=consumption,
                                        compareSupported=supported,
                                        comparedSwitched=switched)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Block block_11")
    #End of block_11

    def block_12(self, LocalVariables):

        # Switch Command
        # Variable Declaration for support
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VS_Flag========================%s"% str(LocalVariables['VS_FLAG']))
        supported = LocalVariables["listData"]
        supported[1] = supported[1] & ((0x4000 * LocalVariables['VS_FLAG']) + 0xBFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "supported========================%s"% str(supported))

        # Call Switch Command for check mode / Check, Expected Status Available
        mode = gvar.CMD6.CHECK
        arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
        blockSize = 0x40
        switched = [LocalVariables['UHS_MODE'],0x0,0x0,0x0,0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR #for Not  Error
        CMD6 = self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                               responseCompare=responseCompare,
                                               compareConsumption=consumption,
                                               compare=[1,1,0,0,1,1],
                                               compareSupported=supported,
                                               comparedSwitched=switched)

        LocalVariables['DRIVER'] = CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup3
        LocalVariables['CURRENT'] = CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup4

        # Variable Declaration
        LocalVariables['RANDOM_RESERVED'] = random.randrange(0, 5) + 5
        LocalVariables['RANDOM_MODE']= random.randrange(0, 3)

        if LocalVariables['RANDOM_MODE'] == 0:

            # Call Switch Command for Switch mode / Check, Expected Status Available
            mode = gvar.CMD6.SWITCH
            arglist = [0xF,LocalVariables['RANDOM_RESERVED'],0xF,0xF,0xF,0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0xF,LocalVariables['DRIVER'],LocalVariables['CURRENT'],0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_ERROR #for Error
            self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.CHECK
            arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,LocalVariables['DRIVER'],LocalVariables['CURRENT'],0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR #for Not Error
            self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

        if LocalVariables['RANDOM_MODE'] == 1:
            # Call Switch Command for Switch mode / Check, Expected Status Available
            mode = gvar.CMD6.SWITCH
            arglist = [0xF,0xF,0xF,0xF,LocalVariables['RANDOM_RESERVED'],0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,LocalVariables['DRIVER'],LocalVariables['CURRENT'],0xF,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_ERROR #for Error
            self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.CHECK
            arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,LocalVariables['DRIVER'],LocalVariables['CURRENT'],0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR #for Not Error
            self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

        if LocalVariables['RANDOM_MODE'] == 2:
            # Call Switch Command for Switch mode / Check, Expected Status Available
            mode = gvar.CMD6.SWITCH
            arglist = [0xF,0xF,0XF,0xF,0xF, LocalVariables['RANDOM_RESERVED']]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,LocalVariables['DRIVER'],LocalVariables['CURRENT'],0x0,0xF]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_ERROR #for Error
            self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

            # Call Switch Command for check mode / Check, Expected Status Available
            mode = gvar.CMD6.CHECK
            arglist = [0xF,0xF,0xF,0xF,0xF,0xF]
            blockSize = 0x40
            switched = [LocalVariables['UHS_MODE'],0x0,LocalVariables['DRIVER'],LocalVariables['CURRENT'],0x0,0x0]
            responseCompare = True #compare True
            consumption = gvar.CMD6.CONSUMPTION_NOT_ERROR #for Not Error
            self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                            responseCompare=responseCompare,
                                            compareConsumption=consumption,
                                            compareSupported=supported,
                                            comparedSwitched=switched)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Block block_12")
        #End of block_12

    def block_13(self):
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Started Block block_13")

        patternGen = PatternGen.PatternGen(self.vtfContainer, writePattern = sdcmdWrap.Pattern.INCREMENTAL, doCompare = True)

        #Multiple Write from start block = 0x0 with end block = 0x32000 with pattern incremental
        patternGen.MultipleWrite(address = 0x0, blockCount = 0x32000)

        #Multiple Read from start block = 0x0 with end block = 0x32000 with pattern incremental
        patternGen.MultipleRead(address = 0x0, blockCount = 0x32000)

        #Single Write from start block = 0x0 to 0x1 with pattern incremental
        patternGen.SingleWrite(address = 0x0, blockCount = 0x1)

        #Single Read from start block = 0x0 to 0x1 with pattern incremental
        patternGen.SingleRead(address = 0x0, blockCount = 0x1)

        #Erase Data from card from StartLba to BlockCount
        StartLBA = 0x0
        BlockCount = 0x32001
        EndLBA = self.__sdCmdObj.calculate_endLba(StartLBA, BlockCount)
        self.__dvtLib.Erase(StartLBA, EndLBA, directCardAPI=True)

        #Multiple Read from start block = 0x000 with end block = 0x32001 with pattern zero
        patternGen.SetPattern(pattern = sdcmdWrap.Pattern.ALL_ZERO)
        patternGen.MultipleRead(address = 0x0, blockCount = 0x32001)

        # Call script Utility_Successful_Verify
        self.__Successful_Verify.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Block block_13")
    #End of Block block_13

    def block_14(self):
        # Get SD Status
        self.__dvtLib.GetSDStatus()

        # Get SCR Values
        self.__dvtLib.GET_SCR_Reg_Values()

        # Get CID Values
        self.__sdCmdObj.GET_CID_VALUES()

        # Select card
        self.__dvtLib.SelectCard()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Block_14\n")

    def Run(self):
        """
        Name : Run
        """

        # Global values from globalPreTestingSettings file
        self.__globalPreTestSettingsObj.Run()

        # Call Utility_LoadLocal_Variables
        LocalVariables = self.__LoadLocal_Variables.Run()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PREREQUISITES")

        # Poweroff
        sdcmdWrap.SetPower(0)

        # Set Volt
        sdVolt = sdcmdWrap.SVoltage()
        sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8 # Region 1
        sdVolt.voltage = 3300 # 3.30 V
        sdVolt.maxCurrent = 200 #For VDDH
        sdVolt.maxVoltage = 3800
        sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ # 250 Hz
        statusReg = 0
        bVddfValue = gvar.PowerSupply.VDDH
        self.__dvtLib.setVolt(sdVolt, statusReg, bVddfValue)

        LocalVariables['MAX_CURRENT'] = 200

        # Poweron
        sdcmdWrap.SetPower(1)

        # Do card Reset
        self.__dvtLib.Reset(mode=sdcmdWrap.CARD_MODE.Sd, ocr=LocalVariables['HcsXpcS18r101'], cardSlot=0x1, sendCmd8=True,
                            initInfo=None, rca=0x0, time=0x0, sendCMD0=0x1, bHighCapacity=True, bSendCMD58=False,
                            version=0x0, VOLA=1, cmdPattern=0xAA, reserved=0x0, expOCRVal=LocalVariables['ReadyCcs18a111'])

        # SwitchVolt_CMD11
        self.__dvtLib.SwitchVolt_CMD11(True, 0, 5)

        # Identify Card
        self.__dvtLib.Identification()

        # Select card
        self.__sdCmdObj.Cmd7()

        # Set BusWidth = 4
        self.__dvtLib.SetBusWidth(busWidth=4)

        LocalVariables['UHS_MODE'] = 1  # SDR25
        LocalVariables['UHS_DRIVE'] = 0 # SDR25
        LocalVariables['UHS_CURRENT'] = 0x0 # SDR25
        LocalVariables['CURRENT_LIMIT'] = 0
        LocalVariables['DRIVER'] = 0
        LocalVariables['CURRENT'] = 0

        # Set SET_FREQ = 50000
        SET_FREQ = 50000

        # Switch command
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VS_Flag========================%s"% str(LocalVariables['VS_FLAG']))
        supported = LocalVariables["listData"]
        supported[1] = supported[1] & ((0x4000 * LocalVariables['VS_FLAG']) + 0xBFFF)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "supported========================%s"% str(supported))

        # Call Switch Command for check mode / Check, Expected Status Available
        mode = gvar.CMD6.SWITCH
        arglist = [LocalVariables['UHS_MODE'],0xF,LocalVariables['UHS_DRIVE'],LocalVariables['UHS_CURRENT'],0xF,0xF]
        blockSize = 0x40
        switched = [LocalVariables['UHS_MODE'],0x0,LocalVariables['UHS_DRIVE'],LocalVariables['UHS_CURRENT'],0x0,0x0]
        responseCompare = True #compare True
        consumption = gvar.CMD6.CONSUMPTION_MATCH_TO_VALUE # for Match to Value = 2
        self.__dvtLib.CardSwitchCommand(mode=mode,arginlist=arglist,blocksize=blockSize,
                                        responseCompare=responseCompare,
                                        compareConsumption=consumption,
                                        compareValue=200,
                                        compareSupported=supported,
                                        comparedSwitched=switched)

        # Set freq to SET_FREQ
        self.__sdCmdObj.SetFrequency(SET_FREQ)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Tag: Start Random Test")

        # Set Label:Loop
        for loop in range(0, 100):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Loop for 100 times, Current iteration is %s\n" % (loop + 1))

            # Variable Declaration
            rand_blk = random.randrange(0, 135) + 1

            if (0 < rand_blk <= 5):
                # Call Block Block_1
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Running Block_1\n")
                self.block_1(LocalVariables)

            if (5 < rand_blk <= 10):
                # Call Block Block_2
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Running Block_2\n")
                self.block_2(LocalVariables)

            if (10 < rand_blk <= 25):
                # Call Block Block_3
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Running Block_3\n")
                self.block_3(LocalVariables)

            if (25 < rand_blk <= 40):
                # Call Block Block_4
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Running Block_4\n")
                self.block_4(LocalVariables)

            if (40 < rand_blk <= 50):
                # Call Block Block_5
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Running Block_5\n")
                self.block_5(LocalVariables)

            if (50 < rand_blk <= 60):
                # Call Block Block_6
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Running Block_6\n")
                self.block_6(LocalVariables)

            if (60 < rand_blk <= 70):
                # Call Block Block_7
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Running Block_7\n")
                self.block_7(LocalVariables)

            if (70 < rand_blk <= 75):
                # Call Block Block_8
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Running Block_8\n")
                self.block_8(LocalVariables)

            if (75 < rand_blk <= 80):
                # Call Block Block_9
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Running Block_9\n")
                self.block_9(LocalVariables)

            if (80 < rand_blk <= 85):
                # Call Block Block_10
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Running Block_10\n")
                self.block_10(LocalVariables)

            if (85 < rand_blk <= 90):
                # Call Block Block_11
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Running Block_11\n")
                self.block_11(LocalVariables)

            if (90 < rand_blk <= 95):
                # Call Block Block_12
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Running Block_12\n")
                self.block_12(LocalVariables)

            if (95 < rand_blk <= 125):
                # Call Block Block_13
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Running Block_13\n")
                self.block_13()

            if (125 < rand_blk <= 135):
                # Call Block Block_14
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Running Block_14\n")
                self.block_14()

            # Variable Declaration
            LocalVariables["UHS_MODE_EX"] = LocalVariables['UHS_MODE']
            LocalVariables["SET_FREQ_EX"] = SET_FREQ
            LocalVariables["MAX_CURRENT_EX"] = LocalVariables['MAX_CURRENT']
            loop = loop-1

        # End of Label Loop
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "END OF SCRIPT")
        return 0

    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_UHS_SD3_TC006_UHSModes_Random_Test_Overcurrent(self):
        obj = UHS_SD3_TC006_UHSModes_Random_Test_Overcurrent(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
