"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : None
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : None
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : GlobalConstants.py
# DESCRIPTION                    : This is the utility file having global constants. Refer SD spec part-I version 7.0.
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Arockiaraj JAI
# REVIEWED BY                    :
# DATE                           : Sep-2022
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
    from builtins import *
    from builtins import object

# GlobalConstants Class - Begins
class GlobalConstants(object):

    ############### Skip write/read Start ###############
    # Flip the below variables to True for run the testcase without executing card write/read (CMD25/CMD24/CMD18/CMD17) commands.
    SKIP_WRITE = False
    SKIP_READ = False
    ############### Skip write/read End ###############

    # Python returns -1 when string is not found
    NOT_FOUND = -1

    # Erase functions
    # SDDVT Defined pattern values
    PATTERN_ALL_ZERO=0
    PATTERN_WORD_REPEATED=1
    PATTERN_INCREMENTAL=2
    PATTERN_ANY_BUFFER=3    # RANDOM
    PATTERN_CONST=4
    PATTERN_ALL_ONE=5
    PATTERN_ANY_WORD=6
    PATTERN_WORD_BLOCK_NUMBER=7
    PATTERN_NEG_INCREMENTAL=8
    PATTERN_NEG_CONST=9
    PATTERN_USER_DATA=10

    # Capacity
    ONE_TB = 1024

    # TimeOut values
    R1bTIMEOUT_VALUE_FOR_CMD43 = 250

    # MAXIMUM BLOCK FOR SECURE WRITE AND READ
    MAX_BLOCK_FOR_SECURE_OP = 0x80

    MAX_TRANSFER_LENGTH = 0x100
    MKB_FILEnumO = 0        # Intitial MKB file number
    MKB_FILEnum16 = 16      # Total number of MKB file
    MAX_MKB_FILES = 16      # No. of Media Key Block files as per Secure Spec 3.0
    SRW_CARD_SLOT = 1       # Card Slot
    CQ_MAX_QUEUE_DEPTH = 32
    CARD_IS_BUSY = 5

    #Global Disctionary
    patternSupportedInCQ = {0:'ALL_ZERO', 1:'WORD_REPEATED', 2:'INCREMENTAL', 4:'CONST', 5:'ALL_ONE', 6:'ANY_WORD',
                            7:'WORD_BLOCK_NUMBER', 8:'PATTERN_NEG_INCREMENTAL', 9:'PATTERN_NEG_CONST'} # 3:ANY_BUFFER not supported in CQ mode

    patternsForDataIntegrity =  {2:'INCREMENTAL', 7:'WORD_BLOCK_NUMBER', 8:'PATTERN_NEG_INCREMENTAL'} # 3:ANY_BUFFER not supported in CQ mode


    #Global Strings
    ERROR_NOT_EXPECTED = "ERROR_NOT_EXPECTED"
    CARD_OUT_OF_RANGE="CARD_OUT_OF_RANGE"

# GlobalConstants Class - Ends

class PowerSupply(object):
    VDDF = True     # Flash
    VDDH = False    # Host

class Erase(object):
    Erase = 0
    Discard = 1
    FULE = 2    # Fule User Area Logical Erase

class CMD6(object):
    # SWITCH COMMAND(CMD6)
    SWITCH = True
    CHECK = False
    CONSUMPTION_NONE = 0
    CONSUMPTION_NOT_ERROR = 1
    CONSUMPTION_MATCH_TO_VALUE = 2
    CONSUMPTION_ERROR = 3

class HostRegisterMode(object):
    # Below enum values are used in sdcmdWrap.SetSpecialModes API
    BROAD_CAST = 0
    BUSY = 1
    WIDE_BUS = 2
    TURN_CRC = 3    # Only for SPI
    NOB_EN = 4
    INIT = 5
    CREATE_CRC_ERROR = 6
    LAST_PERF_BUF = 7

class General_Info_Offsets(object):
    REVISION = 0
    GENERAL_INFORMATION_LENGTH = 2
    NUMBER_of_EXTENSIONS = 4
    EXTENSION_1_Start_Offset = 16
    # Below offsets are from the offset of corresponding function
    SFC = 0
    FCC = 2
    FMC = 4
    FMN = 6
    PFC = 22
    FN = 24
    POINTER_to_NEXT_EXTENSION = 40
    NUMBER_of_REGISTER_SETS = 42


