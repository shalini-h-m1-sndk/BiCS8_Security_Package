"""
class CardRawOperations
A library file to handle card 'raw' operations. Ex: ReadECCPage, WriteECCPage
@ Author: Shaheed Nehal A
@ copyright (C) 2020 Western Digital Corporation
@ Date: 23-Dec-2020
"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    from builtins import range
    pass # from builtins import *
    from builtins import object
from past.utils import old_div
erasedPattern = 0xFF
STATUS_ECC_ERROR= 4
SUSPEND_BACK_GROUND_OPERATIONS = 0
RESUME_BACK_GROUND_OPERATIONS = 1
BE_SPECIFIC_READ_IN_TRUE_BINARY_MODE = 0x200
BE_SPECIFIC_WRITE_IN_TRUE_BINARY_MODE = 0x200
BE_SPECIFIC_READ_PHYSICAL_IN_WORDLINE_ADDRESSING_MODE = 0x400

import Extensions.CVFImports as pyWrap
import AddressTypes
import Core.ValidationError as TestError
import os
import Constants

class CardRawOperations(object):

    def __init__(self, testSpace, fwConfigData, addrTransObj):
        self.vtfContainer = testSpace
        self.logger = self.vtfContainer.GetLogger()

        self.__fwConfigData     = fwConfigData
        self.__addrTransObj     = addrTransObj

        self.__CORRECTABLE   = Constants.FS_Config_CONSTANTS.IFS_CORRECTABLE_ECC
        self.__UNCORRECTABLE = Constants.FS_Config_CONSTANTS.IFS_UNCORRECTABLE_ECC

        self.__RAND = 'RAND'
        self.__CHUNKSIZE = 1# physical page granularity
        self.__initialFillPattern = 0x00
        self.__numOfBitsToCorrupt = 0 # This is used to check if more than the specified no. of bits are corrupted - use it with care
        self.__ErasedEccBuffer = pyWrap.Buffer.CreateBuffer(self.__fwConfigData.sectorsPerRawEccPage, 0xFF)
        self.__eccFieldSize  = self.__fwConfigData.eccFieldSize # size(in bytes) of ecc segment of a ECC page

        if (self.__fwConfigData.mlcLevel == 2): #D2 memory
            self.usedMlcPages = [0,1]
        elif (self.__fwConfigData.mlcLevel == 3):#D3 memory
            self.usedMlcPages = [0,1,2]
        else:
            self.usedMlcPages = [0]

        if self.vtfContainer.isModel:
            self.__flash= self.vtfContainer._livet.GetFlash()
            self.__modelBytesPerPage = self.__flash.GetUintVariable('bytes_per_page')
        return

    def ECCInject(self, corruptLocation, errorType = 0, errorByte = 14, numOfBits = None, ignoreDiagnostic = False):
        """
        Name          :      ECCInject
        Description   :      Injects an error into a defined sector
        Notes         :      Current algorithm only supports sequential bit corruption

        Arguments     :

            corruptLocation:           The physical location where the error would be injected
                                       This has:
                                       - chip,
                                       - die,
                                       - plane,
                                       - block,
                                       - wordLine,
                                       - mlcLevel,
        - eccPage,
        - isTrueBinaryBlock

            errorType:           Level of error injection, # of bits to corrupt is determined by the function.
                                 0 - Correctable
                                 1 - Uncorrectable
                                 RAND - randomly pick the level (correctabl/uncorrectable)
                                 (default = correctable)

            errorByte:           Starting location for the ECC corruption
                                 (default = Byte 14) #to avoid corrupting the header(??)


            numOfBits:           Number of bit errors to create
                                 If numOfBits is defined, errorType will be ignored
                                 If numOfBits is undefined, the function will determine the
                                 number of bits to corrupt
                                 (default = use errorType)
           ignoreDiagnostic:     Used when this function is used from a callback as diagnostics cannot be executed.

        Returns       :      None

        Note          :      The no. of errors that are alredy present in the ECC FIELD are not taken care of
                             while calculating the no. of errors to be injected.
        This is so because we can not read the ECC FIELD DATA with and with out ecc correction
        """
        if not self.vtfContainer.isModel:
            if (not(corruptLocation.isTrueBinaryBlock) and (self.__fwConfigData.mlcLevel == 3)):
                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "[ECCInject] Block is in D3 memory; Can not inject ECC errors!!")

        if (self.__fwConfigData.mlcLevel == 3):
            if corruptLocation.isTrueBinaryBlock :
                self.usedMlcPages = [0]
            else:
                self.usedMlcPages = [0,1,2]
        if  (self.__fwConfigData.mlcLevel == 2):
            if corruptLocation.isTrueBinaryBlock :
                self.usedMlcPages = [0]
            else:
                self.usedMlcPages = [0,1]


         #Suspend the back ground maintenance operations
        if(not(ignoreDiagnostic)):
            self.sctpUtils.DoBackGroundMaintenanceOperations(SUSPEND_BACK_GROUND_OPERATIONS)

        if self.vtfContainer.isModel :
            #For model, error injection is done thru Livet APIs
            # Determine the number of bits to corrupt
            numOfBits = self.__GetNumOfErrorBits(corruptLocation,errorType,numOfBits)
            self.__InjectError(physicalLocation = corruptLocation,  errorByte = errorByte, numOfBits = numOfBits)

        else:
            #For HW, error injection is done thru rdeccpg,eraseblk,bitflipping in buffer & wreccpg
            SINGLE_ECC_PAGE = 1
            ALL_ZEROS = 0X00

            # Check if input parameters are valid
            if (errorType != self.__CORRECTABLE) and (errorType != self.__UNCORRECTABLE) and\
               (errorType != self.__RAND):
                raise ValueError("Invalid ECC error level, errorType=%i" %(errorType))

            # step 1: Read the specified block
            self.__blockDataBuffer = self.__physicalBlockRead(physicalLocation = corruptLocation)

            # read the ecc page data before injection, this will be used at the end to check the error injection
            eccPageDataBeforeCorruption = pyWrap.Buffer.CreateBuffer(self.__fwConfigData.sectorsPerRawEccPage,ALL_ZEROS)
            corruptEccPage              = (corruptLocation.wordLine * len(self.usedMlcPages) + corruptLocation.mlcLevel) * self.__fwConfigData.eccPagesPerMlcPage\
                                        + corruptLocation.eccPage
            corruptedEccPageOffSet      = (corruptEccPage * self.__fwConfigData.sectorsPerRawEccPage * Constants.FwConfig_CONSTANTS.BE_SPECIFIC_BYTES_PER_SECTOR)

            eccPageDataBeforeCorruption.Copy(self.__blockDataBuffer, 0,corruptedEccPageOffSet,self.__fwConfigData.sectorsPerRawEccPage * Constants.FwConfig_CONSTANTS.BE_SPECIFIC_BYTES_PER_SECTOR)


            # step 2: inject the error in the specified location
            # Determine the number of bits to corrupt
            numOfBits = self.__GetNumOfErrorBits(corruptLocation,errorType,numOfBits)
            self.__InjectError(physicalLocation = corruptLocation,  errorByte = errorByte, numOfBits = numOfBits)


            # step 3: Erase the whole block
            # This issues Diag internally
            self.__card.EraseBlock(corruptLocation.chip,corruptLocation.die, corruptLocation.plane, corruptLocation.block,
                                   1, true_binary=corruptLocation.isTrueBinaryBlock)

            # step 4: Write the whole block
            if len(self.usedMlcPages) == 2:
                self.__physicalBlockWriteD2(corruptLocation)
            else:
                self.__physicalBlockWrite(corruptLocation)


            # step 5: Additionl check1
            #         For error injection; the errors that are present in a physical location prior
            #         to the ecc injection are taken care of in the module used to modify the write buffer
            #         before doing a physical write ( this is done in the module __InjectError)
            #         This check could not be done for the ECC FIELD of the ECC Page
            #          - so if the data corruption is targetted at the ECC FIELD then,
            #            we inject the error and read the written data back and check whether the intended error has been
            #            injected into the ECC FIELD or not
            headerAndUserDataSize = Constants.FwConfig_CONSTANTS.BE_SPECIFIC_HEADER_SIZE_IN_BYTES+\
                                  Constants.FwConfig_CONSTANTS.BE_SPECIFIC_BYTES_PER_SECTOR *  self.__fwConfigData.sectorsPerEccPage
            eccFieldDataOffset = headerAndUserDataSize
            if (errorByte >= eccFieldDataOffset):# do the check
                option = 0x20# read scrambled data

                # get the corruption data, this is the data that is intended to be written to the physical location after injectig the error
                corruptionData = pyWrap.Buffer.CreateBuffer(self.__fwConfigData.sectorsPerRawEccPage,ALL_ZEROS)

                corruptionData.Copy(self.__blockDataBuffer, 0,corruptedEccPageOffSet,self.__fwConfigData.sectorsPerRawEccPage *  Constants.FwConfig_CONSTANTS.BE_SPECIFIC_BYTES_PER_SECTOR)

                # get the actual data written
                writtenData = pyWrap.Buffer.CreateBuffer(self.__fwConfigData.sectorsPerRawEccPage,ALL_ZEROS)
                ReadEccPage(writtenData, corruptLocation,SINGLE_ECC_PAGE,option)

                # Compare the data
                try:
                    writtenData.Compare(corruptionData,eccFieldDataOffset,eccFieldDataOffset,self.__fwConfigData.eccFieldSize)
                except:# there is a miss compare so inform this to the user
                    self.logger.Warning("", "[ECCInject] The error injection was not succesfully done since there are some errors"
                                          " already present at the specified location - try changing the physical location or the"
                                          "no. of the bits to be corrupted if the intended results are not out at the ened of the test ")

            # step 6: Additional Check2
            #         If the no. of bits to be corrupted is not greater than the correctable level
            #         then compare the ecc page data after error injection with the data read before
            #         error injection and if the no. of errors injected is beyond the correctable
            #         ecc level then assert it saying that this has happened because of BAD NAND
            if not self.__numOfBitsToCorrupt > self.__fwConfigData.correctableEccLevel:
                # read the raw data after the error injection
                option = 0x20# read scrambled data

                writtenData = pyWrap.Buffer.CreateBuffer(self.__fwConfigData.sectorsPerRawEccPage,ALL_ZEROS)
                ReadEccPage(writtenData, corruptLocation,SINGLE_ECC_PAGE,option)

                # count the no. of flip bits when compared with the data read before error injection
                noOfFlippedBitsAfterInjection = self.GetFlippedBitCount(eccPageDataBeforeCorruption, writtenData, headerAndUserDataSize)
                # if this count is more than the corretable ecc level assert it
                if noOfFlippedBitsAfterInjection > self.__fwConfigData.correctableEccLevel:
                    raise TestError.TestFailError(self.vtfContainer.GetTestName(), "[ECCInject] the no. of errors injected is beyond the correctable ecc level \n"
                                                    "\tThis has happened because of BAD NAND")
        #end of if-else IsProtocolModel
        if self.__fwConfigData.isBiCS:
            phyAddress = [corruptLocation.chip,corruptLocation.die,corruptLocation.plane,corruptLocation.block,corruptLocation.wordLine,corruptLocation.string,corruptLocation.mlcLevel,corruptLocation.eccPage]
        else:
            phyAddress = [corruptLocation.chip,corruptLocation.die,corruptLocation.plane,corruptLocation.block,corruptLocation.wordLine,corruptLocation.mlcLevel,corruptLocation.eccPage]
        self.logger.Info("", "[ECCInject] Error injected successfully on Physical address(%s) errorByte offset(%d) numOfBits(%d)"\
                                    %(phyAddress,errorByte,numOfBits))

        #Resume the back ground maintenance operations
        if(not(ignoreDiagnostic)):
            self.sctpUtils.DoBackGroundMaintenanceOperations(RESUME_BACK_GROUND_OPERATIONS)

    # end of  ECCInject()


    def ECCInjectInAllThreeAreas(self, corruptLocation, errorType , errorByteInData,errorByteInHeader,errorByteInEccPage, numOfBits = None):
        """
        Name        : ECCInjectInAllThreeAreas
        Description : Injects ECC errors to all the 3 areas- host data,header and ecc page areas.
        Notes       :      Current algorithm only supports sequential bit corruption
        Arguments   :
        corruptLocation:           The physical location where the error would be injected
        This has:
        - chip,
        - die,
        - plane,
        - block,
        - page,
        - eccPage
        - isTrueBinaryBlock

        errorType:           Level of error injection, # of bits to corrupt is determined by the function.
        0 - Correctable
        1 - Uncorrectable
        RAND - randomly pick the level (correctabl/uncorrectable)
        (default = correctable)

        errorByteInData:   Starting location for the ECC corruption in host data area

        errorByteInHeader:   Starting location for the ECC corruption in header area

        errorByteInEccPage:   Starting location for the ECC corruption in ecc page area


        numOfBits:           Number of bit errors to create
        If numOfBits is defined, errorType will be ignored
        If numOfBits is undefined, the function will determine the
        number of bits to corrupt
        (default = use errorType)

        Returns       :      None

        Note          :      The no. of errors that are alredy present in the ECC FIELD are not taken care of
        while calculating the no. of errors to be injected.
        This is so because we can not read the ECC FIELD DATA with and with out ecc correction
        Temporary function written for ECC Validation
        """
        if not self.vtfContainer.isModel:
            if (not(corruptLocation.isTrueBinaryBlock) and (self.__fwConfigData.mlcLevel == 3)):
                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "[ECCInject] Block is in D3 memory; Can not inject ECC errors!!")

        if (self.__fwConfigData.mlcLevel == 3):
            if corruptLocation.isTrueBinaryBlock :
                self.usedMlcPages = [0]
            else:
                self.usedMlcPages = [0,1,2]
        if  (self.__fwConfigData.mlcLevel == 2):
            if corruptLocation.isTrueBinaryBlock :
                self.usedMlcPages = [0]
            else:
                self.usedMlcPages = [0,1]

        #Suspend the back ground maintenance operations
        self.sctpUtils.DoBackGroundMaintenanceOperations(SUSPEND_BACK_GROUND_OPERATIONS)

        if self.vtfContainer.isModel:
            self.logger.Warning("", '[ECCInjectInAllThreeAreas] In protocol Model,Error can not be injected in header and ECC area ')
            self.logger.Warning("", '[ECCInjectInAllThreeAreas] Injecting %d bit error in Data area'%numOfBits)
            # Determine the number of bits to corrupt
            numOfBitsInData = self.__GetNumOfErrorBits(corruptLocation,errorType,numOfBits)
            self.__InjectError(physicalLocation = corruptLocation, errorByte = errorByteInData, numOfBits = numOfBitsInData)

        else:

            SINGLE_ECC_PAGE = 1
            ALL_ZEROS = 0X00

            # Check if input parameters are valid
            if (errorType != self.__CORRECTABLE) and (errorType != self.__UNCORRECTABLE) and\
               (errorType != self.__RAND):
                raise ValueError("Invalid ECC error level, errorType=%i" %(errorType))

            # step 1: Read the specified block
            self.__blockDataBuffer = self.__physicalBlockRead(physicalLocation = corruptLocation)

            # read the ecc page data before injection, this will be used at the end to check the error injection
            eccPageDataBeforeCorruption = pyWrap.Buffer.CreateBuffer(self.__fwConfigData.sectorsPerRawEccPage,ALL_ZEROS)
            corruptEccPage = (corruptLocation.wordLine * len(self.usedMlcPages) + corruptLocation.mlcLevel) * self.__fwConfigData.eccPagesPerMlcPage \
                           + corruptLocation.eccPage
            corruptedEccPageOffSet = (corruptEccPage * self.__fwConfigData.sectorsPerRawEccPage * Constants.FwConfig_CONSTANTS.BE_SPECIFIC_BYTES_PER_SECTOR)

            eccPageDataBeforeCorruption.Copy(self.__blockDataBuffer, 0,corruptedEccPageOffSet,self.__fwConfigData.sectorsPerRawEccPage *  Constants.FwConfig_CONSTANTS.BE_SPECIFIC_BYTES_PER_SECTOR)

            # step 2: inject the error in all the 3 areas
            # Determine the number of bits to corrupt
            totNumOfBits = self.__GetNumOfErrorBits(corruptLocation,errorType,numOfBits)
            numOfBitsInEachArea = old_div(totNumOfBits, 3)
            numOfBitsInData = numOfBitsInEachArea + (totNumOfBits%3)
            self.__InjectError(physicalLocation = corruptLocation, errorByte = errorByteInHeader, numOfBits = numOfBitsInEachArea)
            self.__InjectError(physicalLocation = corruptLocation, errorByte = errorByteInEccPage, numOfBits = numOfBitsInEachArea)
            self.__InjectError(physicalLocation = corruptLocation, errorByte = errorByteInData, numOfBits = numOfBitsInData)

            # step 3: Erase the whole block
            # This issues Diag internally
            self.__card.EraseBlock(corruptLocation.chip,corruptLocation.die, corruptLocation.plane, corruptLocation.block,
                                   1, true_binary=corruptLocation.isTrueBinaryBlock)

            # step 4: Write the whole block
            self.__physicalBlockWrite(corruptLocation)

            # step 5: Additionl check1
            #         For error injection; the errors that are present in a physical location prior
            #         to the ecc injection are taken care of in the module used to modify the write buffer
            #         before doing a physical write ( this is done in the module __InjectError)
            #         This check could not be done for the ECC FIELD of the ECC Page
            #          - so if the data corruption is targetted at the ECC FIELD then,
            #            we inject the error and read the written data back and check whether the intended error has been
            #            injected into the ECC FIELD or not
            headerAndUserDataSize = Constants.FwConfig_CONSTANTS.BE_SPECIFIC_HEADER_SIZE_IN_BYTES +\
                                  Constants.FwConfig_CONSTANTS.BE_SPECIFIC_BYTES_PER_SECTOR *  self.__fwConfigData.sectorsPerEccPage
            eccFieldDataOffset = headerAndUserDataSize

            if (errorByteInEccPage >= eccFieldDataOffset):# do the check
                option = 0x20# read scrambled data
                # get the corruption data, this is the data that is intended to be written to the physical location after injectig the error
                corruptionData = pyWrap.Buffer.CreateBuffer(self.__fwConfigData.sectorsPerRawEccPage,ALL_ZEROS)
                corruptionData.Copy(self.__blockDataBuffer, 0,corruptedEccPageOffSet,self.__fwConfigData.sectorsPerRawEccPage * Constants.FwConfig_CONSTANTS.BE_SPECIFIC_BYTES_PER_SECTOR)

                # get the actual data written
                writtenData = pyWrap.Buffer.CreateBuffer(self.__fwConfigData.sectorsPerRawEccPage,ALL_ZEROS)
                ReadEccPage(writtenData,corruptLocation,SINGLE_ECC_PAGE,option)

                # Compare the data
                try:
                    writtenData.Compare(corruptionData,eccFieldDataOffset,eccFieldDataOffset,self.__fwConfigData.eccFieldSize)
                except:# there is a miss compare so inform this to the user
                    self.logger.Warning("", "[ECCInject] The errro injection was not succesfully done since there are some errors"
                                          " already presetn at the specified location - try changing the physical location or the"
                                          "no. of the bits to be corrupted if the intended results are not out at the ened of the test ")


            # step 6: Additional Check2
            #         If the no. of bits to be corrupted is not greater than the correctable level
            #         then compare the ecc page data after error injection with the data read before
            #         error injection and if the no. of errors injected is beyond the correctable
            #         ecc level then assert it saying that this has happened because of BAD NAND
            if not self.__numOfBitsToCorrupt > self.__fwConfigData.correctableEccLevel:
                # read the raw data after the error injection
                option = 0x20# read scrambled data
                writtenData = pyWrap.Buffer.CreateBuffer(self.__fwConfigData.sectorsPerRawEccPage,ALL_ZEROS)
                ReadEccPage(writtenData, corruptLocation,SINGLE_ECC_PAGE,option)

                # count the no. of flip bits when compared with the data read before error injection
                noOfFlippedBitsAfterInjection = self.GetFlippedBitCount(eccPageDataBeforeCorruption, writtenData, headerAndUserDataSize)
                # if this count is more than the corretable ecc level assert it
                if noOfFlippedBitsAfterInjection > self.__fwConfigData.correctableEccLevel:
                    raise TestError.TestFailError(self.vtfContainer.GetTestName(), "[ECCInject] the no. of errors injected is beyond the correctable ecc level \n"
                                                    "\tThis has happened because of BAD NAND")
        #end of if-else IsProtocolModel

        #Resume the back ground maintenance operations
        self.sctpUtils.DoBackGroundMaintenanceOperations(RESUME_BACK_GROUND_OPERATIONS)
        return
    # end of  ECCInjectInAllThreeAreas()

    def EccInjectInModelUsingSTM(self,corruptLocation,ECCType):
        """
        Injecting UECC/CECC Error using STM
        ECCType : 0-CECC
                  1-UECC
                  States for MLC:

                  lower page -states A&E
                  middle page - states B,D,F
                  upper page - states C & G
        """
        livet = self.vtfContainer._livet
        livetFlash = livet.GetFlash()

        REVERT_ON_ERASE=1
        WIDTH_OF_THE_SHIFT = 0

        if ECCType == 0:
            ERROR_TYPE = "CECC"

            if corruptLocation.isTrueBinaryBlock:#SLC

                DAC_SHIFT_VALUE = -40
                AdjList = (livet.stateLM,DAC_SHIFT_VALUE,WIDTH_OF_THE_SHIFT)

            else:

                DAC_SHIFT_VALUE_LOWER = -10
                DAC_SHIFT_VALUE_MIDDLE = -10
                DAC_SHIFT_VALUE_UPPER = -20
                AdjList=(livet.stateA,DAC_SHIFT_VALUE_LOWER,WIDTH_OF_THE_SHIFT, livet.stateE,0,WIDTH_OF_THE_SHIFT,\
                               livet.stateB,DAC_SHIFT_VALUE_MIDDLE,WIDTH_OF_THE_SHIFT, livet.stateD,0,WIDTH_OF_THE_SHIFT,  livet.stateF,0,WIDTH_OF_THE_SHIFT,\
                               livet.stateC,0,WIDTH_OF_THE_SHIFT, livet.stateG,DAC_SHIFT_VALUE_UPPER,WIDTH_OF_THE_SHIFT)



        elif ECCType == 1:
            ERROR_TYPE = "UECC"

            if corruptLocation.isTrueBinaryBlock:#SLC

                DAC_SHIFT_VALUE = -100
                AdjList = (livet.stateLM,DAC_SHIFT_VALUE,WIDTH_OF_THE_SHIFT)

            else:

                DAC_SHIFT_VALUE_LOWER = -100
                DAC_SHIFT_VALUE_MIDDLE = -100
                DAC_SHIFT_VALUE_UPPER = -100

                AdjList=(livet.stateA,DAC_SHIFT_VALUE_LOWER,WIDTH_OF_THE_SHIFT, livet.stateE,DAC_SHIFT_VALUE_LOWER,WIDTH_OF_THE_SHIFT,\
                         livet.stateB,DAC_SHIFT_VALUE_MIDDLE,WIDTH_OF_THE_SHIFT, livet.stateD,DAC_SHIFT_VALUE_MIDDLE,WIDTH_OF_THE_SHIFT, \
                         livet.stateF,DAC_SHIFT_VALUE_MIDDLE,WIDTH_OF_THE_SHIFT,\
                         livet.stateC,DAC_SHIFT_VALUE_UPPER,WIDTH_OF_THE_SHIFT, livet.stateG,DAC_SHIFT_VALUE_UPPER,WIDTH_OF_THE_SHIFT)

        StmObj=livetFlash.CreateSTM(corruptLocation.chip,corruptLocation.die,AdjList)
        self.logger.Info("", "Injecting %s to location :%s with the \n\t\t AdjustementList as %s"%(ERROR_TYPE,corruptLocation,AdjList))
        livetFlash.ApplySTMtoWordline(StmObj,corruptLocation.chip,corruptLocation.die,corruptLocation.plane,\
                                                     corruptLocation.block,corruptLocation.wordLine,REVERT_ON_ERASE)
        return

    def __EccInjectInModel(self,corruptLocation,  errorByte , numOfBits ):
        """
        Name          :      __EccInjectInModel
        Description   :      Injects error into the given address for model protocol

        Arguments     :
        corruptLocation:           The physical location where the error would be injected
        This has:
        - die,
        - plane,
        - block
        - wordLine
        - mlcLevel
        - eccpage

          errorByte:           Starting location for the ECC corruption
                               (default = Byte 14) #to avoid corrupting the header(??)


          numOfBits:           Number of bit errors to create
                               If numOfBits is defined, errorType will be ignored
                               If numOfBits is undefined, the function will determine the
                               number of bits to corrupt
        Returns       :      None

        Note          :      The no. of errors that are alredy present in the ECC FIELD are not taken care of
        while calculating the no. of errors to be injected.
        This is so because we can not read the ECC FIELD DATA with and with out ecc correction

        """
        Livet = self.vtfContainer._livet

        DELAY_TO_RECOVERY=100
        BITS_PER_BYTE=8

        bitsToCorrupt=numOfBits
        self.logger.Debug("", "[__ECCInjectInModel] Number of bits to corrupt = %i" %(bitsToCorrupt))
        self.logger.Debug("", "[__ECCInjectInModel] Injecting ECC Error using Set Logical Trigger" )
        errorType       =Livet.etBadBit
        errorPersistence=Livet.epHard
        delayToOccurence=0             #No delay to occurrence
        delayToRecovery =DELAY_TO_RECOVERY
        errorByteOffset =errorByte

        package      = corruptLocation.chip
        endOfEccPage = self.__fwConfigData.bytesPerSector * self.__fwConfigData.sectorsPerEccPage

        #The Ecc page passed in this does not make much sense. it is redundant, hence removing it and passing 0
        #address=(corruptLocation.die ,corruptLocation.plane ,corruptLocation.block,corruptLocation.wordLine,corruptLocation.mlcLevel,corruptLocation.eccPage)

        # Enable WordLine/MLCPage addressing mode.
        #Livet.GetFlash().SetVariable('report_wordline_addresses','on')

        if (corruptLocation.isTrueBinaryBlock):
            self.logger.Debug("", "[__ECCInjectInModel] The block is in true binary mode...")

        if self.__fwConfigData.isBiCS:
            address=(corruptLocation.die,corruptLocation.plane, corruptLocation.block, corruptLocation.wordLine,corruptLocation.string, corruptLocation.mlcLevel, 0)
        else:
            address=(corruptLocation.die,corruptLocation.plane, corruptLocation.block, corruptLocation.wordLine, corruptLocation.mlcLevel, 0)

        eccPagesPerPhysicalPage = self.__fwConfigData.eccPagesPerMlcPage

        # If the eccPageNumber > 3, the ecc page belongs to the page in the next pseudo plane.
        # Hence, adding the bytesPerPage value provided by Model and recalculating the eccPageNumber=eccPageNumber%4
        if corruptLocation.eccPage >= eccPagesPerPhysicalPage:
            errorByteOffset = errorByteOffset + self.__modelBytesPerPage+((corruptLocation.eccPage% eccPagesPerPhysicalPage)\
                              * (self.__fwConfigData.eccFieldSize  + self.__fwConfigData.headerSizeInBytes + \
                              self.__fwConfigData.bytesPerSector * self.__fwConfigData.sectorsPerEccPage))
        else:
            #model does take care of Ecc Page number, so making changes to error byte to take this into account
            errorByteOffset = errorByteOffset + (corruptLocation.eccPage  * (self.__fwConfigData.eccFieldSize + \
                              self.__fwConfigData.headerSizeInBytes + self.__fwConfigData.bytesPerSector * \
                              self.__fwConfigData.sectorsPerEccPage))

        while bitsToCorrupt:
            if bitsToCorrupt < BITS_PER_BYTE:
                count=bitsToCorrupt
                bitsToCorrupt=0
            else:
                count = BITS_PER_BYTE
                bitsToCorrupt = bitsToCorrupt-count
            # Calculate Byte Mask
            errorByteMask = 0
            while(count):
                errorByteMask = (errorByteMask<<1) | 0x01
                count = count - 1
            errorDescription=(errorType,errorPersistence,delayToOccurence,delayToRecovery,errorByteOffset,errorByteMask)
            Livet.GetFlash().InjectError(package, address, errorDescription)
            self.logger.Debug("", "[__ECCInjectInModel] Error injected successfully on Physical address(%s) errorDescription(%s)"%(address,errorDescription))

        #checking if the eccpage boundary is being exceeded
            if errorByteOffset == endOfEccPage:
                errorByteOffset=0
            else:
                errorByteOffset=errorByteOffset+1

# end of  __EccInjectInModel()

    def ECCInjectInEachEccPage(self, corruptLocation, errorType = 0, errorByte = 14, numOfBits = None):
        """
        Name          :      ECCInjectInEachEccPage
        Description   :      Injects ecc error into each Ecc page of the perticular physical block
        Steps:
        Step 1: Read Physical data of whole block.
        Step 2: Inject Ecc error in the data read at step 1, in each ecc page of the block.
        Step 3: Erase the whole block
        Step 4: Write physical data got in step 2(With ecc error) to whole block.
        Step 5: Do additional check for each ecc page present in physical block

        Arguments     :

            corruptLocation:           The physical location where the error would be injected
                                       This has:
                                       - chip,
                                       - die,
                                       - plane,
                                       - block

            errorType:           Level of error injection, # of bits to corrupt is determined by the function.
                                 0 - Correctable
                                 1 - Uncorrectable
                                 RAND - randomly pick the level (correctabl/uncorrectable)
                                 (default = correctable)

            errorByte:           Starting location for the ECC corruption
                                 (default = Byte 14) #to avoid corrupting the header(??)


            numOfBits:           Number of bit errors to create
                                 If numOfBits is defined, errorType will be ignored
                                 If numOfBits is undefined, the function will determine the
                                 number of bits to corrupt
                                 (default = use errorType)

        Returns       :      None

        Note          :      Current algorithm only supports sequential bit corruption
        The no. of errors that are alredy present in the ECC FIELD are not taken care of
                             while calculating the no. of errors to be injected.
        This is so because we can not read the ECC FIELD DATA with and with out ecc correction
        """
        import General.ByteUtil as ByteUtil
        if not self.vtfContainer.isModel:
            if (not(corruptLocation.isTrueBinaryBlock) and (self.__fwConfigData.mlcLevel == 3)):
                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "[ECCInject] Block is in D3 memory; Can not inject ECC errors!!")

        if (self.__fwConfigData.mlcLevel == 3):
            if corruptLocation.isTrueBinaryBlock :
                self.usedMlcPages = [0]
            else:
                self.usedMlcPages = [0,1,2]
        if  (self.__fwConfigData.mlcLevel == 2):
            if corruptLocation.isTrueBinaryBlock :
                self.usedMlcPages = [0]
            else:
                self.usedMlcPages = [0,1]

        #Suspend the back ground maintenance operations
        self.sctpUtils.DoBackGroundMaintenanceOperations(SUSPEND_BACK_GROUND_OPERATIONS)

        ALL_ZEROS = 0X00

        # Check if input parameters are valid
        if (errorType != self.__CORRECTABLE) and (errorType != self.__UNCORRECTABLE) and\
           (errorType != self.__RAND):
            raise ValueError("Invalid ECC error level, errorType=%i" %(errorType))

        # Step 1: Read Physical data of whole block.
        self.__blockDataBuffer  = self.__physicalBlockRead(physicalLocation = corruptLocation)
        if corruptLocation.isTrueBinaryBlock:
            totalPagesInBlock = old_div(self.__fwConfigData.pagesPerMlcBlock,self.__fwConfigData.mlcLevel)
        else:
            totalPagesInBlock = self.__fwConfigData.pagesPerMlcBlock

        # Save the original data of block before curruption
        blockDataBufferOriginal = pyWrap.Buffer.CreateBuffer(totalPagesInBlock*\
                                                self.__fwConfigData.sectorsPerRawMlcPage,ALL_ZEROS)
        blockDataBufferOriginal.Copy(self.__blockDataBuffer)

        #Step 2: Inject Ecc error in the data read at step 1, in each ecc page of the block.
        self.__InjectErrorInEachECCPage(physicalLocation = corruptLocation, errorType = errorType, errorByte = errorByte, numOfBits = numOfBits)

        if not self.vtfContainer.isModel:

            #This issues Diag internally
            self.__card.EraseBlock(corruptLocation.chip,corruptLocation.die, corruptLocation.plane, corruptLocation.block,
                                   1, true_binary=corruptLocation.isTrueBinaryBlock)

            # step 4: Write the whole block

            if len(self.usedMlcPages) == 2:
                self.__physicalBlockWriteD2(corruptLocation)
            else:
                self.__physicalBlockWrite(corruptLocation)

            # Step 5 : Do additional check for each ecc page present in physical block
            if corruptLocation.isTrueBinaryBlock:
                pagesToCheck = old_div(self.__fwConfigData.pagesPerMlcBlock,self.__fwConfigData.mlcLevel)
            else:
                pagesToCheck = self.__fwConfigData.pagesPerMlcBlock

            eccPagesPerMlcPage        = self.__fwConfigData.eccPagesPerMlcPage
            for pageCount in range(0,pagesToCheck):
                for eccPageCount in range(0,eccPagesPerMlcPage):
                    #adding page and ecc value to corruption location
                    corruptLocation.wordLine = old_div(pageCount,len(self.usedMlcPages))
                    corruptLocation.mlcLevel = pageCount % len(self.usedMlcPages)
                    corruptLocation.eccPage = eccPageCount

                    eccPageDataBeforeCorruption = pyWrap.Buffer.CreateBuffer(self.__fwConfigData.sectorsPerRawEccPage,ALL_ZEROS)
                    # calculating the offset of ECC page in Block buffer
                    corruptEccPage = ((corruptLocation.wordLine * len(self.usedMlcPages) + corruptLocation.mlcLevel)* self.__fwConfigData.eccPagesPerMlcPage) + corruptLocation.eccPage
                    corruptedEccPageOffSet = (corruptEccPage * self.__fwConfigData.sectorsPerRawEccPage * Constants.FwConfig_CONSTANTS.BE_SPECIFIC_BYTES_PER_SECTOR)

                    #check first whether  page is erased
                    if not self.IsErasedPage(self.__blockDataBuffer,corruptedEccPageOffSet):
                        #getting ecc page data before curruption
                        eccPageDataBeforeCorruption.Copy(blockDataBufferOriginal, 0,corruptedEccPageOffSet,self.__fwConfigData.sectorsPerRawEccPage * Constants.FwConfig_CONSTANTS.BE_SPECIFIC_BYTES_PER_SECTOR)
                        # call additional checks function
                        self.__AdditionalChecks(corruptLocation,errorByte,eccPageDataBeforeCorruption,corruptedEccPageOffSet)
                    #end of if
                #end of for loop of eccPageCount
            #end of for loop of pageCount
        #end of if-else IsProtocolModel

        #Resume the back ground maintenance operations
        self.sctpUtils.DoBackGroundMaintenanceOperations(RESUME_BACK_GROUND_OPERATIONS)
    # end of  ECCInjectInEachEccPage()

    def physicalBlockRead(self, physicalLocation,option=None):
        """
        Description: Wrapper for __physicalBlockRead
        """
        blockDataBuffer = self.__physicalBlockRead(physicalLocation,option)
        return blockDataBuffer

    def __physicalBlockRead(self, physicalLocation,option=None):
        """
        Returns buffer containing the whole block data
        """
        if physicalLocation.isTrueBinaryBlock:
            #if block is true binary,totalPagesInBlock = pagesPerPhysBlock/mlcLevel -- for D2 memory,mlcLevel=2
            totalPagesInBlock = old_div(self.__fwConfigData.pagesPerMlcBlock, self.__fwConfigData.mlcLevel)
            self.usedMlcPages = [0] #for accessing only lower pages
        else:
            totalPagesInBlock = self.__fwConfigData.pagesPerMlcBlock

        # create block and temp block buffers
        blockDataBuffer = pyWrap.Buffer.CreateBuffer(size = totalPagesInBlock *\
                                        self.__fwConfigData.sectorsPerRawMlcPage,
                                        initialFillPattern = self.__initialFillPattern)
        blockDataTempBuff = pyWrap.Buffer.CreateBuffer(size = totalPagesInBlock *\
                                          self.__fwConfigData.sectorsPerRawMlcPage,
                                          initialFillPattern = self.__initialFillPattern)
        if option == None:
            option = 0x20# read scrambled data

        tempPhysicalAddress = AddressTypes.PhysicalAddress()
        tempPhysicalAddress.chip = physicalLocation.chip;tempPhysicalAddress.die = physicalLocation.die
        tempPhysicalAddress.plane = physicalLocation.plane;tempPhysicalAddress.block = physicalLocation.block
        tempPhysicalAddress.isTrueBinaryBlock = physicalLocation.isTrueBinaryBlock
        tempPhysicalAddress.eccPage = 0
        tempPhysicalAddress.mlcLevel = 0
        tempPhysicalAddress.wordLine = 0

        #Loop through reading the entire block in chunks
        while(tempPhysicalAddress.wordLine < self.__fwConfigData.wordLinesPerPhysicalBlock_BiCS):
            for mlcLevel in self.usedMlcPages:
                tempPhysicalAddress.mlcLevel = mlcLevel
                for string in range(0,self.__fwConfigData.stringsPerBlock):
                    tempPhysicalAddress.string = string

                    self.logger.Debug("", "ECC page read: Chip = 0x%04x; Die = 0x%04x; Plane = 0x%04x; Block = 0x%04x; WL = 0x%04x;  String = 0x%04x; MLC Level = 0x%04x, Ecc Pg = 0x%04x"%\
                                       (tempPhysicalAddress.chip,tempPhysicalAddress.die,tempPhysicalAddress.plane,tempPhysicalAddress.block,tempPhysicalAddress.wordLine,\
                                        tempPhysicalAddress.string,tempPhysicalAddress.mlcLevel,tempPhysicalAddress.eccPage))
                    ReadEccPage(blockDataTempBuff, tempPhysicalAddress,self.__fwConfigData.eccPagesPerMlcPage, option)

                    blockDataBuffer.Copy(sourceBuf = blockDataTempBuff, thisOffset = \
                                         ((tempPhysicalAddress.wordLine*self.__fwConfigData.stringsPerBlock)+tempPhysicalAddress.string)* ((self.__fwConfigData.eccPagesPerPage * (self.__fwConfigData.stringsPerBlock+1)) * 512),
                                         sourceOffset = 0, byteCount = (self.__fwConfigData.eccPagesPerPage * (self.__fwConfigData.stringsPerBlock+1) * 512))

            #incrementing wordLine
            tempPhysicalAddress.wordLine = tempPhysicalAddress.wordLine + 1

        return blockDataBuffer
    # end of __physicalBlockRead()

    def __physicalBlockWriteD2(self, physicalLocation):
        """
        Separate physical write function since for D2 non-true binary write, write should exactly follow nand sequence(LLULUL) in WL/mlcLevel addressing
        """
        isBlockInTrueBinaryMode = physicalLocation.isTrueBinaryBlock
        wordLinePerBlock = old_div(self.__fwConfigData.pagesPerMlcBlock, self.__fwConfigData.mlcLevel)
        sequence =  [[0,0],[1,0]]
        loopCount =wordLinePerBlock*2-3
        mlcLevel = 0
        wordLine = 1
        for count in range(loopCount):
            if mlcLevel:
                wordLine = wordLine + 2
                mlcLevel = 0
            else:
                wordLine = wordLine -1
                mlcLevel = 1

            sequence.append([wordLine, mlcLevel])
        #end
        sequence.append([wordLinePerBlock -1, 1])
        totalPagesInBlock = old_div(self.__fwConfigData.pagesPerMlcBlock, self.__fwConfigData.mlcLevel)
        # create temp block buffers
        blockDataTempBuff = pyWrap.Buffer.CreateBuffer(size = totalPagesInBlock *\
                                          self.__fwConfigData.sectorsPerRawMlcPage,
                                          initialFillPattern = self.__initialFillPattern)

        # Loop through reading the entire block in chunks
        tempPhysicalLocation = AddressTypes.PhysicalAddress()
        tempPhysicalLocation.chip = physicalLocation.chip;tempPhysicalLocation.die = physicalLocation.die
        tempPhysicalLocation.plane = physicalLocation.plane;tempPhysicalLocation.block = physicalLocation.block
        tempPhysicalLocation.isTrueBinaryBlock = physicalLocation.isTrueBinaryBlock
        tempPhysicalLocation.wordLine = 0
        tempPhysicalLocation.eccPage= 0
        option = 0x20
        #option = GetReadWriteEccPageOption(physicalLocation.inD1, False, True, False)

        for [tempPhysicalLocation.wordLine,tempPhysicalLocation.mlcLevel] in sequence :
            blockDataTempBuff.Copy(sourceBuf = self.__blockDataBuffer, thisOffset = 0,
                                   sourceOffset = (tempPhysicalLocation.wordLine*len(self.usedMlcPages) + tempPhysicalLocation.mlcLevel) * self.__fwConfigData.bytesPerRawPhysicalPage,
                                   byteCount = self.__fwConfigData.bytesPerRawPhysicalPage)
            if not self.IsErasedPage(blockDataTempBuff, 0):
                WriteEccPage(blockDataTempBuff, tempPhysicalLocation,self.__fwConfigData.eccPagesPerMlcPage,option)

    def __physicalBlockWrite(self, physicalLocation):
        """
        write to the whole physical block
        """
        if physicalLocation.isTrueBinaryBlock:
            #if block is true binary,totalPagesInBlock = pagesPerPhysBlock/mlcLevel -- for D2 memory,mlcLevel=2
            totalPagesInBlock = old_div(self.__fwConfigData.pagesPerMlcBlock, self.__fwConfigData.mlcLevel)
            self.usedMlcPages = [0] #for accessing only lower pages
        else:
            totalPagesInBlock = self.__fwConfigData.pagesPerMlcBlock

        # create temp block buffers
        blockDataTempBuff = pyWrap.Buffer.CreateBuffer(size = totalPagesInBlock *\
                                          self.__fwConfigData.sectorsPerRawMlcPage,
                                          initialFillPattern = self.__initialFillPattern)

        # Loop through writing the entire block in chunks
        option = 0x20# write without scrambling the data
        tempPhysicalAddress = AddressTypes.PhysicalAddress()
        tempPhysicalAddress.chip = physicalLocation.chip;tempPhysicalAddress.die = physicalLocation.die
        tempPhysicalAddress.plane = physicalLocation.plane;tempPhysicalAddress.block = physicalLocation.block
        tempPhysicalAddress.isTrueBinaryBlock = physicalLocation.isTrueBinaryBlock
        tempPhysicalAddress.eccPage = 0
        tempPhysicalAddress.mlcLevel = 0
        tempPhysicalAddress.wordLine = 0

        while (tempPhysicalAddress.wordLine < self.__fwConfigData.wordLinesPerPhysicalBlock_BiCS):
            for mlcLevel in self.usedMlcPages:
                blockDataTempBuff.Copy(sourceBuf = self.__blockDataBuffer, thisOffset = 0,
                                       sourceOffset = (tempPhysicalAddress.wordLine*len(self.usedMlcPages)+mlcLevel) * self.__fwConfigData.bytesPerRawPhysicalPage,
                                       byteCount = self.__fwConfigData.bytesPerRawPhysicalPage)

                if not self.IsErasedPage(blockDataTempBuff, 0):
                    tempPhysicalAddress.mlcLevel = mlcLevel
                    WriteEccPage(blockDataTempBuff, tempPhysicalAddress, self.__fwConfigData.eccPagesPerMlcPage,option)
                #End of if not..

            #incrementing wordLine
            tempPhysicalAddress.wordLine = tempPhysicalAddress.wordLine + 1
        return
    # end of __physicalBlockWrite()

    def __InjectError(self, physicalLocation,  errorByte, numOfBits ):

        if self.vtfContainer.isModel:
            # if card protocol is model use
            self.__EccInjectInModel(physicalLocation,errorByte,numOfBits)

        else:

            # Convert bit count to a bit mask
            count = numOfBits
            eCCBitMask = 0
            while(count):
                eCCBitMask = (eCCBitMask<<1) | 0x01
                count = count - 1

            self.logger.Debug("", "[ECCInject] Number of bits to corrupt = %i, error bit mask = 0x%x, error location = %i" %(numOfBits, eCCBitMask, errorByte))

            # Corrupt the host buffer (bit mask may be more than 1 byte), corrupt 1 byte at a time
            page           = physicalLocation.wordLine * len(self.usedMlcPages) + physicalLocation.mlcLevel
            corruptEccPage = (page * self.__fwConfigData.eccPagesPerMlcPage) + physicalLocation.eccPage
            pError         = (corruptEccPage * self.__fwConfigData.sectorsPerRawEccPage * Constants.FwConfig_CONSTANTS.BE_SPECIFIC_BYTES_PER_SECTOR) + errorByte
            while (eCCBitMask):
                # Use bitwise xor corruption
                self.__blockDataBuffer[pError] = self.__blockDataBuffer[pError] ^ (eCCBitMask & 0xFF)
                eCCBitMask = eCCBitMask >> 8
                pError = pError + 1

    # end of __InjectError()

    def __InjectErrorInEachECCPage(self, physicalLocation,errorType,  errorByte, numOfBits ):
        """
        Name          :    __InjectErrorInEachECCPage
        Description   :    This function inject ecc errors in each ecc page of the given physical block location
                          Step used:
        Step 1 : Get number of ecc error bits has to inject
        Step 2 : Inject error in specific location (given by 'errorByte' ) in Ecc pages
        Step 3 : Do step 1 and 2 for each ecc page present in corresponding physical block

        Arguments     :
           physicalLocation :  Physical Location of block where error has to inject
        errorType        :  Level of error injection, # of bits to corrupt is determined by the function.
        0 - Correctable
        1 - Uncorrectable
        RAND - randomly pick the level (correctabl/uncorrectable)
                                 (default = correctable)
        errorByte      :    Starting location for the ECC corruption

        numOfBits       :   Number of bit errors to create
        If numOfBits is defined, errorType will be ignored
        If numOfBits is undefined, the function will determine the
        number of bits to corrupt
        (default = use errorType)

        Return        :  None

        """

        # Get physical information of the ECC page
        sectorsPerRawEccpage          = self.__fwConfigData.sectorsPerRawEccPage
        bytesPerSector                = self.__fwConfigData.bytesPerSector
        eccPagesPerMlcPage        = self.__fwConfigData.eccPagesPerMlcPage

        self.logger.Warning("", "[InjectErrorInEachECCPage] Injecting Error in Each Ecc page of physical block corresponds to "+\
                              "Chip:%d Die:%d Plane:%d Block:0x%X Wordline:0x%x,mlcLevel:0x%x,inD1:%d"%(physicalLocation.chip,physicalLocation.die,physicalLocation.plane,
                                                                                                        physicalLocation.block,physicalLocation.wordLine,physicalLocation.mlcLevel
                                                                                                        ,physicalLocation.isTrueBinaryBlock))
        if physicalLocation.isTrueBinaryBlock:
            pagesToCorrupt = old_div(self.__fwConfigData.pagesPerMlcBlock, self.__fwConfigData.mlcLevel)
        else:
            pagesToCorrupt = self.__fwConfigData.pagesPerMlcBlock

        # currupting the each ecc page of block
        for pageCount in range(0,pagesToCorrupt):
            for eccPageCount in range(0,eccPagesPerMlcPage):
                #adding page and ecc value to corruption location
                physicalLocation.wordLine = old_div(pageCount,len(self.usedMlcPages))
                physicalLocation.mlcLevel = pageCount % len(self.usedMlcPages)
                physicalLocation.eccPage = eccPageCount

                #calculating the offset of ECC page in Block buffer
                corruptEccPage = ((physicalLocation.wordLine * len(self.usedMlcPages) + physicalLocation.mlcLevel) * eccPagesPerMlcPage) + physicalLocation.eccPage
                corruptedEccPageOffSet = (corruptEccPage * sectorsPerRawEccpage * bytesPerSector)

                #check first whether  page is erased
                if not self.IsErasedPage(self.__blockDataBuffer,corruptedEccPageOffSet ) :
                    #inject error in specific location in Ecc pages
                    # Determine the number of bits to corrupt
                    curNumOfBits = self.__GetNumOfErrorBits(physicalLocation,errorType,numOfBits)
                    self.logger.Debug("", "[InjectErrorInEachECCPage] Injecting %d errors to physical location "%curNumOfBits+ "%s" %(physicalLocation))
                    if curNumOfBits >0 :
                        self.__InjectError(physicalLocation, errorByte, curNumOfBits )

            #end of for eccPageCount in range(0,eccPagesPerMlcPage):
        #end of for pageCount in range(0,pagesToCorrupt):
    #end of __InjectErrorInEachECCPage()

    def IsErasedPage(self,dataBuffer,startOfEccPage):
        """
        Name          :    IsErasedPage
        Description   :    This function check whether the ecc page is erased or not.
        It checks header segment of ECC page alone.
        Arguments     :
           dataBuffer     : The data buffer in which erased pattern has to check
        startOfEccPage : Byte offset of start of ecc page in data buffer

        Return        :
             pageErasedFlag :  True  - if eccpage is erased
        False - if eccpage is not erased

        """
        pageErasedFlag = False
        erasedBuf = self.__ErasedEccBuffer
        #checking Header Data ecc page buffer
        byteCount = self.__fwConfigData.headerSizeInBytes
        erasedPatternCount = 0
        for count in range(byteCount):
            if self.__ErasedEccBuffer[count] == dataBuffer[startOfEccPage+count]:
                #increment the erasedPatternCount counter.
                erasedPatternCount = erasedPatternCount + 1

        # Due to an used NAND some bits would have been corrupted and will never program.So there are chances that we will not
        # find 0xFF in every byte. So if at least half of the bytes are 0xFF, we will consider this page as erased.
        if erasedPatternCount > byteCount * 0.7:
            pageErasedFlag = True

        else:
            #the ecc page is not erased
            pageErasedFlag = False

        #if (pageBuffer.GetFourBytesToInt(startOfEccPage)== self.__FourByteErasepattern) and (pageBuffer.GetFourBytesToInt(startOfEccPage+4)==self.__FourByteErasepattern) \
                        #and  (pageBuffer.GetFourBytesToInt(startOfEccPage+8)== self.__FourByteErasepattern) and (pageBuffer.GetFourBytesToInt(startOfEccPage+12)== self.__FourByteErasepattern)\
                        #and (pageBuffer.GetFourBytesToInt(startOfEccPage+20)==self.__FourByteErasepattern) and (pageBuffer.GetFourBytesToInt(startOfEccPage+40)==self.__FourByteErasepattern):
            #pageErasedFlag = True

        return pageErasedFlag


    def __AdditionalChecks(self,corruptLocation,errorByte,eccPageDataBeforeCorruption,corruptedEccPageOffSet ):
        """
        Name          :   __AdditionalChecks
        Description   :    This function check whether the ecc page is erased or not.

        Arguments     :
           corruptLocation : The physical location where the error has been injected
                                       This has:
                                       - chip,
                                       - die,
                                       - plane,
                                       - block,
                                       - wordLine,
        - mlcLevel,
                                       - eccPage
        errorByte     :     Starting location for the ECC corruption

        eccPageDataBeforeCorruption : Ecc page data before curruption
        corruptedEccPageOffSet  :   The eccPage offset in block data buffer
        Return        :  Raise  the exception error is not injected properly
        """
        SINGLE_ECC_PAGE = 1
        ALL_ZEROS = 0X00
        # Additionl check1
        #         For error injection; the errors that are present in a physical location prior
        #         to the ecc injection are taken care of in the module used to modify the write buffer
        #         before doing a physical write ( this is done in the module __InjectError)
        #         This check could not be done for the ECC FIELD of the ECC Page
        #          - so if the data corruption is targetted at the ECC FIELD then,
        #            we inject the error and read the written data back and check whether the intended error has been
        #            injected into the ECC FIELD or not

        headerAndUserDataSize = self.__fwConfigData.headerSizeInBytes +\
                     self.__fwConfigData.bytesPerSector *  self.__fwConfigData.sectorsPerEccPage
        eccFieldDataOffset = headerAndUserDataSize
        if (errorByte >= eccFieldDataOffset):# do the check
            option = 0x20# read scrambled data
            # get the corruption data, this is the data that is intended to be written to the physical location after injectig the error
            corruptionData = pyWrap.Buffer.CreateBuffer(self.__fwConfigData.sectorsPerRawEccPage,ALL_ZEROS)
            corruptionData.Copy(self.__blockDataBuffer, 0,corruptedEccPageOffSet,self.__fwConfigData.sectorsPerRawEccPage *  Constants.FwConfig_CONSTANTS.BE_SPECIFIC_BYTES_PER_SECTOR)

            # get the actual data written
            writtenData = pyWrap.Buffer.CreateBuffer(self.__fwConfigData.sectorsPerRawEccPage,ALL_ZEROS)
            ReadEccPage(writtenData, corruptLocation,SINGLE_ECC_PAGE,option)

            # Compare the data
            try:
                writtenData.Compare(corruptionData,eccFieldDataOffset,eccFieldDataOffset,self.__fwConfigData.eccFieldSize)
            except:# there is a miss compare so inform this to the user
                self.logger.Warning("", "[ECCInject] The error injection was not succesfully done since there are some errors"
                                      " already presetn at the specified location - try changing the physical location or the"
                                      "no. of the bits to be corrupted if the intended results are not out at the ened of the test ")

        # Additional Check2
        #         If the no. of bits to be corrupted is not greater than the correctable level
        #         then compare the ecc page data after error injection with the data read before
        #         error injection and if the no. of errors injected is beyond the correctable
        #         ecc level then assert it saying that this has happened because of BAD NAND
        if not self.__numOfBitsToCorrupt > self.__fwConfigData.correctableEccLevel:
            # read the raw data after the error injection
            option = 0x20# read scrambled data
            writtenData = pyWrap.Buffer.CreateBuffer(self.__fwConfigData.sectorsPerRawEccPage,ALL_ZEROS)
            ReadEccPage(writtenData, corruptLocation,SINGLE_ECC_PAGE,option)

            # count the no. of flip bits when compared with the data read before error injection
            noOfFlippedBitsAfterInjection = self.GetFlippedBitCount(eccPageDataBeforeCorruption, writtenData, headerAndUserDataSize)
            # if this count is more than the corretable ecc level assert it
            if noOfFlippedBitsAfterInjection > self.__fwConfigData.correctableEccLevel:
                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "[ECCInject] the no. of errors injected is beyond the correctable ecc level \n"
                                                "\tThis has happened because of BAD NAND")
            option = 0x20# read scrambled data
            # get the corruption data, this is the data that is intended to be written to the physical location after injectig the error
            corruptionData = pyWrap.Buffer.CreateBuffer(self.__fwConfigData.sectorsPerRawEccPage,ALL_ZEROS)
            corruptionData.Copy(self.__blockDataBuffer, 0,corruptedEccPageOffSet,self.__fwConfigData.sectorsPerRawEccPage * Constants.FwConfig_CONSTANTS.BE_SPECIFIC_BYTES_PER_SECTOR)

            # Compare the data
            try:
                writtenData.Compare(corruptionData,eccFieldDataOffset,eccFieldDataOffset,self.__fwConfigData.eccFieldSize)
            except Buffer.MiscompareError as exc:# there is a miss compare so inform this to the user
                self.logger.Warning("", "[ECCInject] The errro injection was not succesfully there are more or less bit flips than expected ")

    #end of __AdditionalChecks()

    def __GetNumOfErrorBits(self,physicalLocation,errorType,numOfBits):
        """
        Name          :      __GetNumOfErrorBits
        Description   :      This function returns the number of ecc error bits has to inject for perticular
        ecc page based on 'errorType' and 'numOfBits'.
        This function based on following algorithm
        Step 1 : Calculate the number of errors already present at the ecc page, say this number is 'X'
        Step 2 : If 'numOfBits' is None then 'number of error bits'( say N) are calculated from type of error has to inject
        Step 3 : If 'numberOfBits' is  positive number it will concider as 'number of error bits'( say N).
        Step 4 : Finally number of error bit has to injet is calculated as (N-X)

        Arguments     :
           physicalLocation :  Physical Location where error has to inject
        errorType        :  Level of error injection, # of bits to corrupt is determined by the function.
        0 - Correctable
        1 - Uncorrectable
        RAND - randomly pick the level (correctabl/uncorrectable)
                                 (default = correctable)

        numOfBits       :   Number of bit errors to create
        If numOfBits is defined, errorType will be ignored
        If numOfBits is undefined, the function will determine the
        number of bits to corrupt
        (default = use errorType)

        Return        :
        numOfBits:           Number of bit errors to create
        """

        MARGIN_ECC = 2         # ECC Margin for creating ecc errors (Max-margin=MaxFlufCorrectable)

        existingErrorCount = 0
        fwConfigData = self.__fwConfigData
        # get the count of the errors that are already present at the physical location
        existingErrorCount = self.GetExistingErrorCount(physicalLocation)

        if (numOfBits == None):
            correctableEccLevel = self.__fwConfigData.correctableEccLevel
            # if num of bits are not mentioned use Correctable or uncorrectable or randomly select between the above two
            if (errorType == self.__RAND): errorType  = self.globalVars.randomObj.randint(0, 1)

            if(errorType == self.__CORRECTABLE):
                if existingErrorCount <= (correctableEccLevel - MARGIN_ECC):
                    numOfBits = self.globalVars.randomObj.randint(existingErrorCount, correctableEccLevel - MARGIN_ECC)
                else:
                    numOfBits = 0
                self.__numOfBitsToCorrupt = numOfBits # this parameter is used for check at the end of injection
                # take care of the already present errors -so error count will not exceed CECC count
                numOfBits = numOfBits - existingErrorCount
                self.logger.Debug("", "[GetNumOfErrorBits] Type Of ECC Error : Correctable   ")


            elif(errorType == self.__UNCORRECTABLE):
                numOfBits = self.globalVars.randomObj.randint(correctableEccLevel + 5, correctableEccLevel + 20 )
                self.__numOfBitsToCorrupt = numOfBits # this parameter is used for check at the end of injection
                self.logger.Debug("", "[GetNumOfErrorBits] Type Of ECC Error : Uncorrectable   ")

            else:
                raise ValueError("Invalid errorType parameter was provided (range[0,1]). errorType = ", errorType)

        # take care of the already present errors -so error count will not exceed CECC count
        else:
            correctableEccLevel = fwConfigData.correctableEccLevel
            self.__numOfBitsToCorrupt = numOfBits # this parameter is used for check at the end of injection
            numOfBits = numOfBits - existingErrorCount# take care of the already present errors
            if (numOfBits > correctableEccLevel):
                #Record the test event: NumberOfUECCInjected
                ValidationTestEvents_Obj = ValidationTestEvents.ValidationTestEvents(self.logger)
                ValidationTestEvents_Obj.RecordTestEvent('ECC_TE_NumberOfUECCInjected')
            else:
                #Record the test event: NumberOfCECCInjected
                ValidationTestEvents_Obj = ValidationTestEvents.ValidationTestEvents(self.logger)
                ValidationTestEvents_Obj.RecordTestEvent('IFS_TE_NumberOfCECCInjected')
        #if number of bits calculated become negative, make it  to zero
        if(numOfBits < 0):
            numOfBits = 0
        self.logger.Debug("", "[GetNumOfErrorBits]  Number of Error Bits : %d   "%numOfBits)

        return numOfBits
    #end of __GetNumOfErrorBits()

    def GetSectorData(self, readRawBuffer, sectorPositionInEccPage):
        """
        Name :              GetSectorData()

        Description:        coppies the logical data part of a sector form
                            the EccPage data to a one sector  buffer

        Arguments:
           self             - class instance
           readRawBuffer    - the 5 sector buffer with the readEcPage data
           sectorPositionInEccPage - the position of the sector in the EccPage

        Returns -    sectorBuffer

        """
        bytestPerSector = self.__fwConfigData.bytesPerSector# one sector
        OFFSET_ZERO = 0# to the beginning
        sectorSize = 1#sectors
        initialFillPattern = 0x00

        # create a temp buffer and copy the one sector data into it and send it to the caller
        sectorBuffer = pyWrap.Buffer.CreateBuffer(size = sectorSize, initialFillPattern = initialFillPattern)
        readRawBufferOffset = self.__fwConfigData.headerSizeInBytes +\
                            (bytestPerSector * sectorPositionInEccPage)
        sectorBuffer.Copy(sourceBuf = readRawBuffer, thisOffset = OFFSET_ZERO,
                          sourceOffset = readRawBufferOffset, byteCount = bytestPerSector)
        return sectorBuffer
    # end of GetSectorData()

    def GetExistingErrorCount(self, physicalLocation):
        """
        Name :              GetExistingErrorCount()

        Description:        This function counts the no. of ECC errors that
                            are present in a specified location( an ecc page)

        Arguments:
           self                        - class instance
           physicalLocation:           The physical location where the errors are to be counted
                                       This has:
                                       - chip,
                                       - die,
                                       - plane,
                                       - block,
        - wordLine
        - mlcLevel
                                       - eccPage

        Returns:
           existingErrorCount:        The count of the Ecc Errors that are present in the
                                      specified physical location.
        """
        headerSizeInBytes = self.__fwConfigData.headerSizeInBytes
        numOfBytesInOneSector = self.__fwConfigData.bytesPerSector
        numOfEccBytes = self.__fwConfigData.eccFieldSize
        numOfSectorsInOneEccPage = self.__fwConfigData.sectorsPerEccPage
        numOfBytesInOneEccPage = headerSizeInBytes + (numOfBytesInOneSector * numOfSectorsInOneEccPage) + numOfEccBytes

        if self.vtfContainer.isModel== True:
            Model = self.vtfContainer._livet
            # setting a param/flag on to indicate model that WL addressing is being used
            #Model.GetFlash().SetVariable('report_wordline_addresses','on')
            package = physicalLocation.chip
            #column=0 for error injection
            flashAddr = (physicalLocation.die,physicalLocation.plane,physicalLocation.block,physicalLocation.wordLine,physicalLocation.mlcLevel,0)
            numOfBitsToScan = numOfBytesInOneEccPage
            existingErrorBitCount = Model.GetFlash().GetBadBitCount(package,flashAddr,numOfBitsToScan)
            return existingErrorBitCount

        ALL_ZEROS = 0x00
        SINGLE_ECC_PAGE = 1
        isTrueBinaryBlock = physicalLocation.isTrueBinaryBlock

        # step 1: Read the Ecc page data without unscrambling the data and with ECC correction enabled.
        option = 0x120
        EccCorrectedData = pyWrap.Buffer.CreateBuffer(self.__fwConfigData.sectorsPerRawEccPage, ALL_ZEROS)
        ReadEccPage(EccCorrectedData, physicalLocation,SINGLE_ECC_PAGE, option)

        # step 2: Read the Ecc page data without unscrambling the data and with ECC correction disabled.
        option = 0x20
        EccUncorrectedData = pyWrap.Buffer.CreateBuffer(self.__fwConfigData.sectorsPerRawEccPage, ALL_ZEROS)
        ReadEccPage(EccUncorrectedData, physicalLocation,SINGLE_ECC_PAGE,option)

        # Step 3: Get the count of the no. of bits flipped, this is the count of the bits that have been corrupted
        # check for errors only in the header and the data part - not in the ecc field
        byteCount = self.__fwConfigData.headerSizeInBytes +\
                     self.__fwConfigData.bytesPerSector *  self.__fwConfigData.sectorsPerEccPage

        return self.GetFlippedBitCount(bufferOne = EccCorrectedData, bufferTwo = EccUncorrectedData,
                                       bytesToCompare = byteCount)

    # end of GetExistingErrorCount()

    def GetFlippedBitCount(self, bufferOne = None, bufferTwo = None, bytesToCompare = None):
        """
        Name :              GetFlippedBitCount()

        Description:        This function counts the no. of bits that are flipped in one buffer
                            wrt the other buffer and this check is made for the no. of bytes specified by the user

        Arguments:
           self                        - class instance
           bufferOne                   - one of the two buffers to be compared
           bufferTwo            bytesToCompare

        Returns:
           existingErrorCount:        The count of the Ecc Errors that are present in the
                                      specified physical location.

        Note: Since the errors present in the ECC field can not be determined
              we assume the persence of 2 errors in the ECC field

        """
        # do input parameter check
        if (bufferOne == None) or (bufferTwo == None) or (bytesToCompare == None):
            raise TestError.TestFailError(self.vtfContainer.GetTestName(), "[GetFlippedBitCount] Invalid input parameters given")

        TotalFlipBitCount = 0
        for byteOffSet in range(bytesToCompare):
            TotalFlipBitCount = TotalFlipBitCount + self.__CountFlipBits(bufferOne[byteOffSet], bufferTwo[byteOffSet])

        return TotalFlipBitCount
    # end of GetFlippedBitCount()

    def __CountFlipBits(self, byteOne, byteTwo):
        # counts the no. of the bits that are flipped
        flipBits = byteOne ^ byteTwo
        return self.__count1s(flipBits)
    # end of __CountFlipBits()

    def __count1s(self, num):
        # counts no. of 1s in a given no.
        count = 0
        while(num):
            num &= (num-1)
            count = (count + 1)
        return count
    # end of __count1s()

def ReadEccPage(vtfContainer,readBuffer,physicalAddress,eccPageCount,option, FwConfigObj):
    """
    Wrapper for card.ReadEccPage taking care of truebinary access for 32nmD2/D3
    """
    import ByteUtil, DiagnosticLib
    logger = vtfContainer.GetLogger()

    if FwConfigObj.isBiCS:
        opcode = 0xB1
        direction=0
        if option != 0x300:
            option = option | 0x0100
        cdbData = [opcode, physicalAddress.chip, physicalAddress.die, physicalAddress.plane, ByteUtil.LowByte(physicalAddress.block),
                 ByteUtil.HighByte(physicalAddress.block), physicalAddress.wordLine, physicalAddress.string, physicalAddress.mlcLevel, physicalAddress.eccPage, ByteUtil.LowByte(eccPageCount),
                             ByteUtil.HighByte(eccPageCount),0,0, ByteUtil.LowByte(option), ByteUtil.HighByte(option)]
        DiagnosticLib.SendDiagnostic(vtfContainer, readBuffer, cdbData , direction , ((eccPageCount*FwConfigObj.sectorsPerEccPage)+1)) #Why 5: The ECC pages/E-Blocks will be transferred as 5 sector (BCH)        
    else:
        #This is required when rdeccpg/wreccpg are done using Wordline addressing mode
        option = option | BE_SPECIFIC_READ_PHYSICAL_IN_WORDLINE_ADDRESSING_MODE      
        #checking for 32nmD2, for 43nmD2 - no need to add true binary option      
        if (physicalAddress.isTrueBinaryBlock):
            #changing option to true binary option value
            option = option | BE_SPECIFIC_READ_IN_TRUE_BINARY_MODE
            logger.Debug("", "[ReadEccPage] Checking the header contents..,the block is in true binary mode.")

        logger.Debug("", "[ReadEccPage]Reading from Chip:0x%x Die:0x%x, Plane:0x%x Block:0x%x Wordline:0x%x MLC Level:0x%x EccPage:0x%x with option 0x%x"\
                   %(physicalAddress.chip,physicalAddress.die,physicalAddress.plane,physicalAddress.block,physicalAddress.wordLine
                            ,physicalAddress.mlcLevel,physicalAddress.eccPage,option))

        option = option | 0x0100

        DiagnosticLib.ReadECCPage(vtfContainer, outputBuffer, physicalAddress, eccPageCount, eccPage,option)  
    return     
    #End of ReadEccPage

#def ReadEccPage(readBuffer,physicalAddress,eccPageCount,option):
    #"""
    #Wrapper for card.ReadEccPage taking care of truebinary access for 32nmD2/D3
    #"""
    #import ByteUtil
    #globalVarsObj = GlobalVars.GlobalVars()
    #FwConfigObj = globalVarsObj.GetFWConfigData()
    #sctpUtilsObj = globalVarsObj.sctpUtilsObj
    #logger = globalVarsObj.vtfContainer.logger


    #if FwConfigObj.isBiCS:
        #opcode = 0xB1
        #direction=0
        #if option != 0x300:
            #option = option | 0x0100
        #cdbData = [opcode, physicalAddress.chip, physicalAddress.die, physicalAddress.plane, ByteUtil.LowByte(physicalAddress.block),
                 #ByteUtil.HighByte(physicalAddress.block), physicalAddress.wordLine, physicalAddress.string, physicalAddress.mlcLevel, physicalAddress.eccPage, ByteUtil.LowByte(eccPageCount),
                             #ByteUtil.HighByte(eccPageCount),0,0, ByteUtil.LowByte(option), ByteUtil.HighByte(option)]
        #sctpUtilsObj.SendDiagnostic(readBuffer, cdbData , direction , ((eccPageCount*FwConfigObj.sectorsPerEccPage)+1)) #Why 5: The ECC pages/E-Blocks will be transferred as 5 sector (BCH)        
    #else:
        ##This is required when rdeccpg/wreccpg are done using Wordline addressing mode
        #option = option | BE_SPECIFIC_READ_PHYSICAL_IN_WORDLINE_ADDRESSING_MODE      
        ##checking for 32nmD2, for 43nmD2 - no need to add true binary option      
        #if (physicalAddress.isTrueBinaryBlock):
            ##changing option to true binary option value
            #option = option | BE_SPECIFIC_READ_IN_TRUE_BINARY_MODE
            #logger.Debug("", "[ReadEccPage] Checking the header contents..,the block is in true binary mode.")

        #logger.Debug("", "[ReadEccPage]Reading from Chip:0x%x Die:0x%x, Plane:0x%x Block:0x%x Wordline:0x%x MLC Level:0x%x EccPage:0x%x with option 0x%x"\
                   #%(physicalAddress.chip,physicalAddress.die,physicalAddress.plane,physicalAddress.block,physicalAddress.wordLine
                            #,physicalAddress.mlcLevel,physicalAddress.eccPage,option))

        #option = option | 0x0100

        #sctpUtilsObj.ReadECCPage(outputBuffer, physicalAddress, eccPageCount, eccPage,option)  
    #return     
    #End of ReadEccPage

