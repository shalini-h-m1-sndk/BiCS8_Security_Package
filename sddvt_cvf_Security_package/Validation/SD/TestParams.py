"""
################################################################################
# Copyright (c) SanDisk Corp.2013 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# FILE:TestParams.py: Test file to define all Test Parameters.
#              AUTHOR: Ravi G
################################################################################

################################################################################
#                            CHANGE HISTORY
# 13-January-2015    RG  Initial Revision of TestParams.py
################################################################################
"""

PCIeState = {'Visibility':{0:'NOT VISIBLE', 1:'VISIBLE'}, 'Status':{0:'DISABLED', 1:'ENABLED'}, 'AccessProblem': {0: 'NO', 1:'YES'}, 'OSProblem':{0:'NO', 1:'YES'}}

#SCTP COMMAND
CDBLENGTH_16 = 16
IDENTIFYDRIVE = 0xEC
WRITEPORT = 0x8C
READPORT = 0x8D
READFILESYSTEM = 0x8A
WRITEFILESYSTEM = 0x8B
MEDIALAYOUT = 0xBB
FORMAT = 0x8F
FORMATSTATUS = 0x70

AUXSpace = 0x0004

#FILE ID
FILE_220 = 220
FW_CHUNK_SIZE = 4096

DWORD_SIZE = 4

#CTF Configuration Parameters.
CONFIGURATIONPARAMS = dict()
SERIALNRLENGTH = 20

#Status Code Types
SCT = {

    'GENERIC_COMMAND_STATUS'					:0x00,
    'COMMAND_SPECIFIC_STATUS'					:0x01,
    'MEDIA_AND_DATA_INTEGRITY_ERRORS'				:0x02,
    'VENDOR_SPECIFIC'    					:0x07,
}

#NVMe Command Status Codes.
SC = {

    'SUCCESSFUL_COMPLETION'					:0x00,
    'INVALID_COMMAND_OPCODE'					:0x01,
    'INVALID_FIELD'						:0x02,
    'COMMAND_ID_CONFLICT'					:0x03,
    'DATA_TRANSFER_ERROR'					:0x04,
    'COMMANDS_ABORTED_DUE_TO_POWER_LOSS_NOTIFICATION'	        :0x05,
    'INTERNAL_ERROR'						:0x06,
    'COMMAND_ABORT_REQUESTED'					:0x07,
    'COMMAND_ABORTED_SQ_DELETION'				:0x08,
    'COMMAND_ABORTED_FAILED_FUSE_COMMAND'			:0x09,
    'COMMAND_ABORTED_MISSING_FUSE_COMMAND'			:0x0A,
    'INVALID_NAMESPACE_FORMAT'					:0x0B,
    'COMMAND_SEQUENCE_ERROR'					:0x0C,
    'INVALID_SGL_SEGMENT_DESCRIPTOR'				:0x0D,
    'INVALID_NUMBER_OF_SGL_DESCRIPTORS'				:0x0E,
    'DATA_SGL_LENGTH_INVALID'					:0x0F,
    'METADATA_SGL_LENGTH_INVALID'				:0x10,
    'SGL_DESCRIPTOR_TYPE_INVALID'				:0x11,
    'INVALID_USE_OF_CONTROLLER_MEMORY_BUFFER'			:0x12,
    'PRP_OFFSET_INVALID'					:0x13,
    'ATOMIC_WRITE_UNIT_EXCEEDED'				:0x14,
    'LBA_OUT_OF_RANGE'          				:0x80,
    'CAPACITY_EXCEEDED'          				:0x81,
    'NAMESPACE_NOT_READY'          				:0x82,
    'RESERVATION_CONFLICT'          				:0x83,
    'FORMAT_IN_PROGRESS'          				:0x84,
    'UNRECOVERED_READ_ERROR'                    :0x81
}

#Command Specific Status Values.

IOQ_SC = {

    'INVALID_QUEUE_IDENTIFIER'					:0x00,
    'INVALID_QUEZE_SIZE'					:0x01,
    'INVALID_INTERRUPT_VECTOR'					:0x08,
}

#Feature Support
capability = {0 : 'Not Supported', 1 : 'Supported'}

#Command Manager Modes
BATCH_EXECUTION                 = 0
CONTINUOUS_EXECUTION            = 1
SUSTAINED_Q_DEPTH               = 2
SUSTAINED_CMD					= 3

GIT_ORIGIN = '(ORIGIN : gitsdin.sandisk.com\css\hermes\develop)\(COMMIT_ID : '

#DST
DST_RESULT_STRUCTURE_SIZE = 28
MAX_NUM_DST_RESULTS = 20
FIRST_DST_RESULT_OFFSET = 4

#Name of the vendor admin
VENDOR_ADMIN_CMD = 0xFA

#FPGA Parameters. Upper limit of Register is 0 - 4095.
REGISTER_OFFSET_HIGHER = 0xFFF
REGISTER_OFFSET_LOWER = 0x0

REGVALUE_HIGHER = 0xFFFFFFFF
REGVALUE_LOWER = 0x0