class Power_Manage_Func_Offsets(object):
    # Refer Table 5-28 and Figures 5-16, 5-17, 5-18 : In SD spec part-I
    REVISION_Byte_Offset = 0
    REVISION_Bit_Offset = 15    # In binary 00001111

    STATUS_REGISTER_Byte_Offset = 1
    POFR_Bit_Offset = 1         # In binary 00000001
    PSUR_Bit_Offset = 2         # In binary 00000010
    PDMR_Bit_Offset = 4         # In binary 00000100
    POFS_Bit_Offset = 16        # In binary 00010000
    PSUS_Bit_Offset = 32        # In binary 00100000
    PDMS_Bit_Offset = 64        # In binary 01000000

    SETTINGS_REGISTER_Byte_Offset = 2
    POFN_Bit_Offset = 1         # In binary 00000001
    PSUN_Bit_Offset = 2         # In binary 00000010
    PDMN_Bit_Offset = 4         # In binary 00000100


class Perf_Enhan_Func_Offsets(object):
    # Refer Table 5-30 : Performance Enhancement Register Set in SD spec part-I
    REVISION = 0
    FX_EVENT_SUPPORT_Byte_Offset = 1
    FX_EVENT_SUPPORT_Bit_Offset = 1
    CARD_INIT_MAINTEN_SUPPORT_Byte_Offset = 2
    CARD_INIT_MAINTEN_SUPPORT_Bit_Offset = 1
    HOST_INIT_MAINTEN_SUPPORT_Byte_Offset = 2
    HOST_INIT_MAINTEN_SUPPORT_Bit_Offset = 2
    CARD_MAINTEN_URGENCY_Byte_Offset = 3
    CARD_MAINTEN_URGENCY_Bit_Offset = 3
    CACHE_SUPPORT_Byte_Offset = 4
    CACHE_SUPPORT_Bit_Offset = 1
    CQ_SUPPORT_AND_DEPTH = 6
    TASK_ERROR_STATUS = 8
    FX_EVENT_ENABLE_Byte_Offset = 257
    FX_EVENT_ENABLE_Bit_Offset = 1
    CARD_INIT_MAINTEN_ENABLE_Byte_Offset = 258
    CARD_INIT_MAINTEN_ENABLE_Bit_Offset = 1
    HOST_INIT_MAINTEN_ENABLE_Byte_Offset = 258
    HOST_INIT_MAINTEN_ENABLE_Bit_Offset = 2
    START_HOST_INIT_MAINTEN_Byte_Offset = 259
    START_HOST_INIT_MAINTEN_Bit_Offset = 1
    CACHE_ENABLE_Byte_Offset = 260
    CACHE_ENABLE_Bit_Offset = 1
    FLUSH_CACHE_Byte_Offset = 261
    FLUSH_CACHE_Bit_Offset = 1
    ENABLE_CQ_Byte_Offset = 262
    ENABLE_CQ_Bit_Offset = 1
    CQ_MODE_Byte_Offset = 262
    CQ_MODE_Bit_Offset = 2


