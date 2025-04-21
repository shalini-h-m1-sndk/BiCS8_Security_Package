#!/usr/bin/env python

##
# @file
# @brief Way Point Handler Module
# @details this is a module for managing all way point operation
# @author Hemi Paska
# @date 23/03/2013
# @copyright (C) 2014 SanDisk Corporation


# Revision History
# 1. Programmed and Alpha release version (Hemi Paska, 23Jan 2014)
# 2. Added Dummy waypoint                 (Hemi Paska, 30Mrc 2014)
# 2. Import To VTF                        (Hemi Paska, 02Nov 2014)


from builtins import str
from builtins import object
import Core.ValidationError as ValidationError
#import GlobalVars
##
# @brief the Way Point Object class
# @details This class is used for holding all necessary data per way point
# @param wayPointName = the name of the way point according to FW
# @param wayPointFunction = a list of functions to run on call back
# @param PrintArguments = and indicator if the arguments ahold be printed on callback
# @param numberOfCall = hold the number of time the way poiny occured
# @param regEventKey = the event key of the way point
# @param isDummy = indicate if the way point is dummy and we need to read arg from XML
# @param dummyArgumentCounter = this is for dummy argument read from file
class WayPointObject(object):
   def __init__(self,wayPointName):
      self.wayPointName         = wayPointName
      self.wayPointFunction     = []
      self.printArguments       = False
      self.numberOfCall         = 0
      self.regEventKey          = 0
      self.isDummy              = False
      self.dummyArgumentCounter = 0
      self.isLivet              = False
      self.LivetCallBackFunc    = lambda package, address: WayPointHandler.CallBackFunc(wayPointName , package, address)




