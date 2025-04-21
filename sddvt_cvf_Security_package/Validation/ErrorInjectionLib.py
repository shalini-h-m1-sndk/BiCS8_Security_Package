#!/usr/bin/env python

##
# @file
# @brief Livet Way Point Handler Module
# @details this is a module for managing all way point operation
# @author Joydip Roy Chowdhury
# @date 14/04/2020
# @copyright (C) 2014 SanDisk Corporation
# @USAGE from Validation import ErrorInjectionLib as EI

from builtins import object
__author__ = "Joydip Roy Chowdhury"
__date__ = "14/04/2020"
__copyright__ = "Copyright (C) 2021 Western Digital Corporation"



import random
import CTFServiceWrapper as ServiceWrap
import Core.ValidationError as ValidationError
import Validation.CVFTestFactory as FactoryMethod
import Core.Configuration as Configuration
import Core.ProtocolFactory as ProtocolFactory

sysConfig = Configuration.ConfigurationManager().GetSystemConfiguration()
vtf_container = ProtocolFactory.ProtocolFactory.createVTFContainer(sysConfig.protocol)
exportProtocolName = (vtf_container.systemCfg.protocol)
exec("import Protocol.{0}.Basic.VTFContainer as VTF".format(exportProtocolName))
#import Protocol.ata.Basic.VTFContainer as VTF


