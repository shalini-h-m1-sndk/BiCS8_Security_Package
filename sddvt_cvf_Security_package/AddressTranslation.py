"""
class AddressTranslation
Contains APIs related to address translation
@ Author: Shaheed Nehal - ported to CVF
@ copyright (C) 2021 Western Digital Corporation
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    pass # from builtins import *
    from builtins import object
from past.utils import old_div
import Utils as Utis
import DiagnosticLib as DiagLib
import random

class AddressTranslator(object):
    """
    AddressTranslation class for use with card.

    This class is for address translations among Logical, metablock, physical and diagnostic.

    Note:
       This is not to be used for translations of data in Re-Linked metablocks.

    Motivation:
       The intent of developing this class is to have all the possible address translations available together.
    """
    import AddressTypes as __AddressTypes
    def __init__(self, testSpace,fwConfigData):
        """
        Constructor

        Arguments:
           TestSpace          - The test space used for running the test

        Example:
           import AddressTranslation

           AddressTranslator = AddressTranslation.AddressTranslator( TestSpace=TestSpace)


        """
        #Get the items from the test space that we need for this test.
        self.__testSpace = testSpace
        #self.__card = self.__testSpace.GetCard()
        # Harish - Commenting card.Unlock for CTF 1.3.10 onwards
        #self.__card.Unlock()
        self.__logger = self.__testSpace.GetLogger()
        self.__fwConfigData = fwConfigData
        self.randomObj = random.Random(testSpace.cmd_line_args.randomSeed)

    # end of __init__()


    def GetPhysicalAddress(self,fwConfig,block,sectoroffset,isMlc=False):
        '''
        Calculate physical address of blocks based on metablock number and offset (for 1z, BiCS)
        '''
        #get the physical address of the metablock
        phyAddrList = self.__testSpace._livet.GetFirmwareInterface().GetPhysicalBlocksFromMetablockAddress(block, 0)
        objPhysicalAddress = self.__AddressTypes.PhysicalAddress()

        #for addr in phyAddrList:
           #self.__logger.Info("", "Physical address %s"%(list(addr)))

        #Calcaulte the ecc page level granuality
        eccPage = old_div(sectoroffset,fwConfig.sectorsPerEccPage)
        page = old_div(eccPage,fwConfig.eccPagesPerPage)
        phyAddrIndex = page%len(phyAddrList)

        objPhysicalAddress.bank     = 0
        objPhysicalAddress.chip     = phyAddrList[phyAddrIndex][0]
        objPhysicalAddress.die      = phyAddrList[phyAddrIndex][1]
        objPhysicalAddress.plane    = phyAddrList[phyAddrIndex][2]
        objPhysicalAddress.block    = phyAddrList[phyAddrIndex][3]

        #Calculate wordline based on the sectoroffset. Write Offset size in terms of LG Fragment
        if isMlc:
            metaPage = old_div(sectoroffset, fwConfig.sectorsPerMetaPage)
            wordline = old_div(metaPage, (fwConfig.stringsPerBlock * fwConfig.mlcLevel))
            string   = (old_div(metaPage, fwConfig.mlcLevel)) % fwConfig.stringsPerBlock
            objPhysicalAddress.mlcLevel = metaPage % fwConfig.mlcLevel
            objPhysicalAddress.isTrueBinaryBlock = False
        else:
            wordline = old_div(sectoroffset, (fwConfig.sectorsPerMetaPage * fwConfig.stringsPerBlock))
            string   = (old_div(sectoroffset,fwConfig.sectorsPerMetaPage))% fwConfig.stringsPerBlock
            objPhysicalAddress.mlcLevel       = 0
            objPhysicalAddress.isTrueBinaryBlock = True

        #Assign the calcaulated physical address to the return object
        objPhysicalAddress.wordLine          = wordline
        objPhysicalAddress.string            = string
        objPhysicalAddress.eccPage           = eccPage%fwConfig.eccPagesPerPage

        self.__logger.Info("", "Physical address for MB:0x%X and sector offset:0x%X: %s"%(block,sectoroffset,objPhysicalAddress))

        return objPhysicalAddress

    def GetPhyAddrFromMB(self,metaBlock,wordLine=None,mlcLevel=None,string=None,isSLC=True):
        """
        Description:
           * Gets the physical address
        """
        phyAddrList = self.__testSpace._livet.GetFirmwareInterface().GetPhysicalBlocksFromMetablockAddress(metaBlock, 0)
        phyAdd = self.randomObj.choice(phyAddrList)

        self.__phyAdd = self.__AddressTypes.PhysicalAddress()
        self.__phyAdd.chip = phyAdd[0]
        self.__phyAdd.die = phyAdd[1]
        self.__phyAdd.plane = phyAdd[2]
        self.__phyAdd.block = phyAdd[3]

        if mlcLevel == None:
            if isSLC:
                self.__phyAdd.mlcLevel = 0
            else:
                self.__phyAdd.mlcLevel = self.randomObj.randrange(0,self.__fwConfigData.mlcLevel)

        if wordLine == None:
            self.__phyAdd.wordLine = self.randomObj.randrange(1,self.__fwConfigData.wordLinesPerPhysicalBlock_BiCS)
        else:
            self.__phyAdd.wordLine = wordLine

        if string == None:
            self.__phyAdd.string = self.randomObj.randrange(0,self.__fwConfigData.stringsPerBlock)
        else:
            self.__phyAdd.string = string

        return self.__phyAdd


    def CalculatePhysicalBlock(self, physBlock, plane, Die):
        """
        Name : __CalculatePhysicalBlock()
        Description:    Calculates a physical block location based on specified block, plane and die.
                        This value will get sent to the low-level diagnostic commands.
                        This is a private function used by the class
        Inputs: Physical Block Number,Plane Number,Die
        Output: diagnostic Physical Block Number

        """
        planesPerDie = self.__fwConfigData.planesPerDie
        numPlaneBits = 0
        while planesPerDie > 1:
            planesPerDie = planesPerDie >> 1
            numPlaneBits+=1

        physBlockNum = physBlock << numPlaneBits
        physBlockNum = physBlockNum +  plane

        return physBlockNum
    # end of __CalculatePhysicalBlock()

    def TranslateLogicalToPhy(self, lba):
        """
        Name : TranslateLogicalToPhy()
        Description:Calculates the physical address of an lba
        Inputs:
           lba:   lba whose physical address is to be found
        Output:
           PhysicalAddress:   physical address instance
           The returned physical address follows wordline/mlclevel format
        """
        IsBiCS=0
        if self.__fwConfigData.isBiCS:
            IsBiCS=1

        physicalAddress = DiagLib.TranslateLogicalToPhy(self.__testSpace, lba,IsBiCS)[0]

        return physicalAddress
    # end of TranslateLogicalToPhy()


    def TranslateMetaToPhy(self, metaBlockAddress,isBinary=True):
        """
        Name : TranslateMetaToPhy()
        Description: Calculates the Physical address of the given MetaBlock Address
        Inputs: MetaBlockAddress
                Metablock address is an 8-digit Hex value of which the higher 4 digits denote the metablock number
                while the lower 4 digits denote the sector address
        Output:
           returns a physical address instance and the sector pesition in with in the ecc page

        """
        IsBiCS=0
        if self.__fwConfigData.isBiCS:
            IsBiCS=1

        physicalAddress, sectorPositionInEccPage = DiagLib.TranslateMetaToPhysical(self.__testSpace, metaBlockAddress, isBinary, self.__fwConfigData, IsBiCS)

        return physicalAddress,sectorPositionInEccPage
    # end of TranslateMetaToPhy()


    def GetMetaBlockNum(self,lba):
        """
        Name:                   GetMetaBlockNum
        Description:            Calculating the metablock number from the physical location
        Inputs:
            lba                 The Physical location of the Lba
        Outputs:
            metaBlockNum           The metablock number

        Note: This function is not fully complete. The upper bits of chip,die and plane are
        not included which calculating the metablock number. This function is applicable as of now
        as we dont have bigger chip numbers(greater than 3)
        """

        metaBlockNum = DiagLib.GetMetaBlockNum(self.__testSpace, lba)
        return metaBlockNum

    def TranslateMBNumtoMBA(self,mbnum):
        """
        Name:                   TranslateMBNumtoMBA
        Description:            Translate the metablock number to MetaBlock Address
        Inputs:
            mbnum                 metaBlockNum
        Outputs:
             MBA          The metablock Address

        """
        if DiagLib.IsLargeMetablockUsed(self.__testSpace)[0]:
            self.__logger.Info("", "[TranslateMBNumtoMBA]Checking if large MB(Anisha)")
            MBA = (mbnum << 32)
        else:
            MBA = (mbnum << 16)
        return MBA

    def TranslateLBAToMBA(self,lba):
        """
        Name:                   TranslateLBAToMBA
        Description:            Calculating the metablock address of an lba
        Inputs:
            lba                 logical block address

        Outputs:
            metablockAddress    The metablock address of lba
        """


        metaBlockAddress = DiagLib.TranslateLBAtoMBA(self.__testSpace, lba)
        return metaBlockAddress

#end of GetMetaBlockNum
# end of AddressTranslator()
