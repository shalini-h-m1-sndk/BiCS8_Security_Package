"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : None
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : WriteReadUtils.py
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : WriteReadUtils.py
# DESCRIPTION                    : Library file for write, read and erase.
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : Nov-2021
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
from future.utils import with_metaclass

# SDDVT - Dependent TestCases

# SDDVT - Common Interface for Testcase
import SDDVT.Common.DvtCommonLib as DvtCommonLib

# SDDVT - SD Specification and commands related Interface
import SDDVT.Common.SDCommandLib as SDCommandLib
# import Validation.ValidationRwcLib as RWCLib

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


ZEROS_PATTERN = 0x00
ONES_PATTERN = 0x1
WORD_REPEATED_PATTERN = [0x00, 0x01]  # Word Fill

# Word Fill Increment
WORD_LBA_PATTERN = [0, 0, 0, 1, 0, 2, 0, 3, 0, 4, 0, 5, 0, 6, 0, 7, 0, 8, 0, 9, 0, 10, 0, 11, 0, 12, 0, 13, 0, 14, 0, 15, 0, 16, 0, 17, 0, 18, 0, 19, 0, 20, 0, 21, 0, 22, 0, 23, 0, 24, 0, 25, 0, 26, 0, 27, 0, 28, 0, 29, 0, 30, 0, 31, 0, 32, 0, 33, 0, 34, 0, 35, 0, 36, 0, 37, 0, 38, 0, 39, 0, 40,
                    0, 41, 0, 42, 0, 43, 0, 44, 0, 45, 0, 46, 0, 47, 0, 48, 0, 49, 0, 50, 0, 51, 0, 52, 0, 53, 0, 54, 0, 55, 0, 56, 0, 57, 0, 58, 0, 59, 0, 60, 0, 61, 0, 62, 0, 63, 0, 64, 0, 65, 0, 66, 0, 67, 0, 68, 0, 69, 0, 70, 0, 71, 0, 72, 0, 73, 0, 74, 0, 75, 0, 76, 0, 77, 0, 78, 0, 79, 0, 80,
                    0, 81, 0, 82, 0, 83, 0, 84, 0, 85, 0, 86, 0, 87, 0, 88, 0, 89, 0, 90, 0, 91, 0, 92, 0, 93, 0, 94, 0, 95, 0, 96, 0, 97, 0, 98, 0, 99, 0, 100, 0, 101, 0, 102, 0, 103, 0, 104, 0, 105, 0, 106, 0, 107, 0, 108, 0, 109, 0, 110, 0, 111, 0, 112, 0, 113, 0, 114, 0, 115, 0, 116, 0, 117, 0,
                    118, 0, 119, 0, 120, 0, 121, 0, 122, 0, 123, 0, 124, 0, 125, 0, 126, 0, 127, 0, 128, 0, 129, 0, 130, 0, 131, 0, 132, 0, 133, 0, 134, 0, 135, 0, 136, 0, 137, 0, 138, 0, 139, 0, 140, 0, 141, 0, 142, 0, 143, 0, 144, 0, 145, 0, 146, 0, 147, 0, 148, 0, 149, 0, 150, 0, 151, 0, 152, 0,
                    153, 0, 154, 0, 155, 0, 156, 0, 157, 0, 158, 0, 159, 0, 160, 0, 161, 0, 162, 0, 163, 0, 164, 0, 165, 0, 166, 0, 167, 0, 168, 0, 169, 0, 170, 0, 171, 0, 172, 0, 173, 0, 174, 0, 175, 0, 176, 0, 177, 0, 178, 0, 179, 0, 180, 0, 181, 0, 182, 0, 183, 0, 184, 0, 185, 0, 186, 0, 187, 0,
                    188, 0, 189, 0, 190, 0, 191, 0, 192, 0, 193, 0, 194, 0, 195, 0, 196, 0, 197, 0, 198, 0, 199, 0, 200, 0, 201, 0, 202, 0, 203, 0, 204, 0, 205, 0, 206, 0, 207, 0, 208, 0, 209, 0, 210, 0, 211, 0, 212, 0, 213, 0, 214, 0, 215, 0, 216, 0, 217, 0, 218, 0, 219, 0, 220, 0, 221, 0, 222, 0,
                    223, 0, 224, 0, 225, 0, 226, 0, 227, 0, 228, 0, 229, 0, 230, 0, 231, 0, 232, 0, 233, 0, 234, 0, 235, 0, 236, 0, 237, 0, 238, 0, 239, 0, 240, 0, 241, 0, 242, 0, 243, 0, 244, 0, 245, 0, 246, 0, 247, 0, 248, 0, 249, 0, 250, 0, 251, 0, 252, 0, 253, 0, 254]
CONSTANT_PATTERN = 0x01  # Constant as per scripter
CONSTANT_NEGATIVE_PATTERN = 0xFE  # Negetive Constant value as per scripter

# Random Pattern
RANDOM_PATTERN_MINIMUM = 0x00
RANDOM_PATTERN_MAXIMUM = 0xFE
RANDOM_PATTERN_INCREMENT = 0x1
RANDOM_PATTERN_DECREMENT = -1


class Singleton(type):
    def __init__(self, *args, **kwargs):
        super(Singleton, self).__init__(*args, **kwargs)
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = super(Singleton, self).__call__(*args, **kwargs)
        return self.instance


