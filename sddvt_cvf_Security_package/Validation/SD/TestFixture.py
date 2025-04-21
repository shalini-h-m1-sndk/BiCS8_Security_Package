"""
################################################################################
# Copyright (c) SanDisk Corp.2013 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# FILE:TestFixture.py: Test file to Define all global Variables and do the setup
#              AUTHOR: Ravi G
################################################################################

################################################################################
#                            CHANGE HISTORY
# 2-November-2015    RG  Initial Revision of TestFixture.py
################################################################################
"""
from __future__ import division

from builtins import str
from builtins import range
from builtins import object
from past.utils import old_div
import os
import sys
import time
import datetime
import random
import math
import Protocol.NVMe.Basic.VTFContainer as VTF
import Core.ValidationError as ValidationError
import CTFServiceWrapper as ServiceWrap
import NVMeCMDWrapper as NVMeWrap
import Core.ProtocolFactory as ProtocolFactory

import Validation.SD.TestParams as TP

class TestFixture(object):

	#Test Variables.
	cmdsPerCycle = 100
	logger = None

	commndline = ''
	hostname = ''
	CTFVersion = ''
	cardCapacity = ''
	UECCErrorCount=0
	UECCCallBackCount = 0
	testName = None
	testOptions = dict()
	writtenLBAs = list()

	patternDict = dict()
	CVFExceptions = tuple()

	__staticObjTestFixture           = None
	__staticTestFixtureObjectCreated   = False
	nameSpaceID = 1

	def __new__(cls, *args, **kwargs):
		"""
		   Memory allocation ( This function use to create Singleton object of SystemVars)
		"""
		if not TestFixture.__staticObjTestFixture:
			TestFixture.__staticObjTestFixture = super(TestFixture, cls).__new__(cls, *args, **kwargs)
		return TestFixture.__staticObjTestFixture

	def __init__(self, testOptions = None, testName = None):

		#Condition to check if the variable is already created
		if TestFixture.__staticTestFixtureObjectCreated:
			return

		#Set the static variable of class such that the object gets created ONLY once
		TestFixture.__staticTestFixtureObjectCreated = True
		super(TestFixture, self).__init__()

		#self.VTFContainer = VTF.VTFContainer()
		self.VTFContainer = ProtocolFactory.ProtocolFactory.createVTFContainer("SD") #??????????
		self.testSession = self.VTFContainer.device_session
		self.configParser = self.testSession.GetConfigInfo()
		self.isAsynchronousMode =self.VTFContainer.cmd_line_args.AsyncMode
		self.logger = self.testSession.GetLogger()

		self.TAG = "TEST_TRACE"
		self.Latency_TAG = "LATENCY_TRACE"
		self.logger.SetTaggedDebugLevel(self.TAG, ServiceWrap.LOG_LEVEL_FATAL, False)
		#self.logger.SetTaggedDebugLevel(self.Latency_TAG, ServiceWrap.LOG_LEVEL_FATAL, False)

		'''
        self.logger.SetTaggedDebugLevel(self.TAG, ServiceWrap.LOG_LEVEL_INFO, False)
        self.logger.SetTaggedDebugLevel(self.TAG, ServiceWrap.LOG_LEVEL_MESSAGE, False)
        self.logger.SetTaggedDebugLevel(self.TAG, ServiceWrap.LOG_LEVEL_DEBUG, False)
        self.logger.SetTaggedDebugLevel(self.TAG, ServiceWrap.LOG_LEVEL_CTF_TRACE, False)
        self.logger.SetTaggedDebugLevel(self.TAG, ServiceWrap.LOG_LEVEL_WARN, False)
        self.logger.SetTaggedDebugLevel(self.TAG, ServiceWrap.LOG_LEVEL_ERROR, False)
        self.logger.SetTaggedDebugLevel(self.TAG, ServiceWrap.LOG_LEVEL_FATAL, False)
        '''

		if(0): #
			if self.VTFContainer.cmd_mgr:
				self.threadPool = self.VTFContainer.cmd_mgr.GetThreadPoolMgr()

				#Workaround till Re-Init issue on SDR5 is resolved.
				if self.VTFContainer.systemCfg.Host == "":

					#Set the command Manager Mode accordingly.
					if 1 == int(self.configParser.GetValue('queue_depth', 0)[0]):
						self.logger.Info( "*****************      RE INIT COMMAND MANAGER in CONTINUOS SYNC MODE      *****************\n")
						self.VTFContainer.ReInitThreadPool(nvmeQueueDepth = 1, isDeterministic = True)
					elif 0xFFFFFFFFFFFFFFFF == int(self.configParser.GetValue('queue_depth', 0)[0]):
						self.logger.Info( "*****************      RE INIT COMMAND MANAGER in CONTINUOS ASYNC MODE      *****************\n")
						self.VTFContainer.ReInitThreadPool(nvmeQueueDepth = -1, isDeterministic = True)
					elif 1 < int(self.configParser.GetValue('queue_depth', 0)[0]):
						if self.configParser.GetValue('thread_pool_deterministic', 0)[0]:
							self.logger.Info( "*****************      RE INIT COMMAND MANAGER in DETERMINISTIC SUSTAINED COMMAND MODE      *****************\n")
							self.VTFContainer.ReInitThreadPool(nvmeQueueDepth = self.configParser.GetValue('queue_depth', 0)[0], isDeterministic = True)
						else:
							self.logger.Info( "*****************      RE INIT COMMAND MANAGER in NON - DETERMINISTIC SUSTAINED COMMAND MODE      *****************\n")
							self.VTFContainer.ReInitThreadPool(nvmeQueueDepth = self.configParser.GetValue('queue_depth', 0)[0], isDeterministic = False)

				self.threadPool = self.VTFContainer.cmd_mgr.GetThreadPoolMgr()

			else:
				self.logger.Info(self.TAG, "*****************      COMMAND MANAGER IS NOT INITIALIZED. LOOKS LIKE IOQs ARE NOT CREATED      *****************\n")
		self.errorManager = self.testSession.GetErrorManager()
		self.SDerrorManager = self.testSession.GetErrorManager()


		self.NrofBytesWritten = 0
		self.NrofBytesRead = 0
		self.NrofWriteCmds = 0
		self.NrofReadCmds = 0
		self.NrofTrimCmds = 0
		self.NrofWUCCmds = 0
		self.NrofWrite0Cmds = 0
		self.NrofCmprCmds = 0
		self.isCMDMgrSwitch = False

		self.Mode3 = None
		if TP.SUSTAINED_Q_DEPTH == int(self.configParser.GetValue('thread_pool_manager_mode', 0)[0]):
			self.sustainedMode = True
		elif TP.CONTINUOUS_EXECUTION == int(self.configParser.GetValue('thread_pool_manager_mode', 0)[0]):
			self.Mode3 = True
		elif TP.SUSTAINED_CMD == int(self.configParser.GetValue('thread_pool_manager_mode', 0)[0]):
			self.Mode3 = True

		#Enable detailed Traces in Triton.log
		if self.VTFContainer.isModel:

			import Livet

			#host = Livet.GetNVMeHost()
			host = Livet.GetHost()
			host.TraceOn("shared_memory")
			host.TraceOn("hostdata_trace")
			host.TraceOn("PCIe_host")

			Root = Livet.GetRootObject()
			Root.TraceOn("api_calls")
			Livet.GetController().TraceOn("Triton_HimTop.all")

			'''
            dt = Livet.GetDataTracking()
            dt.TraceOn("data_tracking")
            Flash = Livet.GetFlash()
            Flash.TraceOn("data_erase")
            Flash.TraceOn("data_read")
            Flash.TraceOn("data_write")
            '''

		#By Default Enable Error/Fatal Traces.
		if not self.VTFContainer.cmd_line_args.enable_CTF_lib_traces:
			self.logger.SetTaggedDebugLevel("LIB_CMD", ServiceWrap.LOG_LEVEL_ERROR, False)
			self.logger.SetTaggedDebugLevel("LIB_BUFFER", ServiceWrap.LOG_LEVEL_ERROR, False)
			self.logger.SetTaggedDebugLevel("LIB_Data_Tracking", ServiceWrap.LOG_LEVEL_ERROR, False)
			self.logger.SetTaggedDebugLevel("LIB_ThreadPool", ServiceWrap.LOG_LEVEL_WARN, False)

		#if DT is enabled, initialize Pattern Index Map.
		if int(self.configParser.GetValue('datatracking_enabled', 0)[0]):
			bufferManager = self.testSession.GetDTBufferManager()
			#maxPatternID = bufferManager.GetMaxPatternID() # JIRA
			maxPatternID = 0xFF
			retainOtherPatternIDs = True
			patternTypes = [ServiceWrap.ALL_0, ServiceWrap.ALL_1, ServiceWrap.BYTE_REPEAT, ServiceWrap.RANDOM]

			for i in range(maxPatternID):
				patternInfo = ServiceWrap.PatternInfo()
				#patternInfo.patternType = random.choice(patternTypes)
				patternInfo.value = random.randint(0, 255)
				self.patternDict[i] = patternInfo
			#bufferManager.SetPatterns(self.patternDict, retainOtherPatternIDs)

		#If DT is not enabled construct default pattern dictionary.
		else:
			self.patternDict = {0 : 0x11, 1 : 0x22, 2 : 0x33, 3: 0x44, 4: 0x55}

		self.logger.SetDefaultDebugLevel(ServiceWrap.LOG_LEVEL_MESSAGE)
		self.CVFExceptions = (Exception, ServiceWrap.DataTrackingException, ServiceWrap.GenericException, ServiceWrap.PeripheralHWException, ServiceWrap.ModelException, ServiceWrap.CmdException,
				              ServiceWrap.ModelWaypointException, ServiceWrap.ModelIPCException, ServiceWrap.ModelException, ServiceWrap.LoggerException,
				              ServiceWrap.CVFTaskQueueException, ServiceWrap.ThreadPoolException, ServiceWrap.ConfigException, ServiceWrap.BufferException,
				              ServiceWrap.FatalException, ServiceWrap.GeneralException)

	def LogTestEnvironment(self):

		self.logger.Info( "**************LogTestEnvironment*******************\n")
		self.logger.Info( "*****************************************\n")


	def __GetChipConfiguration(self):

		import Validation.SctpUtils as SCTP
		self.UECCErrorCount=0
		#self.sctp = SCTP.SctpUtils()
		#mediaLayout = self.sctp.GetMediaLayout()
		#self.__LogMediaLayout(mediaLayout)

	def __LogMediaLayout(self, mediaLayout):

		self.logger.Message("\n>>>>>>>>>>>>>>>>>>>> MEDIA LAYOUT >>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
		self.logger.Message("%-35s: 0x%X"%('PlanesPerDie', mediaLayout['PlanesPerDie']))
		self.logger.Message("%-35s: 0x%X"%('LogicalChipCount', (mediaLayout['LogicalChipCount'])))
		self.logger.Message("%-35s: 0x%X"%('PhysicalChipCountPerChannel', (mediaLayout['PhysicalChipCountPerChannel'])))
		self.logger.Message("%-35s: 0x%X"%('DiePerPhysicalChip', (mediaLayout['DiePerPhysicalChip'])))
		self.logger.Message("%-35s: 0x%X"%('BlockPerChip', (mediaLayout['BlockPerChip'])))
		self.logger.Message("%-35s: 0x%X"%('ChannelCount', (mediaLayout['ChannelCount'])))
		self.logger.Message("%-35s: 0x%X"%('StarNumber', (mediaLayout['StarNumber'])))

	def __GetCardCapacity(self):
		cardCapacity = [128, 256, 400, 512, 1024]
		capacityInGB = old_div((self.nsCap * 512), (1024 * 1024 * 1024))

		for capacity in cardCapacity:
			if capacity > capacityInGB:
				self.cardCapacity = str(capacity) + ' GB'
				return self.cardCapacity