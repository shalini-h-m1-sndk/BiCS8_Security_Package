"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : None
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : DvtCommonLib.py
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : DvtCommonLib.py
# DESCRIPTION                    : Library file
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
    from builtins import str
    from builtins import chr
    from builtins import range
    from builtins import *
from past.utils import old_div
from future.utils import with_metaclass

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
import re
import os
import sys
import time
import collections
from inspect import currentframe, getframeinfo

BYTES_PER_SECTOR = 512
TIMEOUT = 3 * 60 * 60   # 3hr

class Singleton(type):
    '''
    Class to avoid recreation of object
    '''
    def __init__(self, *args, **kwargs):
        super(Singleton, self).__init__(*args, **kwargs)
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = super(Singleton, self).__call__(*args, **kwargs)
        return self.instance

class DvtCommonLib(with_metaclass(Singleton, customize_log)):
    """
    Class for Common methods used in DVT test case
    Created on 24/11/2021:
    """

    def __init__(self, VTFContainer):
        ###### Creating CVF objects ######
        self.vtfContainer = VTFContainer
        self.currCfg = Configuration.ConfigurationManagerInitializer.ConfigurationManager.currentConfiguration
        self.__CVFTestFactory = FactoryMethod.CVFTestFactory().GetProtocolLib()
        self.__TF = self.__CVFTestFactory.TestFixture
        self.__ErrorManager = self.vtfContainer.device_session.GetErrorManager()
        self.__buffer = ServiceWrap.Buffer.CreateBuffer(1, patternType = 0x0)

        ###### Loading General Variables ######
        self.__testName = self.vtfContainer.GetTestName()

        ###### Creating SDDVT objects ######
        self.__sdCmdObj = SDCommandLib.SdCommandClass(VTFContainer)
        self.__errorCodes = ErrorCodes.ErrorCodes()
        self.__config = getconfig.getconfig()
        self.__cardMaxLba = self.__sdCmdObj.MaxLba()
        # self.__cardMaxLba = 0x11000

        ###### Secure Mode ######
        self.__maxblockforsecureop = 0x80
        self.__WriteSecurityKeysDownloaded = False

        ###### CQ Variables ######
        self._CMD44_ReissueOnFailure = True
        self._CMD44_ReissuedCount = 0
        self._CMD44RetryCount = 0
        self._CQSupported = False
        self.__CQDepthSupportedByDevice = 0
        self.__CQTaskStatusRegValue = 0
        # self.__patternSupportedInCQ = {0:"ALL_0", 1:"ALL_1", 3:"BYTE_REPEAT", 4:"FROM_FILE", 5:"INCREMENTAL", 6:"RANDOM", 7:"names", 8:"values"}
        # self.__patternSupportedInCQ = {"ALL_0":ServiceWrap.ALL_0, "ALL_1":ServiceWrap.ALL_1, "INCREMENTAL":ServiceWrap.INCREMENTAL, "RANDOM":ServiceWrap.RANDOM}
        self.__patternSupportedInCQ = {0:'ALL_ZERO', 1:'WORD_REPEATED', 2:'INCREMENTAL', 4:'CONST', 5:'ALL_ONE', 6:'ANY_WORD',
                                        7:'WORD_BLOCK_NUMBER', 8:'PATTERN_NEG_INCREMENTAL', 9:'PATTERN_NEG_CONST'} # 3:ANY_BUFFER not supported in CQ mode
        # self.__patternSupportedInCQ = {0:sdcmdWrap.Pattern.ALL_ZERO, 1:sdcmdWrap.Pattern.WORD_REPEATED,
                                       #2:sdcmdWrap.Pattern.INCREMENTAL, 4:sdcmdWrap.Pattern.CONST,
                                       #5:sdcmdWrap.Pattern.ALL_ONE, 6:sdcmdWrap.Pattern.ANY_WORD,
                                       #7:sdcmdWrap.Pattern.WORD_BLOCK_NUMBER, 8:sdcmdWrap.Pattern.PATTERN_NEG_INCREMENTAL,
                                       #9:sdcmdWrap.Pattern.PATTERN_NEG_CONST} # 3:sdcmdWrap.Pattern.ANY_BUFFER not supported in CQ mode

        ###### Library Specific Variables ######
        self.__patternsForDataIntegrity =  {2:'INCREMENTAL', 7:'WORD_BLOCK_NUMBER', 8:'PATTERN_NEG_INCREMENTAL'}    # 3:ANY_BUFFER not supported in CQ mode
        # used for FPGA pattern generator buffer pattern
        self.__randombuffer = ServiceWrap.Buffer.CreateBuffer(1)
        # fill will random values, to be used for both write and read operation for FPGA pattern generator
        self.__randombuffer.FillRandom()
        self.__sectorsPerMetaBlock = 0x400
        self.__maxTransferLength = 0x100    # 216

        ###### Customize Log ######
        self.fn = os.path.basename(getframeinfo(currentframe()).filename)
        customize_log.__init__(self, self.__TF)

    def FUNCTION_ENTRY(self, func):
        self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s : Starts -------------------------------------->" % func)

    def FUNCTION_EXIT(self, func):
        self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s : Ends -------------------------------------->\n" % func)

    def GetCardCapacity(self):
        self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Get Card Capacity in gb's")
        cardCapacity = sdcmdWrap.WrapGetCardCapacity()
        cardCapacity = cardCapacity.split("G")  # eg: 8G Split the string to get the capacity 8
        return (int(cardCapacity[0]))

    def GetCQDevConfigDict(self):
        """
        Get the list containing values configured in the device for CQ in Perf Enhancement register
        """
        return self.__sdCmdObj._CQDevConfigDict

    def GetCardTransferMode(self):
        """
        returns card speed mode
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "GetCardTransferMode called")
        try:
            speedMode = sdcmdWrap.GetCardTransferMode()
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CardSpeedMode is: %s" % speedMode)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        return speedMode

    def GetDataPatternListSupportedInCQ(self):
        """
        Get the list containing the data patterns supported in CQ for CMD46/CMD47
        """
        return list(self.__patternSupportedInCQ.keys())

    def GetDataPatternListForDataIntegrity(self):
        """
        Get the list containing the data patterns supported in CQ for CMD46/CMD47
        """
        return list(self.__patternsForDataIntegrity.keys())

    def RandomBufferFill(self, BufferObject):
        NumBlocks = old_div(BufferObject.size(), 512)   # Method size will return buffer size in byte unit. So divided by 512 to convert into block.
        for blkNo in range(0, NumBlocks):
            BufferObject.Copy((blkNo * 512), srcBuf = self.__randombuffer, srcOffset = 0, count = 512)

    def GetSDStatus(self):
        self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "####### SD Status #######")
        try:
            SD_Status = self.__sdCmdObj.SD_STATUS()
        except ValidationError.CVFGenericExceptions as exc:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed to get card SD status")
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetInternalErrorMessage())

        return SD_Status

    def SetBusWidth(self, busWidth = 4):
        """
        busWidth : 1 - Set bus width to 1, 4 - Set bus width to 4.
        """
        if busWidth not in [1, 4]:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Invalid bus width was given")
            raise ValidationError.CVFGenericExceptions(self.fn, "Invalid bus width was given")
        try:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Bus width set to", busWidth))
            ACMD6 = sdcmdWrap.SetBusWidth(uiBusWidth = busWidth)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(ACMD6.pyResponseData.r1Response.uiCardStatus))
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    def GetBusWidth(self):
        SDStatus = self.GetSDStatus()
        BusWidth = SDStatus.objSDStatusRegister.ui64DatBusWidth

        if BusWidth == 0:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus width is 1")
        elif BusWidth == 2:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus width is 4")
        else:
            raise ValidationError.TestFailError(self.fn, "Failed - Not able to verify bus width")
        return BusWidth


    def VerifyBusWidth(self, CheckBusWidth):
        """
        CheckBusWidth : 1 - Bus width is 1 / 4 - Bus width is 4.
        """
        if CheckBusWidth == 1:
            SD_Status_Register_BusWidth_Value = 0
        elif CheckBusWidth == 4:
            SD_Status_Register_BusWidth_Value = 2
        else:
            raise ValidationError.TestFailError(self.fn, "BusWidth should be either 1 or 4")

        BusWidth = self.GetBusWidth()
        if BusWidth == SD_Status_Register_BusWidth_Value:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus Width is set to %s" % CheckBusWidth)
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus Width is not set to %s" % CheckBusWidth)
            raise ValidationError.CVFGenericExceptions(self.fn, "Bus Width is not set to %s" % CheckBusWidth)

    def SpeedClassControl(self, SpeedClassControl = 0x0, SpeedClassCommandDescription = 0x0000000, TimeOut = 10):
        """
        CMD20 - SPEED_CLASS_CONTROL
        Parameter Description:
            SpeedClassControl - Enum from sdcmdWrap.VIDEO_SPEED_CLASS_ENUM
        Note: Unlike CTF, Don't have an option to give timeout in the SpeedClassControl API. Hope it will be taken care based on the argument SpeedClassControl.
        """

        try:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SpeedClassControl - 0x%X, SpeedClassCommandDescription - 0x%X, TimeOut - %s" % (SpeedClassControl, SpeedClassCommandDescription, TimeOut))
            CMD20 = sdcmdWrap.SpeedClassControl(uiSpeedClassCommandDescription = SpeedClassCommandDescription, uiSpeedClassControl = SpeedClassControl, Timeout = TimeOut)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD20.pyResponseData.r1bResponse.uiCardStatus))

        return CMD20

    def GetInSpeedClassMode(self):
        opCode = 0x52
        subOpCode = 0x2

        cdbData = ServiceWrap.DIAG_FBCC_CDB()
        # 16 number list - Command buffer
        cdbData.cdb = [opCode, 0,0,subOpCode,
                    0, 0, 0, 0,
                    0, 0, 0, 0,
                    0, 0, 0, 0]
        cdbData.cdbLen = 16

        SpeedClassModeBuff = ServiceWrap.Buffer.CreateBuffer(1, patternType = ServiceWrap.ALL_0, isSector = True)

        self.__sdCmdObj.SendDiagnostic(SpeedClassModeBuff, cdbData, ServiceWrap.SCTP_DATA_DIRECTION.DIRECTION_OUT)

        return SpeedClassModeBuff

    def GetFatAddr(self):
        # Get Fat Addresses
        # FAT_start_address,H,58,0,32
        # FAT_size,H,5C,0,32
        # LBA_of_first_AU,H,60,0,32
        # RU_SIZE,H,64,0,8
        # BitMap_start_address,H,65,0,32
        # BitMap_size,H,69,0,32

        FatAddresses = {}
        File42Buff = ServiceWrap.Buffer.CreateBuffer(1, patternType = ServiceWrap.ALL_0, isSector = True)
        diagCmd = ServiceWrap.DIAG_FBCC_CDB()
        diagCmd.cdb = [138, 0, 0, 0, 42, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
        diagCmd.cdbLen = 16

        self.__sdCmdObj.SendDiagnostic(File42Buff, diagCmd, ServiceWrap.SCTP_DATA_DIRECTION.DIRECTION_OUT)

        FatAddresses['FAT_start_address'] = File42Buff.GetFourBytesToInt(0x58)
        FatAddresses['FAT_size'] = File42Buff.GetFourBytesToInt(0x5C)
        FatAddresses['LBA_of_first_AU'] = File42Buff.GetFourBytesToInt(0x60)
        FatAddresses['RU_SIZE'] = File42Buff.GetOneByteToInt(0x64)
        FatAddresses['BitMap_start_address'] = File42Buff.GetFourBytesToInt(0x65)
        FatAddresses['BitMap_size'] = File42Buff.GetFourBytesToInt(0x69)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FAT Start Address 8192: %d" % FatAddresses['FAT_start_address'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FAT Block Count 8192: %d" % FatAddresses['FAT_size'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FAT User Area First LBA 16384 : %d" % FatAddresses['LBA_of_first_AU'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "RU SIZE : %d" % FatAddresses['RU_SIZE'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FAT Bitmap Start Address: %d" % FatAddresses['BitMap_start_address'])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FAT Bitmap Block Count: %d" % FatAddresses['BitMap_size'])
        return FatAddresses

    def BasicCommandFPGAReset(self, value):
        try:
            sdcmdWrap.SDRHostReset(bRestoreSettings = value)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())


    def CheckCQSupport(self):
        """
        checks if SDSpec supports command class 11 or not
        checks whether card supports CQ or not
        checks SD status for CQ support
        Checks SD Spec version support, must support spec version 7.0
        Check Cache Support
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_CHECK_CQ_SUPPORT)
        ExtnFunctionCmdClass = 11
        CQCmdClass = 1
        SDSpecVer =  6  # CQ is supported from SD spec part-I version 6. So checking whether card supports spec version 6 or above.

        CommandClassSupport = self.CheckCommandClassSupport(ExtnFunctionCmdClass, CQCmdClass)
        ExtnRegCommandSupportInSCR = self.CheckExtnRegCmdSupportInSCR()

        if CommandClassSupport and (ExtnRegCommandSupportInSCR['CMD48_49'] == 'Supported'):
            SDSpecVersion = self.CheckSDSpecVersion(SDSpecVer, self.__sdCmdObj.SCRRegister)
            SDStatusForCQ = self.CheckSDStatusForCQ()
            CQDepth, CMD48_ReadBuffer = self.GetCQDepth(call_from_CheckCQSupport = True)
            CacheSupport = self.CheckCacheSupport(SDStatusForCQ, CMD48_ReadBuffer)

            if SDSpecVersion and SDStatusForCQ['CQ'] == 'Supported' and CQDepth and CacheSupport:
                self.HashLineWithArg(self.GL_CQ_SUPPORTED)
                self._CQSupported = True
            else:
                raise ValidationError.TestFailError(self.fn, self.GL_CQ_NOT_SUPPORTED)
        else:
            raise ValidationError.TestFailError(self.fn, self.GL_EITHER_ONE_OF_OR_BOTH_CMD_CLASSES_1_AND_11_NOT_SUPPORTED)


    def CheckCommandClassSupport(self, *CommandClass):
        """
        Parameter Description:
            CommandClass - list contains command class numbers, if card supports command classes given, it will return 1 else 0
        """

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CHECK_COMMAND_CLASSES_SUPPORT(*CommandClass))
        self.__sdCmdObj.GetCSD()
        Supported_Command_Classes = []

        for class_number in CommandClass:
            if (self.__sdCmdObj.CSDRegister.uiCcc >> class_number) & 0x1:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_COMMAND_CLASS_SUPPORTED(class_number))
                Supported_Command_Classes.append(class_number)
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_COMMAND_CLASS_NOT_SUPPORTED(class_number))

        retvalue = True if list(CommandClass) == Supported_Command_Classes else False
        self.__sdCmdObj.Cmd7()  # To bring the card to transfer state from standby state.
        return retvalue

    def CheckExtnRegCmdSupportInSCR(self):
        """
        Checks for support of CMD48/CMD49 and CMD58/CMD59 support in SCR register
        """
        ExtnRegCmdSupport = {}
        SupportStatus = {1 : "Supported", 0 : "Not Supported"}

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_CHECK_EXTN_REG_CMDS_SUPPORT_IN_SCR)
        self.__sdCmdObj.Cmd55()
        self.__sdCmdObj.GetSCRRegisterEntry()
        # Refer Table 5-17 and 5-23 in spec 7.0 for Command Support Bits
        ExtnRegCmdSupport['CMD48_49'] = SupportStatus[((self.__sdCmdObj.SCRRegister.objSCRRegister.ui16CmdSupport >> 2) & 0x1)]  # Checking bit 34 in scr reg
        ExtnRegCmdSupport['CMD58_59'] = SupportStatus[((self.__sdCmdObj.SCRRegister.objSCRRegister.ui16CmdSupport >> 3) & 0x1)]  # Checking bit 35 in scr reg
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_EXTN_REG_CMDS_SUPPORT_IN_SCR(ExtnRegCmdSupport))

        return ExtnRegCmdSupport

    def CheckSDSpecVersion(self, version, SCR_Register = None):
        '''
        checks whether the card supports the passed spec version or not.
        returns 1 if supports else 0, also prints supported spec value.
        '''
        Spec_version = 0

        if SCR_Register == None:
            self.__sdCmdObj.Cmd55()
            SCR_Register = self.__sdCmdObj.GetSCRRegisterEntry()

        # Refer table 5-17 in SD spec part-I 9.0
        SD_SPEC = SCR_Register.objSCRRegister.ui8SdSpec
        SD_SPEC3 = SCR_Register.objSCRRegister.ui16SdSpec3
        SD_SPEC4 = SCR_Register.objSCRRegister.ui16SdSpec4
        SD_SPECX = SCR_Register.objSCRRegister.ui16SdSpecx

        self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_SD_SPEC_VERS(SD_SPEC, SD_SPEC3, SD_SPEC4, SD_SPECX))

        # Refer table 5-19 in SD spec part-I 9.0
        SD_SPEC_VERSION = {
            "[0, 0, 0, 0]": 1.0,
            "[1, 0, 0, 0]": 1.10,
            "[2, 0, 0, 0]": 2.00,
            "[2, 1, 0, 0]": 3.00,
            "[2, 1, 1, 0]": 4.00,
            "[2, 1, 0, 1]": 5.00,
            "[2, 1, 1, 1]": 5.00,
            "[2, 1, 0, 2]": 6.00,
            "[2, 1, 1, 2]": 6.00,
            "[2, 1, 0, 3]": 7.00,
            "[2, 1, 1, 3]": 7.00,
            "[2, 1, 0, 4]": 8.00,
            "[2, 1, 1, 4]": 8.00,
            "[2, 1, 0, 5]": 9.00,
            "[2, 1, 1, 5]": 9.00
        }

        Spec_version = SD_SPEC_VERSION["[%s, %s, %s, %s]" % (SD_SPEC, SD_SPEC3, SD_SPEC4, SD_SPECX)]

        if Spec_version >= version:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_SUPPORT_SPEC_VER_OF_CQ(Spec_version))
            return True
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_NOT_SUPPORT_SPEC_VER_OF_CQ(Spec_version))
            return False


    def CheckSDStatusForCQ(self):
        """
        Description: Checks SD status value and prints the currently supported features then returns
                     dictionary with supported functionalities
        For more info: Refer SD spec part-I, Table 4-44 : SD Status, Table 4.10.2-2 : PERFORMANCE_ENHANCE Field
        """
        self.__sdCmdObj.Cmd55()
        sd_status = self.__sdCmdObj.SD_STATUS()
        SDCQSupport = {}
        CQDepth = sd_status.objSDStatusRegister.ui8Performance_Enhance_CommandQueueSupport

        if sd_status.objSDStatusRegister.ui8PerformanceEnhance == 0:
            SDCQSupport['PERF_ENHANCE'] = 'Not Supported'

        if CQDepth > 0:
            SDCQSupport['CQ'] = 'Supported'
            SDCQSupport['CQ_Depth'] = CQDepth
        else:
            SDCQSupport['CQ'] = 'Not Supported'

        if sd_status.objSDStatusRegister.ui8Performance_Enhance_SupportForCache == 1:
            SDCQSupport['Cache'] = 'Supported'
        else:
            SDCQSupport['Cache'] = 'Not Supported'

        if sd_status.objSDStatusRegister.ui8Performance_Enhance_SupportForHostInitiatedMaintenance == 1:
            SDCQSupport['host_init_maintenance'] = 'Supported'
        else:
            SDCQSupport['host_init_maintenance'] = 'Not Supported'

        if sd_status.objSDStatusRegister.ui8Performance_Enhance_SupportForCardInitiatedMaintenance == 1:
            SDCQSupport['card_init_maintenance'] = 'Supported'
        else:
            SDCQSupport['card_init_maintenance'] = 'Not Supported'

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CQ_INFO_IN_SD_STATUS_REG(SDCQSupport))
        return SDCQSupport


    def GetCQDepth(self, call_from_CheckCQSupport = False):
        """
        Function to get supported queue depth
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_GET_CQ_DEPTH)
        if(self.__sdCmdObj.IsSDRFwLoopback() == True):
            if call_from_CheckCQSupport:
                return 32, None
            else:
                return 32
        else:
            readbuff = self.__buffer
            readbuff.Fill(value = 0x0)
            performance_enhancement_function = 2

            try:
                self.__sdCmdObj.Cmd48(DataBuff = readbuff, ExtnFunNum = performance_enhancement_function)
            except ValidationError.CVFGenericExceptions as exc:
                raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

            queue_depth = readbuff.GetOneByteToInt(gvar.Perf_Enhan_Func_Offsets.CQ_SUPPORT_AND_DEPTH)
            if queue_depth == 0:
                self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_CQ_NOT_SUPPORTED_AS_QUEUE_DEPTH_IS_0)
                self.__CQDepthSupportedByDevice = 0
                raise ValidationError.TestFailError(self.fn, self.GL_CQ_NOT_SUPPORTED_AS_QUEUE_DEPTH_IS_0)
            else:
                self.__CQDepthSupportedByDevice = queue_depth + 1
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CQ_SUPPORTED_WITH_QUEUE_DEPTH(self.__CQDepthSupportedByDevice))
                if call_from_CheckCQSupport:
                    return self.__CQDepthSupportedByDevice, readbuff
                else:
                    return self.__CQDepthSupportedByDevice


    def CheckCacheSupport(self, SDStatusForCQ = None, CMD48_ReadBuffer = None):
        """
        returns 1 if cache is supported
        """

        try:
            if CMD48_ReadBuffer == None:
                CMD48_ReadBuffer = self.__buffer
                CMD48_ReadBuffer.Fill(value = 0x0)
                performance_enhancement_function = 2
                self.__sdCmdObj.Cmd48(CMD48_ReadBuffer, ExtnFunNum = performance_enhancement_function)
        except ValidationError.CVFGenericExceptions as exc:
            raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

        if SDStatusForCQ == None:
            SDStatusForCQ = self.CheckSDStatusForCQ()
        if SDStatusForCQ['Cache'] == 'Supported' and self.PerformanceExtnRegSpaceInfo()['Cache_Support'] == 'Supported':
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_CACHE_SUPPORTED)
            return True
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_CACHE_NOT_SUPPORTED)
            return False


    def PerformanceExtnRegSpaceInfo(self):

        Maintenance_urgency_list = ['None','Mild','Middle','Urgent']
        PerfEnhFuncDict = {}

        if self.__sdCmdObj.decoded_Perf_Enhance_Func == None:
            readBuffer = self.__buffer
            readBuffer.Fill(value = 0x0)
            self.__sdCmdObj.Cmd48(readBuffer, ExtnFunNum = 2)

        if self.__sdCmdObj.decoded_Perf_Enhance_Func["REVISION"] == 0:
            PerfEnhFuncDict["REVISION"] = "Revision_1"

        if self.__sdCmdObj.decoded_Perf_Enhance_Func["FX_EVENT_SUPPORT"] == 1:
            PerfEnhFuncDict["FX_EVENT_Support"] = 'Supported'
        elif self.__sdCmdObj.decoded_Perf_Enhance_Func["FX_EVENT_SUPPORT"] == 0:
            PerfEnhFuncDict["FX_EVENT_Support"] = 'Not Supported'

        if self.__sdCmdObj.decoded_Perf_Enhance_Func["CARD_INIT_MAINTEN_SUPPORT"] == 1:
            PerfEnhFuncDict["Card_Init_Maintenance_Support"] = 'Supported'
        elif self.__sdCmdObj.decoded_Perf_Enhance_Func["CARD_INIT_MAINTEN_SUPPORT"] == 0:
            PerfEnhFuncDict["Card_Init_Maintenance_Support"] = 'Not Supported'

        if self.__sdCmdObj.decoded_Perf_Enhance_Func["HOST_INIT_MAINTEN_SUPPORT"] == 1:
            PerfEnhFuncDict["Host_Init_Maintenance_Support"] = 'Supported'
        elif self.__sdCmdObj.decoded_Perf_Enhance_Func["HOST_INIT_MAINTEN_SUPPORT"] == 0:
            PerfEnhFuncDict["Host_Init_Maintenance_Support"] = 'Not Supported'

        PerfEnhFuncDict['Card Maintenance Urgency'] = Maintenance_urgency_list[self.__sdCmdObj.decoded_Perf_Enhance_Func["CARD_MAINTEN_URGENCY"]]

        if self.__sdCmdObj.decoded_Perf_Enhance_Func["CACHE_SUPPORT"] == 1:
            PerfEnhFuncDict["Cache_Support"] = 'Supported'
        elif self.__sdCmdObj.decoded_Perf_Enhance_Func["CACHE_SUPPORT"] == 0:
            PerfEnhFuncDict["Cache_Support"] = 'Not Supported'

        PerfEnhFuncDict['Queue_depth'] = self.__sdCmdObj.decoded_Perf_Enhance_Func["CQ_SUPPORT_AND_DEPTH"]

        if self.__sdCmdObj.decoded_Perf_Enhance_Func["FX_EVENT_ENABLE"] == 1:
            PerfEnhFuncDict["FX_EVENT"] = 'Enabled'
        elif self.__sdCmdObj.decoded_Perf_Enhance_Func["FX_EVENT_ENABLE"] == 0:
            PerfEnhFuncDict["FX_EVENT"] = 'Disabled'

        if self.__sdCmdObj.decoded_Perf_Enhance_Func["CARD_INIT_MAINTEN_ENABLE"] == 1:
            PerfEnhFuncDict["Card_Init_Maintenance"] = 'Enabled'
        elif self.__sdCmdObj.decoded_Perf_Enhance_Func["CARD_INIT_MAINTEN_ENABLE"] == 0:
            PerfEnhFuncDict["Card_Init_Maintenance"] = 'Disabled'

        if self.__sdCmdObj.decoded_Perf_Enhance_Func["HOST_INIT_MAINTEN_ENABLE"] == 1:
            PerfEnhFuncDict["Host_Init_Maintenance"] = 'Enabled'
        elif self.__sdCmdObj.decoded_Perf_Enhance_Func["HOST_INIT_MAINTEN_ENABLE"] == 0:
            PerfEnhFuncDict["Host_Init_Maintenance"] = 'Disabled'

        if self.__sdCmdObj.decoded_Perf_Enhance_Func["CACHE_ENABLE"] == 1:
            PerfEnhFuncDict["Cache"] = 'Enabled'
        elif self.__sdCmdObj.decoded_Perf_Enhance_Func["CACHE_ENABLE"] == 0:
            PerfEnhFuncDict["Cache"] = 'Disabled'

        if self.__sdCmdObj.decoded_Perf_Enhance_Func["ENABLE_CQ"] == 1:
            PerfEnhFuncDict["CQ"] = 'Enabled'
        elif self.__sdCmdObj.decoded_Perf_Enhance_Func["ENABLE_CQ"] == 0:
            PerfEnhFuncDict["CQ"] = 'Disabled'

        if self.__sdCmdObj.decoded_Perf_Enhance_Func["CQ_MODE"] == 1:
            PerfEnhFuncDict["CQMode"] = 'Sequential'
        elif self.__sdCmdObj.decoded_Perf_Enhance_Func["CQ_MODE"] == 0:
            PerfEnhFuncDict["CQMode"] = 'Voluntary'

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_PER_ENHANCE_FUNC_DATA(PerfEnhFuncDict))
        return PerfEnhFuncDict


    def CQEnable(self, Set_CQ = None, Set_Cache = None, Set_Voluntary_mode = None, Set_Sequential_mode = None):
        '''
        Description: Enables or Disables CQ with the given parameters
        Parameters Description:
        SetCQ - True enables the CQ and False disables the CQ
            Set_Cache - True enables the Cache and False disables the Cache
            Set_Voluntary_mode - True enables the CQ in voluntary mode and False disables the CQ
            Set_Sequential_mode - True enables the CQ in sequential mode and False disables the CQ

        Note: At a time should select only one mode
        '''
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_SET_CQ_CACHE_CQMODE(Set_CQ, Set_Cache, Set_Voluntary_mode, Set_Sequential_mode))
        if(self.__sdCmdObj.IsSDRFwLoopback() == True):
            if (Set_CQ == True) and (Set_Cache == True):
                if (self.__sdCmdObj.pgnenable == 1):
                    self.CQ_PGNEnableDisable(0)
                self.CQ_PGNEnableDisable(1)
                self.__sdCmdObj._CQDevConfigDict["CQ Enable"] = True
                self.__sdCmdObj._CQDevConfigDict["Cache Enable"] = True

                if (Set_Sequential_mode == True):
                    self.CQ_PGNEnableDisable(1)
                    self.__sdCmdObj._CQDevConfigDict["Mode"] = "Sequential"
                elif(Set_Voluntary_mode == True):
                    self.__sdCmdObj._CQDevConfigDict["Mode"] = "Voluntary"
            else:
                self.CQ_PGNEnableDisable(0)
                self.__sdCmdObj._CQDevConfigDict["CQ Enable"] = False
                self.__sdCmdObj._CQDevConfigDict["Cache Enable"] = False
                self.__sdCmdObj._AgedOut = False
                self.__sdCmdObj._AgedTaskID = None
            self.__sdCmdObj._CQDevConfigDict["CQ Depth"] = 32
            return
        else:
            if Set_Sequential_mode == False and Set_Voluntary_mode == False:
                raise ValidationError.TestFailError(self.fn, self.STD_LOG_HEADER("Select atleast one mode"))

            if Set_Sequential_mode == True and Set_Voluntary_mode == True:
                raise ValidationError.TestFailError(self.fn, self.STD_LOG_HEADER("Select only one mode"))

            if self.__sdCmdObj._CQDevConfigDict["CQ Enable"] == False:
                if (self.vtfContainer.isModel == True) or (self.__sdCmdObj.DEVICE_FPGA_TMP == 1):
                    self.GetCQDepth()
                else:
                    self.CheckCQSupport()

            self._CMD44_ReissueOnFailure = True
            self._CMD44_ReissuedCount = 0

            current_status = {}
            performance_enhancement_fun = 2

            # Offsets for CQ and Cache Enable/Disable in 512bytes page boundary
            # EnableCQ_and_CQ_Mode_Offset = 262
            # Cache_Offset = 260
            # ADDR = 0
            # LEN = 512

            # Specific offset changes for CQ and Cache Enable/Disable
            EnableCQ_and_CQ_Mode_Offset = 2
            Cache_Offset = 0
            ADDR = 260
            LEN = 3  # 3bytes of data

            buffer = self.__buffer
            buffer.Fill(value = 0x0)
            # Execute CMD48
            try:
                self.__sdCmdObj.Cmd48(buffer, performance_enhancement_fun, Address = ADDR, Length = LEN)
            except ValidationError.CVFGenericExceptions as exc:
                raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

            # Set EnableCQ, CQMode and cache bit to the buffer for extension register write.
            CQ_Byte = data_byte = buffer.GetOneByteToInt(EnableCQ_and_CQ_Mode_Offset)
            if Set_CQ == True:
                data_byte = data_byte | gvar.Perf_Enhan_Func_Offsets.ENABLE_CQ_Bit_Offset
            elif Set_CQ == False:
                data_byte = data_byte & (~(gvar.Perf_Enhan_Func_Offsets.ENABLE_CQ_Bit_Offset | gvar.Perf_Enhan_Func_Offsets.CQ_MODE_Bit_Offset))
            buffer.SetByte(EnableCQ_and_CQ_Mode_Offset, data_byte)

            data_byte = buffer.GetOneByteToInt(Cache_Offset)
            if Set_Cache == True:
                data_byte = data_byte | gvar.Perf_Enhan_Func_Offsets.CACHE_ENABLE_Bit_Offset
            elif Set_Cache == False:
                data_byte = data_byte & (~gvar.Perf_Enhan_Func_Offsets.CACHE_ENABLE_Bit_Offset)
            buffer.SetByte(Cache_Offset, data_byte)

            data_byte = buffer.GetOneByteToInt(EnableCQ_and_CQ_Mode_Offset)
            if Set_Voluntary_mode == True:
                data_byte = data_byte & (~gvar.Perf_Enhan_Func_Offsets.CQ_MODE_Bit_Offset)
            elif Set_Sequential_mode == True:
                data_byte = data_byte | gvar.Perf_Enhan_Func_Offsets.CQ_MODE_Bit_Offset
            buffer.SetByte(EnableCQ_and_CQ_Mode_Offset, data_byte)

            # Execute CMD49 to enable or disable CQ, Cache and set CQMode
            try:
                self.__sdCmdObj.Cmd49(buffer, performance_enhancement_fun, Address = ADDR, LenORMask = LEN)
            except ValidationError.CVFGenericExceptions as exc:
                self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_SET_CQ_CONFIG_FAILED(Set_CQ, Set_Cache, Set_Voluntary_mode, Set_Sequential_mode))
                raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

            current_status = self.CheckCQConfigParams(CQ_Enable = Set_CQ, Cache_Enable = Set_Cache, Sequential_mode = Set_Sequential_mode, Voluntary_mode = Set_Voluntary_mode)
            current_status["CQ Depth"] = self.__CQDepthSupportedByDevice
            self.__sdCmdObj._CQDevConfigDict.update(current_status)

            if self.vtfContainer.isModel == False:
                if (Set_CQ == True) and (self.__sdCmdObj._CQDevConfigDict["CQ Enable"] == True): # PGN Interrupt enable
                    self.CQ_PGNEnableDisable(1)
                    #self._CMD44RetryCount = 0
                    if (CQ_Byte & 0x01) == 0x01:
                        # Task register in the card will not be erased if the CQ is enabled without disable the previously enabled CQ.
                        # Since previously queued tasks are still in the same state, Not erase the CQTaskDetails in the test layer.
                        pass
                    else:
                        self.__sdCmdObj.CQTaskDetails = [{}] * gvar.GlobalConstants.CQ_MAX_QUEUE_DEPTH
                elif (Set_CQ == None) or (Set_CQ == False) or (self.__sdCmdObj._CQDevConfigDict["CQ Enable"] == False): # PGN Interrupt disable
                    self.CQ_PGNEnableDisable(0)


    def CQDisable(self):
        """
        1. Flush Cache
        2. Disables CQ and Cache
        """

        if(self.__sdCmdObj.IsSDRFwLoopback() == False):
            if (self.vtfContainer.isModel == True) or (self.__sdCmdObj.DEVICE_FPGA_TMP == 1):
                pass
            elif (self.__sdCmdObj._CQDevConfigDict["Cache Enable"] == True):
                self.FlushCache()
        if (self.__sdCmdObj._CQDevConfigDict["CQ Enable"] == True) and (self.__sdCmdObj._CQDevConfigDict["Cache Enable"] == True) and (self.__sdCmdObj._CQDevConfigDict["Mode"] == "Sequential"):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_ABORT_QUEUE_BEFORE_DISABLE_CQ)   # Workaround for JIRA - 18418
            self.CQManagement(OpCode = 'WholeQueue')
        self.CQEnable(Set_CQ = False, Set_Cache = False)


    def CQ_PGNEnableDisable(self, enable):
        if enable == 1:
            sdcmdWrap.EnablePGNInterruptForCmdQ(enable = 1)
            self.__sdCmdObj.pgnenable = 1
        else:
            sdcmdWrap.EnablePGNInterruptForCmdQ(enable = 0)
            self.__sdCmdObj.pgnenable = 0
        self.__CQTaskStatusRegValue = 0
        self.__sdCmdObj.CQTaskAgeingDict = collections.OrderedDict(("Task%d" % task, "NQ") for task in range(0, gvar.GlobalConstants.CQ_MAX_QUEUE_DEPTH))
        self.__sdCmdObj._AgedOut = False
        self.__sdCmdObj._AgedTaskID = None

    def FlushCache(self):
        """
        To flush cache. Return True if caches flushed within time, Fails otherwise.
        """
        TimeOutFlag = 0
        FlushChacheOffset = 0
        performance_enhancement_fun = 2

        buff = self.__buffer
        buff.Fill(value = 0x0)
        data_byte = 0x01
        buff.SetByte(FlushChacheOffset, data_byte)
        # CMD49 to Flush Cache
        try:
            self.__sdCmdObj.Cmd49(buff, ExtnFunNum = performance_enhancement_fun, Address = gvar.Perf_Enhan_Func_Offsets.FLUSH_CACHE_Byte_Offset, LenORMask = 1)
        except ValidationError.CVFGenericExceptions as exc:
            raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

        while True:
            # CMD48 to check whether cache flushed or not
            try:
                buff.Fill(value = 0)
                self.__sdCmdObj.Cmd48(buff, ExtnFunNum = performance_enhancement_fun)
            except ValidationError.CVFGenericExceptions as exc:
                raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

            FlushStatus = self.__sdCmdObj.decoded_Perf_Enhance_Func["FLUSH_CACHE"]

            if FlushStatus == 0x0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_CACHE_FLUSHED)
                return 1
            else:
                if TimeOutFlag >= 1:
                    raise ValidationError.TestFailError(self.fn, self.GL_CACHE_NOT_FLUSHED)
                time.sleep(1)
                TimeOutFlag += 1


    def CQManagement(self, TaskID = 0, OpCode = 'SingleTask', expectBsyState = False):
        """
        Description : Function to abort the particular task in the queue or whole queue
        OpCode = 1 / 'WholeQueue' is for aborting the whole queue
        OpCode = 2 / 'SingleTask' is for aborting the particular task (should pass TaskID as well)
        """
        try:
            self.__sdCmdObj.Cmd43(TaskID, OpCode, expectBsyState)
        except ValidationError.CVFGenericExceptions as exc:
            raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

    def CheckCQConfigParams(self, CQ_Enable = None, Cache_Enable = None, Sequential_mode = None, Voluntary_mode = None):
        """
        Description: Checks current CQ status
        Parameter Description:
        CQ_Enable, Cache_Enable, Sequential_mode, Voluntary_mode - Pass True if need to be checked whether function is enabled,
                                                                   Pass False if need to be checked whether function is disabled.
        return: If the status is matched with the passed argument, the function returns a dictionary with enable/disable info
                if not it fails the test case.
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CHECK_CQ_CONFIG(CQ_Enable, Cache_Enable, Sequential_mode, Voluntary_mode))
        Status = {}

        performance_enhancement_fun = 2

        if (((CQ_Enable == True) and (Cache_Enable != True) and (self.__sdCmdObj._CQDevConfigDict["Cache Enable"] == False))
            or ((CQ_Enable == None) and (Cache_Enable == False) and (self.__sdCmdObj._CQDevConfigDict["CQ Enable"] == True))):
            try:
                self.__sdCmdObj.GetCardStatus()
            except ValidationError.CVFGenericExceptions as exc:
                self.Expected_Failure_Check(exc, "CARD_ERROR", "CMD13")
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_ERROR_BIT_SET_IN_CMD13_SINCE_CQ_ENABLED_WITHOUT_CACHE)
                CQ_Enable = False
                Cache_Enable = False
                Sequential_mode = None
                Voluntary_mode = None
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_ERROR_BIT_NOT_SET_IN_CMD13_SINCE_CQ_ENABLED_WITHOUT_CACHE)
                raise ValidationError.TestFailError(self.fn, "Expected CARD_ERROR error not occurred")

        readBuffer = self.__buffer
        readBuffer.Fill(value = 0x0)
        self.__sdCmdObj.Cmd48(readBuffer, performance_enhancement_fun)  # Read extension register

        if CQ_Enable != None:
            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CHECK_CQ_IS_ENABLED)
            if self.__sdCmdObj.decoded_Perf_Enhance_Func["ENABLE_CQ"]:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_HEADER(self.GL_CQ_ENABLED, "#", repeat = 4))
                Status["CQ Enable"] = True
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_HEADER(self.GL_CQ_DISABLED, "#", repeat = 4))
                Status["CQ Enable"] = False
                Sequential_mode = None
                Voluntary_mode = None
            if Status["CQ Enable"] != CQ_Enable:
                raise ValidationError.TestFailError(self.fn, self.STD_LOG_CQ_CONFIG_NOT_MATCH(CQ = CQ_Enable))

        if Cache_Enable != None:
            if self.__sdCmdObj.decoded_Perf_Enhance_Func["CACHE_ENABLE"]:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_HEADER(self.GL_CACHE_IS_ENABLED, "#", repeat = 4))
                Status["Cache Enable"] = True
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_HEADER(self.GL_CACHE_IS_DISABLED, "#", repeat = 4))
                Status["Cache Enable"] = False
            if Status["Cache Enable"] != Cache_Enable:
                raise ValidationError.TestFailError(self.fn, self.STD_LOG_CQ_CONFIG_NOT_MATCH(Cache = Cache_Enable))

        if Voluntary_mode != None:
            if self.__sdCmdObj.decoded_Perf_Enhance_Func["CQ_MODE"] == 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_HEADER(self.GL_VOL_MODE_ENABLED, "#", repeat = 4))
                Status["Mode"] = "Voluntary"
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_HEADER(self.GL_VOL_MODE_DISABLED, "#", repeat = 4))
                Status["Mode"] = "Sequential"
            if Status["Mode"] != "Voluntary":
                raise ValidationError.TestFailError(self.fn, self.STD_LOG_CQ_CONFIG_NOT_MATCH(Voluntary = Voluntary_mode))
        elif Sequential_mode != None:
            if self.__sdCmdObj.decoded_Perf_Enhance_Func["CQ_MODE"] == 1:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_HEADER(self.GL_SEQ_MODE_ENABLED, "#", repeat = 4))
                Status["Mode"] = "Sequential"
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_HEADER(self.GL_SEQ_MODE_DISABLED, "#", repeat = 4))
                Status["Mode"] = "Voluntary"
            if Status["Mode"] != "Sequential":
                raise ValidationError.TestFailError(self.fn, self.STD_LOG_CQ_CONFIG_NOT_MATCH(Sequential = Sequential_mode))

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CQ_CONFIG(Status))
        return Status


    def GetGeneralInformation(self):
        """
        Function to Read General Information Extension Register
        """
        readbuff = self.__buffer
        readbuff.Fill(value = 0x0)
        General_Information_function_number = 0
        try:
            self.__sdCmdObj.Cmd48(readbuff, ExtnFunNum = General_Information_function_number)
        except ValidationError.CVFGenericExceptions as exc:
            raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

        readbuff.PrintToLog()
        DecodedGenResp = self.DecodeGeneralInformation(readbuff)

        return DecodedGenResp

    def DecodeGeneralInformation(self, readbuff):
        """
        To Decode the General Information Extrension Register
        Decoded as dictionary
        General_Information['Length']
        General_Information['no_of_Extension']
        General_Information['function_1']
        General_Information['function_2']
        .
        .
        To Do : data sequence needs to be checked before decoding 2 bytes at a time
        """

        General_Information = {}
        Revision_offset = 0
        General_Information_Length_offset = 2
        Number_of_Ext_offset = 4
        Length_of_function_header = 40
        First_Func_Offset = 16  # header of function starts
        count = 1
        Function_name_offset = 24

        General_Information_Length = readbuff.GetTwoBytesToInt(General_Information_Length_offset)
        General_Information['Length'] = General_Information_Length
        General_Information['Revision'] = readbuff.GetTwoBytesToInt(Revision_offset)
        No_Of_Extensions = readbuff.GetOneByteToInt(Number_of_Ext_offset)  # fetching 4th byte
        General_Information['no_of_Extension'] = No_Of_Extensions

        Next_Extension = First_Func_Offset

        while Next_Extension != 0x00:
            Function_name_offset = Next_Extension + Function_name_offset  # Go to the function name offset
            # read 16bytes function name in hex format
            function_name_ascii = ''
            for offset in range(Function_name_offset, Function_name_offset + 16):  # to discard 00
                byteData = readbuff.GetOneByteToInt(offset)
                if byteData != 0:
                    function_name_ascii += chr(byteData)

            func = 'function_'+str(count)
            General_Information[func] = function_name_ascii

            # goto the function name offset
            Next_Extension = Next_Extension + Function_name_offset
            Next_Extension = readbuff.GetTwoBytesToInt(Next_Extension)  # get the offset of the next function
            Next_Extension = Next_Extension & 0x3ff
            Function_name_offset = 24
            count = count + 1
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_GEN_INFO_FUNC_DATA(General_Information))
        return General_Information

    # def DecodeGeneralInformation(self, CMD48):
    #     # TOBEDONE : Yet to complete the implementation, Only first function's info can be get.
    #     # Refer figure 5-15 Data Structure of General Information in spec 7.0 for more information.
    #     """
    #     To Decode the General Information Extrension Register
    #     Decoded as dictionary
    #     General_Information['Length']
    #     General_Information['no_of_Extension']
    #     General_Information['function_1']
    #     General_Information['function_2']
    #     """

    #     General_Information = {}
    #     count = 1

    #     General_Information['Revision'] = CMD48.extRegisters.u.generalInfo.headerFields.ui16StructRev           # Fetching 0th and 1st bytes
    #     General_Information['Length'] = CMD48.extRegisters.u.generalInfo.headerFields.ui16GeneralInfoLength     # Fetching 2nd and 3rd bytes
    #     General_Information['no_of_Extension'] = CMD48.extRegisters.u.generalInfo.headerFields.ui8NumberOfExtensions    # Fetching 4th byte

    #     count = 1
    #     while(CMD48.extRegisters.u.generalInfo.extregisterFields.ui16PointerToNextExtension != 0):
    #         name_ascii = ''
    #         for name in CMD48.extRegisters.u.generalInfo.extregisterFields.ui8ExtXFunctionName:
    #             if name != 0:
    #                 name_ascii += chr(name)
    #         General_Information["function_{}".format(count)] = name_ascii
    #         count = count + 1
    #         if count > 1:
    #             break
    #         # For now only information of first function(PMF) can be get from general information by sending CMD48.
    #         # Not able to get information of second function (PER) from general information. Not even able to get info of 2nd
    #         # function by reading CMD48.rawBuffer, because rawBuffer object only contains value all 0.

    #     #Next_Extension = First_Func_Offset

    #     #while(Next_Extension != 0x00):
    #         #Function_name_offset = Next_Extension + Function_name_offset    #goto the function name offset
    #         #function_name = CMD48.rawBuffer.GetData(Function_name_offset, 16)  #read 16bytes function name in hex format
    #         #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("function_name", function_name))
    #         #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("function_name", dir(function_name)))
    #         #function_name_ascii = ''
    #         #for name in function_name:                                 #to discard 00
    #             #if name != 0:
    #                 #function_name_ascii += chr(name)

    #         #func = 'function_' + str(count)
    #         #General_Information[func] = function_name_ascii

    #         #Next_Extension = Next_Extension + Function_name_offset      #goto the function name offset
    #         #Next_Extension = CMD48.rawBuffer.GetTwoBytesToInt(Next_Extension)    #get the offset of the next function
    #         #Next_Extension = Next_Extension & 0x3ff
    #         #Function_name_offset = 24
    #         #function_name = ' '
    #         #count = count + 1

    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DecodeGeneralInformation : General_Information = %s" % General_Information)

    #     return General_Information


    def PostConditionReadWithLegacyCMD18(self, No_of_Reads, StartBlockAddr = None, NumBlocks = None, Pattern = None,
                                         ReadDataBuffer = None, lbaTag = False, SequenceTag = None, SequenceNumber = 0):
        """
        Legacy CMD18 read with pattern. Write data in CQ Mode then read written data in legacy.
        """
        if self.vtfContainer.isModel == True:
            return

        if((No_of_Reads == 0) or (StartBlockAddr == None) or (NumBlocks == None) or (Pattern == None)):
            raise ValidationError.TestFailError(self.fn, self.GL_INPUT_IS_ZERO_OR_EMPTY)

        for i in range(0, No_of_Reads):

            if(NumBlocks[i] > 0xFFFF):
                raise ValidationError.TestFailError(self.fn, self.GL_NUMBLOCKS_IS_GREATER_THAN_0xFFFF)

            try:
                self.__sdCmdObj.Cmd18WithPatternCompare(StartLbaAddress = StartBlockAddr[i], NumBlocks = NumBlocks[i], Pattern = Pattern[i],
                                                        ReadDataBuffer = ReadDataBuffer, lbaTag = lbaTag, SequenceTag = SequenceTag, SequenceNumber = SequenceNumber)
            except ValidationError.CVFGenericExceptions as exc:
                errstring = exc.GetInternalErrorMessage()
                if errstring.find('CARD_COMPARE_ERROR') != -1:
                    self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_MISCOMPARE_OCCURED)
                    self.__sdCmdObj.GetMiscompareBuff()
                raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())


    def PreConditionWriteWithLegacyCMD25(self, No_of_Writes, StartBlockAddr = None, NumBlocks = None, Pattern = None,
                                         WriteDataBuffer = None, lbaTag = False, SequenceTag = None, SequenceNumber = 0):
        """
        Legacy CMD25 write with pattern. Used for writing data in Legacy and then reading the same data in CQ mode
        """
        if self.vtfContainer.isModel == True:
            return

        if((No_of_Writes == 0) or (StartBlockAddr == None) or (NumBlocks == None) or (Pattern == None)):
            raise ValidationError.TestFailError(self.fn, self.GL_INPUT_IS_ZERO_OR_EMPTY)

        for i in range(0, No_of_Writes):

            if(NumBlocks[i] > 0xFFFF):
                raise ValidationError.TestFailError(self.fn, self.GL_NUMBLOCKS_IS_GREATER_THAN_0xFFFF)

            try:
                self.__sdCmdObj.Cmd25WithPatternCompare(StartLbaAddress = StartBlockAddr[i], NumBlocks = NumBlocks[i], Pattern = Pattern[i],
                                                        WriteDataBuffer = WriteDataBuffer, lbaTag = lbaTag, SequenceTag = SequenceTag, SequenceNumber = SequenceNumber)
            except ValidationError.CVFGenericExceptions as exc:
                raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())


    def CQTaskInformation(self, NumBlocks, TaskID, Priority, Direction, ExtendedAddress = 0):
        """
        Description: Sets Task ID parameters like, block count, task id, data direction, and priority, it calls CMD44.
        """
        arg = (((Direction & 0x1) << 30) | ((Priority & 0x1) << 23) | ((TaskID & 0x1F) << 16) | (NumBlocks & 0xFFFF))
        try:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CMD44_ARGS(Direction, ExtendedAddress, Priority, TaskID, NumBlocks))
            self.__sdCmdObj.Cmd44(arg)
            #CMD44 = self.__sdCmdObj.Cmd44(NumBlocks, TaskID, Priority, Direction, ExtendedAddress)

            if self._CMD44_ReissuedCount > 0:
                self._CMD44RetryCount += 1
                self._CMD44_ReissuedCount = 0

        except ValidationError.CVFGenericExceptions as exc:
            if self._CMD44_ReissueOnFailure == True:    # Flag kept true always since illegal cmd error failure seen in functional test too and retry count is 3
                if exc.GetInternalErrorMessage().find("CARD_ILLEGAL_CMD") != -1:
                    if self._CMD44_ReissuedCount == 3:  # workaround for JIRA RPG-21836. Retry CMD44 if card reports illegal for a valid CMD44
                        self._CMD44_ReissuedCount = 0
                        raise ValidationError.TestFailError(self.fn, self.STD_LOG_CMD44_FAILED_FOR_3_TIMES(TaskID, exc.GetInternalErrorMessage()))
                    self._CMD44_ReissuedCount += 1
                    self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CMD44_REISSUED_COUNT(self._CMD44_ReissuedCount))
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_RESEND_CMD44)
                    self.CQTaskInformation(NumBlocks, TaskID, Priority, Direction)
                else:
                    raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())
            else:
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetInternalErrorMessage())


    def CQStartBlockAddr(self, StartBlockAddr):
        """
        Description: Sets Task ID's StartBlockAddr, must be followed by CMD44
        """
        try:
            self.__sdCmdObj.Cmd45(StartBlockAddr)
        except ValidationError.CVFGenericExceptions as exc:
            if self.__sdCmdObj._AgedOut == True:
                self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_AGED_OUT(self.__sdCmdObj._AgedTaskID, self.__sdCmdObj.GetCQAgeingThresholdValue()))
            else:
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetInternalErrorMessage())


    def CQExecuteReadTask(self, TaskID, Pattern = 0, StartBlockAddr = 0, NumBlocks = 0, DoCompare = 0, UseCmd12 = False, ReadDataBuffer = None, lbaTag = False, SequenceTag = None, SequenceNumber = 0):
        try:
            PatternString = ("USER BUFFER" , self.__patternSupportedInCQ.get(Pattern))[ReadDataBuffer == None]
            self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "[TaskID : %d, Pattern : %s, StartBlockAddr : 0x%X, NumBlocks : %d, DoCompare : %d, lbaTag=%s, SequenceTag=%s, SequenceNumber = %d]"
                        % (TaskID, PatternString, StartBlockAddr, NumBlocks, DoCompare, lbaTag, SequenceTag, SequenceNumber ))
            CMD46 = self.__sdCmdObj.Cmd46(TaskID = TaskID, Pattern = Pattern, StartBlockAddr = StartBlockAddr, NumBlocks = NumBlocks, DoCompare = DoCompare,
                                          UseCmd12 = UseCmd12, ReadDataBuffer = ReadDataBuffer, lbaTag = lbaTag, SequenceTag = SequenceTag, SequenceNumber = SequenceNumber)

            #NoData = True if (ReadDataBuffer == None) else False
            #self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name,
                        #self.STD_LOG_CQ_EXE_READ_TASK(TaskID, StartBlockAddr, NumBlocks, NoData, PatternString, DoCompare, lbaTag, SequenceTag, SequenceNumber))
            #CMD46 = self.__sdCmdObj.Cmd46(TaskID, StartBlockAddr, blockCount = NumBlocks, NoData = NoData, BufObj = ReadDataBuffer, Pattern = self.__sdCmdObj.GetPatternEnumFromNum(Pattern), DoCompare = DoCompare,
                                          #lbaTag = lbaTag, SequenceTag = SequenceTag,  SequenceNumber = SequenceNumber)

        except ValidationError.CVFGenericExceptions as exc:
            self.vtfContainer.CleanPendingExceptions()
            self.__sdCmdObj.GetCardStatus()
            raise ValidationError.CVFGenericExceptions(self.fn, self.STD_LOG_CQ_EXE_READ_TASK_FAILED(TaskID, exc.GetInternalErrorMessage()))
        return CMD46


    def CQExecuteWriteTask(self, TaskID, Pattern = 0, StartBlockAddr = 0, NumBlocks = 0, UseCmd12=False, WriteDataBuffer = None, lbaTag = False, SequenceTag = None, SequenceNumber = 0):
        try:
            PatternString = ("USER BUFFER", self.__patternSupportedInCQ.get(Pattern))[WriteDataBuffer == None]
            self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "[TaskID : %d, Pattern : %s, StartBlockAddr : 0x%X, NumBlocks : %d, lbaTag=%s, SequenceTag=%s, SequenceNumber = %d]"
                        % (TaskID, PatternString, StartBlockAddr, NumBlocks, lbaTag, SequenceTag, SequenceNumber ))
            CMD47 = self.__sdCmdObj.Cmd47(TaskID, Pattern, StartBlockAddr, NumBlocks, UseCmd12=UseCmd12, WriteDataBuffer = WriteDataBuffer,
                                          lbaTag = lbaTag, SequenceTag = SequenceTag,  SequenceNumber = SequenceNumber)

            #NoData = True if (WriteDataBuffer == None) else False
            #self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name,
                        #self.STD_LOG_CQ_EXE_WRITE_TASK(TaskID, StartBlockAddr, NumBlocks, NoData, PatternString, lbaTag, SequenceTag, SequenceNumber))
            #CMD47 = self.__sdCmdObj.Cmd47(TaskID, StartBlockAddr, blockCount = NumBlocks, NoData = NoData, BufObj = WriteDataBuffer, Pattern = self.__sdCmdObj.GetPatternEnumFromNum(Pattern),
                                          #lbaTag = lbaTag, SequenceTag = SequenceTag,  SequenceNumber = SequenceNumber)

        except ValidationError.CVFGenericExceptions as exc:
            raise ValidationError.CVFGenericExceptions(self.fn, self.STD_LOG_CQ_EXE_WRITE_TASK_FAILED(TaskID, exc.GetInternalErrorMessage()))
        return CMD47


    def GetTaskReadyStatus(self, TaskID, CheckReadyStatus = True):
        """
        Description : Function to Check for the task readiness
        """
        if(CheckReadyStatus == False):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_NOT_CHECK_READINESS_OF_TASK(TaskID))
            return
        ReadyTimeout = 0.250  #250ms
        Task_ID_Ready = self.CheckTaskStatus(TaskID)
        Count = 3    # fix count to 1 to break after 250ms. Update Count to >1 to wait for more ms
        timeout_count = Count
        while (Task_ID_Ready != 1):
            if(Count == 0):
                raise ValidationError.TestFailError(self.fn, self.STD_LOG_READY_BIT_NOT_SET_FOR_TASK(TaskID, timeout_count * ReadyTimeout * 1000))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_READ_TASK_STAUS_AGAIN_FOR_TASK(TaskID, ReadyTimeout * 1000))
            time.sleep(ReadyTimeout)
            Task_ID_Ready = self.CheckTaskStatus(TaskID)
            Count -= 1
        if self.__sdCmdObj._CQDevConfigDict["Mode"] == "Voluntary":
            self.__sdCmdObj.CQTaskAgeingDict["Task%d" % TaskID] = "Rdy"

    def GetTaskReadyList(self):
        """
        Function to get the list of task id that are ready.
        """
        taskReadyList = []
        ReadyTimeout = 0.250  #250ms
        Count = 3    # fixed to 1 to break after 250ms. Update Count to >1 to wait for more ms

        while taskReadyList == []:
            self.__CQTaskStatusRegValue = self.__sdCmdObj.GetTaskStatusRegister()
            if(self.__CQTaskStatusRegValue == 0):
                if(Count == 0):
                    raise ValidationError.TestFailError(self.fn, self.STD_LOG_TASK_STATUS_REG_IS_0(ReadyTimeout * 1000))
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_STATUS_REG_IS_0_READ_TSR_AGAIN(ReadyTimeout * 1000))
                time.sleep(ReadyTimeout)
                Count -= 1
            else:
                for task in range(0, 32):
                    if((self.__CQTaskStatusRegValue >> task) & 0x1 == 1):
                        taskReadyList.append(task)
                        if self.__sdCmdObj._CQDevConfigDict["Mode"] == "Voluntary":
                            self.__sdCmdObj.CQTaskAgeingDict["Task%d" % task] = "Rdy"
                            #ageingList = collections.OrderedDict((taskitr,ageingcount+1) if(type(ageingcount) == int) else (taskitr,ageingcount) for taskitr, ageingcount in  self.__sdCmdObj.CQTaskAgeingDict.items())

                            #self.__sdCmdObj.CQTaskAgeingDict.update(ageingList)

                            #if(self.__sdCmdObj.GetCQAgeingThresholdValue() in self.__sdCmdObj.CQTaskAgeingDict.values()):
                                #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "self.__sdCmdObj.CQTaskAgeingDict.values() = %s"%self.__sdCmdObj.CQTaskAgeingDict.values())
                                #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Task that has aged out with Ageing Threshold %d = %s" % (self.__sdCmdObj.GetCQAgeingThresholdValue(), ([i for i, j in self.__sdCmdObj.CQTaskAgeingDict.items() if j==self.__sdCmdObj.GetCQAgeingThresholdValue()])))
                                #raise ValidationError.TestFailError(self.fn,
                                                                    #"Task that has aged out with Ageing Threshold %d = %s" % (self.__sdCmdObj.GetCQAgeingThresholdValue(), ([i for i, j in self.__sdCmdObj.CQTaskAgeingDict.items() if j==self.__sdCmdObj.GetCQAgeingThresholdValue()])))

                #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "AgeingList = %s\n"%json.dumps(self.__sdCmdObj.CQTaskAgeingDict))

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_READY_LIST(taskReadyList))
        return taskReadyList


    def CheckTaskStatus(self, TaskID):
        """
        1) Gives the readiness of current TaskID

        2) This is an extra logic to avoid unnecessary calls to Cmd13(), at a time many task could get ready
           so every time no need to issue Cmd13(), previously saved value can be used
        """
        if((self.__CQTaskStatusRegValue >> TaskID) & 0x01):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_READY(TaskID))
            return True
        else:
            self.__CQTaskStatusRegValue = self.__sdCmdObj.GetTaskStatusRegister()
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_STATUS_REG_32BIT(self.__CQTaskStatusRegValue))
            if((self.__CQTaskStatusRegValue >> TaskID) & 0x01):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_READY(TaskID))
                return True
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_NOT_READY(TaskID))
                return False

    def GetTaskAbortedStatus(self, TaskID = 32, WholeQueue = False):
        """
        Description: Checks the status of aborted task
        Parameters Description:
            TaskID Value from 0-31
            WholeQueue = True for checking the whole queue aborted status

        If self.__CQTaskStatusRegValue value == 0 then whole queue aborted otherwise not
        If WholeQueue is True then checks for abort status of entire queue
        Need to pass TaskID to check aborted status of particular task and Whole_Queue should not be passed(send False option in this case)
        """
        self.__CQTaskStatusRegValue = self.__sdCmdObj.GetTaskStatusRegister()
        if WholeQueue == True:
            if self.__CQTaskStatusRegValue == 0:
                retvalue =  1
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_WHOLE_Q_ABORTED)
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_WHOLE_Q_NOT_YET_ABORTED)
                retvalue = 0

        elif TaskID < 32:
            ret = self.__CQTaskStatusRegValue >> TaskID & 0x01
            if ret == 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_ABORTED(TaskID))
                retvalue = 1
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_NOT_ABORTED(TaskID))
                retvalue = 0

        else:
            raise ValidationError.TestFailError(self.fn, self.GL_TASKID_EXCEED_MAX_LIMIT)
        return retvalue

    def CheckTaskCompletion(self, TaskID):
        """
        Description: Function to check the data transfer completion status of the task
        """
        if self.vtfContainer.isModel == 1:
            return

        ret = None
        sleepTime = 0.250   # 250 ms

        if(self.__sdCmdObj.IsSDRFwLoopback() == True):
            Count = None
        else:
            Count = int(old_div(TIMEOUT,sleepTime))

        Dir = "Write" if (self.__sdCmdObj.CQTaskDetails[TaskID]["Direction"]) == 0 else "Read"

        SleepCount = 0
        while True:
            # Get Card status and check whether card is busy or not. If card is not busy that means it may completed its
            # read or write task so while loop can be terminated. If card is busy that means card is writing or reading right now,
            # so again check card status after 250 milliseconds(0.250 sec).

            ret = sdcmdWrap.SDRGetCardDataTransferStatus(taskId = TaskID).GetCardDataTransferStatus()
            #self.noiseLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_DATA_TRANS_STATUS(Dir, TaskID, ret))
            if ret != gvar.ErrorCodes.CARD_IS_BUSY:
                break

            time.sleep(sleepTime)
            if Count != None:  # Timeout set to None for infinite polling until busy
                Count = Count - 1
                SleepCount += 1

                if Count == 0:
                    self.__sdCmdObj.GetCardStatus()
                    raise ValidationError.TestFailError(self.fn, self.STD_LOG_TASK_DATA_TRANS_TIMEOUT(Dir, TaskID, TIMEOUT, ret))
        return ret

    def GetTaskCompletionStatus(self, TaskID):
        """
        Description: Function to check the data transfer completion status of the task
        """
        if self.vtfContainer.isModel == 1:
            return

        ret = None
        sleepTime = 0.250   # 250 ms

        if(self.__sdCmdObj.IsSDRFwLoopback() == True):
            Count = None
        else:
            Count = int(old_div(TIMEOUT,sleepTime))

        Dir = "Write" if (self.__sdCmdObj.CQTaskDetails[TaskID]["Direction"]) == 0 else "Read"

        SleepCount = 0
        while True:
            # Get Card status and check whether card is busy or not. If card is not busy that means it may completed its
            # read or write task so while loop can be terminated. If card is busy that means card is writing or reading right now,
            # so again check card status after 250 milliseconds(0.250 sec).

            ret = sdcmdWrap.SDRGetCardDataTransferStatus(taskId = TaskID).GetCardDataTransferStatus()
            #self.noiseLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_DATA_TRANS_STATUS(Dir, TaskID, ret))
            if ret != gvar.ErrorCodes.CARD_IS_BUSY:
                break

            time.sleep(sleepTime)
            if Count != None:  # Timeout set to None for infinite polling until busy
                Count = Count - 1
                SleepCount += 1

                if Count == 0:
                    self.__sdCmdObj.GetCardStatus()
                    raise ValidationError.TestFailError(self.fn, self.STD_LOG_TASK_DATA_TRANS_TIMEOUT(Dir, TaskID, TIMEOUT, ret))

        if ret != 0:
            if ret == self.__errorCodes.CheckError("CARD_COMPARE_ERROR"):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_MISCOMPARE_OCCURED_FOR_TASK(Dir, TaskID))
                self.__sdCmdObj.GetMiscompareBuff()

            self.__sdCmdObj.GetCardStatus()
            raise ValidationError.TestFailError(self.fn, self.STD_LOG_TASK_DATA_TRANS_FAILED(Dir, TaskID, ret, self.__errorCodes.error_codes[ret]))
        else:
            if SleepCount == 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_DATA_TRANS_DONE_WITHIN_250MS(Dir, TaskID, ret))
            else:
                TimeTakenForStatusPolling = SleepCount * sleepTime
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TIME_TAKEN_FOR_TASK_DATA_TRANS(Dir, TaskID, TimeTakenForStatusPolling, ret))

            if SleepCount > int(old_div(180, sleepTime)):   # If time exceeds 3 Min
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_DATA_TRANS_EXCEEDS_3MIN(Dir, TaskID, TimeTakenForStatusPolling))

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_CHECK_IF_CARD_IN_TRANS_STATE)
            CMD13responseList = self.__sdCmdObj.GetCardStatus()

            if "CURRENT_STATE:CQ Tran" in CMD13responseList:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_CARD_IN_CQ_TRANS_STATE)
            else:
                raise ValidationError.TestFailError(self.fn, self.STD_LOG_CARD_NOT_IN_CQ_TRANS_STATE_AFTER_DATA_TRANS(Dir, TaskID, CMD13responseList))

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_DATA_TRANS_DONE(Dir, TaskID))
            if self.__sdCmdObj.CQTaskDetails[TaskID]["Exe"] == "InDataTx":
                self.__sdCmdObj.TasksExecuted += 1
                if(self.__sdCmdObj.CQTaskDetails[TaskID]["Direction"]) == 0:
                    self.__sdCmdObj.WriteTasksExecuted += 1
                if(self.__sdCmdObj.CQTaskDetails[TaskID]["Direction"]) == 1:
                    self.__sdCmdObj.ReadTasksExecuted += 1
                self.__sdCmdObj.BlocksTransferred += self.__sdCmdObj.CQTaskDetails[TaskID]["BlockCount"]
                self.__sdCmdObj.CQTaskDetails[TaskID] = {}


    def GetTaskCompletionStatusValue(self, TaskID):
        """
        Description: Function to return the data transfer completion status value of the task
        """
        ret = None
        sleepTime = 0.250 #250 ms

        if(self.__sdCmdObj.IsSDRFwLoopback() == True):
            Count = None
        else:
            Count = int(old_div(TIMEOUT,sleepTime))

        Dir = "Write" if (self.__sdCmdObj.CQTaskDetails[TaskID]["Direction"]) == 0 else "Read"

        while True:
            ret = sdcmdWrap.SDRGetCardDataTransferStatus(taskId = TaskID).GetCardDataTransferStatus()
            if ret != gvar.ErrorCodes.CARD_IS_BUSY:
                break
            time.sleep(sleepTime)

            if Count != None:  # Timeout set to None for infinite polling until busy
                Count = Count - 1
                if Count == 0:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_CARD_IN_BUSY_STATE)
                    return ret
        if ret != 0:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_DATA_TRANS_FAILED(Dir, TaskID, ret, self.__errorCodes.error_codes[ret]))
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_DATA_TRANS_DONE(Dir, TaskID))
        return ret

    def GetTaskErrorStatusFromPEFRegister(self, TaskID):
        """
        Read Performance Enhancement Function register offset [7-14] to get Task Error Status
        """
        readbuff = self.__buffer
        readbuff.Fill(value = 0x0)
        perfEnhanceFn = 2
        try:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_TASK_ERROR_STATUS_IN_CMD48)
            self.__sdCmdObj.Cmd48(readbuff, ExtnFunNum = perfEnhanceFn, Address = gvar.Perf_Enhan_Func_Offsets.TASK_ERROR_STATUS, Length = 8)
        except ValidationError.CVFGenericExceptions as exc:
            raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_ERROR_STATUS_OF_ALL_TASKS_IN_CMD48(readbuff.GetEightBytesToInt(0)))
        taskErrorByteOffset = old_div(TaskID,4)
        taskErrorStatus = (readbuff.GetOneByteToInt(taskErrorByteOffset) >> ((TaskID % 4) * 2)) & 3
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_ERROR_STATUS_OF_A_TASK_IN_CMD48(TaskID, taskErrorStatus))

        return taskErrorStatus


    def CardSwitchCommand(self, mode = True, arginlist = None, blocksize = 0x200, responseCompare = False, compareConsumption = None,
                          compareValue = None, compare = [1, 1, 1, 1, 1, 1], compareSupported = None, comparedSwitched = None):
        """
        Description: API implemented as per scripter. This API differs from SDCommandLib Cmd6 API with the comparison.
        Parameters Description:
            mode: True - Switch / False - Check
            arginlist: A list contains function number of 6 function groups
            blocksize: size of the response buffer
            responseCompare: Allow for response to be compared
            compareConsumption: Compare the power consumption as per scripter
                None = 0
                Not Error = 1
                Match to Value = 2, User input from parameter compareValue
                Error = 3
            compare: default all 1's, allows for individual values to be compared
            compareSupported: Compare the supported parameter list as per scripter with response buffer
            comparedSwitched: Compare the switched parameter list as per scripter with response buffer
        """

        responseBuff = ServiceWrap.Buffer.CreateBuffer(blocksize, patternType = 0x0, isSector = False)
        CMD6 = self.__sdCmdObj.CardSwitchCmd(mode, arginlist, responseBuff, blocksize)

        if responseCompare == True:
            # Power/Current consumption compare
            powerconsumption = CMD6.statusDataStructure.uiMaximumPowerConsumption

            if compareConsumption == 3:
                if powerconsumption != 0:
                    raise ValidationError.TestFailError(self.fn, "Power consumption value is not ZERO and its value(in mA) is %d" % powerconsumption)
                else:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ERROR option is given, Power consumption value is ZERO[Error as per SD spec/scripter] and its value(in mA) is %d" % powerconsumption)

            elif compareConsumption == 2:
                if compareValue == None:
                    raise ValidationError.ParametersError(self.fn, "Parameter compareValue is not given for power consumption verification")
                elif powerconsumption < compareValue:
                    raise ValidationError.TestFailError(self.fn, "Power consumption value(in mA) %d is not matched to passed value(in mA):%d" % (powerconsumption, compareValue))
                else:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "MATCH TO VALUE option is given, Power consumption value(in mA) %d is matched to passed value(in mA):%d" % (powerconsumption, compareValue))

            elif compareConsumption == 1:
                if powerconsumption == 0:
                    raise ValidationError.TestFailError(self.fn, "Power consumption value is ZERO, which is not expected")
                else:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "NOT ERROR option is given, Power consumption value is not ZERO and its value(in mA) is %d" % powerconsumption)

            elif compareConsumption == 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "NONE option is given, So power consumption value is not checked and its value(in mA) is %d" % powerconsumption)

            else:
                self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Invalid compareConsumption option given")

            # Supported functions of all function groups compare
            for index in range(0, 6):
                responseSupported = eval("CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup%d" % (index + 1))
                # compare the supported function
                if compare[index] == 1: # what function group to be compared
                    if ((responseSupported & compareSupported[index]) != compareSupported[index]):
                        raise ValidationError.TestFailError(self.fn, "[CheckSupportedFunctionsOfFunctionGroup%d], response value: 0x%X is not matched with response compare value: 0x%X" %
                                                            ((index + 1), responseSupported, compareSupported[index]))
                    else:
                        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "[CheckSupportedFunctionsOfFunctionGroup%d], response value: 0x%X is matched with response compare value: 0x%X" %
                                     ((index + 1), responseSupported, compareSupported[index]))
                else:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "[CheckSupportedFunctionsOfFunctionGroup%d], response value: 0x%X"
                                 % ((index + 1), responseSupported))

            # Switched functions of all function groups compare
            for index in range(0, 6):
                responseSwitched = eval("CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup%d" % (index + 1))
                if compare[index] == 1: # what function group to be compared
                    if ((responseSwitched & comparedSwitched[index]) != comparedSwitched[index]):
                        raise ValidationError.TestFailError(self.fn, "[CheckSwitchedFunctionsOfFunctionGroup%d], response value: 0x%X is not matched with response compare value: 0x%X" %
                                                            ((index + 1), responseSwitched, comparedSwitched[index]))
                    else:
                        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "[CheckSwitchedFunctionsOfFunctionGroup%d], response value: 0x%X is matched with response compare value: 0x%X" %
                                     ((index + 1), responseSwitched, comparedSwitched[index]))
                else:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "[CheckSwitchedFunctionsOfFunctionGroup%d], response value: 0x%X"
                                 % ((index + 1), responseSwitched))

        return CMD6


    def SwitchUHS1Mode(self, mode = 'SDR50', freq = 100):
        """
        Description: Function for switching to UHS-I speed mode (SDR12, SDR25, SDR50, DDR50)
        Parameter Description:
            mode = 'SDR12' or 'SDR25' or 'SDR50' or 'DDR50'
            freq = clock frequency in MHz
        """
        self.FUNCTION_ENTRY("SwitchUHS1Mode")

        if mode == 'SDR12':
            arglist = [0x0, 0xF, 0xF, 0xF, 0xF, 0xF]
            if freq > 25:
                freq = 25  # in MHz
            switchString = "SDR12 SWITCHED"

        elif mode == 'SDR25':
            arglist = [0x1, 0x0, 0x0, 0x0, 0x0, 0x0]
            if freq > 50:
                freq = 50  # in MHz
            switchString = "SDR25/HIGH SPEED SWITCHED"

        elif mode == 'SDR50':
            arglist = [0x2, 0xF, 0xF, 0x1, 0xF, 0xF]
            if freq > 100:
                freq = 100  # in MHz
            switchString = "SDR50 SWITCHED"

        elif mode == 'DDR50':
            arglist = [0x4, 0xF, 0xF, 0x1, 0xF, 0xF]
            if freq > 50:
                freq = 50  # in MHz
            switchString = "DDR50 SWITCHED"

        elif mode == 'SDR104':
            arglist = [0x3, 0xF, 0x1, 0x1, 0xF, 0xF]
            if freq > 200:
                freq = 200  # in MHz
            switchString = "SDR104 SWITCHED"

        elif mode == 'DDR200':
            if self.__sdCmdObj._DDR200_SupportedGrpNum == 2:
                arglist = [0xF, 0xE, 0x1, 0x1, 0xF, 0xF]
                switchString = "DDR200 SWITCHED IN GROUP2"
            else:
                arglist = [0x5, 0xF, 0x1, 0x1, 0xF, 0xF]
                switchString = "DDR200 SWITCHED IN GROUP1"
            if freq > 200:
                freq = 200  # in MHz

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Switching to %s speed" % mode)

        CMD6 = self.CardSwitchCommand(arginlist = arglist, blocksize = 0x40)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD6 ui64StatusStructure - %s" % CMD6.statusDataStructure.ui64StatusStructure)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD6 uiDataStructureVersion - %s" % CMD6.statusDataStructure.uiDataStructureVersion)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD6 MaximumPower - %s" % CMD6.statusDataStructure.uiMaximumPowerConsumption)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD6 FunctionSelectionOfFunctionGroup1 - %s" % CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup1)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD6 SupportBitsOfFunctionsInFunctionGroup1 - %s" % CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup1)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD6 uiFunctionSelectionOfFunctionGroup4 - %s" % CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup4)

        decodedResponse = self.__sdCmdObj.DecodeSwitchCommandResponse("SWITCH", CMD6)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd6 Decoded Response = %s\n" % decodedResponse)  # Decoded Message

        if (switchString in decodedResponse):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Switched to %s" % mode)
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed to Switch to %s" % mode)
            raise ValidationError.TestFailError(self.fn, "Failed to switch to %s mode" % mode)

        if (mode == 'SDR50') or (mode == 'SDR104') or (mode == 'DDR50') or (mode == 'DDR200'):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Calling SetFreqWithTuning for %s......\n" % mode)
            # SetFreqWithTuning should be called for UHS-I speed mode
            self.__sdCmdObj.SetFreqWithTuning(freq * 1000)
            freq = old_div((sdcmdWrap.WrapGetSDRFreq()), (1000 * 1000))     # Converting Hz into MHz
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Host Frequency set to %dMHz for %s\n" % (freq, mode))
        else:
            sdcmdWrap.SDRSetFrequency(freq = freq * 1000 * 1000)
            freq = old_div((sdcmdWrap.WrapGetSDRFreq()), (1000 * 1000))     # Converting Hz into MHz
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Setting Host Frequency to %dMHz for %s\n" % (freq, mode))

        self.FUNCTION_EXIT("SwitchUHS1Mode")

    def LVInit(self):
        if self.__sdCmdObj._LVInitDone == False:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "LV initialization .....")
            clockTime = 0x1E
            #clockTime = 0x12
            waitTime= 0x0A
            cardResponseTime= 0x1393
            TpruPlusWaitTime = 1000
            try:
                enableLVInitConfigRetVal = sdcmdWrap.SetLVInitConfiguration(enableLVInit = self.currCfg.variation.lv, clock_time = clockTime,
                                                                            wait_time = waitTime, card_response_time = cardResponseTime,
                                                                            waitingTimeToSendFirstPulse = TpruPlusWaitTime)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                raise ValidationError.TestFailError(self.fn, "LV Config Failed with error - %s" % exc.GetFailureDescription())
            sdcmdWrap.SDRSetFrequency(freq = 20 * 1000 * 1000)
            sdcmdWrap.SetPower(1)

            retVal = sdcmdWrap.GetLVInitStatus()
            # if retVal = 0: Inprogress, 1: LV Init Done with No error, 2: Invalid, 3: LV Init Done with Error
            if retVal == 1:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "LV Init Done with No Error\n")
                self.__sdCmdObj._LVInitDone = True
            else:
                raise ValidationError.TestFailError(self.fn, "LV Initialization failed : %d" % retVal)

    def CQ_LV_PowerOn(self):
        if (self.currCfg.variation.lv == 1) and (self.__sdCmdObj._LVInitDone == True):
            self.__sdCmdObj._LVInitDone = False
            self.__sdCmdObj.CQ_LV_FPGA_Download()
            self.LVInit()
        else:
            sdcmdWrap.SetPower(1)

    def CQ_LV_PowerOn_BatchMode(self):
        if (self.currCfg.variation.lv == 1) and (self.__sdCmdObj._LVInitDone == True):
            self.__sdCmdObj._LVInitDone = False
            #self.__sdCmdObj.BatchMode_FPGA_Download()
            self.LVInit()
        else:
            sdcmdWrap.SetPower(1)

    def Erase(self, StartLba, EndLba, directCardAPI = False):
        """
        Note: Due to some limitation in SDR host, It will reduce the EndLba value by 1 internally. So EndLba value is increased
        by 1 in below code. Refer JIRA: RPG-54470 for more information.
        """

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "EraseDiscardFule API Called")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CVF EraseDiscardFule API called to erase from StartLba:0x%X to EndLba:0x%X"
                              % (StartLba, EndLba))
        if directCardAPI == True:
            try:
                EndLba += 1     # Refer JIRA: RPG-54470
                cmdObjEraseDiscardFule = sdcmdWrap.EraseDiscardFule(uiStartLba = StartLba, uiEndLba = EndLba,
                                                                    doEraseDiscardFule = sdcmdWrap.DISCARD_FULE_ERASE_OPTIONS.DO_ERASE)
                # value of DISCARD_FULE_ERASE_OPTIONS.DO_ERASE is 0
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed CVF EraseDiscardFule API from StartLba: 0x%X to EndLba:0x%X" %  (StartLba, EndLba))
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed CVF EraseDiscardFule API from StartLba:0x%X to EndLba:0x%X" % (StartLba, EndLba))
        else:
            self.__sdCmdObj.Erase(StartAddress = StartLba, EndAddress = EndLba)

    def Discard_FULE(self, startLba, endLba, Operation, expectPrgState, busyTimeout, continueWithErase):
        """
        Checks Discard or FULE support from SD status register and do Discard or FULE or Erase.
        """
        try:
            self.__sdCmdObj.Cmd55()
            ACMD13 = self.__sdCmdObj.SD_STATUS()
        except ValidationError.CVFGenericExceptions as exc:
            raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

        if Operation == "Discard":
            OperationSupport = ACMD13.objSDStatusRegister.ui16DiscardSupport
        elif Operation == "FULE":
            OperationSupport = ACMD13.objSDStatusRegister.ui16FuleSupport

        if OperationSupport == 1:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card Supports %s" % Operation)
            Operation = 1 if Operation == "Discard" else 2  # 1 for Discard, 2 for FULE
        elif continueWithErase == True:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card does not support %s. Continuing with Erase..." % Operation)
            Operation = 0                                   # 0 for Erase
        else:
            raise ValidationError.TestFailError(self.fn, "Card does not support %s" % Operation)

        try:
            self.__sdCmdObj.Cmd32(StartLBA = startLba)
            self.__sdCmdObj.Cmd33(EndLBA = endLba)
            self.__sdCmdObj.Cmd38_WithArg(arg = Operation, expectPrgState = expectPrgState, busyTimeout = busyTimeout)
        except ValidationError.CVFGenericExceptions as exc:
            raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())


    def Discard(self, startLba, endLba, expectPrgState = False, continueWithErase = True):
        """
        Performs discard operation
        """
        busyTimeout = 250   # 250ms as per spec
        self.Discard_FULE(startLba, endLba, "Discard", expectPrgState, busyTimeout, continueWithErase)


    def FULE(self, expectPrgState = False, continueWithErase = True):
        """
        Performs FULE (Full Userarea Logical Erase) operation
        """
        busyTimeout = 1000  # 1sec as per spec
        startLba = 0
        endLba = self.__sdCmdObj.calculate_endLba(startLba, self.__cardMaxLba)
        self.Discard_FULE(startLba, endLba, "FULE", expectPrgState, busyTimeout, continueWithErase)


    def SetTimeOut(self, OtherTO = None, WriteTO = None, ReadTO = None):
        """
        Description :   Set the reset, write and read timeout values
        Arguments   :
            otherTimeout   -   The reset timeout(hard)
            writeTimeout   -   The write timeout(hard)
            readTimeout    -   The read timeout(hard)
       Returns      :   None
       """
        if (OtherTO == None) or (WriteTO == None) or (ReadTO == None):
            OtherTO = int(self.__config.get('configBusyResetTO'))
            WriteTO = int(self.__config.get('configBusyWriteTO'))
            ReadTO = int(self.__config.get('configBusyReadTO'))

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "resetTO - %s, busyTO - %s, readTO - %s" % (OtherTO, WriteTO, ReadTO))
        sdcmdWrap.CardSetTimeout(resetTO = OtherTO, busyTO = WriteTO, readTO = ReadTO)


    def SingleWrite(self, StartLba, BlockCount, pattern = 0xaa):
        """
        Description : This function is used to run CMD24(Single Write Command) regardless of BlockCount given.
                      For instance : If BlockCount is 1, CMD24 will be called once.
                                     If BlockCount is 10, CMD24 will be called 10 times for each block.
        """
        if BlockCount > 1:
            EndLba = self.__sdCmdObj.calculate_endLba(StartLba, BlockCount)
            for startLba, blockCount in self.__sdCmdObj.Data_Trans_Breakup(StartLba, EndLba, 1):
                self.runtimeChangeLogLevel()    # To enable/disable the log during the run time
                try:
                    self.__sdCmdObj.Write(startLba = startLba, transferLen = blockCount, pattern = pattern)
                except ValidationError.CVFGenericExceptions as exc:
                    self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed SingleWrite to the card with StartLba: 0x%X, BlockCount: 0x%X" % (startLba, blockCount))
                    raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())
        else:
            self.__sdCmdObj.Write(startLba = StartLba, transferLen = BlockCount, pattern = pattern)


    def SingleRead(self, StartLba, BlockCount, pattern = 0x0):
        """
        Description : This function is used to run CMD17(Single Read Command) regardless of BlockCount given.
                      For instance : If BlockCount is 1, CMD17 will be called once.
                                     If BlockCount is 10, CMD17 will be called 10 times for each block.
        """
        readDataBuffer = ServiceWrap.Buffer.CreateBuffer(1, 0x0)
        self.__sdCmdObj.FillBufferWithTag(readDataBuffer, StartLba, BlockCount, pattern)
        if BlockCount > 1:
            EndLba = self.__sdCmdObj.calculate_endLba(StartLba, BlockCount)
            for startLba, blockCount in self.__sdCmdObj.Data_Trans_Breakup(StartLba, EndLba, maxTransfer = 1):
                self.runtimeChangeLogLevel()    # To enable/disable the log during the run time
                try:
                    self.__sdCmdObj.Read(startLba = startLba, transferLen = blockCount, readDataBuffer = readDataBuffer)
                except ValidationError.CVFGenericExceptions as exc:
                    self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed SingleRead to the card with StartLba: 0x%X, BlockCount: 0x%X" % (startLba, blockCount))
                    raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())
        else:
            self.__sdCmdObj.Read(startLba = StartLba, transferLen = BlockCount, readDataBuffer = readDataBuffer)


    def MultipleWrite(self, StartLba, BlockCount, pattern = None):
        if self.currCfg.variation.sdconfiguration == 'SPI':
            self.__sdCmdObj.SPIEnable(spiMode = True)
        self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "MultipleWrite to the card with StartLba: 0x%X, BlockCount: 0x%X"
                              % (StartLba, BlockCount))

        EndLba = self.__sdCmdObj.calculate_endLba(StartLba, BlockCount)
        for startLba, blockCount in self.__sdCmdObj.Data_Trans_Breakup(StartLba, EndLba, self.__maxTransferLength):
            self.runtimeChangeLogLevel()    # To enable/disable the log during the run time
            try:
                self.__sdCmdObj.Write(startLba = startLba, transferLen = blockCount)
            except ValidationError.CVFGenericExceptions as exc:
                self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed MultipleWrite to the card with StartLba: 0x%X, BlockCount: 0x%X" % (startLba, blockCount))
                raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())


    def MultWriteBlock(self, StartLba, lbacount, writebuffer):
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple write to the card with StartLBA:0x%X, BlockCount:0x%X" % (StartLba, lbacount))
        try:
            sdcmdWrap.MultWriteBlockCloseEnded(startLba = StartLba, blockCount = lbacount, szBuffer = writebuffer)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple write to the card with StartLBA:0x%X, BlockCount:0x%X completed" % (StartLba, lbacount))
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple write Failed with StartLBA:0x%X, BlockCount:0x%X" % (StartLba, lbacount))
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    def MultReadBlock(self, StartLba, lbacount, cmpbuffer, verify = True):
        readBuff = ServiceWrap.Buffer.CreateBuffer(lbacount, patternType = 0x00, isSector = True)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple read to the card with StartLBA:0x%X, BlockCount:0x%X" % (StartLba, lbacount))
        try:
            sdcmdWrap.MultReadBlockCloseEnded(startLba = StartLba, blockCount = lbacount, szBuffer = readBuff)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple read to the card with StartLBA:0x%X, BlockCount:0x%X completed" % (StartLba, lbacount))

            if verify == True:
                value = self.VerifyReaddata(cmpbuffer, readBuff, StartLba, lbacount)
                if value != 0:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Expected 'MISCOMPARE_ERROR' error occured for CMD18")
                else:
                    raise ValidationError.TestFailError(self.fn, "Expected 'MISCOMPARE_ERROR' error not occured for CMD18")
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple read failed with StartLBA:0x%X, BlockCount:0x%X" % (StartLba, lbacount))
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())


    def WriteWithFPGAPatternAndHandleException(self, StartLba, blockCount, pattern = 0, Anyword_variable = None, usePreDefBlkCount = False, SingleWrite = False, expected_exception="ERROR_NOT_EXPECTED"):

        try:
            self.WriteWithFPGAPattern(StartLba, blockCount, pattern, Anyword_variable, usePreDefBlkCount, SingleWrite)
        except ValidationError.CVFGenericExceptions as exc:
            errstring = exc.GetInternalErrorMessage()
            if (expected_exception == gvar.GlobalConstants.ERROR_NOT_EXPECTED):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple Read Failed %s" %expected_exception)
                raise ValidationError.TestFailError(self.fn, "Test Failed")
            else:
                if errstring.find(expected_exception) != -1:
                    self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple Read Failed as expected: %s" %expected_exception)
                    self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure
                else:
                    self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple Read Failed but not expected as %s" %expected_exception)
                    raise ValidationError.TestFailError(self.fn, "Test Failed - Error other than %s" %expected_exception)
        else:
            if (expected_exception != gvar.GlobalConstants.ERROR_NOT_EXPECTED):
                self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple Read Failed but not expected as %s" %expected_exception)
                raise ValidationError.TestFailError(self.fn, "Test Failed - Error other than %s" %expected_exception)


    def WriteWithFPGAPattern(self, StartLba, blockCount, pattern = 0, Anyword_variable = None, usePreDefBlkCount = False, SingleWrite = False):
        """
        Description:       Use FPGA Pattern generator for pattern generation for Write operation.
                           Support for MultipleWrite/SingleWrite based on SingleWrite argument value
                           For Pattern
                           1>  pattern == 0  # ALL ZERO'S (Note Default pattern)
                           2>  pattern == 1  # WORD_REPEATED
                           3>  pattern == 2  # INCREMENTAL
                           4>  pattern == 3  # RANDOM / ANY_BUFFER
                           5>  pattern == 4  # CONST
                           6>  pattern == 5  # ALL ONE'S
                           7>  pattern == 6  # ANYWORD/VARIABLE  Note: Anyword_variable argument is required and should be of int or hex
                           8>  pattern == 7  # WORD_BLOCK_NUMBER
                           9>  pattern == 8  # PATTERN_NEG_INCREMENTAL
                           10> pattern == 9  # PATTERN_NEG_CONST

                           Note: Filepattern and editorBuffer not implimented

                           CloseEnded (CMD23): usePreDefBlkCount - True
                           OpenEnded         : usePreDefBlkCount - False

        Returns: None
        """
        self.runtimeChangeLogLevel()    # To enable/disable the log during the run time

        # Workaround: When the blockCount is 0, Scripter_Directive/CTF_API sends 1 but not CVF. So, added work around.
        if blockCount == 0:
            blockCount = 1

        if gvar.GlobalConstants.SKIP_WRITE == True:
            self.__sdCmdObj.CARD_OUT_OF_RANGE_Validation(StartLba = StartLba, BlockCount = blockCount, Cmd = "WriteWithFPGAPattern")
            return

        if(pattern == 0):
            pattern_to_write = sdcmdWrap.Pattern.ALL_ZERO
            pattern_str = "Zero's Pattern"
        elif(pattern == 1):
            pattern_to_write = sdcmdWrap.Pattern.WORD_REPEATED
            pattern_str = "Wordrepeat Pattern"
        elif(pattern == 2):
            pattern_to_write = sdcmdWrap.Pattern.INCREMENTAL
            pattern_str = "Increment Pattern"
        elif(pattern == 3):
            # TOBEDONE: Pattern Random buffer is not working properly so using incremental instead of random
            pattern = 2
            pattern_to_write = sdcmdWrap.Pattern.INCREMENTAL
            pattern_str = "Increment Pattern"
            #pattern_to_write = ServiceWrap.Buffer.CreateBuffer(1 if SingleWrite else blockCount, patternType = 0x0, isSector = True)
            #self.RandomBufferFill(BufferObject = pattern_to_write)
            #pattern_str = "Random Pattern"
        elif(pattern == 4):
            pattern_to_write = sdcmdWrap.Pattern.CONST
            pattern_str = "Constant Pattern"
        elif(pattern == 5):
            pattern_to_write = sdcmdWrap.Pattern.ALL_ONE
            pattern_str = "One's Pattern"
        elif(pattern == 6):
            if Anyword_variable == None:
                raise ValidationError.TestFailError(self.fn, "For anyword pattern Anyword_variable argument is missing")
            pattern_to_write = ServiceWrap.Buffer.CreateBuffer(1 if SingleWrite else blockCount, patternType = 0x0, isSector = True)
            self.__sdCmdObj.BufferFilling(pattern_to_write, gvar.GlobalConstants.PATTERN_ANY_WORD, AnyWord = Anyword_variable)
            pattern_str = "Anyword Pattern " + str(Anyword_variable)
        elif(pattern == 7):
            pattern_to_write = sdcmdWrap.Pattern.WORD_BLOCK_NUMBER
            pattern_str = "WorkBockNumber Pattern"
        elif(pattern == 8):
            pattern_to_write = sdcmdWrap.Pattern.PATTERN_NEG_INCREMENTAL
            pattern_str = "Negative Increment Pattern"
        elif(pattern == 9):
            pattern_to_write = sdcmdWrap.Pattern.PATTERN_NEG_CONST
            pattern_str = "Negative Constant Pattern"
        else:   # default all 0's
            pattern_to_write = sdcmdWrap.Pattern.ALL_ZERO
            pattern_str = "Zero's Pattern"

        if SingleWrite == False:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "MultipleWrite to the card with StartLba: 0x%X, BlockCount: 0x%X, Pattern: %s"
                                  % (StartLba, blockCount, pattern_str))
            try:
                if pattern == 3 or pattern == 6:    # for random Pattern and anyword pattern
                    sdcmdWrap.MultWriteBlockCloseEnded(startLba = StartLba, blockCount = blockCount, szBuffer = pattern_to_write,
                                                        usePreDefBlkCount = usePreDefBlkCount)
                else:   # for Pattern Generation
                    sdcmdWrap.MultWriteBlockCloseEndedNoData(startLba = StartLba, blockCount = blockCount, uiPattern = pattern_to_write,
                                                             sectorTag = False, usePreDefBlkCount = usePreDefBlkCount)

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Done MultipleWrite with StartLba: 0x%X, BlockCount: 0x%X, Pattern: %s"
                                      % (StartLba, blockCount, pattern_str))
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "MultipleWrite Failed with StartLba: 0x%X, BlockCount: 0x%X, Pattern: %s, ErrorMessage: %s"
                                       % (StartLba, blockCount, pattern_str, exc.GetFailureDescription()))
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SingleWrite with StartLba: 0x%X, BlockCount: 0x%X, Pattern: %s"
                                  % (StartLba, blockCount, pattern_str))
            try:
                EndLba = self.__sdCmdObj.calculate_endLba(StartLba, blockCount)
                for CurrentStartLba, CurrentBlockCount in self.__sdCmdObj.Data_Trans_Breakup(StartLba, EndLba, maxTransfer = 1):    # maxTransfer is given 1 for single write
                    self.runtimeChangeLogLevel()    # To enable/disable the log during the run time
                    if pattern == 3 or pattern == 6:   # for random Pattern and anyword pattern
                        sdcmdWrap.WriteSingleBlock(startLba = CurrentStartLba, bNoData = False, szBuffer = pattern_to_write)
                    else:
                        sdcmdWrap.WriteBlockCloseEndedNoData(startLba = CurrentStartLba, blockCount = CurrentBlockCount, uiPattern = pattern_to_write,
                                                            sectorTag = False, usePreDefBlkCount = usePreDefBlkCount)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Done SingleWrite with StartLba: 0x%X, BlockCount: 0x%X, Pattern: %s"
                                      % (StartLba, blockCount, pattern_str))
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SingleWrite Failed with StartLba: 0x%X, BlockCount: 0x%X, Pattern: %s, ErrorMessage: %s"
                                       % (CurrentStartLba, CurrentBlockCount, pattern_str, exc.GetFailureDescription()))
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())


    def ReadWithFPGAPatternAndHandleException(self, StartLba, blockCount, pattern = 0, Anyword_variable = None, usePreDefBlkCount = False, SingleRead = False, expected_exception="ERROR_NOT_EXPECTED"):
        """
        Description: This API should be used for only handling expected exception in ReadWithFPGAPattern.
        """

        try:
            self.ReadWithFPGAPattern(StartLba, blockCount, pattern, Anyword_variable, usePreDefBlkCount, SingleRead)
        except ValidationError.CVFGenericExceptions as exc:
            errstring = exc.GetInternalErrorMessage()
            if errstring.find(expected_exception) != -1:
                self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple Read Failed as expected: %s" %expected_exception)
                self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure
            else:
                self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple Read Failed but not expected as %s" %expected_exception)
                raise ValidationError.TestFailError(self.fn, "Test Failed - Error other than %s" %expected_exception)
        else:
            if (expected_exception != gvar.GlobalConstants.ERROR_NOT_EXPECTED):
                self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple Read Failed but not expected as %s" %expected_exception)
                raise ValidationError.TestFailError(self.fn, "Test Failed - Error other than %s" %expected_exception)


    def ReadWithFPGAPattern(self, StartLba, blockCount, pattern = 0, Anyword_variable = None, usePreDefBlkCount = False, SingleRead = False, DoCompare=True):
        """
        Description:       Use FPGA Pattern generator for pattern generation for Read operation and compare the data
                           Support for MultipleRead/SingleRead based on SingleRead argument value
                           For Pattern
                           1>  pattern == 0  # ALL ZERO'S (Note Default pattern)
                           2>  pattern == 1  # WORD_REPEATED
                           3>  pattern == 2  # INCREMENTAL
                           4>  pattern == 3  # RANDOM / ANY_BUFFER
                           5>  pattern == 4  # CONST
                           6>  pattern == 5  # ALL ONE'S
                           7>  pattern == 6  # ANYWORD/VARIABLE  Note: Anyword_variable argument is required and should be of int or hex
                           8>  pattern == 7  # WORD_BLOCK_NUMBER
                           9>  pattern == 8  # PATTERN_NEG_INCREMENTAL
                           10> pattern == 9  # PATTERN_NEG_CONST

                           Note: Filepattern and editorBuffer not implimented

                           CloseEnded (CMD23): usePreDefBlkCount - True
                           OpenEnded         : usePreDefBlkCount - False

        Returns: None
        """
        self.runtimeChangeLogLevel()    # To enable/disable the log during the run time

        # Workaround: When the blockCount is 0, Scripter_Directive/CTF_API sends 1 but not CVF. So, added work around.
        if blockCount == 0:
            blockCount = 1

        if gvar.GlobalConstants.SKIP_READ == True:
            self.__sdCmdObj.CARD_OUT_OF_RANGE_Validation(StartLba = StartLba, BlockCount = blockCount, Cmd = "ReadWithFPGAPattern")
            return

        if(pattern == 0):
            pattern_to_read = sdcmdWrap.Pattern.ALL_ZERO
            pattern_str = "Zero's Pattern"
        elif(pattern == 1):
            pattern_to_read = sdcmdWrap.Pattern.WORD_REPEATED
            pattern_str = "Wordrepeat Pattern"
        elif(pattern == 2):
            pattern_to_read = sdcmdWrap.Pattern.INCREMENTAL
            pattern_str = "Increment Pattern"
        elif(pattern == 3):
            # Pattern Random buffer is not working properly so using incremental instead of random
            pattern = 2
            pattern_to_read = sdcmdWrap.Pattern.INCREMENTAL
            pattern_str = "Increment Pattern"
            # pattern_to_read = ServiceWrap.Buffer.CreateBuffer(1 if SingleRead else blockCount, patternType = 0x0, isSector = True)
            # buffer_to_check_with = ServiceWrap.Buffer.CreateBuffer(1 if SingleRead else blockCount, patternType = 0x0, isSector = True)
            # self.RandomBufferFill(BufferObject = buffer_to_check_with)
            # pattern_str = "Random Pattern"
        elif(pattern == 4):
            pattern_to_read = sdcmdWrap.Pattern.CONST
            pattern_str = "Constant Pattern"
        elif(pattern == 5):
            pattern_to_read = sdcmdWrap.Pattern.ALL_ONE
            pattern_str = "One's Pattern"
        elif(pattern == 6):
            if Anyword_variable == None:
                raise ValidationError.TestFailError(self.fn, "For anyword pattern Anyword_variable argument is missing")
            pattern_to_read = ServiceWrap.Buffer.CreateBuffer(1 if SingleRead else blockCount, patternType = 0x0, isSector = True)
            buffer_to_check_with = ServiceWrap.Buffer.CreateBuffer(1 if SingleRead else blockCount, patternType = 0x0, isSector = True)
            self.__sdCmdObj.BufferFilling(buffer_to_check_with, gvar.GlobalConstants.PATTERN_ANY_WORD, AnyWord = Anyword_variable)
            pattern_str = "Anyword Pattern " + str(Anyword_variable)
        elif(pattern == 7):
            pattern_to_read = sdcmdWrap.Pattern.WORD_BLOCK_NUMBER
            pattern_str = "WorkBockNumber Pattern"
        elif(pattern == 8):
            pattern_to_read = sdcmdWrap.Pattern.PATTERN_NEG_INCREMENTAL
            pattern_str = "Negative Increment Pattern"
        elif(pattern == 9):
            pattern_to_read = sdcmdWrap.Pattern.PATTERN_NEG_CONST
            pattern_str = "Negative Constant Pattern"
        else:       # default all 0's
            pattern_to_read = sdcmdWrap.Pattern.ALL_ZERO
            pattern_str = "Zero's Pattern"

        if SingleRead == False:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "MultipleRead to the card with StartLba: 0x%X, BlockCount: 0x%X, Pattern: %s"
                                  % (StartLba, blockCount, pattern_str))
            try:
                if pattern == 3 or pattern == 6:       # for random Pattern and anyword pattern
                    sdcmdWrap.MultReadBlockCloseEnded(startLba = StartLba, blockCount = blockCount, szBuffer = pattern_to_read, usePreDefBlkCount = usePreDefBlkCount)
                    if DoCompare:
                        self.__sdCmdObj.BufferCompare(writeBuffer = buffer_to_check_with, readBuffer = pattern_to_read)
                else:   # Pattern Gen pattern
                    sdcmdWrap.MultReadBlockCloseEndedNoData(startLba = StartLba, blockCount = blockCount, uiPattern = pattern_to_read,
                                                            sectorTag = False, usePreDefBlkCount = usePreDefBlkCount, bCompare=DoCompare)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Done MultipleRead with StartLba: 0x%X, BlockCount: 0x%X, Pattern: %s"
                                      % (StartLba, blockCount, pattern_str))
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "MultipleRead Failed with StartLba: 0x%X, BlockCount: 0x%X, Pattern: %s, ErrorMessage: %s"
                                       % (StartLba, blockCount, pattern_str, exc.GetFailureDescription()))
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SingleRead with StartLba: 0x%X, BlockCount: 0x%X, Pattern: %s"
                                  % (StartLba, blockCount, pattern_str))
            try:
                EndLba = self.__sdCmdObj.calculate_endLba(StartLba, blockCount)
                for CurrentStartLba, CurrentBlockCount in self.__sdCmdObj.Data_Trans_Breakup(StartLba, EndLba, maxTransfer = 1):    # maxTransfer is given 1 for single read
                    self.runtimeChangeLogLevel()    # To enable/disable the log during the run time
                    if pattern == 3 or pattern == 6:       # for random Pattern and anyword pattern
                        sdcmdWrap.ReadSingleBlock(startLba = CurrentStartLba, bNoData = False, szBuffer = pattern_to_read)
                        if DoCompare:
                            self.__sdCmdObj.BufferCompare(writeBuffer = buffer_to_check_with, readBuffer = pattern_to_read)
                    else:       # Pattern Gen pattern
                        sdcmdWrap.ReadBlockCloseEndedNoData(startLba = CurrentStartLba, blockCount = CurrentBlockCount, uiPattern = pattern_to_read,
                                                            sectorTag = False, usePreDefBlkCount = usePreDefBlkCount, bCompare=DoCompare)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Done SingleRead with StartLba: 0x%X, BlockCount: 0x%X, Pattern: %s"
                                % (StartLba, blockCount, pattern_str))
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SingleRead Failed with StartLba: 0x%X, BlockCount: 0x%X, Pattern: %s, ErrorMessage: %s"
                                       % (CurrentStartLba, CurrentBlockCount, pattern_str, exc.GetFailureDescription()))
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    def ReadWithPattern(self, StartLba, blockCount, Expected_Anyword_variable_pattern = None, SingleRead = False, filename = None, editorbuffer = None, verify = True):
        """
        Description:       Reads the Data from the card and Compares it with expected pattern.
                           Support for MultipleRead/SingleRead based on SingleRead value
                           For Pattern
                               1> Anyword Pattern: Buffer is fill with value in Expected_Anyword_variable_pattern
                               2> Variable Pattern: Buffer is fill with value in Expected_Anyword_variable_pattern
                               3> File Pattern: Buffer is filled by reading file, filename argument is used here
                               4> Editor Pattern: Buffer is filled/copieed with editorbuffer argument.

                           Note: The Expected_Anyword_variable_pattern values has to int, hex, list values.
                           More details are available on Buffer API
        Returns: None
        """
        self.runtimeChangeLogLevel()    # To enable/disable the log during the run time

        if Expected_Anyword_variable_pattern != None:
            self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Expected anyword or variable pattern: %s" % Expected_Anyword_variable_pattern)
            ExpectedDataBuffer = ServiceWrap.Buffer.CreateBuffer(self.__maxTransferLength, patternType = Expected_Anyword_variable_pattern, isSector = True)
        elif filename != None:
            self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Expected pattern file name: %s" % filename)
            # TOBEDONE: FileDataBufferPattern
            #ExpectedDataBuffer = Buffer.FileDataBufferPattern(filename,loopUntilFull) ????
            raise
        elif editorbuffer != None:
            self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Expected pattern is from buffer")
            ExpectedDataBuffer = editorbuffer
        else:
            ExpectedDataBuffer = ServiceWrap.Buffer.CreateBuffer(self.__maxTransferLength, patternType = ServiceWrap.ALL_0, isSector = True)
            self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Pattern Not Provided, using Default Pattern 0's")     # if verify is false

        ReadDataBuffer = ServiceWrap.Buffer.CreateBuffer(self.__maxTransferLength, patternType = ServiceWrap.ALL_0, isSector = True)
        EndLba = self.__sdCmdObj.calculate_endLba(StartLba, blockCount)

        if SingleRead == False:
            self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Multiple Read in card from StartLba:0x%X to EndLba:0x%X" % (StartLba, EndLba))
            try:
                for StartAddress, blockCount in self.__sdCmdObj.Data_Trans_Breakup(StartLba, EndLba, self.__maxTransferLength):
                    self.__sdCmdObj.Read(StartAddress, blockCount, ReadDataBuffer)
                    #self.__sdCmdObj.Cmd12()
                    self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Read with StartLba:0x%X, BlockCount:0x%X" % (StartAddress, blockCount))

                    if verify == True:
                        self.VerifyReaddata(ExpectedDataBuffer, ReadDataBuffer, StartAddress, blockCount)

            except ValidationError.CVFGenericExceptions as exc:
                self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "MultipleRead Failed with StartLba:0x%X, BlockCount:0x%X" % (StartAddress, blockCount))
                raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

            self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Read from StartLba:0x%X to EndLba:0x%X"
                                  % (StartLba, EndLba))
        else:
            self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SingleRead from StartLba: 0x%X to EndLba:0x%X" % (StartLba, EndLba))
            try:
                for StartAddress, blockCount in self.__sdCmdObj.Data_Trans_Breakup(StartLba, EndLba, self.__maxTransferLength):
                    self.__sdCmdObj.Read(StartAddress, blockCount, readDataBuffer = ReadDataBuffer)
                    self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed SingleRead at StartLba: 0x%X" % StartAddress)

                    if verify == True:
                        self.VerifyReaddata(ExpectedDataBuffer, ReadDataBuffer, StartAddress, blockCount)

            except ValidationError.CVFGenericExceptions as exc:
                self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SingleRead Failed at StartLba:0x%X" % StartAddress)
                raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

            self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed SingleRead from StartLba: 0x%X to EndLba:0x%X" % (StartLba, EndLba))

    def LogicalWrite(self, lba, sectorCount, wrBuffer):
        """
        Note: Equivalent CVF API for the CTF API self.__card.WriteLba is not available in CVF, But the SDR host logs
        of CTF API self.__card.WriteLba and CMD25 send through SendBasicCommand in CVF are looks similar. Hence, CMD25
        and CMD12 are called in below implementation.
        """
        if gvar.GlobalConstants.SKIP_WRITE == True:
            self.__sdCmdObj.CARD_OUT_OF_RANGE_Validation(StartLba = sectorCount, BlockCount = lba, Cmd = "LogicalWrite")
            return

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "LogicalWrite called")
        try:
            self.__sdCmdObj.Cmd25(startLbaAddress = lba, transferLen = sectorCount, writeDataBuffer = wrBuffer)
            self.__sdCmdObj.Cmd12()
        except ValidationError.CVFGenericExceptions as exc:
            raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "LogicalWrite completed")

    def LogicalRead(self, lba, sectorCount, cmpBuffer, compare = True):
        """
        Note: Equivalent CVF API for the CTF API self.__card.ReadLba is not available in CVF, But the SDR host logs
        of CTF API self.__card.ReadLba and CMD18 send through SendBasicCommand in CVF are looks similar. Hence, CMD18
        and CMD12 are called in below implementation.
        """
        if gvar.GlobalConstants.SKIP_READ == True:
            self.__sdCmdObj.CARD_OUT_OF_RANGE_Validation(StartLba = sectorCount, BlockCount = lba, Cmd = "LogicalRead")
            return

        rdBuffer = ServiceWrap.Buffer.CreateBuffer(sectorCount, 0x0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "LogicalRead called")
        try:
            self.__sdCmdObj.Cmd18(startLbaAddress = lba, transferLen = sectorCount, readDataBuffer = rdBuffer)
            self.__sdCmdObj.Cmd12()
            if compare == True:
                cmpBuffer.Compare(buf = rdBuffer)
        except ValidationError.CVFGenericExceptions as exc:
            raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "LogicalRead completed")

    def GET_SCR_Reg_Values(self):
        """
        Description: Get the SCR Register values in Dictionary format and Logs it. For more Information refer section 5.6 SCR register in SD Spec 7.0.
        """

        self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##### SCR Register #####")

        self.__sdCmdObj.Cmd55()
        scrReg = self.__sdCmdObj.GetSCRRegisterEntry()

        SCR_Register_Values = {}

        # For SCR_STRUCTURE refer Table 5-18 : SCR Register Structure Version in spec 7.0
        if scrReg.objSCRRegister.ui8ScrStructure == 0:
            SCR_Register_Values["SCR_STRUCTURE"] = "SCR_VERSION_1.0"
        else:
            SCR_Register_Values["SCR_STRUCTURE"] = "RESERVED"

        SCR_Register_Values["SCR_STRUCTURE_Value"] = scrReg.objSCRRegister.ui8ScrStructure

        # For SD_SPEC refer Table 5-19 : Physical Layer Specification Version in spec 7.0
        SD_SPEC = scrReg.objSCRRegister.ui8SdSpec
        SD_SPEC3 = scrReg.objSCRRegister.ui16SdSpec3
        SD_SPEC4 = scrReg.objSCRRegister.ui16SdSpec4
        SD_SPECx = scrReg.objSCRRegister.ui16SdSpecx

        if SD_SPEC == 0 and SD_SPEC3 == 0 and SD_SPEC4 == 0 and SD_SPECx == 0:
            SCR_Register_Values["SD_SPEC"] = "SPEC VERSION 1.0"
        elif SD_SPEC == 1 and SD_SPEC3 == 0 and SD_SPEC4 == 0 and SD_SPECx == 0:
            SCR_Register_Values["SD_SPEC"] = "SPEC VERSION 1.10"
        elif SD_SPEC == 2 and SD_SPEC3 == 0 and SD_SPEC4 == 0 and SD_SPECx == 0:
            SCR_Register_Values["SD_SPEC"] = "SPEC VERSION 2"
        elif SD_SPEC == 2 and SD_SPEC3 == 1 and SD_SPEC4 == 0 and SD_SPECx == 0:
            SCR_Register_Values["SD_SPEC"] = "SPEC VERSION 3"
        elif SD_SPEC == 2 and SD_SPEC3 == 1 and SD_SPEC4 == 1 and SD_SPECx == 0:
            SCR_Register_Values["SD_SPEC"] = "SPEC VERSION 4"
        elif SD_SPEC == 2 and SD_SPEC3 == 1 and (SD_SPEC4 == 0 or SD_SPEC4 == 1) and SD_SPECx == 1:
            SCR_Register_Values["SD_SPEC"] = "SPEC VERSION 5"
        elif SD_SPEC == 2 and SD_SPEC3 == 1 and (SD_SPEC4 == 0 or SD_SPEC4 == 1) and SD_SPECx == 2:
            SCR_Register_Values["SD_SPEC"] = "SPEC VERSION 6"
        elif SD_SPEC == 2 and SD_SPEC3 == 1 and (SD_SPEC4 == 0 or SD_SPEC4 == 1) and SD_SPECx == 3:
            SCR_Register_Values["SD_SPEC"] = "SPEC VERSION 7"
        else:
            SCR_Register_Values["SD_SPEC"] = "RESERVED"

        SCR_Register_Values["SD_SPEC_Values"] = [SD_SPEC, SD_SPEC3, SD_SPEC4, SD_SPECx]

        # For DATA_STAT_AFTER_ERASE Note : This is vendor specific
        if(scrReg.objSCRRegister.ui8DataStateAfterErase == 0):
            SCR_Register_Values["DATA_STAT_AFTER_ERASE"] = 0
        else:
            SCR_Register_Values["DATA_STAT_AFTER_ERASE"] = 1
        SCR_Register_Values["DATA_STAT_AFTER_ERASE_Value"] = scrReg.objSCRRegister.ui8DataStateAfterErase

        # For SD_SECURITY refer Table 5-20 : CPRM Security Version in spec 7.0
        if (scrReg.objSCRRegister.ui8SdSecurity == 0):
            SCR_Register_Values["SD_SECURITY"] = "No Security"
        elif (scrReg.objSCRRegister.ui8SdSecurity == 1):
            SCR_Register_Values["SD_SECURITY"] = "Not Used"
        elif (scrReg.objSCRRegister.ui8SdSecurity == 2):
            SCR_Register_Values["SD_SECURITY"] = "SECURITY VERSION 1.01"    # SDSC Card
        elif (scrReg.objSCRRegister.ui8SdSecurity == 3):
            SCR_Register_Values["SD_SECURITY"] = "SECURITY VERSION 2.00"    # SDHC Card
        elif (scrReg.objSCRRegister.ui8SdSecurity == 4):
            SCR_Register_Values["SD_SECURITY"] = "SECURITY VERSION 3.00"    # SDXC Card
        else:
            SCR_Register_Values["SD_SECURITY"] = "RESERVED"

        SCR_Register_Values["SD_SECURITY_Value"] = scrReg.objSCRRegister.ui8SdSecurity

        # For SD_BUS_WIDTHS refer Table 5-21 : SD Memory Card Supported Bus Widths in spec 7.0
        Four_bit_data = '{:04b}'.format(scrReg.objSCRRegister.ui8SdBusWidth)    # Convert the integer value into 4 bit binary(SCR slice [51:48])
        if (Four_bit_data[3] == "1" and Four_bit_data[1] == "1"):
            SCR_Register_Values["SD_BUS_WIDTHS"] = "1 bit [DAT0] and 4 bit (DAT0-3)"
        elif (Four_bit_data[3] == "1"):     # Four_bit_data[3] is 48th bit of SCR register
            SCR_Register_Values["SD_BUS_WIDTHS"] = "1 bit [DAT0]"
        elif (Four_bit_data[1] == "1"):     # Four_bit_data[1] is 50th bit of SCR register
            SCR_Register_Values["SD_BUS_WIDTHS"] = "4 bit (DAT0-3)"
        else:
            SCR_Register_Values["SD_BUS_WIDTHS"] = "RESERVED"

        # For EX_SECURITY refer Table 5-22 : Extended Security in spec 7.0
        if (scrReg.objSCRRegister.ui16ExSecurity == 0):
            SCR_Register_Values["EX_SECURITY"] = "Extended_Security_Not_Supported"
        else:
            SCR_Register_Values["EX_SECURITY"] = "Extended_Security_Supported"

        SCR_Register_Values["EX_SECURITY_Value"] = scrReg.objSCRRegister.ui16ExSecurity

        # For CMD_SUPPORT refer Table 5-23 : Command Support Bits in spec 7.0
        SCR_Register_Values["CMD_SUPPORT"] = []
        if (scrReg.objSCRRegister.ui16CmdSupport & 0x01) == 1:
            SCR_Register_Values["CMD_SUPPORT"].append("CMD20_Supported")
        if (scrReg.objSCRRegister.ui16CmdSupport & 0x02) == 2:
            SCR_Register_Values["CMD_SUPPORT"].append("CMD23_Supported")
        if (scrReg.objSCRRegister.ui16CmdSupport & 0x04) == 4:
            SCR_Register_Values["CMD_SUPPORT"].append("CMD48_CMD49_Supported")
        if (scrReg.objSCRRegister.ui16CmdSupport & 0x08) == 8:
            SCR_Register_Values["CMD_SUPPORT"].append("CMD58_CMD59_Supported")

        SCR_Register_Values["CMD_SUPPORT_Value"] = scrReg.objSCRRegister.ui16CmdSupport

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SCR_STRUCTURE Version             : %s" % SCR_Register_Values["SCR_STRUCTURE"])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SD Memory Card - Spec. Version    : %s" % SCR_Register_Values["SD_SPEC"])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Data_Status_After Erases          : %s" % SCR_Register_Values["DATA_STAT_AFTER_ERASE"])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CPRM Security Support             : %s" % SCR_Register_Values["SD_SECURITY"])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DAT Bus widths supported          : %s" % SCR_Register_Values["SD_BUS_WIDTHS"])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Extended Security Support         : %s" % SCR_Register_Values["EX_SECURITY"])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Command Support                   : %s" % SCR_Register_Values["CMD_SUPPORT"])
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "##### SCR Register #####\n")

        return SCR_Register_Values

    def Identification(self):
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification of card(CMD2 and CMD3)")

        self.__sdCmdObj.Cmd2()
        RCA = self.__sdCmdObj.Cmd3()
        try:
            sdcmdWrap.SetCardRCA(RCA)
            sdcmdWrap.SDRSetFrequency(25 * 1000 * 1000)     # 25MHz required as per SD Spec
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification of card completed\n")

        except ValidationError.CVFGenericExceptions as exc:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification command failed")
            self.Exception_Details(exc)

    def Reset(self, mode, ocr, cardSlot = 0x1, sendCmd8 = True, initInfo = None, rca = 0x0,
              time = 0x0, sendCMD0 = 0x1, bHighCapacity = True, bSendCMD58 = False, version = 0x1,
              VOLA = 0x1, cmdPattern = 0xAA, reserved = 0x0, expOCRVal = None, sendCMD1 = False):
        """
        Parameters:
        mode - sdcmdWrap.CARD_MODE.Sd or sdcmdWrap.CARD_MODE.SD_IN_SPI
        ocr - the ocr value
        cardSlot - the card slot
        SendCMD8 - send command 8
        initInfo - initialization Buffer
        rca - relative card address
        time - the timeout value incase of Soft Reset enable
        sendCMD0 - Flag for cmd0
        bHighCapacity - True if high capacity card
        bSendCMD58 - send Cmd58
        version - byte value mentioning the version
        VOLA - byte value for VOLA
        cmdPattern - command pattern byte value
        reserved - DWORD Reserved paramenters
        sendCMD1 - Send CMD1 in SPI mode

        Returns: ocr value
        """
        if initInfo == None:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "InitInfo Buffer is None, Default buffer used")
            initInfo = ServiceWrap.Buffer.CreateBuffer(1, patternType = ServiceWrap.ALL_0, isSector = True)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Reset the card with OCR value : 0x%X" % ocr)

        try:
            Expected_Resp = sdcmdWrap.CardReset(mode, ocr = ocr, cardSlot = cardSlot, bSendCMD8 = sendCmd8,
                                                initInfo = initInfo, rca = rca, time = time, sendCMD0 = sendCMD0,
                                                bHighCapacity = bHighCapacity, bSendCMD58 = bSendCMD58, version = version,
                                                VOLA = VOLA, cmdPattern = cmdPattern, reserved = reserved, sendCMD1 = sendCMD1)
            self.__sdCmdObj.OCRRegister = Expected_Resp
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Response of CardReset: 0x%X" % Expected_Resp)

            # Below are the return values from initInfo buffer
            hicapfromcard = initInfo.GetOneByteToInt(0)
            VOLAvalfromcard = initInfo.GetOneByteToInt(3)
            CMDPatternfromcard = initInfo.GetOneByteToInt(4)
            Reservedbitsfromcard = initInfo.GetFourBytesToInt(5, little_endian = False)

            if bHighCapacity == True:
                if (hicapfromcard == 1):
                    self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card response as High Capacity from card.")
                else:
                    self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card response is not High Capacity from card")

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VOLA from card : 0x%X" % VOLAvalfromcard)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD Pattern from card : 0x%X" % CMDPatternfromcard)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Reserved bits from card : 0x%X" % Reservedbitsfromcard)

            if (expOCRVal != None) and (Expected_Resp != expOCRVal):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Expected OCR value is 0x%X, and OCR response value is 0x%X" % (expOCRVal, Expected_Resp))
                raise ValidationError.TestFailError(self.fn, "Expected OCR value is 0x%X, and OCR response value is 0x%X" % (expOCRVal, Expected_Resp))

            return Expected_Resp, initInfo
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed to Reset the card")
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    def HWReset(self, HostReset = True):
        """
        Description: Reset the host to its default.
        """
        try:
            sdcmdWrap.SDRHostReset(bRestoreSettings = HostReset)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    def SetSdMmcCardMode(self, CardMode, SetMode = True):
        """
        Arguments:
                  Cardmode - MMC = 0, MMC_IN_SPI = 1, SD = 2, SD_IN_SPI = 3
                  SetMode - bool value, set True to set the mode
        """
        try:
            raise ValidationError.TestFailError(self.fn, "SetSdMmcCardMode API is not implemented in CVF")
            # TOBEDONE: SetSdMmcCardMode
            #self.__card.SetSdMmcCardMode(CardMode, SetMode)    # CTF API
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    def SetCardMode(self, CardMode):
        """
        Description: set CardMode(bool value) = true then Set SPI mode, set Driver SPI value to True for SPI mode else CardMode = False for SD mode,
        """
        try:
            sdcmdWrap.SetCardMode(modeSPI = CardMode)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    def SelectCard(self, Select = True):
        """
        Note:
        """
        try:
            self.__sdCmdObj.Select_Deselect_Card(Select = Select)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    def SetCardCap(self, hiCap):
        """
        Description : Set Card to High capacity, Adjust driver to HC card.
        Argument : bool hiCap, True for high capacity
        """
        try:
            sdcmdWrap.SetCardCap(bIsHighCap = hiCap)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    def SEND_TUNING_PATTERN(self, numOfCmd, timeOut, bufErr):
        """
        Parametres:
            numOfCmd - (as byte)
            timeOut - A timeout value (as DWORD)
            bufErr - A buffer to receive additional error information (optional)
        """
        try:
            TuningResultBuffer = ServiceWrap.Buffer.CreateBuffer(dataSize = 1, patternType = 0x0, isSector = True)
            sdcmdWrap.TuneHostForUHS(optimalTap = [], tuningBuffer = TuningResultBuffer)
            return TuningResultBuffer
            # raise ValidationError.TestFailError(self.fn, "SendTuningPattern_CMD19 API is not implemented in CVF")
            # TOBEDONE: SendTuningPattern_CMD19
            #self.__card.SendTuningPattern_CMD19(numOfCmd,timeOut,bufErr)  # CTF API
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    #def Delay(self, TimeOut):
        #"""
        #python's time.sleep was used inside of Delay CTF API. Use time.sleep wherever Delay API is called in testscript.
        #"""
        #try:
            ## TOBEDONE : Delay
            ##self.__card.Delay(TimeOut)
            #pass
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Delay Error")
            #raise


    def enableACMD41(self):
        """
        Description:
                EnableACMD41 API enable ACMD41. To be used when for/in SPI mode.
                Allows to pass ACDM41 when reset used for SPI Mode
        arguments: NONE
        return : NONE
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "EnableACMD41 API Called")
        try:
            sdcmdWrap.EnableACMD41()
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "EnableACMD41 API completed\n")
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.TestFailError(self.fn, "Failed to enable ACMD41: %s" % exc.GetFailureDescription())

    def SwitchHostVoltageRegion(self, switch = False):
        '''
        API for SwitchHostVoltageRegion
        Switch Host Volt to 3.3V
        Argument: switch = False: 3.3v
                           True : 1.8v
        '''
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SwitchHostVoltageRegion to %sv called" % (1.8 if switch else 3.3))
        try:
            sdcmdWrap.SwitchHostVoltageRegion(switch)   # True : Switch to 1.8V else 3.3V
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SwitchHostVoltageRegion to %sv Completed\n" % (1.8 if switch else 3.3))
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SwitchHostVoltageRegion to %sv Failed" % (1.8 if switch else 3.3))
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s" % exc.GetFailureDescription())
            raise ValidationError.TestFailError(self.fn, "Failed to switch to host voltage")

    def CardInfo(self):
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "**** CARD INFO ****")

        if self.__sdCmdObj.CIDRegister != None:
            ProductSerialNumber = self.__sdCmdObj.CIDRegister.cidRegisterFieldStruct.uiPsn  # ProductSerialNumber can be get from CID Register
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ProductSerialNumber = 0x%X" % ProductSerialNumber)

        if self.__sdCmdObj.SD_Status != None:
            issecure = self.__sdCmdObj.SD_Status.objSDStatusRegister.ui64SecureMode         # SECURED_MODE can be get from SD Status
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Is card secure = %d" % issecure)

        CardMaximumLBA = sdcmdWrap.WrapGetMaxLBA()
        CardCapacity = sdcmdWrap.WrapGetCardCapacity()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CardMaximumLBA = 0x%X" % CardMaximumLBA)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CardCapacity = %s" % CardCapacity)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "**** CARD INFO ****\n")


    def Setting_PhasedGarbageCollection(self, enable_PGC = False, iPollingTime = None):
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Setting_PhasedGarbageCollection is called")
        # SCTPCommand API can be used for below API
        # TOBEDONE: SetPhasedGarbageCollectionMechaniosm

        try:
            PyEnableGCObj = sdcmdWrap.PyEnableGC()
            if(enable_PGC == True):  # else part will be default values
                PyEnableGCObj.bEnable = enable_PGC
                PyEnableGCObj.iPollingTime = iPollingTime
            raise ValidationError.TestFailError(self.fn, "CVF API SetPhasedGarbageCollectionMechaniosm is not implemented or SCTPCommand should be called from testcase")
            # self.__card.SetPhasedGarbageCollectionMechaniosm(PyEnableGCObj) # CTF API
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Setting_PhasedGarbageCollection: Phase Garbage Collection is set with polling time(in sec) %d"
                                  % PyEnableGCObj.iPollingTime)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Setting_PhasedGarbageCollection: Failed to set Phase Garbage Collection is set")
            self.Exception_Details(exc)
        # end of Setting_PhasedGarbageCollection


    def Exception_Details(self, exc):
        if exc.GetErrorNumber() == 0x1:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Time out error on card response")
        elif exc.GetErrorNumber() == 0x11C:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification command failed")
        elif exc.GetErrorNumber() == 0xF5:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "POWER ON-OFF General Error")
        elif exc.GetErrorNumber() == 0x1F or exc.GetErrorNumber() == 0xE014001F:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CARD_OUT_OF_RANGE occured")
        elif exc.GetErrorNumber() == 5124:
            self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Data Miscompare Error")
        elif exc.GetErrorNumber() == 0x1B:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Time out receive data or Busy Time out")
        elif exc.GetErrorNumber() == 0x8 or exc.GetErrorNumber() == 0xE0140008:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card is reporting illegal command")
        elif exc.GetErrorNumber() == 0xB:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card is reporting MMC card internal error")
        else:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Exception raised!!!, Error Number is %s and Error Group is %s"
                                   % (exc.GetErrorNumber(), exc.GetErrorGroup()))

        self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Error Message -> %s" % exc.GetFailureDescription())

        raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())


    def ReadFirmwareFile(self, fileID):
        '''
        API for Read firmware file
        Argument: File ID
        returns: Firmware Buffer
        '''
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ReadFirmwareFile called")
        try:
            raise ValidationError.TestFailError(self.fn , "ReadFirmware File ID or ReadFile API is not implemented in CVF")
            fileSize = None
            #fileSize=self.__card.GetFileSize(fileID)    # This is CTF line, need to write CVF line of this line.
            fileBuff = ServiceWrap.Buffer.CreateBuffer(fileSize, patternType = ServiceWrap.ALL_0, isSector = True)
            raise ValidationError.TestFailError(self.fn, "ReadFile API is not implemented in CVF")
            #self.__card.ReadFile(fileBuff,fileID,fileSize)  # This is CTF line, need to write CVF line of this line.
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ReadFirmwareFile Completed\n")
            return fileBuff
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ReadFirmwareFile Failed")
            self.__sdCmdObj.ErrorPrint(exc)
            raise ValidationError.TestFailError(self.fn, exc.GetFailureDescription())


    def R1bCommandAbort(self, commandIndex, commandArgument, busyTimeout, abortType, timeUnits, abortCommandIndex,
                        abortCommandArgument, abortCommandResponse, abortDuringBusy, abortTiming, hitIndication = False):
        """
        Parameters Description:
            commandIndex - (byte) command number. Example: 12
            commandArgument - (unsigned long) 32-bit argument to be passed along with the command
            busyTimeout - (int) busy timeout in msec
            abortType - (sdcmdWrap.ER1bAbortType) abort type. Powerloss/ Hw Reset/ command (without Data)
            timeUnits - (sdcmdWrap.EEnancedOpTimeUnits) time units
            abortCommandIndex - (int) (valid only if abortType is Command) abort command number
            abortCommandArgument-(unsigned long) (valid only if abortType is Command) 32-bit argument to be passed along with the command
            abortCommandResponse- (sdcmdWrap.RESP_TYPE) (valid only if abortType is Command) Response type
            abortDuringBusy - (bool) True/False (abort timing reference - During busy time)
            abortTiming - (unsigned long) time value. Example: 10
            hitIndication - (bool) True/False
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "R1bCommandAbort called")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name,
                    "commandIndex - %s, commandArgument - %s, busyTimeout - %s, abortType - %s, timeUnits - %s, abortCommandIndex - %s, abortCommandArgument - %s, abortCommandResponse - %s, abortDuringBusy - %s, abortTiming - %s, hitIndication - %s"
                    % (commandIndex, commandArgument, busyTimeout, abortType, timeUnits, abortCommandIndex, abortCommandArgument, abortCommandResponse, abortDuringBusy, abortTiming, hitIndication))
        try:
            sdcmdWrap.R1bCommandAbort(commandIndex, commandArgument, busyTimeout, abortType, timeUnits, abortCommandIndex,
                                      abortCommandArgument, abortCommandResponse, abortDuringBusy, abortTiming, hitIndication)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.__sdCmdObj.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "R1bCommandAbort completed")


    def SingleCmd25(self, arg, BlockCount, Pattern, Anyword = 0x0):  # For Pattern Generation write
        """
        Cmd25: WRITE_MULTIPLE_BLOCK
        To be used when SingleCommand scripter API is used with FPGA pattern generator

        Note : The date written using filled Buffer from host will vary from PG buffer.
        Same will be applicable for Multiple Read's
        This API to be used when R1bCommandAbort to be used, For all other Single Command 24,25,17,18 used FPGA read and writes,
        verified from scripter code. While using ANY_BUFFER pattern getting 'Error::Windows message::Invalid access to memory location' error.
        """
        self.__responseDataBuf =  ServiceWrap.Buffer.CreateBuffer(1, 0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 25, argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_MULTWRITE)

        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = BlockCount
        commandDataDefinitionObj.uiBlockLen = 512
        commandDataDefinitionObj.uiDataPattern = Pattern
        commandDataDefinitionObj.aIsSectorTag = False
        commandDataDefinitionObj.uiAnyWordPattern = Anyword
        try:
            CMD25 = sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            retValue = self.__responseDataBuf.GetData(0, 6)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R1 type response: %s" % retValue)


    def switchProtocol(self, ScriptName = None):
        protocolName = self.vtfContainer.getActiveProtocol()    # Get current protocol
        if (protocolName == "NVMe_OF_SDPCIe" or protocolName == "NVMe"):
            self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SwitchProtocol----------------------------------------------------------------")
            self.vtfContainer.switchProtocol()      # if current protocol is NVMe then switch to SD protocol
            protocolName = self.vtfContainer.getActiveProtocol()

            if protocolName == "NVMe_OF_SDPCIe":
                protocolName = "NVME"
            if protocolName == "SD_OF_SDPCIe":
                protocolName = "SD"

            if (protocolName == "SD_OF_SDPCIe" or protocolName == "SD"):
                self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Active Protocol is SD_OF_SDPCIe-------------------------------------------------------")
            else:
                raise ValidationError.VtfGeneralError(self.fn, "Failed to Switch Protocol.\n")
        return protocolName

    def ErrorHandlerFunction(self, errorGroup, errorCode):
        self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s : %s" % ("ErrorGroup is", errorGroup))
        self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s : %s" % ("ErrorCode is", errorCode))
        # below CleanPendingExceptions method will let us run testcases even if exception is raised, but it won't work for fatal errors.
        # self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure

    def VerifyReaddata(self, ExpectedDataBuffer, ReadDataBuffer, startlba = None, BlockCount = None):
        """
        Description: Compare the buffers patterns upto BlockCount.
        Returns: None
        """
        try:
            value = ExpectedDataBuffer.Compare(srcBuf = ReadDataBuffer, thisOffset = 0, srcOffset = 0, count = BlockCount * 512)
            self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VerifyReaddata: Completed Read & Verify with StartLba:0x%X, BlockCount:0x%X\n" % (startlba, BlockCount))
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription)
        else:
            if value != 0:
                raise ValidationError.CVFGenericExceptions(self.fn, "CARD_COMPARE_ERROR error occured. Read buffer is not equal to written buffer")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_WRITE_AND_READ_DATA_VERIFIED)
        return value

    def SetSpecialModes(self, HostRegisterMode, SetMode):
        """
        Purpose: Set Special Modes provided by SDR Host

         HostRegisterMode - (int) One of the available host register modes
                            Available Host register modes are:
                            ----------------------------------
                            Broadcast = 0
                            Busy = 1
                            Wide bus = 2
                            Turn CRC = 3 (Only for SPI)
                            NOB EN = 4
                            Init = 5
                            Create CRC Error = 6
                            Last Perf Buf = 7
        SetMode - (bool)True/False
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "HostRegisterMode - %s, SetMode - %s" % (HostRegisterMode, SetMode))
        try:
            sdcmdWrap.SetSpecialModes(Mode = HostRegisterMode, val = SetMode)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SetSpecialModes failed with following error: %s" % exc.GetFailureDescription())
            raise ValidationError.TestFailError(self.fn, "SetSpecialModes failed with following error: %s" % exc.GetFailureDescription())


    def CMD56_SDDeviceHealthStatus(self, Rd_Wr, stuffbits = 0, NoData = False, Buff = None, BlockLength = 512, Pattern = 0xFFFFFFFE):
        """
        CMD56 - GEN_CMD
        Rd_Wr: True - Read / False - Write
        """
        if Buff == None:
            Buff = ServiceWrap.Buffer.CreateBuffer(1, patternType = 0x0, isSector = True)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD56 : Rd_Wr - %s, NoData - %s, BlockLength - %s, Pattern - %s"
                     % (Rd_Wr, NoData, BlockLength, Pattern))

        try:
            CMD56 = sdcmdWrap.GenCmd(uiRd_Wr = Rd_Wr, uistuffbits = stuffbits,
                                     bNoData = NoData, szBuffer = Buff,
                                     blockLength = BlockLength, uiPattern = Pattern)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.__sdCmdObj.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD56.pyResponseData.r1Response.uiCardStatus))

        return CMD56


    def setCardDetect(self, Set = 1):
        '''
        ACMD42
        # Set = 1 for Set
        # Set = 0 for clear
        # 1: Connect, 0: Disconnect the resistor on CD/DAT3 (pin 1) of the card.
        '''
        self.__sdCmdObj.Cmd55()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "setCardDetect called with Set - %s" % Set)
        try:
            ACMD42 = sdcmdWrap.SetClrCardDetect(uiSetCd = Set)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SetCardDetect Failed")
            self.__sdCmdObj.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(ACMD42.pyResponseData.r1Response.uiCardStatus))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "setCardDetect Completed\n")
        return ACMD42


    def initCard(self):
        """
        Name :           initCard
        Description :    Use CVF API and does default intilization
        Returns :        None
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Initialize the card")
        try:
            sdcmdWrap.WrapSDCardInit()      # After card init, card will be in stby mode
            RCA = sdcmdWrap.WrapGetRCA()
            self.__sdCmdObj.SetrelativeCardAddress(RCA)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "completed intilization of card\n")
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Default intilization failed")
            self.Exception_Details(exc)