class Card_Status_Fields(object):
    OUT_OF_RANGE = "OUT_OF_RANGE"
    ADDRESS_ERROR = "ADDRESS_ERROR"
    BLOCK_LEN_ERROR = "BLOCK_LEN_ERROR"
    ERASE_SEQ_ERROR = "ERASE_SEQ_ERROR"
    ERASE_PARAM = "ERASE_PARAM"
    WP_VIOLATION = "WP_VIOLATION"
    CARD_IS_LOCKED = "CARD_IS_LOCKED"
    LOCK_UNLOCK_FAILED = "LOCK_UNLOCK_FAILED"
    COM_CRC_ERROR = "COM_CRC_ERROR"
    ILLEGAL_COMMAND = "ILLEGAL_COMMAND"
    CARD_ECC_FAILED = "CARD_ECC_FAILED"
    CC_ERROR = "CC_ERROR"
    ERROR = "ERROR"
    Reserved = "Reserved"
    DEFERRED_RESPONSE = "DEFERRED_RESPONSE"
    CSD_OVERWRITE = "CSD_OVERWRITE"
    WP_ERASE_SKIP = "WP_ERASE_SKIP"
    CARD_ECC_DISABLED = "CARD_ECC_DISABLED"
    ERASE_RESET = "ERASE_RESET"
    CURRENT_STATE_Reserved = "CURRENT_STATE:Reserved"
    CURRENT_STATE_CQ_Tran = "CURRENT_STATE:CQ Tran"
    CURRENT_STATE_Rdt = "CURRENT_STATE:Rdt"
    CURRENT_STATE_Wdt = "CURRENT_STATE:Wdt"
    CURRENT_STATE_Bsy = "CURRENT_STATE:Bsy"
    CURRENT_STATE_Idle = "CURRENT_STATE:Idle"
    CURRENT_STATE_Ready = "CURRENT_STATE:Ready"
    CURRENT_STATE_Ident = "CURRENT_STATE:Ident"
    CURRENT_STATE_Stby = "CURRENT_STATE:Stby"
    CURRENT_STATE_Tran = "CURRENT_STATE:Tran"
    CURRENT_STATE_Data = "CURRENT_STATE:Data"
    CURRENT_STATE_Rcv = "CURRENT_STATE:Rcv"
    CURRENT_STATE_Prg = "CURRENT_STATE:Prg"
    CURRENT_STATE_Dis = "CURRENT_STATE:Dis"
    CURRENT_STATE_Reserved_for_IO_mode = "CURRENT_STATE:Reserved for IO mode"
    READY_FOR_DATA = "READY_FOR_DATA"
    FIX_EVENT = "FIX_EVENT"
    APP_CMD = "APP_CMD"
    Reserved_For_SD_IO_Card = "Reserved_For_SD_IO_Card"
    AKE_SEQ_ERROR = "AKE_SEQ_ERROR"
    Reserved_For_APP_CMD = "Reserved_For_APP_CMD"
    Reserved_For_Manufacturer_Test_Mode = "Reserved_For_Manufacturer_Test_Mode"


class SD_Status_Fields(object):
    pass


class CSD(object):
    NotUsed = "NotUsed"
    CRC = "CRC"
    FILE_FORMAT = "FILE_FORMAT"
    TMP_WRITE_PROTECT = "TMP_WRITE_PROTECT"
    PERM_WRITE_PROTECT = "PERM_WRITE_PROTECT"
    COPY = "COPY"
    FILE_FORMAT_GRP = "FILE_FORMAT_GRP"
    WRITE_BL_PARTIAL = "WRITE_BL_PARTIAL"
    WRITE_BL_LEN = "WRITE_BL_LEN"
    R2W_FACTOR = "R2W_FACTOR"
    WP_GRP_ENABLE = "WP_GRP_ENABLE"
    WP_GRP_SIZE = "WP_GRP_SIZE"
    SECTOR_SIZE = "SECTOR_SIZE"
    ERASE_BLK_EN = "ERASE_BLK_EN"
    C_SIZE = "C_SIZE"
    DSR_IMP = "DSR_IMP"
    READ_BLK_MISALIGN = "READ_BLK_MISALIGN"
    WRITE_BLK_MISALIGN = "WRITE_BLK_MISALIGN"
    READ_BL_PARTIAL = "READ_BL_PARTIAL"
    READ_BL_LEN = "READ_BL_LEN"
    CCC = "CCC"
    TRAN_SPEED = "TRAN_SPEED"
    TRAN_SPEED_SDR12 = "0x32"
    TRAN_SPEED_SDR25 = "0x5a"
    TRAN_SPEED_SDR50_DDR50 = "0xb"
    TRAN_SPEED_SDR104 = "0x2b"
    NSAC = "NSAC"
    TAAC = "TAAC"
    CSD_STRUCTURE = "CSD_STRUCTURE"
    Reserv1 = "Reserv1"
    Reserv2 = "Reserv2"
    Reserv3 = "Reserv3"
    Reserv4 = "Reserv4"
    Reserv5 = "Reserv5"
    Reserv6 = "Reserv6"


