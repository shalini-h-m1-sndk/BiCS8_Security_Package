"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : None
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : None
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : std_log_format.py
# DESCRIPTION                    : This is the utility file for having standard pattern of log messages
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR                         : Arockiaraj JAI
# UPDATED BY                     : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 11-Nov-2022
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
    from builtins import str
    from builtins import *
    from builtins import object

#Global Variables

################### STANDARD_LOG_MESSAGE DICTIONARY - BEGINS ##############################

#STANDARD_LOG_MESSAGE - CONTROL/FORMAT STRINGS
stdLogMsg = {
    #################### USER SPECIFIC - BEGINS ####################
    "KEY_USER_SPECIFIC_MSG_WITH_TAG": "[USER_MSG:] %s",
    "KEY_USER_SPECIFIC_MSG_WITHOUT_TAG": "%s",
    #################### USER SPECIFIC - ENDS ####################

    #################### GENERAL - BEGINS ####################
    "KEY_EMPTY_STRING": "%s",
    "KEY_HEADER_FOOTER": "{}{}{}",
    "KEY_ITERATION": "********** ITERATION %d *********",
    "KEY_INTERNAL_ITERATION": "********** Internal IterationToExe Count %d *********\n",
    "KEY_NO_OF_ITERATION_TO_EXE": "Number of iterations to execute - %d\n",
    "KEY_DATA_COMPARE_AT_ITERATION": "Going for DataCompare at iteration %d\n",
    "KEY_SETTING": "Setting : %s",
    "KEY_CHECKING": "Checking : %s",
    "KEY_SUPPORTED": "Supported : %s",
    "KEY_SET_FAILED": "Failed to set : %s",
    "KEY_ARGUMENTS": "Argument = {} = {:032b}b",
    "KEY_EXPECTED_ERROR_OCCURED": "Card is reporting expected %s for %s\n",
    "KEY_EXPECTED_ERROR_NOT_OCCURED": "Expected %s is not reported by card for %s",
    "KEY_ERROR_OCCURED_OTHER_THAN_EXPECTED_ERROR": "Expected error is %s for %s. But error occured is - %s",
    "KEY_CARD_STATUS_CMD13": "Card status from 31st bit to 0th bit - %s",
    "KEY_DECODED_R1RESPONSE": "Decoded R1 response: %s",
    "KEY_SD_SPEC_VERSION": "SD_SPEC - %s, SD_SPEC3 - %s, SD_SPEC4 - %s, SD_SPECX - %s",
    "KEY_CARD_SUPPORT_SPEC_VER": "Card supports spec version %s",
    "KEY_CARD_NOT_SUPPORT_SPEC_VER": "Card does not support spec version %s",
    "KEY_VERIFY_STATE_TRANSITION": "Verifying state transition after %s",
    "KEY_NOT_VERIFY_STATE_TRANSITION": "Since card does not support %s, Not sending %s to check the state transition",
    "KEY_VERIFY_STATE_TRANSITION_WHEN_DAT_FREE": "Verifying %s state transition when DAT line is free",
    "KEY_VERIFY_STATE_TRANSITION_WHEN_DAT_IN_USE": "Verifying %s state transition when DAT line is in use",
    "KEY_CMD_PASSED_AS_EXPECTED": "%s passed as expected..\n",
    "KEY_EXE_SUPPORTED_CMD": "Executing supported CMD - %s",
    "KEY_EXE_UNSUPPORTED_CMD": "Executing unsupported CMD - %s",
    "KEY_INJECT_ERROR_SCENARIO": "Executing the error scenario - %s",
    "KEY_ITER_NO_TO_DO_POW_CYCLE_WHEN_BUS_IDLE": "Iteration number to do a power loss when bus is idle - %d",
    #################### GENERAL - ENDS ####################

    #################### CARD SWITCH COMMAND - BEGINS ####################
    "KEY_CMD6_TO_SWITCH_SPEED_MODE": "Sending CMD6 to switch the speed mode to %s",
    "KEY_SPEED_MODE_BACK_TO": "Sending CMD6 to switch the speed mode to %s",
    #################### CARD SWITCH COMMAND - ENDS ####################

    #################### WRITE/READ - BEGINS ####################
    "KEY_SINGLE_BLOCK_WRITE": "SINGLE_BLOCK_WRITE: startLBA = 0x%X",
    "KEY_MULTI_BLOCK_WRITE": "MULTI_BLOCK_WRITE: startLBA = 0x%X, blockCount = 0x%X",
    "KEY_SINGLE_BLOCK_READ": "SINGLE_BLOCK_READ: startLBA = 0x%X",
    "KEY_MULTI_BLOCK_READ": "MULTI_BLOCK_READ: startLBA = 0x%X, blockCount = 0x%X",
    "KEY_SINGLE_BLOCK_WRITE_WITH_PATTERN": "SINGLE_BLOCK_WRITE_WITH_PATTERN: startLBA = 0x%X, pattern = %d",
    "KEY_MULTI_BLOCK_WRITE_WITH_PATTERN": "MULTI_BLOCK_WRITE_WITH_PATTERN: startLBA = 0x%X, blockCount = 0x%X, pattern = %d",
    "KEY_SINGLE_BLOCK_READ_WITH_PATTERN": "SINGLE_BLOCK_READ_WITH_PATTERN: startLBA = 0x%X, pattern = %d",
    "KEY_MULTI_BLOCK_READ_WITH_PATTERN": "MULTI_BLOCK_READ_WITH_PATTERN: startLBA = 0x%X, blockCount = 0x%X, pattern = %d",
    "KEY_SEND_WRITE_OR_READ_CMD_ABORT_AFTER_N_BLOCKS": "Sending %s and aborting after %d blocks",
    "KEY_BUFFER_STRING": "Data read - %s\n",
    "KEY_READ_AFTER_POWER_OFF_ABORT_FAILED": "Data read after power off abort failed with error - %s",
    "KEY_READ_AFTER_CMD0_ABORT_FAILED": "Data read after CMD0 abort failed with error - %s",
    #################### WRITE/READ - ENDS ####################

    #################### ERASE - BEGINS ####################
    "KEY_ERASE": "ERASE: startLBA = 0x%X, endLBA = 0x%X, eraseFunction = %d",
    "KEY_READ_DATA_AFTER_ERASE": "Printing %d blocks of read data after erase",
    "KEY_READ_ERASED_DATA_AFTER_FUNC": "Reading the erased data after %s",
    "KEY_COMPARE_READ_DATA_AFTER_ERASE": "Comparing read data after %s",
    "KEY_ERASE_CMD_FOR_OUT_OF_SEQ": "Erase CMD selected for out of sequence - %s",
    "KEY_ERASE_N_BLOCKS_WITH_FUNC": "Erasing %d blocks with %s option",
    "KEY_CMD_DURING_CMD12_BUSY": "Sending CMD12 then sending %s during CMD12 busy period",
    "KEY_CMD_DURING_CMD38_BUSY": "Sending CMD38 then sending %s during CMD38 busy period",
    "KEY_ERASED_DATA": "Erased data is 0x%X after %s",
    #################### ERASE - ENDS ####################

    #################### CQ - BEGINS ####################
    # "KEY_SET_CQ_CACHE_MODE": "CQ: Set_CQ = %s,  Set_Cache = %s,  Set_Voluntary_mode = %s,  Set_Sequential_mode = %s",
    "KEY_SET_CQ_CONFIG_FAILED": "Write extension register failed to set CQ configuration: %s",
    "KEY_CQ_CONFIG": "Current CQ configuration: %s\n",
    "KEY_GEN_INFO_FUNC_DATA": "General information function data in extension register: %s",
    "KEY_POW_MANAGE_FUNC_DATA": "Power management function data in extension register: %s",
    "KEY_PER_ENHANCE_FUNC_DATA": "Performance enhancement function data in extension register: %s",
    "KEY_TEST_EXT_REG_FUNC": "Testing extension register %s function for offset: %d, length : %d",
    "KEY_CHECK_COMMAND_CLASSES_SUPPORT": "Checking support of command classes - %s in CSD register",
    "KEY_COMMAND_CLASS_SUPPORTED": "Card supports command class - %s",
    "KEY_COMMAND_CLASS_NOT_SUPPORTED": "Card dosen't support command class - %s",
    "KEY_EXTN_REG_CMDS_SUPPORT_IN_SCR": "Extension register commands supported in SCR register - %s",
    "KEY_CQ_INFO_IN_SD_STATUS_REG": "CQ information in SD status register: %s",
    "KEY_CQ_SUPPORTED_WITH_QUEUE_DEPTH": "CQ supported with queue depth: %s",
    "KEY_NO_OF_TASKS_TO_Q": "Number of tasks to queue - %d",
    "KEY_RANDOM_TASK_QUEUE": "Random task to queue - %d",
    "KEY_RANDOM_TASK_EXECUTE": "Random task to execute - %d",
    "KEY_NO_OF_TASKS_TO_Q_PARALLELY_WHILE_TASK_IN_EXE": "Number of tasks to queue parallely during task execution - %d",
    "KEY_RANDOM_NO_OF_TASKS": "Random number of tasks generated is %d",
    "KEY_NO_OF_TASKS_TO_ABORT": "Number of tasks to abort - %s",
    "KEY_NO_OF_TASKS_TO_Q_AFTER_CMD43": "Number of tasks to queue after CMD43 abort - %s",
    "KEY_CQ_TASK_AGEING_DICT": "CQ task ageing dictionary - %s",
    "KEY_CMD43_ARGS_OPCODE": "CMD43[Q-MANAGEMENT] Arguments: OPCode - %s, TaskID - %d",
    "KEY_ABORT_SINGLE_TASK": "Task ID to abort - %d",
    "KEY_ABORT_AFTER_SOME_BLOCKS": "Aborting after %d block",
    "KEY_CMD43_TO_ABORT_REMAINING_TASKS_IN_QUEUE": "Sending CMD43 to abort the remaining %d tasks in queue",
    "KEY_BUSY_STATUS_BY_HOST": "Busy status returned by host = %d",
    "KEY_CMD43_FAILED": "CMD43[Q-MANAGEMENT]: Abort task/tasks operation failed for OpCode - %s",
    "KEY_CMD44_ARGS": "CMD44[Q_TASK_INFO_A] Arguments: Direction - %s, Extended Address - %s, Priority - %s, Task ID - %s, Number of Blocks - 0x%X",
    "KEY_CMD44_FAILED": "CMD44[Q_TASK_INFO_A]: CMD44 failed for Direction - %s, Extended Address - %s, Priority - %s, Task ID - %s, Number of Blocks - 0x%X",
    "KEY_CMD44_REISSUED_COUNT": "CMD44[Q_TASK_INFO_A]: Number of CMD44 re-issued - %d",
    "KEY_CMD44_FAILED_FOR_3_TIMES": "CMD44[Q_TASK_INFO_A]: CMD44 retried 3 times for TaskID %d. Failed with error - %s",
    "KEY_CMD45_ARGS": "CMD45[Q_TASK_INFO_B] Arguments: Start block address - 0x%X",
    "KEY_CMD45_FAILED": "CMD45[Q_TASK_INFO_B]: CMD45 failed for Start block address - 0x%X",
    "KEY_TASK_AGED_OUT": "CMD45[Q_TASK_INFO_B]: TaskID %s has aged out with ageing threshold %d",
    "KEY_CQ_EXECUTE_READ_TASK": "Arguments: Task ID - %d, StartBlockAddr - 0x%X, blockCount: 0x%X, NoData: %s, Pattern: %s, DoCompare: %s, LbaTag: %s, SequenceTag: %s, SequenceNumber: %s",
    "KEY_CQ_EXECUTE_READ_TASK_FAILED": "CMD46 for TaskID %d failed with error = '%s'",
    "KEY_NOT_CHECK_READINESS_OF_TASK": "Returning without checking the readiness of the task %s",
    "KEY_TASK_STATUS_REG_32BIT": "32 bit task status {:032b}",
    "KEY_HIGH_PRIORITY_TASK": "Sending high priority task - %d",
    "KEY_LOW_PRIORITY_TASK": "Sending low priority task - %d",
    "KEY_NO_OF_TASKS_TO_BE_PENDING_IN_Q": "Number of tasks to be pending in queue = %d\n",
    "KEY_PATTERN_LIST": "Pattern list - %s",
    "KEY_SHUFFLED_PATTERN_LIST": "Shuffled pattern list - %s",
    "KEY_TASK_ID_LIST": "Number of tasks - %d. TaskIDList - %s\n",
    "KEY_TASK_UNQUEUED_LIST": "Number of unqueued tasks - %d. TaskUnQueuedList - %s\n",
    "KEY_TASK_QUEUED_LIST_AFTER_N_QUEUE": "Task queued list after queueing %d tasks - %s\n",
    "KEY_TASK_QUEUED_LIST": "Number of tasks in queue - %d. TaskQueueList - %s\n",
    "KEY_TASK_READY_LIST": "Number of tasks ready - %d. TaskReadyList - %s\n",
    "KEY_TASK_NOT_READY_LIST": "Number of tasks not ready - %d. TaskNotReadyList - %s\n",
    "KEY_TASK_EXE_LIST": "Number of tasks to execute - %d. TaskExecutionList - %s\n",
    "KEY_TASK_EXECUTED_LIST": "Tasks executed list - %s\n",
    "KEY_ABORT_TASK_READY_BREAK_LOOP_FOR_SKIP_EXE": "Abort TaskID %d is ready. Breaking the loop for not execute abort task.\n",
    "KEY_DATA_COMPARE_LIST": "DataCompareItrCount - %d, DataCompareItrList - %s\n",
    "KEY_STOP_TRANS_DURING_DATA_TRANS_LIST": "StopTranDuringDataTransIterationCount - %d, StopTranDuringDataTransIterationList - %s\n",
    "KEY_STOP_TRANS_AFTER_DATA_TRANS_LIST": "StopTranAfterDataTransIterationCount - %d, StopTranAfterDataTransIterationList - %s\n",
    "KEY_EXE_REMAINING_QUEUED_TASKS": "Executing the remaining queued %d tasks, Queue list - %s",
    "KEY_NO_OF_REMAIN_TASKS_TO_QUEUE": "Number of remaining tasks to queue - %d\n",
    "KEY_NO_OF_REMAIN_TASKS_TO_EXE": "Number of remaining tasks to execute - %d\n",
    "KEY_TASK_REQUEUED_LIST": "Number of tasks requeued - %d. TaskRequeuedList - %s\n",
    "KEY_TASK_READY": "TaskID %d is ready",
    "KEY_TASK_NOT_READY": "TaskID %d is not ready",
    "KEY_TASK_ABORT": "Aborting the task - %d\n",
    "KEY_TASK_ABORTED": "Task ID %s is aborted\n",
    "KEY_TASK_NOT_ABORTED": "Task ID %s is not aborted\n",
    "KEY_READY_BIT_NOT_SET_FOR_TASK": "Ready bit for TaskID %d is not set after %d ms",
    "KEY_READ_TASK_STAUS_AGAIN_FOR_TASK": "Ready bit for Task %d not set. Wait for %d ms and read the status again",
    "KEY_TSR_VALUE_AFTER_CARD_INIT": "Value of task status register after card init - 0x%X",
    "KEY_TASK_STATUS_REG_IS_0": "Task status register is 0 after %d ms",
    "KEY_TASK_STATUS_REG_IS_0_READ_TSR_AGAIN": "Task Status Register is 0. Wait for %d ms and read the status again",
    "KEY_TASK_STATUS_REG_CLEARED_FOR_TASK": "Task status register bit is cleared for task %d",
    "KEY_TASK_STATUS_REG_NOT_CLEARED_FOR_TASK": "Task status register bit is not cleared for task %d",
    "KEY_TASK_STATUS_REG_CLEARED": "Task status register is cleared. TSR = 0x%X",
    "KEY_TASK_STATUS_REG_NOT_CLEARED": "Task status register is not cleared. TSR = 0x%X",
    "KEY_TASK_STATUS_REG_VALUE_AFTER_TASK_EXE": "CQ task status register value after task completion - 0x%X",
    "KEY_TASK_DATA_TRANS_STATUS": "%s task %d data transfer status - %s",
    "KEY_TASK_DATA_TRANS_TIMEOUT": "%s task %d data transfer is not completed after %s secs. SDRGetCardDataTransferStatus - %d",
    "KEY_TASK_DATA_TRANS_FAILED": "%s task %d data transfer failed with error code - %d, error string - %s\n",
    "KEY_TASK_DATA_TRANS_DONE": "%s task %d data transfer completed successfully\n\n",
    "KEY_TASK_DATA_TRANS_DONE_SEND_CMD13_TO_CHECK_TRANS_STATE": "Task %d data transfer is done. Sending CMD13 to check if the card has moved to CQ Tran state",
    "KEY_TASK_DATA_TRANS_DONE_WITHIN_250MS": "%s task %d data transfer is done in less than 0.250 secs. SDRGetCardDataTransferStatus - %d\n",
    "KEY_TASK_TIME_TAKEN_FOR_TASK_DATA_TRANS": "%s task %d data transfer is done after %0.3f secs. SDRGetCardDataTransferStatus - %d\n",
    "KEY_TASK_DATA_TRANS_EXCEEDS_3MIN": "%s task %d data transfer exceeded 3 mins. Time taken - %0.3f secs",
    "KEY_TASK_TO_ABORT_WITH_CMD0": "Task ID to abort with CMD0 - %d",
    "KEY_CMD0_TO_STOP_DATA_TRANS_OF_TASK": "Sending CMD0 to stop data transfer for task ID: %d",
    "KEY_CMD0_AFTER_EXE_TASK": "Sending CMD0 after executing task ID: %d",
    "KEY_CMD12_TO_STOP_DATA_TRANS_OF_TASK": "Sending CMD12 to stop data transfer for task ID: %d",
    "KEY_TASK_TO_ABORT_WITH_POW_CYCLE": "Task ID to abort with power cycle - %d",
    "KEY_POW_CYCLE_TO_STOP_DATA_TRANS_OF_TASK": "Sending power cycle to stop data transfer for task ID: %d",
    "KEY_POW_CYCLE_AFTER_EXE_TASK": "Sending power cycle after executing task ID: %d",
    "KEY_CARD_NOT_IN_CQ_TRANS_STATE_AFTER_DATA_TRANS": "%s task %d data transfer completed. But card has not moved to CQ Tran state, Current state is %s",
    "KEY_TASK_ERROR_STATUS_OF_ALL_TASKS_IN_CMD48": "Task error status 8bytes in PEF function of extension register - 0x%X",
    "KEY_TASK_ERROR_STATUS_OF_A_TASK_IN_CMD48": "Task %d error status in PEF function of extension register - 0x%X",
    "KEY_TASK_ERROR_STATUS_OF_A_TASK_NOT_SHOWN_IN_CMD48": "Task error status of Task%d in PEF register does not show error",
    "KEY_TASK_TO_CHECK_MISCOMPARE": "Task id selected for miscompare check - %d",
    "KEY_MISCOMPARE_OCCURED_FOR_TASK": "Miscompare error occured for %s task %d",
    "KEY_CQ_EXECUTE_WRITE_TASK": "Arguments: Task ID - %d, StartBlockAddr - 0x%X, blockCount: 0x%X, NoData: %s, Pattern: %s, LbaTag: %s, SequenceTag: %s, SequenceNumber: %s",
    "KEY_CQ_EXECUTE_WRITE_TASK_FAILED": "CMD47 for TaskID %d failed with error = '%s'",
    "KEY_CMD46_ARGS": "CMD46[Q_RD_TASK] Arguments: Task ID - %d, blockCount: 0x%X, NoData: %s, BufObj: %s, Pattern: %s",
    "KEY_CMD47_ARGS": "CMD47[Q_WR_TASK] Arguments: Task ID - %d, blockCount: 0x%X, NoData: %s, BufObj: %s, Pattern: %s",
    "KEY_CMD48_ARGS": "CMD48[READ_EXTR_SINGLE] Arguments: MIO - %s, FNO - %s, ADDR - 0x%X, LEN - %d",
    "KEY_CMD49_ARGS": "CMD49[WRITE_EXTR_SINGLE] Arguments: MIO - %s, FNO - %s, MW - %s, ADDR - 0x%X, LEN/MASK - %d",
    "KEY_AGEING_COUNTER_FOR_TASKS": "Ageing counter for all tasks - %s",
    "KEY_QUEUE_STATUS_IN_SEQ_CQ": "Queue status - %s",
    "KEY_QUEUE_LIST_BEFORE_EXE": "Task queue list before execution = %s\n",
    "KEY_QUEUE_BE_EMPTY_AFTER_N_TASKS": "Queue became empty after completing %d tasks. But initial value of No_of_Tasks = %d",
    "KEY_QUEUE_TASK_TO_ABORT": "Queueing the task to abort - Task ID:%d",
    "KEY_SEND_CMD44_FOR_TASK_ID": "Sending CMD44 for task ID: %d",
    "KEY_SEND_CMD44_AGAIN_FOR_TASK_ID": "Sending CMD44 again for task ID: %d",
    "KEY_SEND_CMD45_FOR_TASK_ID": "Sending CMD45 for task ID: %d",
    "KEY_SEND_CMD44_CMD45_FOR_TASK_ID": "Sending CMD44 and CMD45 for task ID: %d",
    "KEY_SEND_CMD46_FOR_TASK_ID": "Sending CQ read command with Task ID: %d",
    "KEY_SEND_CMD46_FOR_TASK_ID_TO_ABORT": "Sending CMD46 for task ID: %d to abort after %d blocks",
    "KEY_SEND_CMD47_FOR_TASK_ID": "Sending CQ write command with Task ID: %d",
    "KEY_SEND_CMD47_FOR_TASK_ID_TO_ABORT": "Sending CMD47 for task ID: %d to abort after %d blocks",
    "KEY_VERFIY_CQ_WRITE_WITH_LEGACY_READ": "Verifying CQ write data with legacy read for task ID: %d",
    "KEY_COMPARE_CQ_WRITE_READ_DATA": "Comparing write and read data for task id %d",
    "KEY_COMPARE_FAILED_FOR_TASK": "CQ write and read data compare failed for task id %d",
    "KEY_COMPARE_OLD_PATTERN": "Comparing block offset %d to %d for old pattern %s\n",
    "KEY_COMPARE_NEW_PATTERN": "Comparing block offset 0 to %d for new pattern %s\n",
    "KEY_COMPARE_REMAIN_BLOCKS_FOR_OLD_PATTERN": "Compare the remaining blocks from offset %d for number of blocks %d and old pattern %s\n",
    "KEY_BLOCKS_HAD_NEW_PATTERN": "Only %d blocks had new pattern %s\n",
    "KEY_ABORT_TASK_PATTERN": "Pattern for abort task - %s\n",
    "KEY_ABORT_TASK_USER_PATTERN": "User buffer used. Data - %s\n",
    "KEY_USER_BUF_FOR_CQ_WRITE_OR_READ": "User buffer %s is used for CQ StartBlockAddr - 0x%X, blockcount - 0x%X",
    "KEY_PRECOND_PATTERN": "Preconditioning with data pattern - %s",
    "KEY_PRECOND_USER_PATTERN": "Preconditioning with user data pattern - 0x%X",
    "KEY_PRECOND_LEGACY_WRITE_FOR_TASK_ID": "Precondition with legacy write for task %d",
    "KEY_PRECOND_LEGACY_FOR_PATTERN": "Preconditioning in legacy mode with data pattern 0x%X",
    "KEY_SEND_EXT_REG_CMD_IN_LOOP": "Sending %s in loop. Iteration is %d",
    "KEY_SEND_CQ_CMD_IN_LOOP_FOR_A_TASK_ID": "Sending %s in loop for same task ID %d. Iteration is %d",
    "KEY_ABORT_SINGLE_TASK_IN_LOOP_REACHED": "Abort single task in loop has reached. TaskID - %d",
    "KEY_ABORT_WHOLE_QUEUE_IN_LOOP_REACHED": "Task ID to test abort all has reached. TaskID - %d. Breaking main loop without executing tasks....",
    "KEY_ABORT_WHOLE_QUEUE_FOR_ITERATION": "Aborting all the tasks for iteration %d",
    "KEY_NO_OF_TASKS_TO_EXECUTE": "Number of tasks to execute - %d",
    "KEY_NO_OF_TASKS_EXECUTED": "Executed %d tasks",
    "KEY_EXE_QUEUED_TASKS": "Executing all the queued tasks. Number of tasks to execute = %d",
    "KEY_EXE_MAX_OF_30_TASKS": "Only one task is free. Executing %d tasks",
    "KEY_ITERATION_DONE_CHECK_STATUS_OF_TASKID": "Iteration Done.... Checking the status of the TaskID %d in execution",
    "KEY_CARD_OUT_OF_BUSY_IN_ALL_DISCARD_TRY": "Card is out of busy in all discard try. (Discard was tried %d times). Unable to queue in busy state",
    "KEY_BLOCKS_TO_DISCARD": "Blocks to discard - %d",
    "KEY_DISCARD_ITERATION_FOR_BUSY": "Discard iteration for busy %d",
    "KEY_CMD43_ITERATION_FOR_BUSY": "Abort(CMD43) iteration for busy %d",
    "KEY_CARD_SUPPORT_SPEC_VER_OF_CQ": "CQ support >= SD Spec 6.xx(part-1). Card supports SD spec version %s",
    "KEY_CARD_NOT_SUPPORT_SPEC_VER_OF_CQ": "CQ support >= SD Spec 6.xx(part-1). Card supports only spec version %s - No CQ feature",
    "KEY_CARD_STATE_AFTER_CMD38_IN_CQ": "Card is in %s state after CMD38\n",
    "KEY_EXT_REG_PER_FUNC_WRITE_RESERVED_FIELD": "Sending CMD49 to write reserved field of performance enahancement fucntion in the address %d with value 0x%X",
    "KEY_EXT_REG_MASK_WRITE": "Sending Cmd49 to write in the address 0x%X with mask 0x%x and data = 0x%x",
    "KEY_EXT_REG_MASK_WRITE_PASSED": "Mask operation successful [Data : 0x%X] was witten to [Address : 0x%X]",
    "KEY_EXT_REG_MASK_WRITE_FAILED": "Mask operation Failed [Data : 0x%X] was not witten to [Address : 0x%X]",
    "KEY_EXT_REG_ORIGINAL_VALUE_RETAINED_WITH_MASK_0": "Original value is retained with mask 0. [Data : 0x%X] was witten to [Address : 0x%X]",
    "KEY_EXT_REG_ORIGINAL_VALUE_UPDATED_WITH_MASK_0": "Original value is updated with mask 0. [UpdatedData : 0x%X] [OriginalData : 0x%X] at [Address : 0x%X]",
    "KEY_CMD_NOT_SUPPORTED_IN_SDR_FW_LOOPBACK": "%s is not supported in SDR FW Loopback\n",
    "KEY_CMD12_AFTER_QUEUE_TASK": "Sending CMD12 after queueing the task: %d",
    "KEY_CMD12_AFTER_DATA_TRANSFER_OF_TASK": "Sending CMD12 after last block of data transfer for TaskID: %d",
    "KEY_TOTAL_BLOCKS_NO_OF_REGION_REGION_SIZE": "Total blocks to write - 0x%X, Number of regions - %d, Region size - 0x%X\n",
    "KEY_START_ADDR_AND_PATTERN_OF_EACH_REGION": "Start block list of each region - %s, pattern list of each region - %s",
    "KEY_REGION_SIZE_OF_EACH_REGION": "Region size of each region - %s",
    "KEY_REGION_LIST": "Region list - %s",
    "KEY_REGION_SHUFFLED_LIST": "Region shuffled list - %s\n",
    "KEY_WRITE_REGION_IN_CQMODE": "Writing region %s in CQ mode",
    "KEY_WRITE_REGION_IN_LEGACY": "Writing region %s in legacy mode",
    "KEY_READ_REGION_IN_CQMODE": "Reading region %s in CQ mode",
    "KEY_READ_REGION_IN_LEGACY": "Reading region %s in legacy mode",
    "KEY_WRITE_REGION_FINISHED": "Finished writing region - %s",
    "KEY_READ_REGION_FINISHED": "Finished reading region - %s",
    "KEY_ABORT_AT_BIT_POSITION": "Going to Abort at bit position %d",
    "KEY_ABORT_AT_NRC": "Going to abort at NRC after %d clocks",
    "KEY_ABORT_AT_BUSY_TIME_OUT": "Going to abort at busy timeout after %d usec",
    "KEY_ABORT_AT_BUSY_TIME": "Going to abort at busy time after %d usec",
    "KEY_WRITE_DATA_BUFF_FROM_ABORT_BLOCK": "Write data buffer from abort block 0x%X - Blk %d first 8 bytes - 0x%X",
    "KEY_1ST_8_BYTES_OF_A_BLOCK": "Blk %d first 8 bytes - 0x%X",
    "KEY_TEST_STOP_TRANS_WITH_OPTION": "Testing stop transmission in %s with option - '%s'\n",
    "KEY_TEST_POWER_ABORT_WITH_OPTION": "Testing power abort in %s with option - '%s'\n",
    "KEY_TEST_CMD0_ABORT_WITH_OPTION": "Testing CMD0 abort in %s with option - '%s'\n",
    "KEY_TEST_ABORT_IN_LEGACY": "Testing %s abort in legacy %s",
    "KEY_TEST_ABORT_IN_CQ": "Testing %s abort in CQ %s",
    "KEY_MISMATCH_OCCURED_BLOCK": "Data mismatch occured at block %d. Data read = 0x%X",
    "KEY_CMD13_AFTER_ABORT_CMD": "Sending CMD13 after CMD%d",
    "KEY_DATA_TRANS_MODE": "Data transfer in %s",
    "KEY_TASK_REQUEUE": "Task for requeueing - %d",
    "KEY_TASK_QUEUE_WITH_0_BLOCK": "Task ID to queue with block count zero - %d",
    "KEY_VALIDATE_ERROR_FOR_TASK_ID": "Validating error for task ID %d",
    "KEY_ABORT_INVALID_TASK": "Invalid task ID to abort - %d\n",
    "KEY_ABORT_WITH_INVALID_OPCODE": "Sending CMD43 with invalid opcode - %d",
    "KEY_ABORT_N_TASKS": "Aborting %d tasks",
    "KEY_NO_OF_TASKS_TO_EXE_WITH_INVALID_TASK_ID": "Number of tasks to execute with invalid task id - %d",
    "KEY_MISCOMPARE_PATTERN_AND_ACTUAL_PATTERN": "Autual pattern is - %s and miscompare pattern is - %s for read task %d",
    "KEY_CMD49_FOR_FUNC_OFFSET_VALUE": "Sending CMD49 to write at func %d in offset %d with value 0x%X",
    "KEY_CMD49_WRITE_UPDATED_FOR_FUNC_OFFSET_VALUE": "CMD49 write at func %d is updated in offset %d with value 0x%X",
    "KEY_EXT_REG_FUN_WRITE_VALUE_UPDATED_UNEXPECTEDLY": "The write value 0x%X at offset %d updated in function %d of extension register which is not expected",
    "KEY_EXT_REG_FUN_NOT_UPDATED_AS_EXPECTEDLY": "The write value 0x%X at offset %d is not updated in function %d of extension register which is expected",
    "KEY_CQ_CMDS_EXECUTED_IN_LEGACY": "CQ commands executed and passed in the legacy mode are - %s",
    "KEY_CMD_FOR_OUT_OF_RANGE_ADDR": "CMD selected for out of range address - %s",
    "KEY_BUSY_TIMEOUT_RCVD_AT_COUNT": "Busy timeout received at count - %d",
    "KEY_BUSY_TIMEOUT_OCCURED": "Busy timeout occured for %s",
    "KEY_CMD48_READ_1_BYTE_AT_OFFSET": "Sending CMD48 to read 1 byte from offset %s in function %d of extension register",
    "KEY_CMD48_READ_VALUE_AT_PAGE_OFFSET": "Extension register read value 0x%X at page %d and offset %d",
    "KEY_CMD49_WRITE_AT_PAGE_OFFSET_WITH_VALUE": "Sending CMD49 to write 1 byte at page %d and offset %d with value 0x%X",
    "KEY_CMD49_WRITTERN_VALUE_AT_PAGE_OFFSET": "Value 0x%X writtern at page %d and offset %d in extension register",
    "KEY_EXT_REG_RANDOM_PAGE": "Selected page %d for extension register function %d",
    "KEY_WRITE_IN_NOT_IMPLEMENTED_EXT_REG_FUNC": "Writing to extension register function %d which is not yet implemented",
    "KEY_EXT_REG_WRITE_FAILED_FOR_FUNC": "Writing extension register function %d is failed",
    "KEY_EXT_REG_WRITE_PASSED_FOR_FUNC": "CMD49 successfully wrote to extension space function %s",
    "KEY_READ_IN_NOT_IMPLEMENTED_EXT_REG_FUNC": "Reading in extension register function %d which is not yet implemented",
    "KEY_EXT_REG_READ_FAILED_FOR_FUNC": "Reading extension register function %d is failed",
    "KEY_EXT_REG_READ_PASSED_FOR_FUNC": "CMD48 successfully read at extension space function %s",
    "KEY_EXE_REMAINING_TASKS": "Execute remaining %d tasks",
    "KEY_PER_FUNC_WRITE_READ_MATCH_AFTER_STRESS_CMD49": "Data read matches with the data written in performance enhancement function after stressing CMD49 %d times",
    "KEY_POSTION_FOR_CONTIGUOUS_WRITE_OR_READ": "Postion %s will be selected for contiguous write or read option",
    "KEY_TEST_INTENSIVE_CASE": "Testing %s intensive case",
    "KEY_TASKID_LIST_TO_CHANGE_DIRECTION": "List of TaskIDs to change the direction - %s",
    "KEY_DIRECTION_LIST": "Direction list - %s",
    "KEY_CSV_FAIL_CARD_NOT_IN_CQ_TRAN": "Csv %s failed.\nCard is not in CQ tran state. CMD13 response - %s",
    "KEY_PARSE_CSV_FILE": "Going to parse the data in csv file - %s",
    "KEY_QUEUE_NEG_AT_ROW": "%sQueue is negative at row %d..........................\n\n",
    "KEY_ROWS_IN_CSV_EXCLUDE_HEAD": "Total rows in csv excluding header - %s",
    "KEY_ROWS_MANIPULATED_IN_CSV": "Number of rows manipulated in csv with all the above values - %d",
    "KEY_TIME_TO_PARSE_FILE_AND_CREATE_BATCH": "Time taken for parsing file and creating batch - %d sec",
    "KEY_NO_OF_VALID_ENTRIES_IN_CSV": "CSV file %s. Number of valid entries - %d",
    "KEY_NO_OF_BATCH_TO_CREATE": "Number of batches to be created - %d",
    "KEY_SUBMIT_BATCH": "Submitting batch - %d\n",
    "KEY_CSV_FILE_FAILED": "CSV file %s failed with error - %s",
    "KEY_COMPLETED_BATCHES": "Completed %d batches\n",
    "KEY_COMPLETED_BATCHES_IN_CSV": "Completed %d batches in csv file %s\n",
    "KEY_NO_OF_TIMES_CMD": "Number of times %s - %d",
    "KEY_A2_PERF_STATUS": "Performance status - 0x%X (in binary - 0b%s)",
    "KEY_RPTU_START_ADDR": "RPTU start address - 0x%X",
    "KEY_CLASS2_RANDOM_PERF_MEASURE": "Random %s performance measurement in %s",
    "KEY_CLASS2_SEQ_PERF_MEASURE": "Sequential %s performance measurement in %s",
    "KEY_PERF_MEASURE_API_PATTERN": "Performance measurement API with pattern - 0x%X",
    "KEY_NO_OF_WRITE_IN_PERF_MEASURE_TEST": "Number of writes in %d sec is - %d",
    "KEY_NO_OF_READ_IN_PERF_MEASURE_TEST": "Number of reads in %d sec is - %d",
    "KEY_TIME_TAKEN_FOR_EXE": "Time taken for execution in seconds - %d",
    "KEY_RANDOM_IOPS_FOR_SIZE_4K": "%sRandom %s IOPS for IO size 4K - %d\n",
    "KEY_SEQ_WRITE_1GB_TIME": "Time taken for writing 1GB of data in sequential mode - %d",
    "KEY_WRITE_N_BLOCKS_OF_CARD": "Writing %s of the card. Total blocks to write - %d",
    "KEY_WRITE_DATA_IN_RPTU": "Writing data in the selected RPTU. Total blocks to write - %d",
    "KEY_WRITE_WHOLE_CARD": "Writing the whole card. Total blocks to write - %d",
    "KEY_START_LBA_OF_1GB_REGION": "Start LBA of 1GB region - 0x%X",
    "KEY_ENABLE_CQ_AFTER_TEST_WP_VIOLATION": "Enabling %s CQ with cache feature after testing WP violation",
    "KEY_CMD_DURING_DATA_TRANS": "Sending command %s during data transfer",
















    #################### CQ - ENDS ####################

    #################### SECURE - BEGINS ####################
    "KEY_READ_MKB_FILE": "READ_MKB_FILE: cardSlot = %d, startLBA = 0x%X, blockCount = 0x%X, selector = %d",
    "KEY_WRITE_MKB_FILE": "WRITE_MKB_FILE: selector = %d, MKBFileorPath = %s",
    "KEY_SECURE_READ": "SECURE_READ: cardSlot = %d, startLBA = 0x%X, blockCount = 0x%X, selector = %d, authenticate = %s",
    "KEY_SECURE_WRITE": "SECURE_WRITE: cardSlot = %d, startLBA = 0x%X, blockCount = 0x%X, selector = %d, authenticate = %s",
    "KEY_PROTECTED_AREA_SIZE": "PROTECTED_AREA_SIZE: capacity = %s, Size = %sB",
    "KEY_CHANGE_SECURE_AREA": "CHANGE_SECURE_AREA: cardSlot = %d, startLBA = 0x%X, blockCount = 0x%X, selector = %d, authenticate = %s",
    "KEY_CARD_TO_SECURE_MODE": "CARD_TO_SECURE_MODE: startLBA = 0x%X, blockCount = 0x%X, selector = %d",
    #################### SECURE - ENDS ####################

    #################### CARD LOCK/UNLOCK - BEGINS ####################
    "KEY_STD_LOG_CARD_LOCK_UNLOCK": "CARD_LOCK_UNLOCK: setPassword = %s, clearPassword = %s, lock = %s, erase = %s, cop = %s, additionalPassLen = %s, oldPassword = %s, newPassword = %s",

    #################### CARD LOCK/UNLOCK - BEGINS ####################

    #################### WRITE PROTECTION - BEGINS ####################
    "KEY_GET_WRITE_PROTECTED_BLOCK": "GET_WRITE_PROTECTED_BLOCK: startLBA = 0x%X",
    "KEY_SET_WRITE_PROTECTED_BLOCK": "SET_WRITE_PROTECTED_BLOCK: startLBA = 0x%X",
    #################### WRITE PROTECTION - ENDS ####################

    #################### VIDEO SPEED CLASS - BEGINS ####################
    "KEY_SPEED_CLASS": "SPEED_CLASS: speedClass = %d",
    "KEY_RU_READ_PERFORMANCE": "RU_READ_PERFORMANCE: performance = %s MB/sec",
    "KEY_RU_WRITE_PERFORMANCE": "RU_WRITE_PERFORMANCE: performance = %s MB/sec",
    "KEY_SU_READ_PERFORMANCE": "SU_READ_PERFORMANCE: performance = %s MB/sec",
    "KEY_SU_WRITE_PERFORMANCE": "SU_WRITE_PERFORMANCE: performance = %s MB/sec",
    "KEY_RECORDING_UNIT": "RECORDING_UNIT: startLBA = 0x%X, blockCount = 0x%X",
    "KEY_SUB_UNIT": "SUB_UNIT: startLBA = 0x%X, blockCount = 0x%X",
    "KEY_ALLOCATION_UNIT": "ALLOCATION_UNIT: startLBA = 0x%X, blockCount = 0x%X",
    #################### VIDEO SPEED CLASS - ENDS ####################

    #################### OTHERS - BEGINS ####################
    "KEY_GET_BUS_WIDTH": "GET_BUS_WIDTH: busWidth = %d",
    "KEY_SET_BUS_WIDTH": "SET_BUS_WIDTH: busWidth = %d",
    "KEY_SET_HOST_FREQUENCY_KHZ": "SET_HOST_FREQUENCY: hostFreq = %dKHz",
    # "KEY_SET_HOST_FREQUENCY_MHZ": "SET_HOST_FREQUENCY: hostFreq = %dMHz",
    "KEY_SET_SPEED_MODE": "SET_SPEED_MODE: speedMode = %s",
    "KEY_SET_VOLTAGE": "SET_VOLTAGE: voltage = %.2fV",
    # "KEY_CMD_FAILED_WITH_EXCEPTION": "CMD_FAILED_WITH_EXCEPTION: CMD = CMD%d",
    # "KEY_GET_CARD_CAPACITY": "GET_CARD_CAPACITY: cardCapacity = %dGB",
    "KEY_GET_CARD_MAX_LBA": "GET_CARD_MAX_LBA: maxLBA = 0x%X",
    "KEY_FAT": "FAT: startLBA = 0x%X, blockCount = 0x%X, FATaddresses = 0x%X",
    "KEY_FAT2": "FAT2: startLBA = 0x%X, blockCount = 0x%X, FATaddresses = 0x%X",
    "KEY_FAT_BITMAP": "FAT_BITMAP: startLBA = 0x%X, blockCount = 0x%X, FATaddresses = 0x%X",
    "KEY_FAT_USER_AREA": "FAT_USER_AREA: startLBA = 0x%X, blockCount = 0x%X, FATaddresses = 0x%X",
    "KEY_CARD_STATE": "CARD_STATE: state = %s",
    "KEY_CARD_CAPACITY": "CARD_CAPACITY: capacity = %s",
    "KEY_CARD_TYPE": "CARD_TYPE: Type = %s",
    # "KEY_SEND_CMD_WITH_TASK_ID": "SEND_CMD_WITH_TASK_ID: CMD = CMD%d, task = %s",
    "KEY_CALL_FUNCTION": "CALL_FUNCTION: function = %s",
    "KEY_RANDOM_WRITE_IOPS": "RANDOM_WRITE_IOPS: IOSize = %s, IOPS = %d",
    "KEY_RANDOM_READ_IOPS": "RANDOM_READ_IOPS: IOSize = %s, IOPS = %d",
    "KEY_RUN_TEST_SCRIPT": "RUN_TEST_SCRIPT: testScript = %s",
    "KEY_META_PAGE_SIZE": "META_PAGE_SIZE: Size = %d%sB",
    "KEY_META_BLOCK_SIZE": "META_BLOCK_SIZE: Size = %d%sB",
    "KEY_SEQUENTIAL_WRITE_PERFORMANCE": "SEQUENTIAL_WRITE_PERFORMANCE: performance = %s MB/sec, speedMode = %s MB/sec",
    "KEY_SEQUENTIAL_READ_PERFORMANCE": "SEQUENTIAL_READ_PERFORMANCE: performance = %s MB/sec, speedMode = %s MB/sec",
    "KEY_NON_SEQUENTIAL_WRITE_PERFORMANCE": "NON_SEQUENTIAL_WRITE_PERFORMANCE: performance = %s MB/sec, speedMode = %s MB/sec",
    "KEY_NON_SEQUENTIAL_READ_PERFORMANCE": "NON_SEQUENTIAL_READ_PERFORMANCE: performance = %s MB/sec, speedMode = %s MB/sec",
    "KEY_EXECUTION_FAILED_WITH_ERROR": "EXECUTION_FAILED_WITH_ERROR: error = %s",
    "KEY_TOTAL_NUMBER_OF_ERRORS": "TOTAL_NUMBER_OF_ERRORS: noofErrors = %d",
    "KEY_VOLTAGE_OUT_OF_RANGE": "VOLTAGE_OUT_OF_RANGE: voltage = %.2fV",
    "KEY_PERFORMANCE": "PERFORMANCE: performance = %s MB/sec",
    "KEY_NO_OF_ERRORS": "NO_OF_ERRORS: noOfErrors = %d",
    #################### OTHERS - ENDS ####################

    #################### EXPECTED EXCEPTION - BEGINS ####################
    "KEY_EXPECTED_EXCEPTION_OCCURED": "Expected %s exception occured",
    "KEY_EXPECTED_EXCEPTION_NOT_OCCURED": "Expected %s exception not occured",
    #################### EXPECTED EXCEPTION - ENDS ####################

}

