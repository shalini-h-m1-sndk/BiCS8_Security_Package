"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                :
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : CMD23_UT01_AllowedCommands.py
# DESCRIPTION                    :
# PRERQUISTE                     : CMD23_UT04_CMD20_ReadVerify,CMD23_UT05_CMD20Write
# STANDALONE EXECUTION           : No. It is an utility script.
# TEST ARGUMENTS                 : AllowedCommand, Cmd20Variables
# AUTHOR [Referred Scripter/CTF] : Sushmitha P.S
# REVIEWED BY                    : Sivagurunathan
# DATE                           : 29-May-2024
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
    from builtins import *

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

# SDDVT - Dependent TestCases
import CMD23_UT04_CMD20_ReadVerify as CMD20ReadVerify
import CMD23_UT05_CMD20Write as CMD20Write

# Global Variables

# Testcase Utility Class - Begins

class CMD23_UT01_AllowedCommands(customize_log):
    def __init__(self, VTFContainer):
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
        self.vtfContainer = VTFContainer
        self.currCfg = Configuration.ConfigurationManagerInitializer.ConfigurationManager.currentConfiguration
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
        self.__sectorsPerMetaBlock = 0x400

        self.__cmd20ReadVerfiy = CMD20ReadVerify.CMD23_UT04_CMD20_ReadVerify(self.vtfContainer)
        self.__cmd20Write = CMD20Write.CMD23_UT05_CMD20Write(self.vtfContainer)

    # Testcase Utility Logic - Starts

    def Run(self, AllowedCommand = 0, Cmd20Variables = None):

        """
        Name : Run

        AllowedCommand = 0:
            STEP 1 : # Call Utility_CMD20_Write
            STEP 2 : # Call Utility_CMD20_ReadVerify
        AllowedCommand = 1:
            STEP 3 : # Do Single Write from Lba_of_first_AU to 0x100
            STEP 4 : # Do Single Read from Lba_of_first_AU to 0x100
        AllowedCommand = 2:
            STEP 5 : # Call Utility_CMD20_ReadVerify
            STEP 6 : # Do Single Write from Lba_of_first_AU to 0x100
        AllowedCommand = 2:
            STEP 7 : Call Utility_CMD20_Write
            STEP 8 : Call Utility_CMD20_ReadVerify
            STEP 9 : Enable Temp.WP
            STEP 10 : Call Utility_CMD20_ReadVerify
            STEP 11 : Enable Not Temp.WP
            STEP 12 :  Call Utility_CMD20_Write, DataType 2
            STEP 13 :  Call Utility_CMD20_ReadVerify
        AllowedCommand = 4:
            STEP 14 :  GET CID
            STEP 15 :  GET CSD
            STEP 16 :  GET SCR
            STEP 17 :  GET SD STATUS
        AllowedCommand = 5:
            STEP 18 : CALL Script Utility_CMD20_Write
            STEP 19 : ACMD-22
            STEP 20 : Call Script Utility_CMD20_ReadVerify
        AllowedCommand == 6:
                      # Set Bus width to 1
            STEP 21 : Check for globalCPRM == 'Secure', Yes
            STEP 22 : GET SD STATUS
            STEP 23 : Secure Write from startLba = 0 to Transfer Length = 0x10, Selector 0
            STEP 24 : Secure Read, from startLba = 0 to Transfer Length = 0x10, Selector 0
            STEP 25 : SECURE READ MKB, Selector 0
            STEP 26 : Secure Erase, from startLba = 0 to Transfer Length = 0x10, Selector 0
            STEP 27 : Secure Read from startLba = 0 to Transfer Length = 0x10, Selector 0

        """
        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Utility Execution Started " + "-" * 20 + "\n")

        if(Cmd20Variables == None):
            Cmd20Variables = self.__cmd20Variables.Run()

        Lba_of_first_AU = Cmd20Variables['Lba_of_first_AU']

        if AllowedCommand == 0:
            # Call Utility_CMD20_Write
            WriteType = 12
            StartBlock = Cmd20Variables['Lba_of_first_AU']
            BlockCount = 0x100
            BlockSize = 0x200
            DataType = 1
            self.__cmd20Write.Run( WriteType = WriteType, StartBlock=StartBlock, BlockCount=BlockCount, DataType=DataType, cmd20variables = Cmd20Variables, usePreDefBlkCount = True)
            #Set the ReadType = All Zero
            ReadType = 0
            #Call Utility_CMD20_ReadVerify
            self.__cmd20ReadVerfiy.Run(StartBlock=StartBlock, BlockCount=BlockCount, DataType=ReadType, usePreDefBlkCount = True)

        if AllowedCommand == 1:
            BlockCount = 0x100
            #Set DataType as Incremental
            DataType = 2
            #Do Single Write from Lba_of_first_AU to 0x100
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###AllowedCommands [INFO]: Single block Write with StartLba: 0x%X, BlockCount: 0x%X, Pattern:0x%X\n"%(Lba_of_first_AU,BlockCount,DataType))
            self.__dvtLib.WriteWithFPGAPattern(StartLba = Lba_of_first_AU, blockCount = BlockCount, SingleWrite =  True, pattern=DataType)
            #Do Single Read from Lba_of_first_AU to 0x100
            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###AllowedCommands [INFO]: Single block Read with StartLba: 0x%X, BlockCount: 0x%X, Pattern:0x%X\n"%(Lba_of_first_AU,BlockCount,DataType))
            self.__dvtLib.ReadWithFPGAPattern(StartLba = Lba_of_first_AU, blockCount = BlockCount, SingleRead =  True, pattern=DataType)

        if AllowedCommand == 2:
            #Do Single Write from Lba_of_first_AU to 0x100
            Erase = 1
            self.__cmd20ReadVerfiy.Run( StartBlock=Lba_of_first_AU, BlockCount=0x100, DataType=0)

        if AllowedCommand == 3:
            #Call Utility_CMD20_Write
            self.__cmd20Write.Run(cmd20variables=Cmd20Variables)

            #Call Utility_CMD20_ReadVerify
            self.__cmd20ReadVerfiy.Run( StartBlock=StartBlock,
                                      BlockCount=BlockCount,
                                      DataType=ReadType)

            #Enable Temp.WP
            self.__sdCmdObj.PutCardInWriteProtectMode(wpMode = "TMP_WRITE_PROTECT")

            # Do Multiple Write from Lba_of_first_AU
            BlockCount = 0x100

            #Set DataType as Constant
            DataType = 4

            self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###AllowedCommands [INFO]: Multiple block Write with StartLba: 0x%X, BlockCount: 0x%X, Pattern:0x%X\n"%(Lba_of_first_AU,BlockCount,DataType))
            self.__dvtLib.WriteWithFPGAPattern(StartLba =Lba_of_first_AU, blockCount = BlockCount, SingleWrite =  False, pattern=DataType)
            # Call Utility_CMD20_ReadVerify
            try:
                self.__cmd20ReadVerfiy.Run( StartBlock=Lba_of_first_AU, BlockCount=0x100, DataType=0)
            except:
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "FAILED As Expected")
            else:
                raise ValidationError.TestFailError(self.fn, "__cmd20ReadVerfiy Failed as expected didn't occur")

            self.__sdCmdObj.RemoveCardFromWriteProtectMode(wpMode = "TMP_WRITE_PROTECT") #Enable Not Temp.WP

            DataType = 2 #Set DataType as Incremental

            #Call Utility_CMD20_Write, DataType 2
            self.__cmd20Write.Run( WriteType=0, StartBlock=0x0,
                                 BlockCount=0x1,
                                 DataType=DataType,cmd20variables=Cmd20Variables)

            self.__cmd20ReadVerfiy.Run( StartBlock=0x0, BlockCount = 0x1, DataType = DataType)  # Call Utility_CMD20_ReadVerify

        if AllowedCommand == 4:

            # GET CID
            self.__sdCmdObj.GetCID()

            # GET CSD
            self.__sdCmdObj.GetCSD()

            # GET SCR
            self.__dvtLib.GET_SCR_Reg_Values()

            # GET SD STATUS
            self.__dvtLib.GetSDStatus()

        if AllowedCommand == 5:

            # CALL Script Utility_CMD20_Write
            self.__cmd20Write.Run( WriteType=0, StartBlock=0x0,
                                 BlockCount=0x1,
                                 DataType=1,cmd20variables=Cmd20Variables)
            # ACMD-22
            self.__sdCmdObj.ACmd22()

            # Call Script Utility_CMD20_ReadVerify
            self.__cmd20ReadVerfiy.Run( StartBlock = 0x4000, BlockCount = 0x100, DataType = 1, BlockSize = 0x200)

        if AllowedCommand == 6:
            # Set Bus width to 1
            self.__dvtLib.SetBusWidth(1)
            # Check for globalCPRM == 'Secure', Yes
            if self.__config.get('globalCPRM') == 'Secure':
                SRW_CARD_SLOT = 1
                # GET SD STATUS
                self.__dvtLib.GetSDStatus()

                # Secure Write from startLba = 0 to BlockCount = 0x10, Selector 0
                Selector = 0
                Signature = False
                BlockCount = 0x10
                StartBlock = 0x0
                authentication = True
                writeDataBuffer =ServiceWrap.Buffer.CreateBuffer(0x10)
                writeDataBuffer.Fill("0x01")
                self.__sdCmdObj.SecureEnable(True)
                self.__sdCmdObj.SetSelector(0)
                blockCount = 0x10
                #Constant DataType
                DataType = 4

                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###SD3CMD2312_Utility_AllowedCommands [INFO]: Secure Write StartBlock: 0x%X, BlockCount: 0x%X, Pattern:0x%X\n"%(StartBlock,BlockCount,DataType))
                self.__dvtLib.SecureWrite(cardslot = SRW_CARD_SLOT, StartBlock = StartBlock, BlockCount = BlockCount,
                                         writeDataBuffer=writeDataBuffer,
                                         selectorValue = Selector,
                                         enableSignature = Signature,
                                         authentication = authentication)
                #Secure Read, from startLba = 0 to Transfer Length = 0x10, Selector 0
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###SD3CMD2312_Utility_AllowedCommands [INFO]: Secure Read StartBlock: 0x%X, BlockCount: 0x%X, Pattern:0x%X\n"%(StartBlock,BlockCount,DataType))
                self.__dvtLib.SecureRead(cardslot = SRW_CARD_SLOT, StartBlock = StartBlock, BlockCount = BlockCount,
                                         writeDataBuffer=writeDataBuffer,
                                         selectorValue = Selector,
                                         enableSignature = Signature,
                                         authentication = authentication)
                #SECURE READ MKB, Selector 0
                BlockCount = 0x80
                StartBlock = 0x0
                try:
                    self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###SD3CMD2312_Utility_AllowedCommands [INFO]: Secure Read MKB: 0x%X, BlockCount: 0x%X, Pattern:0x%X\n"%(StartBlock,BlockCount))
                    self.__dvtLib.ReadMKBFile(cardslot = SRW_CARD_SLOT, BlockCount = BlockCount,
                                             StartBlock = StartBlock,
                                             selector=0)
                except:
                    self.errorLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###SD3CMD2312_Utility_AllowedCommands [INFO]: Read MKB file:[%d] with startBlkAddr:0x%X ---- FAILED as Expected\n"%(Selector, StartBlock))
                else:
                    raise ValidationError.TestFailError(self.fn, "###SD3CMD2312_Utility_AllowedCommands [INFO]: Read MKB file:[%d] with startBlkAddr:0x%X ---- Failed with unexpected error\n"%(Selector, StartBlock))

                #Secure Erase, from startLba = 0 to Transfer Length = 0x10, Selector 0
                BlockCount = 0x10
                StartBlock = 0x0
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "[SD3CMD2312_Utility_AllowedCommands] Secure Erase Lba: 0x%X sector Count: 0x%X selector: 0"%(StartBlock, BlockCount))
                self.__dvtLib.SecureErase(cardslot = SRW_CARD_SLOT, StartBlock = StartBlock, BlockCount = BlockCount,
                                         selectorValue = Selector,
                                         authentication = authentication)
                #Secure Read from startLba = 0 to Transfer Length = 0x10, Selector 0
                StartBlock = 0x0
                BlockCount = 0x10
                ExpectedDataBuffer =  ServiceWrap.Buffer.CreateBuffer(0x10)
                ExpectedDataBuffer.Fill("0x00")
                self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "###SD3CMD2312_Utility_AllowedCommands [INFO]: Secure Read StartBlock: 0x%X, BlockCount: 0x%X.\n"%(StartBlock,BlockCount))
                self.__dvtLib.SecureRead(cardslot = SRW_CARD_SLOT, StartBlock = StartBlock, BlockCount = BlockCount,
                                         writeDataBuffer=ExpectedDataBuffer,
                                         selectorValue = Selector,
                                         enableSignature = Signature,authentication = authentication)

        self.infoLog(self.fn, currentframe().f_lineno, sys._getframe().f_code.co_name, "-" * 20 + "  Utility Execution Completed " + "-" * 20 + "\n")
        return 0

    #End of Run function
#End of AllowedCommands

    # Testcase Utility Logic - Ends

# Testcase Utility Class - Ends