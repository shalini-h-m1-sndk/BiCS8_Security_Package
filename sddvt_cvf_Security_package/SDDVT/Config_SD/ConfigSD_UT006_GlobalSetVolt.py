"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : ConfigSD_UT006_GlobalSetVolt.st3
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : ConfigSD_UT006_GlobalSetVolt.py
# CVF PLAYLIST SCRIPT            : None
# CVF SCRIPT                     : ConfigSD_UT006_GlobalSetVolt.py
# DESCRIPTION                    : Module to set the host voltage value
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 19/09/2022
################################################################################
"""

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


class globalSetVolt(customize_log):
    """
    class for setting Voltage
    """

    def __init__(self, VTFContainer):
        """
        Name        :  __init__
        Description : Constructor for Class globalSetVolt
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


    def Run(self, globalProjectConfVar):
        """
        Name: Run
        Description: To set the Host voltage value
        This is a configuration script and can be executed as indivual script also.
        if needed, function can be copied directly.
        Step 1: Get the value of globalSpeedMode, globalHostVoltage, globalVDDFMaxCurrent, globalVDDHMaxCurrent
        Step 2: Set Voltage based on value of globalSpeedMode
                set voltage with values: Region = 1, SetVolt = 3.3 V; maxVoltage = 3.8V, maxCurrent = 250mA, A2DRate = 62.5 Hz, PowerSupplier = Flash (VDDF)
                set voltage with Values: Region = 1, SetVolt = globalHostVoltage; maxVoltage = 3.8V, maxCurrent = 250mA, A2DRate = 62.5 Hz, PowerSupplier = Host (VDDH)
                set voltage with values: Region = 1, SetVolt = 3.3 V; maxVoltage = 3.8V, maxCurrent = globalVDDFMaxCurrent, A2DRate = 62.5 Hz, PowerSupplier = Flash (VDDF)
                set voltage with Values: Region = 1, SetVolt = globalHostVoltage; maxVoltage = 3.8V, maxCurrent = globalVDDHMaxCurrent, A2DRate = 62.5 Hz, PowerSupplier = Host (VDDH)
        """

        # Get the value of globalSpeedMode, globalHostVoltage, globalVDDFMaxCurrent, globalVDDHMaxCurrent

        # Set Voltage based on value of globalSpeedMode
        if((globalProjectConfVar['globalSpeedMode'] == 'DDR50') or (globalProjectConfVar['globalSpeedMode'] == 'DDR200') or (globalProjectConfVar['globalSpeedMode'] == 'SDR50') or (globalProjectConfVar['globalSpeedMode'] == 'SDR104')):
            # set voltage with values: Region = 1, SetVolt = 3.3 V; maxVoltage = 3.8V, maxCurrent = 250mA, A2DRate = 62.5 Hz, PowerSupplier = Flash (VDDF)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set card voltage value")
            try:
                sdVolt = sdcmdWrap.SVoltage()
                sdVolt.voltage = 3300       # 3.30 V
                sdVolt.maxVoltage = 3800    # 3.8 V
                # TOBEDONE: maxCurrent CTF / Scripter
                #sdVolt.maxCurrent = 250     # 250 mA - CTF
                sdVolt.maxCurrent = 400   # 400 mA - Scripter
                sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_PARTIAL_1V8           # Region 1
                sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ   # 62.5 Hz

                statusReg = 0
                bVddfValue = gvar.PowerSupply.VDDF           # True - Flash(VDDF) / False - Host(VDDH)

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "voltage - %smV, maxVoltage = %smV, maxCurrent - %smA, A2DRate - %s, PowerSupplier(VDDF) - %s"
                             % (sdVolt.voltage, sdVolt.maxVoltage, sdVolt.maxCurrent, sdVolt.A2DOutrateType, bVddfValue))
                sdcmdWrap.SDRSetVolt(voltStruct = sdVolt, pStatusReg = statusReg, bVddfValue = bVddfValue)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card voltage value is set")

            except ValidationError.CVFExceptionTypes as exc:
                self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed while setting card voltage")
                raise ValidationError.TestFailError(self.fn, "Failed while setting card voltage")

            # set voltage with Values: Region = 1, SetVolt = globalHostVoltage; maxVoltage = 3.8V, maxCurrent = 250mA, A2DRate = 62.5 Hz, PowerSupplier = Host (VDDH)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set host voltage value")
            try:
                sdVolt = sdcmdWrap.SVoltage()
                sdVolt.voltage = globalProjectConfVar['globalHostVoltage']
                sdVolt.maxVoltage = 3800    # 3.8 V
                # TOBEDONE: maxCurrent CTF / Scripter
                sdVolt.maxCurrent = 250     # 250 mA - CTF
                # sdVolt.maxCurrent = 400   # 400 mA - Scripter
                sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_PARTIAL_1V8           # Region 1
                sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ   # 62.5 Hz

                statusReg = 0
                bVddfValue = False          # True - Flash(VDDF) / False - Host(VDDH)

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "voltage - %smV, maxVoltage = %smV, maxCurrent - %smA, A2DRate - %s, PowerSupplier(VDDF) - %s"
                             % (sdVolt.voltage, sdVolt.maxVoltage, sdVolt.maxCurrent, sdVolt.A2DOutrateType, bVddfValue))
                sdcmdWrap.SDRSetVolt(voltStruct = sdVolt, pStatusReg = statusReg, bVddfValue = bVddfValue)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Host voltage value is set")

            except ValidationError.CVFExceptionTypes as exc:
                self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed while setting host voltage")
                raise ValidationError.TestFailError(self.fn, "Failed while setting host voltage")
        else:
            # set voltage with values: Region = 1, SetVolt = 3.3 V; maxVoltage = 3.8V, maxCurrent = globalVDDFMaxCurrent, A2DRate = 62.5 Hz, PowerSupplier = Flash (VDDF)
            try:
                sdVolt = sdcmdWrap.SVoltage()
                sdVolt.voltage = 3300       # 3.30 V
                sdVolt.maxVoltage = 3800    # 3.8 V
                sdVolt.maxCurrent = globalProjectConfVar['globalVDDFMaxCurrent']
                sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_PARTIAL_1V8           # Region 1
                sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ   # 62.5 Hz

                statusReg = 0
                bVddfValue = gvar.PowerSupply.VDDF           # True - Flash(VDDF) / False - Host(VDDH)

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "voltage - %smV, maxVoltage = %smV, maxCurrent - %smA, A2DRate - %s, PowerSupplier(VDDF) - %s"
                             % (sdVolt.voltage, sdVolt.maxVoltage, sdVolt.maxCurrent, sdVolt.A2DOutrateType, bVddfValue))
                sdcmdWrap.SDRSetVolt(voltStruct = sdVolt, pStatusReg = statusReg, bVddfValue = bVddfValue)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card voltage value is set")
            except ValidationError.CVFExceptionTypes as exc:
                self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed while setting card voltage")
                raise ValidationError.TestFailError(self.fn, "Failed while setting card voltage")

            # set voltage with Values: Region = 1, SetVolt = globalHostVoltage; maxVoltage = 3.8V, maxCurrent = globalVDDHMaxCurrent, A2DRate = 62.5 Hz, PowerSupplier = Host (VDDH)
            try:
                sdVolt = sdcmdWrap.SVoltage()
                sdVolt.voltage = globalProjectConfVar['globalHostVoltage']
                sdVolt.maxVoltage = 3800    # 3.8 V
                sdVolt.maxCurrent = globalProjectConfVar['globalVDDHMaxCurrent']
                sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_PARTIAL_1V8           # Region 1
                sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ   # 62.5 Hz

                statusReg = 0
                bVddfValue = False          # True - Flash(VDDF) / False - Host(VDDH)

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "voltage - %smV, maxVoltage = %smV, maxCurrent - %smA, A2DRate - %s, PowerSupplier(VDDF) - %s"
                             % (sdVolt.voltage, sdVolt.maxVoltage, sdVolt.maxCurrent, sdVolt.A2DOutrateType, bVddfValue))
                sdcmdWrap.SDRSetVolt(voltStruct = sdVolt, pStatusReg = statusReg, bVddfValue = bVddfValue)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Host voltage value is set")
            except ValidationError.CVFExceptionTypes as exc:
                self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed while setting host voltage")
                raise ValidationError.TestFailError(self.fn, "Failed while setting host voltage")

        return 0
