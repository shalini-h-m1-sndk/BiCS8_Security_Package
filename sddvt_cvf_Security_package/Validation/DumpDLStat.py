
"""
################################################################################
# Copyright (c) SanDisk Corp.2013 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# FILE:DumpDLStat.py: Command Utility Library.
# AUTHOR: Manjunath Badi
################################################################################

This Module will take Workload object and dump DL workload statistics into test Log.

"""

from future import standard_library
standard_library.install_aliases()
from builtins import str
import os
import sys
import xml.etree.ElementTree as ET

import NVMeCMDWrapper as NVMeWrap
import CTFServiceWrapper as ServiceWrap
import Core.ValidationError as ValidationError
import Protocol.NVMe.Basic.VTFContainer as VTF
from xml.dom import minidom
from collections import OrderedDict
import Lib.System.Randomizer as Randomizer

def Dump(self,Workload):
    self.TF.VTFContainer.ObjectShelfStore("OverallWorkloadInfo", self.workFlowStatus.objOutputData.WorkloadResponse.OverallWorkloadInfo)
    self.TF.logger.Message("\n\n******** START PROFILE RESPONSE STATISTICS  ********\n")
    AllProfile = OrderedDict([('TotalRunTimeinSec',0),('AverageReadTimeMicroSeconds',0),('AverageWriteTimeMicroSeconds',0),('TotalWriteMBs',0),('TotalReadMBs',0),('TotalTrimMBs',0),('RandomReadCommands',0),('RandomWriteCommands',0),('RandomTrimCommands',0),('SeqReadCommands',0),('SeqWriteCommands',0),('SeqTrimCommands',0),('FlushCacheCommands',0),('TotalCommands',0)])
    #AllProfile = {'':0,'':0,'':0,'TotalWriteMBs':0,'TotalReadMBs':0,'TotalTrimMBs':0,'RandomReadCommands':0,'RandomWriteCommands':0,'RandomTrimCommands':0,'SeqReadCommands':0,'SeqWriteCommands':0,'SeqTrimCommands':0,'FlushCacheCommands':0,'TotalCommands':0}
    for workprofile in Workload:
        self.TF.logger.Message("\n..........................................  Profile %d  .......................................... "%(Workload.index(workprofile) + 1))

        self.TF.logger.Message("%-35s: %s"%('IOPS: ', workprofile.ProfileStatistics.Kiops))


        self.TF.logger.Message("%-35s: %s"%('TotalRunTimeinSec: ', workprofile.ProfileStatistics.TotalRuntimeSec))
        AllProfile['TotalRunTimeinSec'] += workprofile.ProfileStatistics.TotalRuntimeSec
        self.TF.logger.Message("%-35s: %s"%('AverageReadTimeMicroSeconds: ', workprofile.ProfileStatistics.ReadAverageTimeMicroSec))
        AllProfile['AverageReadTimeMicroSeconds'] += workprofile.ProfileStatistics.ReadAverageTimeMicroSec
        self.TF.logger.Message("%-35s: %s"%('AverageWriteTimeMicroSeconds: ', workprofile.ProfileStatistics.WriteAverageTimeMicroSec))
        AllProfile['AverageWriteTimeMicroSeconds'] += workprofile.ProfileStatistics.WriteAverageTimeMicroSec


        self.TF.logger.Message("%-35s: %s"%('TotalWriteMBs: ', workprofile.ProfileStatistics.NumOfTotalWriteMB))
        AllProfile['TotalWriteMBs'] += workprofile.ProfileStatistics.NumOfTotalWriteMB
        self.TF.logger.Message("%-35s: %s"%('TotalReadMBs: ', workprofile.ProfileStatistics.NumOfTotalReadMB))
        AllProfile['TotalReadMBs'] += workprofile.ProfileStatistics.NumOfTotalReadMB
        self.TF.logger.Message("%-35s: %s"%('TotalTrimMBs: ', workprofile.ProfileStatistics.NumOfTotalTrimMB))
        AllProfile['TotalTrimMBs'] += workprofile.ProfileStatistics.NumOfTotalTrimMB


        self.TF.logger.Message("%-35s: %s"%('RandomReadCommands: ', workprofile.ProfileStatistics.RandReadNumOfCommands.NumOfSucceededCommands))
        AllProfile['RandomReadCommands'] += workprofile.ProfileStatistics.RandReadNumOfCommands.NumOfSucceededCommands
        self.TF.logger.Message("%-35s: %s"%('RandomWriteCommands: ', workprofile.ProfileStatistics.RandWriteNumOfCommands.NumOfSucceededCommands))
        AllProfile['RandomWriteCommands'] += workprofile.ProfileStatistics.RandWriteNumOfCommands.NumOfSucceededCommands
        self.TF.logger.Message("%-35s: %s"%('RandomTrimCommands: ', workprofile.ProfileStatistics.RandTrimNumOfCommands.NumOfSucceededCommands))
        AllProfile['RandomTrimCommands'] += workprofile.ProfileStatistics.RandTrimNumOfCommands.NumOfSucceededCommands


        self.TF.logger.Message("%-35s: %s"%('SeqReadCommands: ', workprofile.ProfileStatistics.SeqReadNumOfCommands.NumOfSucceededCommands))
        AllProfile['SeqReadCommands'] += workprofile.ProfileStatistics.SeqReadNumOfCommands.NumOfSucceededCommands
        self.TF.logger.Message("%-35s: %s"%('SeqWriteCommands: ', workprofile.ProfileStatistics.SeqWriteNumOfCommands.NumOfSucceededCommands))
        AllProfile['SeqWriteCommands'] += workprofile.ProfileStatistics.SeqWriteNumOfCommands.NumOfSucceededCommands
        self.TF.logger.Message("%-35s: %s"%('SeqTrimCommands: ', workprofile.ProfileStatistics.SeqTrimNumOfCommands.NumOfSucceededCommands))
        AllProfile['SeqTrimCommands'] += workprofile.ProfileStatistics.SeqTrimNumOfCommands.NumOfSucceededCommands


        self.TF.logger.Message("%-35s: %s"%('FlushCacheCommands: ', workprofile.ProfileStatistics.FlushCacheNumOfCommands.NumOfSucceededCommands))
        AllProfile['FlushCacheCommands'] += workprofile.ProfileStatistics.FlushCacheNumOfCommands.NumOfSucceededCommands

        self.TF.logger.Message("%-35s: %s"%('TotalCommands: ', workprofile.ProfileStatistics.TotalNumOfCommands.NumOfSucceededCommands))

        self.TF.logger.Message("%-35s: %s"%('TotalLastReReadMBs: ', workprofile.ProfileStatistics.NumOfTotalReReadMB))
        self.TF.logger.Message("%-35s: %s"%('LastReSendNumOfCommands: ', workprofile.ProfileStatistics.LastReSendNumOfCommands.NumOfSucceededCommands))
        AllProfile['TotalCommands'] += workprofile.ProfileStatistics.TotalNumOfCommands.NumOfSucceededCommands

    self.TF.logger.Message("\n\n******** Total Workload Statistics from above profiles ********\n\n")

    for statparam , statvalue in list(AllProfile.items()):
        self.TF.logger.Message("%-35s: %s"%(statparam, statvalue))

    self.TF.logger.Message("\n\n******** END PROFILE RESPONSE STATISTICS ********\n\n")

    DumpWorkloadStatistics(self, self.workFlowStatus.objOutputData.WorkloadResponse.OverallWorkloadInfo)

    DumpSubmissionQueueStatistics(self)

