from builtins import hex
from builtins import object
import time
import os
import sys
import random
import inspect
import collections

import CTFServiceWrapper as ServiceWrap
import NVMeCMDWrapper as NVMeWrap

import Validation.CMDUtil as CU
import Validation.TestFixture as TestFixture
import Protocol.NVMe.Basic.TestCase as TestCase
import Core.ValidationError as  ValidationError
import Validation.TestParams as TP

import Validation.WayPointHandler as WayPointHandler

class WayPointObject(object):
    def __init__(self,wayPointName):
        self.wayPointName         = wayPointName
        self.wayPointCount        = 0

class Waypoint_Callback(TestCase.TestCase):
    def __init__(self):
        self.TF = TestFixture.TestFixture()
        self.CU = CU.CMDUtil()
        self.bufferManager = self.TF.testSession.GetDTBufferManager()
        self.maxPatternID = self.bufferManager.GetMaxPatternID()

    def RegistreWayPoint(self, WPCallBack_List):
        self.wayPointName = WPCallBack_List
        self.TF.logger.Info(" ********   Register WayPoint Call Back  ******** ")
        #for i in WPCallBack_List:
            #ListWP = str(WPCallBack_List[i])
        self.WayPointToRegister = {
            self.wayPointName  : [self.waypointCallback]
                                   }
        self.LivetObj = self.TF.VTFContainer.GetLivet()
        self.wayPointHandlerObj = WayPointHandler.WayPointHandler(self.LivetObj, self.TF.logger)
        self.wayPointHandlerObj.RegisterWP(self.WayPointToRegister)
        self.TF.logger.Fatal(" ******** Register WayPoint Call Back Completed ******** ")

    def GetWaypointCount(self):
        return self.wayPointCount

    def GetWayPoint(self, WayPoint):
        # Get Format Cmd Way points
        if WayPoint == "FMT_BEFOR":
            return 'WP_FWR_FORMAT_BEFORE_FTL'
        if WayPoint == "FMT_AFTER":
            return 'WP_FWR_FORMAT_AFTER_FTL'
        if WayPoint == "FORMAT_AFTER_ALOCATION_BLOCK":
            return 'WP_FWR_FORMAT_AFTER_ALOCATION_BLOCK'
        if WayPoint == "RestCmd":
            # Reset WayPoints
            #return "WP_FWR_RESET" #'''Working'''
            return "WP_SEC_RESET_HANDLING" #'''Working'''
            #return "WP_PS_UT_ENTER_RESET" -
            #return "WP_PS_UT_EXIT_RESET"
            #return "WP_PS_EF_04_RESET_DIE"
            #return "WP_PS_UEBM_UECC_FLIPFLOP_RESET"
            #return "WP_SAT_PARTIAL_RESET_COMPLETE"
            #return "WP_FWR_RESET_DETAILES"


    def exceptionCallback(self, ErrorGroup, ErrorCode):
        try:
            self.TF.logger.Info("**************   Exception Call Back invoked ******************* \n ")
            self.TF.logger.Info("**************  Details of Exception Call Back *****************  ")
            if len (list(TP.SCT.keys())) >= ErrorGroup:
                self.TF.logger.Info("%-35s: %s - [%s]"%('ErrorGroup', hex(ErrorGroup), (list(TP.SCT.keys())[ErrorGroup]) ))
            else:
                self.TF.logger.Info("%-35s: %s "%('ErrorGroup', hex(ErrorGroup) ))
            if len(list(TP.SC.keys())) >= ErrorCode:
                self.TF.logger.Info("%-35s: %s - [%s]"%('ErrorCode', hex(int(ErrorCode)) , (list(TP.SC.keys())[list(TP.SC.values()).index(int(ErrorCode))]) ))
            else:
                self.TF.logger.Info("%-35s: %s "%('ErrorCode', hex(int(ErrorCode)) ))
            self.TF.logger.Info("%-35s: %s "%('ErrorCmd', self.TF.testSession.GetErrorManager() ))
            self.TF.logger.Info("%-35s: %s\n"%('ErrorDescription',self.TF.testSession.GetErrorManager().GetErrorDescription(ErrorCode,ErrorGroup)))


            if ((ErrorGroup == TP.SCT['GENERIC_COMMAND_STATUS']) and (ErrorCode == TP.SC['FORMAT_IN_PROGRESS'])):
                self.TF.testSession.GetErrorManager().ClearAllErrors(ErrorGroup, ErrorCode)
            elif ((ErrorGroup == TP.SCT['GENERIC_COMMAND_STATUS']) and (ErrorCode == TP.SC['INVALID_NAMESPACE_FORMAT'])) :
                self.TF.testSession.GetErrorManager().ClearAllErrors(ErrorGroup, ErrorCode)
            elif ((ErrorGroup == TP.SCT['GENERIC_COMMAND_STATUS']) and (ErrorCode == TP.SC['INVALID_FIELD'])) :
                self.TF.testSession.GetErrorManager().ClearAllErrors(ErrorGroup, ErrorCode)
            elif ((ErrorGroup == TP.SCT['GENERIC_COMMAND_STATUS']) and (ErrorCode == TP.SC['NAMESPACE_NOT_READY'])) :
                self.TF.testSession.GetErrorManager().ClearAllErrors(ErrorGroup, ErrorCode)
            elif ((ErrorGroup == 0x37) and (ErrorCode == 0xFF0B)) :
                self.TF.testSession.GetErrorManager().ClearAllErrors(ErrorGroup, ErrorCode)
            else:
                self.TF.logger.Fatal(" No Valid Error Group and Error Code toClean up in Exception Call Back \n ")
                raise ValidationError.CVFGenericExceptions("", "Failed \n")
        except ValidationError.CVFExceptionTypes as ex:
            self.TF.logger.Fatal("Failed in Exception Call Back. Exception Message is ->\n %s "%ex.GetFailureDescription())
            raise ValidationError.CVFGenericExceptions("", "Failed in Wxception Call back\n")

    def UnRegisterWP(self, WayPointToRegister):
        self.TF.logger.Fatal(" ********  Un-Register WayPoint Call Back ******** ")
        self.wayPointName = WayPointToRegister
        self.WayPointToRegister = {self.wayPointName  : [self.waypointCallback]}
        self.wayPointHandlerObj.UnRegisterWP(self.WayPointToRegister)
        self.TF.logger.Fatal(" ******** Un-Register WayPoint Call Back Completed ******** ")
