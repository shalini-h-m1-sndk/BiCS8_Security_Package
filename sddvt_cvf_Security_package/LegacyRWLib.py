"""
class LegacyRWLib
CVF library similar to CTF's ValidationRWCLib, includes APIs to perform Writes/Reads/Erases
@ Author: Shaheed Nehal A
@ copyright (C) 2020 Western Digital Corporation
@ Date: 25-Feb-2020
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from builtins import str
from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    pass # from builtins import str
    from builtins import hex
    pass # from builtins import *
    from builtins import object
import Extensions.CVFImports as pyWrap
import SDCommandWrapper as SDwrap
import Utils
import random
import Core.ValidationError as ValidationError
import PatternGen
import SDDVT.Common.SDCommandLib as SDCommandLib
from os import path
import datetime,time
import json
import Core.Configuration as Configuration

SECTORS_PER_FRAGMENT = 8
PATTERNGEN_PATTERN = None

class LegacyRWLib(object):
    
    totalSectorsWritten=0

    def __init__(self, vtfContainer, maxLba, lbaRanges, maxTransferLength, writePattern, usePatternGen=False, patternToBeUsed=None):
        self.vtfContainer = vtfContainer
        self.logger = self.vtfContainer.GetLogger()
        self.randomObj = random.Random(self.vtfContainer.cmd_line_args.randomSeed)
        self.__isProtocolModel = self.vtfContainer.isModel
        self.__sdCmdsClass = SDCommandLib.SdCommandClass(self.vtfContainer)
        self.sysConfig = Configuration.ConfigurationManager().GetSystemConfiguration()
        self.totalIOCommandCount = 0
        self.yodaUploadCheckpointHits = 0
        #check for lbaRanges
        assert type(lbaRanges) in ( list, tuple ) and len(lbaRanges) > 0, \
               "<lbaRanges> must be a list or tuple with length > 0 (got %s, '%s')" % \
               ( type(lbaRanges).__name__, lbaRanges )

        #check for maxLba
        if maxLba is not None:
            assert ( ((type(maxLba) is int ) or (type(maxLba) is int )) and (maxLba >=0 ) ),"maxLba given is not Valid (got %s, '%s')"% \
                   ( type(maxLba).__name__, maxLba )

        #check for maxTransferLength
        assert ((type(maxTransferLength) is int) or (type(maxTransferLength) is int )) and maxTransferLength > 0,\
               "maxTransferLength is invalid (got %s, '%s')"%\
               ( type(maxTransferLength).__name__,maxTransferLength)

        #Variables
        self.__maxTransferLength  = maxTransferLength
        self.__maxLba = maxLba

        #Update RO mode flag
        readOnlyMode = False                ##HARDCODING FOR NOW
        if readOnlyMode:
            self.__isReadOnlyMode = True
        else :
            self.__isReadOnlyMode  = False

        #Process Lba xrange
        self.__lbaRanges = Utils.ProcessLbaRangeInputs(lbaRanges,self.__maxLba)

        #getting extremes of LBA ranges
        self.__minTestLba = min( [ x[0] for x in self.__lbaRanges ] )
        self.__maxTestLba = max( [ x[1] for x in self.__lbaRanges ] )

        #To recheck - Add user pattern/default pattern - check with CVF
        self.__userPattern = writePattern

        self.__usePatternGen = usePatternGen
        self.__patternToBeUsed = patternToBeUsed

        global PATTERNGEN_PATTERN
        if self.__usePatternGen and PATTERNGEN_PATTERN == None:
            if self.vtfContainer.isModel:
                raise ValidationError.TestFailError(self.vtfContainer.GetTestName(), "PGEN is applicable only on HW tests")

            PATTERNGEN_PATTERN = self.__patternToBeUsed
            if self.vtfContainer.cmd_line_args.doComparePatternGen:
                self.__patternGenObj = PatternGen.PatternGen(self.vtfContainer,
                                                             writePattern=self.__patternToBeUsed,
                                                             doCompare=True,
                                                             SeqTag=True,
                                                             lbaTag=True)
            else:
                self.__patternGenObj = PatternGen.PatternGen(self.vtfContainer,
                                                             writePattern=self.__patternToBeUsed,
                                                             doCompare=False,
                                                             SeqTag=False,
                                                             lbaTag=False)
        else:
            self.__patternGenObj = None

        return


    def Write(self, startLba, transferLength, writeBuffer=None, fullDataMode=False, STLength = None, debugAsserts=True, preconditioningWrite=False):
        if self.vtfContainer.cmd_line_args.openEndedCmd :
            bStopTransmissionFlag = True
        else:
            bStopTransmissionFlag = False

        if STLength != None:
            exInfo            = SDwrap.EXTRA_COMMAND_PARAMETERS()
            exInfo.enInfoType = SDwrap.EXTRA_INFO_TYPE.STOP_TRANSMISSION_INFO
            exInfo.uiStopTransMissionAfterTransferLength = STLength
            exInfo.bEnableDataTransferWithotModelReadyAfterSTLength = False

        if debugAsserts:
            if __debug__:
                #check address and transferLength are valid
                assert (startLba >= self.__minTestLba ) ,"Logical Address (0x%X) given is lesser than the lba ranges given (0x%X) "%(startLba,self.__minTestLba)
                #assert (transferLength <= self.__maxTransferLength ),"TransferLength(%s) is out of range('%s') "%(transferLength,self.__maxTransferLength)
                assert (transferLength > 0 ),"TransferLength must be > 0 , (got '%s' )"%transferLength
                assert (startLba + transferLength -1 <= self.__maxTestLba)," trying to access  beyond the maximum lba of Lba ranges(0x%X) given"%self.__maxTestLba
                #assert (not  self.__isReadOnlyMode),"Can not perform write as ValidationRwc object is in Read only mode"


        fullDataMode = False
        writeWithNoData = True

        numOfLbaPrePadded   = startLba % SECTORS_PER_FRAGMENT
        endLba              = startLba + transferLength - 1
        numOfLbaPostPadded  = (SECTORS_PER_FRAGMENT - endLba % SECTORS_PER_FRAGMENT) - 1

        if self.vtfContainer.cmd_line_args.switchDataPatternAfterEveryWrite:
            self.__userPattern = self.randomObj.randint(0,1)
            #Enable the below code after checking if 0-9 patterns work on HW, on model only pattern0,1 works
            #if self.vtfContainer.isModel:
                #self.__userPattern = self.randomObj.randint(0,1) #>< Review: Not working with diff patterns (0-9)
            #else:
                ##Need to check on HW - pending
                #self.__userPattern = self.randomObj.randint(0,9)


        #Issue CMD24 for singlesector writes
        if transferLength == 1:
            try:
                if self.__usePatternGen:
                    if preconditioningWrite:
                        self.logger.Info("", "[Preconditioning][PatternGen]%6s Lba:0x%08X  Transfer Length:0x%04x [numOfLbaPrePadded:%d/numOfLbaPostPadded:%d] "\
                                         %("SingleWrite",startLba,transferLength, numOfLbaPrePadded,numOfLbaPostPadded))
                    else:
                        self.logger.Info("", "[PatternGen]%6s Lba:0x%08X  Transfer Length:0x%04x [numOfLbaPrePadded:%d/numOfLbaPostPadded:%d] "\
                                         %("SingleWrite",startLba,transferLength, numOfLbaPrePadded,numOfLbaPostPadded))
                    PGENParams = self.__patternGenObj.SingleWrite(startLba, transferLength)
                else:
                    if bStopTransmissionFlag == True:
                        if preconditioningWrite:
                            self.logger.Info("", "[Preconditioning][OpenEnded]%6s Lba:0x%08X  Transfer Length:0x%04x [numOfLbaPrePadded:%d/numOfLbaPostPadded:%d] "\
                                             %("Write",startLba,transferLength, numOfLbaPrePadded,numOfLbaPostPadded))
                        else:
                            self.logger.Info("", "[OpenEnded]%6s Lba:0x%08X  Transfer Length:0x%04x [numOfLbaPrePadded:%d/numOfLbaPostPadded:%d] "\
                                             %("Write",startLba,transferLength, numOfLbaPrePadded,numOfLbaPostPadded))
                    else:
                        if preconditioningWrite:
                            self.logger.Info("", "[Preconditioning][CloseEnded]%6s Lba:0x%08X  Transfer Length:0x%04x [numOfLbaPrePadded:%d/numOfLbaPostPadded:%d] "\
                                             %("Write",startLba,transferLength, numOfLbaPrePadded,numOfLbaPostPadded))
                        else:
                            self.logger.Info("", "[CloseEnded]%6s Lba:0x%08X  Transfer Length:0x%04x [numOfLbaPrePadded:%d/numOfLbaPostPadded:%d] "\
                                             %("Write",startLba,transferLength, numOfLbaPrePadded,numOfLbaPostPadded))
                    #self.logger.Info("", "Write Lba: {0} Transfer Length: {1} Pattern: {2}".format(hex(startLba), hex(transferLength), Pattern))
                    CMD24_WriteSingleBlock = SDwrap.WriteSingleBlock(startLba=startLba,
                                                                     bNoData=writeWithNoData,
                                                                     szBuffer=writeBuffer,
                                                                     uiPattern=self.__userPattern, #To recheck - check with CVF
                                                                     blockLength=512)

                    self.totalSectorsWritten += transferLength
                    self.vtfContainer.cmd_line_args.totalDataWritten = (self.totalSectorsWritten * 512) / (1024 * 1024 * 1024)
                    #self.writeCommandCount += 1
                    self.totalIOCommandCount += 1

            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.logger.Info("",  "Write Failed - CMD24 : Write Lba:{0} Transfer Length:{1}".format(hex(startLba), hex(transferLength)))
                raise ValidationError.CVFGenericExceptions(self.vtfContainer.GetTestName(), "Write Failed - CMD24 : "+exc.GetFailureDescription() )

            except Exception as exc:
                raise ValidationError.TestFailError(self.vtfContainer.GetTestName(), str(exc))

        #Issue CMD25 for multisector writes
        else:
            try:
                if self.__usePatternGen:
                    if preconditioningWrite:
                        self.logger.Info("", "[Preconditioning][PatternGen]%6s Lba:0x%08X  Transfer Length:0x%04x [numOfLbaPrePadded:%d/numOfLbaPostPadded:%d] "\
                                         %("MultipleWrite",startLba,transferLength, numOfLbaPrePadded,numOfLbaPostPadded))
                    else:
                        self.logger.Info("", "[PatternGen]%6s Lba:0x%08X  Transfer Length:0x%04x [numOfLbaPrePadded:%d/numOfLbaPostPadded:%d] "\
                                         %("MultipleWrite",startLba,transferLength, numOfLbaPrePadded,numOfLbaPostPadded))
                    PGENParams = self.__patternGenObj.MultipleWrite(startLba, transferLength)
                else:
                    if bStopTransmissionFlag == True:
                        if preconditioningWrite:
                            self.logger.Info("", "[Preconditioning][OpenEnded]%6s Lba:0x%08X  Transfer Length:0x%04x [numOfLbaPrePadded:%d/numOfLbaPostPadded:%d] "\
                                             %("Write",startLba,transferLength, numOfLbaPrePadded,numOfLbaPostPadded))
                        else:
                            self.logger.Info("", "[OpenEnded]%6s Lba:0x%08X  Transfer Length:0x%04x [numOfLbaPrePadded:%d/numOfLbaPostPadded:%d] "\
                                             %("Write",startLba,transferLength, numOfLbaPrePadded,numOfLbaPostPadded))
                    else:
                        if preconditioningWrite:
                            self.logger.Info("", "[Preconditioning][CloseEnded]%6s Lba:0x%08X  Transfer Length:0x%04x [numOfLbaPrePadded:%d/numOfLbaPostPadded:%d] "\
                                             %("Write",startLba,transferLength, numOfLbaPrePadded,numOfLbaPostPadded))
                        else:
                            self.logger.Info("", "[CloseEnded]%6s Lba:0x%08X  Transfer Length:0x%04x [numOfLbaPrePadded:%d/numOfLbaPostPadded:%d] "\
                                             %("Write",startLba,transferLength, numOfLbaPrePadded,numOfLbaPostPadded))

                    #self.logger.Info("", "Write Lba: {0} Transfer Length: {1} Pattern: {2}".format(hex(startLba), hex(transferLength), Pattern))

                    #Call API only for Clos ended HW cases
                    if not bStopTransmissionFlag and (not self.vtfContainer.isModel) :
                        PreDefinedBlkCount = not bStopTransmissionFlag
                        CMD25_WriteMultipleBlocks = SDwrap.MultWriteBlockCloseEnded(startLba=startLba,
                                                                                    blockCount=transferLength,
                                                                                    szBuffer=writeBuffer,
                                                                                    uiPattern=self.__userPattern,
                                                                                    usePreDefBlkCount = PreDefinedBlkCount)
                    else:

                        if (STLength == None):
                            # write fucntion without ST in SD mode
                            CMD25_WriteMultipleBlocks = SDwrap.WriteMultipleBlocks(startLba=startLba,
                                                                                   blockCount=transferLength,
                                                                                   bNoData=writeWithNoData,
                                                                                   szBuffer=writeBuffer,
                                                                                   bStopTransmission=bStopTransmissionFlag,
                                                                                   uiPattern=self.__userPattern,
                                                                                   blockLength=512)
                        else:
                            self.logger.Info("","ST will be issued after TransferLength of 0x%04x"%STLength)
                            CMD25_WriteMultipleBlocks = SDwrap.WriteMultipleBlocks(startLba=startLba,
                                                                                   blockCount=transferLength,
                                                                               bNoData=writeWithNoData,
                                                                               szBuffer=writeBuffer,
                                                                               bStopTransmission=bStopTransmissionFlag,
                                                                               uiPattern=self.__userPattern,
                                                                               extraInfo=exInfo,
                                                                               blockLength=512)


                self.totalSectorsWritten += transferLength
                self.vtfContainer.cmd_line_args.totalDataWritten = (self.totalSectorsWritten * 512.00 ) / (1024.00 * 1024.00 * 1024.00)
        #self.writeCommandCount += 1
                self.totalIOCommandCount += 1
                self.checkpointForYodaUpload()

            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.__sdCmdsClass.Cmd13()
                #NOTE: CVF will check for time remaining before sending any cmd, so in case --timeToRun has elapsed, then that particular cmd wont be sent to FW
                #If --timeToRun elapses in between the cmd, then that cmd will anyway complete and CVF will throw the BoostTimerEvent exc only after the current
                #cmd completes
                import ValidationSpace
                valspace = ValidationSpace.ValidationSpace(self.vtfContainer)
                if valspace.errorManager.GetAllFailureDescription() != '':
                    self.logger.Info("",  "Write Failed - CMD25 : Write Lba:{0} Transfer Length:{1} \n {2}".format(hex(startLba), hex(transferLength), str(exc)))
                    #NOTE: CVFGenericException will clear on the GenericExceptions like BoostTimerEvent etc. Any other genuine write failures will be caught
                    raise ValidationError.CVFGenericExceptions(self.vtfContainer.GetTestName(), "Write Failed - CMD25 : "+exc.GetFailureDescription() )

            except Exception as exc:
                self.logger.Info("",  "Write Failed - CMD25 : Write Lba:{0} Transfer Length:{1} \n {2}".format(hex(startLba), hex(transferLength), str(exc)))
                raise ValidationError.TestFailError(self.vtfContainer.GetTestName(), str(exc))
        return


    def Read(self, startLba, transferLength, fullDataMode=False, readBuffer=None, STLength = None, debugAsserts=True):
        #Always set fullDataMode to False (for model)
        if self.vtfContainer.isModel:
            fullDataMode = False

        if self.vtfContainer.cmd_line_args.openEndedCmd:
            bStopTransmissionFlag = True
        else:
            bStopTransmissionFlag = False

        if debugAsserts:
            if __debug__:
                #check address and transferLength are valid
                assert (startLba >= self.__minTestLba ) ,"Logical Address (0x%X) given is lesser than the lba ranges given (0x%X) "%(startLba,self.__minTestLba)
                #assert (transferLength <= self.__maxTransferLength ),"TransferLength(%s) is out of range('%s') "%(transferLength,self.__maxTransferLength)
                assert (transferLength > 0 ),"TransferLength must be > 0 , (got '%s' )"%transferLength
                assert (startLba + transferLength -1 <= self.__maxTestLba)," trying to access  beyond the maximum lba of Lba ranges(0x%X) given"%self.__maxTestLba

        if not self.__usePatternGen:
            if fullDataMode or self.vtfContainer.cmd_line_args.fullDataMode:
                #Read with data (buffer allocation)
                if readBuffer == None:
                    readBuffer = pyWrap.Buffer.CreateBuffer(transferLength, 0x0, isSector=True)
                readWithNoData = False
            else:
                #Read with no data
                readBuffer = None
                readWithNoData = True

        #Initialise ST Parameters
        if STLength != None:
            exInfo            = SDwrap.EXTRA_COMMAND_PARAMETERS()
            exInfo.enInfoType = SDwrap.EXTRA_INFO_TYPE.STOP_TRANSMISSION_INFO
            exInfo.uiStopTransMissionAfterTransferLength = STLength
            exInfo.bEnableDataTransferWithotModelReadyAfterSTLength = False

        #Issue CMD17 for singlesector reads
        if transferLength == 1:
            try:
                if self.__usePatternGen:
                    self.logger.Info("", "[PatternGen]%6s Lba:0x%08X  Transfer Length:0x%04x   "%("SingleRead",startLba,transferLength))
                    PGENParams = self.__patternGenObj.SingleRead(startLba, transferLength)
                else:
                    if bStopTransmissionFlag:
                        self.logger.Info("", "[OpenEnded]%6s Lba:0x%08X  Transfer Length:0x%04x   "%("Read",startLba,transferLength))
                    else:
                        self.logger.Info("", "[CloseEnded]%6s Lba:0x%08X  Transfer Length:0x%04x   "%("Read",startLba,transferLength))

                    #self.logger.Info("", "Read Lba:{0}  Transfer Length:{1}".format(hex(startLba), hex(transferLength)))
                    CMD17_ReadSingleBlock = SDwrap.ReadSingleBlock(startLba,
                                                                   bNoData=readWithNoData,
                                                                   szBuffer=readBuffer,
                                                                   blockLength=512)
                    #self.Delay(0, 100)

                #self.totalSectorsRead += transferLength
                #self.readCommandCount += 1
                self.totalIOCommandCount += 1

            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.logger.Info("",  "Single Sector Read (CMD17) Failed - Read Lba:{0} Transfer Length:{1}".format(hex(startLba), hex(transferLength)))
                raise ValidationError.CVFGenericExceptions(self.vtfContainer.GetTestName(), "Single Sector Read (CMD17) Failed : "+exc.GetFailureDescription() )

            except Exception as exc:
                raise ValidationError.TestFailError(self.vtfContainer.GetTestName(), str(exc))




        #Issue CMD18 for MultiSector Reads
        else:
            try:
                if self.__usePatternGen:
                    self.logger.Info("", "[PatternGen]%6s Lba:0x%08X  Transfer Length:0x%04x   "%("MultipleRead",startLba,transferLength))
                    PGENParams = self.__patternGenObj.MultipleRead(startLba, transferLength)
                else:
                    if bStopTransmissionFlag:
                        self.logger.Info("", "[OpenEnded]%6s Lba:0x%08X  Transfer Length:0x%04x   "%("Read",startLba,transferLength))
                    else:
                        self.logger.Info("", "[CloseEnded]%6s Lba:0x%08X  Transfer Length:0x%04x   "%("Read",startLba,transferLength))

                    #Call API only for Clos ended HW cases
                    if not bStopTransmissionFlag and (not self.vtfContainer.isModel) :
                        PreDefinedBlkCount = not bStopTransmissionFlag
                        CMD18_ReadMultipleBlocks = SDwrap.MultReadBlockCloseEnded(startLba=startLba,
                                                                                  blockCount=transferLength,
                                                                           szBuffer=readBuffer,
                                                                           usePreDefBlkCount = PreDefinedBlkCount)
                    else:

                        #self.logger.Info("", "Read Lba:{0}  Transfer Length:{1}".format(hex(startLba), hex(transferLength)))
                        if STLength == None:
                            CMD18_ReadMultipleBlocks = SDwrap.ReadMultipleBlocks(startLba=startLba,
                                                                                 blockCount=transferLength,
                                                                                 bNoData=readWithNoData,
                                                                                 szBuffer=readBuffer,
                                                                                 bStopTransmission=bStopTransmissionFlag)
                        else:
                            self.logger.Info("","ST will be issued after TransferLength of 0x%04x"%STLength)
                            CMD18_ReadMultipleBlocks = SDwrap.ReadMultipleBlocks(startLba=startLba,
                                                                                 blockCount=transferLength,
                                                                                 bNoData=readWithNoData,
                                                                                 szBuffer=readBuffer,
                                                                                 extraInfo=exInfo,
                                                                                 bStopTransmission=bStopTransmissionFlag)

                #self.totalSectorsRead += transferLength
                #self.readCommandCount += 1
                self.totalIOCommandCount += 1

            except ValidationError.CVFExceptionTypes as exc:
                exc = exc.CTFExcObj if hasattr(exc, "CTFExcObj") else exc
                self.logger.Info("",  "Multi Sector Read (CMD18) Failed - Read Lba:{0} Transfer Length:{1} \n {2}".format(hex(startLba), hex(transferLength), str(exc)))
                raise ValidationError.CVFGenericExceptions(self.vtfContainer.GetTestName(), "Multi Sector Read (CMD18) Failed : "+exc.GetFailureDescription() )

            except Exception as exc:
                self.logger.Info("",  "Multi Sector Read (CMD18) Failed - Read Lba:{0} Transfer Length:{1} \n {2}".format(hex(startLba), hex(transferLength), str(exc)))
                raise ValidationError.TestFailError(self.vtfContainer.GetTestName(), str(exc))


        return


    def Erase(self,startLba, transferLength, debugAsserts=True):
        if debugAsserts:
            if __debug__:
                #check address and transferLength are valid
                assert (startLba >= self.__minTestLba ) ,"Logical Address (0x%X) given is lesser than the lba ranges given (0x%X) "%(startLba,self.__minTestLba)
                assert ((startLba + transferLength-1) <= self.__maxTestLba), "Trying to access  beyond the maximum lba of Lba ranges(0x%X) given"%self.__maxTestLba
                assert (transferLength > 0 ),"TransferLength must be > 0 , (got '%s' )"%transferLength

        self.logger.Info("", "%6s Lba:0x%08X  Transfer Length:0x%04x   "%("Erase",startLba,transferLength))
        startBLK = startLba
        #To recheck : RPG-49686 (EndBlk is inclusive on HW and exclusive for model only for erase)
        #for Erase EndLBA will be blockcount as per sdr host
        if self.vtfContainer.isModel:
            endBlk = startLba + transferLength - 1
        else:
            endBlk = startLba + transferLength

        #if self.__isProtocolModel:
        #According to new CVF, Both Model and HW handling will be same 
        try:
            SDwrap.EraseDiscardFule(startBLK, endBlk) #This will by default call erase()
        except ValidationError.CVFExceptionTypes as ex:
            ex = ex.CTFExcObj if hasattr(ex, "CTFExcObj") else ex
            self.logger.Info("", "EraseDiscardFule() failed : %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions(self.vtfContainer.GetTestName(), "EraseDiscardFule() failed")
        except Exception as exc:
            raise ValidationError.TestFailError(self.vtfContainer.GetTestName(), str(exc))

        #API similar to model provided for Erase sequence
        #else:
            #try:
                #Cmd38_Erase = SDwrap.Erase(startBLK,endBlk,uiEraseFunction = 0) #To recheck
            #except ValidationError.CVFExceptionTypes as ex:
                #ex = ex.CTFExcObj if hasattr(ex, "CTFExcObj") else ex
                #self.logger.Info("", "CMD38 (Erase) failed : %s "%ex.GetFailureDescription())
                #raise ValidationError.CVFGenericExceptions(self.vtfContainer.GetTestName(), "CMD38 (Erase) failed")
            #except Exception as exc:
                #raise ValidationError.TestFailError(self.vtfContainer.GetTestName(), str(exc))

        #self.eraseCommandCount += 1
        self.totalIOCommandCount += 1

        return

    def checkpointForYodaUpload(self):
        if self.yodaUploadCheckpointHits < self.totalIOCommandCount // 1000:
            import YodaUtils
            self.yodaUtils = YodaUtils.YodaUtils(self.vtfContainer, self.sysConfig)
            execution_info = self.vtfContainer.execution_info
            jsonPath = self.sysConfig.Logger.logFolder + "\\" + "YodaPostTestData_L" + str(execution_info.GeValueFromTestDataCollection("labID")) + "_E" + str(execution_info.GeValueFromTestDataCollection("testQueueId")) + "_" + execution_info.GeValueFromTestDataCollection("logFileName").rstrip(".log") + ".json"
            if path.exists(jsonPath):
                with open(jsonPath, "r") as jsonFile:
                    data = json.load(jsonFile)

                data["payload"]["driver_data"]["data_written"] = float("{:.5f}".format(self.vtfContainer.cmd_line_args.totalDataWritten))
                dtnow = datetime.datetime.utcnow()
                updated_date = dtnow.strftime("%Y-%m-%d %H:%M:%S")
                data["acquired_date"]=updated_date

                with open(jsonPath, "w") as jsonFile:
                    json.dump(data, jsonFile)
            self.yodaUtils.dumpToYoda(jsonPath, 'json', False)
            self.yodaUploadCheckpointHits += 1

    def VerifyAllWrittenData(self, lbaRange = None):

        assert (lbaRange != None ) ,"Verifyallwrittendata - Lba range not specified"

        minLbaToTest = lbaRange[0]
        maxLbaToTest = lbaRange[1]

        transferLength = maxLbaToTest - minLbaToTest
        if transferLength not in [-1, 0]:
            self.Read(minLbaToTest, transferLength)

        return


    def GetAndPrintWriteStatistics(self, printStatistics = True):
        #To recheck - not ported yet
        """
        global g_measureWriteAmplification
        global g_hostWriteCount
        global g_hostSectorCount
        global g_systemWriteCount
        global g_systemWriteCount_SLC
        global g_systemWriteCount_MLC
        global g_systemWriteCount_CONTROL
        global g_systemSectorCount
        global g_systemSectorCount_SLC
        global g_systemSectorCount_MLC
        global g_systemSectorCount_CONTROL
        global g_systemSectorCount_SLCDUMMY
        global g_systemSectorCount_MLCDUMMY
        global g_Logger

        if (g_measureWriteAmplification == True and g_hostSectorCount > 0 ):
            writeAmplificationCount         = 0
            writeAmplificationCount_SLC     = 0
            writeAmplificationCount_MLC     = 0
            writeAmplificationCount_CONTROL = 0
            writeAmplificationCount_SLCDUMMY = 0
            writeAmplificationCount_MLCDUMMY = 0

            if g_hostSectorCount != 0:
                writeAmplificationCount         = float(g_systemSectorCount)/float(g_hostSectorCount)
                writeAmplificationCount_SLC     = float(g_systemSectorCount_SLC)/float(g_hostSectorCount)
                writeAmplificationCount_MLC     = float(g_systemSectorCount_MLC)/float(g_hostSectorCount)
                writeAmplificationCount_SLCDUMMY= float(g_systemSectorCount_SLCDUMMY)/float(g_hostSectorCount)
                writeAmplificationCount_MLCDUMMY= float(g_systemSectorCount_MLCDUMMY)/float(g_hostSectorCount)

            if printStatistics == True:
                g_Logger.Info("*"*160)
                g_Logger.Info("[ValidationRwcLib] WriteAmp:            %.2f  hostWriteCount:         %d  hostSectorCount: %d  systemWriteCount: %d  systemSectorCount: %d " \
                              %(writeAmplificationCount,g_hostWriteCount,g_hostSectorCount, g_systemWriteCount, g_systemSectorCount))
                g_Logger.Info("[ValidationRwcLib] SLC WriteAmp:        %.2f  SLCsystemWriteCount:    %d  SLCsystemSectorCount: %d " \
                              %(writeAmplificationCount_SLC,g_systemWriteCount_SLC, g_systemSectorCount_SLC))
                g_Logger.Info("[ValidationRwcLib] MLC WriteAmp:        %.2f  MLCsystemWriteCount:    %d  MLCsystemSectorCount: %d " \
                              %(writeAmplificationCount_MLC,g_systemWriteCount_MLC, g_systemSectorCount_MLC))
                g_Logger.Info("[ValidationRwcLib] SLC DUMMY WriteAmp:  %.2f  Dummy systemWriteCount: %d  DmmysystemSectorCount: %d " \
                              %(writeAmplificationCount_SLCDUMMY,g_systemWriteCount_SLCDUMMY, g_systemSectorCount_SLCDUMMY))
                g_Logger.Info("[ValidationRwcLib] MLC DUMMY WriteAmp:  %.2f  Dummy systemWriteCount: %d  DmmysystemSectorCount: %d " \
                              %(writeAmplificationCount_MLCDUMMY,g_systemWriteCount_MLCDUMMY, g_systemSectorCount_MLCDUMMY))
                for controlType in g_systemSectorCount_CONTROL.keys():
                    g_Logger.Info("[ValidationRwcLib] CONTROL %d WriteAmp:    %.2f  CONTROLsystemWriteCount:%d  CONTROLsystemSectorCount: %d " \
                                  %(controlType, float(g_systemSectorCount_CONTROL[controlType])/float(g_hostSectorCount),g_systemWriteCount_CONTROL[controlType], g_systemSectorCount_CONTROL[controlType]))
                for pageType in g_systemSectorCount_GAT.keys():
                    g_Logger.Info("[ValidationRwcLib] GAT %d WriteAmp:    %.2f  GATsystemWriteCount:%d  GATsystemSectorCount: %d " \
                                  %(pageType, float(g_systemSectorCount_GAT[pageType])/float(g_hostSectorCount),g_systemWriteCount_GAT[pageType], g_systemSectorCount_GAT[pageType]))
                g_Logger.Info("*"*160)

        else:
            g_Logger.Info("*********************************************************** HW  Test ****************************************************************")
            g_Logger.Info("[ValidationRwcLib] Host command count: %d Host sector count: %d"%(g_hostWriteCount,g_hostSectorCount))
            g_Logger.Info("*************************************************************************************************************************************")

        writeStatisticsList = []
        writeStatisticsList.append(g_hostWriteCount)
        writeStatisticsList.append(g_hostSectorCount)
        writeStatisticsList.append(g_systemWriteCount)
        writeStatisticsList.append(g_systemSectorCount)

        return writeStatisticsList
        """
        pass
    #End of GetAndPrintWriteStatistics