###----------------------------- Card Secure Area Functions Start -----------------------------###
    def CardToSecureMode(self, cardslot, BlockCount, StartBlock, selector, ReadMKB, ReadMID):
        """
        Description :   Put the card into secure mode. Secure mode state can be known from SD status register.
        Returns :       None
        Parameter description :
            [int] cardSlot- card number, 1-16
            [int] blockCount - 0-255 (where 0=256)
            [int] startSector - start address
            [int] selector - MKB number
            [CTFBuffer] DKNumFileBuffer - Buffer
            [bool] getMKB - True/False
            [bool] getMID - True/False
        """

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card to secure mode using authentication")
        try:
            dkBufFilePath = os.path.join(os.getenv('SANDISK_CTF_HOME_X64'), "Security\\DK_num.bin")
            dkFileBuf = ServiceWrap.Buffer.CreateBufferFromFile(dkBufFilePath)

            cmdObj = sdcmdWrap.CardAuthenticateKey(cardSlot = cardslot, blockCount = BlockCount, startSector = StartBlock,
                                                   selector = selector, DKNumFileBuffer = dkFileBuf,
                                                   getMKB = ReadMKB, getMID = ReadMID)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card is in Secure mode\n")
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed to move the card to Secure Mode for StartBlock:0x%X, BlockCount:0x%X, Selector 0x%X"
                                % (StartBlock, BlockCount, selector))
            self.Exception_Details(exc)


    def SecureWrite(self, cardslot, StartBlock, BlockCount, writeDataBuffer, selectorValue, enableSignature,
                    authentication, StrDKFile = "", Pattern = 0, allowAPIhandle = False):
        """
        Description :   Does secure write to the card. For more information refer SD security spec.
        Returns :       None
        Parameter description : [int] cardSlot - card number, 1-16
                                [int] blockCount - 0-255 (where 0 = 256)
                                [int] startLba - start address
                                [CTFBuffer] pBufObj - user data
                                [int] selector - MKB number
                                enable_signature - write the data with signature
                                [bool] authenticate - do authentication or not
                                [string] strDKFile - Device Key file:
                                    a) empty string to use default file(DK_num.bin)
                                    b) full file path
                                    c) file name only (the default path will be used)
                                    d) file path only (the default file name will be used)
                                [int] Pattern - If writeDataBuffer is None, Pattern should be given otherwise pattern will be all zero's
        """

        StartAddress = StartBlock
        EndAddress = self.__sdCmdObj.calculate_endLba(StartBlock, BlockCount)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Secure Write to the card from StartAddress:0x%X to EndAddress:0x%X with Selector 0x%X"
                    % (StartAddress, EndAddress, selectorValue))
        try:
            if allowAPIhandle == False:
                ACMD25 = sdcmdWrap.SecureWrite(cardSlot = cardslot, blockCount = BlockCount, startLba = StartBlock,
                                            pBufObj = writeDataBuffer, selector = selectorValue,
                                            enable_signature = enableSignature, authenticate = authentication,
                                            strDKFile = StrDKFile)
            else:
                for StartBlock, BlockCount in self.__sdCmdObj.Data_Trans_Breakup(StartAddress, EndAddress, self.__maxblockforsecureop):
                    ACMD25 = sdcmdWrap.SecureWrite(cardSlot = cardslot, blockCount = BlockCount, startLba = StartBlock,
                                                pBufObj = writeDataBuffer, selector = selectorValue,
                                                enable_signature = enableSignature, authenticate = authentication,
                                                strDKFile = StrDKFile)

        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Secure Write Failed with StartBlock:0x%X, BlockCount:0x%X, Selector 0x%X"
                                % (StartBlock, BlockCount, selectorValue))
            self.Exception_Details(exc)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Secure Write to the card from StartAddress:0x%X to EndAddress:0x%X with Selector 0x%X\n"
                           % (StartAddress, EndAddress, selectorValue))


    #def SecureWrite_ProtectedArea_Breakup(self, ProtectedArea, cardslot = 0x1, StartBlock = 0x0, BlockCount = 0x80, Pattern = 0,
                                          #Selector = 0x0, Signature = False, authentication = True, StrDKFile = ""):
        #"""
        #Description : Write secure area (ProtectedArea) with the given BlockCount interval. Refer SecureWrite function to
                      #know more about description of above parameters.
        #"""
        #ProtectedAreaEndAddress = StartBlock + ProtectedArea - 1

        #writeDataBuffer = ServiceWrap.Buffer.CreateBuffer(BlockCount)
        #writeDataBuffer = self.__sdCmdObj.BufferFilling(writeDataBuffer, Pattern = Pattern)

        #for startBlock, blockCount in self.__sdCmdObj.Data_Trans_Breakup(StartBlock, ProtectedAreaEndAddress, BlockCount):
            #self.SecureWrite(cardslot = cardslot, StartBlock = startBlock, BlockCount = blockCount,
                             #writeDataBuffer = writeDataBuffer, Selector = Selector,
                             #Signature = Signature, authentication = authentication, StrDKFile = StrDKFile)

        # Below while loop logic was used in early implementation.
        #while(True):
            #CurrentWriteEndAddress = StartBlock + BlockCount - 1
            #if CurrentWriteEndAddress <= ProtectedAreaEndAddress:

                #writeDataBuffer = ServiceWrap.Buffer.CreateBuffer(BlockCount)
                #writeDataBuffer = self.__sdCmdObj.BufferFilling(writeDataBuffer, Pattern = Pattern)

                #self.SecureWrite(cardslot = cardslot, StartBlock = StartBlock, BlockCount = BlockCount,
                                    #writeDataBuffer = writeDataBuffer, Selector = Selector,
                                    #Signature = Signature, authentication = authentication)
            #else:
                #BlockCount = ProtectedAreaEndAddress - StartBlock + 1
                #if BlockCount > 0:
                    #writeDataBuffer = ServiceWrap.Buffer.CreateBuffer(BlockCount)
                    #writeDataBuffer = self.__sdCmdObj.BufferFilling(writeDataBuffer, Pattern = Pattern)

                    #self.SecureWrite(cardslot = cardslot, StartBlock = StartBlock, BlockCount = BlockCount,
                                                #writeDataBuffer = writeDataBuffer, Selector = Selector,
                                                #Signature = Signature, authentication = authentication)
                #break
            #StartBlock = StartBlock + BlockCount


    def SecureRead(self, cardslot, StartBlock, BlockCount, ExpectedDataBuffer, selectorValue, authentication,
                   StrDKFile = "", verify = True, Pattern = 0, allowAPIhandle = False):
        """
        Description :   Does secure read from the card. For more information refer SD security spec.
                        Verify read data to the expected buffer and logs appropriate details.
        Returns :       None
        Parameter description : [int] cardSlot - card number, 1-16
                                [int] blockCount - 0-255 (where 0 = 256)
                                [int] startLba - start address
                                [CTFBuffer] pBufObj - user data
                                [int] selector - MKB number
                                [bool] authenticate - do authentication or not
                                [string] strDKFile - Device Key file:
                                    a) empty string to use default file(DK_num.bin)
                                    b) full file path
                                    c) file name only (the default path will be used)
                                    d) file path only (the default file name will be used)
                                [int] Pattern - If ExpectedDataBuffer is None, Pattern should be given otherwise pattern will be all zero's
        """

        StartAddress = StartBlock
        EndAddress = self.__sdCmdObj.calculate_endLba(StartBlock, BlockCount)

        ReadDataBuffer = ServiceWrap.Buffer.CreateBuffer(self.__maxblockforsecureop, patternType = 0x00)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Secure Read to the card from StartAddress:0x%X to EndAddress:0x%X with Selector 0x%X"
                           % (StartAddress, EndAddress, selectorValue))

        def VerifyRead(StartBlock, BlockCount):
            if verify == True:
                value = ExpectedDataBuffer.Compare(srcBuf = ReadDataBuffer, thisOffset = 0, srcOffset = 0, count = self.__maxblockforsecureop)
                if value != 0:
                    self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "***** Data Miscompare error has occured on StartBlock:0x%X, BlockCount:0x%X, Selector: 0x%X"
                                % (StartBlock, BlockCount, selectorValue))
                    raise ValidationError.TestFailError(self.fn, "Secure read failed with miscompare error")
                else:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Secure Read & verify with StartBlock:0x%X, BlockCount:0x%X, Selector: 0x%X"
                                % (StartBlock, BlockCount, selectorValue))
        try:
            if allowAPIhandle == False:
                ACMD18 = sdcmdWrap.SecureRead(cardSlot = cardslot, blockCount = BlockCount, startLba = StartBlock,
                                            pBufObj = ReadDataBuffer, selector = selectorValue,
                                            authenticate = authentication, strDKFile = StrDKFile)
                VerifyRead(StartBlock, BlockCount)
            else:
                for StartBlock, BlockCount in self.__sdCmdObj.Data_Trans_Breakup(StartAddress, EndAddress, self.__maxblockforsecureop):
                    ACMD18 = sdcmdWrap.SecureRead(cardSlot = cardslot, blockCount = BlockCount, startLba = StartBlock,
                                                pBufObj = ReadDataBuffer, selector = selectorValue,
                                                authenticate = authentication, strDKFile = StrDKFile)
                    VerifyRead(StartBlock, BlockCount)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Secure Read Failed with StartBlock:0x%X, BlockCount:0x%X, Selector 0x%X"
                                % (StartBlock, BlockCount, selectorValue))
            self.Exception_Details(exc)


    #def SecureRead_ProtectedArea_Breakup(self, ProtectedArea, cardslot = 0x1, StartBlock = 0x0, BlockCount = 0x80, Pattern = 0,
                    #Selector = 0x0, authentication = True, StrDKFile = "", verify = True):
        #"""
        #Description : Read secure area (ProtectedArea) with the given BlockCount interval. Refer SecureRead function to
                      #know more about description of above parameters.
        #"""
        #ProtectedAreaEndAddress = StartBlock + ProtectedArea - 1

        #ExpectedDataBuffer = ServiceWrap.Buffer.CreateBuffer(BlockCount)
        #ExpectedDataBuffer = self.__sdCmdObj.BufferFilling(ExpectedDataBuffer, Pattern = Pattern)

        #for startBlock, blockCount in self.__sdCmdObj.Data_Trans_Breakup(StartBlock, ProtectedAreaEndAddress, BlockCount):
            #self.SecureRead(cardslot = cardslot, StartBlock = startBlock, BlockCount = blockCount,
                            #ExpectedDataBuffer = ExpectedDataBuffer, Selector = Selector,
                            #authentication = authentication, StrDKFile = StrDKFile, verify = verify)

        # Below while loop logic was used in early implementation.
        #while(True):
            #CurrentWriteEndAddress = StartBlock + BlockCount - 1
            #if CurrentWriteEndAddress <= ProtectedAreaEndAddress:

                #ExpectedDataBuffer = ServiceWrap.Buffer.CreateBuffer(BlockCount)
                #ExpectedDataBuffer = self.__sdCmdObj.BufferFilling(ExpectedDataBuffer, Pattern = Pattern)

                #self.SecureRead(cardslot = cardslot, StartBlock = StartBlock, BlockCount = BlockCount,
                                #ExpectedDataBuffer = ExpectedDataBuffer, Selector = Selector, authentication = authentication)
            #else:
                #BlockCount = ProtectedAreaEndAddress - StartBlock + 1
                #if BlockCount > 0:
                    #ExpectedDataBuffer = ServiceWrap.Buffer.CreateBuffer(BlockCount)
                    #ExpectedDataBuffer = self.__sdCmdObj.BufferFilling(ExpectedDataBuffer, Pattern = Pattern)

                    #self.SecureRead(cardslot = cardslot, StartBlock = StartBlock, BlockCount = BlockCount,
                                                #ExpectedDataBuffer = ExpectedDataBuffer, Selector = Selector, authentication = authentication)
                #break
            #StartBlock = StartBlock + BlockCount


    def SecureErase(self, cardslot, StartBlock, BlockCount, selectorValue, authentication, StrDKFile = "", allowAPIhandle = False):
        """
        Description :   Does secure erase on card. For more information refer SD security spec.
        Returns :       None
        Parameters description : [int] cardSlot - card number, 1-16
                                 [int] blockCount - 0-255 (where 0 = 256)
                                 [int] startLba - start address
                                 [int] selector - MKB number
                                 [bool] authenticate - do authentication or not
                                 [string] strDKFile - Device Key file:
                                 a) empty string to use default file(DK_num.bin)
                                 b) full file path
                                 c) file name only (the default path will be used)
                                 d) file path only (the default file name will be used)
        """

        StartAddress = StartBlock
        EndAddress = self.__sdCmdObj.calculate_endLba(StartBlock, BlockCount)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Secure Erase to the card with StartBlock:0x%X, BlockCount:0x%X, Selector 0x%X"
                           % (StartBlock, BlockCount, selectorValue))
        try:
            if allowAPIhandle == False:
                ACMD38 = sdcmdWrap.SecureErase(cardSlot = cardslot, blockCount = BlockCount, startLba = StartBlock,
                                                selector = selectorValue, authenticate = authentication, strDKFile = StrDKFile)
            else:
                for StartBlock, BlockCount in self.__sdCmdObj.Data_Trans_Breakup(StartAddress, EndAddress, self.__maxblockforsecureop):
                    ACMD38 = sdcmdWrap.SecureErase(cardSlot = cardslot, blockCount = BlockCount, startLba = StartBlock,
                                                    selector = selectorValue, authenticate = authentication, strDKFile = StrDKFile)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Secure Erase Failed with StartBlock:0x%X, BlockCount:0x%X, Selector 0x%X"
                                % (StartBlock, BlockCount, selectorValue))
            self.Exception_Details(exc)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Secure Erase to the card with StartBlock:0x%X, BlockCount:0x%X, Selector 0x%X"
                           % (StartBlock, BlockCount, selectorValue))


    def ChangeSecureArea(self, CardSlot, StartBlock, Selector, Buffer, Authenticate):
        """
        ChangeSecureArea (ACMD49, CHANGE_SECURE_AREA) - Refer SD Spec Part 3 Security Specification.
        Parameters description:
            [int] cardSlot - card number, 1-16
            [int] startLba - start address
            [int] selector - MKB number
            [CTF Buffer] optionalData - Buffer
            [bool] authenticate - do authentication or not
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CardSlot - %s, StartBlock - %s, Selector - %s, Authenticate - %s"
                              % (CardSlot, StartBlock, Selector, Authenticate))
        try:
            sdcmdWrap.CardChangeSecureArea(cardSlot = CardSlot, startLba = StartBlock, selector = Selector,
                                           optionalData = Buffer, authenticate = Authenticate)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.__sdCmdObj.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())


    def WriteProductionFile(self, MaxLba = 0, FilePath = ""):
        """
        Parameters description:
            [int] maxLba - The maximum LBA index, default value is 0(CVF internally calculates).
            [string] FilePath - Full file name, default value is empty string.
                a) empty string to use default file
                b) full file path
                c) file name only (the default path will be used)
                d) file path only (the default file name will be used)
        """
        path = "Default file will be used" if FilePath == "" else FilePath
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "MaxLba - %s, FilePath - %s." % (MaxLba, path))
        try:
            sdcmdWrap.WriteProductionFile(maxLba = MaxLba, filePath = FilePath)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.__sdCmdObj.ErrorPrint(exc)
            raise ValidationError.TestFailError(self.fn, exc.GetFailureDescription())


    def WriteHiddenSystemFile(self, FilePath = ""):
        """
        Parameters description:
            [string] FilePath - Full file name, default value is empty string.
                a) empty string to use default file(Km.bin)
                b) full file path
                c) file name only (the default path will be used)
                d) file path only (the default file name will be used)
        """
        path = "Default file will be used" if FilePath == "" else FilePath
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FilePath - %s." % path)
        try:
            sdcmdWrap.WriteHIddenSystemFile(filePath = FilePath)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.__sdCmdObj.ErrorPrint(exc)
            raise ValidationError.TestFailError(self.fn, exc.GetFailureDescription())


    def WriteMKBUsingFilenames(self, cardSlot, blockCount, selector, MKBFile = "", DKFile = "", authenticate = False):
        """
        Description: This function write the MKB file based on selector and MKBFile argument - Refer SD Spec Part 3 Security Specification.
        Parameters description:
            [int] cardSlot - card number, 1-16
            [int] blockCount - Number of blocks, 0 - 255 (where 0 = 256)
            [int] selector - MKB number
            [bool] authentication - do authentication or not
            [string] MKBFile - Complete path for the MKB bin file
            [string] DKFile - Complete path for the device key file
        """
        self.__sdCmdObj.Cmd55()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Write MKB - BlockCount: %d, Selector: %d, MKB file: %s" % (blockCount, selector, MKBFile))

        try:
            sdcmdWrap.WriteMKBUsingFilenames(cardSlot = cardSlot, blockCount = blockCount, selector = selector, authenticate = authenticate, strMKBFile = MKBFile, strDKFile = DKFile)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "WriteMKBUsingFilenames failed for BlockCount: %d, Selector: %d, MKB file: %s"
                        % (blockCount, selector, MKBFile))
            self.__sdCmdObj.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())


    def WriteMKB(self, selector = 0, MKBFileorPath = ""):
        """
        WriteMKB (ACMD26, SECURE_WRITE_MKB) - Refer SD Spec Part 3 Security Specification.
        Parameters description:
            [int] selector - MKB number : {0-15}
            [string] MKBFileorPath - Full file name ('Mkb_#0.bin', 'Mkb_#1.bin' ... 'Mkb_#15.bin')
                a) empty string to use default file
                b) full file path
                c) file name only (the default path will be used)
                d) file path only (the default file name will be used)
        If user doesn't pass the MKBFileOrPath, CVF internally chooses MKB files(in security folder) to be written.
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %d" % ('Writing MKB file', selector))

        try:
            if MKBFileorPath == "":
                sdcmdWrap.WriteMKB(selector = selector) # User should not pass empty string to the API.
            else:
                sdcmdWrap.WriteMKB(selector = selector, MKBFileorPath = MKBFileorPath)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "WriteMKB failed when writing file No.%d" % selector)
            self.__sdCmdObj.ErrorPrint(exc)
            raise ValidationError.TestFailError(self.fn, exc.GetFailureDescription())


    def ReadMKBFile(self, cardslot, BlockCount, StartBlock, selector):
        """
        ReadMKBFile (ACMD43, GET_MKB) - Refer SD Spec Part 3 Security Specification.
        Description : This function read the MKB files based on selector.
        Parameters description :
            [int] cardSlot- card number, 1-16
            [CTFBuffer] pBufObj - user data
            [int] startLba - start address
            [int] blockCount - 0-255 (where 0 = 256)
            [int] selector - MKB number
        """
        self.__sdCmdObj.Cmd55()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Read MKB file at StartBlock: 0x%X to BlockCount: 0x%X with selector: 0x%X"
                              % (StartBlock, BlockCount, selector))
        try:
            mkbBuffer = ServiceWrap.Buffer.CreateBuffer(BlockCount, patternType = 0x00)
            sdcmdWrap.CardGetMKB(cardSlot = cardslot, pBufObj = mkbBuffer, startLba = StartBlock,
                                 blockCount = BlockCount, selector = selector)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Read MKB file failed at StartBlock: 0x%X to BlockCount: 0x%X with selector: 0x%X"
                                  % (StartBlock, BlockCount, selector))
            self.__sdCmdObj.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())


    def WriteSecurityKeys(self):
        """
        Description:   This function writes the security keys again because any previous diagnostic command would have erased.
                       This function is called before issuing SecureWrite(ACMD25), SecureRead(ACMD18), CardSecureErase(ACMD38),
                       WriteMKB(ACMD26), CardGetMKB(ACMD43) CVF APIs.
        Returns:       None
        """
        if self.__WriteSecurityKeysDownloaded == True:
            return 0

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, r"Default parameter file from path 'C:\Program Files (x86)\SanDisk\CVF_(current version)\Security' is used")

        self.WriteProductionFile(MaxLba = self.__cardMaxLba)
        self.WriteHiddenSystemFile()

        self.__sdCmdObj.SecureFormatProcess()

        for i in range(gvar.GlobalConstants.MKB_FILEnumO, gvar.GlobalConstants.MKB_FILEnum16):
            self.WriteMKB(selector = i)    # SECURE_WRITE_MKB

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed writing SecurityKeys")

        sdcmdWrap.SDRPowerCycle()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed PowerCycle")

        sdcmdWrap.WrapSDRSystemInit()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed SDRSystemInit")

        sdcmdWrap.WrapSDCardInit()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed SDCardInit")
        self.__WriteSecurityKeysDownloaded = True

