"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : ConfigSD_UT005_GlobalPreTestingSettings.st3
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : ConfigSD_UT005_GlobalPreTestingSettings.py
# CVF PLAYLIST SCRIPT            : None
# CVF SCRIPT                     : ConfigSD_UT005_GlobalPreTestingSettings.py
# DESCRIPTION                    : The configure global values as per project configuration files
# PRERQUISTE                     : ConfigSD_UT014_GlobalSetTO.py
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 20/06/2022
################################################################################
"""
from __future__ import division

# SDDVT - Dependent TestCases
from past.utils import old_div
import SDDVT.Config_SD.ConfigSD_UT014_GlobalSetTO as globalSetTO

# SDDVT - Common Interface for Testcase
import SDDVT.Common.DvtCommonLib as DvtCommonLib

# SDDVT - SD Specification and commands related Interface
import SDDVT.Common.SDCommandLib as SDCommandLib
import SDDVT.Common.DvtLogger as dvtLogger

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
from future.utils import with_metaclass

# Global Variables


class Singleton(type):
    def __init__(self, *args, **kwargs):
        super(Singleton, self).__init__(*args, **kwargs)
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = super(Singleton, self).__call__(*args, **kwargs)
        return self.instance


class globalPreTestingSettings(with_metaclass(Singleton, customize_log)):
    """
    class for Loading all Local variables of params file
    """

    def __init__(self, VTFContainer):
        """
        Name        : __init__
        Description : Constructor for Class globalPreTestingSettings

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
        self.__dvtLogger = dvtLogger.DvtLogger(self.vtfContainer)
        self.__errorCodes = ErrorCodes.ErrorCodes()
        self.__cardMaxLba = self.__sdCmdObj.MaxLba()

        self.__globalSetTO = globalSetTO.globalSetTO(self.vtfContainer)

        ###### Customize Log: ######
        self.fn = os.path.basename(getframeinfo(currentframe()).filename)
        customize_log.__init__(self, self.__TF)

        ##### Testcase Specific Variables #####
        self.__globalProjectConfVar = {}
        self.__allowforfirsttime = 0


    def Run(self):
        """
        Name: Run
        """
        if self.__allowforfirsttime > 0:
            return self.__globalProjectConfVar

        self.__allowforfirsttime = 1
        globalProjectConfVar = self.__globalProjectConfVar

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Default Initialization Start")
        U = self.__cardMaxLba

        g_IsModel = 0x0
        if (g_IsModel == 1):
            # TOBEDONE: JIRA CTISW-5510
            # load_image, usage details part of JIRA CTISW-5510
            raise ValidationError.TestFailError(self.fn, "### Model image not loaded / Not supported in framework")

        self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Pre Testing Settings - Global Variables")

        if self.__config.get('globalCardVoltage') == "HV":
            self.__dvtLib.SwitchHostVoltageRegion(False)    # switch to 3.3V
        if self.__config.get('globalCardVoltage') == "LV":
            self.__dvtLib.SwitchHostVoltageRegion(True)     # switch to 1.8V

        sizeOfCard = self.__cardMaxLba
        sizeOfCard = old_div(old_div(old_div(sizeOfCard * 512, 1024), 1024), 1024)
        if (sizeOfCard <= 2):
            globalProjectConfVar['globalCardCapacity'] = "LC"
        elif (sizeOfCard <= 32 and sizeOfCard >= 2):
            globalProjectConfVar['globalCardCapacity'] = "HC"
        elif (sizeOfCard <= 2048 and sizeOfCard >= 32):
            globalProjectConfVar['globalCardCapacity'] = "XC"
        else:
            globalProjectConfVar['globalCardCapacity'] = "UC"

        globalProjectConfVar['globalPowerUp'] = self.__config.get('globalPowerUp')
        globalProjectConfVar['temp_globalSpeedMode'] = self.__config.get('globalSpeedMode')
        globalProjectConfVar['globalSpeedMode'] = self.__config.get('globalSpeedMode')
        globalProjectConfVar['temp_globalBusMode'] = self.__config.get('globalBusMode')
        globalProjectConfVar['globalBusMode'] = self.__config.get('globalBusMode')
        globalProjectConfVar['globalProtocolMode'] = self.__config.get('globalProtocolMode')
        globalProjectConfVar['globalCardRCA'] = 1
        globalProjectConfVar['globalHostVoltage'] = int(self.__config.get('globalHostVoltage'))
        globalProjectConfVar['globalLSHostFreq'] = int(self.__config.get('globalLSHostFreq'))
        globalProjectConfVar['globalVOLAValue'] = 1
        #globalProjectConfVar['globalHostVoltage'] = int(self.__config.get('globalHostVoltage'))
        #globalProjectConfVar['globalLSHostFreq'] = int(self.__config.get('globalLSHostFreq'))
        globalProjectConfVar['globalResetFreq'] = 300
        globalProjectConfVar['globalFBResetTO'] = 300
        globalProjectConfVar['configPatternFiledInCMD8'] = 170
        globalProjectConfVar['configResetTOCounter'] = self.__config.get('globalResetTO')
        globalProjectConfVar['globalProjectType'] = "SD"
        globalProjectConfVar['globalSPI'] = "yes"
        globalProjectConfVar['globalUHSscope'] = "no"
        globalProjectConfVar['globalHostVoltage'] = int(self.__config.get('globalHostVoltage'))
        globalProjectConfVar['globalVDDFMaxCurrent'] = int(self.__config.get('globalVDDFMaxCurrent'))
        globalProjectConfVar['globalVDDHMaxCurrent'] = int(self.__config.get('globalVDDHMaxCurrent'))

        if ((self.__config.get('globalProtocolMode') == "SDinSPI") or (self.__config.get('globalProtocolMode') == "SD")):
            globalProjectConfVar['globalCardType'] = "SD"

        # Set Time out
        self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Timeout Values")
        self.__globalSetTO.Run()

        if (self.__config.get('globalFlashType') == "X4"):
            # Set for garbage collection
            self.__dvtLib.Setting_PhasedGarbageCollection(True, 530)

        self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power: Off and On")
        #self.__sdCmdObj.PowerCycle()
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        globalProjectConfVar['uhs_support'] = 0

        self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Reset called for initialization of Card")
        globalProjectConfVar['globalOCRArgValue'] = int(self.__config.get('globalOCRArgValue'))
        globalProjectConfVar['globalOCRResValue'] = int(self.__config.get('globalOCRResValue'))

        Expected_Resp = sdcmdWrap.CardReset(sdcmdWrap.CARD_MODE.Sd, ocr = 0x41FF8000,
                                            cardSlot = 1, bSendCMD8 = True, initInfo = None, rca = 0, time = 0,
                                            sendCMD0 = 1, bHighCapacity = False, bSendCMD58 = False, version = 0,
                                            VOLA = 1, cmdPattern = 0xAA, reserved = 0)
        self.__sdCmdObj.OCRRegister = Expected_Resp

        globalProjectConfVar['uhs_support'] = (Expected_Resp >> 24) & 0x1       # S18R bit - Switching to 1.8V Request

        # Default Initialization
        self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Initialization")
        try:
            sdcmdWrap.WrapSDCardInit()
            self.__sdCmdObj.SetrelativeCardAddress(RCA=sdcmdWrap.WrapGetRCA())
            #self.__sdCmdObj.R()
        except ValidationError.CVFExceptionTypes as exc:
            self.__sdCmdObj.ErrorPrint()
            raise ValidationError.TestFailError(self.fn, exc.GetFailureDescription())

        # Log M-CONF
        self.__dvtLogger.getMConfData()

        if globalProjectConfVar['globalCardType'] == "SD":
            self.__sdCmdObj.GET_CSD_VALUES()
        #else:       #Commented as sddvt package is only for SD Cards not for MMC Cards
        #    readBuffer = ServiceWrap.Buffer.CreateBuffer(0x1,0)
        #    self.__card.MMCGetExtCsd(readBuffer)

        if (self.__config.get('globalDVTTestScope') == "SanityDVT"):
            globalProjectConfVar['configLoopCounter'] = 1
            # read from project configuration
            globalReadAheadSize = int(self.__config.get('globalReadAheadSize'))
            globalProjectConfVar['configBlockCNT'] = random.randrange(0, (10000 - globalReadAheadSize)) + globalReadAheadSize   # 10000 as per scripter
        else:
            if (self.__config.get("configBlockCNT") == 0):
                globalProjectConfVar['configBlockCNT'] = old_div(U, 3)      # U = maxlba

            if (self.__config.get("configBlockCNT") == 1):
                globalReadAheadSize = int(self.__config.get('globalReadAheadSize'))
                globalProjectConfVar['configBlockCNT'] = random.randrange(0, (1024 - globalReadAheadSize)) + globalReadAheadSize

        # Pre Testing Settings - for the different products
        if (self.__config.get("globalFlashType") == "OTP"):
            self.__sdCmdObj.ReadFirmwareParameter()
            #self.__testSpace.GetCard().ReadFirmwareParameter(rbuff, 31)    # CTF syntax
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Read file 31 for globalFlashType = OTP")

        if (self.__config.get("globalFlashType") == "ROM"):
            globalProjectConfVar['globallockunlock'] = "no"

        elif (self.__config.get("globalSpecVer") == "eSD2.10"):
            globalProjectConfVar['globalSelectPartitionTO'] = 10
            globalProjectConfVar['globallockunlock'] = "no"

            self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Initialization")
            sdcmdWrap.WrapSDCardInit()

            # Get meta block size
            Mconfbuffer = self.__sdCmdObj.GetMConf()
            MetaBlockSize = Mconfbuffer.GetTwoBytesToInt(385, little_endian = False)     # Reading Value from Buffer

            # Log M-CONF
            self.__dvtLogger.getMConfData()

        # UHS-I initializations
        self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "UHS-1 Initialization")

        if ((globalProjectConfVar['globalSpeedMode'] == "SDR12") or (globalProjectConfVar['globalSpeedMode'] == "SDR25") or (globalProjectConfVar['globalSpeedMode'] == "SDR50")
            or (globalProjectConfVar['globalSpeedMode'] == "SDR104") or (globalProjectConfVar['globalSpeedMode'] == "DDR50")
            or (globalProjectConfVar['globalSpeedMode'] == "RandomSDR12_LS") or (globalProjectConfVar['globalSpeedMode'] == "RandomSDR25_DDR50_HS")):

            globalProjectConfVar['globallockunlock'] = "no"
            globalProjectConfVar['globalSPI'] = "no"
            globalProjectConfVar['globalUHSscope'] = "yes"

        # Running settings (PG, Host log, GC ...)
        # Default to do all Read and Write with SDR Pattern Generator
        # Use below steps for host log
        # sdcmdWrap.SDRSetDebugMethod(Method = sdcmdWrap.DEBUG_METHOD.IO_DEBUG, Set = True)
        # sdcmdWrap.GetHostDebugInformation(szPathToFile = "C:\\reviewlogs\\STPGC.txt")
        self.__dvtLib.CardInfo()

        if (g_IsModel == 1):
            globalProjectConfVar['globalSPI'] = "no"
            globalProjectConfVar['uhs_support'] = 0

        globalProjectConfVar["VS_Flag"] = 0

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Default Initialization Completed\n\n")
        return globalProjectConfVar
