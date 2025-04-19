
"""
################################################################################
# Copyright (c) SanDisk Corp.2013 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# FILE:SCTPUtils.py: Utility to construct and send SCTP Commands.
#            AUTHOR: Ravi G
################################################################################
"""
from __future__ import division

from builtins import object
from past.utils import old_div
import sys, os, time, shutil, datetime, random, string, subprocess, csv
from array import *

import CTFServiceWrapper as ServiceWrap
import NVMeCMDWrapper as NVMeWrap
import Core.ValidationError

import Validation.SD.TestFixture as TestFixture
import Validation.SD.TestParams as TP

#**************************************************************************************************************
##
# @brief Runs all the variations in the testObject
# @details
# @return None
# @exception None
#**************************************************************************************************************
class SctpUtils(object):
	def __init__(self):
		self.TF = TestFixture.TestFixture()

	#**************************************************************************************************************
	# This method is used to send Identify Device (0xEC)
	# This method sends a SCTP Command 0xEC
	# Param None
	# return dataBuffer
	# exception None
	#**************************************************************************************************************
	def IdentifyDrive(self):

		dataBuffer = ServiceWrap.Buffer.CreateBuffer(dataSize = 8, patternType = ServiceWrap.ALL_0, isSector = True)
		diagCommand = ServiceWrap.DIAG_FBCC_CDB()

		diagCommand.cdb = [TP.IDENTIFYDRIVE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		diagCommand.cdbLen = CDBLENGTH_16

		self.TF.logger.Info("Sending IDENDIFY DRIVE CDB: %s"%diagCommand.cdb)
		self.TF.logger.Info("Buffer Size: %d Bytes"%dataBuffer.GetBufferSize())
		sctpCommand = ServiceWrap.SCTPCommand.SCTPCommand(diagCommand, dataBuffer, ServiceWrap.DIRECTION_OUT)
		sctpCommand.Execute()

		return dataBuffer

	#**************************************************************************************************************
	# This method is used to send Write Port (0x8C)
	# This method sends a SCTP Command 0x8C
	# param None
	# return dataBuffer
	# exception None
	#**************************************************************************************************************
	def WritePort(self, option = TP.AUXSpace, address = 0, sectorCount = 1, dataPattern = ServiceWrap.ALL_1):

		dataBuffer = ServiceWrap.Buffer.CreateBuffer(dataSize = sectorCount, patternType = ServiceWrap.ALL_1, isSector = True)
		diagCommand = ServiceWrap.DIAG_FBCC_CDB()

		cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

		cdb[0] = TP.WRITEPORT
		cdb[1] = 0
		cdb[2] = option & 0x00FF
		cdb[3] = option & 0xFF00
		cdb[4] = address & 0x000000FF
		cdb[5] = address & 0x0000FF00
		cdb[6] = address & 0x00FF0000
		cdb[7] = address & 0xFF000000
		cdb[8] = sectorCount & 0x000000FF
		cdb[9] = sectorCount & 0x0000FF00
		cdb[10] = sectorCount & 0x00FF0000
		cdb[11] = sectorCount & 0xFF000000
		cdb[12] = cdb[13] = cdb[14] = cdb[15] = 0

		diagCommand.cdb = cdb
		diagCommand.cdbLen = TP.CDBLENGTH_16

		self.TF.logger.Info("Sending WRITE PORT CDB: %s"%diagCommand.cdb)
		self.TF.logger.Info("Buffer Size: %d Bytes"%dataBuffer.GetBufferSize())
		sctpCommand = ServiceWrap.SCTPCommand.SCTPCommand(diagCommand, dataBuffer, ServiceWrap.DIRECTION_IN)
		sctpCommand.Execute()

		return dataBuffer

	#**************************************************************************************************************
	# This method is used to send Read Port (0x8D)
	# This method sends a SCTP Command 0x8D
	# @param None
	# @return dataBuffer
	# @exception None
	#**************************************************************************************************************
	def ReadPort(self, option = TP.AUXSpace, address = 0, sectorCount = 1):

		dataBuffer = ServiceWrap.Buffer.CreateBuffer(dataSize = sectorCount, patternType = ServiceWrap.ALL_0, isSector = True)
		diagCommand = ServiceWrap.DIAG_FBCC_CDB()

		cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

		cdb[0] = TP.READPORT
		cdb[1] = 0
		cdb[2] = option & 0x00FF
		cdb[3] = option & 0xFF00
		cdb[4] = address & 0x000000FF
		cdb[5] = address & 0x0000FF00
		cdb[6] = address & 0x00FF0000
		cdb[7] = address & 0xFF000000
		cdb[8] = sectorCount & 0x000000FF
		cdb[9] = sectorCount & 0x0000FF00
		cdb[10] = sectorCount & 0x00FF0000
		cdb[11] = sectorCount & 0xFF000000
		cdb[12] = cdb[13] = cdb[14] = cdb[15] = 0

		diagCommand.cdb = cdb
		diagCommand.cdbLen = TP.CDBLENGTH_16

		self.TF.logger.Info("Sending READ PORT CDB: %s"%diagCommand.cdb)
		self.TF.logger.Info("Buffer Size: %d Bytes"%dataBuffer.GetBufferSize())
		sctpCommand = ServiceWrap.SCTPCommand.SCTPCommand(diagCommand, dataBuffer, ServiceWrap.DIRECTION_OUT)
		sctpCommand.Execute()

		return dataBuffer

	#**************************************************************************************************************
	# This method is used to send WriteFileSystem (0x8B)
	# This method sends a SCTP Command 0x8B
	# Param None
	# return dataBuffer
	# exception None
	#**************************************************************************************************************
	def WriteFileSystem(self, fileID = 0, sectorCount = 1, dataBuffer = None):

		diagCommand = ServiceWrap.DIAG_FBCC_CDB()

		cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

		cdb[0] = TP.WRITEFILESYSTEM
		cdb[4] = (fileID & 0xFF)
		cdb[5] = (fileID >> 8) & 0xFF
		cdb[6] = (fileID >> 16) & 0xFF
		cdb[7] = (fileID >> 24) & 0xFF
		cdb[8] = sectorCount & 0xFF
		cdb[9] = (sectorCount >> 8 ) & 0xFF
		cdb[10] = (sectorCount >> 16) & 0xFF
		cdb[11] = (sectorCount >> 24) & 0xFF
		cdb[12] = cdb[13] = cdb[14] = cdb[15] = 0

		diagCommand.cdb = cdb
		diagCommand.cdbLen = TP.CDBLENGTH_16

		self.TF.logger.Info("Sending WRITE FILE SYSTEM CDB: %s"%diagCommand.cdb)
		self.TF.logger.Info("File ID: %d Sector Count: %d"%(fileID, sectorCount))
		self.TF.logger.Info("Write Buffer Size: %d Bytes"%dataBuffer.GetBufferSize())
		sctpCommand = ServiceWrap.SCTPCommand.SCTPCommand(diagCommand, dataBuffer, ServiceWrap.DIRECTION_IN)
		sctpCommand.Execute()


	#**************************************************************************************************************
	# This method is used to send ReadFileSystem (0x8A)
	# This method sends a SCTP Command 0x8A
	# Param None
	# return dataBuffer
	# exception None
	#**************************************************************************************************************
	def ReadFileSystem(self, option = 0, fileID = 0, sectorCount = 1, bankNumber = 0):

		if self.TF.testOptions['protocol'] == 'model':
			sectorCount = old_div(sectorCount, 8)

		dataBuffer = ServiceWrap.Buffer.CreateBuffer(dataSize = sectorCount, patternType = ServiceWrap.ALL_0, isSector = True)
		diagCommand = ServiceWrap.DIAG_FBCC_CDB()

		cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

		cdb[0] = TP.READFILESYSTEM

		cdb[1] = 0
		cdb[2] = 0
		cdb[3] = 0
		cdb[4] = (fileID & 0xFF)
		cdb[5] = (fileID >> 8) & 0xFF
		cdb[6] = (fileID >> 16) & 0xFF
		cdb[7] = (fileID >> 24) & 0xFF
		cdb[8] = sectorCount & 0xFF
		cdb[9] = (sectorCount >> 8 )& 0xFF
		cdb[10] = (sectorCount >> 16) & 0xFF
		cdb[11] = (sectorCount >> 24) & 0xFF
		cdb[12] = cdb[13] = cdb[14] = cdb[15] = 0

		diagCommand.cdb = cdb
		diagCommand.cdbLen = TP.CDBLENGTH_16

		self.TF.logger.Info("Sending READ FILE SYSTEM CDB: %s"%diagCommand.cdb)
		self.TF.logger.Info("File ID: %d Sector Count: %d"%(fileID, sectorCount))
		self.TF.logger.Info("Buffer Size: %d Bytes"%dataBuffer.GetBufferSize())
		sctpCommand = ServiceWrap.SCTPCommand.SCTPCommand(diagCommand, dataBuffer, ServiceWrap.DIRECTION_OUT)
		sctpCommand.Execute()

		return dataBuffer

	#**************************************************************************************************************
	# This method is used to send GetMediaLayout (0xBB)
	# This method sends a SCTP Command 0xBB
	# Param None
	# return dataBuffer
	# exception None
	#**************************************************************************************************************
	def GetMediaLayout(self):

		dataBuffer = ServiceWrap.Buffer.CreateBuffer(dataSize = 2, patternType = ServiceWrap.ALL_0, isSector = True)
		diagCommand = ServiceWrap.DIAG_FBCC_CDB()
		MediaLayout = dict()

		diagCommand.cdb = [TP.MEDIALAYOUT, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		diagCommand.cdbLen = TP.CDBLENGTH_16

		self.TF.logger.Info("Sending GET MEDIA LAYOUT CDB: %s"%diagCommand.cdb)
		self.TF.logger.Info("Buffer Size: %d Bytes"%dataBuffer.GetBufferSize())
		sctpCommand = ServiceWrap.SCTPCommand.SCTPCommand(diagCommand, dataBuffer, ServiceWrap.DIRECTION_OUT)
		sctpCommand.Execute()

		MediaLayout['PlanesPerDie'] = dataBuffer.GetByte(0x3)
		MediaLayout['LogicalChipCount'] = dataBuffer.GetTwoBytesToInt(0x6)
		MediaLayout['PhysicalChipCountPerChannel'] = dataBuffer.GetByte(0x8)
		MediaLayout['DiePerPhysicalChip'] = dataBuffer.GetByte(9)
		MediaLayout['BlockPerChip'] = dataBuffer.GetFourBytesToInt(0xA)
		MediaLayout['ChannelCount'] = dataBuffer.GetByte(0xE)
		MediaLayout['StarNumber'] = dataBuffer.GetByte(0xF)

		return MediaLayout

	#**************************************************************************************************************
	# This method is used to send Format Command (0x8F)
	# This method sends a SCTP Command 0x8F
	# Param None
	# return None
	# exception None
	#**************************************************************************************************************
	def Format(self):

		dataBuffer = ServiceWrap.Buffer.CreateBuffer(dataSize = 4096, patternType = ServiceWrap.ALL_0, isSector = False)
		formatParam = NVMeWrap.FormatParameters(dataBuffer)

		diagCommand = ServiceWrap.DIAG_FBCC_CDB()

		cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

		cdb[0] = TP.FORMAT
		cdb[2] = (formatParam.GetOptions() & 0xFF)
		cdb[3] = (formatParam.GetOptions() >> 8) & 0xFF


		diagCommand.cdb = cdb
		diagCommand.cdbLen = TP.CDBLENGTH_16

		self.TF.logger.Info("Sending FORMAT CDB: %s"%diagCommand.cdb)
		self.TF.logger.Info("Buffer Size: %d Bytes"%dataBuffer.GetBufferSize())

		sctpCommand = ServiceWrap.SCTPCommand.SCTPCommand(diagCommand, formatParam.GetDataBuffer(), ServiceWrap.DIRECTION_IN)
		sctpCommand.Execute()

	#**************************************************************************************************************
	# This method is used to send Get Format Status Command (0x70)
	# This method sends a SCTP Command 0x70
	# Param None
	# return Format Status
	# exception None
	#**************************************************************************************************************
	def GetFormatStatus(self):

		dataBuffer = ServiceWrap.Buffer.CreateBuffer(dataSize = 4096, patternType = ServiceWrap.ALL_0, isSector = False)
		formatParam = NVMeWrap.FormatParameters(dataBuffer)

		diagCommand = ServiceWrap.DIAG_FBCC_CDB()

		cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

		cdb[0] = TP.FORMATSTATUS

		diagCommand.cdb = cdb
		diagCommand.cdbLen = TP.CDBLENGTH_16

		self.TF.logger.Info("Sending Get FORMAT Status CDB: %s"%diagCommand.cdb)
		self.TF.logger.Info("Buffer Size: %d Bytes"%dataBuffer.GetBufferSize())

		sctpCommand = ServiceWrap.SCTPCommand.SCTPCommand(diagCommand, dataBuffer, ServiceWrap.DIRECTION_OUT)
		sctpCommand.Execute()

		formatstatus = dataBuffer.GetByte(0)
		self.TF.logger.Info("Format Status is: %d"%formatstatus)

		return formatstatus

	#**************************************************************************************************************
	# This method is used to Mode to SLC.
	# This method sends a SCTP Command 0x5F
	# Param None
	# return Format Status
	# exception None
	#**************************************************************************************************************
	def ChangeModeToSLC(self):

		self.TF.logger.Message("\n\n----------------- Change mode to SLC using SCTP command 0x5F ---------------------------\n\n")

		dataBuffer = ServiceWrap.Buffer.CreateBuffer(1)
		diagCommand = ServiceWrap.DIAG_FBCC_CDB()
		cdb = [0x5F, 0, 4 , 0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0]
		diagCommand.cdb = cdb
		diagCommand.cdbLen = TP.CDBLENGTH_16
		isStatusPhasePresent = True
		sctpCommand = ServiceWrap.SCTPCommand.SCTPCommand(diagCommand, dataBuffer, ServiceWrap.DIRECTION_OUT, isStatusPhasePresent)
		#sctpCommand.Execute()

		try:
			self.TF.threadPool.PostRequestToWorkerThread(sctpCommand)
		except self.TF.CVFExceptions as ex:
			self.TF.logger.FlushAllMsg()
			self.TF.logger.Debug("Error in posting SCTP command to Command Manager\n")
			raise ValidationError('SCTP Utils', "Error in posting SCTP command to Command Manager\n", ex.GetFailureDescription())

		status = False
		status = self.TF.threadPool.WaitForThreadCompletion()
		if False == status:
			assert(True == False), self.errorManager.GetAllFailureDescription()

	#**************************************************************************************************************
	# This method is used to Mode to TLC.
	# This method sends a SCTP Command 0x5F
	# Param None
	# return Format Status
	# exception None
	#**************************************************************************************************************
	def ChangeModeToTLC(self):

		self.TF.logger.Message("\n\n----------------- Change mode to TLC using SCTP command 0x5F ---------------------------\n\n")

		dataBuffer = ServiceWrap.Buffer.CreateBuffer(1)
		diagCommand = ServiceWrap.DIAG_FBCC_CDB()
		cdb = [0x5F, 0, 2 , 0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0]
		diagCommand.cdb = cdb
		diagCommand.cdbLen = TP.CDBLENGTH_16
		isStatusPhasePresent = True
		sctpCommand = ServiceWrap.SCTPCommand.SCTPCommand(diagCommand, dataBuffer, ServiceWrap.DIRECTION_OUT, isStatusPhasePresent)
		#sctpCommand.Execute()

		try:
			self.TF.threadPool.PostRequestToWorkerThread(sctpCommand)
		except self.TF.CVFExceptions as ex:
			self.TF.logger.FlushAllMsg()
			self.TF.logger.Debug("Error in posting SCTP command to Command Manager\n")
			raise ValidationError('SCTP Utils', "Error in posting SCTP command to Command Manager\n", ex.GetFailureDescription())

		status = False
		status = self.TF.threadPool.WaitForThreadCompletion()
		if False == status:
			assert(True == False), self.errorManager.GetAllFailureDescription()

