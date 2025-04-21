"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : None
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : VSCCMD20_Validation.py
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : VSCCMD20_Validation.py
# DESCRIPTION                    :
# PRERQUISTE                     : CMD20_UT08_AUSize_Calculation.py, ACMD41_UT10_Set_BusSpeedMode.py
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=VSCCMD20_Validation --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 06-Jul-2024
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
class VSCCMD20_Validation(customize_log):
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
        self.__StartLba   = 0
        self.__blockCount = 0
        self.__AUCapacity = 0
        self.__RUinAU     = 0
        self.__FATConfig  = 0
        self.__testerror = 0
        self.__VSC_AU_SIZE = 0


    # Testcase logic - Starts
    def MultipleWrite(self, AU_address, blockCount):
        try:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "startAddress 0x%X with blockcount 0x%X \n" % (AU_address, blockCount))
            perfValue = self.__patternGen.MultipleWrite(AU_address, blockCount)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC Failed with error :%s  \n " % exc.GetFailureDescription())
        return perfValue

    def UpdateDIRrepeat(self):
        """
        CMD20 "Update DIR" to the slot that has already been used to register DIR address,
        the card indicates ERROR in R1 (ERX)
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : Start - Update to already registered slot test")
        #Update DIR 1st Slot
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Update DIR slot 1 ")
        Argument = 0x18000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.010)

        #Write DIR
        DIRStartLba = random.randint(0,8192)
        DIRblockCount = 1
        self.MultipleWrite(DIRStartLba, DIRblockCount)

        #Update DIR 1st Slot
        Argument = 0x18000000
        try:
            self.__sdCmdObj.Cmd20(Argument)
        except ValidationError.CVFGenericExceptions as exc:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "UpdateDIRrepeat function, cannot allocate Update DIR slot 1 again since slot1 already allocated*******")
            self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_ERROR", Operation_Name = "CMD20")
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*******UpdateDIRrepeat function, Update DIR slot 1 alloted though slot1 already registered********")
            raise ValidationError.TestFailError(self.fn, "Expected CARD_ERROR error not occured for CMD20")

        time.sleep(0.010)

        #ReleaseDIR slot1
        Argument = 0x88000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.050)        #50ms delay
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DIR slot 1 released")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : End - Update to already registered slot test")

    def UpdateDIR_powercycle_repeat(self):
        """
        CMD20 "Update DIR" to the slot that has already been used to register DIR address,
        the card indicates ERROR in R1 (ERX)
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : Start - Update to already registered slot test")
        #Update DIR 1st Slot
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Update DIR slot 1 ")
        Argument = 0x18000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.010)

        #Write DIR
        DIRStartLba = random.randint(0,8192)
        DIRblockCount = 1
        self.MultipleWrite(DIRStartLba, DIRblockCount)

        self.PowerCyclecard()

        #Update DIR 1st Slot
        Argument = 0x18000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.010)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "UpdateDIR powercyle repeat function, Update DIR slot 1 alloted after power cycle")

        #ReleaseDIR slot1
        Argument = 0x88000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.050)        #50ms delay
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DIR slot 1 released")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : End - Update to already registered slot test")


    def UpdateReleaseDIRFunction(self):
        """
        CMD20 Update & Release DIR function
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : Start - Update and Release DIR test")
        #Update DIR 1st Slot
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Update DIR slot 1 ")
        Argument = 0x18000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.010)        #10ms delay

        #Write DIR
        DIRStartLba = random.randint(0,8192)
        DIRblockCount = 1
        self.MultipleWrite(DIRStartLba, DIRblockCount)

        #ReleaseDIR slot1
        Argument = 0x88000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.050)        #50ms delay
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DIR slot 1 released")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***********[Pass] UpdateReleaseDIRFunction, after releasing slot1 Update DIR slot 1 registered again**************")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : End - Update and Release DIR test")

    def ReleaseDIR_Repeat(self):
        """
        CMD20 ReleaseDIR_Repeat
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : Start - Release already released slot test")
        #Update DIR 1st Slot
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Update DIR slot 1")
        Argument = 0x18000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.010)        #10ms delay

        #Write DIR
        DIRStartLba = random.randint(0,8192)
        DIRblockCount = 1
        self.MultipleWrite(DIRStartLba, DIRblockCount)

        #ReleaseDIR slot1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DIR slot 1 released")
        Argument = 0x88000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.050)     #50ms delay

        #ReleaseDIR slot1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DIR slot 1 released again")
        Argument = 0x88000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.050)     #50ms delay
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "No Error reported for released unregistered slot 1")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***********[Pass] ReleaseDIRFunction, release free slot completed**************")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : Start - Release already released slot test")

    def Suspend_writeotherAU_ResumeFunction(self):
        """
        CMD20 suspend, write to other AU and resume function
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : Start - Suspend Write to non SUS AU and Resume test")
        try:
            Argument = 0x18000000 #slot 1
            for i in range(8):
                #Update DIR Slot
                self.__sdCmdObj.Cmd20(Argument)
                time.sleep(0.010)        #10ms delay

                #Write DIR
                DIRStartLba = random.randint(0x6000,0x1FFFFF)
                DIRblockCount = 1
                perfValue = self.MultipleWrite(DIRStartLba, DIRblockCount)
                performance = float(perfValue.perfReadWrite.perfResults) / (1000 * 1000)
                TimeDIR = old_div((old_div(512, performance)), 1000)
                if (TimeDIR > 250):
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*********[ERROR] write DIR after Update DIR took > 250ms********")
                Argument = Argument + 0x1000000 #increase slot number

            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()
            AU_start = 0x400000
            selected_AU = 0
            AU_SIZE_Sectors = (old_div(self.__VSC_AU_SIZE * 1024 * 1024, 512))

            selected_AU = (random.randrange(AU_start,0x800000,AU_SIZE_Sectors))
            if selected_AU%AU_SIZE_Sectors > 0:
                selected_AU = ((old_div(selected_AU,AU_SIZE_Sectors)) +1)*AU_SIZE_Sectors
                selected_AU = old_div(selected_AU, AU_SIZE_Sectors)
            else:
                selected_AU = old_div(selected_AU, AU_SIZE_Sectors)

            #start Recording
            Argument = 0x8000000
            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(1)        #1s delay

            #"set free AU "
            RUnum = (old_div((self.__AUCapacity*1024*selected_AU),512))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Free AU : RUnum:0x%x" % RUnum)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Selected AU 0x%x" % selected_AU)

            Argument = (0x7F000000 + RUnum) # Bundle of 8 AUs

            #set free AU
            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RUnum:%x" % RUnum)

            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(0.250)        #250ms delay

            #start Recording
            Argument = 0x8000000
            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(1)        #1s delay

            #self.__StartLba = 0x120000  #24x24x1024x1024/512

            self.__StartLba = old_div((self.__AUCapacity*1024*1024*selected_AU),512)
            #print hex(self.__StartLba)
            self.__blockCount = 0x400
            RU = random.randint(1,(self.__RUinAU - 1))
            leftRU = (self.__RUinAU - RU)
            for i in range (RU):
                #self.AUwrite(self.__StartLba, self.__blockCount)
                perfValue = self.MultipleWrite(self.__StartLba, self.__blockCount)
                self.__StartLba = self.__StartLba + self.__blockCount

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Before suspend sdStatus")
            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()

            #Suspend Recording
            Argument=0x58000000
            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(0.250)        #250ms delay

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "After suspend sdStatus")
            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()

            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "\n*************suspend address: %d*************" % sdStatus.GetOneByteToInt(18))
            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "\n*************suspend address: %d*************" % sdStatus.GetOneByteToInt(19))

            SuspendAddress = ((sdStatus.GetOneByteToInt(18) & 0x3F) << 16) + ((sdStatus.GetOneByteToInt(19) & 0xFF) << 8) + sdStatus.GetOneByteToInt(20)
            SuspendAddress = (SuspendAddress >> 2) * 1024

            ResAddress = self.__StartLba

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************SUS ADDR : %x*************" % SuspendAddress)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************write suspended after RU at %x*************" % ((self.__StartLba-self.__blockCount)))
            Suspended_address = SuspendAddress
            ResAddress = self.__StartLba

            #write to non SUS_AU
            Random_AU = (random.randrange(0x800000,0xA00000,AU_SIZE_Sectors))
            if Random_AU%AU_SIZE_Sectors > 0:
                Random_AU = ((old_div(Random_AU,AU_SIZE_Sectors)) +1)*AU_SIZE_Sectors
                Random_AU = old_div(Random_AU, AU_SIZE_Sectors)
            else:
                Random_AU = old_div(Random_AU, AU_SIZE_Sectors)

            randomLBA = old_div((self.__AUCapacity*1024*1024*Random_AU),512)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Write to non suspended AU at 0x%x" % randomLBA)
            perfValue = self.MultipleWrite(randomLBA, self.__blockCount)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "After write to non suspended AU sdStatus")
            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()

            SuspendAddress = ((sdStatus.GetOneByteToInt(18) & 0x3F) << 16) + ((sdStatus.GetOneByteToInt(19) & 0xFF) << 8) + sdStatus.GetOneByteToInt(20)
            SuspendAddress = (SuspendAddress >> 2) * 1024

            ResAddress = self.__StartLba
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************SUS ADDR: %x*************" % SuspendAddress)
            if (SuspendAddress == 0):
                raise ValidationError.TestFailError(self.fn, "*******[Error] [Unexpected] Suspended Address cleared for write to non Suspended AU *********")
            if (Suspended_address != SuspendAddress):
                raise ValidationError.TestFailError(self.fn, "*******[Error] [Unexpected] Suspended Address changed for write to non Suspended AU *********")
            #Resume Recording
            Argument = 0x68000000
            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(0.250)        #250ms delay
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Resume Recording success")

            self.__StartLba = self.__StartLba + self.__blockCount
            perfValue = self.MultipleWrite(self.__StartLba, self.__blockCount)
            # Releasing all DIR slot Ids

            Argument = 0x88000000 #slot 1
            for i in range(8):
                #Update DIR Slot
                self.__sdCmdObj.Cmd20(Argument)
                time.sleep(0.050)        #50ms delay
                Argument = Argument + 0x1000000 #next slot

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************[Pass] Suspend, Write to non Suspended AU, ResumeFunction passed ")

        except ValidationError.CVFGenericExceptions as exc:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed with error :%s \n " % exc.GetFailureDescription())
            self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure
            self.__testerror = 1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : End - Suspend Write to non SUS AU and Resume test")


    def Suspend_writeSUSAU_ResumeFunction(self):
        """
        CMD20 suspend, write to suspended AU and resume function
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : Start - Suspend Write to  SUS AU and Resume test")
        try:
            Argument = 0x18000000 #slot 1
            for i in range(8):
                #Update DIR Slot
                self.__sdCmdObj.Cmd20(Argument)
                time.sleep(0.010)        #10ms delay

                #Write DIR
                DIRStartLba = random.randint(0x6000,0x1FFFFF)
                DIRblockCount = 1
                perfValue = self.MultipleWrite(DIRStartLba, DIRblockCount)
                performance = float(perfValue.perfReadWrite.perfResults) / (1000 * 1000)
                TimeDIR = old_div((old_div(512, performance)), 1000)
                if (TimeDIR > 250):
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*********[ERROR] write DIR after Update DIR took > 250ms********")
                Argument = Argument + 0x1000000 #increase slot number

            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()
            AU_start = 0x400000
            selected_AU = 0
            AU_SIZE_Sectors = (old_div(self.__VSC_AU_SIZE * 1024 * 1024, 512))

            selected_AU = (random.randrange(AU_start,0x800000,AU_SIZE_Sectors))
            if selected_AU%AU_SIZE_Sectors > 0:
                selected_AU = ((old_div(selected_AU,AU_SIZE_Sectors)) +1)*AU_SIZE_Sectors
                selected_AU = old_div(selected_AU, AU_SIZE_Sectors)
            else:
                selected_AU = old_div(selected_AU, AU_SIZE_Sectors)

            #start Recording
            Argument = 0x8000000
            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(1)        #1s delay

            #"set free AU "
            RUnum = (old_div((self.__AUCapacity*1024*selected_AU),512))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Free AU : RUnum:0x%x" % RUnum)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Selected AU 0x%x" % selected_AU)

            Argument = (0x7F000000 + RUnum) # Bundle of 8 AUs

            #set free AU
            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RUnum:%x" % RUnum)

            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(0.250)        #250ms delay

            #start Recording
            Argument = 0x8000000
            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(1)        #1s delay

            #self.__StartLba = 0x120000  #24x24x1024x1024/512

            self.__StartLba = old_div((self.__AUCapacity*1024*1024*selected_AU),512)
            self.__blockCount = 0x400
            RU = random.randint(1,(self.__RUinAU - 1))
            leftRU = (self.__RUinAU - RU)

            for i in range (RU):
                #self.AUwrite(self.__StartLba, self.__blockCount)
                perfValue = self.MultipleWrite(self.__StartLba, self.__blockCount)
                self.__StartLba = self.__StartLba + self.__blockCount

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Before suspend sdStatus")
            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()

            #Suspend Recording
            Argument=0x58000000
            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(0.250)        #250ms delay

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "After suspend sdStatus")
            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()

            SuspendAddress = ((sdStatus.GetOneByteToInt(18) & 0x3F) << 16) + ((sdStatus.GetOneByteToInt(19) & 0xFF) << 8) + sdStatus.GetOneByteToInt(20)
            SuspendAddress = (SuspendAddress >> 2) * 1024

            ResAddress = self.__StartLba
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************SUS ADDR: %x*************" % SuspendAddress)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************write suspended after RU at %x*************" % ((self.__StartLba-self.__blockCount)))

            ResAddress = self.__StartLba

            #write to SUS_AU
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Write to suspended AU")
            perfValue = self.MultipleWrite(self.__StartLba, self.__blockCount)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "After write to suspended AU sdStatus")
            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()

            SuspendAddress = ((sdStatus.GetOneByteToInt(18) & 0x3F) << 16) + ((sdStatus.GetOneByteToInt(19) & 0xFF) << 8) + sdStatus.GetOneByteToInt(20)
            SuspendAddress = (SuspendAddress >> 2) * 1024

            ResAddress = self.__StartLba
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************SUS ADDR: %x*************" % SuspendAddress)

            #Resume Recording
            Argument = 0x68000000
            try:
                self.__sdCmdObj.Cmd20(Argument)
            except ValidationError.CVFGenericExceptions as exc:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Resume Recording failed as no SUS_ADDR available")
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_ERROR", Operation_Name = "CMD20")
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Resume Recording did not flag error *********")
                raise ValidationError.TestFailError(self.fn, "Expected CARD_ERROR error not occured for CMD20")

            time.sleep(0.250)        #250ms delay

            # Releasing all DIR slot Ids

            Argument = 0x88000000 #slot 1
            for i in range(8):
                #Update DIR Slot
                self.__sdCmdObj.Cmd20(Argument)
                time.sleep(0.050)        #50ms delay
                Argument = Argument + 0x1000000 #next slot

            self.PowerCyclecard()
            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()

            SuspendAddress = ((sdStatus.GetOneByteToInt(18) & 0x3F) << 16) + ((sdStatus.GetOneByteToInt(19) & 0xFF) << 8) + sdStatus.GetOneByteToInt(20)
            SuspendAddress = (SuspendAddress >> 2) * 1024
            if (SuspendAddress != 0):
                raise ValidationError.TestFailError(self.fn, "[Error] [Unexpected] Suspend, Write to Suspended AU, ResumeFunction, SUS_ADDR not cleared after resume and power cycle %x" % SuspendAddress)
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Suspend, Write to Suspended AU, ResumeFunction, SUS_ADDR cleared after resume and power cycle")
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Suspend, Write to Suspended AU, ResumeFunction passed ")
        except ValidationError.CVFGenericExceptions as exc:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed with error :%s \n " % exc.GetInternalErrorMessage())
            self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure
            self.__testerror = 1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : End - Suspend Write to  SUS AU and Resume test")

    def SuspendResumeFunction(self):

        """
        CMD20 suspend and resume function

        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : Start - Suspend Resume test")
        try:
            Argument = 0x18000000 #slot 1
            for i in range(8): #updating 8 slots
                #Update DIR Slot
                self.__sdCmdObj.Cmd20(Argument)
                time.sleep(0.010)        #10ms delay

                #Write DIR
                DIRStartLba = random.randint(0x6000,0x1FFFFF)
                DIRblockCount = 1
                perfValue = self.MultipleWrite(DIRStartLba, DIRblockCount)
                performance = float(perfValue.perfReadWrite.perfResults) / (1000 * 1000)
                TimeDIR = old_div((old_div(512, performance)), 1000)
                if (TimeDIR > 250):
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*********[ERROR] write DIR after Update DIR took > 250ms********")
                Argument = Argument + 0x1000000 #increase slot number

            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()
            AU_start = 0x400000
            selected_AU = 0
            AU_SIZE_Sectors = (old_div(self.__VSC_AU_SIZE * 1024 * 1024, 512))

            selected_AU = (random.randrange(AU_start,0x800000,AU_SIZE_Sectors))
            if selected_AU%AU_SIZE_Sectors > 0:
                selected_AU = ((old_div(selected_AU,AU_SIZE_Sectors)) +1)*AU_SIZE_Sectors
                selected_AU = old_div(selected_AU, AU_SIZE_Sectors)
            else:
                selected_AU = old_div(selected_AU, AU_SIZE_Sectors)

            #"set free AU "
            RUnum = (old_div((self.__AUCapacity*1024*selected_AU),512))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Free AU : RUnum:0x%x" % RUnum)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Selected AU 0x%x" % selected_AU)
            Argument = (0x7F000000 + RUnum) # Bundle of 8 AUs

            #set free AU
            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RUnum:%x" % RUnum)

            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(0.250)        #250ms delay

            #start Recording
            Argument = 0x8000000
            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(1)        #1s delay

            #self.__StartLba = 0x120000  #24x24x1024x1024/512

            self.__StartLba = old_div((self.__AUCapacity*1024*1024*selected_AU),512)
            self.__blockCount = 0x400
            RU = random.randint(1,(self.__RUinAU - 1))
            leftRU = (self.__RUinAU - RU)

            for i in range (RU):
                #self.AUwrite(self.__StartLba, self.__blockCount)
                perfValue = self.MultipleWrite(self.__StartLba, self.__blockCount)
                self.__StartLba = self.__StartLba + self.__blockCount

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Before suspend sdStatus")
            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()

            #Suspend Recording
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Suspend recording")
            Argument=0x58000000
            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(0.250)        #250ms delay

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "After suspend sdStatus")
            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()

            SuspendAddress = ((sdStatus.GetOneByteToInt(18) & 0x3F) << 16) + ((sdStatus.GetOneByteToInt(19) & 0xFF) << 8) + sdStatus.GetOneByteToInt(20)
            SuspendAddress = (SuspendAddress >> 2) * 1024

            ResAddress = self.__StartLba
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************SUS ADDR: %x*************" % SuspendAddress)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************write suspended after RU at %x*************" % ((self.__StartLba-self.__blockCount)))
            Prev_SuspendAddress = SuspendAddress

            self.PowerCyclecard()

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "After suspend sdStatus")
            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()

            SuspendAddress = ((sdStatus.GetOneByteToInt(18) & 0x3F) << 16) + ((sdStatus.GetOneByteToInt(19) & 0xFF) << 8) + sdStatus.GetOneByteToInt(20)
            SuspendAddress = (SuspendAddress >> 2) * 1024

            ResAddress = self.__StartLba
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************After Power Cycle - SUS ADDR: %x*************" % SuspendAddress)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************write suspended after RU at %x*************" % ((self.__StartLba-self.__blockCount)))

            #Resume Recording
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Resume recording")
            Argument = 0x68000000
            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(0.250)        #250ms delay
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Suspend address : %x" % SuspendAddress)

            perfValue = self.MultipleWrite(self.__StartLba, self.__blockCount)
            self.__StartLba = self.__StartLba + self.__blockCount

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "sdStatus after resume")
            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()

            SuspendAddress = ((sdStatus.GetOneByteToInt(18) & 0x3F) << 16) + ((sdStatus.GetOneByteToInt(19) & 0xFF) << 8) + sdStatus.GetOneByteToInt(20)
            SuspendAddress = (SuspendAddress >> 2) * 1024
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************SUS ADDR after resume : %x*************" % SuspendAddress)

            if (SuspendAddress ==0):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Suspend address : %x" % SuspendAddress)
            else:
                raise ValidationError.TestFailError(self.fn, "Suspended address not cleard after resume: %x" % SuspendAddress)

            #Suspend Recording
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Suspend recording")
            Argument=0x58000000
            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(0.250)        #250ms delay

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "After suspend sdStatus")
            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()

            SuspendAddress = ((sdStatus.GetOneByteToInt(18) & 0x3F) << 16) + ((sdStatus.GetOneByteToInt(19) & 0xFF) << 8) + sdStatus.GetOneByteToInt(20)
            SuspendAddress = (SuspendAddress >> 2) * 1024
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************SUS ADDR after suspend: %x*************" % SuspendAddress)

            Curr_SuspendAddress = SuspendAddress

            if (Curr_SuspendAddress == Prev_SuspendAddress):
                raise ValidationError.TestFailError(self.fn, "Suspended address not stored properly: Expected is %x and stored is %x" % (Curr_SuspendAddress,Prev_SuspendAddress))

        # Releasing all DIR slot Ids

            Argument = 0x88000000 #slot 1
            for i in range(8):
                #Update DIR Slot
                self.__sdCmdObj.Cmd20(Argument)
                time.sleep(0.050)        #50ms delay
                Argument = Argument + 0x1000000 #next slot

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************[Pass] SuspendResumeFunction passed, SD status register suspend address: %x & Resumed at address: %x*************" % (SuspendAddress,ResAddress))

        except ValidationError.CVFGenericExceptions as exc:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed with error :%s \n " % exc.GetInternalErrorMessage())
            self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure
            self.__testerror = 1


    def WriteToSuspendAU(self):
        """
        CMD20 any Write to the suspended AU will result in the SUS_ADDR field being cleared to zero
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : Start - Suspend Write to  SUS AU and Resume test")
        #Update DIR 1st Slot
        Argument = 0x18000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.010)        #10ms delay

        #Write DIR
        DIRStartLba = random.randint(0,8192)
        DIRblockCount = 1
        self.__dvtLib.WriteWithFPGAPattern(DIRStartLba, DIRblockCount, pattern = gvar.GlobalConstants.PATTERN_ALL_ONE)

        #UpdateDIR slot2
        Argument = 0x19000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.010)        #10ms delay

        #Write DIR
        DIRStartLba = random.randint(0,8192)
        self.__dvtLib.WriteWithFPGAPattern(DIRStartLba, DIRblockCount, pattern = gvar.GlobalConstants.PATTERN_ALL_ONE)

        #set free AU

        #RUno.=(AUsize*destinationAUno.)/RUsize
        RUnum = old_div((self.__AUCapacity*1024*100),512)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RUnum:%x" % RUnum)

        #Argument = 0x7F0012C0   #8 bundles(AUs) StartAU = 100th

        Argument = (0x7F000000 + RUnum)

        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.250)        #250ms delay

        #start Recording
        Argument = 0x8000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(1)        #1s delay

        #self.__StartLba = 0x4B0000  #100x24x1024x1024/512
        self.__StartLba = old_div((self.__AUCapacity*1024*1024*100),512)
        self.__blockCount = 0x400

        self.AUwrite(self.__StartLba, self.__blockCount)
        self.AUwrite(self.__StartLba, self.__blockCount)
        self.AUwrite(self.__StartLba, self.__blockCount)
        self.AUwrite(self.__StartLba, self.__blockCount)
        #self.AUwrite(self.__StartLba, self.__blockCount)

        #RU=6
        RU = random.randint(1,(self.__RUinAU - 1))
        leftRU = (self.__RUinAU-RU)

        for i in range(RU):
            self.__dvtLib.WriteWithFPGAPattern(self.__StartLba, self.__blockCount, pattern = gvar.GlobalConstants.PATTERN_ALL_ONE)
            self.__StartLba = self.__StartLba + self.__blockCount

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Before suspend sdStatus")
        self.__sdCmdObj.Cmd55()
        sdStatus = self.__sdCmdObj.ACmd13()

        #Suspend Recording
        Argument=0x58000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.250)        #250ms delay

        #self.__dvtLib.WriteWithFPGAPattern(self.__StartLba, self.__blockCount, pattern = gvar.GlobalConstants.PATTERN_ALL_ONE)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "after suspend sdStatus")
        self.__sdCmdObj.Cmd55()
        sdStatus = self.__sdCmdObj.ACmd13()

        SuspendAddress = ((sdStatus.GetOneByteToInt(18) & 0x3F) << 16) + ((sdStatus.GetOneByteToInt(19) & 0xFF) << 8) + sdStatus.GetOneByteToInt(20)
        SuspendAddress = (SuspendAddress >> 2) * 1024

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************suspend address: %x*************" % SuspendAddress)

        #write in same AU will make suspend address zero

        self.__dvtLib.WriteWithFPGAPattern(self.__StartLba, self.__blockCount, pattern = gvar.GlobalConstants.PATTERN_ALL_ONE)

        self.__sdCmdObj.Cmd55()
        sdStatus = self.__sdCmdObj.ACmd13()

        ResAddress = (((sdStatus.GetOneByteToInt(18) & 0x3F) << 16) + ((sdStatus.GetOneByteToInt(19) & 0xFF) << 8) + sdStatus.GetOneByteToInt(20))
        ResAddress = ((ResAddress>>2)*1024)

        #Resume Recording
        Argument = 0x68000000
        try:
            self.__sdCmdObj.Cmd20(Argument)
        except ValidationError.CVFGenericExceptions as exc:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "WriteToSuspendAU Function,cannot resume recording since suspend address is: %x *************" % ResAddress)
            self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_ERROR", Operation_Name = "CMD20")
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "WriteToSuspendAU Function, should not resume recording since suspend adress is %x" % ResAddress)
            raise ValidationError.TestFailError(self.fn, "Expected CARD_ERROR error not occured for CMD20")

        time.sleep(0.250)        #250ms delay

        # Releasing all DIR slot Ids

        #ReleaseDIR slot1
        Argument = 0x88000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.050)        #50ms delay

        #ReleaseDIR slot2
        Argument = 0x89000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.050)        #50ms delay

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "after suspend sdStatus")
        self.__sdCmdObj.Cmd55()
        sdStatus = self.__sdCmdObj.ACmd13()

        SuspendAddress = ((sdStatus.GetOneByteToInt(18) & 0x3F) << 16) + ((sdStatus.GetOneByteToInt(19) & 0xFF) << 8) + sdStatus.GetOneByteToInt(20)
        SuspendAddress = (SuspendAddress >> 2) * 1024
        if (SuspendAddress != 0):
            raise ValidationError.TestFailError(self.fn, "[Error] [Unexpected] WriteToSuspendAU Function, SUS_ADDR not cleared after resume and power cycle %x" % SuspendAddress)
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "WriteToSuspendAU Function, SUS_ADDR cleared after resume and power cycle")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : End - Suspend Write to  SUS AU and Resume test")

    def PowerCyclecard(self):
        #power cycle the card
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************POWER CYCLE CARD")
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)
        globalProjectConfVar = self.__sdCmdObj.DoBasicInit()
        globalProjectConfVar['globalSpeedMode'] = 'SDR50'
        self.__globalSetBusSpeedModeObj.Run(globalProjectConfVar)
        self.__dvtLib.GetCardTransferMode()
        self.__sdCmdObj.SetFrequency(Freq = 80 * 1000)
        self.__sdCmdObj.GetFrequency()

    def SetFreeAuAtZeroAddress(self):

        #Update DIR 1st Slot
        Argument = 0x18000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.010)        #10ms delay

        #Write DIR
        DIRStartLba = random.randint(0,8192)
        DIRblockCount = 1
        self.__dvtLib.WriteWithFPGAPattern(DIRStartLba, DIRblockCount, pattern = gvar.GlobalConstants.PATTERN_ALL_ONE)

        #set free AU LBA 0
        Argument = 0x7F000000   #8 bundles(AUs) StartAU = 0th

        try:
            self.__sdCmdObj.Cmd20(Argument)
        except ValidationError.CVFGenericExceptions as exc:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SetFreeAu At ZeroAddress Failed")
            self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_ERROR", Operation_Name = "CMD20")
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SetFreeAu At ZeroAddress did not fail")
            raise ValidationError.TestFailError(self.fn, "Expected CARD_ERROR error not occured for CMD20")

        time.sleep(0.250)        #250ms delay

        #set free AU non AU aligned address
        RUnum = old_div((self.__AUCapacity*1024*200),512)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RUnum: %x" % RUnum)
        Argument = (0x7F000000 + RUnum-3)  #8 bundles(AUs) StartAU = 0th
        try:
            self.__sdCmdObj.Cmd20(Argument)
        except ValidationError.CVFGenericExceptions as exc:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SetFreeAu At non Aligned Address Failed")
            self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_ERROR", Operation_Name = "CMD20")
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SetFreeAu At non Aligned Address did not fail")
            raise ValidationError.TestFailError(self.fn, "Expected CARD_ERROR error not occured for CMD20")

        time.sleep(0.250)        #250ms delay

        #ReleaseDIR slot1
        Argument = 0x88000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.050)        #50ms delay


    def SuspendAtAuBoundary(self):
        """
        CMD20 "Suspend AU" command is issued at AU boundary than suspand address will be zero
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : Start - Suspend at AU boundary ")

        #Update DIR 1st Slot
        Argument = 0x18000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.010)        #10ms delay
        #

        #Write DIR
        DIRStartLba = random.randint(0,8192)
        DIRblockCount = 1
        self.__dvtLib.WriteWithFPGAPattern(DIRStartLba, DIRblockCount, pattern = gvar.GlobalConstants.PATTERN_ALL_ONE)
        #set free AU

        #Argument = 0x7F0012C0   #8 bundles(AUs) StartAU = 100th

        #RUno.=(AUsize*destinationAUno.)/RUsize
        RUnum = old_div((self.__AUCapacity*1024*200),512)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RUnum: %x" % RUnum)

        Argument = (0x7A000000 + RUnum)   #3 bundles(AUs) StartAU = 200th

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Argument: %x" % Argument)

        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.250)        #250ms delay
        #

        #start Recording
        Argument = 0x8000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(1)        #1s delay
        #

        #self.__StartLba = 0x960000   #200x24x1024x1024/512

        self.__StartLba = old_div((self.__AUCapacity*1024*1024*200),512)

        self.__blockCount = 0x400

        self.AUwrite(self.__StartLba, self.__blockCount)

        self.AUwrite(self.__StartLba, self.__blockCount)

        #Suspend Recording
        Argument=0x58000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.250)        #250ms delay

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "after suspend sdStatus")
        self.__sdCmdObj.Cmd55()
        sdStatus = self.__sdCmdObj.ACmd13()

        SuspendAddress = ((sdStatus.GetOneByteToInt(18) & 0x3F) << 16) + ((sdStatus.GetOneByteToInt(19) & 0xFF) << 8) + sdStatus.GetOneByteToInt(20)
        SuspendAddress = (SuspendAddress >> 2) * 1024
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************SUS ADDR: %x*************" % SuspendAddress)
        if (SuspendAddress == 0):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Suspended Address is 'zero' for suspend at AU boundary")
        else:
            raise ValidationError.TestFailError(self.fn, "[Error] [UnExpected] Suspended Address not 'zero' for suspend at AU boundary")

        #Resume Recording
        Argument = 0x68000000
        try:
            self.__sdCmdObj.Cmd20(Argument)
        except ValidationError.CVFGenericExceptions as exc:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SuspendAtAuBoundary Function, Cannot resume recording since suspend at AU boundary suspend address is %x" % SuspendAddress)
            self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_ERROR", Operation_Name = "CMD20")
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SuspendAtAuBoundary Function, resume recording didnt fail for suspend at AU boundary")
            raise ValidationError.TestFailError(self.fn, "Expected CARD_ERROR error not occured for CMD20")

        time.sleep(0.250)        #250ms delay

        #ReleaseDIR slot1
        Argument = 0x88000000
        self.__sdCmdObj.Cmd20(Argument)
        time.sleep(0.050)        #50ms delay
        #
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : End - Suspend at AU boundary ")

    def Suspend_Erase_SUS_AU_ResumeFunction(self):

        """
            CMD20 suspend and resume function

            """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : Start - Suspend Erase SUS AU Resume test")
        try:
            Argument = 0x18000000 #slot 1
            for i in range(8):
                #Update DIR Slot
                self.__sdCmdObj.Cmd20(Argument)
                time.sleep(0.010)        #10ms delay

                #Write DIR
                DIRStartLba = random.randint(0x6000,0x1FFFFF)
                DIRblockCount = 1
                perfValue = self.MultipleWrite(DIRStartLba, DIRblockCount)
                performance = float(perfValue.perfReadWrite.perfResults) / (1000 * 1000)
                TimeDIR = old_div((old_div(512, performance)), 1000)
                if (TimeDIR > 250):
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*********[ERROR] write DIR after Update DIR took > 250ms********")
                Argument = Argument + 0x1000000 #increase slot number


            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()
            AU_start = 0x400000
            selected_AU = 0
            AU_SIZE_Sectors = (old_div(self.__VSC_AU_SIZE * 1024 * 1024, 512))

            selected_AU = random.randrange(AU_start,0x800000,AU_SIZE_Sectors)
            if selected_AU%AU_SIZE_Sectors > 0:
                selected_AU = ((old_div(selected_AU,AU_SIZE_Sectors)) +1)*AU_SIZE_Sectors
                selected_AU = old_div(selected_AU, AU_SIZE_Sectors)
            else:
                selected_AU = old_div(selected_AU, AU_SIZE_Sectors)

            #start Recording
            Argument = 0x8000000
            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(1)        #1s delay

            #"set free AU "
            RUnum = (old_div((self.__AUCapacity*1024*selected_AU),512))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Free AU : RUnum:0x%x" % RUnum)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Selected AU 0x%x" % selected_AU)

            Argument = (0x7F000000 + RUnum) # Bundle of 8 AUs

            #set free AU
            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RUnum:%x" % RUnum)

            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(0.250)        #250ms delay

            #start Recording
            Argument = 0x8000000
            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(1)        #1s delay

            #self.__StartLba = 0x120000  #24x24x1024x1024/512

            self.__StartLba = old_div((self.__AUCapacity*1024*1024*selected_AU),512)
            self.__blockCount = 0x400
            RU = random.randint(1,(self.__RUinAU - 1))
            leftRU = (self.__RUinAU - RU)

            for i in range (RU):
                #self.AUwrite(self.__StartLba, self.__blockCount)
                perfValue = self.MultipleWrite(self.__StartLba, self.__blockCount)
                self.__StartLba = self.__StartLba + self.__blockCount

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Before suspend sdStatus")
            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()

            #Suspend Recording
            Argument=0x58000000
            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(0.250)        #250ms delay
            #

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "after suspend sdStatus")
            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()

            SuspendAddress = ((sdStatus.GetOneByteToInt(18) & 0x3F) << 16) + ((sdStatus.GetOneByteToInt(19) & 0xFF) << 8) + sdStatus.GetOneByteToInt(20)
            SuspendAddress = (SuspendAddress >> 2) * 1024
            ResAddress = self.__StartLba
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************SUS ADDR: %x*************" % SuspendAddress)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************write suspended after RU at %x*************" % ((self.__StartLba-self.__blockCount)))

            ResAddress = self.__StartLba
            EndLBA = self.__sdCmdObj.calculate_endLba(startLba = self.__StartLba, blockcount = self.__blockCount)
            self.__dvtLib.Erase(StartLba = self.__StartLba, EndLba = EndLBA, directCardAPI=True)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "After Erase to suspended AU sdStatus")
            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()

            SuspendAddress = ((sdStatus.GetOneByteToInt(18) & 0x3F) << 16) + ((sdStatus.GetOneByteToInt(19) & 0xFF) << 8) + sdStatus.GetOneByteToInt(20)
            SuspendAddress = (SuspendAddress >> 2) * 1024
            ResAddress = self.__StartLba
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************SUS ADDR: %x*************" % SuspendAddress)
            if (SuspendAddress != 0):
                raise ValidationError.TestFailError(self.fn, "should not occur as Erase performed on suspend AU")

            #Resume Recording
            Argument = 0x68000000
            try:
                self.__sdCmdObj.Cmd20(Argument)
            except ValidationError.CVFGenericExceptions as exc:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Resume Recording failed. Error reported as no SUS_ADDR available")
                self.__dvtLib.Expected_Failure_Check(exc, Expected_Exception = "CARD_ERROR", Operation_Name = "CMD20")
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Resume Recording did not report error")
                raise ValidationError.TestFailError(self.fn, "Expected CARD_ERROR error not occured for CMD20")

            time.sleep(0.250)        #250ms delay

            # Releasing all DIR slot Ids
            Argument = 0x88000000 #slot 1
            for i in range(8):
                #Update DIR Slot
                self.__sdCmdObj.Cmd20(Argument)
                time.sleep(0.050)        #50ms delay
                Argument = Argument + 0x1000000 #next slot

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************[Pass] Suspend Erase ResumeFunction passed")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : End - Suspend Erase SUS AU Resume test")

        except ValidationError.CVFGenericExceptions as exc:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed with error :%s \n " % exc.GetInternalErrorMessage())
            self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure
            self.__testerror = 1

    def Suspend_Erase_Other_AU_ResumeFunction(self):
        """
        CMD20 suspend and resume function
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : Start - Suspend Erase other AU Resume test")
        try:
            Argument = 0x18000000 #slot 1
            for i in range(8):
                #Update DIR Slot
                self.__sdCmdObj.Cmd20(Argument)
                time.sleep(0.010)        #10ms delay

                #Write DIR
                DIRStartLba = random.randint(0x6000,0x1FFFFF)
                DIRblockCount = 1
                perfValue = self.MultipleWrite(DIRStartLba, DIRblockCount)
                performance = float(perfValue.perfReadWrite.perfResults) / (1000 * 1000)
                TimeDIR = old_div((old_div(512, performance)), 1000)
                if (TimeDIR > 250):
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*********[ERROR] write DIR after Update DIR took > 250ms********")
                Argument = Argument + 0x1000000 #increase slot number


            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()
            AU_start = 0x400000
            selected_AU = 0
            AU_SIZE_Sectors = (old_div(self.__VSC_AU_SIZE * 1024 * 1024, 512))

            selected_AU = (random.randrange(AU_start,0x800000,AU_SIZE_Sectors))
            if selected_AU%AU_SIZE_Sectors > 0:
                selected_AU = ((old_div(selected_AU,AU_SIZE_Sectors)) +1)*AU_SIZE_Sectors
                selected_AU = old_div(selected_AU, AU_SIZE_Sectors)
            else:
                selected_AU = old_div(selected_AU, AU_SIZE_Sectors)

            #start Recording
            Argument = 0x8000000
            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(1)        #1s delay

            #"set free AU "
            RUnum = (old_div((self.__AUCapacity*1024*selected_AU),512))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set Free AU : RUnum:0x%x" % RUnum)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Selected AU 0x%x" % selected_AU)

            Argument = (0x7F000000 + RUnum) # Bundle of 8 AUs

            #set free AU
            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RUnum:%x" % RUnum)

            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(0.250)        #250ms delay

            #start Recording
            Argument = 0x8000000
            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(1)        #1s delay

            #self.__StartLba = 0x120000  #24x24x1024x1024/512

            self.__StartLba = old_div((self.__AUCapacity*1024*1024*selected_AU),512)
            self.__blockCount = 0x400
            RU = random.randint(1,(self.__RUinAU - 1))
            leftRU = (self.__RUinAU - RU)

            for i in range (RU):
                #self.AUwrite(self.__StartLba, self.__blockCount)
                perfValue = self.MultipleWrite(self.__StartLba, self.__blockCount)
                self.__StartLba = self.__StartLba + self.__blockCount

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Before suspend sdStatus")
            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()

            #Suspend Recording
            Argument=0x58000000
            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(0.250)        #250ms delay
            #

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "After suspend sdStatus")
            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()

            SuspendAddress = ((sdStatus.GetOneByteToInt(18) & 0x3F) << 16) + ((sdStatus.GetOneByteToInt(19) & 0xFF) << 8) + sdStatus.GetOneByteToInt(20)
            SuspendAddress = (SuspendAddress >> 2) * 1024
            ResAddress = self.__StartLba
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************SUS ADDR: %x*************" % SuspendAddress)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************write suspended after RU at %x*************" % ((self.__StartLba-self.__blockCount)))

            ResAddress = self.__StartLba
            #write to non SUS_AU
            Random_AU = (random.randrange(0x800000,0xA00000,AU_SIZE_Sectors))
            if Random_AU%AU_SIZE_Sectors > 0:
                Random_AU = ((old_div(Random_AU,AU_SIZE_Sectors)) +1)*AU_SIZE_Sectors
                Random_AU = old_div(Random_AU, AU_SIZE_Sectors)
            else:
                Random_AU = old_div(Random_AU, AU_SIZE_Sectors)

            randomLBA = old_div((self.__AUCapacity*1024*1024*Random_AU),512)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Erase to non suspended AU at 0x%x" % randomLBA)

            EndLBA = self.__sdCmdObj.calculate_endLba(startLba = randomLBA, blockcount = self.__blockCount)
            self.__dvtLib.Erase(StartLba = randomLBA, EndLba = EndLBA, directCardAPI=True)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "After Erase to suspended AU sdStatus")
            self.__sdCmdObj.Cmd55()
            sdStatus = self.__sdCmdObj.ACmd13()

            SuspendAddress = ((sdStatus.GetOneByteToInt(18) & 0x3F) << 16) + ((sdStatus.GetOneByteToInt(19) & 0xFF) << 8) + sdStatus.GetOneByteToInt(20)
            SuspendAddress = (SuspendAddress >> 2) * 1024
            ResAddress = self.__StartLba
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************SUS ADDR: %x*************" % SuspendAddress)
            if (SuspendAddress == 0):
                raise ValidationError.TestFailError(self.fn, "should not occur as Erase performed on non suspended AU")

            #Resume Recording
            Argument = 0x68000000
            self.__sdCmdObj.Cmd20(Argument)
            time.sleep(0.250)        #250ms delay
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************[INFO] [Expected] Resume Recording success")

            # Releasing all DIR slot Ids

            Argument = 0x88000000 #slot 1
            for i in range(8):
                #Update DIR Slot
                self.__sdCmdObj.Cmd20(Argument)
                time.sleep(0.050)        #50ms delay
                Argument = Argument + 0x1000000 #next slot

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*************[Pass] Suspend Erase ResumeFunction passed")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VSC CMD20 Tests : End - Suspend Erase non SUS AU Resume test")

        except ValidationError.CVFGenericExceptions as exc:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed with error :%s \n " % exc.GetInternalErrorMessage())
            self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure
            self.__testerror = 1

    def AUwrite(self, StartLba, blockCount):
        self.__StartLba=StartLba
        self.__blockCount=blockCount
        for i in range(self.__RUinAU):
            self.__dvtLib.WriteWithFPGAPattern(self.__StartLba, self.__blockCount, pattern = gvar.GlobalConstants.PATTERN_ALL_ONE)
            self.__StartLba = self.__StartLba + self.__blockCount
            if (((i % 3)==0) and (self.__FATConfig==3)):
                self.FATupdate()

            if (((i % 2)==0) and (self.__FATConfig==2)):
                self.FATupdate()

            if (((i % 1)==0) and (self.__FATConfig==1)):
                self.FATupdate()


    def FATupdate(self):
        FAT1 = random.randint(0x2000, 0x3FDF)
        FAT2 = random.randint(0x4000, 0x5FDF)
        FATblockCount = 0x20    # 16KB
        if FAT1 + FATblockCount > 0x3FDF:
            FAT1 = 0x3FDF-FATblockCount
        if FAT2 + FATblockCount > 0x5FDF:
            FAT2 = 0x5FDF-FATblockCount
        self.__dvtLib.WriteWithFPGAPattern(FAT1, FATblockCount, pattern = gvar.GlobalConstants.PATTERN_ALL_ONE)
        self.__dvtLib.WriteWithFPGAPattern(FAT2, FATblockCount, pattern = gvar.GlobalConstants.PATTERN_ALL_ONE)

    def Run(self):

        globalProjectConfVar = self.__sdCmdObj.DoBasicInit()

        self.__sdCmdObj.Cmd55()
        sdStatus = self.__sdCmdObj.ACmd13()

        self.__VSC_AU_SIZE = (((sdStatus.GetOneByteToInt(16)&0x03) << 8) + sdStatus.GetOneByteToInt(17))

        if ((self.__VSC_AU_SIZE!= 0) and (sdStatus.GetOneByteToInt(15)>0) ):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "**************SD5.0 CMD20 supported******************")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "**************VSC AU size:%d MB******************" % self.__VSC_AU_SIZE)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "**************Video Speed Class : %d ************" % sdStatus.GetOneByteToInt(15))
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "**********SD5.0 CMD20 not supported*****************")
            raise ValidationError.TestFailError(self.fn, "[ERROR]**********SD5.0 CMD20 not supported*****************")

        #VSC support check - SCR fields
        self.__sdCmdObj.Cmd55()
        scrReg = self.__sdCmdObj.GetSCRRegisterEntry()
        #For SD_SPEC
        # if (scrReg.objSCRRegister.ui8SdSpec == 0 and scrReg.objSCRRegister.ui16SdSpec3 == 0 and scrReg.objSCRRegister.ui16SdSpec4 == 0 and scrReg.objSCRRegister.ui16SdSpecx == 0):
        #     raise ValidationError.TestFailError(self.fn, "Physical layer specification version no. 1.0 and 1.01")

        # elif (scrReg.objSCRRegister.ui8SdSpec == 1 and scrReg.objSCRRegister.ui16SdSpec3 == 0 and scrReg.objSCRRegister.ui16SdSpec4 == 0 and scrReg.objSCRRegister.ui16SdSpecx == 0):
        #     raise ValidationError.TestFailError(self.fn, "Physical layer specification version no. 1.10")

        # elif (scrReg.objSCRRegister.ui8SdSpec == 2 and scrReg.objSCRRegister.ui16SdSpec3 == 0 and scrReg.objSCRRegister.ui16SdSpec4 == 0 and scrReg.objSCRRegister.ui16SdSpecx == 0):
        #     raise ValidationError.TestFailError(self.fn, "Physical layer specification version no. 2.00")

        # elif (scrReg.objSCRRegister.ui8SdSpec == 2 and scrReg.objSCRRegister.ui16SdSpec3 == 1 and scrReg.objSCRRegister.ui16SdSpec4 == 0 and scrReg.objSCRRegister.ui16SdSpecx == 0):
        #     raise ValidationError.TestFailError(self.fn, "Physical layer specification version no. 3.0x")

        # elif (scrReg.objSCRRegister.ui8SdSpec == 2 and scrReg.objSCRRegister.ui16SdSpec3 == 1 and scrReg.objSCRRegister.ui16SdSpec4 == 1 and scrReg.objSCRRegister.ui16SdSpecx == 0):
        #     raise ValidationError.TestFailError(self.fn, "Physical layer specification version no. 4.xx")

        if (scrReg.objSCRRegister.ui8SdSpec == 2 and scrReg.objSCRRegister.ui16SdSpec3 == 1 and (scrReg.objSCRRegister.ui16SdSpec4 == 0 or scrReg.objSCRRegister.ui16SdSpec4 == 1) and scrReg.objSCRRegister.ui16SdSpecx == 1):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SD 5.xx Supported")
        elif (scrReg.objSCRRegister.ui8SdSpec == 2 and scrReg.objSCRRegister.ui16SdSpec3 == 1 and (scrReg.objSCRRegister.ui16SdSpec4 == 0 or scrReg.objSCRRegister.ui16SdSpec4 == 1) and scrReg.objSCRRegister.ui16SdSpecx == 2):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SD 6.xx Supported")
        else:
            raise ValidationError.TestFailError(self.fn, "SD 5.xx OR SD 6.xx not supported")

        #Get AU size
        AU  = self.__AUsize.Run(ret = 1)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Au Size %d" % AU)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "cardMaxLba %x" % self.__cardMaxLba)

        self.__AUCapacity = self.__VSC_AU_SIZE
        self.__RUinAU = (old_div((self.__AUCapacity * 1024), 512))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RU in AU:%d" % self.__RUinAU)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*******Set Card to SDR50**********")
        globalProjectConfVar['globalSpeedMode']='SDR50'
        self.__globalSetBusSpeedModeObj.Run(globalProjectConfVar)
        self.__dvtLib.GetCardTransferMode()

        self.__sdCmdObj.SetFrequency(Freq = 80 * 1000)
        self.__sdCmdObj.GetFrequency()

        self.UpdateDIRrepeat()
        self.UpdateDIR_powercycle_repeat()
        self.UpdateReleaseDIRFunction()
        self.ReleaseDIR_Repeat()
        self.SetFreeAuAtZeroAddress()
        self.SuspendAtAuBoundary()
        self.SuspendResumeFunction()
        self.Suspend_writeSUSAU_ResumeFunction()
        self.Suspend_writeotherAU_ResumeFunction()
        self.Suspend_Erase_Other_AU_ResumeFunction()
        self.Suspend_Erase_SUS_AU_ResumeFunction()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*********SD5.0 CMD20 Test script end*********")

        if (self.__testerror == 1):
            raise ValidationError.TestFailError(self.fn, "SD5.0 CMD20 Test completed with failures ")
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "*********SD5.0 CMD20 Test completed*********")


    # Testcase logic - Ends
# Testcase Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_VSCCMD20_Validation(self):
        obj = VSCCMD20_Validation(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
