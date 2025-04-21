"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : None
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : SdCommandLib.py
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : SDCommandLib.py
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
    from builtins import hex
    from builtins import range
    from builtins import *
from past.utils import old_div
from future.utils import with_metaclass

# SDDVT - Error Utils
import SDDVT.Common.ErrorCodes as ErrorCodes

# SDDVT - Configuration Data
import SDDVT.Common.getconfig as getconfig
import SDDVT.Common.GlobalConstants as gvar
from SDDVT.Common.customize_log import customize_log

# CVF Packages
import PatternGen
import SDCommandWrapper as sdcmdWrap
import CTFServiceWrapper as ServiceWrap
import Protocol.SD.Basic.TestCase as TestCase
import Core.Configuration as Configuration
import Core.ValidationError as ValidationError
import Validation.CVFTestFactory as FactoryMethod

# Python Build-in Modules
import os
import re
import sys
import time
import math
import copy
import random
import calendar
import collections
from inspect import currentframe, getframeinfo


# Global Variables
SRW_CARD_SLOT = 1
SDR_FW_LOOPBACK = 0
DEVICE_FPGA_TMP = 0
OCR_BYTE_31 = 0


class Singleton(type):
    def __init__(self, *args, **kwargs):
        super(Singleton, self).__init__(*args, **kwargs)
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance == None:
            self.instance = super(Singleton, self).__call__(*args, **kwargs)
        return self.instance


class SdCommandClass(with_metaclass(Singleton, customize_log)):

    def __init__(self, VTFContainer):
        ###### Creating CVF objects ######
        self.vtfContainer = VTFContainer
        #self.vtfContainer.cfg_manager.currentConfiguration.system       # systemCfg.xml values
        #self.vtfContainer.device_session.GetConfigInfo().GetIniDict()   # cvf.ini values in dictionary, refer https://confluence.wdc.com/display/SWT/2.6+ConfigInfo
        #self.vtfContainer.cfg_manager.currentConfiguration.variation    # current test file's xml values
        #self.vtfContainer.cmd_line_args                                 # command line arguments
        # To make changes in xml file on runtime use below method.
        # import Core.Configuration as Configuration
        # cfgMngr = Configuration.ConfigurationManagerInitializer.ConfigurationManager
        # cfgMngr.currentConfiguration.variation.No_of_Tasks = Max_CQ_Depth

        self.currCfg = Configuration.ConfigurationManagerInitializer.ConfigurationManager.currentConfiguration
        #self.currCfg.variation.No_of_Tasks = Max_CQ_Depth   # To make changes in xml file on runtime use this method.

        self.__CVFTestFactory = FactoryMethod.CVFTestFactory().GetProtocolLib()
        self.__TF = self.__CVFTestFactory.TestFixture
        self.__ErrorManager = self.vtfContainer.device_session.GetErrorManager()

        ###### Loading General Variables ######
        self.__testName = self.vtfContainer.GetTestName()
        #self.__cardMaxLba = self.vtfContainer.maxLBA
        self.__cardMaxLba = sdcmdWrap.WrapGetMaxLBA()

        ###### Creating SDDVT objects ######
        self.__errorCodes = ErrorCodes.ErrorCodes()
        self.__config = getconfig.getconfig()

        ###### Registers ######
        self.OCRRegister = 0xC1FF8000
        self.SCRRegister = None
        self.CSDRegister = None
        self.ArrCsdRegisterFieldStruct = None
        self.__CSDresponceBuff = ServiceWrap.Buffer.CreateBuffer(1, patternType = 0x00, isSector = True)
        self.__CIDresponceBuff = ServiceWrap.Buffer.CreateBuffer(1, patternType = 0x00, isSector = True)
        self.CIDRegister = None
        self.SD_Status = None
        self.__sdStatusReg = ServiceWrap.Buffer.CreateBuffer(1, patternType = 0x00, isSector = True)
        self.__sdSCR = ServiceWrap.Buffer.CreateBuffer(1, patternType = 0x00, isSector = True)
        self.__relativeCardAddress = 0x0000     # CMD3 - R6 Response

        ###### Secure Mode ######
        self.ProtectedArea = 0
        self.__SecureEnable = False
        self.__enableSignature = True   # This Flag is set to False if test application wants the signature to be disabled
        self.__selectorValue = 0
        self.__authenticate = True
        self.__ProtectedArea_MemCap = 0

        ###### CQ Variables ######
        self.CQTaskAgeingDict = collections.OrderedDict(("Task%d" % task, "NQ") for task in range(0, gvar.GlobalConstants.CQ_MAX_QUEUE_DEPTH))
        self.CQTaskDetails = [{}] * gvar.GlobalConstants.CQ_MAX_QUEUE_DEPTH
        self._CQDevConfigDict = {"CQ Enable": False, "Cache Enable": False, "Mode": "Voluntary", "CQ Depth": 0}
        # 128 + 32, ageing threshould decided by the Device
        self.__CQAgeingThreshold = 32
        self.__CMD44TaskID = None   # to store task id in Cmd44 and use it in Cmd45 in case of ageing in voluntary
        self.pgnenable = 0
        self.TasksQueued = 0
        self.ReadTasksQueued = 0
        self.WriteTasksQueued = 0
        self.TasksExecuted = 0
        self.ReadTasksExecuted = 0
        self.WriteTasksExecuted = 0
        self.TasksAborted = 0
        self._AgedOut = False
        self._AgedTaskID = None
        self.__patternSupportedInCQ =  {0:'ALL_ZERO', 1:'WORD_REPEATED', 2:'INCREMENTAL', 4:'CONST', 5:'ALL_ONE', 6:'ANY_WORD',
                                        7:'WORD_BLOCK_NUMBER', 8:'PATTERN_NEG_INCREMENTAL', 9:'PATTERN_NEG_CONST'} # 3:ANY_BUFFER not supported in CQ mode
        #self.__patternSupportedInCQ = {0:sdcmdWrap.Pattern.ALL_ZERO, 1:sdcmdWrap.Pattern.WORD_REPEATED,
                                        #2:sdcmdWrap.Pattern.INCREMENTAL, 4:sdcmdWrap.Pattern.CONST,
                                        #5:sdcmdWrap.Pattern.ALL_ONE, 6:sdcmdWrap.Pattern.ANY_WORD,
                                        #7:sdcmdWrap.Pattern.WORD_BLOCK_NUMBER, 8:sdcmdWrap.Pattern.PATTERN_NEG_INCREMENTAL,
                                        #9:sdcmdWrap.Pattern.PATTERN_NEG_CONST} # 3:sdcmdWrap.Pattern.ANY_BUFFER not supported in CQ mode

        ###### Initialization Specific Variables ######
        self.__fpgadownload = False
        self.__globalProjectConfVar = None
        self.__basicInitFlag = 0
        self._LVInitDone = False
        self.__spiMode = False

        ###### Response Variables ######
        self.__responseDataBuf = ServiceWrap.Buffer.CreateBuffer(1, 0x0)
        self.decoded_Perf_Enhance_Func = None
        self.decoded_Power_Management_Func = None
        self.decoded_General_Information = None
        self.decodedR1response = None
        self.__decodedR1bresponse = None
        self.__decodedR6response = None
        self.__decodedR7response = None
        self.__decodedSPIR1response = None
        self.__decodedSPIR2response = None
        self.__decodedSPIR3response = None
        self.__decodedSPIR7response = None

        ###### Library Specific Variables ######
        self.__WriteToReadOnlyBitsOfCSDnVerifyCMD27Status = None
        self.__strDKFile = os.path.join(os.getenv('SANDISK_CTF_HOME_X64'), "Security\\DK_num.bin")  # DK file path from CVF, reading based on global variables set by CVF
        self._anyWord = random.randint(1, 0xFFFF)  # 2 bytes of random data
        self.DEVICE_FPGA_TMP = DEVICE_FPGA_TMP
        self.__doErrorHandling = True
        self.__MULT = 0         # Calculated using C_SIZE_MULT in CSD Register.
        self.__BLOCK_LEN  = 0   # Calculated using READ_BL_LEN in CSD Register.
        self.__MemCap = 0
        self.BlocksTransferred = 0
        self._DDR200_SupportedGrpNum = 1
        self._CardMap = []      # list to store sequence number of LBAs starting from LBA specified by _CardMap_StartLBA and stores upto blockcount specified by _CardMap_BlockCount
        self._CardMap_StartLBA = 0x0        # Start LBA of the card map
        self._CardMap_BlockCount = 65536    # CardMap for 32MB
        self._CardMap_EndLBA = self._CardMap_StartLBA + self._CardMap_BlockCount - 1
        self.__ErrorManager.RegisterCallback(self.ExceptionCallBack)
        self.SDXC_SETTINGS = {"Set_XPC_bit": 0, "Send_CMD11_in_the_next_card_init": 0}

        ###### Customize Log ######
        self.fn = os.path.basename(getframeinfo(currentframe()).filename)
        customize_log.__init__(self, self.__TF)


    def FUNCTION_ENTRY(self, func):
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s : Starts -------------------------------------->" % func)

    def FUNCTION_EXIT(self, func):
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s : Ends -------------------------------------->\n" % func)

    def MaxLba(self):
        return self.__cardMaxLba

    def ErrorPrint(self, exc):
        self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s : %s" % ("GetErrorGroup", exc.GetErrorGroup()))
        self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s : %s" % ("GetErrorNumber", exc.GetErrorNumber()))
        self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Exception Message is -> %s" % exc.GetFailureDescription())

    def ExceptionCallBack(self, ErrorGroup, ErrorNumber_or_CardStatusEnum):
        """
        Description:
             As per the SD spec, CARD_IS_LOCKED and ERASE_RESET are not error bits but CVF raises exception for those bits.
             So clearing those exceptions here and handling those exceptions from the 32 bit R1/R1b response.
             For more info refer JIRA: CVF-22247
        Parameter Description:
             ErrorNumber_or_CardStatusEnum - If the exception is thrown by SDR host, second argument of this method
                                             will be filled with SDR error code. If the exception is thrown by CVF,
                                             second argument of this method will be filled with CVF enum of corresponding card status bit.
        """
        #self.noiseLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "------------- CallBack ----------------")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ErrorGroup - 0x%X, ErrorNumber_or_CardStatusEnum - 0x%X" % (ErrorGroup, ErrorNumber_or_CardStatusEnum))

        if ((ErrorNumber_or_CardStatusEnum == self.__errorCodes.CheckError('CARD_IS_LOCKED')) or (ErrorNumber_or_CardStatusEnum == sdcmdWrap.CARD_STATUS.STATUS_CODE_CARD_IS_LOCKED_S_X)
            or (ErrorNumber_or_CardStatusEnum == self.__errorCodes.CheckError('CARD_ERASE_RESET')) or (ErrorNumber_or_CardStatusEnum == sdcmdWrap.CARD_STATUS.STATUS_CODE_ERASE_RESET_S_R)):
            self.__ErrorManager.ClearAllErrors()
            # self.vtfContainer.CleanPendingExceptions()
        return 0

    def Data_Trans_Breakup(self, StartAddress, EndAddress, maxTransfer):
        """
        Description : In the case where testcase wants to write/read/erase within some particular LBA range with an interval,
                      this function will be used.
        Example     : StartAddress = 121, EndAddress = 424, maxTransfer = 100, then the yield will be like
                      First yield - 121, 100
                      Second yield - 221, 100
                      Third yield - 321, 100
                      Fourth yield - 421, 4
        """
        while True:
            currentTransferEndAddress = StartAddress + maxTransfer - 1
            if currentTransferEndAddress <= EndAddress:
                yield StartAddress, maxTransfer
            else:
                yield StartAddress, EndAddress - StartAddress + 1
            StartAddress += maxTransfer
            if StartAddress > EndAddress:
                break

        #for StartAddress in xrange(StartAddress, EndAddress + 1, maxTransfer):
            #currentTransferEndAddress = StartAddress + maxTransfer - 1
            #if currentTransferEndAddress <= EndAddress:
                #yield StartAddress, maxTransfer
            #else:
                #yield StartAddress, EndAddress - StartAddress + 1


    def CARD_OUT_OF_RANGE_Validation(self, StartLba, BlockCount, Cmd):

        CARD_OUT_OF_RANGE_Occured = True if (StartLba < 0 or StartLba >= self.__cardMaxLba or BlockCount < 1 or BlockCount > self.__cardMaxLba or (StartLba + BlockCount - 1) >= self.__cardMaxLba) else False

        if CARD_OUT_OF_RANGE_Occured:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CARD_OUT_OF_RANGE occured for StartLba: %s, BlockCount: %s" % (StartLba, BlockCount))
            raise ValidationError.CVFGenericExceptions(self.fn, "CARD_OUT_OF_RANGE occured for StartLba: %s, BlockCount: %s" % (StartLba, BlockCount))
        else:
            self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Checking boundary condition and continue without executing %s" % Cmd)

    def SetrelativeCardAddress(self, RCA = 0):
        self.__relativeCardAddress = RCA

    def GetRCA(self):
        """
        To get the RCA value
        """
        return self.__relativeCardAddress

    def GetMULT(self):
        # MULT is calculated from CSD register. Refer GetCSD method.
        return self.__MULT

    def SecureEnable(self, flag):
        self.__SecureEnable = flag
        return 0

    def enableSignature(self, flag):
        self.__enableSignature = flag
        return 0

    def SetSelector(self, selectorNum):
        self.__selectorValue = selectorNum
        return 0

    def DoErrorHandling (self, setFlag):
        self.__doErrorHandling = setFlag
        return 0

    def IsSDRFwLoopback(self):
        """
        Check the value for SDR_FW_LOOPBACK
        """
        if SDR_FW_LOOPBACK == 1:
            return True
        else:
            return False

    def SPIEnable(self, spiMode = True):
        """
        SPI Enable
        """
        self.__spiMode = spiMode

    def SPIEnableStatus(self):
        return self.__spiMode

    def GetCQAgeingThresholdValue(self):
        """
        To get the CQ Ageing Threshold value
        """
        return self.__CQAgeingThreshold

    def getProtectedArea(self):
        if self.ProtectedArea == None:
            raise ValidationError.TestFailError(self.fn, "Protected area value is not updated")
        return self.ProtectedArea

    def calculate_blockcount(self, startLba, endLba):
        """
        Ex: startLba = 0, endLba = 99, Number of blockcount = 100
        """
        return (endLba - startLba + 1)

    def calculate_endLba(self, startLba, blockcount):
        """
        Ex: startLba = 0, blockcount = 256 i.e) Lba range to be accessed 0 to 255
        """
        return (startLba + blockcount - 1)

    def ExtractError(self, exc, ErrorType = "ErrorCode"):
        """
        Parameter Description:
            exc - Exception get from "ValidationError.CVFGenericExceptions"
            ErrorType - "ErrorCode" returns error code of the exception / "ErrorString" returns error string of the exception
        """
        Pattern = r"Error (?P<ErrorCode>\d+): " if ErrorType == "ErrorCode" else r"CVFGenericExceptions: \\n(?P<ErrorString>.+)\\n\\nError"
        ExtractError = re.search(Pattern, exc.GetInternalErrorMessage())
        Error = int(ExtractError.group("ErrorCode")) if ErrorType == "ErrorCode" else ExtractError.group("ErrorString")
        return Error


    def GetMiscompareBuff(self):
        self.vtfContainer.CleanPendingExceptions()  # Clear CARD_COMPARE_ERROR error to prevent script failure
        MiscompareBuffer = ServiceWrap.Buffer.CreateBuffer(1, patternType = ServiceWrap.ALL_0, isSector = True)
        sdcmdWrap.GetBufferError(MiscompareBuffer)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_HEADER("Miscompare Data Buffer", "#", repeat = 18))
        MiscompareBuffer.PrintToLog()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_HEADER())
        return MiscompareBuffer

    def Set_SDXC_SETTINGS(self, Set_XPC_bit, Send_CMD11_in_the_next_card_init):
        self.SDXC_SETTINGS["Set_XPC_bit"] = Set_XPC_bit
        self.SDXC_SETTINGS["Send_CMD11_in_the_next_card_init"] = Send_CMD11_in_the_next_card_init

    def Get_SDXC_SETTINGS(self):
        Set_XPC_bit = self.SDXC_SETTINGS["Set_XPC_bit"]
        Send_CMD11_in_the_next_card_init = self.SDXC_SETTINGS["Send_CMD11_in_the_next_card_init"]
        self.Set_SDXC_SETTINGS(Set_XPC_bit = 0, Send_CMD11_in_the_next_card_init = 0)
        return Set_XPC_bit, Send_CMD11_in_the_next_card_init

    def Set_cvf_ini_File_Value(self, Name, Value):
        """
        Description   : This method is used to change the default value of variables from cvf.ini file on runtime.
        Parameters    : Name - The config parameter string whose value is to be set
                        Value - value to be set in microseconds
        For more info : https://confluence.wdc.com/display/SWT/2.6+ConfigInfo
        """
        DefaultValue = self.vtfContainer.device_session.GetConfigInfo().GetIniDict()[Name]
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Default value of '%s' is - %s in cvf.ini config file" % (Name, DefaultValue))
        self.vtfContainer.device_session.GetConfigInfo().SetValue(Name, Value)
        Value = self.vtfContainer.device_session.GetConfigInfo().GetIniDict()[Name]
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Value of '%s' is set to - %s in cvf.ini config file" % (Name, Value))

    def getCurrentExeCmdResponseBuf(self):
        '''
        Returns executed command response buffer
        '''
        return self.__responseDataBuf

    def WriteRegister(self, address, value):
        """
        address : Address of the SDR register where write has to happen
        value : Value that needs to be written on the SDR register address
        """
        sdcmdWrap.WriteRegister(regAddress = address, regValue = value)

    def ReadRegister(self, address):
        """
        address : Address of the register that needs to be read
        """
        RegisterValue = sdcmdWrap.ReadRegister(regAddress = address)
        return RegisterValue.GetRegisterValue()

    def SetVoltage(self, Voltage):
        """
        Set voltage to card
        Note: Equivalent CVF API of the CTF API power.SetVdd(voltage) is not available, Hence implementing the SetVdd
        API in the test layer based on the host log captured. Please refer SDR Reg_Map_SD-SDR2_2-01-01-xxxx.xls
        for more info about below registers.
        """
        Voltage = int(Voltage * 1000)    # Converting voltage to milli voltage
        self.ReadRegister(address = 0x18)
        self.ReadRegister(address = 0xAC)
        self.WriteRegister(address = 0xAE, value = 0xFA)
        self.WriteRegister(address = 0xB0, value = 0x07)

        ReadVoltage = self.ReadRegister(address = 0xA7)   # Reading the VDD value
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Current VDD is %s milli voltage" % ReadVoltage)
        self.ReadRegister(address = 0xA5)   # Reading the SDR power status

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Setting the VDD to %s milli voltage" % Voltage)
        Voltage = 0x8000 ^ Voltage
        self.WriteRegister(address = 0xA7, value = Voltage) # Setting the VDD value

        HW_Clear_Timeout_Count = 10
        while HW_Clear_Timeout_Count:
            ReadVoltage = self.ReadRegister(address = 0xA7)   # Reading the VDD value
            if (ReadVoltage >> 15) == 0:
                break
            HW_Clear_Timeout_Count -= 1

        if (ReadVoltage >> 15) != 0:
            raise ValidationError.TestFailError(self.fn, "MSB of SDR VDD(0xA7) register's value is non zero")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Current VDD is %s milli voltage" % ReadVoltage)
        self.ReadRegister(address = 0xA5)   # Reading the SDR power status

    def PowerCycle(self):
        """
        Description: Do card power cycle
        """
        sdPowerCycleParam = ServiceWrap.SD_POWER_CYCLE_PARAMS()
        sdPowerCycleParam.bIsEnablePowerSustenance = True   # Power Off Notification True
        sdPowerCycleParam.bIsEnableCache = False
        sdPowerCycleParam.bIsEnableCardInitiatedSelfMaintenance = False
        sdPowerCycleParam.bIsEnableHostInitiatedMaintenance = False
        sdPowerCycleParam.bIsDisablePowerManagementFunction = False
        sdPowerCycleParam.sdShutdownType = 0

        sdProtocolParam = ServiceWrap.PROTOCOL_SPECIFIC_PARAMS()
        sdProtocolParam.paramType = ServiceWrap.SD_POWER_CYCLE
        sdProtocolParam.sdParams = sdPowerCycleParam
        PowerCycle = ServiceWrap.PowerCycle(shutdownType = ServiceWrap.GRACEFUL, protocolParams = sdProtocolParam, sendType = ServiceWrap.SEND_IMMEDIATE_SYNC)
        return PowerCycle

    def SetFrequency(self, Freq):
        """
        Description: Set the frequency
        Parameter Description:
            Freq - Frequency in KHz
        """
        sdcmdWrap.SDRSetFrequency(freq = Freq * 1000)   # CVF API takes frequency in Hz, So multiply with 1000.
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Host frequency set to %d KHz\n" % (Freq))

    def GetFrequency(self):
        """
        Description: Get the frequency
        """
        # self.WriteRegister(address = 0x9C, value = 0x8000)
        # Freq = self.ReadRegister(address = 0x9A)
        self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "There is no CVF API equivalent to CTF API GetFrequency.")
        self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Value returned by GetFrequency is nowhere used. Hence returing from the function instead of raising exception.")
        return
        raise ValidationError.TestFailError(self.fn, "GetFrequency API is not implemented in CVF")
        # TOBEDONE: GetFrequency
        # Freq = self.__adapter.GetFrequency()   # CTF API
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Host frequency is %d KHz\n" % Freq)

    # def SetFreqWithTuning(self, Freq, tuneHostIfNeeded = True):
    #     """
    #     Description: This method should be called to set card frequency for UHS-I speed modes.
    #     Parameter Description:
    #         Freq : Frequency in KHz
    #         tuneHostIfNeeded: True - Send CMD19 to tune the host / False - CMD19 won't be sent
    #     """
    #     try:
    #         sdcmdWrap.SetFreqWithTuning(freq = Freq, tuneHostIfNeeded = tuneHostIfNeeded)
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    def SetFreqWithTuning(self, Freq):
        """
        Description: This method should be called to set card frequency for UHS-I speed modes.
        Parameter Description:
            Freq - Frequency in KHz
        """
        self.SetFrequency(Freq)
        TuningResultBuffer = ServiceWrap.Buffer.CreateBuffer(dataSize = 1, patternType = 0x0, isSector = True)
        sdcmdWrap.TuneHostForUHS(optimalTap = [], tuningBuffer = TuningResultBuffer)
        return TuningResultBuffer

    def globalSetSpeedMode(self, mode):
        self.FUNCTION_ENTRY("globalSetSpeedMode")

        if mode == "SDR12":
            globalHSHostFreq = int(self.__config.get('globalHSHostFreq'))   # Frequency value in KHz

            self.SwitchSpeedMode(mode = mode, freq = old_div(globalHSHostFreq, 1000))   # SwitchSpeedMode function takes freq in MHz

            CSD_Reg_Values= self.GET_CSD_VALUES()
            if(CSD_Reg_Values['TRAN_SPEED'] != gvar.CSD.TRAN_SPEED_SDR12):
                raise ValidationError.TestFailError(self.fn, "Transfer speed did not match with expected value")

        elif mode == "SDR25":
            globalHSHostFreq = int(self.__config.get('globalHSHostFreq'))   # Frequency value in KHz

            self.SwitchSpeedMode(mode = mode, freq = old_div(globalHSHostFreq, 1000))   # SwitchSpeedMode function takes freq in MHz

            CSD_Reg_Values= self.GET_CSD_VALUES()
            if(CSD_Reg_Values['TRAN_SPEED'] != gvar.CSD.TRAN_SPEED_SDR25):
                raise ValidationError.TestFailError(self.fn, "Transfer speed did not match with expected value")

        elif mode == "SDR50":
            globalVHSHostFreq = int(self.__config.get('globalVHSHostFreq')) # Frequency value in KHz

            self.SwitchSpeedMode(mode = mode, freq = old_div(globalVHSHostFreq, 1000))  # SwitchSpeedMode function takes freq in MHz

            CSD_Reg_Values= self.GET_CSD_VALUES()
            if(CSD_Reg_Values['TRAN_SPEED'] != gvar.CSD.TRAN_SPEED_SDR50_DDR50):
                raise ValidationError.TestFailError(self.fn, "Transfer speed did not match with expected value")

        elif mode == "DDR50":
            globalHSHostFreq = int(self.__config.get('globalHSHostFreq'))   # Frequency value in KHz

            self.SwitchSpeedMode(mode = mode, freq = old_div(globalHSHostFreq, 1000))   # SwitchSpeedMode function takes freq in MHz

            CSD_Reg_Values= self.GET_CSD_VALUES()
            if(CSD_Reg_Values['TRAN_SPEED'] != gvar.CSD.TRAN_SPEED_SDR50_DDR50):
                raise ValidationError.TestFailError(self.fn, "Transfer speed did not match with expected value")

        elif mode == "SDR104":
            globalVHSHostFreq = int(self.__config.get('globalVHSHostFreq')) # Frequency value in KHz

            self.SwitchSpeedMode(mode = mode, freq = old_div(globalVHSHostFreq, 1000))  # SwitchSpeedMode function takes freq in MHz

            CSD_Reg_Values= self.GET_CSD_VALUES()
            if(CSD_Reg_Values['TRAN_SPEED'] != gvar.CSD.TRAN_SPEED_SDR104):
                raise ValidationError.TestFailError(self.fn, "Transfer speed did not match with expected value")

        elif mode == "DDR200":
            globalVHSHostFreq = int(self.__config.get('globalVHSHostFreq')) # Frequency value in KHz

            self.SwitchSpeedMode(mode = mode, freq = old_div(globalVHSHostFreq, 1000))  # SwitchSpeedMode function takes freq in MHz

            CSD_Reg_Values= self.GET_CSD_VALUES()
            if(CSD_Reg_Values['TRAN_SPEED'] != gvar.CSD.TRAN_SPEED_SDR104):
                raise ValidationError.TestFailError(self.fn, "Transfer speed did not match with expected value")
        else:
            raise ValidationError.TestFailError(self.fn, "Invalid/No speed mode given")

        if self.GetCardStatus().count("CURRENT_STATE:Tran") != 1 :
            self.Cmd7()    # added to get the card to tran state

        self.FUNCTION_EXIT("globalSetSpeedMode")


    def SwitchSpeedMode(self, mode = 'SDR50', freq = 100):
        """
        Description: Function for switching to UHS-I speed mode (SDR12, SDR25, SDR50, DDR50)
        Parameter Description:
            mode = 'SDR12' or 'SDR25' or 'SDR50' or 'DDR50'
            freq = clock frequency in MHz
        """
        self.FUNCTION_ENTRY("SwitchSpeedMode")

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
            if self._DDR200_SupportedGrpNum == 2:
                arglist = [0xF, 0xE, 0x1, 0x1, 0xF, 0xF]
                switchString = "DDR200 SWITCHED IN GROUP2"
            else:
                arglist = [0x5, 0xF, 0x1, 0x1, 0xF, 0xF]
                switchString = "DDR200 SWITCHED IN GROUP1"
            if freq > 200:
                freq = 200  # in MHz

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Switching to %s speed" % mode)

        CMD6 = self.CardSwitchCmd(arginlist = arglist, blocksize = 0x40)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD6 ui64StatusStructure - %s" % CMD6.statusDataStructure.ui64StatusStructure)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD6 uiDataStructureVersion - %s" % CMD6.statusDataStructure.uiDataStructureVersion)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD6 MaximumPower - %s" % CMD6.statusDataStructure.uiMaximumPowerConsumption)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD6 FunctionSelectionOfFunctionGroup1 - %s" % CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup1)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD6 SupportBitsOfFunctionsInFunctionGroup1 - %s" % CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup1)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD6 uiFunctionSelectionOfFunctionGroup4 - %s" % CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup4)

        decodedResponse = self.DecodeSwitchCommandResponse("SWITCH", CMD6)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd6 Decoded Response = %s\n" % decodedResponse)  # Decoded Message

        if (switchString in decodedResponse):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Switched to %s" % mode)
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed to Switch to %s" % mode)
            raise ValidationError.TestFailError(self.fn, "Failed to switch to %s mode" % mode)

        if (mode == 'SDR104') or (mode == 'DDR50') or (mode == 'DDR200') or (mode == 'SDR50'):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Calling SetFreqWithTuning for %s......\n" % mode)
            # SetFreqWithTuning should be called for UHS-I speed mode
            self.SetFreqWithTuning(freq * 1000)
            freq = old_div((sdcmdWrap.WrapGetSDRFreq()), (1000 * 1000))     # Converting Hz into MHz
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Host Frequency set to %dMHz for %s\n" % (freq, mode))
        else:
            sdcmdWrap.SDRSetFrequency(freq = freq * 1000 * 1000)
            freq = old_div((sdcmdWrap.WrapGetSDRFreq()), (1000 * 1000))     # Converting Hz into MHz
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Setting Host Frequency to %dMHz for %s\n" % (freq, mode))

        self.FUNCTION_EXIT("SwitchSpeedMode")

###----------------------------- Class 0 Basic Start -----------------------------###

    def Cmd0(self, arg = 0x0):
        """
        CMD0: GO_IDLE_STATE
        """
        self.FUNCTION_ENTRY("Cmd0")

        if self.__spiMode == True:
            responseType = sdcmdWrap.TYPE_RESP._R1
        else:
            responseType = sdcmdWrap.TYPE_RESP._R0  # SD Mode

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 0,
                                                           argument = arg,
                                                           responseType = responseType,
                                                           responseData = self.__responseDataBuf)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        if self.__spiMode == True:
            self.DecodeR1Response(R1_Response = self.__responseDataBuf)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R1 type response")
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with no response")
        self.FUNCTION_EXIT("Cmd0")
        return self.__responseDataBuf

    # def Cmd0(self):
    #     """
    #     Cmd0 - GO_IDLE_STATE
    #     """
    #     self.FUNCTION_ENTRY("Cmd0")
    #     try:
    #         self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_CMD0_TO_RESET_CARD)
    #         sdcmdWrap.GoIdleState()
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         self.ErrorPrint(exc)
    #         raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
    #     self.FUNCTION_EXIT("Cmd0")


    def Cmd1(self, arg = 0x0):
        """
        CMD1: SEND_OP_COND
        Description:
            CMD1 is only valid in SPI mode, Reserved CMD in SD mode.
            It sends Host Capacity Support information and activates the card's initialization process.
        """
        self.FUNCTION_ENTRY("Cmd1")

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 1,
                                                           argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.DecodeR1Response(R1_Response = self.__responseDataBuf)
        self.FUNCTION_EXIT("Cmd1")
        return self.__responseDataBuf


    def Cmd2(self):
        """
        CMD2 - ALL_SEND_CID
        """
        self.FUNCTION_ENTRY("Cmd2")
        self.__CIDresponceBuff.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 2,
                                                           argument = 0x00,
                                                           responseType = sdcmdWrap.TYPE_RESP._R2,
                                                           responseData = self.__CIDresponceBuff)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            retValue = self.__CIDresponceBuff.GetData(0, 17)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.vtfContainer.CleanPendingExceptions()
            self.__CIDresponceBuff = ServiceWrap.Buffer.CreateBuffer(1, 0x00)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R2 type response")
        retValue.PrintToLog()
        self.FUNCTION_EXIT("Cmd2")
        return retValue

    #def Cmd2(self):
        #"""
        #Cmd2 - All_Send_CID
        #"""
        #self.FUNCTION_ENTRY("Cmd2")
        #try:
            #CMD2 = sdcmdWrap.AllSendCid()
            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('CID Register', CMD2.pyResponseData.r2Response.iCID_CSD))
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.ErrorPrint(exc)
            #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
        #self.FUNCTION_EXIT("Cmd2")
        #return CMD2

    def Cmd3(self):
        """
        CMD3 - SET_RELATIVE_ADDRESS
        """
        self.FUNCTION_ENTRY("Cmd3")
        self.__responseDataBuf.Fill(value = 0x0)
        self.__relativeCardAddress = 0x0

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 3,
                                                           argument = 0x00,
                                                           responseType = sdcmdWrap.TYPE_RESP._R6,
                                                           responseData = self.__responseDataBuf)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            retValue = self.__responseDataBuf.GetData(0, 6)
            self.__decodedR6response = self.DecodeR6Response(resBuffer = retValue)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.__decodedR6response = self.DecodeR6Response(resBuffer = retValue)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R6 type response: %s" % self.__decodedR6response)
        self.FUNCTION_EXIT("Cmd3")
        return self.__relativeCardAddress

    #def Cmd3(self):
        #"""
        #Cmd3 - Send_Relative_Address
        #"""
        #self.FUNCTION_ENTRY("Cmd3")
        #try:
            #CMD3 = sdcmdWrap.SendRelativeAddr()
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.ErrorPrint(exc)
            #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('New-RCA', CMD3.pyResponseData.r6Response.uiNewPublishedRCAOfCard))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Card-Status-Bits', CMD3.pyResponseData.r6Response.uiCardStatusBits))
        #self.__relativeCardAddress = CMD3.pyResponseData.r6Response.uiNewPublishedRCAOfCard
        #self.FUNCTION_EXIT("Cmd3")
        #return CMD3

    def Cmd4(self, DSR = 0x0):
        """
        CMD4 - SET_DSR
        """
        self.FUNCTION_ENTRY("Cmd4")
        DSR = DSR << 16

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 4,
                                                           argument = DSR,
                                                           responseType = sdcmdWrap.TYPE_RESP._R0)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with no response")
        self.FUNCTION_EXIT("Cmd4")

    #def Cmd4(self, DSR = 0x404):
        #"""
        #CMD4 - SET_DSR
        #"""
        #self.FUNCTION_ENTRY("Cmd4")
        #try:
            #CMD4 = sdcmdWrap.SDSetDSR(uiDSR = DSR)
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.ErrorPrint(exc)
            #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD4.pyResponseData.r1Response.uiCardStatus))
        #self.FUNCTION_EXIT("Cmd4")
        #return CMD4

    def Cmd7(self, deSelect = False):
        """
        CMD7 - SEL_DESELECT_CARD
        """
        self.FUNCTION_ENTRY("Cmd7")
        self.__responseDataBuf.Fill(value = 0x0)
        if deSelect == True:
            arg = 0x00000000
        else:
            arg = self.__relativeCardAddress << 16

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 7,
                                                           argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            # If expectTimeOut is true don't raise exception. 27 is error code for time out exception
            if ((exc.GetErrorNumber() == 0x1) or (exc.GetErrorNumber() == 27)) and (deSelect == True):
                self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure
                cardState = self.GetCardStatus()
                if(cardState.count('CURRENT_STATE:Stby') > 0):
                    return 0
                else:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD7[SEL_DESELECT_CARD] Failed with Timout Error")
                    raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
            else:
                self.ErrorPrint(exc)
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card-Status : %s" % self.decodedR1response)
        self.FUNCTION_EXIT("Cmd7")

    def Select_Deselect_Card(self, Select = True):
        """
        Cmd7 - Select_Deselect_Card
        """
        self.FUNCTION_ENTRY("Cmd7")

        if Select == False:
            RCA = 0x0000
        else:
            RCA = self.__relativeCardAddress
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %x" % ('CMD7 with argument RCA as', RCA))

        try:
            CMD7 = sdcmdWrap.SelectDeselectCard(uiRCA = RCA, sdr_card_slot = 1, sdr_bSelect = Select)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Card-Req-ui32Args', CMD7.pyCmdObject.commandData.ui32Args))
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            # If expectTimeOut is true don't raise exception. 27 is error code for time out exception
            if ((exc.GetErrorNumber() == 0x1) or (exc.GetErrorNumber() == 27)) and (Select == False):
                self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure
                cardState = self.GetCardStatus()
                if(cardState.count('CURRENT_STATE:Stby') > 0):
                    return 0
                else:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed with Timout Error")
                    raise ValidationError.TestFailError(self.fn, exc.GetFailureDescription())
            else:
                self.ErrorPrint(exc)
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD7.pyResponseData.r1bResponse.uiCardStatus))
        self.FUNCTION_EXIT("Cmd7")

    def Cmd8(self, argVal=0x000001AA):
        """
        CMD8 - SEND_IF_COND
        """
        self.FUNCTION_ENTRY("Cmd8")
        self.__responseDataBuf.Fill(value = 0x0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Sending CMD8 with argument = 0x%X" % argVal)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 8,
                                                           argument = argVal,
                                                           responseType = sdcmdWrap.TYPE_RESP._R7,
                                                           responseData = self.__responseDataBuf)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        if self.__spiMode == True:
            retValue = self.__responseDataBuf   # SPI Mode
        else:
            retValue = self.__responseDataBuf.GetData(0, 6) # SD Mode

        self.__decodedR7response = self.DecodeR7Response(self.__responseDataBuf)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R7 type response: %s" % self.__decodedR7response)

        self.FUNCTION_EXIT("Cmd8")
        return retValue

    # def Cmd8(self, PCIe1_2VSupport = True, PCIeAvailibility = True, VoltageSuppliedVHS = 0x1, CheckPattern = 0xAA):
    #     """
    #     CMD8 - Send_IF_Cond

    #     VoltageSuppliedVHS : 0x1 - check whether card supports voltage between 2.7V - 3.6V
    #     Set default value of CheckPattern as 0xAA(10101010b)(170) recommented by SD Spec 7.0.
    #     """

    #     self.FUNCTION_ENTRY("Cmd8")
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('PCIe1_2VSupport as', PCIe1_2VSupport))
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('PCIeAvailibility as', PCIeAvailibility))
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('VoltageSuppliedVHS as', VoltageSuppliedVHS))
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('CheckPattern as', CheckPattern))

    #     try:
    #         CMD8 = sdcmdWrap.SendIFCond(uiPCIe1_2VSupport = PCIe1_2VSupport, uiPCIeAvailibility = PCIeAvailibility,
    #                                     uiVoltageSuppliedVHS = VoltageSuppliedVHS, uiCheckPattern = CheckPattern)
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         self.ErrorPrint(exc)
    #         raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('PCIe1_2VSupport', CMD8.pyResponseData.r7Response.uiPCIe_1_2_v_Support))
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('PCIeAvailibility', CMD8.pyResponseData.r7Response.uiPCIeResponse))
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('VoltageSuppliedVHS', CMD8.pyResponseData.r7Response.uiVoltageAccepted))
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('CheckPattern', CMD8.pyResponseData.r7Response.uiEchobackCheckPattern))

    #     self.FUNCTION_EXIT("Cmd8")
    #     return CMD8

    def Cmd9(self):
        """
        CMD9 - SEND_CSD
        Note: Unlike the SD Memory Card protocol (where the register contents is sent as a command response),
        reading the contents of the CSD and CID registers in SPI mode is a simple read-block transaction. The
        card will respond with a standard response token followed by a data block of 16 bytes
        suffixed with a 16-bit CRC.
        """
        self.FUNCTION_ENTRY("Cmd9")
        self.__CSDresponceBuff.Fill(value = 0x0)
        arg = self.__relativeCardAddress << 16

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 9,
                                                           argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R2,
                                                           responseData = self.__CSDresponceBuff)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            retValue = self.__CSDresponceBuff.GetData(offset = 0, length = 17)    # Get 136 bits buffer of R2 response which includes 128bits data content of CSD Register
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.vtfContainer.CleanPendingExceptions()
            self.__CSDresponceBuff = ServiceWrap.Buffer.CreateBuffer(1, 0x00)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        retValue.PrintToLog()
        self.FUNCTION_EXIT("Cmd9")
        return retValue

    # def Cmd9(self):
    #     """
    #     CMD9 - SendCSD
    #     """
    #     self.FUNCTION_ENTRY("Cmd9")

    #     try:
    #         CMD9 = sdcmdWrap.SendCsd(uiRCA = self.__relativeCardAddress)
    #         self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s" % CMD9.pyResponseData.r2Response.iCID_CSD)
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         self.ErrorPrint(exc)
    #         raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    #     self.FUNCTION_EXIT("Cmd9")
    #     return CMD9


    def GetCSDStructVer(self):
        """
        Description : Checks 30th(CCS - Card Capacity Support) and 27th(CO2T - Card Over 2TB) bit of OCR register to get
                      the card capacity type. Based on the card capacity CSD register has different structure.
                      For more info refer Figure 4-75 in SD spec part - 1(Physical layer).
        """

        if ((self.OCRRegister & 0x40000000) != 0) and ((self.OCRRegister & 0x8000000) != 0):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card is SDUC card. CSD register field structure version is 3.")
            return 3

        elif ((self.OCRRegister & 0x40000000) != 0) and ((self.OCRRegister & 0x8000000) == 0):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card is SDHC/SDXC card. CSD register field structure version is 2.")
            return 2

        elif ((self.OCRRegister & 0x40000000) == 0) and ((self.OCRRegister & 0x8000000) == 0):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card is SDSC card. CSD register field structure version is 1.")
            return 1
        else:
            # if CO2T(Card over 2TB) bit is set as 1 in response then CCS(Card Capacity Support) bit shall also be 1.
            raise ValidationError.TestFailError(self.fn, "CCS bit is 0. CO2T bit is 1 in OCR register")


    def GetCSD(self):
        """
        Get Card Specific Data

        Note: Unlike the SD Memory Card protocol (where the register contents is sent as a command response),
        reading the contents of the CSD and CID registers in SPI mode is a simple read-block transaction. The
        card will respond with a standard response token followed by a data block of 16 bytes
        suffixed with a 16-bit CRC.
        """
        self.FUNCTION_ENTRY("GetCSD")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "************************* CSD Register *************************\n")

        try:
            csd = sdcmdWrap.WrapGetCsd()    # Getting CSD Register
            self.ArrCsdRegisterFieldStruct = csd.uiArrCsdRegisterFieldStruct[::-1]

            CSD_STRUCT_VER = self.GetCSDStructVer()
            exec("self.CSDRegister = csd.CsdRegisterFieldStructVer%d" % CSD_STRUCT_VER)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.CRC, self.CSDRegister.uiCrc))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.FILE_FORMAT, self.CSDRegister.uiFileFormaT))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.TMP_WRITE_PROTECT, self.CSDRegister.uiTmpWriteProtect))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.PERM_WRITE_PROTECT, self.CSDRegister.uiPerm_Write_Protect))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.COPY, self.CSDRegister.uiCopy))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.FILE_FORMAT_GRP, self.CSDRegister.uiFileFormatGrp))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.WRITE_BL_PARTIAL, self.CSDRegister.uiWritEBlPartial))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.WRITE_BL_LEN, self.CSDRegister.uiWriteBlLen))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.R2W_FACTOR, self.CSDRegister.uiR2WFactor))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.WP_GRP_ENABLE, self.CSDRegister.uiWpGrpEnable))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.WP_GRP_SIZE, self.CSDRegister.uiWpGrpSize))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.SECTOR_SIZE, self.CSDRegister.uiSectorSize))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.ERASE_BLK_EN, self.CSDRegister.uiEraseBlkEn))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.C_SIZE, self.CSDRegister.uiC_Size))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.DSR_IMP, self.CSDRegister.uiDsrImp))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.READ_BLK_MISALIGN, self.CSDRegister.uiReadBlkMisalign))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.WRITE_BLK_MISALIGN, self.CSDRegister.uiWriteBlkMisalign))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.READ_BL_PARTIAL, self.CSDRegister.uiReadBlPartial))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.READ_BL_LEN, self.CSDRegister.uiReadBlLen))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.CCC, self.CSDRegister.uiCcc))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.TRAN_SPEED, self.CSDRegister.uiTranSpeed))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.NSAC, self.CSDRegister.uiNsac))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.TAAC, self.CSDRegister.uiTaac))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % (gvar.CSD.CSD_STRUCTURE, self.CSDRegister.uiCsdStructure))

            # In case of SDSC cards.
            if CSD_STRUCT_VER == 1:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Device size multiplier', self.CSDRegister.uiCSizeMult))
                # To know more about below calculation refer C_SIZE explanation at chapter 5.3.2 CSD Register (CSD Version 1.0)
                # in SD spec part 1 physical layer specification version 7.0
                self.__MULT = math.pow(2, (self.CSDRegister.uiCSizeMult + 2))
                self.__BLOCK_LEN = math.pow(2, self.CSDRegister.uiReadBlLen)

        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.FUNCTION_EXIT("GetCSD")
        return csd


    def Cmd10(self):
        """
        CMD10 - SEND_CID
        """
        self.FUNCTION_ENTRY("Cmd10")
        self.__CIDresponceBuff.Fill(value = 0x0)
        arg = self.__relativeCardAddress << 16

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 10,
                                                           argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R2,
                                                           responseData = self.__CIDresponceBuff)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            retValue = self.__CIDresponceBuff.GetData(offset = 0, length = 17)    # Get 136 bits buffer of R2 response which includes 128bits data content of CID Register
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.vtfContainer.CleanPendingExceptions()
            self.__CIDresponceBuff = ServiceWrap.Buffer.CreateBuffer(1, 0x00)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R2 type response")
        retValue.PrintToLog()
        self.FUNCTION_EXIT("Cmd10")
        return retValue

    # def Cmd10(self, RCA = 0xD555):
    #     """
    #     CMD10 - SendCID
    #     """
    #     self.FUNCTION_ENTRY("Cmd10")
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s : %s" % ("RCA of Card is", RCA))

    #     try:
    #         CMD10 = sdcmdWrap.SendCid(uiRCA = RCA)
    #         self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CID Register: %s" % CMD10.pyResponseData.r2Response.iCID_CSD)
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         self.ErrorPrint(exc)
    #         raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    #     self.FUNCTION_EXIT("Cmd10")
    #     return CMD10


    def GetCID(self):
        """
        Get Card Identification Data
        """
        self.FUNCTION_ENTRY("GetCID")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "\n************************************ CID Register ************************************\n")

        try:
            cid = sdcmdWrap.WrapGetCid()
            self.CIDRegister = cid
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.FUNCTION_EXIT("GetCID")
        return cid

    def Cmd11(self, ForceSwitch = False):
        """
        CMD11 - VOLTAGE_SWITCH
        Use ForceSwitch when we want to execute CMD11 even when we do not want to switch to 1.8V
        """
        self.FUNCTION_ENTRY("Cmd11")
        global OCR_BYTE_31
        self.__responseDataBuf.Fill(value = 0x0)
        arg = 0x00

        if ForceSwitch == False:
            S18A_bit = 0x01
            if ((OCR_BYTE_31 & S18A_bit) == 0x01):

                commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 11,
                                                                   argument = arg,
                                                                   responseType = sdcmdWrap.TYPE_RESP._R1,
                                                                   responseData = self.__responseDataBuf)
                commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

                try:
                    sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
                    retValue = self.__responseDataBuf.GetData(0, 6)
                except ValidationError.CVFExceptionTypes as exc:
                    exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                    self.ErrorPrint(exc)
                    raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

                self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "!!!!!! Sleeping 1 sec after CMD11")
                time.sleep(1)
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "S18A_bit is 0, So not switching to 1.8V")
        elif ForceSwitch == True:
            commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 11,
                                                               argument = arg,
                                                               responseType = sdcmdWrap.TYPE_RESP._R1,
                                                               responseData = self.__responseDataBuf)
            commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

            try:
                sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                errstring = exc.GetFailureDescription()
                if errstring.find("CARD_IS_NOT_RESPONDING") != -1:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card is reporting expected CARD_IS_NOT_RESPONDING error for Cmd11\n")
                    self.vtfContainer.CleanPendingExceptions()  # Clear CARD_IS_NOT_RESPONDING error to prevent script failure
                else:
                    self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Expected error is CARD_IS_NOT_RESPONDING for Cmd11. But error occured is - %s" % errstring)
                    raise ValidationError.TestFailError(self.fn, "Expected error is CARD_IS_NOT_RESPONDING for Cmd11. But error occured is - %s" % errstring)
            else:
                raise ValidationError.TestFailError(self.fn, "Expected CARD_IS_NOT_RESPONDING failure is not occured")

        self.FUNCTION_EXIT("Cmd11")


    def Cmd12(self, arg = 0xaaaaaaaa):
        """
        CMD12 - STOP_TRANSMISSION
        """
        self.FUNCTION_ENTRY("Cmd12")
        self.__responseDataBuf.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 12,
                                                           argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1b,
                                                           responseData = self.__responseDataBuf)
        cmdFlags = sdcmdWrap.CommandFlags()
        cmdFlags.DoSendStatus = True
        commandDefinitionObj.flags = cmdFlags

        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R1b type response: 0x%X" % self.__responseDataBuf.GetFourBytesToInt(offset = 1, little_endian = False))
        self.FUNCTION_EXIT("Cmd12")

    # def Cmd12(self):
    #     """
    #     CMD12 - STOP_TRANSMISSION
    #     """
    #     self.FUNCTION_ENTRY("Cmd12")

    #     try:
    #         CMD12 = sdcmdWrap.StopTransmission()
    #         self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Card-Req-ui32Args', CMD12.pyCmdObject.commandData.ui32Args))
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         self.ErrorPrint(exc)
    #         raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD12.pyResponseData.r1bResponse.uiCardStatus))
    #     self.FUNCTION_EXIT("Cmd12")
    #     return CMD12

    def Cmd13(self, SendTaskStatus = False):
        """
        CMD13 - SEND_STATUS
        """
        self.FUNCTION_ENTRY("Cmd13")
        self.__responseDataBuf.Fill(value = 0x0)
        arg = self.__relativeCardAddress << 16

        if self.__spiMode != True:
            if SendTaskStatus == True:
                arg = ((self.__relativeCardAddress << 16) | (1 << 15))

            commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 13,
                                                               argument = arg,
                                                               responseType = sdcmdWrap.TYPE_RESP._R1,
                                                               responseData = self.__responseDataBuf)
            commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

            try:
                sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.ErrorPrint(exc)
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

            if SendTaskStatus == False:
                self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
                self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card-Status with R1 response : %s" % self.decodedR1response)
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Task-Status : %s" % self.__responseDataBuf.GetFourBytesToInt(offset = 1, little_endian = False))
        else:
            commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 13,
                                                               argument = 0,
                                                               responseType = sdcmdWrap.TYPE_RESP._R2,
                                                               responseData = self.__responseDataBuf)
            commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

            try:
                sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.ErrorPrint(exc)
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

            self.__decodedSPIR2response = self.DecodeSPIR2Response(self.__responseDataBuf)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "(SPI)Card-Status with R2 response : %s" % self.__decodedSPIR2response)

        self.FUNCTION_EXIT("Cmd13")
        return self.__responseDataBuf

    # def Cmd13(self, SendTaskStatus = False):
    #     """
    #     CMD13 - CARD_STATUS
    #     """
    #     self.FUNCTION_ENTRY("Cmd13")
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("RCA", self.__relativeCardAddress))

    #     try:
    #         CMD13 =  sdcmdWrap.SendStatus(uiRCA = self.__relativeCardAddress, bSendTaskStatus = SendTaskStatus)
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         self.ErrorPrint(exc)
    #         raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    #     if(self.__spiMode != True):
    #         self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Cmd-Status', CMD13.pyResponseData.r1Response.eStatus))
    #         self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Cmd-Resp1', CMD13.pyResponseData.r1Response.sdR1RespData))

    #         if SendTaskStatus == False:
    #             self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD13.pyResponseData.r1Response.uiCardStatus))
    #             self.decodedR1response = self.DecodeR1Response(CMD13.pyResponseData.r1Response.uiCardStatus)
    #         else:
    #             self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Task-Status', CMD13.pyResponseData.r1Response.uiCardStatus))

    #     self.FUNCTION_EXIT("Cmd13")
    #     return CMD13

    def Cmd15(self, RCA = None):
        """
        CMD15 - GO_INACTIVE_STATE
        """
        self.FUNCTION_ENTRY("Cmd15")
        if RCA == None:
            arg = self.__relativeCardAddress << 16
        else:
            arg = RCA << 16

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 15,
                                                           argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R0)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with no response")
        self.FUNCTION_EXIT("Cmd15")

    #def Cmd15(self, RCA = None):
        #"""
        #CMD15 - GO_INACTIVE_STATE
        #"""
        #if RCA == None:
            #RCA = self.__relativeCardAddress
        #self.FUNCTION_ENTRY("Cmd15")
        #try:
            #sdcmdWrap.GoInactiveState(uiRCA = RCA)
            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD15[GO_INACTIVE_STATE] Passed")
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.ErrorPrint(exc)
            #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
        #self.FUNCTION_EXIT("Cmd15")

###----------------------------- Class 0 Basic End -----------------------------###

###----------------------------- Class 1 Command Queue Function Commands Start -----------------------------###

    def Cmd43(self, TaskID, OpCode, expectBsyState = False, argument=None):
        """
        CMD43 - Queue_Management
        """
        self.FUNCTION_ENTRY("Cmd43")

        r1btimeout = 250
        self.__responseDataBuf.Fill(value = 0x0)
        OpCodeDict = {'WholeQueue':1, 'SingleTask':2, 1:1, 2:2}

        if (argument == None):
            if OpCode in OpCodeDict:
                arg = ((TaskID & 0x1F) << 16 ) | (OpCodeDict[OpCode] & 0xF)
            else:
                arg = ((TaskID & 0x1F) << 16 ) | (OpCode & 0xF)
        else:
            arg = argument

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD43[Q-MANAGEMENT]: Argument = 0x%X" % arg)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 43,
                                                           argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1b,
                                                           responseData = self.__responseDataBuf,
                                                           R1bTimeout = r1btimeout)
        commandDefinitionObj.flags.DoSendStatus = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        if (OpCode == 2) or (OpCode == "SingleTask"):
            self.TasksAborted += 1
            if self._CQDevConfigDict["Mode"] == "Voluntary":
                self.CQTaskAgeingDict["Task%d" % TaskID] = "NQ"
        else:
            count = collections.Counter(list(self.CQTaskAgeingDict.values()))
            self.TasksAborted += (len(list(self.CQTaskAgeingDict.values())) - count["NQ"])
            self.CQTaskAgeingDict = collections.OrderedDict(("Task%d" % task, "NQ") for task in range(0, gvar.GlobalConstants.CQ_MAX_QUEUE_DEPTH))
            self._AgedOut = False
            self._AgedTaskID = None
            self.CQTaskDetails = [{}] * gvar.GlobalConstants.CQ_MAX_QUEUE_DEPTH

        self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R1b type response: %s" % self.decodedR1response)

        if expectBsyState == True:
            self.FUNCTION_EXIT("Cmd43")
            return
        else:
            # Comes here in case of CQ mode immediately after receiving the CMD43 R1 response.
                # 1. Check for busytimeout status from host using GetDeviceBusyStatus API
                # 2. Keep sending CMD13 until the card is out of busy
            self.CheckDeviceBusyStatus(Command = "CMD43")

        self.FUNCTION_EXIT("Cmd43")

    # def Cmd43(self, TaskID = 0, OpCode = 'SingleTask', expectBsyState = False):
    #     """
    #     CMD43 - Queue_Management
    #     Parameter Description:
    #         OpCode: 1 / 'WholeQueue' - 1, 2 / 'SingleTask' - 2
    #         TaskID: Task ID of the queued task which to be aborted. TaskID is valid when OpCode is 2.
    #                 As per SD spec 9.0 part-I, In sequential mode, single task abort should not be given.
    #     """
    #     self.FUNCTION_ENTRY("Cmd43")

    #     OpCodeDict = {'WholeQueue': 1, 'SingleTask': 2, 1: 1, 2: 2}
    #     if OpCode in OpCodeDict:
    #         OpCode = OpCodeDict[OpCode]

    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CMD43_ARGS(OpCode, TaskID))

    #     try:
    #         CMD43 = sdcmdWrap.QueueManagementCmd(uiTaskID = TaskID, uiOPCode = OpCode)
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CMD43_FAILED(TaskID, OpCode))
    #         self.ErrorPrint(exc)
    #         raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD43.pyResponseData.r1bResponse.uiCardStatus))

    #     if (OpCode == 2):
    #         self.TasksAborted += 1
    #         if self._CQDevConfigDict["Mode"] == "Voluntary":
    #             self.CQTaskAgeingDict["Task%d" % TaskID] = "NQ"
    #     else:
    #         count = collections.Counter(self.CQTaskAgeingDict.values())
    #         self.TasksAborted += (len(self.CQTaskAgeingDict.values()) - count["NQ"])
    #         self.CQTaskAgeingDict = collections.OrderedDict(("Task%d" % task, "NQ") for task in range(0, gvar.GlobalConstants.CQ_MAX_QUEUE_DEPTH))
    #         self._AgedOut = False
    #         self._AgedTaskID = None
    #         self.CQTaskDetails = [{}] * gvar.GlobalConstants.CQ_MAX_QUEUE_DEPTH

    #     self.decodedR1response = self.DecodeR1Response(CMD43.pyResponseData.r1Response.uiCardStatus)

    #     if expectBsyState == True:
    #         self.FUNCTION_EXIT("Cmd43")
    #         return
    #     else:
    #         # Comes here in case of CQ mode immediately after receiving the CMD43 R1 response.
    #             # 1. Check for busytimeout status from host using GetDeviceBusyStatus API
    #             # 2. Keep sending CMD13 until the card is out of busy
    #         self.CheckDeviceBusyStatus(Command = "CMD43")

    #     self.FUNCTION_EXIT("Cmd43")
    #     return CMD43


    def Cmd44(self, arg):
        """
        CMD44 - Q_Task_Info_A
        """
        self.FUNCTION_ENTRY("Cmd44")
        self.__responseDataBuf.Fill(value = 0x0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD44[Q-TASK_INFO_A]: Argument = 0x%X" % arg)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 44,
                                                           argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
        commandDefinitionObj.flags.DoSendStatus = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R1 type response : %s" % self.decodedR1response)
        TaskID = (arg >> 16) & 0x1F
        self.__CMD44TaskID = TaskID # used for ageing. TaskID stored in CMD44 and used in CMD45.
        BlockCount = arg & 0xFFFF
        Priority = (arg >> 23) & 0x1
        Direction = (arg >> 30) & 0x1
        self.CQTaskDetails[TaskID] = {"TaskID":TaskID}
        self.CQTaskDetails[TaskID].update({"BlockCount": BlockCount, "Direction": Direction, "Priority": Priority})
        self.FUNCTION_EXIT("Cmd44")

    #def Cmd44(self, NumberOfBlocks = 8, TaskID = 1, Priority = 0, Direction = 0, ExtendedAddress = 0):
        #"""
        #CMD44 - Q_Task_Info_A

        #Functionality: To Specify the task parameters of a particular task
        #NumBlocks is 16 bit value, 0xFFFF is maximum value of 16 bit binary that is 1111111111111111;
        #Priority = 0    # 0 means No Priority request and 1 means Priority;
        #ExtendedAddress = random.randint(1, 0x3F)  # ExtendedAddress is 6 bit value;
        #Direction = random.randint(0, 1)    # 0 means write and 1 means read.
        #"""
        #self.FUNCTION_ENTRY("Cmd44")

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CMD44_ARGS(Direction, ExtendedAddress, Priority, TaskID, NumberOfBlocks))

        #try:
            #CMD44 =  sdcmdWrap.QueueTaskInfoA(uiNumberOfBlocks = NumberOfBlocks,
                                              #uiTaskID = TaskID,
                                              #uiPriority = Priority,
                                              #uiExtendedAddress = ExtendedAddress,
                                              #uiDirection = Direction)
            #self.noiseLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD44.pyResponseData.r1Response.uiCardStatus))
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CMD44_FAILED(Direction, ExtendedAddress, Priority, TaskID, NumberOfBlocks))
            #self.ErrorPrint(exc)
            #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        #self.decodedR1response = self.DecodeR1Response(CMD44.pyResponseData.r1Response.uiCardStatus)
        #self.__CMD44TaskID = TaskID         # Used for ageing. TaskID stored in CMD44 and used in CMD45.
        #self.CQTaskDetails[TaskID] = {"TaskID": TaskID}
        #self.CQTaskDetails[TaskID].update({"BlockCount": NumberOfBlocks, "Direction": Direction, "Priority": Priority})

        #self.FUNCTION_EXIT("Cmd44")
        #return CMD44


    def Cmd45(self, StartBlockAddr):
        """
        CMD45 - Q_Task_Info_B
        """
        self.FUNCTION_ENTRY("Cmd45")
        self.__responseDataBuf.Fill(value = 0x0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD45[Q-TASK_INFO_B]: StartBlockAddr = 0x%X" % StartBlockAddr)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 45,
                                                           argument = StartBlockAddr,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
        commandDefinitionObj.flags.DoSendStatus = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            if self.__CMD44TaskID != None:
                self.CQTaskDetails[self.__CMD44TaskID] = {}
            self.__CMD44TaskID = None           # Used for ageing. Clearing it in failure
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R1 type response : %s" % self.decodedR1response)

        TaskID = self.__CMD44TaskID
        self.__CMD44TaskID = None

        if TaskID != None:
            self.CQTaskDetails[TaskID].update({"LBA": hex(StartBlockAddr)})
            self.TasksQueued += 1

            if(self.CQTaskDetails[TaskID]["Direction"]) == 0:
                self.WriteTasksQueued += 1
            elif(self.CQTaskDetails[TaskID]["Direction"]) == 1:
                self.ReadTasksQueued += 1

            if self._CQDevConfigDict["Mode"] == "Sequential":
                self.CQTaskAgeingDict["Task%d" % TaskID] = "InQ"
            else:
                self.CQTaskAgeingDict["Task%d" % TaskID] = 0

                ageingList = collections.OrderedDict((taskit, ageingcount + 1) if(type(ageingcount) == int) else(taskit, ageingcount) for taskit, ageingcount in  list(self.CQTaskAgeingDict.items()))
                self.CQTaskAgeingDict.update(ageingList)

                if(self.__CQAgeingThreshold in list(self.CQTaskAgeingDict.values())):
                    self._AgedTaskID = ([i for i, j in list(self.CQTaskAgeingDict.items()) if j == self.__CQAgeingThreshold])
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CQ_TASK_AGEING_DICT(self.CQTaskAgeingDict))
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_AGED_OUT(self._AgedTaskID, self.__CQAgeingThreshold))
                    self._AgedOut = True
                    raise ValidationError.CVFGenericExceptions(self.fn, self.STD_LOG_TASK_AGED_OUT(self._AgedTaskID, self.__CQAgeingThreshold))

            self.CQGetPendingTasksDump()
        self.FUNCTION_EXIT("Cmd45")

    #def Cmd45(self, StartBlockAddress):
        #"""
        #CMD45 - Q_Task_Info_B
        #"""
        #self.FUNCTION_ENTRY("Cmd45")
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CMD45_ARGS(StartBlockAddress))

        #try:
            #CMD45 = sdcmdWrap.QueueTaskInfoB(uiStartBlockAddress = StartBlockAddress)
            #self.noiseLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD45.pyResponseData.r1Response.uiCardStatus))
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CMD45_FAILED(StartBlockAddress))
            #if self.__CMD44TaskID != None:
                #self.CQTaskDetails[self.__CMD44TaskID] = {}
            #self.__CMD44TaskID = None           # Used for ageing. Clearing it in failure
            #self.ErrorPrint(exc)
            #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        #self.decodedR1response = self.DecodeR1Response(CMD45.pyResponseData.r1Response.uiCardStatus)

        #TaskID = self.__CMD44TaskID
        #self.__CMD44TaskID = None

        #if TaskID != None:
            #self.CQTaskDetails[TaskID].update({"LBA": hex(StartBlockAddress)})
            #self.TasksQueued += 1

            #if(self.CQTaskDetails[TaskID]["Direction"]) == 0:
                #self.WriteTasksQueued += 1
            #elif(self.CQTaskDetails[TaskID]["Direction"]) == 1:
                #self.ReadTasksQueued += 1

            #if self._CQDevConfigDict["Mode"] == "Sequential":
                #self.CQTaskAgeingDict["Task%d" % TaskID] = "InQ"
            #else:
                #self.CQTaskAgeingDict["Task%d" % TaskID] = 0

                #ageingList = collections.OrderedDict((taskit, ageingcount + 1) if(type(ageingcount) == int) else(
                    #taskit, ageingcount) for taskit, ageingcount in  self.CQTaskAgeingDict.items())
                #self.CQTaskAgeingDict.update(ageingList)

                #if(self.__CQAgeingThreshold in self.CQTaskAgeingDict.values()):
                    #self._AgedTaskID = ([i for i, j in self.CQTaskAgeingDict.items() if j == self.__CQAgeingThreshold])
                    #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CQ_TASK_AGEING_DICT(self.CQTaskAgeingDict))
                    #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_AGED_OUT(self._AgedTaskID, self.__CQAgeingThreshold))
                    #self._AgedOut = True
                    #raise ValidationError.TestFailError(self.fn, self.STD_LOG_TASK_AGED_OUT(self._AgedTaskID, self.__CQAgeingThreshold))

            #self.CQGetPendingTasksDump()
        #self.FUNCTION_EXIT("Cmd45")
        #return CMD45


    def Cmd46(self, TaskID, Pattern = 0, StartBlockAddr = 0, NumBlocks = 0, DoCompare = 0, UseCmd12 = False, ReadDataBuffer = None,
                argument = None, lbaTag = False, SequenceTag = None, SequenceNumber = 0):
        """
        CMD46: Q_RD_Task
        Description: To perform read operation for the specified task
        """
        self.FUNCTION_ENTRY("Cmd46")
        self.__responseDataBuf.Fill(value = 0x0)
        if(argument == None):
            arg = ((TaskID & 0x1F) << 16)
        else:
            arg = argument
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD46[Q_RD_Task]: Argument = 0x%X" % arg)
        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 46, argument = arg,
                                                            responseType = sdcmdWrap.TYPE_RESP._R1,
                                                            responseData = self.__responseDataBuf,
                                                            dataMode = sdcmdWrap.DATA_TRANS_.DATA_MULTREAD)

        commandDefinitionObj.flags.DoSendStatus = True
        commandDefinitionObj.flags.useCmd12 = UseCmd12
        commandDefinitionObj.flags.AnalyzeResponse = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = NumBlocks
        commandDataDefinitionObj.uiBlockLen = 512
        commandDataDefinitionObj.address = StartBlockAddr

        if ReadDataBuffer != None:
            self.noiseLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD46[Q_RD_Task]: User defined data buffer used")
            commandDataDefinitionObj.ptrBuffer = ReadDataBuffer
            commandDataDefinitionObj.uiDataPattern = 3
        else:
            self.noiseLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD46[Q_RD_Task]: Data Pattern used = %d" % Pattern)
            commandDataDefinitionObj.uiDataPattern = Pattern
            commandDataDefinitionObj.bCompareData = DoCompare
            commandDataDefinitionObj.aIsSectorTag = lbaTag
            if SequenceTag != None:
                commandDataDefinitionObj.bSeqTagEnable = SequenceTag
                commandDataDefinitionObj.uiSeqTagNumber = SequenceNumber

            if(Pattern == 6):
                commandDataDefinitionObj.uiAnyWordPattern = self._anyWord

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD46[Q_RD_Task]: Passed with R1 type response: %s\n" % self.decodedR1response)

        if(self.CQTaskDetails[TaskID]["Direction"]) == 1:
            self.CQTaskDetails[TaskID]["Exe"] = "InDataTx"

        if self._CQDevConfigDict["Mode"] == "Voluntary" and self.CQTaskAgeingDict["Task%d" % TaskID] == "Rdy":
            self.CQTaskAgeingDict["Task%d" % TaskID] = "NQ"

        if self._CQDevConfigDict["Mode"] == "Sequential" and self.CQTaskAgeingDict["Task%d" % TaskID] == "InQ":
            self.CQTaskAgeingDict["Task%d" % TaskID] = "NQ"
        self.CQTaskAgeingDict_Dump()

        self.FUNCTION_EXIT("Cmd46")
        return self.__responseDataBuf


    #def Cmd46(self, TaskID, StartBlockAddr, blockCount, NoData, BufObj, Pattern = 0, DoCompare = 0, lbaTag = False,
              #SequenceTag = None, SequenceNumber = 0):
        #"""
        #CMD46 - Q_RD_Task
        #"""
        #self.FUNCTION_ENTRY("Cmd46")

        #if (DoCompare == 1) and (BufObj == None):
            #NoData = False
            #BufObj = ServiceWrap.Buffer.CreateBuffer(blockCount, patternType = ServiceWrap.ALL_0, isSector = True)

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CMD46_ARGS(TaskID, blockCount, NoData, BufObj, Pattern))

        #try:
            #CMD46 = sdcmdWrap.QueueReadTaskCmd(uiTaskID = TaskID, blockCount = blockCount, bNoData = NoData,
                                               #pBufObj = BufObj, blockLength = 512, uiPattern = Pattern)
            #self.noiseLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD46.pyResponseData.r1Response.uiCardStatus))
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.ErrorPrint(exc)
            #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        #if DoCompare == 1:
            #self.Compare(readBuffer = BufObj, startLBA = StartBlockAddr, blockCount = blockCount, Pattern = Pattern,
                         #LbaTag = lbaTag, SeqTag = SequenceTag, SeqNumber = SequenceNumber)

        #self.decodedR1response = self.DecodeR1Response(CMD46.pyResponseData.r1Response.uiCardStatus)

        #if(self.CQTaskDetails[TaskID]["Direction"]) == 1:
            #self.CQTaskDetails[TaskID]["Exe"] = "InDataTx"

        #if self._CQDevConfigDict["Mode"] == "Voluntary" and self.CQTaskAgeingDict["Task%d" % TaskID] == "Rdy":
            #self.CQTaskAgeingDict["Task%d" % TaskID] = "NQ"

        #if self._CQDevConfigDict["Mode"] == "Sequential" and self.CQTaskAgeingDict["Task%d" % TaskID] == "InQ":
            #self.CQTaskAgeingDict["Task%d" % TaskID] = "NQ"

        #self.CQTaskAgeingDict_Dump()
        #self.FUNCTION_EXIT("Cmd46")
        #return CMD46


    def Cmd47(self, TaskID, Pattern = 0, StartBlockAddr = 0, NumBlocks = 0, UseCmd12 = False, WriteDataBuffer = None, argument = None,
                lbaTag = False, SequenceTag = None, SequenceNumber = 0):
        """
        CMD47: Q_WR_Task
        Description: To perform write operation for the specified task
        """
        self.FUNCTION_ENTRY("Cmd47")
        self.__responseDataBuf.Fill(value = 0x0)
        if argument == None:
            arg = ((TaskID & 0x1F) << 16)
        else:
            arg = argument
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD47[Q_WR_Task] : Argument = 0x%X" % arg)
        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 47, argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_MULTWRITE)

        commandDefinitionObj.flags.DoSendStatus = True
        commandDefinitionObj.flags.useCmd12 = UseCmd12
        commandDefinitionObj.flags.AnalyzeResponse = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = NumBlocks
        commandDataDefinitionObj.uiBlockLen = 512
        commandDataDefinitionObj.address = StartBlockAddr

        if (WriteDataBuffer != None):
            self.noiseLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD47[Q_WR_Task] : User defined data buffer used")
            commandDataDefinitionObj.ptrBuffer = WriteDataBuffer
            commandDataDefinitionObj.uiDataPattern = 3
        else:
            self.noiseLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD47[Q_WR_Task] : Data Pattern used = %d" % Pattern)
            commandDataDefinitionObj.uiDataPattern = Pattern
            commandDataDefinitionObj.aIsSectorTag = lbaTag
            if SequenceTag != None:
                commandDataDefinitionObj.bSeqTagEnable = SequenceTag
                commandDataDefinitionObj.uiSeqTagNumber = SequenceNumber

            if(Pattern == 6):
                commandDataDefinitionObj.uiAnyWordPattern = self._anyWord

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)

        if(self.CQTaskDetails[TaskID]["Direction"]) == 0:
            self.CQTaskDetails[TaskID]["Exe"] = "InDataTx"

        if self._CQDevConfigDict["Mode"] == "Voluntary" and self.CQTaskAgeingDict["Task%d" % TaskID] == "Rdy":
            self.CQTaskAgeingDict["Task%d" % TaskID] = "NQ"

        if self._CQDevConfigDict["Mode"] == "Sequential" and self.CQTaskAgeingDict["Task%d" % TaskID] == "InQ":
            self.CQTaskAgeingDict["Task%d" % TaskID] = "NQ"
        self.CQTaskAgeingDict_Dump()

        self.FUNCTION_EXIT("Cmd47")
        return self.__responseDataBuf


    #def Cmd47(self, TaskID, StartBlockAddr, blockCount, NoData, BufObj, Pattern = 0, lbaTag = False, SequenceTag = None, SequenceNumber = 0):
        #"""
        #CMD47 - Q_WR_Task
        #"""
        #self.FUNCTION_ENTRY("Cmd47")

        #if (lbaTag == True) or (SequenceTag == True):
            #if BufObj == None:
                #NoData = False
                #BufObj = ServiceWrap.Buffer.CreateBuffer(blockCount, patternType = ServiceWrap.ALL_0)
            #self.FillBufferWithTag(BufObj, StartBlockAddr, blockCount, Pattern, lbaTag, SequenceTag, SeqNumber = SequenceNumber)

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CMD47_ARGS(TaskID, blockCount, NoData, BufObj, Pattern))

        #try:
            #CMD47 = sdcmdWrap.QueueWriteTaskCmd(uiTaskID = TaskID, blockCount = blockCount,
                                                #bNoData = NoData, pBufObj = BufObj,
                                                #blockLength = 512, uiPattern = Pattern)
            #self.noiseLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD47.pyResponseData.r1Response.uiCardStatus))
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.ErrorPrint(exc)
            #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        #self.decodedR1response = self.DecodeR1Response(CMD47.pyResponseData.r1Response.uiCardStatus)

        #if(self.CQTaskDetails[TaskID]["Direction"]) == 0:
            #self.CQTaskDetails[TaskID]["Exe"] = "InDataTx"

        #if self._CQDevConfigDict["Mode"] == "Voluntary" and self.CQTaskAgeingDict["Task%d" % TaskID] == "Rdy":
            #self.CQTaskAgeingDict["Task%d" % TaskID] = "NQ"

        #if self._CQDevConfigDict["Mode"] == "Sequential" and self.CQTaskAgeingDict["Task%d" % TaskID] == "InQ":
            #self.CQTaskAgeingDict["Task%d" % TaskID] = "NQ"

        #self.CQTaskAgeingDict_Dump()
        #self.FUNCTION_EXIT("Cmd47")
        #return CMD47


###----------------------------- Class 1 Command Queue Function Commands End -----------------------------###

###----------------------------- Class 2 Block Read Start -----------------------------###

    def Cmd16(self, BlockLength):
        """
        CMD16 - SET_BLOCK_LENGTH
        """
        self.FUNCTION_ENTRY("Cmd16")
        self.__responseDataBuf.Fill(value = 0x0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "BlockLength is set to - %s" % BlockLength)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 16,
                                                           argument = BlockLength,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf)
        commandDefinitionObj.flags.DoSendStatus = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card-Status : %s" % self.decodedR1response)
        self.FUNCTION_EXIT("Cmd16")
        return self.__responseDataBuf

    # def Cmd16(self, BlockLength = 512):
    #     """
    #     CMD16 - SET_BLOCK_LENGTH
    #     """
    #     self.FUNCTION_ENTRY("Cmd16")
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('BlockLength is set to ', BlockLength))

    #     try:
    #         CMD16 = sdcmdWrap.SDSetBlockLength(sdr_blockLength = BlockLength)   # For HW
    #         #CMD16 = sdcmdWrap.SDSetBlockLength(uiBlockLength = BlockLength)     # For model
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         self.ErrorPrint(exc)
    #         raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD16.pyResponseData.r1Response.uiCardStatus))

    #     self.FUNCTION_EXIT("Cmd16")
    #     return CMD16

    def Cmd17(self, startLbaAddress, readDataBuffer):
        """
        CMD17 - READ_SINGLE_BLOCK
        """
        self.FUNCTION_ENTRY("Cmd17")
        self.__responseDataBuf.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 17,
                                                           argument = startLbaAddress,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_READ)
        commandDefinitionObj.flags.DoSendStatus = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = 1
        commandDataDefinitionObj.uiBlockLen = 512
        commandDataDefinitionObj.ptrBuffer = readDataBuffer
        #commandDataDefinitionObj.dataPattern = Pattern
        #commandDataDefinitionObj.compareData = DoCompare

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R1 type response : %s" % self.decodedR1response)
        self.FUNCTION_EXIT("Cmd17")

    # def Cmd17(self, StartLBA, NoData = True, RDBuff = None, Pattern = 0xFFFFFFFE, blockLen = 512):
    #     """
    #     CMD17 - Read_Single_Block
    #     """
    #     self.FUNCTION_ENTRY("Cmd17")
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Start LBA is', StartLBA))
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('NoDataMode is', NoData))

    #     if(NoData == False and RDBuff == None):
    #         RDBuff =  ServiceWrap.Buffer.CreateBuffer(blockLen, patternType = ServiceWrap.ALL_0, isSector = False)
    #         self.FUNCTION_EXIT("Read-Data-Buffer")

    #     try:
    #         CMD17 = sdcmdWrap.ReadSingleBlock(startLba = StartLBA, bNoData = NoData,
    #                                           szBuffer = RDBuff, uiPattern = Pattern,
    #                                           blockLength = blockLen)
    #         self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Data Tracking', CMD17.GetVersionDTInfo()))
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         self.ErrorPrint(exc)
    #         raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD17.pyResponseData.r1Response.uiCardStatus))

    #     self.FUNCTION_EXIT("Cmd17")
    #     return CMD17


    #def Cmd18(self, StartLba, BlockCount, NoData = True, RDBuff = None, StopTransmission = True, extraInfo = None,
              #Pattern = 0xFFFFFFFE, blockLen = 512):
        #"""
        #CMD18 - Read_Multiple_Block
        #"""
        #if gvar.GlobalConstants.SKIP_READ == True:
            #self.CARD_OUT_OF_RANGE_Validation(StartLba = StartLba, BlockCount = BlockCount, Cmd = "CMD18")
            #return

        #self.FUNCTION_ENTRY("Cmd18")
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Start LBA: 0x%X, block Count: 0x%X, NoDataMode: %s"
                     #% (StartLba, BlockCount, NoData))

        #if(NoData == False and RDBuff == None):
            #BuffLen = (blockLen * BlockCount)
            #RDBuff =  ServiceWrap.Buffer.CreateBuffer(BuffLen, patternType = ServiceWrap.ALL_0, isSector = False)
        ## TOBEDONE: CVF internally changes the startLba and blockCount values. So getting out of range error.
        #try:
            #if extraInfo == None:
                #CMD18 = sdcmdWrap.ReadMultipleBlocks(startLba = StartLba, blockCount = BlockCount,
                                                     #bNoData = NoData, szBuffer = RDBuff,
                                                     #bStopTransmission = StopTransmission,
                                                     #uiPattern = Pattern, blockLength = blockLen)
            #else:
                #CMD18 = sdcmdWrap.ReadMultipleBlocks(startLba = StartLba, blockCount = BlockCount,
                                                     #bNoData = NoData, szBuffer = RDBuff,
                                                     #bStopTransmission = StopTransmission, extraInfo = extraInfo,
                                                     #uiPattern = Pattern, blockLength = blockLen)

            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Data Tracking', CMD18.GetVersionDTInfo()))
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.ErrorPrint(exc)
            #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD18.pyResponseData.r1Response.uiCardStatus))

        #self.FUNCTION_EXIT("Cmd18")
        #return CMD18

    def Cmd18(self, startLbaAddress, transferLen, readDataBuffer):
        """
        CMD18 - Read_Multiple_Block
        """
        self.FUNCTION_ENTRY("Cmd18")
        self.__responseDataBuf.Fill(value = 0x0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Start LBA: 0x%X, block Count: 0x%X" % (startLbaAddress, transferLen))

        if self.__spiMode != True:
            commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = sdcmdWrap._CARD_COMMAND_._READ_MULTIPLE_BLOCK,
                                                               argument = startLbaAddress,
                                                               responseType = sdcmdWrap.TYPE_RESP._R1,
                                                               responseData = self.__responseDataBuf,
                                                               dataMode = sdcmdWrap.DATA_TRANS_.DATA_MULTREAD)
            commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
            commandDataDefinitionObj.dwBlockCount = transferLen
            commandDataDefinitionObj.uiBlockLen = 512
            commandDataDefinitionObj.ptrBuffer = readDataBuffer
            #commandDataDefinitionObj.dataPattern = Pattern
            #commandDataDefinitionObj.compareData = DoCompare
            commandDefinitionObj.flags.DoSendStatus = True

            try:
                sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.ErrorPrint(exc)
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DecodedR1Response = %s" % self.DecodeR1Response(self.__responseDataBuf))
        else:
            commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = sdcmdWrap._CARD_COMMAND_._READ_MULTIPLE_BLOCK,
                                                               argument = startLbaAddress,
                                                               responseType = sdcmdWrap.TYPE_RESP._R1,
                                                               responseData = self.__responseDataBuf,
                                                               dataMode = sdcmdWrap.DATA_TRANS_.DATA_MULTREAD)
            commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
            commandDataDefinitionObj.dwBlockCount = transferLen
            commandDataDefinitionObj.uiBlockLen = 512
            commandDataDefinitionObj.ptrBuffer = readDataBuffer

            try:
                sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.ErrorPrint(exc)
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DecodedR1Response = %s" % self.DecodeR1Response(self.__responseDataBuf))
        self.FUNCTION_EXIT("Cmd18")

    def Cmd18WithPatternCompare(self, StartLbaAddress, NumBlocks, Pattern, ReadDataBuffer = None, UseCmd12=True, lbaTag = False, SequenceTag = None, SequenceNumber = 0):
        """
        CMD18 - READ_MULTI_BLOCK with pattern. Used for verifying data written in CQ mode
        """
        if gvar.GlobalConstants.SKIP_READ == True:
            self.CARD_OUT_OF_RANGE_Validation(StartLba = StartLbaAddress, BlockCount = NumBlocks, Cmd = "CMD18")
            return

        self.FUNCTION_ENTRY("Cmd18WithPatternCompare")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "LEGACY READ (CMD18)--> Start Block Addr = 0x%X, NumBlocks = 0x%X, Pattern = %s" %
                     (StartLbaAddress, NumBlocks, self.GetPatternEnumFromNum(Pattern)))

        if (ReadDataBuffer != None):
            self.__responseDataBuf.Fill(value = 0x0)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD18[READ_MULTIPLE_BLOCK]: User defined data buffer used")

            commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = sdcmdWrap._CARD_COMMAND_._READ_MULTIPLE_BLOCK,
                                                               argument = StartLbaAddress,
                                                               responseType = sdcmdWrap.TYPE_RESP._R1,
                                                               responseData = self.__responseDataBuf,
                                                               dataMode = sdcmdWrap.DATA_TRANS_.DATA_MULTREAD)
            commandDefinitionObj.flags.useCmd12 = UseCmd12

            commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
            commandDataDefinitionObj.dwBlockCount = NumBlocks
            commandDataDefinitionObj.uiBlockLen = 512
            commandDataDefinitionObj.address = StartLbaAddress
            commandDataDefinitionObj.ptrBuffer = ReadDataBuffer

            try:
                sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.ErrorPrint(exc)
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DecodedR1Response = %s" % self.DecodeR1Response(self.__responseDataBuf))
        else:
            try:
                if SequenceTag != None:
                    patternGen = PatternGen.PatternGen(self.vtfContainer,
                                                       writePattern = self.GetPatternEnumFromNum(Pattern),
                                                       doPerformance = False,
                                                       iddMsrSampleRate = sdcmdWrap.EIddMsrSampleRate.ONE_MS,
                                                       iddNumOfSamples = 0, doLatency = False,
                                                       doIddMeasurment = False,
                                                       doCompare = True, lbaTag = lbaTag,
                                                       anyWord = self._anyWord, SeqTag = SequenceTag,
                                                       SeqNumber = SequenceNumber, enable_logging = False)
                else:
                    patternGen = PatternGen.PatternGen(self.vtfContainer,
                                                       writePattern = self.GetPatternEnumFromNum(Pattern),
                                                       doCompare = True, lbaTag = lbaTag,
                                                       anyWord = self._anyWord, enable_logging = False)
                MultiRead = patternGen.MultipleRead(address = StartLbaAddress, blockCount = NumBlocks)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Performance of Multiple Read is %sMB" % (float(MultiRead.perfReadWrite.perfResults) / (1000 * 1000)))
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.ErrorPrint(exc)
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.FUNCTION_EXIT("Cmd18")


    def Cmd19(self):
        """
        CMD19 - SEND_TUNING_PATTERN
        """
        self.FUNCTION_ENTRY("Cmd19")
        self.__responseDataBuf.Fill(value = 0x0)
        self.__tuningBuf = ServiceWrap.Buffer.CreateBuffer(64, patternType = 0x00, isSector = False)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 19,
                                                           argument = 0x0,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_READ)
        cmdFlags = sdcmdWrap.CommandFlags()
        cmdFlags.DoSendStatus = True
        commandDefinitionObj.flags = cmdFlags

        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = 1
        commandDataDefinitionObj.uiBlockLen = 64
        commandDataDefinitionObj.ptrBuffer = self.__tuningBuf

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.__tuningBuf.PrintToLog()
        self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R1 type response : %s" % self.decodedR1response)
        self.FUNCTION_EXIT("Cmd19")

    # def Cmd19(self):
    #     """
    #     CMD19 - SEND_TUNING_BLOCK
    #     """
    #     self.FUNCTION_ENTRY("Cmd19")

    #     try:
    #         CMD19 = sdcmdWrap.SendTuningBlock()
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         self.ErrorPrint(exc)
    #         raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD19.pyResponseData.r1Response.uiCardStatus))

    #     self.FUNCTION_EXIT("Cmd19")
    #     return CMD19


    def Cmd20(self, Argument):
        """
        CMD20 - SPEED_CLASS_CONTROL
        """
        self.FUNCTION_ENTRY("Cmd20")

        self.__responseDataBuf.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 20,
                                                           argument = Argument,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1b,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
        cmdFlags = sdcmdWrap.CommandFlags()
        cmdFlags.DoSendStatus = True
        cmdFlags.AnalyzeResponse = True
        cmdFlags.DoSendCmd12InError = True
        commandDefinitionObj.flags = cmdFlags

        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)

        self.FUNCTION_EXIT("Cmd20")
        return self.__responseDataBuf

    def Cmd22(self, AddressExtension = 0x0):
        """
        CMD22 - ADDRESS_EXTENSION
        """
        self.FUNCTION_ENTRY("Cmd22")
        self.__responseDataBuf.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 22,
                                                           argument = AddressExtension,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
        cmdFlags = sdcmdWrap.CommandFlags()
        cmdFlags.DoSendStatus = True
        commandDefinitionObj.flags = cmdFlags

        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R1 type response : %s" % self.decodedR1response)
        self.FUNCTION_EXIT("Cmd22")

    def Cmd23(self, blockCount):
        """
        CMD23 - SET_BLOCK_COUNT
        """
        self.FUNCTION_ENTRY("Cmd23")
        self.__responseDataBuf.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 23,
                                                           argument = blockCount,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
        cmdFlags = sdcmdWrap.CommandFlags()
        cmdFlags.DoSendStatus = True
        commandDefinitionObj.flags = cmdFlags

        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R1 type response : %s" % self.decodedR1response)
        self.FUNCTION_EXIT("Cmd23")

    # def Cmd23(self, BlockCount = 1):
    #     """
    #     CMD23
    #     """
    #     self.FUNCTION_ENTRY("Cmd23")
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('BlockCount set to ', BlockCount))

    #     try:
    #         CMD23 = sdcmdWrap.SetBlockCount(blockCount = BlockCount)
    #         self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Card-Req-ui32Args', CMD23.pyCmdObject.commandData.ui32Args))
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         self.ErrorPrint(exc)
    #         raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD23.pyResponseData.r1Response.uiCardStatus))

    #     self.FUNCTION_EXIT("Cmd23")
    #     return CMD23

###---------------------------------- Class 2 Block Read End -----------------------------------------------------------------------###

###---------------------------------- Class 4 Block Write Start -----------------------------------------------------------------------###

    def Cmd24(self, startLbaAddress, writeDataBuffer):
        """
        CMD24 - WRITE_BLOCK
        """
        self.FUNCTION_ENTRY("Cmd24")
        self.__responseDataBuf.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 24,
                                                           argument = startLbaAddress,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_WRITE)
        commandDefinitionObj.flags.DoSendStatus = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = 1
        commandDataDefinitionObj.uiBlockLen = 512
        commandDataDefinitionObj.ptrBuffer = writeDataBuffer

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        self.debugLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R1 type response : %s" % self.decodedR1response)
        self.FUNCTION_EXIT("Cmd24")

    # def Cmd24(self, StartLBA, NoData = True, WRBuff = None, Pattern = 0xFFFFFFFE, blockLen = 512):
    #     """
    #     CMD24 - Write_Single_Block
    #     """
    #     self.FUNCTION_ENTRY("Cmd24")
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Start LBA is', StartLBA))
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('NoData Mode is', NoData))

    #     if(NoData == False and WRBuff == None):
    #         WRBuff =  ServiceWrap.Buffer.CreateBuffer(blockLen, patternType = ServiceWrap.ALL_0, isSector = False)

    #     try:
    #         CMD24 = sdcmdWrap.WriteSingleBlock(startLba = StartLBA, bNoData = NoData,
    #                                            szBuffer = WRBuff, uiPattern = Pattern,
    #                                            blockLength = blockLen)
    #         self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Data Tracking', CMD24.GetVersionDTInfo()))
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         self.ErrorPrint(exc)
    #         raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD24.pyResponseData.r1Response.uiCardStatus))

    #     self.FUNCTION_EXIT("Cmd24")
    #     return CMD24


    #def Cmd25(self, StartLba, BlockCount, NoData = True, WRBuff = None, StopTransmission = True, extraInfo = None,
              #Pattern = 0xFFFFFFFE, blockLen = 512):
        #"""
        #CMD25 - Write_Multiple_Block
        #"""
        #if gvar.GlobalConstants.SKIP_WRITE == True:
            #self.CARD_OUT_OF_RANGE_Validation(StartLba = StartLba, BlockCount = BlockCount, Cmd = "CMD25")
            #return

        #self.FUNCTION_ENTRY("Cmd25")
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Start LBA: 0x%X, block Count: 0x%X, NoDataMode: %s"
                     #% (StartLba, BlockCount, NoData))

        #if(NoData == False and WRBuff == None):
            #BuffLen = (BlockCount * blockLen)
            #WRBuff = ServiceWrap.Buffer.CreateBuffer(BuffLen, patternType = sdcmdWrap.Pattern.ALL_ONE, isSector = False)

        #try:
            #if extraInfo == None:
                #CMD25 = sdcmdWrap.WriteMultipleBlocks(startLba = StartLba, blockCount = BlockCount,
                                                      #bNoData = NoData, szBuffer = WRBuff,
                                                      #bStopTransmission = StopTransmission,
                                                      #uiPattern = Pattern, blockLength = blockLen)
            #else:
                #CMD25 = sdcmdWrap.WriteMultipleBlocks(startLba = StartLba, blockCount = BlockCount,
                                                      #bNoData = NoData, szBuffer = WRBuff,
                                                      #bStopTransmission = StopTransmission, extraInfo = extraInfo,
                                                      #uiPattern = Pattern, blockLength = blockLen)

            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Data Tracking', CMD25.GetVersionDTInfo()))
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.ErrorPrint(exc)
            #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD25.pyResponseData.r1Response.uiCardStatus))

        #if((NoData == False) and (LogDump_Dis == True)):
            #WRBuff.PrintToLog()

        #self.FUNCTION_EXIT("Cmd25")
        #return CMD25

    def Cmd25(self, startLbaAddress, transferLen, writeDataBuffer):
        """
        CMD25 - WRITE_MULTIPLE_BLOCK
        """
        self.FUNCTION_ENTRY("Cmd25")
        self.__responseDataBuf.Fill(value = 0x0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Start LBA: 0x%X, block Count: 0x%X" % (startLbaAddress, transferLen))

        if self.__spiMode != True:
            commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = sdcmdWrap._CARD_COMMAND_._WRITE_MULTIPLE_BLOCK,
                                                               argument = startLbaAddress,
                                                               responseType = sdcmdWrap.TYPE_RESP._R1,
                                                               responseData = self.__responseDataBuf,
                                                               dataMode = sdcmdWrap.DATA_TRANS_.DATA_MULTWRITE)
            commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
            commandDataDefinitionObj.dwBlockCount = transferLen
            commandDataDefinitionObj.uiBlockLen = 512
            commandDataDefinitionObj.ptrBuffer = writeDataBuffer
            commandDefinitionObj.flags.DoSendStatus = True

            try:
                sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.ErrorPrint(exc)
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DecodedR1Response = %s" % self.DecodeR1Response(self.__responseDataBuf))
        else:
            commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = sdcmdWrap._CARD_COMMAND_._WRITE_MULTIPLE_BLOCK,
                                                               argument = startLbaAddress,
                                                               responseType = sdcmdWrap.TYPE_RESP._R1,
                                                               responseData = self.__responseDataBuf,
                                                               dataMode = sdcmdWrap.DATA_TRANS_.DATA_MULTWRITE)
            commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
            commandDataDefinitionObj.dwBlockCount = transferLen
            commandDataDefinitionObj.uiBlockLen = 512
            commandDataDefinitionObj.ptrBuffer = writeDataBuffer

            try:
                sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.ErrorPrint(exc)
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DecodedR1Response = %s" % self.DecodeR1Response(self.__responseDataBuf))
        self.FUNCTION_EXIT("Cmd25")

    def Cmd25WithPatternCompare(self, StartLbaAddress, NumBlocks, Pattern, WriteDataBuffer = None, UseCmd12=True, lbaTag = False, SequenceTag = None, SequenceNumber = 0):
        """
        CMD25 - WRITE_MULTIPLE_BLOCK with pattern. Used for writing data in Legacy and then reading the same data in CQ mode.
        Pattern - sdcmdWrap.Pattern......
        """
        if gvar.GlobalConstants.SKIP_WRITE == True:
            self.CARD_OUT_OF_RANGE_Validation(StartLba = StartLbaAddress, BlockCount = NumBlocks, Cmd = "CMD25")
            return

        self.FUNCTION_ENTRY("Cmd25WithPatternCompare")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "LEGACY WRITE (CMD25)--> Start Block Addr = 0x%X, NumBlocks = 0x%X, Pattern = %s"
                     % (StartLbaAddress, NumBlocks, self.GetPatternEnumFromNum(Pattern)))

        if (WriteDataBuffer != None):
            self.__responseDataBuf.Fill(value = 0x0)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD25[WRITE_MULTIPLE_BLOCK]: User defined data buffer used")
            commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = sdcmdWrap._CARD_COMMAND_._WRITE_MULTIPLE_BLOCK,
                                                               argument = StartLbaAddress,
                                                               responseType = sdcmdWrap.TYPE_RESP._R1,
                                                               responseData = self.__responseDataBuf,
                                                               dataMode = sdcmdWrap.DATA_TRANS_.DATA_MULTWRITE)
            commandDefinitionObj.flags.useCmd12 = UseCmd12

            commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
            commandDataDefinitionObj.dwBlockCount = NumBlocks
            commandDataDefinitionObj.uiBlockLen = 512
            commandDataDefinitionObj.address = StartLbaAddress
            commandDataDefinitionObj.ptrBuffer = WriteDataBuffer

            try:
                sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.ErrorPrint(exc)
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DecodedR1Response = %s" % self.DecodeR1Response(self.__responseDataBuf))
        else:
            try:
                if SequenceTag != None:
                    patternGen = PatternGen.PatternGen(self.vtfContainer,
                                                       writePattern = self.GetPatternEnumFromNum(Pattern),
                                                       doPerformance = False,
                                                       iddMsrSampleRate = sdcmdWrap.EIddMsrSampleRate.ONE_MS,
                                                       iddNumOfSamples = 0, doLatency = False,
                                                       doIddMeasurment = False,
                                                       doCompare = False, lbaTag = lbaTag,
                                                       anyWord = self._anyWord, SeqTag = SequenceTag,
                                                       SeqNumber = SequenceNumber, enable_logging = False)
                else:
                    patternGen = PatternGen.PatternGen(self.vtfContainer,
                                                       writePattern = self.GetPatternEnumFromNum(Pattern),
                                                       doCompare = False, lbaTag = lbaTag,
                                                       anyWord = self._anyWord)

                MultiWrite = patternGen.MultipleWrite(address = StartLbaAddress, blockCount = NumBlocks)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Performance of Multiple Write is %sMB" % (float(MultiWrite.perfReadWrite.perfResults) / (1000 * 1000)))
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.ErrorPrint(exc)
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.FUNCTION_EXIT("Cmd25WithPatternCompare")


    def Cmd26(self, ProgBuff):
        """
        CMD26: PROGRAM_CID (Reserved for Manufacturer)
        """
        self.__responseDataBuf.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 26,
                                                           argument = 0x00,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_WRITE)

        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = 1
        commandDataDefinitionObj.uiBlockLen = 16
        commandDataDefinitionObj.ptrBuffer = ProgBuff

        try:
            rc = sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            retValue = self.__responseDataBuf.GetData(0, 6)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD26 Passed with R1 type response:%s" % retValue)

    def Cmd27(self, ProgBuff):
        """
        CMD27 - PROGRAM_CSD
        """
        self.FUNCTION_ENTRY("Cmd27")
        self.__responseDataBuf.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 27,
                                                           argument = 0x00,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_WRITE)

        cmdFlags = sdcmdWrap.CommandFlags()
        cmdFlags.DoSendStatus = True
        cmdFlags.AnalyzeResponse=True
        commandDefinitionObj.flags = cmdFlags

        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = 1
        commandDataDefinitionObj.uiBlockLen = 16
        commandDataDefinitionObj.ptrBuffer = ProgBuff

        try:
            rc = sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            retValue = self.__responseDataBuf.GetData(0, 6)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.DecodeR1Response(R1_Response = self.__responseDataBuf)
        self.FUNCTION_EXIT("Cmd27")
        return retValue

    # def Cmd27(self, CsdRegister = None):
    #     """
    #     CMD27 - PROGRAM_CSD
    #     """
    #     self.FUNCTION_ENTRY("Cmd27")

    #     if CsdRegister == None:
    #         CsdRegister = sdcmdWrap.CSD_REGISTER_FIELD_STRUCT()
    #         CSD_STRUCT_VER = self.GetCSDStructVer()
    #         exec("CsdRegister.CsdRegisterFieldStructVer%d = sdcmdWrap.CSD_REGISTER_FIELD_STRUCT_VER%d()" % (CSD_STRUCT_VER, CSD_STRUCT_VER))
    #     try:
    #         CMD27 = sdcmdWrap.ProgramCsd(csdRegister = CsdRegister)
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         self.ErrorPrint(exc)
    #         raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD27.pyResponseData.r1Response.uiCardStatus))

    #     self.FUNCTION_EXIT("Cmd27")
    #     return CMD27

###----------------------------- Class 4 Block Write End -----------------------------###

###----------------------------- Class 5 Erase Start -----------------------------###

    def Cmd32(self, StartLBA):
        """
        CMD32: ERASE_WR_BLOCK_START_ADDRESS
        """
        self.FUNCTION_ENTRY("Cmd32")
        self.__responseDataBuf.Fill(value = 0x0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD32[ ERASE_WR_BLOCK_START_ADDRESS ] : Start LBA Address = 0x%X" % StartLBA)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 32, argument = StartLBA,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf)
        commandDefinitionObj.flags.DoSendStatus = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            self.__decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.FUNCTION_EXIT("Cmd32")
        return self.__responseDataBuf

    def Cmd33(self, EndLBA):
        """
        CMD33: ERASE_BLOCK_END_ADDRESS
        """
        self.FUNCTION_ENTRY("Cmd33")
        self.__responseDataBuf.Fill(value = 0x0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD33[ERASE_BLOCK_END_ADDRESS]: End LBA Address = 0x%X" % EndLBA)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 33, argument = EndLBA,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf)
        commandDefinitionObj.flags.DoSendStatus = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            self.__decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.FUNCTION_EXIT("Cmd33")
        return self.__responseDataBuf

    def Cmd38(self, expectPrgState = False):
        """
        CMD38: ERASE_COMMAND
        Description: This function will only do erase, not FULE and discard.
        """
        self.FUNCTION_ENTRY("Cmd38")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "EraseFunction is erase")

        r1btimeout = 250    # For all speedmodes
        if self.currCfg.variation.sdconfiguration in ["UHS104", "SDR104"]:
            r1btimeout = 2  # For 104 speedmode
        if expectPrgState:
            if self.currCfg.variation.sdconfiguration in ["HS", "LS"]:
                r1btimeout = 50
                time.sleep(1)
            else:
                r1btimeout = 1
                # This is added for checking current state in prg
                time.sleep(1)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 38, argument = 0,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1b,
                                                           responseData = self.__responseDataBuf,
                                                           R1bTimeout = r1btimeout #Time for Prg state in seconds
                                                           )
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            self.__decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Erasing the Card......")

            if (exc.GetErrorNumber() == 0x5 or exc.GetErrorNumber() == 0x25):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card is Busy programming, Continuing to Test..")
                self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure
                # For erase time out value "Number of write blocks to be erased * 250ms"
                if expectPrgState == True:
                    return self.GetCardStatus()  # For Immediate response
                else:
                    time.sleep(30)      # Delay added as erase takes some time for erase
            else:
                self.ErrorPrint(exc)
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.FUNCTION_EXIT("Cmd38")
        return self.__responseDataBuf

    def Cmd38_WithArg(self, arg = 0, expectPrgState = False, busyTimeout = 250):
        """
        CMD38: ERASE_COMMAND
        Arguments:
            arg : 1 for Discard, 2 for FULE, others for erase
        """
        self.FUNCTION_ENTRY("Cmd38_WithArg")

        r1btimeout = busyTimeout
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD38 Argument = 0x%X BusyTimeOut= %d ms" % (arg, busyTimeout))

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 38, argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1b,
                                                           responseData = self.__responseDataBuf,
                                                           R1bTimeout = r1btimeout #Time for Prg state in milliseconds
                                                           )
        commandDefinitionObj.flags.DoSendStatus = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            self.__decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Erasing the Card......")

            if (exc.GetErrorNumber() == 0x5 or exc.GetErrorNumber() == 0x25):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card is Busy programming, Continuing to Test..")
                self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure
            else:
                self.ErrorPrint(exc)
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.__decodedR1bresponse = self.DecodeR1Response(self.__responseDataBuf)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R1b type response:%s\n" % self.__decodedR1bresponse)

        if expectPrgState == True:
            return self.__responseDataBuf
        else:
            # Comes here in Legacy when busytimeout given as input is less and card is still in prg state. Keep sending CMD13 until the card is out of prg state
            # Comes here in case of CQ mode immediately after receiving the CMD38 R1 response.
                    # 1. Check for busytimeout status from host using GetDeviceBusyStatus API
                    # 2. Keep sending CMD13 until the card is out of prg

            timeout = 5         # 5 sec
            sleepTime = 0.250   # 250 ms
            count = int(old_div(timeout, sleepTime))

            while(count > 0):
                if ((self.currCfg.variation.cq == 1) and (self.pgnenable == 1)):
                    state = "CURRENT_STATE:CQ Tran"
                    busyStatusObj = sdcmdWrap.GetDeviceBusyStatus()
                    busyStatus = busyStatusObj.GetBusyStatus()
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_BUSY_STATUS_BY_HOST(busyStatus))
                    if(busyStatus == self.__errorCodes.CheckError('CARD_TIME_OUT_RCVD')): # If busy timed out
                        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Busy timeout received after timeout value %d ms..." % busyTimeout)
                        raise ValidationError.TestFailError(self.fn, "Busy timeout received after timeout value %d ms..." % busyTimeout)
                else:
                    state = "CURRENT_STATE:Tran"

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_CHECK_IF_CARD_IN_TRANS_STATE)
                resp = self.GetCardStatus()
                if(state in resp):
                    break
                time.sleep(sleepTime)
                count -= 1

            if (count == 0) and (state not in resp):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_CARD_NOT_MOVED_TO_TRANS_STATE)
                raise ValidationError.TestFailError(self.fn, self.GL_CARD_NOT_MOVED_TO_TRANS_STATE)

        self.FUNCTION_EXIT("Cmd38_WithArg")
        return self.__responseDataBuf


    #def Cmd32(self, StartLba):
        #"""
        #CMD32: ERASE_WR_BLOCK_START_ADDRESS
        #"""
        #self.FUNCTION_ENTRY("Cmd32")
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD32[ ERASE_WR_BLOCK_START_ADDRESS ] : Start LBA Address = 0x%X" % StartLba)

        #try:
            #CMD32 = sdcmdWrap.EraseWrBlkStart(uiStartLba = StartLba)
            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD32.pyResponseData.r1Response.uiCardStatus))
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.ErrorPrint(exc)
            #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        #self.FUNCTION_EXIT("Cmd32")
        #return CMD32


    #def Cmd33(self, EndLba):
        #"""
        #CMD33: ERASE_BLOCK_END_ADDRESS
        #"""
        #self.FUNCTION_ENTRY("Cmd33")
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD33[ERASE_BLOCK_END_ADDRESS]: End LBA Address = 0x%X" % EndLba)

        #try:
            #CMD33 = sdcmdWrap.EraseWrBlkEnd(uiEndLba = EndLba)
            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD33.pyResponseData.r1Response.uiCardStatus))
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.ErrorPrint(exc)
            #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        #self.FUNCTION_EXIT("Cmd33")
        #return CMD33


    #def Cmd38(self, StartLBA, EndLBA, EraseFunction = 0, expectPrgState = False):
        #"""
        #CMD38: ERASE_COMMAND
        #Note: Due to design limitation Erase command API signature takes dwStartLBA and dwEndLBA.
              #For HW, SDR would internally create and execute CMD32, CMD33 & CMD38 as part of this command.
              #Refer: RPG-54510. This Erase API is deprecated.
        #Arguments:
            #EraseFunction = 1    # Discard
            #EraseFunction = 2    # FULE
            #EraseFunction = Others    # Erase
        #"""
        #self.FUNCTION_ENTRY("Cmd38")

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: 0x%X" % ('StartLBA is', StartLBA))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: 0x%X" % ('EndLBA is', EndLBA))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('EraseFunction is', EraseFunction))
        ## EraseFunction - 1 means Discard, 2 means FULE, all other values are Erase.

        #try:
            #CMD38 = sdcmdWrap.Erase(dwStartLBA = StartLBA,
                                    #dwEndLBA = EndLBA,
                                    #uiEraseFunction = EraseFunction)
            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD38.pyResponseData.r1bResponse.uiCardStatus))
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD38[ ERASE_COMMAND ] Erasing the Card......")

            #if (exc.GetErrorNumber() == 0x5 or exc.GetErrorNumber() == 0x25):
                #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD38[ ERASE_COMMAND ] Card is Busy programming, Continuing to Test..")
                # self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure
                ## For erase time out value "Number of write blocks to be erased * 250ms"
                #if expectPrgState == True:
                    #return self.GetCardStatus()  # for Immediate response
                #else:
                    #time.sleep(30)      # Delay added as erase takes some time for erase
            #else:
                #self.ErrorPrint(exc)
                #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        #self.FUNCTION_EXIT("Cmd38")
        #return CMD38


    #def Cmd38_WithArg(self, StartLBA, EndLBA, EraseFunction = 0, expectPrgState = False, busyTimeout = 250):
        #"""
        #CMD38: ERASE_COMMAND
        #Arguments:
            #EraseFunction : 1 for Discard, 2 for FULE, others for erase
            #expectPrgState : True - Do not wait until card come to trans state,
                             #False - Wait and confim card came out from programming state to transfer state
            #busyTimeout : In milliseconds,
                #Timeout values are not internally calculated by CVF for this Erase cmd. (Please use EraseDiscardFule API for that)
                #Test must explicitly calculate these separately,

                #Default Timeout values in cvf.ini:
                    #discard_time_out_micro_sec = 250000
                    #erase_time_out_micro_sec = 1000000 (Test would have to calculate and set this parameter using ConfigParser
                                                        #object explicitly before issuing the Erase cmd)
                    #fule_time_out_micro_sec = 10000000
        #"""
        #self.FUNCTION_ENTRY("Cmd38_WithArg")

        ## Change default time out value in cvf.ini config file
        #TimeoutInMicrosec = busyTimeout * 1000
        #if EraseFunction == 1 and busyTimeout != 250:
            #self.Set_cvf_ini_File_Value(Name = "discard_time_out_micro_sec", Value = TimeoutInMicrosec)
        #elif EraseFunction == 2 and busyTimeout != 1000:
            #self.Set_cvf_ini_File_Value(Name = "fule_time_out_micro_sec", Value = TimeoutInMicrosec)
        #elif busyTimeout != 1000:
            #self.Set_cvf_ini_File_Value(Name = "erase_time_out_micro_sec", Value = TimeoutInMicrosec)

        #Function = {0: "erase", 1: "discard", 2: "FULE"}
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: 0x%X" % ('StartLBA is', StartLBA))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: 0x%X" % ('EndLBA is', EndLBA))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('EraseFunction is', Function[EraseFunction]))
        ## EraseFunction - 1 means Discard, 2 means FULE, all other values are Erase.

        #try:
            #CMD38 = sdcmdWrap.Erase(dwStartLBA = StartLBA, dwEndLBA = EndLBA, uiEraseFunction = EraseFunction)
            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD38.pyResponseData.r1bResponse.uiCardStatus))
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Erasing the Card......")

            #if (exc.GetErrorNumber() == 0x5 or exc.GetErrorNumber() == 0x25):
                #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card is Busy programming, Continuing to Test..")
                # self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure
                ## For erase time out value "Number of write blocks to be erased * 250ms"
            #else:
                #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed to Post the Command 38 to Threadpool. Exception Message is -> %s "
                             #% exc.GetFailureDescription())
                #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        #self.__decodedR1bresponse = self.DecodeR1Response(CMD38.pyResponseData.r1bResponse.uiCardStatus)
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R1b type response:%s\n" % self.__decodedR1bresponse)

        #if expectPrgState == True:
            #return CMD38
        #else:
            ## Comes here in Legacy when busytimeout given as input is less and card is still in prg state. Keep sending CMD13 until the card is out of prg state
            ## Comes here in case of CQ mode immediately after receiving the CMD38 R1 response.
                    ## 1. Check for busytimeout status from host using GetDeviceBusyStatus API
                    ## 2. Keep sending CMD13 until the card is out of prg

            #timeout = 5         # 5 sec
            #sleepTime = 0.250   # 250 ms
            #count = int(timeout / sleepTime)

            #while(count > 0):
                #if((self.currCfg.variation.cq == 1) and (self.pgnenable == 1)):
                    #state = "CURRENT_STATE:CQ Tran"
                    #busyStatusObj = sdcmdWrap.GetDeviceBusyStatus()
                    #busyStatus = busyStatusObj.GetBusyStatus()
                    #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_BUSY_STATUS_BY_HOST(busyStatus))
                    #if(busyStatus == self.__errorCodes.CheckError('CARD_TIME_OUT_RCVD')): # if busy timed out
                        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Busy timeout received after timeout value %d microsecond..." % busyTimeout)
                        #raise ValidationError.TestFailError(self.fn, "Busy timeout received after timeout value %d microsecond..." % busyTimeout)
                #else:
                    #state = "CURRENT_STATE:Tran"

                #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_CHECK_IF_CARD_IN_TRANS_STATE)
                #resp = self.GetCardStatus()
                #if(state in resp):
                    #break
                #time.sleep(sleepTime)
                #count -= 1

            #if (count == 0) and (state not in resp):
                #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_CARD_NOT_MOVED_TO_TRANS_STATE)
                #raise ValidationError.TestFailError(self.fn, self.GL_CARD_NOT_MOVED_TO_TRANS_STATE)

        #self.FUNCTION_EXIT("Cmd38_WithArg")
        #return CMD38

###----------------------------- Class 5 Erase End -----------------------------###


###----------------------------- Class 6 Block Oriented Write Protection Start -----------------------------###

    def Cmd28(self, StartLba):
        """
        CMD28: SET_WRITE_PROT
        """
        self.FUNCTION_ENTRY("Cmd28")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD28[SET_WRITE_PROT]: Start LBA Address = 0x%X" % StartLba)
        self.__responseDataBuf.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 28, argument = StartLba,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1b,
                                                           responseData = self.__responseDataBuf)
        commandDefinitionObj.flags.DoSendStatus = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            self.__decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.FUNCTION_EXIT("Cmd28")
        return self.__responseDataBuf


    # def Cmd28(self, StartLba):
    #     """
    #     CMD28: SET_WRITE_PROT
    #     """
    #     self.FUNCTION_ENTRY("Cmd28")
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD28[SET_WRITE_PROT]: Start LBA Address = 0x%X" % StartLba)

    #     try:
    #         CMD28 = sdcmdWrap.SetWriteProt(uiStartLba = StartLba)
    #         self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD28.pyResponseData.r1bResponse.uiCardStatus))
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         self.ErrorPrint(exc)
    #         raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    #     self.FUNCTION_EXIT("Cmd28")
    #     return CMD28

    def Cmd29(self, StartLba):
        """
        CMD29: CLR_WRITE_PROT
        """
        self.FUNCTION_ENTRY("Cmd29")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD29[CLR_WRITE_PROT]: Start LBA Address = 0x%X" % StartLba)
        self.__responseDataBuf.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 29, argument = StartLba,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1b,
                                                           responseData = self.__responseDataBuf)
        commandDefinitionObj.flags.DoSendStatus = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            self.__decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.FUNCTION_EXIT("Cmd29")
        return self.__responseDataBuf

    # def Cmd29(self, StartLba):
    #     """
    #     CMD29: CLR_WRITE_PROT
    #     """
    #     self.FUNCTION_ENTRY("Cmd29")
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD29[CLR_WRITE_PROT]: Start LBA Address = 0x%X" % StartLba)

    #     try:
    #         CMD29 = sdcmdWrap.ClrWriteProt(uiStartLba = StartLba)
    #         self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD29.pyResponseData.r1bResponse.uiCardStatus))
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         self.ErrorPrint(exc)
    #         raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    #     self.FUNCTION_EXIT("Cmd29")
    #     return CMD29

    def Cmd30(self, StartLba, readDataBuffer = None):
        """
        CMD30: SEND_WRITE_PROT
        """
        self.FUNCTION_ENTRY("Cmd30")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD30[SEND_WRITE_PROT]: Start LBA Address = 0x%X" % StartLba)
        self.__responseDataBuf.Fill(value = 0x0)
        if readDataBuffer == None:
            readDataBuffer = ServiceWrap.Buffer.CreateBuffer(0x1, 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 30, argument = StartLba,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_READ)
        commandDefinitionObj.flags.DoSendStatus = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = 1
        commandDataDefinitionObj.uiBlockLen = 512
        commandDataDefinitionObj.ptrBuffer = readDataBuffer

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            self.__decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.FUNCTION_EXIT("Cmd29")
        return self.__responseDataBuf

    # def Cmd30(self, StartLba):
    #     """
    #     CMD30: SEND_WRITE_PROT
    #     """
    #     self.FUNCTION_ENTRY("Cmd30")
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD30[SEND_WRITE_PROT]: Start LBA Address = 0x%X" % StartLba)

    #     try:
    #         CMD30 = sdcmdWrap.SendWriteProt(uiStartLba = StartLba)
    #         self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD30.pyResponseData.r1Response.uiCardStatus))
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         self.ErrorPrint(exc)
    #         raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    #     self.FUNCTION_EXIT("Cmd30")
    #     return CMD30

###----------------------------- Class 6 Block Oriented Write Protection End -----------------------------###


###----------------------------- Class 7 Lock Card Start -----------------------------###

    def Cmd42(self, dataBuffer, blkLen=0x200):
        """
        CMD42: LOCK_UNLOCK
        """
        self.FUNCTION_ENTRY("Cmd42")
        self.__responseDataBuf.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 42, argument = 0x00000000,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_WRITE)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = 1
        commandDataDefinitionObj.uiBlockLen = blkLen
        commandDataDefinitionObj.ptrBuffer = dataBuffer

        # Erase operation opcode(0x08) needs time delay
        Byte0 = dataBuffer.GetOneByteToInt(offset = 0)
        busydown = 0

        if ((Byte0 & 0x8) == 8):
            try:
                sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                if (exc.GetErrorNumber() == 0x5 or exc.GetErrorNumber() == 0x25):
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Erasing the Card/Card is Busy......")
                    self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure
                    while(busydown == 0):
                        try:
                            CardStatus = self.GetCardStatus()
                        except ValidationError.CVFGenericExceptions as exc:
                            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card is still busy %s\n" % exc.GetInternalErrorMessage())
                        else:
                            if 'CURRENT_STATE:Prg' in CardStatus:
                                continue
                            busydown = 1
                else:
                    raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
        else:
            try:
                sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.ErrorPrint(exc)
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        if(self.__spiMode!=True):
            self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Card-Status with R1 response : %s" % self.decodedR1response)
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "(SPI)Card-Status with R2 response : %s" % self.__responseDataBuf.GetTwoBytesToInt(offset = 1))

        self.FUNCTION_EXIT("Cmd42")
        return self.__responseDataBuf

    # def Cmd42(self, LockCardDataStructure, SkipCMD13):
    #     """
    #     CMD42: LOCK_UNLOCK
    #     """
    #     self.FUNCTION_ENTRY("Cmd42")
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('skipCmd13 is', SkipCMD13))

    #     try:
    #         CMD42 = sdcmdWrap.LockUnlock(objLockCardDataStructure = LockCardDataStructure, skipCmd13 = SkipCMD13)
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         if LockCardDataStructure.lockCardDataStructureByte0.uiErase == False:
    #             raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    #         # Erase Operation needs time delay
    #         if (exc.GetErrorNumber() == 0x5 or exc.GetErrorNumber() == 0x27):
    #             #if expectTimeOut is true don't raise exception. 27 is error code for time out exception
    #             self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD42[LOCK_UNLOCK] Erasing the Card / Card is Busy......")
    #             self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure

    #             while True:
    #                 try:
    #                     CardStatus = self.GetCardStatus()
    #                 except ValidationError.CVFGenericExceptions as ex:
    #                     errstring = ex.GetInternalErrorMessage()
    #                     if (errstring.find('CARD_IS_BUSY') != -1) or (errstring.find('CARD_TIME_OUT_RCVD') != -1):
    #                         self.vtfContainer.CleanPendingExceptions()  # Clear Expected_Exception error to prevent script failure
    #                         continue
    #                     else:
    #                         raise ValidationError.TestFailError(self.fn, ex.GetInternalErrorMessage())
    #                 else:
    #                     if 'CURRENT_STATE:Prg' in CardStatus:
    #                         continue
    #                     break
    #         else:
    #             raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD42.pyResponseData.r1Response.uiCardStatus))
    #     self.FUNCTION_EXIT("Cmd42")
    #     return CMD42

###----------------------------- Class 7 Lock Card End -----------------------------###

###----------------------------- Class 8 Application Specific Start -----------------------------###

    def Cmd55(self, setRCA = False, RCAVal = 0):
        """
        CMD55 - APP_CMD
        """
        self.FUNCTION_ENTRY("Cmd55")
        self.__responseDataBuf.Fill(value = 0x0)

        if setRCA or self.__spiMode:
            arg = self.__relativeCardAddress = 0
        else:
            if RCAVal == 0:
                arg = self.__relativeCardAddress << 16
            else:
                arg = RCAVal

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD55 arg = 0x%X" % arg)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 55,
                                                           argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf)

        if self.__spiMode == False:
            commandDefinitionObj.flags.DoSendStatus = True  # Send CMD13 in case of SD mode
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            CMD55 = sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.DecodeR1Response(self.__responseDataBuf)
        self.FUNCTION_EXIT("Cmd55")
        return self.__responseDataBuf

    #def Cmd55(self, setRCA = False, RCAVal = 0):
        #"""
        #CMD55 - APP_CMD
        #"""
        #self.FUNCTION_ENTRY("Cmd55")

        #if setRCA:
            #RCA = self.__relativeCardAddress = 0x0
        #else:
            #if RCAVal == 0:
                #RCA = self.__relativeCardAddress
            #else:
                #RCA = RCAVal

        #try:
            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD55 RCA = 0x%X" % RCA)
            #CMD55 = sdcmdWrap.AppCmd(uiRCA = RCA)
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.ErrorPrint(exc)
            #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD55.pyResponseData.r1Response.uiCardStatus))

        #self.FUNCTION_EXIT("Cmd55")
        #return CMD55

    def Cmd56(self, RDorWR = 0x110005FF, Buff = None):
        """
        CMD56 - GEN_CMD
        """
        self.FUNCTION_ENTRY("Cmd56")
        self.__responseDataBuf.Fill(value = 0x0)

        Mask = RDorWR & 0x01
        if Buff == None:
            Buff = ServiceWrap.Buffer.CreateBuffer(0x1, patternType = 0x0, isSector = True)

        if Mask == 0x01:
            commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 56,
                                                               argument = RDorWR,
                                                               responseType = sdcmdWrap.TYPE_RESP._R1,
                                                               responseData = self.__responseDataBuf,
                                                               dataMode = sdcmdWrap.DATA_TRANS_.DATA_READ)
        else:
            commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 56,
                                                               argument = RDorWR,
                                                               responseType = sdcmdWrap.TYPE_RESP._R1,
                                                               responseData = self.__responseDataBuf,
                                                               dataMode = sdcmdWrap.DATA_TRANS_.DATA_WRITE)

        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = 1
        commandDataDefinitionObj.uiBlockLen = 512
        commandDataDefinitionObj.ptrBuffer = Buff

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R1 type response : %s" % self.decodedR1response)
        self.FUNCTION_EXIT("Cmd56")
        return Buff

    #def Cmd56(self, Rd_Wr, stuffbits = 0, NoData = False, Buff = None, BlockLength = 512, Pattern = 0xFFFFFFFE):
        #"""
        #CMD56 - GEN_CMD
        #Rd_Wr: True - Read / False - Write
        #"""
        #self.FUNCTION_ENTRY("Cmd56")

        #if Buff == None:
            #Buff = ServiceWrap.Buffer.CreateBuffer(1, patternType = 0x0, isSector = True)
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD56 : Rd_Wr - %s, NoData - %s, BlockLength - %s, Pattern - %s"
                     #% (Rd_Wr, NoData, BlockLength, Pattern))

        #try:
            #CMD56 = sdcmdWrap.GenCmd(uiRd_Wr = Rd_Wr, uistuffbits = stuffbits,
                                     #bNoData = NoData, szBuffer = Buff,
                                     #blockLength = BlockLength, uiPattern = Pattern)
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.ErrorPrint(exc)
            #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD56.pyResponseData.r1Response.uiCardStatus))

        #self.FUNCTION_EXIT("CMD56")
        #return CMD56


    def ACmd6(self, width = 1):
        """
        ACMD6 - SET_BUS_WIDTH
        Parameter Description:
        width : 1 - Set bus width to 1, 4 - Set bus width to 4.
        """
        self.FUNCTION_ENTRY("ACmd6")
        if width == 1:
            arg = 0x00000000
        elif width == 4:
            arg = 0x00000002
        else:
            raise ValidationError.CVFGenericExceptions(self.fn, "Invalid bus width was given")

        self.__responseDataBuf.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 6,
                                                           argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf)
        commandDefinitionObj.flags.DoSendStatus = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            self.__decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.FUNCTION_EXIT("ACmd6")

    def ACmd13(self, arg = 0x0):
        """
        ACMD13 - SD_STATUS
        """
        self.FUNCTION_ENTRY("ACmd13")

        self.__responseDataBuf.Fill(value = 0x0)

        if self.__spiMode != True:
            commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 13,
                                                               argument = arg,
                                                               responseType = sdcmdWrap.TYPE_RESP._R1,
                                                               responseData = self.__responseDataBuf,
                                                               dataMode = sdcmdWrap.DATA_TRANS_.DATA_READ)
            commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
            commandDataDefinitionObj.dwBlockCount = 1
            commandDataDefinitionObj.uiBlockLen = 64
            commandDataDefinitionObj.ptrBuffer = self.__sdStatusReg

            try:
                sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
                self.__decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.ErrorPrint(exc)
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
        else:
            commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 13,
                                                               argument = 0x0,
                                                               responseType = sdcmdWrap.TYPE_RESP._R2,
                                                               responseData = self.__responseDataBuf,
                                                               dataMode = sdcmdWrap.DATA_TRANS_.DATA_READ)
            commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
            commandDataDefinitionObj.dwBlockCount = 1
            commandDataDefinitionObj.uiBlockLen = 64
            commandDataDefinitionObj.ptrBuffer = self.__sdStatusReg

            try:
                sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
                self.__decodedSPIR2response = self.DecodeSPIR2Response(self.__responseDataBuf)
            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.ErrorPrint(exc)
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        sdStatus = self.__sdStatusReg.GetData(0, 64)
        sdStatus.PrintToLog()
        self.FUNCTION_EXIT("ACMD13")
        return sdStatus

    def SD_STATUS(self):
        """
        ACMD13 - SD_STATUS
        """
        self.FUNCTION_ENTRY("SD_STATUS")

        try:
            ACMD13 = sdcmdWrap.SDStatus()
            self.SD_Status = ACMD13

            #ACMD13.pBufferObj.PrintToLog()
            self.HashLineWithArg("SD-STATUS-Response")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - DiscardSupport', ACMD13.objSDStatusRegister.ui16DiscardSupport))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - FuleSupport', ACMD13.objSDStatusRegister.ui16FuleSupport))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - Reserved_3', ACMD13.objSDStatusRegister.ui16Reserved_3))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - Reserved_5', ACMD13.objSDStatusRegister.ui16Reserved_5))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - AppPerfClass', ACMD13.objSDStatusRegister.ui32AppPerfClass))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - Reserved_4', ACMD13.objSDStatusRegister.ui32Reserved_4))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - SUSAddr', ACMD13.objSDStatusRegister.ui32SUSAddr))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - DatBusWidth', ACMD13.objSDStatusRegister.ui64DatBusWidth))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - EraseOffset', ACMD13.objSDStatusRegister.ui64EraseOffset))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - EraseSize', ACMD13.objSDStatusRegister.ui64EraseSize))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - EraseTimeout', ACMD13.objSDStatusRegister.ui64EraseTimeout))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - PerformanceMove', ACMD13.objSDStatusRegister.ui64PerformanceMove))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - ReservedForSecurityFunctions', ACMD13.objSDStatusRegister.ui64ReservedForSecurityFunctions))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - Reserved_1', ACMD13.objSDStatusRegister.ui64Reserved_1))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - Reserved_2', ACMD13.objSDStatusRegister.ui64Reserved_2))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - SDCardType', ACMD13.objSDStatusRegister.ui64SDCardType))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - SDStatus', ACMD13.objSDStatusRegister.ui64SDStatus))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - UHSAuSize', ACMD13.objSDStatusRegister.ui64UHSAuSize))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - UHSSpeedGrades', ACMD13.objSDStatusRegister.ui64UHSSpeedGrades))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - VideoSpeedClass', ACMD13.objSDStatusRegister.ui64VideoSpeedClass))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - ui8PerformanceEnhance', ACMD13.objSDStatusRegister.ui8PerformanceEnhance))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - Performance_Enhance_CommandQueueSupport', ACMD13.objSDStatusRegister.ui8Performance_Enhance_CommandQueueSupport))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - Performance_Enhance_SupportForCache', ACMD13.objSDStatusRegister.ui8Performance_Enhance_SupportForCache))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - Performance_Enhance_SupportForHostInitiatedMaintenance', ACMD13.objSDStatusRegister.ui8Performance_Enhance_SupportForHostInitiatedMaintenance))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - Performance_Enhance_SupportForCardInitiatedMaintenance', ACMD13.objSDStatusRegister.ui8Performance_Enhance_SupportForCardInitiatedMaintenance))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - SizeOfProtectedArea', ACMD13.objSDStatusRegister.ui64SizeOfProtectedArea))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - VSCAuSize', ACMD13.objSDStatusRegister.ui16VSCAuSize))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - SecureMode', ACMD13.objSDStatusRegister.ui64SecureMode))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - SpeedClass', ACMD13.objSDStatusRegister.ui64SpeedClass))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SD - AuSize', ACMD13.objSDStatusRegister.ui64AuSize))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('CardStatus', ACMD13.pyResponseData.r1Response.uiCardStatus))
            #----------------------------------------------------
            # For calculation of ProtectedArea refer chapter 4.10.2.1 in SD spec part 1 physical layer specification version 7.0.
            if ((self.OCRRegister & 0x40000000) != 0) and ((self.OCRRegister & 0x8000000) != 0):        # SDUC card
                # In SDUC cards, capacity of protected area is always zero.
                self.ProtectedArea = ACMD13.objSDStatusRegister.ui64SizeOfProtectedArea

            elif ((self.OCRRegister & 0x40000000) != 0) and ((self.OCRRegister & 0x8000000) == 0):      # SDHC/SDXC card
                self.ProtectedArea = int(ACMD13.objSDStatusRegister.ui64SizeOfProtectedArea)            # Value in byte count

            elif ((self.OCRRegister & 0x40000000) == 0) and ((self.OCRRegister & 0x8000000) == 0):      # SDSC card
                # In SDSC cards, MULT and BLOCK_LEN are calculated using the fields C_SIZE_MULT and READ_BL_LEN from CSD Register.
                self.ProtectedArea = int(ACMD13.objSDStatusRegister.ui64SizeOfProtectedArea * self.__MULT * self.__BLOCK_LEN)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s bytes" % ('Calculated-Protected Area is', self.ProtectedArea))
            #----------------------------------------------------
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.FUNCTION_EXIT("SD_STATUS")
        return ACMD13


    def CardSecureRead(self, CardSlot, BlockCount, StartLba, ReadDataBuffer, Selector, Authenticate, StrDKFile = ""):
        """
        CardSecureRead - SECURE_READ_MULTI_BLOCK (ACMD18) - Refer Part 3 Security Specification

        Parameter description:
        [int] cardSlot- card number, 1-16
        [int] blockCount - 0-255 (where 0=256)
        [int] startLba - start address
        [CTFBuffer] pBufObj - user data
        [int] selector - MKB number
        [bool] authenticate - do authentication or not
        [string] strDKFile - Device Key file:
            a) empty string to use default file(DK_num.bin)
            b) full file path
            c) file name only (the default path will be used)
            d) file path only (the default file name will be used)
        """
        self.FUNCTION_ENTRY("CardSecureRead")

        try:
            CardSecureRead = sdcmdWrap.SecureRead(cardSlot = CardSlot, blockCount = BlockCount, startLba = StartLba,
                                          pBufObj = ReadDataBuffer, selector = Selector,
                                          authenticate = Authenticate, strDKFile = StrDKFile)       # self.__strDKFile
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CardSecureRead.pyResponseData.r1Response.uiCardStatus))

        self.FUNCTION_EXIT("CardSecureRead")
        return CardSecureRead

    def ACmd18(self, arg=0x0):
        """
        Description:Acmd18 is a reserved security command which is used to reads continuously transfer data blocks from protected area of SD memory card.
        """
        self.FUNCTION_ENTRY("ACMD18")
        self.__responseDataBuf.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 18,
                                                            argument = arg,
                                                            responseType = sdcmdWrap.TYPE_RESP._R1,
                                                            responseData = self.__responseDataBuf,
                                                            dataMode = sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
        commandDefinitionObj.flags.DoSendStatus = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DecodedR1Response = %s" % self.DecodeR1Response(self.__responseDataBuf))
        self.FUNCTION_EXIT("ACMD18")
        return self.__responseDataBuf

    def ACmd22(self):
        """
        ACmd22 - SEND_NUM_WR_BLOCKS
        """
        self.FUNCTION_ENTRY("ACmd22")

        try:
            ACMD22 = sdcmdWrap.SendNumberOfWrittenBlocks()
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(ACMD22.pyResponseData.r1Response.uiCardStatus))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('numberOfWrittenBlocks', ACMD22.numberOfWrittenBlocks))

        self.FUNCTION_EXIT("ACmd22")
        return ACMD22

    def ACmd23(self, blockCount):
        """
        ACMD23: SET_WR_BLK_ERASE_COUNT
        """
        self.FUNCTION_ENTRY("ACmd23")

        if blockCount > 0x7FFFFF:
            raise ValidationError.TestFailError(self.fn, "Invalid block count given to ACMD23")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Number of write blocks to be pre-erased before writing', blockCount))
        self.__responseDataBuf.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 23,
                                                           argument = blockCount,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf)
        cmdFlags = sdcmdWrap.CommandFlags()
        cmdFlags.DoSendStatus = True
        commandDefinitionObj.flags = cmdFlags

        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            self.__decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.FUNCTION_EXIT("ACmd23")

    #def ACmd23(self, NumOfBlocks = 0):
        #"""
        #ACmd23 - SER_WR_BLOCK_ERASE_COUNT
        #"""
        #self.FUNCTION_ENTRY("ACmd23")
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Number of write blocks to be pre-erased before writing', NumOfBlocks))

        #try:
            #ACMD23 = sdcmdWrap.SetWriteBlocksEraseCount(uiNumOfBlocks = NumOfBlocks)
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.ErrorPrint(exc)
            #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(ACMD23.pyResponseData.r1Response.uiCardStatus))

        #self.FUNCTION_EXIT("ACmd23")
        #return ACMD23


    def CardSecureWrite(self, CardSlot, BlockCount, StartLba, WriteDataBuffer, Selector, Enable_Signature, Authenticate, StrDKFile = ""):
        """
        CardSecureWrite - SECURE_WRITE_MULTI_BLOCK (ACMD25) - Refer SD Spec Part 3 Security Specification.

        Parameter description:
        [int] cardSlot- card number, 1-16
        [int] blockCount - 0-255 (where 0=256)
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
        """
        self.FUNCTION_ENTRY("CardSecureWrite")

        try:
            CardSecureWrite = sdcmdWrap.SecureWrite(cardSlot = CardSlot, blockCount = BlockCount, startLba = StartLba,
                                           pBufObj = WriteDataBuffer, selector = Selector, enable_signature = Enable_Signature,
                                           authenticate = Authenticate, strDKFile = StrDKFile)        # self.__strDKFile
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CardSecureWrite.pyResponseData.r1Response.uiCardStatus))

        self.FUNCTION_EXIT("CardSecureWrite")
        return CardSecureWrite

    def ACmd25(self, arg = 0x0):
        """
        Description: ACMD25 is a reserved security command which is used to writes continuously transfer data blocks from protected area of SD memory card.
        """
        self.FUNCTION_ENTRY("ACMD25")
        self.__responseDataBuf.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 25,
                                                            argument = arg,
                                                            responseType = sdcmdWrap.TYPE_RESP._R1,
                                                            responseData = self.__responseDataBuf,
                                                            dataMode = sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
        commandDefinitionObj.flags.DoSendStatus = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DecodedR1Response = %s" % self.DecodeR1Response(self.__responseDataBuf))
        self.FUNCTION_EXIT("ACMD25")
        return self.__responseDataBuf

    def CardSecureErase(self, CardSlot, BlockCount, StartLba, Selector, Authenticate, StrDKFile = ""):
        """
        CardSecureErase - SECURE_ERASE - Refer SD Spec Part 3 Security Specification.

        Parameter description:
        [int] cardSlot- card number, 1-16
        [int] blockCount - 0-255 (where 0=256)
        [int] startLba - start address
        [int] selector - MKB number
        [bool] authenticate - do authentication or not
        [string] strDKFile - Device Key file:
            a) empty string to use default file(DK_num.bin)
            b) full file path
            c) file name only (the default path will be used)
            d) file path only (the default file name will be used)
        """
        self.FUNCTION_ENTRY("CardSecureErase")

        try:
            CardSecureErase = sdcmdWrap.SecureErase(cardSlot = CardSlot, blockCount = BlockCount, startLba = StartLba,
                                           selector = Selector, authenticate = Authenticate,
                                           strDKFile = StrDKFile)        # self.__strDKFile
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CardSecureErase.pyResponseData.r1bResponse.uiCardStatus))

        self.FUNCTION_EXIT("CardSecureErase")
        return CardSecureErase

    def ACmd38(self, arg = 0x0):
        """
        Description: ACmd38 is a reserved security command which is used to erases a specified region of the protected area of SD memory card.
        """
        self.FUNCTION_ENTRY("ACMD38")
        self.__responseDataBuf.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 38, argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1b,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_ABSENT)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            self.__decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.FUNCTION_EXIT("Cmd38")
        return self.__responseDataBuf

    def ACmd41(self, hcs = 1 , xpc = 0, s18r = 1, ho2t = 0, argVal=0xFF8000,computedarg = False, diffResp = False, withOcrValue = False):

        self.FUNCTION_ENTRY("ACmd41")
        global OCR_BYTE_31
        self.__responseDataBuf.Fill(pattern_string = "00")

        if computedarg == False:
            arg = (argVal | (hcs << 30) | (xpc << 28) | (s18r << 24) | (ho2t << 27))
        else:
            arg = argVal

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ACMD41 arg = 0x%X" % arg)
        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 41,
                                                           argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R3,
                                                           responseData = self.__responseDataBuf)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            rc = sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            retValue = self.__responseDataBuf.GetData(0,6)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD41[ SD_SEND_OP_COND ] Passed with R3 type response")
            retValue.PrintToLog()

            if diffResp ==False:
                OCR_BYTE_31 = self.__responseDataBuf.GetOneByteToInt(0x01)
            else:
                #the return value needs to match to get the correct output as per the condition if ((last_resp & 0x00FFFFFF) != 0xFF8000):
                OCR_BYTE_31=self.__responseDataBuf.GetFourBytesToInt(0x2, little_endian=False) >> 8
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.FUNCTION_EXIT("ACmd41")
        if (withOcrValue == False):
            return OCR_BYTE_31
        else:
            return retValue


    #def ACmd41(self, HCS, XPC, S18R, VddVoltageWindow = 0xFF8000):
        #"""
        #ACmd41
        #Parameters:
            #HCS  : False - SDSC Only Host, True - SDHC or SDXC Supported by host.
            #XPC  : False - Power Saving, True - Maximum Performance.
            #S18R : False - Use current signal voltage, True - Switch to 1.8V signal voltage.
            #VddVoltageWindow : This is 16 bit argument(In OCR bit 23 to 8).
        #"""
        #self.FUNCTION_ENTRY("ACmd41")

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s : %s" % ("High Capacity Support as", HCS))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s : %s" % ("SDXC Power Control as", XPC))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s : %s" % ("Switching_to_1.8V_Request as", S18R))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s : %s" % ("VddVoltageWindow as", VddVoltageWindow))

        #try:
            #ACMD41 = sdcmdWrap.SdSendOpCond(uiHCS = HCS, uiXPC = XPC, uiS18R = S18R, uiVddVoltageWindow = VddVoltageWindow)
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.ErrorPrint(exc)
            #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('OCR Register', ACMD41.pyResponseData.r3Response.uiOCRReg))

        #self.FUNCTION_EXIT("ACmd41")
        #return ACMD41

    def ACmd42(self, SetClear = True):
        """
        ACmd42: SET_CLR_CARD_DETECT
        """
        self.FUNCTION_ENTRY("ACmd42")
        self.__responseDataBuf.Fill(value = 0x0)
        SetClear = 0x1 if (SetClear == True) else 0x0
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SetClear is', SetClear))

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 42,
                                                           argument = SetClear,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            self.__decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            if (exc.GetErrorNumber() == 0x1 or exc.GetErrorNumber() == 0x27) and SetClear == True:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Timed Out")
                cardState = self.GetCardStatus()  # For Immediate response
                if (cardState.count('CURRENT_STATE:Stby') > 0):
                    self.FUNCTION_EXIT("ACmd42")
                    return self.__responseDataBuf
                else:
                    raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
            else:
                self.ErrorPrint(exc)
                raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())


    # def ACmd42(self, SetClear = 0):
    #     self.FUNCTION_ENTRY("ACmd42")
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SetCd is', SetClear))
    #     try:
    #         ACMD42 = sdcmdWrap.SetClrCardDetect(uiSetCd=SetClear)
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         self.ErrorPrint(exc)
    #         raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(ACMD42.pyResponseData.r1Response.uiCardStatus))
    #     self.FUNCTION_EXIT("ACmd42")
    #     return ACMD42

    def ACmd51(self, arg = 0x0):
        """
        ACmd51: SEND SCR
        """
        self.FUNCTION_ENTRY("ACmd51")
        self.__responseDataBuf.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 51,
                                                           argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_READ)
        commandDefinitionObj.flags.DoSendStatus = False
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = 1
        commandDataDefinitionObj.uiBlockLen = 8
        commandDataDefinitionObj.ptrBuffer = self.__sdSCR

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
            sdScr = self.__sdSCR.GetData(offset = 0, length = 8)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        sdScr.PrintToLog()
        self.FUNCTION_EXIT("ACmd51")
        return sdScr

    def GetSCRRegisterEntry(self):
        """
        ACmd51 - Send_SCR
        """
        # For more Information refer section 5.6 SCR register in Spec 7.0.
        self.FUNCTION_ENTRY("GetSCRRegisterEntry")

        try:
            ACMD51 = sdcmdWrap.SendSCR()
            self.SCRRegister = ACMD51
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(ACMD51.pyResponseData.r1Response.uiCardStatus))
        self.HashLineWithArg("SCR - Register values")
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ScrStructure', ACMD51.objSCRRegister.ui8ScrStructure))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SdSpec', ACMD51.objSCRRegister.ui8SdSpec))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('DataStateAfterErase', ACMD51.objSCRRegister.ui8DataStateAfterErase))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SdSecurity', ACMD51.objSCRRegister.ui8SdSecurity))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SdBusWidth', ACMD51.objSCRRegister.ui8SdBusWidth))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SdSpec3', ACMD51.objSCRRegister.ui16SdSpec3))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ExSecurity', ACMD51.objSCRRegister.ui16ExSecurity))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SdSpec4', ACMD51.objSCRRegister.ui16SdSpec4))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('SdSpecx', ACMD51.objSCRRegister.ui16SdSpecx))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('CmdSupport', ACMD51.objSCRRegister.ui16CmdSupport))

        self.FUNCTION_EXIT("GetSCRRegisterEntry")
        return ACMD51

###----------------------------- Class 8 Application Specific End -----------------------------###

###----------------------------- Class 10 Switch Function Commands Start -----------------------------###

    def CardSwitchCmd(self, mode = 1, arginlist = None, responseBuff = None, blocksize = 0x40):
        """
        CMD6 - SWITCH_FUNCTION_COMMAND

        CMD6 is mandatory for an SD memory card of version 1.10 and higher. The host should check the "SD_SPEC" field in the
        SCR register to identify what version of the spec the card complies with before using CMD6. It is also possible to
        check support of CMD6 by bit10 of CCC in CSD.

        Parameter Description:
        mode: 0 - Check / 1 - Switch
        arginlist: A list contains function number of 6 function groups. Ex: [0xF, 0xF, 0xF, 0xF, 0xF, 0xF]
        responseBuff: 512 bit(64 bytes) of information. Table 4-13 : Status Data Structure in SD Spec Part-I.
        blocksize: size of the response buffer
        """
        self.FUNCTION_ENTRY("CardSwitchCmd")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "mode: %s, arginlist: %s, blockSizeOfResponseBuffer: %s" % (mode, arginlist, blocksize))

        try:
            CardSwitchCmd = sdcmdWrap.SwitchFunction(SwitchMode = mode, args6 = arginlist, buffer = responseBuff, BlockLen = blocksize)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CardSwitchCmd.pyResponseData.r1Response.uiCardStatus))

        self.FUNCTION_EXIT("CardSwitchCmd")
        return CardSwitchCmd

    def Cmd6(self, arg, readDataBuffer, operationalMode):
        """
        CMD6 - SWITCH_FUNCTION_COMMAND

        CMD6 is mandatory for an SD memory card of version 1.10 and higher. The host should check the "SD_SPEC" field in the
        SCR register to identify what version of the spec the card complies with before using CMD6. It is also possible to
        check support of CMD6 by bit10 of CCC in CSD.

        Parameter Description:
            arg: Bits 23 to 0(6 function's value)
            readDataBuffer: 512 bit(64 bytes) of information. Table 4-13 : Status Data Structure in SD Spec Part-I.
            operationalMode: 0 - Check / 1 - Switch
        """
        self.FUNCTION_ENTRY("Cmd6")
        self.__responseDataBuf.Fill(value = 0x0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "arg: %s, operationalMode: %s" % (arg, operationalMode))

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 6, argument = arg,
                                                            responseType = sdcmdWrap.TYPE_RESP._R1,
                                                            responseData = self.__responseDataBuf,
                                                            dataMode = sdcmdWrap.DATA_TRANS_.DATA_READ)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = 1
        commandDataDefinitionObj.uiBlockLen = 64
        commandDataDefinitionObj.ptrBuffer = readDataBuffer

        try:
            CMD6 = sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.DecodeSwitchCommandResponse(operationalMode, readDataBuffer)

        self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf.GetFourBytesToInt(offset = 1, little_endian = False))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DecodedR1Response: %s" % self.decodedR1response)

        self.FUNCTION_EXIT("Cmd6")
        return readDataBuffer

    def Cmd34(self, startLbaAddress, readDataBuffer):
        """
        CMD34: UNTAG_SEC
        """
        self.__responseDataBuf.Fill(pattern_string = "00")

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 34, argument = startLbaAddress,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_READ)
        commandDefinitionObj.flags.DoSendStatus = True

        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = 1
        commandDataDefinitionObj.uiBlockLen = 512
        commandDataDefinitionObj.ptrBuffer = readDataBuffer

        try:
            rc = sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            retValue = self.__responseDataBuf.GetData(0, 6)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd34[UNTAG_SEC] Failed with an exception")
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        if rc == 0 or rc == None:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd34[UNTAG_SEC] Passed with R1 type response:%s" % retValue)
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd34[UNTAG_SEC] Failed with R1 type response:%s" % retValue)
            raise ValidationError.TestFailError(self.fn, "Cmd34[UNTAG_SEC] Failed with R1 type response:%s" % retValue)


    def Cmd35(self, startLbaAddress, writeDataBuffer):
        """
        CMD35 - TAG_ERASE_GRP_START
        """
        self.__responseDataBuf.Fill(pattern_string = "00")

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd=35,
                                                           argument = startLbaAddress,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_WRITE)

        commandDefinitionObj.flags.DoSendStatus = True
        commandDefinitionObj.flags.AnalyzeResponse = True

        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = 1
        commandDataDefinitionObj.uiBlockLen = 512
        commandDataDefinitionObj.ptrBuffer = writeDataBuffer

        try:
            rc = sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd35[TAG_ERASE_GRP_START] Failed with an exception")
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        if(self.__spiMode != True):
            if rc == 0 or rc == None:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd35[TAG_ERASE_GRP_START] Passed with R1 type response")
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd35[TAG_ERASE_GRP_START] Failed with R1 type response")
                raise ValidationError.TestFailError(self.fn, "Cmd35[TAG_ERASE_GRP_START] Failed with R1 type response")
        else:
            if rc == 0 or rc == None:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd35[TAG_ERASE_GRP_START(SPI Mode)] Passed with R2 type response")
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd35[TAG_ERASE_GRP_START(SPI Mode)] Failed with R2 type response")
                raise ValidationError.TestFailError(self.fn, "Cmd35[TAG_ERASE_GRP_START(SPI Mode)] Failed with R2 type response")


    def Cmd36(self, startLbaAddress, writeDataBuffer):
        """
        CMD36 - TAG_ERASE_GROUP_END
        """
        self.__responseDataBuf.Fill(pattern_string = "00")

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 36,
                                                           argument = startLbaAddress,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_WRITE)
        commandDefinitionObj.flags.DoSendStatus = True

        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = 1
        commandDataDefinitionObj.uiBlockLen = 512
        commandDataDefinitionObj.ptrBuffer = writeDataBuffer

        try:
            rc = sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            retValue = self.__responseDataBuf.GetData(0, 6)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd36 Failed with an exception")
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        if rc == 0 or rc == None:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd36 Passed with R1 type response:%s" % retValue)
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd36 Failed with R1 type response:%s" % retValue)
            raise ValidationError.TestFailError(self.fn, "Cmd36 Failed with R1 type response:%s" % retValue)


    def Cmd37(self, startLbaAddress, writeDataBuffer):
        """
        CMD37 - TAG_ERASE_GROUP
        """
        self.__responseDataBuf.Fill(pattern_string = "00")

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 37,
                                                           argument = startLbaAddress,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_WRITE)
        commandDefinitionObj.flags.DoSendStatus = True

        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = 1
        commandDataDefinitionObj.uiBlockLen = 512
        commandDataDefinitionObj.ptrBuffer = writeDataBuffer

        try:
            rc = sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            retValue = self.__responseDataBuf.GetData(0, 6)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd37 Failed with an exception")
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        if rc == 0 or rc == None:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd37 Passed with R1 type response:%s" % retValue)
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd37 Failed with R1 type response:%s" % retValue)
            raise ValidationError.TestFailError(self.fn, "Cmd37 Failed with R1 type response:%s" % retValue)


    def Cmd50(self, startLbaAddress, writeDataBuffer):
        """
        CMD50 - DIRECT_SECURE_READ
        """
        self.__responseDataBuf.Fill(pattern_string = "00")

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 50,
                                                           argument = startLbaAddress,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_WRITE)
        commandDefinitionObj.flags.DoSendStatus = True

        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = 1
        commandDataDefinitionObj.uiBlockLen = 512
        commandDataDefinitionObj.ptrBuffer = writeDataBuffer

        try:
            rc = sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            retValue = self.__responseDataBuf.GetData(0, 6)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd50 Failed with an exception")
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        if rc == 0 or rc == None:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd50 Passed with R1 type response:%s" % retValue)
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd50 Failed with R1 type response:%s" % retValue)
            raise ValidationError.TestFailError(self.fn, "Cmd50 Failed with R1 type response:%s" % retValue)


    def Cmd57(self, startLbaAddress, writeDataBuffer):
        """
        CMD57 - DIRECT_SECURE_WRITE
        """
        self.__responseDataBuf.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 57,
                                                           argument = startLbaAddress,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_WRITE)
        commandDefinitionObj.flags.DoSendStatus = True

        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = 1
        commandDataDefinitionObj.uiBlockLen = 512
        commandDataDefinitionObj.ptrBuffer = writeDataBuffer

        try:
            rc = sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            retValue = self.__responseDataBuf.GetData(0, 6)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd57 Failed with an exception")
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        if rc == 0 or rc == None:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd57 Passed with R1 type response:%s" % retValue)
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Cmd57 Failed with R1 type response:%s" % retValue)
            raise ValidationError.TestFailError(self.fn, "Cmd57 Failed with R1 type response:%s" % retValue)


###----------------------------- Class 10 Switch Function Commands End -----------------------------###

###----------------------------- Class 11 Extension Register Start -----------------------------###

    def Cmd48(self, DataBuff, ExtnFunNum, MIO = 0, Address = 0x0, Length = 512):
        """
        Description: To perform a single block read of extension register
        Parameters Description:
            ExtnFunNum: Extension register function number
            DataBuff: Buffer to hold data read from extension register
            Address: Page number(upper 8bit) and offset within the page(lower 9bit) of extension register function from where data to be read
            MIO: 0 - Memory Extension, 1 - I/O Extension
            Length: Number of bytes to read
        """
        self.FUNCTION_ENTRY(self.GL_CMD48_FUNC_ENTRY_EXIT)
        self.__responseDataBuf.Fill(value = 0x0)

        # Length - 0 is 1 byte, ....., 511(0x1FF) is 512 bytes. So reducing Length by 1 in below code.
        arg = (((MIO & 0x1) << 31) | ((ExtnFunNum & 0xF) << 27) | ((Address & 0x1FFFF) << 9) | ((Length - 1) & 0x1FF))

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CMD48_ARGS(MIO, ExtnFunNum, Address, Length))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_ARGUMENTS(arg))

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 48, argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_READ)
        commandDefinitionObj.flags.DoSendStatus = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = 1
        commandDataDefinitionObj.uiBlockLen = 512
        commandDataDefinitionObj.ptrBuffer = DataBuff

        config = getconfig.getconfig()
        globalResetTO = int(config.get('globalResetTO'))
        globalReadTO = int(config.get('globalReadTO'))
        globalWriteTO = int(config.get('globalWriteTO'))

        try:
            sdcmdWrap.CardSetTimeout(resetTO = 1000, busyTO = 1000, readTO = 1000)
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            sdcmdWrap.CardSetTimeout(resetTO = globalResetTO, busyTO = globalWriteTO, readTO = globalReadTO)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.vtfContainer.CleanPendingExceptions()
            sdcmdWrap.CardSetTimeout(resetTO = globalResetTO, busyTO = globalWriteTO, readTO = globalReadTO)
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        if ExtnFunNum == 0:
            self.General_Information(DataBuff)
        elif ExtnFunNum == 1:
            self.Power_Management(DataBuff)
        elif ExtnFunNum == 2:
            self.Performance_Enhancement_Register_Set(DataBuff)

        self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)

        self.FUNCTION_EXIT(self.GL_CMD48_FUNC_ENTRY_EXIT)
        return self.__responseDataBuf


    #def Cmd48(self, FNO, MIO = False, Address = 0x0, Length = 0x1FF):
        #"""
        #CMD48 - READ_EXTR_SINGLE
        #Parameters Description:
            #FNO - FunctionNumber
            #MIO - Memory or I/O
            #uiAddress - Address is 17 bit value. upper 8 bit takes page offset and lower 9 bit takes byte offset of the function
            #specified in the parameter FNO.
            #Length - Number of the bytes to be read from the page and byte offset specified in uiAddress.
        #"""
        #self.FUNCTION_ENTRY("Cmd48")

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FNO - %s, MIO = %s, Address = %s, Length = %s" % (FNO, MIO, Address, Length))

        #try:
            #CMD48 = sdcmdWrap.ExtensionRegisterSingleReadCmd(uiLen = Length, uiAddress = Address, uiFNO = FNO, bMIO = MIO)
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CQ Extension register read command failed")
            #self.ErrorPrint(exc)
            #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD48.pyResponseData.r1Response.uiCardStatus))

        #if FNO == 0:
            #self.General_Information(CMD48)
        #elif FNO == 1:
            #self.Power_Management(CMD48)
        #elif FNO == 2:
            #self.Performance_Enhancement_Register_Set(CMD48)

        #self.decodedR1response = self.DecodeR1Response(CMD48.pyResponseData.r1Response.uiCardStatus)

        #self.FUNCTION_EXIT("Cmd48")
        #return CMD48


    def Cmd49(self, DataBuff, ExtnFunNum, MIO = 0, MW = 0, Address = 0x00, LenORMask = 512):
        """
        Description: To perform a single block write of extension register
        Parameters Description:
            ExtnFunNum: Extension register function number
            DataBuff: Buffer to hold data to write to extension register
        Address: Page number(upper 8bit) and offset within the page(lower 9bit) of extension register function to which data is to be written
        MIO: 0 - Memory Extension, 1 - I/O Extension
        LenORMask: Number of bytes to write
        MW: Mask write mode. 0 - Mask Disabled, 1 - Mask Enabled, If MW is 1 then consider LenORMask as Mask(8 bit field)
        """
        self.FUNCTION_ENTRY(self.GL_CMD49_FUNC_ENTRY_EXIT)
        self.__responseDataBuf.Fill(value = 0x0)

        if MW == 1:
            arg = (((MIO & 0x1) << 31) | ((ExtnFunNum & 0xF) << 27) | ((MW & 0x1) << 26) | ((Address & 0x1FFFF) << 9) | ((LenORMask) & 0xFF))  # For mask operation
        else:
            # LenORMask - 0 is 1 byte, ....., 511(0x1FF) is 512 bytes. So reducing LenORMask by 1 in below code.
            arg = (((MIO & 0x1) << 31) | ((ExtnFunNum & 0xF) << 27) | ((MW & 0x1) << 26) | ((Address & 0x1FFFF) << 9) | ((LenORMask - 1) & 0x1FF))

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CMD49_ARGS(MIO, ExtnFunNum, MW, Address, LenORMask))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_ARGUMENTS(arg))

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 49, argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_WRITE)
        commandDefinitionObj.flags.DoSendStatus = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = 1
        commandDataDefinitionObj.uiBlockLen = 512
        commandDataDefinitionObj.ptrBuffer = DataBuff

        config = getconfig.getconfig()
        globalResetTO = int(config.get('globalResetTO'))
        globalReadTO = int(config.get('globalReadTO'))
        globalWriteTO = int(config.get('globalWriteTO'))

        try:
            sdcmdWrap.CardSetTimeout(resetTO = 1000, busyTO = 1000, readTO = 1000)
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            sdcmdWrap.CardSetTimeout(resetTO = globalResetTO, busyTO = globalWriteTO, readTO = globalReadTO)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.vtfContainer.CleanPendingExceptions()
            sdcmdWrap.CardSetTimeout(resetTO = globalResetTO, busyTO = globalWriteTO, readTO = globalReadTO)
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)

        self.FUNCTION_EXIT(self.GL_CMD49_FUNC_ENTRY_EXIT)
        return self.__responseDataBuf


    #def Cmd49(self, FNO, ExtRegFunc, Address = 0x0, LenORMask = 0x1FF, MW = False, MIO = False):
        #"""
        #CMD49 - WRITE_EXTR_SINGLE

        #Parameters:
            #FNO : Extension Function number
            #Address : page number(upper 8bit) and offset within the page(lower 9bit) of Extension Register to which data is to be written
            #MIO : 0 - Memory Extension, 1 - I/O Extension
            #LenORMask : Number of bytes to write. 0 is 1 byte, ....., 511(0x1FF) is 512 bytes.
            #MW : Mask Write Mode. 0 - Mask Disabled, 1 - Mask Enabled, If MW is 1 then consider LenORMask as Mask(8 bit field)
        #"""
        #self.FUNCTION_ENTRY("Cmd49")

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FNO - %s, Address = %s, LenORMask = %s, MW - %s, MIO = %s" % (FNO, Address, LenORMask, MW, MIO))

        #UpdateReg = sdcmdWrap.U()
        #if FNO == 0:
            #UpdateReg.generalInfo = ExtRegFunc
        #elif FNO == 1:
            #UpdateReg.powerMgmntFunc = ExtRegFunc
        #elif FNO == 2:
            #UpdateReg.perfEncmntFunc = ExtRegFunc

        #extRegister = sdcmdWrap.EXTENSION_REGISTERS()
        #extRegister.u = UpdateReg

        #try:
            #CMD49 = sdcmdWrap.ExtensionRegisterSingleWriteCmd(uiLenORMask = LenORMask, uiAddress = Address,
                                                                #bMW = MW, uiFNO = FNO, bMIO = MIO, extRegister = extRegister)
        #except ValidationError.CVFExceptionTypes as exc:
            #exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            #self.ErrorPrint(exc)
            #raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        #self.decodedR1response = self.DecodeR1Response(CMD49.pyResponseData.r1Response.uiCardStatus)
        #self.FUNCTION_EXIT("Cmd49")
        #return CMD49

    def Cmd58_MultiBlkRead(self, ExtnFunNum, DataBuff, Address = 0x00, BUS = 0, MIO = 0, BUC = 1):
        """
        CMD58 - READ_EXTR_MULTI

        Parameters:
            ExtnFunNum : Extension Function number
            DataBuff : buffer to hold data read from Extension Register
            Address : page number(upper 8bit) and offset within the page(lower 9bit) of Extension Register from where data is to be read
            MIO : 0 -> Mem Extension, 1 for I/O Extension
            BUC : 0 -> Block Unit Count (ranges from 0 to 512 Block units)
            BUS : Block Unit Select
                0 - 512Bytes
                1 - 32KBytes :: 64 data blocks [32 *1024 == 64 * 512]

            Total block count will be (Block unit * Block Unit Count)
        """
        self.FUNCTION_ENTRY("Cmd58_MultiBlkRead")
        self.__responseDataBuf.Fill(value = 0x0)

        arg = (((MIO & 0x1) << 31) | ((ExtnFunNum & 0xF) << 27) | ((BUS & 0x1) << 26) | ((Address & 0x1FFFF) << 9) | ((BUC - 1) & 0x1FF))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD58[READ_EXTR_MULTI]: Argument = 0x%X" % arg)

        if BUS == 1:
            totalBlocks = 64 * BUC
        else:
            totalBlocks = BUC

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 58,
                                                           argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_MULTREAD)
        commandDefinitionObj.flags.DoSendStatus = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = totalBlocks
        commandDataDefinitionObj.uiBlockLen = 512
        commandDataDefinitionObj.ptrBuffer = DataBuff

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R1 type response : %s" % self.decodedR1response)
        self.FUNCTION_EXIT("Cmd58_MultiBlkRead")

    # def Cmd58(self, ExtnFunNum, Address = 0x00, MIO = 0, BUS = 0, BUC = 1, NoData = True,
    #           StopTransmission = True, BlockLength = 512, Pattern = 0xFFFFFFFE):
    #     """
    #     CMD58 - Extension_Register_Multiple_Read

    #     Funtionality: To read multiple blocks of data
    #     Arguments:
    #         ExtnFunNum : Extension Function number
    #         Address : page number(upper 8bit) and offset within the page(lower 9bit) of Extension Register from where data is to be read
    #         MIO : 0 - Memory Extension, 1 - Input/Output Extension
    #         BUS : Block Unit Select
    #             0 - 512Bytes
    #             1 - 32KBytes :: 64 data blocks [32 *1024 == 64 * 512]
    #         BUC : 0 - Block Unit Count (ranges from 0 to 512 Block units)

    #     Total block count will be (Block unit * Block Unit Count)
    #     """
    #     self.FUNCTION_ENTRY("Cmd58_MultiBlkRead")

    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ExtnFunNum = %d, Address = 0x%X, MIO = %s, BUS = %s, BUC = %s, NoData = %s, StopTransmission = %s, BlockLength = %d, Pattern = %s"
    #                  % (ExtnFunNum, Address, MIO, BUS, BUC, NoData, StopTransmission, BlockLength, Pattern))

    #     try:
    #         CMD58 = sdcmdWrap.ReadExtraMulti(uiAddress = Address, bMemoryOrIo = MIO, bBlockUnitSelect = BUS, uiBlockUnitCount = BUC,
    #                                          uiFunctionNo = ExtnFunNum, bNoData = NoData, bStopTransmission = StopTransmission,
    #                                          #extraInfo = NONE_INFO,
    #                                          uiBlockLength = BlockLength, uiPattern = Pattern)
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         self.ErrorPrint(exc)
    #         raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD58.pyResponseData.r1Response.uiCardStatus))
    #     self.decodedR1response = self.DecodeR1Response(CMD58.pyResponseData.r1Response.uiCardStatus)

    #     self.FUNCTION_EXIT("Cmd58_MultiBlkRead")
    #     return CMD58

    def Cmd59_MultiBlkWrite(self, ExtnFunNum, DataBuff, Address = 0x00, BUS = 0, MIO = 0, BUC = 1):
        """
        CMD59 - WRITE_EXTR_MULTI

        Parameters:
            ExtnFunNum : Extension Function number
            DataBuff : buffer to write the data into extension register
            Address : page number(upper 8bit) and offset within the page(lower 9bit) of Extension Register from where data is to be write
            MIO : 0 -> Mem Extension, 1 for I/O Extension
            BUC : 0 -> Block Unit Count (ranges from 0 to 512 Block units)
            BUS : Block Unit Select
                0 - 512Bytes
                1 - 32KBytes :: 64 data blocks [32 *1024 == 64 * 512]
            Total block count will be (Block unit * Block Unit Count)
        """
        self.FUNCTION_ENTRY("Cmd59_MultiBlkWrite")
        self.__responseDataBuf.Fill(value = 0x0)

        arg = (((MIO & 0x1) << 31) | ((ExtnFunNum & 0xF) << 27) | ((BUS & 0x1) << 26) | ((Address & 0x1FFFF) << 9) | ((BUC - 1) & 0x1FF))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CMD59[WRITE_EXTR_MULTI]: Argument = 0x%X" % arg)

        if BUS == 1:
            totalBlocks = 64 * BUC
        else:
            totalBlocks = BUC

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 59,
                                                           argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_MULTWRITE)
        commandDefinitionObj.flags.DoSendStatus = True
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = totalBlocks
        commandDataDefinitionObj.uiBlockLen = 512
        commandDataDefinitionObj.ptrBuffer = DataBuff

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R1 type response : %s" % self.decodedR1response)
        self.FUNCTION_EXIT("Cmd59_MultiBlkWrite")

    # def Cmd59(self, ExtnFunNum, ExtentionRegister, Address = 0x00, MIO = 0, BUS = 0, BUC = 1, NoData = True,
    #           StopTransmission = True, BlockLength = 512, Pattern = 0xFFFFFFFE):
    #     """
    #     CMD59 - Extension_Register_Multiple_Write

    #     Funtionality: To write multiple blocks of data
    #     Arguments:
    #     ExtnFunNum : Extension Function number
    #         Address : page number(upper 8bit) and offset within the page(lower 9bit) of Extension Register from where data is to be write
    #         MIO : 0 - Memory Extension, 1 - Input/Output Extension
    #         BUS : Block Unit Select
    #             0 - 512Bytes
    #             1 - 32KBytes :: 64 data blocks [32 * 1024 == 64 * 512]
    #         BUC : 0 - Block Unit Count (ranges from 0 to 512 Block units)

    #     Total block count will be (Block unit * Block Unit Count)
    #     """
    #     self.FUNCTION_ENTRY("Cmd59_MultiBlkWrite")

    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "ExtnFunNum = %d, Address = 0x%X, MIO = %s, BUS = %s, BUC = %s, NoData = %s, StopTransmission = %s, BlockLength = %s, Pattern = %s"
    #                  % (ExtnFunNum, Address, MIO, BUS, BUC, NoData, StopTransmission, BlockLength, Pattern))

    #     UpdateReg = sdcmdWrap.U()
    #     if ExtnFunNum == 0:
    #         UpdateReg.generalInfo = ExtentionRegister
    #     elif ExtnFunNum == 1:
    #         UpdateReg.powerMgmntFunc = ExtentionRegister
    #     elif ExtnFunNum == 2:
    #         UpdateReg.perfEncmntFunc = ExtentionRegister

    #     extRegister = sdcmdWrap.EXTENSION_REGISTERS()
    #     extRegister.u = UpdateReg

    #     try:
    #         CMD59 = sdcmdWrap.WriteExtraMulti(uiAddress = Address, bMemoryOrIo = MIO, bBlockUnitSelect = BUS,
    #                                           uiBlockUnitCount = BUC, uiFunctionNo = ExtnFunNum,
    #                                           objExtentionRegister = ExtentionRegister, bNoData = NoData,
    #                                           bStopTransmission = StopTransmission,
    #                                           #extraInfo = NONE_INFO,
    #                                           uiBlockLength = BlockLength, uiPattern = Pattern)
    #     except ValidationError.CVFExceptionTypes as exc:
    #         exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
    #         self.ErrorPrint(exc)
    #         raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

    #     self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CARD_STATUS_CMD13(CMD59.pyResponseData.r1Response.uiCardStatus))
    #     self.decodedR1response = self.DecodeR1Response(CMD59.pyResponseData.r1Response.uiCardStatus)

    #     self.FUNCTION_EXIT("Cmd59_MultiBlkWrite")
    #     return CMD59


###----------------------------- Class 11 Extension Register End -----------------------------###

###----------------------------- Command Response Decode Start -----------------------------###

    def DecodeR1ResponseFromBuffer(self, resBuffer):
        retValue = []

        CmdIndex = resBuffer.GetOneByteToInt(0)
        retValue.append(CmdIndex)

        errValue1 = resBuffer.GetOneByteToInt(1)
        if (errValue1 & 0x80):
            retValue.append(gvar.Card_Status_Fields.OUT_OF_RANGE)
        if (errValue1 & 0x40):
            retValue.append(gvar.Card_Status_Fields.ADDRESS_ERROR)
        if (errValue1 & 0x20):
            retValue.append(gvar.Card_Status_Fields.BLOCK_LEN_ERROR)
        if (errValue1 & 0x10):
            retValue.append(gvar.Card_Status_Fields.ERASE_SEQ_ERROR)
        if (errValue1 & 0x08):
            retValue.append(gvar.Card_Status_Fields.ERASE_PARAM)
        if (errValue1 & 0x04):
            retValue.append(gvar.Card_Status_Fields.WP_VIOLATION)
        if (errValue1 & 0x02):
            retValue.append(gvar.Card_Status_Fields.CARD_IS_LOCKED)
        if (errValue1 & 0x01):
            retValue.append(gvar.Card_Status_Fields.LOCK_UNLOCK_FAILED)

        errValue1 = resBuffer.GetOneByteToInt(2)
        if (errValue1 & 0x80):
            retValue.append(gvar.Card_Status_Fields.COM_CRC_ERROR)
        if (errValue1 & 0x40):
            retValue.append(gvar.Card_Status_Fields.ILLEGAL_COMMAND)
        if (errValue1 & 0x20):
            retValue.append(gvar.Card_Status_Fields.CARD_ECC_FAILED)
        if (errValue1 & 0x10):
            retValue.append(gvar.Card_Status_Fields.CC_ERROR)
        if (errValue1 & 0x08):
            retValue.append(gvar.Card_Status_Fields.ERROR)
        if (errValue1 & 0x04):
            retValue.append(gvar.Card_Status_Fields.Reserved)
        if (errValue1 & 0x02):
            retValue.append(gvar.Card_Status_Fields.DEFERRED_RESPONSE)
        if (errValue1 & 0x01):
            retValue.append(gvar.Card_Status_Fields.CSD_OVERWRITE)

        errValue = resBuffer.GetOneByteToInt(3)
        if (errValue & 0x80):
            retValue.append(gvar.Card_Status_Fields.WP_ERASE_SKIP)
        if (errValue & 0x40):
            retValue.append(gvar.Card_Status_Fields.CARD_ECC_DISABLED)
        if (errValue & 0x20):
            retValue.append(gvar.Card_Status_Fields.ERASE_RESET)

        currentState = (errValue & 0x1E) >> 1
        if (self.currCfg.variation.cq == 1) and (self.pgnenable == 1):
            if (currentState == 0):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
            if (currentState == 1):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
            if (currentState == 2):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
            if (currentState == 3):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
            if (currentState == 4):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_CQ_Tran)
            if (currentState == 5):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Rdt)
            if (currentState == 6):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Wdt)
            if (currentState == 7):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Bsy)
            if (currentState == 8):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
            if (currentState == 9):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
            if (currentState == 10):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
            if (currentState == 11):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
            if (currentState == 12):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
            if (currentState == 13):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
            if (currentState == 14):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
            if (currentState == 15):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
        else:
            if (currentState == 0):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Idle)
            if (currentState == 1):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Ready)
            if (currentState == 2):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Ident)
            if (currentState == 3):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Stby)
            if (currentState == 4):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Tran)
            if (currentState == 5):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Data)
            if (currentState == 6):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Rcv)
            if (currentState == 7):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Prg)
            if (currentState == 8):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Dis)
            if (currentState == 9):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
            if (currentState == 10):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
            if (currentState == 11):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
            if (currentState == 12):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
            if (currentState == 13):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
            if (currentState == 14):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
            if (currentState == 15):
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved_for_IO_mode)

        if (errValue & 0x01):
            retValue.append(gvar.Card_Status_Fields.READY_FOR_DATA)

        errValue1 = resBuffer.GetOneByteToInt(4)
        if (errValue1 & 0x80):
            retValue.append(gvar.Card_Status_Fields.Reserved)
        if (errValue1 & 0x40):
            retValue.append(gvar.Card_Status_Fields.FIX_EVENT)
        if (errValue1 & 0x20):
            retValue.append(gvar.Card_Status_Fields.APP_CMD)
        if (errValue1 & 0x10):
            retValue.append(gvar.Card_Status_Fields.Reserved_For_SD_IO_Card)
        if (errValue1 & 0x08):
            retValue.append(gvar.Card_Status_Fields.AKE_SEQ_ERROR)
        if (errValue1 & 0x04):
            retValue.append(gvar.Card_Status_Fields.Reserved_For_APP_CMD)
        if (errValue1 & 0x02):
            retValue.append(gvar.Card_Status_Fields.Reserved_For_Manufacturer_Test_Mode)
        if (errValue1 & 0x01):
            retValue.append(gvar.Card_Status_Fields.Reserved_For_Manufacturer_Test_Mode)

        return retValue

    def DecodeR1ResponseFromObject(self, R1_Response):
        retValue = []
        R1_binary = "{:032b}".format(R1_Response)   # interger into 32 bit binary then make binary as string
        R1_binary = R1_binary[::-1]                 # string reverse

        ####--------------------- Reading bit from 31 to 13 ---------------------------###
        if R1_binary[31] == '1':
            retValue.append(gvar.Card_Status_Fields.OUT_OF_RANGE)
        if R1_binary[30] == '1':
            retValue.append(gvar.Card_Status_Fields.ADDRESS_ERROR)
        if R1_binary[29] == '1':
            retValue.append(gvar.Card_Status_Fields.BLOCK_LEN_ERROR)
        if R1_binary[28] == '1':
            retValue.append(gvar.Card_Status_Fields.ERASE_SEQ_ERROR)
        if R1_binary[27] == '1':
            retValue.append(gvar.Card_Status_Fields.ERASE_PARAM)
        if R1_binary[26] == '1':
            retValue.append(gvar.Card_Status_Fields.WP_VIOLATION)
        if R1_binary[25] == '1':
            retValue.append(gvar.Card_Status_Fields.CARD_IS_LOCKED)
        if R1_binary[24] == '1':
            retValue.append(gvar.Card_Status_Fields.LOCK_UNLOCK_FAILED)
        if R1_binary[23] == '1':
            retValue.append(gvar.Card_Status_Fields.COM_CRC_ERROR)
        if R1_binary[22] == '1':
            retValue.append(gvar.Card_Status_Fields.ILLEGAL_COMMAND)
        if R1_binary[21] == '1':
            retValue.append(gvar.Card_Status_Fields.CARD_ECC_FAILED)
        if R1_binary[20] == '1':
            retValue.append(gvar.Card_Status_Fields.CC_ERROR)
        if R1_binary[19] == '1':
            retValue.append(gvar.Card_Status_Fields.ERROR)
        if R1_binary[18] == '1':
            retValue.append(gvar.Card_Status_Fields.Reserved)
        if R1_binary[17] == '1':
            retValue.append(gvar.Card_Status_Fields.DEFERRED_RESPONSE)
        if R1_binary[16] == '1':
            retValue.append(gvar.Card_Status_Fields.CSD_OVERWRITE)
        if R1_binary[15] == '1':
            retValue.append(gvar.Card_Status_Fields.WP_ERASE_SKIP)
        if R1_binary[14] == '1':
            retValue.append(gvar.Card_Status_Fields.CARD_ECC_DISABLED)
        if R1_binary[13] == '1':
            retValue.append(gvar.Card_Status_Fields.ERASE_RESET)

        ####--------------------- Reading bit from 12 to 9 ---------------------------####
        if (self.currCfg.variation.cq == 1) and (self.pgnenable == 1):
            if R1_binary[9:13][::-1] in ['0000','0001','0010','0011','1000','1001','1010','1011','1100','1101','1110','1111']:
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
            if R1_binary[9:13][::-1] == '0100':
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_CQ_Tran)
            if R1_binary[9:13][::-1] == '0101':
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Rdt)
            if R1_binary[9:13][::-1] == '0110':
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Wdt)
            if R1_binary[9:13][::-1] == '0111':
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Bsy)
        else:
            if R1_binary[9:13][::-1] == '0000':
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Idle)
            if R1_binary[9:13][::-1] == '0001':
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Ready)
            if R1_binary[9:13][::-1] == '0010':
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Ident)
            if R1_binary[9:13][::-1] == '0011':
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Stby)
            if R1_binary[9:13][::-1] == '0100':
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Tran)
            if R1_binary[9:13][::-1] == '0101':
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Data)
            if R1_binary[9:13][::-1] == '0110':
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Rcv)
            if R1_binary[9:13][::-1] == '0111':
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Prg)
            if R1_binary[9:13][::-1] == '1000':
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Dis)
            if R1_binary[9:13][::-1] in ['1001','1010','1011','1100','1101','1110',]:
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
            if R1_binary[9:13][::-1] == '1111':
                retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved_for_IO_mode)

        ####--------------------- Reading bit from 8 to 0 ---------------------------####
        if R1_binary[8] == '1':
            retValue.append(gvar.Card_Status_Fields.READY_FOR_DATA)
        if R1_binary[7] == '1':
            retValue.append(gvar.Card_Status_Fields.Reserved)
        if R1_binary[6] == '1':
            retValue.append(gvar.Card_Status_Fields.FIX_EVENT)
        if R1_binary[5] == '1':
            retValue.append(gvar.Card_Status_Fields.APP_CMD)
        if R1_binary[4] == '1':
            retValue.append(gvar.Card_Status_Fields.Reserved_For_SD_IO_Card)
        if R1_binary[3] == '1':
            retValue.append(gvar.Card_Status_Fields.AKE_SEQ_ERROR)
        if R1_binary[2] == '1':
            retValue.append(gvar.Card_Status_Fields.Reserved_For_APP_CMD)
        if R1_binary[1] == '1':
            retValue.append(gvar.Card_Status_Fields.Reserved_For_Manufacturer_Test_Mode)
        if R1_binary[0] == '1':
            retValue.append(gvar.Card_Status_Fields.Reserved_For_Manufacturer_Test_Mode)

        return retValue

    def DecodeR1Response(self, R1_Response):
        if self.__spiMode != True:  # SD Mode
            if type(R1_Response) == ServiceWrap.Buffer:
                retValue = self.DecodeR1ResponseFromBuffer(resBuffer = R1_Response)
            else:
                retValue = self.DecodeR1ResponseFromObject(R1_Response = R1_Response)
            self.decodedR1response = retValue
        else:   # SPI Mode
            retValue = self.DecodeSPIR1Response(resBuffer = R1_Response)
            self.__decodedSPIR1response = retValue
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_DECODED_R1RESPONSE(retValue))
        return retValue

    def DecodeR6Response(self, resBuffer):
        retValue = []

        CmdIndex = resBuffer.GetOneByteToInt(offset = 0)
        retValue.append(CmdIndex)

        self.__relativeCardAddress = resBuffer.GetTwoBytesToInt(offset = 1, little_endian = False)
        retValue.append("RCA:0x%X" % self.__relativeCardAddress)

        CardStatus_23_22_19_12To8 = resBuffer.GetOneByteToInt(offset = 3)
        if (CardStatus_23_22_19_12To8 & 0x80):
            retValue.append(gvar.Card_Status_Fields.COM_CRC_ERROR)
        if (CardStatus_23_22_19_12To8 & 0x40):
            retValue.append(gvar.Card_Status_Fields.ILLEGAL_COMMAND)
        if (CardStatus_23_22_19_12To8 & 0x20):
            retValue.append(gvar.Card_Status_Fields.ERROR)

        currentState = (CardStatus_23_22_19_12To8 & 0x1E) >> 1
        if (currentState == 0):
            retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Idle)
        if (currentState == 1):
            retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Ready)
        if (currentState == 2):
            retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Ident)
        if (currentState == 3):
            retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Stby)
        if (currentState == 4):
            retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Tran)
        if (currentState == 5):
            retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Data)
        if (currentState == 6):
            retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Rcv)
        if (currentState == 7):
            retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Prg)
        if (currentState == 8):
            retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Dis)
        if (currentState == 9):
            retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
        if (currentState == 10):
            retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
        if (currentState == 11):
            retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
        if (currentState == 12):
            retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
        if (currentState == 13):
            retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
        if (currentState == 14):
            retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved)
        if (currentState == 15):
            retValue.append(gvar.Card_Status_Fields.CURRENT_STATE_Reserved_for_IO_mode)

        if (CardStatus_23_22_19_12To8 & 0x01):
            retValue.append(gvar.Card_Status_Fields.READY_FOR_DATA)

        CardStatus_7To0 = resBuffer.GetOneByteToInt(offset = 4)

        if (CardStatus_7To0 & 0x80):
            retValue.append(gvar.Card_Status_Fields.Reserved)
        if (CardStatus_7To0 & 0x40):
            retValue.append(gvar.Card_Status_Fields.FIX_EVENT)
        if (CardStatus_7To0 & 0x20):
            retValue.append(gvar.Card_Status_Fields.APP_CMD)
        if (CardStatus_7To0 & 0x10):
            retValue.append(gvar.Card_Status_Fields.Reserved_For_SD_IO_Card)
        if (CardStatus_7To0 & 0x08):
            retValue.append(gvar.Card_Status_Fields.AKE_SEQ_ERROR)
        if (CardStatus_7To0 & 0x04):
            retValue.append(gvar.Card_Status_Fields.Reserved_For_APP_CMD)
        if (CardStatus_7To0 & 0x02):
            retValue.append(gvar.Card_Status_Fields.Reserved_For_Manufacturer_Test_Mode)
        if (CardStatus_7To0 & 0x01):
            retValue.append(gvar.Card_Status_Fields.Reserved_For_Manufacturer_Test_Mode)

        return retValue

    def DecodeR7ResponseSD(self, resBuffer):
        """
        DecodeR7Response: It decodes the R7 response in SD mode.
        """
        retValue = {}

        CmdIndex = resBuffer.GetOneByteToInt(0)
        retValue["CMD"] = CmdIndex

        PCIe_and_VHS = resBuffer.GetOneByteToInt(3)

        retValue["PCIeAvailibility"] = (PCIe_and_VHS & 0x10) >> 4
        retValue["PCIe1_2VSupport"] = (PCIe_and_VHS & 0x20) >> 5

        VHS = PCIe_and_VHS & 0x0F
        if VHS == 1:
            retValue["VHS"] = "2.7-3.6V"
        elif VHS == 2:
            retValue["VHS"] = "Reserved_for_Low_Voltage_Range"
        elif (VHS == 4) or (VHS == 8):
            retValue["VHS"] = "Reserved"
        else:
            retValue["VHS"] = "Not_Defined"

        retValue["Check_Pattern"] = resBuffer.GetOneByteToInt(4)
        retValue["CRC"] = (resBuffer.GetOneByteToInt(5) & 0xFE) >> 1

        return retValue

    def DecodeR7Response(self, resBuffer):
        if self.__spiMode == True: # SPI Mode
            retValue = self.DecodeSPIR7Response(resBuffer = resBuffer)
            self.__decodedSPIR7response = retValue
        else:   # SD Mode
            retValue = self.DecodeR7ResponseSD(resBuffer = resBuffer)
            self.__decodedR7response = retValue

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Decoded R7 response: %s" % retValue)
        return retValue

    #def DecodeSwitchCommandResponse(self, operationalMode, responseBuff):
        #"""
        #Description: DecodeSwitchCommandResponse decodes the response buffer of CMD6. Refer section 4.3.10.4 or Table 4-13 in SD Spec Part-I.
        #Parameter Description:
            #operationalMode: 0 - Check / 1 - Switch
            #responseBuff: 64 bytes(511 bits) response buffer of CMD6. Refer Table 4-13 : Status Data Structure.
        #"""

        #Available_Functions = {"Group1": ["SDR12", "SDR25", "SDR50", "SDR104", "DDR50"] + (["Reserved"] * 11),
                                #"Group2": ["Default", "For eC", "Reserved", "OTP", "ASSD"] + (["Reserved"] * 11),
                                #"Group3": ["Type B", "Type A", "Type C", "Type D"] + (["Reserved"] * 12),
                                #"Group4": ["0.72W", "1.44W", "2.16W", "2.88W", "1.80W"] + (["Reserved"] * 11),
                                #"Group5": [] + (["Reserved"] * 16),
                                #"Group6": [] + (["Reserved"] * 16)}

        #Maximum_Power_or_Current_Consumption = responseBuff.GetTwoBytesToInt(offset = 0, little_endian = False)    # Bit 511 to 496
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Maximum power/current consumption is - %s" %  Maximum_Power_or_Current_Consumption)
        #if Maximum_Power_or_Current_Consumption == 0:
            #raise ValidationError.TestFailError(self.fn, "Maximum power/current consumption is - 0")

        #Supported_Bits_of_Functions_Start_Offset = 2
        #Supported_Functions = {"Group1": [], "Group2": [], "Group3": [], "Group4": [], "Group5": [], "Group6": []}

        #Function_Selection = {}
        #Function_Selection_of_Function_Group_6_and_5 = responseBuff.GetOneByteToInt(offset = 14)    # Bit 399 to 392
        #Function_Selection_of_Function_Group_6 = Function_Selection_of_Function_Group_6_and_5 >> 4    # Bit 399 to 396
        #Function_Selection_of_Function_Group_5 = Function_Selection_of_Function_Group_6_and_5 &    0xF    # Bit 395 to 392
        #Function_Selection_of_Function_Group_4_and_3 = responseBuff.GetOneByteToInt(offset = 15)    # Bit 391 to 384
        #Function_Selection_of_Function_Group_4 = Function_Selection_of_Function_Group_4_and_3 >> 4    # Bit 391 to 388
        #Function_Selection_of_Function_Group_3 = Function_Selection_of_Function_Group_4_and_3 &    0xF    # Bit 387 to 384
        #Function_Selection_of_Function_Group_1_and_2 = responseBuff.GetOneByteToInt(offset = 16)    # Bit 383 to 376
        #Function_Selection_of_Function_Group_2 = Function_Selection_of_Function_Group_1_and_2 >> 4    # Bit 383 to 380
        #Function_Selection_of_Function_Group_1 = Function_Selection_of_Function_Group_1_and_2 &    0xF    # Bit 379 to 376

        #for group in [6, 5, 4, 3, 2, 1]:
            #group = "Group%s" % group

            #Supported_Bits = "{:016b}".format(responseBuff.GetTwoBytesToInt(offset = Supported_Bits_of_Functions_Start_Offset, little_endian = False))    # Convert two byte int to 16 bit binary string
            #Supported_Bits = Supported_Bits[::-1]        # String reverse(From supported functions 15:0 to 0:15)
            #for function in range(0, len(Supported_Bits)):
                #if (Supported_Bits[function] == "1") and (Available_Functions[group][function] != "Reserved"):
                    #Supported_Functions[group].append(Available_Functions[group][function])
            #Supported_Bits_of_Functions_Start_Offset += 2

            #if Available_Functions[group][Function_Selection_of_Function_Group_6] != "Reserved":
                #Function_Selection[group] = Available_Functions[group][Function_Selection_of_Function_Group_6]
            #else:
                #Function_Selection[group] = None

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Supported functions of switch command - %s" % Supported_Functions)
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Function selection of switch command - %s" % Function_Selection)

        #return {"Maximum_Power": Maximum_Power_or_Current_Consumption, "Supported_Functions": Supported_Functions, "Function_Selection": Function_Selection}

    def DecodeSwitchCommandResponseFromBuffer(self,operationalMode,responseList):
        """
        DecodeSwitchCommandResponseFromBuffer decodes the response buffer of CMD6.
        """
        decodedList = []

        if operationalMode == "CHECK":
            if (responseList.GetOneByteToInt(0) == 0) and (responseList.GetOneByteToInt(1) == 0):
                # For LC and LC SPI mode value is 0
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "OperatingCurrent:0")
            else:
                decodedList.append("OperatingCurrent:%s" % responseList.GetOneByteToInt(1))
            if responseList.GetOneByteToInt(13) & 0x01:
                decodedList.append("SDR12 SUPPORTED")
            if responseList.GetOneByteToInt(13) & 0x02:
                decodedList.append("SDR25/HIGH SPEED SUPPORTED")
            if responseList.GetOneByteToInt(13) & 0x04:
                decodedList.append("SDR50 SUPPORTED")
            if responseList.GetOneByteToInt(13) & 0x08:
                decodedList.append("SDR104 SUPPORTED")
            if responseList.GetOneByteToInt(13) & 0x10:
                decodedList.append("DDR50 SUPPORTED")
            if responseList.GetOneByteToInt(13) & 0x20: #Group1 - Function 0x5
                decodedList.append("DDR200 SUPPORTED IN GROUP1")
                self._DDR200_SupportedGrpNum = 1
            if responseList.GetOneByteToInt(10) & 0x40: #Group2 - Function 0xE
                decodedList.append("DDR200 SUPPORTED IN GROUP2")
                self._DDR200_SupportedGrpNum = 2
            if responseList.GetOneByteToInt(7) & 0x01:
                decodedList.append("Current: 200mA SUPPORTED")
            if responseList.GetOneByteToInt(7) & 0x02:
                decodedList.append("Current: 400mA SUPPORTED")
            if responseList.GetOneByteToInt(7) & 0x04:
                decodedList.append("Current: 600mA SUPPORTED")
            if responseList.GetOneByteToInt(7) & 0x08:
                decodedList.append("Current: 800mA SUPPORTED")
        elif operationalMode == "SWITCH":
            decodedList.append("OperatingCurrent:%s mA" % responseList.GetOneByteToInt(1))
            if responseList.GetOneByteToInt(16) == 0:
                decodedList.append("SDR12 SWITCHED")
            if responseList.GetOneByteToInt(16) == 1:
                decodedList.append("SDR25/HIGH SPEED SWITCHED")
            if responseList.GetOneByteToInt(16) == 2:
                decodedList.append("SDR50 SWITCHED")
            if responseList.GetOneByteToInt(16) == 3:
                decodedList.append("SDR104 SWITCHED")
            if responseList.GetOneByteToInt(16) == 4:
                decodedList.append("DDR50 SWITCHED")
            if responseList.GetOneByteToInt(16) == 5:   # Group1 - Function 0x5
                decodedList.append("DDR200 SWITCHED IN GROUP1")
            if (responseList.GetOneByteToInt(16) >> 4) == 0xE:  # Group2 - Function 0xE
                decodedList.append("DDR200 SWITCHED IN GROUP2")
            if responseList.GetOneByteToInt(15) >> 4 == 0:
                decodedList.append("200mA SWITCHED")
            if responseList.GetOneByteToInt(15) >> 4 == 1:
                decodedList.append("400mA SWITCHED")
            if responseList.GetOneByteToInt(15) >> 4 == 2:
                decodedList.append("600mA SWITCHED")
            if responseList.GetOneByteToInt(15) >> 4 == 2:
                decodedList.append("800mA SWITCHED")

        return  decodedList

    def DecodeSwitchCommandResponseFromObject(self, operationalMode, CMD6):
        """
        DecodeSwitchCommandResponseFromObject decodes the response object of CMD6
        """
        decodedList = []

        if operationalMode == "CHECK":
            if CMD6.statusDataStructure.uiMaximumPowerConsumption == 0:
                # For LC and LC SPI mode value is 0
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "OperatingCurrent:0")
            else:
                decodedList.append("OperatingCurrent:%s" % CMD6.statusDataStructure.uiMaximumPowerConsumption)
            if CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup1 & 0x1:
                decodedList.append("SDR12 SUPPORTED")
            if CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup1 & 0x2:
                decodedList.append("SDR25/HIGH SPEED SUPPORTED")
            if CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup1 & 0x4:
                decodedList.append("SDR50 SUPPORTED")
            if CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup1 & 0x8:
                decodedList.append("SDR104 SUPPORTED")
            if CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup1 & 0x10:
                decodedList.append("DDR50 SUPPORTED")
            if CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup4 & 0x1:
                decodedList.append("Current: 200mA SUPPORTED")
            if CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup4 & 0x2:
                decodedList.append("Current: 400mA SUPPORTED")
            if CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup4 & 0x4:
                decodedList.append("Current: 600mA SUPPORTED")
            if CMD6.statusDataStructure.uiSupportBitsOfFunctionsInFunctionGroup4 & 0x8:
                decodedList.append("Current: 800mA SUPPORTED")
        elif operationalMode == "SWITCH":
            decodedList.append("OperatingCurrent:%s" % CMD6.statusDataStructure.uiMaximumPowerConsumption)
            if CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup1 == 0:
                decodedList.append("SDR12 SWITCHED")    # Function 0x0 of function group 1
            if CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup1 == 1:
                decodedList.append("SDR25/HIGH SPEED SWITCHED")     # Function 0x1 of function group 1
            if CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup1 == 2:
                decodedList.append("SDR50 SWITCHED")    # Function 0x2 of function group 1
            if CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup1 == 3:
                decodedList.append("SDR104 SWITCHED")   # Function 0x3 of function group 1
            if CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup1 == 4:
                decodedList.append("DDR50 SWITCHED")    # Function 0x4 of function group 1
            if CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup4 == 0:
                decodedList.append("200mA SWITCHED")    # 0.72W - Function 0x0 of function group 4
            if CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup4 == 1:
                decodedList.append("400mA SWITCHED")    # 1.44W - Function 0x1 of function group 4
            if CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup4 == 2:
                decodedList.append("600mA SWITCHED")    # 2.16W - Function 0x2 of function group 4
            if CMD6.statusDataStructure.uiFunctionSelectionOfFunctionGroup4 == 3:
                decodedList.append("800mA SWITCHED")    # 2.88W - Function 0x3 of function group 4

        return decodedList

    def DecodeSwitchCommandResponse(self, operationalMode, CMD6):
        """
        DecodeSwitchCommandResponse decodes the response buffer of CMD6.
        Refer section 4.3.10.4 or table 4-13 in spec 7.0
        """
        if type(CMD6) == ServiceWrap.Buffer:
            decodedList = self.DecodeSwitchCommandResponseFromBuffer(operationalMode, CMD6)
        else:
            decodedList = self.DecodeSwitchCommandResponseFromObject(operationalMode, CMD6)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DecodedSwitchCommandResponse %s" % decodedList)
        return decodedList

###----------------------------- Command Response Decode End -----------------------------###

###----------------------------- Card Initialization Part Start -----------------------------###

    def DoBasicInit(self):
        self.FUNCTION_ENTRY("DoBasicInit")

        if ((self.vtfContainer.isModel == 1) or (self.DEVICE_FPGA_TMP == 1)) and (self.currCfg.variation.sdconfiguration != "SPI"):
            self.CardInit_WithSendBasicCmd_Interface()
            return 0

        if self.vtfContainer.isModel == 1:
            self.__fpgadownload = True
        if self.currCfg.variation.lv == 1:
            self.__fpgadownload = False

        if(self.__basicInitFlag == 0):

            if self.__fpgadownload == False:
                self.Download_SDRBin()
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Already FPGA Image is Downloaded")

            if(self.IsSDRFwLoopback() == True):
                self.__basicInitFlag = 1

            import SDDVT.Config_SD.ConfigSD_UT002_GlobalInitCard as globalInitCard
            self._LVInitDone = False

            if self.__globalProjectConfVar == None:     # Allows for One time call for globalPresetting file
                import SDDVT.Config_SD.ConfigSD_UT005_GlobalPreTestingSettings as globalPreTestingSettings
                globalPreTestingSettingsObj = globalPreTestingSettings.globalPreTestingSettings(self.vtfContainer)
                self.__globalProjectConfVar = globalPreTestingSettingsObj.Run()

            globalInitCardObj = globalInitCard.globalInitCard(self.vtfContainer)
            # For GlobalPreSetting and GlobalSDinitcard
            globalInitCardObj.Run(self.__globalProjectConfVar)

        if (self.currCfg.variation.cq == 1):
            sdcmdWrap.EnablePGNInterruptForCmdQ(0)
            self._CQDevConfigDict = {"CQ Enable": False, "Cache Enable": False, "Mode": "Voluntary", "CQ Depth": 0}
            self.CQTaskAgeingDict = collections.OrderedDict(("Task%d" % task, "NQ") for task in range(0, gvar.GlobalConstants.CQ_MAX_QUEUE_DEPTH))
            self._AgedOut = False
            self._AgedTaskID = None
            self.pgnenable = 0

        self.FUNCTION_EXIT("DoBasicInit")
        return self.__globalProjectConfVar


    #def DoBasicInit(self):
        #self.FUNCTION_ENTRY("DoBasicInit")

        #if self.vtfContainer.isModel == 1:
            #self.__fpgadownload = True
        #if self.currCfg.variation.lv == 1:
            #self.__fpgadownload = False

        #if(self.__basicInitFlag == 0):

            ## Download FPGA file for SD_IN_SPI card selected
            #if self.__fpgadownload == False:
                #sdcmdWrap.SetPower(0)   # 1 for on, 0 for off

                #self.Download_SDRBin()

                #sdcmdWrap.SwitchHostVoltageRegion(False)    # True - switch to 1.8V / False - switch to 3.3V
                #ResetTO=1000
                #WriteTO=550#250
                #ReadTO=200
                #sdcmdWrap.CardSetTimeout(ResetTO, WriteTO, ReadTO)

                #sdcmdWrap.SetPower(1)   # 1 for on, 0 for off
            #else:
                #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Already FPGA Image is Downloaded")
            ##self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SD_LEGACY-SDR2_2-01-00-0001 is set.")

            #if(self.IsSDRFwLoopback() == True):
                #self.__basicInitFlag = 1

            #self.CardInitialization()

        #if (self.currCfg.variation.cq == 1):
            #sdcmdWrap.EnablePGNInterruptForCmdQ(0)
            #self._CQDevConfigDict = {"CQ Enable": False, "Cache Enable": False, "Mode": "Voluntary", "CQ Depth": 0}
            #self.CQTaskAgeingDict = collections.OrderedDict(("Task%d" % task, "NQ") for task in range(0, gvar.GlobalConstants.CQ_MAX_QUEUE_DEPTH))
            #self._AgedOut = False
            #self._AgedTaskID = None
            #self.pgnenable = 0

        #self.FUNCTION_EXIT("DoBasicInit")


    def INITCARD(self, SpeedMode = 0):
        """
        Description: This function initialize the card and set the frequency
        It does not require power cycle.
        Usage: It can be used directly, if power off on is used before calling this function
        """
        # Unlock - Init
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#" * 150)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Resetting the card and passing init sequence again")
        self.__relativeCardAddress = 0

        globalOCRArgValue = int(self.__config.get('globalOCRArgValue'))

        Set_XPC_bit, Send_CMD11_in_the_next_card_init = self.Get_SDXC_SETTINGS()
        if Set_XPC_bit == 1:
            globalOCRArgValue = globalOCRArgValue | 0x10000000  # Enabling XPC bit of ACMD41 command argument

        Expected_Resp = sdcmdWrap.CardReset(
            sdcmdWrap.CARD_MODE.Sd,
            ocr = globalOCRArgValue,    # default value is 0xFF8000
            cardSlot = 1,           # default value is 1
            bSendCMD8 = True,       # default value is False
            initInfo = None,        # default value is NULL
            rca = 0,                # default value is 0
            time = 0,               # default value is 0
            sendCMD0 = 1,           # default value is 1
            bHighCapacity = True,   # default value is True
            bSendCMD58 = True,      # default value is False
            version = 1,            # default value is 1
            VOLA = 1,               # default value is 1
            cmdPattern = 0xAA,      # default value is 0xAA
            reserved = 0,           # default value is 0
            sendCMD1 = False        # default value is False
        )

        # check bit 24 in ocr whether it supports switching 1.8V
        if (((Expected_Resp >> 24) & 1) == 1) and (Send_CMD11_in_the_next_card_init == 1):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Sending CMD11 to switch to 1.8v")
            sdcmdWrap.VoltageSwitch(sdr_switchTo1_8 = True, sdr_timeToClockOff = 0, sdr_clockOffPeriod = 5)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VoltageSwitch Completed")

        self.Cmd2()
        self.Cmd3()
        sdcmdWrap.SetCardRCA(self.__relativeCardAddress)

        sdcmdWrap.SDRSetFrequency(25 * 1000 * 1000)     # 25MHz required as per SD Spec

        self.Cmd9()
        self.Cmd7()

        # Switch to High Speed if High Speed is supported, then Set Frequency to 50MHz. If Default Speed, Set Frequency to 25MHz.
        if SpeedMode == 1:
            CMD6 = self.CardSwitchCmd(mode = gvar.CMD6.CHECK, arginlist = [0x1, 0xF, 0x0, 0xF, 0xF, 0xF], blocksize = 0x40)
            decodedResponse = self.DecodeSwitchCommandResponse("CHECK", CMD6)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s" % (decodedResponse))

            CMD6 = self.CardSwitchCmd(mode = gvar.CMD6.SWITCH, arginlist = [0x1, 0xF, 0x0, 0xF, 0xF, 0xF], blocksize = 0x40)
            decodedResponse = self.DecodeSwitchCommandResponse("SWITCH", CMD6)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%s" % (decodedResponse))

            sdcmdWrap.SDRSetFrequency(50 * 1000 * 1000)
        else:
            sdcmdWrap.SDRSetFrequency(25 * 1000 * 1000)

    def DoInitIDD(self, SpeedMode = 0):
        LowSpeed = 0
        HighSpeed = 1

        # Power Cycle
        sdcmdWrap.SDRPowerCycle()

        #Power Off
        sdcmdWrap.SetPower(0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power is off!!!!")

        #Set Frequency to 20MHz
        sdcmdWrap.SDRSetFrequency(freq = 20 * 1000 * 1000)

        #Power On
        sdcmdWrap.SetPower(1)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power is On!!!!")

        #Unlock - Init
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#" * 150)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Resetting the card and passing init sequence again")
        self.__relativeCardAddress = 0

        sdcmdWrap.SDRSetFrequency(freq = 300 * 1000)
        self.Cmd0()
        self.Cmd8()

        CCS = 0x80
        OCR_BYTE_31 = 0
        i = 0
        while ((OCR_BYTE_31 & CCS) == 0x00) and (i < 100):
            self.Cmd55()
            OCR_BYTE_31 = self.ACmd41(hcs = 1 , xpc = 1, s18r = 1)
            i += 1

        self.Cmd2()
        self.Cmd3()
        self.Cmd9()
        self.Cmd7()

        #Switch to High Speed if High Speed is supported
        if SpeedMode == HighSpeed:
            responseBuff = ServiceWrap.Buffer.CreateBuffer(0x40, 0x0, isSector = False)
            CardSwitchCmd = sdcmdWrap.SwitchFunction(SwitchMode = gvar.CMD6.CHECK, args6 = [0x1, 0xF, 0x0, 0xF, 0xF, 0xF], buffer = responseBuff, BlockLen = 0x40)
            decodedResponse  = self.DecodeSwitchCommandResponse("CHECK", responseBuff)
            CardSwitchCmd = sdcmdWrap.SwitchFunction(SwitchMode = gvar.CMD6.SWITCH, args6 = [0x1, 0xF, 0x0, 0xF, 0xF, 0xF], buffer = responseBuff, BlockLen = 0x40)
            decodedResponse  = self.DecodeSwitchCommandResponse("SWITCH", responseBuff)

        #Set Bus Width to 4
        sdcmdWrap.SetBusWidth(uiBusWidth = 4)

        #Set Frequency to 25MHz if LowSpeed or 50MHz if HighSpeed
        if SpeedMode == HighSpeed:
            sdcmdWrap.SDRSetFrequency(freq = 50 * 1000 * 1000)
        else:
            sdcmdWrap.SDRSetFrequency(freq = 25 *1000 * 1000)

    def Download_SDRBin(self, filepath = None):
        self.FUNCTION_ENTRY("Download_SDRBin")

        if filepath == None:
            CVF_PATH = os.getenv('SANDISK_CTF_HOME_X64')
            if not CVF_PATH:
                raise ValidationError.VtfGeneralError(self.fn, "Failed to Read CVF Path using SANDISK_CTF_HOME_X64 Env Variable")
        else:
            CVF_PATH = filepath

        if self.currCfg.variation.cq == 0:

            # SDR104/DDR200/Legacy modes
            if self.currCfg.variation.sdconfiguration == "UHS104" or self.currCfg.variation.sdconfiguration == "SDR104":
                # SDR104 LV Configuration
                if self.currCfg.variation.lv == 1:
                    path = CVF_PATH + r"\FPGA"
                    for root, dirs, files in os.walk(path):
                        for s in files:
                            if s.startswith('SDR104_'):
                                path = os.path.join(root, s)
                else:
                    path = CVF_PATH + r"\FPGA\SD-SDR2_2-01-01-0061.bin"

            # DDR200
            elif self.currCfg.variation.sdconfiguration == "DDR200":
                path = CVF_PATH + r"\FPGA"
                for root, dirs, files in os.walk(path):
                    for s in files:
                        if s.startswith('SDR104_'):
                            path = os.path.join(root, s)

            # Legacy modes < SDR104
            else:
                path = CVF_PATH + r"\FPGA\SD_LEGACY-SDR2_2-01-00-0001.bin"

        # CQ Mode
        elif self.currCfg.variation.cq == 1:
            path = CVF_PATH + r"\FPGA"

            # all CQ configurations < SDR104
            if(self.currCfg.variation.sdconfiguration != "SDR104" and self.currCfg.variation.sdconfiguration != "DDR200"):
                for root, dirs, files in os.walk(path):
                    for s in files:
                        if s.find('A1A2') != -1:
                            path = os.path.join(root, s)

            # SDR104 mode CQ
            elif(self.currCfg.variation.sdconfiguration == "SDR104"):
                for root, dirs, files in os.walk(path):
                    for s in files:
                        if s.find('104CQ') != -1:
                            path = os.path.join(root, s)

            # DDR200 mode CQ FPGA
            else:
                for root, dirs, files in os.walk(path):
                    for s in files:
                        if s.startswith('SDR104_DDR200'):
                            path = os.path.join(root, s)

        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CommandLine value %s given for CQ bin file download is not valid" % (self.currCfg.variation.cq))
            raise ValidationError.InvalidArgument(self.fn, "%s" % self.currCfg.variation.cq, "0 or 1")

        returnvalue = sdcmdWrap.DownloadFpgaFile(path)
        if returnvalue != 0:
            raise ValidationError.TestFailError(self.fn, "Failed to find/download %s" % path)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FPGA Image Downloaded Is: %s" % path)

        if self.currCfg.variation.lv == 0:
            self.__fpgadownload = True

        self.FUNCTION_EXIT("Download_SDRBin")


    def CardInitialization(self):
        self.FUNCTION_ENTRY("CardInitialization")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Resetting SD card")
        initInfo = ServiceWrap.Buffer.CreateBuffer(1, patternType = ServiceWrap.ALL_0, isSector = True)
        OCR = sdcmdWrap.CardReset(
            sdcmdWrap.CARD_MODE.Sd,
            ocr = int(self.__config.get('globalOCRArgValue')),     #default value is 0xFF8000
            cardSlot = 1,           #default value is 1
            bSendCMD8 = True,       #default value is False
            initInfo = initInfo,    #default value is NULL
            rca = 0,                #default value is 0
            time = 0,               #default value is 0
            sendCMD0 = 1,           #default value is 1
            bHighCapacity = True,   #default value is True
            bSendCMD58 = True,      #default value is False
            version = 1,            #default value is 1
            VOLA = 1,               #default value is 1
            cmdPattern = 0xAA,      #default value is 0xAA
            reserved = 0,           #default value is 0
            sendCMD1 = False        #default value is False
        )
        self.OCRRegister = OCR
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Response of CardReset: 0x%X" % OCR)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "SDRSystemInit and SDCardInit")
        sdcmdWrap.WrapSDRSystemInit()
        sdcmdWrap.WrapSDCardInit()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power off and Power on")
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Setting Host Frequency to 300KHz")
        Frequency = 300 * 1000      # 300 KHz or 0.3 MHz
        sdcmdWrap.SDRSetFrequency(freq = Frequency, sendType = ServiceWrap.CMD_SEND_TYPE.SEND_IMMEDIATE_SYNC)

        def Set_Voltage(MaxCurrent):
            VoltStructObj = sdcmdWrap.SVoltage()
            VoltStructObj.voltage = 3300
            VoltStructObj.maxVoltage = 3800
            VoltStructObj.maxCurrent = MaxCurrent
            VoltStructObj.regionSelect = sdcmdWrap.REGION_SELECT_PARTIAL_1V8
            VoltStructObj.actualVoltage = 0
            VoltStructObj.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ
            sdcmdWrap.SDRSetVolt(voltStruct = VoltStructObj, pStatusReg = 0, bVddfValue = False)

        Set_Voltage(MaxCurrent = 100)
        Set_Voltage(MaxCurrent = 300)

        ResetTO = 800
        WriteTO = 250
        ReadTO = 100
        sdcmdWrap.CardSetTimeout(ResetTO, WriteTO, ReadTO)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Resetting SD card")
        initInfo = ServiceWrap.Buffer.CreateBuffer(1, patternType = ServiceWrap.ALL_0, isSector = True)
        OCR = sdcmdWrap.CardReset(mode = sdcmdWrap.CARD_MODE.Sd, ocr = int(self.__config.get('globalOCRArgValue')),
                                  cardSlot = 1, bSendCMD8 = True, initInfo = initInfo, rca = 1, time = 0,
                                  sendCMD0 = 1, bHighCapacity = True, bSendCMD58 = False, version = 1,
                                  VOLA = 1, cmdPattern = 0xAA, reserved = 0, sendCMD1 = False)
        self.OCRRegister = OCR
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Response of CardReset : 0x%X" % OCR)

        if ((OCR >> 24) & 1 == 1):      # OCR - Operating Condition Register
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Sending CMD11 to switch to 1.8v")
            sdcmdWrap.VoltageSwitch(sdr_switchTo1_8 = True, sdr_timeToClockOff = 0, sdr_clockOffPeriod = 5)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VoltageSwitch Completed")

        ResetTO = 800
        WriteTO = 250
        ReadTO = 100
        sdcmdWrap.CardSetTimeout(ResetTO, WriteTO, ReadTO)

        self.Cmd2()

        self.Cmd3()
        sdcmdWrap.SetCardRCA(self.__relativeCardAddress)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Setting Host Frequency to 25MHz")
        Frequency = 25 * 1000 * 1000
        sdcmdWrap.SDRSetFrequency(freq = Frequency, sendType = ServiceWrap.CMD_SEND_TYPE.SEND_IMMEDIATE_SYNC)

        busWidth = 4
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Bus width set to", busWidth))
        ACMD6 = sdcmdWrap.SetBusWidth(uiBusWidth = busWidth)

        self.globalSetSpeedMode(mode = self.currCfg.variation.sdconfiguration)

        CardTransferMode = sdcmdWrap.GetCardTransferMode()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('CardTransferMode is', CardTransferMode))
        self.FUNCTION_EXIT("CardInitialization")


    def CardReinit(self, sendCMD0 = 0):
        """
        Reinitialize the card
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_HEADER(self.GL_REINIT_CARD))
        self.FUNCTION_ENTRY("CardReinit")

        if self.DEVICE_FPGA_TMP == 1:
            self.CardInit_WithSendBasicCmd_Interface()
        else:
            globalProjectConfVar = self.__globalProjectConfVar
            # Get the values from Project Configuration
            globalSpeedMode = globalProjectConfVar['globalSpeedMode']
            globalCardRCA = globalProjectConfVar['globalCardRCA']
            globalOCRArgValue = globalProjectConfVar["globalOCRArgValue"]

            if((self.currCfg.variation.cq == 1) and (self.pgnenable == 1)):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Disabling PGN interrupt")
                sdcmdWrap.EnablePGNInterruptForCmdQ(0)

                self._CQDevConfigDict = {"CQ Enable": False, "Cache Enable": False, "Mode": "Voluntary", "CQ Depth": 0}
                self.CQTaskAgeingDict = collections.OrderedDict(("Task%d" % task, "NQ") for task in range(0, gvar.GlobalConstants.CQ_MAX_QUEUE_DEPTH))

                self._AgedOut = False
                self._AgedTaskID = None
                self.pgnenable = 0

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Setting Host Frequency to %dKHz" % globalProjectConfVar['globalResetFreq'])
            sdcmdWrap.SDRSetFrequency(globalProjectConfVar['globalResetFreq'] * 1000)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Resetting SD card")
            if self.currCfg.variation.lv == 1:  # LV
                OCR = sdcmdWrap.CardReset(sdcmdWrap.CARD_MODE.Sd, ocr = 0x40FF8000, cardSlot = 1, bSendCMD8 = True,
                                          initInfo = None, rca = globalCardRCA, time = 0, sendCMD0 = sendCMD0,
                                          bHighCapacity = True, bSendCMD58 = True, version = 1, VOLA = 2,
                                          cmdPattern = 0xA5, reserved = 0, sendCMD1 = False)
            else:  # legacy
                OCR = sdcmdWrap.CardReset(sdcmdWrap.CARD_MODE.Sd, ocr = globalOCRArgValue, cardSlot = 1,
                                          bSendCMD8 = True, initInfo = None, rca = globalCardRCA, time = 0,
                                          sendCMD0 = sendCMD0, bHighCapacity = True, bSendCMD58 = True,
                                          version = 1, VOLA = 1, cmdPattern = 0xAA, reserved = 0, sendCMD1 = False)
            self.OCRRegister = OCR
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Response of CardReset : 0x%X" % OCR)

            globalPowerUp = True if (globalProjectConfVar['globalPowerUp'] == 'powerCycle' or globalProjectConfVar['globalPowerUp'] == 'powerCycleNoCMD0') else False

            if (globalSpeedMode in ["SDR12", "SDR25", "SDR50", "SDR104", "DDR50", "DDR200"]) and globalPowerUp and self.currCfg.variation.lv == 0:
                if ((OCR >> 24) & 1 == 1):      # OCR - Operating Condition Register
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Sending CMD11 to switch to 1.8v")

                    try:
                        sdcmdWrap.VoltageSwitch(sdr_switchTo1_8 = True, sdr_timeToClockOff = 0, sdr_clockOffPeriod = 5)
                        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VoltageSwitch Completed")

                    except ValidationError.CVFGenericExceptions as exc:
                        self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VoltageSwitch Command failed")
                        raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

            if ((globalProjectConfVar['globalCardType'] == 'SD') and (globalProjectConfVar['globalProtocolMode'] == 'SD')):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification of card(CMD2 and CMD3)")
                try:
                    # ResetTO = 800
                    # WriteTO = 250
                    # ReadTO = 100
                    # sdcmdWrap.CardSetTimeout(ResetTO, WriteTO, ReadTO)
                    self.Cmd2()

                    self.Cmd3()
                    sdcmdWrap.SetCardRCA(self.__relativeCardAddress)

                    sdcmdWrap.SDRSetFrequency(globalProjectConfVar['globalLSHostFreq'] * 1000)        # Frequency value in KHz
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Identification of card completed")

                except ValidationError.CVFExceptionTypes as exc:
                    exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                    self.ErrorPrint(exc)
                    raise ValidationError.TestFailError(self.fn, exc.GetFailureDescription())
                except ValidationError.CVFGenericExceptions as exc:
                    raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

            # Set the bus Width
            if globalProjectConfVar["globalBusMode"] == "Four":
                BUS_WIDTH = 4
            else:
                BUS_WIDTH = 1

            # Set the bus Width
            try:
                sdcmdWrap.SetBusWidth(uiBusWidth = BUS_WIDTH)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus width is set to %d" % BUS_WIDTH)
            except ValidationError.CVFGenericExceptions as exc:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus width is not set to %d, which is not Expected" % BUS_WIDTH)
                self.ErrorPrint(exc)
                raise ValidationError.TestFailError(self.fn, "Buswidth setting failed")

            # Get the Sd status and Verify for Bus Width
            try:
                self.Cmd55()
                ACMD13 = self.SD_STATUS()
            except ValidationError.CVFGenericExceptions as exc:
                self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Failed to get card SD status")
                self.ErrorPrint(exc)
                raise ValidationError.TestFailError(self.fn, "Failed to get card SD status")

            if BUS_WIDTH == 4:
                if ACMD13.objSDStatusRegister.ui64DatBusWidth == 2:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus width is set to %d and Verified" % BUS_WIDTH)
                else:
                    self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus width is not set to %d, which is not Expected" % BUS_WIDTH)
                    raise ValidationError.TestFailError(self.fn, "Buswidth %d not updated in Device" % BUS_WIDTH)
            else:
                if ACMD13.objSDStatusRegister.ui64DatBusWidth == 0:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus width is set to %d and Verified" % BUS_WIDTH)
                else:
                    self.fatalLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus width is not set to %d, which is not Expected" % BUS_WIDTH)
                    raise ValidationError.TestFailError(self.fn, "Buswidth %d not updated in Device" % BUS_WIDTH)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Setting Speed mode")
            import SDDVT.Config_SD.ConfigSD_UT013_GlobalSetSpeedMode as globalSetSpeedMode
            globalSetSpeedModeObj = globalSetSpeedMode.globalSetSpeedMode(self.vtfContainer)
            globalSetSpeedModeObj.Run(self.__globalProjectConfVar)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_INIT_DONE)
        self.FUNCTION_EXIT("CardReinit")


    def DoBasicInitIDD(self, SpeedMode = None):

        # Power Cycle for half sec
        sdcmdWrap.SDRPowerCycle()

        # Power Off
        sdcmdWrap.SetPower(0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power is off!!!!")

        # Set Frequency to 20MHz
        sdcmdWrap.SDRSetFrequency(freq = 20 * 1000 * 1000)

        # Set SD Voltage to 3.3V
        VoltStructObj = sdcmdWrap.SVoltage()
        VoltStructObj.voltage = 3300
        VoltStructObj.maxVoltage = 3800
        VoltStructObj.maxCurrent = 250
        VoltStructObj.regionSelect = sdcmdWrap.REGION_SELECT_PARTIAL_1V8
        VoltStructObj.actualVoltage = 0
        VoltStructObj.A2DOutrateType = sdcmdWrap.A2D_OUT_RATE_SELECT.A2D_62_5_HZ
        sdcmdWrap.SDRSetVolt(voltStruct = VoltStructObj, pStatusReg = 0, bVddfValue = gvar.PowerSupply.VDDF)

        # Power On
        sdcmdWrap.SetPower(1)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power is on!!!!")

        # Unlock - Init
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#" * 150)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Resetting the card and passing init sequence again")

        self.__relativeCardAddress = 0

        sdcmdWrap.SDRSetFrequency(freq = 300 * 1000)
        self.Cmd0()
        self.Cmd8()

        CCS=0x80
        OCR_BYTE_31 = 0
        i = 0
        while ((OCR_BYTE_31 & CCS) == 0x00) and (i < 100):
            self.Cmd55()
            OCR_BYTE_31 = self.ACmd41(hcs = 1, xpc = 1, s18r = 1, ho2t = 0)
            i += 1

        self.Cmd2()
        self.Cmd3()
        sdcmdWrap.SetCardRCA(rca = self.__relativeCardAddress)
        sdcmdWrap.SDRSetFrequency(freq = 25 * 1000 * 1000)
        self.Cmd9()
        self.Cmd7()

        # Switch to High Speed if High Speed is supported
        if SpeedMode == 'HighSpeed':
            responseBuff = ServiceWrap.Buffer.CreateBuffer(0x40, patternType = 0x0, isSector = False)
            CMD6 = self.CardSwitchCmd(mode = gvar.CMD6.CHECK, arginlist = [0x1, 0xF, 0x0, 0xF, 0xF, 0xF], responseBuff = responseBuff, blocksize = 0x40)
            decodedResponse = self.DecodeSwitchCommandResponse(operationalMode = "CHECK", CMD6 = CMD6)

            responseBuff = ServiceWrap.Buffer.CreateBuffer(0x40, patternType = 0x0, isSector = False)
            CMD6 = self.CardSwitchCmd(mode = gvar.CMD6.SWITCH, arginlist = [0x1, 0xF, 0x0, 0xF, 0xF, 0xF], responseBuff = responseBuff, blocksize = 0x40)
            decodedResponse = self.DecodeSwitchCommandResponse(operationalMode = "SWITCH", CMD6 = CMD6)

        busWidth = 4
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Bus width set to", busWidth))
        ACMD6 = sdcmdWrap.SetBusWidth(uiBusWidth = busWidth)

        # Set Frequency to 25MHz
        sdcmdWrap.SDRSetFrequency(freq = 25 * 1000 * 1000)


    def R(self, OCRArgValue = 0x41FF8000):
        """
        Description : This function does the soft reset. Issue power cycle + Reset/Identify card.
        """
        sdcmdWrap.SetPower(0)
        sdcmdWrap.SetPower(1)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Power is On!!!!")

        Set_XPC_bit, Send_CMD11_in_the_next_card_init = self.Get_SDXC_SETTINGS()
        if Set_XPC_bit == 1:
            OCRArgValue = OCRArgValue | 0x10000000  # Enabling XPC bit of ACMD41 command argument

        Expected_Resp = sdcmdWrap.CardReset(sdcmdWrap.CARD_MODE.Sd, ocr = OCRArgValue, cardSlot = 1, bSendCMD8 = True,
                                            initInfo = None, rca = 0, time = 0, sendCMD0 = 1, bHighCapacity = True,
                                            bSendCMD58 = True, version = 1, VOLA = 1, cmdPattern = 0xAA, reserved = 0,
                                            sendCMD1 = False)
        self.OCRRegister = Expected_Resp

        # check bit 24 in ocr whether it supports switching 1.8V
        if (((Expected_Resp >> 24) & 1) == 1) and (Send_CMD11_in_the_next_card_init == 1):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Sending CMD11 to switch to 1.8v")
            sdcmdWrap.VoltageSwitch(sdr_switchTo1_8 = True, sdr_timeToClockOff = 0, sdr_clockOffPeriod = 5)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "VoltageSwitch Completed")

        self.Cmd2()
        self.Cmd3()
        sdcmdWrap.SetCardRCA(rca = self.__relativeCardAddress)
        sdcmdWrap.SDRSetFrequency(25 * 1000 * 1000)     # 25MHz required as per SD Spec
        self.Cmd9()
        self.Cmd7()
        self.SPIEnable(False)       # Get to default state


    def RR(self):
        """
        Description : Same as R function(R directive in scripter) plus test unlock that will put the card into test mode.
        """
        self.R()

        # Call PutCardInTestMode function (UNLOCK directive in scripter) to put the card into test mode
        self.PutCardInTestMode()


    def Update_UHS_ConfigValues(self, SpeedMode = "SDR50"):

        self.currCfg.variation.sdconfiguration = SpeedMode

        if self.__globalProjectConfVar == None:     # Allows for One time call for globalPresetting file
            import SDDVT.Config_SD.ConfigSD_UT005_GlobalPreTestingSettings as globalPreTestingSettings
            globalPreTestingSettingsObj = globalPreTestingSettings.globalPreTestingSettings(self.vtfContainer)
            self.__globalProjectConfVar = globalPreTestingSettingsObj.Run()
        else:
            config = getconfig.getconfig()
            self.__globalProjectConfVar["globalVHSHostFreq"] = config.get('globalVHSHostFreq')
            self.__globalProjectConfVar["globalSpeedMode"] = config.get('globalSpeedMode')
            self.__globalProjectConfVar['temp_globalSpeedMode'] = config.get('globalSpeedMode')


    def SoftReset(self, OCRArgValue = 0x41FF8000):
        self.R(OCRArgValue = OCRArgValue)


    def CardInit_WithSendBasicCmd_Interface(self):
        self.FUNCTION_ENTRY("CardInit_WithSendBasicCmd_Interface")

        if (self.currCfg.variation.cq == 1) and (self.vtfContainer.isModel == 0):
            sdcmdWrap.EnablePGNInterruptForCmdQ(1)
            self.pgnenable = 0

        sdcmdWrap.SDRSetFrequency(300 * 1000)
        self.Cmd0()
        self.Cmd8()

        # Case 1: Using SendBasicCommand API
        Busy_Status=0x80
        OCR_BYTE_31 = 0
        i = 0
        while(((OCR_BYTE_31 & Busy_Status) == 0x00) and (i < 100)):
            self.Cmd55()
            OCR_BYTE_31 = self.ACmd41(1,1,1, ho2t=0)
            i += 1

        # Case 2: Using CVF Wrapper API
        # OCR_BYTE_31 = 0
        # i = 0
        # while((OCR_BYTE_31 == 0x0) and (i < 100)):
        #     self.Cmd55()
        #     ACMD41 = self.ACmd41(HCS = True, XPC = True, S18R = True, VddVoltageWindow = 0xFF8000)
        #     OCRReg_32bit_Response_from_31bit_to_0bit = '{:032b}'.format(ACMD41.pyResponseData.r3Response.uiOCRReg)
        #     OCRReg_32bit_Response_from_0bit_to_31bit = OCRReg_32bit_Response_from_31bit_to_0bit[::-1]
        #     OCR_BYTE_31 = OCRReg_32bit_Response_from_0bit_to_31bit[31]
        #     i += 1

        # Case 3: Using CVF Wrapper API
        #timeOutStart = time.time()
        #while(True):
            #self.Cmd55()
            #ACMD41 = self.ACmd41(HCS = True, XPC = True, S18R = True, VddVoltageWindow = 0xFF8000)

            #OCRReg_32bit_Response_from_31bit_to_0bit = '{:032b}'.format(ACMD41.pyResponseData.r3Response.uiOCRReg)
            #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "OCRReg_32bit_Response_from_31bit_to_0bit : %s" % OCRReg_32bit_Response_from_31bit_to_0bit)

            #OCRReg_32bit_Response_from_0bit_to_31bit = OCRReg_32bit_Response_from_31bit_to_0bit[::-1]
            #timeOutEnd = time.time()

            ## if 32nd bit(Card Power Up bit) of OCR Register is 1(that means card power up procedure have been finished and
            ## card is in ready state) or ACMD41 should have been sending for 1 second. If card power up was finished
            ## within 1 second break the loop and continue the script further.
            #if (OCRReg_32bit_Response_from_0bit_to_31bit[31] == 1):
                #break
            #elif((timeOutEnd - timeOutStart) > 1):
                #raise ValidationError.TestFailError(self.fn, "Card did not go to ready state even after ACMD41 had been giving for 1 second")

        self.Cmd2()             #CMD2
        self.Cmd3()      #CMD3
        self.Cmd9()       #CMD9
        self.Cmd7()       #CMD7

        sdcmdWrap.SDRSetFrequency(20 * 1000 * 1000)

        self.FUNCTION_EXIT("CardInit_WithSendBasicCmd_Interface")


    def CQ_LV_FPGA_Download(self):
        # Downloading the CQ FPGA image
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Downloading FPGA ..........\n\n")

        CVF_PATH = os.getenv('SANDISK_CTF_HOME_X64')
        if not CVF_PATH:
            raise ValidationError.VtfGeneralError(self.fn, "Failed to Read CVF Path using SANDISK_CTF_HOME_X64 Env Variable")

        if (self.currCfg.variation.cq == 1):
            path = CVF_PATH + r"\FPGA"
            for root, dirs, files in os.walk(path):
                for s in files:
                    if s.startswith('SD_CQ_A1A2'):
                        path = os.path.join(root, s)
        else:
            path = CVF_PATH + r"\FPGA\SD_LEGACY-SDR2_2-01-00-0001.bin"

        returnvalue = sdcmdWrap.DownloadFpgaFile(path)

        if returnvalue != 0:
            raise ValidationError.TestFailError(self.fn, "Failed to find/download %s" % path)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FPGA Image Downloaded Is: %s\n" % path)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FPGA Downloaded successfully\n\n")


    def BatchMode_FPGA_Download(self):
        # Downloading the CQ FPGA image
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Downloading BatchMode FPGA ..........\n\n")
        if (self.currCfg.variation.cq == 1):
            CVF_PATH = os.getenv('SANDISK_CTF_HOME_X64')
            path = CVF_PATH + r"\FPGA"
            for root, dirs, files in os.walk(path):
                for s in files:
                    if s.startswith('SD_CQ_BatchMode'):
                        path = os.path.join(root, s)

        retunrvalue = sdcmdWrap.DownloadFpgaFile(path)
        if retunrvalue != 0:
            raise ValidationError.TestFailError(self.fn, "Failed to find/download " + path)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FPGA Image Downloaded Is: %s" % path)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FPGA Downloaded successfully\n\n")

###----------------------------- Card Initialization Part End -----------------------------###

###----------------------------- Diagnostic Command Start -----------------------------###

    def SendDiagnostic(self, dataBuffer, cdbData, direction, enableStatusPhase = True,
                       sctpAppSignature = None, TimeOut = 20000,
                       SendType = ServiceWrap.CMD_SEND_TYPE.SEND_IMMEDIATE, commandName = "Diagnostic command"):
        """
        Generic SendDiagnostic command, Executes the Diagnostic command
        SendDiagnostic common function to execute the Diagnostic Command for SD card.
        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Executing %s diagnostic command" % commandName)

        try:
            ServiceWrap.SCTPCommand.SCTPCommand(fbcccdb = cdbData, objBuffer = dataBuffer, enDataDirection = direction,
                                                bIsStatusPhasePresent = enableStatusPhase, sctpAppSignature = sctpAppSignature,
                                                dwTimeOut = TimeOut, sendType = SendType)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FBCC Command %s failed" % commandName)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        return dataBuffer


    def GetMConf(self):
        """
        Generic SendDiagnostic command, Executes the Diagnostic command.
        Returns: MConf Buffer
        GetMConf returns the MConf Buffer from the Card.
        """
        # self.FUNCTION_ENTRY("GetMConf")

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
            self.SendDiagnostic(dataBuffer = mConfBuf, cdbData = cdbData, direction = ServiceWrap.SCTP_DATA_DIRECTION.DIRECTION_OUT,
                                enableStatusPhase = True, commandName = "MConf Diagnostic")
        except ValidationError.CVFGenericExceptions as exc:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Diagnostic command failed with Opcode: 0x%X, SubOpcode: 0x%X\n" % (opCode, subOpCode))
            raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

        # self.FUNCTION_EXIT("GetMConf")
        return mConfBuf


    def SecureFormatProcess(self):
        # self.FUNCTION_ENTRY("SecureFormatProcess")
        buf = ServiceWrap.Buffer.CreateBuffer(1, patternType = ServiceWrap.ALL_1, isSector = True)

        diagCmd = ServiceWrap.DIAG_FBCC_CDB()
        options = 1
        # 16 number list - Command buffer
        diagCmd.cdb = [0x91, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        diagCmd.cdbLen = 16
        diagCmd.cdb[2] = (options & 0xFF)
        diagCmd.cdb[3] = (options >> 8) & 0xFF

        try:
            self.SendDiagnostic(dataBuffer = buf, cdbData = diagCmd, direction = ServiceWrap.SCTP_DATA_DIRECTION.DIRECTION_NONE,
                                enableStatusPhase = False,
                                commandName = "SecureFormatProcess Diagnostic Command")
        except ValidationError.CVFGenericExceptions as exc:
            self.ErrorPrint(exc)
            raise ValidationError.TestFailError(self.fn, exc.GetInternalErrorMessage())

        # self.FUNCTION_EXIT("SecureFormatProcess")
        return buf


    def PutCardInTestMode(self):
        """
        # Call PutCardInTestMode function (UNLOCK directive in scripter) to put the card into test mode
        """
        opcode = 0x8089

        diagCmd = ServiceWrap.DIAG_FBCC_CDB()
        diagCmd.cdb = [0x80, 0x89, 0, 0,
                       0, 0, 0, 0,
                       0, 0, 0, 0,
                       0, 0, 0, 0]
        diagCmd.cdbLen = 16

        dataBuffer = ServiceWrap.Buffer.CreateBuffer(1, patternType = ServiceWrap.ALL_0, isSector = True)
        self.SendDiagnostic(dataBuffer = dataBuffer, cdbData = diagCmd,
                            direction = ServiceWrap.SCTP_DATA_DIRECTION.DIRECTION_IN, commandName = "Unlock")

    def ReadFirmwareParameter(self):
        """
        TOBEDONE: YetTo check the exact opcode. Refer JIRA CVF-20375 for more info.
        """
        rbuff = ServiceWrap.Buffer.CreateBuffer(1, patternType = ServiceWrap.ALL_0, isSector = True)
        cdbData = ServiceWrap.DIAG_FBCC_CDB()
        # 16 number list - Command buffer
        cdbData.cdb = [2, 0, 0, 0,
                       0, 0, 0, 0,
                       0, 0, 0, 0,
                       0, 0, 0, 0]
        cdbData.cdbLen = 16
        self.SendDiagnostic(rbuff, cdbData, direction = ServiceWrap.SCTP_DATA_DIRECTION.DIRECTION_OUT)    # CVF-20375
        rbuff.PrintToLog()

###----------------------------- Diagnostic Command End -----------------------------###

###----------------------------- General API Start -----------------------------###


    def GET_CSD_VALUES(self):
        """
        # 128 Bit length CSD Register and for more information refer
        SD spec 7.0 Table 5-4, 5-16, 5.3.4-1 : The CSD Register Fields
        Access the fields by below keywords

        CSD_STRUCTURE       (2 bits ,            Starts at 126)
        TAAC                (1 byte ,            Starts at 112) data read access-time-1
        NSAC                (1 byte ,            Starts at 104) data read access-time-2 in CLK cycles
        TRAN_SPEED          (1 byte ,            Starts at  96) maximum data transfer rate(32h, 5Ah, 0Bh and  2Bh)
        CCC                 (1 byte and 4 bits , Starts at  84) card command classes, represented as 01x110110101b
        READ_BL_LEN         (4 bits ,            Starts at  80) maximum read data block length
        READ_BL_PARTIAL     (1 bit  ,            Starts at  79) partial blocks for read allowed
        WRITE_BLK_MISALIGN  (1 bit  ,            Starts at  78) write block misalignment
        READ_BLK_MISALIGN   (1 bit  ,            Starts at  77) read block misalignment
        DSR_IMP             (1 bit  ,            Starts at  76) DSR implemented
        C_SIZE              (Ver1 - 12 bits, Ver2 - 22 bits, Ver3 - 28 bits) device size
        ERASE_BLK_EN        (1 bit  ,            Starts at  46) erase single block enable
        SECTOR_SIZE         (7 bits ,            Starts at  39) erase sector size
        WP_GRP_SIZE         (7 bits ,            Starts at  32) write protect group size
        WP_GRP_ENABLE       (1 bit  ,            Starts at  31) write protect group enable
        R2W_FACTOR          (3 bits ,            Starts at  26) write speed factor
        WRITE_BL_LEN        (4 bits ,            Starts at  22) maximum write data block length
        WRITE_BL_PARTIAL    (1 bit  ,            Starts at  21) partial blocks for write allowed
        FILE_FORMAT_GRP     (1 bit  ,            Starts at  15) File format group
        COPY                (1 bit  ,            Starts at  14) copy flag
        PERM_WRITE_PROTECT  (1 bit  ,            Starts at  13) permanent write protection
        TMP_WRITE_PROTECT   (1 bit  ,            Starts at  12) temporary write protection
        FILE_FORMAT         (2 bits ,            Starts at  10) File format
        CRC                 (7 bits ,            Starts at  1 ) CRC
        """

        CSD = self.GetCSD()

        CSD_REG_LIST = {}

        CSD_REG_LIST[gvar.CSD.CSD_STRUCTURE] = hex(self.CSDRegister.uiCsdStructure)          # For CSD_STRUCTURE
        CSD_REG_LIST[gvar.CSD.Reserv1] = hex(self.CSDRegister.uiReserved1)                   # Reserv1
        CSD_REG_LIST[gvar.CSD.TAAC] = hex(self.CSDRegister.uiTaac)       # TAAC
        CSD_REG_LIST[gvar.CSD.NSAC] = hex(self.CSDRegister.uiNsac)       # NSAC
        CSD_REG_LIST[gvar.CSD.TRAN_SPEED] = hex(self.CSDRegister.uiTranSpeed)                # TRAN_SPEED
        CSD_REG_LIST[gvar.CSD.CCC] = hex(self.CSDRegister.uiCcc)         # CCC
        CSD_REG_LIST[gvar.CSD.READ_BL_LEN] = hex(self.CSDRegister.uiReadBlLen)               # READ_BL_LEN
        CSD_REG_LIST[gvar.CSD.READ_BL_PARTIAL] = hex(self.CSDRegister.uiReadBlPartial)       # READ_BL_PARTIAL
        CSD_REG_LIST[gvar.CSD.WRITE_BLK_MISALIGN] = hex(self.CSDRegister.uiWriteBlkMisalign) # WRITE_BLK_MISALIGN
        CSD_REG_LIST[gvar.CSD.READ_BLK_MISALIGN] = hex(self.CSDRegister.uiReadBlkMisalign)   # READ_BLK_MISALIGN
        CSD_REG_LIST[gvar.CSD.DSR_IMP] = hex(self.CSDRegister.uiDsrImp)                      # DSR_IMP
        CSD_REG_LIST[gvar.CSD.C_SIZE] = hex(self.CSDRegister.uiC_Size)                       # C_SIZE
        CSD_REG_LIST[gvar.CSD.Reserv2] = hex(self.CSDRegister.uiReserved2)                   # Reserv2
        CSD_REG_LIST[gvar.CSD.ERASE_BLK_EN] = hex(self.CSDRegister.uiEraseBlkEn)             # ERASE_BLK_EN
        CSD_REG_LIST[gvar.CSD.SECTOR_SIZE] = hex(self.CSDRegister.uiSectorSize)              # SECTOR_SIZE
        CSD_REG_LIST[gvar.CSD.WP_GRP_SIZE] = hex(self.CSDRegister.uiWpGrpSize)               # WP_GRP_SIZE
        CSD_REG_LIST[gvar.CSD.WP_GRP_ENABLE] = hex(self.CSDRegister.uiWpGrpEnable)           # WP_GRP_ENABLE
        if hasattr(self.CSDRegister, "uiReserved3"):
            CSD_REG_LIST[gvar.CSD.Reserv3] = hex(self.CSDRegister.uiReserved3)               # Reserv3
        else:
            CSD_REG_LIST[gvar.CSD.Reserv3] = hex(self.CSDRegister.uiRererved3)               # Reserv3
        # was implemented like uiRererved3 for CSD structure version 3 in CVF, Yet to inform CVF team
        CSD_REG_LIST[gvar.CSD.R2W_FACTOR] = hex(self.CSDRegister.uiR2WFactor)                # R2W_FACTOR
        CSD_REG_LIST[gvar.CSD.WRITE_BL_LEN] = hex(self.CSDRegister.uiWriteBlLen)             # WRITE_BL_LEN
        CSD_REG_LIST[gvar.CSD.WRITE_BL_PARTIAL] = hex(self.CSDRegister.uiWritEBlPartial)     # WRITE_BL_PARTIAL
        if hasattr(self.CSDRegister, "uiReserved4"):
            CSD_REG_LIST[gvar.CSD.Reserv4] = hex(self.CSDRegister.uiReserved4)               # Reserv4
        else:
            CSD_REG_LIST[gvar.CSD.Reserv4] = hex(self.CSDRegister.uiRererved4)               # Reserv4
        # was implemented like uiRererved4 for CSD structure version 2 in CVF, Yet to inform CVF team
        CSD_REG_LIST[gvar.CSD.FILE_FORMAT_GRP] = hex(self.CSDRegister.uiFileFormatGrp)       # FILE_FORMAT_GRP
        CSD_REG_LIST[gvar.CSD.COPY] = hex(self.CSDRegister.uiCopy)                           # COPY Flag
        CSD_REG_LIST[gvar.CSD.PERM_WRITE_PROTECT] = hex(self.CSDRegister.uiPerm_Write_Protect)   # PERM_WRITE_PROTECT
        CSD_REG_LIST[gvar.CSD.TMP_WRITE_PROTECT] = hex(self.CSDRegister.uiTmpWriteProtect)   # TMP_WRITE_PROTECT
        CSD_REG_LIST[gvar.CSD.FILE_FORMAT] = hex(self.CSDRegister.uiFileFormaT)              # FILE_FORMAT
        CSD_REG_LIST[gvar.CSD.Reserv5] = hex(self.CSDRegister.uiReserved5)                   # Reserv5
        CSD_REG_LIST[gvar.CSD.CRC] = hex(self.CSDRegister.uiCrc)                             # CRC
        CSD_REG_LIST[gvar.CSD.NotUsed] = hex(self.CSDRegister.uiNotUsed)                     # NotUsed
        if hasattr(self.CSDRegister, "uiReserved6"):          # Only CSD Structure Version 2 has Reserved field 6
            CSD_REG_LIST[gvar.CSD.Reserv6] = hex(self.CSDRegister.uiReserved6)

        return CSD_REG_LIST


    def CheckTransferSpeedInCSD(self, TRAN_SPEED):
        csd_value = self.GET_CSD_VALUES()
        if csd_value["TRAN_SPEED"] == TRAN_SPEED:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Data transfer rate matched to %s\n" % TRAN_SPEED)
        else:
            raise ValidationError.TestFailError(self.fn, "Failed to match data transfer rate to %s" % TRAN_SPEED)


    def GET_CID_VALUES(self):
        """
        # 128 Bit length CID Register and for more information refer
        SD spec 7.0 Table 5-2 : The CID Fields
        Access the fields by below keywords
        """
        CID = self.GetCID()

        CID_REG_LIST = {}
        CID_REG_LIST[gvar.CID.MID] = CID.cidRegisterFieldStruct.uiMid
        CID_REG_LIST[gvar.CID.OID] = CID.cidRegisterFieldStruct.uiOid
        CID_REG_LIST[gvar.CID.PNM] = CID.cidRegisterFieldStruct.uiPnm
        CID_REG_LIST[gvar.CID.PRV] = CID.cidRegisterFieldStruct.uiPrv
        CID_REG_LIST[gvar.CID.PSN] = CID.cidRegisterFieldStruct.uiPsn

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Manufacturer ID", CID.cidRegisterFieldStruct.uiMid))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("OEM/Application ID", CID.cidRegisterFieldStruct.uiOid))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Product Name", CID.cidRegisterFieldStruct.uiPnm))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Product Revision", CID.cidRegisterFieldStruct.uiPrv))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Product Serial Number", CID.cidRegisterFieldStruct.uiPsn))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Reserved", CID.cidRegisterFieldStruct.Reserved))

        MDT = CID.cidRegisterFieldStruct.uiMdt
        month = MDT & 0x00f       # Check last four bit
        year = ((MDT & 0xff0) >> 4) + 200
        CID_REG_LIST[gvar.CID.MDT] = str(calendar.month_name[month]) + " " + str(year)

        CID_REG_LIST[gvar.CID.CRC] = CID.uiArrCidRegisterFieldStruct[0] >> 1

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("Manufacturing Date", CID_REG_LIST[gvar.CID.MDT]))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ("CRC CheckSum", CID_REG_LIST[gvar.CID.CRC]))

        return CID_REG_LIST


    def BufferFilling(self, BufferObject, Pattern, Data = 0, AnyWord = None):
        """
        Function to fill buffer with pattern
        """
        # 0:'ALL_ZERO', 1:'WORD_REPEATED', 2:'INCREMENTAL', 3: RANDOM BUFFER, 4:'CONST', 5:'ALL_ONE', 6:'ANY_WORD', 7:'WORD_BLOCK_NUMBER' ,8:'NEG_INCREMENTAL', 9:'NEG_CONST'

        if Pattern == 0:
            BufferObject.Fill(value = 0x0)
            # BufferObject.Fill(value = ServiceWrap.ALL_0)
        elif Pattern == 1:
            NumBlocks = old_div(BufferObject.size(), 512)   # Method size will return buffer size in byte unit. So divided by 512 to convert into block.
            for blkNo in range(0, NumBlocks):
                value = 0
                for i in range(0, 512, 2):
                    BufferObject.SetTwoBytes((blkNo * 512) + i, (value & 0xFFFF), little_endian = False)
                    value += 1
        elif Pattern == 2:
            BufferObject.FillIncrementing()
        elif Pattern == 3:
            BufferObject.FillRandom()
        elif Pattern == 4:
            BufferObject.Fill(value = random.randint(1, 0xFF))
        elif Pattern == 5:
            BufferObject.Fill(value = 0xFF)
            # BufferObject.Fill(value = ServiceWrap.ALL_1)  # TOBEDONE: ServiceWrap.ALL_1 has bug that it fills 0x01 instead of 0xff
        elif Pattern == 6:
            AnyWord = self._anyWord if AnyWord == None else AnyWord
            AnyWord = hex(AnyWord)[2:]  # Removing '0x'
            BufferObject.Fill(pattern_string = AnyWord)
            #LSB = 0xFF & AnyWord
            #MSB = 0xFF & (AnyWord >> 8)
            ##BufferObject.Fill([MSB, LSB])    # TOBEDONE: CTF buffer fill method takes values in array. but CVF buffer fill method does not take values in array.
            #twoBytes = "%x%x" % (MSB, LSB)
            #twoBytes = int(twoBytes, base = 16)
            #NumBlocks = BufferObject.size() / 512   # Method size will return buffer size in byte unit. So divided by 512 to convert into block.
            #for blkNo in range(0, NumBlocks):
                #for byteOffset in range(0, 512, 2):
                    #BufferObject.SetTwoBytes((blkNo * 512) + byteOffset, twoBytes, little_endian = False)
        elif Pattern == 7:
            BufferObject.FillMultiple(list(range(0, 0xFF)))
        elif Pattern == 8:
            BufferObject.FillFromSequence(list(range(0xFF, -1, -1)))
        elif Pattern == 9:
            BufferObject.FillMultiple(list(range(0xFF, 0x0, -1)))
        elif Pattern == 10:
            BufferObject.Fill(pattern_string = hex(Data)[2:])
        else:
            raise ValidationError.TestFailError(self.fn, "Undefined pattern was given")

        return BufferObject


    def BufferCompare(self, writeBuffer, readBuffer):
        value = writeBuffer.Compare(buf = readBuffer)
        if value != 0:
            raise ValidationError.CVFGenericExceptions(self.fn, "CARD_COMPARE_ERROR error occured. Read buffer is not equal to written buffer")
        self.noiseLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_WRITE_AND_READ_DATA_VERIFIED)


    def Compare(self, readBuffer, writeBuffer = None, startLBA = None, blockCount = None, Pattern = None, LbaTag = False, SeqTag = False, SeqNumber = 0):
        """
        Description: Used to compare two buffers of same size and type.
        Parameters Description:
            readBuffer - Buffer return by read command
            writeBuffer - Buffer created from testcase with the given pattern
            startLBA - Used to fill the writeBuffer in case of LbaTag is True
        """
        if writeBuffer == None:
            writeBuffer = ServiceWrap.Buffer.CreateBuffer(blockCount, patternType = ServiceWrap.ALL_0, isSector = True)
            self.FillBufferWithTag(writeBuffer, startLBA, blockCount, Pattern, LbaTag, SeqTag, SeqNumber)

        self.BufferCompare(writeBuffer, readBuffer)


    def GetPatternEnumFromNum(self, pattern):
        if(pattern == 0):
            patternEnum = sdcmdWrap.Pattern.ALL_ZERO
        elif(pattern == 1):
            patternEnum = sdcmdWrap.Pattern.WORD_REPEATED
        elif(pattern == 2):
            patternEnum = sdcmdWrap.Pattern.INCREMENTAL
        elif(pattern == 3):
            patternEnum = sdcmdWrap.Pattern.ANY_BUFFER
        elif(pattern == 4):
            patternEnum = sdcmdWrap.Pattern.CONST
        elif(pattern == 5):
            patternEnum = sdcmdWrap.Pattern.ALL_ONE
        elif(pattern == 6):
            patternEnum = sdcmdWrap.Pattern.ANY_WORD
        elif(pattern == 7):
            patternEnum = sdcmdWrap.Pattern.WORD_BLOCK_NUMBER
        elif(pattern == 8):
            patternEnum = sdcmdWrap.Pattern.PATTERN_NEG_INCREMENTAL
        elif(pattern == 9):
            patternEnum = sdcmdWrap.Pattern.PATTERN_NEG_CONST

        return patternEnum


    def CheckBusWidth(self):
        self.FUNCTION_ENTRY("CheckBusWidth")
        self.Cmd55()
        sd_status = self.SD_STATUS()

        if(sd_status.objSDStatusRegister.ui64DatBusWidth == 0):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus width is set to Default which is 1.")
            BusWidth=1
        elif(sd_status.objSDStatusRegister.ui64DatBusWidth == 2):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Bus Width is set to 4.")
            BusWidth=4
        elif(sd_status.objSDStatusRegister.ui64DatBusWidth == 1):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Reserved Bit.")
            BusWidth=0
        elif(sd_status.objSDStatusRegister.ui64DatBusWidth == 3):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Reserved Bit.")
            BusWidth=0
        else:
            raise ValidationError.TestFailError(self.fn, "Failed - Not able to verify bus width.")

        self.FUNCTION_EXIT("CheckBusWidth")
        return BusWidth


    def getCurrentExeCmdDecodedR1Response(self):
        return self.decodedR1response


    def GetCardStatus(self):
        self.FUNCTION_ENTRY("GetCardStatus")
        self.Cmd13()
        if (self.__spiMode != True):
            self.FUNCTION_EXIT("GetCardStatus")
            return self.decodedR1response
        else:
            self.FUNCTION_EXIT("GetCardStatus")
            return self.__decodedSPIR2response


    def ASCII_Code_to_String(self, function_name):
        function_name_ascii = ""
        for offset in range(0, function_name.GetSize()):
            character = function_name.GetOneByteToInt(offset)
            if character != 0:
                function_name_ascii += chr(character)
        return function_name_ascii


    def General_Information(self, DataBuff):
        """
        Description: To decode the General Information Extension Register. Decoded as dictionary.
            GeneralInformation['Length']
            GeneralInformation['no_of_Extension']
            GeneralInformation['function_1']
            GeneralInformation['function_2']
            .
            .
        Parameter Description: DataBuff - One block read data of general information. Refer Figure 5-15 in SD Spec Part-I 7.0.
        """
        self.FUNCTION_ENTRY("General_Information")

        GeneralInformation = {}

        GeneralInformation["Revision"] = DataBuff.GetTwoBytesToInt(gvar.General_Info_Offsets.REVISION)
        GeneralInformation["Length"] = DataBuff.GetTwoBytesToInt(gvar.General_Info_Offsets.GENERAL_INFORMATION_LENGTH)
        GeneralInformation["no_of_Extension"] = DataBuff.GetOneByteToInt(gvar.General_Info_Offsets.NUMBER_of_EXTENSIONS)

        Current_Extension = gvar.General_Info_Offsets.EXTENSION_1_Start_Offset
        count = 1

        while Current_Extension != 0x00:
            Temp_Dictionary = {}
            Temp_Dictionary["SFC"] = DataBuff.GetTwoBytesToInt(Current_Extension + gvar.General_Info_Offsets.SFC)
            Temp_Dictionary["FCC"] = DataBuff.GetTwoBytesToInt(Current_Extension + gvar.General_Info_Offsets.FCC)
            Temp_Dictionary["FMC"] = DataBuff.GetTwoBytesToInt(Current_Extension + gvar.General_Info_Offsets.FMC)
            FMN = DataBuff.GetData(Current_Extension + gvar.General_Info_Offsets.FMN, 16)
            Temp_Dictionary["FMN"] = self.ASCII_Code_to_String(FMN)
            Temp_Dictionary["PFC"] = DataBuff.GetTwoBytesToInt(Current_Extension + gvar.General_Info_Offsets.PFC)
            FN = DataBuff.GetData(Current_Extension + gvar.General_Info_Offsets.FN, 16)
            Temp_Dictionary["FN"] = self.ASCII_Code_to_String(FN)
            Temp_Dictionary["Pointer_to_Next_Extension"] = DataBuff.GetTwoBytesToInt(Current_Extension + gvar.General_Info_Offsets.POINTER_to_NEXT_EXTENSION)
            Temp_Dictionary["Number_of_Register_Sets"] = DataBuff.GetTwoBytesToInt(Current_Extension + gvar.General_Info_Offsets.NUMBER_of_REGISTER_SETS)

            GeneralInformation["Function_%s" % count] = Temp_Dictionary
            Current_Extension = GeneralInformation["Function_%s" % count]["Pointer_to_Next_Extension"]
            count = count + 1

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_GEN_INFO_FUNC_DATA(GeneralInformation))

        self.decoded_General_Information = GeneralInformation
        self.FUNCTION_EXIT("General_Information")


    def Decode_Power_Management_Func(self, DataBuff):
        """
        Description: Decodes the buffer of power management function and return values in dictionary format.
        Parameter Description: DataBuff - One block read data of power management function
        """
        PowerMangement = {}

        PowerMangement["REVISON"] = DataBuff.GetOneByteToInt(gvar.Power_Manage_Func_Offsets.REVISION_Byte_Offset) & gvar.Power_Manage_Func_Offsets.REVISION_Bit_Offset

        STATUS_REGISTER = DataBuff.GetOneByteToInt(gvar.Power_Manage_Func_Offsets.STATUS_REGISTER_Byte_Offset)
        PowerMangement["POFR"] = STATUS_REGISTER & gvar.Power_Manage_Func_Offsets.POFR_Bit_Offset
        PowerMangement["PSUR"] = (STATUS_REGISTER & gvar.Power_Manage_Func_Offsets.PSUR_Bit_Offset) >> 1
        PowerMangement["PDMR"] = (STATUS_REGISTER & gvar.Power_Manage_Func_Offsets.PDMR_Bit_Offset) >> 2
        PowerMangement["POFS"] = (STATUS_REGISTER & gvar.Power_Manage_Func_Offsets.POFS_Bit_Offset) >> 4
        PowerMangement["PSUS"] = (STATUS_REGISTER & gvar.Power_Manage_Func_Offsets.PSUS_Bit_Offset) >> 5
        PowerMangement["PDMS"] = (STATUS_REGISTER & gvar.Power_Manage_Func_Offsets.PDMS_Bit_Offset) >> 6

        SETTINGS_REGISTER = DataBuff.GetOneByteToInt(gvar.Power_Manage_Func_Offsets.SETTINGS_REGISTER_Byte_Offset)
        PowerMangement["POFN"] = SETTINGS_REGISTER & gvar.Power_Manage_Func_Offsets.POFN_Bit_Offset
        PowerMangement["PSUN"] = (SETTINGS_REGISTER & gvar.Power_Manage_Func_Offsets.PSUN_Bit_Offset) >> 1
        PowerMangement["PDMN"] = (SETTINGS_REGISTER & gvar.Power_Manage_Func_Offsets.PDMN_Bit_Offset) >> 2

        self.decoded_Power_Management_Func = PowerMangement
        return PowerMangement

    def Power_Management(self, DataBuff):
        """
        Refer Table 5-28, Figures 5-16, 5-17, 5-18 in SD Physical Layer Specification 7.0
        """
        self.FUNCTION_ENTRY("Power_Management")
        PMF = self.Decode_Power_Management_Func(DataBuff)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_POW_MANAGE_FUNC_DATA(PMF))
        # # Power Management Revision Register
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Revision', PMF["REVISON"]))

        # # Power Management Status Register
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('POFR', PMF["POFR"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('PSUR', PMF["PSUR"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('PDMR', PMF["PDMR"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('POFS', PMF["POFS"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('PSUS', PMF["PSUS"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('PDMS', PMF["PDMS"]))

        # # Power Management Setting Register
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('POFN', PMF["POFN"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('PSUN', PMF["PSUN"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('PDMN', PMF["PDMN"]))

        self.FUNCTION_EXIT("Power_Management")

    def Decode_Perf_Enhance_Func(self, DataBuff):
        """
        Description: Decodes the buffer of performance enhancement function and return values in dictionary format.
        Parameter Description: DataBuff - One block read data of performance enhancement function
        """
        PerfEnhancement = {}
        PerfEnhancement["REVISION"] = DataBuff.GetOneByteToInt(gvar.Perf_Enhan_Func_Offsets.REVISION)

        PerfEnhancement["FX_EVENT_SUPPORT"] = DataBuff.GetOneByteToInt(gvar.Perf_Enhan_Func_Offsets.FX_EVENT_SUPPORT_Byte_Offset) & gvar.Perf_Enhan_Func_Offsets.FX_EVENT_SUPPORT_Bit_Offset
        PerfEnhancement["CARD_INIT_MAINTEN_SUPPORT"] = DataBuff.GetOneByteToInt(gvar.Perf_Enhan_Func_Offsets.CARD_INIT_MAINTEN_SUPPORT_Byte_Offset) & gvar.Perf_Enhan_Func_Offsets.CARD_INIT_MAINTEN_SUPPORT_Bit_Offset
        PerfEnhancement["HOST_INIT_MAINTEN_SUPPORT"] = (DataBuff.GetOneByteToInt(gvar.Perf_Enhan_Func_Offsets.HOST_INIT_MAINTEN_SUPPORT_Byte_Offset) & gvar.Perf_Enhan_Func_Offsets.HOST_INIT_MAINTEN_SUPPORT_Bit_Offset) >> 1
        PerfEnhancement["CARD_MAINTEN_URGENCY"] = DataBuff.GetOneByteToInt(gvar.Perf_Enhan_Func_Offsets.CARD_MAINTEN_URGENCY_Byte_Offset) & gvar.Perf_Enhan_Func_Offsets.CARD_MAINTEN_URGENCY_Bit_Offset
        PerfEnhancement["CACHE_SUPPORT"] = DataBuff.GetOneByteToInt(gvar.Perf_Enhan_Func_Offsets.CACHE_SUPPORT_Byte_Offset) & gvar.Perf_Enhan_Func_Offsets.CACHE_SUPPORT_Bit_Offset
        CQ_SUPPORT_AND_DEPTH = DataBuff.GetOneByteToInt(gvar.Perf_Enhan_Func_Offsets.CQ_SUPPORT_AND_DEPTH)
        PerfEnhancement["CQ_SUPPORT_AND_DEPTH"] = CQ_SUPPORT_AND_DEPTH if CQ_SUPPORT_AND_DEPTH == 0 else CQ_SUPPORT_AND_DEPTH + 1
        PerfEnhancement["TASK_ERROR_STATUS"] = DataBuff.GetEightBytesToInt(gvar.Perf_Enhan_Func_Offsets.TASK_ERROR_STATUS)

        PerfEnhancement["FX_EVENT_ENABLE"] = DataBuff.GetOneByteToInt(gvar.Perf_Enhan_Func_Offsets.FX_EVENT_ENABLE_Byte_Offset) & gvar.Perf_Enhan_Func_Offsets.FX_EVENT_ENABLE_Bit_Offset
        PerfEnhancement["CARD_INIT_MAINTEN_ENABLE"] = DataBuff.GetOneByteToInt(gvar.Perf_Enhan_Func_Offsets.CARD_INIT_MAINTEN_ENABLE_Byte_Offset) & gvar.Perf_Enhan_Func_Offsets.CARD_INIT_MAINTEN_ENABLE_Bit_Offset
        PerfEnhancement["HOST_INIT_MAINTEN_ENABLE"] = (DataBuff.GetOneByteToInt(gvar.Perf_Enhan_Func_Offsets.HOST_INIT_MAINTEN_ENABLE_Byte_Offset) & gvar.Perf_Enhan_Func_Offsets.HOST_INIT_MAINTEN_ENABLE_Bit_Offset) >> 1
        PerfEnhancement["START_HOST_INIT_MAINTEN"] = DataBuff.GetOneByteToInt(gvar.Perf_Enhan_Func_Offsets.START_HOST_INIT_MAINTEN_Byte_Offset) & gvar.Perf_Enhan_Func_Offsets.START_HOST_INIT_MAINTEN_Bit_Offset
        PerfEnhancement["CACHE_ENABLE"] = DataBuff.GetOneByteToInt(gvar.Perf_Enhan_Func_Offsets.CACHE_ENABLE_Byte_Offset) & gvar.Perf_Enhan_Func_Offsets.CACHE_ENABLE_Bit_Offset
        PerfEnhancement["FLUSH_CACHE"] = DataBuff.GetOneByteToInt(gvar.Perf_Enhan_Func_Offsets.FLUSH_CACHE_Byte_Offset) & gvar.Perf_Enhan_Func_Offsets.FLUSH_CACHE_Bit_Offset
        PerfEnhancement["ENABLE_CQ"] = DataBuff.GetOneByteToInt(gvar.Perf_Enhan_Func_Offsets.ENABLE_CQ_Byte_Offset) & gvar.Perf_Enhan_Func_Offsets.ENABLE_CQ_Bit_Offset
        PerfEnhancement["CQ_MODE"] = (DataBuff.GetOneByteToInt(gvar.Perf_Enhan_Func_Offsets.CQ_MODE_Byte_Offset) & gvar.Perf_Enhan_Func_Offsets.CQ_MODE_Bit_Offset) >> 1

        self.decoded_Perf_Enhance_Func = PerfEnhancement
        return PerfEnhancement

    def Performance_Enhancement_Register_Set(self, DataBuff):
        """
        Refer Table 5-30 in SD Spec 7.0
        """

        self.FUNCTION_ENTRY("Performance_Enhancement_Register_Set")
        PERF = self.Decode_Perf_Enhance_Func(DataBuff)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_PER_ENHANCE_FUNC_DATA(PERF))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('PerfEnhencementFunctionRev', PERF["REVISON"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('FX_EVENTSupport', PERF["FX_EVENT_SUPPORT"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('CardInitiatedMntnceSupport', PERF["CARD_INIT_MAINTEN_SUPPORT"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('HostInitiatedMntnceSupport', PERF["HOST_INIT_MAINTEN_SUPPORT"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('CardMaintenanceUrgency', PERF["CARD_MAINTEN_URGENCY"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('CacheSupport', PERF["CACHE_SUPPORT"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('CQSupportAndDepth', PERF["CQ_SUPPORT_AND_DEPTH"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('TaskErrorStatus', PERF["TASK_ERROR_STATUS"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('FXEventEnable', PERF["FX_EVENT_ENABLE"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('CardInitiatedMntnceEnable', PERF["CARD_INIT_MAINTEN_ENABLE"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('HostInitiatedMntnceEnable', PERF["HOST_INIT_MAINTEN_ENABLE"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('StartHostInitiatedMntnce', PERF["START_HOST_INIT_MAINTEN"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('CacheEnable', PERF["CACHE_ENABLE"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('FlushCache', PERF["FLUSH_CACHE"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('EnableCQ', PERF["ENABLE_CQ"]))
        # self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('CQMode', PERF["CQ_MODE"]))

        self.FUNCTION_EXIT("Performance_Enhancement_Register_Set")


    #def General_Information(self, CMD48):
        #"""
        #Refer Table 5-31 in SD Spec 7.0
            #"""
        #self.FUNCTION_ENTRY("General_Information")

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "********** General Information Header Fields Start **********")
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('StructRevision', CMD48.extRegisters.u.generalInfo.headerFields.ui16StructRev))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('GeneralInfoLength', CMD48.extRegisters.u.generalInfo.headerFields.ui16GeneralInfoLength))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('NumberOfExtensions', CMD48.extRegisters.u.generalInfo.headerFields.ui8NumberOfExtensions))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "********** General Information Header Fields End **********")

        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "********** General Information Extention Register First Function's Fields Start **********")
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ExtXStandardFunctionCode', CMD48.extRegisters.u.generalInfo.extregisterFields.ui16ExtXStandardFunctionCode))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ExtXFunctionCapabilityCode', CMD48.extRegisters.u.generalInfo.extregisterFields.ui16ExtXFunctionCapabilityCode))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ExtXFunctionManufacturerCode', CMD48.extRegisters.u.generalInfo.extregisterFields.ui16ExtXFunctionManufacturerCode))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ExtXFunctionManufacturerName', CMD48.extRegisters.u.generalInfo.extregisterFields.ui8ExtXFunctionManufacturerName))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ExtXParticularFunctionCode', CMD48.extRegisters.u.generalInfo.extregisterFields.ui16ExtXParticularFunctionCode))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ExtXFunctionName', CMD48.extRegisters.u.generalInfo.extregisterFields.ui8ExtXFunctionName))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('PointerToNextExtension', CMD48.extRegisters.u.generalInfo.extregisterFields.ui16PointerToNextExtension))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('NumberOfRegisterSets', CMD48.extRegisters.u.generalInfo.extregisterFields.ui8NumberOfRegisterSets))

        ##self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ui32FNO', CMD48.extRegisters.u.generalInfo.extregisterFields.data.objExtRegisterSetAddressX.ui32FNO))
        ##self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ui32StartAddressOfARegisterSet', CMD48.extRegisters.u.generalInfo.extregisterFields.data.objExtRegisterSetAddressX.ui32StartAddressOfARegisterSet))
        ##self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ui32_bit17', CMD48.extRegisters.u.generalInfo.extregisterFields.data.objExtRegisterSetAddressX.ui32_bit17))
        ##self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ui32ExtRegisterSetAddressX', CMD48.extRegisters.u.generalInfo.extregisterFields.data.ui32ExtRegisterSetAddressX))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "********** General Information Extention Register First Function's Fields End **********")

        #self.FUNCTION_EXIT("General_Information")


    #def Power_Management(self, CMD48):
        #"""
        #Refer Table 5-28, Figures 5-16, 5-17, 5-18 in SD Physical Layer Specification 7.0
        #"""
        #self.FUNCTION_ENTRY("Power_Management")

        ## Power Management Revision Register
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Revision', CMD48.extRegisters.u.powerMgmntFunc.powerManagementRevisionRegister.ui8Revision))

        ## Power Management Status Register
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Pdmr', CMD48.extRegisters.u.powerMgmntFunc.powerManagementStatusRegister.ui8Pdmr))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Pdms', CMD48.extRegisters.u.powerMgmntFunc.powerManagementStatusRegister.ui8Pdms))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Pofr', CMD48.extRegisters.u.powerMgmntFunc.powerManagementStatusRegister.ui8Pofr))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Pofs', CMD48.extRegisters.u.powerMgmntFunc.powerManagementStatusRegister.ui8Pofs))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Psur', CMD48.extRegisters.u.powerMgmntFunc.powerManagementStatusRegister.ui8Psur))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Psus', CMD48.extRegisters.u.powerMgmntFunc.powerManagementStatusRegister.ui8Psus))

        ## Power Management Setting Register
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Pdmn', CMD48.extRegisters.u.powerMgmntFunc.powerManagementSettingRegister.ui8Pdmn))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Psun', CMD48.extRegisters.u.powerMgmntFunc.powerManagementSettingRegister.ui8Psun))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('Pofn', CMD48.extRegisters.u.powerMgmntFunc.powerManagementSettingRegister.ui8Pofn))

        #self.FUNCTION_EXIT("Power_Management")


    #def Performance_Enhancement_Register_Set(self, CMD48):
        #"""
        #Refer Table 5-30 in SD Spec 7.0
        #"""

        #self.FUNCTION_ENTRY("Performance_Enhancement_Register_Set")
        #if CMD48.extRegisters.u.perfEncmntFunc.ui8CQSupportAndDepth > 0:
            #QueueDepth = CMD48.extRegisters.u.perfEncmntFunc.ui8CQSupportAndDepth + 1
        #else:
            #QueueDepth = 0
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('PerfEnhencementFunctionRev', CMD48.extRegisters.u.perfEncmntFunc.ui8PerfEnhencementFunctionRev))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('FX_EVENTSupport', CMD48.extRegisters.u.perfEncmntFunc.ui8FX_EVENTSupport))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('CardInitiatedMntnceSupport', CMD48.extRegisters.u.perfEncmntFunc.ui8CardInitiatedMntnceSupport))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('HostInitiatedMntnceSupport', CMD48.extRegisters.u.perfEncmntFunc.ui8HostInitiatedMntnceSupport))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('CardMaintenanceUrgency', CMD48.extRegisters.u.perfEncmntFunc.ui8CardMaintenanceUrgency))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('CacheSupport', CMD48.extRegisters.u.perfEncmntFunc.ui8CacheSupport))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('CQSupportAndDepth', QueueDepth))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_0', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_0))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_1', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_1))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_2', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_2))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_3', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_3))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_4', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_4))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_5', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_5))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_6', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_6))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_7', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_7))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_8', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_8))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_9', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_9))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_10', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_10))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_11', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_11))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_12', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_12))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_13', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_13))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_14', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_14))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_15', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_15))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_16', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_16))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_17', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_17))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_18', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_18))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_19', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_19))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_20', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_20))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_21', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_21))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_22', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_22))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_23', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_23))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_24', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_24))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_25', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_25))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_26', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_26))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_27', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_27))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_28', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_28))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_29', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_29))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_30', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_30))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('ErrorStatusTaskID_31', CMD48.extRegisters.u.perfEncmntFunc.ui64ErrorStatusTaskID_31))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('FXEventEnable', CMD48.extRegisters.u.perfEncmntFunc.ui8FXEventEnable))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('CardInitiatedMntnceEnable', CMD48.extRegisters.u.perfEncmntFunc.ui8CardInitiatedMntnceEnable))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('HostInitiatedMntnceEnable', CMD48.extRegisters.u.perfEncmntFunc.ui8HostInitiatedMntnceEnable))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('StartHostInitiatedMntnce', CMD48.extRegisters.u.perfEncmntFunc.ui8StartHostInitiatedMntnce))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('CacheEnable', CMD48.extRegisters.u.perfEncmntFunc.ui8CacheEnable))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('FlushCache', CMD48.extRegisters.u.perfEncmntFunc.ui8FlushCache))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('EnableCQ', CMD48.extRegisters.u.perfEncmntFunc.ui8EnableCQ))
        #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "%-35s: %s" % ('CQMode', CMD48.extRegisters.u.perfEncmntFunc.ui8CQMode))
        #self.FUNCTION_EXIT("Performance_Enhancement_Register_Set")


    def TaskSummaryInit(self):
        self.TasksQueued = 0
        self.ReadTasksQueued = 0
        self.WriteTasksQueued = 0
        self.TasksExecuted = 0
        self.ReadTasksExecuted = 0
        self.WriteTasksExecuted = 0
        self.TasksAborted = 0
        self.BlocksTransferred = 0


    def GetTaskSummary(self):
        """
        To get the CQ Ageing Threshold value
        """
        if self.TasksQueued > 0:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "\n\n\n")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "################################# SUMMARY #####################################")
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "No of Tasks Queued = %d, Read = %d, Write = %d"
                         % (self.TasksQueued, self.ReadTasksQueued, self.WriteTasksQueued))

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "No of Tasks Executed successfully = %d, Read = %d, Write = %d"
                         % (self.TasksExecuted, self.ReadTasksExecuted, self.WriteTasksExecuted))

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "No of Tasks Aborted = %d" % self.TasksAborted)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Total Data blocks transferred = %d" % self.BlocksTransferred)

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###############################################################################")
            self.TaskSummaryInit()

        return


    def UpdateTaskCompletionInAgeingDict(self, TaskID):
        """
        Function to update the Task Completion status in AgeingDict
        """
        self.CQTaskDetails[TaskID] = {}
        self.CQTaskAgeingDict["Task%d" % TaskID] = "NQ"


    def CQTaskAgeingDict_Dump(self, OnlyDictValues = True):
        if OnlyDictValues == True:
            if self._CQDevConfigDict["Mode"] == "Voluntary":
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_QUEUE_STATUS_IN_VOL_CQ(self.CQTaskAgeingDict))
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_NQ_IS_NOT_IN_QUEUE)
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_QUEUE_STATUS_IN_SEQ_CQ(self.CQTaskAgeingDict))
        else:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_BLANK_LINE)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_HEADER(self.GL_CQ_TASK_AGEING_DICT, special_character = "*"))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_BLANK_LINE)
            i = 1
            ag = ""

            for key in self.CQTaskAgeingDict:
                ag += "%-6s - %-8s" % (key, self.CQTaskAgeingDict[key])

                if i % 8 == 0:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CQ_AGEING(ag))
                    ag = ""
                i += 1

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_CQ_AGEING(ag))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_HEADER(special_character = "*", repeat = 100))


    def CQGetPendingTasksDump(self):
        TasksStatus = list(self.CQTaskAgeingDict.values())
        TasksQueued = []

        for i in range(0, len(TasksStatus)):
            if self._CQDevConfigDict["Mode"] == "Voluntary":
                if type(TasksStatus[i]) == int:
                    TasksQueued.append(i)
            else:
                if TasksStatus[i] == "InQ":
                    TasksQueued.append(i)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Tasks in Queue = %s" % TasksQueued)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "No. of pending tasks in Queue = %s" % (len(TasksQueued)))


    def GetRandomLBA(self, NumBlocks, NumBlockList, StartBlockAddrList, lbaalignment = 1):
        # Purpose of Function: Generate random start lba compliance with other task's lba range of start and end lba to write or read.
        while(True):
            randomStartLba = random.randrange(0, ((self.__cardMaxLba + 1) - NumBlocks), lbaalignment)
            count = 0
            for i in range(0, len(StartBlockAddrList)):
                # Below code checks whether generated random lba comes within the lba range(start and end) of other tasks or not.
                # if it comes within the lba range of other task then break for loop and again do while till succeed.
                if (randomStartLba > (StartBlockAddrList[i] + NumBlockList[i])) or ((randomStartLba + NumBlocks) < StartBlockAddrList[i]):
                    count += 1
                else:
                    break
            # count is equvailent to length of StartBlockAddrList(number of tasks), that means generated randomstartlba
            # does not conflict with lba range of other tasks.
            if count == len(StartBlockAddrList):
                break

        return randomStartLba


    def GetMiscompareDetails(self, exc):
        # TOBEDONE: Below methods being called from object 'exc' are copied from CTF, Yet to verify if CVF have same methods with the same name.
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "#################  Getting Miscompare Details  #########################\n")

        MiscompareByteOffset = exc.GetMiscompareLocation() % 512
        MiscompareBlkOffset = old_div(exc.GetMiscompareLocation(), 512)

        Buffer1 = exc.GetBuffer1()
        Buffer2 = exc.GetBuffer2()

        BeginBlkNum1 = old_div(exc.GetMiscompareBeginOffset1(), 512)  # in terms of blocks
        BeginBlkNum2 = old_div(exc.GetMiscompareBeginOffset2(), 512)

        # starting block address of the miscompare in terms of bytes
        MiscompareBlkStartOffset1 = (BeginBlkNum1 + MiscompareBlkOffset) * 512
        MiscompareBlkStartOffset2 = (BeginBlkNum2 + MiscompareBlkOffset) * 512

        MiscompareData1 = Buffer1.GetOneByteToInt(MiscompareBlkStartOffset1 + MiscompareByteOffset)
        MiscompareData2 = Buffer2.GetOneByteToInt(MiscompareBlkStartOffset2 + MiscompareByteOffset)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Miscompare started:")

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Location Sector: Byte - 0x%X:0x%X (%d:%d)"
                     % (BeginBlkNum1, MiscompareByteOffset, BeginBlkNum1, MiscompareByteOffset))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Location2 Sector: Byte - 0x%X:0x%X (%d:%d)"
                     % (BeginBlkNum2, MiscompareByteOffset, BeginBlkNum2, MiscompareByteOffset))
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Data miscompared: 0x%X (%d) != 0x%X (%d)"
                     % (MiscompareData1, MiscompareData1, MiscompareData2, MiscompareData2))

        self.blankLine()

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Miscompare is located at offset 0x%X:\n\n Buffer1 around miscompare: \n\n%s\nBuffer2 around miscompare: \n\n%s\n"
                     % (exc.GetMiscompareLocation(),
                        Buffer1.GenerateFormattedString(startOffset = MiscompareBlkStartOffset1, endOffset = MiscompareBlkStartOffset1 + 511),
                        Buffer2.GenerateFormattedString(startOffset = MiscompareBlkStartOffset2, endOffset = MiscompareBlkStartOffset2 + 511)
                        )
                     )

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Miscompare error occured at offset = 0x%X" % (exc.GetMiscompareLocation()))
        #raise ValidationError.TestFailError(self.fn, "Miscompare error occured at offset = 0x%X" % (exc.GetMiscompareLocation()))


    def GetTaskStatusRegister(self):
        """
        CMD13 - SEND_STATUS to read Task Status Register
        Functionality: To get the task status register value
        """
        self.FUNCTION_ENTRY("GetTaskStatusRegister")

        try:
            response = self.Cmd13(SendTaskStatus = True)
            Task_Status = response.GetFourBytesToInt(offset = 1, little_endian = False)
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Task Status Register - {0:#0{1}x}".format(Task_Status, 10))   # 32 bit task status is equal to 8 digit hex
            # {   - Format identifier
            # 0:  - first parameter
            # #   - use "0x" prefix
            # 0   - fill with zeroes
            # {1} - to a length of n characters (including 0x), defined by the second parameter
            # x   - hexadecimal number, using lowercase letters for a-f
            # }   - End of format identifier
        except ValidationError.CVFGenericExceptions as exc:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, exc.GetInternalErrorMessage())
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetInternalErrorMessage())

        self.FUNCTION_EXIT("GetTaskStatusRegister")
        return Task_Status


    def GetRegressionLogDirectory(self):
        self.FUNCTION_ENTRY("GetRegressionLogDirectory")

        BotFileName = None
        FilePath = self.currCfg.system.TestsDir           # Root folder of sddvt package.
        FwFilePath = FilePath + "\\DeviceFWBotFile"
        # TOBEDONE: DieNumber
        # DieNum = str(self.currCfg.variation.DieNumber)
        DieNum = 0
        raise ValidationError.TestFailError(self.fn, "Not able to get DieNum")
        FwFilePath += "\\" + DieNum + "D"

        files = os.listdir(FwFilePath)

        for f in files:
            if ".bot" in f:
                BotFileName = f.strip(".bot")
        fp = FilePath.strip(FilePath.split("\\")[-1])
        logDir = fp + "RegressionLogs\\" + "SD_DVT_LOGS___FW_" + BotFileName + time.strftime("___%B%d")

        raise ValidationError.TestFailError(self.fn, "FWDownload API is not implemented in CVF")

        if not os.path.exists(logDir):
            os.makedirs(logDir)

        self.FUNCTION_EXIT("GetRegressionLogDirectory")
        return logDir


    def DumpTestLogs(self, clearLog = False, sheet = None, script = None):
        self.FUNCTION_ENTRY("DumpTestLogs")

        from shutil import copyfile
        # TOBEDONE: HostLogEnable is hardcoded
        #if self.currCfg.variation.HostLogEnable == 1:
        HostLogEnable = 1
        raise ValidationError.TestFailError(self.fn, "HostLogEnable")
        if HostLogEnable == 1:

            logDir = self.GetRegressionLogDirectory() +"\\"+sheet
            if not os.path.exists(logDir):
                os.makedirs(logDir)

            FilePath = self.currCfg.system.TestsDir           # Root folder of sddvt package.
            hostlog = FilePath + "\\DefaultHostLog.txt"

            if script == None:
                #scriptlog = self.__TF.logger.GetLogFilename().split("\\")[-1].split(".")[0]    # CTF line
                logfilename = None      # self.__TF.logger has no method GetLogFilename().
                scriptlog = logfilename.split("\\")[-1].split(".")[0]
            else:
                scriptlog = script + "_" + time.strftime("%Y%m%d_%H%M%S")

            sdcmdWrap.GetHostDebugInformation(szPathToFile = FilePath + "\\DefaultHostLog.txt")
            copyfile(hostlog, logDir + "\\HostLog_" + scriptlog + ".txt")

            if clearLog == True:
                open(hostlog, "w").close()
                # value of sdcmdWrap.DEBUG_METHOD.IO_DEBUG is 0.
                sdcmdWrap.SDRSetDebugMethod(Method = sdcmdWrap.DEBUG_METHOD.IO_DEBUG, Set = True)

            # TOBEDONE: logfilename
            logfilename = None
            #f = open(self.__TF.logger.GetLogFilename())
            f = open(logfilename)
            f1 = open(logDir + "\\" + scriptlog + ".log", 'a')

            StartCopying = False
            for line in f.readlines():
                if "Started Running script " + script in line:
                    StartCopying = True

                if StartCopying:
                    f1.write(line)

            f1.close()
            f.close()
            self.FUNCTION_EXIT("DumpTestLogs")

    def StausAfterWriteToReadOnlyBitsOfCSDnVerify(self):
        '''
        This API should be called After calling WriteToReadOnlyBitsOfCSDnVerify, else error will be reported.
        '''
        if self.__WriteToReadOnlyBitsOfCSDnVerifyCMD27Status == None:
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "From SDCommandLib, Call WriteToReadOnlyBitsOfCSDnVerify Before calling StausAfterWriteToReadOnlyBitsOfCSDnVerify API\n")
            raise ValidationError.TestFailError(self.fn, "SDCommandLib attribute self.__WriteToReadOnlyBitsOfCSDnVerifyCMD27Status is None")
        else:
            return self.__WriteToReadOnlyBitsOfCSDnVerifyCMD27Status

    def SetOrResetCopyFlagBit(self, Enable = None):
        """
        Description:
            Enable : 0 - Original / 1 - Copied
        Note: Use CheckCopyFlagBit after this function to make sure the bit is set or reset
        """

        if Enable == None:
            raise ValidationError.TestFailError(self.fn, "Enable mode can not be None. Pass either 0 to disable or 1 to enable Copy Flag bit of CSD register")

        if self.__spiMode != True:
            # Send card to Standby mode
            self.Cmd7(deSelect = True)

        # Get CSD register value and check the card current status
        self.Cmd9()
        self.__CSDresponceBuff.PrintToLog(start = 0, end = 16)

        modifiedCSDbuff = ServiceWrap.Buffer.CreateBuffer(16, 0x00, isSector = False)
        modifiedCSDbuff.Copy(thisOffset = 0, srcBuf = self.__CSDresponceBuff, srcOffset = 1, count = 16)
        modifiedCSDbuff.PrintToLog()

        CopyFlagBit = modifiedCSDbuff.GetOneByteToInt(offset = 14)

        if Enable == 1:
            if (CopyFlagBit & 0x40) != 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CopyFlag bit already enabled. So doing nothing")
            else:
                CopyFlagBit = CopyFlagBit ^ 0x40
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Enabling Copy Flag bit in the temporary buffer")
        else:
            if CopyFlagBit & 0x40 == 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CopyFlag bit already disabled. So doing nothing")
            else:
                CopyFlagBit = CopyFlagBit ^ 0x40
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Disabling Copy Flag bit in the temporary buffer")

        if self.__spiMode != True:
            self.Cmd7()

        modifiedCSDbuff.SetByte(index = 14, value = CopyFlagBit)
        modifiedCSDbuff.PrintToLog()

        self.Cmd27(ProgBuff = modifiedCSDbuff)
        self.GetCardStatus()

    # def SetOrResetCopyFlagBit(self, Enable = None):
    #     """
    #     Enable : 0 - Original / 1 - Copied
    #     """

    #     # Get CSD register value and check the card current status
    #     CSD = self.GetCSD()

    #     CsdRegister = sdcmdWrap.CSD_REGISTER_FIELD_STRUCT()
    #     CSD_STRUCT_VER = self.GetCSDStructVer()
    #     csdStruct = eval("sdcmdWrap.CSD_REGISTER_FIELD_STRUCT_VER%d()" % CSD_STRUCT_VER)

    #     if Enable == 1:
    #         if self.CSDRegister.uiCopy == 1:
    #             self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CopyFlag bit already enabled. So doing nothing")
    #             if self.__spiMode != True:
    #                 self.Cmd7()
    #             return
    #         elif self.CSDRegister.uiCopy == 0:
    #             csdStruct.uiCopy = 1
    #             if self.__spiMode != True:
    #                 self.Cmd7()
    #     elif Enable == 0:
    #         if self.CSDRegister.uiCopy == 0:
    #             self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CopyFlag bit already disabled. So doing nothing")
    #             if self.__spiMode != True:
    #                 self.Cmd7()
    #             return
    #         elif self.CSDRegister.uiCopy == 1:
    #             csdStruct.uiCopy = 0
    #             if self.__spiMode != True:
    #                 self.Cmd7()
    #     else:
    #         raise ValidationError.TestFailError(self.fn, "Enable mode can not be None. Pass either 0 to disable or 1 to enable Copy Flag bit of CSD register")

    #     exec("CsdRegister.CsdRegisterFieldStructVer%d = csdStruct" % CSD_STRUCT_VER)
    #     self.Cmd27(CsdRegister)


    def CheckCopyFlagBit(self):
        """
        returns 0 if CopyFlag bit is disabled and 1 if CopyFlag bit is enabled
        """

        # Get CSD register value
        CSD = self.GetCSD()
        self.Cmd7()

        return self.CSDRegister.uiCopy

    def __FlipWriteProtectBit(self, wpMode = None):
        """
        This API should be called immediately after CMD9.
        """

        Buff = ServiceWrap.Buffer.CreateBuffer(16, 0x00, isSector = False)
        Buff.Copy(thisOffset = 0, srcBuf = self.__CSDresponceBuff, srcOffset = 1, count = 16)

        WRITE_PROTECT = Buff.GetOneByteToInt(offset = 14)

        if wpMode == "TMP_WRITE_PROTECT":
            WRITE_PROTECT = WRITE_PROTECT ^ 0x10
        elif wpMode == "PERM_WRITE_PROTECT":
            WRITE_PROTECT = WRITE_PROTECT ^ 0x20
        else:
            raise ValidationError.TestFailError(self.fn, "invalid wpMode option")

        Buff.SetByte(14, WRITE_PROTECT)
        return Buff

    #def __FlipWriteProtectBit(self, wpMode = None):
        #"""
        #This API should be called immediately after CMD9.
        #"""

        #CsdRegister = sdcmdWrap.CSD_REGISTER_FIELD_STRUCT()

        #CSD_STRUCT_VER = self.GetCSDStructVer()

        #csdStruct = eval("sdcmdWrap.CSD_REGISTER_FIELD_STRUCT_VER%d()" % CSD_STRUCT_VER)

        #if wpMode == "TMP_WRITE_PROTECT":
            #csdStruct.uiTmpWriteProtect = not self.CSDRegister.uiTmpWriteProtect
        #elif wpMode == "PERM_WRITE_PROTECT":
            #csdStruct.uiPerm_Write_Protect = not self.CSDRegister.uiPerm_Write_Protect
        #else:
            #raise ValidationError.TestFailError(self.fn, "invalid wpMode option")

        #exec("CsdRegister.CsdRegisterFieldStructVer%d = csdStruct" % CSD_STRUCT_VER)
        #return CsdRegister

    def PutCardInWriteProtectMode(self, wpMode = None, expectError = False):
        """
        wpMode : "TMP_WRITE_PROTECT" - Enable temporary write protection / "PERM_WRITE_PROTECT" - Enable permanent write protection
        """
        if wpMode == None:
            raise ValidationError.TestFailError(self.fn, "WP mode can not be None. Pass either TMP_WRITE_PROTECT for temporary write protection or PERM_WRITE_PROTECT for Permanent write protection")

        # Send card to Standby mode
        self.Cmd7(deSelect = True)

        # Get CSD register value and check the card current status
        self.Cmd9()
        self.Cmd7()
        WRITE_PROTECT = self.__CSDresponceBuff.GetOneByteToInt(offset = 15)

        if expectError == False:
            if wpMode == "TMP_WRITE_PROTECT":
                if WRITE_PROTECT & 0x10 != 0 :
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TMP_WRITE_PROTECT bit already enabled. So doing nothing")
                    return 1
            if wpMode == "PERM_WRITE_PROTECT":
                if WRITE_PROTECT & 0x20 != 0:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PERM_WRITE_PROTECT bit already enabled. So doing nothing")
                    return 1
        else:
            pass    # Forfully try to modify Tmp/Pwr Write protection bit

        modifiedCSDbuff = self.__FlipWriteProtectBit(wpMode)
        self.Cmd27(modifiedCSDbuff)
        self.__WriteToReadOnlyBitsOfCSDnVerifyCMD27Status = self.GetCardStatus()

        # Cross check card status
        self.Cmd7(deSelect = True)
        self.Cmd9()
        self.Cmd7()

        WRITE_PROTECT = self.__CSDresponceBuff.GetOneByteToInt(offset = 15)

        if wpMode == "TMP_WRITE_PROTECT":
            if WRITE_PROTECT & 0x10 != 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TMP_WRITE_PROTECT bit is enabled. Card is put to temporary write protected mode")
            else:
                raise ValidationError.TestFailError(self.fn, "Failed to put card in Temp Write Protected Mode")

        if wpMode == "PERM_WRITE_PROTECT":
            if WRITE_PROTECT & 0x20 != 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PERM_WRITE_PROTECT bit is enabled. Card is put to permanent write protected mode")
            else:
                raise ValidationError.TestFailError(self.fn, "Failed to put card in Perm Write Protected Mode")

        return 0

    #def PutCardInWriteProtectMode(self, wpMode = None, expectError = False):
        #"""
        #wpMode : "TMP_WRITE_PROTECT"/"PERM_WRITE_PROTECT"
        #"""
        #if wpMode == None:
            #raise ValidationError.TestFailError(self.fn, "WP mode can not be None. Pass either TMP_WRITE_PROTECT for temporary write protection or PERM_WRITE_PROTECT for Permanent write protection")

        ## Get CSD register value and check the card current status
        #CSD = self.GetCSD()
        #self.Cmd7()

        #if expectError == False:
            #if wpMode == "TMP_WRITE_PROTECT":
                #if self.CSDRegister.uiTmpWriteProtect == 1:
                    #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TMP_WRITE_PROTECT bit already enabled. So doing nothing")
                    #return 1
            #if wpMode == "PERM_WRITE_PROTECT":
                #if self.CSDRegister.uiPerm_Write_Protect == 1:
                    #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PERM_WRITE_PROTECT bit already enabled. So doing nothing")
                    #return 1
        #else:
            #pass  # forfully try to modify Tmp/Pwr Write protection bit

        #CsdRegister = self.__FlipWriteProtectBit(wpMode)
        #self.Cmd27(CsdRegister)

        #self.__WriteToReadOnlyBitsOfCSDnVerifyCMD27Status = self.GetCardStatus()

        ## Cross check card status
        #CSD = self.GetCSD()
        #self.Cmd7()

        #if wpMode == "TMP_WRITE_PROTECT":
            #if self.CSDRegister.uiTmpWriteProtect != 0:
                #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TMP_WRITE_PROTECT bit is enabled. Card is put to temporary write protected mode")
            #else:
                #raise ValidationError.TestFailError(self.fn, "Failed to put card in Temp Write Protected Mode")

        #if wpMode == "PERM_WRITE_PROTECT":
            #if self.CSDRegister.uiPerm_Write_Protect != 0:
                #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PERM_WRITE_PROTECT bit is enabled. Card is put to permanent write protected mode")
            #else:
                #raise ValidationError.TestFailError(self.fn, "Failed to put card in Perm Write Protected Mode")
        #return 0


    def RemoveCardFromWriteProtectMode(self, wpMode = None, expectError = False):
        """
        wpMode : TMP_WRITE_PROTECT - disable temporary write protection / PERM_WRITE_PROTECT - disable permanent write protection
        """

        if wpMode == None:
            raise ValidationError.TestFailError(self.fn, "WP mode can not be None. Pass either TMP_WRITE_PROTECT for temporary write protection or PERM_WRITE_PROTECT for Permanent write protection")

        # Send card to Standby mode
        self.Cmd7(deSelect = True)

        # Get CSD register value and check the card current status
        self.Cmd9()
        self.Cmd7()
        WRITE_PROTECT = self.__CSDresponceBuff.GetOneByteToInt(offset = 15)

        if expectError == False:
            if wpMode == "TMP_WRITE_PROTECT":
                if WRITE_PROTECT & 0x10 == 0:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TMP_WRITE_PROTECT bit already disabled. So doing nothing")
                    return 1
            if wpMode == "PERM_WRITE_PROTECT":
                if WRITE_PROTECT & 0x20 == 0:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PERM_WRITE_PROTECT bit already disabled. So doing nothing")
                    return 1
        else:
            pass

        modifiedCSDbuff = self.__FlipWriteProtectBit(wpMode)
        self.Cmd27(modifiedCSDbuff)
        self.__WriteToReadOnlyBitsOfCSDnVerifyCMD27Status = self.GetCardStatus()

        # Cross check card status
        self.Cmd7(deSelect = True)
        self.Cmd9()
        self.Cmd7()

        WRITE_PROTECT = self.__CSDresponceBuff.GetOneByteToInt(offset = 15)

        if wpMode == "TMP_WRITE_PROTECT":
            if WRITE_PROTECT & 0x10 == 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TMP_WRITE_PROTECT bit is disabled. Card is removed from Write Protected Mode")
            else:
                raise ValidationError.TestFailError(self.fn, "Failed to remove the card from Temp Write Protected Mode")

        if wpMode == "PERM_WRITE_PROTECT":
            if WRITE_PROTECT & 0x20 == 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PERM_WRITE_PROTECT bit is disabled. Card is removed from Write Protected Mode")
            else:
                raise ValidationError.TestFailError(self.fn, "Failed to remove the card from Perm Write Protected Mode")

        return 0

    #def RemoveCardFromWriteProtectMode(self, wpMode = None, expectError = False):
        #"""
        #wpMode : TMP_WRITE_PROTECT - disable temporary write protection / PERM_WRITE_PROTECT - disable permanent write protection
        #"""

        #if wpMode == None:
            #raise ValidationError.TestFailError(self.fn, "WP mode can not be None. Pass either TMP_WRITE_PROTECT for temporary write protection or PERM_WRITE_PROTECT for Permanent write protection")

        ## Get CSD register value and check the card current status
        #CSD = self.GetCSD()
        #self.Cmd7()

        #if expectError == False:
            #if wpMode == "TMP_WRITE_PROTECT":
                #if self.CSDRegister.uiTmpWriteProtect == 0:
                    #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TMP_WRITE_PROTECT bit already disabled. So doing nothing")
                    #return 1
            #if wpMode == "PERM_WRITE_PROTECT":
                #if self.CSDRegister.uiPerm_Write_Protect == 0:
                    #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PERM_WRITE_PROTECT bit already disabled. So doing nothing")
                    #return 1
        #else:
            #pass

        #csdStruct = self.__FlipWriteProtectBit(wpMode)
        #self.Cmd27(csdStruct)

        #self.__WriteToReadOnlyBitsOfCSDnVerifyCMD27Status = self.GetCardStatus()

        ## Cross check card status
        #CSD = self.GetCSD()
        #self.Cmd7()

        #if wpMode == "TMP_WRITE_PROTECT":
            #if self.CSDRegister.uiTmpWriteProtect == 0:
                #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TMP_WRITE_PROTECT bit is disabled. Card is removed from Write Protected Mode")
            #else:
                #raise ValidationError.TestFailError(self.fn, "Failed to remove the card from Temp Write Protected Mode")

        #if wpMode == "PERM_WRITE_PROTECT":
            #if self.CSDRegister.uiPerm_Write_Protect == 0:
                #self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PERM_WRITE_PROTECT bit is disabled. Card is removed from Write Protected Mode")
            #else:
                #raise ValidationError.TestFailError(self.fn, "Failed to remove the card from Perm Write Protected Mode")

        #return 0


    def CheckWriteProtectedMode(self):
        """
        returns TMP_WRITE_PROTECT and PERM_WRITE_PROTECT bit
        """
        # Get CSD register value
        self.GetCSD()

        self.Cmd7()

        return self.CSDRegister.uiTmpWriteProtect, self.CSDRegister.uiPerm_Write_Protect

    def CheckWriteProtectedMode_SPI(self):
        """
        returns TMP_WRITE_PROTECT and PERM_WRITE_PROTECT bit
        """
        self.GetCSD()
        WRITE_PROTECT = self.ArrCsdRegisterFieldStruct[14]

        if WRITE_PROTECT & 0x10 == 0:
            tempWriteProtectBit = 0
        else:
            tempWriteProtectBit = 1

        if WRITE_PROTECT & 0x20 == 0:
            permWriteProtectBit = 0
        else:
            permWriteProtectBit = 1

        return tempWriteProtectBit, permWriteProtectBit


    def PutCardInWriteProtectMode_SPI(self, wpMode = None,ForceCheck = False):
        """
        wpMode : "TMP_WRITE_PROTECT" - Enable temporary write protection / "PERM_WRITE_PROTECT" - Enable permanent write protection
        """
        if wpMode == None:
            raise ValidationError.TestFailError(self.fn, "WP mode can not be None. Pass either TMP_WRITE_PROTECT for temporary write protection or PERM_WRITE_PROTECT for Permanent write protection")

        # Get CSD register value and check the card current status
        self.GetCSD()
        WRITE_PROTECT = self.ArrCsdRegisterFieldStruct[14]

        if ForceCheck == False:
            if wpMode == "TMP_WRITE_PROTECT":
                if WRITE_PROTECT & 0x10 != 0:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TMP_WRITE_PROTECT bit already enabled. So doing nothing")
                    return 1
            if wpMode == "PERM_WRITE_PROTECT":
                if WRITE_PROTECT & 0x20 != 0:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PERM_WRITE_PROTECT bit already enabled. So doing nothing")
                    return 1

        modifiedCSDbuff = ServiceWrap.Buffer.CreateBuffer(16, 0x00, isSector = False)
        for offset in range(0, 16):
            modifiedCSDbuff.SetByte(index = offset, value = self.ArrCsdRegisterFieldStruct[offset])

        if wpMode == "TMP_WRITE_PROTECT":
            WRITE_PROTECT = WRITE_PROTECT ^ 0x10
        elif wpMode == "PERM_WRITE_PROTECT":
            WRITE_PROTECT = WRITE_PROTECT ^ 0x20
        else:
            raise ValidationError.TestFailError(self.fn, "invalid wpMode option")

        modifiedCSDbuff.SetByte(index = 14, value = WRITE_PROTECT)
        self.Cmd27(modifiedCSDbuff)

        # Cross check card status
        self.GetCSD()
        WRITE_PROTECT = self.ArrCsdRegisterFieldStruct[14]

        if wpMode == "TMP_WRITE_PROTECT":
            if WRITE_PROTECT & 0x10 != 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TMP_WRITE_PROTECT bit is enabled. Card is put to Write Protected Mode")
            else:
                raise ValidationError.TestFailError(self.fn, "Failed to put card in Temp Write Protected Mode")

        if wpMode == "PERM_WRITE_PROTECT":
            if WRITE_PROTECT & 0x20 != 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PERM_WRITE_PROTECT bit is enabled. Card is put to Write Protected Mode")
            else:
                raise ValidationError.TestFailError(self.fn, "Failed to put card in Perm Write Protected Mode")

        return 0

    # def PutCardInWriteProtectMode_SPI(self, wpMode = None, ForceCheck = False):
    #     if wpMode == None:
    #         raise ValidationError.TestFailError(self.fn, "WP mode can not be None. Pass either TMP_WRITE_PROTECT for temporary write protection or PERM_WRITE_PROTECT for Permanent write protection")

    #     # Get CSD register value and check the card current status
    #     self.GetCSD()
    #     WRITE_PROTECT = self.ArrCsdRegisterFieldStruct[14]

    #     if ForceCheck == False:
    #         if wpMode == "TMP_WRITE_PROTECT":
    #             if WRITE_PROTECT & 0x10 != 0:
    #                 self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TMP_WRITE_PROTECT bit already enabled. So doing nothing")
    #                 return 1
    #         if wpMode == "PERM_WRITE_PROTECT":
    #             if WRITE_PROTECT & 0x20 != 0:
    #                 self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PERM_WRITE_PROTECT bit already enabled. So doing nothing")
    #                 return 1

    #     CsdRegister = sdcmdWrap.CSD_REGISTER_FIELD_STRUCT()
    #     CSD_STRUCT_VER = self.GetCSDStructVer()
    #     csdStruct = eval("sdcmdWrap.CSD_REGISTER_FIELD_STRUCT_VER%d()" % CSD_STRUCT_VER)

    #     if wpMode == "TMP_WRITE_PROTECT":
    #         csdStruct.uiTmpWriteProtect = WRITE_PROTECT ^ 0x10
    #     elif wpMode == "PERM_WRITE_PROTECT":
    #         csdStruct.uiPerm_Write_Protect = WRITE_PROTECT ^ 0x20
    #     else:
    #         raise ValidationError.TestFailError(self.fn, "invalid wpMode option")

    #     exec("CsdRegister.CsdRegisterFieldStructVer%d = csdStruct" % CSD_STRUCT_VER)
    #     self.Cmd27(CsdRegister)

    #     # Cross check card status
    #     self.GetCSD()
    #     WRITE_PROTECT = self.ArrCsdRegisterFieldStruct[14]

    #     if wpMode == "TMP_WRITE_PROTECT":
    #         if WRITE_PROTECT & 0x10 != 0:
    #             self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TMP_WRITE_PROTECT bit is enabled. Card is put to temporary write protected mode")
    #         else:
    #             raise ValidationError.TestFailError(self.fn, "Failed to put card in Temp Write Protected Mode")
    #     if wpMode == "PERM_WRITE_PROTECT":
    #         if WRITE_PROTECT & 0x20 != 0:
    #             self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PERM_WRITE_PROTECT bit is enabled. Card is put to permanent write protected mode")
    #         else:
    #             raise ValidationError.TestFailError(self.fn, "Failed to put card in Perm Write Protected Mode")

    #     return 0


    def RemoveCardFromWriteProtectMode_SPI(self, wpMode = None,ForceCheck = False):
        """
        wpMode : TMP_WRITE_PROTECT - disable temporary write protection / PERM_WRITE_PROTECT - disable permanent write protection
        """
        if wpMode == None:
            raise ValidationError.TestFailError(self.fn, "WP mode can not be None. Pass either TMP_WRITE_PROTECT for temporary write protection or PERM_WRITE_PROTECT for Permanent write protection")

        # Get CSD register value and check the card current status
        self.GetCSD()
        WRITE_PROTECT = self.ArrCsdRegisterFieldStruct[14]

        if ForceCheck == False:
            if wpMode == "TMP_WRITE_PROTECT":
                if WRITE_PROTECT & 0x10 == 0:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TMP_WRITE_PROTECT bit already disabled. So doing nothing")
                    return 1
            if wpMode == "PERM_WRITE_PROTECT":
                if WRITE_PROTECT & 0x20 == 0:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PERM_WRITE_PROTECT bit already disabled. So doing nothing")
                    return 1

        modifiedCSDbuff = ServiceWrap.Buffer.CreateBuffer(16, 0x00, isSector = False)
        for offset in range(0, 16):
            modifiedCSDbuff.SetByte(index = offset, value = self.ArrCsdRegisterFieldStruct[offset])

        if wpMode == "TMP_WRITE_PROTECT":
            WRITE_PROTECT = WRITE_PROTECT ^ 0x10
        elif wpMode == "PERM_WRITE_PROTECT":
            WRITE_PROTECT = WRITE_PROTECT ^ 0x20
        else:
            raise ValidationError.TestFailError(self.fn, "invalid wpMode option")

        modifiedCSDbuff.SetByte(index = 14, value = WRITE_PROTECT)
        self.Cmd27(modifiedCSDbuff)

        # Cross check card status
        self.GetCSD()
        WRITE_PROTECT = self.ArrCsdRegisterFieldStruct[14]

        if wpMode == "TMP_WRITE_PROTECT":
            if WRITE_PROTECT & 0x10 == 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TMP_WRITE_PROTECT bit is disabled. Card is removed from Write Protected Mode")
            else:
                raise ValidationError.TestFailError(self.fn, "Failed to remove the card from Temp Write Protected Mode")

        if wpMode == "PERM_WRITE_PROTECT":
            if WRITE_PROTECT & 0x20 == 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PERM_WRITE_PROTECT bit is disabled. Card is removed from Write Protected Mode")
            else:
                raise ValidationError.TestFailError(self.fn, "Failed to remove the card from Perm Write Protected Mode")

        return 0

    # def RemoveCardFromWriteProtectMode_SPI(self, wpMode = None, ForceCheck = False):
    #     """
    #     wpMode : TMP_WRITE_PROTECT - disable temporary write protection / PERM_WRITE_PROTECT - disable permanent write protection
    #     """

    #     if wpMode == None:
    #         raise ValidationError.TestFailError(self.fn, "WP mode can not be None. Pass either TMP_WRITE_PROTECT for temporary write protection or PERM_WRITE_PROTECT for Permanent write protection")

    #     # Get CSD register value and check the card current status
    #     self.GetCSD()
    #     WRITE_PROTECT = self.ArrCsdRegisterFieldStruct[14]

    #     if ForceCheck == False:
    #         if wpMode == "TMP_WRITE_PROTECT":
    #             if WRITE_PROTECT & 0x10 == 0:
    #                 self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TMP_WRITE_PROTECT bit already disabled. So doing nothing")
    #                 return 1
    #         if wpMode == "PERM_WRITE_PROTECT":
    #             if WRITE_PROTECT & 0x20 == 0:
    #                 self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PERM_WRITE_PROTECT bit already disabled. So doing nothing")
    #                 return 1

    #     CsdRegister = sdcmdWrap.CSD_REGISTER_FIELD_STRUCT()
    #     CSD_STRUCT_VER = self.GetCSDStructVer()
    #     csdStruct = eval("sdcmdWrap.CSD_REGISTER_FIELD_STRUCT_VER%d()" % CSD_STRUCT_VER)

    #     if wpMode == "TMP_WRITE_PROTECT":
    #         csdStruct.uiTmpWriteProtect = WRITE_PROTECT ^ 0x10
    #     elif wpMode == "PERM_WRITE_PROTECT":
    #         csdStruct.uiPerm_Write_Protect = WRITE_PROTECT ^ 0x20
    #     else:
    #         raise ValidationError.TestFailError(self.fn, "invalid wpMode option")

    #     exec("CsdRegister.CsdRegisterFieldStructVer%d = csdStruct" % CSD_STRUCT_VER)
    #     self.Cmd27(csdStruct)

    #     # Cross check card status
    #     self.GetCSD()
    #     WRITE_PROTECT = self.ArrCsdRegisterFieldStruct[14]

    #     if wpMode == "TMP_WRITE_PROTECT":
    #         if WRITE_PROTECT & 0x10 == 0:
    #             self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "TMP_WRITE_PROTECT bit is disabled. Card is removed from Write Protected Mode")
    #         else:
    #             raise ValidationError.TestFailError(self.fn, "Failed to remove the card from Temp Write Protected Mode")
    #     if wpMode == "PERM_WRITE_PROTECT":
    #         if WRITE_PROTECT & 0x20 == 0:
    #             self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "PERM_WRITE_PROTECT bit is disabled. Card is removed from Write Protected Mode")
    #         else:
    #             raise ValidationError.TestFailError(self.fn, "Failed to remove the card from Perm Write Protected Mode")

    #     return 0

    def SetCSDRegBit(self, CheckBit = None, Verification = None):
        """
        Set's CSD_STRUCTURE, FILE_FORMAT_GRP or FILE_FORMAT bit of CSD register
        """
        CSD_STRUCTURE = 0
        FILE_FORMAT_GRP = 1
        FILE_FORMAT = 2

        if CheckBit == None:
            raise ValidationError.TestFailError(self.fn, "CSD bit can not be None. Pass either 0,1,2 to enable CSD_STRUCTURE,FILE_FORMAT_GRP,FILE_FORMAT bit of CSD register")

        #Send card to Standby mode
        self.Cmd7(deSelect = True)

        #Get CSD register value and check the card current status
        self.Cmd9()

        self.__CSDresponceBuff.PrintToLog(start = 0, end = 16)

        modifiedCSDbuff = ServiceWrap.Buffer.CreateBuffer(16, 0x00, isSector = False)
        modifiedCSDbuff.Copy(thisOffset = 0, srcBuf = self.__CSDresponceBuff, srcOffset = 1, count = 16)
        modifiedCSDbuff.PrintToLog()

        Structure = modifiedCSDbuff.GetOneByteToInt(offset = 0x0)
        Format = modifiedCSDbuff.GetOneByteToInt(offset = 14)

        if Verification == 0:
            if CheckBit == 0:
                CStructure = Structure ^ 0x40
                modifiedCSDbuff.SetByte(00, CStructure)
            elif CheckBit == 2:
                FFormat = Format ^ 0x80
                modifiedCSDbuff.SetByte(14, FFormat)
            else:
                FFormatGrp = Format ^ 0x04
                modifiedCSDbuff.SetByte(14, FFormatGrp)

            modifiedCSDbuff.PrintToLog()

            self.Cmd7()
            self.Cmd27(modifiedCSDbuff)
            self.__WriteToReadOnlyBitsOfCSDnVerifyCMD27Status = self.GetCardStatus()

            self.Cmd7(deSelect=True)
            self.Cmd9()

            VerifyCSDBuff = ServiceWrap.Buffer.CreateBuffer(16, 0x00, isSector=False)
            VerifyCSDBuff.Copy(thisOffset = 0, srcBuf = self.__CSDresponceBuff, srcOffset = 1, count = 16)

            VerifyByte0 = VerifyCSDBuff.GetOneByteToInt(offset = 0x0)
            VerifyByte1 = VerifyCSDBuff.GetOneByteToInt(offset = 14)

            self.Cmd7()

            if CheckBit == FILE_FORMAT_GRP:
                if VerifyByte1 == FFormatGrp:
                    return 0
                else:
                    return 1
            elif CheckBit == FILE_FORMAT:
                if VerifyByte1 == FFormat:
                    return 0
                else:
                    return 1
            else:
                if VerifyByte0 == CStructure:
                    return 0
                else:
                    return 1
        elif Verification == 1:
            self.Cmd7(deSelect=True)
            self.Cmd9()

            self.__CSDresponceBuff.PrintToLog(start = 0, end = 16)

            VerifyCSDBuff = ServiceWrap.Buffer.CreateBuffer(16, 0x00, isSector=False)
            VerifyCSDBuff.Copy(thisOffset = 0, srcBuf = self.__CSDresponceBuff, srcOffset = 1, count = 16)

            if CheckBit == 0:
                CStructure = Structure & 0x40
                VerifyCSDBuff.SetByte(0x0, CStructure)
            elif CheckBit == 2:
                FFormat = Format & 0x80
                VerifyCSDBuff.SetByte(14, FFormat)
            else:
                FFormatGrp = Format & 0x04
                VerifyCSDBuff.SetByte(14, FFormatGrp)

            VerifyByte0 = VerifyCSDBuff.GetOneByteToInt(offset = 0x0)
            VerifyByte1 = VerifyCSDBuff.GetOneByteToInt(offset = 14)

            if CheckBit == FILE_FORMAT_GRP:
                if VerifyByte1 == FFormatGrp:
                    return 1
                else:
                    return 0
            elif CheckBit == FILE_FORMAT:
                if VerifyByte1 == FFormat:
                    return 1
                else:
                    return 0

            self.Cmd7()

    def WriteToReadOnlyFieldsOfCSD(self, WriteField = None, WriteValue = None):
        """
        Description: Tries to write the read only bits of CSD Register, This function is compliance with CSD structure version 2.
        Parameters Description:
             WriteField - Name of the CSD register (read or one time writable) field, Name should be get from the ENUM gvar.CSD
             WriteValue - Value of the field to be written
        """
        if WriteField == None:
            raise ValidationError.TestFailError(self.fn, "WriteField can not be None. Pass the name of any one of CSD register read only fields")

        if self.__spiMode != True:
            # Send card to Standby mode
            self.Cmd7(deSelect = True)

        # Get CSD register value and check the card current status
        self.Cmd9()

        if self.__spiMode != True:
            self.Cmd7() # Select the card

        Buff = ServiceWrap.Buffer.CreateBuffer(16, 0x00, isSector = False)
        Buff.Copy(thisOffset = 0, srcBuf = self.__CSDresponceBuff, srcOffset = 1, count = 16)

        if gvar.CSD.CSD_STRUCTURE == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 0)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x3, ("Given CSD field %s's value is larger than expected" % gvar.CSD.CSD_STRUCTURE)
                WriteValue = (WriteValue << 6) | (ActualData & 0x3F)
            Buff.SetByte(index = 0, value = WriteValue)
        elif gvar.CSD.Reserv1 == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 0)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x3F, ("Given CSD field %s's value is larger than expected" % gvar.CSD.Reserv1)
                WriteValue = WriteValue | (ActualData & 0xC0)
            Buff.SetByte(index = 0, value = WriteValue)
        elif gvar.CSD.TAAC == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 1)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0xFF, ("Given CSD field %s's value is larger than expected" % gvar.CSD.TAAC)
            Buff.SetByte(index = 1, value = WriteValue)
        elif gvar.CSD.NSAC == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 2)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0xFF, ("Given CSD field %s's value is larger than expected" % gvar.CSD.NSAC)
            Buff.SetByte(index = 2, value = WriteValue)
        elif gvar.CSD.TRAN_SPEED == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 3)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0xFF, ("Given CSD field %s's value is larger than expected" % gvar.CSD.TRAN_SPEED)
            Buff.SetByte(index = 3, value = WriteValue)
        elif gvar.CSD.CCC == WriteField:
            ActualData = Buff.GetTwoBytesToInt(offset = 4, little_endian = False)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0xFFF, ("Given CSD field %s's value is larger than expected" % gvar.CSD.CCC)
                WriteValue = (WriteValue << 4) | (ActualData & 0xF)
            Buff.SetTwoBytes(index = 4, value = WriteValue, little_endian = False)
        elif gvar.CSD.READ_BL_LEN == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 5)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0xF, ("Given CSD field %s's value is larger than expected" % gvar.CSD.READ_BL_LEN)
                WriteValue = WriteValue | (ActualData & 0xF0)
            Buff.SetByte(index = 5, value = WriteValue)
        elif gvar.CSD.READ_BL_PARTIAL == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 6)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x1, ("Given CSD field %s's value is larger than expected" % gvar.CSD.READ_BL_PARTIAL)
                WriteValue = (WriteValue << 7) | (ActualData & 0x7F)
            Buff.SetByte(index = 6, value = WriteValue)
        elif gvar.CSD.WRITE_BLK_MISALIGN == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 6)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x1, ("Given CSD field %s's value is larger than expected" % gvar.CSD.WRITE_BLK_MISALIGN)
                WriteValue = (WriteValue << 6) | (ActualData & 0xBF)
            Buff.SetByte(index = 6, value = WriteValue)
        elif gvar.CSD.READ_BLK_MISALIGN == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 6)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x1, ("Given CSD field %s's value is larger than expected" % gvar.CSD.READ_BLK_MISALIGN)
                WriteValue = (WriteValue << 5) | (ActualData & 0xDF)
            Buff.SetByte(index = 6, value = WriteValue)
        elif gvar.CSD.DSR_IMP == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 6)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x1, ("Given CSD field %s's value is larger than expected" % gvar.CSD.DSR_IMP)
                WriteValue = (WriteValue << 4) | (ActualData & 0xEF)
            Buff.SetByte(index = 6, value = WriteValue)
        elif gvar.CSD.Reserv2 == WriteField:
            ActualData = Buff.GetTwoBytesToInt(offset = 6, little_endian = False)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x3F, ("Given CSD field %s's value is larger than expected" % gvar.CSD.Reserv2)
                WriteValue = (WriteValue << 6) | (ActualData & 0xF03F)
            Buff.SetTwoBytes(index = 6, value = WriteValue, little_endian = False)
        elif gvar.CSD.C_SIZE == WriteField:
            ActualData = Buff.GetFourBytesToInt(offset = 7, little_endian = False)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x3FFFFF, ("Given CSD field %s's value is larger than expected" % gvar.CSD.C_SIZE)
                WriteValue = WriteValue | (ActualData & 0xC00000)
            Buff.SetFourBytes(index = 7, value = WriteValue, little_endian = False)
        elif gvar.CSD.Reserv3 == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 10)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x1, ("Given CSD field %s's value is larger than expected" % gvar.CSD.Reserv3)
                WriteValue = (WriteValue << 7) | (ActualData & 0x7F)
            Buff.SetByte(index = 10, value = WriteValue)
        elif gvar.CSD.ERASE_BLK_EN == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 10)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x1, ("Given CSD field %s's value is larger than expected" % gvar.CSD.ERASE_BLK_EN)
                WriteValue = (WriteValue << 6) | (ActualData & 0xBF)
            Buff.SetByte(index = 10, value = WriteValue)
        elif gvar.CSD.SECTOR_SIZE == WriteField:
            ActualData = Buff.GetTwoBytesToInt(offset = 10, little_endian = False)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x7F, ("Given CSD field %s's value is larger than expected" % gvar.CSD.SECTOR_SIZE)
                WriteValue = (WriteValue << 7) | (ActualData & 0xC07F)
            Buff.SetTwoBytes(index = 10, value = WriteValue, little_endian = False)
        elif gvar.CSD.WP_GRP_SIZE == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 11)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x7F, ("Given CSD field %s's value is larger than expected" % gvar.CSD.WP_GRP_SIZE)
                WriteValue = WriteValue | (ActualData & 0x80)
            Buff.SetByte(index = 11, value = WriteValue)
        elif gvar.CSD.WP_GRP_ENABLE == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 12)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x1, ("Given CSD field %s's value is larger than expected" % gvar.CSD.WP_GRP_ENABLE)
                WriteValue = (WriteValue << 7) | (ActualData & 0x7F)
            Buff.SetByte(index = 12, value = WriteValue)
        elif gvar.CSD.Reserv4 == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 12)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x3, ("Given CSD field %s's value is larger than expected" % gvar.CSD.Reserv4)
                WriteValue = (WriteValue << 5) | (ActualData & 0x9F)
            Buff.SetByte(index = 12, value = WriteValue)
        elif gvar.CSD.R2W_FACTOR == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 12)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x7, ("Given CSD field %s's value is larger than expected" % gvar.CSD.R2W_FACTOR)
                WriteValue = (WriteValue << 2) | (ActualData & 0xE3)
            Buff.SetByte(index = 12, value = WriteValue)
        elif gvar.CSD.WRITE_BL_LEN == WriteField:
            ActualData = Buff.GetTwoBytesToInt(offset = 12, little_endian = False)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0xF, ("Given CSD field %s's value is larger than expected" % gvar.CSD.WRITE_BL_LEN)
                WriteValue = (WriteValue << 6) | (ActualData & 0xFC3F)
            Buff.SetTwoBytes(index = 12, value = WriteValue, little_endian = False)
        elif gvar.CSD.WRITE_BL_PARTIAL == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 13)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x1, ("Given CSD field %s's value is larger than expected" % gvar.CSD.WRITE_BL_PARTIAL)
                WriteValue = (WriteValue << 5) | (ActualData & 0xDF)
            Buff.SetByte(index = 13, value = WriteValue)
        elif gvar.CSD.Reserv5 == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 13)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x1F, ("Given CSD field %s's value is larger than expected" % gvar.CSD.Reserv5)
                WriteValue = WriteValue | (ActualData & 0xE0)
            Buff.SetByte(index = 13, value = WriteValue)
        elif gvar.CSD.FILE_FORMAT_GRP == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 14)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x1, ("Given CSD field %s's value is larger than expected" % gvar.CSD.FILE_FORMAT_GRP)
                WriteValue = (WriteValue << 7) | (ActualData & 0x7F)
            Buff.SetByte(index = 14, value = WriteValue)
        elif gvar.CSD.COPY == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 14)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x1, ("Given CSD field %s's value is larger than expected" % gvar.CSD.COPY)
                WriteValue = (WriteValue << 6) | (ActualData & 0xBF)
            Buff.SetByte(index = 14, value = WriteValue)
        elif gvar.CSD.PERM_WRITE_PROTECT == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 14)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x1, ("Given CSD field %s's value is larger than expected" % gvar.CSD.PERM_WRITE_PROTECT)
                WriteValue = (WriteValue << 5) | (ActualData & 0xDF)
            Buff.SetByte(index = 14, value = WriteValue)
        elif gvar.CSD.FILE_FORMAT == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 14)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x3, ("Given CSD field %s's value is larger than expected" % gvar.CSD.FILE_FORMAT)
                WriteValue = (WriteValue << 2) | (ActualData & 0xF3)
            Buff.SetByte(index = 14, value = WriteValue)
        elif gvar.CSD.Reserv6 == WriteField:
            ActualData = Buff.GetOneByteToInt(offset = 14)
            if WriteValue == None:
                WriteValue = ActualData
            else:
                assert WriteValue <= 0x3, ("Given CSD field %s's value is larger than expected" % gvar.CSD.Reserv6)
                WriteValue = WriteValue | (ActualData & 0xFC)
            Buff.SetByte(index = 14, value = WriteValue)

        self.Cmd27(Buff)

        self.__WriteToReadOnlyBitsOfCSDnVerifyCMD27Status = self.GetCardStatus() #added to store the status after trying to modity CSD(CMD27)


    # def WriteToReadOnlyBitsOfCSDnVerify(self, WriteField = None, WriteValue = None):
    #     """
    #     Description: Tries to write the read only bits of CSD Register
    #     Parameters Description:
    #          WriteField - Name of the CSD register read only field
    #          WriteValue - Value of the field
    #     """
    #     if WriteField == None:
    #         raise ValidationError.TestFailError(self.fn, "WriteField can not be None. Pass the name of any one of CSD register read only fields")

    #     if self.__spiMode != True:
    #         # Send card to Standby mode
    #         self.Cmd7(deSelect = True)

    #     # Get CSD register value and check the card current status
    #     self.Cmd9()

    #     Buff = ServiceWrap.Buffer.CreateBuffer(16, 0x00, isSector = False)
    #     Buff.Copy(thisOffset = 0, srcBuf = self.__CSDresponceBuff, srcOffset = 1, count = 16)

    #     FirstByte = Buff.GetOneByteToInt(0x00)
    #     SecondByte = Buff.GetOneByteToInt(0x01)
    #     ThirdByte = Buff.GetOneByteToInt(0x02)
    #     FourthByte = Buff.GetOneByteToInt(0x03)
    #     FifthNSixthByte = Buff.GetTwoBytesToInt(offset = 0x04, little_endian = False)
    #     SeventhByte = Buff.GetOneByteToInt(0x06)
    #     EigthToEleventhByte = Buff.GetFourBytesToInt(offset = 0x07, little_endian = False)
    #     TwelfthByte = Buff.GetOneByteToInt(0x0B)
    #     ThirteenthByte = Buff.GetOneByteToInt(0x0C)
    #     FourteenthByte = Buff.GetOneByteToInt(0x0D)

    #     if WriteField == 17:
    #         if WriteValue == None:
    #             CSD_Struct = FirstByte
    #         else:
    #             CSD_Struct = WriteValue
    #             Buff.SetByte(0x00, CSD_Struct)
    #     elif WriteField == 18:
    #         if WriteValue == None:
    #             DataReadAccessTime = SecondByte
    #         else:
    #             DataReadAccessTime = WriteValue
    #             Buff.SetByte(0x01, DataReadAccessTime)
    #     elif WriteField == 2:
    #         if WriteValue == None:
    #             DataReadAccessTimeInCLK = ThirdByte
    #         else:
    #             DataReadAccessTimeInCLK = WriteValue
    #             Buff.SetByte(0x02, DataReadAccessTimeInCLK)
    #     elif WriteField == 3:
    #         if WriteValue == None:
    #             MaxDataTransferRate = FourthByte
    #             return MaxDataTransferRate
    #         else:
    #             MaxDataTransferRate = WriteValue
    #             Buff.SetByte(0x03, MaxDataTransferRate)
    #     elif WriteField == 4:
    #         if WriteValue == None:
    #             MaxDataTransferRate = FifthNSixthByte
    #         else:
    #             MaxDataTransferRate = WriteValue
    #             Buff.SetTwoBytes(0x04, MaxDataTransferRate)
    #     elif WriteField == 5:
    #         if WriteValue == None:
    #             MaxReadDataBlockLength = FifthNSixthByte
    #         else:
    #             MaxReadDataBlockLength = WriteValue
    #             Buff.SetTwoBytes(0x04, MaxReadDataBlockLength)
    #     elif WriteField == 6:
    #         if WriteValue == None:
    #             PartialBlocksForReadAllowed = SeventhByte
    #         else:
    #             PartialBlocksForReadAllowed = WriteValue
    #             Buff.SetByte(0x06, PartialBlocksForReadAllowed)
    #     elif WriteField == 7:
    #         if WriteValue == None:
    #             WriteBlockMisalignment = SeventhByte
    #         else:
    #             WriteBlockMisalignment = WriteValue
    #             Buff.SetByte(0x06, WriteBlockMisalignment)
    #     elif WriteField == 8:
    #         if WriteValue == None:
    #             ReadBlockMisalignment = SeventhByte
    #         else:
    #             ReadBlockMisalignment = WriteValue
    #             Buff.SetByte(0x06, ReadBlockMisalignment)
    #     elif WriteField == 9:
    #         if WriteValue == None:
    #             DSRImpletmented = SeventhByte
    #         else:
    #             DSRImpletmented = WriteValue
    #             Buff.SetByte(0x06, DSRImpletmented)
    #     elif WriteField == 10:
    #         if WriteValue == None:
    #             DeviseSize = EigthToEleventhByte
    #         else:
    #             DeviseSize = WriteValue
    #             Buff.SetFourBytes(0x07, DeviseSize)
    #     elif WriteField == 11:
    #         if WriteValue == None:
    #             EraseSingleBlockEnable = EigthToEleventhByte
    #         else:
    #             EraseSingleBlockEnable = WriteValue
    #             Buff.SetFourBytes(0x07, EraseSingleBlockEnable)
    #     elif WriteField == 12:
    #         if WriteValue == None:
    #             SectorSize1stHalf = EigthToEleventhByte
    #         else:
    #             SectorSize1stHalf = WriteValue
    #             Buff.SetFourBytes(0x07, SectorSize1stHalf)
    #     elif WriteField == 20:
    #         if WriteValue == None:
    #             SectorSize2ndHalf = TwelfthByte
    #         else:
    #             SectorSize2ndHalf = WriteValue
    #             Buff.SetByte(0x0B, SectorSize2ndHalf)
    #     elif WriteField == 19:
    #         if WriteValue == None:
    #             WriteProtectGroupSize = TwelfthByte
    #         else:
    #             WriteProtectGroupSize = WriteValue
    #             Buff.SetByte(0x0B, WriteProtectGroupSize)
    #     elif WriteField == 13:
    #         if WriteValue == None:
    #             WriteProtectGrpEnable = ThirteenthByte
    #         else:
    #             WriteProtectGrpEnable = WriteValue
    #             Buff.SetByte(0x0C, WriteProtectGrpEnable)
    #     elif WriteField == 14:
    #         if WriteValue == None:
    #             WriteSpeedFactor = ThirteenthByte
    #         else:
    #             WriteSpeedFactor = WriteValue
    #             Buff.SetByte(0x0C, WriteSpeedFactor)
    #     elif WriteField == 15:
    #         if WriteValue == None:
    #             MaxWriteDataBlockLength1stHalf = ThirteenthByte
    #         else:
    #             MaxWriteDataBlockLength1stHalf = WriteValue
    #             Buff.SetByte(0x0C, MaxWriteDataBlockLength1stHalf)
    #     elif WriteField == 21:
    #         if WriteValue == None:
    #             MaxWriteDataBlockLength2ndHalf = FourteenthByte
    #         else:
    #             MaxWriteDataBlockLength2ndHalf = WriteValue
    #             Buff.SetByte(0x0D, MaxWriteDataBlockLength2ndHalf)
    #     else:
    #         if WriteValue == None:
    #             PartialBlocksForWriteAllowed = FourteenthByte
    #         else:
    #             PartialBlocksForWriteAllowed = WriteValue
    #             Buff.SetByte(0x0D, PartialBlocksForWriteAllowed)

    #     #Buff.PrintToLog() #modified buffer

    #     modifiedCSDbuff = Buff

    #     if self.__spiMode != True:
    #         self.Cmd7()
    #     self.Cmd27(modifiedCSDbuff)

    #     self.__WriteToReadOnlyBitsOfCSDnVerifyCMD27Status = self.GetCardStatus() #added to store the status after trying to modity CSD(CMD27)

    #     if self.__spiMode != True:
    #         self.Cmd7(deSelect = True)
    #     self.Cmd9()

    #     VerifyCSDBuff = ServiceWrap.Buffer.CreateBuffer(16, 0x00, isSector = False)
    #     VerifyCSDBuff.Copy(thisOffset = 0, srcBuf = self.__CSDresponceBuff, srcOffset = 1, count = 16)

    #     if self.__spiMode != True:
    #         self.Cmd7()

    #     VerifyFirstByte = VerifyCSDBuff.GetOneByteToInt(0x00)
    #     VerifySecondByte = VerifyCSDBuff.GetOneByteToInt(0x01)
    #     VerifyThirdByte = VerifyCSDBuff.GetOneByteToInt(0x02)
    #     VerifyFourthByte = VerifyCSDBuff.GetOneByteToInt(0x03)
    #     VerifyFifthNSixthByte = VerifyCSDBuff.GetTwoBytesToInt(offset = 0x04, little_endian = False)
    #     VerifySeventhByte = VerifyCSDBuff.GetOneByteToInt(0x06)
    #     VerifyEigthToEleventhByte = VerifyCSDBuff.GetFourBytesToInt(offset = 0x07, little_endian = False)
    #     VerifyTwelfthByte = VerifyCSDBuff.GetOneByteToInt(0x0B)
    #     VerifyThirteenthByte = VerifyCSDBuff.GetOneByteToInt(0x0C)
    #     VerifyFourteenthByte = VerifyCSDBuff.GetOneByteToInt(0x0D)

    #     if WriteField == 17:
    #         if VerifyFirstByte == CSD_Struct:
    #             return 0
    #         else:
    #             return 1
    #     elif WriteField == 18:
    #         if VerifySecondByte == DataReadAccessTime:
    #             return 0
    #         else:
    #             return 1
    #     elif WriteField == 2:
    #         if VerifyThirdByte == DataReadAccessTimeInCLK:
    #             return 0
    #         else:
    #             return 1
    #     elif WriteField == 3:
    #         if VerifyFourthByte == MaxDataTransferRate:
    #             return 0
    #         else:
    #             return 1
    #     elif WriteField == 4:
    #         if VerifyFifthNSixthByte == MaxDataTransferRate:
    #             return 0
    #         else:
    #             return 1
    #     elif WriteField == 5:
    #         if VerifyFifthNSixthByte == MaxReadDataBlockLength:
    #             return 0
    #         else:
    #             return 1
    #     elif WriteField == 6:
    #         if VerifySeventhByte == PartialBlocksForReadAllowed:
    #             return 0
    #         else:
    #             return 1
    #     elif WriteField == 7:
    #         if VerifySeventhByte == WriteBlockMisalignment:
    #             return 0
    #         else:
    #             return 1
    #     elif WriteField == 8:
    #         if VerifySeventhByte == ReadBlockMisalignment:
    #             return 0
    #         else:
    #             return 1
    #     elif WriteField == 9:
    #         if VerifySeventhByte == DSRImpletmented:
    #             return 0
    #         else:
    #             return 1
    #     elif WriteField == 10:
    #         if VerifyEigthToEleventhByte == DeviseSize:
    #             return 0
    #         else:
    #             return 1
    #     elif WriteField == 11:
    #         if VerifyEigthToEleventhByte == EraseSingleBlockEnable:
    #             return 0
    #         else:
    #             return 1
    #     elif WriteField == 12:
    #         if VerifyEigthToEleventhByte == SectorSize1stHalf:
    #             return 0
    #         else:
    #             return 1
    #     elif WriteField == 20:
    #         if VerifyTwelfthByte == SectorSize2ndHalf:
    #             return 0
    #         else:
    #             return 1
    #     elif WriteField == 19:
    #         if VerifyTwelfthByte == WriteProtectGroupSize:
    #             return 0
    #         else:
    #             return 1
    #     elif WriteField == 13:
    #         if VerifyThirteenthByte == WriteProtectGrpEnable:
    #             return 0
    #         else:
    #             return 1
    #     elif WriteField == 14:
    #         if VerifyThirteenthByte == WriteSpeedFactor:
    #             return 0
    #         else:
    #             return 1
    #     elif WriteField == 15:
    #         if VerifyThirteenthByte == MaxWriteDataBlockLength1stHalf:
    #             return 0
    #         else:
    #             return 1
    #     elif WriteField == 21:
    #         if VerifyFourteenthByte == MaxWriteDataBlockLength2ndHalf:
    #             return 0
    #         else:
    #             return 1
    #     else:
    #         if VerifyFourteenthByte == PartialBlocksForWriteAllowed:
    #             return 0
    #         else:
    #             return 1

    # def WriteToReadOnlyBitsOfCSDnVerify(self, WriteField = None, WriteValue = None):
    #     """
    #     Description: Tries to write the read only bits of CSD Register
    #     Parameters Description:
    #          WriteField - Name of the CSD register read only field
    #          WriteValue - Value of the field
    #     """

    #     if WriteField == None:
    #         raise ValidationError.TestFailError(self.fn, "WriteField can not be None. Pass the name of any one of CSD register read only fields")

    #     # Get CSD register value and check the card current status
    #     self.GetCSD()

    #     CsdRegister = sdcmdWrap.CSD_REGISTER_FIELD_STRUCT()
    #     CSD_STRUCT_VER = self.GetCSDStructVer()
    #     csdStruct = eval("sdcmdWrap.CSD_REGISTER_FIELD_STRUCT_VER%d()" % CSD_STRUCT_VER)

    #     CSD_Reg_Fields_Dict = {"CSD_STRUCTURE": "uiCsdStructure", "TAAC": "uiTaac", "NSAC": "uiNsac", "TRAN_SPEED": "uiTranSpeed", "CCC": "uiCcc",
    #                            "READ_BL_LEN": "uiReadBlLen", "READ_BL_PARTIAL": "uiReadBlPartial", "WRITE_BLK_MISALIGN": "uiWriteBlkMisalign",
    #                            "READ_BLK_MISALIGN": "uiReadBlkMisalign", "DSR_IMP": "uiDsrImp", "C_SIZE": "uiC_Size", "ERASE_BLK_EN": "uiEraseBlkEn",
    #                            "SECTOR_SIZE": "uiSectorSize", "WP_GRP_SIZE": "uiWpGrpSize", "WP_GRP_ENABLE": "uiWpGrpEnable", "R2W_FACTOR": "uiR2WFactor",
    #                            "WRITE_BL_LEN": "uiWriteBlLen", "WRITE_BL_PARTIAL": "uiWritEBlPartial", "FILE_FORMAT_GRP": "uiFileFormatGrp", "COPY": "uiCopy",
    #                            "PERM_WRITE_PROTECT": "uiPerm_Write_Protect", "TMP_WRITE_PROTECT": "uiTmpWriteProtect", "FILE_FORMAT": "uiFileFormaT", "CRC": "uiCrc"}

    #     eval("WriteValue = (self.CSDRegister.%s ^ 1) if WriteValue == None else WriteValue" % CSD_Reg_Fields_Dict[WriteField])
    #     eval("csdStruct.%s = WriteValue" % CSD_Reg_Fields_Dict[WriteField])
    #     exec("CsdRegister.CsdRegisterFieldStructVer%d = csdStruct" % CSD_STRUCT_VER)

    #     self.Cmd7()
    #     self.Cmd27(CsdRegister)

    #     # added to store the status after trying to modity CSD(CMD27)
    #     self.__WriteToReadOnlyBitsOfCSDnVerifyCMD27Status = self.GetCardStatus()

    #     # Get CSD register value and check if value is modified or not
    #     self.GetCSD()
    #     self.Cmd7()

    #     status = eval("0 if self.CSDRegister.%s == csdStruct.%s else 1" % (CSD_Reg_Fields_Dict[WriteField], CSD_Reg_Fields_Dict[WriteField]))
    #     if status == 1:
    #         self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "CSD read only field '%s' is not modified" % WriteField)
    #     else:
    #         raise ValidationError.TestFailError(self.fn, "CSD read only field '%s' is modified" % WriteField)

    def VerifyReliableWrite(self, StartLBA, BlockCount, Pattern):
        """
        CTF has open JIRA for this API:5914 [CTISW-5914: Information required about API VERIFY RELIABLE WRITE].
        CVF JIRA - 'CVF-16550'.
        Since this API is out of scope for CVF, Implementing the VerifyReliableWrite API in test layer based
        on the host log captured for scripter directive VERIFY RELIABLE WRITE.
        """
        self.FUNCTION_ENTRY("VerifyReliableWrite")
        readDataBuffer = ServiceWrap.Buffer.CreateBuffer(BlockCount)
        self.Cmd18(startLbaAddress = StartLBA, transferLen = BlockCount, readDataBuffer = readDataBuffer)
        self.Cmd12()

        self.Compare(readDataBuffer, startLBA = StartLBA, blockCount = BlockCount, Pattern = Pattern)
        self.FUNCTION_EXIT("VerifyReliableWrite")

    def Write(self, startLba, transferLen, pattern = 0, forceMultipleWrite = False):
        writeDataBuffer = ServiceWrap.Buffer.CreateBuffer(transferLen)
        self.BufferFilling(writeDataBuffer, pattern)

        if (self.__SecureEnable == False):
            if transferLen == 1 and forceMultipleWrite == False:    # For single sector/block/lba write
                self.Cmd24(startLba, writeDataBuffer = writeDataBuffer)
            else:
                self.Cmd25(startLbaAddress = startLba, transferLen = transferLen, writeDataBuffer = writeDataBuffer)

            if self.__doErrorHandling == True:
                if(self.__spiMode != True):
                    CMD13_res = self.Cmd13()
                    if CMD13_res.GetOneByteToInt(1) != 0:
                        raise ValidationError.TestFailError(self.fn, "Previous CMD before CMD13 has an error")
        else:
            self.CardSecureWrite(CardSlot = SRW_CARD_SLOT, BlockCount = transferLen, StartLba = startLba, WriteDataBuffer = writeDataBuffer,
                        Selector = self.__selectorValue, Enable_Signature = self.__enableSignature, Authenticate = True)
            self.__enableSignature == True


    def Read(self, startLba, transferLen, readDataBuffer, forceMultipleRead = False):
        if (self.__SecureEnable == False):
            if transferLen == 1 and forceMultipleRead == False:
                self.Cmd17(startLba, readDataBuffer = readDataBuffer)
            else:
                self.Cmd18(startLbaAddress = startLba, transferLen = transferLen, readDataBuffer = readDataBuffer)

            if self.__doErrorHandling == True:
                if(self.__spiMode != True):

                    CMD13_res = self.Cmd13()
                    if CMD13_res.GetOneByteToInt(1) != 0:
                        raise ValidationError.TestFailError(self.fn, "Previous CMD before CMD13 has an error")
        else:
            self.CardSecureRead(CardSlot = SRW_CARD_SLOT, BlockCount = transferLen, StartLba = startLba, ReadDataBuffer = readDataBuffer,
                        Selector = self.__selectorValue, Authenticate = True)
        return 0


    def Erase(self, StartAddress, EndAddress):
        if (self.__SecureEnable == False):
            """
            Normal Card Erase
            """
            self.Cmd32(StartLBA = StartAddress)
            self.Cmd33(EndLBA = EndAddress)
            self.Cmd38()

            if self.__doErrorHandling == True:
                if(self.__spiMode != True):
                    self.Cmd13()
        else:
            """
            Secure Mode
            """
            blockCount = self.calculate_blockcount(startLba = StartAddress, endLba = EndAddress)
            self.Cmd55()
            self.CardSecureErase(CardSlot = SRW_CARD_SLOT, BlockCount = blockCount, StartLba = StartAddress,
                        Selector = self.__selectorValue, Authenticate = True)
        return 0


    # def LockUnlockSdCard(self, cop = False, Erase = False, LockUnLock = False, ClrPwd = False, SetPwd = False,
    #                      Password = [], SkipCMD13 = False):

    #     if type(Password) == str:
    #         Password = list(Password)

    #     lockCardDSbyte0 = sdcmdWrap.LOCK_CARD_DATA_STRUCTURE_BYTE0()
    #     lockCardDSbyte0.uiSet_Pwd = SetPwd
    #     lockCardDSbyte0.uiClr_Pwd = ClrPwd
    #     lockCardDSbyte0.uiLock_Unlock = LockUnLock
    #     lockCardDSbyte0.uiErase = Erase
    #     lockCardDSbyte0.uiCop = cop

    #     LockCardDataStruct = sdcmdWrap.LOCK_CARD_DATA_STRUCTURE()
    #     LockCardDataStruct.lockCardDataStructureByte0 = lockCardDSbyte0
    #     LockCardDataStruct.uiPWDS_LEN = len(Password)
    #     LockCardDataStruct.uiPasswordData = Password

    #     CMD42_LockUnlock = self.Cmd42(LockCardDataStructure = LockCardDataStruct, SkipCMD13 = SkipCMD13)

    #     return CMD42_LockUnlock


    def FillBufferWithTag(self, DataBuffer, startLba = 0, NumBlocks = 1, Pattern = sdcmdWrap.Pattern.ALL_ZERO,
                          LbaTag = False, SeqTag = False, SeqNumber = 0, DataFillValue = None):
        """
        Function to fill buffer with pattern:
            0: 'ALL_ZERO', 1: 'WORD_REPEATED', 2: 'INCREMENTAL', 3: RANDOM BUFFER, 4: 'CONST', 5: 'ALL_ONE', 6: 'ANY_WORD',
            7: 'WORD_BLOCK_NUMBER' ,8: 'NEG_INCREMENTAL', 9: 'NEG_CONST'
        Note: Argument DataFillValue should be given when argument Pattern is "USER_BUFFER" or 10.
        """

        if Pattern == sdcmdWrap.Pattern.ALL_ZERO:
            DataBuffer.Fill(value = 0x0)
            # DataBuffer.Fill(value = ServiceWrap.ALL_0)

        elif Pattern == sdcmdWrap.Pattern.WORD_REPEATED:
            for blkNo in range(0, NumBlocks):
                value = 0
                for i in range(0, 512, 2):
                    DataBuffer.SetTwoBytes((blkNo * 512) + i, (value & 0xFFFF), little_endian = False)
                    value += 1

        elif Pattern == sdcmdWrap.Pattern.INCREMENTAL:
            LBA = (startLba & 0xFF) + 1
            for blkNo in range(0, NumBlocks):
                for i in range(0, 512):
                    value = (LBA + i) & 0xFF
                    DataBuffer.SetByte((blkNo * 512) + i, value)
                LBA += 1

        elif Pattern == sdcmdWrap.Pattern.ANY_BUFFER:
            DataBuffer.FillRandom()

        elif Pattern == sdcmdWrap.Pattern.CONST:
            LBA = (startLba & 0xFF) + 1
            for blkNo in range(0, NumBlocks):
                for i in range(0, 512):
                    value = LBA & 0xFF
                    DataBuffer.SetByte((blkNo * 512) + i, value)
                LBA += 1

        elif Pattern == sdcmdWrap.Pattern.ALL_ONE:
            DataBuffer.Fill(value = 0xFF)
            # DataBuffer.Fill(value = ServiceWrap.ALL_1)    # TOBEDONE: ServiceWrap.ALL_1 has bug that it fills 0x01 instead of 0xff

        elif Pattern == sdcmdWrap.Pattern.ANY_WORD:
            for blkNo in range(0, NumBlocks):
                for byteOffset in range(0, 512, 2):
                    DataBuffer.SetTwoBytes((blkNo * 512) + byteOffset, self._anyWord, little_endian = False)

        elif Pattern == sdcmdWrap.Pattern.WORD_BLOCK_NUMBER:
            value = 0x1
            for blkNo in range(0, NumBlocks):
                for i in range(0, 512, 2):
                    DataBuffer.SetTwoBytes((blkNo * 512) + i, (value & 0xFFFF), little_endian = False)
                value += 1

        elif Pattern == sdcmdWrap.Pattern.PATTERN_NEG_INCREMENTAL:
            LBA = (startLba & 0xFF) + 1
            for blkNo in range(0, NumBlocks):
                for i in range(0, 512):
                    value = 0xFF - ((LBA + i) & 0xFF)
                    DataBuffer.SetByte((blkNo * 512) + i, value)
                LBA += 1

        elif Pattern == sdcmdWrap.Pattern.PATTERN_NEG_CONST:
            LBA = (startLba & 0xFF) + 1
            for blkNo in range(0, NumBlocks):
                for i in range(0, 512):
                    value = 0xFF - (LBA & 0xFF)
                    DataBuffer.SetByte((blkNo * 512) + i, value)
                LBA += 1

        elif (Pattern == "USER_BUFFER") or (Pattern == 10):
            if DataFillValue == None:
                raise ValidationError.TestFailError(self.fn, "'UserBuffer' is not given")
            DataBuffer.Fill(pattern_string = hex(DataFillValue)[2:])

        if SeqTag == True:
            SeqNum = SeqNumber & 0xFF
            SeqNum_OnesComplement = (~SeqNum) & 0xFFFFFFFF
            for blkNo in range(0, NumBlocks):
                # Tagging SeqNumber in next 4 bytes of the block
                DataBuffer.SetFourBytes((blkNo * 512) + 8, SeqNum, little_endian = False)
                # Tagging Ones complement of SeqNumber in the next 4 bytes
                DataBuffer.SetFourBytes((blkNo * 512) + 12, SeqNum_OnesComplement, little_endian = False)

                # Tagging SeqNumber in the previous 4 bytes of the block
                DataBuffer.SetFourBytes((blkNo * 512) + (512 - 12), SeqNum, little_endian = False)
                # Tagging Ones complement of the SeqNumber in the previous 4 bytes of the block
                DataBuffer.SetFourBytes((blkNo * 512) + (512 - 16), SeqNum_OnesComplement, little_endian = False)

        if LbaTag == True:
            LBA = startLba

            for blkNo in range(0, NumBlocks):
                LBA_OnesComplement = (~LBA) & 0xFFFFFFFF
                # Tagging LBA in first 4 bytes of the block
                DataBuffer.SetFourBytes(blkNo * 512, LBA, little_endian = False)
                # Tagging Ones complement of LBA in the next 4 bytes
                DataBuffer.SetFourBytes((blkNo * 512) + 4, LBA_OnesComplement, little_endian = False)

                # Tagging LBA in the last 4 bytes of the block
                DataBuffer.SetFourBytes((blkNo * 512) + (512 - 4), LBA, little_endian = False)
                # Tagging Ones complement of the LBA in the previous 4 bytes of the block
                DataBuffer.SetFourBytes((blkNo * 512) + (512 - 8), LBA_OnesComplement, little_endian = False)

                LBA += 1


    def PrepareCardMap(self, startLba, endLba):
        """
        Function to create a CardMap with sequence number from the startLba provided for NumBlocks
        """

        if endLba >= self.__cardMaxLba:
            raise ValidationError.TestFailError(self.fn, "Provided startLba and endLba range exceeds card capacity. Unable to create CardMap")

        self._CardMap_StartLBA = startLba
        self._CardMap_EndLBA = endLba

        for i in range(0, self._CardMap_BlockCount):
            self._CardMap.append(0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Created CardMap for %d Blocks for LBA Range - [0x%X to 0x%X]\n\n"
                     % (self._CardMap_BlockCount, startLba, endLba))


    def GetSequenceNum(self, startLba, endLba):
        """
        Function to get the sequence number for the provided LBA and
        the number of blocks that have the same sequence number adjacent to the provided LBA
        """

        # Check LBA is with in Card map range
        if (startLba < self._CardMap_StartLBA) or (endLba > self._CardMap_EndLBA) or (startLba > endLba):
            raise ValidationError.TestFailError(self.fn, "Provided startLba and endLba is not in the valid card map range. CardMap LBA Range - [0x%X - 0x%X]"
                                                % (self._CardMap_StartLBA, self._CardMap_EndLBA))

        blockOffset = startLba - self._CardMap_StartLBA
        seqNumber = self._CardMap[blockOffset]
        blkcount = 0
        for i in range(blockOffset, self._CardMap_BlockCount):
            if self._CardMap[i] == seqNumber:
                blkcount += 1   # blkcount with same sequence number
            else:
                break

        return seqNumber, blkcount


    def UpdateSequenceNum(self, startLba, NumBlocks):
        """
        Function to update the Sequence number for the startLba and NumBlocks provided
        """

        # check LBA is with in Card map range
        endLba = self.calculate_endLba(startLba, NumBlocks)
        if (startLba < self._CardMap_StartLBA) or (endLba > self._CardMap_EndLBA) or (startLba > endLba):
            raise ValidationError.TestFailError(self.fn, "Provided startLba and endLba is not in the valid card map range. CardMap LBA Range - [0x%X - 0x%X]"
                                                % (self._CardMap_StartLBA, self._CardMap_EndLBA))

        blockOffset = startLba - self._CardMap_StartLBA
        seqNumber = self._CardMap[blockOffset]

        seqNumber += 1
        seqNumber = seqNumber & 0xFF

        for i in range(blockOffset, (blockOffset + NumBlocks)):
            self._CardMap[i] = seqNumber

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "********* CardMap *************\n%s" % self._CardMap)

        return seqNumber

    def StartDebugHostLog(self, Method = None):
        Method = sdcmdWrap.DEBUG_METHOD.PROTOCOL_DEBUG if Method == None else Method
        sdcmdWrap.SDRSetDebugMethod(Method)

    def DumpHostLog(self, szPathToFile = None):
        Path = self.currCfg.system.TestsDir + "\\HostLog.txt"
        szPathToFile = Path if szPathToFile == None else szPathToFile
        sdcmdWrap.GetHostDebugInformation(szPathToFile)

    def CheckDeviceBusyStatus(self, Command):
        timeout = 5         # 5sec
        sleepTime = 0.250   # 250 ms
        count = int(old_div(timeout, sleepTime))

        while count > 0:
            busyStatusObj = sdcmdWrap.GetDeviceBusyStatus()
            busyStatus = busyStatusObj.GetBusyStatus()
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_BUSY_STATUS_BY_HOST(busyStatus))
            if (busyStatus == self.__errorCodes.CheckError('CARD_TIME_OUT_RCVD')):  # If busy timed out
                raise ValidationError.TestFailError(self.fn, self.STD_LOG_BUSY_TIMEOUT_OCCURED(Command))

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_CHECK_IF_CARD_IN_TRANS_STATE)
            resp = self.GetCardStatus()
            if('CURRENT_STATE:CQ Tran' in resp):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_CARD_OUT_OF_BUSY_STATE)
                break # breaking while since card is now out of busy state

            time.sleep(sleepTime)
            count -= 1
        if (count == 0) and ('CURRENT_STATE:CQ Tran' not in resp):
            self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_CARD_NOT_MOVED_TO_TRANS_STATE)
            raise ValidationError.TestFailError(self.fn, self.GL_CARD_NOT_MOVED_TO_TRANS_STATE)

    def RegisterContinueOnException(self, CMD_ID, ErrorCode, ErrorGroup = 0xFF3A):
        """
        Description: For below enum IDs refer CVF API document.
                    CMD_ID - serviceWrap.E_COMMAND_TYPE_ID.........
                    ErrorCode - sdcmdWrap.CARD_STATUS..........
        """
        self.__ErrorManager.RegisterContinueOnException(cmdID = CMD_ID, errorCode = ErrorCode, errorGrp = ErrorGroup)

    def DeRegisterContinueOnException(self, CMD_ID, ErrorCode, ErrorGroup = 0xFF3A):
        """
        Description: For below enum IDs refer CVF API document.
                    CMD_ID - serviceWrap.E_COMMAND_TYPE_ID.........
                    ErrorCode - sdcmdWrap.CARD_STATUS..........
        """
        self.__ErrorManager.DeRegisterContinueOnException(enCmdType = CMD_ID, errorCode = ErrorCode, errorGrp = ErrorGroup)
###----------------------------- General API End -----------------------------###


###----------------------------- SPI Starts -----------------------------###
    def ACmd41_SPI(self, arg):
        """
        ACmd41 - SD_SEND_OP_COND
        """
        self.FUNCTION_ENTRY("ACmd41_SPI")
        self.__responseDataBuf.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 41,
                                                           argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.DecodeR1Response(self.__responseDataBuf)
        self.FUNCTION_EXIT("ACmd41_SPI")
        return self.__responseDataBuf

    def Cmd58_SPI(self, arg = 0x00):
        """
        CMD58 - Read_OCR
        """
        self.FUNCTION_ENTRY("Cmd58_SPI")
        self.__responseDataBuf.Fill(value = 0x0)

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 58,
                                                           argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R3,
                                                           responseData = self.__responseDataBuf)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.__decodedSPIR3response = self.DecodeSPIR3Response(self.__responseDataBuf)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R3 type response: 0x%X" % self.__responseDataBuf.GetFourBytesToInt(offset = 0, little_endian = False))
        self.FUNCTION_EXIT("Cmd58_SPI")
        return self.__responseDataBuf

    def Cmd59_SPI(self, CRCOption):
        """
        CMD59 - CRC_ON_OFF
        """
        self.FUNCTION_ENTRY("Cmd59_SPI")
        self.__responseDataBuf.Fill(value = 0x0)
        arg = 0x1 if CRCOption == True else 0x0

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 59,
                                                           argument = arg,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
            retValue = self.__responseDataBuf.GetData(0, 2)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())

        self.__decodedR1response = self.DecodeR1Response(self.__responseDataBuf)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Passed with R1 type response: %s" % self.__decodedR1response)
        self.FUNCTION_EXIT("Cmd59_SPI")
        return self.__decodedR1response


    def DecodeSPIR1Response(self, resBuffer):
        retValue = []

        CmdIndex = resBuffer.GetOneByteToInt(0)
        retValue.append(CmdIndex)

        errValue1 = resBuffer.GetOneByteToInt(1)
        if (errValue1 & 0x40):
            retValue.append ("PARAMETER_ERROR")
        if (errValue1 & 0x20):
            retValue.append ("ADDRESS_ERROR")
        if (errValue1 & 0x10):
            retValue.append ("ERASE_SEQUENCE_ERROR")
        if (errValue1 & 0x08):
            retValue.append ("COM_CRC_ERROR")
        if (errValue1 & 0x04):
            retValue.append ("ILLEGAL_COMMAND")
        if (errValue1 & 0x02):
            retValue.append ("ERASE_RESET")
        if (errValue1 & 0x01):
            retValue.append("CURRENT_STATE:Idle")
        else:
            retValue.append("CURRENT_STATE:Tran")
            retValue.append("READY_FOR_DATA")

        return retValue

    def DecodeSPIR2Response(self, resBuffer):
        retValue = []
        CmdIndex = '13'
        retValue.append(CmdIndex)

        errValue = resBuffer.GetOneByteToInt(offset = 0)
        if (errValue & 0x40):
            retValue.append("PARAMETER_ERROR")
        if (errValue & 0x20):
            retValue.append("ADDRESS_ERROR")
        if (errValue & 0x10):
            retValue.append("ERASE_SEQ_ERROR")
        if (errValue & 0x08):
            retValue.append("COM_CRC_ERROR")
        if (errValue & 0x04):
            retValue.append("ILLEGAL_COMMAND")
        if (errValue & 0x02):
            retValue.append("ERASE_RESET")
        if (errValue & 0x01):
            retValue.append("CURRENT_STATE:Idle")
        else:
            retValue.append("CURRENT_STATE:Tran")
            retValue.append("READY_FOR_DATA")

        errValue = resBuffer.GetOneByteToInt(offset = 1)
        if (errValue & 0x80):
            retValue.append("OUT_OF_RANGE or CSD_OVERWRITE")
        if (errValue & 0x40):
            retValue.append("ERASE_PARAM")
        if (errValue & 0x20):
            retValue.append("WP_VIOLATION")
        if (errValue & 0x10):
            retValue.append("CARD_ECC_FAILED")
        if (errValue & 0x08):
            retValue.append("CC_ERROR")
        if (errValue & 0x04):
            retValue.append("ERROR")
        if (errValue & 0x02):
            retValue.append("WP_ERASE_SKIP or LOCK_UNLOCK_FAILED")
        if (errValue & 0x01):
            retValue.append("CARD_IS_LOCKED")

        return retValue

    #def DecodeSPIR2Response(self, resBuffer):
        #retValue = []
        #CmdIndex = '13'
        #retValue.append(CmdIndex)

        #errValue1 = resBuffer.GetOneByteToInt(offset = 1)
        #if (errValue1 & 0x01):
            #retValue.append("CARD_IS_LOCKED")
        #if (errValue1 & 0x02):
            #retValue.append("WP_ERASE_SKIP or LOCK_UNLOCK_FAILED")
        #if (errValue1 & 0x04):
            #retValue.append("ILLEGAL_COMMAND")
        #if (errValue1 & 0x20):
            #retValue.append("WP_VIOLATION")
        #if (errValue1 & 0x40):
            #retValue.append("ERASE_PARAM")
        #if (errValue1 & 0x80):
            #retValue.append("OUT_OF_RANGE")

        #errValue = resBuffer.GetOneByteToInt(offset = 0)
        #if ((errValue << 7) == 0):
            #retValue.append("CURRENT_STATE:Tran")
            #retValue.append("READY_FOR_DATA")
        #elif ((errValue << 7) == 1):
            #retValue.append("CURRENT_STATE:Idle")
            #retValue.append("READY_FOR_DATA")

        #return retValue

    def DecodeSPIR3Response(self, resBuffer):
        """
        DecodeSPIR3Response: It decodes the R3 response in SPI mode. This R3 response came from command
        R3 Response: [0-39]bit, which is R1[32-39] and OCR[0-31]
        """
        retValue = {}

        R1Response = []
        errValue1 = resBuffer.GetOneByteToInt(0)    # This handles R1 part of R7 response
        if (errValue1 & 0x40):
            R1Response.append("PARAMETER_ERROR")
        if (errValue1 & 0x20):
            R1Response.append("ADDRESS_ERROR")
        if (errValue1 & 0x10):
            R1Response.append("ERASE_SEQUENCE_ERROR")
        if (errValue1 & 0x08):
            R1Response.append("COM_CRC_ERROR")
        if (errValue1 & 0x04):
            R1Response.append("ILLEGAL_COMMAND")
        if (errValue1 & 0x02):
            R1Response.append("ERASE_RESET")
        if (errValue1 & 0x01):
            R1Response.append("IDLE_STATE")
        retValue["R1Response"] = R1Response

        retValue["OCR"] = resBuffer.GetFourBytesToInt(0x1, little_endian=False)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Decoded R3 response in SPI mode: R1-%s, OCR-0x%X" % (retValue["R1Response"], retValue["OCR"]))
        return retValue

    def DecodeSPIR7Response(self, resBuffer):
        """
        DecodeSPIR7Response: It decodes the R7 response in SPI mode.
        R7 Response: [0-39]bit, which is R1[39-32], command version [31-28], reserved [27-12], voltage accepted [11-8], Check pattern [7-0]
        """
        retValue = {}

        R1Response = []
        errValue1 = resBuffer.GetOneByteToInt(0)    # This handles R1 part of R7 response
        if (errValue1 & 0x40):
            R1Response.append("PARAMETER_ERROR")
        if (errValue1 & 0x20):
            R1Response.append("ADDRESS_ERROR")
        if (errValue1 & 0x10):
            R1Response.append("ERASE_SEQUENCE_ERROR")
        if (errValue1 & 0x08):
            R1Response.append("COM_CRC_ERROR")
        if (errValue1 & 0x04):
            R1Response.append("ILLEGAL_COMMAND")
        if (errValue1 & 0x02):
            R1Response.append("ERASE_RESET")
        if (errValue1 & 0x01):
            R1Response.append("IDLE_STATE")
        retValue["R1Response"] = R1Response

        retValue["CMD_Version"] = resBuffer.GetOneByteToInt(1) >> 4
        retValue["VHS"] = resBuffer.GetOneByteToInt(3) & 0xF
        retValue["Check_Pattern"] = resBuffer.GetOneByteToInt(4)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Decoded R7 response in SPI mode: %s" % retValue)
        return retValue

###----------------------------- SPI Ends -----------------------------###

###----------------------------- Reserved Commands Starts -----------------------------###

    def ACmd31(self, startLbaAddress, transferLen, writeDataBuffer):
        """
        ACmd31
        """
        self.FUNCTION_ENTRY("ACmd31")
        self.__responseDataBuf.Fill(value = 0x0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Start LBA: 0x%X, block Count: 0x%X" % (startLbaAddress, transferLen))

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 31,
                                                           argument = startLbaAddress,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_MULTWRITE)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = transferLen
        commandDataDefinitionObj.uiBlockLen = 512
        commandDataDefinitionObj.ptrBuffer = writeDataBuffer
        commandDefinitionObj.flags.DoSendStatus = True

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DecodedR1Response = %s" % self.DecodeR1Response(self.__responseDataBuf))
        self.FUNCTION_EXIT("ACmd31")


    def ACmd33(self, startLbaAddress, transferLen, writeDataBuffer):
        """
        ACmd33
        """
        self.FUNCTION_ENTRY("ACmd33")
        self.__responseDataBuf.Fill(value = 0x0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Start LBA: 0x%X, block Count: 0x%X" % (startLbaAddress, transferLen))

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 33,
                                                           argument = startLbaAddress,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_MULTWRITE)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = transferLen
        commandDataDefinitionObj.uiBlockLen = 512
        commandDataDefinitionObj.ptrBuffer = writeDataBuffer
        commandDefinitionObj.flags.DoSendStatus = True

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DecodedR1Response = %s" % self.DecodeR1Response(self.__responseDataBuf))
        self.FUNCTION_EXIT("ACmd33")


    def ACmd53(self, startLbaAddress, transferLen, readDataBuffer):
        """
        ACmd53 - Read_Multiple_Block
        """
        self.FUNCTION_ENTRY("ACmd53")
        self.__responseDataBuf.Fill(value = 0x0)
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "Start LBA: 0x%X, block Count: 0x%X" % (startLbaAddress, transferLen))

        commandDefinitionObj = sdcmdWrap.CommandDefinition(cmd = 53,
                                                           argument = startLbaAddress,
                                                           responseType = sdcmdWrap.TYPE_RESP._R1,
                                                           responseData = self.__responseDataBuf,
                                                           dataMode = sdcmdWrap.DATA_TRANS_.DATA_MULTREAD)
        commandDataDefinitionObj = sdcmdWrap.CommandDataDefinition()
        commandDataDefinitionObj.dwBlockCount = transferLen
        commandDataDefinitionObj.uiBlockLen = 512
        commandDataDefinitionObj.ptrBuffer = readDataBuffer
        #commandDataDefinitionObj.dataPattern = Pattern
        #commandDataDefinitionObj.compareData = DoCompare
        commandDefinitionObj.flags.DoSendStatus = True

        try:
            sdcmdWrap.SendBasicCommand(commandDefinitionObj, commandDataDefinitionObj)
        except ValidationError.CVFExceptionTypes as exc:
            exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
            self.ErrorPrint(exc)
            raise ValidationError.CVFGenericExceptions(self.fn, exc.GetFailureDescription())
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "DecodedR1Response = %s" % self.DecodeR1Response(self.__responseDataBuf))
        self.FUNCTION_EXIT("ACmd53")

###----------------------------- Reserved Commands Ends -----------------------------###

