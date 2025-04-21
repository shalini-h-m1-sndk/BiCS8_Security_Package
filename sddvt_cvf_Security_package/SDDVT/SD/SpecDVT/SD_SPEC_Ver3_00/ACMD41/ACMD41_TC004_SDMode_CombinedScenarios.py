"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : ACMD41_TC004_SDMode_CombinedScenarios.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : ACMD41_TC004_SDMode_CombinedScenarios.py
# DESCRIPTION                    : The purpose of this test is to assure SD Combined Scenarios.
# PRERQUISTE                     : ACMD41_UT03_CMD20_Sequence.py, ACMD41_UT06_LoadCMD20_Variables.py, ACMD41_UT07_Load_LocalVariables.py
                                   ACMD41_UT08_Reset.py, ACMD41_UT13_Successful_Verify_MaxVoltage.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=ACMD41_TC004_SDMode_CombinedScenarios --isModel=false --enable_console_log=1 --adapter=0
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
import ACMD41_UT03_CMD20_Sequence as Cmd20Sequence
import ACMD41_UT06_LoadCMD20_Variables as CMD20Variables
import ACMD41_UT07_Load_LocalVariables as LocalVariables
import ACMD41_UT08_Reset as ResetUtil
import ACMD41_UT13_Successful_Verify_MaxVoltage as SuccessfulVerifyMaxVoltage

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


