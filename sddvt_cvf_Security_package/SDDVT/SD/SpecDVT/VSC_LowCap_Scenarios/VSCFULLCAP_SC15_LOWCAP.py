"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : None
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : VSCFULLCAPSC15_Validation.py
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : VSCFULLCAP_SC15_LOWCAP.py
# DESCRIPTION                    : Video speed class performance measurement tests
# PRERQUISTE                     : CMD20_UT08_AUSize_Calculation.py, ACMD41_UT10_Set_BusSpeedMode.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=VSCFULLCAP_SC15_LOWCAP --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 30-May-2024
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
    from builtins import hex
    from builtins import range
    from builtins import *
from past.utils import old_div

# SDDVT - Dependent TestCases
import SDDVT.SD.SpecDVT.SD_SPEC_Ver3_00.CMD20.CMD20_UT08_AUSize_Calculation as AuSizeCalculation
import SDDVT.SD.SpecDVT.SD_SPEC_Ver3_00.ACMD41.ACMD41_UT10_Set_BusSpeedMode as SetBusModeSpeedMode

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
import math
from inspect import currentframe, getframeinfo

# Global Variables


# Testcase Class - Begins
class VSCFULLCAP_SC15_LOWCAP(customize_log):
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
        self.__AUsize = AuSizeCalculation.CMD20_UT08_AUSize_Calculation(self.vtfContainer)
        self.__globalSetBusSpeedModeObj = SetBusModeSpeedMode.ACMD41_UT10_Set_BusSpeedMode(self.vtfContainer)
        self.__patternGen = PatternGen.PatternGen(self.vtfContainer, writePattern = sdcmdWrap.Pattern.ANY_WORD,
                                                  doPerformance = True, iddMsrSampleRate = sdcmdWrap.EIddMsrSampleRate.ONE_MS,
                                                  iddNumOfSamples = 0, doLatency = True, doIddMeasurment = False,
                                                  doCompare = False, lbaTag = False, anyWord = 0xA5A5)
        self.__globalProjectConfVar = None
        self.__CardAddress = self.__dvtLib.GetFatAddr()
        self.__counter = 0
        self.__AUCapacity = 0
        self.__speedclass = 10
        self.__Tfw = []
        self.__SUsize = 0
        self.__RU_size = 512    # 512 KB is RU size
        self.__performanceError = 0
        self.__TimeDIR = 0
        self.__FATupdate = 0
        self.__DIRStartLba = 0x6000
        self.__skipFATupdate = 0
        self.__VSC_AU_SIZE = 0
        self.__selected_AU_list = []
        self.__total_AUs = 0
        self.__failure_reason = 0
        self.__failure_speedmode = ''
        self.__failureVSC = ''
        self.__FAT1 = 0x2000
        self.__FAT2 = 0x4000
        self.__CIADDRESS = 0X400000
        self.__RUCOUNT = 0
        self.__AUCOUNT = 0
        self.__speedmodes = 0
        self.__Randomdisturbance_counter = 0
        self.__FAT1start = 0
        self.__FAT1end = 0
        self.__FAT2start = 0
        self.__FAT2end = 0
        self.__C_SIZE = 0


    # Testcase logic - Starts
    def vsc6(self):
        """
        Name: VSC6
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC 6 validation started")
        self.__speedclass = 6
        frequency_vsc6 = [20, 40, 80]
        speedMode = ['SDR25', 'DDR50', 'SDR50']
        for index in range(self.__speedmodes):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC %d speedMode : %s" % (self.__speedclass, speedMode[index]))
            self.Compute_FATaddress()
            self.__globalProjectConfVar['globalSpeedMode'] = speedMode[index]
            #Call to utility script SetBusModeSpeedMode
            self.__globalSetBusSpeedModeObj.Run(self.__globalProjectConfVar)
            self.__dvtLib.GetCardTransferMode()
            self.__sdCmdObj.SetFrequency(frequency_vsc6[index] * 1000)
            self.__sdCmdObj.GetFrequency()
            self.Measure_Pw()

    def vsc10(self):
        """
        Name :vsc10
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC 10 validation started")
        self.__speedclass = 10
        frequency_vsc10 = [40, 40, 80]
        speedMode = ['SDR25', 'DDR50', 'SDR50']
        for index in range(self.__speedmodes):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC %d speedMode : %s" % (self.__speedclass, speedMode[index]))
            self.Compute_FATaddress()
            self.__globalProjectConfVar['globalSpeedMode'] = speedMode[index]
            #Call to utility script SetBusModeSpeedMode
            self.__globalSetBusSpeedModeObj.Run(self.__globalProjectConfVar)
            self.__dvtLib.GetCardTransferMode()
            self.__sdCmdObj.SetFrequency(frequency_vsc10[index] * 1000)
            self.__sdCmdObj.GetFrequency()
            self.Measure_Pw()

    def vsc30(self):
        """
        Name :vsc30
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC 30 validation started")
        self.__speedclass = 30
        frequency_vsc30 = [45, 90]
        speedMode = ['DDR50','SDR50']
        for index in range(self.__speedmodes):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC %d speedMode : %s" % (self.__speedclass, speedMode[index]))
            self.Compute_FATaddress()
            self.__globalProjectConfVar['globalSpeedMode'] = speedMode[index]
            #Call to utility script SetBusModeSpeedMode
            self.__globalSetBusSpeedModeObj.Run(self.__globalProjectConfVar)
            self.__dvtLib.GetCardTransferMode()
            self.__sdCmdObj.SetFrequency(frequency_vsc30[index] * 1000)
            self.__sdCmdObj.GetFrequency()
            self.Measure_Pw()

    def Compute_exFAT_CSIZE(self):
        argument = old_div((((self.__C_SIZE + 1) * 512) * 1024), 512)

        if (((self.__C_SIZE + 1) * 512) > 32 * 1024 * 1024) and (((self.__C_SIZE + 1) * 512) < 200 * 1024 * 1024):
            SC = 256
            BU = 32768
        elif (((self.__C_SIZE + 1) * 512) > 200 * 1024 * 1024 ) and (((self.__C_SIZE + 1) * 512) <= 512 * 1024 * 1024 ):
            SC = 512
            BU = 65536
        elif (((self.__C_SIZE + 1) * 512) > 512 * 1024 * 1024) and (((self.__C_SIZE + 1) * 512) < 2048 * 1024 * 1024):
            SC = 1024
            BU = 131072

        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cluster size: %s" % SC)

        SS = 512
        PO = BU
        TS = argument
        VL = TS - BU
        #print TS
        FATbits = 32
        FATOFFSET = old_div(BU, 2)
        FATLENGTH = old_div(BU, 2)
        BITMAPSTART = BU
        Clustercount = old_div((TS - BU * 2), SC)
        BITMAPSIZE = old_div(Clustercount, 8)
        BITMAPSIZE = math.ceil(old_div(BITMAPSIZE, 512))

        self.__FAT1start = int(FATOFFSET + BU)
        self.__FAT1end = self.__FAT1start + int(FATLENGTH) - 1
        self.__FAT2start = int(BITMAPSTART + BU)
        self.__FAT2end = self.__FAT2start + int(BITMAPSIZE) - 1


    def Compute_FAT32_CSZIZE(self):
        argument = old_div((((self.__C_SIZE + 1) * 512) * 1024), 512)
        SC = 64
        SS = 512
        BU = 8192
        TS = argument - BU
        #print TS
        FATbits = 32
        SF = math.ceil(old_div(((old_div(TS, SC)) * FATbits), (SS * 8)))

        NOM = BU
        RSC = BU - 2 * SF
        if (RSC <9):
            RSC = RSC + BU

        SSA =   RSC + 2 * SF
        MAX = (old_div((TS - NOM - SSA ), SC)) + 1
        SF1 = math.ceil(old_div((2 + (MAX + 1) * FATbits), (SS * 8 )))
        if (SF > SF1):
            SF = SF -1
            RSC = BU - 2 * SF
            SSA =   RSC + 2 * SF
            MAX = (old_div((TS - NOM - SSA ), SC)) + 1
            SF1 = math.ceil(old_div((2 + (MAX + 1) * FATbits), (SS * 8 )))

        if (SF1 > SF):
            SSA = SSA + BU
            RSC = RSC + BU
            MAX = (old_div((TS - NOM - SSA ), SC)) + 1
            SF1 = math.ceil(old_div((2 + (MAX + 1) * FATbits), (SS * 8 )))
        if (RSC < 0):
            self.__FAT1start = int(BU + RSC + BU)
        else :
            self.__FAT1start = int(BU + RSC)
        self.__FAT1end = self.__FAT1start+ (int(SF))
        self.__FAT2start = self.__FAT1end + 1
        self.__FAT2end = self.__FAT2start + (int(SF))

    def Compute_FATaddress(self):
        self.__FAT1start = 0x2000
        self.__FAT1end = 0x3FFF
        self.__FAT2start = 0x4000
        self.__FAT2end = 0x7FFF

        self.__sdCmdObj.Cmd7(deSelect = True)
        CSD_Buffer = self.__sdCmdObj.Cmd9()
        self.__sdCmdObj.Cmd7()
        C_SIZE = hex(CSD_Buffer.GetFourBytesToInt(8, little_endian=False) & 0x3fffff00)[:-2]
        #print "C_SIZE:", C_SIZE
        self.__C_SIZE = int(C_SIZE, 16)
        if (((self.__C_SIZE + 1) * 512) > 32 * 1024 * 1024): #EXFAT - FAT and Bitmap
            self.Compute_exFAT_CSIZE()
            fileSystem = "EXFAT"
        elif (((self.__C_SIZE + 1) * 512) > 2 * 1024 * 1024):
            if ((((self.__C_SIZE + 1) * 512) < 32 * 1024 * 1024)):     #FAT32 - FAT1 and FAT2
                self.Compute_FAT32_CSZIZE()
                fileSystem = "FAT32"
        else: #FAT16
            self.__FAT1start = 0x2000
            self.__FAT1end = 0x3FFF
            self.__FAT2start = 0x4000
            self.__FAT2end = 0x7FFF


        # file42Buf = self.__dvtLib.ReadFirmwareFile(42)
        # if (((C_SIZE+1)*512) > 32*1024*1024 ): #EXFAT - FAT and Bitmap
        #     self.__FAT1start = file42Buf.GetFourBytesToInt(0x58)
        #     fatsize = file42Buf.GetFourBytesToInt(0x5C)
        #     self.__FAT1end = self.__FAT1start + fatsize
        #     self.__FAT2start = file42Buf.GetFourBytesToInt(0x65)
        #     bitmapsize = file42Buf.GetFourBytesToInt(0x69)
        #     self.__FAT2end = self.__FAT2start + bitmapsize
        # elif (((((C_SIZE+1)*512) > 2*1024*1024) and (((C_SIZE+1)*512) < 32*1024*1024))) :     #FAT32 - FAT1 and FAT2
        #     self.__FAT1start = file42Buf.GetFourBytesToInt(0x58)
        #     fatsize = file42Buf.GetFourBytesToInt(0x5C)
        #     self.__FAT1end = self.__FAT1start + fatsize
        #     self.__FAT2start = self.__FAT1end
        #     self.__FAT2end = self.__FAT2start + fatsize
        # elif (((C_SIZE+1)*512) < 2*1024*1024):
        #     #dummy
        #     print ''

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FAT1 Start : 0x%X FAT1 End : 0x%X, FAT2 Start : 0x%X, FAT2 end : 0x%X" % (self.__FAT1start, self.__FAT1end, self.__FAT2start, self.__FAT2end))
        self.__FAT1 = self.__FAT1start
        self.__FAT2 = self.__FAT2start
        self.PopulateMBR(fileSystem)

    def PopulateMBR(self,fileSystem):
        self.isPBRSameAsMBR = False
        self.MBRBuffer = ServiceWrap.Buffer.CreateBuffer(1,0x0)
        self.MBRBuffer.SetTwoBytes(0x1FE, 0xAA55)

        if(self.isPBRSameAsMBR == True):
            self.addresstoStoreInPBRoffset = 0XFFFFFFFF
            self.MBRBuffer.SetFourBytes(0x1C6, self.addresstoStoreInPBRoffset)
            self.addresstoStoreInPBRoffset = 0x0
            self.PBRBuffer = self.PopulatePBR(fileSystem, self.MBRBuffer)
        else:
            PBRBuffer = ServiceWrap.Buffer.CreateBuffer(1,0x0)
            self.addresstoStoreInPBRoffset = 0x8000
            self.MBRBuffer.SetFourBytes(0x1C6,self.addresstoStoreInPBRoffset)
            PBRBuffer = self.PopulatePBR(fileSystem, PBRBuffer)
            self.__sdCmdObj.Cmd25(startLbaAddress = self.addresstoStoreInPBRoffset, transferLen = 0x1, writeDataBuffer = PBRBuffer)
            self.__sdCmdObj.Cmd12()
            self.__sdCmdObj.Cmd25(startLbaAddress = 0x0, transferLen = 1, writeDataBuffer = self.MBRBuffer)
            self.__sdCmdObj.Cmd12()
            self.MBRBuffer.PrintToLog()

    def PopulatePBR(self, fileSystem, PBRBuffer):
        #global VSC_FAT1_START_ADDRESS,VSC_FAT1_END_ADDRESS,VSC_FAT2_START_ADDRESS,VSC_FAT2_END_ADDRESS
        PBRBuffer.SetByte(0x0, 0xEB)
        PBRBuffer.SetTwoBytes(0x1FE, 0XAA55)

        if(fileSystem == "EXFAT"):
            PBRBuffer.SetRawStringChar(offset = 0x3, value = "EXFAT     ", strLen = 10)
            self.FAT1StartAddress = self.__FAT1start
            self.FAT1Length = self.__FAT1end - self.__FAT1start + 1
            self.BitmapAddress = self.__FAT2start
            self.clusterCount = (self.__FAT2end - self.__FAT2start + 1) * 8 * 512   #This value is in bits

            #if(self.__cardCapacity == 64):
                #self.FATAddressToStoreAt0x40 = 0x8000  #Taken from the trace
                #self.FATAddressToStoreAt0x50 = 0x4000
            ##endif

            #else:
            self.FATAddressToStoreAt0x40 = random.randrange(0x0, self.FAT1StartAddress, 0x1000)
            self.FATAddressToStoreAt0x50 = self.FAT1StartAddress - self.FATAddressToStoreAt0x40

            PBRBuffer.SetFourBytes(0x40, self.FATAddressToStoreAt0x40)
            PBRBuffer.SetFourBytes(0x50, self.FATAddressToStoreAt0x50)
            PBRBuffer.SetFourBytes(0x54, self.FAT1Length)
            PBRBuffer.SetFourBytes(0x5C, self.clusterCount)
            self.BitmapLength = self.__FAT2end - self.__FAT2start + 1
            self.FATEndAddress = self.__FAT2end

        elif(fileSystem == "FAT32"):
            PBRBuffer.SetRawStringChar(offset = 0x52, value = "FAT32     ", strLen = 10)
            #self.FAT1StartAddress = self.randomObj.randrange(0x2000,0x4000) + self.addresstoStoreInPBRoffset
            self.FAT1StartAddress = self.__FAT1start
            self.FAT1Length = self.__FAT1end - self.__FAT1start + 1

            self.FAT2Address = self.__FAT2start
            self.FAT2Length = self.__FAT2end - self.__FAT2start + 1

            #self.BitmapLength     = self.randomObj.randrange(0x1,0x200)
            self.FATAddressToStoreAt0xE = self.FAT1StartAddress - self.addresstoStoreInPBRoffset
            assert self.FATAddressToStoreAt0xE > 0x0

            PBRBuffer.SetTwoBytes(0xE, self.FATAddressToStoreAt0xE)
            PBRBuffer.SetFourBytes(0x24, self.FAT1Length)
        PBRBuffer.PrintToLog()
        return PBRBuffer

    def ReleaseDIR(self):
        """
        Name :Release DIR
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*****Release DIR slot 1*******")
        #ReleaseDIR slot1
        Argument = 0x88000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.050)        #50ms delay

    def UpdateDIR(self):
        """
        Name : Update DIR
        """
        #Update DIR 1st Slot
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*****Update DIR slot 1*******")
        Argument = 0x18000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.010)        #10ms delay

        #Write DIR
        self.__DIRStartLba = random.randint(int(self.__FAT2end+10),0x1FFFFF)  # Any address from 0x6000 to first 1GB of card capacity
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DIR selected address : %x" % self.__DIRStartLba)

        DIRblockCount = 1
        perfValue = self.MultipleWrite(self.__DIRStartLba, DIRblockCount)
        performance = float(perfValue.perfReadWrite.perfResults) / (1000 * 1000)
        try:
            TimeDIR = old_div((old_div(512, performance)), 1000)
        except ZeroDivisionError:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "UpdateDir performance value : %s" % performance)
        else:
            if (TimeDIR > 250):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*********[ERROR] Write DIR after Update DIR took > 250ms********")
                #raise ValidationError.TestFailError(self.fn, "Write DIR after Update DIR took > 250ms")
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Write DIR performance [MBps]: %f" % performance)
                self.__performanceError = 1
                self.__failure_reason = self.__failure_reason | 1 << 7


    def FATWrite(self):
        """
        Name : FATWrite
        """

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FAT & DIR write started")
        self.__RUCOUNT = self.__RUCOUNT + 1

        #32GB-FAT1:2000-3FFF    FAT2:4000-5FFF
        #FAT1 = random.randint(0x2000, 0x3FDF)
        #self.__FAT1 = 0x2000
        #FAT2 = random.randint(0x4000, 0x5FDF)
        #self.__FAT2 = 0x4000
        blockCount = 0x20    # 16K

        #Multiple FAT write & read
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FAT1 address : %x" % self.__FAT1)
        perfValue = self.MultipleWrite(self.__FAT1, blockCount)
        performance = float(perfValue.perfReadWrite.perfResults) / (1000 * 1000)

        try:
            TimeFAT1 = old_div((old_div((blockCount * 512), performance)), 1000)       #Converting time (msec)
        except ZeroDivisionError:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FAT1write performance value : %s" % performance)
            TimeFAT1 = 0
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FAT1 timing [msec]: %f" % TimeFAT1)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FAT2 address : %x" % self.__FAT2)
        perfValue = self.MultipleWrite(self.__FAT2, blockCount)
        performance = float(perfValue.perfReadWrite.perfResults) / (1000 * 1000)

        try:
            TimeFAT2 = old_div((old_div((blockCount * 512), performance)), 1000)
        except ZeroDivisionError:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FAT2write performance value : %s" % performance)
            TimeFAT2 = 0
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FAT2 timing [msec]: %f" % TimeFAT2)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DIR address:%x" % self.__DIRStartLba)
        blockCount = 0x1 #512b
        perfValue = self.MultipleWrite(self.__DIRStartLba, blockCount)
        performance = float(perfValue.perfReadWrite.perfResults) / (1000 * 1000)

        try:
            TimeDIR = old_div((old_div((blockCount * 512), performance)), 1000)                                    #Converting time to (msec) since DIR is 512
        except ZeroDivisionError:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TimeDir performance value : %s" % performance)
            TimeDIR = 0
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DIR update timing [msec]: %f" %TimeDIR)

        if TimeFAT1 != 0 and TimeFAT2 != 0 and TimeDIR != 0:
            Time = TimeFAT1 + TimeFAT2 + TimeDIR
            self.__Tfw.append(Time)

        if (len(self.__Tfw) == 8):
                #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "list:%s" % self.__Tfw)
            TfwAvg = old_div(sum(self.__Tfw),len(self.__Tfw))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TfwAvg [msec]: %f" % TfwAvg)
            TfwMax = max(self.__Tfw)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TfwMax [msec]: %f" % TfwMax)

            self.__Tfw.remove(self.__Tfw[0])

            if (TfwAvg > 100):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "In VSC %d & speed mode %s" % (self.__speedclass, self.__globalProjectConfVar['globalSpeedMode']))
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*********[ERROR] Tfw average > 100ms : %s ********" % self.__globalProjectConfVar['globalSpeedMode'])
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TfwAvg [msec]: %f" % TfwAvg)
                #raise ValidationError.TestFailError(self.fn, "Tfw average > 100ms")
                self.__performanceError = 1
                #self.__failure_reason = 1
                self.__failure_reason = self.__failure_reason | 1 << 0
            if (TfwMax > 750):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*********[ERROR] Tfw max > 750ms : %s ********" % self.__globalProjectConfVar['globalSpeedMode'])
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TfwMax [msec]: %f" % TfwMax)
                #raise ValidationError.TestFailError(self.fn, "Tfw max > 750ms")
                self.__performanceError = 1
                #self.__failure_reason = 2
                self.__failure_reason = self.__failure_reason | 1 << 1
        self.CI_Write()
        if ( self.__RUCOUNT == 16) : # increment FAT, DIR and CI address per 16 access
            self.__FAT1 = self.__FAT1 + 32
            if (self.__FAT1 + 32 > self.__FAT1end):
                self.__FAT1 = self.__FAT1start
            self.__FAT2 = self.__FAT2 + 32
            if (self.__FAT2 + 32 > self.__FAT2end):
                self.__FAT2 = self.__FAT2start
            self.__RUCOUNT = 0

    def CI_Write(self):
        """
        Name: Random_Write_Disturbance
        """
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*******CI Write**********")

        blockCount = 0x1 # 1 block
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CI write address : %x" % self.__CIADDRESS)
        perfValue = self.MultipleWrite(self.__CIADDRESS, blockCount)
        performance = float(perfValue.perfReadWrite.perfResults) / (1000 * 1000)
        try:
            TimeCI = old_div((old_div(512, performance)), 1000)
        except ZeroDivisionError:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CI_Write performance value : %f" % performance)
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CI write timing [msec]: %f" % TimeCI)
            if (TimeCI > 250):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*********[ERROR] CI write > 250ms : %s ********" % self.__globalProjectConfVar['globalSpeedMode'])
                self.__performanceError = 1
                #self.__failure_reason = 3
                self.__failure_reason = self.__failure_reason | 1 << 2

    def Random_Write_Disturbance(self):
        """
        Name: Random_Write_Disturbance
        """

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*******Random Write Disturbance**********")
        if (self.__Randomdisturbance_counter < 2048):
            blockCount = 0x80 # 64K Chunk
            for i in range(8): #
                randomRU = random.randrange(0x200000, 0x3FFFFF, 0x80) # from 1GB to 2B space in card capacity
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "random RU address : %x" % randomRU)
                perfValue = self.MultipleWrite(randomRU, blockCount)
                performance = float(perfValue.perfReadWrite.perfResults) / (1000 * 1000)
                #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%d Random write disturbance: RU Performance [MB/Sec] :%f" % ((i + 1), performance))
                try:
                    Time_rand_write = old_div((old_div(65536, performance)), 1000)
                except ZeroDivisionError:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Random_Write_Disturbance performance value : %f" % performance)
                else:
                    if (Time_rand_write > 250):
                        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*********[ERROR] Random write > 250ms : %s ********" % self.__globalProjectConfVar['globalSpeedMode'])
                        self.__performanceError = 1
                        #self.__failure_reason = 4
                        self.__failure_reason = self.__failure_reason | 1 << 3
            self.__Randomdisturbance_counter = self.__Randomdisturbance_counter + 1

    def Precondition_card(self):
        """
        Name: Precondition_card
        """
        # 75% capacity filled in VSC pattern with 1FAT update per RU, DIR update to a single address
        #FAT1:2000-3FFF    FAT2:4000-5FFF DIR : 0x6000 AU start : 0x600000

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*******Precondition card**********")
        self.__globalProjectConfVar['globalSpeedMode']='SDR50'
        self.__globalSetBusSpeedModeObj.Run(self.__globalProjectConfVar)
        self.__dvtLib.GetCardTransferMode()

        self.__sdCmdObj.SetFrequency(100*1000)
        self.__sdCmdObj.GetFrequency()
        FAT_blockCount = 0x20    # 16KB
        DIR_blockCount = 0x1     # 512 B
        blockCount = 0x400 # 512K Chunk - RU SIZE
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card MAx LBA : %x" % self.__cardMaxLba)
        RUaddress = 0x600000 # start after 3GB
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Precondition start address : %x" % RUaddress)
        ru_count = 0
        #"set free AU "
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Free AU : RUaddress:0x%x" % (old_div(RUaddress, 1024)))
        Argument = 0x7F000000 + (old_div(RUaddress, 1024))
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.250)        #250ms delay

        while (RUaddress < (old_div(self.__cardMaxLba * 3, 4))):
            if (ru_count == 8 * self.__RUinAU):
                #"set free AU "
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Free AU : RUaddress:0x%x" % (old_div(RUaddress, 1024)))
                Argument = 0x7F000000 + (old_div(RUaddress, 1024))
                self.__sdCmdObj.Cmd20(Argument)
                time.sleep(0.250)        #250ms delay
                ru_count = 0
            try:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "startAddress 0x%X with blockcount 0x%X\n" % (RUaddress, blockCount))
                perfValue = self.__patternGen.MultipleWrite(RUaddress, blockCount)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC -Precondition RU write Failed with error :%s\n" % exc.GetFailureDescription())
                raise ValidationError.TestFailError(self.fn, "VSC -Precondition RU write Failed with error :%s\n" % exc.GetFailureDescription())

            FAT1 = random.randint(0x2000, 0x3FDF)
            FAT2 = random.randint(0x4000, 0x5FDF)
            try:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "startAddress 0x%X with blockcount 0x%X\n" % (FAT1,FAT_blockCount))
                perfValue = self.__patternGen.MultipleWrite(FAT1, FAT_blockCount)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC -Precondition FAT1 write Failed with error :%s\n" % exc.GetFailureDescription())
                raise ValidationError.TestFailError(self.fn, "VSC -Precondition FAT1 write Failed with error :%s\n" % exc.GetFailureDescription())

            try:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "startAddress 0x%X with blockcount 0x%X\n" % (FAT2,FAT_blockCount))
                perfValue = self.__patternGen.MultipleWrite(FAT2, FAT_blockCount)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC -Precondition FAT2 write Failed with error :%s\n" % exc.GetFailureDescription())
                raise ValidationError.TestFailError(self.fn, "VSC -Precondition FAT2 write Failed with error :%s\n" % exc.GetFailureDescription())

            try:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "startAddress 0x6000 with blockcount 0x%X\n" % (DIR_blockCount))
                perfValue = self.__patternGen.MultipleWrite(0x6000, DIR_blockCount)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC -Precondition DIR write Failed with error :%s\n" % exc.GetFailureDescription())
                raise ValidationError.TestFailError(self.fn, "VSC -Precondition DIR write Failed with error :%s\n" % exc.GetFailureDescription())

            RUaddress = RUaddress + 0x400
            ru_count = ru_count + 1

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Precondition end address : %x" % (RUaddress - 0x400))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*******Precondition card complete**********")

    def MultipleWrite(self, AU_address, blockCount):
        try:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "startAddress 0x%X with blockcount 0x%X\n" % (AU_address, blockCount))
            perfValue = self.__patternGen.MultipleWrite(AU_address, blockCount)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC Failed with error :%s\n" % exc.GetFailureDescription())
            raise ValidationError.TestFailError(self.fn, "*******[Error] [Unexpected] VSC Validation Failed with error :%s \n  *********" % exc.GetFailureDescription())
        return perfValue

    def Measure_Pw(self):

        #Name : Measure_Pw
        VSC_PW = [6, 10, 30, 60, 90]
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***********Pw Measurement started**************")
        AUList = []
        read_AUList = []
        self.__AUCOUNT = 0

        blockCount = 0x400              # 1 RU size is 512 kB

        self.__sdCmdObj.Cmd55()
        sdStatus = self.__sdCmdObj.ACmd13()

        # AU selection
        #AU start -> first AU after 3GB of card capacity
        #AU end -> last AU of the card

        AU_start = 0x600000
        AU_SIZE_Sectors = (old_div(self.__VSC_AU_SIZE * 1024 * 1024, 512))
        if (len(self.__selected_AU_list) == 0):
            if (AU_start % AU_SIZE_Sectors) > 0:
                AU0 = ((old_div(AU_start, AU_SIZE_Sectors)) + 1) * AU_SIZE_Sectors
                AU0 = old_div(AU0, AU_SIZE_Sectors)
            else:
                AU0 = old_div(AU_start, AU_SIZE_Sectors)

            if self.__cardMaxLba % AU_SIZE_Sectors != 0:
                AU1 = (old_div(self.__cardMaxLba, AU_SIZE_Sectors) - 1) * AU_SIZE_Sectors
                AU1 = old_div(AU1, AU_SIZE_Sectors)
            else:
                AU1 = (old_div(self.__cardMaxLba, AU_SIZE_Sectors)) - 1

            #self.__selected_AU_list.append(AU1)
            self.__total_AUs = AU1 - AU0
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Total AUs:%s" % (self.__total_AUs))
            random_AU = AU0

            while len(self.__selected_AU_list) < self.__total_AUs: # AUs filled up sequentially
                self.__selected_AU_list.append(random_AU)
                random_AU = random_AU + 1

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "selected AUs:%s" % (self.__selected_AU_list))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "size of selected AUs:%s" % len(self.__selected_AU_list))

        self.UpdateDIR()

        #"set free AU "
        RUnum = (old_div((self.__AUCapacity * 1024 * self.__selected_AU_list[0]), 512))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Free AU : RUnum:0x%x" % RUnum)

        Argument = (0x7F000000 + RUnum) # Bundle of 8 AUs

        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.250)        #250ms delay

        #start Recording
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Start Recording")
        Argument = 0x8000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(1)        #1s delay
        RUperf = 0
        read_RUperf = 0
        counter = 0
        RUwrite_time = 0
        RUread_time = 0

        for loop_count in range(self.__total_AUs): # all AUs to be checked for Pw
            Address_in_AU = self.__selected_AU_list[loop_count] * AU_SIZE_Sectors
            SUList = []
            read_SUList = []
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "address in AU%d: %x" % (loop_count,Address_in_AU))

            write_PerformanceZero_count = 0
            Read_PerformanceZero_count = 0

            for i in range(self.__RUinAU):
                perfValue = self.MultipleWrite(Address_in_AU, blockCount)
                performance = old_div((float(perfValue.perfReadWrite.perfResults)), (1000 * 1000))  # converting performance to MB/s
                try:
                    write_time = old_div((old_div((blockCount * 512), performance)), 1000)
                except ZeroDivisionError:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "write_time performance value : %f" % performance)
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%d RU write Performance [MB/Sec] :%f" % ((i + 1), performance))
                    write_PerformanceZero_count = write_PerformanceZero_count + 1
                    write_time = 0
                else:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "In VSC %d & speed mode %s" % (self.__speedclass, self.__globalProjectConfVar['globalSpeedMode']))
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%d RU write Performance [MB/Sec] :%f" % ((i + 1), performance))
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%d RU write Performance  :%fms" % ((i + 1), write_time))

                read_perfValue = self.__patternGen.MultipleRead(Address_in_AU, blockCount)
                read_performance = old_div((float(read_perfValue.perfReadWrite.perfResults)),(1000*1000))  # converting performance to MB/s
                try:
                    read_time = old_div((old_div((blockCount * 512), read_performance)), 1000)
                except ZeroDivisionError:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "read_time performance value : %f" % read_performance)
                    Read_PerformanceZero_count = Read_PerformanceZero_count + 1
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%d RU read Performance [MB/Sec] :%f" % ((i + 1), read_performance))
                    read_time = 0
                else:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "In VSC %d & speed mode %s" % (self.__speedclass, self.__globalProjectConfVar['globalSpeedMode']))
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%d RU read Performance [MB/Sec] :%f" % ((i + 1), read_performance))
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%d RU read Performance  :%fms" % ((i + 1), read_time))


                Address_in_AU = Address_in_AU + blockCount
                RUperf = performance + RUperf
                RUwrite_time = write_time + RUwrite_time

                # if ((loop_count > 0) and (i==1)):
                #     RUwrite_time = RUwrite_time + 10 #to account time of Set Free AU - 10ms observed for Sparrow

                read_RUperf = read_performance + read_RUperf
                RUread_time = read_time + RUread_time
                counter = counter + 1
                if (counter == self.__RUinSU):
                    if self.__RUinSU==write_PerformanceZero_count:
                        raise ValidationError.TestFailError(self.fn, "*******[Error] [Unexpected] Write performance got 0 MB/s for all RuinSu *********")
                    if self.__RUinSU == Read_PerformanceZero_count:
                        raise ValidationError.TestFailError(self.fn, "*******[Error] [Unexpected] Read performance got 0 MB/s for all RuinSu *********")
                    SUAvg=old_div(RUperf, (self.__RUinSU - write_PerformanceZero_count))
                    SUPwAvg = old_div((old_div((self.__RUinSU * blockCount * 512), RUwrite_time)), 1000)
                    #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Write performance of SU [MB/Sec]: %f" % SUAvg)
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Write performance of SU [MB/Sec]: %f" % SUPwAvg)
                    SUList.append(SUPwAvg)

                    SUAvg=old_div(read_RUperf,(self.__RUinSU-Read_PerformanceZero_count))
                    SUPrAvg = old_div((old_div((self.__RUinSU * blockCount * 512), RUread_time)), 1000) # [(RU_Count* 0x400 * 512)/time_Taken_for_all_RUs)/1000
                    #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Read performance of SU [MB/Sec]: %f" % SUAvg)
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Read performance of SU [MB/Sec]: %f" % SUPrAvg)
                    read_SUList.append(SUPrAvg)
                    RUperf = 0
                    read_RUperf = 0
                    RUwrite_time = 0
                    RUread_time = 0
                    counter = 0

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SUList: %s" % SUList)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "read_SUList: %s" % read_SUList)
            read_AUList.append(min(read_SUList))
            AUList.append(min(SUList))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*********************Write performance of AU%d in [MB/Sec]: %f **********************" % (loop_count,min(SUList)))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*********************Read performance of AU%d in [MB/Sec]: %f **********************" % (loop_count,min(read_SUList)))
            #self.Random_Write_Disturbance()

            self.__AUCOUNT = self.__AUCOUNT + 1 #increment AU count

            if ( self.__AUCOUNT % 2 == 0 ) : # FAT update per 2 AU
                if (self.__skipFATupdate == 0):
                    self.FATWrite()
                    #Release DIR slot and update new DIR slot
                    self.ReleaseDIR()
                    self.UpdateDIR()
                    self.__CIADDRESS = random.randrange(0x400000, 0x5FFFFF) # CI address from 2GB to 3B space in card capacity
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CI selected address : %x" %self.__CIADDRESS)

            if (loop_count < (self.__total_AUs-1)):
                #"set free AU " per bundle of 8 AU
                if ( self.__AUCOUNT % 8 == 0 ) : # Set Free AU per 8 AUs as AUs are written sequentially
                    RUnum = (old_div((self.__AUCapacity * 1024 * self.__selected_AU_list[loop_count + 1]), 512))
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Free AU : RUnum:0x%x" % RUnum)
                    Argument = (0x7F000000 + RUnum) # bundle of 8 AUs
                    self.__sdCmdObj.Cmd20(Argument)
                    time.sleep(0.250)        #250ms delay

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "AUList:%s" % AUList)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "read_AUList:%s" % read_AUList)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*********************VSC %d Sequential AU write Card performance in speed mode %s [MB/sec]: %f ********************" % (self.__speedclass, self.__globalProjectConfVar['globalSpeedMode'] ,min(AUList)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*********************VSC %d Sequential AU read Card performance in speed mode %s [MB/sec]: %f ********************" % (self.__speedclass, self.__globalProjectConfVar['globalSpeedMode'] ,min(read_AUList)))

        if (self.__speedclass == 6):
            if (min(AUList) < VSC_PW[0]):
                self.__performanceError = 1
                #self.__failure_reason = 5
                self.__failure_reason = self.__failure_reason | 1 << 4
                self.__failure_speedmode = self.__globalProjectConfVar['globalSpeedMode']
                self.__failureVSC = self.__speedclass
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "****************[ERROR] Pw VSC %d Card performance not met in speed mode %s ********************" % (self.__speedclass, self.__globalProjectConfVar['globalSpeedMode'] ))
            if (min(read_AUList) < VSC_PW[0]):
                self.__performanceError = 1
                #self.__failure_reason = 6
                self.__failure_reason = self.__failure_reason | 1 << 5
                self.__failure_speedmode = self.__globalProjectConfVar['globalSpeedMode']
                self.__failureVSC = self.__speedclass
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "****************[ERROR] Pr VSC %d Card performance not met in speed mode %s ********************" % (self.__speedclass, self.__globalProjectConfVar['globalSpeedMode']))
        elif (self.__speedclass == 10):
            if (min(AUList) < VSC_PW[1]) :
                self.__performanceError = 1
                #self.__failure_reason = 5
                self.__failure_reason = self.__failure_reason | 1 << 4
                self.__failure_speedmode = self.__globalProjectConfVar['globalSpeedMode']
                self.__failureVSC = self.__speedclass
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "****************[ERROR] Pw VSC %d Card performance not met in speed mode %s ********************" % (self.__speedclass, self.__globalProjectConfVar['globalSpeedMode'] ))
            if (min(read_AUList) < VSC_PW[1]):
                self.__performanceError = 1
                #self.__failure_reason = 6
                self.__failure_reason = self.__failure_reason | 1 << 5
                self.__failure_speedmode = self.__globalProjectConfVar['globalSpeedMode']
                self.__failureVSC = self.__speedclass
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "****************[ERROR] Pr VSC %d Card performance not met in speed mode %s ********************" % (self.__speedclass, self.__globalProjectConfVar['globalSpeedMode'] ))
        elif (self.__speedclass == 30):
            if (min(AUList) < VSC_PW[2]):
                self.__performanceError = 1
                #self.__failure_reason = 5
                self.__failure_reason = self.__failure_reason | 1 << 4
                self.__failure_speedmode = self.__globalProjectConfVar['globalSpeedMode']
                self.__failureVSC = self.__speedclass
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "****************[ERROR] Pw VSC %d Card performance not met in speed mode %s ********************" % (self.__speedclass, self.__globalProjectConfVar['globalSpeedMode'] ))
            if (min(read_AUList) < VSC_PW[2]):
                self.__performanceError = 1
                #self.__failure_reason = 6
                self.__failure_reason = self.__failure_reason | 1 << 5
                self.__failure_speedmode = self.__globalProjectConfVar['globalSpeedMode']
                self.__failureVSC = self.__speedclass
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "****************[ERROR] Pr VSC %d Card performance not met in speed mode %s ********************" % (self.__speedclass, self.__globalProjectConfVar['globalSpeedMode'] ))
        self.ReleaseDIR()

    def Run(self):
        """
        Name : Run
        """

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "### VSC TEST STARTED.")

        # Initialize the SD card
        self.__globalProjectConfVar = self.__sdCmdObj.DoBasicInit()

        Mconf_Buffer=self.__sdCmdObj.GetMConf()
        CardCapacity= Mconf_Buffer.GetFourBytesToInt(30,little_endian=False)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CardCapacity : %d" % CardCapacity)

        if (CardCapacity < 65536):
            raise ValidationError.TestFailError(self.fn, "Card Capacity < 32MB : ROM mode")

        #Check if bus width is set
        SD_Status = self.__dvtLib.GetSDStatus()

        BusWidth = int(SD_Status.objSDStatusRegister.ui64DatBusWidth) # datBusWidth gives buffer values, if 0 or 1- Bus width is 1. if 2 - bus width is 4.
        if (BusWidth == 2):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus Width is set to 4 as expected.")
        else:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus width is not set to 4.")
            raise ValidationError.TestFailError(self.fn, "Bus width is not set to 4, which is not expected.")

        # Check for AU_Size and assign the Value for AU_Size
        AU_Size = int(SD_Status.objSDStatusRegister.ui64AuSize)
        AU = 2 * 16 * pow(2, AU_Size - 1)
        AU= old_div(AU, 2)
        if (AU < 1024):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "AU SIZE for this card is :\n AU_SIZE:%xh \n Value Definition(MAX AU Size):%x KB" % (AU_Size, AU))
        else:
            AU = old_div(AU, 1024)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "AU SIZE for this card is :\n AU_SIZE:%xh \n Value Definition(MAX AU Size):%x MB" % (AU_Size, AU))

        #Get AU size
        AU_SIZE = SD_Status.objSDStatusRegister.ui64AuSize
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Au Size %d" % AU_SIZE)
        AU = self.__AUsize.Run(ret = 1)

        #Get configuration parameter
        globalSpeedMode = self.__config.get('globalSpeedMode')
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "globalSpeedMode : %s" % globalSpeedMode)

        LBA_of_first_AU = self.__CardAddress['LBA_of_first_AU']
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "LBA_of_first_AU: %x" % LBA_of_first_AU)
        #VSC support check - SCR fields
        self.__sdCmdObj.Cmd55()
        scrReg = self.__sdCmdObj.GetSCRRegisterEntry()
        #For SD_SPEC
        #if (scrReg.objSCRRegister.ui8SdSpec == 0 and scrReg.objSCRRegister.ui16SdSpec3 == 0 and scrReg.objSCRRegister.ui16SdSpec4 == 0 and scrReg.objSCRRegister.ui16SdSpecx == 0):
            #raise ValidationError.TestFailError(self.fn, "Physical layer specification version no. 1.0 and 1.01")

        #elif (scrReg.objSCRRegister.ui8SdSpec == 1 and scrReg.objSCRRegister.ui16SdSpec3 == 0 and scrReg.objSCRRegister.ui16SdSpec4 == 0 and scrReg.objSCRRegister.ui16SdSpecx == 0):
            #raise ValidationError.TestFailError(self.fn, "Physical layer specification version no. 1.10")

        #elif (scrReg.objSCRRegister.ui8SdSpec == 2 and scrReg.objSCRRegister.ui16SdSpec3 == 0 and scrReg.objSCRRegister.ui16SdSpec4 == 0 and scrReg.objSCRRegister.ui16SdSpecx == 0):
            #raise ValidationError.TestFailError(self.fn, "Physical layer specification version no. 2.00")

        #elif (scrReg.objSCRRegister.ui8SdSpec == 2 and scrReg.objSCRRegister.ui16SdSpec3 == 1 and scrReg.objSCRRegister.ui16SdSpec4 == 0 and scrReg.objSCRRegister.ui16SdSpecx == 0):
            #raise ValidationError.TestFailError(self.fn, "Physical layer specification version no. 3.0x")

        #elif (scrReg.objSCRRegister.ui8SdSpec == 2 and scrReg.objSCRRegister.ui16SdSpec3 == 1 and scrReg.objSCRRegister.ui16SdSpec4 == 1 and scrReg.objSCRRegister.ui16SdSpecx == 0):
            #raise ValidationError.TestFailError(self.fn, "Physical layer specification version no. 4.xx")

        if (scrReg.objSCRRegister.ui8SdSpec == 2 and scrReg.objSCRRegister.ui16SdSpec3 == 1 and (scrReg.objSCRRegister.ui16SdSpec4 == 0 or scrReg.objSCRRegister.ui16SdSpec4 == 1) and scrReg.objSCRRegister.ui16SdSpecx == 1):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SD 5.xx Supported")
        elif (scrReg.objSCRRegister.ui8SdSpec == 2 and scrReg.objSCRRegister.ui16SdSpec3 == 1 and (scrReg.objSCRRegister.ui16SdSpec4 == 0 or scrReg.objSCRRegister.ui16SdSpec4 == 1) and scrReg.objSCRRegister.ui16SdSpecx == 2):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SD 6.xx Supported")
        else:
            raise ValidationError.TestFailError(self.fn, "SD 5.xx OR SD 6.xx not supported")

        #VSC support check - SD Status fields
        self.__sdCmdObj.Cmd55()
        sdStatus = self.__sdCmdObj.ACmd13()

        self.__VSC_AU_SIZE = (((sdStatus.GetOneByteToInt(16)&0x03) << 8) + sdStatus.GetOneByteToInt(17))

        if ((self.__VSC_AU_SIZE!= 0) and (sdStatus.GetOneByteToInt(15)>0) ):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "**************VSC AU size:%d MB******************" % self.__VSC_AU_SIZE)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "**************Video Speed Class : %d ************" % sdStatus.GetOneByteToInt(15))
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "**********SD5.0 not supported*****************")
            raise ValidationError.TestFailError(self.fn, "**********SD5.0 not supported*****************")

        self.__AUCapacity = self.__VSC_AU_SIZE
        self.__RUinAU = (old_div((self.__AUCapacity * 1024), 512))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RU in AU:%d" % self.__RUinAU)
        # to calculate the self.__SUsize

        if ((self.__AUCapacity % 7)==0):
            self.__SUsize = 7
        elif ((self.__AUCapacity % 8)==0):
            self.__SUsize = 8
        elif ((self.__AUCapacity % 9)==0):
            self.__SUsize = 9
        elif ((self.__AUCapacity % 10)==0):
            self.__SUsize = 10
        else:
            raise ValidationError.TestFailError(self.fn, "AU size not correct")

        self.__RUinSU = old_div((self.__SUsize * 1024), 512)
        self.__SUinAU = old_div(self.__AUCapacity, self.__SUsize)
        self.__RUinAU = old_div((self.__AUCapacity * 1024), self.__RU_size)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SUsize:%d" % self.__SUsize)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RUinSU:%d" % self.__RUinSU)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "__RUinAU:%d" % self.__RUinAU)

        #precondition the card
        #self.Precondition_card()
        #return # test line
        vsc=sdStatus.GetOneByteToInt(15)
        # Checking performance with various video speed class

        if (vsc in [30,60,90]):
            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC - with FAT Update per RU\n")
            self.__skipFATupdate = 0
            self.__speedmodes = 2 # 5 cycles in total
            self.vsc30()
            self.__speedmodes = 2
            self.vsc10()
            self.__speedmodes = 1
            self.vsc6()

        elif (vsc == 10):
            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC - 1 FAT Update per RU\n")
            self.__skipFATupdate = 0
            self.__speedmodes = 3 # 5 cycles in total
            self.vsc10()
            self.__speedmodes = 2
            self.vsc6()

        elif (vsc == 6):
            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC - 1 FAT Update per RU\n")
            self.__skipFATupdate = 0
            self.__speedmodes = 3 # 3 cycles in total
            self.vsc6()
            self.__speedmodes = 0
            self.vsc6()

        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "******No VSC support******")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "******Script end without performance validation******")

        if (self.__performanceError == 1):
            if self.__failure_reason >> 0 & 1  == 1:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card did not meet VSC conditions - Tfw avg exceeds 100ms")
            if self.__failure_reason >> 1 & 1  == 1:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card did not meet VSC conditions - Tfw max exceeds 750ms")
            if self.__failure_reason >> 2 & 1  == 1:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card did not meet VSC conditions - CI write exceeds 250ms")
            if self.__failure_reason >> 3 & 1  == 1:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card did not meet VSC conditions - Random write exceeds 250ms")
            if self.__failure_reason >> 4 & 1  == 1:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card did not meet VSC conditions - Pw not met in VSC%d %s condition" % (self.__failureVSC,self.__failure_speedmode))
            if self.__failure_reason >> 5 & 1  == 1:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card did not meet VSC conditions - Pr not met in VSC%d %s condition" % (self.__failureVSC,self.__failure_speedmode))
            if self.__failure_reason >> 6 & 1  == 1:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card did not meet VSC conditions - DIR Write exceeds 250ms")
            raise ValidationError.TestFailError(self.fn, "**********SD5.0 not met*****************")
    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_VSCFULLCAP_SC15_LOWCAP(self):
        obj = VSCFULLCAP_SC15_LOWCAP(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
