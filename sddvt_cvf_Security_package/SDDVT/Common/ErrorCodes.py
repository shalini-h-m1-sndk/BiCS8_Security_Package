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
            0:'CARD_NO_ERROR',
            1:'CARD_IS_NOT_RESPONDING',
            2:'CARD_CMD_CRC_ERROR',
            3:'CARD_ILLEGAL_CRC_STATUS',
            4:'CARD_DATA_STATUS_CRC_ERROR',
            5:'CARD_IS_BUSY',
            6:'CARD_IS_NOT_READY',
            7:'CARD_READ_CRC_ERROR',
            8:'CARD_ILLEGAL_CMD',
            9:'CARD_ERASE_PARAM',
            10:'CARD_WP_VIOLATION',
            11:'CARD_ERROR',
            12:'CARD_WP_ERASE_SKIP',
            13:'CARD_ADDRESS_ERROR',
            14:'CARD_ECC_FAILED',
            15:'CARD_IS_LOCKED',
            16:'CARD_WRONG_MODE',
            17:'CARD_CMD_PARAM_ERROR',
            18:'CARD_ERASE_SEQ_ERROR',
            19:'CARD_ERASE_RESET',
            20:'CARD_NO_CRC_WR_RESP',
            21:'CARD_OVERRUN',
            22:'CARD_UNDERRUN',
            23:'CARD_CIDCSD_OVERWRITE',
            24:'CARD_ECC_DISABLED',
            25:'WATCHDOG_TIME_OUT_FIFO_EMP',
            26:'CARD_BLK_LEN_ERROR',
            27:'CARD_TIME_OUT_RCVD',
            28:'WATCHDOG_TIME_OUT_FIFO_FULL',
            29:'CARD_LOCK_UNLOCK_FAILED',
            30:'CARD_NOT_IN_TEST_MODE',
            31:'CARD_OUT_OF_RANGE',
            32:'CARD_CC_ERROR',
            33:'CARD_INTERFACE_ERROR',
            34:'CARD_FREQ_ERROR',
            35:'MMC_LAST_WRITE_MISMATCH',
            36:'MMC_NOT_SUPPORT_BURST',
            37:'WATCHDOG_TIME_OUT_END_RESP',
            38:'MMC_ERR_NEXT_DATA',
            39:'CARD_COMPARE_ERROR',
            40:'SD_VERIFICATION_FAILED = 40',
            41:'SD_ATHENTICATION_FAILED',
            42:'SD_FAILED_ACMD_ENABLE',
            43:'SD_FAILED_GET_R2',
            44:'CARD_FAILED_CARD_SELECTION',
            45:'SD_FAILED_SECURE_READ_CMD',
            46:'SD_FAILED_SECURE_WRITE_CMD',
            47:'VERIFY_MEDIA_KEY_FAILED',
            48:'PROCESS_NEW_MKB_FAILED',
            49:'SD_FAILED_TO_OPEN_NEW_MKB_FILE',
            50:'ERROR_CARD_DETECTED',
            51:'CARD_COM_CRC_ERROR',
            52:'CARD_ILLEGAL_MODE',
            53:'CARD_TIME_OUT_PRG_DONE',
            54:'CARD_SPI_ERROR_TOKEN',
            55:'USER_PARAMETER_ERROR',
            56:'DRIVER_INTERNAL_ERROR',
            57:'BUFFER_ALLOCATION_ERROR',
            58:'CARD_END_ERR',
            59:'CARD_OVERFLOW_ERR',
            60:'CARD_RD_DT_ERR',
            61:'WATCHDOG_TIME_OUT_ENHANCED_OPERATION',
            62:'CARD_ENHANCED_RES_ERROR',
            63:'IDD_MEASURE_HOST_ERROR',
            64:'COMPATIBILLITY_ERROR',
            65:'CARD_SWITCH_ERROR',
            66:'FORCE_STOP_ERROR',
            67:'EPP_START_ERROR',
            68:'EPP_END_ERROR',
            69:'PARAMETER_ERROR',
            70:'USD_ADTR_CMDSUCCESS',
            71:'USD_ADTR_CMDFAIL',
            72:'INVALID_DATALENGTH',
            73:'COMMIT_ERROR',
            74:'THIRD_COMMAND_ERROR',
            75:'SECURE_DATA_IN_ERROR',
            76:'PATTERN_DATA_IN_ERROR',
            77:'SEND_DATA_BLK_ERROR',
            78:'READ_DATA_BLK_ERROR',
            79:'UNKNOWN_ERROR',
            80:'UIB_TIME_OUT_ERROR',
            81:'UNKOWN_OPCODE_ERROR',
            82:'UNKOWN_CMD_CODE_ERROR',
            83:'EMPTY_STATUS_FIFO',
            84:'STATUS_FIFO_OVERFLOW',
            192:'UIB_WRITE_TIMEOUT_ERROR',
            193:'UIB_READ_TIMEOUT_ERROR',
            194:'EPP_TIMEOUT_ERR',
            195:'MAIL_BOX_NO_MESSG',
            196:'INVALID_PARAM_ERROR',
            197:'RS232_RECEIVE_FAIL',
            198:'TRGR_IN_PATH_ERROR',
            224:'FLASH_INTEGRITY_CHECK',
            225:'RECORD_TYPE',
            226:'SEGMENT_TYPE',
            227:'CHECKSUM_ERROR',
            228:'CODE_SIZE_EXCEEDED',
            229:'USD_BL_ADRSPACE',
            230:'EOF_REACHED',
            231:'SCSI_PARAM_ERROR',
            232:'CBW_SIGNATURE_ERROR',
            233:'NOT_ALL_BLOCKS_WRITTEN',
            234:'WATCHDOG_TIMEOUT_PATERN_GEN',
            235:'WATCHDOG_TIMEOUT_POWER',
            236:'DUT_INTERFACE_ERROR',
            237:'HW_MON_3V3',
            238:'HW_MON_VDD_IO',
            239:'HW_MON_VDD_SD',
            240:'HW_MON_VDD_INAND',
            241:'HW_MON_CU_SD',
            242:'HW_MON_CU_INAND',
            243:'NO_CARD_ERR',
            244:'NO_HID',
            245:'POWER_ON_OFF_GENERAL_ERR',
            246:'CU_TEST_ERROR',
            247:'HOST_MAX_READ_TO_CROSSED',
            248:'HOST_MAX_WRITE_TO_CROSSED',
            249:'HOST_FREQ_ERR',
            250:'HOST_FREQ_TIMEOUT',
            251:'HOST_IS_NOT_CONNECTED',
            252:'TOKEN_TIMEOUT_ERR',
            253:'DATA_TIMEOUT_ERR',
            254:'TOKEN_ERR',
            255:'BOOT_DONE_ERR',
            256:'BOOT_USER_PARAM_ERROR',
            257:'PG_ST_PROCESS_ERROR',
            258:'HW_SET_VOLT_ERROR',
            259:'EMMC_SLEEP_STATE_VERIFICATION_ERROR',
            260:'ERROR_PAT_GEN_NOT_MATCHING_SDR_FPGA_REV',
            261:'ERROR_CARD_PROP_FACTORY_INVALID_STATE',
            262:'ERROR_CARD_PROP_FACTORY_INVALID_CARD_MODE',
            263:'ERROR_CARD_PROP_FACTORY_UNKNOWN_CSD_STRUCT_VER',
            264:'ERROR_CARD_PROP_FACTORY_UNKNOWN_EXT_CSD_VER',
            265:'ERROR_CARD_PROP_FACTORY_CARD_MODE_NOT_INITIALIZED',
            266:'ERROR_SD_CARD_PROPERTIES_INSTANCE',
            267:'ERROR_SD_CMD38_ARGUMENT_IS_NOT_DEFINED',
            268:'ERROR_SD_CARD_ERASE_GRP_SIZE_ZERO',
            269:'ERROR_SD_CARD_DEOS_NOT_SUPPORT_OPERATION',
            270:'PROGRAMMING_BOOTLOADER_FAILED',
            271:'MY_HOST_FPGA_DOWNLOAD_FAILED',
            272:'NO_XLINX_HOST_CONNECTED',
            273:'TOKEN_BUS_MISMATCH_ERROR',
            274:'HWRESET_WATCHDOG_TIMEOUT',
            275:'USER_SET_MAX_CURRENT_OVER_HOST_LIMIT',
            276:'CMD_WENT_HIGH_AFTER_RESPONSE',
            277:'DATA_WENT_HIGH_AFTER_RESPONSE',
            278:'CMD_AND_DATA_WENT_HIGH_AFTER_RESPONSE',
            279:'CMD_WENT_HIGH_DURING_CLOCK_OFF',
            280:'DATA_WENT_HIGH_DURING_CLOCK_OFF',
            281:'CMD_AND_DATA_WENT_HIGH_DURING_CLOCK_OFF',
            282:'DATA_WENT_HIGH_FIRST',
            283:'CMD_AND_DATA_DIDNT_GO_HIGH',
            284:'DATA_DIDNT_GO_HIGH',
            285:'CMD_DIDNT_GO_HIGH',
            286:'CMD19_TIMEOUT_ERROR',
            287:'CMD19_RESPONSE_TO_ERROR',
            288:'CMD19_DATA_MISCOMPARE_ERROR',
            289:'CMD19_CRC_RESPONSE_ERROR',
            290:'CMD19_READ_TIMEOUT_ERROR',
            291:'CMD19_CRC_DATA_ERROR',
            292:'WATCHDOG_TIMEOUT_TUNING',
            293:'FAST_BOOT_TIMEOUT_ERR',
            294:'SET_HIGH_SPEED_NOT_SUPORTED_IN_MMC',
            295:'HPI_TIMEOUT_ERROR',
            296:'DRIVER_FAILURE',
            297:'CHUNK_COUNT_BLOCK_MISMATCH',
            298:'PARTIAL_CONFIG_SWITCH_ERROR',
            299:'PARTIAL_CONFIG_WATCHDOG_ERROR',
            300:'FPGA_DOES_NOT_SUPPORT_OPERATION',
            301:'ENABLE_VDDIO_ISNT_SUPPORT_IN_LOW_REGION',
            302:'UHS_VDDIO_HIGH_THAN_1V9',
            303:'SET_VOLT_OUT_OF_REGION_ERROR',
            304:'VDDH_HIGHER_THAN_LIMIT',
            305:'LATENCY_OVERFLOW',
            306:'MDL_CPP_EXCEPTION',
            307:'HOST_ASYNC_POWER_LOSS_OR_HWRST_EVENT',
            308:'NO_OPTIMAL_TAP_FOUND',
            309:'USER_SET_SUM_OF_VDDS_MAX_CURRENT_OVER_HOST_LIMIT',
            310:'ILLEGAL_VDET_SEQUENCE_ERROR',
            311:'WRONG_SUB_PROTOCOL_TYPE',
            312:'WINDOWS_DIR_NOT_FOUND',
            313:'FREQUENCY_OPERATION_ERROR',
            314:'UNSUPPORTED_DATA_TRANSER_MODE',
            315:'UNSUPPORTED_ABORT_MODE',
            316:'UNSUPPORTED_ABORT_OPERATION',
            317:'UNSUPPORTED_BOOT_SCOPE',
            318:'UNSUPPORTED_MACRO_TYPE',
            319:'UNSUPPORTED_ABORT_TYPE',
            320:'UNSUPPORTED_IMMEDIATE_FORMAT',
            321:'WATCHDOG_TIMEOUT_DEL_TAP',
            322:'VDDIO_HIGHER_THAN_VDDH',
            323:'TRYING_TO_SET_A_SD_MODE_ON_MMC_FW',
            324:'CARD_END_BIT_ERROR',
            325:'CARD_CC_TOTAL_ERRORS',
            5124: 'DATA_MISCOMPARE_ERROR'

            }
        self.Error_names = ['CARD_IS_NOT_RESPONDING',
                            'CARD_CMD_CRC_ERROR',
                            'CARD_ILLEGAL_CRC_STATUS',
                            'CARD_DATA_STATUS_CRC_ERROR',
                            'CARD_READ_CRC_ERROR',
                            'CARD_NO_CRC_WR_RESP',
                            'CARD_TIME_OUT_RCVD',
                            'WATCHDOG_TIME_OUT_END_RESP',
                            'CARD_COMPARE_ERROR',
                            'CARD_END_ERR',
                            'WATCHDOG_TIMEOUT_PATERN_GEN'
                            ]
        self.DataErrorList = list(map(self.CheckError, self.Error_names))    #Returns the error number of all the errors mentioned in the Error_names

    def CheckError(self, ErrorString):
        for key, value in list(self.error_codes.items()):
            if ErrorString == value:
                return key
