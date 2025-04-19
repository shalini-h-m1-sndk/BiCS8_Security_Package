"""
class DiagnosticLib
Contains the definition of all diag cmds
@ Author: Shaheed Nehal - ported to CVF
@ copyright (C) 2021 Western Digital Corporation
"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from builtins import next
from builtins import str
from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    from builtins import zip
    pass # from builtins import str
    from builtins import hex
    from builtins import range
    pass # from builtins import *
from past.utils import old_div
import Extensions.CVFImports as pyWrap
import Core.ValidationError as TestError
#import Constants
#import AddressTypes
#import ByteUtil
#import FileData
import os
import SDCommandWrapper as SDWrap

#OPCODES
DIAG_GET_HOT_COUNT_OPCODE = 0x61
DIAG_SET_HOT_COUNT_OPCODE = 0x62
DIAG_READ_BE_ERROR_LOG = 0x64
DIAG_GET_BE_BUILD_FEATURES = 0xD1

READ_DATA = 0
WRITE_DATA = 1
NO_DATA = 2
SINGLE_SECTOR = 0x01
TWO_SECTORS = 2
FOUR_SECTORS = 4
EIGHT_SECTORS = 8 # Added to handle >8MMPs

DIAG_SECTORLENGTH=1
GET_MML_DATA = 0xC9
SET_MML_DATA = 0xCA

#constants
MASK_UPPER_BYTE = 0x00FF
MASK_LOW_WORD = 0x0000FFFF
MASK_LOW_BYTE = 0x00FF
SINGLE_SECTOR = 1
BE_SPECIFIC_BYTES_PER_SECTOR = 512

# Opcodes for SFS diag  0x86
GET_SFS_ENABLED_SUBOPCODE = 1          # Returns 1 byte
GET_FS_METABLOCKS_SUBOPCODE = 2        # Returns 2 X 4-byte Primary MB Addresses, 2 X 4-byte Secondary MB Addresses
GET_SFS_FS_METABLOCKS_SUBOPCODE = 0    # Returns 2 X 4-byte Primary MB Addresses, 2 X 4-byte Secondary MB Addresses, 1 byte SFS enabled/disabled
GET_RS_QUEUE_SUBOPCODE=  0x2
RSS_QUEUESIZE        =   8

#Added code to avoid sending Diag for so many times
g_IsLargeMBUsed    = -1
g_NumOfBlocksPerMB = -1
SCTP_RSA_Signature = [
    0x1D ,0x96 ,0x44 ,0x9D ,0x0F ,0xB3 ,0x5A ,0x91 ,0x8C ,0xC5 ,0xF9 ,0xFA ,0x14 ,0x69 ,0xF6 ,0x33 ,
    0xEB ,0x78 ,0xE2 ,0xEA ,0x6D ,0x3C ,0xF8 ,0x78 ,0x27 ,0xFE ,0xA7 ,0xCB ,0xF3 ,0x1E ,0xA6 ,0xD6 ,
    0x97 ,0xD5 ,0xE3 ,0xC6 ,0xAA ,0x42 ,0xDB ,0x3A ,0x52 ,0x26 ,0xA0 ,0x51 ,0x28 ,0x99 ,0x60 ,0x57 ,
    0x30 ,0x86 ,0xED ,0xEB ,0x66 ,0x67 ,0x4B ,0x6E ,0x0C ,0x4B ,0xBB ,0x03 ,0xDD ,0xDA ,0x8A ,0x7C ,
    0x32 ,0xD8 ,0xE3 ,0x51 ,0x70 ,0x69 ,0x2D ,0x0D ,0x6D ,0xDF ,0xEA ,0xD3 ,0x8B ,0x41 ,0x7A ,0x55 ,
    0xD8 ,0xD4 ,0x09 ,0x23 ,0x74 ,0xC5 ,0x5F ,0x31 ,0x4A ,0x23 ,0xED ,0x2B ,0x2A ,0xF4 ,0xCD ,0x15 ,
    0xF4 ,0x40 ,0xA0 ,0xDB ,0x92 ,0xC0 ,0xF4 ,0xD5 ,0x0A ,0x5C ,0x4B ,0x78 ,0xE4 ,0xE3 ,0xF7 ,0x96 ,
    0xE3 ,0xC7 ,0x01 ,0x04 ,0x8C ,0x8F ,0xA0 ,0x82 ,0x43 ,0x35 ,0xE5 ,0xC6 ,0xB0 ,0xE3 ,0xCC ,0x35 ,
    0x7E ,0x63 ,0x90 ,0xFE ,0x1E ,0x9C ,0xF1 ,0x18 ,0x8B ,0x78 ,0x79 ,0x81 ,0x83 ,0x3A ,0x59 ,0x57 ,
    0x6F ,0x83 ,0x83 ,0xBF ,0xDF ,0xA5 ,0x7F ,0x50 ,0x3E ,0x58 ,0xD9 ,0x17 ,0x45 ,0x08 ,0x19 ,0x24 ,
    0x69 ,0xDB ,0x4F ,0x5E ,0x6C ,0x41 ,0x62 ,0x95 ,0x93 ,0xB7 ,0x2F ,0xE2 ,0xA8 ,0x28 ,0x85 ,0x0A ,
    0x5B ,0xA5 ,0x7D ,0x0B ,0xBA ,0xD7 ,0x82 ,0x77 ,0xC5 ,0xDC ,0xDD ,0x13 ,0x96 ,0xEF ,0x6E ,0x43 ,
    0x8B ,0xC7 ,0xA8 ,0x97 ,0xFF ,0x36 ,0x46 ,0x65 ,0x53 ,0x5E ,0x4D ,0x90 ,0xC5 ,0xC7 ,0xCF ,0xDC ,
    0x70 ,0xC0 ,0xC6 ,0x85 ,0xE5 ,0xF8 ,0x2C ,0x9F ,0x12 ,0x7D ,0xB6 ,0x95 ,0x90 ,0xAE ,0x53 ,0x5B ,
    0x39 ,0x8A ,0x96 ,0xDB ,0x8F ,0x54 ,0x13 ,0xB9 ,0x32 ,0x68 ,0x71 ,0x8E ,0x2E ,0xE7 ,0xDB ,0x4B ,
    0xB2 ,0x4C ,0x95 ,0x8A ,0x36 ,0x4F ,0xF1 ,0xF1 ,0x47 ,0xEF ,0x3C ,0x2A ,0xFF ,0x16 ,0xE0 ,0xE8 , 
] 

# GAT Cache Info diagnostic offsets
#
#  typedef struct _GAT_Diagnostic_Info_t {
#      PhysicalAddressInfo_t           PBA_GAT;   Size : 1 * 6 = 6 bytes
#      GAT_Delta_Entry_Merged_t        gatDelta[384];  Size : 384 * 16 = 6144 bytes
#      GAT_Directory_Delta_Entry_t     gatDirectoryDelta[48]; Size : 48 * 8 = 384 bytes
#      IGAT_Delta_Entry_t              igatDelta[64];  Size : 64 * 8 = 512 bytes
#      RGAT_Delta_Entry_Merged_t       rgatDelta[88]; Size : 88  * 16 = 1408 bytes
#      RGAT_Dir_Delta_Entry_t          rgatDirDelta[64];  Size : 64 * 8 = 512 bytes
#      uint16                          GATMetaBlockNumber[MAX_NUMBER_OF_GAT_BLOCKS];   Size : 2 * 480 = 960 bytes    # Modified based on RPG-30943
#      uint16                          MlcFBLCounter;
#      uint16                          BinaryFBLCounter;
#      uint16                          BinaryFBLMetablockNumber;
#      uint8                           MLCWearLevelingCounter;
#      uint16                          activeBlockWriteOffset;
#      uint16                          gatDeltaSize;
#      uint16                          igatDeltaSize;
#      uint16                          gatDirDeltaSize;
#   #ifdef PROD_BICS3_CC
#      uint16                          rgatDeltaSize;
#      uint16                          rgatDirDeltaSize;
#   #endif
#  } GAT_Diagnostic_Info_t;


PHYSICAL_ADDRESS = 0
GAT_DELTA_ENTRY_MERGED =  PHYSICAL_ADDRESS + 6 + 2 # 2 BYTE PADDING
GAT_DIRECTORY_DELTA_ENTRY = GAT_DELTA_ENTRY_MERGED + 6144
IGAT_DELTA_ENTRY = GAT_DIRECTORY_DELTA_ENTRY  + 512
RGAT_DELTA_ENTRY_MERGED = IGAT_DELTA_ENTRY + 512
RGAT_DIR_DELTA_ENTRY = RGAT_DELTA_ENTRY_MERGED + 1056
GAT_METABLOCK_NUMBER = RGAT_DIR_DELTA_ENTRY + 512
MLC_FBL_COUNTER = GAT_METABLOCK_NUMBER + 960
BINARY_FBL_COUNTER = MLC_FBL_COUNTER + 2
BINARY_FBL_METABLOCK_COUNTER = BINARY_FBL_COUNTER + 2
MLC_WEARLEVELING_COUNTER = BINARY_FBL_METABLOCK_COUNTER + 2
ACTIVE_BLOCK_WRITE_OFFSET = MLC_WEARLEVELING_COUNTER + 2  # 1 BYTE PADDING
GAT_DELTA_SIZE_OFFSET = ACTIVE_BLOCK_WRITE_OFFSET + 4
IGAT_DELTA_SIZE_OFFSET = GAT_DELTA_SIZE_OFFSET + 2
GAT_DIR_DELTA_SIZE = IGAT_DELTA_SIZE_OFFSET + 2
RGAT_DELTA_SIZE = GAT_DIR_DELTA_SIZE + 2
RGAT_DIR_DELTA_SIZE = RGAT_DELTA_SIZE + 2

#DIAG_CONFIG.ini
GET_FS_DATA_FW_DIAG_OPCODE = 0x86
READ_FW_PARAM_DIAG_OPCODE = 0x65
READ_MML_PARAMETERS_SUBOPCODE = 0x03
READ_CONFIGURABLE_PERFORMANCE_SET   = 0xF6
BE_CONF_PERF_SETS_OFFSET            = 0x00
BE_CONF_PERF_MAX_NO_OF_SETS_OFFSETS = 0x30


def enum(*sequential, **named):

    enums = dict(list(zip(sequential, list(range(len(sequential))))), **named)
    return type('Enum', (), enums)



def GetWearLevelInfo(vtfContainer, blkType ):
    """
    Name : GetWearLevelInfo()
    Description : This function calls "Get Hot Count Diagnostic(0x61)", provides Wear Level Info.
    Arguments :
        vtfContainer - vtfContainer Object
        blkType - Block Type
    Returns : Wear level parameters (Like - average hot count, Number of Certain blocks)
    opcode = 0xC9
    subOpcode = 13
    """
    opcode      = 0xC9
    subopcode   = 13
    commandName = "Get Wear level Info"
    bankNum = 0
    cdb = [
        opcode, subopcode, blkType, 0,
        0, 0, 0, 0,
       0, 0, bankNum, 0,
      0, 0, 0, 0
    ]

    wlBuf = pyWrap.Buffer.CreateBuffer( 1, 0 )
    wlBuf = SendDiagnostic( vtfContainer, wlBuf, cdb, 0, 1, opcode, commandName )
    wlData = {
        "AverageHC"     : None,
        "NumBlocks"     : None,
      "WLCount"       : None,
      "HCWithinCycle" : None,
      "CopiedBlocks"  : None,
      "PageRover"     : None,
      "Blocks"        : None,
      "State"         : None,
      "hottestMP"     : None,
      "numZones"      : None,
      "Request"       : None,
      "MB"            : None,      
    }

    wlData["AverageHC"]     = wlBuf.GetFourBytesToInt( 0 )
    wlData["NumBlocks"]     = wlBuf.GetTwoBytesToInt( 4 )
    wlData["WLCount"]       = wlBuf.GetTwoBytesToInt( 6 )
    wlData["HCWithinCycle"] = wlBuf.GetTwoBytesToInt( 8 )
    wlData["CopiedBlocks"]  = wlBuf.GetTwoBytesToInt( 10 )
    wlData["PageRover"]     = wlBuf.GetTwoBytesToInt( 12 )
    # Resolution to SPARROW-1159:
    # Reading list of blocks on which wear levelling
    # is being carried out -- Aditya Gadgil on 28-Oct-2014
    wlblocks = []
    for index in range( 16 ):
        block = wlBuf.GetTwoBytesToInt( 14 + ( index * 2 ) )
        wlblocks.append( block )
    # end_for
    wlData["Blocks"] = wlblocks
    wlData["State"]         = wlBuf.GetOneByteToInt( 46 )

    return wlData
#end of GetWearLevelInfo

def GetHotCountsOffset(vtfContainer, subOpcode, blkType, bankNum = 0):
    """
    Name : GetHotCountsOffset()

    Description : This function calls "Get Hot Count Offset ( HCOffset) Diagnostic(0x61)", provides hot counts list.
                  This function is appicable only for SubOpcode 0x0A
    Arguments :
              vtfContainer - vtfContainer Object
              subOpcde - sub-opcode for hot count information for the blocks
              blkType - Block Type
    Returns :
          uint32 HotCountOffset;
    uint16 HotCountThreshold;
    uint16 HotCountReduction;

    opcode = 0x61

    """
    #Creating a buffer of 1 sector Size
    getMMLDataBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR, 0)
    commandName = "Get Hot Counts for All Blocks"
    opcode = DIAG_GET_HOT_COUNT_OPCODE
    HCoffset = 0
    HCthreshold = 0
    HCReduction = 0

    option = 0x00 # Length Mode:To determine how many sectors are required to for transferring all the data
    optNumberLo = ByteUtil.HighByte(option)
    optNumberHi = ByteUtil.LowByte(option)
    cdb = [opcode,subOpcode,optNumberHi,optNumberLo,
           0,0,0,0,
           0,0,bankNum,blkType,
          0,0,0,0]

    getMMLDataBuf = SendDiagnostic(vtfContainer, getMMLDataBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    HCoffset = getMMLDataBuf.GetFourBytesToInt(0x0)
    HCthreshold = getMMLDataBuf.GetTwoBytesToInt(0x4)
    HCReduction = getMMLDataBuf.GetTwoBytesToInt(0x6)

    return HCoffset, HCthreshold, HCReduction


def GetHotCounts(vtfContainer, subOpcode, blkType, bankNum = 0):
    """
    Name : GetHotCounts()

    Description : This function calls "Get Hot Count Diagnostic(0x61)", provides hot counts list.
                  This function is common to the sunopcodes 0x01-0x09
    Arguments :
              vtfContainer - vtfContainer Object
              subOpcde - sub-opcode for hot count information for the blocks
              blkType - Block Type

    Returns :
             totalNumOfBlks - toltal number of blocks in sector size
             hotCountArray - Hot Counts List
    metablkArray - corresponding metablock addresses' list

    opcode = 0x61

    """
    #offsets
    LENGTH_OF_BUFFER_IN_SECTORS_NORMAL_MODE = 0
    META_BLOCK_OFFSET = 2
    HOT_COUNT_OFFSET = 4

    metablkArray =[]
    hotCountArray = []

    #Creating a buffer of 1 sector Size
    getMMLDataBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR, 0)
    commandName = "Get Hot Counts for All Blocks"
    opcode = DIAG_GET_HOT_COUNT_OPCODE

    option = 0x00 # Length Mode:To determine how many sectors are required to for transferring all the data
    optNumberLo = ByteUtil.HighByte(option)
    optNumberHi = ByteUtil.LowByte(option)
    if subOpcode == 0x09: #(This opcode is common for both SLC and MLC, needs blkType input in cdb)

        cdb = [opcode,subOpcode,optNumberHi,optNumberLo,
               0,0,0,0,
               0,0,bankNum,blkType,
             0,0,0,0]
    else:
        cdb = [opcode,subOpcode,optNumberHi,optNumberLo,
               0,0,0,0,
               0,0,bankNum,blkType,
             0,0,0,0]

    getMMLDataBuf = SendDiagnostic(vtfContainer, getMMLDataBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    sectorLen = getMMLDataBuf.GetTwoBytesToInt(LENGTH_OF_BUFFER_IN_SECTORS_NORMAL_MODE)

    if sectorLen > 0:
        #Creating a buffer of sectorLen sector Size
        getMMLDataBuf = pyWrap.Buffer.CreateBuffer(sectorLen, 0x00)

        option = 0x01 #This option actually gets info for num. of sectors determined in option 0x01 - Ish
        optNumberLo = ByteUtil.HighByte(option)
        optNumberHi = ByteUtil.LowByte(option)
        if subOpcode == 0x09: #(This opcode is common for both SLC and MLC, needs blkType input in cdb)
            cdb = [opcode,subOpcode,optNumberHi,optNumberLo,
                   0,0,0,0,
                   0,0,bankNum,blkType,
                0,0,0,0]
        else:
            cdb = [opcode,subOpcode,optNumberHi,optNumberLo,
                   0,0,0,0,
                   0,0,bankNum,blkType,
                0,0,0,0]

        getMMLDataBuf = SendDiagnostic(vtfContainer, getMMLDataBuf, cdb, READ_DATA, sectorLen, opcode, commandName)

        totalNumOfBlks = getMMLDataBuf.GetTwoBytesToInt(LENGTH_OF_BUFFER_IN_SECTORS_NORMAL_MODE)

        metBlkOffset = 2
        hotCountOffset = 4
    else:
        totalNumOfBlks = 0

    for blkNum in range(0, totalNumOfBlks):
        metaBlkNum = getMMLDataBuf.GetTwoBytesToInt(META_BLOCK_OFFSET)
        hotCount = getMMLDataBuf.GetFourBytesToInt(HOT_COUNT_OFFSET)
        META_BLOCK_OFFSET = META_BLOCK_OFFSET + 6
        HOT_COUNT_OFFSET = HOT_COUNT_OFFSET + 6
# discarding invalid metablocks:
        if (metaBlkNum == 0xFFFF):
            continue
        metablkArray.append(metaBlkNum)
        hotCountArray.append(hotCount)
    totalNumOfBlks = len(metablkArray)

    return (totalNumOfBlks, hotCountArray, metablkArray)
#end of GetHotCountList


def GetHotCountofAllBlks(vtfContainer, totalNumOfBlks,numberOfMetaPlane):
    """
    Name : GetHotCountofAllBlks()

    Description : This function calls "GET_MML_DATA(0xC9)", provides hot counts list.
    Arguments :
              vtfContainer - vtfContainer Object
    Returns :
             hotCountArray - Hot Counts List

    opcode = 0xC9
    subopcode = 50

    """
    #offsets
    HOT_COUNT_OFFSET = 0
    hotCountArray = []
    #changed size from 10 * multi metaplane for MMP
    mmlDataBuffer = pyWrap.Buffer.CreateBuffer(10*numberOfMetaPlane,0)
    opcode = GET_MML_DATA
    subOpcode = 50
    option=0
    cdbData = [opcode,subOpcode,option,0,0,0,0,0,0,0,0,0,0,0,0,0]
    direction = READ_DATA

    SendDiagnostic(vtfContainer, mmlDataBuffer , cdbData , direction , 10*numberOfMetaPlane )

    for blkNum in range(0, totalNumOfBlks):
        hotCount = mmlDataBuffer.GetTwoBytesToInt(HOT_COUNT_OFFSET)
        HOT_COUNT_OFFSET = HOT_COUNT_OFFSET + 2
        hotCountArray.append(hotCount)

    return hotCountArray
#end of GetHotCountofAllBlks

def GetSinglePlaneControlBlocksList(vtfContainer, fwConfigObj,numGATBlocks):
    """
    Name : GetHotCountofAllBlks()

    Description : This function calls "GET_MML_DATA(0xC9)", provides hot counts list.
    Arguments :
              vtfContainer - vtfContainer Object
    Returns :
             hotCountArray - Hot Counts List

    opcode = 0xC9
    subopcode = 50

    """
    MAX_METAPLANES = 4

    #offsets
    SINGLE_PLANE_BLOCK_OFFSET = 0
    singlePlaneControlBlocksList = []
    mipBlkList = {}
    gatBlkList = {}
    gatFBLList = {}
    gatPrimaryBlkList = []
    gatSecondary = []
    gatFBLTemp = []
    mipPrimary = []
    mipSecondary = []

    numOfMetaplane = fwConfigObj.numberOfMetaPlane - fwConfigObj.dummyMetaPlane
    numOfPlane = fwConfigObj.dieInterleave * fwConfigObj.planeInterleave * numOfMetaplane
    mmlDataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR * 7, 0)
    opcode = GET_MML_DATA
    subOpcode = 62
    option=0
    cdbData = [opcode,subOpcode,option,0,0,0,0,0,0,0,0,0,0,0,0,0]
    direction = READ_DATA

    SendDiagnostic(vtfContainer, mmlDataBuffer , cdbData , direction , SINGLE_SECTOR * 7, opcode)

    numOfFBLPerMMP = []
    for mmp in range(0, numOfMetaplane):
        numOfFBLPerMMP.append( mmlDataBuffer.GetTwoBytesToInt(SINGLE_PLANE_BLOCK_OFFSET))
        SINGLE_PLANE_BLOCK_OFFSET += 2

    configParam = FileData.GetFile14Data(vtfContainer)
    GATFbl =  configParam["numofGATFblBlocks"] * numOfMetaplane
    GATBlkIndex = ((numGATBlocks) * numOfPlane) - 1 - GATFbl
    totalNumOfBlks = (numGATBlocks * numOfPlane) + sum(numOfFBLPerMMP) - GATFbl

    numOfBlks = 0
    index = 0
    blocks = []
    GATFBLMP = [[],[],[],[]]
    GATFBL = []
    for blkNum in range(0, totalNumOfBlks):
        metaBlock = mmlDataBuffer.GetTwoBytesToInt(SINGLE_PLANE_BLOCK_OFFSET)
        SINGLE_PLANE_BLOCK_OFFSET += 2
        planeNumber = mmlDataBuffer.GetTwoBytesToInt(SINGLE_PLANE_BLOCK_OFFSET)
        SINGLE_PLANE_BLOCK_OFFSET += 2
        hotCount  = mmlDataBuffer.GetTwoBytesToInt(SINGLE_PLANE_BLOCK_OFFSET)
        SINGLE_PLANE_BLOCK_OFFSET += 2

        if blkNum == 0:
            mipPrimary =  [metaBlock,planeNumber,hotCount]
        elif blkNum == 1:
            mipSecondary =  [metaBlock,planeNumber,hotCount]
        else:
            if blkNum < GATBlkIndex:
                gatPrimaryBlkList.append([metaBlock,planeNumber,hotCount])
            elif blkNum == GATBlkIndex :
                gatSecondary = [metaBlock,planeNumber,hotCount]
                GATFBLIndex = GATBlkIndex + numOfFBLPerMMP[index]
            else:
                GATFBLMP[index].append([metaBlock,planeNumber,hotCount])
                GATFBL.append([metaBlock,planeNumber,hotCount])

                if blkNum == GATFBLIndex:
                    index += 1
                    if index < numOfMetaplane:
                        GATFBLIndex += numOfFBLPerMMP[index]

    # Chcek for extra Bytes beyond the buffer value
    metaBlock = mmlDataBuffer.GetTwoBytesToInt(SINGLE_PLANE_BLOCK_OFFSET)
    SINGLE_PLANE_BLOCK_OFFSET += 2
    planeNumber = mmlDataBuffer.GetTwoBytesToInt(SINGLE_PLANE_BLOCK_OFFSET)
    SINGLE_PLANE_BLOCK_OFFSET += 2
    hotCount  = mmlDataBuffer.GetTwoBytesToInt(SINGLE_PLANE_BLOCK_OFFSET)
    SINGLE_PLANE_BLOCK_OFFSET += 2
    if (metaBlock != 0 or planeNumber != 0 or hotCount != 0):
        raise TestError.TestFailError(vtfContainer.GetTestName(), "Block allocated beyond the Range")

    mipBlkList = {'mipPrimary':mipPrimary,'mipSecondary':mipSecondary}
    gatBlkList = {'gatPrimary': gatPrimaryBlkList,'gatSecondary': gatSecondary}
    gatFBLList = {'gatFBL': GATFBL, 'gatFBLMP0':GATFBLMP[0], 'gatFBLMP1':GATFBLMP[1], 'gatFBLMP2':GATFBLMP[2], 'gatFBLMP3':GATFBLMP[3]}
    singlePlaneControlBlocksList = [mipBlkList,gatBlkList,gatFBLList,numOfFBLPerMMP]

    return singlePlaneControlBlocksList
##end of GetHotCountofAllBlks

def GetMMLSlotCountInfo(vtfContainer):

    commandName="GetMMLSlotCountInfo"
    opcode=0xc9
    subOpcode=58
    getMMLDataBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    cdb = [opcode, subOpcode, 0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, READ_DATA))
    try:
        getMMLDataBuf      = SendDiagnostic(vtfContainer,getMMLDataBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
        slotThreshold    = getMMLDataBuf.GetOneByteToInt(0x00)
    except:
        vtfContainer.GetLogger().Info("", "[GetMMLSlotCountInfo]Diag Failed, unable to get MAX_NUM_UNCOMMITTED_SRC_MLC")
        slotThreshold    = 0

    return slotThreshold
def GetHotCountsForControlBlocks(vtfContainer, subOpcode, blkType=0, bankNum = 0):
    """
    Name : GetHotCountsForControlBlocks()

    Description : This function calls "Get Hot Count Diagnostic(0x61)", provides hot counts for control blocks.
                  This function is common to the sunopcodes 0x01-0x09
    Arguments :
              vtfContainer - vtfContainer Object
              subOpcde - sub-opcode for hot count information for the blocks
    0x03 - Get Hot Counts for Boot and FS Blocks
              blkType - Block Type

    Returns :
             totalNumOfBlks - toltal number of blocks in sector size
             hotCountArray - Hot Counts List
    metablkArray - corresponding metablock addresses' list

    opcode = 0x61

    """
    #offsets
    LENGTH_OF_BLOCKS_IN_LIST = 0
    META_BLOCK_OFFSET = 2
    HOT_COUNT_OFFSET = 4

    metablkArray =[]
    hotCountArray = []

    #Creating a buffer of 1 sector Size
    getMMLDataBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR, 0)
    commandName = "Get Hot Counts for Control Blocks"
    opcode = DIAG_GET_HOT_COUNT_OPCODE

    option = 0x01 #Data Mode
    optNumberLo = ByteUtil.HighByte(option)
    optNumberHi = ByteUtil.LowByte(option)
    cdb = [opcode,subOpcode,optNumberHi,optNumberLo,
           0,0,0,0,
           0,0,bankNum,blkType,
          0,0,0,0]

    getMMLDataBuf = SendDiagnostic(vtfContainer, getMMLDataBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    totalNumOfBlks = getMMLDataBuf.GetTwoBytesToInt(LENGTH_OF_BLOCKS_IN_LIST)

    for blkNum in range(0, totalNumOfBlks):
        metaBlkNum = getMMLDataBuf.GetTwoBytesToInt(META_BLOCK_OFFSET)
        hotCount = getMMLDataBuf.GetFourBytesToInt(HOT_COUNT_OFFSET)
        META_BLOCK_OFFSET = META_BLOCK_OFFSET + 6
        HOT_COUNT_OFFSET = HOT_COUNT_OFFSET + 6
        # discarding invalid metablocks:
        if (metaBlkNum == 0xFFFF):
            continue
        metablkArray.append(metaBlkNum)
        hotCountArray.append(hotCount)
    totalNumOfBlks = len(metablkArray)

    return (totalNumOfBlks, hotCountArray, metablkArray)
#end of GetHotCountsForControlBlocks

def HotCountReductionBoundary(vtfContainer, blkType):
    """
    Name : HotCountReductionBoundary()

    Description : This function calls "Get Hot Count Diagnostic(0x61)", provides threshold and reduction.

    Arguments :
              vtfContainer - vtfContainer Object
              blkType - Block Type

    Returns :
             wlData - Wear level reduction data

    opcode = 0x61
    """
    #offsets
    AVERAGE_HOTCOUNT_OFFSET = 0
    NUM_OF_CRETAIN_BLKS_OFFSET = 4
    WEARLEVEL_COUNT_OFFSET = 6

    commandName = "Get Wear level Info"
    opcode = DIAG_GET_HOT_COUNT_OPCODE
    subOpcode = 0x0A
    bankNum = 0

    cdb = [opcode,subOpcode,0,0,
           0,0,0,0,
           0,0,bankNum,blkType,
          0,0,0,0]

    wlBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,0)

    wlBuf = SendDiagnostic(vtfContainer, wlBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    wlData = {"hotCountOffset":None, "hotCountThreshold":None, "hotCountDecrement":None}

    wlData["hotCountOffset"] = wlBuf.GetFourBytesToInt(AVERAGE_HOTCOUNT_OFFSET)
    wlData["hotCountThreshold"] = wlBuf.GetTwoBytesToInt(NUM_OF_CRETAIN_BLKS_OFFSET)
    wlData["hotCountDecrement"] = wlBuf.GetTwoBytesToInt(WEARLEVEL_COUNT_OFFSET)

    return wlData
#end of HotCountReductionBoundary

def SetHotCountToAllBlks(vtfContainer, hotCountValue,blockType,bankNum = 0, skipForRelinkblks = 0):
    """
    Name : SetHotCountToAllBlks()

    Description : This function calls "Set Hot Counts Diagnostic(0x62)", sets given hot count value

    Arguments :
              vtfContainer - vtfContainer Object
              hotCountValue - hot count value for setting
              blockType - Block Type

    Returns : None

    opcode = 0x62

    subOpcode = 0x0
    """
    #offsets
    HOT_COUNT_OFFSET = 0
    BLOCK_TYPE_OFFSET = 4

    commandName = "Set Hot count To All Blocks"
    opcode = DIAG_SET_HOT_COUNT_OPCODE
    subOpcode = 0x0

    setHotCountBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,0)

    lgHighWord = ByteUtil.HighWord(hotCountValue)
    lgLowWord = ByteUtil.LowWord(hotCountValue)

    lgHighLsb = ByteUtil.LowByte(lgHighWord)
    lgHighMsb = ByteUtil.HighByte(lgHighWord)
    lgLowLsb = ByteUtil.LowByte(lgLowWord)
    lgLowMsb = ByteUtil.HighByte(lgLowWord)


    setHotCountBuf.SetFourBytes(HOT_COUNT_OFFSET, hotCountValue)
    setHotCountBuf.SetByte(BLOCK_TYPE_OFFSET, blockType)

    cdb = [opcode, subOpcode, lgLowLsb,lgLowMsb,
           lgHighLsb,lgHighMsb,skipForRelinkblks,0,
           0,0,bankNum,blockType,
          0,0,0,0]

    SendDiagnostic(vtfContainer, setHotCountBuf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)
#end of   SetHotCountToAllBlks

def SetHotCountToAllGatAndMipBlocks(vtfContainer, hotCountValue,blockType,bankNum = 0, skipForRelinkblks = 0):
    """
    Name : GetHotCountofAllBlks()

    Description : This function calls "GET_MML_DATA(0xC9)", provides hot counts list.
    Arguments :
              vtfContainer - vtfContainer Object
    Returns :
             hotCountArray - Hot Counts List

    opcode = 0x62
    subOpcode = 0x4

    """
    HOT_COUNT_OFFSET = 0
    BLOCK_TYPE_OFFSET = 4

    commandName = "Set Hot count To All GAT and MIP Blocks"
    opcode = DIAG_SET_HOT_COUNT_OPCODE
    subOpcode = 0x4

    setHotCountBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,0)

    lgHighWord = ByteUtil.HighWord(hotCountValue)
    lgLowWord = ByteUtil.LowWord(hotCountValue)

    lgHighLsb = ByteUtil.LowByte(lgHighWord)
    lgHighMsb = ByteUtil.HighByte(lgHighWord)
    lgLowLsb = ByteUtil.LowByte(lgLowWord)
    lgLowMsb = ByteUtil.HighByte(lgLowWord)


    setHotCountBuf.SetFourBytes(HOT_COUNT_OFFSET, hotCountValue)
    setHotCountBuf.SetByte(BLOCK_TYPE_OFFSET, blockType)

    cdb = [opcode, subOpcode, lgLowLsb,lgLowMsb,
           lgHighLsb,lgHighMsb,skipForRelinkblks,0,
           0,0,bankNum,blockType,
          0,0,0,0]

    SendDiagnostic(vtfContainer, setHotCountBuf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)

def SetAvgHotCounters(vtfContainer, avgHc, numOfCertainBlks, wlCount, hcInCycle,copiedBlks,pageRover, blkTyp, bankNum=0):
    """
    Name : SetAvgHotCounters()

    Description : This function calls "Set WL Info Diagnostic(0x62)", sets given average hot count value

    Arguments :
              vtfContainer - vtfContainer Object
              avgHc - avreage hot count value for setting
              numOfCertainBlks - number of Certain blocks
              wlCount - Wear level count
              hcInCycle - hot count within cycle
              copiedBlks - copied blocks
              pageRover - page rover
              blkTyp - Block Type

    Returns : None

    opcode = 0x62

    subOpcode = 0x1
    """
    AVG_HOTCOUNT_OFFSET = 0
    NUM_OF_CRETAIN_BLKS_OFFSET = 0x04
    WEARLEVEL_COUNT_OFFSET = 0x06
    HOTCOUNT_WITHIN_CYCLE_OFFSET = 0x08
    COPIED_BLKS_OFFSET = 0x0A
    PAGE_ROVER_OFFSET = 0x0C

    commandName = "Set average hot count counters"
    opcode = DIAG_SET_HOT_COUNT_OPCODE
    subOpcode = 0x1
    bankNum = 0

    cdb = [opcode,subOpcode,0,0,
           0,0,0,0,
           0,0,bankNum,blkTyp,
          0,0,0,0]

    hotCountBuf  = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,0)

    hotCountBuf.SetFourBytes(AVG_HOTCOUNT_OFFSET,avgHc)
    hotCountBuf.SetTwoBytes(NUM_OF_CRETAIN_BLKS_OFFSET,numOfCertainBlks)
    hotCountBuf.SetTwoBytes(WEARLEVEL_COUNT_OFFSET,wlCount)
    hotCountBuf.SetTwoBytes(HOTCOUNT_WITHIN_CYCLE_OFFSET,hcInCycle)
    hotCountBuf.SetTwoBytes(COPIED_BLKS_OFFSET,copiedBlks)
    hotCountBuf.SetTwoBytes(PAGE_ROVER_OFFSET,pageRover)

    SendDiagnostic(vtfContainer, hotCountBuf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)

#end of SetAvgHotCounters

def SetHotCountOneBlock(vtfContainer, mbAddr, newHotCount, bankNum=0, blkType=0):
    """
    Name: SetHotCountOneBlock
    Description: This diagnostic sets Hot Cont for an individual block.
    opcode = 0x62
    sub Opcode = 2
    """

    commandName = "Set hot count of an individual block"
    opcode = DIAG_SET_HOT_COUNT_OPCODE
    subOpcode = 0x2
    bankNum = 0
    hotCountBuf = pyWrap.Buffer.CreateBuffer(1,0) #dummy buf

    newHcLowByte = ByteUtil.LowByte(newHotCount)
    newHcHighByte = ByteUtil.HighByte(newHotCount)
    mbAddrHighByte = ByteUtil.HighByte(mbAddr)
    mbAddrLowByte = ByteUtil.LowByte(mbAddr)

    cdb = [opcode,subOpcode,
           newHcLowByte,newHcHighByte,0,0,
           mbAddrLowByte,mbAddrHighByte,
          0,0,bankNum,blkType,
          0,0,0,0]

    SendDiagnostic(vtfContainer, hotCountBuf, cdb, WRITE_DATA, 0, opcode, commandName)

def SetHotCountSPCBOneBlock(vtfContainer, mbAddr, newHotCount, plane, bankNum=0, blkType=2):
    """
    Name: SetHotCountSPCBOneBlock
    Description: This diagnostic sets Hot Count for an individual SPCB block.
    opcode = 0x62
    sub Opcode = 4
    blkType = 2
    """

    commandName = "Set hot count of an individual SPCB block"
    opcode = DIAG_SET_HOT_COUNT_OPCODE
    subOpcode = 0x4
    bankNum = 0
    hotCountBuf = pyWrap.Buffer.CreateBuffer(1,0) #dummy buf

    newHcLowByte = ByteUtil.LowByte(newHotCount)
    newHcHighByte = ByteUtil.HighByte(newHotCount)
    mbAddrHighByte = ByteUtil.HighByte(mbAddr)
    mbAddrLowByte = ByteUtil.LowByte(mbAddr)

    cdb = [opcode,subOpcode,
           newHcLowByte,newHcHighByte,0,0,
           mbAddrLowByte,mbAddrHighByte,
          plane,0,bankNum,blkType,
          0,0,0,0]

    SendDiagnostic(vtfContainer, hotCountBuf, cdb, WRITE_DATA, 0, opcode, commandName)
def GetGeneralErrorLogInfo(vtfContainer):
    """
    Name : GetGeneralErrorLogInfo()

    Description : This function calls "Read Error Log Diagnostic(0x61)", provides general error log information.

    Arguments :
              vtfContainer - vtfContainer Object
              elfGeneralInfo - ELFGeneralInfo object

    Returns :
             elfGeneralInfo - ELFGeneralInfo object

    opcode : 0x64

    subopcode : 0x0
    """

    #offsets
    ERROR_LOG_DIAG_GENINFO_OFFSET_LLS_ENTRIES = 4
    ERROR_LOG_DIAG_GENINFO_OFFSET_COUNTER_ENTRIES = 6
    ERROR_LOG_DIAG_GENINFO_OFFSET_LEN_LLS = 8
    ERROR_LOG_DIAG_GENINFO_OFFSET_LEN_COUNTER = 10
    ERROR_LOG_DIAG_GENINFO_OFFSET_LLS_RAM = 12
    ERROR_LOG_DIAG_GENINFO_OFFSET_COUNTER_RAM = 14

    commandName = "Get General Error Log Info"
    opcode = DIAG_READ_BE_ERROR_LOG
    subOpcode = 0
    errorLogDataBuf = pyWrap.Buffer.CreateBuffer(1, 0x00)
    subOpcodeLsb = ByteUtil.LowByte(subOpcode)
    subOpcodeMsb = ByteUtil.HighByte(subOpcode)

    # Call Error Log Diag to featch general inforamtion of Error Log File
    cdb = [opcode, 0, subOpcodeLsb, subOpcodeMsb,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]


    errorLogDataBuf = SendDiagnostic(vtfContainer, errorLogDataBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    elfGeneralInfo = {"numLLSRecords":None, "numCounterRecords":None, "numOfSectorsRequiedForLLSRecord":None, "numOfSectorsRequiedForCounterRecord":None, "numLLSRecordsInRAM":None, "numCounterRecordsInRAM":None }

    elfGeneralInfo["numLLSRecords"] = errorLogDataBuf.GetTwoBytesToInt(ERROR_LOG_DIAG_GENINFO_OFFSET_LLS_ENTRIES)
    elfGeneralInfo["numCounterRecords"] = errorLogDataBuf.GetTwoBytesToInt(ERROR_LOG_DIAG_GENINFO_OFFSET_COUNTER_ENTRIES)
    elfGeneralInfo["numOfSectorsRequiedForLLSRecord"] = errorLogDataBuf.GetTwoBytesToInt(ERROR_LOG_DIAG_GENINFO_OFFSET_LEN_LLS)
    elfGeneralInfo["numOfSectorsRequiedForCounterRecord"] = errorLogDataBuf.GetTwoBytesToInt(ERROR_LOG_DIAG_GENINFO_OFFSET_LEN_COUNTER)
    elfGeneralInfo["numLLSRecordsInRAM"] = errorLogDataBuf.GetTwoBytesToInt(ERROR_LOG_DIAG_GENINFO_OFFSET_LLS_RAM )
    elfGeneralInfo["numCounterRecordsInRAM"] = errorLogDataBuf.GetTwoBytesToInt(ERROR_LOG_DIAG_GENINFO_OFFSET_COUNTER_RAM)

    return elfGeneralInfo
#end


def WriteEccPage(vtfContainer, chip, die, plane, block, wordline, page, eccPage, eccPageCount, dataBuf, isBiCS=1):
    """
    Description: Writes to ECC page ignoring the ECC engine
    """
    import FwConfig as FwConfig
    FwConfigObj=FwConfig.FwConfig(vtfContainer)
    commandName = "WriteEccPage"
    opcode = 0xB2
    option = 0x0600

    blockLsb = ByteUtil.LowByte(block)
    blockMsb = ByteUtil.HighByte(block)
    pageCountLsb = ByteUtil.LowByte(eccPageCount)
    pageCountMsb = ByteUtil.HighByte(eccPageCount)
    optionLsb = ByteUtil.LowByte(option)
    optionMsb = ByteUtil.HighByte(option)

    if isBiCS:
        mlcPage = 0
        cdb = [opcode, chip, die, plane,
               blockLsb, blockMsb,wordline,page,
               mlcPage,eccPage,pageCountLsb,pageCountMsb,
             0,0,optionLsb,optionMsb]

    else:
        cdb = [opcode, chip, die, plane,
               blockLsb, blockMsb,wordline,page,
               eccPage,0,pageCountLsb,pageCountMsb,
             0,0,optionLsb,optionMsb]

    dataBuf = SendDiagnostic(vtfContainer, dataBuf, cdb, WRITE_DATA, ((FwConfigObj.sectorsPerEccPage*eccPageCount)+1), opcode, commandName)

    return dataBuf


def ReadAllLLSRecords(vtfContainer):
    """
    Name : ReadAllLLSRecords()

    Description : This function calls "Read Error Log Diagnostic(0x61)", provides LLS error log entry.

    Arguments :
              vtfContainer - vtfContainer Object
              elfGeneralInfo - ELFGeneralInfo object

    Returns :
             elfLLSRecords - ELFGeneralInfo object

    opcode : 0x64

    subopcode : 0x1
    """
    #offsets
    ERROR_LOG_DIAG_LLSRECORDS_OFFSET_ERROR_STATUS = 8
    ERROR_LOG_DIAG_LLSRECORDS_OFFSET_ERROR_LBA = 16
    ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_BANK = 30
    ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_DIE = 31
    ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_SECTOR = 32
    ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_PAGE = 33
    ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_BLOCK_INDEX = 35
    ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_PLANE = 36
    ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_CHIP = 37
    ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_BLOCK_LIST =38

    #constants
    MAX_NUMBER_OF_BLOCKS_IN_BLOCK_LIST = 8
    ELF_ERROR_RECORD_LEN = 64
    NUMBER_OF_BYTES_FOR_BLOCK_NUMBER = 2

    #Call the Diag with different SubOpcode to get the number of records.
    elfGeneralInfo = GetGeneralErrorLogInfo(vtfContainer)

    commandName = "Read all LLS Records"
    opcode = 0x64
    subOpcode = 1
    subOpcodeLsb = ByteUtil.LowByte(subOpcode)
    subOpcodeMsb = ByteUtil.HighByte(subOpcode)
    errorLogDataBuf = pyWrap.Buffer.CreateBuffer(elfGeneralInfo["numOfSectorsRequiedForLLSRecord"], 0x00)

    # Call Error Log Diag to featch general inforamtion of Error Log File
    cdb = [opcode, 0, subOpcodeLsb, subOpcodeMsb,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    errorLogDataBuf = SendDiagnostic(vtfContainer, errorLogDataBuf, cdb, READ_DATA, elfGeneralInfo["numOfSectorsRequiedForLLSRecord"], opcode, commandName)
    elfLLSRecords = []
    offset = 0
    for index in range(0, elfGeneralInfo["numLLSRecords"])  :
        llsRec = []
        errorStatus = errorLogDataBuf.GetTwoBytesToInt(offset + ERROR_LOG_DIAG_LLSRECORDS_OFFSET_ERROR_STATUS)
        errorLba = errorLogDataBuf.GetFourBytesToInt(offset + ERROR_LOG_DIAG_LLSRECORDS_OFFSET_ERROR_LBA)
        bank = errorLogDataBuf.GetOneByteToInt(offset + ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_BANK)
        chip =errorLogDataBuf.GetOneByteToInt(offset + ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_CHIP)
        die = errorLogDataBuf.GetOneByteToInt(offset + ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_DIE)
        plane=errorLogDataBuf.GetOneByteToInt(offset + ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_PLANE)
        #calculate the block index
        blockIndex = errorLogDataBuf.GetOneByteToInt(offset + ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_BLOCK_INDEX)
        block = errorLogDataBuf.GetTwoBytesToInt(offset + ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_BLOCK_LIST + NUMBER_OF_BYTES_FOR_BLOCK_NUMBER*plane)

        #get the wordline from page addressing
        page =errorLogDataBuf.GetTwoBytesToInt(offset+ ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_PAGE)

        #wordLine = errorLogObj.GetWordLineFromPage(bank,chip,die,plane,block,page)
        llsRec.extend([errorStatus, errorLba, bank, chip, die, plane, block, page])
        elfLLSRecords.append(llsRec)

        #increment the offset value
        offset = offset + ELF_ERROR_RECORD_LEN

    return elfLLSRecords
#end of ReadAllLLSRecords

def ReadAllLLSRecordsFromRAM(vtfContainer):
    """
    Name : ReadAllLLSRecords()

    Description : This function calls "Read Error Log Diagnostic(0x61)", provides LLS error log entry.

    Arguments :
              vtfContainer - vtfContainer Object
              elfGeneralInfo - ELFGeneralInfo object

    Returns :
             elfLLSRecords - ELFGeneralInfo object

    opcode : 0x64

    subopcode : 0x1
    """
    #offsets
    ERROR_LOG_DIAG_LLSRECORDS_OFFSET_ERROR_STATUS = 8
    ERROR_LOG_DIAG_LLSRECORDS_OFFSET_ERROR_LBA = 16
    ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_BANK = 30
    ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_DIE = 31
    ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_SECTOR = 32
    ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_PAGE = 33
    ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_BLOCK_INDEX = 35
    ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_PLANE = 36
    ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_CHIP = 37
    ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_BLOCK_LIST =38

    #constants
    MAX_NUMBER_OF_BLOCKS_IN_BLOCK_LIST = 8
    ELF_ERROR_RECORD_LEN = 64
    NUMBER_OF_BYTES_FOR_BLOCK_NUMBER = 2

    #Call the Diag with different SubOpcode to get the number of records.
    elfGeneralInfo = GetGeneralErrorLogInfo(vtfContainer)
    elfGeneralInfo["numOfSectorsRequiedForLLSRecord"] = 1

    commandName = "Read all LLS Records From RAM"
    opcode = 0x64
    subOpcode = 3
    subOpcodeLsb = ByteUtil.LowByte(subOpcode)
    subOpcodeMsb = ByteUtil.HighByte(subOpcode)
    errorLogDataBuf = pyWrap.Buffer.CreateBuffer(elfGeneralInfo["numOfSectorsRequiedForLLSRecord"], 0x00)

    # Call Error Log Diag to featch general inforamtion of Error Log File
    cdb = [opcode, 0, subOpcodeLsb, subOpcodeMsb,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    errorLogDataBuf = SendDiagnostic(vtfContainer, errorLogDataBuf, cdb, READ_DATA, elfGeneralInfo["numOfSectorsRequiedForLLSRecord"], opcode, commandName)
    elfLLSRecords = []
    offset = 0
    for index in range(0, elfGeneralInfo["numLLSRecordsInRAM"])  :
        llsRec = []
        errorStatus = errorLogDataBuf.GetTwoBytesToInt(offset + ERROR_LOG_DIAG_LLSRECORDS_OFFSET_ERROR_STATUS)
        errorLba = errorLogDataBuf.GetFourBytesToInt(offset + ERROR_LOG_DIAG_LLSRECORDS_OFFSET_ERROR_LBA)
        bank = errorLogDataBuf.GetOneByteToInt(offset + ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_BANK)
        chip =errorLogDataBuf.GetOneByteToInt(offset + ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_CHIP)
        die = errorLogDataBuf.GetOneByteToInt(offset + ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_DIE)
        plane=errorLogDataBuf.GetOneByteToInt(offset + ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_PLANE)

        #calculate the block index
        blockIndex = errorLogDataBuf.GetOneByteToInt(offset + ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_BLOCK_INDEX)
        block = errorLogDataBuf.GetTwoBytesToInt(offset + ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_BLOCK_LIST + NUMBER_OF_BYTES_FOR_BLOCK_NUMBER*blockIndex)

        #get the wordline from page addressing
        page =errorLogDataBuf.GetTwoBytesToInt(offset+ ERROR_LOG_DIAG_LLSRECORDS_OFFSET_PA_PAGE)

        #wordLine = errorLogObj.GetWordLineFromPage(bank,chip,die,plane,block,page)
        llsRec.extend([errorStatus, errorLba, bank, chip, die, plane, block, page])
        elfLLSRecords.append(llsRec)

        #increment the offset value
        offset = offset + ELF_ERROR_RECORD_LEN

    return elfLLSRecords
#end of ReadAllLLSRecords

def GetNumErrLogEventsReadErrorLog(vtfContainer):
    """
    Name : ReadErrorLog()

    Description : This function calls "Read Error Log Diagnostic(0x82)", provides size of error log entry.

    Arguments :
              vtfContainer - vtfContainer Object
              elfGeneralInfo - ELFGeneralInfo object

    Returns :
             elfGeneralInfo - ELFGeneralInfo object

    opcode : 0x82

    option : 0x4
    """
    #offsets
    NUM_OF_LOGGER_EVENTS_OFFSET = 0

    commandName = "ReadErrorLog"
    opcode = 0x82
    option = 4
    optionLo = ByteUtil.LowByte(option)
    optionHi = ByteUtil.HighByte(option)
    #validationErrorLogObj = ValidationErrorLog.ELFGeneralInfo()
    errorLogDataBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR, 0x00)
    cdb =  [opcode, 0, optionLo, optionHi, 0, 0, 0, 0, SINGLE_SECTOR, 0, 0, 0, 0, 0, 0, 0]

    errorLogDataBuf = SendDiagnostic(vtfContainer, errorLogDataBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    numOfErrorLogEvents = errorLogDataBuf.GetTwoBytesToInt(NUM_OF_LOGGER_EVENTS_OFFSET)

    return numOfErrorLogEvents
#end of ReadErrorLog
def ReadAllCounterRecords(vtfContainer, elfGeneralInfo):
    """
    Name : ReadAllCounterRecords()

    Description : This function calls "Read Error Log Diagnostic(0x61)", provides all counter log entries.

    Arguments :
              vtfContainer - vtfContainer Object
              elfGeneralInfo - ELFGeneralInfo object

    Returns :
             elfLLSRecords - ELFGeneralInfo object

    opcode : 0x64

    subopcode : 0x2
    """
    #offsets
    ERROR_LOG_DIAG_COUNTERRECORDS_OFFSET_COUNTER_PF = 8
    ERROR_LOG_DIAG_COUNTERRECORDS_OFFSET_COUNTER_EF = 10
    ERROR_LOG_DIAG_COUNTERRECORDS_OFFSET_COUNTER_UECC = 18

    #constants
    ELF_ERROR_RECORD_LEN = 64

    commandName = "Read all counter Records"
    opcode = 0x64
    subOpcode = 2

    assert elfGeneralInfo.numCounterRecords > 0 ,"Number of Counter records is [%d], it should be greater than zero"%(elfGeneralInfo.numCounterRecords)
    assert elfGeneralInfo.numOfSectorsRequiedForCounterRecord > 0 ,"Length of Counter records is [%d], it should be greater than zero"%(elfGeneralInfo.numOfSectorsRequiedForCounterRecord)

    elfCounterRecords = [ValidationErrorLog.ELFCounterRecord()
                         for each in range(0, elfGeneralInfo.numCounterRecords)]

    errorLogDataBuf = pyWrap.Buffer.CreateBuffer(elfGeneralInfo.numOfSectorsRequiedForCounterRecord,0x00)

    subOpcodeLsb = ByteUtil.LowByte(subOpcode)
    subOpcodeMsb = ByteUtil.HighByte(subOpcode)


    # Call Error Log Diag to featch general inforamtion of Error Log File
    cdb = [opcode, 0, subOpcodeLsb, subOpcodeMsb,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    errorLogDataBuf = SendDiagnostic(vtfContainer, errorLogDataBuf, cdb, READ_DATA, elfGeneralInfo.numOfSectorsRequiedForCounterRecord, opcode, commandName)

    offset = 0
    for index in range(0, elfGeneralInfo.numCounterRecords)  :

        elfCounterRecords[index].counterPF = errorLogDataBuf.GetTwoBytesToInt(offset+
                                                                              ERROR_LOG_DIAG_COUNTERRECORDS_OFFSET_COUNTER_PF)

        elfCounterRecords[index].counterEF = errorLogDataBuf.GetTwoBytesToInt(offset+
                                                                              ERROR_LOG_DIAG_COUNTERRECORDS_OFFSET_COUNTER_EF)

        elfCounterRecords[index].counterUECC = errorLogDataBuf.GetTwoBytesToInt(offset+
                                                                                ERROR_LOG_DIAG_COUNTERRECORDS_OFFSET_COUNTER_UECC)

        offset = offset + ELF_ERROR_RECORD_LEN


    return elfCounterRecords
#end of ReadAllCountersRecords

def GetHighByte(num):
    return (num & 0xFF00) >> 8

def GetLowByte(num):
    return num & 0x00FF

def ReadEccPage(vtfContainer, outputBuffer, physAddress, eccPageCount, option):

    logger = vtfContainer.GetLogger()
    opcode = 0xB1
    if outputBuffer is None:
        outputBuffer = pyWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_1, isSector=True)
    diagCmd = pyWrap.DIAG_FBCC_CDB()
    diagCmd.cdb = [opcode, physAddress.chip, physAddress.die, physAddress.plane, GetLowByte(physAddress.block),
                   GetHighByte(physAddress.block), physAddress.wordLine, physAddress.string, physAddress.mlcLevel, physAddress.eccPage, GetLowByte(eccPageCount),
                   GetHighByte(eccPageCount),0,0, GetLowByte(option), GetHighByte(option)]

    diagCmd.cdbLen = 16
    direction = 0
    logger.Info("","Executing diag: ReadECCPage() -  Opcode : 0x%x"%opcode)
    try:

        sctpCommand = pyWrap.SCTPCommand.SCTPCommand(diagCmd, outputBuffer, pyWrap.DIRECTION_OUT)
        sctpCommand.Execute()
    except Exception as e:
        raise TestError.TestFailError("","ReadECCPage() diag failed with error: %s"%e)
    return outputBuffer


def ReadAllErrorLogs(vtfContainer,isROmode=False):
    """
    Name : ReadAllErrorLogs

    Description : This function reads error log entries from File50 using diagnostic command 0x82

    Arguments : vtfContainer - vtfContainer Object

    Returns : noOfErrorsLogs, errorLogObj

    opcode : 0x82
    """

    #Offsets
    ERROR_LOG_DIAG_READ_ONLY_MODE_SIGNATURE = 4
    ERROR_LOG_DIAG_OFFSET_RECORD_TYPE = 5
    ERROR_LOG_DIAG_OFFSET_ERROR_STATUS = 16
    ERROR_LOG_DIAG_OFFSET_ERROR_LBA = 24
    ERROR_LOG_DIAG_OFFSET_PA_BANK = 38
    ERROR_LOG_DIAG_OFFSET_PA_DIE = 39
    ERROR_LOG_DIAG_OFFSET_PA_PAGE = 40
    ERROR_LOG_DIAG_OFFSET_PA_SECTOR = 42
    ERROR_LOG_DIAG_OFFSET_PA_BLOCK_INDEX = 43
    ERROR_LOG_DIAG_OFFSET_PA_PLANE = 44
    ERROR_LOG_DIAG_OFFSET_PA_CHIP = 45
    ERROR_LOG_DIAG_OFFSET_PA_BLOCK_LIST = 46

    if isROmode==True:
        ERROR_LOG_RECORD_LEN = 512
    else:
        ERROR_LOG_RECORD_LEN = 128

    opcode = 0x82
    commandName = "Read File50 error logs"
    logger = vtfContainer.GetLogger()
    errorLogDataBuf = pyWrap.Buffer.CreateBuffer(1, 0x00)
    #Get the number of sectors to be read from File50
    cdb = [0x82,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
    #card.SendDiagnostic(noOfSectors, cdb, 0, 1)
    buf=SendDiagnostic(vtfContainer, errorLogDataBuf, cdb, 0, 1, opcode, commandName)
    buf.PrintToLog()
    noOfSectors = errorLogDataBuf.GetOneByteToInt(0)
    errorLogDataBuf = pyWrap.Buffer.CreateBuffer(max(1,noOfSectors), 0x00)
    #Read File50 Sectors
    noOfRecs = 0
    if(noOfSectors > 0):
        cdb = [0x82,0x00,0x00,0x00,0x00,0x00,0x00,0x00,noOfSectors,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
        #card.SendDiagnostic(errorLogDataBuf, cdb, 0, noOfSectors)
        buf=SendDiagnostic(vtfContainer, errorLogDataBuf, cdb, 0, noOfSectors, opcode, commandName)
        buf.PrintToLog()
        errorLogRecords = []
        if isROmode==True:
            offset=0x100 #RPG-49436
        else:
            offset=0
        if isROmode!=True:
            noOfSectors= noOfSectors*4
        for log in range(0, (noOfSectors )):    # * 4)):
            errLog = []
            errType = errorLogDataBuf.GetOneByteToInt(offset)
            recordType = errorLogDataBuf.GetOneByteToInt(offset + ERROR_LOG_DIAG_OFFSET_RECORD_TYPE)
            signatureROMode1 = errorLogDataBuf.GetFourBytesToInt(offset + ERROR_LOG_DIAG_READ_ONLY_MODE_SIGNATURE)
            signatureROMode2 = errorLogDataBuf.GetFourBytesToInt(offset + ERROR_LOG_DIAG_READ_ONLY_MODE_SIGNATURE + 4)
            signatureROMode3 = errorLogDataBuf.GetFourBytesToInt(offset + ERROR_LOG_DIAG_READ_ONLY_MODE_SIGNATURE + 28)
            # LSB four bits represent record type - LLS / Counter
            recordType = recordType & 0xf
            errorStatus = errorLogDataBuf.GetTwoBytesToInt(offset + ERROR_LOG_DIAG_OFFSET_ERROR_STATUS)
            if(signatureROMode1 == 0xAAAAAAAA) and (signatureROMode2 == 0xBBBBBBBB) and (signatureROMode3 == 0xCCCCCCCC):
                line1 = errorLogDataBuf.GetFourBytesToInt(offset + ERROR_LOG_DIAG_READ_ONLY_MODE_SIGNATURE + 8)   # 12)
                line2 = errorLogDataBuf.GetFourBytesToInt(offset + ERROR_LOG_DIAG_READ_ONLY_MODE_SIGNATURE + 12)  # 16)
                if( not line1) and (not line2):
                    errLog.extend([0x3d092, 0, 0, 0, 0, 0, 0, 0])   #Status Read only mode value taken from Chorus File System Spec
                else:
                    continue
            elif(errorStatus == 0) or (recordType != 1):
                offset += ERROR_LOG_RECORD_LEN
                continue
            else:
                errorLba = errorLogDataBuf.GetFourBytesToInt(offset + ERROR_LOG_DIAG_OFFSET_ERROR_LBA)
                bank = errorLogDataBuf.GetOneByteToInt(offset + ERROR_LOG_DIAG_OFFSET_PA_BANK)
                die = errorLogDataBuf.GetOneByteToInt(offset + ERROR_LOG_DIAG_OFFSET_PA_DIE)
                page = errorLogDataBuf.GetTwoBytesToInt(offset + ERROR_LOG_DIAG_OFFSET_PA_PAGE)
                sector = errorLogDataBuf.GetOneByteToInt(offset + ERROR_LOG_DIAG_OFFSET_PA_SECTOR)
                blockIndex = errorLogDataBuf.GetOneByteToInt(offset + ERROR_LOG_DIAG_OFFSET_PA_BLOCK_INDEX)
                plane = errorLogDataBuf.GetOneByteToInt(offset + ERROR_LOG_DIAG_OFFSET_PA_PLANE)
                chip = errorLogDataBuf.GetOneByteToInt(offset + ERROR_LOG_DIAG_OFFSET_PA_CHIP)
                blockOffset = ERROR_LOG_DIAG_OFFSET_PA_BLOCK_LIST + (blockIndex * 2) # 2 bytes per block
                block = errorLogDataBuf.GetTwoBytesToInt(offset + blockOffset)

                errLog.extend([errorStatus, errorLba, bank, chip, die, plane, block, page])
            errorLogRecords.append(errLog)
            noOfRecs = noOfRecs + 1

            #increment the offset value
            offset = offset + ERROR_LOG_RECORD_LEN
        return noOfRecs, errorLogRecords
    else:
        return 0, None

def ReadAllCounterRecordsFromRAM(vtfContainer, elfGeneralInfo):
    """
    Name : ReadAllCounterRecords()

    Description : This function calls "Read Error Log Diagnostic(0x61)", provides all counter log entries.

    Arguments :
              vtfContainer - vtfContainer Object
              elfGeneralInfo - ELFGeneralInfo object

    Returns :
             elfLLSRecords - ELFGeneralInfo object

    opcode : 0x64

    subopcode : 0x2
    """
    #offsets
    ERROR_LOG_DIAG_COUNTERRECORDS_OFFSET_COUNTER_PF = 8
    ERROR_LOG_DIAG_COUNTERRECORDS_OFFSET_COUNTER_EF = 10
    ERROR_LOG_DIAG_COUNTERRECORDS_OFFSET_COUNTER_UECC = 18

    #constants
    ELF_ERROR_RECORD_LEN = 64

    commandName = "Read all counter Records"
    opcode = 0x64
    subOpcode = 4

    assert elfGeneralInfo.numCounterRecordsInRAM > 0 ,"Number of Counter records is [%d], it should be greater than zero"%(elfGeneralInfo.numCounterRecordsInRAM)
    assert elfGeneralInfo.numOfSectorsRequiedForCounterRecord > 0 ,"Length of Counter records is [%d], it should be greater than zero"%(elfGeneralInfo.numOfSectorsRequiedForCounterRecord)

    elfCounterRecords = [ValidationErrorLog.ELFCounterRecord()
                         for each in range(0, elfGeneralInfo.numCounterRecordsInRAM)]

    errorLogDataBuf = pyWrap.Buffer.CreateBuffer(elfGeneralInfo.numOfSectorsRequiedForCounterRecord,0x00)

    subOpcodeLsb = ByteUtil.LowByte(subOpcode)
    subOpcodeMsb = ByteUtil.HighByte(subOpcode)


    # Call Error Log Diag to featch general inforamtion of Error Log File
    cdb = [opcode, 0, subOpcodeLsb, subOpcodeMsb,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    errorLogDataBuf = SendDiagnostic(vtfContainer, errorLogDataBuf, cdb, READ_DATA, elfGeneralInfo.numOfSectorsRequiedForCounterRecord, opcode, commandName)

    offset = 0
    for index in range(0, elfGeneralInfo.numCounterRecords)  :

        elfCounterRecords[index].counterPF = errorLogDataBuf.GetTwoBytesToInt(offset+
                                                                              ERROR_LOG_DIAG_COUNTERRECORDS_OFFSET_COUNTER_PF)

        elfCounterRecords[index].counterEF = errorLogDataBuf.GetTwoBytesToInt(offset+
                                                                              ERROR_LOG_DIAG_COUNTERRECORDS_OFFSET_COUNTER_EF)

        elfCounterRecords[index].counterUECC = errorLogDataBuf.GetTwoBytesToInt(offset+
                                                                                ERROR_LOG_DIAG_COUNTERRECORDS_OFFSET_COUNTER_UECC)

        offset = offset + ELF_ERROR_RECORD_LEN


    return elfCounterRecords
#end of ReadAllCountersRecords


def ReadControlBlockAddresses(vtfContainer, returnBuffer=0):
    """
    Name : ReadControlBlockAddresses()

    Description : This function calls "Read firmware parameters(0x65)", provides all control block adresses

    Arguments :
              vtfContainer - vtfContainer Object
              returnBuffer - returns data buffer if this is '1'

    Returns :
             fWParametersData - f/w parameter buffer
             configParams - dictionary with control block adresses

    opcode = 0x65

    subOpcode = 0x1

    """
    import ValidationSpace
    validationSpace = ValidationSpace.ValidationSpace(vtfContainer)
    fwConfigObj = validationSpace.GetFWConfigData()

    if IsLargeMetablockUsed(vtfContainer)[0]:
        #Support for only 2MB's For each primary and secondary FS
        BOOT_BLOCK_ADDRESS1_OFFSET = 0
        BOOT_BLOCK_ADDRESS2_OFFSET = BOOT_BLOCK_ADDRESS1_OFFSET + 4                    #4
        BOOT_BLOCK_SIZE_OFFSET = BOOT_BLOCK_ADDRESS2_OFFSET + 4                        #8
        PRIMARY_FS_METABLOCK_ADDRESS1_OFFSET = BOOT_BLOCK_SIZE_OFFSET + 4                      #12
        PRIMARY_FS_METABLOCK_ADDRESS2_OFFSET = PRIMARY_FS_METABLOCK_ADDRESS1_OFFSET + 4  #16
        SECONDARY_FS_METABLOCK_ADDRESS1_OFFSET = PRIMARY_FS_METABLOCK_ADDRESS2_OFFSET + 4 #20
        SECONDARY_FS_METABLOCK_ADDRESS2_OFFSET = SECONDARY_FS_METABLOCK_ADDRESS1_OFFSET + 4 #24
        GAT_METABLOCK_NUMBER1_OFFSET = SECONDARY_FS_METABLOCK_ADDRESS2_OFFSET + 4           #28
    else:
        #offsets
        #Updated to get the offsets based on relative offset values.
        BOOT_BLOCK_ADDRESS1_OFFSET = 0
        BOOT_BLOCK_ADDRESS2_OFFSET = BOOT_BLOCK_ADDRESS1_OFFSET + 4                            #4
        BOOT_BLOCK_SIZE_OFFSET = BOOT_BLOCK_ADDRESS2_OFFSET + 4                        #8
        PRIMARY_FS_METABLOCK_ADDRESS1_OFFSET = BOOT_BLOCK_SIZE_OFFSET + 4                      #12
        PRIMARY_FS_METABLOCK_ADDRESS2_OFFSET = PRIMARY_FS_METABLOCK_ADDRESS1_OFFSET + 4     #16
        PRIMARY_FS_METABLOCK_ADDRESS3_OFFSET = PRIMARY_FS_METABLOCK_ADDRESS2_OFFSET + 4     #20
        PRIMARY_FS_METABLOCK_ADDRESS4_OFFSET = PRIMARY_FS_METABLOCK_ADDRESS3_OFFSET + 4     #24
        PRIMARY_FS_METABLOCK_ADDRESS5_OFFSET = PRIMARY_FS_METABLOCK_ADDRESS4_OFFSET + 4     #28
        PRIMARY_FS_METABLOCK_ADDRESS6_OFFSET = PRIMARY_FS_METABLOCK_ADDRESS5_OFFSET + 4     #32
        PRIMARY_FS_METABLOCK_ADDRESS7_OFFSET = PRIMARY_FS_METABLOCK_ADDRESS6_OFFSET + 4     #36
        PRIMARY_FS_METABLOCK_ADDRESS8_OFFSET = PRIMARY_FS_METABLOCK_ADDRESS7_OFFSET + 4     #40
        SECONDARY_FS_METABLOCK_ADDRESS1_OFFSET = PRIMARY_FS_METABLOCK_ADDRESS8_OFFSET + 4   #44
        SECONDARY_FS_METABLOCK_ADDRESS2_OFFSET = SECONDARY_FS_METABLOCK_ADDRESS1_OFFSET + 4       #48
        SECONDARY_FS_METABLOCK_ADDRESS3_OFFSET = SECONDARY_FS_METABLOCK_ADDRESS2_OFFSET + 4       #52
        SECONDARY_FS_METABLOCK_ADDRESS4_OFFSET = SECONDARY_FS_METABLOCK_ADDRESS3_OFFSET + 4       #56
        SECONDARY_FS_METABLOCK_ADDRESS5_OFFSET = SECONDARY_FS_METABLOCK_ADDRESS4_OFFSET + 4       #60
        SECONDARY_FS_METABLOCK_ADDRESS6_OFFSET = SECONDARY_FS_METABLOCK_ADDRESS5_OFFSET + 4       #64
        SECONDARY_FS_METABLOCK_ADDRESS7_OFFSET = SECONDARY_FS_METABLOCK_ADDRESS6_OFFSET + 4       #68
        SECONDARY_FS_METABLOCK_ADDRESS8_OFFSET = SECONDARY_FS_METABLOCK_ADDRESS7_OFFSET + 4       #72
        GAT_METABLOCK_NUMBER1_OFFSET  = SECONDARY_FS_METABLOCK_ADDRESS8_OFFSET + 4                #76

    GAT_METABLOCK_NUMBER2_OFFSET  = GAT_METABLOCK_NUMBER1_OFFSET + 4                      #80
    GAT_METABLOCK_NUMBER3_OFFSET  = GAT_METABLOCK_NUMBER2_OFFSET + 4                      #84
    GAT_METABLOCK_NUMBER4_OFFSET  = GAT_METABLOCK_NUMBER3_OFFSET + 4                      #88
    GAT_METABLOCK_NUMBER5_OFFSET  = GAT_METABLOCK_NUMBER4_OFFSET + 4                      #92
    GAT_METABLOCK_NUMBER6_OFFSET  = GAT_METABLOCK_NUMBER5_OFFSET + 4                      #96
    GAT_METABLOCK_NUMBER7_OFFSET  = GAT_METABLOCK_NUMBER6_OFFSET + 4                      #100
    GAT_METABLOCK_NUMBER8_OFFSET  = GAT_METABLOCK_NUMBER7_OFFSET + 4                      #104
    GAT_METABLOCK_NUMBER9_OFFSET  = GAT_METABLOCK_NUMBER8_OFFSET + 4                      #108
    GAT_METABLOCK_NUMBER10_OFFSET = GAT_METABLOCK_NUMBER9_OFFSET        + 4                       #112
    GAT_METABLOCK_NUMBER11_OFFSET = GAT_METABLOCK_NUMBER10_OFFSET + 4                     #116
    GAT_METABLOCK_NUMBER12_OFFSET = GAT_METABLOCK_NUMBER11_OFFSET + 4                     #120
    GAT_METABLOCK_NUMBER13_OFFSET = GAT_METABLOCK_NUMBER12_OFFSET + 4                     #124
    GAT_METABLOCK_NUMBER14_OFFSET = GAT_METABLOCK_NUMBER13_OFFSET + 4                     #128
    GAT_METABLOCK_NUMBER15_OFFSET = GAT_METABLOCK_NUMBER14_OFFSET + 4                     #132
    GAT_METABLOCK_NUMBER16_OFFSET = GAT_METABLOCK_NUMBER15_OFFSET + 4                     #136

    GAT_METABLOCK_NUMBER17_OFFSET = GAT_METABLOCK_NUMBER16_OFFSET + 4                     #140
    GAT_METABLOCK_NUMBER18_OFFSET = GAT_METABLOCK_NUMBER17_OFFSET + 4                     #144
    GAT_METABLOCK_NUMBER19_OFFSET = GAT_METABLOCK_NUMBER18_OFFSET + 4                     #148
    GAT_METABLOCK_NUMBER20_OFFSET = GAT_METABLOCK_NUMBER19_OFFSET + 4                     #152
    GAT_METABLOCK_NUMBER21_OFFSET = GAT_METABLOCK_NUMBER20_OFFSET + 4                     #156
    GAT_METABLOCK_NUMBER22_OFFSET = GAT_METABLOCK_NUMBER21_OFFSET + 4                     #160
    GAT_METABLOCK_NUMBER23_OFFSET = GAT_METABLOCK_NUMBER22_OFFSET + 4                     #164
    GAT_METABLOCK_NUMBER24_OFFSET = GAT_METABLOCK_NUMBER23_OFFSET + 4                     #168
    GAT_METABLOCK_NUMBER25_OFFSET = GAT_METABLOCK_NUMBER24_OFFSET + 4                     #172
    GAT_METABLOCK_NUMBER26_OFFSET = GAT_METABLOCK_NUMBER25_OFFSET + 4                     #176
    GAT_METABLOCK_NUMBER27_OFFSET = GAT_METABLOCK_NUMBER26_OFFSET + 4                     #180
    GAT_METABLOCK_NUMBER28_OFFSET = GAT_METABLOCK_NUMBER27_OFFSET + 4                     #184
    GAT_METABLOCK_NUMBER29_OFFSET = GAT_METABLOCK_NUMBER28_OFFSET + 4                     #188
    GAT_METABLOCK_NUMBER30_OFFSET = GAT_METABLOCK_NUMBER29_OFFSET + 4                     #192
    GAT_METABLOCK_NUMBER31_OFFSET = GAT_METABLOCK_NUMBER30_OFFSET + 4                     #196
    GAT_METABLOCK_NUMBER32_OFFSET = GAT_METABLOCK_NUMBER31_OFFSET + 4                     #200

    GAT_METABLOCK_NUMBER33_OFFSET = GAT_METABLOCK_NUMBER32_OFFSET + 4                     #204
    GAT_METABLOCK_NUMBER34_OFFSET = GAT_METABLOCK_NUMBER33_OFFSET + 4                     #208
    GAT_METABLOCK_NUMBER35_OFFSET = GAT_METABLOCK_NUMBER34_OFFSET + 4                     #212
    GAT_METABLOCK_NUMBER36_OFFSET = GAT_METABLOCK_NUMBER35_OFFSET + 4                     #216
    GAT_METABLOCK_NUMBER37_OFFSET = GAT_METABLOCK_NUMBER36_OFFSET + 4                     #220
    GAT_METABLOCK_NUMBER38_OFFSET = GAT_METABLOCK_NUMBER37_OFFSET + 4                     #224
    GAT_METABLOCK_NUMBER39_OFFSET = GAT_METABLOCK_NUMBER38_OFFSET + 4                     #228
    GAT_METABLOCK_NUMBER40_OFFSET = GAT_METABLOCK_NUMBER39_OFFSET + 4                     #232
    GAT_METABLOCK_NUMBER41_OFFSET = GAT_METABLOCK_NUMBER40_OFFSET + 4                     #236
    GAT_METABLOCK_NUMBER42_OFFSET = GAT_METABLOCK_NUMBER41_OFFSET + 4                     #240
    GAT_METABLOCK_NUMBER43_OFFSET = GAT_METABLOCK_NUMBER42_OFFSET + 4                     #244
    GAT_METABLOCK_NUMBER44_OFFSET = GAT_METABLOCK_NUMBER43_OFFSET + 4                     #248
    GAT_METABLOCK_NUMBER45_OFFSET = GAT_METABLOCK_NUMBER44_OFFSET + 4                     #252
    GAT_METABLOCK_NUMBER46_OFFSET = GAT_METABLOCK_NUMBER45_OFFSET + 4                     #256
    GAT_METABLOCK_NUMBER47_OFFSET = GAT_METABLOCK_NUMBER46_OFFSET + 4                     #260
    GAT_METABLOCK_NUMBER48_OFFSET = GAT_METABLOCK_NUMBER47_OFFSET + 4                     #264

    GAT_METABLOCK_NUMBER49_OFFSET = GAT_METABLOCK_NUMBER48_OFFSET + 4                     #268
    GAT_METABLOCK_NUMBER50_OFFSET = GAT_METABLOCK_NUMBER49_OFFSET + 4                     #272
    GAT_METABLOCK_NUMBER51_OFFSET = GAT_METABLOCK_NUMBER50_OFFSET + 4                     #276
    GAT_METABLOCK_NUMBER52_OFFSET = GAT_METABLOCK_NUMBER51_OFFSET + 4                     #280
    GAT_METABLOCK_NUMBER53_OFFSET = GAT_METABLOCK_NUMBER52_OFFSET + 4                     #284
    GAT_METABLOCK_NUMBER54_OFFSET = GAT_METABLOCK_NUMBER53_OFFSET + 4                     #288
    GAT_METABLOCK_NUMBER55_OFFSET = GAT_METABLOCK_NUMBER54_OFFSET + 4                     #292
    GAT_METABLOCK_NUMBER56_OFFSET = GAT_METABLOCK_NUMBER55_OFFSET + 4                     #296
    GAT_METABLOCK_NUMBER57_OFFSET = GAT_METABLOCK_NUMBER56_OFFSET + 4                     #300
    GAT_METABLOCK_NUMBER58_OFFSET = GAT_METABLOCK_NUMBER57_OFFSET + 4                     #304
    GAT_METABLOCK_NUMBER59_OFFSET = GAT_METABLOCK_NUMBER58_OFFSET + 4                     #308
    GAT_METABLOCK_NUMBER60_OFFSET = GAT_METABLOCK_NUMBER59_OFFSET + 4                     #312
    GAT_METABLOCK_NUMBER61_OFFSET = GAT_METABLOCK_NUMBER60_OFFSET + 4                     #316
    GAT_METABLOCK_NUMBER62_OFFSET = GAT_METABLOCK_NUMBER61_OFFSET + 4                     #320
    GAT_METABLOCK_NUMBER63_OFFSET = GAT_METABLOCK_NUMBER62_OFFSET + 4                     #324
    GAT_METABLOCK_NUMBER64_OFFSET = GAT_METABLOCK_NUMBER63_OFFSET + 4                     #328

    GAT_METABLOCK_NUMBER65_OFFSET  = GAT_METABLOCK_NUMBER64_OFFSET + 4                    #76
    GAT_METABLOCK_NUMBER66_OFFSET  = GAT_METABLOCK_NUMBER65_OFFSET + 4                    #80
    GAT_METABLOCK_NUMBER67_OFFSET  = GAT_METABLOCK_NUMBER66_OFFSET + 4                    #84
    GAT_METABLOCK_NUMBER68_OFFSET  = GAT_METABLOCK_NUMBER67_OFFSET + 4                    #88
    GAT_METABLOCK_NUMBER69_OFFSET  = GAT_METABLOCK_NUMBER68_OFFSET + 4                    #92
    GAT_METABLOCK_NUMBER70_OFFSET  = GAT_METABLOCK_NUMBER69_OFFSET + 4                    #96
    GAT_METABLOCK_NUMBER71_OFFSET  = GAT_METABLOCK_NUMBER70_OFFSET + 4                    #100
    GAT_METABLOCK_NUMBER72_OFFSET  = GAT_METABLOCK_NUMBER71_OFFSET + 4                    #104
    GAT_METABLOCK_NUMBER73_OFFSET  = GAT_METABLOCK_NUMBER72_OFFSET + 4                    #108
    GAT_METABLOCK_NUMBER74_OFFSET = GAT_METABLOCK_NUMBER73_OFFSET  + 4                    #112
    GAT_METABLOCK_NUMBER75_OFFSET = GAT_METABLOCK_NUMBER74_OFFSET + 4                     #116
    GAT_METABLOCK_NUMBER76_OFFSET = GAT_METABLOCK_NUMBER75_OFFSET + 4                     #120
    GAT_METABLOCK_NUMBER77_OFFSET = GAT_METABLOCK_NUMBER76_OFFSET + 4                     #124
    GAT_METABLOCK_NUMBER78_OFFSET = GAT_METABLOCK_NUMBER77_OFFSET + 4                     #128
    GAT_METABLOCK_NUMBER79_OFFSET = GAT_METABLOCK_NUMBER78_OFFSET + 4                     #132
    GAT_METABLOCK_NUMBER80_OFFSET = GAT_METABLOCK_NUMBER79_OFFSET + 4                     #136

    GAT_METABLOCK_NUMBER81_OFFSET = GAT_METABLOCK_NUMBER80_OFFSET + 4                     #140
    GAT_METABLOCK_NUMBER82_OFFSET = GAT_METABLOCK_NUMBER81_OFFSET + 4                     #144
    GAT_METABLOCK_NUMBER83_OFFSET = GAT_METABLOCK_NUMBER82_OFFSET + 4                     #148
    GAT_METABLOCK_NUMBER84_OFFSET = GAT_METABLOCK_NUMBER83_OFFSET + 4                     #152
    GAT_METABLOCK_NUMBER85_OFFSET = GAT_METABLOCK_NUMBER84_OFFSET + 4                     #156
    GAT_METABLOCK_NUMBER86_OFFSET = GAT_METABLOCK_NUMBER85_OFFSET + 4                     #160
    GAT_METABLOCK_NUMBER87_OFFSET = GAT_METABLOCK_NUMBER86_OFFSET + 4                     #164
    GAT_METABLOCK_NUMBER88_OFFSET = GAT_METABLOCK_NUMBER87_OFFSET + 4                     #168
    GAT_METABLOCK_NUMBER89_OFFSET = GAT_METABLOCK_NUMBER88_OFFSET + 4                     #172
    GAT_METABLOCK_NUMBER90_OFFSET = GAT_METABLOCK_NUMBER89_OFFSET + 4                     #176
    GAT_METABLOCK_NUMBER91_OFFSET = GAT_METABLOCK_NUMBER90_OFFSET + 4                     #180
    GAT_METABLOCK_NUMBER92_OFFSET = GAT_METABLOCK_NUMBER91_OFFSET + 4                     #184
    GAT_METABLOCK_NUMBER93_OFFSET = GAT_METABLOCK_NUMBER92_OFFSET + 4                     #188
    GAT_METABLOCK_NUMBER94_OFFSET = GAT_METABLOCK_NUMBER93_OFFSET + 4                     #192
    GAT_METABLOCK_NUMBER95_OFFSET = GAT_METABLOCK_NUMBER94_OFFSET + 4                     #196
    GAT_METABLOCK_NUMBER96_OFFSET = GAT_METABLOCK_NUMBER95_OFFSET + 4                     #200

    GAT_METABLOCK_NUMBER97_OFFSET = GAT_METABLOCK_NUMBER96_OFFSET + 4                     #204
    GAT_METABLOCK_NUMBER98_OFFSET = GAT_METABLOCK_NUMBER97_OFFSET + 4                     #208
    GAT_METABLOCK_NUMBER99_OFFSET = GAT_METABLOCK_NUMBER98_OFFSET + 4                     #212
    GAT_METABLOCK_NUMBER100_OFFSET = GAT_METABLOCK_NUMBER99_OFFSET + 4                    #216
    GAT_METABLOCK_NUMBER101_OFFSET = GAT_METABLOCK_NUMBER100_OFFSET + 4                   #220
    GAT_METABLOCK_NUMBER102_OFFSET = GAT_METABLOCK_NUMBER101_OFFSET + 4                   #224
    GAT_METABLOCK_NUMBER103_OFFSET = GAT_METABLOCK_NUMBER102_OFFSET + 4                   #228
    GAT_METABLOCK_NUMBER104_OFFSET = GAT_METABLOCK_NUMBER103_OFFSET + 4                   #232
    GAT_METABLOCK_NUMBER105_OFFSET = GAT_METABLOCK_NUMBER104_OFFSET + 4                   #236
    GAT_METABLOCK_NUMBER106_OFFSET = GAT_METABLOCK_NUMBER105_OFFSET + 4                   #240
    GAT_METABLOCK_NUMBER107_OFFSET = GAT_METABLOCK_NUMBER106_OFFSET + 4                   #244
    GAT_METABLOCK_NUMBER108_OFFSET = GAT_METABLOCK_NUMBER107_OFFSET + 4                   #248
    GAT_METABLOCK_NUMBER109_OFFSET = GAT_METABLOCK_NUMBER108_OFFSET + 4                   #252
    GAT_METABLOCK_NUMBER110_OFFSET = GAT_METABLOCK_NUMBER109_OFFSET + 4                   #256
    GAT_METABLOCK_NUMBER111_OFFSET = GAT_METABLOCK_NUMBER110_OFFSET + 4                   #260
    GAT_METABLOCK_NUMBER112_OFFSET = GAT_METABLOCK_NUMBER111_OFFSET + 4                   #264

    GAT_METABLOCK_NUMBER113_OFFSET = GAT_METABLOCK_NUMBER112_OFFSET + 4                   #268
    GAT_METABLOCK_NUMBER114_OFFSET = GAT_METABLOCK_NUMBER113_OFFSET + 4                   #272
    GAT_METABLOCK_NUMBER115_OFFSET = GAT_METABLOCK_NUMBER114_OFFSET + 4                   #276
    GAT_METABLOCK_NUMBER116_OFFSET = GAT_METABLOCK_NUMBER115_OFFSET + 4                   #280
    GAT_METABLOCK_NUMBER117_OFFSET = GAT_METABLOCK_NUMBER116_OFFSET + 4                   #284
    GAT_METABLOCK_NUMBER118_OFFSET = GAT_METABLOCK_NUMBER117_OFFSET + 4                   #288
    GAT_METABLOCK_NUMBER119_OFFSET = GAT_METABLOCK_NUMBER118_OFFSET + 4                   #292
    GAT_METABLOCK_NUMBER120_OFFSET = GAT_METABLOCK_NUMBER119_OFFSET + 4                   #296
    GAT_METABLOCK_NUMBER121_OFFSET = GAT_METABLOCK_NUMBER120_OFFSET + 4                   #300
    GAT_METABLOCK_NUMBER122_OFFSET = GAT_METABLOCK_NUMBER121_OFFSET + 4                   #304
    GAT_METABLOCK_NUMBER123_OFFSET = GAT_METABLOCK_NUMBER122_OFFSET + 4                   #308
    GAT_METABLOCK_NUMBER124_OFFSET = GAT_METABLOCK_NUMBER123_OFFSET + 4                   #312
    GAT_METABLOCK_NUMBER125_OFFSET = GAT_METABLOCK_NUMBER124_OFFSET + 4                   #316
    GAT_METABLOCK_NUMBER126_OFFSET = GAT_METABLOCK_NUMBER125_OFFSET + 4                   #320
    GAT_METABLOCK_NUMBER127_OFFSET = GAT_METABLOCK_NUMBER126_OFFSET + 4                   #324
    GAT_METABLOCK_NUMBER128_OFFSET = GAT_METABLOCK_NUMBER127_OFFSET + 4                   #328

    ACTIVE_GAT_METABLOCK_NUM_OFFSET = GAT_METABLOCK_NUMBER128_OFFSET + 4                  #540
    LATEST_PRIMARY_FSBS_ADDR_OFFSET = 1952                                                #1952
    LATEST_SECONDARY_FSBS_ADDR_OFFSET = 1956                                              #1956
    ACTIVE_MIP_ADDRESSING_GAT_OFFSET = 572

    commandName = "Read FirmWare Parameters"
    #opcode = 0xBA
    opcode = 0x65
    subOpcode = 0x01

    cdb = [ opcode, 0, subOpcode, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
           0, 0, 0, 0
           ]

    fWParametersData = pyWrap.Buffer.CreateBuffer(FOUR_SECTORS)

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: 0x%X, Data Direction: %s" %(opcode, subOpcode, READ_DATA))

    # Sending diagnostic command
    fWParametersData = SendDiagnostic(vtfContainer, fWParametersData, cdb, READ_DATA, TWO_SECTORS, opcode, commandName)
    if returnBuffer:
        return fWParametersData

    configParams = { "bootBlockAddr1":None, "bootBlockAddr2":None, "bootBlockSize":None, "priFsMetaBlockAddr1":None,
                     "secFsMetaBlockAddr1":None, "GatMetaBlockNum1":None, "GatMetaBlockNum2":None, "GatMetaBlockNum3":None,
                     "GatMetaBlockNum4":None , "GatMetaBlockNum5":None, "GatMetaBlockNum6":None, "GatMetaBlockNum7":None,
                    "GatMetaBlockNum8":None, "GatMetaBlockNum9":None, "GatMetaBlockNum10":None, "GatMetaBlockNum11":None,
                    "GatMetaBlockNum12":None, "GatMetaBlockNum13":None, "GatMetaBlockNum14":None, "GatMetaBlockNum15":None,

                    "GatMetaBlockNum16":None, "GatMetaBlockNum17":None , "GatMetaBlockNum18":None, "GatMetaBlockNum19":None,
                    "GatMetaBlockNum20":None, "GatMetaBlockNum21":None , "GatMetaBlockNum22":None, "GatMetaBlockNum23":None,
                    "GatMetaBlockNum24":None, "GatMetaBlockNum25":None , "GatMetaBlockNum26":None, "GatMetaBlockNum27":None,
                    "GatMetaBlockNum28":None, "GatMetaBlockNum29":None , "GatMetaBlockNum30":None, "GatMetaBlockNum31":None,
                    "GatMetaBlockNum32":None, "GatMetaBlockNum33":None , "GatMetaBlockNum34":None, "GatMetaBlockNum35":None,
                    "GatMetaBlockNum36":None, "GatMetaBlockNum37":None , "GatMetaBlockNum38":None, "GatMetaBlockNum39":None,
                    "GatMetaBlockNum40":None, "GatMetaBlockNum41":None , "GatMetaBlockNum42":None, "GatMetaBlockNum43":None,
                    "GatMetaBlockNum44":None, "GatMetaBlockNum45":None , "GatMetaBlockNum46":None, "GatMetaBlockNum47":None,

                    "GatMetaBlockNum48":None, "GatMetaBlockNum49":None , "GatMetaBlockNum50":None, "GatMetaBlockNum51":None,
                    "GatMetaBlockNum52":None, "GatMetaBlockNum53":None , "GatMetaBlockNum54":None, "GatMetaBlockNum55":None,
                    "GatMetaBlockNum56":None, "GatMetaBlockNum57":None , "GatMetaBlockNum58":None, "GatMetaBlockNum59":None,
                    "GatMetaBlockNum60":None, "GatMetaBlockNum61":None , "GatMetaBlockNum62":None, "GatMetaBlockNum63":None,
                    "GatMetaBlockNum64":None,

                    "GatMetaBlockNum65":None,   "GatMetaBlockNum66":None,   "GatMetaBlockNum67":None,  "GatMetaBlockNum68":None,
                    "GatMetaBlockNum69":None,   "GatMetaBlockNum70":None,   "GatMetaBlockNum71":None,  "GatMetaBlockNum72":None,
                    "GatMetaBlockNum73":None,   "GatMetaBlockNum74":None,   "GatMetaBlockNum75":None,  "GatMetaBlockNum76":None,
                    "GatMetaBlockNum77":None,   "GatMetaBlockNum78":None,   "GatMetaBlockNum79":None,  "GatMetaBlockNum80":None,
                    "GatMetaBlockNum81":None,   "GatMetaBlockNum82":None,   "GatMetaBlockNum83":None,  "GatMetaBlockNum84":None,
                    "GatMetaBlockNum85":None,   "GatMetaBlockNum86":None,   "GatMetaBlockNum87":None,  "GatMetaBlockNum88":None,
                    "GatMetaBlockNum89":None,   "GatMetaBlockNum90":None,   "GatMetaBlockNum91":None,  "GatMetaBlockNum92":None,
                    "GatMetaBlockNum93":None,   "GatMetaBlockNum94":None,   "GatMetaBlockNum95":None,  "GatMetaBlockNum96":None,
                    "GatMetaBlockNum97":None,   "GatMetaBlockNum98":None,   "GatMetaBlockNum99":None,  "GatMetaBlockNum100":None,
                    "GatMetaBlockNum101":None,  "GatMetaBlockNum102":None,  "GatMetaBlockNum103":None, "GatMetaBlockNum104":None,
                    "GatMetaBlockNum105":None,  "GatMetaBlockNum106":None,  "GatMetaBlockNum107":None, "GatMetaBlockNum108":None,
                    "GatMetaBlockNum109":None,  "GatMetaBlockNum110":None,  "GatMetaBlockNum111":None, "GatMetaBlockNum112":None,
                    "GatMetaBlockNum113":None,  "GatMetaBlockNum114":None,  "GatMetaBlockNum115":None, "GatMetaBlockNum116":None,
                    "GatMetaBlockNum117":None,  "GatMetaBlockNum118":None,  "GatMetaBlockNum119":None, "GatMetaBlockNum120":None,
                    "GatMetaBlockNum121":None,  "GatMetaBlockNum122":None,  "GatMetaBlockNum123":None, "GatMetaBlockNum124":None,
                    "GatMetaBlockNum125":None,  "GatMetaBlockNum126":None,  "GatMetaBlockNum127":None, "GatMetaBlockNum128":None
                    }

    configParams["bootBlockAddr1"] = fWParametersData.GetFourBytesToInt(BOOT_BLOCK_ADDRESS1_OFFSET)
    configParams["bootBlockAddr2"] = fWParametersData.GetFourBytesToInt(BOOT_BLOCK_ADDRESS2_OFFSET)
    configParams["bootBlockSize"] = fWParametersData.GetFourBytesToInt(BOOT_BLOCK_SIZE_OFFSET)
    configParams["priFsMetaBlockAddr1"] = fWParametersData.GetFourBytesToInt(PRIMARY_FS_METABLOCK_ADDRESS1_OFFSET)
    configParams["priFsMetaBlockAddr2"] = fWParametersData.GetFourBytesToInt(PRIMARY_FS_METABLOCK_ADDRESS2_OFFSET)
    if not IsLargeMetablockUsed(vtfContainer)[0]:
        configParams["priFsMetaBlockAddr3"] = fWParametersData.GetFourBytesToInt(PRIMARY_FS_METABLOCK_ADDRESS3_OFFSET)
        configParams["priFsMetaBlockAddr4"] = fWParametersData.GetFourBytesToInt(PRIMARY_FS_METABLOCK_ADDRESS4_OFFSET)
        configParams["priFsMetaBlockAddr5"] = fWParametersData.GetFourBytesToInt(PRIMARY_FS_METABLOCK_ADDRESS5_OFFSET)
        configParams["priFsMetaBlockAddr6"] = fWParametersData.GetFourBytesToInt(PRIMARY_FS_METABLOCK_ADDRESS6_OFFSET)
        configParams["priFsMetaBlockAddr7"] = fWParametersData.GetFourBytesToInt(PRIMARY_FS_METABLOCK_ADDRESS7_OFFSET)
        configParams["priFsMetaBlockAddr8"] = fWParametersData.GetFourBytesToInt(PRIMARY_FS_METABLOCK_ADDRESS8_OFFSET)

    configParams["secFsMetaBlockAddr1"] = fWParametersData.GetFourBytesToInt(SECONDARY_FS_METABLOCK_ADDRESS1_OFFSET)
    configParams["secFsMetaBlockAddr2"] = fWParametersData.GetFourBytesToInt(SECONDARY_FS_METABLOCK_ADDRESS2_OFFSET)

    if not IsLargeMetablockUsed(vtfContainer)[0]:
        configParams["secFsMetaBlockAddr3"] = fWParametersData.GetFourBytesToInt(SECONDARY_FS_METABLOCK_ADDRESS3_OFFSET)
        configParams["secFsMetaBlockAddr4"] = fWParametersData.GetFourBytesToInt(SECONDARY_FS_METABLOCK_ADDRESS4_OFFSET)
        configParams["secFsMetaBlockAddr5"] = fWParametersData.GetFourBytesToInt(SECONDARY_FS_METABLOCK_ADDRESS5_OFFSET)
        configParams["secFsMetaBlockAddr6"] = fWParametersData.GetFourBytesToInt(SECONDARY_FS_METABLOCK_ADDRESS6_OFFSET)
        configParams["secFsMetaBlockAddr7"] = fWParametersData.GetFourBytesToInt(SECONDARY_FS_METABLOCK_ADDRESS7_OFFSET)
        configParams["secFsMetaBlockAddr8"] = fWParametersData.GetFourBytesToInt(SECONDARY_FS_METABLOCK_ADDRESS8_OFFSET)

    configParams["gatMetaBlockNum1"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER1_OFFSET)
    configParams["gatMetaBlockNum2"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER2_OFFSET)
    configParams["gatMetaBlockNum3"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER3_OFFSET)
    configParams["gatMetaBlockNum4"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER4_OFFSET)
    configParams["gatMetaBlockNum5"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER5_OFFSET)
    configParams["gatMetaBlockNum6"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER6_OFFSET)
    configParams["gatMetaBlockNum7"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER7_OFFSET)
    configParams["gatMetaBlockNum8"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER8_OFFSET)
    configParams["gatMetaBlockNum9"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER9_OFFSET)
    configParams["gatMetaBlockNum10"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER10_OFFSET)
    configParams["gatMetaBlockNum11"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER11_OFFSET)
    configParams["gatMetaBlockNum12"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER12_OFFSET)
    configParams["gatMetaBlockNum13"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER13_OFFSET)
    configParams["gatMetaBlockNum14"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER14_OFFSET)
    configParams["gatMetaBlockNum15"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER15_OFFSET)
    configParams["gatMetaBlockNum16"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER16_OFFSET)

    #if fwConfigObj.numberOfMetaPlane == 2 or fwConfigObj.numberOfMetaPlane == 4:
    configParams["gatMetaBlockNum17"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER17_OFFSET)
    configParams["gatMetaBlockNum18"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER18_OFFSET)
    configParams["gatMetaBlockNum19"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER19_OFFSET)
    configParams["gatMetaBlockNum20"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER20_OFFSET)
    configParams["gatMetaBlockNum21"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER21_OFFSET)
    configParams["gatMetaBlockNum22"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER22_OFFSET)
    configParams["gatMetaBlockNum23"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER23_OFFSET)
    configParams["gatMetaBlockNum24"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER24_OFFSET)
    configParams["gatMetaBlockNum25"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER25_OFFSET)
    configParams["gatMetaBlockNum26"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER26_OFFSET)
    configParams["gatMetaBlockNum27"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER27_OFFSET)
    configParams["gatMetaBlockNum28"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER28_OFFSET)
    configParams["gatMetaBlockNum29"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER29_OFFSET)
    configParams["gatMetaBlockNum30"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER30_OFFSET)
    configParams["gatMetaBlockNum31"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER31_OFFSET)
    configParams["gatMetaBlockNum32"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER32_OFFSET)

    #if fwConfigObj.numberOfMetaPlane == 4:
    configParams["gatMetaBlockNum33"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER33_OFFSET)
    configParams["gatMetaBlockNum34"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER34_OFFSET)
    configParams["gatMetaBlockNum35"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER35_OFFSET)
    configParams["gatMetaBlockNum36"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER36_OFFSET)
    configParams["gatMetaBlockNum37"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER37_OFFSET)
    configParams["gatMetaBlockNum38"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER38_OFFSET)
    configParams["gatMetaBlockNum39"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER39_OFFSET)
    configParams["gatMetaBlockNum40"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER40_OFFSET)
    configParams["gatMetaBlockNum41"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER41_OFFSET)
    configParams["gatMetaBlockNum42"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER42_OFFSET)
    configParams["gatMetaBlockNum43"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER43_OFFSET)
    configParams["gatMetaBlockNum44"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER44_OFFSET)
    configParams["gatMetaBlockNum45"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER45_OFFSET)
    configParams["gatMetaBlockNum46"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER46_OFFSET)
    configParams["gatMetaBlockNum47"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER47_OFFSET)
    configParams["gatMetaBlockNum48"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER48_OFFSET)

    configParams["gatMetaBlockNum49"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER49_OFFSET)
    configParams["gatMetaBlockNum50"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER50_OFFSET)
    configParams["gatMetaBlockNum51"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER51_OFFSET)
    configParams["gatMetaBlockNum52"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER52_OFFSET)
    configParams["gatMetaBlockNum53"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER53_OFFSET)
    configParams["gatMetaBlockNum54"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER54_OFFSET)
    configParams["gatMetaBlockNum55"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER55_OFFSET)
    configParams["gatMetaBlockNum56"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER56_OFFSET)
    configParams["gatMetaBlockNum57"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER57_OFFSET)
    configParams["gatMetaBlockNum58"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER58_OFFSET)
    configParams["gatMetaBlockNum59"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER59_OFFSET)
    configParams["gatMetaBlockNum60"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER60_OFFSET)
    configParams["gatMetaBlockNum61"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER61_OFFSET)
    configParams["gatMetaBlockNum62"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER62_OFFSET)
    configParams["gatMetaBlockNum63"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER63_OFFSET)
    configParams["gatMetaBlockNum64"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER64_OFFSET)

    configParams["gatMetaBlockNum65"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER65_OFFSET)
    configParams["gatMetaBlockNum66"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER66_OFFSET)
    configParams["gatMetaBlockNum67"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER67_OFFSET)
    configParams["gatMetaBlockNum68"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER68_OFFSET)
    configParams["gatMetaBlockNum69"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER69_OFFSET)
    configParams["gatMetaBlockNum70"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER70_OFFSET)
    configParams["gatMetaBlockNum71"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER71_OFFSET)
    configParams["gatMetaBlockNum72"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER72_OFFSET)
    configParams["gatMetaBlockNum73"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER73_OFFSET)
    configParams["gatMetaBlockNum74"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER74_OFFSET)
    configParams["gatMetaBlockNum75"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER75_OFFSET)
    configParams["gatMetaBlockNum76"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER76_OFFSET)
    configParams["gatMetaBlockNum77"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER77_OFFSET)
    configParams["gatMetaBlockNum78"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER78_OFFSET)
    configParams["gatMetaBlockNum79"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER79_OFFSET)
    configParams["gatMetaBlockNum80"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER80_OFFSET)

    configParams["gatMetaBlockNum81"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER81_OFFSET)
    configParams["gatMetaBlockNum82"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER82_OFFSET)
    configParams["gatMetaBlockNum83"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER83_OFFSET)
    configParams["gatMetaBlockNum84"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER84_OFFSET)
    configParams["gatMetaBlockNum85"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER85_OFFSET)
    configParams["gatMetaBlockNum86"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER86_OFFSET)
    configParams["gatMetaBlockNum87"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER87_OFFSET)
    configParams["gatMetaBlockNum88"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER88_OFFSET)
    configParams["gatMetaBlockNum89"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER89_OFFSET)
    configParams["gatMetaBlockNum90"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER90_OFFSET)
    configParams["gatMetaBlockNum91"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER91_OFFSET)
    configParams["gatMetaBlockNum92"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER92_OFFSET)
    configParams["gatMetaBlockNum93"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER93_OFFSET)
    configParams["gatMetaBlockNum94"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER94_OFFSET)
    configParams["gatMetaBlockNum95"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER95_OFFSET)
    configParams["gatMetaBlockNum96"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER96_OFFSET)

    #if fwConfigObj.numberOfMetaPlane == 4:
    configParams["gatMetaBlockNum97"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER97_OFFSET)
    configParams["gatMetaBlockNum98"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER98_OFFSET)
    configParams["gatMetaBlockNum99"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER99_OFFSET)
    configParams["gatMetaBlockNum100"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER100_OFFSET)
    configParams["gatMetaBlockNum101"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER101_OFFSET)
    configParams["gatMetaBlockNum102"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER102_OFFSET)
    configParams["gatMetaBlockNum103"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER103_OFFSET)
    configParams["gatMetaBlockNum104"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER104_OFFSET)
    configParams["gatMetaBlockNum105"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER105_OFFSET)
    configParams["gatMetaBlockNum106"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER106_OFFSET)
    configParams["gatMetaBlockNum107"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER107_OFFSET)
    configParams["gatMetaBlockNum108"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER108_OFFSET)
    configParams["gatMetaBlockNum109"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER109_OFFSET)
    configParams["gatMetaBlockNum110"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER110_OFFSET)
    configParams["gatMetaBlockNum111"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER111_OFFSET)
    configParams["gatMetaBlockNum112"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER122_OFFSET)

    configParams["gatMetaBlockNum113"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER113_OFFSET)
    configParams["gatMetaBlockNum114"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER114_OFFSET)
    configParams["gatMetaBlockNum115"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER115_OFFSET)
    configParams["gatMetaBlockNum116"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER116_OFFSET)
    configParams["gatMetaBlockNum117"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER117_OFFSET)
    configParams["gatMetaBlockNum118"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER118_OFFSET)
    configParams["gatMetaBlockNum119"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER119_OFFSET)
    configParams["gatMetaBlockNum120"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER120_OFFSET)
    configParams["gatMetaBlockNum121"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER121_OFFSET)
    configParams["gatMetaBlockNum122"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER122_OFFSET)
    configParams["gatMetaBlockNum123"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER123_OFFSET)
    configParams["gatMetaBlockNum124"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER124_OFFSET)
    configParams["gatMetaBlockNum125"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER125_OFFSET)
    configParams["gatMetaBlockNum126"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER126_OFFSET)
    configParams["gatMetaBlockNum127"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER127_OFFSET)
    configParams["gatMetaBlockNum128"] = fWParametersData.GetFourBytesToInt(GAT_METABLOCK_NUMBER128_OFFSET)

    configParams["latestPriFSBSAddr"] = fWParametersData.GetFourBytesToInt(LATEST_PRIMARY_FSBS_ADDR_OFFSET)
    configParams["latestSecFSBSAddr"] = fWParametersData.GetFourBytesToInt(LATEST_SECONDARY_FSBS_ADDR_OFFSET)
    configParams["activeGatMetaBlockNumber"] = fWParametersData.GetFourBytesToInt(ACTIVE_GAT_METABLOCK_NUM_OFFSET)
    configParams["activeMipAddressingGat"] = fWParametersData.GetFourBytesToInt(ACTIVE_MIP_ADDRESSING_GAT_OFFSET)

    return configParams
# end of ReadControlBlockAddresses

#----------------------------------------------------------------------
def GetDFDblocks(vtfContainer):
    """
    Description:
         Get DFD Blocks
    """
    commandName="GetDFDBlocks"
    opcode=0x65
    subOpcode=0xc
    cdb = [ opcode, 0, subOpcode, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
           0, 0, 0, 0
              ]
    DFDBlocksBuffer= pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: 0x%X, Data Direction: %s" %(opcode, subOpcode, READ_DATA))
    DFDBlocksInfo = SendDiagnostic(vtfContainer, DFDBlocksBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    DFDBlock1=DFDBlocksInfo.GetTwoBytesToInt(0x0)
    DFDBlock2=DFDBlocksInfo.GetTwoBytesToInt(0x2)
    return(DFDBlock1,DFDBlock2)

def GetFreeMLCBlockCount(vtfContainer):
    """
    GET_FREE_BLOCK_COUNT_OPCODE = 0xC9
    GET_FREE_BLOCK_COUNT_SUBOPCODE = 59
    NUM_BLOCK_TYPES = 0                              #0
    FREE_SLC_BLOCK_COUNT = NUM_BLOCK_TYPES + 2       #1
    FREE_MLC_BLOCK_COUNT = FREE_SLC_BLOCK_COUNT + 2  #3

    commandName = "Get Free Block Count"

    opcode = GET_FREE_BLOCK_COUNT_OPCODE
    subOpcode = GET_FREE_BLOCK_COUNT_SUBOPCODE

    cdb = [ opcode, subOpcode, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
    ]

    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    configParams = {"numOfBlockTypes":None, "freeSlcBlockCount":None, "freeMlcBlockCount":None}

    #configParams["numOfBlockTypes"] = dataBuffer.GetOneByteToInt(NUM_BLOCK_TYPES)
    configParams["freeSlcBlockCount"] = dataBuffer.GetTwoBytesToInt(FREE_SLC_BLOCK_COUNT)
    configParams["freeMlcBlockCount"] = dataBuffer.GetTwoBytesToInt(FREE_MLC_BLOCK_COUNT)

    return configParams
    """
    opcode=0xc9
    subOpcode=63
    Buf = pyWrap.Buffer.CreateBuffer(1)
    cdb = [opcode, subOpcode, 0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    logger = vtfContainer.GetLogger()
    logger.Info("", "Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, 0))
    responseBuf = SendDiagnostic(vtfContainer, Buf, cdb, 0, 1, opcode, "Free MLC Block count")

    FBL = responseBuf.GetTwoBytesToInt(0x0)
    return FBL

def GetFreeBlockCount(vtfContainer):
    """
    Description:
       * Gets the free block count of SLC and MLC
    """
    # Offsets
    GET_FREE_BLOCK_COUNT_OPCODE = 0xC9
    GET_FREE_BLOCK_COUNT_SUBOPCODE = 0x30
    NUM_BLOCK_TYPES = 0                              #0
    FREE_SLC_BLOCK_COUNT = NUM_BLOCK_TYPES + 1       #1
    FREE_MLC_BLOCK_COUNT = FREE_SLC_BLOCK_COUNT + 2  #3

    commandName = "Get Free Block Count"

    opcode = GET_FREE_BLOCK_COUNT_OPCODE
    subOpcode = GET_FREE_BLOCK_COUNT_SUBOPCODE

    cdb = [ opcode, subOpcode, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
           0, 0, 0, 0
           ]

    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    configParams = {"numOfBlockTypes":None, "freeSlcBlockCount":None, "freeMlcBlockCount":None}

    configParams["numOfBlockTypes"] = dataBuffer.GetOneByteToInt(NUM_BLOCK_TYPES)
    configParams["freeSlcBlockCount"] = dataBuffer.GetTwoBytesToInt(FREE_SLC_BLOCK_COUNT)
    configParams["freeMlcBlockCount"] = dataBuffer.GetTwoBytesToInt(FREE_MLC_BLOCK_COUNT)

    return configParams
#----------------------------------------------------------------------
def GetCountOfDies(vtfContainer):
    ConfiguraionBuffer=ReadConfigurationParameters(vtfContainer)
    diesPerPhysChip=ConfiguraionBuffer["diesPerPhysChip"]
    numPhysChip=ConfiguraionBuffer["numPhysChip"]
    diecount = diesPerPhysChip * numPhysChip
    return diecount

def ReadMmlParameters(vtfContainer):
    """
    Name : ReadMmlParameters(): _Get_Diag_MMLConfigData_t

    Description : This function calls "Read firmware parameters(0x65)", provides MML parameters

    Arguments :
    vtfContainer - vtfContainer Object

    Returns :
    configParams - dictionary with MML parameters

    opcode = 0x65
    subOpcode = 0x03
    """

    #Meta block information
    SLC_MB_SIZE = 0                                               #0->4
    MLC_MB_SIZE = 4 #SLC_MB_SIZE + 4                              #4->4
    PAGE_SIZE = 8 #MLC_MB_SIZE + 4                                #8->9
    META_PLANE_SIZE = 9 #PAGE_SIZE + 1                            #9->11
    NUM_META_PLANE_IN_SYSTEM = 11 #META_PLANE_SIZE + 1           #11->12
    START_DUMMY_FILL_SIZE = 12 #NUM_META_PLANE_IN_SYSTEM + 1     #12->13
    END_DUMMY_FILL_SIZE = 13 #START_DUMMY_FILL_SIZE + 1           #13->14
    NUM_MP_IN_SAFE_MARGIN= 14 #END_DUMMY_FILL_SIZE + 1            #14->16

    #MIP information
    NUM_GAT_MIP_MB = 16 #NUM_MP_IN_SAFE_MARGIN + 2               #16->17
    MIP_PAGE_SIZE = 17 #NUM_GAT_MIP_MB + 1                        #17->18
    GAT_PAGE_SIZE = 18 #MIP_PAGE_SIZE + 1                         #18->19
    IGAT_PAGE_SIZE = 19 #GAT_PAGE_SIZE + 1                        #19->20
    MAX_GAT_IGAT_PAGES_IN_GAT_PAGE_CACHE = 20 #IGAT_PAGE_SIZE + 1 #20->21
    GAT_PAGE_CACHE_DIRTY_PAGE_COUNT = 21 #MAX_GAT_IGAT_PAGES_IN_GAT_PAGE_CACHE + 1    #21->22
    GAT_DELTA_SIZE = 22 #GAT_PAGE_CACHE_DIRTY_PAGE_COUNT + 1                          #22->24
    IGAT_DELTA_SIZE = 24 #GAT_DELTA_SIZE + 1                                          #24->25
    MIP_WRITE_STEP = 25 #IGAT_DELTA_SIZE + 1                                          #25->26
    GAT_PAGE_COUNT = 26 #MIP_WRITE_STEP + 1                                           #26->28
    IGAT_PAGE_COUNT = 28 #GAT_PAGE_COUNT + 2                                          #28->30
    GAT_PAGE_ENTRY_COUNT = 30 #IGAT_PAGE_COUNT + 2                                    #30->32
    IGAT_PAGE_ENTRY_COUNT = 32 #GAT_PAGE_ENTRY_COUNT + 2                              #32->36

    #Block manager information
    SLC_FBL_SIZE = 36 #IGAT_PAGE_ENTRY_COUNT + 4                                      #36->38
    MLC_FBL_SIZE = 38 #SLC_FBL_SIZE + 1                                               #38->40
    SLC_FBL_FREE_BLOCK_THRESHOLD = 40 #MLC_FBL_SIZE + 1                               #40->41
    MLC_FBL_FREE_BLOCK_THRESHOLD = 41 #SLC_FBL_FREE_BLOCK_THRESHOLD + 1               #41->42

    #GC information
    IDLE_FOLDING_LG_THRESHOLD = 42 #MLC_FBL_FREE_BLOCK_THRESHOLD + 1                  #42->46
    FOREGROUND_FOLDING_LG_THRESHOLD = 46 #IDLE_FOLDING_LG_THRESHOLD + 4               #46->50

    #Update manager information
    OPEN_UB_COUNT = 50 #FOREGROUND_FOLDING_LG_THRESHOLD + 4                           #50->51
    LG_PER_SLC_BLOCK = 51 #OPEN_UB_COUNT + 1                                          #51->55
    LG_PER_MLC_BLOCK = 55 #LG_PER_SLC_BLOCK + 1                                       #55->59
    NUM_SECTORS_PER_LG_FRAGMENT = 59 #LG_PER_MLC_BLOCK + 1                            #59->60
    NUM_FRAGMENTS_PER_META_PAGE = 60 #NUM_SECTORS_PER_LG_FRAGMENT + 1                 #60->61
    MIN_PROGRAMMABLE_UNIT_IN_SECTORS = 61 #NUM_FRAGMENTS_PER_META_PAGE + 1            #61->62
    MIN_EMPTY_BLOCKS = 62 #MIN_PROGRAMMABLE_UNIT_IN_SECTORS + 1                       #62->63
    LOG_2_NUM_SECTORS_PER_LG_FRAGMENT = 63 #MIN_EMPTY_BLOCKS + 1                      #63->64
    NUM_FRAGMENTS_PER_LG = 64 #LOG_2_NUM_SECTORS_PER_LG_FRAGMENT + 1                  #64->66
    EPWR_THRESHOLD_IN_PAGES = 66 #NUM_FRAGMENTS_PER_LG + 2                            #66->68
    NUM_SLC_MB = 68 #EPWR_THRESHOLD_IN_PAGES + 2                                      #68->70
    NUM_MLC_MB = 70 #NUM_SLC_MB + 2                                                   #70->72
    LG_SIZE = 72 #NUM_MLC_MB + 2                                                      #72->74

    #GAT config information
    NUM_SECTORS_IN_SUB_LG = 74 #LG_SIZE + 2                                           #74->75
    CONTROL_PAGE_SIZE_IN_SECTORS = 75 #NUM_SECTORS_IN_SUB_LG + 1                      #75->76
    NUM_GAT_BLOCKS = 76 #CONTROL_PAGE_SIZE_IN_SECTORS +  1                            #76->77
    NUM_LG_IN_GAT_PAGE = 77 #NUM_GAT_BLOCKS + 1                                       #77->78
    DUAL_WRITE_ENABLED_GAT = 78 #NUM_LG_IN_GAT_PAGE + 1                               #78->80
    NUM_SECTORS_IN_LG = 79 #DUAL_WRITE_ENABLED_GAT + 1                                #80->82
    NUM_SUB_LGS_IN_LG = 81 #NUM_SECTORS_IN_LG + 2                                     #82->84
    CONTROL_PAGE_SIZE_IN_BYTES = 83 #NUM_SUB_LGS_IN_LG + 2                            #84->86
    GAT_DELTA_MAX_ENTRIES = 85 #CONTROL_PAGE_SIZE_IN_BYTES + 2                        #86->88
    GAT_DELTA_THRESHOLD_LEVEL = 87 #GAT_DELTA_MAX_ENTRIES + 2                         #88->90
    NUM_GAT_DIR_PAGES = 89 #GAT_DELTA_THRESHOLD_LEVEL + 2                             #90->92
    NUM_ENTRIES_PER_GAT_DIR_PAGE = 91 #NUM_GAT_DIR_PAGES + 2                          #92->94
    NUM_ENTRIES_PER_GAT_DIR_RAND_PAGE = 93 #NUM_ENTRIES_PER_GAT_DIR_PAGE + 2          #94->96
    NUM_SECTORS_IN_DEVICE = 95 #NUM_ENTRIES_PER_GAT_DIR_RAND_PAGE + 2                 #96->100
    NUM_LG_IN_DEVICE = 99 #NUM_SECTORS_IN_DEVICE + 4                                  #100->104
    NUM_SUB_LG_IN_DEVICE = 103 #NUM_LG_IN_DEVICE + 4                                   #104->108
    GAT_DIR_DELTA_MAX_ENTRIES = 107 #NUM_SUB_LG_IN_DEVICE + 4                          #108->112
    GAT_DIR_DELTA_THRESHOLD_LEVEL = 111 #GAT_DIR_DELTA_MAX_ENTRIES +  4                #112->116
    NUM_GAT_DIR_RAND_ENTRY_PAGES = 115 #GAT_DIR_DELTA_THRESHOLD_LEVEL + 4              #116->120

    #IGAT config information
    IGAT_DELTA_MAX_ENTRIES = 119 #NUM_GAT_DIR_RAND_ENTRY_PAGES + 4                     #120->121
    IGAT_DELTA_THRESHOLD_LEVEL = 120 #IGAT_DELTA_MAX_ENTRIES + 1                       #121->122
    NUM_ENTRIES_PER_IGAT_PAGE = 121 #IGAT_DELTA_THRESHOLD_LEVEL + 1                    #122->124
    NUM_SUB_LG_IN_SLC_BLOCK = 123 #NUM_ENTRIES_PER_IGAT_PAGE + 2                       #124->126
    NUM_SUB_LG_IN_MLC_BLOCK = 125 #NUM_SUB_LG_IN_SLC_BLOCK + 2                         #126->128

    #Stream manager information
    NUM_RANDOM_STREAMS= 127 #NUM_SUB_LG_IN_MLC_BLOCK + 2                                #128->129
    NUM_SEQ_STREAMS = 128 #NUM_RANDOM_STREAMS + 1                                       #129->130
    NUM_RELOCATION_STREAMS = 129 #NUM_SEQ_STREAMS + 1                                   #130->131
    DUAL_WRITE_SEQ_STREAM = 130 #NUM_RELOCATION_STREAMS + 1                             #131->146
    DUAL_WRITE_SLC_RAND_STREAM = 146 #DUAL_WRITE_SEQ_STREAM + 16                        #146->148
    DUAL_WRITE_MLC_RAND_STREAM = 148 #DUAL_WRITE_SLC_RAND_STREAM + 2                    #148->149

    #RGAT Config Information
    RGAT_DELTA_MAX_ENTRIES = 149 #DUAL_WRITE_MLC_RAND_STREAM + 1                          #149->150
    RGAT_DELTA_THRESHOLD_LEVEL = 150 #RGAT_DELTA_MAX_ENTRIES +  1                        #150->151
    RGAT_DIR_DELTA_MAX_ENTRIES = 151 #RGAT_DELTA_THRESHOLD_LEVEL +1                      #151->152
    RGAT_DIR_DELTA_THRESHOLD_LEVEL = 152 #RGAT_DIR_DELTA_MAX_ENTRIES +  1                #152->153
    NUM_ENTRIES_PER_RGAT_PAGE = 153 #RGAT_DIR_DELTA_THRESHOLD_LEVEL +   1                #153->155
    NUM_ENTRIES_PER_RGAT_DIR_PAGE = 155 #NUM_ENTRIES_PER_RGAT_PAGE + 2                   #155->157
    NUM_RGAT_PAGES_PER_MB = 157 #NUM_ENTRIES_PER_RGAT_DIR_PAGE + 1                       #157->159

    #Flag to intimate Test about Dedicted MIP block enabling
    MIP_IS_DEDICATED_BLOCK = 159 #NUM_RGAT_PAGES_PER_MB + 2                            #159->160
    MLC_MAX_GROWN_DEFECTS = 160 #MIP_IS_DEDICATED_BLOCK + 1                            #160->161
    SLC_POOL_BUDGET = 161 #MLC_MAX_GROWN_DEFECTS + 1                                   #161->162
    NUMBER_OF_CONTEXT_BLOCKS = 162 #SLC_POOL_BUDGET + 1                                 #162->163
    LAST_META_BLOCK_NUM_MLC = 163 #NUMBER_OF_CONTEXT_BLOCKS + 1                         #163->165
    LAST_META_BLOCK_NUM_SLC = 165 #LAST_META_BLOCK_NUM_MLC + 2                         #165->167
    DLM_MIN_THRESHOLD = 167 #LAST_META_BLOCK_NUM_SLC + 2                               #167->169

    #To be Asked
    #DUAL_WRITE_RAND_STREAM= DUAL_WRITE_SLC_RAND_STREAM + 2                        #133->137

    #TIMESTAMP_THRESHOLD = NUMBER_OF_CONTEXT_BLOCKS + 1                               #145
    #OMW_GAT_DELTA_MARGIN = TIMESTAMP_THRESHOLD + 2
    #OMW_TS_MARGIN = OMW_GAT_DELTA_MARGIN + 1
    #OMW_BALANCED_GC_THRESHOLD_FRAGS = OMW_TS_MARGIN + 1

    commandName = "Read MML Parameters"

    opcode = READ_FW_PARAM_DIAG_OPCODE
    subOpcode = READ_MML_PARAMETERS_SUBOPCODE

    cdb = [ opcode, 0, subOpcode, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
           0, 0, 0, 0
           ]

    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: 0x%X, Data Direction: %s" %(opcode, subOpcode, READ_DATA))

    dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    configParams = {"slcMbsize":None, "mlcMbSize":None, "pageSize":None, "metaPlaneSize":None, "numMetaPlanesInSystem":None,"DummyFillStart":None, \
                    "DummyFillEnd":None,"numofMpInSafeMargin":None,"numGatMipMb":None, "mipPageSize":None, "gatPageSize":None, "igatPageSize":None, \
                    "maxGatIgatPagesInGatPageCache":None, "gatPageCacheDirtyPageCount":None, "gatDeltaSize":None, "igatDeltaSize":None, \
                   "mipWriteStep":None, "gatPageCount":None, "igat_pageCount":None, "gatPageEntrycount":None, "igatPageEntryCount":None, \
                   "slcFblSize":None, "mlcFblSize":None, "slcFblFreeBlockThreshold":None, "mlcFblFreeBlockThreshold":None, \
                   "idleFoldingLgThreshold":None, "foregroundFoldingLgThreshold":None,"openUbCount":None, "lgsPerSlcBlock":None, \
                   "lgsPerMlcBlock":None, "sectorsPerLgFragment":None, "fragmentsPerMetaPage":None, "minProgrammableUnit":None, "minEmptyBlocks":None, \
                   "log2SectorsPerLgFrag":None, "fragmentsPerLg":None, "epwrThresholdInPages":None, "numSlcMb":None, "numMlcMb":None, "lgSize":None, \
                   "sectorsInSubLg":None, "controlPageSizeInSectors":None, "numGatBlocks":None, "numLgInGatPage":None, "DualWriteEnabledInGat":None,\
                   "sectorsInLg":None, "numsubLgsInLg":None, "controlPageSizeInBytes":None, "gatDeltaMaxEntries":None, "gatDeltaThresholdLevel":None, \
                   "numGatDirPages":None, "numEntriesPerGatDirPage":None, "numPagesPerGatDirRandPage":None, "numSectorsInDevice":None, \
                   "numLgsInDevice":None, "numSubLgsInDevice":None, "gatDirDeltaMaxEntries":None,"gatDirDeltaThresholdLevel":None,\
                   "numGatDirRandEntryPages":None, "igatDeltaMaxEntries":None, "igatDeltaThresholdLevel":None, "entriesPerIgatPage":None,\
                   "numSubLgInSlcBlock":None, "numSubLgInMlcBlock":None,"numRandomStreams":None,"numSeqStreams":None,"numRelocationStreams":None,\
                   "DualWriteSeqStream":None,"DualWriteSLCRandStream":None,"DualWriteMLCRandStream":None , "MIPIsDedicatedBlock": None, "MlcMaxGrownDefects": None,\
                   "SlcPoolBudget": None, "NumContextBlocks": None, "timeStampThresholdLevel": None, "OMWGatDeltaMargin": None, "OMWTSMargin": None, "OMWBalGCThresholdFrags": None,\
                   "RGATDeltaMaxEntries":None, "RGATDeltaThresholdLevel":None, "RGATDirDeltaMaxEntries":None, "RGATDirDeltaThresholdLevel":None, \
                   "numEntriesPerRGATPage":None, "numEntriesPerRGATDirPage":None, "numRGATPagesPerMB":None, "lastSLCRelinkedMB":None, "lastMLCRelinkedMB":None}

        #RPG-13756 : Harish
    # Changing from Reading 2 bytes to 4 bytes for SLC_MB & MLC_MB size
    #configParams["slcMbsize"] = dataBuffer.GetTwoBytesToInt(SLC_MB_SIZE)
    #configParams["mlcMbSize"] = dataBuffer.GetTwoBytesToInt(MLC_MB_SIZE)
    configParams["slcMbsize"] = dataBuffer.GetFourBytesToInt(SLC_MB_SIZE)
    configParams["mlcMbSize"] = dataBuffer.GetFourBytesToInt(MLC_MB_SIZE)
    configParams["pageSize"] = dataBuffer.GetOneByteToInt(PAGE_SIZE)
    configParams["metaPlaneSize"] = dataBuffer.GetOneByteToInt(META_PLANE_SIZE)
    configParams["numMetaPlanesInSystem"] = dataBuffer.GetOneByteToInt(NUM_META_PLANE_IN_SYSTEM)
    configParams["DummyFillStart"] = dataBuffer.GetOneByteToInt(START_DUMMY_FILL_SIZE)
    configParams["DummyFillEnd"] = dataBuffer.GetOneByteToInt(END_DUMMY_FILL_SIZE)
    configParams["numofMpInSafeMargin"]=dataBuffer.GetOneByteToInt(NUM_MP_IN_SAFE_MARGIN)
    configParams["numGatMipMb"] = dataBuffer.GetOneByteToInt(NUM_GAT_MIP_MB)
    configParams["mipPageSize"] = dataBuffer.GetOneByteToInt(MIP_PAGE_SIZE)
    configParams["gatPageSize"] = dataBuffer.GetOneByteToInt(GAT_PAGE_SIZE)
    configParams["igatPageSize"] = dataBuffer.GetOneByteToInt(IGAT_PAGE_SIZE)
    configParams["maxGatIgatPagesInGatPageCache"] = dataBuffer.GetOneByteToInt(MAX_GAT_IGAT_PAGES_IN_GAT_PAGE_CACHE)
    configParams["gatPageCacheDirtyPageCount"] = dataBuffer.GetOneByteToInt(GAT_PAGE_CACHE_DIRTY_PAGE_COUNT)
    configParams["gatDeltaSize"] = dataBuffer.GetOneByteToInt(GAT_DELTA_SIZE)
    configParams["igatDeltaSize"] = dataBuffer.GetOneByteToInt(IGAT_DELTA_SIZE)
    configParams["mipWriteStep"] = dataBuffer.GetOneByteToInt(MIP_WRITE_STEP)
    configParams["gatPageCount"] = dataBuffer.GetTwoBytesToInt(GAT_PAGE_COUNT)
    configParams["igat_pageCount"] = dataBuffer.GetTwoBytesToInt(IGAT_PAGE_COUNT)
    configParams["gatPageEntrycount"] = dataBuffer.GetTwoBytesToInt(GAT_PAGE_ENTRY_COUNT)
    configParams["igatPageEntryCount"] = dataBuffer.GetTwoBytesToInt(IGAT_PAGE_ENTRY_COUNT)
    configParams["slcFblSize"] = dataBuffer.GetOneByteToInt(SLC_FBL_SIZE)
    configParams["mlcFblSize"] = dataBuffer.GetOneByteToInt(MLC_FBL_SIZE)
    configParams["slcFblFreeBlockThreshold"] = dataBuffer.GetOneByteToInt(SLC_FBL_FREE_BLOCK_THRESHOLD)
    configParams["mlcFblFreeBlockThreshold"] = dataBuffer.GetOneByteToInt(MLC_FBL_FREE_BLOCK_THRESHOLD)
    configParams["idleFoldingLgThreshold"] = dataBuffer.GetFourBytesToInt(IDLE_FOLDING_LG_THRESHOLD)
    configParams["foregroundFoldingLgThreshold"] = dataBuffer.GetFourBytesToInt(FOREGROUND_FOLDING_LG_THRESHOLD)
    configParams["openUbCount"] = dataBuffer.GetOneByteToInt(OPEN_UB_COUNT)
    configParams["lgsPerSlcBlock"] = dataBuffer.GetOneByteToInt(LG_PER_SLC_BLOCK)
    configParams["lgsPerMlcBlock"] = dataBuffer.GetOneByteToInt(LG_PER_MLC_BLOCK)
    configParams["sectorsPerLgFragment"] = dataBuffer.GetOneByteToInt(NUM_SECTORS_PER_LG_FRAGMENT)
    configParams["fragmentsPerMetaPage"] = dataBuffer.GetOneByteToInt(NUM_FRAGMENTS_PER_META_PAGE)
    configParams["minProgrammableUnit"] = dataBuffer.GetOneByteToInt(MIN_PROGRAMMABLE_UNIT_IN_SECTORS)
    configParams["minEmptyBlocks"] = dataBuffer.GetOneByteToInt(MIN_EMPTY_BLOCKS)
    configParams["log2SectorsPerLgFrag"] = dataBuffer.GetOneByteToInt(LOG_2_NUM_SECTORS_PER_LG_FRAGMENT)
    configParams["fragmentsPerLg"] = dataBuffer.GetTwoBytesToInt(NUM_FRAGMENTS_PER_LG)
    configParams["epwrThresholdInPages"] = dataBuffer.GetTwoBytesToInt(EPWR_THRESHOLD_IN_PAGES)
    configParams["numSlcMb"] = dataBuffer.GetTwoBytesToInt(NUM_SLC_MB)
    configParams["numMlcMb"] = dataBuffer.GetTwoBytesToInt(NUM_MLC_MB)
    configParams["lgSize"] = dataBuffer.GetTwoBytesToInt(LG_SIZE)
    configParams["sectorsInSubLg"] = dataBuffer.GetOneByteToInt(NUM_SECTORS_IN_SUB_LG)
    configParams["controlPageSizeInSectors"] = dataBuffer.GetOneByteToInt(CONTROL_PAGE_SIZE_IN_SECTORS)
    configParams["numGatBlocks"] = dataBuffer.GetOneByteToInt(NUM_GAT_BLOCKS)
    configParams["numLgInGatPage"] = dataBuffer.GetOneByteToInt(NUM_LG_IN_GAT_PAGE)
    configParams["DualWriteEnabledInGat"] = dataBuffer.GetOneByteToInt(DUAL_WRITE_ENABLED_GAT)
    configParams["sectorsInLg"] = dataBuffer.GetTwoBytesToInt(NUM_SECTORS_IN_LG)
    configParams["numsubLgsInLg"] = dataBuffer.GetTwoBytesToInt(NUM_SUB_LGS_IN_LG)
    configParams["controlPageSizeInBytes"] = dataBuffer.GetTwoBytesToInt(CONTROL_PAGE_SIZE_IN_BYTES)
    configParams["gatDeltaMaxEntries"] = dataBuffer.GetTwoBytesToInt(GAT_DELTA_MAX_ENTRIES)
    configParams["gatDeltaThresholdLevel"] = dataBuffer.GetTwoBytesToInt(GAT_DELTA_THRESHOLD_LEVEL)
    configParams["numGatDirPages"] = dataBuffer.GetTwoBytesToInt(NUM_GAT_DIR_PAGES)
    configParams["numEntriesPerGatDirPage"] = dataBuffer.GetTwoBytesToInt(NUM_ENTRIES_PER_GAT_DIR_PAGE)
    configParams["numPagesPerGatDirRandPage"] = dataBuffer.GetTwoBytesToInt(NUM_ENTRIES_PER_GAT_DIR_RAND_PAGE)
    configParams["numSectorsInDevice"] = dataBuffer.GetFourBytesToInt(NUM_SECTORS_IN_DEVICE)
    configParams["numLgsInDevice"] = dataBuffer.GetFourBytesToInt(NUM_LG_IN_DEVICE)
    configParams["numSubLgsInDevice"] = dataBuffer.GetFourBytesToInt(NUM_SUB_LG_IN_DEVICE)
    configParams["gatDirDeltaMaxEntries"] = dataBuffer.GetFourBytesToInt(GAT_DIR_DELTA_MAX_ENTRIES)
    configParams["gatDirDeltaThresholdLevel"] = dataBuffer.GetFourBytesToInt(GAT_DIR_DELTA_THRESHOLD_LEVEL)
    configParams["numGatDirRandEntryPages"] = dataBuffer.GetFourBytesToInt(NUM_GAT_DIR_RAND_ENTRY_PAGES)
    configParams["igatDeltaMaxEntries"] = dataBuffer.GetOneByteToInt(IGAT_DELTA_MAX_ENTRIES)
    configParams["igatDeltaThresholdLevel"] = dataBuffer.GetOneByteToInt(IGAT_DELTA_THRESHOLD_LEVEL)
    configParams["entriesPerIgatPage"] = dataBuffer.GetOneByteToInt(NUM_ENTRIES_PER_IGAT_PAGE)
    configParams["numSubLgInSlcBlock"] = dataBuffer.GetTwoBytesToInt(NUM_SUB_LG_IN_SLC_BLOCK)
    configParams["numSubLgInMlcBlock"] = dataBuffer.GetTwoBytesToInt(NUM_SUB_LG_IN_MLC_BLOCK)
    configParams["numRandomStreams"] = dataBuffer.GetOneByteToInt(NUM_RANDOM_STREAMS)
    configParams["numSeqStreams"] = dataBuffer.GetOneByteToInt(NUM_SEQ_STREAMS)
    configParams["numRelocationStreams"] = dataBuffer.GetOneByteToInt(NUM_RELOCATION_STREAMS)
    configParams["DualWriteSeqStream"] = dataBuffer.GetData(DUAL_WRITE_SEQ_STREAM,8)
    configParams["DualWriteSLCRandStream"] = dataBuffer.GetData(DUAL_WRITE_SLC_RAND_STREAM,2)
    configParams["DualWriteMLCRandStream"] = dataBuffer.GetOneByteToInt(DUAL_WRITE_SLC_RAND_STREAM)
    configParams["MIP_IsDedicatedBlock"] = dataBuffer.GetOneByteToInt(MIP_IS_DEDICATED_BLOCK)
    configParams["MlcMaxGrownDefects"] = dataBuffer.GetOneByteToInt(MLC_MAX_GROWN_DEFECTS)
    configParams["SlcPoolBudget"] = dataBuffer.GetOneByteToInt(SLC_POOL_BUDGET)
    #configParams["NumContextBlocks"] = dataBuffer.GetOneByteToInt(NUMBER_OF_CONTEXT_BLOCKS)
    #configParams["timeStampThresholdLevel"] = dataBuffer.GetTwoBytesToInt(TIMESTAMP_THRESHOLD)
    #configParams["OMWGatDeltaMargin"] = dataBuffer.GetOneByteToInt(OMW_GAT_DELTA_MARGIN)
    #configParams["OMWTSMargin"] = dataBuffer.GetOneByteToInt(OMW_TS_MARGIN)
    #configParams["OMWBalGCThresholdFrags"] = dataBuffer.GetTwoBytesToInt(OMW_BALANCED_GC_THRESHOLD_FRAGS)
    configParams["RGATDeltaMaxEntries"] = dataBuffer.GetOneByteToInt(RGAT_DELTA_MAX_ENTRIES)
    configParams["RGATDeltaThresholdLevel"] = dataBuffer.GetOneByteToInt(RGAT_DELTA_THRESHOLD_LEVEL)
    configParams["RGATDirDeltaMaxEntries"] = dataBuffer.GetOneByteToInt(RGAT_DIR_DELTA_MAX_ENTRIES)
    configParams["RGATDirDeltaThresholdLevel"] = dataBuffer.GetOneByteToInt(RGAT_DIR_DELTA_THRESHOLD_LEVEL)
    configParams["numEntriesPerRGATPage"] = dataBuffer.GetTwoBytesToInt(NUM_ENTRIES_PER_RGAT_PAGE)
    configParams["numEntriesPerRGATDirPage"] = dataBuffer.GetTwoBytesToInt(NUM_ENTRIES_PER_RGAT_DIR_PAGE)
    configParams["numRGATPagesPerMB"] = dataBuffer.GetTwoBytesToInt(NUM_RGAT_PAGES_PER_MB)
    configParams["lastMLCRelinkedMB"] = dataBuffer.GetTwoBytesToInt(LAST_META_BLOCK_NUM_MLC)
    configParams["lastSLCRelinkedMB"] = dataBuffer.GetTwoBytesToInt(LAST_META_BLOCK_NUM_SLC)

    return configParams

#end of ReadMmlParameterss


#----------------------------------------------------------------------
def GetCurrentDeltaSize(vtfContainer,Structure,multiMP=1):

    CacheInfo=GetGatCacheInfo(vtfContainer)

    GATDeltaSizeOffset  = GAT_DELTA_SIZE_OFFSET #0x2412
    IGATDeltaSizeoffset = IGAT_DELTA_SIZE_OFFSET #0x2414
    RGATDeltaSizeoffset = RGAT_DELTA_SIZE #0x2418


    if Structure=="IGAT":
        return CacheInfo.GetTwoBytesToInt(IGATDeltaSizeoffset)
    elif Structure=="GAT":
        return CacheInfo.GetTwoBytesToInt(GATDeltaSizeOffset)
    elif Structure=="RGAT":
        return CacheInfo.GetTwoBytesToInt(RGATDeltaSizeoffset)

#----------------------------------------------------------------------
def FBLCount_GatCacheInfo(vtfContainer,Structure):

    CacheInfo=GetGatCacheInfo(vtfContainer)
    SLCFBLCountOffset = BINARY_FBL_COUNTER #0x240A
    MLCFBLCountOffset = MLC_FBL_COUNTER #0x2408

    if Structure=="SLCFBLCount":
        return CacheInfo.GetTwoBytesToInt(SLCFBLCountOffset)
    elif Structure=="MLCFBLCount":
        return CacheInfo.GetTwoBytesToInt(MLCFBLCountOffset)
#----------------------------------------------------------------------

def IsDoubleFineProgrammingEnabled(vtfContainer):
    commandName = "IsDoubleFineProgrammingEnabled"
    opcode = 0xc9
    Subopcode = 0x35
    try:
        cdb = [ opcode, Subopcode,0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
              0, 0, 0, 0
                 ]

        dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

        dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

        IsEnabled=dataBuffer.GetOneByteToInt(0x0)
    except:
        IsEnabled=0

    return IsEnabled
#----------------------------------------------------------------------
def IsPPDEnabled(vtfContainer):
    commandName = "IsPPDEnabled"
    opcode = 0xc9
    Subopcode = 0x38
    try:
        cdb = [ opcode, Subopcode,0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
              0, 0, 0, 0
                 ]

        dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

        dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

        IsEnabled=dataBuffer.GetOneByteToInt(0x0)
    except:
        IsEnabled=0

    return IsEnabled
def GATActiveBlockWriteOffset_GatCacheInfo(vtfContainer):

    CacheInfo=GetGatCacheInfo(vtfContainer)
    GATActiveBlockWriteOffset = ACTIVE_BLOCK_WRITE_OFFSET #0x2410

    return CacheInfo.GetTwoBytesToInt(GATActiveBlockWriteOffset)

#----------------------------------------------------------------------

def MipFlush(vtfContainer):
    """
    Name : MipFlush

    Description : This function calls "Read firmware parameters(0x65)", provides MML parameters

    Arguments :
              vtfContainer - vtfContainer Object

    Returns :
             configParams - dictionary with MML parameters

    opcode = 0xCA

    subOpcode = 0x13

    """
    commandName = "MipFlush"

    opcode=0xCA
    subOpcode = 0x13

    cdb = [ opcode, subOpcode,0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
           0, 0, 0, 0
           ]

    StatusBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: 0x%X, Data Direction: %s" %(opcode, subOpcode, NO_DATA))

    SendDiagnostic(vtfContainer, StatusBuffer, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)


    return 0
#----------------------------------------------------------------------

def ReadConfigurationParameters(vtfContainer):
    """
    Name : ReadConfigurationParameters()

    Description : This function calls "Read firmware parameters(0x65)", provides firmware configuration parameters.

    Arguments :
              vtfContainer - vtfContainer Object
              returnBuffer - returns data buffer if this is '1'

    Returns :
             fWParametersData - f/w parameter buffer
             configParams - dictionary with firmware configuration parameters

    opcode = 0x65

    subOpcode = 0x02

    """
    #offsets modified to take relative values.
    BE_CAPACITY_PER_BANK_OFFSET = 0                               #0
    FLASH_ID_OFFSET = BE_CAPACITY_PER_BANK_OFFSET + 4             #4
    BYTES_PER_SECTOR_OFFSET = FLASH_ID_OFFSET + 16                #20
    SECTORS_PER_PAGE_OFFSET = BYTES_PER_SECTOR_OFFSET + 4         #24
    PAGES_PER_MLC_BLOCK_OFFSET = SECTORS_PER_PAGE_OFFSET        + 4       #28
    BLOCKS_PER_DIE_OFFSET = PAGES_PER_MLC_BLOCK_OFFSET +        4         #32
    DIES_PER_PHY_CHIP_OFFSET = BLOCKS_PER_DIE_OFFSET + 4                  #36
    NUM_LOG_CHIPS_PER_BANK_OFFSET = DIES_PER_PHY_CHIP_OFFSET + 4          #40
    NUM_PHY_CHIPS_OFFSET = NUM_LOG_CHIPS_PER_BANK_OFFSET        + 4       #44
    PLANES_PER_CHIP_OFFSET = NUM_PHY_CHIPS_OFFSET + 4             #48
    SECTORS_PER_ECC_PAGE_OFFSET = PLANES_PER_CHIP_OFFSET        + 4       #52
    ECC_PAGES_PER_PAGE_OFFSET = SECTORS_PER_ECC_PAGE_OFFSET + 4   #56
    SEC_PER_METAPAGE_OFFSET = ECC_PAGES_PER_PAGE_OFFSET + 4       #60
    SEC_PER_METABLOCK_OFFSET = SEC_PER_METAPAGE_OFFSET +        4         #64
    PHY_PAGES_PER_METAPAGE_OFFSET = SEC_PER_METABLOCK_OFFSET + 4          #68
    METAPAGES_PER_METABLOCK_OFFSET = PHY_PAGES_PER_METAPAGE_OFFSET + 4     #72
    TOTAL_META_BLOCKS_IN_BANK_OFFSET = METAPAGES_PER_METABLOCK_OFFSET + 4   #76
    NUM_LG_IN_MEDIA_OFFSET = TOTAL_META_BLOCKS_IN_BANK_OFFSET + 4          #80
    PLANE_INTERLEAVE_OFFSET = NUM_LG_IN_MEDIA_OFFSET + 4                           #84
    DIE_INTERLEAVE_OFFSET = PLANE_INTERLEAVE_OFFSET + 4                    #88
    PHY_CHIP_INTELEAVE_OFFSET = DIE_INTERLEAVE_OFFSET + 4                  #92
    PAGE_INTERLEAVE_OFFSET = PHY_CHIP_INTELEAVE_OFFSET +        4                  #96
    LOG_2_PLANE_INTERLEAVE_OFFSET = PAGE_INTERLEAVE_OFFSET + 4             #100
    LOG_2_DIE_INTERLEAVE_OFFSET = LOG_2_PLANE_INTERLEAVE_OFFSET + 4        #104
    LOG_2_PHYS_CHIP_INTERLEAVE_OFFSET = LOG_2_DIE_INTERLEAVE_OFFSET + 4    #108
    LOG_2_PAGE_INTERLEAVE_OFFSET = LOG_2_PHYS_CHIP_INTERLEAVE_OFFSET + 4           #112
    LOG_2_METABLOCK_SIZE_OFFSET = LOG_2_PAGE_INTERLEAVE_OFFSET +        4          #116
    LOG_2_SECTORS_PER_PAGE_OFFSET = LOG_2_METABLOCK_SIZE_OFFSET + 4        #120
    LOG_2_PAGE_PER_BLOCK_OFFSET = LOG_2_SECTORS_PER_PAGE_OFFSET + 4        #124
    LOG_2_BLOCK_PER_PLANE_OFFSET = LOG_2_PAGE_PER_BLOCK_OFFSET +        4          #128
    LOG_2_PLANES_PER_CHIP_OFFSET = LOG_2_BLOCK_PER_PLANE_OFFSET + 4        #132
    LOG_2_DIE_PER_PHYS_CHIP_OFFSET = LOG_2_PLANES_PER_CHIP_OFFSET + 4      #136
    LOG_2_BLOCK_PER_DIE_OFFSET = LOG_2_DIE_PER_PHYS_CHIP_OFFSET + 4        #140
    LOG_2_NUM_LOG_CHIPS_OFFSET = LOG_2_BLOCK_PER_DIE_OFFSET + 4            #144
    LOG_2_SECTORS_PER_ECC_PAGE_OFFSET = LOG_2_NUM_LOG_CHIPS_OFFSET + 4     #148
    CHIP_MAXP_BLOCK_OFFSET = LOG_2_SECTORS_PER_ECC_PAGE_OFFSET +        4          #152
    DEVICE_MODE_OFFSET = CHIP_MAXP_BLOCK_OFFSET + 4         #156
    FLASH_MODE_OFFSET = DEVICE_MODE_OFFSET + 4               #160
    PLANE_STEPPING_OFFSET = FLASH_MODE_OFFSET + 4            #164
    DIE_STEPPING_OFFSET = PLANE_STEPPING_OFFSET + 4          #168
    CHIP_STEPPING_OFFSET = DIE_STEPPING_OFFSET + 4           #172
    ECC_TYPE_OFFSET = CHIP_STEPPING_OFFSET + 4               #176
    ECC_FIELD_SIZE_BYTE_OFFSET = ECC_TYPE_OFFSET + 4         #180
    FEATURES_BITS_OFFSET = ECC_FIELD_SIZE_BYTE_OFFSET +  4   #184
    FIRST_UPPER_PAGE_ADDR_OFFSET = FEATURES_BITS_OFFSET + 4  #188
    NUMER_OF_BANKS_OFFSET = FIRST_UPPER_PAGE_ADDR_OFFSET + 4 #192
    PAGES_PER_SLC_BLOCK_OFFSET = NUMER_OF_BANKS_OFFSET + 4   #196
    DEVICE_IN_SLC_MODE = PAGES_PER_SLC_BLOCK_OFFSET + 4     #200
    RSECC_PARITY_2 = DEVICE_IN_SLC_MODE+4                    #204
    FS_PAGES_PER_BLOCK=RSECC_PARITY_2+4                      #208
    FS_METABLOCK=FS_PAGES_PER_BLOCK+2                        #210
    RS_NUM_COPIES=FS_METABLOCK+1                             #211

    STRINGS_PER_BLOCK = RS_NUM_COPIES+1                      #212
    WL_PER_BLOCK = STRINGS_PER_BLOCK+1                       #213
    NUMBER_OF_SLOTS = WL_PER_BLOCK+4                         #217
    commandName = "Read Configuration Parameters"
    opcode = 0x65
    subOpcode = 0x02
    cdb = [ opcode, 0, subOpcode, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
           0, 0, 0, 0
           ]
    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: 0x%X, Data Direction: %s" %(opcode, subOpcode, READ_DATA))

    dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    configParams = {"beCapacityPerBank":None, "flashId":None, "bytesPerSector":None, "sectorsPerPage":None,
                    "pagesPerMlcBlock":None, "blocksPerDie":None, "diesPerPhysChip":None, "numPhysChip":None, "planesPerChp":None,
                    "sectorsPerEccPage":None, "eccPagesPerPage":None, "sectorsPerMetaPage":None, "sectorsPerMetaBlock":None,
                   "phyPagesPerMetaPage":None, "metaPagesPerMetaBlock":None, "totalMetaBlocksPerBank":None, "numberOfLgInMedia":None,
                   "planeInterleave":None, "dieInterleave":None, "physChipInterleave":None,
                   "pageInterleave":None, "log2SectorsPerPage":None, "log2BlockPerPlane":None,"log2PlanesPerChip":None,"log2BlockPerDie":None, "chipMaxPBlock":None,
                   "flashMode":None, "eccFieldSizeByte":None, "featureBits":None, "firstUpperPageAddress":None,
                   "numOfBanks":None,"pagesPerSlcBlock":None, "slcmode":None,"FsPagesPerBlock":None,"FsMetablock":None,"RsNumOfCopies":None,"StringsPerBlock":None,
                   "WordlinesPerBlock_BiCS":None,"NumberOfSlots_BiCS":None, "log2DiesPerPhysChip":None}

    configParams["beCapacityPerBank"] = dataBuffer.GetFourBytesToInt(BE_CAPACITY_PER_BANK_OFFSET)
    configParams["flashId"] = dataBuffer.GetEightBytesToInt(FLASH_ID_OFFSET)
    configParams["bytesPerSector"] = dataBuffer.GetFourBytesToInt(BYTES_PER_SECTOR_OFFSET)
    configParams["sectorsPerPage"] = dataBuffer.GetFourBytesToInt(SECTORS_PER_PAGE_OFFSET)
    configParams["pagesPerMlcBlock"] = dataBuffer.GetFourBytesToInt(PAGES_PER_MLC_BLOCK_OFFSET)
    configParams["blocksPerDie"] = dataBuffer.GetFourBytesToInt(BLOCKS_PER_DIE_OFFSET)
    configParams["diesPerPhysChip"] = dataBuffer.GetFourBytesToInt(DIES_PER_PHY_CHIP_OFFSET)
    configParams["numPhysChip"] = dataBuffer.GetFourBytesToInt(NUM_PHY_CHIPS_OFFSET)
    configParams["planesPerChp"] = dataBuffer.GetFourBytesToInt(PLANES_PER_CHIP_OFFSET)
    configParams["sectorsPerEccPage"] = dataBuffer.GetFourBytesToInt(SECTORS_PER_ECC_PAGE_OFFSET)
    configParams["eccPagesPerPage"] = dataBuffer.GetFourBytesToInt(ECC_PAGES_PER_PAGE_OFFSET)
    configParams["sectorsPerMetaPage"] = dataBuffer.GetFourBytesToInt(SEC_PER_METAPAGE_OFFSET)
    configParams["sectorsPerMetaBlock"] = dataBuffer.GetFourBytesToInt(SEC_PER_METABLOCK_OFFSET)
    configParams["phyPagesPerMetaPage"] = dataBuffer.GetFourBytesToInt(PHY_PAGES_PER_METAPAGE_OFFSET)
    configParams["metaPagesPerMetaBlock"] = dataBuffer.GetFourBytesToInt(METAPAGES_PER_METABLOCK_OFFSET)
    configParams["totalMetaBlocksPerBank"] = dataBuffer.GetFourBytesToInt(TOTAL_META_BLOCKS_IN_BANK_OFFSET)
    configParams["numberOfLgInMedia"] = dataBuffer.GetFourBytesToInt(NUM_LG_IN_MEDIA_OFFSET)
    configParams["planeInterleave"] = dataBuffer.GetFourBytesToInt(PLANE_INTERLEAVE_OFFSET)
    configParams["dieInterleave"] = dataBuffer.GetFourBytesToInt(DIE_INTERLEAVE_OFFSET)
    configParams["physChipInterleave"] = dataBuffer.GetFourBytesToInt(PHY_CHIP_INTELEAVE_OFFSET)
    configParams["pageInterleave"] = dataBuffer.GetFourBytesToInt(PAGE_INTERLEAVE_OFFSET)
    configParams["log2SectorsPerPage"] = dataBuffer.GetFourBytesToInt(LOG_2_SECTORS_PER_PAGE_OFFSET)
    configParams["log2BlockPerPlane"] = dataBuffer.GetFourBytesToInt(LOG_2_BLOCK_PER_PLANE_OFFSET)
    configParams["log2PlanesPerChip"] = dataBuffer.GetFourBytesToInt(LOG_2_PLANES_PER_CHIP_OFFSET)
    configParams["log2BlockPerDie"] = dataBuffer.GetFourBytesToInt(LOG_2_BLOCK_PER_DIE_OFFSET)
    configParams["chipMaxPBlock"] = dataBuffer.GetFourBytesToInt(CHIP_MAXP_BLOCK_OFFSET)
    configParams["flashMode"] = dataBuffer.GetFourBytesToInt(FLASH_MODE_OFFSET)
    configParams["eccFieldSizeByte"] = dataBuffer.GetFourBytesToInt(ECC_FIELD_SIZE_BYTE_OFFSET)
    configParams["featureBits"] = dataBuffer.GetFourBytesToInt(FEATURES_BITS_OFFSET)
    configParams["firstUpperPageAddress"] = dataBuffer.GetFourBytesToInt(FIRST_UPPER_PAGE_ADDR_OFFSET)
    configParams["numOfBanks"] = dataBuffer.GetFourBytesToInt(NUMER_OF_BANKS_OFFSET)
    configParams["pagesPerSlcBlock"] = dataBuffer.GetFourBytesToInt(PAGES_PER_SLC_BLOCK_OFFSET)
    configParams["slcmode"] = dataBuffer.GetOneByteToInt(DEVICE_IN_SLC_MODE)
    configParams["FsPagesPerBlock"] = dataBuffer.GetTwoBytesToInt(FS_PAGES_PER_BLOCK)
    configParams["FsMetablock"] = dataBuffer.GetOneByteToInt(FS_METABLOCK)
    configParams["RsNumOfCopies"] = dataBuffer.GetOneByteToInt(RS_NUM_COPIES)
    configParams["StringsPerBlock"] = dataBuffer.GetOneByteToInt(STRINGS_PER_BLOCK)
    configParams["WordlinesPerBlock_BiCS"] = dataBuffer.GetOneByteToInt(WL_PER_BLOCK)
    configParams["NumberOfSlots_BiCS"] = dataBuffer.GetFourBytesToInt(NUMBER_OF_SLOTS)
    configParams["log2DiesPerPhysChip"] = dataBuffer.GetFourBytesToInt(LOG_2_DIE_PER_PHYS_CHIP_OFFSET)
    return configParams
#end of GetFirmwareParametes


def GetDRHistoryCase(vtfContainer, dieAddr, history = True):
    """
    This function uses diag "Dynamic Read Diagnostics" opcode "0xA1" subopcode "0000" to get DR history case of a page
    """
    commandName = "Dynamic Read History Case"
    opcode = 0xA1
    subopcode = 0x00
    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    cdb = [ opcode, 0, 0, 0, 0, 0, 0, 0, 0, dieAddr, 0, 0, 0, 0, 0, 0]
    dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    if history:
        historyCase = dataBuffer.GetOneByteToInt(4)
        return historyCase
    else:
        # Returns MLC mapping table
        mapValue0 = dataBuffer.GetOneByteToInt(11)
        mapValue1 = dataBuffer.GetOneByteToInt(12)
        mapValue2 = dataBuffer.GetOneByteToInt(13)
        mapValue3 = dataBuffer.GetOneByteToInt(14)
        mapValue4 = dataBuffer.GetOneByteToInt(15)
        mapValue5 = dataBuffer.GetOneByteToInt(16)
        mapValue6 = dataBuffer.GetOneByteToInt(17)
        return [mapValue0,mapValue1,mapValue2,mapValue3,mapValue4,mapValue5,mapValue6]



def TranslateGATMetaToPhysical(vtfContainer, metaBlockAddr, isBinary, FwConfigData):
    """
    Name : TranslateGATMetaToPhysical()

    Description :  This function calls "Read firmware parameters(0x65)", gives physical address for the given GAT meta block address.
    This Function is applicable for LARGE_MB / NON_LARGE_MB where GAT MB address passed is 32-bit Adress,hence not using "TranslateMetaToPhysical"

    Arguments :
              vtfContainer - vtfContainer Object
              metaBlockAddr - meta block address of GAT
              isBinary - mlc type
              FwConfigData - FwConfig object

    Returns :
             physicalAddress : physical address for the given meta block address of GAT
             sectorPositionInEccPage : sector position in ECC page

    opcode = 0x65

    subOpcode = 0x06
    """
    #constants
    BE_SPECIFIC_RLF_POSITION = 15 # 15th bit
    BE_SPECIFIC_GET_SECTOR_PART_IN_METABLK_ADDR = 0x7FFF

    #offsets
    READ_FW_CHIP_OFFSET = 0
    READ_FW_DIE_OFFSET = 1
    READ_FW_PLANE_OFFSET = 2
    READ_FW_BLOCK_OFFSET = 3
    READ_FW_PAGE_OFFSET = 5
    READ_FW_ECC_PAGE_OFFSET = 7

    commandName = "Read Firmware Parameter"
    opcode = 0x65
    subOpcode = 0x6

    #option is a two bit value
    #(bit 0 = 0 --> non Binary Block)
    #(bit 0 = 1 --> Binary Block)
    option = 2   #Initialize with 2 = bits (10)

    #Fix for FWBESIX-8208.
    #If the isBinary parameter is not passed appropriately
    #it might cause some failures. We need to be careful.
    if isBinary:
        option=3   #3 in binary is (11). Bit 0 = 1 and bit 1 = 1 ( bit 2,1 = 0,1 --> Wordline mlc Addresing mode)

    metaBlockAddr = int(metaBlockAddr)

    #The higher 4 digits (2 Bytes) denote the metablock number
    mbHighWord = ByteUtil.HighWord(metaBlockAddr)
    mbHighLsb = ByteUtil.LowByte(mbHighWord)
    mbHighMsb = ByteUtil.HighByte(mbHighWord)

    #The lower 4 digits (2 Bytes) denote the sector address
    mbLowWord = ByteUtil.LowWord(metaBlockAddr)
    sLowLsb = ByteUtil.LowByte(mbLowWord)
    sbLowMsb = ByteUtil.HighByte(mbLowWord)


    RLF = (metaBlockAddr & pow(2,BE_SPECIFIC_RLF_POSITION) ) >> BE_SPECIFIC_RLF_POSITION

    cdbData = [opcode, 0, subOpcode, int(mbHighLsb), int(mbHighMsb), int(sLowLsb), int(sbLowMsb), RLF, option, 0, 0, 0, 0, 0, 0, 0]

    configurationDataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: 0x%X, Data Direction: %s" %(opcode, subOpcode, READ_DATA))

    configurationDataBuffer = SendDiagnostic(vtfContainer, configurationDataBuffer, cdbData, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    physicalAddress = AddressTypes.PhysicalAddress()

    physicalAddress.chip = configurationDataBuffer.GetOneByteToInt(READ_FW_CHIP_OFFSET)
    physicalAddress.die = configurationDataBuffer.GetOneByteToInt(READ_FW_DIE_OFFSET )
    physicalAddress.plane = configurationDataBuffer.GetOneByteToInt(READ_FW_PLANE_OFFSET)
    physicalAddress.block = configurationDataBuffer.GetTwoBytesToInt(READ_FW_BLOCK_OFFSET)
    physicalAddress.wordLine = configurationDataBuffer.GetOneByteToInt(READ_FW_PAGE_OFFSET)
    physicalAddress.mlcLevel = configurationDataBuffer.GetOneByteToInt(READ_FW_PAGE_OFFSET+1)
    physicalAddress.eccPage = configurationDataBuffer.GetOneByteToInt(READ_FW_ECC_PAGE_OFFSET)

    sectorPositionInEccPage = (metaBlockAddr & MASK_UPPER_BYTE ) % FwConfigData.sectorsPerEccPage

    return physicalAddress,sectorPositionInEccPage
#end of TranslateGATMetaToPhysical


def TranslateMetaToPhysical(vtfContainer, metaBlockAddr, isBinary, FwConfigData, IsBiCS=1):
    """
    Name : TranslateMetaToPhysical()

    Description : This function calls "Read firmware parameters(0x65)", gives physical address for the given meta block address.

    Arguments :
              vtfContainer - vtfContainer Object
              metaBlockAddr - meta block address
              isBinary - mlc type
              FwConfigData - FwConfig object

    Returns :
             physicalAddress : physical address for the given meta block address
             sectorPositionInEccPage : sector position in ECC page

    opcode = 0x65

    subOpcode = 0x06
    """
    #constants
    BE_SPECIFIC_RLF_POSITION = 15 # 15th bit
    BE_SPECIFIC_GET_SECTOR_PART_IN_METABLK_ADDR = 0x7FFF

    #offsets
    if FwConfigData.isBiCS:
        #offsets
        READ_FW_CHIP_OFFSET = 0
        READ_FW_DIE_OFFSET = 1
        READ_FW_PLANE_OFFSET = 2
        READ_FW_BLOCK_OFFSET = 3
        READ_FW_WL_OFFSET = 5
        READ_FW_STRING_OFFSET = 6
        READ_FW_MLCLEVEL_OFFSET =  7
        READ_FW_ECC_PAGE_OFFSET = 8
    else:
        #offsets
        READ_FW_CHIP_OFFSET = 0
        READ_FW_DIE_OFFSET = 1
        READ_FW_PLANE_OFFSET = 2
        READ_FW_BLOCK_OFFSET = 3
        READ_FW_WL_OFFSET = 5
        READ_FW_ECC_PAGE_OFFSET = 7

    commandName = "Read Firmware Parameter"
    opcode = 0x65
    subOpcode = 0x6

    #option is a two bit value
    #(bit 0 = 0 --> non Binary Block)
    #(bit 0 = 1 --> Binary Block)
    option = 2   #Initialize with 2 = bits (10)

    #Fix for FWBESIX-8208.
    #If the isBinary parameter is not passed appropriately
    #it might cause some failures. We need to be careful.
    if isBinary:
        option=3   #3 in binary is (11). Bit 0 = 1 and bit 1 = 1 ( bit 2,1 = 0,1 --> Wordline mlc Addresing mode)

    metaBlockAddr = int(metaBlockAddr)

    if IsLargeMetablockUsed(vtfContainer)[0]:

        metaBlockNo = int(metaBlockAddr >> 32)#In place of Metablock Address ,FW Returns only Metablock Num
        SectorOffset = int(metaBlockAddr & 0xFFFFFFFF)

        RLF=0
        metaBlockNoLo_lowerByte = metaBlockNo & MASK_UPPER_BYTE
        metaBlockNo = metaBlockNo >> 8
        metaBlockNoLo_HigherByte = metaBlockNo & MASK_UPPER_BYTE
        metaBlockNo = metaBlockNo >> 8
        metaBlockNoHi_lowerByte = metaBlockNo & MASK_UPPER_BYTE
        metaBlockNo = metaBlockNo >> 8
        metaBlockNoHi_HigherByte = metaBlockNo & MASK_UPPER_BYTE

        sectorNoLo_lowerByte = SectorOffset & MASK_UPPER_BYTE
        SectorOffset = SectorOffset>>8
        sectorNoLo_HigherByte = SectorOffset & MASK_UPPER_BYTE
        SectorOffset = SectorOffset>>8
        sectorNoHi_lowerByte = SectorOffset & MASK_UPPER_BYTE
        SectorOffset = SectorOffset>>8
        sectorNoHi_HigherByte = SectorOffset & MASK_UPPER_BYTE

        cdbData = [ opcode, 0, subOpcode, metaBlockNoLo_lowerByte,metaBlockNoLo_HigherByte,
                    metaBlockNoHi_lowerByte,metaBlockNoHi_HigherByte,sectorNoLo_lowerByte,
                    sectorNoLo_HigherByte,sectorNoHi_lowerByte,sectorNoHi_HigherByte,
                  RLF,option, 0, 0,0]
    else:

        #The higher 4 digits (2 Bytes) denote the metablock number
        mbHighWord = ByteUtil.HighWord(metaBlockAddr)
        mbHighLsb = ByteUtil.LowByte(mbHighWord)
        mbHighMsb = ByteUtil.HighByte(mbHighWord)

        #The lower 4 digits (2 Bytes) denote the sector address
        mbLowWord = ByteUtil.LowWord(metaBlockAddr)
        sLowLsb = ByteUtil.LowByte(mbLowWord)
        sbLowMsb = ByteUtil.HighByte(mbLowWord)


        RLF = (metaBlockAddr & pow(2,BE_SPECIFIC_RLF_POSITION) ) >> BE_SPECIFIC_RLF_POSITION

        cdbData = [opcode, 0, subOpcode, int(mbHighLsb),
                   int(mbHighMsb), int(sLowLsb), int(sbLowMsb), RLF,
                   option, 0, 0, 0,
                 0, 0, 0, 0
                 ]

    configurationDataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: 0x%X, Data Direction: %s" %(opcode, subOpcode, READ_DATA))

    configurationDataBuffer = SendDiagnostic(vtfContainer, configurationDataBuffer, cdbData, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    physicalAddress = AddressTypes.PhysicalAddress()

    physicalAddress.chip = configurationDataBuffer.GetOneByteToInt(READ_FW_CHIP_OFFSET)
    physicalAddress.die = configurationDataBuffer.GetOneByteToInt(READ_FW_DIE_OFFSET )
    physicalAddress.plane = configurationDataBuffer.GetOneByteToInt(READ_FW_PLANE_OFFSET)
    physicalAddress.block = configurationDataBuffer.GetTwoBytesToInt(READ_FW_BLOCK_OFFSET)
    physicalAddress.wordLine = configurationDataBuffer.GetOneByteToInt(READ_FW_WL_OFFSET)
    if FwConfigData.isBiCS:
        physicalAddress.string = configurationDataBuffer.GetOneByteToInt(READ_FW_STRING_OFFSET)
        physicalAddress.mlcLevel = configurationDataBuffer.GetOneByteToInt(READ_FW_MLCLEVEL_OFFSET)
        physicalAddress.eccPage = configurationDataBuffer.GetOneByteToInt(READ_FW_ECC_PAGE_OFFSET)
    else:
        physicalAddress.mlcLevel = configurationDataBuffer.GetOneByteToInt(READ_FW_WL_OFFSET+1)
        physicalAddress.eccPage = configurationDataBuffer.GetOneByteToInt(READ_FW_ECC_PAGE_OFFSET)

    sectorPositionInEccPage = (metaBlockAddr & MASK_UPPER_BYTE ) % FwConfigData.sectorsPerEccPage

    return physicalAddress,sectorPositionInEccPage
#end of TranslateMetaToPhysical

def TranslateLogicalToPhy(vtfContainer, lba,IsBiCS=1):

    """
   Name : TranslateLogicalToPhy()

   Description : This function calls "Translate physical(0x87)", gives physical address for the given lba.

   Arguments :
             vtfContainer - vtfContainer Object
             lba - logical block address

   Returns :
            physicalAddress : physical address for the given lba

   opcode = 0x87

   """
    # Fix for SPARROW-822. Issuing diag immediately after powercycle leads to access violation error. Hence issuing dummy read.
    rdBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    if vtfContainer.isModel:
        readWithNoData = True
    else:
        readWithNoData = False

    # Fix for Sparrow-1053 (In case Dummy Read has UECC handle that)
    try:
        #card.ReadLba(1,1,rdBuf)
        SDWrap.ReadSingleBlock(1,bNoData=readWithNoData,szBuffer=rdBuf,blockLength=512)
    except:
        pass

    #offsets
    if IsBiCS:
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_CHIP_OFFSET = 0X11
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_DIE_OFFSET = 0X12
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_PLANE_OFFSET = 0X13
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_BLOCK_OFFSET = 0X14
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_WORDLINE_OFFSET = 0X16
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_STRING_OFFSET = 0x17
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_MLCLEVEL_OFFSET = 0X18
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_ECCPAGE_OFFSET = 0X19
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_IND1_OFFSET = 0x1A
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_MB_OFFSET = 0X1C
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_PRI_MB_WRITEOFFSET_OFFSET = 0X20
    else:
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_CHIP_OFFSET = 0X11
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_DIE_OFFSET = 0X12
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_PLANE_OFFSET = 0X13
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_BLOCK_OFFSET = 0X14
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_WORDLINE_OFFSET = 0X16
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_MLCLEVEL_OFFSET = 0X17
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_ECCPAGE_OFFSET = 0X18
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_IND1_OFFSET = 0X19
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_MB_OFFSET = 0X1C
        DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_PRI_MB_WRITEOFFSET_OFFSET = 0X20

    commandName = "Translate physical"
    opcode = 0x87
    readBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    physicalAddress = AddressTypes.PhysicalAddress()


    # This option value tells that returned address should be in wordLine/MLCLevel format.Refer chorus common diag for more details
    option = 0x0401
    optionLsb = ByteUtil.LowByte(option)
    optionMsb = ByteUtil.HighByte(option)
    lbaHighWord = ByteUtil.HighWord(lba)
    lbaLowWord = ByteUtil.LowWord(lba)
    lbaHighLsb = ByteUtil.LowByte(lbaHighWord)
    lbaHighMsb = ByteUtil.HighByte(lbaHighWord)
    lbaLowLsb = ByteUtil.LowByte(lbaLowWord)
    lbaLowMsb = ByteUtil.HighByte(lbaLowWord)

    #Form the CDB to send the Diagnostic Command

    cdbData = [opcode, 0, optionLsb, optionMsb,
               lbaLowLsb, lbaLowMsb, lbaHighLsb, lbaHighMsb,
               0,0,0,0,
              0,0,0,0 ]

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, Data Direction: %s" %(opcode, READ_DATA))
    readBuffer = SendDiagnostic(vtfContainer, readBuffer, cdbData, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    physicalAddress.chip = readBuffer.GetOneByteToInt(DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_CHIP_OFFSET)
    physicalAddress.die = readBuffer.GetOneByteToInt(DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_DIE_OFFSET)
    physicalAddress.plane = readBuffer.GetOneByteToInt(DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_PLANE_OFFSET)
    physicalAddress.block = readBuffer.GetTwoBytesToInt(DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_BLOCK_OFFSET)
    physicalAddress.wordLine = readBuffer.GetOneByteToInt(DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_WORDLINE_OFFSET)
    if IsBiCS:
        physicalAddress.string = readBuffer.GetOneByteToInt(DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_STRING_OFFSET)
    physicalAddress.mlcLevel = readBuffer.GetOneByteToInt(DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_MLCLEVEL_OFFSET)
    physicalAddress.eccPage  = readBuffer.GetOneByteToInt(DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_ECCPAGE_OFFSET)

    if ( readBuffer.GetOneByteToInt(DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_IND1_OFFSET) == 0):
        physicalAddress.isTrueBinaryBlock = False
    else:
        physicalAddress.isTrueBinaryBlock = True

    PriMB = readBuffer.GetFourBytesToInt(DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_MB_OFFSET)
    MBOffset = readBuffer.GetFourBytesToInt(DGN_ADDRESS_TRANSLATE_LBA_TO_PHY_PRI_MB_WRITEOFFSET_OFFSET)

    return physicalAddress, PriMB, MBOffset
#end of TranslateLogicalToPhy

def TranslateLBAtoMBA(vtfContainer, lba):
    """
    Name : TranslateLBAtoMBA()

    Description : This function calls "Get MML Data diag(0xC9)", gives meta block address for the given lba.

    Arguments :
              vtfContainer - vtfContainer Object
              lba - logical block address

    Returns :
             metaBlockAddr : logical block address for the given lba

    opcode = 0x87

    subOpcode = 0xa

    option=1
    """
    #offset
    LBA_TO_MBA_ADDRESS_OFFSET = 0

    commandName = "Get MML Data"
    mmlDataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    opcode = 0xC9
    subOpcode = 0xa
    option=1
    optionEx=lba
    bank=0

    cdbData = [opcode,subOpcode,option,0,
               ByteUtil.LowByte(ByteUtil.LowWord(optionEx)),ByteUtil.HighByte(ByteUtil.LowWord(optionEx)),
               ByteUtil.LowByte(ByteUtil.HighWord(optionEx)),ByteUtil.HighByte(ByteUtil.HighWord(optionEx)),
              0,0,bank,0,0,0,0,0]

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: 0x%X, Data Direction: %s" %(opcode, subOpcode, READ_DATA))

    mmlDataBuffer = SendDiagnostic(vtfContainer, mmlDataBuffer, cdbData, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    if IsLargeMetablockUsed(vtfContainer)[0]:
        #Returns 64 Bit Address instead of 32 bit address
        metaBlockAddr = mmlDataBuffer.GetEightBytesToInt(LBA_TO_MBA_ADDRESS_OFFSET)
    else:
        metaBlockAddr = mmlDataBuffer.GetFourBytesToInt(LBA_TO_MBA_ADDRESS_OFFSET)

    return metaBlockAddr
#end of TranslateLBAtoMBA

def GetListOfRoFiles(vtfContainer):
    """
    Name : GetListOfRoFiles()

    Description : This function calls "Get FIle List diag(0x88)", gives list of Read Only Files list from the file system.

    Arguments :
              vtfContainer - vtfContainer Object

    Returns :
             roFileList : Read Only Files from the file system

    opcode = 0x88

    option = 0
    """
    commandName = "Get List of Read only Files"
    opcode = 0x88
    configurationDataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR, 0)
    bytesPerSector = 512
    option = 0
    roFileList = []
    opcodeLo = ByteUtil.LowByte(opcode)
    opcodeHi = ByteUtil.HighByte(opcode)

    optionLo = ByteUtil.LowByte(option)
    optionHi = ByteUtil.HighByte(option)

    cdb = [opcodeLo,opcodeHi,optionLo,optionHi,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0 ]

    configurationDataBuffer =  SendDiagnostic(vtfContainer, configurationDataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    for offset in range(0, bytesPerSector):
        #Getting the file number of the file
        fileNo=configurationDataBuffer.GetOneByteToInt(offset)
        if fileNo==0x00:
            break
        else:
            roFileList.append(fileNo)

    return roFileList
#end of GetListOfRoFiles


def GetCMCRegisterValue(vtfContainer):

    commandName = "GetCMCRegisterValue"
    opcode    = 0x65
    SubOpcode = 0x0C
    cmcRegBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR, 0)

    cdb = [opcode,0,SubOpcode,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0 ]

    cmcRegBuffer =  SendDiagnostic(vtfContainer, cmcRegBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    return cmcRegBuffer


def CallStartRecording(vtfContainer):
    """
    # Harish - 12-Jun-16,
    # Changed direction from 1 to NO_DATA, as per the mail from Ravi Gaja
    # reason being
    # This change was causing a model hang, coz host was expecting some data from startrecording.
    # But we dont return any data here. Thats why I changed the function to no_data mode.
    """
    opcode = 0xD3
    subOpcode = 0x0
    readBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,0)
    cdb = [opcode,subOpcode,0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0 ]
    direction = 1
    # Harish - 12 jun 16
    # changed from 1 to NO_DATA mode
    direction = NO_DATA
    readBuffer = SendDiagnostic(vtfContainer, readBuffer, cdb, direction, SINGLE_SECTOR)

    return readBuffer

def CallCreateDir(vtfContainer):
    opcode = 0xD3
    subOpcode = 0x1
    readBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,0)
    cdb = [opcode,subOpcode,0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0 ]
    direction = 1

    readBuffer = SendDiagnostic(vtfContainer, readBuffer, cdb, direction, SINGLE_SECTOR, opcode)
    return readBuffer

def CallUpdateCi(vtfContainer):
    import time
    opcode = 0xD3
    subOpcode = 0x2
    readBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,0)
    cdb = [opcode,subOpcode,0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0 ]
    direction = 1
    #time.sleep(0.25)

    readBuffer = SendDiagnostic(vtfContainer, readBuffer, cdb, direction, SINGLE_SECTOR, opcode)
    return readBuffer

def CallSuspendAu(vtfContainer):
    opcode = 0xD3
    subOpcode = 0x3
    readBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,0)
    cdb = [opcode,subOpcode,0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0 ]
    direction = 1



    readBuffer = SendDiagnostic(vtfContainer, readBuffer, cdb, direction, SINGLE_SECTOR, opcode)
    return readBuffer

def CallResumeAu(vtfContainer):
    import time
    opcode = 0xD3
    subOpcode = 0x4
    readBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,0)
    cdb = [opcode,subOpcode,0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0 ]
    direction = 1


    readBuffer = SendDiagnostic(vtfContainer, readBuffer, cdb, direction, SINGLE_SECTOR, opcode)
    return readBuffer

def CallSetFreeAu(vtfContainer,startau=0,count=1):
    opcode = 0xD3
    subOpcode = 0x5
    readBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,0)
    optionEx=startau

    cdbData = [opcode,subOpcode,
               ByteUtil.LowByte(ByteUtil.LowWord(optionEx)),ByteUtil.HighByte(ByteUtil.LowWord(optionEx)),ByteUtil.LowByte(ByteUtil.HighWord(optionEx)),ByteUtil.HighByte(ByteUtil.HighWord(optionEx)),
               count,0,0,0,0,0,0,0,0,0,0,0]

    direction = 1

    #time.sleep(0.25)

    readBuffer = SendDiagnostic(vtfContainer, readBuffer, cdbData, direction, SINGLE_SECTOR, opcode)
    return readBuffer


def GetMConf(vtfContainer):
    """
    Returns MConf Buffer
    Generic SendDiagnostic command,Executes the Diagnostic command
    Author : Venkat Krishna Date: 08/28/2014
    GetMConf returns the MConf Buffer from the Card.
    """
    opCode = 0x9A
    subOpCode = 0x1
    # 16 number list - Command buffer

    cdb = [opCode,0,subOpCode,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    mConfBuf = pyWrap.Buffer.CreateBuffer(1,0)

    try:
        SendDiagnostic(vtfContainer, mConfBuf, cdb, READ_DATA, SINGLE_SECTOR, opCode)
        vtfContainer.GetLogger().Info("", "[Diagnostic] Opcode: 0x%X SubOpcode 0x%X\n" %(opCode,subOpCode))

    except Exception as exc:
        vtfContainer.GetLogger().Info("", "[Diagnostic command Failed] Opcode: 0x%X SubOpcode 0x%X\n" %(opCode,subOpCode))
        vtfContainer.GetLogger().Info("", "%s" %exc)
    #mConfBuf.Dump()
    return mConfBuf

def CallReleaseDir(vtfContainer):
    import time
    opcode = 0xD3
    subOpcode = 0x6
    readBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,0)
    cdb = [opcode,subOpcode,0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0 ]
    direction = 1
    #time.sleep(0.05)

    readBuffer = SendDiagnostic(vtfContainer, readBuffer, cdb, direction, SINGLE_SECTOR, opcode)
    return readBuffer


def CheckSanityDiag(vtfContainer):
    commandName = "GetCMCRegisterValue"
    opcode      = 0xA8
    SubOpcode   = 0x00
    statusBuff  = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR, 0)

    cdb = [opcode,SubOpcode,0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0 ]

    statusBuff =  SendDiagnostic(vtfContainer, statusBuff, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    return statusBuff





def GetListOfRwFiles(vtfContainer):
    """
    Name : GetListOfRwFiles()

    Description : This function calls "Get FIle List diag(0x88)", gives list of Read write Files list from the file system.

    Arguments :
              vtfContainer - vtfContainer Object

    Returns :
             rwFileList : Read write Files from the file system

    opcode = 0x88

    option = 1
    """
    commandName = "Get List of Read Write Files"
    opcode = 0x88
    configurationDataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR, 0)
    bytesPerSector = 512
    option = 1
    rwFileList = []
    opcodeLo = ByteUtil.LowByte(opcode)
    opcodeHi = ByteUtil.HighByte(opcode)

    optionLo = ByteUtil.LowByte(option)
    optionHi = ByteUtil.HighByte(option)

    cdb = [opcodeLo,opcodeHi,optionLo,optionHi,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0 ]

    configurationDataBuffer =  SendDiagnostic(vtfContainer, configurationDataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    for offset in range(0, bytesPerSector):
        #Getting the file number of the file
        fileNo=configurationDataBuffer.GetOneByteToInt(offset)
        if fileNo==0x00:
            break
        else:
            rwFileList.append(fileNo)
    #Just for debugging only(Temporary Fix)
    rwFileList.remove(42)

    return rwFileList
#end of GetListOfRwFiles

def GetListOfAllFiles(vtfContainer):
    """
    Name : GetListOfAllFiles()

    Description : This function calls "Get FIle List diag(0x88)", gives list of All Files list from the file system.

    Arguments :
              vtfContainer - vtfContainer Object

    Returns :
             allFileList : All Files from the file system
    opcode : 0x88

    option = 2
    """
    commandName = "Get List of All Files"
    opcode = 0x88
    configurationDataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR, 0)
    bytesPerSector = 512
    option = 2
    allFileList = []
    opcodeLo = ByteUtil.LowByte(opcode)
    opcodeHi = ByteUtil.HighByte(opcode)

    optionLo = ByteUtil.LowByte(option)
    optionHi = ByteUtil.HighByte(option)

    cdb = [opcodeLo,opcodeHi,optionLo,optionHi,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0 ]

    configurationDataBuffer =  SendDiagnostic(vtfContainer, configurationDataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    for offset in range(0, bytesPerSector):
        #Getting the file number of the file
        fileNo=configurationDataBuffer.GetOneByteToInt(offset)
        if fileNo==0x00:
            break
        else:
            allFileList.append(fileNo)

    return allFileList
#end of GetListOfAllFiles

def GetRSPending(vtfContainer):
    """
    Name:                   GetRSPending

    Description:            Gets the number of Pending copy and Pending Scan entries
    Arguments:
        vtfContainer:          Card Test Space

    Returns:
       pendingCopy          The number of pending copy entries
       pendingScan          The number of pending scan entries
    """
    #logger=vtfContainer.GetLogger()

    mmlDataBuffer = pyWrap.Buffer.CreateBuffer(DIAG_SECTORLENGTH,0)
    opcode = GET_MML_DATA
    subOpcode = GET_RS_QUEUE_SUBOPCODE
    option=1
    cdbData = [opcode,subOpcode,option,0,0,0,0,0,0,0,0,0,0,0,0,0]
    direction = READ_DATA

    SendDiagnostic(vtfContainer, mmlDataBuffer , cdbData , direction , DIAG_SECTORLENGTH, opcode)

    pendingCopyOffset=0
    pendingScanOffset=1
    pendingCopy=mmlDataBuffer.GetOneByteToInt(pendingCopyOffset)
    pendingScan=mmlDataBuffer.GetOneByteToInt(pendingScanOffset)

    return pendingCopy,pendingScan
#end of GetRSPending

def GetRS_StatisticCounters(vtfContainer):
    """
    Name:                   GetRS_StatisticCounters

    Description:            Get the read scrub statistic counters
    Arguments:
        vtfContainer:          Card Test Space
    Returns:
       counter{}            A dictionary containing all the RS counters
    """
    #logger=vtfContainer.GetLogger()

    counter={}
    mmlDataBuffer = pyWrap.Buffer.CreateBuffer(DIAG_SECTORLENGTH,0)

    opcode = GET_MML_DATA
    subOpcode = GET_RS_QUEUE_SUBOPCODE
    option=2
    cdbData = [opcode,subOpcode,option,0,0,0,0,0,0,0,0,0,0,0,0,0]
    direction = READ_DATA

    SendDiagnostic(vtfContainer, mmlDataBuffer , cdbData , direction , DIAG_SECTORLENGTH, opcode)

    offset=0
    counter["RemovedFromRSQueueCount"]=mmlDataBuffer.GetFourBytesToInt(offset)
    counter["RSBlocksConvertedFromScanToCopy"]=mmlDataBuffer.GetFourBytesToInt(offset+4)
    counter["FileSystemBlocksCopyPerformed"]=mmlDataBuffer.GetFourBytesToInt(offset+8)
    counter["ScannedCount"]=mmlDataBuffer.GetFourBytesToInt(offset+12)
    counter["MLCBlocksCopied"]=mmlDataBuffer.GetFourBytesToInt(offset+16)
    counter["SLCBlocksCopied"]=mmlDataBuffer.GetFourBytesToInt(offset+20)


    return counter
#end of GetRS_StatisticCounters

def GetSecondaryBlocks(vtfContainer):
    NUM_OF_AVAILABLE_MB_OFFSET = 0
    opcode=0xC9
    subOpcode = 0x36
    commandName = "Get MML Data"
    cdb = [opcode,subOpcode,0,0,0,0
           ,0,0,0,0
           ,0,0,0,0,0,0]
    readBuffer = pyWrap.Buffer.CreateBuffer(1)
    SendDiagnostic(vtfContainer, readBuffer, cdb, 0, 1, opcode, commandName)
    listOfSecondaryBlocks = []

    ByteToRead = 0x0
    BlockAddress = 0x0
    temporaryBuffer = 0x0
    secondaryBlockCount = 0
    while (temporaryBuffer != 0xff7f):
        temporaryBuffer = readBuffer.GetTwoBytesToInt(ByteToRead)
        High = ByteUtil.HighByte(temporaryBuffer)
        Low = ByteUtil.LowByte(temporaryBuffer)

        BlockAddress = Low*256 + High

        listOfSecondaryBlocks.append(BlockAddress)
        ByteToRead +=0x2
        secondaryBlockCount += 1

    del listOfSecondaryBlocks[secondaryBlockCount-1]
    return  listOfSecondaryBlocks

def GetRSQueue(vtfContainer,bank=0):
    """
    Name:                   GetRSQueue

    Description:            Checks if the give metablock is available in the RS queue with the expected entry
    Arguments:     
        vtfContainer:          Card Test Space      

    Returns:
       rsqueue[]            A list containing all the valid metablocks and its flag in the RS queue   
    """
    #logger=vtfContainer.GetLogger()

    rsqueue = []

    mmlDataBuffer = pyWrap.Buffer.CreateBuffer(DIAG_SECTORLENGTH, 0) 
    opcode = GET_MML_DATA
    subOpcode = 2
    option=0
    cdbData = [opcode,subOpcode,option,0,0,0,0,0,0,0,bank,0,0,0,0,0]
    direction = READ_DATA

    mmlDataBuffer = SendDiagnostic(vtfContainer, mmlDataBuffer , cdbData , direction , DIAG_SECTORLENGTH, opcode)


    blockinfo = mmlDataBuffer.GetFourBytesToInt(124)
    flag_info =  mmlDataBuffer.GetFourBytesToInt(128)
    if flag_info == 1:
        mb = blockinfo & 0x1FFFFFF
        planeNo = blockinfo >> 26
        rsqueue.append([mb, planeNo])

    return rsqueue
#end of GetRSQueue

def ReadChipDeviceId(vtfContainer):
    """
    Name : ReadChipDeviceId()

    Description : This function calls "Read Chip Device Id diag(0x88)", gives Device Id.

    Arguments :
              vtfContainer - vtfContainer Object

    Returns :
             configParams : dictionary having device id

    opcode = 0x8E
    """
    #offsets
    ID_INFO_FROM_NAND_OFFSET = 0x00
    EXT_INFO_ID_FROM_NAND_OFFSET = 0x08

    commandName = "Read Chip Device Id"
    opcode = 0x8E
    chip = 0

    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    cdb = [opcode, chip, 0,0,
           0,0,0,0,
           1,0,0,0,
          0,0,0,0]

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X,  Data Direction: %s" %(opcode,READ_DATA))
    dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    configParams = {"idInfoFromNand":None, "extendedIdInfoFromNand":None}

    configParams["idInfoFromNand"] = dataBuffer.GetEightBytesToInt(ID_INFO_FROM_NAND_OFFSET)
    configParams["extendedIdInfoFromNand"] = dataBuffer.GetEightBytesToInt(EXT_INFO_ID_FROM_NAND_OFFSET)

    return configParams
#enf of ReadChipDeviceId

def DoBackGroundMaintenanceOperations(vtfContainer, function = None):
    """
    Name : DoBackGroundMaintenanceOperations

    Description : Suspend or resume the backGround Maitenance operations

    Arguments:
       vtfContainer : Card vtfContainer object
       function : 0 - suspend
                  1 - resume
                  [None]
    Returns:
            None

    opcode : 0xBC

    """

    if function == None:
        raise TestError.TestFailError(vtfContainer.GetTestName(), "[DoBackGroundMaintenanceOperations] Invalid function option provided - None\n"
                                      " Should be either:\n 0 - suspend\n or\n 1 - resume")

    opcode = 0xBC
    if function == 0:
        vtfContainer.GetLogger().Info("", 'Suspending the back ground maintenance operations')
    elif function == 1:
        vtfContainer.GetLogger().Info("", 'Resuminging the back ground maintenance operations')

    cdb = [opcode, function, 0, 0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    commandName = "DoBackGroundMaintenanceOperations"

    #???? Defining the data buffer to None
    dataBuffer = pyWrap.Buffer.CreateBuffer(1)
    direction = NO_DATA
    sectors = 0
    SendDiagnostic(vtfContainer, dataBuffer, cdb, direction, sectors, opcode, commandName)
#End of DoBackGroundMaintenanceOperations()

def StoreCountersToFile232(vtfContainer):
    """
    Name : StoreCountersToFile232

    Description : Stores Counters to the File#232

    Arguments:
       vtfContainer : Card vtfContainer object

    Returns:
            None

    opcode : 0xBD
    """
    commandName = "Store Counters to file #232"

    opcode = 0xBD
    cdb = [opcode,0,0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    statusBuffer= pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)# status buffer

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, Data Direction: %s" %(opcode, READ_DATA))
    mmlDataBuffer = SendDiagnostic(vtfContainer, statusBuffer, cdb, NO_DATA, SINGLE_SECTOR, opcode, commandName)
#end of StoreCountersToFile232

def ClearContentsOfFile232(vtfContainer):
    """
    Name : ClearContentsOfFile232

    Description :Clears contents of File#232

    Arguments:
       vtfContainer : Card vtfContainer object

    Returns:
            None

    opcode : 0xBE
    """
    commandName = "Clear Contents Of File 232"
    opcode = 0xBE

    cdb = [opcode,0,0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    statusBuffer= pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)# status buffer
    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, Data Direction: %s" %(opcode, READ_DATA))
    mmlDataBuffer = SendDiagnostic(vtfContainer, statusBuffer, cdb, NO_DATA, SINGLE_SECTOR, opcode, commandName)
    return
#End of ClearContentsOfFile232

def GetGatCacheInfo(vtfContainer):
    """
    Name : GetGatInfo()

    Description : This function calls "Get MML Data diag(0x88)", gives GAT infor.

    Arguments :
              vtfContainer - vtfContainer Object

    Returns :
             gatAddressTypesObj : GAT block Physical address
             bcAddressTypesObj : Binary Cache block Physical address

    opcode : 0xC9

    subopcode : 1

    """
    MML_DATA_BUFFER_SIZE = 19 #Sectors
    commandName = "Get GAT Cache Info"
    opcode = 0xC9
    subOpcode = 1

    cdb = [opcode, subOpcode, 0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    commandName = "GET MML DATA"
    mmlParametersData = pyWrap.Buffer.CreateBuffer(MML_DATA_BUFFER_SIZE)

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode : %s ,Data Direction: %s" %(opcode, subOpcode, READ_DATA))
    mmlDataBuffer = SendDiagnostic(vtfContainer, mmlParametersData, cdb, READ_DATA, MML_DATA_BUFFER_SIZE, opcode, commandName)

    return mmlDataBuffer

#----------------------------------------------------------------------
def GetGatVFCcount(vtfContainer):
    """
    Name : GetGatInfo()

    Description : This function calls "Get MML Data diag(0x88)", gives GAT infor.

    Arguments :
              vtfContainer - vtfContainer Object

    Returns :
             gatAddressTypesObj : GAT block Physical address
             bcAddressTypesObj : Binary Cache block Physical address

    opcode : 0xC9

    subopcode : 1

    """
    commandName = "Get GAT VFC count"
    opcode = 0xC9
    subOpcode = 0x2E
    NumOFGatBlocks=ReadMmlParameters(vtfContainer)["numGatBlocks"]
    offset=0
    ListofGatBlocksVFC=[]

    cdb = [opcode, subOpcode, 0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    commandName = "GET MML DATA"
    mmlParametersData = pyWrap.Buffer.CreateBuffer(4)

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode : %s ,Data Direction: %s" %(opcode, subOpcode, READ_DATA))
    mmlDataBuffer = SendDiagnostic(vtfContainer, mmlParametersData, cdb, READ_DATA, 4, opcode, commandName)

    for blk in range(0,NumOFGatBlocks):
        BlkNum=mmlDataBuffer.GetTwoBytesToInt(offset)
        VFC=mmlDataBuffer.GetTwoBytesToInt(offset+2)
        ListofGatBlocksVFC.append((BlkNum,VFC))
        offset=offset+4

    return ListofGatBlocksVFC
#----------------------------------------------------------------------

def  GetGatPhysicalAddress(vtfContainer, FwConfigData):
    mmlDataBuffer=GetGatCacheInfo(vtfContainer)
    #offsets
    GAT_PHY_ADDRESS_DIE_OFFSET = 0x00
    GAT_PHY_ADDRESS_PLANE_OFFSET = 0x01
    GAT_PHY_ADDRESS_BLOCK_OFFSET = 0x02
    GAT_PHY_ADDRESS_SECTOR_OFFSET = 0x05

    # Commenting BC Block section as FW MML data structure is changed and BC block is removed
    #BC_BLOCK_PHY_ADDRESS_DIE_OFFSET = 0x06
    #BC_BLOCK_PHY_ADDRESS_PLANE_OFFSET = 0x07
    #BC_BLOCK_PHY_ADDRESS_BLOCK_OFFSET = 0x08
    #BC_BLOCK_PHY_ADDRESS_SECTOR_OFFSET = 0x0b

    #GAT physical address
    gatAddressTypesObj = AddressTypes.SectorBasedPhysicalAddress()
    chipDieNumber = mmlDataBuffer.GetOneByteToInt(GAT_PHY_ADDRESS_DIE_OFFSET)
    gatAddressTypesObj.chip = chipDieNumber >> (FwConfigData.log2DiesPerChip)
    gatAddressTypesObj.die = chipDieNumber & (FwConfigData.diesPerChip - 1)
    gatAddressTypesObj.plane = mmlDataBuffer.GetOneByteToInt(GAT_PHY_ADDRESS_PLANE_OFFSET)
    gatAddressTypesObj.block = mmlDataBuffer.GetTwoBytesToInt(GAT_PHY_ADDRESS_BLOCK_OFFSET)
    gatAddressTypesObj.sector = mmlDataBuffer.GetTwoBytesToInt(GAT_PHY_ADDRESS_SECTOR_OFFSET)

    #BC block physical address
    #bcAddressTypesObj = AddressTypes.SectorBasedPhysicalAddress()
    #bcAddressTypesObj.die = mmlDataBuffer.GetOneByteToInt(BC_BLOCK_PHY_ADDRESS_DIE_OFFSET)
    #bcAddressTypesObj.plane = mmlDataBuffer.GetOneByteToInt(BC_BLOCK_PHY_ADDRESS_PLANE_OFFSET)
    #bcAddressTypesObj.block = mmlDataBuffer.GetOneByteToInt(BC_BLOCK_PHY_ADDRESS_BLOCK_OFFSET)
    #bcAddressTypesObj.sector = mmlDataBuffer.GetOneByteToInt(BC_BLOCK_PHY_ADDRESS_SECTOR_OFFSET)

    return gatAddressTypesObj, 0

#end of GetGatInfo

def MMP_FBL_Info(vtfContainer):  # Free block list Info

    opcode = 0xC9
    subOpcode = 0x14
    commandName = "MMP FBL Info"

    cdb = [ opcode, subOpcode, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
           0, 0, 0, 0
              ]

    Buff = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    Buff = SendDiagnostic(vtfContainer, Buff, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    MMP_FBL_Info_Params = {"SLC_FBL_CAPACITY":None, "SLC_FBL_COUNT_MP0":None, "SLC_FBL_COUNT_MP1":None, "Size_of_Element_in_SLC_List":None, "free_blocks_in_the_SLC_FBL_MP0":None,  "free_blocks_in_the_SLC_FBL_MP1":None, \
                           "MLC_FBL_CAPACITY":None, "MLC_FBL_COUNT":None, "Size_of_Element_in_MLC_List":None, "List_of_all_free_blocks_in_the_MLC_FBL_of_both_metaplanes":None }

    SLC_FBL_CAPACITY = Buff.GetTwoBytesToInt(0)
    SLC_FBL_COUNT_MP0 = Buff.GetTwoBytesToInt(2)
    #SLC_FBL_COUNT_MP1 = Buff.GetTwoBytesToInt(4)
    #Size_of_Element_in_SLC_List = Buff.GetTwoBytesToInt(6)
    #Addr_free_blocks_in_the_SLC_FBL_MP0 = 8
    #Addr_free_blocks_in_the_SLC_FBL_MP1 = 148

    #SLC_FBL_MP0_list = []
    #SLC_FBL_MP1_list = []
    #SLC_FBL_list = []

    #for index in range(0,SLC_FBL_COUNT_MP0 ):
        #SLC_FBL_MP0_list.append(Buff.GetTwoBytesToInt(Addr_free_blocks_in_the_SLC_FBL_MP0 + (index*Size_of_Element_in_SLC_List)))
        #SLC_FBL_list.append(Buff.GetTwoBytesToInt(Addr_free_blocks_in_the_SLC_FBL_MP0 + (index*Size_of_Element_in_SLC_List)))

    #for index in range(0,SLC_FBL_COUNT_MP1 ):
        #SLC_FBL_MP1_list.append(Buff.GetTwoBytesToInt(Addr_free_blocks_in_the_SLC_FBL_MP1 + (index*Size_of_Element_in_SLC_List)))
        #SLC_FBL_list.append(Buff.GetTwoBytesToInt(Addr_free_blocks_in_the_SLC_FBL_MP1 + (index*Size_of_Element_in_SLC_List)))

    #MLC_FBL_CAPACITY = Buff.GetTwoBytesToInt(288)
    #MLC_FBL_COUNT = Buff.GetTwoBytesToInt(290)
    #Size_of_Element_in_MLC_List = Buff.GetTwoBytesToInt(292)
    #Addr_free_blocks_in_the_MLC_FBL_of_both_metaplanes = 294

    #MLC_FBL_list = []
    #listOfDedicatedFBLMetaBlocks = []

    #for index in range(0,MLC_FBL_COUNT ):
        #MLC_FBL_list.append(Buff.GetFourBytesToInt(Addr_free_blocks_in_the_MLC_FBL_of_both_metaplanes + (index*Size_of_Element_in_MLC_List)))

    #FS_FBL_CAPACITY = Buff.GetTwoBytesToInt(374)
    #FS_FBL_COUNT = Buff.GetTwoBytesToInt(376)
    #Size_of_Element_in_FS_List = Buff.GetTwoBytesToInt(378)
    #Addr_FS_FBL_of_both_metaplanes = 380

    #for index in range(0,FS_FBL_COUNT ):
        #listOfDedicatedFBLMetaBlocks.append(Buff.GetFourBytesToInt(Addr_FS_FBL_of_both_metaplanes + (index*Size_of_Element_in_FS_List)))

    #totalSpareBlockCount = MLC_FBL_COUNT + SLC_FBL_COUNT_MP0 + SLC_FBL_COUNT_MP1

    #return totalSpareBlockCount, SLC_FBL_list, MLC_FBL_list, listOfDedicatedFBLMetaBlocks, SLC_FBL_MP0_list, SLC_FBL_MP1_list
    return SLC_FBL_CAPACITY, SLC_FBL_COUNT_MP0

def GetSpareBlocksForSLCAndMLC(vtfContainer):
    """
    Name       :   GetSpareBlockCount
    Description:   Get the Spare Block Spare Block Count and return the same.
    Arguments  :
                   None
    Returns    :
        SpareBlockCount - Number of spare blocks present in the card/model.
    """
    #offsets
    import FwConfig, FileData
    fwCnfObj = FwConfig.FwConfig(vtfContainer)
    file14 = FileData.GetFile14Data(vtfContainer)
    mlcGrownDefects = file14["mlcGrownDefects"] * fwCnfObj.numberOfMetaPlane

    TOTAL_NUM_OF_SPARE_BLOCK_COUNT_SLC = 0x0
    TOTAL_NUM_OF_SPARE_BLOCK_COUNT_MLC = TOTAL_NUM_OF_SPARE_BLOCK_COUNT_SLC + 0x2
    TOTAL_NUM_OF_SPARE_BLOCK_COUNT_CARD = TOTAL_NUM_OF_SPARE_BLOCK_COUNT_MLC + 0x2
    SLC_SPARE_PER_METAPLANE_OFFSET = TOTAL_NUM_OF_SPARE_BLOCK_COUNT_CARD + 0x2
    MLC_SPARE_PER_METAPLANE_OFFSET = (SLC_SPARE_PER_METAPLANE_OFFSET+fwCnfObj.numberOfMetaPlane)
    getSpareBlockDataBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    opcode = 0xC9
    subOpcode = 65
    commandName   = "GET SPARE BLOCK COUNT"
    cdb = [opcode, subOpcode, 0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    getSpareBlockDataBuf = SendDiagnostic(vtfContainer, getSpareBlockDataBuf,cdb,READ_DATA,SINGLE_SECTOR,opcode, commandName)
    numOfSpareBlock_SLC = getSpareBlockDataBuf.GetTwoBytesToInt(TOTAL_NUM_OF_SPARE_BLOCK_COUNT_SLC)
    numOfSpareBlock_MLC = getSpareBlockDataBuf.GetTwoBytesToInt(TOTAL_NUM_OF_SPARE_BLOCK_COUNT_MLC)
    numOfSpareBlock_CARD = getSpareBlockDataBuf.GetTwoBytesToInt(TOTAL_NUM_OF_SPARE_BLOCK_COUNT_CARD)
    numOfSpareBlock_SLC_PerMetaplane = []
    numOfSpareBlock_MLC_PerMetaplane = []

    subOffset = 0
    for mmp in range(fwCnfObj.numberOfMetaPlane):
        offset_SLC = SLC_SPARE_PER_METAPLANE_OFFSET + subOffset
        offset_MLC = MLC_SPARE_PER_METAPLANE_OFFSET + subOffset
        numOfSpareBlock_SLC_PerMetaplane.append(getSpareBlockDataBuf.GetOneByteToInt(offset_SLC))
        numOfSpareBlock_MLC_PerMetaplane.append(getSpareBlockDataBuf.GetOneByteToInt(offset_MLC))
        subOffset += 1

    sumOfSpareCountSLC = 0
    for spareCount in numOfSpareBlock_SLC_PerMetaplane:
        sumOfSpareCountSLC += spareCount

    if sumOfSpareCountSLC != numOfSpareBlock_SLC:
        vtfContainer.GetLogger().Error("", "[Test: Error] Sum of SLC spares in all metaplanes: %d, num of SLC spares in card: %d"%(sumOfSpareCountSLC, numOfSpareBlock_SLC))
        raise TestError.TestFailError(vtfContainer.GetTestName(), "Mismatch in the SLC spare block count returned by the diag GetSpareBlocksForSLCAndMLC")

    sumOfSpareCountMLC = 0
    for spareCount in numOfSpareBlock_MLC_PerMetaplane:
        sumOfSpareCountMLC += spareCount

    if sumOfSpareCountMLC != numOfSpareBlock_MLC-mlcGrownDefects:
        vtfContainer.GetLogger().Error("", "[Test: Error] Sum of MLC spares in all metaplanes: %d, num of MLC spares in card: %d, mlc spares reserved for GBBs: %d x %d = %d"%(sumOfSpareCountMLC, numOfSpareBlock_MLC, file14["mlcGrownDefects"], fwCnfObj.numberOfMetaPlane, mlcGrownDefects))
        raise TestError.TestFailError(vtfContainer.GetTestName(), "Mismatch in the MLC spare block count returned by the diag GetSpareBlocksForSLCAndMLC")

    returnval = [numOfSpareBlock_CARD,numOfSpareBlock_SLC,numOfSpareBlock_MLC, numOfSpareBlock_SLC_PerMetaplane, numOfSpareBlock_MLC_PerMetaplane]
    vtfContainer.GetLogger().Info("", "Num of SLC spares = %d, Num of MLC spares = %d, Total spares in entire card = %d, SLC per metaplane spare count: %s, MLC per metaplane spare count: %s"%(numOfSpareBlock_SLC, numOfSpareBlock_MLC, numOfSpareBlock_CARD, numOfSpareBlock_SLC_PerMetaplane, numOfSpareBlock_MLC_PerMetaplane))
    if (numOfSpareBlock_SLC + numOfSpareBlock_MLC != numOfSpareBlock_CARD):
        raise TestError.TestFailError(vtfContainer.GetTestName(), "Diag Issue: Sum of SLC and MLC spares is not matching with total spares in card")
    return returnval
#end of GetSpareBlockCount

def ReadScrubInfoOption0(vtfContainer):
    """
    Name : ReadScrubInfoOption0()

    Description : This function calls "Get MML Data diag(0xC9)", gives read scrub info.

    Arguments :
              vtfContainer - vtfContainer Object

    Returns :
             configParams : dictionary of Read Scrub info(such as "Queue entires", "read scrub flag" and so on)

    opcode : 0xC9

    subopcode : 2

    option : 0
    """
    #offsets
    RS_QUEUE_ENTRIES_OFFSET = 0x00
    RS_FLAG_OFFSET = 0x10
    RS_NUM_PENDING_COPIES = 0x12
    RS_NUM_PENDING_SCANS_OFFSET = 0x13
    RS_STATUS_OFFSET = 0x14
    RS_MIP_SAVE_REQUIRED_OFFSET = 0x15

    commandName = "Read Scrub data"
    opcode = 0xC9
    subOpcode = 2
    option = 0
    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    cdb = [opcode, subOpcode, option, 0,
           0, 0, 0, 0,
           0, 0, 0, 0,
          0, 0, 0, 0]

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, READ_DATA))
    getMMLDataBuf = SendDiagnostic(vtfContainer,dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    configParams = {"readScrubQueueEntries":None, "readScurbFlag":None, "rsNumPendingCopies":None,
                    "rsNumPendingScans":None, "readScrubStatus":None, "rsMipSaveRequired":None}

    configParams["readScrubQueueEntries"] = dataBuffer.GetTwoBytesToInt(RS_QUEUE_ENTRIES_OFFSET)
    configParams["readScurbFlag"] = dataBuffer.GetTwoBytesToInt(RS_FLAG_OFFSET)
    configParams["rsNumPendingCopies"] = dataBuffer.GetOneByteToInt(RS_NUM_PENDING_COPIES)
    configParams["rsNumPendingScans"] = dataBuffer.GetOneByteToInt(RS_NUM_PENDING_SCANS_OFFSET)
    configParams["readScrubStatus"] = dataBuffer.GetOneByteToInt(RS_STATUS_OFFSET)
    configParams["rsMipSaveRequired"] = dataBuffer.GetOneByteToInt(RS_MIP_SAVE_REQUIRED_OFFSET)

    return configParams
#end of ReadScrubInfoOption0

def ReadScrubInfoOption2(vtfContainer):
    """
    Name : ReadScrubInfoOption2()

    Description : This function calls "Get MML Data diag(0xC9)", gives read scrub info.

    Arguments :
              vtfContainer - vtfContainer Object

    Returns :
             configParams : dictionary of Read Scrub info(such as "read scrub removed from queue count", "read scrub scan converted to copy count" and so on)

    opcode : 0xC9

    subopcode : 2

    option : 2
    """
    #offsets
    RS_REMOVE_FROM_QUEUE_COUNT_OFFSET = 0x00
    RS_SCAN_CONVERTED_TO_COPY_COUNT_OFFSET = 0x02
    RS_FS_BLOCK_COPY_COUNT_OFFSET = 0x04
    RS_METABLOCK_SCAN_COUNT_OFFSET = 0x06
    RS_METABLOCK_COPY_COUNT_OFFSET = 0x08

    commandName = "Read Scrub data"
    opcode = 0xC9
    subOpcode = 2
    option = 2
    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    cdb = [opcode, subOpcode, option, 0,
           0, 0, 0, 0,
           0, 0, 0, 0,
          0, 0, 0, 0]

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, READ_DATA))
    dataBuffer = SendDiagnostic(vtfContainer,dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    configParams = {"rsRemovedFromQueueCount":None, "rsScanConvertedToCopyCount":None, "rsFileSystemCopyCount":None,
                    "rsMetaBlockScanCount":None, "rsMetaBlockCopyCount":None}

    configParams["rsRemovedFromQueueCount"] = dataBuffer.GetTwoBytesToInt(RS_REMOVE_FROM_QUEUE_COUNT_OFFSET)
    configParams["rsScanConvertedToCopyCount"] = dataBuffer.GetTwoBytesToInt(RS_SCAN_CONVERTED_TO_COPY_COUNT_OFFSET)
    configParams["rsFileSystemCopyCount"] = dataBuffer.GetTwoBytesToInt(RS_FS_BLOCK_COPY_COUNT_OFFSET)
    configParams["rsMetaBlockScanCount"] = dataBuffer.GetTwoBytesToInt(RS_METABLOCK_SCAN_COUNT_OFFSET)
    configParams["rsMetaBlockCopyCount"] = dataBuffer.GetTwoBytesToInt(RS_METABLOCK_COPY_COUNT_OFFSET)

    return configParams
#end of ReadScrubInfoOption2

def ReadScrubInfoOption3(vtfContainer):
    """
    Name : ReadScrubInfoOption3()

    Description : This function calls "Get MML Data diag(0xC9)", gives read scrub info.

    Arguments :
              vtfContainer - vtfContainer Object

    Returns :
             configParams : dictionary of Read Scrub info(such as "read scrub scan block" and "read scrub copy block")

    opcode : 0xC9

    subopcode : 2

    option : 3

    """
    #offsets
    RS_COPY_BLOCK_ADDR_OFFSET = 0x00
    RS_SCAN_BLOCK_ADDR_OFFSET = 0x02

    commandName = "Read Scrub data"
    opcode = 0xC9
    subOpcode = 2
    option = 3
    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    cdb = [opcode, subOpcode, option, 0,
           0, 0, 0, 0,
           0, 0, 0, 0,
          0, 0, 0, 0]

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, READ_DATA))
    dataBuffer = SendDiagnostic(vtfContainer,dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    configParams = {"rsCopyBlockAddr":None, "rsScanBlockAddr":None}

    configParams["rsCopyBlockAddr"] = dataBuffer.GetTwoBytesToInt(RS_COPY_BLOCK_ADDR_OFFSET)
    configParams["rsScanBlockAddr"] = dataBuffer.GetTwoBytesToInt(RS_SCAN_BLOCK_ADDR_OFFSET)

    return configParams
#end of ReadScrubInfoOption3

def GetBlockManagerInfo(vtfContainer,metaPlane, fblIndex = 0, OutputData = 0, blockType = 0,bankNumber = 0):
    """
    Name : GetBlockManagerInfo()

    Description : This function calls "Get MML Data diag(0xC9)", gives Block manager info.

    Arguments :
              vtfContainer - vtfContainer Object
              metaPlane - Meta plane address
              fblIndex - Free block list index offset
              OutputData - output data
              blockType - block type for mlc level
              bankNumber - Bank number

    Returns :
             nextMba : next meta block address

    opcode : 0xC9

    subopcode : 3

    """
    #offset
    NEXT_MBA_OFFSET = 0

    commandName = "Get Next MBA In FBL"

    getMMLDataBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR, 0x0)
    opcode = 0xC9      #Get MML data opCode 0xc9
    subOpcode = 3   #Sub opcode for Block Manager Info 0x03
    OutputDataType = OutputData
    #bank = 0                                           #In BE6 , number of Bank is 1
    if OutputData == 0:
        cdb = [opcode, subOpcode, blockType, fblIndex,
               OutputDataType, metaPlane, 0, 0,
               0,0, bankNumber, 0,
             0,0,0,0]

    elif OutputData == 1:
        fblIndexOffset = fblIndex
        cdb = [opcode, subOpcode, fblIndexOffset, 0,
               OutputDataType, metaPlane, 0, 0,
               0,0, bankNumber, 0,
             0,0,0,0]

    getMMLDataBuf = SendDiagnostic(vtfContainer, getMMLDataBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    nextMba = getMMLDataBuf.GetFourBytesToInt(NEXT_MBA_OFFSET)
    nextMba = nextMba << 16

    return nextMba

def GetGatDeltaEntry(vtfContainer,NumOfEntries=64):
    """
    Name : GetGatDeltaEntry()

    Description : This function retrieves the GAT Delta Info from GAT Cache

    Arguments :
              vtfContainer - vtfContainer Object
              logicalGroupNo - logical group number

    Returns :
             List of GAT delta Entry(LgNum,offsetInLG,Insync,SlcFlag,MBNum,offsetInMb,Runlength)


    typedef struct _GAT_Entry_t
    {
        uint16      SLCFlag:GAT_ENTRY_NUM_BITS_SLC_FLAG; 1 bit
    #ifdef PROD_SPARROW_X2_ZERO_FILL_ON_UECC
        uint16      ZeroFillOnUECC:GAT_ENTRY_NUM_BITS_ZERO_FILL;
    #endif
        uint16      MBNum:GAT_ENTRY_NUM_BITS_MBNUM; 15 bits
        uint16      OffsetInMB:GAT_ENTRY_NUM_BITS_OFFSET_IN_MB; 16 bits
    }GAT_Entry_t;


    typedef struct _GAT_Delta_Entry_t
    {
        GAT_Entry_t       GATEntry;
        uint32            LGNum;
        uint16            OffsetInLG;
        uint16            RunLength;
        uint16            prevNode;
        uint16            nextNode;
    } GAT_Delta_Entry_t;


    """

    mmlDataBuffer= GetGatCacheInfo(vtfContainer)
    GAT_DELTA_INFO_START= GAT_DELTA_ENTRY_MERGED #0X8

    gatDeltaSize = mmlDataBuffer.GetTwoBytesToInt(GAT_DELTA_SIZE_OFFSET)
    GATDeltaEntry=[]

    #StartOfGatDelta = mmlDataBuffer.GetTwoBytesToInt(GAT_DELTA_INFO_START)

    for i in range (0, gatDeltaSize):   #while(StartOfGatDelta != 0xFFFF):
        MBInfo=(mmlDataBuffer.GetTwoBytesToInt(GAT_DELTA_INFO_START))
        SlcFlag=MBInfo&0x01
        MBNum = (MBInfo >> 1) & 0x7FFF

        offsetInMb = (mmlDataBuffer.GetTwoBytesToInt(GAT_DELTA_INFO_START + 2))

        LgNum = (mmlDataBuffer.GetFourBytesToInt(GAT_DELTA_INFO_START + 4))
        offsetInLG = (mmlDataBuffer.GetTwoBytesToInt(GAT_DELTA_INFO_START + 8))

        #Insync Variable is removed from structure
        Insync = 0
        Runlength = (mmlDataBuffer.GetTwoBytesToInt((GAT_DELTA_INFO_START)+10))

        GATDeltaEntry.append((LgNum,offsetInLG,Insync,SlcFlag,MBNum,offsetInMb,Runlength))

        #StartOfGatDelta=mmlDataBuffer.GetTwoBytesToInt((GAT_DELTA_INFO_START)+16)

        GAT_DELTA_INFO_START=GAT_DELTA_INFO_START+16

    return GATDeltaEntry
#----------------------------------------------------------------------
# New diagnostic for storing the RGAT delta entries - Lambeau
def GetRGatDeltaEntry(vtfContainer):

    #offsets
    RGAT_DELTA_INFO_START = RGAT_DELTA_ENTRY_MERGED #0x1B88

    mmlDataBuffer= GetGatCacheInfo(vtfContainer)
    #16 bytes per entry * 88 = 1408 bytes
    RGATDeltaEntry=[]

    """
   typedef struct _RGAT_Delta_Entry_Merged_t
   {
              RGAT_Delta_Entry_t      RGat_DeltaEntry;
              RGAT_Delta_RunLength_t  RunLength;
           }RGAT_Delta_Entry_Merged_t; (12 bytes)

   typedef struct _RGAT_Delta_Entry_t
   {
              uint16                  MBNum;
              uint16                  OffsetInMB;
              RGAT_Entry_t            RGATEntry;
              uint16                  RunLength;
           }RGAT_Delta_Entry_t; (10 bytes)

   typedef struct _RGAT_Entry_t
   {
              uint32                  OffsetInLG:  10;
              uint32                  LGNum:       22;
           }RGAT_Entry_t; (4 bytes)

   typedef uint16 RGAT_Delta_RunLength_t; (2 bytes)
   """

    for i in range(88):
        MBNum = (mmlDataBuffer.GetTwoBytesToInt(RGAT_DELTA_INFO_START))

        if MBNum == 0xFFFF:
            break;
        offsetInMb = (mmlDataBuffer.GetTwoBytesToInt(RGAT_DELTA_INFO_START + 2))

        LgInfo = mmlDataBuffer.GetFourBytesToInt(RGAT_DELTA_INFO_START + 4)
        LgOffset = LgInfo & 0x3FF
        LgNum = (LgInfo >> 10) & 0x3FFFFF

        RGATDeltaEntry.append((MBNum, offsetInMb, LgOffset, LgNum))
        RGAT_DELTA_INFO_START = RGAT_DELTA_INFO_START + 12

    return RGATDeltaEntry
#end of GetRGatDeltaEntry

# New diagnostic for storing the RGAT  directory delta entries - Lambeau
def GetRGatDirDeltaEntry(vtfContainer):

    #offsets
    RGAT_DIR_DELTA_INFO_START = RGAT_DIR_DELTA_ENTRY #0x2108

    mmlDataBuffer= GetGatCacheInfo(vtfContainer)
    #8 bytes per entry * 64 = 256 bytes
    RGATDirDeltaEntry=[]


    """
typedef struct _RGAT_Page_Ptr_t
{
   uint8       IsSequential:              1;
   uint8       IsPseudoSequential:        1;
   uint8       Reserved:                  6;
   uint8       MBNum;
   uint16      OffsetInMB;
}RGAT_Page_Ptr_t; (4 bytes)

typedef struct _RGAT_Seq_Ptr_t
{
   uint32      IsSequential:              1;
   uint32      LGNum:                     21;
   uint32      OffsetInLG:                10;
}RGAT_Seq_Ptr_t; (4 bytes)

typedef union _RGAT_Dir_Entry_t
{
   RGAT_Page_Ptr_t      rgatPagePtr;
   RGAT_Seq_Ptr_t       rgatSeqPtr;
}RGAT_Dir_Entry_t;

typedef struct _RGAT_Dir_Delta_Entry_t
{
   uint32                  pageNum;
   RGAT_Dir_Entry_t        rgatDirEntry;
}RGAT_Dir_Delta_Entry_t;

   """

    RGATDirSize = mmlDataBuffer.GetTwoBytesToInt(RGAT_DIR_DELTA_SIZE)
    for i in range(0, RGATDirSize):
        pageNum = (mmlDataBuffer.GetFourBytesToInt(RGAT_DIR_DELTA_INFO_START))

        pageInfo = (mmlDataBuffer.GetTwoBytesToInt(RGAT_DIR_DELTA_INFO_START + 4))

        IsSequential = pageInfo & 0x01

        if IsSequential == 0:
            IsPseudoSequential = (pageInfo >> 1) & 0x01
            MBNum = (pageInfo >> 8) & 0xFF
            offsetInMb = (mmlDataBuffer.GetTwoBytesToInt(RGAT_DIR_DELTA_INFO_START + 6))
            RGATDirDeltaEntry.append((IsSequential, MBNum, offsetInMb))
        else:

            lgInfo =  (mmlDataBuffer.GetFourBytesToInt(RGAT_DIR_DELTA_INFO_START + 8))
            IsSequential1 = lgInfo & 0x01
            lgNum = (lgInfo >> 1) & 0x1FFFFF
            offsetInLg = (lgInfo >> 22) & 0x3FF
            RGATDirDeltaEntry.append((IsSequential, lgNum, offsetInLg))

        RGAT_DIR_DELTA_INFO_START = RGAT_DIR_DELTA_INFO_START + 8

    return RGATDirDeltaEntry
#end of GetRGatDirDeltaEntry

def GetGatEntry(vtfContainer,lgNum,lgOffset=0):
    """
    Name : GetGatEntry()

    Description : This function retrieves the Gat Entry Info not GAT page Info

    Arguments :
    vtfContainer - vtfContainer Object
    lgNum     - logical group number
    lgOffset  - offset of the LG Num

    Returns :
    GAT entry Info for the passed LG num and LG fragment offset(MBnum,SlcFlag,MBoffset)
    """
    commandName="GAT Info"
    opcode=0xc9
    subOpcode=0x4
    LgLowBye=ByteUtil.LowByte(lgNum)
    LgHighByte=ByteUtil.HighByte(lgNum)
    lgOffsetLowbyte=ByteUtil.LowByte(lgOffset)
    lgOffsetHighbyte=ByteUtil.HighByte(lgOffset)
    getMMLDataBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    MBNumoffset=0x00
    MBoffset=0x02

    cdb = [opcode, subOpcode, 0,0,
           LgLowBye,LgHighByte,lgOffsetLowbyte,lgOffsetHighbyte,
           0,0,0,0,
          0,0,0,0]
    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, READ_DATA))
    getMMLDataBuf = SendDiagnostic(vtfContainer,getMMLDataBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)


    MBNumandSlcFlag=getMMLDataBuf.GetTwoBytesToInt(MBNumoffset)
    MBnum=MBNumandSlcFlag&0xFFFE
    MBnum=MBnum>>1
    SlcFlag=MBNumandSlcFlag&0x0001
    MBoffset=getMMLDataBuf.GetTwoBytesToInt(MBoffset)

    return (MBnum,SlcFlag,MBoffset)

# New diagnostic for storing the RGAT entries - Lambeau
def GetRGatEntry(vtfContainer,mbNum,mbOffset=0):

    commandName="RGAT Info"
    opcode=0xc9
    subOpcode=65
    MbLowBye=ByteUtil.LowByte(mbNum)
    MbHighByte=ByteUtil.HighByte(mbNum)
    MbOffsetLowbyte=ByteUtil.LowByte(mbOffset)
    MbOffsetHighbyte=ByteUtil.HighByte(mbOffset)
    getMMLDataBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    LGNumoffset=0x00
    LGoffset=0x02


    cdb = [opcode, subOpcode, 0,0,
           MbLowBye,MbHighByte,MbOffsetLowbyte,MbOffsetHighbyte,
           0,0,0,0,
          0,0,0,0]
    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, READ_DATA))
    getMMLDataBuf = SendDiagnostic(vtfContainer,getMMLDataBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    """
   typedef struct _RGAT_Entry_t
   {
   uint32                 OffsetInLG:10;
   uint32                  LGNum:22;
   }RGAT_Entry_t;

   """

    LgOffsetInfo1=getMMLDataBuf.GetTwoBytesToInt(0x00,0)
    LgOffset1 = LgOffsetInfo1&0xFFC0
    LgOffset = LgOffset1>>6

    LgInfo1=getMMLDataBuf.GetOneByteToInt(0x01)
    LgNum1 = LgInfo1&0x3F
    LgInfo2=getMMLDataBuf.GetTwoBytesToInt(0x02,0)
    LgNum = LgNum1+LgInfo2

    return (LgNum,LgOffset)
#end of GetRGatEntry


def GetIGATDeltaEntry(vtfContainer,multiMP=1):
    """
    typedef struct _IGAT_Delta_Entry_t
    {
       uint16   MBNum:16;
       int16    VFCountChange;
       IGAT_Delta_Entry_union_t   igatDeltaEntryBitField;
    } IGAT_Delta_Entry_t;

    typedef struct _IGAT_Delta_BitField_t
    {
       uint32   DataInvalidatedInMetaBlock:   1;
       uint32   BlockTypeChange:              1;
       uint32   BlockType:                    1;
       uint32   BlockStatusChange:            1;
       uint32   BlockStatusValue:             2;
       uint32   HotCountChange:               10;
       uint32   WriteModeChange:              1;
       uint32   WriteModeValue:               1;
       uint32   RetireBlock:                  1;
       uint32   PFStatusChange:               1;
       uint32   PFStatus:                     1;
       uint32   EPWRStatusChange:             1;
       uint32   EPWRStatus:                   1;
       uint32   UECCStatusChange:             1;
       uint32   UECCStatus:                   1;
       uint32   WAStatusChange:               1;
       uint32   WAStatus:                     1;
       uint32   Reserved:                     5;
    }IGAT_Delta_BitField_t; (4 bytes)

    """
    #offset chnge is needed here: manoj

    mmlDataBuffer= GetGatCacheInfo(vtfContainer)
    IGATdeltaEntries=[]
    IGAT_DELTA_INFO_START  = IGAT_DELTA_ENTRY #0x1988

    IGATDeltaSize = mmlDataBuffer.GetTwoBytesToInt(IGAT_DELTA_SIZE_OFFSET)

    for count in range(IGATDeltaSize):
        IGATMB = mmlDataBuffer.GetTwoBytesToInt(IGAT_DELTA_INFO_START)
        VFCountChange = mmlDataBuffer.GetTwoBytesToInt(IGAT_DELTA_INFO_START + 2)


        BlockTypeInfo = mmlDataBuffer.GetFourBytesToInt(IGAT_DELTA_INFO_START + 4)
        IGATDataInvalidated = BlockTypeInfo & 0x01
        BlockTypeChange = (BlockTypeInfo >> 1) & 0x01
        BlockType = (BlockTypeInfo >> 1) & 0x01
        BlockStatusChange = (BlockTypeInfo >> 3) & 0x01
        BlockStatusValue = (BlockTypeInfo >> 4) & 0x03
        HotCountChange = (BlockTypeInfo >> 6) & 0x3FF
        WriteModeChange = (BlockTypeInfo >> 16) & 0x01
        WriteModeValue = (BlockTypeInfo >> 17) & 0x01
        RetireBlock = (BlockTypeInfo >> 18) & 0x01

        PFStatusChange = (BlockTypeInfo >> 19) & 0x01
        PFStatus = (BlockTypeInfo >> 20) & 0x01
        EPWRStatusChange = (BlockTypeInfo >> 21) & 0x01
        EPWRStatus = (BlockTypeInfo >> 22) & 0x01
        UECCStatusChange = (BlockTypeInfo >> 23) & 0x01
        UECCStatus = (BlockTypeInfo >> 24) & 0x01
        WAStatusChange = (BlockTypeInfo >> 25) & 0x01
        WAStatus = (BlockTypeInfo >> 26) & 0x01

        IGAT_DELTA_INFO_START = IGAT_DELTA_INFO_START + 8

        IGATdeltaEntries.append((IGATMB,IGATDataInvalidated,VFCountChange,BlockTypeInfo))

    return IGATdeltaEntries
#----------------------------------------------------------------------
def GetIGATEntryInfo(vtfContainer, mbnum):

    """
    Get the IGAT Entry info for a given MB number
   """
    commandName = "Get MML Data"
    opcode = 0xc9
    subOpcode = 0x18
    option=0
    optionEx=mbnum
    mmlDataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    cdbData = [opcode,subOpcode,option,0,
               ByteUtil.LowByte(ByteUtil.LowWord(optionEx)), ByteUtil.HighByte(ByteUtil.LowWord(optionEx)),
               ByteUtil.LowByte(ByteUtil.HighWord(optionEx)),ByteUtil.HighByte(ByteUtil.HighWord(optionEx)),
              0,0,0,0,0,0,0,0]

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, Data Direction: %s" %(opcode, READ_DATA))
    mmlDataBuffer = SendDiagnostic(vtfContainer, mmlDataBuffer, cdbData, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    VFCount = mmlDataBuffer.GetTwoBytesToInt(0x00)
    HotCount = mmlDataBuffer.GetTwoBytesToInt(0x02)
    BlockStatus = mmlDataBuffer.GetOneByteToInt(0x04)
    BlockType = mmlDataBuffer.GetOneByteToInt(0x05)
    WriteMode = mmlDataBuffer.GetOneByteToInt(0x06)
    RetireBlock = mmlDataBuffer.GetOneByteToInt(0x07) & 0xF
    RetireReason = (mmlDataBuffer.GetOneByteToInt(0x07) >> 4) & 0xF

    """
   Old
   VFCount = mmlDataBuffer.GetTwoBytesToInt(0x00)
   HotCount = mmlDataBuffer.GetOneByteToInt(0x02)
   BlockStatus = mmlDataBuffer.GetOneByteToInt(0x03)
   BlockType = mmlDataBuffer.GetOneByteToInt(0x04)
   RetireBlock = mmlDataBuffer.GetOneByteToInt(0x05)
   WriteMode = mmlDataBuffer.GetOneByteToInt(0x06)
   Reserved = mmlDataBuffer.GetOneByteToInt(0x07)
   """

    #IGATEntryInfo = (VFCount, HotCount, BlockStatus, WriteMode, BlockType, PFStatus, EPWRStatus, UECCStatus, WAStatus, RetireBlock, data)
    IGATEntryInfo = (VFCount, HotCount, BlockStatus, WriteMode, BlockType, RetireBlock, RetireReason)  #NOT CHANGING THE ORDER
    #IGATEntryInfo = (VFCount, HotCount, BlockStatus, BlockType, WriteMode, RetireBlock, RetireReason)

    return  IGATEntryInfo
#end of GetIGATEntryInfo



def GetMetaBlockNum(vtfContainer, lba):
    """
    Calculating the metablock number from the physical location
    """
    #offsets
    if IsLargeMetablockUsed(vtfContainer)[0]:
        GET_METABLOCK_NUMBER_OFFSET=4
    else:
        GET_METABLOCK_NUMBER_OFFSET = 2

    commandName = "Get MML Data"
    opcode = 0xc9
    subOpcode = 0xa
    option=1
    optionEx=lba
    bank=0
    mmlDataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    #cdbData = [opcode,subOpcode,option,0,optionEx,optionEx>>8,optionEx>>16,optionEx>>24,0,0,bank,0,0,0,0,0]
    cdbData = [opcode,subOpcode,option,0,
               ByteUtil.LowByte(ByteUtil.LowWord(optionEx)), ByteUtil.HighByte(ByteUtil.LowWord(optionEx)),
               ByteUtil.LowByte(ByteUtil.HighWord(optionEx)),ByteUtil.HighByte(ByteUtil.HighWord(optionEx)),
              0,0,bank,0,0,0,0,0]


    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, Data Direction: %s" %(opcode, READ_DATA))
    mmlDataBuffer = SendDiagnostic(vtfContainer, mmlDataBuffer, cdbData, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    if IsLargeMetablockUsed(vtfContainer)[0]:
        MBNum=mmlDataBuffer.GetFourBytesToInt(GET_METABLOCK_NUMBER_OFFSET)
    else:
        MBNum=mmlDataBuffer.GetTwoBytesToInt(GET_METABLOCK_NUMBER_OFFSET)
    return MBNum
#end of GetMetaBlockNum

def GetWLCounters(vtfContainer,partitionIndex):
    #offsets
    WEARLEVEL_COUNT_OFFSET         = 0x00
    AVERAGE_HOTCOUNT_OFFSET        = 0x02
    NUM_OF_BLOCKS_OFFSET           = 0x06
    HOT_COUNT_WITH_IN_CYCLE_OFFSET = 0x08
    COPIED_BLOCKS_COUNT_OFFSET     = 0x0A
    GAT_PAGE_ROWER_POINTER_OFFSET  = 0x0C


    commandName = "Get WL Counters"
    opcode = 0xC9
    subOpcode = 13 #Sub opcode for WL Counters
    getMMLDataBuf = pyWrap.Buffer.CreateBuffer(1, 0x00)
    optionLow   = partitionIndex & MASK_LOW_BYTE
    optionHigh  = (partitionIndex >> 8) & MASK_LOW_BYTE

    cdb = [opcode, subOpcode, optionLow,optionHigh,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, READ_DATA))
    getMMLDataBuf = SendDiagnostic(vtfContainer,getMMLDataBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    configParams = {"wearLevelCount":None, "averageHotCount":None,"numOfBlocks":None,"hcWithInCycle":None,"copiedBlocksCout":None,"gatPageRowerPointer":None}

    configParams["wearLevelCount"]      = getMMLDataBuf.GetTwoBytesToInt(WEARLEVEL_COUNT_OFFSET)
    configParams["averageHotCount"]     = getMMLDataBuf.GetFourBytesToInt(AVERAGE_HOTCOUNT_OFFSET)
    configParams["numOfBlocks"]         = getMMLDataBuf.GetTwoBytesToInt(NUM_OF_BLOCKS_OFFSET)
    configParams["hcWithInCycle"]       = getMMLDataBuf.GetFourBytesToInt(HOT_COUNT_WITH_IN_CYCLE_OFFSET)
    configParams["copiedBlocksCout"]    = getMMLDataBuf.GetTwoBytesToInt(COPIED_BLOCKS_COUNT_OFFSET)
    configParams["gatPageRowerPointer"] = getMMLDataBuf.GetFourBytesToInt(GAT_PAGE_ROWER_POINTER_OFFSET)

    return configParams
#end of GetWLCounters

def GetSpareBlockListInfo(vtfContainer,getHotCountForSpareBlocks=False):
    """
    Name       :   GetSpareBlockListInfo
    Description:   Get the Spare Block List info and calculate Spare Block Count and return the same.
    Arguments  :
                   None
    Returns    :
        SpareBlockCount - Number of spare blocks present in the card/model.
    """
    #offsets
    LENGTH_OF_SLC_FBL_ARRAY = 0x0
    NUM_SLC_FBL_ENTRIES_OFFSET = 0x02
    LENGTH_OF_ONE_SLC_FBL_ENTRY = 0x04
    LIST_OF_META_BLOCKS_IN_FBL_OFFSET = 0x06

    #getMMLDataBuf = pyWrap.Buffer.CreateBuffer(size = 1, initialFillPattern = 0x00)
    getMMLDataBuf = pyWrap.Buffer.CreateBuffer(EIGHT_SECTORS, 0x00)

    opcode = 0xC9
    subOpcode = 0x14 # SpareBlockListInfo - in Dec:20 & in Hex:0x14 Ref:Chrous Doc for More Details

    commandName   = "GET MML DATA"

    cdb = [opcode, subOpcode, 0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    #getMMLDataBuf = SendDiagnostic(vtfContainer, getMMLDataBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    getMMLDataBuf = SendDiagnostic(vtfContainer, getMMLDataBuf, cdb, READ_DATA, EIGHT_SECTORS, opcode, commandName)
    #Get number of sectors required for Diag to return data
    #Number of SLC FBL entries
    numberOfSLC_FBLEntries = getMMLDataBuf.GetTwoBytesToInt(NUM_SLC_FBL_ENTRIES_OFFSET)
    listOfSLCMetaBlocksInFBL = getMMLDataBuf.GetFourBytesToInt(LIST_OF_META_BLOCKS_IN_FBL_OFFSET)

    #Get the offset of MLC
    startingAddressOfMLC = 0x06 + (4 * listOfSLCMetaBlocksInFBL)

    numberOfSectors = old_div(startingAddressOfMLC,512)
    if (startingAddressOfMLC % 512):
        numberOfSectors = numberOfSectors + 1

    #getMMLDataBuf = pyWrap.Buffer.CreateBuffer(size = numberOfSectors, initialFillPattern = 0x00) #CHECK WITH MANOJ
    getMMLDataBuf = pyWrap.Buffer.CreateBuffer(EIGHT_SECTORS, 0x00)


    # now get full data
    opcode = 0xC9
    subOpcode = 0x14 # SpareBlockListInfo - in Dec:20 & in Hex:0x14 Ref:Chrous Doc for More Details

    commandName   = "GET MML DATA"

    cdb = [opcode, subOpcode, 0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    #getMMLDataBuf = SendDiagnostic(vtfContainer, getMMLDataBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    #getMMLDataBuf = SendDiagnostic(vtfContainer, getMMLDataBuf, cdb, READ_DATA, FOUR_SECTORS, opcode, commandName)
    getMMLDataBuf = SendDiagnostic(vtfContainer, getMMLDataBuf, cdb, READ_DATA, EIGHT_SECTORS, opcode, commandName)


    #SpareBlockListInfo (From  "Chorus Common Diagnostic Commands Spec.doc" Document)

    #subOpcode  Options
        #Options Ex     Data returned                           Byte offset (hex)       Field size (bytes)      Number of fields
        #20     n/a     n/a     length of SLC FBL Array                 0x0                     2                       1
                        #Total Number of SLC FBL Entries                0x2                     2                       1
                        #Length of one element in the SLC FBL           0x4                     2                       1
                        #List of SLC meta blocks in FBL                 0x6                     4               <len SLC list>
                        #x = 0x6 + (4 x Total length (SLC list))
                        #length of MLC FBL Array                        x                       2                       1
                            #TotalNumber of MLC FBL Entries             x + 0x02                2                       1
                        #Length of one element in the MLC FBL           x + 0x04                2                       1
                        #List of MLC meta blocks in FBL                 x + 0x06                4               <len MLC list>

    #Number of SLC FBL entries
    lengthOfSLC_FBLArray = getMMLDataBuf.GetTwoBytesToInt(LENGTH_OF_SLC_FBL_ARRAY)
    numberOfSLC_FBLEntries = getMMLDataBuf.GetTwoBytesToInt(NUM_SLC_FBL_ENTRIES_OFFSET)
    lengthofSLCFBLEntry = getMMLDataBuf.GetTwoBytesToInt(LENGTH_OF_ONE_SLC_FBL_ENTRY)
    listOfSLCMetaBlocksInFBL = []
    listOfHCforSLCMetaBlocksInFBL=[]
    for index in range(0,numberOfSLC_FBLEntries ):
        listOfSLCMetaBlocksInFBL.append(getMMLDataBuf.GetTwoBytesToInt(LIST_OF_META_BLOCKS_IN_FBL_OFFSET + (index*lengthofSLCFBLEntry)))
        listOfHCforSLCMetaBlocksInFBL.append(getMMLDataBuf.GetTwoBytesToInt(LIST_OF_META_BLOCKS_IN_FBL_OFFSET + (index*lengthofSLCFBLEntry)+2))
    #Get MLC FBL Info
    #Get the offset of MLC
    startingAddressOfMLC = 0x06 + (lengthofSLCFBLEntry * lengthOfSLC_FBLArray)
    lengthOfMLC_FBLArray = getMMLDataBuf.GetTwoBytesToInt(startingAddressOfMLC)
    #Number of MLC FBL entries
    numberOfMLC_FBLEntries = getMMLDataBuf.GetTwoBytesToInt(startingAddressOfMLC+0x02)
    lengthofMLCFBLEntry = getMMLDataBuf.GetTwoBytesToInt(startingAddressOfMLC+0x04)
    listOfMLCMetaBlocksInFBL = []
    listOfHCforMLCMetaBlocksInFBL=[]
    for index in range(0,numberOfMLC_FBLEntries ):
        listOfMLCMetaBlocksInFBL.append(getMMLDataBuf.GetTwoBytesToInt(startingAddressOfMLC+LIST_OF_META_BLOCKS_IN_FBL_OFFSET + (index*lengthofMLCFBLEntry)))
        listOfHCforMLCMetaBlocksInFBL.append(getMMLDataBuf.GetTwoBytesToInt(startingAddressOfMLC+LIST_OF_META_BLOCKS_IN_FBL_OFFSET + (index*lengthofMLCFBLEntry)+2))

    #Get Dedicated FBL Info
    #Get the offset of Dedicated FBL
    startingAddressOfDFBL = startingAddressOfMLC + 0x06 + (lengthofMLCFBLEntry * lengthOfMLC_FBLArray)
    lengthOfDFBL_FBLArray = getMMLDataBuf.GetTwoBytesToInt(startingAddressOfDFBL)
    #Number of Dedicated FBL entries
    numberOfDFBL_FBLEntries = getMMLDataBuf.GetTwoBytesToInt(startingAddressOfDFBL+0x02)
    lengthofDFBLEntry = getMMLDataBuf.GetTwoBytesToInt(startingAddressOfDFBL+0x04)
    listOfDedicatedFBLMetaBlocks = []
    listOfHCforDedicatedFBLMetaBlocks=[]
    for index in range(0,numberOfDFBL_FBLEntries ):
        listOfDedicatedFBLMetaBlocks.append(getMMLDataBuf.GetTwoBytesToInt(startingAddressOfDFBL+LIST_OF_META_BLOCKS_IN_FBL_OFFSET + (index*lengthofDFBLEntry)))
        listOfHCforDedicatedFBLMetaBlocks.append(getMMLDataBuf.GetTwoBytesToInt(startingAddressOfDFBL+LIST_OF_META_BLOCKS_IN_FBL_OFFSET + (index*lengthofDFBLEntry)+2))
    #Total Spare blocks count is sumof number of SLC , MLC & Dedicated FBL entries
    totalSpareBlockCount = (numberOfSLC_FBLEntries + numberOfMLC_FBLEntries +numberOfDFBL_FBLEntries)
    if getHotCountForSpareBlocks==True:
        return(totalSpareBlockCount,listOfSLCMetaBlocksInFBL,listOfHCforSLCMetaBlocksInFBL,listOfMLCMetaBlocksInFBL,listOfHCforMLCMetaBlocksInFBL,\
               listOfDedicatedFBLMetaBlocks,listOfHCforDedicatedFBLMetaBlocks)
    else:
        return totalSpareBlockCount, listOfSLCMetaBlocksInFBL, listOfMLCMetaBlocksInFBL, listOfDedicatedFBLMetaBlocks
#end of GetSpareBlockListInfo

def GetSpareBlockFBLInfo(vtfContainer, bankNumber = 0):
    """
    Name       :   GetSpareBlockListInfo
    Description:   Get the Spare Block List info and calculate Spare Block Count and return the same.
    Arguments  :
    BankNumber: Zero if not specified.
    Returns    :
        SpareBlockCount - Number of spare blocks present in the card/model.
    """
    #offsets
    NUM_SLC_FBL_ENTRIES_OFFSET = 0x02
    LIST_OF_META_BLOCKS_IN_FBL_OFFSET = 0x06

    LENGTH_OF_SLC_FBL_ARRAY = 0x0
    TOTAL_NUMBER_OF_SLC_FBL_ENTRIES = 0x2
    LENGTH_OF_ONE_ELEMENT_IN_THE_SLC_FBL = 0x4
    LIST_OF_SLC_META_BLOCKS_IN_FBL = 0x6

    #getMMLDataBuf = pyWrap.Buffer.CreateBuffer(size = 1, initialFillPattern = 0x00)
    getMMLDataBuf = pyWrap.Buffer.CreateBuffer(FOUR_SECTORS, 0x00)
    opcode = 0xC9
    subOpcode = 0x14 # SpareBlockListInfo - in Dec:20 & in Hex:0x14 Ref:Chrous Doc for More Details
    commandName   = "GET MML DATA"
    cdb = [opcode, subOpcode, 0,0,
           0,0,0,0,
           0,0,bankNumber,0,
          0,0,0,0]
    #getMMLDataBuf = SendDiagnostic(vtfContainer, getMMLDataBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    getMMLDataBuf = SendDiagnostic(vtfContainer, getMMLDataBuf, cdb, READ_DATA, FOUR_SECTORS, opcode, commandName)
    #Number of SLC FBL entries
    numberOfSLC_FBLEntries = getMMLDataBuf.GetTwoBytesToInt(NUM_SLC_FBL_ENTRIES_OFFSET)
    #Number of MLC FBL entries
    lenOfSLC_FBL_Array = getMMLDataBuf.GetTwoBytesToInt(LENGTH_OF_SLC_FBL_ARRAY)
    Total_Number_of_SLC_FBL_Entries = getMMLDataBuf.GetTwoBytesToInt(TOTAL_NUMBER_OF_SLC_FBL_ENTRIES)
    Length_of_one_element_in_the_SLC_FBL = getMMLDataBuf.GetTwoBytesToInt(LENGTH_OF_ONE_ELEMENT_IN_THE_SLC_FBL)
    List_of_SLC_meta_blocks_in_FBL = getMMLDataBuf.GetTwoBytesToInt(LIST_OF_SLC_META_BLOCKS_IN_FBL)
    #x = 0x6 + ((Length of one element) x (Total length SLC list))
    startingAddressOfMLC = 0x6 + (Length_of_one_element_in_the_SLC_FBL * lenOfSLC_FBL_Array)
    numberOfMLC_FBLEntries =  getMMLDataBuf.GetTwoBytesToInt(startingAddressOfMLC + 0x02)
    return [numberOfSLC_FBLEntries ,numberOfMLC_FBLEntries,(numberOfSLC_FBLEntries +numberOfMLC_FBLEntries )]
#end of GetSpareBlockListInfo

def GetSpareBlockCount(vtfContainer, bankNumber=0):
    """
    Name       :   GetSpareBlockCount
    Description:   Get the Spare Block Spare Block Count and return the same.
    Arguments  :
                   None
    Returns    :
        SpareBlockCount - Number of spare blocks present in the card/model.
    """
    #offsets
    NUM_OF_BLOCK_TYPE = 0x0
    TOTAL_NUM_OF_SPARE_BLOCK_COUNT_SLC_FBL_ENTRIES = 0x01
    TOTAL_NUM_OF_SPARE_BLOCK_COUNT_MLC_FBL_ENTRIES = 0x03
    getSpareBlockDataBuf = pyWrap.Buffer.CreateBuffer( 1, 0x00)
    opcode = 0xC9
    subOpcode = 0x2A  # SpareBlockCount - in Dec:42 & in Hex:0x2A Ref:Chrous Doc for More Details
    commandName   = "GET SPARE BLOCK COUNT"
    cdb = [opcode, subOpcode, 0,0,
           0,0,0,0,
           0,0,bankNumber,0,
          0,0,0,0]
    getSpareBlockDataBuf = SendDiagnostic(vtfContainer, getSpareBlockDataBuf,cdb,READ_DATA,SINGLE_SECTOR,opcode, commandName)
    numOfBlkType = getSpareBlockDataBuf.GetOneByteToInt(NUM_OF_BLOCK_TYPE)
    numOfSpareBlock_SLC = getSpareBlockDataBuf.GetOneByteToInt(TOTAL_NUM_OF_SPARE_BLOCK_COUNT_SLC_FBL_ENTRIES)
    numOfSpareBlock_MLC = getSpareBlockDataBuf.GetOneByteToInt(TOTAL_NUM_OF_SPARE_BLOCK_COUNT_MLC_FBL_ENTRIES)
    totalSpareBlockCount = (numOfSpareBlock_SLC + numOfSpareBlock_MLC)
    returnval = [numOfSpareBlock_SLC,numOfSpareBlock_MLC,(numOfSpareBlock_SLC+numOfSpareBlock_MLC)]
    return returnval
#end of GetSpareBlockCount


def GetIGATEntry(vtfContainer, mbNumber,getIGatEntryBuf = False):
    """
    Name       :   GetIGATEntry
    Description:   Returns IGatEntry of the specified metablock
    Arguments  :
       mbNumber   -   metablockNumber
       getIGatEntryBuf  :   (Default is False)
               True    :  return the buffer also
               False   :  dont return the buffer
    Returns    :
      MBA
      HC
      RLF
      badblockbit
      res
      pageIndex
    """
    #offset
    HOT_COUNT_OFFSET       = 0
    BLOCK_TYPE_OFFSET      = 2
    PARTITION_ID_OFFSET    = 3
    VALIDITY_BITMAP_1_OFFSET = 4
    VALIDITY_BITMAP_2_OFFSET = 8

    commandName = "Get I-GAT Entry"
    opcode = 0xC9
    subOpcode = 0x18 #GET I-GAT ENTRY subOpcode
    option = 0
    getMMLDataBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    mbNumberNoLo = mbNumber & MASK_LOW_BYTE
    mbNumberNoHi = (mbNumber>>8) & MASK_LOW_BYTE
    optionLow    =  option & MASK_LOW_BYTE
    optionHi     =  (option >> 8)& MASK_LOW_BYTE



    cdb = [opcode, subOpcode, optionLow,optionHi,
           mbNumberNoLo,mbNumberNoHi,0,0,
           0,0,0,0,
          0,0,0,0]

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, READ_DATA))
    getMMLDataBuf = SendDiagnostic(vtfContainer,getMMLDataBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    configParams = {"hotCount":None, "blockType":None, "controlBlock":None, "partitionId":None,"validityBitmap":None}

    configParams["hotCount"]       = getMMLDataBuf.GetTwoBytesToInt(HOT_COUNT_OFFSET)
    blockTypeData                  = getMMLDataBuf.GetOneByteToInt(BLOCK_TYPE_OFFSET)
    configParams["blockType"]      = blockTypeData & 0x01
    configParams["controlBlock"]   = (blockTypeData >>1 ) & 0x01
    configParams["partitionId"]    = getMMLDataBuf.GetOneByteToInt(PARTITION_ID_OFFSET)
    validityBitmap1                = getMMLDataBuf.GetOneByteToInt(VALIDITY_BITMAP_1_OFFSET)
    validityBitmap2                = getMMLDataBuf.GetOneByteToInt(VALIDITY_BITMAP_2_OFFSET)
    configParams["validityBitmap"] = (validityBitmap1<<32)|validityBitmap2


    if getIGatEntryBuf :
        return configParams,getMMLDataBuf
    else:
        return configParams
#End of GetIGATEntry

def GetCountOfFoldingDuringITGC(vtfContainer):
    """
    returns the num of steps ,1WL folded =2steps,for the 1st and last wordline num of steps would be -4 or +4
    From Test Perspective we just check if its greater than 0 or previously fetched Diagnostic
    """
    commandName="GetCountOfFoldingDuringITGC"
    opcode=0xc9
    subOpcode=51
    getMMLDataBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    cdb = [opcode, subOpcode, 0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, READ_DATA))
    getMMLDataBuf = SendDiagnostic(vtfContainer,getMMLDataBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    numOfStepsTakenForFolding=getMMLDataBuf.GetTwoBytesToInt(0x00)
    return numOfStepsTakenForFolding
#End of GetCountOfFoldingDuringITGC

def GetMinFoldSet(vtfContainer):
    """
    This diag returns min fold sets that should be present in a block to be considered for folding
    """
    commandName="GetMinFoldSet"
    opcode=0xc9
    subOpcode=54
    getMMLDataBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    cdb = [opcode, subOpcode, 0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, READ_DATA))
    getMMLDataBuf = SendDiagnostic(vtfContainer,getMMLDataBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    minFoldSet=getMMLDataBuf.GetOneByteToInt(0x00)
    return minFoldSet

def IsLargeMetablockUsed(vtfContainer):
    """
    This Diag Returns if Large Metablock is used in the Firmware
    """
    global g_IsLargeMBUsed
    global g_NumOfBlocksPerMB
    #Addtional Check is added to the Diag to make sure that the Diag is sent to firmware only once and use the same return value for the rest.
    if (g_IsLargeMBUsed == -1 and g_NumOfBlocksPerMB == -1):
        commandName="IsLargeMetablockUsed"
        opcode=0xc9
        subOpcode=52
        getMMLDataBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
        cdb = [opcode, subOpcode, 0,0,
               0,0,0,0,
               0,0,0,0,
             0,0,0,0]
        vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, READ_DATA))
        try:
            getMMLDataBuf      = SendDiagnostic(vtfContainer,getMMLDataBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
            g_IsLargeMBUsed    = getMMLDataBuf.GetOneByteToInt(0x00)
            g_NumOfBlocksPerMB = getMMLDataBuf.GetTwoBytesToInt(0x01)
        except:
            vtfContainer.GetLogger().Info("", "[DiagCheckForAnisha]Diag Failed,Its not Large MB")
            g_IsLargeMBUsed    = 0
            g_NumOfBlocksPerMB = 0

    return (g_IsLargeMBUsed, g_NumOfBlocksPerMB)
#End of IsLargeMetablockUsed

def SetFblInfo(vtfContainer, metablockAddress,hotCountValue):
    #offset
    META_BLOCK_ADDRESS_OFFSET = 0
    HOT_COUNT_OFFSET = 2

    commandName = "Set GAT Entry"
    opcode = 0xCA
    subOpcode = 3
    option = 1

    cdb = [opcode, subOpcode, option,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    wrBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,0)

    wrBuf.SetTwoBytes(META_BLOCK_ADDRESS_OFFSET,metablockAddress)
    wrBuf.SetTwoBytes(HOT_COUNT_OFFSET,hotCountValue)

    SendDiagnostic(vtfContainer, wrBuf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)
#end of SetFblInfo





def SetWearLevelInfo(vtfContainer, WL_Data, blkType = 0 ):
    """
    This function calls "Set MML info" diagnostic to set the wear level info
    opcode = 0xCA
    subOpcode = 0x06

    Arguments :
        WL_Data: Dictionary() got from GET MML DATA(0xc9,13)
    wlData = { "WLCount":None, "AverageHC":None, "NumBlocks":None, "HCWithinCycle":None,
    "CopiedBlocks":None, "PageRover":None, "Blocks":None, Request":None,"State":None, "MB":None }"
        blockType : 0 - SLC : Default
    1 - MLC
    """
    commandName = "Set Wear Level Info"
    opcode    = 0x62
    subOpcode = 0x01

    dataBuf = pyWrap.Buffer.CreateBuffer( 1, 0x00 )
    dataBuf.SetFourBytes( 0, WL_Data["AverageHC" ] )
    dataBuf.SetTwoBytes( 4, WL_Data["NumBlocks"] )
    dataBuf.SetTwoBytes( 6 , WL_Data["WLCount"] )
    dataBuf.SetTwoBytes( 8, WL_Data["HCWithinCycle"] )
    dataBuf.SetTwoBytes( 12, WL_Data["PageRover"] )
    # Resolution to SPARROW-1159:
    # Writing as it is, the list of blocks on which wear levelling
    # is being carried out -- Aditya Gadgil on 28-Oct-2014
    for index in range( 16 ):
        dataBuf.SetTwoBytes( ( ( index * 2 ) + 14 ), WL_Data["Blocks"][index] )
    # end_for
    dataBuf.SetByte( 46, WL_Data["State"])

    bankNum = 0
    cdb = [
        opcode, subOpcode, 0, 0,
        0, 0, 0, 0,
       0, 0, bankNum, blkType,
      0, 0, 0, 0
    ]

    vtfContainer.GetLogger().Debug("",  "Diag: 0x%X, subOpcode: %s Data Direction: %s" % ( opcode, subOpcode, 0 ) )
    statusBuffer = SendDiagnostic( vtfContainer, dataBuf, cdb, 1, 1, opcode, commandName )

#end of SetWearLevelInfo

def SetHotCountForFBL(vtfContainer, hcValue):
    commandName = "Set Hot Count for FBL"
    opcode = 0xCA
    subOpcode = 0x08
    optionLow = hcValue & MASK_LOW_BYTE
    optionHigh = (hcValue >> 8) & MASK_LOW_BYTE
    cdb=[opcode,subOpcode,optionLow,optionHigh,
         0,0,0,0,
         0,0,0,0,
        0,0,0,0]

    rdBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,0)
    rdBuf =SendDiagnostic(vtfContainer, rdBuf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)
#end of SetHotCountForFBL

def GetFilePhysicalLocation(vtfContainer, fileId, copy, fwConfigData):
    #offsets

    if fwConfigData.isBiCS:

        BLOCK_NUMBER_OFFSET = 0
        WL_NUM_OFFSET = 2
        STRING_OFFSET = 3
        CHIP_NUMBER_OFFSET = 4
        DIE_NUM_OFFSET = 5
        PLANE_NUMBER_OFFSET = 6
        SECTOR_OFFSET = 7
    else:
        BLOCK_NUMBER_OFFSET = 0
        WL_NUM_OFFSET = 2
        CHIP_NUMBER_OFFSET = 4
        DIE_NUM_OFFSET = 5
        PLANE_NUMBER_OFFSET = 6
    SECTOR_OFFSET = 7

    commandName = "Get Physical Location of File"
    opcode = 0xCE

    cdb = [opcode,0,ByteUtil.LowByte(fileId),ByteUtil.HighByte(fileId),
           ByteUtil.LowByte(copy),ByteUtil.HighByte(copy),0,0,
           0,0,0,0,
          0,0,0,0]

    phyAddrDataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR, 0)

    phyAddrDataBuffer = SendDiagnostic(vtfContainer, phyAddrDataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    physicalAddress = AddressTypes.PhysicalAddress()

    physicalAddress.block = phyAddrDataBuffer.GetTwoBytesToInt(BLOCK_NUMBER_OFFSET)
    physicalAddress.chip = phyAddrDataBuffer.GetOneByteToInt(CHIP_NUMBER_OFFSET)
    physicalAddress.die = phyAddrDataBuffer.GetOneByteToInt(DIE_NUM_OFFSET)
    physicalAddress.plane = phyAddrDataBuffer.GetOneByteToInt(PLANE_NUMBER_OFFSET)
    physicalAddress.wordLine = phyAddrDataBuffer.GetTwoBytesToInt(WL_NUM_OFFSET)
    if fwConfigData.isBiCS:
        physicalAddress.wordLine = phyAddrDataBuffer.GetOneByteToInt(WL_NUM_OFFSET)
        physicalAddress.string = phyAddrDataBuffer.GetOneByteToInt(STRING_OFFSET)
    physicalAddress.sector = phyAddrDataBuffer.GetOneByteToInt(SECTOR_OFFSET)
    physicalAddress.mlcLevel = 0
    physicalAddress.eccPage = (old_div(physicalAddress.sector, (fwConfigData.sectorsPerEccPage)))
    sectorPositionInEccPage = (physicalAddress.sector % (fwConfigData.sectorsPerEccPage))

    return physicalAddress, sectorPositionInEccPage
#end of GetFilePhysicalLocation

def CloseActiveRange(vtfContainer, startLg = 0, endLg = 0, startOffset = 0, endOffset = 0, bankId = 0):

    opcode = 0xD0
    subOpcode = 1
    commandName = "Manage RBC"

    # get 2-bytes in lsb and msb for startLg
    startLgLsb = startLg & MASK_LOW_WORD
    startLgMsb = (startLg >> 16) & MASK_LOW_WORD

    # get byte for lsb startLgLsb
    startLgLsbByte0 = startLgLsb & MASK_LOW_BYTE
    startLgLsbByte1 = (startLgLsb >> 8) & MASK_LOW_BYTE

    # get byte for Msb startLgMsb
    startLgMsbByte0 = startLgMsb & MASK_LOW_BYTE
    startLgMsbByte1 = (startLgMsb >> 8) & MASK_LOW_BYTE

    # get 2-bytes in lsb and msb for endLg
    endLgLsb = endLg & MASK_LOW_WORD
    endLgMsb = (endLg >> 16) & MASK_LOW_WORD

    # get byte for lsb endLgLsb
    endLgLsbByte0 = endLgLsb & MASK_LOW_BYTE
    endLgLsbByte1 = (endLgLsb >> 8) & MASK_LOW_BYTE

    # get byte for Msb endLgMsb
    endLgMsbByte0 = startLgMsb & MASK_LOW_BYTE
    endLgMsbByte1 = (startLgMsb >> 8) & MASK_LOW_BYTE

    # get lsb and msb for startLgOffset
    startLgOffsetLsb = startOffset & MASK_LOW_BYTE
    startLgOffsetMsb = (startOffset >> 8) & MASK_LOW_BYTE

        # get lsb and msb for endLgOffset
    endLgOffsetLsb = endOffset & MASK_LOW_BYTE
    endLgOffsetMsb = (endOffset >> 8) & MASK_LOW_BYTE

    cdb = [opcode, subOpcode,0,0,
           0,0,0,0,
           startLgLsbByte0,startLgLsbByte1,startLgMsbByte0,startLgMsbByte1,
          endLgLsbByte0,endLgLsbByte1,endLgMsbByte0,endLgMsbByte1,
          startLgOffsetLsb,startLgOffsetMsb,endLgOffsetLsb,endLgOffsetMsb,
          bankId,0,0,0]

    buf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, READ_DATA))
    statusBuffer = SendDiagnostic(vtfContainer, buf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)
#end of CloseActiveRanges

def EvictClosedRanges(vtfContainer):
    commandName = "Evict Closed Ranges"
    opcode = 0xD0
    subOpcode = 2
    cdb = [opcode, subOpcode,0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    buf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, READ_DATA))
    statusBuffer = SendDiagnostic(vtfContainer, buf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)
#end of EvictClosedRanges

def StartDlt( vtfContainer):
    import time as time

    commandName = "Start DLT"
    opcode = 0xFA
    statusBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    cdb = [ opcode, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
           0, 0, 0, 0 ]

    #command parameters:dataBuffer, CDB, 2-for no data cmd, Num of sectors to read
    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, Data Direction: %s" %(opcode, READ_DATA))
    statusBuffer = SendDiagnostic(vtfContainer, statusBuffer, cdb, NO_DATA, SINGLE_SECTOR, opcode, commandName)

    if vtfContainer.isModel:
        cmd=vtfContainer.Livet.GetCmdGenerator()
        cmd.Delay(5,0)
    else:
        time.sleep(5)
#end of StartDlt

def ResumeDlt(vtfContainer):

    #constants
    DELAY_TIME=15  #Delay time for the Resume DLT in seconds

    import time

    commandName = "Resume DLT"
    opcode = 0xFA
    statusBuffer = pyWrap.Buffer.CreateBuffer(1, 0)
    option = 0x1
    cdb = [ opcode, 0, option, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
           0, 0, 0, 0 ]

    statusBuffer = SendDiagnostic(vtfContainer, statusBuffer, cdb, NO_DATA, SINGLE_SECTOR, opcode, commandName)

    if vtfContainer.isModel:
        cmd=vtfContainer.Livet.GetCmdGenerator()
        #Giving the time delay as 15 seconds as suggested by Satya-BEVM-681
        cmd.Delay(DELAY_TIME,0)
    else:
        #Giving the time delay as 15 seconds as suggested by Satya-BEVM-681
        time.sleep(DELAY_TIME)

#end of ResumeDlt()

def SetDltParams( vtfContainer, buf):
    """
         The buffer which contains the DLT parameters
    """
    commandName = "Set DLT Parameters"
    opcode = 0xFB

    cdb = [ opcode, 0, 0, 0,
            0, 0, 0, 0,
            1, 0, 0, 0,
           0, 0, 0, 0 ]

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, Data Direction: %s" %(opcode, READ_DATA))
    dataBuffer = SendDiagnostic(vtfContainer, buf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)
#end of SetDltParams()

def StopDlt( vtfContainer):
    commandName = "Stop DLT"
    opcode = 0xFC
    statusBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    cdb = [ opcode, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
           0, 0, 0, 0 ]

    #command parameters:dataBuffer, CDB, 2-for no data cmd, Num of sectors to read
    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, Data Direction: %s" %(opcode, READ_DATA))
    statusBuffer = SendDiagnostic(vtfContainer, statusBuffer, cdb, NO_DATA, SINGLE_SECTOR, opcode, commandName)
#end of StopDlt

def GetDltStatus(vtfContainer):
    #offset
    DLT_STATE_OFFSET = 0x00
    ELAPSED_LOOP_COUNT_OFFSET = 0x02
    NEXT_LBA_TO_ACCESS_OFFSET = 0x06
    NUM_SECTORS_PROCESSED_IN_LAST_WRITE_READ_OFFSET = 0x0A

    commandName = " Get DLT Status"
    opcode = 0xFD

    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    cdb = [ opcode, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0 ]

    dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    configParams = {"dltState":None, "elapsedLoopCount":None, "nxtLbaToaccess":None, "numSecProcessedInLastWR":None}

    configParams["dltState"] = dataBuffer.GetTwoBytesToInt(DLT_STATE_OFFSET)
    configParams["elapsedLoopCount"] = dataBuffer.GetFourBytesToInt(ELAPSED_LOOP_COUNT_OFFSET)
    configParams["nxtLbaToaccess"] = dataBuffer.GetFourBytesToInt(NEXT_LBA_TO_ACCESS_OFFSET)
    configParams["numSecProcessedInLastWR"] = dataBuffer.GetFourBytesToInt(NUM_SECTORS_PROCESSED_IN_LAST_WRITE_READ_OFFSET)

    return configParams
#end of GetDltStatus

def SetWriteCounterValue(vtfContainer,writeCounterValue):
    """
    Name  :  SetWriteCounterValue
    Description : Sets the RPMB write count value
    Arguments: writeCounterValue : The Value to write counter to be set
    Returns: None
    """
    #offset
    opcode = 0xCA
    subOpcode = 0x15
    # Buffer
    getMMLDataBuf = pyWrap.Buffer.CreateBuffer(1, 0x00)

    commandName = "Set RPMB Count"

    wcNumberHiWord = ByteUtil.HighWord(writeCounterValue)
    mbNumberLoWord = ByteUtil.LowWord(writeCounterValue)

    wcNumberHiWordHiByte = ByteUtil.HighByte(wcNumberHiWord)
    wcNumberHiWordLoByte = ByteUtil.LowByte(wcNumberHiWord)

    mbNumberLoWordHiByte = ByteUtil.HighByte(mbNumberLoWord)
    mbNumberLoWordLoByte = ByteUtil.LowByte(mbNumberLoWord)

    #logger.Info("", "wcNumberHiWordHiByte = %x,wcNumberHiWordHiByte = %x,mbNumberLoWordHiByte = %x,mbNumberLoWordLoByte = %x"%(wcNumberHiWordHiByte,wcNumberHiWordLoByte,mbNumberLoWordHiByte,
                                                                                                                            #  mbNumberLoWordLoByte))

    cdb = [opcode, subOpcode,mbNumberLoWordHiByte,mbNumberLoWordLoByte,
           wcNumberHiWordHiByte,wcNumberHiWordLoByte,0,0,
           0,0,0,0,
          0,0,0,0]

    dataBuffer = SendDiagnostic(vtfContainer, getMMLDataBuf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)
    return


def whetherDRHistoryEnabled(vtfContainer):
    """
    Description:
       * Check if DR history is enabled
    """
    commandName = "Dynamic history"
    offset = 0 #Are history cases stored?  (0 = no, 1 = yes)
    opcode = 0x65
    subopcode = 0x0A
    cdb = [ opcode, 0, subopcode, 0,0, 0, 0, 0,0, 0, 0, 0,0, 0, 0, 0]

    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    historyEnabled = dataBuffer.GetFourBytesToInt(offset)

    if historyEnabled == 1:
        return True
    else:
        return False


def EnableSecureMode(vtfContainer):
    commandName = "Enable Secure Mode"
    opcode = 0x91
    subopcode = 0x0
    cdb = [ opcode,0,subopcode,0,0,0,0,0,0,0,0,0,0,0,0,0]

    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, NO_DATA, SINGLE_SECTOR, opcode, commandName)

    return


def SendDiagnostic(vtfContainer, dataBuffer, cdbData, direction, sectors, opcode=None, commandName = "Diagnostic command", bIsStatusPhase = True, returnStatus = False, increaseTO=False):
    if vtfContainer.isModel:
        livetRoot = vtfContainer._livet.GetRootObject()
    diagCmd = pyWrap.DIAG_FBCC_CDB()
    #cdbData = FormSignedSCTP(cdbData,corrupt)
    diagCmd.cdb = cdbData
    diagCmd.cdbLen = len(cdbData)

    if direction == 0:
        direction = pyWrap.DIRECTION_OUT
        if increaseTO:
            if vtfContainer.isModel:
                currentReadTO = livetRoot.GetVariable("host.read_timeout")
                updatedReadTO = 500*int(currentReadTO)
                vtfContainer.GetLogger().Info("", "[SendDiagnostic] Updating --read_timeout from %d to %d before issuing diag to avoid diag timeout"%(int(currentReadTO), int(updatedReadTO)))
                livetRoot.SetVariable("host.read_timeout", str(updatedReadTO))
                updatedReadTO = livetRoot.GetVariable("host.read_timeout")
                if int(updatedReadTO) != 500*int(currentReadTO):
                    raise TestError.TestFailError(vtfContainer.GetTestName(), "Timeout update did not reflect in Livet Root object")
            else:
                currentReadTO = int(vtfContainer.cmd_line_args.read_timeout)
                updatedReadTO = 2000
                vtfContainer.GetLogger().Info("", "[SendDiagnostic] Updating --read_timeout from %d to %d before issuing diag to avoid diag timeout"%(int(currentReadTO), int(updatedReadTO)))
                #Increasing read TO before calling the diag
                SDWrap.CardSetTimeout(int(vtfContainer.cmd_line_args.init_timeout), int(vtfContainer.cmd_line_args.write_timeout), updatedReadTO)  #Values accepted in millisecs
                reset, write, read = SDWrap.WrapGetCardTimeout()
                if reset != int(vtfContainer.cmd_line_args.init_timeout) or write != int(vtfContainer.cmd_line_args.write_timeout) or read != updatedReadTO:
                    vtfContainer.GetLogger().Error("" , "[Test: Error] SDWrap.WrapGetCardTimeout  returned (%d, %d, %d)"%(reset, write, read))
                    raise TestError.TestFailError(vtfContainer.GetTestName(), "Timeout update did not happen with SDWrap.CardSetTimeout")

    elif direction == 1:
        direction = pyWrap.DIRECTION_IN
        if increaseTO:
            if vtfContainer.isModel:
                currentWriteTO = livetRoot.GetVariable("host.write_timeout")
                updatedWriteTO = 500*int(currentWriteTO)
                vtfContainer.GetLogger().Info("", "[SendDiagnostic] Updating --write_timeout from %d to %d before issuing diag to avoid diag timeout"%(int(currentWriteTO), int(updatedWriteTO)))
                livetRoot.SetVariable("host.write_timeout", str(updatedWriteTO))
                updatedWriteTO = livetRoot.GetVariable("host.write_timeout")
                if int(updatedWriteTO) != 500*int(currentWriteTO):
                    raise TestError.TestFailError(vtfContainer.GetTestName(), "Timeout update did not reflect in Livet Root object")
            else:
                currentWriteTO = vtfContainer.cmd_line_args.write_timeout
                updatedWriteTO = 2000
                vtfContainer.GetLogger().Info("", "[SendDiagnostic] Updating --write_timeout from %s to %d before issuing diag to avoid diag timeout"%(str(currentWriteTO), int(updatedWriteTO)))
                #Increasing write TO before calling the diag
                #SDWrap.CardSetTimeout(int(vtfContainer.cmd_line_args.init_timeout), updatedWriteTO, int(vtfContainer.cmd_line_args.read_timeout))  #Values accepted in millisecs
                #SDWrap.CardSetTimeout(str(vtfContainer.cmd_line_args.init_timeout), updatedWriteTO, str(vtfContainer.cmd_line_args.read_timeout))
                SDWrap.CardSetTimeout(0, updatedWriteTO, 0)
                reset, write, read = SDWrap.WrapGetCardTimeout()
                if reset != str(vtfContainer.cmd_line_args.init_timeout) or write != updatedWriteTO or read != str(vtfContainer.cmd_line_args.read_timeout):
                    vtfContainer.GetLogger().Error("" , "[Test: Error] SDWrap.WrapGetCardTimeout  returned (%d, %d, %d)"%(reset, write, read))
                    raise TestError.TestFailError(vtfContainer.GetTestName(), "Timeout update did not happen with SDWrap.CardSetTimeout")
    else:
        direction = pyWrap.DIRECTION_NONE

    try:
        sctpCommand = pyWrap.SCTPCommand.SCTPCommand(diagCmd, dataBuffer, direction, bIsStatusPhase)
        sctpCommand.Execute()
        vtfContainer.logger.Info("", "[SendDiagnostic] %s issued : %s"%(commandName, [hex(i) for i in cdbData]))
        status = sctpCommand.GetStatusFrame().Status
    except: # TestError.CVFExceptionTypes , exc:
        status = sctpCommand.GetStatusFrame().Status
        vtfContainer.logger.Warning("","[SendDiagnostic] FBCC command %s (0x%X) failed" %(commandName, opcode))
        #vtfContainer.logger.Info("","\n %s"%exc)
        if not returnStatus:
            raise TestError.TestFailError("", "[SendDiagonostic] Failed with exception")

    if increaseTO:
        if vtfContainer.isModel:
            if direction == pyWrap.DIRECTION_OUT:
                vtfContainer.GetLogger().Info("", "[SendDiagnostic] Resetting --read_timeout from %d to %d before issuing diag to avoid diag timeout"%(int(updatedReadTO), int(currentReadTO)))
                livetRoot.SetVariable("host.read_timeout", currentReadTO)
                updatedReadTO = livetRoot.GetVariable("host.read_timeout")
                if updatedReadTO != currentReadTO:
                    raise TestError.TestFailError(vtfContainer.GetTestName(), "Timeout reset did not reflect in Livet Root object")
            elif direction == pyWrap.DIRECTION_IN:
                vtfContainer.GetLogger().Info("", "[SendDiagnostic] Resetting --write_timeout from %d to %d before issuing diag to avoid diag timeout"%(int(updatedWriteTO), int(currentWriteTO)))
                livetRoot.SetVariable("host.write_timeout", currentWriteTO)
                updatedWriteTO = livetRoot.GetVariable("host.write_timeout")
                if updatedWriteTO != currentWriteTO:
                    raise TestError.TestFailError(vtfContainer.GetTestName(), "Timeout reset did not reflect in Livet Root object")
        else:
            vtfContainer.GetLogger().Info("", "[SendDiagnostic] Resetting timeouts to (%d, %d, %d) (resetTO, writeTO, readTO) before issuing diag to avoid diag timeout"%(int(vtfContainer.cmd_line_args.init_timeout), int(vtfContainer.cmd_line_args.write_timeout), int(vtfContainer.cmd_line_args.read_timeout)))
            #Resetting TO after calling the diag
            SDWrap.CardSetTimeout(int(vtfContainer.cmd_line_args.init_timeout), int(vtfContainer.cmd_line_args.write_timeout), int(vtfContainer.cmd_line_args.read_timeout))  #Values accepted in millisecs
            reset, write, read = SDWrap.WrapGetCardTimeout()
            if reset != int(vtfContainer.cmd_line_args.init_timeout) or write != int(vtfContainer.cmd_line_args.write_timeout) or read != int(vtfContainer.cmd_line_args.read_timeout):
                vtfContainer.GetLogger().Error("" , "[Test: Error] SDWrap.WrapGetCardTimeout  returned (%d, %d, %d)"%(reset, write, read))
                raise TestError.TestFailError(vtfContainer.GetTestName(), "Timeout reset did not happen with SDWrap.CardSetTimeout")

    if not returnStatus:
        return dataBuffer
    else:
        return status
#end of SendDiagnostic

def GetDeviceChallenge(vtfContainer, cdb):
    opcode = 0x40
    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,  0)
    commandName = "GetDeviceChallenge"
    status = SendDiagnostic(vtfContainer, dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName, returnStatus = True)
    status = int("0x" + "".join(["%02x" % (i) for i in reversed(status)]), base=16)
    if status != 0:
        
        #raise TestError.TestFailError("", "[SendDiagonostic] %s Failed with exception 0x%x" % (commandName,status))
        raise TestError.TestFailError("", "0x%x" % (status))
        

    return dataBuffer, status



def Unlock(vtfContainer, dataBuffer, cdb):
    opcode = 0x41
    commandName = "Unlock"
    configParser = vtfContainer.device_session.GetConfigInfo()
    configParser.SetValue("sctp_write_time_out_micro_sec", 1200000)
    status = SendDiagnostic(vtfContainer, dataBuffer, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName, increaseTO=False, returnStatus = True)
    configParser.SetValue("sctp_write_time_out_micro_sec", 250000)
    status = int("0x" + "".join(["%02x" % (i) for i in reversed(status)]), base=16)
    if status != 0:
        raise TestError.TestFailError("", "[SendDiagonostic] %s Failed with exception 0x%x" % (commandName,status))    
    return status


def FormSignedSCTP(cdb, corrupt=False):
    '''
    Approach for now:
    Create a separate  API (FormSignedSCTP) 
    Call: FormSignedSCTP(cdb) pass the cdb buffer created previously
    Inside FormSignedSCTP append RSA signature to cdb buffer. ( Also make cdb size = 432)
    -----------------------------------------------  |
    CDB (16B)                                        |
    -----------------------------------------------  | 432 Bytes
    APPLICATION SPECIFIC DATA (160B)                 |
    -----------------------------------------------  |
    SIGNATURE (256B)Signed with Product Private Key  |

    RSA signature to be obtained by RSA(SHA256(SCTP sign + App Sign), private key) 
    '''
    app_specific_data = [0] * 160; #App Specific data is 416 bytes excluding CDB, including CDB, it is 432 bytes
    #For Signed SCTP, set the final 256 bytes with RSA signature value
    #sctp_rsa_signature = self.GetSCTPRSASignature()
    #Extend app specific data, include sctp sign
    #sctp_rsa_signature_Hex = ''.join(x.encode('hex') for x in sctp_rsa_signature)
    #sctp_rsa_signature_bytes = self.FromHexStringArrayToByteArray(sctp_rsa_signature_Hex)

    #Comment this hardcoded signature and use our own calculated signature once Private keys are known.
    #Otherwise don't make it complex, take final precomputed signature from FW and hard code it.
    """
    sctp_rsa_signature_bytes = [
           0xb6, 0xa1, 0xf5, 0xba, 0xfe, 0xd8, 0xff, 0x24, 0x20, 0x7f, 0x19, 0x4f, 0x8d, 0x9e, 0x00, 0x88,
           0x2f, 0xb9, 0x0a, 0x9e, 0x83, 0x53, 0x44, 0xe6, 0x4d, 0xcd, 0xb2, 0x79, 0x9d, 0xd8, 0x4d, 0x49,
           0xb5, 0x82, 0xfb, 0x1e, 0xd8, 0x40, 0x5d, 0x9c, 0x6f, 0xc7, 0x9e, 0x58, 0x55, 0xe5, 0xb5, 0x40,
           0x9e, 0x4b, 0x67, 0xb3, 0xd7, 0x17, 0x79, 0x9a, 0x7d, 0x97, 0xae, 0x84, 0x48, 0xf3, 0xf4, 0x0a,
           0xc9, 0x61, 0xf6, 0xdc, 0xe5, 0x6f, 0xfa, 0xea, 0x30, 0xbf, 0x43, 0x07, 0xa8, 0x4d, 0xb2, 0x27,
           0x6d, 0x49, 0x59, 0x4b, 0x42, 0xc2, 0x70, 0x1b, 0x5e, 0x62, 0xa7, 0x93, 0x15, 0x9f, 0x19, 0xe7,
           0xd0, 0xa2, 0x98, 0x56, 0x22, 0x5c, 0xaa, 0x03, 0x3c, 0x0d, 0x54, 0xaa, 0xaa, 0x6d, 0x3f, 0xa5,
           0x3c, 0x52, 0xf1, 0x98, 0xc5, 0xd3, 0x3b, 0x9d, 0x1f, 0x17, 0xe3, 0x10, 0x48, 0xd7, 0xbc, 0x2c,
           0xcc, 0x88, 0x30, 0x1b, 0x52, 0xb8, 0xe3, 0x83, 0xe8, 0x25, 0xa0, 0xed, 0x03, 0x81, 0xb7, 0xe0,
           0xa5, 0x1f, 0x66, 0x2d, 0x00, 0xac, 0xf7, 0x3d, 0x51, 0xd6, 0xce, 0x99, 0x51, 0xbd, 0x85, 0x9f,
           0x1b, 0x61, 0xd2, 0xe1, 0x8c, 0x4e, 0xf5, 0x7d, 0xe5, 0xa2, 0x0e, 0x87, 0xe8, 0x6b, 0x3c, 0x99,
           0xd2, 0xf3, 0x29, 0xc3, 0x3e, 0x1f, 0xfe, 0x30, 0x69, 0x64, 0xb2, 0xb5, 0xa8, 0xb4, 0xbb, 0x30,
           0xc9, 0x50, 0x94, 0x28, 0x91, 0x73, 0x93, 0xf1, 0x00, 0x81, 0x0b, 0xfc, 0x15, 0x0f, 0x41, 0xd6,
           0x2a, 0x65, 0x49, 0x6b, 0xa4, 0x8f, 0x64, 0xea, 0x8c, 0x38, 0x31, 0x8b, 0x2e, 0xc9, 0xe7, 0x6d,
           0xe1, 0x2b, 0x41, 0x54, 0x69, 0xbb, 0xe5, 0x33, 0x95, 0xda, 0xdd, 0x3d, 0xad, 0x33, 0x08, 0xa7,
           0x7b, 0x5a, 0xb4, 0x40, 0x73, 0xea, 0x7c, 0x61, 0xa5, 0x79, 0x9a, 0xd7, 0xe3, 0x12, 0xa5, 0xef]
    """
    #SCTP from release keys
    global SCTP_RSA_Signature
    if corrupt:
        SCTP_RSA_Signature[0] = SCTP_RSA_Signature[0] ^ 0xFF		

    app_specific_data.extend(SCTP_RSA_Signature)
    #Add the app specific data to the cdb
    cdb.extend(app_specific_data)
    return cdb

def MoveToLock(vtfContainer):
    opcode = 0x42
    subOpcode = 0x00
    cdb = [ opcode, subOpcode,0, 0,
           0, 0, 0, 0,
           0, 0, 0, 0,
           0, 0, 0, 0
           ]   
    commandName = "MoveToLock"
    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,  0)
    SendDiagnostic(vtfContainer, dataBuffer, cdb, NO_DATA, SINGLE_SECTOR, opcode, commandName)

    return   



def GetDeviceState(vtfContainer, cdb=None):
    """
    Issue this Diagnostic using SecurityUtils!!!!!!!
    Security Utils has the implementation to compute cdb and signature
    opcode = 0x43
    subOpcode = 0x00
    """     
    opCode = 0x43
    subOpcode = 0x0
    options = 0x0 
    if cdb is None:
        cdb = [opCode,subOpcode,options,0,0,0,0,0,0,0,0,0,0,0,0,0]        
    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,  0)
    commandName = "GetDeviceState"
    dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opCode, commandName)


    return dataBuffer.GetOneByteToInt(0)

def GetFBLEntry(vtfContainer,index,blockType,addrType):
    """
    Name:                   GetMetaBlockNum
    Description:            Calculating the metablock number from the physical location
    Inputs:
        vtfContainer:             Card Test Space
        index:                 Index of FBL array
        blockType:             MLC (=1) or SLC (=0) block
        addrType:              type of address to return (=0 MetaBlockNumber) (=1 Physical)

    Outputs:
        metaBlockNum           The metablock number
        or
        PhysicalAddr           The physical address

    Note: This function is not fully complete. The upper bits of chip,die and plane are
    not included which calculating the metablock number. This function is applicable as of now
    as we dont have bigger chip numbers(greater than 3)
    """

    mmlDataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,  0)
    opcode = 0xC9
    subOpcode = 32

    ##option = (index<<8) + blockType
    ##optionEx = addrType
    ##bank=0
    ##cdbData = [opcode,subOpcode,option,option>>8,optionEx,0,0,0,0,0,bank,0,0,0,0,0]

    cdbData = [opcode,subOpcode,blockType,index,
               0,0,0,0,
               0,0,0,0,
              0,0,0,0]
    SendDiagnostic(vtfContainer, mmlDataBuffer , cdbData , READ_DATA , SINGLE_SECTOR, opcode)

    if (addrType == 0):
        return mmlDataBuffer.GetTwoBytesToInt(0)
    else:
        chip    = mmlDataBuffer.GetOneByteToInt(17)
        die     = mmlDataBuffer.GetOneByteToInt(18)
        plane   = mmlDataBuffer.GetOneByteToInt(19)
        block   = mmlDataBuffer.GetTwoBytesToInt(20)
        page    = mmlDataBuffer.GetTwoBytesToInt(22)
        eccPage = mmlDataBuffer.GetOneByteToInt(24)
        return (chip,die,plane,block,page,eccPage)

#end of GetFBLEntry

GET_IP_INFO_OPCODE = 0xF5
GET_IP_INFO_SELECT_BE_IP = 0x20
GET_IP_INFO_MAX_BAD_COL_OFFSET = 0x4A

def GetMaxBadColInfo(vtfContainer):
    logger = vtfContainer.GetLogger()

    getIpInfoDataBuf = pyWrap.Buffer.CreateBuffer(1, 0x0)

    opCode = GET_IP_INFO_OPCODE # 0xF5 GET IP Info
    ipSelect = GET_IP_INFO_SELECT_BE_IP # 0x20 IP=BE
    ipSelectLsb = ByteUtil.LowByte(ipSelect)
    ipSelectMsb = ByteUtil.HighByte(ipSelect)

    cdb = [opCode,0,ipSelectLsb,ipSelectMsb,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    logger.Info("", "[GetMaxBadColInfo] Calling GetIPInfo Diag Function with Opcode 0xF5, ipSelect 0x20")

    BadBlockInfo = getIpInfoDataBuf.GetFourBytesToInt(GET_IP_INFO_MAX_BAD_COL_OFFSET)
    logger.Debug("", "[GetMaxBadColInfo] Bad Block Info : 0x%X"%(BadBlockInfo & 0xff))
    maxBadBlkColumns = 0
    if (BadBlockInfo & 0x80):
        maxBadBlkColumns = BadBlockInfo & 0x7f

    return maxBadBlkColumns

def IsDelayedPFHandlingEnabledInBCUB(vtfContainer):
    """
    Name        :IsDelayedPFHandlingEnabledInBCUB
    Description :This function returns True if Delayed PF Handling feature is enabled, False Otherwise
    It returns two values, one for BC and another for UB
    Arguments   :vtfContainer - Test space of the card
    Returns     : A tuple of 2 elements
    1. True if Delayed PF handling is enabled in BC, False Otherwise
    2. True if Delayed PF handling is enabled in UB, False Otherwise
    """

    logger = vtfContainer.GetLogger()

    # Diagnostic - Get BE Build Features (0xD1)
    # Offset 0x1B - if set delayed PF handling in UM is enabled.
    # Offset 0x1C - if set delayed EH in BC is enabled.
    DELAYED_EH_IN_BC_ENABLED_OFFSET = 0x1B
    DELAYED_PF_HANDLING_IN_UM_ENABLED_OFFSET = 0x1C

    getBEFeaturesBuf = pyWrap.Buffer.CreateBuffer(1, 0x00)

    opCode = DIAG_GET_BE_BUILD_FEATURES
    subOpcode = 0x00
    cdb = [opCode, 0,subOpcode, 0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    SendDiagnostic(vtfContainer, getBEFeaturesBuf,cdb,READ_DATA,SINGLE_SECTOR, opCode)

    delayedEHInBCEnabled = False
    delayedPFHandlingInUMEnabled = False

    if(getBEFeaturesBuf.GetOneByteToInt(DELAYED_EH_IN_BC_ENABLED_OFFSET) != 0):
        delayedEHInBCEnabled = True
        logger.Info("", "[IsDelayedPFHandlingEnabled] Delayed PF Handling is Enabled in BC")
    if(getBEFeaturesBuf.GetOneByteToInt(DELAYED_PF_HANDLING_IN_UM_ENABLED_OFFSET) != 0):
        delayedPFHandlingInUMEnabled = True
        logger.Info("", "[IsDelayedPFHandlingEnabled] Delayed PF Handling is Enabled in UB")

    return delayedEHInBCEnabled,delayedPFHandlingInUMEnabled
# End of IsDelayedPFHandlingEnabledInBCUB()

def CheckSFS(vtfContainer):
    """
    To Do change this header information
    Name        :CheckSFS
    Description :This function returns True if SFS is enabled and also returns Metablock addresses for Primary and Secondary FS from RW Area,
    False otherwise
    Arguments   :vtfContainer - Test space of the card
    Returns     : A tuple of 5 elements
    1. True if SFS is enabled
    2. Metablock addresses for Primary FS from RW area i.e priSFSMetaBlockAddr1
    3  Metablock addresses for Primary FS from RW area i.e priSFSMetaBlockAddr2
    4  Metablock addresses for Secondary FS from RW area i.e secSFSMetaBlockAddr1
    5  Metablock addresses for Secondary FS from RW area i.e secSFSMetaBlockAddr2
    """
    SFS_RW_PRIFSMETABLKADDRESS1_OFFSET = 0
    SFS_RW_PRIFSMETABLKADDRESS2_OFFSET = 4
    SFS_RW_SECFSMETABLKADDRESS1_OFFSET = 8
    SFS_RW_SECFSMETABLKADDRESS2_OFFSET = 12
    SFS_RW_ENABLED = 16
    FILE_14_SPLIT_FS_ENABLE_OFFSET = 0x29

    logger = vtfContainer.GetLogger()
    #Check if SFS is enabled in File 14 and then call the Diag. The diag might fail if SFS is not enabled
    rdBuf = pyWrap.Buffer.CreateBuffer(1)

    priSFSMetaBlockAddr1 = priSFSMetaBlockAddr2 = secSFSMetaBlockAddr1 = secSFSMetaBlockAddr2 = 0xFFFFFFFF
    #vtfContainer.GetCard().ReadFile(rdBuf, 14, 1)
    rdBuf = ReadFileSystem(vtfContainer,14,1)
    confFlags = rdBuf.GetOneByteToInt(FILE_14_SPLIT_FS_ENABLE_OFFSET)
    if (confFlags & 0x04 == 0x04):
        singleSector = 1
        # set CDB
        opcode = GET_FS_DATA_FW_DIAG_OPCODE
        subOpcode = GET_SFS_FS_METABLOCKS_SUBOPCODE
        cdb = [ opcode, 0, subOpcode, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
              0, 0, 0, 0
              ]

        commandName = "Get FS Data(0x%X)SubOpcode - %d " %(GET_FS_DATA_FW_DIAG_OPCODE, GET_SFS_ENABLED_SUBOPCODE)
        #SFSData = pyWrap.Buffer.CreateBuffer(singleSector)
        SFSData = pyWrap.Buffer.CreateBuffer(singleSector)

        try:# issue the Diagnostic command
            SendDiagnostic(vtfContainer,SFSData,cdb,0,singleSector,opcode)
            logger.Debug("", "Get FS-Data Diagnostic was called..")
        except:
            logger.Debug("", "Split FS Enabled = False")
            raise TestError.TestFailError(vtfContainer.GetTestName(), "[ReadFWParameters] Diagnostic command Read FirmWare Parameters(0x%X) failed - Assuming that SFS is disabled"%GET_FS_DATA_FW_DIAG_OPCODE)


        priSFSMetaBlockAddr1= SFSData.GetFourBytesToInt(SFS_RW_PRIFSMETABLKADDRESS1_OFFSET,0)#Get the data from Big Endian (word swap) Format
        priSFSMetaBlockAddr2= SFSData.GetFourBytesToInt(SFS_RW_PRIFSMETABLKADDRESS2_OFFSET,0)#Get the data from Big Endian (word swap) Format
        secSFSMetaBlockAddr1= SFSData.GetFourBytesToInt(SFS_RW_SECFSMETABLKADDRESS1_OFFSET,0)#Get the data from Big Endian (word swap) Format
        secSFSMetaBlockAddr2= SFSData.GetFourBytesToInt(SFS_RW_SECFSMETABLKADDRESS2_OFFSET,0)#Get the data from Big Endian (word swap) Format
        if IsLargeMetablockUsed(vtfContainer)[0]:
            priSFSMetaBlockAddr1=priSFSMetaBlockAddr1<<32
            priSFSMetaBlockAddr2=priSFSMetaBlockAddr2<<32
            secSFSMetaBlockAddr1=secSFSMetaBlockAddr1<<32
            secSFSMetaBlockAddr2=secSFSMetaBlockAddr2<<32
        logger.Debug("", "Primary FS MB Address 1 = 0x%x" %(priSFSMetaBlockAddr1))
        logger.Debug("", "Primary FS MB Address 2 = 0x%x" %(priSFSMetaBlockAddr2))
        logger.Debug("", "Secondary FS MB Address 1 = 0x%x" %(secSFSMetaBlockAddr1))
        logger.Debug("", "Secondary FS MB Address 2 = 0x%x" %(secSFSMetaBlockAddr2))

        if ( SFSData.GetOneByteToInt(SFS_RW_ENABLED) == 1):
            logger.Debug("", "Split FS Enabled = True")
            return True,priSFSMetaBlockAddr1,priSFSMetaBlockAddr2,secSFSMetaBlockAddr1,secSFSMetaBlockAddr2
        else:
            logger.Debug("", "Split FS Enabled = False")
            return False,priSFSMetaBlockAddr1,priSFSMetaBlockAddr2,secSFSMetaBlockAddr1,secSFSMetaBlockAddr2
    else:
        logger.Debug("", "Split FS Enabled = False")
        return False,priSFSMetaBlockAddr1,priSFSMetaBlockAddr2,secSFSMetaBlockAddr1,secSFSMetaBlockAddr2

    return
# End of CheckSFS()



def ForceGC(vtfContainer, enable=1,urgent=0):
    """
    Diagnostic to Enable/Disable Force GC
    Disable =0
    Enable = 1
    """
    opcode = SET_MML_DATA
    subOpcode = 27
    option1=enable  #
    option2=urgent
    cdbData = [opcode,subOpcode,option1,0,option2,0,0,0,0,0,0,0,0,0,0,0]
    direction = WRITE_DATA
    data_buf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    SendDiagnostic(vtfContainer, data_buf, cdbData, direction, DIAG_SECTORLENGTH, SET_MML_DATA,
                   commandName="Force GC")
    import GCBalancingUtils
    import ValidationSpace
    validationSpace    = ValidationSpace.ValidationSpace(vtfContainer)
    FwConfigData       = validationSpace.GetFWConfigData()
    GCBalUtils         = GCBalancingUtils.GCBalancingUtils(vtfContainer, FwConfigData )
    GCBalUtils.BalancedGCThreshold = GetFreeMLCBlockCount(vtfContainer)
    GCBalUtils.AcceleratedGCThreshold = GCBalUtils.BalancedGCThreshold - 6
    GCBalUtils.UrgentGCThreshold = GCBalUtils.BalancedGCThreshold - 9
    GCBalancingUtils.BALANCED_GC_THRESHOLD = GCBalUtils.BalancedGCThreshold



    return

def ForceGATGC(vtfContainer, enable=1, urgent=0):
    """
    Diagnostic to Enable/Disable Force GC
    Disable =0
    Enable = 1
    """
    opcode = SET_MML_DATA
    subOpcode = 29
    option1=enable  #
    option2=urgent
    cdbData = [opcode,subOpcode,option1,option2,0,0,0,0,0,0,0,0,0,0,0,0]
    direction = WRITE_DATA
    data_buf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    SendDiagnostic(vtfContainer, data_buf, cdbData, direction, DIAG_SECTORLENGTH, SET_MML_DATA,
                   commandName="Force GAT GC")



    return


def IsSecondaryUBPresent(vtfContainer, primaryMBNumber, seqPairing = False):
    """
    return true is secondry is present
    """
    opcode = GET_MML_DATA
    subOpcode = 49
    option = 0
    optionEx = primaryMBNumber
    direction = READ_DATA
    cdbData = [opcode,subOpcode,option,0,
               ByteUtil.LowByte(ByteUtil.LowWord(optionEx)),ByteUtil.HighByte(ByteUtil.LowWord(optionEx)),
               ByteUtil.LowByte(ByteUtil.HighWord(optionEx)),ByteUtil.HighByte(ByteUtil.HighWord(optionEx)),
              0,0,0,0,0,0,0,0]
    data_buf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR, 0xFF)
    SendDiagnostic(vtfContainer, data_buf, cdbData, direction, DIAG_SECTORLENGTH, GET_MML_DATA,
                   commandName="Is Secondry UB present")

    present = data_buf.GetOneByteToInt(0)
    seqPairingEnabled = data_buf.GetOneByteToInt(2)

    if seqPairing:
        return seqPairingEnabled
    else:
        return present



def GetNumOfAvailableMB(vtfContainer):
    """
    Name : GetNumOfAvailableMB()

    Description : This function calls "Get MML Data diag(0xC9)", gives total available meta blocks.

    Arguments :
              vtfContainer - vtfContainer Object

    Returns :
             numOfMetaBlocks : total available meta blocks

    opcode = 0xC9

    subOpcode = 0x8
    """
    #offset
    NUM_OF_AVAILABLE_MBs_OFFSET = 0

    commandName = "Get MML Data"
    mmlDataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    opcode = 0xC9
    subOpcode = 0x8

    cdbData = [opcode,subOpcode,0,0,
               0,0,0,0,
               0,0,0,0,0,0,0,0]

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: 0x%X, Data Direction: %s" %(opcode, subOpcode, READ_DATA))

    mmlDataBuffer = SendDiagnostic(vtfContainer, mmlDataBuffer, cdbData, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    numOfMetaBlocks = mmlDataBuffer.GetTwoBytesToInt(NUM_OF_AVAILABLE_MBs_OFFSET)

    return numOfMetaBlocks
#end of GetNumOfAvailableMB

def GetMaxSetsFromBEConfPerformance(vtfContainer):
    """
    Name : GetMaxSetsFromBEConfPerformance()
    Description :
       This Function will return the Maximum Sets from BE Configurable Performance
    Arguments:
       None
    Return:
       MaxSets
    """

    CurrentSet,maxSets = SetBEConfigurablePerformance(vtfContainer)

    return maxSets
# End of GetMaxSetsFromBEConfPerformance

def SetBEConfigurablePerformance(vtfContainer, setConfig = 0, displayLog=True):
    """
    Name : SetBEConfigurablePerformance()
    Description : This Function will set BE Configurable Performance
    Arguments:
       SetConfig - Which set needs to be set
    (Defalut Value for SetConfig -Set 0)
    Returns:
     CurrentSet : The set we want to config
     maxSets    : Number of Maximum sets configuration avilable
    """

    commandName = "SetBEConfigurablePerformance"

    opcode    = READ_CONFIGURABLE_PERFORMANCE_SET
    subOpcode = setConfig

    cdb = [opcode,subOpcode,0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    # Create Buffer
    Buf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,'a')

    # Call Send Diag
    Buf = SendDiagnostic( vtfContainer, Buf, cdb, READ_DATA, SINGLE_SECTOR, commandName)

    # Define logger
    logger = vtfContainer.GetLogger()

    currentSet = Buf.GetOneByteToInt(iniReaderObj.BE_CONF_PERF_SETS_OFFSET)
    maxSets    = Buf.GetOneByteToInt(iniReaderObj.BE_CONF_PERF_MAX_NO_OF_SETS_OFFSETS)
    if (currentSet == setConfig):
        if displayLog:
            logger.Info("", "[%s] Successfully configured - we are try to set SetConfig as:%d and the Diag returns the Current Config as:%d (Both are same)" %(commandName, setConfig, currentSet))
    else:
        logger.Info("", "[%s] Expectation didn't meet - we are try to set SetConfig as:%d But the Diag returns the Current Config as:%d (Both should be same)" %(commandName, setConfig, currentSet))
        raise TestError.TestFailError(vtfContainer.GetTestName(), "Required set of configuration is not setting up properly using BEConfigurable performance Diag")
    if (maxSets <= 0):
        logger.Info("", "[%s] MaxSets for the product is not returning the proper value setconfig %d - currentSet - %d" %(commandName, setConfig, currentSet))
        raise TestError.TestFailError(vtfContainer.GetTestName(), "MaxSets for the product is not returning the proper value - Check Diag(0xF6) offsets ")
    return currentSet, maxSets

# End of SetBEConfigurablePerformance


def DFDErrorLogStartByteOffset(vtfContainer):
    """
    Name : DFDErrorLogStartByteOffset()
    Description : This Function will give the starting/first Byte offset of the DFD Error Log Info
    Arguments:
       subopcode - None
    Returns:
       MBA - starting/first Byte offset of the DFD Error Log Info.
    """
    commandName = "DFDErrorLogStartByteOffset"
    opcode    = 0x65
    subOpcode = 0xD
    cdb = [opcode,0x0,subOpcode,0x0, 0x00,0x0,0x0,0x0, 0x0,0x0,0x0,0x0, 0x0,0x0,0x0,0x0]

    DFDBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: 0x%X, Data Direction: %s" %(opcode, subOpcode, READ_DATA))
    DFDOffsetInfo = SendDiagnostic(vtfContainer, DFDBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    StartingByteOffset = DFDOffsetInfo.GetTwoBytesToInt(0x0)

    return StartingByteOffset



def Purge_MLC_Blocks(vtfContainer, spareBlockCount =0):
    """
    This diagnostic removes the extra MLC blocks so that the
    device can be scaled down without extra MLC blocks
    """
    commandName = "Diagnostic to scale the number of blocks down as per card capacity"

    opcode = 0xCA
    subOpcode = 28
    dataBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    bankNum = 0
    option = spareBlockCount
    optNumberLo = ByteUtil.HighByte(option)
    optNumberHi = ByteUtil.LowByte(option)
    cdb = [opcode,subOpcode,optNumberHi,optNumberLo,
           0,0,0,0,
           0,0,bankNum,0,
          0,0,0,0]

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, READ_DATA))
    statusBuffer = SendDiagnostic(vtfContainer, dataBuf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)


def GetWritePosition(vtfContainer,displayLog=False):
    """
    Name : GetWritePosition()
    Description : This Function will Get the write position
    Arguments:
       subopcode - None
    Returns:
       MBA - Current Meta Block Address for all the open UBs, GAT & GC Context blocks.(Both Primary & Secondary).
    """
    commandName = "GetWritePosition"
    READ_WRITE_POSITION = 0x27
    MBAList     = []

    MB_NUM_OFFSET = 8
    SECTOR_OFFSET = 8

    opcode      = GET_MML_DATA
    subOpcode   = READ_WRITE_POSITION

    vtfContainer.GetLogger().Info("", "[%s] Issue Diag CMD Get Write Position"%(commandName))

    cdb = [opcode,subOpcode,0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    #Create Buffer
    Buf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    #Call Send Diag
    Buf = SendDiagnostic( vtfContainer, Buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    MBNum = 0
    SecOff = 4
    while Buf.GetFourBytesToInt(MBNum)!= 0 :
        entry = (Buf.GetFourBytesToInt(MBNum), Buf.GetFourBytesToInt(SecOff))
        MBAList.append(entry)
        MBNum += MB_NUM_OFFSET
        SecOff += SECTOR_OFFSET
    #Added for to Get Src SLC MB and Src MLC MB selected for compaction
    slcGC_Src_Selected = Buf.GetFourBytesToInt(MBNum)
    mlcGC_Src_Selected = Buf.GetFourBytesToInt(SecOff)
    if displayLog:
        vtfContainer.GetLogger().Info("", "[%s] Diag CMD Get Write Position was sent successfully "%commandName)
    return MBAList, slcGC_Src_Selected, mlcGC_Src_Selected
#End of GetWritePosition
#End of File
def CleanUpSequence(vtfContainer,subOpCode):
    commandName = "CleanUpSequence"
    opcode    = 0xA6
    subOpcode = subOpCode
    cdb = [opcode,0x0,subOpcode,0x0,
           0x00,0x0,0x0,0x0,
           0x0,0x0,0x0,0x0,
          0x0,0x0,0x0,0x0]

    Buf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    #SendDiagnostic(vtfContainer, Buf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)
    SendDiagnostic(vtfContainer, Buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    return


def SetPollingMode(vtfContainer):
    commandName = "SetPollingMode"
    opcode    = 0xA6
    subOpcode = 0x1
    cdb = [opcode,0x0,subOpcode,0x0,
           0x00,0x0,0x0,0x0,
           0x0,0x0,0x0,0x0,
          0x0,0x0,0x0,0x0]

    Buf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    SendDiagnostic(vtfContainer, Buf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)

    return


def GetPollingMode(vtfContainer):
    """
    typedef enum
    {
       NOT_ACTIVE = 0,      //Host  must configure
       SHRACK_MODE,          //Polling mode is active
       TANISYS_MODE        //In this mode we do not polling!!!
    } POLLING_MODE_e;
    When polling mode is set it is in "SHRACK_MODE", when cleared it is "NOT_ACTIVE"
    """
    commandName = "GetPollingMode"
    opcode    = 0xA6
    subOpcode = 0x2
    cdb = [opcode,0x0,subOpcode,0x0,
           0x00,0x0,0x0,0x0,
           0x0,0x0,0x0,0x0,
          0x0,0x0,0x0,0x0]

    Buf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    SendDiagnostic(vtfContainer, Buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    status = Buf.GetOneByteToInt(0x6)

    return status

def SedInjectError(vtfContainer):
    """
    Description:
       * Injects bit flips on the given RAM location
    """
    commandName = "SedInjectError"
    opcode    = 0x60
    subOpcode = 0x0
    cdb = [opcode,0x0,subOpcode,0x0,
           0x00,0x0,0x0,0x0,
           0x0,0x0,0x0,0x0,
          0x0,0x0,0x0,0x0]

    Buf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    SendDiagnostic(vtfContainer, Buf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)

    return


def ReadPort(vtfContainer,addr,byteCount):
    """
    Description:
       * Reads data from the given RAM location
    """
    commandName = "ReadPort"
    opcode    = 0x8D
    cdb = [opcode,0x0,0x0,0x0,
           ByteUtil.LowByte(ByteUtil.LowWord(addr)),ByteUtil.HighByte(ByteUtil.LowWord(addr)),
           ByteUtil.LowByte(ByteUtil.HighWord(addr)),ByteUtil.HighByte(ByteUtil.HighWord(addr)),
          ByteUtil.LowByte(ByteUtil.LowWord(byteCount)),ByteUtil.HighByte(ByteUtil.LowWord(byteCount)),
          ByteUtil.LowByte(ByteUtil.HighWord(byteCount)),ByteUtil.HighByte(ByteUtil.HighWord(byteCount)),
          0x0,0x0,0x0,0x0]

    if old_div(byteCount,BE_SPECIFIC_BYTES_PER_SECTOR) > 0:
        sector_count = old_div(byteCount,BE_SPECIFIC_BYTES_PER_SECTOR)
    else:
        sector_count = 1

    Buf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR * sector_count)
    SendDiagnostic(vtfContainer, Buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    return Buf


def WritePort(vtfContainer,addr,byteCount,buf):
    """
    Description:
       * Writes data to the given RAM location
    """
    commandName = "WritePort"
    opcode    = 0x8C
    cdb = [opcode,0x0,0x0,0x0,
           ByteUtil.LowByte(ByteUtil.LowWord(addr)),ByteUtil.HighByte(ByteUtil.LowWord(addr)),
           ByteUtil.LowByte(ByteUtil.HighWord(addr)),ByteUtil.HighByte(ByteUtil.HighWord(addr)),
          ByteUtil.LowByte(ByteUtil.LowWord(byteCount)),ByteUtil.HighByte(ByteUtil.LowWord(byteCount)),
          ByteUtil.LowByte(ByteUtil.HighWord(byteCount)),ByteUtil.HighByte(ByteUtil.HighWord(byteCount)),
          0x0,0x0,0x0,0x0]

    SendDiagnostic(vtfContainer, buf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)

    return


def SetCacheStatus(vtfContainer,pageType=0,pageNum=0,dirty=0,reserved=0):
    """
    Description:
       * Set the Gat cache pages as dirty/reserved
    """
    commandName="SetCacheStatus"
    opcode=0xc9
    subOpcode=64
    cacheBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    pageTypeLo = ByteUtil.HighByte(pageType)
    pageTypeHi = ByteUtil.LowByte(pageType)

    pageNumLo = ByteUtil.HighByte(pageNum)
    pageNumHi = ByteUtil.LowByte(pageNum)

    cdb = [opcode,subOpcode,pageTypeHi,pageTypeLo,
           pageNumHi,pageNumLo,dirty,reserved,
           0,0,0,0,
          0,0,0,0]

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, READ_DATA))
    cacheBuf = SendDiagnostic(vtfContainer, cacheBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    return


def GetOmwEntryThreshold(vtfContainer):
    """
    Description:
       * Set the Gat cache pages as dirty/reserved
    """
    OmwEntryThreshold = 1

    return OmwEntryThreshold



def GetOMREntryThreshold(vtfContainer):
    """
    Description:
       * Set the Gat cache pages as dirty/reserved
    """
    OmrEntryThreshold = 4

    return OmrEntryThreshold


def GetOMRContinueThreshold(vtfContainer):
    """
    Description:
       * Set the Gat cache pages as dirty/reserved
    """
    OmrEntryThreshold = 2

    return OmrEntryThreshold


def GetCurrentQueueDepth(vtfContainer):
    """
    Description:
       * Set the Gat cache pages as dirty/reserved
    """
    commandName="GetCurrentQueueDepth"
    opcode=0xA9
    subOpcode=0
    outputBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    cdb = [opcode,subOpcode,0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, READ_DATA))
    outputBuf = SendDiagnostic(vtfContainer, outputBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    currentQueueDepth = outputBuf.GetTwoBytesToInt(0x0)

    return currentQueueDepth


def GetCacheInfo(vtfContainer):
    """
    Description:
       * Returns the pages that are cached
    """
    commandName="GetCacheInfo"
    opcode=0xc9
    subOpcode=63
    cacheBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    cdb = [opcode, subOpcode, 0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, READ_DATA))
    cacheBuf = SendDiagnostic(vtfContainer, cacheBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    GatPage = []
    GatDirPage = []
    IgatPage = []
    RgatPage = []
    RgatDirPage = []

    offset = 0
    for count in range(0,15):
        offset = count * 8
        tempPage = []
        pageId = cacheBuf.GetTwoBytesToInt(offset)
        tempPage.append(cacheBuf.GetTwoBytesToInt(offset))
        tempPage.append(cacheBuf.GetTwoBytesToInt(offset+2))
        tempPage.append(cacheBuf.GetOneByteToInt(offset+4))
        tempPage.append(cacheBuf.GetOneByteToInt(offset+5))
        tempPage.append(cacheBuf.GetOneByteToInt(offset+6))
        tempPage.append(cacheBuf.GetOneByteToInt(offset+7))

        if pageId == Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_GAT_PAGE_HEADER:
            GatPage.append(tempPage)

        elif pageId == Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_GAT_DIRECTORY_PAGE_HEADER:
            GatDirPage.append(tempPage)

        elif pageId == Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_IGAT_PAGE_HEADER:
            IgatPage.append(tempPage)

        elif pageId == Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_RGAT_PAGE_HEADER:
            RgatPage.append(tempPage)

        elif pageId == Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_RGAT_DIRECTORY_PAGE_HEADER:
            RgatDirPage.append(tempPage)

    return GatPage,GatDirPage,IgatPage,RgatPage,RgatDirPage


def GetPreErasedBlocksList(vtfContainer, metaPlane, blockType = 0):
    """
    Name : GetPreErasedBlocksList()

    Description : This function calls "Get MML Data diag(0xC9)", gives Pre Erased blocks list.

    Arguments :
              vtfContainer - vtfContainer Object
              metaPlane - Meta plane Number
              blockType - block type SLC/TLC
    Returns :
             List of pre-erased blocks MB numbers
    opcode : 0xC9
    subopcode : 0X3A

    """
    #offset

    commandName = "Get Pre-Erased Blocks List"

    getPreErasedBlocksListBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR, 0x0)
    opcode = 0xC9      #Get MML data opCode 0xc9
    subOpcode = 0x3A   #Sub opcode for Pre-erased blocks list 0x3A

    cdb = [opcode, subOpcode, metaPlane, 0,
           0, 0, 0, 0,
           0, 0, 0, blockType,
          0, 0, 0, 0]

    getPreErasedBlocksListBuf = SendDiagnostic(vtfContainer, getPreErasedBlocksListBuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    preErasedBlockList = []
    offset = 0
    for i in range(0, 5):
        mbNum = getPreErasedBlocksListBuf.GetTwoBytesToInt(offset)
        if mbNum == 0xFFFF:
            break
        preErasedBlockList.append(mbNum)
        offset += 4

    return preErasedBlockList
def GetIGATFreeBlockCount(vtfContainer,bankNumber=0):
    """
    Description:
       * Gets the free block count of SLC and MLC
    """
    # Offsets
    GET_FREE_BLOCK_COUNT_OPCODE = 0xC9
    GET_FREE_BLOCK_COUNT_SUBOPCODE = 0x37
    NUM_BLOCK_TYPES = 0                              #0
    FREE_SLC_BLOCK_COUNT = NUM_BLOCK_TYPES + 1       #1
    FREE_MLC_BLOCK_COUNT = FREE_SLC_BLOCK_COUNT + 2  #3

    commandName = "Get IGAT Free Block Count"

    opcode = GET_FREE_BLOCK_COUNT_OPCODE
    subOpcode = GET_FREE_BLOCK_COUNT_SUBOPCODE

    cdb = [ opcode, subOpcode, 0, 0,
            0, 0, 0, 0,
            0, 0, bankNumber, 0,
           0, 0, 0, 0
           ]

    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    configParams = {"numOfBlockTypes":None, "freeSlcBlockCount":None, "freeMlcBlockCount":None}

    configParams["numOfBlockTypes"] = dataBuffer.GetOneByteToInt(NUM_BLOCK_TYPES)
    configParams["freeSlcBlockCount"] = dataBuffer.GetTwoBytesToInt(FREE_SLC_BLOCK_COUNT)
    configParams["freeMlcBlockCount"] = dataBuffer.GetTwoBytesToInt(FREE_MLC_BLOCK_COUNT)

    return configParams

def GetDynamicRelinkedBlockList(vtfContainer, bank=0, blktype=0):
    """
    Name: GetDynamicRelinkedBlockList
    Description: This diagnostic is used to get the list of relinked blocks.
    opcode = 0xC9
    sub Opcode = 0x3B or 59 in Dec
    """

    commandName = "Get the list of relinked blocks"
    opcode = GET_MML_DATA
    subOpcode = 0x3B

    dynamicrelinkbuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR, 0)

    cdb = [opcode,subOpcode,0,0,
           0,0,0,0,
           0,0,bank,blktype,
          0,0,0,0]

    SendDiagnostic(vtfContainer, dynamicrelinkbuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    MBCountOffset = 0x0
    offset = 0x0
    totalNumOfBlks = dynamicrelinkbuf.GetTwoBytesToInt(MBCountOffset)
    offset = offset + 2
    listOfRelinkedMB = []
    for count in range(0, totalNumOfBlks):
        listOfRelinkedMB.append(dynamicrelinkbuf.GetTwoBytesToInt(offset))
        offset = offset + 2

    return {"TotalMetaBlocks":totalNumOfBlks, "MetaBlockList":listOfRelinkedMB}

def GetDynamicRelinkedMBPhysicalAddress(vtfContainer, MetaBlock=0, bank=0, blktype=0):
    """
    Name: GetDynamicRelinkedMBPhysicalAddress
    Description: This diagnostic is used to get the list of physical blocks of the relinked metablock.
    opcode = 0xC9
    sub Opcode = 0x3C or 60 in DEC
    """

    commandName = "Get the list of physical blocks of relinked metablock"
    opcode = GET_MML_DATA
    subOpcode = 0x3C  # 60 Dec
    subOpcodeLsb = ByteUtil.LowByte(MetaBlock)
    subOpcodeMsb = ByteUtil.HighByte(MetaBlock)
    dynamicrelinkbuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR, 0)

    cdb = [opcode,subOpcode,subOpcodeLsb,subOpcodeMsb,
           0,0,0,0,
           0,0,bank,blktype,
          0,0,0,0]

    SendDiagnostic(vtfContainer, dynamicrelinkbuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    Offset = 0x0
    MBNum = dynamicrelinkbuf.GetTwoBytesToInt(Offset)
    Offset = Offset + 0x2
    HotCount = dynamicrelinkbuf.GetTwoBytesToInt(Offset)
    Offset = Offset+0x2
    BlkType = dynamicrelinkbuf.GetOneByteToInt(Offset)
    Offset = Offset + 0x1

    BlockList = []
    BlockList.append((0, 0, 0, dynamicrelinkbuf.GetTwoBytesToInt(Offset)))
    Offset = Offset+0x2
    BlockList.append((0, 0, 1, dynamicrelinkbuf.GetTwoBytesToInt(Offset)))
    Offset = Offset+0x2
    BlockList.append((0, 1, 0, dynamicrelinkbuf.GetTwoBytesToInt(Offset)))
    Offset = Offset+0x2
    BlockList.append((0, 1, 1, dynamicrelinkbuf.GetTwoBytesToInt(Offset)))
    Offset = Offset+0x2
    BlockList.append((0, 2, 0, dynamicrelinkbuf.GetTwoBytesToInt(Offset)))
    Offset = Offset+0x2
    BlockList.append((0, 2, 1, dynamicrelinkbuf.GetTwoBytesToInt(Offset)))
    Offset = Offset+0x2
    BlockList.append((0, 3, 0, dynamicrelinkbuf.GetTwoBytesToInt(Offset)))
    Offset = Offset+0x2
    BlockList.append((0, 3, 1, dynamicrelinkbuf.GetTwoBytesToInt(Offset)))

    return {"MBNum":MBNum, "BlockType":BlkType, "HotCount":HotCount, "BlockList":BlockList}


def GetDLMInfo(vtfContainer, bank=0, blktype=0):
    """
    Name: GetDynamicRelinkedMBPhysicalAddress
    Description: This diagnostic is used to get the list of physical blocks of the relinked metablock.
    opcode = 0xC9
    sub Opcode = 0x3D or 61 Dec
    """

    commandName = "Get the list of physical blocks of relinked metablock"
    opcode = GET_MML_DATA
    subOpcode = 0x3D  #61 Dec

    dynamicrelinkbuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR, 0)

    cdb = [opcode,subOpcode,0,0,
           0,0,0,0,
           0,0,bank,blktype,
          0,0,0,0]

    SendDiagnostic(vtfContainer, dynamicrelinkbuf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    Offset = 0x0
    FirstMBNum = dynamicrelinkbuf.GetTwoBytesToInt(Offset)
    Offset = Offset + 0x2
    NumEntriesInRelinkTable = dynamicrelinkbuf.GetTwoBytesToInt(Offset)
    Offset = Offset + 0x2
    logTableDeltaNumEntries = dynamicrelinkbuf.GetOneByteToInt(Offset)
    Offset = Offset + 0x1
    numPlanesPerMetaBlock = dynamicrelinkbuf.GetTwoBytesToInt(Offset)
    Offset = Offset + 0x2
    numErrorLogPages = dynamicrelinkbuf.GetOneByteToInt(Offset)
    Offset = Offset + 0x1
    numEntriesPerErrorLogPage = dynamicrelinkbuf.GetTwoBytesToInt(Offset)
    Offset = Offset + 0x2
    numRelinkPages = dynamicrelinkbuf.GetOneByteToInt(Offset)
    Offset = Offset + 0x1
    numEntriesPerRelinkPage = dynamicrelinkbuf.GetTwoBytesToInt(Offset)
    Offset = Offset + 0x2
    maxNumLogTableDeltaEntries = dynamicrelinkbuf.GetOneByteToInt(Offset)
    Offset = Offset + 0x1
    syncThresholdLogTableDeltaEntries = dynamicrelinkbuf.GetOneByteToInt(Offset)
    Offset = Offset + 0x1

    return {"FirstMBNum":FirstMBNum, "NumEntriesInRelinkTable":NumEntriesInRelinkTable, "logTableDeltaNumEntries":logTableDeltaNumEntries,  \
            "numPlanesPerMetaBlock":numPlanesPerMetaBlock, "numErrorLogPages":numErrorLogPages, "numEntriesPerErrorLogPage":numEntriesPerErrorLogPage,  \
            "numRelinkPages":numRelinkPages, "numEntriesPerRelinkPage":numEntriesPerRelinkPage, "maxNumLogTableDeltaEntries":maxNumLogTableDeltaEntries,  \
           "syncThresholdLogTableDeltaEntries":syncThresholdLogTableDeltaEntries}


def GetThrottlingMode(vtfContainer):
    """
    Name: GetThrottlingMode
    Description: This diagnostic is used to know whether firmware is in normal/throttling mode
    opcode = 0xC
    SubOpcode = 0x0
    """

    commandName = "Get throttling mode"
    opcode = 0xC9 #0xAC
    subOpcode = 0x49 #0x0

    cdb = [opcode,subOpcode,0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR, 0)
    dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    mode = dataBuffer.GetOneByteToInt(0)
    nandTemperature = dataBuffer.GetOneByteToInt(1)
    tempSenseCmdCount = dataBuffer.GetTwoBytesToInt(2)
    tempDie = dataBuffer.GetOneByteToInt(3)

    return mode, nandTemperature, tempSenseCmdCount, tempDie


def GetMMLSpareBlockCount(vtfContainer):
    """
    Name : GetMMLSpareBlockCount()

    Description : This function calls "Get MML Data diag(0xC9)", to get spare block count info.

    Arguments :
              vtfContainer - vtfContainer Object

    Returns :
             configParams : Spare block count for TLC and SLC blocks

    opcode : 0xC9

    subopcode : 42

    """

    commandName = "Get spare block count"
    opcode = 0xC9
    subOpcode = 42
    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    cdb = [opcode, subOpcode, 0, 0,
           0, 0, 0, 0,
           0, 0, 0, 0,
          0, 0, 0, 0]

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, READ_DATA))
    dataBuffer = SendDiagnostic(vtfContainer,dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    DATA_OFFSET = 0
    nBlkType = dataBuffer.GetOneByteToInt(DATA_OFFSET)
    DATA_OFFSET += 1
    spareBlockCnt = []

    for i in range(nBlkType):
        spareBlockCnt.append(dataBuffer.GetTwoBytesToInt(DATA_OFFSET))
        DATA_OFFSET += 2

    spareMetaBlockCnt = dataBuffer.GetTwoBytesToInt(DATA_OFFSET)
    return nBlkType, spareBlockCnt, spareMetaBlockCnt
#end of GetMMLSpareBlockCount

def setWriteReadUnitDelay(vtfContainer,option1,option2,option3):
    """
    0x01 - Write delay, 0x02 Read delay, and 0x03 Unit delay.
    """
    commandName = "Setting Read/Write/Unit delay"
    opcode = 0xCA
    subOpcode = 53
    cdbData = [opcode,subOpcode,option1,option2,option3,0,0,0,0,0,0,0,0,0,0,0,0]
    rdBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,0)
    SendDiagnostic(vtfContainer, rdBuf, cdbData, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)

def readWriteReadUnitDelay(vtfContainer):
    """
    0x01 - Write delay, 0x02 Read delay, and 0x03 Unit delay.
    """
    commandName = "Setting Read/Write/Unit delay"
    opcode = 0xC9
    subOpcode = 94
    cdbData = [opcode,subOpcode,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    rdBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,0)
    buf=SendDiagnostic(vtfContainer, rdBuf, cdbData, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    return buf

def GetSLCAllocationInfo(vtfContainer):
    """
    Name : GetSLCAllocationInfo()

    Description : This function calls "Get MML Data diag(0xC9)", to get SLC block allocation.

    Arguments :
              vtfContainer - vtfContainer Object

    Returns :
             configParams : SLC block allocated for each metaplane

    opcode : 0xC9

    subopcode : 66

    Structure details:
    typedef PACKED struct _SLC_AllocationItems
    {
       uint8 NumPrimaryGATBlocks;
       uint8 NumSecondaryGATBlocks;
       uint8 NumMIPBlocks;
       uint8 NumUpdateBlocks;
       uint8 NumFreeBlocks;
    } SLC_AllocationItems_t;

    typedef PACKED struct _SLC_AllocationInfo
    {
       uint8 NumberOfMetaplanes;
       uint8 NumberOfItemsPerPlane;
       SLC_AllocationItems_t slcAllocationItems[PROD_MAX_METAPLANE];
    } SLC_AllocationInfo_t;


    """

    commandName = "Get spare block count"
    opcode = 0xC9
    subOpcode = 66
    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    cdb = [opcode, subOpcode, 0, 0,
           0, 0, 0, 0,
           0, 0, 0, 0,
          0, 0, 0, 0]

    vtfContainer.GetLogger().Debug("", "Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, READ_DATA))
    dataBuffer = SendDiagnostic(vtfContainer,dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    numOfMetaplanes = dataBuffer.GetOneByteToInt(0)
    numOfItemsPerMP = dataBuffer.GetOneByteToInt(1)
    slcAllocationInfo = {}

    offset = 2
    for mp in range(numOfItemsPerMP):
        numPrimaryGATBlocks = dataBuffer.GetOneByteToInt(offset)
        numSecondaryGATBlocks = dataBuffer.GetOneByteToInt(offset + 1)
        numMIPBlocks = dataBuffer.GetOneByteToInt(offset + 2)
        numUpdateBlocks = dataBuffer.GetOneByteToInt(offset + 3)
        numFreeBlocks = dataBuffer.GetOneByteToInt(offset + 4)
        offset += 5
        slcAllocationInfo[mp] = [numPrimaryGATBlocks, numSecondaryGATBlocks, numMIPBlocks, numUpdateBlocks, numFreeBlocks]

    return numOfMetaplanes, numOfItemsPerMP, slcAllocationInfo
#end of GetSLCAllocationInfo


def GetSDDeviceHealthStatus(vtfContainer):
    """
    Name: GetSDDeviceHealthStatus
    Description: Diagnostic which gives values related to device health
    Opcode -----0xC9
    Subopcode---0x28
    Returns:  A list of values
    1. User Health Status Percentage
    2. Spare Block Percentage
    3. Health Status Used Percentage
    4. Spare Slc Block Count At T0
    5. Spare Mlc Block Count At T0
    6. Current Spare Slc Block Count
    7. Current Spare Mlc Block Count
    """
    DGN_GET_MML_DATA_CMD_OPCODE = 0xc9
    READ_SD_DEVICE_HEALTH_STATUS = 0x28

    #RPG-10732: No change Old parameter offsets
    READ_CURRENT_SLC_HOT_COUNT = 0x00
    READ_CURRENT_MLC_HOT_COUNT = 0x04
    READ_SLC_SPARE_BLOCK_COUNT_T0 = 0x10
    READ_MLC_SPARE_BLOCK_COUNT_T0 = 0x12
    READ_CURRENT_SLC_SPARE_NUMBER = 0x14
    READ_CURRENT_MLC_SPARE_NUMBER = 0x16
    READ_USER_HEALTH_PERCENTAGE = 0x18
    READ_SPARE_BLOCK_PERCENTAGE = 0x19
    READ_HEALTH_STATUS_USED_PERCENTAGE = 0x1A

    #RPG-10732: New params with offsets
    READ_SLC_USER_HEALTH = 0x1B
    READ_MLC_USER_HEALTH = 0X1C #After this skip 2 bytes as they are same as slcT0 and MlcT0
    READ_BAD_BLKS_COUNT_T0 = 0X1F
    READ_CURRENT_SLC_BAD_BLK_COUNT = 0X20
    READ_CURRENT_MLC_BAD_BLK_COUNT = 0X21
    READ_SLC_SPARE_HEALTH = 0X22
    READ_MLC_SPARE_HEALTH = 0X23
    READ_NUM_OF_TOTAL_UECC = 0X24 #Size of UECC is changed from 1 byte to 2 byte
    READ_NUM_OF_POWER_CYCLE = 0X26
    READ_MEM_TECH_NODE = 0X28
    READ_BITS_PER_CELL = 0X29


    # set CDB
    opcode = DGN_GET_MML_DATA_CMD_OPCODE
    subOpcode = READ_SD_DEVICE_HEALTH_STATUS
    cdb = [ opcode, subOpcode,0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
              0, 0, 0, 0
              ]

    commandName = "Read SD Device Health Status(0xBA)SubOpcode - 39"
    deviceHealthStatus = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR, 0x00)

    deviceHealthStatusBuf = SendDiagnostic(vtfContainer, deviceHealthStatus, cdb, 0, SINGLE_SECTOR, opcode, commandName)

    deviceHealthStatusValues = {
        'userHealthPercentage' : None,
        'spareBlockPercentage' : None,
          'healthStatusUsedPercentage' : None,
         'spareSlcBlockCountAtT0' : None,
         'spareMlcBlockCountAtT0' : None,
         'currentSpareSlcBlockCount' : None,
         'currentSpareMlcBlockCount' : None,
         'currentSlcAvgHotCount' : None,
         'currentMlcAvgHotCount' : None,
         'slcUserHealth' : None,
         'mlcUserHealth' : None,
         'badBlocksCountAtT0' : None,
         'slcCurrentBadBlockCount' : None,
         'mlcCurrentBadBlockCount' : None,
         'slcSpareHealth' : None,
         'mlcSpareHealth' : None,
         'numOfTotalUECC' : None,
         'numOfPowerCycle' : None,
         'memoryTechNode' : None,
         'bitsPerCell' : None
    }

    userHealthPercentage = deviceHealthStatus.GetOneByteToInt(READ_USER_HEALTH_PERCENTAGE)
    deviceHealthStatusValues['userHealthPercentage'] = userHealthPercentage
    spareBlockPercentage = deviceHealthStatus.GetOneByteToInt(READ_SPARE_BLOCK_PERCENTAGE)
    deviceHealthStatusValues['spareBlockPercentage'] = spareBlockPercentage
    healthStatusUsedPercentage = deviceHealthStatus.GetOneByteToInt(READ_HEALTH_STATUS_USED_PERCENTAGE)
    deviceHealthStatusValues['healthStatusUsedPercentage'] = healthStatusUsedPercentage
    spareSlcBlockCountAtT0 = deviceHealthStatus.GetTwoBytesToInt(READ_SLC_SPARE_BLOCK_COUNT_T0)
    deviceHealthStatusValues['spareSlcBlockCountAtT0'] = spareSlcBlockCountAtT0
    spareMlcBlockCountAtT0 = deviceHealthStatus.GetTwoBytesToInt(READ_MLC_SPARE_BLOCK_COUNT_T0)
    deviceHealthStatusValues['spareMlcBlockCountAtT0'] = spareMlcBlockCountAtT0
    currentSpareSlcBlockCount = deviceHealthStatus.GetTwoBytesToInt(READ_CURRENT_SLC_SPARE_NUMBER)
    deviceHealthStatusValues['currentSpareSlcBlockCount'] = currentSpareSlcBlockCount
    currentSpareMlcBlockCount = deviceHealthStatus.GetTwoBytesToInt(READ_CURRENT_MLC_SPARE_NUMBER)
    deviceHealthStatusValues['currentSpareMlcBlockCount'] = currentSpareMlcBlockCount
    currentSlcAvgHotCount = deviceHealthStatus.GetFourBytesToInt(READ_CURRENT_SLC_HOT_COUNT)
    deviceHealthStatusValues['currentSlcAvgHotCount'] = currentSlcAvgHotCount
    currentMlcAvgHotCount = deviceHealthStatus.GetFourBytesToInt(READ_CURRENT_MLC_HOT_COUNT)
    deviceHealthStatusValues['currentMlcAvgHotCount'] = currentMlcAvgHotCount

    #RPG-10732: New params with offsets
    deviceHealthStatusValues['slcUserHealth'] = deviceHealthStatus.GetOneByteToInt(READ_SLC_USER_HEALTH)
    deviceHealthStatusValues['mlcUserHealth'] = deviceHealthStatus.GetOneByteToInt(READ_MLC_USER_HEALTH)
    deviceHealthStatusValues['badBlocksCountAtT0'] = deviceHealthStatus.GetOneByteToInt(READ_BAD_BLKS_COUNT_T0)
    deviceHealthStatusValues['slcCurrentBadBlockCount'] = deviceHealthStatus.GetOneByteToInt(READ_CURRENT_SLC_BAD_BLK_COUNT)
    deviceHealthStatusValues['mlcCurrentBadBlockCount'] = deviceHealthStatus.GetOneByteToInt(READ_CURRENT_MLC_BAD_BLK_COUNT)
    deviceHealthStatusValues['slcSpareHealth'] = deviceHealthStatus.GetOneByteToInt(READ_SLC_SPARE_HEALTH)
    deviceHealthStatusValues['mlcSpareHealth'] = deviceHealthStatus.GetOneByteToInt(READ_MLC_SPARE_HEALTH)
    #deviceHealthStatusValues['numOfTotalUECC'] = deviceHealthStatus.GetOneByteToInt(READ_NUM_OF_TOTAL_UECC)
    deviceHealthStatusValues['numOfTotalUECC'] = deviceHealthStatus.GetTwoBytesToInt(READ_NUM_OF_TOTAL_UECC)  #Size changed to 2 byte
    deviceHealthStatusValues['numOfPowerCycle'] = deviceHealthStatus.GetTwoBytesToInt(READ_NUM_OF_POWER_CYCLE)
    deviceHealthStatusValues['memoryTechNode'] = deviceHealthStatus.GetOneByteToInt(READ_MEM_TECH_NODE)
    deviceHealthStatusValues['bitsPerCell'] = deviceHealthStatus.GetOneByteToInt(READ_BITS_PER_CELL)

    return deviceHealthStatusValues

def SetROFSCounters(vtfContainer, ROFSReadSenseThreshold, ROFSMIPDumpFrequency, ROFSInitMIPDumpAdjustment):
    """
    Name: SetROFSCounters
    Description: This diagnostic is used to set the RO FS counters
    opcode = 0xCA
    SubOpcode = 0x1E
    """

    commandName = "Set RO FS Counters"
    opcode = 0xCA
    subOpcode = 0x1E

    cdb = [opcode,subOpcode,
           ByteUtil.HighByte(ByteUtil.HighWord(ROFSReadSenseThreshold)),ByteUtil.LowByte(ByteUtil.HighWord(ROFSReadSenseThreshold)),
           ByteUtil.HighByte(ByteUtil.LowWord(ROFSReadSenseThreshold)),ByteUtil.LowByte(ByteUtil.LowWord(ROFSReadSenseThreshold)),
          ByteUtil.HighByte(ByteUtil.HighWord(ROFSMIPDumpFrequency)),ByteUtil.LowByte(ByteUtil.HighWord(ROFSMIPDumpFrequency)),
          ByteUtil.HighByte(ByteUtil.LowWord(ROFSMIPDumpFrequency)),ByteUtil.LowByte(ByteUtil.LowWord(ROFSMIPDumpFrequency)),
          ByteUtil.HighByte(ROFSInitMIPDumpAdjustment),ByteUtil.LowByte(ROFSInitMIPDumpAdjustment),
          0,0,0,0]

    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR, 0)
    dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)

    return

def GetROFSCounters(vtfContainer):
    """
    Description:
       * Gets the RO FS counters
    """
    # Offsets
    opcode = 0xC9
    subOpcode = 0x43
    RO_FS_READ_SENSE_THRESHOLD = 0x0
    RO_FS_MIP_DUMP_FREQUENCY = 0x4
    RO_FS_INIT_MIP_DUMP_ADJUSTMENT = 0x8
    RO_FS_READCOUNT_IN_MIP = 0xA
    RO_FS_READCOUNT_IN_RAM = 0xE

    commandName = "Get RO FS counters"

    cdb = [ opcode, subOpcode, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
           0, 0, 0, 0
           ]

    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    #configParams = {"ROFSReadSenseThreshold":None, "ROFSMIPDumpFrequency":None, "ROFSInitMIPDumpAdjustment":None}

    ROFSReadSenseThreshold = dataBuffer.GetFourBytesToInt(RO_FS_READ_SENSE_THRESHOLD)
    ROFSMIPDumpFrequency = dataBuffer.GetFourBytesToInt(RO_FS_MIP_DUMP_FREQUENCY)
    ROFSInitMIPDumpAdjustment = dataBuffer.GetTwoBytesToInt(RO_FS_INIT_MIP_DUMP_ADJUSTMENT)
    ROFSReadCountInMip = dataBuffer.GetFourBytesToInt(RO_FS_READCOUNT_IN_MIP)
    ROFSReadCountInRAM = dataBuffer.GetFourBytesToInt(RO_FS_READCOUNT_IN_RAM)
    ROFSValues = [ROFSReadSenseThreshold, ROFSMIPDumpFrequency, ROFSInitMIPDumpAdjustment, ROFSReadCountInMip, ROFSReadCountInRAM]
    return ROFSValues


def GetFSblocksHCValues(vtfContainer):
    """
    Description:
       * Gets the FS blks ( RO and RW Primary and Sec) HC values
       * This diag will give boot blocks HC as well
    """
    # Offsets
    opcode = 0x61
    subOpcode = 0x3
    option = 1

    #Boot blks nums and HCs offsets
    NUM_CTRL_BLKS = 0x0
    PRIMARY_BOOT_BLK_NUM = 0x2
    PRIMARY_BOOT_BLK_NUM_HC = 0x4
    SECONDARY_BOOT_BLK_NUM = 0x8
    SECONDARY_BOOT_BLK_NUM_HC = 0xA

    #RO FS primary0  blk and HC offsets
    ROFS_PRIMARY0_BLK_NUM = 0xE
    ROFS_PRIMARY0_BLK_NUM_HC = 0x10

    #RO FS primary1 blk and HC offsets  If product is having two primary blks
    ROFS_PRIMARY1_BLK_NUM = 0x14
    ROFS_PRIMARY1_BLK_NUM_HC = 0x16

    #RO FS Secondary0  blk and HC offsets
    ROFS_SECONDARY0_BLK_NUM = 0x1A
    ROFS_SECONDARY0_BLK_NUM_HC = 0X1C

    #RO FS Secondary1 blk and HC offsets  If product is having two primary blks
    ROFS_SECONDARY1_BLK_NUM = 0x20
    ROFS_SECONDARY1_BLK_NUM_HC = 0x22

    #RO FS primary0  blk and HC offsets
    RWFS_PRIMARY0_BLK_NUM = 0x26
    RWFS_PRIMARY0_BLK_NUM_HC = 0x28

    #RO FS primary1 blk and HC offsets  If product is having two primary blks
    RWFS_PRIMARY1_BLK_NUM = 0x2C
    RWFS_PRIMARY1_BLK_NUM_HC =  0x2E

    #RO FS Secondary0  blk and HC offsets
    RWFS_SECONDARY0_BLK_NUM = 0x32
    RWFS_SECONDARY0_BLK_NUM_HC = 0x34

    #RO FS Secondary1 blk and HC offsets  If product is having two primary blks
    RWFS_SECONDARY1_BLK_NUM = 0x38
    RWFS_SECONDARY1_BLK_NUM_HC = 0x3A

    commandName = "Ctrl blocks HC"


    cdb = [ opcode, subOpcode, option, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
           0, 0, 0, 0
           ]

    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    numofcontrolblksdata = dataBuffer.GetTwoBytesToInt(NUM_CTRL_BLKS)
    #Boot blks details
    primarybootblknum = dataBuffer.GetTwoBytesToInt(PRIMARY_BOOT_BLK_NUM)
    primarybootblknum_HC = dataBuffer.GetFourBytesToInt(PRIMARY_BOOT_BLK_NUM_HC)

    secondarybootblknum = dataBuffer.GetTwoBytesToInt(SECONDARY_BOOT_BLK_NUM)
    secondarybootblknum_HC = dataBuffer.GetFourBytesToInt(SECONDARY_BOOT_BLK_NUM_HC)

    #RO FS blks primary 0 and 1 details
    ROFS_primary0_blknum = dataBuffer.GetTwoBytesToInt(ROFS_PRIMARY0_BLK_NUM)
    ROFS_primary0_blknum_HC = dataBuffer.GetFourBytesToInt(ROFS_PRIMARY0_BLK_NUM_HC)

    ROFS_primary1_blknum = dataBuffer.GetTwoBytesToInt(ROFS_PRIMARY1_BLK_NUM)
    ROFS_primary1_blknum_HC = dataBuffer.GetFourBytesToInt(ROFS_PRIMARY1_BLK_NUM_HC)

    #RO FS blks secondary 0 and 1 details
    ROFS_secondary0_blknum = dataBuffer.GetTwoBytesToInt(ROFS_SECONDARY0_BLK_NUM)
    ROFS_secondary0_blknum_HC = dataBuffer.GetFourBytesToInt(ROFS_SECONDARY0_BLK_NUM_HC)

    ROFS_secondary1_blknum = dataBuffer.GetTwoBytesToInt(ROFS_SECONDARY1_BLK_NUM)
    ROFS_secondary1_blknum_HC = dataBuffer.GetFourBytesToInt(ROFS_SECONDARY1_BLK_NUM_HC)

    #RW FS blks primary 0 and 1 details
    RWFS_primary0_blknum = dataBuffer.GetTwoBytesToInt(RWFS_PRIMARY0_BLK_NUM)
    RWFS_primary0_blknum_HC = dataBuffer.GetFourBytesToInt(RWFS_PRIMARY0_BLK_NUM_HC)

    RWFS_primary1_blknum = dataBuffer.GetTwoBytesToInt(RWFS_PRIMARY1_BLK_NUM)
    RWFS_primary1_blknum_HC = dataBuffer.GetFourBytesToInt(RWFS_PRIMARY1_BLK_NUM_HC)

    #RW FS blks secondary 0 and 1 details
    RWFS_secondary0_blknum = dataBuffer.GetTwoBytesToInt(RWFS_SECONDARY0_BLK_NUM)
    RWFS_secondary0_blknum_HC = dataBuffer.GetFourBytesToInt(RWFS_SECONDARY0_BLK_NUM_HC)

    RWFS_secondary1_blknum = dataBuffer.GetTwoBytesToInt(RWFS_SECONDARY1_BLK_NUM)
    RWFS_secondary1_blknum_HC = dataBuffer.GetFourBytesToInt(RWFS_SECONDARY1_BLK_NUM_HC)

    blks_details = [numofcontrolblksdata, primarybootblknum, primarybootblknum_HC,  secondarybootblknum, secondarybootblknum_HC,
                    ROFS_primary0_blknum, ROFS_primary0_blknum_HC, ROFS_primary1_blknum, ROFS_primary1_blknum_HC,
                    ROFS_secondary0_blknum, ROFS_secondary0_blknum_HC, ROFS_secondary1_blknum, ROFS_secondary1_blknum_HC,
                   RWFS_primary0_blknum, RWFS_primary0_blknum_HC, RWFS_primary1_blknum, RWFS_primary1_blknum_HC,
                   RWFS_secondary0_blknum, RWFS_secondary0_blknum_HC, RWFS_secondary1_blknum, RWFS_secondary1_blknum_HC]
    return blks_details



def GetHybridBlockListAndCount(vtfContainer, MMP):
    """
    Hybrid block count and list of hybrid blocks allocated
    Diagnostic Name: DiagMML_GetHybridBlockListAndCount
    Opcode: DIAG_CMD_OPCODE_GET_MML_DATA               0xC9
    Sub Opcode:
    DiagMML_GetHybridBlockListAndCount         68
    Input : self.__fwConfigObj.MMP

    This diag will return

       //Total number of hybrid blocks which are in use.
       //Includes blocks in open UB, pair list, EPWR hide secondary, block under GC, closed block etc.
       //Effectively, the number of hybrid blocks, which are not yet added to free list.
       //Maximum supported is 'MAX_HYBRID_BLOCKS_PER_METAPLANE'
       //'numOpenMlcBlocks' must and total count in 'mb' must be equal.
       uint8 numOpenMlcBlocks;

    //Array of maximum number of hybrid blocks in current meta plane.
       //Maximum supported number is hard coded in FW.
       uint16 mb[MAX_HYBRID_BLOCKS_PER_METAPLANE];

    (MAX_HYBRID_BLOCKS_PER_METAPLANE – 10)

    """
    # Offsets
    opcode = 0xC9
    subOpcode = 0x44
    cdb = [ opcode, subOpcode, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
           0, 0, 0, 0
           ]

    commandName = "HybridBlkListAndCount"
    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    openHybridBlkDetails = {}
    offset = 0
    for mmp in range(MMP):
        MAX_HYBRID_BLOCKS_PER_METAPLANE  = 10
        hybridblksInUse = []
        metaplane_num  = dataBuffer.GetOneByteToInt(offset)
        offset +=1
        numofopenmlcblks = dataBuffer.GetOneByteToInt(offset)
        offset += 1
        current_offset = offset
        while (dataBuffer.GetTwoBytesToInt(offset)) !=0x1FFF and numofopenmlcblks>0 and MAX_HYBRID_BLOCKS_PER_METAPLANE>0:
            hybridblksInUse.append(dataBuffer.GetTwoBytesToInt(offset))
            offset +=2
            MAX_HYBRID_BLOCKS_PER_METAPLANE -= 1

        offset = current_offset + 2*10  # 10 blks  per metaplane
        openHybridBlkDetails[metaplane_num] = [numofopenmlcblks, hybridblksInUse]

    return openHybridBlkDetails


def GetHybridBlockAllCounters(vtfContainer, MMP):
    """
    1. SLC and TLC counter values (config values)
    2. Number of times Max Hybrid block threshold has been hit
    3. Number of times Force Close Stream Hybrid Block hit
    input: self.__fwConfigObj.MMP  config FW config
    """
    # Offsets
    opcode = 0xC9
    subOpcode = 0x45
    cdb = [ opcode, subOpcode, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
           0, 0, 0, 0
           ]
    commandName = "HybridBlkAllCounters"
    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)

    dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    SLC_BLK_RATIO_COUNT = 0x0
    MLC_BLK_RATIO_COUNT = 0x1
    MAX_MLC_HYBRID_THRESHOLD = 0x2
    SLC_THRESHOLD_FOR_STREAM_CLOSE = 0x3

    slc_block_ratio_count = dataBuffer.GetOneByteToInt(SLC_BLK_RATIO_COUNT)
    mlc_block_ratio_count = dataBuffer.GetOneByteToInt(MLC_BLK_RATIO_COUNT)
    max_mlc_hybrid_threshold = dataBuffer.GetOneByteToInt(MAX_MLC_HYBRID_THRESHOLD)
    slc_threshold_for_stream_close = dataBuffer.GetOneByteToInt(SLC_THRESHOLD_FOR_STREAM_CLOSE)

    HybridBlockAllCounters = {}
    offset = 4
    for mmp in range(MMP+1):
        metaplane_num  = dataBuffer.GetOneByteToInt(offset)
        offset += 1

        num_open_mlc_blks              = dataBuffer.GetOneByteToInt(offset)
        offset += 1
        num_allocated_mlc_blks         = dataBuffer.GetOneByteToInt(offset)
        offset += 1
        num_allocated_slc_blks         = dataBuffer.GetOneByteToInt(offset)
        offset += 1
        slc_blk_counter                = dataBuffer.GetOneByteToInt(offset)
        offset += 1

        num_allocated_mlc_blks_counter = dataBuffer.GetFourBytesToInt(offset)
        offset += 4
        num_allocated_slc_blks_counter  = dataBuffer.GetFourBytesToInt(offset)
        offset += 4
        num_allocated_slc_blks_other_cases_counter = dataBuffer.GetFourBytesToInt(offset)
        offset += 4
        force_closing_stream_counter   = dataBuffer.GetTwoBytesToInt(offset)
        offset += 2
        max_mlc_hybrid_threshold_counter =dataBuffer.GetTwoBytesToInt(offset)
        offset += 2
        slc_seq_mode  =dataBuffer.GetOneByteToInt(offset)
        offset += 1
        HybridBlockAllCounters[metaplane_num] = [slc_block_ratio_count, mlc_block_ratio_count, max_mlc_hybrid_threshold, slc_threshold_for_stream_close,
                                                 num_open_mlc_blks, num_allocated_mlc_blks, num_allocated_slc_blks, slc_blk_counter,
                                                 num_allocated_mlc_blks_counter, num_allocated_slc_blks_counter, num_allocated_slc_blks_other_cases_counter,
                                               force_closing_stream_counter, max_mlc_hybrid_threshold_counter, slc_seq_mode]


    return HybridBlockAllCounters   #Eg: {0: [4, 4, 5, 5, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0]} for single Multi Metaplane


def SetHybridBlockRatioCounterAndThresholdValues(vtfContainer, SLCBlkRatioCount=0, MLCBlkRatioCount=0, MaxMLCHybridThreshold=0, SLCThresholdForStreamClose=0):
    """
    For updating Hybrid block count threshold
    Diagnostic Name: Diag_MML_SetHybridBlockRatioCounterAndThresholdValues
    Opcode:  DIAG_CMD_OPCODE_GET_MML_DATA                  0xCA
    Sub Opcode:
    DiagMML_SetHybridBlockRatioCounterAndThresholdValues  32

    This diag will set Hybrid Block Ratio Counter and Threshold Values.

    uint8    SLCBlockRatioCount;        // SLC Block ratio count
    uint8    MLCBlockRatioCount;        // MLC Block ratio count
    uint8    MaxMLCHybridThreshold;     // Max MLC in Hybrid Block
    uint8    SLCThresholdForStreamClose;// SLC Threshold for Stream Close to release Hybrid blocks
    """
    # Offsets
    opcode = 0xCA
    subOpcode = 0x20

    cdb = [ opcode, subOpcode,0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
           0, 0, 0, 0
           ]

    commandName = "SetHybridBlockRatioCounterAndThresholdValues"
    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    dataBuffer[0] = SLCBlkRatioCount
    dataBuffer[1] = MLCBlkRatioCount
    dataBuffer[2] = MaxMLCHybridThreshold
    dataBuffer[3] = SLCThresholdForStreamClose


    dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)
    return


def PSRStart(vtfContainer):
    """
    Start PSR Screen Diag
    """
    logger = vtfContainer.GetLogger()
    opcode = 0xC9
    subOpcode = 79
    Buf = pyWrap.Buffer.CreateBuffer(1,0)
    cdb = [opcode,subOpcode,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    logger.Info("", "Diagnostic command (PSR Start Opcode 0x%x, Sub opcode 0x%x)" %(opcode,subOpcode))
    SendDiagnostic(vtfContainer,Buf, cdb, 0,1)
    status = Buf.GetTwoBytesToInt(0)
    return status


def PSRStatus(vtfContainer):
    """
    Retunrs:
       - status -> non zero if PSR screening failed else zero
       - LastLBA -> Last LBA written
    """
    import time
    import datetime
    logger = vtfContainer.GetLogger()
    opcode = 0xC9
    subOpcode = 80
    Buf = pyWrap.Buffer.CreateBuffer(1,0)
    cdb = [opcode,subOpcode,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    logger.Info("", "Diagnostic command (PSR Status Opcode 0x%x, Sub opcode 0x%x)" %(opcode,subOpcode))
    SendDiagnostic(vtfContainer,Buf, cdb, 0,1)
    Status  = Buf.GetFourBytesToInt(0)
    LastLBAWritten = Buf.GetFourBytesToInt(4)
    logger.Info("", "Status:  (%s) "%Buf.GetFourBytesToInt(0))
    logger.Info("", "LastLBAWritten: (%s) "%Buf.GetFourBytesToInt(4))
    return Status, LastLBAWritten

def PSRDisable(vtfContainer):
    """
    PSR Disable Diag
    """
    logger = vtfContainer.GetLogger()
    opcode = 0xC9
    subOpcode = 81
    Buf = pyWrap.Buffer.CreateBuffer(1,0)
    cdb = [opcode,subOpcode,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    logger.Info("", "Diagnostic command (PSR Disable Opcode 0x%x, Sub opcode 0x%x)" %(opcode,subOpcode))
    SendDiagnostic(vtfContainer, Buf, cdb, 0,1)
    status = Buf.GetTwoBytesToInt(0)
    return status


def PSREnabledOrDisabledStatus(vtfContainer):
    """
    Return : 0/1 -> 1- PSR ENABLED else NOT
    """
    opcode = 0xC9
    subOpcode = 78
    cdb = [ opcode, subOpcode, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
           0, 0, 0, 0
           ]
    commandName = "PSREnabledOrDisabledStatus"
    PSR_ENABLE_DISALE_STATUS = 0
    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    PSRStatus  = dataBuffer.GetOneByteToInt(PSR_ENABLE_DISALE_STATUS)  # First Byte will info about enabled/disabled
    return PSRStatus

def GetFWFeatureEnableDisableInfo(vtfContainer):
    """
    Name        :  GetFWFeatureEnableDisableInfo
    Description :  Get and validate FW feature enabled/disabled from MML module.
    Arguments   :  vtfContainer : Card Test Space
    Returns     :  List of FW features enable/disable info.
    isTTFeatureEnaDis         :0-Disable, 1-Enable.
    isECCFeatureEnaDis        :0-Disable, 1-Enable.
    isEDGEWLSkipFeatureEnaDis :0-Disable, 1-Enable.
    isSkipSLCPFFeatureEnaDis  :0-Disable, 1-Enable.
    isSkipMLCPFFeatureEnaDis  :0-Disable, 1-Enable.
    """
    #FW feature index or offset for feature mapping at buffer
    THERMAL_TROTTLING_SUPPORT_OFFSET     = 0                                     # 0
    EARLY_COMMAND_COMPLETION_OFFSET      = THERMAL_TROTTLING_SUPPORT_OFFSET + 1  # 1
    EDGE_WL_SKIP_OFFSET                  = EARLY_COMMAND_COMPLETION_OFFSET  + 1  # 2
    SKIP_SLC_PF_OFFSET                   = EDGE_WL_SKIP_OFFSET              + 1  # 3
    SKIP_MLC_PF_OFFSET                   = SKIP_SLC_PF_OFFSET               + 1  # 4
    FWFeaturesEnable                     = {}
    commandName = "FW Feature Status"
    opcode = 0xC9  #DIAG_CMD_OPCODE_GET_MML_DATA
    subopcode = 0x49 #0x76, 0x73 DiagMML_GetFWFeatureEnableStatus

    #Create a cdb command.
    cdb = [ opcode, subopcode, 0, 0,0, 0, 0, 0,0, 0, 0, 0,0, 0, 0, 0]

    #Create a buffer to collect the MML data to get FW feature enable/disable info.
    mmlDataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    mmlDataBuffer = SendDiagnostic(vtfContainer, mmlDataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    #Get THERMAL_TROTTLING_SUPPORT feature disable information.
    ThermalThrottleEnabled = mmlDataBuffer.GetOneByteToInt(THERMAL_TROTTLING_SUPPORT_OFFSET)

    #Get EARLY_COMMAND_COMPLETION feature enable/disable information.
    EarlyCmdCompEnable = mmlDataBuffer.GetOneByteToInt(EARLY_COMMAND_COMPLETION_OFFSET)

    #Get EDGE_WL_SKIP feature enable/disable information.
    EdgeWlSkipEnable = mmlDataBuffer.GetOneByteToInt(EDGE_WL_SKIP_OFFSET)

    #Get SKIP_SLC_PF feature enable/disable information.
    SlcPfSkipEnable = mmlDataBuffer.GetOneByteToInt(SKIP_SLC_PF_OFFSET)

    #Get SKIP_MLC_PF feature enable/disable information.
    MlcPfSkipEnable = mmlDataBuffer.GetOneByteToInt(SKIP_MLC_PF_OFFSET)

    FWFeaturesEnable = {"ThermalThrottleEnable":ThermalThrottleEnabled, "EarlyCmdCompEnable":EarlyCmdCompEnable, "EdgeWlSkipEnable":EdgeWlSkipEnable, "SlcPfSkipEnable":SlcPfSkipEnable, "MlcPfSkipEnable":MlcPfSkipEnable}

    return FWFeaturesEnable


def SetPGCBusyPeriod(vtfContainer, timeInms):
    commandName = "Set custom PGC quota"
    opcode = 0xCA
    subOpcode = 0x2D #0x2E
    optionLow = timeInms & MASK_LOW_BYTE
    optionHigh = (timeInms >> 8) & MASK_LOW_BYTE
    cdb=[opcode,subOpcode,optionLow,optionHigh,
         0,0,0,0,
         0,0,0,0,
        0,0,0,0]

    rdBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,0)
    rdBuf =SendDiagnostic(vtfContainer, rdBuf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)


def SetDisablePreventTimeoutCheck(vtfContainer, disable = 1):
    commandName = "Set custom PGC quota"
    opcode = 0xCA
    subOpcode = 0x2E #0x2F
    option1=disable
    cdbData = [opcode,subOpcode,option1,0,0,0,0,0,0,0,0,0,0,0,0,0]
    rdBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,0)
    rdBuf =SendDiagnostic(vtfContainer, rdBuf, cdbData, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)


#End of GetListOfFWFeatureEnableDisable



def getMBAndWriteOffsetInfo(vtfContainer):
    """
    Name        :  getMBAndWriteOffsetInfo
    Description :  MB and MB Offset info
    Arguments   :  vtfContainer : Card Test Space
    Returns     :
    """
    #FW feature index or offset for feature mapping at buffer
    WriteMB                              = 0                                     # 0
    WriteMbOffset                        = WriteMB + 2                           # 2
    WriteAbortCount                      = WriteMbOffset + 4                     # 4
    ErcMB                                = WriteAbortCount + 2                   # 3
    ErcMbSector                          = ErcMB + 4                             # 4
    MBOffsetInfo                         = {}

    commandName = "WriteOffsetWAERCInfo"
    opcode = 0xC9
    subopcode = 74

    #Create a cdb command.
    cdb = [ opcode, subopcode, 0, 0,0, 0, 0, 0,0, 0, 0, 0,0, 0, 0, 0]

    #Create a buffer to collect the MML data to get FW feature enable/disable info.
    mmlDataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    mmlDataBuffer = SendDiagnostic(vtfContainer, mmlDataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    WriteMbA        = mmlDataBuffer.GetTwoBytesToInt(WriteMB)
    WriteOffsetinMB = mmlDataBuffer.GetFourBytesToInt(WriteMbOffset)
    WACount         = mmlDataBuffer.GetTwoBytesToInt(WriteAbortCount)
    ErcMBA          = mmlDataBuffer.GetFourBytesToInt(ErcMB)
    ErcSectorinMB   = mmlDataBuffer.GetFourBytesToInt(ErcMbSector)

    MBOffsetInfo = {"WriteMBNum":WriteMbA, "WriteOffsetInMB":WriteOffsetinMB, "WACounter":WACount, "ERCMBNum":ErcMBA, "ErcSectorinMB":ErcSectorinMB}

    return MBOffsetInfo

def ReadFileSystem(vtfContainer,fileID = 0, sectorCount = None, readBuff=None, option = None):
    logger = vtfContainer.GetLogger()
    if option == None:
        option = 0x00
    elif option == "PRI":
        option = 0x2
    elif option == "SEC":
        option = 0x6

    sectorCount, sectorCount_inBytes = LengthOfFileInBytes(fileId=fileID)
    if sectorCount<1:
        logger.Info("", "Sector count for FILE %d is invalid: 0x%X"%(fileID, sectorCount))
        raise TestError.TestFailError("", "Length of FILE is 0, check log")
    diagCommand = pyWrap.DIAG_FBCC_CDB()

    cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    cdb[0] = 0x8A
    cdb[1] = 0
    cdb[2] = (option & 0xFF);
    cdb[3] = (option >> 8) & 0xFF;
    cdb[4] = (fileID & 0xFF);
    cdb[5] = (fileID >> 8) & 0xFF;
    cdb[6] = (fileID >> 16) & 0xFF;
    cdb[7] = (fileID >> 24) & 0xFF;
    cdb[8] = sectorCount & 0x000000FF
    cdb[9] = (sectorCount >> 8 )& 0x000000FF
    cdb[10] = (sectorCount >> 16) & 0x000000FF
    cdb[11] = (sectorCount >> 24) & 0x000000FF
    cdb[12] = cdb[13] = cdb[14] = cdb[15] = 0

    cdb = FormSignedSCTP(cdb)
    diagCommand.cdb = cdb
    diagCommand.cdbLen = len(cdb)

    if readBuff == None:
        readBuff = pyWrap.Buffer.CreateBuffer(sectorCount, 0x0, True)

    try:
        sctpCommand = pyWrap.SCTPCommand.SCTPCommand(diagCommand, readBuff, pyWrap.DIRECTION_OUT, True, None, 200000)
        sctpCommand.Execute()
        return readBuff
    except TestError.CVFExceptionTypes as exc:
        exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
        raise TestError.TestFailError("", "Read File System Diagnostic Failed",exc.GetFailureDescription())

def LengthOfFileInBytes(fileId):
    sectorCount = Constants.FS_CONSTANTS.SECTOR_SIZE_TO_GET_LENGTH_OF_FILE
    buff = pyWrap.Buffer.CreateBuffer(sectorCount, 0x00,True)

    diagCommand = pyWrap.DIAG_FBCC_CDB()
    cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    cdb[0] = 0x8A
    cdb[1] = 0
    cdb[2] = 0x01
    cdb[3] = 0
    cdb[4] = (fileId & 0xFF)
    cdb[5] = (fileId >> 8) & 0xFF
    cdb[6] = (fileId >> 16) & 0xFF
    cdb[7] = (fileId >> 24) & 0xFF
    cdb[8] = sectorCount & 0x000000FF
    cdb[9] = (sectorCount >> 8 )& 0x000000FF
    cdb[10] = (sectorCount >> 16) & 0x000000FF
    cdb[11] = (sectorCount >> 24) & 0x000000FF
    cdb[12] = cdb[13] = cdb[14] = cdb[15] = 0

    cdb =FormSignedSCTP(cdb)
    diagCommand.cdb = cdb
    diagCommand.cdbLen = len(cdb)
    try:
        sctpCommand = pyWrap.SCTPCommand.SCTPCommand(diagCommand, buff, pyWrap.DIRECTION_OUT)
        sctpCommand.Execute()

        fileSizeInSectors = buff.GetFourBytesToInt(0)
        fileSizeInBytes = fileSizeInSectors * 512


        #fileSizeInSectors = (fileSizeInBytes/512)
        #if fileSizeInBytes%512 != 0:
                #fileSizeInSectors = fileSizeInSectors + 1

        return fileSizeInSectors, fileSizeInBytes
    except TestError.CVFExceptionTypes as exc:
        exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
        raise TestError.TestFailError("", "Length of File Diagnostic Failed",exc.GetFailureDescription())


def WriteFileSystem(vtfContainer, fileID = 0, sectorCount = 1, dataBuffer = None):
    diagCommand = pyWrap.DIAG_FBCC_CDB()
    logger = vtfContainer.GetLogger()
    cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    cdb[0] = 0x8B
    cdb[1] = 0
    cdb[2] = 0
    cdb[3] = 0
    cdb[4] = (fileID & 0xFF);
    cdb[5] = (fileID >> 8) & 0xFF;
    cdb[6] = (fileID >> 16) & 0xFF;
    cdb[7] = (fileID >> 24) & 0xFF;
    cdb[8] = sectorCount & 0x000000FF
    cdb[9] = (sectorCount >> 8 )& 0x000000FF
    cdb[10] = (sectorCount >> 16) & 0x000000FF
    cdb[11] = (sectorCount >> 24) & 0x000000FF
    cdb[12] = cdb[13] = cdb[14] = cdb[15] = 0
    
    cdb = FormSignedSCTP(cdb)
    diagCommand.cdb = cdb
    diagCommand.cdbLen = len(cdb)

    logger.Info("", "Sending WRITE FILE SYSTEM CDB: %s"%diagCommand.cdb)
    logger.Info("", "File ID: %d Sector Count: %d"%(fileID, sectorCount))
    logger.Info("", "Write Buffer Size: %d Bytes"%dataBuffer.GetBufferSize())
    try:
        sctpCommand = pyWrap.SCTPCommand.SCTPCommand(diagCommand, dataBuffer, pyWrap.DIRECTION_IN, True, None, 200000)
        sctpCommand.Execute()
        logger.Info("", "Write File Diagnostic completed successfully")

    #except Exception, exc:
    except TestError.CVFExceptionTypes as exc:
        exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
        #pass
        logger.Info("",  "Write File Diagnostic Failed")
        logger.Info("",  "Error:\n%s" %exc)
        #raise ValidationError.TestFailError("Write File System Diagnostic", GlobalVars.FVTExcPrint())
        raise TestError.TestFailError(vtfContainer.GetTestName(), "Write File System Diagnostic",exc.GetFailureDescription())

def ReadSFR(vtfContainer, address, byteCount, options=0):
    """
    Description: Memory allocation ( This function use to create Singleton object of OrthogonalTestManager)
    Parameters: None
    Returns: None
    Exceptions: None
    """
    opcode = 0xC1
    buf = pyWrap.Buffer.CreateBuffer(1)
    cdb = [0] * 16
    cdb[0] = opcode
    cdb[2] = options & 0xFF
    cdb[3] = options >> 8 & 0xFF
    cdb[4] = int(address & 0xFF)
    cdb[5] = int(address >> 8 & 0xFF)
    cdb[6] = int(address >> 16 & 0xFF)
    cdb[7] = int(address >> 24 & 0xFF)
    cdb[8] = byteCount & 0xFF
    cdb[9] = byteCount >> 8 & 0xFF
    cdb[10] = byteCount >> 16 & 0xFF
    cdb[11] = byteCount >> 24 & 0xFF
    logger = vtfContainer.GetLogger()
    logger.Info("", "Issuing READ_SFR (0xC1) diag for Register 0x%X, bytecount 0x%X"%(address, byteCount))
    #cdb = [0xC1, 0, 0, 0, 0x9C, 0x00, 0x01, 0xF0, 0x4, 0x0, 0, 0, 0, 0, 0, 0]
    buf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, 1, 0xC1, "READ_SFR")

    return buf

def WriteSEDRegister(vtfContainer, address, Value, options=1):
    """
    Description: Use to write SFR registers (Implemented for SED)
    Parameters: None
    Returns: None
    Exceptions: None
    """
    opcode = 0xBB
    subopcode = 0x1
    buf = pyWrap.Buffer.CreateBuffer(1)
    cdb = [0] * 16
    cdb[0] = opcode
    cdb[1] = subopcode
    cdb[2] = 0 #options & 0xFF
    cdb[3] = 0# options >> 8 & 0xFF
    cdb[4] = int(address & 0xFF)
    cdb[5] = int(address >> 8 & 0xFF)
    cdb[6] = int(address >> 16 & 0xFF)
    cdb[7] = int(address >> 24 & 0xFF)
    cdb[8] = Value & 0xFF
    cdb[9] = Value >> 8 & 0xFF
    cdb[10] = Value >> 16 & 0xFF
    cdb[11] = Value >> 24 & 0xFF
    logger = vtfContainer.GetLogger()
    logger.Info("", "Issuing WRITE_SFR (0xBB) diag for Register 0x%X, Value 0x%X"%(address, Value))
    #cdb = [0xC1, 0, 0, 0, 0x9C, 0x00, 0x01, 0xF0, 0x4, 0x0, 0, 0, 0, 0, 0, 0]
    buf = SendDiagnostic(vtfContainer, buf, cdb, WRITE_DATA, 1, 0xC1, "WRITE_SFR")

    return buf


def PerformGCRRPhase1Only(vtfContainer, option=1):
    #snddiag([0xCA,0x2A,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0,0x00,0x00,0x00,0x00,0x00], 1, 1, rdb)
    opcode = 0xCA
    subopcode = 0x2A

    cdb = [opcode, subopcode,option,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0,0x00,0x00,0x00,0x00,0x00]
    buf = pyWrap.Buffer.CreateBuffer(1)
    buf = SendDiagnostic(vtfContainer, buf, cdb, WRITE_DATA, 1, 0xCA, "GC_PHASE1_ONLY")
    return buf

def GetHostEpwrSlotInfo(vtfContainer):
    opcode = 0xC9
    subOpcode = 0x58 #0x53
    logger = vtfContainer.GetLogger()
    Buf = pyWrap.Buffer.CreateBuffer(1,0)
    cdb = [opcode,subOpcode,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    logger.Info("", "Diagnostic command (Host EPWR Slot Info Opcode 0x%x, Sub opcode 0x%x)" %(opcode,subOpcode))
    Buf = SendDiagnostic(vtfContainer,Buf, cdb, 0,1)
    slotsFilled = Buf.GetOneByteToInt(0)
    return slotsFilled

def GetReadRetryDetails(vtfContainer):
    #Die – 1byte
    #Block – 2bytes
    #Wordline – 1byte
    #String – 1byte
    #Syn Wt – 4byte
    #BES Optimum DAC - 7 bytes
    #Failed Page – 1byte
    #RR Stage – 1byte

    opcode = 0xC9
    subopcode = 0x4D

    cdb = [opcode,subopcode,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
    buf = pyWrap.Buffer.CreateBuffer(2)
    buf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, 2, 0xC9, "GET_READ_RETRY_DETAILS")
    return buf

def GetReadErrorCounters(vtfContainer):
    #Die – 1byte
    #Block – 2bytes
    #Wordline – 1byte
    #String – 1byte
    #Syn Wt – 4byte
    #BES Optimum DAC - 7 bytes
    #Failed Page – 1byte
    #RR Stage – 1byte

    opcode = 0xC9
    subopcode = 0x52 #0x54

    cdb = [opcode,subopcode,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
    buf = pyWrap.Buffer.CreateBuffer(1)
    buf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, 1, 0xC9, "GET_READ_RETRY_DETAILS")
    return buf

def ForceBootUpdate(vtfContainer, enable=1):
    """
    Diagnostic to Enable/Disable Force GC
    Disable =0
    Enable = 1
    """
    #card = testspace.GetCard()
    opcode = SET_MML_DATA
    subOpcode = 32
    #option1=enable  #
    #option2=urgent
    cdbData = [opcode,subOpcode,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    direction = WRITE_DATA
    data_buf = pyWrap.Buffer.CreateBuffer(1,0)
    #data_buf = Buffer.Buffer(SINGLE_SECTOR)
    SendDiagnostic(vtfContainer, data_buf, cdbData, direction, DIAG_SECTORLENGTH, SET_MML_DATA,
                   commandName="Force Boot Update")

    return

def GetSourceSlotsFilled(vtfContainer):

    opcode = 0xC9
    subopcode = 0x5A #0x56

    cdb = [opcode, subopcode,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0,0x00,0x00,0x00,0x00,0x00]
    buf = pyWrap.Buffer.CreateBuffer(1)
    buf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, 1, 0xC9, "GC_SOURCE_SLOTS_FILLED")
    slotsFilled = buf.GetOneByteToInt(0)
    return slotsFilled

def GetGCRandomClosedBlocks(vtfContainer):

    opcode = 0xC9
    subopcode = 0x5B #0x57

    cdb = [opcode, subopcode,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0,0x00,0x00,0x00,0x00,0x00]
    buf = pyWrap.Buffer.CreateBuffer(1)
    buf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, 1, 0xC9, "GC_CLOSED_RANDOM_BLOCKS")
    closedRandomBlks = buf.GetOneByteToInt(0)
    return closedRandomBlks

def GetZQCalRAMAddress(vtfContainer):

    opcode = 0xC9
    subopcode = 0x59 #0x55

    cdb = [opcode, subopcode,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0,0x00,0x00,0x00,0x00,0x00]
    buf = pyWrap.Buffer.CreateBuffer(1)
    buf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, 1, 0xC9, "ZQ_CALIBRATION_RAM_ADDRESS")
    return buf

############################################################################################################################
###################################### Production Diags - ROM mode #########################################################
############################################################################################################################

BOTFileSectorLimit=128
DLE_FormatTimeout=200

def ExtractFilesFromBot(botfile, OutputDir, logger, configfiles=None):
    import BotExploder
    botfilename=os.path.basename(botfile)
    botfilepath=os.path.dirname(botfile)
    FormatDataFile=None
    os.chdir(botfilepath)
    filesFromBot = BotExploder.ExplodeBOT( botfilename, OutputDir )
    if not filesFromBot:
        logger.error("No files extracted from BOT file '%s'", botfilename)
        raise RuntimeError("No files extracted from BOT file '%s'" % botfilename)
    curdir = os.getcwd()
    os.chdir(OutputDir)
    return filesFromBot


def gotoDLE(vtfContainer, botfile, endDle = True, filesFromBot=None):

    import random
    logger = vtfContainer.GetLogger()
    livet = vtfContainer._livet
    logger.Info("", "Enters DLE")
    bbl_list = []
    tempStr = botfile.split('\\')
    extracttempdir = '\\'.join(tempStr[:-1])
    if not filesFromBot:
        filesFromBot= ExtractFilesFromBot(botfile, extracttempdir, logger)
    FormatDataFile=os.path.join(extracttempdir,"FD.bin")
    logger.Info("", "Sending Format Command..")
    SendFormatCommand(livet,FormatDataFile) #Livet API

    StartSecs, StartNS = livet.GetSimulationTime()
    while 1:
        logger.Info("", "Format in Progress")
        status =getFormatStatusCommand(livet)        #Livet API
        livet.GetCmdGenerator().Delay(0,500 * 1000 * 1000)  # 500 milliseconds between retries
        if status == 3 or status == 4:
            break
        if status > 4:  # invalid status
            raise RuntimeError("Invalid status from GetFormatStatus")
        if livet.GetSimulationTime()[0] - StartSecs > DLE_FormatTimeout:
            raise RuntimeError("Format Failed to complete after % seconds"% DLE_FormatTimeout)
    if status == 3:
        logger.Info("", "++ Format Completed: Status: %s" % status)
    else:
        raise RuntimeError("Format completed with error")

    writeFilesFromBOT(livet, logger, extracttempdir,filesFromBot)

    if endDle:
        import SDCommandWrapper as SDWrap
        SDWrap.WriteFile42()
        SendDLEEnd(livet, logger)
        logger.Info("", "*******DLE DONE/COMPLETED********")
    return True


def SendFormatCommand(Model,FormatDataFile):
    ''' Send the format command, SCTP command 8f.
        Search wiki for "Chorus Common Files.doc"

        Configuration comes from (optional) binary file, with (optional)
        command line overrides.
    '''
    import FormatData
    cmd = 0x8f
    buf = Model.GetDataBlock(512)
    db = CreateSCTPdatabuffer(0, cmd, buffertemp=buf)
    if not Model.GetCmdGenerator().WriteSectors(cmd, 1, db):
        showError("Write")

    theFormatData = FormatData.FormatData(FormatDataFile)
    bufferSize = 0x2000
    db = Model.GetDataBlock(bufferSize * 512)

    for i in range(512):
        db.SetByte(i, theFormatData[i])

    #Send off file14 as the Data Phase, and read back a status sector.
    if not Model.GetCmdGenerator().WriteSectors(cmd, 1, db):
        showError("Write")
    if not Model.GetCmdGenerator().ReadSectors(cmd, 1, db):
        showError("Write")

    #writeData(cmd, 1, db)
    #readData(cmd, 1, db)
    status = db.GetDword(0x4c)
    return

def GetFormatStatus(testSpace, lbaDataSize=4096):
    commandName = "GetFormatStatus"
    logger = testSpace.GetLogger()
    dataBuffer = Buffer.Buffer(4096, isSectors=False)
    cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    cdb[0] = 0x70
    formatstatus = 2
    try:
        dataBuffer = SendDiagnostic(testSpace, dataBuffer, cdb, READ_DATA, 8, 0x70, commandName)
        logger.Info("", "Format Device Diagnostic completed successfully")
        formatstatus = dataBuffer.GetByte(0)
        logger.Info("", "FormatStatus: %s" %formatstatus)
    except Exception as exc:
        logger.Info("",  "Error:\n%s" %exc)

    return formatstatus

def getFormatStatusCommand(livet):
    cmd = 0x70
    buf= livet.GetDataBlock(512)
    db = CreateSCTPdatabuffer(1, cmd,buffertemp=buf)
    #print "++ Sending Get Format Status command", attime()
    if not livet.GetCmdGenerator().WriteSectors(cmd, 1, db):
        showError("Write")
    if not livet.GetCmdGenerator().ReadSectors(cmd, 1, db):
        showError("Read")
    bufferSize = 0x2000
    statusDb = livet.GetDataBlock(bufferSize * 512)
    if not livet.GetCmdGenerator().ReadSectors(cmd, 1, statusDb):
        showError("Read")
    status = db.GetByte(0)
    #print "++ Done Sending GetFormatStatus command: '%s'" % FormatStatusDecode(status), attime()
    return status


def GetDataBlocksFromFile(Model, filename, maxsectors=BOTFileSectorLimit, dataBlockSize=512, header=False, headerSize=512):
    ''' Read 'fileNNN' where filenumber is NNN. Create a list of
     datablocks, maximum length 'maxsectors', and return this list, the
     total number of sectors of all datablocks, and the file size in bytes. '''

    if filename.startswith("file") and filename.endswith(".bin"):
        filenumber = int(filename[4:filename.rindex(".")])
    else:
        filenumber = 0

    if not os.path.exists(filename):
        logger.error("Could not open file '%s'", os.path.abspath(filename))
        raise RuntimeError("Could not open file '%s'" % os.path.abspath(filename))

    filesize = os.path.getsize( filename )
    origsize = filesize
    nSectors = old_div((filesize+dataBlockSize - 1),dataBlockSize)

    if not filesize:
        logger.error("%s: zero length file", os.path.abspath(filename))
        raise RuntimeError("%s: zero length file" % os.path.abspath(filename))

    datablocks = []
    f = open(filename, mode="rb")

    if header:
        header.SetDword(4, origsize)
        filesize += headerSize
        db = Model.GetDataBlock(dataBlockSize)
        for i in range(headerSize):
            db.SetByte(i, (header.GetByte(i)))
        for i in range(headerSize, dataBlockSize):
            db.SetByte(i, ord(f.read(1)))
        filesize -= dataBlockSize
        datablocks.append(db)

    while filesize > 0:
        length = min(filesize, maxsectors * dataBlockSize)  #maxsectors*512)
        dbsize = dataBlockSize * (old_div((length + dataBlockSize - 1),dataBlockSize))
        db = Model.GetDataBlock(dbsize)
        for i in range(length):
            db.SetByte(i, ord(f.read(1)))
        # Filesystem files are padded with their file number
        for i in range(filesize, dbsize):
            db.SetByte(i, filenumber)
        filesize -= length
        datablocks.append(db)
    f.close()

    return datablocks, nSectors, origsize

def sendWriteFile(livet, logger, FileNum, Sectors, datablocks):
    # simulate writing a file system file with arbitrary data
    if FileNum==234:
        pass
    cmd = 0x8B
    buf=livet.GetDataBlock(512)
    db = CreateSCTPdatabuffer(0, cmd, Sectors*512,buffertemp=buf)
    #Bytes 84/5 is the fileID, Dword 88 is number of sectors.
    db.SetWord(84,FileNum)
    db.SetDword(88, Sectors)

    logger.Info("", "++ Writing file %s %s sectors"% (FileNum,  Sectors))
    if not livet.GetCmdGenerator().WriteSectors(cmd, 1, db):
        showError("Write")
    for FileData in datablocks:
        nSectors = min(Sectors, BOTFileSectorLimit)
        if not livet.GetCmdGenerator().WriteSectors(cmd, nSectors, FileData):
            showError("Write")
        Sectors -= nSectors

    # Don't forget the terminating status phase of SCTP!
    buf= livet.GetDataBlock(512)
    db = CreateSCTPdatabuffer(1, cmd,buffertemp=buf)
    if not livet.GetCmdGenerator().ReadSectors(cmd, 1, db):
        showError("Read")

def writeFilesFromBOT(livet, logger, outdir,filesFromBot, fileNumber = 0):
    curdir = os.getcwd()
    datablocks = []
    try:
        os.chdir(outdir)
        # Write Entire payload from Botfile
        if (fileNumber == 0):
            for fn in filesFromBot:
                datablocks, nSectors, origsize =  GetDataBlocksFromFile(livet, "file%s.bin" % fn )
                sendWriteFile(livet, logger, fn, nSectors, datablocks)
            #print "++ File %s (%s sectors) written to flash" \
                #% (fn, nSectors), attime()
        else:
            # Write specified fileNumber only
            fn = fileNumber
            datablocks, nSectors, origsize = GetDataBlocksFromFile(livet, "file%s.bin" % fn )
            sendWriteFile(livet, logger, fn, nSectors, datablocks)
            #print "++ File %s (%s sectors) written to flash" \
                #% (fn, nSectors), attime()
    finally:
        os.chdir(curdir)
        for db in datablocks:
            try:
                del db
            except:
                pass

def SendDLEEnd(livet, logger):
    cmd = 0x93
    buf=livet.GetDataBlock(512)
    db = CreateSCTPdatabuffer(1, cmd,DataLen=0,buffertemp=buf)
    db.SetByte(82, 1)

    if not livet.GetCmdGenerator().WriteSectors(cmd, 1, db):
        showError("Write")
    if not livet.GetCmdGenerator().ReadSectors(cmd, 1, db):
        showError("Write")
    status = db.GetDword(0x4c)
    if status != 0:
        raise RuntimeError("++ DLE End failed: Status: %s" % status)
    logger.Info("", "++ Done Sending DLE End command")
    livet.GetCmdGenerator().Delay(1,0)


    ##
    # @brief This method is used to send format command in DLE mode.
    # @details This method sends an SCTP command 0x8F.  To run whole format process, we need to call this function and then
    #          send format status command and check the status until format device status shows format completion.
    # @param in command phase (16 byte CDB)
    #        Option = 1 : Perform special flash write for all user blocks
    #        Option = 2 : Use external BBM structure. Host must transfer MBBT, PS0, PS1 during the data phase
    # @param in command phase (16 byte CDB)
    #        numBytes (only needed for Option = 2) : The number of bytes of the buffer sent from host
def SendFormatCmd(testSpace, Option=2, numBytes=4096, dataBuffer = None):

    commandName = "SendFormatCmd"
    logger = testSpace.GetLogger()

    cdb = [0]*16
    cdb[0] = 0x8F
    cdb[2] = Option & 0xFF
    cdb[3] = ((Option  >> 8) & 0xFF)
    cdb[4] = numBytes & 0xFF
    cdb[5] = (numBytes >> 8) & 0xFF
    cdb[6] = (numBytes >> 16) & 0xFF
    cdb[7] = (numBytes >> 24) & 0xFF

    logger.Info("", "Sending Format Device cmd CDB: %s"%cdb)
    logger.Info("", "Option: %d "%Option)
    logger.Info("", "numBytes: %d "%numBytes)

    if not dataBuffer == None:
        direction = READ_DATA
    elif dataBuffer == None or Option == 1:
        dataBuffer = Buffer.Buffer(8)
        direction = READ_DATA

    try:
        dataBuffer = SendDiagnostic(testSpace, dataBuffer, cdb, direction, 8, 0x8f, commandName)
        logger.Info("", "Format Device Diagnostic completed successfully")
    except Exception as exc:
        logger.Info("",  "Format Device Diagnostic Failed")
        logger.Info("",  "Error:\n%s" %exc)


def CreateSCTPdatabuffer(IsRead, Opcode, DataLen=0x200, Subopcode=0, dwordParam=0,buffertemp=None):
    from struct import unpack, pack
    ''' Construct a SCTP command frame.  '''
    # 00 32 bytes SCTP Signature
    # 20 32 bytes Application Signature: Diagnostic App
    # 40 4  bytes tag
    # 44 4  bytes Offset to LBA
    # 48 1  byte delay sectors before data transfer
    # 49 1  byte delay sectors after data transfer
    # 4a 1  byte Control flag 1 <- 00 = write, 01 = read
    # 4b 1  byte Control flag 2
    # 4c 4  bytes Transfer Length of following Data Phase
    # ---- Application specific bytes (CDB). Refer to FBCC/SCTP command spec
    # 50 16 bytes command:
    # 50 1  Opcode
    #                     8f: Format
    #                     70: GetFormatStatus
    #                     ec: IdentifyDrive
    # 51 1  Chip (unused)
    # 52 1  Subopcode (low byte)
        # 53 1
    # 54 1  byte 0 of optional 4-byte parameter
    # 55 1  byte 1 of optional 4-byte parameter
    # 56 1  byte 2 of optional 4-byte parameter
    # 57 1  byte 3 of optional 4-byte parameter

    # Platform-independent way of extracting the bytes from dword
    # in little-endian order, which is target processor's byte order
    #global singleSectorBuffer
    singleSectorBuffer=buffertemp

    packedDwordParam = pack('<l', dwordParam)
    bytes = unpack('4b', packedDwordParam)

    sctp_command_frame = '''
      dd 4c 02 d8 0f f5 0a 70 5e 7f 5a 84 c6 f7 4b 6b
      d2 42 71 28 46 42 7b 89 7d 8c 55 7c 3a 5a 30 39
      10 25 42 eb 4e 10 90 8f 4b 45 6f 88 4f f2 9f 61
      5d ec 18 d2 2b 71 60 f4 be 58 cb 04 87 f7 cf 94
      00 00 00 00 00 00 00 00 00 00 %s 00 00 02 00 00
      %s 00 %s 00 %s %s %s %s 00 00 00 00 00 00 00
   ''' % (hex(IsRead),
          hex(Opcode),
          hex(Subopcode),
          hex(bytes[0]),
          hex(bytes[1]),
          hex(bytes[2]),
          hex(bytes[3]))

    # Poke the command frame into a datablock and return it
    db = singleSectorBuffer
    for i, data in enumerate(sctp_command_frame.split()):
        db.SetByte(i, int(data, 16))
    # Set the length of the next phase.
    db.SetDword(0x4c, DataLen)
    return db






def AutoTrimStart(vtfContainer, numClkConfigSets, numOscTrimSets, dataBuffer):
    opcode = 0xF2

    cdb = [opcode, 1, 4, 1, 1, 0, 0, 0, 0, 0, numClkConfigSets, numOscTrimSets, 0, 0, 0, 0]
    statusList = SendDiagnostic(vtfContainer, dataBuffer, cdb, WRITE_DATA, TWO_SECTORS, opcode, returnStatus=True)

    status = statusList[0] | statusList[1] << 8 | statusList[2] << 16 | statusList[3] << 24
    return status


def AutoTrimStop(vtfContainer, hostClkFreq):
    opcode = 0xF2

    cdb = [opcode, 0, 4, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    cdb[12] = ((hostClkFreq >>0)&0xff)
    cdb[13] = ((hostClkFreq >>8)&0xff)
    cdb[14] = ((hostClkFreq >>16)&0xff)
    cdb[15] = ((hostClkFreq >>24)&0xff)

    statusList = SendDiagnostic(vtfContainer, None, cdb, NO_DATA, 0, opcode, returnStatus=True)
    status = statusList[0] | statusList[1] << 8 | statusList[2] << 16 | statusList[3] << 24

    return status




def JumpToRom(vtfContainer, option) :

    opcode = 0x90
    buf = pyWrap.Buffer.CreateBuffer(1)
    options = 0x01
    cdb = [0x90, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    cdb[2] = (options & 0xFF)
    cdb[3] = (options >> 8) & 0xFF
    #cdb = [0xF2, 1, 4, 1, 1, 0x00, 0x00, 0x00, 0x00, 0x0, 6, 6, 0, 0, 0, 0]
    buf = SendDiagnostic(vtfContainer, None, cdb, NO_DATA, 1, opcode, bIsStatusPhase=False)

    return


def GetEFuseData(vtfContainer, option=1):
    """
    option = 0 EFuse data will be read from MIP
    option = 1 EFuse data will be read from EFuse
    """

    opcode = 0xA7
    subOpcode = option

    buf = pyWrap.Buffer.CreateBuffer(1, patternType=pyWrap.ALL_0, isSector=True)
    cdb = [0] * 16

    cdb = [opcode, subOpcode, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    dataBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, 1, opcode, commandName="Get Efuse data")

    return dataBuf


def GetEfuseCrcStatus(vtfContainer):

    opcode = 0xA3
    subOpcode = 0

    buf = pyWrap.Buffer.CreateBuffer(1, patternType=pyWrap.ALL_0, isSector=True)
    cdb = [0] * 16

    cdb = [opcode, subOpcode, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    dataBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, 1, opcode, commandName="Get Efuse Crc Status")

    waferSortCrc = dataBuf.GetOneByteToInt(0)
    packageCrc = dataBuf.GetOneByteToInt(1)
    return waferSortCrc, packageCrc


def WriteEfuseData(vtfContainer, option=None):

    opcode = 0x46
    subopcode = option

    if option == None or option < 1 or option > 2:
        raise TestError.TestFailError("", "Write EFuse Option[1 or 2] not specified")

    buf = pyWrap.Buffer.CreateBuffer(1, patternType=pyWrap.ALL_0, isSector=True)

    cdb = [opcode, subopcode, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    status = SendDiagnostic(vtfContainer, buf, cdb, 2, 0, opcode, commandName="Write Efuse data", returnStatus=True)

    return status

def GetHCForBlocksinDFBL(vtfContainer):

    opcode = 0xC9
    subopcode = 0x5C #89

    cdb = [opcode, subopcode,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0,0x00,0x00,0x00,0x00,0x00]
    buf = pyWrap.Buffer.CreateBuffer(1)
    buf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, 1, 0xC9, "GET_HC_FOR_BLOCKS_IN_DFBL")
    return buf

def isValidLatch(vtfContainer):

    opcode = 0xC9
    subopcode = 0x57 #0x52

    cdb = [opcode, subopcode,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0,0x00,0x00,0x00,0x00,0x00]
    buf = pyWrap.Buffer.CreateBuffer(1)
    buf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, 1, 0xC9, "IS_VALID_LATCH")

    return buf

def GetPGCTrackerQuotas(vtfContainer):
    import FileData
    opcode = 0xc9
    subopcode = 0x5D #0x5a
    logger = vtfContainer.GetLogger()
    file21Obj = FileData.ConfigurationFile21Data(vtfContainer)

    cdb = [opcode, subopcode,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0,0x00,0x00,0x00,0x00,0x00]
    buf = pyWrap.Buffer.CreateBuffer(1)
    buf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, 1, 0xC9, "GET_PGC_Trakcer_Quota")
    buf.PrintToLog()
    #Enums
    Enum_size = 8
    WorstTime_Offset = 6
    GCC_ComponentsList = ["HOST_EPWR", "GAT_COMPACTION", "GAT_EPWR" , "FS_COMPACTION", "GCC_SCAN" , "GCC_READ" , "GCC_WRITE" , "GCC_COMMIT_MLC" , "GCC_COMMIT_SLC", "GCC_PC_COMMIT_MLC",
                          "GCC_PC_COMMIT_SLC", "GCC_ONE_PHASE_MLC", "GCC_ONE_PHASE_SLC" , "GAT_SYNC_GC" ,  "GCC_HANDLE_PCWA_MLC", "GCC_HANDLE_PCWA_SLC" , "GCC_EPWR_MLC", "GCC_EPWR_SLC" ,
                          "GCC_DEST_EXCHANGE_MLC", "GCC_DEST_EXCHANGE_SLC", "GCC_PADDING_MLC", "GCC_PADDING_SLC", "GCC_PC_RGAT_COMMIT_MLC", "GCC_PC_RGAT_COMMIT_SLC" , "GCC_IDLE_MLC", "GCC_IDLE_SLC"]

    GCC_PGC_Dict = ['HOST_EPWR', 'GAT_COMPACTION', 'GAT_EPWR', 'FS_COMPACTION','GCC_PHASED_GC_IN_PROGRESS', 'GCC_PHASED_GC_IN_PROGRESS', 'GCC_PHASED_GC_IN_PROGRESS', 'GCC_PHASED_COMMIT', 'GCC_PHASED_COMMIT', 'GCC_PHASED_PC_COMMITS',
                    'GCC_PHASED_PC_COMMITS', 'GCC_PHASED_GC_IN_PROGRESS', 'GCC_PHASED_GC_IN_PROGRESS', 'GAT_SYNC', 'GCC_HANDLE_PC_WA', 'GCC_HANDLE_PC_WA', 'GCC_PHASED_EPWR', 'GCC_PHASED_EPWR',
                    'GCC_DEST_EXCHANGE', 'GCC_DEST_EXCHANGE','GCC_PHASED_PADDING', 'GCC_PHASED_PADDING','GCC_PC_RGAT_COMMIT', 'GCC_PC_RGAT_COMMIT', 'GCC_IDLE', 'GCC_IDLE']
    GCC_Components = {}

    logger.Info("","-"*100)

    for i in range(0, len(GCC_ComponentsList)):
        GCC_Components[GCC_ComponentsList[i]] = buf.GetTwoBytesToInt( i * Enum_size + WorstTime_Offset)
        PGCQuotaTimeTaken = GCC_Components[GCC_ComponentsList[i]]

        if GCC_PGC_Dict[i] != None:
            PGCQuotaLimit = file21Obj.PGCQuotaValues_Dict[GCC_PGC_Dict[i]]
            if PGCQuotaTimeTaken > PGCQuotaLimit:
                logger.Info(""," ERROR [QUOTA_LIMIT_EXCEEDED] ::: PGC Component %s   : %d milliseconds , QUOTA LIMIT : %d "%(GCC_ComponentsList[i], PGCQuotaTimeTaken, PGCQuotaLimit ))

    import Core.ExecutionInfo as ExecutionInfo

    executionInfoObj = ExecutionInfo.ExecutionInfo()
    GCComponentDictinfo = executionInfoObj.convertDictToString(GCC_Components)

    maxLineLen = max([len(line) for line in GCComponentDictinfo.split("\n")]) + 80
    logger.Info("","<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< GC COMPONENTS WORST CASE TIME (in Milliseconds) >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")

    header = "\n" + GCComponentDictinfo + "\n"
    vtfContainer.logger.Info("","{0}".format(header))
    logger.Info("","-"*100)
    return


def ErasePhyBlock(vtfContainer, option_0=0, option_1=0):
    #Opcode: Diag_Erase_PhyBlock      0x81
    #uint8  opcode;
    #uint8  chip;
    #uint16 option; used as a flag; utilize bitmapping to indicate type of access, type of block erase through option flag
    #Flag = 0 - Normal erase mode
    #Flag = ERASE_FACTORY_BB                0x01 - Erase factory defect block
    #Flag = 2 - Do not erase grown defects
    #flag = ERASE_ENTIRE_CARD               0x04 // if set, erases the entire card
    #USE_BINARY_ACCESS               0x200 // to indicate binary access mode
    #uint16 phyBlock;
    #uint16 unassigned;
    #uint32 blockCount; (no of blocks to be erased) #fails at blockCount = 160 (threshold) for normal erase operation; Timeout issue resolved
    #FACTORY_BB_SIG                  0xDEAD(factory marked bad block signature)
    #To erase entire card            0x00
    #uint32 reserved;

    opcode = 0x81
    subopcode = 0

    #phyBlock possible values 8,9,28,27,25,19,13..
    phyBlock_0 = 10
    phyBlock_1 = 0
    unassigned_0 = 0
    unassigned_1 = 0
    #blockCounnt 0xDEAD FACTORY_BB_SIG
    blockCount_0 = 200 #0xAD #173
    blockCount_1 = 0 #0xDE #222
    blockCount_2 = 0
    blockCount_3 = 0

    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode, subopcode, option_0 , option_1,
           phyBlock_0 ,phyBlock_1, unassigned_0, unassigned_1,
           blockCount_0, blockCount_1, blockCount_2, blockCount_3,
          0,0,0,0]

    SendDiagnostic(vtfContainer, buf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName="Erase Physical Block")
    return

def DoDataSwap(vtfContainer):
    opcode = 0xCF
    subOpcode = 0

    buf = pyWrap.Buffer.CreateBuffer(1,0)

    cdb = [opcode,subOpcode, 0, 1,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    status = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName="Do Data Swap")
    return status

def GetRamToFlash(vtfContainer):
    #Opcode: 0xB7

    #uint8  opcode;
    #uint8  reserved1;
    #uint8  lba[4];                  // This is not aligned to 4 bytes
    #uint8  sectorCount[4];
    #uint8  unused[6] transferSize;
    commandName="Get Ram to Flash"
    opcode = 0xB7
    lba_0 = 0x11
    lba_1 = 0x00
    lba_2 = 0
    lba_3 = 0
    sectorCount_0 = 1
    sectorCount_1 = 0
    sectorCount_2 = 0
    sectorCount_3 = 0

    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode, 0, lba_0, lba_1,
           lba_2, lba_3, sectorCount_0, sectorCount_1,
           sectorCount_2, sectorCount_3, 22,0,
          0,0,0,0]

    readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    #readBuf.SetByte(0, 1)
    #readBuf.SetByte(1, 7)
    #readBuf.SetByte(2, 3)
    #readBuf.SetByte(3, 2)
    #readBuf.SetByte(4, 1)
    return readBuf

def GetFlashToRam(vtfContainer):
    #Opcode: 0xB4
    #uint8  opcode;
    #uint8  reserved1;
    #uint8  lba[4];                  // This is not aligned to 4 bytes
    #uint8  sectorCount[4];
    #uint8  unused[6] transferSize;
    commandName="Get Flash to Ram"
    opcode = 0xB4
    lba_0 = 10
    lba_1 = 0
    lba_2 = 0
    lba_3 = 0
    sectorCount_0 = 1
    sectorCount_1 = 0
    sectorCount_2 = 0
    sectorCount_3 = 0

    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode, 0, lba_0, lba_1,
           lba_2, lba_3, sectorCount_0, sectorCount_1,
           sectorCount_2, sectorCount_3, 0,0,
          0,0,0,0]

    readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)

    return readBuf

def ReadCFGConf(vtfContainer):
    commandName="Read CFG Config"
    opcode = 0xCB
    subOpcode = 0

    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode,subOpcode, 0, 0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    return readBuf

def ReadFwCFGConf(vtfContainer):
    commandName="Read CFG Config"
    opcode = 0xCC
    subOpcode = 0

    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode,subOpcode, 0, 0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    return readBuf

def ReadBEConf(vtfContainer):
    commandName="Read BE Config"
    opcode = 0xCD
    subOpcode = 0

    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode,subOpcode, 0, 0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    return readBuf

def EraseBlock_NewFormat(vtfContainer, option_0=0, option_1=0):
    #Opcode: 0xB6

    #uint8 opcode;
    #uint8 chip;
    #uint8 die;
    #uint8 plane;
    #uint16 block;
    #uint16 option; bitmapping -> ERASE_FACTORY_BB 0x01, USE_BINARY_ACCESS 0x200 (option_1 = 0x02), ERASE_ENTIRE_CARD 0x04
    #uint32 blockCount; no of blocks to be erased, blockCount = 0 for full card erase
    #uint32 reserved;

    opcode = 0xB6
    chip = 0
    die = 1
    plane = 0
    block_0 = 0
    block_1 = 0

    blockCount_0 = 1
    blockCount_1 = 0
    blockCount_2 = 0
    blockCount_3 = 0

    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode, chip, die, plane,
           block_0, block_1, option_0, option_1,
           blockCount_0, blockCount_1, blockCount_2, blockCount_3,
          0,0,0,0]

    SendDiagnostic(vtfContainer, buf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName="Erase Block NewFormat")
    return

def ReadRelinkEntryOffset(vtfContainer):
    commandName="Read Relink Entry"
    opcode = 0x55
    subOpcode = 0

    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode,subOpcode, 0, 0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    return readBuf

def ReadRelinkEntryPhysicalBlocks(vtfContainer):

        #uint8  opcode;
        #uint8  mmlDataType; //subopcode
        #uint16 options;   // for passing block number
    commandName="Read Relink Entry Physical Blocks"
    opcode = 0x56
    subOpcode = 0
    options_0 = 0x7E
    options_1 = 0x0

    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode,subOpcode, options_0, options_1,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    return readBuf

def ToggleModeCommand(vtfContainer, option=0):
    #uint8   opcode; 0xF9
    #uint8   option; 1
    #M_WRITE          = 0x01,
    #TM_READ           = 0x02,
    #TM_WR_RD          = 0x03,
    #TM_WR_RD_CMP      = 0x04,
    #TM_WR_RD_CMP_ALL  = 0x05
    #uint16  loopCount; 2
    #uint8   bankNum; 4
    #uint8   chipNum; 5
    #uint8   dieNum; 6
    #uint8   reserved1; 7
    #uint32  reserved2; 8
    #uint32  reserved3; 12
    commandName = "Toggle Mode Command"
    opcode = 0xF9
    loopCount_0 = 10
    loopCount_1 = 0
    bankNum = 0
    chipNum = 0
    dieNum = 0
    buf = pyWrap.Buffer.CreateBuffer(1)
    #for i in range(0,1000, 1):
        #Buf.SetByte(i, i)

    #Buf.SetByte(0, 1)
    #Buf.SetByte(1, 7)
    #Buf.SetByte(2, 3)
    #Buf.SetByte(3, 2)
    #Buf.SetByte(4, 1)

    cdb = [opcode, option, loopCount_0, loopCount_1,
           bankNum, chipNum, dieNum,0,
           0,0,0,0,
          0,0,0,0]

    SendDiagnostic(vtfContainer, buf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)
    return

def DistributionRead(vtfContainer, subOpcode=0, readFlag=0):

    #uint8  opcode;
    #uint8  subopcode;
    # DIAG_CMD_READ_DISTR_SubOpcodeRead           (0x00)
    # DIAG_CMD_READ_DISTR_SubOpcodeQueryParams    (0x01)
    # DIAG_CMD_READ_DISTR_SubOpcodeSetParams      (0x02)
    #uint8  bankNumber;
    #uint8  chip;
    #uint8  die;
    #uint8  plane;
    #uint16 block;
    #uint16 page;
    #uint8  eccPage;
    #uint8  count;
    #uint8  isSLC;
    #uint8  isNDWL;
    commandName = "Distribution Read"
    opcode = 0xDD

    bankNumber = 0
    chip = 0
    die = 0
    plane = 0
    block_0 = 0
    block_1 = 0
    page_0 = 0
    page_1 = 0
    eccPage = 0
    if subOpcode == 0:
        count = 4
    else:
        count = 1
    isSLC = 0
    isNDWL = 0

    buf = pyWrap.Buffer.CreateBuffer(count)
    #buf.SetByte(0, 1)
    cdb = [opcode,subOpcode, bankNumber, chip,
           die, plane, block_0, block_1,
           page_0, page_1, eccPage, count,
          isSLC, isNDWL,0,0]
    if subOpcode==0x2 and readFlag==1:
        SendDiagnostic(vtfContainer, buf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)
        return
    elif readFlag==0:
        readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, count, opcode, commandName)
        return readBuf

def SwitchEraseMode(vtfContainer):
    commandName = "Switch Erase Mode"
    opcode = 0xE5
    eraseMode = 1

    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode,eraseMode, 0, 0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    SendDiagnostic(vtfContainer, buf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)
    return

def ReadSuspendResumeRegisters(vtfContainer):
    commandName = "Suspend Resume Register"
    opcode = 0xD4
    subOpcode = 0

    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode,subOpcode, 0, 0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    return readBuf

def ReadWaferSort(vtfContainer, readType=0):
    #Opcode: 0xC4
    #uint8   opcode;
    #uint8   die;
    #uint8   readType;
    #DFD_GET_LOT_ID = 0,
    #DFD_GET_WAFER_NUMBER = 1,
    #DFD_GET_X_LOCATION = 2,
    #DFD_GET_Y_LOCATION = 3
    commandName = "Read Wafer Sort"
    opcode = 0xC4
    die = 0
    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode, die, readType, 0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    return readBuf

def ReadMMLCheckSystemTime(vtfContainer):
    #Opcode: 0xC8
    #uint8  opcode;
    #uint8  subopcode;    // '0' be the only subOpcode
    #uint8 option // delay in ms for loop to iterate
    commandName = "Read MML System Time"
    opcode = 0xC8
    subOpcode = 0
    option = 100

    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode,subOpcode, option, 0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    return readBuf

def GetTimingData(vtfContainer):
    #Opcode: 0xC0
    #Sub Opcode:
    #SUBOP_GET_DATA                          (0x00)
    #SUBOP_CLEAR_DATA                        (0x01)
    commandName = "Get Timing Data"
    opcode = 0xC0
    subOpcode = 0x0
    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode,subOpcode, 0, 0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    return readBuf

def SetTimingData(vtfContainer):
    #Opcode: 0xC0
    #Sub Opcode:
    #SUBOP_GET_DATA                          (0x00)
    #SUBOP_CLEAR_DATA                        (0x01)
    commandName = "Set Timing Data"
    opcode = 0xC0
    subOpcode = 0x1
    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode,subOpcode, 0, 0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    SendDiagnostic(vtfContainer, buf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)
    return

def GetScannedBootBlockList(vtfContainer): # need to add in DLE?
    #Opcode: 0xC0
    #Sub Opcode:
    commandName = "Get Scanned Boot Block List"
    opcode = 0xC0
    subOpcode = 0

    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode,subOpcode, 0, 0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    return readBuf

def ReadMAPFile(vtfContainer):
    commandName = "Read MAP File"
    opcode = 0xC3
    subOpcode = 0

    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode,subOpcode, 0, 0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    return readBuf

def GetRomInitBeInfo(vtfContainer, subOpcode=0): # need to add in DLE?
    #Opcode: 0xA5
    #Sub Opcode:
    #uint8   opcode;
    #uint8   subopcode;
    #DDR_SDR_INFO=0,
    #LDPC_CONFIG_TYPE = 1
    #CONTROL_BLOCK_INFO = 2
    #FLASHPADORDER = 3
    #DLECOMPLETE_STATUS = 4
    #FIRMWARE_PARAMETER_INFO = 5
    #uint8   reserved[14]
    commandName = "Get ROM INIT BE INFO"
    opcode = 0xA5

    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode,subOpcode, 0, 0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    return readBuf

def GetSumCmds(vtfContainer, subOpcode_0=0, readFlag=0, type_0=0):
    #Opcode: 0xA5
    #BYTE  opcode;
    #BYTE  reserved;
    #WORD  subopcode;
    #CHECK_SUM_SET                              0x00
    #CHECK_SUM_GET                              0x01
    #DWORD startLBA; // required only for set operation
    #DWORD numberOfSector; // required only for set operation
    #WORD  type; // required only for set operation
    #REGULAR_CHECK_SUM_TYPE        0
    #PROTECTED_CHECK_SUM_TYPE      1
    #WORD reserved2;
    commandName = "Check Sum CMD"
    opcode = 0xA5
    subOpcode_1 = 0
    startLBA_0 = 0x10
    startLBA_1 = 0x10
    startLBA_2 = 0x00
    startLBA_3 = 0x00
    numberOfSector_0 = 1
    numberOfSector_1 = 0
    numberOfSector_2 = 0
    numberOfSector_3 = 0
    type_1 = 0
    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode, 0, subOpcode_0, subOpcode_1,
           startLBA_0, startLBA_1, startLBA_2, startLBA_3,
           numberOfSector_0, numberOfSector_1, numberOfSector_2, numberOfSector_3,
          type_0, type_1,0,0]
    if readFlag==1:
        SendDiagnostic(vtfContainer, buf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)
        return
    elif readFlag==0:
        readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
        return readBuf

def GetPatchFunctionAddress(vtfContainer):
    commandName = "Patch function Address"
    opcode = 0xB5
    subOpcode = 0

    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode,subOpcode, 0, 0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    return readBuf

def GetSpeedClassCmd(vtfContainer, subOpcode=0):
    #Opcode: 0x52

    #BYTE  opcode;
    #BYTE  reserved;
    #BYTE  reserved0;
    #BYTE  subopcode;
    #DIAG_SPEED_CLASS_FAT_DATA 1
    #DIAG_SPEED_CLASS_BE_MODE  2
    commandName = "Speed Class CMD"
    opcode = 0x52
    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode, 0, 0, subOpcode,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    return readBuf

def ReadBadBlockTableDLE(vtfContainer):
    #Opcode: 0xB3
    #Sub Opcode:
    #uint8  opcode;
    #uint8  subopcode;
    #uint8  reserved[14];
    commandName = "Read BadBlock Table"
    opcode = 0xB3
    subOpcode = 0
    reserved_0 = 0 #chip
    reserved_1 = 1 #die
    reserved_2 = 1 #uncertain regarding what it does
    reserved_3 = 0x01 #offsetInROMFuse_0
    reserved_4 = 0x00 #offsetInROMFuse_1

    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode, subOpcode, reserved_0, reserved_1,
           reserved_2, reserved_3, reserved_4,0,
           0,0,0,0,
          0,0,0,0]
    readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    return readBuf

def ReadBadBlockTable(vtfContainer, die, sectors, chip, option=0, lsb=0, msb=0):
    #Flashware diag
    #option=0 --> to calculate BB info offset in REGFUSE and return buffer from that offset
    #If user wants to specify the offset from where ROMFUSE should be read, then set option=1 and specify offset using lsb, msb fields
    #Ex: 0x2e00 --> then option=1, lsb=0x00, msb=0x2e
    buf = pyWrap.Buffer.CreateBuffer(sectors, patternType=pyWrap.ALL_1, isSector=True)
    opcode = 0xC9
    cdb = [opcode, 95, chip, die, option, lsb, msb, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, sectors, opcode)
    buf.PrintToLog()
    return buf

def ReadErrorLog(vtfContainer, option_0=0):
    #Opcode: Diag_SYS_Read_ErrorLog       0x82
    #option0 = 0,1,2,4,8
    #ERRLOG_OPT_RD  = 0, Send ErrLog file to host
    #ERRLOG_OPT_SZ  = 1, size of error log (pass sectorCount0 != 1 else will lead to error for size and clear options)
    #ERRLOG_OPT_CLR = 2, clear the error log (pass sectorCount0 != 1 else will lead to error for size and clear options)
    #ERRLOG_OPT_REC = 4, gets number of records
    #ERRLOG_OPT_RAM = 8, limits size or read req to events still in ram (no handler code for this option)
    commandName = "Read Error Log"
    opcode = 0x82
    option_1 = 0
    sectorCount0 = 1 #no of sectors to be read from error log
    sectorCount1 = 0
    sectorCount2 = 0
    sectorCount3 = 0

    buf = pyWrap.Buffer.CreateBuffer(1)

    cdb = [opcode, 0, option_0, option_1,
           0,0,0,0,
           sectorCount0, sectorCount1, sectorCount2, sectorCount3,
          0,0,0,0]
    readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    return readBuf

def GetSplPhasedGCWBBStatus(vtfContainer):
    opCode = 0x9A
    subOpCode = 0x5

    cdb = [opCode,0,subOpCode,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    buf = pyWrap.Buffer.CreateBuffer(1,0)

    readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opCode)
    vtfContainer.GetLogger().Info("", "[Diagnostic] Opcode: 0x%X SubOpcode 0x%X\n" %(opCode,subOpCode))
    return readBuf

def DoSDUnlockFW(vtfContainer):
    #Opcode: 0x89
    #Sub Opcode:
    commandName = "Do BE SD Unlock FW"
    opcode = 0x89
    subOpcode = 0

    buf = pyWrap.Buffer.CreateBuffer(1,0)

    cdb = [opcode,subOpcode, 0, 0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    SendDiagnostic(vtfContainer, buf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)
    return

def GetVersionInfo(vtfContainer, ipSelect_0=0):
    #Opcode: 0xF5
    #Sub Opcode:
    #uint8  opcode
    #uint8  unused
    #uint16 ipSelect
    #return file 51 info to host
    #IP_RESERVED = 0
    #SYS Related IP
    #IP_SYS  = 0x10,
    #IP_RTOS = 0x11,
    #BE Related IP
    #IP_BE= 0x20
    #FE Related IP
    #IP_FE_Common  = 0x40
    opcode = 0xF5
    ipSelect_1 = 0

    cdb = [opcode,0, ipSelect_0, ipSelect_1,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]
    buf = pyWrap.Buffer.CreateBuffer(1,0)

    readBuf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opCode)
    vtfContainer.GetLogger().Info("", "[Diagnostic] Opcode: 0x%X SubOpcode 0x%X\n" %(opCode,subOpCode))
    return readBuf


def SecureFormatProcess(vtfContainer):
    buf = pyWrap.Buffer.CreateBuffer(1, patternType=pyWrap.ALL_1, isSector=True)

    opcode = 0x91
    options = 1 #Default value used in SVP SRW01 script.
    cdb = [opcode, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    cdb[2] = (options & 0xFF)
    cdb[3]  =  (options >> 8) & 0xFF
    SendDiagnostic(vtfContainer, buf, cdb, NO_DATA, SINGLE_SECTOR, opcode)

    return


def SetSecureState(vtfContainer, state):
    buf = pyWrap.Buffer.CreateBuffer(1, patternType=pyWrap.ALL_1, isSector=True)

    opcode = 0x93
    subopcode = 0x02
    cdb = [opcode, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    cdb[2] = (subopcode & 0xFF)
    cdb[3]  =  (subopcode >> 8) & 0xFF
    cdb[4] =  (state & 0xFF)
    cdb[5] =  (state >> 8) & 0xFF
    SendDiagnostic(vtfContainer, buf, cdb, NO_DATA, SINGLE_SECTOR, opcode)

    return

def ReadRomFuse(vtfContainer, romFuseAddressOffset, die, chip=0):
    """
    Name : ReadRomFuseDiagnosticCommand()

    Description : Call the Read ROM FUSE diagnostic command return the buffer

    Aguments:
       vtfContainer              :   Card Test Space
       chip,die               :  chio and die number
       romFuseAddressOffset   : address of rom fuse data to readors

    Returns:
          romFuseBuffer : rom fuse data buffer

    opcode : 0xA2

    subOpcode : 1
    """

    ROM_FUSE_NUM_OF_SECTORS_TO_READ    = 16

    #initialising the buffer
    romFuseBuffer      = pyWrap.Buffer.CreateBuffer(ROM_FUSE_NUM_OF_SECTORS_TO_READ,0x00)

    commandName = "Read ROM Fuse Data"

    #opcode and Sub opcode of diagnostic command
    opcode    = 0xA2     #DGN_NAND_ROM_READ_CMD_opcode
    subOpcode = 1        #DGN_NAND_ROM_READ_ROMFUSE_SUB_opcode
    subOpcodeLowByte  = subOpcode &0xFF
    subOpcodeHighByte = subOpcode >> 8

    #Starting address offsets
    startOffsetLowByte  = romFuseAddressOffset & 0xFF
    startOffsetHighByte = romFuseAddressOffset >> 8

    #Data size in bytes
    sizeOfBufferInBytes     = ROM_FUSE_NUM_OF_SECTORS_TO_READ * BE_SPECIFIC_BYTES_PER_SECTOR
    sizeOfBufferInBytesLow  = sizeOfBufferInBytes & 0xFF
    sizeOfBufferInBytesHigh = sizeOfBufferInBytes >> 8

    #form the CDB for daignostic command
    cdb = [opcode,chip, subOpcodeLowByte,subOpcodeHighByte,
           die,0,0,0,
           0,0,startOffsetLowByte,startOffsetHighByte,
          sizeOfBufferInBytesLow,sizeOfBufferInBytesHigh,0,0 ]

    #Send the diagnostic command
    SendDiagnostic(vtfContainer, romFuseBuffer, cdb, READ_DATA, ROM_FUSE_NUM_OF_SECTORS_TO_READ, opcode, commandName )
    romFuseBuffer.PrintToLog()
    return romFuseBuffer
#end of ReadRomFuseDiagnosticCommand


def GetNANDIDBytes(vtfContainer):
    '''
    Returns a dictionary NANDIDBytes with all the values extracted from ID Bytes
    NANDIDBytes = {
        ManufacturerID   - 0th Byte : For SNDK/TSB, the ID is 0x45
        DevCode          - 1st Byte : Device Density per CE
        CharacterCode    - 2nd Byte : Has info like no of dies, no of states
        NoOfDies         - Extracted from CharacterCode (no of dies in the card)
        NoOfStates       - Extracted from CharacterCode (no of states in a cell)
        MemType          - X3/X4 memory type based on the NoOfStates
        PhysicalPageSize - 3rd Byte : 2nd,3rd bit gives info on the no of bytes each phy page has
        NoOfPlanes       - 4th Byte : Total no of planes in card (not per Die)
        MemNode          - 5th Byte : Bics node
        VarietyCode      - 7th Byte : ?
    }

    @Author: Shaheed Nehal A
    '''
    import Utils
    commandName = "GetNANDIDBytes"
    NO_OF_NAND_ID_BYTES = 8
    opcode = 0xA5
    buf = pyWrap.Buffer.CreateBuffer(1)
    cdb = [opcode, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, 1, opcode, commandName )
    buf.PrintToLog()

    IDBytesdata= []
    for byte in range(NO_OF_NAND_ID_BYTES):
        IDBytedata = buf.GetOneByteToInt(byte)
        IDBytesdata.append(IDBytedata)

    return Utils.GetIDBytesDict(vtfContainer, IDBytesdata)

# Switch the card to ROM mode by means of SCTP command
def JumpToRom(vtfContainer):
    import SDCommandWrapper as SDWrap
    options = 0x01
    cdb = [0x90, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    cdb[2] = (options & 0xFF)
    cdb[3] = (options >> 8) & 0xFF
    SendDiagnostic(vtfContainer, None, cdb, NO_DATA, 0, opcode, commandName )

    time.sleep(2)
    SDWrap.WrapSDCardInit()
    time.sleep(2)  # Allow the card to come back to life after the Jump Idle Loop.
# End of JumpToRom()

def isCardInROMMode(vtfContainer) :
    buf = GetIdentifyDrive(vtfContainer)
    logger = vtfContainer.GetLogger()
    # Check if the ROM info (8 bytes) at offset 0x2E and 0x1B0 match
    # If they match, the card is in ROM mode, else in Flash mode
    if(len(buf.FindMiscompare(this_offset=0x2E, rhs=buf, rhs_offset=0x1B0, count=8)) == 0):
        inRomMode = True
        logger.Info("", "Check result: card is in ROM mode.\n" )
    else:
        inRomMode = False
        logger.Info("", "Check result: card is NOT in ROM mode.\n" )
    return inRomMode
# End of isCardInROMMode()

def GetIdentifyDrive(vtfContainer):
    commandName = "GetIdentifyDrive"
    buf = pyWrap.Buffer.CreateBuffer(1, patternType=pyWrap.ALL_1, isSector=True)
    opcode = 0xEC
    blockLen = 512
    cdb = [opcode, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    cdb[8] = (blockLen & 0xFF)
    cdb[9]  =  (blockLen >> 8) & 0xFF
    cdb[10] =  (blockLen >> 16) & 0xFF
    cdb[11] =  (blockLen >> 24) & 0xFF

    SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, 1, opcode, commandName)
    return buf

def GetGCBalancedInfo(vtfContainer):

    opcode = 0xC9
    subopcode = 97

    cdb = [opcode, subopcode,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0,0x00,0x00,0x00,0x00,0x00]
    buf = pyWrap.Buffer.CreateBuffer(1)
    buf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, 0xC9, "GET GC BALANCED INFO")
    return buf

def SetMLCFBLCount(vtfContainer, option):

    opcode = 0xCA
    subopcode = 0x26 #0x55
        # option : FBL value to be set
    optNumberLo = ByteUtil.LowByte(option)
    optNumberHi = ByteUtil.HighByte(option)
    cdb = [opcode, subopcode,optNumberLo,optNumberHi,0x00,0x00,0x00,0x00,0x00,0x00,0x0,0x00,0x00,0x00,0x00,0x00]
    buf = pyWrap.Buffer.CreateBuffer(1)
    SendDiagnostic(vtfContainer, buf, cdb, WRITE_DATA, SINGLE_SECTOR, 0xCA, "SET MLC Free Block Count")
    return


def GetPhyBlocksInMB(vtfContainer, MB, fwConfig):
    opcode = 0xC9
    subopcode = 96
    LowByte = ByteUtil.LowByte(MB)
    HighByte = ByteUtil.HighByte(MB)
    cdb = [opcode, subopcode, LowByte, HighByte, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    buf = pyWrap.Buffer.CreateBuffer(1)
    SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, "Get Phy Blocks in MB")

    phyBlockList = []
    offset = 33
    chip = buf.GetOneByteToInt(offset)
    logicalDie = buf.GetOneByteToInt(offset-1)
    #die = logicalDie%4
    die = logicalDie%fwConfig.diesPerChip
    offset=0
    for index in range(fwConfig.dieInterleave):
        for plane in range(fwConfig.planeInterleave):
            block = buf.GetTwoBytesToInt(offset)
            addr = (chip, die+index, plane, block)
            phyBlockList.append(addr)
            offset += 2

    return phyBlockList

def GetStaticRelinkedMBList(testSpace, maxMBNum):
    MBList = []
    opcode = 0x66
    cdb = [opcode, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    buf = pyWrap.Buffer.CreateBuffer(0x18)
    SendDiagnostic(testSpace, buf, cdb, READ_DATA, SINGLE_SECTOR*0x18, opcode, "Get Static Relinked MBs", increaseTO=True)

    for byteOffset in range(0, 0x18*512, 2):
        Val = buf.GetTwoBytesToInt(byteOffset)
        if Val == 0xffff:
            break
        MBList.append(Val)

    SLCMBList = []
    MLCMBList = []
    for MB in MBList:
        if GetIGATEntryInfo(testSpace, MB)[4] == 0:
            SLCMBList.append(MB)
        else:
            MLCMBList.append(MB)

        if MB <= maxMBNum:
            testSpace.GetLogger().Error("", "[Test: Error] Relinked MB 0x%X is less than the max MB Num 0x%X"%(MB, maxMBNum))
            raise TestError.TestFailError(testSpace.GetTestName(), "Relinked MB num cannot be <= maxMBNum")

    return SLCMBList, MLCMBList

def GetHCForFS(vtfContainer):

    opcode = 0x61
    subopcode = 3

    cdb = [opcode, subopcode,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0,0x00,0x00,0x00,0x00,0x00]
    buf = pyWrap.Buffer.CreateBuffer(1)
    buf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode)
    return buf

def SetBalancedGCThreshold(vtfContainer, GCType, FBLcount):
    opcode = SET_MML_DATA
    subopcode = 54
    GCTypeLowByte = ByteUtil.LowByte(GCType)
    GCTypeHighByte = ByteUtil.HighByte(GCType)
    FBLcountLowByte = ByteUtil.LowByte(FBLcount)
    FBLcountHighByte = ByteUtil.HighByte(FBLcount)
    cdb = [opcode, subopcode, GCTypeLowByte, GCTypeHighByte, FBLcountLowByte, FBLcountHighByte, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    buf = pyWrap.Buffer.CreateBuffer(1)
    SendDiagnostic(vtfContainer, buf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, "Set BALANCED GC Threshold")
    return

def MaskAssertUrgentGC(vtfContainer, disable = 0):
    opcode = SET_MML_DATA
    subopcode = 55
    cdb = [opcode, subopcode, disable,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0,0x00,0x00,0x00,0x00,0x00]
    buf = pyWrap.Buffer.CreateBuffer(1)
    buf = SendDiagnostic(vtfContainer, buf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, "MASK URGENT GC ASSERT")
    return

def GetMIPGeneralVariables(vtfContainer):
    """
    Name : GetMMLSpareBlockCount()

    Description : This function calls "Get MML Data diag(0xC9)", to get spare block count info.

    Arguments :
              testSpace - TestSpace Object

    Returns :
             configParams : Spare block count for TLC and SLC blocks

    opcode : 0xC9

    subopcode : 42

    """
    MIPSize = 4084
    commandName = "Get spare block count"
    logger = vtfContainer.GetLogger()
    opcode = 0xC9
    subOpcode = 67
    dataBuffer = pyWrap.Buffer.CreateBuffer(8)

    cdb = [opcode, subOpcode, 0, 0,
           0, 0, 0, 0,
           0, 0, 0, 0,
          0, 0, 0, 0]

    logger.Info("","Diag: 0x%X, subOpcode: %s Data Direction: %s" %(opcode,subOpcode, READ_DATA))
    dataBuffer = SendDiagnostic(vtfContainer,dataBuffer, cdb, READ_DATA, 8, opcode, commandName)

    return dataBuffer

def GetIGATEntryForAllMetablocks(vtfContainer, num_mbs ):
    """
    Description:
        Sends diagnostic call with opcode = 201 (0xC9 - Get MML Data ) and
        subopcode = 47 (0x2F) to receive IGAT entries for all metablocks in the
        firmware.
    Arguments:
        testspace = handle to TestFramework.TestSpace object
    Returns:
        buf = buffer containing IGAT entries for all metablocks
    """
    opcode      = 201
    subopcode   = 47
    commandName = "Get IGAT Entries For All Metablocks"
    bankNum     = 0
    cdb         = [
        opcode, subopcode, 1, 0,
        0, 0, 0, 0,
       0, 0, bankNum, 0,
      0, 0, 0, 0
    ]

    bufsize = ( old_div(( num_mbs * 8 ), 512) ) + 1
    buf = pyWrap.Buffer.CreateBuffer(bufsize)
    buf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, bufsize, opcode, commandName )

    """
   typedef PACKED struct _IGAT_Entry_t
   {
     uint16   VFCount;
     uint8    HotCount;
     uint8    BlockStatus; // IGAT_BlockStatus_e
     uint8    BlockType;   // BlockType_t
     uint8    RetireBlock;
     uint8    Reserved[2];
  } VIEWEREXPORTAS(IGAT_Entry_MIPChunk) IGAT_Entry_t;
  """

    IGATEntries = {}
    offset = 0x0
    for mb in range(0, num_mbs):
        VFCount = buf.GetTwoBytesToInt(offset) #
        HotCount = buf.GetOneByteToInt(offset + 0x2)
        BlockStatus = buf.GetOneByteToInt(offset + 0x3)
        BlockType = buf.GetOneByteToInt(offset + 0x4)
        RetireBlock = buf.GetOneByteToInt(offset + 0x5)
        Reserved = buf.GetTwoBytesToInt(offset + 0x6)

        offset += 0x8

        IGATEntries[mb] = [VFCount, HotCount, BlockStatus, BlockType, RetireBlock]

    return IGATEntries

# end of GetIGATEntryForAllMetablocks function
def GetOprRemDACs(vtfContainer, Operation, Die = 0):
    """
typedef enum S_TAG_REQ_READ_LEVEL_REMEMBERANCE

{

    E_DFD_HOST_READ   = 0 ,

    E_DFD_EPWR_VERIFY  = 1,

    E_DFD_SCATTER_READ = 2,

    E_DFD_MAX_READ_LEVEL_REM

}S_REQ_READ_LEVEL_REMEMBERANCE;
    DB = (struct _CDB_t *)(void *)pAppCmdData;

    """
    commandName = "Get The Remembered DAC values for Particular Operation and Die"
    opcode = 0xac
    buf = pyWrap.Buffer.CreateBuffer(1, 0xAA) 
    cdbData = [opcode,Die,Operation,0x0,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
    direction = READ_DATA
    buf = SendDiagnostic(vtfContainer, buf , cdbData , direction , DIAG_SECTORLENGTH, opcode, commandName)

    #Since the Coding Scheme is 2-3-2 in Felix Bics6 x3
    #For LP we have to sense at S1, S5
    #For MP we have to sense at S2, S4, S6
    #For UP we have to sense at S3, S7
    lp_dac = [buf.GetTwoBytesToInt(0), buf.GetTwoBytesToInt(8)]
    mp_dac = [buf.GetTwoBytesToInt(2), buf.GetTwoBytesToInt(6),  buf.GetTwoBytesToInt(10)]
    up_dac = [buf.GetTwoBytesToInt(4), buf.GetTwoBytesToInt(12)]



    return [lp_dac, mp_dac, up_dac]


def GetClosedMLCBlockList(vtfContainer):
    opcode = 0xc9
    subopcode = 102
    cdb = [opcode, subopcode,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0,0x00,0x00,0x00,0x00,0x00]
    buf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR*4)
    buf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR*4, opcode, "GetClosedMLCBlockList")
    #vtfContainer.GetLogger().Info("", buf.Dump())
    listOfClosedMLCs = []
    offset = 0
    while 1:
        block = buf.GetTwoBytesToInt(offset)
        offset += 2
        if block == 0xffff:
            break
        listOfClosedMLCs.append(block)   
    return listOfClosedMLCs

def GetRSQueueInfo(vtfContainer):
    opcode = 0xc9
    subopcode = 100
    cdb = [opcode, subopcode,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0,0x00,0x00,0x00,0x00,0x00]
    buf = pyWrap.Buffer.CreateBuffer(1)
    buf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, "GetRSQueueInfo")
    offset = 0
    blocksInRSQueue = []
    while 1:
        block = buf.GetTwoBytesToInt(offset)
        offset += 2
        priority = buf.GetTwoBytesToInt(offset)
        offset += 2
        if block == 0xffff and priority == 0xffff:
            break
        blocksInRSQueue.append([block, priority])
    return blocksInRSQueue

def GetCurrentReadCounter(vtfContainer):
    opcode = 0xc9
    subopcode = 101
    cdb = [opcode, subopcode,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0,0x00,0x00,0x00,0x00,0x00]
    buf = pyWrap.Buffer.CreateBuffer(1)
    buf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, "GetCurrentReadCounter")
    currentReadCounter = buf.GetOneByteToInt(0)
    return currentReadCounter 

def GetGCBitMapInfo(vtfContainer, option):
    #GC_Category_PostInit,
    #GC_Category_Read,
    #GC_Category_Write,
    #GC_Category_Idle,
    #GC_Category_ReadOnly,
    #GC_Category_Erase,
    #GC_Category_Last   
    import Utils
    opcode = 0xc9
    subopcode = 103  
    cdb = [opcode, subopcode,option,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
    buf = pyWrap.Buffer.CreateBuffer(1)
    buf = SendDiagnostic(vtfContainer, buf, cdb, READ_DATA, SINGLE_SECTOR, opcode, "GetGCBitMapInfo")
    GCBitMap = buf.GetFourBytesToInt(0)
    GCComponentList = Utils.GetGCComponentList(vtfContainer)
    GCBitMapInfo = {}
    SetComponents = []
    for component in GCComponentList:
        GCBitMapInfo[component] = 0

    startChecking = False
    SetBitCount = 0
    reversedBitMap = reversed(bin(GCBitMap))
    index = 0
    while 1:
        bit = next(reversedBitMap)
        if bit == '1':
            GCBitMapInfo[GCComponentList[index]] = 1
            SetBitCount += 1
            SetComponents.append(GCComponentList[index])
        else:
            GCBitMapInfo[GCComponentList[index]] = 0
        index += 1
        if bit == 'b':
            break
    return GCBitMap, SetBitCount, SetComponents, GCBitMapInfo

def ForceRSGC(vtfContainer, priority=1, urgent=0, numOfBlocks=0):
    """
    Diagnostic to trigger Force RS GC
    priority: 0/1
    urgent: 0/1/2 --> 0 for Normal, 1 for Gear2, 2 for Urgent
    numOfBlocks --> num of blocks to add to queue

    Note: The diag works in the following order:
    1. If numOfBlocks is passed, then it will check if so many closed QLC blocks are present. If yes, add so many blocks. If not, add max possible.
    2. If numOfBlocks is not passed, then it will check if urgent is non-zero.
       2a. If urgent is zero, then it will add 1 block to RS queue and with priority passed
       2b. If urgent is non-zero, then it will add File160 based number of blocks to queue (depending on Gear2 (1) or Urgent (2) being passed)
    """
    opcode    = 0xCA
    subOpcode = 72
    prio = priority

    cdbData = [opcode,subOpcode,prio,0x00,numOfBlocks,0x00,urgent,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]   

    direction = WRITE_DATA
    data_buf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    if numOfBlocks != 0:
        vtfContainer.GetLogger().Info("", "Issuing ForceRSGC() with %d blocks to be added to RS Queue"%numOfBlocks)
    else:
        if urgent == 0:
            vtfContainer.GetLogger().Info("", "Issuing ForceRSGC() and adding 1 block to RS queue with priority %d"%priority)
        else:
            if urgent == 1:
                vtfContainer.GetLogger().Info("", "Issuing ForceRSGC() with Gear2 flag set")
            elif urgent == 2:
                vtfContainer.GetLogger().Info("", "Issuing ForceRSGC() with Urgent flag set")
            else:
                raise TestError.TestFailError(vtfContainer.GetTestName(), "urgent arg value can be 0,1,2. Passed value is %d"%urgent)

    SendDiagnostic(vtfContainer, data_buf, cdbData, direction, DIAG_SECTORLENGTH, SET_MML_DATA, 
                   commandName="Force RS GC")     

    return

def SetDttTempToThrottle(vtfContainer, option = 1, temp=67):
    commandName = "Set DTT Temp to throttle"
    opcode = SET_MML_DATA
    subOpcode = 0x2C
    """
   option-1 - state overide
   option-2 -
   option-3 - throttle due to temp(X6-X1)
   """
    option1 = 0o3
    option = 00
    temp1= temp
    temp = 00

    setTempBuf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR,0)
    #setTempBuf.SetTwoBytes()
    #cdbData = [opcode,subOpcode,option,temp,0,0,0,0,0,0,0,0,0,0,0,0]
    cdbData = [opcode,subOpcode,option1,option,temp1,temp,0,0,0,0,0,0,0,0,0,0]
    #cdbData = [opcode,subOpcode,option,option1,temp,temp1,0,0,0,0,0,0,0,0,0,0]
    SendDiagnostic(vtfContainer, setTempBuf, cdbData, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)


def MMLSetPowerCycles(vtfContainer, newPCOffset):
    """
    [OPcode: 0xCA, subopcode: 71, <Pow_cycle_Lower_Byte>,<Pow_cycle_Higher_Byte>, 0,0...]
    """

    commandName = "Diag_MML_SetPowerCycles"
    opcode = 0xCA
    subOpcode = 71
    bankNum = 0

    data_buf = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    newPCLowByte = ByteUtil.LowByte(newPCOffset)
    newPCHighByte = ByteUtil.HighByte(newPCOffset)

    cdb = [opcode,subOpcode,newPCLowByte,newPCHighByte,0,0,
           0,0,
           0,0,0,0,
           0,0,0,0]

    SendDiagnostic(vtfContainer, data_buf, cdb, WRITE_DATA, 0, opcode, commandName)


    return

def GetFWDebugData(vtfContainer):
    opcode = SET_MML_DATA
    subopcode = 0x44
    cdb = [opcode, subopcode, 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0,0x00,0x00,0x00,0x00,0x00]
    buf = pyWrap.Buffer.CreateBuffer(1)
    SendDiagnostic(vtfContainer, buf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, "DumpFWDebugData")
    return

def DumpFWDebugDataSetpath(vtfContainer, path = "C:\tests\Logs\BIN"):
    opcode = SET_MML_DATA
    subopcode = 0x45
    cdb = [opcode, subopcode, 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0,0x00,0x00,0x00,0x00,0x00]
    path = os.path.join(os.path.dirname(vtfContainer.FrWorkExpansion.test_log_file_name), "BIN")
    if not os.path.exists(path):
        os.mkdir(path)
    buf = pyWrap.Buffer.CreateBuffer(1)
    hexPath = path.encode('utf-8').hex()
    index=0
    for byteIndex in range(0,len(hexPath),2):
        buf.SetByte(index,int(hexPath[byteIndex:byteIndex+2],16))
        index+=1

    SendDiagnostic(vtfContainer, buf, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, "DumpFWDebugData_Setpath")
    return

def EnableORDisableROMode(vtfContainer, ChangeToRoMode = 1):
    """
    Name: Move the Card to RO mode OR take out the card from RO mode
    Description: This diagnostic is used to take the card out of RO mode, set to 1 to send the card to RO mode.
    opcode = 0xCA
    SubOpcode = 0x36
    ChangeToRoMode = 1  ==> Move the Card to RO mode
    ChangeToRoMode = 0 ==> Card will come out from RO Mode
    """ 
    logger = vtfContainer.GetLogger()
    commandName = "EnableORDisableROMode"
    if ChangeToRoMode:
        logger.Info("", "Enabling the  RO Mode")
    else:
        logger.Info("", "Disabling the RO Mode")
    opcode = 0xCA
    subOpcode = 73
    cdb = [opcode,subOpcode, 0,0,
           0,0,0,0,
           0,0,0,0,
          0,0,0,0]

    #dataBuffer = Buffer.Buffer(SINGLE_SECTOR, 0)
    dataBuffer = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    dataBuffer.SetByte(0, ChangeToRoMode)
    dataBuffer = SendDiagnostic(vtfContainer, dataBuffer, cdb, WRITE_DATA, SINGLE_SECTOR, opcode, commandName)
    return True

def discardLatch(vtfContainer, fwConfig):

    opcode = 0xC9
    subopcode = 0x2B

    for MP in range(0,fwConfig.numberOfMetaPlane):
        cdb = [opcode, subopcode,MP,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0,0x00,0x00,0x00,0x00,0x00]
        buf = pyWrap.Buffer.CreateBuffer(1)
        SendDiagnostic(vtfContainer, buf, cdb, WRITE_DATA, 1, 0xC9, "DISCARD_LATCH")

    return

def GetParametersFromNAND(vtfContainer, NANDAddr):
    commandName = "GetParametersFromNAND for addr 0x%X"%NANDAddr
    opcode = 0xC7

    #cdb structure

    #struct _myCDB_t
    #{
    #uint8 opcode; // opcode: DIAG_GETSETNANDPARAMS:                                                          0x71
    #uint8 bankNum;                                                                                              0
    #uint8 chip;                                                                                                 0
    #uint8 die;                                                                                                  0
    #uint16 NANDAddress;                                                                                  NANDAddr
    #uint8 Data;                                                                                                 0
    #uint8 Mask;                                                                                                 0
    #uint8 option; // 1 = Set NAND Param Die; 2 = Set Param Bit Mask; If other value = Error                     0
    #uint8 subOption; // 1 = Trim; 2 = Set (Direct Value); If other value = Error                                0
    #uint8 OperationState; // 1 = Get Param Operation; 2 = Set Param Operation; If other value = Error           1
    #uint8 reserved2;                                                                                            0
    #uint32 reserved3;                                                                                           0
    #}

    #cbd = [opcode, bankNum, chip, die, NANDAddr, Data, Mask, option, subOption, OperationState, reserved2, reserved3]
    #cbd = [0x71,0,0,0,NANDAddr,0,0,0,0,1,0,0]

    if NANDAddr < 0x100:
        #[0x71,0,0,0,0x70(Address),0x00 (Above 0x100 Bit),0x40,0x0f,1,2,1(Read Param),0,0,0,0,0]
        cdb = [opcode,0,0,0,NANDAddr,0x00,0x40,0x0f,1,2,0,0,0,0,0,0]
        #cdb = [0x71,0,0,0,NANDAddr,0x00,0x40,0xff,1,2,1,0,0,0,0,0]
        NANDAddr -= 0x100
    else:
        cdb = [opcode,0,0,0,NANDAddr,0x01,0x40,0x0f,1,2,0,0,0,0,0,0]
        #cdb = [0x71,0,0,0,NANDAddr,0x01,0x40,0xff,1,2,1,0,0,0,0,0]

    buff = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    buff = SendDiagnostic(vtfContainer, buff, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    paramValue = buff.GetOneByteToInt(0)
    return paramValue


def GetSetFeature(vtfContainer, Addr):
    commandName = "GetSetFeature for addr 0x%X"%Addr
    opcode = 0xAB

    #cdb structure

    #struct _myCDB_t
    #{
    #uint8 opcode; //0th byte // opcode: 0xAB
    #uint8 bankNum; //1st byte // If required, remove it for single bank products.
    #uint8 chipNo; //2nd byte
    #uint8 dieNo; //3rd byte
    #uint16 featureAddr; //4th - 5th byte
    #uint8 cmdType; //6th byte // 1 = UNICAST Command; 2 = BROADCAST Comamnd; If other value = Error
    #uint8 subOption; //7th byte
    #uint8 operationState; //8th byte // 0 = GET_FEATURE_OP Operation; 1 = SET_FEATURE_OPOperation; If other value = Error
    #uint8 isTM; //9th byte
    #uint16 data; //10th - 11th byte
    #uint16 data1; //12th - 13th byte
    #uint16 reserved2; //14th - 15th byte                                                                                          0
    #}

    #cbd = [opcode, bankNum, chip, die, featureAddrByte1, featureAddrByte2, cmdType, subOption, subOption, isTM, reserved2, reserved3]
    #cbd = [0xAB,0,0,0,Addr_LSB,Addr_MSB,2,1,0,0,1,0,0,0,0,0]
    # For Get feature diag cdb = [opcode,0,0,0,NANDAddr,0,0x01,0,0,0x01,0,0,0,0,0,0]

    Addr_LSB = Addr & 0xFF
    Addr_MSB = Addr >> 8

    cdb = [opcode,0,0,0,Addr_LSB,Addr_MSB,1,0,0,1,0,0,0,0,0,0]

    buff = pyWrap.Buffer.CreateBuffer(SINGLE_SECTOR)
    buff = SendDiagnostic(vtfContainer, buff, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
    paramValue = buff.GetOneByteToInt(0)
    return paramValue
