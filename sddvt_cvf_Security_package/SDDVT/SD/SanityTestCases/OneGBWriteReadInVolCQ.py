"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : None
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : OneGBWriteReadInVolCQ.py
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : OneGBWriteReadInVolCQ.py
# DESCRIPTION                    : To execute one GB write and read in voluntary CQ mode
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : Yes
# TEST ARGUMENTS                 : --test=OneGBWriteReadInVolCQ --isModel=false --enable_console_log=1 --adapter=0
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 10-Jan-2022
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
import time
import os
import sys
from inspect import currentframe, getframeinfo

# Global Variables
No_of_Tasks = 32

class OneGBWriteReadInVolCQ(TestCase.TestCase, customize_log):

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

    def WriteRead(self, Direction):
        global No_of_Tasks

        StartBlockAddr = 0
        Pattern = 5             # All_ONE
        TaskIdList = list(range(0, 32))
        NumBlocksList = [0] * 32  # List initialized with all zeros
        StartBlockAddrList = [0] * 32
        PatternList = [0] * 32

        random.shuffle(TaskIdList)      # Shuffle all the task id's

        StartTime = time.time()
        # queueing 32 tasks
        for task in range(0, No_of_Tasks):
            TaskID = TaskIdList[task]

            StartBlockAddrList[TaskID] = StartBlockAddr

            NumBlocks = 0xFFFF      # 32MB
            NumBlocksList[TaskID] = NumBlocks

            PatternList[TaskID] = Pattern

            Priority = random.randint(0, 1)

            # Send CMD44 for Queueing Task
            self.noiseLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_SEND_CMD44_CMD45_FOR_TASK_ID(TaskID))
            self.__dvtLib.CQTaskInformation(NumBlocks = NumBlocks, TaskID = TaskID, Direction = Direction, Priority = Priority)

            # Send CMD45 for Start Lba
            self.__dvtLib.CQStartBlockAddr(StartBlockAddr = StartBlockAddr)
            StartBlockAddr = StartBlockAddr + 0xffff

        # loop for execute 32 queued tasks
        count = 0
        while (count < No_of_Tasks):

            # Get the list of tasks ready
            taskReadyList = self.__dvtLib.GetTaskReadyList()

            for task in range(0, len(taskReadyList)):
                TaskID = taskReadyList[task]

                # Execute the task
                if Direction == 0:
                    self.noiseLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_SEND_CMD47_FOR_TASK_ID(TaskID))
                    self.__dvtLib.CQExecuteWriteTask(TaskID = TaskID, Pattern = PatternList[TaskID],
                                                     StartBlockAddr = StartBlockAddrList[TaskID], NumBlocks = NumBlocksList[TaskID])
                else:
                    self.noiseLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_SEND_CMD46_FOR_TASK_ID(TaskID))
                    self.__dvtLib.CQExecuteReadTask(TaskID = TaskID, Pattern = PatternList[TaskID],
                                                    StartBlockAddr = StartBlockAddrList[TaskID], NumBlocks = NumBlocksList[TaskID])

                # Check for Task completion status
                self.__dvtLib.GetTaskCompletionStatus(TaskID)
                count = count + 1

        EndTime = time.time()
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "[OneGBWriteReadInVolCQ]: One GB CQ %s is done in %s seconds" % ("read" if Direction else "write", EndTime - StartTime))


    def Run(self):
        """
        To execute one GB write and read in voluntary CQ mode
        """

        # Enable the Voluntary CQ Mode
        self.noiseLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_ENABLE_VOL_CQ_WITH_CACHE)
        self.__dvtLib.CQEnable(Set_CQ = True, Set_Cache = True, Set_Voluntary_mode = True)

        # One GB write and read in voluntary CQ mode
        for loop in range(0, self.testLoop):
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.STD_LOG_ITERATION(loop + 1))

            self.WriteRead(Direction = 0)

            self.WriteRead(Direction = 1)

        # Disable CQ mode
        self.noiseLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, self.GL_DISABLE_CQ_AND_CACHE)
        self.__dvtLib.CQDisable()


    # CVF Hook Function: [Testcase Should start with "test_"]
    def test_OneGBWriteReadInVolCQ(self):  # [Same in xml tag: <Test name="test_OneGBWriteReadInVolCQ">]
        # Initialize the SD card
        self.__sdCmdObj.DoBasicInit()

        # Calling Testcase logic
        self.Run()
