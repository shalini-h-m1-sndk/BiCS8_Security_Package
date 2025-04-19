from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    pass # from builtins import *
import argparse
import FirmwareWaypointReg
import Lib.Utilities.TypesConvert as TypesConvert
import Core.Basic.TestCase as TestCaseBase
import re
from itertools import groupby
import Utils

RR_CMDPREFIX_CONFIG = [-1] * (len(FirmwareWaypointReg.ReadRetryState)-1) #Remove UECC

def CmdLineArgs(VTFargparse):
    # ###########NSV Args #############
    VTFargparse.add_argument("--nsv", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--MSTO", type = str, default = "None")
    VTFargparse.add_argument("--act", type = TypesConvert.str2bool, default = False)

    # ############# ROM Mode args ############
    VTFargparse.add_argument("--romMode", type=TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--botfilename", type=str, default = None)
    VTFargparse.add_argument("--fileIDs", type=str, default = 'random')    

    # ############# PGEN args ############
    VTFargparse.add_argument("--usePatternGen", type=TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--doComparePatternGen", type=TypesConvert.str2bool, default = False)

    # ############# RC plan global variables ############
    VTFargparse.add_argument("--numberOfDiesInCard", type=int, default = 8)
    VTFargparse.add_argument("--isShiftedDualWrite", type=TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--lbaRanges", type=str2IntRange, default = [0,-1])
    VTFargparse.add_argument("--randomSeed", type=int, default = Utils.GetRandomSeed())
    VTFargparse.add_argument("--regressionDuration", type=int, default = 43200) #In secs (Default = 12hrs)


    # ############# ValidationRWCManager/Lib related args ############
    #Default --transferLengthRange is not 0x98-0x99, but rather seqdetThresh/2 - seqdetThresh
    #0x98-0x99 is to identify if test is not updating this range in cmdline (Check ValidationRwcManager where this gets updated)
    VTFargparse.add_argument("--transferLengthRange", type = str2IntRange, default = "0x98-0x99")
    VTFargparse.add_argument("--verifyAtEnd", type = TypesConvert.str2bool, default = True)
    VTFargparse.add_argument("--lbaRanges", type = str2ListOfRanges, default = "0:-1")
    VTFargparse.add_argument("--InitiateBadBlocks", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--sdDelay", type = TypesConvert.str2bool, default = True)
    VTFargparse.add_argument("--sdDelayFreq", type=int, default = 8000)
    VTFargparse.add_argument("--powCycleEnable", type = TypesConvert.str2bool, default = True)
    VTFargparse.add_argument("--powerCyclefreq", type=int, default = 1000)
    VTFargparse.add_argument("--testNameList", type=str2StringList, default = [])
    VTFargparse.add_argument("--ProductType", type=str2StringList, default = "DW")
    VTFargparse.add_argument("--badBlocksCount", type=int, default = 0)
    VTFargparse.add_argument("--SPCBPreCondition", type=TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--stPowCycle", type=TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--verifyManualLock", type=TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--UnifiedMLCPool", type=TypesConvert.str2bool, default = False)

    #SFFU
    VTFargparse.add_argument("--sFFUPowerCycle", type=TypesConvert.str2bool, default = True)
    VTFargparse.add_argument("--NoPowerOffForsFFUCMCReset", type=TypesConvert.str2bool, default = False)    

    # ############ Additional cmd line args used by AP testcases #############
    VTFargparse.add_argument("--testmaxlba", type=int, default=0)
    VTFargparse.add_argument("--totalCommandsPerCycle", type=str2IntRange, default = [500,1000])
    VTFargparse.add_argument("--testDuration", type = str, default = None)
    VTFargparse.add_argument("--applicationDuration", type = str, default = None)
    VTFargparse.add_argument("--testCount", type=int, default=None) #Total number of tests to be run (each test could be randomly chosen from the testnamelist)
    VTFargparse.add_argument("--alignvalue", type=int, default=0) #Number of sectors(should be multiple of 8 sector or 4k fragment(default  is 0)
    VTFargparse.add_argument("--lbaOffsetRange", type=list, default = [1,0x80])
    VTFargparse.add_argument("--addressToCompare", type=int, default=2)
    VTFargparse.add_argument("--maxDataLength", type=int, default=256)
    VTFargparse.add_argument("--dataLengthStep", type=int, default=2)
    VTFargparse.add_argument("--zigzagArmLengthRange", type=list, default = [1000,5000])
    VTFargparse.add_argument("--zigzagArmsCountRan", type=list, default = [30,40])
    VTFargparse.add_argument("--calcWriteAmp", type=TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--printHCOfAllBlks", type=TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--forceGC", type=TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--randomDataPattern", type=TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--checkUrgentGC", type=TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--dataPatternForWrites", type = str, default = "Random")
    VTFargparse.add_argument("--WearLevellingPhase", type = str, default = "Relocation")
    VTFargparse.add_argument("--WLVFCReduce", type=TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--disableWaypointLogging", type=TypesConvert.str2bool, default = False)


    # ############ Additional cmd line args used by Feature testcases #############
    VTFargparse.add_argument("--selectRandomSdrMode", type=TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--selectrandomHtatValue", type=TypesConvert.str2bool, default = True)
    VTFargparse.add_argument("--htatValue", type=int, default=0)
    VTFargparse.add_argument("--sdwCheck", type=TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--caseToRun", type=int, default = 0)
    VTFargparse.add_argument("--exceedStream", type=TypesConvert.str2bool, default = False)

    # ############ Cmd line args used in SDR mode Switch #############
    VTFargparse.add_argument("--sdrMode", type = str, default = None)
    VTFargparse.add_argument("--sdConfiguration", type = str, default = None)
    VTFargparse.add_argument("--doSDRSwitchDuringPC", type=TypesConvert.str2bool, default = True) #>< Review: Default=True
    VTFargparse.add_argument("--ProjConfig", type = str, default = "Felix")
    VTFargparse.add_argument("--LV", type = int, default = 0)
    VTFargparse.add_argument("--CQ", type=TypesConvert.str2bool, default = False)

    # ############ Cmd line args used by CAM testcases #############
    VTFargparse.add_argument("--inputFileName", type = str, default = None)
    VTFargparse.add_argument("--camPatternCycles", type=int, default = 5)
    # ############ Cmd line args used by Host Pattern testcases #############
    VTFargparse.add_argument("--inputDir", type = str, default = None)

    # ############# PData/Error Precondition related args #############
    VTFargparse.add_argument("--writePercent", type=int, default = None) #This is used to indicate card fill percentage
    VTFargparse.add_argument("--enableFwWaypoint", type=TypesConvert.str2bool, default = False) #To enable WPs during precond
    VTFargparse.add_argument("--preConditionPattern", type=str2StringList, default = "") #This is used to indicate in which pattern card needs to be preconditioned
    VTFargparse.add_argument("--partitionCard", type=int, default = 5) #This is used to partition the card logically
    VTFargparse.add_argument("--transferLengthList", type=list, default = [0x4,0x8,0x10,0x20,0x40,0x80,0x100]) #List of transferlengths
    VTFargparse.add_argument("--forceGC", type=TypesConvert.str2bool, default = False) #To force GC in AP tests
    VTFargparse.add_argument("--PreLbaRanges", type=str2ListOfRanges, default = "0:-1")
    VTFargparse.add_argument("--errorInjectionPattern", type=int, default = 1)
    VTFargparse.add_argument("--preconditionBlocksWithError", type=TypesConvert.str2bool, default = False) #Test preconditions blocks with errors
    VTFargparse.add_argument("--errorType", type = str, default = '')
    VTFargparse.add_argument("--numberOfErrorsToInject", type=int, default = 1) #number of eoors to inject, defaultValue = 1
    VTFargparse.add_argument("--pfConfiguration", type=int, default = 0)
    VTFargparse.add_argument("--epwrConfiguration", type=int, default = 0)
    VTFargparse.add_argument("--Pattern", type=str, default = None)
    VTFargparse.add_argument("--GCBalancing", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--useUserDefinedWritePercent", type = TypesConvert.str2bool, default = False)

    # ############# mode check argument #############
    VTFargparse.add_argument("--isSdMode", type=TypesConvert.str2bool, default = False) #used to parse the mode in which want to execute
    VTFargparse.add_argument("--hWDataTrackingEnabled", type=TypesConvert.str2bool, default = False) #used to enable the hardware data tracking
    VTFargparse.add_argument("--hWDataTrackingDataLoad", type=TypesConvert.str2bool, default = False) #used to load the data tracked for HW verification
    VTFargparse.add_argument("--NDWL_Mode", type = str, default = "SGD")

    # ############# sparsely used arguments #############
    VTFargparse.add_argument("--OTM_Freq", type=int, default = None)
    VTFargparse.add_argument("--numOfQs", type=int, default = None)  #used for CreateAllQs
    VTFargparse.add_argument("--queueSize", type=str, default = None)
    VTFargparse.add_argument("--QD", type=int, default = None)  #Used for CreateAllQs
    VTFargparse.add_argument("--randomQs", type = TypesConvert.str2bool, default = None)
    VTFargparse.add_argument("--randomQD", type = TypesConvert.str2bool, default = None)
    VTFargparse.add_argument("--QInfo", type=str, default = None)
    VTFargparse.add_argument("--lbaDataSize",type=int,default=None)#used for setting lba size
    #Used for Qs with Different Depth and CQs Format: <csvSQIDs-csvQDs-perCQID> : <csvSQIDs-csvQDs-perCQID>
    # eg. 1,2,3-4,32,64-1 : 4,5-64,64-2
    #SQID1 with Q size 4, SQID2 with Q Size 32, SQID3 with Q Size 64 are associated to CQID1
    #SQID4 with Q size 64, SQID5 with Q Size 64 are associated to CQID2
    VTFargparse.add_argument("--manualDoorBell", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--drawGraph", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--isPICT", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--lbaDataPattern", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--numOfCmdsToWFC", type = int, default = 5000)
    VTFargparse.add_argument("--numOfCmdsToDBL", type = int, default = 256)

    VTFargparse.add_argument("--numOfNS", type=int, default = None)
    VTFargparse.add_argument("--namespaceTest", type = str, default = False)

    VTFargparse.add_argument("--DTTraceForHW", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--livetTrace", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--CItestUUID", type = str, default = None)

    VTFargparse.add_argument("--PECSLCLimit", type = int, default = 75000)
    VTFargparse.add_argument("--PECTLCLimit", type = int, default = 1500)
    VTFargparse.add_argument("--isNST", type = TypesConvert.str2bool, default = False)

    # ############# AP Test related arguments #############
    VTFargparse.add_argument("--toggleVWC", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--toggleFUA", type = str, default = None)
    VTFargparse.add_argument("--syncMode", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--amountOfDataInSectors", type = int, default = None)
    VTFargparse.add_argument("--alignment", type = int, default = None)
    VTFargparse.add_argument("--transferLength", type = int, default = None)
    VTFargparse.add_argument("--startLba", type = int, default = None)
    VTFargparse.add_argument("--startLbaNumber", type = int, default = None)
    VTFargparse.add_argument("--endLba", type = int, default = None)
    VTFargparse.add_argument("--format", type = int, default = 512)
    VTFargparse.add_argument("--FDEndOfTest", type = str, default = None)
    #VTFargparse.add_argument("--customTransferLengthList", type = TypesConvert.str2List, default = None)
    VTFargparse.add_argument("--openEndedCmd", type = TypesConvert.str2bool, default = True)
    VTFargparse.add_argument("--frontEndTest", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--customTransferLengthList", type = str, default = None)
    VTFargparse.add_argument("--APTests", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--writeMultiplier", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--modelCapacity", type = str, default = None)
    VTFargparse.add_argument("--disableFVTPrints", type = TypesConvert.str2bool, default = False)
    #VTFargparse.add_argument("--testCycleCount", type = int, default = 1)
    VTFargparse.add_argument("--readWriteSelect", type = str, default = None)
    VTFargparse.add_argument("--randomWorkload", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--injectEI", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--lbaDataSize",type=int,default=None)#used for setting lba size
    VTFargparse.add_argument("--switchDataPatternAfterEveryWrite", type=TypesConvert.str2bool, default=False)

    #Used for AP when reading commands from CSV
    VTFargparse.add_argument("--csvLocation", type=str, default = False)

    VTFargparse.add_argument("--blackBox", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--grayBox", type = TypesConvert.str2bool, default = False)

    # ############# WriteZero related arguments #############
    VTFargparse.add_argument("--typeOfWrite", type = str, default = None)
    VTFargparse.add_argument("--wrWeightage", type = int, default = None)
    VTFargparse.add_argument("--numOfCmdsWzWr", type = int, default = None)

    # ############# NSV used arguments #############
    VTFargparse.add_argument("--nsv", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--act", type = TypesConvert.str2bool, default = False)

    # ############# model Report CSV create used arguments #############
    VTFargparse.add_argument("--modelCsv", type = TypesConvert.str2bool, default = False)


    # ############# Fadi used arguments #############
    VTFargparse.add_argument("--disableFadi", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--fadiFile", type = str, default = None)
    VTFargparse.add_argument("--sdbFile", type = str, default = None)
    VTFargparse.add_argument("--codeESL", type = str, default = None)
    VTFargparse.add_argument("--elseverity", type = str, default = None)
    VTFargparse.add_argument("--smallDump", type = str, default = None)


    # ############# PWRM used arguments #############
    VTFargparse.add_argument("--powerState", type = int, default = None)
    VTFargparse.add_argument("--NonL12", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--PwrmPowerCycleTest", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--ignorePMMCounterValidation", type = TypesConvert.str2bool, default = False)

    # ############# Bullseye Coverage related arguments #############
    VTFargparse.add_argument("--commitID", type = str, default = None)
    VTFargparse.add_argument("--coverageRun", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--FWVersion", type = str, default = False)
    VTFargparse.add_argument("--serverPath", type = str, default = None)

    # ############# Compare Test arguments #############
    VTFargparse.add_argument("--compareEn", type = TypesConvert.str2bool, default = False)


    # ############# DPA Test arguments #############
    # paDebug - use detemenistic decisions instead of random decision (for debug purpose)
    VTFargparse.add_argument("--dpaDebug", type = TypesConvert.str2bool, default = False)
    # paUseEi - use error injection tools for accurate power aborts
    VTFargparse.add_argument("--dpaUseEi", type = TypesConvert.str2bool, default = False)

    VTFargparse.add_argument("--ModelTraceOn", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--delayBeforeUGSD", type = int, default = 0)
    VTFargparse.add_argument("--loadEIFile", type=str, default = None)
    VTFargparse.add_argument("--CmdLineBasedUGSDEnable", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--numOfUGSDForOTM", type = int, default = 0)
    VTFargparse.add_argument("--enableUGSDAndWAStatistics", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--ignoreSpecificTestLogicForDPA", type = TypesConvert.str2bool, default = False)


    # ###### WEAR LEVEL TEST ARGUMENT ######## #
    VTFargparse.add_argument("--wearLevelCheck", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--WLpriority", type=str, default = None)

    # ###### BKOPS OTM TEST ARGUMENT ######## #
    VTFargparse.add_argument("--testRelocation", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--bkopsTrigger", type = str, default = "")

    # ############ Error Injection Test arguments #############
    VTFargparse.add_argument("--ReturnLBA", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--UseEIFramework", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--EIPattern", type = str, default = None)
    VTFargparse.add_argument("--blockType", type = str, default = None)
    VTFargparse.add_argument("--PercentageOfPFEFerrors", type = int, default = 0)
    VTFargparse.add_argument("--isEItest", type = str, default = False)

    # ############# Format Gray box Test argument --formatInBtwVar --userErsInBtwVar #############
    VTFargparse.add_argument("--formatInBtwVar", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--userErsInBtwVar", type = TypesConvert.str2bool, default = False)

    # ############# Xplorer related arguments #############
    VTFargparse.add_argument("--FVTXplorer", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--rwrFilePath", type = str, default = None)
    VTFargparse.add_argument("--configPath", type = str, default = None)
    VTFargparse.add_argument("--remoteAddress", type = str, default = '127.0.0.1')
    VTFargparse.add_argument("--remotePort", type = int, default = 8081)
    VTFargparse.add_argument("--informerSerialNumber", type = str, default = '000000')
    VTFargparse.add_argument("--product", type = str, default = 'Hermes')
    VTFargparse.add_argument("--atbMode", type = str, default = '20E')
    VTFargparse.add_argument("--calibrationEnabled", type = str, default = 'false')
    VTFargparse.add_argument("--rwrPath", type = str, default = 'rwrPath')
    VTFargparse.add_argument("--rwrMaxFileSize", type = int, default = 100)
    VTFargparse.add_argument("--rwrMaxFileCount", type = int, default = 100)
    VTFargparse.add_argument("--dcoPath", type = str, default = 'dcoPath')
    VTFargparse.add_argument("--genType", type = str, default = 'Gen2')
    VTFargparse.add_argument("--FVTxplorerClusterIP", type = str, default = "127.0.0.1")
    VTFargparse.add_argument("--waitUntilAuraProcessComplete", type = TypesConvert.str2bool, default = True)
    VTFargparse.add_argument("--delOldRwrFiles", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--setEventConfig", type = str, default = False)
    VTFargparse.add_argument("--setFilterLevel", type = int, default = 1)
    VTFargparse.add_argument("--queryExpression", type = str, default = None) # mbOffsetFromStart
    VTFargparse.add_argument("--mbOffsetFromStart", type = int, default = -1)
    VTFargparse.add_argument("--mbOffsetFromEnd", type = int, default = 10000)
    VTFargparse.add_argument("--mbCount", type = int, default = 10000)

    VTFargparse.add_argument("--rwrJsonFileName", type = str, default = 'xplorer-cli-session-informer-filtered-rwr.json')

    # ########################## DPDM Cmdline args ###########################
    VTFargparse.add_argument("--enableDPDMforSED", type = TypesConvert.str2bool, default = False) #Enable Full Page EPWR





    # ############# FW Trace Arguments #############
    VTFargparse.add_argument("--enableFWTrace", type = str, default = False)

    '''
xPlorerPath = "d:\\\\xtools\\app\\\\xplorer"
rwrFilePathDir = "d:\\\\xtools\\user-storage\\\\rwr"
values4HermesXplorerJSON = [{"remoteAddress":'127.0.0.1'}, {"remotePort":8081}, {"informerSerialNumber":'000000'}, {"product":'Hermes'}, {"atbMode":'20E'}, {"calibrationEnabled":'false'}, {"rwrPath":'rwrPath'}, {"rwrMaxFileSize":100}, {"rwrMaxFileCount":20}, {"dcoPath":'dcoPath'}, {"type":'Gen2'}]
                           [{'remoteAddress': '127.0.0.1'}, {'remotePort': 8081}, {'informerSerialNumber': '000000'}, {'product': 'Hermes'}, {'atbMode': '20E'}, {'calibrationEnabled': 'false'}, {'rwrPath': 'rwrPath'}, {'rwrMaxFileSize': 100}, {'rwrMaxFileCount': 20}, {'dcoPath': 'dcoPath'}, {'type': 'Gen2'}]
'''

    # ############# FFU Test arguments #############
    VTFargparse.add_argument("--firmwareSlot", type = int, default = None)
    VTFargparse.add_argument("--commitAction", type = int, default = None)
    VTFargparse.add_argument("--currentFWVersion", type = str, default = None)
    VTFargparse.add_argument("--updateToFWVersion", type = str, default = None)
    VTFargparse.add_argument("--flufFileName", type = str, default = "CFGenc.fluf")
    VTFargparse.add_argument("--ffuServerPath", type = str, default = None)
    VTFargparse.add_argument("--isSecureFFU", type = TypesConvert.str2bool, default = True)
    VTFargparse.add_argument("--writeReadVerify4FFU", type = TypesConvert.str2bool, default = True)
    VTFargparse.add_argument("--FFUhistory", type = TypesConvert.str2bool, default = True)
    VTFargparse.add_argument("--doFFU", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--skipFWVersion",type = str, default = None)
    VTFargparse.add_argument("--enablesdrlog", type=TypesConvert.str2bool, default = False)

    # ############# Security Test argument --resetType #############
    VTFargparse.add_argument("--resetType", type = str, default = None)    #Also used for FFU
    VTFargparse.add_argument("--TCGActivate", type = TypesConvert.str2bool, default = False)
    #VTFargparse.add_argument("--SecurityProtocol", type = str, default = "PYRITE")
    VTFargparse.add_argument("--SetEncryptionKeyMisuse", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--randomWRByteTable", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--SecurityAuditLog", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--securitywithPMM", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--TCGLogging", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--KeyManager", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--security_usecase", type = str, default = '')
    VTFargparse.add_argument("--Admins", type = parseUserAdmins, default = '')
    VTFargparse.add_argument("--Users", type = parseUserAdmins, default = '')
    VTFargparse.add_argument("--LockingRanges", type = parseUserAdmins, default = '')
    VTFargparse.add_argument("--range_lockvalue", type = str, default = None)
    VTFargparse.add_argument("--securityProtocol", type = str, default = None)
    VTFargparse.add_argument("--RevertatEnd", type = TypesConvert.str2bool, default = True)
    VTFargparse.add_argument("--SecurityTest", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--Activate_ADST", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--NumOfDST", type = str, default = 'one')
    VTFargparse.add_argument("--event_offset", type = int, default = None)
    VTFargparse.add_argument("--RMACorruption", type = str, default = None)
    VTFargparse.add_argument("--PowercycletoLock", type = str, default = None)
    VTFargparse.add_argument("--BigRMAUnlockWith", type = str, default = None)

    # ############# CVD Distribution arguments #############
    VTFargparse.add_argument("--bltype", type = int, default = 0) # 0 for SLC/1 for TLC
    VTFargparse.add_argument("--metablock", type=int, default=0)
    VTFargparse.add_argument("--metadie", type = int, default = 0)
    VTFargparse.add_argument("--fim", type=int, default=0)
    VTFargparse.add_argument("--fmu", type = int, default = 0)
    VTFargparse.add_argument("--wordline", type=int, default=0)
    VTFargparse.add_argument("--string", type = int, default = 0)
    VTFargparse.add_argument("--plane", type = int, default = 0)
    VTFargparse.add_argument("--VBA", type=int, default=0) # VBA(0) or DeVBA(1)
    VTFargparse.add_argument("--isDummyWL", type=int, default=0)
    VTFargparse.add_argument("--page", type=int, default=0)

    VTFargparse.add_argument("--bkopsTest", type = TypesConvert.str2bool, default = False)

    # ############# Get Assert from debugger argument #############
    VTFargparse.add_argument("--getAssert", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--botFilePath", type = str, default = False)

    # ############# MOONSHOT-17932 argument #############
    VTFargparse.add_argument("--CVFInstaller", type = str, default = None)
    VTFargparse.add_argument("--FVTInstaller", type = str, default = None)
    VTFargparse.add_argument("--FwSourcepath", type = str, default = None)
    VTFargparse.add_argument("--BuildDebugDlls", type = str, default = None)

    # ############# Enable or Disbale HMB ###############
    VTFargparse.add_argument("--enableHMB", type = str, default = None)
    VTFargparse.add_argument("--numOfDescriptors", type = int, default = 0)
    VTFargparse.add_argument("--EqDescSize", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--RandDes", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--isContigous", type = int, default = 1)
    VTFargparse.add_argument("--MaxDescriptors", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--HMBSize", type = int, default = 0)
    VTFargparse.add_argument("--MRPHPath", type = str, default = 'sclfilip')


    # ############# get DUI log ###############
    VTFargparse.add_argument("--getDUIlog", type = TypesConvert.str2bool, default = False)

    # ############# For CTD #############
    VTFargparse.add_argument("--testList", type = str, default = None)
    VTFargparse.add_argument('--useCSVFile', type=str, default=None)

    # ############## For AP Model GSD/UGSD ########
    VTFargparse.add_argument("--isIssueGSD", type = bool, default = False)
    VTFargparse.add_argument('--isIssueUGSD', type=bool, default=False)
    VTFargparse.add_argument('--resetFrequencyInModelRun', type=int, default=1000)

    # MRPH USSEROM BIN FILE CORRUPTION
    VTFargparse.add_argument("--WL", type = parseUserAdmins, default = '')
    VTFargparse.add_argument("--Copies", type = parseUserAdmins, default = '')
    VTFargparse.add_argument("--USERROM", type = parseUserAdmins, default = '')
    VTFargparse.add_argument("--CorruptBothUSEROMofWL", type = TypesConvert.str2bool, default = False)

    # ############# D3Hot Based arguments ###############
    VTFargparse.add_argument("--d3HotExitType", type = str, default = None)

    # ############ Enable Pre/Post SMART Check ################
    VTFargparse.add_argument("--enableSMARTCheck", type = TypesConvert.str2bool, default = None)

    # ############ Enable Preconditioning #############
    VTFargparse.add_argument("--Preconditions", type = int, default = 0)
    VTFargparse.add_argument("--SplitSelector", type = int, default = 0)

    # ############ CMDP Ignore Error ###################
    VTFargparse.add_argument('--IgnoreError', type=bool, default=False)

    # ##########For BootCases And FS###########################
    VTFargparse.add_argument('--fileSizeRange', type=list, default=[1,32])
    VTFargparse.add_argument('--maxFileWrites', type=int, default=1000)
    VTFargparse.add_argument('--filesPerCycle', type=int, default=50)

    # ########## SPCB Preconditioning cmdline args ###########################
    VTFargparse.add_argument('--SPCBPreCondition', type = TypesConvert.str2bool, default=False)
    VTFargparse.add_argument("--SPBadBlockPattern", type = str, default = "MAX_BAD_BLOCKS")
    VTFargparse.add_argument("--BadBlockPattern", type = str, default = "MAX_BAD_BLOCKS")

    # ########## Cmdline args mentioned in CTF ValidationSpace ###########################
    VTFargparse.add_argument("--busWidth", type = int, default = None)
    VTFargparse.add_argument("--setFreq", type = int, default = None)
    VTFargparse.add_argument("--badblockrange", type=str2IntRange, default = [300, 400])

    VTFargparse.add_argument("--enableCmdQueue", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--switchCmdQueue", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--fullDataMode", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--iniFile", type = str, default = None)
    VTFargparse.add_argument("--seq", type = TypesConvert.str2bool, default = False)

    # ########## Cmdline args mentioned in SRW ValidationSpace ###########################
    VTFargparse.add_argument("--doSecureRW", type = TypesConvert.str2bool, default = False)

    # ########################### Traces related Cmdline args ###########################
    VTFargparse.add_argument("--enableCRTrace", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--enableFRTrace", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--enableVCDDump", type = TypesConvert.str2bool, default = False)

    VTFargparse.add_argument("--enableZeroPatternTest", type = int, default = 0)
    VTFargparse.add_argument("--doStxRW", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--doScrRW", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--isTwoPassPgm", type = TypesConvert.str2bool, default = True)
    VTFargparse.add_argument("--confPerf", type = int, default = 0)

    # ########################### WFO/CMR related Cmdline args ###########################
    VTFargparse.add_argument("--filesPerCycle", type = int, default = 50)
    VTFargparse.add_argument("--fileSizeRange", type=str2IntRange, default = [1,32])
    VTFargparse.add_argument("--fatOffset", type = int, default = None)
    VTFargparse.add_argument("--verifyImmediateRequired", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--chunkSizeForFileWrite", type = int, default = None)

    # ########################## WL related Cmdline args ###########################
    VTFargparse.add_argument("--writeData",type=int,default=100)

    # ########################## Scaling down Cmdline args ###########################
    VTFargparse.add_argument("--spareBlockCount",type=int,default=20)
    VTFargparse.add_argument("--scaledownEnabled", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--reducecapacityEnabled", type=TypesConvert.str2bool, default = False)

    # ########################## LDPC RR Cmdline args ###########################
    VTFargparse.add_argument("--readretrypath", type = str, default = None) #Defines the path number ex: Path12
    VTFargparse.add_argument("--readretryEIPage", type = str, default = None)
    VTFargparse.add_argument("--RROnRelinkedBlocks", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--RROnClosedBlock", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--ReadRequestOnSameLBA", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--forMSVCDDump", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--RRPathList", type=str2IntList, default = [0,0])
    VTFargparse.add_argument("--eBlockList", type=str2IntList, default = [-1,-1])
    VTFargparse.add_argument("--RRCmdConfig", type=str2IntList, default = RR_CMDPREFIX_CONFIG)
    VTFargparse.add_argument("--GCFragmentList", type=str2IntList, default = [])
    VTFargparse.add_argument("--decodeFailureType", type=int, default = 0) #0 for ALLZERO, 1 for ALLONE
    VTFargparse.add_argument("--paddingCheck", type = TypesConvert.str2bool, default = False) #To check if latch contents get padded before moving to Phase2
    VTFargparse.add_argument("--controlBlockType", type = str, default = "GAT")

    # ########################## EPWR Cmdline args ###########################
    VTFargparse.add_argument("--fullPageEpwr", type = TypesConvert.str2bool, default = False) #Enable Full Page EPWR
    VTFargparse.add_argument("--slowAccEpwr", type = TypesConvert.str2bool, default = False) #Enable Full Page EPWR

    # ########################## TT Cmdline args ###########################
    VTFargparse.add_argument("--tempPollingDie",type = int, default = 0)
    VTFargparse.add_argument("--enableASIC", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--enableNAND", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--enableDelay", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--enableFreqScale", type = TypesConvert.str2bool, default = False)

    # ########################## UM Cmdline args ###########################
    VTFargparse.add_argument("--relinked", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--SeqStreamPattern", type = str, default = None)
    VTFargparse.add_argument("--jumpFrequency", type = str, default = None)
    VTFargparse.add_argument("--jumpType", type = str, default = None)
    VTFargparse.add_argument("--overwriteFrequency", type = str, default = None)
    ###################################################################################################
    ################## Command Line Arguments related Related to closed block #########################
    ###################################################################################################
    #disabling these as these are present only in Folding platform
    #VTFargparse.add_argument("--closeBlockEnable", type = TypesConvert.str2bool, default = False)
    #VTFargparse.add_argument("--closeBlockFreq",type=int,default=300)
    #VTFargparse.add_argument("--closeBlockThreshold",type=int,default=15)
    #VTFargparse.add_argument("--closeBlockException", type = TypesConvert.str2bool, default = False)


    # ########################## DLT Cmdline args ###########################
    VTFargparse.add_argument("--totalnumloops", type=int, default = 10)
    VTFargparse.add_argument("--readloops", type=int, default = 1)
    VTFargparse.add_argument("--writeloops", type=int, default = 1)
    VTFargparse.add_argument("--chunksize", type=int, default = 0x400)
    VTFargparse.add_argument("--ischeckerboardpattern", type = TypesConvert.str2bool, default = True)
    VTFargparse.add_argument("--isreadafterwrite", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--writemaxlbadivider", type=int, default = 0x7f)
    VTFargparse.add_argument("--randomwritesectors", type=int, default = 0xf)
    VTFargparse.add_argument("--randomwritefrequency", type=int, default = 8)
    VTFargparse.add_argument("--delaytime", type=int, default = 20)
    VTFargparse.add_argument("--enablerandrangelimit", type=int, default = 0)
    VTFargparse.add_argument("--userandseedno", type=int, default = 0)
    VTFargparse.add_argument("--randomdltseed", type=int, default = None)
    VTFargparse.add_argument("--randlbarange", type=int, default = None)
    VTFargparse.add_argument("--randlbastart", type=int, default = None)
    VTFargparse.add_argument("--configFilename", type = str, default = None)
    VTFargparse.add_argument("--checkSMARTVendorCmd",type = TypesConvert.str2bool, default = False)

    # ########################## Command Queue related Cmdline args ###########################
    VTFargparse.add_argument("--cqmode", type = str, default = None)
    VTFargparse.add_argument("--cqWrites", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--cqReads", type = TypesConvert.str2bool, default = False)

    VTFargparse.add_argument("--capacity", type = str, default = None)
    VTFargparse.add_argument("--checkZoneBasedBBInjection",type = TypesConvert.str2bool, default = False)

    # ########################## YODA Cmdline args ###########################
    VTFargparse.add_argument("--isLegacy", type = TypesConvert.str2bool, default=True)
    VTFargparse.add_argument("--feature", type = str, default=None)
    VTFargparse.add_argument("--regressionDurationHrs", type = str2Dict, default = None)
    VTFargparse.add_argument("--exitPassPercentage", type = str2Dict, default = None)
    VTFargparse.add_argument("--totalTestsToDeploy", type = int, default = 0)
    VTFargparse.add_argument("--program", type = str, default = None)
    VTFargparse.add_argument("--totalDataWritten", type = setToZero, default = 0.0)

    # ########################## VSC related Cmdline args ###########################
    VTFargparse.add_argument("--pferrorinjection", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--eferrorinjection", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--isPreConditionReqd", type = TypesConvert.str2bool, default = True)
    VTFargparse.add_argument("--vscstoponfailure", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--vscisdynamicfatdetection", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--memorytype", type = str, default = None)
    VTFargparse.add_argument("--vscSpeed", type = int, default = 10)
    VTFargparse.add_argument("--dopowcycle", type = TypesConvert.str2bool, default = True)
    VTFargparse.add_argument("--isrambase", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--randWrDisturbanceBlockSize", type = int, default = 128)
    VTFargparse.add_argument("--projectconfig", type = str, default = None)

    # ########################## Read Scrub Cmdline args ########################
    VTFargparse.add_argument("--rsgcGear", type = str, default = None)
    VTFargparse.add_argument("--doPC", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--cmdtype", type=str, default = "")
    VTFargparse.add_argument("--triggerotherGCs", type = TypesConvert.str2bool, default = False)
    VTFargparse.add_argument("--reduceRSSyndWgt", type = TypesConvert.str2bool, default = False)    

    return VTFargparse


def parseNumList(string):
    m = re.match(r'(\d+)(?:-(\d+))?$', string)
    if not m:
        raise "'"
    start = m.group(1)
    end = m.group(2)
    #return list(range(int(start,10), int(end,10)+1))
    return list((int(start,10), int(end,10)))

def parseUserAdmins(string):
    if string == 'Random' or string == 'ALL':
        return string
    elif string =='':
        return None
    else:
        user_admin_list = [int(''.join(i)) for is_digit, i in groupby(string, str.isdigit) if is_digit]
        if not len(user_admin_list):
            raise "'"
        return user_admin_list

def str2StringList(param):
    StringList = []
    values = param.split(",")
    for val in values:
        StringList.append(val.strip())
    return StringList

def str2IntList(param):
    values = param.split(",")
    IntList = []
    for val in values:
        IntList.append(int(val.strip()))

    return IntList

def str2ListOfRanges(param):
    #Ex: --arg=min1:max1,min2:max2...
    values = param.split(",")
    ListOfRanges = []
    for val in values:
        rangeVals = val.split(":")
        range = []
        for rangeVal in rangeVals:
            range.append(int(rangeVal.strip()))

        ListOfRanges.append(range)
    return ListOfRanges

def str2IntRange(param):
    #Ex: 0x1-0x80 ---> [1,128]
    values = param.split("-")
    RangeList = []
    for val in values:
        val = val.strip()
        if val.isdigit():
            RangeList.append(int(val))
        else:
            RangeList.append(int(val, 0))
    return RangeList

def str2Dict(param):
    """
    Ex: 
    "{cc:12,fc:24,beta:48,rc:72}" ---> {"cc":12,"fc":24,"beta":48,"rc":72}
    "{apNonEi:80,apEi:75,ftLegacyNonEi:90,ftLegacyEi:85,ftNewNonEi:75,ftNewEi:85} ---> 
    {"apNonEi":80,"apEi":75,"ftLegacyNonEi":90,"ftLegacyEi":85,"ftNewNonEi":75,"ftNewEi":85}"
    """
    key_val_pairs = re.findall(r'\w+\:[\[\],\d]+\]', param) if re.findall(r'\w+\:[\[\],\d]+\]', param) else param[1:-1].split(",")
    key_val_pairs = [re.sub(r'\s+', '', c) for c in key_val_pairs]
    out_dict = {}
    for key_val_pair in key_val_pairs:
        out_dict[key_val_pair.split(":")[0]] = key_val_pair.split(":")[1]
    return out_dict
def setToZero(param):
    return 0.0