# Testcase Class - Begins
class ACMD41_TC004_SDMode_CombinedScenarios(customize_log):
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
        self.__getSequence = Cmd20Sequence.ACMD41_UT03_CMD20_Sequence(self.vtfContainer)


    # Testcase Logic - Starts
    def Run(self):
        """
        Name : Run
        """
        globalProjectConfVar = self.__sdCmdObj.DoBasicInit()

        # Load Variables from the Script Utility_Load_LocalVariables
        localVariables = LocalVariables.ACMD41_UT07_Load_LocalVariables(self.vtfContainer).Run(ret = 1)

        # Load CMD20 Specific variables from the Script Utility_CMD20_Variables
        cmd20variables = CMD20Variables.ACMD41_UT06_LoadCMD20_Variables(self.vtfContainer).Run()

        # Set voltage = 3.3V, Max current = 150mA, A2D Rate : 62.5 Hz, Power supplier = Flash
        sdvoltage = sdcmdWrap.SVoltage()
        sdvoltage.voltage = 3300
        sdvoltage.maxCurrent = 150
        sdvoltage.maxVoltage = 3800
        sdvoltage.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ
        sdvoltage.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8

        self.__dvtLib.setVolt(sdVolt = sdvoltage, statusReg = 0, powerSupp = gvar.PowerSupply.VDDF)

        # Set voltage = globalHostVoltage, Max current = 150mA, A2D Rate : 62.5 Hz, Power supplier = HOST
        globalHostVoltage = int(self.__config.get('globalHostVoltage'))
        sdvoltage.voltage = globalHostVoltage

        self.__dvtLib.setVolt(sdVolt = sdvoltage, statusReg = 0, powerSupp = gvar.PowerSupply.VDDH)

        # Variable declaration
        localVariables['SendOCR'] = localVariables['HcsXpcS18r110']
        localVariables['ExpectOCR'] = localVariables['ReadyCcs18a110']
        localVariables['VerifyType'] = 3
        localVariables['ProtocolMode'] = 1
        localVariables['SetPower'] = 1
        localVariables['SendCMD0'] = 1
        localVariables['SendCMD8'] = 1

        # Loop Reset1
        for Reset1 in range(0, 2):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set label Reset1 loop count is %s" % (Reset1 + 1))

            # Call script reset utility
            ResetUtil.ACMD41_UT08_Reset(self.vtfContainer).Run(globalProjectConfVar, localVariables)

            # GET SD STATUS
            ACMD13 = self.__dvtLib.GetSDStatus()

            # Check SpeedClass = 0
            if ACMD13.objSDStatusRegister.ui64SpeedClass == 0:
                raise ValidationError.TestFailError(self.fn, "Speed Class should be > 0")

            # Call Script Utility CMD20Sequence
            self.__getSequence.Run(cmd20variables)

            localVariables['SendOCR'] = localVariables['HcsXpcS18r111']

        localVariables['SendOCR'] = localVariables['HcsXpcS18r111']

        # Call script reset utility
        ResetUtil.ACMD41_UT08_Reset(self.vtfContainer).Run(globalProjectConfVar, localVariables)

        # GET SD STATUS
        ACMD13 = self.__dvtLib.GetSDStatus()

        # Check SpeedClass = 0
        if ACMD13.objSDStatusRegister.ui64SpeedClass == 0:
            raise ValidationError.TestFailError(self.fn, "Speed Class should be > 0")

        # Call Script Utility CMD20Sequence
        self.__getSequence.Run(cmd20variables)

        # Call script utility SuccessVerifyMaxVoltage
        SuccessfulVerifyMaxVoltage.ACMD41_UT13_Successful_Verify_MaxVoltage(self.vtfContainer).Run()

        localVariables['SendOCR'] = localVariables['HcsXpcS18r100']

        # Set voltage = 3.3V, Max current = 100mA, A2D Rate : 62.5 Hz, Power supplier = Flash
        sdvoltage = sdcmdWrap.SVoltage()
        sdvoltage.voltage = 3300
        sdvoltage.maxCurrent = 100
        sdvoltage.maxVoltage = 3800
        sdvoltage.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ
        sdvoltage.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8

        self.__dvtLib.setVolt(sdVolt = sdvoltage, statusReg = 0, powerSupp = gvar.PowerSupply.VDDF)

        # Set voltage = globalHostVoltage, Max current = 100mA, A2D Rate : 62.5 Hz, Power supplier = Host
        globalHostVoltage = self.__config.get('globalHostVoltage')
        sdvoltage.voltage = int(globalHostVoltage)

        self.__dvtLib.setVolt(sdVolt = sdvoltage, statusReg = 0, powerSupp = gvar.PowerSupply.VDDH)

        localVariables['SetPower'] = 0

        # Call script reset utility
        ResetUtil.ACMD41_UT08_Reset(self.vtfContainer).Run( globalProjectConfVar, localVariables)

        # Call script utility SuccessVerifyMaxVoltage
        SuccessfulVerifyMaxVoltage.ACMD41_UT13_Successful_Verify_MaxVoltage(self.vtfContainer).Run()

        localVariables['SendOCR'] = localVariables['HcsXpcS18r111']

        # Set voltage = 3.3V, Max current = 150mA, A2D Rate : 62.5 Hz, Power supplier = Flash
        sdvoltage = sdcmdWrap.SVoltage()
        sdvoltage.voltage = 3300
        sdvoltage.maxCurrent = 150
        sdvoltage.maxVoltage = 3800
        sdvoltage.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ
        sdvoltage.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8

        self.__dvtLib.setVolt(sdVolt = sdvoltage, statusReg = 0, powerSupp = gvar.PowerSupply.VDDF)

        # Set voltage = globalHostVoltage, Max current = 100mA, A2D Rate : 62.5 Hz, Power supplier = Host
        globalHostVoltage = self.__config.get('globalHostVoltage')
        sdvoltage.voltage = int(globalHostVoltage)

        self.__dvtLib.setVolt(sdVolt = sdvoltage, statusReg = 0, powerSupp = gvar.PowerSupply.VDDH)

        # Call script reset utility
        ResetUtil.ACMD41_UT08_Reset(self.vtfContainer).Run(globalProjectConfVar, localVariables)

        # GET SD STATUS
        ACMD13 = self.__dvtLib.GetSDStatus()

        # Check SpeedClass = 0
        if ACMD13.objSDStatusRegister.ui64SpeedClass == 0:
            raise ValidationError.TestFailError(self.fn, "Speed Class should be > 0")

        # Call script utility SuccessVerifyMaxVoltage
        SuccessfulVerifyMaxVoltage.ACMD41_UT13_Successful_Verify_MaxVoltage(self.vtfContainer).Run()

        # Variable declaration
        localVariables['SendOCR'] = localVariables['HcsXpcS18r000']
        localVariables['VerifyType'] = 0
        localVariables['ProtocolMode'] = 2
        localVariables['Identification'] = 0

        # Call script reset utility
        ResetUtil.ACMD41_UT08_Reset(self.vtfContainer).Run(globalProjectConfVar, localVariables)

        localVariables['SendOCR'] = localVariables['HcsXpcS18r100']

        # Set voltage = 3.3V, Max current = 100mA, A2D Rate : 62.5 Hz, Power supplier = Flash
        sdvoltage = sdcmdWrap.SVoltage()
        sdvoltage.voltage = 3300
        sdvoltage.maxCurrent = 100
        sdvoltage.maxVoltage = 3800
        sdvoltage.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ
        sdvoltage.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8

        self.__dvtLib.setVolt(sdVolt = sdvoltage, statusReg = 0, powerSupp = gvar.PowerSupply.VDDF)

        # Set voltage = globalHostVoltage, Max current = 100mA, A2D Rate : 62.5 Hz, Power supplier = Host
        globalHostVoltage = self.__config.get('globalHostVoltage')
        sdvoltage.voltage = int(globalHostVoltage)

        self.__dvtLib.setVolt(sdVolt = sdvoltage, statusReg = 0, powerSupp = gvar.PowerSupply.VDDH)

        localVariables['ProtocolMode'] = 1
        localVariables['VerifyType'] = 3
        localVariables['Identification'] = 1

        # Call script reset utility
        ResetUtil.ACMD41_UT08_Reset(self.vtfContainer).Run(globalProjectConfVar, localVariables)

        # Call script utility SuccessVerifyMaxVoltage
        SuccessfulVerifyMaxVoltage.ACMD41_UT13_Successful_Verify_MaxVoltage(self.vtfContainer).Run()

        # Set voltage = 3.3V, Max current = globalVDDFMaxCurrent, A2D Rate : 62.5 Hz, Power supplier = Flash
        globalVDDFMaxCurrent = self.__config.get('globalVDDFMaxCurrent')
        sdvoltage = sdcmdWrap.SVoltage()
        sdvoltage.voltage = 3300
        sdvoltage.maxCurrent = int(globalVDDFMaxCurrent)
        sdvoltage.maxVoltage = 3800
        sdvoltage.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ
        sdvoltage.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8

        self.__dvtLib.setVolt(sdVolt = sdvoltage, statusReg = 0, powerSupp = gvar.PowerSupply.VDDF)

        # Set voltage = globalHostVoltage, Max current = globalVDDHMaxCurrent, A2D Rate : 62.5 Hz, Power supplier = Host
        globalHostVoltage = self.__config.get('globalHostVoltage')
        globalVDDHMaxCurrent = self.__config.get('globalVDDHMaxCurrent')
        sdvoltage.voltage = int(globalHostVoltage)
        sdvoltage.maxCurrent = int(globalVDDHMaxCurrent)

        self.__dvtLib.setVolt(sdVolt = sdvoltage, statusReg = 0, powerSupp = gvar.PowerSupply.VDDH)

        return 0
    # Testcase Logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_ACMD41_TC004_SDMode_CombinedScenarios(self):
        obj = ACMD41_TC004_SDMode_CombinedScenarios(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
