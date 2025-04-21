"""
################################################################################
# Copyright (c) SanDisk Corp.2013 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# FILE:CVFramework.py: Factory Method for CVF product lines.
#                  AUTHOR: Balraj/Ravi
################################################################################
"""

## VTF Lib
from builtins import object
import sys
import Validation.CVFTestFactory as FactoryMethod
import Core.Configuration as Configuration
import Core.ProtocolFactory as ProtocolFactory

sysConfig = Configuration.ConfigurationManager().GetSystemConfiguration()
vtf_container = ProtocolFactory.ProtocolFactory.createVTFContainer(sysConfig.protocol)

exportProtocolName = (vtf_container.systemCfg.protocol).upper()

#**************************************************************************************************************
##
# @brief Runs all the variations in the testObject
# @details
# @return None
# @exception None
#**************************************************************************************************************
class CVFTestFixture(object):

    def __init__(self, testOptions = None, testName = None):
        pass

    def CVFLogTestEnvironment(self):

        import socket
        import datetime
        import multiprocessing
        import os
        import sys
        import platform
        #import Validation.SATA.PlatformUtils as PU
        exec("from Validation.{0} import PlatformUtils as PU".format(exportProtocolName))

        self.hostname = socket.gethostname()
        PUObj = PU.PlatformUtils()
        IP = PUObj.GetIPAddress()
        self.PID = os.getpid()

        self.nrOfCPUCores = PUObj.GetCPUCores()
        totalMemory, availableMemory = PUObj.GetMemoryDetails()

        if  self.isAsynchronousMode == '0':
            self.logger.Message("\n\n### COMMAND MANAGER IS RUNNING IN SYNC MODE###")
        else:
            self.logger.Message("\n\n### COMMAND MANAGER IS RUNNING IN ASYNC MODE###")

        self.logger.Message("\n\n################### TEST ENVIRONMENT ###################\n")

        self.logger.Message("%-35s: %s"%('Python Version', sys.version[0:5]))
        self.logger.Message("%-35s: %s"%('Host OS', platform.platform() + ', ' + platform.machine()))
        self.logger.Message("%-35s: %s"%('Number of CPU Cores', self.nrOfCPUCores))
        self.logger.Message("%-35s: %s"%('Total Physical Memory', totalMemory))
        self.logger.Message("%-35s: %s"%('Available Physical Memory', availableMemory))

        self.logger.Message("\n################### DEVICE CAPABILITIES ###################\n")
        if(0): #DEVICE relatest parameters has not been populated so far ----Identify SATA ????
            self.logger.Message("%-35s: 0x%X"%('PCIe Vendor ID', self.vendorID))
        if self.VTFContainer.IsModel:
            self.logger.Message("\n################### Model : DEVICE CAPABILITIES ###################\n")
            if(0):
                self.logger.Message("%-35s: %s"%("Model Init State", self.modelNum[self.modelNum.lower().find('rom'):][:8]))
                self.logger.Message("%-35s: %s"%('Firmware Revision', self.fwRevision))
                self.logger.Message("%-35s: %s"%('MaximumDataTransSize-MDTS', self.MDTS))
