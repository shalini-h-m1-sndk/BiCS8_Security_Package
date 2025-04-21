"""
class ValidationRwcManager
Contains APIs to perform BB injection, Preconditioning, Writes/Reads/Erases
@ Author: Shaheed Nehal A
@ copyright (C) 2020 Western Digital Corporation
@ Date: 25-Feb-2020
"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    pass # from builtins import str
    from builtins import range
    pass # from builtins import *
    from builtins import object
from past.utils import old_div
import Core.ValidationError as TestError
import LegacyRWLib
import FwConfig as FwConfig
import random
import Utils as Utils
import FileData as FileData
import BadBlockLib
import SDDVT.Common.SDCommandLib as SDCommandLib
#import SdCommands.SdCommandLibViaLivet as SDCommandLibModel
#import SdSpecificTests.SRW.SrwUtils as SrwUtils
import ValidationSpace
import PatternGen
import CTFServiceWrapper as PyServiceWrap
#import ReduceCapacity
import DiagnosticLib
import Utils
#import GCBalancingUtils
#from CQUtils import CQUtils

DEFAULT_POWER_CYCLE_FREQ = 100
DEFAULT_DELAY_FREQ = 50
g_currentStartLba = None
g_currentTransferLength = None
g_lastcmdIssued = None
g_currentEraseStartLba = None
g_currentEraseTransferLength = None
g_currentReadStartLba = None
g_currentReadTransferLength = None
PATTERNGEN_PATTERN = None
TOTAL_DATA_WRITTEN = 0
GC_SRC_BLOCKS = {}
inject_more_than_max_BBs = False
HOTCOUNT = 100
MODEL_LOGS_SIZE_PRINT_FREQ = 100

CVF_UserPatterns = [
    PyServiceWrap.ALL_0,
    PyServiceWrap.ALL_1,
    PyServiceWrap.BYTE_REPEAT,
    PyServiceWrap.INCREMENTAL,
    PyServiceWrap.RANDOM,
    #PyServiceWrap.FROM_FILE
]

class ValidationRwcManager(object):
    """
      Name:  __init__
      Description: Constructor for ValidationRwcManager
      Return   : None
    """
    def __init__(self,vtfContainer, disableBBVerification=False):
        self.__validationSpace = ValidationSpace.ValidationSpace(vtfContainer)
        self.vtfContainer = vtfContainer
        if vtfContainer.cmd_line_args.init_timeout == None:
            raise TestError.TestFailError(vtfContainer.GetTestName(), "--init_timeout not provided")
        elif vtfContainer.cmd_line_args.read_timeout == None:
            raise TestError.TestFailError(vtfContainer.GetTestName(), "--read_timeout not provided")
        elif vtfContainer.cmd_line_args.write_timeout == None:
            raise TestError.TestFailError(vtfContainer.GetTestName(), "--write_timeout not provided")

        self.__randomSeed = vtfContainer.cmd_line_args.randomSeed
        self.randomObj     = random.Random(self.__randomSeed)
        self.logger        = vtfContainer.GetLogger()
        self.__optionValues = vtfContainer.cmd_line_args
        self.ioCount = 0

        self.fwConfigObj   = self.__validationSpace.GetFWConfigData()
        self.__FileDataObj = FileData.ConfigurationFile21Data(self.vtfContainer)
        #>< Review: Default txlen is X/2-X where X=seqDetThresh
        if self.__optionValues.transferLengthRange == [0x98,0x99]:
            self.vtfContainer.cmd_line_args.transferLengthRange = [old_div(self.__FileDataObj.seqWriteDetectionThreshold,2), self.__FileDataObj.seqWriteDetectionThreshold]
            self.__optionValues = self.vtfContainer.cmd_line_args
            self.__issueOneSectorCommandInBetween = True
        else:
            self.__issueOneSectorCommandInBetween = False
        #Variables
        self.__maxLba              = self.fwConfigObj.maxLba
        self.isReducedCap = False
        self.logger.Info("", "MaxLba of the card: 0x%X "%self.__maxLba)
        if self.vtfContainer.isModel and not self.__optionValues.scaledownEnabled:
            firmware = self.vtfContainer.device_session.GetConfigInfo().GetValue("firmware","")
            if "_RC" in firmware[0].upper():
                self.logger.Info("", "RUNNING ON REDUCED CAPACITY BOT")
                self.isReducedCap = True
        self.__transferLengthRange = self.__optionValues.transferLengthRange
        self.__verifyAtTheEnd      = self.__optionValues.verifyAtEnd

        #Max transferLength for read/write
        self.__maxTransferLenForReadWrite = self.__transferLengthRange[1]

        #Get Lba Range
        self.__lbaRanges = Utils.ProcessLbaRangeInputs(self.__optionValues.lbaRanges, self.__maxLba )

        #minimum and maximum Lba value that has written (That will use for Verify at end)
        self.__minLbaWritten = self.__maxLba +1
        self.__maxLbaWritten = -1


        self.__numOfReads   = 0
        self.__numOfWrites = 0
        self.__numOfErases = 0
        self.__checkpointForWrittenDataPrints = 0x200000
        self.powerCycleOccured = False

        #Gc balancing framework variable
        self.HostWriteCountList = []
        self.__checkpointToLogGCBalancingInfo = 10*self.fwConfigObj.mlcMBSize
        self.__GCBalUtils  = GCBalancingUtils.GCBalancingUtils(self.vtfContainer, self.fwConfigObj)
        self.maxVFCinMLCBlk = old_div(self.fwConfigObj.mlcMBSize, self.fwConfigObj.sectorsPerLgFragment)
        self.GCSrcVFCPrevious = 0
        self.GCSrcVFCCurrent = 0

        if self.vtfContainer.cmd_line_args.UnifiedMLCPool:
            self.HotCountBasedMetaPlaneCycling()

        device_session = self.vtfContainer.device_session
        self.dataTrackingBufferManager = device_session.GetDTBufferManager()

        #Reduced capacity
        self.reduceCapacityEnabled = False
        if self.__optionValues.reducecapacityEnabled and self.vtfContainer.isModel:
            self.reduceCapacityEnabled = True
            self.objReduceCapacity = ReduceCapacity.ReduceCapacity(self.vtfContainer)
            Utils.WriteConfigFile(self.vtfContainer, configFileId=14, Offset=0x41, Value=self.objReduceCapacity.slcPoolSize, numberOfBytes=1)
            Utils.WriteConfigFile(self.vtfContainer, configFileId=14, Offset=0x5C, Value=self.objReduceCapacity.numOfGATBlocks, numberOfBytes=1, doPowerCycle=True)

        #Bad Block library
        self.__badBlockInjected   = False
        if vtfContainer.isModel:
            self.__BadBlockInjection(disableBBVerification=disableBBVerification)
            if self.__optionValues.InitiateBadBlocks:
                self.__badBlockInjected = True
        else:
            #No bad block verification on red cap --> no way to know if a given MB is valid or not due to zone based BBs creating holes randomly in between the card
            if not self.isReducedCap:
                import sys, os
                sys.path.insert(1, os.path.abspath(os.path.join(os.getenv("FVTPATH"), "Tests", "FeatureTests", "BBS")))
                import BadBlockScanLib as BBSLib
                bbsLibObj = BBSLib.BadBlockScanLib(self.vtfContainer)
                badBlockDict, badBlockCountPerDie = bbsLibObj.ReadREGFUSEContents()
                REGFUSE_FBBs = bbsLibObj.extractBBAddrListFromREGFuseDict([badBlockDict, badBlockCountPerDie])
                expectedFBBsInFile224 = bbsLibObj.getExpectedFBBsInFile224(REGFUSE_FBBs)
                Utils.g_factoryMarkedBadBlockList = [tuple(badBlockAddr) for badBlockAddr in expectedFBBsInFile224]
                Utils.VerifyBlockRelinkAndGetAllValidMetaBlockList(self.vtfContainer)

        if self.vtfContainer.cmd_line_args.GCBalancing:
            CurrentFBL = DiagnosticLib.GetFreeMLCBlockCount(self.vtfContainer)
            self.logger.Info("","Current FBL: 0x%X" %(CurrentFBL))
            if self.vtfContainer.cmd_line_args.test.startswith("GCBAL"):
                pass
            else:
                cardCap = old_div((self.__maxLba*512),(1024*1024*1024))
                if cardCap >256:
                    self.__GCBalUtils.UpdateGCBalancingThresholds(self.randomObj.randint(old_div(CurrentFBL,3),old_div((2*CurrentFBL),3)))



        if vtfContainer.isModel:

            # Required for STM based error injection
            self.__livet = vtfContainer._livet
            self.__livetFlash = vtfContainer._livet.GetFlash()
            self.__livetFlash.SetErrorCalcMode(self.__livet.ErrorCalcMode_STM, 0xFFFFFFFF)
            self.__livetFlash.SetVariable('report_wordline_addresses','on')

        #Initialise the parameters regarding Power Cycle
        self.__InitPowerCycle()

        # Initialize delay
        self.__InitDelay()

        #Initialise the parameters regarding STX
        self.__InitialiseSTX()

        #Initialise the parameters related to PGEN
        self.__InitPGEN()

        #Legacy library
        #>< Review: Switch data pattern in every write, or constant random pattern through out the test
        self.__optionValues.switchDataPatternAfterEveryWrite = self.randomObj.choice([0,1])
        self.dataPatternForWrites = self.randomObj.randint(0,1) #Not working for (0,9), need to check with CVF

        #if self.__optionValues.randomDataPattern:
            #self.dataPatternForWrites = self.randomObj.randint(0,9)
        #else:
            #self.dataPatternForWrites = 1

        self.__legacyRWLibObj = LegacyRWLib.LegacyRWLib(vtfContainer,
                                                        self.__maxLba,\
                                                        self.__lbaRanges, \
                                                        maxTransferLength = self.__maxTransferLenForReadWrite,
                                                        writePattern=self.dataPatternForWrites,
                                                        usePatternGen=self.usePatternGen,
                                                        patternToBeUsed=self.__patternGenPattern)
        #CQ library
        self.__cqRWLibObj = None

        #Secure library
        self.__secureRWLibObj = None
        if self.__optionValues.doSecureRW==True:
            self.__secureRWLibObj = SrwUtils.SecureReadWrite(vtfContainer)

        if self.__optionValues.cqWrites or self.__optionValues.cqReads:
            self.cqUtils = CQUtils(self.vtfContainer, self.fwConfigObj, self.__validationSpace)

        #OM library
        self.__omRWLibObj = None

        self.initReadDict()

        self.testFailed = False
        self.FailureMessage = None
        if self.vtfContainer.isModel and self.__optionValues.checkUrgentGC:
            import FirmwareWaypointReg
            WayPointObj = FirmwareWaypointReg.Waypoint(self.vtfContainer)
            WayPointObj.RegisterFirmwareWayPoint(WayPointObj.GCTaskStarted, self._OnGCTaskStarted)
            WayPointObj.RegisterFirmwareWayPoint(WayPointObj.GCCSrcSelect, self._OnGCCSrcSelect)
            WayPointObj.RegisterFirmwareWayPoint(WayPointObj.GCCStart, self._OnGCCStart)
            WayPointObj.RegisterFirmwareWayPoint(WayPointObj.ReadOnlyMode)
            self.__checkUrgentGC = False

        #Precondition with Error
        if self.__optionValues.preconditionBlocksWithError == True:
            import PreconditionBlocksUtil
            #self.__optionValues.errorInjectionPattern = self.randomObj.randint(1,6)
            preconditionBlocksObj = PreconditionBlocksUtil.PreconditionBlockClass(self.__validationSpace, self.__randomSeed)
            preconditionBlocksObj.DoBlockPrecondition()

        #Precondition with Data
        if self.__optionValues.writePercent != None or self.__optionValues.preConditionPattern != ['']:
            import PreConditionPattern

            #If no pattern is provided in cmdline, then randomly pick the pattern
            if self.__optionValues.preConditionPattern == ['']:
                patterns = PreConditionPattern.PRECONDITION_PATTERNS
                if not self.__optionValues.usePatternGen:
                    patterns.remove('SingleFullCardWritePrecondition')
                self.__optionValues.preConditionPattern = [self.randomObj.choice(patterns)]

            #If useUserDefinedWritePercent is set to True, then do not modify the --writePercent
            if not self.__optionValues.useUserDefinedWritePercent:
                #Check if the maxLBA is of 2TB or if its reducedCap
                if self.isReducedCap:
                    if self.__optionValues.usePatternGen:
                        self.__optionValues.writePercent = self.randomObj.choice([80,90,100])
                        self.logger.Info("", "--writePercent randomly chosen between 80-100 since this is with PGEN --> %d"%self.__optionValues.writePercent)
                else:
                    if self.__optionValues.usePatternGen:
                        if self.__optionValues.preConditionPattern == ["RandomWriteOnPartitionedCard"]:
                            self.__optionValues.writePercent = self.randomObj.choice([10,20])
                        else:
                            self.__optionValues.writePercent = self.randomObj.choice([40,50,60])
                        self.logger.Info("", "--writePercent randomly chosen between 40-60 since this is with PGEN --> %d"%self.__optionValues.writePercent)
                    else:
                        #To recheck: For AP - need to discuss
                        Card_Capacity = old_div((self.fwConfigObj.maxLba*512),(1024*1024*1024))
                        if Card_Capacity > 512: 
                            if self.__optionValues.writePercent >= 10:
                                self.__optionValues.writePercent = 10
                                self.logger.Info("", "--writePercent restricted to 10% since this is with CVF")

            self.logger.Info("", "PRECONDITION PATTERN SELECTED: %s"%self.__optionValues.preConditionPattern)
            self.logger.Info("", "PRECONDITION PERCENTAGE: %d"%self.__optionValues.writePercent)
            preConditionPatternObj = PreConditionPattern.DoCardPreCondition(self.vtfContainer, self)
            preConditionPatternObj.Run()


    def printModelLogsDirSize(func):
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            if self.vtfContainer.isModel:
                if self.ioCount % MODEL_LOGS_SIZE_PRINT_FREQ == 0:
                    try:
                        #modelLogsPath = [line for line in self.vtfContainer.modelIniString.split("\n") if line.startswith("folder")][0].split(" = ")[1]
                        self.logger.VtfSmallBanner("Data written = %d MB, Size of model logs dir = %d MB"%(old_div(TOTAL_DATA_WRITTEN, 0x800), old_div(Utils.getDirSize(), (1024 * 1024))))
                    except:
                        pass
                self.ioCount += 1
            return result
        return wrapper

    def GetLegacyRwLibObject(self):
        """
        Description:
           * Returns Legacy RwLib object
        """

        return self.__legacyRWLibObj


    def GetSecureRwLibObject(self):
        """
        Description:
           * Returns Secure RwLib object
        """

        return self.__secureRWLibObj

    @printModelLogsDirSize
    def Write(self, \
              startLba, \
              transferLength, \
              closedEndedCmd = False, \
              doSecureRW = False, \
              selector = None, \
              doCQRW = False,\
              dataBuffer=None,\
              STLength=None,
              preconditioningWrite=False):
        if self.testFailed:
            raise TestError.TestFailError(self.vtfContainer.GetTestName(), "%s"%self.FailureMessage)

        global g_currentStartLba, g_currentTransferLength, g_lastcmdIssued
        g_currentStartLba = startLba
        g_currentTransferLength = transferLength
        g_lastcmdIssued = "Write"

        if doSecureRW:
            if selector == None:
                if self.vtfContainer.isModel:
                    self.__secureRWLibObj.LegacyWrite(startLba, transferLength)
                else:
                    self.__legacyRWLibObj.Write(startLba, transferLength, writeBuffer=dataBuffer)
            else:
                self.__secureRWLibObj.WriteSecure(startLba, transferLength, selector)

        elif doCQRW or self.__optionValues.cqWrites:
            self.cqUtils.issueCqReadWrites(startLba, transferLength, rw="Write")

        #Default case
        else:
            if self.vtfContainer.isModel:
                self.__legacyRWLibObj.Write(startLba, transferLength, STLength=STLength, preconditioningWrite=preconditioningWrite)
            else:
                #self.__SetDataPattern() #To recheck - Not yet tested
                self.__legacyRWLibObj.Write(startLba, transferLength, writeBuffer=dataBuffer, preconditioningWrite=preconditioningWrite)

        #Update the min and max lba written
        if self.__minLbaWritten > startLba:
            self.__minLbaWritten = startLba
        if self.__maxLbaWritten < startLba + transferLength - 1:
            self.__maxLbaWritten = startLba + transferLength - 1

        #New code for Optimization : Code as part of API
        self.updateReadDict(startLba, transferLength)

        self.__numOfWrites += 1
        global TOTAL_DATA_WRITTEN
        TOTAL_DATA_WRITTEN += transferLength
        if TOTAL_DATA_WRITTEN >= self.__checkpointForWrittenDataPrints:
            self.logger.Info("", "[ValidationRwCManager] Data Written in GBs : %d"%(old_div(TOTAL_DATA_WRITTEN,0x200000)))
            if self.vtfContainer.cmd_line_args.GCBalancing:
                FBL = DiagnosticLib.GetFreeMLCBlockCount(self.vtfContainer)
                self.logger.Info("","[ValidationRwCManager] FBL: 0x%X"%(FBL))
            self.__checkpointForWrittenDataPrints += 0x200000

        #Log GC balancing Details after every 2MBs written
        if TOTAL_DATA_WRITTEN >= self.__checkpointToLogGCBalancingInfo:

            #Log Info after every 2 MB if GC is trigerred
            if self.vtfContainer.cmd_line_args.GCBalancing or not self.vtfContainer.isModel:
                if self.LogAndValidateGCBalancingInfo() :
                    self.__checkpointToLogGCBalancingInfo += 2*self.fwConfigObj.mlcMBSize
                #Else, after every 20MBs
                else:
                    self.__checkpointToLogGCBalancingInfo += 4*self.fwConfigObj.mlcMBSize


        #check for performing power cycle
        self.powerCycleOccured = False
        if (self.__doPowerCycle and (self.__powerCycleFreq !=0 )):
            self.__DoPor()

        #check for issuing delay
        if (self.__introduceDelay and (self.__delayFreq !=0 )):
            self.__IntroduceDelay()

        return

    @printModelLogsDirSize
    def Erase(self, \
              startLba, \
              transferLength,\
              doSecureRW = False, \
              selector = None, \
              doCQRW = False):
        if self.testFailed:
            raise TestError.TestFailError(self.vtfContainer.GetTestName(), "%s"%self.FailureMessage)

        global g_currentEraseStartLba, g_currentEraseTransferLength, g_lastcmdIssued
        g_currentEraseStartLba = startLba
        g_currentEraseTransferLength = transferLength
        g_lastcmdIssued = "Erase"

        if doSecureRW and selector!=None:
            self.__secureRWLibObj.EraseSecure(startLba, transferLength, selector)

        elif doCQRW:
            pass

        else:
            self.__legacyRWLibObj.Erase(startLba, transferLength)

        self.__numOfErases  += 1

        #check for performing power cycle
        self.powerCycleOccured = False
        if (self.__doPowerCycle and (self.__powerCycleFreq !=0 )):
            self.__DoPor()

        #check for issuing delay
        if (self.__introduceDelay and (self.__delayFreq !=0 )):
            self.__IntroduceDelay()

        self.updateReadDict(startLba, transferLength, erase=True)

        return

    @printModelLogsDirSize
    def Read(self, \
              startLba, \
              transferLength, \
              doSecureRW = False, \
              selector = None, \
              doCQRW = False,\
              dataBuffer = None,\
              STLength = None):
        if self.testFailed:
            raise TestError.TestFailError(self.vtfContainer.GetTestName(), "%s"%self.FailureMessage)

        global g_lastcmdIssued, g_currentReadStartLba, g_currentReadTransferLength
        g_lastcmdIssued = "Read"
        g_currentReadStartLba = startLba
        g_currentReadTransferLength  = transferLength
        if doSecureRW:
            if selector == None:
                if self.vtfContainer.isModel:
                    self.__secureRWLibObj.LegacyRead(startLba, transferLength)
                else:
                    self.__legacyRWLibObj.Read(startLba, transferLength, readBuffer=dataBuffer)
            else:
                self.__secureRWLibObj.ReadSecure(startLba, transferLength, selector)

        elif doCQRW or self.__optionValues.cqReads:
            self.cqUtils.issueCqReadWrites(startLba, transferLength, rw="Read")

        else:
            if self.vtfContainer.isModel:
                self.__legacyRWLibObj.Read(startLba, transferLength, STLength=STLength)
            else:
                self.__legacyRWLibObj.Read(startLba, transferLength, readBuffer=dataBuffer)

        self.__numOfReads  += 1
        #check for performing power cycle
        self.powerCycleOccured = False
        if (self.__doPowerCycle and (self.__powerCycleFreq !=0 )):
            self.__DoPor()

        #check for issuing delay
        if (self.__introduceDelay and (self.__delayFreq !=0 )):
            self.__IntroduceDelay()

        return

    def GetTheProcessedLbaRange(self):
        return self.__lbaRanges

    def GetTransferLengthRange(self):
        return self.__transferLengthRange

    def __InitPowerCycle(self):

        #power cycle option
        self.__doPowerCycle = self.__optionValues.powCycleEnable

        #get the power cycle frequency
        self.__powerCycleFreq = self.__optionValues.powerCyclefreq

        #Check for the default values of power cycle freq
        if (self.__doPowerCycle and self.__powerCycleFreq ==0):
            self.__powerCycleFreq  = DEFAULT_POWER_CYCLE_FREQ

        return
    #end of __InitPowerCycle


    def __InitDelay(self):

        #delay option
        self.__introduceDelay = self.__optionValues.sdDelay

        #get the delay frequency
        self.__delayFreq = self.__optionValues.sdDelayFreq

        #Check for the default values of delay freq
        if (self.__introduceDelay and self.__delayFreq == 0 ):
            self.__delayFreq  = DEFAULT_DELAY_FREQ

        return
    #end of __InitDelay

    def __InitialiseSTX(self):
        #To recheck - STX related stuff needs to be added
        pass

    def __InitPGEN(self):
        global PATTERNGEN_PATTERN
        self.usePatternGen = self.__optionValues.usePatternGen
        self.logger.Info("", "[ValidationRWCManager] PatternGen Enabled? --> %s"%self.usePatternGen)
        if self.usePatternGen:
            if self.vtfContainer.isModel:
                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "PGEN is applicable only on HW Tests")
            if self.__optionValues.dataPatternForWrites == "Random":
                pattern = self.randomObj.choice([i for i in range(10) if i not in [3,7]]) #ANY_BUFFER, WORD BLOCK NUMBER (RPG-53560) not to be selected
                self.__patternGenPattern = PatternGen.PatternTransformer.pattern[pattern]
                self.logger.Info("", "[ValidationRWCManager] PatternGen Pattern Selected: %s (Pattern #%d)"%(self.__patternGenPattern, pattern))
                PATTERNGEN_PATTERN = self.__patternGenPattern
            else:
                import SDCommandWrapper as sdcmdWrap
                availablePGENPatterns = list(PatternGen.PatternTransformer.pattern.values())
                availablePGENPatterns_String = []
                for pattern in availablePGENPatterns:
                    availablePGENPatterns_String.append(str(pattern))
                if self.__optionValues.dataPatternForWrites not in availablePGENPatterns_String:
                    raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Invalid --dataPatternForWrites provided in cmdline (%s)"%self.__optionValues.dataPatternForWrites)
                else:
                    PGENPatternIndex = list(PatternGen.PatternTransformer.pattern.values()).index(eval("sdcmdWrap.Pattern." + self.__optionValues.dataPatternForWrites))
                    PATTERNGEN_PATTERN = self.__patternGenPattern = PatternGen.PatternTransformer.pattern[PGENPatternIndex]
                    self.logger.Info("", "[ValidationRWCManager] PatternGen Pattern Selected: %s (Pattern #%d)"%(self.__patternGenPattern, PGENPatternIndex))
        else:
            self.__patternGenPattern = None

    def __IntroduceDelay(self):
        """
        Name : __IntroduceDelay
        Description :
                Keeps track of the total no. of commands issued and issues a delay at the set frequency(no. of read/write commands)
        Arguments :
                None

        Return  None
        """

        #Only for model. Add model Check
        if ((self.__numOfReads + self.__numOfWrites + self.__numOfErases) % self.__delayFreq == 0):
            Utils.InsertDelay(self.randomObj.randint(5, 10), self.vtfContainer)

        return


    def __DoPor(self):
        """
        Name : __DoPor
        Description :
                Keeps track of the total no. of commands issued and issued a power cycle at the set frequency(no. of read/write commands)
        Arguments :
                None

        Return  None
        """
        if ((self.__numOfReads + self.__numOfWrites + self.__numOfErases) % self.__powerCycleFreq == 0):
            Utils.PowerCycle(self.vtfContainer, randomObj=self.randomObj)
            self.powerCycleOccured = True

        return

    def __BadBlockInjection(self, disableBBVerification=False):
        self.__botFilename = None
        self.__paramsfilepath = None
        #Marking Bad BLocks
        self.__objBadBlockLib    = None
        self.__badBlockCount     = self.__optionValues.badBlocksCount
        self.__badBlockList      = []
        self.__badBlockCountPerPlane = {}

        if self.__optionValues.SPCBPreCondition == True:
            self.logger.Info("", "Since SPCB is disabled, updating the pattern to inject across all planes")
            self.__optionValues.SPCBPreCondition = False
            self.__optionValues.InitiateBadBlocks = True

        if self.__optionValues.InitiateBadBlocks==True:

            self.__FileDataObj = FileData.ConfigurationFile21Data(self.vtfContainer)
            maxBadBlockCount    = self.__FileDataObj.maxBadBlockCount # FILE_21 offset = 0x50
            self.logger.Info("","Max bad block allowed per plane configured in File 21 (2byte value at offset 0x50) is: %d"%(maxBadBlockCount))

            if self.__badBlockCount > 0:
                if self.__badBlockCount > maxBadBlockCount:
                    self.logger.Info ("","Bad block count 0x%X-(%d) mentioned in command line option exceeds card max badblock limit:%d"\
                                       %(self.__optionValues.badBlocksCount, self.__optionValues.badBlocksCount,maxBadBlockCount ))
                    self.__badBlockCount = maxBadBlockCount
                    self.logger.Info("","Setting badblock count to : %d" %(self.__badBlockCount))


            elif self.__optionValues.badblockrange[0] > 0:
                self.__badBlockCount = self.randomObj.randrange(self.__optionValues.badblockrange[0],self.__optionValues.badblockrange[1])

                if self.__badBlockCount > maxBadBlockCount:
                    self.logger.Info ("","badblockrange=%d-%d passed from cmd line option exceeds card max badblock limit:%d"\
                                       %(self.__optionValues.badblockrange[0], self.__optionValues.badblockrange[1],maxBadBlockCount ))
                    self.__badBlockCount = maxBadBlockCount
                    self.logger.Info("","So setting badblock count to max allowed : %d" %(self.__badBlockCount))
            else:
                self.__badBlockCount = maxBadBlockCount
                self.logger.Info("","Setting badblock count to max allowed : %d" %(self.__badBlockCount))


            if inject_more_than_max_BBs:
                self.__badBlockCount = maxBadBlockCount + self.randomObj.randint(10,20)
                self.logger.Info("","[ValidationRWCManager: BadBlockInjection] Current scenario (more than max BBs). BB Count updated to - %d" %(self.__badBlockCount))

            #RPG-21379, check badblockcount only if InitiateBadBlock is enabled
            # currently the below condition was out of this condition check,
            # this was causing wrong marking of bad blocks, even though we are not creating any badblocks and was failing
            if ( self.__badBlockCount > 0):
                #create the object for  bad block lib
                self.__objBadBlockLib = BadBlockLib.BadBlockValidation(self.vtfContainer, isReducedCap=self.isReducedCap)

                #marks random bad blocks
                self.__badBlockList, self.__badBlockCountPerPlane = self.__objBadBlockLib.MarkRandomBadBlocks(badBlockCount = self.__badBlockCount,
                                                                                                              botFilename   = self.__botFilename,
                                                                                                              paramsfilepath = self.__paramsfilepath,
                                                                                                              disableBBVerification=disableBBVerification)

             #end of if for bad block injection

        if (self.__optionValues.SPCBPreCondition == True and self.__optionValues.InitiateBadBlocks == False):
            raise TestError.TestFailError(self.vtfContainer.GetTestName(), "SP BB marking should not be done (--SPCBPreCondition=True)")
            #self.__FileDataObj  = FileData.ConfigurationFile21Data(self.vtfContainer)
            #maxBadBlockCount    = self.__FileDataObj.maxBadBlockCount # FILE_21 offset = 0x50
            #self.logger.Info("","Max bad block allowed per plane configured in File 21 (2byte value at offset 0x50) is: %d"%(maxBadBlockCount))
            ##create the object for  bad block lib
            #self.__objBadBlockLib = BadBlockLib.BadBlockValidation(self.vtfContainer)
            ##marks random bad blocks
            #self.__objBadBlockLib.MarkRandomBadBlocksSinglePlane(badBlockCount = maxBadBlockCount, botFilename   = self.__botFilename,
                                                   #paramsfilepath = self.__paramsfilepath)

    def OperationToPerformAtEndOfTest(self, disablePowerCycle=False):
        if self.__verifyAtTheEnd:
            self.__VerifyDataAtTheEnd(disablePowerCycle=disablePowerCycle)

        if self.__optionValues.preconditionBlocksWithError:
            self.logger.Info("", "#"*200)
            self.logger.Info("", "[TestRunner] Error Injected list")

            for errorDetails in Utils.g_errorInjectedList:
                self.logger.Info("", "[TestRunner] ErrorType: %08s, metaBlock: 0x%08X, Chip: 0x%08X, Die: 0x%08X, Plane: 0x%08X, Block: 0x%08X, Wordline: 0x%08X, String: 0x%08X, MlcLevel: 0x%08X, EccPage: 0x%08X"
                              %(errorDetails[0],errorDetails[1],errorDetails[2],errorDetails[3],errorDetails[4],errorDetails[5],errorDetails[6],errorDetails[7],errorDetails[8],errorDetails[9]))
            self.logger.Info("", "#"*200)
            self.logger.Info("", "[TestRunner] Error occured list")

            for errorDetails in Utils.g_errorOccurredList:
                self.logger.Info("", "[TestRunner] ErrorType: %08s, metaBlock: 0x%08X, Chip: 0x%08X, Die: 0x%08X, Plane: 0x%08X, Block: 0x%08X, Wordline: 0x%08X, String: 0x%08X, MlcLevel: 0x%08X, EccPage: 0x%08X"
                               %(errorDetails[0],errorDetails[1],errorDetails[2],errorDetails[3],errorDetails[4],errorDetails[5],errorDetails[6],errorDetails[7],errorDetails[8],errorDetails[9]))
            self.logger.Info("", "#"*200)

        return


    def __VerifyDataAtTheEnd(self, objMultiPartition=None, disablePowerCycle=False):
        """
        Name : __VerifyDataAtTheEnd

        Description :
                 It check for entire LBA range.If verify the data only when any LBA is written in the card.

        Arguments :
                SecurityEraseFlag      :  Used for Security Erase
        Return :
             listOfUpdatedLbaAndTransferLength : list containing information for what are the Lbas has written before
        """
        #Logging max Accumulated host sector count in teardown
        if len(self.HostWriteCountList)>0:
            self.logger.Info("", "*"*80)
            self.logger.Info("", "[GC_BALANCING] Maximum Accumulated Host Sector Count : 0x%X"%self.HostWriteCountList[-1])
            self.logger.Info("", "*"*80)

        self.logger.Info("", "Calling GC Profiling Diag : PGC components Quota Time")
        DiagnosticLib.GetPGCTrackerQuotas(self.vtfContainer)

        pendingCVFExceptions = self.__validationSpace.errorManager.GetPendingExceptionList()

        #The assumption is that there would be only 1 CVF exception
        if len(pendingCVFExceptions) >= 1:
            exception = pendingCVFExceptions[0]
            #Boost timer event exception
            if exception.GetErrorGroup() == 0xff22 and exception.GetErrorNumber() == 0x3001:
                self.logger.Info("","[VerifyDataAtTheEnd] [CVF:ErrorHandler] Clearing all Errors as time has elapsed ...")
                self.__validationSpace.errorManager.ClearAllErrors() #This shouldn't be used as it clears all errors, but can be used here since there is only 1 exc
            else:
                return True


        #--------------------------------------------------

        if (disablePowerCycle == False) and (not Utils.IscardInReadOnlyMode(self.vtfContainer)):
            Utils.PowerCycle(self.vtfContainer, randomObj=self.randomObj)
        self.logger.SmallBanner("\n\n\n")
        self.logger.SmallBanner("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        self.logger.SmallBanner("   Verify all written data  ")
        self.logger.SmallBanner("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        self.logger.SmallBanner("Warning: Verification process may take longer time for larger LBA ranges")

        global g_lastcmdIssued, g_currentReadStartLba, g_currentReadTransferLength
        for i in self.__readDict:
            g_lastcmdIssued = "VerifyAtEndRead"
            g_currentReadStartLba = self.__readDict[i][0]
            g_currentReadTransferLength  = self.__readDict[i][1] - self.__readDict[i][0]

            if self.vtfContainer.isModel:
                if g_currentReadTransferLength <= 0:
                    continue
                dataTrackingHandle = self.vtfContainer._livet.GetDataTracking()
                patternList = dataTrackingHandle.GetPatternForLBARange(g_currentReadStartLba, g_currentReadTransferLength)

                #Get the indices where the LBA is marked as UNPREDICTABLE from test end
                indicesOfErroneousPatterns = []
                for errorPattern in list(self.__validationSpace.livetErrorDataPattern.keys()):
                    if errorPattern in patternList:
                        self.logger.Warning("", "Few LBAs in current range are returning %s pattern. Ignoring these LBAs and reading only valid LBAs"%self.__validationSpace.livetErrorDataPattern[errorPattern])
                        for index, pattern in enumerate(patternList):
                            if pattern == errorPattern:
                                indicesOfErroneousPatterns.append(index)

                #Skip the erroneous LBAs and read only the valid LBAs
                if indicesOfErroneousPatterns != []:
                    startLba = g_currentReadStartLba
                    for index in indicesOfErroneousPatterns:
                        endLba = g_currentReadStartLba + index
                        if startLba != endLba:
                            #print (startLba, endLba)
                            self.__legacyRWLibObj.VerifyAllWrittenData(lbaRange=[startLba, endLba])
                        startLba = endLba + 1

                    #The left over good LBAs in the list need to be added to valid LBA list
                    if indicesOfErroneousPatterns[-1] < len(patternList)-1:
                        startLba = g_currentReadStartLba + indicesOfErroneousPatterns[-1] + 1
                        #print (startLba, g_currentReadStartLba+g_currentReadTransferLength)
                        self.__legacyRWLibObj.VerifyAllWrittenData(lbaRange=[startLba, g_currentReadStartLba+g_currentReadTransferLength])

                else:
                    #If none of the LBAs in current range are marked as UNPREDICTABLE, then read entire range
                    self.__legacyRWLibObj.VerifyAllWrittenData(lbaRange = [self.__readDict[i][0], self.__readDict[i][1]])
            else:
                self.__legacyRWLibObj.VerifyAllWrittenData(lbaRange = [self.__readDict[i][0], self.__readDict[i][1]])

        self.logger.SmallBanner("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        self.logger.SmallBanner("%%%%%%%%%%%%%%%%    All written data verified     %%%%%%%%%%%%%%%%%%%%%%")
        self.logger.SmallBanner("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        return

    def _OnGCTaskStarted(self, eventkey, args):
        #Bank:0x0, GCComponentType:0x4, GCCategoryType:0x2, Time:0x96
        '''
        typedef enum _GC_Component_t
        {
            GC_Component_MIP,
            GC_Component_GatPhasedEPWR_GC,
            GC_Component_GatCompaction,
            GC_Component_SLCCompaction,
            GC_Component_MLCCompaction,
            GC_Component_Folding,
            GC_Component_ReadScrub,
            GC_Component_WearLevelling,
            GC_Component_ImmediateGC,
            GC_Component_RandomBlkGC,
            GC_Component_PF,
            GC_Component_GATSync,
            GC_Component_Last
        } GC_Component_t;
        '''
        if args[1] in [0x0, 0x1, 0x2, 0x3, 0x6, 0X8]:
            self.__blockType = "SLC"
        elif args[1] in [0x4, 0x5]:
            self.__blockType = "MLC"
        else:
            self.__blockType = "Unknown"


    def _OnGCCSrcSelect(self, eventKey, args):
        #SrcSlot:0x%X, SrcMB:0x%X, VFC:0x%X
        VFC = args[2]
        if self.__blockType == "SLC":
            totalFragsInBlock = old_div(self.fwConfigObj.slcMBSize,self.fwConfigObj.sectorsPerLgFragment) #Need to check for SLC/MLC GC before this
        elif self.__blockType == "MLC":
            totalFragsInBlock = old_div(self.fwConfigObj.mlcMBSize,self.fwConfigObj.sectorsPerLgFragment) #Need to check for SLC/MLC GC before this
        else:
            return
        VFC_Percentage = float(old_div(totalFragsInBlock,VFC)) * 100

        if VFC_Percentage >= 80:
            self.__checkUrgentGC = False
        else:
            self.__checkUrgentGC = True

    def _OnGCCStart(self, eventKey, args):
        #Src MB:0x%X, Dest MB:0x%X, Block Type:0x%X, Urgent:0x%X, Compaction Type:0x%X
        global GC_SRC_BLOCKS

        if self.__checkUrgentGC and args[3] == True:
            self.testFailed = 1
            self.FailureMessage = "GC_TASK_URGENT hit. Urgent GC not expected"
            self.logger.Error("", "[Test: Error] %s"%self.FailureMessage)
            return

    def __SetDataPattern(self):
        retainOtherPatternIDs = False
        patternDict = dict()

        maxPatternID = self.dataTrackingBufferManager.GetMaxPatternID()
        randomPattern = self.randomObj.choice(CVF_UserPatterns)
        for i in range(maxPatternID):
            patternInfo = PyServiceWrap.PatternInfo()
            patternInfo.patternType = self.randomObj.choice(CVF_UserPatterns) #randomPattern
            patternInfo.value = self.randomObj.randint(0, 255) #Applicable only for BYTE_REPEAT/INCREMENTAL
            patternDict[i] = patternInfo
        '''
        patternInfo = PyServiceWrap.PatternInfo()
        patternInfo.patternType = self.randomObj.choice(CVF_UserPatterns)
        patternInfo.value = self.randomObj.randint(0, 255)
        patternDict[0] = patternInfo
        self.logger.Info("", "Random data pattern selected - %s"%patternInfo.patternType)
        '''
        self.dataTrackingBufferManager.SetPatterns(patternDict, retainOtherPatternIDs)

    def GetBadBlockInfo(self):
        return self.__badBlockList, self.__badBlockCountPerPlane

    def LogAndValidateGCBalancingInfo(self):

        GCtype = { 0: "IDLE", 1: "BALANCED", 2 : "ACCELERATED", 3: "URGENT", 4: "UNDEFINED"}

        databuf = DiagnosticLib.GetGCBalancedInfo(self.vtfContainer)
        isGCTrigerred = databuf.GetOneByteToInt(0)
        GCstate = databuf.GetOneByteToInt(1)
        HostWriteCount = databuf.GetFourBytesToInt(2)
        CurrentGCSrcVFC = databuf.GetFourBytesToInt(6)
        VFCPercentage = (float(CurrentGCSrcVFC)/self.maxVFCinMLCBlk)*100

        self.GCSrcVFCPrevious = self.GCSrcVFCCurrent
        self.GCSrcVFCCurrent = VFCPercentage

        self.logger.Info("", "[VALIDATION_RWC GC_BALANCING] GC Balancing Trigerred : 0x%X"%isGCTrigerred)
        self.logger.Info("", "[VALIDATION_RWC GC_BALANCING] VFC of Current GC Src Blk : 0x%X"%CurrentGCSrcVFC)
        if self.GCSrcVFCPrevious != 0:
            self.logger.Info("", "[VALIDATION_RWC GC_BALANCING] VFC Percentage of Previous GC Source Block: %.2f"%(self.GCSrcVFCPrevious))
        self.logger.Info("", "[VALIDATION_RWC GC_BALANCING] VFC Percentage of Current GC Src Blk : %.2f"%VFCPercentage)

        if isGCTrigerred :
            if GCstate in GCtype:
                self.logger.Info("", "[VALIDATION_RWC GC_BALANCING] GC is triggered in %s state"%GCtype[GCstate])
            else:
                self.logger.Info("", "ERROR ::: [VALIDATION_RWC GC_BALANCING] GC is triggered in unexpected 0x%X state"%GCstate)

        self.logger.Info("", "[VALIDATION_RWC GC_BALANCING] Accumulated host write count : 0x%X"%HostWriteCount)

        if HostWriteCount not in self.HostWriteCountList:
            self.HostWriteCountList.append(HostWriteCount)
            self.HostWriteCountList = sorted(self.HostWriteCountList)

        #1. CHECK IF FBL < THRESHOLDS
        FBL = DiagnosticLib.GetFreeMLCBlockCount(self.vtfContainer)
        self.logger.Info("", "MLC FBL  count: 0x%X "%(FBL))

        #GC should not trigger
        cardCap = old_div((self.fwConfigObj.maxLba*512),(1024*1024*1024))
        if self.vtfContainer.cmd_line_args.GCBalancing and cardCap > 256:
            BalancedGCThreshold = GCBalancingUtils.BALANCED_GC_THRESHOLD
            AccleratedGCThreshold = GCBalancingUtils.BALANCED_GC_THRESHOLD - (self.__FileDataObj.BalancedGCThreshold - self.__FileDataObj.AccleratedGCThreshold)
            UrgentGCThreshold = GCBalancingUtils.BALANCED_GC_THRESHOLD - (self.__FileDataObj.BalancedGCThreshold - self.__FileDataObj.UrgentGCThreshold)
        else:
            BalancedGCThreshold =  self.__FileDataObj.BalancedGCThreshold
            AccleratedGCThreshold = self.__FileDataObj.AccleratedGCThreshold
            UrgentGCThreshold = self.__FileDataObj.UrgentGCThreshold

        ROModeThreshold =  UrgentGCThreshold - self.__FileDataObj.UrgentGCThreshold

        self.logger.Info("", "[VALIDATION_RWC GC_BALANCING] Thresholds for GC_BALANCING => Balanced GC : 0x%X , Accelerated GC : 0x%X , Urgent GC : 0x%X "%(BalancedGCThreshold, AccleratedGCThreshold, UrgentGCThreshold))
        self.logger.Info("", "[VALIDATION_RWC GC_BALANCING] Thresholds for RO_MODE =>  0x%X"%ROModeThreshold)

        if not self.vtfContainer.cmd_line_args.test.startswith("GCBAL") and self.vtfContainer.cmd_line_args.GCBalancing == True:
            if GCtype[GCstate] == "URGENT" and CurrentGCSrcVFC != 0:
                if self.GCSrcVFCPrevious < 75 and self.GCSrcVFCCurrent < 75 :
                    self.logger.Info ("", "Test is triggered in Balanced Mode, but it is going in Urgent mode and current GC Src VFC is %.2f"%VFCPercentage)
                    raise TestError.TestFailError("", "Test is triggered in Balanced Mode, but it is going in Urgent mode and current GC Src VFC is %.2f"%VFCPercentage)

            if GCtype[GCstate] == "ACCELERATED" and CurrentGCSrcVFC != 0:
                if self.GCSrcVFCPrevious < 45 and self.GCSrcVFCCurrent < 45 :
                    self.logger.Info ("", "Test is triggered in Balanced Mode, but it is going in Accelerated mode and current GC Src VFC is %.2f"%VFCPercentage)
                    raise TestError.TestFailError("", "Test is triggered in Balanced Mode, but it is going in Accelerated mode and current GC Src VFC is %.2f"%VFCPercentage)

        return isGCTrigerred

    def HotCountBasedMetaPlaneCycling(self):

        global HOTCOUNT
        self.TargetedBlockinMMP = [ [] for i in range(self.fwConfigObj.numberOfMetaPlane) ]
        for MMP in range(self.fwConfigObj.numberOfMetaPlane):
            self.logger.Info("", "Selected MMP: 0x%X"% (MMP))
            self.__MMPwiseBlockList = []
            MMPwiseBlockList = list(range(MMP,self.fwConfigObj.totalMetaBlocksInCard,self.fwConfigObj.numberOfMetaPlane)) #Includes SLC also
            for block in MMPwiseBlockList:
                BlockInfo = DiagnosticLib.GetIGATEntryInfo(self.vtfContainer, block)
                if BlockInfo[4] == 1:
                    self.__MMPwiseBlockList.append(block)
                    DiagnosticLib.SetHotCountOneBlock(self.vtfContainer, block, HOTCOUNT)

            self.logger.Info("", "Block List in MMP 0x%X: %s"% (MMP, self.__MMPwiseBlockList))
            self.TargetedBlockinMMP[MMP] = self.randomObj.sample(self.__MMPwiseBlockList, self.fwConfigObj.numberOfMetaPlane)
            self.logger.Info("", "Targeted Block in MMP 0x%X: %s"% (MMP, self.TargetedBlockinMMP[MMP] ))
            HotCount = old_div(self.__FileDataObj.WlFreq,2)
            Delta = 0
            for Blk in self.TargetedBlockinMMP[MMP]:
                DiagnosticLib.SetHotCountOneBlock(self.vtfContainer, Blk, HotCount+Delta )
                BlockInfo_updatedHC = DiagnosticLib.GetIGATEntryInfo(self.vtfContainer, Blk)
                self.logger.Info("", "IGAT entry for MB 0x%X after updating Hot Count => %s"%(Blk, BlockInfo_updatedHC))
                Delta += 1

        Utils.PowerCycle(self.vtfContainer)
        HOTCOUNT += 10


    def updateReadDict(self, startLba, transferLength, erase=False):
        if not self.usePatternGen and erase:
            return
        cardMapWriteLba = startLba
        cardMapTrLen = transferLength
        partition = old_div(cardMapWriteLba,self.__partitionSize)

        if partition not in self.__readDict:
            if old_div((cardMapTrLen + cardMapWriteLba),self.__partitionSize) == partition and not erase:
                self.__readDict[partition] = [cardMapWriteLba , cardMapWriteLba + cardMapTrLen -1]
            else:
                for i in range(partition, old_div((cardMapTrLen + cardMapWriteLba),self.__partitionSize)):
                    if i == partition and not erase:
                        self.__readDict[i] = [cardMapWriteLba, (i + 1) * self.__partitionSize -1]
                    else:
                        if not erase:
                            self.__readDict[i] = [i * self.__partitionSize, (i + 1) * self.__partitionSize -1]
                        else:
                            self.__readDict.pop(i, None)
                if not erase:
                    self.__readDict[(old_div((cardMapTrLen + cardMapWriteLba),self.__partitionSize))] = [(old_div((cardMapTrLen + cardMapWriteLba),self.__partitionSize)) * self.__partitionSize, cardMapWriteLba + cardMapTrLen -1]
                else:
                    self.__readDict.pop(old_div((cardMapTrLen + cardMapWriteLba),self.__partitionSize), None)
        else:
            if old_div((cardMapTrLen + cardMapWriteLba),self.__partitionSize) == partition:
               #Update the min and max lba written in the same partition
                if not erase:
                    if self.__readDict[partition][0] > cardMapWriteLba :
                        self.__readDict[partition][0] = cardMapWriteLba
                    if self.__readDict[partition][1] < cardMapWriteLba+ cardMapTrLen -1:
                        self.__readDict[partition][1] = cardMapWriteLba+ cardMapTrLen -1
                else:
                    self.__readDict.pop(partition, None)
            else:
                for i in range(partition, old_div((cardMapTrLen + cardMapWriteLba),self.__partitionSize)):
                    if i == partition:
                        if not erase:
                            if self.__readDict[i][0] > cardMapWriteLba :
                                self.__readDict[i][0] = cardMapWriteLba
                            self.__readDict[i][1] =  (i + 1) * self.__partitionSize -1
                        else:
                            self.__readDict.pop(i, None)
                    else:
                        if not erase:
                            self.__readDict.update({i: [i * self.__partitionSize, (i+1) * self.__partitionSize - 1]})
                        else:
                            self.__readDict.pop(i, None)

                if old_div((cardMapTrLen + cardMapWriteLba),self.__partitionSize) in self.__readDict and not erase:
                    self.__readDict[old_div((cardMapTrLen + cardMapWriteLba),self.__partitionSize)][0] = (old_div((cardMapTrLen + cardMapWriteLba),self.__partitionSize)) * self.__partitionSize
                    if self.__readDict[old_div((cardMapTrLen + cardMapWriteLba),self.__partitionSize)][1] < cardMapWriteLba + cardMapTrLen - 1 :
                        self.__readDict[old_div((cardMapTrLen + cardMapWriteLba),self.__partitionSize)][1] = cardMapWriteLba + cardMapTrLen - 1
                else:
                    if not erase:
                        self.__readDict.update({ old_div((cardMapTrLen + cardMapWriteLba),self.__partitionSize) : [ (old_div((cardMapTrLen + cardMapWriteLba),self.__partitionSize)) * self.__partitionSize , cardMapWriteLba + cardMapTrLen - 1]})
                if erase:
                    self.__readDict.pop(old_div((cardMapTrLen + cardMapWriteLba),self.__partitionSize), None)


    def updateCqWritesInReadDict(self, cqWriteList):
        for item in cqWriteList:
            self.updateReadDict(*item)
            
            
    def initReadDict(self):
        ### New code for optimization of 'Verify at End Funct' ###
        self.__readDict = {}
        self.__partitionSize = self.fwConfigObj.sectorsPerLg * 2
        ### New code for optimization of 'Verify at End Funct' ###     
