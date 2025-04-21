"""
class Constants
Contains all constant values
@ Author: Shaheed Nehal
@ copyright (C) 2021 Western Digital Corporation
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    pass # from builtins import *
    from builtins import object
import Extensions.CVFImports as pyWrap
import os

SECURITY_ENABLED = False
PAGE_IN_SLC_BLK = 256
PAGE_IN_TLC_BLK = PAGE_IN_SLC_BLK * 3

# Option enable/disable
ENABLED = 1
DISABLED = 0

KB = 1024.0
MB = 1024 * KB
GB = 1024 * MB
NUM_OF_BITS_PER_BYTE = 8

#CSSSYSVAL-5438
MIN_TXLEN_IN_KB = 256 * KB

# one GB based on 512 bytes per lba
LBA_1GB = 0x1FFFFF
LBA_200MB = 0x64000


SECTORALIGNED = 1

#Index for Range List
START_INDEX = 0
END_INDEX = 1
START_RANGE = 0
END_RANGE = 1
LUN = 0

START_LBA = 0
TRANSFER_LEN = 8

eDrive_byteOffset = 60

#Telemetry
TELEMETRY_HOST_INITIATED = 0x07
TELEMETRY_CONTROLLER_INITIATED = 0x08

# return value for success/failure
SUCCESS = True
FAILURE = False

# NODE_TYPE DETAILS
EQUAL_NUM_SEQUENTIAL_LBAS = 0
UNEQUAL_NUM_SEQUENTIAL_LBAS = 1
EQUAL_NUM_RANDOM_LBAS = 2
UNEQUAL_NUM_RANDOM_LBAS = 3

# TRAVERSAL LIST
RANDOM_TRAVERSAL = 0
PREORDER_TRAVERSAL = -1
POSTORDER_TRAVERSAL = 1

# TRANSFER_MODE modes
FIXED_TRANSFER_MODE = 0
RANDOM_TRANSFER_MODE = 1

# VERIFY_MODE
REGULAR_VERIFY = 0
RANDOM_VERIFY = 1
IMMEDIATE_VERIFY = 2
REVERSE_VERIFY = 3
DO_NOT_VERIFY = 4

# ERASE_MODE Modes
ERASE_SEQUENTIAL = 0
ERASE_RANDOM_SEQUENCE = 1
ERASE_RANDOM = 2

# ERASE_VERIFY_MODE Verification types
# Write Erase Read
ERASE_VERIFY_WER = 0
# Write Erase Write Read
ERASE_VERIFY_WEWR = 1

#ERASE_TYPE
ERASE_UNMAP_ERASE = 0
ERASE_UNMAP_DISCARD = 1
ERASE_RANDOM_UNMAP = 2
ERASE_PURGE0 = 3
ERASE_FORMAT = 4

#ERASE info tuple
ERASE_STARTLBA = 0
ERASE_TRANSFERLENGTH = 1

#StarVMDoCompare
STARLBA = 0
TRANSFER_LENGTH = 100

#to prevent overlap writes
MINIMUM_COMMANDS_PER_CYCLE = 64

#number of cycles to consider for preventing overlaps
OVERLAP_PREVENTION_CYCLES = 2
DISALLOW_OVERLAP = False
ALLOW_OVERLAP = True

# AP utils differentiation between sequential and random
AP_SEQUENTIAL_TEST = 0
AP_RANDOM_TEST = 1

# MST File Size
FILE_51_SIZE = 8192 #bytes
MST_TEST_START_TIME = 150 #seconds

# COMPLETION_TIMEOUT used in CCM
COMPLETION_TIMEOUT = 1000

#Payload
PAYLOAD = 16

#BreakMode
BREAK_MODE_DENOMINATOR = 8

#partitions
SLC = 0
TLC = 1

#AP tests sequential change
# in terms of lbas with 4096 byte size
# 1 LBA or Sector = 512 Bytes
# 1 KB = 1024 Bytes (Binary Capacity)
# 1 GB = 2097152 lbas
# 1 MB = 2048 lbas (Sectors)
APTEST_MAX_LBA_RANGE_TO_WRITE_PER_CYCLE = 65536 #(65536 Sectors = 0xFFFF sector count reg. = 32MB)
MAX_LBA_SAMSUMG_DEVICE = 500118080 #(~238GB - after that you get Out of LBA range error)
# when getting a random number if the loop exceeds this number of tries we mark it failed
GET_RANDOM_LOOP_LIMIT = 32

# Constants for Read-Scrub Command (BLOCK TYPE VALUE)
OPEN_BLOCK = OPEN_BLOCK_BOUNDARY = 0x1
CLOSED_BLOCK = 0x2

NONE_STRING = "None"

#Common libraries names
UTILS_MODULE = "Utils"

# DataProgressMode
DATA_PROGRESS_SEQUENTIAL = 0
DATA_PROGRESS_RANDOM     = 1

##
# @brief Defines Write Types
# @details Based on CTF 1.5
OperationOrder_FORWARD = 0
OperationOrder_BACKWARD = 1
OperationOrder_RANDOM = 2

READ_GPL_COMMAND_OPCODE = 0x2F # added by Sravan K Ghantasala
READ_GPL_SUBCOMMAND_OPCODE = 0x0 #added by Sravan K Ghantasala

IDENTIFY_CONTROLLER_BUFFER_SIZE = 4096

#constants used by precondition
DEFAULT_XFERLENGTH = 128
XFERLENGTH_128k_IN_SECTORS = 32
XFERLENGTH_4K_IN_SECTORS = 1
XFERLENGTH_64k_IN_SECTORS = 16
SHORTSTROKE_4X = 4
SHORTSTROKE_2X = 2
DEFAULT_LBARANGE = 0.1
XFERLENGTH_4K_IN_SECTORS_updated = 8
##Contants used by BBM validation
BBM_FORMATDEVICE_STATUS = True

#NVME log page ID
SMART_PAGE_ID_GENERIC = 0x02
SMART_PAGE_ID_LENOVO = 0XDF
SMART_PAGE_ID_DELL = 0XCA
SMART_PAGE_ID_ASUS = 0xCD
SMART_PAGE_ID_HP = 0xC7
ERROR_INFORMATION_PAGE_ID = 0x1
FIRMWARE_SLOT_INFORMATION_PAGE_ID = 0x3
CHANGE_NAME_SPACE_LIST_PAGE_ID = 0x4
COMMAND_EFFECTS_LOG_PAGE_ID = 0x5
SANITIZE_STATUS_LOG_PAGE_ID = 0x81
DST_LOG_PAGE_ID = 0x6
PLP_STATISTICS_LOG_PAGE = 0xF0
PE_LOG_PAGE = 0x0D

#Thread pool manager mode
BURST_MODE = 0
CONTINUOUS_MODE = 1
SUSTAINED_MODE = 2

# **Compare and Fused Commands**

FUSED_DISABLE = 0
FUSED_FIRST_CMD = 1
FUSED_SECOND_CMD = 2

# RS scan types
ACTIVE_SCAN = 0
PASSIVE_SCAN = 1
RANDOM_SCAN = 2

#Hermes NPSS
DEVICE_NPSS = 4 #Zero Based

#Queue
NUMOFQUEUES = 16

class FW_Read_Status_CONSTANTS(object):
    STATUS_OK = 0x0
    STATUS_ERASED_READ = 0x2
    STATUS_READ_ECC_ERROR = 0x4
    STATUS_CANNOT_COMPLETE = 0x667

class FwConfig_CONSTANTS(object):
    #Constants
    D2_DIV_FACTOR = 2
    CONTROL_BLOCK_NO_OF_ENTRIES_IN_A_GAT_PAGE = 416 # DS Change --> 400 for ME5
    BE_SPECIFIC_SECTORS_PER_RAW_ECC_PAGE = 0x5
    BE_SPECIFIC_BYTES_PER_SECTOR = 0x200
    BE_SPECIFIC_HEADER_SIZE_IN_BYTES = 0x20
    FLASH_TYPE_MLC = 0x02
    FLASH_TYPE_BINARY = 0x01
    FLASH_TYPE_ABL = 0x10
    FLASH_TYPE_SAMSUNG = 0x8
    FLASH_TYPE_D3 = 0x80

class Setup_Config_CONSTANTS(object):
    #SETUP_CONFIG.ini
    STD_MODEL_WRITE_TIMEOUT = 25000  #Standard Write timeOut Value as per MODEL Spec
    STD_MODEL_READ_TIMEOUT  = 10000  #Standard Read timeOut Value as per MODEL Spec
    STD_MODEL_RESET_TIMEOUT = 10000  #Standard reset timeOut Value as per MODEL Spec
    BE_SPECIFIC_BYTES_PER_SECTOR            = 0x200
    CONTROL_ADDITIONAL_OFFSET               = 0x100
    CONTROL_BLOCK_RGAT_PAGE_HEADER            = 0x18
    CONTROL_BLOCK_RGAT_DIRECTORY_PAGE_HEADER  = 0x19
    BE_SPECIFIC_MIP_ID_BYTE_IN_HEADER       = 0x21
    CONTROL_BLOCK_GAT_PAGE_HEADER           = 0x22
    BE_SPECIFIC_BCI_ID_BYTE_IN_HEADER       = 0x23
    CONTROL_BLOCK_ICB_PAGE_ID               = 0x24
    CONTROL_BLOCK_BOOT_PAGE_ID              = 0x25
    CONTROL_BLOCK_FS_NON_MAP_PAGE_HEADER    = 0x26
    CONTROL_BLOCK_FS_MAP_PAGE_HEADER        = 0x27
    CONTROL_BLOCK_GAT_DIRECTORY_PAGE_HEADER = 0x28
    CONTROL_BLOCK_IGAT_PAGE_HEADER          = 0x29
    CONTROL_BLOCK_RGAT_DIRECTORY_OF_DIRECTORIES_PAGE_HEADER = 0x1A
    GC_CONTEXT_EPWR_HEADER_ID               = 0x2A
    GC_CONTEXT_UECC_HEADER_ID               = 0x2B
    GC_CONTEXT_BLOCK_HEADER_ID              = 0x2C
    GC_CONTEXT_UGC_HEADER_ID                = 0x2C
    GC_CONTEXT_UGC_BITMAP_HEADER_ID         = 0x2D
    GC_CONTEXT_MLC_HEADER_ID                = 0x2E
    GC_CONTEXT_MLC_BITMAP_HEADER_ID         = 0x2F
    COMPACTION_INFO_POINTERS                = 0x2E
    SLC_FIFO_DUMP                           = 0x2F
    ID_ERR_LOG                              = 0x35
    ID_ERR_LOG_DIR                          = 0x36
    MAX_RETRIAL_AFTER_CRC_ERROR = 3
    CRC_ERROR_CODE = 0xE0100012
    MAX_RANDOM_SEED_VALUE = 10000
    MAX_TEST_NAME_LENGTH = 55
    STD_SD_WRITE_TIMEOUT = 250
    STD_SD_READ_TIMEOUT  = 100
    STD_SD_RESET_TIMEOUT = 100
    STD_SCSI_WRITE_TIMEOUT = 10000
    STD_SCSI_READ_TIMEOUT  = 10000
    STD_SCSI_RESET_TIMEOUT = 10000
    STD_MS_WRITE_TIMEOUT = 1000
    STD_MS_READ_TIMEOUT  = 1000
    STD_MS_RESET_TIMEOUT = 1000
    IS_SUPPORT_DETERMINISTIC_TRIM = True

class FS_Config_CONSTANTS(object):
    #FS_CONFIG.ini
    MAX_FS_FILES=70
    IFS_LARGE_FILE_START_NUMBER=240
    IFS_CORRECTABLE_ECC = 0X0
    IFS_UNCORRECTABLE_ECC =0x1
    IFS_IMPORTANT_FILE_LIST = [1,80,228,229,240,242]
    IFS_FACTORY_MARKED_BAD_BLOCK_FILE_ID =224
    IFS_LINK_FILE_ID =235
    IFS_FILE_VERSION_LENGTH = 0x02
    IFS_BLOCK_SIZE_IN_ENTRY_IN_LINK_FILE = 2
    IFS_LINK_ENTRY_SIZE_IN_LINK_FILE = 16
    IFS_LINK_ENTRIES_START_OFFSET_IN_LINK_FILE = 32

class BB_Config_CONSTANTS(object):
    #BB_CONFIG.ini
    REG_FUSE_ADDRESS_COPY_OFFSETS_X2_1Y   = [0x640,0x1640,0x2640,0x3640]
    REG_FUSE_ADDRESS_COPY_OFFSETS_EX3_1Y  = [0x380,0xB80,0x1380,0x1B80]
    REG_FUSE_ADDRESS_COPY_OFFSETS_EX3_1Z  = [0x800,0x1800,0x2800,0x3800]
    REG_FUSE_ADDRESS_COPY_OFFSETS_EX3_BICS = [0x400,0x1400,0x2400,0x3400]
    USER_ROM_ADDRESS_COPY_OFFSETS_EX3_1Y  = [0x380,0xB80,0x1380,0x1B80]
    USER_ROM_ADDRESS_COPY_OFFSETS_EX2_1Y  = [0x640,0x1640,0x2640,0x3640]
    USER_ROM_ADDRESS_COPY_OFFSETS_EX2_1Y_128G = [0xA80,0x1A80,0x2A80,0x3A80]
    ROM_FUSE_BYTE_COUNT_PER_DIE        = 1024
    REG_FUSE_BYTE_COUNT_PER_DIE        = 512
    ROM_FUSE_NUM_OF_SECTORS_TO_READ    = 32
    REG_FUSE_NUM_OF_SECTORS_TO_READ    = 1
    NUM_OF_BYTES_PER_ONE_BAD_BLOCK_INFO = 4
    ROM_FUSE_SPEC_INDEX_BIT             = 7
    REG_FUSE_SPEC_INDEX_BIT             = 7
    USER_ROM_BYTE_COUNT_PER_DIE        = 12288
    USER_ROM_NUM_OF_SECTORS_TO_READ    = 24
    USER_ROM_SPEC_INDEX_BIT             = 7
    READ_FW_MAXLBA_OFFSET = 0x00
    BE_SPECIFIC_BYTES_PER_SECTOR = 0x200
    DGN_NAND_ROM_OR_REG_READ_CMD_OPCODE = 0xA2
    DGN_NAND_ROM_READ_ROMFUSE_SUB_OPCODE = 1
    DGN_NAND_ROM_READ_BADBLOCK_SOURCE_SUB_OPCODE = 2
    DGN_NAND_ROM_READ_USERROM_BADBLOCKTABLE_SUB_OPCODE = 3
    DGN_NAND_USERROM_READ_BADBLOCK_SOURCE_SUB_OPCODE = 5
    DGN_NAND_REG_READ_REGFUSE_SUB_OPCODE = 4


class SendType(object):
    SEND_NONE = pyWrap.SEND_NONE
    SEND_IMMEDIATE = pyWrap.SEND_IMMEDIATE
    SEND_IMMEDIATE_ASYNC = pyWrap.SEND_IMMEDIATE_ASYNC
    SEND_QUEUED = pyWrap.SEND_QUEUED


values4HermesXplorerJSON = [{"remoteAddress":'127.0.0.1'}, {"remotePort":8081}, {"informerSerialNumber":'000000'}, {"product":'Hermes'}, {"atbMode":'20E'}, {"calibrationEnabled":'false'}, {"rwrPath":'rwrPath'}, {"rwrMaxFileSize":100}, {"rwrMaxFileCount":0}, {"dcoPath":'dcoPath'}, {"type":'Gen2'}]


##
# @brief This class contains the waypoints names as constants to be used in the test layer
# @details Each waypoint is a unique string. Args description are presented for each waypoint
# @author - Asaf Eiger
# @date 8June2016
# @copyright Copyright (C) 2016 SanDisk Corporation
class Waypoints(object):
    ##
    # @brief
    # @param arg[0] = Group ID
    # @param arg[1] = Accumlator Type [0-SLC, 1-RND TLC, 2-SEQ TLC]
    WP_FTL_HWD_ROUTING_RULES = "WP_FTL_HWD_ROUTING_RULES"

    ##
    # @brief
    # @param arg[0] = Group ID
    # @param arg[1] = FMU Padded
    WP_FTL_HWD_PADDING = "WP_FTL_HWD_PADDING"

    ##
    # @brief
    # @param arg[0] = HWD CTX ID
    # @param arg[1] = Group ID
    WP_FTL_HWD_START_WRITE = "WP_FTL_HWD_START_WRITE"

    ##
    # @brief Indicates RMW started for this group
    # @param arg[0] = Group ID
    # @param arg[1] = FMU Index
    # @param arg[2] = BLS Head
    # @param arg[3] = Sector Count
    WP_FTL_HWD_RMW = "WP_FTL_HWD_RMW"

    ##
    # @brief Indicates RMW is done for this group
    # @param arg[0] = Group ID
    WP_FTL_HWD_RMW_DONE = "WP_FTL_HWD_RMW_DONE"

    ##
    # @brief Indicates FUA started for this ITag
    # @param arg[0] = HWD CTX ID
    # @param arg[1] = ITag
    # @param arg[2] = HWD CTXT
    WP_FTL_HWD_FUA = "WP_FTL_HWD_FUA"

    ##
    # @brief Indicates FUA is done for this ITag
    # @param arg[0] = ITag
    WP_FTL_HWD_FUA_DONE = "WP_FTL_HWD_FUA_DONE"

    ##
    # @brief
    # @param arg[0] = Stream ID
    # @param arg[1] = FFLBA
    # @param arg[2] = First Sector Offset
    # @param arg[3] = Size
    WP_FTL_HWD_STREAM_STATUS = "WP_FTL_HWD_STREAM_STATUS"

    ##
    # @brief
    # @param arg[0] = Stream ID
    # @param arg[1] = FFLBA
    # @param arg[2] = First Sector Offset
    # @param arg[3] = Size
    WP_FTL_HRF_STREAM_STATUS = "WP_FTL_HRF_STREAM_STATUS"


    ##
    # @brief
    WP_FTL_OLP_START_SYNC = "WP_FTL_OLP_START_SYNC"

    ##
    # @brief Processing 1 entry from the overlap queue
    # @param arg[0] = HWD ID
    WP_FTL_OLP_PROCESS_ENTRY = "WP_FTL_OLP_PROCESS_ENTRY"

    ##
    # @brief Processing 1 entry from the FE admin queue
    WP_FTL_OLP_FEADMIN_PROCESS_ENTRY = "WP_FTL_OLP_FEADMIN_PROCESS_ENTRY"

    ##
    # @brief Waiting is done. Can start processing from the FW admin queue
    WP_FTL_OLP_FEADMIN_CALLBACK = "WP_FTL_OLP_FEADMIN_CALLBACK"

    ##
    # @brief
    # @param arg[0] = Stream Type [0-RND, 1-SEQ, 2-OVLP]
    # @param arg[1] = HWD ID to wait for OR Number of entries in the overlap queue if there are 2 streams
    WP_FTL_OLP_START_STREAM_WRITE_SYNC = "WP_FTL_OLP_START_STREAM_WRITE_SYNC"

    ##
    # @brief No entries in this stream
    # @param arg[0] = Stream Type [0-RND, 1-SEQ, 2-OVLP]
    WP_FTL_OLP_STREAM_EMPTY = "WP_FTL_OLP_STREAM_EMPTY"

    ##
    # @brief Start RMW sync on a stream
    # @param arg[0] = Stream Type [0-RND, 1-SEQ, 2-OVLP]
    # @param arg[1] = Number of in-flight RMW
    WP_FTL_OLP_START_STREAM_RMW_SYNC = "WP_FTL_OLP_START_STREAM_RMW_SYNC"

    ##
    # @brief Start TLC sync on a stream
    # @param arg[0] = Stream Type [0-RND, 1-SEQ, 2-OVLP]
    WP_FTL_OLP_START_STREAM_TLC_SYNC = "WP_FTL_OLP_START_STREAM_TLC_SYNC"


class PEL_Constants(object):
    ACTION_Read_Log_Data=0x0
    ACTION_Establish_Context_Read_Log_Data=0x1
    ACTION_Release_Context=0x2
    Log_Id = 0
    TNEV = 4
    TLL = 8
    Log_Revision = 16
    Log_Header_Length = 18
    TimeStamp = 20
    Power_On_Hours=28
    Power_Cycle_Count=44
    PCI_Vendor_ID = 52
    PCISSVID = 54
    Serial_Number = 56
    Model_Number = 76
    NVMSUBQualifiedName = 116
    SupportedEventsBitMap = 480

    #EventHeaderInformation
    EventType = 0
    EventTypeRevision = 1
    EventHeaderLength = 2
    ControllerIdentifier = 4
    EventTimestamp = 6
    VSIL = 20
    EventLength = 22

    #Max Events in PEL
    SMART = 2
    Firmware_Commit = 10
    TimeStampEvent = 100
    Power_On_Reset = 20
    FormatNVMStart = 2
    FormatNVMComplete = 2
    SanitizeStart = 2
    SanitizeComplete = 2
    ThermalExcursion = 20
    HardwareErrors=20

class SectorsInKB(object):
    SECTORS_IN_4KB = 8


# Constants for Morpheus diagnostic command
class MRPH_CONST(object):
    MRPH_MAPENTRY_SIZE_BYTES_REV0A              = 12    # number of Bytes in each morpheus map entry
    MRPH_MAPENTRY_SIZE_BYTES                    = 8    # number of Bytes in each morpheus map entry
    MRPH_MAPENTRY_PAYLOADSIZE_BYTE_OFFSET_REV0A = 8     # Byte offset of payload size in each morpheus map entry
    MRPH_MAPENTRY_PAYLOADSIZE_BYTE_OFFSET       = 6     # Byte offset of payload size in each morpheus map entry
    MRPH_MAPENTRY_FASTSLC_TABLEID               = 5     # Fast SLC table ID in the morpheus map entry
    MRPH_MAPENTRY_END_TABLEID                   = 0xFFFF # End of mapentry table ID in the morpheus map entry
    MRPH_SECT_FASTSLC_HEADERBYTES               = 4     # number of Bytes in Fast SLC section before encountering actual Fast SLC info
    MRPH_SECT_FASTSLC_PECBYTES                  = 2     # number of Bytes used to specify a PE Threshold entry
    MRPH_SECT_FASTSLC_PARAMBYTES                = 4     # number of Bytes used to describe all the info for a single Fast SLC Nand parameter
    CFGSET_MRPH_SECT_VERSION                    = 10    # Morpheus config set number for Morpheus version
    CFGSET_MRPH_SECT_CVDTRACK                   = 11    # Morpheus config set number for CVD Tracking
    CFGSET_MRPH_SECT_FLGP                       = 12    # Morpheus config set number for find last good page
    CFGSET_MRPH_SECT_DX3W                       = 13    # Morpheus config set number for direct x3 write
    CFGSET_MRPH_SECT_FASTSLC                    = 14    # Morpheus config set number for Fast SLC adaptive vpgm
    CFGSET_MRPH_SECT_RS                         = 15    # Morpheus config set number for read scrub
    CFGSET_MRPH_SECT_ZQ                         = 16    # Morpheus config set number for zq calibration
    CFGSET_MRPH_SECT_LDPC                       = 17    # Morpheus config set number for ldpc
    CFGSET_MRPH_SECT_REHOPTIONS                 = 18    # Morpheus config set number for REH options
    CFGSET_MRPH_SECT_RI                         = 19    # Morpheus config set number for read improvements
    CFGSET_MRPH_SECT_LDPCSTATIC                 = 20    # Morpheus config set number for LDPC static config
    CFGSET_MRPH_SECT_BES                        = 21    # Morpheus config set number for cross temp AT
    CFGSET_NAND_VER                             = 23    # Nand version, MT version, ROM Fuse RPGM Version


class FS_CONSTANTS(object):

    SECTOR_SIZE_TO_GET_LENGTH_OF_FILE = 1

    ACTIVE_PARTITION_FILE_DIRECTORY_BASE_OFFSET = 768   #648
    CODE_PARTITION_FILE_DIRECTORY_BASE_OFFSET = 408     #416
    BOOT_BLOCK_LIST_ENTRIES_BASE_OFFSET = 20
    PARTITION_BLOCK_LIST_ENTRIES_BASE_OFFSET = 120


    ACTIVE_PARTITION_FILE_DIRECTORY_ENTRIES = 81
    CODE_PARTITION_FILE_DIRECTORY_ENTRIES = 19
    PARTITION_BLOCK_LIST_ENTRIES = 32  #24
    BOOT_BLOCK_LIST_ENTRIES = 20

    OFFSET_TO_GET_CODE_PARTITION_LENGTH_IN_BYTES = 412
    BYTES_PER_CODE_PARTITION_ENTRY = 12
    OFFSET_TO_GET_ACTIVE_PARTITION_LENGTH_IN_BYTES = 764     #644
    BYTES_PER_ACTIVE_PARTITION_ENTRY = 12

    DIRECTORY_FILE_ID = 1
    READ_PRIMARY_COPY_OPTION = 2
    READ_SECONDARY_COPY_OPTION = 6

    MRPH_USERROM_PAYLOAD_FILE_ID = 22
    MRPH_DRIVE_PAYLOAD_FILE_ID = 23
    RELINK_BSBM_PS0_FID = 224
    RELINK_BSBM_PS1_FID = 225
    MBBT_FILE_ID = 226
    UECC_LIST_PS0 = 227

    FIRMWARE_STRUCTURE_SCHEMA_FILE = 95



    #BOOT_BLOCK_LIST_OWNER_DICT = {"BOOT_BLOCK": 1 , "FREE_BLOCK": 5, "FAIL_BLOCK":4}
    PARTITION_BLOCK_LIST_OWNER_DICT = {"CODE_BLOCK": 1 , "ACTIVE_BLOCK": 3, "FAIL_BLOCK":4, "FREE_BLOCK":5}
    PARTITION_BLOCK_LIST = {"CODE_P", "CODE_S", "ACTIVE_P", "ACTIVE_S", "FREE1", "FREE2", "FREE3", "FREE4", "FREE5", "FREE6", "FREE7", "FREE8", "FREE9", "FREE10", "FREE11", "FREE12", "FREE13", "FREE14", "FREE15", "FREE16", "FREE17", "FREE18", "FREE19", "FREE20"}

    POWER_STATE = 0
    SET_FEATURE = 1
    NS_CREATION = 2

    #IFS EI Options supported by SCTP
    IFS_CLR_ERR_INJ = 0
    IFS_ERR_RD_PRI = 1
    IFS_ERR_RD_SEC = 2
    IFS_ERR_COMP_RD_PRI = 3
    IFS_ERR_COMP_RD_SEC = 4
    IFS_ERR_WR_PF_PRI = 5
    IFS_ERR_WR_PF_SEC = 6
    IFS_ERR_WR_TO_PRI = 7
    IFS_ERR_WR_TO_SEC = 8
    IFS_ERR_COMP_WR_PF_PRI = 9
    IFS_ERR_COMP_WR_PF_SEC = 10
    IFS_ERR_COMP_WR_PF_ANY = 11
    IFS_ERR_COMP_WR_TO_SEC = 12
    IFS_ERR_WR_UPD_BP_PRI = 13
    IFS_ERR_WR_UPD_BP_SEC = 14
    IFS_ERR_COMP_UPD_BP_PRI = 15
    IFS_ERR_COMP_UPD_BP_SEC = 16
    IFS_ERR_PF_WR_PRI_DIR = 17
    IFS_ERR_PF_WR_SEC_DIR = 18
    IFS_ERR_FFU_DWL_WR = 19
    IFS_ERR_FFU_COMMIT_RD = 20
    IFS_ERR_FFU_FS_WR_PRI = 21
    IFS_ERR_FFU_FS_WR_SEC = 22
    IFS_ERR_ERASE_BLOCK = 23
    IFS_ERR_FADI_WRITE = 24


class SCTP_CONSTANTS(object):
    CDB_LENGTH = 16
    SCTP_PARTITIONID_SLC = 0x0
    SCTP_PARTITIONID_TLC = 0x1
    SCTP_GETPE_INDIVIDUAL = 0x0
    SCTP_GETPE_COMPLETEPARTITION = 0x1
    SCTP_GETPE_COMPLETE = 0x2
    SCTP_GETPE_MAXAVG = 0x3
    SCTP_READ_PHYSICAL = 0xB1
    SCTP_WRITE_PHYSICAL = 0xB2
    SCTP_ERASE_PHYSICAL_BLOCK = 0x81
    SCTP_TRANSLATE_LBA_TO_INTERNAL_FLASH_ADDRESS = 0X87
    SCTP_SCTP_TRANSLATE_VBA_TO_DEVBA_PBA = 0XD7
    SCTP_OPCODE_GET_NAND_PARAM = 0xD8
    SCTP_OPCODE_FIND_LAST_GOOD_PAGE = 0xDC
    SCTP_OPCODE_PERFORMANCE_MEASUREMENT_TEST = 0xDE
    SCTP_OPCODE_NPDP_UNIT_TESTS = 0xD5
    SUBOPCODE_TRANSLATE_VBA_TO_DEVBA = 0
    SUBOPCODE_TRANSLATE_VBA_TO_PBA = 1
    SCTP_INJECT_IFS_ERRORS = 0xF9
    SCTP_GET_NDWL_MAINTENANCE_STATUS = 0x0219


class EI_FRAMEWORK_CONSTANTS(object):

    #BASEOFFSET_SLOT = {0: 3216, 1: 3312, 2: 3408, 3: 3504, 4: 3600, 5: 3696}
    BASEOFFSET_SLOT = (3216, 3312, 3408, 3504, 3600, 3696)

    ADDR_OFFSET = 0
    ADDR_TYPE_OFFSET = 8
    ADDR_TYPE = {'VBA': 0, 'deVBA': 1, 'LBA': 2, 'Op-ID': 3}
    NSID_OFFSET = 9
    OPERATION_TO_INJECT_OFFSET = 10
    OPERATION_TO_INJECT = {'READ': 0, 'PROG': 1, 'ERASE': 2, 'LOAD': 3,
                           'REBUILD': 4, 'RECOVERY_LOAD': 5,
                           'RECOVERY_UNROLL_PS0': 6, 'RECOVERY_UNROLL_PS1': 7,'STORE':10}
    IS_VALID_OFFSET = 11
    READ_FAILURE_TYPE = {'NO_FAILURE': 0, 'SB0': 2, 'SB1': 3, 'SB2': 4,
                         'SB2+DLA': 5, 'CLIP': 6, 'UECC': 7}

    PROG_FAILURE_TYPE = {'1WL': 0, 'WL2WL': 1, 'LWL2LWL': 2, '1WL_2PLANES': 3, '2PLANES_WL2WL': 4,
                         'WL2WL_P2P': 5, 'EPWR': 6, 'WA': 7, '1LWL': 8, 'SKIP_WRITE': 9}
    PF_READ_INJECT_PAGE = {'NUM0': 4, 'NUM1': 6, 'NUM2': 8, 'NUM3': 10, 'NUM4': 12, 'NUM5': 14,
                           'NUM6': 16, 'NUM7': 18}
    PF_FAIL_TYPE_PAGE = {'NUM0': 20, 'NUM1': 24, 'NUM2': 28, 'NUM3': 32, 'NUM4': 36, 'NUM5': 40,
                         'NUM6': 44, 'NUM7': 48}
    PF_NESTED_ERROR_PAGE = {'NUM0': 48, 'NUM1': 48, 'NUM2': 48, 'NUM3': 48}

    FAIL_PAGE_SLOT = [16, 24, 32, 40, 48, 56]
    SLOT_ZERO_BASEOFFSET = 3216
    SLOT_ONE_BASEOFFSET = 3312

    HOST_OPERATIONS = 0
    RMW_OPERATIONS = 1
    FUA_OPERATIONS = 2
    DEALLOCATE_CONTROL_DATA_OPERATIONS = 3
    LOG_OPERATIONS = 4
    RLA_OPERATIONS = 5
    MTM_OPERATIONS = 6
    XOR_BLOCK_OPERATIONS = 7
    XOR_ZONE_REBUILD = 8
    ACTIVE_RS = 9
    FLGP = 10
    SCAN_FWD = 11
    READ_HEADERS = 12
    RLC_HOST_VC = 13
    RLC_HOST_BLOCKS = 14
    RLC_MTM_BLOCKS = 15
    RLC_XOR_BLOCKS = 16
    BRLC_HOST_BLOCKS = 17
    BRLC_RLC_BLOCKS = 18
    BRLC_MTM_BLOCKS = 19
    BRLC_XOR_BLOCKS = 20
    IFS_BLOCKS = 21
    FADI_BLOCKS = 22
    BOOT_BLOCKS = 23
    IFS_DIRECTORY_BLOCKS = 24
    HOSTLESS_OPERATIONS = 25

class PS_CONSTANTS(object):
    NUM_OF_FIMS = 2
    PAGES_IN_SLC_LWL = 1
    PAGES_IN_TLC_LWL = 3
    SLC_PAGES_IN_TLC_PAGE = 3
    NUMBER_OF_FIMS_IN_MB = 4
    PLANES_IN_PHYSICAL_BLK = 2
    NUM_OF_XOR_PAGES_SLC = 1
    METADATA_PER_FMU = 32
    #Hermes 2 Constants, SLC/TLC Block Type should be 1 and 2 if is Hermes
    SLC_BLOCK_TYPE = 0
    TLC_BLOCK_TYPE = 1
    BYTES_IN_PHYSICAL_PAGE = 16384
    BYTES_IN_FMU = 4096
    RAW_BYTES_IN_FMU = 4584
    FMU_COUNT_IN_PAGE = 4
    METADIES_PER_ZONE = 2
    #METADIES_PHOENIX_128GB = 1
    METADIES_PHOENIX_64GB = 1
    METADIES_PHOENIX_128GB = 2
    DIE_GB_CAPACITY = 32
    NUM_SECTORS_PER_LWL = 512
    BYTES_PER_PHY_PAGE = 16384
    PLANES_PER_PHY_BLK = 2
    PHY_BLKS_IN_METABLK = 4#8
    METABLKS_IN_JUMBOBLK = 2
    NUM_OF_PS_PROCESSORS = 2
    PLANES_PER_JUMBOBLK = PHY_BLKS_IN_METABLK * NUM_OF_PS_PROCESSORS
    NUM_OF_LOGICAL_WL_PER_PHY_WL = 4
    # Parity Pages for SLC or TLC
    PARITY_PAGES_PER_ZONE_SLC = PHY_BLKS_IN_METABLK * PAGES_IN_SLC_LWL
    PARITY_PAGES_PER_ZONE_SLC_BiCS4 = PHY_BLKS_IN_METABLK * PAGES_IN_SLC_LWL * NUM_OF_PS_PROCESSORS
    STARTING_PARITY_BINS_SLC = [0, 4, 1, 5, 2, 6, 3, 7]
    STARTING_PARITY_BINS_SLC_BiCS4 = [[0,8,2,10,4,12,6,14], [1,9,3,11,5,13,7,15]]
    PARITY_PAGES_SLC = (7, 3, 0, 4, 1, 5, 2, 6)
    #PARITY_PAGES_SLC_BiCS4 = (7, 15, 1, 9, 3, 11, 5, 13, 0, 8, 2, 10, 4, 12, 6, 14)
    PARITY_PAGES_SLC_BiCS4 = (6, 14, 2, 10, 0, 8, 4, 12, 7, 15, 3, 11, 1, 9, 5, 13)
    PARITY_BIN_MAX_SLC = 7
    PARITY_BIN_MAX_SLC_BiCS4 = 15
    PARITY_PAGES_PER_ZONE_TLC = PHY_BLKS_IN_METABLK * PAGES_IN_TLC_LWL * NUM_OF_PS_PROCESSORS
    STARTING_PARITY_BINS_TLC = [0, 12, 3, 15, 6, 18, 9, 21]
    STARTING_PARITY_BINS_TLC_BiCS4 = [[0, 24, 6, 30, 12,36, 18, 42], [3, 27, 9, 33, 15, 39, 21, 45]]
    PARITY_PAGES_TLC = (21,  9, 0, 12, 3, 15, 6, 18,
                        22, 10, 1, 13, 4, 16, 7, 19,
                        23, 11, 2, 14, 5, 17, 8, 20)
    PARITY_BIN_MAX_TLC = 23

    #PARITY_PAGES_TLC_BiCS4 = (21, 45,3,27,9,33,15,39,0,24,6,30,12,36,18,42,
                            #22,46,4,28,10,34,16,40,1,25,7,31,13,37,19,43,
                            #23,47,5,29,11,35,17,41,2,26,8,32,14,38,20,44)
    PARITY_PAGES_TLC_BiCS4 = (18, 42,6,30,0,24,12,36,19,43,7,31,1,15,13,37,
                            20,44,8,32,2,26,14,38,21,45,9,33,3,7,15,39,
                            22,46,10,34,4,28,16,40,23,47,11,35,5,29,17,41)
    PARITY_BIN_MAX_TLC_BiCS4 = 47

    # Fims in PS0 and PS1
    PARITY_BINS_SLC = (0, 4, 1, 5, 2, 6, 3, 7)
    PARITY_BINS_TLC = ([0, 12, 3, 15, 6, 18,  9, 21],
                       [1, 13, 4, 16, 7, 19, 10, 22],
                       [2, 14, 5, 17, 8, 20, 11, 23])

    PARITY_BINS_SLC_BiCS4 = (0,8,2,10,4,12,6,14,1,9,3,11,5,13,7,15)
    PARITY_BINS_TLC_BiCS4 = ([0,24,6,30,12,36,18,42,3,27,9,33,15,39,21,45],
                             [1,25,7,31,13,37,19,43,4,28,10,34,16,40,22,46],
                             [2,26,8,32,14,38,20,44,5,29,11,35,17,41,23,47])

    PAGE = (0, 1, 2)
    FIM = (0, 1, 2, 3, 4, 5, 6, 7)
    PLANE = (0, 1)
    BIN_NUM_SLC = {FIM[0]: {PLANE[0]: PARITY_BINS_SLC[0], PLANE[1]: PARITY_BINS_SLC[1]},
                  FIM[1]: {PLANE[0]: PARITY_BINS_SLC[2], PLANE[1]: PARITY_BINS_SLC[3]},
                  FIM[2]: {PLANE[0]: PARITY_BINS_SLC[4], PLANE[1]: PARITY_BINS_SLC[5]},
                  FIM[3]: {PLANE[0]: PARITY_BINS_SLC[6], PLANE[1]: PARITY_BINS_SLC[7]},
                  FIM[4]: {PLANE[0]: PARITY_BINS_SLC[0], PLANE[1]: PARITY_BINS_SLC[1]},
                  FIM[5]: {PLANE[0]: PARITY_BINS_SLC[2], PLANE[1]: PARITY_BINS_SLC[3]},
                  FIM[6]: {PLANE[0]: PARITY_BINS_SLC[4], PLANE[1]: PARITY_BINS_SLC[5]},
                  FIM[7]: {PLANE[0]: PARITY_BINS_SLC[6], PLANE[1]: PARITY_BINS_SLC[7]}}

    BIN_NUM_TLC = {PAGE[0]: {FIM[0]: {PLANE[0]: PARITY_BINS_TLC[0][0], PLANE[1]: PARITY_BINS_TLC[0][1]},
                             FIM[1]: {PLANE[0]: PARITY_BINS_TLC[0][2], PLANE[1]: PARITY_BINS_TLC[0][3]},
                             FIM[2]: {PLANE[0]: PARITY_BINS_TLC[0][4], PLANE[1]: PARITY_BINS_TLC[0][5]},
                             FIM[3]: {PLANE[0]: PARITY_BINS_TLC[0][6], PLANE[1]: PARITY_BINS_TLC[0][7]},
                             FIM[4]: {PLANE[0]: PARITY_BINS_TLC[0][0], PLANE[1]: PARITY_BINS_TLC[0][1]},
                             FIM[5]: {PLANE[0]: PARITY_BINS_TLC[0][2], PLANE[1]: PARITY_BINS_TLC[0][3]},
                             FIM[6]: {PLANE[0]: PARITY_BINS_TLC[0][4], PLANE[1]: PARITY_BINS_TLC[0][5]},
                             FIM[7]: {PLANE[0]: PARITY_BINS_TLC[0][6], PLANE[1]: PARITY_BINS_TLC[0][7]}},

                   PAGE[1]: {FIM[0]: {PLANE[0]: PARITY_BINS_TLC[1][0], PLANE[1]: PARITY_BINS_TLC[1][1]},
                             FIM[1]: {PLANE[0]: PARITY_BINS_TLC[1][2], PLANE[1]: PARITY_BINS_TLC[1][3]},
                             FIM[2]: {PLANE[0]: PARITY_BINS_TLC[1][4], PLANE[1]: PARITY_BINS_TLC[1][5]},
                             FIM[3]: {PLANE[0]: PARITY_BINS_TLC[1][6], PLANE[1]: PARITY_BINS_TLC[1][7]},
                             FIM[4]: {PLANE[0]: PARITY_BINS_TLC[1][0], PLANE[1]: PARITY_BINS_TLC[1][1]},
                             FIM[5]: {PLANE[0]: PARITY_BINS_TLC[1][2], PLANE[1]: PARITY_BINS_TLC[1][3]},
                             FIM[6]: {PLANE[0]: PARITY_BINS_TLC[1][4], PLANE[1]: PARITY_BINS_TLC[1][5]},
                             FIM[7]: {PLANE[0]: PARITY_BINS_TLC[1][6], PLANE[1]: PARITY_BINS_TLC[1][7]}},

                   PAGE[2]: {FIM[0]: {PLANE[0]: PARITY_BINS_TLC[2][0], PLANE[1]: PARITY_BINS_TLC[2][1]},
                             FIM[1]: {PLANE[0]: PARITY_BINS_TLC[2][2], PLANE[1]: PARITY_BINS_TLC[2][3]},
                             FIM[2]: {PLANE[0]: PARITY_BINS_TLC[2][4], PLANE[1]: PARITY_BINS_TLC[2][5]},
                             FIM[3]: {PLANE[0]: PARITY_BINS_TLC[2][6], PLANE[1]: PARITY_BINS_TLC[2][7]},
                             FIM[4]: {PLANE[0]: PARITY_BINS_TLC[2][0], PLANE[1]: PARITY_BINS_TLC[2][1]},
                             FIM[5]: {PLANE[0]: PARITY_BINS_TLC[2][2], PLANE[1]: PARITY_BINS_TLC[2][3]},
                             FIM[6]: {PLANE[0]: PARITY_BINS_TLC[2][4], PLANE[1]: PARITY_BINS_TLC[2][5]},
                             FIM[7]: {PLANE[0]: PARITY_BINS_TLC[2][6], PLANE[1]: PARITY_BINS_TLC[2][7]}}}

    WL_PER_PHY_BLK_BICS2 = 48
    WL_PER_PHY_BLK_BICS3 = 64
    WL_PER_PHY_BLK_BICS4 = 96
    # Logical Word Length Per Physical Block
    LWL_PER_PHY_BLK_BICS2 = WL_PER_PHY_BLK_BICS2 * NUM_OF_LOGICAL_WL_PER_PHY_WL
    LWL_PER_PHY_BLK_BICS3 = WL_PER_PHY_BLK_BICS3 * NUM_OF_LOGICAL_WL_PER_PHY_WL
    LWL_PER_PHY_BLK_BICS4 = WL_PER_PHY_BLK_BICS4 * NUM_OF_LOGICAL_WL_PER_PHY_WL
    # Total Pages In a Zone (WL * LWL * Planes * PS)
    PAGES_PER_ZONE_BICS2 = LWL_PER_PHY_BLK_BICS2 * 8 * 2
    PAGES_PER_ZONE_BICS3 = LWL_PER_PHY_BLK_BICS3 * 8 * 2
    PAGES_PER_ZONE_BICS4 = LWL_PER_PHY_BLK_BICS4 * 8 * 2

    PAGES_PER_PHY_BLK_SLC_BICS2 = LWL_PER_PHY_BLK_BICS2 * PAGES_IN_SLC_LWL
    PAGES_PER_PHY_BLK_SLC_BICS3 = LWL_PER_PHY_BLK_BICS3 * PAGES_IN_SLC_LWL
    PAGES_PER_PHY_BLK_SLC_BICS4 = LWL_PER_PHY_BLK_BICS4 * PAGES_IN_SLC_LWL
    PAGES_PER_PHY_BLK_TLC_BICS2 = LWL_PER_PHY_BLK_BICS2 * PAGES_IN_TLC_LWL
    PAGES_PER_PHY_BLK_TLC_BICS3 = LWL_PER_PHY_BLK_BICS3 * PAGES_IN_TLC_LWL
    PAGES_PER_PHY_BLK_TLC_BICS4 = LWL_PER_PHY_BLK_BICS4 * PAGES_IN_TLC_LWL

    BYTES_IN_PHY_BLK_BICS2 = LWL_PER_PHY_BLK_BICS2 *  BYTES_PER_PHY_PAGE * PLANES_PER_PHY_BLK
    BYTES_IN_PHY_BLK_BICS3 = LWL_PER_PHY_BLK_BICS3 *  BYTES_PER_PHY_PAGE * PLANES_PER_PHY_BLK
    BYTES_IN_PHY_BLK_BICS4 = LWL_PER_PHY_BLK_BICS4 *  BYTES_PER_PHY_PAGE * PLANES_PER_PHY_BLK

    BYTES_IN_METABLK_BICS2 = BYTES_IN_PHY_BLK_BICS2 * PHY_BLKS_IN_METABLK
    BYTES_IN_METABLK_BICS3 = BYTES_IN_PHY_BLK_BICS3 * PHY_BLKS_IN_METABLK
    BYTES_IN_METABLK_BICS4 = BYTES_IN_PHY_BLK_BICS4 * PHY_BLKS_IN_METABLK

    BYTES_IN_JUMBOBLK_BICS2 = BYTES_IN_METABLK_BICS2 * METABLKS_IN_JUMBOBLK
    BYTES_IN_JUMBOBLK_BICS3 = BYTES_IN_METABLK_BICS3 * METABLKS_IN_JUMBOBLK
    BYTES_IN_JUMBOBLK_BICS4 = BYTES_IN_METABLK_BICS4 * METABLKS_IN_JUMBOBLK

    LWL_PER_PHY_WL = 4
    LWL_PER_JUMBO_BLK_BICS2 = 48 * LWL_PER_PHY_WL
    LWL_PER_JUMBO_BLK_BICS3 = 64 * LWL_PER_PHY_WL
    LWL_PER_JUMBO_BLK_BICS4 = 96 * LWL_PER_PHY_WL

    DATA_CHUNK_SIZE_IN_FMU_DATA = 512
    NUM_OF_DATA_CHUNK_IN_FMU_DATA = 8
    DATA_CHUNK_START_OFFSET_FROM_FMU_DATA = 0
    LDPC_SCRAMBLE_SEED_OFFSET_FROM_FMU_DATA = DATA_CHUNK_SIZE_IN_FMU_DATA * NUM_OF_DATA_CHUNK_IN_FMU_DATA - 1
    LDPC_SCRAMBLE_SEED_SIZE_IN_FMU_DATA = 2
    DATA_TYPE_OFFSET_FROM_FMU_DATA = LDPC_SCRAMBLE_SEED_OFFSET_FROM_FMU_DATA + LDPC_SCRAMBLE_SEED_SIZE_IN_FMU_DATA
    DATA_TYPE_SIZE_IN_FMU_DATA = 1
    NAMESPACE_OFFSET_FROM_FMU_DATA = DATA_TYPE_OFFSET_FROM_FMU_DATA + DATA_TYPE_SIZE_IN_FMU_DATA
    NAMESPACE_SIZE_IN_FMU_DATA = 1
    LBA_OFFSET_FROM_FMU_DATA = NAMESPACE_OFFSET_FROM_FMU_DATA + NAMESPACE_SIZE_IN_FMU_DATA
    WUC_OFFSET_IN_HEADER = 2

    LWL_SIZE_TLC_IN_KB = 768
    LWL_SIZE_SLC_IN_KB = 256
    FMU_SIZE_IN_KB = 4

    READ_RETRY_BASEOFFSET_PS0 = 16
    HARDBIT_RETRY_BASEOFFSET_PS0 = 48
    SOFTBIT1_RETRY_BASEOFFSET_PS0 = 80
    SOFTBIT2_RETRY_BASEOFFSET_PS0 = 112
    XOR_ENTRY_BASEOFFSET_PS0 = 144


    READ_RETRY_BASEOFFSET_PS1 = 16
    HARDBIT_RETRY_BASEOFFSET_PS1 = 48
    SOFTBIT1_RETRY_BASEOFFSET_PS1 = 80
    SOFTBIT2_RETRY_BASEOFFSET_PS1 = 112
    XOR_ENTRY_BASEOFFSET_PS1 = 144

    DISTRIBUTION_PADDING = 4096

class NO_OF_BYTES(object):
    PER_KB = 1024
    PER_MB = 1024 * PER_KB
    PER_GB = 1024 * PER_MB
    PER_SECTOR = 4096


# Number of Ranges in one Deallcoate Command
Deallocate_Minimum_Count = 1
Deallocate_Maximum_Count = 256

# Added value for one GB
# 1GB to LBA convert
oneGB = 262144

#Draw Graph Constants
WRITE_GRAPH = 1
READ_GRAPH = 1



class FFU_CONSTANTS(object):

    SERVERPATH = "\\\\sclfilip14\\moonshot\\FVT\\CFG\\BICS3_CFG"
    flufFileName = "CFGenc.fluf"
    HSMPath = "\\\\sclfilip14\\moonshot\\FVT\\HSMSigning"

class CSV_CONSTANTS(object):
    CSVPATH = "\\\\sclfilip14\\moonshot\\FVT\\CSV"

class SECURITY_CONSTANTS(object):
    # @brief This class will contain the constants to be used in the security tests validation
    # Default Password used for ATA protocol
    PASSWORD = "sandisk"

    # Max password used/supported by ATA protocol
    ATA_MAX_PASSWORD_LENGTH = 30

    # Security protocol names
    ATA_SECURITY_PROTOCOL = 'ATA'
    OPAL_SECURITY_PROTOCOL = 'OPAL'
    PYRITE_SECURITY_PROTOCOL = 'PYRITE'
    EDRIVE_SECURITY_PROTOCOL = 'EDRIVE'

    # Security status
    SECURITY_ACTIVATE = 'ACTIVATE'
    SECURITY_DEACTIVATE = 'DEACTIVATE'
    SECURITY_EXISTING = 'EXISTING'

    # Power cycle constants
    GSD_POWER_CYCLE = "GSD"
    UGSD_POWER_CYCLE = "UGSD"
    RANDOM_POWER_CYCLE = "RANDOM"
    POWER_CYCLE_TIME = 1

    # Locking States
    LOCK_GLOBAL_RANGE = 0
    UNLOCK_GLOBAL_RANGE = 1
    RANDOMLY_LOCK_OR_UNLOCK = 2

    # Locking ranges constants
    ATA_MAX_LOCKING_RANGE  = 1
    OPAL_MAX_LOCKING_RANGE = 8

    # Range Constants
    LOCAL_RANGE_TYPE  = "LOCAL_RANGE"
    GLOBAL_RANGE_TYPE = "GLOBAL_RANGE"


    MAXIMUM_ATTEMPTS = 4
    GLOBAL_RANGE_NAME = "Global_Range"
    RANGE_NAME        = "Range_"
    OFFSET_RANGE_NAME = "OffsetRange_"

    # Range Access flags
    READ_LOCKED   = "ReadLocked"
    WRITE_LOCKED  = "WriteLocked"
    READ_LOCKED_ENABLED  = "ReadLockedEnabled"
    WRITE_LOCKED_ENABLED = "WriteLockedEnabled"

    # Variable names used to repport error/warnings
    READ_LOCKED_RANGES_COUNT      = "readLockedRangesCount"
    WRITE_LOCKED_RANGES_COUNT     = "writeLockedRangesCount"
    READ_LOCKED_ENABLE_RANGES_COUNT  = "readLockedEnableRangesCount"
    WRITE_LOCKED_ENABLE_RANGES_COUNT = "writeLockedEnableRangesCount"

    # SHADOW_WRITE to MBR region
    WRITE_SHADOWMBR = 0XFF10

    """Below are constants like,
    1. Commonly used token such as list tokens, named tokens etc.
    2. Lenghts of various fields such as MethodUID lengths etc.
    3. Starting Offsets of each segment in the command buffer such as lengths of compacket, packet, payload , subpacket etc.
    4. UIDs of various objects.
    5. Method UIDs

