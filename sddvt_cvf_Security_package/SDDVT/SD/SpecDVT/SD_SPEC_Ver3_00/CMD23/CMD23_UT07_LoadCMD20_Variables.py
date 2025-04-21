"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                :
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : CMD23_UT07_LoadCMD20_Variables.py
# DESCRIPTION                    :
# PRERQUISTE                     :
# STANDALONE EXECUTION           : No. It is an utility script.
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sushmitha P.S
# REVIEWED BY                    : Sivagurunathan
# DATE                           : 05-Jun-2024
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
from inspect import currentframe, getframeinfo

# SDDVT - Dependent TestCases
import CMD23_UT02_AUSize_Calculation as AUSizeCalculation

# Global Variables

# Testcase Utility Class - Begins

class CMD23_UT07_LoadCMD20_Variables(customize_log):
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
        self.__ErrorManager = self.vtfContainer.device_session.GetErrorManager()

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

        ###### Check and Switch to SD Protocol ######
        self.protocolName = self.__dvtLib.switchProtocol(ScriptName = self.__testName)

        ###### Customize Log ######
        self.fn = os.path.basename(getframeinfo(currentframe()).filename)
        customize_log.__init__(self, self.__TF)

        ###### Testcase Specific Variables ######
        self.__AUSize = AUSizeCalculation.CMD23_UT02_AUSize_Calculation(self.vtfContainer)

    # Testcase Utility Logic - Starts

    def Run(self):
        """
        Name : Run
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Utility Execution Started " + "-" * 20 + "\n")

        U = self.__cardMaxLba

        # Populate the variable declarations into dictionary CMD20Variables[{} and return.
        CMD20Variables = {}
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ReadType: 1 = ReadAll ")
        CMD20Variables['ReadType']   = 1

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RU Sequence = 1, RU after RU, AU after RU, RuSequence = 0, Jump to random free AU")
        CMD20Variables['RuSequence'] = 1

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ExpectSequence: 1 = In Sequence, 2 = Out of sequence ")
        RUNumber             = 0
        CMD20Variables['ExpectSequence']      = 1
        CMD20Variables['RuNumber']            = RUNumber

        CMD20Variables['FatStartAdress'] = 0x0
        CMD20Variables['FatSize'] = 0x0
        CMD20Variables['DIRconstAddress'] = old_div(U,2)
        CMD20Variables['BitmapStartAddress'] = 0x0
        CMD20Variables['BitmapBlockCount'] = 0x0
        CMD20Variables['Lba_of_first_AU'] = 0x0

        # Call GET FAT ADDRESSES
        FatAddresses = self.__dvtLib.GetFatAddr()

        # Variable declaration
        CMD20Variables['BitmapRandomAddress']  = random.randrange(0,FatAddresses['BitMap_size']) + FatAddresses['BitMap_start_address']
        CMD20Variables['FatRandomAddress']     = FatAddresses['FAT_start_address']
        RU       = 0x200
        CMD20Variables['RU']                   = 0x200
        CMD20Variables['Offset']               = CMD20Variables['RuNumber']*CMD20Variables['RU'] + CMD20Variables['RU']
        AU                                     = self.__AUSize.Run( ret = 1)
        CMD20Variables['AU']                   = AU
        NumOfAU                                = old_div((U - FatAddresses['LBA_of_first_AU']),CMD20Variables['AU'])
        CMD20Variables['NumOfAU']              = NumOfAU
        RuStartBlock                           = (random.randrange(0,NumOfAU) * AU) + FatAddresses['LBA_of_first_AU']
        CMD20Variables['RuStartBlock']         = RuStartBlock
        CMD20Variables['RUStartBlockRead']     = RuStartBlock
        CMD20Variables['CiStartBlock']         = old_div((U - AU), AU) * AU
        CMD20Variables['FatUpdateFatSize']     = random.randrange(0,32) + 1
        CMD20Variables['FatUpdateBitmapSize']  = random.randrange(0,32) + 1
        CMD20Variables['AllowedCommand']       = 0
        CMD20Variables['NotAllowedCommand']    = 0

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "BitmapRandomAddress %d" %CMD20Variables['BitmapRandomAddress'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FatRandomAddress %d" %CMD20Variables['FatRandomAddress'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RU %d" %CMD20Variables['RU'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Offset %d" %CMD20Variables['Offset'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "AU %d" %CMD20Variables['AU'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "NumOfAU %d" %CMD20Variables['NumOfAU'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RuStartBlock %d" %CMD20Variables['RuStartBlock'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RUStartBlockRead %d" %CMD20Variables['RUStartBlockRead'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CiStartBlock %d" %CMD20Variables['CiStartBlock'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FatUpdateFatSize %d" %CMD20Variables['FatUpdateFatSize'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FatUpdateBitmapSize %d" %CMD20Variables['FatUpdateBitmapSize'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "AllowedCommand %d" %CMD20Variables['AllowedCommand'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "NotAllowedCommand %d" %CMD20Variables['NotAllowedCommand'])

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Utility Execution Completed " + "-" * 20 + "\n")
        return CMD20Variables

    #End of Run function
#End of LoadCMD20Variables


    # Testcase Utility Logic - Ends

# Testcase Utility Class - Ends