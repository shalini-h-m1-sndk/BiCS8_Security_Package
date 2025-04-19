"""
class FwConfig
Contains all Configuration parameters
@ Author: Shaheed Nehal - ported to CVF
@ copyright (C) 2021 Western Digital Corporation
"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

from builtins import str
from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    pass # from builtins import str
    from builtins import range
    pass # from builtins import *
    from builtins import object
from past.utils import old_div
import DiagnosticLib
import Core.ValidationError as ValidationError
import Utils as Utils
import SDCommandWrapper as SDWrap
import FileData as FileData

#Constants
BE_SPECIFIC_SECTORS_PER_RAW_ECC_PAGE = 0x5
BE_SPECIFIC_BYTES_PER_SECTOR = 0x200
BE_SPECIFIC_HEADER_SIZE_IN_BYTES = 0x20 #To recheck
FLASH_TYPE_MLC = 0x02
FLASH_TYPE_BINARY = 0x01
FLASH_TYPE_D3 = 0x80

#Checks if the used memory type is eD3
#Bit 0x40 currently marked as X4-bit
#(from be_rm_Config.h ) '''
#TODO: isED3 and isX4 are using the same bit
FLASH_TYPE_EX3 = 0x40
FEATURE_BIT_FLASHVISON_BICS = 0x40000000

ECC_FIELD_SIZE_BYTE_ONE = 0x50
ECC_FIELD_SIZE_BYTE_TWO = 0x62
ECC_FIELD_SIZE_BYTE_THREE = 0x92
ECC_FIELD_SIZE_BYTE_FOUR = 0xE6
ECC_FIELD_SIZE_LAMBEAU_BiCS3 = 0x1C0
#Max correctable bits
CORRECTABLE_ECC_LEVEL_ONE = 0x2A
CORRECTABLE_ECC_LEVEL_TWO = 0x34
CORRECTABLE_ECC_LEVEL_THREE = 0x4D
CORRECTABLE_ECC_LEVEL_FOUR = 0x7A
CORRECTABLE_ECC_LEVEL_LAMBEAU_BiCS3 = 0x28A #650

class FwConfig(object):
    def __init__(self, vtfContainer):
        """
        That object of this clss contais all the information related to Firmware that will not change till end of FW life (download)
        """
        #TODO: Ask Satya why these operations are being done. Is it necessary?
        logger = vtfContainer.logger

        #To recheck
        #cardInfo = card.GetCardInfo()
        #cardInfo.Update()

        self.SFSList = DiagnosticLib.CheckSFS(vtfContainer)
        self.SFSenabled = self.SFSList[0]
        # Configuration parameters
        configBuf = DiagnosticLib.ReadConfigurationParameters(vtfContainer)
        self.beCapacity = configBuf["beCapacityPerBank"]
        self.sectorsPerMetaBlock = configBuf["sectorsPerMetaBlock"]
        self.sectorsPerMetaPage = configBuf["sectorsPerMetaPage"]
        self.sectorsPerPage = configBuf["sectorsPerPage"]
        self.numOfBanks = configBuf["numOfBanks"]
        self.sectorsPerEccPage = configBuf["sectorsPerEccPage"]
        self.flashMode = configBuf["flashMode"]
        self.featureBits = configBuf["featureBits"]
        self.phyPagesPerMetaPage = configBuf["phyPagesPerMetaPage"]
        self.eccPagesPerPage = configBuf["eccPagesPerPage"]
        self.isSLCOnly = configBuf["slcmode"]
        self.numOfSlots = configBuf["NumberOfSlots_BiCS"]

        #Max LBA is number of blocks available to write
        #If its 256: Range is 0-255
        self.maxLba = SDWrap.WrapGetMaxLBA() - 1
        #self.maxLba = self.beCapacity * self.numOfBanks
        assert self.maxLba >= 0, "The max LBA of card is negative [Found : %d]"%self.maxLba

        self.bytesPerSector = BE_SPECIFIC_BYTES_PER_SECTOR # Since this diag is not functional hence hard coding configBuf["bytesPerSector"]


        self.metaPagesPerMetaBlock = old_div(self.sectorsPerMetaBlock, self.sectorsPerMetaPage)

        self.pagesPerMetaBlock = old_div(self.sectorsPerMetaBlock, self.sectorsPerPage)


        self.headerSizeInBytes = BE_SPECIFIC_HEADER_SIZE_IN_BYTES
        self.eccPagesPerMlcPage    = old_div(self.sectorsPerPage, self.sectorsPerEccPage)
        #TODO : What is the difference and is it needed?
        self.BEMaxLba = self.beCapacity * self.numOfBanks
        self.sectorsPerMegaBlock =  self.sectorsPerMetaBlock * self.numOfBanks

        #TODO : should it be isMLC
        self.isMlc     = self.__CheckFlashMode(FLASH_TYPE_MLC)
        self.isBinary  = self.__CheckFlashMode(FLASH_TYPE_BINARY)
        self.isD3      = self.__CheckFlashMode(FLASH_TYPE_D3)
        self.isEx3     = self.__CheckFlashMode(FLASH_TYPE_EX3)  #This is same as X4 memory
        self.isBiCS = self.__CheckFeatureBits(FEATURE_BIT_FLASHVISON_BICS)

        #Parameters for true binary blocks
        self.pagesPerMetaBlockInTrueBinaryMode = old_div(self.pagesPerMetaBlock, self.__GetMlcLevel())
        self.sectorsPerMetaBlockInTrueBinaryMode = self.pagesPerMetaBlockInTrueBinaryMode * self.sectorsPerPage
        self.metaPagesPerMetaBlockInTrueBinaryMode = old_div(self.sectorsPerMetaBlockInTrueBinaryMode, self.sectorsPerMetaPage)

        #Firmware Parameters

        self.pagesPerMlcBlock = configBuf["pagesPerMlcBlock"]#Pages Per MLC block is equal to pages per physical block
        self.numOfLgsInMedia = configBuf["numberOfLgInMedia"]
        self.firstUpperpageAddr = configBuf["firstUpperPageAddress"]
        self.totalMetaBlocksInCard = configBuf["totalMetaBlocksPerBank"]


        self.planesPerChip = configBuf["planesPerChp"]
        self.diesPerChip = configBuf["diesPerPhysChip"]
        self.blocksPerDie = configBuf["blocksPerDie"]
        self.numChips = configBuf["numPhysChip"]
        self.chipMaxPBlock = configBuf["chipMaxPBlock"]
        #TODO: have to check why do planesper die is same asplanes per chip
        self.planesPerDie = configBuf["planesPerChp"] #PlanesPerChip actually means planesPerLogicalChip
        self.planesPerChip = self.planesPerDie *self.diesPerChip
        self.blocksPerPlane = old_div(self.blocksPerDie,self.planesPerDie)
        self.log2BlockPerPlane = configBuf["log2BlockPerPlane"]
        self.log2BlockPerDie = configBuf["log2BlockPerDie"]
        self.eccFieldSizeByte = configBuf["eccFieldSizeByte"]
        self.eccFieldSize, self.correctableEccLevel = self.__GetEccDetails()
        self.physChipInterleave = configBuf["physChipInterleave"]
        self.dieInterleave = configBuf["dieInterleave"]
        self.planeInterleave = configBuf["planeInterleave"]
        self.pageInterleave = configBuf["pageInterleave"]
        self.log2DiesPerChip = configBuf["log2DiesPerPhysChip"]

        self.totalNumPhysicalBlocks = self.blocksPerDie * self.diesPerChip * self.numChips

        #Get WordlinesPerPhysicalBlock &stringsPerBlk for BiCS from config Params Diag
        self.wordLinesPerPhysicalBlock_BiCS = configBuf["WordlinesPerBlock_BiCS"]
        assert self.wordLinesPerPhysicalBlock_BiCS!=0 ,"wordLinesPerPhysicalBlock_BiCS cannot be 0"

        self.stringsPerBlock = configBuf["StringsPerBlock"]

        configBuf = DiagnosticLib.GetFreeBlockCount(vtfContainer)
        self.freeSlcBlockCount = configBuf["freeSlcBlockCount"]

        #Binary cache parameters
        configBuf = DiagnosticLib.ReadMmlParameters(vtfContainer)

        #To recheck - Hardcoding this to true since its dual write by default always (Need to review the API __isDWEnabled() if there is no Dual Write in future)
        self.isDualWriteEnabled = True #self.__isDWEnabled(configParams=configBuf, TypeOfPattern="sequential")
        self.numberOfMetaPlane =  configBuf['numMetaPlanesInSystem']

        #To recheck: This has to be reviewed
        #6D configuration
        self.dummyMetaPlane = 0

        if vtfContainer.cmd_line_args.numberOfDiesInCard == 6 or vtfContainer.cmd_line_args.numberOfDiesInCard == 12:
            self.numberOfMetaPlane = 4
            self.dummyMetaPlane = 1

        #check if multi meta plane is enabled
        if (self.numberOfMetaPlane > 1):
            self.MMP = 1
        else :
            self.MMP = 0



        self.sectorsPerLg = configBuf["lgSize"]


        #configBuf["DummyFillEnd"]-configBuf["DummyFillStart"] returns the Number of Fragments in EX3

        #To be recheck -
        self.slcMBSize = configBuf["slcMbsize"]-((configBuf["DummyFillEnd"]-configBuf["DummyFillStart"])*configBuf["sectorsPerLgFragment"])


        self.mlcMBSize = configBuf["mlcMbSize"]
        self.numOfLgsPerSlcBlk = configBuf["lgsPerSlcBlock"]
        self.numOfLgsPerMlcBlk = configBuf["lgsPerMlcBlock"]


        self.lgFragmentSize = configBuf["sectorsPerLgFragment"]


        self.fragmentsPerMetaPage = configBuf["fragmentsPerMetaPage"]
        self.metaPageSize = self.fragmentsPerMetaPage * self.lgFragmentSize
        self.pageSize = configBuf["pageSize"]
        self.numSeqStreams = configBuf["numSeqStreams"]


        self.sectorsPerLgFragment = configBuf["sectorsPerLgFragment"]


        self.dummyFillStart = configBuf["DummyFillStart"]
        self.dummyFillEnd = configBuf["DummyFillEnd"]
        self.foldingThreshold = configBuf["foregroundFoldingLgThreshold"]
        self.metaPagesInSafeMargin = configBuf["numofMpInSafeMargin"]
        self.dedicatedMIP = configBuf["MIP_IsDedicatedBlock"]

        if(self.sectorsPerLg):
            self.lgsInCard = old_div(self.maxLba,self.sectorsPerLg)
        else:
            self.lgsInCard = self.maxLba

        self.mlcLevel = self.__GetMlcLevel()
        self.pagesPerSlcBlock = old_div(self.pagesPerMlcBlock,self.mlcLevel) #configBuf["pagesPerSlcBlock"] - This is not 0 now.
        if self.isSLCOnly:
            self.mlcLevel=1

        self.sectorsPerMlcBlock = self.pagesPerMlcBlock * self.sectorsPerPage
        self.sectorsPerSlcBlock = self.pagesPerSlcBlock * self.sectorsPerPage
        self.sectorsPerRawEccPage = BE_SPECIFIC_SECTORS_PER_RAW_ECC_PAGE # number of sectors
        self.eccPagesPerMlcBlock  = old_div(self.sectorsPerMlcBlock, self.sectorsPerEccPage)
        self.eccPagesPerSlcBlock  = old_div(self.sectorsPerSlcBlock, self.sectorsPerEccPage)
        self.sectorsPerRawMlcPage  = self.eccPagesPerMlcPage * self.sectorsPerRawEccPage
        self.sectorsPerRawSlcPage  = self.eccPagesPerSlcBlock * self.sectorsPerRawEccPage
        self.bytesPerRawEccPage = self.sectorsPerRawEccPage * self.bytesPerSector
        self.bytesPerRawMlcPage = self.eccPagesPerMlcBlock * self.bytesPerRawEccPage
        self.bytesPerRawSlcPage = self.eccPagesPerSlcBlock * self.bytesPerRawEccPage
        self.bytesPerRawPhysicalPage = self.eccPagesPerMlcPage * self.bytesPerRawEccPage
        self.sectorsPerMlcMetaBlock = self.pagesPerMlcBlock * self.sectorsPerPage * self.physChipInterleave * self.dieInterleave * self.planeInterleave
        self.sectorsPerSlcMetaBlock = self.pagesPerSlcBlock * self.sectorsPerPage * self.physChipInterleave * self.dieInterleave * self.planeInterleave

        #To recheck - ECC page size calculation should be done from the flashPageFormat
        if vtfContainer.isModel:
            self.columnsPerRawEccPage = self.__GetRawECCPageSizeFromFlashPageFormat(vtfContainer) #self.headerSizeInBytes+(self.bytesPerSector*self.sectorsPerEccPage)+self.eccFieldSize

        self.gatDeltaThresholdLevel = configBuf["gatDeltaThresholdLevel"]
        self.gatDirDeltaThresholdLevel = configBuf["gatDirDeltaThresholdLevel"]
        self.igatDeltaThresholdLevel = configBuf["igatDeltaThresholdLevel"]
        self.rgatDeltaThresholdLevel = configBuf["RGATDeltaThresholdLevel"]
        self.rgatDirDeltaThresholdLevel = configBuf["RGATDirDeltaThresholdLevel"]
        self.timeStampThresholdLevel = configBuf["timeStampThresholdLevel"]
        self.omwGatDeltaMargin = configBuf["OMWGatDeltaMargin"]
        self.omwTSMargin = configBuf["OMWTSMargin"]
        self.omwBalGCThresholdFrags = configBuf["OMWBalGCThresholdFrags"]
        #self.lastSLCRelinkedMB = configBuf["lastSLCRelinkedMB"]
        #self.lastMLCRelinkedMB = configBuf["lastMLCRelinkedMB"]
        #self.InvalidMB = 0x1FFF
        #if vtfContainer.cmd_line_args.numberOfDiesInCard == 16:
        self.InvalidMB = 0x3FFF

        return

    def __GetMlcLevel(self):
        if self.isBinary:
            mlcLevel = 1
        elif self.isMlc:
            mlcLevel = 2
        elif self.isD3:
            mlcLevel = 3
        else:
            raise
        return mlcLevel
        # End of GetMlcLevel

    def __CheckFlashMode(self, FLASH_TYPE):
        if(self.flashMode & FLASH_TYPE):
            return (1) #Return True
        else:
            return(0) #Returns False


    def __CheckFeatureBits(self, FEATURE_TYPE):

        if(self.featureBits & FEATURE_TYPE):
            return(1) #Return True
        else:
            return(0) #Return False

    def __GetEccDetails(self):
        eccFieldSize = self.eccFieldSizeByte
        if eccFieldSize == ECC_FIELD_SIZE_BYTE_ONE:
            correctableEccLevel = CORRECTABLE_ECC_LEVEL_ONE
        elif eccFieldSize == ECC_FIELD_SIZE_BYTE_TWO:
            correctableEccLevel = CORRECTABLE_ECC_LEVEL_TWO
        elif eccFieldSize == ECC_FIELD_SIZE_BYTE_THREE:
            correctableEccLevel = CORRECTABLE_ECC_LEVEL_THREE
        elif eccFieldSize == ECC_FIELD_SIZE_BYTE_FOUR:
            correctableEccLevel = CORRECTABLE_ECC_LEVEL_FOUR
        elif eccFieldSize == ECC_FIELD_SIZE_LAMBEAU_BiCS3:
            correctableEccLevel =  CORRECTABLE_ECC_LEVEL_LAMBEAU_BiCS3
        else:
            #Harish 29Sep2017 - Lambeau CC default set to level Four / need to raise a JIRA
            correctableEccLevel = CORRECTABLE_ECC_LEVEL_FOUR
            #raise

        return eccFieldSize, correctableEccLevel
    # end of __GetEccDetails

    def GetStartLbaSectorsPerLgFromLgNum(self, lg):
        """
        Name:          GetStartLbaSectorsPerLgFromLgNum()
        Description:   Gets Start LBA & Sectors Per LG of the LG that is passed
        Arguments:     lg : lg number
        Returns:       Start LBA & Sectors Per LG of that LG
        """
        assert (lg < self.lgsInCard), "LG %d is invalid" %lg
        startLba = lg*self.sectorsPerLg
        if lg < (self.lgsInCard-1):
            sectorsPerLG = self.sectorsPerLg
        else:
            sectorsPerLG = self.maxLba%self.sectorsPerLg

        return startLba, sectorsPerLG
    # end of GetStartLbaSectorsPerLgFromLgNum()


    def __isDWEnabled(self, configParams, TypeOfPattern):
        NumOfSeqStreams       = configParams["numSeqStreams"]
        NumOfRandStreams      = configParams["numRandomStreams"]
        NumofRelocationStream = configParams["numRelocationStreams"]
        DWEnabld=False
        TypeOfPattern=TypeOfPattern.lower()
        if TypeOfPattern=="sequential":
            for i in range(0,NumOfSeqStreams):
                #To recheck - this returns a buffer (indexing on buffers is not valid)
                if configParams["DualWriteSeqStream"][i]==1:
                    DWEnabld=True
                else:
                    DWEnabld=False
        elif TypeOfPattern=="random":
            for i in range(0,NumOfRandStreams):
                if configParams["DualWriteSLCRandStream"][i]==1:
                    DWEnabld=True
                else:
                    DWEnabld=False
        elif TypeOfPattern=="mlcrandomStream":
            if configParams["DualWriteMLCRandStream"]==1:
                DWEnabld==True

        return DWEnabld

    def __GetRawECCPageSizeFromFlashPageFormat(self, vtfContainer):
        '''
        Description: Parses the flashPageFormat to get the raw eccPage size
        Author: Shaheed Nehal
        Example: [[D512]2H8E128[D512]2H8E128[D512]2H8E128[D512]2H3S2C3E128] ==> 512*2 + 8 + 128 + 512*2 + 8 + 128 + 512*2 + 8 + 128 + 512*2 + 3 + 2 + 3 + 128
        '''
        import ValidationSpace
        validationSpace = ValidationSpace.ValidationSpace(vtfContainer)

        #For X4 (in Felix), we have 2 flashPageFormats ('flashPageFormat0' X3 for P0/P1 Boot writes, 'flashPageFormat1' X4 for others) Hence using flashPageFormat1
        if "flashPageFormat1" in list(validationSpace.configParser.GetIniDict().keys()):
            flashPageFormatOriginal = str(validationSpace.configParser.GetValue("flashPageFormat1", "")[0])
        elif "controller.flash_page_format_1" in list(validationSpace.configParser.GetIniDict().keys()):
            flashPageFormatOriginal = str(validationSpace.configParser.GetValue("controller.flash_page_format_1", "")[0])
        else:
            flashPageFormatOriginal = str(validationSpace.configParser.GetValue("flashPageFormat", "")[0])
        vtfContainer.GetLogger().Info("", "[FwConfig: __GetRawECCPageSizeFromFlashPageFormat()] FlashPageFormat - %s"%flashPageFormatOriginal)
        flashPageFormat = flashPageFormatOriginal.replace(' ', '') #Remove white spaces
        stack = []
        index = 0
        currentOpenBracket = None
        eccPageSize = 0
        while (index < len(flashPageFormat)):
            if flashPageFormat[index] in ['[', '(']:
                BytesPerSector = ""
                currentOpenBracket = flashPageFormat[index]
                #Parsing the total bytes in 1 sector times no of sectors in the eccpage
                while flashPageFormat[index] not in [']', ')']:
                    stack.append(flashPageFormat[index])
                    index += 1

                if currentOpenBracket == '[':
                    if flashPageFormat[index] != ']':
                        raise ValidationError.TestFailError(vtfContainer.GetTestName(), "flashPageFormat is incorrect - %s"%flashPageFormatOriginal)

                    while (stack[-1] != '['):
                        if len(stack) == 0:
                            raise ValidationError.TestFailError(vtfContainer.GetTestName(), "flashPageFormat is incorrect - %s"%flashPageFormatOriginal)

                        stackTop = stack.pop(-1)
                        if stackTop.isdigit():
                            BytesPerSector += stackTop

                    BytesPerSector = int(BytesPerSector[::-1])
                    vtfContainer.GetLogger().Info("", "[FwConfig: __GetRawECCPageSizeFromFlashPageFormat()] Bytes per sector: %dB"%BytesPerSector)

            elif flashPageFormat[index] in [']', ')']:
                stackTop = stack.pop(-1)
                if flashPageFormat[index] == ']':
                    if stackTop != '[':
                        raise ValidationError.TestFailError(vtfContainer.GetTestName(), "flashPageFormat is incorrect - %s"%flashPageFormatOriginal)
                    index += 1
                    #If we still have flashPageFormat to parse, then it means the next number has to be multiplied with eccPageSize
                    if len(stack) != 0:
                        eccPageSize += BytesPerSector * int(flashPageFormat[index])
                        index += 1
                        vtfContainer.GetLogger().Info("", "[FwConfig: __GetRawECCPageSizeFromFlashPageFormat()] ECCPageSize: %dB"%eccPageSize)

            elif flashPageFormat[index].isalpha():
                BytesPerSector = ""
                index+=1
                bytesToAdd = ""
                while(flashPageFormat[index].isdigit()):
                    bytesToAdd += flashPageFormat[index]
                    index += 1
                eccPageSize += int(bytesToAdd)
                vtfContainer.GetLogger().Info("", "[FwConfig: __GetRawECCPageSizeFromFlashPageFormat()] ECCPageSize: %dB"%eccPageSize)

            else:
                BytesPerSector = ""
                index += 1

        if stack != []:
            raise ValidationError.TestFailError(vtfContainer.GetTestName(), "Something went wrong while parsing flashPageFormat for ECCPageSize")

        #This is an additional check to see if the parsing was fine or not
        eccPageSizeFromFW = old_div(self.sectorsPerPage,self.eccPagesPerPage) * 512 #Can be either 2k or 4k bytes

        if eccPageSizeFromFW not in [2048, 4096]:
            raise ValidationError.TestFailError(vtfContainer,GetTestName(), "eccPageSize is not 2K or 4K, it is %dB"%eccPageSizeFromFW)

        #LMB had 4K Eccpage (X3=4576, X4=4640), but Felix has 2K Eccpage (X3=2292, X4=2372)
        if (eccPageSizeFromFW == 2048 and eccPageSize not in [2292, 2372]) or (eccPageSizeFromFW == 4096 and eccPageSize not in [4576, 4640]):
            raise ValidationError.TestFailError(vtfContainer,GetTestName(), "eccPageSize is not 2K (Parsed value - %dB). Check the flashPageFormat parsing"%eccPageSize)

        return eccPageSize


class FwFeatureConfig(object):

    def __init__(self, vtfContainer):
        self.logger = vtfContainer.GetLogger()
        self.isSpcbEnabled = None
        self.isSpcbBootFsEnabled = None
        self.isSpcbBadBlockMmpCompensationEnabled = None
        self.isSlcPfDisabled = None
        self.isMlcPfDisabled = None

        # Initialize Feature Specific Flags
        self.InitializeProductFeatureFlags()

        return

    def GetProductFeatures(self):
        # Intitialize everything to 'False' by default
        enabledFeatureDictionary = {
           'spcbbadblockmmpcompensation' : False,
           'slcpfdisable' : False,
           'mlcpfdisable' : False,
           'spcb' : False,
           'spcbBootFs' : False
        }
        # Number of dies
        numberOfDies = Utils.numberOfDiesInTheCard

        # Set features to 'True' if it is applicable to current project
        if numberOfDies in [1,2,4,6,8,12,16]:
            enabledFeatureDictionary['slcpfdisable'] = True
            enabledFeatureDictionary['spcbbadblockmmpcompensation'] = True
            enabledFeatureDictionary['spcb'] = True if numberOfDies in [1,2,4,6] else False
            enabledFeatureDictionary['spcbBootFs'] = True

        return enabledFeatureDictionary

    def InitializeProductFeatureFlags(self):
        t_featureDictionary = self.GetProductFeatures()
        self.isSpcbEnabled = t_featureDictionary['spcb']
        self.isSpcbBootFsEnabled = t_featureDictionary['spcbBootFs']
        self.isSpcbBadBlockMmpCompensationEnabled = t_featureDictionary['spcbbadblockmmpcompensation']
        self.isSlcPfDisabled = t_featureDictionary['slcpfdisable']
        self.isMlcPfDisabled = t_featureDictionary['mlcpfdisable']

        self.logger.Info("", "SPCB Enabled - %s"%self.isSpcbEnabled)
        self.logger.Info("", "SPCB on BOOT/FS Enabled - %s"%self.isSpcbBootFsEnabled)
        self.logger.Info("", "SLC PF Disabled - %s"%self.isSlcPfDisabled)
        self.logger.Info("", "MLC PF Disabled - %s"%self.isMlcPfDisabled)
        self.logger.Info("", "SPCB BadBlock MMP Compensation Enabled - %s"%self.isSpcbBadBlockMmpCompensationEnabled)

        return True
