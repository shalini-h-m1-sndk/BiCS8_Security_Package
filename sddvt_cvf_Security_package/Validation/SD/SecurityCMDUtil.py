
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

from builtins import object
import sys, os, time, shutil, datetime, random, string, subprocess, csv
from array import *

import CTFServiceWrapper as ServiceWrap
#import NVMeCMDWrapper as NVMeWrap
import Core.ValidationError as ValidationError

#import Validation.NVMe_TestFixture as TestFixture
#import Validation.NVMe_TestParams as TP

#**************************************************************************************************************
##
# @brief Runs all the variations in the testObject
# @details
# @return None
# @exception None
#**************************************************************************************************************
class SECUCMDUtil(object):

    cardMap = dict()
    #readBuffer = ServiceWrap.Buffer.CreateBuffer(1)
    def __init__(self):
        pass

        #self.TF = TestFixture.TestFixture()
        #self.configParser = self.TF.testSession.GetConfigInfo()
        #self.errorManager = self.TF.testSession.GetErrorManager()

        #self.dataTrackEnabled = False
        #if int(self.configParser.GetValue('datatracking_enabled', 0)[0]):
            #self.dataTrackEnabled = True

        #self.patternDict = dict()
        #self.patternTypes = [ServiceWrap.ALL_0, ServiceWrap.ALL_1, ServiceWrap.BYTE_REPEAT, ServiceWrap.RANDOM]

        #self.modelPowerParams = ServiceWrap.MODEL_POWER_PARAMS()
        #self.modelPowerParams.delayTimeInNanaSec = 1000
        #self.modelPowerParams.railID = 0
        #self.modelPowerParams.transitionTimeInNanoSec = 1000

        #self.sectorSize = int(self.configParser.GetValue('sector_size_in_bytes', 0)[0])

        #self.sCCP = 0x01
        #self.sPSP = 0x7FFE
        #self.lEN = 4096
        #self.nSSF = 0x00
        #self.NSID = 0x01
        #self.protocolSpecificBuff = ServiceWrap.Buffer.CreateBuffer(20, patternType = ServiceWrap.ALL_0, isSector = False)
        #self.protocolSpecificBuff.SetByte(0, self.sCCP)
        #self.protocolSpecificBuff.SetTwoBytes(1, self.sPSP)
        #self.protocolSpecificBuff.SetByte(3, self.nSSF)
        #self.protocolSpecificBuff.SetFourBytes(4, self.lEN)



    #def CallBackRecv(self,ErrorGroup,ErrorNumber):

        #self.TF.logger.Info("", '------------- CallBack ----------------\n')

        #assert(ErrorGroup == 0xFF24 and ErrorNumber == 0x4204), '"Fail: Oustanding Data \n'
        #if ErrorGroup == 0xFF24 and ErrorNumber == 0x4204:
            ##self.errorManager.ClearContinueOnException(ErrorGroup, ErrorNumber)
            #self.errorManager.ClearAllErrors(ErrorGroup, ErrorNumber)
            #self.TF.logger.Info("","!!!Clearing error :: ErrorGroup == 0xFF24 and ErrorNumber == 0x4204 !!!")
            #self.sCCP = 0x01
            #self.sPSP = 0x7FFE
            #self.lEN = 4096
            #self.nSSF = 0x00
            #self.NSID = 0x01
            #self.protocolSpecificBuffRecv = ServiceWrap.Buffer.CreateBuffer(20, patternType = ServiceWrap.ALL_0, isSector = False)
            #self.protocolSpecificBuffRecv.SetByte(0, self.sCCP)
            #self.protocolSpecificBuffRecv.SetTwoBytes(1, self.sPSP)
            #self.protocolSpecificBuffRecv.SetByte(3, self.nSSF)
            #self.protocolSpecificBuffRecv.SetFourBytes(4, self.lEN)
            #protocolSpecificBuff=self.protocolSpecificBuffRecv
        #self.TF.logger.Info("", '---------------------------------------\n')

    #def PostLeve0(self, sndTyp):

        ##RdTable = ServiceWrap.ReadTable()
        #try:
            #Level0 = ServiceWrap.Level0Discovery(0x01, pProtocolSpecific=None, sendType=sndTyp)
        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        #status = False
        #status = self.TF.threadPool.WaitForThreadCompletion()
        #if False == status:
            #self.__CheckForErrors()
            #raise ValidationError.TestFailError(self.fn, self.errorManager.GetAllFailureDescription())

        #return (Level0)


    #def PropertiesExchange(self, MaxComPacketSize, MaxResponseComPacketSize, MaxPacketSize, MaxIndTokenSize, MaxPackets, MaxSubpackets, MaxMethods, IsASyncMode, cmdDir, sndType):

        ##Register Call back----------------------------------------------------------------------------------------
        ##self.errorManager.RegisterCallback(self.CallBackRecv)
        ##----------------------------------------------------------------------------------------------------------

        #if(cmdDir == ServiceWrap.SECURITY_RECEIVE):

            #self.sCCP = 0x01
            #self.sPSP = 0x7FFE
            #self.lEN = 4096
            #self.nSSF = 0x00
            #self.NSID = 0x01
            #self.protocolSpecificBuffRecv = ServiceWrap.Buffer.CreateBuffer(20, patternType = ServiceWrap.ALL_0, isSector = False)
            #self.protocolSpecificBuffRecv.SetByte(0, self.sCCP)
            #self.protocolSpecificBuffRecv.SetTwoBytes(1, self.sPSP)
            #self.protocolSpecificBuffRecv.SetByte(3, self.nSSF)
            #self.protocolSpecificBuffRecv.SetFourBytes(4, self.lEN)
            #protocolSpecificBuff=self.protocolSpecificBuffRecv
        #else:
            #protocolSpecificBuff = self.protocolSpecificBuff

        #ComID = 0x7FFE
        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #TperExchng = ServiceWrap.PropertiesExchange(uiComId=ComID, uiMaxComPacketSize=MaxComPacketSize, uiMaxResponseComPacketSize=MaxResponseComPacketSize, uiMaxPacketSize=MaxPacketSize, uiMaxIndTokenSize=MaxIndTokenSize, uiMaxPackets=MaxPackets, uiMaxSubpackets=MaxSubpackets, uiMaxMethods=MaxMethods, pProtocolSpecific=protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #TperExchng = ServiceWrap.PropertiesExchange(uiComId=ComID, uiMaxComPacketSize=MaxComPacketSize, uiMaxResponseComPacketSize=MaxResponseComPacketSize, uiMaxPacketSize=MaxPacketSize, uiMaxIndTokenSize=MaxIndTokenSize, uiMaxPackets=MaxPackets, uiMaxSubpackets=MaxSubpackets, uiMaxMethods=MaxMethods, pProtocolSpecific=protocolSpecificBuff,isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #else:
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #TperExchng = ServiceWrap.PropertiesExchange(uiComId=ComID, uiMaxComPacketSize=MaxComPacketSize, uiMaxResponseComPacketSize=MaxResponseComPacketSize, uiMaxPacketSize=MaxPacketSize, uiMaxIndTokenSize=MaxIndTokenSize, uiMaxPackets=MaxPackets, uiMaxSubpackets=MaxSubpackets, uiMaxMethods=MaxMethods, pProtocolSpecific=protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)

        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        #self.TF.logger.Message("------------------------------------------------------------\n")
        #Status = TperExchng.response.status#
        #while(Status!=0):
            #try:
                #TperExchng = ServiceWrap.PropertiesExchange(pProtocolSpecific=protocolSpecificBuff, isAsync=False,  cmdDirection=ServiceWrap.SECURITY_RECEIVE, sendType=ServiceWrap.CMD_SEND_TYPE.SEND_IMMEDIATE)
                #self.TF.logger.Message("Response Buffer: Revert Tper--------------------------\n")
                #Status = TperExchng.response.status
                #self.TF.logger.Message("%-35s: %s"%('Status Code: ', Status))
            #except ValidationError.CVFExceptionTypes as ex:
                #self.TF.logger.Fatal("Failed to Post the Security Rec. Exception Message is ->\n %s "%ex.GetFailureDescription())
                #self.TF.logger.FlushAllMsg()
                #assert(True == False), ex.GetFailureDescription()

        #if(0):
            #status = False
            #status = self.TF.threadPool.WaitForThreadCompletion()
            #if False == status:
                #self.__CheckForErrors()
                #raise ValidationError.TestFailError(self.fn, self.errorManager.GetAllFailureDescription())

        #return (TperExchng)

    #def PostStartSession(self, SPID, HostChallenge, HostSigningCert, IsASyncMode, cmdDir, sndType = ServiceWrap.SEND_IMMEDIATE):

        #ComID = 0x7FFE
        #HSN=1
        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #StartSession = ServiceWrap.StartSession(uiHostSessionID=HSN, uiComId=ComID, szSPID=SPID, Write=1, szHostChallenge=HostChallenge, szHostSigningAuthority=HostSigningCert, dwTimeOut=20000, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #StartSession = ServiceWrap.StartSession(uiHostSessionID=HSN, uiComId=ComID, szSPID=SPID, Write=1, szHostChallenge=HostChallenge, szHostSigningAuthority=HostSigningCert, dwTimeOut=20000, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #else:
                #sndType=sndType
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #StartSession = ServiceWrap.StartSession(uiHostSessionID=HSN, uiComId=ComID, szSPID=SPID, Write=1, szHostChallenge=HostChallenge, szHostSigningAuthority=HostSigningCert, dwTimeOut=20000, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        #status = StartSession.response.status
        #if(status!=0):
            #StartSession = ServiceWrap.StartSession(pProtocolSpecific=self.protocolSpecificBuff, isAsync=False,  cmdDirection=ServiceWrap.SECURITY_RECEIVE, sendType=ServiceWrap.CMD_SEND_TYPE.SEND_IMMEDIATE)
        #else:
            #status = False
            #status = self.TF.threadPool.WaitForThreadCompletion()
            #if False == status:
                #self.__CheckForErrors()
                #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #return (StartSession)

    #def PostGetMSIDPIN(self, TSN, IsASyncMode, cmdDir, sndType = ServiceWrap.SEND_IMMEDIATE):
        #self.TF.logger.Message("Get MSID PIN from C-PIN table---------------------------------\n")
        #InvoikingId = "C_PIN_MSID"  # 0x0B00008402 Invoking-UID C_PIN_MSID UID <00 00 00 0B 00 00 84 02>
        #HSN=1
        #ComID = 0x7FFE
        #StartColumn = 3  #<PIN>
        #EndColumn = 3    #<PIN>
        #MethodUID = "GET" #  Method-UID Get Method UID -- <00 00 00 06 00 00 00 16>
        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #GetPin = ServiceWrap.GetPin(szInvokingId= InvoikingId, uiHSN = HSN, uiTSN = TSN, uiComId = ComID , uiStartColumn = StartColumn, uiEndColumn = EndColumn, szMethodUID = MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #GetPin = ServiceWrap.GetPin(szInvokingId= InvoikingId, uiHSN = HSN, uiTSN = TSN, uiComId = ComID , uiStartColumn = StartColumn, uiEndColumn = EndColumn, szMethodUID = MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #else:
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #GetPin = ServiceWrap.GetPin(szInvokingId= InvoikingId, uiHSN = HSN, uiTSN = TSN, uiComId = ComID , uiStartColumn = StartColumn, uiEndColumn = EndColumn, szMethodUID = MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #status = False
        #status = self.TF.threadPool.WaitForThreadCompletion()
        #if False == status:
            #self.__CheckForErrors()
            #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #return (GetPin)

    #def PostGetLifeCycle(self, InvokingId, TSN, IsASyncMode, cmdDir, sndType = ServiceWrap.SEND_IMMEDIATE):
        ##InvokingId = "LOCKING_SP" #LockingSP 0x020500000002 Invoking-UID LockingSP UID <00 00 02 05 00 00 00 02>
        #HSN=1
        #ComID = 0x7FFE
        #StartColumn = 6  #<LifeCycle> <6>
        #EndColumn = 6  #<LifeCycle> <6>
        #MethodUID=  "GET" #00 00 00 06 00 00 00 16   Method-UID Get Method UID <00 00 00 06 00 00 00 16>
        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #GetLifeCycle = ServiceWrap.GetLifeCycle(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId= ComID, uiStartColumn=StartColumn, uiEndColumn=EndColumn,szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #GetLifeCycle = ServiceWrap.GetLifeCycle(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId= ComID, uiStartColumn=StartColumn, uiEndColumn=EndColumn,szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #else:
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #GetLifeCycle = ServiceWrap.GetLifeCycle(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId= ComID, uiStartColumn=StartColumn, uiEndColumn=EndColumn,szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #status = False
        #status = self.TF.threadPool.WaitForThreadCompletion()
        #if False == status:
            #self.__CheckForErrors()
            #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #return (GetLifeCycle)

    #def PostActivateLockingSP(self, InvokingId, TSN, IsASyncMode, cmdDir, sndType = ServiceWrap.SEND_IMMEDIATE):
        #ComID = 0x7FFE
        #HSN = 1
        ##InvokingId= "LOCKING_SP" #"0x020500000002" # ?Invoking UID LockingSP_UID -- <00 00 02 05 00 00 00 02>
        #MethodUID= "ACTIVATE"    #"0x0600000203" #??# Activate UID- Method ID-- <00 00 00 06 00 00 02 03>
        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #ActivateLockingSP = ServiceWrap.ActivateLockingSP(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #self.TF.logger.Message("Sent Type is: SEND_QUEUED  \n")
                #ActivateLockingSP = ServiceWrap.ActivateLockingSP(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #else:
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #ActivateLockingSP = ServiceWrap.ActivateLockingSP(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #status = False
        #status = self.TF.threadPool.WaitForThreadCompletion()
        #if False == status:
            #self.__CheckForErrors()
            #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #return(ActivateLockingSP)

    #def PostSetPin(self, InvokingId, TSN, PIN,  IsASyncMode, cmdDir, sndType = ServiceWrap.SEND_IMMEDIATE):
        #InvokingId = "C_PIN_SID" # <Invoking-UID C_PIN table SID row UID> -- <00 00 00 0B 00 00 00 01>
        #Method = "SET" #"0x0600000017"   #<Method-UID Set Method UID> -- <00 00 00 06 00 00 00 17>
        #ComID = 0x7FFE
        #HSN =1
        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #SetPin = ServiceWrap.SetPin(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szPin=PIN, szMethodUID=Method, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #SetPin = ServiceWrap.SetPin(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szPin=PIN, szMethodUID=Method, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #else:
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #SetPin = ServiceWrap.SetPin(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szPin=PIN, szMethodUID=Method, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #status = False
        #status = self.TF.threadPool.WaitForThreadCompletion()
        #if False == status:
            #self.__CheckForErrors()
            #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #return(SetPin)

    #def PostLockOrUnlockReadAndWriteOnGlobalOrLocalRange(self, InvokingId, TSN, RdLock_enb, WRLock_enb, RD_locked, WR_locked, ResetTypeObj, IsASyncMode, cmdDir,  sndType = ServiceWrap.SEND_IMMEDIATE):
        #HSN=1
        #ComID = 0x7FFE
        #MethodUID="SET"
        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #LockOrUnlockReadAndWriteOnGlobalOrLocalRange = ServiceWrap.LockOrUnlockReadAndWriteOnGlobalOrLocalRange(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, readLock_enabled=RdLock_enb, writeLock_enabled=WRLock_enb, read_locked=RD_locked, write_locked=WR_locked, AllowedResetTypes=ResetTypeObj, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #LockOrUnlockReadAndWriteOnGlobalOrLocalRange = ServiceWrap.LockOrUnlockReadAndWriteOnGlobalOrLocalRange(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, readLock_enabled=RdLock_enb, writeLock_enabled=WRLock_enb, read_locked=RD_locked, write_locked=WR_locked, AllowedResetTypes=ResetTypeObj, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #else:
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #LockOrUnlockReadAndWriteOnGlobalOrLocalRange = ServiceWrap.LockOrUnlockReadAndWriteOnGlobalOrLocalRange(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, readLock_enabled=RdLock_enb, writeLock_enabled=WRLock_enb, read_locked=RD_locked, write_locked=WR_locked, AllowedResetTypes=ResetTypeObj, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #status = False
        #status = self.TF.threadPool.WaitForThreadCompletion()
        #if False == status:
            #self.__CheckForErrors()
            #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #return(LockOrUnlockReadAndWriteOnGlobalOrLocalRange)

    #def PostGetGlobalOrLocalRangeConfiguration(self, InvokingId, TSN, StartColumn,  EndColumn, IsASyncMode, cmdDir, sndTyp = ServiceWrap.SEND_IMMEDIATE):
        #HSN =1
        #ComID = 0x7FFE
        #InvoikingId = "GLOBAL_RANGE_UID" #0x80200000001
        #MethodUID = "GET"
        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #GetGlobalOrLocalRangeConfiguration = ServiceWrap.GetGlobalOrLocalRangeConfiguration(szInvokingId=InvoikingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartColumn=StartColumn, uiEndColumn=EndColumn, szMethodUID=MethodUID,  pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #GetGlobalOrLocalRangeConfiguration = ServiceWrap.GetGlobalOrLocalRangeConfiguration(szInvokingId=InvoikingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartColumn=StartColumn, uiEndColumn=EndColumn, szMethodUID=MethodUID,  pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #else:
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #GetGlobalOrLocalRangeConfiguration = ServiceWrap.GetGlobalOrLocalRangeConfiguration(szInvokingId=InvoikingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartColumn=StartColumn, uiEndColumn=EndColumn, szMethodUID=MethodUID,  pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #status = False
        #status = self.TF.threadPool.WaitForThreadCompletion()
        #if False == status:
            #self.__CheckForErrors()
            #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #return(GetGlobalOrLocalRangeConfiguration)


    #def PostGenKey(self, InvokingId, TSN, IsASyncMode, cmdDir, sndType = ServiceWrap.SEND_IMMEDIATE):
        #HSN =1
        #ComID = 0x7FFE
        ##InvokingId = "K_AES_256_GLOBALRANGE_KEY" #0x080600000001
        #MethodUID = "GENKEY"

        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #GenKey = ServiceWrap.GenKey(szInvokingId=InvokingId, uiHSN= HSN, uiTSN=TSN, uiComId=ComID, szMethodUID=MethodUID,  pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)

            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #GenKey = ServiceWrap.GenKey(szInvokingId=InvokingId, uiHSN= HSN, uiTSN=TSN, uiComId=ComID, szMethodUID=MethodUID,  pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #else:
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #GenKey = ServiceWrap.GenKey(szInvokingId=InvokingId, uiHSN= HSN, uiTSN=TSN, uiComId=ComID, szMethodUID=MethodUID,  pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #status = False
        #status = self.TF.threadPool.WaitForThreadCompletion()
        #if False == status:
            #self.__CheckForErrors()
            #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #return(GenKey)


    #def PostTCG_Get(self, InvokingId, TSN, StartColumn, EndColumn, IsASyncMode, cmdDir, sndType = ServiceWrap.SEND_IMMEDIATE):
        #HSN =1
        #ComID = 0x7FFE
        #MethodUID=  "GET" #00 00 00 06 00 00 00 16   Method-UID Get Method UID <00 00 00 06 00 00 00 16>

        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #TCG_Get = ServiceWrap.TCG_Get(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartColumn=StartColumn, uiEndColumn=EndColumn, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #TCG_Get = ServiceWrap.TCG_Get(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartColumn=StartColumn, uiEndColumn=EndColumn, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #else:
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #TCG_Get = ServiceWrap.TCG_Get(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartColumn=StartColumn, uiEndColumn=EndColumn, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)

        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #status = False
        #status = self.TF.threadPool.WaitForThreadCompletion()
        #if False == status:
            #self.__CheckForErrors()
            #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #return(TCG_Get)

    #def PostTCG_Set(self, InvokingId, TSN, DICT, WHERE, IsASyncMode, cmdDir, sndType = ServiceWrap.SEND_IMMEDIATE):
        #MethodUID = "SET" #"0x0600000017"   #<Method-UID Set Method UID> -- <00 00 00 06 00 00 00 17>
        #ComID = 0x7FFE
        #HSN = 1
        #Where =WHERE
        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #TCGSET = ServiceWrap.TCG_Set(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, ucWhere=Where, mapOfValues=DICT, szMethodUID=MethodUID, pProtocolSpecific=None, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #TCGSET = ServiceWrap.TCG_Set(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, ucWhere=Where, mapOfValues=DICT, szMethodUID=MethodUID, pProtocolSpecific=None, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #else:
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #self.TF.logger.Message("Sent Type is: SEND_NONE and  (Executed in Direct-mode)  \n")
                #TCGSET = ServiceWrap.TCG_Set(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, ucWhere=Where, mapOfValues=DICT, szMethodUID=MethodUID, pProtocolSpecific=None, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #status = False
        #status = self.TF.threadPool.WaitForThreadCompletion()
        #if False == status:
            #self.__CheckForErrors()
            #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #return(TCGSET)

    #def PostMBRStatsEnb(self, TSN, StartColumn, EndColumn, IsASyncMode, cmdDir, sndType = ServiceWrap.SEND_IMMEDIATE):
        #HSN =1
        #ComID = 0x7FFE
        #InvokingId = "MBR_CONTROL_UID"
        #MethodUID=  "GET"
        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #GetMBRControlDoneEnable = ServiceWrap.GetMBRControlDoneEnable(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartColumn=StartColumn, uiEndColumn=EndColumn, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #GetMBRControlDoneEnable = ServiceWrap.GetMBRControlDoneEnable(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartColumn=StartColumn, uiEndColumn=EndColumn, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #else:
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #GetMBRControlDoneEnable = ServiceWrap.GetMBRControlDoneEnable(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartColumn=StartColumn, uiEndColumn=EndColumn, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)

        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #status = False
        #status = self.TF.threadPool.WaitForThreadCompletion()
        #if False == status:
            #self.__CheckForErrors()
            #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #return(GetMBRControlDoneEnable)

    #def PostEnableDisableMBR(self, TSN, actnOnMBR, enbMBR, ResetTypeObj, IsASyncMode, cmdDir, sndType = ServiceWrap.SEND_IMMEDIATE):
        #HSN =1
        #ComID = 0x7FFE
        #InvokingId = "MBR_CONTROL_UID"
        #MethodUID=  "SET"
        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #self.TF.logger.Message("Sent Type is: SEND_IMMEDIATE  \n")
                #EnableDisableMBR = ServiceWrap.EnableDisableMBR(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, actionOnMBR=actnOnMBR, enableMBR=enbMBR, AllowedResetTypes=ResetTypeObj, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #self.TF.logger.Message("Sent Type is: SEND_QUEUED  \n")
                #EnableDisableMBR = ServiceWrap.EnableDisableMBR(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, actionOnMBR=actnOnMBR, enableMBR=enbMBR, AllowedResetTypes=ResetTypeObj, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #else:
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #EnableDisableMBR = ServiceWrap.EnableDisableMBR(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, actionOnMBR=actnOnMBR, enableMBR=enbMBR, AllowedResetTypes=ResetTypeObj, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)

        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #status = False
        #status = self.TF.threadPool.WaitForThreadCompletion()
        #if False == status:
            #self.__CheckForErrors()
            #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #return(EnableDisableMBR)

    #def PostConfigureLockingFeatureForLockingRanges(self, InvokingId, TSN, RangeStart, RangeLength, rdLock_en, wrLock_en, IsASyncMode, cmdDir, sndType = ServiceWrap.SEND_IMMEDIATE):
        #HSN =1
        #ComID = 0x7FFE
        #MethodUID='SET'
        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #ConfigureLockingFeatureForLockingRanges = ServiceWrap.ConfigureLockingFeatureForLockingRanges(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiRangeStart=RangeStart, uiRangeLength=RangeLength, readLock_enabled=rdLock_en, writeLock_enabled=wrLock_en, szMethodUID=MethodUID,  pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)

            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #ConfigureLockingFeatureForLockingRanges = ServiceWrap.ConfigureLockingFeatureForLockingRanges(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiRangeStart=RangeStart, uiRangeLength=RangeLength, readLock_enabled=rdLock_en, writeLock_enabled=wrLock_en, szMethodUID=MethodUID,  pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)

            #else:
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #ConfigureLockingFeatureForLockingRanges = ServiceWrap.ConfigureLockingFeatureForLockingRanges(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiRangeStart=RangeStart, uiRangeLength=RangeLength, readLock_enabled=rdLock_en, writeLock_enabled=wrLock_en, szMethodUID=MethodUID,  pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)

        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #status = False
        #status = self.TF.threadPool.WaitForThreadCompletion()
        #if False == status:
            #self.__CheckForErrors()
            #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #return(ConfigureLockingFeatureForLockingRanges)


    #def PostGetGlobalOrLocalRangeConfiguration(self, InvokingId, TSN, StartColumn,  EndColumn, IsASyncMode, cmdDir, sndType= ServiceWrap.SEND_IMMEDIATE):
        #HSN =1
        #ComID = 0x7FFE
        #MethodUID = "GET"
        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #GetGlobalOrLocalRangeConfiguration = ServiceWrap.GetGlobalOrLocalRangeConfiguration(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartColumn=StartColumn, uiEndColumn=EndColumn, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #GetGlobalOrLocalRangeConfiguration = ServiceWrap.GetGlobalOrLocalRangeConfiguration(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartColumn=StartColumn, uiEndColumn=EndColumn, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #else:
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #GetGlobalOrLocalRangeConfiguration = ServiceWrap.GetGlobalOrLocalRangeConfiguration(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartColumn=StartColumn, uiEndColumn=EndColumn, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #status = False
        #status = self.TF.threadPool.WaitForThreadCompletion()
        #if False == status:
            #self.__CheckForErrors()
            #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #return(GetGlobalOrLocalRangeConfiguration)

    #def PostStartTransaction(self, TSN, IsASyncMode, cmdDir, sndType = ServiceWrap.SEND_IMMEDIATE):
        #HSN =1
        #ComID = 0x7FFE
        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #StartTrans = ServiceWrap.StartTransaction(uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szToken=0xFB, dwTimeOut=20000, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #StartTrans = ServiceWrap.StartTransaction(uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szToken=0xFB, dwTimeOut=20000, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #else:
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #StartTrans = ServiceWrap.StartTransaction(uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szToken=0xFB, dwTimeOut=20000, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #OnlyPush = 1
        #if(OnlyPush):
            #status = False
            #status = self.TF.threadPool.WaitForThreadCompletion()
            #if False == status:
                #self.__CheckForErrors()
                #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #return(StartTrans)

    #def PostEndTransaction(self, TSN, StatusEndTrans, IsASyncMode, cmdDir, sndType = ServiceWrap.SEND_IMMEDIATE):
        #HSN =1
        #ComID = 0x7FFE
        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #EndTrans = ServiceWrap.EndTransaction(uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szToken=0xFC, ucStatus=StatusEndTrans, dwTimeOut=20000, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #EndTrans = ServiceWrap.EndTransaction(uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szToken=0xFC, ucStatus=StatusEndTrans, dwTimeOut=20000, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #else:
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #EndTrans = ServiceWrap.EndTransaction(uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szToken=0xFC, ucStatus=StatusEndTrans, dwTimeOut=20000, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #OnlyPush = 1
        #if(OnlyPush):
            #status = False
            #status = self.TF.threadPool.WaitForThreadCompletion()
            #if False == status:
                #self.__CheckForErrors()
                #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #return(EndTrans)

    #def PostWriteDataToByteTable(self, InvokingId, Where, length,  patrnID, TSN, IsASyncMode, cmdDir, sndType = ServiceWrap.SEND_IMMEDIATE):
        #HSN =1
        #ComID = 0x7FFE
        #DataToWrite=None
        #MethodUID='SET'
        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #WriteByteTable = ServiceWrap.WriteDataToByteTable(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, ucWhere=Where, lenData=length, patternID=patrnID, szDataToWrite=DataToWrite, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)

            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #WriteByteTable = ServiceWrap.WriteDataToByteTable(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, ucWhere=Where, lenData=length, patternID=patrnID, szDataToWrite=DataToWrite, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)

            #else:
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #WriteByteTable = ServiceWrap.WriteDataToByteTable(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, ucWhere=Where, lenData=length, patternID=patrnID, szDataToWrite=DataToWrite, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)

        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #status = False
        #status = self.TF.threadPool.WaitForThreadCompletion()
        #if False == status:
            #self.__CheckForErrors()
            #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #return(WriteByteTable)

    #def PostReadDataFromByteTable(self, InvokingId, TSN, StartRow, EndRow, IsASyncMode, cmdDir, sndType = ServiceWrap.SEND_IMMEDIATE):
        #HSN =1
        #ComID = 0x7FFE
        #DataToWrite=None
        #MethodUID='GET'
        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #ReadDStable = ServiceWrap.ReadDataFromByteTable(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartRow=StartRow, uiEndRow=EndRow, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)

            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #ReadDStable = ServiceWrap.ReadDataFromByteTable(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartRow=StartRow, uiEndRow=EndRow, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #else:
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #ReadDStable = ServiceWrap.ReadDataFromByteTable(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartRow=StartRow, uiEndRow=EndRow, szMethodUID=MethodUID, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)

        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #status = False
        #status = self.TF.threadPool.WaitForThreadCompletion()
        #if False == status:
            #self.__CheckForErrors()
            #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #return(ReadDStable)

    #def PostTPer_Reset(self,  IsASyncMode, cmdDir, sndType = ServiceWrap.SEND_IMMEDIATE):
        #NSID = 1
        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #ServiceWrap.TPerReset(uiNSID=NSID, pProtocolSpecific=None, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #ServiceWrap.TPerReset(uiNSID=NSID, pProtocolSpecific=None, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #else:
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #ServiceWrap.TPerReset(uiNSID=NSID, pProtocolSpecific=None, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")
        #status = False
        #status = self.TF.threadPool.WaitForThreadCompletion()
        #if False == status:
            #self.__CheckForErrors()
            #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #return(0)

    #def PostEndSession(self, TSN,  IsASyncMode, cmdDir, sndType = ServiceWrap.SEND_IMMEDIATE):
        #ComID = 0x7FFE
        #HSN = 1
        #TimeOUT = 200000
        #Token = 0xFA
        #try:
            #if(sndType == ServiceWrap.SEND_IMMEDIATE):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #EndSession = ServiceWrap.EndSession(uiHSN = HSN, uiTSN = TSN, uiComId = ComID, szToken= Token, dwTimeOut = TimeOUT, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #elif(sndType == ServiceWrap.SEND_QUEUED):
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #EndSession = ServiceWrap.EndSession(uiHSN = HSN, uiTSN = TSN, uiComId = ComID, szToken= Token, dwTimeOut = TimeOUT, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
            #else:
                #self.TF.logger.Message("%-35s: %s"%('Sent Type is: ', sndType))
                #EndSession = ServiceWrap.EndSession(uiHSN = HSN, uiTSN = TSN, uiComId = ComID, szToken= Token, dwTimeOut = TimeOUT, pProtocolSpecific=self.protocolSpecificBuff, isAsync=IsASyncMode, cmdDirection=cmdDir, sendType=sndType)
        #except ValidationError.CVFExceptionTypes as ex:
            #self.TF.logger.Fatal("Failed to Post the SECU-Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        #status = False
        #status = self.TF.threadPool.WaitForThreadCompletion()
        #if False == status:
            #self.__CheckForErrors()
            #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #return(EndSession)





    #def RevertTper(self):
        #SPID = "ADMIN_SP"  # <AdminSP UID> --<00 00 02 05 00 00 00 01>
        #HostSigningAuthority = "SID_UID"  #  Value <SID_UID> -- <00 00 00 09 00 00 00 06>
        #ComID = 0x07FFE

        #try:
            #NewPasswd =  ServiceWrap.Buffer.CreateBuffer(9, patternType = ServiceWrap.ALL_0, isSector = False)
            #index = 0
            #byteval = 0x50 #P
            #NewPasswd.SetByte(index, byteval)
            #index = index+1
            #byteval = 0x61 #a
            #NewPasswd.SetByte(index, byteval)
            #index = index+1
            #byteval = 0x73 #s
            #NewPasswd.SetByte(index, byteval)
            #index = index+1
            #byteval = 0x73 #s
            #NewPasswd.SetByte(index, byteval)
            #index = index+1
            #byteval = 0x77 #w
            #NewPasswd.SetByte(index, byteval)
            #index = index+1
            #byteval = 0x6f #o
            #NewPasswd.SetByte(index, byteval)
            #index = index+1
            #byteval = 0x72 #r
            #NewPasswd.SetByte(index, byteval)
            #index = index+1
            #byteval = 0x64 #d
            #NewPasswd.SetByte(index, byteval)
            #index = index+1
            #byteval = 0x31 #1
            #NewPasswd.SetByte(index, byteval)
        #except self.TF.CVFExceptions as ex:
            #self.TF.logger.Fatal("Failed to Create-Buiffer. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #self.TF.logger.FlushAllMsg()
            #assert(True == False), ex.GetFailureDescription()
        #try:
            #StartSession = ServiceWrap.StartSession( uiHostSessionID=1, uiComId=ComID, szSPID=SPID, Write=1, szHostChallenge=NewPasswd, szHostSigningAuthority=HostSigningAuthority,  pProtocolSpecific=None)
            #StartSession.Execute()
            #StartSession.HandleOverlappedExecute()
            #StartSession.HandleAndParseResponse()
        #except self.TF.CVFExceptions as ex:
            #self.TF.logger.Fatal("Failed to Post the Start-Session USER Passwd Exception Message is ->\n %s "%ex.GetFailureDescription())
            #self.TF.logger.FlushAllMsg()
            #assert(True == False), ex.GetFailureDescription()
        #self.TF.logger.Message("InPut Buffer: SID New Passwd---------------------------------\n")
        #StartSession.pReqBuffer.PrintToLog()
        #self.TF.logger.Message("Response Buffer: SID New Passwd-------------------------------\n")
        #StartSession.pRespBuffer.PrintToLog()
        #self.TSN = StartSession.pRespBuffer.GetTwoBytesToInt(0x4E, False)
        #self.TSN = StartSession.response.TSN
        #Status = StartSession.response.status
        #self.TF.logger.Message("%-35s: %s"%('Status Code: ', Status))
        #assert(Status == 0)
        ##Read Table LifeCycleState--------------------------------------------------
        #self.TF.logger.Message("Issue LifeCycleState Command ------------------------------------\n")
        #InvokingId = "LOCKING_SP" #LockingSP 0x020500000002 Invoking-UID LockingSP UID <00 00 02 05 00 00 00 02>
        #HSN = 1
        #TSN = self.TSN
        #StartColumn = 6  #<LifeCycle> <6>
        #EndColumn = 6  #<LifeCycle> <6>
        #MethodUID=  "GET" #00 00 00 06 00 00 00 16   Method-UID Get Method UID <00 00 00 06 00 00 00 16>
        #try:
            #GetLifeCycle = ServiceWrap.GetLifeCycle(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId= ComID, uiStartColumn=StartColumn, uiEndColumn=EndColumn,szMethodUID=MethodUID, pProtocolSpecific=None)
            #GetLifeCycle.Execute()
            #GetLifeCycle.HandleOverlappedExecute()
            #GetLifeCycle.HandleAndParseResponse()
            ##ResLfCycle = GetLifeCycle.pRespBufferData
        #except self.TF.CVFExceptions as ex:
            #self.TF.logger.Fatal("Failed to Post the Get LIfe Cycle Exception Message is ->\n %s "%ex.GetFailureDescription())
            #self.TF.logger.FlushAllMsg()
            #assert(True == False), ex.GetFailureDescription()
        #self.TF.logger.Message("InPut Buffer: get LIfe Cycle-------------------------------\n")
        #GetLifeCycle.pRequestBufferData.PrintToLog()
        #self.TF.logger.Message("Response Buffer: get LIfe Cycle-----------------------------\n")
        #GetLifeCycle.pRespBufferData.PrintToLog()
        #Status = GetLifeCycle.response.status
        #self.TF.logger.Message("%-35s: %s"%('Status Code: ', Status))
        #assert(Status == 0)
        ##-------------------------------------------------------------------------------------
        ##Revert Tper--------------------------------------------------------------------------
        #self.TF.logger.Message("Issue Rever Tper Command ------------------------------------\n")
        #InvokingId="ADMIN_SP"
        #MethodUID="REVERT"  # "0x0600000202" #RevertTper: Method UID--<00 00 00 06 00 00 02 02> #??
        #try:
            #RevrtTper = ServiceWrap.RevertTPer("ADMIN_SP", HSN, TSN, 0x7FFE, "REVERT", pProtocolSpecific=None)
            ##WRTable.RevertTPer("ADMIN_SP", HSN, TSN, 0x7FFE, "REVERT")
            #RevrtTper.Execute()
            #RevrtTper.HandleOverlappedExecute()
            #RevrtTper.HandleAndParseResponse()
        #except self.TF.CVFExceptions as ex:
            #self.TF.logger.Fatal("Failed to Post the Security Rec. Exception Message is ->\n %s "%ex.GetFailureDescription())
            #self.TF.logger.FlushAllMsg()
            #assert(True == False), ex.GetFailureDescription()
        #self.TF.logger.Message("Input Buffer: Revert Tper----------------------------\n")
        #RevrtTper.pReqBuffer.PrintToLog()
        #self.TF.logger.Message("Response Buffer: Revert Tper--------------------------\n")
        #RevrtTper.pRespBuffer.PrintToLog()
        #self.TF.logger.Message("*****************************************************\n")
    #def PostTCG_GET(self, InvokingId, TSN, StartCol, EndCol,  sndType = ServiceWrap.SEND_IMMEDIATE):
        #MethodUID=  "GET" #00 00 00 06 00 00 00 16   Method-UID Get Method UID <00 00 00 06 00 00 00 16>
        #ComID = 0x7FFE
        #HSN = 1
        #if(sndType == ServiceWrap.SEND_IMMEDIATE):
            #self.TF.logger.Message("Sent Type is: SEND_IMMEDIATE  \n")
            #TCG_Get = ServiceWrap.TCG_Get(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartColumn=StartCol, uiEndColumn=EndCol, szMethodUID=MethodUID, pProtocolSpecific=None, sendType=sndType)
        #elif(sndType == ServiceWrap.SEND_QUEUED):
            #self.TF.logger.Message("Sent Type is: SEND_QUEUED  \n")
            #TCG_Get = ServiceWrap.TCG_Get(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartColumn=StartCol, uiEndColumn=EndCol, szMethodUID=MethodUID, pProtocolSpecific=None, sendType=sndType)
            #status = False
            #status = self.TF.threadPool.WaitForThreadCompletion()
            #if False == status:
                #self.__CheckForErrors()
                #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #else:
            #SendType=ServiceWrap.CMD_SEND_TYPE.SEND_NONE
            #self.TF.logger.Message("Sent Type is: SEND_NONE and  (Executed in Direct-mode)  \n")
            #TCG_Get = ServiceWrap.TCG_Get(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartColumn=StartCol, uiEndColumn=EndCol, szMethodUID=MethodUID, pProtocolSpecific=None, sendType=sndType)
            #TCG_Get.Execute()
            #TCG_Get.pRequestBufferData.PrintToLog()
            #TCG_Get.HandleOverlappedExecute()
            #TCG_Get.HandleAndParseResponse()
        ##Response validation
        #Status = TCG_Get.response.status
        #self.TF.logger.Message("%-35s: %s"%('Status Code: ', Status))
        #assert(Status == ServiceWrap.TCG_STATUS_CODE.SUCCESS)
        ##Request and Reseponse buffer------------
        #self.TF.logger.Message("Input-Buffer: TCG-Get Requeset Buffer:--------------------\n")
        #TCG_Get.pRequestBufferData.PrintToLog() # ???????????????
        #self.TF.logger.Message("Output-Buffer: TCG-Get Response Buffer:--------------------\n")
        #TCG_Get.pRespBufferData.PrintToLog() #????????????
        #ResBuff =  ServiceWrap.Buffer.CreateBuffer(512, patternType = ServiceWrap.ALL_0, isSector = False)
        #ResBuff.FullCopy(TCG_Get.pRespBufferData)   #???????????????
        #return (ResBuff)
        ##return (ServiceWrap.TCG_Get(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartColumn=StartCol, uiEndColumn=EndCol, szMethodUID=MethodUID, sendType=ServiceWrap.CMD_SEND_TYPE.SEND_NONE))
    #def PostTCG_SET(self, InvokingId, TSN, DICT, WHERE, sndType = ServiceWrap.SEND_IMMEDIATE):
        #MethodUID = "SET" #"0x0600000017"   #<Method-UID Set Method UID> -- <00 00 00 06 00 00 00 17>
        #ComID = 0x7FFE
        #HSN = 1
        #Where =WHERE
        #if(sndType == ServiceWrap.SEND_IMMEDIATE):
            #self.TF.logger.Message("Sent Type is: SEND_IMMEDIATE  \n")
            #TCGSET = ServiceWrap.TCG_Set(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, ucWhere=Where, mapOfValues=DICT, szMethodUID=MethodUID, pProtocolSpecific=None, sendType=sndType)
        #elif(sndType == ServiceWrap.SEND_QUEUED):
            #self.TF.logger.Message("Sent Type is: SEND_QUEUED  \n")
            #TCGSET = ServiceWrap.TCG_Set(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, ucWhere=Where, mapOfValues=DICT, szMethodUID=MethodUID, pProtocolSpecific=None, sendType=sndType)
            #status = False
            #status = self.TF.threadPool.WaitForThreadCompletion()
            #if False == status:
                #self.__CheckForErrors()
                #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #else:
            #SendType=ServiceWrap.CMD_SEND_TYPE.SEND_NONE
            #self.TF.logger.Message("Sent Type is: SEND_NONE and  (Executed in Direct-mode)  \n")
            #TCGSET = ServiceWrap.TCG_Set(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, ucWhere=Where, mapOfValues=DICT, szMethodUID=MethodUID, pProtocolSpecific=None, sendType=sndType)
        ##Response validation
        #Status = TCGSET.response.status
        #self.TF.logger.Message("%-35s: %s"%('Status Code: ', Status))
        ##Request and Reseponse buffer------------
        #self.TF.logger.Message("Input-Buffer: TCGSET Requeset Buffer:--------------------\n")
        #TCGSET.pReqBuffer.PrintToLog()  #???
        #self.TF.logger.Message("Output-Buffer: TCGSET Response Buffer:--------------------\n")
        #TCGSET.pRespBuffer.PrintToLog() #???
        #ResBuff =  ServiceWrap.Buffer.CreateBuffer(512, patternType = ServiceWrap.ALL_0, isSector = False)
        #ResBuff.FullCopy(TCGSET.pRespBuffer)     #????
        #return (ResBuff)
        ##return ServiceWrap.TCG_Set(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, ucWhere=Where, mapOfValues=DICT, szMethodUID=MethodUID, sendType=ServiceWrap.CMD_SEND_TYPE.SEND_NONE)

    #def PostWRTable(self, InvokingId, TSN, NewPasswd, MethodUID):
        #ComID = 0x7FFE
        #HSN =1
        #WRTable = ServiceWrap.WriteTable()
        #WRTable.SetPin(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szPin=NewPasswd, szMethodUID=MethodUID)
        #return (WRTable)

    #def PostActivate(self, InvokingId, TSN, MethodUID, sndType = ServiceWrap.SEND_IMMEDIATE):
        #ComID = 0x7FFE
        #HSN =1
        #if(sndType == ServiceWrap.SEND_IMMEDIATE):
            #self.TF.logger.Message("Sent Type is: SEND_IMMEDIATE  \n")
            #ActivateLockingSP = ServiceWrap.ActivateLockingSP(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szMethodUID=MethodUID, pProtocolSpecific=None, sendType=sndType)
        #elif(sndType == ServiceWrap.SEND_QUEUED):
            #self.TF.logger.Message("Sent Type is: SEND_QUEUED  \n")
            #ActivateLockingSP = ServiceWrap.ActivateLockingSP(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szMethodUID=MethodUID, pProtocolSpecific=None, sendType=sndType)
            #status = False
            #status = self.TF.threadPool.WaitForThreadCompletion()
            #if False == status:
                #self.__CheckForErrors()
                #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #else:
            #SendType=ServiceWrap.CMD_SEND_TYPE.SEND_NONE
            #self.TF.logger.Message("Sent Type is: SEND_NONE and  (Executed in Direct-mode)  \n")
            #ActivateLockingSP = ServiceWrap.ActivateLockingSP(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szMethodUID=MethodUID, pProtocolSpecific=None, sendType=sndType)
            #ActivateLockingSP.Execute()
            #ActivateLockingSP.HandleOverlappedExecute()
            #ActivateLockingSP.HandleAndParseResponse()
        ##Response validation
        #Status = ActivateLockingSP.response.status
        #self.TF.logger.Message("%-35s: %s"%('Status Code: ', Status))
        #assert(Status == ServiceWrap.TCG_STATUS_CODE.SUCCESS)
        ##Request and Reseponse buffer------------
        #self.TF.logger.Message("Input-Buffer: ActivateLockingSP Requeset Buffer:--------------------\n")
        #ActivateLockingSP.pReqBuffer.PrintToLog()
        #self.TF.logger.Message("Output-Buffer: ActivateLockingSP Response Buffer:--------------------\n")
        #ActivateLockingSP.pRespBuffer.PrintToLog()
        #ResBuff =  ServiceWrap.Buffer.CreateBuffer(512, patternType = ServiceWrap.ALL_0, isSector = False)
        #ResBuff.FullCopy(ActivateLockingSP.pRespBuffer)
        #return (ResBuff)

        ##WRTable = ServiceWrap.WriteTable()
        ##WRTable.ActivateLockingSP("LOCKING_SP", HSN, TSN, 0x7ffe, "ACTIVATE")
        ##WRTable.ActivateLockingSP(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szMethodUID=MethodUID)
        ##return (WRTable)

    #def PostAuthOpenSession(self, InvokingId, TSN, UID, NewPasswd, sndType = ServiceWrap.SEND_IMMEDIATE):
        #MethodUID = "AUTHENTICATE" # #0x060000001C
        #ComID = 0x7FFE
        #HSN =1
        #if(sndType == ServiceWrap.SEND_IMMEDIATE):
            #self.TF.logger.Message("Sent Type is: SEND_IMMEDIATE  \n")
            #AuthenticateUserToAnOpenedSession = ServiceWrap.AuthenticateUserToAnOpenedSession(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szUID=UID, szUserPassword=NewPasswd, szMethodUID=MethodUID,  pProtocolSpecific=None, sendType=sndType)
        #elif(sndType == ServiceWrap.SEND_QUEUED):
            #self.TF.logger.Message("Sent Type is: SEND_QUEUED  \n")
            #AuthenticateUserToAnOpenedSession = ServiceWrap.AuthenticateUserToAnOpenedSession(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szUID=UID, szUserPassword=NewPasswd, szMethodUID=MethodUID,  pProtocolSpecific=None, sendType=sndType)
            #status = False
            #status = self.TF.threadPool.WaitForThreadCompletion()
            #if False == status:
                #self.__CheckForErrors()
                #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #else:
            #SendType=ServiceWrap.CMD_SEND_TYPE.SEND_NONE
            #self.TF.logger.Message("Sent Type is: SEND_NONE and  (Executed in Direct-mode)  \n")
            #AuthenticateUserToAnOpenedSession = ServiceWrap.AuthenticateUserToAnOpenedSession(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szUID=UID, szUserPassword=NewPasswd, szMethodUID=MethodUID,  pProtocolSpecific=None, sendType=sndType)
            #AuthenticateUserToAnOpenedSession.Execute()
            #AuthenticateUserToAnOpenedSession.HandleOverlappedExecute()
            #AuthenticateUserToAnOpenedSession.HandleAndParseResponse()
        ##Response validation
        #Status = AuthenticateUserToAnOpenedSession.response.status
        #self.TF.logger.Message("%-35s: %s"%('Status Code: ', Status))
        #assert(Status == ServiceWrap.TCG_STATUS_CODE.SUCCESS)
        ##Request and Reseponse buffer------------
        #self.TF.logger.Message("Input-Buffer: AuthenticateUserToAnOpenedSession Requeset Buffer:--------------------\n")
        #AuthenticateUserToAnOpenedSession.pReqBuffer.PrintToLog()
        #self.TF.logger.Message("Output-Buffer: AuthenticateUserToAnOpenedSession Response Buffer:--------------------\n")
        #AuthenticateUserToAnOpenedSession.pRespBuffer.PrintToLog()
        #ResBuff =  ServiceWrap.Buffer.CreateBuffer(512, patternType = ServiceWrap.ALL_0, isSector = False)
        #ResBuff.FullCopy(AuthenticateUserToAnOpenedSession.pRespBuffer)
        #return (ResBuff)
        ##WRTable = ServiceWrap.WriteTable()
        ##WRTable.AuthenticateUserToAnOpenedSession(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szUID=UID, szUserPassword=NewPasswd, szMethodUID=MethodUID)
        ##return (WRTable)


    #def EraseGenKey(self, InvokingId, TSN, MethodUID, sndType = ServiceWrap.SEND_IMMEDIATE):
        #HSN = 1
        #MethodUID = "GENKEY"
        #ComID = 0x7FFE
        #HSN =1
        #if(sndType == ServiceWrap.SEND_IMMEDIATE):
            #self.TF.logger.Message("Sent Type is: SEND_IMMEDIATE  \n")
            #GenKeyEraseResBuff = ServiceWrap.GenKey(szInvokingId=InvokingId, uiHSN= HSN, uiTSN=TSN, uiComId=ComID, szMethodUID=MethodUID,  pProtocolSpecific=None, sendType=sndType)
        #elif(sndType == ServiceWrap.SEND_QUEUED):
            #self.TF.logger.Message("Sent Type is: SEND_QUEUED  \n")
            #GenKeyEraseResBuff = ServiceWrap.GenKey(szInvokingId=InvokingId, uiHSN= HSN, uiTSN=TSN, uiComId=ComID, szMethodUID=MethodUID,  pProtocolSpecific=None, sendType=sndType)
            #status = False
            #status = self.TF.threadPool.WaitForThreadCompletion()
            #if False == status:
                #self.__CheckForErrors()
                #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #else:
            #SendType=ServiceWrap.CMD_SEND_TYPE.SEND_NONE
            #self.TF.logger.Message("Sent Type is: SEND_NONE and  (Executed in Direct-mode)  \n")
            #GenKeyEraseResBuff = ServiceWrap.GenKey(szInvokingId=InvokingId, uiHSN= HSN, uiTSN=TSN, uiComId=ComID, szMethodUID=MethodUID,  pProtocolSpecific=None, sendType=sndType)
            #GenKeyEraseResBuff.Execute()
            #GenKeyEraseResBuff.HandleOverlappedExecute()
            #GenKeyEraseResBuff.HandleAndParseResponse()
        ##Response validation
        #Status = GenKeyEraseResBuff.response.status
        #self.TF.logger.Message("%-35s: %s"%('Status Code: ', Status))
        #assert(Status == ServiceWrap.TCG_STATUS_CODE.SUCCESS)
        ##Request and Reseponse buffer------------
        #self.TF.logger.Message("Input-Buffer: GenKeyEraseRes Requeset Buffer:--------------------\n")
        #GenKeyEraseResBuff.pReqBuffer.PrintToLog()
        #self.TF.logger.Message("Output-Buffer: GenKeyErase Response Buffer:--------------------\n")
        #GenKeyEraseResBuff.pRespBuffer.PrintToLog()
        #ResBuff =  ServiceWrap.Buffer.CreateBuffer(512, patternType = ServiceWrap.ALL_0, isSector = False)
        #ResBuff.FullCopy(GenKeyEraseResBuff.pRespBuffer)
        #return (ResBuff)
        ##WRTable = ServiceWrap.WriteTable()
        ##WRTable.AuthenticateUserToAnOpenedSession(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szUID=UID, szUserPassword=NewPasswd, szMethodUID=MethodUID)
        ##return (WRTable)


    #def PostGetAuthState(self, InvokingId, TSN, ENTITY, NOFENTITY, MethodUID, sndType = ServiceWrap.SEND_IMMEDIATE):
        #ComID = 0x7FFE
        #HSN =1
        #Entity = ENTITY
        #NumOfEntities = NOFENTITY

        #if(sndType == ServiceWrap.SEND_IMMEDIATE):
            #self.TF.logger.Message("Sent Type is: SEND_IMMEDIATE  \n")
            #GetAuthorityStates = ServiceWrap.GetAuthorityStates(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szEntity=Entity, uiNumOfEntities=NumOfEntities, szMethodUID=MethodUID,  pProtocolSpecific=None, sendType=sndType)
        #elif(sndType == ServiceWrap.SEND_QUEUED):
            #self.TF.logger.Message("Sent Type is: SEND_QUEUED  \n")
            #GetAuthorityStates = ServiceWrap.GetAuthorityStates(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szEntity=Entity, uiNumOfEntities=NumOfEntities, szMethodUID=MethodUID,  pProtocolSpecific=None, sendType=sndType)
            #status = False
            #status = self.TF.threadPool.WaitForThreadCompletion()
            #if False == status:
                #self.__CheckForErrors()
                #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #else:
            #SendType=ServiceWrap.CMD_SEND_TYPE.SEND_NONE
            #self.TF.logger.Message("Sent Type is: SEND_NONE and  (Executed in Direct-mode)  \n")
            #GetAuthorityStates = ServiceWrap.GetAuthorityStates(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szEntity=Entity, uiNumOfEntities=NumOfEntities, szMethodUID=MethodUID,  pProtocolSpecific=None, sendType=sndType)
            #GetAuthorityStates.Execute()
            #GetAuthorityStates.HandleOverlappedExecute()
            #GetAuthorityStates.HandleAndParseResponse()
        ##Response validation
        #Status = GetAuthorityStates.response.status
        #self.TF.logger.Message("%-35s: %s"%('Status Code: ', Status))
        #assert(Status == ServiceWrap.TCG_STATUS_CODE.SUCCESS)
        ##Request and Reseponse buffer------------
        #self.TF.logger.Message("Input-Buffer: GetAuthorityStates Requeset Buffer:--------------------\n")
        #GetAuthorityStates.pRequestBufferData.PrintToLog()
        #self.TF.logger.Message("Output-Buffer: GetAuthorityStates Response Buffer:--------------------\n")
        #GetAuthorityStates.pRespBufferData.PrintToLog()
        #ResBuff =  ServiceWrap.Buffer.CreateBuffer(512, patternType = ServiceWrap.ALL_0, isSector = False)
        #ResBuff.FullCopy(GetAuthorityStates.pRespBufferData)
        #return (ResBuff)
        ##RdTable = ServiceWrap.ReadTable()
        ##RdTable.GetAuthorityStates(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szEntity=Entity, uiNumOfEntities=NumOfEntities, szMethodUID=MethodUID)
        ##return (RdTable)

    #def PostSetBooleanExprn(self, InvokingId, TSN, HalfUID, HalfUID_2, UID_1, UID_2,  MethodUID, sndType = ServiceWrap.SEND_IMMEDIATE):
        #ComID = 0x7FFE
        #HSN = 1

        #if(sndType == ServiceWrap.SEND_IMMEDIATE):
            #self.TF.logger.Message("Sent Type is: SEND_IMMEDIATE  \n")
            #SetBooleanExprToACETable = ServiceWrap.SetBooleanExprToACETable(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szHalfUID=HalfUID, szHalfUID_2=HalfUID_2, szUID_1=UID_1, szUID_2=UID_2, szMethodUID=MethodUID,  pProtocolSpecific=None, sendType=sndType)
        #elif(sndType == ServiceWrap.SEND_QUEUED):
            #self.TF.logger.Message("Sent Type is: SEND_QUEUED  \n")
            #SetBooleanExprToACETable = ServiceWrap.SetBooleanExprToACETable(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szHalfUID=HalfUID, szHalfUID_2=HalfUID_2, szUID_1=UID_1, szUID_2=UID_2, szMethodUID=MethodUID,  pProtocolSpecific=None, sendType=sndType)
            #status = False
            #status = self.TF.threadPool.WaitForThreadCompletion()
            #if False == status:
                #self.__CheckForErrors()
                #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #else:
            #SendType=ServiceWrap.CMD_SEND_TYPE.SEND_NONE
            #self.TF.logger.Message("Sent Type is: SEND_NONE and  (Executed in Direct-mode)  \n")
            #SetBooleanExprToACETable = ServiceWrap.SetBooleanExprToACETable(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szHalfUID=HalfUID, szHalfUID_2=HalfUID_2, szUID_1=UID_1, szUID_2=UID_2, szMethodUID=MethodUID,  pProtocolSpecific=None, sendType=sndType)
            #SetBooleanExprToACETable.Execute()
            #SetBooleanExprToACETable.HandleOverlappedExecute()
            #SetBooleanExprToACETable.HandleAndParseResponse()
        ##Response validation
        #Status = SetBooleanExprToACETable.response.status
        #self.TF.logger.Message("%-35s: %s"%('Status Code: ', Status))
        #assert(Status == ServiceWrap.TCG_STATUS_CODE.SUCCESS)
        ##Request and Reseponse buffer------------
        #self.TF.logger.Message("Input-Buffer: SetBooleanExprToACETable Requeset Buffer:--------------------\n")
        #SetBooleanExprToACETable.pReqBuffer.PrintToLog()
        #self.TF.logger.Message("Output-Buffer: SetBooleanExprToACETable Response Buffer:--------------------\n")
        #SetBooleanExprToACETable.pRespBuffer.PrintToLog()
        #ResBuff =  ServiceWrap.Buffer.CreateBuffer(512, patternType = ServiceWrap.ALL_0, isSector = False)
        #ResBuff.FullCopy(SetBooleanExprToACETable.pRespBuffer)
        #return (ResBuff)

    #def GetAccRightsOfMethodAgainstTableOrObject(self, InvokingId, TSN, UserUID, UserMethodUID, MethodUID, sndType = ServiceWrap.SEND_IMMEDIATE):
        #ComID = 0x7FFE
        #HSN = 1
        ##UserUID = "USER1" #?  #0x0900030001
        ##UserMethodUID= "GET" #?  #GET Method-UID Get Method UID -- <0000000600000016>
        ##MethodUID = "GETACL" #  0x060000000D
        #if(sndType == ServiceWrap.SEND_IMMEDIATE):
            #self.TF.logger.Message("Sent Type is: SEND_IMMEDIATE  \n")
            #GetAccessRightsOfMethodAgainstTableOrObject = ServiceWrap.GetAccessRightsOfMethodAgainstTableOrObject(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szUserUID=UserUID, szUserMethodUID=UserMethodUID, szMethodUID=MethodUID,  pProtocolSpecific=None, sendType=sndType)
        #elif(sndType == ServiceWrap.SEND_QUEUED):
            #self.TF.logger.Message("Sent Type is: SEND_QUEUED  \n")
            #GetAccessRightsOfMethodAgainstTableOrObject = ServiceWrap.GetAccessRightsOfMethodAgainstTableOrObject(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szUserUID=UserUID, szUserMethodUID=UserMethodUID, szMethodUID=MethodUID,  pProtocolSpecific=None, sendType=sndType)
            #status = False
            #status = self.TF.threadPool.WaitForThreadCompletion()
            #if False == status:
                #self.__CheckForErrors()
                #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #else:
            #SendType=ServiceWrap.CMD_SEND_TYPE.SEND_NONE
            #self.TF.logger.Message("Sent Type is: SEND_NONE and  (Executed in Direct-mode)  \n")
            #GetAccessRightsOfMethodAgainstTableOrObject = ServiceWrap.GetAccessRightsOfMethodAgainstTableOrObject(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szUserUID=UserUID, szUserMethodUID=UserMethodUID, szMethodUID=MethodUID,  pProtocolSpecific=None, sendType=sndType)
            #GetAccessRightsOfMethodAgainstTableOrObject.Execute()
            #GetAccessRightsOfMethodAgainstTableOrObject.HandleOverlappedExecute()
            #GetAccessRightsOfMethodAgainstTableOrObject.HandleAndParseResponse()
        ##Response validation
        #Status = GetAccessRightsOfMethodAgainstTableOrObject.response.status
        #self.TF.logger.Message("%-35s: %s"%('Status Code: ', Status))
        #assert(Status == ServiceWrap.TCG_STATUS_CODE.SUCCESS)
        ##Request and Reseponse buffer------------
        #self.TF.logger.Message("Input-Buffer: GetAccessRightsOfMethodAgainstTableOrObject  Requeset Buffer:--------------------\n")
        #GetAccessRightsOfMethodAgainstTableOrObject.pRequestBufferData.PrintToLog()
        #self.TF.logger.Message("Output-Buffer: GetAccessRightsOfMethodAgainstTableOrObject Response Buffer:--------------------\n")
        #GetAccessRightsOfMethodAgainstTableOrObject.pRespBufferData.PrintToLog()
        #ResBuff =  ServiceWrap.Buffer.CreateBuffer(512, patternType = ServiceWrap.ALL_0, isSector = False)
        #ResBuff.FullCopy(GetAccessRightsOfMethodAgainstTableOrObject.pRespBufferData)
        #return (ResBuff)

    #def AuthToOpenSession(self, InvokingId, TSN, NewPasswd, MethodUID, sndType = ServiceWrap.SEND_IMMEDIATE):
        #ComID = 0x7FFE
        #HSN = 1
        #UID = "USER1"
        #MethodUID = "AUTHENTICATE" # #0x060000001C

        #if(sndType == ServiceWrap.SEND_IMMEDIATE):
            #self.TF.logger.Message("Sent Type is: SEND_IMMEDIATE  \n")
            #AuthenticateUserToAnOpenedSession  = ServiceWrap.AuthenticateUserToAnOpenedSession(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szUID=UID, szUserPassword=NewPasswd, szMethodUID=MethodUID,  pProtocolSpecific=None, sendType=sndType)
        #elif(sndType == ServiceWrap.SEND_QUEUED):
            #self.TF.logger.Message("Sent Type is: SEND_QUEUED  \n")
            #AuthenticateUserToAnOpenedSession  = ServiceWrap.AuthenticateUserToAnOpenedSession(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szUID=UID, szUserPassword=NewPasswd, szMethodUID=MethodUID,  pProtocolSpecific=None, sendType=sndType)
            #status = False
            #status = self.TF.threadPool.WaitForThreadCompletion()
            #if False == status:
                #self.__CheckForErrors()
                #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #else:
            #SendType=ServiceWrap.CMD_SEND_TYPE.SEND_NONE
            #self.TF.logger.Message("Sent Type is: SEND_NONE and  (Executed in Direct-mode)  \n")
            #AuthenticateUserToAnOpenedSession  = ServiceWrap.AuthenticateUserToAnOpenedSession(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, szUID=UID, szUserPassword=NewPasswd, szMethodUID=MethodUID,  pProtocolSpecific=None, sendType=sndType)
            #AuthenticateUserToAnOpenedSession.Execute()
            #AuthenticateUserToAnOpenedSession.HandleOverlappedExecute()
            #AuthenticateUserToAnOpenedSession.HandleAndParseResponse()
        ##Response validation
        #Status = AuthenticateUserToAnOpenedSession.response.status
        #self.TF.logger.Message("%-35s: %s"%('Status Code: ', Status))
        #assert(Status == ServiceWrap.TCG_STATUS_CODE.SUCCESS)
        ##Request and Reseponse buffer------------
        #self.TF.logger.Message("Input-Buffer: AuthenticateUserToAnOpenedSession  Requeset Buffer:--------------------\n")
        #AuthenticateUserToAnOpenedSession.pReqBuffer.PrintToLog()
        #self.TF.logger.Message("Output-Buffer: AuthenticateUserToAnOpenedSession Response Buffer:--------------------\n")
        #AuthenticateUserToAnOpenedSession.pRespBuffer.PrintToLog()
        #ResBuff =  ServiceWrap.Buffer.CreateBuffer(512, patternType = ServiceWrap.ALL_0, isSector = False)
        #ResBuff.FullCopy(AuthenticateUserToAnOpenedSession.pRespBuffer)
        #return (ResBuff)

    #def ReadDataStoreTable(self, InvokingId, TSN, NewPasswd, MethodUID, sndType = ServiceWrap.SEND_IMMEDIATE):
        #ComID = 0x7FFE
        #HSN = 1
        #MethodUID='GET'  #00 00 00 06 00 00 00 16   Method-UID Get Method UID <00 00 00 06 00 00 00 16>
        #if(sndType == ServiceWrap.SEND_IMMEDIATE):
            #self.TF.logger.Message("Sent Type is: SEND_IMMEDIATE  \n")
            #ReadDStable = ServiceWrap.ReadDataFromByteTable(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartRow=StartRow, uiEndRow=EndRow, szMethodUID=MethodUID, pProtocolSpecific=None, sendType=sndType)
        #elif(sndType == ServiceWrap.SEND_QUEUED):
            #self.TF.logger.Message("Sent Type is: SEND_QUEUED  \n")
            #ReadDStable = ServiceWrap.ReadDataFromByteTable(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartRow=StartRow, uiEndRow=EndRow, szMethodUID=MethodUID, pProtocolSpecific=None, sendType=sndType)
            #status = False
            #status = self.TF.threadPool.WaitForThreadCompletion()
            #if False == status:
                #self.__CheckForErrors()
                #raise ValidationError.CVFGenericExceptions("Wait For Thread Completion Failed", self.errorManager.GetAllFailureDescription())
        #else:
            #SendType=ServiceWrap.CMD_SEND_TYPE.SEND_NONE
            #self.TF.logger.Message("Sent Type is: SEND_NONE and  (Executed in Direct-mode)  \n")
            #ReadDStable = ServiceWrap.ReadDataFromByteTable(szInvokingId=InvokingId, uiHSN=HSN, uiTSN=TSN, uiComId=ComID, uiStartRow=StartRow, uiEndRow=EndRow, szMethodUID=MethodUID, pProtocolSpecific=None, sendType=sndType)
            #ReadDStable.Execute()
            #ReadDStable.HandleOverlappedExecute()
            #ReadDStable.HandleAndParseResponse()
        ##Response validation
        #Status = ReadDStable.response.status
        #self.TF.logger.Message("%-35s: %s"%('Status Code: ', Status))
        #assert(Status == ServiceWrap.TCG_STATUS_CODE.SUCCESS)
        ##Request and Reseponse buffer------------
        #self.TF.logger.Message("Input-Buffer: ReadDataStoreTable  Requeset Buffer:--------------------\n")
        #ReadDStable.pRequestBufferData.PrintToLog()
        #self.TF.logger.Message("Output-Buffer: ReadDataStoreTable Response Buffer:--------------------\n")
        #ReadDStable.pRespBufferData.PrintToLog()
        #ResBuff =  ServiceWrap.Buffer.CreateBuffer(512, patternType = ServiceWrap.ALL_0, isSector = False)
        #ResBuff.FullCopy(ReadDStable.pRespBufferData)
        #return (ResBuff)


    #def ResponseStartSession(self, StartSessionObj):
        #self.TF.logger.Message(self.TF.TAG, "\n**********************Start Session Response***************************\n")
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Status', StartSessionObj.response.status))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('ComPacket', StartSessionObj.response.comPacket))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('DataSubpacket', StartSessionObj.response.comPacket.extendedComID))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('DataSubpacket', StartSessionObj.response.comPacket.length))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('DataSubpacket', StartSessionObj.response.comPacket.minTransfer))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('DataSubpacket', StartSessionObj.response.comPacket.outStandingData))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('DataSubpacket', StartSessionObj.response.HSN))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('DataSubpacket', StartSessionObj.response.invokingUID))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('DataSubpacket', StartSessionObj.response.methodUID))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Packet', StartSessionObj.response.packet.session))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Packet', StartSessionObj.response.packet.seqNumber))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Packet', StartSessionObj.response.packet.length))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Packet', StartSessionObj.response.packet.ackType))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Packet', StartSessionObj.response.packet.acknowledgement))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('DataSubpacket', StartSessionObj.response.TSN))

        #self.__ValidateStartSessionBuff(StartSessionObj)

    #def ResponseTCGget(self, TCGgetObj):
        #self.TF.logger.Message(self.TF.TAG, "\n**********************TCG-GET***************************\n")
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Status', TCGgetObj.response.status))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Status', TCGgetObj.response.PIN))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('TSN', TCGgetObj.response.TSN))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('PIN', TCGgetObj.response.PIN))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('packet', TCGgetObj.response.packet.acknowledgement))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('packet', TCGgetObj.response.packet.ackType))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('packet', TCGgetObj.response.packet.length))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('packet', TCGgetObj.response.packet.seqNumber))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('packet', TCGgetObj.response.packet.session))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('mbrControlTableData', TCGgetObj.response.mbrControlTableData.done))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('mbrControlTableData', TCGgetObj.response.mbrControlTableData.enable))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('mbrControlTableData', TCGgetObj.response.mbrControlTableData.MBRDoneOnReset))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', TCGgetObj.response.lockingTableData.activeKey))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', TCGgetObj.response.lockingTableData.advKeyMode))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', TCGgetObj.response.lockingTableData.commonName))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', TCGgetObj.response.lockingTableData.contOnReset))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', TCGgetObj.response.lockingTableData.generalStatus))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', TCGgetObj.response.lockingTableData.lastReEncryptLBA))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', TCGgetObj.response.lockingTableData.lastReEncStat))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', TCGgetObj.response.lockingTableData.lockOnReset))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', TCGgetObj.response.lockingTableData.name))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', TCGgetObj.response.lockingTableData.nextKey))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', TCGgetObj.response.lockingTableData.rangeLength))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', TCGgetObj.response.lockingTableData.rangeStart))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', TCGgetObj.response.lockingTableData.readLocked))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', TCGgetObj.response.lockingTableData.readLockEnabled))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', TCGgetObj.response.lockingTableData.reEncryptRequest))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', TCGgetObj.response.lockingTableData.reEncryptState))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', TCGgetObj.response.lockingTableData.verifyMode))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', TCGgetObj.response.lockingTableData.writeLocked))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', TCGgetObj.response.lockingTableData.writeLockEnabled))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('lifeCycleState', TCGgetObj.response.lifeCycleState))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('HSN', TCGgetObj.response.HSN))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('dataSubpacket', TCGgetObj.response.dataSubpacket.kind))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('dataSubpacket', TCGgetObj.response.dataSubpacket.length))

    #def ResponseEndSession(self, EndSessionObj):
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Status', EndSessionObj.response.status))

    #def ResponseTCGset(self, TCGsetObj):
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Status', TCGsetObj.response.status))

    #def ResponseWRtable(self, WRTableObj):
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Status', WRTableObj.response.status))

    #def ResponseReadTable(self, ReadTableObj):
        #self.TF.logger.Message(self.TF.TAG, "\n**********************Read Table ***************************\n")
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('Status', ReadTableObj.response.status))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('TSN', ReadTableObj.response.TSN))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('PIN', ReadTableObj.response.PIN))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('packet', ReadTableObj.response.packet.acknowledgement))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('packet', ReadTableObj.response.packet.ackType))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('packet', ReadTableObj.response.packet.length))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('packet', ReadTableObj.response.packet.seqNumber))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('packet', ReadTableObj.response.packet.session))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('mbrControlTableData', ReadTableObj.response.mbrControlTableData.done))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('mbrControlTableData', ReadTableObj.response.mbrControlTableData.enable))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('mbrControlTableData', ReadTableObj.response.mbrControlTableData.MBRDoneOnReset))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', ReadTableObj.response.lockingTableData.activeKey))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', ReadTableObj.response.lockingTableData.advKeyMode))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', ReadTableObj.response.lockingTableData.commonName))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', ReadTableObj.response.lockingTableData.contOnReset))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', ReadTableObj.response.lockingTableData.generalStatus))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', ReadTableObj.response.lockingTableData.lastReEncryptLBA))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', ReadTableObj.response.lockingTableData.lastReEncStat))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', ReadTableObj.response.lockingTableData.lockOnReset))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', ReadTableObj.response.lockingTableData.name))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', ReadTableObj.response.lockingTableData.nextKey))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', ReadTableObj.response.lockingTableData.rangeLength))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', ReadTableObj.response.lockingTableData.rangeStart))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', ReadTableObj.response.lockingTableData.readLocked))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', ReadTableObj.response.lockingTableData.readLockEnabled))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', ReadTableObj.response.lockingTableData.reEncryptRequest))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', ReadTableObj.response.lockingTableData.reEncryptState))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', ReadTableObj.response.lockingTableData.verifyMode))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', ReadTableObj.response.lockingTableData.writeLocked))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('LockingTableData', ReadTableObj.response.lockingTableData.writeLockEnabled))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('lifeCycleState', ReadTableObj.response.lifeCycleState))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('HSN', ReadTableObj.response.HSN))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('dataSubpacket', ReadTableObj.response.dataSubpacket.kind))
        #self.TF.logger.Message(self.TF.TAG, "%-35s: %s"%('dataSubpacket', ReadTableObj.response.dataSubpacket.length))


    #def __ValidateStartSessionBuff(self, StartSessionOBJ):
        #Referensebuff = StartSessionOBJ.pRespBuffer
        #HSNval = StartSessionOBJ.pRespBuffer.GetByte(0x4E)
        #HSNExpval = HSNval & (0xF0)
        #HSNExpval = StartSessionOBJ.response.HSN
        ##assert (HSNExpval == StartSessionOBJ.response.HSN)

        #Statusval = StartSessionOBJ.pRespBuffer.GetByte(0x53)
        #StatusExpval = Statusval & (0xFF)
        ##assert (StatusExpval == StartSessionOBJ.response.status)