!!!!!!!!!!
All the names should be CAPITALIZED as they are constants and also,
in the scipt, every where the referece for these constants are pulled using uppercase strings.
!!!!!!!!!!
"""
    START_PAYLOAD   = 0xF8
    END_PAYLOAD     = 0xF9

    START_LIST  = 0xF0
    END_LIST    = 0xF1

    START_NAMED_TOKEN   = 0xF2
    END_NAMED_TOKEN     = 0xF3

    SMUID = 0xFF
    SPUID = 0x10
    Security_Protocol_mapping = {'Pyrite':0x1,'Pyrite2':0x1,'Opal':0x1,'SUM':0x1,'eDrive':0xEE,'ATA':0x1,'OPAL':0x1,'PYRITE':0x1}

    class LENGTHS(object):
        METHOD_LENGTH   = 8
        SMUID_LENGTH    = 8

    class STARTING_OFFSETS(object):
        """All the attributes in here should be starting with the keyword 'FOR_'"""
        FOR_COMPACKET       = 0
        FOR_PACKET          = 20
        FOR_DATA_SUBPACKET  = 44
        FOR_PAYLOAD         = 56

    class UID(object):
        """All the attributes in here should be starting with the keyword 'OF_'"""
        OF_SMUID = 0xFF
        OF_GLOBAL_RANGE_UID = 0x80200000001

        # Ace tables UIDs
        OF_ACE_LOCKING_GLOBALRANGE_SET_RDLOCKED_UID = 0x080003E000
        OF_ACE_LOCKING_GLOBALRANGE_SET_WRLOCKED_UID = 0x080003E800
        OF_ACE_DATASTORE_GET_ALL_UID = 0x080003FC00
        OF_ACE_DATASTORE_SET_ALL_UID = 0X080003FC01
        OF_ACE_AUTHORITY_GET_ALL_UID = 0x0800039000
        OF_ACE_AUTHORITY_SET_ENABLED = 0x0800039001
        OF_ACE_C_PIN_USER1_SET_PIN   = 0x080003A801
        OF_ACE_C_PIN_USER2_SET_PIN   = 0x080003A802
        OF_ACE_C_PIN_USER3_SET_PIN   = 0x080003A803
        OF_ACE_C_PIN_USER4_SET_PIN   = 0x080003A804
        OF_ACE_C_PIN_USER5_SET_PIN   = 0x080003A805
        OF_ACE_C_PIN_USER6_SET_PIN   = 0x080003A806
        OF_ACE_C_PIN_USER7_SET_PIN   = 0x080003A807
        OF_ACE_C_PIN_USER8_SET_PIN   = 0x080003A808

        # Taken from Authorities table of Locking SP
        OF_ADMINS   = 0x0900000002
        OF_ADMIN    = 0x0900010001

        OF_ADMIN1   = 0x0900010002
        OF_ADMIN2   = 0x0900010003
        OF_ADMIN3   = 0x0900010004

        OF_USER1    = 0x0900030001
        OF_USER2    = 0x0900030002
        OF_USER3    = 0x0900030003
        OF_USER4    = 0x0900030004
        OF_USER5    = 0x0900030005
        OF_USER6    = 0x0900030006
        OF_USER7    = 0x0900030007
        OF_USER8    = 0x0900030008

        OF_SID_UID  = 0x0900000006
        OF_MSID_UID = 0x0900000100
        OF_USERS    = 0x0900030000              # added only for getting the list of users using Next method.

        # Taken from "Locking" table of Locking SP
        OF_LOCKING_GLOBALRANGE    = 0x080200000001

        # UIDS for SPs
        OF_ADMIN_SP_UID     = 0x020500000001
        OF_LOCKING_SP_UID   = 0x020500000002
        OF_THIS_SP_UID      = 0x01

        # Table IDs
        OF_DATASTORE_UID    = 0x100100000000
        OF_ACCESSCONTROLTABLE_UID = 0x000700000000

        # CPINs from CPIN table
        OF_C_PIN_SID    = 0x0B00000001
        OF_C_PIN_ADMIN1 = 0x0B00010001
        OF_C_PIN_ADMIN  = 0x0B00010002

        OF_C_PIN_ADMIN2 = 0x0B00010003
        OF_C_PIN_ADMIN3 = 0x0B00010004
        OF_C_PIN_ADMIN4 = 0x0B00010005

        OF_C_PIN_USER1  = 0x0B00030001
        OF_C_PIN_USER2  = 0x0B00030002
        OF_C_PIN_USER3  = 0x0B00030003
        OF_C_PIN_USER4  = 0x0B00030004
        OF_C_PIN_USER5  = 0x0B00030005
        OF_C_PIN_USER6  = 0x0B00030006
        OF_C_PIN_USER7  = 0x0B00030007
        OF_C_PIN_USER8  = 0x0B00030008
        OF_C_PIN_MSID   = 0x0B00008402

        # Half UIDS
        AUTHORITY_HALF_UID  = 0x0C05
        BOOLEAN_HALF_UID    = 0x040E

        # Boolean UIDs
        OF_AND  = 0x00
        OF_OR   = 0x01

        #Table UIDs
        OF_AUTHORITY    = 0x0900000000


    class METHODID(object):
        """All the attributes in here should be starting with the keyword 'FOR_'"""
        FOR_PROPERTIES      = 0xFF01
        FOR_STARTSESSION    = 0xFF02
        FOR_SET             = 0x0600000017
        FOR_GET             = 0x0600000016
        FOR_ACTIVATE        = 0x0600000203
        FOR_REVERT          = 0x0600000202
        FOR_REVERTSP        = 0x0600000011
        FOR_NEXT            = 0x0600000008
        FOR_GETACL          = 0x060000000D
        FOR_AUTHENTICATE    = 0x060000001C

    class eDrive(object):

        Status_codes = {
            0x0:'Sucess',
            0x1:'Sucess',
            0x80:'Failure',
            0x81:'Unsupported_IEEE_Version',
            0x82:'Invalid_TCG_ComID',
            0x83:'Synchronus_Protocol_Viloation',
            0xF6:'Silo_interaction_error',
            0xF7:'Invalid_Parameter_Configuration',
            0xF8:'Inavlid Parameter Length',
            0xF9:'Inconsistent Payload Conetent Length',
            0xFA:'Inavlid Silo',
            0xFB:'Incomplete_Command_Received',
            0xFC:'Invalid_Parameter',
            0xFD:'P_OUT/P_IN Sequence_rejection',
            0xFE:'NO_Probe',
            0xFF:'Ivalid Command ID'
        }

##
# @brief This class will contain the constants to be used in the error log tests validation

class ERROR_LOG_CONSTANTS(object):


    FADI_DEFAULT_ENTRY_SIZE = 4096
    #Amount Of Supported Error Log Page Entries In The Identify Controller
    ERROR_LOG_PAGEENTRIES_SUPPORTED = 255

    XPYFAD_FILE_NAME = "xpyfad.exe"

    #Severity Levels
    CRITICAL_SEVERITY = 1
    WARNING_SEVERITY = 2
    INFO_SEVERITY = 3

    NUMBER_OF_PARAMETERS = 5

    #Error Source
    FADI_FVT_ARTIFICIAL = -1
    FADI_FVT_EL_PS0 = 0
    FADI_FVT_EL_PS1 = 1
    FADI_FVT_EL_FTL = 2
    FADI_FVT_EL_INFRA = 3
    FADI_FVT_EL_FE = 4
    FADI_FVT_EL_SECURITY = 5

    class ErrorNames(object):
        #Artificial Error Log Names
        CRITICAL_ERROR_NAME = 'FADI_ERRORLOG_CODE_FVT_CRITICAL_MARKER'
        WARNING_ERROR_NAME = 'FADI_ERRORLOG_CODE_FVT_WARNING_MARKER'
        INFO_ERROR_NAME = 'FADI_ERRORLOG_CODE_FVT_INFO_MARKER'

        #PS Errors
        FADI_PS_EH_LOG_CODE_CRITICAL = "FADI_PS_EH_LOG_CODE_CRITICAL"

        #Infra Errors
        FADI_ERRORLOG_CODE_TT_EXTREME_THROTTLING = 'FADI_ERRORLOG_CODE_TT_EXTREME_THROTTLING'
        FADI_ERRORLOG_CODE_TT_THERMAL_SHUTDOWN = 'FADI_ERRORLOG_CODE_TT_THERMAL_SHUTDOWN'
        FADI_ERRORLOG_CODE_TT_PMIC_WARNING = 'FADI_ERRORLOG_CODE_TT_THERMAL_SHUTDOWN'
        FADI_ERRORLOG_CODE_TT_PMIC_SHUTDOWN = 'FADI_ERRORLOG_CODE_TT_THERMAL_SHUTDOWN'

        #FE Errors

        #FTL Errors
##
# @brief A class to contain host power states constants
class PowerStates(object):
    PS3 = 3 #DPS2
    PS4 = 4 #DPS3

# @brief A class to contain Sanitize constants
class SANITIZE_CONSTANTS(object):

    #Sanitize command comst
    ExitFailureMode = 0x1
    StartBlockEraseSanitize = 0x2
    StartOverwriteSanitize = 0x3
    StartCryptoEraseSanitize = 0x4

    #Sanitize log const
    TheNVMSubsystemNeverBeenSanitized = 0x0
    LastSanitizeCompletedSuccessfully = 0x1
    SanitizeInProgress = 0x2
    LastSanitizeOperationFailed = 0x3
    SPROGconst = 65536
    SPROGDeafultStatus = 0xFFFF

# @brief A class to contain SMART constants
class SMART_CONSTANTS(object):

    AsyncEventInformation_Reliability = AsyncEventInformation_PercentageUsedHP = 0x0
    AsyncEventInformation_Temperature = 0x1
    AsyncEventInformation_Spare = 0x2

    CriticalWarning_Spare = 0x1
    CriticalWarning_Temperature = 0x2
    CriticalWarning_Reliability = 0x4
    CriticalWarning_RO = 0x8

class PCF_CONSTANTS(object):
    import random

    DOORBELL_MODE = {'AUTO': 0, 'MANUAL': 1, 'MIN': 2, 'MAX': 3}
    CMD_ID = {'CTRL_EN'       : pyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_CONTROLLER_RESET,
              'NSSR'          : pyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_CONTROLLER_SUBSYSTEM_RESET,
              'PCIe_FLR'      : pyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_PCIE_FLR_RESET,
              'PCIe_HOT_RESET': pyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_PCIE_HOT_RESET,
              'PCIe_LINK_DIS' : pyWrap.E_COMMAND_TYPE_ID.CTF_CMD_ID_PCIE_DSPORT_RESET}

    RAND_CHOICE = lambda: random.choice(['CTRL_EN', 'NSSR', 'PCIe_FLR', 'PCIe_HOT_RESET', 'PCIe_LINK_DIS'])

    CTRL_EN        = pyWrap.GetNVMeCCRegisterAddressAndData
    NSSR           = pyWrap.GetNVMeNSSRRegisterAddressAndData
    PCIe_FLR       = pyWrap.GetPCIFLRRegisterAddressAndData
    PCIe_HOT_RESET = pyWrap.GetPCIBridgeControlRegisterAddressAndData
    PCIe_LINK_DIS  = pyWrap.GetPCILinkControlRegisterAddressAndData


#Xplorer path. Please note Xplorer should always be installed at C:\Xtools
#rwr gets recorded and stored at D:\user-storage\rwr; the SetDictionary.dco shall be placed her
#configPath folder shall also exist at D:\user-storage\configPath
    ## xPlorer path
    #if os.path.exists("D:\\"):
        #xPlorerPath = "d:\\\\xtools\\app\\\\xplorer"
        #informerRecorderPath = "d:\\\\xtools\\app\\\\xrwrrecorder"
        #rwrFilePathDir = "D:\\user-storage\\rwr"
    #else:
        #xPlorerPath = "C:\\\\xtools\\app\\\\xplorer"
        #informerRecorderPath = "C:\\\\xtools\\app\\\\xrwrrecorder"
        #rwrFilePathDir = "C:\\user-storage\\rwr"


class FLGP_Constants(object):
    SIGNATURES = ["TER", "BER", "MPD"]
    LGW = {"TER" : 0}
    WA = {"TER" : 1}
    NEXT_WRITABLE_PAGE = {"TER" : 1}
    EPWR_PHYSICAL_WORDLINES = [0,47,95]
    SECTORS_PER_LWL = 256
    FMU_COUNT_TLC_PAGE = 12
    FMU_COUNT_SLC_PAGE = 4
    RAW_BYTES_IN_FMU = 4584
    BLOCK_TYPE_SLC = 0
    BLOCK_TYPE_TLC = 1
    RAW_WRITE_OPTION_SLC = 0x01 #0xB2
    RAW_WRITE_OPTION_TLC = 0x09 #0xB2
    RAW_READ_OPTION_SLC = 0x20 #0xB1
    RAW_READ_OPTION_TLC = 0x28 #0xB1
    SECTORS_PER_PAGE_SLC = FMU_COUNT_SLC_PAGE*RAW_BYTES_IN_FMU
    SECTORS_PER_PAGE_TLC = FMU_COUNT_TLC_PAGE*RAW_BYTES_IN_FMU
    BUFFER_PATTERN_ALL_0 = 0


class FLGP_CONSTANTS(object):
    SIGNATURES = ["TER", "BER", "MPD"]
    LGW = {"TER" : 0}
    WA = {"TER" : 1}
    NEXT_WRITABLE_PAGE = {"TER" : 1}
    EPWR_PHYSICAL_WORDLINES = [0,47,95]
    SECTORS_PER_LWL = 256
    FMU_COUNT_TLC_PAGE = 12
    FMU_COUNT_SLC_PAGE = 4
    RAW_BYTES_IN_FMU = 4584
    BLOCK_TYPE_SLC = 0
    BLOCK_TYPE_TLC = 1
    RAW_WRITE_OPTION_SLC = 0x01 #0xB2
    RAW_WRITE_OPTION_TLC = 0x09 #0xB2
    RAW_READ_OPTION_SLC = 0x20 #0xB1
    RAW_READ_OPTION_TLC = 0x28 #0xB1
    SECTORS_PER_PAGE_SLC = FMU_COUNT_SLC_PAGE*RAW_BYTES_IN_FMU
    SECTORS_PER_PAGE_TLC = FMU_COUNT_TLC_PAGE*RAW_BYTES_IN_FMU
    BUFFER_PATTERN_ALL_0 = 0
    XFER_LEN_HOST_WRITE = {0:256, 1:512, 2:1024, 3: 768}
    MAX_PHYSICAL_WL = 95
    MAX_LOGICAL_WL = 383

    OPEN_BLOCK_ENUM = {0: "OBM_BLOCK_TYPE_DATA_BLK_BASE , OBM_BLOCK_TYPE_TLC_BASE, OBM_BLOCK_TYPE_DYN_RLC",
                       1: "OBM_BLOCK_TYPE_STC_RLC",
                       2: "OBM_BLOCK_TYPE_HOST_SEQ_TLC",
                       3: "OBM_BLOCK_TYPE_HOST_RND_TLC",
                       4: "OBM_BLOCK_TYPE_HOST_SEQ_SLC",
                       5: "OBM_BLOCK_TYPE_HOST_RND_SLC",
                       6: "OBM_BLOCK_TYPE_CTL_BLK",
                       7: "OBM_BLOCK_TYPE_XOR",
                       8: "OBM_BLOCK_TYPE_LOG",
                       9: "OBM_BLOCK_TYPE_BRLC",
                       10: "OBM_BLOCK_TYPE_MAX",
                       255: "OBM_BLOCK_TYPE_PHYSICALLY_CLOSED / OBM_BLOCK_TYPE_ILLEGAL"}


class OpenBlockSLC(object):
    LWL_PER_PHYSICAL_WL = 4
    SECTORS_PER_LWL = 256
    RAW_BYTES_SINGLE_FMU = 4584
    FMU_PER_LWL_SINGLE_MD = 4
    SECTORS_PER_PHYSICAL_WL = LWL_PER_PHYSICAL_WL * SECTORS_PER_LWL
    RAW_BYTES_PER_LWL_SINGLE_MD = FMU_PER_LWL_SINGLE_MD * RAW_BYTES_SINGLE_FMU
    HOST_WRITE_OPTIONS_SEQ = 4
    HOST_WRITE_OPTIONS_RND = 5


class OpenBlockTLC(object):
    LWL_PER_PHYSICAL_WL = 4
    PAGES_PER_LWL = 3
    SECTORS_PER_LWL = 256*PAGES_PER_LWL
    RAW_BYTES_SINGLE_FMU = 4584
    FMU_PER_LWL_SINGLE_MD = 12
    SECTORS_PER_PHYSICAL_WL = LWL_PER_PHYSICAL_WL * PAGES_PER_LWL * SECTORS_PER_LWL
    RAW_BYTES_PER_LWL_SINGLE_MD = FMU_PER_LWL_SINGLE_MD * RAW_BYTES_SINGLE_FMU
    HOST_WRITE_OPTIONS_SEQ = 2
    HOST_WRITE_OPTIONS_RND = 3
    EPWR_WORDLINES = [0, 47, 95]

class String_Constants(object):
    STR_OPEN = 'OPEN'
    STR_CLOSED = 'CLOSED'
    STR_SD = 'SD'
    STR_NVME = 'NVME'
    STR_NVMe_OF_SDPCIE = 'NVME_OF_SDPCIE'
    STR_SD_OF_SDPCIE = 'SD_OF_SDPCIE'
    STR_WRITE = 'WRITE'
    STR_READ = 'READ'
    STR_UGSD = 'UGSD'
    STR_GSD = 'GSD'
    STR_PC = 'PC'  #power cycle (performs UGSD) - similar to re-initialization
    STR_PA = 'PA'  #power abort (performs UGSD) - similar to write abort
    STR_WA = 'WA'  #write abort (performs UGSD)
    STR_SLC = 'SLC'
    STR_TLC = 'TLC'
    STR_SLC_XTEMP = 'SLC_XTEMP'
    STR_TLC_XTEMP = 'TLC_XTEMP'
    STR_BALANCED = 'BALANCED'
    STR_URGENT = 'URGENT'
    STR_BOTH = 'BOTH'
    STR_TRUE = 'TRUE'
    STR_FALSE = 'FALSE'
    STR_PF = 'PF'
    STR_MODE_SWITCH = 'MODE_SWITCH'
    STR_DIAG = 'DIAG'
    STR_HOST_PF = 'HOST_PF'
    STR_HOST_UECC = 'HOST_UECC'
    STR_MTM_PF = 'MTM_PF'
    STR_MTM_UECC = 'MTM_UECC'
    STR_MTM = 'MTM'
    STR_LOG = 'LOG'
    STR_XOR = 'XOR'

    STR_WRITE_OPEN_ENDED_CMD = 'WRITE_OPEN_ENDED_CMD'
    STR_READ_OPEN_ENDED_CMD = 'READ_OPEN_ENDED_CMD'

    STR_WRITE_OPEN_ENDED_CMD_PREMATURE_ST = 'WRITE_OPEN_ENDED_CMD_PREMATURE_ST'
    STR_READ_OPEN_ENDED_CMD_PREMATURE_ST = 'READ_OPEN_ENDED_CMD_PREMATURE_ST'

    STR_WRITE_CLOSED_ENDED_CMD = 'WRITE_CLOSED_ENDED_CMD'
    STR_READ_CLOSED_ENDED_CMD = 'READ_CLOSED_ENDED_CMD'

    STR_WRITE_CLOSED_ENDED_CMD_PREMATURE_ST = 'WRITE_CLOSED_ENDED_CMD_PREMATURE_ST'
    STR_READ_CLOSED_ENDED_CMD_PREMATURE_ST = 'READ_CLOSED_ENDED_CMD_PREMATURE_ST'

    STR_WRITE_SINGLE_SECTOR_CMD24 = 'WRITE_SINGLE_SECTOR_CMD24'
    STR_READ_SINGLE_SECTOR_CMD24 = 'READ_SINGLE_SECTOR_CMD24'

    STR_NONE = 'NONE'

class  Boolean_Constants(object):
    BOOL_FALSE = False
    BOOL_TRUE = True


class Numerical_Constants(object):
    CONST_NUMERICAL_ZERO = 0
    CONST_NUMERICAL_ONE = 1
    CONST_NUMERICAL_TWO = 2
    CONST_NUMERICAL_THREE = 3
    CONST_NUMERICAL_FOUR = 4
    CONST_NUMERICAL_FIVE = 5
    CONST_NUMERICAL_SIX = 6
    CONST_NUMERICAL_SEVEN = 7
    CONST_NUMERICAL_EIGHT = 8
    CONST_NUMERICAL_NINE = 9
    CONST_NUMERICAL_TEN = 10