##
# @brief the Way Point Handler class
# @details This class is used for mannaging all way point operation :
# Register, unRegister, counters, dummyWP(in the future)
class WayPointHandler(object):

   __wayPointObjects   = {}
   __activeWayPoints   = {}

   ################################################################################
   ##                   Internal calculations and methods                        ##
   ################################################################################
   def __init__(self, livet, Logger):

      self._logger = Logger
      self._livet  = livet
   ##
   # @brief This method generates a list of arguments(from XML) for specific way point
   # @details This method receive a awy point name and the creating a list of arguments
   # from XML file, the list is the structure of the way point arguments
   # @param wayPointName = the name of the way point to generate arguments for.
   # @return This method returns a list [eventKey, args, processorID]
   @staticmethod
   def __GetWayPointArguments(wayPointName):
      wayPointObj = WayPointHandler.__wayPointObjects[wayPointName]
      xmlDoc = minidom.parse('WayPointArguments.xml')
      itemlist = xmlDoc.getElementsByTagName(wayPointName)
      eventKey = int(itemlist[wayPointObj.dummyArgumentCounter].attributes['eventKey'].value)
      args = itemlist[wayPointObj.dummyArgumentCounter].attributes['args'].value
      processorID = int(itemlist[wayPointObj.dummyArgumentCounter].attributes['processorID'].value)
      wayPointObj.dummyArgumentCounter+=1
      args = args.split(',')
      returnList = []
      for arg in args:
         returnList.append(int(arg))
      return [eventKey,returnList,processorID]

   ##
   # @brief A function that calls a printing function of a way point
   # @details this function sets the logger level to print if needed, and calls the basic
   # printing function of the way point.
   # @param wayPointName string - as defined in F/W
   # @param eventKey of waypoint - as defined in F/W
   # @param args
   # @param processorID
   @staticmethod
   def __printWayPointArguments(wayPointName, eventKey, args, processorID):

      WayPointHandler._logger.Info("","%s way point occured, Aruguments :  %s"%(WayPointHandler.__activeWayPoints[eventKey],str(args[:])))

   ##
   # @brief this is the global call cak function
   # @details all the way point are register only to this function.
   # this function gets the the relevant way point object and then call all of the
   # function in the call back list of the specific way point
   # @param eventKey of waypoint - as defined in F/W
   # @param args
   # @param processorID
   # @return return 1
   @staticmethod
   def CallBackFunc(eventKey, args, processorID):
      #get the way point object
      wayPointName = WayPointHandler.__activeWayPoints[eventKey]
      WayPointObj = WayPointHandler.__wayPointObjects[wayPointName]
      #update the way point call counter
      WayPointObj.numberOfCall += 1
      #print if needed
      if  WayPointObj.printArguments:
         WayPointHandler.__printWayPointArguments(wayPointName, eventKey, args, processorID)

      #activate all the function registers to the way point
      for wayPointFunction in WayPointObj.wayPointFunction:
         wayPointFunction(eventKey, args, processorID)

      if WayPointObj.wayPointFunction!=[] :
         #set the way point object
         WayPointHandler.__wayPointObjects[wayPointName] = WayPointObj
      return 1

   ################################################################################
   ##                             External methods                               ##
   ################################################################################

   ##
   # @brief This is a  call back that handles manual trigger for way point
   # @details This method receives a way point name and activate the way point
   # functions. if all argument are null the function will load arguments from XML file
   # @param wayPointName - as defined in F/W
   # @param eventKey
   # @param args
   # @param processorID
   # @return This methud returns 1
   def TriggerWayPoint(self, wayPointName, eventKey = None, args = None, processorID =  None):
      #check if way point is registered
      if wayPointName not in list(WayPointHandler.__wayPointObjects.keys()):
         WayPointHandler._logger.Info("",'Way point %s not registered'%wayPointName)
         raise  ValidationError.TestFailError(self.fn, ("Way point %s not registered" %(wayPointName)))
      #get the way point object
      WayPointObj = WayPointHandler.__wayPointObjects[wayPointName]
      #update the way point call counter
      WayPointObj.numberOfCall = WayPointObj.numberOfCall + 1
      #check if call back args exist
      if (eventKey == None and args == None and processorID == None ):
         #if not, load from file
         [eventKey, args, processorID] = WayPointHandler.__GetWayPointArguments(wayPointName)
      #print if needed
      if  WayPointObj.printArguments:
         WayPointHandler.__printWayPointArguments(wayPointName,eventKey, args, processorID)

      #activate all the function registers to the way point
      for wayPointFunction in WayPointObj.wayPointFunction:
         wayPointFunction(eventKey, args, processorID)

      #set the way point object
      WayPointHandler.__wayPointObjects[wayPointName] = WayPointObj
      return 1

   ##
   # @brief This will register way points for functions
   # @details This method receives a dictionary consist of way points names and
   # a list of fucntion for every way point. The function register every list to
   # the relavant waypoint.
   # @param wpDict is the dictionary that holds the way points and the relevant functions
   # Example:
   # wpDict = { 'D_MODEL_MB_RELOCATION_COMPLETED' : [Relocation.RelovationCallBackFunc],
   #            'D_MODEL_CVD_BLOCK_CLOSED'        : ['PrintArguments',Relocation.RelocationCallBackFunc],
   #            'Way Point Name'                  : [ Function pointer List ]}
   # @param preProductionFlag [int] this param is set to 0 by default. If equals 1 than test will not
   # fail if WP registration status was 0 (registration done pre production of the device)
   # @return This method returns a dictionary of way points that registered
   # @exception In case of failure in register way point (waypoint not registered) an exception will raise
   def RegisterWP(self, wpDict, preProductionFlag=0):
      wayPointRegistered = {}
      for wayPointName in wpDict:
         #check if way point alredy registered
         if (wayPointName in list(self.__wayPointObjects.keys())):
            wayPointObj = WayPointHandler.__wayPointObjects[wayPointName]
         else:
            #in case way point not registered
            wayPointObj = WayPointObject(wayPointName)
            #Check if the way point is dummy or real way point
            if 'isDummy' not in wpDict[wayPointName]:

               #Livet Way Point
               if ("lc" in wayPointName):
                  livetAttr  = getattr(self._livet, wayPointName)
                  self._livet.RegisterLivetCallback(livetAttr,wayPointObj.LivetCallBackFunc)
                  self._logger.Info("","[WayPointHandler] %s Way Point Registration is successful "%wayPointName)
                  regEventKey = wayPointName
               #Firmware Way Point
               else:
                  #in case of a real way point Register the the way point to class basic callback
                  regEventKey = self._livet.RegisterFirmwareWaypoint(wayPointName, WayPointHandler.CallBackFunc)
                  #check if registration was successful. Only check for WP that are registered after production
                  if (regEventKey==0 and preProductionFlag==0):
                     raise  ValidationError.TestFailError(self.fn, ("%s Register Failed (regEventKey=0)" % (wayPointName)))
                  self._logger.Info("","[WayPointHandler] %s Way Point Registration is successful (regEventKey = %d)"%(wayPointName, regEventKey))

            else:
               #in case of a Dummy way point
               wpDict[wayPointName].pop(wpDict[wayPointName].index('isDummy'))
               wayPointObj.isDummy = True
               regEventKey = 0
            # after register was seccessful update rest of data
            WayPointHandler.__activeWayPoints[regEventKey] = wayPointName
            wayPointObj.wayPointName = wayPointName
            wayPointObj.regEventKey = regEventKey

            wayPointRegistered[wayPointName]=regEventKey
         # make sure not to add 'PrintArguments'  more then once
         if 'PrintArguments' in wpDict[wayPointName]:
            wayPointObj.printArguments = True
            wpDict[wayPointName].pop(wpDict[wayPointName].index('PrintArguments'))

         #add the way point fucntion list to activate if not already in list
         funcInList = False
         if wayPointName in WayPointHandler.__wayPointObjects:
            for fucntion in WayPointHandler.__wayPointObjects[wayPointName].wayPointFunction:
               if fucntion.__name__ == wpDict[wayPointName][0].__name__:
                  funcInList = True

         if not funcInList:
            wayPointObj.wayPointFunction.extend(wpDict[wayPointName])
         WayPointHandler.__wayPointObjects[wayPointName] = wayPointObj
      return wayPointRegistered

   ##
   # @brief This will unregister way points for functions
   # @details This method receives a dictionary consist of way points names and
   # a list of fucntion for every way point. The function un register the
   # functions from the way points.
   # @param wpDict is the dictionary that holds the way points and the relevant functions
   # Example:
   # wpDict = { 'D_MODEL_MB_RELOCATION_COMPLETED' : [Relocation.RelovationCallBackFunc],
   #            'D_MODEL_CVD_BLOCK_CLOSED'        : ['PrintArguments',Relocation.RelocationCallBackFunc],
   #            'Way Point Name'                  : [ Function pointer List ]}
   # @return This methud return no value

   def UnRegisterWP(self, wpDict):
      for wayPointName in wpDict:
         wayPointObj = WayPointHandler.__wayPointObjects[wayPointName]
         if ('All' in wpDict[wayPointName]):
            wpDict[wayPointName] =  wayPointObj.wayPointFunction
         if ('PrintArguments' in wpDict[wayPointName]):
            wayPointObj.printArguments = False
            wpDict[wayPointName].pop(wpDict[wayPointName].index('PrintArguments'))
         #remove all the function form the list
         listfuncToRemove = []
         listfuncToRemove.extend(wpDict[wayPointName])
         for functionToRemove in listfuncToRemove:
            try:
               wayPointObj.wayPointFunction.pop(wayPointObj.wayPointFunction.index(functionToRemove))
            except Exception as exc:
               self._logger.Info("", ("[RegisterWaypoints] In %s UnRegister Nonexisting function %s(regEventKey=0)" % (wayPointName,functionToRemove)))
               raise exc
         #if there is no function left, unregister the way point
         if  wayPointObj.wayPointFunction == [] and wayPointObj.printArguments == False:
            # pop the Way point from the dictionary
            WayPointHandler.__wayPointObjects.pop(wayPointName)
            WayPointHandler.__activeWayPoints.pop(wayPointObj.regEventKey)
            #Livet Way Point
            if ("lc" in wayPointName):
               livetAttr  = getattr(self._livet, wayPointName)
               self._livet.UnregisterLivetCallback(livetAttr)
               self._logger.Info("","[WayPoint Handler] UnRegister Waypoints %s is successful " % wayPointName)
            else:
               regEventKey = self._livet.RegisterFirmwareWaypoint(wayPointName, None)
               self._logger.Info("","[WayPoint Handler] UnRegister Waypoints %s is successful (regEventKey = %d)"%(wayPointName, regEventKey))
         else:
            WayPointHandler.__wayPointObjects[wayPointName] = wayPointObj

   ##
   # @brief This will unregister all way points
   # @details This method will unregister all way points
   def UnRegisterAllWP(self):
      registeredWpList = self.GetActiveWayPoint()
      for wpName in registeredWpList:
         self.UnRegisterWP({wpName : "All"})
      self._logger.Info("","[WayPoint Handler] All WayPoint Hnadler Way Points Unregistered Successfully|")
   ##
   # @brief This will returns a list of the active way points
   # @details This method checks which way point are activated and
   # return a list of the active one
   # @return This method return a list of active way points
   def GetActiveWayPoint(self):
      activeWayPointsList = []
      for key, value in list(WayPointHandler.__activeWayPoints.items()):
         activeWayPointsList.append(value)
      return activeWayPointsList

   ##
   # @brief This method return a list of call back function of the way point
   # @details
   # @param wayPointName = the way point name to return function list for.
   # @return This method return a list of call back function of the way point
   def GetCallBackList(self, wayPointName):
      #check if way point is registered
      if wayPointName not in list(WayPointHandler.__wayPointObjects.keys()):
         WayPointHandler._logger.Info("",'Way point %s not registered'%wayPointName)
         return []
      functionList = []
      # append the call back names to function list
      for fucntion in WayPointHandler.__wayPointObjects[wayPointName].wayPointFunction:
         functionList.append[fucntion.__name__]
      #add print arguments flag if activeted
      if WayPointHandler.__wayPointObjects[wayPointName].printArguments:
         functionList.append['PrintArguments']
      return functionList
   ##
   # @brief This method return a the number of times the way point occurred
   # @details
   # @param wayPointName = the way point name
   # @return This method return a int counter of what point,if way point not registerd return None
   def GetWPCounter(self, wayPointName):
      if wayPointName not in list(WayPointHandler.__wayPointObjects.keys()):
         WayPointHandler._logger.Info("",'Way point %s not registered'%wayPointName)
         return None
      return self.__wayPointObjects[wayPointName].numberOfCall