class CID(object):
    MID = "MID"     # Manufacturer ID
    OID = "OID"     # OEM/Application ID
    PNM = "PNM"     # Product Name
    PRV = "PRV"     # Product Revision
    PSN = "PSN"     # Product Serial Number
    Reserved = "Reserved"
    MDT = "MDT"     # Manufacturing Date
    CRC = "CRC"     # Cyclic Redundancy Code


class SCTPCOMMAND(object):
    CDBLENGTH_16 = 16
    IDENTIFYDRIVE = 0xEC
    WRITEPORT = 0x8C
    READPORT = 0x8D
    READFILESYSTEM = 0x8A
    WRITEFILESYSTEM = 0x8B
    MEDIALAYOUT = 0xBB
    FORMAT = 0x8F
    FORMATSTATUS = 0x70


class ErrorCodes(object):
    CARD_NO_ERROR = 0
    CARD_IS_NOT_RESPONDING = 1
    CARD_CMD_CRC_ERROR = 2
    CARD_ILLEGAL_CRC_STATUS = 3
    CARD_DATA_STATUS_CRC_ERROR = 4
    CARD_IS_BUSY = 5
    CARD_IS_NOT_READY = 6
    CARD_READ_CRC_ERROR = 7
    CARD_ILLEGAL_CMD = 8
    CARD_ERASE_PARAM = 9
    CARD_WP_VIOLATION = 10
    CARD_ERROR = 11
    CARD_WP_ERASE_SKIP = 12
    CARD_ADDRESS_ERROR = 13
    CARD_ECC_FAILED = 14
    CARD_IS_LOCKED = 15
    CARD_WRONG_MODE = 16
    CARD_CMD_PARAM_ERROR = 17
    CARD_ERASE_SEQ_ERROR = 18
    CARD_ERASE_RESET = 19
    CARD_NO_CRC_WR_RESP = 20
    CARD_OVERRUN = 21
    CARD_UNDERRUN = 22
    CARD_CIDCSD_OVERWRITE = 23
    CARD_ECC_DISABLED = 24
    WATCHDOG_TIME_OUT_FIFO_EMP = 25
    CARD_BLK_LEN_ERROR = 26
    CARD_TIME_OUT_RCVD = 27
    WATCHDOG_TIME_OUT_FIFO_FULL = 28
    CARD_LOCK_UNLOCK_FAILED = 29
    CARD_NOT_IN_TEST_MODE = 30
    CARD_OUT_OF_RANGE = 31
    CARD_CC_ERROR = 32
    CARD_INTERFACE_ERROR = 33
    CARD_FREQ_ERROR = 34
    MMC_LAST_WRITE_MISMATCH = 35
    MMC_NOT_SUPPORT_BURST = 36
    WATCHDOG_TIME_OUT_END_RESP = 37
    MMC_ERR_NEXT_DATA = 38
    CARD_COMPARE_ERROR = 39
    SD_VERIFICATION_FAILED = 40
    SD_ATHENTICATION_FAILED = 41
    SD_FAILED_ACMD_ENABLE = 42
    SD_FAILED_GET_R2 = 43
    CARD_FAILED_CARD_SELECTION = 44
    SD_FAILED_SECURE_READ_CMD = 45
    SD_FAILED_SECURE_WRITE_CMD = 46
    VERIFY_MEDIA_KEY_FAILED = 47
    PROCESS_NEW_MKB_FAILED = 48
    SD_FAILED_TO_OPEN_NEW_MKB_FILE = 49
    ERROR_CARD_DETECTED = 50
    CARD_COM_CRC_ERROR = 51
    CARD_ILLEGAL_MODE = 52
    CARD_TIME_OUT_PRG_DONE = 53
    CARD_SPI_ERROR_TOKEN = 54
    USER_PARAMETER_ERROR = 55
    DRIVER_INTERNAL_ERROR = 56
    BUFFER_ALLOCATION_ERROR = 57
    CARD_END_ERR = 58
    CARD_OVERFLOW_ERR = 59
    CARD_RD_DT_ERR = 60
    WATCHDOG_TIME_OUT_ENHANCED_OPERATION = 61
    CARD_ENHANCED_RES_ERROR = 62
    IDD_MEASURE_HOST_ERROR = 63
    COMPATIBILLITY_ERROR = 64
    CARD_SWITCH_ERROR = 65
    FORCE_STOP_ERROR = 66
    EPP_START_ERROR = 67
    EPP_END_ERROR = 68
    PARAMETER_ERROR = 69
    USD_ADTR_CMDSUCCESS = 70
    USD_ADTR_CMDFAIL = 71
    INVALID_DATALENGTH = 72
    COMMIT_ERROR = 73
    THIRD_COMMAND_ERROR = 74
    SECURE_DATA_IN_ERROR = 75
    PATTERN_DATA_IN_ERROR = 76
    SEND_DATA_BLK_ERROR = 77
    READ_DATA_BLK_ERROR = 78
    UNKNOWN_ERROR = 79
    UIB_TIME_OUT_ERROR = 80
    UNKOWN_OPCODE_ERROR = 81
    UNKOWN_CMD_CODE_ERROR = 82
    EMPTY_STATUS_FIFO = 83
    STATUS_FIFO_OVERFLOW = 84
    UIB_WRITE_TIMEOUT_ERROR = 192
    UIB_READ_TIMEOUT_ERROR = 193
    EPP_TIMEOUT_ERR = 194
    MAIL_BOX_NO_MESSG = 195
    INVALID_PARAM_ERROR = 196
    RS232_RECEIVE_FAIL = 197
    TRGR_IN_PATH_ERROR = 198
    FLASH_INTEGRITY_CHECK = 224
    RECORD_TYPE = 225
    SEGMENT_TYPE = 226
    CHECKSUM_ERROR = 227
    CODE_SIZE_EXCEEDED = 228
    USD_BL_ADRSPACE = 229
    EOF_REACHED = 230
    SCSI_PARAM_ERROR = 231
    CBW_SIGNATURE_ERROR = 232
    NOT_ALL_BLOCKS_WRITTEN = 233
    WATCHDOG_TIMEOUT_PATERN_GEN = 234
    WATCHDOG_TIMEOUT_POWER = 235
    DUT_INTERFACE_ERROR = 236
    HW_MON_3V3 = 237
    HW_MON_VDD_IO = 238
    HW_MON_VDD_SD = 239
    HW_MON_VDD_INAND = 240
    HW_MON_CU_SD = 241
    HW_MON_CU_INAND = 242
    NO_CARD_ERR = 243
    NO_HID = 244
    POWER_ON_OFF_GENERAL_ERR = 245
    CU_TEST_ERROR = 246
    HOST_MAX_READ_TO_CROSSED = 247
    HOST_MAX_WRITE_TO_CROSSED = 248
    HOST_FREQ_ERR = 249
    HOST_FREQ_TIMEOUT = 250
    HOST_IS_NOT_CONNECTED = 251
    TOKEN_TIMEOUT_ERR = 252
    DATA_TIMEOUT_ERR = 253
    TOKEN_ERR = 254
    BOOT_DONE_ERR = 255
    BOOT_USER_PARAM_ERROR = 256
    PG_ST_PROCESS_ERROR = 257
    HW_SET_VOLT_ERROR = 258
    EMMC_SLEEP_STATE_VERIFICATION_ERROR = 259
    ERROR_PAT_GEN_NOT_MATCHING_SDR_FPGA_REV = 260
    ERROR_CARD_PROP_FACTORY_INVALID_STATE = 261
    ERROR_CARD_PROP_FACTORY_INVALID_CARD_MODE = 262
    ERROR_CARD_PROP_FACTORY_UNKNOWN_CSD_STRUCT_VER = 263
    ERROR_CARD_PROP_FACTORY_UNKNOWN_EXT_CSD_VER = 264
    ERROR_CARD_PROP_FACTORY_CARD_MODE_NOT_INITIALIZED = 265
    ERROR_SD_CARD_PROPERTIES_INSTANCE = 266
    ERROR_SD_CMD38_ARGUMENT_IS_NOT_DEFINED = 267
    ERROR_SD_CARD_ERASE_GRP_SIZE_ZERO = 268
    ERROR_SD_CARD_DEOS_NOT_SUPPORT_OPERATION = 269
    PROGRAMMING_BOOTLOADER_FAILED = 270
    MY_HOST_FPGA_DOWNLOAD_FAILED = 271
    NO_XLINX_HOST_CONNECTED = 272
    TOKEN_BUS_MISMATCH_ERROR = 273
    HWRESET_WATCHDOG_TIMEOUT = 274
    USER_SET_MAX_CURRENT_OVER_HOST_LIMIT = 275
    CMD_WENT_HIGH_AFTER_RESPONSE = 276
    DATA_WENT_HIGH_AFTER_RESPONSE = 277
    CMD_AND_DATA_WENT_HIGH_AFTER_RESPONSE = 278
    CMD_WENT_HIGH_DURING_CLOCK_OFF = 279
    DATA_WENT_HIGH_DURING_CLOCK_OFF = 280
    CMD_AND_DATA_WENT_HIGH_DURING_CLOCK_OFF = 281
    DATA_WENT_HIGH_FIRST = 282
    CMD_AND_DATA_DIDNT_GO_HIGH = 283
    DATA_DIDNT_GO_HIGH = 284
    CMD_DIDNT_GO_HIGH = 285
    CMD19_TIMEOUT_ERROR = 286
    CMD19_RESPONSE_TO_ERROR = 287
    CMD19_DATA_MISCOMPARE_ERROR = 288
    CMD19_CRC_RESPONSE_ERROR = 289
    CMD19_READ_TIMEOUT_ERROR = 290
    CMD19_CRC_DATA_ERROR = 291
    WATCHDOG_TIMEOUT_TUNING = 292
    FAST_BOOT_TIMEOUT_ERR = 293
    SET_HIGH_SPEED_NOT_SUPORTED_IN_MMC = 294
    HPI_TIMEOUT_ERROR = 295
    DRIVER_FAILURE = 296
    CHUNK_COUNT_BLOCK_MISMATCH = 297
    PARTIAL_CONFIG_SWITCH_ERROR = 298
    PARTIAL_CONFIG_WATCHDOG_ERROR = 299
    FPGA_DOES_NOT_SUPPORT_OPERATION = 300
    ENABLE_VDDIO_ISNT_SUPPORT_IN_LOW_REGION = 301
    UHS_VDDIO_HIGH_THAN_1V9 = 302
    SET_VOLT_OUT_OF_REGION_ERROR = 303
    VDDH_HIGHER_THAN_LIMIT = 304
    LATENCY_OVERFLOW = 305
    MDL_CPP_EXCEPTION = 306
    HOST_ASYNC_POWER_LOSS_OR_HWRST_EVENT = 307
    NO_OPTIMAL_TAP_FOUND = 308
    USER_SET_SUM_OF_VDDS_MAX_CURRENT_OVER_HOST_LIMIT = 309
    ILLEGAL_VDET_SEQUENCE_ERROR = 310
    WRONG_SUB_PROTOCOL_TYPE = 311
    WINDOWS_DIR_NOT_FOUND = 312
    FREQUENCY_OPERATION_ERROR = 313
    UNSUPPORTED_DATA_TRANSER_MODE = 314
    UNSUPPORTED_ABORT_MODE = 315
    UNSUPPORTED_ABORT_OPERATION = 316
    UNSUPPORTED_BOOT_SCOPE = 317
    UNSUPPORTED_MACRO_TYPE = 318
    UNSUPPORTED_ABORT_TYPE = 319
    UNSUPPORTED_IMMEDIATE_FORMAT = 320
    WATCHDOG_TIMEOUT_DEL_TAP = 321
    VDDIO_HIGHER_THAN_VDDH = 322
    TRYING_TO_SET_A_SD_MODE_ON_MMC_FW = 323
    CARD_END_BIT_ERROR = 324
    CARD_CC_TOTAL_ERRORS = 325
    DATA_MISCOMPARE_ERROR = 5124


