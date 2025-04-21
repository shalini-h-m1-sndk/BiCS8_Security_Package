
"""
################################################################################
# Copyright (c) SanDisk Corp.2013 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# FILE:DPAModelLib.py: Command Utility Library.
# AUTHOR: Manjunath & Balraj
################################################################################
"""

from builtins import range
from builtins import object
import sys, os, time, shutil, datetime, random, string, subprocess, csv
from array import *

import CTFServiceWrapper as ServiceWrap
import NVMeCMDWrapper as NVMeWrap
import Core.ValidationError as ValidationError
import Protocol.NVMe.Basic.VTFContainer as VTF

import Validation.CVFTestFactory as FactoryMethod

#**************************************************************************************************************
##
# @brief Runs all the variations in the testObject
# @details
# @return None
# @exception None
#**************************************************************************************************************
class DPAModelLib(object):

    cardMap = dict()
    #readBuffer = ServiceWrap.Buffer.CreateBuffer(1)
    def __init__(self,currCfg):#
        # Define Instance
        self.CVFTestFactory = FactoryMethod.CVFTestFactory().GetProtocolLib()
        self.TF = self.CVFTestFactory.TestFixture
        self.CU = self.CVFTestFactory.CMDUtil
        self.RWCLib = self.CVFTestFactory.RWCLib
        self.SCTPUtils =  self.CVFTestFactory.SctpUtils

        self.bufferManager = self.TF.testSession.GetDTBufferManager()
        self.maxPatternID = self.bufferManager.GetMaxPatternID()

        self.configParser = self.TF.testSession.GetConfigInfo()
        self.errorManager = self.TF.testSession.GetErrorManager()
        self.VTFContainer = VTF.VTFContainer()
        self.statistics = self.TF.testSession.GetStatisticsObj()

        # Variation
        self.startLba= currCfg.startLba
        self.maxLba= self.TF.nsCap
        self.transferlength=currCfg.transferlength
        self.writeTimeout = currCfg.writeTimeout
        self.readTimeout=currCfg.readTimeout
        self.CommandCount=currCfg.CommandCount
        self.nameSpaceID = currCfg.nameSpaceID
        self.wayPointList = 0
        self.FormateCount = 0
        self.txLenMin = currCfg.transferlengthmin
        self.txLenMax = currCfg.transferlengthmax


        self.submissionQID = 1

        self.sendType = ServiceWrap.CMD_SEND_TYPE.SEND_QUEUED
        self.isAsync = False
        self.deleteQs = False

        self.dataTrackEnabled = False
        if int(self.configParser.GetValue('datatracking_enabled', 0)[0]):
            self.dataTrackEnabled = True

        self.patternDict = dict()
        self.patternTypes = [ServiceWrap.ALL_0, ServiceWrap.ALL_1, ServiceWrap.BYTE_REPEAT, ServiceWrap.RANDOM]
        self.ShutdownType = NVMeWrap.NORMAL_SHDN
        self.ResetType = self.CU.GetDPAResetType()
        self.uiNamespaceId = 1
        self.sectorSize = self.TF.testSession.GetLbaSizeInBytes(self.uiNamespaceId)

    def GSDPowerCycleCmd(self, isAsync, deleteQs, ShutdownType= NVMeWrap.NORMAL_SHDN):
        self.TF.logger.Info("********   Posting GSD - PowerCycle Cmd  with isAsync- %s, deleteQs- %s, ShutdownType-%s ********  "%(isAsync, deleteQs, ShutdownType))
        pProtocolParams = ServiceWrap.PROTOCOL_SPECIFIC_PARAMS()
        pProtocolParams.nvmeParams.nvmeShutdownType = ShutdownType
        pProtocolParams.nvmeParams.deleteQueues = False

        protocolParamsObj = self.CU.PostPowerCycle(ServiceWrap.GRACEFUL,protocolParamsObj = pProtocolParams, isAsync = isAsync,sendType=ServiceWrap.CMD_SEND_TYPE.SEND_QUEUED)
        self.TF.logger.Info("********   Completed GSD PowerCycle Cmd  ********  ")

    def UGSDPowerCycleCmd(self,isAsync, deleteQs):
        self.TF.logger.Info("********   Posting USDG PowerCycle Cmd  with isAsync - %s,  deleteQs = %s ********  "%(isAsync, deleteQs))
        ugsdCmd = self.CU.PostPowerCycle(ServiceWrap.UNGRACEFUL, isAsync = isAsync,sendType=ServiceWrap.CMD_SEND_TYPE.SEND_QUEUED)
        self.TF.logger.Info("********   Completed USDG PowerCycle Cmd  ********  ")

    def AbortPowerCycleCmd(self,isAsync, deleteQs):
        self.TF.logger.Info("********   Posting Power Abort Cmd with isAsync - %s,  deleteQs = %s ********  "%(isAsync, deleteQs))
        powerAbortCmd = self.CU.PostPowerCycle(ServiceWrap.ABORT, isAsync = isAsync,sendType=ServiceWrap.CMD_SEND_TYPE.SEND_QUEUED)
        self.TF.logger.Info("********   Completed Power Abort Cmd  ********  ")

    def WriteCmd(self):
        self.TF.logger.Info("********   Posting Write Cmd  ********  ")
        self.RWCLib.DoWrites(count = self.CommandCount, ErrorExpected = True)
        self.TF.logger.Info("********   Completed Write Cmd  ********  ")

    def ReadCmd(self):
        self.TF.logger.Info("********   Posting Read Cmd  ********  ")
        self.RWCLib.DoRead(count = self.CommandCount, ErrorExpected = True)
        self.TF.logger.Info("********   Completed read Cmd  ********  ")

    def FormatCmd(self, SES=0):
        self.TF.logger.Info("********   Posting Format Cmd  ********  ")
        self.CU.PostFormat(SES =SES,  sendType=ServiceWrap.CMD_SEND_TYPE.SEND_QUEUED)
        self.TF.logger.Info("********  Format Cmd Completed    ********")

    def TrimCmd(self):
        self.TF.logger.Info("********   Posting Trim Cmd  ********  ")
        lbaRangeList = self.RWCLib.GetLbaRange(self.maxLba, self.txLenMin, self.txLenMax, self.startLba)
        self.CU.PostTrim(lbaRangeList, self.submissionQID, self.nameSpaceID)

    def WriteUncorrectableCmd(self, count = 100):
        self.TF.logger.Info("********   Posting WUC Cmd  ********  ")
        self.RWCLib.DoWUCmd(count = self.CommandCount, ErrorExpected = True)

    def Write0(self, count = 0, lenMax = 0):
        self.TF.logger.Info("********   Posting Write Zeros Cmd  ********  ")
        self.RWCLib.DoWr0(self.nameSpaceID, count , lenMax )

    def update_status(self,sendType):
        getNvmeConfigReg = NVMeWrap.GetNVMeConfigReg(NVMeWrap.ControllerReg.CSTS, sendType)
        return getNvmeConfigReg

    def ResetControllerCmd(self, ResetType):
        sendType = ServiceWrap.SEND_IMMEDIATE
        getNvmeConfigReg = NVMeWrap.GetNVMeConfigReg(NVMeWrap.ControllerReg.CSTS, sendType)
        self.CU.SetDPAResetType(ResetType)
        if ('disablectrl' == self.CU.GetDPAResetType() ):
            self.TF.logger.Info("********   Posting DISABLE CONTROLLER  ********  ")
            resetCommand = self.CU.ResetController(disableController = True, shutdown = False, deleteQueues = False, NVMeSubsytemReset = False, sendType = self.sendType)
            self.update_status(sendType)
            #if not getNvmeConfigReg.Output.CSTS.RDY:
            self.CU.ActivateControllerCmd()
        elif ('deleteq' == self.CU.GetDPAResetType() ):
            self.TF.logger.Info("********  Posting DELETE QUEUES  ********  ")
            resetCommand = self.CU.ResetController(disableController = False, shutdown = False, deleteQueues = True, NVMeSubsytemReset = False, sendType = self.sendType)
            self.CU.ActivateControllerCmd()
        elif ('shutdown' == self.CU.GetDPAResetType() ):
            self.TF.logger.Info("********  Posting SHUTDOWN   ********  ")
            resetCommand = self.CU.ResetController(disableController = False, shutdown = True, deleteQueues = False, NVMeSubsytemReset = False, sendType = self.sendType)
            self.update_status(sendType)
            #if getNvmeConfigReg.Output.CSTS.SHST == 0x02:
            self.CU.ActivateControllerCmd()
        elif ('NSSR' == self.CU.GetDPAResetType() ):
            self.TF.logger.Info("******** Posting  NVMe Sub System Reset   ******** ")
            resetCommand = self.CU.ResetController(disableController = False, shutdown = False, deleteQueues = False, NVMeSubsytemReset = True, sendType = self.sendType)
            self.update_status(sendType)
            #if getNvmeConfigReg.Output.CSTS.RDY:
            self.CU.ActivateControllerCmd()
        self.TF.logger.Info("******** Controller - %s Command Completed  ******** \n\n"%self.ResetType)

    def WriteFileSystem(self, fileID = 0, sectorCount = 1):
        try:
            dataBuffer = ServiceWrap.Buffer.CreateBuffer(8, patternType = 0, isSector = True)
            self.TF.logger.Info("********   Posting SCTP-Write Cmd  ********  ")
            self.SCTPUtils.WriteFileSystem(fileID = fileID, sectorCount = sectorCount, dataBuffer = dataBuffer)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the SCTP-Write Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting SCTP-Write Command\n")

    def Set_PWS_Mgmt(self):
        NS_ID = 0xFFFFFFFF
        NPSS = self.TF.powerstate
        self.TF.logger.Message("%-35s: %s"%('NUm of Pwer Sate  NPSS: ', NPSS))
        for PwrSt in range(0, (NPSS+1)):
            NxtPS = PwrSt
            self.TF.logger.Message("%-35s: %s"%('\nIssue Set feature cmd to put Device in PwrSate: ', NxtPS))
            try:
                SetPwrSt = self.CU.SetPwrState(NxtPS)
            except ValidationError.CVFExceptionTypes as ex:
                self.TF.logger.Fatal("Failed to Post the Get/Set Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
                raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
            self.TF.threadPool.WaitForThreadCompletion()

    def Get_PWS_Mgmt(self):
        self.TF.logger.Message("----- Get Current Pwr State---------------------------------------\n")
        try:
            GetPwrSt = self.CU.GetPwrStateCap(NVMeWrap.CURRENT)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed to Post the Get/Set Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        self.TF.threadPool.WaitForThreadCompletion()

        outputDW0 = GetPwrSt.objNVMeComIOEntry.completionEntry.DW0
            ##Extract the PS and WH value
        WH = outputDW0 & 0xFFFFFFE0
        CrntPS = outputDW0 & 0x1F
        self.TF.logger.Message("-----------------------------------------------------\n")
        self.TF.logger.Message("%-35s: %s"%('Current PowerState is : ', CrntPS))
        self.TF.logger.Message("-----------------------------------------------------\n")

    def Do_PWS_Mgmt(self):
        self.TF.logger.Info("********  Set PWS Selected  ********  ")
        self.Set_PWS_Mgmt()
        self.TF.logger.Info("********  Get PWS IO Selected  ********  ")
        self.Get_PWS_Mgmt()

    def DoIOCmd(self,IOCmd):
        self.TF.logger.Info("********   IO Selected  ********  ")
        if IOCmd == 'WriteCmd':
            sendTypee = self.GetSendType()
            self.RWCLib.DoWrites(count = self.CommandCount, sendTypee = sendTypee)
        elif IOCmd == 'ReadCmd':
            sendTypee = self.GetSendType()
            self.RWCLib.DoRead(count = self.CommandCount, sendTypee = sendTypee)
        elif IOCmd == 'TrimCmd':
            sendTypee = self.GetSendType()
            self.RWCLib.DoTrim(count = self.CommandCount, lenMax = self.txLenMax, sendTypee = sendTypee)
        elif IOCmd == 'WZerosCmd':
            sendTypee = self.GetSendType()
            self.RWCLib.DoWr0(count = self.CommandCount, lenMax = self.txLenMax, sendTypee = sendTypee)
        elif IOCmd == 'WUCCmd':
            sendTypee = self.GetSendType()
            self.RWCLib.DoWUCmd(count = self.CommandCount, sendTypee = sendTypee)
        elif IOCmd == 'SCTPWriteFileSystem':
            sendTypee = self.GetSendType()
            self.RWCLib.DoWUCmd(count = self.CommandCount, sendTypee = sendTypee)

    def DoIOExcesies(self,IOsCmd, EventCmd ,ActionCmd):
        self.TF.logger.Info("********   IO Exceises Started  ********  ")
        if ServiceWrap.CMD_SEND_TYPE.SEND_IMMEDIATE == self.GetSendType():
            self.setSendType(ServiceWrap.CMD_SEND_TYPE.SEND_QUEUED)
        self.DoIOCmd(IOsCmd)
        self.DoEventToTrigger(EventCmd)
        self.DoIOCmd(IOsCmd)

    def DoFMT(self,EventCmd):
        self.TF.logger.Info("********   FMT Selected  ********  ")
        if (EventCmd == 'FMT_AFTER_0') or (EventCmd == 'FMT_BEFORE_0'):
            self.FormatCmd(SES=0)
        elif (EventCmd == 'FMT_AFTER_1') or (EventCmd == 'FMT_BEFORE_1'):
            self.FormatCmd(SES=1)
        elif('FMT2' == EventCmd):
            self.FormatCmd(SES=2)

    def SCTP_WriteFileSystem(self, EventCmd):
        self.TF.logger.Info("********  %s : Command A Selected  ********  "%(EventCmd))
        if (  (EventCmd == 'INFRA_IFS_IN_WRITE_FILE')):
            self.WriteFileSystem(fileID = 8, sectorCount = 8)

    def DoEventToTrigger(self, EventCmd):
        self.TF.logger.Info("********  %s : Command A Selected  ********  "%(EventCmd))
        if (  (EventCmd == 'FMT_AFTER_0') or (EventCmd == 'FMT_BEFORE_0') or (EventCmd == 'FMT_AFTER_1') or (EventCmd == 'FMT_BEFORE_1')) :
            self.DoFMT(EventCmd)
        elif('SHUTDOWN_STATE_START' == EventCmd):
            isAsync, deleteQs = self.Get_DeletQ_AsyncFlags()
            self.GSDPowerCycleCmd(isAsync, deleteQs, self.GetShutdownType())
        elif('INFRA_IFS_IN_WRITE_FILE' == EventCmd):
            self.SCTP_WriteFileSystem(EventCmd)
        elif('All_PWS_WP' == EventCmd):
            self.Do_PWS_Mgmt()
        '''if('CntrlResetCmd_NSSR' == ActionCmd):
            self.ResetControllerCmd('NSSR')
        elif('CntrlResetCmd_DisableCtrl' == ActionCmd):
            self.ResetControllerCmd('disablectrl')
        elif('CntrlResetCmd_DeleteQs' == ActionCmd):
            self.ResetControllerCmd('deleteq')
        elif('CntrlResetCmd_shutDown' == ActionCmd):
            self.ResetControllerCmd('shutdown')
        elif('PowerCycle_PA' == ActionCmd):
            isAsync, deleteQs = self.Get_DeletQ_AsyncFlags()
            self.AbortPowerCycleCmd(isAsync, deleteQs)
        elif('PowerCycle_UGSD' == ActionCmd):
            isAsync, deleteQs = self.Get_DeletQ_AsyncFlags()
            self.UGSDPowerCycleCmd(isAsync, deleteQs)
        elif('WriteCmd' == ActionCmd):
            self.RWCLib.DoWrites(count = 1, ErrorExpected = True)'''

    def GetSendType(self):
        sendType = self.sendType
        return sendType

    def setSendType(self, sendType):
        self.sendType = sendType

    def Get_DeletQ_AsyncFlags(self):
        isAsync = self.isAsync
        deleteQs = self.deleteQs
        return isAsync, deleteQs

    def set_DeletQ_Async_GSD(self,isAsync, deleteQs):
        self.isAsync = isAsync
        self.deleteQs = deleteQs

    def Set_DeletQ_AsyncFlags(self,var):
        if var == 0:
            self.isAsync = False
            self.deleteQs = False
        if var == 1:
            self.isAsync = True
            self.deleteQs = False
        '''
        if var == 2:
            self.isAsync = False
            self.deleteQs = False
        if var == 3:
            self.isAsync = True
            self.deleteQs = False
            '''
    def setShutdownType(self, ShutdownType):
        self.ShutdownType = ShutdownType

    def GetShutdownType(self):
        if self.ShutdownType == 0:
            return NVMeWrap.NORMAL_SHDN
        elif self.ShutdownType == 1:
            return NVMeWrap.ABRUPT_SHDN