###----------------------------- Card Secure Area Functions End -----------------------------###

###----------------------------- LockUnLock Specific Functions Start -----------------------------###

    def Lock_unlock(self, setPassword = False, clearPassword = False, lock = False, erase = False, cop = False,
                    reservedBitsR1ToR3 = [0, 0, 0], additionalPassLen = 0, oldPassword = "", newPassword = "",
                    blockLength = 0x200):
        """
        Description:       Does set password, clear password, Lock unlock and erase operations on card.
                           Note this API allows to modify the block length(Send CMD16 based on the argument blockLength).
                           cop       : Card Ownership Protection
                           lock      : 1 - Locks the card / 0 - Unlocks the card
                           erase     : 1 - Erase the card / 0 - Not Erase
        Returns: None
        """

        status = self.__sdCmdObj.GetCardStatus()
        if status.count("CURRENT_STATE:Tran") != 1:
            self.__sdCmdObj.Cmd7()      # Added to get the card to tran state

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "setPassword:%d, clearPassword:%d, lock:%d, erase:%d, cop:%d, reservedBitsR1ToR3:%s, additionalPassLen: %d, oldPassword:%s, newPassword: %s, blockLength: %s\n"
                    % (setPassword,clearPassword,lock,erase,cop,reservedBitsR1ToR3,additionalPassLen,oldPassword,newPassword,blockLength))

        buffForCardLock = ServiceWrap.Buffer.CreateBuffer(blockLength, 0x00, isSector=False)
        firstbyte = 0
        if(setPassword ==1):
            firstbyte = 1     #to set first bit i.e set password
        if(clearPassword == 1):
            firstbyte = firstbyte + 2  #to set second bit i.e clear password
        if(lock == 1):
            firstbyte = firstbyte + 4  #to set third bit i.e lock
        if(erase == 1):
            firstbyte = firstbyte + 8  #to set fourth bit i.e erase
        if(cop == 1):
            firstbyte = firstbyte + 16  #to set fifth bit i.e cop
        if(reservedBitsR1ToR3[0] == 1):
            firstbyte = firstbyte + 32 #Reserve 2 bit
        if(reservedBitsR1ToR3[1] == 1):
            firstbyte = firstbyte + 64  #Reserve 3 bit
        if(reservedBitsR1ToR3[2] == 1):
            firstbyte = firstbyte + 128  #Reserve 4 bit

        buffForCardLock.SetByte(0,firstbyte)   # set first byte
        Password = str(oldPassword) + str(newPassword)
        BufferSizeNeeded = (len(Password) + 2)  # 2 is first 2 bytes

        if (blockLength >= 0x2):
            if additionalPassLen == 0:
                buffForCardLock.SetByte(1,len(Password)) # set second byte
            else:
                buffForCardLock.SetByte(1,additionalPassLen)  # set the additional password length in second byte

        if (blockLength > 0x2):
            if blockLength >= BufferSizeNeeded:
                buffForCardLock.SetRawStringChar(offset = 2, value = Password, strLen = len(Password), little_endian = True) # Set from third byte
            elif blockLength < BufferSizeNeeded:
                PasswordToSet = Password[:(blockLength - 2)]
                buffForCardLock.SetRawStringChar(offset = 2, value = PasswordToSet, strLen = len(PasswordToSet), little_endian = True)    # Set from third byte
        #buffForCardLock.PrintToLog()

        try:
            if blockLength < 0x200:     # for block count less than 0x200(512 LBA)
                self.__sdCmdObj.Cmd16(blockLength)

            self.__sdCmdObj.Cmd42(buffForCardLock, blockLength)
            #self.__ErrorManager.RegisterContinueOnException(ServiceWrap.CTF_CMD_ID_SD_SEND_TASK_STATUS, sdcmdWrap.STATUS_CODE_CARD_IS_LOCKED_S_X, 0xFF3A, False)
            status = self.__sdCmdObj.GetCardStatus()
            #self.__ErrorManager.DeRegisterContinueOnException(ServiceWrap.CTF_CMD_ID_SD_SEND_TASK_STATUS, sdcmdWrap.STATUS_CODE_CARD_IS_LOCKED_S_X, 0xFF3A, False)

            if blockLength < 0x200:             # check the condition for block count less than 0x200
                self.__sdCmdObj.Cmd16(0x200)    # restore block length to default value

        except ValidationError.CVFGenericExceptions as exc:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Lock unlock operation failed")
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetInternalErrorMessage())
        return status

    #def Lock_unlock(self, setPassword = False, clearPassword = False, lock = False, erase = False, cop = False,
                    #reservedBitsR1ToR3 = [0, 0, 0], additionalPassLen = 0, oldPassword = "", newPassword = "",
                    #blockLength = 0x200, SkipCMD13 = True):
        #"""
        #Description:       Does set password, clear password, Lock unlock and erase operations on card.
                           #Note this API allows to modify the block length(Send CMD16 based on the argument blockLength).
                           #cop       : Card Ownership Protection
                           #lock      : 1 - Locks the card / 0 - Unlocks the card
                           #erase     : 1 - Erase the card / 0 - Not Erase
                           #SkipCMD13 : 1 - CMD13 will be sent after CMD42 / 0 - CMD13 will not be sent after CMD42
        #Returns: None
        #"""

        #status = self.__sdCmdObj.GetCardStatus()
        #if status.count("CURRENT_STATE:Tran") != 1:
            #self.__sdCmdObj.Cmd7()      # Added to get the card to tran state

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "setPassword:%d, clearPassword:%d, lock:%d, erase:%d, cop:%d, reservedBitsR1ToR3:%s, additionalPassLen: %d, oldPassword:%s, newPassword: %s, blockLength: %s\n"
                    #% (setPassword,clearPassword,lock,erase,cop,reservedBitsR1ToR3,additionalPassLen,oldPassword,newPassword,blockLength))

        #lockCardDSbyte0 = sdcmdWrap.LOCK_CARD_DATA_STRUCTURE_BYTE0()
        #lockCardDSbyte0.uiSet_Pwd = setPassword
        #lockCardDSbyte0.uiClr_Pwd = clearPassword
        #lockCardDSbyte0.uiLock_Unlock = lock
        #lockCardDSbyte0.uiErase = erase
        #lockCardDSbyte0.uiCop = cop
        #lockCardDSbyte0.ui8Rsv5, lockCardDSbyte0.ui8Rsv6, lockCardDSbyte0.ui8Rsv7 = reservedBitsR1ToR3

        #LockCardDataStruct = sdcmdWrap.LOCK_CARD_DATA_STRUCTURE()
        #LockCardDataStruct.lockCardDataStructureByte0 = lockCardDSbyte0        # set first byte

        #Password = oldPassword + newPassword
        #BufferSizeNeeded = (len(Password) + 2) # 2 is first 2 bytes

        #if (blockLength >= 0x2):
            #if additionalPassLen == 0:
                #LockCardDataStruct.uiPWDS_LEN = len(Password)      # set second byte
            #else:
                #LockCardDataStruct.uiPWDS_LEN = additionalPassLen   # set the additional password length in second byte

        #if blockLength >= BufferSizeNeeded:
            #LockCardDataStruct.uiPasswordData = [char for char in (Password)]
        #elif blockLength < BufferSizeNeeded:
            #LockCardDataStruct.uiPasswordData = [char for char in (Password[:-(BufferSizeNeeded - blockLength)])]

        #try:
            #if blockLength < 0x200:     # for block count less than 0x200(512 Lba)
                #self.__sdCmdObj.Cmd16(blockLength)

            #CMD42 = self.__sdCmdObj.Cmd42(LockCardDataStructure = LockCardDataStruct, SkipCMD13 = SkipCMD13)
            #status = self.__sdCmdObj.GetCardStatus()

            #if blockLength < 0x200:             # check the condition for block count less than 0x200
                #self.__sdCmdObj.Cmd16(0x200)    # restore block length to default value

        #except ValidationError.CVFGenericExceptions as exc:
            #self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Lock unlock operation failed")
            #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetInternalErrorMessage())
        #return CMD42

    def CardStatus_Check(self, Expected_Status, Pass_case, Fail_case):
        """
        Expected_Status : Expected_Status must be dictionary.
                          Key   : Key must be string and one of Card_Status_Fields(Check GlobalConstants.py file) values.
                          Value : 1 - Check whether 'Key' is enabled or not in card status. If not raise exception
                                  0 - Check whether 'Key' is disabled or not in card status. If not raise exception
        """
        assert type(Expected_Status) == dict
        cardStatus = self.__sdCmdObj.GetCardStatus()

        if all([cardStatus.count(card_status) == enabled for (card_status, enabled) in list(Expected_Status.items())]):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, Pass_case)
        else:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, Fail_case)
            raise ValidationError.TestFailError(self.fn, Fail_case)


    def Check_Card_LockUnlock_Status(self, Lock):
        """
        Lock : 1 - confirm card is locked. If card is not locked then raise exception.
               0 - confirm card is not locked. If card is locked then raise exception.
        """
        Pass_case = "Card is %s\n" % ("locked" if Lock == 1 else "not locked")
        Fail_case = "Card is %s\n" % ("not locked" if Lock == 1 else "locked")
        self.CardStatus_Check({gvar.Card_Status_Fields.CARD_IS_LOCKED : Lock}, Pass_case, Fail_case)


    def Check_Card_Trans_State(self, Trans):
        """
        Trans : 1 - confirm card is in trans state. If card is not in trans state then raise exception.
                0 - confirm card is not in trans state. If card is in trans state then raise exception.
        """
        Pass_case = "Card is %s trans state\n" % ("in" if Trans == 1 else "not in")
        Fail_case = "Card is %s trans state\n" % ("not in" if Trans == 1 else "in")
        self.CardStatus_Check({gvar.Card_Status_Fields.CURRENT_STATE_Tran : Trans}, Pass_case, Fail_case)


    def Check_Trans_Locked(self):
        """
        Description : Check card is in transfer state and is locked. If not raise exception.
        """
        Pass_case = "Card is in tran state and is locked\n"
        Fail_case = "Card is not in tran state or is not locked"
        self.CardStatus_Check({gvar.Card_Status_Fields.CURRENT_STATE_Tran: 1, gvar.Card_Status_Fields.READY_FOR_DATA: 1,
                               gvar.Card_Status_Fields.CARD_IS_LOCKED : 1}, Pass_case, Fail_case)


    def Check_Trans_NotLocked(self):
        """
        Description : Check card is in transfer state and is not locked. If not raise exception.
        """
        Pass_case = "Card is in trans state and is not locked\n"
        Fail_case = "Card is not in trans state or is locked"
        self.CardStatus_Check({gvar.Card_Status_Fields.CURRENT_STATE_Tran : 1, gvar.Card_Status_Fields.READY_FOR_DATA: 1,
                               gvar.Card_Status_Fields.CARD_IS_LOCKED : 0}, Pass_case, Fail_case)

    def Check_Stby_Locked(self):
        """
        Description : Check card is in standby state and is locked. If not raise exception.
        """
        Pass_case = "Card is in Stby state and is Locked\n"
        Fail_case = "Card is not locked or not in Stby state"
        self.CardStatus_Check({gvar.Card_Status_Fields.CURRENT_STATE_Stby: 1, gvar.Card_Status_Fields.CARD_IS_LOCKED : 1}, Pass_case, Fail_case)

    def Check_ReadyForData_Locked(self):
        """
        Description : Check card is ready for data and is locked. If not raise exception.
        """
        Pass_case = "Card is ready for data and is locked\n"
        Fail_case = "Card is not ready for data or is not locked"
        self.CardStatus_Check({gvar.Card_Status_Fields.READY_FOR_DATA: 1, gvar.Card_Status_Fields.CARD_IS_LOCKED : 1}, Pass_case, Fail_case)

    def Check_ReadyForData_NotLocked(self):
        """
        Description : Check card is ready for data and is not locked. If not raise exception.
        """
        Pass_case = "Card is ready for data and is not locked\n"
        Fail_case = "Card is not ready for data or is locked"
        self.CardStatus_Check({gvar.Card_Status_Fields.READY_FOR_DATA: 1, gvar.Card_Status_Fields.CARD_IS_LOCKED : 0}, Pass_case, Fail_case)

    def Lock_Unlock_Failure_Check(self, exc):
        """
        Description : Check expected LockUnlock failure occured or not. if not raise exception.
        exc         : Exception captured from ValidationError.CVFGenericExceptions
        """
        errstring = exc.GetInternalErrorMessage()
        if (errstring.find('CARD_LOCK_UNLOCK_FAILED') != -1) or (errstring.find('LOCK_UNLOCK_FAILED') != -1):
            self.vtfContainer.CleanPendingExceptions()  # Clear expected LOCK_UNLOCK_FAILED error to prevent script failure
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Expected failure LOCK_UNLOCK_FAILED occured\n")
        else:
            raise ValidationError.TestFailError(self.fn, "Expected error is LOCK_UNLOCK_FAILED. Error occurred is: %s" % errstring)

