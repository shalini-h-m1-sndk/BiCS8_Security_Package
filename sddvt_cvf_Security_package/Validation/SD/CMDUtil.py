
"""
################################################################################
# Copyright (c) SanDisk Corp.2013 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# FILE:CMDUtil.py: Command Utility Library.
# AUTHOR: Himanshu Naruka
################################################################################
"""
from __future__ import print_function
from __future__ import division

from builtins import hex
from builtins import str
from builtins import range
from builtins import object
from past.utils import old_div
import sys, os, time, shutil, datetime, random, string, subprocess, csv
from array import *

import CTFServiceWrapper as ServiceWrap
import NVMeCMDWrapper as NVMeWrap
import Core.ValidationError as ValidationError
import Protocol.NVMe.Basic.VTFContainer as VTF
import math
import Validation.SD.TestFixture as TestFixture
import Validation.SD.TestParams as TP

# Shmoo Support libarys
#import GPIOShmooWrapper as GPIOShmooWrap
#import xPlorerCMDWrapper as xPlorerCMDWrap
#**************************************************************************************************************
##
# @brief Runs all the variations in the testObject
# @details
# @return None
# @exception None
#**************************************************************************************************************
class CMDUtil(object):

    cardMap = dict()
    #readBuffer = ServiceWrap.Buffer.CreateBuffer(1)
    def __init__(self):

        self.TF = TestFixture.TestFixture()
        self.configParser = self.TF.testSession.GetConfigInfo()
        self.errorManager = self.TF.testSession.GetErrorManager()
        self.VTFContainer = VTF.VTFContainer()
        self.statistics = self.TF.testSession.GetStatisticsObj()

        self.dataTrackEnabled = False
        if int(self.configParser.GetValue('datatracking_enabled', 0)[0]):
            self.dataTrackEnabled = True

        self.patternDict = dict()
        self.patternTypes = [ServiceWrap.ALL_0, ServiceWrap.ALL_1, ServiceWrap.BYTE_REPEAT, ServiceWrap.RANDOM]

        self.modelPowerParams = ServiceWrap.MODEL_POWER_PARAMS()
        self.modelPowerParams.delayTimeInNanaSec = 1000
        self.modelPowerParams.railID = 0
        self.modelPowerParams.transitionTimeInNanoSec = 1000
        self.uiNamespaceId = 1
        #self.sectorSize = self.TF.testSession.GetLbaSizeInBytes(self.uiNamespaceId)
        self.DPAResetType = None
        #self.HWUtils = ServiceWrap.GenericHWUtilties(self.TF.testSession)
        # SD- Global Variables -----------------------------------------------------------
        self.MULT = 0
        self.BLOCK_LEN  = 0
        self.MemCap = 0
        self.ProtectedArea = 0
        self.ProtectedArea_MemCap = 0
        #---------------------------------------------------------------------------------

    @staticmethod
    def UpdateCardMap(LBA, txLen, patternType):

        for i in range(txLen):
            if LBA in CMDUtil.cardMap:
                CMDUtil.cardMap[LBA] = patternType
            else:
                CMDUtil.cardMap.update({LBA : patternType})

            LBA = LBA + 1
            #print CMDUtil.cardMap

    @staticmethod
    def CheckDataIntegrity(LBA, txLen, readBuffer):

        tmpBuffer = ServiceWrap.Buffer.CreateBuffer(1)
        refBuffer = ServiceWrap.Buffer.CreateBuffer(1)

        for i in range(txLen):
            try:
                expectedPattern = CMDUtil.cardMap[LBA]
                tmpBuffer.Fill(expectedPattern)
            #If LBA is not written it shall have 0.
            except KeyError:
                TestFixture.TestFixture().logger.Info(TestFixture.TestFixture().TAG, "LBA Read before Write. So Data Integrity Not Verified for -> LBA : 0x%08X  TxLen : 0x%08X"%(LBA, txLen))
                return

            if 0 == i:
                refBuffer.FullCopy(tmpBuffer)
            else:
                refBuffer.Append(tmpBuffer)

            LBA = LBA + 1

        #refBuffer.PrintToLog()
        #readBuffer.PrintToLog()

        if 0 == refBuffer.Compare(readBuffer):
            TestFixture.TestFixture().logger.Info(TestFixture.TestFixture().TAG, "Data Integrity PASSED for -> LBA : 0x%08X  TxLen : 0x%08X"%((LBA - txLen), txLen))
        else:
            raise ValidationError.CVFGenericExceptions("Read FAIL", "Data Read is not same as Data Written\n")

    def ResetController(self, disableController = True, shutdown = False, deleteQueues = False, NVMeSubsytemReset = False, isAsync = True, sendType = ServiceWrap.SEND_IMMEDIATE):

        self.TF.logger.Info("\n\nIssuing Reset Controller Command isAsync:\t %s Send type:\t %s \n" %(isAsync, sendType))

        try:
            NVMeWrap.ControllerResetCMD(bytDisable = disableController, bytShutdown = shutdown, bytDeleteQueues = deleteQueues, bytNvmeSubsystemReset = NVMeSubsytemReset, ulShutdownTimeout=1000, ulDisableTimeout=10000, bIsAsync = isAsync, sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def PostReset(self, disableController = True, shutdown = False, deleteQueues = False, NVMeSubsytemReset = False, isAsync = True, sendType = ServiceWrap.SEND_IMMEDIATE):

        self.TF.logger.Info("\n\nIssuing Reset Controller Command. isAsync:\t %s Send type:\t %s \n" %(isAsync, sendType))

        try:
            NVMeWrap.ControllerResetCMD(bytDisable = disableController, bytShutdown = shutdown, bytDeleteQueues = deleteQueues, bytNvmeSubsystemReset = NVMeSubsytemReset, bIsAsync = isAsync, sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def PostPCIeHotReset(self, isAsync = True, sendType = ServiceWrap.SEND_IMMEDIATE):

        self.TF.logger.Info("\n\nIssuing PCIe Hot Reset Command. Send type:\t %s \n" %(sendType))
        try:
            ServiceWrap.PCIeHotReset(isAsync = isAsync, sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def PostPCIeHotResetEnter(self,isAsync = True, sendType = ServiceWrap.SEND_IMMEDIATE):
        self.TF.logger.Info("\n\nIssuing PCIe Hot Reset Enter Controller Command. isAsync:\t %s Send type:\t %s \n" %(isAsync, sendType))
        try:
            ServiceWrap.PCIeHotResetEnter(isAsync = isAsync, sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def PostPCIeHotResetExit(self, sendType = ServiceWrap.SEND_IMMEDIATE):
        self.TF.logger.Info("\n\nIssuing PCIe Hot Reset Exit Controller Command. Send type:\t %s \n" %(sendType))
        try:
            ServiceWrap.PCIeHotResetExit(sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def PostPCIeDSPortResetEnter(self,isAsync = True, sendType = ServiceWrap.SEND_IMMEDIATE):
        self.TF.logger.Info("\n\nIssuing PCIe Down Stream Port Reset Enter Controller Command. isAsync:\t %s Send type:\t %s \n" %(isAsync, sendType))
        try:
            ServiceWrap.PCIeDownStreamPortResetEnter(isAsync = isAsync, sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def PostPCIeDSPortResetExit(self, sendType = ServiceWrap.SEND_IMMEDIATE):
        self.TF.logger.Info("\n\nIssuing PCIe Down Stream Port Reset Exit Controller Command. Send type:\t %s \n" %(sendType))

        try:
            ServiceWrap.PCIeDownStreamPortResetExit(sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def PostFLREnter(self,isAsync = True, sendType = ServiceWrap.SEND_IMMEDIATE):
        self.TF.logger.Info("\n\nIssuing FunctionLevelReset Enter Controller Command. isAsync:\t %s Send type:\t %s \n" %(isAsync, sendType))
        try:
            ServiceWrap.PCIeFLRResetEnter(isAsync = isAsync, sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def PostFLRExit(self, sendType = ServiceWrap.SEND_IMMEDIATE):
        self.TF.logger.Info("\n\nIssuing FunctionLevelReset Exit Controller Command. Send type:\t %s \n" %(sendType))
        try:
            ServiceWrap.PCIeFLRResetExit(sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def AddGetLogPageCmd(self, LID = NVMeWrap.EN_ERROR_INFORMATION, LogPageEntry = 1, NSID = 0, DWORDs = 1):

        self.TF.logger.Info(self.TF.TAG, "Adding to TPL: GETLOGPAGE -> NSID : %d  LogPageIdentifier : 0x%X LogPageEntry : %d DWORDS : 0x%X \n"%(NSID, LID, LogPageEntry, DWORDs))
        GetLogPageObj = NVMeWrap.GetLogPage(LID, LogPageEntry, NSID, DWORDs)
        return GetLogPageObj

    def AddFormatNVMCmd(self, NSID = 1, FORMATDW10 = NVMeWrap.ADMIN_FORMAT_NVM_COMMAND_DW10(), sendType = ServiceWrap.CMD_SEND_TYPE.SEND_IMMEDIATE):

        SupportedLBAformates = self.TF.nLBAf

        try:
            NVMeWrap.FormatNVMCmd(NSID, FORMATDW10, sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def TRIM(self, lbaRangeList = list(), submissionQID = 1, NSID = 1):

        return NVMeWrap.DeAllocate(lbaRangeList, NSID, submissionQID, 20000)

    def PowerCycle(self, PwrCycleMode, protocolParamsObj = ServiceWrap.PROTOCOL_SPECIFIC_PARAMS(), isAsync = True, sendType = ServiceWrap.SEND_IMMEDIATE):

        pGPIOParams = ServiceWrap.GPIO_MAP()
        pGPIOParams.FORCE_DOWNLOAD =1
        pGPIOParams.HALT =1
        pGPIOParams.POWER_ON_OFF =0
        pGPIOParams.UART_BOOT = 1

        if ServiceWrap.GRACEFUL == PwrCycleMode:
            isAsync = False

        else:
            isAsync = random.choice([True, False])

        self.TF.logger.Info(self.TF.TAG, "Adding to TPL: POWER CYCLE -> PC_Type : %s  Async : %s \n"%(PwrCycleMode, isAsync))
        try:
            ServiceWrap.PowerCycle(PwrCycleMode, self.modelPowerParams, pGPIOParams, protocolParamsObj, isAsync, sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        return pwrCycle

    def GetFeature(self, FID = 1, SEL = 0, nameSpaceID = 0):

        self.TF.logger.Info("Posting ADMIN Command: Get Feature\n")

        try:
            GetFeature = NVMeWrap.GetFeatures(FID, SEL, nameSpaceID)
            GetFeature.Execute()
            GetFeature.HandleOverlappedExecute()
            GetFeature.HandleAndParseResponse()
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        SC = GetFeature.objNVMeComIOEntry.completionEntry.DW3.SF.SC
        assert(TP.SC['SUCCESSFUL_COMPLETION'] == SC), "GetFeature  Command Execution Failed.\n"
        DWrd0 = GetFeature.objNVMeComIOEntry.completionEntry.DW0;
        return(DWrd0)

    def SetTempThreshold(self, TempThreshold):

        NS_ID = 0
        try:
            ObjSetTempThreshold = NVMeWrap.SetFeatures(NVMeWrap.FID_TEMP_THRESHOLD, False, 0, NS_ID)
            ObjSetTempThreshold.SetTempThresholdTMPTH(TempThreshold)
            ObjSetTempThreshold.Execute()
            ObjSetTempThreshold.HandleOverlappedExecute()
            ObjSetTempThreshold.HandleAndParseResponse()
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        SC = ObjSetTempThreshold.objNVMeComIOEntry.completionEntry.DW3.SF.SC
        assert(TP.SC['SUCCESSFUL_COMPLETION'] == SC), "SetFeature-TempThreshold Command Execution Failed.\n"

    def SetAsysncEventNotice(self, AsynscEvent):

        NS_ID = 0xFFFFFFFF
        try:
            ObjSetAysncEvent = NVMeWrap.SetFeatures(NVMeWrap.FID_ASYNC_EVENT_CONFIG, False, 0, NS_ID)
            ObjSetAysncEvent.SetAsyncEventConfigSMART(AsynscEvent)
            ObjSetAysncEvent.Execute()
            ObjSetAysncEvent.HandleOverlappedExecute()
            ObjSetAysncEvent.HandleAndParseResponse()
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        SC = ObjSetAysncEvent.objNVMeComIOEntry.completionEntry.DW3.SF.SC
        assert(TP.SC['SUCCESSFUL_COMPLETION'] == SC), "SetFeature-AysncEvent Command Execution Failed.\n"


    def AddAbortCmd(self, SQID = 1):

        self.TF.logger.Info("Posting ADMIN Command: Abort\n")
        AbortCmd = NVMeWrap.AbortCmd(SQID, 30000)

        return AbortCmd


    def AddAttacheNS(self, NS_ID = 1, Ctrl_ID = 0):
        Ctrl_List = NVMeWrap.NAMESPACE_ATTACHMENT_CONTROLLER_LIST_FORMAT_BUFFER
        Ctrl_List.Identifier_N = Ctrl_ID

        AttachNS = NVMeWrap.AttachNamespace(NS_ID, Ctrl_List, 30000)

        return AttachNS


    def AddCreateNS(self, nZSE = 0x0001000000, nCAP = 0x0001000000, fLBAS = 1,  dPS = 1, nMIC = 0):

        NS_data = NVMeWrap.NAMESPACE_MANAGEMENT
        NS_data.NSZE = nZSE
        NS_data.NCAP = nCAP
        NS_data.FLBAS = fLBAS
        NS_data.DPS = dPS
        NS_data.NMIC = nMIC

        CreateNS = NVMeWrap.CreateNamespace(NS_data, 30000)

        return CreateNS

    def AddDetachNS(self, NS_ID =1, Ctrl_ID = 0):

        Ctrl_List = NVMeWrap.NAMESPACE_ATTACHMENT_CONTROLLER_LIST_FORMAT_BUFFER
        Ctrl_List.Identifier_N = Ctrl_ID
        DetachNS = NVMeWrap.DetachNamespace(NS_ID, Ctrl_List, 30000)

        return DetachNS

    def AddDeleteNS(self, NS_ID = 1):
        #Delete NS
        self.TF.logger.Info(self.TF.TAG, "Issuing Delete-NS Command\n")
        DeleteNS = NVMeWrap.DeleteNamespace(NS_ID, 30000)

        return DeleteNS

    def ActivateController(self, disableController = False, shutdown = False, deleteQueues = False, NVMeSubsytemReset = False, sendType = ServiceWrap.CMD_SEND_TYPE.SEND_IMMEDIATE):

        #Activate Controller
        self.TF.logger.Info(self.TF.TAG, "Issuing Activate Controller Command\n")
        try:
            NVMeWrap.ActivateCntrlrCMD(bytDisableDone = disableController, bytShutdownDone = shutdown, bytDeleteQueuesDone = deleteQueues, bytNvmeSubsystemResetDone = NVMeSubsytemReset, sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def PostActivateController(self, disableController = False, shutdown = False, deleteQueues = False, NVMeSubsytemReset = False, isAsync = True, sendType = ServiceWrap.CMD_SEND_TYPE.SEND_IMMEDIATE):

        #Activate Controller
        self.TF.logger.Info(self.TF.TAG, "Issuing Activate Controller Command\n")

        try:
            NVMeWrap.ActivateCntrlrCMD(bytDisableDone = disableController, bytShutdownDone = shutdown, bytDeleteQueuesDone = deleteQueues, bytNvmeSubsystemResetDone = NVMeSubsytemReset, sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def AddCreateCQ(self, QueueSize, QueueCID):

        MsgID = (QueueCID-1)

        CreateCQ = NVMeWrap.CreateCQ(QueueSize, QueueCID, MsgID)

        return CreateCQ

    def AddCreateSQ(self, QueueSize, QueueSID, QueueCID, QPriority):

        CreateSQ = NVMeWrap.CreateSQ(QueueSize, QueueSID, QueueCID, QPriority)

        return CreateSQ

    def AddDeleteCQ(self, QueueCID):

        CreateCQ = NVMeWrap.DeleteCQ(QueueCID)

        return CreateCQ


    def AddDeleteSQ(self, QueueSID):
        CreateSQ = NVMeWrap.DeleteSQ(QueueSID)

        return CreateSQ

    def CreateCQ(self, QueueSize, QueueCID, sendType = ServiceWrap.CMD_SEND_TYPE.SEND_IMMEDIATE):

        self.TF.logger.Info("Posting ADMIN Command: Create IOCQ Nr : %d QSize : %d \n"%(QueueCID, QueueSize))

        MsgID = (QueueCID-1)
        #objCreateCQ = NVMeWrap.CreateCQ(QueueSize, QueueCID, MsgID)
        #objCreateCQ.Execute()
        #objCreateCQ.HandleOverlappedExecute()
        #objCreateCQ.HandleAndParseResponse()

        try:
            NVMeWrap.CreateCQ(QueueSize, QueueCID, MsgID, sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #SC = objCreateCQ.objNVMeComIOEntry.completionEntry.DW3.SF.SC

        #assert(TP.SC['SUCCESSFUL_COMPLETION'] == SC), "Create-CQ Command Execution Failed.\n"

    def CreateSQ(self, QueueSize, QueueSID, QueueCID, QPriority, UnalignedStep = 0,  sendType = ServiceWrap.CMD_SEND_TYPE.SEND_IMMEDIATE):

        self.TF.logger.Info("Posting ADMIN Command: Create IOSQ Nr : %d QSize : %d \n"%(QueueSID, QueueSize))

        #objCreateSQ = NVMeWrap.CreateSQ(QueueSize, QueueSID, QueueCID, QPriority)
        #objCreateSQ.Execute()
        #objCreateSQ.HandleOverlappedExecute()
        #objCreateSQ.HandleAndParseResponse()
        try:
            if(UnalignedStep>0):
                NVMeWrap.CreateSQ(QueueSize, QueueSID, QueueCID, QPriority, UnalignedStep, sendType)
            else:
                UnalignedStep = 0
                NVMeWrap.CreateSQ(QueueSize, QueueSID, QueueCID, QPriority, UnalignedStep, sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #SC = objCreateSQ.objNVMeComIOEntry.completionEntry.DW3.SF.SC

        #assert(TP.SC['SUCCESSFUL_COMPLETION'] == SC), "Create-SQ  Command Execution Failed.\n"

    def DeleteCQ(self, QueueCID, sendType = ServiceWrap.CMD_SEND_TYPE.SEND_IMMEDIATE):

        self.TF.logger.Info("Posting ADMIN Command: Delete IOCQ Nr: %d\n"%QueueCID)

        #objDeleteCQ = NVMeWrap.DeleteCQ(QueueCID)
        #objDeleteCQ.Execute()
        #objDeleteCQ.HandleOverlappedExecute()
        #objDeleteCQ.HandleAndParseResponse()
        try:
            NVMeWrap.DeleteCQ(QueueCID, sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #SC = objDeleteCQ.objNVMeComIOEntry.completionEntry.DW3.SF.SC

        #assert(TP.SC['SUCCESSFUL_COMPLETION'] == SC), "Delete-SQ  Command Execution Failed.\n"

    def DeleteSQ(self, QueueSID, sendType = ServiceWrap.CMD_SEND_TYPE.SEND_IMMEDIATE):

        self.TF.logger.Info("Posting ADMIN Command: Delete IOSQ Nr: %d\n"%QueueSID)

        #objDeleteSQ = NVMeWrap.DeleteSQ(QueueSID)
        #objDeleteSQ.Execute()
        #objDeleteSQ.HandleOverlappedExecute()
        #objDeleteSQ.HandleAndParseResponse()
        try:
            NVMeWrap.DeleteSQ(QueueSID, sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #SC = objDeleteSQ.objNVMeComIOEntry.completionEntry.DW3.SF.SC

        #assert(TP.SC['SUCCESSFUL_COMPLETION'] == SC), "Delete-SQ  Command Execution Failed.\n"

    def CreateAllQs(self, QueueDepth = 256, NOQs = 8,sendType = ServiceWrap.CMD_SEND_TYPE.SEND_IMMEDIATE):

        if self.TF.VTFContainer.isModel:
            NOQs = self.TF.NumOfCore

        try:
            NVMeWrap.CreateAllQs(QueueDepth, NOQs, sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def AddCreateAllQs(self):

        self.TF.logger.Info("Posting ADMIN Command: Create All IOQs\n")

        ObjCreateAllQs = NVMeWrap.CreateAllQs()

    def DeleteAllQs(self,Timeout = 30,isAsync=True, sendType = ServiceWrap.CMD_SEND_TYPE.SEND_IMMEDIATE):

        try:
            NVMeWrap.DeleteAllQs(Timeout,isAsync,sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def AddDeleteAllQs(self):

        self.TF.logger.Info("Posting ADMIN Command: Delete All IOQs\n")

        ObjDeleteAllQs = NVMeWrap.DeleteAllQs()


    def FlushCahe(self, nameSpace = 1, SubQID = 1, sendType = ServiceWrap.SEND_IMMEDIATE):

        self.TF.logger.Info("Posting Command: Flush Cache\n")

        try:
            if(SubQID <= self.TF.nrOfsubmissionQ):
                FlushCacheObj = NVMeWrap.FlushCache(nameSpace, SubQID, sendType = sendType)
            else:
                assert(SubQID > self.TF.nrOfsubmissionQ), "Error: Invalid Parameter\n"
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def GetPwrStateCap(self, CAP, sendType = ServiceWrap.SEND_IMMEDIATE):

        try:
            ObjGetFeature = NVMeWrap.GetFeatures(NVMeWrap.FID_PWR_MGMT, CAP, 0xFFFFFFFF, sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        return ObjGetFeature

    def SetPwrState(self, DW11 = 0, sendType = ServiceWrap.SEND_IMMEDIATE):

        try:
            ObjSetFeature = NVMeWrap.SetFeatures(NVMeWrap.FID_PWR_MGMT, False, DW11, 0xFFFFFFFF, sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        return ObjSetFeature

    def DisableVolWriteCache(self, sendType = ServiceWrap.SEND_IMMEDIATE):
        identifyObj = self.IdentifyController()
        if (identifyObj.VWC.Present==0):
            self.TF.logger.Info("Volatile Cache is not present in device. Skipping Disable Cache Command")
            return
        ObjSetFeature = None
        self.TF.logger.Info("Posting ADMIN Command: Disable Cache\n")

        try:
            ObjSetFeature = NVMeWrap.SetFeatures(NVMeWrap.FID_VOL_WR_CACHE, False, 1, 0xFFFFFFFF, sendType = sendType)
            ObjSetFeature.SetVolatileWriteCacheWCE(0)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def EnableVolWriteCache(self, sendType = ServiceWrap.SEND_IMMEDIATE):
        identifyObj = self.IdentifyController()
        if (identifyObj.VWC.Present==0):
            self.TF.logger.Info("Volatile Cache is not present in device. Skipping Enable Cache Command")
            return
        ObjSetFeature = None

        self.TF.logger.Info("Posting ADMIN Command: Enable Cache\n")
        try:
            ObjSetFeature = NVMeWrap.SetFeatures(NVMeWrap.FID_VOL_WR_CACHE, False, 1, 0xFFFFFFFF, sendType = sendType)
            ObjSetFeature.SetVolatileWriteCacheWCE(1)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def EnableWriteAutomicity(self):

        DN = 0 #Disable Normal-
        try:
            ObjSetFeatureWrAtom = NVMeWrap.SetFeatures(NVMeWrap.FID_WRITE_ATOMICITY, False, 1, 0xFFFFFFFF)
            ObjSetFeatureWrAtom.SetWriteAtomicityDN(DN)
            ObjSetFeatureWrAtom.Execute()
            ObjSetFeatureWrAtom.HandleOverlappedExecute()
            ObjSetFeatureWrAtom.HandleAndParseResponse()
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        SC = ObjSetFeatureWrAtom.objNVMeComIOEntry.completionEntry.DW3.SF.SC
        assert(TP.SC['SUCCESSFUL_COMPLETION'] == SC), "FlushCache  Command Execution Failed.\n"

    def DisableWriteAutomicity(self):

        DN = 1 #Disable Normal- AWUN, NAWUN, AWUPF, and NAWUPF shall be honored by the controller
        try:
            ObjSetFeatureWrAtom = NVMeWrap.SetFeatures(NVMeWrap.FID_WRITE_ATOMICITY, False, 1, 0xFFFFFFFF)
            ObjSetFeatureWrAtom.SetWriteAtomicityDN(DN)
            ObjSetFeatureWrAtom.Execute()
            ObjSetFeatureWrAtom.HandleOverlappedExecute()
            ObjSetFeatureWrAtom.HandleAndParseResponse()
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        SC = ObjSetFeatureWrAtom.objNVMeComIOEntry.completionEntry.DW3.SF.SC
        assert(TP.SC['SUCCESSFUL_COMPLETION'] == SC), "FlushCache  Command Execution Failed.\n"

    def DeviceHealth(self, LoopCnt):

        try:
            ObjGetDevHealth = NVMeWrap.GetDeviceHealth()
            ObjGetDevHealth.Execute()
            ObjGetDevHealth.HandleOverlappedExecute()
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        self.TF.logger.Message(self.TF.TAG, "\n**********************    Device/Controller Health Info    ***************************\n")
        self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('UP TimeMs', ObjGetDevHealth.objOutputdata.basicInfo.upTimeMs))
        self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('OpMode', ObjGetDevHealth.objOutputdata.basicInfo.opMode))
        self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('FailureCodeBitmap', ObjGetDevHealth.objOutputdata.basicInfo.failureCodeBitmap))
        self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Controller Status', ObjGetDevHealth.objOutputdata.basicInfo.controllerStatus))
        self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Controller Configuration', ObjGetDevHealth.objOutputdata.basicInfo.controllerConfiguration))
        self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('controller Capabilities', ObjGetDevHealth.objOutputdata.basicInfo.controllerCapabilities))
        self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Number Of ConfiguredSQs', ObjGetDevHealth.objOutputdata.basicInfo.numberOfConfiguredSQs))
        self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Number Of ConfiguredCQs', ObjGetDevHealth.objOutputdata.basicInfo.numberOfConfiguredCQs))
        self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Controller Shutdown', ObjGetDevHealth.objOutputdata.basicInfo.controllerShutdown))
        self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Controller Ready', ObjGetDevHealth.objOutputdata.basicInfo.controllerReady))
        self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Processing Paused', ObjGetDevHealth.objOutputdata.basicInfo.processingPaused))
        self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Subsystem ResetOccured', ObjGetDevHealth.objOutputdata.basicInfo.controllerReady))

        nrOfSQ = ObjGetDevHealth.objOutputdata.basicInfo.numberOfConfiguredSQs
        nrOfCQ = ObjGetDevHealth.objOutputdata.basicInfo.numberOfConfiguredCQs

        SQ_Data = ObjGetDevHealth.objOutputdata.sqData
        self.TF.logger.Message(self.TF.TAG, "\n**********************    Submission Queue Attributes    ***************************\n")
        self.TF.logger.Message(self.TF.TAG, "QueueID\t\tHisMaxDepth\t\tMaxCap\t\tNumBufReq\t\tCurntDep\t\tCurntDep\t\tQTailOff\t\tQHeadOff\t\tCmdProcCnt\t\tQPrior\t\tCplQ-ID\n")

        if (self.TF.NumDriverMappedMSI <= self.TF.NumOfCore):
            queueRange = self.TF.NumDriverMappedMSI
        else:
            queueRange = self.TF.NumOfCore

        for cnt1 in range(0, queueRange):
            self.ObjSqData = SQ_Data[cnt1]
            self.TF.logger.Message(self.TF.TAG, "%s\t\t\t%s\t\t\t\t%s\t\t\t%s\t\t\t%s\t\t\t\t%s\t\t\t\t%s\t\t\t\t%s\t\t\t\t%s\t\t\t%s\t\t\t\t%s\n"%(self.ObjSqData.queueID, self.ObjSqData.historicalMaxDepth, self.ObjSqData.maxCapacity, self.ObjSqData.maxCapacity, self.ObjSqData.numBufferedRequests, self.ObjSqData.currentDepth, self.ObjSqData.qTailOffset, self.ObjSqData.qHeadOffset, self.ObjSqData.commandsProccessedCount, self.ObjSqData.queuePriority, self.ObjSqData.cplQueueID))
        self.TF.logger.Message(self.TF.TAG, "\n**********************    Completion Queue Attributes    ***************************\n")
        CQData = ObjGetDevHealth.objOutputdata.cqData
        self.TF.logger.Message(self.TF.TAG, "Used\t\tQueueID\t\tMaxCap\t\tCurntDep\t\tMSImsgID\t\tCmdProcCnt\t\tqTlOff\t\tqHdOff\n")
        for cnt2 in range(0, queueRange):
            self.ObjCqData = CQData[cnt2]
            self.TF.logger.Message(self.TF.TAG, "%s\t\t\t%s\t\t\t%s\t\t%s\t\t\t%s\t\t\t\t%s\t\t\t\t%s\t\t\t\t%s\n"%(self.ObjCqData.used, self.ObjCqData.queueID, self.ObjCqData.maxCapacity, self.ObjCqData.currentDepth, self.ObjCqData.msiMessageId, self.ObjCqData.commandsProccessedCount, self.ObjCqData.qTailOffset, self.ObjCqData.qHeadOffset))

        return (nrOfSQ, nrOfCQ)

    def PowerOffPowerOn(self, powerCycleType):

        if self.TF.sustainedMode:
            return

        powerOff = ServiceWrap.GenericPowerOff(powerCycleType)
        powerOn = ServiceWrap.GenericPowerOn()

        #Post and Execute Power Off Command.
        try:
            self.TF.threadPool.PostRequestToWorkerThread(powerOff)
        except self.TF.CVFExceptions as ex:
            self.TF.logger.Fatal(self.TF.TAG, "Failed to Post the Command to Threadpool. Exception Message is->\n %s "%ex.GetFailureDescription())
            #Flush all the pending log messages.
            self.TF.logger.FlushAllMsg()
            assert(True == False), ex.GetFailureDescription()

        #Run the commands queued up in ThreadPool.
        status = False
        status = self.TF.threadPool.WaitForThreadCompletion()
        if False == status:
            self.__CheckForErrors()
            assert(True == False), self.errorManager.GetAllFailureDescription()

        #Post and Execute Power On Command.
        try:
            self.TF.threadPool.PostRequestToWorkerThread(powerOn)
        except self.TF.CVFExceptions as ex:
            self.TF.logger.Fatal(self.TF.TAG, "Failed to Post the Command to Threadpool. Exception Message is->\n %s "%ex.GetFailureDescription())
            #Flush all the pending log messages.
            self.TF.logger.FlushAllMsg()
            assert(True == False), ex.GetFailureDescription()

        #Run the commands queued up in ThreadPool.
        status = False
        status = self.TF.threadPool.WaitForThreadCompletion()
        if False == status:
            self.__CheckForErrors()
            assert(True == False), self.errorManager.GetAllFailureDescription()

    def IdentifyController(self):

        try:
            identifyContObj = NVMeWrap.IdentifyController(sendType = ServiceWrap.SEND_IMMEDIATE)
            return identifyContObj.objOutputData
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def IdentifyNamespace(self, nameSpaceID = 0xFFFFFFFF, sendType = ServiceWrap.SEND_IMMEDIATE):

        self.TF.logger.Info("Posting Identify Namespace -> NSID : 0x%08X  "%(nameSpaceID))
        try:
            identifyNSObj = NVMeWrap.IdentifyNamespace(nameSpaceID, sendType)
            return identifyNSObj.objOutputData
        except ValidationError.CVFExceptionTypes as exc:
            raise ValidationError.CVFGenericExceptions (self.VTFContainer.GetTestName(), "Error occurred in IdentifyNamespace"+ exc.GetFailureDescription())

    def ErrorIdentifyNamespace(self, nameSpaceID = 0xFFFFFFFF, sendType = ServiceWrap.SEND_IMMEDIATE):

        self.TF.logger.Info("Posting Identify Namespace -> NSID : 0x%08X  "%(nameSpaceID))
        try:
            identifyNSObj = NVMeWrap.IdentifyNamespace(nameSpaceID, sendType)
        except ValidationError.CVFExceptionTypes as exc:
            raise ValidationError.CVFGenericExceptions (self.VTFContainer.GetTestName(), "Error occurred in IdentifyNamespace"+ exc.GetFailureDescription())

    def DeviceSelfTest(self, testType, nameSpaceID):

        self.TF.logger.Info(self.TF.TAG, "Posting DST -> NSID : 0x%08X  TestType : 0x%02X "%(nameSpaceID, testType))

        if self.TF.sustainedMode:
            selfTest = NVMeWrap.DST(testType, nameSpaceID)
        else:
            selfTest = NVMeWrap.DST(testType, nameSpaceID)

        return selfTest

    def DumpDSTLog(self, DSTBuffer):

        self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Device Self-Test Operation', DSTBuffer.GetOneByteToInt(0)))
        self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Device Self-Test Completion', str(DSTBuffer.GetOneByteToInt(1)) + ' %'))

        nrOfTestRes = TP.MAX_NUM_DST_RESULTS
        offset = TP.FIRST_DST_RESULT_OFFSET

        for i in range(nrOfTestRes):

            self.TF.logger.Message(self.TF.TAG, "\nDevice Self-Test result of %d test\n"%i)
            self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Device Self-Test Status', DSTBuffer.GetOneByteToInt(offset)))
            self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Segment Number', DSTBuffer.GetOneByteToInt(offset + 1)))
            self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Valid Diagnostic Information', DSTBuffer.GetOneByteToInt(offset + 2)))
            self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Power On Hours - POH', DSTBuffer.GetEightBytesToInt(offset + 4)))
            self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Namespace Identifier - NSID', DSTBuffer.GetFourBytesToInt(offset + 12)))
            self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Failing LBA', DSTBuffer.GetEightBytesToInt(offset + 16)))
            self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Status Code Type', DSTBuffer.GetOneByteToInt(offset + 24)))
            self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Status Code', DSTBuffer.GetOneByteToInt(offset + 25)))

            offset = offset + TP.DST_RESULT_STRUCTURE_SIZE

    def PostIdentifyController(self, sendType = ServiceWrap.SEND_IMMEDIATE):
        try:
            identifyContObj = NVMeWrap.IdentifyController(sendType = sendType)
            return identifyContObj.objOutputData
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def PostWriteLba(self, startLba, transferLength, submissionQID = 1, nameSpaceID = 1, FUA = 0, pattern = 0, writeTimeout = None, writeBuffer = None, sendType = ServiceWrap.SEND_QUEUED):

        self.TF.NrofBytesWritten += ( transferLength * self.sectorSize )
        self.TF.NrofWriteCmds += 1

        if writeTimeout is not None:
            self.configParser.SetValue('write_time_out', writeTimeout)

        #RG: 26-09-17. This restriction may no longer be valid.
        if self.TF.isSNDKDrive and transferLength >= 1024:
            transferLength = 1024

        if self.TF.isCMDMgrSwitch and 0 == self.TF.nrOfCommands % 2000:
            self.ChangeCMDMgrMode()

        #if there are at least 2000 commands posted, invoke wait for thread completion to avoid Insufficient Memeory Error.
        if 0 == self.TF.nrOfCommands % 2000 and False == self.TF.sustainedMode and 0 != self.TF.nrOfCommands:
            self.__CallWaitForThreadCompletion()

        isScsiWrite = False

        #Create the WriteCommand.

        self.TF.logger.Info(self.TF.TAG, "Adding to TPL: WLBA -> NSID : %d  SQID : %d LBA : 0x%08X  TxLen : 0x%08X  PatternIndex : 0x%02X "%(nameSpaceID, submissionQID, startLba, transferLength, pattern))

        try:
            if self.TF.Mode3 and self.dataTrackEnabled:
                writeCommand = NVMeWrap.WriteCommand(startLba, transferLength, submissionQID, nameSpaceID, FUA, writeBuffer, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, pattern, sendType = sendType)

            elif self.TF.Mode3 and not self.dataTrackEnabled:
                TPLWriteBuff = ServiceWrap.Buffer.CreateBuffer(transferLength, pattern)
                TPLWriteBuff.Fill(self.TF.patternDict[pattern])
                writeCommand = NVMeWrap.WriteCommand(startLba, transferLength, submissionQID, nameSpaceID, FUA, TPLWriteBuff, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, pattern, sendType = sendType)

            elif False == self.dataTrackEnabled:

                TPLWriteBuff = ServiceWrap.Buffer.CreateBuffer(transferLength, pattern)
                TPLWriteBuff.Fill(self.TF.patternDict[pattern])
                writeCommand = NVMeWrap.WriteCommand(startLba, transferLength, submissionQID, nameSpaceID, FUA, TPLWriteBuff)
                self.TF.threadPool.PostRequestToWorkerThread(writeCommand)
            elif self.dataTrackEnabled:
                writeCommand = NVMeWrap.WriteCommand(startLba, transferLength, submissionQID, nameSpaceID, FUA, None, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, m_patternID = pattern)
                self.TF.threadPool.PostRequestToWorkerThread(writeCommand)

            self.TF.logger.Info(self.TF.Latency_TAG, "Latency for WLBA: -> LBA : 0x%08X  TxLen : 0x%08X Latency : %d"%(startLba, transferLength, writeCommand.GetExecutionLatecy()))

        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        if self.TF.continuosMode and not self.dataTrackEnabled:
            CMDUtil.UpdateCardMap(startLba, transferLength, self.TF.patternDict[pattern])

            return writeCommand

    def PostReadLba(self, startLba, transferLength, submissionQID = 1, nameSpaceID = 1,  FUA = 0, patternIndex = 0, readTimeout = None, readBuffer = None, sendType = ServiceWrap.SEND_QUEUED):

        self.TF.NrofBytesRead += ( transferLength * self.sectorSize )
        self.TF.NrofReadCmds += 1

        if readTimeout is not None:
            self.configParser.SetValue('read_time_out', readTimeout)

        #RG: 26-09-17. This restriction may no longer be valid.
        if self.TF.isSNDKDrive and transferLength >= 1024:
            transferLength = 1024

        if self.TF.isCMDMgrSwitch and 0 == self.TF.nrOfCommands % 2000:
            self.ChangeCMDMgrMode()

        #if there are at least 2000 commands posted, invoke wait for thread completion to avoid Insufficient Memeory Error.
        if 0 == self.TF.nrOfCommands % 2000 and False == self.TF.sustainedMode and 0 != self.TF.nrOfCommands:
            self.__CallWaitForThreadCompletion()

        isScsiWrite = False

        #Perform Write Operation on the requested LBA range on the nameSpace.
        self.TF.logger.Info(self.TF.TAG, "Adding to TPL: RDLBA -> NSID : %d  SQID : %d LBA : 0x%08X  TxLen : 0x%08X "%(nameSpaceID, submissionQID, startLba, transferLength))

        try:
            if self.TF.Mode3 and self.dataTrackEnabled:
                readcommand = NVMeWrap.ReadCommand(startLba, transferLength, submissionQID, nameSpaceID, FUA, None, sendType = sendType)

            elif self.TF.Mode3 and not self.dataTrackEnabled:
                readBuff = ServiceWrap.Buffer.CreateBuffer(transferLength)
                readcommand = NVMeWrap.ReadCommand(startLba, transferLength, submissionQID, nameSpaceID, FUA, readBuff, sendType = sendType)

            elif False == self.dataTrackEnabled:
                readBuff = ServiceWrap.Buffer.CreateBuffer(transferLength)
                readcommand = NVMeWrap.ReadCommand(startLba, transferLength, submissionQID, nameSpaceID, FUA, readBuff)
                self.TF.threadPool.PostRequestToWorkerThread(readcommand)
            else:
                readcommand = NVMeWrap.ReadCommand(startLba, transferLength, submissionQID, nameSpaceID, FUA, None)
                self.TF.threadPool.PostRequestToWorkerThread(readcommand)

            self.TF.logger.Info(self.TF.Latency_TAG, "Latency for RDLBA: -> LBA : 0x%08X  TxLen : 0x%08X Latency : %d"%(startLba, transferLength, readcommand.GetExecutionLatecy()))

        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        #if self.TF.continuosMode and not self.dataTrackEnabled:
            #readBuff = ServiceWrap.Buffer.CreateBuffer(transferLength)
            #CMDUtil.CheckDataIntegrity(startLba, transferLength, readBuff)
        return readcommand

    def PostTrim(self, lbaRangeList = list(), submissionQID = 1, NSID = 1, sendType = ServiceWrap.SEND_QUEUED):

        self.TF.NrofTrimCmds += 1

        self.TF.logger.Info(self.TF.TAG, "Adding to TPL: TRIM -> NSID : %d  SQID : %d"%(NSID, submissionQID))

        if self.TF.isCMDMgrSwitch and 0 == self.TF.nrOfCommands % 2000:
            self.ChangeCMDMgrMode()

        try:
            trimCommand = NVMeWrap.DeAllocate(lbaRangeList, NSID, submissionQID, sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        self.TF.logger.Info(self.TF.Latency_TAG, "Latency for TRIM: Latency : %d"%(trimCommand.GetExecutionLatecy()))

    def PostWUC(self, NameSpaceID = 1 , SQID = 1, SLBA = 1,  NLBA = 1, writeTimeout = None, sendType = ServiceWrap.SEND_QUEUED):

        self.TF.NrofWUCCmds += 1

        #RG: 26-09-17. This restriction may no longer be valid.
        #if self.TF.isSNDKDrive and NLBA >= 127:
            #NLBA = 127

        self.TF.logger.Info(self.TF.TAG, "Adding to TPL: WUC -> NSID : %d  SQID : %d LBA : 0x%08X  TxLen : 0x%08X "%(NameSpaceID, SQID, SLBA, NLBA))

        if self.TF.isCMDMgrSwitch and 0 == self.TF.nrOfCommands % 2000:
            self.ChangeCMDMgrMode()

        try:
            WUCCommand = NVMeWrap.WriteUncorrectable(NameSpaceID, SQID, SLBA, NLBA, sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        self.TF.logger.Info(self.TF.Latency_TAG, "Latency for WUC: Latency : %d"%(WUCCommand.GetExecutionLatecy()))


    def PostWrite0(self, startLba, LR = 0, FUA = 0, PRINFO = 0, NLB = 1, ILBRT = 0, LBATM = 0, LBAT = 0, NameSpaceID = 1, SQID = 1, writeTimeout = None, sendType = ServiceWrap.SEND_QUEUED):

        self.TF.NrofWrite0Cmds += 1

        #RG: 26-09-17. This restriction may no longer be valid.
        #if self.TF.isSNDKDrive and NLB >= 127:
            #NLB = 127

        self.TF.logger.Info(self.TF.TAG, "Adding to TPL: WRITE0 -> NSID : %d  SQID : %d LBA : 0x%08X  TxLen : 0x%08X "%(NameSpaceID, SQID, startLba, NLB))

        if self.TF.isCMDMgrSwitch and 0 == self.TF.nrOfCommands % 2000:
            self.ChangeCMDMgrMode()

        try:
            writeZero = NVMeWrap.WriteZeroes(startLba, LR, FUA, PRINFO, NLB, ILBRT, LBATM, LBAT, NameSpaceID, SQID, sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        self.TF.logger.Info(self.TF.Latency_TAG, "Latency for Write Zero: Latency : %d"%(writeZero.GetExecutionLatecy()))

    def PostCompare(self, startLba, transferLength, userData = None, fua = False, fused = 0, lr = 1, prinfo = 0, eilbrt = 0, elbatm = 0,\
                    elbat = 0, namespaceID = 1, submissionQID = 1, compareTimeout = 20000000, sendType = ServiceWrap.SEND_QUEUED):

        self.TF.NrofCmprCmds += 1
        identifyObj = self.IdentifyController()
        if(identifyObj.FUSES.SupportsCompare_Write==0):
            self.TF.logger.Info("Device doesn't support Write Compare . Skipping Command")
            return
        if self.TF.isCMDMgrSwitch and 0 == self.TF.nrOfCommands % 2000:
            self.ChangeCMDMgrMode()

        #Perform Compare Operation on the requested LBA range on the nameSpace.
        self.TF.logger.Info(self.TF.TAG, "Adding to TPL: COMPARE -> NSID : %d  SQID : %d LBA : 0x%08X  TxLen : 0x%08X "%(namespaceID, submissionQID, startLba, transferLength))

        try:
            NVMeWrap.Compare(startLBA = startLba, noOfBlocks = transferLength, userData = userData, FUA = fua, FUSED = fused, LR = lr, prInfo = prinfo, eILBRT = eilbrt, eLBATM = elbatm,\
                             eLBAT = elbat, nameSpaceID = namespaceID, sQID = submissionQID, sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def PostLogPage(self, LID = NVMeWrap.EN_ERROR_INFORMATION, LogPageEntry = 1, NSID = 0, DWORDs = 1, sendType = ServiceWrap.SEND_IMMEDIATE):

        self.TF.logger.Info(self.TF.TAG, "Adding to TPL: GETLOGPAGE -> NSID : %d  LogPageIdentifier : 0x%X LogPageEntry : %d DWORDS : 0x%X \n"%(NSID, LID, LogPageEntry, DWORDs))

        try:
            GetLogPageCmd = NVMeWrap.GetLogPage(LID, LogPageEntry, NSID, DWORDs, sendType = sendType)
        except ValidationError.CVFExceptionTypes as exc:
            raise ValidationError.CVFGenericExceptions("FrameworkExpansion",exc.GetFailureDescription())

        return GetLogPageCmd.smartHealthInformation

    def PostPowerCycle(self, PwrCycleMode, protocolParamsObj = ServiceWrap.PROTOCOL_SPECIFIC_PARAMS(), isAsync = True, sendType = ServiceWrap.SEND_IMMEDIATE):

        pGPIOParams = ServiceWrap.GPIO_MAP()
        pGPIOParams.FORCE_DOWNLOAD =1
        pGPIOParams.HALT =1
        pGPIOParams.POWER_ON_OFF =0
        pGPIOParams.UART_BOOT = 1

        if ServiceWrap.GRACEFUL == PwrCycleMode:
            isAsync = False

        else:
            isAsync = random.choice([True, False])

        self.TF.logger.Info(self.TF.TAG, "Adding to TPL: POWER CYCLE -> PC_Type : %s  Async : %s \n"%(PwrCycleMode, isAsync))

        try:
            ServiceWrap.PowerCycle(PwrCycleMode, self.modelPowerParams, pGPIOParams, protocolParamsObj, isAsync, sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def PostConsecutiveResets(self, firstReset, secondReset, isAsync = True):

        self.TF.logger.Info(self.TF.TAG, "Issuing Consecutive Resets -> First Reset: %s Second Reset: %s Command\n"%(firstReset, secondReset))

        if self.TF.sustainedMode:
            Reset = ServiceWrap.ConsecutiveResetTask(firstReset, secondReset, isAsync)
        else:
            Reset = NVMeWrap.ConsecutiveReset(firstReset, secondReset, isAsync)

        self.TF.threadPool.PostRequestToWorkerThread(Reset)

    def PostFormat(self, SES = 0, namespaceID = 0x1, blockSize = 512, sendType = ServiceWrap.SEND_IMMEDIATE):

        self.TF.logger.Info("Posting Format Command for the NSID : %d BlockSize : %d \n"%(namespaceID, blockSize))
        try:
            if self.GetDPAResetType() == None:

                identifyNSObj = self.IdentifyNamespace(nameSpaceID = 1)
                # find matching index from data returned
                flag = True

                for selIndex in range(identifyNSObj.NLBAF + 1):
                    lbads = identifyNSObj.LBAFx[selIndex].LBADS
                    if (blockSize == pow(2, lbads)):
                        flag = False

                # format using SES 0 all namespaces LBAF = matching index
                # set Format_NVM_CDW10 to index as the index is the lowest 4 bits
                FORMATDW10 = NVMeWrap.ADMIN_FORMAT_NVM_COMMAND_DW10()
                FORMATDW10.LBAF = selIndex
                FORMATDW10.MS = 0
                FORMATDW10.PI = 0
                FORMATDW10.IPL = 0
                FORMATDW10.SES = SES

                FORMATNVMObj = NVMeWrap.FormatNVMCmd(namespaceID, FORMATDW10, sendType = sendType)
                self.TF.threadPool.WaitForThreadCompletion()
            else:
                self.ActivateControllerCmd()
                identifyNSObj = self.IdentifyNamespace(nameSpaceID = 1)
                # find matching index from data returned
                flag = True

                for selIndex in range(identifyNSObj.NLBAF + 1):
                    lbads = identifyNSObj.LBAFx[selIndex].LBADS
                    if (blockSize == pow(2, lbads)):
                        flag = False

                # format using SES 0 all namespaces LBAF = matching index
                # set Format_NVM_CDW10 to index as the index is the lowest 4 bits
                FORMATDW10 = NVMeWrap.ADMIN_FORMAT_NVM_COMMAND_DW10()
                FORMATDW10.LBAF = selIndex
                FORMATDW10.MS = 0
                FORMATDW10.PI = 0
                FORMATDW10.IPL = 0
                FORMATDW10.SES = SES

                FORMATNVMObj = NVMeWrap.FormatNVMCmd(namespaceID, FORMATDW10, sendType = sendType)
                #self.TF.threadPool.WaitForThreadCompletion()
                if(flag):
                    raise ValidationError.CVFGenericExceptions("Format Command", "Format index is not found")
        except ValidationError.CVFExceptionTypes as exc:
            raise ValidationError.CVFGenericExceptions (self.VTFContainer.GetTestName(), "Error occurred in Format"+ exc.GetFailureDescription())

    def MDBPostFormat(self, SES = 0, namespaceID = 0x1, blockSize = 512, sendType = ServiceWrap.SEND_IMMEDIATE):

        self.TF.logger.Info("Posting Format Command for the NSID : %d BlockSize : %d \n"%(namespaceID, blockSize))

        try:
            #identifyNSObj = self.IdentifyNamespace(nameSpaceID = 1)
            # find matching index from data returned
            flag = True

            for selIndex in range(self.TF.nLBAf + 1):
                lbads = self.TF.LBAFx[selIndex].LBADS
                if (blockSize == pow(2, lbads)):
                    flag = False
                    # format using SES 0 all namespaces LBAF = matching index
                    # set Format_NVM_CDW10 to index as the index is the lowest 4 bits
                    FORMATDW10 = NVMeWrap.ADMIN_FORMAT_NVM_COMMAND_DW10()
                    FORMATDW10.LBAF = selIndex
                    FORMATDW10.MS = 0
                    FORMATDW10.PI = 0
                    FORMATDW10.IPL = 0
                    FORMATDW10.SES = SES

                    FORMATNVMObj = NVMeWrap.FormatNVMCmd(namespaceID, FORMATDW10, sendType = sendType)

            if(flag):
                raise ValidationError.CVFGenericExceptions("Format Command", "Format index is not found")
        except ValidationError.CVFExceptionTypes as exc:
            raise ValidationError.CVFGenericExceptions (self.vtfContainer.GetTestName(), "Error occurred in Format"+ exc.GetFailureDescription())

    def GetFormatProgressStatus(self, namespaceID):

        try:
            identifyNSObj = NVMeWrap.IdentifyNamespace(namespaceID, sendType = ServiceWrap.SEND_IMMEDIATE)
            currentFPI = identifyNSObj.objOutputData.FPI.PercentageRemainsToBeFormatted
            return currentFPI
        except ValidationError.CVFExceptionTypes as exc:
            raise ValidationError.CVFGenericExceptions (self.vtfContainer.GetTestName(), "Error occurred in Identify Namespace"+ exc.GetFailureDescription())

    def __CallWaitForThreadCompletion(self):

        #Don't call waitforthreadcompletion in Sustained Mode.
        if self.TF.sustainedMode:
            return
        else:
            self.TF.logger.Info(self.TF.TAG, "\nInvoking WaitForThreadPoolCompletion. Total Commands pushed so far is:%d\n"%self.TF.nrOfCommands)
            status = False
            status = self.TF.threadPool.WaitForThreadCompletion()
            if False == status:
                raise ValidationError.CVFGenericExceptions("ERROR", "Error occured in Waitforthreadcompletion\n")

    def ChangeCMDMgrMode(self):

        qDepth = random.choice([-1, 0, 1, 2])
        deterministic = False

        if 2 == qDepth:
            qDepth = random.choice([32, 64, 128, 256])
            deterministic = random.choice([True, False])

        self.TF.logger.Info("OTM Call Back: Changing Command Manager Queue Depth : %d\tDeterministic : %s\t"%(qDepth, deterministic))

        try:
            self.VTFContainer.ReInitThreadPool(nvmeQueueDepth = qDepth, isDeterministic = deterministic)
        except ValidationError.CVFExceptionTypes as exc:
            raise ValidationError.CVFGenericExceptions("Error in Re-Initializing Threadpool",exc.GetFailureDescription())

        self.TF.threadPool = self.VTFContainer.cmd_mgr.GetThreadPoolMgr()

        if qDepth > 1:
            assert(qDepth == self.configParser.GetValue('nvme_queue_depth', 0)[0]), "Error. New QDepth set through ReInitThreadPool is not considered.\n"

        self.TF.logger.Info("OTM Call Back: Re-Initialized Threadpool successfullly with qDepth : %d\tDeterministic : %s\t"%(qDepth, deterministic))

    def ReInitCMDMgr(self):
        self.TF.logger.Message(self.TF.TAG, "\n Command-Manager Re-Initialization\n")
        nvmeQDepth = self.TF.configParser.GetValue('nvme_queue_depth', 0)[0]
        threadPoolDepth = random.randint(1, 50000)
        threadpoolMode = self.TF.configParser.GetValue('thread_pool_manager_mode', 0)[0]
        isAsync = self.TF.VTFContainer.systemCfg.AsyncMode
        self.TF.VTFContainer.ReInitCommandManager(nvmeQDepth, threadPoolDepth, threadpoolMode, isAsync)
        self.TF.threadPool = self.TF.VTFContainer.cmd_mgr.GetThreadPoolMgr()

    def ReturnTestStatistics(self):
        statisticDict = {}
        statisticDict["TotalGSDCount"]= self.statistics.GetTotalGSDCount()
        statisticDict["TotalUGSDCount"] = self.statistics.GetTotalUGSDCount()
        statisticDict["TotalPowerAbortsCount"] = self.statistics.GetTotalPowerAbortsCount()
        statisticDict["TotalPCIeDSPortResetCount"] = self.statistics.GetTotalPCIeDSPortResetCount()
        statisticDict["TotalPCIeFLRResetCount"] = self.statistics.GetTotalPCIeFLRResetCount()
        statisticDict["TotalPCIeHotResetCount"] = self.statistics.GetTotalPCIeHotResetCount()
        statisticDict["TotalDisableControllerCount"] = self.statistics.GetTotalDisableControllerCount()
        statisticDict["TotalShutDownControllerCount"] = self.statistics.GetTotalShutDownControllerCount()
        statisticDict["TotalNvmeSubsystemResetCount"] = self.statistics.GetTotalNvmeSubsystemResetCount()
        statisticDict["TotalWriteCmdCount"] = statsObj.GetStatisticsCount(CTFPyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_WRITE)
        statisticDict["TotalReadCmdCount"] = statsObj.GetStatisticsCount(CTFPyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_READ)
        statisticDict["CommandLatencyHistogram"] = self.statistics.GetCommandLatencyHistogram()
        statisticDict["TotalDPACount"] = self.statistics.GetTotalDPACount()
        statisticDict["TotalConfiguredSetEventCount"] = self.statistics.GetTotalConfiguredSetEventCount()
        statisticDict["TotalResponseCompleteIops"] = self.statistics.GetResponseCompleteIops()
        statisticDict["TotalSendingCompleteIops"] = self.statistics.GetSendingCompleteIops()
        statisticDict["TotalReadSizeInGB"] = self.statistics.GetTotalReadSizeInGB()
        statisticDict["TotalWriteSizeInGB"] = self.statistics.GetTotalWriteSizeInGB()
        statisticDict["TotalDeallocateCount"] = statsObj.GetStatisticsCount(CTFPyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_TRIM)
        statisticDict["TotalIdentifyControllerCount"] = statsObj.GetStatisticsCount(CTFPyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_IDENTIFY_CONTROLLER)
        statisticDict["TotalIdentifyNamespaceCount"] = statsObj.GetStatisticsCount(CTFPyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_IDENTIFY_ACTIVE_NAMESPACES)
        statisticDict["TotalSetFeaturesCount"] = statsObj.GetStatisticsCount(CTFPyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_SET_FEATURES)
        statisticDict["TotalGetFeaturesCount"] = statsObj.GetStatisticsCount(CTFPyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_GET_FEATURES)
        statisticDict["TotalResetActivateControllerCount"] = statsObj.GetStatisticsCount(CTFPyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_RESET_ACTIVATE_CONTROLLER)
        statisticDict["TotalFormatCount"] = statsObj.GetStatisticsCount(CTFPyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_FORMAT)
        statisticDict["TotalFlushCount"] = statsObj.GetStatisticsCount(CTFPyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_FLUSHCACHE)
        statisticDict["TotalWriteZeroesCount"] = statsObj.GetStatisticsCount(CTFPyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_WRITEZEROES)
        statisticDict["TotalCompareCount"] = statsObj.GetStatisticsCount(CTFPyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_COMPARE)
        statisticDict["TotalGetLogPageCount"] = statsObj.GetStatisticsCount(CTFPyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_GET_LOG_PAGE)
        statisticDict["TotalFusedCommandCount"] = statsObj.GetStatisticsCount(CTFPyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_FUSED_COMPARE_WRITE)
        statisticDict["TotalDeleteAndCreateAllQCount"] = statsObj.GetStatisticsCount(CTFPyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_DELETE_AND_CREATE_ALL_Q)
        statisticDict["TotalAERCommandCount"] = statsObj.GetStatisticsCount(CTFPyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_ASYNC_EVENT_REQ)
        statisticDict["TotalWriteUncorrectableCount"] = statsObj.GetStatisticsCount(CTFPyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_WRITEUNCORRECTABLE)
        statisticDict["TotalFirmwareActivateCommandCount"] = statsObj.GetStatisticsCount(CTFPyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_FW_ACTIVATE)
        return statisticDict

    def CreateIOQsReinitCmdMgr(self):

        #Choose a random number of IOQs to be created between 1 and numberOfCPUCores.
        nrOfQs = random.randint(1, self.TF.NumDriverMappedMSI)

        #Create nrOfQs where Queue IDs are picked Randomly.
        self.TF.availableIOQs = random.sample(list(range(1, self.TF.NumDriverMappedMSI + 1)), nrOfQs)

        self.TF.logger.Info("List of IOQs getting created is %s\n"%self.TF.availableIOQs)

        ioQSize = int(self.configParser.GetValue('automatic_io_queue_size', 0)[0])
        UrgentPriority = 2
        LowPriority = 0

        for QID in self.TF.availableIOQs:

            #Create CQ
            self.TF.logger.Info("Creating CQ with CQID : %d  CQSIZE : %d "%(QID, ioQSize))
            createCQ = NVMeWrap.CreateCQ(ioQSize, QID, QID - 1)
            createCQ.Execute()
            createCQ.HandleOverlappedExecute()
            createCQ.HandleAndParseResponse()

            SC = createCQ.objNVMeComIOEntry.completionEntry.DW3.SF.SC
            assert(TP.SC['SUCCESSFUL_COMPLETION'] == SC), "Create-CQ Command Execution Failedn"

            #Create SQ
            QPriority  = random.randint(LowPriority, UrgentPriority)
            self.TF.logger.Info("Creating SQ with SQID : %d  SQSIZE : %d Associated CQID : %d Q Priority : %d"%(QID, ioQSize, QID, QPriority))
            try:
                createSQ = NVMeWrap.CreateSQ(ioQSize, QID, QID, QPriority)
                createSQ.Execute()
                createSQ.HandleOverlappedExecute()
                createSQ.HandleAndParseResponse()
            except ValidationError.CVFExceptionTypes as ex:
                self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
                raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

            SC = createSQ.objNVMeComIOEntry.completionEntry.DW3.SF.SC
            assert(TP.SC['SUCCESSFUL_COMPLETION'] == SC), "Create-SQ Command Execution Failed."

        try:
            getDevHealth = NVMeWrap.GetDeviceHealth()
            getDevHealth.Execute()
            getDevHealth.HandleOverlappedExecute()
            getDevHealth.HandleAndParseResponse()
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in command execution. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        assert(nrOfQs == getDevHealth.objOutputdata.basicInfo.numberOfConfiguredSQs), "Not all IOCQs as requested are created\n"
        assert(nrOfQs == getDevHealth.objOutputdata.basicInfo.numberOfConfiguredCQs), "Not all IOSQs as requested are created\n\n"

        '''
        #Reinstantiate Command Manager after IOQ creation.

        nvmeQDepth = self.configParser.GetValue('nvme_queue_depth', 0)[0]
        threadPoolDepth = random.randint(1, 50000)
        threadpoolMode = self.configParser.GetValue('thread_pool_manager_mode', 0)[0]
        isAsync = self.TF.VTFContainer.systemCfg.AsyncMode

        self.TF.logger.Info("Re Initializing CMDMgr in Mode: %d\t isAsync: %s\t nvmeQDepth: %d\t threadPoolDepth: %d\t after creating IOQs.\n"%(threadpoolMode, isAsync, threadPoolDepth, nvmeQDepth))

        #self.TF.VTFContainer.ReInitCommandManager(nvmeQDepth, threadPoolDepth, threadpoolMode, isAsync)
        #self.TF.threadPool = self.TF.VTFContainer.cmd_mgr.GetThreadPoolMgr()
        '''

    def RingDoorbell(self, QID = 0, timeout = 20000, sendType = ServiceWrap.SEND_IMMEDIATE):
        self.TF.logger.Info("\n################### RINGING QID:\t%d DOORBELL ###################" % QID)
        try:
            NVMeWrap.RingDoorBell(QID, timeout, sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in posting Ring Doorbell Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed after Ringing Admin Queue Manually\n")

        self.TF.logger.Info("\n################### DOORBELL RUNG SUCCESFULLY ###################")

    def SetSQRingDoorBellMode(self, ringDoorBellMode = NVMeWrap.eRingDoorbellMode.AUTOMATIC_RING_DOORBELL_MODE, QID = 0, sendType = ServiceWrap.SEND_IMMEDIATE):
        try:
            NVMeWrap.SetSQRingDoorBellMode(ringDoorBellMode = ringDoorBellMode, sendType = sendType, QID = QID)
            self.TF.logger.Info("Set SQ Ring Door Bell Mode:  %s"%(QID))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in when attempted to configure Admin Queue Doorbell to Manual Mode.\n")

    def GetSQRingDoorBellMode(self, QID = 0, sendType = ServiceWrap.SEND_IMMEDIATE):
        try:
            doorbellMode = NVMeWrap.GetSQRingDoorBellMode(sendType = sendType, QID = QID)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in when attempted to configure Admin Queue Doorbell to Manual Mode.\n")
        return doorbellMode.ringDoorBellMode

    def GetDoorbellAddress(self, QID = 0, TimeDelay = 20000, sendType = ServiceWrap.SEND_IMMEDIATE):
        try:
            rdbInfo = NVMeWrap.RingDoorBellAddress(QID, TimeDelay, sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            raise ValidationError.CVFGenericExceptions("", "Failed in fetching Command Offsets/Values\n")

        self.TF.logger.Info("doorBellOffset = %s"%rdbInfo.doorBellOffset)
        self.TF.logger.Info("doorBellValue = %s"%rdbInfo.doorBellValue)
        self.TF.logger.Info("ringDoorbellMode = %s"%rdbInfo.ringDoorbellMode)

        deviceSlotObj = self.TF.testSession.GetDeviceSlotObject()
        PCIHeader = deviceSlotObj.ReadPCIHeader()
        self.TF.logger.Info("PCIHeader.BAR0.bar0Address = %s"%hex(PCIHeader.BAR0.bar0Address))

        address = int(PCIHeader.BAR0.bar0Address) + int(rdbInfo.doorBellOffset)
        self.TF.logger.Info("%s"%hex(address))

        return [rdbInfo.doorBellOffset, rdbInfo.doorBellValue, rdbInfo.ringDoorbellMode]

    def get_door_bell_mode(self, qid=0):
        dbMode = NVMeWrap.GetSQRingDoorBellMode(sendType = ServiceWrap.SEND_IMMEDIATE, QID=qid)
        if dbMode.ringDoorBellMode == NVMeWrap.eRingDoorbellMode.RING_DOORBELL_MODE_MIN:
            mode = 'AUTO'
        else:
            mode = 'MANUAL'
        return mode

    def ConfigureFWEvent(self, sendType = ServiceWrap.SEND_IMMEDIATE):
        try:
            # Calling Configure FW Event for Xplorer Cmd
            xPlorerCMDWrap.ConfigureFWEvent(sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Configure FW Event in xPlorer CMD. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed to Configure FW Event in xPlorer CMD\n")

    def SetActionConfiguredOnExternalBoard(self, CommandType = ServiceWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_RING_DOOR_BELL):
        try:
            # Configuring action On External board
            self.HWUtils.SetActionConfiguredOnExternalBoard(CommandType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in Set Action Configured On External Board. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Set Action Configured On External Board\n")

    def CmdDelay(self, miliSleep = 6000, nanoSleep = 1, isAsync = False):
        try:
            NVMeWrap.CmdDelay(miliSleep, nanoSleep, isAsync, sendType=ServiceWrap.SEND_IMMEDIATE)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in Cmd Delay. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Cmd Delay\n")


    def GPIOShmooConfigActionPolling(self, Address, Data, sendType = ServiceWrap.SEND_IMMEDIATE_ASYNC):
        try:
            # This API is called for to Config Shmoo command
            GPIOShmooWrap.GPIOShmooConfigActionPolling(Address, Data, sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in GPIO Shmoo Config Action Polling. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in GPIO Shmoo Config Action Polling Command\n")

    def SetNVMeConfigRegisterAndValue(self, Address, Data, sendType = ServiceWrap.SEND_IMMEDIATE_ASYNC):
        try:
            # This is called for to Config Action command
            NVMeWrap.SetNVMeConfigReg.SetNVMeConfigRegisterAndValue(Address, Data, sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in Set NVMe Config Register And Value. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Set NVMe Config Register And Value Command\n")

    def GPIOShmooDeConfigActionPolling(self, sendType = ServiceWrap.SEND_IMMEDIATE_ASYNC):
        try:
            # This API is called for to Config Shmoo command
            GPIOShmooWrap.GPIOShmooDeConfigActionPolling(sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in GPIO Shmoo De Config Action Polling. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in GPIO Shmoo De Config Action Polling\n")

    def PostVendorAdminCmd(self, OPCode = 0xFA, testbuffer = None, DWord10=127, DWord11=0, DWord12=0, DWord13=0, enDirection = NVMeWrap.DIRECTION_DEVICE_TO_HOST, sendType = ServiceWrap.SEND_IMMEDIATE):

        try:
            NVMeWrap.VendorAdminCmd(ucOPCode= OPCode, buffer = testbuffer, ulDWord10= DWord10, ulDWord11=DWord11, ulDWord12=DWord12, ulDWord13=DWord13, ulDWord14=0, ulDWord15=0, enDirection = enDirection, sendType = sendType)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Error occurred in VendorAdminCmd.\n")

    def GetNVMeCCRegisterAddressAndData(self):
        address, value = NVMeWrap.GetNVMeCCRegisterAddressAndData()
        self.TF.logger.Info("CTRL Reset adress = %s"%address)
        self.TF.logger.Info("value = %s"%value)

        return address, value

    def GetNVMeNSSRRegisterAddressAndData(self):
        address, value = NVMeWrap.GetNVMeNSSRRegisterAddressAndData()
        self.TF.logger.Info("NSSR Reset adress = %s"%address)
        self.TF.logger.Info("value = %s"%value)

        return address, value

    def GetPCIFLRRegisterAddressAndData(self):
        address, value = NVMeWrap.GetPCIFLRRegisterAddressAndData()
        self.TF.logger.Info("PCIe_FLR adress = %s"%address)
        self.TF.logger.Info("value = %s"%value)

        return address, value

    def GetPCIBridgeControlRegisterAddressAndData(self):
        address, value = NVMeWrap.GetPCIBridgeControlRegisterAddressAndData()
        self.TF.logger.Info("PCIe_HOT_RESET adress = %s"%address)
        self.TF.logger.Info("value = %s"%value)

        return address, value

    def GetPCILinkControlRegisterAddressAndData(self):
        address, value = NVMeWrap.GetPCILinkControlRegisterAddressAndData()
        self.TF.logger.Info("PCIe_LINK_DIS adress = %s"%address)
        self.TF.logger.Info("value = %s"%value)

        return address, value

    def SetDPAResetType(self, DPAResetType):
        self.DPAResetType = DPAResetType

    def GetDPAResetType(self):
        return self.DPAResetType

    def ActivateControllerCmd(self ):
        """ResetType     = disablectrl
                         = deleteq
                         = shutdown
                         = NSSR
            """
        if ('disablectrl' == self.GetDPAResetType()):
            self.TF.logger.Info("********   Posting DISABLE CONTROLLER  ********  ")
            activateController = self.ActivateController(disableController = True, shutdown = False, deleteQueues = False, NVMeSubsytemReset = False, sendType = ServiceWrap.CMD_SEND_TYPE.SEND_QUEUED)
        elif ('deleteq' == self.GetDPAResetType()):
            self.TF.logger.Info("********  Posting DELETE QUEUES  ********  ")
            activateController = self.ActivateController(disableController = False, shutdown = False, deleteQueues = True, NVMeSubsytemReset = False, sendType = ServiceWrap.CMD_SEND_TYPE.SEND_QUEUED)
        elif ('shutdown' == self.GetDPAResetType()):
            self.TF.logger.Info("********  Posting SHUTDOWN   ********  ")
            activateController = self.ActivateController(disableController = False, shutdown = True, deleteQueues = False, NVMeSubsytemReset = False, sendType = ServiceWrap.CMD_SEND_TYPE.SEND_QUEUED)
        elif ('NSSR' == self.GetDPAResetType()):
            self.TF.logger.Info("******** Posting  NVMe Sub System Reset   ******** ")
            activateController = self.ActivateController(disableController = False, shutdown = False, deleteQueues = False, NVMeSubsytemReset = True, sendType = ServiceWrap.CMD_SEND_TYPE.SEND_QUEUED)
        self.SetDPAResetType(None)
        self.TF.logger.Info("******** Controller - %s Command Completed  ******** \n\n"%self.GetDPAResetType())

    def GetSMART(self):

        try:
            #For HGST NSID shall be 0x01 but for Phoenix/Hermes it shall be 0x00.
            if 'sandisk' in self.TF.modelNum.lower():
                smartHealthInfo = self.PostLogPage(LID = NVMeWrap.EN_SMART_HEALTH_INFORMATION, NSID = 0x00, sendType = ServiceWrap.SEND_IMMEDIATE)
            else:
                smartHealthInfo = self.PostLogPage(LID = NVMeWrap.EN_SMART_HEALTH_INFORMATION, NSID = 0x01, sendType = ServiceWrap.SEND_IMMEDIATE)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in Tear Down. Error Message ->\n %s "%ex.GetFailureDescription())

        self.TF.logger.Info("\n\n******** WRITE/READ STATISTICS FROM SMART ********\n\n")
        self.TF.logger.Message("%-35s: %s"%('HostReadCommands_Low: ', smartHealthInfo.HostReadCommands_Low))
        self.TF.logger.Message("%-35s: %s"%('HostReadCommands_High: ', smartHealthInfo.HostReadCommands_High))
        self.TF.logger.Message("%-35s: %s"%('HostWriteCommands_Low: ', smartHealthInfo.HostWriteCommands_Low))
        self.TF.logger.Message("%-35s: %s"%('HostWriteCommands_High: ', smartHealthInfo.HostWriteCommands_High))

        return(smartHealthInfo.HostReadCommands_High, smartHealthInfo.HostReadCommands_Low, smartHealthInfo.HostWriteCommands_High, smartHealthInfo.HostWriteCommands_Low)

    def DumpCancelledCmdStats(self, original, latest, testSendWriteCommands):

        self.TF.logger.Message("%-35s: %s"%('Cancelled HostWriteCommands_Low: ', testSendWriteCommands - (latest[3] - original[3])))
        self.TF.logger.Message("%-35s: %s"%('Cancelled HostWriteCommands_High: ', testSendWriteCommands - (latest[2] - original[2])))

###--------------------------------SD-Command ------------------------------------------------------------------------- ###
### SD-Command--------------------------------------------------------------------------------------------------------- ###


    def SD_ExtnRegSingleWrite(self, fno = 2, EnblDis_Cache = 1, EnblDis_CQ = 1, Sel_CQMODE = 0):

        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        import SDCommandWrapper as SDwrap
        self.TF.logger.Message("---------------------------------------------------------------------------------------------------------------------\n")
        Extregs = SDwrap.EXT_REGISTER_SET_FOR_PERFORMANCE_ENHENCEMENT_FUNCTION()
        Extregs.ui8CacheEnable = EnblDis_Cache
        Extregs.ui8EnableCQ = EnblDis_CQ
        Extregs.ui8CQMode = Sel_CQMODE  #Vaoluntary mode:1, Sequential:1
        UpdateReg = SDwrap.U()
        UpdateReg.perfEncmntFunc = Extregs
        ExtReg = SDwrap.EXTENSION_REGISTERS()
        ExtReg.u = UpdateReg
        self.TF.logger.Message("CMD49_ExtensionRegisterSingleWriteCmd---------------------------------------------------------------------------------\n")
        LenORMask = 511
        Add = 0
        MW = False
        FNO = fno
        MIO = False
        try:
            CMD49_ExtensionRegisterSingleWriteCmd = SDwrap.ExtensionRegisterSingleWriteCmd(uiLenORMask = LenORMask, uiAddress = Add, bMW = MW, uiFNO = FNO, bMIO = MIO, extRegister = ExtReg)
            self.TF.logger.Message("%-35s: %s"%('CMD49_ExtensionRegisterSingleWriteCmd Args: ', CMD49_ExtensionRegisterSingleWriteCmd.pyCmdObject.commandData.ui32Args))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")


    def SD_ExtnRegSingleRead(self, fno = 2):

        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        import SDCommandWrapper as SDwrap
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        self.TF.logger.Message("CMD48_ExtensionRegisterSingleReadCmd ---------------------------------------------------------------------------------\n")
        Len = 511
        Add = 0
        FNO = fno
        MIO = False
        try:
            CMD48_ExtensionRegisterSingleReadCmd = SDwrap.ExtensionRegisterSingleReadCmd(uiLen=Len, uiAddress=Add, uiFNO=FNO, bMIO=MIO)
            self.TF.logger.Message("%-35s: %s"%('CMD48_ExtensionRegisterSingleReadCmd Args: ', CMD48_ExtensionRegisterSingleReadCmd.pyCmdObject.commandData.ui32Args))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("%-35s: %s"%('Card-Status', CMD48_ExtensionRegisterSingleReadCmd.pyResponseData.r1Response.uiCardStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Status: ', CMD48_ExtensionRegisterSingleReadCmd.pyResponseData.r1Response.eStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Resp1: ', CMD48_ExtensionRegisterSingleReadCmd.pyResponseData.r1Response.sdR1RespData))
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        self.TF.logger.Message("%-35s: %s"%('PerfEnhencementFunctionRev: ', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui8PerfEnhencementFunctionRev))
        self.TF.logger.Message("%-35s: %s"%('FX_EVENTSupport', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui8FX_EVENTSupport))
        self.TF.logger.Message("%-35s: %s"%('CardInitiatedMntnceSupport', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui8CardInitiatedMntnceSupport))
        self.TF.logger.Message("%-35s: %s"%('HostInitiatedMntnceSupport', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui8HostInitiatedMntnceSupport))
        self.TF.logger.Message("%-35s: %s"%('CardMaintenanceUrgency', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui8CardMaintenanceUrgency))
        self.TF.logger.Message("%-35s: %s"%('CacheSupport', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui8CacheSupport))
        self.TF.logger.Message("%-35s: %s"%('CQSupportAndDepth', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui8CQSupportAndDepth))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_0', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_0))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_1', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_1))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_2', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_2))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_3', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_3))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_4', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_4))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_5', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_5))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_6', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_6))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_7', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_7))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_8', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_8))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_9', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_9))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_10', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_10))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_11', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_11))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_12', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_12))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_13', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_13))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_14', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_14))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_15', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_15))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_16', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_16))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_17', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_17))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_18', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_18))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_19', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_19))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_20', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_20))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_21', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_21))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_22', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_22))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_23', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_23))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_24', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_24))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_25', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_25))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_26', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_26))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_27', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_27))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_28', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_28))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_29', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_29))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_30', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_30))
        self.TF.logger.Message("%-35s: %s"%('ErrorStatusTaskID_31', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_31))
        self.TF.logger.Message("%-35s: %s"%('FXEventEnable', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui8FXEventEnable))
        self.TF.logger.Message("%-35s: %s"%('CardInitiatedMntnceEnable', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui8CardInitiatedMntnceEnable))
        self.TF.logger.Message("%-35s: %s"%('HostInitiatedMntnceEnable', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui8HostInitiatedMntnceEnable))
        self.TF.logger.Message("%-35s: %s"%('StartHostInitiatedMntnce', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui8StartHostInitiatedMntnce))
        self.TF.logger.Message("%-35s: %s"%('CacheEnable', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui8CacheEnable))
        self.TF.logger.Message("%-35s: %s"%('CacheEnable', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui8FlushCache))
        self.TF.logger.Message("%-35s: %s"%('EnableCQ', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui8EnableCQ))
        self.TF.logger.Message("%-35s: %s"%('CQMode: ', CMD48_ExtensionRegisterSingleReadCmd.extRegisters.u.perfEncmntFunc.ui8CQMode))
        return CMD48_ExtensionRegisterSingleReadCmd


    def SD_TASKStatus(self):

        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        import SDCommandWrapper as SDwrap
        self.TF.logger.Message("CMD13_SendStatus -----------------------------------------------------------------------------------------------------\n")
        RCA = 0xD555
        try:
            CMD13_SendStatus =  SDwrap.SendStatus(uiRCA=RCA, bSendTaskStatus = True)
            self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', CMD13_SendStatus.pyCmdObject.commandData.ui32Args))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("%-35s: %s"%('Card-Status', CMD13_SendStatus.pyResponseData.r1Response.uiCardStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Status: ', CMD13_SendStatus.pyResponseData.r1Response.eStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Resp1: ', CMD13_SendStatus.pyResponseData.r1Response.sdR1RespData))
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        return CMD13_SendStatus

    def SD_AddExtn(self, extendedAdd):

        import SDCommandWrapper as SDwrap
        self.TF.logger.Message("CMD22_AddressExtension -----------------------------------------------------------------------------------------------\n")
        ExtendedAddress = extendedAdd
        self.TF.logger.Message("%-35s: %s"%('ExtendedAddress is : ', ExtendedAddress))
        try:
            CMD22_AddressExtension =  SDwrap.AddressExtension(uiExtendedAddress = ExtendedAddress)
            self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', CMD22_AddressExtension.pyCmdObject.commandData.ui32Args))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("%-35s: %s"%('Card-Status', CMD22_AddressExtension.pyResponseData.r1Response.uiCardStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Status: ', CMD22_AddressExtension.pyResponseData.r1Response.eStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Resp1: ', CMD22_AddressExtension.pyResponseData.r1Response.sdR1RespData))
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        return CMD22_AddressExtension


    def SD_ReadSingleBLK(self, StartLBA, No_Data = True,  LogDump_Dis = True, PostErase = False ):

        import SDCommandWrapper as SDwrap
        sLba = StartLBA
        NoData = No_Data
        Pattern = 0xFFFFFFFE
        blockLen = 512
        RDBuff = None
        self.TF.logger.Message("CMD17_ReadSingleBlock-------------------------------------------------------------------------------------------------\n")
        self.TF.logger.Message("%-35s: %s"%('Start LBA is: ', sLba))
        self.TF.logger.Message("%-35s: %s"%('NoDataMode is: ', NoData))
        if(NoData==False):
            self.TF.logger.Message("Read-Data-Buffer -------------------------------------------------------------------------------------------------\n")
            BuffLen = (blockLen)
            if(PostErase == True):
                RDBuff =  ServiceWrap.Buffer.CreateBuffer(BuffLen, patternType = ServiceWrap.ALL_1, isSector = False)
            else:
                RDBuff =  ServiceWrap.Buffer.CreateBuffer(BuffLen, patternType = ServiceWrap.ALL_0, isSector = False)
            if(LogDump_Dis):
                self.TF.logger.Message("--------------------------------------------------------------------------------------------------------------\n")
                #RDBuff.PrintToLog()
                self.TF.logger.Message("--------------------------------------------------------------------------------------------------------------\n")
            self.TF.logger.Message("------------------------------------------------------------------------------------------------------------------\n")
        try:
            CMD17_ReadSingleBlock = SDwrap.ReadSingleBlock(startLba=sLba, bNoData=NoData, szBuffer=RDBuff, uiPattern=Pattern, blockLength=blockLen)
            self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', CMD17_ReadSingleBlock.pyCmdObject.commandData.ui32Args))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("%-35s: %s"%('Card-Status: ', CMD17_ReadSingleBlock.pyResponseData.r1Response.uiCardStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Status: ', CMD17_ReadSingleBlock.pyResponseData.r1Response.eStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Resp1: ', CMD17_ReadSingleBlock.pyResponseData.r1Response.sdR1RespData))
        self.TF.logger.Message("%-35s: %s"%('DT-ver:', CMD17_ReadSingleBlock.GetVersionDTInfo()))
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        if((NoData==False) and (LogDump_Dis==True)):
            RDBuff.PrintToLog()
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        return RDBuff

    def SD_ReadMulBLKST(self, StartLBA = 0, blockCount =2, No_Data = True, StopBlk_Cont=2, LogDump_Dis = False):

        import SDCommandWrapper as SDwrap
        self.Ext_Parms = SDwrap.EXTRA_COMMAND_PARAMETERS()
        self.Ext_Parms.enInfoType=SDwrap.EXTRA_INFO_TYPE.STOP_TRANSMISSION_INFO
        self.Ext_Parms.uiStopTransMissionAfterTransferLength = StopBlk_Cont
        self.Ext_Parms.bEnableDataTransferWithotModelReadyAfterSTLength = False
        sLba =StartLBA
        NoData = No_Data
        Pattern = 0xFFFFFFFE
        blockLen = 512
        RDBuff = None
        blockCNT = blockCount
        self.TF.logger.Message("CMD18_ReadMultipleBlocks ----------------------------------------------------------------------------------------------\n")
        self.TF.logger.Message("%-35s: %s"%('Start LBA is: ', sLba))
        self.TF.logger.Message("%-35s: %s"%('blockCount is: ', blockCount))
        self.TF.logger.Message("%-35s: %s"%('NoDataMode is: ', NoData))
        if(NoData==False):
            self.TF.logger.Message("Read-Multi-Data-Buffer -------------------------------------------------------------------------------\n")
            BuffLen = (blockCNT * 512)
            RDBuff =  ServiceWrap.Buffer.CreateBuffer(BuffLen, patternType = ServiceWrap.ALL_0, isSector = False)
            if(LogDump_Dis):
                RDBuff.PrintToLog()
            #self.TF.logger.Message("------------------------------------------------------------------------------------------------------\n")
        try:
            CMD18_ReadMultipleBlocks = SDwrap.ReadMultipleBlocks(startLba=sLba, blockCount=blockCNT, bNoData=NoData, szBuffer= RDBuff, bStopTransmission=True, extraInfo= self.Ext_Parms, uiPattern=Pattern, blockLength=blockLen)
            self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', CMD18_ReadMultipleBlocks.pyCmdObject.commandData.ui32Args))
            self.TF.logger.Message("%-35s: %s"%('CmdExecutionTimeInNanoSec: ', CMD18_ReadMultipleBlocks.pyDwTimeTakenForCmdexecutionInNanoSec))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("%-35s: %s"%('Card-Status', CMD18_ReadMultipleBlocks.pyResponseData.r1Response.uiCardStatus))
        self.TF.logger.Message("%-35s: %s"%('eStatus : ', CMD18_ReadMultipleBlocks.pyResponseData.r1Response.eStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Resp1: ', CMD18_ReadMultipleBlocks.pyResponseData.r1Response.sdR1RespData))
        return RDBuff


    def SD_ReadMulBLK(self, StartLBA = 0, blockCount =2, No_Data = True, LogDump_Dis = False, PostErase = False):

        import SDCommandWrapper as SDwrap
        self.TF.logger.Message("------------------------------------------------------------------------------------------------------------------\n")
        sLba = StartLBA
        NoData = No_Data
        Pattern = 0xFFFFFFFE
        blockLen = 512
        RDBuff = None
        blockCNT = blockCount
        self.TF.logger.Message("CMD18_ReadMultipleBlocks ----------------------------------------------------------------------------------------------\n")
        self.TF.logger.Message("%-35s: %s"%('Start LBA is: ', sLba))
        self.TF.logger.Message("%-35s: %s"%('blockCount is: ', blockCount))
        self.TF.logger.Message("%-35s: %s"%('NoDataMode is: ', NoData))
        if(NoData==False):
            self.TF.logger.Message("Read-Data-Buffer -------------------------------------------------------------------------------------------------\n")
            BuffLen = (blockLen*blockCNT)
            if(PostErase == True):
                RDBuff =  ServiceWrap.Buffer.CreateBuffer(BuffLen, patternType = ServiceWrap.ALL_1, isSector = False)
            else:
                RDBuff =  ServiceWrap.Buffer.CreateBuffer(BuffLen, patternType = ServiceWrap.ALL_0, isSector = False)
            if(LogDump_Dis):
                RDBuff.PrintToLog()
            self.TF.logger.Message("------------------------------------------------------------------------------------------------------------------\n")
        try:
            CMD18_ReadMultipleBlocks = SDwrap.ReadMultipleBlocks(startLba=sLba, blockCount=blockCNT, bNoData=NoData, szBuffer= RDBuff, bStopTransmission=True, uiPattern=Pattern, blockLength=blockLen)
            self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', CMD18_ReadMultipleBlocks.pyCmdObject.commandData.ui32Args))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("%-35s: %s"%('Card-Status: ', CMD18_ReadMultipleBlocks.pyResponseData.r1Response.uiCardStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Status: ', CMD18_ReadMultipleBlocks.pyResponseData.r1Response.eStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Resp1: ', CMD18_ReadMultipleBlocks.pyResponseData.r1Response.sdR1RespData))
        self.TF.logger.Message("%-35s: %s"%('DT-ver:', CMD18_ReadMultipleBlocks.GetVersionDTInfo()))
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        return RDBuff


    def SD_WriteSingleBLK(self, StartLBA = 0, No_Data = True, Pattern_Seed = 0x00, LogDump_Dis = False):

        import SDCommandWrapper as SDwrap
        sLba = StartLBA
        NoData = No_Data
        Pattern = 0xFFFFFFFE
        blockLen = 512
        WRBuff = None
        self.TF.logger.Message("CMD24_WriteSingleBlock------------------------------------------------------------------------------------------------\n")
        self.TF.logger.Message("%-35s: %s"%('Start LBA is: ', sLba))
        self.TF.logger.Message("%-35s: %s"%('NoData Mode is: ', NoData))
        if(NoData==False):
            self.TF.logger.Message("Write-Data-Buffer ------------------------------------------------------------------------------------------------\n")
            BuffLen = (blockLen)
            WRBuff =  ServiceWrap.Buffer.CreateBuffer(512, patternType = ServiceWrap.ALL_0, isSector = False)
            #pattern = random.randint(1, 0xAA)
            self.TF.logger.Message("%-35s: %s"%('pattern is: ', hex(Pattern_Seed)))
            WRBuff.Fill(Pattern_Seed)
            if(LogDump_Dis):
                WRBuff.PrintToLog()
            #self.TF.logger.Message("------------------------------------------------------------------------------------------------------------------\n")
        try:
            CMD24_WriteSingleBlock = SDwrap.WriteSingleBlock(startLba=sLba,  bNoData=NoData, szBuffer=WRBuff, uiPattern=Pattern, blockLength=blockLen)
            self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', CMD24_WriteSingleBlock.pyCmdObject.commandData.ui32Args))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("%-35s: %s"%('Card-Status: ', CMD24_WriteSingleBlock.pyResponseData.r1Response.uiCardStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Status: ', CMD24_WriteSingleBlock.pyResponseData.r1Response.eStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Resp1: ', CMD24_WriteSingleBlock.pyResponseData.r1Response.sdR1RespData))
        self.TF.logger.Message("%-35s: %s"%('DT-ver:', CMD24_WriteSingleBlock.GetVersionDTInfo()))
        #self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        return WRBuff


    def SD_WriteMulBLKST(self, StartLBA =0 , blockCount=2, No_Data = True, Pattern_Seed = 0x00, StopBlk_Cont=2, LogDump_Dis = False):

        import SDCommandWrapper as SDwrap
        import SDCommandWrapper as SDwrap
        self.Ext_Parms = SDwrap.EXTRA_COMMAND_PARAMETERS()
        self.Ext_Parms.enInfoType=SDwrap.EXTRA_INFO_TYPE.STOP_TRANSMISSION_INFO
        self.Ext_Parms.uiStopTransMissionAfterTransferLength = StopBlk_Cont
        self.Ext_Parms.bEnableDataTransferWithotModelReadyAfterSTLength = False
        sLba =StartLBA

        sLba = StartLBA
        NoData = No_Data
        Pattern = 0xFFFFFFFE
        blockLen = 512
        blockCNT = blockCount
        WRBuff = None
        self.TF.logger.Message("CMD25_WriteMultipleBlocks---------------------------------------------------------------------------------------------\n")
        self.TF.logger.Message("%-35s: %s"%('Start LBA is: ', sLba))
        self.TF.logger.Message("%-35s: %s"%('blockCNT is: ', blockCNT))
        if(NoData==False):
            self.TF.logger.Message("WriteMulti-Data-Buffer -------------------------------------------------------------------------------------------\n")
            BuffLen = (blockCNT * 512)
            WRBuff =  ServiceWrap.Buffer.CreateBuffer(BuffLen, patternType = ServiceWrap.ALL_0, isSector = False)
            #pattern = random.randint(1, 0xAA)
            WRBuff.Fill(Pattern_Seed)
            if(LogDump_Dis):
                WRBuff.PrintToLog()
        self.TF.logger.Message("------------------------------------------------------------------------------------------------------------------\n")
        try:
            CMD25_WriteMultipleBlocks = SDwrap.WriteMultipleBlocks(startLba=sLba, blockCount=blockCNT, bNoData=NoData, szBuffer=WRBuff, bStopTransmission=True, extraInfo= self.Ext_Parms, uiPattern=Pattern, blockLength=blockLen)
            self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', CMD25_WriteMultipleBlocks.pyCmdObject.commandData.ui32Args))
            self.TF.logger.Message("%-35s: %s"%('CmdExecutionTimeInNanoSec: ', CMD25_WriteMultipleBlocks.pyDwTimeTakenForCmdexecutionInNanoSec))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("%-35s: %s"%('Card-Status', CMD25_WriteMultipleBlocks.pyResponseData.r1Response.uiCardStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Status: ', CMD25_WriteMultipleBlocks.pyResponseData.r1Response.eStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Resp1: ', CMD25_WriteMultipleBlocks.pyResponseData.r1Response.sdR1RespData))
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        return WRBuff


    def SD_WriteMulBLK(self, StartLBA =0 , blockCount=2, No_Data = True, Pattern_Seed = 0x00, LogDump_Dis = False):

        import SDCommandWrapper as SDwrap
        sLba = StartLBA
        NoData = No_Data
        Pattern = 0xFFFFFFFE
        blockLen = 512
        blockCNT = blockCount
        WRBuff = None
        self.TF.logger.Message("CMD25_WriteMultipleBlocks---------------------------------------------------------------------------------------------\n")
        self.TF.logger.Message("%-35s: %s"%('Start LBA is: ', sLba))
        self.TF.logger.Message("%-35s: %s"%('blockCNT is: ', blockCNT))
        if(NoData==False):
            self.TF.logger.Message("WriteMulti-Data-Buffer -------------------------------------------------------------------------------------------\n")
            BuffLen = (blockCNT * 512)
            WRBuff =  ServiceWrap.Buffer.CreateBuffer(BuffLen, patternType = ServiceWrap.ALL_0, isSector = False)
            #pattern = random.randint(1, 0xAA)
            WRBuff.Fill(Pattern_Seed)
            if(LogDump_Dis):
                WRBuff.PrintToLog()
            self.TF.logger.Message("------------------------------------------------------------------------------------------------------------------\n")
        try:
            CMD25_WriteMultipleBlocks = SDwrap.WriteMultipleBlocks(startLba=sLba, blockCount=blockCNT, bNoData=NoData, szBuffer=WRBuff, bStopTransmission=True, uiPattern=Pattern, blockLength=blockLen)
            self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', CMD25_WriteMultipleBlocks.pyCmdObject.commandData.ui32Args))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("%-35s: %s"%('Card-Status', CMD25_WriteMultipleBlocks.pyResponseData.r1Response.uiCardStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Status: ', CMD25_WriteMultipleBlocks.pyResponseData.r1Response.eStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Resp1: ', CMD25_WriteMultipleBlocks.pyResponseData.r1Response.sdR1RespData))
        self.TF.logger.Message("%-35s: %s"%('DT-ver:', CMD25_WriteMultipleBlocks.GetVersionDTInfo()))
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        return WRBuff


    def SD_SelectDeselectCard(self, RCA = 0xD555):

        import SDCommandWrapper as SDwrap
        self.TF.logger.Message("%-35s: %s"%('RCA: Received from device: ', RCA))
        try:
            CMD7_SelectDeselectCard = SDwrap.SelectDeselectCard(uiRCA=RCA)
            self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', CMD7_SelectDeselectCard.pyCmdObject.commandData.ui32Args))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("%-35s: %s"%('Card-Status', CMD7_SelectDeselectCard.pyResponseData.r1Response.uiCardStatus))
        return CMD7_SelectDeselectCard


    def SD_GETSDMemoryCap(self):

        import SDCommandWrapper as SDwrap
        self.TF.logger.Info("\n\n*************************Memory Capacity***********************************************************************\n\n")
        csd=SDwrap.WrapGetCsd()
        c_Size = csd.CsdRegisterFieldStructVer1.uiC_Size
        cSizeMult = csd.CsdRegisterFieldStructVer1.uiCSizeMult
        MULT = (math.pow(2, (cSizeMult+2)))
        self.MULT = MULT
        BLOCKNR = ((c_Size + 1) * MULT)
        BLOCK_LEN = math.pow(2,csd.CsdRegisterFieldStructVer1.uiReadBlLen)
        self.BLOCK_LEN = BLOCK_LEN
        MemCap = int (BLOCKNR * BLOCK_LEN)
        self.TF.logger.Message("%-35s: %s"%('MemCap: ', MemCap))
        self.TF.logger.Info("\n\n**************************************************************************************************************\n\n")
        self.MemCap = MemCap
        return MemCap

    def SD_GETCID(self):

        try:
            import SDCommandWrapper as SDwrap
            self.TF.logger.Info("\n\n*************************CID Register ***********************************************************************\n\n")
            cid=SDwrap.WrapGetCid()
            self.TF.logger.Message("%-35s: %s"%('MID: ', cid.cidRegisterFieldStruct.uiMid))
            self.TF.logger.Message("%-35s: %s"%('OID: ', cid.cidRegisterFieldStruct.uiOid))
            self.TF.logger.Message("%-35s: %s"%('P-Name: ', cid.cidRegisterFieldStruct.uiPnm))
            self.TF.logger.Message("%-35s: %s"%('P-Version: ', cid.cidRegisterFieldStruct.uiPrv))
            self.TF.logger.Message("%-35s: %s"%('P-Serial No: ', cid.cidRegisterFieldStruct.uiPsn))
            self.TF.logger.Message("%-35s: %s"%('Reserved: ', cid.cidRegisterFieldStruct.Reserved))
            self.TF.logger.Info("\n\n*************************************************************************************************************\n\n")
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def SD_GETCSD(self):

        try:
            import SDCommandWrapper as SDwrap
            self.TF.logger.Info("\n\n*************************CDS Register ***********************************************************************\n\n")
            csd=SDwrap.WrapGetCsd()
            self.TF.logger.Message("%-35s: %s"%('FileFormaT: ', csd.CsdRegisterFieldStructVer1.uiFileFormaT))
            self.TF.logger.Message("%-35s: %s"%('TmpWriteProtect: ', csd.CsdRegisterFieldStructVer1.uiTmpWriteProtect))
            self.TF.logger.Message("%-35s: %s"%('Perm_Write_Protect: ', csd.CsdRegisterFieldStructVer1.uiPerm_Write_Protect))
            self.TF.logger.Message("%-35s: %s"%('Copy: ', csd.CsdRegisterFieldStructVer1.uiCopy))
            self.TF.logger.Message("%-35s: %s"%('FileFormatGrp: ', csd.CsdRegisterFieldStructVer1.uiFileFormatGrp))
            self.TF.logger.Message("%-35s: %s"%('WritEBlPartial: ', csd.CsdRegisterFieldStructVer1.uiWritEBlPartial))
            self.TF.logger.Message("%-35s: %s"%('WriteBlLen: ', csd.CsdRegisterFieldStructVer1.uiWriteBlLen))
            self.TF.logger.Message("%-35s: %s"%('R2WFactor: ', csd.CsdRegisterFieldStructVer1.uiR2WFactor))
            self.TF.logger.Message("%-35s: %s"%('WpGrpEnable: ', csd.CsdRegisterFieldStructVer1.uiWpGrpEnable))
            self.TF.logger.Message("%-35s: %s"%('WpGrpSize: ', csd.CsdRegisterFieldStructVer1.uiWpGrpSize))
            self.TF.logger.Message("%-35s: %s"%('SectorSize: ', csd.CsdRegisterFieldStructVer1.uiSectorSize))
            self.TF.logger.Message("%-35s: %s"%('EraseBlkEn: ', csd.CsdRegisterFieldStructVer1.uiEraseBlkEn))
            self.TF.logger.Message("%-35s: %s"%('CSizeMult: ', csd.CsdRegisterFieldStructVer1.uiCSizeMult))
            self.TF.logger.Message("%-35s: %s"%('VddWCurrMax: ', csd.CsdRegisterFieldStructVer1.uiVddWCurrMax))
            self.TF.logger.Message("%-35s: %s"%('VddWCurrMin: ', csd.CsdRegisterFieldStructVer1.uiVddWCurrMin))
            self.TF.logger.Message("%-35s: %s"%('VddRCurrMax: ', csd.CsdRegisterFieldStructVer1.uiVddRCurrMax))
            self.TF.logger.Message("%-35s: %s"%('VddRCurrMin: ', csd.CsdRegisterFieldStructVer1.uiVddRCurrMin))
            self.TF.logger.Message("%-35s: %s"%('C_Size: ', csd.CsdRegisterFieldStructVer1.uiC_Size))
            self.TF.logger.Message("%-35s: %s"%('DsrImp: ', csd.CsdRegisterFieldStructVer1.uiDsrImp))
            self.TF.logger.Message("%-35s: %s"%('ReadBlkMisalign: ', csd.CsdRegisterFieldStructVer1.uiReadBlkMisalign))
            self.TF.logger.Message("%-35s: %s"%('WriteBlkMisalign: ', csd.CsdRegisterFieldStructVer1.uiWriteBlkMisalign))
            self.TF.logger.Message("%-35s: %s"%('ReadBlPartial: ', csd.CsdRegisterFieldStructVer1.uiReadBlPartial))
            self.TF.logger.Message("%-35s: %s"%('ReadBlLen: ', csd.CsdRegisterFieldStructVer1.uiReadBlLen))
            self.TF.logger.Message("%-35s: %s"%('Ccc: ', csd.CsdRegisterFieldStructVer1.uiCcc))
            self.TF.logger.Message("%-35s: %s"%('TranSpeed: ', csd.CsdRegisterFieldStructVer1.uiTranSpeed))
            self.TF.logger.Message("%-35s: %s"%('Nsac: ', csd.CsdRegisterFieldStructVer1.uiNsac))
            self.TF.logger.Message("%-35s: %s"%('Taac: ', csd.CsdRegisterFieldStructVer1.uiTaac))
            self.TF.logger.Message("%-35s: %s"%('CsdStructure: ', csd.CsdRegisterFieldStructVer1.uiCsdStructure))
            self.TF.logger.Info("\n\n*************************************************************************************************************\n\n")
            return csd
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")



    def APPCMD55(self, rca=0x0000):

        import SDCommandWrapper as SDwrap
        self.TF.logger.Message("APP-SD-Command55------------------------------------------------------------------------------------------------------\n")
        RCA = rca
        try:
            CMD55_AppCmd = SDwrap.AppCmd(uiRCA=RCA)
            self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', CMD55_AppCmd.pyCmdObject.commandData.ui32Args))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("%-35s: %s"%('Card-Status', CMD55_AppCmd.pyResponseData.r1Response.uiCardStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Status: ', CMD55_AppCmd.pyResponseData.r1Response.eStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Resp1: ', CMD55_AppCmd.pyResponseData.r1Response.sdR1RespData))
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")

    def ACMD51_SendSCR(self):
        import SDCommandWrapper as SDwrap
        self.TF.logger.Message("ACMD51_SendSCR ---------------------------------------------------------------------------------------------------\n")
        try:
            ACMD51_SendSCR = SDwrap.SendSCR()
            self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', ACMD51_SendSCR.pyCmdObject.commandData.ui32Args))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("%-35s: %s"%('Card-Status', ACMD51_SendSCR.pyResponseData.r1Response.uiCardStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Status: ', ACMD51_SendSCR.pyResponseData.r1Response.eStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Resp1: ', ACMD51_SendSCR.pyResponseData.r1Response.sdR1RespData))
        ACMD51_SendSCR.objSCRRegister.ui16ExSecurity
        self.TF.logger.Message("SCR-Reg --------------------------------------------------------------------------------------------------------------\n")
        self.TF.logger.Message("%-35s: %s"%(' ScrStructure : ', ACMD51_SendSCR.objSCRRegister.ui8ScrStructure))
        self.TF.logger.Message("%-35s: %s"%(' SdSpec: ', ACMD51_SendSCR.objSCRRegister.ui8SdSpec))
        self.TF.logger.Message("%-35s: %s"%(' DataStateAfterErase: ', ACMD51_SendSCR.objSCRRegister.ui8DataStateAfterErase))
        self.TF.logger.Message("%-35s: %s"%(' SdSecurity : ', ACMD51_SendSCR.objSCRRegister.ui8SdSecurity))
        self.TF.logger.Message("%-35s: %s"%(' SdBusWidth : ', ACMD51_SendSCR.objSCRRegister.ui8SdBusWidth))
        self.TF.logger.Message("%-35s: %s"%(' SdSpec3: ', ACMD51_SendSCR.objSCRRegister.ui16SdSpec3))
        self.TF.logger.Message("%-35s: %s"%(' ExSecurity : ', ACMD51_SendSCR.objSCRRegister.ui16ExSecurity))
        self.TF.logger.Message("%-35s: %s"%(' SdSpec4: ', ACMD51_SendSCR.objSCRRegister.ui16SdSpec4))
        self.TF.logger.Message("%-35s: %s"%(' SdSpecx : ', ACMD51_SendSCR.objSCRRegister.ui16SdSpecx))
        self.TF.logger.Message("%-35s: %s"%(' CmdSupport : ', ACMD51_SendSCR.objSCRRegister.ui16CmdSupport))
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")

    def ACMD23_SetWriteBlocksEraseCount(self, NumBlks = 0):
        import SDCommandWrapper as SDwrap
        self.TF.logger.Message("ACMD23_SetWriteBlocksEraseCount: -------------------------------------------------------------------------------------\n")
        NumOfBlocks = NumBlks
        try:
            ACMD23_SetWriteBlocksEraseCount = SDwrap.SetWriteBlocksEraseCount(uiNumOfBlocks=NumOfBlocks)
            self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', ACMD23_SetWriteBlocksEraseCount.pyCmdObject.commandData.ui32Args))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("%-35s: %s"%('Card-Status: ', ACMD23_SetWriteBlocksEraseCount.pyResponseData.r1Response.uiCardStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Status: ', ACMD23_SetWriteBlocksEraseCount.pyResponseData.r1Response.eStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Resp1: ', ACMD23_SetWriteBlocksEraseCount.pyResponseData.r1Response.sdR1RespData))
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")

    def ACMD42_SetClrCardDetect(self, Set_Cd = 0):
        import SDCommandWrapper as SDwrap
        self.TF.logger.Message("ACMD42_SetClrCardDetect: ---------------------------------------------------------------------------------------------\n")
        SetCd = Set_Cd
        self.TF.logger.Message("%-35s: %s"%('Set_Cd is : ', Set_Cd))
        try:
            ACMD42_SetClrCardDetect = SDwrap.SetClrCardDetect(uiSetCd=SetCd)
            self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', ACMD42_SetClrCardDetect.pyCmdObject.commandData.ui32Args))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("%-35s: %s"%('Card-Status: ', ACMD42_SetClrCardDetect.pyResponseData.r1Response.uiCardStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Status: ', ACMD42_SetClrCardDetect.pyResponseData.r1Response.eStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Resp1: ', ACMD42_SetClrCardDetect.pyResponseData.r1Response.sdR1RespData))
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        return ACMD42_SetClrCardDetect


    def CMD56_GenCMD(self, BlockCnt):
        import SDCommandWrapper as SDwrap
        self.TF.logger.Message("CMD56_GenCmd ---------------------------------------------------------------------------------------------------------\n")
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")


    def CMD23_SetBlockCount(self, BlockCnt):
        import SDCommandWrapper as SDwrap
        self.TF.logger.Message("CMD23_SetBlockCount --------------------------------------------------------------------------------------------------\n")
        blockCnt = BlockCnt
        self.TF.logger.Message("%-35s: %s"%('BlockCnt  set to  ', BlockCnt))
        try:
            CMD23_SetBlockCount = SDwrap.SetBlockCount(blockCount = blockCnt)
            self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', CMD23_SetBlockCount.pyCmdObject.commandData.ui32Args))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("%-35s: %s"%('Card-Status', CMD23_SetBlockCount.pyResponseData.r1Response.uiCardStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Status: ', CMD23_SetBlockCount.pyResponseData.r1Response.eStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Resp1: ', CMD23_SetBlockCount.pyResponseData.r1Response.sdR1RespData))
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        return CMD23_SetBlockCount

    def ACMD22_NumOfWrittenBlocks(self):
        import SDCommandWrapper as SDwrap
        self.TF.logger.Message("ACMD22_SendNumberOfWrittenBlocks -------------------------------------------------------------------------------------\n")
        try:
            ACMD22_SendNumberOfWrittenBlocks = SDwrap.SendNumberOfWrittenBlocks()
            self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', ACMD22_SendNumberOfWrittenBlocks.pyCmdObject.commandData.ui32Args))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("%-35s: %s"%('Card-Status', ACMD22_SendNumberOfWrittenBlocks.pyResponseData.r1Response.uiCardStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Status: ', ACMD22_SendNumberOfWrittenBlocks.pyResponseData.r1Response.eStatus))
        self.TF.logger.Message("%-35s: %s"%('Cmd-Resp1: ', ACMD22_SendNumberOfWrittenBlocks.pyResponseData.r1Response.sdR1RespData))
        self.TF.logger.Message("%-35s: %s"%('numberOfWrittenBlocks: ', ACMD22_SendNumberOfWrittenBlocks.numberOfWrittenBlocks))
        self.TF.logger.Message("--------------------------------------------------------------------------------------------------------------------\n")
        return ACMD22_SendNumberOfWrittenBlocks

    def ACMD13_SDStatus(self):

        import SDCommandWrapper as SDwrap
        try:
            self.TF.logger.Message("SD-STATUS ACMD-13-------------------------------------------------------------------------------------------------\n")
            Acmd13=SDwrap.SDStatus()
            self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', Acmd13.pyCmdObject.commandData.ui32Args))
            Acmd13.pBufferObj.PrintToLog()
            self.TF.logger.Message("SD-STATUS-Response -----------------------------------------------------------------------------------------------\n")
            self.TF.logger.Message("%-35s: %s"%('SD- DiscardSupport: ', Acmd13.objSDStatusRegister.ui16DiscardSupport))
            self.TF.logger.Message("%-35s: %s"%('SD- FuleSupport: ', Acmd13.objSDStatusRegister.ui16FuleSupport))
            self.TF.logger.Message("%-35s: %s"%('SD- Reserved_3: ', Acmd13.objSDStatusRegister.ui16Reserved_3))
            self.TF.logger.Message("%-35s: %s"%('SD- Reserved_5: ', Acmd13.objSDStatusRegister.ui16Reserved_5))
            self.TF.logger.Message("%-35s: %s"%('SD- AppPerfClass: ', Acmd13.objSDStatusRegister.ui32AppPerfClass))
            self.TF.logger.Message("%-35s: %s"%('SD- Reserved_4: ', Acmd13.objSDStatusRegister.ui32Reserved_4))
            self.TF.logger.Message("%-35s: %s"%('SD- SUSAddr: ', Acmd13.objSDStatusRegister.ui32SUSAddr))
            self.TF.logger.Message("%-35s: %s"%('SD- DatBusWidth: ', Acmd13.objSDStatusRegister.ui64DatBusWidth))
            self.TF.logger.Message("%-35s: %s"%('SD- EraseOffset: ', Acmd13.objSDStatusRegister.ui64EraseOffset))
            self.TF.logger.Message("%-35s: %s"%('SD- EraseSize: ', Acmd13.objSDStatusRegister.ui64EraseSize))
            self.TF.logger.Message("%-35s: %s"%('SD- EraseTimeout: ', Acmd13.objSDStatusRegister.ui64EraseTimeout))
            self.TF.logger.Message("%-35s: %s"%('SD- PerformanceMove: ', Acmd13.objSDStatusRegister.ui64PerformanceMove))
            self.TF.logger.Message("%-35s: %s"%('SD- ReservedForSecurityFunctions: ', Acmd13.objSDStatusRegister.ui64ReservedForSecurityFunctions))
            self.TF.logger.Message("%-35s: %s"%('SD- Reserved_1: ', Acmd13.objSDStatusRegister.ui64Reserved_1))
            self.TF.logger.Message("%-35s: %s"%('SD- Reserved_2: ', Acmd13.objSDStatusRegister.ui64Reserved_2))
            self.TF.logger.Message("%-35s: %s"%('SD- SDCardType: ', Acmd13.objSDStatusRegister.ui64SDCardType))
            self.TF.logger.Message("%-35s: %s"%('SD- SDStatus: ', Acmd13.objSDStatusRegister.ui64SDStatus))
            self.TF.logger.Message("%-35s: %s"%('SD- UHSAuSize: ', Acmd13.objSDStatusRegister.ui64UHSAuSize))
            self.TF.logger.Message("%-35s: %s"%('SD- UHSSpeedGrades: ', Acmd13.objSDStatusRegister.ui64UHSSpeedGrades))
            self.TF.logger.Message("%-35s: %s"%('SD- VideoSpeedClass: ', Acmd13.objSDStatusRegister.ui64VideoSpeedClass))
            self.TF.logger.Message("%-35s: %s"%('SD- ui8PerformanceEnhance: ', Acmd13.objSDStatusRegister.ui8PerformanceEnhance))
            self.TF.logger.Message("%-35s: %s"%('SD- Performance_Enhance_CommandQueueSupport: ', Acmd13.objSDStatusRegister.ui8Performance_Enhance_CommandQueueSupport))
            self.TF.logger.Message("%-35s: %s"%('SD- Performance_Enhance_SupportForCache: ', Acmd13.objSDStatusRegister.ui8Performance_Enhance_SupportForCache))
            self.TF.logger.Message("%-35s: %s"%('SD- Performance_Enhance_SupportForHostInitiatedMaintenance: ', Acmd13.objSDStatusRegister.ui8Performance_Enhance_SupportForHostInitiatedMaintenance))
            self.TF.logger.Message("%-35s: %s"%('SD- Performance_Enhance_SupportForCardInitiatedMaintenance: ', Acmd13.objSDStatusRegister.ui8Performance_Enhance_SupportForCardInitiatedMaintenance))
            self.TF.logger.Message("%-35s: %s"%('SD- SizeOfProtectedArea: ', Acmd13.objSDStatusRegister.ui64SizeOfProtectedArea))
            self.TF.logger.Message("%-35s: %s"%('SD- VSCAuSize: ', Acmd13.objSDStatusRegister.ui16VSCAuSize))
            self.TF.logger.Message("%-35s: %s"%('SD- SecureMode: ', Acmd13.objSDStatusRegister.ui64SecureMode))
            self.TF.logger.Message("%-35s: %s"%('SD- SpeedClass: ', Acmd13.objSDStatusRegister.ui64SpeedClass))
            self.TF.logger.Message("%-35s: %s"%('SD- AuSize: ', Acmd13.objSDStatusRegister.ui64AuSize))
            self.TF.logger.Message("%-35s: %s"%('CardStatus: ', Acmd13.pyResponseData.r1bResponse.uiCardStatus))
            #-------------------------------------------------------------------------------------------------------
            self.ProtectedArea = int (self.MULT*self.BLOCK_LEN*Acmd13.objSDStatusRegister.ui64SizeOfProtectedArea)
            self.TF.logger.Message("%-35s: %s"%('Calculated-Protected Area is: ', self.ProtectedArea))
            self.ProtectedArea_MemCap = self.ProtectedArea + self.MemCap
            self.TF.logger.Message("%-35s: %s"%('ProtectedArea_MemCap Area is: ', self.ProtectedArea_MemCap))
            #-------------------------------------------------------------------------------------------------------
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        return Acmd13

    def CMD20_SDSpeedClassControl(self, SpeedClass = 0x00, SpeedClassDes=0x00000000):

        import SDCommandWrapper as SDwrap
        import CTFServiceWrapper as ServiceWrap
        SpeedClassCommandDescription = SpeedClassDes
        SpeedClassControl = SpeedClass
        try:
            self.TF.logger.Message("SpeedClassControl-CMD20: -----------------------------------------------------------------------------------------\n")
            CMD20_SDSpeedClassControl = SDwrap.SpeedClassControl(uiSpeedClassCommandDescription=SpeedClassCommandDescription, uiSpeedClassControl=SpeedClassControl, sendType=ServiceWrap.SEND_IMMEDIATE)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        return CMD20_SDSpeedClassControl


    def Erase_TimeOUT(self, XAUs = 1):

        import SDCommandWrapper as SDwrap
        self.TF.logger.Message("APP-SD-Command55------------------------------------------------------------------------------------------------------\n")
        RCA = 0xD555
        try:
            CMD55_AppCmd = SDwrap.AppCmd(uiRCA=RCA)
            self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', CMD55_AppCmd.pyCmdObject.commandData.ui32Args))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        self.TF.logger.Message("SD-STATUS ACMD-13-----------------------------------------------------------------------------------------------------\n")
        Acmd13=SDwrap.SDStatus()
        self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', Acmd13.pyCmdObject.commandData.ui32Args))
        #Acmd13.pBufferObj.PrintToLog()
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        AUSize  = Acmd13.objSDStatusRegister.ui64AuSize
        N_ERASE = Acmd13.objSDStatusRegister.ui64EraseSize
        T_ERASE = Acmd13.objSDStatusRegister.ui64EraseTimeout
        T_OFFSET = Acmd13.objSDStatusRegister.ui64EraseOffset
        self.TF.logger.Message("%-35s: %s"%('N_ERASE is : ', N_ERASE))
        self.TF.logger.Message("%-35s: %s"%('T_ERASE is : ', T_ERASE))
        if((Acmd13.objSDStatusRegister.ui64EraseTimeout) == 0 or (Acmd13.objSDStatusRegister.ui64EraseSize == 0)):
            self.TF.logger.Message("%-35s: %s"%('SD- EraseSize: ', Acmd13.objSDStatusRegister.ui64EraseSize))
            self.TF.logger.Message("%-35s: %s"%('SD- EraseTimeout: ', Acmd13.objSDStatusRegister.ui64EraseTimeout))
            self.TF.logger.Message("ERASE TimeOUT calculation NOT Supported\n")
            return 0
        else:
            T_OFFSET = (Acmd13.objSDStatusRegister.ui64EraseOffset)
            self.TF.logger.Message("%-35s: %s"%('T_OFFSET is : ', T_OFFSET))
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        self.TF.logger.Message("%-35s: %s"%('XAUs is : ', XAUs))
        slope = float (T_ERASE ) / float (N_ERASE)
        self.TF.logger.Message("%-35s: %s"%('slope: ', slope))
        EraseTimeout_XAU = ((slope * XAUs ) + T_OFFSET)
        self.TF.logger.Message("%-35s: %s"%('EraseTimeout_XAU: ', EraseTimeout_XAU))
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        return EraseTimeout_XAU

    def SD_LockUnlock(self, PWDSLEN=0,cop=0,Erase=0,LockUnLock=0,ClrPwd=0,SetPwd=0, Password=[], SkipCMD13 = False):
        import SDCommandWrapper as SDwrap
        PSW = list()
        PSW = Password #[1,2,3,4,5,6,7,8]
        CardSrtuctCnf = SDwrap.LOCK_CARD_DATA_STRUCTURE()
        CardSrtuct = SDwrap.LOCK_CARD_DATA_STRUCTURE()
        CardSrtuct.lockCardDataStructureByte0.uiSet_Pwd = SetPwd
        CardSrtuct.lockCardDataStructureByte0.uiClr_Pwd = ClrPwd
        CardSrtuct.lockCardDataStructureByte0.uiLock_Unlock = LockUnLock
        CardSrtuct.lockCardDataStructureByte0.uiErase = Erase
        CardSrtuct.lockCardDataStructureByte0.uiCop = cop
        if(Erase == 0):
            CardSrtuct.uiPasswordData =  PSW
            CardSrtuct.uiPWDS_LEN = PWDSLEN
        self.TF.logger.Message("CMD42_LockUnlock: ----------------------------------------------------------------------------------------------------\n")
        CardSrtuctCnf = CardSrtuct
        self.TF.logger.Message("%-35s: %s"%('SetPwd is: ', CardSrtuctCnf.lockCardDataStructureByte0.uiSet_Pwd))
        self.TF.logger.Message("%-35s: %s"%('Clr_Pwd is: ', CardSrtuctCnf.lockCardDataStructureByte0.uiClr_Pwd))
        self.TF.logger.Message("%-35s: %s"%('Lock_Unlock is: ', CardSrtuctCnf.lockCardDataStructureByte0.uiLock_Unlock))
        self.TF.logger.Message("%-35s: %s"%('Erase is: ', CardSrtuctCnf.lockCardDataStructureByte0.uiErase))
        self.TF.logger.Message("%-35s: %s"%('Cop is: ', CardSrtuctCnf.lockCardDataStructureByte0.uiCop))
        self.TF.logger.Message("%-35s: %s"%('PSW is: ', CardSrtuctCnf.uiPasswordData))
        skipCmd13 = SkipCMD13
        self.TF.logger.Message("%-35s: %s"%('skipCmd13 is: ', skipCmd13))
        try:
            CMD42_LockUnlock = SDwrap.LockUnlock(CardSrtuctCnf, skipCmd13)
            self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', CMD42_LockUnlock.pyCmdObject.commandData.ui32Args))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        return CMD42_LockUnlock
        #self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")

    def SD_ConfQueue(self, StartBlockAddress=0 , NumberOfBlocks=8, TaskID=1, Priority=0, ExtendedAddress=0, Direction=0):
        import SDCommandWrapper as SDwrap
        self.TF.logger.Message("CMD44_QueueTaskInfoA--------------------------------------------------------------------------------------\n")
        self.TF.logger.Message("%-35s: %s"%('CMD44_QueueTaskInfoA with NumberOfBlocks: ', NumberOfBlocks))
        self.TF.logger.Message("%-35s: %s"%('CMD44_QueueTaskInfoA with Priority: ', Priority))
        self.TF.logger.Message("%-35s: %s"%('CMD44_QueueTaskInfoA with TaskID: ', TaskID))
        self.TF.logger.Message("%-35s: %s"%('CMD44_QueueTaskInfoA with ExtendedAddress: ', ExtendedAddress))
        self.TF.logger.Message("%-35s: %s"%('CMD44_QueueTaskInfoA with Direction: ', Direction))
        try:
            CMD44_QueueTaskInfoA  = SDwrap.QueueTaskInfoA(uiNumberOfBlocks=NumberOfBlocks, uiTaskID=TaskID, uiPriority=Priority, uiExtendedAddress=ExtendedAddress, uiDirection=Direction)
            self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', CMD44_QueueTaskInfoA.pyCmdObject.commandData.ui32Args))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.logger.Message("CMD45_QueueTaskInfoB--------------------------------------------------------------------------------------\n")
        StartBlockAddress
        self.TF.logger.Message("%-35s: %s"%('CMD45_QueueTaskInfoB with StartBlockAddress: ', StartBlockAddress))
        try:
            CMD45_QueueTaskInfoB = SDwrap.QueueTaskInfoB(uiStartBlockAddress = StartBlockAddress)
            self.TF.logger.Message("%-35s: %s"%('Card-Req-ui32Args: ', CMD45_QueueTaskInfoB.pyCmdObject.commandData.ui32Args))
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        return CMD45_QueueTaskInfoB



    def SD_PowerCycle(self):
        import SDCommandWrapper as SDwrap
        import CTFServiceWrapper as serviceWrap

        SendType = serviceWrap.SEND_IMMEDIATE_SYNC
        sdPpwerCycleParam = serviceWrap.SD_POWER_CYCLE_PARAMS()
        sdPpwerCycleParam.bIsEnablePowerSustenance = True # Power oFF notification TRue
        sdPpwerCycleParam.bIsEnableCache = False
        sdPpwerCycleParam.bIsEnableCardInitiatedSelfMaintenance = False
        sdPpwerCycleParam.bIsEnableHostInitiatedMaintenance = False
        sdPpwerCycleParam.bIsDisablePowerManagementFunction = False
        sdPpwerCycleParam.sdShutdownType = 0

        sdProtocolParam = serviceWrap.PROTOCOL_SPECIFIC_PARAMS()
        sdProtocolParam.paramType = serviceWrap.SD_POWER_CYCLE
        sdProtocolParam.sdParams = sdPpwerCycleParam
        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")

        #PowerCycle = ServiceWrap.PowerCycle(shutdownType= ServiceWrap.GRACEFUL, pModelPowerParamsObj= {0}, pGPIOMap= {0}, protocolParams = sdProtocolParam, isAsync= False,  SDsendType= SendType)
        PowerCycle = ServiceWrap.PowerCycle(shutdownType = serviceWrap.GRACEFUL, protocolParams = sdProtocolParam, sendType= SendType)

        self.TF.logger.Message("----------------------------------------------------------------------------------------------------------------------\n")
        return PowerCycle

