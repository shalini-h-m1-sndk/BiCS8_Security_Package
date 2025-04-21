"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : PQT_CA001_QuarterlyPartitionWRC.st3
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : PQT_CA001_QuarterlyPartitionWRC.py
# DESCRIPTION                    : For PQUAL Test
# PRERQUISTE                     : PQT_TC01_VoltageLogicCheck.py, PQT_UT01_Common_Init.py, PQT_UT02_HighSpeed_Init.py, PQT_UT03_UHS_Init.py, PQT_TC02_Stage1_Readout.py, PQT_TC03_Stage2_WriteReadQuarter.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=PQT_CA001_QuarterlyPartitionWRC --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 30-May-2024
# UPDATED BY                     : Shalini HM
# UPDATED DATE                   : 31-Jul-2024
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
    from builtins import *
from past.utils import old_div

# SDDVT - Dependent TestCases
import PQT_TC01_VoltageLogicCheck as VoltageLogicCheck
import PQT_UT01_Common_Init as Common_Init
import PQT_UT02_HighSpeed_Init as HighSpeed_Init
import PQT_UT03_UHS_Init as UHS_Init
import PQT_TC02_Stage1_Readout as stage1Readout
import PQT_TC03_Stage2_WriteReadQuarter as Stage2WriteReadQuarter

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
import time
from inspect import currentframe, getframeinfo
from threading import Thread

# Global Variables