def DumpWorkloadStatistics(self,Workload):

    self.TF.logger.Message("\n\n******** START WORKLOAD STATISTICS (From Driver Loop) ********\n")


    self.TF.logger.Message("%-35s: %s"%('IOPS: ', Workload.ProfileStatistics.Kiops))


    self.TF.logger.Message("%-35s: %s"%('TotalRunTimeinSec: ', Workload.ProfileStatistics.TotalRuntimeSec))
    self.TF.logger.Message("%-35s: %s"%('AverageReadTimeMicroSeconds: ', Workload.ProfileStatistics.ReadAverageTimeMicroSec))
    self.TF.logger.Message("%-35s: %s"%('AverageWriteTimeMicroSeconds: ', Workload.ProfileStatistics.WriteAverageTimeMicroSec))


    self.TF.logger.Message("%-35s: %s"%('TotalWriteMBs: ', Workload.ProfileStatistics.NumOfTotalWriteMB))
    self.TF.logger.Message("%-35s: %s"%('TotalReadMBs: ', Workload.ProfileStatistics.NumOfTotalReadMB))
    self.TF.logger.Message("%-35s: %s"%('TotalTrimMBs: ', Workload.ProfileStatistics.NumOfTotalTrimMB))



    self.TF.logger.Message("%-35s: %s"%('RandomReadCommands: ', Workload.ProfileStatistics.RandReadNumOfCommands.NumOfSucceededCommands))
    self.TF.logger.Message("%-35s: %s"%('RandomWriteCommands: ', Workload.ProfileStatistics.RandWriteNumOfCommands.NumOfSucceededCommands))
    self.TF.logger.Message("%-35s: %s"%('RandomTrimCommands: ', Workload.ProfileStatistics.RandTrimNumOfCommands.NumOfSucceededCommands))


    self.TF.logger.Message("%-35s: %s"%('SeqReadCommands: ', Workload.ProfileStatistics.SeqReadNumOfCommands.NumOfSucceededCommands))
    self.TF.logger.Message("%-35s: %s"%('SeqWriteCommands: ', Workload.ProfileStatistics.SeqWriteNumOfCommands.NumOfSucceededCommands))
    self.TF.logger.Message("%-35s: %s"%('SeqTrimCommands: ', Workload.ProfileStatistics.SeqTrimNumOfCommands.NumOfSucceededCommands))


    self.TF.logger.Message("%-35s: %s"%('FlushCacheCommands: ', Workload.ProfileStatistics.FlushCacheNumOfCommands.NumOfSucceededCommands))

    self.TF.logger.Message("%-35s: %s"%('TotalCommands: ', Workload.ProfileStatistics.TotalNumOfCommands.NumOfSucceededCommands))

    self.TF.logger.Message("%-35s: %s"%('TotalLastReReadMBs: ', Workload.ProfileStatistics.NumOfTotalReReadMB))
    self.TF.logger.Message("%-35s: %s"%('LastReSendNumOfCommands: ', Workload.ProfileStatistics.LastReSendNumOfCommands.NumOfSucceededCommands))

    self.TF.logger.Message("\n******** Total Workload Statistics from above profiles ********\n")


    self.TF.logger.Message("\n******** END WORKLOAD STATISTICS ********\n")

