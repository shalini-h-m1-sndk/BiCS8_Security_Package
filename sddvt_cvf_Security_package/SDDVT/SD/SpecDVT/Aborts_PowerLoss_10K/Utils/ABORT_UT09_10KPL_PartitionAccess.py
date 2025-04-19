"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : ABORT_TC001_10K_PowerLossTest.st3
# SCRIPTER SCRIPT                : ABORT_UT09_10KPL_PartitionAccess.st3
# CVF CALL ALL SCRIPT            : ABORT_TC001_10K_PowerLossTest.py
# CVF SCRIPT                     : ABORT_UT09_10KPL_PartitionAccess.py
# DESCRIPTION                    : The purpose of this utility script is to access the partition and update the g_CurrentPartSize variable (OOR Patch assistant)
                                   NOTE : This script is valid for MMC Cards. Hence, Functionality verification has not been done.
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 27/06/2022
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
    from builtins import *
from past.utils import old_div

# SDDVT - Dependent TestCases

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
from inspect import currentframe, getframeinfo

# Global Variables


class ABORT_UT09_10KPL_PartitionAccess(customize_log):
    """
    class for Defining Write operation that can be used by
    Main scripts
    """

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
        # self.__ErrorManager = self.vtfContainer.device_session.GetErrorManager()

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

        ###### Customize Log ######
        self.fn = os.path.basename(getframeinfo(currentframe()).filename)
        customize_log.__init__(self, self.__TF)

        ##### Testcase Specific Variables #####


    def Run(self, partitionID):
        readBuffer = ServiceWrap.Buffer.CreateBuffer(0x1, 0)
        # TOBEDONE : MMCGetExtCsd
        #self.__card.MMCGetExtCsd(readBuffer)
        raise ValidationError.TestFailError(self.fn, "Yet to implement CVF API MMCGetExtCsd")

        # TOBEDONE : partitionConfig declaration
        # Run MMC GET EXD.CSD cmd and get the partitionConfig value
        partitionConfig = partitionConfig & 0xF8
        partitionConfig = partitionConfig | partitionID
        globalWriteTO  = int(self.__config.get('globalWriteTO'))
        tempglobalWriteTO = globalWriteTO

        # Run MMC GET EXD.CSD cmd and get the globalSpecEnum value
        # TOBEDONE : globalSpecEnum declaration
        if globalSpecEnum >= 5:
            # TOBEDONE : MMCGetExtCsd
            #self.__card.MMCGetExtCsd(readBuffer)
            # raise ValidationError.TestFailError(self.fn, "Yet to implement CVF API MMCGetExtCsd")

            # TOBEDONE : PARTITION_SWITCH_TIME declaration
            # Run MMC GET EXD.CSD cmd and get the PARTITION_SWITCH_TIME value
            tempglobalWriteTO = PARTITION_SWITCH_TIME * 10

        # Set Time Out
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Setting TimeOut")
        self.__dvtLib.SetTimeOut(int(self.__config.get('globalResetTO')), tempglobalWriteTO, int(self.__config.get('globalReadTO')))

        # TOBEDONE: eMMC Partion config
        raise ValidationError.TestFailError(self.fn, "Yet to implement CVF API eMMC Partion config")

        # Set Time Out
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Setting TimeOut")

        self.__dvtLib.SetTimeOut(int(self.__config.get('globalResetTO')), int(self.__config.get('globalReadTO')),
                                 int(self.__config.get('globalWriteTO')))

        # TOBEDONE : MMCGetExtCsd
        #self.__card.MMCGetExtCsd(readBuffer)
        raise ValidationError.TestFailError(self.fn, "Yet to implement CVF API MMCGetExtCsd")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Update the size of the current partition")

        # Get g_CurrentPartSize value based on partitionID
        if (partitionID == 0):
            g_CurrentPartSize = self.__cardMaxLba
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CurrentPartSize: %d" % g_CurrentPartSize)

        # Get g_CurrentPartSize value based on partitionID
        if (partitionID == 1) or (partitionID == 2):
            # TOBEDONE : MMCGetExtCsd
            #self.__card.MMCGetExtCsd(readBuffer)
            raise ValidationError.TestFailError(self.fn, "Yet to implement CVF API MMCGetExtCsd")

            # TOBEDONE : bootPartSize declaration
            # Run MMC GET EXD.CSD cmd and get the bootPartSize value
            g_CurrentPartSize = old_div(bootPartSize * 128 * 1024, 512)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CurrentPartSize: %d" % g_CurrentPartSize)

            # Get g_CurrentPartSize value based on partitionID
        if (partitionID == 3):
            # TOBEDONE : MMCGetExtCsd
            #self.__card.MMCGetExtCsd(readBuffer)
            raise ValidationError.TestFailError(self.fn, "Yet to implement CVF API MMCGetExtCsd")

            # TOBEDONE : RPMBSize declaration
            # Run MMC GET EXD.CSD cmd and get the RPMBSize value
            g_CurrentPartSize = old_div(2 * RPMBSize * 128 * 1024, 512)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CurrentPartSize: %d" % g_CurrentPartSize)

        if (partitionID > 3):
            #eMMC Patrion Retrieve:
            # TOBEDONE: eMMC Patrion Retrieve
            raise ValidationError.TestFailError(self.fn, "Yet to implement CVF API eMMC Patrion Retrieve")

            currentGPPID = partitionID - 3
            newVarName = GPP + currentGPPID + _Size
            #calculation of W
            #writeBlockLen  = CSD_WRITE_BL_LEN / DEFAULT_BLK_LEN(0x200)
            #sizeOfErasableSec = writeBlockLen * (CSD_SECTOR_SIZE + 1)
            #wpGroupSize = CSD_WP_GRP_SIZE + 1
            #W =  wpGroupSize * sizeOfErasableSec

            #As per Scripter value of W = 0x80
            W = 0x80
            # TOBEDONE: Exact calculation of W
            g_CurrentPartSize = newVarName * W

        return g_CurrentPartSize


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_ABORT_UT09_10KPL_PartitionAccess(self):
        obj = ABORT_UT09_10KPL_PartitionAccess(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
