"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : CMD20_CA01_SDMode.st3
# SCRIPTER SCRIPT                : CMD20_UT01_LoadCMD20_Variables.st3
# CVF CALL ALL SCRIPT            : CMD20_CA01_SDMode.py
# CVF SCRIPT                     : CMD20_UT01_LoadCMD20_Variables.py
# DESCRIPTION                    :
# PRERQUISTE                     : CMD20_UT08_AUSize_Calculation.py
# STANDALONE EXECUTION           : No. It is an utility script.
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : Nov-2022
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
import CMD20_UT08_AUSize_Calculation as AuSizeCalculation

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

# Global Variables

# Testcase Utility Class - Begins
class CMD20_UT01_LoadCMD20_Variables(customize_log):
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
        self.__ausize = AuSizeCalculation.CMD20_UT08_AUSize_Calculation(self.vtfContainer)

    # Testcase Utility Logic - Starts

    def Run(self):
        """
        Name : Run
        """
        U = self.__sdCmdObj.MaxLba()

        CMD20Variables = {}
        # ReadType: 1 = ReadAll
        CMD20Variables['ReadType'] = 1

        # RU Sequence = 1
        CMD20Variables['RuSequence'] = 1

        # ExpectSequence: 1 = In Sequence, 2 = Out of sequence
        CMD20Variables['ExpectSequence'] = 1

        CMD20Variables['RuNumber'] = 0

        # Call GET FAT ADDRESSES
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Call GetFatAddress routine to get CMD20 Variables.\n")
        FatAddresses = self.__dvtLib.GetFatAddr()

        CMD20Variables['FatStartAdress'] = FatAddresses['FAT_start_address']
        CMD20Variables['FatSize'] = FatAddresses['FAT_size']
        CMD20Variables['DIRconstAddress'] = old_div(U,2)
        CMD20Variables['BitmapBlockCount'] = FatAddresses['BitMap_size']
        CMD20Variables['BitmapStartAddress'] = FatAddresses['BitMap_start_address']
        CMD20Variables['Lba_of_first_AU'] = FatAddresses['LBA_of_first_AU']

        if not CMD20Variables['BitmapBlockCount']:
            CMD20Variables['BitmapRandomAddress'] = 0x0 + CMD20Variables['BitmapStartAddress']
        else:
            CMD20Variables['BitmapRandomAddress'] = random.randrange(0, CMD20Variables['BitmapBlockCount'])  + CMD20Variables['BitmapStartAddress']

        CMD20Variables['FatRandomAddress'] = CMD20Variables['FatStartAdress']
        CMD20Variables['RU'] = 0x200
        CMD20Variables['Offset'] = ((CMD20Variables['RuNumber']*CMD20Variables['RU']) + CMD20Variables['RU'])

        # Call Utility AU Size CalCulation
        AU = self.__ausize.Run(ret = 1)
        CMD20Variables['AU'] = AU
        NumOfAU = old_div((U - CMD20Variables['Lba_of_first_AU']),CMD20Variables['AU'])
        CMD20Variables['NumOfAU'] = NumOfAU
        RuStartBlock = ((random.randrange(0, NumOfAU - 1)) * AU) + CMD20Variables['Lba_of_first_AU']
        CMD20Variables['RuStartBlock'] = RuStartBlock
        CMD20Variables['RUStartBlockRead'] = RuStartBlock
        CMD20Variables['CiStartBlock'] = (old_div((U - AU), AU)) * AU
        CMD20Variables['FatUpdateFatSize'] = random.randrange(0, 32) + 1
        CMD20Variables['FatUpdateBitmapSize'] = random.randrange(0, 32) + 1
        CMD20Variables['AllowedCommand'] = 0
        CMD20Variables['NotAllowedCommand'] = 0

        return CMD20Variables
    # Testcase Utility Logic - Ends
# Testcase Utility Class - Ends


# CVF Hook Class - Starts
class MainClass(TestCase.TestCase, customize_log):

    # Act as a Constructor
    def setUp(self):
        pass

    # CVF Hook Function: [CVF hook function should start with "test"]
    def test_CMD20_UT01_LoadCMD20_Variables(self):
        obj = CMD20_UT01_LoadCMD20_Variables(self.vtfContainer)
        obj.Run()

# CVF Hook Class - Ends
