"""
class BadBlockLib
Contains APIs related to Badblock injection
@ Author: Shaheed Nehal - ported to CVF
@ copyright (C) 2021 Western Digital Corporation
"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
#First 128 physical blocks in Chip 0 are considered as ROM_VISIBLE_BLOCKS
from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    from builtins import map
    pass # from builtins import str
    from builtins import range
    pass # from builtins import *
    from builtins import object
from past.utils import old_div
ROM_VISIBLE_BLOCKS = 128
BOOT_BLOCKS = 2
FS_BLOCKS = 4

#importing the Validation library
import ValidationSpace
import AddressTypes
import random
import Extensions.CVFImports as pyWrap
import Utils
import Core.ValidationError as TestError
import FileData
import FwConfig
import copy
import math
import Constants
import DiagnosticLib
from bisect import bisect

g_Bad_block_Config_file_name = None

class BadBlockValidation(object):

    DieListForEIinSingleMP = [] # listof Die which belong to the MP where error needs to be injected
    def __init__(self, vtfContainer, isReducedCap=False):
        """
        Constructor
        """
        self.__validationSpace  = ValidationSpace.ValidationSpace(vtfContainer)
        self.vtfContainer       = vtfContainer
        self.__fwConfigData     = None
        #self.__sdfsObj         = None
        self.__addrTranslateObj = None

        #Initialise all the variables
        self.__InitialiseVariables()

        self.__optionValues     = self.__validationSpace.GetOptionValues()
        self.__randomObj        = random.Random(self.vtfContainer.cmd_line_args.randomSeed)

        self.__FileDataObj  = FileData.ConfigurationFile21Data(self.vtfContainer)
        maxBadBlockCount    = self.__FileDataObj.maxBadBlockCount # FILE_21 offset = 0x50
        self.__file14Object = FileData.GetFile14Data(self.vtfContainer)
        self.__numGATBlocks = self.__file14Object['numOfGATBlocks']
        self.logger = self.vtfContainer.GetLogger()
        self.logger.Info("","Max bad block allowed per plane configured in File 21 (2byte value at offset 0x50) is: %d"%(maxBadBlockCount))
        self.__dedicatedFBLBlocks = self.__file14Object['numOfBlocksDedicatedFBL']
        self.__NoOfGoodBlocksinROMVisible = BOOT_BLOCKS + FS_BLOCKS + self.__dedicatedFBLBlocks
        self.isReducedCap = isReducedCap
    #end of __init__

    def __InitialiseVariables(self):
        """
        Name: __InitialiseVariables()
        Description:    This Funcion all the variables that depends on testSpace. This function should be called when there is download happens.

        Arguments:
                None
        Returns :
                 None
        """
        self.vtfContainer          = self.__validationSpace.GetvtfContainer()
        self.__fwConfigData       = self.__validationSpace.GetFWConfigData()
        #self.__sdfsObj            = self.__validationSpace.GetSDFSObj()
        self.__addrTranslateObj   = self.__validationSpace.GetAddressTranslationObj()
        self.__livet = self.vtfContainer._livet

    #end __InitialiseVariables



    def MarkBadBlocks(self,
                      badBlockList,
                      botFilename = '',
                      paramsfilepath = None,
                      trimfile  = None,
                      maxLba=0,
                      useExistingCardMap = False,
                      disableBlockRelinkVerification=False):
        """
        Name: MarkBadBlock()
        Description:    This Funcion Marks a list of blocks as a factory failed block.
                        If it is already a Factory Failed bad block, it ignores that block and marks the rest and
                        returns status as Fail.

        Arguments:
           testSpace   :  TestSpace
           badBlockList:  List of Physical Address of the block which needs to be made BAD.
                          The Page and the EccPage parameters in the PhysicalAdd object are ignored.
           botFilename :  Bot file PATH
           paramsfilepath : parameter file path
           maxLba      :  Max LBA to Format
        Returns        :
                 None
        """
        #check  bot file path given
        global g_Bad_block_Config_file_name

        Utils.g_factoryMarkedBadBlockList = []
        for phyBlock in badBlockList:
            Utils.g_factoryMarkedBadBlockList.append ((phyBlock.chip, phyBlock.die, phyBlock.plane, phyBlock.block))

        moduleName = "MarkBadBlock "
        fileName = None

        #if Protocol is not model
        if not self.vtfContainer.isModel == True:
            badBlockBuf =  pyWrap.Buffer.CreateBuffer(2,0xFF)
            optionFlag = 0
            offset = 0

            for phyAddress in badBlockList:
                badBlockBuf[offset] = (phyAddress.chip<<4)|optionFlag
                badBlockBuf[offset+1] = (phyAddress.plane<<4)|phyAddress.die
                badBlockBuf.SetTwoBytes(offset+2,phyAddress.block)
                self.logger.Info(""," [%s] BadBlock to mark: chip=0x%X, die=0x%X, plane=0x%X, phy Block = 0x%X" \
                            %(moduleName,phyAddress.chip, phyAddress.die, phyAddress.plane, phyAddress.block))
                offset = offset + 4

            fileName="BadBlockEntryFile.bin"
            fptr = open(fileName, 'wb')
            mystrList = badBlockBuf.GetData(0, len(badBlockBuf))
            mystr = ''.join(map(chr,mystrList))
            fptr.write(mystr)
            fptr.close()

        #if Protocol is model
        else:

            import os
            FW_VALIDATION_PATH= os.getenv('FVTPATH')
            pid = os.getpid()
            rand_No = self.__randomObj.randint(1,573279)
            create_dir = FW_VALIDATION_PATH+ "\\Tests\\BadBlockConfigFiles"
            try:
                if not os.path.exists(create_dir):
                    os.makedirs(create_dir)
                    self.logger.Info("","Directory '%s' created successfully" % create_dir)
            except OSError as error:
                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Directory '%s' can not be created" % create_dir)

            fileName = create_dir + "\\BadBlockConfigFile" + str(pid+rand_No) + ".configtxt"
            g_Bad_block_Config_file_name = fileName

            self.logger.Info("","The Bad Block Config File created is: %s" %(fileName))

            fptr = open(fileName, 'w')
            SELECT_PLANE_STR     = '$select_plane'
            SELECT_BAD_BLOCK_STR = '$bad_block '

            if badBlockList != None:
                self.logger.Info("","[%s] Total Bad Blocks to mark : %d"%(moduleName, len(badBlockList)))

                for phyAddress in badBlockList:
                    #select the plane
                    curString = SELECT_PLANE_STR + '  %d'%phyAddress.chip + '  %d'%phyAddress.die + '  %d'%phyAddress.plane + ' \n'
                    fptr.write(curString)

                    curString = SELECT_BAD_BLOCK_STR + '  %d'%phyAddress.block+ ' \n'
                    fptr.write(curString)

                    self.logger.Info("","[%s] BadBlock to mark: chip=0x%X, die=0x%X, plane=0x%X, phy Block = 0x%X" \
                                %(moduleName, phyAddress.chip, phyAddress.die, phyAddress.plane, phyAddress.block))
                #End of for loop

            FW_VALIDATION_PATH= os.getenv('FVTPATH')
            configParser = self.vtfContainer.device_session.GetConfigInfo()
            FilePath = ""
            retTuple = configParser.GetValue("deviceConfigFile", FilePath)
            FilePath = retTuple[0]

            fptr2  = open(FilePath, 'r')
            for line in fptr2.readlines():
                fptr.write(line)

            fptr.close()
            fptr2.close()
            #end of check for
        #end of check if not model types

        self.logger.BigBanner("Performing ReInit() With Bad Blocks Injected\nBB injected DCF - %s)"%fileName)
        self.vtfContainer.device_session.GetConfigInfo().SetValue("device_configuration_file",fileName)
        try:
            self.vtfContainer.device_session.ReInit("protocol")
            import Production_SD
            self.obj = Production_SD.ModelProduction(self.vtfContainer.device_session)
            self.obj.Execute()            
        except:
            #self.ProductionError = True
            #self.vtfContainer.device_session.GetErrorManager().ClearAllErrors()
            raise TestError.TestFailError(self.vtfContainer.GetTestName(), "In Bad Block Injection Lib", "INIT UNSUCCESSFUL!!")
        #Initialise all the variables
        self.__InitialiseVariables()

        #Attaching new Livet handle as ReInit() destroys previous handle
        self.vtfContainer._livet.Attach(self.vtfContainer.device_session.GetModelDllHandle())
        self.__livet = self.vtfContainer._livet

        # To set the FW stats dump on model only
        if self.vtfContainer.isModel:
            DiagnosticLib.DumpFWDebugDataSetpath(self.vtfContainer)

        #To recheck: Need diag for this to know the good blocks (with zone based BB in redcap, there will be holes in between --> fetching phyblocks of nonexistant metablocks throws error)
        if self.isReducedCap:
            disableBlockRelinkVerification = True

        if disableBlockRelinkVerification == False:
            #pass
            validSlcMetaBlockNumbers,  validMlcMetaBlockNumbers = Utils.VerifyBlockRelinkAndGetAllValidMetaBlockList(self.vtfContainer)
        else:
            validSlcMetaBlockNumbers = [0]
            validMlcMetaBlockNumbers = [0]

        regEventKey = self.__livet.RegisterFirmwareWaypoint("BE_HEAP_USAGE", None)
        assert regEventKey > 0, "BE_HEAP_USAGE waypoint is not registered"
        self.logger.Info("", "Waypoint for the event BE_HEAP_USAGE has been registered successfully (Reg event key value = %d)"%(regEventKey))

        return
    #end of MarkBadBlocks

    def MarkRandomBadBlocksIncludingROMVisibleAndSPCBs(self,badBlockCount = None,
                                                       botFilename = '',
                                                       paramsfilepath = None,
                                                       maxLba=0):
            #Get Physical information of card
        numOfChips      = self.__fwConfigData.numChips * self.__fwConfigData.numOfBanks
        diesPerChip     = self.__fwConfigData.diesPerChip
        planesPerDie    = self.__fwConfigData.planesPerDie
        blocksPerPlane  = self.__fwConfigData.blocksPerPlane
        totalPlane = old_div(self.__NoOfGoodBlocksinROMVisible,(self.__fwConfigData.planesPerChip*1.0))
        additionBadBlockLimit = int(math.ceil(totalPlane))

        numberOfMetaPlane = self.__fwConfigData.numberOfMetaPlane
        maxBadBlockImbalanceList = []
        MaxBadBlocksWithImbalance = badBlockCount + self.__numGATBlocks + additionBadBlockLimit
        MinBadBlocksWithImbalance = badBlockCount - self.__numGATBlocks - additionBadBlockLimit
        planesWithMoreThanMaxBBs = self.__randomObj.sample(list(range(self.__fwConfigData.planeInterleave)), 2)
        for plane in range(self.__fwConfigData.planeInterleave):
            if plane not in planesWithMoreThanMaxBBs:
                maxBadBlockImbalanceList.append(MinBadBlocksWithImbalance)
            else:
                maxBadBlockImbalanceList.append(MaxBadBlocksWithImbalance)

        maxBadBlockImbalanceInPlane = badBlockCount + self.__numGATBlocks + additionBadBlockLimit

        fwFeatureConfig = FwConfig.FwFeatureConfig(self.vtfContainer) #Since testspace is not required

        #This is just a workaround till FW diag is changed to give right value
        if self.__optionValues.numberOfDiesInCard == 6 or self.__optionValues.numberOfDiesInCard == 12:
            numberOfMetaPlane = 3

        """
        if numberOfMetaPlane > 1 and fwFeatureConfig.isSpcbBadBlockMmpCompensationEnabled:
           SPBadBlockPatternList = ["DIE_MAX_ONEPLANE","DIE_MAX_BAD_BLOCKS","DIE_MAX_IMBALANCE","DIE_RANDOM_IMBALANCE","DIE_LESS_BAD_BLOCKS","META_BLK_IMBALANCE",\
                                  "MMP_MAX_IMBALANCE_MAX_ONEPLANE","MMP_MAX_BAD_BLOCKS_MAX_IMBALANCE","MMP_MAX_IMBALANCE_RANDOM_IMBALANCE","MMP_IMBALANCE","PS_SAME_DIE_PLANE",\
                                  "PS_DIFF_DIE_DIFF_PLANE","PS_SAME_DIE_DIFF_PLANE","PS_DIFF_DIE_SAME_PLANE","MMP_WORST_CASE_IMBALANCE","MMP_MAX_BADBLOCKS_ONEMP", "MMP_MIN_BADBLOCKS_ONEMP"]

        elif numberOfMetaPlane == 1:
           if self.__fwConfigData.diesPerChip > 1:
              SPBadBlockPatternList = ["DIE_MAX_ONEPLANE","DIE_MAX_BAD_BLOCKS","DIE_MAX_IMBALANCE","DIE_RANDOM_IMBALANCE","DIE_LESS_BAD_BLOCKS","META_BLK_IMBALANCE",\
                                       "PS_SAME_DIE_PLANE","PS_DIFF_DIE_DIFF_PLANE","PS_SAME_DIE_DIFF_PLANE","PS_DIFF_DIE_SAME_PLANE"]
           else:
              SPBadBlockPatternList = ["DIE_MAX_ONEPLANE","DIE_MAX_BAD_BLOCKS","DIE_MAX_IMBALANCE","DIE_RANDOM_IMBALANCE","DIE_LESS_BAD_BLOCKS",\
                                      "PS_SAME_DIE_PLANE","PS_SAME_DIE_DIFF_PLANE"]
        """
        SPBadBlockPatternList = ["DIE_MAX_ONEPLANE", #Only 1 plane of Die0 is having max bad blocks
                                 "DIE_MAX_BAD_BLOCKS", #All planes in all dies have max bad blocks (per plane) injected
                                 "DIE_MAX_IMBALANCE",  #One plane has (max bad block + Gat limit + DFBL limit), the other plane has (max bad block - Gat limit - DFBL limit)
                                 "DIE_RANDOM_IMBALANCE", #One plane has X more than max bad blocks, the other plane X less than max bad blocks (X is not the Gat limit here)
                                 "DIE_LESS_BAD_BLOCKS", #Only 1 plane has badblocks injected (less than max)
                                 "PS_SAME_DIE_PLANE",
                                 "PS_SAME_DIE_DIFF_PLANE",
                                 "HORIZONTAL"]

        #Updating the BB patterns for non-SPCB tests
        if self.__optionValues.InitiateBadBlocks:
            SPBadBlockPatternList.extend(["RANDOM_BLOCKS", "RANDOM_UNIQUE_BLOCKS"])
            if self.__optionValues.SPBadBlockPattern == "MAX_BAD_BLOCKS": #Randomly pick a pattern if not specified in cmdline
                self.__optionValues.SPBadBlockPattern = "RANDOM"

            if self.__optionValues.RROnRelinkedBlocks == True:
                SPBadBlockPatternList = ["RANDOM_BLOCKS", "RANDOM_UNIQUE_BLOCKS", "DIE_MAX_BAD_BLOCKS"]

        if self.__fwConfigData.diesPerChip > 1:
            SPBadBlockPatternList.extend(["META_BLK_IMBALANCE", "PS_DIFF_DIE_DIFF_PLANE", "PS_DIFF_DIE_SAME_PLANE"])
        if (numberOfMetaPlane > 1) and fwFeatureConfig.isSpcbBadBlockMmpCompensationEnabled:
            SPBadBlockPatternList.extend(["MMP_MAX_IMBALANCE_MAX_ONEPLANE", "MMP_MAX_BAD_BLOCKS_MAX_IMBALANCE", "MMP_MAX_IMBALANCE_RANDOM_IMBALANCE", "MMP_IMBALANCE", \
                                          "MMP_WORST_CASE_IMBALANCE","MMP_MAX_BADBLOCKS_ONEMP", "MMP_MIN_BADBLOCKS_ONEMP"])

        if self.__optionValues.SPBadBlockPattern == "RANDOM":
            initial_pattern = self.__optionValues.SPBadBlockPattern
            self.__optionValues.SPBadBlockPattern = self.__randomObj.choice(SPBadBlockPatternList)

        self.logger.Info("","[BadBlockLib :: MarkRandomBadBlocksIncludingROMVisibleAndSPCBs] Selected Bad Block Pre-condition Pattern :%s"%self.__optionValues.SPBadBlockPattern)

        badBlockList = []
        totalBadBlockCount = 0
        BadBlockCountPerPlane = {}
        LastBlockIDInRomVisibility = -1 #Block 0 can also be marked bad
        badBlocklist_InROMVisibility = []
        BadBlockCountPerPlane_InROMVisibility = {}
        badBlockPerPlaneList = [0]*self.__fwConfigData.planeInterleave

        for die in range(self.__fwConfigData.dieInterleave):
            for plane in range(self.__fwConfigData.planeInterleave):
                BadBlockCountPerPlane_InROMVisibility[(die, plane)] = 0

        #Include ROM Visible blocks in BadBlockList for below patterns
        if self.__optionValues.SPBadBlockPattern in ["RANDOM_BLOCKS", "RANDOM_UNIQUE_BLOCKS", "DIE_MAX_BAD_BLOCKS", "HORIZONTAL"]:
            #badBlocklist_InROMVisibility, BadBlockCountPerPlane_InROMVisibility = self.MarkBadBlocksinROMVisibleBlocks(pattern=self.__randomObj.choice(["RANDOM_12_GOOD", "FIRST_12_GOOD", "LAST_12_GOOD"]), retval=1)
            badBlocklist_InROMVisibility, BadBlockCountPerPlane_InROMVisibility = self.MarkBadBlocksinROMVisibleBlocks(pattern=self.__randomObj.choice(["FIRST_12_GOOD", "LAST_12_GOOD", "LAST_12_GOOD", "LAST_12_GOOD"]), retval=1)
            ROMVisibleBlocks = self.GetROMVisibleBlocks()
            LastBlockIDInRomVisibility = ROMVisibleBlocks[-1][-1]

        self.logger.BigBanner("Bad Block Distribution Per Plane in ROM Visibility")
        for die in range(self.__fwConfigData.dieInterleave):
            for plane in range(self.__fwConfigData.planeInterleave):
                BadBlockCountPerPlane[(die, plane)] = 0
                BadBlockCountPerPlane[(die, plane)] += BadBlockCountPerPlane_InROMVisibility[(die, plane)]
                self.logger.Info("", "Bad blocks to be marked in Die: 0x%X, Plane: 0x%X - %d"%(die, plane, BadBlockCountPerPlane[(die, plane)]))

        #Bad block imbalance with in die
        if "DIE" in self.__optionValues.SPBadBlockPattern and "PS" not in self.__optionValues.SPBadBlockPattern:

            if self.__optionValues.SPBadBlockPattern == "DIE_MAX_BAD_BLOCKS":
                #All dies, all planes have max badblocks injected
                for plane in range(self.__fwConfigData.planeInterleave):
                    badBlockPerPlaneList[plane] = badBlockCount

            elif self.__optionValues.SPBadBlockPattern == "DIE_MAX_IMBALANCE":
                badBlockPerPlaneList = maxBadBlockImbalanceList

            elif self.__optionValues.SPBadBlockPattern == "DIE_RANDOM_IMBALANCE":
                randomNumOfBBs = self.__randomObj.randint(badBlockCount-self.__numGATBlocks-additionBadBlockLimit, maxBadBlockImbalanceInPlane-1)
                if randomNumOfBBs >= badBlockCount:
                    PlaneWithMoreBBs = randomNumOfBBs
                    PlaneWithLessBBs = badBlockCount - (randomNumOfBBs - badBlockCount)
                else:
                    PlaneWithMoreBBs = badBlockCount + (badBlockCount - randomNumOfBBs)
                    PlaneWithLessBBs = randomNumOfBBs

                RandomImbalanceList = []
                planesWithMoreBBs = self.__randomObj.sample(list(range(self.__fwConfigData.planeInterleave)), 2)
                for plane in range(self.__fwConfigData.planeInterleave):
                    if plane not in planesWithMoreBBs:
                        RandomImbalanceList.append(PlaneWithLessBBs)
                    else:
                        RandomImbalanceList.append(PlaneWithMoreBBs)
                badBlockPerPlaneList = RandomImbalanceList

            elif self.__optionValues.SPBadBlockPattern == "DIE_LESS_BAD_BLOCKS":
                badBlockPlane = self.__randomObj.choice(list(range(self.__fwConfigData.planeInterleave)))
                badBlockPerPlaneList[badBlockPlane] = self.__randomObj.randint(1, badBlockCount-1)

            elif self.__optionValues.SPBadBlockPattern == "DIE_MAX_ONEPLANE":
                planeWithMaxBadBlocks = self.__randomObj.choice(list(range(self.__fwConfigData.planeInterleave)))
                badBlockPerPlaneList[planeWithMaxBadBlocks] = MaxBadBlocksWithImbalance


            for chip in range (0, numOfChips):
                #MMP_BB_List_Chosen = False
                for die in range (0, diesPerChip):
                    multiMetaPlane  = old_div(((chip * diesPerChip) + die), self.__fwConfigData.dieInterleave)
                    if self.__optionValues.SPBadBlockPattern == "DIE_MAX_ONEPLANE" and die != 0 :
                        badBlockPerPlaneList = [0]*self.__fwConfigData.planeInterleave
                    if multiMetaPlane == numberOfMetaPlane:
                        break
                    totalBadBlockCountPerPlane = 0
                    for plane in range (0, planesPerDie):
                        totalBadBlockCountPerPlane = 0
                        if self.__optionValues.SPBadBlockPattern == "LESS_BAD_BLOCKS":
                            badBlockPerPlane = self.__randomObj.randint(4, 15)
                        else:
                            """
                            if multiMetaPlane>0 and initial_pattern == "RANDOM":
                               if MMP_BB_List_Chosen == False :
                                  MMP_badBlockPerPlaneList = self.__randomObj.choice([badBlockPerPlaneList1,badBlockPerPlaneList2,badBlockPerPlaneList3,badBlockPerPlaneList4])
                                  MMP_BB_List_Chosen = True
                               badBlockPerPlane = MMP_badBlockPerPlaneList[plane]
                            else:
                            """
                            badBlockPerPlane = badBlockPerPlaneList[plane] - BadBlockCountPerPlane_InROMVisibility[(die, plane)]
                        chosenBlockList = []
                        while badBlockPerPlane > 0:
                            block = self.__randomObj.randint(LastBlockIDInRomVisibility+1, blocksPerPlane - 1)
                            physicalAddress = AddressTypes.PhysicalAddress()
                            physicalAddress.chip    = chip
                            physicalAddress.die     = die
                            physicalAddress.plane   = plane
                            physicalAddress.block   = block
                            physicalAddress.wordLine  = 0
                            physicalAddress.mlcLevel  = 0
                            physicalAddress.eccPage = 0
                            if self.__fwConfigData.isBiCS:
                                physicalAddress.string  = 0
                            isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
                            if not isBadBlock and (block not in (chosenBlockList)) :
                                badBlockList.append(physicalAddress)
                                chosenBlockList.append(block)
                                badBlockPerPlane = badBlockPerPlane - 1
                                totalBadBlockCount = totalBadBlockCount + 1
                                totalBadBlockCountPerPlane = totalBadBlockCountPerPlane + 1
                                self.logger.Info("","[ TotalBadBlockCount : %d TotalBadBlockCountPerPlane : %d ]  Block selected %s"%(totalBadBlockCount, totalBadBlockCountPerPlane, physicalAddress))
                                BadBlockCountPerPlane[(die, plane)] += 1
        elif  "MMP" in self.__optionValues.SPBadBlockPattern:
            badBlockPerPlaneList = []

            if self.__optionValues.SPBadBlockPattern == "MMP_MAX_IMBALANCE_MAX_ONEPLANE":
                if numberOfMetaPlane == 2:
                    MMPPatternList = ["MAX_IMBALANCE","MAX_ONEPLANE"]
                elif numberOfMetaPlane == 3:
                    MMPPatternList = ["MAX_IMBALANCE","MAX_ONEPLANE","MAX_IMBALANCE"]
                elif numberOfMetaPlane == 4:
                    MMPPatternList = ["MAX_IMBALANCE","MAX_ONEPLANE","MAX_IMBALANCE","MAX_ONEPLANE"]

                for i in range (0,len(MMPPatternList)):
                    badBlockPerPlaneList_t = [0]*self.__fwConfigData.planeInterleave
                    Pattern_Choosen=self.__randomObj.choice(MMPPatternList)
                    MMPPatternList.remove(Pattern_Choosen)
                    if Pattern_Choosen == "MAX_IMBALANCE":
                        #To recheck: MMP cases to be added
                        raise TestError.TestFailError(self.vtfContainer.GetTestName(), "BadBlock Imbalance Pattern Handling not added yet for 4P")
                        badBlockCountPlane0 = self.__randomObj.choice(maxBadBlockImbalanceList)
                        maxBadBlockImbalanceList.remove(badBlockCountPlane0)
                        badBlockCountPlane1 =  self.__randomObj.choice(maxBadBlockImbalanceList)

                        maxBadBlockImbalanceList = [badBlockCount + self.__numGATBlocks,badBlockCount - self.__numGATBlocks]

                    elif Pattern_Choosen == "MAX_ONEPLANE":
                        planeWithMaxBadBlocks = self.__randomObj.choice(list(range(self.__fwConfigData.planeInterleave)))
                        badBlockPerPlaneList_t[planeWithMaxBadBlocks] = badBlockCount

                    badBlockPerPlaneList.append(badBlockPerPlaneList_t)


            elif self.__optionValues.SPBadBlockPattern == "MMP_MAX_BAD_BLOCKS_MAX_IMBALANCE":

                if numberOfMetaPlane == 2:
                    MMPPatternList = ["MAX_IMBALANCE","MAX_BAD_BLOCKS"]
                elif numberOfMetaPlane == 3:
                    MMPPatternList = ["MAX_IMBALANCE","MAX_BAD_BLOCKS","MAX_IMBALANCE"]
                elif numberOfMetaPlane == 4:
                    MMPPatternList = ["MAX_IMBALANCE","MAX_BAD_BLOCKS","MAX_IMBALANCE","MAX_BAD_BLOCKS"]

                for i in range (0,len(MMPPatternList)):
                    badBlockPerPlaneList_t = [0]*self.__fwConfigData.planeInterleave
                    Pattern_Choosen=self.__randomObj.choice(MMPPatternList)
                    MMPPatternList.remove(Pattern_Choosen)
                    if Pattern_Choosen == "MAX_IMBALANCE":
                        #To recheck: MMP cases to be added
                        raise TestError.TestFailError(self.vtfContainer.GetTestName(), "BadBlock Imbalance Pattern Handling not added yet for 4P")
                        badBlockCountPlane0 = self.__randomObj.choice(maxBadBlockImbalanceList)
                        maxBadBlockImbalanceList.remove(badBlockCountPlane0)
                        badBlockCountPlane1 =  self.__randomObj.choice(maxBadBlockImbalanceList)

                        maxBadBlockImbalanceList = [badBlockCount + self.__numGATBlocks,badBlockCount - self.__numGATBlocks]

                    elif Pattern_Choosen == "MAX_BAD_BLOCKS":
                        badBlockPerPlaneList_t = [badBlockCount]*self.__fwConfigData.planeInterleave

                    badBlockPerPlaneList.append(badBlockPerPlaneList_t)

            elif self.__optionValues.SPBadBlockPattern == "MMP_MAX_IMBALANCE_RANDOM_IMBALANCE":

                if numberOfMetaPlane == 2:
                    MMPPatternList = ["MAX_IMBALANCE","RANDOM_IMBALANCE"]
                elif numberOfMetaPlane == 3:
                    MMPPatternList = ["MAX_IMBALANCE","RANDOM_IMBALANCE","MAX_IMBALANCE"]
                elif numberOfMetaPlane == 4:
                    MMPPatternList = ["MAX_IMBALANCE","RANDOM_IMBALANCE","MAX_IMBALANCE","RANDOM_IMBALANCE"]

                for i in range (0,len(MMPPatternList)):
                    badBlockPerPlaneList_t = [0]*self.__fwConfigData.planeInterleave
                    Pattern_Choosen=self.__randomObj.choice(MMPPatternList)
                    MMPPatternList.remove(Pattern_Choosen)
                    if Pattern_Choosen == "MAX_IMBALANCE":
                        #To recheck: MMP cases to be added
                        raise TestError.TestFailError(self.vtfContainer.GetTestName(), "BadBlock Imbalance Pattern Handling not added yet for 4P")
                        badBlockCountPlane0 = self.__randomObj.choice(maxBadBlockImbalanceList)
                        maxBadBlockImbalanceList.remove(badBlockCountPlane0)
                        badBlockCountPlane1 =  self.__randomObj.choice(maxBadBlockImbalanceList)
                        maxBadBlockImbalanceList = [badBlockCount + self.__numGATBlocks,badBlockCount - self.__numGATBlocks]

                    elif Pattern_Choosen == "RANDOM_IMBALANCE":
                        #To recheck: MMP cases to be added
                        raise TestError.TestFailError(self.vtfContainer.GetTestName(), "BadBlock Imbalance Pattern Handling not added yet for 4P")
                        badBlockCountPlane0 = self.__randomObj.randint(badBlockCount-self.__numGATBlocks, maxBadBlockImbalanceInPlane-1)
                        if badBlockCountPlane0 >= badBlockCount:
                            badBlockCountPlane1 = badBlockCount - (badBlockCountPlane0 - badBlockCount)
                        else:
                            badBlockCountPlane1 = badBlockCount + (badBlockCount - badBlockCountPlane0)

                    badBlockPerPlaneList.append([badBlockCountPlane0,badBlockCountPlane1])

            elif self.__optionValues.SPBadBlockPattern == "MMP_IMBALANCE":

                if numberOfMetaPlane == 2:
                    MMPPatternList = ["MAX_ALL_PLANE_IMBALANCE","MIN_ALL_PLANE_IMBALANCE"]
                elif numberOfMetaPlane == 3:
                    MMPPatternList = ["MAX_ALL_PLANE_IMBALANCE","MAX_IMBALANCE","MIN_ALL_PLANE_IMBALANCE"]
                elif numberOfMetaPlane == 4:
                    MMPPatternList = ["MAX_ALL_PLANE_IMBALANCE","MIN_ALL_PLANE_IMBALANCE","MAX_ALL_PLANE_IMBALANCE","MIN_ALL_PLANE_IMBALANCE"]

                for i in range (0,len(MMPPatternList)):
                    badBlockPerPlaneList_t = [0]*self.__fwConfigData.planeInterleave
                    Pattern_Choosen=self.__randomObj.choice(MMPPatternList)
                    MMPPatternList.remove(Pattern_Choosen)
                    if Pattern_Choosen == "MAX_ALL_PLANE_IMBALANCE":
                        badBlockPerPlaneList_t = [badBlockCount + self.__numGATBlocks]*self.__fwConfigData.planeInterleave

                    elif Pattern_Choosen == "MAX_IMBALANCE":
                        #To recheck: MMP cases to be added
                        raise TestError.TestFailError(self.vtfContainer.GetTestName(), "BadBlock Imbalance Pattern Handling not added yet for 4P")

                        badBlockCountPlane0 = self.__randomObj.choice(maxBadBlockImbalanceList)
                        maxBadBlockImbalanceList.remove(badBlockCountPlane0)
                        badBlockCountPlane1 =  self.__randomObj.choice(maxBadBlockImbalanceList)

                        maxBadBlockImbalanceList = [badBlockCount + self.__numGATBlocks,badBlockCount - self.__numGATBlocks]

                    elif Pattern_Choosen == "MIN_ALL_PLANE_IMBALANCE":
                        badBlockPerPlaneList_t = [badBlockCount - self.__numGATBlocks]*self.__fwConfigData.planeInterleave

                    badBlockPerPlaneList.append(badBlockPerPlaneList_t)

            elif self.__optionValues.SPBadBlockPattern == "MMP_MAX_BADBLOCKS_ONEMP":

                if numberOfMetaPlane == 2:
                    MMPPatternList = ["MAX_ALL_PLANE_IMBALANCE", "NONE"]
                elif numberOfMetaPlane == 3:
                    MMPPatternList = ["MAX_ALL_PLANE_IMBALANCE", "NONE","NONE"]
                elif numberOfMetaPlane == 4:
                    MMPPatternList = ["MAX_ALL_PLANE_IMBALANCE", "NONE","NONE","NONE"]

                for i in range (0,len(MMPPatternList)):
                    badBlockPerPlaneList_t = [0]*self.__fwConfigData.planeInterleave
                    Pattern_Choosen=self.__randomObj.choice(MMPPatternList)
                    MMPPatternList.remove(Pattern_Choosen)

                    if Pattern_Choosen == "MAX_ALL_PLANE_IMBALANCE":
                        badBlockPerPlaneList_t = [badBlockCount + self.__numGATBlocks]*self.__fwConfigData.planeInterleave

                    badBlockPerPlaneList.append(badBlockPerPlaneList_t)

            elif self.__optionValues.SPBadBlockPattern == "MMP_MIN_BADBLOCKS_ONEMP":

                if numberOfMetaPlane == 2:
                    MMPPatternList = ["MIN_ALL_PLANE_IMBALANCE", "NONE"]
                elif numberOfMetaPlane == 3:
                    MMPPatternList = ["MIN_ALL_PLANE_IMBALANCE", "NONE","NONE"]
                elif numberOfMetaPlane == 4:
                    MMPPatternList = ["MIN_ALL_PLANE_IMBALANCE", "NONE","NONE","NONE"]

                for i in range (0,len(MMPPatternList)):
                    badBlockPerPlaneList_t = [0]*self.__fwConfigData.planeInterleave
                    Pattern_Choosen=self.__randomObj.choice(MMPPatternList)
                    MMPPatternList.remove(Pattern_Choosen)

                    if Pattern_Choosen == "MIN_ALL_PLANE_IMBALANCE":
                        badBlockPerPlaneList_t = [badBlockCount - self.__numGATBlocks]*self.__fwConfigData.planeInterleave

                    badBlockPerPlaneList.append(badBlockPerPlaneList_t)

            elif self.__optionValues.SPBadBlockPattern == "MMP_WORST_CASE_IMBALANCE":

                # Mark badblocks consecutively after 1st 128 blocks in all planes of only one Meta Plane.
                if numberOfMetaPlane == 2:
                    MMPPatternList = ["MAX_ALL_PLANE_IMBALANCE", "MIN_ALL_PLANE_IMBALANCE"]
                elif numberOfMetaPlane == 3:
                    MMPPatternList = ["MAX_ALL_PLANE_IMBALANCE", "MAX_IMBALANCE","MIN_ALL_PLANE_IMBALANCE"]
                elif numberOfMetaPlane == 4:
                    MMPPatternList = ["MAX_ALL_PLANE_IMBALANCE", "MIN_ALL_PLANE_IMBALANCE","MIN_ALL_PLANE_IMBALANCE","MAX_ALL_PLANE_IMBALANCE"]

                for i in range (0,len(MMPPatternList)):
                    badBlockPerPlaneList_t = [0]*self.__fwConfigData.planeInterleave
                    Pattern_Choosen = MMPPatternList[i]

                    if Pattern_Choosen == "MAX_ALL_PLANE_IMBALANCE":
                        badBlockPerPlaneList_t = [badBlockCount + self.__numGATBlocks]*self.__fwConfigData.planeInterleave

                    elif Pattern_Choosen == "MIN_ALL_PLANE_IMBALANCE":
                        badBlockPerPlaneList_t = [badBlockCount - self.__numGATBlocks]*self.__fwConfigData.planeInterleave

                    elif Pattern_Choosen == "MAX_IMBALANCE":
                        #To recheck: MMP cases to be added
                        raise TestError.TestFailError(self.vtfContainer.GetTestName(), "BadBlock Imbalance Pattern Handling not added yet for 4P")

                        badBlockCountPlane0 = self.__randomObj.choice(maxBadBlockImbalanceList)
                        maxBadBlockImbalanceList.remove(badBlockCountPlane0)
                        badBlockCountPlane1 =  self.__randomObj.choice(maxBadBlockImbalanceList)
                        maxBadBlockImbalanceList = [badBlockCount + self.__numGATBlocks,badBlockCount - self.__numGATBlocks]

                    badBlockPerPlaneList.append(badBlockPerPlaneList_t)

            for chip in range (0, numOfChips):
                #MMP_BB_List_Chosen = False
                for die in range (0, diesPerChip):
                    multiMetaPlane  = old_div(((chip * diesPerChip) + die), self.__fwConfigData.dieInterleave)
                    if multiMetaPlane == numberOfMetaPlane:
                        break
                    totalBadBlockCountPerPlane = 0
                    for plane in range (0, planesPerDie):
                        totalBadBlockCountPerPlane = 0
                        badBlockPerPlane = badBlockPerPlaneList[multiMetaPlane][plane]
                        chosenBlockList = []
                        while badBlockPerPlane > 0:
                            if self.__optionValues.SPBadBlockPattern == "MMP_WORST_CASE_IMBALANCE":
                                block = blocksPerPlane-badBlockPerPlane
                            else:
                                block = self.__randomObj.randint(2, blocksPerPlane - 1)
                            physicalAddress = AddressTypes.PhysicalAddress()
                            physicalAddress.chip    = chip
                            physicalAddress.die     = die
                            physicalAddress.plane   = plane
                            physicalAddress.block   = block
                            physicalAddress.wordLine  = 0
                            physicalAddress.mlcLevel  = 0
                            physicalAddress.eccPage = 0
                            if self.__fwConfigData.isBiCS:
                                physicalAddress.string  = 0
                            isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
                            if not isBadBlock and (block not in (chosenBlockList)) :
                                badBlockList.append(physicalAddress)
                                chosenBlockList.append(block)
                                badBlockPerPlane = badBlockPerPlane - 1
                                totalBadBlockCount = totalBadBlockCount + 1
                                totalBadBlockCountPerPlane = totalBadBlockCountPerPlane + 1
                                self.logger.Info("","[ TotalBadBlockCount : %d TotalBadBlockCountPerPlane : %d ]  Block selected %s"%(totalBadBlockCount, totalBadBlockCountPerPlane, physicalAddress))

        #Bad block imbalance with in meta block
        elif self.__optionValues.SPBadBlockPattern == "META_BLK_IMBALANCE":
            badBlockPerPlaneListTemp = []
            dieInterleave            = self.__fwConfigData.dieInterleave
            numOfPlanesInMetaPlane   = dieInterleave * self.__fwConfigData.planeInterleave
            numPlaneWithMaxBB = 1
            maxBadBlocksInMetaPlane  = numOfPlanesInMetaPlane * badBlockCount
            while (numPlaneWithMaxBB * maxBadBlockImbalanceInPlane < maxBadBlocksInMetaPlane):
                numPlaneWithMaxBB += 1
            numPlaneWithMaxBB        = numPlaneWithMaxBB - 1
            badBlockPerPlaneList     = [maxBadBlockImbalanceInPlane] * numPlaneWithMaxBB
            remainingBadBlocks       = maxBadBlocksInMetaPlane - (maxBadBlockImbalanceInPlane * numPlaneWithMaxBB)
            if dieInterleave > 1:
                badBlocksInOtherPlanes   = remainingBadBlocks
                badBlockPerPlaneList.extend([badBlocksInOtherPlanes])
                remainingPlane = numOfPlanesInMetaPlane - (numPlaneWithMaxBB + 1)
                for i in range(remainingPlane):
                    badBlockPerPlaneList.append(0)

            for chip in range (0, numOfChips):
                for die in range (0, diesPerChip):
                    multiMetaPlane  = old_div(((chip * diesPerChip) + die), self.__fwConfigData.dieInterleave)
                    if multiMetaPlane == numberOfMetaPlane:
                        break
                    if die%dieInterleave == 0:
                        badBlockPerPlaneListTemp = copy.deepcopy(badBlockPerPlaneList)
                    totalBadBlockCountPerPlane = 0
                    for plane in range (0, planesPerDie):
                        totalBadBlockCountPerPlane = 0
                        badBlockPerPlane = self.__randomObj.choice(badBlockPerPlaneListTemp)
                        badBlockPerPlaneListTemp.remove(badBlockPerPlane)
                        chosenBlockList = []
                        while badBlockPerPlane > 0:
                            block = self.__randomObj.randint(2, blocksPerPlane - 1)
                            physicalAddress = AddressTypes.PhysicalAddress()
                            physicalAddress.chip    = chip
                            physicalAddress.die     = die
                            physicalAddress.plane   = plane
                            physicalAddress.block   = block
                            physicalAddress.wordLine  = 0
                            physicalAddress.mlcLevel  = 0
                            physicalAddress.eccPage = 0
                            if self.__fwConfigData.isBiCS:
                                physicalAddress.string  = 0
                            isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
                            if not isBadBlock and (block not in (chosenBlockList)) :
                                badBlockList.append(physicalAddress)
                                chosenBlockList.append(block)
                                badBlockPerPlane = badBlockPerPlane - 1
                                totalBadBlockCount = totalBadBlockCount + 1
                                totalBadBlockCountPerPlane = totalBadBlockCountPerPlane + 1
                                self.logger.Info("","[ TotalBadBlockCount : %d TotalBadBlockCountPerPlane : %d ]  Block selected %s"%(totalBadBlockCount, totalBadBlockCountPerPlane, physicalAddress))
                                BadBlockCountPerPlane[(die, plane)] += 1
        #Primary/Secondary block selection
        elif "PS" in self.__optionValues.SPBadBlockPattern:
            dieInterleave            = self.__fwConfigData.dieInterleave
            planeInterLeave          = self.__fwConfigData.planeInterleave
            planeList                = list(range(planeInterLeave))
            dieList                  = list(range(dieInterleave))
            if self.__optionValues.SPBadBlockPattern == "PS_SAME_DIE_PLANE":
                #Inject min BBs on selected plane so that MIP/GAT pri and sec blocks are allocated on the same die, same plane
                selectedDiePlane = [self.__randomObj.choice(dieList),self.__randomObj.choice(planeList)]
                badBlockOnSelectedPlane = self.__randomObj.randint(5,old_div(badBlockCount,2))
                if self.__optionValues.badBlocksCount != 0:
                    badBlocksOnOtherPlane = self.__optionValues.badBlocksCount
                else:
                    badBlocksOnOtherPlane = self.__randomObj.randint(badBlockOnSelectedPlane + 6,badBlockCount)
                badBlockPerPlaneList = [[badBlocksOnOtherPlane for i in range(planeInterLeave)] for i in range(dieInterleave)]
                badBlockPerPlaneList[selectedDiePlane[0]][selectedDiePlane[1]] = badBlockOnSelectedPlane

            elif self.__optionValues.SPBadBlockPattern == "PS_SAME_DIE_DIFF_PLANE":
                #Inject min BBs on any 2 random planes, first MIP Pri will be allocated in PlaneX and then MIP Sec in PlaneY
                #Similarly GAT pri/sec blocks will be allocated in different planes
                dieSelected = self.__randomObj.choice(dieList)
                primaryPlane = self.__randomObj.choice(planeList)
                planeList.remove(primaryPlane)
                secondaryPlane = self.__randomObj.choice(planeList)
                badBlockOnPrimaryPlane = self.__randomObj.randint(5,old_div(badBlockCount,2))
                if self.__optionValues.badBlocksCount != 0:
                    badBlocksOnOtherPlane = self.__optionValues.badBlocksCount
                else:
                    badBlocksOnOtherPlane = self.__randomObj.randint(badBlockOnPrimaryPlane + 6,badBlockCount)
                badBlockPerPlaneList = [[badBlocksOnOtherPlane for i in range(planeInterLeave)] for i in range(dieInterleave)]
                badBlockPerPlaneList[dieSelected][primaryPlane] = badBlockOnPrimaryPlane
                badBlockPerPlaneList[dieSelected][secondaryPlane] = badBlockOnPrimaryPlane

            elif self.__optionValues.SPBadBlockPattern == "PS_DIFF_DIE_SAME_PLANE" and self.__fwConfigData.diesPerChip > 1:
                #MIP/GAT pri and sec blocks should be allocated on different dies but same plane
                primaryDie = self.__randomObj.choice(dieList)
                dieList.remove(primaryDie)
                secondaryDie = self.__randomObj.choice(dieList)
                PlaneSelected = self.__randomObj.choice(planeList)
                badBlockOnPrimaryPlane = self.__randomObj.randint(5,old_div(badBlockCount,2))
                if self.__optionValues.badBlocksCount != 0:
                    badBlocksOnOtherPlane = self.__optionValues.badBlocksCount
                else:
                    badBlocksOnOtherPlane = self.__randomObj.randint(badBlockOnPrimaryPlane + 6,badBlockCount)
                badBlockPerPlaneList = [[badBlocksOnOtherPlane for i in range(planeInterLeave)] for i in range(dieInterleave)]
                badBlockPerPlaneList[primaryDie][PlaneSelected] = badBlockOnPrimaryPlane
                badBlockPerPlaneList[secondaryDie][PlaneSelected] = badBlockOnPrimaryPlane

            elif self.__optionValues.SPBadBlockPattern == "PS_DIFF_DIE_DIFF_PLANE" and self.__fwConfigData.diesPerChip > 1:
                primaryDie = self.__randomObj.choice(dieList)
                dieList.remove(primaryDie)
                secondaryDie = self.__randomObj.choice(dieList)
                primaryPlane = self.__randomObj.choice(planeList)
                planeList.remove(primaryPlane)
                secondaryPlane = self.__randomObj.choice(planeList)
                badBlockOnPrimaryPlane = self.__randomObj.randint(5,old_div(badBlockCount,2))
                if self.__optionValues.badBlocksCount != 0:
                    badBlocksOnOtherPlane = self.__optionValues.badBlocksCount
                else:
                    badBlocksOnOtherPlane = self.__randomObj.randint(badBlockOnPrimaryPlane + 6,badBlockCount)
                badBlockPerPlaneList = [[badBlocksOnOtherPlane for i in range(planeInterLeave)] for i in range(dieInterleave)]
                badBlockPerPlaneList[primaryDie][primaryPlane] = badBlockOnPrimaryPlane
                badBlockPerPlaneList[secondaryDie][secondaryPlane] = badBlockOnPrimaryPlane
            else :
                self.logger.Info("","Selected bad block precondition : %s is valid only for multi die configuration")
                return

            for chip in range (0, numOfChips):
                for die in range (0, diesPerChip):
                    multiMetaPlane  = old_div(((chip * diesPerChip) + die), self.__fwConfigData.dieInterleave)
                    if multiMetaPlane == numberOfMetaPlane:
                        break
                    totalBadBlockCountPerPlane = 0
                    for plane in range (0, planesPerDie):
                        totalBadBlockCountPerPlane = 0
                        badBlockPerPlane = badBlockPerPlaneList[die%self.__fwConfigData.dieInterleave][plane]
                        chosenBlockList = []
                        while badBlockPerPlane > 0:
                            block = self.__randomObj.randint(2, blocksPerPlane - 1)
                            physicalAddress = AddressTypes.PhysicalAddress()
                            physicalAddress.chip    = chip
                            physicalAddress.die     = die
                            physicalAddress.plane   = plane
                            physicalAddress.block   = block
                            physicalAddress.wordLine  = 0
                            physicalAddress.mlcLevel  = 0
                            physicalAddress.eccPage = 0
                            if self.__fwConfigData.isBiCS:
                                physicalAddress.string  = 0
                            isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
                            if not isBadBlock and (block not in (chosenBlockList)) :
                                badBlockList.append(physicalAddress)
                                chosenBlockList.append(block)
                                badBlockPerPlane = badBlockPerPlane - 1
                                totalBadBlockCount = totalBadBlockCount + 1
                                totalBadBlockCountPerPlane = totalBadBlockCountPerPlane + 1
                                self.logger.Info("","[ TotalBadBlockCount : %d TotalBadBlockCountPerPlane : %d ]  Block selected %s"%(totalBadBlockCount, totalBadBlockCountPerPlane, physicalAddress))
                                BadBlockCountPerPlane[(die, plane)] += 1

        elif self.__optionValues.SPBadBlockPattern == "RANDOM_BLOCKS":
            for chip in range (0, numOfChips):
                for die in range (0, diesPerChip):
                    multiMetaPlane  = old_div(((chip * diesPerChip) + die), self.__fwConfigData.dieInterleave)
                    if multiMetaPlane == numberOfMetaPlane:
                        break
                    totalBadBlockCountPerPlane = 0
                    for plane in range (0, planesPerDie):
                        totalBadBlockCountPerPlane = 0
                        badBlockPerPlane = badBlockCount
                        chosenBlockList = []
                        while badBlockPerPlane > 0:
                            block = self.__randomObj.randint(LastBlockIDInRomVisibility+1, blocksPerPlane - 1)
                            physicalAddress = AddressTypes.PhysicalAddress()
                            physicalAddress.chip    = chip
                            physicalAddress.die     = die
                            physicalAddress.plane   = plane
                            physicalAddress.block   = block
                            physicalAddress.wordLine  = 0
                            physicalAddress.mlcLevel  = 0
                            physicalAddress.eccPage = 0
                            if self.__fwConfigData.isBiCS:
                                physicalAddress.string  = 0
                            isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
                            if not isBadBlock and (block not in (chosenBlockList)) :
                                badBlockList.append(physicalAddress)
                                chosenBlockList.append(block)
                                badBlockPerPlane = badBlockPerPlane - 1
                                totalBadBlockCount = totalBadBlockCount + 1
                                totalBadBlockCountPerPlane = totalBadBlockCountPerPlane + 1
                                self.logger.Info("","[ TotalBadBlockCount : %d TotalBadBlockCountPerPlane : %d ]  Block selected %s"%(totalBadBlockCount, totalBadBlockCountPerPlane, physicalAddress))
                                #self.logger.Info("Random block selected %s"%(physicalAddress))
                        BadBlockCountPerPlane[(die, plane)] = totalBadBlockCountPerPlane


        elif self.__optionValues.SPBadBlockPattern == "RANDOM_UNIQUE_BLOCKS": #Unique blocks throughout the MP, one physical blcok in each Horizontal MB

            chosenMultiMetaPlane = []
            for chip in range (0, numOfChips):
                for die in range (0, diesPerChip):

                    multiMetaPlane  = old_div(((chip * diesPerChip) + die), self.__fwConfigData.dieInterleave)
                    if multiMetaPlane == numberOfMetaPlane:
                        break

                    if multiMetaPlane not in chosenMultiMetaPlane:
                        chosenBlockListInAMetaplane = []
                        chosenMultiMetaPlane.append(multiMetaPlane)

                    totalBadBlockCountPerPlane = 0
                    for plane in range (0, planesPerDie):
                        totalBadBlockCountPerPlane = 0
                        badBlockPerPlane = badBlockCount
                        chosenBlockList = []
                        while badBlockPerPlane > 0:
                            block = self.__randomObj.randint(LastBlockIDInRomVisibility+1, blocksPerPlane - 1)
                            physicalAddress = AddressTypes.PhysicalAddress()
                            physicalAddress.chip    = chip
                            physicalAddress.die     = die
                            physicalAddress.plane   = plane
                            physicalAddress.block   = block
                            physicalAddress.wordLine  = 0
                            physicalAddress.mlcLevel  = 0
                            physicalAddress.eccPage = 0
                            if self.__fwConfigData.isBiCS:
                                physicalAddress.string  = 0
                            isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
                            #Random Unique pattern --> Block num would be uniquely picked, same block num would not be picked in current metaplane
                            if not isBadBlock and (block not in (chosenBlockList)) and (block not in (chosenBlockListInAMetaplane)) :
                                badBlockList.append(physicalAddress)
                                chosenBlockList.append(block)
                                chosenBlockListInAMetaplane.append(block)
                                badBlockPerPlane = badBlockPerPlane - 1
                                totalBadBlockCount = totalBadBlockCount + 1
                                totalBadBlockCountPerPlane = totalBadBlockCountPerPlane + 1
                                self.logger.Info("","[ TotalBadBlockCount : %d TotalBadBlockCountPerPlane : %d ]  Block selected %s"%(totalBadBlockCount, totalBadBlockCountPerPlane, physicalAddress))
                                #self.logger.Info("Random block selected %s"%(physicalAddress))
                        BadBlockCountPerPlane[(die, plane)] = totalBadBlockCountPerPlane



        elif self.__optionValues.SPBadBlockPattern == "HORIZONTAL": #one each plane, inject BB on incremental block num
            for chip in range (0, numOfChips):
                for die in range (0, diesPerChip):
                    for plane in range (0, planesPerDie):
                        badBlockPerPlane = badBlockCount - BadBlockCountPerPlane_InROMVisibility[(0,0)]
                        totalBadBlockCountPerPlane = 0
                        lastBlockInRomVisibility = self.GetROMVisibleBlocks()[-1][3]
                        chosenBlockList = []
                        for block in range(lastBlockInRomVisibility+1, badBlockPerPlane+lastBlockInRomVisibility+1):
                            physicalAddress = AddressTypes.PhysicalAddress()
                            physicalAddress.chip    = chip
                            physicalAddress.die     = die
                            physicalAddress.plane   = plane
                            physicalAddress.block   = block
                            physicalAddress.wordLine  = 0
                            physicalAddress.mlcLevel  = 0
                            physicalAddress.eccPage = 0
                            if self.__fwConfigData.isBiCS:
                                physicalAddress.string  = 0
                            isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
                            if not isBadBlock and block not in chosenBlockList:
                                badBlockList.append(physicalAddress)
                                chosenBlockList.append(block)
                                totalBadBlockCount = totalBadBlockCount + 1
                                totalBadBlockCountPerPlane = totalBadBlockCountPerPlane + 1
                                self.logger.Info("","[ TotalBadBlockCount : %d TotalBadBlockCountPerPlane : %d ]  Block selected %s"%(totalBadBlockCount, totalBadBlockCountPerPlane, physicalAddress))
                                #self.logger.Info("Random block selected %s"%(physicalAddress))
                        BadBlockCountPerPlane[(die, plane)] = totalBadBlockCountPerPlane

        if self.__optionValues.SPBadBlockPattern in ["RANDOM_BLOCKS", "RANDOM_UNIQUE_BLOCKS"]:
            import ValidationRwcManager
            if not ValidationRwcManager.inject_more_than_max_BBs:
                #Remove excess blocks from all planes as we have added bad blocks from ROM visibility
                badBlockList, BadBlockCountPerPlane = self.RemoveExcessBadBlocksFromAllPlanes(BadBlockCountPerPlane, badBlocklist_InROMVisibility, BadBlockCountPerPlane_InROMVisibility, badBlockList)
        else:
            badBlockList.extend(badBlocklist_InROMVisibility)

        self.logger.BigBanner("Bad Block Distribution Per Plane (Pattern - %s)"%self.__optionValues.SPBadBlockPattern)
        for die in range(self.__fwConfigData.dieInterleave):
            for plane in range(self.__fwConfigData.planeInterleave):
                self.logger.Info("", "Bad blocks to be marked in Die: 0x%X, Plane: 0x%X - %d"%(die, plane, BadBlockCountPerPlane[(die, plane)]))

        self.MarkBadBlocks(badBlockList,botFilename,paramsfilepath,maxLba)

        #Check Whether the bad blocks added to Grown badblock list
        for physicalAddress in (badBlockList):
            physicalAddress.wordLine = 0
            physicalAddress.mlcLevel = 0
            physicalAddress.eccPage = 0
            if self.__fwConfigData.isBiCS:
                physicalAddress.string = 0
            isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
            if isBadBlock:
                self.logger.Info("","[CreateFactoryMarkedBlocksInTheCard] The bad block which was created is found in factory marked badblock file which belongs to Chip no[0x%X],Die no[0x%X],Plane no[0x%X],Block no[0x%X]"
                                 %(physicalAddress.chip,physicalAddress.die,physicalAddress.plane,physicalAddress.block))

            else:
                self.logger.Info(""," [CreateFactoryMarkedBlocksInTheCard] The bad block which was created is not found in factory marked badblock file which belongs to Chip no[0x%X],Die no[0x%X],Plane no[0x%X],Block no[0x%X]"
                                 %(physicalAddress.chip,physicalAddress.die,physicalAddress.plane,physicalAddress.block))
                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "[CreateFactoryMarkedBlocksInTheCard] Created bad block is not found in factory marked badblock file")
        return badBlockList, BadBlockCountPerPlane
        #end of MarkRandomBadBlocks

    def CleanUpMarkedBadBlocks(self ,botFilename = '',
                               paramsfilepath = None,
                               maxLba=0):
        """
        Name : CleanUpMarkedBadBlocks
        Deescription :
             Clean all the bad blocks that marked bad
        Argument :
             botFilename       : Bot file path
             paramsfilepath    : Parameter file path
             maxLba            : maxLba of card
        Return :
             None
        """
        #for clean up all the bad blocks do the normal download
        self.__validationSpace.DoDownLoadAndFormat(botFilename,
                                                   paramsFile = paramsfilepath,
                                                   maxLba = maxLba)

        #Initialise all the variables
        self.__InitialiseVariables()

    def NumberOfBBpresentInFile224 (self):
        numOfChip   = self.__fwConfigData.numChips
        numOfDie    =  self.__fwConfigData.diesPerChip
        numOfPlane  = self.__fwConfigData.planesPerDie
        numOfBlock  = self.__fwConfigData.blocksPerPlane

        badBlockCount  = 0
        goodBlockCount = 0
        physicalAddress = AddressTypes.PhysicalAddress()
        #Apply Dr thresholds to all the blocks in the card
        for chip in range (0, numOfChip):
            for die in range (0, numOfDie):
                for plane in range (0, numOfPlane):
                    for block in range (0, numOfBlock):
                        physicalAddress.block   = block
                        physicalAddress.plane   = plane
                        physicalAddress.die     = die
                        physicalAddress.chip    = chip
                        physicalAddress.wordLine = 0
                        physicalAddress.mlcLevel = 0
                        physicalAddress.eccPage = 0
                        if self.__fwConfigData.isBiCS:
                            physicalAddress.string    = 0
                        retVal = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
                        if retVal == True:
                            badBlockCount = badBlockCount + 1
                            self.logger.Info("","Chip:0x%x, Die:0x%x, Plane:0x%x, Block:0x%x"%(chip,die,plane,block))
                        if retVal == False:
                            goodBlockCount = goodBlockCount + 1
        return badBlockCount, goodBlockCount

    #End of NumberOfBBpresentinFile224

    #end of CleanUpMarkedBadBlocks()
    def CheckInFactoryMarkedBadBlockFile(self,phyAddress,listToDumpFile224Buffer=[],logicalPlanesToConsider=True):
        """
        Name:           CheckInFactoryMarkedBadBlockFile()
        Description:    Checks whether the block marked as bad has registered in FACTORY_MARKED_BAD_BLOCK_FILE as
                        a bad block or not
        Arguments:
           card:        card Object
           phyAddress:  Physical address of block that need to be checked in FACTORY_MARKED_BAD_BLOCK_FILE
        Returns:
           True:        If the block number is registered as a bad block in the FACTORY_MARKED_BAD_BLOCK_FILE
           False:       If the block number is not registered as a bad block in the FACTORY_MARKED_BAD_BLOCK_FILE
        """

        import math
        NO_OF_BITS_IN_A_BYTE = 8


        chipsPerBank = self.__fwConfigData.numChips
        blocksPerPlane = self.__fwConfigData.blocksPerPlane
        planesPerDie = self.__fwConfigData.planesPerDie
        planesPerChip = self.__fwConfigData.planesPerChip
        noOfBanks = self.__fwConfigData.numOfBanks
        numOfLogicalPlanesPerPlane = 1

        fileSizeInSectors, fileSizeInBytes = DiagnosticLib.LengthOfFileInBytes(fileId=Constants.FS_Config_CONSTANTS.IFS_FACTORY_MARKED_BAD_BLOCK_FILE_ID)
        rBuf = DiagnosticLib.ReadFileSystem(self.vtfContainer, fileID=Constants.FS_Config_CONSTANTS.IFS_FACTORY_MARKED_BAD_BLOCK_FILE_ID, sectorCount=fileSizeInSectors)
        IFS_FILE_VERSION_LENGTH = Constants.FS_Config_CONSTANTS.IFS_FILE_VERSION_LENGTH

        bytesPerPlane = old_div((self.__fwConfigData.blocksPerPlane+7),NO_OF_BITS_IN_A_BYTE)

        byte = IFS_FILE_VERSION_LENGTH +\
                   (phyAddress.chip * self.__fwConfigData.diesPerChip * planesPerDie * bytesPerPlane) +\
                   (phyAddress.die * planesPerDie * bytesPerPlane) +\
                   (phyAddress.plane * numOfLogicalPlanesPerPlane * bytesPerPlane) +\
                   (old_div(phyAddress.block,NO_OF_BITS_IN_A_BYTE))

        # Each bank reserves 17 sectors for its bitmap data.
        if ((old_div(phyAddress.chip, chipsPerBank)) > 0):
            byte = byte + phyAddress.bank * 17 * DiagnosticLib.BE_SPECIFIC_BYTES_PER_SECTOR


        mask = pow(2,(phyAddress.block % NO_OF_BITS_IN_A_BYTE))
        if (rBuf.GetOneByteToInt(int(byte)) & mask):
            return True
        else:
            listToDumpFile224Buffer.append(rBuf)
            return False

    #End of CheckInFactoryMarkedBadBlockFile

    def __GetNextPowOf2(self,num):
        """
        Name : __GetNextPowOf2
        Deescription :   Calculates the next Power of 2 for the given number
        Argument :
             NUM     :   number for which next power fo 2 has to be calculated
        Return :
             Return next power of 2 to the specified number
        """
        count = 0
        while num>1:
            num = num >> 1
            count = count + 1
        return pow(2, count + 1)
    #End of GetNextPowOf2


    def MarkBadBlocksinROMVisibleBlocks(self, pattern,botFilename='',paramsfilepath=None, maxLba=0, retval=0):
        badblockList = []
        BadBlockCountPerPlane = {}
        for die in range(self.__fwConfigData.dieInterleave):
            for plane in range(self.__fwConfigData.planeInterleave):
                BadBlockCountPerPlane[(die, plane)] = 0

        self.logger.Info("", "[BadBlockLib: MarkBadBlocksInROMVisibleBlocks] Bad block pattern selected (in ROM visibility) - %s"%pattern)
        romVisibleBlockList = self.GetROMVisibleBlocks()
        totalBadBlockCount = 0
        # Account for max allowed bad blocks per plane while marking bad blocks as per the pattern
        maxBadBlockAdjust = max(0, (len(romVisibleBlockList) - self.__NoOfGoodBlocksinROMVisible) - (self.__fwConfigData.planesPerChip * self.__FileDataObj.maxBadBlockCount))
        if pattern == "FIRST_12_GOOD":
            blockstoMarkBadBlock = romVisibleBlockList[self.__NoOfGoodBlocksinROMVisible + maxBadBlockAdjust:]
            for i in range(0, len(blockstoMarkBadBlock)):
                phyAdd = AddressTypes.PhysicalAddress()
                phyAdd.chip  = blockstoMarkBadBlock[i][0]
                phyAdd.die   = blockstoMarkBadBlock[i][1]
                phyAdd.plane = blockstoMarkBadBlock[i][2]
                phyAdd.block = blockstoMarkBadBlock[i][3]

                badblockList.append(phyAdd)
                BadBlockCountPerPlane[(phyAdd.die, phyAdd.plane)] += 1
                totalBadBlockCount += 1
                self.logger.Info("", "[BadBlockLib: MarkBadBlocksInROMVisibleBlocks] Block selected: %s"%phyAdd)
                self.logger.Info("", "[BadBlockLib: MarkBadBlocksInROMVisibleBlocks] TotalBadBlockCount: %d, TotalBadBlockCountPerPlane: %d"%(totalBadBlockCount, BadBlockCountPerPlane[(phyAdd.die, phyAdd.plane)]))

        elif pattern == "LAST_12_GOOD":
            blockstoMarkBadBlock = romVisibleBlockList[:-(self.__NoOfGoodBlocksinROMVisible + maxBadBlockAdjust)]
            for i in range(0, len(blockstoMarkBadBlock)):
                phyAdd = AddressTypes.PhysicalAddress()
                phyAdd.chip  = blockstoMarkBadBlock[i][0]
                phyAdd.die   = blockstoMarkBadBlock[i][1]
                phyAdd.plane = blockstoMarkBadBlock[i][2]
                phyAdd.block = blockstoMarkBadBlock[i][3]

                badblockList.append(phyAdd)
                BadBlockCountPerPlane[(phyAdd.die, phyAdd.plane)] += 1
                totalBadBlockCount += 1
                self.logger.Info("", "[BadBlockLib: MarkBadBlocksInROMVisibleBlocks] Block selected: %s"%phyAdd)
                self.logger.Info("", "[BadBlockLib: MarkBadBlocksInROMVisibleBlocks] TotalBadBlockCount: %d, TotalBadBlockCountPerPlane: %d"%(totalBadBlockCount, BadBlockCountPerPlane[(phyAdd.die, phyAdd.plane)]))

        elif pattern == "RANDOM_12_GOOD":
            blockstoMarkBadBlock = romVisibleBlockList
            randomgoodblock = self.__randomObj.sample(romVisibleBlockList[self.__NoOfGoodBlocksinROMVisible:-self.__NoOfGoodBlocksinROMVisible], self.__NoOfGoodBlocksinROMVisible + maxBadBlockAdjust)
            for i in range(0, len(randomgoodblock)):
                if randomgoodblock[i] in romVisibleBlockList:
                    blockstoMarkBadBlock.remove(randomgoodblock[i])

            for i in range(0, len(blockstoMarkBadBlock)):
                phyAdd = AddressTypes.PhysicalAddress()
                phyAdd.chip  = blockstoMarkBadBlock[i][0]
                phyAdd.die   = blockstoMarkBadBlock[i][1]
                phyAdd.plane = blockstoMarkBadBlock[i][2]
                phyAdd.block = blockstoMarkBadBlock[i][3]

                badblockList.append(phyAdd)
                BadBlockCountPerPlane[(phyAdd.die, phyAdd.plane)] += 1
                totalBadBlockCount += 1
                self.logger.Info("", "[BadBlockLib: MarkBadBlocksInROMVisibleBlocks] Block selected: %s"%phyAdd)
                self.logger.Info("", "[BadBlockLib: MarkBadBlocksInROMVisibleBlocks] TotalBadBlockCount: %d, TotalBadBlockCountPerPlane: %d"%(totalBadBlockCount, BadBlockCountPerPlane[(phyAdd.die, phyAdd.plane)]))

        elif pattern == "WORST_CASE":
            #Inject 126 Badblocks
            blockstoMarkBadBlock = romVisibleBlockList
            for i in range(0, ROM_VISIBLE_BLOCKS - 2):
                phyAdd = AddressTypes.PhysicalAddress()
                phyAdd.chip  = blockstoMarkBadBlock[i][0]
                phyAdd.die   = blockstoMarkBadBlock[i][1]
                phyAdd.plane = blockstoMarkBadBlock[i][2]
                phyAdd.block = blockstoMarkBadBlock[i][3]

                badblockList.append(phyAdd)
                BadBlockCountPerPlane[(phyAdd.die, phyAdd.plane)] += 1
                totalBadBlockCount += 1
                self.logger.Info("", "[BadBlockLib: MarkBadBlocksInROMVisibleBlocks] Block selected: %s"%phyAdd)
                self.logger.Info("", "[BadBlockLib: MarkBadBlocksInROMVisibleBlocks] TotalBadBlockCount: %d, TotalBadBlockCountPerPlane: %d"%(totalBadBlockCount, BadBlockCountPerPlane[(phyAdd.die, phyAdd.plane)]))

        if retval:
            return badblockList, BadBlockCountPerPlane

        # Marking the block bad
        self.MarkBadBlocks(badblockList,botFilename,paramsfilepath,maxLba,disableBlockRelinkVerification=True)

    def GetROMVisibleBlocks(self):
        #Ex: Assuming we have 2D, 4P memory, then boot block search happens as shown (Limited to CE0)
        #D0                #D1
        #P0  P1  P2  P3     P0  P1  P2  P3
        #0   1   2   3      4   5   6   7
        #8   9   10  11     12  13  14  15
        #Author: Shaheed Nehal A

        global ROM_VISIBLE_BLOCKS
        ROMVisibleBlocksList = []
        DieConfig = self.__fwConfigData.diesPerChip
        planeConfig  = self.__fwConfigData.planesPerDie
        numberOfMetaPlane = self.__fwConfigData.numberOfMetaPlane
        BootBlockSearchCounter = 0
        blockNo = 0
        curMetaPlaneNo, multiMetaPlane = 0, 0
        chip=0 #ROM visibility is restricted to CE0
        while (BootBlockSearchCounter < ROM_VISIBLE_BLOCKS):
            for die in range(DieConfig):
                if len(ROMVisibleBlocksList) == ROM_VISIBLE_BLOCKS:
                    break
                multiMetaPlane  = old_div(((chip * DieConfig) + die), self.__fwConfigData.dieInterleave)
                if multiMetaPlane != curMetaPlaneNo:
                    curMetaPlaneNo = multiMetaPlane
                    blockNo+=1
                for plane in range(planeConfig):
                    ROMVisibleBlocksList.append((chip, die, plane, blockNo))
                    BootBlockSearchCounter += 1
                    if len(ROMVisibleBlocksList) == ROM_VISIBLE_BLOCKS:
                        break
            if (multiMetaPlane == numberOfMetaPlane) or (numberOfMetaPlane == 1):
                blockNo+=1
        return ROMVisibleBlocksList

    def RemoveExcessBadBlocksFromAllPlanes(self, BadBlockCountPerPlane, badBlocklist_InROMVisibility, BadBlockCountPerPlane_InROMVisibility, BadBlockList):
        #After injecting BBs from ROM visibility, there might be excess BBs in some planes, this API will remove them
        #Author: Shaheed Nehal A

        global ROM_VISIBLE_BLOCKS
        ExcessBadBlockCountPerPlane = {}
        BadBlocksToRemove = []
        for die in range(self.__fwConfigData.dieInterleave):
            for plane in range(self.__fwConfigData.planeInterleave):
                BadBlockCountPerPlane[(die, plane)] += BadBlockCountPerPlane_InROMVisibility[(die, plane)]
                if BadBlockCountPerPlane[(die, plane)] > self.__FileDataObj.maxBadBlockCount:
                    ExcessBadBlockCountPerPlane[(die, plane)] = BadBlockCountPerPlane[(die, plane)] - self.__FileDataObj.maxBadBlockCount

                    self.logger.Info("", "Excess Bad Blocks in die: 0x%X, plane: 0x%X --> %d"%(die, plane, ExcessBadBlockCountPerPlane[(die, plane)]))
                    for badBlockCount in range(ExcessBadBlockCountPerPlane[(die, plane)]):
                        random.shuffle(BadBlockList)
                        for badBlock in BadBlockList:
                            if badBlock.die == die and badBlock.plane == plane and badBlock not in BadBlocksToRemove:
                                BadBlocksToRemove.append(badBlock)
                                break

        for badblock in BadBlocksToRemove:
            self.logger.Info("", "[BadBlockLib: Block removed from BadBlockList - %s]"%badblock)
            BadBlockList.remove(badblock)
            BadBlockCountPerPlane[(badblock.die, badblock.plane)] -= 1

        self.logger.Info("", "Total BadBlocks to mark (excluding the blocks in ROM visibility) %d"%len(BadBlockList))
        BadBlockList = BadBlockList + badBlocklist_InROMVisibility
        self.logger.Info("", "Total BadBlocks to mark (including the blocks in ROM visibility) - %d"%len(BadBlockList))
        return BadBlockList, BadBlockCountPerPlane

    def MarkRandomBadBlocks(self,badBlockCount,
                            botFilename = '',
                            paramsfilepath = None,
                            maxLba=0,
                            disableBBVerification=False):
        """
         Name :  MarkRandomBadBlocks
         Description :
                    Mark N(given by user in commndline options ) bad blocks
         Arguments :
                 badBlockCount: Number of Bad blocks to mark
                 botFilename :  Bot file PATH
                 paramsfilepath : parameter file path
                 maxLba      :  Max LBA to Format
        Return   :
            None

        """

        logger = self.logger
        # check number of bad block given by user should not exceed the maximum number of bad blocks
        #assert badBlockCount <= MAX_BADBLOCKS_PER_CARD, "Maximum number of Bad Blocks in a Card is %d"%MAX_BADBLOCKS_PER_CARD

        #Get Physical information of card
        numOfChips      = self.__fwConfigData.numChips * self.__fwConfigData.numOfBanks
        diesPerChip     = self.__fwConfigData.diesPerChip
        planesPerDie    = self.__fwConfigData.planesPerDie
        blocksPerPlane  = self.__fwConfigData.blocksPerPlane
        totalDiesInCard = numOfChips*diesPerChip
        numberOfMetaPlane = self.__fwConfigData.numberOfMetaPlane
        diesPerMMP      = old_div(totalDiesInCard,numberOfMetaPlane)
        planesPerMMP    = diesPerMMP*self.__fwConfigData.planeInterleave

        if self.__optionValues.numberOfDiesInCard == 6 or self.__optionValues.numberOfDiesInCard == 12: #This is just a workaround till FW diag is changed to give right value
            numberOfMetaPlane = 3
            #badBlockCount = 92

        #initialise the badBlock list
        badBlockList = []
        BadBlockCountPerPlane = {}
        self.BBsMarkedByFW = []

        #RANDOM_BLOCKS        --> In each plane, the block num would be uniquely picked. But 2 different planes might have same block bad.
        #RANDOM_UNIQUE_BLOCKS --> In each metaplane, the block picked for marking would be unique.
                                  #This pattern would only work if maxBBPerPlane*NoOfPlanesIn1MMP < totalBlocksIn1Plane
        #ROM_VISIBLE_MAX_IMBALANCE --> Rom visible blocks (Boot/FS) are Single Plane blocks. Chip0 (first 4 dies) would have these blocks.
                                       #This pattern would have imbalance BB pattern in only first 4 dies, while the other dies would have
                                       #same pattern as RANDOM_BLOCKS
        #MORE_THAN_MAX_IN_ONE_ZONE --> FBBs in 1 random zone would be more than 'per zone' limit (in all dies)
        #

        if self.isReducedCap:
            #Gets the expected list of blocks to be marked bad by FW while reducing capacity --> based on Zone Based Bad Block Marking scheme
            self.BBsMarkedByFW = self.CheckFWMarkingToReduceCapacity()

        BadBlockPatternList = ["RANDOM_BLOCKS", "RANDOM_UNIQUE_BLOCKS"]

        #if self.isReducedCap:
            #BadBlockPatternList.extend(["MORE_THAN_MAX_IN_ONE_ZONE", "MORE_THAN_MAX_IN_RANDOM_ZONES", "MORE_FBBS_IN_INITIAL_ZONES", "MORE_FBBS_IN_LATER_ZONES"])

        #Remove RANDOM_UNIQUE_BLOCKS if num of good blocks < num of unique blocks to mark bad in a metaplane
        #Total good blocks in each plane = 3660-3304 = 356
        #Max BB limit per plane = 64. Total planes in a metaplane is 8. So we need 8*64=512 unique blocks which is more than available good blocks 356.
        numOfDiesInAMetaplane = old_div((self.__fwConfigData.diesPerChip*self.__fwConfigData.numChips),(self.__fwConfigData.numberOfMetaPlane-self.__fwConfigData.dummyMetaPlane))
        numOfPlanesInAMetaplane = numOfDiesInAMetaplane*self.__fwConfigData.planesPerDie
        numOfUniqueBlocksNeededIn1Metaplane = numOfPlanesInAMetaplane*self.__FileDataObj.maxBadBlockCount
        numOfAvailableGoodBlocksForMarking = self.__fwConfigData.blocksPerDie - self.__file14Object["TotalBadBlocksRequiredPerDie"]
        if self.isReducedCap and numOfUniqueBlocksNeededIn1Metaplane > numOfAvailableGoodBlocksForMarking:
            self.logger.Warning("", "[Test: Warning] Removing RANDOM_UNIQUE_BLOCKS pattern as numOfUniqueBlocksNeededIn1Metaplane=%d is more than numOfAvailableGoodBlocksForMarking=%d"%(numOfUniqueBlocksNeededIn1Metaplane,numOfAvailableGoodBlocksForMarking))
            BadBlockPatternList.remove("RANDOM_UNIQUE_BLOCKS")

        ##In AP EI, we inject 10 BBs, but imbalance pattern will do +12, -12 --> leading to -ve values. Hence avoiding imbalancing in such cases
        #if badBlockCount != self.__FileDataObj.maxBadBlockCount:
            #BadBlockPatternList.remove("ROM_VISIBLE_MAX_IMBALANCE")

        if self.__optionValues.BadBlockPattern == "MAX_BAD_BLOCKS":
            case = self.__randomObj.choice(BadBlockPatternList)
        else:
            case = self.__optionValues.BadBlockPattern
            if case not in BadBlockPatternList:
                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Unhandled --BadBlockPattern received")

        #case = "MORE_THAN_MAX_IN_ONE_ZONE"
        logger.Info("","[BadBlock Pattern] %s is chosen for making factory marked bad blocks"%(case))
        totalBadBlockCount = 0

        if case == "RANDOM_BLOCKS":
            for chip in range (0, numOfChips):
                for die in range (0, diesPerChip):
                    BBsinDie = []
                    multiMetaPlane  = old_div(((chip * diesPerChip) + die), self.__fwConfigData.dieInterleave)
                    self.logger.SmallBanner("Current MetaPlane: %d"%multiMetaPlane)
                    if multiMetaPlane == numberOfMetaPlane:
                        break
                    totalBadBlockCountPerPlane = 0
                    for plane in range (0, planesPerDie):
                        totalBadBlockCountPerPlane = 0
                        BadBlockCountPerPlane[(chip, die, plane)] = 0
                        badBlockPerPlane = badBlockCount
                        chosenBlockList = []

                        if self.isReducedCap and not self.__optionValues.checkZoneBasedBBInjection:
                            #In reduced cap, FW would have marked some blocks as bad already --> so picking only available good blocks
                            blocksMarkedByFWAsBadInCurrentPlane = []
                            for phyAddr in self.BBsMarkedByFW:
                                if phyAddr.chip == chip and phyAddr.die == die and phyAddr.plane == plane:
                                    blocksMarkedByFWAsBadInCurrentPlane.append(phyAddr.block)
                            #Removing first 10 phy blocks to avoid marking ROM visible blocks bad
                            goodBlocksInCurrentPlane = list(set(range(self.__fwConfigData.blocksPerPlane)) - set(blocksMarkedByFWAsBadInCurrentPlane) - set(range(10)))
                            if len(goodBlocksInCurrentPlane) < self.__FileDataObj.maxBadBlockCount:
                                self.logger.Error("", "[Test: Error] Available good blocks for marking in current plane: %d"%ken(goodBlocksInCurrentPlane))
                                self.logger.Error("", "[Test: Error] Max BB limit per plane: %d"%self.__FileDataObj.maxBadBlockCount)
                                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Available good blocks for marking bad < per plane limit. Cannot mark FBBs")

                        while badBlockPerPlane > 0:
                            if self.isReducedCap and not self.__optionValues.checkZoneBasedBBInjection:
                                #This makes sure the block picking happens quickly (if not, there will be too many BB hits due to FW marking and the loop would run much longer)
                                block = self.__randomObj.choice(goodBlocksInCurrentPlane)
                            else:
                                block = self.__randomObj.randint(10, blocksPerPlane - 1)
                            physicalAddress = AddressTypes.PhysicalAddress()
                            physicalAddress.chip    = chip
                            physicalAddress.die     = die
                            physicalAddress.plane   = plane
                            physicalAddress.block   = block
                            physicalAddress.wordLine  = 0
                            physicalAddress.mlcLevel  = 0
                            physicalAddress.eccPage = 0
                            if self.__fwConfigData.isBiCS:
                                physicalAddress.string  = 0
                            if self.isReducedCap and self.__optionValues.checkZoneBasedBBInjection:
                                isBadBlock = False
                            else:
                                isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
                            if not isBadBlock and (block not in (chosenBlockList)) :
                                badBlockList.append(physicalAddress)
                                chosenBlockList.append(block)
                                if self.isReducedCap and not self.__optionValues.checkZoneBasedBBInjection:
                                    goodBlocksInCurrentPlane.remove(block)
                                badBlockPerPlane = badBlockPerPlane - 1
                                totalBadBlockCount = totalBadBlockCount + 1
                                totalBadBlockCountPerPlane = totalBadBlockCountPerPlane + 1
                                BadBlockCountPerPlane[(chip, die, plane)] += 1
                                DieBlockNum = block*self.__fwConfigData.planesPerDie + plane
                                if DieBlockNum in BBsinDie:
                                    raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Die Block Num repeated - not expected")
                                BBsinDie.append(DieBlockNum)
                                logger.Info("", "[ TotalBadBlockCount : %d TotalBadBlockCountPerPlane : %d ] Die Block Num: %d -->  Block selected %s"%(totalBadBlockCount, totalBadBlockCountPerPlane, DieBlockNum, physicalAddress))
                    BBsinDie.sort()
                    self.logger.Info("", "[Test: BBsInDie] chip: 0x%X, die: 0x%X --> %s"%(chip, die, BBsinDie))

        elif case == "RANDOM_UNIQUE_BLOCKS":
            totalBadBlockCount = 0
            #Works only if maxBBPerPlane*NoOfPlanesIn1MMP < totalBlocksIn1Plane, raising an assert if calculation doesn't hold good
            if badBlockCount*planesPerMMP > blocksPerPlane:
                self.logger.Error("", "[Test: Error] Max BB limit per plane = %d"%badBlockCount)
                self.logger.Error("", "[Test: Error] Total planes in 1 MMP = %d"%planesPerMMP)
                self.logger.Error("", "[Test: Error] Max BB limit per MMP = %d x %d = %d"%(badBlockCount, planesPerDie, badBlockCount*planesPerDie))
                self.logger.Error("", "[Test: Error] Total blocks per plane = %d"%blocksPerPlane)
                self.logger.Error("", "[Test: Error] RANDOM_UNIQUE_BLOCKS pattern will mark unique blocks in a metaplane, since max BB limit per MMP > total Block count, this is not applicable")
                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "RANDOM_UNIQUE_BLOCKS pattern is not applicable")

            chosenMultiMetaPlane = []
            for chip in range (0, numOfChips):
                for die in range (0, diesPerChip):
                    BBsinDie = []
                    multiMetaPlane  = old_div(((chip * diesPerChip) + die), self.__fwConfigData.dieInterleave)
                    self.logger.SmallBanner("Current MetaPlane: %d"%multiMetaPlane)
                    if multiMetaPlane == numberOfMetaPlane:
                        break

                    if multiMetaPlane not in chosenMultiMetaPlane:
                        chosenBlockListInAMetaplane = []
                        chosenMultiMetaPlane.append(multiMetaPlane)

                    totalBadBlockCountPerPlane = 0
                    for plane in range (0, planesPerDie):
                        totalBadBlockCountPerPlane = 0
                        BadBlockCountPerPlane[(chip, die, plane)] = 0
                        badBlockPerPlane = badBlockCount
                        chosenBlockList = []

                        if self.isReducedCap and not self.__optionValues.checkZoneBasedBBInjection:
                            blocksMarkedByFWAsBadInCurrentPlane = []
                            for phyAddr in self.BBsMarkedByFW:
                                if phyAddr.chip == chip and phyAddr.die == die and phyAddr.plane == plane:
                                    blocksMarkedByFWAsBadInCurrentPlane.append(phyAddr.block)

                            #Removing first 10 phy blocks to avoid marking ROM visible blocks bad
                            goodBlocksInCurrentPlane = list(set(range(self.__fwConfigData.blocksPerPlane)) - set(blocksMarkedByFWAsBadInCurrentPlane) - set(range(10)))
                            if len(goodBlocksInCurrentPlane) < self.__FileDataObj.maxBadBlockCount:
                                self.logger.Error("", "[Test: Error] Available good blocks for marking in current plane: %d"%ken(goodBlocksInCurrentPlane))
                                self.logger.Error("", "[Test: Error] Max BB limit per plane: %d"%self.__FileDataObj.maxBadBlockCount)
                                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Available good blocks for marking bad < per plane limit. Cannot mark FBBs")

                        while badBlockPerPlane > 0:
                            if self.isReducedCap and not self.__optionValues.checkZoneBasedBBInjection:
                                #This makes sure the block picking happens quickly (if not, there will be too many BB hits due to FW marking and the loop would run much longer)
                                block = self.__randomObj.choice(goodBlocksInCurrentPlane)
                            else:
                                block = self.__randomObj.randint(10, blocksPerPlane - 1)
                            physicalAddress = AddressTypes.PhysicalAddress()
                            physicalAddress.chip    = chip
                            physicalAddress.die     = die
                            physicalAddress.plane   = plane
                            physicalAddress.block   = block
                            physicalAddress.wordLine  = 0
                            physicalAddress.mlcLevel  = 0
                            physicalAddress.eccPage = 0
                            if self.__fwConfigData.isBiCS:
                                physicalAddress.string  = 0
                            if self.isReducedCap and self.__optionValues.checkZoneBasedBBInjection:
                                isBadBlock = False
                            else:
                                isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
                            if not isBadBlock and (block not in (chosenBlockList)) and (block not in (chosenBlockListInAMetaplane)) :
                                badBlockList.append(physicalAddress)
                                chosenBlockList.append(block)
                                chosenBlockListInAMetaplane.append(block)
                                badBlockPerPlane = badBlockPerPlane - 1
                                totalBadBlockCount = totalBadBlockCount + 1
                                totalBadBlockCountPerPlane = totalBadBlockCountPerPlane + 1
                                BadBlockCountPerPlane[(chip, die, plane)] += 1
                                DieBlockNum = block*self.__fwConfigData.planesPerDie + plane
                                if DieBlockNum in BBsinDie:
                                    raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Die Block Num repeated - not expected")
                                logger.Info("", "[ TotalBadBlockCount : %d TotalBadBlockCountPerPlane : %d ] Die Block Num: %d -->  Block selected %s"%(totalBadBlockCount, totalBadBlockCountPerPlane, DieBlockNum, physicalAddress))

                    BBsinDie.sort()
                    self.logger.Info("", "[Test: BBsInDie] chip: 0x%X, die: 0x%X --> %s"%(chip, die, BBsinDie))

        elif case == "ROM_VISIBLE_MAX_IMBALANCE":
            totalBadBlockCount = 0
            #Only 1st chip should have the ROM visible blocks (SPBBs) --> Hence creating imbalance in all dies of first chip only
            #12 SPBBs are available, these can be distributed across first chip (4 dies)
            #Ex: Valid pattern:
            #Chip0. Die0. P0 --> max+8
            #Chip0. Die1. P1 --> max+4
            #Chip0. Die0. P3 --> max-4
            #Chip0. Die2. P2 --> max-4
            #Chip0. Die3. P1 --> max-4

            #Inject more than max first
            chip = 0
            ImbalanceCountInfo_MoreThanMax = {}
            diesWithImbalance_MoreThanMax = sorted(self.__randomObj.sample(list(range(self.__fwConfigData.diesPerChip)), self.__randomObj.randint(1, self.__fwConfigData.diesPerChip)))
            for die in diesWithImbalance_MoreThanMax:
                planesWithImbalance = sorted(self.__randomObj.sample(list(range(self.__fwConfigData.planeInterleave)), self.__randomObj.randint(1, self.__fwConfigData.planeInterleave)))
                ImbalanceCountInfo_MoreThanMax[die] = {}
                for plane in planesWithImbalance:
                    ImbalanceCountInfo_MoreThanMax[die][plane] = 0

            planeLevelEICount = 0
            BadBlocksToInject = self.__NoOfGoodBlocksinROMVisible
            for die in list(ImbalanceCountInfo_MoreThanMax.keys()):
                if BadBlocksToInject <= 0:
                    break
                for plane in ImbalanceCountInfo_MoreThanMax[die]:
                    if BadBlocksToInject <= 0:
                        break
                    planeLevelEICount = self.__randomObj.randint(1, BadBlocksToInject)
                    BadBlocksToInject -= planeLevelEICount
                    ImbalanceCountInfo_MoreThanMax[die][plane] = planeLevelEICount

            if BadBlocksToInject > 0:
                ImbalanceCountInfo_MoreThanMax[die][plane] = planeLevelEICount + BadBlocksToInject

            self.logger.Info("", "[BadBlockLib][MoreThanMax] Excess BBs to be injected across the first chip --> %d"%self.__NoOfGoodBlocksinROMVisible)
            for die in list(ImbalanceCountInfo_MoreThanMax.keys()):
                for plane in ImbalanceCountInfo_MoreThanMax[die]:
                    if ImbalanceCountInfo_MoreThanMax[die][plane] != 0:
                        self.logger.Info("", "[BadBlockLib][MoreThanMax] Chip: 0x%X, Die: 0x%X, Plane: 0x%X --> No of extra BBs: %d"%(chip, die, plane, ImbalanceCountInfo_MoreThanMax[die][plane]))

            #Inject less than max next
            chip = 0
            ImbalanceCountInfo_LessThanMax = {}
            diesWithImbalance_LessThanMax = list(range(self.__fwConfigData.diesPerChip)) #sorted(self.__randomObj.sample(range(self.__fwConfigData.diesPerChip), self.__randomObj.randint(1, self.__fwConfigData.diesPerChip)))
            for die in diesWithImbalance_LessThanMax:
                planesWithImbalance = sorted(self.__randomObj.sample(list(range(self.__fwConfigData.planeInterleave)), self.__randomObj.randint(1, self.__fwConfigData.planeInterleave)))
                ImbalanceCountInfo_LessThanMax[die] = {}
                if die in list(ImbalanceCountInfo_MoreThanMax.keys()) and list(ImbalanceCountInfo_MoreThanMax[die].keys()) != list(range(self.__fwConfigData.planeInterleave)):
                    for plane in planesWithImbalance:
                        #Dont include planes with more than max BBs
                        if die in list(ImbalanceCountInfo_MoreThanMax.keys()):
                            if plane not in list(ImbalanceCountInfo_MoreThanMax[die].keys()):
                                ImbalanceCountInfo_LessThanMax[die][plane] = 0
                        else:
                            ImbalanceCountInfo_LessThanMax[die][plane] = 0

            for die in list(ImbalanceCountInfo_LessThanMax.keys()):
                if list(ImbalanceCountInfo_LessThanMax[die].keys()) == []:
                    for plane in range(self.__fwConfigData.planeInterleave):
                        if die in list(ImbalanceCountInfo_MoreThanMax.keys()):
                            if plane not in list(ImbalanceCountInfo_MoreThanMax[die].keys()):
                                ImbalanceCountInfo_LessThanMax[die][plane] = 0
                        else:
                            ImbalanceCountInfo_LessThanMax[die][plane] = 0
                else:
                    break


            planeLevelEICount = 0
            BadBlocksToInject = self.__NoOfGoodBlocksinROMVisible
            for die in list(ImbalanceCountInfo_LessThanMax.keys()):
                if BadBlocksToInject <= 0 or ImbalanceCountInfo_LessThanMax[die] == {}:
                    del ImbalanceCountInfo_LessThanMax[die]
                    continue
                for plane in ImbalanceCountInfo_LessThanMax[die]:
                    if BadBlocksToInject <= 0:
                        break
                    planeLevelEICount = self.__randomObj.randint(1, BadBlocksToInject)
                    BadBlocksToInject -= planeLevelEICount
                    ImbalanceCountInfo_LessThanMax[die][plane] = 0-planeLevelEICount

            #if ImbalanceCountInfo_LessThanMax.keys() == []:

            lastDie = list(ImbalanceCountInfo_LessThanMax.keys())[-1]
            for plane in list(ImbalanceCountInfo_LessThanMax[lastDie].keys()):
                if ImbalanceCountInfo_LessThanMax[lastDie][plane] == 0:
                    del ImbalanceCountInfo_LessThanMax[lastDie][plane]

            lastPlane = list(ImbalanceCountInfo_LessThanMax[lastDie].keys())[-1]
            if BadBlocksToInject > 0:
                ImbalanceCountInfo_LessThanMax[lastDie][lastPlane] -= BadBlocksToInject

            self.logger.Info("", "[BadBlockLib][LessThanMax] BB count to be subtracted across the first chip --> %d"%self.__NoOfGoodBlocksinROMVisible)
            for die in list(ImbalanceCountInfo_LessThanMax.keys()):
                for plane in ImbalanceCountInfo_LessThanMax[die]:
                    if ImbalanceCountInfo_LessThanMax[die][plane] != 0:
                        self.logger.Info("", "[BadBlockLib][LessThanMax] Chip: 0x%X, Die: 0x%X, Plane: 0x%X --> No of extra BBs: %d"%(chip, die, plane, ImbalanceCountInfo_LessThanMax[die][plane]))

            chip=0
            for die in range (0, diesPerChip):
                multiMetaPlane  = old_div(((chip * self.__fwConfigData.diesPerChip) + die), self.__fwConfigData.dieInterleave)
                self.logger.SmallBanner("Current MetaPlane: %d"%multiMetaPlane)
                if multiMetaPlane == numberOfMetaPlane:
                    break
                totalBadBlockCountPerPlane = 0

                for plane in range (0, planesPerDie):
                    totalBadBlockCountPerPlane = 0
                    BadBlockCountPerPlane[(chip, die, plane)] = 0
                    badBlockPerPlane = badBlockCount
                    #Imbalance pattern
                    if die in list(ImbalanceCountInfo_MoreThanMax.keys()) and plane in ImbalanceCountInfo_MoreThanMax[die]:
                        badBlockPerPlane += ImbalanceCountInfo_MoreThanMax[die][plane]
                    if die in list(ImbalanceCountInfo_LessThanMax.keys()) and plane in ImbalanceCountInfo_LessThanMax[die]:
                        badBlockPerPlane += ImbalanceCountInfo_LessThanMax[die][plane]

                    self.logger.Info("", "[BadBlockLib][EICountPerPlane] Chip: 0x%X, Die: 0x%X, Plane: 0x%X --> %d"%(chip, die, plane, badBlockPerPlane))

                    chosenBlockList = []
                    while badBlockPerPlane > 0:
                        block = self.__randomObj.randint(10, blocksPerPlane - 1)
                        physicalAddress = AddressTypes.PhysicalAddress()
                        physicalAddress.chip    = chip
                        physicalAddress.die     = die
                        physicalAddress.plane   = plane
                        physicalAddress.block   = block
                        physicalAddress.wordLine  = 0
                        physicalAddress.mlcLevel  = 0
                        physicalAddress.eccPage = 0
                        if self.__fwConfigData.isBiCS:
                            physicalAddress.string  = 0
                        if self.isReducedCap and self.__optionValues.checkZoneBasedBBInjection:
                            isBadBlock = False
                        else:
                            isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
                        if not isBadBlock and (block not in (chosenBlockList)) :
                            badBlockList.append(physicalAddress)
                            chosenBlockList.append(block)
                            badBlockPerPlane = badBlockPerPlane - 1
                            totalBadBlockCount = totalBadBlockCount + 1
                            totalBadBlockCountPerPlane = totalBadBlockCountPerPlane + 1
                            BadBlockCountPerPlane[(chip, die, plane)] += 1
                            logger.Info("", "[ TotalBadBlockCount : %d TotalBadBlockCountPerPlane : %d ]  Block selected %s"%(totalBadBlockCount, totalBadBlockCountPerPlane, physicalAddress))

            #Going ahead with RANDOM_BADBLOCKS on all other chips
            for chip in range (1, numOfChips):
                for die in range (0, diesPerChip):
                    multiMetaPlane  = old_div(((chip * diesPerChip) + die), self.__fwConfigData.dieInterleave)
                    self.logger.SmallBanner("Current MetaPlane: %d"%multiMetaPlane)
                    if multiMetaPlane == numberOfMetaPlane:
                        break
                    totalBadBlockCountPerPlane = 0
                    for plane in range (0, planesPerDie):
                        totalBadBlockCountPerPlane = 0
                        BadBlockCountPerPlane[(chip, die, plane)] = 0
                        badBlockPerPlane = badBlockCount
                        chosenBlockList = []
                        self.logger.Info("", "[BadBlockLib][EICountPerPlane] Chip: 0x%X, Die: 0x%X, Plane: 0x%X --> %d"%(chip, die, plane, badBlockPerPlane))

                        while badBlockPerPlane > 0:
                            block = self.__randomObj.randint(10, blocksPerPlane - 1)
                            physicalAddress = AddressTypes.PhysicalAddress()
                            physicalAddress.chip    = chip
                            physicalAddress.die     = die
                            physicalAddress.plane   = plane
                            physicalAddress.block   = block
                            physicalAddress.wordLine  = 0
                            physicalAddress.mlcLevel  = 0
                            physicalAddress.eccPage = 0
                            if self.__fwConfigData.isBiCS:
                                physicalAddress.string  = 0
                            if self.isReducedCap and self.__optionValues.checkZoneBasedBBInjection:
                                isBadBlock = False
                            else:
                                isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
                            if not isBadBlock and (block not in (chosenBlockList)) :
                                badBlockList.append(physicalAddress)
                                chosenBlockList.append(block)
                                badBlockPerPlane = badBlockPerPlane - 1
                                totalBadBlockCount = totalBadBlockCount + 1
                                totalBadBlockCountPerPlane = totalBadBlockCountPerPlane + 1
                                BadBlockCountPerPlane[(chip, die, plane)] += 1
                                logger.Info("", "[ TotalBadBlockCount : %d TotalBadBlockCountPerPlane : %d ]  Block selected %s"%(totalBadBlockCount, totalBadBlockCountPerPlane, physicalAddress))

        elif case == "MORE_THAN_MAX_IN_ONE_ZONE":
            perZoneLimit = self.__file14Object["MaxAllowableBBPerZone"]
            perDieLimit = self.__file14Object["TotalBadBlocksRequiredPerDie"]
            perPlaneLimit = old_div(perDieLimit,self.__fwConfigData.planesPerDie)
            numOfZonesPerDie = self.__file14Object["NoOfZonesPerDie"]
            blocksPerZone, BlockRangesPerZoneInEachDie = self.getBlocksPerZone()
            totalBlocksInDie = old_div(self.__fwConfigData.totalNumPhysicalBlocks,(self.__fwConfigData.numChips*self.__fwConfigData.diesPerChip))
            blocksInEachZone = old_div(totalBlocksInDie,numOfZonesPerDie)
            for chip in range (0, numOfChips):
                for die in range (0, diesPerChip):
                    zoneWithMoreThanMaxLimitFBBs = self.__randomObj.randint(0,numOfZonesPerDie-1)
                    numOfFBBsToInjectInSelectedZone = self.__randomObj.randint(perZoneLimit+1, blocksInEachZone) #More than perzone limit
                    self.logger.Info("", "[Test: Info] Test will inject %d FBBs which is more than per zone limit (of %d) in zone %d of all dies, all chips"%(numOfFBBsToInjectInSelectedZone, perZoneLimit, zoneWithMoreThanMaxLimitFBBs))
                    self.logger.Info("", "[Test: Info] Block range for zone %d --> [%d to %d]"%(zoneWithMoreThanMaxLimitFBBs, BlockRangesPerZoneInEachDie[zoneWithMoreThanMaxLimitFBBs][0], BlockRangesPerZoneInEachDie[zoneWithMoreThanMaxLimitFBBs][1]))

                    FBBsInjected = 0
                    BBsinDie = []
                    testInjectedFBBsInSelectedZone = []
                    for dieBlockAddr in blocksPerZone[zoneWithMoreThanMaxLimitFBBs]:
                        dieBlock = dieBlockAddr.block*self.__fwConfigData.planesPerDie + dieBlockAddr.plane

                        #Skipping first 10 blocks to avoid EI on ROM visible blocks
                        if dieBlock in range(10):
                            continue

                        if (chip, die, dieBlockAddr.plane) not in list(BadBlockCountPerPlane.keys()):
                            BadBlockCountPerPlane[(chip, die, dieBlockAddr.plane)] = 0
                        elif BadBlockCountPerPlane[(chip, die, dieBlockAddr.plane)] >= perPlaneLimit:
                            continue

                        dieBlockAddr.chip = chip
                        dieBlockAddr.die = die
                        badBlockList.append(dieBlockAddr)
                        totalBadBlockCount = totalBadBlockCount + 1
                        BadBlockCountPerPlane[(chip, die, dieBlockAddr.plane)] += 1
                        if dieBlock in BBsinDie:
                            raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Die Block Num repeated - not expected")
                        BBsinDie.append(dieBlock)
                        testInjectedFBBsInSelectedZone.append(dieBlockAddr)
                        logger.Info("", "[ TotalBadBlockCount : %d TotalBadBlockCountPerPlane : %d ] Die Block Num: %d -->  Block selected %s"%(totalBadBlockCount, BadBlockCountPerPlane[(chip, die, dieBlockAddr.plane)], dieBlock, dieBlockAddr))
                        if totalBadBlockCount == numOfFBBsToInjectInSelectedZone:
                            break

                    BBsinDie.sort()
                    self.logger.Info("", "[Test: BBsInDie] chip: 0x%X, die: 0x%X --> %s"%(chip, die, BBsinDie))

        # Marking the block bad
        self.MarkBadBlocks(badBlockList,botFilename,paramsfilepath,maxLba,disableBlockRelinkVerification=disableBBVerification)

        #Check Whether the bad blocks added to Grown badblock list
        for physicalAddress in (badBlockList):
            physicalAddress.wordLine = 0
            physicalAddress.mlcLevel = 0
            physicalAddress.eccPage = 0
            if self.__fwConfigData.isBiCS:
                physicalAddress.string = 0
            isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
            if isBadBlock:
                logger.Info("","[CreateFactoryMarkedBlocksInTheCard] The bad block which was created is found in factory marked badblock file which belongs to Chip no[0x%X],Die no[0x%X],Plane no[0x%X],Block no[0x%X]"
                                 %(physicalAddress.chip,physicalAddress.die,physicalAddress.plane,physicalAddress.block))
            else:
                #logger.Info(" [CreateFactoryMarkedBlocksInTheCard] The bad block which was created is not found in factory marked badblock file which belongs to Chip no[0x%X],Die no[0x%X],Plane no[0x%X],Block no[0x%X]"
                                #%(physicalAddress.chip,physicalAddress.die,physicalAddress.plane,physicalAddress.block))
                logger.Info("",":::ERROR::: Created bad block (chip=0x%X, die=0x%X, plane=0x%X, phy Block = 0x%X) is not found in factory marked badblock file"\
                                                            %(physicalAddress.chip,physicalAddress.die,physicalAddress.plane,physicalAddress.block))
                raise TestError.TestFailError(self.vtfContainer.GetTestName(), ":::ERROR::: Created bad block (chip=0x%X, die=0x%X, plane=0x%X, phy Block = 0x%X) is not found in factory marked badblock file"\
                                                            %(physicalAddress.chip,physicalAddress.die,physicalAddress.plane,physicalAddress.block))

        if self.isReducedCap and self.__optionValues.checkZoneBasedBBInjection:
            self.VerifyReducedCapBBMarking(badBlockList, BadBlockCountPerPlane)

        return badBlockList, BadBlockCountPerPlane
    #end of MarkRandomBadBlocks

    def MarkRandomBadBlocksSinglePlane(self,badBlockCount = None,
                                  botFilename = '',
                                  paramsfilepath = None,
                                  maxLba=0):

        """
         Name :  MarkRandomBadBlocks
         Description :
                    Mark N(given by user in commndline options ) bad blocks
         Arguments :
                 badBlockCount: Number of Bad blocks to mark
                 botFilename :  Bot file PATH
                 paramsfilepath : parameter file path
                 maxLba      :  Max LBA to Format
        Return   :
            None

        """
        #Necessary test objects
        logger = self.__testSpace.GetLogger()
        #Get Physical information of card
        numOfChips      = self.__fwConfigData.numChips * self.__fwConfigData.numOfBanks
        diesPerChip     = self.__fwConfigData.diesPerChip
        planesPerDie    = self.__fwConfigData.planesPerDie
        blocksPerPlane  = self.__fwConfigData.blocksPerPlane

        numberOfMetaPlane = self.__fwConfigData.numberOfMetaPlane
        badBlockCountPlane0 = 0
        badBlockCountPlane1 = 0
        maxBadBlockImbalanceList = [badBlockCount + self.__numGATBlocks,badBlockCount - self.__numGATBlocks]
        maxBadBlockImbalanceInPlane = badBlockCount + self.__numGATBlocks

        fwFeatureConfig = FwConfig.FwFeatureConfig(self.__testSpace) #Since testspace is not required

        #This is just a workaround till FW diag is changed to give right value
        if self.__optionValues.numberOfDiesInCard == 6 or self.__optionValues.numberOfDiesInCard == 12:
            numberOfMetaPlane = 3

        """
        if numberOfMetaPlane > 1 and fwFeatureConfig.isSpcbBadBlockMmpCompensationEnabled:
           SPBadBlockPatternList = ["DIE_MAX_ONEPLANE","DIE_MAX_BAD_BLOCKS","DIE_MAX_IMBALANCE","DIE_RANDOM_IMBALANCE","DIE_LESS_BAD_BLOCKS","META_BLK_IMBALANCE",\
                                  "MMP_MAX_IMBALANCE_MAX_ONEPLANE","MMP_MAX_BAD_BLOCKS_MAX_IMBALANCE","MMP_MAX_IMBALANCE_RANDOM_IMBALANCE","MMP_IMBALANCE","PS_SAME_DIE_PLANE",\
                                  "PS_DIFF_DIE_DIFF_PLANE","PS_SAME_DIE_DIFF_PLANE","PS_DIFF_DIE_SAME_PLANE","MMP_WORST_CASE_IMBALANCE","MMP_MAX_BADBLOCKS_ONEMP", "MMP_MIN_BADBLOCKS_ONEMP"]

        elif numberOfMetaPlane == 1:
           if self.__fwConfigData.diesPerChip > 1:
              SPBadBlockPatternList = ["DIE_MAX_ONEPLANE","DIE_MAX_BAD_BLOCKS","DIE_MAX_IMBALANCE","DIE_RANDOM_IMBALANCE","DIE_LESS_BAD_BLOCKS","META_BLK_IMBALANCE",\
                                       "PS_SAME_DIE_PLANE","PS_DIFF_DIE_DIFF_PLANE","PS_SAME_DIE_DIFF_PLANE","PS_DIFF_DIE_SAME_PLANE"]
           else:
              SPBadBlockPatternList = ["DIE_MAX_ONEPLANE","DIE_MAX_BAD_BLOCKS","DIE_MAX_IMBALANCE","DIE_RANDOM_IMBALANCE","DIE_LESS_BAD_BLOCKS",\
                                      "PS_SAME_DIE_PLANE","PS_SAME_DIE_DIFF_PLANE"]
        """
        SPBadBlockPatternList = ["DIE_MAX_ONEPLANE","DIE_MAX_BAD_BLOCKS","DIE_MAX_IMBALANCE","DIE_RANDOM_IMBALANCE","DIE_LESS_BAD_BLOCKS",\
                                            "PS_SAME_DIE_PLANE","PS_SAME_DIE_DIFF_PLANE"]
        if self.__fwConfigData.diesPerChip > 1:
            SPBadBlockPatternList.extend(["META_BLK_IMBALANCE", "PS_DIFF_DIE_DIFF_PLANE", "PS_DIFF_DIE_SAME_PLANE"])
        if (numberOfMetaPlane > 1) and fwFeatureConfig.isSpcbBadBlockMmpCompensationEnabled:
            SPBadBlockPatternList.extend(["MMP_MAX_IMBALANCE_MAX_ONEPLANE", "MMP_MAX_BAD_BLOCKS_MAX_IMBALANCE", "MMP_MAX_IMBALANCE_RANDOM_IMBALANCE", "MMP_IMBALANCE", \
                                          "MMP_WORST_CASE_IMBALANCE","MMP_MAX_BADBLOCKS_ONEMP", "MMP_MIN_BADBLOCKS_ONEMP"])

        if self.__optionValues.SPBadBlockPattern == "RANDOM":
            initial_pattern = self.__optionValues.SPBadBlockPattern
            self.__optionValues.SPBadBlockPattern = self.__randomObj.choice(SPBadBlockPatternList)


        logger.Info("","Selected Bad Block Pre-condition Pattern :%s"%self.__optionValues.SPBadBlockPattern)
        #Initialise the badBlock list
        badBlockList = []
        totalBadBlockCount = 0
        #Bad block imbalance with in die
        if "DIE" in self.__optionValues.SPBadBlockPattern and "PS" not in self.__optionValues.SPBadBlockPattern:

            if self.__optionValues.SPBadBlockPattern == "DIE_MAX_BAD_BLOCKS":
                badBlockCountPlane0 = badBlockCount
                badBlockCountPlane1 = badBlockCount

            elif self.__optionValues.SPBadBlockPattern == "DIE_MAX_IMBALANCE":
                badBlockCountPlane0 = self.__randomObj.choice(maxBadBlockImbalanceList)
                maxBadBlockImbalanceList.remove(badBlockCountPlane0)
                badBlockCountPlane1 =  self.__randomObj.choice(maxBadBlockImbalanceList)

            elif self.__optionValues.SPBadBlockPattern == "DIE_RANDOM_IMBALANCE":
                badBlockCountPlane0 = self.__randomObj.randint(badBlockCount-self.__numGATBlocks, maxBadBlockImbalanceInPlane-1)
                if badBlockCountPlane0 >= badBlockCount:
                    badBlockCountPlane1 = badBlockCount - (badBlockCountPlane0 - badBlockCount)
                else:
                    badBlockCountPlane1 = badBlockCount + (badBlockCount - badBlockCountPlane0)

            elif self.__optionValues.SPBadBlockPattern == "DIE_LESS_BAD_BLOCKS":
                badBlockCountPlane0 = 10

            elif self.__optionValues.SPBadBlockPattern == "DIE_MAX_ONEPLANE":
                badBlockCountPlane0 = badBlockCount
                badBlockCountPlane1 = 0


            badBlockPerPlaneList = [badBlockCountPlane0,badBlockCountPlane1]
            for chip in range (0, numOfChips):
                #MMP_BB_List_Chosen = False
                for die in range (0, diesPerChip):
                    multiMetaPlane  = old_div(((chip * diesPerChip) + die), self.__fwConfigData.dieInterleave)
                    if self.__optionValues.SPBadBlockPattern == "DIE_MAX_ONEPLANE" and die != 0 :
                        badBlockPerPlaneList = [0,0]
                    if multiMetaPlane == numberOfMetaPlane:
                        break
                    totalBadBlockCountPerPlane = 0
                    for plane in range (0, planesPerDie):
                        totalBadBlockCountPerPlane = 0
                        if self.__optionValues.SPBadBlockPattern == "LESS_BAD_BLOCKS":
                            badBlockPerPlane = self.__randomObj.randint(4, badBlockCountPlane0)
                        else:
                            """
                            if multiMetaPlane>0 and initial_pattern == "RANDOM":
                               if MMP_BB_List_Chosen == False :
                                  MMP_badBlockPerPlaneList = self.__randomObj.choice([badBlockPerPlaneList1,badBlockPerPlaneList2,badBlockPerPlaneList3,badBlockPerPlaneList4])
                                  MMP_BB_List_Chosen = True
                               badBlockPerPlane = MMP_badBlockPerPlaneList[plane]
                            else:
                            """
                            badBlockPerPlane = badBlockPerPlaneList[plane]
                        chosenBlockList = []
                        while badBlockPerPlane > 0:
                            block = self.__randomObj.randint(2, blocksPerPlane - 1)
                            physicalAddress = AddressTypes.PhysicalAddress()
                            physicalAddress.chip    = chip
                            physicalAddress.die     = die
                            physicalAddress.plane   = plane
                            physicalAddress.block   = block
                            physicalAddress.wordLine  = 0
                            physicalAddress.mlcLevel  = 0
                            physicalAddress.eccPage = 0
                            if self.__fwConfigData.isBiCS:
                                physicalAddress.string  = 0
                            isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
                            if not isBadBlock and (block not in (chosenBlockList)) :
                                badBlockList.append(physicalAddress)
                                chosenBlockList.append(block)
                                badBlockPerPlane = badBlockPerPlane - 1
                                totalBadBlockCount = totalBadBlockCount + 1
                                totalBadBlockCountPerPlane = totalBadBlockCountPerPlane + 1
                                logger.Info("","[ TotalBadBlockCount : %d TotalBadBlockCountPerPlane : %d ]  Block selected %s"%(totalBadBlockCount, totalBadBlockCountPerPlane, physicalAddress))

        elif  "MMP" in self.__optionValues.SPBadBlockPattern:
            badBlockPerPlaneList = []
            if self.__optionValues.SPBadBlockPattern == "MMP_MAX_IMBALANCE_MAX_ONEPLANE":


                if numberOfMetaPlane == 2:
                    MMPPatternList = ["MAX_IMBALANCE","MAX_ONEPLANE"]
                elif numberOfMetaPlane == 3:
                    MMPPatternList = ["MAX_IMBALANCE","MAX_ONEPLANE","MAX_IMBALANCE"]
                elif numberOfMetaPlane == 4:
                    MMPPatternList = ["MAX_IMBALANCE","MAX_ONEPLANE","MAX_IMBALANCE","MAX_ONEPLANE"]

                for i in range (0,len(MMPPatternList)):
                    Pattern_Choosen=self.__randomObj.choice(MMPPatternList)
                    MMPPatternList.remove(Pattern_Choosen)
                    if Pattern_Choosen == "MAX_IMBALANCE":
                        badBlockCountPlane0 = self.__randomObj.choice(maxBadBlockImbalanceList)
                        maxBadBlockImbalanceList.remove(badBlockCountPlane0)
                        badBlockCountPlane1 =  self.__randomObj.choice(maxBadBlockImbalanceList)

                        maxBadBlockImbalanceList = [badBlockCount + self.__numGATBlocks,badBlockCount - self.__numGATBlocks]

                    elif Pattern_Choosen == "MAX_ONEPLANE":
                        badBlockCountPlane0 = badBlockCount
                        badBlockCountPlane1 = 0

                    badBlockPerPlaneList.append([badBlockCountPlane0,badBlockCountPlane1])


            elif self.__optionValues.SPBadBlockPattern == "MMP_MAX_BAD_BLOCKS_MAX_IMBALANCE":

                if numberOfMetaPlane == 2:
                    MMPPatternList = ["MAX_IMBALANCE","MAX_BAD_BLOCKS"]
                elif numberOfMetaPlane == 3:
                    MMPPatternList = ["MAX_IMBALANCE","MAX_BAD_BLOCKS","MAX_IMBALANCE"]
                elif numberOfMetaPlane == 4:
                    MMPPatternList = ["MAX_IMBALANCE","MAX_BAD_BLOCKS","MAX_IMBALANCE","MAX_BAD_BLOCKS"]

                for i in range (0,len(MMPPatternList)):
                    Pattern_Choosen=self.__randomObj.choice(MMPPatternList)
                    MMPPatternList.remove(Pattern_Choosen)
                    if Pattern_Choosen == "MAX_IMBALANCE":
                        badBlockCountPlane0 = self.__randomObj.choice(maxBadBlockImbalanceList)
                        maxBadBlockImbalanceList.remove(badBlockCountPlane0)
                        badBlockCountPlane1 =  self.__randomObj.choice(maxBadBlockImbalanceList)

                        maxBadBlockImbalanceList = [badBlockCount + self.__numGATBlocks,badBlockCount - self.__numGATBlocks]

                    elif Pattern_Choosen == "MAX_BAD_BLOCKS":
                        badBlockCountPlane0 = badBlockCount
                        badBlockCountPlane1 = badBlockCount

                    badBlockPerPlaneList.append([badBlockCountPlane0,badBlockCountPlane1])


            elif self.__optionValues.SPBadBlockPattern == "MMP_MAX_IMBALANCE_RANDOM_IMBALANCE":

                if numberOfMetaPlane == 2:
                    MMPPatternList = ["MAX_IMBALANCE","RANDOM_IMBALANCE"]
                elif numberOfMetaPlane == 3:
                    MMPPatternList = ["MAX_IMBALANCE","RANDOM_IMBALANCE","MAX_IMBALANCE"]
                elif numberOfMetaPlane == 4:
                    MMPPatternList = ["MAX_IMBALANCE","RANDOM_IMBALANCE","MAX_IMBALANCE","RANDOM_IMBALANCE"]

                for i in range (0,len(MMPPatternList)):
                    Pattern_Choosen=self.__randomObj.choice(MMPPatternList)
                    MMPPatternList.remove(Pattern_Choosen)
                    if Pattern_Choosen == "MAX_IMBALANCE":
                        badBlockCountPlane0 = self.__randomObj.choice(maxBadBlockImbalanceList)
                        maxBadBlockImbalanceList.remove(badBlockCountPlane0)
                        badBlockCountPlane1 =  self.__randomObj.choice(maxBadBlockImbalanceList)
                        maxBadBlockImbalanceList = [badBlockCount + self.__numGATBlocks,badBlockCount - self.__numGATBlocks]

                    elif Pattern_Choosen == "RANDOM_IMBALANCE":
                        badBlockCountPlane0 = self.__randomObj.randint(badBlockCount-self.__numGATBlocks, maxBadBlockImbalanceInPlane-1)
                        if badBlockCountPlane0 >= badBlockCount:
                            badBlockCountPlane1 = badBlockCount - (badBlockCountPlane0 - badBlockCount)
                        else:
                            badBlockCountPlane1 = badBlockCount + (badBlockCount - badBlockCountPlane0)

                    badBlockPerPlaneList.append([badBlockCountPlane0,badBlockCountPlane1])

            elif self.__optionValues.SPBadBlockPattern == "MMP_IMBALANCE":

                if numberOfMetaPlane == 2:
                    MMPPatternList = ["MAX_BOTH_PLANE_IMBALANCE","MIN_BOTH_PLANE_IMBALANCE"]
                elif numberOfMetaPlane == 3:
                    MMPPatternList = ["MAX_BOTH_PLANE_IMBALANCE","MAX_IMBALANCE","MIN_BOTH_PLANE_IMBALANCE"]
                elif numberOfMetaPlane == 4:
                    MMPPatternList = ["MAX_BOTH_PLANE_IMBALANCE","MIN_BOTH_PLANE_IMBALANCE","MAX_BOTH_PLANE_IMBALANCE","MIN_BOTH_PLANE_IMBALANCE"]

                for i in range (0,len(MMPPatternList)):
                    Pattern_Choosen=self.__randomObj.choice(MMPPatternList)
                    MMPPatternList.remove(Pattern_Choosen)
                    if Pattern_Choosen == "MAX_BOTH_PLANE_IMBALANCE":
                        badBlockCountPlane0 = badBlockCount + self.__numGATBlocks
                        badBlockCountPlane1 = badBlockCount + self.__numGATBlocks

                    elif Pattern_Choosen == "MAX_IMBALANCE":
                        badBlockCountPlane0 = self.__randomObj.choice(maxBadBlockImbalanceList)
                        maxBadBlockImbalanceList.remove(badBlockCountPlane0)
                        badBlockCountPlane1 =  self.__randomObj.choice(maxBadBlockImbalanceList)

                        maxBadBlockImbalanceList = [badBlockCount + self.__numGATBlocks,badBlockCount - self.__numGATBlocks]

                    elif Pattern_Choosen == "MIN_BOTH_PLANE_IMBALANCE":
                        badBlockCountPlane0 = badBlockCount - self.__numGATBlocks
                        badBlockCountPlane1 = badBlockCount - self.__numGATBlocks

                    badBlockPerPlaneList.append([badBlockCountPlane0,badBlockCountPlane1])

            elif self.__optionValues.SPBadBlockPattern == "MMP_MAX_BADBLOCKS_ONEMP":

                if numberOfMetaPlane == 2:
                    MMPPatternList = ["MAX_BOTH_PLANE_IMBALANCE", "NONE"]
                elif numberOfMetaPlane == 3:
                    MMPPatternList = ["MAX_BOTH_PLANE_IMBALANCE", "NONE","NONE"]
                elif numberOfMetaPlane == 4:
                    MMPPatternList = ["MAX_BOTH_PLANE_IMBALANCE", "NONE","NONE","NONE"]

                for i in range (0,len(MMPPatternList)):
                    Pattern_Choosen=self.__randomObj.choice(MMPPatternList)
                    MMPPatternList.remove(Pattern_Choosen)

                    if Pattern_Choosen == "MAX_BOTH_PLANE_IMBALANCE":
                        badBlockCountPlane0 = badBlockCount + self.__numGATBlocks
                        badBlockCountPlane1 = badBlockCount + self.__numGATBlocks

                    elif Pattern_Choosen == "NONE":
                        badBlockCountPlane0 = 0
                        badBlockCountPlane1 = 0

                    badBlockPerPlaneList.append([badBlockCountPlane0,badBlockCountPlane1])

            elif self.__optionValues.SPBadBlockPattern == "MMP_MIN_BADBLOCKS_ONEMP":

                if numberOfMetaPlane == 2:
                    MMPPatternList = ["MIN_BOTH_PLANE_IMBALANCE", "NONE"]
                elif numberOfMetaPlane == 3:
                    MMPPatternList = ["MIN_BOTH_PLANE_IMBALANCE", "NONE","NONE"]
                elif numberOfMetaPlane == 4:
                    MMPPatternList = ["MIN_BOTH_PLANE_IMBALANCE", "NONE","NONE","NONE"]

                for i in range (0,len(MMPPatternList)):
                    Pattern_Choosen=self.__randomObj.choice(MMPPatternList)
                    MMPPatternList.remove(Pattern_Choosen)

                    if Pattern_Choosen == "MIN_BOTH_PLANE_IMBALANCE":
                        badBlockCountPlane0 = badBlockCount - self.__numGATBlocks
                        badBlockCountPlane1 = badBlockCount - self.__numGATBlocks

                    elif Pattern_Choosen == "NONE":
                        badBlockCountPlane0 = 0
                        badBlockCountPlane1 = 0

                    badBlockPerPlaneList.append([badBlockCountPlane0,badBlockCountPlane1])

            elif self.__optionValues.SPBadBlockPattern == "MMP_WORST_CASE_IMBALANCE":

                # Mark badblocks consecutively after 1st 128 blocks in all planes of only one Meta Plane.
                if numberOfMetaPlane == 2:
                    MMPPatternList = ["MAX_BOTH_PLANE_IMBALANCE", "MIN_BOTH_PLANE_IMBALANCE"]
                elif numberOfMetaPlane == 3:
                    MMPPatternList = ["MAX_BOTH_PLANE_IMBALANCE", "MAX_IMBALANCE","MIN_BOTH_PLANE_IMBALANCE"]
                elif numberOfMetaPlane == 4:
                    MMPPatternList = ["MAX_BOTH_PLANE_IMBALANCE", "MIN_BOTH_PLANE_IMBALANCE","MIN_BOTH_PLANE_IMBALANCE","MAX_BOTH_PLANE_IMBALANCE"]

                for i in range (0,len(MMPPatternList)):

                    Pattern_Choosen = MMPPatternList[i]

                    if Pattern_Choosen == "MAX_BOTH_PLANE_IMBALANCE":
                        badBlockCountPlane0 = badBlockCount + self.__numGATBlocks
                        badBlockCountPlane1 = badBlockCount + self.__numGATBlocks

                    elif Pattern_Choosen == "MIN_BOTH_PLANE_IMBALANCE":
                        badBlockCountPlane0 = badBlockCount - self.__numGATBlocks
                        badBlockCountPlane1 = badBlockCount - self.__numGATBlocks

                    elif Pattern_Choosen == "MAX_IMBALANCE":
                        badBlockCountPlane0 = self.__randomObj.choice(maxBadBlockImbalanceList)
                        maxBadBlockImbalanceList.remove(badBlockCountPlane0)
                        badBlockCountPlane1 =  self.__randomObj.choice(maxBadBlockImbalanceList)
                        maxBadBlockImbalanceList = [badBlockCount + self.__numGATBlocks,badBlockCount - self.__numGATBlocks]

                    elif Pattern_Choosen == "NONE":
                        badBlockCountPlane0 = 0
                        badBlockCountPlane1 = 0

                    badBlockPerPlaneList.append([badBlockCountPlane0,badBlockCountPlane1])


            for chip in range (0, numOfChips):
                #MMP_BB_List_Chosen = False
                for die in range (0, diesPerChip):
                    multiMetaPlane  = old_div(((chip * diesPerChip) + die), self.__fwConfigData.dieInterleave)
                    if multiMetaPlane == numberOfMetaPlane:
                        break
                    totalBadBlockCountPerPlane = 0
                    for plane in range (0, planesPerDie):
                        totalBadBlockCountPerPlane = 0
                        badBlockPerPlane = badBlockPerPlaneList[multiMetaPlane][plane]
                        chosenBlockList = []
                        while badBlockPerPlane > 0:
                            if self.__optionValues.SPBadBlockPattern == "MMP_WORST_CASE_IMBALANCE":
                                block = blocksPerPlane-badBlockPerPlane
                            else:
                                block = self.__randomObj.randint(2, blocksPerPlane - 1)
                            physicalAddress = AddressTypes.PhysicalAddress()
                            physicalAddress.chip    = chip
                            physicalAddress.die     = die
                            physicalAddress.plane   = plane
                            physicalAddress.block   = block
                            physicalAddress.wordLine  = 0
                            physicalAddress.mlcLevel  = 0
                            physicalAddress.eccPage = 0
                            if self.__fwConfigData.isBiCS:
                                physicalAddress.string  = 0
                            isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
                            if not isBadBlock and (block not in (chosenBlockList)) :
                                badBlockList.append(physicalAddress)
                                chosenBlockList.append(block)
                                badBlockPerPlane = badBlockPerPlane - 1
                                totalBadBlockCount = totalBadBlockCount + 1
                                totalBadBlockCountPerPlane = totalBadBlockCountPerPlane + 1
                                logger.Info("","[ TotalBadBlockCount : %d TotalBadBlockCountPerPlane : %d ]  Block selected %s"%(totalBadBlockCount, totalBadBlockCountPerPlane, physicalAddress))





        #Bad block imbalance with in meta block
        elif self.__optionValues.SPBadBlockPattern == "META_BLK_IMBALANCE":
            badBlockPerPlaneListTemp = []
            dieInterleave            = self.__fwConfigData.dieInterleave
            numOfPlanesInMetaPlane   = dieInterleave * self.__fwConfigData.planeInterleave
            numPlaneWithMaxBB = 1
            maxBadBlocksInMetaPlane  = numOfPlanesInMetaPlane * badBlockCount
            while (numPlaneWithMaxBB * maxBadBlockImbalanceInPlane < maxBadBlocksInMetaPlane):
                numPlaneWithMaxBB += 1
            numPlaneWithMaxBB        = numPlaneWithMaxBB - 1
            badBlockPerPlaneList     = [maxBadBlockImbalanceInPlane] * numPlaneWithMaxBB
            remainingBadBlocks       = maxBadBlocksInMetaPlane - (maxBadBlockImbalanceInPlane * numPlaneWithMaxBB)
            if dieInterleave > 1:
                badBlocksInOtherPlanes   = remainingBadBlocks
                badBlockPerPlaneList.extend([badBlocksInOtherPlanes])
                remainingPlane = numOfPlanesInMetaPlane - (numPlaneWithMaxBB + 1)
                for i in range(remainingPlane):
                    badBlockPerPlaneList.append(0)

            for chip in range (0, numOfChips):
                for die in range (0, diesPerChip):
                    multiMetaPlane  = old_div(((chip * diesPerChip) + die), self.__fwConfigData.dieInterleave)
                    if multiMetaPlane == numberOfMetaPlane:
                        break
                    if die%dieInterleave == 0:
                        badBlockPerPlaneListTemp = copy.deepcopy(badBlockPerPlaneList)
                    totalBadBlockCountPerPlane = 0
                    for plane in range (0, planesPerDie):
                        totalBadBlockCountPerPlane = 0
                        badBlockPerPlane = self.__randomObj.choice(badBlockPerPlaneListTemp)
                        badBlockPerPlaneListTemp.remove(badBlockPerPlane)
                        chosenBlockList = []
                        while badBlockPerPlane > 0:
                            block = self.__randomObj.randint(2, blocksPerPlane - 1)
                            physicalAddress = AddressTypes.PhysicalAddress()
                            physicalAddress.chip    = chip
                            physicalAddress.die     = die
                            physicalAddress.plane   = plane
                            physicalAddress.block   = block
                            physicalAddress.wordLine  = 0
                            physicalAddress.mlcLevel  = 0
                            physicalAddress.eccPage = 0
                            if self.__fwConfigData.isBiCS:
                                physicalAddress.string  = 0
                            isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
                            if not isBadBlock and (block not in (chosenBlockList)) :
                                badBlockList.append(physicalAddress)
                                chosenBlockList.append(block)
                                badBlockPerPlane = badBlockPerPlane - 1
                                totalBadBlockCount = totalBadBlockCount + 1
                                totalBadBlockCountPerPlane = totalBadBlockCountPerPlane + 1
                                logger.Info("","[ TotalBadBlockCount : %d TotalBadBlockCountPerPlane : %d ]  Block selected %s"%(totalBadBlockCount, totalBadBlockCountPerPlane, physicalAddress))

        #Primary/Secondary block selection
        elif "PS" in self.__optionValues.SPBadBlockPattern:
            dieInterleave            = self.__fwConfigData.dieInterleave
            planeInterLeave          = self.__fwConfigData.planeInterleave
            planeList                = list(range(planeInterLeave))
            dieList                  = list(range(dieInterleave))
            if self.__optionValues.SPBadBlockPattern == "PS_SAME_DIE_PLANE":
                selectedDiePlane = [self.__randomObj.choice(dieList),self.__randomObj.choice(planeList)]
                badBlockOnSelectedPlane = self.__randomObj.randint(5,old_div(badBlockCount,2))
                badBlocksOnOtherPlane = self.__randomObj.randint(badBlockOnSelectedPlane + 6,badBlockCount)
                badBlockPerPlaneList = [[badBlocksOnOtherPlane for i in range(planeInterLeave)] for i in range(dieInterleave)]
                badBlockPerPlaneList[selectedDiePlane[0]][selectedDiePlane[1]] = badBlockOnSelectedPlane

            elif self.__optionValues.SPBadBlockPattern == "PS_SAME_DIE_DIFF_PLANE":
                dieSelected = self.__randomObj.choice(dieList)
                primaryPlane = self.__randomObj.choice(planeList)
                planeList.remove(primaryPlane)
                secondaryPlane = self.__randomObj.choice(planeList)
                badBlockOnPrimaryPlane = self.__randomObj.randint(5,old_div(badBlockCount,2))
                badBlocksOnOtherPlane = self.__randomObj.randint(badBlockOnPrimaryPlane + 6,badBlockCount)
                badBlockPerPlaneList = [[badBlocksOnOtherPlane for i in range(planeInterLeave)] for i in range(dieInterleave)]
                badBlockPerPlaneList[dieSelected][primaryPlane] = badBlockOnPrimaryPlane
                badBlockPerPlaneList[dieSelected][secondaryPlane] = badBlockOnPrimaryPlane + 1

            elif self.__optionValues.SPBadBlockPattern == "PS_DIFF_DIE_SAME_PLANE" and self.__fwConfigData.diesPerChip > 1:
                primaryDie = self.__randomObj.choice(dieList)
                dieList.remove(primaryDie)
                secondaryDie = self.__randomObj.choice(dieList)
                PlaneSelected = self.__randomObj.choice(planeList)
                badBlockOnPrimaryPlane = self.__randomObj.randint(5,old_div(badBlockCount,2))
                badBlocksOnOtherPlane = self.__randomObj.randint(badBlockOnPrimaryPlane + 6,badBlockCount)
                badBlockPerPlaneList = [[badBlocksOnOtherPlane for i in range(planeInterLeave)] for i in range(dieInterleave)]
                badBlockPerPlaneList[primaryDie][PlaneSelected] = badBlockOnPrimaryPlane
                badBlockPerPlaneList[secondaryDie][PlaneSelected] = badBlockOnPrimaryPlane + 1

            elif self.__optionValues.SPBadBlockPattern == "PS_DIFF_DIE_DIFF_PLANE" and self.__fwConfigData.diesPerChip > 1:
                primaryDie = self.__randomObj.choice(dieList)
                dieList.remove(primaryDie)
                secondaryDie = self.__randomObj.choice(dieList)
                primaryPlane = self.__randomObj.choice(planeList)
                planeList.remove(primaryPlane)
                secondaryPlane = self.__randomObj.choice(planeList)
                badBlockOnPrimaryPlane = self.__randomObj.randint(5,old_div(badBlockCount,2))
                badBlocksOnOtherPlane = self.__randomObj.randint(badBlockOnPrimaryPlane + 6,badBlockCount)
                badBlockPerPlaneList = [[badBlocksOnOtherPlane for i in range(planeInterLeave)] for i in range(dieInterleave)]
                badBlockPerPlaneList[primaryDie][primaryPlane] = badBlockOnPrimaryPlane
                badBlockPerPlaneList[secondaryDie][secondaryPlane] = badBlockOnPrimaryPlane + 1
            else :
                logger.Info("","Selected bad block precondition : %s is valid only for multi die configuration")
                return

            for chip in range (0, numOfChips):
                for die in range (0, diesPerChip):
                    multiMetaPlane  = old_div(((chip * diesPerChip) + die), self.__fwConfigData.dieInterleave)
                    if multiMetaPlane == numberOfMetaPlane:
                        break
                    totalBadBlockCountPerPlane = 0
                    for plane in range (0, planesPerDie):
                        totalBadBlockCountPerPlane = 0
                        badBlockPerPlane = badBlockPerPlaneList[die%self.__fwConfigData.dieInterleave][plane]
                        chosenBlockList = []
                        while badBlockPerPlane > 0:
                            block = self.__randomObj.randint(2, blocksPerPlane - 1)
                            physicalAddress = AddressTypes.PhysicalAddress()
                            physicalAddress.chip    = chip
                            physicalAddress.die     = die
                            physicalAddress.plane   = plane
                            physicalAddress.block   = block
                            physicalAddress.wordLine  = 0
                            physicalAddress.mlcLevel  = 0
                            physicalAddress.eccPage = 0
                            if self.__fwConfigData.isBiCS:
                                physicalAddress.string  = 0
                            isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
                            if not isBadBlock and (block not in (chosenBlockList)) :
                                badBlockList.append(physicalAddress)
                                chosenBlockList.append(block)
                                badBlockPerPlane = badBlockPerPlane - 1
                                totalBadBlockCount = totalBadBlockCount + 1
                                totalBadBlockCountPerPlane = totalBadBlockCountPerPlane + 1
                                logger.Info("","[ TotalBadBlockCount : %d TotalBadBlockCountPerPlane : %d ]  Block selected %s"%(totalBadBlockCount, totalBadBlockCountPerPlane, physicalAddress))

        # Marking the block bad
        self.MarkBadBlocks(badBlockList,botFilename,paramsfilepath,maxLba,disableBlockRelinkVerification=True)
        #Check Whether the bad blocks added to Grown badblock list
        for physicalAddress in (badBlockList):
            physicalAddress.wordLine = 0
            physicalAddress.mlcLevel = 0
            physicalAddress.eccPage = 0
            if self.__fwConfigData.isBiCS:
                physicalAddress.string = 0
            isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
            if isBadBlock:
                logger.Info("","[CreateFactoryMarkedBlocksInTheCard] The bad block which was created is found in factory marked badblock file which belongs to Chip no[0x%X],Die no[0x%X],Plane no[0x%X],Block no[0x%X]"
                                 %(physicalAddress.chip,physicalAddress.die,physicalAddress.plane,physicalAddress.block))

            else:
                logger.Info(""," [CreateFactoryMarkedBlocksInTheCard] The bad block which was created is not found in factory marked badblock file which belongs to Chip no[0x%X],Die no[0x%X],Plane no[0x%X],Block no[0x%X]"
                                 %(physicalAddress.chip,physicalAddress.die,physicalAddress.plane,physicalAddress.block))
                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "[CreateFactoryMarkedBlocksInTheCard] Created bad block is not found in factory marked badblock file")
        return
    #end of MarkRandomBadBlocks

    def GetAllBadBlocksInCard(self, chip, die, FBBList, BlockRangesPerZoneInEachDie):
        bbList = {}
        FBBCount = 0
        currentZone = 0
        for dieBlock in range(self.__fwConfigData.blocksPerDie):
            if dieBlock > BlockRangesPerZoneInEachDie[currentZone][1]:
                currentZone+=1
            physicalAddress = AddressTypes.PhysicalAddress()
            physicalAddress.chip    = chip
            physicalAddress.die     = die
            physicalAddress.plane   = dieBlock%self.__fwConfigData.planesPerDie
            physicalAddress.block   = old_div(dieBlock,self.__fwConfigData.planesPerDie)
            physicalAddress.wordLine  = 0
            physicalAddress.mlcLevel  = 0
            physicalAddress.eccPage = 0
            if self.__fwConfigData.isBiCS:
                physicalAddress.string  = 0
            isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
            if isBadBlock:
                isFBB = False
                for addr in FBBList:
                    if addr.chip == physicalAddress.chip and addr.die == physicalAddress.die and addr.plane == physicalAddress.plane and addr.block == physicalAddress.block:
                        if addr.plane not in list(bbList.keys()):
                            bbList[addr.plane] = []
                        bbList[addr.plane].append("Z" + str(currentZone) + "-" + str(dieBlock) + "-FBB")
                        isFBB = True
                        FBBCount += 1
                        break
                if not isFBB:
                    if physicalAddress.plane not in list(bbList.keys()):
                        bbList[physicalAddress.plane] = []
                    bbList[physicalAddress.plane].append("Z" + str(currentZone) + "-" + str(dieBlock))

        totalBBsInDie = 0
        for plane in range(self.__fwConfigData.planesPerDie):
            self.logger.Info("", "[GetAllBadBlocksInCard][Plane%d] %s"%(plane, bbList[plane]))
            self.logger.Info("", "[GetAllBadBlocksInCard] Total bad blocks found in plane%d = %d"%(plane, len(bbList[plane])))
            totalBBsInDie += len(bbList[plane])
        self.logger.Info("", "[GetAllBadBlocksInCard] Total FBBs found in current die = %d"%FBBCount)
        self.logger.Info("", "[GetAllBadBlocksInCard] Total blocks marked by FW as bad = %d"%(totalBBsInDie-FBBCount))
        return bbList, totalBBsInDie

    #@Author: Shaheed Nehal A
    #Objective: To verify if FW is marking the BBs as per spec for reduced capacity bots
    def VerifyReducedCapBBMarking(self, badBlockList, BadBlockCountPerPlane):
        numOfZonesPerDie = self.__file14Object["NoOfZonesPerDie"]
        expectedBBCountPerDie = self.__file14Object["TotalBadBlocksRequiredPerDie"]
        expectedBBCountPerPlane = old_div(expectedBBCountPerDie,self.__fwConfigData.planesPerDie)
        maxBBperZone = self.__file14Object["MaxAllowableBBPerZone"]
        startBlockForMarking_PerZoneList = self.__file14Object["StartBlockPerZoneList"] #[eval("self.__file14Object['StartBlockZone{}']".format(i)) for i in range(numOfZonesPerDie)]
        totalBlocksInDie = old_div(self.__fwConfigData.totalNumPhysicalBlocks,(self.__fwConfigData.numChips*self.__fwConfigData.diesPerChip))
        blocksInEachZone = old_div(totalBlocksInDie,numOfZonesPerDie)
        BlockRangesPerZoneInEachDie = [(i*blocksInEachZone,(i+1)*blocksInEachZone-1) for i in range(numOfZonesPerDie)]

        self.logger.BigBanner("Verifying Zone Based Bad Block Injection")
        self.logger.Info("", "[Test: Info] Total num of dies in card: %d"%(self.__fwConfigData.diesPerChip*self.__fwConfigData.numChips))
        self.logger.Info("", "[Test: Info] Total phy blocks per die: %d"%totalBlocksInDie)
        self.logger.Info("", "[Test: Info] BBs to be marked in each die: %d"%expectedBBCountPerDie)
        self.logger.Info("", "[Test: Info] BBs to be marked in each plane: %d"%expectedBBCountPerPlane)
        self.logger.Info("", "[Test: Info] Num of zones in each die: %d"%numOfZonesPerDie)
        self.logger.Info("", "[Test: Info] Num of BBs to be injected in each zone at max: %d"%maxBBperZone)
        self.logger.Info("", "[Test: Info] Start blocks for marking per zone in each die: %s"%startBlockForMarking_PerZoneList)
        self.logger.Info("", "[Test: Info] Block Range per zone in each die: %s"%BlockRangesPerZoneInEachDie)

        FBBDistribution = {}
        for bb in badBlockList:
            if(bb.chip, bb.die) not in FBBDistribution:
                FBBDistribution[(bb.chip, bb.die)] = [bb]
            else:
                FBBDistribution[(bb.chip, bb.die)].append(bb)

        FBBsPerZone = {}
        expectedBBsPerDie = {}
        #Count num of BBs in each zone of every die
        for (chip, die) in sorted(list(FBBDistribution.keys()), key=lambda x: (x[0], x[1])):
            FBBsPerZone[(chip, die)] = [{"InZone":[], "OutZone":[]} for _ in range(numOfZonesPerDie)]
            expectedBBsPerDie[(chip, die)] = [[] for _ in range(numOfZonesPerDie)]

            #Get the FBBs lying within and outside BB marking region in each zone of current die
            for block in sorted(FBBDistribution[(chip, die)], key=lambda x: (x.plane, x.block)):
                #blockNumInDie = block.block + block.plane*self.__fwConfigData.blocksPerPlane
                blockNumInDie = block.block*self.__fwConfigData.planeInterleave + block.plane
                for BlockRange in BlockRangesPerZoneInEachDie:
                    if blockNumInDie in range(BlockRange[0], BlockRange[1]+1):
                        currentZone = BlockRangesPerZoneInEachDie.index(BlockRange)
                        BBStartBlock = startBlockForMarking_PerZoneList[currentZone]
                        BBEndBlock = startBlockForMarking_PerZoneList[currentZone] + maxBBperZone - 1
                        #Check if current block is inside BB marking region
                        if BBStartBlock <= blockNumInDie <= BBEndBlock:
                            FBBsPerZone[(chip, die)][currentZone]["InZone"].append((blockNumInDie, block))
                        else:
                            FBBsPerZone[(chip, die)][currentZone]["OutZone"].append((blockNumInDie, block))
                        break

            #Check if the num of FBBs > max limit per die
            FBBCountInCurrentDie = len(FBBDistribution[(chip, die)])
            totalBadBlocksInDie = 0
            BadBlocksInCard = {}

            if FBBCountInCurrentDie > expectedBBCountPerDie:
                self.logger.Error("", "[Test: Error] Max allowed BBs per die: %d"%expectedBBCountPerDie)
                self.logger.Error("", "[Test: Error] FBB count in current (chip:%d, die:%d): %d"%(chip, die, FBBCountInCurrentDie))
                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "FBB count per die cannot cross the max BB limit per die")

            self.logger.BigBanner("FBB/FW marking info in chip: 0x%X, die: 0x%X"%(chip, die))
            self.logger.Info("", "[Test: Info] Total blocks present in 1 die: %d"%totalBlocksInDie)
            self.logger.Info("", "[Test: Info] Max BBs that can be injected in 1 die: %d"%expectedBBCountPerDie)
            self.logger.Info("", "[Test: Info] No of FBBs present in current die: %d"%FBBCountInCurrentDie)

            totalFBBsInDie = 0
            totalFBBsInMarkingRegion = 0
            totalFBBsOutMarkingRegion = 0

            FBBsTrackedInTest = []
            #Printing the no of FBBs within and outside BB marking region of each zone in current die
            for zone in range(numOfZonesPerDie):
                FBBCountWithinBBRegion = len(FBBsPerZone[(chip, die)][zone]["InZone"])
                FBBCountOutsideBBRegion = len(FBBsPerZone[(chip, die)][zone]["OutZone"])
                FBBCountInCurrentZone = FBBCountWithinBBRegion + FBBCountOutsideBBRegion
                totalFBBsInDie += FBBCountInCurrentZone
                totalFBBsInMarkingRegion += FBBCountWithinBBRegion
                totalFBBsOutMarkingRegion += FBBCountOutsideBBRegion
                self.logger.Info("", "[Test: FBBInfo] Chip: %d, Die: %d, Zone: %d --> No of FBBs inside BB marking region: %d"%(chip, die, zone, FBBCountWithinBBRegion))
                self.logger.Info("", "[Test: FBBInfo] Chip: %d, Die: %d, Zone: %d --> No of FBBs inside current zone, but outside BB marking region: %d"%(chip, die, zone,FBBCountOutsideBBRegion))
                self.logger.Info("", "[Test: FBBInfo] Chip: %d, Die: %d, Zone: %d --> Total no of FBBs in current zone: %d"%(chip, die, zone, FBBCountInCurrentZone))
                self.logger.Info("", "[Test: FBBInfo] Chip: %d, Die: %d, Zone: %d --> Total no of FBBs in current die: %d"%(chip, die, zone, totalFBBsInDie))

                FBBsPerZone[(chip, die)][zone]["InZone"].sort()
                FBBsPerZone[(chip, die)][zone]["OutZone"].sort()

                for FBB in FBBsPerZone[(chip, die)][zone]["InZone"]:
                    FBBsTrackedInTest.append(FBB[0])
                for FBB in FBBsPerZone[(chip, die)][zone]["OutZone"]:
                    FBBsTrackedInTest.append(FBB[0])

            self.logger.Info("", "[Test: FBBInfo] Total FBBs in current die = %d"%totalFBBsInDie)
            self.logger.Info("", "[Test: FBBInfo] Total FBBs inside marking region = %d"%totalFBBsInMarkingRegion)
            self.logger.Info("", "[Test: FBBInfo] Total FBBs outside marking region = %d"%totalFBBsOutMarkingRegion)

            if totalFBBsInDie != FBBCountInCurrentDie:
                self.logger.Error("", "[Test: Error] Consolidated FBB list of all zones in current die: %s"%FBBsTrackedInTest)
                self.logger.Error("", "[Test: Error] Check '[Test: BBsInDie]' string for same die in log to know the difference")
                self.logger.Error("", "[Test: Error] Sum of FBBs in all zones: %d"%totalFBBsInDie)
                self.logger.Error("", "[Test: Error] Expected FBB count in current die: %d"%FBBCountInCurrentDie)
                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Mismatch in sum of FBBs in all zones vs FBB count in die")

            totalBadBlocksInPlane = {}
            badblocksInPlane = {}
            blocksAlreadyConsidered = []

            #Check if FW is injecting per zone limit worth of bad blocks considering already present FBBs in each zone
            for zone in range(numOfZonesPerDie):
                totalBBsInjectedInCurrentZone = 0
                FBBCountWithinBBRegion = len(FBBsPerZone[(chip, die)][zone]["InZone"])
                FBBCountOutsideBBRegion = len(FBBsPerZone[(chip, die)][zone]["OutZone"])
                FBBCountInCurrentZone = FBBCountWithinBBRegion + FBBCountOutsideBBRegion
                BBStartBlock = startBlockForMarking_PerZoneList[zone]
                BBEndBlock = startBlockForMarking_PerZoneList[zone] + maxBBperZone - 1
                self.logger.BigBanner("Verifying Zone %d"%zone)
                self.logger.Info("", "[Test: FBBInfo] Chip: %d, Die: %d, Zone: %d --> No of FBBs inside BB marking region: %d"%(chip, die, zone, FBBCountWithinBBRegion))
                self.logger.Info("", "[Test: FBBInfo] Chip: %d, Die: %d, Zone: %d --> No of FBBs inside current zone, but outside BB marking region: %d"%(chip, die, zone,FBBCountOutsideBBRegion))
                self.logger.Info("", "[Test: FBBInfo] Chip: %d, Die: %d, Zone: %d --> Total no of FBBs in current zone: %d"%(chip, die, zone, FBBCountInCurrentZone))
                self.logger.Info("", "[Test: Info] Block range in current zone --> [%d-%d]"%(BlockRangesPerZoneInEachDie[zone][0], BlockRangesPerZoneInEachDie[zone][1]))
                for FBB in FBBsPerZone[(chip, die)][zone]["InZone"]:
                    self.logger.Info("", "[FBB][InBBRegion][Zone%d] Die Block Num: %d (StartBlock %d to EndBlock %d) --> chip: 0x%X, die: 0x%X, plane: 0x%X, block: 0x%X"%(zone, FBB[0], BBStartBlock, BBEndBlock, FBB[1].chip, FBB[1].die, FBB[1].plane, FBB[1].block))

                for FBB in FBBsPerZone[(chip, die)][zone]["OutZone"]:
                    self.logger.Info("", "[FBB][OutBBRegion][Zone%d] Die Block Num: %d (StartBlock %d to EndBlock %d) --> chip: 0x%X, die: 0x%X, plane: 0x%X, block: 0x%X"%(zone, FBB[0], BBStartBlock, BBEndBlock, FBB[1].chip, FBB[1].die, FBB[1].plane, FBB[1].block))


                if FBBCountInCurrentZone > maxBBperZone:
                    BBsExpectedToBeMarkedByFW = maxBBperZone
                else:
                    BBsExpectedToBeMarkedByFW = maxBBperZone - FBBCountOutsideBBRegion

                blocksWithinMarkingRegion = [block[0] for block in [item for item in FBBsPerZone[(chip, die)]][zone]["InZone"]]
                blocksWithinMarkingRegion.sort()
                lastBlockToMark = BBStartBlock + BBsExpectedToBeMarkedByFW - 1

                #If last zone, then due to plane limits, the blocks might be marked bad beyond the endblock in zone, so setting lastBlockToMark to last die block
                if zone == numOfZonesPerDie-1:
                    lastBlockToMark = self.__fwConfigData.blocksPerDie-1

                self.logger.Info("", "[Test: FBBInfo] Chip: %d, Die: %d, Zone: %d --> FW should inject %d BBs from StartBlock: %d in current zone, i.e., till block %d"%(chip, die, zone, BBsExpectedToBeMarkedByFW, BBStartBlock, lastBlockToMark))

                blockNoInDie = BBStartBlock
                outsideMarkingRegionChecked = False
                FBBsAlreadyConsidered = [] #To track some FBBs which fall inside marking region but FW wont go till that block due to zone limit being met

                #Go through all blocks from startBlock till expected endBlock in current zone and check if FW has marked as bad
                while blockNoInDie <= lastBlockToMark and blockNoInDie < self.__fwConfigData.blocksPerDie:
                    if blockNoInDie in FBBsAlreadyConsidered:
                        blockNoInDie += 1
                        continue
                    plane = blockNoInDie%self.__fwConfigData.planesPerDie
                    if plane not in list(totalBadBlocksInPlane.keys()):
                        totalBadBlocksInPlane[plane] = 0

                    if plane not in list(badblocksInPlane.keys()):
                        badblocksInPlane[plane] = []

                    block = old_div(blockNoInDie,self.__fwConfigData.planesPerDie)
                    isCurrentBlockFBB = False

                    AllFBBList = FBBsPerZone[(chip, die)][zone]["InZone"] + FBBsPerZone[(chip, die)][zone]["OutZone"]
                    AllFBBList.sort()
                    for phyBlock in AllFBBList:
                        if (chip, die, plane, block) == (phyBlock[1].chip, phyBlock[1].die, phyBlock[1].plane, phyBlock[1].block):
                            if blockNoInDie != phyBlock[0]:
                                self.logger.Error("", "[Test: Error] Should not come here")
                                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Something went wrong in calculating the Die Block Num")
                            if blockNoInDie not in FBBsAlreadyConsidered:
                                totalBBsInjectedInCurrentZone+=1
                                totalBadBlocksInDie += 1
                                totalBadBlocksInPlane[plane] += 1
                                badblocksInPlane[plane].append(blockNoInDie)
                                FBBsAlreadyConsidered.append(blockNoInDie)
                            isCurrentBlockFBB = True
                            self.logger.Info("", "[ExpectedBBMarking][FBBInjected] ZONE: %d totalBBsInjectedInCurrentZone: %d totalBBsInjectedInCurrentDie: %d, totalBBsInPlane %d: %d --> Current die block %d (chip: 0x%X, die: 0x%X, plane: 0x%X, block: 0x%X) is an FBB in BB zone. Skipping this."%(zone, totalBBsInjectedInCurrentZone, totalBadBlocksInDie, plane, totalBadBlocksInPlane[plane], blockNoInDie, chip, die, plane, block))
                            blockNoInDie += 1
                            break

                    if not isCurrentBlockFBB:
                        #Calculate the phy block address from the die Block num
                        physicalAddress = AddressTypes.PhysicalAddress()
                        physicalAddress.chip    = chip
                        physicalAddress.die     = die
                        physicalAddress.plane   = plane
                        physicalAddress.block   = block
                        physicalAddress.wordLine  = 0
                        physicalAddress.mlcLevel  = 0
                        physicalAddress.eccPage = 0
                        if self.__fwConfigData.isBiCS:
                            physicalAddress.string  = 0
                        isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
                        if not isBadBlock:
                            self.logger.Info("", "[NotABadBlock] ZONE: %d totalBBsInjectedInCurrentZone: %d, totalBBsInjectedInCurrentDie: %d, totalBBsInPlane %d: %d --> BlockNumInDie:%d --> chip:0x%X, die:0x%X, plane:0x%X, block:0x%X is expected to be marked bad from FW end"%(zone, totalBBsInjectedInCurrentZone, totalBadBlocksInDie, plane, totalBadBlocksInPlane[plane], blockNoInDie, chip, die, plane, block))
                            if totalBadBlocksInDie == expectedBBCountPerDie:
                                self.logger.Info("", "[Test: Info] Die limit met, hence the above block was not marked by FW as expected")
                                break
                            if totalBadBlocksInPlane[plane] == expectedBBCountPerPlane:
                                self.logger.Info("", "[Test: Info] Plane limit met, hence the above block was not marked by FW as expected")
                                blockNoInDie += 1
                                continue

                            if not outsideMarkingRegionChecked:
                                #Check if there are any FBBs within current zone which aren't yet checked in the loop because of zone limit being met
                                indexOfCurrentBlockInListOfBlocksWithinMarkingRegion = bisect(blocksWithinMarkingRegion, blockNoInDie) #This returns index of current block if it were to be inserted in the list of blocksWithinMarkingRegion

                                #All FBBs which are present within marking region but not checked because of zone limit being met will lie ahead of current blocks insertion index
                                numOfFBBsNotCheckedInCurrentZone = len(blocksWithinMarkingRegion) - indexOfCurrentBlockInListOfBlocksWithinMarkingRegion

                                #Check all FBBs and increment their respective plane BB count
                                for blockIndex in range(indexOfCurrentBlockInListOfBlocksWithinMarkingRegion, len(blocksWithinMarkingRegion)):
                                    FBBDieBlockNum = blocksWithinMarkingRegion[blockIndex]
                                    FBBPlane = FBBDieBlockNum%self.__fwConfigData.planesPerDie
                                    FBBBlock = old_div(FBBDieBlockNum,self.__fwConfigData.planesPerDie)
                                    if FBBDieBlockNum not in FBBsAlreadyConsidered:
                                        badblocksInPlane[FBBPlane].append(FBBDieBlockNum)
                                        totalBBsInjectedInCurrentZone += 1
                                        totalBadBlocksInPlane[FBBPlane] += 1
                                        totalBadBlocksInDie += 1
                                        self.logger.Info("", "[ExpectedBBMarking_ButSkippedDuetoInsideRegion] ZONE: %d totalBBsInjectedInCurrentZone: %d, totalBBsInjectedInCurrentDie: %d, totalBBsInPlane %d: %d --> BlockNumInDie:%d --> chip:0x%X, die:0x%X, plane:0x%X, block:0x%X is expected to be marked bad from FW end"%(zone, totalBBsInjectedInCurrentZone, totalBadBlocksInDie, FBBPlane, totalBadBlocksInPlane[FBBPlane], FBBDieBlockNum, chip, die, FBBPlane, FBBBlock))
                                        FBBsAlreadyConsidered.append(FBBDieBlockNum)

                                #Including FBB count outside the marking region
                                for FBB in FBBsPerZone[(chip, die)][zone]["OutZone"]:
                                    FBBDieBlockNum = FBB[0]
                                    FBBPlane = FBB[1].plane
                                    FBBBlock = FBB[1].die
                                    if FBBDieBlockNum not in FBBsAlreadyConsidered:
                                        badblocksInPlane[FBBPlane].append(FBBDieBlockNum)
                                        totalBBsInjectedInCurrentZone += 1
                                        totalBadBlocksInPlane[FBBPlane] += 1
                                        totalBadBlocksInDie += 1
                                        self.logger.Info("", "[ExpectedBBMarking_ButSkippedDuetoOutsideRegion] ZONE: %d totalBBsInjectedInCurrentZone: %d, totalBBsInjectedInCurrentDie: %d, totalBBsInPlane %d: %d --> BlockNumInDie:%d --> chip:0x%X, die:0x%X, plane:0x%X, block:0x%X is expected to be marked bad from FW end"%(zone, totalBBsInjectedInCurrentZone, totalBadBlocksInDie, FBBPlane, totalBadBlocksInPlane[FBBPlane], FBBDieBlockNum, chip, die, FBBPlane, FBBBlock))
                                        #For last zone, the loop would go till last die block so FBB recheck might happen --> so appending outside region blocks too
                                        FBBsAlreadyConsidered.append(FBBDieBlockNum)

                                outsideMarkingRegionChecked = True

                            if totalBBsInjectedInCurrentZone == maxBBperZone:
                                self.logger.Info("", "[Test: Info] Zone limit met, hence the above block was not marked by FW as expected")
                                break
                            blockNoInDie+=1
                        else:
                            totalBBsInjectedInCurrentZone += 1
                            totalBadBlocksInDie += 1
                            totalBadBlocksInPlane[plane] += 1
                            self.logger.Info("", "[ExpectedBBMarking] ZONE: %d totalBBsInjectedInCurrentZone: %d, totalBBsInjectedInCurrentDie: %d, totalBBsInPlane %d: %d --> BlockNumInDie:%d --> chip:0x%X, die:0x%X, plane:0x%X, block:0x%X is expected to be marked bad from FW end"%(zone, totalBBsInjectedInCurrentZone, totalBadBlocksInDie, plane, totalBadBlocksInPlane[plane], blockNoInDie, chip, die, plane, block))
                            badblocksInPlane[plane].append(blockNoInDie)
                            blockNoInDie += 1
                            if totalBadBlocksInPlane[plane] > expectedBBCountPerPlane:
                                self.logger.Error("", "[Test: Error] Bad blocks exceeded per plane limit. Currently marked bad blocks in current plane = %d"%totalBadBlocksInPlane[plane])
                                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Bad block count exceeded per plane limit")

                self.logger.Info("", "[BBInfo: Zone%d] Total BBs injected by FW (including the already present FBBs) --> %d, totalBBsInjectedInCurrentDie: %d, totalBBsInPlane %d: %d"%(zone, totalBBsInjectedInCurrentZone, totalBadBlocksInDie, plane, totalBadBlocksInPlane[plane]))

                #Check if zone limit is met
                if totalBBsInjectedInCurrentZone != maxBBperZone:
                    self.logger.Warning("", "[Test: Warning] Zone limit not met for current zone %d"%zone)

                    #Do not repeat checks for FBB outside the marking region is already done (will lead to incorrect bad block count)
                    if not outsideMarkingRegionChecked:
                        #Including FBB count outside the marking region to see if above zone limit not being met is due to FBBs lying outside marking region
                        for FBB in FBBsPerZone[(chip, die)][zone]["OutZone"]:
                            FBBDieBlockNum = FBB[0]
                            FBBPlane = FBB[1].plane
                            FBBBlock = FBB[1].die
                            if FBBDieBlockNum not in FBBsAlreadyConsidered:
                                badblocksInPlane[FBBPlane].append(FBBDieBlockNum)
                                totalBBsInjectedInCurrentZone += 1
                                totalBadBlocksInPlane[FBBPlane] += 1
                                totalBadBlocksInDie += 1
                                self.logger.Info("", "[ExpectedBBMarking_ButSkippedDuetoOutsideRegion] ZONE: %d totalBBsInjectedInCurrentZone: %d, totalBBsInjectedInCurrentDie: %d, totalBBsInPlane %d: %d --> BlockNumInDie:%d --> chip:0x%X, die:0x%X, plane:0x%X, block:0x%X is expected to be marked bad from FW end"%(zone, totalBBsInjectedInCurrentZone, totalBadBlocksInDie, FBBPlane, totalBadBlocksInPlane[FBBPlane], FBBDieBlockNum, chip, die, FBBPlane, FBBBlock))

                    #Zone limit may not be met in case of last zones due to die limit already being met
                    if totalBBsInjectedInCurrentZone != maxBBperZone and totalBadBlocksInDie != expectedBBCountPerDie:
                        raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Zone limit not met for current zone")

            #Check if plane limit is met
            for plane in range(self.__fwConfigData.planesPerDie):
                if totalBadBlocksInPlane[plane] != expectedBBCountPerPlane:
                    self.logger.Error("", "[Test: Error] Current plane %d --> bad blocks found: %d, but expected: %d"%(plane, totalBadBlocksInPlane[plane], expectedBBCountPerPlane))
                    raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Plane limit not met for current plane")

            #Check if die limit is met
            if totalBadBlocksInDie != expectedBBCountPerDie:
                self.logger.Error("", "[Test: Error] Total blocks marked as bad by FW = %d"%totalBadBlocksInDie)
                self.logger.Error("", "[Test: Error] Expected blocks to marked as bad by FW = %d"%expectedBBCountPerDie)
                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Die limit not met for current die")

    def CheckFWMarkingToReduceCapacity(self):
        numOfZonesPerDie = self.__file14Object["NoOfZonesPerDie"]
        if numOfZonesPerDie == 0:
            raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Num of zones in each die cannot be zero - check config file 14, offset 0xBA")
        expectedBBCountPerDie = self.__file14Object["TotalBadBlocksRequiredPerDie"]
        expectedBBCountPerPlane = old_div(expectedBBCountPerDie,self.__fwConfigData.planesPerDie)
        maxBBperZone = self.__file14Object["MaxAllowableBBPerZone"]
        startBlockForMarking_PerZoneList = self.__file14Object["StartBlockPerZoneList"] #[eval("self.__file14Object['StartBlockZone{}']".format(i)) for i in range(numOfZonesPerDie)]
        totalBlocksInDie = old_div(self.__fwConfigData.totalNumPhysicalBlocks,(self.__fwConfigData.numChips*self.__fwConfigData.diesPerChip))
        blocksInEachZone = old_div(totalBlocksInDie,numOfZonesPerDie)
        BlockRangesPerZoneInEachDie = [(i*blocksInEachZone,(i+1)*blocksInEachZone-1) for i in range(numOfZonesPerDie)]

        self.logger.BigBanner("Zone Based Bad Block Config File Information")
        self.logger.Info("", "[Test: Info] Total num of dies in card: %d"%(self.__fwConfigData.diesPerChip*self.__fwConfigData.numChips))
        self.logger.Info("", "[Test: Info] Total phy blocks per die: %d"%totalBlocksInDie)
        self.logger.Info("", "[Test: Info] BBs to be marked in each die: %d"%expectedBBCountPerDie)
        self.logger.Info("", "[Test: Info] BBs to be marked in each plane: %d"%expectedBBCountPerPlane)
        self.logger.Info("", "[Test: Info] Num of zones in each die: %d"%numOfZonesPerDie)
        self.logger.Info("", "[Test: Info] Num of BBs to be injected in each zone at max: %d"%maxBBperZone)
        self.logger.Info("", "[Test: Info] Start blocks for marking per zone in each die: %s"%startBlockForMarking_PerZoneList)
        self.logger.Info("", "[Test: Info] Block Range per zone in each die: %s"%BlockRangesPerZoneInEachDie)

        self.expectedBBsPerZone = {}
        remainingBBs = expectedBBCountPerDie
        for startBlock in startBlockForMarking_PerZoneList:
            if (startBlock+maxBBperZone < totalBlocksInDie):
                if remainingBBs >= maxBBperZone:
                    endBlock = startBlock + maxBBperZone
                    remainingBBs -= maxBBperZone
                else:
                    endBlock = startBlock + remainingBBs
                    remainingBBs = 0
                self.expectedBBsPerZone[startBlockForMarking_PerZoneList.index(startBlock)] = (startBlock, endBlock)
            else:
                self.logger.Error("", "[Test: Error] CurrentZone: %d, StartBlock: %d, maxBBsPerZone: %d, totalBlocksInDie: %d"%(startBlockForMarking_PerZoneList.index(startBlock), startBlock, maxBBperZone, totalBlocksInDie))
                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "StartBlock + maxBBsPerZone is crossing the last Block in die")

        for zone in range(numOfZonesPerDie):
            startDieBlock = self.expectedBBsPerZone[zone][0]
            endDieBlock = self.expectedBBsPerZone[zone][1]
            self.logger.Info("", "Zone %d --> StartBlock = %d (0x%X), EndBlock = %d (0x%X), TotalCountOfBBsInZone: %d"%(zone, startDieBlock, startDieBlock, endDieBlock-1, endDieBlock-1, endDieBlock-startDieBlock))

        FWMarkedBadBlockList = []
        for chip in range (self.__fwConfigData.numChips):
            for die in range (self.__fwConfigData.diesPerChip):
                BBsPerPlane = {}
                totalBadBlocksPerDie = 0
                #Go through each of zone and check if all blocks are marked bad
                for zone in range(numOfZonesPerDie):
                    startDieBlock = self.expectedBBsPerZone[zone][0]
                    endDieBlock = self.expectedBBsPerZone[zone][1]
                    if zone == numOfZonesPerDie-1:
                        endDieBlock = totalBlocksInDie
                    for DieBlock in range(startDieBlock, endDieBlock):
                        block = old_div(DieBlock,self.__fwConfigData.planesPerDie)
                        plane = DieBlock%self.__fwConfigData.planesPerDie
                        if plane not in list(BBsPerPlane.keys()):
                            BBsPerPlane[plane] = 0

                        #Calculate the phy block address from the die Block num
                        physicalAddress = AddressTypes.PhysicalAddress()
                        physicalAddress.chip    = chip
                        physicalAddress.die     = die
                        physicalAddress.plane   = plane
                        physicalAddress.block   = block
                        physicalAddress.wordLine  = 0
                        physicalAddress.mlcLevel  = 0
                        physicalAddress.eccPage = 0
                        if self.__fwConfigData.isBiCS:
                            physicalAddress.string  = 0

                        #For last zone, FW marking should be only till self.expectedBBsPerZone[zone][1] and not till endDieBlock (which is updated to totalBlocksPerDie for last zone)
                        if zone == numOfZonesPerDie-1:
                            if DieBlock < self.expectedBBsPerZone[zone][1]:
                                FWMarkedBadBlockList.append(physicalAddress)
                        else:
                            FWMarkedBadBlockList.append(physicalAddress)

                        if self.__optionValues.checkZoneBasedBBInjection:
                            isBadBlock = self.CheckInFactoryMarkedBadBlockFile(physicalAddress)
                            if isBadBlock:
                                BBsPerPlane[plane] += 1
                                totalBadBlocksPerDie += 1
                                self.logger.Info("", "[FW Marking] ZONE: %d --> Chip: 0x%X, Die: 0x%X, Plane: 0x%X, PhyBlock: %d, DieBlock: %d (0x%X), BBsInCurrentPlane: %d"%(zone, chip, die, plane, block, DieBlock, DieBlock, BBsPerPlane[plane]))
                            else:
                                if BBsPerPlane[plane] == expectedBBCountPerPlane:
                                    continue
                                else:
                                    self.logger.Error("", "[Test: Error][FW Marking] ZONE: %d --> Chip: 0x%X, Die: 0x%X, Plane: 0x%X, PhyBlock: %d, DieBlock: %d (0x%X), BBsInCurrentPlane: %d, BBsInCurrentDie: %d"%(zone, chip, die, plane, block, DieBlock, DieBlock, BBsPerPlane[plane], totalBadBlocksPerDie))
                                    self.logger.Error("", "[Test: Error] Test expected BB on current plane as BBsInCurrentPlane %d < expectedBBCountPerPlane %d"%(BBsPerPlane[plane], expectedBBCountPerPlane))
                                    raise TestError.TestFailError(self.vtfContainer.GetTestName(), "BadBlock was expected")

                if self.__optionValues.checkZoneBasedBBInjection and totalBadBlocksPerDie != expectedBBCountPerDie:
                    self.logger.Warning("", "[Test: Warning] Expected bad block count in current chip: 0x%X, die: 0x%X --> %d, but actual BBs found: %d"%(chip, die, totalBadBlocksPerDie, expectedBBCountPerDie))
                    for plane in range(self.__fwConfigData.planeInterleave):
                        if BBsPerPlane[plane] != expectedBBCountPerPlane:
                            self.logger.Error("", "[Test: Error] BBs expected on Plane %d --> %d, but found %d BBs"%(plane, expectedBBCountPerPlane, BBsPerPlane[plane]))
                            raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Expected num of BBs were not injected in current plane")

        return FWMarkedBadBlockList

    def getBlocksPerZone(self):
        numOfZonesPerDie = self.__file14Object["NoOfZonesPerDie"]
        totalBlocksInDie = old_div(self.__fwConfigData.totalNumPhysicalBlocks,(self.__fwConfigData.numChips*self.__fwConfigData.diesPerChip))
        blocksInEachZone = old_div(totalBlocksInDie,numOfZonesPerDie)
        BlockRangesPerZoneInEachDie = [(i*blocksInEachZone,(i+1)*blocksInEachZone-1) for i in range(numOfZonesPerDie)]
        blocksPerZone = {}

        for zone in range(numOfZonesPerDie):
            if zone not in list(blocksPerZone.keys()):
                blocksPerZone[zone] = []
            for dieBlockNum in range(BlockRangesPerZoneInEachDie[zone][0], BlockRangesPerZoneInEachDie[zone][1]+1):
                block = old_div(dieBlockNum,self.__fwConfigData.planesPerDie)
                plane = dieBlockNum%self.__fwConfigData.planesPerDie
                physicalAddress = AddressTypes.PhysicalAddress()
                physicalAddress.plane   = plane
                physicalAddress.block   = block
                blocksPerZone[zone].append(physicalAddress)

        return blocksPerZone, BlockRangesPerZoneInEachDie

    #end of class BadBlockValidation