# Testcase Class - Begins
class PQT_CA001_QuarterlyPartitionWRC(customize_log):
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
        self.__VoltageLogicCheck = VoltageLogicCheck.PQT_TC01_VoltageLogicCheck(self.vtfContainer)
        self.__Common_Init = Common_Init.PQT_UT01_Common_Init(self.vtfContainer)
        self.__HighSpeed_Init = HighSpeed_Init.PQT_UT02_HighSpeed_Init(self.vtfContainer)
        self.__UHSInit =  UHS_Init.PQT_UT03_UHS_Init(self.vtfContainer)
        self.__stage1Readout = stage1Readout.PQT_TC02_Stage1_Readout(self.vtfContainer)
        self.__stage2WriteReadQuarter =  Stage2WriteReadQuarter.PQT_TC03_Stage2_WriteReadQuarter(self.vtfContainer)

        #Thread.__init__(self)
        self.__globalParameters         = self.GetInitConfigValues()


    # Testcase logic - Starts
    def Run(self):
        """
        Does Read and Writes with differnt voltages
        """

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Execution Started\n")

        #Read parameter files values
        globalParameters = self.__globalParameters
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s" % globalParameters)

        #Download FPGA
        CVF_PATH = os.getenv('SANDISK_CTF_HOME_X64')
        if not CVF_PATH:
            raise ValidationError.TestFailError(self.fn, "Failed to Read CTF Path using SANDISK_SFCL_BE_HOME Env Variable")

        if self.currCfg.variation.sdconfiguration != "SDR104" or int(globalParameters["globalSpeedMode_Value"]) != 3: #for 104 config
            path = CVF_PATH + r"\FPGA\SD_LEGACY-SDR2_2-01-00-0001.bin"
        else:
            path = CVF_PATH + r"\FPGA\SD-SDR2_2-01-01-0061.bin"

        retunrvalue = sdcmdWrap.DownloadFpgaFile(path)
        if retunrvalue != 0:
            raise ValidationError.TestFailError(self.fn, "Failed to find/download SD_LEGACY-SDR2_2-01-00-0001.bin from Path " + path)
        self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FPGA downloaded SD_LEGACY-SDR2_2-01-00-0001")
        #Download FPGA

        #Low=2(1.8) high=1(3.3)
        globalParameters["FPGA_Low_Reg_enable"]= 1 #0 for 3.3 and 1 for 1.8

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###  -----------------  VDDF Variables   --------------")
        globalParameters["VDDF_enable"]= 0
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###  -----------------  end of VDDF Variables   --------------\n")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###  -----------------  VDDH Variables   --------------")
        globalParameters["Voltage_1"]= 3300 # 3.3 VOLT
        globalParameters["Voltage_2"]= 3600 # 3.6 VOLT
        globalParameters["Voltage_3"]= 2700 # 2.7 VOLT
        globalParameters["Voltage_4"]= 3000 # 3  VOLT
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###  -----------------  end of VDDH Variables   --------------\n")


        globalParameters["FilePatternLocation"]=None #Location for file that holds some pattern
        globalParameters["PatternNumber"]= 2 #2 = Incremental
        globalParameters["StartReadAddress"]=0x0 #Start Address for Read Operation
        globalParameters["BlockSizeRead"]= 0x200 #Block size for  Read Operation
        globalParameters["SingleReadAtEnd"]= True #if true enforce Single Read at the End of a multiple read operation
        globalParameters["SingleReadAtEnd_SIZE"]=16 #Number of Blocks from card end where Single Read would be enforced


        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###  -----------------  OTP Control   --------------")
        globalParameters["OTP"] =False #Card is OTP type
        globalParameters["WrittenOnce"]= False #if OTP - this flag will show that the card already written - so Read only with validation from this point
        globalParameters["FileSystemSize"]= 0x760 #If OTP card, this enforce that all read & write operation will start beyond this address.

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###  -----------------  End of OTP Control   --------------")

        globalParameters["LoopsDone"]=0

        self.__dvtLib.SwitchHostVoltageRegion(globalParameters["FPGA_Low_Reg_enable"])

        if int(globalParameters["ReadOnly"]) == True:
            globalParameters["WRITE"]= "NOP"

        #volatelogicchecking.st3
        self.__VoltageLogicCheck.Run(globalParameters)
        #volatelogicchecking.st3

        globalParameters["Volt"]= globalParameters["Voltage_1"]


        #Initialization section
        if int(globalParameters["InitMode_Value"]) == 0:#default initialization LS
            self.__Common_Init.Run(globalParameters)
        elif int(globalParameters["InitMode_Value"]) == 1:#HS initialization
            self.__HighSpeed_Init.Run(globalParameters)
        #elif int(globalParameters["InitMode_Value"]) == 2:#HS 75Khz initialization
            #hs75khzInit.PQT_UT01_Common_Init(self.vtfContainer).Run(globalParameters)
        #elif int(globalParameters["InitMode_Value"]) == 3:#EMMC initialization
            #emmcInit.CHZSCRIPTPQUALHIGHSPEED05_Init(self.vtfContainer).Run(globalParameters)
        elif int(globalParameters["InitMode_Value"]) == 4:#UHS initialization
            self.__UHSInit.Run(globalParameters)

        else:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Wrong Parameter file- Need updated file\n")
            raise ValidationError.TestFailError(self.fn, "Wrong Parameter file- Need updated file\n")

        #Get CID
        self.__sdCmdObj.GET_CID_VALUES()

        globalParameters["CardSize"] = sdcmdWrap.WrapGetMaxLBA()

        #Command line arg defines number for times to loop
        #if self.__optionValues["cycleCount"] > 1:
            #cyclecount  = self.__optionValues["cycleCount"]
        #else :#default loops to 10
            #cyclecount  = 10

        LoopsCounter = int(globalParameters["LoopsCounter"])
        while LoopsCounter > 0:

            #Start Address for Read Operation
            globalParameters["StartRead"] = int(globalParameters["StartReadAddress"])
            #Block Count for  Read Operation
            globalParameters["ReadSize"]= globalParameters["CardSize"] -  globalParameters["StartRead"]

            #if Single Read is enforced at card edge
            if int(globalParameters["SingleReadAtEnd"]) == True:
                #Block Count for  Read Operation
                globalParameters["ReadSize"]= globalParameters["ReadSize"] - globalParameters["SingleReadAtEnd_SIZE"]

            #Block Count for  Read Operation- Remember This value
            globalParameters["ReadSize_Const"] = globalParameters["ReadSize"]
            globalParameters["Now_EnforceSingleReadV"] = False

            #Stage 1*******************************************************
            #Read without compare for 4 times in quarters

            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#################Stage 1 started(Read in Four Quaters with 4 Voltages) ################\n")

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#################Stage 1 with Voltage 1 ################\n")
            globalParameters["Volt"]= globalParameters["Voltage_1"]
            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "With Voltage_1 %d\n"%globalParameters["Volt"])
            #Read the entire card without compare
            self.__stage1Readout.Run(globalParameters)
            #Set Frequency to 50 Mhz
            self.__sdCmdObj.SetFrequency(70000)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#################Stage 1 with Voltage 1 completed ################\n")

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#################Stage 1 with Voltage 2 ################\n")
            globalParameters["Volt"]= globalParameters["Voltage_2"]
            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "With Voltage_2 %d\n"%globalParameters["Volt"])
            #Read the entire card without compare
            self.__stage1Readout.Run(globalParameters)
            #Set Frequency to 50 Mhz
            self.__sdCmdObj.SetFrequency(70000)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#################Stage 1 with Voltage 2 completed ################\n")

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#################Stage 1 with Voltage 3 ################\n")
            globalParameters["Volt"]= globalParameters["Voltage_3"]
            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "With Voltage_3 %d\n"%globalParameters["Volt"])
            #Read the entire card without compare
            self.__stage1Readout.Run(globalParameters)
            #Set Frequency to 50 Mhz
            self.__sdCmdObj.SetFrequency(70000)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#################Stage 1 with Voltage 3 completed ################\n")

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#################Stage 1 with Voltage 4 ################\n")
            globalParameters["Volt"]= globalParameters["Voltage_4"]
            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "With Voltage_4 %d\n"%globalParameters["Volt"])
            #Read the entire card without compare
            self.__stage1Readout.Run(globalParameters)
            #Set Frequency to 50 Mhz
            self.__sdCmdObj.SetFrequency(70000)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#################Stage 1 with Voltage 1 completed ################\n")

            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#################Stage 1 completed ################\n")

            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#################Stage 2 started (Write and Read in Four Quaters with 4 Voltages)################\n")
            #Write and read with compare

            globalParameters["StartValidationAt"] =  0x0
            if globalParameters["OTP"] == True:
                globalParameters["StartValidationAt"] = globalParameters["FileSystemSize"]

            globalParameters["Size"] = old_div((globalParameters["CardSize"] - globalParameters["StartValidationAt"]), 4)
            globalParameters["StartAddress"] = globalParameters["StartValidationAt"]
            globalParameters["WrittenSize"]=  0
            globalParameters["Quarter"] =  1
            globalParameters["Volt"] = globalParameters["Voltage_1"]

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "################# Write the First Quarter of the card ################\n")
            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "With Voltage_1 %d\n"%globalParameters["Volt"])
            #Read compare the first Quarter
            #Read without compare the rest of the card
            globalParameters["SingleReadAtEnd"] = True
            globalParameters = self.__stage2WriteReadQuarter.Run(globalParameters)
            #Set Frequency to 50 Mhz
            self.__sdCmdObj.SetFrequency(70000)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "################# Write the Second Quarter of the card  ################\n")
            #Read compare the first half of the card
            #Read without compare the rest of the card
            globalParameters["Quarter"] =  2
            globalParameters["StartAddress"] = globalParameters["StartAddress"] + globalParameters["Size"]
            globalParameters["Volt"] = globalParameters["Voltage_2"]
            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "With Voltage_2 %d\n"%globalParameters["Volt"])

            globalParameters = self.__stage2WriteReadQuarter.Run(globalParameters)
            #Set Frequency to 50 Mhz
            #self.__adapter.SetHostFrequency(int(globalParameters["Freq"]) * 1000) #in Hertz
            self.__sdCmdObj.SetFrequency(70000)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "################# Write the Third Quarter of the card  ################\n")
            #Read compare the first three quarters of the card
            #Read without compare the rest of the card
            globalParameters["Quarter"] =  3
            globalParameters["StartAddress"] = globalParameters["StartAddress"] + globalParameters["Size"]
            globalParameters["Volt"] = globalParameters["Voltage_4"]
            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "With Voltage_4 %d\n"%globalParameters["Volt"])

            globalParameters = self.__stage2WriteReadQuarter.Run(globalParameters)
            #Set Frequency to 50 Mhz
            self.__sdCmdObj.SetFrequency(70000)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "################# Write the Fourth Quarter of the card  ################\n")
            #Write the fourth quarter of the card
            #Read compare the entire card
            globalParameters["Quarter"] =  4
            globalParameters["StartAddress"] = globalParameters["StartAddress"] + globalParameters["Size"]
            globalParameters["Volt"] = globalParameters["Voltage_3"]

            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "With Voltage_3 %d\n"%globalParameters["Volt"])

            globalParameters = self.__stage2WriteReadQuarter.Run(globalParameters)
            #Set Frequency to 50 Mhz
            self.__sdCmdObj.SetFrequency(70000)

            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#################Stage 2 completed ################\n")

            globalParameters["Volt"] = globalParameters["Voltage_1"]

            if globalParameters["OTP"] == True:
                globalParameters["WrittenOnce"] = True
            globalParameters["LoopsDone"] = globalParameters["LoopsDone"] + 1

            LoopsCounter -= 1

        self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Execution Completed\n")
        return 0


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

        self.cfgfile = os.path.join(self.__TestsDir,'SDDVT', 'SD', 'Chz', 'Pqualtest','ParameterFilesMaster', "Master_ParameterFile_SDR104_150MHz.txt")

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
    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_PQT_CA001_QuarterlyPartitionWRC(self):
        obj = PQT_CA001_QuarterlyPartitionWRC(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
