"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : ConfigSD_UT013_GlobalSetSpeedMode.st3
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : ConfigSD_UT013_GlobalSetSpeedMode.py
# CVF PLAYLIST SCRIPT            : None
# CVF SCRIPT                     : ConfigSD_UT013_GlobalSetSpeedMode.py
# DESCRIPTION                    : Module to set speed mode
# PRERQUISTE                     : [ConfigSD_UT009_GlobalSetHSHostFreq, ConfigSD_UT011_GlobalSetLSHostFreq.py, ConfigSD_UT015_GlobalSetVHSHostFreq]
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 19/09/2022
################################################################################
"""
from __future__ import division

# SDDVT - Dependent TestCases
from past.utils import old_div
import SDDVT.Config_SD.ConfigSD_UT011_GlobalSetLSHostFreq as globalSetLSHostFreq
import SDDVT.Config_SD.ConfigSD_UT009_GlobalSetHSHostFreq as globalSetHSHostFreq
import SDDVT.Config_SD.ConfigSD_UT015_GlobalSetVHSHostFreq as globalSetVeryHSHostFreq

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


class globalSetSpeedMode(customize_log):
    """
    class for setting Bus Width
    """

    def __init__(self, VTFContainer):
        """
        Name :  __init__
        Description : Constructor for Class globalSetSpeedMode
        Arguments : VTFContainer - The VTFContainer used for running the test
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
        self.__globalSetLSHostFreqObj = globalSetLSHostFreq.globalSetLSHostFreq(self.vtfContainer)
        self.__globalSetHSHostFreqObj = globalSetHSHostFreq.globalSetHSHostFreq(self.vtfContainer)
        self.__globalSetVeryHSHostFreqObj = globalSetVeryHSHostFreq.globalSetVeryHSHostFreq(self.vtfContainer)


    def Run(self, globalProjectConfVar):
        """
        For more understanding about this script, Refer Table 4-11 : Available Functions of CMD6 and refer definitions of
        TRAN_SPEED in sections 5.3.2(CSD version 1.0), 5.3.3(CSD version 2.0) and 5.3.4(CSD version 3.0) in SD spec version 7.0
        part-I(Physical layer).
        """
        self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set the Speed mode to the card")
        globalProjectConfVar["SpeedModeSwitchValue"] = 0x000000
        globalProjectConfVar["SwitchCMDCurrentValue"] = 100

        if((globalProjectConfVar['globalCardType'] == 'SD') and (globalProjectConfVar['globalProtocolMode'] != 'SDinSPI')
           and (globalProjectConfVar['globalSpeedMode'] == 'HS') and (self.__config.get('globalSpecVer') != 'SD1.01')):

            self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "High Speed Mode in SD Card")
            arglist = [0x1, 0x0, 0x0, 0x0, 0x0, 0x0]    # switch to high speed(SDR25) and verify high speed
            self.__dvtLib.CardSwitchCommand(arginlist = arglist, blocksize = 0x200)

            CSD_Reg_Values =  self.__sdCmdObj.GET_CSD_VALUES()
            if(CSD_Reg_Values['TRAN_SPEED'] != '0x5a'):     # 0x5a is for SDR25
                raise ValidationError.TestFailError(self.fn, "Transfer speed did not match with expected value")

            self.__globalSetHSHostFreqObj.Run()
            self.__sdCmdObj.Cmd7()

            globalProjectConfVar["SpeedModeSwitchValue"] = 0x100000
            globalProjectConfVar["SwitchCMDCurrentValue"] = 200

        if((globalProjectConfVar['globalCardType'] == 'SD') and (globalProjectConfVar['globalProtocolMode'] != 'SDinSPI')
           and (globalProjectConfVar['globalSpeedMode'] == 'Lightning') and (self.__config.get('globalSpecVer') != 'SD1.01')):

            self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Switch to high speed")
            arglist = [0x1, 0xF, 0xF, 0xF, 0xF, 0xF]    # switch to high speed(SDR25) and verify high speed
            self.__dvtLib.CardSwitchCommand(arginlist = arglist, blocksize = 0x200)

            CSD_Reg_Values =  self.__sdCmdObj.GET_CSD_VALUES()
            if(CSD_Reg_Values['TRAN_SPEED'] != '0x5a'):     # 0x5a is for SDR25
                raise ValidationError.TestFailError(self.fn, "Transfer speed did not match with expected value")

            self.__globalSetHSHostFreqObj.Run()
            self.__sdCmdObj.Cmd7()

            self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Switch to Vendor Specific mode")
            arglist = [0xF, 0xE, 0xF, 0xF, 0xF, 0xF]
            self.__dvtLib.CardSwitchCommand(arginlist = arglist, blocksize = 0x200)

            CMD35_ARG = 0
            CMD34_RESP = 0

            #Not VS specific card were avilable as per System team to test CMD34 and CMD35, and this section is never getting executed.
            #VS Single Write #CMD35 with correct parameters and password
            #VS Single Read #CMD34 say - Lightning is supported
            raise ValidationError.TestFailError(self.fn, "VS APIs(for CMD34 and CMD35) are not available and VS specific card is also not available")
            self.__globalSetVeryHSHostFreqObj.Run()

            globalProjectConfVar["SpeedModeSwitchValue"] = 0x1E0000
            globalProjectConfVar["SwitchCMDCurrentValue"] = 200

        globalSpeedMode = globalProjectConfVar['globalSpeedMode']
        if ((globalSpeedMode == "SDR12") or (globalSpeedMode == "SDR25") or (globalSpeedMode == "SDR50") or (globalSpeedMode == "SDR104")
          or (globalSpeedMode == "DDR50") or (globalSpeedMode == "DDR200") or (globalSpeedMode == "RandomSDR12_LS") or (globalSpeedMode == "RandomSDR25_DDR50_HS")):

            self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "IF UHS Mode")

            if globalSpeedMode == 'SDR12':
                self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Switch to SDR12 Speed")
                arglist = [0x0, 0x0, 0x0, 0x0, 0x0, 0x0]    # switch to default speed(SDR12) and verify default speed
                self.__dvtLib.CardSwitchCommand(arginlist = arglist, blocksize = 0x40)

                self.__globalSetLSHostFreqObj.Run()

                CSD_Reg_Values =  self.__sdCmdObj.GET_CSD_VALUES()
                if(CSD_Reg_Values['TRAN_SPEED'] != '0x32'):     # 0x32 is for SDR12
                    raise ValidationError.TestFailError(self.fn, "Transfer speed did not match with expected value")

                globalProjectConfVar["SpeedModeSwitchValue"] = 0x000000
                globalProjectConfVar["SwitchCMDCurrentValue"] = 100

            elif globalSpeedMode == 'SDR25':
                self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Switch to SDR25 speed")
                arglist = [0x1, 0x0, 0x0, 0x0, 0x0, 0x0]        # switch to high speed(SDR25) and verify high speed
                self.__dvtLib.CardSwitchCommand(arginlist = arglist, blocksize = 0x40)

                self.__globalSetHSHostFreqObj.Run()

                CSD_Reg_Values =  self.__sdCmdObj.GET_CSD_VALUES()
                if(CSD_Reg_Values['TRAN_SPEED'] != '0x5a'):     # 0x5a is for SDR25
                    raise ValidationError.TestFailError(self.fn, "Transfer speed did not match with expected value")

                globalProjectConfVar["SpeedModeSwitchValue"] = 0x100000
                globalProjectConfVar["SwitchCMDCurrentValue"] = 200

            elif globalSpeedMode == 'SDR50':
                self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Switch to SDR50 speed")
                arglist = [0x2, 0xF, 0xF, 0x1, 0xF, 0xF]        # switch to SDR50 and verify SDR50
                self.__dvtLib.CardSwitchCommand(arginlist = arglist, blocksize = 0x40)

                self.__globalSetVeryHSHostFreqObj.Run()

                CSD_Reg_Values = self.__sdCmdObj.GET_CSD_VALUES()
                if(CSD_Reg_Values['TRAN_SPEED'] != '0xb'):      # 0xb is for SDR50 and DDR50, here SDR50 was tried to be set
                    raise ValidationError.TestFailError(self.fn, "Transfer speed did not match with expected value")

                globalProjectConfVar["SpeedModeSwitchValue"] = 0x200100
                globalProjectConfVar["SwitchCMDCurrentValue"] = 250

            elif globalSpeedMode == 'DDR50':
                self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Switch to DDR50 speed")
                arglist = [0x4, 0xF, 0xF, 0x1, 0xF, 0xF]        # switch to DDR50 and verify DDR50
                self.__dvtLib.CardSwitchCommand(arginlist = arglist, blocksize = 0x40)

                self.__globalSetHSHostFreqObj.Run()

                CSD_Reg_Values = self.__sdCmdObj.GET_CSD_VALUES()
                if(CSD_Reg_Values['TRAN_SPEED'] != '0xb'):      # 0xb is for SDR50 and DDR50, here DDR50 was tried to be set
                    raise ValidationError.TestFailError(self.fn, "Transfer speed did not match with expected value")

                globalProjectConfVar["SpeedModeSwitchValue"] = 0x400100
                globalProjectConfVar["SwitchCMDCurrentValue"] = 250

                # moving the card to tran state for tuning
                if self.__sdCmdObj.GetCardStatus().count("CURRENT_STATE:Tran")!=1 :
                    self.__sdCmdObj.Cmd7()    # added to get the card to tran state

                #TuningBuffer = ServiceWrap.Buffer.CreateBuffer(1)
                #TapList = []
                #sdcmdWrap.TuneHostForUHS(TapList, TuningBuffer)
                #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Optimal TapList value:%s"%TapList)

                globalHSHostFreq = int(self.__config.get('globalHSHostFreq'))
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Calling SetFreqWithTuning......\n")
                self.__sdCmdObj.SetFreqWithTuning(globalHSHostFreq)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Host Frequency set to %d MHz"%(old_div(globalHSHostFreq,1000)))

            elif globalSpeedMode == 'SDR104':
                self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Switch to SDR104 speed")
                arglist = [0x3, 0xF, 0x1, 0x1, 0xF, 0xF]        # switch to SDR104 and verify SDR104

                self.__dvtLib.CardSwitchCommand(arginlist = arglist, blocksize = 0x40)

                self.__globalSetVeryHSHostFreqObj.Run()

                CSD_Reg_Values = self.__sdCmdObj.GET_CSD_VALUES()
                if(CSD_Reg_Values['TRAN_SPEED'] != '0x2b'):     # 0x2b is for SDR104
                    raise ValidationError.TestFailError(self.fn, "Transfer speed did not match with expected value")

                globalProjectConfVar["SpeedModeSwitchValue"] = 0x301100
                globalProjectConfVar["SwitchCMDCurrentValue"] = 250

            # TOBEDONE: DDR200
            elif globalSpeedMode == 'DDR200':
                self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Checking for DDR200 Support")

                CMD6 = self.__dvtLib.CardSwitchCommand(mode = gvar.CMD6.CHECK, arginlist = [0xF, 0xF, 0xF, 0xF, 0xF, 0xF], blocksize = 0x40)
                
                decodedResponse = self.__sdCmdObj.DecodeSwitchCommandResponse("CHECK", CMD6)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd6 Decoded Response = %s" % decodedResponse) # Decoded Message

                if("DDR200 SUPPORTED IN GROUP1" in decodedResponse):
                    arglist = [0x5, 0xF, 0x1, 0x1, 0xF, 0xF]
                    switchString = "DDR200 SWITCHED IN GROUP1"
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card supports DDR200 in Group1")

                elif ("DDR200 SUPPORTED IN GROUP2" in decodedResponse):
                    arglist = [0xF, 0xE, 0x1, 0x1, 0xF, 0xF]
                    switchString = "DDR200 SWITCHED IN GROUP2"
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card supports DDR200 in Group2")
                else:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Doesn't support DDR200")
                    raise ValidationError.TestFailError(self.fn, "Card Doesn't support DDR200")

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Switch to DDR200 speed")

                CMD6 = self.__dvtLib.CardSwitchCommand(arginlist = arglist, blocksize = 0x40)
                decodedResponse = self.__sdCmdObj.DecodeSwitchCommandResponse("SWITCH", CMD6)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd6 Decoded Response = %s" % decodedResponse) # Decoded Message

                if(switchString in decodedResponse):
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Switched to DDR200")
                else:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed to Switch to DDR200")
                    raise ValidationError.TestFailError(self.fn, "Failed to switch to DDR200 Mode")

                self.__globalSetVeryHSHostFreqObj.Run()

                CSD_Reg_Values = self.__sdCmdObj.GET_CSD_VALUES()
                if(CSD_Reg_Values['TRAN_SPEED'] != '0x2b'):
                    raise ValidationError.TestFailError(self.fn,
                                                        " Transfer speed did not match with expected value")

                globalProjectConfVar["SpeedModeSwitchValue"] = 0x501100
                globalProjectConfVar["SwitchCMDCurrentValue"] = 250

            else:
                self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Default Speeed Mode Set")

            if self.__sdCmdObj.GetCardStatus().count("CURRENT_STATE:Tran") != 1:
                self.__sdCmdObj.Cmd7()    # added to get the card to tran state

        return 0
