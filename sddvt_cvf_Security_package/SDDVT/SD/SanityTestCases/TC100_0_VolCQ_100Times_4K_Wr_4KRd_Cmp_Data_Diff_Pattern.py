"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                :
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : TC100_0_VolCQ_100Times_4K_Wr_4KRd_Cmp_Data_Diff_Pattern.py
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : TC100_0_VolCQ_100Times_4K_Wr_4KRd_Cmp_Data_Diff_Pattern.py
# DESCRIPTION                    :
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=TC100_0_VolCQ_100Times_4K_Wr_4KRd_Cmp_Data_Diff_Pattern --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Arockiaraj Jai
# REVIEWED BY                    :
# DATE                           : DD-Mmm-2023
################################################################################
"""

# Python future modules for python3 forward compatibility
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    from builtins import range
    from builtins import *

# SDDVT - Dependent TestCases

# SDDVT - Common Interface for Testcase
import SDDVT.Common.DvtCommonLib as DvtCommonLib

# SDDVT - SD Specification and commands related Interface
import SDDVT.Common.SDCommandLib as SDCommandLib

# SDDVT - Error Utils
import SDDVT.Common.ErrorCodes as ErrorCodes

# SDDVT - Configuration Data
import SDDVT.Common.getconfig as getconfig
import SDDVT.Common.GlobalConstants as gvar
from SDDVT.Common.customize_log import customize_log

# CVF Packages
import SDCommandWrapper as sdcmdWrap
import CTFServiceWrapper as ServiceWrap
import Protocol.SD.Basic.TestCase as TestCase
import Core.Configuration as Configuration
import Core.ValidationError as ValidationError
import Validation.CVFTestFactory as FactoryMethod

# Python Build-in Modules
import random
import os
import sys
from inspect import currentframe, getframeinfo

# Global Variables
# Test Variables

Priority = 0    # Default priority

ITERATION = 1
Write_Direction = 0
Read_Direction = 1
No_of_blocks = 65535 #0XFFFF
StartBlockAddrWrite = 0
StartBlockAddrRead = 0
NumOfTaskQueued = 0
NumOfTasksExecuted = 0
TaskIDInExe = None
NumOfTimes = 32
BlockSize = 512

# Testcase Class - Begins
class TC100_0_VolCQ_100Times_4K_Wr_4KRd_Cmp_Data_Diff_Pattern(TestCase.TestCase, customize_log):
    # Act as a Constructor
    def setUp(self):
        """
        1) Creating CVF objects
        2) Loading General Variables
        3) Loading testcase specific XML variables [If any variable is added in the xml, it needs to be loaded here]
        4) Creating SDDVT objects
        5) Check and Switch to SD Protocol
        6) Customize Log base class Object Initialization
        7) Declare the Testcase Specific Variables
        """

        ###### Creating CVF objects ######
        self.CVFTestFactory = FactoryMethod.CVFTestFactory().GetProtocolLib()
        self.__TF = self.CVFTestFactory.TestFixture
        self.__ErrorManager = self.vtfContainer.device_session.GetErrorManager()

        ###### Loading General Variables ######
        self.__testName = self.vtfContainer.GetTestName()

        ###### Loading testcase specific XML variables ######
        self.testLoop = self.currCfg.variation.testloop
        self.StartBlockAddr = self.currCfg.variation.startlba
        self.NumBlocks = self.currCfg.variation.blockcount
        self.lbaAlignment = self.currCfg.variation.lbaalignment
        self.TaskID = self.currCfg.variation.taskid
        self.Direction = self.currCfg.variation.direction      # 1-Read, 0-Write
        self.Priority = self.currCfg.variation.priority        # 0-No Priority, 1-Priority request
        self.No_of_Tasks = self.currCfg.variation.no_of_tasks

        ###### Creating SDDVT objects ######
        self.__config = getconfig.getconfig()
        self.__dvtLib = DvtCommonLib.DvtCommonLib(self.vtfContainer)
        self.__sdCmdObj = SDCommandLib.SdCommandClass(self.vtfContainer)
        self.__errorCodes = ErrorCodes.ErrorCodes()
        self.__cardMaxLba = self.__sdCmdObj.MaxLba()

        ###### Check and Switch to SD Protocol ######
        self.protocolName = self.__dvtLib.switchProtocol(ScriptName = self.__testName)

        ###### Customize Log ######
        self.fn = os.path.basename(getframeinfo(currentframe()).filename)
        customize_log.__init__(self, self.__TF)

        ###### Testcase Specific Variables ######
        self.__TaskIdList = [] #list of all free tasks
        self.__TaskIdQueuedList = [] # list to add the queued tasks
        self.__PatternList = []
        self.__TransferLen  = No_of_blocks
        self.__Max_CQ_Depth = 0


    # Testcase logic - Starts

    def ExecuteTasks(self, No_of_Tasks, Direction):
        """
        Function to execute the queued tasks
        """
        global NumOfTasksExecuted
        global TaskIDInExe

        count = 0
        while (count < No_of_Tasks):

            if TaskIDInExe != None :
                #time.sleep(0.5)
                #Check for the task completion

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[ExecuteTasks:C:1.1] Direction = %d TaskID = %d Pattern = %d StartBlockAddr = 0x%X NumBlocks = %d"%(Direction, TaskIDInExe, self.__PatternList[TaskIDInExe], self.__StartBlockAddrList[TaskIDInExe], self.__NumBlocksList[TaskIDInExe]))
                self.CheckForTaskCompletion(TaskIDInExe)
                TaskIDInExe = None

            if len(self.__TaskIdQueuedList) <= 0 :
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[ExecuteTasks:2] Direction = %d No of task in Queue = %d \n" %(Direction, len(self.__TaskIdQueuedList)))
                break

            # Get the list of tasks ready
            taskReadyList = self.__dvtLib.GetTaskReadyList()

            if len(taskReadyList) > 0 :
                TaskID = taskReadyList[0]
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[ExecuteTasks:4] Direction = %d TaskID = %d No. of Tasks Ready = %d. TaskReadyList =  %s\n" %(Direction, TaskID, len(taskReadyList),taskReadyList))
            else:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[ExecuteTasks:5:No Task] Direction = %d No. of Tasks Ready = %d. TaskReadyList =  %s\n" %(Direction, len(taskReadyList),taskReadyList))
                break

            if Direction == 0:
                # Execute the write task
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[ExecuteTasks:W:6] Direction = %d TaskID = %d Pattern = %d StartBlockAddr = 0x%X NumBlocks = %d"%(Direction, TaskID, self.__PatternList[TaskID], self.__StartBlockAddrList[TaskID], self.__NumBlocksList[TaskID]))
                self.__dvtLib.CQExecuteWriteTask(TaskID=TaskID, Pattern=self.__PatternList[TaskID], StartBlockAddr=self.__StartBlockAddrList[TaskID], NumBlocks=self.__NumBlocksList[TaskID])
            else:
                # Execute the read task
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[ExecuteTasks:R:7] Direction = %d TaskID = %d Pattern = %d StartBlockAddr = 0x%X NumBlocks = %d"%(Direction, TaskID, self.__PatternList[TaskID], self.__StartBlockAddrList[TaskID], self.__NumBlocksList[TaskID]))
                self.__dvtLib.CQExecuteReadTask(TaskID=TaskID, Pattern=self.__PatternList[TaskID], StartBlockAddr=self.__StartBlockAddrList[TaskID], NumBlocks=self.__NumBlocksList[TaskID], DoCompare=1)

            TaskIDInExe = TaskID
            count = count + 1
            NumOfTasksExecuted = NumOfTasksExecuted + 1


    def QueueTasks(self, No_of_Tasks, Direction):
        """
        Function to queue N tasks
        """
        global StartBlockAddrWrite
        global StartBlockAddrRead
        global NumOfTaskQueued

        # Shuffle all the task id's
        random.shuffle(self.__TaskIdList)

        NumBlocks = No_of_blocks

        if  Direction:
            StartBlockAddr = StartBlockAddrRead
        else:
            StartBlockAddr = StartBlockAddrWrite

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_TASK_UNQUEUED_LIST(self.__TaskIdList))
        No_of_queued_tasks = 0

        for task in range(0, No_of_Tasks):
            if (StartBlockAddr >= self.__cardMaxLba) :
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[BREAK:Max:QueueTasks:2]: Direction = %d  StartBlockAddr = 0x%X cardMaxLba = 0x%X\n"%(Direction,StartBlockAddr, self.__cardMaxLba))
                break

            if len(self.__TaskIdList) <= 0:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[BREAK:AllTaskinQueue:QueueTasks:3]: Direction = %d No of Free tasks = %d. TaskIdList = %s\n"%(Direction, len(self.__TaskIdList),self.__TaskIdList))
                break

            TaskID = self.__TaskIdList[0]

            if ((StartBlockAddr+NumBlocks) > self.__cardMaxLba) :
                NumBlocks = (self.__cardMaxLba - StartBlockAddr)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[RangeCrossingMaxLBA:QueueTasks:5]: Direction = %d StartBlockAddr = 0x%X  NumBlocks = %d\n"%(Direction, StartBlockAddr, NumBlocks))

            # Selecting the pattern based on the start LBA (3 bits from LSB bit) - pattern 0-7 will be taken
            Pattern = StartBlockAddr & 7
            if Pattern == 3: # since pattern 3 is user define buffer we are using some other patter instead of pattern 3
                Pattern = 9
            self.__PatternList[TaskID] = Pattern

            self.__NumBlocksList[TaskID] = NumBlocks
            self.__StartBlockAddrList[TaskID] = StartBlockAddr
            self.__DirectionList[TaskID] = Direction

            self.__dvtLib._CMD44_ReissueOnFailure=True

            self.noiseLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_SEND_CMD44_CMD45_FOR_TASK_ID(TaskID))
            # Send CMD44 for Queueing the task
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[QueueTasks:6:CMD44]: Queueing the task: Direction = %d TaskID = %d NumBlocks = %d  "%(Direction, TaskID, NumBlocks))
            self.__dvtLib.CQTaskInformation(NumBlocks = NumBlocks, TaskID = TaskID, Direction = Direction, Priority = Priority)

            # Send CMD45 for Start Lba
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[QueueTasks:7:CMD45]: Queueing the task: Direction = %d TaskID = %d StartBlockAddr = 0x%X"%(Direction, TaskID, StartBlockAddr))
            self.__dvtLib.CQStartBlockAddr(StartBlockAddr=StartBlockAddr)

            self.__TaskIdQueuedList.append(TaskID) # Add the queued task to TaskIdQueuedList

            self.__TaskIdList.remove(TaskID) # Remove the queued task from TaskIdList

            NumOfTaskQueued += 1
            No_of_queued_tasks+=1
            StartBlockAddr = StartBlockAddr + NumBlocks

        if Direction:
            StartBlockAddrRead = StartBlockAddr
        else:
            StartBlockAddrWrite = StartBlockAddr

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[QueueTasks:8]: No of Queued tasks = %d QueuedTaskIdList = %s\n"%(len(self.__TaskIdQueuedList),self.__TaskIdQueuedList))

        return No_of_queued_tasks


    def CheckForTaskCompletion(self,TaskID):
        """
        Function to check the task completion and update the taskid and queue list
        """
        self.__dvtLib.GetTaskCompletionStatus(TaskID)
        self.__TaskIdList.append(TaskID) # add the completed task to TaskIdList
        self.__TaskIdQueuedList.remove(TaskID)  # remove completed task from TaskIdQueuedList


    def WriteOrRead(self, Direction):
        """
        Function for selecting StartLBA and NumBlocks to write/read 100 capacity
        """
        global NumOfTaskQueued
        global NumOfTasksExecuted
        global StartBlockAddrWrite
        global StartBlockAddrRead

        No_of_Tasks_ToQueue = 1   # for first task to queue

        while True:

            if (Direction == 0) and (StartBlockAddrWrite < self.__cardMaxLba):
                ret= self.QueueTasks( No_of_Tasks_ToQueue, Direction)
            elif Direction and (StartBlockAddrRead < self.__cardMaxLba):
                ret= self.QueueTasks( No_of_Tasks_ToQueue, Direction)
            elif (NumOfTaskQueued == NumOfTasksExecuted):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[BREAK::1]: NumOfTimes * 4K Write Done or 100 write done Blocks %d NumOfTaskQueued %d"%(NumOfTaskQueued))
                break

            NumOfTaskInQueuedList = len(self.__TaskIdQueuedList)
            if(NumOfTaskInQueuedList >= 1): # At least one task should be in queue to execute
                NumOfTasksToBeExecuted = random.randint(1, NumOfTaskInQueuedList)
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[WriteOrRead:2]: NumOfTasksToBeExecuted = %d NumOfTaskInQueuedList = %d"%(NumOfTasksToBeExecuted, NumOfTaskInQueuedList))
                self.ExecuteTasks(NumOfTasksToBeExecuted, Direction)

            NumOfTaskInQueuedList = len(self.__TaskIdQueuedList) #ReCheck the QueuedList again
            No_of_Tasks_ToQueue = random.randint(1, (self.__Max_CQ_Depth - NumOfTaskInQueuedList))
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[WriteOrRead:3]: No_of_Tasks_ToQueue = %d NumOfTaskInQueuedList %d Max_CQ_Depth =%d\0n"%(No_of_Tasks_ToQueue, NumOfTaskInQueuedList, self.__Max_CQ_Depth ))

            if (No_of_Tasks_ToQueue + NumOfTaskInQueuedList) > self.__Max_CQ_Depth:
                No_of_Tasks_ToQueue = self.__Max_CQ_Depth - NumOfTaskInQueuedList #No of task to be queued should be less than MaxDepth
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[WriteOrRead:4]: NumOfTaskInQueuedList = %d\n"%No_of_Tasks_ToQueue)

            if Direction:
                StartLBA = StartBlockAddrRead
            else:
                StartLBA = StartBlockAddrWrite

            if (StartLBA >= self.__cardMaxLba) and (NumOfTaskQueued == NumOfTasksExecuted):
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[WriteOrRead:5] BreakWhileLoop: StartLBA = %d NumOfTasksExecuted = %d " %(StartLBA, NumOfTasksExecuted))
                break

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[WriteOrRead:6] : Iteration Done....: Direction = %d"%Direction)



    def Run(self):
        """
        Function to queue N tasks while one task is in execution
        """
        global ITERATION
        global No_of_blocks
        global NumOfTaskQueued
        global NumOfTasksExecuted
        global TaskIDInExe

        # Get Device supported Max Depth
        self.__Max_CQ_Depth = self.__dvtLib.GetCQDepth()

        self.__TaskIdList = list(range(0, self.__Max_CQ_Depth))
        self.__NumBlocksList = [0] * self.__Max_CQ_Depth  # List initialized with all zeros
        self.__StartBlockAddrList = [0] * self.__Max_CQ_Depth
        self.__PatternList = [0] * self.__Max_CQ_Depth
        self.__DirectionList = [0] * self.__Max_CQ_Depth

        #Enable the Sequential CQ Mode
        self.noiseLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_ENABLE_VOL_CQ_WITH_CACHE)
        self.__dvtLib.CQEnable(Set_CQ = True, Set_Cache = True, Set_Voluntary_mode= True)

        # loop for ITERATION times
        for loop in range(0, ITERATION):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "\n###[Run:2] : ********** ITERATION %d  *********"%(loop+1))

            while True:
                if StartBlockAddrWrite < self.__cardMaxLba:
                    # function call to write to the 100Times card
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[Run:3] : ###### Writing at StartBlockAddr = 0x%X ######"%StartBlockAddrWrite)
                    self.WriteOrRead( Write_Direction)
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[Run:4] : ###### Writing at StartBlockAddr = 0x%X - Done ######"%StartBlockAddrWrite)

                if StartBlockAddrRead < self.__cardMaxLba:
                    # function call to read the 100Times card
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[Run:5] : ###### Reading  from StartBlockAddr = 0x%X ######"%StartBlockAddrRead)
                    self.WriteOrRead( Read_Direction)
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[Run:6] : ###### Reading  from StartBlockAddr = 0x%X -Done ######"%StartBlockAddrRead)

                if StartBlockAddrWrite >= self.__cardMaxLba and StartBlockAddrRead >= self.__cardMaxLba and (NumOfTaskQueued == NumOfTasksExecuted):
                    if TaskIDInExe != None :
                        #time.sleep(0.5)
                        #Check for the task completion
                        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[Run:7] TaskIDInExe = %d \n" %(TaskIDInExe))
                        self.CheckForTaskCompletion(TaskIDInExe)
                        TaskIDInExe = None

                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[Run:8] : ########## Finished writing and reading 100 times")
                    #Checking the Task Status register for value 0 after completing all the tasks
                    CQTaskStatusRegValue = self.__sdCmdObj.GetTaskStatusRegister()
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###[Run:9] : Task Status Register value = 0x%X"%CQTaskStatusRegValue)
                    if(CQTaskStatusRegValue !=0):
                        raise ValidationError.TestFailError(self.fn, "Run:CQTaskStatusRegister is not 0 after executing or aborting all the tasks")

                    break

        # Disable CQ mode
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "### [Run:10] : Disabling CQ and Cache")
        self.__dvtLib.CQDisable()



    # Testcase logic - Ends

    # CVF Hook Function: [Testcase Should start with "test_"]
    def test_TC100_0_VolCQ_100Times_4K_Wr_4KRd_Cmp_Data_Diff_Pattern(self):  # [Same in xml tag: <Test name="test_TC100_0_VolCQ_100Times_4K_Wr_4KRd_Cmp_Data_Diff_Pattern">]
        # Initialize the SD card
        self.__sdCmdObj.DoBasicInit()

        # Calling Testcase logic
        self.Run()

# Testcase Class - Ends