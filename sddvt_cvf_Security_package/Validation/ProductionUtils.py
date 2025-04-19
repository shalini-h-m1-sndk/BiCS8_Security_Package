
"""
################################################################################
# Copyright (c) SanDisk Corp.2013 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# FILE:ProductionUtils.py: Production Utility.
#                  AUTHOR: Ravi G
################################################################################
"""

from builtins import chr
from builtins import object
import random

import CTFServiceWrapper as ServiceWrap
import NVMeCMDWrapper as NVMeWrap

import Validation.TestFixture as TestFixture
import Validation.TestParams as TP


#**************************************************************************************************************
##
# @brief Runs all the variations in the testObject
# @details
# @return None
# @exception None
#**************************************************************************************************************
class ProductionUtils(object):
    def __init__(self):

        self.TF = TestFixture.TestFixture()
        self.configParser = self.TF.configParser

    def DownloadImage(self, chunkNr, FWBuffer, nrOfDwords, offset, namespaceID = 0, timeout = None):

        self.TF.logger.Debug("DOWNLOADING CHUNK NUMBER %d CHUNKSIZE %d -> NSID : %d  "%(chunkNr, nrOfDwords, namespaceID))

        downloadFW = NVMeWrap.FWImgDownLoadCmd(FWBuffer, namespaceID, nrOfDwords, offset)
        downloadFW.Execute()
        downloadFW.HandleOverlappedExecute()
        downloadFW.HandleAndParseResponse()

        SCT = downloadFW.objNVMeComIOEntry.completionEntry.DW3.SF.SCT
        SC = downloadFW.objNVMeComIOEntry.completionEntry.DW3.SF.SC

        self.TF.logger.Debug("%-35s: (%s, %s)"%('FW CHUNK DOWNLOAD STATUS', list(TP.SCT.keys())[list(TP.SCT.values()).index(SCT)], list(TP.SC.keys())[list(TP.SC.values()).index(SC)]))

        return(SCT, SC)

    def FWCommit(self, CA, FS, namespaceID = 0):

        FWCmmitDW10 = NVMeWrap.SPEC_1_2_ADMIN_FIRMWARE_ACTIVATE_COMMAND_DW10()
        FWCmmitDW10.CA = CA
        FWCmmitDW10.FS = FS

        self.TF.logger.Debug("%-35s: (%s, %s)"%('FW COMMIT -> COMMIT ACTION, FIRMWARE SLOT: ', CA, FS))

        FWCommit = NVMeWrap.FWCommitCmd(namespaceID, FWCmmitDW10)
        FWCommit.Execute()
        FWCommit.HandleOverlappedExecute()
        FWCommit.HandleAndParseResponse()

        SCT = FWCommit.objNVMeComIOEntry.completionEntry.DW3.SF.SCT
        SC = FWCommit.objNVMeComIOEntry.completionEntry.DW3.SF.SC

        self.TF.logger.Debug("%-35s: (%s, %s)"%('FW COMMIT STATUS', list(TP.SCT.keys())[list(TP.SCT.values()).index(SCT)], list(TP.SC.keys())[list(TP.SC.values()).index(SC)]))

        return(SCT, SC)


    def CheckROMMode(self):

        if(-1 != self.TF.modelNum.lower().find('rom')):
            self.TF.logger.Debug("Current Mode of the Model is: %s\n"% self.TF.modelNum[self.TF.modelNum.lower().find('rom'):][:8])
            return True
        else:
            return False

    def ParseBotFile(self):

        self.TF.logger.Info('Parsing BOT File')
        self.botParser.Open(self.botFilePath)

        self.botBuffer = self.botParser.GetBotSection(NVMeWrap.BOT_DLEFORMAT)
        self.TF.logger.Info('Extracted DLE from BOT File')

    def CheckDLEMode(self):

        self.configParser.SetValue('identify_controller_time_out', self.timeout)

        identifyContObj = NVMeWrap.IdentifyController()
        identifyContObj.Execute()
        identifyContObj.HandleOverlappedExecute()
        identifyContObj.HandleAndParseResponse()
        SC = identifyContObj.objNVMeComIOEntry.completionEntry.DW3.SF.SC
        SCT = identifyContObj.objNVMeComIOEntry.completionEntry.DW3.SF.SCT

        self.TF.logger.Debug("%-35s: (%s, %s)"%('IDENTIFY CONTROLLER COMMAND STATUS, (SCT, SC)', list(TP.SCT.keys())[list(TP.SCT.values()).index(SCT)], list(TP.SC.keys())[list(TP.SC.values()).index(SC)]))
        assert(SC == TP.SC['SUCCESSFUL_COMPLETION']), "IDENTIFY COMMAND EXECUTION FAILEDS. Status Code ->  %s\n"%list(TP.SC.keys())[list(TP.SC.values()).index(SC)]

        modelNum = identifyContObj.objOutputData.MN
        modelNum = ''.join(chr(e) for e in modelNum)
        #Remove unwanted characters.
        modelNum = modelNum.replace('\x00', '').rstrip()

        if modelNum.lower().find('dle-mode') != -1:
            return True
        else:
            return False

    def GetFWVersion(self):

        self.configParser.SetValue('identify_controller_time_out', self.timeout)
        identifyContObj = NVMeWrap.IdentifyController()
        identifyContObj.Execute()
        identifyContObj.HandleOverlappedExecute()
        identifyContObj.HandleAndParseResponse()

        SC = identifyContObj.objNVMeComIOEntry.completionEntry.DW3.SF.SC
        SCT = identifyContObj.objNVMeComIOEntry.completionEntry.DW3.SF.SCT

        self.TF.logger.Debug("%-35s: (%s, %s)"%('IDENTIFY CONTROLLER COMMAND STATUS, (SCT, SC)', list(TP.SCT.keys())[list(TP.SCT.values()).index(SCT)], list(TP.SC.keys())[list(TP.SC.values()).index(SC)]))
        assert(SC == TP.SC['SUCCESSFUL_COMPLETION']), "IDENTIFY COMMAND EXECUTION FAILEDS. Status Code ->  %s\n"%list(TP.SC.keys())[list(TP.SC.values()).index(SC)]

        newFWRevision = identifyContObj.objOutputData.FR
        newFWRevision = ''.join(chr(e) for e in newFWRevision)

        return newFWRevision

    def CheckFWMode(self):

        self.configParser.SetValue('identify_controller_time_out', self.timeout)
        identifyContObj = NVMeWrap.IdentifyController()
        identifyContObj.Execute()
        identifyContObj.HandleOverlappedExecute()
        identifyContObj.HandleAndParseResponse()
        SC = identifyContObj.objNVMeComIOEntry.completionEntry.DW3.SF.SC
        SCT = identifyContObj.objNVMeComIOEntry.completionEntry.DW3.SF.SCT

        self.TF.logger.Debug("%-35s: (%s, %s)"%('IDENTIFY CONTROLLER COMMAND STATUS, (SCT, SC)', list(TP.SCT.keys())[list(TP.SCT.values()).index(SCT)], list(TP.SC.keys())[list(TP.SC.values()).index(SC)]))
        assert(SC == TP.SC['SUCCESSFUL_COMPLETION']), "IDENTIFY COMMAND EXECUTION FAILEDS. Status Code ->  %s\n"%list(TP.SC.keys())[list(TP.SC.values()).index(SC)]

        modelNum = identifyContObj.objOutputData.MN
        modelNum = ''.join(chr(e) for e in modelNum)
        #Remove unwanted characters.
        modelNum = modelNum.replace('\x00', '').rstrip()
        self.TF.logger.Debug("Current State of the Model is %s"%modelNum)

        if modelNum.upper().find('FW -MODE') != -1:
            return True
        else:
            return False

    def ResetController(self, disableController = True, shutdown = False, deleteQueues = False, NVMeSubsytemReset = False):

        self.TF.logger.Debug("Issuing Reset Controller Command\n")

        reset = NVMeWrap.ControllerResetCMD(bytDisable = disableController, bytShutdown = shutdown, bytDeleteQueues = deleteQueues, bytNvmeSubsystemReset = NVMeSubsytemReset)
        reset.Execute()
        reset.HandleOverlappedExecute()
        reset.HandleAndParseResponse()

        getDevHealth = NVMeWrap.GetDeviceHealth()
        getDevHealth.Execute()
        getDevHealth.HandleOverlappedExecute()

        nrOfsubmissionQ = getDevHealth.objOutputdata.basicInfo.numberOfConfiguredSQs
        nrOfcompletionQ = getDevHealth.objOutputdata.basicInfo.numberOfConfiguredCQs

        ControlConf = getDevHealth.objOutputdata.basicInfo.controllerConfiguration
        CCEn = (ControlConf & 0x01)

        if deleteQueues:
            assert(0 == nrOfcompletionQ), "CQs are not deleted though Delete Queues is Set in Controller Reset Command"
            assert(0 == nrOfsubmissionQ), "SQs are not deleted though Delete Queues is Set in Controller Reset Command"





