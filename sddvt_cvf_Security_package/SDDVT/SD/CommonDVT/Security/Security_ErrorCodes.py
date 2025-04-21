# Security ERROR CODES
# Python future modules for python3 forward compatibility
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    from builtins import map
    from builtins import *
    from builtins import object
class ErrorCodes(object):

    def __init__(self):

        self.error_codes = {
            
            '0x6000001': 'STATUS_SEC_INTERNAL_ERROR',
            '0x6000002': 'STATUS_SEC_KAT_FAILURE',                 
            '0x6000003': 'STATUS_SEC_INVALID_PARAMETER',
            '0x6000004': 'STATUS_SEC_DIAG_NOT_ALLOWED',
            '0x6000005': 'STATUS_SEC_DIAG_NOT_ALLOWED_NS',
            '0x6000006': 'STATUS_SEC_COMMAND_ABORTED',
            '0x6000007': 'STATUS_SEC_TRANSFER_ERROR',
            '0x6000008': 'STATUS_SEC_SEQUENCE_ERROR',
            '0x6000009': 'STATUS_SEC_MEDIA_ACCESS_DENIED',
            '0x600000a': 'STATUS_SEC_INVALID_FILE_SIZE',
            '0x600000b': 'STATUS_SEC_MEM_ALLOC_FAILED',
            '0x600000c': 'TATUS_SEC_MEM_RELESE_FAILED',
            '0x600000d': 'STATUS_SEC_SIGNATURE_FAILED',
            
 
            '0x6000202': 'STATUS_RMA_ERROR_MEMORY_ALLOCATION_FAILURE',
            '0x6000203': 'STATUS_RMA_ERROR_MEMORY_RELEASE_FAILURE',
            '0x6000204': 'STATUS_RMA_ERROR_AUTHENTICATION_FAILURE',            
            '0x6000205': 'STATUS_RMA_ERROR_PROTOCOL_VIOLATION',            
            '0x6000206': 'STATUS_RMA_ERROR_LOCK_LOCKED_DEVICE',
            '0x6000207': 'STATUS_RMA_ERROR_UNLOCK_UNLOCKED_DEVICE',
            '0x6000208': 'STATUS_RMA_ERROR_UNLOCK_NONSED_IN_DLE',
            '0x6000209': 'STATUS_RMA_ERROR_INVALID_PARAMETER',
            '0x600020a': 'STATUS_RMA_ERROR_CMD_ABORTED',
            '0x600020b': 'STATUS_RMA_ERROR_DIAG_NOT_ALLOWED_LRMA',
            '0x600020c': 'STATUS_RMA_ERROR_RSA_KEYLENGTH_MISMATCH',
            
            '0x6000301': 'STATUS_RSA_KEY_EFUSE_PARITY_FAILED',                 
            '0x6000302': 'STATUS_RSA_KEY_MEM_ALLOCATION_FAILED',
            '0x6000303': 'STATUS_RSA_KEY_VALIDATION_FAILED',
            '0x6000304': 'STATUS_SEC_RSA_SIGNATURE_FAILED',
            '0x6000305': 'STATUS_SEC_RSA_HASH_CALCULATION_FAILED',
            
          }

    def CheckError(self, errorcode):
        for key, value in list(self.error_codes.items()):
            if errorcode == key:
                return value
