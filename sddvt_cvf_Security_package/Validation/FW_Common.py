from __future__ import division
from builtins import range
from builtins import object
from past.utils import old_div
import time
import os
import sys
import random
import inspect
import collections
import Validation.CMDUtil as CU
import Validation.Extensions.CVFImports as PyWrap
import Validation.TestFixture as TestFixture
import Validation.SctpUtils as SCTP

capacityMultiplier = 1

def TagLBA(buff, lba, sectorcount , bytePerSector ):

	tempSectors = sectorcount
	increment = 1
	offset = 0

	while tempSectors:
		buff.SetFourBytes(offset , lba)
		offset += bytePerSector
		lba += increment
		tempSectors = tempSectors - 1

# assume we want to read all that we write
class WriteReadOps(object):

	def __init__(self, WriteType, WriteReadAmount, startLba, FUA_Enable, QueueSID, QueueCID, nameSpaceID, WriteChunkSize, randomOp, seed = 12345):

		self.TF = TestFixture.TestFixture()
		self.CU = CU.CMDUtil()
		self.errorManager = self.TF.testSession.GetErrorManager()

		self.WriteType = WriteType
		self.WriteReadAmount = WriteReadAmount
		self.startLba = startLba
		self.FUA_Enable = FUA_Enable
		self.QueueSID = QueueSID
		self.QueueCID = QueueCID
		self.nameSpaceID = nameSpaceID
		self.WriteChunkSize = WriteChunkSize
		self.random = randomOp
		self.WthreadPool = PyWrap.ThreadPoolMgr.GetThreadPoolMgr(5000)
		self.WthreadPool.SetAsynchronousMode(1)

		if (self.FUA_Enable!=0) and (self.WriteChunkSize<8):
			raise AssertionError("No support for FUA commands and unaligned write.\n")

		#just overwrite FUA enable in case of TLC !!!!!
		if (self.FUA_Enable!=0) and (self.WriteType == "TLC"):
			self.FUA_Enable = 0;

		self.iterations = old_div(self.WriteReadAmount, self.WriteChunkSize)

		#lets create the SLC LBA random list
		self.LBAList = list(range(self.startLba, (self.iterations) * self.WriteChunkSize + self.startLba, self.WriteChunkSize))
		if (self.random == True):
			random.shuffle(self.LBAList)

		#add -1 to the end of list for avoiding Out of Bounds access
		self.LBAList.append(-1)

	def executeWrite(self,lbaIndex=0,forceNumbering=0,batchCommands=0,queueNumber=1,shdwn_prob=0, writeChunkSize=0):
	#reset_probability is in percent from 0-100 integer.
		countLBA = self.LBAList[lbaIndex]
		startSubQueue = self.QueueSID
		reset_allowed = False

		if (writeChunkSize != 0):
			self.WriteChunkSize = writeChunkSize				#use arg chunkSize
			#self.iterations = self.WriteReadAmount / self.WriteChunkSize	#calc iterations according to new readChunk size

		#lets assure that shutdown_probability is integer
		if(shdwn_prob>100):
			raise AssertionError("Invalid Reset Probability!!!!" )
		shdwn_prob = int(shdwn_prob)


		for i in range(forceNumbering , forceNumbering + self.iterations):
			writeBuffer = PyWrap.Buffer.CreateBuffer(self.WriteChunkSize)
			writeBuffer.FillIncrementing(85, 170, 85)
			TagLBA(writeBuffer, countLBA, self.WriteChunkSize, writeBuffer.GetBytesPerSector())

			#writeDiskObj = PyWrap.WriteCommand(countLBA, self.WriteChunkSize, startSubQueue+(i % queueNumber) , self.nameSpaceID, self.FUA_Enable, writeBuffer)
			try:
				writeDiskObj = self.CU.PostWriteLba(countLBA, self.WriteChunkSize, startSubQueue+(i % queueNumber) , self.nameSpaceID, self.FUA_Enable, writeBuffer = writeBuffer)
			except (PyWrap.ThreadPoolException) as ex:
				raise ValidationError.CVFGenericExceptions("WT_PlaylistScript8", "Failed in Posting Write Command\n")

			if i % 200 == 0:
				status = False
				status = self.TF.threadPool.WaitForThreadCompletion()

		#Execute Pending Commands if any.
		status = False
		status = self.TF.threadPool.WaitForThreadCompletion()

		if(batchCommands == 0):
			self.TF.logger.Message( "%s Write numbered %d WLBA -> NSID : %d  SQID : %d FUA : %d LBA : 0x%08X  TxLen : 0x%08X PASSED" % (self.WriteType,i, self.nameSpaceID, startSubQueue+(i % queueNumber), self.FUA_Enable, countLBA, self.WriteChunkSize))
		else:
			self.TF.logger.Message( "%s Writes numbered %d WLBA -> NSID : %d  SQID : %d FUA : %d LBA : 0x%08X  TxLen : 0x%08X SENT" % (self.WriteType,i, self.nameSpaceID, startSubQueue+(i % queueNumber), self.FUA_Enable, countLBA, self.WriteChunkSize))
		#increment the LBA in front of the list

		countLBA = self.LBAList[i+1 - forceNumbering]

	def executeRead(self,readZeroes=False,lbaIndex=0,forceNumbering=0,batchCommands=0,queueNumber=1, shdwn_prob=0, readChunkSize=0):

		#shdwn_prob is in percent from 0-100 integer.
		countLBA = self.LBAList[lbaIndex]
		startSubQueue = self.QueueSID
		reset_allowed = False

		#lets assure that shutdown_probability is integer
		if(shdwn_prob>100):
			raise AssertionError("Invalid Reset Probability!!!!" )
		shdwn_prob = int(shdwn_prob)
		if (readChunkSize != 0):
			self.WriteChunkSize = readChunkSize					#use arg chunkSize
			self.iterations = old_div(self.WriteReadAmount, self.WriteChunkSize)	#calc iterations according to new readChunk size

		for i in range(forceNumbering , forceNumbering + self.iterations):
			readBuffer = PyWrap.Buffer.CreateBuffer(self.WriteChunkSize)
			if (readZeroes == False):
				refBuffer = PyWrap.Buffer.CreateBuffer(self.WriteChunkSize)
				refBuffer.FillIncrementing(85, 170, 85)
				TagLBA(refBuffer, countLBA, self.WriteChunkSize, refBuffer.GetBytesPerSector())
			else:
				refBuffer = PyWrap.Buffer.CreateBuffer(self.WriteChunkSize, patternType = 0)
				refBuffer.FillFromPattern(0)

			try:
				readDiskObj = self.CU.PostReadLba(countLBA, self.WriteChunkSize, startSubQueue+(i % queueNumber) , self.nameSpaceID, 0, readBuffer = readBuffer)
			except (PyWrap.ThreadPoolException) as ex:
				raise ValidationError.CVFGenericExceptions("WT_PlaylistScript8", "Failed in Posting Read Command\n")

			if i % 200 == 0:

				status = False
				status = self.TF.threadPool.WaitForThreadCompletion()

		#Execute if there are any pending commands.

		status = False
		status = self.TF.threadPool.WaitForThreadCompletion()
		if False == status:
			assert(True == False), self.errorManager.GetAllFailureDescription()
			'''
			if (batchCommands > 0):
				self.WthreadPool.PostRequestToWorkerThread(readDiskObj)
				if((i+1)%batchCommands == 0) or (((self.iterations-i)<batchCommands) and ((i+1)==self.iterations)):
					status =  self.WthreadPool.WaitForThreadCompletion()
					self.TF.logger.Message( "%s Reads numbered %d PASSED to the Q" % (self.WriteType,i))
					if False == status:
						handleThreadError()
					else:
						reset_allowed = True
			else:
				readDiskObj.Execute()
				readDiskObj.HandleOverlappedExecute()
				readDiskObj.HandleAndParseResponse()

				SCT = readDiskObj.objNVMeComIOEntry.completionEntry.DW3.SF.SC
				SC = readDiskObj.objNVMeComIOEntry.completionEntry.DW3.SF.SC

				if (SC != 0 or SCT != 0):
					raise AssertionError("Read Command %d Execution Failed.\n",i)
				else:
					reset_allowed = True

			if(shdwn_prob>0) and (reset_allowed == True):
				reset_allowed = False
				if(self.rndObj.randint(1,100)<=shdwn_prob):
					self.TF.logger.Message( "\n----------------------------Execute Read: Power Cycle Start--------------------------------\n")
					#execute power cycle
					DoPowerCycleandStart(batchCommands)
					#restore the queues
					createBasicQueues(SavedQueueSize, SavedMsgID , SavedQueueCID, SavedQueueSID, SavedQPriority, Savedcount,batch_mode=batchCommands)
					self.TF.logger.Message( "\n----------------------------Execute Read: Power Cycle End--------------------------------\n")
			'''
			if(batchCommands > 0):
				self.TF.logger.Message( "%s Reads %d RLBA -> NSID : %d  SQID : %d LBA : 0x%08X  TxLen : 0x%08X SENT" % (self.WriteType,i, self.nameSpaceID, startSubQueue+(i % queueNumber), countLBA, self.WriteChunkSize))
			else:
				self.TF.logger.Message( "%s Read and Compare cycle %d RLBA -> NSID : %d  SQID : %d LBA : 0x%08X  TxLen : 0x%08X PASSED" % (self.WriteType,i, self.nameSpaceID, startSubQueue+(i % queueNumber), countLBA, self.WriteChunkSize))

			if (readChunkSize == 0):
				countLBA = self.LBAList[i+1 - forceNumbering]
			else:
				countLBA = countLBA + self.WriteChunkSize

