"""
class ValidationSpace
@ Shaheed Nehal A
@ copyright (C) 2022 Western Digital Corporation
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    pass # from builtins import str
    from builtins import range
    pass # from builtins import *
    from builtins import object
import Core.ValidationError as ValidationError
import Utils
import DiagnosticLib
import FwConfig
from datetime import datetime
import SDCommandWrapper as SDWrap
import EIMediator
import random
import SDDVT.Common.SDCommandLib as SDCommandLib
#import SdCommands.SdCommandLibViaLivet as SDCommandLibModel

class ValidationSpace(object):
    """
    Validation Space contain all the object related to Test (For example TestSpace, optionValues, dbHandle,validaationRWC and many more).
    It also contain API like Download and Format.

    Some Notes while using validation Space class:
        1. The validation Space is Singleton class. It means, if object is created once then same object will be return next time.
           User can import this file (ValidationSpace.py) and create this object any where in any script.
           --> Its strictly recommonded that validation Space object must not be created in libraried in "ValidationSpaceLib".

        2. The object of validation Space will never die till end of test. (Similarly logger,optionValues and dbHandle object also never die till end of test)
           The object of validation Space,logger and dbHandle will never be effected due to download and Format.
        3. The objects optionValues, logger, testSpace and dBHandle, initialized in SetupTestEnvironment() method.
        4. The object related "ValidationSpaceLib" folder libraries must be accessed via validationSpace object.
            (For example GetValidationRwcObj() method used to get validationSpace object)
            All object of  "ValidationSpaceLib" folder libraries (except FwConfig) are lazy initialized. Such that validationSpace will never create the object unless user query for it.
           --> Its is strictly recommonded that user must not create the object of "ValidationSpaceLib" folder libraries.
        5. The download and format function invalidate the testSpace object and create new testSpace object.
        6. The download and format function also invaldate the object related to "ValidationSpaceLib" folder libraries. As they all depends on testSpace.
        7. The user can get updated testSpace object by using GetvtfContainer() method.

    """
    import CardRawOperations as __CardRawOperations
    import FwConfig as __FwConfig
    import LegacyRWLib as __ValidationRwcLib
    import AddressTranslation as __AddressTranslation
    #import ValidationSpaceLib.SDFS as __SDFS
    import os as __os


    #Cteate Static Validation Space Object
    __static_ObjValidationSpace             = None
    __static_validationSpaceObjectCreated   = False

    def __new__(cls, vtfContainer, *args, **kwargs ):
        """
           Memory allocation ( This function use to create Singleton object of ValidationSpace)
        """
        if not ValidationSpace.__static_ObjValidationSpace:
            ValidationSpace.__static_ObjValidationSpace = super(ValidationSpace, cls).__new__(
               cls, *args, **kwargs)
        return ValidationSpace.__static_ObjValidationSpace
    #end of __new__

    def __init__(self, vtfContainer):
        """
        Constructor of Validation Space Class
        """
        #check if the variable is already created
        if ValidationSpace.__static_validationSpaceObjectCreated :
            return
        #condition to check if the variable is already created

        #Set the static variable of class such that we the object has created once
        ValidationSpace.__static_validationSpaceObjectCreated = True

        #member which will remain constant in entire test run
        self.vtfContainer = vtfContainer
        self.__optionValues = self.vtfContainer.cmd_line_args
        self.logger         = self.vtfContainer.GetLogger()
        self.__randomObj    = random.Random(self.vtfContainer.cmd_line_args.randomSeed)
        self.__fwConfigData = None

        self.InitVars()

        self.errorManager = self.vtfContainer.device_session.GetErrorManager()
        ret = self.errorManager.RegisterCallback(self.ErrorHandlerFunction)
        if ret:
            self.logger.Info("", "[ValidationSpace] CVF ErrorHandler callback registered")

        #self.livet = self.vtfContainer._livet
        #self.livet.UnregisterLivetCallback(self.livet.lcCrash)
        #self.livet.RegisterLivetCallback(self.livet.lcCrash, self.__class__.LivetCrashHandler)

        self.configParser = self.vtfContainer.device_session.GetConfigInfo()
        self.expectedROModeOccurred = False
        self.expectedUECC = False
        self.expectedFuleError = False
        self.readFailed= False
        self.expectedSEDISR = False
        self.expectedSCTPFailure = False
        self.expected_BE_ERROR_Failure = False
        self.SDCmdFailed = False
        self.expectedIllegalCmd = False
        self.expectedEraseReset = False
        self.expectedEraseSeqError = False
        self.expectedOutOfRangeError = False
        self.expectedGeneralError = False
        self.expectedWatchdogTimeout = False
        self.clearexpectedIllegalCmdAfterOneInstance = False
        self.expectedEraseParam= False
        self.expectedWriteProtectViolation = False
        self.CQWAHandlingReqd = False
        self.watchdogTimeoutOccured = False
        self.expectedCardTimeout = False
        self.expectedCardDataStatusCrcError = False

        # Validation Objects
        self.__objCardRawOperation     = None
        self.__objValidationRwc        = None
        self.__objValidationSRW_Rwc    = None
        self.__objAddressTranslation   = None
        #self.__objSDFS                 = None

        #By default enable the full data mode
        self.__isCardInFullDataMode = None

        self.__isLargeMetablockUsed = False

        #------------------------------------Adding TestRunner related initializations------------------------------------#
        Utils.RESET_TIMEOUT = int(vtfContainer.cmd_line_args.init_timeout)
        Utils.WRITE_TIMEOUT = int(vtfContainer.cmd_line_args.write_timeout)
        Utils.READ_TIMEOUT = int(vtfContainer.cmd_line_args.read_timeout)

        #To recheck - To be added when SDRMode changes are pulled - Anamika
        Utils.BUS_WIDTH= vtfContainer.cmd_line_args.busWidth
        Utils.SETFREQ=vtfContainer.cmd_line_args.setFreq
        #Utils.TRANSFER_MODE=vtfContainer.cmd_line_args.mode
        #Utils.STOP_CMD = vtfContainer.cmd_line_args.stopCmd
        #Utils.PRINT_PGC = vtfContainer.cmd_line_args.printPGC
        #if vtfContainer.cmd_line_args.voltage:
            #Utils.VOLTAGE=vtfContainer.cmd_line_args.voltage

        if not self.__optionValues.romMode:
            if self.vtfContainer.cmd_line_args.CQ or self.vtfContainer.cmd_line_args.cqWrites or self.vtfContainer.cmd_line_args.cqReads:
                Utils.availableSdConfigurations.remove("DDR200")
                Utils.availableSpeedModes.remove("DDR200")
                if not self.vtfContainer.isModel:
                    self.expectedWatchdogTimeout = True #refer RPG-53728

            if vtfContainer.isModel:
                Utils.SetTimeOut(self.vtfContainer, Utils.RESET_TIMEOUT,Utils.WRITE_TIMEOUT,Utils.READ_TIMEOUT)

                #If --sdrMode is not passed in cmdline, randomly pick the sdrMode
                if self.__optionValues.sdrMode == None:
                    self.__optionValues.sdrMode = self.__randomObj.choice(Utils.availableSpeedModes)
                    self.logger.Info("", "[ValidationRWCManager] --sdrMode=None, the randomly picked SDR mode is %s"%self.__optionValues.sdrMode)
                Utils.PowerCycle(self.vtfContainer)
                #Utils.SetSDRMode(self.vtfContainer, self.__optionValues.sdrMode, self.__optionValues.selectRandomSdrMode, self.__randomObj)
                Utils.SetHostTurnAroundTime(self.vtfContainer, self.__optionValues.htatValue, self.__optionValues.selectrandomHtatValue, self.__randomObj)

            else:
                #If --sdrMode is not passed in cmdline, randomly pick the sdrMode
                if self.__optionValues.sdConfiguration == None:
                    self.__optionValues.sdConfiguration = self.__randomObj.choice(Utils.availableSdConfigurations)
                    self.logger.Info("", "[ValidationRWCManager] --sdConfiguratione=None, the randomly picked SDConfiguration is %s"%self.__optionValues.sdConfiguration)
                self.__sdlibObj    = SDCommandLib.SdCommandClass(vtfContainer)
                self.__sdlibObj.DoBasicInit()

        #------------------------------------Adding TestRunner related initializations------------------------------------#
        Utils.numberOfDiesInTheCard = self.__optionValues.numberOfDiesInCard

        if self.__optionValues.enableCmdQueue == True:
            Utils.enableCmdQueue = True

        if self.__optionValues.switchCmdQueue == True:
            Utils.switchCmdQueue = True

        if not self.__optionValues.romMode:
            self.SetupTestEnvironment()

        self.logger.BigBanner("Start of Device Information")
        self.logger.Info("", "Device Capacity:  {0} GB".format(int(SDWrap.WrapGetCardCapacity()[:-2])))
        self.logger.Info("", "Max LBA: 0x%X"%(SDWrap.WrapGetMaxLBA()-1))
        self.__fwFeatureObj = FwConfig.FwFeatureConfig(self.vtfContainer)
        self.logger.SmallBanner("End of Device Information")

        #DATA TRACKING Pattern dict initialisation
        self.livetErrorDataPattern ={ 3: "Unpredictable", 4: "UECC" , 5: "UnpredictableUECC"}

    #end of constructor

    ###################################################################################################
    ##################   Methods related that called only once (Starting of test)       ###############
    ###################################################################################################

    def InitVars(self):
        #Setting the global variables in Utils
        Utils.RESET_TIMEOUT = int(self.__optionValues.init_timeout)
        Utils.WRITE_TIMEOUT = int(self.__optionValues.write_timeout)
        Utils.READ_TIMEOUT = int(self.__optionValues.read_timeout)

        #To recheck - Anamika
        Utils.BUS_WIDTH= self.__optionValues.busWidth
        Utils.SETFREQ= self.__optionValues.setFreq
        #Utils.TRANSFER_MODE=self.__optionValues.mode
        #Utils.STOP_CMD = self.__optionValues.stopCmd
        #Utils.PRINT_PGC = self.__optionValues.printPGC
        #if self.__optionValues.voltage:
            #Utils.VOLTAGE=self.__optionValues.voltage

        #Stats related variables
        self.writeCommandCount = 0
        self.readCommandCount = 0
        self.eraseCommandCount = 0
        self.totalIOCommandCount = 0
        self.totalSectorsRead = 0
        self.totalSectorsWritten = 0
        self.numberOfCommands = 0
        self.IOPS = 0.0
        self.teraBytesWritten = 0.0
        self.teraBytesRead = 0.0
        self.bandwidth = 0.0
        self.totalSectorsWritten = 0
        self.totalSectorsRead = 0
        self.startTime = datetime.now()

    def SetupTestEnvironment(self,testDescription = "",extraHelpString ="", setTestSpaceWithOutCardInfo = False):
        """
        Name       :    SetupEnvironment
        Description:    Sets the environment for the running of the test.
                          1. It Process the command line option
                          2. Create logger object
                          3. Create testSpace Object
                          4. Setup the dependent variables on testSpace
                          5. Setup the data base object
        Arguments  :
           testDescription    : Test Descriotion String
           extraHelpString    : Extra Help string for Command Line arguments
        Returns:
           None
        """
        if(self.__optionValues.scaledownEnabled):
            self.logger.Info("", "Sending Diagnostic to Invalidate Extra MLC blocks")
            DiagnosticLib.Purge_MLC_Blocks(self.vtfContainer, self.__optionValues.spareBlockCount)
            Utils.PowerCycle(self.vtfContainer)

        if DiagnosticLib.IsLargeMetablockUsed(self.vtfContainer)[0]:
            self.__isLargeMetablockUsed = True

        # To set the FW stats dump on model only
        if self.vtfContainer.isModel:
            DiagnosticLib.DumpFWDebugDataSetpath(self.vtfContainer)

        #Added for PM01
        if not setTestSpaceWithOutCardInfo:
            #setup variable depends on testSpace
            self.__SetupVariablesDependOnTestSpace()
        self.__OperationsHasToPerFormDuringCardInit()

        return
    # end of SetupTestEnvironment()


    def IsCardInFullDataMode(self):
        """
        This Function return flag if the card in Full data mode
        Note: this function should be called after the testSpace creation
        """
        assert self.__isCardInFullDataMode is not None
        return self.__isCardInFullDataMode
    #end of IsCardInFullDataMode

    ###################################################################################################
    ##################   Methods which return a object related to validationSpace       ###############
    ###################################################################################################

    def GetvtfContainer(self):
        """
        This Function Return the testSpace if the testSpace is Intialized.
        This function always return the updated testSpace object
        See Also:
           SetupTestEnvironment()
           DoDownLoadAndFormat()
        """
        assert self.vtfContainer is not None, "testSpace is not initialised yet"

        #To recheck
        #if self.__isLargeMetablockUsed == True:
            #self.__ValidationConfig.FW_FS_CONFIG=self.__ValidationConfig.FW_VALIDATION_PATH +'\Validation\FS_CONFIG_LARGEMB.ini'
        return self.vtfContainer
    #end of GetTestSpace

    def GetFWConfigData(self):
        """
        This Function Return the FW config object. That object contais all the information related to Firmware that will not change till end of FW life (download)
        """
        assert self.__fwConfigData is not None, "fwConfigData is not initialised yet"
        return self.__fwConfigData
    #end of GetFWConfigData


    def GetOptionValues(self):
        """
        This Function Return process command line arguments
        See Also:
           ProcessCommandLineOptions()
           SetupTestEnvironment()
        """
        assert self.__optionValues is not None, "optionValues is not initialised yet"
        return self.__optionValues
    #end of GetOptionValues

    ###################################################################################################
    ##################   Methods which return a object related to ValidationSpaceLib    ###############
    ###########################  All these objects are lazy initialized ###############################
    ###################################################################################################

    def GetLegacyRWLibObj(self,
                          maxLba = None,
                          lbaRanges = [(0,-1)],
                          maxTransferLength=0x80,
                          usePatternGen=False,
                          patternToBeUsed=None,
                          writePattern=1):
        """
           This function creates the object of ValidationSpaceLib\ValidationRwcLib.
           This function takes all the arguments related to ValidationSpaceLib\ValidationRwcLib (except Full data mode)
        """
        #create the object if it is not created earlier
        if self.__objValidationRwc is None:
            if maxLba == None:
                maxLba = self.__fwConfigData.maxLba
            #??? Created Card MAP out side of Validation library.
            self.__objValidationRwc = self.__ValidationRwcLib.LegacyRWLib(self.vtfContainer,
                                                                          maxLba,\
                                                                          lbaRanges, \
                                                                          maxTransferLength,
                                                                          usePatternGen=usePatternGen,
                                                                          patternToBeUsed=patternToBeUsed,
                                                                          writePattern=writePattern)
            #end of creation o object
            #end of check if object is already created
        return self.__objValidationRwc
    #end of GetValidationRwcObj


    def GetValidationSRW_RwcObj(self,
                                maxTransferLength = 0x80,
                                erasePattern = 0,
                                randomSeed = None,
                                paramsfilepath = None):
        """
           This function creates the object of ValidationSpaceLib\ValidationSRW_RWCLib.
        """
        #create the object if it is not created earlier
        if self.__objValidationSRW_Rwc is None:

            #Create the object of SRW
            self.__objValidationSRW_Rwc = self.__ValidationSRW_RWCLib.ValidationSRW_Rwc(testSpace = self.GetvtfContainer(),
                                                                                        maxTransferLength = maxTransferLength,
                                                                                        erasePattern = erasePattern,
                                                                                        randomSeed = randomSeed,
                                                                                        paramsfilepath = paramsfilepath)
            #end of creation o object
        #end of check if object is already created

        return self.__objValidationSRW_Rwc
    #end of GetValidationSRW_RwcObj


    def GetCardRawOperationObj(self):
        """
           This function creates the object of ValidationSpaceLib\CardRawOperations.
           This function takes all the arguments related to ValidationSpaceLib\CardRawOperations
        """
        #create the object if it is not created earlier
        if self.__objCardRawOperation == None:
            self.__objCardRawOperation = self.__CardRawOperations.CardRawOperations(testSpace = self.GetvtfContainer(),
                                                                                    fwConfigData = self.GetFWConfigData(),
                                                                                    addrTransObj = self.GetAddressTranslationObj())
        #end of check if object is already created
        return self.__objCardRawOperation
    #end of GetCardRawOperationObj

    def GetSDFSObj(self):
        """
           This function creates the object of ValidationSpaceLib\SDFS.
           This function takes all the arguments related to ValidationSpaceLib\SDFS
        """
        #create the object if it is not created earlier
        if self.__objSDFS == None:
            self.__objSDFS = self.__SDFS.SDFS(testSpace = self.GetvtfContainer(),
                                              fwConfigData = self.GetFWConfigData(),
                                              objCardRawOperation = self.GetCardRawOperationObj(),
                                              addrTransObj = self.GetAddressTranslationObj())
        #end of check if object is already created
        return self.__objSDFS
    #end of GetCardRawOperationObj

    def GetAddressTranslationObj(self):
        """
           This function creates the object of ValidationSpaceLib\AddressTranslation.
           This function takes all the arguments related to ValidationSpaceLib\AddressTranslation
        """
        #create the object if it is not created earlier
        if self.__objAddressTranslation == None:
            self.__objAddressTranslation = self.__AddressTranslation.AddressTranslator(testSpace = self.GetvtfContainer(),
                                                                                       fwConfigData = self.GetFWConfigData())
        #end of check if object is already created
        return self.__objAddressTranslation
    #end of GetAddressTranslationObj

    ##################################################################################################
    #########################           Statistical APIs          ####################################
    ##################################################################################################
    def GetAndPrintWriteStatistics(self):
        """
        This API prints and return the write amplification statistics
        """
        if self.__objValidationRwc != None:
            return self.__objValidationRwc.GetAndPrintWriteStatistics()
        else:
            self.logger.Info("", "[ValidationSpace] ValidationRwcLib needs to be initialized before calling GetAndPrintWriteStatistics" )
    #End of GetAndPrintWriteStatistics

    ###################################################################################################
    ##################   Methods related to some operations (e.g.DownLoad and Format )    ###############
    ###################################################################################################

    def DoDownLoadAndFormat(self,botFilename = None,
                            paramsFile=None,
                            trimfile = None,
                            trimMethod = "ref",
                            multitrim = "yes",
                            DCF="",
                            maxLba=0,
                            doAlt = False,
                            altRetries = 0x100,
                            altOptions = 0,
                            productFam="", secure=False):

        """
         Name               -  DoDownLoadAndFormat()
         Description        - This function do download on hardware and Model both. It Invalidate the testSpace and its depended object.
         Arguments:
           botFilename      - Path of the BOT file
           paramsFile       - Parameter file path,
           DCF              - bad bloack File used to markBadBlock
           maxLba           - maxLba of the card to set during format
           doAlt            - Ferporm Address Line Test (ALT) during Download,
           altRetries       - Number of ALT retries
           altOptions       - ALT options
        Returns:
            None
        See Also:
           SetupTestEnvironment()
           __SetupVariablesDependOnTestSpace()
           __DownloadOnModel()
           __DownloadOnHardware()
        """
        #RPG-49719 : Clear all errors before doing DownloadAndFormat() as the new instance should have no errors
        if self.errorManager.GetPendingExceptionList() != []:
            self.vtfContainer.CleanPendingExceptions()

        if self.vtfContainer.isModel:   
            self.__DownloadOnModel(botFilename,DCF,maxLba)
            if botFilename != None:
                self.configParser.SetValue("bot_file", botFilename)            
            import Production_SD
            self.productionObj = Production_SD.ModelProduction(self.vtfContainer.device_session, secure=secure)
            
            self.productionObj.Execute()
            
            if secure:
                self.devicechallenge, rsa_key_size = self.productionObj.GetDeviceChallenge(0)
                self.password_hash = self.productionObj.GenerateRMAPin(self.devicechallenge) 
                self.productionObj.SecureUnlock(Production_SD.FromHexStringArrayToByteArray(self.password_hash), 0, rsa_key_size)
                self.productionObj.IdentifyDrive()
            DiagnosticLib.DumpFWDebugDataSetpath(self.vtfContainer)
        else:
            if botFilename is not None:
                self.__DownloadOnHardware(botFilename, paramsFile, trimfile, trimMethod, multitrim, DCF,maxLba,doAlt,altRetries,altOptions,productFam)
            else:
                raise ValidationError.TestFailError(self.vtfContainer.GetTestName(), "[DoDownLoad] For performing download on hardware, bot file is required")

        if not self.__optionValues.romMode:
            self.__SetupVariablesDependOnTestSpace()

    def __CreateTestSpace(self,maxLBA = 0,deviceConfigFile = ""):

        #If DCF not provided, then pick up the same file as in model.ini (This needs to be properly defined always by FW team)
        if deviceConfigFile == "":
            FilePath = ""
            retTuple = self.configParser.GetValue("deviceConfigFile", FilePath)
            deviceConfigFile = retTuple[0]
            self.vtfContainer.GetLogger().BigBanner("Performing ReInit() with the DCF mentioned in model.ini\nDCF- %s"%deviceConfigFile)

        self.vtfContainer.device_session.GetConfigInfo().SetValue("device_configuration_file",deviceConfigFile)
        try:
            self.vtfContainer.device_session.ReInit("protocol")
        except:
            raise ValidationError.TestFailError(self.vtfContainer.GetTestName(), "DoDownloadAndFormat (ReInit()) failed")

        #To recheck - Read and verify needed here?
        Utils.CalculateStatistics(self.vtfContainer)

        #Initialise all the variables
        self.InitVars()

        #Attaching new Livet handle as ReInit() destroys previous handle
        self.vtfContainer._livet.Attach(self.vtfContainer.device_session.GetModelDllHandle())

    def __DownloadOnModel(self,
                          botFilename = None,
                          badBlockFilePath = "",
                          maxLba=0):
        """
         Name               - __DownloadOnModel()
         Description        - This function do download on Model

         Arguments:
           botFilename      - Path of the BOT file
           badBlockFilePath - bad bloack File used to markBadBlock
           maxLba           - maxLba of the card to set during format
        Returns:
            None
        """
        assert self.vtfContainer.isModel , "DownloadOnModel() function is applicable only for Model Protocol "

        self.__CreateTestSpace(maxLba,deviceConfigFile = badBlockFilePath)

    def __DownloadOnHardware(self,
                             botFilename,
                             paramsFile=None,
                             trimfile = None,
                             trimMethod = "ref",
                             multitrim = "yes",
                             badBlockFilePath=None,
                             maxLba=None,
                             doAlt = False,
                             altRetries = 0x100,
                             altOptions = 0,
                             productFam = ""):
        """
         Name               -  __DownloadOnHardware()
         Description        - This function do download on hardware

         Arguments:
           botFilename      - Path of the BOT file
           paramsFile       - Parameter file path,
           badBlockFilePath - bad bloack File used to markBadBlock
           maxLba           - maxLba of the card to set during format
           doAlt            - Ferporm Address Line Test (ALT) during Download,
           altRetries       - Number of ALT retries
           altOptions       - ALT options
        Returns:
            None
        """
        #????? check use of maxLba in download on hardware

        import Card.DownloadChorus.DownloadChorus as DownloadChorus
        import CardFramework.TestSpace as TestSpaceCreationFile
        import string
        lineLength=80
        star="*"
        retValue  = 0


        self.logger.Warning("", star*lineLength+"\n")
        self.logger.Warning("", string.center("CALLING DOWNLOAD AND FORMAT", lineLength,star))
        self.logger.Warning("", "\n"+star*lineLength)

        #creating the download string argument
        dowloadString = ""

        #add protocol in download string
        protocol=str(self.card.GetProtocol())
        dowloadString += "--protocol=%s"%protocol

        #add adapter in download string
        adapter=str(self.adapter.GetAdapterIndex())
        dowloadString += " --adapter=%s"%adapter

        #add botfile path in download string
        dowloadString += " --botfilename=%s"%botFilename

        #add logger file in download string
        logfilename= self.logger.GetLogFilename()
        logfilename= logfilename.replace(".log","_download.log")
        dowloadString += " --logfilename=%s"%logfilename

        #add serial number in download string
        serialNumber = self.card.GetCardInfo().GetSerialNumber()
        dowloadString += " --iddriveserial=%s"%str(serialNumber)

        #add parameter file path in download string (if given)
        if paramsFile:
            dowloadString += " --paramsfile=%s"%paramsFile
        #add trimMethod in download string (if given)
        if trimMethod:
            dowloadString += " --trimMethod=%s"%trimMethod
        #add trimMethod in download string (if given)
        if multitrim:
            dowloadString += " --multitrim=%s"%multitrim
        #add trimMethod in download string (if given)
        if trimfile:
            dowloadString += " --trimfile=%s"%trimfile
        #add badbloack file path in download string (if given)
        if badBlockFilePath:
            dowloadString += " --badBlockEntryFile=%s"%badBlockFilePath

        dowloadString += " --productFam=%s"%productFam

        #add ALT testing in download string (if ALT flag is enabled)
        if doAlt:
            #set ALT enabled
            dowloadString += " --alt=yes"
            #set the alt retries
            dowloadString += " --altretries=%d"%altRetries
            #Set ALT Options
            dowloadString += " --altoptions=%d"%altOptions
            if self.__optionValues.altnumofbanks == 0:
                #Get the number of banks
                import CardLib.CardData
                data = CardLib.CardData.CardData( self.vtfContainer )
                numofBanks = data.NumOfBanks
            else:
                numofBanks = self.__optionValues.altnumofbanks
            dowloadString += " --altnumberofbanks=%d"%numofBanks

        #check for ALT
        #end of download string formation

        try:
            #Perform Download and Format
            DownloadChorus.FWDownload(dowloadString,self.logger,self.vtfContainer)
            #Get the updated testSpace
            self.vtfContainer = TestSpaceCreationFile.GetCurrent()
            #Do power cycle
            self.vtfContainer.GetAdapter().PowerCycle()
            Utils.PowerCycle(testSpace=self.vtfContainer)


        except OSError:
            self.logger.Critical("[DownloadOnHardware] OsError: No such file or directory")
            retValue =1
            raise

        except KeyboardInterrupt:
            self.logger.Critical("[DownloadOnHardware] KeyboardInterrupt: Download Interrupted")
            retValue =1
            raise

        except:
            self.logger.Critical("[DownloadOnHardware] Download Failed")
            retValue =1
            raise

        self.logger.Warning("", star*lineLength+"\n")
        self.logger.Warning("", string.center("COMPLETED DOWNLOAD AND FORMAT", lineLength,star))
        self.logger.Warning("", "\n"+star*lineLength)

        return
    #End of __DownloadOnHardware()


    def GetAndPrintHCOfAllBlocks(self):
        """
        This API prints and return the write amplification statistics
        """
        self.logger.Info("", "Printing Hotcount of all MetaBlocks....")
        totalMetaBlocksInCard = self.__fwConfigData.totalMetaBlocksInCard
        hotCountArray = DiagnosticLib.GetHotCountofAllBlks(self.vtfContainer, totalMetaBlocksInCard, self.__fwConfigData.numberOfMetaPlane)
        for blk in range(0, totalMetaBlocksInCard):
            self.logger.Info("", "MB Num = 0x%X, Hot Count is=0x%X" %(blk,hotCountArray[blk]))
        return
    #End of GetAndPrintHCOfAllBlocks

    def __SetupVariablesDependOnTestSpace(self):
        """
         Name               -  __SetupVariablesDependOnTestSpace()
         Description        - This function will setup all variables of Validation Space which are dependent on testSpace
         Arguments:
            None
        Returns:
            None
        See Also:
           SetupTestEnvironment()
           DoDownLoadAndFormat()
           __DownloadOnModel()
           __CreateTestSpace()

        """
        #setup card physical and logical info
        self.__fwConfigData = self.__FwConfig.FwConfig(self.vtfContainer)

        if (self.__objValidationRwc is not None):
            self.__objValidationRwc = None #Since the card is being re-downloaded. All the data and instance saved from the previous run
                                           #needs to be cleared to ensure it does not interfere with the current run.

        self.__objCardRawOperation     = None
        self.__objAddressTranslation   = None
        #self.__objSDFS                 = None
    #end of __SetupVariablesDependOnTestSpace

    def __OperationsHasToPerFormDuringCardInit(self):
        if self.vtfContainer.isModel:
            if self.__optionValues.fullDataMode == True:
                raise ValidationError.TestFailError(self.vtfContainer.GetTestName(), "--fullDataMode=1 for model")
            #Set the flag for full data mode
            self.__isCardInFullDataMode = False
        else:
            #Set the flag for full data mode
            self.__isCardInFullDataMode = True

        #Setting the time out
        Utils.SetTimeOut(self.vtfContainer,Utils.RESET_TIMEOUT,Utils.WRITE_TIMEOUT,Utils.READ_TIMEOUT)

        #Read and Verify Grown Bad Block file
        #Utils.ReadAndVerifyGrownBadBlockFile(self.vtfContainer)

        if self.__optionValues.enableCRTrace or self.__optionValues.enableFRTrace or self.__optionValues.enableVCDDump:
            if self.vtfContainer.isModel:
                Livet = self.vtfContainer._livet
                if self.__optionValues.enableCRTrace:
                    self.logger.Warning("", "Enabling CR traces..")
                    Livet.GetController().TraceOn("CR0.log_to_file")
                    Livet.GetController().TraceOn("CR1.log_to_file")

                if self.__optionValues.enableFRTrace:
                    self.logger.Warning("", "Enabling FR traces..")
                    Livet.GetController().TraceOn("FR0.log_to_file")
                    Livet.GetController().TraceOn("FR1.log_to_file")

                if self.__optionValues.enableVCDDump:
                    self.logger.Warning("", "Turning On VCD Dump")
                    Livet.VcdDump(1)
            else:
                self.logger.Warning("", "CR,FR traces and VCD dump can be enabled ONLY on model;\
                 Run the script on model or dont enable the trace flag on HW")
                raise ValidationError.TestFailError(vtfContainer.GetTestName(), "CR,FR traces and VCD dump can be enabled ONLY on model")

        if self.vtfContainer.activeProtocol == "SD":
            if self.__optionValues.setFreq != None:
                #??? SetFrequency is not defined in Utils
                #Utils.SetFrequency(self.vtfContainer,self.__optionValues.setFreq)
                assert 0,"#??? SetFrequency is not defined in Utils"

            if self.__optionValues.busWidth != None:
                #Utils.SetBusWidth(self.vtfContainer,self.__optionValues.busWidth)
                assert 0,"#??? SetBusWidth is not defined in Utils"

    #@staticmethod
    #def LivetCrashHandler(crashMsg):
        #ValidationSpace.__static_ObjValidationSpace.logger.Info("", "[ValidationSpace] [LivetCrashHandler] Livet crashed with the following error message: %s"%(crashMsg))
        #from VtfSmartExecutor import VtfSmartExecutor
        #vtfSmartExec = VtfSmartExecutor
        #vtfSmartExec.ErrorTestCall()

    #Need to check with CVF for more info
    def ErrorHandlerFunction(self,errorGroup, errorCode):
        GRP_ERROR_SD_PROTOCOL = 0xFF3A               #ErrorGroup for SD protocol
        GRP_ERROR_MODEL_EXCEPTION = 0xFF0B           #ErrorGroup for model exceptions

        self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Received error group : 0x%X error code : 0x%X"%(errorGroup, errorCode))

        #RO Mode handling - CVF returns 'GENERAL OR UNKNOWN ERROR' for RO mode
        if self.expectedROModeOccurred or self.expectedGeneralError:
            if errorGroup == GRP_ERROR_SD_PROTOCOL and errorCode == 0x80000:
                self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected RO mode occurred")
                self.vtfContainer.CleanPendingExceptions()
                self.expectedGeneralError = False
                #Not recommended to issue any Diag from Callbacks
                #May lead to unexpected behaviour
                #SpareBlockCountList = DiagnosticLib.GetSpareBlockCount(self.vtfContainer)
                #self.logger.Info("", "SLC Spare Block Count - %d"%SpareBlockCountList[0])
                #self.logger.Info("", "MLC Spare Block Count - %d"%SpareBlockCountList[1])
                #FBLEntryList = DiagnosticLib.GetSpareBlockFBLInfo(self.vtfContainer)
                #self.logger.Info("", "SLC FBL Entries Count - %d"%FBLEntryList[0])
                #self.logger.Info("", "MLC FBL Entries Count - %d"%FBLEntryList[1])
                #SpareBlockListInfo = DiagnosticLib.GetSpareBlockListInfo(self.vtfContainer)
                #self.logger.Info("", "Total spare block count - %s"%str(SpareBlockListInfo[0]))
                #self.logger.Info("", "SLC MBs in FBL - %s"%str(SpareBlockListInfo[1]))
                #self.logger.Info("", "MLC MBs in FBL - %s"%str(SpareBlockListInfo[2]))
                #self.logger.Info("", "MBs in Dedicated FBL - %s"%str(SpareBlockListInfo[3]))
                #import FileData
                #self.__file14Object = FileData.GetFile14Data(self.vtfContainer)
                #self.__numGATBlocks = self.__file14Object['numOfGATBlocks']
                #SPCBlocks = DiagnosticLib.GetSinglePlaneControlBlocksList(self.vtfContainer, self.__fwConfigData, self.__numGATBlocks)
                ##Check if all the blocks are allocated as expected
                #self.mipList  = SPCBlocks[0]
                ##gatBlkList =  SPCBlocks[1]['gatPrimary'] + SPCBlocks[1]['gatSecondary']
                #self.gatBlkList =  SPCBlocks[1]['gatPrimary'] + [SPCBlocks[1]['gatSecondary']]
                #self.gatFblList = SPCBlocks[2]['gatFBLMP0'] + SPCBlocks[2]['gatFBLMP1'] + SPCBlocks[2]['gatFBLMP2'] + SPCBlocks[2]['gatFBLMP3']
                #self.logger.Info("", "SP Control blocks list [Block ID,Plane Number,HotCount]")
                #self.logger.Info("", "SP MIP blocks list: %s"%self.mipList)
                #self.logger.Info("", "SP GAT blocks list: %s"%self.gatBlkList)
                #self.logger.Info("", "SP GAT FBL: %s"%self.gatFblList)

            #RO Mode handling - CVF returns 'GENERAL OR UNKNOWN ERROR' for RO mode
            elif (errorGroup == GRP_ERROR_MODEL_EXCEPTION and errorCode == 0x1):
                self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected RO mode occurred")
                self.vtfContainer.CleanPendingExceptions()
                self.expectedROModeOccurred = False

        if EIMediator.hasWAOccurred:
            if errorGroup == GRP_ERROR_MODEL_EXCEPTION and errorCode == 0x1:
                self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected WA occurred")
                self.errorManager.ClearAllErrors(errorGroup, errorCode)
                EIMediator.hasWAOccurred = False
                if self.__optionValues.CQ or self.__optionValues.cqReads or self.__optionValues.cqWrites:
                    self.CQWAHandlingReqd = True

        if EIMediator.hasEAOccurred:
            if errorGroup == GRP_ERROR_MODEL_EXCEPTION and errorCode == 0x1:
                self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected EA occurred")
                self.errorManager.ClearAllErrors(errorGroup, errorCode)
                EIMediator.hasEAOccurred = False

        if self.expectedSEDISR:
            if errorGroup == GRP_ERROR_MODEL_EXCEPTION and errorCode == 0x1:
                self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected SED ISR occurred")
                self.errorManager.ClearAllErrors()
                self.expectedSEDISR = False

        if self.expectedSCTPFailure:
            if errorGroup == 0xFF0D and (errorCode == 0x2000 or errorCode == 0x2001):
                self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected SED ISR occurred")
                self.errorManager.ClearAllErrors(errorGroup, errorCode)
                #self.expectedSCTPFailure = False # Recheck - Disabling the sctpFailure flag to avoid multiple error calls - oneCVF issue

        #19th bit: BE_Error is expected to be set in CMD13 response (CMD56 ZQ usecase)
        if self.expected_BE_ERROR_Failure:
            isModel = self.vtfContainer.isModel
            if (isModel and errorGroup == GRP_ERROR_SD_PROTOCOL and errorCode == 0x80000 ) or (not isModel and errorGroup == GRP_ERROR_SD_PROTOCOL and errorCode == 0xB):
                self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected SD command failed")
                self.errorManager.ClearAllErrors(errorGroup, errorCode)
                self.expected_BE_ERROR_Failure = False
                self.SDCmdFailed = True

        if self.expectedWatchdogTimeout:
            if errorGroup == GRP_ERROR_SD_PROTOCOL and (errorCode == 0x19):
                self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected Watchdog Reset occurred")
                failureDesc = self.errorManager.GetAllFailureDescription()
                if not self.vtfContainer.isModel and "WATCHDOG_TIME_OUT_FIFO_EMP" not in failureDesc:
                    raise ValidationError.TestFailError(self.vtfContainer.GetTestName(), "[ValidationSpace] [CVF:ErrorHandler] WATCHDOG_TIME_OUT_FIFO_EMP response not received! Actual response = %s"%failureDesc)
                self.watchdogTimeoutOccured = True
                self.errorManager.ClearAllErrors()
                Utils.InsertDelay(250, self.vtfContainer)
                self.__sdlibObj.Cmd13()

            if errorGroup == GRP_ERROR_SD_PROTOCOL and (errorCode == 0x1C):
                self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected Watchdog Reset occurred")
                failureDesc = self.errorManager.GetAllFailureDescription()
                if not self.vtfContainer.isModel and "WATCHDOG_TIME_OUT_FIFO_FULL" not in failureDesc:
                    raise ValidationError.TestFailError(self.vtfContainer.GetTestName(), "[ValidationSpace] [CVF:ErrorHandler] WATCHDOG_TIME_OUT_FIFO_FULL response not received! Actual response = %s"%failureDesc)
                self.watchdogTimeoutOccured = True
                self.errorManager.ClearAllErrors()
                Utils.InsertDelay(250, self.vtfContainer)
                self.__sdlibObj.Cmd13()

        if self.expectedCardTimeout:
            if errorGroup == GRP_ERROR_SD_PROTOCOL and (errorCode == 0x1b):
                self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected Card Timeout occurred")
                failureDesc = self.errorManager.GetAllFailureDescription()
                if not self.vtfContainer.isModel and "CARD_TIME_OUT_RCVD" not in failureDesc:
                    raise ValidationError.TestFailError(self.vtfContainer.GetTestName(), "[ValidationSpace] [CVF:ErrorHandler] CARD_TIME_OUT_RCVD response not received! Actual response = %s"%failureDesc)
                self.errorManager.ClearAllErrors()

        if self.expectedCardDataStatusCrcError:
            if errorGroup == GRP_ERROR_SD_PROTOCOL and (errorCode == 0x4):
                self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected Card Data Status CRC error occurred")
                failureDesc = self.errorManager.GetAllFailureDescription()
                if not self.vtfContainer.isModel and "CARD_DATA_STATUS_CRC_ERROR" not in failureDesc:
                    raise ValidationError.TestFailError(self.vtfContainer.GetTestName(), "[ValidationSpace] [CVF:ErrorHandler] CARD_DATA_STATUS_CRC_ERROR response not received! Actual response = %s"%failureDesc)
                self.errorManager.ClearAllErrors()

        if self.expectedEraseParam:
            if errorGroup == GRP_ERROR_SD_PROTOCOL and (errorCode == 0x9 or errorCode == 0x8000000):
                self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected Erase Param Error occurred")
                failureDesc = self.errorManager.GetAllFailureDescription()
                if not self.vtfContainer.isModel and "ERASE_PARAM" not in failureDesc:
                    raise ValidationError.TestFailError(self.vtfContainer.GetTestName(), "[ValidationSpace] [CVF:ErrorHandler] ERASE_PARAM response not received! Actual response = %s"%failureDesc)
                self.errorManager.ClearAllErrors()
                self.expectedEraseParam = False

        elif self.expectedEraseReset:
            if errorGroup == GRP_ERROR_SD_PROTOCOL and errorCode == 0x2000:
                self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected Erase Reset occurred")
                failureDesc = self.errorManager.GetAllFailureDescription()
                if not self.vtfContainer.isModel and "ERASE_RESET" not in failureDesc:
                    raise ValidationError.TestFailError(self.vtfContainer.GetTestName(), "[ValidationSpace] [CVF:ErrorHandler] ERASE_RESET response not received! Actual response = %s"%failureDesc)
                self.errorManager.ClearAllErrors()
                self.expectedEraseReset = False

        elif self.expectedEraseSeqError:
            if errorGroup == GRP_ERROR_SD_PROTOCOL and errorCode == 0x10000000:
                self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected Erase Sequence Error occurred")
                self.errorManager.ClearAllErrors()
                self.expectedEraseSeqError = False

        elif self.expectedOutOfRangeError:
            if errorGroup == GRP_ERROR_SD_PROTOCOL and (errorCode == 0x80000000 or errorCode == 0x1F):
                self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected OUT_OF_RANGE error occurred")
                failureDesc = self.errorManager.GetAllFailureDescription()
                if not self.vtfContainer.isModel and "OUT_OF_RANGE" not in failureDesc:
                    raise ValidationError.TestFailError(self.vtfContainer.GetTestName(), "[ValidationSpace] [CVF:ErrorHandler] OUT_OF_RANGE response not received! Actual response = %s"%failureDesc)
                self.errorManager.ClearAllErrors()
                self.expectedOutOfRangeError = False

        elif self.expectedFuleError:
            if errorGroup == GRP_ERROR_SD_PROTOCOL and errorCode == 0x10000000:
                self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected Fule(During CMD33) Error occurred")
                self.errorManager.ClearAllErrors()
                self.expectedFuleError = False
            elif errorGroup == GRP_ERROR_SD_PROTOCOL and errorCode == 0x2000:
                self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected Fule(During CMD23) Error occurred")
                self.errorManager.ClearAllErrors()
                self.expectedFuleError = False

        elif self.expectedWriteProtectViolation:
            if errorGroup == GRP_ERROR_SD_PROTOCOL and errorCode == 0x4000000:
                self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected Write Protect Violation occurred")
                self.errorManager.ClearAllErrors()
                self.expectedWriteProtectViolation = False

        elif self.expectedIllegalCmd:
            if errorGroup == GRP_ERROR_MODEL_EXCEPTION and errorCode == 0x1:
                self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing model general error during expected CQ(During CMD44/45) Error occurred")
                self.errorManager.ClearAllErrors()
                if self.clearexpectedIllegalCmdAfterOneInstance:
                    self.expectedIllegalCmd = False

            if errorGroup == GRP_ERROR_SD_PROTOCOL and (errorCode == 0x400000 or errorCode == 0x8):
                self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected CQ(During CMD44/45) Error occurred")
                failureDesc = self.errorManager.GetAllFailureDescription()
                if not self.vtfContainer.isModel and "ILLEGAL_CMD" not in failureDesc:
                    raise ValidationError.TestFailError(self.vtfContainer.GetTestName(), "[ValidationSpace] [CVF:ErrorHandler] ILLEGAL_COMMAND response not received! Actual response = %s"%failureDesc)
                self.errorManager.ClearAllErrors()
                self.expectedIllegalCmd = False

        else:
            #Check if last Command Read : Expected read failures
            if self.vtfContainer.isModel and not self.expectedUECC and Utils.GetLastHostCommand() == "Read":
                lba,trlength = Utils.GetLastReadCommand()
                dataTrackingHandle = self.vtfContainer._livet.GetDataTracking()

                #Get the updated pattern for current lba range : Returns list for all LBAs in the range
                patternList = dataTrackingHandle.GetPatternForLBARange(lba,trlength)
                clearFlag= True

                for pattern in patternList:
                    if pattern not in self.livetErrorDataPattern:
                        #Set flag as false if one of the LBAs not updated as unpredictable in range
                        clearFlag=False

                if clearFlag:
                    self.logger.Info("", "DataTracking for unpredictable data pattern is updated for lba:0x%X for transferlength:0x%X"%(lba,trlength))
                    self.expectedUECC= True


            if self.expectedUECC:
                if errorGroup == GRP_ERROR_MODEL_EXCEPTION and errorCode == 0x1:
                    self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected read failure ")
                    self.errorManager.ClearAllErrors(errorGroup, errorCode)

                # 2nd failure: Cmd13 failed( General error), Clear error if 1st failure occured. Reset UECC flag
                if errorGroup == GRP_ERROR_SD_PROTOCOL and errorCode == 0x80000:
                    self.logger.Info("", "[ValidationSpace] [CVF:ErrorHandler] Clearing all errors as expected read failure ")
                    self.errorManager.ClearAllErrors(errorGroup, errorCode)
                    self.readFailed= True
                    self.expectedUECC = False

        return 0
