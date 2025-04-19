"""
################################################################################
# Copyright (c) SanDisk Corp.2013 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# FILE:CVFTestFactory.py: Factory Method for CVF product lines.
#                  AUTHOR: Joydip/Ravi
# Description : This file is designed in such a way that it will automatically take the
# protocal name and import the respective Protocol Library File.
# It is highly recommended that users should not change anything in this file, as a small
# change can break many things in other protocols. Any change to this file has to be done
# via proper review and inform others also.
################################################################################
"""

## VTF Lib

from builtins import object
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
class CVFTestFactory(object):

    __staticObjTestFactory           = None
    __staticCVFTestFactoryObjectCreated   = False

    def __new__(cls, *args, **kwargs):
        """
           Memory allocation ( This function use to create Singleton object of SystemVars)
        """
        if not CVFTestFactory.__staticObjTestFactory:
            CVFTestFactory.__staticObjTestFactory = super(CVFTestFactory, cls).__new__(cls, *args, **kwargs)
        return CVFTestFactory.__staticObjTestFactory

    def __init__(self, testOptions = None, testName = None):

        #Condition to check if the variable is already created
        if CVFTestFactory.__staticCVFTestFactoryObjectCreated:
            return
        exportProtocolName = (vtf_container.systemCfg.protocol).upper()

        if exportProtocolName == "NVME_OF_SDPCIE":
            exportProtocolName = "NVMe"
        if exportProtocolName == "SD_OF_SDPCIE":
            exportProtocolName = "SD"

        exec("from Validation.{0} import TestFixture as TestFixture".format(exportProtocolName), globals())
        exec("from Validation.{0} import RWCLib as RWCLib".format(exportProtocolName), globals())
        exec("from Validation.{0} import CMDUtil as CMDUtil".format(exportProtocolName), globals())
        exec("from Validation.{0} import TestParams as TestParams".format(exportProtocolName), globals())
        exec("from Validation.{0} import SecurityCMDUtil as SECUCMDUtil".format(exportProtocolName), globals())
        exec("from Validation.{0} import SctpUtils as SctpUtils".format(exportProtocolName), globals())
        exec("from Validation.{0} import PlatformUtils as PlatformUtils".format(exportProtocolName), globals())
        #exec("from Validation.{0} import SpecSATA as SpecSATA".format(exportProtocolName)) #???? for Jenkins setup--Temp:changes

        #Set the static variable of class such that the object gets created ONLY once
        CVFTestFactory.__staticCVFTestFactoryObjectCreated = True
        super(CVFTestFactory, self).__init__()

        self.factory = genericFunc()
        self.ProtocolName = exportProtocolName

        self.factory.PlatformUtils = PlatformUtils.PlatformUtils()
        self.factory.TestFixture = TestFixture.TestFixture()
        self.factory.TestParams = TestParams
        self.factory.SATA_RWCLib = RWCLib.RWCLib()
        #self.factory.SpecSATA = SpecSATA.SpecSATA() #???? for Jenkins setup--Temp:changes

        self.factory.CMDUtil = CMDUtil.CMDUtil()
        #self.factory.SpecSATA = SpecSATA.SpecSATA()
        self.factory.SECUCMDUtil = SECUCMDUtil.SECUCMDUtil()
        self.factory.SctpUtils = SctpUtils.SctpUtils()




        #return self.factory


    def GetProtocolLib(self):



        self.factory.TestFixture = self.factory.TestFixture#()
        self.factory.TestParams = self.factory.TestParams#()
        if(0):
            self.factory.SATA_RWCLib = self.factory.RWCLib()
            self.factory.CMDUtil = self.factory.CMDUtil()
            self.factory.SECUCMDUtil = self.factory.SECUCMDUtil()
            self.factory.SctpUtils = self.factory.SctpUtils()
            self.factory.PlatformUtils = self.factory.PlatformUtils()

        return self.factory


# Abstract Class
class CVFElementFactory(object):
    def TestFixture(self): pass
    def PlatformUtils(self): pass

class genericFunc(CVFElementFactory):
    def _init_(self):
        self.Protocol.TestFixture =  self.factory.TestFixture()
        self.Protocol.TP = None
        self.Protocol.RWCLib = None
        self.Protocol.CMDUtil = None
        self.Protocol.SECUCMDUtil = None
        self.Protocol.PlatformUtils = None


    def TestFixture(self):
        return TestFixture.TestFixture()

    def TestParams(self):
        return TestParams

    def RWCLib(self):
        return RWCLib.RWCLib()

    def CMDUtil(self):
        return CMDUtil.CMDUtil()

    def SECUCMDUtil(self):
        return SECUCMDUtil.SECUCMDUtil()

    def SctpUtils(self):
        return SctpUtils.SctpUtils()

    def PlatformUtils(self):
        return PlatformUtils.PlatformUtils()