def DumpSubmissionQueueStatistics(self):
    self.TF.logger.Message("\n\n******** START SUBMISSION QUEUE STATISTICS (Get Device health) ********\n")

    self.TF.logger.Message("Queue -> Commands Processd Count")
    try:
        getDevHealth = NVMeWrap.GetDeviceHealth()
        getDevHealth.Execute()
        getDevHealth.HandleOverlappedExecute()
        getDevHealth.HandleAndParseResponse()
        SQData = getDevHealth.objOutputdata.sqData
        CQData = getDevHealth.objOutputdata.cqData
    except ValidationError.CVFExceptionTypes as exc:
        raise ValidationError.CVFGenericExceptions (self.vtfContainer.GetTestName(), ""+ exc.GetFailureDescription())
    except:
        self.TF.logger.Info("","UnHandled Exception in DumpDLStat.py")

    queuecount = 0
    queuestring = ""

    for Queue in SQData:
        queuecount += 1
        queuestring += "%s ->  %s \t\t\t"%(str(Queue.queueID),str(Queue.commandsProccessedCount))

        if queuecount % 8 == 0:
            self.TF.logger.Message("%s"%(queuestring))
            queuecount = 0
            queuestring = ""

    self.TF.logger.Message("\n\n******** END SUBMISSION QUEUE STATISTICS  ********\n")

    self.TF.logger.Message("\n\n******** START Completion QUEUE STATISTICS (Get Device health) ********\n")

    self.TF.logger.Message("Queue -> Commands Processd Count")
    queuecount = 0
    queuestring = ""

    for Queue in CQData:
        queuecount += 1
        queuestring += "%s ->  %s \t\t\t"%(str(Queue.queueID),str(Queue.commandsProccessedCount))

        if queuecount % 8 == 0:
            self.TF.logger.Message("%s"%(queuestring))
            queuecount = 0
            queuestring = ""

    self.TF.logger.Message("\n\n******** END SUBMISSION QUEUE STATISTICS  ********\n")


