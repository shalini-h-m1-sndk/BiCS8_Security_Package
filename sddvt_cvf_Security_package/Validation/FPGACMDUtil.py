"""
################################################################################
# Copyright (c) SanDisk Corp.2013 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# FILE:FPGACMDUtil.py: CMD Utility Specific to FPGA.
#              AUTHOR: Ravi G
################################################################################

################################################################################
#                            CHANGE HISTORY
# 16-JANUARY-2019    RG  Initial Revision of FPGACMDUtil.py
################################################################################
"""
from builtins import object
import CTFServiceWrapper as ServiceWrap
import NVMeCMDWrapper as NVMeWrap
import Gen4FPGAWrapper as FPGAWrapper
import Core.ValidationError as ValidationError
import Protocol.NVMe.Basic.VTFContainer as VTF

import Validation.TestFixture as TestFixture
import Validation.CMDUtil as CU

class FPGACMDUtil(object):

    def __init__(self):

        self.TF = TestFixture.TestFixture()

    def GSD(self, T1Delay = 50, T2Delay = 50, isAsync = True, sendType = ServiceWrap.SEND_QUEUED):

        shutdownType = ServiceWrap.SHUTDOWN_TYPE.GRACEFUL
        powerCycleParams = ServiceWrap.FPGA_TESTER_POWER_CYCLE_PARAMS()
        powerCycleParams.ui32T1Delay = T1Delay
        powerCycleParams.ui32T2Delay = T2Delay

        hardwareParams = ServiceWrap.HARDWARE_SPECIFIC_PARAMS()
        hardwareParams.paramType = ServiceWrap.HARDWARE_SPECIFIC_PARAM_TYPE.FPGA_TESTER_POWER_CYCLE
        hardwareParams.gen4PowerCycleParams = powerCycleParams

        self.logger.Info("", "Posting GSD")

        try:
            ServiceWrap.PowerCycle(shutdownType, hardwareParams, isAsync = isAsync, sendType = sendType)
        except ValidationError.CVFExceptionTypes as exc:
            raise ValidationError.VtfGeneralError("GSD",exc.GetFailureDescription())

        self.logger.Info("","GSD completed successfullly\n")

        if not int(self.TF.configParser.GetValue('enable_automatic_io_queue_creation', 0)[0]):
            self.CMDUtil.CreateIOQsReinitCmdMgr()

    def UGSD(self, T1Delay = 50, T2Delay = 50, isAsync = True, sendType = ServiceWrap.SEND_QUEUED):

        shutdownType = ServiceWrap.SHUTDOWN_TYPE.UNGRACEFUL
        powerCycleParams = ServiceWrap.FPGA_TESTER_POWER_CYCLE_PARAMS()
        powerCycleParams.ui32T1Delay = T1Delay
        powerCycleParams.ui32T2Delay = T2Delay

        hardwareParams = ServiceWrap.HARDWARE_SPECIFIC_PARAMS()
        hardwareParams.paramType = ServiceWrap.HARDWARE_SPECIFIC_PARAM_TYPE.FPGA_TESTER_POWER_CYCLE
        hardwareParams.gen4PowerCycleParams = powerCycleParams

        self.logger.Info("", "Posting UGSD")

        try:
            ServiceWrap.PowerCycle(shutdownType, hardwareParams, isAsync = isAsync, sendType = sendType)
        except ValidationError.CVFExceptionTypes as exc:
            raise ValidationError.VtfGeneralError("UGSD",exc.GetFailureDescription())

        self.logger.Info("","UGSD completed successfullly\n")

        if not int(self.TF.configParser.GetValue('enable_automatic_io_queue_creation', 0)[0]):
            self.CMDUtil.CreateIOQsReinitCmdMgr()

    def HotReset(self, T1Delay = 50, T2Delay = 50, isAsync = True, sendType = ServiceWrap.SEND_QUEUED):

        resetType = ServiceWrap.FPGA_TESTER_HOT_RESET
        resetParams = ServiceWrap.HOT_RESET_PARAMS
        resetParams.ui32T1Delay = T1Delay
        resetParams.ui32T2Delay = T2Delay

        self.logger.Info("", "Posting Hot Reset")

        try:
            FPGAWrapper.PCIeHotReset(HOT_RESET_PARAMS = resetParams, bIsAsync = self.isAsync, sendType = sendType)
        except ValidationError.CVFExceptionTypes as exc:
            raise ValidationError.VtfGeneralError("Hot Reset",exc.GetFailureDescription())

        self.logger.Info("","Hot Reset completed successfullly\n")

        if not int(self.TF.configParser.GetValue('enable_automatic_io_queue_creation', 0)[0]):
            self.CMDUtil.CreateIOQsReinitCmdMgr()