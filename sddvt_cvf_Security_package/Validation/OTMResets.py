"""
################################################################################
# Copyright (c) SanDisk Corp.2013 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# FILE: OTMResets.py
#This Script implements ResetsOnResets in OTM Callback Mechanism.

################################################################################
"""
import Protocol.NVMe.Basic.TestCase as TestCase
import Core.ValidationError as ValidationError
import CTFServiceWrapper as ServiceWrap
import NVMeCMDWrapper as NVMeWrap

import RWCLib as RWCLib
import TestFixture as TestFixture
import CMDUtil as CMDUtil
import Validation.TestParams as TP

class OTMResets(TestCase.TestCase):

    def setUp(self):

        self.TF = TestFixture.TestFixture()
        self.CU = CMDUtil.CMDUtil()
        self.OTM_TAG = "OTM_TRACE"
        self.TF.logger.SetTaggedDebugLevel(self.OTM_TAG, ServiceWrap.LOG_LEVEL_INFO, False)
        self.logger.Info(self.OTM_TAG,"OTM_Count func is called")
        self.isDeterministic = int(self.TF.configParser.GetValue('thread_pool_deterministic', 0)[0])

    def FLRonNSSR(self):

        self.logger.Info(self.OTM_TAG,"OTM Call Back: Posting FLRonNSSR from OTM call back")
        try:
            self.TF.logger.Fatal("Posting PCIeHotReset during NSSR in Async SEND_QUEUED %s Mode\n" % "DETERMINISTIC" if self.isDeterministic else "NON DETERMINISTIC")
            NVMeWrap.ResetInReset(NVMeWrap.eResetType.SUBSYSTEM_RESET,
                                  NVMeWrap.eResetType.PCIe_FLR_RESET, 1, bIsAsync = True,
                                  sendType=ServiceWrap.SEND_QUEUED)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in FLRonNSSR ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        self.logger.Info(self.OTM_TAG,"OTM Call Back: FLRonNSSR Completed from OTM call back")

    def SyncFLRonNSSR(self):

        self.logger.Info(self.OTM_TAG,"OTM Call Back: Posting FLRonNSSR from OTM call back")
        try:
            self.TF.logger.Fatal("Posting PCIe_FLR_RESET during NSSR in Sync SEND_QUEUED %s Mode\n" % "DETERMINISTIC" if self.isDeterministic else "NON DETERMINISTIC")
            NVMeWrap.ResetInReset(NVMeWrap.eResetType.SUBSYSTEM_RESET, NVMeWrap.eResetType.PCIe_FLR_RESET, 5, bIsAsync = False, sendType=ServiceWrap.SEND_QUEUED)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in FLRonNSSR ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        self.logger.Info(self.OTM_TAG,"OTM Call Back: FLRonNSSR Completed from OTM call back")

    def FLRonNSSRIMD(self):

        self.logger.Info(self.OTM_TAG,"OTM Call Back: Posting FLRonNSSR from OTM call back")
        try:
            self.TF.logger.Fatal("Posting PCIe_FLR_RESET during NSSR in Async SEND_IMMEDIATE %s Mode\n" % "DETERMINISTIC" if self.isDeterministic else "NON DETERMINISTIC")
            NVMeWrap.ResetInReset(NVMeWrap.eResetType.SUBSYSTEM_RESET, NVMeWrap.eResetType.PCIe_FLR_RESET, 1, bIsAsync = True, sendType=ServiceWrap.SEND_IMMEDIATE)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in FLRonNSSR ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        self.logger.Info(self.OTM_TAG,"OTM Call Back: FLRonNSSR Completed from OTM call back")

    def SyncFLRonNSSRIMD(self):

        self.logger.Info(self.OTM_TAG,"OTM Call Back: Posting FLRonNSSR from OTM call back")
        try:
            self.TF.logger.Fatal("Posting PCIe_FLR_RESET during NSSR in Sync SEND_IMMEDIATE %s Mode\n" % "DETERMINISTIC" if self.isDeterministic else "NON DETERMINISTIC")
            NVMeWrap.ResetInReset(NVMeWrap.eResetType.SUBSYSTEM_RESET, NVMeWrap.eResetType.PCIe_FLR_RESET, 5, bIsAsync = False, sendType=ServiceWrap.SEND_IMMEDIATE)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in FLRonNSSR ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        self.logger.Info(self.OTM_TAG,"OTM Call Back: FLRonNSSR Completed from OTM call back")

    def PCIeonNSSR(self):

        self.logger.Info(self.OTM_TAG,"OTM Call Back: Posting PCIeonNSSR from OTM call back")
        try:
            self.TF.logger.Fatal("Posting PCIe_FLR_RESET during NSSR in Sync SEND_IMMEDIATE %s Mode\n" % "DETERMINISTIC" if self.isDeterministic else "NON DETERMINISTIC")
            NVMeWrap.ResetInReset(NVMeWrap.eResetType.SUBSYSTEM_RESET, NVMeWrap.eResetType.PCIe_HOT_RESET, 5, bIsAsync = True, sendType=ServiceWrap.SEND_IMMEDIATE)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in FLRonNSSR ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        self.logger.Info(self.OTM_TAG,"OTM Call Back: PCIeonNSSR Completed from OTM call back")

    def SyncPCIeonNSSR(self):

        self.logger.Info(self.OTM_TAG,"OTM Call Back: Posting SyncPCIeonNSSR from OTM call back")
        try:
            self.TF.logger.Fatal("Posting PCIe_FLR_RESET during NSSR in Sync SEND_IMMEDIATE %s Mode\n" % "DETERMINISTIC" if self.isDeterministic else "NON DETERMINISTIC")
            NVMeWrap.ResetInReset(NVMeWrap.eResetType.SUBSYSTEM_RESET, NVMeWrap.eResetType.PCIe_HOT_RESET, 5, bIsAsync = False, sendType=ServiceWrap.SEND_IMMEDIATE)
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in FLRonNSSR ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

        self.logger.Info(self.OTM_TAG,"OTM Call Back: SyncPCIeonNSSR Completed from OTM call back")