def WriteEccPage(readBuffer,physicalAddress,eccPageCount,option):
    """
    Wrapper for card. taking care of truebinary access for 32nmD2/D3
    """
    import ByteUtil
    globalVarsObj = GlobalVars.GlobalVars()
    FwConfigObj = globalVarsObj.GetFWConfigData()
    sctpUtilsObj = globalVarsObj.sctpUtilsObj
    logger = globalVarsObj.vtfContainer.logger

    #This is required when rdeccpg/wreccpg are done using Wordline addressing mode
    option = option | BE_SPECIFIC_READ_PHYSICAL_IN_WORDLINE_ADDRESSING_MODE

    if (physicalAddress.isTrueBinaryBlock):
        #changing option to true binary option value
        option = option | BE_SPECIFIC_WRITE_IN_TRUE_BINARY_MODE
        logger.Debug("", "[WriteEccPage] The block is in true binary mode..")

    logger.Debug("", "[WriteEccPage]Writing to Chip:0x%x Die:0x%x, Plane:0x%x Block:0x%x WordLine:0x%x MLC Level:0x%x EccPage:0x%x with option 0x%x"\
                        %(physicalAddress.chip,physicalAddress.die,physicalAddress.plane,physicalAddress.block,
                          physicalAddress.wordLine,physicalAddress.mlcLevel,physicalAddress.eccPage,option))

    sctpUtilsObj.WriteEccPage(physicalAddress.chip, physicalAddress.die, physicalAddress.plane, physicalAddress.block, physicalAddress.wordLine, \
                              physicalAddress.mlcLevel, eccPage,option, eccPageCount, readBuffer)
    return
    #End of WriteEccPage