### SD-Command--End------------------------------------------------------------------------------------------------------ ###

### SD-Command-Security Commands---------------------------------------------------------------------------------------- ###


    def WriteSecurityInternalFiles(self, paramsFile, maxLba):
        import SDCommandWrapper as SDwrap
        try:
            SDwrap.WriteProductionFile(maxLba, paramsFile)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        try:
            SDwrap.WriteHIddenSystemFile()
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def WriteSecurityKeys(self ):
        import SDCommandWrapper as SDwrap
        MKB_FILEnumO = 0
        MKB_FILEnum16 = 16
        for i in range(MKB_FILEnumO, MKB_FILEnum16):
            #logger.Info("","Write MKB #[%d] " %(i))
            self.TF.logger.Message("%-35s: %s"%('Write MKB #[%d]: ', i))
            try:
                SDwrap.WriteMKB(i)
            except ValidationError.CVFExceptionTypes as ex:
                self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
                raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def SetSecurityState(self ):
        import SDCommandWrapper as SDwrap
        try:
            SDwrap.SetSecureState(7)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")


    def SecureFormatProcess(self ):
        import SDCommandWrapper as SDwrap
        import CTFServiceWrapper as serviceWrap

        buf = serviceWrap.Buffer.CreateBuffer(1, patternType=serviceWrap.ALL_1, isSector=True)
        diagCmd = serviceWrap.DIAG_FBCC_CDB()

        blockLen = 512
        options = 1 #Default value used in SVP SRW01 script.
        diagCmd.cdb = [0x91, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        diagCmd.cdbLen = 16
        diagCmd.cdb[2] = (options & 0xFF)
        diagCmd.cdb[3]  =  (options >> 8) & 0xFF
        try:
            sctpCommand = serviceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, serviceWrap.DIRECTION_NONE, False, None, 20000, sendType=serviceWrap.SEND_IMMEDIATE_SYNC)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

    def DoPowerCycle(self ):
        import SDCommandWrapper as SDwrap
        import time

        self.TF.logger.Message("PowerCycle HW - Begin-------------------------------------------------------------------------------------------------\n")
        #Power Off
        try:
            SDwrap.SDRPowerCycle()
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        time.sleep(4)
        self.TF.logger.Message("PowerCycle HW - End   ------------------------------------------------------------------------------------------------\n")


    def Update_MkB(self, keyID, newKeyID, nSectors = 128 ):
        import SDCommandWrapper as SDwrap
        import CTFServiceWrapper as serviceWrap
        import time

        self.TF.logger.Message("WriteMKBUsingFilenames HW - Begin-------------------------------------------------------------------------------------\n")
        keyPath = os.getenv("SANDISK_CTF_HOME_X64")
        dkPath = os.path.join(keyPath, "Security\DK_num.bin")
        mkbFilename = "Security\\" + "Mkb_#" + str(newKeyID) + ".bin"
        mkbPath = os.path.join(keyPath, mkbFilename)
        if not os.path.exists(dkPath):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DK file doesn't exist in path - %s" % dkPath)
        if not os.path.exists(mkbPath):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "New MKB file doesn't exist in path - %s" % mkbPath)
        try:
            update_mkb = SDwrap.WriteMKBUsingFilenames(1, nSectors, keyID, True, mkbPath, dkPath, sendType=serviceWrap.SEND_IMMEDIATE_SYNC)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the  Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #update_mkb.Execute()
        #update_mkb.HandleAndParseResponse()
        self.TF.logger.Message("WriteMKBUsingFilenames- End   ----------------------------------------------------------------------------------------\n")

    def GetMaxLbaFromParameterFile(self, paramsFile,capacity):

        maxLba=None
        try:
            f = open(paramsFile)
            linelist=f.readlines()
            f.close()
        except:
            #logger.Critical("", "Unable to open the parameter file %s."%(paramsFile))
            self.TF.logger.Message("%-35s: %s"%('nable to open the parameter file: ', paramsFile))
            raise

        if capacity == '394G':
            capacity = '400G'

        if capacity == '197G':
            capacity = '200G'

        if capacity == '1T':
            capacity = '1024G'

        startIndex=linelist.index("[CAPACITIES]\n")
        capacityList=[]
        for element in linelist[startIndex+1:]:
            capacityList.append(element)
            if "[" in element:
                break

        #print capacityList

        searchString="="+capacity
        for line in capacityList:
            if not line[0]=="#":
                if searchString in line:
                    maxLba,capacity=line.split("=")
                    break

        if maxLba is None:
            raise Exception("[GetMaxLbaFromParameterFile] Unable to find the maxLba for the capacity %s in the given parameter file %s"%(capacity,paramsFile))

        return int(maxLba)








