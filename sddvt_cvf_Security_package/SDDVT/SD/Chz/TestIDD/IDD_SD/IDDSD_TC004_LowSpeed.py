"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : IDDSD_TC004_LowSpeed.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : IDDSD_TC004_LowSpeed.py
# DESCRIPTION                    : For IDD Test in LowSpeed Mode
# PRERQUISTE                     : IDDSD_UT004_InitCard, IDDSD_UT001_InitCardSimple, IDDSD_UT005_PreSleepExec
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=IDDSD_TC004_LowSpeed --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 30-May-2024
# UPDATED BY                     : Sushmitha P.S
# UPDATED DATE                   : 29-Aug-2024
################################################################################
"""

# Python future modules for python3 forward compatibility
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    from builtins import str
    from builtins import range
    from builtins import *
    from builtins import object
from past.utils import old_div

# SDDVT - Dependent TestCases
import IDDSD_UT004_InitCard as IDD_InitCard
import IDDSD_UT001_InitCardSimple as InitCardSample
import IDDSD_UT005_PreSleepExec as PreSleepExec

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
from datetime import datetime
import socket

# Global Variables
intToSampleRate = {0:sdcmdWrap.EIddMsrSampleRate.ONE_MS, 1:sdcmdWrap.EIddMsrSampleRate.TWO_MS, 2:sdcmdWrap.EIddMsrSampleRate.FOUR_MS,
                   3:sdcmdWrap.EIddMsrSampleRate.EIGHT_MS, 4:sdcmdWrap.EIddMsrSampleRate.SIXTEEN_MS, 5:sdcmdWrap.EIddMsrSampleRate.THIRTY_TWO_MS,
                   6:sdcmdWrap.EIddMsrSampleRate.SIXTY_FOUR_MS, 7:sdcmdWrap.EIddMsrSampleRate.ONE_HUNDRED_TWENTY_EIGHT_MS}

class MeasurmentResult( object ):
    def __init__(self,startTime = 0,endTime= 0, numOfSamples = 0, minimum = 0, maximum = 0, average = 0):
        self.startTime    = startTime
        self.endTime      = endTime
        self.numOfSamples = numOfSamples
        self.minimum      = minimum
        self.maximum      = maximum
        self.average      = average

# Testcase Class - Begins
class IDDSD_TC004_LowSpeed(customize_log):
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
        self.__InitCard = IDD_InitCard.IDDSD_UT004_InitCard(self.vtfContainer)
        self.__InitCardSimple = InitCardSample.IDDSD_UT001_InitCardSimple(self.vtfContainer)
        self.__PreSleepExec = PreSleepExec.IDDSD_UT005_PreSleepExec(self.vtfContainer)

        self.__sdVoltage           = sdcmdWrap.SVoltage()
        self.__globalParameters    = {} #gloval file values
        self.__dirPath             = None
        self.__results             = {"hotInsertion":MeasurmentResult(),
                                                                "hotInsertionVddf":MeasurmentResult(),
                                                                "sleepMode":MeasurmentResult(),
                                                                "sleepModeVddf":MeasurmentResult(),
                                                                "write":MeasurmentResult(),
                                                                "writeVddf":MeasurmentResult(),
                                                                "read":MeasurmentResult(),
                                                                "readVddf":MeasurmentResult()}
        self.__currentVoltage      = None
        self.__mesureVDDF          = False
        self.__readStartAddress   = 0
        self.__writeStartAdress   = 0
        self.__blocksToWrite       = 0
        self.__blocksToRead        = 0
        self.__log_file_name = None
        self.__ProductSerialNumber = 0

    def GetInitConfigValues(self):
        """
        Read the parameter file and returns the values as string in dictionary
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "GetInitConfigValues:Reading of parameter file started\n")
        tdic = {}
        self.__project_config = None
        self.__sdconfig       = None
        self.__TestsDir = self.currCfg.system.TestsDir
        if not self.__TestsDir:
            raise ValidationError.TestFailError(self.fn, "SDDVT home path not set")
        self.__project_config = self.currCfg.system.TestsCfgDir
        if not self.__project_config:
            raise ValidationError.TestFailError(self.fn, "Project Configuration Not Found..." % self.__project_config)
        self.__sdconfig = self.currCfg.variation.sdconfiguration
        if not self.__sdconfig:
            raise ValidationError.TestFailError(self.fn, '%s, sdconfiguration Not Found...'%(self.__sdconfig))

        self.cfgfile = os.path.join(self.__TestsDir,'SDDVT', 'SD', 'Chz', 'TestIDD','Configurations_Master', "Master_Configuration_IDD_SD_LowSpeed.txt")

        if not os.path.isfile(self.cfgfile):
            raise ValidationError.TestFailError(self.fn, "config file not found..." % self.cfgfile)

        if self.cfgfile:
            if not os.path.isfile(self.cfgfile):
                raise ValidationError.TestFailError(self.fn, "config file not found..." % self.cfgfile)
            fh = open(self.cfgfile, 'r')
            for line in fh.readlines():
                if line.find('=')!=-1 and line.startswith("//") == False:
                    #print line
                    key,val = line.split("(")[0],line.split("(")[1].split("=")[1].strip()
                    tdic[key] = val
                else:
                    continue
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "GetInitConfigValues:Reading of parameter file completed\n")
        return tdic

    # Testcase logic - Starts
    def Run(self):

        self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Started Execution\n")

        globalParameters = self.__globalParameters
        globalParameters = self.GetInitConfigValues() #Load from config files

        FPGA_Low_Reg_enable = 1 #0 for 3.3 and 1 for 1.8
        firstLoop = 1 #Just started, so we're in the first loop

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###  -----------------  Define Variables for Deep Sleep   --------------")
        In_IDD_DeepSleepAvgSet1,In_IDD_DeepSleepMaxSet1,In_IDD_DeepSleepMinSet1 = 0,0,0
        In_IDD_DeepSleepAvgSet2,In_IDD_DeepSleepMaxSet2,In_IDD_DeepSleepMinSet2 = 0,0,0
        In_IDD_DeepSleepAvgSet3,In_IDD_DeepSleepMaxSet3,In_IDD_DeepSleepMinSet3 = 0,0,0
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###  -----------------  Define Variables for Deep Sleep completed   --------------\n")

        self.__sdCmdObj.Set_SDXC_SETTINGS(Set_XPC_bit = 1, Send_CMD11_in_the_next_card_init = 0)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###  -----------------   INIT SEQUENCE   --------------")
        self.__dvtLib.SwitchHostVoltageRegion(FPGA_Low_Reg_enable) #Switche to 3.3

        #Default Intilization
        self.__InitCardSimple.Run(globalParameters)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "========== MAIN PROCEDURE ==========")

        CID_Values = self.__sdCmdObj.GET_CID_VALUES()
        self.__ProductSerialNumber = CID_Values[gvar.CID.PSN]

        #Check for Folder measurement
        FW_VALIDATION_PATH = self.currCfg.system.TestsDir
        directory = os.path.join(FW_VALIDATION_PATH,'SDDVT', 'SD', 'Chz', 'TestIDD' , 'IDD_SD' ,'Measurements','LS')

        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except Exception as exc:
                self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed to create directory ans error is %s"%exc)
                raise ValidationError.TestFailError(self.fn, "Failed to create directory ans error is %s" % exc)

        self.__dirPath = directory
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###  -----------------   MAIN PROCEDURE    --------------\n")

        vddh_index = 0
        #Extraction Buffer from config file
        globalParameters["VDDH_MilliVoltages"] = globalParameters["VDDH_MilliVoltages"].replace("}",'').replace("{",'').replace(" ","").split(",")
        globalParameters["VDDF_MilliVoltages"] = globalParameters["VDDF_MilliVoltages"].replace("}",'').replace("{",'').replace(" ","").split(",")
        vddhRepresentation = int(globalParameters["VDDH_MilliVoltages"][vddh_index])
        vddh = vddhRepresentation * 50

        #Intilaize Card
        self.__InitCardSimple.Run(globalParameters)

        #Verify IDD blocks is in card range
        if int(globalParameters["IDD_Blocks"]) >= self.__cardMaxLba:
            globalParameters["IDD_Blocks"] = self.__cardMaxLba - 500

        #Loop Over VDDH
        loopsHost = 16777215
        while (loopsHost != 0) and (vddhRepresentation != 0xFF):

            sdcmdWrap.SetPower(0)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power is OFF\n")

            #Set SD Voltage to 3.0V
            sdvoltage = sdcmdWrap.SVoltage()
            sdvoltage.voltage = vddh
            sdvoltage.maxCurrent = 250
            sdvoltage.maxVoltage = 3800
            sdvoltage.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ
            sdvoltage.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8
            self.__dvtLib.setVolt(sdVolt = sdvoltage, statusReg = 0, powerSupp = gvar.PowerSupply.VDDH)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Voltage of host completed\n")

            sdcmdWrap.SetPower(1)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power is ON\n")

            #Check for VDDF or VDDH
            if globalParameters["IDD_MeasureVddf"] == 1:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#"*150)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "************  VDDF SECTION *****************")
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#"*150)

                self.__mesureVDDF = True #Flag allows for measuring VDDF in Hot Insertion/Read/Write and Sleep

                # VDDF START
                vddf_index = 0
                vddfRepresentation =  int(globalParameters["VDDF_MilliVoltages"][vddf_index])
                vddf = vddfRepresentation * 50

                #Loop Over VDDF
                loopsFlash = 16777215
                while (loopsFlash != 0) and (vddfRepresentation  != 0xFF):

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========   START HOT INSERTION   ==========\n")

                    sdcmdWrap.SetPower(0)
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power is OFF\n")

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Voltage of Flash Started")

                    #Set SD Voltage to 3.0V
                    sdvoltage = sdcmdWrap.SVoltage()
                    sdvoltage.voltage = vddf
                    sdvoltage.maxCurrent = 250
                    sdvoltage.maxVoltage = 3800
                    sdvoltage.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ
                    sdvoltage.regionSelect = sdcmdWrap.REGION_SELECT_TYPE.REGION_SELECT_PARTIAL_1V8

                    self.__dvtLib.setVolt(sdVolt = sdvoltage, statusReg = 0, powerSupp = gvar.PowerSupply.VDDF)
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Voltage of Flash completed\n")

                    sdcmdWrap.SetPower(1)
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power is ON\n")

                    self.__currentVoltage = vddf

                    self.iddMesureInSleepMode_HotInsertionMode() #Read Hot insertion

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========   END HOT INSERTION  ========== \n\n")

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========   START ON WRITE   ==========\n")

                    self.__InitCardSimple.Run(globalParameters)

                    if firstLoop == 1:
                        firstLoop = 0

                    self.iddMesureInSleepMode_Write(globalParameters)  # Mesure IDD for Write Mode

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========   END ON WRITE   ========== \n\n")

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========    DEEP SLEEP SET 1   ==========\n")

                    if int(globalParameters["IDD_DeepSleep"]) == 1: #Condition is always false and section include MMC API

                        self.__dvtLib.SelectCard(False)

                        # Commented below line as sddvt package is only for SD Cards not for MMC Cards
                        # self.__card.MMCSleepAwake(True,500,False,True)
                        #MMC sleep awake
                        #sleep - TRUE to switch to SLEEP from STANDBY, FALSE to awake from SLEEP to STANDBY.
                        #R1bTimeout - timeout of R1b response. The sleep command has a R1b response. This response has a busy that has a specific timeout definition.
                        #controlVddf - TRUE to switch OFF Vccf power supply during going to Sleep state and to switch ON Vccf power supply during going from Sleep state.
                        #verifySleepState - TRUE to test the card state on awake command response. Has affect only if sleep is FALSE

                        #IDD measurement in sleep mode for deepSleep JIRA CTISW-5665

                    #End of if
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========  End OF DEEP SLEEP SET 1   ========== \n\n")

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========   START ON READ   ==========\n")

                    self.__InitCardSimple.Run(globalParameters)

                    self.iddMesureInSleepMode_Read(globalParameters)  #IDD Mearurement in Read Mode

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========    END ON READ   ========== \n\n")

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========    DEEP SLEEP SET 2   ==========\n")
                    if int(globalParameters["IDD_DeepSleep"]) == 1: #Condition is always false and section include MMC API

                        self.__dvtLib.SelectCard(False)
                        # Commented below line as sddvt package is only for SD Cards not for MMC Cards
                        # self.__card.MMCSleepAwake(True,500,False,True)
                        #MMC sleep awake
                        #sleep - TRUE to switch to SLEEP from STANDBY, FALSE to awake from SLEEP to STANDBY.
                        #R1bTimeout - timeout of R1b response. The sleep command has a R1b response. This response has a busy that has a specific timeout definition.
                        #controlVddf - TRUE to switch OFF Vccf power supply during going to Sleep state and to switch ON Vccf power supply during going from Sleep state.
                        #verifySleepState - TRUE to test the card state on awake command response. Has affect only if sleep is FALSE

                        #IDD measurement in sleep mode for deepSleep JIRA CTISW-5665

                    #End of if
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========  End OF DEEP SLEEP SET 2   ========== \n\n")

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========    START OF SLEEP MODE  ==========\n")

                    self.__PreSleepExec.Run(globalParameters)

                    self.iddMesureInSleepMode_SleepMode() #IDD Mearurement in SLeep Mode

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========    END OF SLEEP MODE  ========== \n\n")

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========    DEEP SLEEP SET 3   ==========\n")

                    if int(globalParameters["IDD_DeepSleep"]) == 1: #Condition is always false and section include MMC API

                        self.__dvtLib.SelectCard(False)

                        # Commented below line as sddvt package is only for SD Cards not for MMC Cards
                        # self.__card.MMCSleepAwake(True,500,False,True)
                        #MMC sleep awake
                        #sleep - TRUE to switch to SLEEP from STANDBY, FALSE to awake from SLEEP to STANDBY.
                        #R1bTimeout - timeout of R1b response. The sleep command has a R1b response. This response has a busy that has a specific timeout definition.
                        #controlVddf - TRUE to switch OFF Vccf power supply during going to Sleep state and to switch ON Vccf power supply during going from Sleep state.
                        #verifySleepState - TRUE to test the card state on awake command response. Has affect only if sleep is FALSE

                        #IDD measurement in sleep mode for deepSleep JIRA CTISW-5665

                    #End of if

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========  End OF DEEP SLEEP SET 3  ==========\n")

                    #Change the Voltage and rerun loop
                    filename = os.path.join(self.__dirPath, "Current_Measurements_VDDF", str(self.__currentVoltage) + '.dat')

                    # Check if the directory exists; if not, create it
                    directory = os.path.dirname(filename)
                    if not os.path.exists(directory):
                        os.makedirs(directory)

                    # Now open the file in append mode to create it if it doesn't exist
                    with open(filename, 'a') as file:
                        self.WriteGeneralResultsFile(filename)

                    vddf_index = vddf_index + 1
                    vddfRepresentation = int(globalParameters["VDDF_MilliVoltages"][vddf_index])
                    vddf = vddfRepresentation * 50

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#"*150)
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "************  VDDF SECTION END*****************\n")
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#"*150)

                #End of While
                #End of IF
                #VDDF END

            else:  #VDDH section

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#"*150)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "************  VDDH SECTION STARTED*****************")
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#"*150)

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========   START HOT INSERTION   ==========\n")

                sdcmdWrap.SetPower(0)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power is OFF\n")

                sdcmdWrap.SetPower(1)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power is ON\n")

                self.__currentVoltage = vddh

                self.iddMesureInSleepMode_HotInsertionMode() #read Hot insertion

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========   STOP HOT INSERTION  ========== \n\n")

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========   START ON WRITE   ==========\n")

                self.__InitCard.Run(globalParameters)

                self.iddMesureInSleepMode_Write(globalParameters)  #Mesure IDD in Write Mode

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========   END ON WRITE   ==========\n")

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========    DEEP SLEEP SET 1   ==========\n")
                if int(globalParameters["IDD_DeepSleep"]) == 1: #Condition is always false and section include MMC API

                    self.__dvtLib.SelectCard(False)

                    # Commented below line as sddvt package is only for SD Cards not for MMC Cards
                    # self.__card.MMCSleepAwake(True,500,False,True)
                    #MMC sleep awake
                    #sleep - TRUE to switch to SLEEP from STANDBY, FALSE to awake from SLEEP to STANDBY.
                    #R1bTimeout - timeout of R1b response. The sleep command has a R1b response. This response has a busy that has a specific timeout definition.
                    #controlVddf - TRUE to switch OFF Vccf power supply during going to Sleep state and to switch ON Vccf power supply during going from Sleep state.
                    #verifySleepState - TRUE to test the card state on awake command response. Has affect only if sleep is FALSE

                    #IDD measurement in sleep mode for deepSleep JIRA CTISW-5665

                    #End of if
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========  End OF DEEP SLEEP SET 1   ==========\n")

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========   START ON READ   ==========\n")

                self.__InitCard.Run(globalParameters)

                self.iddMesureInSleepMode_Read(globalParameters)  #Mesure IDD in Read Mode

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========   END ON READ   ==========\n")

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========    DEEP SLEEP SET 2   ==========\n")
                if int(globalParameters["IDD_DeepSleep"]) == 1: #Condition is always false and section include MMC API

                    self.__dvtLib.SelectCard(False)

                    # Commented below line as sddvt package is only for SD Cards not for MMC Cards
                    # self.__card.MMCSleepAwake(True,500,False,True)
                    #MMC sleep awake
                    #sleep - TRUE to switch to SLEEP from STANDBY, FALSE to awake from SLEEP to STANDBY.
                    #R1bTimeout - timeout of R1b response. The sleep command has a R1b response. This response has a busy that has a specific timeout definition.
                    #controlVddf - TRUE to switch OFF Vccf power supply during going to Sleep state and to switch ON Vccf power supply during going from Sleep state.
                    #verifySleepState - TRUE to test the card state on awake command response. Has affect only if sleep is FALSE

                    #IDD measurement in sleep mode for deepSleep JIRA CTISW-5665

                #End of if
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========  End OF DEEP SLEEP SET 2   ========== \n\n")

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========   START IN SLEEP   ==========\n")
                self.__PreSleepExec.Run(globalParameters)

                self.iddMesureInSleepMode_SleepMode() #read Hot insertion

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========   END IN SLEEP   ========== \n\n")

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========    DEEP SLEEP SET 3   ==========\n")

                if int(globalParameters["IDD_DeepSleep"]) == 1: #Condition is always false and section include MMC API

                    self.__dvtLib.SelectCard(False)

                    # Commented below line as sddvt package is only for SD Cards not for MMC Cards
                    # self.__card.MMCSleepAwake(True,500,False,True)
                    #MMC sleep awake
                    #sleep - TRUE to switch to SLEEP from STANDBY, FALSE to awake from SLEEP to STANDBY.
                    #R1bTimeout - timeout of R1b response. The sleep command has a R1b response. This response has a busy that has a specific timeout definition.
                    #controlVddf - TRUE to switch OFF Vccf power supply during going to Sleep state and to switch ON Vccf power supply during going from Sleep state.
                    #verifySleepState - TRUE to test the card state on awake command response. Has affect only if sleep is FALSE

                    #IDD measurement in sleep mode for deepSleep JIRA CTISW-5665

                    #End of if
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "==========  End OF DEEP SLEEP SET 3  ==========\n")

                #VDDH section end

                filename = os.path.join(self.__dirPath, "Current_Measurements_VDDH", str(self.__currentVoltage) + '.dat')

                # Check if the directory exists; if not, create it
                directory = os.path.dirname(filename)
                if not os.path.exists(directory):
                    os.makedirs(directory)

                # Now open the file in append mode to create it if it doesn't exist
                with open(filename, 'a') as file:
                    self.WriteGeneralResultsFile(filename)

                vddh_index = vddh_index + 1
                vddhRepresentation = int(globalParameters["VDDH_MilliVoltages"][vddh_index])
                vddh = vddhRepresentation * 50

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#"*150)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "************  VDDH SECTION END*****************")
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#"*150)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "WriteRegister Started\n")
        address = 160
        value = 1
        self.__sdCmdObj.WriteRegister(address,value)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "WriteRegister ReadRegister Value %d at address %d\n"%(value,address))

        self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Execution\n")

        return 0

    #Below function can be Added to common library
    def iddMesureInSleepMode_HotInsertionMode(self,iddMsrSmpRate=intToSampleRate[7],numberOfsamples = 100):
        '''
        IDD iddMesureInSleepMode_HotInsertionMode
        '''
        self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Started IDDMesureInSleepMode_HotInsertionMode\n")
        iddMsrParams = sdcmdWrap.PySIddMsrParams()
        iddBuf = ServiceWrap.Buffer.CreateBuffer(dataSize = 2000*4, patternType = 0x00, isSector = False)
        iddMsrParams.iddSampleBuffer =  iddBuf
        iddMsrParams.iddMsrSampleRate   =  iddMsrSmpRate
        iddMsrParams.numberOfSamples = numberOfsamples

        if self.__mesureVDDF:
            vddfIddMsrParams = sdcmdWrap.PySIddMsrParams()
            # Create a 2000 elements buffer, where each element is 4 bytes
            vddfIddBuf = ServiceWrap.Buffer.CreateBuffer(dataSize = 2000*4, patternType = 0x00, isSector = False)
            vddfIddMsrParams.iddSampleBuffer  =  vddfIddBuf
            vddfIddMsrParams.numberOfSamples  = numberOfsamples
        else:
            vddfIddMsrParams = None

        self.__results["hotInsertion"].startTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sdcmdWrap.CardIddMsrInSleepMode(numberOfsamples * 128, iddMsrParams, vddfIddMsrParams)
        self.__results["hotInsertion"].endTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Store results
        self.__results["hotInsertion"].numOfSamples = iddMsrParams.numberOfSamples
        self.__results["hotInsertion"].maximum =  iddMsrParams.iddHighest
        self.__results["hotInsertion"].minimum =  iddMsrParams.iddLowest
        self.__results["hotInsertion"].average =  iddMsrParams.iddAvg

        if self.__mesureVDDF:
            self.__results["hotInsertionVddf"].numOfSamples = iddMsrParams.numberOfSamples
            self.__results["hotInsertionVddf"].maximum =  vddfIddMsrParams.iddHighest
            self.__results["hotInsertionVddf"].minimum =  vddfIddMsrParams.iddLowest
            self.__results["hotInsertionVddf"].average =  vddfIddMsrParams.iddAvg

        self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed IDDMesureInSleepMode_HotInsertionMode\n")

        #End of iddMesureInSleepMode_HotInsertionMode

    def iddMesureInSleepMode_SleepMode(self,iddMsrSmpRate=intToSampleRate[7],numberOfsamples = 100):
        '''
        IDD MesureInSleepMode_SleepMode
        '''
        self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Started IDDMesureInSleepMode_SleepMode\n")

        iddMsrParams = sdcmdWrap.PySIddMsrParams()
        iddBuf = ServiceWrap.Buffer.CreateBuffer(dataSize = 2000*4, patternType = 0x00, isSector = False)
        iddMsrParams.iddSampleBuffer =  iddBuf
        iddMsrParams.iddMsrSampleRate   =  iddMsrSmpRate
        iddMsrParams.numberOfSamples = numberOfsamples

        if self.__mesureVDDF:
            vddfIddMsrParams = sdcmdWrap.PySIddMsrParams()
            # Create a 2000 elements buffer, where each element is 4 bytes
            vddfIddBuf = ServiceWrap.Buffer.CreateBuffer(dataSize = 2000*4, patternType = 0x00, isSector = False)
            vddfIddMsrParams.iddSampleBuffer  =  vddfIddBuf
            vddfIddMsrParams.numberOfSamples  = numberOfsamples
        else:
            vddfIddMsrParams = None

        self.__results["sleepMode"].startTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sdcmdWrap.CardIddMsrInSleepMode(numberOfsamples * 128, iddMsrParams, vddfIddMsrParams)
        self.__results["sleepMode"].endTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Store results
        self.__results["sleepMode"].numOfSamples = iddMsrParams.numberOfSamples
        self.__results["sleepMode"].maximum =  iddMsrParams.iddHighest
        self.__results["sleepMode"].minimum =  iddMsrParams.iddLowest
        self.__results["sleepMode"].average =  iddMsrParams.iddAvg

        if self.__mesureVDDF:
            self.__results["sleepModeVddf"].numOfSamples = iddMsrParams.numberOfSamples
            self.__results["sleepModeVddf"].maximum =  vddfIddMsrParams.iddHighest
            self.__results["sleepModeVddf"].minimum =  vddfIddMsrParams.iddLowest
            self.__results["sleepModeVddf"].average =  vddfIddMsrParams.iddAvg

        self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed IDDMesureInSleepMode_SleepMode\n")

        #End of iddMesureInSleepMode_SleepMode


    def iddMesureInSleepMode_Write(self,globalParameters):
        '''
        IDD iddMesureInSleepMode_Write
        '''
        self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Started IDDMesureInSleepMode_Write\n")

        PatternGenObj = PatternGen.PatternGen(self.vtfContainer,sdcmdWrap.Pattern.ANY_WORD,False,intToSampleRate[int(globalParameters["IDD_ActiveSampleRate"])],0,False,True,False,False,int(globalParameters["IDD_Pattern"]))
        self.__results["write"].startTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.__writeStartAdress = int(globalParameters["IDD_StartAddress"])
        self.__blocksToWrite = int(globalParameters["IDD_Blocks"])

        iddResults = PatternGenObj.MultipleWrite(self.__writeStartAdress,self.__blocksToWrite)
        self.__results["write"].endTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.__results["write"].numOfSamples = iddResults.iddMsrParams.numberOfSamples
        self.__results["write"].maximum =  int(old_div(iddResults.iddMsrParams.iddHighest, 1000))
        self.__results["write"].minimum =  int(old_div(iddResults.iddMsrParams.iddLowest, 1000))
        self.__results["write"].average =  int(old_div(iddResults.iddMsrParams.iddAvg, 1000))
        self.writeCommaSeparatedFile('WriteCurrent_Vddh', iddResults.iddMsrParams.numberOfSamples, iddResults.iddSampleBuffer)
        if self.__mesureVDDF:
            self.__results["readVddf"].maximum =  int(old_div(iddResults.vddfIddMsrParams.iddHighest, 1000))
            self.__results["readVddf"].minimum =  int(old_div(iddResults.vddfIddMsrParams.iddLowest, 1000))
            self.__results["readVddf"].average =  int(old_div(iddResults.vddfIddMsrParams.iddAvg, 1000))
            self.writeCommaSeparatedFile('WriteCurrent_Vddf', iddResults.vddfIddMsrParams.numberOfSamples, iddResults.vddfIddSampleBuffer)

        self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed IDDMesureInSleepMode_Write\n")

        #End of iddMesureInSleepMode_Write


    def iddMesureInSleepMode_Read(self,globalParameters):
        '''
        IDD iddMesureInSleepMode_Read
        '''
        self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Started IDDMesureInSleepMode_Read\n")

        PatternGenObj = PatternGen.PatternGen(self.vtfContainer,sdcmdWrap.Pattern.ANY_WORD,False,intToSampleRate[int(globalParameters["IDD_ActiveSampleRate"])],0,False,True,False,True,int(globalParameters["IDD_Pattern"]))
        self.__results["read"].startTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.__readStartAddress = int(globalParameters["IDD_StartAddress"])
        self.__blocksToRead = int(globalParameters["IDD_Blocks"])
        iddResults = PatternGenObj.MultipleRead(self.__readStartAddress,self.__blocksToRead)
        self.__results["read"].endTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.__results["read"].numOfSamples = iddResults.iddMsrParams.numberOfSamples
        self.__results["read"].maximum =  int(old_div(iddResults.iddMsrParams.iddHighest, 1000))
        self.__results["read"].minimum =  int(old_div(iddResults.iddMsrParams.iddLowest, 1000))
        self.__results["read"].average =  int(old_div(iddResults.iddMsrParams.iddAvg, 1000))
        self.writeCommaSeparatedFile('ReadCurrent_Vddh', iddResults.iddMsrParams.numberOfSamples, iddResults.iddSampleBuffer)
        if self.__mesureVDDF:
            self.__results["readVddf"].maximum =  int(old_div(iddResults.vddfIddMsrParams.iddHighest, 1000))
            self.__results["readVddf"].minimum =  int(old_div(iddResults.vddfIddMsrParams.iddLowest, 1000))
            self.__results["readVddf"].average =  int(old_div(iddResults.vddfIddMsrParams.iddAvg, 1000))
            self.writeCommaSeparatedFile('ReadCurrent_Vddf', iddResults.vddfIddMsrParams.numberOfSamples, iddResults.vddfIddSampleBuffer)

        self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed IDDMesureInSleepMode_Read\n")
        #End of iddMesureInSleepMode_Read

    def WriteGeneralResultsFile(self,filename):
        """
        WriteGeneralResultsFile
        """

        fp = open(filename,"w")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, '\n\n      ------------ Adapter Current Measurements -------------- \n')

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Program Revision                        : %s' % self.__results["hotInsertion"].startTime, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Date and Time                            : %s' % datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Card Serial Number                       : 0x%X' % (self.__ProductSerialNumber), fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Capacity is Sectors                      : %d' % (self.__cardMaxLba), fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'User Name/IP Address                     : %s / %s' % (os.getenv('USERNAME'), socket.gethostbyname(socket.gethostname())), fp)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Voltage                                  : %s' % self.__currentVoltage, fp)
        self.__dvtLib.CardInfo()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, '\n\n      ------------Hot Insertion Operation --------------')
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Start Date and Time                      : %s' % self.__results["hotInsertion"].startTime, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'End Date and Time                        : %s' % self.__results["hotInsertion"].endTime, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Hot Insertion Sample Size                : %d\n' % self.__results["hotInsertion"].numOfSamples, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'VDDH Current Measurements                : %s v' % str(self.__currentVoltage/1000.0), fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, '---------------------------------------------', fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Minimum Hot Insertion Current            : %d uA' % self.__results["hotInsertion"].minimum, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Maximum Hot Insertion Current            : %d uA' % self.__results["hotInsertion"].maximum, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Average Hot Insertion Current            : %d uA\n' % self.__results["hotInsertion"].average, fp)
        if self.__mesureVDDF:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'VDDF Current Measurements                : %sv' % str(self.__currentVoltage/1000.0), fp)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, '---------------------------------------------', fp)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Minimum Hot Insertion Current        : %d uA' % self.__results["hotInsertionVddf"].minimum, fp)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Maximum Hot Insertion Current        : %d uA' % self.__results["hotInsertionVddf"].maximum, fp)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Average Hot Insertion Current        : %d uA\n' % self.__results["hotInsertionVddf"].average, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, ' -------------------------------------------------------- \n', fp)


        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, '\n\n      ------------Sleep Operation -------------- \n', fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Start Date and Time                      : %s' % self.__results["sleepMode"].startTime, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'End Date and Time                        : %s' % self.__results["sleepMode"].endTime, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Sleep Sample Size                        : %d \n' % self.__results["sleepMode"].numOfSamples, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'VDDH Current Measurements                : %s v' % str(self.__currentVoltage/1000.0), fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, '--------------------------------------------- \n', fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Minimum Sleep Current                    : %d uA' % self.__results["sleepMode"].minimum, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Maximum Sleep Current                    : %d uA' % self.__results["sleepMode"].maximum, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Average Sleep Current                    : %d uA\n' % self.__results["sleepMode"].average, fp)
        if self.__mesureVDDF:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'VDDF Current Measurements                : %sv' % str(self.__currentVoltage/1000.0), fp)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, '---------------------------------------------', fp)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'VDDF Minimum Sleep Current                  : %d uA' % self.__results["sleepModeVddf"].minimum, fp)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'VDDF Maximum Sleep Current                  : %d uA' % self.__results["sleepModeVddf"].maximum, fp)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'VDDF Average Sleep Current                  : %d uA\n' % self.__results["sleepModeVddf"].average, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, ' -------------------------------------------------------- \n', fp)


        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, '\n\n      ------------Read Operation -------------- \n', fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Start Date and Time                      : %s' % self.__results["read"].startTime, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'End Date and Time                        : %s' % self.__results["read"].endTime, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Read LBA                                 : 0x%X' % self.__readStartAddress, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Read Block Count                         : 0x%X' % self.__blocksToRead, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Read Sample Size                         : %d ' % self.__results["read"].numOfSamples, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, '\n VDDH Current Measurements                : %sv' % str(self.__currentVoltage/1000.0), fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, '--------------------------------------------- ', fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Minimum Read Current                     : %d mA' % self.__results["read"].minimum, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Maximum Read Current                     : %d mA' % self.__results["read"].maximum, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Average Read Current                     : %d mA\n' % self.__results["read"].average, fp)
        if self.__mesureVDDF:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'VDDF Current Measurements                : %sv' % str(self.__currentVoltage/1000.0), fp)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, '---------------------------------------------', fp)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'VDDF Minimum Read Current                  : %d mA' % self.__results["readVddf"].minimum, fp)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'VDDF Maximum Read Current                  : %d mA' % self.__results["readVddf"].maximum, fp)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'VDDF Average Read Current                  : %d mA\n' % self.__results["readVddf"].average, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, ' -------------------------------------------------------- \n', fp)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, '\n\n      ------------Write Operation -------------- \n', fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Start Date and Time                      : %s' % self.__results["write"].startTime, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'End Date and Time                        : %s' % self.__results["write"].endTime, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Write LBA                                : 0x%X' % self.__writeStartAdress, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Write Block Count                        : 0x%X' % self.__blocksToWrite, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Write Sample Size                        : %d' % self.__results["write"].numOfSamples, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, '\n VDDH Current Measurements                : %sv' % str(self.__currentVoltage/1000.0), fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, '--------------------------------------------- ', fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Minimum Write Current                    : %d mA' % self.__results["write"].minimum, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Maximum Write Current                    : %d mA' % self.__results["write"].maximum, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'Average Write Current                    : %d mA\n' % self.__results["write"].average, fp)
        if self.__mesureVDDF:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'VDDF Current Measurements                : %sv' % str(self.__currentVoltage/1000.0), fp)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, '---------------------------------------------', fp)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'VDDF Minimum Write Current                 : %d mA' % self.__results["writeVddf"].minimum, fp)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'VDDF Maximum Write Current                 : %d mA' % self.__results["writeVddf"].maximum, fp)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, 'VDDF Average Write Current                 : %d mA' % self.__results["writeVddf"].average, fp)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, ' -------------------------------------------------------- \n', fp)

        #self.__logger.SetFileLogging(None,False)

        self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed to write to results file\n", fp)

        fp.close()

        #End of WriteGeneralResultsFile

    def writeCommaSeparatedFile(self, fileName, numOfSamples, buffer):
        """
        writeCommaSeparatedFile
        """
        self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Started to write comma seperated values to  file\n")
        try:
            self.__log_file_name = os.path.join(self.__dirPath,datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + "_" + fileName + "_" + socket.gethostname() + "_"  + str(self.__ProductSerialNumber) + "_" + str(self.__currentVoltage) + '.log')
            file = open(self.__log_file_name, 'w')
        except ValidationError.CVFGenericExceptions as exc:
            raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

        for i in range(numOfSamples):
            file.write('%d' % buffer.GetFourBytesToInt(i*4))
            if i != numOfSamples - 1:
                file.write(',')

        file.close()
        self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed  to write comma seperated values to  file\n")
        #End of writeCommaSeparatedFile

    # Testcase logic - Ends
# Testcase Class - Ends

# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_IDDSD_TC004_LowSpeed(self):
        obj = IDDSD_TC004_LowSpeed(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