class SpecialTest(object):

	def __init__(self, QueueSID, QueueCID):

		self.TF = TestFixture.TestFixture()
		self.SCTP = SCTP.SctpUtils()

		self.QueueSID = QueueSID
		self.QueueCID = QueueCID

	def runReadZeroes(self, erasedLBA = 0x007FFFFF, txSize = 8):

		self.TF.logger.Message( "\n\n---------------- Run ReadZeroes write and then read verify test --------------------------\n\n")
		#operational section:

		transferLength = 8
		FUA = 0
		nameSpaceID = 1
		isRandomOpeation = False

		operation = WriteReadOps("SLC", txSize, erasedLBA, FUA, self.QueueSID, self.QueueCID, nameSpaceID, transferLength, isRandomOpeation)
		operation.executeRead(True)

	def runMixWriteAndRead(self, amount, startLBA, largestChunkSize, smallestChunkSize, seed=None, FUA_state=0, shtdwn_prob=0):
			#the ReadWriteResetDistribution is not exact, the ration between the Read and Writes is not determisnistic, therefore the number
			# of Resets is not deterministic. The value of the number of reset will be a reasonable approach. Please do not touch this values if you are
			# not sure what you want from the test. The ratio 7:2 assures that the number of writes and reads are almot the same. This should be
			# further developed.


			self.TF.logger.Message( "\n\n ----------------------- Run MixWriteAndRead and verify test ------------------\n")
			#check arguments:
			if(amount%smallestChunkSize != 0):
				raise AssertionError("amount to transfer is not a multiplication of the smallest chunk size")
			if(96 % smallestChunkSize != 0):
				raise AssertionError("smallestChunkSize is not a multiplication good for TLC write operations")
			#variables for the test:
			mode ="SLC"
			writeCounter = 0
			readCounter  = 0

			#set mode to SLC
			self.SCTP.ChangeModeToTLC()
			# this list will hold the usage of LBA's. was the LBA used already? if so update to the iteration it was used on counted by iterations counter (itr_counter).
			itr_counter = 0
			LBA_usageTag = [-1] * (old_div(amount,smallestChunkSize))
			#init the operations class:
			operation = WriteReadOps("SLC",amount ,startLBA ,FUA_state, self.QueueSID, self.QueueCID, 1 ,smallestChunkSize, False)
			#each operation will be one itteration:
			operation.iterations = 1
			counter = 0
			#lets select the probability of read, writes and resets
			#lets turn all numebers to integer/abs
			shtdwn_prob = int(shtdwn_prob)

			while(readCounter <= amount):
				#randomize the LBA to start using and tag it:
				currentLBA = random.randint(0,len(operation.LBAList) - 2)
				#randomize the size of transfer in chunks of "smallestChunkSize":
				sizeTx = random.randint(1,old_div(largestChunkSize,smallestChunkSize))

				# 10% chance to change operation type:
				if(random.randint(1,10) == 1):
					if(mode == "SLC"):
						mode = "TLC"
						#changeModeToTLC()
						#allow only chunks of 384KB:
						sizeTx = max(old_div(96,smallestChunkSize), (old_div(sizeTx,(old_div(96,smallestChunkSize)))) * (old_div(96,smallestChunkSize)))
						if(sizeTx < min((old_div(amount,smallestChunkSize) - currentLBA - 1) , sizeTx )):
							mode = "SLC"
							#changeModeToSLC()
					else:
						mode = "SLC"
						#changeModeToSLC()

				# amount/smallestChunkSize holds the maximal lba index.   (amount/smallestChunkSize) - currentLBA is the remaining LBA's in the list that can be used
				operation.WriteReadAmount = smallestChunkSize * min((old_div(amount,smallestChunkSize) - currentLBA - 1) , sizeTx )
				if(operation.WriteReadAmount == 0):
					operation.WriteReadAmount = smallestChunkSize * 1
				operation.WriteChunkSize = operation.WriteReadAmount
				operation.WriteType = mode
				#check if LBA's are written already:
				written = True
				for i in range(currentLBA,currentLBA + old_div(operation.WriteReadAmount,smallestChunkSize)):
					if(LBA_usageTag[i] == -1):
						written = False
						break



				# pick operation to execute with 50% chance and fisible read conditions
				if(random.randint(1,2) == 1 and written == True):
					#execute read:
					operation.executeRead(False,currentLBA,counter,shdwn_prob=shtdwn_prob)
					readCounter += operation.WriteReadAmount
				else:
					#execute the write operation itself:
					operation.executeWrite(currentLBA,counter,shdwn_prob=shtdwn_prob)
					writeCounter += operation.WriteReadAmount
					for i in range(currentLBA,currentLBA + old_div(operation.WriteReadAmount,smallestChunkSize)):
						LBA_usageTag[i] = counter
				counter += 1

			self.TF.logger.Message( "\n\n----------------- END MixWriteAndRead and verify PASS -----------------------\n\n")

	def runQdepth(self, startBatch=2, endBatch=512, shut_prob=0):

		self.TF.logger.Message( "\n\n-------------------- Run Queue depth write and then read verify test ---------------------------\n\n")
		#operational section:
		txSize = 512*8 * capacityMultiplier # 1 JB SLC 1D
		batchCommands = startBatch # init the Q depth to 2
		counter = 0
		operation = WriteReadOps("SLC",txSize, 0, 0, self.QueueSID, self.QueueCID, 1, 8,  False)
		while (batchCommands <= endBatch):
			self.TF.logger.Message( "\n\n--------------------------------------- Start With batch: %d -------------------------------\n\n" %batchCommands)
			self.TF.logger.Message( "\n\n-------------------------------------- Batch: %d timestamp:%f ----------------------\n" %(batchCommands,time.time()))
			operation.executeWrite(0, counter, batchCommands,shdwn_prob=shut_prob)
			operation.executeRead(False, 0, counter, batchCommands,shdwn_prob=shut_prob)
			counter += old_div(txSize,8)
			batchCommands = batchCommands*2

	def runWriteRead4K(self,slcJB = 12160 * capacityMultiplier):

		self.TF.logger.Message( "\n\n---------------------------- Run WriteRead4K write and then read verify test ------------------\n\n")
		#operational section:
		tlcJB = slcJB * 3

		operation = WriteReadOps("SLC", slcJB, 0, 0, self.QueueSID, self.QueueCID, 1, 1,  False)
		operation.executeWrite()
		operation.executeRead()

		self.TF.logger.Message( "\n\n------------------------ END WriteRead4K write and then read verify PASS -------------------\n\n")

	def runOverlapWAW(self, startLBA = 0x4000, lbaRange = 0x1000, seed=None):

		self.TF.logger.Message( "\n\n -------------------------------------- Run Overlap Write After Write test -------------------------------\n\n")
		#operational section:

		overlapLBA = (startLBA + (old_div(lbaRange,2)))

		#create random object:
		randomObj = random.Random()
		randomObj.seed(seed)

		#set mode to SLC
		self.SCTP.ChangeModeToSLC()
		operation = WriteReadOps("SLC", lbaRange, startLBA, 0, self.QueueSID, self.QueueCID, 1, 8, False)
		operation.executeWrite()

		#main loop
		for i in range(100):
			doRegularWrite = randomObj.randint(0,0xF)
			if doRegularWrite==0:
				overlapLBA = randomObj.randint(startLBA,startLBA+lbaRange)
				overlapLBA = overlapLBA & 0xFFFFFFF8
				#write 256(64*4)K using 32K chunks
				doTLCWrite = randomObj.randint(0,0x5)
				if doTLCWrite==0:
					#set mode to TLC
					self.SCTP.ChangeModeToTLC()
					operation = WriteReadOps("TLC", 96, overlapLBA, 0, self.QueueSID, self.QueueCID, 1, 96,  False)
					operation.executeWrite()
					#set mode back to SLC
					self.SCTP.ChangeModeToSLC()
				else:
					operation = WriteReadOps("SLC", 96, overlapLBA, 0, self.QueueSID, self.QueueCID, 1, 8,  False)
					operation.executeWrite()
			else:
				# do the overalp writes
				operation = WriteReadOps("SLC",8, overlapLBA, 0, self.QueueSID, self.QueueCID, 1, 8,  False)
				operation.executeWrite()

		time.sleep(2)
		operation = WriteReadOps("SLC", lbaRange, startLBA, 0, self.QueueSID, self.QueueCID, 1, 8, False)
		operation.executeRead()

		self.TF.logger.Message( "\n\n------------------ END Overlap Write After Write test PASS ----------------------------\n\n")