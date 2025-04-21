"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : ConfigSD_UT003_GlobalInitSDCard.st3
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : ConfigSD_UT003_GlobalInitSDCard.py
# CVF PLAYLIST SCRIPT            : None
# CVF SCRIPT                     : ConfigSD_UT003_GlobalInitSDCard.py
# DESCRIPTION                    : globalInitSDCard for Global Reset for SD Card type
# PRERQUISTE                     : Dictionary returned by ConfigSD_UT005_GlobalPreTestingSettings.py as argument to Run method
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 21/06/2022
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


class globalInitSDCard(customize_log):
    """
    class for SD and SPI initialization using RESET
    """

    def __init__(self, VTFContainer):
        """
        Name        :  __init__
        Description : Constructor for Class globalInitSDCard
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

        # Get the values from Project Configuration dictionary
        globalCardRCA = globalProjectConfVar['globalCardRCA']
        globalOCRArgValue = globalProjectConfVar["globalOCRArgValue"]
        globalOCRResValue = globalProjectConfVar['globalOCRResValue']
        globalVOLAValue = globalProjectConfVar['globalVOLAValue']
        globalSpeedMode = globalProjectConfVar['globalSpeedMode']
        globalBusMode = globalProjectConfVar['globalBusMode']
        globalPowerUp = globalProjectConfVar['globalPowerUp']

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Global Reset for SD Card type")

        if((globalProjectConfVar['globalProtocolMode'] == 'SD')):
            if(globalPowerUp == 'powerCycleNoCMD0'):
                CMD0Flag = 0
            else:
                CMD0Flag = 1

            if((self.__config.get('globalSpecVer') == 'SD2.00') or (self.__config.get('globalSpecVer') == 'eSD2.10') or
               (self.__config.get('globalSpecVer') == 'SD3.00')):
                if(self.__config.get('globalCardCapacity') == 'HC') or (self.__config.get('globalCardCapacity') == 'XC'):
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Reset for SD HC/XC SPEC 2.00 card in SD Mode")

                    #if self.__optionValues.LV == 1:  # LV
                    LV = 0
                    if LV == 1:
                        # TOBEDONE: Yet to covert LV initialization from CTF to CVF
                        pass
                    else:
                        if globalProjectConfVar['globalPowerUp'] == 'softReset':
                            globalOCRResValue = self.__config.get('globalOCRResValue')
                            if globalOCRResValue:
                                globalOCRResValue = (int(globalOCRResValue) & 0xFEFFFFFF)
                                globalProjectConfVar['globalOCRResValue'] = globalOCRResValue
                                Expected_Resp, initInfo = self.__dvtLib.Reset(mode = sdcmdWrap.CARD_MODE.Sd, ocr = 0x40FF8000,
                                                                              cardSlot = globalCardRCA, rca = globalCardRCA,
                                                                              sendCMD0 = CMD0Flag, VOLA = globalVOLAValue,
                                                                              expOCRVal = globalOCRResValue)
                        else:
                            Expected_Resp, initInfo = self.__dvtLib.Reset(mode = sdcmdWrap.CARD_MODE.Sd, ocr = globalOCRArgValue,
                                                                          cardSlot = globalCardRCA, rca = globalCardRCA,
                                                                          sendCMD0 = CMD0Flag, VOLA = globalVOLAValue,
                                                                          expOCRVal = globalOCRResValue)

                    self.__sdCmdObj.SPIEnable(False)
                    # Check for Expected Values
                    self.compareExpectedValues(Expected_Resp, initInfo, [1, 1, 1, 1, 0], globalProjectConfVar)

                else:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Reset for SD LC SPEC 2.00 card in SD Mode")
                    self.__dvtLib.Reset(mode = sdcmdWrap.CARD_MODE.Sd, ocr = globalOCRArgValue,
                                        cardSlot = globalCardRCA, rca = globalCardRCA,
                                        sendCMD0 = CMD0Flag, bHighCapacity = False,
                                        VOLA = globalVOLAValue, expOCRVal = globalOCRResValue)
                    self.__sdCmdObj.SPIEnable(False)


            if((self.__config.get('globalSpecVer') == 'SD1.01') or (self.__config.get('globalSpecVer') == 'SD1.1')):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Reset for SD Legacy SPEC 1.1 or 1.01 card in SD Mode")
                self.__dvtLib.Reset(mode = sdcmdWrap.CARD_MODE.Sd, ocr = globalOCRArgValue, cardSlot = globalCardRCA,
                                    sendCmd8 = False, sendCMD0 = CMD0Flag, bHighCapacity = False, bSendCMD58 = False,
                                    VOLA = globalVOLAValue, expOCRVal = globalOCRResValue)
                self.__sdCmdObj.SPIEnable(False)


            if(((globalSpeedMode == 'SDR12') or (globalSpeedMode == 'SDR25') or (globalSpeedMode == 'SDR50') or
                (globalSpeedMode == 'SDR104') or (globalSpeedMode == 'DDR50') or (globalSpeedMode == 'DDR200')) and
               ((globalPowerUp == 'powerCycle') or (globalPowerUp == 'powerCycleNoCMD0'))):

                # check bit 24 in ocr whether it supports switching 1.8V
                if((globalOCRResValue >> 24) & 1 == 1):
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "IF UHS Card, CMD11 - Host switch to 1.8V")
                    # True : Switch to 1.8V else 3.3V
                    self.__dvtLib.SwitchVolt_CMD11(switchTo1_8v = True, timeToClockOff = 0, clockOffPeriod = 5)

        elif((globalProjectConfVar['globalProtocolMode'] == 'SDinSPI')):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Protocol Mode is SPI")

            self.__dvtLib.enableACMD41()

            if((self.__config.get('globalSpecVer') == 'SD2.00') or (self.__config.get('globalSpecVer') == 'eSD2.10') or
               (self.__config.get('globalSpecVer') == 'SD3.00')):

                if(self.__config.get('globalCardCapacity') == 'HC' or self.__config.get('globalCardCapacity') == 'XC'):
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Reset for SD HC SPEC 2.00 card in SPI Mode")

                    Expected_Resp, initInfo = self.__dvtLib.Reset(mode = sdcmdWrap.CARD_MODE.SD_IN_SPI, ocr = globalOCRArgValue,
                                                                  cardSlot = globalCardRCA, sendCmd8 = True, initInfo = None,
                                                                  rca = 0, time = 0, sendCMD0 = 1, bHighCapacity = True,
                                                                  bSendCMD58 = True, version = 0, VOLA = globalVOLAValue,
                                                                  cmdPattern = 0xAA, reserved = 0, expOCRVal = globalOCRResValue)
                    self.compareExpectedValues(Expected_Resp, initInfo, [0, 1, 1, 1, 0], globalProjectConfVar)

                else:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Reset for SD LC SPEC 2.00 card in SPI Mode")

                    Expected_Resp, initInfo = self.__dvtLib.Reset(mode = sdcmdWrap.CARD_MODE.SD_IN_SPI, ocr = globalOCRArgValue,
                                                                  cardSlot = globalCardRCA, sendCmd8 = True, initInfo = None,
                                                                  rca = 0, time = 0, sendCMD0 = 1, bHighCapacity = False,
                                                                  bSendCMD58 = True, version = 0, VOLA = globalVOLAValue,
                                                                  cmdPattern = 0xAA, reserved = 0, expOCRVal = globalOCRResValue)
                    self.compareExpectedValues(Expected_Resp, initInfo, [0, 0, 1, 1, 0], globalProjectConfVar)

            if((self.__config.get('globalSpecVer') == 'SD1.01') or (self.__config.get('globalSpecVer') == 'SD1.1')):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Reset for SD Legacy SPEC 1.1 or 1.01 card in SPI Mode")

                Expected_Resp, initInfo = self.__dvtLib.Reset(mode = sdcmdWrap.CARD_MODE.SD_IN_SPI, ocr = globalOCRArgValue,
                                                              cardSlot = globalCardRCA, sendCmd8 = False, initInfo = None,
                                                              rca = 0, time = 0, sendCMD0 = 1, bHighCapacity = False,
                                                              bSendCMD58 = True, version = 0, VOLA = globalVOLAValue,
                                                              cmdPattern = 0xAA, reserved = 0)
            self.__sdCmdObj.SPIEnable()
        return 0

    def compareExpectedValues(self, reset_Resp, initInfo, compareAll, globalProjectConfVar):
        '''
        For Reset return value comparison
        '''
        if self.currCfg.variation.lv == 1:
            CheckPattern = 0xA5
        else:
            CheckPattern = 0xAA

        if compareAll[0] == 1:
            if reset_Resp != globalProjectConfVar['globalOCRResValue']:
                pass
                # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "[INFO] Expected value %d amd Actula return value %d "%(globalProjectConfVar['globalOCRResValue'],reset_Resp))
                # raise self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "OCR value compare error")
        if compareAll[1] == 1:
            if initInfo.GetOneByteToInt(0) != 1:  # hicapfromcard
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "[INFO] Expected value %d amd Actual return value %d"
                                      % (1, initInfo.GetOneByteToInt(0)))
                raise self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "High capacity compare error")
        if compareAll[2] == 1:
            # VOLAvalfromcard
            if initInfo.GetOneByteToInt(3) != globalProjectConfVar['globalVOLAValue']:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "[INFO] Expected value %d amd Actual return value %d"
                                      % (globalProjectConfVar['globalVOLAValue'], initInfo.GetOneByteToInt(3)))
                raise self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Vola card compare error")
        if compareAll[3] == 1:
            if initInfo.GetOneByteToInt(4) != CheckPattern:  # CMDPatternfromcard
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "[INFO] Expected value %s amd Actula return value %d"
                                      % ("0xAA", initInfo.GetOneByteToInt(0)))
                raise self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Command pattern compare error")
        if compareAll[4] == 1:  # For Reserved bits
            Reservedbitsfromcard = initInfo.GetFourBytesToInt(5, little_endian = False)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "[INFO] Expected value %d amd Actula return value %d"
                                  % (1, initInfo.GetOneByteToInt(0)))
            raise self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "High capacity compare error")