def IsBlockInTrueBinaryMode(self,physicalAddress):
    """
    Name:             IsBlockInTrueBinaryMode
    Description:      This function return true if the block is in True Binary mode else return false.
    This function first check that True Binary mode is enabled/Disable. If its enable then it
    check the block address belongs to any one of the control block
    Arguments:

    physicalAddress: physical addres tuple of the block
    Returns:
    trueBinaryMode    :  flag tell the block is in true binary mode
    """
    self.logger.Error("", "[IsBlockInTrueBinaryMode]No Need to use this function !!!")

    import math
    trueBinaryMode = False

    #if truebinary status is already known
    if physicalAddress.isTrueBinaryBlock != None:
        trueBinaryMode = physicalAddress.isTrueBinaryBlock
    #if truebinary status is not known,then scan physically and check header data..
    else:
        raise TestError.TestFailError(self.vtfContainer.GetTestName(), "[IsBlockInTrueBinaryMode] Don't use this part of the function")
    return trueBinaryMode


def GetReadWriteEccPageOption(trueBinary=None, eccCorrection=None, scrambled=None, eccInfoRet=None, option=0):
    """
    Description: Returns the Option value for Read/WriteEccPage command according to the input given.
    trueBinary: True if the block which is read/written is in True Binary Mode, else False.
    eccCorrection: True if ECC correction should be applied to the read data.
    scrambled: True if data is scrambled after reading. False if data should be unscrambled.
    eccInfoRet: True if ECC info should be appended in the data field.
    """
    if (trueBinary is not None):#If the inD1 option is not given, it is assumed to be inD1 instead of throwing syntax error.
        if (trueBinary == True or trueBinary == None):
            option = option | 0x200
        else:
            option = option & (~0x200)

    if (eccCorrection is not None):
        if (eccCorrection):
            option = option | 0x100
        else:
            option = option & (~0x100)

    if (scrambled is not None):
        if (scrambled):
            option = option | 0x020
        else:
            option = option & (~0x020)

    if (eccInfoRet is not None):
        if (eccInfoRet):
            option = option | 0x080
        else:
            option = option & (~0x080)

    return option
