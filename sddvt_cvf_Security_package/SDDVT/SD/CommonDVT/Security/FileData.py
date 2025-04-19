"""
class DiagnosticLib
Contains config files' data
@ Author: Shaheed Nehal - ported to CVF
@ copyright (C) 2021 Western Digital Corporation
"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from builtins import str
from builtins import hex
from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    pass # from builtins import str
    from builtins import range
    pass # from builtins import *
    from builtins import object
from past.utils import old_div
import Extensions.CVFImports as pyWrap
import Utils as Utils
import DiagnosticLib
import FwConfig as FwConfig
import Core.ValidationError as TestError

def GetFile14Data(vtfContainer):
    #offsets
    PHY_CHIP_IL = 0x8
    DIE_IL = 0x9
    PLANE_IL = 0xA
    BANK_SPLITTING_OFFSET = 0xB
    SHIFTED_WORDLINE = 0x2A
    NUM_OF_SLC_FBL_BLOCKS = 0x41
    NUM_SEQ_STREAMS = 0x44
    NUM_RANDOM_STREAMS = 0x45
    NUM_OF_RELOCATION_STREAMS = 0x46
    GAT_BLOCK_DUAL_WRITE_ENABLE = 0x51
    MLC_GROWN_DEFECT = 0x54
    GAT_DELTA_MAX_ENTRY = 0x55
    GAT_DIR_DELTA_MAX_ENTRY = 0x57
    IGAT_DELTA_MAX_ENTRY = 0x5B
    NUM_GAT_BLOCKS = 0x5C
    CONTROL_PAGE_SIZE_IN_SECTORS = 0x5E
    MIP_PAGE_SIZE_IN_SECTORS = 0x5F
    MIN_BINARY_FBL_LENGTH_OFFSET = 0x60 #Min SLC FBL Size Per Metaplane
    MAX_BINARY_FBL_LENGTH_OFFSET = 0x61 #Max SLC FBL Size Per Metaplane
    MIN_MLC_FBL_LENGTH_OFFSET = 0x62    #Min MLC FBL Size Per Metaplane
    MAX_MLC_FBL_LENGTH_OFFSET = 0x63    #Max MLC FBL Size Per Metaplane
    NUM_BLOCKS_DEDICATED_FBL = 0x66
    SLC_FBL_RATIO = 0x6A #For every 10 spare blocks, how many SLCs to be allocated first
    EFUSE_PRODUCTION_DATA = 0x6D
    NUM_OF_GAT_FBL_BLOCKS = 0X7A #Need to confirm this value

    NUM_ZONES_PER_DIE = 0x0BA #1B
    TOTAL_BADBLOCKS_REQUIRED_PER_DIE = 0x0BB #2B
    MAX_ALLOWABLE_BB_PER_ZONE = 0x0BD #2B
    START_BB_OFFSET_FIRST_ZONE = 0x0BF #2B

    ZQ_CALP = 0x101
    ZQ_CALN= 0x102

    FILE_ID = 14

    fileBuf = DiagnosticLib.ReadFileSystem(vtfContainer, fileID=FILE_ID)

    configParams = {"phyChipIL":None, "DieIL":None, "PlaneIL":None, "bankSplitting":None,\
                    "minmlcFblLenght":None,"maxmlcFblLenght":None, "minbinaryFblLength":None,\
                    "maxbinaryFblLength":None, "numOfBlocksDedicatedFBL":None, "numOfGATBlocks":None,\
                    "numOfSlcFblBlocks":None, "numofGATFblBlocks":None, "shiftedWLValue":None,\
                    "EFuseProductionData":None, "EFuseProcutionCrc":None, "GatBlockDualWriteEnabled":None,\
                    "GATDeltaMaxEntry":None, "GATDirDeltaMaxEntry":None, "IGATDeltaMaxEntry":None,\
                    "ControlPageSizeInSectors":None, "MIPPageSizeInSectors":None, "SLCFBLRatio": None, \
                    "mlcGrownDefects":None , "ZQ_CALP":None, "ZQ_CALN":None}

    configParams["phyChipIL"] = fileBuf.GetOneByteToInt(PHY_CHIP_IL)
    configParams["DieIL"] = fileBuf.GetOneByteToInt(DIE_IL)
    configParams["PlaneIL"] = fileBuf.GetOneByteToInt(PLANE_IL)
    configParams["bankSplitting"] = fileBuf.GetOneByteToInt(BANK_SPLITTING_OFFSET)
    configParams["numOfSlcFblBlocks"] = fileBuf.GetTwoBytesToInt(NUM_OF_SLC_FBL_BLOCKS)
    configParams["numOfSeqStream"] = fileBuf.GetOneByteToInt(NUM_SEQ_STREAMS)
    configParams["numOfRandomStream"] = fileBuf.GetOneByteToInt(NUM_RANDOM_STREAMS)
    configParams["minmlcFblLenght"] = fileBuf.GetOneByteToInt(MIN_MLC_FBL_LENGTH_OFFSET)
    configParams["maxmlcFblLenght"] = fileBuf.GetOneByteToInt(MAX_MLC_FBL_LENGTH_OFFSET)
    configParams["minbinaryFblLength"] = fileBuf.GetOneByteToInt(MIN_BINARY_FBL_LENGTH_OFFSET)
    configParams["maxbinaryFblLength"] = fileBuf.GetOneByteToInt(MAX_BINARY_FBL_LENGTH_OFFSET)
    configParams["numOfBlocksDedicatedFBL"] = fileBuf.GetOneByteToInt(NUM_BLOCKS_DEDICATED_FBL)
    configParams["numOfGATBlocks"] = fileBuf.GetTwoBytesToInt(NUM_GAT_BLOCKS)
    configParams["numOfRelocationStream"] = fileBuf.GetOneByteToInt(NUM_OF_RELOCATION_STREAMS)
    configParams["numofGATFblBlocks"] = fileBuf.GetOneByteToInt(NUM_OF_GAT_FBL_BLOCKS)
    configParams["shiftedWLValue"] = fileBuf.GetOneByteToInt(SHIFTED_WORDLINE)
    configParams["EFuseProductionData"] = fileBuf.GetFourBytesToInt(EFUSE_PRODUCTION_DATA)
    configParams["EFuseProcutionCrc"] = fileBuf.GetOneByteToInt(EFUSE_PRODUCTION_DATA+4)
    configParams["GatBlockDualWriteEnabled"] = fileBuf.GetOneByteToInt(GAT_BLOCK_DUAL_WRITE_ENABLE)
    configParams["GATDeltaMaxEntry"] = fileBuf.GetTwoBytesToInt(GAT_DELTA_MAX_ENTRY)
    configParams["GATDirDeltaMaxEntry"] = fileBuf.GetFourBytesToInt(GAT_DIR_DELTA_MAX_ENTRY)
    configParams["IGATDeltaMaxEntry"] = fileBuf.GetOneByteToInt(IGAT_DELTA_MAX_ENTRY)
    configParams["ControlPageSizeInSectors"] = fileBuf.GetOneByteToInt(CONTROL_PAGE_SIZE_IN_SECTORS)
    configParams["MIPPageSizeInSectors"] = fileBuf.GetOneByteToInt(MIP_PAGE_SIZE_IN_SECTORS)
    configParams["SLCFBLRatio"] = fileBuf.GetOneByteToInt(SLC_FBL_RATIO)
    configParams["mlcGrownDefects"] = fileBuf.GetOneByteToInt(MLC_GROWN_DEFECT)
    configParams["ZQ_CALP"] = fileBuf.GetOneByteToInt(ZQ_CALP)
    configParams["ZQ_CALN"] = fileBuf.GetOneByteToInt(ZQ_CALN)

    #Applicable only to reduced capacity FW
    configParams["NoOfZonesPerDie"] = fileBuf.GetOneByteToInt(NUM_ZONES_PER_DIE)
    configParams["TotalBadBlocksRequiredPerDie"] = fileBuf.GetTwoBytesToInt(TOTAL_BADBLOCKS_REQUIRED_PER_DIE)
    configParams["MaxAllowableBBPerZone"] = fileBuf.GetTwoBytesToInt(MAX_ALLOWABLE_BB_PER_ZONE)
    configParams["StartBlockPerZoneList"] = []

    for zone in range(configParams["NoOfZonesPerDie"]):
        configParams["StartBlockZone" + str(zone)] = fileBuf.GetTwoBytesToInt(START_BB_OFFSET_FIRST_ZONE+(zone*2))
        configParams["StartBlockPerZoneList"].append(configParams["StartBlockZone" + str(zone)])

    return configParams
#end Of File14Data

class ConfigurationFile23Data(object):
    """
    This class is used to read/parse/write configuration file (File 23) data
    """

    FILE_ID = 23

    #offsets
    FILE_23_TRIM_SET_OFFSET               = 0x0
    FILE_23_WRITE_DELAY_OFFSET            = 0x03
    FILE_23_READ_DELAY_OFFSET             = 0x04
    FILE_23_UNIT_DELAY_OFFSET             = 0x05
    FILE_23_TAPCOUNT_OFFSET               = 0x6
    FILE_23_MANUAL_LOCK_ENABLE_OFFSET     = 0xB

    FILE_23_SPEED_MODE_LS_OFFSET        = 0xC0
    FILE_23_LS_GC_QUOTA_READ_PER_4MB_Y  = 0xD2
    FILE_23_LS_GC_QUOTA_READ_PER_CMD_X  = 0xD4

    FILE_23_SPEED_MODE_HS_OFFSET        = 0xF0
    FILE_23_HS_GC_QUOTA_READ_PER_4MB_Y  = 0x102
    FILE_23_HS_GC_QUOTA_READ_PER_CMD_X  = 0x104   

    FILE_23_SPEED_MODE_SDR50_OFFSET        = 0x138
    FILE_23_SDR50_GC_QUOTA_READ_PER_4MB_Y  = 0x14A
    FILE_23_SDR50_GC_QUOTA_READ_PER_CMD_X  = 0x14C    


    FILE_23_SPEED_MODE_SDR104_OFFSET        = 0x150
    FILE_23_SDR104_GC_QUOTA_READ_PER_4MB_Y  = 0x162
    FILE_23_SDR104_GC_QUOTA_READ_PER_CMD_X  = 0x164   

    FILE_23_SPEED_MODE_DDR50_OFFSET        = 0x168
    FILE_23_DDR50_GC_QUOTA_READ_PER_4MB_Y  = 0x17A
    FILE_23_DDR50_GC_QUOTA_READ_PER_CMD_X  = 0x17C   

    FILE_23_SPEED_MODE_DDR200_OFFSET        = 0x180
    FILE_23_DDR200_GC_QUOTA_READ_PER_4MB_Y  = 0x192
    FILE_23_DDR200_GC_QUOTA_READ_PER_CMD_X  = 0x194   


    def __init__(self, vtfContainer):
        self.vtfContainer = vtfContainer
        self.Getfile23data()

    def DoFileRead(self,vtfContainer):
        """
        Name : __DoFileRead
        Description :
             This function read the lates Configuration File and return the buffer data
        Arguments :
            testSpace : testSpace of the card
        Return
               fileBuf     : file buffer
               fileSize    : file buffer size
        """
        fileSize, fileSizeBytes = DiagnosticLib.LengthOfFileInBytes(fileId=self.FILE_ID)
        fileBuf = DiagnosticLib.ReadFileSystem(vtfContainer, fileID=self.FILE_ID, sectorCount=fileSize)

        return fileBuf,fileSize

        #end of __DoFileRead
    def DoWriteFile(self,vtfContainer,fileBuf,fileSize):
        """
        Name : __DoWriteFile
        Description :
                 This function write the file data to card
        Arguments :
                testSpace   : testSpace of the card
                fileBuf     : file buffer
                fileSize    : file buffer size
        Return
               None
        """
        DiagnosticLib.WriteFileSystem(self.vtfContainer, fileID= self.FILE_ID,  sectorCount = fileSize, dataBuffer= fileBuf)

        return
        #end of __DoWriteFile

    def Getfile23data(self):

        fileBuf = DiagnosticLib.ReadFileSystem(self.vtfContainer, fileID=self.FILE_ID)

        self.speedmodelsoffset                = fileBuf.GetOneByteToInt(self.FILE_23_SPEED_MODE_LS_OFFSET)
        self.speedmodehsoffset                = fileBuf.GetOneByteToInt(self.FILE_23_SPEED_MODE_HS_OFFSET)
        self.speedmodesdr50offset             = fileBuf.GetOneByteToInt(self.FILE_23_SPEED_MODE_SDR50_OFFSET)
        self.speedmodesdr104offset            = fileBuf.GetOneByteToInt(self.FILE_23_SPEED_MODE_SDR104_OFFSET)
        self.speedmodeddr50offset             = fileBuf.GetOneByteToInt(self.FILE_23_SPEED_MODE_DDR50_OFFSET)
        self.speedmodeddr200offset            = fileBuf.GetOneByteToInt(self.FILE_23_SPEED_MODE_DDR200_OFFSET)
        self.trimsetoffset                    = fileBuf.GetOneByteToInt(self.FILE_23_TRIM_SET_OFFSET)
        self.writedelayoffset                 = fileBuf.GetOneByteToInt(self.FILE_23_WRITE_DELAY_OFFSET)
        self.readdelayoffset                  = fileBuf.GetOneByteToInt(self.FILE_23_READ_DELAY_OFFSET)
        self.unitdelayoffset                  = fileBuf.GetOneByteToInt(self.FILE_23_UNIT_DELAY_OFFSET)
        self.lstapcount                       = fileBuf.GetTwoBytesToInt(self.FILE_23_SPEED_MODE_LS_OFFSET + self.FILE_23_TAPCOUNT_OFFSET)
        self.hstapcount                       = fileBuf.GetTwoBytesToInt(self.FILE_23_SPEED_MODE_HS_OFFSET + self.FILE_23_TAPCOUNT_OFFSET)
        self.sdr50tapcount                    = fileBuf.GetTwoBytesToInt(self.FILE_23_SPEED_MODE_SDR50_OFFSET + self.FILE_23_TAPCOUNT_OFFSET)
        self.sdr104tapcount                   = fileBuf.GetTwoBytesToInt(self.FILE_23_SPEED_MODE_SDR104_OFFSET + self.FILE_23_TAPCOUNT_OFFSET)
        self.ddr50tapcount                    = fileBuf.GetTwoBytesToInt(self.FILE_23_SPEED_MODE_DDR50_OFFSET + self.FILE_23_TAPCOUNT_OFFSET)
        self.ddr200tapcount                   = fileBuf.GetTwoBytesToInt(self.FILE_23_SPEED_MODE_DDR200_OFFSET + self.FILE_23_TAPCOUNT_OFFSET)
        self.lsManualLockEnable               = fileBuf.GetOneByteToInt(self.FILE_23_SPEED_MODE_LS_OFFSET + self.FILE_23_MANUAL_LOCK_ENABLE_OFFSET)
        self.hsManualLockEnable               = fileBuf.GetOneByteToInt(self.FILE_23_SPEED_MODE_HS_OFFSET + self.FILE_23_MANUAL_LOCK_ENABLE_OFFSET)
        self.sdr50ManualLockEnable            = fileBuf.GetOneByteToInt(self.FILE_23_SPEED_MODE_SDR50_OFFSET + self.FILE_23_MANUAL_LOCK_ENABLE_OFFSET)
        self.sdr104ManualLockEnable           = fileBuf.GetOneByteToInt(self.FILE_23_SPEED_MODE_SDR104_OFFSET + self.FILE_23_MANUAL_LOCK_ENABLE_OFFSET)
        self.ddr50ManualLockEnable            = fileBuf.GetOneByteToInt(self.FILE_23_SPEED_MODE_DDR50_OFFSET + self.FILE_23_MANUAL_LOCK_ENABLE_OFFSET)
        self.ddr200ManualLockEnable           = fileBuf.GetOneByteToInt(self.FILE_23_SPEED_MODE_DDR200_OFFSET + self.FILE_23_MANUAL_LOCK_ENABLE_OFFSET)


        #In the y/x calculations related to RS GC --> below values are 'y'
        self.ReadQuotaPer4MBChunkForGC_SDR12 = self.ReadQuotaPer4MBChunkForGC_LS = fileBuf.GetTwoBytesToInt(self.FILE_23_LS_GC_QUOTA_READ_PER_4MB_Y)
        self.ReadQuotaPer4MBChunkForGC_SDR25 = self.ReadQuotaPer4MBChunkForGC_HS = fileBuf.GetTwoBytesToInt(self.FILE_23_HS_GC_QUOTA_READ_PER_4MB_Y)
        self.ReadQuotaPer4MBChunkForGC_SDR50  = fileBuf.GetTwoBytesToInt(self.FILE_23_SDR50_GC_QUOTA_READ_PER_4MB_Y)
        self.ReadQuotaPer4MBChunkForGC_SDR104 = fileBuf.GetTwoBytesToInt(self.FILE_23_SDR104_GC_QUOTA_READ_PER_4MB_Y)
        self.ReadQuotaPer4MBChunkForGC_DDR50  = fileBuf.GetTwoBytesToInt(self.FILE_23_DDR50_GC_QUOTA_READ_PER_4MB_Y)
        self.ReadQuotaPer4MBChunkForGC_DDR200 = fileBuf.GetTwoBytesToInt(self.FILE_23_DDR200_GC_QUOTA_READ_PER_4MB_Y)

        #In the y/x calculations related to RS GC --> below values are 'x'
        self.ReadQuotaPerCmdForGC_SDR12 = self.ReadQuotaPerCmdForGC_LS = fileBuf.GetOneByteToInt(self.FILE_23_LS_GC_QUOTA_READ_PER_CMD_X)
        self.ReadQuotaPerCmdForGC_SDR25 = self.ReadQuotaPerCmdForGC_HS = fileBuf.GetOneByteToInt(self.FILE_23_HS_GC_QUOTA_READ_PER_CMD_X)
        self.ReadQuotaPerCmdForGC_SDR50  = fileBuf.GetOneByteToInt(self.FILE_23_SDR50_GC_QUOTA_READ_PER_CMD_X)
        self.ReadQuotaPerCmdForGC_SDR104 = fileBuf.GetOneByteToInt(self.FILE_23_SDR104_GC_QUOTA_READ_PER_CMD_X)
        self.ReadQuotaPerCmdForGC_DDR50  = fileBuf.GetOneByteToInt(self.FILE_23_DDR50_GC_QUOTA_READ_PER_CMD_X)
        self.ReadQuotaPerCmdForGC_DDR200 = fileBuf.GetOneByteToInt(self.FILE_23_DDR200_GC_QUOTA_READ_PER_CMD_X)        

        return


class ConfigurationFile21Data(object):
    """
    This class is used to read/parse/write configuration file (File 21) data
    """

    FILE_ID = 21

    #offsets


    FILE_21_COMMON_BACKEND_FLASHWARE_FLAGS_OFFSET = 0X008
    FILE_21_ECC_CONTROL_FLAG_OFFSET = 0X00C
    FILE_21_CECC_LEVEL_REASSIGN_OFFSET = 0X0D
    FILE_21_CECC_LEVEL_REASSIGN_OFFSET_MLC = 0X0E
    FILE_21_WEARLEVEL_FREQUENCY_OFFSET = 0x1A
    FILE_21_WEARLEVEL_REMEMBRANCE_STRUCTURE_RESET = 0x149
    FILE_21_WEARLEVEL_COLDESTBLK_HC_DIFF_THRESHOLD_TO_TRIGGER_WL = 0x147     
    FILE_21_ENHANCED_WRITE_ABORT_MODE_OFFSET = 0x1F

    FILE_21_BALANCED_MLC_GC_THRESHOLD = 0x27
    FILE_21_URGENT_MLC_GC_THRESHOLD = 0x28
    FILE_21_SLC_COMPACTION_BALANCED_GC =0X32
    FILE_21_PLCC_THRESHOLD_OFFSET = 0X48
    FILE_21_MAX_BAD_BLOCKS_ALLOWED = 0x50
    #EPWR Offsets
    FILE_21_SLC_EPWR_SAFE_MARGIN = 0x52
    FILE_21_MLC_EPWR_SAFE_MARGIN = 0x53

    #Read cache
    FILE_21_SLC_MLC_READ_CACHE = 0x55
    FILE_21_CONTROL_BLOCK_READ_CACHE = 0x56

    #PF Configurability
    FILE_21_PF_CONFIGURATION = 0x59
    FILE_21_STOP_ON_X_PF_SLC = 0x5B
    FILE_21_STOP_ON_Y_EPWR_SLC = 0x5C
    FILE_21_STOP_ON_X_PF_MLC = 0x5D
    FILE_21_STOP_ON_Y_EPWR_MLC = 0x5E
    FILE_21_STOP_ON_Y_EPWR_GAT = 0x5F

    #Healthmeter Parameters 
    FILE_21_SLC_ENDURANCE = 0x1F7
    FILE_21_MLC_ENDURANCE = 0x1F9
    FILE_21_PROD_ENDURANCE = 0x1FB

    #Recheck :Max EPWR in a Block
    FILE_21_MAX_EPWR_FAILURE_IN_BLOCK_SLC = 0x5C
    FILE_21_MAX_EPWR_FAILURE_IN_BLOCK_MLC = 0x5E

    #MLC WA Scaning
    FILE_21_MLC_ZONE_BASED_SCANNING_ENABLE = 0x74
    FILE_21_NUMBER_OF_WL_ZONES             = 0x75
    FILE_21_WL_ZONES_INFO                  = 0x76

    #Configurable NLP and VPGM address
    FILE_21_CONFIGURABLE_NLP_ADDRESS               = 0x83
    FILE_21_CONFIGURABLE_VPGM_ADDRESS              = 0x85
    FILE_21_IS_NLP_SEQUENCE_ENABLED                = 0x86
    FILE21_CONFIG_PAGE_EPWR = 0X9E

    #Accelerated EPWR Chunk size
    FILE21_FRAGACCEPWR = 0XB1

    #UM offsets
    FILE_21_SEQ_WRITE_DETECTION_THRESHOLD_OFFSET = 0xB6
    FILE_21_FORWARD_JUMP_RANGE_OFFSET = 0xB8
    FILE_21_BACKWARD_JUMP_RANGE_OFFSET = 0xBA
    FILE_21_HOT_LBA_THRESHOLD_OFFSET = 0xBC
    FILE_21_SECTOR_INVALIDATION_THRESHOLD_OFFSET = 0xBE
    FILE_21_CLOSEST_RANGE_THRESHOLD_OFFSET = 0x9F

    FILE_21_CMDC6_ENABLE                    = 0xC0
    FILE_21_CMDC6_SAMPLING_WL_SLC           = 0xC1
    FILE_21_CMDC6_SAMPLING_WL_MLC           = 0xC2


    FILE_21_EPWR_DR_ENABLE = 0xCA

    FILE_21_COMMAND_PREDICTION_THRESHOLD = 0xD2

    #String based EPWR
    FILE_21_STRING_BASED_EPWR_ENABLE = 0xE4
    FILE_21_STRING_BASED_EPWR_SLC_STRING_START_OFFSET = 0xE5
    FILE_21_STRING_BASED_EPWR_MLC_STRING_START_OFFSET = 0xE8
    FILE_21_STRING_BASED_EPWR_GAT_STRING_START_OFFSET = 0xEB
    FILE_21_MLC_EPWR_BES_STAGE2_ENABLE_OFFSET = 0xF0
    FILE_21_RANDOM_GC_THRESHOLD = 0xFF

    #PGC Options 1
    FILE_21_PGC_GAT_COMPACTION_TIME = 0x109
    FILE_21_PGC_GAT_COMPACTION_STEP_SIZE = 0x10A

    #GC balancing Offsets
    FILE_21_COMMON_WEIGHTAGE_DENOMINATOR = 0x11A
    FILE_21_RELOCATION_WEIGHTAGE_NUMERATOR = 0x10C
    FILE_21_EPWR_WEIGHTAGE_NUMERATOR  = 0x10D
    FILE_21_GATCOMMIT_WEIGHTAGE_NUMERATOR = 0x10E
    FILE_21_ACCELERATED_GC_THRESHOLD = 0x10F
    FILE_21_ACCELERATED_GC_CHUNKSIZE = 0x110
    FILE_21_ACCELERATED_GC_MIN_CHUNK_THRESHOLD = 0x112
    FILE_21_ACCELERATED_GC_MAX_CHUNK_THRESHOLD = 0x116



    FILE_21_DOUBLE_ERASE_ENABLE = 0x12B

    FILE_21_MLC_PRIMARY_EPWR_THRESHOLD = 0x138
    FILE_21_MLC_SECONDARY_EPWR_THRESHOLD = 0x13A

    #Zone Based Adaptive ERC Offsets
    FILE_21_NUM_OF_SLC_ZONES             =       0x14E
    FILE_21_NUM_OF_TLC_ZONES             =       0x14F

    FILE_21_UPPER_ZONE_LIMIT_SLC_00      =       0x150
    FILE_21_UPPER_ZONE_LIMIT_SLC_01      =       0x151
    FILE_21_UPPER_ZONE_LIMIT_SLC_02      =       0x152
    FILE_21_UPPER_ZONE_LIMIT_SLC_03      =       0x153
    FILE_21_UPPER_ZONE_LIMIT_SLC_04      =       0x154
    FILE_21_UPPER_ZONE_LIMIT_SLC_05      =       0x155
    FILE_21_UPPER_ZONE_LIMIT_SLC_06      =       0x156
    FILE_21_UPPER_ZONE_LIMIT_SLC_07      =       0x157
    FILE_21_UPPER_ZONE_LIMIT_SLC_08      =       0x158
    FILE_21_UPPER_ZONE_LIMIT_SLC_09      =       0x159
    FILE_21_UPPER_ZONE_LIMIT_SLC_10      =       0x15A
    FILE_21_UPPER_ZONE_LIMIT_SLC_11      =       0x15B
    FILE_21_UPPER_ZONE_LIMIT_SLC_12      =       0x15C
    FILE_21_UPPER_ZONE_LIMIT_SLC_13      =       0x15D
    FILE_21_UPPER_ZONE_LIMIT_SLC_14      =       0x15E
    FILE_21_UPPER_ZONE_LIMIT_SLC_15      =       0x15F

    FILE_21_UPPER_ZONE_LIMIT_TLC_00      =       0x160
    FILE_21_UPPER_ZONE_LIMIT_TLC_01      =       0x161
    FILE_21_UPPER_ZONE_LIMIT_TLC_02      =       0x162
    FILE_21_UPPER_ZONE_LIMIT_TLC_03      =       0x163
    FILE_21_UPPER_ZONE_LIMIT_TLC_04      =       0x164
    FILE_21_UPPER_ZONE_LIMIT_TLC_05      =       0x165
    FILE_21_UPPER_ZONE_LIMIT_TLC_06      =       0x166
    FILE_21_UPPER_ZONE_LIMIT_TLC_07      =       0x167
    FILE_21_UPPER_ZONE_LIMIT_TLC_08      =       0x168
    FILE_21_UPPER_ZONE_LIMIT_TLC_09      =       0x169
    FILE_21_UPPER_ZONE_LIMIT_TLC_10      =       0x16A
    FILE_21_UPPER_ZONE_LIMIT_TLC_11      =       0x16B
    FILE_21_UPPER_ZONE_LIMIT_TLC_12      =       0x16C
    FILE_21_UPPER_ZONE_LIMIT_TLC_13      =       0x16D
    FILE_21_UPPER_ZONE_LIMIT_TLC_14      =       0x16E
    FILE_21_UPPER_ZONE_LIMIT_TLC_15      =       0x16F


    FILE_21_SLC_VPGM_SHIFT_ENABLED = 0x190
    FILE_21_SLC_ADAPTIVE_TRIM_COUNT = 0x191  #LMB_CC Change
    FILE_21_SLC_ADAPTIVE_TRIM_MULTIPLIER = 0x192
    FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_1ST_LIMIT = 0x194
    FILE_21_SLC_ADATIVE_TRIM_DAC_1ST_LIMIT = 0x195
    FILE_21_SLC_ADATIVE_TRIM_NLP_1ST_LIMIT = 0x196
    FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_2ND_LIMIT = 0x197
    FILE_21_SLC_ADATIVE_TRIM_DAC_2ND_LIMIT = 0x198
    FILE_21_SLC_ADATIVE_TRIM_NLP_2ND_LIMIT = 0x199
    FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_3RD_LIMIT = 0x19A
    FILE_21_SLC_ADATIVE_TRIM_DAC_3RD_LIMIT = 0x19B
    FILE_21_SLC_ADATIVE_TRIM_NLP_3RD_LIMIT = 0x19C
    FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_4TH_LIMIT = 0x19D
    FILE_21_SLC_ADATIVE_TRIM_DAC_4TH_LIMIT = 0x19E
    FILE_21_SLC_ADATIVE_TRIM_NLP_4TH_LIMIT = 0x19F
    FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_5TH_LIMIT = 0x1A0
    FILE_21_SLC_ADATIVE_TRIM_DAC_5TH_LIMIT = 0x1A1
    FILE_21_SLC_ADATIVE_TRIM_NLP_5TH_LIMIT = 0x1A2
    FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_6TH_LIMIT = 0x1A3
    FILE_21_SLC_ADATIVE_TRIM_DAC_6TH_LIMIT = 0x1A4
    FILE_21_SLC_ADATIVE_TRIM_NLP_6TH_LIMIT = 0x1A5
    FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_7TH_LIMIT = 0x1A6
    FILE_21_SLC_ADATIVE_TRIM_DAC_7TH_LIMIT = 0x1A7
    FILE_21_SLC_ADATIVE_TRIM_NLP_7TH_LIMIT = 0x1A8
    FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_8TH_LIMIT = 0x1A9
    FILE_21_SLC_ADATIVE_TRIM_DAC_8TH_LIMIT = 0x1AA
    FILE_21_SLC_ADATIVE_TRIM_NLP_8TH_LIMIT = 0x1AB
    FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_9TH_LIMIT = 0x1AC
    FILE_21_SLC_ADATIVE_TRIM_DAC_9TH_LIMIT = 0x1AD
    FILE_21_SLC_ADATIVE_TRIM_NLP_9TH_LIMIT = 0x1AE
    FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_10TH_LIMIT = 0x1AF
    FILE_21_SLC_ADATIVE_TRIM_DAC_10TH_LIMIT = 0x1B0
    FILE_21_SLC_ADATIVE_TRIM_NLP_10TH_LIMIT = 0x1B1
    FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_11TH_LIMIT = 0x1B2
    FILE_21_SLC_ADATIVE_TRIM_DAC_11TH_LIMIT = 0x1B3
    FILE_21_SLC_ADATIVE_TRIM_NLP_11TH_LIMIT = 0x1B4

    #PGC OPTIONS2
    FILE_21_PGC_GAT_PHASED_EPWR_TIME    = 0x1B8
    FILE_21_PGC_READ_SCRUB_TIME         = 0x1B9
    FILE_21_PGC_GCC_PHASED_COMMIT_TIME  = 0x1BA
    FILE_21_PGC_GAT_FLUSH_TIME          = 0x1BB #0x101
    FILE_21_PGC_GAT_SYNC_TIME           = 0x1BC

    FILE_21_SLC_COMPACTION_EARLY1_GC = 0X1BD
    FILE_21_SLC_COMPACTION_EARLY2_GC = 0x1BE

    #PGC Quota values
    FILE_21_PGC_GCC_PHASED_GC_TIME        = 0x1E2
    FILE_21_PGC_GCC_PHASED_PC_COMMIT_TIME = 0x1E3
    FILE_21_PGC_GCC_PHASED_PC_WA_TIME     = 0x1E5 #FILE_21_PGC_GCCPhasedPCCommitTimeMs + 1
    FILE_21_PGC_GCC_PHASED_EPWR_TIME      = 0x1E6 #FILE_21_PGC_GCCPhasedPCWATimeMs + 1
    FILE_21_PGC_HOST_EPWR_TIME            = 0x1F6

    #CMD B2
    FILE_21_CMDB2ENABLE = 0x100

    def __init__(self,vtfContainer):
        """
        Name : __init__
        Description :
                 Constructor of the class. It calls RefessData() function for getting all the variables
        Arguments :
                vtfContainer : vtfContainer of the card

        Return
             None
        """
        self.vtfContainer = vtfContainer
        self.__fwConfigObj =    FwConfig.FwConfig(vtfContainer)
        self.__fwFeatureConfigObj = FwConfig.FwFeatureConfig(self.vtfContainer)
        self.spcbEnabled = self.__fwFeatureConfigObj.isSpcbEnabled
        # Initialize all the configuration file variables (to remove pylintm error and to access these variables from Wing-IDE)
        self.commonBEFlashwareFlags          = None
        self.plccThreshold                   = None
        self.eccControlFlag                  = None
        self.ceccLevelForReassign            = None
        self.ceccLevelForReassignMlc         = None
        self.WlFreq                          = None
        self.mlcDynamicReadFlag              = None
        self.slcDynamicReadFlagType1         = None
        self.slcDynamicReadFlagType2         = None
        self.enhancedWriteAbortModeFlag      = None
        self.epwrMlcThreshold                = None
        self.epwrSlcThreshold                = None
        self.secondaryepwrMlcThreshold       = None

        self.spcbEnable                    = None
        self.epwrSLCSafeMargin             = None
        self.epwrMLCSafeMargin             = None
        self.lowerPageEpwrEnable           = None
        self.middlePageEpwrEnable          = None
        self.upperPageEpwrEnable           = None
        self.fragAcceleratedEpwr           = None

        self.configurableNLPAddress = None
        self.configurableVPGMAddress = None
        self.isNLPSequenceEnabled = None

        self.slcEndurance                   = None 
        self.mlcEndurance                   = None
        self.productEndurance               = None
        self.maxBadBlockCount               = None
        self.maxEPWRFailureinBlockSlc       = None
        self.maxEPWRFailureinBlockMlc       = None
        self.seqWriteDetectionThreshold     = None
        self.slcVpgmShiftEnabled            = None
        self.slcAdaptiveTrimCount           = None
        self.slcAdaptiveTrimMultiplier      = None
        self.adaptiveTrimThreshold1         = None
        self.adaptiveTrimDAC1               = None
        self.adaptiveTrimNLP1               = None
        self.adaptiveTrimThreshold2         = None
        self.adaptiveTrimDAC2               = None
        self.adaptiveTrimNLP2               = None
        self.adaptiveTrimThreshold3         = None
        self.adaptiveTrimDAC3               = None
        self.adaptiveTrimNLP3               = None
        self.adaptiveTrimThreshold4         = None
        self.adaptiveTrimDAC4               = None
        self.adaptiveTrimNLP4               = None
        self.adaptiveTrimThreshold5         = None
        self.adaptiveTrimDAC5               = None
        self.adaptiveTrimNLP5               = None
        self.adaptiveTrimThreshold6         = None
        self.adaptiveTrimDAC6               = None
        self.adaptiveTrimNLP6               = None
        self.adaptiveTrimThreshold7         = None
        self.adaptiveTrimDAC7               = None
        self.adaptiveTrimNLP7               = None
        self.adaptiveTrimThreshold8         = None
        self.adaptiveTrimDAC8               = None
        self.adaptiveTrimNLP8               = None
        self.adaptiveTrimThreshold9         = None
        self.adaptiveTrimDAC9               = None
        self.adaptiveTrimNLP9               = None
        self.adaptiveTrimThreshold10        = None
        self.adaptiveTrimDAC10              = None
        self.adaptiveTrimNLP10              = None
        self.adaptiveTrimThreshold11        = None
        self.adaptiveTrimDAC11              = None
        self.adaptiveTrimNLP11              = None
        self.slcCompactionEarly1Threshold   = None
        self.slcCompactionEarly2Threshold   = None
        self.slcCompactionBalancedThreshold = None

        self.doubleEraseEnable              = None
        self.numSLCWLToSkip                 = None

        self.cmdC6Enable                  =       None
        self.cmdC6EnableSlc               =       None
        self.cmdC6EnableMlc               =       None

        self.cmdc6SamplingWLSLC           =       None
        self.cmdc6SamplingWLMLC           =       None

        #Adaptive ERC
        self.NumZonesUsedForSLC           =       None
        self.NumZonesUsedForTLC           =       None

        self.UpperZoneLimitForSLC_00      =       None
        self.UpperZoneLimitForSLC_01      =       None
        self.UpperZoneLimitForSLC_02      =       None
        self.UpperZoneLimitForSLC_03      =       None
        self.UpperZoneLimitForSLC_04      =       None
        self.UpperZoneLimitForSLC_05      =       None
        self.UpperZoneLimitForSLC_06      =       None
        self.UpperZoneLimitForSLC_07      =       None
        self.UpperZoneLimitForSLC_08      =       None
        self.UpperZoneLimitForSLC_09      =       None
        self.UpperZoneLimitForSLC_10      =       None
        self.UpperZoneLimitForSLC_11      =       None
        self.UpperZoneLimitForSLC_12      =       None
        self.UpperZoneLimitForSLC_13      =       None
        self.UpperZoneLimitForSLC_14      =       None
        self.UpperZoneLimitForSLC_15      =       None

        self.UpperZoneLimitForTLC_00      =       None
        self.UpperZoneLimitForTLC_01      =       None
        self.UpperZoneLimitForTLC_02      =       None
        self.UpperZoneLimitForTLC_03      =       None
        self.UpperZoneLimitForTLC_04      =       None
        self.UpperZoneLimitForTLC_05      =       None
        self.UpperZoneLimitForTLC_06      =       None
        self.UpperZoneLimitForTLC_07      =       None
        self.UpperZoneLimitForTLC_08      =       None
        self.UpperZoneLimitForTLC_09      =       None
        self.UpperZoneLimitForTLC_10      =       None
        self.UpperZoneLimitForTLC_11      =       None
        self.UpperZoneLimitForTLC_12      =       None
        self.UpperZoneLimitForTLC_13      =       None
        self.UpperZoneLimitForTLC_14      =       None
        self.UpperZoneLimitForTLC_15      =       None

        # String Based EPWR Offsets (RPG-32083
        self.StringBasedEpwrEnableSLC = None
        self.StringBasedEpwrEnableMLC = None
        self.StringBasedEpwrEnableGAT = None

        self.StringBasedEpwrSlcStringList = [None] * self.__fwConfigObj.stringsPerBlock # 4 strings in BiCS4
        self.StringBasedEpwrMlcStringList = [None] * self.__fwConfigObj.stringsPerBlock # 4 strings in BiCS4
        self.StringBasedEpwrGatStringList = [None] * self.__fwConfigObj.stringsPerBlock # 4 strings in BiCS4


        # MLC WA Scaning
        self.isMLCZoneBasedWAScanningEnbale = False
        self.NumberOfWLZones                = None
        self.WLZonesRange                   = {}

        # PF Congirability
        self.StopOnXPFSlc = None
        self.StopOnXPFMlc = None
        self.StopOnYEpwrSlc = None
        self.StopOnYEpwrMlc = None
        self.StopOnYEpwrGat = None

        self.PfConfigurationSlc = None
        self.PfConfigurationMlc = None
        self.PfConfigurationGat = None
        self.PfConfigurationMip = None

        self.PfConfiguration = None
        self.BalancedGCThreshold = None
        self.MLCEPWRBESStage2Enabled = None
        self.CmdB2Enable = None
        #PGC Quota Variables
        #self.PGCQuotaValues_Dict = {
            #'GCC_IDLE' : None,
            #'GCC_PHASED_GC_IN_PROGRESS' : None,
            #'GCC_PHASED_PADDING'    : None,
            #'GCC_PHASED_PRIMAY_PADDING' : None,
            #'GCC_PHASED_SECONDARY_PADDING' : None,
            #'GCC_PHASED_EPWR' : None,
            #'GCC_HANDLE_PC_WA' : None,
            #'GCC_PC_RGAT_COMMIT' : None,
            #'GCC_DEST_EXCHANGE' : None,
            #'GCC_PHASED_PC_COMMITS' : None,
            #'GCC_PHASED_COMMIT': None,
            #'GCC_Last': None,
            #}

        # Extreme 2TB
        self.PGCQuotaValues_Dict = {
            'GCC_IDLE' :None,
            'GCC_PHASED_GC_IN_PROGRESS' : None,
            'GCC_PHASED_PADDING' : None,
            'GCC_HANDLE_PC_WA' : None,
            'GCC_DEST_EXCHANGE' : None,
            'GCC_PHASED_PC_COMMITS' : None,
            'GCC_PHASED_COMMIT': None,
            'GCC_Last' : None
            #'GCC_INVALID_STATE' = MAX_UINT8
        }


        #calling refresh data function for getting all configuration values
        self.RefreshData(vtfContainer)
    #end of __init__

    def RefreshData(self,vtfContainer):
        """
        Name : RefreshData
        Description :
                 This function read the latest Configuration File and update all the configuration data
        Arguments :
                vtfContainer : vtfContainer of the card
        Return
             None
        """
        #read the file data
        fileBuf,fileSize = self.__DoFileRead(vtfContainer)

        #Parse the Configuration data from the file buffer
        self.__ParseConfigurationData(fileBuf)
    #end of RefreshData


    def SetWLFlag(self,vtfContainer,SetWLFlag = True):
        """
        Name : SetWLFlag
        Description :
                 It is used to set/clear the bit in File21 to enable/disable the Wear Levelling option
        Arguments :
                vtfContainer   :  vtfContainer
                SetWLFlag   :  True or False to enable/disable the Wear Levelling option
        Return
             None
        """
        DISABLE_WL_OPTION = 0xFBF7 #Bit 3(MLC Blocks) & Bit 10(SLC Blocks)
        ENABLE_WL_OPTION = 0x0408

        #read the file data
        fileBuf,fileSize = self.__DoFileRead(vtfContainer)

        #Parse the file data
        self.__ParseConfigurationData(fileBuf)

        #Enabling or Disabling Wear Levelling option
        if (SetWLFlag == True):
            finalWLControlFlag = (self.commonBEFlashwareFlags | ENABLE_WL_OPTION ) #Enable the WL
        else:
            finalWLControlFlag = (self.commonBEFlashwareFlags & DISABLE_WL_OPTION ) #disable the WL

        #set this byte in
        fileBuf.SetTwoBytes(self.FILE_21_COMMON_BACKEND_FLASHWARE_FLAGS_OFFSET,finalWLControlFlag)

        #do write file
        self.__DoWriteFile(vtfContainer,fileBuf,fileSize)

        #Doing a Power Cycle
        import Validation.Utils as Utils
        Utils.PowerCycle(vtfContainer)
    #end of SetWLFlag

    def __ParseConfigurationData(self,fileBuf):
        """
        Name : __ParseConfigurationData
        Description :
                 This function parse the data from file buffer
        Arguments :
                fileBuf   : configuration file buffer
        Return
             None
        """
        #???? Why are constants class variable?
        #Parsing the data
        #Recheck: SPCB  & Sting Based EPWR default values in Felix
        self.spcbEnable                      = self.spcbEnabled #fileBuf.GetOneByteToInt(self.FILE21_SPCB_ENABLE)
        self.numSLCWLToSkip                  = 0 # fileBuf.GetOneByteToInt(self.FILE_21_NUM_SLC_WLTOSKIP)
        self.isSinglePageEPWREnabled         = fileBuf.GetOneByteToInt(self.FILE21_CONFIG_PAGE_EPWR) & 0x7

        self.commonBEFlashwareFlags          = fileBuf.GetTwoBytesToInt(self.FILE_21_COMMON_BACKEND_FLASHWARE_FLAGS_OFFSET)
        self.plccThreshold                   = fileBuf.GetOneByteToInt(self.FILE_21_PLCC_THRESHOLD_OFFSET)
        self.eccControlFlag                  = fileBuf.GetOneByteToInt(self.FILE_21_ECC_CONTROL_FLAG_OFFSET)
        self.ceccLevelForReassign            = fileBuf.GetOneByteToInt(self.FILE_21_CECC_LEVEL_REASSIGN_OFFSET)
        self.ceccLevelForReassignMlc         = fileBuf.GetOneByteToInt(self.FILE_21_CECC_LEVEL_REASSIGN_OFFSET_MLC)
        self.seqWriteDetectionThreshold      = fileBuf.GetTwoBytesToInt(self.FILE_21_SEQ_WRITE_DETECTION_THRESHOLD_OFFSET)
        self.ForwardJumpRange                = fileBuf.GetTwoBytesToInt(self.FILE_21_FORWARD_JUMP_RANGE_OFFSET)
        self.BackwardJumpRange               = fileBuf.GetTwoBytesToInt(self.FILE_21_BACKWARD_JUMP_RANGE_OFFSET)
        self.HotLbaThreshold                 = fileBuf.GetTwoBytesToInt(self.FILE_21_HOT_LBA_THRESHOLD_OFFSET)
        self.sectorInvalidationThreshold     = fileBuf.GetTwoBytesToInt(self.FILE_21_SECTOR_INVALIDATION_THRESHOLD_OFFSET)
        self.closestRangeThreshold           = fileBuf.GetTwoBytesToInt(self.FILE_21_CLOSEST_RANGE_THRESHOLD_OFFSET)
        self.WlFreq                          = fileBuf.GetOneByteToInt(self.FILE_21_WEARLEVEL_FREQUENCY_OFFSET)
        self.epwrMlcThreshold                = fileBuf.GetTwoBytesToInt(self.FILE_21_MLC_PRIMARY_EPWR_THRESHOLD) #& self.FILE_21_EPWR_MLC_THRESHOLD_MASK
        self.secondaryepwrMlcThreshold       = fileBuf.GetTwoBytesToInt(self.FILE_21_MLC_SECONDARY_EPWR_THRESHOLD)

        self.epwrSLCSafeMargin             = fileBuf.GetOneByteToInt(self.FILE_21_SLC_EPWR_SAFE_MARGIN)
        self.epwrMLCSafeMargin             = fileBuf.GetOneByteToInt(self.FILE_21_MLC_EPWR_SAFE_MARGIN)

        self.HostReadCacheEnabled            = fileBuf.GetOneByteToInt(self.FILE_21_SLC_MLC_READ_CACHE)
        self.ControlReadCacheEnabled         = fileBuf.GetOneByteToInt(self.FILE_21_CONTROL_BLOCK_READ_CACHE)

        self.BalancedGCThreshold             = fileBuf.GetOneByteToInt(self.FILE_21_BALANCED_MLC_GC_THRESHOLD)
        self.UrgentGCThreshold               = fileBuf.GetOneByteToInt(self.FILE_21_URGENT_MLC_GC_THRESHOLD)
        self.RandomGCThreshold               = fileBuf.GetOneByteToInt(self.FILE_21_RANDOM_GC_THRESHOLD)
        #To recheck : currently hardcoded in FW
        self.AccleratedGCThreshold           = fileBuf.GetOneByteToInt(self.FILE_21_ACCELERATED_GC_THRESHOLD)
        self.commondenominator               = float(fileBuf.GetOneByteToInt(self.FILE_21_COMMON_WEIGHTAGE_DENOMINATOR))
        self.EPWRWeightageNumerator          = fileBuf.GetOneByteToInt(self.FILE_21_EPWR_WEIGHTAGE_NUMERATOR)
        self.RelocationWeightageNumerator    = fileBuf.GetOneByteToInt(self.FILE_21_RELOCATION_WEIGHTAGE_NUMERATOR)
        self.GatCommitWeightageNumerator     = fileBuf.GetOneByteToInt(self.FILE_21_GATCOMMIT_WEIGHTAGE_NUMERATOR)
        self.GCBalancingminChunkThreshold    = fileBuf.GetOneByteToInt(self.FILE_21_ACCELERATED_GC_MIN_CHUNK_THRESHOLD)
        self.GCBalancingmaxChunkThreshold    = fileBuf.GetOneByteToInt(self.FILE_21_ACCELERATED_GC_MAX_CHUNK_THRESHOLD)

        self.slcEndurance                      = fileBuf.GetTwoBytesToInt(self.FILE_21_SLC_ENDURANCE)     
        self.mlcEndurance                      = fileBuf.GetTwoBytesToInt(self.FILE_21_MLC_ENDURANCE)      
        self.productEndurance                  = fileBuf.GetTwoBytesToInt(self.FILE_21_PROD_ENDURANCE)
        self.WlRemembranceStructResetThreshold = fileBuf.GetTwoBytesToInt(self.FILE_21_WEARLEVEL_REMEMBRANCE_STRUCTURE_RESET)
        self.WlColdestBlkHcDiffThresholdToTriggerWL = fileBuf.GetTwoBytesToInt(self.FILE_21_WEARLEVEL_COLDESTBLK_HC_DIFF_THRESHOLD_TO_TRIGGER_WL)         

        if self.commondenominator !=0.0 :
            self.RelocationWeightage             = old_div(self.RelocationWeightageNumerator,self.commondenominator)
            self.GCEpwrWeightage                 = old_div(self.EPWRWeightageNumerator,self.commondenominator)
            self.GCGatCommitWeightage            = old_div(self.GatCommitWeightageNumerator,self.commondenominator)
        else:
            #hardcoded values
            self.RelocationWeightage             = 0.6
            self.GCEpwrWeightage                 = 0.2
            self.GCGatCommitWeightage            = 0.2

        self.doubleEraseEnable                  = fileBuf.GetOneByteToInt(self.FILE_21_DOUBLE_ERASE_ENABLE)

        #if isSinglePageEPWREnabled is 0x0 then EPWR will be done for all MLC levels
        if not self.isSinglePageEPWREnabled or self.isSinglePageEPWREnabled == 0x7:
            self.lowerPageEpwrEnable           = 1
            self.middlePageEpwrEnable          = 1
            self.upperPageEpwrEnable           = 1
            self.isSinglePageEPWREnabled       = 0
        else:
            self.lowerPageEpwrEnable           = fileBuf.GetOneByteToInt(self.FILE21_CONFIG_PAGE_EPWR) & 1
            self.middlePageEpwrEnable          = (fileBuf.GetOneByteToInt(self.FILE21_CONFIG_PAGE_EPWR) & 2 )>>1
            self.upperPageEpwrEnable           = (fileBuf.GetOneByteToInt(self.FILE21_CONFIG_PAGE_EPWR) & 4)>>2

        self.fragAcceleratedEpwr             = fileBuf.GetTwoBytesToInt(self.FILE21_FRAGACCEPWR)
        self.enhancedWriteAbortModeFlag      = fileBuf.GetOneByteToInt(self.FILE_21_ENHANCED_WRITE_ABORT_MODE_OFFSET)

        #Configurable NLP and VPGM address
        self.configurableNLPAddress     = fileBuf.GetTwoBytesToInt(self.FILE_21_CONFIGURABLE_NLP_ADDRESS)
        self.configurableVPGMAddress    = fileBuf.GetOneByteToInt(self.FILE_21_CONFIGURABLE_VPGM_ADDRESS)
        self.isNLPSequenceEnabled       = fileBuf.GetOneByteToInt(self.FILE_21_IS_NLP_SEQUENCE_ENABLED)

        self.maxBadBlockCount            =fileBuf.GetTwoBytesToInt(self.FILE_21_MAX_BAD_BLOCKS_ALLOWED)
        self.maxEPWRFailureinBlockSlc       =fileBuf.GetOneByteToInt(self.FILE_21_MAX_EPWR_FAILURE_IN_BLOCK_SLC)
        self.maxEPWRFailureinBlockMlc       =fileBuf.GetOneByteToInt(self.FILE_21_MAX_EPWR_FAILURE_IN_BLOCK_MLC)
        self.slcVpgmShiftEnabled            = fileBuf.GetOneByteToInt(self.FILE_21_SLC_VPGM_SHIFT_ENABLED)
        self.slcAdaptiveTrimCount           = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADAPTIVE_TRIM_COUNT)
        self.slcAdaptiveTrimMultiplier      = fileBuf.GetTwoBytesToInt(self.FILE_21_SLC_ADAPTIVE_TRIM_MULTIPLIER)
        self.adaptiveTrimThreshold1         = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_1ST_LIMIT)
        self.adaptiveTrimDAC1               = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_DAC_1ST_LIMIT)
        self.adaptiveTrimNLP1               = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_NLP_1ST_LIMIT)
        self.adaptiveTrimThreshold2         = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_2ND_LIMIT)
        self.adaptiveTrimDAC2               = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_DAC_2ND_LIMIT)
        self.adaptiveTrimNLP2               = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_NLP_2ND_LIMIT)
        self.adaptiveTrimThreshold3         = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_3RD_LIMIT)
        self.adaptiveTrimDAC3               = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_DAC_3RD_LIMIT)
        self.adaptiveTrimNLP3               = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_NLP_3RD_LIMIT)
        self.adaptiveTrimThreshold4         = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_4TH_LIMIT)
        self.adaptiveTrimDAC4               = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_DAC_4TH_LIMIT)
        self.adaptiveTrimNLP4               = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_NLP_4TH_LIMIT)
        self.adaptiveTrimThreshold5         = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_5TH_LIMIT)
        self.adaptiveTrimDAC5               = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_DAC_5TH_LIMIT)
        self.adaptiveTrimNLP5               = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_NLP_5TH_LIMIT)
        self.adaptiveTrimThreshold6         = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_6TH_LIMIT)
        self.adaptiveTrimDAC6               = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_DAC_6TH_LIMIT)
        self.adaptiveTrimNLP6               = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_NLP_6TH_LIMIT)
        self.adaptiveTrimThreshold7         = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_7TH_LIMIT)
        self.adaptiveTrimDAC7               = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_DAC_7TH_LIMIT)
        self.adaptiveTrimNLP7               = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_NLP_7TH_LIMIT)
        self.adaptiveTrimThreshold8         = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_8TH_LIMIT)
        self.adaptiveTrimDAC8               = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_DAC_8TH_LIMIT)
        self.adaptiveTrimNLP8               = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_NLP_8TH_LIMIT)
        self.adaptiveTrimThreshold9         = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_9TH_LIMIT)
        self.adaptiveTrimDAC9               = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_DAC_9TH_LIMIT)
        self.adaptiveTrimNLP9               = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_NLP_9TH_LIMIT)
        self.adaptiveTrimThreshold10        = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_10TH_LIMIT)
        self.adaptiveTrimDAC10              = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_DAC_10TH_LIMIT)
        self.adaptiveTrimNLP10              = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_NLP_10TH_LIMIT)
        self.adaptiveTrimThreshold11        = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_THRESHOLD_11TH_LIMIT)
        self.adaptiveTrimDAC11              = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_DAC_11TH_LIMIT)
        self.adaptiveTrimNLP11              = fileBuf.GetOneByteToInt(self.FILE_21_SLC_ADATIVE_TRIM_NLP_11TH_LIMIT)

        self.slcCompactionEarly1Threshold   = fileBuf.GetOneByteToInt(self.FILE_21_SLC_COMPACTION_EARLY1_GC)
        self.slcCompactionEarly2Threshold   = fileBuf.GetOneByteToInt(self.FILE_21_SLC_COMPACTION_EARLY2_GC)
        self.slcCompactionBalancedThreshold = fileBuf.GetOneByteToInt(self.FILE_21_SLC_COMPACTION_BALANCED_GC)


        self.cmdC6Enable                  =       fileBuf.GetOneByteToInt(self.FILE_21_CMDC6_ENABLE)
        self.cmdC6EnableSlc               =       (self.cmdC6Enable & 0x1)
        self.cmdC6EnableMlc               =       (self.cmdC6Enable >> 4) & 0x1
        self.cmdc6SamplingWLSLC           =       fileBuf.GetOneByteToInt(self.FILE_21_CMDC6_SAMPLING_WL_SLC)
        self.cmdc6SamplingWLMLC           =       fileBuf.GetOneByteToInt(self.FILE_21_CMDC6_SAMPLING_WL_MLC)

        self.mlcEPWRDREnable              =       fileBuf.GetOneByteToInt(self.FILE_21_EPWR_DR_ENABLE) & 1
        self.slcEPWRDREnable              =       fileBuf.GetOneByteToInt(self.FILE_21_EPWR_DR_ENABLE) & 2

        #Adaptive ERC
        self.NumZonesUsedForSLC           =       fileBuf.GetOneByteToInt(self.FILE_21_NUM_OF_SLC_ZONES)
        self.NumZonesUsedForTLC           =       fileBuf.GetOneByteToInt(self.FILE_21_NUM_OF_TLC_ZONES)

        self.UpperZoneLimitForSLC_0       =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_SLC_00)
        self.UpperZoneLimitForSLC_1       =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_SLC_01)
        self.UpperZoneLimitForSLC_2       =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_SLC_02)
        self.UpperZoneLimitForSLC_3       =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_SLC_03)
        self.UpperZoneLimitForSLC_4       =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_SLC_04)
        self.UpperZoneLimitForSLC_5       =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_SLC_05)
        self.UpperZoneLimitForSLC_6       =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_SLC_06)
        self.UpperZoneLimitForSLC_7       =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_SLC_07)
        self.UpperZoneLimitForSLC_8       =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_SLC_08)
        self.UpperZoneLimitForSLC_9       =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_SLC_09)
        self.UpperZoneLimitForSLC_10      =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_SLC_10)
        self.UpperZoneLimitForSLC_11      =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_SLC_11)
        self.UpperZoneLimitForSLC_12      =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_SLC_12)
        self.UpperZoneLimitForSLC_13      =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_SLC_13)
        self.UpperZoneLimitForSLC_14      =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_SLC_14)
        self.UpperZoneLimitForSLC_15      =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_SLC_15)

        self.UpperZoneLimitForTLC_0       =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_TLC_00)
        self.UpperZoneLimitForTLC_1       =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_TLC_01)
        self.UpperZoneLimitForTLC_2       =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_TLC_02)
        self.UpperZoneLimitForTLC_3       =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_TLC_03)
        self.UpperZoneLimitForTLC_4       =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_TLC_04)
        self.UpperZoneLimitForTLC_5       =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_TLC_05)
        self.UpperZoneLimitForTLC_6       =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_TLC_06)
        self.UpperZoneLimitForTLC_7       =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_TLC_07)
        self.UpperZoneLimitForTLC_8       =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_TLC_08)
        self.UpperZoneLimitForTLC_9       =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_TLC_09)
        self.UpperZoneLimitForTLC_10      =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_TLC_10)
        self.UpperZoneLimitForTLC_11      =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_TLC_11)
        self.UpperZoneLimitForTLC_12      =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_TLC_12)
        self.UpperZoneLimitForTLC_13      =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_TLC_13)
        self.UpperZoneLimitForTLC_14      =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_TLC_14)
        self.UpperZoneLimitForTLC_15      =       fileBuf.GetOneByteToInt(self.FILE_21_UPPER_ZONE_LIMIT_TLC_15)

        # Pf Configurability
        self.StopOnXPFSlc = fileBuf.GetOneByteToInt(self.FILE_21_STOP_ON_X_PF_SLC)
        self.StopOnXPFMlc = fileBuf.GetOneByteToInt (self.FILE_21_STOP_ON_X_PF_MLC)
        self.StopOnYEpwrSlc = fileBuf.GetOneByteToInt (self.FILE_21_STOP_ON_Y_EPWR_SLC)
        self.StopOnYEpwrMlc = fileBuf.GetOneByteToInt (self.FILE_21_STOP_ON_Y_EPWR_MLC)
        self.StopOnYEpwrGat = fileBuf.GetOneByteToInt (self.FILE_21_STOP_ON_Y_EPWR_GAT)
        self.PfConfiguration = fileBuf.GetOneByteToInt (self.FILE_21_PF_CONFIGURATION)
        self.PfConfigurationSlc = fileBuf.GetOneByteToInt (self.FILE_21_PF_CONFIGURATION) & 0x3
        self.PfConfigurationMlc = (fileBuf.GetOneByteToInt (self.FILE_21_PF_CONFIGURATION) & 0xc) >> 2
        self.PfConfigurationGat = (fileBuf.GetOneByteToInt (self.FILE_21_PF_CONFIGURATION) & 0x30) >> 4
        self.PfConfigurationMip = (fileBuf.GetOneByteToInt (self.FILE_21_PF_CONFIGURATION)& 0xc0) >> 6



        self.CmdPredictionThreshold = fileBuf.GetOneByteToInt(self.FILE_21_COMMAND_PREDICTION_THRESHOLD)

        # String Based EPWR Offsets (RPG-32083)
        self.StringBasedEpwrEnableSLC = (fileBuf.GetOneByteToInt(self.FILE_21_STRING_BASED_EPWR_ENABLE) & 1)^1
        self.StringBasedEpwrEnableMLC = ((fileBuf.GetOneByteToInt(self.FILE_21_STRING_BASED_EPWR_ENABLE) & 2) >> 1)^1
        self.StringBasedEpwrEnableGAT = ((fileBuf.GetOneByteToInt(self.FILE_21_STRING_BASED_EPWR_ENABLE) & 4) >> 2)^1

        SLCStringEPWRValue = fileBuf.GetFourBytesToInt(self.FILE_21_STRING_BASED_EPWR_SLC_STRING_START_OFFSET)  & 0x0FFFFF
        MLCStringEPWRValue = fileBuf.GetFourBytesToInt(self.FILE_21_STRING_BASED_EPWR_MLC_STRING_START_OFFSET)  & 0x0FFFFF
        GATStringEPWRValue = fileBuf.GetFourBytesToInt(self.FILE_21_STRING_BASED_EPWR_GAT_STRING_START_OFFSET)  & 0x0FFFFF
        for string in range(0, self.__fwConfigObj.stringsPerBlock): # 4 strings in BiCS4
            self.StringBasedEpwrSlcStringList[string] = (SLCStringEPWRValue >> (4*string)) & 0xF
            self.StringBasedEpwrMlcStringList[string] = (MLCStringEPWRValue >> (4*string)) & 0xF
            self.StringBasedEpwrGatStringList[string] = (GATStringEPWRValue >> (4*string)) & 0xF

        #MLC WA Scaning
        self.isMLCZoneBasedWAScanningEnbale = fileBuf.GetOneByteToInt(self.FILE_21_MLC_ZONE_BASED_SCANNING_ENABLE)
        self.NumberOfWLZones                = fileBuf.GetOneByteToInt(self.FILE_21_NUMBER_OF_WL_ZONES)
        counter = 0
        for index in range(0, self.NumberOfWLZones):
            self.WLZonesRange[index] = [fileBuf.GetOneByteToInt(self.FILE_21_WL_ZONES_INFO+counter)]
            counter += 1
            self.WLZonesRange[index].append(fileBuf.GetOneByteToInt(self.FILE_21_WL_ZONES_INFO+counter))
            counter += 1

        #PGC Quota Time Values
        self.PGCQuotaValues_Dict['GAT_COMPACTION'] = fileBuf.GetOneByteToInt(self.FILE_21_PGC_GAT_COMPACTION_TIME)
        self.PGCQuotaValues_Dict['GAT_EPWR'] = fileBuf.GetOneByteToInt(self.FILE_21_PGC_GAT_PHASED_EPWR_TIME)
        self.PGCQuotaValues_Dict['FS_COMPACTION'] = fileBuf.GetOneByteToInt(self.FILE_21_PGC_READ_SCRUB_TIME)
        self.PGCQuotaValues_Dict['GAT_SYNC'] = fileBuf.GetOneByteToInt(self.FILE_21_PGC_GAT_SYNC_TIME)
        self.PGCQuotaValues_Dict['GCC_IDLE'] = fileBuf.GetOneByteToInt(self.FILE_21_PGC_GCC_PHASED_GC_TIME)
        self.PGCQuotaValues_Dict['GCC_PHASED_GC_IN_PROGRESS'] = fileBuf.GetOneByteToInt(self.FILE_21_PGC_GCC_PHASED_GC_TIME)
        self.PGCQuotaValues_Dict['GCC_PHASED_PC_COMMITS'] = fileBuf.GetOneByteToInt(self.FILE_21_PGC_GCC_PHASED_PC_COMMIT_TIME)
        self.PGCQuotaValues_Dict['GCC_HANDLE_PC_WA'] = fileBuf.GetOneByteToInt(self.FILE_21_PGC_GCC_PHASED_PC_WA_TIME)
        self.PGCQuotaValues_Dict['GCC_PHASED_EPWR'] = fileBuf.GetOneByteToInt(self.FILE_21_PGC_GCC_PHASED_EPWR_TIME)
        self.PGCQuotaValues_Dict['GCC_PHASED_PADDING'] = fileBuf.GetOneByteToInt(self.FILE_21_PGC_GCC_PHASED_GC_TIME)
        self.PGCQuotaValues_Dict['GCC_PC_RGAT_COMMIT'] = fileBuf.GetOneByteToInt(self.FILE_21_PGC_GCC_PHASED_PC_WA_TIME)
        self.PGCQuotaValues_Dict['GCC_DEST_EXCHANGE'] = fileBuf.GetOneByteToInt(self.FILE_21_PGC_GCC_PHASED_GC_TIME)
        self.PGCQuotaValues_Dict['GCC_PHASED_COMMIT'] = fileBuf.GetOneByteToInt(self.FILE_21_PGC_GCC_PHASED_COMMIT_TIME)
        self.PGCQuotaValues_Dict['HOST_EPWR'] = fileBuf.GetOneByteToInt(self.FILE_21_PGC_HOST_EPWR_TIME)

        self.MLCEPWRBESStage2Enabled = fileBuf.GetOneByteToInt(self.FILE_21_MLC_EPWR_BES_STAGE2_ENABLE_OFFSET)
        self.CmdB2Enable = fileBuf.GetOneByteToInt(self.FILE_21_CMDB2ENABLE)
    #end of __ParseConfigurationData


    def __DoFileRead(self,vtfContainer):
        """
        Name : __DoFileRead
        Description :
                 This function read the lates Configuration File and return the buffer data
        Arguments :
                vtfContainer : vtfContainer of the card
        Return
               fileBuf     : file buffer
               fileSize    : file buffer size
        """
        fileSize, fileSizeBytes = DiagnosticLib.LengthOfFileInBytes(fileId=self.FILE_ID)
        fileBuf = DiagnosticLib.ReadFileSystem(vtfContainer, fileID=self.FILE_ID, sectorCount=fileSize)

        return fileBuf,fileSize

    #end of __DoFileRead

    def __DoWriteFile(self,fileBuf,fileSize):
        """
        Name : __DoWriteFile
        Description :
                 This function write the file data to card
        Arguments :
                fileBuf     : file buffer
                fileSize    : file buffer size
        Return
               None
        """

        DiagnosticLib.WriteFileSystem(self.vtfContainer, fileID= self.FILE_ID,  sectorCount = fileSize, dataBuffer= fileBuf)

        return

#end of class


def GetFile50Data(vtfContainer):
    #offsets
    FILE_50_LOG_CLASS_NAME_T = 0X000
    FILE_50_LOG_ANNOTATION_T = 0X001
    FILE_50_ERROR_RECORD_TYPE = 0X005
    FILE_50_PAYLOAD_LENGTH = 0X006
    FILE_50_ERROR_STATUS = 0X010
    FILE_50_ERROR_LBA = 0x018
    FILE_50_RESTORE_COUNT = 0X01C
    FILE_50_DIE_NUMBER = 0X01F
    FILE_50_SECTOR_NUMBER = 0X020
    FILE_50_PAGE_NUMBER = 0X021
    FILE_50_BLOCK_INDEX = 0X023
    FILE_50_PLANE_NUMBER = 0X024
    FILE_50_PHYSICAL_CHIP_NUMBER = 0X025
    #FILE_50_BLOCK_LIST = 0X026

    FILE_ID = 50

    fileBuf = DiagnosticLib.ReadFileSystem(vtfContainer, fileID=FILE_ID)

    configParams = {"errorLogClassNameT":None, "errorLogAnnotationT":None,"errorRecordType":None,
                    "payloadLength":None,"errorStatus":None, "errorLba":None, "restoreCount":None, "dieNum":None,
                    "sectorNum":None,"pageNum":None,"blockNum":None, "planeNum":None, "phyChipNum":None}

    #configParams["errorLogUpdateCounter"] = fileBuf.GetOneByteToInt(FILE_50_ERRORLOG_UPDATE_COUNTER_OFFSET)
    configParams["errorLogClassNameT"] = fileBuf.GetOneByteToInt(FILE_50_LOG_CLASS_NAME_T)
    configParams["errorLogAnnotationT"] = fileBuf.GetOneByteToInt(FILE_50_LOG_ANNOTATION_T)
    configParams["errorRecordType"] = fileBuf.GetOneByteToInt(FILE_50_ERROR_RECORD_TYPE)
    configParams["payloadLength"] = fileBuf.GetTwoBytesToInt(FILE_50_PAYLOAD_LENGTH)
    configParams["errorStatus"] = fileBuf.GetOneByteToInt(FILE_50_ERROR_STATUS)
    configParams["errorLba"] = fileBuf.GetFourBytesToInt(FILE_50_ERROR_LBA)
    configParams["restoreCount"] = fileBuf.GetTwoBytesToInt(FILE_50_RESTORE_COUNT)
    configParams["dieNum"] = fileBuf.GetOneByteToInt(FILE_50_DIE_NUMBER)
    configParams["sectorNum"] = fileBuf.GetOneByteToInt(FILE_50_SECTOR_NUMBER)
    configParams["pageNum"] = fileBuf.GetTwoBytesToInt(FILE_50_PAGE_NUMBER)
    configParams["blockNum"] = fileBuf.GetOneByteToInt(FILE_50_BLOCK_INDEX)
    configParams["planeNum"] = fileBuf.GetOneByteToInt(FILE_50_PLANE_NUMBER)
    configParams["phyChipNum"] = fileBuf.GetOneByteToInt(FILE_50_PHYSICAL_CHIP_NUMBER)
    #configParams["blockList"] = fileBuf.GetsByteToInt(FILE_50_BLOCK_LIST)

    return configParams
#end of GetFile50Data()

def GetFile54Data(vtfContainer):

    #New File for Zone based Adaptive ERC

    FILE_54_SLC_MULTIPLIER_FOR_HC = 0x08
    FILE_54_TLC_MULTIPLIER_FOR_HC = 0x0A
    FILE_54_SLC_HC_THRESHOLD_ENTRIES = 0x0B
    FILE_54_TLC_HC_THRESHOLD_ENTRIES = 0x0C

    FILE_54_SLC_HC_THRESHOLD_00 = 0x0D
    FILE_54_SLC_HC_THRESHOLD_01 = 0x2E
    FILE_54_SLC_HC_THRESHOLD_02 = 0x4F
    FILE_54_SLC_HC_THRESHOLD_03 = 0x70
    FILE_54_SLC_HC_THRESHOLD_04 = 0x91
    FILE_54_SLC_HC_THRESHOLD_05 = 0xB2
    FILE_54_SLC_HC_THRESHOLD_06 = 0xD3
    FILE_54_SLC_HC_THRESHOLD_07 = 0xF4
    FILE_54_SLC_HC_THRESHOLD_08 = 0x115
    FILE_54_SLC_HC_THRESHOLD_09 = 0x136

    FILE_54_TLC_HC_THRESHOLD_00 = 0x157
    FILE_54_TLC_HC_THRESHOLD_01 = 0x178
    FILE_54_TLC_HC_THRESHOLD_02 = 0x199
    FILE_54_TLC_HC_THRESHOLD_03 = 0x1BA
    FILE_54_TLC_HC_THRESHOLD_04 = 0x1DB

    #SLC DAC and Bit Threshold Values for 1st HC Value
    FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_0       =       FILE_54_SLC_HC_THRESHOLD_00 + 1
    FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_1       =       FILE_54_SLC_HC_THRESHOLD_00 + 3
    FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_2       =       FILE_54_SLC_HC_THRESHOLD_00 + 5
    FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_3       =       FILE_54_SLC_HC_THRESHOLD_00 + 7
    FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_4       =       FILE_54_SLC_HC_THRESHOLD_00 + 9
    FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_5       =       FILE_54_SLC_HC_THRESHOLD_00 + 11
    FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_6       =       FILE_54_SLC_HC_THRESHOLD_00 + 13
    FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_7       =       FILE_54_SLC_HC_THRESHOLD_00 + 15
    FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_8       =       FILE_54_SLC_HC_THRESHOLD_00 + 17
    FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_9       =       FILE_54_SLC_HC_THRESHOLD_00 + 19
    FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_10      =       FILE_54_SLC_HC_THRESHOLD_00 + 21
    FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_11      =       FILE_54_SLC_HC_THRESHOLD_00 + 23
    FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_12      =       FILE_54_SLC_HC_THRESHOLD_00 + 25
    FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_13      =       FILE_54_SLC_HC_THRESHOLD_00 + 27
    FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_14      =       FILE_54_SLC_HC_THRESHOLD_00 + 29
    FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_15      =       FILE_54_SLC_HC_THRESHOLD_00 + 31

    FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_0       =       FILE_54_SLC_HC_THRESHOLD_00 + 2
    FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_1       =       FILE_54_SLC_HC_THRESHOLD_00 + 4
    FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_2       =       FILE_54_SLC_HC_THRESHOLD_00 + 6
    FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_3       =       FILE_54_SLC_HC_THRESHOLD_00 + 8
    FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_4       =       FILE_54_SLC_HC_THRESHOLD_00 + 10
    FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_5       =       FILE_54_SLC_HC_THRESHOLD_00 + 12
    FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_6       =       FILE_54_SLC_HC_THRESHOLD_00 + 14
    FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_7       =       FILE_54_SLC_HC_THRESHOLD_00 + 16
    FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_8       =       FILE_54_SLC_HC_THRESHOLD_00 + 18
    FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_9       =       FILE_54_SLC_HC_THRESHOLD_00 + 20
    FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_10      =       FILE_54_SLC_HC_THRESHOLD_00 + 22
    FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_11      =       FILE_54_SLC_HC_THRESHOLD_00 + 24
    FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_12      =       FILE_54_SLC_HC_THRESHOLD_00 + 26
    FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_13      =       FILE_54_SLC_HC_THRESHOLD_00 + 28
    FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_14      =       FILE_54_SLC_HC_THRESHOLD_00 + 30
    FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_15      =       FILE_54_SLC_HC_THRESHOLD_00 + 32

    #SLC DAC and Bit Threshold Values for 2nd HC Value
    FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_0       =       FILE_54_SLC_HC_THRESHOLD_01 + 1
    FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_1       =       FILE_54_SLC_HC_THRESHOLD_01 + 3
    FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_2       =       FILE_54_SLC_HC_THRESHOLD_01 + 5
    FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_3       =       FILE_54_SLC_HC_THRESHOLD_01 + 7
    FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_4       =       FILE_54_SLC_HC_THRESHOLD_01 + 9
    FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_5       =       FILE_54_SLC_HC_THRESHOLD_01 + 11
    FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_6       =       FILE_54_SLC_HC_THRESHOLD_01 + 13
    FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_7       =       FILE_54_SLC_HC_THRESHOLD_01 + 15
    FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_8       =       FILE_54_SLC_HC_THRESHOLD_01 + 17
    FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_9       =       FILE_54_SLC_HC_THRESHOLD_01 + 19
    FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_10      =       FILE_54_SLC_HC_THRESHOLD_01 + 21
    FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_11      =       FILE_54_SLC_HC_THRESHOLD_01 + 23
    FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_12      =       FILE_54_SLC_HC_THRESHOLD_01 + 25
    FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_13      =       FILE_54_SLC_HC_THRESHOLD_01 + 27
    FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_14      =       FILE_54_SLC_HC_THRESHOLD_01 + 29
    FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_15      =       FILE_54_SLC_HC_THRESHOLD_01 + 31

    FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_0       =       FILE_54_SLC_HC_THRESHOLD_01 + 2
    FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_1       =       FILE_54_SLC_HC_THRESHOLD_01 + 4
    FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_2       =       FILE_54_SLC_HC_THRESHOLD_01 + 6
    FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_3       =       FILE_54_SLC_HC_THRESHOLD_01 + 8
    FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_4       =       FILE_54_SLC_HC_THRESHOLD_01 + 10
    FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_5       =       FILE_54_SLC_HC_THRESHOLD_01 + 12
    FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_6       =       FILE_54_SLC_HC_THRESHOLD_01 + 14
    FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_7       =       FILE_54_SLC_HC_THRESHOLD_01 + 16
    FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_8       =       FILE_54_SLC_HC_THRESHOLD_01 + 18
    FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_9       =       FILE_54_SLC_HC_THRESHOLD_01 + 20
    FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_10      =       FILE_54_SLC_HC_THRESHOLD_01 + 22
    FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_11      =       FILE_54_SLC_HC_THRESHOLD_01 + 24
    FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_12      =       FILE_54_SLC_HC_THRESHOLD_01 + 26
    FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_13      =       FILE_54_SLC_HC_THRESHOLD_01 + 28
    FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_14      =       FILE_54_SLC_HC_THRESHOLD_01 + 30
    FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_15      =       FILE_54_SLC_HC_THRESHOLD_01 + 32

    #TLC DAC and Bit Threshold Values for 1st HC Value
    FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_0       =       FILE_54_TLC_HC_THRESHOLD_00 + 1
    FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_1       =       FILE_54_TLC_HC_THRESHOLD_00 + 3
    FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_2       =       FILE_54_TLC_HC_THRESHOLD_00 + 5
    FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_3       =       FILE_54_TLC_HC_THRESHOLD_00 + 7
    FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_4       =       FILE_54_TLC_HC_THRESHOLD_00 + 9
    FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_5       =       FILE_54_TLC_HC_THRESHOLD_00 + 11
    FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_6       =       FILE_54_TLC_HC_THRESHOLD_00 + 13
    FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_7       =       FILE_54_TLC_HC_THRESHOLD_00 + 15
    FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_8       =       FILE_54_TLC_HC_THRESHOLD_00 + 17
    FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_9       =       FILE_54_TLC_HC_THRESHOLD_00 + 19
    FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_10      =       FILE_54_TLC_HC_THRESHOLD_00 + 21
    FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_11      =       FILE_54_TLC_HC_THRESHOLD_00 + 23
    FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_12      =       FILE_54_TLC_HC_THRESHOLD_00 + 25
    FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_13      =       FILE_54_TLC_HC_THRESHOLD_00 + 27
    FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_14      =       FILE_54_TLC_HC_THRESHOLD_00 + 29
    FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_15      =       FILE_54_TLC_HC_THRESHOLD_00 + 31


    FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_0       =       FILE_54_TLC_HC_THRESHOLD_00 + 2
    FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_1       =       FILE_54_TLC_HC_THRESHOLD_00 + 4
    FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_2       =       FILE_54_TLC_HC_THRESHOLD_00 + 6
    FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_3       =       FILE_54_TLC_HC_THRESHOLD_00 + 8
    FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_4       =       FILE_54_TLC_HC_THRESHOLD_00 + 10
    FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_5       =       FILE_54_TLC_HC_THRESHOLD_00 + 12
    FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_6       =       FILE_54_TLC_HC_THRESHOLD_00 + 14
    FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_7       =       FILE_54_TLC_HC_THRESHOLD_00 + 16
    FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_8       =       FILE_54_TLC_HC_THRESHOLD_00 + 18
    FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_9       =       FILE_54_TLC_HC_THRESHOLD_00 + 20
    FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_10      =       FILE_54_TLC_HC_THRESHOLD_00 + 22
    FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_11      =       FILE_54_TLC_HC_THRESHOLD_00 + 24
    FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_12      =       FILE_54_TLC_HC_THRESHOLD_00 + 26
    FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_13      =       FILE_54_TLC_HC_THRESHOLD_00 + 28
    FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_14      =       FILE_54_TLC_HC_THRESHOLD_00 + 30
    FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_15      =       FILE_54_TLC_HC_THRESHOLD_00 + 32


    #TLC DAC and Bit Threshold Values for 2nd HC Value
    FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_0       =       FILE_54_TLC_HC_THRESHOLD_01 + 1
    FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_1       =       FILE_54_TLC_HC_THRESHOLD_01 + 3
    FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_2       =       FILE_54_TLC_HC_THRESHOLD_01 + 5
    FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_3       =       FILE_54_TLC_HC_THRESHOLD_01 + 7
    FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_4       =       FILE_54_TLC_HC_THRESHOLD_01 + 9
    FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_5       =       FILE_54_TLC_HC_THRESHOLD_01 + 11
    FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_6       =       FILE_54_TLC_HC_THRESHOLD_01 + 13
    FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_7       =       FILE_54_TLC_HC_THRESHOLD_01 + 15
    FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_8       =       FILE_54_TLC_HC_THRESHOLD_01 + 17
    FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_9       =       FILE_54_TLC_HC_THRESHOLD_01 + 19
    FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_10      =       FILE_54_TLC_HC_THRESHOLD_01 + 21
    FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_11      =       FILE_54_TLC_HC_THRESHOLD_01 + 23
    FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_12      =       FILE_54_TLC_HC_THRESHOLD_01 + 25
    FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_13      =       FILE_54_TLC_HC_THRESHOLD_01 + 27
    FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_14      =       FILE_54_TLC_HC_THRESHOLD_01 + 29
    FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_15      =       FILE_54_TLC_HC_THRESHOLD_01 + 31

    FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_0       =       FILE_54_TLC_HC_THRESHOLD_01 + 2
    FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_1       =       FILE_54_TLC_HC_THRESHOLD_01 + 4
    FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_2       =       FILE_54_TLC_HC_THRESHOLD_01 + 6
    FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_3       =       FILE_54_TLC_HC_THRESHOLD_01 + 8
    FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_4       =       FILE_54_TLC_HC_THRESHOLD_01 + 10
    FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_5       =       FILE_54_TLC_HC_THRESHOLD_01 + 12
    FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_6       =       FILE_54_TLC_HC_THRESHOLD_01 + 14
    FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_7       =       FILE_54_TLC_HC_THRESHOLD_01 + 16
    FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_8       =       FILE_54_TLC_HC_THRESHOLD_01 + 18
    FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_9       =       FILE_54_TLC_HC_THRESHOLD_01 + 20
    FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_10      =       FILE_54_TLC_HC_THRESHOLD_01 + 22
    FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_11      =       FILE_54_TLC_HC_THRESHOLD_01 + 24
    FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_12      =       FILE_54_TLC_HC_THRESHOLD_01 + 26
    FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_13      =       FILE_54_TLC_HC_THRESHOLD_01 + 28
    FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_14      =       FILE_54_TLC_HC_THRESHOLD_01 + 30
    FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_15      =       FILE_54_TLC_HC_THRESHOLD_01 + 32

    #TLC DAC and Bit Threshold Values for 3rd HC Value
    FILE_54_TLC_DAC_THRESHOLD_HC_02_ZONE_0       =       FILE_54_TLC_HC_THRESHOLD_02 + 1
    FILE_54_TLC_DAC_THRESHOLD_HC_02_ZONE_1       =       FILE_54_TLC_HC_THRESHOLD_02 + 3
    FILE_54_TLC_DAC_THRESHOLD_HC_02_ZONE_2       =       FILE_54_TLC_HC_THRESHOLD_02 + 5
    FILE_54_TLC_DAC_THRESHOLD_HC_02_ZONE_3       =       FILE_54_TLC_HC_THRESHOLD_02 + 7
    FILE_54_TLC_DAC_THRESHOLD_HC_02_ZONE_4       =       FILE_54_TLC_HC_THRESHOLD_02 + 9
    FILE_54_TLC_DAC_THRESHOLD_HC_02_ZONE_5       =       FILE_54_TLC_HC_THRESHOLD_02 + 11

    FILE_54_TLC_BIT_THRESHOLD_HC_02_ZONE_0       =       FILE_54_TLC_HC_THRESHOLD_02 + 2
    FILE_54_TLC_BIT_THRESHOLD_HC_02_ZONE_1       =       FILE_54_TLC_HC_THRESHOLD_02 + 4
    FILE_54_TLC_BIT_THRESHOLD_HC_02_ZONE_2       =       FILE_54_TLC_HC_THRESHOLD_02 + 6
    FILE_54_TLC_BIT_THRESHOLD_HC_02_ZONE_3       =       FILE_54_TLC_HC_THRESHOLD_02 + 8
    FILE_54_TLC_BIT_THRESHOLD_HC_02_ZONE_4       =       FILE_54_TLC_HC_THRESHOLD_02 + 10
    FILE_54_TLC_BIT_THRESHOLD_HC_02_ZONE_5       =       FILE_54_TLC_HC_THRESHOLD_02 + 12

    #TLC DAC and Bit Threshold Values for 4th HC Value
    FILE_54_TLC_DAC_THRESHOLD_HC_03_ZONE_0       =       FILE_54_TLC_HC_THRESHOLD_03 + 1
    FILE_54_TLC_DAC_THRESHOLD_HC_03_ZONE_1       =       FILE_54_TLC_HC_THRESHOLD_03 + 3
    FILE_54_TLC_DAC_THRESHOLD_HC_03_ZONE_2       =       FILE_54_TLC_HC_THRESHOLD_03 + 5
    FILE_54_TLC_DAC_THRESHOLD_HC_03_ZONE_3       =       FILE_54_TLC_HC_THRESHOLD_03 + 7
    FILE_54_TLC_DAC_THRESHOLD_HC_03_ZONE_4       =       FILE_54_TLC_HC_THRESHOLD_03 + 9
    FILE_54_TLC_DAC_THRESHOLD_HC_03_ZONE_5       =       FILE_54_TLC_HC_THRESHOLD_03 + 11

    FILE_54_TLC_BIT_THRESHOLD_HC_03_ZONE_0       =       FILE_54_TLC_HC_THRESHOLD_03 + 2
    FILE_54_TLC_BIT_THRESHOLD_HC_03_ZONE_1       =       FILE_54_TLC_HC_THRESHOLD_03 + 4
    FILE_54_TLC_BIT_THRESHOLD_HC_03_ZONE_2       =       FILE_54_TLC_HC_THRESHOLD_03 + 6
    FILE_54_TLC_BIT_THRESHOLD_HC_03_ZONE_3       =       FILE_54_TLC_HC_THRESHOLD_03 + 8
    FILE_54_TLC_BIT_THRESHOLD_HC_03_ZONE_4       =       FILE_54_TLC_HC_THRESHOLD_03 + 10
    FILE_54_TLC_BIT_THRESHOLD_HC_03_ZONE_5       =       FILE_54_TLC_HC_THRESHOLD_03 + 12


    #TLC DAC and Bit Threshold Values for 5th HC Value
    FILE_54_TLC_DAC_THRESHOLD_HC_04_ZONE_0       =       FILE_54_TLC_HC_THRESHOLD_04 + 1
    FILE_54_TLC_DAC_THRESHOLD_HC_04_ZONE_1       =       FILE_54_TLC_HC_THRESHOLD_04 + 3
    FILE_54_TLC_DAC_THRESHOLD_HC_04_ZONE_2       =       FILE_54_TLC_HC_THRESHOLD_04 + 5
    FILE_54_TLC_DAC_THRESHOLD_HC_04_ZONE_3       =       FILE_54_TLC_HC_THRESHOLD_04 + 7
    FILE_54_TLC_DAC_THRESHOLD_HC_04_ZONE_4       =       FILE_54_TLC_HC_THRESHOLD_04 + 9
    FILE_54_TLC_DAC_THRESHOLD_HC_04_ZONE_5       =       FILE_54_TLC_HC_THRESHOLD_04 + 11

    FILE_54_TLC_BIT_THRESHOLD_HC_04_ZONE_0       =       FILE_54_TLC_HC_THRESHOLD_04 + 2
    FILE_54_TLC_BIT_THRESHOLD_HC_04_ZONE_1       =       FILE_54_TLC_HC_THRESHOLD_04 + 4
    FILE_54_TLC_BIT_THRESHOLD_HC_04_ZONE_2       =       FILE_54_TLC_HC_THRESHOLD_04 + 6
    FILE_54_TLC_BIT_THRESHOLD_HC_04_ZONE_3       =       FILE_54_TLC_HC_THRESHOLD_04 + 8
    FILE_54_TLC_BIT_THRESHOLD_HC_04_ZONE_4       =       FILE_54_TLC_HC_THRESHOLD_04 + 10
    FILE_54_TLC_BIT_THRESHOLD_HC_04_ZONE_5       =       FILE_54_TLC_HC_THRESHOLD_04 + 12


    FILE_ID = 54

    fileBuf = DiagnosticLib.ReadFileSystem(vtfContainer, fileID=FILE_ID)

    configParams = {"SLCMultiplierForHC":None,"TLCMultiplierForHC":None,"SLCHCThresholdEntry":None,"TLCHCThresholdEntry":None,"SLCHCThreshold_0":None,"SLCHCThreshold_1":None,\
                    "SLCHCThreshold_2":None,"SLCHCThreshold_3":None,"SLCHCThreshold_4":None,"SLCHCThreshold_5":None,"SLCHCThreshold_6":None,"SLCHCThreshold_7":None,"SLCHCThreshold_8":None,\
                    "SLCHCThreshold_9":None,"TLCHCThreshold_0":None,"TLCHCThreshold_1":None,"TLCHCThreshold_2":None,"TLCHCThreshold_3":None,"TLCHCThreshold_4":None,\
                    "SLC_DAC_HC_0_Zone0" :None,"SLC_DAC_HC_0_Zone1" :None,"SLC_DAC_HC_0_Zone2" :None,"SLC_DAC_HC_0_Zone3" :None,"SLC_DAC_HC_0_Zone4" :None,"SLC_DAC_HC_0_Zone5" :None,"SLC_DAC_HC_0_Zone6" :None,"SLC_DAC_HC_0_Zone7" :None,\
                    "SLC_BIT_HC_0_Zone0" :None,"SLC_BIT_HC_0_Zone1" :None,"SLC_BIT_HC_0_Zone2" :None,"SLC_BIT_HC_0_Zone3" :None,"SLC_BIT_HC_0_Zone4" :None,"SLC_BIT_HC_0_Zone5" :None,"SLC_BIT_HC_0_Zone6" :None,"SLC_BIT_HC_0_Zone7" :None,\
                    "SLC_DAC_HC_1_Zone0" :None,"SLC_DAC_HC_1_Zone1" :None,"SLC_DAC_HC_1_Zone2" :None,"SLC_DAC_HC_1_Zone3" :None,"SLC_DAC_HC_1_Zone4" :None,"SLC_DAC_HC_1_Zone5" :None,"SLC_DAC_HC_1_Zone6" :None,"SLC_DAC_HC_1_Zone7" :None,\
                    "SLC_BIT_HC_1_Zone0" :None,"SLC_BIT_HC_1_Zone1" :None,"SLC_BIT_HC_1_Zone2" :None,"SLC_BIT_HC_1_Zone3" :None,"SLC_BIT_HC_1_Zone4" :None,"SLC_BIT_HC_1_Zone5" :None,"SLC_BIT_HC_1_Zone6" :None,"SLC_BIT_HC_1_Zone7" :None,\
                    "TLC_DAC_HC_0_Zone0" :None,"TLC_DAC_HC_0_Zone1" :None,"TLC_DAC_HC_0_Zone2" :None,"TLC_DAC_HC_0_Zone3" :None,"TLC_DAC_HC_0_Zone4" :None,"TLC_DAC_HC_0_Zone5" :None,"TLC_DAC_HC_0_Zone6" :None,"TLC_DAC_HC_0_Zone7" :None,"TLC_DAC_HC_0_Zone8" :None,\
                    "TLC_BIT_HC_0_Zone0" :None,"TLC_BIT_HC_0_Zone1" :None,"TLC_BIT_HC_0_Zone2" :None,"TLC_BIT_HC_0_Zone3" :None,"TLC_BIT_HC_0_Zone4" :None,"TLC_BIT_HC_0_Zone5" :None,"TLC_BIT_HC_0_Zone6" :None,"TLC_BIT_HC_0_Zone7" :None,"TLC_BIT_HC_0_Zone8" :None,\
                    "TLC_DAC_HC_1_Zone0" :None,"TLC_DAC_HC_1_Zone1" :None,"TLC_DAC_HC_1_Zone2" :None,"TLC_DAC_HC_1_Zone3" :None,"TLC_DAC_HC_1_Zone4" :None,"TLC_DAC_HC_1_Zone5" :None,"TLC_DAC_HC_1_Zone6" :None,"TLC_DAC_HC_1_Zone7" :None,"TLC_DAC_HC_1_Zone8" :None,\
                    "TLC_BIT_HC_1_Zone0" :None,"TLC_BIT_HC_1_Zone1" :None,"TLC_BIT_HC_1_Zone2" :None,"TLC_BIT_HC_1_Zone3" :None,"TLC_BIT_HC_1_Zone4" :None,"TLC_BIT_HC_1_Zone5" :None,"TLC_BIT_HC_1_Zone6" :None,"TLC_BIT_HC_1_Zone7" :None,"TLC_BIT_HC_1_Zone8" :None,\
                    "TLC_DAC_HC_2_Zone0" :None,"TLC_DAC_HC_2_Zone1" :None,"TLC_DAC_HC_2_Zone2" :None,"TLC_DAC_HC_2_Zone3" :None,"TLC_DAC_HC_2_Zone4" :None,"TLC_DAC_HC_2_Zone5" :None,"TLC_DAC_HC_2_Zone6" :None,"TLC_DAC_HC_2_Zone7" :None,"TLC_DAC_HC_2_Zone8" :None,\
                    "TLC_BIT_HC_2_Zone0" :None,"TLC_BIT_HC_2_Zone1" :None,"TLC_BIT_HC_2_Zone2" :None,"TLC_BIT_HC_2_Zone3" :None,"TLC_BIT_HC_2_Zone4" :None,"TLC_BIT_HC_2_Zone5" :None,"TLC_BIT_HC_2_Zone6" :None,"TLC_BIT_HC_2_Zone7" :None,"TLC_BIT_HC_2_Zone8" :None,\
                    "TLC_DAC_HC_3_Zone0" :None,"TLC_DAC_HC_3_Zone1" :None,"TLC_DAC_HC_3_Zone2" :None,"TLC_DAC_HC_3_Zone3" :None,"TLC_DAC_HC_3_Zone4" :None,"TLC_DAC_HC_3_Zone5" :None,"TLC_DAC_HC_3_Zone6" :None,"TLC_DAC_HC_3_Zone7" :None,"TLC_DAC_HC_3_Zone8" :None,\
                    "TLC_BIT_HC_3_Zone0" :None,"TLC_BIT_HC_3_Zone1" :None,"TLC_BIT_HC_3_Zone2" :None,"TLC_BIT_HC_3_Zone3" :None,"TLC_BIT_HC_3_Zone4" :None,"TLC_BIT_HC_3_Zone5" :None,"TLC_BIT_HC_3_Zone6" :None,"TLC_BIT_HC_3_Zone7" :None,"TLC_BIT_HC_3_Zone8" :None,\
                    "TLC_DAC_HC_4_Zone0" :None,"TLC_DAC_HC_4_Zone1" :None,"TLC_DAC_HC_4_Zone2" :None,"TLC_DAC_HC_4_Zone3" :None,"TLC_DAC_HC_4_Zone4" :None,"TLC_DAC_HC_4_Zone5" :None,"TLC_DAC_HC_4_Zone6" :None,"TLC_DAC_HC_4_Zone7" :None,"TLC_DAC_HC_4_Zone8" :None,\
                    "TLC_BIT_HC_4_Zone0" :None,"TLC_BIT_HC_4_Zone1" :None,"TLC_BIT_HC_4_Zone2" :None,"TLC_BIT_HC_4_Zone3" :None,"TLC_BIT_HC_4_Zone4" :None,"TLC_BIT_HC_4_Zone5" :None,"TLC_BIT_HC_4_Zone6" :None,"TLC_BIT_HC_4_Zone7" :None,"TLC_BIT_HC_4_Zone8" :None}

    configParams["SLCMultiplierForHC"] = fileBuf.GetTwoBytesToInt(FILE_54_SLC_MULTIPLIER_FOR_HC)
    configParams["TLCMultiplierForHC"] = fileBuf.GetOneByteToInt(FILE_54_TLC_MULTIPLIER_FOR_HC)
    configParams["SLCHCThresholdEntry"] = fileBuf.GetOneByteToInt(FILE_54_SLC_HC_THRESHOLD_ENTRIES)
    configParams["TLCHCThresholdEntry"] = fileBuf.GetOneByteToInt(FILE_54_TLC_HC_THRESHOLD_ENTRIES)
    configParams["SLCHCThreshold_0"] = fileBuf.GetOneByteToInt(FILE_54_SLC_HC_THRESHOLD_00)
    configParams["SLCHCThreshold_1"] = fileBuf.GetOneByteToInt(FILE_54_SLC_HC_THRESHOLD_01)
    configParams["TLCHCThreshold_0"] = fileBuf.GetOneByteToInt(FILE_54_TLC_HC_THRESHOLD_00)
    configParams["TLCHCThreshold_1"] = fileBuf.GetOneByteToInt(FILE_54_TLC_HC_THRESHOLD_01)
    configParams["TLCHCThreshold_2"] = fileBuf.GetOneByteToInt(FILE_54_TLC_HC_THRESHOLD_02)
    configParams["TLCHCThreshold_3"] = fileBuf.GetOneByteToInt(FILE_54_TLC_HC_THRESHOLD_03)
    configParams["TLCHCThreshold_4"] = fileBuf.GetOneByteToInt(FILE_54_TLC_HC_THRESHOLD_04)

    configParams["SLC_DAC_HC_0_Zone0"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_0)
    configParams["SLC_DAC_HC_0_Zone1"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_1)
    configParams["SLC_DAC_HC_0_Zone2"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_2)
    configParams["SLC_DAC_HC_0_Zone3"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_3)
    configParams["SLC_DAC_HC_0_Zone4"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_4)
    configParams["SLC_DAC_HC_0_Zone5"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_5)
    configParams["SLC_DAC_HC_0_Zone6"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_6)
    configParams["SLC_DAC_HC_0_Zone7"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_7)
    configParams["SLC_DAC_HC_0_Zone8"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_8)
    configParams["SLC_DAC_HC_0_Zone9"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_9)
    configParams["SLC_DAC_HC_0_Zone10"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_10)
    configParams["SLC_DAC_HC_0_Zone11"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_11)
    configParams["SLC_DAC_HC_0_Zone12"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_12)
    configParams["SLC_DAC_HC_0_Zone13"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_13)
    configParams["SLC_DAC_HC_0_Zone14"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_14)
    configParams["SLC_DAC_HC_0_Zone15"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_00_ZONE_15)

    configParams["SLC_BIT_HC_0_Zone0"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_0)
    configParams["SLC_BIT_HC_0_Zone1"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_1)
    configParams["SLC_BIT_HC_0_Zone2"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_2)
    configParams["SLC_BIT_HC_0_Zone3"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_3)
    configParams["SLC_BIT_HC_0_Zone4"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_4)
    configParams["SLC_BIT_HC_0_Zone5"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_5)
    configParams["SLC_BIT_HC_0_Zone6"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_6)
    configParams["SLC_BIT_HC_0_Zone7"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_7)
    configParams["SLC_BIT_HC_0_Zone8"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_8)
    configParams["SLC_BIT_HC_0_Zone9"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_9)
    configParams["SLC_BIT_HC_0_Zone10"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_10)
    configParams["SLC_BIT_HC_0_Zone11"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_11)
    configParams["SLC_BIT_HC_0_Zone12"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_12)
    configParams["SLC_BIT_HC_0_Zone13"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_13)
    configParams["SLC_BIT_HC_0_Zone14"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_14)
    configParams["SLC_BIT_HC_0_Zone15"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_00_ZONE_15)

    configParams["SLC_DAC_HC_1_Zone0"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_0)
    configParams["SLC_DAC_HC_1_Zone1"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_1)
    configParams["SLC_DAC_HC_1_Zone2"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_2)
    configParams["SLC_DAC_HC_1_Zone3"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_3)
    configParams["SLC_DAC_HC_1_Zone4"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_4)
    configParams["SLC_DAC_HC_1_Zone5"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_5)
    configParams["SLC_DAC_HC_1_Zone6"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_6)
    configParams["SLC_DAC_HC_1_Zone7"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_7)
    configParams["SLC_DAC_HC_1_Zone8"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_8)
    configParams["SLC_DAC_HC_1_Zone9"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_9)
    configParams["SLC_DAC_HC_1_Zone10"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_10)
    configParams["SLC_DAC_HC_1_Zone11"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_11)
    configParams["SLC_DAC_HC_1_Zone12"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_12)
    configParams["SLC_DAC_HC_1_Zone13"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_13)
    configParams["SLC_DAC_HC_1_Zone14"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_14)
    configParams["SLC_DAC_HC_1_Zone15"] = fileBuf.GetOneByteToInt(FILE_54_SLC_DAC_THRESHOLD_HC_01_ZONE_15)

    configParams["SLC_BIT_HC_1_Zone0"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_0)
    configParams["SLC_BIT_HC_1_Zone1"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_1)
    configParams["SLC_BIT_HC_1_Zone2"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_2)
    configParams["SLC_BIT_HC_1_Zone3"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_3)
    configParams["SLC_BIT_HC_1_Zone4"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_4)
    configParams["SLC_BIT_HC_1_Zone5"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_5)
    configParams["SLC_BIT_HC_1_Zone6"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_6)
    configParams["SLC_BIT_HC_1_Zone7"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_7)
    configParams["SLC_BIT_HC_1_Zone8"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_8)
    configParams["SLC_BIT_HC_1_Zone9"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_9)
    configParams["SLC_BIT_HC_1_Zone10"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_10)
    configParams["SLC_BIT_HC_1_Zone11"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_11)
    configParams["SLC_BIT_HC_1_Zone12"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_12)
    configParams["SLC_BIT_HC_1_Zone13"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_13)
    configParams["SLC_BIT_HC_1_Zone14"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_14)
    configParams["SLC_BIT_HC_1_Zone15"] = fileBuf.GetOneByteToInt(FILE_54_SLC_BIT_THRESHOLD_HC_01_ZONE_15)

    configParams["TLC_DAC_HC_0_Zone0"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_0)
    configParams["TLC_DAC_HC_0_Zone1"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_1)
    configParams["TLC_DAC_HC_0_Zone2"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_2)
    configParams["TLC_DAC_HC_0_Zone3"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_3)
    configParams["TLC_DAC_HC_0_Zone4"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_4)
    configParams["TLC_DAC_HC_0_Zone5"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_5)
    configParams["TLC_DAC_HC_0_Zone6"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_6)
    configParams["TLC_DAC_HC_0_Zone7"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_7)
    configParams["TLC_DAC_HC_0_Zone8"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_8)
    configParams["TLC_DAC_HC_0_Zone9"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_9)
    configParams["TLC_DAC_HC_0_Zone10"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_10)
    configParams["TLC_DAC_HC_0_Zone11"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_11)
    configParams["TLC_DAC_HC_0_Zone12"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_12)
    configParams["TLC_DAC_HC_0_Zone13"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_13)
    configParams["TLC_DAC_HC_0_Zone14"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_14)
    configParams["TLC_DAC_HC_0_Zone15"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_00_ZONE_15)

    configParams["TLC_BIT_HC_0_Zone0"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_0)
    configParams["TLC_BIT_HC_0_Zone1"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_1)
    configParams["TLC_BIT_HC_0_Zone2"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_2)
    configParams["TLC_BIT_HC_0_Zone3"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_3)
    configParams["TLC_BIT_HC_0_Zone4"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_4)
    configParams["TLC_BIT_HC_0_Zone5"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_5)
    configParams["TLC_BIT_HC_0_Zone6"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_6)
    configParams["TLC_BIT_HC_0_Zone7"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_7)
    configParams["TLC_BIT_HC_0_Zone8"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_8)
    configParams["TLC_BIT_HC_0_Zone9"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_9)
    configParams["TLC_BIT_HC_0_Zone10"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_10)
    configParams["TLC_BIT_HC_0_Zone11"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_11)
    configParams["TLC_BIT_HC_0_Zone12"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_12)
    configParams["TLC_BIT_HC_0_Zone13"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_13)
    configParams["TLC_BIT_HC_0_Zone14"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_14)
    configParams["TLC_BIT_HC_0_Zone15"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_00_ZONE_15)

    configParams["TLC_DAC_HC_1_Zone0"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_0)
    configParams["TLC_DAC_HC_1_Zone1"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_1)
    configParams["TLC_DAC_HC_1_Zone2"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_2)
    configParams["TLC_DAC_HC_1_Zone3"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_3)
    configParams["TLC_DAC_HC_1_Zone4"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_4)
    configParams["TLC_DAC_HC_1_Zone5"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_5)
    configParams["TLC_DAC_HC_1_Zone6"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_6)
    configParams["TLC_DAC_HC_1_Zone7"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_7)
    configParams["TLC_DAC_HC_1_Zone8"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_8)
    configParams["TLC_DAC_HC_1_Zone9"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_9)
    configParams["TLC_DAC_HC_1_Zone10"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_10)
    configParams["TLC_DAC_HC_1_Zone11"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_11)
    configParams["TLC_DAC_HC_1_Zone12"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_12)
    configParams["TLC_DAC_HC_1_Zone13"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_13)
    configParams["TLC_DAC_HC_1_Zone14"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_14)
    configParams["TLC_DAC_HC_1_Zone15"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_01_ZONE_15)

    configParams["TLC_BIT_HC_1_Zone0"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_0)
    configParams["TLC_BIT_HC_1_Zone1"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_1)
    configParams["TLC_BIT_HC_1_Zone2"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_2)
    configParams["TLC_BIT_HC_1_Zone3"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_3)
    configParams["TLC_BIT_HC_1_Zone4"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_4)
    configParams["TLC_BIT_HC_1_Zone5"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_5)
    configParams["TLC_BIT_HC_1_Zone6"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_6)
    configParams["TLC_BIT_HC_1_Zone7"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_7)
    configParams["TLC_BIT_HC_1_Zone8"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_8)
    configParams["TLC_BIT_HC_1_Zone9"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_9)
    configParams["TLC_BIT_HC_1_Zone10"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_10)
    configParams["TLC_BIT_HC_1_Zone11"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_11)
    configParams["TLC_BIT_HC_1_Zone12"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_12)
    configParams["TLC_BIT_HC_1_Zone13"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_13)
    configParams["TLC_BIT_HC_1_Zone14"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_14)
    configParams["TLC_BIT_HC_1_Zone15"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_01_ZONE_15)

    configParams["TLC_DAC_HC_2_Zone0"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_02_ZONE_0)
    configParams["TLC_DAC_HC_2_Zone1"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_02_ZONE_1)
    configParams["TLC_DAC_HC_2_Zone2"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_02_ZONE_2)
    configParams["TLC_DAC_HC_2_Zone3"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_02_ZONE_3)
    configParams["TLC_DAC_HC_2_Zone4"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_02_ZONE_4)
    configParams["TLC_DAC_HC_2_Zone5"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_02_ZONE_5)

    configParams["TLC_BIT_HC_2_Zone0"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_02_ZONE_0)
    configParams["TLC_BIT_HC_2_Zone1"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_02_ZONE_1)
    configParams["TLC_BIT_HC_2_Zone2"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_02_ZONE_2)
    configParams["TLC_BIT_HC_2_Zone3"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_02_ZONE_3)
    configParams["TLC_BIT_HC_2_Zone4"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_02_ZONE_4)
    configParams["TLC_BIT_HC_2_Zone5"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_02_ZONE_5)

    configParams["TLC_DAC_HC_3_Zone0"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_03_ZONE_0)
    configParams["TLC_DAC_HC_3_Zone1"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_03_ZONE_1)
    configParams["TLC_DAC_HC_3_Zone2"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_03_ZONE_2)
    configParams["TLC_DAC_HC_3_Zone3"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_03_ZONE_3)
    configParams["TLC_DAC_HC_3_Zone4"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_03_ZONE_4)
    configParams["TLC_DAC_HC_3_Zone5"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_03_ZONE_5)

    configParams["TLC_BIT_HC_3_Zone0"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_03_ZONE_0)
    configParams["TLC_BIT_HC_3_Zone1"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_03_ZONE_1)
    configParams["TLC_BIT_HC_3_Zone2"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_03_ZONE_2)
    configParams["TLC_BIT_HC_3_Zone3"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_03_ZONE_3)
    configParams["TLC_BIT_HC_3_Zone4"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_03_ZONE_4)
    configParams["TLC_BIT_HC_3_Zone5"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_03_ZONE_5)

    configParams["TLC_DAC_HC_4_Zone0"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_04_ZONE_0)
    configParams["TLC_DAC_HC_4_Zone1"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_04_ZONE_1)
    configParams["TLC_DAC_HC_4_Zone2"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_04_ZONE_2)
    configParams["TLC_DAC_HC_4_Zone3"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_04_ZONE_3)
    configParams["TLC_DAC_HC_4_Zone4"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_04_ZONE_4)
    configParams["TLC_DAC_HC_4_Zone5"] = fileBuf.GetOneByteToInt(FILE_54_TLC_DAC_THRESHOLD_HC_04_ZONE_5)

    configParams["TLC_BIT_HC_4_Zone0"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_04_ZONE_0)
    configParams["TLC_BIT_HC_4_Zone1"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_04_ZONE_1)
    configParams["TLC_BIT_HC_4_Zone2"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_04_ZONE_2)
    configParams["TLC_BIT_HC_4_Zone3"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_04_ZONE_3)
    configParams["TLC_BIT_HC_4_Zone4"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_04_ZONE_4)
    configParams["TLC_BIT_HC_4_Zone5"] = fileBuf.GetOneByteToInt(FILE_54_TLC_BIT_THRESHOLD_HC_04_ZONE_5)


    return configParams

def GetFile234Data(vtfContainer):
    """
    # THERMAL THROTTLING RELATED OFFSETS
    THROTTLING_NAND_HIGH_TEMP_THRESHOLD_1_OFFSET   = 0x15C
    THROTTLING_NAND_LOW_TEMP_THRESHOLD_1_OFFSET    = 0x15D
    THROTTLING_SCHEME_OFFSET                       = 0x15E
    THROTTLING_NAND_HIGH_TEMP_THRESHOLD_2_OFFSET   = 0x15F
    THROTTLING_NAND_LOW_TEMP_THRESHOLD_2_OFFSET    = 0x160
    THROTTLING_ASIC_HIGH_TEMP_THRESHOLD_1_OFFSET   = 0x161
    THROTTLING_ASIC_LOW_TEMP_THRESHOLD_1_OFFSET    = 0x162
    THROTTLING_ASIC_HIGH_TEMP_THRESHOLD_2_OFFSET   = 0x163
    THROTTLING_ASIC_LOW_TEMP_THRESHOLD_2_OFFSET    = 0x164
    THROTTLING_NUM_OF_SECTORS_TO_POLL              = 0x165
    THROTTLING_SECOND_THRESHOLD_WRITE_DELAY        = 0x167
    THROTTLING_SECOND_THRESHOLD_READ_DELAY         = 0x168
    THROTTLING_FIRST_THRESHOLD_WRITE_DELAY         = 0x169
    THROTTLING_FIRST_THRESHOLD_READ_DELAY          = 0x16A
    THROTTLING_TEMPERATURE_POLLING_DIE             = 0x16B
    THROTTLING_NOP_MULTIPLIER                      = 0x16C

    FILE_ID = 234
    fileBuf = DiagnosticLib.ReadFileSystem(vtfContainer, fileID=FILE_ID)

    configParams = {"THROTTLING_ASIC_ENABLE":None, "THROTTLING_NAND_ENABLE":None, "NAND_HIGH_TEMP_THRESHOLD1":None,"NAND_LOW_TEMP_THRESHOLD1":None, "NAND_HIGH_TEMP_THRESHOLD2":None, \
                    "NAND_LOW_TEMP_THRESHOLD2":None, "ASIC_HIGH_TEMP_THRESHOLD1":None, "ASIC_LOW_TEMP_THRESHOLD1":None, "ASIC_HIGH_TEMP_THRESHOLD2":None, "ASIC_LOW_TEMP_THRESHOLD2":None, \
                    "NUM_OF_SECTORS_TO_POLL":None, "FIRST_THRESHOLD_WRITE_DELAY":None, "FIRST_THRESHOLD_READ_DELAY":None, "SECOND_THRESHOLD_WRITE_DELAY":None, "SECOND_THRESHOLD_READ_DELAY":None, \
                    "TEMPERATURE_POLLING_DIE":None, "NOP_MULTIPLIER":None}

    configParams["NAND_HIGH_TEMP_THRESHOLD1"]      =    fileBuf.GetOneByteToInt(THROTTLING_NAND_HIGH_TEMP_THRESHOLD_1_OFFSET)
    configParams["NAND_LOW_TEMP_THRESHOLD1"]       =    fileBuf.GetOneByteToInt(THROTTLING_NAND_LOW_TEMP_THRESHOLD_1_OFFSET)
    configParams["THROTTLING_ASIC_ENABLE"]         =    fileBuf.GetOneByteToInt(THROTTLING_SCHEME_OFFSET) & 1
    configParams["THROTTLING_NAND_ENABLE"]         =    (fileBuf.GetOneByteToInt(THROTTLING_SCHEME_OFFSET) & 2) >> 1
    configParams["NAND_HIGH_TEMP_THRESHOLD2"]      =    fileBuf.GetOneByteToInt(THROTTLING_NAND_HIGH_TEMP_THRESHOLD_2_OFFSET)
    configParams["NAND_LOW_TEMP_THRESHOLD2"]       =    fileBuf.GetOneByteToInt(THROTTLING_NAND_LOW_TEMP_THRESHOLD_2_OFFSET)
    configParams["ASIC_HIGH_TEMP_THRESHOLD1"]      =    fileBuf.GetOneByteToInt(THROTTLING_ASIC_HIGH_TEMP_THRESHOLD_1_OFFSET)
    configParams["ASIC_LOW_TEMP_THRESHOLD1"]       =    fileBuf.GetOneByteToInt(THROTTLING_ASIC_LOW_TEMP_THRESHOLD_1_OFFSET)
    configParams["ASIC_HIGH_TEMP_THRESHOLD2"]      =    fileBuf.GetOneByteToInt(THROTTLING_ASIC_HIGH_TEMP_THRESHOLD_2_OFFSET)
    configParams["ASIC_LOW_TEMP_THRESHOLD2"]       =    fileBuf.GetOneByteToInt(THROTTLING_ASIC_LOW_TEMP_THRESHOLD_2_OFFSET)
    configParams["NUM_OF_SECTORS_TO_POLL"]         =    fileBuf.GetTwoBytesToInt(THROTTLING_NUM_OF_SECTORS_TO_POLL)
    configParams["FIRST_THRESHOLD_WRITE_DELAY"]    =    fileBuf.GetOneByteToInt(THROTTLING_FIRST_THRESHOLD_WRITE_DELAY)
    configParams["FIRST_THRESHOLD_READ_DELAY"]     =    fileBuf.GetOneByteToInt(THROTTLING_FIRST_THRESHOLD_READ_DELAY)
    configParams["SECOND_THRESHOLD_WRITE_DELAY"]   =    fileBuf.GetOneByteToInt(THROTTLING_SECOND_THRESHOLD_WRITE_DELAY)
    configParams["SECOND_THRESHOLD_READ_DELAY"]    =    fileBuf.GetOneByteToInt(THROTTLING_SECOND_THRESHOLD_READ_DELAY)
    configParams["TEMPERATURE_POLLING_DIE"]        =    fileBuf.GetOneByteToInt(THROTTLING_TEMPERATURE_POLLING_DIE)
    configParams["NOP_MULTIPLIER"]                 =    fileBuf.GetOneByteToInt(THROTTLING_NOP_MULTIPLIER)

    return configParams
    """
    # New offsets for Extremes/x4
    # THERMAL THROTTLING RELATED OFFSETS
    X6_TEMPERATURE_OFFSET = 0x15C
    X5_TEMPERATURE_OFFSET = 0x15D
    X4_TEMPERATURE_OFFSET = 0x15E
    X3_TEMPERATURE_OFFSET = 0x15F
    X2_TEMPERATURE_OFFSET = 0x160
    X1_TEMPERATURE_OFFSET = 0x161
    FREQ_SET_TO_BE_USED_FOR_X6_OFFSET = 0x162 #[4:7]
    FREQ_SET_TO_BE_USED_FOR_X5_OFFSET = 0x162 #[0:3]
    FREQ_SET_TO_BE_USED_FOR_X4_OFFSET = 0x163
    FREQ_SET_TO_BE_USED_FOR_X3_OFFSET = 0x163
    FREQ_SET_TO_BE_USED_FOR_X2_OFFSET = 0x164
    FREQ_SET_TO_BE_USED_FOR_X1_OFFSET = 0x164
    ASIC_HIGH_TEMPERATURE_OFFSET = 0x165
    ASIC_LOW_TEMPERATURE_OFFSET = 0x165
    ASIC_HARD_STOP_DELAY_SET_OFFSET = 0x166
    NAND_TEMPERATURE_PREDICTIVE_THROTTLING_ENABLE_OFFSET = 0x167 # [0]
    ASIC_FULL_THROTTLE_FEATURE_ENABLE_OFFSET = 0x167 # [1]
    DTT_SCHEME_DELAY_FREQUENCYSCALING_OFFSET = 0x167 # [2]
    X6_DELAY_FOR_WRITES_OFFSET = 0x168
    X6_DELAY_FOR_READS_OFFSET = 0x169
    X5_DELAY_FOR_WRITES_OFFSET = 0x16A
    X5_DELAY_FOR_READS_OFFSET = 0x16B
    X4_DELAY_FOR_WRITES_OFFSET = 0x16C
    X4_DELAY_FOR_READS_OFFSET = 0x16D
    X3_DELAY_FOR_WRITES_OFFSET = 0x16E
    X3_DELAY_FOR_READS_OFFSET = 0x16F
    X2_DELAY_FOR_WRITES_OFFSET = 0x170
    X2_DELAY_FOR_READS_OFFSET = 0x171
    X1_DELAY_FOR_WRITES_OFFSET = 0x172
    X1_DELAY_FOR_READS_OFFSET = 0x173
    DELAY_MULTIPLIER_FOR_READS_OFFSET = 0x174
    DELAY_MULTIPLIER_FOR_WRITES_OFFSET = 0x175
    DIE_TO_POLL_OFFSET = 0x176
    NUM_OF_SECTORS_TO_POLL_OFFSET = 0x177 # 2bytes
    SAMPLE_THRESHOLD_OFFSET = 0x179

    FILE_ID = 234
    fileBuf = DiagnosticLib.ReadFileSystem(vtfContainer, fileID=FILE_ID)

    configParams = {"X6_TEMPERATURE":None, "X5_TEMPERATURE":None, "X4_TEMPERATURE":None, "X3_TEMPERATURE":None, "X2_TEMPERATURE":None, "X1_TEMPERATURE":None, "FREQ_SET_TO_BE_USED_FOR_X6":None, "FREQ_SET_TO_BE_USED_FOR_X5":None, "FREQ_SET_TO_BE_USED_FOR_X4":None, \
                    "FREQ_SET_TO_BE_USED_FOR_X3":None, "FREQ_SET_TO_BE_USED_FOR_X2":None, "FREQ_SET_TO_BE_USED_FOR_X1":None, "ASIC_HIGH_TEMPERATURE":None, "ASIC_LOW_TEMPERATURE":None, "NAND_TEMPERATURE_PREDICTIVE_THROTTLING_ENABLE":None, \
                    "ASIC_FULL_THROTTLE_FEATURE_ENABLE":None, "DTT_SCHEME_DELAY_FREQUENCYSCALING":None, "DTT_SCHEME_FREQUENCYSCALING":None, "ASIC_HARD_STOP_DELAY_SET":None, "X6_DELAY_FOR_WRITES":None, "X6_DELAY_FOR_READS":None, "X5_DELAY_FOR_WRITES":None, "X5_DELAY_FOR_READS":None, \
                    "X4_DELAY_FOR_WRITES":None, "X4_DELAY_FOR_READS":None, "X3_DELAY_FOR_WRITES":None, "X3_DELAY_FOR_READS":None, "X2_DELAY_FOR_WRITES":None, "X2_DELAY_FOR_READS":None, "X1_DELAY_FOR_WRITES":None, "X1_DELAY_FOR_READS":None, \
                    "DELAY_MULTIPLIER_FOR_READS":None, "DELAY_MULTIPLIER_FOR_WRITES":None, "DIE_TO_POLL":None, "NUM_OF_SECTORS_TO_POLL":None, "SAMPLE_THRESHOLD":None}

    configParams["X6_TEMPERATURE"]      =    fileBuf.GetOneByteToInt(X6_TEMPERATURE_OFFSET)
    configParams["X5_TEMPERATURE"]      =    fileBuf.GetOneByteToInt(X5_TEMPERATURE_OFFSET)
    configParams["X4_TEMPERATURE"]      =    fileBuf.GetOneByteToInt(X4_TEMPERATURE_OFFSET)
    configParams["X3_TEMPERATURE"]      =    fileBuf.GetOneByteToInt(X3_TEMPERATURE_OFFSET)
    configParams["X2_TEMPERATURE"]      =    fileBuf.GetOneByteToInt(X2_TEMPERATURE_OFFSET)
    configParams["X1_TEMPERATURE"]      =    fileBuf.GetOneByteToInt(X1_TEMPERATURE_OFFSET)
    configParams["FREQ_SET_TO_BE_USED_FOR_X6"]      =    (fileBuf.GetOneByteToInt(FREQ_SET_TO_BE_USED_FOR_X6_OFFSET) & 0xF0) >> 4
    configParams["FREQ_SET_TO_BE_USED_FOR_X5"]      =    fileBuf.GetOneByteToInt(FREQ_SET_TO_BE_USED_FOR_X5_OFFSET) & 0xF
    configParams["FREQ_SET_TO_BE_USED_FOR_X4"]      =    (fileBuf.GetOneByteToInt(FREQ_SET_TO_BE_USED_FOR_X4_OFFSET) & 0xF0) >> 4
    configParams["FREQ_SET_TO_BE_USED_FOR_X3"]      =    fileBuf.GetOneByteToInt(FREQ_SET_TO_BE_USED_FOR_X3_OFFSET) & 0xF
    configParams["FREQ_SET_TO_BE_USED_FOR_X2"]      =    (fileBuf.GetOneByteToInt(FREQ_SET_TO_BE_USED_FOR_X2_OFFSET) & 0xF0) >> 4
    configParams["FREQ_SET_TO_BE_USED_FOR_X1"]      =    fileBuf.GetOneByteToInt(FREQ_SET_TO_BE_USED_FOR_X1_OFFSET) & 0xF
    configParams["ASIC_HIGH_TEMPERATURE"]      =    (fileBuf.GetOneByteToInt(ASIC_HIGH_TEMPERATURE_OFFSET) & 0xF0) >> 4
    configParams["ASIC_LOW_TEMPERATURE"]      =    fileBuf.GetOneByteToInt(ASIC_LOW_TEMPERATURE_OFFSET) & 0xF
    configParams["NAND_TEMPERATURE_PREDICTIVE_THROTTLING_ENABLE"]      =    fileBuf.GetOneByteToInt(NAND_TEMPERATURE_PREDICTIVE_THROTTLING_ENABLE_OFFSET) & 0x1
    configParams["ASIC_FULL_THROTTLE_FEATURE_ENABLE"]      =    (fileBuf.GetOneByteToInt(ASIC_FULL_THROTTLE_FEATURE_ENABLE_OFFSET) & 0x2) >> 1
    configParams["DTT_SCHEME_DELAY_FREQUENCYSCALING"]      =    (fileBuf.GetOneByteToInt(DTT_SCHEME_DELAY_FREQUENCYSCALING_OFFSET) & 0x4) >> 2
    configParams["DTT_SCHEME_FREQUENCYSCALING"]      =    (fileBuf.GetOneByteToInt(DTT_SCHEME_DELAY_FREQUENCYSCALING_OFFSET) & 0x8) >> 3
    configParams["ASIC_HARD_STOP_DELAY_SET"]      =    fileBuf.GetOneByteToInt(ASIC_HARD_STOP_DELAY_SET_OFFSET)
    configParams["X6_DELAY_FOR_WRITES"]      =    fileBuf.GetOneByteToInt(X6_DELAY_FOR_WRITES_OFFSET)
    configParams["X6_DELAY_FOR_READS"]      =    fileBuf.GetOneByteToInt(X6_DELAY_FOR_READS_OFFSET)
    configParams["X5_DELAY_FOR_WRITES"]      =    fileBuf.GetOneByteToInt(X5_DELAY_FOR_WRITES_OFFSET)
    configParams["X5_DELAY_FOR_READS"]      =    fileBuf.GetOneByteToInt(X5_DELAY_FOR_READS_OFFSET)
    configParams["X4_DELAY_FOR_WRITES"]      =    fileBuf.GetOneByteToInt(X4_DELAY_FOR_WRITES_OFFSET)
    configParams["X4_DELAY_FOR_READS"]      =    fileBuf.GetOneByteToInt(X4_DELAY_FOR_READS_OFFSET)
    configParams["X3_DELAY_FOR_WRITES"]      =    fileBuf.GetOneByteToInt(X3_DELAY_FOR_WRITES_OFFSET)
    configParams["X3_DELAY_FOR_READS"]      =    fileBuf.GetOneByteToInt(X3_DELAY_FOR_READS_OFFSET)
    configParams["X2_DELAY_FOR_WRITES"]      =    fileBuf.GetOneByteToInt(X2_DELAY_FOR_WRITES_OFFSET)
    configParams["X2_DELAY_FOR_READS"]      =    fileBuf.GetOneByteToInt(X2_DELAY_FOR_READS_OFFSET)
    configParams["X1_DELAY_FOR_WRITES"]      =    fileBuf.GetOneByteToInt(X1_DELAY_FOR_WRITES_OFFSET)
    configParams["X1_DELAY_FOR_READS"]      =    fileBuf.GetOneByteToInt(X1_DELAY_FOR_READS_OFFSET)
    configParams["DELAY_MULTIPLIER_FOR_READS"]      =    fileBuf.GetOneByteToInt(DELAY_MULTIPLIER_FOR_READS_OFFSET)
    configParams["DELAY_MULTIPLIER_FOR_WRITES"]      =    fileBuf.GetOneByteToInt(DELAY_MULTIPLIER_FOR_WRITES_OFFSET)
    configParams["DIE_TO_POLL"]      =    fileBuf.GetOneByteToInt(DIE_TO_POLL_OFFSET)
    configParams["NUM_OF_SECTORS_TO_POLL"]      =    fileBuf.GetTwoBytesToInt(NUM_OF_SECTORS_TO_POLL_OFFSET)
    configParams["SAMPLE_THRESHOLD"]      =    fileBuf.GetOneByteToInt(SAMPLE_THRESHOLD_OFFSET)

    return configParams
#end of GetFile234Data()


def GetFile23Data(vtfContainer):
    #Recheck : Sangeetha
    CLOCK_FREQUENCY_SET_USED_FROM_TRIMFILE_LS      = 0xC0
    CLOCK_FREQUENCY_SET_USED_FROM_TRIMFILE_HS      = 0xF0
    CLOCK_FREQUENCY_SET_USED_FROM_TRIMFILE_SDR50   = 0x138
    CLOCK_FREQUENCY_SET_USED_FROM_TRIMFILE_SDR104  = 0x150
    CLOCK_FREQUENCY_SET_USED_FROM_TRIMFILE_DDR50   = 0x168
    CLOCK_FREQUENCY_SET_USED_FROM_TRIMFILE_DDR200  = 0x180

    FILE_ID = 23
    fileBuf = DiagnosticLib.ReadFileSystem(vtfContainer, fileID=FILE_ID)

    configParams = {"clkSetUsedLS":None, "clkSetUsedHS":None, "clkSetUsedSDR50":None, "clkSetUsedSDR104":None, "clkSetUsedDDR50":None, "clkSetUsedDDR200":None}

    configParams["clkSetUsedLS"]                   =    fileBuf.GetOneByteToInt(CLOCK_FREQUENCY_SET_USED_FROM_TRIMFILE_LS)
    configParams["clkSetUsedHS"]                   =    fileBuf.GetOneByteToInt(CLOCK_FREQUENCY_SET_USED_FROM_TRIMFILE_HS)
    configParams["clkSetUsedSDR50"]                =    fileBuf.GetOneByteToInt(CLOCK_FREQUENCY_SET_USED_FROM_TRIMFILE_SDR50)
    configParams["clkSetUsedSDR104"]               =    fileBuf.GetOneByteToInt(CLOCK_FREQUENCY_SET_USED_FROM_TRIMFILE_SDR104)
    configParams["clkSetUsedDDR50"]                =    fileBuf.GetOneByteToInt(CLOCK_FREQUENCY_SET_USED_FROM_TRIMFILE_DDR50)
    configParams["clkSetUsedDDR200"]               =    fileBuf.GetOneByteToInt(CLOCK_FREQUENCY_SET_USED_FROM_TRIMFILE_DDR200)

    return configParams


class GrownBadBlockFileData(object):
    """
    This class is used to read/parse/write Grown Bad Block File Data (File 226).
    """
    ##to recheck: systems/FW
    FILE_ID = 226
    FILE_226_GROWN_DEFECT_BLOCKS_COUNT_OFFSET = 0x02
    FILE_226_GBB_VERSION = 0x00
    FILE_226_GROWN_DEFECT_FILE_SIZE_PER_BANK_IN_SECTORS = 0x04
    #Offsets

    def __init__(self,vtfContainer,GBBLSizePerBank,numBanks=1):
        """
        Name : __init__
        Description :
                 Constructor of the class. It calls RefreshData() function for getting all the variables
        Arguments :
                vtfContainer : vtfContainer of the card
                GBBLSizePerBank: Size of GBBL per bank
                numBanks: Number of Banks

        Return
             None
        """
        # Initialize all the configuration file variables (to remove pylintm error and to access these variables from Wing-IDE)
        self.vtfContainer = vtfContainer
        self.fileVersion = 0
        self.grownDefectFileSizePerBank = GBBLSizePerBank
        self.numOfBanks = numBanks
        # callinfg refresh data function for getting all configuration values
        self.RefreshData(vtfContainer)
    #end of __init__

    def RefreshData(self,vtfContainer):
        """
        Name : RefreshData
        Description :
                 This function read the latest File data and update the same
        Arguments :
                vtfContainer : vtfContainer of the card
        Return
             None
        """
        #read the file data
        fileBuf,fileSize = self.__DoFileRead(vtfContainer)

        #Parse the Configuration data from the file buffer
        self.__ParseConfigurationData(fileBuf)
    #end of RefreshData
    def __ParseConfigurationData(self,fileBuf):
        """
        Name : __ParseConfigurationData
        Description :
                 This function parse the data from file buffer
        Arguments :
                fileBuf   : configuration file buffer
        Return
             None
        """
        self.fileVersion = fileBuf.GetTwoBytesToInt(self.FILE_226_GBB_VERSION)
    #end of __ParseConfigurationData

    def __DoFileRead(self,vtfContainer):
        """
        Name : __DoFileRead
        Description :
                 This function read the lates File data and return the buffer data
        Arguments :
                vtfContainer : vtfContainer of the card
        Return
               fileBuf     : file buffer
               fileSize    : file buffer size
        """
        fileSize, fileSizeBytes = DiagnosticLib.LengthOfFileInBytes(fileId=self.FILE_ID)
        fileBuf = DiagnosticLib.ReadFileSystem(vtfContainer, fileID=self.FILE_ID, sectorCount=fileSize)

        return fileBuf,fileSize
    #end of __DoFileRead
    def GetGrownDefectBlocksCount(self,vtfContainer):
        """
        Name : GetGrownDefectBlocksCount
        Description :
                 This function returns the count of Grown bad blocks in each bank
        Arguments :
                vtfContainer   : vtfContainer of the card
        Return
               GrownBadBlockCountArray: Array containing the count of GBB in each Bank
        """
        #read the file data
        fileBuf,fileSize = self.__DoFileRead(vtfContainer)
        GrownBadBlockCountArray = []
        for i in range(self.numOfBanks):
            GrownBadBlockCountArray.append(fileBuf.GetTwoBytesToInt(i * self.grownDefectFileSizePerBank + self.FILE_226_GROWN_DEFECT_BLOCKS_COUNT_OFFSET))
        return GrownBadBlockCountArray
    # End of GetGrownDefectBlocksCount

    def GetGrownBadBlockFileVersion(self,vtfContainer):
        """
        Name : GetGrownBadBlockFileVersion
        Description :
                 returns version of GBB file
        Arguments :
                 vtfContainer   : vtfContainer of the card
        Return
                 version of GBB file
        """
        #read the file data
        fileBuf,fileSize = self.__DoFileRead(vtfContainer)
        fileVersion = fileBuf.GetTwoBytesToInt(self.FILE_226_GBB_VERSION)

        return fileVersion

    # End of GetGrownBadBlockFileVersion

#end of class


class ConfigurationFile35Data(object):
    """
    This class is used to read/parse/write configuration file (File 21) data
    """
    FILE_ID = 35

    # SLC SGD PARAMETERS
    FILE35_SLC_SGD_ENABLE = 0x33
    FILE35_SLC_SGD_LT_PECOUNT = 0x34
    FILE35_SLC_SGD_LT_FREQUENCY = 0x36
    FILE35_SLC_SGD_DETAILED_ENABLE = 0x38
    FILE35_SLC_SGD_UT_FBC = 0x39
    FILE35_SLC_SGD_UT_VT = 0x3A
    FILE35_SLC_SGD_LT_FBC = 0x3C
    FILE35_SLC_SGD_LT_VT = 0x3D
    FILE35_SLC_SGD_OP_FBC = 0x3F
    FILE35_SLC_SGD_OP_VT = 0x40
    FILE35_SLC_SGD_UT_PECOUNT = 0x42
    FILE35_SLC_SGD_UT_FREQUENCY = 0x44

    # SLC SGS PARAMETERS
    FILE35_SLC_SGS_ENABLE = 0x47
    FILE35_SLC_SGS_LT_PECOUNT = 0x48
    FILE35_SLC_SGS_LT_FREQUENCY = 0x4A
    FILE35_SLC_SGS_DETAILED_ENABLE = 0x4C
    FILE35_SLC_SGS_UT_FBC = 0x4D
    FILE35_SLC_SGS_UT_VT = 0x4E
    FILE35_SLC_SGS_LT_FBC = 0x50
    FILE35_SLC_SGS_LT_VT = 0x51
    FILE35_SLC_SGS_OP_FBC = 0x53
    FILE35_SLC_SGS_OP_VT = 0x54
    FILE35_SLC_SGS_UT_PECOUNT = 0x56
    FILE35_SLC_SGS_UT_FREQUENCY = 0x58

    # TLC SGD PARAMETERS
    FILE35_TLC_SGD_ENABLE = 0x5B
    FILE35_TLC_SGD_LT_PECOUNT = 0x5C
    FILE35_TLC_SGD_LT_FREQUENCY = 0x5D
    FILE35_TLC_SGD_UT_PECOUNT = 0x5E
    FILE35_TLC_SGD_UT_FREQUENCY = 0x5F
    FILE35_TLC_SGD_DETAILED_ENABLE = 0x64
    FILE35_TLC_SGD_UT_FBC = 0x65
    FILE35_TLC_SGD_UT_VT = 0x66
    FILE35_TLC_SGD_LT_FBC = 0x68
    FILE35_TLC_SGD_LT_VT = 0x69
    FILE35_TLC_SGD_OP_FBC = 0x6B
    FILE35_TLC_SGD_OP_VT = 0x6C

    # TLC SGS PARAMETERS
    FILE35_TLC_SGS_ENABLE = 0x73
    FILE35_TLC_SGS_LT_PECOUNT = 0x74
    FILE35_TLC_SGS_LT_FREQUENCY = 0x75
    FILE35_TLC_SGS_UT_PECOUNT = 0x76
    FILE35_TLC_SGS_UT_FREQUENCY = 0x77
    FILE35_TLC_SGS_DETAILED_ENABLE = 0x78
    FILE35_TLC_SGS_UT_FBC = 0x79
    FILE35_TLC_SGS_UT_VT = 0x7A
    FILE35_TLC_SGS_LT_FBC = 0x7C
    FILE35_TLC_SGS_LT_VT = 0x7D
    FILE35_TLC_SGS_OP_FBC = 0x7F
    FILE35_TLC_SGS_OP_VT = 0x80


    def __init__(self, vtfContainer):
        self.vtfContainer = vtfContainer
        # Initialize all the configuration file variables
        # SLC SGD PARAMETERS
        self.SLC_SGD_ENABLE = None
        self.SLC_SGD_LT_PECOUNT = None
        self.SLC_SGD_LT_FREQUENCY = None
        self.SLC_SGD_DETAILED_ENABLE = None
        self.SLC_SGD_UT_FBC = None
        self.SLC_SGD_UT_VT = None
        self.SLC_SGD_LT_FBC = None
        self.SLC_SGD_LT_VT = None
        self.SLC_SGD_OP_FBC = None
        self.SLC_SGD_OP_VT = None
        self.SLC_SGD_UT_PECOUNT = None
        self.SLC_SGD_UT_FREQUENCY = None

        # SLC SGS PARAMETERS
        self.SLC_SGS_ENABLE = None
        self.SLC_SGS_LT_PECOUNT = None
        self.SLC_SGS_LT_FREQUENCY = None
        self.SLC_SGS_DETAILED_ENABLE = None
        self.SLC_SGS_UT_FBC = None
        self.SLC_SGS_UT_VT = None
        self.SLC_SGS_LT_FBC = None
        self.SLC_SGS_LT_VT = None
        self.SLC_SGS_OP_FBC = None
        self.SLC_SGS_OP_VT = None
        self.SLC_SGS_UT_PECOUNT = None
        self.SLC_SGS_UT_FREQUENCY = None

        # TLC SGD PARAMETERS
        self.TLC_SGD_ENABLE = None
        self.TLC_SGD_LT_PECOUNT = None
        self.TLC_SGD_LT_FREQUENCY = None
        self.TLC_SGD_UT_PECOUNT = None
        self.TLC_SGD_UT_FREQUENCY = None
        self.TLC_SGD_DETAILED_ENABLE = None
        self.TLC_SGD_UT_FBC = None
        self.TLC_SGD_UT_VT = None
        self.TLC_SGD_LT_FBC = None
        self.TLC_SGD_LT_VT = None
        self.TLC_SGD_OP_FBC = None
        self.TLC_SGD_OP_VT = None

        # TLC SGS PARAMETERS
        self.TLC_SGS_ENABLE = None
        self.TLC_SGS_LT_PECOUNT = None
        self.TLC_SGS_LT_FREQUENCY = None
        self.TLC_SGS_UT_PECOUNT = None
        self.TLC_SGS_UT_FREQUENCY = None
        self.TLC_SGS_DETAILED_ENABLE = None
        self.TLC_SGS_UT_FBC = None
        self.TLC_SGS_UT_VT = None
        self.TLC_SGS_LT_FBC = None
        self.TLC_SGS_LT_VT = None
        self.TLC_SGS_OP_FBC = None
        self.TLC_SGS_OP_VT = None

        #calling refresh data function for getting all configuration values
        self.RefreshData(vtfContainer)
        #end of __init__

    def RefreshData(self, vtfContainer):
        """
        Name : RefreshData
        Description :
        This function read the latest Configuration File and update all the configuration data
        Return
        None
        """
        #read the file data
        fileBuf, fileSize = self.__DoFileRead()

        #Parse the Configuration data from the file buffer
        self.__ParseConfigurationData(fileBuf)
    #end of RefreshData


    def __ParseConfigurationData(self,fileBuf):
        """
        Name : __ParseConfigurationData
        Description :
                 This function parse the data from file buffer
        Arguments :
                fileBuf   : configuration file buffer
        Return
             None
        """
        # SLC SGD PARAMETERS
        self.SLC_SGD_ENABLE = fileBuf.GetOneByteToInt(self.FILE35_SLC_SGD_ENABLE)
        self.SLC_SGD_LT_PECOUNT = fileBuf.GetTwoBytesToInt(self.FILE35_SLC_SGD_LT_PECOUNT)
        self.SLC_SGD_LT_FREQUENCY = fileBuf.GetTwoBytesToInt(self.FILE35_SLC_SGD_LT_FREQUENCY)
        self.SLC_SGD_DETAILED_ENABLE = fileBuf.GetOneByteToInt(self.FILE35_SLC_SGD_DETAILED_ENABLE)
        self.SLC_SGD_UT_FBC = fileBuf.GetOneByteToInt(self.FILE35_SLC_SGD_UT_FBC)
        self.SLC_SGD_UT_VT = fileBuf.GetTwoBytesToInt(self.FILE35_SLC_SGD_UT_VT)
        self.SLC_SGD_LT_FBC = fileBuf.GetOneByteToInt(self.FILE35_SLC_SGD_LT_FBC)
        self.SLC_SGD_LT_VT = fileBuf.GetTwoBytesToInt(self.FILE35_SLC_SGD_LT_VT)
        self.SLC_SGD_OP_FBC = fileBuf.GetOneByteToInt(self.FILE35_SLC_SGD_OP_FBC)
        self.SLC_SGD_OP_VT = fileBuf.GetTwoBytesToInt(self.FILE35_SLC_SGD_OP_VT)
        self.SLC_SGD_UT_PECOUNT = fileBuf.GetTwoBytesToInt(self.FILE35_SLC_SGD_UT_PECOUNT)
        self.SLC_SGD_UT_FREQUENCY = fileBuf.GetTwoBytesToInt(self.FILE35_SLC_SGD_UT_FREQUENCY)

        # SLC SGS PARAMETERS
        self.SLC_SGS_ENABLE = fileBuf.GetOneByteToInt(self.FILE35_SLC_SGS_ENABLE)
        self.SLC_SGS_LT_PECOUNT = fileBuf.GetTwoBytesToInt(self.FILE35_SLC_SGS_LT_PECOUNT)
        self.SLC_SGS_LT_FREQUENCY = fileBuf.GetTwoBytesToInt(self.FILE35_SLC_SGS_LT_FREQUENCY)
        self.SLC_SGS_DETAILED_ENABLE = fileBuf.GetOneByteToInt(self.FILE35_SLC_SGS_DETAILED_ENABLE)
        self.SLC_SGS_UT_FBC = fileBuf.GetOneByteToInt(self.FILE35_SLC_SGS_UT_FBC)
        self.SLC_SGS_UT_VT = fileBuf.GetTwoBytesToInt(self.FILE35_SLC_SGS_UT_VT)
        self.SLC_SGS_LT_FBC = fileBuf.GetOneByteToInt(self.FILE35_SLC_SGS_LT_FBC)
        self.SLC_SGS_LT_VT = fileBuf.GetTwoBytesToInt(self.FILE35_SLC_SGS_LT_VT)
        self.SLC_SGS_OP_FBC = fileBuf.GetOneByteToInt(self.FILE35_SLC_SGS_OP_FBC)
        self.SLC_SGS_OP_VT = fileBuf.GetTwoBytesToInt(self.FILE35_SLC_SGS_OP_VT)
        self.SLC_SGS_UT_PECOUNT = fileBuf.GetTwoBytesToInt(self.FILE35_SLC_SGS_UT_PECOUNT)
        self.SLC_SGS_UT_FREQUENCY = fileBuf.GetTwoBytesToInt(self.FILE35_SLC_SGS_UT_FREQUENCY)

        # TLC SGD PARAMETERS
        self.TLC_SGD_ENABLE = fileBuf.GetOneByteToInt(self.FILE35_TLC_SGD_ENABLE)
        self.TLC_SGD_LT_PECOUNT = fileBuf.GetOneByteToInt(self.FILE35_TLC_SGD_LT_PECOUNT)
        self.TLC_SGD_LT_FREQUENCY = fileBuf.GetOneByteToInt(self.FILE35_TLC_SGD_LT_FREQUENCY)
        self.TLC_SGD_UT_PECOUNT = fileBuf.GetOneByteToInt(self.FILE35_TLC_SGD_UT_PECOUNT)
        self.TLC_SGD_UT_FREQUENCY = fileBuf.GetOneByteToInt(self.FILE35_TLC_SGD_UT_FREQUENCY)
        self.TLC_SGD_DETAILED_ENABLE = fileBuf.GetOneByteToInt(self.FILE35_TLC_SGD_DETAILED_ENABLE)
        self.TLC_SGD_UT_FBC = fileBuf.GetOneByteToInt(self.FILE35_TLC_SGD_UT_FBC)
        self.TLC_SGD_UT_VT = fileBuf.GetTwoBytesToInt(self.FILE35_TLC_SGD_UT_VT)
        self.TLC_SGD_LT_FBC = fileBuf.GetOneByteToInt(self.FILE35_TLC_SGD_LT_FBC)
        self.TLC_SGD_LT_VT = fileBuf.GetTwoBytesToInt(self.FILE35_TLC_SGD_LT_VT)
        self.TLC_SGD_OP_FBC = fileBuf.GetOneByteToInt(self.FILE35_TLC_SGD_OP_FBC)
        self.TLC_SGD_OP_VT = fileBuf.GetTwoBytesToInt(self.FILE35_TLC_SGD_OP_VT)

        # TLC SGS PARAMETERS
        self.TLC_SGS_ENABLE = fileBuf.GetOneByteToInt(self.FILE35_TLC_SGS_ENABLE)
        self.TLC_SGS_LT_PECOUNT = fileBuf.GetOneByteToInt(self.FILE35_TLC_SGS_LT_PECOUNT)
        self.TLC_SGS_LT_FREQUENCY = fileBuf.GetOneByteToInt(self.FILE35_TLC_SGS_LT_FREQUENCY)
        self.TLC_SGS_UT_PECOUNT = fileBuf.GetOneByteToInt(self.FILE35_TLC_SGS_UT_PECOUNT)
        self.TLC_SGS_UT_FREQUENCY = fileBuf.GetOneByteToInt(self.FILE35_TLC_SGS_UT_FREQUENCY)
        self.TLC_SGS_DETAILED_ENABLE = fileBuf.GetOneByteToInt(self.FILE35_TLC_SGS_DETAILED_ENABLE)
        self.TLC_SGS_UT_FBC = fileBuf.GetOneByteToInt(self.FILE35_TLC_SGS_UT_FBC)
        self.TLC_SGS_UT_VT = fileBuf.GetTwoBytesToInt(self.FILE35_TLC_SGS_UT_VT)
        self.TLC_SGS_LT_FBC = fileBuf.GetOneByteToInt(self.FILE35_TLC_SGS_LT_FBC)
        self.TLC_SGS_LT_VT = fileBuf.GetTwoBytesToInt(self.FILE35_TLC_SGS_LT_VT)
        self.TLC_SGS_OP_FBC = fileBuf.GetOneByteToInt(self.FILE35_TLC_SGS_OP_FBC)
        self.TLC_SGS_OP_VT = fileBuf.GetTwoBytesToInt(self.FILE35_TLC_SGS_OP_VT)

        #end of __ParseConfigurationData

    def SetBytes(self,offset,numOfBytes):
        """
        Name : SetBytes
        Description :
                 It is used to set/clear bits
        Return
             None
        """

        #read the file data
        fileBuf, fileSize = self.__DoFileRead()

        #set this byte in
        if numOfBytes == 1:
            fileBuf.SetByte(offset,value)
        elif numOfBytes == 2:
            fileBuf.SetTwoBytes(offset,value)
        else:
            assert (numOfBytes <= 2), "Number of bytes greater than 2 bytes not handled."

        #do write file
        self.__DoWriteFile(fileBuf,fileSize)

        Utils.PowerCycle(self.vtfContainer)

        #Parse the file data
        self.__ParseConfigurationData(fileBuf)
    # End of SetBytes

    def __DoFileRead(self):
        """
        Name : __DoFileRead
        Description :
                 This function read the lates Configuration File and return the buffer data
        Return
               fileBuf     : file buffer
        """
        fileBuf = DiagnosticLib.ReadFileSystem(self.vtfContainer, fileID=self.FILE_ID)
        fileSizeSectors, fileSizeBytes = DiagnosticLib.LengthOfFileInBytes(fileId=self.FILE_ID)
        return fileBuf, fileSizeSectors
    #end of __DoFileRead

    def __DoWriteFile(self,fileBuf,fileSize):
        """
        Name : __DoWriteFile
        Description :
                 This function write the file data to card
        Arguments :
                fileBuf     : file buffer
                fileSize    : file buffer size
        Return
               None
        """
        DiagnosticLib.WriteFileSystem(self.vtfContainer, fileID= self.FILE_ID,  sectorCount = fileSize, dataBuffer= fileBuf)
        return
    #end of __DoWriteFile

    def SetSGDSGSCountandFrequency(self):
        """
        Name : SetBytes
        Description :
                 It is used to set/clear bits
        Return
             None
        """

        #read the file data
        fileBuf,fileSize = self.__DoFileRead()

        """
        SetByte - For one Byte
        SetTwoBytes - For two Bytes
        """
        # Enable Section
        # SLC SGD
        #fileBuf.SetByte(self.FILE35_SLC_SGD_ENABLE, 1)
        #fileBuf.SetByte(self.FILE35_SLC_SGD_DETAILED_ENABLE, 5)
        # SLC SGS
        #fileBuf.SetByte(self.FILE35_SLC_SGS_ENABLE, 1)
        #fileBuf.SetByte(self.FILE35_SLC_SGS_DETAILED_ENABLE, 5)
        # TLC SGD
        #fileBuf.SetByte(self.FILE35_TLC_SGD_ENABLE, 1)
        #fileBuf.SetByte(self.FILE35_TLC_SGD_DETAILED_ENABLE, 7)
        # TLC SGS
        #fileBuf.SetByte(self.FILE35_TLC_SGS_ENABLE, 1)
        #fileBuf.SetByte(self.FILE35_TLC_SGS_DETAILED_ENABLE, 5)

        # Change HotCount Threshold and Frequency
        # SLC SGD
        fileBuf.SetTwoBytes(self.FILE35_SLC_SGD_LT_PECOUNT,1)
        fileBuf.SetTwoBytes(self.FILE35_SLC_SGD_LT_FREQUENCY,1)
        fileBuf.SetTwoBytes(self.FILE35_SLC_SGD_UT_PECOUNT,1)
        fileBuf.SetTwoBytes(self.FILE35_SLC_SGD_UT_FREQUENCY,1)
        # SLC SGS
        fileBuf.SetTwoBytes(self.FILE35_SLC_SGS_LT_PECOUNT,1)
        fileBuf.SetTwoBytes(self.FILE35_SLC_SGS_LT_FREQUENCY,1)
        fileBuf.SetTwoBytes(self.FILE35_SLC_SGS_UT_PECOUNT,1)
        fileBuf.SetTwoBytes(self.FILE35_SLC_SGS_UT_FREQUENCY,1)
        # TLC SGD
        fileBuf.SetByte(self.FILE35_TLC_SGD_LT_PECOUNT,1)
        fileBuf.SetByte(self.FILE35_TLC_SGD_LT_FREQUENCY,1)
        fileBuf.SetByte(self.FILE35_TLC_SGD_UT_PECOUNT,1)
        fileBuf.SetByte(self.FILE35_TLC_SGD_UT_FREQUENCY,1)
        # TLC SGS
        fileBuf.SetByte(self.FILE35_TLC_SGS_LT_PECOUNT,1)
        fileBuf.SetByte(self.FILE35_TLC_SGS_LT_FREQUENCY,1)
        fileBuf.SetByte(self.FILE35_TLC_SGS_UT_PECOUNT,1)
        fileBuf.SetByte(self.FILE35_TLC_SGS_UT_FREQUENCY,1)

        #do write file
        self.__DoWriteFile(fileBuf,fileSize)

        Utils.PowerCycle(self.vtfContainer)

        #Parse the file data
        self.__ParseConfigurationData(fileBuf)
    # End of SetBytes

class ConfigurationFile24Data(object):
    """
    Description:
       Contains File 24 Structure
    """
    ##Shaheed : To check once again
    # Parameter IDs
    MAX_TAG_ID = 4
    FILE24_SLC_DR_TAG_ID = 0
    FILE24_TLC_DR_TAG_ID = None
    FILE24_SLC_EPWR_DR_TAG_ID = 1
    FILE24_TLC_EPWR_DR_TAG_ID = 3
    FILE24_TLC_WA_SCAN_TAG_ID = 4

    # Offsets
    FILE24_TLV_START = 0x10

    def __init__(self, vtfContainer):
        """
        Name : __init__
        Description :
                 Constructor of the class.
        Return
             None
        """
        self.vtfContainer = vtfContainer

        # File24 Structures
        # SLC DR - Tag 0
        self.slcStates = None
        self.slcNumberOfCases = None
        self.slcDrTable = {}
        self.slcDrAddressMap = {}
        self.slcDrLevelMap = {}
        # TLC DR - Tag 1
        self.tlcStates = None
        self.tlcNumberOfCases = None
        self.tlcDrTable = {}
        self.tlcDrAddressMap = {}
        self.tlcDrLevelMap = {}
        # SLC EPWR DR - Tag 2
        self.slcEpwrStates = None
        self.slcEpwrNumberOfCases = None
        self.slcEpwrDrTable = {}
        self.slcEpwrDrAddressMap = {}
        self.slcEpwrDrLevelMap = {}
        # TLC EPWR DR - Tag 3
        self.tlcEpwrStates = None
        self.tlcEpwrNumberOfCases = None
        self.tlcEpwrDrTable = {}
        self.tlcEpwrDrAddressMap = {}
        self.tlcEpwrDrLevelMap = {}
        # TLC WA Scan - Tag 4
        self.tlcWaScanStates = None
        self.tlcWaScanNumberOfCases = None
        self.tlcWaScanTable = {}
        self.tlcWaScanAddressMap = {}
        self.tlcWaScanLevelMap = {}

        self.RefreshData()
        return

    def __DoFileRead(self,fileID):
        """
        Name : __DoFileRead
        Description :
             This function read the lates Configuration File and return the buffer data
        Arguments :
            testSpace : testSpace of the card
        Return
               fileBuf     : file buffer
               fileSize    : file buffer size
        """
        fileBuf = DiagnosticLib.ReadFileSystem(self.vtfContainer, fileID)
        fileSizeSectors, fileSizeBytes = DiagnosticLib.LengthOfFileInBytes(fileID)
        return fileBuf, fileSizeSectors

    def RefreshData(self,fileID=24):
        """
        Name : RefreshData
        Description :
                 This function read the latest Configuration File and update all the configuration data
        Arguments :
                testSpace : testSpace of the card
        Return
             None
        """
        # Read the file data
        fileBuf,fileSize = self.__DoFileRead(fileID)

        # Parse the Configuration data from the file buffer
        self.__ParseConfigurationData(fileBuf)
        # End of RefreshData

        return True

    def __ParseConfigurationData(self,fileBuf):
        """
        Name : __ParseConfigurationData
        Description :
                 This function parse the data from file buffer
        Arguments :
                fileBuf   : configuration file buffer
        Return
             None
        """
        currentFileOffset = self.FILE24_TLV_START
        nextFileOffset = None

        while (fileBuf.GetOneByteToInt(currentFileOffset) != 0xFF):
            tagID = fileBuf.GetOneByteToInt(currentFileOffset)
            currentFileOffset += 1
            length = fileBuf.GetTwoBytesToInt(currentFileOffset)
            currentFileOffset += 2
            nextFileOffset = currentFileOffset + length
            if tagID == self.FILE24_SLC_DR_TAG_ID: # SLC DR
                currentFileOffset += 1
                self.slcStates = fileBuf.GetOneByteToInt(currentFileOffset)
                currentFileOffset += 1
                self.slcNumberOfCases = fileBuf.GetOneByteToInt(currentFileOffset)
                currentFileOffset += 1
                for i in range(0, self.slcStates):
                    self.slcDrAddressMap[i] = fileBuf.GetOneByteToInt(currentFileOffset)
                    currentFileOffset += 1
                for i in range(0,self.slcNumberOfCases):
                    stateShifts = []
                    for j in range(0,self.slcStates):
                        """
                        stateShifts.append(fileBuf.GetOneByteToInt(currentFileOffset))
                        currentFileOffset += 1
                        """
                        stateShifts.append(fileBuf.GetTwoBytesToInt(currentFileOffset))
                        currentFileOffset += 2
                    self.slcDrTable[i] = list(stateShifts)
                assert (currentFileOffset == nextFileOffset), "File24 Parsing may be incorrect."
            elif tagID == self.FILE24_TLC_DR_TAG_ID: # TLC DR
                currentFileOffset += 1
                self.tlcStates = fileBuf.GetOneByteToInt(currentFileOffset)
                currentFileOffset += 1
                self.tlcNumberOfCases = fileBuf.GetOneByteToInt(currentFileOffset)
                currentFileOffset += 1
                for i in range(0, self.tlcStates):
                    self.tlcDrAddressMap[i] = fileBuf.GetOneByteToInt(currentFileOffset)
                    currentFileOffset += 1
                for i in range(0, self.tlcStates):
                    self.tlcDrLevelMap[i] = fileBuf.GetOneByteToInt(currentFileOffset)
                    currentFileOffset += 1
                for i in range(0,self.tlcNumberOfCases):
                    stateShifts = []
                    for j in range(0,self.tlcStates):
                        stateShifts.append(fileBuf.GetOneByteToInt(currentFileOffset))
                        currentFileOffset += 1
                    self.tlcDrTable[i] = list(stateShifts)
                assert (currentFileOffset == nextFileOffset), "File24 Parsing may be incorrect."
            elif tagID == self.FILE24_SLC_EPWR_DR_TAG_ID: # SLC EPWR DR
                currentFileOffset += 1
                self.slcEpwrStates = fileBuf.GetOneByteToInt(currentFileOffset)
                currentFileOffset += 1
                self.slcEpwrNumberOfCases = fileBuf.GetOneByteToInt(currentFileOffset)
                currentFileOffset += 1
                for i in range(0, self.slcEpwrStates):
                    self.slcEpwrDrAddressMap[i] = fileBuf.GetOneByteToInt(currentFileOffset)
                    currentFileOffset += 1
                for i in range(0,self.slcEpwrNumberOfCases):
                    stateShifts = []
                    for j in range(0,self.slcEpwrStates):
                        """
                        stateShifts.append(fileBuf.GetOneByteToInt(currentFileOffset))
                        currentFileOffset += 1
                        """
                        stateShifts.append(fileBuf.GetTwoBytesToInt(currentFileOffset))
                        currentFileOffset += 2
                    self.slcEpwrDrTable[i] = list(stateShifts)
                assert (currentFileOffset == nextFileOffset), "File24 Parsing may be incorrect."
            elif tagID == self.FILE24_TLC_EPWR_DR_TAG_ID: # TLC EPWR DR
                currentFileOffset += 1
                self.tlcEpwrStates = fileBuf.GetOneByteToInt(currentFileOffset)
                currentFileOffset += 1
                self.tlcEpwrNumberOfCases = fileBuf.GetOneByteToInt(currentFileOffset)
                currentFileOffset += 1
                for i in range(0, self.tlcEpwrStates):
                    self.tlcEpwrDrAddressMap[i] = fileBuf.GetOneByteToInt(currentFileOffset)
                    currentFileOffset += 1
                for i in range(0, self.tlcEpwrStates):
                    self.tlcEpwrDrLevelMap[i] = fileBuf.GetOneByteToInt(currentFileOffset)
                    currentFileOffset += 1
                self.vtfContainer.GetLogger().BigBanner("EPWR DR Table")
                for i in range(0,self.tlcEpwrNumberOfCases):
                    stateShifts = []
                    for j in range(0,self.tlcEpwrStates):
                        stateShifts.append(fileBuf.GetOneByteToInt(currentFileOffset))
                        currentFileOffset += 1
                    self.tlcEpwrDrTable[i] = list(stateShifts)
                    self.vtfContainer.GetLogger().Info("", "Case %d - %s"%(i, list(stateShifts)))
                assert (currentFileOffset == nextFileOffset), "File24 Parsing may be incorrect."
            elif tagID == self.FILE24_TLC_WA_SCAN_TAG_ID: # TLC WA Scan
                currentFileOffset += 1
                self.tlcWaScanStates = fileBuf.GetOneByteToInt(currentFileOffset)
                currentFileOffset += 1
                self.tlcWaScanNumberOfCases = fileBuf.GetOneByteToInt(currentFileOffset)
                currentFileOffset += 1
                for i in range(0, self.tlcWaScanStates):
                    self.tlcWaScanAddressMap[i] = fileBuf.GetOneByteToInt(currentFileOffset)
                    currentFileOffset += 1
                for i in range(0, self.tlcWaScanStates):
                    self.tlcWaScanLevelMap[i] = fileBuf.GetOneByteToInt(currentFileOffset)
                    currentFileOffset += 1
                for i in range(0,self.tlcWaScanNumberOfCases):
                    stateShifts = []
                    for j in range(0,self.tlcWaScanStates):
                        stateShifts.append(fileBuf.GetOneByteToInt(currentFileOffset))
                        currentFileOffset += 1
                    self.tlcWaScanTable[i] = list(stateShifts)
                assert (currentFileOffset == nextFileOffset), "File24 Parsing may be incorrect."
            else:
                currentFileOffset = nextFileOffset
        return True

    def __DoWriteFile(self,fileBuf,fileSize):
        """
        Name : __DoWriteFile
        Description :
                 This function write the file data to card
        Arguments :
                testSpace   : testSpace of the card
                fileBuf     : file buffer
                fileSize    : file buffer size
        Return
               None
        """
        DiagnosticLib.WriteFileSystem(self.vtfContainer, fileID= 24,  sectorCount = fileSize, dataBuffer= fileBuf)
        return
        #end of __DoWriteFile


class ConfigurationFile39Data(object):
    """
    This class is used to read/parse/write configuration file (File 21) data
    """

    FILE_ID = 39

    __DAC_IN_MILLIVOLT = 12.5 #1 DAC = 12.5mV

    # Decode thresholds
    __FILE39_OFFSET_HB_SYNDROME_WEIGHT_THRESHOLD = 0x14C
    __FILE39_OFFSET_SB1_SYNDROME_WEIGHT_THRESHOLD = 0x14E
    __FILE39_OFFSET_SB2_SYNDROME_WEIGHT_THRESHOLD = 0x150


    # BES7 Coarse Windows for all states
    #NOTE: In actual config file, BES7C would be depicted as BES5 (For Felix, BES5 means BES7C)
    #BES Window - SLC State
    __FILE39_OFFSET_BES7C_SLC_LOW_DELTA_SHIFT_BES_WINDOW = 0x70  #Positive window
    __FILE39_OFFSET_BES7C_SLC_HIGH_DELTA_SHIFT_BES_WINDOW = 0x71 #Negative window

    #BES Window - TLC States
    __FILE39_OFFSET_BES7C_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_A = 0xB8  #Positive window
    __FILE39_OFFSET_BES7C_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_A = 0xB9 #Negative window

    __FILE39_OFFSET_BES7C_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_B = 0xBC  #Positive window
    __FILE39_OFFSET_BES7C_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_B = 0xBD #Negative window

    __FILE39_OFFSET_BES7C_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_C = 0xC0  #Positive window
    __FILE39_OFFSET_BES7C_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_C = 0xC1 #Negative window

    __FILE39_OFFSET_BES7C_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_D = 0xC4  #Positive window
    __FILE39_OFFSET_BES7C_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_D = 0xC5 #Negative window

    __FILE39_OFFSET_BES7C_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_E = 0xC8  #Positive window
    __FILE39_OFFSET_BES7C_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_E = 0xC9 #Negative window

    __FILE39_OFFSET_BES7C_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_F = 0xCC  #Positive window
    __FILE39_OFFSET_BES7C_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_F = 0xCD #Negative window

    __FILE39_OFFSET_BES7C_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_G = 0xD0  #Positive window
    __FILE39_OFFSET_BES7C_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_G = 0xD1 #Negative window


    # BES7 Fine Windows for all states
    #NOTE: In actual config file, BES7F would be depicted as BES7 (For Felix, BES7 means BES7F)
    #BES Window - SLC State
    __FILE39_OFFSET_BES7F_SLC_LOW_DELTA_SHIFT_BES_WINDOW = 0x74  #Positive window
    __FILE39_OFFSET_BES7F_SLC_HIGH_DELTA_SHIFT_BES_WINDOW = 0x75 #Negative window

    #BES Window - TLC States
    __FILE39_OFFSET_BES7F_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_A = 0xF8  #Positive window
    __FILE39_OFFSET_BES7F_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_A = 0xF9 #Negative window

    __FILE39_OFFSET_BES7F_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_B = 0xFC  #Positive window
    __FILE39_OFFSET_BES7F_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_B = 0xFD #Negative window

    __FILE39_OFFSET_BES7F_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_C = 0x100  #Positive window
    __FILE39_OFFSET_BES7F_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_C = 0x101 #Negative window

    __FILE39_OFFSET_BES7F_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_D = 0x104  #Positive window
    __FILE39_OFFSET_BES7F_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_D = 0x105 #Negative window

    __FILE39_OFFSET_BES7F_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_E = 0x108  #Positive window
    __FILE39_OFFSET_BES7F_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_E = 0x109 #Negative window

    __FILE39_OFFSET_BES7F_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_F = 0x10C  #Positive window
    __FILE39_OFFSET_BES7F_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_F = 0x10D #Negative window

    __FILE39_OFFSET_BES7F_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_G = 0x112  #Positive window
    __FILE39_OFFSET_BES7F_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_G = 0x113 #Negative window

    FILE39_SLC_EPWR_CORRECTION_THRESHOLD = 0x1BA
    FILE39_MLC_EPWR_CORRECTION_THRESHOLD = 0x1BC

    #Command Prefixes
    FILE39_SLC_STAGE1_CONFIGURATION = 0x1CE #1 Byte value --> 0th LSB: CMD-5D, 1st LSB: CMD-CF, 2nd LSB: CMD-26, 3rd LSB: CMD-B3
    FILE39_MLC_STAGE1_CONFIGURATION = 0x1CF
    FILE39_SLC_STAGE2_CONFIGURATION = 0x1D0
    FILE39_MLC_STAGE2_CONFIGURATION = 0x1D1
    FILE39_SLC_STAGE3_CONFIGURATION = 0x1D2
    FILE39_MLC_STAGE3_CONFIGURATION = 0x1D3
    FILE39_SLC_STAGE4_CONFIGURATION = 0x1D4
    FILE39_MLC_STAGE4_CONFIGURATION = 0x1D5
    FILE39_SLC_STAGE5_CONFIGURATION = 0x1D6
    FILE39_MLC_STAGE5_CONFIGURATION = 0x1D7
    FILE39_SLC_STAGE6_CONFIGURATION = 0x1D8
    FILE39_MLC_STAGE6_CONFIGURATION = 0x1D9
    FILE39_SLC_STAGE7_CONFIGURATION = 0x1DA
    FILE39_MLC_STAGE7_CONFIGURATION = 0x1DB
    FILE39_SLC_STAGE8_CONFIGURATION = 0x1DC
    FILE39_MLC_STAGE8_CONFIGURATION = 0x1DD
    FILE39_SLC_STAGE9_CONFIGURATION = 0x1DE
    FILE39_MLC_STAGE9_CONFIGURATION = 0x1DF
    FILE39_SLC_STAGE10_CONFIGURATION = 0x1E0
    FILE39_MLC_STAGE10_CONFIGURATION = 0x1E1
    FILE39_SLC_STAGE11_CONFIGURATION = 0x1E2
    FILE39_MLC_STAGE11_CONFIGURATION = 0x1E3
    FILE39_SLC_STAGE12_CONFIGURATION = 0x1E4
    FILE39_MLC_STAGE12_CONFIGURATION = 0x1E5


    def __init__(self,testSpace):
        """
        Name : __init__
        Description :
                 Constructor of the class. It calls RefessData() function for getting all the variables
        Arguments :
                testSpace : testSpace of the card

        Return
             None
        """
        self.vtfContainer = testSpace

        # Initialize all the configuration file variables
        self.SLCEPWRCorrectionThreshold = None
        self.MLCEPWRCorrectionThreshold = None
        self.HB_SYNDROME_WEIGHT_THRESHOLD = None
        self.SB1_SYNDROME_WEIGHT_THRESHOLD = None
        self.SB2_SYNDROME_WEIGHT_THRESHOLD = None
        self.BESWindowSize_BES7C_SLC = None
        self.BESWindowSize_BES7F_SLC = None
        self.BESWindowSize_BES7C_TLC = None
        self.BESWindowSize_BES7F_TLC = None
        self.SLCStage1CmdPrefix = None
        self.MLCStage1CmdPrefix = None
        self.SLCStage2CmdPrefix = None
        self.MLCStage2CmdPrefix = None
        self.SLCStage3CmdPrefix = None
        self.MLCStage3CmdPrefix = None
        self.SLCStage4CmdPrefix = None
        self.MLCStage4CmdPrefix = None
        self.SLCStage5CmdPrefix = None
        self.MLCStage5CmdPrefix = None
        self.SLCStage6CmdPrefix = None
        self.MLCStage6CmdPrefix = None
        self.SLCStage7CmdPrefix = None
        self.MLCStage7CmdPrefix = None
        self.SLCStage8CmdPrefix = None
        self.MLCStage8CmdPrefix = None
        self.SLCStage9CmdPrefix = None
        self.MLCStage9CmdPrefix = None
        self.SLCStage10CmdPrefix = None
        self.MLCStage10CmdPrefix = None
        self.SLCStage11CmdPrefix = None
        self.MLCStage11CmdPrefix = None

        #calling refresh data function for getting all configuration values
        self.RefreshData(testSpace)
    #end of __init__

    def RefreshData(self,testSpace):
        """
        Name : RefreshData
        Description :
                 This function read the latest Configuration File and update all the configuration data
        Arguments :
                testSpace : testSpace of the card
        Return
             None
        """
        #read the file data
        fileBuf,fileSize = self.__DoFileRead(testSpace)

        #Parse the Configuration data from the file buffer
        self.__ParseConfigurationData(fileBuf)
    #end of RefreshData


    def __ParseConfigurationData(self,fileBuf):
        """
        Name : __ParseConfigurationData
        Description :
                 This function parse the data from file buffer
        Arguments :
                fileBuf   : configuration file buffer
        Return
             None
        #Parsing the data
        self.commonBEFlashwareFlags          = fileBuf.GetTwoBytesToInt(self.FILE_21_COMMON_BACKEND_FLASHWARE_FLAGS_OFFSET)
        self.plccThreshold                   = fileBuf.GetOneByteToInt(self.FILE_21_PLCC_THRESHOLD_OFFSET)
        """
        self.SLCEPWRCorrectionThreshold = fileBuf.GetTwoBytesToInt(self.FILE39_SLC_EPWR_CORRECTION_THRESHOLD)
        self.MLCEPWRCorrectionThreshold = fileBuf.GetTwoBytesToInt(self.FILE39_MLC_EPWR_CORRECTION_THRESHOLD)
        # RR path prefix commands
        self.HB_SYNDROME_WEIGHT_THRESHOLD = fileBuf.GetTwoBytesToInt(self.__FILE39_OFFSET_HB_SYNDROME_WEIGHT_THRESHOLD)
        self.SB1_SYNDROME_WEIGHT_THRESHOLD = fileBuf.GetTwoBytesToInt(self.__FILE39_OFFSET_SB1_SYNDROME_WEIGHT_THRESHOLD)
        self.SB2_SYNDROME_WEIGHT_THRESHOLD = fileBuf.GetTwoBytesToInt(self.__FILE39_OFFSET_SB2_SYNDROME_WEIGHT_THRESHOLD)


        #Get SLC BES Windows for BES7C and BES7F
        BESWindowSize_BES7C_SLC_LowDeltaShift = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7C_SLC_LOW_DELTA_SHIFT_BES_WINDOW)
        BESWindowSize_BES7C_SLC_HighDeltaShift = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7C_SLC_LOW_DELTA_SHIFT_BES_WINDOW)
        BESWindowSize_BES7F_SLC_HighDeltaShift = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7F_SLC_HIGH_DELTA_SHIFT_BES_WINDOW)
        BESWindowSize_BES7F_SLC_LowDeltaShift = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7F_SLC_LOW_DELTA_SHIFT_BES_WINDOW)

        if (BESWindowSize_BES7C_SLC_HighDeltaShift != BESWindowSize_BES7C_SLC_LowDeltaShift) or (BESWindowSize_BES7F_SLC_HighDeltaShift != BESWindowSize_BES7F_SLC_LowDeltaShift):
            raise TestError.TestFailError(self.vtfContainer.GetTestName(), "SLC BES Window Size is different on opposite ends")
        else:
            self.BESWindowSize_BES7C_SLC = BESWindowSize_BES7C_SLC_HighDeltaShift * self.__DAC_IN_MILLIVOLT
            self.BESWindowSize_BES7F_SLC = BESWindowSize_BES7F_SLC_HighDeltaShift * self.__DAC_IN_MILLIVOLT


        #Get TLC BES Windows for BES7C and BES7F
        BESWindowSize_BES7C_TLC_LowDeltaShift_StateA = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7C_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_A)
        BESWindowSize_BES7C_TLC_LowDeltaShift_StateB = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7C_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_B)
        BESWindowSize_BES7C_TLC_LowDeltaShift_StateC = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7C_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_C)
        BESWindowSize_BES7C_TLC_LowDeltaShift_StateD = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7C_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_D)
        BESWindowSize_BES7C_TLC_LowDeltaShift_StateE = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7C_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_E)
        BESWindowSize_BES7C_TLC_LowDeltaShift_StateF = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7C_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_F)
        BESWindowSize_BES7C_TLC_LowDeltaShift_StateG = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7C_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_G)

        BESWindowSize_BES7C_TLC_HighDeltaShift_StateA = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7C_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_A)
        BESWindowSize_BES7C_TLC_HighDeltaShift_StateB = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7C_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_B)
        BESWindowSize_BES7C_TLC_HighDeltaShift_StateC = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7C_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_C)
        BESWindowSize_BES7C_TLC_HighDeltaShift_StateD = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7C_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_D)
        BESWindowSize_BES7C_TLC_HighDeltaShift_StateE = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7C_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_E)
        BESWindowSize_BES7C_TLC_HighDeltaShift_StateF = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7C_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_F)
        BESWindowSize_BES7C_TLC_HighDeltaShift_StateG = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7C_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_G)

        if not (BESWindowSize_BES7C_TLC_LowDeltaShift_StateA == BESWindowSize_BES7C_TLC_HighDeltaShift_StateA and \
                BESWindowSize_BES7C_TLC_LowDeltaShift_StateB == BESWindowSize_BES7C_TLC_HighDeltaShift_StateB and \
                BESWindowSize_BES7C_TLC_LowDeltaShift_StateC == BESWindowSize_BES7C_TLC_HighDeltaShift_StateC and \
                BESWindowSize_BES7C_TLC_LowDeltaShift_StateD == BESWindowSize_BES7C_TLC_HighDeltaShift_StateD and \
                BESWindowSize_BES7C_TLC_LowDeltaShift_StateE == BESWindowSize_BES7C_TLC_HighDeltaShift_StateE and \
                BESWindowSize_BES7C_TLC_LowDeltaShift_StateF == BESWindowSize_BES7C_TLC_HighDeltaShift_StateF and \
                BESWindowSize_BES7C_TLC_LowDeltaShift_StateG == BESWindowSize_BES7C_TLC_HighDeltaShift_StateG):
            raise TestError.TestFailError(self.vtfContainer.GetTestName(), "SLC BES Window Size is different on opposite ends")
        else:
            self.BESWindowSize_BES7C_TLC = BESWindowSize_BES7C_TLC_LowDeltaShift_StateA * self.__DAC_IN_MILLIVOLT


        #Get TLC BES Windows for BES7C and BES7F
        BESWindowSize_BES7F_TLC_LowDeltaShift_StateA = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7F_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_A)
        BESWindowSize_BES7F_TLC_LowDeltaShift_StateB = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7F_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_B)
        BESWindowSize_BES7F_TLC_LowDeltaShift_StateC = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7F_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_C)
        BESWindowSize_BES7F_TLC_LowDeltaShift_StateD = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7F_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_D)
        BESWindowSize_BES7F_TLC_LowDeltaShift_StateE = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7F_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_E)
        BESWindowSize_BES7F_TLC_LowDeltaShift_StateF = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7F_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_F)
        BESWindowSize_BES7F_TLC_LowDeltaShift_StateG = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7F_TLC_LOW_DELTA_SHIFT_BES_WINDOW_STATE_G)

        BESWindowSize_BES7F_TLC_HighDeltaShift_StateA = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7F_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_A)
        BESWindowSize_BES7F_TLC_HighDeltaShift_StateB = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7F_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_B)
        BESWindowSize_BES7F_TLC_HighDeltaShift_StateC = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7F_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_C)
        BESWindowSize_BES7F_TLC_HighDeltaShift_StateD = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7F_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_D)
        BESWindowSize_BES7F_TLC_HighDeltaShift_StateE = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7F_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_E)
        BESWindowSize_BES7F_TLC_HighDeltaShift_StateF = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7F_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_F)
        BESWindowSize_BES7F_TLC_HighDeltaShift_StateG = fileBuf.GetOneByteToInt(self.__FILE39_OFFSET_BES7F_TLC_HIGH_DELTA_SHIFT_BES_WINDOW_STATE_G)

        if not (BESWindowSize_BES7F_TLC_LowDeltaShift_StateA == BESWindowSize_BES7F_TLC_HighDeltaShift_StateA and \
                BESWindowSize_BES7F_TLC_LowDeltaShift_StateB == BESWindowSize_BES7F_TLC_HighDeltaShift_StateB and \
                BESWindowSize_BES7F_TLC_LowDeltaShift_StateC == BESWindowSize_BES7F_TLC_HighDeltaShift_StateC and \
                BESWindowSize_BES7F_TLC_LowDeltaShift_StateD == BESWindowSize_BES7F_TLC_HighDeltaShift_StateD and \
                BESWindowSize_BES7F_TLC_LowDeltaShift_StateE == BESWindowSize_BES7F_TLC_HighDeltaShift_StateE and \
                BESWindowSize_BES7F_TLC_LowDeltaShift_StateF == BESWindowSize_BES7F_TLC_HighDeltaShift_StateF and \
                BESWindowSize_BES7F_TLC_LowDeltaShift_StateG == BESWindowSize_BES7F_TLC_HighDeltaShift_StateG):
            raise TestError.TestFailError(self.vtfContainer.GetTestName(), "TLC BES Window Size is different on opposite ends")
        else:
            self.BESWindowSize_BES7F_TLC = BESWindowSize_BES7F_TLC_LowDeltaShift_StateA * self.__DAC_IN_MILLIVOLT

        self.SLCStage1CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_SLC_STAGE1_CONFIGURATION)
        self.MLCStage1CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_MLC_STAGE1_CONFIGURATION)
        self.SLCStage2CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_SLC_STAGE2_CONFIGURATION)
        self.MLCStage2CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_MLC_STAGE2_CONFIGURATION)
        self.SLCStage3CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_SLC_STAGE3_CONFIGURATION)
        self.MLCStage3CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_MLC_STAGE3_CONFIGURATION)
        self.SLCStage4CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_SLC_STAGE4_CONFIGURATION)
        self.MLCStage4CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_MLC_STAGE4_CONFIGURATION)
        self.SLCStage5CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_SLC_STAGE5_CONFIGURATION)
        self.MLCStage5CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_MLC_STAGE5_CONFIGURATION)
        self.SLCStage6CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_SLC_STAGE6_CONFIGURATION)
        self.MLCStage6CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_MLC_STAGE6_CONFIGURATION)
        self.SLCStage7CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_SLC_STAGE7_CONFIGURATION)
        self.MLCStage7CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_MLC_STAGE7_CONFIGURATION)
        self.SLCStage8CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_SLC_STAGE8_CONFIGURATION)
        self.MLCStage8CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_MLC_STAGE8_CONFIGURATION)
        self.SLCStage9CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_SLC_STAGE9_CONFIGURATION)
        self.MLCStage9CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_MLC_STAGE9_CONFIGURATION)
        self.SLCStage10CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_SLC_STAGE10_CONFIGURATION)
        self.MLCStage10CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_MLC_STAGE10_CONFIGURATION)
        self.SLCStage11CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_SLC_STAGE11_CONFIGURATION)
        self.MLCStage11CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_MLC_STAGE11_CONFIGURATION)
        self.SLCStage12CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_SLC_STAGE12_CONFIGURATION)
        self.MLCStage12CmdPrefix = fileBuf.GetOneByteToInt(self.FILE39_MLC_STAGE12_CONFIGURATION)
        #end of __ParseConfigurationData

    def SetBytes(self,testSpace):
        """
        Name : SetBytes
        Description :
                 It is used to set/clear bits
        Return
             None
        """
        #read the file data
        fileBuf,fileSize = self.__DoFileRead(testSpace)

        #Parse the file data
        self.__ParseConfigurationData(fileBuf)

        #set this byte in
        fileBuf.SetTwoBytes(self.FILE_21_COMMON_BACKEND_FLASHWARE_FLAGS_OFFSET,finalWLControlFlag)

        #do write file
        self.__DoWriteFile(testSpace,fileBuf,fileSize)

        #Doing a Power Cycle
        import Validation.Utils as Utils
        Utils.PowerCycle(testSpace)
        #end of SetWLFlag

    def __DoFileRead(self,testSpace):
        """
        Name : __DoFileRead
        Description :
                 This function read the lates Configuration File and return the buffer data
        Arguments :
                testSpace : testSpace of the card
        Return
               fileBuf     : file buffer
               fileSize    : file buffer size
        """
        fileBuf = DiagnosticLib.ReadFileSystem(testSpace, fileID=self.FILE_ID)
        fileSizeSectors, fileSizeBytes = DiagnosticLib.LengthOfFileInBytes(fileId=self.FILE_ID)
        return fileBuf, fileSizeSectors

    def __DoWriteFile(self,testSpace,fileBuf,fileSize):
        """
        Name : __DoWriteFile
        Description :
                 This function write the file data to card
        Arguments :
                testSpace   : testSpace of the card
                fileBuf     : file buffer
                fileSize    : file buffer size
        Return
               None
        """
        DiagnosticLib.WriteFileSystem(testSpace, fileID= self.FILE_ID,  sectorCount = fileSize, dataBuffer= fileBuf)
        return
    #end of __DoWriteFile

#end of class
class ConfigurationFile160Data(object):
    """
    This class is used to read/parse/write configuration file (File 160) data (Host Read Scrub configurations)
    """
    FILE_ID = 160
    SYND_WGT_PRS_BESC_OFFSET = 0x8
    SYND_WGT_PRS_BESF_OFFSET = 0xA
    SYND_WGT_PRS_PRIORITY_OFFSET = 0xC
    SYND_WGT_ARS_BESC_BESF_OFFSET = 0xE
    SYND_WGT_ARS_PRIORITY_OFFSET = 0x10
    ARS_PAGES_TO_SCAN_OFFSET = 0x12
    ARS_ECCPAGE_TO_SCAN_STRING0_OFFSET = 0x13 #First 4bits (LSB)
    ARS_ECCPAGE_TO_SCAN_STRING1_OFFSET = 0x13 #Last 4bits (MSB)
    ARS_ECCPAGE_TO_SCAN_STRING2_OFFSET = 0x14 #4 LSBs
    ARS_ECCPAGE_TO_SCAN_STRING3_OFFSET = 0x14 #4 MSBs       
    ARS_ECCPAGE_TO_SCAN_STRING4_OFFSET = 0x15 #4 LSBs
    ARS_TRIGGER_THRESHOLD_READ_COUNTER_OFFSET = 0x18
    ARS_PC_READ_COUNTER_INCREMENT_OFFSET = 0x1A
    DEFAULT_MIP_FLUSH_MULTIPLIER_OFFSET = 0x1B #Multiply by 128 to get the threshold no of cmds (w,r,e) at which MIP flush is done
    ARS_BLOCK_SCAN_QUOTA_PER_HOST_READ_CMD_IN_MILLISECS_OFFSET = 0x1C
    READ_SCRUB_CONFIG_PARAMS_OFFSET = 0x1D

    RS_NUM_STEPS_WRITE_PATH_NON_MLCGC = 0x1F
    RS_NUM_STEPS_WRITE_PATH_MLCGC = 0x20
    RS_EXTRA_RSGC_STEPS_AT_READ = 0x52
    RS_TIME_TO_SCHEDULE_EXTRA_RSGC = 0X51
    #ARS_PAGES_TO_SCAN_OFFSET = 0x53
    ARS_BLOCK_SCAN_QUOTA_PER_HOST_WRITE_CMD_IN_MILLISECS_OFFSET = 0x21
    RS_QUEUE_DEPTH_OFFSET = 0x23
    RS_QUEUE_DEPTH_GEAR2_GC_THRESHOLD_OFFSET = 0x24
    RS_QUEUE_DEPTH_URGENT_GC_THRESHOLD_OFFSET = 0x25
    ARS_NUM_WORDLINES_TO_SCAN_OFFSET = 0x26 #Max 16 WLs
    ARS_WORDLINE_ZONE_START_OFFSET = 0x27 #2bytes each
    FS_READSCRUB_SW_THRESHOLD = 0x4F #2 bytes each
    def __init__(self, vtfContainer):
        self.vtfContainer = vtfContainer
        self.logger = vtfContainer.GetLogger()
        self.PRSSyndWgtBESC = None
        self.PRSSyndWgtBESF = None
        self.PRSSyndWgtPriority = None
        self.ARSSyndWgtBESC = self.ARSSyndWgtBESF = None
        self.ARSSyndWgtPriority = None
        self.ARSWLLogicalPageMapping = {}
        self.ARSStringEccPageMapping = None
        self.ARSTriggerThresholdReadCounter = None
        self.ARSPCReadCounterIncrementValue = None
        self.DefaultMIPFlushThreshold = None
        self.ARSScanMaxQuotaDuringRead = None
        self.ARSScanMaxQuotaDuringWrite = None

        #RS Enable/Disable configuration
        self.isRSEnabledOnHostWrites = None
        self.isRSEnabledOnHostReads = None
        self.isRSEnabledOnWriteReadPostInit = None
        self.isRSEnabledOnHostMLCBlocks = None
        self.isRSEnabledOnFSBlocks = None
        self.isFullEBlockScanEnabled = None
        self.isPRSEnabledOnHostReads = None
        self.isARSScanOnEntireCardEnabled = None

        self.NumStepsRSGCWritePath_Gear2Mode = None
        self.NumStepsRSGCWritePath_NormalMode = None

        self.RSQueueLength = None
        self.RSQueueLengthForGear2Trigger = None
        self.RSQueueLengthForUrgentTrigger = None

        self.ARSNumberOfWordlinesToScan = None
        self.FSRSSWThreshold = None
        self.ARSWordlineList = []
        self.RefreshData(vtfContainer)

    def RefreshData(self,testSpace):
        fileBuf,fileSize = self.__DoFileRead(testSpace)
        self.__ParseConfigurationData(fileBuf)

    def __DoFileRead(self,testSpace):
        fileBuf = DiagnosticLib.ReadFileSystem(testSpace, fileID=self.FILE_ID)
        fileSizeSectors, fileSizeBytes = DiagnosticLib.LengthOfFileInBytes(fileId=self.FILE_ID)
        return fileBuf, fileSizeSectors

    def __ParseConfigurationData(self,fileBuf):
        #Syndrome weight thresholds for PRS and ARS
        self.PRSSyndWgtBESC = fileBuf.GetTwoBytesToInt(self.SYND_WGT_PRS_BESC_OFFSET)
        self.PRSSyndWgtBESF = fileBuf.GetTwoBytesToInt(self.SYND_WGT_PRS_BESF_OFFSET)
        self.PRSSyndWgtPriority = fileBuf.GetTwoBytesToInt(self.SYND_WGT_PRS_PRIORITY_OFFSET)
        self.ARSSyndWgtBESC = self.ARSSyndWgtBESF = fileBuf.GetTwoBytesToInt(self.SYND_WGT_ARS_BESC_BESF_OFFSET)
        self.ARSSyndWgtPriority = fileBuf.GetTwoBytesToInt(self.SYND_WGT_ARS_PRIORITY_OFFSET)

        #1byte for 2 strings
        string0ECCPage = fileBuf.GetOneByteToInt(self.ARS_ECCPAGE_TO_SCAN_STRING0_OFFSET) & 15  #4 LSBs
        string1ECCPage = (fileBuf.GetOneByteToInt(self.ARS_ECCPAGE_TO_SCAN_STRING1_OFFSET) & 240) >> 4#4 MSBs
        string2ECCPage = fileBuf.GetOneByteToInt(self.ARS_ECCPAGE_TO_SCAN_STRING2_OFFSET) & 15  #4 LSBs
        string3ECCPage = (fileBuf.GetOneByteToInt(self.ARS_ECCPAGE_TO_SCAN_STRING3_OFFSET) & 240) >> 4 #4 MSBs      
        string4ECCPage = fileBuf.GetOneByteToInt(self.ARS_ECCPAGE_TO_SCAN_STRING4_OFFSET) & 15  #4 LSBs
        self.ARSStringEccPageMapping = {0:string0ECCPage, 1:string1ECCPage, 2:string2ECCPage, 3:string3ECCPage, 4:string4ECCPage}

        #Command counter thresholds
        self.ARSTriggerThresholdReadCounter = fileBuf.GetTwoBytesToInt(self.ARS_TRIGGER_THRESHOLD_READ_COUNTER_OFFSET)
        self.ARSPCReadCounterIncrementValue = fileBuf.GetOneByteToInt(self.ARS_PC_READ_COUNTER_INCREMENT_OFFSET)
        self.DefaultMIPFlushThreshold = fileBuf.GetOneByteToInt(self.DEFAULT_MIP_FLUSH_MULTIPLIER_OFFSET) * 128 #This is per 128 host cmd MML chunks (write, read and erase)

        #Block scan quota
        self.ARSScanMaxQuotaDuringRead = fileBuf.GetOneByteToInt(self.ARS_BLOCK_SCAN_QUOTA_PER_HOST_READ_CMD_IN_MILLISECS_OFFSET) #in millisec
        self.ARSScanMaxQuotaDuringWrite = fileBuf.GetOneByteToInt(self.ARS_BLOCK_SCAN_QUOTA_PER_HOST_WRITE_CMD_IN_MILLISECS_OFFSET) #in millisec

        #RS Enable/Disable configuration
        ReadScrubConfig = fileBuf.GetOneByteToInt(self.READ_SCRUB_CONFIG_PARAMS_OFFSET) #in millisec   
        self.isRSEnabledOnHostWrites = ReadScrubConfig & 1
        ReadScrubConfig >>= 1
        self.isFullEBlockScanEnabled = ReadScrubConfig & 1
        ReadScrubConfig >>= 1
        self.isRSEnabledOnHostReads = ReadScrubConfig & 1
        ReadScrubConfig >>= 1
        self.isRSEnabledOnWriteReadPostInit = ReadScrubConfig & 1
        ReadScrubConfig >>= 1
        self.isRSEnabledOnHostMLCBlocks = ReadScrubConfig & 1
        ReadScrubConfig >>= 1
        self.isRSEnabledOnFSBlocks = ReadScrubConfig & 1
        ReadScrubConfig >>= 1
        self.isPRSEnabledOnHostReads = ReadScrubConfig & 1
        ReadScrubConfig >>= 1
        self.isARSScanOnEntireCardEnabled = ReadScrubConfig & 1

        #Num of steps of RS GC or WL GC to do during Non-GC or GC operations
        self.NumStepsRSGCWritePathNonMLCGC = fileBuf.GetOneByteToInt(self.RS_NUM_STEPS_WRITE_PATH_NON_MLCGC)
        self.NumStepsRSGCWritePathMLCGC = fileBuf.GetOneByteToInt(self.RS_NUM_STEPS_WRITE_PATH_MLCGC)

        #ExtraRSGC schdule related
        self.TimeToScheduleExtraRSGC = fileBuf.GetOneByteToInt(self.RS_TIME_TO_SCHEDULE_EXTRA_RSGC)
        self.ExtraRSGCStepsAtRead = fileBuf.GetOneByteToInt(self.RS_EXTRA_RSGC_STEPS_AT_READ)

        #Read Scrub Queue related params
        self.RSQueueLength = fileBuf.GetOneByteToInt(self.RS_QUEUE_DEPTH_OFFSET)
        self.RSQueueLengthForGear2Trigger = fileBuf.GetOneByteToInt(self.RS_QUEUE_DEPTH_GEAR2_GC_THRESHOLD_OFFSET)
        self.RSQueueLengthForUrgentTrigger = fileBuf.GetOneByteToInt(self.RS_QUEUE_DEPTH_URGENT_GC_THRESHOLD_OFFSET)

        #ARS Wordline related params
        self.ARSNumberOfWordlinesToScan = fileBuf.GetOneByteToInt(self.ARS_NUM_WORDLINES_TO_SCAN_OFFSET)
        t_ARSWordLineZoneStartOffset = self.ARS_WORDLINE_ZONE_START_OFFSET
        for WL in range(self.ARSNumberOfWordlinesToScan):
            self.ARSWordlineList.append(fileBuf.GetTwoBytesToInt(t_ARSWordLineZoneStartOffset))
            t_ARSWordLineZoneStartOffset += 2
        self.FSRSSWThreshold = fileBuf.GetTwoBytesToInt(self.FS_READSCRUB_SW_THRESHOLD)
        #1bit to denote the page to scan (LSB->MSB :: LP, MP, UP, TP)
        MLC_Pages = ["LP", "MP", "UP", "TP"]
        for WordlineNo in range(self.ARSNumberOfWordlinesToScan):
            ARSPagesToScan = fileBuf.GetOneByteToInt(self.ARS_PAGES_TO_SCAN_OFFSET)
            self.ARSWLLogicalPageMapping[self.ARSWordlineList[WordlineNo]] = []
            for page in MLC_Pages:
                if ARSPagesToScan & 1 == 1:
                    self.ARSWLLogicalPageMapping[self.ARSWordlineList[WordlineNo]].append(page)
                ARSPagesToScan >>= 1        
        self.__PrintFile160Data()


    def __PrintFile160Data(self):
        self.logger.BigBanner("File160 Data")
        self.logger.SmallBanner("ARS/PRS THRESHOLDS")
        self.logger.Info("", "PRSSyndWgtBESC = 0x%X"%self.PRSSyndWgtBESC)
        self.logger.Info("", "PRSSyndWgtBESF = 0x%X"%self.PRSSyndWgtBESF)
        self.logger.Info("", "PRSSyndWgtPriority = 0x%X"%self.PRSSyndWgtPriority)
        self.logger.Info("", "ARSSyndWgtBESC = 0x%X"%self.ARSSyndWgtBESC)
        self.logger.Info("", "ARSSyndWgtBESF = 0x%X"%self.ARSSyndWgtBESF)
        self.logger.Info("", "ARSSyndWgtPriority = 0x%X"%self.ARSSyndWgtPriority)
        self.logger.SmallBanner("ARS WORDLINES AND ECC PAGE TO STRING MAPPING")
        self.logger.Info("", "ARSNumberOfWordlinesToScan = 0x%X"%self.ARSNumberOfWordlinesToScan)
        self.logger.Info("", "ARSWordlineList = %s"%('[{}]'.format(', '.join(hex(x) for x in self.ARSWordlineList))))

        for string in list(self.ARSStringEccPageMapping.keys()):
            self.logger.Info("", "ARSStringEccPageMapping[string %d] = %d"%(string, self.ARSStringEccPageMapping[string]))

        wordlineindex =0       
        for wordline in list(self.ARSWLLogicalPageMapping.keys()):
            self.logger.Info("", "ARSWLLogicalPageMapping[wordline 0x%x] = %s"%(self.ARSWordlineList[wordlineindex], self.ARSWLLogicalPageMapping[wordline]))
            wordlineindex += 1

        self.logger.SmallBanner("ARS READ COUNTER VALUES")
        self.logger.Info("", "ARSTriggerThresholdReadCounter = 0x%X"%self.ARSTriggerThresholdReadCounter)

        self.logger.SmallBanner("OTHER VALUES")
        self.logger.Info("", "ARSPCReadCounterIncrementValue = 0x%X"%self.ARSPCReadCounterIncrementValue)
        self.logger.Info("", "DefaultMIPFlushThreshold = 0x%X"%self.DefaultMIPFlushThreshold)
        self.logger.Info("", "ARSScanMaxQuotaDuringWrite = %dms"%self.ARSScanMaxQuotaDuringWrite)
        self.logger.Info("", "ARSScanMaxQuotaDuringRead = %dms"%self.ARSScanMaxQuotaDuringRead)

        self.logger.SmallBanner("RS GC VALUES")
        self.logger.Info("", "NumStepsRSGCWritePathNonMLCGC = 0x%X"%self.NumStepsRSGCWritePathNonMLCGC)
        self.logger.Info("", "NumStepsRSGCWritePathMLCGC = 0x%X"%self.NumStepsRSGCWritePathMLCGC)
        self.logger.Info("", "RSQueueLength = 0x%X"%self.RSQueueLength)
        self.logger.Info("", "RSQueueLengthForGear2Trigger = 0x%X"%self.RSQueueLengthForGear2Trigger)
        self.logger.Info("", "RSQueueLengthForUrgentTrigger = 0x%X"%self.RSQueueLengthForUrgentTrigger)
        self.logger.Info("", "TimeToScheduleExtraRSGCDuringRead = 0x%X"%self.TimeToScheduleExtraRSGC)
        self.logger.Info("", "ExtraRSGCStepsAtRead = 0x%X"%self.ExtraRSGCStepsAtRead)



        self.logger.SmallBanner("-")


class ConfigurationFile199Data(object):
    """
    This class is used to read/parse/write configuration file (File 21) data
    """

    FILE_ID = 199

    #offsets
    FILE_199_FIRST_FOUR = 0x0

    def __init__(self,vtfContainer):
        """
        Name : __init__
        Description :
                 Constructor of the class. It calls RefessData() function for getting all the variables
        Arguments :
                vtfContainer : vtfContainer of the card

        Return
             None
        """
        self.vtfContainer = vtfContainer
        self.KeyFirstFour = None
        self.RefreshData(self.vtfContainer)

    def RefreshData(self,vtfContainer):
        """
        Name : RefreshData
        Description :
                 This function read the latest Configuration File and update all the configuration data
        Arguments :
                vtfContainer : vtfContainer of the card
        Return
             None
        """
        #read the file data
        fileBuf,fileSize = self.__DoFileRead(vtfContainer)

        #Parse the Configuration data from the file buffer
        self.__ParseConfigurationData(fileBuf)
    #end of RefreshData

    def __ParseConfigurationData(self,fileBuf):
        """
        Name : __ParseConfigurationData
        Description :
                 This function parse the data from file buffer
        Arguments :
                fileBuf   : configuration file buffer
        Return
             None
        """
        # Pf Configurability
        self.KeyFirstFour = fileBuf.GetTwoBytesToInt(self.FILE_199_FIRST_FOUR)

    def __DoFileRead(self,vtfContainer):
        """
        Name : __DoFileRead
        Description :
                 This function read the lates Configuration File and return the buffer data
        Arguments :
                vtfContainer : vtfContainer of the card
        Return
               fileBuf     : file buffer
               fileSize    : file buffer size
        """
        fileSize, fileSizeBytes = DiagnosticLib.LengthOfFileInBytes(fileId=self.FILE_ID)
        fileBuf = DiagnosticLib.ReadFileSystem(vtfContainer, fileID=self.FILE_ID, sectorCount=fileSize)

        return fileBuf,fileSize

    #end of __DoFileRead

    def __DoWriteFile(self,fileBuf,fileSize):
        """
        Name : __DoWriteFile
        Description :
                 This function write the file data to card
        Arguments :
                fileBuf     : file buffer
                fileSize    : file buffer size
        Return
               None
        """

        DiagnosticLib.WriteFileSystem(self.vtfContainer, fileID= self.FILE_ID,  sectorCount = fileSize, dataBuffer= fileBuf)

        return

#end of class

