
"""
################################################################################
# Copyright (c) SanDisk Corp.2013 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# FILE:RWCLib.py: Read/Write/Compare Library.
#         AUTHOR: Ravi G
################################################################################
"""

from builtins import object
import random

import CTFServiceWrapper as ServiceWrap
#import NVMeCMDWrapper as NVMeWrap
#import SATAWrapper as SATAWrap
import Core.ValidationError as ValidationError

#import Validation.NVMe_TestFixture as TestFixture
#import Validation.NVMe_TestParams as TP
#import Validation.NVMe_CMDUtil as CU

#**************************************************************************************************************
##
# @brief Runs all the variations in the testObject
# @details
# @return None
# @exception None
#**************************************************************************************************************
class RWCLib(object):
    def __init__(self):
        pass

        #self.TF = TestFixture.TestFixture()
        #self.CU = CU.CMDUtil()
        #self.configParser = self.TF.testSession.GetConfigInfo()
        #self.dataTrackEnabled = False
        #if int(self.configParser.GetValue('datatracking_enabled', 0)[0]):
            #self.dataTrackEnabled = True

    #def WriteLba(self, startLba, transferLength, submissionQID = 1, nameSpaceID = 1, FUA = 0, pattern = 0x55, writeTimeout = None):

        #isScsiWrite = False

        ##Create the required write buffer and fill a valid data pattern.
        #writeBuff = ServiceWrap.Buffer.CreateBuffer(transferLength, pattern)

        ##Perform Write Operation on the requested LBA range on the nameSpace.
        ##self.TF.logger.Debug("WLBA -> NSID : %d  SQID : %d LBA : 0x%08X  TxLen : 0x%08X  "%(nameSpaceID, submissionQID, startLba, transferLength))
        #writeCommand = NVMeWrap.WriteCommand(startLba, transferLength, submissionQID, nameSpaceID, FUA, None, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, m_patternID = pattern)
        #writeCommand.Execute()
        #writeCommand.HandleOverlappedExecute()
        #writeCommand.HandleAndParseResponse()

        #SCT = writeCommand.objNVMeComIOEntry.completionEntry.DW3.SF.SCT
        #SC = writeCommand.objNVMeComIOEntry.completionEntry.DW3.SF.SC

        #self.TF.logger.Debug("%-35s: (%s, %s)"%('WRITE CQ STATUS CODE', TP.SCT.keys()[TP.SCT.values().index(SCT)], TP.SC.keys()[TP.SC.values().index(SC)]))

        #return(SCT, SC)

    #def ReadLba(self, startLba, transferLength, submissionQID = 1, nameSpaceID = 1, expectedPattern = 0x0, readTimeout = None):

        #isScsiWrite = False

        ##Create the required write buffer and fill a valid data pattern.
        #readBuff = ServiceWrap.Buffer.CreateBuffer(transferLength)
        #refBuffer = ServiceWrap.Buffer.CreateBuffer(transferLength, expectedPattern)
        #readBuff.Fill(0x0)

        ##Perform Write Operation on the requested LBA range on the nameSpace.
        ##self.TF.logger.Debug("RDLBA -> NSID : %d  SQID : %d LBA : 0x%08X  TxLen : 0x%08X  "%(nameSpaceID, submissionQID, startLba, transferLength))
        #readcommand = NVMeWrap.ReadCommand(startLba, transferLength, submissionQID, nameSpaceID, 0, readBuff)
        #readcommand.Execute()
        #readcommand.HandleOverlappedExecute()
        #readcommand.HandleAndParseResponse()

        #SCT = readcommand.objNVMeComIOEntry.completionEntry.DW3.SF.SCT
        #SC = readcommand.objNVMeComIOEntry.completionEntry.DW3.SF.SC

        ##Compare Buffers

        #status = readBuff.Compare(refBuffer)
        #miscompareNrs = readBuff.FindMiscompare(refBuffer)
        #miscompareOffsets = readBuff.FindMiscompare(0, refBuffer, 0, readBuff.GetBufferSize())

        #self.TF.logger.Debug("%-35s: (%s, %s, %s)"%('Status and Miscomapre', status, miscompareNrs, miscompareOffsets))
        #self.TF.logger.Debug("%-35s: (%s, %s)"%('READ CQ SCT, SC', TP.SCT.keys()[TP.SCT.values().index(SCT)], TP.SC.keys()[TP.SC.values().index(SC)]))

        ##Validate comparision results only if Data Tracking is Disabled
        #if self.dataTrackEnabled == '0':
            #assert(0 == (status or len(miscompareNrs) or len(miscompareOffsets))), "BUFFER MISCOMPARE:\n\nMiscompare Occurred in Sector Numbers:\n %s\n\nMiscompare Occurred at Offsets:\n %s"%(miscompareNrs, miscompareOffsets)

        #return(SCT, SC)

    #def RandomReadLba(self, dictOfLBAs, startLba, transferLength, submissionQID = 1, nameSpaceID = 1, readTimeout = None):

        ##if there are at least 2000 commands posted, invoke wait for thread completion to avoid Insufficient Memeory Error.
        #if 0 == self.TF.nrOfCommands % 2000 and False == self.TF.sustainedMode and 0 != self.TF.nrOfCommands:
            #self.__CallWaitForThreadCompletion()

        #isScsiWrite = False

        ##Create the required write buffer and fill a valid data pattern.
        #readBuff = ServiceWrap.Buffer.CreateBuffer(transferLength)

        #readBuff.Fill(0x0)

        ##Perform Write Operation on the requested LBA range on the nameSpace.
        #self.TF.logger.Debug("RDLBA -> NSID : %d  SQID : %d LBA : 0x%08X  TxLen : 0x%08X  "%(nameSpaceID, submissionQID, startLba, transferLength))
        #readcommand = NVMeWrap.ReadCommand(startLba, transferLength, submissionQID, nameSpaceID, 0, readBuff)
        #readcommand.Execute()
        #readcommand.HandleOverlappedExecute()
        #readcommand.HandleAndParseResponse()

        #SCT = readcommand.objNVMeComIOEntry.completionEntry.DW3.SF.SCT
        #SC = readcommand.objNVMeComIOEntry.completionEntry.DW3.SF.SC

        ##Compare Buffers
        #refBuffer = None
        #for LBA in range(startLba, startLba + transferLength):
            #expectedPattern = dictOfLBAs[LBA]
            #tmpBuffer = ServiceWrap.Buffer.CreateBuffer(1, expectedPattern)
            #if refBuffer is None:
                #refBuffer = ServiceWrap.Buffer.CreateBuffer(1, expectedPattern)
            #else:
                #refBuffer.Append(tmpBuffer)

        #status = readBuff.Compare(refBuffer)
        #miscompareNrs = readBuff.FindMiscompare(refBuffer)
        #miscompareOffsets = readBuff.FindMiscompare(0, refBuffer, 0, readBuff.GetBufferSize())

        #self.TF.logger.Debug("%-35s: (%s, %s, %s)"%('Status and Miscomapre', status, miscompareNrs, miscompareOffsets))
        #self.TF.logger.Debug("%-35s: (%s, %s)"%('READ CQ SCT, SC', TP.SCT.keys()[TP.SCT.values().index(SCT)], TP.SC.keys()[TP.SC.values().index(SC)]))

        ##Validate comparision results only if Data Tracking is Disabled
        #if self.dataTrackEnabled == '0':
            #assert(0 == (status or len(miscompareNrs) or len(miscompareOffsets))), "BUFFER MISCOMPARE:\n\nMiscompare Occurred in Sector Numbers:\n %s\n\nMiscompare Occurred at Offsets:\n %s"%(miscompareNrs, miscompareOffsets)

        #return(SCT, SC)

    #def TaggedReadLba(self, dictOfLBAs, startLba, transferLength, submissionQID = 0, nameSpaceID = 1, readTimeout = None, uniqueID = 0x0):

        #isScsiWrite = False

        #lbaTagSize = self.configParser.GetValue('lba_val_tag_size', 0)
        #uniqueIDTagSize = self.configParser.GetValue('version_tag_size', 0)

        #totalTagSize = lbaTagSize[0] + uniqueIDTagSize[0]

        ##Create the required write buffer and fill a valid data pattern.
        #readBuff = ServiceWrap.Buffer.CreateBuffer(transferLength)

        #readBuff.Fill(0x0)

        ##Perform Write Operation on the requested LBA range on the nameSpace.
        #self.TF.logger.Debug("RDLBA -> NSID : %d  SQID : %d LBA : 0x%08X  TxLen : 0x%08X  "%(nameSpaceID, submissionQID, startLba, transferLength))
        #readcommand = NVMeWrap.ReadCommand(startLba, transferLength, submissionQID, nameSpaceID, 0, readBuff)
        #readcommand.Execute()
        #readcommand.HandleOverlappedExecute()
        #readcommand.HandleAndParseResponse()

        #SCT = readcommand.objNVMeComIOEntry.completionEntry.DW3.SF.SCT
        #SC = readcommand.objNVMeComIOEntry.completionEntry.DW3.SF.SC

        ##Compare Buffers
        #refBuffer = None
        #for LBA in range(startLba, startLba + transferLength):
            #expectedPattern = dictOfLBAs[LBA][0]
            #tmpBuffer = ServiceWrap.Buffer.CreateBuffer(1)
            #if (expectedPattern == ServiceWrap.EPattern.BYTE_REPEAT):
                #expectedPattern = dictOfLBAs[LBA][1]
                #tmpBuffer.Fill(expectedPattern)
            #elif (expectedPattern == ServiceWrap.EPattern.INCREMENTAL):
                #value = dictOfLBAs[LBA][1] - totalTagSize
                #if value < 0:
                    #value = range(0xFF + 1)[value]
                #tmpBuffer.FillIncrementing(value, 0xff, 1, 0xffff)
            #else:
                #tmpBuffer.Fill(expectedPattern)

            #tmpBuffer = self.TagBuffer(tmpBuffer, LBA, 1, uniqueID)
            #if refBuffer is None:
                #refBuffer = ServiceWrap.Buffer.CreateBuffer(1)
                #if (expectedPattern == ServiceWrap.EPattern.INCREMENTAL):
                    #value = dictOfLBAs[LBA][1] - totalTagSize
                    #if value < 0:
                        #value = range(0xFF + 1)[value]
                    #refBuffer.FillIncrementing(value, 0xff, 1, 0xffff)
                #else:
                    #refBuffer.Fill(expectedPattern)
                #refBuffer = self.TagBuffer(refBuffer, LBA, 1, uniqueID)
            #else:
                #refBuffer.Append(tmpBuffer)

        #status = 0
        #miscompareNrs = list()
        #miscompareOffsets = list()
        #if expectedPattern != ServiceWrap.EPattern.RANDOM:

            #status = readBuff.Compare(refBuffer)
            #miscompareNrs = readBuff.FindMiscompare(refBuffer)
            #miscompareOffsets = readBuff.FindMiscompare(0, refBuffer, 0, readBuff.GetBufferSize())

        #self.TF.logger.Debug("%-35s: (%s, %s, %s)"%('Status and Miscomapre', status, miscompareNrs, miscompareOffsets))
        #self.TF.logger.Debug("%-35s: (%s, %s)"%('READ CQ SCT, SC', TP.SCT.keys()[TP.SCT.values().index(SCT)], TP.SC.keys()[TP.SC.values().index(SC)]))

        ##Validate comparision results only if Data Tracking is Disabled
        #if self.dataTrackEnabled == False:
            #assert(0 == (status or len(miscompareNrs) or len(miscompareOffsets))), "BUFFER MISCOMPARE:\n\nMiscompare Occurred in Sector Numbers:\n %s\n\nMiscompare Occurred at Offsets:\n %s"%(miscompareNrs, miscompareOffsets)

        #return(SCT, SC)

    #def AutoWriteLba(self, startLba, transferLength, submissionQID = 0, taggedBuffer = None, nameSpaceID = 1, writeTimeout = None):

        ##if there are at least 2000 commands posted, invoke wait for thread completion to avoid Insufficient Memeory Error.
        #if 0 == self.TF.nrOfCommands % 2000 and False == self.TF.sustainedMode and 0 != self.TF.nrOfCommands:
            #self.__CallWaitForThreadCompletion()

        #isScsiWrite = False

        ##Create the required write buffer and fill a valid data pattern.
        #writeBuff = taggedBuffer

        ##Perform Write Operation on the requested LBA range on the nameSpace.
        #self.TF.logger.Debug("WLBA -> NSID : %d  SQID : %d LBA : 0x%08X  TxLen : 0x%08X  "%(nameSpaceID, submissionQID, startLba, transferLength))
        #writeCommand = NVMeWrap.WriteCommand(startLba, transferLength, submissionQID,  nameSpaceID,0,writeBuff)
        #writeCommand.Execute()
        #writeCommand.HandleOverlappedExecute()
        #writeCommand.HandleAndParseResponse()

        #SCT = writeCommand.objNVMeComIOEntry.completionEntry.DW3.SF.SCT
        #SC = writeCommand.objNVMeComIOEntry.completionEntry.DW3.SF.SC

        #self.TF.logger.Debug("%-35s: (%s, %s)"%('WRITE CQ STATUS CODE', TP.SCT.keys()[TP.SCT.values().index(SCT)], TP.SC.keys()[TP.SC.values().index(SC)]))

        #return(SCT, SC)

    #def AutoReadLba(self, startLba, transferLength, submissionQID = 0, nameSpaceID = 1, expectedBuffer = None, readTimeout = None):

        ##if there are at least 2000 commands posted, invoke wait for thread completion to avoid Insufficient Memeory Error.
        #if 0 == self.TF.nrOfCommands % 2000 and False == self.TF.sustainedMode and 0 != self.TF.nrOfCommands:
            #self.__CallWaitForThreadCompletion()

        #isScsiWrite = False

        ##Create the required write buffer and fill a valid data pattern.
        #readBuff = ServiceWrap.Buffer.CreateBuffer(transferLength)
        #readBuff.Fill(0x0)
        #refBuffer = expectedBuffer

        ##Perform Write Operation on the requested LBA range on the nameSpace.
        #self.TF.logger.Debug("RDLBA -> NSID : %d  SQID : %d LBA : 0x%08X  TxLen : 0x%08X  "%(nameSpaceID, submissionQID, startLba, transferLength))
        #readcommand = NVMeWrap.ReadCommand(startLba, transferLength, submissionQID, nameSpaceID, 0,  readBuff)
        #readcommand.Execute()
        #readcommand.HandleOverlappedExecute()
        #readcommand.HandleAndParseResponse()

        #SCT = readcommand.objNVMeComIOEntry.completionEntry.DW3.SF.SCT
        #SC = readcommand.objNVMeComIOEntry.completionEntry.DW3.SF.SC

        ##Compare Buffers

        #status = readBuff.Compare(refBuffer)
        #miscompareNrs = readBuff.FindMiscompare(refBuffer)
        #miscompareOffsets = readBuff.FindMiscompare(0, refBuffer, 0, readBuff.GetBufferSize())

        #self.TF.logger.Debug("%-35s: (%s, %s, %s)"%('Status and Miscomapre', status, miscompareNrs, miscompareOffsets))
        #self.TF.logger.Debug("%-35s: (%s, %s)"%('READ CQ SCT, SC', TP.SCT.keys()[TP.SCT.values().index(SCT)], TP.SC.keys()[TP.SC.values().index(SC)]))

        ##Validate comparision results only if Data Tracking is Disabled
        #if self.dataTrackEnabled == '0':
            #assert(0 == (status or len(miscompareNrs) or len(miscompareOffsets))), "BUFFER MISCOMPARE:\n\nMiscompare Occurred in Sector Numbers:\n %s\n\nMiscompare Occurred at Offsets:\n %s"%(miscompareNrs, miscompareOffsets)

        #return(SCT, SC)

    #def TagBuffer(self, refBuffer, startLBA, txLen, uniqueID):

        #self.configParser = self.TF.testSession.GetConfigInfo()
        #lbaTagSize = self.configParser.GetValue('lba_val_tag_size', 0)
        #uniqueIDTagSize = self.configParser.GetValue('version_tag_size', 0)

        #shiftOperation = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120]

        #bufferOffset = 0

        #for i in range(txLen):

            #for i in range(lbaTagSize[0]):
                #lba = (startLBA >> shiftOperation[i]) & 0xFF
                #refBuffer.SetByte(bufferOffset + i, lba)

            #offset = bufferOffset + lbaTagSize[0]
            #for i in range(uniqueIDTagSize[0]):
                #uID = (uniqueID >> shiftOperation[i]) & 0xFF
                #refBuffer.SetByte(offset, uID)
                #offset = offset + 1

            #bufferOffset = bufferOffset + 512
            #startLBA = startLBA + 1

        #return refBuffer

    #def ReadRandomLBAs(self, maxAllowableLba, nrOfLBAs = 100000, sendType = ServiceWrap.SEND_QUEUED):

        #self.TF.logger.Message("\t\t******** STARTED READING ALL THE LBAs in the Card ********")
        #transferLength = 127
        #for i in range(nrOfLBAs):

            #LBA = random.randint(0, self.TF.nsCap)
            #submissionQID = random.choice(self.TF.availableIOQs)

            #if LBA + transferLength >= maxAllowableLba:
                #LBA = 0

            #try:
                #self.CU.PostReadLba(LBA, transferLength, submissionQID = submissionQID, nameSpaceID = 1, sendType = sendType)
            #except ValidationError.CVFExceptionTypes as ex:
                #self.TF.logger.Fatal("Failed to Post the Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
                #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

            #self.TF.nrOfCommands += 1

        #self.TF.logger.Debug("******** COMPLETED READING RANDOM LBAs ******** ")

    #def ReadAroundLBAs(self, startLBA, txLen):

        #lbaRange = ['written', 'subset', 'nonwritten', 'nonwrittenR', 'nonwrittenL']
        #offset = random.randint(1, 1024)

        #choice = random.choice(lbaRange)
        #newStartLBA = startLBA

        #if choice == 'written':

            #transferLength = self.FitTransferLengthToRange(txLen, startLBA, self.TF.nsCap)

        #elif choice == 'subset':

            #newStartLBA = random.choice(range(startLBA, startLBA + txLen))
            #transferLength = txLen - newStartLBA
            #transferLength = self.FitTransferLengthToRange(transferLength, newStartLBA, self.TF.nsCap)

        #elif choice == 'nonwritten':

            #newStartLBA = abs(startLBA - offset)
            #transferLength = 2 * offset + txLen

            #if newStartLBA >= self.TF.nsCap:
                #newStartLBA = 0
            #transferLength = self.FitTransferLengthToRange(txLen, newStartLBA, self.TF.nsCap)

        #elif choice == 'nonwrittenR':

            #newStartLBA = random.choice(range(startLBA, startLBA + txLen))
            #transferLength = self.FitTransferLengthToRange(txLen + offset, newStartLBA, self.TF.nsCap)

            #return(newStartLBA, transferLength)

        #elif choice == 'nonwrittenL':

            #newStartLBA = abs(startLBA - offset)
            #transferLength = self.FitTransferLengthToRange(txLen, newStartLBA, self.TF.nsCap)

        #if transferLength == 0:
            #newStartLBA = 0
            #transferLength = 256

        #return(newStartLBA, transferLength)

    #def FitTransferLengthToRange(self, transferLength, startLba, maxAllowableLba ):
        #"""
        #Fit a transfer length to the LBA range it will be used in.  The transfer length
        #will be truncated so as to not exceed the maximum allowable LBA.

        #Arguments:
           #transferLength  - the transfer length
           #startLba        - the lba where the data transfer will begin
           #maxAllowableLba - the maximum allowable LBA for the data transfer.  This
                             #may be less than the max LBA of the card.

        #Returns:
           #the transfer length fit to the lba range
        #"""

        ## Truncate the transfer length if it will exceed the maximum allowable LBA
        #if startLba + transferLength - 1 >= maxAllowableLba:
            #transferLength = maxAllowableLba - startLba
        #if transferLength < 0:
            #transferLength = 0

        #return( transferLength )
        ##end of FitTransferLengthToRange

    #def GetLbaRange(self, maxLBA, txLenMin, txLenMax, startLBA = 0):

        #lbaRangeList = list()
        #if self.TF.isSNDKDrive:
            #maxNumberOfRanges = 127
        #else:
            #maxNumberOfRanges = int('11111111', 2)
        #numberOfRanges = random.randint(1, maxNumberOfRanges)

        #for i in range(numberOfRanges):
            #lba = random.randint(startLBA, maxLBA)
            #sectorCount = random.randint(txLenMin, txLenMax)

            #if lba + sectorCount <= maxLBA:
                #lbaRange = ServiceWrap.LbaRange(lba, sectorCount)
                #lbaRangeList.append(lbaRange)

            #else:
                #lba = 0
                #lbaRange = ServiceWrap.LbaRange(lba, sectorCount)
                #lbaRangeList.append(lbaRange)
            ##Updated StartLBA for Selecting new ranges

            #startLBA = startLBA + sectorCount
            #if startLBA  >= maxLBA:
                #startLBA = 0

        #self.TF.logger.Info(self.TF.TAG, "\n\nNumber of TRIM LBA Ranges constructed is -> %d."%len(lbaRangeList))

        ##for lbaRange in lbaRangeList:
                ##self.TF.logger.Info("LBA : 0x%08X  TxLen : 0x%08X"%(lbaRange.startLba, lbaRange.count))

        #return lbaRangeList

    #def AddCompare(self, startLba, transferLength, userData = None, fua = False, fused = 0, lr = 1, prinfo = 0, eilbrt = 0, elbatm = 0,\
                   #elbat = 0, namespaceID = 1, submissionQID = 1, compareTimeout = 20000000):

        ##if there are at least 2000 commands posted, invoke wait for thread completion to avoid Insufficient Memeory Error.
        #if 0 == self.TF.nrOfCommands % 2000 and False == self.TF.sustainedMode and 0 != self.TF.nrOfCommands:
            #self.__CallWaitForThreadCompletion()

        ##Perform Compare Operation on the requested LBA range on the nameSpace.
        #self.TF.logger.Debug("Adding to TPL: COMPARE -> NSID : %d  SQID : %d LBA : 0x%08X  TxLen : 0x%08X "%(namespaceID, submissionQID, startLba, transferLength))

        #if self.TF.sustainedMode:
            #compareCommand = NVMeWrap.CompareTask(startLBA = startLba, noOfBlocks = transferLength, userData = userData, FUA = fua, FUSED = fused, LR = lr, prInfo = prinfo, eILBRT = eilbrt, eLBATM = elbatm,\
                                                  #eLBAT = elbat, nameSpaceID = namespaceID, dwTimeOut = compareTimeout)
            #return compareCommand

        #if False == self.dataTrackEnabled:
            #if readBuffer is None:
                #readBuff = ServiceWrap.Buffer.CreateBuffer(transferLength)
                #readBuff.Fill(0x0)
            #else:
                #readBuff = readBuffer
            #compareCommand = NVMeWrap.Compare(startLBA = startLba, noOfBlocks = transferLength, userData = userData, FUA = fua, FUSED = fused, LR = lr, prInfo = prinfo, eILRBRT = eilbrt, eLBATM = elbatm,\
                                              #eLBAT = elbat, nameSpaceID = namespaceID, sQID = submissionQID, dwTimeOut = compareTimeout)
        #else:
            #compareCommand = NVMeWrap.Compare(startLBA = startLba, noOfBlocks = transferLength, userData = userData, FUA = fua, FUSED = fused, LR = lr, prInfo = prinfo, eILBRT = eilbrt, eLBATM = elbatm,\
                                              #eLBAT = elbat, nameSpaceID = namespaceID, sQID = submissionQID, dwTimeOut = compareTimeout)

        #return compareCommand

    #def __CallWaitForThreadCompletion(self):

        ##Don't call waitforthreadcompletion in Sustained Mode.
        #if self.TF.sustainedMode:
            #return
        #else:
            #self.TF.logger.Info("\nInvoking WaitForThreadPoolCompletion. Total Commands pushed so far is:%d\n"%self.TF.nrOfCommands)
            #status = False
            #status = self.TF.threadPool.WaitForThreadCompletion()
            #if False == status:

                #raise ValidationError.CVFGenericExceptions("ERROR", "Error occured in Waitforthreadcompletion\n")

    #def DoWrites(self, nameSpaceID = 1, count = 0, ErrorExpected = False, sendTypee = ServiceWrap.SEND_QUEUED):
        #startLba = 0
        #submissionQID = 0
        #FUA = 1
        #writeCommandCount = 0
        #TransferLenth = 1024
        #while writeCommandCount <= count:
            #patternIndex = random.choice(self.TF.patternDict.keys())
            #submissionQID = ((submissionQID % len((self.TF.availableIOQs))) + 1)
            #FUA = not FUA

            #try:
                #writeCommand = self.CU.PostWriteLba(startLba, TransferLenth, submissionQID, nameSpaceID, FUA, pattern = patternIndex, sendType = sendTypee)
            #except ValidationError.CVFExceptionTypes as ex:
                #self.TF.logger.Fatal("Failed to Post the Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
                #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

            #self.TF.nrOfCommands = self.TF.nrOfCommands + 1
            #writeCommandCount = writeCommandCount + 1
            #if 0 == self.TF.nrOfCommands % count:
                #break

            #startLba = startLba + TransferLenth

    #def DoWUCmd(self, nameSpaceID = 1, count = 0, ErrorExpected = False, sendTypee = ServiceWrap.SEND_QUEUED):
        #startLba = 0
        #submissionQID = 0
        #FUA = 1
        #WUCmdCount = 0
        #TransferLenth = 1024
        #while WUCmdCount <= count:

            #submissionQID = ((submissionQID % len((self.TF.availableIOQs))) + 1)

            #try:
                #WUCcmd = self.CU.PostWUC(nameSpaceID, submissionQID, startLba, TransferLenth)
            #except ValidationError.CVFExceptionTypes as ex:
                #self.TF.logger.Fatal("Failed to Post the Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
                #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

            #self.TF.nrOfCommands = self.TF.nrOfCommands + 1
            #WUCmdCount = WUCmdCount + 1
            #if 0 == self.TF.nrOfCommands % count:
                #break

            #startLba = startLba + TransferLenth

    #def DoRead(self, nameSpaceID = 1, count = 0, ErrorExpected = False, sendTypee = ServiceWrap.SEND_QUEUED):
        #startLba = 0
        #submissionQID = 0
        #FUA = 1
        #ReadCount = 0
        #TransferLenth = 1024
        #while ReadCount <= count:

            #patternIndex = random.choice(self.TF.patternDict.keys())
            #submissionQID = ((submissionQID % len((self.TF.availableIOQs))) + 1)
            #FUA = not FUA

            #try:
                #readCommand = self.CU.PostReadLba(startLba, TransferLenth, submissionQID, nameSpaceID, FUA, sendType = ServiceWrap.SEND_QUEUED)
            #except ValidationError.CVFExceptionTypes as ex:
                #self.TF.logger.Fatal("Failed to Post the Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
                #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

            #ReadCount = ReadCount + 1
            #self.TF.nrOfCommands = self.TF.nrOfCommands + 1
            #if 0 == self.TF.nrOfCommands % count:
                #break

            #startLba = startLba + TransferLenth

    #def DoWr0(self, nameSpaceID = 1, count = 0, lenMax = 0, ErrorExpected = False, sendTypee = ServiceWrap.SEND_QUEUED):
        #startLba = 0
        #submissionQID = 0
        #FUA = 1
        #Wr0Count = 0
        #TransferLenth = 1024
        #while Wr0Count <= count:

            #submissionQID = ((submissionQID % len((self.TF.availableIOQs))) + 1)

            #try:
                #self.CU.PostWrite0(startLba, LR = 0, FUA =0, PRINFO = 0, NLB = lenMax, ILBRT = 0, LBATM = 0, LBAT = 0, NameSpaceID = nameSpaceID, SQID = submissionQID)
            #except ValidationError.CVFExceptionTypes as ex:
                #self.TF.logger.Fatal("Failed to Post the Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
                #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

            #self.TF.nrOfCommands = self.TF.nrOfCommands + 1
            #Wr0Count = Wr0Count + 1
            #if 0 == self.TF.nrOfCommands % count:
                #break

            #startLba = startLba + TransferLenth

    #def DoTrim(self, nameSpaceID = 1, count = 0, lenMax = 0, ErrorExpected = False, sendTypee = ServiceWrap.SEND_QUEUED):
        #startLba = 0
        #submissionQID = 0
        #TrimCount = 0

        #while TrimCount <= count:

            #try:
                #lbaRangeList = self.GetLbaRange(lenMax, 1, 127)
                #Trimcmd = self.CU.PostTrim(lbaRangeList, 1, nameSpaceID)
            #except ValidationError.CVFExceptionTypes as ex:
                #self.TF.logger.Fatal("Failed to Post the Command to Threadpool. Exception Message is ->\n %s "%ex.GetFailureDescription())
                #raise ValidationError.CVFGenericExceptions("", "Failed in Posting Command\n")

            #TrimCount = TrimCount + 1
            #self.TF.nrOfCommands = self.TF.nrOfCommands + 1
            #if 0 == self.TF.nrOfCommands % count:
                #break