###----------------------------- LockUnLock Specific Functions End -----------------------------###

    def Expected_Failure_Check(self, exc, Expected_Exception, Operation_Name):
        """
        Expected_Exception : Check whether expected exception occured in the exc get from ValidationError.CVFGenericExceptions
                             or not. If not, raise exception.
        Operation_Name     : Name of the API or function calling this function.
        """
        if hasattr(exc, "GetFailureDescription"):
            errstring = exc.GetFailureDescription()
        elif hasattr(exc, "GetInternalErrorMessage"):
            errstring = exc.GetInternalErrorMessage()
        else:
            if hasattr(exc, "message"):
                errstring = exc.message
            elif hasattr(exc, "msg"):
                errstring = exc.msg
            raise ValidationError.TestFailError(self.fn, "General python error occurred other than CVF error. Python error is - %s" % errstring)

        if errstring.find(Expected_Exception) != -1:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_EXPECTED_ERROR_OCCURED(Expected_Exception, Operation_Name))
            self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure
            #self.__ErrorManager.ClearAllErrors()    # Old CVF API to clear errors occurred - JIRA RPG-54232
        else:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_ERROR_OCCURED_OTHER_THAN_EXPECTED_ERROR(Expected_Exception, Operation_Name, errstring))
            raise ValidationError.TestFailError(self.fn, self.STD_LOG_ERROR_OCCURED_OTHER_THAN_EXPECTED_ERROR(Expected_Exception, Operation_Name, errstring))


    #def Failure_Handle(self, Execute, Expected_Exception, Operation_Name):
        #try:
            #exec(Execute)
        #except ValidationError.CVFGenericExceptions as exc:
            #self.Expected_Failure_Check(exc, Expected_Exception, Operation_Name)
        #else:
            #raise ValidationError.TestFailError(self.fn, "Expected expection %s is not reported by card for %s" % (Expected_Exception, Operation_Name))


    def Write_Protection_Check(self, Enable = 0x1):
        """
        Enable      : "0x1" - To check enable / "0x0" - To check disable
        Description : Case 1: If Enable is 0x1, check whether both temporary and permanent write protection bits are enabled
                              in CSD register or not, if either one of or both temporary and permanent bits are disabled then
                              raise exception.
                      Case 2: If Enable is 0x0, check whether both temporary and permanent write protection bits are disabled
                              in CSD register or not, if either one of or both temporary and permanent bits are enabled then
                              raise exception.
        """
        Pass_case = "Temporary and Permanent write protection bits are %s\n" % ("set" if Enable == 0x1 else "disabled")
        Fail_case = "Either one of or both Temporary and Permanent write protection bits are \n" % ("not set" if Enable == 0x1 else "set")

        CSD__Reg_VALUES = self.__sdCmdObj.GET_CSD_VALUES()
        self.__sdCmdObj.Cmd7()
        if(CSD__Reg_VALUES[gvar.CSD.PERM_WRITE_PROTECT] == Enable and CSD__Reg_VALUES[gvar.CSD.TMP_WRITE_PROTECT] == Enable):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, Pass_case)
        else:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, Fail_case)
            raise ValidationError.TestFailError(self.fn, Fail_case)


    def CSD_Field_Check(self, CSD_Field, Value, CSD = None):
        """
        Description : Check whether the given 'Value' is set for the given CSD_Field or not, if it is not set then raise exception.
        Parameters Description:
            CSD_Field : "TAAC", "CCC", "C_SIZE", "PERM_WRITE_PROTECT", "TMP_WRITE_PROTECT", ......
            Value : "0x0", "0x1", "0x3", "0xF2", .......
            CSD : A list returned by the method self.__sdCmdObj.GET_CSD_VALUES().
        """
        Pass_case = "The value of CSD field %s is %s \n" % (CSD_Field, Value)
        Fail_case = "The value of CSD field %s is not %s \n" % (CSD_Field, Value)

        if CSD == None:
            CSD__Reg_VALUES = self.__sdCmdObj.GET_CSD_VALUES()
            if self.__sdCmdObj.SPIEnableStatus() != True:
                self.__sdCmdObj.Cmd7()  # In case of SD mode select the card.
        else:
            CSD__Reg_VALUES = CSD

        if(CSD__Reg_VALUES[CSD_Field] == Value):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, Pass_case)
        else:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, Fail_case)
            raise ValidationError.TestFailError(self.fn, Fail_case)


    def Enable_Perm_Disable_Temp_Write_Protection_Check(self):
        """
        Description : To confirm permanent write protection bit is enabled and temporary write protection bit is disabled.
                      If any one of or both temporary and permanent write protection bits are violate the expectation of the
                      function then raise exception.
        """
        CSD__Reg_VALUES = self.__sdCmdObj.GET_CSD_VALUES()
        self.__sdCmdObj.Cmd7()
        if (CSD__Reg_VALUES[gvar.CSD.PERM_WRITE_PROTECT] == 0x1) and (CSD__Reg_VALUES[gvar.CSD.TMP_WRITE_PROTECT] == 0x0):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Temporary write protection is disabled and Permanent write protection is enabled\n")
        else:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Temporary write protection is not disabled or Permanent write protection is not enabled\n")
            raise ValidationError.TestFailError(self.fn, "Temporary write protection is not disabled or Permanent write protection is not enabled\n")

    def Disable_Perm_Enable_Temp_Write_Protection_Check(self):
        """
        Description : To confirm permanent write protection bit is disabled and temporary write protection bit is enabled.
                      If any one of or both temporary and permanent write protection bits are violate the expectation of the
                      function then raise exception.
        """
        CSD__Reg_VALUES = self.__sdCmdObj.GET_CSD_VALUES()
        self.__sdCmdObj.Cmd7()
        if (CSD__Reg_VALUES[gvar.CSD.PERM_WRITE_PROTECT] == 0x0) and (CSD__Reg_VALUES[gvar.CSD.TMP_WRITE_PROTECT] == 0x1):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Permanent write protection bit is disabled and Temporary write protection bit is enabled\n")
        else:
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Permanent write protection is not disabled or Temporary write protection bit is not enabled\n")
            raise ValidationError.TestFailError(self.fn, "Permanent write protection is not disabled or Temporary write protection bit is not enabled\n")

    def setHighSpeed(self, HIGH_SPEED_MODE = None, CurrentLimit = None):
        """
        Description : Set card to HIGH_SPEED_MODE's
        Parameter : HIGH_SPEED_MODE - options from sdcmdWrap.HIGH_SPEED_MODE.SWITCH_HIGH_SPEED, sdcmdWrap.SD_CURRENT_LIMIT.CURRENT_NO_INFLUENCE
        Returns : None
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Set card to High Speed")
        if (HIGH_SPEED_MODE != None and CurrentLimit != None):
            try:
                sdcmdWrap.SetHighFrequency(setHighFreq = HIGH_SPEED_MODE, uhsCurrentLimit = CurrentLimit)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Completed Set card to High Speed")
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed to set Set card to High Speed")
                self.Exception_Details(exc)
        else:
            raise ValidationError.TestFailError(self.fn, "Inputs are missing")

    def setVolt(self, sdVolt, statusReg = 0, powerSupp = False):
        """
        SetVolt API for setting VDDF and VDDF voltage

        arguments:
            sdVolt : sdcmdWrap.SVoltage()
            statusReg = status
            powerSupp = True for VDDF(Flash) and False for VDDH(Host)
        Example :
            sdVolt = sdcmdWrap.SVoltage()
            sdVolt.voltage = 3300 # 3.30 V
            sdVolt.IO_voltage
            sdVolt.EnIOvoltage
            sdVolt.maxVoltage = 3800 # 3.8 V
            sdVolt.maxCurrent = 250  # 250 mA
            sdVolt.powerState
            sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_PARTIAL_1V8
            sdVolt.actualVoltage = 0
            sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ
            statusReg = 0
            bVddfValue = True
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Voltage=%s V, maxCurrent=%s, maxVoltage=%s V, A2DRate=%s Hz, PowerSupplier=%s"%(sdVolt.voltage,sdVolt.maxCurrent,sdVolt.maxVoltage,sdVolt.A2DOutrateType,powerSupp))

        try:
            GetSDRVol = sdcmdWrap.SDRSetVolt(voltStruct = sdVolt, pStatusReg = statusReg, bVddfValue = powerSupp)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.__sdCmdObj.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    def getVolt(self):
        try:
            GetSDRVol = sdcmdWrap.SDRGetVolt()
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.__sdCmdObj.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
        return GetSDRVol

    def SetVoltage(self, voltage = 3300):
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SetVoltage: Set to %.2f" % voltage)
        sdVolt = sdcmdWrap.SVoltage()
        if re.search('^\d\.\d*$', str(voltage)):
            sdVolt.voltage = int(voltage) * 1000
        elif re.search('^\d{4}$', str(voltage)):
            sdVolt.voltage = int(voltage)
        else:
            raise ValidationError.TestFailError(self.fn, "SetVoltage: Sd Voltage not in the range")

        sdVolt.maxVoltage = 3800 # 3.8 V
        sdVolt.maxCurrent = 250  # 250 mA
        sdVolt.regionSelect = sdcmdWrap.REGION_SELECT_PARTIAL_1V8
        sdVolt.actualVoltage = 0
        sdVolt.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_250_HZ

        self.setVolt(sdVolt = sdVolt, powerSupp = gvar.PowerSupply.VDDH)


    def SingleCommand(self, OPCode = 0, Argument = 0x1, ResponseType = sdcmdWrap.TYPE_RESP._R1, R1bTimeOut = 0, DataTransfer = sdcmdWrap.DATA_TRANS_.DATA_ABSENT):

        responseData = ServiceWrap.Buffer.CreateBuffer(0x1, patternType = 0x0, isSector = True)
        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = OPCode,
                                                           argument = Argument,
                                                           responseType = ResponseType,
                                                           responseData = responseData,
                                                           R1bTimeout = R1bTimeOut,
                                                           dataMode = DataTransfer)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            CMDObj = sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.__sdCmdObj.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        if ResponseType == sdcmdWrap.TYPE_RESP._R0:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD%d Passed with no response" % (OPCode))
        elif ResponseType == sdcmdWrap.TYPE_RESP._R1:
            response = self.__sdCmdObj.DecodeR1Response(responseData)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD%d Passed with R1 response:%s" % (OPCode, response))
        elif ResponseType == sdcmdWrap.TYPE_RESP._R2:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD%d Passed with R2 response:0x%X" % (OPCode, responseData.GetFourBytesToInt(offset = 1, little_endian = False)))
        elif ResponseType == sdcmdWrap.TYPE_RESP._R3:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD%d Passed with R3 response:0x%X" % (OPCode, responseData.GetFourBytesToInt(offset = 1, little_endian = False)))

        return CMDObj

    def SwitchVolt_CMD11(self, switchTo1_8v = True, timeToClockOff = 0, clockOffPeriod = 5):

        try:
            CMD11 = sdcmdWrap.VoltageSwitch(sdr_switchTo1_8 = switchTo1_8v,
                                            sdr_timeToClockOff = timeToClockOff,
                                            sdr_clockOffPeriod = clockOffPeriod)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Card-Status", CMD11.pyResponseData.r1Response.uiCardStatus))
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.__sdCmdObj.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "!!!!!! Sleeping 1 sec after CMD11")
        time.sleep(1)

        return CMD11

    def GetIdentifyDrive(self):
        # TOBEDONE: Decode the returned dataBuffer
        """
        # This method sends a SCTP Command 0xEC (Identify Device)
        # Param None
        # return dataBuffer
        # exception None
        """
        self.__sdCmdObj.FUNCTION_ENTRY("GetIdentifyDrive")
        dataBuffer = ServiceWrap.Buffer.CreateBuffer(dataSize = 8, patternType = ServiceWrap.ALL_0, isSector = True)

        diagCommand = ServiceWrap.DIAG_FBCC_CDB()
        diagCommand.cdb = [gvar.SCTPCOMMAND.IDENTIFYDRIVE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        diagCommand.cdbLen = gvar.SCTPCOMMAND.CDBLENGTH_16

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Sending IDENDIFY DRIVE CDB: %s" % diagCommand.cdb)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Buffer Size: %d Bytes" % dataBuffer.GetBufferSize())

        sctpCommand = ServiceWrap.SCTPCommand.SCTPCommand(fbcccdb = diagCommand, objBuffer = dataBuffer,
                                                          enDataDirection = ServiceWrap.DIRECTION_OUT)

        self.__sdCmdObj.FUNCTION_EXIT("GetIdentifyDrive")
        return dataBuffer

    def SingleRead_Exp_Hndl(self, StartLba, BlockCount, Pattern):
        for i in range(BlockCount):
            try:
                readDataBuffer = ServiceWrap.Buffer.CreateBuffer(1, patternType = Pattern)
                self.__sdCmdObj.Read(startLba = StartLba, transferLen = 0x1, readDataBuffer = readDataBuffer)
            except ValidationError.CVFGenericExceptions as exc:
                self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Single Read Failed for StartLba:0x%X, BlockCount:0x1" % StartLba)
                raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

            StartLba = StartLba + 1

    def ReadPort(self, option = 0x0004, address = 0, bytecount = 512):
        dataBuffer = ServiceWrap.Buffer.CreateBuffer(dataSize = bytecount, patternType = ServiceWrap.ALL_0, isSector = False)
        diagCommand = ServiceWrap.DIAG_FBCC_CDB()

        cdb = [141, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        cdb[0] = 141
        cdb[1] = 0
        cdb[2] = int((option & 0x00FF))
        cdb[3] = int((option & 0xFF00) >> 8)
        cdb[4] = int((address & 0xFF000000) >> 24)
        cdb[5] = int((address & 0x00FF0000) >> 16)
        cdb[6] = int((address & 0x0000FF00) >> 8)
        cdb[7] = int(address & 0x000000FF)
        cdb[8] = int((bytecount & 0xFF000000) >> 24)
        cdb[9] = int((bytecount & 0x00FF0000) >> 16)
        cdb[10] = int((bytecount & 0x0000FF00) >> 8)
        cdb[11] = int(bytecount & 0x000000FF)
        cdb[12] = cdb[13] = cdb[14] = cdb[15] = 0
        diagCommand.cdb = cdb
        diagCommand.cdbLen = 16

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Sending READ PORT CDB: %s" % diagCommand.cdb)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Buffer Size: %d Bytes" % dataBuffer.GetBufferSize())

        self.__sdCmdObj.SendDiagnostic(dataBuffer, diagCommand, ServiceWrap.SCTP_DATA_DIRECTION.DIRECTION_OUT)
        return dataBuffer