class ErrorInjectionLib(object):

   """
    Description: Error injection library class
                 A library class which contains the Error Injection test APIs
    """
   # To retrieve the class object
   __staticObj = None
   errorInjObjCreated = False

   def __new__(cls, *args, **kwargs):
      """
      Description: To create singleton object of error injection class
      Parameters:
          @param: None
      Returns:
          @return: Error injection library object
      Exceptions:
          @exception: None
      """
      if not ErrorInjectionLib.__staticObj:
         ErrorInjectionLib.__staticObj = super(
            ErrorInjectionLib, cls).__new__(cls, *args, **kwargs)
      return ErrorInjectionLib.__staticObj

   def __init__(self):

      staticObj = None
      #if LivetWayPoint.__staticWayPointHandlerObjectCreated:
         #return
      #LivetWayPoint.__staticWayPointHandlerObjectCreated = True
      #super(LivetWayPoint, self).__init__()
      #LivetWayPoint.staticObj = self
      self.VTFContainer = VTF.VTFContainer()
      #self.livetObj = self.VTFContainer._livet
      self.CVFTestFactory = FactoryMethod.CVFTestFactory()
      self.TF = self.CVFTestFactory.factory.TestFixture
      if self.VTFContainer.isModel:
         self.livetObj = self.VTFContainer._livet
         self.flashObj = self.livetObj.GetFlash()

      self.onWriteAbortCallback = None
      self.onPreWriteAbortCallback = None
      self.onPostWriteAbortCallback = None
      self.onProgramFailureCallback = None
      self.onWL2WLShortCallback = None
      self.onProgramPowerGlitchCallback = None
      self.onReadPowerGlitchCallback = None
      self.onErasePowerGlitchCallback = None
      self.onEraseAbortCallback = None
      self.onPreEraseAbortCallback = None
      self.onPostEraseAbortCallback = None
      self.onEraseFailureCallback = None
      self.onLogicalTriggerCallback = None

      #  Definitions of different error types based on Livet API format
      if self.VTFContainer.isModel:
         self.errorTypeDef = {
            "PF": self.livetObj.etProgramError,
            "PA": self.livetObj.etProgramAbort,
            "PrePA": self.livetObj.etPreProgramAbort,
            "PostPA": self.livetObj.etPostProgramAbort,
            "EF": self.livetObj.etEraseError,
            "EA": self.livetObj.etEraseAbort,
            "PreEA": self.livetObj.etPreEraseAbort,
            "PostEA": self.livetObj.etPostEraseAbort,
            "WL2WL": self.livetObj.etWordlineShort,
            "CECC": self.livetObj.etBadBit,
            "UECC": self.livetObj.etBadPage,
         }

         #  Definitions of different error persistence based on Livet API format
         self.errorPersistenceDef = {
            "soft": self.livetObj.epSoft,
            "hard": self.livetObj.epHard,
            "permanent": self.livetObj.epPermanent
         }


   def GetLivetFlashOperation(self, flashoprn = "PF"):
      flashOperation = {}
      flashOperation = {
         "PF": self.livetObj.etProgramError,
         "PA": self.livetObj.etProgramAbort,
         "PrePA": self.livetObj.etPreProgramAbort,
         "PostPA": self.livetObj.etPostProgramAbort,
         "EF": self.livetObj.etEraseError,
         "EA": self.livetObj.etEraseAbort,
         "PreEA": self.livetObj.etPreEraseAbort,
         "PostEA": self.livetObj.etPostEraseAbort,
         "WL2WL": self.livetObj.etWordlineShort,
         "CECC": self.livetObj.etBadBit,
         "UECC": self.livetObj.etBadPage,
      }

      return flashOperation[flashoprn]

   def InjectPostPAOnLBA(self, errorLBA, errorPersistence, skipCount=None,
                         callbackFunc=None, countToOccur=None,
                         countToRecover=None):

      self.__InjectError(errorType="PostPA", errorPersistence=errorPersistence,
                         errorLBA=errorLBA, skipCount=skipCount,
                         callbackFunc=callbackFunc,
                         countToOccur=countToOccur,
                         countToRecover=countToRecover)
      self.TF.logger.Info("Post PA Error injection done through Livet API")

   def InjectPrePAOnLBA(self, errorLBA, errorPersistence, skipCount=None,
                        callbackFunc=None, countToOccur=None,
                        countToRecover=None):
      """
      Description: Inject Pre Program Abort on the given logical address.
                   Power loss simulated just before prgramming of page starts
      Parameters:
          @param: errorLBA - Set a logical trigger based on LBA read, written
                             or erased. The model identifies the physical
                             location involved and injects error there
          @param: errorPersistence - Persistence of error after occurrence
                               Can be soft,hard(cleared after block erase),
                               permanent(persists even after block erase)
          @param: skipCount - No. of logical flash operations to skip before
                              err injection. (Used only for logical triggers)
          @param: callbackFunc - Callback function to be invoked with the
                                 address details, after error injection done.
                                 If not mentioned, then default callback
                                 function will be used.
                                 (Used only for logical triggers)
          @param: countToOccur - Optional. Defines how many opportunities for
                                 failure occur before the error is actually
                                 triggered (defaults to 0)
          @param: countToRecover - Optional. Defines the number of failures
                                   before the error is removed. (Used only
                                   for soft errors, and defaults to 1)
      Returns:
          @return: None
      Exceptions:
          @exception: Errors in input parameters can cause assertion
      """

      self.__InjectError(errorType="PrePA", errorPersistence=errorPersistence,
                         errorLBA=errorLBA, skipCount=skipCount,
                         callbackFunc=callbackFunc,
                         countToOccur=countToOccur,
                         countToRecover=countToRecover)
      self.TF.logger.Info(
         "Pre PA Error injection done through Livet API")

      def InjectPAOnLBA(self, errorLBA, errorPersistence, skipCount=None,
                        callbackFunc=None, countToOccur=None,
                        countToRecover=None, progressLevel=None):
         """
         Description: Inject Program Abort on the given logical address
         Parameters:
             @param: errorLBA - Set a logical trigger based on LBA read, written
                                or erased. The model identifies the physical
                                location involved and injects error there
             @param: errorPersistence - Persistence of error after occurrence
                                  Can be soft,hard(cleared after block erase),
                                  permanent(persists even after block erase)
             @param: skipCount - No. of logical flash operations to skip before
                                 err injection. (Used only for logical triggers)
             @param: callbackFunc - Callback function to be invoked with the
                                    address details, after error injection done.
                                    If not mentioned, then default callback
                                    function will be used.
                                    (Used only for logical triggers)
             @param: countToOccur - Optional. Defines how many opportunities for
                                    failure occur before the error is actually
                                    triggered (defaults to 0)
             @param: countToRecover - Optional. Defines the number of failures
                                      before the error is removed. (Used only
                                      for soft errors, and defaults to 1)
             @param: progressLevel - Optional.Mentions the % level of prgramming
                                     at which abort error is injected
                                     0: Legacy behaviour.
                                     1: Abort happened very close to prgm start
                                     25: 25% of program time.
                                     50: 50% of program time.
                                     75: 75% of program time.
                                     99: Abort happened very close to prgm end
         Returns:
             @return: None
         Exceptions:
             @exception: Errors in input parameters can cause assertion
         """

         #  Set the default value of elem5 and 6 of error descr tuple as (0,0)
         errorDescExt = [0, 0]

         # If input param is present, define progressLevel as
         # element5 of the error description tuple
         if progressLevel is not None:
            if progressLevel not in set(PROGRAM_PROGRESS_LEVELS):
               self.globalVarsObj.logger.Fatal("Progress Level must be 0, 1, 25, 50, 75 or 99")
               raise validationError.ParametersError(
                  "", "Progress Level must be 0, 1, 25, 50, 75 or 99")
            else:
               errorDescExt[0] = progressLevel

         self.__InjectError(errorType="PA", errorPersistence=errorPersistence,
                            errorLBA=errorLBA, skipCount=skipCount,
                            callbackFunc=callbackFunc,
                            countToOccur=countToOccur,
                            countToRecover=countToRecover,
                            errorDescExt=errorDescExt)
         self.TF.logger.logger.Info(
            "PA Error injection done through Livet API")

   def __GetErrorDescription(self,errorType, errorPersistence, countToOccur, countToRecover,
                             errorDescExt):
      #self.errorTypeDef = {
         #"PF": self.livetObj.etProgramError,
         #"PA": self.livetObj.etProgramAbort,
         #"PrePA": self.livetObj.etPreProgramAbort,
         #"PostPA": self.livetObj.etPostProgramAbort,
         #"EF": self.livetObj.etEraseError,
         #"EA": self.livetObj.etEraseAbort,
         #"PreEA": self.livetObj.etPreEraseAbort,
         #"PostEA": self.livetObj.etPostEraseAbort,
         #"WL2WL": self.livetObj.etWordlineShort
      #}
      ##  Definitions of different error persistence based on Livet API format
      #self.errorPersistenceDef = {
         #"soft": self.livetObj.epSoft,
         #"hard": self.livetObj.epHard,
         #"permanent": self.livetObj.epPermanent
      #}

      errorDescription = (self.errorTypeDef[errorType],
                          self.errorPersistenceDef[errorPersistence],
                          countToOccur, countToRecover, errorDescExt[0],
                          errorDescExt[1])

      return errorDescription

   @staticmethod
   def LogicalTriggerCallback(lba, partition, flashOp, skipCount, errorDescr,
                              package, phyAddr):
      #cmd = CMDUtil()
      #TF = cmd.TestFixture()
      TF = ErrorInjectionLib.TestFixture()
      TF.logger.Info("Callback Occurred for %s\n" %(flashOp))
      TF.logger.Info("Error injected at LBA:0x%X, flashOp:%s, "
                     "skipCount:0x%X, errorDescription:%s, "
                     "package:0x%X, physicalAddress:%s"
                     % (lba, flashOp, skipCount, errorDescr,
                        package, phyAddr))
   @staticmethod
   def TestFixture():
      CVFTestFactory = FactoryMethod.CVFTestFactory()
      TF = CVFTestFactory.factory.TestFixture
      return TF

   def __InjectError(self, errorType, errorPersistence, errorLBA=None,
                     package=None, phyAddress=None, skipCount=None,
                     callbackFunc=None, countToOccur=None, countToRecover=None,
                     errorDescExt=None):

      flashOperation = {
         "PF": self.livetObj.foProgram,
         "EF": self.livetObj.foErase,
         "PA": self.livetObj.foProgram,
         "PrePA": self.livetObj.foProgram,
         "PostPA": self.livetObj.foProgram,
         "EA": self.livetObj.foErase,
         "PreEA": self.livetObj.foErase,
         "PostEA": self.livetObj.foErase,
         "WL2WL": self.livetObj.foProgram,
         "CECC": self.livetObj.foRead,
         "UECC": self.livetObj.foRead,
      }

      self.TF.logger.Info("Injecting error through Livet API")

      if countToOccur is None:
         countToOccur = 0
      if countToRecover is None:
         countToRecover = 1
      if errorDescExt is None:
         errorDescExt = [0, 0]

      errorDescription = self.__GetErrorDescription(
         errorType, errorPersistence, countToOccur, countToRecover,
         errorDescExt)

      if callbackFunc is not None:
         self.onLogicalTriggerCallback = callbackFunc
      if skipCount is None:
         skipCount = 0

      self.flashObj.SetLogicalTrigger(
         errorLBA, flashOperation[errorType], skipCount,
         errorDescription, self.__class__.LogicalTriggerCallback)

      self.TF.logger.Info(
         "%s injected on LBA:0x%08X" % (errorType, errorLBA))