class RwcUsageClass(with_metaclass(Singleton, customize_log)):

    def __init__(self, VTFContainer):
        ###### Creating CVF objects ######
        self.vtfContainer = VTFContainer
        self.currCfg = Configuration.ConfigurationManagerInitializer.ConfigurationManager.currentConfiguration
        self.__CVFTestFactory = FactoryMethod.CVFTestFactory().GetProtocolLib()
        self.__TF = self.__CVFTestFactory.TestFixture

        ###### Creating SDDVT objects ######
        self.__sdCmdObj = SDCommandLib.SdCommandClass(self.vtfContainer)
        self.__cardMaxLba = self.__sdCmdObj.MaxLba()
        ###### Customize Log ######
        self.fn = os.path.basename(getframeinfo(currentframe()).filename)
        customize_log.__init__(self, self.__TF)

        ##### Testcase Specific Variables #####


    def GetStartLbaOffset(self):
        """
        This function will give a start lba offset, that can be used when we
        don't want to write/read the whole card.
        If option value "writeReadPercent" is 100% then start lba offset will be 0
        """
        startLbaOffset = int(self.__cardMaxLba - (old_div((self.__cardMaxLba * self.currCfg.variation.writeReadPercent), 100)))
        return startLbaOffset


    def Write(self, startLba, transferLength, userPatternIndex = 3, expectTimeOut = False, forceMultipleWrite = False, dontUpdateCardMap = False):
        """
        Name:             Write
        Description:      Does Write operation card for below patterns.

        Returns: None

        Pattern Usage:
        default userPatternIndex will write Randomdata Pattern as per existing framework
        userPatternIndex = 0 for all 0s                       (Values all 0x0's as per scripter)
        userPatternIndex = 1 for all WORD_REPEATED_PATTERN    (Value 0x00 0x01 repeated word as per scripter)
        userPatternIndex = 2 for all INCREMENTAL              (Values 0x00 to 0xFE as per scripter)
        userPatternIndex = 3 for all RANDOM                   (Values random from 0x00 to 0xFE as per scripter)
        userPatternIndex = 4 for all CONSTANT                 (Value 0x1 as per scripter)
        userPatternIndex = 5 for all 1s                       (Values all 0x1's as per scripter)
        userPatternIndex = 7 for all WORD_LBA_PATTERN         (Value 0x00 0x00, 0x00 0x01 increment word as per scripter)
        userPatternIndex = 8 for all NEGATIVE_INCREMENTAL     (Value 0xFE to 0x00 as per scripter)
        userPatternIndex = 9 for all NEGATIVE_CONSTANT        (Value 0xFE as per scripter)

        Note:
        For below pattern usage, WriteReadUtils can not be used
        FILE - Incorporate in code, fill buffer with file continent
        ANY WORD(PATTERN) - Incorporate in code, fill buffer with pattern given
        EDITOR - Incorporate in code, fill buffer with the values as per editor
        VARIABLES - Incorporate in code, fill buffer with buffer variable as per scripter

        Fill in buffer with values and using sdcommand write API and data has to be verified on read operation
        """

        #if forceMultipleWrite == True:
            #RWCLib.g_forceMultipleWrite = True
        #else:
            #RWCLib.g_forceMultipleWrite = False

        try:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Writing StartLba:0x%X TransferLength:0x%X" % (startLba, transferLength))
            self.__sdCmdObj.Write(startLba, transferLength, userPatternIndex, forceMultipleWrite)

            self.__sdCmdObj.Cmd12()
        except ValidationError.CVFGenericExceptions as exc:
            # if expectTimeOut is true don't raise exception. 27 is error code for time out exception
            if exc.GetErrorNumber() == 27 and expectTimeOut == True:
                #if forceMultipleWrite == True:
                    #RWCLib.g_forceMultipleRead = False
                return 1
            else:
                raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

        #if forceMultipleWrite == True:
            #RWCLib.g_forceMultipleWrite = False

        return 0


    def Read(self, startLba, transferLength, verify = True, expectTimeOut = False, forceMultipleRead = False):
        """
        logicalAddress, transferLength, verify = True
        """

        #if forceMultipleRead == True:
            #RWCLib.g_forceMultipleRead = True
        #else:
            #RWCLib.g_forceMultipleRead = False

        try:
            readBuff = ServiceWrap.Buffer.CreateBuffer(transferLength, 0x00)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Reading StartLba:0x%X, TransferLength:0x%X" % (startLba, transferLength))
            self.__sdCmdObj.Read(startLba, transferLength, readBuff, forceMultipleRead)

            self.__sdCmdObj.Cmd12()
        except ValidationError.CVFGenericExceptions as exc:
            # if expectTimeOut is true don't raise exception. 27 is error code for time out exception
            if exc.GetErrorNumber() == 27 and expectTimeOut == True:
                #if forceMultipleRead == True:
                    #RWCLib.g_forceMultipleRead = False
                return 1
            else:
                raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

        #if forceMultipleRead == True:
            #RWCLib.g_forceMultipleRead = False

        return 0


    def Erase(self, startLba, transferLength):
        """
        logicalAddress, transferLength
        """
        status = self.__sdCmdObj.GetCardStatus()
        if(status.count("CURRENT_STATE:Tran") != 1):
            self.__sdCmdObj.Cmd7()    # added to get the card to tran state

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Erasing Lba:0x%X Transfer Length:0x%X" % (startLba, transferLength))
        self.__sdCmdObj.Erase(startLba, startLba+transferLength-1)

        return 0
