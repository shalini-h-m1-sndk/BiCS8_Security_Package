#!/usr/bin/env python

##
# @file
# @brief Livet Way Point Handler Module
# @details this is a module for managing all way point operation
# @author Joydip Roy Chowdhury
# @date 14/04/2020
# @copyright (C) 2014 SanDisk Corporation
# @USAGE from Validation import GlobalCounter as WP

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



class GlobalCounter(object):

   def __init__(self):
      self.VTFContainer = VTF.VTFContainer()
      self.livetObj = self.VTFContainer._livet
      self.CVFTestFactory = FactoryMethod.CVFTestFactory()
      self.TF = self.CVFTestFactory.factory.TestFixture
      self.defaultdict = {"LBA":0, "TransferLength":8}



   def UpdateCounter(self, LBA = 0, TransferLength = 8):
      self.defaultdict["LBA"] = LBA
      self.defaultdict["TransferLength"] = TransferLength
      global LbaTl
      LbaTl = self.defaultdict

   def GetCounter(self):

      return LbaTl

class GlobalList(object):

   def __init__(self):
      self.VTFContainer = VTF.VTFContainer()
      self.livetObj = self.VTFContainer._livet
      self.CVFTestFactory = FactoryMethod.CVFTestFactory()
      self.TF = self.CVFTestFactory.factory.TestFixture
      self.defaultPVLst = []
      self.defaultResetLst = []

   def FillProtocolViolationErrorList(self):


      self.defaultPVLst.insert(0, 0xC)
      self.defaultPVLst.insert(0, 0xE)
      self.defaultPVLst.insert(0, 0x16)


   def GetProtocolErrorList(self):
      self.FillProtocolViolationErrorList()
      return self.defaultPVLst

   def FillResetErrorList(self):

      self.defaultResetLst.insert(0, 0xD)
      self.defaultResetLst.insert(0, 0xE)
      self.defaultResetLst.insert(0, 0x10)

   def GetResetErrorList(self):
      self.FillProtocolViolationErrorList()
      return self.defaultResetLst