### SD-Command-Security Commands-End------------------------------------------------------------------------------------ ###



###--------------------------------SD-Command-END ----------------------------------------------------------------------- ###






###--------------------------------SCTP Command ------------------------------------------------------------------------- ###
    def ReadConfigSet(self, ConfSet, secCount, RequestSize = False, sendType = ServiceWrap.SEND_IMMEDIATE):
        """"""
        # number of bytes in sectors...
        LengthInBytes = secCount * self.SECTOR_SIZE

        Buffer = ServiceWrap.Buffer.CreateBuffer(LengthInBytes , patternType=ServiceWrap.ALL_1, isSector=False)

        diagCmd = ServiceWrap.DIAG_FBCC_CDB()

        if RequestSize:
            OpcodeId = 0x41         #  DIAG_SUBCODE_CFG_SET_LENGTH
            secCount = 2
        else:
            OpcodeId = 0x40         #  DIAG_SUBCODE_READ_CFG_SET

        diagCmd.cdb = [0x8A, 0, 0, 0, 0,0, 0,0, 0,0,0,0, 0,0,0,0]
        diagCmd.cdb[2] = (OpcodeId & 0xFF)
        diagCmd.cdb[3] = (OpcodeId >> 8) & 0xFF
        diagCmd.cdb[4] = ConfSet & 0xFF
        diagCmd.cdb[5] = (ConfSet >> 8 ) & 0xFF
        diagCmd.cdb[8] = secCount & 0xFF
        diagCmd.cdb[9] = (secCount >> 8 ) & 0xFF
        diagCmd.cdb[10] = (secCount >> 16) & 0xFF
        diagCmd.cdb[11] = (secCount >> 24) & 0xFF
        diagCmd.cdb[12] = LengthInBytes & 0xFF
        diagCmd.cdb[13] = (LengthInBytes >> 8 ) & 0xFF
        diagCmd.cdb[14] = (LengthInBytes >> 16) & 0xFF
        diagCmd.cdb[15] = (LengthInBytes >> 24) & 0xFF

        diagCmd.cdbLen = 16
        self.TF.logger.Info("SendDiagnostic : Read Configuration Set - CDB={0}".format(diagCmd.cdb))

        try:

            sctpCommand = NVMeWrap.SCTPCommand.SCTPCommand(diagCmd, Buffer, ServiceWrap.DIRECTION_OUT,False, None, 200000, sendType = sendType)
            self.TF.logger.Info("Read Config Diagnostic completed successfully")

            #Buffer.PrintToLog()

            return Buffer

        except ValidationError.CVFExceptionTypes as ex:
            raise ValidationError.VtfGeneralError("SCTP_ERROR","Read config set Diagnostic Failed" + ex.GetFailureDescription())


    def ReadCardGeometry(self, sendType = ServiceWrap.SEND_IMMEDIATE):

        diagCommand = ServiceWrap.DIAG_FBCC_CDB()
        dataBuffer = ServiceWrap.Buffer.CreateBuffer(self.SECTOR_SIZE , patternType=ServiceWrap.ALL_0, isSector=False)

        cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        cdb     = [0xB8, 0, 0, 0, 0,0, 0,0, 0,0,0,0, 0,0,0,0]
        #cdb[2]  = subOpcode & 0xFF

        diagCommand.cdb = cdb
        diagCommand.cdbLen = len(cdb)
        self.DirectMode = 1
        self.TF.logger.Info("Sending SCTP for Get Card Geometry Data CDB: %s"%diagCommand.cdb)
        #self.TF.logger.Info("SubOpcode: %d "%(subOpcode))

        try:

            sctpCommand = ServiceWrap.SCTPCommand.SCTPCommand(diagCommand, dataBuffer, ServiceWrap.DIRECTION_OUT,False, None, 200000, sendType = sendType )
            self.TF.logger.Info("SCTP for Get Read Scrub data completed successfully")

        except ValidationError.CVFExceptionTypes as ex:
            raise ValidationError.VtfGeneralError("SCTP_ERROR","Get Read Scrub Diagnostic Failed" + ex.GetFailureDescription())
        return dataBuffer


    def WriteFileSystem(self, fileID = 0, sectorCount = 1, dataBuffer = None, sendType = ServiceWrap.SEND_IMMEDIATE):

        diagCommand = ServiceWrap.DIAG_FBCC_CDB()

        cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        cdb[0] = 0x8B
        cdb[1] = cdb[2] = cdb[3] = 0
        cdb[4] = (fileID & 0xFF)
        cdb[5] = (fileID >> 8) & 0xFF
        cdb[6] = (fileID >> 16) & 0xFF
        cdb[7] = (fileID >> 24) & 0xFF
        cdb[8] = sectorCount & 0xFF
        cdb[9] = (sectorCount >> 8 ) & 0xFF
        cdb[10] = (sectorCount >> 16) & 0xFF
        cdb[11] = (sectorCount >> 24) & 0xFF
        cdb[12] = cdb[13] = cdb[14] = cdb[15] = 0

        diagCommand.cdb = cdb
        diagCommand.cdbLen = len(cdb)

        self.TF.logger.Info("Sending WRITE FILE SYSTEM CDB: %s"%diagCommand.cdb)
        self.TF.logger.Info("File ID: %d Sector Count: %d"%(fileID, sectorCount))
        self.TF.logger.Info("Write Buffer Size: %d Bytes"%dataBuffer.GetBufferSize())

        try:

            sctpCommand = ServiceWrap.SCTPCommand.SCTPCommand(diagCommand, dataBuffer, ServiceWrap.DIRECTION_IN,False, None, 200000, sendType = sendType )

        except ValidationError.CVFExceptionTypes as ex:
            raise ValidationError.VtfGeneralError("SCTP_ERROR","Write File system Diagnostic Failed" + ex.GetFailureDescription())



    def ReadFileSize(self, fileid, sendType = ServiceWrap.SEND_IMMEDIATE):
        #ReadFile
        sectorCount = 1
        opcode = 0x8A
        OpcodeId = 0x0001   # DIAG_SUBCODE_FILE_LENGTH

        readbuff = ServiceWrap.Buffer.CreateBuffer(sectorCount)
        diagCommand = ServiceWrap.DIAG_FBCC_CDB()
        cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        cdb[0] = (opcode & 0xFF);
        cdb[1] = (opcode >> 8) & 0xFF;
        cdb[2] = OpcodeId
        #cdb[2] = (OpcodeId & 0xFF)
        #cdb[3] = (OpcodeId >> 8) & 0xFF
        cdb[4] = (fileid & 0xFF);
        cdb[5] = (fileid >> 8) & 0xFF;
        cdb[6] = (fileid >> 16) & 0xFF;
        cdb[7] = (fileid >> 24) & 0xFF;
        cdb[8] = sectorCount & 0x000000FF
        cdb[9] = (sectorCount >> 8 )& 0x000000FF
        cdb[10] = (sectorCount >> 16) & 0x000000FF
        cdb[11] = (sectorCount >> 24) & 0x000000FF

        diagCommand.cdb = cdb
        print(diagCommand.cdb)
        diagCommand.cdbLen = 16

        #sctpCommand = PyWrap.SCTPCommand.SCTPCommand(diagCommand, readbuff, PyWrap.DIRECTION_OUT,sendType=PyWrap.SEND_IMMEDIATE)
        #sctpCommand = PyWrap.SCTPCommand.SCTPCommand(diagCommand, readbuff, PyWrap.DIRECTION_OUT,False, None, 200000, PyWrap.SEND_IMMEDIATE)
        try:
            sctpCommand = ServiceWrap.SCTPCommand.SCTPCommand(diagCommand, readbuff, ServiceWrap.DIRECTION_OUT,False, None, 200000, sendType = sendType )
            #self.vtfContainer.cmd_mgr.PostRequestToWorkerThread(sctpCommand)
            self.TF.logger.Info("Read File Diagnostic completed successfully")

            size = old_div(readbuff.GetTwoBytesToInt(0, False),16) # divide by 16 because of 4K sector

            return size

        except ValidationError.CVFExceptionTypes as ex:
            raise ValidationError.VtfGeneralError("SCTP_ERROR","Read file size Diagnostic Failed" + ex.GetFailureDescription())


    def ReadNANDInfo(self, subOpcode=0, FIM=0, Chip=0, Die=0, dataBuffer = None, sendType = ServiceWrap.SEND_IMMEDIATE):
        diagCommand = PyWrap.DIAG_FBCC_CDB()
        cdb = [0]*16

        cdb[0] = 0xA2
        cdb[1] = 0
        cdb[2] = 0x0000
        cdb[3] = 1
        cdb[4] = 1
        cdb[5] = 1

        diagCommand.cdb = cdb
        diagCommand.cdbLen = 16


        self.TF.logger.Info("Sending ReadNANDInfo CDB: %s"%diagCommand.cdb)
        self.TF.logger.Info("subOpcode: {0}, FIM:{1}, Chip:{2}, Die:{3} ".format(subOpcode, FIM, Chip, Die))
        dataBuffer = PyWrap.Buffer.CreateBuffer(4096 , patternType=PyWrap.ALL_0, isSector=False)

        try:

            sctpCommand = PyWrap.SCTPCommand.SCTPCommand(diagCommand, dataBuffer, PyWrap.DIRECTION_OUT ,False, None, 200000, sendType = sendType )
            self.TF.logger.Info("ReadNANDInfo Diagnostic completed successfully")
        except ValidationError.CVFExceptionTypes as ex:
            raise ValidationError.VtfGeneralError("SCTP_ERROR","Read Nand info Diagnostic Failed" + ex.GetFailureDescription())


    def Format(self, sendType = ServiceWrap.SEND_IMMEDIATE):

        dataBuffer = PyWrap.Buffer.CreateBuffer(dataSize = 4096, patternType = PyWrap.ALL_0, isSector = False)
        formatParam = PyWrap.FormatParameters(dataBuffer)

        diagCommand = PyWrap.DIAG_FBCC_CDB()

        cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        cdb[0] = 0x8F
        cdb[2] = (formatParam.GetOptions() & 0xFF)
        cdb[3] = (formatParam.GetOptions() >> 8) & 0xFF


        diagCommand.cdb = cdb
        diagCommand.cdbLen = 16

        self.TF.logger.Info("Sending FORMAT CDB: %s"%diagCommand.cdb)
        self.TF.logger.Info("Buffer Size: %d Bytes"%dataBuffer.GetBufferSize())

        sctpCommand = NVMeWrap.SCTPCommand.SCTPCommand(diagCommand, formatParam.GetDataBuffer(), PyWrap.DIRECTION_IN,False, None, 200000, PyWrap.SEND_IMMEDIATE)
        try:
            #sctpCommand = PyWrap.SCTPCommand.SCTPCommand(diagCommand, formatParam.GetDataBuffer(), PyWrap.DIRECTION_IN,False, None, 200000, PyWrap.SEND_IMMEDIATE)
            self.TF.logger.Info("Format Diagnostic command is excuted as part of production sequence and hence assumed that its working")

        except ValidationError.CVFExceptionTypes as ex:

            raise ValidationError.VtfGeneralError("SCTP_ERROR","Format  Diagnostic Failed" + ex.GetFailureDescription())
    #**************************************************************************************************************
    # This method is used to send Get Format Status Command (0x70)
    # This method sends a SCTP Command 0x70
    # Param None
    # return Format Status
    # exception None
    #**************************************************************************************************************
    def GetFormatStatus(self, sendType = ServiceWrap.SEND_IMMEDIATE):

        dataBuffer = PyWrap.Buffer.CreateBuffer(dataSize = 4096, patternType = PyWrap.ALL_0, isSector = False, )
        formatParam = PyWrap.FormatParameters(dataBuffer)

        diagCommand = PyWrap.DIAG_FBCC_CDB()

        cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        cdb[0] = 0x70

        diagCommand.cdb = cdb
        diagCommand.cdbLen = 16

        self.TF.logger.Info("Sending Get FORMAT Status CDB: %s"%diagCommand.cdb)
        self.TF.logger.Info("Buffer Size: %d Bytes"%dataBuffer.GetBufferSize())

        #sctpCommand = PyWrap.SCTPCommand.SCTPCommand(diagCommand, dataBuffer, PyWrap.DIRECTION_OUT,False, None, 200000, PyWrap.SEND_IMMEDIATE)
        try:

            #self.vtfContainer.cmd_mgr.PostRequestToWorkerThread(sctpCommand)
            sctpCommand = NVMeWrap.SCTPCommand.SCTPCommand(diagCommand, dataBuffer, PyWrap.DIRECTION_OUT,False, None, 200000, PyWrap.SEND_IMMEDIATE)
            self.TF.logger.Info("Get FORMAT Status Diagnostic Exeucted as part of Prod seq and hence assumed as working")

        except ValidationError.CVFExceptionTypes as ex:

            raise ValidationError.VtfGeneralError("SCTP_ERROR","Get FORMAT Status  Diagnostic Failed" + ex.GetFailureDescription())
        return formatstatus


