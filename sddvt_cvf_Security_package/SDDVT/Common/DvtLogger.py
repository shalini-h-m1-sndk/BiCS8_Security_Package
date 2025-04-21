"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : None
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : DvtLogger.py
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : DvtLogger.py
# DESCRIPTION                    : Library file
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 20/06/2022
################################################################################
"""

# Python future modules for python3 forward compatibility
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    from builtins import hex
    from builtins import *
from future.utils import with_metaclass

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
import random, os, sys, re
from inspect import currentframe, getframeinfo

# Global Variables


class Singleton(type):
    def __init__(self, *args, **kwargs):
        super(Singleton, self).__init__(*args, **kwargs)
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = super(Singleton, self).__call__(*args, **kwargs)
        return self.instance


class DvtLogger(with_metaclass(Singleton, customize_log)):

    def __init__(self, VTFContainer):

        ###### Creating CVF objects ######
        self.vtfContainer = VTFContainer
        self.currCfg = Configuration.ConfigurationManagerInitializer.ConfigurationManager.currentConfiguration
        self.CVFTestFactory = FactoryMethod.CVFTestFactory().GetProtocolLib()
        self.__TF = self.CVFTestFactory.TestFixture
        ###### Customize Log ######
        self.fn = os.path.basename(getframeinfo(currentframe()).filename)
        customize_log.__init__(self, self.__TF)


    def __SendDiagnostic(self, dataBuffer, cdbData, direction, enableStatusPhase = True, sctpAppSignature = None,
                         TimeOut = 20000, SendType = ServiceWrap.CMD_SEND_TYPE.SEND_IMMEDIATE):

        if direction == None:
            direction = ServiceWrap.SCTP_DATA_DIRECTION.DIRECTION_NONE  # value is 2, No Data

        if dataBuffer == None:
            dataBuffer = ServiceWrap.Buffer.CreateBuffer(1)
        try:
            ServiceWrap.SCTPCommand.SCTPCommand(fbcccdb = cdbData, objBuffer = dataBuffer, enDataDirection = direction,
                                                bIsStatusPhasePresent = enableStatusPhase, sctpAppSignature = sctpAppSignature,
                                                dwTimeOut = TimeOut, sendType = SendType)
            #ServiceWrap.SCTPCommand.SCTPCommand(cdbData, dataBuffer, direction)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed to send SCTPCommand - %s" % exc.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        return dataBuffer


    def __getMConfData(self):
        """
        Diagnostic to get values from Mconf data structure
        """
        opCode = 0x9A
        subOpCode = 0x1

        cdbData = ServiceWrap.DIAG_FBCC_CDB()
        # 16 number list - Command buffer
        cdbData.cdb = [opCode, 0, subOpCode, 0,
                       0, 0, 0, 0,
                       0, 0, 0, 0,
                       0, 0, 0, 0]
        cdbData.cdbLen = 16

        mConfBuf = ServiceWrap.Buffer.CreateBuffer(1, patternType = ServiceWrap.ALL_0, isSector = True)

        try:
            # ServiceWrap.SCTP_DATA_DIRECTION.DIRECTION_OUT - value is 1, Read from device
            self.__SendDiagnostic(mConfBuf, cdbData, ServiceWrap.SCTP_DATA_DIRECTION.DIRECTION_OUT, opCode)
        except ValidationError.CVFGenericExceptions as exc:
            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Diagnostic command failed with Opcode: 0x%X SubOpcode 0x%X\n" % (opCode, subOpCode))
            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s" % exc)
            raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "<<<<<<<<<<<<<<<         M-CONF INFO          >>>>>>>>>>>>>>>")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Max LBA", hex(mConfBuf.GetFourBytesToInt(offset = 30, little_endian = False))))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("FW Revision", hex(mConfBuf.GetFourBytesToInt(offset = 14))))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Internal Flashware Revision", ""))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Romware revision", ))   # TOBEDONE: Should be get from GetIdentifyDrive using SCTPCommand
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Device Count", hex(mConfBuf.GetOneByteToInt(13))))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Device Type", hex(mConfBuf.GetOneByteToInt(12))))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Device Configuration", hex(mConfBuf.GetOneByteToInt(12))))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("ASIC id", ""))   # TOBEDONE: Get from GetIdentifyDrive using SCTPCommand
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("ASIC Vendor", hex(mConfBuf.GetOneByteToInt(9))))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("ASIC Revision", hex(mConfBuf.GetOneByteToInt(10))))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Security", hex(mConfBuf.GetOneByteToInt(34))))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("File Number", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("File Version", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("File Sign", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Bot File Version", bytes(mConfBuf.GetRawString(35, 32)).decode('utf-8').rstrip('\x00')))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Param File Version", hex(mConfBuf.GetFourBytesToInt(67))))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Lot Number", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Talisman Security Code", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Reserved", hex(mConfBuf.GetTwoBytesToInt(88))))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("SNDK Version", hex(mConfBuf.GetFourBytesToInt(90))))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("CRYS Version", hex(mConfBuf.GetFourBytesToInt(94))))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("PDL Version", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Memory ID", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("File21 Version", bytes(mConfBuf.GetRawString(100, 8)).decode('utf-8').rstrip('\x00')))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Secured Flashware", hex(mConfBuf.GetOneByteToInt(108))))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Compilation Date", bytes(mConfBuf.GetRawString(121, 12)).decode('utf-8').rstrip('\x00')))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Compilation Time", bytes(mConfBuf.GetRawString(133, 9)).decode('utf-8').rstrip('\x00')))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Sectors Per Block", hex(mConfBuf.GetTwoBytesToInt(142))))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("FFU State", hex(mConfBuf.GetOneByteToInt(144))))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set0 Cpu Clock", mConfBuf.GetFourBytesToInt(145, little_endian = False)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set0 Cpu Divider", mConfBuf.GetOneByteToInt(149)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set0 Fim Write Clock", mConfBuf.GetFourBytesToInt(150, little_endian = False)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set0 Fim Write Divider", mConfBuf.GetOneByteToInt(154)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set0 Fim Read Clock", mConfBuf.GetFourBytesToInt(155, little_endian = False)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set0 Fim Read Divider", mConfBuf.GetOneByteToInt(159)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set0 Hs Cpu Clock", mConfBuf.GetFourBytesToInt(160, little_endian = False)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set0 Hs Cpu Divider", mConfBuf.GetOneByteToInt(164)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set0 Ecc Clock", mConfBuf.GetFourBytesToInt(165,little_endian = False)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set0 Ecc Divider", mConfBuf.GetOneByteToInt(169)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set0 Hs Fim Clock", mConfBuf.GetFourBytesToInt(170, little_endian = False)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set0 Hs Fim Divider", mConfBuf.GetOneByteToInt(174)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set0 System Divider", mConfBuf.GetOneByteToInt(175)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set1 Cpu Clock", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set1 Cpu Divider", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set1 Fim Write Clock", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set1 Fim Write Divider", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set1 Fim Read Clock", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set1 Fim Read Divider", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set1 Hs Cpu Clock", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set1 Hs Cpu Divider", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set1 Ecc Clock", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set1 Ecc Divider", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set1 Hs Fim Clock", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set1 Hs Fim Divider", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set1 System Divider", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Update Blocks", mConfBuf.GetOneByteToInt(207)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Chaotic Blocks", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Die Interleave", mConfBuf.GetOneByteToInt(209)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Lower Page", mConfBuf.GetOneByteToInt(210)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("File 31 In User Area", mConfBuf.GetOneByteToInt(211)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("SSA Version", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("App Versions", mConfBuf.GetEightBytesToInt(214)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Top Level IPartNum", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Part Number", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set2 Cpu Clock", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set2 Cpu Divider", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set2 Fim Write Clock", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set2 Fim Write Divider", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set2 Fim Read Clock", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set2 Fim Read Divider", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set2 Hs Cpu Clock", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set2 Hs Cpu Divider", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set2 Ecc Clock", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set2 Ecc Divider", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set2 Hs Fim Clock", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set2 Hs Fim Divider", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set2 System Divider", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set3 Cpu Clock", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set3 Cpu Divider", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set3 Fim Write Clock", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set3 Fim Write Divider", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set3 Fim Read Clock", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set3 Fim Read Divider", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set3 Hs Cpu Clock", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set3 Hs Cpu Divider", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set3 Ecc Clock", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set3 Ecc Divider", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set3 Hs Fim Clock", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set3 Hs Fim Divider", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set3 System Divider", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set4 Cpu Clock", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set4 Cpu Divider", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set4 Fim Write Clock", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set4 Fim Write Divider", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set4 Fim Read Clock", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set4 Fim Read Divider", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set4 Hs Cpu Clock", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set4 Hs Cpu Divider", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set4 Ecc Clock", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set4 Ecc Divider", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set4 Hs Fim Clock", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set4 Hs Fim Divider", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set4 System Divider", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set5 Cpu Clock", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set5 Cpu Divider", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set5 Fim Write Clock", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set5 Fim Write Divider", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set5 Fim Read Clock", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set5 Fim Read Divider", ""))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set5 Hs Cpu Clock", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set5 Hs Cpu Divider", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set5 Ecc Clock", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set5 Ecc Divider", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set5 Hs Fim Clock", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set5 Hs Fim Divider", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Set5 System Divider", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("MetaBlockSize", mConfBuf.GetTwoBytesToInt(393)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Card Physical Size", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("WORM Card Lock", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("OTEC Version", 0))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Meta Page Size", mConfBuf.GetTwoBytesToInt(385)))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Worm Version", 0))

        return mConfBuf

    def DvtLogMessages(self):
        pass


    def getMConfData(self):
        return self.__getMConfData()
