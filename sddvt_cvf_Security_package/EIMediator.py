"""
class EIMediator
Contains various error injection APIs
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
import sys, time, traceback, os, math, random
import AddressTypes
import Utils
import FwConfig
import DiagnosticLib
import AddressTranslation
import FileData
import random
import AddressTypes
import Core.ValidationError as TestError
import Constants
import CardRawOperations
import os
hasWAOccurred = False
hasEAOccurred = False
DoHostReset = False
BiCSConfig = 8

class ErrorInjectionClass(object):
    """
    This is a mediator for registering error callback and injecting errors and getting callback
    """
    _staticErrorInjectionClassObj = None
    _errorOccurredType            = None
    _updateCardMapReq             = None

    def __init__(self, testSpace, randomSeed):
        self.logger    = testSpace.GetLogger()
        self.vtfContainer   = testSpace
        self.livet     = self.vtfContainer._livet
        self.flash     = self.livet.GetFlash()
        self.randomObj      = random.Random(randomSeed)
        self.injectedErrors = {"PF":[],"UECC":[],"WA":[],"PRWA":[],"POWA":[],"EA":[],"PREA":[],"POEA":[],"UECC":[],"CECC":[]}
        self.hitErrors      = {"PF":[],"UECC":[],"WA":[],"PRWA":[],"POWA":[],"EA":[],"PREA":[],"POEA":[],"UECC":[],"CECC":[]}
        self.fwConfigObj    = FwConfig.FwConfig(self.vtfContainer)
        self.addressTranslateObj = AddressTranslation.AddressTranslator(self.vtfContainer, self.fwConfigObj)
        self.file21Obj             = FileData.ConfigurationFile21Data(self.vtfContainer)
        self.cardRawObj          = CardRawOperations.CardRawOperations(self.vtfContainer, self.fwConfigObj, self.addressTranslateObj)

        #To give back the callback control on error occurrence to user registered function these variables are used
        self.OnWriteAbortCallback      = None
        self.OnPreWriteAbortCallback   = None
        self.OnPostWriteAbortCallback  = None
        self.OnProgramFailureCallback  = None
        self.OnEraseAbortCallback      = None
        self.OnPreEraseAbortCallback   = None
        self.OnPostEraseAbortCallback  = None
        self.OnEraseFailureCallback    = None

        self.hasWAOccurred = False
        self.hasEAOccurred = False

        #Creating object of StaticErrorInjectionStateClass which will be help for telling the error injected and occurred details
        self.staticErrorInjectionStateObj = StaticErrorInjectionStateClass()

        self.errorInjectionUtilsObj       = ErrorInjectionUtilsClass(testSpace)

        #Enable WordLine/MLCPage addressing mode.
        #self.flash.SetVariable('report_wordline_addresses','on')

        # STM Pool
        self.loadedSTMObj = []

        ### Get PF configs
        #fileBuf = DiagnosticLib.ReadFileSystem(self.vtfContainer, fileID=21)
        #self.__pfConfigSLC = fileBuf.GetOneByteToInt(0x5A)
        #self.__pfConfigMLC = fileBuf.GetOneByteToInt(0x5B)

        self.UECCInjecetedPhyAddr = None
        self.CECCInjecetedPhyAddr = None


        ErrorInjectionClass._staticErrorInjectionClassObj = self

        # Dictionary of Strings of all the control data structures(hypothetical lba's)
        self.__dictionaryOfStringsControlDataLbas = {}
    def RegisterWriteAbortCallback(self, functToBeCalledOnCallback):
        self.livet.UnregisterLivetCallback(self.livet.lcFlashProgramAbort)
        #To give callback on error occurrence to the registered function we need to remember the registered function so adding it to below variable
        self.OnWriteAbortCallback = functToBeCalledOnCallback

        #Registering for WriteAbort callback with predefined OnWriteAbort static method because we print the error occurrence details and then pass the control to registered function
        self.livet.RegisterLivetCallback(self.livet.lcFlashProgramAbort, self.__class__.OnWriteAbort)
        self.logger.Info("","[EIMediator] Registered Livet call back self.livet.lcFlashProgramAbort")
        self.RegisterHostReset()

    #End of RegisterWriteAbortCallback()

    def RegisterPreWriteAbortCallback(self, functToBeCalledOnCallback):
        self.livet.UnregisterLivetCallback(self.livet.lcPreProgramAbort)
        #To give callback on error occurrence to the registered function we need to remember the registered function so adding it to below variable
        self.OnPreWriteAbortCallback = functToBeCalledOnCallback

        #Registering for PreWriteAbort callback with predefined OnPreWriteAbort static method because we print the error occurrence details and then pass the control to registered function
        self.livet.RegisterLivetCallback(self.livet.lcPreProgramAbort, self.__class__.OnPreWriteAbort)
        self.logger.Info("","[EIMediator] Registered Livet call back self.livet.lcPreProgramAbort")
        self.RegisterHostReset()

    #End of RegisterPreWriteAbortCallback()


    def RegisterPostWriteAbortCallback(self, functToBeCalledOnCallback):
        self.livet.UnregisterLivetCallback(self.livet.lcPostProgramAbort)
        #To give callback on error occurrence to the registered function we need to remember the registered function so adding it to below variable
        self.OnPostWriteAbortCallback = functToBeCalledOnCallback

        #Registering for PostWriteAbort callback with predefined OnPostWriteAbort static method because we print the error occurrence details and then pass the control to registered function
        self.livet.RegisterLivetCallback(self.livet.lcPostProgramAbort, self.__class__.OnPostWriteAbort)
        self.logger.Info("","[EIMediator] Registered Livet call back self.livet.lcPostProgramAbort")

        self.RegisterHostReset()

    #End of RegisterPostWriteAbortCallback()

    def RegisterHostReset(self):

        self.livet.UnregisterLivetCallback(self.livet.lcHostReset)

        #Registering for OnHostReset callback.
        self.livet.RegisterLivetCallback(self.livet.lcHostReset, self.__class__.OnHostReset)
        self.logger.Info("","[EIMediator] Registered Livet call back self.livet.lcHostReset")

    #End of RegisterHostReset()

    def RegisterProgramFailureCallback(self, functToBeCalledOnCallback):
        self.livet.UnregisterLivetCallback(self.livet.lcFlashProgramFail)
        #To give callback on error occurrence to the registered function we need to remember the registered function so adding it to below variable
        self.OnProgramFailureCallback = functToBeCalledOnCallback

        #Registering for Program Failure callback with predefined OnProgramFailure static method because we print the error occurrence details and then pass the control to registered function
        self.livet.RegisterLivetCallback(self.livet.lcFlashProgramFail, self.__class__.OnProgramFailure)
        self.logger.Info("","[EIMediator] Registered Livet call back self.livet.lcFlashProgramFail")

    #End of RegisterProgramFailureCallback()


    def RegisterEraseAbortCallback(self, functToBeCalledOnCallback):
        self.livet.UnregisterLivetCallback(self.livet.lcFlashEraseAbort)
        #To give callback on error occurrence to the registered function we need to remember the registered function so adding it to below variable
        self.OnEraseAbortCallback = functToBeCalledOnCallback

        #Registering for EraseAbort callback with predefined OnEraseAbort static method because we print the error occurrence details and then pass the control to registered function
        self.livet.RegisterLivetCallback(self.livet.lcFlashEraseAbort, self.__class__.OnEraseAbort)
        self.logger.Info("","[EIMediator] Registered Livet call back self.livet.lcFlashEraseAbort")
        self.RegisterHostReset()

    #End of RegisterEraseAbortCallback()


    def RegisterPreEraseAbortCallback(self, functToBeCalledOnCallback):
        self.livet.UnregisterLivetCallback(self.livet.lcPreEraseAbort)
        #To give callback on error occurrence to the registered function we need to remember the registered function so adding it to below variable
        self.OnPreEraseAbortCallback = functToBeCalledOnCallback

        #Registering for PreEraseAbort callback with predefined OnPreEraseAbort static method because we print the error occurrence details and then pass the control to registered function
        self.livet.RegisterLivetCallback(self.livet.lcPreEraseAbort, self.__class__.OnPreEraseAbort)
        self.logger.Info("","[EIMediator] Registered Livet call back self.livet.lcPreEraseAbort")
        self.RegisterHostReset()

    #End of RegisterPreEraseAbortCallback()


    def RegisterPostEraseAbortCallback(self, functToBeCalledOnCallback):
        self.livet.UnregisterLivetCallback(self.livet.lcPostEraseAbort)
        #To give callback on error occurrence to the registered function we need to remember the registered function so adding it to below variable
        self.OnPostEraseAbortCallback = functToBeCalledOnCallback

        #Registering for PostEraseAbort callback with predefined OnPostEraseAbort static method because we print the error occurrence details and then pass the control to registered function
        self.livet.RegisterLivetCallback(self.livet.lcPostEraseAbort, self.__class__.OnPostEraseAbort)
        self.logger.Info("","[EIMediator] Registered Livet call back self.livet.lcPostEraseAbort")
        self.RegisterHostReset()

    #End of RegisterPostEraseAbortCallback()


    def RegisterEraseFailureCallback(self, functToBeCalledOnCallback):
        self.livet.UnregisterLivetCallback(self.livet.lcFlashEraseFail)
        #To give callback on error occurrence to the registered function we need to remember the registered function so adding it to below variable
        self.OnEraseFailureCallback = functToBeCalledOnCallback

        #Registering for EraseFailure callback with predefined OnEraseFailure static method because we print the error occurrence details and then pass the control to registered function
        self.livet.RegisterLivetCallback(self.livet.lcFlashEraseFail, self.__class__.OnEraseFailure)
        self.logger.Info("","[EIMediator] Registered Livet call back self.livet.lcFlashEraseFail")

    #End of RegisterEraseFailureCallback()


    def InjectWriteAbortError(self, errorType, errorLba=None, errorPhyAddress=None, skipCount=0, errorDescription=(), callbackFunction=None, skipWlUpdate=False):
        """
        Arguments : erroType         : "wrab", "prwa", "powa"]
                    errorLba         : Lba where error to be injected
                    errorPhyAddress  : PhysicalAddress where error to be injected
                    skipCount        : Determines the number of occurrences of the logical operation to ignore
                    erroDescription  : Errors are described by creating a 5 to 6 element Python tuple. (errorType, errorPersistence, delayToOccurrence, delayToRecovery, optional, optional)
                    callbackFunction : If callback is needed on SetLogicalTrigger
        errorType and (errorLba or errorPhyAddress) are mandatory

        """
        assert(errorLba != None or errorPhyAddress != None), "Physical Address and Error Lba, both cannot be None"
        assert(errorType != None), "Error Type should not be None, Please specify which error you want to inject [Ex: 'wrab', 'prwa', 'powa']!"
        assert(errorType != "wrab" or errorType != "prwa" or errorType != "powa"), "Allowed error types are 'wrab', 'prwa', 'powa' but provided %s"%(errorType)

        if errorType == "wrab":
            errorName = "Write Abort"
        elif errorType == "prwa":
            errorName = "PreWrite Abort"
        elif errorType == "powa":
            errorName = "PostWrite Abort"

        ##########################################################################################################
        #                                            WRITE ABORT                                                 #
        ##########################################################################################################
        #Prepare error description
        flashOperation = self.livet.foProgram
        partition      = 0
        if errorType == "wrab" and errorDescription == ():
            errType           = self.livet.etProgramAbort
            errorPersistence  = self.livet.epSoft
            delayToOccurrence = 0
            delayToRecovery   = 1
            errorByteOffset   = 0
            errorByteMask     = 0
            errorDescription  = (errType, errorPersistence, delayToOccurrence, delayToRecovery, errorByteOffset, errorByteMask)
        elif errorType == "prwa" and errorDescription == ():
            errType           = self.livet.etPreProgramAbort
            errorPersistence  = self.livet.epSoft
            delayToOccurrence = 0
            delayToRecovery   = 1
            errorByteOffset   = 0
            errorByteMask     = 0
            errorDescription  = (errType, errorPersistence, delayToOccurrence, delayToRecovery, errorByteOffset, errorByteMask)
        elif errorType == "powa" and errorDescription == ():
            errType           = self.livet.etPostProgramAbort
            errorPersistence  = self.livet.epSoft
            delayToOccurrence = 0
            delayToRecovery   = 1
            errorByteOffset   = 0
            errorByteMask     = 0
            errorDescription  = (errType, errorPersistence, delayToOccurrence, delayToRecovery, errorByteOffset, errorByteMask)

        #Inject error on LBA
        #self.logger.Info("#"*80)
        if errorLba != None:
            #Check whether error to be injected on Control Data
            self.__IsInjectingErrorOnControlData(errorLba)
            if callbackFunction == None:
                callbackFunction = self.__class__.CallbackFunction
            self.flash.SetLogicalTrigger((partition , errorLba), flashOperation, skipCount, errorDescription, callbackFunction)
            self.logger.Info("","[EIMediator] %s injected on Lba:0x%08X"%(errorName, errorLba))
        #Inject error in Physical address
        elif errorPhyAddress != None:
            if self.file21Obj.numSLCWLToSkip :
                if not skipWlUpdate:
                    errorPhyAddress = self.UpdateWordline(errorPhyAddress)
            wordLineBasedAddress = (errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine, errorPhyAddress.string,\
                                    errorPhyAddress.mlcLevel, errorPhyAddress.eccPage)
            self.flash.InjectError(errorPhyAddress.chip, wordLineBasedAddress, errorDescription)
            self.logger.Info("","[EIMediator] %s injected at Address : Chip:%d Die:%d"%(errorName, errorPhyAddress.chip, errorPhyAddress.die) +\
                             "Plane:%d Block:0x%04x WordLine:0x%04x String:0x%04x mlcLevel:0x%04x eccPage:0x%04x\n\t\t" %(errorPhyAddress.plane, errorPhyAddress.block,\
                                                                                                                          errorPhyAddress.wordLine, errorPhyAddress.string,\
                                                                                                                          errorPhyAddress.mlcLevel, errorPhyAddress.eccPage))
        #self.logger.Info("#"*80)

        return True
    #End of InjectWriteAbortError()

    def InjectProgramFailureError(self, errorLba=None, errorPhyAddress=None, skipCount=0, errorDescription=(), callbackFunction=None, blktype=None, skipWlUpdate=False):
        """
        Arguments : errorLba         : Lba where error to be injected
                    errorPhyAddress  : PhysicalAddress where error to be injected
                    skipCount        : Determines the number of occurrences of the logical operation to ignore
                    erroDescription  : Errors are described by creating a 5 to 6 element Python tuple. (errorType, errorPersistence, delayToOccurrence, delayToRecovery, optional, optional)
                    callbackFunction : If callback is needed on SetLogicalTrigger
        (errorLba or errorPhyAddress) are mandatory
        """
        assert(errorLba != None or errorPhyAddress != None), "Physical Address and Error Lba, both cannot be None"

        ##########################################################################################################
        #                                          PROGRAM FAILURE                                               #
        ##########################################################################################################
        #Prepare error description
        flashOperation = self.livet.foProgram
        partition      = 0
        if errorDescription == ():
            errType           = self.livet.etProgramError
            errorPersistence  = self.livet.epHard
            delayToOccurrence = 0
            delayToRecovery   = 1
            errorByteOffset   = self.randomObj.randint(1, 5) #There are several PF state, 0 is not supported
            errorByteMask     = 0
            errorDescription = (errType, errorPersistence, delayToOccurrence, delayToRecovery, errorByteOffset, errorByteMask)

        ##For PF config other than 'Stop on First PF', inject epSoft errors
        #if (self.__pfConfigSLC != 3) or (self.__pfConfigMLC != 3):
            #errType = errorDescription[0]
            #errorPersistence = self.livet.epSoft
            #delayToOccurrence = errorDescription[2]
            #delayToRecovery = errorDescription[3]
            #errorByteOffset = errorDescription[4]
            #errorByteMask = errorDescription[5]
            #errorDescription = (errType, errorPersistence, delayToOccurrence, delayToRecovery, errorByteOffset, errorByteMask)

        #Inject error on LBA
        self.logger.Debug("","#"*80)
        if errorLba != None:
            #Check whether error to be injected on Control Data
            self.__IsInjectingErrorOnControlData(errorLba)
            if callbackFunction == None:
                callbackFunction = self.__class__.CallbackFunction
            self.flash.SetLogicalTrigger((partition , errorLba), flashOperation, skipCount, errorDescription, callbackFunction)
            self.logger.Info("","[EIMediator] Program Failure injected on Lba:0x%08X"%(errorLba))
        #Inject error in Physical address
        elif errorPhyAddress != None:
            if self.file21Obj.numSLCWLToSkip :
                if not skipWlUpdate:
                    errorPhyAddress = self.UpdateWordline(errorPhyAddress, blktype)
            wordLineBasedAddress = (errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine, errorPhyAddress.string,\
                                    errorPhyAddress.mlcLevel, errorPhyAddress.eccPage)
            self.flash.InjectError(errorPhyAddress.chip, wordLineBasedAddress, errorDescription)
            self.logger.Info("","[EIMediator] Program Failure injected at Address : Chip:%d Die:%d"%(errorPhyAddress.chip, errorPhyAddress.die) +\
                             "Plane:%d Block:0x%04x WordLine:0x%04x String:0x%04x mlcLevel:0x%04x eccPage:0x%04x with error discription:%s\t\t"%(errorPhyAddress.plane, errorPhyAddress.block,\
                                                                                                           errorPhyAddress.wordLine, errorPhyAddress.string,\
                                                                                                           errorPhyAddress.mlcLevel, errorPhyAddress.eccPage, errorDescription))
        self.logger.Debug("","#"*80)

        return False #model will handle Stm injection on PF location
    #End of InjectProgramFailureError()

    def InjectEPDerror(self, errorPhyAddress=None, errorDescription=(), plcDeltaValue = 0):
        """
        Arguments :
                    errorPhyAddress  : PhysicalAddress where error to be injected
                    skipCount        : Determines the number of occurrences of the logical operation to ignore
                    erroDescription  : Errors are described by creating a 5 to 6 element Python tuple. (errorType, errorPersistence, delayToOccurrence, delayToRecovery, optional, optional)
                    callbackFunction : If callback is needed on SetLogicalTrigger
        (errorLba or errorPhyAddress) are mandatory
        """
        assert(errorPhyAddress != None), "Physical Address cannot be None"

        ##########################################################################################################
        #                                          PROGRAM FAILURE                                               #
        ##########################################################################################################
        #Prepare error description
        flashOperation = self.livet.foProgram
        partition      = 0
        if errorDescription == ():
            errType           = self.livet.etProgLoopCount
            errorPersistence  = self.livet.epHard
            delayToOccurrence = 0
            delayToRecovery   = 1
            errorDescription = (errType, errorPersistence, delayToOccurrence, delayToRecovery, plcDeltaValue )

        if self.file21Obj.numSLCWLToSkip :
            errorPhyAddress = self.UpdateWordline(errorPhyAddress)
        wordLineBasedAddress = (errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine, errorPhyAddress.string, 2, 0)
        self.flash.InjectError(errorPhyAddress.chip, wordLineBasedAddress, errorDescription)
        self.logger.Info("","[EIMediator] EPD Failure injected at Address : Chip:0x%X Die:0x%X, Plane:0x%X Block:0x%X WordLine:0x%X String:0x%X BitOnWL:0x%X Column:0x%X"\
                         %(errorPhyAddress.chip, errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine, errorPhyAddress.string, 2,0))
        return True
    #End of InjectEPDerror()

    def InjectEraseAbortError(self, errorType, errorLba=None, errorPhyAddress=None, skipCount=0, errorDescription=(), callbackFunction=None):
        """
        Arguments : erroType         : "erab", "prea", "poea"]
                    errorLba         : Lba where error to be injected
                    errorPhyAddress  : PhysicalAddress where error to be injected
                    skipCount        : Determines the number of occurrences of the logical operation to ignore
                    erroDescription  : Errors are described by creating a 5 to 6 element Python tuple. (errorType, errorPersistence, delayToOccurrence, delayToRecovery, optional, optional)
                    callbackFunction : If callback is needed on SetLogicalTrigger
        errorType and (errorLba or errorPhyAddress) are mandatory
        """
        assert(errorLba != None or errorPhyAddress != None), "Physical Address and Error Lba, both cannot be None"
        assert(errorType != None), "Error Type should not be None, Please specify which error you want to inject [Ex: 'erab', 'prea', 'poea']"
        assert(errorType != "erab" or errorType != "prea" or errorType != "poea"), "Allowed error types are 'erab', 'prea', 'poea' but provided %s"%(errorType)

        if errorType == "erab":
            errorName = "Erase Abort"
        elif errorType == "prea":
            errorName = "PreEraseAbort"
        elif errorType == "poea":
            errorName = "PostErase Abort"

        ##########################################################################################################
        #                                            ERASE ABORT                                                 #
        ##########################################################################################################
        #Prepare error description
        flashOperation = self.livet.foErase
        partition      = 0
        if errorType == "erab" and errorDescription == ():
            errorType         = self.livet.etEraseAbort
            errorPersistence  = self.livet.epSoft
            delayToOccurrence = 0
            delayToRecovery   = 1
            errorByteOffset   = 0
            errorByteMask     = 0
            errorDescription  = (errorType, errorPersistence, delayToOccurrence, delayToRecovery, errorByteOffset, errorByteMask)
        elif errorType == "prea":
            errorType         = self.livet.etPreEraseAbort
            errorPersistence  = self.livet.epSoft
            delayToOccurrence = 0
            delayToRecovery   = 1
            errorByteOffset   = 0
            errorByteMask     = 0
            errorDescription  = (errorType, errorPersistence, delayToOccurrence, delayToRecovery, errorByteOffset, errorByteMask)
        elif errorType == "poea":
            errorType         = self.livet.etPostEraseAbort
            errorPersistence  = self.livet.epSoft
            delayToOccurrence = 0
            delayToRecovery   = 1
            errorByteOffset   = 0
            errorByteMask     = 0
            errorDescription  = (errorType, errorPersistence, delayToOccurrence, delayToRecovery, errorByteOffset, errorByteMask)

        #Inject error on LBA
        #self.logger.Info("#"*80)
        if errorLba != None:
            #Check whether error to be injected on Control Data
            self.__IsInjectingErrorOnControlData(errorLba)
            if callbackFunction == None:
                callbackFunction = self.__class__.CallbackFunction
            self.flash.SetLogicalTrigger((partition , errorLba), flashOperation, skipCount, errorDescription, callbackFunction)
            self.logger.Info("","[EIMediator] %s injected on Lba:0x%08X"%(errorName, errorLba))
        #Inject error in Physical address
        elif errorPhyAddress != None:
            if self.file21Obj.numSLCWLToSkip :
                errorPhyAddress = self.UpdateWordline(errorPhyAddress)
            wordLineBasedAddress = (errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine, errorPhyAddress.string,\
                                    errorPhyAddress.mlcLevel, errorPhyAddress.eccPage)
            self.flash.InjectError(errorPhyAddress.chip, wordLineBasedAddress, errorDescription)
            self.logger.Info("","[EIMediator] %s injected at Address : Chip:%d Die:%d"%(errorName, errorPhyAddress.chip, errorPhyAddress.die) +\
                             "Plane:%d Block:0x%04x WordLine:0x%04x String:0x%04x, mlcLevel:0x%04x eccPage:0x%04x\n\t\t"%(errorPhyAddress.plane, errorPhyAddress.block,\
                                                                                                                          errorPhyAddress.wordLine, errorPhyAddress.string,\
                                                                                                                          errorPhyAddress.mlcLevel,errorPhyAddress.eccPage))
        #self.logger.Info("#"*80)

        return True
    #End of InjectEraseAbortError()


    def InjectEraseFailureError(self, errorLba=None, errorPhyAddress=None, skipCount=0, errorDescription=(), callbackFunction=None, skipWlUpdate=False):
        """
        Arguments : errorLba         : Lba where error to be injected
                    errorPhyAddress  : PhysicalAddress where error to be injected
                    skipCount        : Determines the number of occurrences of the logical operation to ignore
                    erroDescription  : Errors are described by creating a 5 to 6 element Python tuple. (errorType, errorPersistence, delayToOccurrence, delayToRecovery, optional, optional)
                    callbackFunction : If callback is needed on SetLogicalTrigger
        (errorLba or errorPhyAddress) are mandatory
        """
        assert(errorLba != None or errorPhyAddress != None), "Physical Address and Error Lba, both cannot be None"

        ##########################################################################################################
        #                                           ERASE FAILURE                                                #
        ##########################################################################################################
        #Prepare error description
        flashOperation = self.livet.foErase
        partition      = 0
        if errorDescription == ():
            errType           = self.livet.etEraseError
            errorPersistence  = self.livet.epPermanent
            delayToOccurrence = 0
            delayToRecovery   = 1
            errorByteOffset   = 0
            errorByteMask     = 0
            errorDescription = (errType, errorPersistence, delayToOccurrence, delayToRecovery, errorByteOffset, errorByteMask)

        #Inject error on LBA
        #self.logger.Info("#"*80)
        if errorLba != None:
            #Check whether error to be injected on Control Data
            self.__IsInjectingErrorOnControlData(errorLba)
            if callbackFunction == None:
                callbackFunction = self.__class__.CallbackFunction
            self.flash.SetLogicalTrigger((partition , errorLba), flashOperation, skipCount, errorDescription, callbackFunction)
            self.logger.Info("","[EIMediator] Erase Failure injected on Lba:0x%08X"%(errorLba))
        #Inject error in Physical address
        elif errorPhyAddress != None:
            if self.file21Obj.numSLCWLToSkip :
                if not skipWlUpdate:
                    errorPhyAddress = self.UpdateWordline(errorPhyAddress)
            wordLineBasedAddress = (errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine, errorPhyAddress.string,\
                                    errorPhyAddress.mlcLevel, errorPhyAddress.eccPage)
            self.flash.InjectError(errorPhyAddress.chip, wordLineBasedAddress, errorDescription)
            self.logger.Info("","[EIMediator] Erase Failure injected at Address : Chip:%d Die:%d"%(errorPhyAddress.chip, errorPhyAddress.die) +\
                             "Plane:%d Block:0x%04x WordLine:0x%04x String:0x%04x mlcLevel:0x%04x eccPage:0x%04x\n\t\t"%(errorPhyAddress.plane, errorPhyAddress.block,\
                                                                                                                         errorPhyAddress.wordLine, errorPhyAddress.string,\
                                                                                                                         errorPhyAddress.mlcLevel, errorPhyAddress.eccPage))
        #self.logger.Info("#"*80)

        return True
    #End of InjectEraseFailureError()

    def InjectUECCErrorWithSTM(self, errorPhyAddress=None, isCalledFromWaypoint=False, isForceUECC=False, blktype=None, applyOnlyToCurrentMLCPage=None, applyOnlyToPhysicalPage = False, applyOnlyToEccPage = False, dont_update_the_WL = False, skipMlcLevelUpdate=False, skipEccPageUpdate=False):
        """
        Arguments : errorPhyAddress  : PhysicalAddress where error to be injected
        NOTE: This should be called only on written pages (Will lead to picking wrong STMs if called on unwritten/erased pages)
        """
        assert(errorPhyAddress != None), "Physical Address cannot be None"

        SUSPEND_BACK_GROUND_OPERATIONS = 0
        RESUME_BACK_GROUND_OPERATIONS  = 1
        REVERT_ON_ERASE                = 1

        if self.file21Obj.numSLCWLToSkip :
            if not dont_update_the_WL:
                errorPhyAddress = self.UpdateWordline(errorPhyAddress)

        #Before injecting UECC or translating lba to physical address suspend back ground operation, this avoids data movement in the background
        if not isCalledFromWaypoint:
            DiagnosticLib.DoBackGroundMaintenanceOperations(self.vtfContainer, SUSPEND_BACK_GROUND_OPERATIONS)

        package, die, plane, block, wordLine = errorPhyAddress.chip, errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine
        if self.fwConfigObj.isBiCS:
            string = errorPhyAddress.string
        #t_mlcLevel, eccPage = errorPhyAddress.mlcLevel, errorPhyAddress.eccPage

        if skipMlcLevelUpdate or not self.file21Obj.isSinglePageEPWREnabled:
            mlcLevel, eccPage = errorPhyAddress.mlcLevel, errorPhyAddress.eccPage
        else:
            if self.file21Obj.isSinglePageEPWREnabled:
                mlcLevelForOnePageEpwr = []
                if self.file21Obj.lowerPageEpwrEnable:
                    mlcLevelForOnePageEpwr.append(0)
                if self.file21Obj.middlePageEpwrEnable:
                    mlcLevelForOnePageEpwr.append(1)
                if self.file21Obj.upperPageEpwrEnable:
                    mlcLevelForOnePageEpwr.append(2)
                if not mlcLevelForOnePageEpwr:
                    mlcLevelForOnePageEpwr.extend([0, 1, 2])
                errorPhyAddress.mlcLevel = self.randomObj.choice(mlcLevelForOnePageEpwr) if errorPhyAddress.mlcLevel not in mlcLevelForOnePageEpwr else errorPhyAddress.mlcLevel
                mlcLevel = errorPhyAddress.mlcLevel

        if blktype == None:
            if self.fwConfigObj.isBiCS:
                blktype = self.livet.GetFlash().GetBlockType(package, (die, plane, block, wordLine, string, mlcLevel, 0))
            else:
                blktype = self.livet.GetFlash().GetBlockType(package, (die, plane, block, wordLine, mlcLevel, 0))

        if skipEccPageUpdate or applyOnlyToPhysicalPage:
            eccPage = errorPhyAddress.eccPage
        elif applyOnlyToEccPage:
            if blktype == "GAT":
                if self.file21Obj.StringBasedEpwrEnableGAT:
                    eccPage = self.file21Obj.StringBasedEpwrGatStringList[errorPhyAddress.string]
                else:
                    eccPage = errorPhyAddress.eccPage
            elif blktype in [self.livet.pyBlockProgramState.bpsD1,self.livet.pyBlockProgramState.bpsErased,self.livet.pyBlockProgramState.bpsLowerPage,self.livet.pyBlockProgramState.bpsBinErase]:
                if self.file21Obj.StringBasedEpwrEnableSLC:
                    eccPage = self.file21Obj.StringBasedEpwrSlcStringList[errorPhyAddress.string]
                else:
                    eccPage = errorPhyAddress.eccPage
            elif blktype not in [self.livet.pyBlockProgramState.bpsD1,self.livet.pyBlockProgramState.bpsErased,self.livet.pyBlockProgramState.bpsLowerPage,self.livet.pyBlockProgramState.bpsBinErase]:
                if self.file21Obj.StringBasedEpwrEnableMLC:
                    eccPage = self.file21Obj.StringBasedEpwrMlcStringList[errorPhyAddress.string]
                else:
                    eccPage = errorPhyAddress.eccPage

            errorPhyAddress.eccPage = eccPage

        mlcPage = None if not self.file21Obj.isSinglePageEPWREnabled else ["LP", "MP", "UP"][errorPhyAddress.mlcLevel]
        if applyOnlyToCurrentMLCPage or skipMlcLevelUpdate:
            mlcPage = ["LP", "MP", "UP"][errorPhyAddress.mlcLevel]

        if self.fwConfigObj.isBiCS:
            if blktype in [self.livet.pyBlockProgramState.bpsD1,self.livet.pyBlockProgramState.bpsErased,self.livet.pyBlockProgramState.bpsLowerPage,self.livet.pyBlockProgramState.bpsBinErase]:
                stmfile = self.ChooseSTMFile(isSlc=1, errorType="UECC")
            else:
                stmfile = self.ChooseSTMFile(isSlc=0, errorType="UECC", mlcPage=mlcPage)
        else:
            if blktype in [self.livet.pyBlockProgramState.bpsD1,self.livet.pyBlockProgramState.bpsErased,self.livet.pyBlockProgramState.bpsLowerPage,self.livet.pyBlockProgramState.bpsBinErase]:
                stmfile = self.ChooseSTMFile(isSlc=1, errorType="UECC")
            else:
                stmfile = self.ChooseSTMFile(isSlc=0, errorType="UECC", mlcPage=mlcPage)

        #self.livet.GetFlash().TraceOn( "stm_debug" )
        #self.livet.GetFlash().TraceOn( "stm_debug_ber" )
        #self.livet.GetFlash().TraceOn( "stm_debug_thresh" )

        stmHandle = self.LoadExistingStmHandle(stmfile)
        self.logger.Info("","[EIMediator] STM Handle: %d" %stmHandle)
        StmObj = stmHandle

        #StmObj=self.livet.GetFlash().LoadSTMfromDisk(stmfile)
        if self.fwConfigObj.isBiCS:
            if self.file21Obj.numSLCWLToSkip :
                if not dont_update_the_WL:
                    errorPhyAddress = self.UpdateWordline(errorPhyAddress)
            package = errorPhyAddress.chip
            phyaddr = (errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine,\
                       errorPhyAddress.string, errorPhyAddress.mlcLevel, errorPhyAddress.eccPage*self.fwConfigObj.columnsPerRawEccPage)
            #code length for lambeau1ZCR is 35520 bits i.e. 4420 bytes, we are corrupting only 50% of ECC page thats why we are giving 2220
            self.logger.Info("","[EIMediator] Injecting UECC error at Physical Address:[chip:0x%X, die:0x%X, plane:0x%X, block:0x%X, wordline:0x%X, string:0x%X, mlcLevel:0x%X, eccPage:0x%X]"%\
                             (errorPhyAddress.chip, errorPhyAddress.die, errorPhyAddress.plane,\
                              errorPhyAddress.block, errorPhyAddress.wordLine,errorPhyAddress.string,\
                              errorPhyAddress.mlcLevel, errorPhyAddress.eccPage))
        else:
            package = errorPhyAddress.chip
            phyaddr = (errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine,\
                       errorPhyAddress.mlcLevel, errorPhyAddress.eccPage*self.fwConfigObj.columnsPerRawEccPage)
            self.logger.Info("","[EIMediator] Injecting UECC error at Physical Address:[chip:0x%X, die:0x%X, plane:0x%X, block:0x%X, wordline:0x%X, mlcLevel:0x%X, eccPage:0x%X]"%\
                             (errorPhyAddress.chip, errorPhyAddress.die, errorPhyAddress.plane,\
                              errorPhyAddress.block, errorPhyAddress.wordLine,\
                              errorPhyAddress.mlcLevel, errorPhyAddress.eccPage))

        #randomly selecting between 50% to 100% of the columnsPerRawEccPage
        #length = self.randomObj.randint(1110, 2220)
        length = self.fwConfigObj.columnsPerRawEccPage #self.randomObj.randint((self.fwConfigObj.columnsPerRawEccPage/2), self.fwConfigObj.columnsPerRawEccPage)

        if applyOnlyToEccPage == True:
            self.logger.Info("","[EIMediator: InjectUECCErrorWithSTM] Applying STM at ECCPage Level at the provided Physical Address")
            self.livet.GetFlash().ApplySTMtoCol(StmObj, package, phyaddr, length, REVERT_ON_ERASE)
        #self.livet.GetFlash().ApplySTMtoCol(StmObj, package, phyaddr, length, REVERT_ON_ERASE)
        #Apply STM to all planes of the die & to the complete Wordline
        elif applyOnlyToPhysicalPage == True:
            self.logger.Info("","[EIMediator: InjectUECCErrorWithSTM] Corrupting physical page of Die %d Plane %d and all Strings of selected Wordline %d"
                             %(errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.wordLine))
            self.livet.GetFlash().ApplySTMtoWordline(StmObj, package, errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine, REVERT_ON_ERASE)
        else:
            self.logger.Info("","[EIMediator: InjectUECCErrorWithSTM] Corrupting Die page of Die %d and all Strings of selected Wordline %d"
                             %(errorPhyAddress.die, errorPhyAddress.wordLine))
            for plane in range(0, self.fwConfigObj.planeInterleave):
                self.livet.GetFlash().ApplySTMtoWordline(StmObj, package, errorPhyAddress.die, plane, errorPhyAddress.block, errorPhyAddress.wordLine, REVERT_ON_ERASE)

        self.UECCInjecetedPhyAddr = errorPhyAddress

        #Before injecting UECC or translating lba to physical address suspended back ground operation, to avoid data movement in the background
        if not isCalledFromWaypoint:
            DiagnosticLib.DoBackGroundMaintenanceOperations(self.vtfContainer, RESUME_BACK_GROUND_OPERATIONS)
        return True
    #End of InjectUECCErrorWithSTM()

    def InjectRomDrErrorWithSTM(self, errorPhyAddress, error, applyOnlyToEccPage=False, applyOnlyToPhyPage=True, applyToEntireWordline=False,\
                             applyToEntirePhyBlock=False, isCalledFromWaypoint=False, BlockType="SLC"):
        """
        Arguments : errorPhyAddress  : PhysicalAddress where error to be injected
                    error            : can be 'DRCaseX' (X = 0-12)
        @Author: Shaheed Nehal A
        """

        self.ROMDRTable = ['00', 'E0', '20', 'F0', '10', 'D0', '30', 'C0', '40', '50', '60', 'B0', 'A0']

        #fwConfigObj = Diag.GetFWConfig(self.testSpace)
        assert(errorPhyAddress != None), "Physical Address cannot be None"

        SUSPEND_BACK_GROUND_OPERATIONS = 0
        RESUME_BACK_GROUND_OPERATIONS  = 1
        REVERT_ON_ERASE                = 1
        ECCPageSize = self.fwConfigObj.columnsPerRawEccPage
        NO_OF_STRINGS = self.fwConfigObj.stringsPerBlock
        NO_OF_WORDLINES = self.fwConfigObj.wordLinesPerPhysicalBlock_BiCS
        NO_OF_ECCPAGES_PER_PAGE = self.fwConfigObj.eccPagesPerPage

        FW_VALIDATION_PATH = os.getenv('FVTPATH')
        STM_FILES_PATH  = FW_VALIDATION_PATH + "\\Tests\\" + "FelixSTMs\\" + "BiCS" + str(BiCSConfig) + "\\SLC\\" + "ROM_DR\\"

        if "DRCase" in error:
            DRCaseNo = int(error.split("DRCase")[-1])
            STMFile = STM_FILES_PATH + "\Case_" + str(DRCaseNo+1) + "_" + self.ROMDRTable[DRCaseNo] + "_SLC_DRT.STM"
        else:
            raise TestError.TestFailedError("","[EIMediator: InjectRomDrErrorWithSTM] Unknown error (%s) passed"%error)

        stmHandle = self.LoadExistingStmHandle(STMFile)
        self.logger.Info("","STM Handle: %d" %stmHandle)
        self.logger.Info("","STM File Path: %s"%STMFile)
        StmObj = stmHandle

        package = errorPhyAddress.chip
        phyaddr = (errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine,\
                   errorPhyAddress.string, errorPhyAddress.mlcLevel, errorPhyAddress.eccPage)
        self.logger.Info("","Injecting %s error at Physical Address:[chip:0x%X, die:0x%X, plane:0x%X, block:0x%X, wordline:0x%X, string:0x%X, mlcLevel:0x%X, eccPage:0x%X]"%\
                         (error, errorPhyAddress.chip, errorPhyAddress.die, errorPhyAddress.plane,\
                          errorPhyAddress.block, errorPhyAddress.wordLine,errorPhyAddress.string,\
                          errorPhyAddress.mlcLevel, errorPhyAddress.eccPage))

        if applyOnlyToEccPage:
            # Select 1 ECC Page length
            length = ECCPageSize #self.fwConfigObj.columnsPerRawEccPage  --> HARDCODED (FwConfig not available)
            self.logger.Info("","[EIMediator: InjectRomDrErrorWithSTM] Applying STM at ECCPage Level at the provided Physical Address")
            self.livet.GetFlash().ApplySTMtoCol(StmObj, package, phyaddr, length, REVERT_ON_ERASE)

        elif applyOnlyToPhyPage:
            # Select 1 Phy Page (ECCpagesize * EccPagesPerPage)
            length =  ECCPageSize*NO_OF_ECCPAGES_PER_PAGE  #self.fwConfigObj.columnsPerRawEccPage * self.fwConfigObj.eccPagesPerPage --> HARDCODED (FwConfig not available)
            self.logger.Info("","[EIMediator: InjectRomDrErrorWithSTM] Applying STM at PhyPage Level at the provided Physical Address")
            #Applying on all ecc pages of the phy page, hence setting eccPage=0
            errorPhyAddress.eccPage = 0
            addr = (errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine,\
                       errorPhyAddress.string, errorPhyAddress.mlcLevel, errorPhyAddress.eccPage)
            self.livet.GetFlash().ApplySTMtoCol(StmObj, package, addr, length, REVERT_ON_ERASE)

        elif applyToEntireWordline:
            self.logger.Info("","[EIMediator: InjectRomDrErrorWithSTM] Applying STM at Wordline Level at the provided Physical Address")
            self.livet.GetFlash().ApplySTMtoWordline(StmObj, package, errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine, REVERT_ON_ERASE)

        else:
            self.logger.Info("","[EIMediator: InjectRomDrErrorWithSTM] Applying STM at PhyBlock Level at the provided Physical Address")
            self.livet.GetFlash().ApplySTMtoBlock(StmObj, package, errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, REVERT_ON_ERASE)

        return True

    def InjectEpwrDrErrorWithSTM(self, errorPhyAddress, isSlc, applyOnlyToEccPage=False, isCalledFromWaypoint=False):
        """
        Arguments : errorPhyAddress  : PhysicalAddress where error to be injected
        """
        assert(errorPhyAddress != None), "Physical Address cannot be None"

        mlcLevel = errorPhyAddress.mlcLevel
        SUSPEND_BACK_GROUND_OPERATIONS = 0
        RESUME_BACK_GROUND_OPERATIONS  = 1
        REVERT_ON_ERASE                = 1

        #Before injecting UECC or translating lba to physical address suspend back ground operation, this avoids data movement in the background
        if not isCalledFromWaypoint:
            DiagnosticLib.DoBackGroundMaintenanceOperations(self.vtfContainer, SUSPEND_BACK_GROUND_OPERATIONS)

        # Validation Package Path
        import os
        FW_VALIDATION_PATH = os.getenv('FVTPATH')

        if isSlc:
            if self.file21Obj.slcEPWRDREnable:
                FilePath  = FW_VALIDATION_PATH + r"\Tests\FelixSTMs\BiCS" + str(BiCSConfig) + "\SLC\EPWR_DR_UniqueSTMs" + "\\" #No folder as of now, no SLC EPWR DR
            else:
                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Test tried to inject EPWR DR error on SLC, but SLC EPWR DR is disabled in File21, offset 0xCA")
        else:
            if self.file21Obj.mlcEPWRDREnable:
                FilePath  = FW_VALIDATION_PATH + r"\Tests\FelixSTMs\BiCS" + str(BiCSConfig) + "\TLC\EPWR_DR_UniqueSTMs" + "\\" + ["LP", "MP", "UP"][mlcLevel] + "\\"
            else:
                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Test tried to inject EPWR DR error on MLC, but MLC EPWR DR is disabled in File21, offset 0xCA")

        if applyOnlyToEccPage:
            if isSlc:
                if self.file21Obj.StringBasedEpwrEnableSLC:
                    eccPage = self.file21Obj.StringBasedEpwrSlcStringList[errorPhyAddress.string]
                else:
                    eccPage = errorPhyAddress.eccPage
            else:
                if self.file21Obj.StringBasedEpwrEnableMLC:
                    eccPage = self.file21Obj.StringBasedEpwrMlcStringList[errorPhyAddress.string]
                else:
                    eccPage = errorPhyAddress.eccPage

            errorPhyAddress.eccPage = eccPage
        listOfStmFiles = [stmFile for stmFile in os.listdir(FilePath) if stmFile.endswith(".STM")]
        selectedStmFile = self.randomObj.choice(listOfStmFiles)
        stmfile = FilePath + selectedStmFile

        stmHandle = self.LoadExistingStmHandle(stmfile)
        self.logger.Info("","[EIMediator] STM Handle: %d" %stmHandle)
        self.logger.Info("", "[EIMediator] STM file used: %s"%stmfile)
        StmObj = stmHandle

        if self.fwConfigObj.isBiCS:
            package = errorPhyAddress.chip
            phyaddr = (errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine,\
                       errorPhyAddress.string, errorPhyAddress.mlcLevel, errorPhyAddress.eccPage*self.fwConfigObj.columnsPerRawEccPage)
            #code length for lambeau1ZCR is 35520 bits i.e. 4420 bytes, we are corrupting only 50% of ECC page thats why we are giving 2220
            self.logger.Info("","[EIMediator] Injecting EPWR DR error at Physical Address:[chip:0x%X, die:0x%X, plane:0x%X, block:0x%X, wordline:0x%X, string:0x%X, mlcLevel:0x%X, eccPage:0x%X]"%\
                             (errorPhyAddress.chip, errorPhyAddress.die, errorPhyAddress.plane,\
                              errorPhyAddress.block, errorPhyAddress.wordLine,errorPhyAddress.string,\
                              errorPhyAddress.mlcLevel, errorPhyAddress.eccPage))
        else:
            package = errorPhyAddress.chip
            phyaddr = (errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine,\
                       errorPhyAddress.mlcLevel, errorPhyAddress.eccPage*self.fwConfigObj.columnsPerRawEccPage)
            self.logger.Info("","[EIMediator] Injecting EPWR DR error at Physical Address:[chip:0x%X, die:0x%X, plane:0x%X, block:0x%X, wordline:0x%X, mlcLevel:0x%X, eccPage:0x%X]"%\
                             (errorPhyAddress.chip, errorPhyAddress.die, errorPhyAddress.plane,\
                              errorPhyAddress.block, errorPhyAddress.wordLine,\
                              errorPhyAddress.mlcLevel, errorPhyAddress.eccPage))

        # Select 1 ECC Page length
        length = self.fwConfigObj.columnsPerRawEccPage #self.randomObj.randint((self.fwConfigObj.columnsPerRawEccPage/2), self.fwConfigObj.columnsPerRawEccPage)

        if applyOnlyToEccPage == True:
            self.logger.Info("","[EIMediator: InjectEpwrDrErrorWithSTM] Applying STM at ECCPage Level at the provided Physical Address")
            self.livet.GetFlash().ApplySTMtoCol(StmObj, package, phyaddr, length, REVERT_ON_ERASE)
        #self.livet.GetFlash().ApplySTMtoCol(StmObj, package, phyaddr, length, REVERT_ON_ERASE)
        #Apply STM to all planes of the die & to the complete Wordline
        else:
            self.logger.Info("","[EIMediator: InjectEpwrDrErrorWithSTM] Corrupting physical page of Die %d Plane %d and all Strings of selected Wordline %d"
                             %(errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.wordLine))
            self.livet.GetFlash().ApplySTMtoWordline(StmObj, package, errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine, REVERT_ON_ERASE)

        #Before injecting UECC or translating lba to physical address suspended back ground operation, to avoid data movement in the background
        if not isCalledFromWaypoint:
            DiagnosticLib.DoBackGroundMaintenanceOperations(self.vtfContainer, RESUME_BACK_GROUND_OPERATIONS)
        return True
    # End of InjectEpwrDrErrorWithSTM()

    def InjectWorstCaseEpwrDrOnBlock(self, metaBlock, isSlc, isCalledFromWaypoint=False):
        phyAddrList = self.livet.GetFirmwareInterface().GetPhysicalBlocksFromMetablockAddress(metaBlock, 0)

        phyAdd = AddressTypes.PhysicalAddress()

        # Validation Package Path
        FW_VALIDATION_PATH = os.getenv('FVTPATH')

        # Number of TLC Pages (x3)
        NUM_MLC_LEVELS = self.fwConfigObj.mlcLevel
        PAGE_LIST = ["LP","MP","UP"]

        listOfStmFiles = []
        if isSlc:
            if not self.file21Obj.slcEPWRDREnable:
                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Test tried to inject EPWR DR error on SLC, but SLC EPWR DR is disabled in File21, offset 0xCA")

            mlcLevel = 0
            FilePath  = FW_VALIDATION_PATH + r"\Tests\FelixSTMs\BiCS" + str(BiCSConfig) + "\SLC\\EPWR_DR_UniqueSTMs\\"
            listOfStmFiles = [[stmFile for stmFile in os.listdir(FilePath) if stmFile.endswith(".STM")][-2:]]
        else:
            if not self.file21Obj.mlcEPWRDREnable:
                raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Test tried to inject EPWR DR error on MLC, but MLC EPWR DR is disabled in File21, offset 0xCA")

            for t_mlcLevel in range(0, NUM_MLC_LEVELS):
                FilePath  = FW_VALIDATION_PATH + r"\Tests\FelixSTMs\BiCS" + str(BiCSConfig) + "\TLC\\EPWR_DR_UniqueSTMs" + "\\" + PAGE_LIST[t_mlcLevel] + "\\"
                t_listOfStmFiles = [stmFile for stmFile in os.listdir(FilePath) if stmFile.endswith(".STM")]
                if len(t_listOfStmFiles) >= 1:
                    t_listOfStmFiles.reverse()
                    listOfStmFiles.append(t_listOfStmFiles)
                else:
                    assert (False), ("[InjectWorstCaseEpwrDrOnBlock] No STM Present in Folder %s" %(FilePath))

        # Store Block Type Information
        if isSlc:
            phyAdd.isTrueBinaryBlock = True
            phyAdd.mlcLevel = 0
        else:
            phyAdd.isTrueBinaryBlock = False

        # Decide Start WL
        if isSlc:
            startWL = Utils.GetPaddedWL()
        else:
            startWL = 0

        totalUniqueSTMsAvailablePerPage = 3
        currentMlcLevel = self.randomObj.choice(list(range(self.fwConfigObj.mlcLevel)))
        stmCount = 0

        # Loop though all physical blocks in given MB
        for planeIndex in range(0, len(phyAddrList)):
            phyAdd.chip=phyAddrList[planeIndex][0]
            phyAdd.block=phyAddrList[planeIndex][3]
            baseCaseIndex = self.randomObj.choice(list(range(totalUniqueSTMsAvailablePerPage)))
            currentCaseIndex = baseCaseIndex

            for WL in range(startWL, self.fwConfigObj.wordLinesPerPhysicalBlock_BiCS):
                phyAdd.wordLine = WL

                for string in range(0, self.fwConfigObj.stringsPerBlock):
                    phyAdd.string = string

                    for die in range(0, self.fwConfigObj.dieInterleave):
                        if die != phyAddrList[planeIndex][1]:
                            continue

                        phyAdd.die = phyAddrList[planeIndex][1]

                        for plane in range(0, self.fwConfigObj.planeInterleave):
                            if plane != phyAddrList[planeIndex][2]:
                                continue

                            phyAdd.plane = phyAddrList[planeIndex][2]

                            if not isSlc:
                                FilePath  = FW_VALIDATION_PATH + r"\Tests\FelixSTMs\BiCS" + str(BiCSConfig) + "\TLC\\EPWR_DR_UniqueSTMs" + "\\" + PAGE_LIST[currentMlcLevel % NUM_MLC_LEVELS] + "\\"
                            else:
                                FilePath  = FW_VALIDATION_PATH + r"\Tests\FelixSTMs\BiCS" + str(BiCSConfig) + "\SLC\\EPWR_DR_UniqueSTMs\\"

                            selectedStmFile = listOfStmFiles[currentMlcLevel % NUM_MLC_LEVELS][currentCaseIndex % totalUniqueSTMsAvailablePerPage]
                            stmfile = FilePath + selectedStmFile

                            # Apply diff STM on every physical page
                            self.ApplySTM(errorPhyAddress=phyAdd,
                                          stmfile=stmfile,
                                          length=self.fwConfigObj.eccPagesPerPage*self.fwConfigObj.columnsPerRawEccPage,
                                          isCalledFromWaypoint=isCalledFromWaypoint)

                            currentCaseIndex += 1
                            stmCount += 1
                            if stmCount % self.fwConfigObj.mlcLevel == 0:
                                currentMlcLevel += 1
                                currentCaseIndex = baseCaseIndex

        return True
        # End of InjectWorstCaseEpwrDrOnBlock

    def InjectSTMOnHypotheticalLba(self,errorLba,errorType,mode=None):
        """
        Description:
           * Injects STM on hypothetical Lba
        """
        partition = 0
        flashOperation = self.livet.foRead
        skipCount = 0
        clsObj = ErrorInjectionClass._staticErrorInjectionClassObj
        clsObj.staticErrorInjectionStateObj.SetMostRecentErrorOccurredState(errorType=errorType, updateCardmap=False, mode=mode)

        #errorDescription = (errorType, errorPersistence, delayToOccurrence, delayToRecovery, errorByteOffset, errorByteMask)
        errorDescription = (self.livet.etBadBit, self.livet.epHard, 0, 100, 0, 1)
        if errorType == "UECC" or errorType == "CECC":
            self.logger.Info("","[EIMediator: InjectSTMOnHypotheticalLba]: %s will be injected on hypothetical lba 0x%04x"%(errorType,errorLba))
            self.flash.SetLogicalTrigger((partition, errorLba), flashOperation, skipCount, errorDescription, self.__class__.GetPhyAddrFromHypotheticalLbaForECC)
        else:
            raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Error type (CECC/UECC) needs to be given")


    @staticmethod
    def GetPhyAddrFromHypotheticalLbaForECC(arg0, arg1, arg2, arg3, arg4, arg5, arg6 ):
        """
        Description:
           * Get Physical address from Hypothetical Lba and Inject STM
        """
        clsObj = ErrorInjectionClass._staticErrorInjectionClassObj
        errorType, updateCardmap, mode = clsObj.staticErrorInjectionStateObj.GetMostRecentErrorOccurredState()

        phyAdd = AddressTypes.PhysicalAddress()

        phyAdd.chip     = arg5
        phyAdd.die      = arg6[0]
        phyAdd.plane    = arg6[1]
        phyAdd.block    = arg6[2]
        phyAdd.wordLine = arg6[3]
        phyAdd.string   = arg6[4]
        phyAdd.mlcLevel = arg6[5]
        phyAdd.eccPage  = arg6[6]

        if errorType == "UECC":
            clsObj.InjectUECCErrorWithSTM(errorPhyAddress=phyAdd, isCalledFromWaypoint = True, applyOnlyToPhysicalPage=True)
        elif errorType == "CECC":
            clsObj.InjectCECCErrorWithSTM(errorPhyAddress=phyAdd, isCalledFromWaypoint = True, mode=mode, applyOnlyToPhysicalPage=True)


    def InjectCECCErrorWithSTM(self, errorPhyAddress=None, isCalledFromWaypoint=False, mode=None, blktype=None,entireBlock=None,applyOnlyToPhysicalPage = False, applyOnlyToEccPage=False, dont_update_the_WL = False, longestPath=False, skipEccPageUpdate=False):
        """
        Arguments : errorPhyAddress  : PhysicalAddress where error to be injected
        NOTE: This should be called only on written pages (Will lead to picking wrong STMs if called on unwritten/erased pages)
        """
        assert(errorPhyAddress != None), "Physical Address cannot be None"

        SUSPEND_BACK_GROUND_OPERATIONS = 0
        RESUME_BACK_GROUND_OPERATIONS  = 1
        REVERT_ON_ERASE                = 1

        #Before injecting UECC or translating lba to physical address suspend back ground operation, this avoids data movement in the background
        if not isCalledFromWaypoint:
            DiagnosticLib.DoBackGroundMaintenanceOperations(self.vtfContainer, SUSPEND_BACK_GROUND_OPERATIONS)

        package, die, plane, block, wordLine = errorPhyAddress.chip, errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine
        if self.fwConfigObj.isBiCS:
            string = errorPhyAddress.string
        mlcLevel, eccPage = errorPhyAddress.mlcLevel, errorPhyAddress.eccPage

        if blktype == None:
            if self.fwConfigObj.isBiCS:
                blktype = self.livet.GetFlash().GetBlockType(package, (die, plane, block, wordLine, string, mlcLevel, 0))
            else:
                blktype = self.livet.GetFlash().GetBlockType(package, (die, plane, block, wordLine, mlcLevel, 0))

        if skipEccPageUpdate or applyOnlyToPhysicalPage:
            eccPage = errorPhyAddress.eccPage
        elif applyOnlyToEccPage:
            if blktype == "GAT":
                if self.file21Obj.StringBasedEpwrEnableGAT:
                    eccPage = self.file21Obj.StringBasedEpwrGatStringList[errorPhyAddress.string]
                else:
                    eccPage = errorPhyAddress.eccPage
            elif blktype in [self.livet.pyBlockProgramState.bpsD1,self.livet.pyBlockProgramState.bpsErased,self.livet.pyBlockProgramState.bpsLowerPage,self.livet.pyBlockProgramState.bpsBinErase]:
                if self.file21Obj.StringBasedEpwrEnableSLC:
                    eccPage = self.file21Obj.StringBasedEpwrSlcStringList[errorPhyAddress.string]
                else:
                    eccPage = errorPhyAddress.eccPage

            elif blktype not in [self.livet.pyBlockProgramState.bpsD1,self.livet.pyBlockProgramState.bpsErased,self.livet.pyBlockProgramState.bpsLowerPage,self.livet.pyBlockProgramState.bpsBinErase]:
                if self.file21Obj.StringBasedEpwrEnableMLC:
                    eccPage = self.file21Obj.StringBasedEpwrMlcStringList[errorPhyAddress.string]
                else:
                    eccPage = errorPhyAddress.eccPage

            errorPhyAddress.eccPage = eccPage

        mode = "CECC"
        if longestPath:
            mode = "CECC_LongestPath"

        if self.fwConfigObj.isBiCS:
            if blktype in [self.livet.pyBlockProgramState.bpsD1,self.livet.pyBlockProgramState.bpsErased,self.livet.pyBlockProgramState.bpsLowerPage,self.livet.pyBlockProgramState.bpsBinErase]:
                stmfile = self.ChooseSTMFile(isSlc=1, errorType=mode)
            else:
                MLCPages = ["LP", "MP", "UP"]
                stmfile = self.ChooseSTMFile(isSlc=0, errorType=mode, mlcPage=MLCPages[mlcLevel])
        else:
            if blktype in [self.livet.pyBlockProgramState.bpsD1,self.livet.pyBlockProgramState.bpsErased,self.livet.pyBlockProgramState.bpsLowerPage,self.livet.pyBlockProgramState.bpsBinErase]:
                stmfile = self.ChooseSTMFile(isSlc=1, errorType=mode)
            else:
                stmfile = self.ChooseSTMFile(isSlc=0, errorType=mode)

        #self.livet.GetFlash().TraceOn( "stm_debug" )
        #self.livet.GetFlash().TraceOn( "stm_debug_ber" )
        #self.livet.GetFlash().TraceOn( "stm_debug_thresh" )

        stmHandle = self.LoadExistingStmHandle(stmfile)
        self.logger.Info("","[EIMediator] STM Handle: %d" %stmHandle)
        StmObj = stmHandle

        if self.fwConfigObj.isBiCS:
            if self.file21Obj.numSLCWLToSkip :
                if not dont_update_the_WL:
                    errorPhyAddress = self.UpdateWordline(errorPhyAddress)
            package = errorPhyAddress.chip
            phyaddr = (errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine,\
                       errorPhyAddress.string, errorPhyAddress.mlcLevel, errorPhyAddress.eccPage*self.fwConfigObj.columnsPerRawEccPage)
            self.logger.Info("","[EIMediator] Injecting CECC error at Physical Address:[chip:0x%X, die:0x%X, plane:0x%X, block:0x%X, wordline:0x%X, string:0x%X, mlcLevel:0x%X, eccPage:0x%X]"%\
                             (errorPhyAddress.chip, errorPhyAddress.die, errorPhyAddress.plane,\
                              errorPhyAddress.block, errorPhyAddress.wordLine,errorPhyAddress.string,\
                              errorPhyAddress.mlcLevel, errorPhyAddress.eccPage))
        else:
            package = errorPhyAddress.chip
            phyaddr = (errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine,\
                       errorPhyAddress.mlcLevel, errorPhyAddress.eccPage*self.fwConfigObj.columnsPerRawEccPage)
            self.logger.Info("","[EIMediator] Injecting CECC error at Physical Address:[chip:0x%X, die:0x%X, plane:0x%X, block:0x%X, wordline:0x%X, mlcLevel:0x%X, eccPage:0x%X]"%\
                             (errorPhyAddress.chip, errorPhyAddress.die, errorPhyAddress.plane,\
                              errorPhyAddress.block, errorPhyAddress.wordLine,\
                              errorPhyAddress.mlcLevel, errorPhyAddress.eccPage))

        #randomly selecting between 50% to 100% of the columnsPerRawEccPage
        #length = self.randomObj.randint(1110, 2220)
        #length = self.randomObj.randint((self.fwConfigObj.columnsPerRawEccPage/2), self.fwConfigObj.columnsPerRawEccPage)
        #self.livet.GetFlash().ApplySTMtoCol(StmObj, package, phyaddr, length, REVERT_ON_ERASE)
        length = self.fwConfigObj.columnsPerRawEccPage #self.randomObj.randint((self.fwConfigObj.columnsPerRawEccPage/2), self.fwConfigObj.columnsPerRawEccPage)

        if applyOnlyToEccPage == True:
            self.logger.Info("","[EIMediator: InjectCECCErrorWithSTM] Applying STM at ECCPage Level at the provided Physical Address")
            self.livet.GetFlash().ApplySTMtoCol(StmObj, package, phyaddr, length, REVERT_ON_ERASE)

        elif entireBlock == None or entireBlock == False:
            if applyOnlyToPhysicalPage == True:
                self.logger.Info("","[EIMediator: InjectCECCErrorWithSTM] Corrupting physical page of Die %d Plane %d and all Strings of selected Wordline %d"
                                 %(errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.wordLine))
                self.livet.GetFlash().ApplySTMtoWordline(StmObj, package, errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine, REVERT_ON_ERASE)
            else:
                self.logger.Info("","[EIMediator: InjectCECCErrorWithSTM] Corrupting Die page of Die %d and all Strings of selected Wordline %d"
                                 %(errorPhyAddress.die, errorPhyAddress.wordLine))
                #Apply STM to all planes of the die & to the complete Wordline
                for plane in range(0, self.fwConfigObj.planeInterleave):
                    self.livet.GetFlash().ApplySTMtoWordline(StmObj, package, errorPhyAddress.die, plane, errorPhyAddress.block, errorPhyAddress.wordLine, REVERT_ON_ERASE)
        else:
             #Apply STM on entire block
            self.livet.GetFlash().ApplySTMtoBlock(StmObj, package, errorPhyAddress.die, plane, errorPhyAddress.block, REVERT_ON_ERASE)

        self.CECCInjecetedPhyAddr = errorPhyAddress

        if not isCalledFromWaypoint:
            DiagnosticLib.DoBackGroundMaintenanceOperations(self.vtfContainer, RESUME_BACK_GROUND_OPERATIONS)

        return True
    #End of InjectCECCErrorWithSTM()

    def LoadExistingStmHandle(self, stmFilePath):
        for stmHandleEntries in self.loadedSTMObj:
            if stmHandleEntries[0] == stmFilePath:
                return stmHandleEntries[1]

        stmObjToUse = self.flash.LoadSTMfromDisk(stmFilePath)
        self.loadedSTMObj.append([stmFilePath, stmObjToUse])
        return stmObjToUse
    # End of LoadExistingStmHandle

    def ApplySTM(self, errorPhyAddress, stmfile, length=None, isCalledFromWaypoint = False, isToBeAppliedToWordline = False, isToBeAppliedToPlane = False, isToBeAppliedToBlock=False, isSkipWL=False):
        """
        Applies the specified STM
        """
        assert(errorPhyAddress != None), "Physical Address cannot be None"
        assert(stmfile != ""), "STM to be applied should be mentioned"

        SUSPEND_BACK_GROUND_OPERATIONS = 0
        RESUME_BACK_GROUND_OPERATIONS  = 1
        REVERT_ON_ERASE                = 1

        #Before injecting UECC or translating lba to physical address suspend back ground operation, this avoids data movement in the background
        if not isCalledFromWaypoint:
            DiagnosticLib.DoBackGroundMaintenanceOperations(self.vtfContainer, SUSPEND_BACK_GROUND_OPERATIONS)

        self.logger.Info("","[EIMediator] STM file applied is %s"%stmfile)
        stmHandle = self.LoadExistingStmHandle(stmfile)
        self.logger.Info("","[EIMediator] STM Handle: %d" %stmHandle)
        StmObj = stmHandle

        if self.fwConfigObj.isBiCS:
            if self.file21Obj.numSLCWLToSkip :
                if isSkipWL:
                    errorPhyAddress = self.UpdateWordline(errorPhyAddress)
            package = errorPhyAddress.chip
            phyaddr = (errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine,\
                       errorPhyAddress.string, errorPhyAddress.mlcLevel, errorPhyAddress.eccPage*self.fwConfigObj.columnsPerRawEccPage)
            self.logger.Info("","[EIMediator] Applying STM at Physical Address:[chip:0x%X, die:0x%X, plane:0x%X, block:0x%X, wordline:0x%X, string:0x%X, mlcLevel:0x%X, eccPage:0x%X]"%\
                               (errorPhyAddress.chip, errorPhyAddress.die, errorPhyAddress.plane,\
                                errorPhyAddress.block, errorPhyAddress.wordLine,errorPhyAddress.string,\
                                errorPhyAddress.mlcLevel, errorPhyAddress.eccPage))
        else:
            package = errorPhyAddress.chip
            phyaddr = (errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine,\
                       errorPhyAddress.mlcLevel, errorPhyAddress.eccPage*self.fwConfigObj.columnsPerRawEccPage)
            self.logger.Info("","[EIMediator] Applying STM at Physical Address:[chip:0x%X, die:0x%X, plane:0x%X, block:0x%X, wordline:0x%X, mlcLevel:0x%X, eccPage:0x%X]"%\
                               (errorPhyAddress.chip, errorPhyAddress.die, errorPhyAddress.plane,\
                                errorPhyAddress.block, errorPhyAddress.wordLine,\
                                errorPhyAddress.mlcLevel, errorPhyAddress.eccPage))

        #Apply to column level (code length=2292 bytes --> for X3)
        if length == None:
            length = self.fwConfigObj.columnsPerRawEccPage

        if isToBeAppliedToWordline:
            self.logger.Info("","[EIMediator: ApplySTM] Corrupting Die page of Die %d and all Strings of selected Wordline %d"
                             %(errorPhyAddress.die, errorPhyAddress.wordLine))
            #Apply STM to all planes of the die
            for plane in range(0, self.fwConfigObj.planeInterleave):
                self.livet.GetFlash().ApplySTMtoWordline(StmObj, package, errorPhyAddress.die, plane, errorPhyAddress.block, errorPhyAddress.wordLine, REVERT_ON_ERASE)
        elif isToBeAppliedToPlane:
            self.logger.Info("","[EIMediator: ApplySTM] Corrupting physical page of Die %d Plane %d and all Strings of selected Wordline %d"
                             %(errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.wordLine))
            self.livet.GetFlash().ApplySTMtoWordline(StmObj, package, errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine, REVERT_ON_ERASE)
        elif isToBeAppliedToBlock:
            self.logger.Info("","[EIMediator: ApplySTM] Applying STM at Entire Block")
            self.livet.GetFlash().ApplySTMtoBlock(StmObj, package, errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, REVERT_ON_ERASE)
        else:
            if length == self.fwConfigObj.columnsPerRawEccPage:
                self.logger.Info("","[EIMediator: ApplySTM] Applying STM at ECCPage Level at the provided Physical Address (ECCPageSize = %dB)"%length)
            else:
                self.logger.Info("","[EIMediator: ApplySTM] Applying STM at the provided Physical Address (User specified length = %dB)"%length)
            self.livet.GetFlash().ApplySTMtoCol(StmObj, package, phyaddr, length, REVERT_ON_ERASE)
        if not isCalledFromWaypoint:
            DiagnosticLib.DoBackGroundMaintenanceOperations(self.vtfContainer, RESUME_BACK_GROUND_OPERATIONS)

    def ChooseSTMFile(self, isSlc, errorType, mlcPage=None):
        """
        Name: ChooseSTMFile
        Description: To chose one of the stm file based on the parameter passed to the function.
        Arguments: is it bics, is it slc type and mode type.
        Returns: stm file.
        """
        import os

        FW_VALIDATION_PATH = os.getenv('FVTPATH')

        if isSlc:
            FilePath  = FW_VALIDATION_PATH + "\\Tests\\" + "\\FelixSTMs\\" + "\\BiCS" + str(BiCSConfig) + "\\SLC\\"
        else:
            FilePath  = FW_VALIDATION_PATH + "\\Tests\\" + "\\FelixSTMs\\" + "\\BiCS" + str(BiCSConfig) +  "\\TLC\\"

        FilePath = FilePath + errorType + "\\"
        #Below check added to make sure CVF fails the test if path not found and also ptin
        if not os.path.exists(FilePath):
            self.logger.BigBanner("", "[EIMediator: Error] Path not found \n%s"%FilePath)
            raise TestError.TestFailError(self.vtfContainer.GetTestName(), "Path (%s) not found"%FilePath)
        listOfStmFiles = [stmFile for stmFile in os.listdir(FilePath) if stmFile.upper().endswith(".STM")]

        #If mlcPage is provided, then pick CECC STM targeted for that mlcPage
        if not isSlc and mlcPage!=None:
            while 1:
                stmFileOnly = self.randomObj.choice(listOfStmFiles)
                if mlcPage in stmFileOnly:
                    break
        else:
            stmFileOnly = self.randomObj.choice(listOfStmFiles)

        stmFile = FilePath + stmFileOnly
        self.logger.Info("", "[EIMediator] The stm file chosen is : %s"%(stmFile))

        #Below check added to make sure CVF fails the test if file not found
        if not os.path.exists(stmFile):
            self.logger.BigBanner("", "[EIMediator: Error] STM file not found \n%s"%stmFile)
            raise TestError.TestFailError(self.vtfContainer.GetTestName(), "STM file (%s) not found"%stmFile)

        return stmFile
    #End of ChooseSTMFile

    def ChooseEpwrUeccSTMFile(self, isSlc, secondthresholdFail, mlcLevel):
        """
        Name: ChooseSTMFile
        Description: To chose one of the stm file based on the parameter passed to the function.
        Arguments: is it bics, is it slc type and mode type.
        Returns: stm file.
        """
        import os

        FW_VALIDATION_PATH = os.getenv('FVTPATH')

        if isSlc == "yes" :
            if secondthresholdFail:
                FilePath  = FW_VALIDATION_PATH + "\\Tests\\" + "\\FelixSTMs\\" + "\\BICS" + str(BiCSConfig) + "\\SLC\\" + "EPWR_UECC\\" + "SECOND_THRESH\\"
            else:
                FilePath  = FW_VALIDATION_PATH + "\\Tests\\" + "\\FelixSTMs\\" + "\\BICS" + str(BiCSConfig) + "\\SLC\\" + "EPWR_UECC\\" + "FIRST_THRESH\\"

        if isSlc == "no" :
            pageType = {0: "LP", 1: "MP", 2: "UP"}
            if mlcLevel not in [0,1,2]:
                FilePath  = FW_VALIDATION_PATH + "\\Tests\\" + "\\FelixSTMs\\" + "\\BICS" + str(BiCSConfig) + "\\TLC\\" + "EPWR_UECC\\"
            else:
                FilePath  = FW_VALIDATION_PATH + "\\Tests\\" + "\\FelixSTMs\\" + "\\BICS" + str(BiCSConfig) + "\\TLC\\" + "EPWR_UECC\\" + pageType[mlcLevel] + "\\"


        listOfStmFiles = [stmFile for stmFile in os.listdir(FilePath) if stmFile.endswith(".STM")]

        stmFileOnly = self.randomObj.choice(listOfStmFiles)
        stmFile = FilePath + stmFileOnly

        self.logger.Info("","[EIMediator] The stm file chosen is : %s"%(stmFile))

        return stmFile
    #End of ChooseEpwrUeccSTMFile

    @staticmethod
    def CallbackFunction(lba, partition, flashOperation, skipCount, errorDescription, package, physicalAddress):
        clsObj = ErrorInjectionClass._staticErrorInjectionClassObj

        clsObj.logger.Debug("","#"*80)
        clsObj.logger.Debug("","Error being injecting at : ")
        clsObj.logger.Debug("","Lba:0x%X -> Partition:0x%X, flashOperation:%s, skipCount:0x%X, errorDescription:%s, package:0x%X, physicalAddress:%s"%(lba, partition, flashOperation, skipCount,\
                                                                                                                                                   list(errorDescription), package, list(physicalAddress)))
        clsObj.logger.Debug("","#"*80)

        return True
    #End of CallbackFunction()


    @staticmethod
    def OnWriteAbort(package, addr):
        global hasWAOccurred , DoHostReset

        clsObj = ErrorInjectionClass._staticErrorInjectionClassObj


        bank, chip         = clsObj.GetBankAndChipNumberFromPackage(package, clsObj.fwConfigObj.numChips)
        bank, metaBlockNum = clsObj.livet.GetFirmwareInterface().GetMetablock(package,addr)

        clsObj.logger.Info("","*"*80)
        clsObj.logger.Info("","[EIMediator] ---WRITE ABORT--- Occurred at -> Bank:%d   MetaBlock:0x%X"%(bank, metaBlockNum))
        clsObj.logger.Info("","[EIMediator] Physical Address : (Chip:0x%X Die:0x%X Plane:0x%X, Block:0x%X, Wordline:0x%X, MlcLevel:0x%X, Column:0x%X)"%(chip, addr[0], addr[1], addr[2], addr[3], addr[4], addr[5]))
        clsObj.logger.Info("","*"*80)

        #Get the wordLine LBAs
        wordLineLbas =  clsObj.flash.GetWordlineLBAs(package,addr)
        #Get the affected LBAs
        affectedLbas = clsObj.flash.GetAffectedLBAs()
        #Log the wordline Lbas
        clsObj.errorInjectionUtilsObj.LogWordlineLbas(package, addr, wordLineLbas, headerString = "WRITE ABORT")

        #In case of error to update cardmap with UECC set the error occurrence state
        clsObj.staticErrorInjectionStateObj.SetMostRecentErrorOccurredState(errorType="wrab", updateCardmap=True)

        #Whenever caller registered with None type no need to give the control or else need to provide callback to regestired function
        if clsObj.OnWriteAbortCallback != None:
            try:
                clsObj.OnWriteAbortCallback(package, addr, metaBlockNum)
            except (TypeError):
                clsObj.OnWriteAbortCallback(package, addr)
            except:
                raise

        #Update model data tracking module to exclude last written host command
        #Commenting as updating model data tracking during HostReset
        #if Utils.GetLastHostCommand() == "Write":
            #lba,trlength = Utils.GetLastWriteCommand()
            #clsObj.logger.Info("", "[EIMediator] Model DataTracking Updated with UnPredictable Pattern for last written command Lba : 0x%X TransferLength : 0x%X "%(lba ,trlength))
            #clsObj.UpdateModelDataTrackingWithUnPredictablePattern(clsObj.livet, lba, trlength)

        ##To recheck - Updating model DT in case the last command was Erase, but there was a write abort during internal write
        ##Check with Livet - we need to revert prev state
        #elif Utils.GetLastHostCommand() == "Erase":
            ##Update model data tracking module to exclude last written host command
            #lba,trlength = Utils.GetLastEraseCommand()
            #clsObj.logger.Info("", "[EIMediator] Model DataTracking Updated with UnPredictable Pattern for last erased command Lba : 0x%X TransferLength : 0x%X "%(lba ,trlength))
            #clsObj.UpdateModelDataTrackingWithUnPredictablePattern(clsObj.livet, lba, trlength)

        DoHostReset = True
        hasWAOccurred = True

        #Filter the wordLine Lbas so that only valid Lbas present in the error affected Lbas
        mlcLevel = addr[4]
        if mlcLevel != 0:
            numOfPages        = wordLineLbas[0] #0th argument tells the number of pages can be written in a wordline
            errorAffectedLbas = []
            for lba in wordLineLbas[numOfPages+1:]: #1st argument till numOfPages represents number of Lbas in each page (lower, middle, upper etc.) so the actual Lbas starts from numOfPages+1
                if 0 <= lba <= clsObj.fwConfigObj.maxLba:
                    errorAffectedLbas.append(lba)
            clsObj.staticErrorInjectionStateObj.SetListOfErrorAffectedLbas(errorAffectedLbas)

        return False #Fasle : Model simulate the failure. True: The test needs to do flash operation to cause WA symptom and then return
    #End of OnProgramAbort()


    @staticmethod
    def OnPreWriteAbort(package, addr):
        global hasWAOccurred , DoHostReset
        clsObj = ErrorInjectionClass._staticErrorInjectionClassObj

        bank, chip         = clsObj.GetBankAndChipNumberFromPackage(package, clsObj.fwConfigObj.numChips)
        bank, metaBlockNum = clsObj.livet.GetFirmwareInterface().GetMetablock(package,addr)

        clsObj.logger.Info("","*"*80)
        clsObj.logger.Info("","[EIMediator] ---PRE WRITE ABORT--- Occurred at -> Bank:%d   MetaBlock:0x%X"%(bank, metaBlockNum))
        clsObj.logger.Info("","[EIMediator] Physical Address : (Chip:0x%X Die:0x%X Plane:0x%X, Block:0x%X, Wordline:0x%X, MlcLevel:0x%X, Column:0x%X)"%(chip, addr[0], addr[1], addr[2], addr[3], addr[4], addr[5]))
        clsObj.logger.Info("","*"*80)
        #Get the wordLine LBAs
        wordLineLbas =  clsObj.flash.GetWordlineLBAs(package,addr)
        #Log the wordline Lbas
        clsObj.errorInjectionUtilsObj.LogWordlineLbas(package, addr, wordLineLbas, headerString = "PRE WRITE ABORT")

        #In case of error to update cardmap with UECC set the error occurrence state
        clsObj.staticErrorInjectionStateObj.SetMostRecentErrorOccurredState(errorType="prwa", updateCardmap=True)

        #Whenever caller registered with None type no need to give the control or else need to provide callback to regestired function
        if clsObj.OnPreWriteAbortCallback != None:
            try:
                clsObj.OnPreWriteAbortCallback(package, addr, metaBlockNum)
            except (TypeError):
                clsObj.OnPreWriteAbortCallback(package, addr)
            except :
                raise
        #Commenting as updating model data tracking during HostReset
        #if Utils.GetLastHostCommand() == "Write":
            ##Update model data tracking module to exclude last written host command
            #lba,trlength = Utils.GetLastWriteCommand()
            #clsObj.logger.Info("", "[EIMediator] Model DataTracking Updated with UnPredictable Pattern for last written command Lba : 0x%X TransferLength : 0x%X "%(lba ,trlength))
            #clsObj.UpdateModelDataTrackingWithUnPredictablePattern(clsObj.livet, lba, trlength)

        ##To recheck - Updating model DT in case the last command was Erase, but there was a write abort during internal write
        #elif Utils.GetLastHostCommand() == "Erase":
            ##Update model data tracking module to exclude last written host command
            #lba,trlength = Utils.GetLastEraseCommand()
            #clsObj.logger.Info("", "[EIMediator] Model DataTracking Updated with UnPredictable Pattern for last erased command Lba : 0x%X TransferLength : 0x%X "%(lba ,trlength))
            #clsObj.UpdateModelDataTrackingWithUnPredictablePattern(clsObj.livet, lba, trlength)

        hasWAOccurred = True
        DoHostReset = True

        return False #Fasle : Model simulate the failure. True: The test needs to do flash operation to cause WA symptom and then return
    #End of OnPreWriteAbort()


    @staticmethod
    def OnPostWriteAbort(package, addr):
        global hasWAOccurred , DoHostReset

        clsObj = ErrorInjectionClass._staticErrorInjectionClassObj


        bank, chip         = clsObj.GetBankAndChipNumberFromPackage(package, clsObj.fwConfigObj.numChips)
        bank, metaBlockNum = clsObj.livet.GetFirmwareInterface().GetMetablock(package,addr)

        clsObj.logger.Info("","*"*80)
        clsObj.logger.Info("","[EIMediator] ---POST WRITE ABORT--- Occurred at -> Bank:%d   MetaBlock:0x%X"%(bank, metaBlockNum))
        clsObj.logger.Info("","[EIMediator] Physical Address : (Chip:0x%X Die:0x%X Plane:0x%X, Block:0x%X, Wordline:0x%X, MlcLevel:0x%X, Column:0x%X)"%(chip, addr[0], addr[1], addr[2], addr[3], addr[4], addr[5]))
        clsObj.logger.Info("","*"*80)

        #Get the wordLine LBAs
        wordLineLbas =  clsObj.flash.GetWordlineLBAs(package,addr)
        #Log the wordline Lbas
        clsObj.errorInjectionUtilsObj.LogWordlineLbas(package, addr, wordLineLbas, headerString = "POST WRITE ABORT")

        #In case of error to update cardmap with UECC set the error occurrence state
        clsObj.staticErrorInjectionStateObj.SetMostRecentErrorOccurredState(errorType="powa", updateCardmap=True)

        #Whenever caller registered with None type no need to give the control or else need to provide callback to regestired function
        if clsObj.OnPostWriteAbortCallback != None:
            try:
                clsObj.OnPostWriteAbortCallback(package, addr, metaBlockNum)
            except (TypeError):
                clsObj.OnPostWriteAbortCallback(package, addr)
            except:
                raise

        #Commenting as updating model data tracking during HostReset
        #if Utils.GetLastHostCommand() == "Write":
            ##Update model data tracking module to exclude last written host command
            #lba,trlength = Utils.GetLastWriteCommand()
            #clsObj.logger.Info("", "[EIMediator] Model DataTracking Updated with UnPredictable Pattern for last written command Lba : 0x%X TransferLength : 0x%X "%(lba ,trlength))
            #clsObj.UpdateModelDataTrackingWithUnPredictablePattern(clsObj.livet, lba, trlength)

        ##To recheck - Updating model DT in case the last command was Erase, but there was a write abort during internal write
        #elif Utils.GetLastHostCommand() == "Erase":
            ##Update model data tracking module to exclude last written host command
            #lba,trlength = Utils.GetLastEraseCommand()
            #clsObj.logger.Info("", "[EIMediator] Model DataTracking Updated with UnPredictable Pattern for last erased command Lba : 0x%X TransferLength : 0x%X "%(lba ,trlength))
            #clsObj.UpdateModelDataTrackingWithUnPredictablePattern(clsObj.livet, lba, trlength)

        DoHostReset = True
        hasWAOccurred = True
        return False #Fasle : Model simulate the failure. True: The test needs to do flash operation to cause WA symptom and then return
    #End of OnPostWriteAbort()


    @staticmethod
    def OnHostReset (self):

        clsObj = ErrorInjectionClass._staticErrorInjectionClassObj
        clsObj.logger.Info("","*"*80)
        clsObj.logger.Info("","[EIMediator] ---------------HOST RESET--------------- Occurred ")
        clsObj.logger.Info("","*"*80)

        global DoHostReset , hasEAOccurred
        #Update model data tracking module to exclude last written host command
        if Utils.GetLastHostCommand() != "PC":
        #if DoHostReset or hasEAOccurred:
            if Utils.GetLastHostCommand() == "Write":
                lba,trlength = Utils.GetLastWriteCommand()
                #printing LBA's
                lba,trlength = Utils.GetLastWriteCommand()
                clsObj.logger.Info(""," Host Reset LBA :  0x%X trlength : 0x%X "%(lba , trlength))

                clsObj.logger.Info("", "[EIMediator] Model DataTracking Updated with UnPredictable Pattern for last written command Lba : 0x%X TransferLength : 0x%X "%(lba ,trlength))
                clsObj.UpdateModelDataTrackingWithUnPredictablePattern(clsObj.livet, lba, trlength)

            #To recheck - Updating model DT in case the last command was Erase, but there was a write abort during internal write
            #Check with Livet - we need to revert prev state
            elif Utils.GetLastHostCommand() == "Erase":
                #Update model data tracking module to exclude last written host command
                lba,trlength = Utils.GetLastEraseCommand()
                #printing LBA's
                lba,trlength = Utils.GetLastWriteCommand()
                clsObj.logger.Info(""," Host Reset LBA :  0x%X trlength : 0x%X "%(lba , trlength))

                clsObj.logger.Info("", "[EIMediator] Model DataTracking Updated with UnPredictable Pattern for last erased command Lba : 0x%X TransferLength : 0x%X "%(lba ,trlength))
                clsObj.UpdateModelDataTrackingWithUnPredictablePattern(clsObj.livet, lba, trlength)

            DoHostReset = False


    @staticmethod
    def OnProgramFailure(package, addr):
        clsObj = ErrorInjectionClass._staticErrorInjectionClassObj

        bank, chip         = clsObj.GetBankAndChipNumberFromPackage(package, clsObj.fwConfigObj.numChips)
        bank, metaBlockNum = clsObj.livet.GetFirmwareInterface().GetMetablock(package,addr)

        clsObj.hitErrors['PF'].append(tuple([chip]+list(addr[:4])))
        clsObj.logger.Info("","*"*80)
        clsObj.logger.Info("","[EIMediator] ---PROGRAM FAILURE--- Occurred at -> Bank:%d   MetaBlock:0x%X"%(bank, metaBlockNum))
        clsObj.logger.Info("","[EIMediator] Physical Address : (Chip:0x%X Die:0x%X Plane:0x%X, Block:0x%X, Wordline:0x%X, String :0x%X, MlcLevel:0x%X, EccPage:0x%X)"%(chip, addr[0], addr[1], addr[2], addr[3], addr[4], addr[5],addr[6]))
        clsObj.logger.Info("","*"*80)

        #Get the wordLine LBAs
        wordLineLbas =  clsObj.flash.GetWordlineLBAs(package,addr)
        #Get the affected LBAs
        affectedLbas = clsObj.flash.GetAffectedLBAs()
        #Log the wordline Lbas
        clsObj.errorInjectionUtilsObj.LogWordlineLbas(package, addr, wordLineLbas, headerString = "PROGRAM FAILURE")

        #In case of error to update cardmap with UECC set the error occurrence state
        clsObj.staticErrorInjectionStateObj.SetMostRecentErrorOccurredState(errorType="prfa", updateCardmap=False)

        #Whenever caller registered with None type no need to give the control or else need to provide callback to regestired function
        retVal = False
        if clsObj.OnProgramFailureCallback != None:
            retVal = clsObj.OnProgramFailureCallback(package, addr)

        if retVal == True:
            return True
        else:
            return False #Fasle : Model simulate the failure. True: The test needs to do flash operation to cause WA symptom and then return
    #End of OnProgramFailure()


    @staticmethod
    def OnEraseAbort(package, addr):
        global hasEAOccurred
        clsObj = ErrorInjectionClass._staticErrorInjectionClassObj

        bank, chip         = clsObj.GetBankAndChipNumberFromPackage(package, clsObj.fwConfigObj.numChips)
        bank, metaBlockNum = clsObj.livet.GetFirmwareInterface().GetMetablock(package,addr)

        clsObj.logger.Info("","*"*80)
        clsObj.logger.Info("","[EIMediator] ---ERASE ABORT--- Occurred at -> Bank:%d   MetaBlock:0x%X"%(bank, metaBlockNum))
        clsObj.logger.Info("","[EIMediator] Physical Address : (Chip:0x%X Die:0x%X Plane:0x%X, Block:0x%X, Wordline:0x%X, MlcLevel:0x%X, Column:0x%X)"%(chip, addr[0], addr[1], addr[2], addr[3], addr[4], addr[5]))
        clsObj.logger.Info("","*"*80)

        #Get the wordLine LBAs
        wordLineLbas =  clsObj.flash.GetWordlineLBAs(package,addr)
        #Log the wordline Lbas
        clsObj.errorInjectionUtilsObj.LogWordlineLbas(package, addr, wordLineLbas, headerString = "ERASE ABORT")

        #In case of error to update cardmap with UECC set the error occurrence state
        clsObj.staticErrorInjectionStateObj.SetMostRecentErrorOccurredState(errorType="erab", updateCardmap=True)

        #Commenting as updating model data tracking during HostReset
        #if Utils.GetLastHostCommand() == "Erase":
            ##Update model data tracking module to exclude last written host command
            #lba,trlength = Utils.GetLastEraseCommand()
            #clsObj.logger.Info("", "[EIMediator] Model DataTracking Updated with UnPredictable Pattern for last erased command Lba : 0x%X TransferLength : 0x%X "%(lba ,trlength))
            ##To recheck - Upon Erase(), the version should revert to prev value. Does this API work for Erase?
            #clsObj.UpdateModelDataTrackingWithUnPredictablePattern(clsObj.livet, lba, trlength)

        #elif Utils.GetLastHostCommand() == "Write":
            ##Update model data tracking module to exclude last written host command
            #lba,trlength = Utils.GetLastWriteCommand()
            #clsObj.logger.Info("", "[EIMediator] Model DataTracking Updated with UnPredictable Pattern for last write command Lba : 0x%X TransferLength : 0x%X "%(lba ,trlength))
            #clsObj.UpdateModelDataTrackingWithUnPredictablePattern(clsObj.livet, lba, trlength)

        hasEAOccurred = True
        #Whenever caller registered with None type no need to give the control or else need to provide callback to regestired function
        if clsObj.OnEraseAbortCallback != None:
            try:
                clsObj.OnEraseAbortCallback(package, addr, metaBlockNum)
            except (TypeError):
                clsObj.OnEraseAbortCallback(package, addr)
            except:
                raise
        DoHostReset = True
        return False #Fasle : Model simulate the failure. True: The test needs to do flash operation to cause WA symptom and then return
    #End of OnEraseAbort()


    @staticmethod
    def OnPreEraseAbort(package, addr):
        global hasEAOccurred
        clsObj = ErrorInjectionClass._staticErrorInjectionClassObj

        bank, chip         = clsObj.GetBankAndChipNumberFromPackage(package, clsObj.fwConfigObj.numChips)
        bank, metaBlockNum = clsObj.livet.GetFirmwareInterface().GetMetablock(package,addr)

        clsObj.logger.Info("","*"*80)
        clsObj.logger.Info("","[EIMediator] ---PRE ERASE ABORT--- Occurred at -> Bank:%d   MetaBlock:0x%X"%(bank, metaBlockNum))
        clsObj.logger.Info("","[EIMediator] Physical Address : (Chip:0x%X Die:0x%X Plane:0x%X, Block:0x%X, Wordline:0x%X, MlcLevel:0x%X, Column:0x%X)"%(chip, addr[0], addr[1], addr[2], addr[3], addr[4], addr[5]))
        clsObj.logger.Info("","*"*80)

        #Get the wordLine LBAs
        wordLineLbas =  clsObj.flash.GetWordlineLBAs(package,addr)
        #Log the wordline Lbas
        clsObj.errorInjectionUtilsObj.LogWordlineLbas(package, addr, wordLineLbas, headerString = "PRE ERASE ABORT")

        #In case of error to update cardmap with UECC set the error occurrence state
        clsObj.staticErrorInjectionStateObj.SetMostRecentErrorOccurredState(errorType="prea", updateCardmap=True)

        #To recheck - Below check works only when prev host command was Erase and it failed
        #How to handle EA injected failures?

        #Commenting as updating model data tracking during HostReset
        #if Utils.GetLastHostCommand() == "Erase":
            ##Update model data tracking module to exclude last written host command
            #lba,trlength = Utils.GetLastEraseCommand()
            #clsObj.logger.Info("", "[EIMediator] Model DataTracking Updated with UnPredictable Pattern for last erased command Lba : 0x%X TransferLength : 0x%X "%(lba ,trlength))
            ##To recheck - Upon Erase(), the version should revert to prev value. Does this API work for Erase?
            #clsObj.UpdateModelDataTrackingWithUnPredictablePattern(clsObj.livet, lba, trlength)

        #elif Utils.GetLastHostCommand() == "Write":
            ##Update model data tracking module to exclude last written host command
            #lba,trlength = Utils.GetLastWriteCommand()
            #clsObj.logger.Info("", "[EIMediator] Model DataTracking Updated with UnPredictable Pattern for last write command Lba : 0x%X TransferLength : 0x%X "%(lba ,trlength))
            #clsObj.UpdateModelDataTrackingWithUnPredictablePattern(clsObj.livet, lba, trlength)

        hasEAOccurred = True


        #Whenever caller registered with None type no need to give the control or else need to provide callback to regestired function
        if clsObj.OnPreEraseAbortCallback != None:
            try:
                clsObj.OnPreEraseAbortCallback(package, addr, metaBlockNum)

            except (TypeError):
                clsObj.OnPreEraseAbortCallback(package, addr)
            except:
                raise
        DoHostReset = True
        return False #Fasle : Model simulate the failure. True: The test needs to do flash operation to cause WA symptom and then return
    #End of OnPreEraseAbort()


    @staticmethod
    def OnPostEraseAbort(package, addr):
        global hasEAOccurred
        clsObj = ErrorInjectionClass._staticErrorInjectionClassObj

        bank, chip         = clsObj.GetBankAndChipNumberFromPackage(package, clsObj.fwConfigObj.numChips)
        bank, metaBlockNum = clsObj.livet.GetFirmwareInterface().GetMetablock(package,addr)

        clsObj.logger.Info("","*"*80)
        clsObj.logger.Info("","[EIMediator] ---POST ERASE ABORT--- Occurred at -> Bank:%d   MetaBlock:0x%X"%(bank, metaBlockNum))
        clsObj.logger.Info("","[EIMediator] Physical Address : (Chip:0x%X Die:0x%X Plane:0x%X, Block:0x%X, Wordline:0x%X, MlcLevel:0x%X, Column:0x%X)"%(chip, addr[0], addr[1], addr[2], addr[3], addr[4], addr[5]))
        clsObj.logger.Info("","*"*80)

        #Get the wordLine LBAs
        wordLineLbas =  clsObj.flash.GetWordlineLBAs(package,addr)
        #Log the wordline Lbas
        clsObj.errorInjectionUtilsObj.LogWordlineLbas(package, addr, wordLineLbas, headerString = "POST ERASE ABORT")

        #In case of error to update cardmap with UECC set the error occurrence state
        clsObj.staticErrorInjectionStateObj.SetMostRecentErrorOccurredState(errorType="poea", updateCardmap=True)

        #Commenting as updating model data tracking during HostReset
        #if Utils.GetLastHostCommand() == "Erase":
            ##Update model data tracking module to exclude last written host command
            #lba,trlength = Utils.GetLastEraseCommand()
            #clsObj.logger.Info("", "[EIMediator] Model DataTracking Updated with UnPredictable Pattern for last erased command Lba : 0x%X TransferLength : 0x%X "%(lba ,trlength))
            ##To recheck - Upon Erase(), the version should revert to prev value. Does this API work for Erase?
            #clsObj.UpdateModelDataTrackingWithUnPredictablePattern(clsObj.livet, lba, trlength)

        #elif Utils.GetLastHostCommand() == "Write":
            ##Update model data tracking module to exclude last written host command
            #lba,trlength = Utils.GetLastWriteCommand()
            #clsObj.logger.Info("", "[EIMediator] Model DataTracking Updated with UnPredictable Pattern for last write command Lba : 0x%X TransferLength : 0x%X "%(lba ,trlength))
            #clsObj.UpdateModelDataTrackingWithUnPredictablePattern(clsObj.livet, lba, trlength)

        hasEAOccurred = True

        #Whenever caller registered with None type no need to give the control or else need to provide callback to regestired function
        if clsObj.OnPostEraseAbortCallback != None:
            try:
                clsObj.OnPostEraseAbortCallback(package, addr, metaBlockNum)
            except (TypeError):
                clsObj.OnPostEraseAbortCallback(package, addr)
            except:
                raise

        DoHostReset = True
        return False #Fasle : Model simulate the failure. True: The test needs to do flash operation to cause WA symptom and then return
    #End of OnPostEraseAbort()


    @staticmethod
    def OnEraseFailure(package, addr):
        clsObj = ErrorInjectionClass._staticErrorInjectionClassObj

        bank, chip         = clsObj.GetBankAndChipNumberFromPackage(package, clsObj.fwConfigObj.numChips)
        bank, metaBlockNum = clsObj.livet.GetFirmwareInterface().GetMetablock(package,addr)

        clsObj.logger.Info("","*"*80)
        clsObj.logger.Info("","[EIMediator] ---ERASE FAILURE--- Occurred at -> Bank:%d   MetaBlock:0x%X"%(bank, metaBlockNum))
        clsObj.logger.Info("","[EIMediator] Physical Address : (Chip:0x%X Die:0x%X Plane:0x%X, Block:0x%X, Wordline:0x%X, MlcLevel:0x%X, Column:0x%X)"%(chip, addr[0], addr[1], addr[2], addr[3], addr[4], addr[5]))
        clsObj.logger.Info("","*"*80)

        #Get the wordLine LBAs
        wordLineLbas =  clsObj.flash.GetWordlineLBAs(package,addr)
        #Log the wordline Lbas
        clsObj.errorInjectionUtilsObj.LogWordlineLbas(package, addr, wordLineLbas, headerString = "ERASE FAILURE")

        #In case of error to update cardmap with UECC set the error occurrence state
        clsObj.staticErrorInjectionStateObj.SetMostRecentErrorOccurredState(errorType="erfa", updateCardmap=False)

        #Whenever caller registered with None type no need to give the control or else need to provide callback to regestired function
        if clsObj.OnEraseFailureCallback != None:
            try:
                clsObj.OnEraseFailureCallback(package, addr,metaBlockNum)
            except (TypeError):
                clsObj.OnEraseFailureCallback(package, addr)
            except:
                raise
        return False #Fasle : Model simulate the failure. True: The test needs to do flash operation to cause WA symptom and then return
    #End of OnEraseFailure()


    def GetBankAndChipNumberFromPackage(self, package, numOfChipPerBank = 1):
        #calculation of bank and chip from package
        bankNum = old_div(package, numOfChipPerBank)
        chipNum = package % numOfChipPerBank

        return bankNum,chipNum
    #End of GetBankAndChipNumberFromPackage()

    def __IsInjectingErrorOnControlData(self, errorLba):
        # RPG-12172 : Harish : 03-Jan-2017, Changed Hypothetical LBA calculations from Physical Address to Logical Address
        gatPageHypotheticalLba          = self.livet.GetLogicalCapacity() + Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_GAT_PAGE_HEADER
        mipPageHypotheticalLba          = self.livet.GetLogicalCapacity() + Constants.Setup_Config_CONSTANTS.BE_SPECIFIC_MIP_ID_BYTE_IN_HEADER
        igatPageHypotheticalLba         = self.livet.GetLogicalCapacity() + Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_IGAT_PAGE_HEADER
        gatDirectroyPageHypotheticalLba = self.livet.GetLogicalCapacity() + Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_GAT_DIRECTORY_PAGE_HEADER
        compactionInfoPointers          = self.livet.GetLogicalCapacity() + Constants.Setup_Config_CONSTANTS.COMPACTION_INFO_POINTERS
        contextLba                      = self.livet.GetLogicalCapacity() + Constants.Setup_Config_CONSTANTS.GC_CONTEXT_UGC_HEADER_ID
        contextBitmapLba                = self.livet.GetLogicalCapacity() + Constants.Setup_Config_CONSTANTS.GC_CONTEXT_UGC_BITMAP_HEADER_ID
        bootPageHypotheticalLba         = self.livet.GetLogicalCapacity() + Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_BOOT_PAGE_ID
        # RPG-17948 : Harish : 31-Oct-2017, Commented RGAT Page Header / RGAT Directory Page Header, as these are not there in Setup_Config.ini
        # Harish : 06 Nov 2017 : Reverted the comments, CONTROL_BLOCK_RGAT_ and CONTROL_BLOCK_RGAT_PAGE_HEADER  were same

        rgatPageHypotheticalLba         = self.livet.GetLogicalCapacity() + Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_RGAT_PAGE_HEADER
        rgatDirPageHypotheticalLba      = self.livet.GetLogicalCapacity() + Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_RGAT_DIRECTORY_PAGE_HEADER

        if errorLba == gatPageHypotheticalLba:
            self.logger.Info("", "[EIMediator] Injecting Error to GAT Page")
        elif errorLba == mipPageHypotheticalLba:
            self.logger.Info("", "[EIMediator] Injecting Error to MIP Page")
        elif errorLba == igatPageHypotheticalLba:
            self.logger.Info("", "[EIMediator] Injecting Error to IGAT Page")
        elif errorLba == gatDirectroyPageHypotheticalLba:
            self.logger.Info("", "[EIMediator] Injecting Error to GAT Directory Page")
        elif errorLba == compactionInfoPointers:
            self.logger.Info("", "[EIMediator] Injecting Error to Context Lba")
        elif errorLba == contextLba:
            self.logger.Info("", "[EIMediator] Injecting Error to Context Lba")
        elif errorLba == contextBitmapLba:
            self.logger.Info("", "[EIMediator] Injecting Error to Context Bitmap Lba")
        elif errorLba == bootPageHypotheticalLba:
            self.logger.Info("", "[EIMediator] Injecting Error to Boot block")

        #elif errorLba == rgatPageHypotheticalLba:
            #self.logger.Info("Injecting Error to RGAT Page")
        #elif errorLba == rgatDirPageHypotheticalLba:
            #self.logger.Info("Injecting Error to RGAT Directory Page")

        elif errorLba >= self.fwConfigObj.maxLba:
            raise Exception("[EIMediator] Trying to inject error on non-hypothetical LBA:0x%X and LBA:0x%X which is greater than max LBA:0x%X"%(errorLba, errorLba, self.fwConfigObj.maxLba))

        return
    #End of __IsInjectingErrorOnControlData()
    @staticmethod
    def GetEIObject():
        """
        Once the object is created there should
        be a way to get the EI object
        """
        return ErrorInjectionClass._staticErrorInjectionClassObj

    def UpdateCardMap(self,packageAddrList,startLba,trLen):
        """
        Description:
           * Update the cardmap in case of aborts
        """
        self.__sortedWordlineLbasList = []

        for count in range(0,len(packageAddrList)):
            self.__package = packageAddrList[count][0]
            self.__addr = packageAddrList[count][1]

            # Get the wordline lba's
            wordLineLbas = self.flash.GetWordlineLBAs(self.__package,self.__addr)
            startIndex = wordLineLbas[0] + 1

            # Form a list with valid lba's
            for lba in range(startIndex,len(wordLineLbas)):
                if (not wordLineLbas[lba] < 0) and (not wordLineLbas[lba] > 0):
                    self.__sortedWordlineLbasList.append(wordLineLbas[lba])

        # Update with unpredictable pattern for the wordline lbas
        for count in range(0,len(self.__sortedWordlineLbasList)):
            self.UpdateModelDataTrackingWithUnPredictablePattern(self.livet, self.__sortedWordlineLbasList[count], 1)

        # Update the current command with unpredictable pattern
        lbaList = list(range(startLba,(startLba + trLen)))
        for count in range(0,len(lbaList)):
            if not lbaList[count] in self.__sortedWordlineLbasList:
                self.UpdateModelDataTrackingWithUnPredictablePattern(self.livet, lbaList[count],1)

    def UpdateWordline(self, errorPhyAddress, blktype = None):
        """
        Only Applicable for Lambeau purple
        if Error being injected at WL 0,1,2,3 of SLC Block
        Change the WL to WL + 4 as we have 4 WL skip feature in case of purple
        """
        package, die, plane, block, wordLine = errorPhyAddress.chip, errorPhyAddress.die, errorPhyAddress.plane, errorPhyAddress.block, errorPhyAddress.wordLine

        if self.fwConfigObj.isBiCS:
            string = errorPhyAddress.string
        mlcLevel, eccPage = errorPhyAddress.mlcLevel, errorPhyAddress.eccPage

        if blktype == None:
            if self.fwConfigObj.isBiCS:
                blktype = self.livet.GetFlash().GetBlockType(package, (die, plane, block, wordLine, string, mlcLevel, 0))
            else:
                blktype = self.livet.GetFlash().GetBlockType(package, (die, plane, block, wordLine, mlcLevel, 0))

        #if blktype is SLC
        if blktype in [self.livet.pyBlockProgramState.bpsD1,self.livet.pyBlockProgramState.bpsErased,self.livet.pyBlockProgramState.bpsLowerPage,self.livet.pyBlockProgramState.bpsBinErase]:
            if errorPhyAddress.wordLine in [0,1,2,3]:
                errorPhyAddress.wordLine = errorPhyAddress.wordLine + self.file21Obj.numSLCWLToSkip

        return errorPhyAddress
    def CalculateHypotheticalLba(self,controlDataOffset):


        """
        Name       : CalculateHypotheticalLba
        Description: This function Calculates and returns the hypothetical Lba of the given input type of Control Data.The different offsets are:
         GAT           : CONTROL_BLOCK_GAT_PAGE_HEADER
         MIP           : BE_SPECIFIC_MIP_ID_BYTE_IN_HEADER
         BCI           : BE_SPECIFIC_BCI_ID_BYTE_IN_HEADER
         ICB           : CONTROL_BLOCK_ICB_PAGE_ID
         BOOT          : CONTROL_BLOCK_BOOT_PAGE_ID
         FSMAP         : CONTROL_BLOCK_FS_MAP_PAGE_HEADER
         FSNONMAP      : CONTROL_BLOCK_FS_NON_MAP_PAGE_HEADER
         GATDIRECTORY  : CONTROL_BLOCK_GAT_DIRECTORY_PAGE_HEADER
         IGAT          : CONTROL_BLOCK_IGAT_PAGE_HEADER
         ErrorLogEPWR  : GC_CONTEXT_EPWR_HEADER_ID
         ErrorLogUECC  : GC_CONTEXT_UECC_HEADER_ID
         ContextBlock  : GC_CONTEXT_HEADER_ID
        Arguments  : 1. controlDataOffset
        Returns    : hypotheticalLba
        """
        assert (controlDataOffset == Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_GAT_PAGE_HEADER\
                or controlDataOffset == Constants.Setup_Config_CONSTANTS.BE_SPECIFIC_MIP_ID_BYTE_IN_HEADER\
                or controlDataOffset == Constants.Setup_Config_CONSTANTS.BE_SPECIFIC_BCI_ID_BYTE_IN_HEADER\
                or controlDataOffset == Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_ICB_PAGE_ID\
                or controlDataOffset == Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_BOOT_PAGE_ID\
                or controlDataOffset == Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_FS_MAP_PAGE_HEADER\
                or controlDataOffset == Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_FS_NON_MAP_PAGE_HEADER\
                or controlDataOffset == Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_GAT_DIRECTORY_PAGE_HEADER\
                or controlDataOffset == Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_IGAT_PAGE_HEADER\
                or controlDataOffset == Constants.Setup_Config_CONSTANTS.GC_CONTEXT_EPWR_HEADER_ID\
                or controlDataOffset == Constants.Setup_Config_CONSTANTS.GC_CONTEXT_UECC_HEADER_ID\
                or controlDataOffset == Constants.Setup_Config_CONSTANTS.GC_CONTEXT_UGC_HEADER_ID\
                or controlDataOffset == Constants.Setup_Config_CONSTANTS.GC_CONTEXT_UGC_BITMAP_HEADER_ID\
                or controlDataOffset == Constants.Setup_Config_CONSTANTS.GC_CONTEXT_MLC_HEADER_ID\
                or controlDataOffset == Constants.Setup_Config_CONSTANTS.GC_CONTEXT_MLC_BITMAP_HEADER_ID\
                or controlDataOffset == Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_RGAT_PAGE_HEADER\
                or controlDataOffset == Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_RGAT_DIRECTORY_PAGE_HEADER),"The given control data offset does not belong to any control data type"

        # Calculate the Hypothetical Lba
        #hypotheticalLba = self.__cardPhysicalCapacity - self.__iniObj.CONTROL_ADDITIONAL_OFFSET + controlDataOffset
        hypotheticalLba = self.livet.GetLogicalCapacity() + controlDataOffset
        return hypotheticalLba

   # end of CalculateHypotheticalLba





    def GetHypotheticalLbaDict(self):




        """
        Name: GetHypotheticalLbaDict
        Description: This function Calculates all the hypothetical Lba's and returns the dictionary
        Arguments: None
        Returns: None
        """
        controlDataLBADict = {}
        # Calculate the Hypothetical Lba's
        controlDataLBADict['gat'] = self.CalculateHypotheticalLba(Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_GAT_PAGE_HEADER)
        self.__dictionaryOfStringsControlDataLbas[controlDataLBADict['gat']] = "gat"
        controlDataLBADict['mip'] = self.CalculateHypotheticalLba(Constants.Setup_Config_CONSTANTS.BE_SPECIFIC_MIP_ID_BYTE_IN_HEADER)
        self.__dictionaryOfStringsControlDataLbas[controlDataLBADict['mip']] = "mip"
        controlDataLBADict['bci'] = self.CalculateHypotheticalLba(Constants.Setup_Config_CONSTANTS.BE_SPECIFIC_BCI_ID_BYTE_IN_HEADER)
        self.__dictionaryOfStringsControlDataLbas[controlDataLBADict['bci']] = "bci"
        controlDataLBADict['icb'] = self.CalculateHypotheticalLba(Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_ICB_PAGE_ID)
        self.__dictionaryOfStringsControlDataLbas[controlDataLBADict['icb']] = "icb"
        controlDataLBADict['boot'] = self.CalculateHypotheticalLba(Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_BOOT_PAGE_ID)
        self.__dictionaryOfStringsControlDataLbas[controlDataLBADict['boot']] = "boot"
        controlDataLBADict['fsmap'] = self.CalculateHypotheticalLba(Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_FS_MAP_PAGE_HEADER)
        self.__dictionaryOfStringsControlDataLbas[controlDataLBADict['fsmap']] = "fsmap"
        controlDataLBADict['fsnonmap'] = self.CalculateHypotheticalLba(Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_FS_NON_MAP_PAGE_HEADER)
        self.__dictionaryOfStringsControlDataLbas[controlDataLBADict['fsnonmap']] = "fsnonmap"
        controlDataLBADict['gatDirectory'] = self.CalculateHypotheticalLba(Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_GAT_DIRECTORY_PAGE_HEADER)
        self.__dictionaryOfStringsControlDataLbas[controlDataLBADict['gatDirectory']] = "gatDirectory"
        controlDataLBADict['igat'] = self.CalculateHypotheticalLba(Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_IGAT_PAGE_HEADER)
        self.__dictionaryOfStringsControlDataLbas[controlDataLBADict['igat']] = "igat"
        controlDataLBADict['errorLogEPWR'] = self.CalculateHypotheticalLba(Constants.Setup_Config_CONSTANTS.GC_CONTEXT_EPWR_HEADER_ID)
        self.__dictionaryOfStringsControlDataLbas[controlDataLBADict['errorLogEPWR']] = "errorLogEPWR"
        controlDataLBADict['errorLogUECC'] = self.CalculateHypotheticalLba(Constants.Setup_Config_CONSTANTS.GC_CONTEXT_UECC_HEADER_ID)
        self.__dictionaryOfStringsControlDataLbas[controlDataLBADict['errorLogUECC']] = "errorLogUECC"
        controlDataLBADict['gcContextUGC'] = self.CalculateHypotheticalLba(Constants.Setup_Config_CONSTANTS.GC_CONTEXT_UGC_HEADER_ID )
        self.__dictionaryOfStringsControlDataLbas[controlDataLBADict['gcContextUGC']] = "gcContextUGC"
        controlDataLBADict['gcContextUGCBitmap'] = self.CalculateHypotheticalLba(Constants.Setup_Config_CONSTANTS.GC_CONTEXT_UGC_BITMAP_HEADER_ID )
        self.__dictionaryOfStringsControlDataLbas[controlDataLBADict['gcContextUGCBitmap']] = "gcContextUGCBitmap"
        controlDataLBADict['gcContextMLC'] = self.CalculateHypotheticalLba(Constants.Setup_Config_CONSTANTS.GC_CONTEXT_MLC_HEADER_ID )
        self.__dictionaryOfStringsControlDataLbas[controlDataLBADict['gcContextMLC']] = "gcContextMLC"
        controlDataLBADict['gcContextMLCBitmap'] = self.CalculateHypotheticalLba(Constants.Setup_Config_CONSTANTS.GC_CONTEXT_MLC_BITMAP_HEADER_ID )
        self.__dictionaryOfStringsControlDataLbas[controlDataLBADict['gcContextMLCBitmap']] = "gcContextMLCBitmap"
        controlDataLBADict['rgat'] = self.CalculateHypotheticalLba(Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_RGAT_PAGE_HEADER)
        self.__dictionaryOfStringsControlDataLbas[controlDataLBADict['rgat']] = "rgat"
        controlDataLBADict['rgatDirectory'] = self.CalculateHypotheticalLba(Constants.Setup_Config_CONSTANTS.CONTROL_BLOCK_RGAT_DIRECTORY_PAGE_HEADER)
        self.__dictionaryOfStringsControlDataLbas[controlDataLBADict['rgatDirectory']] = "rgatDirectory"



        return controlDataLBADict
   # end of GetHypotheticalLbaDict

    def UpdateModelDataTrackingWithUnPredictablePattern(self, livet,lba,trlength, LogInfo=True):
        dataTrackingHandle = livet.GetDataTracking()
        dataTrackingHandle.RequestDataPatternControl(True)
        if LogInfo:
            self.logger.Info("", "DataTracking: updating model for lba:0x%X for transferlength:0x%X"%(lba,trlength))
        dataTrackingHandle.UpdatePattern(lba,trlength, livet.dpUnpredictable)
        return

class StaticErrorInjectionStateClass(object):
    _errorOccurredType = None
    _errorInjectedType = None
    _updateCardMapReq  = False
    _mode = None
    _errorAffectedLbas = []

    def __init__(self):
        return

    def SetMostRecentErrorOccurredState(self, errorType, updateCardmap, mode=None):
        StaticErrorInjectionStateClass._errorOccurredType = errorType
        StaticErrorInjectionStateClass._updateCardMapReq  = updateCardmap
        StaticErrorInjectionStateClass._mode = mode

    def ResetMostRecentErrorOccurredState(self):
        StaticErrorInjectionStateClass._errorOccurredType = None
        StaticErrorInjectionStateClass._updateCardMapReq  = False
        StaticErrorInjectionStateClass._mode = None

    def GetMostRecentErrorOccurredState(self):
        return StaticErrorInjectionStateClass._errorOccurredType, StaticErrorInjectionStateClass._updateCardMapReq, StaticErrorInjectionStateClass._mode

    def SetListOfErrorAffectedLbas(self, errorAffectedLbas):
        StaticErrorInjectionStateClass._errorAffectedLbas.extend(errorAffectedLbas)

    def ResetListOfErrorAffectedLbas(self):
        StaticErrorInjectionStateClass._errorAffectedLbas = []

    def GetListOfErrorAffectedLbas(self):
        return StaticErrorInjectionStateClass._errorAffectedLbas





class ErrorInjectionUtilsClass(object):
    def __init__(self,testSpace):
        self.__logger    = testSpace.GetLogger()

        self.__fwConfigObj = FwConfig.FwConfig(testSpace)

        #Dictionary of Strings of all the control data structures(hypothetical lba's)
        self.__dictionaryOfStringsControlDataLbas = {}


    def LogWordlineLbas(self, chipNum, addr, wordLineLbas, headerString ="", logLbasOnlyForLowerPage = False):
        """
        Name        : LogWordLineLbas
        Description : This Function Logs the wordLine LBAs
        Arguments   : 1. wordLineLbas                 : list of LBAs in wordLine
                      2. headerString                 : Header string to log
                      3. logLbasOnlyForLowerPage      : check for if log the data only for Lower page alone
        Returns     : None
        """
        #decode the wordLineLbas
        numOfPagesInWordLine = wordLineLbas[0]
        numOfLbasPerPage     = []

        #get the number of sectors per pages
        for count in range(numOfPagesInWordLine):
            numOfLbasPerPage.append(wordLineLbas[count + 1])

        startIndexInList = numOfPagesInWordLine
        endIndexInList   = numOfPagesInWordLine

        self.__logger.Info("","----------------------------------------------------------------------------------------")
        for count in range(numOfPagesInWordLine):
            if logLbasOnlyForLowerPage:
                self.__logger.Info("","[EIMediator] LBA's in Wordline at Physical Location(chip:%d; die:%d; plane:%d ; block:0x%04X ; wordLine:0x%04X)at Lower page:%d "\
                                    %(chipNum,addr[0],addr[1],addr[2],addr[3],count))
            else:
                self.__logger.Info("","[EIMediator] LBA's in Wordline at Physical Location(chip:%d; die:%d; plane:%d ; block:0x%04X ; wordLine:0x%04X)at mlcLevel:%d "\
                                       %(chipNum,addr[0],addr[1],addr[2],addr[3],count))

            printString = ""

            startIndexInList =  endIndexInList + 1
            endIndexInList   = startIndexInList + numOfLbasPerPage[count] -1
            curNumOfLbasInOneline  = 0
            #Logging LBAs
            for lbaIndex in range(startIndexInList, endIndexInList + 1):
                lba = wordLineLbas[lbaIndex]
                if lba >=0 and lba <= self.__fwConfigObj.maxLba:
                    printString += "  0x%08X,"%lba
                elif lba > self.__fwConfigObj.maxLba:
                    if lba in list(self.__dictionaryOfStringsControlDataLbas.keys()):
                        printString += self.__dictionaryOfStringsControlDataLbas[lba].center(12)+","
                    else:
                        self.__logger.Info("","[EIMediator] MaxLba:0x%X Lba Received:0x%X"%(self.__fwConfigObj.maxLba,lba))
                        self.__logger.Info("","*************************************************")
                        self.__logger.Info("","[EIMediator] The Received Lba Going Beyond maxLba")
                        self.__logger.Info("","*************************************************")


                else:
                    printString += " INVALID LBA,"

                #check number of lbas in one Line of logger
                curNumOfLbasInOneline +=1

                #check for number of lbas in one line
                if curNumOfLbasInOneline%8 ==0:
                    self.__logger.Info("",printString)
                    printString = ""
            #End of inner for loop
            self.__logger.Info("",printString)

            #break the for outer loop if it is require to log only for lower page
            if logLbasOnlyForLowerPage:
                break
            #End of check
        #End of outer for loop
        self.__logger.Info("","----------------------------------------------------------------------------------------")

    #End of LogWordLineLbas