################### STANDARD_LOG_MESSAGE DICTIONARY - ENDS ##############################

################### STANDARD_LOG_MESSAGE FUNCTION - BEGINS ##############################
# Standard Log Format  Class - Begins
class std_log_format(object):

    def __init__(self):
        print ("Standard log class constructor-Invoked")

    #################### USER SPECIFIC - BEGINS ####################
    # USER_SPECIFIC_MSG_WITH_TAG - Should avoid - FUNCTION
    def STD_LOG_USER_SPECIFIC_MSG_WITH_TAG(self, optDbgMsg = ""):
        return stdLogMsg["KEY_USER_SPECIFIC_MSG_WITH_TAG"] % (optDbgMsg)

    # USER_SPECIFIC_MSG_WITHOUT_TAG - Should avoid - FUNCTION
    def STD_LOG_USER_SPECIFIC_MSG_WITHOUT_TAG(self, optDbgMsg = ""):
        return stdLogMsg["KEY_USER_SPECIFIC_MSG_WITHOUT_TAG"] % (optDbgMsg)
    #################### USER SPECIFIC - ENDS ####################

    #################### LOG UTIL - BEGINS ####################
    def STD_LOG_PRINT_NOT_NONE_ARUGUMENTS(self, **argument):
        print_string = ""
        for key, value in list(argument.items()):
            if (value == True) or (value == False):
                print_string += "%s - %s, " % (key, value)
        print_string = print_string[:-2] if print_string[-2:] == ", " else print_string
        return print_string

    def STD_LOG_PRINT_DICTIONARY_VALUES(self, dictionary, new_line = False):
        print_string = ""
        for key, value in list(dictionary.items()):
            if new_line:
                print_string = print_string + "\n" + ("%s - %s" % (key, value))
            else:
                print_string += "%s - %s, " % (key, value)
        print_string = print_string[:-2] if print_string[-2:] == ", " else print_string
        return print_string
    #################### LOG UTIL - ENDS ####################

    #x.OPTIONAL MESSAGE -FUNCTION
    def STD_LOG_APPEND_OPTIONAL_MSG(self, logmsg, optDbgMsg = ""):
        return logmsg if (optDbgMsg == "") else logmsg+" [EXTRA_MSG: %s]"%optDbgMsg

    #################### GENERAL - BEGINS ####################
    def STD_LOG_HEADER(self, print_string = "", special_character = "#", repeat = 25):
        if print_string != "":
            print_string = " %s " % print_string
        return stdLogMsg["KEY_HEADER_FOOTER"].format(special_character * repeat, print_string, special_character * repeat)

    def STD_LOG_ITERATION(self, IterationCount):
        return stdLogMsg["KEY_ITERATION"] % IterationCount

    def STD_LOG_INTERAL_ITERATION(self, IterationCount):
        return stdLogMsg["KEY_INTERNAL_ITERATION"] % IterationCount

    def STD_LOG_NO_OF_ITERATION_TO_EXE(self, No_Of_Iteration):
        return stdLogMsg["KEY_NO_OF_ITERATION_TO_EXE"] % No_Of_Iteration

    def STD_LOG_DATA_COMPARE_AT_ITERATION(self, Iteration):
        return stdLogMsg["KEY_DATA_COMPARE_AT_ITERATION"] % Iteration

    def STD_LOG_CARD_STATUS_CMD13(self, card_status):
        return stdLogMsg["KEY_CARD_STATUS_CMD13"] % "{:032b}".format(card_status)

    def STD_LOG_DECODED_R1RESPONSE(self, decodedR1response):
        return stdLogMsg["KEY_DECODED_R1RESPONSE"] % decodedR1response

    def STD_LOG_SD_SPEC_VERS(self, SD_SPEC, SD_SPEC3, SD_SPEC4, SD_SPECX):
        return stdLogMsg["KEY_SD_SPEC_VERSION"] % (SD_SPEC, SD_SPEC3, SD_SPEC4, SD_SPECX)

    def STD_LOG_CARD_SUPPORT_SPEC_VER(self, Spec_version):
        return stdLogMsg["KEY_CARD_SUPPORT_SPEC_VER"] % Spec_version

    def STD_LOG_CARD_NOT_SUPPORT_SPEC_VER(self, Spec_version):
        return stdLogMsg["KEY_CARD_NOT_SUPPORT_SPEC_VER"] % Spec_version

    def STD_LOG_VERIFY_CMD_STATE_TRANSITION(self, CMD):
        return self.STD_LOG_HEADER(stdLogMsg["KEY_VERIFY_STATE_TRANSITION"] % CMD, special_character = "*", repeat = 5)

    def STD_LOG_NOT_VERIFY_CMD_STATE_TRANSITION(self, CMD):
        return self.STD_LOG_HEADER(stdLogMsg["KEY_NOT_VERIFY_STATE_TRANSITION"] % CMD, special_character = "*", repeat = 5)

    def STD_LOG_VERIFY_CMD_STATE_TRANSITION_WHEN_DAT_FREE(self, CMD):
        return self.STD_LOG_HEADER(stdLogMsg["KEY_VERIFY_STATE_TRANSITION_WHEN_DAT_FREE"] % CMD, special_character = "*", repeat = 5)

    def STD_LOG_VERIFY_CMD_STATE_TRANSITION_WHEN_DAT_IN_USE(self, CMD):
        return self.STD_LOG_HEADER(stdLogMsg["KEY_VERIFY_STATE_TRANSITION_WHEN_DAT_IN_USE"] % CMD, special_character = "*", repeat = 5)

    def STD_LOG_ARGUMENTS(self, Argument):
        return stdLogMsg["KEY_ARGUMENTS"].format("0x%X" % Argument, Argument)

    def STD_LOG_EXPECTED_ERROR_OCCURED(self, ExpectedError, OperationName):
        return stdLogMsg["KEY_EXPECTED_ERROR_OCCURED"] % (ExpectedError, OperationName)

    def STD_LOG_EXPECTED_ERROR_NOT_OCCURED(self, ExpectedError, OperationName):
        return stdLogMsg["KEY_EXPECTED_ERROR_NOT_OCCURED"] % (ExpectedError, OperationName)

    def STD_LOG_ERROR_OCCURED_OTHER_THAN_EXPECTED_ERROR(self, ExpectedError, OperationName, errstring):
        return stdLogMsg["KEY_ERROR_OCCURED_OTHER_THAN_EXPECTED_ERROR"] % (ExpectedError, OperationName, errstring)

    def STD_LOG_CMD_PASSED_AS_EXPECTED(self, CMD):
        return stdLogMsg["KEY_CMD_PASSED_AS_EXPECTED"] % CMD

    def STD_LOG_EXE_SUPPORTED_CMD(self, CMD):
        return stdLogMsg["KEY_EXE_SUPPORTED_CMD"] % CMD

    def STD_LOG_EXE_UNSUPPORTED_CMD(self, CMD):
        return stdLogMsg["KEY_EXE_UNSUPPORTED_CMD"] % CMD

    def STD_LOG_INJECT_ERROR_SCENARIO(self, CMD):
        return stdLogMsg["KEY_INJECT_ERROR_SCENARIO"] % CMD

    def STD_LOG_ITER_NO_TO_DO_POW_CYCLE_WHEN_BUS_IDLE(self, Iteration):
        return stdLogMsg["KEY_ITER_NO_TO_DO_POW_CYCLE_WHEN_BUS_IDLE"] % Iteration
    #################### GENERAL - ENDS ####################

    #################### CARD SWITCH COMMAND - BEGINS ####################
    def STD_LOG_CMD6_TO_SWITCH_SPEED_MODE(self, SpeedMode):
        return stdLogMsg["KEY_CMD6_TO_SWITCH_SPEED_MODE"] % SpeedMode

    def STD_LOG_SPEED_MODE_BACK_TO(self, SpeedMode):
        return stdLogMsg["KEY_SPEED_MODE_BACK_TO"] % SpeedMode
    #################### CARD SWITCH COMMAND - ENDS ####################

    #################### CQ - BEGINS ####################
    # ENABLE_CQ/DISABLE_CQ - FUNCTION
    def STD_LOG_SET_CQ_CACHE_CQMODE(self, Set_CQ = None, Set_Cache = None, Set_Voluntary_mode = None, Set_Sequential_mode = None):
        return stdLogMsg["KEY_SETTING"] % self.STD_LOG_PRINT_NOT_NONE_ARUGUMENTS(EnableCQ = Set_CQ, EnableCache = Set_Cache,
                                                                                 SetVoluntaryMode = Set_Voluntary_mode,
                                                                                 SetSequentialMode = Set_Sequential_mode)

    # SET CQ CONFIGURATION FAILED - FUNCTION
    def STD_LOG_SET_CQ_CONFIG_FAILED(self, Set_CQ = None, Set_Cache = None, Set_Voluntary_mode = None, Set_Sequential_mode = None):
        return stdLogMsg["KEY_SET_CQ_CONFIG_FAILED"] % self.STD_LOG_PRINT_NOT_NONE_ARUGUMENTS(EnableCQ = Set_CQ, EnableCache = Set_Cache,
                                                                                 SetVoluntaryMode = Set_Voluntary_mode,
                                                                                 SetSequentialMode = Set_Sequential_mode)

    # CHECK CURRENT CQ CONFIGURATION - FUNCTION
    def STD_LOG_CHECK_CQ_CONFIG(self, CQ_Enable = None, Cache_Enable = None, Sequential_mode = None, Voluntary_mode = None):
        return stdLogMsg["KEY_CHECKING"] % self.STD_LOG_PRINT_NOT_NONE_ARUGUMENTS(CQEnabled = CQ_Enable, CacheEnabled = Cache_Enable,
                                                                                  SequentialModeSet = Sequential_mode,
                                                                                  VoluntaryModeSet = Voluntary_mode)

    # CQ CONFIGURATION NOT MATCHED - FUNCTION
    def STD_LOG_CQ_CONFIG_NOT_MATCH(self, CQ = None, Cache = None, Voluntary = None, Sequential = None):
        return stdLogMsg["KEY_SET_FAILED"] % self.STD_LOG_PRINT_NOT_NONE_ARUGUMENTS(CQ = CQ, Cache = Cache,
                                                                                    Voluntary = Voluntary, Sequential = Sequential)

    # PRINT CURRENT CQ CONFIGURATION - FUNCTION
    def STD_LOG_CQ_CONFIG(self, CurrentCQConfiguration):
        return stdLogMsg["KEY_CQ_CONFIG"] % self.STD_LOG_PRINT_DICTIONARY_VALUES(CurrentCQConfiguration)

    # PRINT GENERAL INFORMATION FUNCTION DATA - FUNCTION
    def STD_LOG_GEN_INFO_FUNC_DATA(self, General_Information):
        return stdLogMsg["KEY_GEN_INFO_FUNC_DATA"] % self.STD_LOG_PRINT_DICTIONARY_VALUES(General_Information, new_line = False)

    # PRINT POWER MANAGEMENT FUNCTION DATA - FUNCTION
    def STD_LOG_POW_MANAGE_FUNC_DATA(self, PowerManagementFuncDict):
        return stdLogMsg["KEY_POW_MANAGE_FUNC_DATA"] % self.STD_LOG_PRINT_DICTIONARY_VALUES(PowerManagementFuncDict, new_line = False)

    # PRINT PERFORMANCE ENHANCEMENT FUNCTION DATA - FUNCTION
    def STD_LOG_PER_ENHANCE_FUNC_DATA(self, PerfEnhFuncDict):
        return stdLogMsg["KEY_PER_ENHANCE_FUNC_DATA"] % self.STD_LOG_PRINT_DICTIONARY_VALUES(PerfEnhFuncDict, new_line = False)

    # TESTING FUNCTIONS OF EXTENSION REGISTER - FUNCTION
    def STD_LOG_TEST_EXT_REG_FUNC(self, FUNCTION, ADDRESS, LENGTH):
        return stdLogMsg["KEY_TEST_EXT_REG_FUNC"] % (FUNCTION, ADDRESS, LENGTH)

    # CQ INFO IN SD STATUS REGISTER - FUNCTION
    def STD_LOG_CQ_INFO_IN_SD_STATUS_REG(self, CQInfoInSDStatusRegister):
        return stdLogMsg["KEY_CQ_INFO_IN_SD_STATUS_REG"] % self.STD_LOG_PRINT_DICTIONARY_VALUES(CQInfoInSDStatusRegister)

    # CHECK COMMAND CLASSES SUPPORT - FUNCTION
    def STD_LOG_CHECK_COMMAND_CLASSES_SUPPORT(self, *CommandClass):
        return stdLogMsg["KEY_CHECK_COMMAND_CLASSES_SUPPORT"] % str(CommandClass)

    # COMMAND CLASS SUPPORTED - FUNCTION
    def STD_LOG_COMMAND_CLASS_SUPPORTED(self, CommandClassNumber):
        return stdLogMsg["KEY_COMMAND_CLASS_SUPPORTED"] % CommandClassNumber

    # COMMAND CLASS NOT SUPPORTED - FUNCTION
    def STD_LOG_COMMAND_CLASS_NOT_SUPPORTED(self, CommandClassNumber):
        return stdLogMsg["KEY_COMMAND_CLASS_NOT_SUPPORTED"] % CommandClassNumber

    # EXTENSION REGISTER SUPPORTED/NOT SUPPORTED - FUNCTION
    def STD_LOG_EXTN_REG_CMDS_SUPPORT_IN_SCR(self, ExtnRegCmdSupport):
        return stdLogMsg["KEY_EXTN_REG_CMDS_SUPPORT_IN_SCR"] % ExtnRegCmdSupport

    # CQ SUPPORTED - FUNCTION
    def STD_LOG_CQ_SUPPORTED_WITH_QUEUE_DEPTH(self, QueueDepth):
        return stdLogMsg["KEY_CQ_SUPPORTED_WITH_QUEUE_DEPTH"] % QueueDepth

    # NUMBER OF TASKS - FUNCTION
    def STD_LOG_NO_OF_TASKS_TO_Q(self, No_of_Tasks):
        return stdLogMsg["KEY_NO_OF_TASKS_TO_Q"] % No_of_Tasks

    # QUEUE RANDOM TASK - FUNCTION
    def STD_LOG_RANDOM_TASK_QUEUE(self, TaskID):
        return stdLogMsg["KEY_RANDOM_TASK_QUEUE"] % TaskID

    # EXECUTE RANDOM TASK - FUNCTION
    def STD_LOG_RANDOM_TASK_EXECUTE(self, TaskID):
        return stdLogMsg["KEY_RANDOM_TASK_EXECUTE"] % TaskID

    # NUMBER OF TASKS TO QUEUE PARALLELY WHILE ONE TASK IS IN EXECUTION - FUNCTION
    def STD_LOG_NO_OF_TASKS_TO_Q_PARALLELY_WHILE_TASK_IN_EXE(self, No_of_Tasks):
        return stdLogMsg["KEY_NO_OF_TASKS_TO_Q_PARALLELY_WHILE_TASK_IN_EXE"] % No_of_Tasks

    # RANDOM NUMBER OF TASKS GENERATED - FUNCTION
    def STD_LOG_RANDOM_NO_OF_TASKS(self, No_of_Tasks):
        return stdLogMsg["KEY_RANDOM_NO_OF_TASKS"] % No_of_Tasks

    # NUMBER OF TASKS TO ABORT - FUNCTION
    def STD_LOG_NO_OF_TASKS_TO_ABORT(self, No_of_Tasks):
        return stdLogMsg["KEY_NO_OF_TASKS_TO_ABORT"] % No_of_Tasks

    # NUMBER OF TASKS TO QUEUE AFTER CMD43 - FUNCTION
    def STD_LOG_NO_OF_TASKS_TO_Q_AFTER_CMD43(self, No_of_Tasks):
        return stdLogMsg["KEY_NO_OF_TASKS_TO_Q_AFTER_CMD43"] % No_of_Tasks

    # CMD43 ARGUMENTS - FUNCTION
    def STD_LOG_CMD43_ARGS(self, OpCode, TaskID):
        return stdLogMsg["KEY_CMD43_ARGS_OPCODE"] % (OpCode, TaskID)

    # SEND CMD43 TO ABORT SINGLE TASK - FUNCTION
    def STD_LOG_ABORT_SINGLE_TASK(self, TaskID):
        return stdLogMsg["KEY_ABORT_SINGLE_TASK"] % TaskID

    def STD_LOG_ABORT_AFTER_SOME_BLOCKS(self, No_of_Blocks):
        return stdLogMsg["KEY_ABORT_AFTER_SOME_BLOCKS"] % No_of_Blocks

    # CMD43 TO ABORT REMAINING TASKS IN QUEUE - FUNCTION
    def STD_LOG_CMD43_TO_ABORT_REMAINING_TASKS_IN_QUEUE(self, No_of_Tasks):
        return stdLogMsg["KEY_CMD43_TO_ABORT_REMAINING_TASKS_IN_QUEUE"] % No_of_Tasks

    # CMD43 BUSY STATUS - FUNCTION
    def STD_LOG_BUSY_STATUS_BY_HOST(self, BusyStatus):
        return stdLogMsg["KEY_BUSY_STATUS_BY_HOST"] % BusyStatus

    # CMD43 FAILURE - FUNCTION
    def STD_LOG_CMD43_FAILED(self, TaskID, OpCode):
        return stdLogMsg["KEY_CMD43_FAILED"] % (OpCode if OpCode == 1 else ("%s, TaskID - %s" % (OpCode, TaskID)))

    # CMD44 ARGUMENTS - FUNCTION
    def STD_LOG_CMD44_ARGS(self, Direction, ExtendedAddress, Priority, TaskID, NumberOfBlocks):
        return stdLogMsg["KEY_CMD44_ARGS"] % (Direction, ExtendedAddress, Priority, TaskID, NumberOfBlocks)

    # CMD44 FAILURE - FUNCTION
    def STD_LOG_CMD44_FAILED(self, Direction, ExtendedAddress, Priority, TaskID, NumberOfBlocks):
        return stdLogMsg["KEY_CMD44_FAILED"] % (Direction, ExtendedAddress, Priority, TaskID, NumberOfBlocks)

    # CMD44 REISSUED COUNT - FUNCTION
    def STD_LOG_CMD44_REISSUED_COUNT(self, Reissued_count):
        return stdLogMsg["KEY_CMD44_REISSUED_COUNT"] % Reissued_count

    # CMD44 FAILED FOR 3 TIMES - FUNCTION
    def STD_LOG_CMD44_FAILED_FOR_3_TIMES(self, TaskID, ErrorMessage):
        return stdLogMsg["KEY_CMD44_FAILED_FOR_3_TIMES"] % (TaskID, ErrorMessage)

    # CMD45 ARGUMENTS - FUNCTION
    def STD_LOG_CMD45_ARGS(self, StartBlockAddress):
        return stdLogMsg["KEY_CMD45_ARGS"] % StartBlockAddress

    # CMD45 FAILURE - FUNCTION
    def STD_LOG_CMD45_FAILED(self, StartBlockAddress):
        return stdLogMsg["KEY_CMD45_FAILED"] % StartBlockAddress

    # TASK AGED OUT - FUNCTION
    def STD_LOG_TASK_AGED_OUT(self, AgedTaskID, AgeingThreshold):
        return stdLogMsg["KEY_TASK_AGED_OUT"] % (AgedTaskID, AgeingThreshold)

    # CQ TASK AGEING DICTIONARY - FUNCTION
    def STD_LOG_CQ_TASK_AGEING_DICT(self, CQTaskAgeingDict):
        return stdLogMsg["KEY_CQ_TASK_AGEING_DICT"] % CQTaskAgeingDict

    # CQ_EXECUTE_READ_TASK - FUNCTION
    def STD_LOG_CQ_EXE_READ_TASK(self, TaskID, StartBlockAddr, NumBlocks, NoData, Pattern, DoCompare, lbaTag, SequenceTag, SequenceNumber):
        return stdLogMsg["KEY_CQ_EXECUTE_READ_TASK"] % (TaskID, StartBlockAddr, NumBlocks, NoData, Pattern, DoCompare, lbaTag, SequenceTag, SequenceNumber)

    # CQ_EXECUTE_READ_TASK_FAILED - FUNCTION
    def STD_LOG_CQ_EXE_READ_TASK_FAILED(self, TaskID, ErrorMessage):
        return stdLogMsg["KEY_CQ_EXECUTE_READ_TASK_FAILED"] % (TaskID, ErrorMessage)

    # CQ_EXECUTE_WRITE_TASK - FUNCTION
    def STD_LOG_CQ_EXE_WRITE_TASK(self, TaskID, StartBlockAddr, NumBlocks, NoData, Pattern, lbaTag, SequenceTag, SequenceNumber):
        return stdLogMsg["KEY_CQ_EXECUTE_WRITE_TASK"] % (TaskID, StartBlockAddr, NumBlocks, NoData, Pattern, lbaTag, SequenceTag, SequenceNumber)

    # CQ_EXECUTE_WRITE_TASK_FAILED - FUNCTION
    def STD_LOG_CQ_EXE_WRITE_TASK_FAILED(self, TaskID, ErrorMessage):
        return stdLogMsg["KEY_CQ_EXECUTE_WRITE_TASK_FAILED"] % (TaskID, ErrorMessage)

    # CMD46 ARGUMENTS - FUNCTION
    def STD_LOG_CMD46_ARGS(self, TaskID, blockCount, NoData, BufObj, Pattern):
        return stdLogMsg["KEY_CMD46_ARGS"] % (TaskID, blockCount, NoData, BufObj, Pattern)

    # CMD47 ARGUMENTS - FUNCTION
    def STD_LOG_CMD47_ARGS(self, TaskID, blockCount, NoData, BufObj, Pattern):
        return stdLogMsg["KEY_CMD47_ARGS"] % (TaskID, blockCount, NoData, BufObj, Pattern)

    # CMD48 ARGUMENTS - FUNCTION
    def STD_LOG_CMD48_ARGS(self, MIO, ExtnFunNum, Address, Length):
        return stdLogMsg["KEY_CMD48_ARGS"] % (MIO, ExtnFunNum, Address, Length)

    # CMD49 ARGUMENTS - FUNCTION
    def STD_LOG_CMD49_ARGS(self, MIO, ExtnFunNum, MW, Address, LenORMask):
        return stdLogMsg["KEY_CMD49_ARGS"] % (MIO, ExtnFunNum, MW, Address, LenORMask)

    # AGEING COUNTER FOR ALL TASKS - FUNCTION
    def STD_LOG_QUEUE_STATUS_IN_VOL_CQ(self, CQTaskAgeingDict):
        return stdLogMsg["KEY_AGEING_COUNTER_FOR_TASKS"] % CQTaskAgeingDict

    # QUEUE STATUS OF ALL TASKS - FUNCTION
    def STD_LOG_QUEUE_STATUS_IN_SEQ_CQ(self, CQTaskAgeingDict):
        return stdLogMsg["KEY_QUEUE_STATUS_IN_SEQ_CQ"] % CQTaskAgeingDict

    # QUEUE LIST BEFORE EXECUTION - FUNCTION
    def STD_LOG_QUEUE_LIST_BEFORE_EXE(self, TaskQueuedList):
        return stdLogMsg["KEY_QUEUE_LIST_BEFORE_EXE"] % TaskQueuedList

    # QUEUE BECAME EMPTY AFTER N NUMBER OF TASKS - FUNCTION
    def STD_LOG_QUEUE_BE_EMPTY_AFTER_EXE_N_TASKS(self, No_of_Tasks_Executed, Initial_No_of_Tasks):
        return stdLogMsg["KEY_QUEUE_BE_EMPTY_AFTER_N_TASKS"] % (No_of_Tasks_Executed, Initial_No_of_Tasks)

    # NOT CHECKING THE READINESS OF THE TASK - FUNCTION
    def STD_LOG_NOT_CHECK_READINESS_OF_TASK(self, TaskID):
        return stdLogMsg["KEY_NOT_CHECK_READINESS_OF_TASK"] % TaskID

    # 32 BIT TASK STATUS REGISTER - FUNCTION
    def STD_LOG_TASK_STATUS_REG_32BIT(self, TSR):
        return stdLogMsg["KEY_TASK_STATUS_REG_32BIT"].format(TSR)

    # SEND HIGH PRIORITY TASK - FUNCTION
    def STD_LOG_HIGH_PRIORITY_TASK(self, TaskID):
        return stdLogMsg["KEY_HIGH_PRIORITY_TASK"] % TaskID

    # SEND LOW PRIORITY TASK - FUNCTION
    def STD_LOG_LOW_PRIORITY_TASK(self, TaskID):
        return stdLogMsg["KEY_LOW_PRIORITY_TASK"] % TaskID

    # NUMBER OF TASKS TO BE PENDING IN THE QUEUE - FUNCTION
    def STD_LOG_NO_OF_TASKS_TO_BE_PENDING_IN_Q(self, NO_OF_TASKS):
        return stdLogMsg["KEY_NO_OF_TASKS_TO_BE_PENDING_IN_Q"] % NO_OF_TASKS

    def STD_LOG_PATTERN_LIST(self, PATTERN_LIST):
        return stdLogMsg["KEY_PATTERN_LIST"] % PATTERN_LIST

    def STD_LOG_SHUFFLED_PATTERN_LIST(self, SHUFFLED_PATTERN_LIST):
        return stdLogMsg["KEY_SHUFFLED_PATTERN_LIST"] % SHUFFLED_PATTERN_LIST

    # TASK ID LIST - FUNCTION
    def STD_LOG_TASK_ID_LIST(self, TASK_ID_LIST):
        return stdLogMsg["KEY_TASK_ID_LIST"] % (len(TASK_ID_LIST), TASK_ID_LIST)

    # TASK UNQUEUED LIST - FUNCTION
    def STD_LOG_TASK_UNQUEUED_LIST(self, TASK_UNQUEUED_LIST):
        return stdLogMsg["KEY_TASK_UNQUEUED_LIST"] % (len(TASK_UNQUEUED_LIST), TASK_UNQUEUED_LIST)

    # TASK QUEUED LIST AFTER QUEUE N TASKS - FUNCTION
    def STD_LOG_TASK_QUEUED_LIST_AFTER_N_QUEUE(self, No_of_Tasks_Queued, TASK_QUEUED_LIST):
        return stdLogMsg["KEY_TASK_QUEUED_LIST_AFTER_N_QUEUE"] % (No_of_Tasks_Queued, TASK_QUEUED_LIST)

    # TASK QUEUED LIST - FUNCTION
    def STD_LOG_TASK_QUEUED_LIST(self, TASK_QUEUED_LIST):
        return stdLogMsg["KEY_TASK_QUEUED_LIST"] % (len(TASK_QUEUED_LIST), TASK_QUEUED_LIST)

    # TASK READY LIST - FUNCTION
    def STD_LOG_TASK_READY_LIST(self, TASK_READY_LIST):
        return stdLogMsg["KEY_TASK_READY_LIST"] % (len(TASK_READY_LIST), TASK_READY_LIST)

    # TASK NOT READY LIST - FUNCTION
    def STD_LOG_TASK_NOT_READY_LIST(self, TASK_NOT_READY_LIST):
        return stdLogMsg["KEY_TASK_NOT_READY_LIST"] % (len(TASK_NOT_READY_LIST), TASK_NOT_READY_LIST)

    # TASK LIST TO EXECUTE - FUNCTION
    def STD_LOG_TASK_EXE_LIST(self, TASK_EXE_LIST):
        return stdLogMsg["KEY_TASK_EXE_LIST"] % (len(TASK_EXE_LIST), TASK_EXE_LIST)

    # TASK EXECUTED LIST - FUNCTION
    def STD_LOG_TASK_EXECUTED_LIST(self, TasksCompletedList):
        return stdLogMsg["KEY_TASK_EXECUTED_LIST"] % TasksCompletedList

    # ABORT TASK READY. SO BREAK THE LOOP TO SKIP EXE - FUNCTION
    def STD_LOG_ABORT_TASK_READY_BREAK_LOOP_FOR_SKIP_EXE(self, TaskID):
        return stdLogMsg["KEY_ABORT_TASK_READY_BREAK_LOOP_FOR_SKIP_EXE"] % TaskID

    # DATA COMPARE ITERATION LIST - FUNCTION
    def STD_LOG_DATA_COMPARE_LIST(self, DataCompareCount, DataCompareList):
        return stdLogMsg["KEY_DATA_COMPARE_LIST"] % (DataCompareCount, DataCompareList)

    # STOP TRANSMISSION DURING DATA TRANSFER LIST - FUNCTION
    def STD_LOG_STOP_TRANS_DURING_DATA_TRANS_LIST(self, StopTransmissionCount, StopTransmissionList):
        return stdLogMsg["KEY_STOP_TRANS_DURING_DATA_TRANS_LIST"] % (StopTransmissionCount, StopTransmissionList)

    # STOP TRANSMISSION AFTER DATA TRANSFER LIST - FUNCTION
    def STD_LOG_STOP_TRANS_AFTER_DATA_TRANS_LIST(self, StopTransmissionCount, StopTransmissionList):
        return stdLogMsg["KEY_STOP_TRANS_AFTER_DATA_TRANS_LIST"] % (StopTransmissionCount, StopTransmissionList)

    # EXECUTE REMAINING QUEUED TASKS - FUNCTION
    def STD_LOG_EXE_REMAINING_QUEUED_TASKS(self, NO_OF_REMAINING_QUEUED_TASKS, TASK_QUEUED_LIST):
        return stdLogMsg["KEY_EXE_REMAINING_QUEUED_TASKS"] % (NO_OF_REMAINING_QUEUED_TASKS, TASK_QUEUED_LIST)

    # NUMBER OF REMAINING TASKS TO QUEUE - FUNCTION
    def STD_LOG_NO_OF_REMAIN_TASKS_TO_QUEUE(self, NO_OF_TASKS):
        return stdLogMsg["KEY_NO_OF_REMAIN_TASKS_TO_QUEUE"] % NO_OF_TASKS

    # NUMBER OF REMAINING TASKS TO EXECUTE - FUNCTION
    def STD_LOG_NO_OF_REMAIN_TASKS_TO_EXE(self, NO_OF_TASKS):
        return stdLogMsg["KEY_NO_OF_REMAIN_TASKS_TO_EXE"] % NO_OF_TASKS

    # TASK REQUEUED LIST - FUNCTION
    def STD_LOG_TASK_REQUEUED_LIST(self, NO_OF_TASKS_REQUEUED, TASK_REQUEUED_LIST):
        return stdLogMsg["KEY_TASK_REQUEUED_LIST"] % (NO_OF_TASKS_REQUEUED, TASK_REQUEUED_LIST)

    # TASK IS READY - FUNCTION
    def STD_LOG_TASK_READY(self, TaskID):
        return stdLogMsg["KEY_TASK_READY"] % TaskID

    # TASK IS NOT READY - FUNCTION
    def STD_LOG_TASK_NOT_READY(self, TaskID):
        return stdLogMsg["KEY_TASK_NOT_READY"] % TaskID

    # TASK ABORT - FUNCTION
    def STD_LOG_TASK_ABORT(self, TaskID):
        return stdLogMsg["KEY_TASK_ABORT"] % TaskID

    # TASK ABORTED - FUNCTION
    def STD_LOG_TASK_ABORTED(self, TaskID):
        return stdLogMsg["KEY_TASK_ABORTED"] % TaskID

    # TASK NOT ABORTED - FUNCTION
    def STD_LOG_TASK_NOT_ABORTED(self, TaskID):
        return stdLogMsg["KEY_TASK_NOT_ABORTED"] % TaskID

    # READY BIT NOT SET FOR THE TASK - FUNCTION
    def STD_LOG_READY_BIT_NOT_SET_FOR_TASK(self, TaskID, TimeInMs):
        return stdLogMsg["KEY_READY_BIT_NOT_SET_FOR_TASK"] % (TaskID, TimeInMs)

    # READY BIT NOT SET FOR THE TASK, SO READ THE TASK STATUS REGISTER AGAIN - FUNCTION
    def STD_LOG_READ_TASK_STAUS_AGAIN_FOR_TASK(self, TaskID, TimeInMs):
        return stdLogMsg["KEY_READ_TASK_STAUS_AGAIN_FOR_TASK"] % (TaskID, TimeInMs)

    # TASK STATUS REGISTER VALUE AFTER CARD INIT - FUNCTION
    def STD_LOG_TSR_VALUE_AFTER_CARD_INIT(self, TSR):
        return stdLogMsg["KEY_TSR_VALUE_AFTER_CARD_INIT"] % TSR

    # TASK STATUS REGISTER IS 0 - FUNCTION
    def STD_LOG_TASK_STATUS_REG_IS_0(self, TimeInMs):
        return stdLogMsg["KEY_TASK_STATUS_REG_IS_0"] % TimeInMs

    # TASK STATUS REGISTER IS 0, SO READ TASK STATUS REGISTER AGAINS - FUNCTION
    def STD_LOG_TASK_STATUS_REG_IS_0_READ_TSR_AGAIN(self, TimeInMs):
        return stdLogMsg["KEY_TASK_STATUS_REG_IS_0_READ_TSR_AGAIN"] % TimeInMs

    # TASK STATUS REGISTER IS CLEARED FOR TASK - FUNCTION
    def STD_LOG_TASK_STATUS_REG_CLEARED_FOR_TASK(self, TaskID):
        return stdLogMsg["KEY_TASK_STATUS_REG_CLEARED_FOR_TASK"] % TaskID

    # TASK STATUS REGISTER IS NOT CLEARED FOR TASK - FUNCTION
    def STD_LOG_TASK_STATUS_REG_NOT_CLEARED_FOR_TASK(self, TaskID):
        return stdLogMsg["KEY_TASK_STATUS_REG_NOT_CLEARED_FOR_TASK"] % TaskID

    # TASK STATUS REGISTER IS CLEARED - FUNCTION
    def STD_LOG_TASK_STATUS_REG_CLEARED(self, TSR):
        return stdLogMsg["KEY_TASK_STATUS_REG_CLEARED"] % TSR

    # TASK STATUS REGISTER IS NOT CLEARED - FUNCTION
    def STD_LOG_TASK_STATUS_REG_NOT_CLEARED(self, TSR):
        return stdLogMsg["KEY_TASK_STATUS_REG_NOT_CLEARED"] % TSR

    # TASK STATUS REGISTER VALUE AFTER TASK COMPLETION - FUNCTION
    def STD_LOG_TASK_STATUS_REG_VALUE_AFTER_TASK_EXE(self, TSR):
        return stdLogMsg["KEY_TASK_STATUS_REG_VALUE_AFTER_TASK_EXE"] % TSR

    # TASK DATA TRANSFER STATUS - FUNCTION
    def STD_LOG_TASK_DATA_TRANS_STATUS(self, Direction, TaskID, DataTransferStatus):
        return stdLogMsg["KEY_TASK_DATA_TRANS_STATUS"] % (Direction, TaskID, DataTransferStatus)

    # TASK DATA TRANSFER TIMEOUT - FUNCTION
    def STD_LOG_TASK_DATA_TRANS_TIMEOUT(self, Direction, TaskID, TIMEOUT, DataTransferStatus):
        return stdLogMsg["KEY_TASK_DATA_TRANS_TIMEOUT"] % (Direction, TaskID, TIMEOUT, DataTransferStatus)

    # TASK DATA TRANSFER FAILED - FUNCTION
    def STD_LOG_TASK_DATA_TRANS_FAILED(self, Direction, TaskID, ErrorCode, ErrorString):
        return stdLogMsg["KEY_TASK_DATA_TRANS_FAILED"] % (Direction, TaskID, ErrorCode, ErrorString)

    # TASK DATA TRANSFER DONE - FUNCTION
    def STD_LOG_TASK_DATA_TRANS_DONE(self, Direction, TaskID):
        return stdLogMsg["KEY_TASK_DATA_TRANS_DONE"] % (Direction, TaskID)

    # TASK DATA TRANS DONE SEND CMD13 TO CHECK TRANS STATE - FUNCTION
    def STD_LOG_TASK_DATA_TRANS_DONE_SEND_CMD13_TO_CHECK_TRANS_STATE(self, TaskID):
        return stdLogMsg["KEY_TASK_DATA_TRANS_DONE_SEND_CMD13_TO_CHECK_TRANS_STATE"] % (TaskID)

    # TASK DATA TRANSFER DONE WITHIN 0.250 SECOND - FUNCTION
    def STD_LOG_TASK_DATA_TRANS_DONE_WITHIN_250MS(self, Direction, TaskID, DataTransferStatus):
        return stdLogMsg["KEY_TASK_DATA_TRANS_DONE_WITHIN_250MS"] % (Direction, TaskID, DataTransferStatus)

    # TIME TAKEN FOR TASK DATA TRANSFER - FUNCTION
    def STD_LOG_TIME_TAKEN_FOR_TASK_DATA_TRANS(self, Direction, TaskID, TimeTakenForStatusPolling, DataTransferStatus):
        return stdLogMsg["KEY_TASK_TIME_TAKEN_FOR_TASK_DATA_TRANS"] % (Direction, TaskID, TimeTakenForStatusPolling, DataTransferStatus)

    # TASK DATA TRANSFER EXCEEDS 3 MINUTES - FUNCTION
    def STD_LOG_TASK_DATA_TRANS_EXCEEDS_3MIN(self, Direction, TaskID, TimeTakenForStatusPolling):
        return stdLogMsg["KEY_TASK_DATA_TRANS_EXCEEDS_3MIN"] % (Direction, TaskID, TimeTakenForStatusPolling)

    def STD_LOG_TASK_TO_ABORT_WITH_CMD0(self, TaskID):
        return stdLogMsg["KEY_TASK_TO_ABORT_WITH_CMD0"] % TaskID

    def STD_LOG_CMD0_TO_STOP_DATA_TRANS_OF_TASK(self, TaskID):
        return stdLogMsg["KEY_CMD0_TO_STOP_DATA_TRANS_OF_TASK"] % TaskID

    def STD_LOG_CMD0_AFTER_EXE_TASK(self, TaskID):
        return stdLogMsg["KEY_CMD0_AFTER_EXE_TASK"] % TaskID

    def STD_LOG_CMD12_TO_STOP_DATA_TRANS_OF_TASK(self, TaskID):
        return stdLogMsg["KEY_CMD12_TO_STOP_DATA_TRANS_OF_TASK"] % TaskID

    def STD_LOG_TASK_TO_ABORT_WITH_POW_CYCLE(self, TaskID):
        return stdLogMsg["KEY_TASK_TO_ABORT_WITH_POW_CYCLE"] % TaskID

    def STD_LOG_POW_CYCLE_TO_STOP_DATA_TRANS_OF_TASK(self, TaskID):
        return stdLogMsg["KEY_POW_CYCLE_TO_STOP_DATA_TRANS_OF_TASK"] % TaskID

    def STD_LOG_POW_CYCLE_AFTER_EXE_TASK(self, TaskID):
        return stdLogMsg["KEY_POW_CYCLE_AFTER_EXE_TASK"] % TaskID

    # CARD IS NOT IN CQ TRANSFER STATE AFTER TASK DATA TRANSFER COMPLETION - FUNCTION
    def STD_LOG_CARD_NOT_IN_CQ_TRANS_STATE_AFTER_DATA_TRANS(self, Direction, TaskID, CMD13responseList):
        return stdLogMsg["KEY_CARD_NOT_IN_CQ_TRANS_STATE_AFTER_DATA_TRANS"] % (Direction, TaskID, CMD13responseList)

    # TASK ERROR STATUS OF ALL TASKS IN EXTENSION REGISTER - FUNCTION
    def STD_LOG_TASK_ERROR_STATUS_OF_ALL_TASKS_IN_CMD48(self, TaskErrorStatus):
        return stdLogMsg["KEY_TASK_ERROR_STATUS_OF_ALL_TASKS_IN_CMD48"] % TaskErrorStatus

    # TASK ERROR STATUS OF A TASK IN EXTENSION REGISTER - FUNCTION
    def STD_LOG_TASK_ERROR_STATUS_OF_A_TASK_IN_CMD48(self, TaskID, TaskErrorStatus):
        return stdLogMsg["KEY_TASK_ERROR_STATUS_OF_A_TASK_IN_CMD48"] % (TaskID, TaskErrorStatus)

    # TASK ERROR STATUS OF A TASK IS NOT SHOWN IN EXTENSION REGISTER - FUNCTION
    def STD_LOG_TASK_ERROR_STATUS_OF_A_TASK_NOT_SHOWN_IN_CMD48(self, TaskID):
        return stdLogMsg["KEY_TASK_ERROR_STATUS_OF_A_TASK_NOT_SHOWN_IN_CMD48"] % TaskID

    # TASK ID TO CHECK MISCOMPARE - FUNCTION
    def STD_LOG_TASK_TO_CHECK_MISCOMPARE(self, TaskID):
        return stdLogMsg["KEY_TASK_TO_CHECK_MISCOMPARE"] % TaskID

    # MISCOMPARE OCCURED FOR TASK - FUNCTION
    def STD_LOG_MISCOMPARE_OCCURED_FOR_TASK(self, Direction, TaskID):
        return stdLogMsg["KEY_MISCOMPARE_OCCURED_FOR_TASK"] % (Direction, TaskID)

    # CQ AGEING - FUNCTION
    def STD_LOG_CQ_AGEING(self, ag):
        return stdLogMsg["KEY_EMPTY_STRING"] % ag

    # QUEUE THE TASK TO ABORT - FUNCTION
    def STD_LOG_QUEUE_TASK_TO_ABORT(self, TaskID):
        return stdLogMsg["KEY_QUEUE_TASK_TO_ABORT"] % TaskID

    # SEND CMD44 FOR TASK ID - FUNCTION
    def STD_LOG_SEND_CMD44_FOR_TASK_ID(self, TaskID):
        return stdLogMsg["KEY_SEND_CMD44_FOR_TASK_ID"] % TaskID

    # SEND CMD44 AGAIN FOR TASK ID - FUNCTION
    def STD_LOG_SEND_CMD44_AGAIN_FOR_TASK_ID(self, TaskID):
        return stdLogMsg["KEY_SEND_CMD44_AGAIN_FOR_TASK_ID"] % TaskID

    # SEND CMD45 FOR TASK ID - FUNCTION
    def STD_LOG_SEND_CMD45_FOR_TASK_ID(self, TaskID):
        return stdLogMsg["KEY_SEND_CMD45_FOR_TASK_ID"] % TaskID

    # SEND CMD44 AND CMD45 FOR TASK ID - FUNCTION
    def STD_LOG_SEND_CMD44_CMD45_FOR_TASK_ID(self, TaskID):
        return stdLogMsg["KEY_SEND_CMD44_CMD45_FOR_TASK_ID"] % TaskID

    # SEND CMD46 FOR TASK ID - FUNCTION
    def STD_LOG_SEND_CMD46_FOR_TASK_ID(self, TaskID):
        return stdLogMsg["KEY_SEND_CMD46_FOR_TASK_ID"] % TaskID

    # SEND CMD46 FOR TASK ID TO ABORT AFTER SOME PARTICULAR BLOCKS - FUNCTION
    def STD_LOG_SEND_CMD46_FOR_TASK_ID_TO_ABORT(self, TaskID, NumBlocksForAbort):
        return stdLogMsg["KEY_SEND_CMD46_FOR_TASK_ID_TO_ABORT"] % (TaskID, NumBlocksForAbort)

    # SEND CMD47 FOR TASK ID - FUNCTION
    def STD_LOG_SEND_CMD47_FOR_TASK_ID(self, TaskID):
        return stdLogMsg["KEY_SEND_CMD47_FOR_TASK_ID"] % TaskID

    # SEND CMD47 FOR TASK ID TO ABORT AFTER SOME PARTICULAR BLOCKS - FUNCTION
    def STD_LOG_SEND_CMD47_FOR_TASK_ID_TO_ABORT(self, TaskID, NumBlocksForAbort):
        return stdLogMsg["KEY_SEND_CMD47_FOR_TASK_ID_TO_ABORT"] % (TaskID, NumBlocksForAbort)

    # VERFIY CQ WRITE WITH LEGACY READ - FUNCTION
    def STD_LOG_VERFIY_CQ_WRITE_WITH_LEGACY_READ(self, TaskID):
        return stdLogMsg["KEY_VERFIY_CQ_WRITE_WITH_LEGACY_READ"] % TaskID

    # COMPARE CQ WRITE AND READ DATA - FUNCTION
    def STD_LOG_COMPARE_CQ_WRITE_READ_DATA(self, TaskID):
        return stdLogMsg["KEY_COMPARE_CQ_WRITE_READ_DATA"] % TaskID

    # CQ WRITE AND READ COMPARE FAILED FOR TASK ID - FUNCTION
    def STD_LOG_COMPARE_FAILED_FOR_TASK(self, TaskID):
        return stdLogMsg["KEY_COMPARE_FAILED_FOR_TASK"] % TaskID

    # COMPARE FOR OLD PATTERN AFTER STOP TRANSMISSION - FUNCTION
    def STD_LOG_COMPARE_OLD_PATTERN(self, Offset, No_of_Blocks, Pattern):
        return stdLogMsg["KEY_COMPARE_OLD_PATTERN"] % (Offset, No_of_Blocks, Pattern)

    # COMPARE FOR NEW PATTERN AFTER STOP TRANSMISSION - FUNCTION
    def STD_LOG_COMPARE_NEW_PATTERN(self, No_of_Blocks, Pattern):
        return stdLogMsg["KEY_COMPARE_NEW_PATTERN"] % (No_of_Blocks, Pattern)

    # COMPARE REMAINING BLOCKS FOR OLD PATTERN - FUNCTION
    def STD_LOG_COMPARE_REMAIN_BLOCKS_FOR_OLD_PATTERN(self, Offset, No_of_Blocks, Pattern):
        return stdLogMsg["KEY_COMPARE_REMAIN_BLOCKS_FOR_OLD_PATTERN"] % (Offset, No_of_Blocks, Pattern)

    # BLOCKS WHICH HAD NEW PATTERN AFTER STOP TRANSMISSION - FUNCTION
    def STD_LOG_BLOCKS_HAD_NEW_PATTERN(self, No_of_Blocks, Pattern):
        return stdLogMsg["KEY_BLOCKS_HAD_NEW_PATTERN"] % (No_of_Blocks, Pattern)

    # ABORT TASK WITH PATTERN - FUNCTION
    def STD_LOG_ABORT_TASK_PATTERN(self, Pattern):
        return stdLogMsg["KEY_ABORT_TASK_PATTERN"] % Pattern

    # ABORT TASK WITH USER PATTERN - FUNCTION
    def STD_LOG_ABORT_TASK_USER_PATTERN(self, Pattern):
        return stdLogMsg["KEY_ABORT_TASK_USER_PATTERN"] % Pattern

    # USER BUFFER USED FOR CQ WRITE/READ - FUNCTION
    def STD_LOG_USER_BUF_FOR_CQ_WRITE_OR_READ(self, Pattern, StartLba, BlockCount):
        return stdLogMsg["KEY_USER_BUF_FOR_CQ_WRITE_OR_READ"] % (Pattern, StartLba, BlockCount)

    # PRECONDITION WITH PATTERN - FUNCTION
    def STD_LOG_PRECOND_PATTERN(self, Pattern):
        return stdLogMsg["KEY_PRECOND_PATTERN"] % Pattern

    # PRECONDITION WITH USER PATTERN - FUNCTION
    def STD_LOG_PRECOND_USER_PATTERN(self, Pattern):
        return stdLogMsg["KEY_PRECOND_USER_PATTERN"] % Pattern

    # PRECONDITION LEGACY WRITE FOR CQ TASK - FUNCTION
    def STD_LOG_PRECOND_LEGACY_WRITE_FOR_TASK_ID(self, TaskID):
        return stdLogMsg["KEY_PRECOND_LEGACY_WRITE_FOR_TASK_ID"] % TaskID

    # PRECONDITION IN LEGACY FOR PATTERN - FUNCTION
    def STD_LOG_PRECOND_LEGACY_FOR_PATTERN(self, Pattern):
        return stdLogMsg["KEY_PRECOND_LEGACY_FOR_PATTERN"] % Pattern

    # SEND EXTENSION REGISTER CMD IN LOOP - FUNCTION
    def STD_LOG_SEND_EXT_REG_CMD_IN_LOOP(self, CMD, Iteration):
        return stdLogMsg["KEY_SEND_EXT_REG_CMD_IN_LOOP"] % (CMD, Iteration)

    # SEND CQ CMD IN LOOP FOR SAME TASK - FUNCTION
    def STD_LOG_SEND_CQ_CMD_IN_LOOP_FOR_A_TASK_ID(self, CMD, TaskID, Iteration):
        return stdLogMsg["KEY_SEND_CQ_CMD_IN_LOOP_FOR_A_TASK_ID"] % (CMD, TaskID, Iteration)

    def STD_LOG_ABORT_SINGLE_TASK_IN_LOOP_REACHED(self, TaskID):
        return stdLogMsg["KEY_ABORT_SINGLE_TASK_IN_LOOP_REACHED"] % TaskID

    def STD_LOG_ABORT_WHOLE_QUEUE_IN_LOOP_REACHED(self, TaskID):
        return stdLogMsg["KEY_ABORT_WHOLE_QUEUE_IN_LOOP_REACHED"] % TaskID

    def STD_LOG_ABORT_WHOLE_QUEUE_FOR_ITERATION(self, TaskID):
        return stdLogMsg["KEY_ABORT_WHOLE_QUEUE_FOR_ITERATION"] % TaskID

    # NUMBER OF TASKS TO EXECUTE - FUNCTION
    def STD_LOG_NO_OF_TASKS_TO_EXECUTE(self, NO_OF_TASKS):
        return stdLogMsg["KEY_NO_OF_TASKS_TO_EXECUTE"] % NO_OF_TASKS

    # NUMBER OF TASKS EXECUTED - FUNCTION
    def STD_LOG_NO_OF_TASKS_EXECUTED(self, NO_OF_TASKS):
        return stdLogMsg["KEY_NO_OF_TASKS_EXECUTED"] % NO_OF_TASKS

    # EXECUTE ALL THE QUEUED TASKS - FUNCTION
    def STD_LOG_EXE_QUEUED_TASKS(self, NO_OF_TASKS):
        return stdLogMsg["KEY_EXE_QUEUED_TASKS"] % NO_OF_TASKS

    # ONLY ONE TASK IS FREE. EXECUTE MAXIMUM OF 30 TASKS TO QUEUE LATER - FUNCTION
    def STD_LOG_EXE_MAX_OF_30_TASKS(self, NO_OF_TASKS_TO_EXE):
        return stdLogMsg["KEY_EXE_MAX_OF_30_TASKS"] % NO_OF_TASKS_TO_EXE

    def STD_LOG_ITERATION_DONE_CHECK_STATUS_OF_TASKID(self, TaskIDInExecution):
        return stdLogMsg["KEY_ITERATION_DONE_CHECK_STATUS_OF_TASKID"] % TaskIDInExecution

    # CARD IS OUT OF BUSY IN ALL DISCARD TRY - FUNCTION
    def STD_LOG_CARD_OUT_OF_BUSY_IN_ALL_DISCARD_TRY(self, NO_OF_TIME_TRIED):
        return stdLogMsg["KEY_CARD_OUT_OF_BUSY_IN_ALL_DISCARD_TRY"] % NO_OF_TIME_TRIED

    # BLOCKS TO DISCARD - FUNCTION
    def STD_LOG_BLOCKS_TO_DISCARD(self, NO_OF_BLOCKS):
        return stdLogMsg["KEY_BLOCKS_TO_DISCARD"] % NO_OF_BLOCKS

    # DISCARD IN LOOP FOR BUSY - FUNCTION
    def STD_LOG_DISCARD_IN_LOOP_FOR_BUSY(self, Iteration):
        return self.STD_LOG_HEADER(print_string = stdLogMsg["KEY_DISCARD_ITERATION_FOR_BUSY"] % Iteration, special_character = "*", repeat = 10)

    # ABORT IN LOOP FOR BUSY - FUNCTION
    def STD_LOG_ABORT_IN_LOOP_FOR_BUSY(self, Iteration):
        return self.STD_LOG_HEADER(print_string = stdLogMsg["KEY_CMD43_ITERATION_FOR_BUSY"] % Iteration, special_character = "*", repeat = 10)

    def STD_LOG_CARD_SUPPORT_SPEC_VER_OF_CQ(self, Spec_version):
        return stdLogMsg["KEY_CARD_SUPPORT_SPEC_VER_OF_CQ"] % Spec_version

    def STD_LOG_CARD_NOT_SUPPORT_SPEC_VER_OF_CQ(self, Spec_version):
        return stdLogMsg["KEY_CARD_NOT_SUPPORT_SPEC_VER_OF_CQ"] % Spec_version

    def STD_LOG_CARD_STATE_AFTER_CMD38_IN_CQ(self, Card_State):
        return stdLogMsg["KEY_CARD_STATE_AFTER_CMD38_IN_CQ"] % Card_State

    def STD_LOG_EXT_REG_PER_FUNC_WRITE_RESERVED_FIELD(self, Offset, Value):
        return stdLogMsg["KEY_EXT_REG_PER_FUNC_WRITE_RESERVED_FIELD"] % (Offset, Value)

    def STD_LOG_EXT_REG_MASK_WRITE(self, Address, Mask, Data):
        return stdLogMsg["KEY_EXT_REG_MASK_WRITE"] % (Address, Mask, Data)

    def STD_LOG_EXT_REG_MASK_WRITE_PASSED(self, Data, Address):
        return stdLogMsg["KEY_EXT_REG_MASK_WRITE_PASSED"] % (Data, Address)

    def STD_LOG_EXT_REG_MASK_WRITE_FAILED(self, Data, Address):
        return stdLogMsg["KEY_EXT_REG_MASK_WRITE_FAILED"] % (Data, Address)

    def STD_LOG_EXT_REG_ORIGINAL_VALUE_RETAINED_WITH_MASK_0(self, Data, Address):
        return stdLogMsg["KEY_EXT_REG_ORIGINAL_VALUE_RETAINED_WITH_MASK_0"] % (Data, Address)

    def STD_LOG_EXT_REG_ORIGINAL_VALUE_UPDATED_WITH_MASK_0(self, UpdatedData, OriginalData, Address):
        return stdLogMsg["KEY_EXT_REG_ORIGINAL_VALUE_UPDATED_WITH_MASK_0"] % (UpdatedData, OriginalData, Address)

    def STD_LOG_CMD_NOT_SUPPORTED_IN_SDR_FW_LOOPBACK(self, CMD):
        return stdLogMsg["KEY_CMD_NOT_SUPPORTED_IN_SDR_FW_LOOPBACK"] % CMD

    def STD_LOG_CMD12_AFTER_QUEUE_TASK(self, TaskID):
        return stdLogMsg["KEY_CMD12_AFTER_QUEUE_TASK"] % TaskID

    def STD_LOG_CMD12_AFTER_DATA_TRANSFER_OF_TASK(self, TaskID):
        return stdLogMsg["KEY_CMD12_AFTER_DATA_TRANSFER_OF_TASK"] % TaskID

    def STD_LOG_TOTAL_BLOCKS_NO_OF_REGION_REGION_SIZE(self, TotalBlocks, No_of_Regions, Region_Size):
        return stdLogMsg["KEY_TOTAL_BLOCKS_NO_OF_REGION_REGION_SIZE"] % (TotalBlocks, No_of_Regions, Region_Size)

    def STD_LOG_START_ADDR_AND_PATTERN_OF_EACH_REGION(self, StartAddrListOfEachRegion, PatternListOfEachRegion):
        return stdLogMsg["KEY_START_ADDR_AND_PATTERN_OF_EACH_REGION"] % (StartAddrListOfEachRegion, PatternListOfEachRegion)

    def STD_LOG_REGION_SIZE_OF_EACH_REGION(self, RegionSizeListOfEachRegion):
        return stdLogMsg["KEY_REGION_SIZE_OF_EACH_REGION"] % RegionSizeListOfEachRegion

    def STD_LOG_REGION_LIST(self, RegionList):
        return stdLogMsg["KEY_REGION_LIST"] % RegionList

    def STD_LOG_REGION_SHUFFLED_LIST(self, RegionList):
        return stdLogMsg["KEY_REGION_SHUFFLED_LIST"] % RegionList

    def STD_LOG_WRITE_REGION_IN_CQMODE(self, Region):
        return stdLogMsg["KEY_WRITE_REGION_IN_CQMODE"] % Region

    def STD_LOG_WRITE_REGION_IN_LEGACY(self, Region):
        return stdLogMsg["KEY_WRITE_REGION_IN_LEGACY"] % Region

    def STD_LOG_READ_REGION_IN_CQMODE(self, Region):
        return stdLogMsg["KEY_READ_REGION_IN_CQMODE"] % Region

    def STD_LOG_READ_REGION_IN_LEGACY(self, Region):
        return stdLogMsg["KEY_READ_REGION_IN_LEGACY"] % Region

    def STD_LOG_WRITE_REGION_FINISHED(self, Region):
        return stdLogMsg["KEY_WRITE_REGION_FINISHED"] % Region

    def STD_LOG_READ_REGION_FINISHED(self, Region):
        return stdLogMsg["KEY_READ_REGION_FINISHED"] % Region

    def STD_LOG_ABORT_AT_BIT_POSITION(self, BitPositionInBlock):
        return stdLogMsg["KEY_ABORT_AT_BIT_POSITION"] % BitPositionInBlock

    def STD_LOG_ABORT_AT_NRC(self, AbortNRCValue):
        return stdLogMsg["KEY_ABORT_AT_NRC"] % AbortNRCValue

    def STD_LOG_ABORT_AT_BUSY_TIME_OUT(self, AbortBusy):
        return stdLogMsg["KEY_ABORT_AT_BUSY_TIME_OUT"] % AbortBusy

    def STD_LOG_ABORT_AT_BUSY_TIME(self, AbortBusy):
        return stdLogMsg["KEY_ABORT_AT_BUSY_TIME"] % AbortBusy

    def STD_LOG_WRITE_DATA_BUFF_FROM_ABORT_BLOCK(self, AbortBlock, BlockNumber, First8Bytes):
        return stdLogMsg["KEY_WRITE_DATA_BUFF_FROM_ABORT_BLOCK"] % (AbortBlock, BlockNumber, First8Bytes)

    def STD_LOG_1ST_8_BYTES_OF_A_BLOCK(self, BlockNumber, First8Bytes):
        return stdLogMsg["KEY_1ST_8_BYTES_OF_A_BLOCK"] % (BlockNumber, First8Bytes)

    def STD_LOG_TEST_STOP_TRANS_WITH_OPTION(self, CMD, Stop_Transmission_Option):
        return stdLogMsg["KEY_TEST_STOP_TRANS_WITH_OPTION"] % (CMD, Stop_Transmission_Option)

    def STD_LOG_TEST_POWER_ABORT_WITH_OPTION(self, CMD, Power_Abort_Option):
        return stdLogMsg["KEY_TEST_POWER_ABORT_WITH_OPTION"] % (CMD, Power_Abort_Option)

    def STD_LOG_TEST_CMD0_ABORT_WITH_OPTION(self, CMD, CMD0_Abort_Option):
        return stdLogMsg["KEY_TEST_CMD0_ABORT_WITH_OPTION"] % (CMD, CMD0_Abort_Option)

    def STD_LOG_TEST_ABORT_IN_LEGACY(self, CMD, Function):
        return self.STD_LOG_HEADER(stdLogMsg["KEY_TEST_ABORT_IN_LEGACY"] % (CMD, Function), special_character = "*", repeat = 10)

    def STD_LOG_TEST_ABORT_IN_CQ(self, CMD, Function):
        return self.STD_LOG_HEADER(stdLogMsg["KEY_TEST_ABORT_IN_CQ"] % (CMD, Function), special_character = "*", repeat = 10)

    def STD_LOG_MISMATCH_OCCURED_BLOCK(self, BlockNumber, Data):
        return stdLogMsg["KEY_MISMATCH_OCCURED_BLOCK"] % (BlockNumber, Data)

    def STD_LOG_CMD13_AFTER_ABORT_CMD(self, CMDForAbort):
        return stdLogMsg["KEY_CMD13_AFTER_ABORT_CMD"] % CMDForAbort

    def STD_LOG_DATA_TRANS_MODE(self, CQ_or_Legacy):
        return stdLogMsg["KEY_DATA_TRANS_MODE"] % CQ_or_Legacy

    def STD_LOG_TASK_REQUEUE(self, TaskID):
        return stdLogMsg["KEY_TASK_REQUEUE"] % TaskID

    def STD_LOG_TASK_QUEUE_WITH_0_BLOCK(self, TaskID):
        return stdLogMsg["KEY_TASK_QUEUE_WITH_0_BLOCK"] % TaskID

    def STD_LOG_VALIDATE_ERROR_FOR_TASK_ID(self, TaskID):
        return stdLogMsg["KEY_VALIDATE_ERROR_FOR_TASK_ID"] % TaskID

    def STD_LOG_ABORT_INVALID_TASK(self, TaskID):
        return stdLogMsg["KEY_ABORT_INVALID_TASK"] % TaskID

    def STD_LOG_ABORT_WITH_INVALID_OPCODE(self, InvalidOpcode):
        return stdLogMsg["KEY_ABORT_WITH_INVALID_OPCODE"] % InvalidOpcode

    def STD_LOG_ABORT_N_TASKS(self, No_of_Tasks):
        return stdLogMsg["KEY_ABORT_N_TASKS"] % No_of_Tasks

    def STD_LOG_NO_OF_TASKS_TO_EXE_WITH_INVALID_TASK_ID(self, TaskID):
        return stdLogMsg["KEY_NO_OF_TASKS_TO_EXE_WITH_INVALID_TASK_ID"] % TaskID

    def STD_LOG_MISCOMPARE_PATTERN_AND_ACTUAL_PATTERN(self, AutualPattern, MiscomparePattern, TaskID):
        return stdLogMsg["KEY_MISCOMPARE_PATTERN_AND_ACTUAL_PATTERN"] % (AutualPattern, MiscomparePattern, TaskID)

    def STD_LOG_CMD49_FOR_FUNC_OFFSET_VALUE(self, Function, Offset, Value):
        return stdLogMsg["KEY_CMD49_FOR_FUNC_OFFSET_VALUE"] % (Function, Offset, Value)

    def STD_LOG_CMD49_WRITE_UPDATED_FOR_FUNC_OFFSET_VALUE(self, Function, Offset, Value):
        return stdLogMsg["KEY_CMD49_WRITE_UPDATED_FOR_FUNC_OFFSET_VALUE"] % (Function, Offset, Value)

    def STD_LOG_EXT_REG_FUN_WRITE_VALUE_UPDATED_UNEXPECTEDLY(self, Value, Offset, Function):
        return stdLogMsg["KEY_EXT_REG_FUN_WRITE_VALUE_UPDATED_UNEXPECTEDLY"] % (Value, Offset, Function)

    def STD_LOG_EXT_REG_FUN_NOT_UPDATED_AS_EXPECTEDLY(self, Value, Offset, Function):
        return stdLogMsg["KEY_EXT_REG_FUN_NOT_UPDATED_AS_EXPECTEDLY"] % (Value, Offset, Function)

    def STD_LOG_CQ_CMDS_EXECUTED_IN_LEGACY(self, CMDList):
        return stdLogMsg["KEY_CQ_CMDS_EXECUTED_IN_LEGACY"] % CMDList

    def STD_LOG_CMD_FOR_OUT_OF_RANGE_ADDRESS(self, CMDList):
        return stdLogMsg["KEY_CMD_FOR_OUT_OF_RANGE_ADDR"] % CMDList

    def STD_LOG_BUSY_TIMEOUT_RCVD_AT_COUNT(self, Count):
        return stdLogMsg["KEY_BUSY_TIMEOUT_RCVD_AT_COUNT"] % Count

    def STD_LOG_BUSY_TIMEOUT_OCCURED(self, Operation):
        return stdLogMsg["KEY_BUSY_TIMEOUT_OCCURED"] % Operation

    def STD_LOG_CMD48_READ_1_BYTE_AT_OFFSET(self, Offset, Function):
        return stdLogMsg["KEY_CMD48_READ_1_BYTE_AT_OFFSET"] % (Offset, Function)

    def STD_LOG_CMD48_READ_VALUE_AT_PAGE_OFFSET(self, Value, Page, Offset):
        return stdLogMsg["KEY_CMD48_READ_VALUE_AT_PAGE_OFFSET"] % (Value, Page, Offset)

    def STD_LOG_CMD49_WRITE_AT_PAGE_OFFSET_WITH_VALUE(self, Page, Offset, Value):
        return stdLogMsg["KEY_CMD49_WRITE_AT_PAGE_OFFSET_WITH_VALUE"] % (Page, Offset, Value)

    def STD_LOG_CMD49_WRITTERN_VALUE_AT_PAGE_OFFSET(self, Value, Page, Offset):
        return stdLogMsg["KEY_CMD49_WRITTERN_VALUE_AT_PAGE_OFFSET"] % (Value, Page, Offset)

    def STD_LOG_EXT_REG_RANDOM_PAGE(self, Page, Function):
        return stdLogMsg["KEY_EXT_REG_RANDOM_PAGE"] % (Page, Function)

    def STD_LOG_WRITE_IN_NOT_IMPLEMENTED_EXT_REG_FUNC(self, FunctionNumber):
        return stdLogMsg["KEY_WRITE_IN_NOT_IMPLEMENTED_EXT_REG_FUNC"] % FunctionNumber

    def STD_LOG_EXT_REG_WRITE_FAILED_FOR_FUNC(self, FunctionNumber):
        return stdLogMsg["KEY_EXT_REG_WRITE_FAILED_FOR_FUNC"] % FunctionNumber

    def STD_LOG_EXT_REG_WRITE_PASSED_FOR_FUNC(self, FunctionNumber):
        return stdLogMsg["KEY_EXT_REG_WRITE_PASSED_FOR_FUNC"] % FunctionNumber

    def STD_LOG_READ_IN_NOT_IMPLEMENTED_EXT_REG_FUNC(self, FunctionNumber):
        return stdLogMsg["KEY_READ_IN_NOT_IMPLEMENTED_EXT_REG_FUNC"] % FunctionNumber

    def STD_LOG_EXT_REG_READ_FAILED_FOR_FUNC(self, FunctionNumber):
        return stdLogMsg["KEY_EXT_REG_READ_FAILED_FOR_FUNC"] % FunctionNumber

    def STD_LOG_EXT_REG_READ_PASSED_FOR_FUNC(self, FunctionNumber):
        return stdLogMsg["KEY_EXT_REG_READ_PASSED_FOR_FUNC"] % FunctionNumber

    def STD_LOG_EXE_REMAINING_TASKS(self, No_of_Tasks):
        return stdLogMsg["KEY_EXE_REMAINING_TASKS"] % No_of_Tasks

    def STD_LOG_PER_FUNC_WRITE_READ_MATCH_AFTER_STRESS_CMD49(self, StressLoopCount):
        return stdLogMsg["KEY_PER_FUNC_WRITE_READ_MATCH_AFTER_STRESS_CMD49"] % StressLoopCount

    def STD_LOG_POSTION_FOR_CONTIGUOUS_WRITE_OR_READ(self, No_of_Tasks):
        return stdLogMsg["KEY_POSTION_FOR_CONTIGUOUS_WRITE_OR_READ"] % No_of_Tasks

    def STD_LOG_TEST_INTENSIVE_CASE(self, DataDirection):
        return stdLogMsg["KEY_TEST_INTENSIVE_CASE"] % DataDirection

    def STD_LOG_TASKID_LIST_TO_CHANGE_DIRECTION(self, TaskIDList):
        return stdLogMsg["KEY_TASKID_LIST_TO_CHANGE_DIRECTION"] % TaskIDList

    def STD_LOG_DIRECTION_LIST(self, DirectionList):
        return stdLogMsg["KEY_DIRECTION_LIST"] % DirectionList

    def STD_LOG_CSV_FAIL_CARD_NOT_IN_CQ_TRAN(self, Filename, CMD13responseList):
        return stdLogMsg["KEY_CSV_FAIL_CARD_NOT_IN_CQ_TRAN"] % (Filename, CMD13responseList)

    def STD_LOG_PARSE_CSV_FILE(self, Filename):
        return stdLogMsg["KEY_PARSE_CSV_FILE"] % Filename

    def STD_LOG_QUEUE_NEG_AT_ROW(self, Direction, RowNo):
        return stdLogMsg["KEY_QUEUE_NEG_AT_ROW"] % (Direction, RowNo)

    def STD_LOG_ROWS_IN_CSV_EXCLUDE_HEAD(self, No_of_Rows):
        return stdLogMsg["KEY_ROWS_IN_CSV_EXCLUDE_HEAD"] % No_of_Rows

    def STD_LOG_ROWS_MANIPULATED_IN_CSV(self, No_of_Rows):
        return stdLogMsg["KEY_ROWS_MANIPULATED_IN_CSV"] % No_of_Rows

    def STD_LOG_TIME_TO_PARSE_FILE_AND_CREATE_BATCH(self, Time):
        return stdLogMsg["KEY_TIME_TO_PARSE_FILE_AND_CREATE_BATCH"] % Time

    def STD_LOG_NO_OF_VALID_ENTRIES_IN_CSV(self, Filename, No_of_Valid_Entries):
        return stdLogMsg["KEY_NO_OF_VALID_ENTRIES_IN_CSV"] % (Filename, No_of_Valid_Entries)

    def STD_LOG_NO_OF_BATCH_TO_CREATE(self, BatchCount):
        return stdLogMsg["KEY_NO_OF_BATCH_TO_CREATE"] % BatchCount

    def STD_LOG_SUBMIT_BATCH(self, BatchNumber):
        return stdLogMsg["KEY_SUBMIT_BATCH"] % BatchNumber

    def STD_LOG_CSV_FILE_FAILED(self, Filename, Exception):
        return stdLogMsg["KEY_CSV_FILE_FAILED"] % (Filename, Exception)

    def STD_LOG_COMPLETED_BATCHES(self, BatchCount):
        return stdLogMsg["KEY_COMPLETED_BATCHES"] % BatchCount

    def STD_LOG_COMPLETED_BATCHES_IN_CSV(self, BatchCount, Filename):
        return stdLogMsg["KEY_COMPLETED_BATCHES_IN_CSV"] % (BatchCount, Filename)

    def STD_LOG_NO_OF_TIMES_CMD(self, CMD, No_of_Times):
        return stdLogMsg["KEY_NO_OF_TIMES_CMD"] % (CMD, No_of_Times)

    def STD_LOG_A2_PERF_STATUS(self, Status):
        return stdLogMsg["KEY_A2_PERF_STATUS"] % (Status, "{0:b}".format(Status))

    def STD_LOG_RPTU_START_ADDR(self, StartLBA):
        return stdLogMsg["KEY_RPTU_START_ADDR"] % StartLBA

    def STD_LOG_CLASS2_RANDOM_PERF_MEASURE(self, DataDirection, SpeedMode):
        return self.STD_LOG_HEADER(stdLogMsg["KEY_CLASS2_RANDOM_PERF_MEASURE"] % (DataDirection, SpeedMode), "*", 10)

    def STD_LOG_CLASS2_SEQ_PERF_MEASURE(self, DataDirection, SpeedMode):
        return self.STD_LOG_HEADER(stdLogMsg["KEY_CLASS2_SEQ_PERF_MEASURE"] % (DataDirection, SpeedMode), "*", 10)

    def STD_LOG_PERF_MEASURE_API_PATTERN(self, Pattern):
        return stdLogMsg["KEY_PERF_MEASURE_API_PATTERN"] % Pattern

    def STD_LOG_NO_OF_WRITE_IN_PERF_MEASURE_TEST(self, Time, WriteCount):
        return stdLogMsg["KEY_NO_OF_WRITE_IN_PERF_MEASURE_TEST"] % (Time, WriteCount)

    def STD_LOG_NO_OF_READ_IN_PERF_MEASURE_TEST(self, Time, ReadCount):
        return stdLogMsg["KEY_NO_OF_READ_IN_PERF_MEASURE_TEST"] % (Time, ReadCount)

    def STD_LOG_TIME_TAKEN_FOR_EXE(self, Time):
        return stdLogMsg["KEY_TIME_TAKEN_FOR_EXE"] % Time

    def STD_LOG_RANDOM_IOPS_FOR_SIZE_4K(self, DataDirection, IOPS, SpeedMode = None):
        return stdLogMsg["KEY_RANDOM_IOPS_FOR_SIZE_4K"] % ((("%s Mode - " % SpeedMode) if SpeedMode != None else ""), DataDirection, IOPS)

    def STD_LOG_SEQ_WRITE_1GB_TIME(self, Time):
        return stdLogMsg["KEY_SEQ_WRITE_1GB_TIME"] % Time

    def STD_LOG_WRITE_N_BLOCKS_OF_CARD(self, No_of_GB_or_Percentage, TotalBlocksToWrite):
        return stdLogMsg["KEY_WRITE_N_BLOCKS_OF_CARD"] % (No_of_GB_or_Percentage, TotalBlocksToWrite)

    def STD_LOG_WRITE_DATA_IN_RPTU(self, TotalBlocksToWrite):
        return stdLogMsg["KEY_WRITE_DATA_IN_RPTU"] % TotalBlocksToWrite

    def STD_LOG_WRITE_WHOLE_CARD(self, TotalBlocksToWrite):
        return stdLogMsg["KEY_WRITE_WHOLE_CARD"] % TotalBlocksToWrite

    def STD_LOG_START_LBA_OF_1GB_REGION(self, StartLBA):
        return stdLogMsg["KEY_START_LBA_OF_1GB_REGION"] % StartLBA

    def STD_LOG_ENABLE_CQ_AFTER_TEST_WP_VIOLATION(self, CQMode):
        return stdLogMsg["KEY_ENABLE_CQ_AFTER_TEST_WP_VIOLATION"] % CQMode

    def STD_LOG_CMD_DURING_DATA_TRANS(self, CMD):
        return stdLogMsg["KEY_CMD_DURING_DATA_TRANS"] % CMD
    #################### CQ - ENDS ####################

    #################### WRITE/READ - BEGINS ####################
    # SINGLE_BLOCK_WRITE - FUNCTION
    def STD_LOG_SINGLE_BLOCK_WRITE(self, startLBA, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_SINGLE_BLOCK_WRITE"] % (startLBA), optDbgMsg)

    # MULTI_BLOCK_WRITE - FUNCTION
    def STD_LOG_MULTI_BLOCK_WRITE(self, startLBA, blockCount, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_MULTI_BLOCK_WRITE"] % (startLBA, blockCount), optDbgMsg)

    # SINGLE_BLOCK_READ - FUNCTION
    def STD_LOG_SINGLE_BLOCK_READ(self, startLBA, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_SINGLE_BLOCK_READ"] % (startLBA), optDbgMsg)

    # MULTI_BLOCK_READ - FUNCTION
    def STD_LOG_MULTI_BLOCK_READ(self, startLBA, blockCount, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_MULTI_BLOCK_READ"] % (startLBA, blockCount), optDbgMsg)

    #SINGLE_BLOCK_WRITE_WITH_PATTERN - FUNCTION
    def STD_LOG_SINGLE_BLOCK_WRITE_WITH_PATTERN(self, startLBA, pattern, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_SINGLE_BLOCK_WRITE_WITH_PATTERN"] % (startLBA, pattern), optDbgMsg)

    #MULTI_BLOCK_WRITE_WITH_PATTERN - FUNCTION
    def STD_LOG_MULTI_BLOCK_WRITE_WITH_PATTERN(self, startLBA, blockCount, pattern, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_MULTI_BLOCK_WRITE_WITH_PATTERN"] % (startLBA, blockCount, pattern), optDbgMsg)

    #SINGLE_BLOCK_READ_WITH_PATTERN - FUNCTION
    def STD_LOG_SINGLE_BLOCK_READ_WITH_PATTERN(self, startLBA, pattern, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_SINGLE_BLOCK_READ_WITH_PATTERN"] % (startLBA, pattern), optDbgMsg)

    #MULTI_BLOCK_READ_WITH_PATTERN - FUNCTION
    def STD_LOG_MULTI_BLOCK_READ_WITH_PATTERN(self, startLBA, blockCount, pattern, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_MULTI_BLOCK_READ_WITH_PATTERN"] % (startLBA, blockCount, pattern), optDbgMsg)

    # WRITE OR READ ABORT AFTER N BLOCKS - FUNCTION
    def STD_LOG_SEND_WRITE_OR_READ_CMD_ABORT_AFTER_N_BLOCKS(self, CMDForAbort, NumBlocksForAbort):
        return stdLogMsg["KEY_SEND_WRITE_OR_READ_CMD_ABORT_AFTER_N_BLOCKS"] % (CMDForAbort, NumBlocksForAbort)

    # PRINT THE READ BUFFER AS STRING - FUNCTION
    def STD_LOG_BUFFER_STRING(self, BlksToPrint):
        return stdLogMsg["KEY_BUFFER_STRING"] % (BlksToPrint)

    def STD_LOG_READ_AFTER_POWER_OFF_ABORT_FAILED(self, ErrorCode):
        return stdLogMsg["KEY_READ_AFTER_POWER_OFF_ABORT_FAILED"] % ErrorCode

    def STD_LOG_READ_AFTER_CMD0_ABORT_FAILED(self, ErrorCode):
        return stdLogMsg["KEY_READ_AFTER_CMD0_ABORT_FAILED"] % ErrorCode
    #################### WRITE/READ - ENDS ####################

    #################### ERASE - BEGINS ####################
    # ERASE - FUNCTION
    def STD_LOG_ERASE(self, startLBA, endLBA, eraseFunction, timeOut = None, optDbgMsg = ""):
        logMessage = stdLogMsg["KEY_ERASE"] if timeOut == None else stdLogMsg["KEY_ERASE_WITH_TIMEOUT"]
        return self.STD_LOG_APPEND_OPTIONAL_MSG(logMessage%(startLBA, endLBA, eraseFunction), optDbgMsg)

    # ERASE N BLOCKS WITH ONE OF ERASE FUNCTIONS - FUNCTION
    def STD_LOG_ERASE_N_BLOCKS_WITH_FUNC(self, No_of_Blocks, EraseFunction):
        return stdLogMsg["KEY_ERASE_N_BLOCKS_WITH_FUNC"] % (No_of_Blocks, EraseFunction)

    # SEND COMMAND DURING CMD12 BUSY PERIOD - FUNCTION
    def STD_LOG_CMD_DURING_CMD12_BUSY(self, FuncForAbort):
        return stdLogMsg["KEY_CMD_DURING_CMD12_BUSY"] % (("CMD%d" % FuncForAbort) if (type(FuncForAbort) == int) else FuncForAbort)

    # SEND COMMAND DURING CMD38 BUSY PERIOD - FUNCTION
    def STD_LOG_CMD_DURING_CMD38_BUSY(self, FuncForAbort):
        return stdLogMsg["KEY_CMD_DURING_CMD38_BUSY"] % (("CMD%d" % FuncForAbort) if (type(FuncForAbort) == int) else FuncForAbort)

    # ERASED DATA - FUNCTION
    def STD_LOG_ERASED_DATA(self, CMD38Operation, Data):
        return stdLogMsg["KEY_ERASED_DATA"] % (Data, CMD38Operation)

    # PRINT THE READ DATA AFTER ERASE - FUNCTION
    def STD_LOG_READ_DATA_AFTER_ERASE(self, No_of_blks_to_print):
        return stdLogMsg["KEY_READ_DATA_AFTER_ERASE"] % No_of_blks_to_print

    # READ ERASED DATA AFTER OPERATION - FUNCTION
    def STD_LOG_READ_ERASED_DATA_AFTER_FUNC(self, FuncForAbort):
        return stdLogMsg["KEY_READ_ERASED_DATA_AFTER_FUNC"] % (("CMD%d" % FuncForAbort) if (type(FuncForAbort) == int) else FuncForAbort)

    # COMPARE READ DATA AFTER ERASE - FUNCTION
    def STD_LOG_COMPARE_READ_DATA_AFTER_ERASE(self, EraseOption):
        return stdLogMsg["KEY_COMPARE_READ_DATA_AFTER_ERASE"] % EraseOption

    def STD_LOG_ERASE_CMD_FOR_OUT_OF_SEQ(self, CMD):
        return stdLogMsg["KEY_ERASE_CMD_FOR_OUT_OF_SEQ"] % CMD
    #################### ERASE - ENDS ####################

    #################### SECURE - BEGINS ####################
    # READ_MKB_FILE - FUNCTION
    def STD_LOG_READ_MKB_FILE(self, cardSlot, startLBA, blockCount, selector, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_LOG_READ_MKB_FILE"] % (cardSlot, startLBA, blockCount, selector), optDbgMsg)

    # WRITE_MKB_FILE - FUNCTION
    def STD_LOG_WRITE_MKB_FILE(self, selector, MKBFileorPath, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_LOG_WRITE_MKB_FILE"] % (selector, MKBFileorPath), optDbgMsg)

    # SECURE_READ - FUNCTION
    def STD_LOG_SECURE_READ(self, cardSlot, startLBA, blockCount, selector, authenticate, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_SECURE_READ"] % (cardSlot, startLBA, blockCount, selector, authenticate), optDbgMsg)

    # SECURE_WRITE - FUNCTION
    def STD_LOG_SECURE_WRITE(self, cardSlot, startLBA, blockCount, selector, authenticate, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_SECURE_WRITE"] % (cardSlot, startLBA, blockCount, selector, authenticate), optDbgMsg)

    # PROTECTED_AREA_SIZE - FUNCTION
    def STD_LOG_PROTECTED_AREA_SIZE(self, capacity, Size, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_PROTECTED_AREA_SIZE"] % (capacity, Size), optDbgMsg)

    # CARD_TO_SECURE_MODE - FUNCTION
    def STD_LOG_CARD_TO_SECURE_MODE(self, startLBA, blockCount, selector, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_CARD_TO_SECURE_MODE"] % (startLBA, blockCount, selector), optDbgMsg)

    # CHANGE_SECURE_AREA - FUNCTION
    def STD_LOG_CHANGE_SECURE_AREA(self, cardSlot, startLBA, blockCount, selector, authenticate, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_CHANGE_SECURE_AREA"] % (cardSlot, startLBA, blockCount, selector, authenticate), optDbgMsg)

    # CHANGE_SECURE_AREA - FUNCTION
    def STD_LOG_CHANGE_SECURE_AREA(self, cardSlot, startLBA, blockCount, selector, authenticate, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_CHANGE_SECURE_AREA"] % (cardSlot, startLBA, blockCount, selector, authenticate), optDbgMsg)
    #################### SECURE - ENDS ####################

    #################### CARD LOCK/UNLOCK - BEGINS ####################
    # CARD_LOCK_UNLOCK - FUNCTION
    def STD_LOG_CARD_LOCK_UNLOCK(self, setPassword, clearPassword, lock, erase, cop, additionalPassLen, oldPassword, newPassword, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_STD_LOG_CARD_LOCK_UNLOCK"] % (setPassword, clearPassword, lock, erase, cop, additionalPassLen, oldPassword, newPassword), optDbgMsg)

    # SET_NEW_PASSWORD_LOCK_CARD - FUNCTION
    # def STD_LOG_SET_NEW_PASSWORD_LOCK_CARD(self, password, optDbgMsg = ""):
    #     return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_SET_NEW_PASSWORD_LOCK_CARD"] % (password), optDbgMsg)

    # CLEAR_PASSWORD - FUNCTION
    # def STD_LOG_CLEAR_PASSWORD(self, password, optDbgMsg = ""):
    #     return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_CLEAR_PASSWORD"] % (password), optDbgMsg)
    #################### CARD LOCK/UNLOCK - ENDS ####################

    #################### WRITE PROTECTION - BEGINS ####################
    # GET_WRITE_PROTECTED_BLOCK - FUNCTION
    def STD_LOG_GET_WRITE_PROTECTED_BLOCK(self, startLBA, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_GET_WRITE_PROTECTED_BLOCK"] % (startLBA), optDbgMsg)

    # SET_WRITE_PROTECTED_BLOCK - FUNCTION
    def STD_LOG_SET_WRITE_PROTECTED_BLOCK(self, startLBA, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_SET_WRITE_PROTECTED_BLOCK"] % (startLBA), optDbgMsg)
    #################### WRITE PROTECTION - ENDS ####################

    #################### VIDEO SPEED CLASS - BEGINS ####################
    # SPEED_CLASS - FUNCTION
    def STD_LOG_SPEED_CLASS(self, speedClass, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_SPEED_CLASS"] % (speedClass), optDbgMsg)

    # RU_READ_PERFORMANCE - FUNCTION
    def STD_LOG_RU_READ_PERFORMANCE(self, performance, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_RU_READ_PERFORMANCE"] % (performance), optDbgMsg)

    # RU_WRITE_PERFORMANCE - FUNCTION
    def STD_LOG_RU_WRITE_PERFORMANCE(self, performance, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_RU_WRITE_PERFORMANCE"] % (performance), optDbgMsg)

    # SU_READ_PERFORMANCE - FUNCTION
    def STD_LOG_SU_READ_PERFORMANCE(self, performance, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_SU_READ_PERFORMANCE"] % (performance), optDbgMsg)

    # SU_WRITE_PERFORMANCE - FUNCTION
    def STD_LOG_SU_WRITE_PERFORMANCE(self, performance, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_SU_WRITE_PERFORMANCE"] % (performance), optDbgMsg)

    # RECORDING_UNIT - FUNCTION
    def STD_LOG_RECORDING_UNIT(self, startLBA, blockCount, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_RECORDING_UNIT"] % (startLBA, blockCount), optDbgMsg)

    # SUB_UNIT - FUNCTION
    def STD_LOG_SUB_UNIT(self, startLBA, blockCount, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_SUB_UNIT"] % (startLBA, blockCount), optDbgMsg)

    # ALLOCATION_UNIT - FUNCTION
    def STD_LOG_ALLOCATION_UNIT(self, startLBA, blockCount, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_ALLOCATION_UNIT"] % (startLBA, blockCount), optDbgMsg)
    #################### VIDEO SPEED CLASS - ENDS ####################

    #################### OTHERS - BEGINS ####################
    # GET_BUS_WIDTH - FUNCTION
    def STD_LOG_GET_BUS_WIDTH(self, busWidth, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_GET_BUS_WIDTH"] % (busWidth), optDbgMsg)

    # SET_BUS_WIDTH - FUNCTION
    def STD_LOG_SET_BUS_WIDTH(self, busWidth, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_GET_BUS_WIDTH"] % (busWidth), optDbgMsg)

    # SET_HOST_FREQUENCY_KHZ - FUNCTION
    def STD_LOG_SET_HOST_FREQUENCY_KHZ(self, hostFreq, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_SET_HOST_FREQUENCY_KHZ"] % (hostFreq), optDbgMsg)

    # SET_HOST_FREQUENCY_MHZ - FUNCTION
    # def STD_LOG_SET_HOST_FREQUENCY_MHZ(self, hostFreq, optDbgMsg = ""):
    #     return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_SET_HOST_FREQUENCY_MHZ"] % (hostFreq), optDbgMsg)

    # SET_SPEED_MODE - FUNCTION
    def STD_LOG_SET_SPEED_MODE(self, speedMode, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_SET_SPEED_MODE"] % (speedMode), optDbgMsg)

    # SET_VOLTAGE - FUNCTION
    def STD_LOG_SET_VOLTAGE(self, voltage, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_SET_VOLTAGE"] % (voltage), optDbgMsg)

    # CMD_FAILED_WITH_EXCEPTION - FUNCTION
    # def STD_LOG_CMD_FAILED_WITH_EXCEPTION(self, CMD, optDbgMsg = ""):
    #     return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_CMD_FAILED_WITH_EXCEPTION"] % (CMD), optDbgMsg)

    # # GET_CARD_CAPACITY - FUNCTION
    # def STD_LOG_CARD_CAPACITY(self, cardCapacity, optDbgMsg = ""):
    #     return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_GET_CARD_CAPACITY"] % (cardCapacity), optDbgMsg)

    # GET_CARD_MAX_LBA - FUNCTION
    def STD_LOG_CARD_MAX_LBA(self, maxLBA, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_GET_CARD_MAX_LBA"] % (maxLBA), optDbgMsg)

    # FAT - FUNCTION
    def STD_LOG_FAT(self, startLBA, blockCount, selector, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_FAT"] % (startLBA, blockCount, selector), optDbgMsg)

    # FAT2 - FUNCTION
    def STD_LOG_FAT2(self, startLBA, blockCount, selector, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_FAT2"] % (startLBA, blockCount, selector), optDbgMsg)

    # FAT_BITMAP - FUNCTION
    def STD_LOG_FAT_BITMAP(self, startLBA, blockCount, selector, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_FAT_BITMAP"] % (startLBA, blockCount, selector), optDbgMsg)

    # FAT_USER_AREA - FUNCTION
    def STD_LOG_FAT_USER_AREA(self, startLBA, blockCount, selector, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_FAT_USER_AREA"] % (startLBA, blockCount, selector), optDbgMsg)

    # CARD_STATE - FUNCTION
    def STD_LOG_CARD_STATE(self, state, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_CARD_STATE"] % (state), optDbgMsg)

    # CARD_CAPACITY - FUNCTION
    def STD_LOG_CARD_CAPACITY(self, capacity, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_CARD_CAPACITY"] % (capacity), optDbgMsg)

    # CALL_FUNCTION - FUNCTION
    def STD_LOG_CALL_FUNCTION(self, function, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_CALL_FUNCTION"] % (function), optDbgMsg)

    # RANDOM_WRITE_IOPS - FUNCTION
    def STD_LOG_RANDOM_WRITE_IOPS(self, IOSize, IOPS, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_RANDOM_WRITE_IOPS"] % (IOSize, IOPS), optDbgMsg)

    # READ_IOPS - FUNCTION
    def STD_LOG_READ_IOPS(self, IOSize, IOPS, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_READ_IOPS"] % (IOSize, IOPS), optDbgMsg)

    # RUN_TEST_SCRIPT - FUNCTION
    def STD_LOG_RUN_TEST_SCRIPT(self, testScript, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_RUN_TEST_SCRIPT"] % (testScript), optDbgMsg)

    # META_PAGE_SIZE - FUNCTION
    def STD_LOG_META_PAGE_SIZE(self, Size, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_META_PAGE_SIZE"] % (Size), optDbgMsg)

    # META_BLOCK_SIZE - FUNCTION
    def STD_LOG_META_BLOCK_SIZE(self, Size, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_META_BLOCK_SIZE"] % (Size), optDbgMsg)

    # SEQUENTIAL_WRITE_PERFORMANCE - FUNCTION
    def STD_LOG_SEQUENTIAL_WRITE_PERFORMANCE(self, performance, speedMode, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_SEQUENTIAL_WRITE_PERFORMANCE"] % (performance, speedMode), optDbgMsg)

    # SEQUENTIAL_READ_PERFORMANCE - FUNCTION
    def STD_LOG_SEQUENTIAL_READ_PERFORMANCE(self, performance, speedMode, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_SEQUENTIAL_READ_PERFORMANCE"] % (performance, speedMode), optDbgMsg)

    # NON_SEQUENTIAL_WRITE_PERFORMANCE - FUNCTION
    def STD_LOG_NON_SEQUENTIAL_WRITE_PERFORMANCE(self, performance, speedMode, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_NON_SEQUENTIAL_WRITE_PERFORMANCE"] % (performance, speedMode), optDbgMsg)

    # NON_SEQUENTIAL_READ_PERFORMANCE - FUNCTION
    def STD_LOG_NON_SEQUENTIAL_READ_PERFORMANCE(self, performance, speedMode, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_NON_SEQUENTIAL_WRITE_PERFORMANCE"] % (performance, speedMode), optDbgMsg)

    # EXECUTION_FAILED_WITH_ERROR - FUNCTION
    def STD_LOG_EXECUTION_FAILED_WITH_ERROR(self, error, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_EXECUTION_FAILED_WITH_ERROR"] % (error), optDbgMsg)

    # TOTAL_NUMBER_OF_ERRORS - FUNCTION
    def STD_LOG_TOTAL_NUMBER_OF_ERRORS(self, noofErrors, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_TOTAL_NUMBER_OF_ERRORS"] % (noofErrors), optDbgMsg)

    # SD_SPEC_VERSION - FUNCTION
    def STD_LOG_SD_SPEC_VERSION(self, version, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_SD_SPEC_VERSION"] % (version,), optDbgMsg)

    # VOLTAGE_OUT_OF_RANGE - FUNCTION
    def STD_LOG_VOLTAGE_OUT_OF_RANGE(self, voltage, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_VOLTAGE_OUT_OF_RANGE"] % (voltage), optDbgMsg)

    # PERFORMANCE - FUNCTION
    def STD_LOG_PERFORMANCE(self, performance, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_PERFORMANCE"] % (performance), optDbgMsg)

    # NO_OF_ERRORS - FUNCTION
    def STD_LOG_CMD_NO_OF_ERRORS(self, noOfErrors, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_NO_OF_ERRORS"] % (noOfErrors), optDbgMsg)

    # CARD_TYPE - FUNCTION
    def STD_LOG_CARD_TYPE(self, Type, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_CARD_TYPE"] % (Type), optDbgMsg)

    # SEND_CMD_WITH_TASK_ID - FUNCTION
    # def STD_LOG_SEND_CMD_WITH_TASK_ID(self, CMD, task, optDbgMsg = ""):
    #     return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_KEY_SEND_CMD_WITH_TASK_ID"] % (CMD, task), optDbgMsg)
    #################### OTHERS - ENDS ####################

    # EXPECTED EXCEPTION
    def STD_LOG_EXPECTED_EXCEPTION(self, exp, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_EXPECTED_EXCEPTION_OCCURED"] % (exp), optDbgMsg)

    # EXPECTED EXCEPTION NOT OCCURED
    def STD_LOG_EXPECTED_EXCEPTION_NOT_OCCURED(self, exp, optDbgMsg = ""):
        return self.STD_LOG_APPEND_OPTIONAL_MSG(stdLogMsg["KEY_EXPECTED_EXCEPTION_NOT_OCCURED"] % (exp), optDbgMsg)


################### STANDARD_LOG_MESSAGE FUNCTION - ENDS ##############################

# Standard Log Format  Class - Ends
