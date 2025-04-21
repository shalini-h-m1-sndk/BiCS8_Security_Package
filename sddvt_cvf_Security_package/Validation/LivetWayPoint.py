#!/usr/bin/env python

##
# @file
# @brief Livet Way Point Handler Module
# @details this is a module for managing all way point operation
# @author Joydip Roy Chowdhury
# @date 14/04/2020
# @copyright (C) 2014 SanDisk Corporation
# @USAGE from Validation import LivetWayPoint as WP

from builtins import str
from builtins import range
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
#import Protocol.ata.Basic.VTFContainer as VTF


class LivetWayPoint(object):

   __staticObjWayPointHandler = None
   __staticWayPointHandlerObjectCreated = None

   def __new__(cls, *args, **kwargs):
      """
      Memory allocation ( This function use to create Singleton object of OrthogonalTestManager)
      """

      if not LivetWayPoint.__staticObjWayPointHandler:
         LivetWayPoint.__staticObjWayPointHandler = super(LivetWayPoint, cls).__new__(cls, *args, **kwargs)
      return LivetWayPoint.__staticObjWayPointHandler

   def __init__(self):

      staticObj = None
      if LivetWayPoint.__staticWayPointHandlerObjectCreated:
         return
      LivetWayPoint.__staticWayPointHandlerObjectCreated = True
      super(LivetWayPoint, self).__init__()
      LivetWayPoint.staticObj = self
      self.VTFContainer = VTF.VTFContainer()
      self.livetObj = self.VTFContainer._livet
      self.CVFTestFactory = FactoryMethod.CVFTestFactory()
      self.TF = self.CVFTestFactory.factory.TestFixture
      self.wayPointDefaultDict = {
                  "D_MODEL_FLASH_WRITE_COMPLETED": [0, 0, self.CB_FlashWriteComplete],
                  "D_MODEL_FLASH_READ_COMPLETED": [0, 0, self.CB_FlashReadComplete],
                  #"D_MODEL_DCT_READ_COLLISION_DETECTED": [0, 0, self.CB_ReadCollisionDetected],
                  #"D_MODEL_DCT_WRITE_COLLISION_DETECTED": [0, 0, self.CB_WriteCollisionDetected],
                  "D_MODEL_DCT_WRITE_CACHE_FLUSHED": [0, 0, self.CB_WriteCacheFlushed],
                  #"D_MODEL_DCT_READ_CACHE_FLUSHED": [0, 0, self.CB_ReadCachedFlushed],
                  #"D_MODEL_INP_WRITE_QUEUE_FULL": [0, 0, self.CB_InPutWriteQueueFull],
                  #"D_MODEL_OPB_WRITE_TO_HSB": [0, 0, self.CB_OpenSequentialBlock],
                  #"D_MODEL_OPB_WRITE_TO_HRB": [0, 0, self.CB_OpenRandomBlock],
                  #"D_MODEL_BAM_BEFORE_BLOCK_ALLOCATION": [0, 0, self.CB_BeforeBlockAllocation],
                  #"D_MODEL_BAM_BLOCK_ALLOCATED": [0, 0, self.CB_BlockAllocated],
                  #"D_MODEL_BAM_BLOCK_REUSE": [0, 0, self.CB_BlockReuse],
                  #"D_MODEL_BAM_BLOCK_FREE": [0, 0, self.CB_BlockFree],
                  #"D_MODEL_BAM_NOTIFY_BAD_BLOCK": [0, 0, self.CB_MarkedBadBlock],
                  #"D_MODEL_BAM_HANDLE_BAD_BLOCK": [0, 0, self.CB_HandleBadBlock],
                  #"D_MODEL_BAM_INVALIDATE_METABLOCK": [0, 0, self.CB_InvalidatedMetaBlock],
                  #"D_MODEL_BMS_HOST_TARGET_SELECT": [0, 0, self.CB_BMSHostTargetSelect],
                  #"D_MODEL_FTL_CONTROL_WRITE": [0, 0, self.CB_ControlWrite],
                  #"D_MODEL_FTL_CONTROL_READ": [0, 0, self.CB_ControlRead],
                  #"D_MODEL_MST_UPDATED": [0, 0, self.CB_MSTUpdated],
                  #"D_MODEL_RMW_DETECTED": [0, 0, self.CB_RMWDetected],
                  #"D_MODEL_SGC_DELTA_FLUSH ": [0, 0, self.CB_GATDeltaFlush],
                  #"D_MODEL_ROM_IDLE_MODE": [0, 0, self.CB_ROMIdleLoop],
                  #"D_MODEL_DLE_IDLE_MODE": [0, 0, self.CB_DLEIdleLoop],
                  #"D_MODEL_TRIM_CMD_TIMEOUT": [0, 0, self.CB_TrimCmdTimeOut],
                  #"D_MODEL_TRIM_OVERLAP_DETECTED": [0, 0, self.CB_TrimWPUOverlapDetected],
                  #"D_MODEL_TRIM_CC_DETECTED": [0, 0, self.CB_TrimDCTCollision],
                  #"D_MODEL_TRIM_BM_UNMAP_QUEUE_FULL": [0, 0, self.CB_TrimBMUnmapQueueFull],
                  #"D_MODEL_TRIM_COMPLETE": [0, 0, self.CB_TrimComplete],
                  #"D_MODEL_INP_READ_STRICT_ORDER_SEQ_ID": [0, 0, self.CB_InOrderReadSeqGenerated],
                  #"D_MODEL_HIMSS_READCMD_COMPLETE": [0, 0, self.CB_HimssReadCmdComplete],
                  #"D_MODEL_HIMSS_WRITECMD_COMPLETE": [0, 0, self.CB_HimssWriteCmdComplete],
                  "D_MODEL_HIMSS_BEFORECMD_COMPLETE": [0, 0, self.CB_HimssBeforeCmdComplete],
                  #"D_MODEL_HIMSS_DATAXFER_IN_PROGRESS": [0, 0, self.CB_HimssDataXferInProgress],
                  #"D_MODEL_HIMSS_EXCEPTIONHANDLING_INPROGRESS": [0, 0, self.CB_HimssExceptionHandlingInProgress],
                  #"D_MODEL_HIMSS_EXCEPTIONHANDLING_COMPLETE": [0, 0, self.CB_HimssExceptionHandlingComplete],
                  #"D_MODEL_LINK_POWER_STATE_TRANSITION": [0, 0, self.CB_LinkStateChange],
                  #"D_MODEL_SYS_POWER_STATE_TRANSITION": [0, 0, self.CB_SysPwrStateChange],
                  #"D_MODEL_DEVICE_POWER_STATE_TRANSITION": [0, 0, self.CB_DevPwrStateChange],
                  #"D_MODEL_TVx_TIMER_EXPIRED": [0, 0, self.CB_TVxTimerExpired],
                  #"D_MODEL_STANDBY_TIMER_EXPIRED": [0, 0, self.CB_StandbyTimerExpired],
                  #"D_MODEL_BI_READ_FROM_ROM_END": [0, 0, self.CB_BIReadFromROMEnd],
                  #"D_MODEL_BLR_READ_FROM_ROM_END": [0, 0, self.CB_BLRReadFromROMEnd],
                  #"D_MODEL_BI_ACTIVE_COPY": [0, 0, self.CB_BIActiveCopy],
                  #"D_MODEL_BI_WRITE_START": [0, 0, self.CB_OnBIWriteStart],
                  #"D_MODEL_BI_WRITE_END": [0, 0, self.CB_OnBIWriteEnd],
                  #"D_MODEL_BI_ERASE": [0, 0, self.CB_OnBIErase],
                  #"D_MODEL_BI_WRITE_READVERIFY_START": [0, 0, self.CB_ReadVerifyStart],
                  #"D_MODEL_BTST_TEST_TERMINATED": [0, 0, self.CB_OnBTSTTerminated],
                  #"D_MODEL_USER_ROM_DATA_READ_STARTED": [0, 0, self.CB_OnUROMDataReadStarted],
                  #"D_MODEL_USER_ROM_DATA_READ_SUCCEEDED": [0, 0, self.CB_OnUROMDataReadSucceeded],
                  #"D_MODEL_USER_ROM_DATA_READ_UNUSED_BYTE": [0, 0, self.CB_OnUROMDataReadUnUsed],
                  #"D_MODEL_USER_ROM_DATA_READ_FAIL": [0, 0, self.CB_OnUROMDataReadFail],
                  #"D_MODEL_USER_ROM_MEMCEL_STANDALONE_FILE_READ": [0, 0, self.CB_OnUROMMemcelStandaloneFileRead],
                  #"D_MODEL_USER_ROM_SN_CORRUPTED": [0, 0, self.CB_OnUROMSNDKCorrupted],
                  #"D_MODEL_DLE_READ_USER_ROM": [0, 0, self.CB_OnDLEReadUROM],
                  #"D_MODEL_DLE_READ_USER_ROM_PAGE_COPY": [0, 0, self.CB_OnDLEReadUROMCopy],
                  #"D_MODEL_FGI_LOAD_SUCCEEDED": [0, 0, self.CB_OnFGILoadSucceeded],
                  #"D_MODEL_FGI_LOAD_FAILED": [0, 0, self.CB_OnFGILoadFailed],
                  #"D_MODEL_LDPC_CONFIG_READ_SUCCEEDED": [0, 0, self.CB_OnLDPCConfigReadSucceeded],
                  #"D_MODEL_LDPC_CONFIG_READ_FAILED": [0, 0, self.CB_OnLDPCConfigReadFailed],
                  #"D_MODEL_INVALID_BACKUP_ID": [0, 0, self.CB_OnInvalidBackupID],
                  #"D_MODEL_VALID_BACKUP_ID": [0, 0, self.CB_OnValidBackupID],
                  #"D_MODEL_FM_OPEN_BLOCK": [0, 0, self.CB_OnFmOpenBlock],
                  #"D_MODEL_MST_STORE": [0, 0, self.CB_BeforeMSTStore],
                  #"D_MODEL_MST_STORE_COMPLETED": [0, 0, self.CB_MSTStoreCompleted],
                  #"D_MODEL_MST_UPDATED": [0, 0, self.CB_OnMstUpdated],
                  #"D_MODEL_MST_HANDLE_EXCEPTION": [0, 0, self.CB_OnMstHandleException],
                  #"D_MODEL_MST_ALLOC_NEW_MST_BLOCK": [0, 0, self.CB_OnMstAllocNewMstBlock],
                  #"D_MODEL_SIB_WRITE_PFMU": [0, 0, self.CB_OnSibWritePfmu],
                  #"D_MODEL_SIB_READ_PFMU": [0, 0, self.CB_OnSibReadePfmu],
                  #"D_MODEL_SIB_HANDLE_EXCEPTION": [0, 0, self.CB_OnSibHandleException],
                  #"D_MODEL_FM_FIRST_TIME_MOUNT_START": [0, 0, self.CB_FirstMountStart],
                  #"D_MODEL_FM_FIRST_TIME_MOUNT_END": [0, 0, self.CB_FirstMountEnd],
                  #"D_MODEL_FM_NORMAL_MOUNT_START": [0, 0, self.CB_NormalMountStart],
                  #"D_MODEL_FM_NORMAL_MOUNT_END": [0, 0, self.CB_NormalMountEnd],
                  #"D_MODEL_MST_SIB_UPDATED": [0, 0, self.CB_MSTMBaddrUpdatedInSIB],
                  #"D_MODEL_MST_MOUNT_DONE": [0, 0, self.CB_MSTloadingCompletedDuringNM],
                  #"D_MODEL_MST_READ_VERIFY_STARTED": [0, 0, self.CB_MSTReadVerifyStarted],
                  #"D_MODEL_MST_READ_VERIFY_COMPLETED": [0, 0, self.CB_MSTReadVerifyCompleted],
                  #"D_MODEL_MST_SIB_UPDATE_STARTED": [0, 0, self.CB_MSTSIBUpdateStarted],
                  #"D_MODEL_NDWL_DETECTION_TRIGGER": [0, 0, self.CB_OnNDWLDetectionTrigger],
                  #"D_MODEL_NDWL_DETECTION_COMPLETE": [0, 0, self.CB_OnNDWLDetectionComplete],
                  #"D_MODEL_NDWL_CORRECTION_TRIGGER": [0, 0, self.CB_OnNDWLCorrectionTrigger],
                  #"D_MODEL_NDWL_CORRECTION_COMPLETE": [0, 0, self.CB_OnNDWLCorrectionComplete],
                  #"D_MODEL_NDWL_NOTIFYING_BAD_BLOCK": [0, 0, self.CB_OnNDWLNotificationOfBadBock],
                  ##"D_MODEL_DP_COUNT_BLOCK_ERASE": [0, 0, self.CB_OnOPDetectionTrigger],
                  ##"BLOCK_RETIRED": [0, 0, self.CB_OnBlockRetirement],
                  #"D_MODEL_NDWL_ERASE_COMPLETE": [0, 0, self.CB_OnNDWLEraseComplete],
                  ##"MB_ERASE_START": [0, 0, self.CB_OnMBEraseStart],
                  #"D_MODEL_SIB_READ_PFMU": [0, 0, self.CB_OnSIBRead],
                  #"D_MODEL_SIB_WRITE_PFMU": [0, 0, self.CB_OnSIBWrite],
                  #"D_MODEL_SIB_HANDLE_EVENT_START": [0, 0, self.CB_OnSIBHandleStart],
                  #"D_MODEL_SIB_HANDLE_EVENT_END": [0, 0, self.CB_OnSIBHandleEnd],
                  #"D_MODEL_HPM_HIGH_BER_SIB": [0, 0, self.CB_OnSIBHighBER],
                  #"D_MODEL_DLE_UT_SIB_BLOCK_ALLOCATED": [0, 0, self.CB_OnSIBBlockAllocation],
                  #"D_MODEL_DLE_UT_FA_BLOCK_ALLOCATED": [0, 0, self.CB_OnFABlockAllocation],
                  #"D_MODEL_DLE_UT_BAD_BLOCK_FOUND": [0, 0, self.CB_OnBadBlockFound],
                  #"D_MODEL_SIB_HANDLE_EXCEPTION": [0, 0, self.CB_OnSIBHandleException],
                  #"D_MODEL_SIB_FIRST_TIME_MOUNT_END": [0, 0, self.CB_OnSIBFirstTimeMountEnd],
                  #"D_MODEL_SIB_NORMAL_MOUNT_END": [0, 0, self.CB_OnSIBNormalMountEnd],
                  #"D_MODEL_SIB_BLOCK_FULL": [0, 0, self.CB_OnSIBBlockFull],
                  #"D_MODEL_FM_NORMAL_MOUNT_START": [0, 0, self.CB_OnFMNormalMountStart],
                  #"D_MODEL_FM_FIRST_TIME_MOUNT_START": [0, 0, self.CB_OnFMFirstTimeMountStart],
                  #"D_MODEL_FM_REUSE_BLOCK": [0, 0, self.CB_OnSIBReuseBlock],
                  #"D_MODEL_MEMCEL_FILE_UPDATE_STATUS": [0, 0, self.CB_OnMemcelFileUpdateStatus],
                  #"D_MODEL_MEMCEL_EXTENDED_TABLE_PAGE_PARSE_SUCCESS": [0, 0, self.CB_OnMemcelExtTablePageAddrParse],
                  #"D_MODEL_USE_USER_ROM_MEMCEL": [0, 0, self.CB_OnUseUserRomMemcel],
                  #"D_MODEL_USER_ROM_MEMCEL_DECODE_STATUS": [0, 0, self.CB_OnUserRomMemcelDecodeStatus],
                  #"D_MODEL_CURRENT_MEMCEL_IN_USE": [0, 0, self.CB_OnCurrentMemcelInUse],
                  #"D_MODEL_OPB_OPEN_BLOCK": [0, 0, self.CB_OPBOpenBlock],
                  #"D_MODEL_OPB_BLOCK_CLOSURE": [0, 0, self.CB_OnOpenBlockClosure],
                  #"D_MODEL_HFM_RLC_SELECT_SOURCE_BLOCK": [0, 0, self.CB_OnRLCSourceSelect],
                  #"D_MODEL_HFM_RLC_SELECT_TARGET_BLOCK": [0, 0, self.CB_RLCTargetSelect],
                  #"D_MODEL_HFM_RLC_SOURCE_FINISHED": [0, 0, self.CB_RLCSourceFinished],
                  #"D_MODEL_HFM_RLC_COMPLETED": [0, 0, self.CB_RLCCompleted],
                  #"D_MODEL_HFM_RLC_RELEASE_BLOCK": [0, 0, self.CB_RLCBlockRelease],
                  #"D_MODEL_HFM_RLC_CANCELLED": [0, 0, self.CB_RLCCancelled],
                  #"D_MODEL_BME_RLC_STEP_DONE": [0, 0, self.CB_RLCStepDone],
                  #"D_MODEL_BME_RLC_EPWR_STEP": [0, 0, self.CB_RLCEpwrStep],
                  #"D_MODEL_BME_RLC_EPWR_COMPLETE": [0, 0, self.CB_RLCEpwrComplete],
                  #"D_MODEL_HFM_RLC_ALLOCATE_TARGET_FOR_DEST_RLC": [0, 0, self.CB_RLCAllocateTargetForDestRlc],
                  #"D_MODEL_BM_HYBRID_STATE": [0, 0, self.CB_BM_Hybrid_State],
                  #"D_MODEL_MST_WRITE_PON": [0, 0, self.CB_MstWritePon],
                  #"D_MODEL_MTM_FIRST_MOUNT_STARTED": [0, 0, self.CB_MTMFirstMountStart],
                  #"D_MODEL_MTM_FIRST_MOUNT_COMPLETED": [0, 0, self.CB_MTMFirstMountEnd],
                  #"D_MODEL_MTM_NORMAL_MOUNT_STARTED": [0, 0, self.CB_MTMNormalMountStart],
                  #"D_MODEL_MTM_NORMAL_MOUNT_COMPLETED": [0, 0, self.CB_MTMNormalMountEnd],
                  #"D_MODEL_FM_GOING_TO_OPEN_BLOCK": [0, 0, self.CB_AllocateNewTBBorTRB],
                  #"D_MODEL_MTM_TRB_REPLACE": [0, 0, self.CB_TRBAllocted],
                  #"D_MODEL_MTM_TBB_ALLOCATED": [0, 0, self.CB_TBBAllocated],
                  #"D_MODEL_MTM_TOB_REPLACE": [0, 0, self.CB_ReplaceTOBwithTBB],
                  #"D_MODEL_MTM_CLOSE_BLOCK": [0, 0, self.CB_CloseMTMBlock],
                  #"D_MODEL_MTM_BLOCK_MOUNT_COMPLETED": [0, 0, self.CB_MTMBlockMountCompleted],
                  #"D_MODEL_MTM_WRITE_PART": [0, 0, self.CB_MTMWritePart],
                  #"D_MODEL_MTM_READ_PART": [0, 0, self.CB_MTMReadPart],
                  #"D_MODEL_MTM_FLUSH_LDT_DELTA": [0, 0, self.CB_MTMFlushLDTDetla],
                  #"D_MODEL_MTM_WRITE_EXCEPTION_OCCURRED": [0, 0, self.CB_MTMWriteExceptionOccurred],
                  #"D_MODEL_MTM_FREE_METABLOCK": [0, 0, self.CB_ReleaseMTMMetaBlock],
                  #"D_MODEL_MTM_READ_EXCEPTION_OCCURRED": [0, 0, self.CB_MTMReadExceptionOccurred],
                  #"D_MODEL_DYNAMIC_BLOCK_MFMU": [0, 0, self.CB_CompactionSourceSelected],
                  #"D_MODEL_TMB_RELOCATION_IN_PROGRESS": [0, 0, self.CB_MTMCompactionStarted],
                  #"D_MODEL_MTM_COMPACTION_COMPLETE": [0, 0, self.CB_MTMCompactionCompleted],
                  #"D_MODEL_MTM_MRCB_BUILDING_STARTED": [0, 0, self.CB_MRCBBuildingStarted],
                  #"D_MODEL_MTM_MRCB_BUILDING_COMPLETE": [0, 0, self.CB_MRCBBuildingCompleted],
                  #"D_MODEL_MTM_UPDATE_TOT": [0, 0, self.CB_ToTCommitDone],
                  #"D_MODEL_MTM_CLEAR_MRCB_BIT": [0, 0, self.CB_MRCBBitCleared],
                  #"D_MODEL_MTM_DELAYED_COMMIT_START": [0, 0, self.CB_DelayedCommitStart],
                  #"D_MODEL_MTM_DELAYED_COMMIT_INFO": [0, 0, self.CB_DelayedCommitInfo],
                  #"D_MODEL_MTM_DELAYED_COMMIT_SKIP": [0, 0, self.CB_DelayedCommitSkipped],
                  #"D_MODEL_MTM_DELAYED_COMMIT_COMPLETED": [0, 0, self.CB_DelayedCommitComplete],
                  #"D_MODEL_MTM_DCB_TCB_INFO_STORE": [0, 0, self.CB_FlagSetIndicatingTCBisPartOfDCB],
                  #"D_MODEL_MTM_DCB_TCB_INFO_CLEAR": [0, 0, self.CB_FlagClearIndicatingTCBisNotPartOfDCB],
                  #"D_MODEL_MTM_CLEAR_DCB_ON_PF": [0, 0, self.CB_ClearDCBonPF],
                  #"D_MODEL_BMD_DISPATCH_HOST_WRITE": [0, 0, self.CB_OnHostWrite],
                  #"D_MODEL_BMX_DISPATCH_WRITE_TO_RECOVERY": [0, 0, self.CB_OnRecoveryWrite],
                  #"D_MODEL_PFI_DISPATCH_ASB_WRITE": [0, 0, self.CB_OnXORDump],
                  #"D_MODEL_PFI_LOAD_SNAPSHOT_ASB": [0, 0, self.CB_OnXORRead],
                  #"D_MODEL_PFI_RECOVER_FROM_XTRAM": [0, 0, self.CB_OnXORReadFromXRAM],
                  #"D_MODEL_PFI_DEXOR": [0, 0, self.CB_OnHostReadForRecovery],
                  #"D_MODEL_PFI_PARTIAL_PARITY_WRITE": [0, 0, self.CB_OnParityRecreation],
                  #"D_MODEL_PFI_RECOVERY_FAILURE": [0, 0, self.CB_OnRecoveryFailure],
                  #"D_MODEL_CVD_EXCEPTION_HANDLING_START": [0, 0, self.CB_WP_CVD_ExceptionHandlingStart],
                  #"D_MODEL_CVD_EXCEPTION_HANDLING_FINISH": [0, 0, self.CB_WP_CVD_ExceptionHandlingFinish],
                  #"D_MODEL_CVD_BES_OP_START": [0, 0, self.CB_WP_CVD_BESOperationStart],
                  #"D_MODEL_CVD_BES_OP_RESULT": [0, 0, self.CB_WP_CVD_BESResult],
                  #"D_MODEL_CVD_EXPLICIT_BER_OP": [0, 0, self.CB_WP_CVDExplicitBerOp],
                  #"D_MODEL_DPX_LDPC_EXCEPTION": [0, 0, self.CB_WP_DpxLdpcException],
                  #"D_MODEL_DPX_FIM_EXCEPTION": [0, 0, self.CB_WP_DpxFimException],
                  #"D_MODEL_CVD_UNDERFLOW_DETECTED": [0, 0, self.CB_WP_CVD_UnderFlowDetected],
                  #"D_MODEL_CVD_OVERFLOW_DETECTED": [0, 0, self.CB_WP_CVD_OverFlowDetected],
                  #"D_MODEL_MTR_ADD_SB": [0, 0, self.CB_MtrAddSb],
                  #"D_MODEL_MTR_ADD_BB": [0, 0, self.CB_MtrAddBb],
                  #"D_MODEL_MTR_FTM_RELINK": [0, 0, self.CB_MtrFtmRelink],
                  #"D_MODEL_MTR_VALID_NONRELINKED_METABLOCK": [0, 0, self.CB_MtrValidNonRelinkedMetablock],
                  #"D_MODEL_MTR_INVALID_METABLOCK": [0, 0, self.CB_MtrInvalidMetablock],
                  #"D_MODEL_MTR_RELINK": [0, 0, self.CB_MtrRelink],
                  #"D_MODEL_MTR_CANCEL_RELINK": [0, 0, self.CB_MtrCancelRelink],
                  #"D_MODEL_MTR_METABLOCK_INVALIDATED": [0, 0, self.CB_MtrMetablockInvalidated],
                  #"D_MODEL_MTR_NOTIFY_BB": [0, 0, self.CB_MtrNotifyBb],
                  #"D_MODEL_MTR_NOTIFY_RELEASED_METABLOCK": [0, 0, self.CB_MtrNotifyReleasedMetablock],
                  #"D_MODEL_MTR_SUSPECTED_BB": [0, 0, self.CB_MtrSuspectedBb],
                  #'D_MODEL_MTR_FTM_FACTORY_BB': [0, 0, self.CB_MtrFtmFactoryBb],
                  #"D_MODEL_MTR_FALIED_CONSTRAINTS": [0, 0, self.CB_MtrFaliedConstraints],
                  #"D_MODEL_MTR_UNMARK_SUSPECTED_METABLOCK": [0, 0, self.CB_MtrUnmarkSuspectedMetablock],
                  #"D_MODEL_MTR_FTM_MAP_METADIE": [0, 0, self.CB_MtrFtmMapMetadie],
                  #"D_MODEL_MTM_START_PREPARE_FOR_TABLE_WRITE": [0, 0, self.CB_MtmStartPrepareForTableWrite],
                  #"D_MODEL_EPWR_START": [0, 0, self.CB_EPWRBegin],
                  #"D_MODEL_EPWR_END": [0, 0, self.CB_EPWREnd],
                  #"D_MODEL_EPWR_BALANCING_PHASED_START": [0, 0, self.CB_EPWRPhaseStart],
                  #"D_MODEL_EPWR_BALANCING_PHASED_END": [0, 0, self.CB_EPWRPhaseEnd],
                  #"D_MODEL_EPWR_MFMU_INFO": [0, 0, self.CB_EPWROnMFMU],
                  #"D_MODEL_EPWR_HANDLE_FAILURE": [0, 0, self.CB_HandleEPWRFailure],
                  #"D_MODEL_EPWR_FAILURE_RECOVERY": [0, 0, self.CB_EPWRRecoveryFailure],
                  #"D_MODEL_EPWR_RECOVERY_COMMIT": [0, 0, self.CB_EPWRRecoveryCommit],
                  #"D_MODEL_CVD_EXCEPTION_HANDLING_SB_START": [0, 0, self.CB_WP_ExceptionHandlingSbStart],
                  #"D_MODEL_BMD_GENERIC_ERASE": [0, 0, self.CB_BeforeBlockErase],
                  #"D_MODEL_READ_ONLY_MODE": [0, 0, self.CB_CardInReadOnlyMode],
                  #"D_MODEL_BAM_ERASE_COMPLETE": [0, 0, self.CB_BAMEraseComplete],
                  #"D_MODEL_PRE_EOL_DEVICE_STATUS_PER_POOL": [0, 0, self.CB_OnDeviceStatus],
                  #"D_MODEL_BAM_ERASE_START": [0, 0, self.CB_BAMEraseStart],
                  #"D_MODEL_CVD_MARGINAL_RECOVERY": [0, 0, self.CB_OnCVDMarginal],
                  #"D_MODEL_FM_CLOSE_BLOCK": [0, 0, self.CB_FmCloseBock],
                  #"D_MODEL_FM_FREE_BLOCK": [0, 0, self.CB_FmFreeBock],
              }
      self.defaultWpDictLen = len(self.wayPointDefaultDict["D_MODEL_FLASH_WRITE_COMPLETED"])

   def RegisterWaypoint(self, wpString):

      for key, value in list(wpString.items()):
         # Check if waypoint exist
         if key not in list(self.wayPointDefaultDict.keys()):
            raise ValidationError.TestFailError(self.fn, " Waypoint %s is Invalid" % (key))

         if value is not None:
            # Check if Waypoint is already registered, if yes Skip Registration
            if self.wayPointDefaultDict[key][0] == 0:
               self.wayPointDefaultDict[key].append(value)
               defaultFunc = self.wayPointDefaultDict[key]
               ret = self.livetObj.RegisterFirmwareWaypoint(str(key), defaultFunc[2])
               self.wayPointDefaultDict[key][0] = 1
               if ret == 0:
                  raise ValidationError.TestFailError(self.fn, " Waypoint %s Registration Failed." % (key))
               self.TF.logger.Info("Waypoint %s Registered Successfully" % (key))
            else:
               self.TF.logger.Info("Waypoint %s Is Already Registered.. Skipping" % (key))
         else:
            # Check if Waypoint is already registered, if yes Skip Registration
            if self.wayPointDefaultDict[key][0] == 0:
               wpString[key] = self.wayPointDefaultDict[key]
               defaultFunc = self.wayPointDefaultDict[key]
               ret = self.livetObj.RegisterFirmwareWaypoint(str(key), defaultFunc[2])
               self.wayPointDefaultDict[key][0] = 1
               if ret == 0:
                  raise ValidationError.TestFailError(self.fn, " Waypoint %s Registration Failed." % (key))
               self.TF.logger.Info("Waypoint %s Registered Successfully" % (key))
            else:
               self.TF.logger.Info("Waypoint %s Is Already Registered.. Skipping" % (key))
   @staticmethod
   def CallCustomCallBacks(waypointName, eventKey, args, processorId):
      """
      Description: If More than one callback are registered with waypoint
      this function will call them all.
      Parameters: waypointName: Name of waypoint.
      Parameters: eventKey: Gives registered key of Event
                  args:  args given in waypoint.
                  processorId: gives processor Id.
      Returns: None
      Exceptions: None
      """
      testobj = LivetWayPoint.staticObj
      noOfCallbacks = len(testobj.wayPointDefaultDict[waypointName])
      if noOfCallbacks:
         funcList = testobj.wayPointDefaultDict[waypointName]
         for currCallBack in range(testobj.defaultWpDictLen, noOfCallbacks):
            funcList[currCallBack](eventKey, args, processorId)


   def DeRegisterWaypoint(self, wpString, WaypointName):
      """
      Description: UnRegister Waypoint .
      Parameters: wpString: WayPoint String as mentioned in ModelWaypoint.h
                  wpCallBackFunc: callback function needs to registered for WP.
      Returns: None
      Exceptions: None
      """
      foundKey = False
      for key in list(wpString.keys()):
         if key == WaypointName:
            del wpString[key]
            ret = self.livetObj.RegisterFirmwareWaypoint(key, None)
            self.wayPointDefaultDict[key][0] = 0
            if ret == 0:
               raise ValidationError.TestFailError(self.fn, " Waypoint %s DeRegistration Failed." % (key))
            foundKey = True
            return

      if foundKey is False:
         self.TF.logger.Info(" Waypoint %s is not registered with test" % (WaypointName))
         assert foundKey is False, " Trying to DeRegister Unknown Waypoint"

   def DeRegisterAllWaypoints(self, wpString):
      """
      Description: UnRegister All Waypoints .
      Parameters: wpString: WayPoint dictionary provided by test to DeRegister.
      Returns: None
      Exceptions: None
      """
      for key, value in list(wpString.items()):
         value = None
         if key in list(wpString.keys()):
            ret = self.livetObj.RegisterFirmwareWaypoint(key, value)
            self.wayPointDefaultDict[key][0] = 0
            if ret == 0:
               raise ValidationError.TestFailError(self.fn, " Waypoint %s DeRegistration Failed." % (key))

   @staticmethod
   def CB_FlashWriteComplete(eventKey, args, processorId):
      """
      Description: Write Complete waypoint default handler .
      Parameters: eventKey: Gives registered key of Event
                  args:  arguments passed (total 5).
                         args[0] -> MB Number
                         args[1] -> MB Offset
                         args[2] -> LFMU
                         args[3] -> Amount of LFMU
                         args[4] -> PFMU
                  processorId: gives processor Id.
      Returns: None
      Exceptions: None
      """
      testobj = LivetWayPoint.staticObj
      testobj.TF.logger.Info("D_MODEL_FLASH_WRITE_COMPLETED : MB = 0x%04x; MB_Offset = 0x%04x;\
        lfmu = 0x%04x; AMountOfLfmu = 0x%04x, pfmu = 0x%04x" %
                                                             (args[0], args[1], args[2], args[3], args[4]))

      # Increment Counter
      testobj.wayPointDefaultDict["D_MODEL_FLASH_WRITE_COMPLETED"][1] += 1
      ## Call custom callbacks if registered.
      if len(testobj.wayPointDefaultDict["D_MODEL_FLASH_WRITE_COMPLETED"]) > testobj.defaultWpDictLen:
         testobj.CallCustomCallBacks("D_MODEL_FLASH_WRITE_COMPLETED", eventKey, args, processorId)

   @staticmethod
   def CB_FlashReadComplete(eventKey, args, processorId):
      """
      Description: Write Complete waypoint default handler .
      Parameters: eventKey: Gives registered key of Event
                  args:  arguments passed (total 5).
                         args[0] -> MB Number
                         args[1] -> MB Offset
                         args[2] -> LFMU
                         args[3] -> Amount of LFMU
                         args[4] -> PFMU
                  processorId: gives processor Id.
      Returns: None
      Exceptions: None
      """
      testobj = LivetWayPoint.staticObj
      testobj.TF.logger.Info("D_MODEL_FLASH_READ_COMPLETED : MB = 0x%04x; MB_Offset = 0x%04x; \
        lfmu = 0x%04x; AMountOfLfmu = 0x%04x, pfmu = 0x%04x" %
                                                             (args[0], args[1], args[2], args[3], args[4]))

      # Increment Counter
      testobj.wayPointDefaultDict["D_MODEL_FLASH_READ_COMPLETED"][1] += 1
      # Call custom callbacks if registered.
      if len(testobj.wayPointDefaultDict["D_MODEL_FLASH_READ_COMPLETED"]) > testobj.defaultWpDictLen:
         testobj.CallCustomCallBacks("D_MODEL_FLASH_READ_COMPLETED", eventKey, args, processorId)

   @staticmethod
   def CB_WriteCacheFlushed(eventKey, args, processorId):
      """
      Description: Cache Flush Event during Write .
      Parameters: eventKey: Gives registered key of Event
                  args:  None
                  processorId: gives processor Id.
      Returns: None
      Exceptions: None
      """
      testobj = LivetWayPoint.staticObj
      testobj.TF.logger.Info("D_MODEL_DCT_WRITE_CACHE_FLUSHED : Cache Flushed during write")

      # Increment Counter
      testobj.wayPointDefaultDict["D_MODEL_DCT_WRITE_CACHE_FLUSHED"][1] += 1
      # Call custom callbacks if registered.
      if len(testobj.wayPointDefaultDict["D_MODEL_DCT_WRITE_CACHE_FLUSHED"]) > testobj.defaultWpDictLen:
         testobj.CallCustomCallBacks("D_MODEL_DCT_WRITE_CACHE_FLUSHED", eventKey, args, processorId)

   @staticmethod
   def CB_HimssBeforeCmdComplete(eventKey, args, processorId):
      """
      Description: This waypoint is for Flash Write Completion.
      Parameters: eventKey: Gives registered key of Event
                  args:  args[0]--> Cmd Tag
                  processorId: gives processor Id.

      Returns: None
      Exceptions: None
      """
      testobj = LivetWayPoint.staticObj
      testobj.TF.logger.Info("D_MODEL_HIMSS_BEFORECMD_COMPLETE : eventKey=%d, args=%s, processorId=%d"
                       % (eventKey, args, processorId))

      # Increment Counter
      testobj.wayPointDefaultDict["D_MODEL_HIMSS_BEFORECMD_COMPLETE"][1] += 1
      # Call custom callbacks if registered.
      if len(testobj.wayPointDefaultDict["D_MODEL_HIMSS_BEFORECMD_COMPLETE"]) > testobj.defaultWpDictLen:
         testobj.CallCustomCallBacks("D_MODEL_HIMSS_BEFORECMD_COMPLETE", eventKey, args, processorId)