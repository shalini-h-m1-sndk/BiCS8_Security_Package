"""
class Utils
Contains all the Utility functions
@ Author: Shaheed Nehal A
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
    from builtins import hex
    pass # from builtins import str
    from builtins import range
    pass # from builtins import *
    from builtins import object
from past.utils import old_div
import random, subprocess, threading, math, shutil, os, sys, socket, json, time, urllib.request, urllib.error, urllib.parse
import Core.ValidationError as TestError
import FileData as FileData
import Core.ValidationError as ValidationError
import Constants
#import SDDVT.Extensions.CVFImports as pyWrap
import Extensions.CVFImports as pyWrap
from datetime import datetime
import CTFServiceWrapper as ServiceWrap
import SDCommandWrapper as SDWrap
#import ValidationRwcManager
import DiagnosticLib as DiagLib
#import FwConfig as FwConfig
import ValidationSpace
from os import walk, path, getcwd

# ############### Porting from CTF ############### #
g_sectorsperLG  = -1
g_bcThreshold = -1

#global
RESET_TIMEOUT=None
WRITE_TIMEOUT=None
READ_TIMEOUT=None
VOLTAGE=None
MAX_RANDOM_SEED = 0xFFFFFFFF

NUM_BOOT_BLOCK_SPARROW = 2
DEDICATED_FBL_SPARROW = 2
GC_CONTEXT_BLOCK_SPARROW = 1 #* NP
NUM_RO_FILE_SPARROW = 2
NUM_RW_FILE_SPARROW = 2
SLC_COMPACTION_BLOCK_SPARROW = 1 #* NP
NUM_SAFE_ZONE_BLOCK_SPARROW = 1
NUM_MLC_COMPACTION_BLOCK_SPARROW = 1
MAX_COMPATCION_SLOTS_SPARROW = 5
MAX_COLD_BLOCK_SPARROW = 6
FILE_42_SPEEDCLASS_OFFSET = 0x140

#Global variable for Flatten function
g_FlattenList = []

#global pointer to keept track of the next error log event dump
g_FlushStartPtrFound={"block":0,"WL":0,"eccpage":0}
#Global variable to set power cycle
g_PowerCycleState = False
g_eiEnabledAfterPowerCycle = 5

REINIT_ON_READONLY_MODE = True
#Fake open ended read test case uses this global variables
g_MaxReadCommands=None
g_MaxDataLength  =None

g_openEndedWriteRead = False

availableSpeedModes = ["SDR12", "SDR25", "SDR50", "SDR104", "DDR50","DDR200" , "LS" , "HS"] #Equal weightage to all modes #To recheck: DDR to be added
availableSdConfigurations = ["SDR12", "SDR25", "SDR50", "SDR104", "DDR50","DDR200" , "HS"]
g_factoryMarkedBadBlockList = []

#This global flag is to differentiate DW and NDW product.
#Its value is set in TestRunner.py
PRODUCT_TYPE = None

g_validSlcMetaBlockNumbers = None
g_validMlcMetaBlockNumbers = None
g_waypointRegistered = False

g_blindFoldEnabled = True

numberOfDiesInTheCard = 0 #This value is set in TestRunner.py file

#These variables are used in TestRunner and PreconditionBlocksUtils files to
#Track error injected & error occurred
g_errorOccurredList = []
g_errorInjectedList = []

#This variable is used in ValidationRWCLib.
#This variable is used to track and avoid multiple WA callbacks
g_detectFirstWA_callback  = True

enableCmdQueue = False
switchCmdQueue = False

#Add new configurable SDW WL shift values to the below list
ConfigPaddedWLs = [0, 8]

def importModules(moduleList):
    for module in moduleList:
        try:
            __import__(module)
        except ImportError:
            excCmd = 'python ' + os.path.dirname(sys.executable) + '\Scripts\pip.exe install http://artifactory.wdc.com/artifactory/fvt-release-global/{0}.zip'.format(module)
            os.system(excCmd)
            __import__(module)

    # To install pip and openpyxl packages to use Excel file
    FVTPath = os.environ["TESTS_ROOT_DIR"]
    getPipPath = '"' + FVTPath + r'\Tools\get-pip.py' + '"'
    try:
        urllib.request.urlopen("http://pypi.python.org")
        os.system("python " + getPipPath)
    except urllib.error.URLError:
        print("Cannot connect to pypi.python.org, will install from artifactory.")



def FlushCache(vtfContainer):
    """
    Description:
       * Flushes the cache before power cycle
    """
    from SdCommands import SdCommandLib as SDCommandLib
    SDCmdLib= SDCommandLib.SdCommandClass(vtfContainer)

    logger = vtfContainer.GetLogger()

    databuf = pyWrap.Buffer.CreateBuffer( 1 )
    logger.Info("", "Trying to flush the cache by issuing CMD 48")
    SDCmdLib.Cmd48(  ExtnFunNum = 2, DataBuff = databuf , Address = 0x00, MIO = 0, Length = 511 )
    InsertDelay( 1, vtfContainer )


def PowerCycle(vtfContainer, waitTime = None, resetSmartTrace = True, resetSDRMode = True, randomObj = None, verifyMDllLock=False):
    """
    Name:                       PowerCycle
    Description:                Powercycling the card

    Arguments:
       vtfContainer:               Card vtfContainer object
       waitTime                 wait time before which the device is expected to respond after the power up

    Returns:
       None
    """
    import CTFServiceWrapper as serviceWrap
    #import ValidationSpace
    import ValidationRwcManager
    import SDDVT.Common.SDCommandLib as SdCommandLib
    global enableCmdQueue, RESET_TIMEOUT, WRITE_TIMEOUT, READ_TIMEOUT

    RESET_TIMEOUT = int(vtfContainer.cmd_line_args.init_timeout) if RESET_TIMEOUT is None else RESET_TIMEOUT
    WRITE_TIMEOUT = int(vtfContainer.cmd_line_args.write_timeout) if WRITE_TIMEOUT is None else WRITE_TIMEOUT
    READ_TIMEOUT = int(vtfContainer.cmd_line_args.read_timeout) if READ_TIMEOUT is None else READ_TIMEOUT

    logger = vtfContainer.GetLogger()
    #validationSpace = ValidationSpace.ValidationSpace()
    optionValues = vtfContainer.cmd_line_args
    if randomObj == None:
        randomObj =  random.Random(vtfContainer.cmd_line_args.randomSeed)

    #To recheck - CQ
    #if enableCmdQueue == True:
        #FlushCache(vtfContainer)

    logger.Debug("" , '[PowerCycle] entering ')
    SetAndResetPowerCycleState(SetPCFlag=True) #This function used to set the powercyclestate to True after every powercycle

    logger.Warning("" , '[PowerCycle] Doing Power cycle... ')
    #status = adapter.PowerCycle()
    status = None
    try:
        if vtfContainer.isModel:
            ValidationRwcManager.g_lastcmdIssued = "PC"
            modelParams, SDParams= PowercycleCVFargs()
            PowerCycleobj= serviceWrap.PowerCycle(shutdownType = serviceWrap.GRACEFUL, pModelPowerParamsObj = modelParams, protocolParams = SDParams , sendType=serviceWrap.SEND_IMMEDIATE)
            #To recheck: No status returned in CVF
            #status = power.Cycle(0)
        else:
            SDWrap.SDRPowerCycle()
            #status = power.Cycle (waitTime)
    except ValidationError.CVFExceptionTypes as ex:
        ex = ex.CTFExcObj if hasattr(ex, "CTFExcObj") else ex
        logger.Info("", "Powercycle failed - %s"%ex.GetFailureDescription())
        raise ValidationError.CVFGenericExceptions(vtfContainer.GetTestName(), "Powercycle failed")
    except Exception as exc:
        logger.Info("", "Powercycle failed - %s"%exc)
        raise ValidationError.TestFailError(vtfContainer.GetTestName(), "Powercycle failed")
    
    ValidationRwcManager.g_lastcmdIssued = "PC"
    #Setting timeout
    SetTimeOut(vtfContainer,RESET_TIMEOUT,WRITE_TIMEOUT,READ_TIMEOUT)

    if resetSDRMode:
        if vtfContainer.activeProtocol=="SD" :
            if not vtfContainer.isModel :

                sdCmdobj = SdCommandLib.SdCommandClass(vtfContainer)
                sdCmdobj.DoBasicInit()
            else:
                #Do SDR switch only if this flag (doSDRSwitchDuringPC) is set
                if vtfContainer.cmd_line_args.doSDRSwitchDuringPC:
                    SetSDRMode(vtfContainer, randSDR=True, randomobj=randomObj)
                #Reset the SDRMode to --sdrMode
                else:
                    SetSDRMode(vtfContainer, vtfContainer.cmd_line_args.sdrMode, randomobj=randomObj)
                SetHostTurnAroundTime(vtfContainer, 0)

    logger.Debug("" , '[PowerCycle] exiting ')

    if vtfContainer.cmd_line_args.verifyManualLock == True:
        verifyMDllLock = True

    if verifyMDllLock:
        import FileData as FileData

        InsertDelay(randomObj.randint(5, 10), vtfContainer)

        sdrMode = vtfContainer.cmd_line_args.sdConfiguration
        file23Obj = FileData.ConfigurationFile23Data(vtfContainer)
        if vtfContainer.cmd_line_args.sdConfiguration == 'LS' or vtfContainer.cmd_line_args.sdConfiguration == 'SDR12':
            expectTapCount = file23Obj.lstapcount
            manualLockEnable = file23Obj.lsManualLockEnable
        elif vtfContainer.cmd_line_args.sdConfiguration == 'HS' or vtfContainer.cmd_line_args.sdConfiguration == 'SDR25':
            expectTapCount = file23Obj.hstapcount
            manualLockEnable = file23Obj.hsManualLockEnable
        elif vtfContainer.cmd_line_args.sdConfiguration == 'SDR50':
            expectTapCount = file23Obj.sdr50tapcount
            manualLockEnable = file23Obj.sdr50ManualLockEnable
        elif vtfContainer.cmd_line_args.sdConfiguration == 'SDR104':
            expectTapCount = file23Obj.sdr104tapcount
            manualLockEnable = file23Obj.sdr104ManualLockEnable
        elif vtfContainer.cmd_line_args.sdConfiguration == 'DDR50':
            expectTapCount = file23Obj.ddr50tapcount
            manualLockEnable = file23Obj.ddr50ManualLockEnable
        elif vtfContainer.cmd_line_args.sdConfiguration == 'DDR200':
            expectTapCount = file23Obj.ddr200tapcount
            manualLockEnable = file23Obj.ddr200ManualLockEnable
        else:
            manualLockEnable = False

        if manualLockEnable:
            FIM_MDLL_CTRL_REG = 0x080003010
            FIM_PHY_DLL_TAP_COUNT_BITS = 9
            dataBuf = DiagLib.ReadSFR(vtfContainer, FIM_MDLL_CTRL_REG, 4)
            registerValue = dataBuf.GetFourBytesToInt(0)
            mask = (1 << FIM_PHY_DLL_TAP_COUNT_BITS) - 1
            tapCount = registerValue & mask

            if expectTapCount == tapCount:
                logger.Debug("", "MDLL lock Tapcount is matching - 0x%x" % tapCount)
            else:
                raise TestError.TestFailError("", "MDLL Lock tapcount - 0x%x not matching expected value[FILE23] - 0x%x" % (tapCount, expectTapCount))


    if vtfContainer.cmd_line_args.GCBalancing :
        import ValidationRwcManager
        import GCBalancingUtils
        if ValidationRwcManager.TOTAL_DATA_WRITTEN  :
            validationSpace    = ValidationSpace.ValidationSpace(vtfContainer)
            FwConfigData       = validationSpace.GetFWConfigData()
            GCBalUtils         = GCBalancingUtils.GCBalancingUtils(vtfContainer, FwConfigData )
            randomObj          =  random.Random(vtfContainer.cmd_line_args.randomSeed)
            GCBalUtils.UpdateGCBalancingThresholds(GCBalancingUtils.BALANCED_GC_THRESHOLD)
    SetAndResetPowerCycleState(ResetPCFlag=True)
    return
    #To recheck: CQ
    #if enableCmdQueue == True:
        #EnableCommandQueue(vtfContainer)
#End of PowerCycle()

def GetPowerCycleState():
    return g_PowerCycleState
#End of GetPowerCycleState

def PowercycleCVFargs():
    import CTFServiceWrapper as serviceWrap

    #Model Power parameters
    modelPowerParamsObj = serviceWrap.MODEL_POWER_PARAMS()
    modelPowerParamsObj.railID = 0
    modelPowerParamsObj.delayTimeInNanaSec = 0
    modelPowerParamsObj.transitionTimeInNanoSec = 0

    #SD Protocol parameters
    sdPowerCycleParam = serviceWrap.SD_POWER_CYCLE_PARAMS()
    sdPowerCycleParam.bIsEnablePowerSustenance = True
    sdPowerCycleParam.bIsEnableCache = False
    sdPowerCycleParam.bIsEnableCardInitiatedSelfMaintenance = False
    sdPowerCycleParam.bIsEnableHostInitiatedMaintenance = False
    sdPowerCycleParam.bIsDisablePowerManagementFunction = True
    sdPowerCycleParam.sdShutdownType = 0

    sdProtocolParam = serviceWrap.PROTOCOL_SPECIFIC_PARAMS()
    sdProtocolParam.paramType = serviceWrap.SD_POWER_CYCLE
    sdProtocolParam.sdParams = sdPowerCycleParam

    return modelPowerParamsObj, sdProtocolParam


def SetAndResetPowerCycleState(SetPCFlag=False, ResetPCFlag=False):
    """
    This function sets the powercyclestate to TRUE after every powercycle
    By setting the powercyclestate to TRUE we can avoid error injection immediately after powercycle
    after avoiding the error injection we reset the powercyclestate to False
    """
    global g_PowerCycleState
    global g_eiEnabledAfterPowerCycle
    if g_PowerCycleState == False and SetPCFlag == True:
        g_PowerCycleState = True
        g_eiEnabledAfterPowerCycle = 5
    elif g_PowerCycleState == True and ResetPCFlag == True:
        g_PowerCycleState = False
#End of SetPowerCycleState




def EIEnablerAfterPowerCycle():
    """
    Immediately after power cyle do not inject any error or don't send any diagnostic until the completion of post init
    """
    global g_eiEnabledAfterPowerCycle
    if g_eiEnabledAfterPowerCycle != 0:
        g_eiEnabledAfterPowerCycle = g_eiEnabledAfterPowerCycle - 1 #Inject error when g_eiEnabledAfterPowerCycle is 0 and reset it to 5 after power cycle

    return g_eiEnabledAfterPowerCycle


def SetTimeOut(vtfContainer,otherTimeout = None,
               writeTimeout = None,
               readTimeout = None):
    """
    Name:          SetTimeOut()
    Description:   Set the reset,write and read timeout values
    Arguments:
       vtfContainer      Card Test Space
       otherTimeout   The reset timeout(hard)
       writeTimeout   The write timeout(hard)
       readTimeout    The read timeout(hard)
    Returns:       None
    """

    #othertimeout is resettimeout
    #busytimeout is writetimeout
    vtfContainer.GetLogger().Info("" , "[Utils] Setting timeouts for ResetTimeout:%d writeTimeout:%d readTimeout%d"%(otherTimeout,writeTimeout,readTimeout))
    if otherTimeout is not None and writeTimeout is not None and readTimeout is not None:
        SDWrap.CardSetTimeout(otherTimeout,writeTimeout,readTimeout)

# End of SetTimeOut
def SetBusFrequencyDDR(vtfContainer,clk_freq_in_Mhz):
    logger = vtfContainer.GetLogger()
    logger.Info("", "-"*60)
    clk_freq = clk_freq_in_Mhz * 1000 * 1000
    clk_period_ns = old_div(1000,clk_freq_in_Mhz)

    #due to 4 data lines we need two clock cycles
    byte_time = clk_period_ns
    logger.Info("",  "byte time for clk_freq = %d MHz is %6.2f ns "%(clk_freq_in_Mhz,byte_time))

    vtfContainer._livet.GetRootObject().SetVariable( "host.ProtocolDataByteWriteTransfer", str( byte_time ) )
    vtfContainer._livet.GetRootObject().SetVariable( "host.ProtocolDataByteReadTransfer", str( byte_time ) )

    sector_time = byte_time * 512
    vtfContainer._livet.GetRootObject().SetVariable( "host.WriteSectorTransfer", str( sector_time ) )
    vtfContainer._livet.GetRootObject().SetVariable( "host.ReadSectorTransfer", str( sector_time ) )

    #every command has 48-bits i.e. 6 bytes i.e. cmd time will be 6 times byte time


    cmd_time = byte_time * 6
    #self.Model.GetRootObject().SetVariable( "host.ProtocolCmdByteTransfer", str( cmd_time ) )
    vtfContainer._livet.GetRootObject().SetVariable( "host.WriteCommandTransfer", str( cmd_time ) )
    vtfContainer._livet.GetRootObject().SetVariable( "host.ReadCommandTransfer", str( cmd_time ) )

    #adding overhead of startbit stop bit and crc of 2 bytes
    start_bit_time = float(old_div(byte_time,8))
    stop_bit_time = float(old_div(byte_time,8))
    crc_time = byte_time*2
    total_overhead = float(start_bit_time + stop_bit_time) + float(crc_time)

    import math as maths
    total_sector_overhead = int(maths.ceil(total_overhead))

    vtfContainer._livet.GetRootObject().SetVariable( "host.ProtocolWriteDataTransferOverhead", str( total_sector_overhead ) )
    vtfContainer._livet.GetRootObject().SetVariable( "host.ProtocolReadDataTransferOverhead", str( total_sector_overhead ) )
    SdHim = vtfContainer._livet.GetController().GetSubObject( "SD_HIM" )
    SdHim.ExecuteCommand( "set_bus_frequency", [int(clk_freq)] )
    logger.Info("", "-"*60)
    return
#end of setBusFrequencyDDR

#set bus frequency on model
def SetBusFrequency(vtfContainer,clk_freq_in_Mhz):
    logger = vtfContainer.GetLogger()
    logger.Info("", "-"*60)
    clk_freq = clk_freq_in_Mhz * 1000 * 1000
    clk_period_ns = old_div(1000,clk_freq_in_Mhz)

    #due to 4 data lines we need two clock cycles
    byte_time = clk_period_ns * 2
    logger.Info("",  "byte time for clk_freq = %d MHz is %6.2f ns "%(clk_freq_in_Mhz,byte_time))

    vtfContainer._livet.GetRootObject().SetVariable( "host.ProtocolDataByteWriteTransfer", str( byte_time ) )
    vtfContainer._livet.GetRootObject().SetVariable( "host.ProtocolDataByteReadTransfer", str( byte_time ) )

    sector_time = byte_time * 512
    vtfContainer._livet.GetRootObject().SetVariable( "host.WriteSectorTransfer", str( sector_time ) )
    vtfContainer._livet.GetRootObject().SetVariable( "host.ReadSectorTransfer", str( sector_time ) )

    #every command has 48-bits i.e. 6 bytes i.e. cmd time will be 6 times byte time


    cmd_time = byte_time * 6
    #self.Model.GetRootObject().SetVariable( "host.ProtocolCmdByteTransfer", str( cmd_time ) )
    vtfContainer._livet.GetRootObject().SetVariable( "host.WriteCommandTransfer", str( cmd_time ) )
    vtfContainer._livet.GetRootObject().SetVariable( "host.ReadCommandTransfer", str( cmd_time ) )

    #adding overhead of startbit stop bit and crc of 2 bytes
    start_bit_time = float(old_div(byte_time,8))
    stop_bit_time = float(old_div(byte_time,8))
    crc_time = byte_time*2
    total_overhead = float(start_bit_time + stop_bit_time) + float(crc_time)

    import math as maths
    total_sector_overhead = int(maths.ceil(total_overhead))

    vtfContainer._livet.GetRootObject().SetVariable( "host.ProtocolWriteDataTransferOverhead", str( total_sector_overhead ) )
    vtfContainer._livet.GetRootObject().SetVariable( "host.ProtocolReadDataTransferOverhead", str( total_sector_overhead ) )
    SdHim = vtfContainer._livet.GetController().GetSubObject( "SD_HIM" )
    SdHim.ExecuteCommand( "set_bus_frequency", [int(clk_freq)] )
    logger.Info("", "-"*60)
    return
#end of setBusFrequency

def SetBusWidth(vtfContainer,busWidth):
    """
    Name:          SetBusWidth()
    Description:   Set the buswidth
    Arguments:
       vtfContainer      Card Test Space
       busWidth       bus width that has to be set,either 1,4 or 8
    Returns:       None
    """

    logger=vtfContainer.GetLogger()
    try:
        #To recheck: MS Cards??
        #if card.IsMs(): #for MS cards
            #import py_sfcl
            #if busWidth==1:
                #oprnMode=py_sfcl.OPERATION_MODE.SERIAL_IF_MODE
            #elif busWidth==4:
                #oprnMode=py_sfcl.OPERATION_MODE.PARALLEL_4BIT_IF_MODE
            #elif busWidth==8:
                #oprnMode=py_sfcl.OPERATION_MODE.PARALLEL_8BIT_IF_MODE
            #else:
                #logger.Critical("","Invalid bus width given=%s.So not able to set the bus width"%busWidth)
                #raise TestError.TestFailError("","[SetBusWidth] failed to set bus width")

            #vtfContainer.GetAdapter().SetOperationMode(oprnMode)
        #else:#for other than MS cards
        SDWrap.SetBusWidth(busWidth)
    except:
        logger.Critical("","[SetBusWidth] failed to set bus width")
        raise TestError.TestFailError("","[SetBusWidth] failed to set bus width")
    return
#end of SetBusWidth


def SetSDRMode(vtfContainer, sdrMode=None, randSDR=False, randomobj=None):
    """
    Name:          SetSDRMode()
    Description:   For model tests:
                       1. If --sdrMode is provided in cmdline, then this function will set the SDR mode to whatever has been provided
                       2. If --sdrMode is not provided, then the default cmdline arg value will be chosen (SDR12 currently - can be updated in CmdLineArgs.py)
                       3. If the test is an AP test, then regardless of --sdrMode, this function will always randomly set the SDR mode
                       4. If randSDR flag is set, then also random SDR mode switching will happen
                   For HW tests:
                       To be defined
    """
    import SDDVT.Common.SDCommandLib  as SdCommandModel
    global availableSpeedModes, availableSdConfigurations
    logger =  vtfContainer.GetLogger()

    if sdrMode == None:
        randSDR = True

    if randSDR:
        if randomobj == None:
            raise TestError.TestFailError(vtfContainer.GetTestName(), "randomObj was not passed as an arg to SetSDRMode()")

        randomobj.shuffle(availableSpeedModes)
        sdrMode               = randomobj.choice(availableSpeedModes) #"SDR" + str(sdrModeParseValue)
    if sdrMode == "LS":
        #Default SDR mode , No change required
        return
    elif sdrMode == "HS":
        sdrMode_string = "SDR25"
    else:
        sdrMode_string = sdrMode

    splitStr= 'SDR'
    if 'DDR' in sdrMode:
        splitStr= 'DDR'

    sdrModeParseValue = int(sdrMode_string.split(splitStr)[1])
    sdrModeValue = sdrModeParseValue * 2 # Frequency multiplicated by 2

    if sdrModeValue == 24:
        sdrModeValue = sdrModeValue + 1

    if (vtfContainer.isModel):
        try:
            sdlivetObj    = SdCommandModel.SDProtocolCommands(vtfContainer)
            if sdrMode == "HS":
                sdlivetObj.InitToState(target_state=4, Issue_CMD11 = False)
            else:
                sdlivetObj.InitToState(target_state=4)

            logger.Info("", "-"*60)
            logger.Info("", "[UTILS] Switching to %s MODE"%sdrMode)

            if sdrMode == "SDR12" :
                byte_time = 80 #in nanosec
            elif sdrMode in ["SDR25" , "HS"]:
                byte_time = 40 #in nanosec
            elif sdrMode == "SDR50" or sdrMode == "DDR50":
                byte_time = 20 #in nanosec
            elif sdrMode == "SDR104" or sdrMode == "DDR200" :
                byte_time = 10 #in nanosec

            import SDDVT.Common.SDCommandLib as SDCommandLib
            sdLibObj= SDCommandLib.SDProtocolCommands(vtfContainer)
            if sdrMode == 'DDR200':
                cmdSystem = "RESERVED"
                arg = sdLibObj.SwitchCmd(operationalMode="SWITCH", accessMode=sdrMode, commandSystem= cmdSystem)
            else:
                arg = sdLibObj.SwitchCmd(operationalMode="SWITCH", accessMode=sdrMode_string)
            sdLibObj.CMD6(arg)


            clk_period = float(old_div(byte_time,2))
            clk_freq = old_div(1.0E+9, clk_period)

            logger.Info("",  "clk freq calculated for mode = %s is %d MHz"%(sdrMode,old_div(clk_freq,(1000*1000))) )

            vtfContainer._livet.GetRootObject().SetVariable( "host.ProtocolDataByteWriteTransfer", str( byte_time ) )
            vtfContainer._livet.GetRootObject().SetVariable( "host.ProtocolDataByteReadTransfer", str( byte_time ) )
            if splitStr == 'SDR':
                sector_time = byte_time * 512
            else:
                sector_time = (old_div(byte_time,2)) * 512
            vtfContainer._livet.GetRootObject().SetVariable( "host.WriteSectorTransfer", str( sector_time ) )
            vtfContainer._livet.GetRootObject().SetVariable( "host.ReadSectorTransfer", str( sector_time ) )

            #every command has 48-bits i.e. 6 bytes i.e. cmd time will be 6 times byte time
            cmd_time = byte_time * 6

            #self.Model.GetRootObject().SetVariable( "host.ProtocolCmdByteTransfer", str( cmd_time ) )
            vtfContainer._livet.GetRootObject().SetVariable( "host.WriteCommandTransfer", str( cmd_time ) )
            vtfContainer._livet.GetRootObject().SetVariable( "host.ReadCommandTransfer", str( cmd_time ) )

            #adding overhead of startbit stop bit and crc of 2 bytes
            start_bit_time = float(old_div(byte_time,8))
            stop_bit_time = float(old_div(byte_time,8))
            crc_time = byte_time*2
            total_overhead = float(start_bit_time + stop_bit_time) + float(crc_time)

            import math as maths
            total_sector_overhead = int(maths.ceil(total_overhead))

            vtfContainer._livet.GetRootObject().SetVariable( "host.ProtocolWriteDataTransferOverhead", str( total_sector_overhead ) )
            vtfContainer._livet.GetRootObject().SetVariable( "host.ProtocolReadDataTransferOverhead", str( total_sector_overhead ) )
            SdHim = vtfContainer._livet.GetController().GetSubObject("SD_HIM")
            SdHim.ExecuteCommand("set_bus_frequency", [int(clk_freq)] )
            sdLibObj.RCA=0xd555
            sdLibObj.CMD13()
        except Exception as exc:
            logger.Info("", "[UTILS] : SDR Switch to %s Mode Failed. \n %s"%(sdrMode, exc))
            raise ValidationError.TestFailError("", "[UTILS] : SDR Switch to %s Mode Failed.  %s"%(sdrMode, exc))
        #CMD6


        logger.Info("", "-"*60)
# End of SetSDRMode fun

def SetDDRMode(vtfContainer,ddrMode,randDDR = False,randomobj=None):
    """
       Name:          SetSDRMode()
       Description:   To Set one of the SDR mode given in the command line option SDR mode - 12,25,50,104
       Arguments:
          vtfContainer      Card Test Space
       Returns:       None
       """

    logger =  vtfContainer.GetLogger()
    if randDDR:
        ddrModeParseValueList = [12,25,50,104]
        ddrModeIndex          = randomobj.randint(0,3)
        ddrModeParseValue     = sdrModeParseValueList[sdrModeIndex]
        ddrModeValue          = sdrModeParseValue
    else:
        ddrModeParseValue = int(ddrMode.split('DDR')[1])
        ddrModeValue = ddrModeParseValue

    if (vtfContainer.isModel):
        #adapter.SetHostFrequency(ddrModeValue * 1000000)
        #logger.Info("", "-"*60)
        #logger.Info("", "DDR Mode is set to DDR_%d "%(ddrModeParseValue))
        #logger.Info("", "Frequency is set to %d MHz"%(ddrModeValue))
        #sectorTransferTimeNs = ( (512*1000 *1000000) / (ddrModeValue*1000000) )
        #logger.Info("", "Read/Write SectorTransfer is set to %d ns"%(sectorTransferTimeNs))
        #vtfContainer._livet.GetRootObject().SetVariable ("host.WriteSectorTransfer", str (sectorTransferTimeNs))
        #vtfContainer._livet.GetRootObject().SetVariable ("host.ReadSectorTransfer", str (sectorTransferTimeNs))
        #vtfContainer._livet.GetRootObject().SetVariable('host.erase_timeout', '250ms')
        #logger.Info("", "-"*60)
        logger.Info("", "-"*60)
        logger.Info("", "DDR Mode is set to DDR_%d "%(ddrModeParseValue))
        logger.Info("", "Frequency is set to %d MHz"%(ddrModeValue))

        if ddrModeValue == 12:
            byte_time = 80 #in nanosec
        elif ddrModeValue == 25 :
            byte_time = 40 #in nanosec
        elif ddrModeValue == 50 :
            byte_time = 20 #in nanosec
        elif ddrModeValue == 104 :
            byte_time = 10 #in nanosec

        #FOR DDR MODES byte time is half of time required for SDR mode
        byte_time = old_div(byte_time, 2)

        clk_freq = ddrModeValue * 1000 * 1000
        logger.Info("",  "clk freq calculated for mode = %s is %d MHz"%(ddrMode,old_div(clk_freq,(1000*1000))) )

        vtfContainer._livet.GetRootObject().SetVariable( "host.ProtocolDataByteWriteTransfer", str( byte_time ) )
        vtfContainer._livet.GetRootObject().SetVariable( "host.ProtocolDataByteReadTransfer", str( byte_time ) )

        sector_time = byte_time * 512
        vtfContainer._livet.GetRootObject().SetVariable( "host.WriteSectorTransfer", str( sector_time ) )
        vtfContainer._livet.GetRootObject().SetVariable( "host.ReadSectorTransfer", str( sector_time ) )

        #every command has 48-bits i.e. 6 bytes i.e. cmd time will be 6 times byte time


        cmd_time = byte_time * 6
        #self.Model.GetRootObject().SetVariable( "host.ProtocolCmdByteTransfer", str( cmd_time ) )
        vtfContainer._livet.GetRootObject().SetVariable( "host.WriteCommandTransfer", str( cmd_time ) )
        vtfContainer._livet.GetRootObject().SetVariable( "host.ReadCommandTransfer", str( cmd_time ) )

        #adding overhead of startbit stop bit and crc of 2 bytes
        start_bit_time = float(old_div(byte_time,8))
        stop_bit_time = float(old_div(byte_time,8))
        crc_time = byte_time*2
        total_overhead = float(start_bit_time + stop_bit_time) + float(crc_time)

        import math as maths
        total_sector_overhead = int(maths.ceil(total_overhead))

        vtfContainer._livet.GetRootObject().SetVariable( "host.ProtocolWriteDataTransferOverhead", str( total_sector_overhead ) )
        vtfContainer._livet.GetRootObject().SetVariable( "host.ProtocolReadDataTransferOverhead", str( total_sector_overhead ) )
        SdHim = vtfContainer._livet.GetController().GetSubObject( "SD_HIM" )
        SdHim.ExecuteCommand( "set_bus_frequency", [int(clk_freq)] )

        logger.Info("", "-"*60)
    # End of SetTimeOut



def SetHostTurnAroundTime(vtfContainer, HTAT_Value, randHTAT=False, randomobj=None):
    """
    Name:          SetHostTurnAroundTime()
    Description:   To Set HTAT Value for model.
    Arguments:
       vtfContainer :     Card Test Space
    Returns:       None
    """

    logger =  vtfContainer.GetLogger()
    if (vtfContainer.isModel):
        #Random HTAT Value setting
        if randHTAT:
            randHTATList = [0,10000,100000, randomobj.randint(1,1000000)]
            HTAT_Index   = randomobj.randint(0,3)
            HTAT_Value   = randHTATList[HTAT_Index]

        #Host Turn Around Time Set to 0microSec for Read and write by defalut if the cmd option is not set to randHTAT=true
        logger.Info("", "-"*60)
        logger.Info("", "HTAT Value for Write is set to %d microSec"%(HTAT_Value))
        vtfContainer._livet.GetLogicalHost().SetVariable("WriteCommandOverhead", str(HTAT_Value))
        logger.Info("", "HTAT Value for Read is set to %d microSec"%(HTAT_Value))
        vtfContainer._livet.GetLogicalHost().SetVariable("ReadCommandOverhead", str(HTAT_Value))
        logger.Info("", "-"*60)
# End of SetTimeOut

def SetVoltage(vtfContainer,voltage = VOLTAGE):
    """
    Name:          SetVoltage()
    Description:   Set the voltage
    Arguments:
       vtfContainer      Card Test Space
       voltage        voltage volues
    Returns:       None
    """

    logger = vtfContainer.GetLogger()

    try:
        #To recheck -- TO be continued
        ##No CVF API where we can pass only volt , Need to pass the structure
        #SDWrap.SDRSetVolt(voltStruct,pStatusReg, bVddfValue)

        ##power.SetVdd(voltage)
        #change the global value of voltage also
        global VOLTAGE
        VOLTAGE  = voltage
    except:
        logger.Critical("","[SetVoltage] failed to set voltage")
        raise TestError.TestFailError("","[SetVoltage] failed to set voltage")
    return
#end of voltage

def BufferCompare(vtfContainer,buffer1,buffer2,offset1=0,offset2=0,byteCount=None,buffer1Description=None,\
                  buffer2Description=None):
    """
    Name         :  BufferCompare
    Description  :  Compares the buffer contents with offsets specified and reports miscompare location if the
                    errorLogEnabled falg is enabled
    Arguments    :
     buffer1     - buffer containing the expected data
     buffer2     - buffer containing the data obtained from card
     offset1     - offset in buffer1 from where compare should be done
     offset2     - offset in buffer2 from where compare should be done
     byteCount   - number of bytes to compare
     buffer1Description - if none, then taken as expected data
     buffer2Description - if none,then taken as data obtained from card
     startLba    - starting Lba of the data compare
     errorLogEnabled    - if this flag is true, then miscompare locations are reported in log,otherwise not reported

    Returns     :
      None
    """
    logger = vtfContainer.GetLogger()
    #defaulting the buffer descriptions if not passed
    if buffer1Description == None:
        buffer1Description = 'Expected data'
    if buffer2Description == None:
        buffer2Description = 'Data obtained from card'
    try:
        buffer1.Compare(buffer2,offset1,offset2,byteCount,buffer1Description,buffer2Description)
    except Exception as exc:
        logger.Warning("" , "[BufferCompare]********Data Miscompare error has occured*********")
        raise

def InsertDelay(delayTimeInMS,vtfContainer):
    """
    Name:             InsertDelay
    Description:      Insert delay in milli second
    Arguments:
      delayTimeInMS   : delay in millisec
      vtfContainer       : vtfContainer of card
    Returns:
           None

    """
    millisecInSec = 1000
    nanoSecInMillSec = 1000*1000
    logger = vtfContainer.GetLogger()
    logger.Warning("" , "[InsertDelay] Inserting delay for %d millisec" %delayTimeInMS)
    if vtfContainer.isModel:# if Model Protocol
        delaySec = int(old_div(delayTimeInMS, millisecInSec))
        remDelayInNanoSec = int((delayTimeInMS % millisecInSec)*nanoSecInMillSec )
        vtfContainer._livet.GetCmdGenerator().Delay(delaySec,remDelayInNanoSec)
    else:# other than model protocol
        import time as time
        #make it in seconds
        delayTimeInSec = float(delayTimeInMS) / 1000
        time.sleep(delayTimeInSec)

#end of InsertDelay()

def GetWriteEccPageOption(initialWriteOption, isBlockInTrueBinaryMode = True):

    """
    Name:             GetWriteEccPageOption
    Description:      This function will change the user initial option for writeEccPage, if the block is in True Binary mode.
                   This function will return the same otion if block is not True Binary mode
    Arguments:
      initialWriteOption      : initial write Ecc page option
      isBlockInTrueBinaryMode : flag tell wether its a True Binary block or normal block
    Returns:
       finalWriteOption    : final write Ecc option
    """
    iniObj=IniReader.IniClass()
    finalWriteOption = initialWriteOption

    #if block is in true binary mode change the write ecc option
    if isBlockInTrueBinaryMode:
        WRITE_IN_TRUE_BINARY_MODE = iniObj.BE_SPECIFIC_WRITE_IN_TRUE_BINARY_MODE
        finalWriteOption = initialWriteOption | WRITE_IN_TRUE_BINARY_MODE  # Seeting the option so that the block will be programmed in True Binary mode
    #end of if
    return finalWriteOption


def DecToBin(decValue):
    """
    Description:
       * Convert decimal to binary
    """
    binaryValue = []

    if decValue == 0:
        return '0'
    while decValue > 0:
        binaryValue.append(decValue%2)
        decValue  = decValue >> 1

    while (len(binaryValue) < 16):
        binaryValue.append(0)

    return binaryValue
# End of DecToBin


def IscardInReadOnlyMode(vtfContainer):
    """
    Name        :IscardInReadOnlyMode
    Description :This function returns true if card is in read only mode
    Arguments   :None
    Returns     :True if card is read only mode
    """

    try:
        livet = vtfContainer._livet
        adapter = vtfContainer.systemCfg.FrameWork.adapter
        logger = vtfContainer.GetLogger()
    except:
        return __ReadOnlyModeOriginal(vtfContainer)

    # the device is in ReadOnly mode or not. (long)dataSize [, (int)patternType [, (bool)isSector]]
    getMMLDataBuf = pyWrap.Buffer.CreateBuffer(1, 0x00)

    opCode = DiagLib.READ_FW_PARAM_DIAG_OPCODE
    subOpcode = 0x08
    cdb = [opCode, 0,subOpcode, 0,
               0,0,0,0,
               0,0,0,0,
               0,0,0,0]


    try:
        DiagLib.SendDiagnostic(vtfContainer,getMMLDataBuf,cdb,0,1) # single sector read
    except Exception as exc:
        #if WA occured during read.
        if vtfContainer.isModel:
            if(int(SDWrap.HOST_COMMAND_STATUS.hcsPowerFail) != SDWrap.WrapGetLastCommandStatus()):  #self.__adapter.GetLastCommandStatus()):
                logger.Info("", ' [On ReadOnlyMode] Power Failure (Write Abort) detected. Continuing....')
            else:
                #To recheck - adapter related APIs GetLastCrashMessage() (Can we simply use __ReadOnlyModeOriginal() API)
                #check for Model Fata error
                if IsModelFatalError(adapter,exc):
                    logger.Error("", "Model has FATAL error")
                    raise
    except:
        logger.Error("", "*** ReadOnlyMode Diag command failed with unknown reason ***")
        raise

    if(getMMLDataBuf.GetOneByteToInt(0)==1):
        return True
    return False

def __ReadOnlyModeOriginal(card):
    """
    Name        :IscardInReadOnlyMode
    Description :This function returns true if card is in read only mode
    Arguments   :None
    Returns     :True if card is read only mode
    """

    # the device is in ReadOnly mode or not.
    getMMLDataBuf = pyWrap.Buffer.CreateBuffer(1,0x00)
    #To recheck: use the opcode from Diagnostic/Constants
    opCode = 0x65 #READ_FW_PARAM_DIAG_OPCODE
    subOpcode = 0x08
    cdb = [opCode, 0,subOpcode, 0,
           0,0,0,0,
           0,0,0,0,
           0,0,0,0]

    diagCmd = pyWrap.DIAG_FBCC_CDB()
    diagCmd.cdb = cdb
    diagCmd.cdbLen = 16

    sctpCommand = pyWrap.SCTPCommand.SCTPCommand(diagCmd, getMMLDataBuf, pyWrap.DIRECTION_OUT)
    sctpCommand.Execute()

    if(getMMLDataBuf.GetOneByteToInt(0)==1):
        return True
    return False
#End of __ReadOnlyModeOriginal


def IsLBAInLastWrittenPage(vtfContainer, Lba):
    return vtfContainer._livet.GetFlash().IsLBAInLastWrittenPage(Lba)

def thisFunctionName():

    """
      Name:  thisFunctionName
      Description: Returns the current function name
      Arguments:
           None
      Return   :
           function name
    """
    import inspect
    return inspect.stack()[1][3]
#End of thisFunctionName

def GetMaxLbaFromParameterFile(paramsFile,capacity):
    """
    Name :              GetMaxLbaFromParameterFile()

    Description:        Get the maxLba by parsing the parameter file
    Arguments:
       paramsFile          Parameter file name
    Returns:
       maxLba     maxLba got from the parameter file
    """
    maxLba=None
    try:
        f = open(paramsFile)
        linelist=f.readlines()
        f.close()
    except :
        raise


    startIndex=linelist.index("[CAPACITIES]\n")
    capacityList=[]
    for element in linelist[startIndex+1:]:
        capacityList.append(element)
        if "[" in element:
            break

    #print capacityList

    searchString="="+capacity
    for line in capacityList:
        if not line[0]=="#":
            if searchString in line:
                maxLba,capacity=line.split("=")
                break

    if maxLba is None:
        raise TestError.TestFailError("","[GetMaxLbaFromParameterFile] Unable to find the maxLba for the capacity %s in the given parameter file %s"%(capacity,paramsFile))

    return int(maxLba)
# end of GetMaxLbaFromParameterFile

def FitTransferLengthToRange(transferLength,
                             startLba, maxAllowableLba ):
    """
    Fit a transfer length to the LBA range it will be used in.  The transfer length
    will be truncated so as to not exceed the maximum allowable LBA.

    Arguments:
       transferLength  - the transfer length
       startLba        - the lba where the data transfer will begin
       maxAllowableLba - the maximum allowable LBA for the data transfer.  This
                         may be less than the max LBA of the card.

    Returns:
       the transfer length fit to the lba range
    """

    assert startLba <= maxAllowableLba , "Start Lba (0x%X) is > maxLba(0x%X)"%(startLba, maxAllowableLba)

    # Truncate the transfer length if it will exceed the maximum allowable LBA
    if startLba + transferLength - 1 > maxAllowableLba:
        transferLength = maxAllowableLba - startLba + 1

    return( transferLength )
#end of FitTransferLengthToRange


def ProcessLbaRangeInputs(lbaRanges,maxLba):

    for currLbaRangeIndex, currLbaRange in enumerate( lbaRanges ):
        currStartLba = currLbaRange[0]
        currEndLba   = currLbaRange[1]

        if currStartLba < 0:
            currStartLba += maxLba +1

        if currEndLba < 0:
            currEndLba += maxLba + 1

        assert currStartLba >=0 , "Start Lba of LbaRange is less than 0 "
        assert currEndLba <= maxLba , "End Lba of Lbarange is > maxLba"
        assert currStartLba <= currEndLba, "Start Lba  > End Lba of LbaRange "

        lbaRanges[currLbaRangeIndex] = [ currStartLba, currEndLba ]
        #end of for loop
    return( lbaRanges )
    #End of ProcessLbaRangeInputs


def IsDeviceSd(vtfContainer):
    """
    Checks if the device used SD protocol whether its card of Model
    """

    return ((vtfContainer.getActiveProtocol() == "SD") or (vtfContainer.isModel))



class ReadOnlyModeReason(object):
    RO_Reason_NotEnabled = 0
    RO_Reason_SwitchedByAnotherBank = 1
    RO_Reason_UM_DoubleWA =2
    RO_Reason_MIP_FlushFailed = 3
    RO_Reason_BM_TooFewBlocks = 4
    RO_Reason_BCZone_NoSpaceForPFRecovery = 5
    RO_Reason_GC_UECCError = 6
    RO_Reason_MML_UECCReturnedFromWrite = 7
    RO_Reason_ICB_CompactionFailed = 8
    RO_Reason_BEThread_MMLRecoveryBGFailed = 9
    RO_Reason_BEThread_IdleBGFailed = 10
    RO_Reason_BEThread_CallMMLFailed = 11
    RO_Reason_EH_PFRecoveryFailed =  12
    RO_Reason_GAT_BufferNotAllocated = 13
    RO_Reason_GAT_PFRecoveryFailed = 14
    RO_Reason_MIP_PFRecoveryFailed = 15
    RO_Reason_UM_CopySectors_PFRecoveryFailed = 16
    RO_Reason_FM_BlockNotAllocatedForReplacing = 17
    RO_Reason_MML_PostInitFailed = 18


class CallMMLFailed_Payload(object):
    STATUS_NO_BLOCKS = 15
    MML_MAX_EPWR_FAIL = 1616


def VerifyReadOnlyModeCondition(vtfContainer, readOnlyModeReason, readOnlyModePayLoad):
    """
    This function verifies whether the read only mode condition encountered was valid.
    send a Diagnostic if it fails. Do a power cycle and then verify the condition for  which the device went in RO mode
    """

    global g_factoryMarkedBadBlockList, g_validSlcMetaBlockNumbers, g_validMlcMetaBlockNumbers
    g_factoryMarkedBadBlockList = []
    g_validSlcMetaBlockNumbers  = None
    g_validMlcMetaBlockNumbers  = None

    logger = vtfContainer.GetLogger()
    logger.Info("", "Verifying the Read only mode Reason")
    if (readOnlyModeReason == ReadOnlyModeReason.RO_Reason_BEThread_CallMMLFailed):
        if(readOnlyModePayLoad == CallMMLFailed_Payload.STATUS_NO_BLOCKS):
            # check in FBL if there are no free blocks available
            logger.Info("", "Card went in to Read only mode with Reason: RO_Reason_BEThread_CallMMLFailed. Reason: Status no blocks")
            try:
                logger.Info("", "Sending Diagnostic to get spare block count")
                fblCount = DiagLib.GetSpareBlockCount(vtfContainer)
            except:
                logger.Info("", "Diagnostic failed as test is in Read only Mode. ")
                return # cannot check
            if(fblCount[0] == 0):
                # there are no SLC blocks available
                logger.Info("", "There are no free SLC blocks")
                # do a power cycle and then check again ??
            else:
                import TestElement.TestError as Error
                logger.Info("", "Free SLC Block = %s"%fblCount[0])
                logger.Info("", "Free MLC Block = %s"%fblCount[1])
                raise Error.TestFailError("Utils","The number of free SLC blocks is %s"%fblCount[0])
        #elif (readOnlyModePayLoad == CallMMLFailed_Payload.MML_MAX_EPWR_FAIL):
            # Where do I find these errors ??


class SdModeClass(object):
    #To recheck: SDModeClass Implementation
    def __init__(self, vtfContainer):
        self.__logger   =  vtfContainer.GetLogger()

    #end of __init__

    def SetRandomSDRmode(self, randonObj):
        resBuff = pyWrap.Buffer.CreateBuffer(0x40, 0x0, isSectors = False)
        self.__card.CardSwitchCmd(False, [0x2, 0xF, 0xF, 0xF, 0xF, 0xF], resBuff, 0x40)
        decodedResponse = self.DecodeSwitchCommandResponse("CHECK", resBuff)
        self.__logger.Info("", "[setSDRmode]:%s"%(decodedResponse))

        responceLen = len (decodedResponse)
        if responceLen < 3:
            self.__logger ("No SDR mode supported. Some thing wrong in the test")
            raise TestError.TestFailError("","No SDR mode supported. Some thing wrong in the test")

        supportedSDRmodeList = []
        for index in range (1, responceLen - 1):
            if decodedResponse [index] == "SDR12 SUPPORTED":
                supportedSDRmodeList.append('SDR12')
            elif decodedResponse [index] == "SDR25/HIGH SPEED SUPPORTED":
                supportedSDRmodeList.append('SDR25')
            elif decodedResponse [index] == "SDR50 SUPPORTED":
                supportedSDRmodeList.append('SDR50')
            elif decodedResponse [index] == "SDR104 SUPPORTED":
                supportedSDRmodeList.append('SDR104')
            elif decodedResponse [index] == "DDR50 SUPPORTED":
                supportedSDRmodeList.append('DDR50')

        self.__logger.Info("", "Supported SDR modes are %s"%(supportedSDRmodeList,))
        radomSdrMode = supportedSDRmodeList[randonObj.randint(0, (len(supportedSDRmodeList) - 1))]

        self.setSDRmode(radomSdrMode)
        return
    #end of SetRandomSDRmode

    def setSDRmode(self, sdrMode = None):
        self.__logger.Info("", "#"*150)
        if sdrMode == 'SDR12':
            self.__SetSDRmode(sdrMode = 'SDR12', hostFrequency = 25*1000*1000,busWidth = 4)
        elif sdrMode == 'SDR25':
            self.__SetSDRmode(sdrMode = 'SDR25', hostFrequency = 50*1000*1000,busWidth = 4)
        elif sdrMode == 'SDR50':
            self.__SetSDRmode(sdrMode = 'SDR50', hostFrequency = 100*1000*1000,busWidth = 4)
        elif sdrMode == 'SDR104':
            self.__SetSDRmode(sdrMode = 'SDR104', hostFrequency = 208*1000*1000,busWidth = 4)
        elif sdrMode == 'DDR50':
            self.__SetSDRmode(sdrMode = 'DDR50', hostFrequency = 50*1000*1000,busWidth = 4)
        elif sdrMode == 'HS':
            self.__SetSDRmode(sdrMode = 'HS', hostFrequency = 50*1000*1000,busWidth = 4)
        elif sdrMode == 'LS':
            self.__SetSDRmode(sdrMode = 'LS', hostFrequency = 25*1000*1000,busWidth = 4)
        elif sdrMode == 'HS_UHS':
            self.__SetSDRmode(sdrMode = 'HS_UHS', hostFrequency = 25*1000*1000,busWidth = 4)
        elif sdrMode == 'LS_UHS':
            self.__SetSDRmode(sdrMode = 'LS_UHS', hostFrequency = 12*1000*1000,busWidth = 4)
        else:
            self.__logger.Info("", "Trying to set wrong SDR mode")
            raise TestError.TestFailError("","Trying to set wrong SDR mode")
        self.__logger.Info("", "#"*150)
        #End of DoBasicInit function

    def __SetSDRmode(self, sdrMode = None, hostFrequency = 0, busWidth = 4):
        if sdrMode == None:
            self.__logger.Info("", "SDR mode can not be None")
            raise TestError.TestFailError("","SDR mode can not be None")

        responseBuff = pyWrap.Buffer.CreateBuffer(0x40, 0x0, isSectors = False)
        self.__card.CardSwitchCmd(False, [0x2, 0xF, 0xF, 0xF, 0xF, 0xF], responseBuff, 0x40)
        decodedResponse = self.DecodeSwitchCommandResponse("CHECK", responseBuff)
        self.__logger.Info("", "[setSDRmode]:%s"%(decodedResponse))

        if sdrMode == 'SDR12' or sdrMode == 'LS_UHS' or sdrMode == 'LS':
            self.__logger.Info("", "[setSDRmode] Switch to %s Access mode"%sdrMode)
            self.__card.CardSwitchCmd(True, [0xF, 0xF, 0xF, 0xF, 0xF, 0xF], responseBuff, 0x40)
            decodedResponse  = self.DecodeSwitchCommandResponse("SWITCH", responseBuff)
            self.__logger.Info("", "[setSDRmode]:%s"%(decodedResponse))

        elif sdrMode == 'SDR25' or sdrMode == 'HS_UHS' or sdrMode == 'HS':
            self.__logger.Info("", "[setSDRmode] Switch to %s Access mode"%sdrMode)
            self.__card.CardSwitchCmd(True, [0x1, 0xF, 0x0, 0xF, 0xF, 0xF], responseBuff, 0x40)
            decodedResponse  = self.DecodeSwitchCommandResponse("SWITCH", responseBuff)
            self.__logger.Info("", "[setSDRmode]:%s"%(decodedResponse))

        elif sdrMode == 'SDR50':
            self.__logger.Info("", "[setSDRmode] Switch to %s Access mode"%sdrMode)
            self.__card.CardSwitchCmd(True, [0x2, 0xF, 0xF, 0xF, 0xF, 0xF], responseBuff, 0x40)
            decodedResponse  = self.DecodeSwitchCommandResponse("SWITCH", responseBuff)
            self.__logger.Info("", "[setSDRmode]:%s"%(decodedResponse))

        elif sdrMode == 'SDR104':
            self.__logger.Info("", "[setSDRmode] Switch to %s Access mode"%sdrMode)
            self.__card.CardSwitchCmd(True, [0x3, 0xF, 0x0, 0x1, 0xF, 0xF], responseBuff, 0x40)
            decodedResponse  = self.DecodeSwitchCommandResponse("SWITCH", responseBuff)
            self.__logger.Info("", "[setSDRmode]:%s"%(decodedResponse))

        elif sdrMode == 'DDR50':
            self.__logger.Info("", "[setSDRmode] Switch to %s Access mode"%sdrMode)
            self.__card.CardSwitchCmd(True, [0x4, 0xF, 0xF, 0xF, 0xF, 0xF], responseBuff, 0x40)
            decodedResponse  = self.DecodeSwitchCommandResponse("SWITCH", responseBuff)
            self.__logger.Info("", "[setSDRmode]:%s"%(decodedResponse))

        if decodedResponse[1] ==  'NOT_SWITCHED':
            self.__logger.Info("", "[setSDRmode] Not switched to Expected SDR Mode")
            raise TestError.TestFailError("","Not switched to Expected SDR Mode")#('Not switched to Expected SDR Mode')

        self.__logger.Info("", "[setSDRmode] Setting BusWidth to:%d"%busWidth)
        self.__card.SetBusWidth(busWidth)
        self.__logger.Info("", "[setSDRmode] Setting Host Frequency in Hz:%d"%hostFrequency)
        self.__adapter.SetHostFrequency(hostFrequency)
    #End of SetSDR50mode

    def DecodeSwitchCommandResponse(self,operationalMode,responseList):
        """
        DecodeSwitchCommandResponse decodes the response buffer of CMD6.
        """
        decodedList = []
        if(operationalMode == "CHECK"):
            if(responseList[0] == 0 and responseList[1] == 0):
                decodedList.append("ERROR-No Operation Current")
                self.__logger.Info("", "[setSDRmode] Failed with Operating Current:00")
            else:
                decodedList.append("OperatingCurrent:%s"%responseList[1])
            if(responseList[13] & 0x01):
                decodedList.append("SDR12 SUPPORTED")
            if(responseList[13] & 0x02):
                decodedList.append("SDR25/HIGH SPEED SUPPORTED")
            if(responseList[13] & 0x04):
                decodedList.append("SDR50 SUPPORTED")
            if(responseList[13] & 0x08):
                decodedList.append("SDR104 SUPPORTED")
            if(responseList[13] & 0x10):
                decodedList.append("DDR50 SUPPORTED")
            if(responseList[7] & 0x01):
                decodedList.append("Current: 200mA SUPPORTED")
            if(responseList[7] & 0x02):
                decodedList.append("Current: 400mA SUPPORTED")
            if(responseList[7] & 0x04):
                decodedList.append("Current: 600mA SUPPORTED")
            if(responseList[7] & 0x08):
                decodedList.append("Current: 800mA SUPPORTED")
        elif(operationalMode == "SWITCH"):
            decodedList.append("OperatingCurrent:%s mA"%responseList[1])
            if(responseList[16] == 0):
                decodedList.append("SDR12 SWITCHED")
            elif(responseList[16] == 1):
                decodedList.append("SDR25/HIGH SPEED SWITCHED")
            elif(responseList[16] == 2):
                decodedList.append("SDR50 SWITCHED")
            elif(responseList[16] == 3):
                decodedList.append("SDR104 SWITCHED")
            elif(responseList[16] == 4):
                decodedList.append("DDR50 SWITCHED")
            else:
                decodedList.append("NOT_SWITCHED")

            if(responseList[15] >>4 == 0):
                decodedList.append("200mA SWITCHED")
            if(responseList[15] >>4 == 1):
                decodedList.append("400mA SWITCHED")
            if(responseList[15] >>4 == 2):
                decodedList.append("600mA SWITCHED")
            if(responseList[15] >>4 == 2):
                decodedList.append("800mA SWITCHED")

        return  decodedList
    #End of DecodeSwitchCommandResponse

def CalculateTimeDiff(startSec,startNanoSec,endSec,endNanoSec):
    startNanoSec = (startSec * 1000000000) + startNanoSec
    endNanoSec = (endSec * 1000000000) + endNanoSec
    if startNanoSec > endNanoSec:
        raise TestError.TestFailError("","start simulation time is greater than end simulation time")
    timeDiffInNanoSec = endNanoSec - startNanoSec

    return timeDiffInNanoSec



#RPG_18390 - Merged code from Lambeau_PB stream
def GetSLCBlockBudget(vtfContainer):


    slcBadBlkRange = (0,0)
    validationSpace              = ValidationSpace.ValidationSpace(vtfContainer)
    FwConfigData                  = validationSpace.GetFWConfigData()

    numOfPlane = FwConfigData.numberOfMetaPlane
    unCommittedSrcBlk = FwConfigData.unCommittedSrcBlk

    File14ConfigBuf = FileData.GetFile14Data(vtfContainer)

    slcPoolBudgetPerPlane = File14ConfigBuf["slcPoolBudget"]
    numOfSeqStreams = File14ConfigBuf["numOfSeqStreams"]
    numOfRandomStreams = File14ConfigBuf["numOfRandomStreams"]
    numOfGATBlocksPerPlanePerPlane = File14ConfigBuf["numOfGATBlocks"]
    numOfBlocksDedicatedFBL = File14ConfigBuf["numOfBlocksDedicatedFBL"]

    MMLParams=DiagLib.ReadMmlParameters(vtfContainer)
    dedicatedMIP = MMLParams["MIP_IsDedicatedBlock"]
    slcPoolBudget = slcPoolBudgetPerPlane * numOfPlane
    numOfSlcCompDestBlks = SLC_COMPACTION_BLOCK_SPARROW * numOfPlane

    numGCContextBlk = GC_CONTEXT_BLOCK_SPARROW * numOfPlane
    numGATBlk = (numOfGATBlocksPerPlanePerPlane * numOfPlane)
    if dedicatedMIP:
        numGATBlk = numGATBlk-1

    slcFIFOSize = slcPoolBudget - (numOfSeqStreams + numOfRandomStreams + NUM_SAFE_ZONE_BLOCK_SPARROW + numOfSlcCompDestBlks + NUM_MLC_COMPACTION_BLOCK_SPARROW)

    slcFIFOSizePerPlane = old_div(slcFIFOSize,numOfPlane)
    slcBadBlkMin = slcFIFOSizePerPlane - (MAX_COLD_BLOCK_SPARROW + MAX_COMPATCION_SLOTS_SPARROW)
    # Card can go to RO mode between the calculated MIN to MAX+1 PF range
    slcBadBlkRange = (slcBadBlkMin,slcFIFOSizePerPlane+1)


    return slcBadBlkRange

def GetNumOfPFPerPlane(vtfContainer,pfAddressList):

    PFPerMetaPlaneDict = {}
    PFPerMetaPlaneDictComplete = {}
    blockListPerPlane = {}
    numPF = 0
    pBlklist = []
    validationSpace              = ValidationSpace.ValidationSpace(vtfContainer)
    FwConfigData                  = validationSpace.GetFWConfigData()
    planeInterleave = FwConfigData.planeInterleave
    dieInterleave   = FwConfigData.dieInterleave
    numOfDies = FwConfigData.diesPerChip

    if FwConfigData.MMP:
        planeList = list(range(numOfDies))
        planeList = [planeList[count:count+dieInterleave] for count in range(0, len(planeList), dieInterleave)]
        #Get PF injected blocks per plane
        for plane in range(0,planeInterleave):
            key = 'p'+str(plane)
            blockListPerPlane[key] =  planeList[plane]

        planeList =  list(blockListPerPlane.keys())
        for addr in pfAddressList:
            die = addr[0]
            block =addr[2]
            for plane in planeList:
                if die in blockListPerPlane[plane]:
                    if plane in PFPerMetaPlaneDict:
                        PFPerMetaPlaneDict[plane].append(block)
                    else:
                        PFPerMetaPlaneDict[plane] =[block]
                    break

        for plane in list(PFPerMetaPlaneDict.keys()):
            numPF = len(PFPerMetaPlaneDict[plane])
            PFPerMetaPlaneDictComplete[plane] = {'blklist' : PFPerMetaPlaneDict[plane],'numPF' : numPF }


    else:
        for addr in pfAddressList:
            block =addr[2]
            pBlklist.append(block)

        numPF = len(pBlklist)
        PFPerMetaPlaneDictComplete['p0'] = {'blklist' : pBlklist,'numPF' : numPF }


    return PFPerMetaPlaneDictComplete

def ConvertAddrListToHex(addrList):

    hexList = [hex(x) for x in addrList]

    return hexList

def CheckDulicateBlock(blockAddrList):
    """
      return duplicate items if found
    """
    dupBlockList = [block for block in range(len(blockAddrList))if blockAddrList.count(block) > 1]

    return dupBlockList


def ReadAndVerifyGrownBadBlockFile(vtfContainer):
    """
        Reads and verifies Grown bad block file
    """

    #Check if File 226 is created after format and its empty.
    validationSpace              = ValidationSpace.ValidationSpace(vtfContainer)
    FwConfigData                  = validationSpace.GetFWConfigData()

    logger = vtfContainer.GetLogger()

    numBanks = FwConfigData.numOfBanks
    GBBLSizePerBank = FwConfigData.sectorsPerEccPage * FwConfigData.bytesPerSector
    file226Object     = FileData.GrownBadBlockFileData(vtfContainer,GBBLSizePerBank,numBanks)
    #Get the Grown defect block count from file 226
    initialGrownDefectBlockCount = file226Object.GetGrownDefectBlocksCount(vtfContainer)
    gbbFileVersion = file226Object.GetGrownBadBlockFileVersion(vtfContainer)
    logger.Info("", "File 226[Grown Bad Block File] Version : %d "%gbbFileVersion)
    # If GBB file is empty fail the test
    if len(initialGrownDefectBlockCount) == 1:
        index = 0
        if not ( initialGrownDefectBlockCount[index] == 0):
            #StandardMessages.DisplayFileContents(vtfContainer,[226])
            filebuff = DiagLib.ReadFileSystem(vtfContainer,226)
            filebuff.PrintToLog()
            raise TestError.TestFailError("","File 226[Grown Bad Block File] is not Empty after Format")
    else:
        for index in range(0, len(initialGrownDefectBlockCount)-1):
            if not ( initialGrownDefectBlockCount[index] == 0):
                #StandardMessages.DisplayFileContents(vtfContainer,[226])
                filebuff = DiagLib.ReadFileSystem(vtfContainer,226)
                filebuff.PrintToLog()
                raise TestError.TestFailError("","File 226[Grown Bad Block File] is not Empty after Format")

    logger.Info("", "File 226[Grown Bad Block File] is Empty after Format")

def GetPaddedWL(vtfContainer):
    """
    Description:
       * Number of wordlines padded
    """
    import ValidationSpace, FileData
    validationSpace = ValidationSpace.ValidationSpace(vtfContainer)
    file14Obj = FileData.GetFile14Data(vtfContainer)
    return file14Obj["shiftedWLValue"]



def VerifyBlockRelinkAndGetAllValidMetaBlockList(vtfContainer):
    """
    This function verifies block relink logic
    Also reurns valid SLC and MLC meta block list
    """
    global g_factoryMarkedBadBlockList, g_validSlcMetaBlockNumbers, g_validMlcMetaBlockNumbers
    validationSpace              = ValidationSpace.ValidationSpace(vtfContainer)
    logger                       = vtfContainer.GetLogger()
    livet                        = vtfContainer._livet
    fwConfigObj                  = validationSpace.GetFWConfigData()
    optionValues                 = validationSpace.GetOptionValues()

    FileDataObj      = FileData.ConfigurationFile21Data( vtfContainer )
    maxBadBlockCount = FileDataObj.maxBadBlockCount # FILE_21 offset = 0x50
    File14Object     = FileData.GetFile14Data(vtfContainer)
    numGATBlocks     = File14Object['numOfGATBlocks']

    logger.Info ("","::::::::::::::::::: Verifying relinked blocks : START   :::::::::::::::::::")

    totalMetaBlocksInCard      = fwConfigObj.totalMetaBlocksInCard
    numberOfMetaPlane          = fwConfigObj.numberOfMetaPlane
    diesPerChip                = fwConfigObj.diesPerChip
    createInvalidMBNumbersList = []

    (totalSpareBlockCount, listOfSLCMetaBlocksInFBL, listOfMLCMetaBlocksInFBL,listOfDedicatedFBLMetaBlocks)=DiagLib.GetSpareBlockListInfo(vtfContainer)

    maxStrightMetaBlockNumber = None
    if optionValues.numberOfDiesInCard == 2 or optionValues.numberOfDiesInCard == 4 or optionValues.numberOfDiesInCard == 1: #MMP 1
        maxStrightMetaBlockNumber = totalMetaBlocksInCard #1478
    if optionValues.numberOfDiesInCard == 6 or optionValues.numberOfDiesInCard == 12 or optionValues.numberOfDiesInCard == 8:#MMP 3
        maxStrightMetaBlockNumber = totalMetaBlocksInCard #5912
    if optionValues.numberOfDiesInCard == 8: #MMP 2
        maxStrightMetaBlockNumber = totalMetaBlocksInCard #2956
    if optionValues.numberOfDiesInCard == 16: #MMP 4
        maxStrightMetaBlockNumber = totalMetaBlocksInCard #7832

    metaPlaneSubtractionFactor = 0
    if optionValues.numberOfDiesInCard == 6 or optionValues.numberOfDiesInCard == 12:#This is a workaround for 6D initial regressions, needs to be removed once FW issue is resolved
        #maxBadBlockCount = 92
        numberOfMetaPlane = 4
        totalMetaBlocksInCard = 1478 * numberOfMetaPlane
        metaPlaneSubtractionFactor = 1

    # Remove the GAT Blocks from the min meta  blocks expected as these would be allocated as Single Plnae Control Blocks
    #spControlBlocks = DiagLib.GetSinglePlaneControlBlocksList(vtfContainer,fwConfigObj,numGATBlocks)
    #total_SPCB = len(spControlBlocks[0]) + len(spControlBlocks[1]['gatPrimary'] + [spControlBlocks[1]['gatSecondary']]) + len(spControlBlocks[2]['gatFBL'])

    minMetaBlokExpected = (totalMetaBlocksInCard  - (1478 * metaPlaneSubtractionFactor ))  - (maxBadBlockCount * (numberOfMetaPlane - metaPlaneSubtractionFactor)) - numGATBlocks * (numberOfMetaPlane - metaPlaneSubtractionFactor)

    for phyBlkAddress in g_factoryMarkedBadBlockList:
        if fwConfigObj.numberOfMetaPlane == 1:
            if phyBlkAddress[3] not in createInvalidMBNumbersList:
                createInvalidMBNumbersList.append (phyBlkAddress[3])
        else:
            #metaPlaneOfaBlock = phyBlkAddress[1] / fwConfigObj.dieInterleave
            metaPlaneOfaBlock  = old_div(((phyBlkAddress[0] * diesPerChip) + phyBlkAddress[1]), fwConfigObj.dieInterleave)
            metaBlock = (phyBlkAddress[3] * numberOfMetaPlane) + metaPlaneOfaBlock
            if metaBlock not in createInvalidMBNumbersList:
                createInvalidMBNumbersList.append (metaBlock)

    if optionValues.numberOfDiesInCard == 6 or optionValues.numberOfDiesInCard == 12: #This is just a workaround till FW diag is changed to give right value
        for metaBlock in range (0, totalMetaBlocksInCard * 2):
            if metaBlock % 4 == 3:
                createInvalidMBNumbersList.append(metaBlock)

    logger.Debug("","Factory marked bad blocks are ::: %s"%(g_factoryMarkedBadBlockList))
    logger.Debug("","Expected INVALID blocks are  ::: %s"%(createInvalidMBNumbersList))

    validSlcMetaBlockNumbers = []
    validMlcMetaBlockNumbers = []

    for metaBlockNum in range (0, totalMetaBlocksInCard): # + len (createInvalidMBNumbersList) + 10000):
        #RPG-18491
        # Harish - Temp fix, where in if GetIGATEntryInfo fails with exception,
        # Assume that it has crossed the max limit of metaBlockNum which iGATEntry can hold and exit
        try:
            IGATEntryInfo = DiagLib.GetIGATEntryInfo(vtfContainer, metaBlockNum)
        except Exception as exc:
            break
        logger.Info ("", "*"*200)
        logger.Debug ("", "[Diag ] ::: MBN ::: %d  blk details ::: %s"%(metaBlockNum, IGATEntryInfo))
        #logger.Info("", "Number of valid meta block found so far : %d  minimum expected is : %d"%((len(validSlcMetaBlockNumbers) + len(validMlcMetaBlockNumbers)),minMetaBlokExpected))
        if (len(validSlcMetaBlockNumbers) + len(validMlcMetaBlockNumbers)) == minMetaBlokExpected:
            logger.Info("", "-"*200)
            logger.Info ("", "Max meta block count has reached. Stoping verification here at metablock number ::: %d"%(metaBlockNum))
            numSlcMetaBlocks       = len(validSlcMetaBlockNumbers)
            numMlcMetaBlocks       = len(validMlcMetaBlockNumbers)
            numNumMetaBlocksInCard = len(validSlcMetaBlockNumbers) + len(validMlcMetaBlockNumbers)
            logger.Info ("", "Number of SLC meta blocks : %d Number of MLC meta blocks : %d Total number of meta blocks in the card : %d (min expected metaBlk num : %d)"%(numSlcMetaBlocks,numMlcMetaBlocks,numNumMetaBlocksInCard, minMetaBlokExpected))
            logger.Info("", "-"*200)
            break

        if (metaBlockNum not in createInvalidMBNumbersList):

            if metaBlockNum >= maxStrightMetaBlockNumber:
                if IGATEntryInfo[4] == 0 and (metaBlockNum not in listOfSLCMetaBlocksInFBL or IGATEntryInfo[10] != 1024):
                    logger.Info ("", "MLC MetaBlockNum ::: 0x%05X  MetaBlock detail ::: %s as expected"%(metaBlockNum, "INVALID"))
                    logger.Info ("", "*"*200)
                    continue

            phyAddrList = DiagLib.GetPhyBlocksInMB(vtfContainer, metaBlockNum, fwConfigObj)
            logger.Info ("", "MBN ::: 0x%X  blk details ::: %s"%(metaBlockNum, phyAddrList))

            if  IGATEntryInfo[4] == 0:
                logger.Debug ("", "[Diag ] Meta block Number ::: %d MetaBlockType ::: %s  "%(metaBlockNum, "SLC"))
                validSlcMetaBlockNumbers.append(metaBlockNum)
            elif IGATEntryInfo[4] == 1:
                logger.Debug ("", "[Diag ] Meta block Number ::: %d MetaBlockType ::: %s  "%(metaBlockNum, "MLC"))
                validMlcMetaBlockNumbers.append(metaBlockNum)
            else:
                logger.Info ("", "[Test: Error] ::: [Diag ] Meta block Number ::: 0x%X MetaBlockType ::: %s"%(metaBlockNum, "INVALID BLOCK TYPE"))
                raise TestError.TestFailError("","ERROR ::: [Diag ] Meta block Number ::: 0x%X MetaBlockType ::: %s"%(metaBlockNum, "INVALID BLOCK TYPE"))

            for phyAddr in phyAddrList:
                if phyAddr in g_factoryMarkedBadBlockList:
                    logger.Info ("", "MetaBlockNumber ::: 0x%X  blk details ::: %s"%(metaBlockNum, phyAddrList))
                    logger.Info ("", "[Test: Error] ::: physical address %s is part of factory marked bad block list"%(phyAddr,))
                    raise TestError.TestFailError("","FBB (addr - %s) used in linking MB: 0x%X"%(phyAddr, metaBlockNum))

            logger.Info("", "Number of valid meta block found so far : %d  minimum expected is : %d"%((len(validSlcMetaBlockNumbers) + len(validMlcMetaBlockNumbers)),minMetaBlokExpected))
            logger.Info ("", "*"*200)
        else:
            if fwConfigObj.dummyMetaPlane and (metaBlockNum % 4 == 3):
                logger.Info ("", "MetaBlockNum ::: 0x%05X  MetaBlock detail ::: %s as expected (metablock in dummy metaplane)"%(metaBlockNum, "INVALID"))
            else:
                logger.Info ("", "MetaBlockNum ::: 0x%05X  MetaBlock detail ::: %s as expected (created because of bad block injection)"%(metaBlockNum, "INVALID"))
            logger.Info ("", "*"*200)

    g_validSlcMetaBlockNumbers = validSlcMetaBlockNumbers
    g_validMlcMetaBlockNumbers = validMlcMetaBlockNumbers

    if ((len(validSlcMetaBlockNumbers) + len(validMlcMetaBlockNumbers)) <  minMetaBlokExpected):
        logger.Info("","$"*200)
        logger.Info("", "ERROR ::: Number of valid meta block Expected %d = Total MetaBlocks in Card : %d - Max BadBlock Count : %d "%(minMetaBlokExpected, totalMetaBlocksInCard, maxBadBlockCount))
        logger.Info("", "ERROR ::: Number of valid meta block found so far : %d is not meeting  minimum expected metablock number : %d"%((len(validSlcMetaBlockNumbers) + len(validMlcMetaBlockNumbers)), minMetaBlokExpected))
        logger.Info ("", "$"*200)
        #raise TestError.TestFailError("","Number of valid meta block found so far : %d is not meeting  minimum expected metablock number : %d"%((len(validSlcMetaBlockNumbers) + len(validMlcMetaBlockNumbers)), minMetaBlokExpected))
    """
    SLCMBList, MLCMBList = DiagLib.GetStaticRelinkedMBList(vtfContainer, maxMBNum=totalMetaBlocksInCard-1)
    RelinkedMBList = SLCMBList + MLCMBList

    for metaBlockNum in RelinkedMBList:
       IGATEntryInfo = DiagLib.GetIGATEntryInfo(vtfContainer, metaBlockNum)

       logger.Info ("", "*"*200)
       logger.Debug ("", "[Diag ] ::: RELINKED MB ::: %d  blk details ::: %s"%(metaBlockNum, IGATEntryInfo))

       phyAddrList = DiagLib.GetPhyBlocksInMB(vtfContainer, metaBlockNum, fwConfigObj)
       logger.Info ("", "MBN ::: 0x%X  blk details ::: %s"%(metaBlockNum, phyAddrList))

       if IGATEntryInfo[4] == 0:
          logger.Debug ("", "[Diag ] Meta block Number ::: %d MetaBlockType ::: %s  "%(metaBlockNum, "SLC"))
       elif IGATEntryInfo[4] == 1:
          logger.Debug ("", "[Diag ] Meta block Number ::: %d MetaBlockType ::: %s  "%(metaBlockNum, "MLC"))
       else:
          logger.Info ("", "[Test: Error] ::: [Diag ] Meta block Number ::: 0x%X MetaBlockType ::: %s"%(metaBlockNum, "INVALID BLOCK TYPE"))
          raise TestError.TestFailError(vtfContainer.GetTestName(), "ERROR ::: [Diag ] Meta block Number ::: 0x%X MetaBlockType ::: %s"%(metaBlockNum, "INVALID BLOCK TYPE"))

       for phyAddr in phyAddrList:
          if phyAddr in g_factoryMarkedBadBlockList:
             logger.Info ("", "MetaBlockNumber ::: 0x%X  blk details ::: %s"%(metaBlockNum, phyAddrList))
             logger.Info ("", "[Test: Error] ::: physical address %s is part of factory marked bad block list"%(phyAddr,))
             raise TestError.TestFailError(vtfContainer.GetTestName(), "FBB (addr - %s) used in relinked MB: 0x%X"%(phyAddr, metaBlockNum))
    """
    logger.Info("", "::::::::::::::::::: Verifying relinked blocks : SUCCESS :::::::::::::::::::")
    return validSlcMetaBlockNumbers,  validMlcMetaBlockNumbers



def SplitMeteBlockListPerMetaPlane (metaBlockList, numberOfMetaPlane):
    #select MLC blocks for
    metaPlaneBlockList = []
    for metaPlane in range(numberOfMetaPlane):
        metaPlaneBlockList.append([])

    for metaBlock in metaBlockList:
        metaBlockIndex = metaBlock % (numberOfMetaPlane)
        if metaBlockIndex < numberOfMetaPlane:
            metaPlaneBlockList[metaBlockIndex].append(metaBlock)
        else:
            raise TestError.TestFailError("","::: ERROR ::: Test script error. MLC meta blocks are in invalid meta plane")

    return metaPlaneBlockList


def ReadFile50ErrorLog(vtfContainer):

    noOfErrorLogs, errorLogObj = DiagLib.ReadAllErrorLogs(vtfContainer)
    return noOfErrorLogs, errorLogObj

def RestFactoryMarkedBadBlockDetails():
    global g_factoryMarkedBadBlockList, g_validSlcMetaBlockNumbers, g_validMlcMetaBlockNumbers
    g_factoryMarkedBadBlockList = []
    g_validSlcMetaBlockNumbers  = None
    g_validMlcMetaBlockNumbers  = None
#end of RestFactoryMarkedBadBlockDetails

def GetLastWriteCommand():
    """
       * Returns last written lba and transfer length
    """
    import ValidationRwcManager

    return ValidationRwcManager.g_currentStartLba ,ValidationRwcManager.g_currentTransferLength

def GetLastHostCommand():
    import ValidationRwcManager

    return ValidationRwcManager.g_lastcmdIssued

def GetLastEraseCommand():
    """
    * Returns last erased lba and transfer length
    """
    import ValidationRwcManager
    return ValidationRwcManager.g_currentEraseStartLba ,ValidationRwcManager.g_currentEraseTransferLength

def GetLastReadCommand():
    """
    * Returns last read lba and transfer length
    """
    import ValidationRwcManager
    return ValidationRwcManager.g_currentReadStartLba ,ValidationRwcManager.g_currentReadTransferLength

#To recheck: Enable and Disable CQ
def EnableCommandQueue( vtfContainer, mode = "voluntary" ):
    """
    Description: This method enables command queue in card using SD Protocol commands
    Arguments: mode = "voluntary" or "sequential"
    Returns: Nothing
    """
    import Validation.SdProtocolCommandsViaCTF as SdCmdsCtfLib

    SdCmdsCls = SdCmdsCtfLib.SDProtocolCommands( vtfContainer )

    #InitToTranstate will be called for both model and hardware as DoBasicInit is disabled in Powercycle
    if vtfContainer.isModel:
        SdCmdsCls.InitToTranState()
    #SdCmdsCls.InitToTranState()

    # Get handle to info function
    logger        = vtfContainer.GetLogger()
    #livet         = vtfContainer._livet
    #flash         = livet.GetFlash()

    info = logger.Info
    verbosity = 2

    message = "Enabling command queue in %s mode" % mode
    info( message )

    # Read function extension registers for performance enhancement registers ( FNO = 2 ),
    if verbosity > 2:
        message = "Reading Performance Enhancement Register set in Extension Registers (FNO = 2)"
        info( message )
    # end_if
    databuf = pyWrap.Buffer.CreateBuffer( 1 )
    SdCmdsCls.CMD48( mio = 0, fno = 2, addr = 0, length = 511, databuf = databuf )
    InsertDelay( 1, vtfContainer )

    # Check the status of command queue byte 262,
    if verbosity > 2:
        message = "Checking byte 262 to determine if command queue is already enabled"
        info( message )
    # end_if
    byte = databuf.GetOneByteToInt( 262 )

    if( ( byte & 0x01 ) == 0x01 ):
        # Command queue is already enabled in voluntary mode, do nothing and exit!
        if verbosity > 2:
            message = "Command queue is already enabled in voluntary mode"
            info( message )
        # end_if
        SdCmdsCls.CMDQ_enabled = True
        if( ( byte & 0x03 ) == 0x01 ):
            SdCmdsCls.CMDQ_mode = "voluntary"
        else:
            SdCmdsCls.CMDQ_mode = "sequential"
        # end_if
    else:
        if verbosity > 2:
            message = "Command queue is disabled"
            info( message )
        # end_if

        # Check if Cache is supported,
        byte = databuf.GetOneByteToInt( 4 )
        # end_if
        if( ( byte & 0x01 ) == 0x01 ):
            # Cache is supported, prepare databuf to enable it
            if verbosity > 2:
                message = "Internal cache is supported, enabling it,"
                info( message )
            # end_if
            databuf.SetByte( 260, 0x01 )
        else:
            # Cache is not supported, prepare databuf to keep it disabled!
            if verbosity > 2:
                message = "Internal cache is not supported, keeping it disabled,"
                info( message )
            # end_if
            databuf.SetByte( 260, 0x00 )
        # end_if

        # Check if command queue is supported, if yes what is the depth allowed?
        cmdq_byte = databuf.GetOneByteToInt( 6 )
        # end_if
        if cmdq_byte == 0:
            # Command queue is not supported!
            message = "This device doesn't support Command Queue"
            info( message )
            raise Exception( message )
        elif cmdq_byte > 0x1F:
            # Illegal depth of command queue!
            message = "This device shows illegal depth of command queue = %d" % cmdq_byte
            info( message )
            raise Exception( message )
        else:
            cmdq_depth = ( cmdq_byte + 1 )
            if verbosity > 2:
                message = "This card supports command queue depth = %d" % cmdq_depth
                info( message )
            # end_if
        # end_if

        # Command queue is disabled, set byte 262 to enable it according to required mode!
        if mode == "voluntary":
            databuf.SetByte( 262, 0x01 )
            SdCmdsCls.CMDQ_mode = "voluntary"
        else:
            databuf.SetByte( 262, 0x03 )
            SdCmdsCls.CMDQ_mode = "sequential"
        # end_if

        # Write function extension registers for performance enhancement ( FNO = 2 ),
        SdCmdsCls.CMD49( mio = 0, fno = 2, mw = 0, addr = 0, length = 511, databuf = databuf )
        InsertDelay( 1, vtfContainer )
        SdCmdsCls.CMDQ_enabled = True
    # end_if

    # Start the thread now
    #self.Condition1 = threading.Condition()
    #self.Thread1 = threading.Thread( target = self.ExecuteFirmware, args = () )
    #self.Thread1.start()

    return
# end of EnableCommandQueue methid of ValidationRwcManager class


def DisableCommandQueue( vtfContainer, mode = "voluntary" ):
    """
    Description: This method flushes cache and disables command queue in card using SD Protocol commands
    Arguments: None
    Returns: Nothing
    """
    import Validation.SdProtocolCommandsViaCTF as SdCmdsCtfLib

    SdCmdsCls = SdCmdsCtfLib.SDProtocolCommands( vtfContainer )

    if vtfContainer.isModel:
        SdCmdsCls.InitToTranState()

    # Get handle to info function
    logger        = vtfContainer.GetLogger()

    # Get handle to info function
    info = logger.Info
    verbosity = 2

    message = "Disabling command queue now"
    info( message )

    if verbosity > 2:
        message = "Reading Performance Enhancement Register set in Extension Registers (FNO = 2)"
        info( message )
    # end_if
    # Read function extension registers for performance enhancement registers ( FNO = 2 ),
    databuf = pyWrap.Buffer.CreateBuffer( 1 )
    SdCmdsCls.CMD48( mio = 0, fno = 2, addr = 0, length = 511, databuf = databuf )
    InsertDelay( 1, vtfContainer )

    # Check the status of command queue byte 262,
    if verbosity > 2:
        message = "Checking byte 262 to determine if command queue is already enabled"
        info( message )
    # end_if
    byte = databuf.GetOneByteToInt( 262 )

    if( ( byte & 0x01 ) == 0x01 ):
        # Command queue is enabled, disable it now by setting byte 262!
        SdCmdsCls.CMDQ_enabled = True
        if verbosity > 2:
            message = "Command queue is already enabled, disabling it now"
            info( message )
        # end_if

        databuf.SetByte( 262, 0x00 )
        # Write function extension registers for performance enhancement ( FNO = 2 ),
        SdCmdsCls.CMD49( mio = 0, fno = 2, mw = 0, addr = 0, length = 511, databuf = databuf )
        InsertDelay( 1, vtfContainer )

        SdCmdsCls.CMDQ_enabled = False
    else:
        # Command Queue is already disabled, do nothing and exit!
        SdCmdsCls.CMDQ_enabled = False
        if verbosity > 2:
            message = "Command queue is already disabled."
            info( message )
        # end_if
    # end_if

    return
# end of DisableCommandQueue methid of ValidationRwcManager class

def GetGCComponentList(vtfContainer):
    import FirmwareWaypointReg
    
    GCComponentList = list(FirmwareWaypointReg.gcComponent_Priority.values())
    return GCComponentList

def WriteConfigFile(vtfContainer, configFileId, Offset, Value, numberOfBytes, doPowerCycle=False):
    #import CardFramework.Buffer as Buffer
    import Extensions.CVFImports as pyWrap

    # Get the size of buffer
    fileSize, sectorCount_inBytes = DiagLib.LengthOfFileInBytes(fileId=configFileId)
    # Create the buffer
    fileBuf = pyWrap.Buffer.CreateBuffer(fileSize)
    # Read the file
    fileBuf = DiagLib.ReadFileSystem(vtfContainer, configFileId, fileSize)

    if numberOfBytes == 1:
        fileBuf.SetByte(Offset,Value)
    elif numberOfBytes == 2:
        fileBuf.SetTwoBytes(Offset,Value)
    else:
        assert (False), "[Utils :: WriteConfigFile] Number of bytes > 2 not handled"

    DiagLib.WriteFileSystem(vtfContainer, configFileId, fileSize, fileBuf)

    if doPowerCycle:
        PowerCycle(vtfContainer)

    return True

def ReadConfigFile(vtfContainer, configFileId, Offset, numberOfBytes):
    # Get the size of buffer
    fileSize, sectorCount_inBytes = DiagLib.LengthOfFileInBytes(fileId=configFileId)

    # Create the buffer
    fileBuf = pyWrap.Buffer.CreateBuffer(fileSize)
    # Read the file
    fileBuf= DiagLib.ReadFileSystem(vtfContainer, configFileId, fileSize, fileBuf)

    if numberOfBytes == 1:
        Value = fileBuf.GetOneByteToInt(Offset)
    elif numberOfBytes == 2:
        Value = fileBuf.GetTwoBytesToInt(Offset)
    else:
        assert (False), "[Utils :: ReadConfigFile] Number of bytes > 2 not handled"

    return Value

def ModifyConfig(vtfContainer, FileID, offset, value):
    UNSET_MASK = 0x0
    BinFile=""
    newBinFile=""

    logger = vtfContainer.GetLogger()
    origWorkingDir  = os.getcwd()
    validationDir = os.getenv('FVTPATH')
    if validationDir.endswith("\\"):
        validationDir = validationDir + "ValidationLib\\ConfigFile"
    else:
        validationDir = validationDir + "\\ValidationLib\\ConfigFile"
    orig_bot = vtfContainer.cmd_line_args.botFilename
    paramsfilepath = vtfContainer.cmd_line_args.sdparamsfile
    os.chdir(validationDir)

    head, tail = os.path.split(orig_bot)
    currentBotFileName = tail
    currentBotFilePath = os.path.join(validationDir,currentBotFileName)

    if os.path.exists(currentBotFilePath):
        os.remove(currentBotFilePath)
             #os.remove('*.bin')
    if os.path.isfile(orig_bot):
        logger.Info("", "Copy the bot file from path %s"%orig_bot)
        shutil.copy2(orig_bot,  currentBotFilePath)
    else:
        raise TestError.TestFailError("Utils", "- Botfile is missing")

    #Extract configuration file/files from bot file
    try:
             #remove any existing bin files if any and verify the executables are available
        if os.path.exists(BinFile):
            os.remove(BinFile)

        if os.path.exists(newBinFile):
            os.remove(newBinFile)

        #Check if the elfBotter.exe is available in the specified path
        if not(os.path.exists("elfbotter.exe")):
            logger.Critical("", "- elfbotter.exe is not present in the current path")
            raise TestError.TestFailError("Utils", "- elfbotter file is missing")

        #Extract file FDT/Format File
        if FileID == 14:
            BinFile = "FD.bin"
            newBinFile = "FD_T.bin"
            #elfbotter -r 21 CFG.bot
            os.system("elfbotter.exe -S FD %s"%currentBotFileName)
        else:
            BinFile = "file" + str(FileID) + ".bin"
            newBinFile = "file" + str(FileID) + "_T.bin"
            os.system("elfbotter.exe -r %d \"%s\""%(FileID, currentBotFileName))
            if not(os.path.exists(BinFile)):
                raise TestError.TestFailError("Utils", "- %d not extracted"%BinFile)
    except:
        raise TestError.TestFailError("Utils", "Failed to extract bin files")

    #Update the File Offsets
    try:
        if os.path.exists(BinFile):
            os.system("hexciting.exe -a -r \"%d\" \"%d\" \"%s\" \"%d\" "%( offset, offset+1,BinFile,UNSET_MASK))
            os.system("hexciting.exe -o -r \"%d\" \"%d\" \"%s\" \"%d\" "%(offset ,offset+1,BinFile,value))
            shutil.copy2(BinFile, newBinFile)
    except:
        raise TestError.TestFailError("Utils", "Failed to modify required configuraton binary files")

    #Patch the current bot file
    try:
        if os.path.exists(newBinFile):
            if FileID == 14:
                os.system("elfbotter.exe -b \"%s\" -x fd\"%s\""%(currentBotFileName, newBinFile))
            else:
                os.system("elfbotter.exe -b \"%s\" -x %d\"%s\""%(currentBotFileName, FileID, newBinFile))
    except:
        raise TestError.TestFailError("Utils", "Failed to repatch modified configuartion files")

    os.chdir(origWorkingDir)
    DoDownLoadAndFormat()
    #Update the botfile to the newly created one
    vtfContainer.cmd_line_args.botFilename = currentBotFilePath
    logger.Info("", "**************************[Utils.ModifyConfig]**************************************")
    logger.Info("", "File %s, offset 0x%X changed to %s"%(FileID, offset, value))
    logger.Info("", "**************************[Utils.ModifyConfig]**************************************")
    return

def CalculateStatistics(vtfContainer):
    #To recheck - not implemented yet

    return
    logger= vtfContainer.GetLogger()
    vtfContainer.cmd_mgr.WaitForThreadCompletion()
    endTime = datetime.now()

    teraBytesWritten = old_div((float(self.globalVarsObj.totalSectorsWritten * self.globalVarsObj.FLBAS)), pow(2, 40))
    amountOfDataWrittenInGB = LbasToGB(self.globalVarsObj.totalSectorsWritten)
    amountOfDataReadInGB = LbasToGB(self.globalVarsObj.totalSectorsRead)

    tDiff = endTime - self.globalVarsObj.startTime
    totalTimeInMicroSeconds = (tDiff.microseconds + (tDiff.seconds + tDiff.days * 24 * 3600) * 10 ** 6)
    totalTime = float(totalTimeInMicroSeconds) / 10 ** 6

    try:
        self.globalVarsObj.IOPS = float(self.globalVarsObj.totalIOCommandCount) / totalTime
    except Exception as exc:
        logger.Info(self.globalVarsObj.TAG, "ERROR in Utils - CalculateStatistics - totalTime is ZERO",
                                          exc.message)
        self.globalVarsObj.IOPS = None

    logger.BigBanner("", "START OF TEST STATS")

    logger.Info("", "Total commands issued: {0}".format(
            (self.globalVarsObj.totalIOCommandCount + self.globalVarsObj.totalAdminCommandCount)))

    logger.Info("", "Total IO commands issued: {0}".format(self.globalVarsObj.totalIOCommandCount))
    logger.Info("", "Total Admin commands issued: {0}".format(self.globalVarsObj.totalAdminCommandCount))

    logger.Info("", "Total Write commands issued: {0}".format(self.globalVarsObj.writeCommandCount))
    logger.Info("", "Total Read commands issued: {0}".format(self.globalVarsObj.readCommandCount))

    logger.Info("", "Total GSD issued: {0}".format(self.globalVarsObj.totalGSDCount))
    logger.Info("", "Total UGSD commands issued: {0}".format(self.globalVarsObj.totalUGSDCount))
    logger.Info("", "Total Power Abort commands issued: {0}".format(self.globalVarsObj.totalPowerAbort))

    logger.Info("", "Total Amount of Data Written: {0} sectors".format(self.globalVarsObj.totalSectorsWritten))
    logger.Info("", "Total Amount of Data Read: {0} sectors".format(self.globalVarsObj.totalSectorsRead))

    logger.Info("", "Total Amount of Data Written: {0} GB".format(amountOfDataWrittenInGB))
    logger.Info("", "Total Amount of Data Read: {0} GB".format(amountOfDataReadInGB))
    logger.Info("", "Terabytes Written: {0} TB".format(teraBytesWritten))

    logger.Info("", "Total Test Time: {0} seconds".format(totalTime))
    logger.Info("", "IOPS: {0}\n".format(self.globalVarsObj.IOPS))
    MBPS = "NA" if totalTime == 0 else old_div(((amountOfDataReadInGB + amountOfDataWrittenInGB) * 1024), totalTime)
    logger.Info("", "MBPS: {0}\n".format(MBPS))

    logger.SmallBanner("END OF TEST STATS")

    if len(self.globalVarsObj.timeList) >= 1:
        self.globalVarsObj.amountWrittenInGBList.append(
                abs(math.ceil(amountOfDataWrittenInGB - self.globalVarsObj.amountWrittenInGBList[-1])))
        self.globalVarsObj.amountReadInGBList.append(
                abs(math.ceil(amountOfDataReadInGB - self.globalVarsObj.amountReadInGBList[-1])))
        self.globalVarsObj.totalSectorsWrittenList.append(
                abs(self.globalVarsObj.totalSectorsWritten - self.globalVarsObj.totalSectorsWrittenList[-1]))
        self.globalVarsObj.totalSectorsReadList.append(
                abs(self.globalVarsObj.totalSectorsRead - self.globalVarsObj.totalSectorsReadList[-1]))
        self.globalVarsObj.timeDiffList.append(totalTime - self.globalVarsObj.timeList[-1])
    else:
        self.globalVarsObj.amountWrittenInGBList.append(math.ceil(amountOfDataWrittenInGB))
        self.globalVarsObj.amountReadInGBList.append(math.ceil(amountOfDataReadInGB))
        self.globalVarsObj.totalSectorsWrittenList.append(self.globalVarsObj.totalSectorsWritten)
        self.globalVarsObj.totalSectorsReadList.append(self.globalVarsObj.totalSectorsRead)
        self.globalVarsObj.timeDiffList.append(totalTime)

    self.globalVarsObj.timeList.append(math.floor(totalTime))
    self.globalVarsObj.IOPSList.append(math.ceil(self.globalVarsObj.IOPS))
    self.globalVarsObj.MBPSList.append(math.ceil(MBPS))

    # logger.Info(self.globalVarsObj.TAG, "Time List: {0}".format(self.globalVarsObj.timeList))
    # logger.Info(self.globalVarsObj.TAG, "IOPS List: {0}".format(self.globalVarsObj.IOPSList))
    # logger.Info(self.globalVarsObj.TAG, "MBPS List: {0}".format(self.globalVarsObj.MBPSList))
    # logger.Info(self.globalVarsObj.TAG, "Data Written In GB List: {0}".format(self.globalVarsObj.amountWrittenInGBList))
    # logger.Info(self.globalVarsObj.TAG, "Data Read In GB List: {0}".format(self.globalVarsObj.amountReadInGBList))
    # logger.Info(self.globalVarsObj.TAG, "Total Sectors Written List: {0}".format(self.globalVarsObj.totalSectorsWrittenList))
    # logger.Info(self.globalVarsObj.TAG, "Total Sectors Read List: {0}".format(self.globalVarsObj.totalSectorsReadList))
    # logger.Info(self.globalVarsObj.TAG, "Time Diff List: {0}".format(self.globalVarsObj.timeDiffList))

    DiagLib.GetHybridBlockCounterValues(vtfContainer)
    DiagLib.GetHoutCountStatistics(vtfContainer)


def LbasToGB(self, lbas):
    return float(old_div((lbas * 512), (Constants.GB)))


class RegisterWaypoint(object):
    """
    Description:
       * Class to register TWO_PASS_PARAMETERS waypoint
    """
    # Initializing the static variables
    __static_objOfThisClass = None

    def __init__(self, testSpace, fileDataObj, logger):
        """
        Description:
           * Constructor of the class TestProcedure.
           * Initializes all the variables.
        """
        self.livet  = testSpace._livet
        self.logger = logger
        self.regEventKey = self.livet.RegisterFirmwareWaypoint("TWO_PASS_PARAMETERS", None)
        self.regEventKey = self.livet.RegisterFirmwareWaypoint("TWO_PASS_PARAMETERS", self.__class__.OnTwoPassParameters)
        assert (self.regEventKey > 0 )  ,"Invalid Registered Event Key [%d]"%(self.regEventKey)
        logger.Info("", "Waypoint for the event TWO_PASS_PARAMETERS has been registered successfully (Reg event key value = %d)"%(self.regEventKey))
        self.expectedArray = [fileDataObj.twoPassTempPara1,fileDataObj.twoPassTempPara2,fileDataObj.twoPassTempPara3,fileDataObj.twoPassTempPara4,\
                                fileDataObj.twoPassTempPara5,fileDataObj.twoPassTempPara6,fileDataObj.twoPassTempPara7,fileDataObj.twoPassTempPara8,\
                                fileDataObj.twoPassTempPara9,fileDataObj.twoPassTempPara10,fileDataObj.twoPassTempPara11,fileDataObj.twoPassTempPara12,\
                                fileDataObj.twoPassTempPara13]
        logger.Info("", "File 21 parameters corresponding to two pass programming = %s"%(self.expectedArray))
        self.receivedArray = []
        RegisterWaypoint.__static_objOfThisClass = self



    @staticmethod
    def OnTwoPassParameters(eventKey, args, processorID):
        """
        Description: Parameter used form config file
        """
        RegisterWaypoint.__static_objOfThisClass.logger.Info("", "TWO_PASS_PARAMETERS : 0x%X"%(args[0]))
        RegisterWaypoint.__static_objOfThisClass.receivedArray.append(args[0])

        if len(RegisterWaypoint.__static_objOfThisClass.receivedArray) > len(RegisterWaypoint.__static_objOfThisClass.expectedArray):
            RegisterWaypoint.__static_objOfThisClass.receivedArray = []
            RegisterWaypoint.__static_objOfThisClass.receivedArray.append(args[0])

        return True


def GetRandomSeed(startRandomSeed = None):
    """
    This function generates a randomSeed depend on previous randomSeed
    """
    randObj    = random.Random(startRandomSeed)
    randomSeed = randObj.randint(1,MAX_RANDOM_SEED)
    return randomSeed

class TestRunAttributes(object):
    """
    class used for maintaining Cycle count and test durations
    """

    import time as time
    IGNORE_TIME = False

    #Create Static Validation Space Object
    __static_ObjTestRunAttributes             = None
    __static_TestRunAttributesObjectCreated   = False

    def __new__(cls, *args, **kwargs):
        """
           Memory allocation ( This function use to create Singleton object of TestRunAttributes)
        """
        if not TestRunAttributes.__static_ObjTestRunAttributes:
            TestRunAttributes.__static_ObjTestRunAttributes = super(TestRunAttributes, cls).__new__(cls)
        return TestRunAttributes.__static_ObjTestRunAttributes
    #end of __new__


    IS_FIRST_CYCLE = True  # Flag to indicate first cycle
    def __init__(self,cycleCount = None,testDuration = None,
                 logger = None,testName = None):
        """
        Name : __init__()
        Description :
                  Constructor of the class
        Arguments :
                cycleCount     : The number of times to run a test
                      None : Infinite time
                      +ve  : test will run as specified

                testDuration : Its s string argument to tell the maximum duartion of test
                                If it is None test duration is taken as infinite time
                                If the testDuration is int of long, it means the value given in seconds

                logger      : logger is used to put logger comments in
                testName    : test Name is used in logger
        Return  :
            None
        """
        #check if the variable is already created
        if TestRunAttributes.__static_TestRunAttributesObjectCreated :
            #return TestRunAttributes.__static_ObjTestRunAttributes
            return
        #condition to check if the variable is already created

        #Set the static variable of class such that we the object has created once
        TestRunAttributes.__static_TestRunAttributesObjectCreated = True
        #logger
        self.__isLoggerEnabled = False
        if logger is not None:
            self.__isLoggerEnabled = True

        self.__logger    = logger
        self.__testName  = testName

        #initialise all veribles
        self.currentCycleCount = 0
        #Get Test cout and test duration
        ##(self.__infiniteCycleFlag, self.__numOfCyclesToTest) = self.DecodeNumOfCycles(cycleCount)
        self.__timeDurationInSec = self.DecodeTestDuration(testDuration)

        #Get Start Time
        self.__starTime =  self.time.time()

        #Put Logger Comments
        if self.__isLoggerEnabled:
            if self.__timeDurationInSec is None:  ##self.__infiniteCycleFlag and
                self.__logger.Info("","[%s]  Will run for infinite count and Infinite Time"%(self.__testName))
            ##if not self.__infiniteCycleFlag:
                ##self.__logger.Info("[%s]  Will run for %d count(s) "%(self.__testName,self.__numOfCyclesToTest))
            if self.__timeDurationInSec is not None:
                self.__logger.Info("","[%s]  Will run for %d seconds(s) "%(self.__testName,self.__timeDurationInSec))



    #end of __init()__

    def DecodeNumOfCycles(self,numOfCycles):
        """
        Name : DecodeNumOfCycles
        Description :
                  Check for number of times to run a test
        Arguments :
                numOfCycles : The number of times to run a test
                   None : Infinite time
                   +ve  : test will run as specified

        Return
          infiniteCycleFlag   :
                         True  : test will run for Infinite nymber of cycles
                         False : test will run for specific number of cycles

          numOfCyclesToTest : Total number of cycles to run the test cycle
        """
        if numOfCycles is not None:
            assert type(numOfCycles) in (int,int),"Cycle count should be a integer number"
            assert numOfCycles > 0 ,"cycle count must be greater than 0"

        numOfCyclesToTest = 0
        infiniteCycleFlag = False
        if(numOfCycles == None):
            infiniteCycleFlag = True

        #if numberOfCycle is +v then it taken as the same
        elif(numOfCycles >=0):
            numOfCyclesToTest = numOfCycles

        return (infiniteCycleFlag, numOfCyclesToTest)
    #end of DecodeNumOfCycles()

    def DecodeTestDuration(self, testDuration):
        """
        Name :  DecodeTestDuration
        Description :
                   Check the test duration  in seconds for test has to run
        Arguments :
                testDuration : Its s string argument to tell the maximum duartion of test
                               If it is None test duration is taken as infinite time
                               If the testDuration is int of long, it means the value given in seconds

        Return
          timeDurationInSec   :  time duration of test in seconds

        """

        timeDurationInSec = None
        starTime          = None
        if(testDuration is not None):
            if type(testDuration) in  ( int, int ):
                timeDurationInSec = testDuration
            else:
                timeDurationInSec = GetNumberOfSecondsFromTimeString(testDuration)
        #end of if test duration is not none

        return(timeDurationInSec)
    #end of DecodeTestDuration()

    def UpdateTestDuration(self, testDuration):
        """
        Name :  UpdateTestDuration
        Description :
                   Update the test duration  in seconds for test to run
        Arguments :
                testDuration : Its s string argument to tell the maximum duartion of test
                               If it is None test then assert
                               If the testDuration is int of long, it means the value given in seconds

        Return
          None

        """
        assert testDuration >0 , "test duration is less than 0 "

        timeDurationInSec = None
        self.__starTime = self.time.time() #Reseting the Starttime.
        if type(testDuration) in  ( int, int ):
            timeDurationInSec = testDuration
        else:
            timeDurationInSec = GetNumberOfSecondsFromTimeString(testDuration)

        self.__timeDurationInSec = (timeDurationInSec)
        return
    #end of UpdateTestDuration()

    def GetRemainingTimeInSeconds(self):
        """
        Name :  GetRemainingTimeInSeconds
        Description :
                   Returns the time remained to stop in seconds. In case of infinite time it return None
                   If return negative number it means, the time has already elapled
        Arguments :
           None

        Return
          timeRemainedinSec  : time remained in seconds
        """
        timeRemainedinSec = None
        if(TestRunAttributes.IGNORE_TIME):
            return 1 # Non zero Value to enusre the test continues
        if not self.__timeDurationInSec is None:
            timeElapsedInSec = self.time.time()- self.__starTime
            timeRemainedinSec = max(int(self.__timeDurationInSec - timeElapsedInSec),0)

        #return the timeRemainedinSec
        return timeRemainedinSec

    #end of GetRemainingTimeInSeconds()

    def GetCurrentCycleCount(self):
        """
        Name :  GetCurrentCycleCount
        Description :
                   Returns the current cycle count number
        Arguments :
           None

        Return
          currentCycleCount  : cycle count number
        """

        #return the currentCycleCount
        return self.currentCycleCount

    #end of GetRemainingTimeInSeconds()

    def IsTestTimeAndCycleCountOver(self,inceaseCount = True):
        """
         Name :  IsTestTimeAndCycleCountOver
         Description :
                    Check whether the time or cycle count has elapsed for the test
         Arguments :
                 inceaseCount  : the flag saying that increase the current cycle count before checking

         Return
           True  : if test is over
           False : if test is not over
         """
        # Reset the flag if it is not the first cycle
        if self.currentCycleCount > 0:
            TestRunAttributes.IS_FIRST_CYCLE = False

        #increase the current cycle count if required
        if inceaseCount :
            self.currentCycleCount += 1

        #check for infinite run
        if self.__timeDurationInSec is None :   ##self.__infiniteCycleFlag and
            return False

        #check for the cycle count
        ##if not self.__infiniteCycleFlag and (self.currentCycleCount > self.__numOfCyclesToTest):
            ###Put Logger Comments
            ##if self.__isLoggerEnabled:
                ##self.__logger.Info("[%s]  Has stoppeed as total count(s) [%d] has exausted  "%(self.__testName,self.__numOfCyclesToTest))
                ##if inceaseCount :
                    ##self.currentCycleCount -= 1
            ##return True

        #check for time duration
        if (self.__timeDurationInSec is not None) and self.GetRemainingTimeInSeconds() <=0:
            #Put Logger Comments
            if self.__isLoggerEnabled:
                self.__logger.Info("","[%s]  Has stoppeed as total time [%d seconds] has exausted  "%(self.__testName,self.__timeDurationInSec))

            #Harish - Decrease the count, since the time is over and we are not running the next cycle, and it is already incremented
            #RPG-18233
            if inceaseCount :
                self.currentCycleCount -= 1
            return True

        #In other cases return False
        return False
    #end of IsTestTimeAndCycleCountOver
#end of class TestRunAttributes

def DumpCaptureStopAndNSVSequenceCheckStart(vtfContainer,disableNSV = False):
    if vtfContainer.cmd_line_args.nsv == True:
        import NSVUtils as NSVUtils
        nsvUtils = NSVUtils.NSVUtils(vtfContainer)
        livet = vtfContainer.GetLivet()
        livet.VcdDump(0)

        #self.globalVarsObj.nsvUtilsObj.Dump_to_txt_part_alone()  #added this fn call since MS team asked only for dumps with NSV disabled.
        nsvUtils.CallNSVAnalyzerNPrint()
    if disableNSV:
        vtfContainer.cmd_line_args.nsv = False

def DumpCaptureStartByEnablingNSV(vtfContainer,enableNSV=False):
    if enableNSV:
        vtfContainer.cmd_line_args.nsv = True
    if vtfContainer.cmd_line_args.nsv == True:
        livet = vtfContainer._livet
        flashObj = livet.GetFlash()

        # model debug trace
        flashObj.TraceOn("stm_debug")
        livet.VcdDump(1)

def getDirSize():
    totalSize = 0
    for dirpath, dirnames, filenames in walk(getcwd()):
        for f in filenames:
            if f.endswith(".tmp"):
                fp = path.join(dirpath, f)
                if not path.islink(fp):
                    totalSize += path.getsize(fp)
    return totalSize
