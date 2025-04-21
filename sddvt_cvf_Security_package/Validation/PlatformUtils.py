from __future__ import print_function
from builtins import str
from builtins import range
from builtins import object
"""
################################################################################
# Copyright (c) SanDisk Corp.2013 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# FILE:PlatformUtils.py: Utility to access Test Machine resourses.
#                AUTHOR: Manjunath Badi
################################################################################
#                            CHANGE HISTORY
# 31-07-2017    Histogram feature is added.
################################################################################
Test Algorithm:
1. Collecting command history
2. Creating Histogram based on latency of commands from command history
3. Generating Histogram report for write, read, trim, write0, writeUC and format commands.
"""""

import subprocess
import multiprocessing
import re
import Validation.NVMe.TestFixture as TestFixture
import Core.ValidationError as ValidationError
from  collections import OrderedDict

class PlatformUtils(object):
    def __init__(self):
        pass
# **************************************************************************************************************
# This method is used to get Physical Memory of the Test Machine.
# This method sends Windows dos command systeminfo.
# Param None
# return string
# exception None
# **************************************************************************************************************

    def GetMemoryDetails(self):
        command = subprocess.Popen('systeminfo | findstr /C:"Physical Memory"', stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        result, error = command.communicate()
        return (result.splitlines()[0][27:], result.splitlines()[1][27:])
# **************************************************************************************************************
# This method is used to get IP Address of the Test Machine.
# This method sends Windows dos command ipconfig.
# Param None
# return string
# exception None
# **************************************************************************************************************

    def GetIPAddress(self):
        command = subprocess.Popen('ipconfig | findstr /C:"IPv4 Address. . . . . . . . . . . :"', stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        result, error = command.communicate()
        return (result.split(':')[1].strip())
# **************************************************************************************************************
# This method is used to get Number of CPU Cores of the Test Machine.
# Param None
# return integer
# exception None
# **************************************************************************************************************

    def GetCPUCores(self):
        return multiprocessing.cpu_count()



class Histogram(object):

    def __init__(self,instance, CommandList, CommandRequired=0):
# self.command_List = Commands #Raw command details will be in list of strings( ['',''] ).
        self.selfobj = instance
        self.CommandId = CommandRequired
        #self.Histogram_Format = {'0-99': [0, ], '100-500': [0, ], '501-1000': [0, ], '1001-2000': [0, ], '2001-3000': [0, ], '3001-4000': [0, ], '4001-5000': [0, ], '5001-6000': [0, ], '6001-7000': [0, ], '7001-8000': [0, ], '8001-10000': [0, ], '10001-15000': [0, ], '15001-20000': [0, ], '20000+': [0, ]}
        self.Histogram_Format = OrderedDict([('0-99',[0, ]),('100-500',[0, ]),('501-1000',[0, ]),('1001-2000',[0, ]),('2001-3000',[0, ]),('3001-4000',[0, ]),('4001-5000',[0, ]),('5001-6000',[0, ]),('6001-7000',[0, ]),('7001-8000',[0, ]),('8001-10000',[0, ]),('10001-15000',[0, ]),('15001-20000',[0, ]),('20000+',[0, ])])
        self.SpuriousLatencyCommands = []
        self.TF = TestFixture.TestFixture()
        self.write_command_name = "writedisk"  # command names must be in lower case
        self.read_command_name = "readdisk"
        self.write_zero_command_name = "writezeroes"
        self.trim_command_name = "trim"
        self.Format_command_name = "format"
        self.writeUC_command_name = "writeuncorrectable"
        self.total_Command_count = 0
        self.total_write_commands = 0
        self.total_read_commands = 0
        self.total_writezero_commands = 0
        self.total_trim_commands = 0
        self.total_writeUC_commands = 0
        self.total_Format_commands = 0
        self.Command_Latency = CommandList
        self.Histogram_Dict = self.Get_Histogram()
        self.cvfWriteCommandCount = 0
        self.cvfReadCommandCount = 0
        self.cvfTrimCommandCount = 0
        self.cvfWriteZeroCommandCount = 0
        self.cvfWriteUCCommandCount = 0
        self.cvfFormatCommandCount = 0
        self.CVF_Histogram = OrderedDict()

    def Get_Histogram_Full_Report(self, Destination_Path="C:\\Users\\user\\Desktop\\Histo.txt"):
        with open(Destination_Path, "w+") as FilaHandle:
            import pprint
            pprint.pprint(self.Histogram_Dict, stream=FilaHandle)

    def Histogram_Report(self):
        """Prints Histogram report in test log for all commands."""
        statObj = self.selfobj.vtfContainer.nvme_session.GetStatisticsObj()
        self.CVF_Histogram = statObj.GetCommandLatencyHistogram()
        cvf_Histo = ""
        self.TF.logger.Info("", "##############################################################################")
        self.TF.logger.Info("", "#                            CVF Histogram                                   #")
        self.TF.logger.Info("", "##############################################################################")
        for DICT in list(self.CVF_Histogram.keys()):
            for DICTinDICT in list(self.CVF_Histogram[DICT].keys()):
                cvf_Histo += str(DICTinDICT)+"-"+str(self.CVF_Histogram[DICT][DICTinDICT])+","
            self.TF.logger.Info("", " {}".format(str(cvf_Histo)))
            cvf_Histo = ""
        Histogram_Dict = self.Get_Write_Command_Histogram()
        cvf_Histo = ""
        self.TF.logger.Info("", "##############################################################################")
        self.TF.logger.Info("", "#                            Write Command Histogram                         #")
        self.TF.logger.Info("", "##############################################################################")
        for i in list(self.CVF_Histogram[3].keys()):
            cvf_Histo += str(i)+"-"+str(self.CVF_Histogram[3][i])+","
            self.cvfWriteCommandCount += self.CVF_Histogram[3][i]
        self.TF.logger.Info("", " {}".format(str(cvf_Histo)))
        self.TF.logger.Info("", "##############################################################################")
        for key in list(Histogram_Dict.keys()):
            self.TF.logger.Info("", "{}-{}".format(key, str(Histogram_Dict[key])))
        Histogram_Dict = self.Get_Read_Command_Histogram()
        cvf_Histo = ""
        self.TF.logger.Info("", "##############################################################################")
        self.TF.logger.Info("", "#                            Read Command Histogram                          #")
        self.TF.logger.Info("", "##############################################################################")
        for i in list(self.CVF_Histogram[2].keys()):
            cvf_Histo += str(i)+"-"+str(self.CVF_Histogram[2][i])+","
            self.cvfReadCommandCount += self.CVF_Histogram[2][i]
        self.TF.logger.Info("", " {}".format(str(cvf_Histo)))
        self.TF.logger.Info("", "##############################################################################")
        for key in list(Histogram_Dict.keys()):
            self.TF.logger.Info("", "{}-{}".format(key, str(Histogram_Dict[key])))
        Histogram_Dict = self.Get_write_zero_Command_Histogram()
        cvf_Histo = ""
        self.TF.logger.Info("", "##############################################################################")
        self.TF.logger.Info("", "#                            WriteZeros Command Histogram                    #")
        self.TF.logger.Info("", "##############################################################################")
        for i in list(self.CVF_Histogram[4].keys()):
            cvf_Histo += str(i)+"-"+str(self.CVF_Histogram[4][i])+","
            self.cvfWriteZeroCommandCount += self.CVF_Histogram[4][i]
        self.TF.logger.Info("", "CVF Histogram {}".format(str(cvf_Histo)))
        self.TF.logger.Info("", "##############################################################################")
        for key in list(Histogram_Dict.keys()):
            self.TF.logger.Info("", "{}-{}".format(key, str(Histogram_Dict[key])))
        Histogram_Dict = self.Get_Trim_Command_Histogram()
        cvf_Histo = ""
        self.TF.logger.Info("", "##############################################################################")
        self.TF.logger.Info("", "#                            Trim Command Histogram                          #")
        self.TF.logger.Info("", "##############################################################################")
        for i in list(self.CVF_Histogram[6].keys()):
            cvf_Histo += str(i)+"-"+str(self.CVF_Histogram[6][i])+","
            self.cvfTrimCommandCount += self.CVF_Histogram[6][i]
        self.TF.logger.Info("", "CVF Histogram {}".format(str(cvf_Histo)))
        self.TF.logger.Info("", "##############################################################################")
        for key in list(Histogram_Dict.keys()):
            self.TF.logger.Info("", "{}-{}".format(key, str(Histogram_Dict[key])))
        Histogram_Dict = self.Get_WriteUC_Command_Histogram()
        cvf_Histo = ""
        self.TF.logger.Info("", "##############################################################################")
        self.TF.logger.Info("", "#                            WriteUC Command Histogram                       #")
        self.TF.logger.Info("", "##############################################################################")
        for i in list(self.CVF_Histogram[5].keys()):
            cvf_Histo += str(i)+"-"+str(self.CVF_Histogram[5][i])+","
            self.cvfWriteUCCommandCount += self.CVF_Histogram[5][i]
        self.TF.logger.Info("", "CVF Histogram {}".format(str(cvf_Histo)))
        self.TF.logger.Info("", "##############################################################################")
        for key in list(Histogram_Dict.keys()):
            self.TF.logger.Info("", "{}-{}".format(key, str(Histogram_Dict[key])))
        Histogram_Dict = self.Get_Format_Command_Histogram()
        cvf_Histo = ""
        self.TF.logger.Info("", "##############################################################################")
        self.TF.logger.Info("", "#                            Format Command Histogram                        #")
        self.TF.logger.Info("", "##############################################################################")
        for i in list(self.CVF_Histogram[7].keys()):
            cvf_Histo += str(i)+"-"+str(self.CVF_Histogram[7][i])+","
            self.cvfFormatCommandCount += self.CVF_Histogram[7][i]
        self.TF.logger.Info("", "CVF Histogram {}".format(str(cvf_Histo)))
        self.TF.logger.Info("", "##############################################################################")
        for key in list(Histogram_Dict.keys()):
            self.TF.logger.Info("", "{}-{}".format(key, str(Histogram_Dict[key])))

    def Get_Total_write_Command_Count(self):
        """Returns number of write commands execuited"""
        return self.total_write_commands

    def Get_Total_Read_Command_Count(self):
        """Returns number of read commands execuited"""
        return self.total_read_commands

    def Get_Total_Write_ZeroCommand_Count(self):
        """Returns number of commands execuited"""
        return self.total_writezero_commands

    def Get_Total_Trim_Command_Count(self):
        """Returns number of commands execuited"""
        return self.total_trim_commands

    def Get_Total_write_UC_Command_Count(self):
        """Returns number of commands execuited"""
        return self.total_writeUC_commands

    def Get_Total_Command_Count(self):
        """Returns number of commands execuited"""
        return self.total_Command_count

    def Get_Total_Format_Command_Count(self):
        """Returns number of write commands execuited"""
        return self.total_Format_commands


    def Get_Write_Command_Histogram(self):
        """This method extracts Histogram of all commands from Get_Histogram method , extracts only write command histogram and returns dictionary of write command histogram"""
        write_Histogram_Dict = OrderedDict()
        for bucket in list(self.Histogram_Dict.keys()):
            write_Histogram_Dict[bucket] = [0, ]
            for cmd in self.Histogram_Dict[bucket][1:]:
                if cmd != 0:
                    if cmd.split(" ")[0].lower() in self.write_command_name:
                        write_Histogram_Dict[bucket].append(cmd)
                        write_Histogram_Dict[bucket][0] += 1
                else:
                    break
        if self.CommandId == 1:
            return write_Histogram_Dict
        else:
            temp_Dict = OrderedDict()
            for key, value in list(write_Histogram_Dict.items()):
                temp_Dict[key] = write_Histogram_Dict[key][0]
            return temp_Dict

    def Get_Read_Command_Histogram(self):
        """This method extracts Histogram of all commands from Get_Histogram method , extracts only read command histogram and returns dictionary of read command histogram"""
        read_Histogram_Dict = OrderedDict()
        for bucket in list(self.Histogram_Dict.keys()):
            read_Histogram_Dict[bucket] = [0, ]
            for cmd in self.Histogram_Dict[bucket][1:]:
                if cmd != 0:
                    if cmd.split(" ")[0].lower() in self.read_command_name:
                        read_Histogram_Dict[bucket].append(cmd)
                        read_Histogram_Dict[bucket][0] += 1
                else:
                    break
        if self.CommandId == 1:
            return read_Histogram_Dict409

        else:
            temp_Dict = OrderedDict()
            for key, value in list(read_Histogram_Dict.items()):
                temp_Dict[key] = read_Histogram_Dict[key][0]
            return temp_Dict

    def Get_write_zero_Command_Histogram(self):
        """This method extracts Histogram of all commands from Get_Histogram method , extracts only write_zero command histogram and returns dictionary of write_zero command histogram"""
        write_zero_Histogram_Dict = OrderedDict()
        for bucket in list(self.Histogram_Dict.keys()):
            write_zero_Histogram_Dict[bucket] = [0, ]
            for cmd in self.Histogram_Dict[bucket][1:]:
                if cmd != 0:
                    if cmd.split(" ")[0].lower() in self.write_zero_command_name:
                        write_zero_Histogram_Dict[bucket].append(cmd)
                        write_zero_Histogram_Dict[bucket][0] += 1
                else:
                    break
        if self.CommandId == 1:
            return write_zero_Histogram_Dict
        else:
            temp_Dict = OrderedDict()
            for key, value in list(write_zero_Histogram_Dict.items()):
                temp_Dict[key] = write_zero_Histogram_Dict[key][0]
            return temp_Dict

    def Get_Trim_Command_Histogram(self):
        """This method extracts Histogram of all commands from Get_Histogram method , extracts only Trim command histogram and returns dictionary of Trim command histogram"""
        Trim_Histogram_Dict = OrderedDict()
        for bucket in list(self.Histogram_Dict.keys()):
            Trim_Histogram_Dict[bucket] = [0, ]
            for cmd in self.Histogram_Dict[bucket][1:]:
                if cmd != 0:
                    if cmd.split(" ")[0].lower() in self.trim_command_name:
                        Trim_Histogram_Dict[bucket].append(cmd)
                        Trim_Histogram_Dict[bucket][0] += 1
                else:
                    break
        if self.CommandId == 1:
            return Trim_Histogram_Dict
        else:
            temp_Dict = OrderedDict()
            for key, value in list(Trim_Histogram_Dict.items()):
                temp_Dict[key] = Trim_Histogram_Dict[key][0]
            return temp_Dict

    def Get_WriteUC_Command_Histogram(self):
        """This method extracts Histogram of all commands from Get_Histogram method , extracts only WriteUC command histogram and returns dictionary of WriteUC command histogram"""
        WriteUC_Histogram_Dict = OrderedDict()
        for bucket in list(self.Histogram_Dict.keys()):
            WriteUC_Histogram_Dict[bucket] = [0, ]
            for cmd in self.Histogram_Dict[bucket][1:]:
                if cmd != 0:
                    if cmd.split(" ")[0].lower() in self.writeUC_command_name:
                        WriteUC_Histogram_Dict[bucket].append(cmd)
                        WriteUC_Histogram_Dict[bucket][0] += 1
                else:
                    break
        if self.CommandId == 1:
            return WriteUC_Histogram_Dict
        else:
            temp_Dict = OrderedDict()
            for key, value in list(WriteUC_Histogram_Dict.items()):
                temp_Dict[key] = WriteUC_Histogram_Dict[key][0]
            return temp_Dict

    def Get_Format_Command_Histogram(self):
        """This method extracts Histogram of all commands from Get_Histogram method , extracts only Format command histogram and returns dictionary of Format command histogram"""
        Format_Histogram_Dict = OrderedDict()
        for bucket in list(self.Histogram_Dict.keys()):
            Format_Histogram_Dict[bucket] = [0, ]
            for cmd in self.Histogram_Dict[bucket][1:]:
                if cmd != 0:
                    if cmd.split(" ")[0].lower() in self.Format_command_name:
                        Format_Histogram_Dict[bucket].append(cmd)
                        Format_Histogram_Dict[bucket][0] += 1
                else:
                    break
        if self.CommandId == 1:
            return Format_Histogram_Dict
        else:
            temp_Dict = OrderedDict()
            for key, value in list(Format_Histogram_Dict.items()):
                temp_Dict[key] = Format_Histogram_Dict[key][0]
            return temp_Dict

    def Get_Histogram(self):
            #last_bucket_start_value = 8001.0 24082017
            last_bucket_start_value = 20001.0
            try:
                self.Histogram_Dict = self.Histogram_Format
                for key in list(self.Histogram_Dict.keys()):
                    for item in self.Command_Latency:
                        latency_In_us = item.split("-")[-1]
                        latency_In_ms = float(latency_In_us) / 1000.0
                        #if(key == '8001+'): 24082017
                        if(key == '20000+'):
                            if(latency_In_ms >= last_bucket_start_value):
                                self.Histogram_Dict[key].append(item)
                                self.Histogram_Dict[key][0] += 1
                                self.total_Command_count += 1
                        else:
                            mn, mx = key.split("-")
                            mx = float(mx) + 0.999999999
                            if(latency_In_ms >= float(mn) and latency_In_ms <= float(mx)):
                                self.Histogram_Dict[key].append(item)
                                self.Histogram_Dict[key][0] += 1
                                self.total_Command_count += 1
                return self.Histogram_Dict
            except:
                print("")


    def HistogramVerification(self):
        """This method will verify the cvf histogram and test histogram."""
        funclist = [self.Get_Read_Command_Histogram,self.Get_Write_Command_Histogram,self.Get_write_zero_Command_Histogram,self.Get_WriteUC_Command_Histogram,self.Get_Trim_Command_Histogram,self.Get_Format_Command_Histogram]
        cvfHistoEnumeration = [2,3,4,5,6,7] # NVME command enumerations
        ErrorMessage = ""
        for item in range(len(cvfHistoEnumeration)):
            testHisto = funclist[item]()
            cvfHisto = self.CVF_Histogram[cvfHistoEnumeration[item]]
            for cvfHistogramKey in cvfHisto:
                if cvfHistogramKey == 0:
                    if cvfHisto[cvfHistogramKey] == testHisto['0-99']:
                        pass
                    else:
                        if cvfHistoEnumeration[item] == 2:
                            ErrorMessage += " Read (0-99),"
                        elif cvfHistoEnumeration[item] == 3:
                            ErrorMessage += " Write (0-99),"
                        elif cvfHistoEnumeration[item] == 4:
                            ErrorMessage += " WriteZero (0-99),"
                        elif cvfHistoEnumeration[item] == 5:
                            ErrorMessage += " WriteUC (0-99),"
                        elif cvfHistoEnumeration[item] == 6:
                            ErrorMessage += " Trim (0-99),"
                        elif cvfHistoEnumeration[item] == 7:
                            ErrorMessage += " Format (0-99),"
                if cvfHistogramKey == 1:
                    if cvfHisto[cvfHistogramKey] == testHisto['100-500']:
                        pass
                    else:
                        if cvfHistoEnumeration[item] == 2:
                            ErrorMessage += " Read (100-500),"
                        elif cvfHistoEnumeration[item] == 3:
                            ErrorMessage += " Write (100-500),"
                        elif cvfHistoEnumeration[item] == 4:
                            ErrorMessage += " WriteZero (100-500),"
                        elif cvfHistoEnumeration[item] == 5:
                            ErrorMessage += " WriteUC (100-500),"
                        elif cvfHistoEnumeration[item] == 6:
                            ErrorMessage += " Trim (100-500),"
                        elif cvfHistoEnumeration[item] == 7:
                            ErrorMessage += " Format (100-500),"
                if cvfHistogramKey == 2:
                    if cvfHisto[cvfHistogramKey] == testHisto['501-1000']:
                        pass
                    else:
                        if cvfHistoEnumeration[item] == 2:
                            ErrorMessage += " Read (501-1000),"
                        elif cvfHistoEnumeration[item] == 3:
                            ErrorMessage += " Write (501-1000),"
                        elif cvfHistoEnumeration[item] == 4:
                            ErrorMessage += " WriteZero (501-1000),"
                        elif cvfHistoEnumeration[item] == 5:
                            ErrorMessage += " WriteUC (501-1000),"
                        elif cvfHistoEnumeration[item] == 6:
                            ErrorMessage += " Trim (501-1000),"
                        elif cvfHistoEnumeration[item] == 7:
                            ErrorMessage += " Format (501-1000),"
                if cvfHistogramKey == 3:
                    if cvfHisto[cvfHistogramKey] == testHisto['1001-2000']:
                        pass
                    else:
                        if cvfHistoEnumeration[item] == 2:
                            ErrorMessage += " Read (1001-2000),"
                        elif cvfHistoEnumeration[item] == 3:
                            ErrorMessage += " Write (1001-2000),"
                        elif cvfHistoEnumeration[item] == 4:
                            ErrorMessage += " WriteZero (1001-2000),"
                        elif cvfHistoEnumeration[item] == 5:
                            ErrorMessage += " WriteUC (1001-2000),"
                        elif cvfHistoEnumeration[item] == 6:
                            ErrorMessage += " Trim (1001-2000),"
                        elif cvfHistoEnumeration[item] == 7:
                            ErrorMessage += " Format (1001-2000),"
                if cvfHistogramKey == 4:
                    if cvfHisto[cvfHistogramKey] == testHisto['2001-3000']:
                        pass
                    else:
                        if cvfHistoEnumeration[item] == 2:
                            ErrorMessage += " Read (2001-3000),"
                        elif cvfHistoEnumeration[item] == 3:
                            ErrorMessage += " Write (2001-3000),"
                        elif cvfHistoEnumeration[item] == 4:
                            ErrorMessage += " WriteZero (2001-3000),"
                        elif cvfHistoEnumeration[item] == 5:
                            ErrorMessage += " WriteUC (2001-3000),"
                        elif cvfHistoEnumeration[item] == 6:
                            ErrorMessage += " Trim (2001-3000),"
                        elif cvfHistoEnumeration[item] == 7:
                            ErrorMessage += " Format (2001-3000),"
                if cvfHistogramKey == 5:
                    if cvfHisto[cvfHistogramKey] == testHisto['3001-4000']:
                        pass
                    else:
                        if cvfHistoEnumeration[item] == 2:
                            ErrorMessage += " Read (3001-4000),"
                        elif cvfHistoEnumeration[item] == 3:
                            ErrorMessage += " Write (3001-4000),"
                        elif cvfHistoEnumeration[item] == 4:
                            ErrorMessage += " WriteZero (3001-4000),"
                        elif cvfHistoEnumeration[item] == 5:
                            ErrorMessage += " WriteUC (3001-4000),"
                        elif cvfHistoEnumeration[item] == 6:
                            ErrorMessage += " Trim (3001-4000),"
                        elif cvfHistoEnumeration[item] == 7:
                            ErrorMessage += " Format (3001-4000),"
                if cvfHistogramKey == 6:
                    if cvfHisto[cvfHistogramKey] == testHisto['4001-5000']:
                        pass
                    else:
                        if cvfHistoEnumeration[item] == 2:
                            ErrorMessage += " Read (4001-5000),"
                        elif cvfHistoEnumeration[item] == 3:
                            ErrorMessage += " Write (4001-5000),"
                        elif cvfHistoEnumeration[item] == 4:
                            ErrorMessage += " WriteZero (4001-5000),"
                        elif cvfHistoEnumeration[item] == 5:
                            ErrorMessage += " WriteUC (4001-5000),"
                        elif cvfHistoEnumeration[item] == 6:
                            ErrorMessage += " Trim (4001-5000),"
                        elif cvfHistoEnumeration[item] == 7:
                            ErrorMessage += " Format (4001-5000),"
                if cvfHistogramKey == 7:
                    if cvfHisto[cvfHistogramKey] == testHisto['5001-6000']:
                        pass
                    else:
                        if cvfHistoEnumeration[item] == 2:
                            ErrorMessage += " Read (5001-6000),"
                        elif cvfHistoEnumeration[item] == 3:
                            ErrorMessage += " Write (5001-6000),"
                        elif cvfHistoEnumeration[item] == 4:
                            ErrorMessage += " WriteZero (5001-6000),"
                        elif cvfHistoEnumeration[item] == 5:
                            ErrorMessage += " WriteUC (5001-6000),"
                        elif cvfHistoEnumeration[item] == 6:
                            ErrorMessage += " Trim (5001-6000),"
                        elif cvfHistoEnumeration[item] == 7:
                            ErrorMessage += " Format (5001-6000),"
                if cvfHistogramKey == 8:
                    if cvfHisto[cvfHistogramKey] == testHisto['6001-7000']:
                        pass
                    else:
                        if cvfHistoEnumeration[item] == 2:
                            ErrorMessage += " Read (6001-7000),"
                        elif cvfHistoEnumeration[item] == 3:
                            ErrorMessage += " Write (6001-7000),"
                        elif cvfHistoEnumeration[item] == 4:
                            ErrorMessage += " WriteZero (6001-7000),"
                        elif cvfHistoEnumeration[item] == 5:
                            ErrorMessage += " WriteUC (6001-7000),"
                        elif cvfHistoEnumeration[item] == 6:
                            ErrorMessage += " Trim (6001-7000),"
                        elif cvfHistoEnumeration[item] == 7:
                            ErrorMessage += " Format (6001-7000),"
                if cvfHistogramKey == 9:
                    if cvfHisto[cvfHistogramKey] == testHisto['7001-8000']:
                        pass
                    else:
                        if cvfHistoEnumeration[item] == 2:
                            ErrorMessage += " Read (7001-8000),"
                        elif cvfHistoEnumeration[item] == 3:
                            ErrorMessage += " Write (7001-8000),"
                        elif cvfHistoEnumeration[item] == 4:
                            ErrorMessage += " WriteZero (7001-8000),"
                        elif cvfHistoEnumeration[item] == 5:
                            ErrorMessage += " WriteUC (7001-8000),"
                        elif cvfHistoEnumeration[item] == 6:
                            ErrorMessage += " Trim (7001-8000),"
                        elif cvfHistoEnumeration[item] == 7:
                            ErrorMessage += " Format (7001-8000),"
                if cvfHistogramKey == 10:
                    if cvfHisto[cvfHistogramKey] == testHisto['8001-10000']:
                        pass
                    else:
                        if cvfHistoEnumeration[item] == 2:
                            ErrorMessage += " Read (8001-10000),"
                        elif cvfHistoEnumeration[item] == 3:
                            ErrorMessage += " Write (8001-10000),"
                        elif cvfHistoEnumeration[item] == 4:
                            ErrorMessage += " WriteZero (8001-10000),"
                        elif cvfHistoEnumeration[item] == 5:
                            ErrorMessage += " WriteUC (8001-10000),"
                        elif cvfHistoEnumeration[item] == 6:
                            ErrorMessage += " Trim (8001-10000),"
                        elif cvfHistoEnumeration[item] == 7:
                            ErrorMessage += " Format (8001-10000),"
                if cvfHistogramKey == 11:
                    if cvfHisto[cvfHistogramKey] == testHisto['10001-15000']:
                        pass
                    else:
                        if cvfHistoEnumeration[item] == 2:
                            ErrorMessage += " Read (10001-15000),"
                        elif cvfHistoEnumeration[item] == 3:
                            ErrorMessage += " Write (10001-15000),"
                        elif cvfHistoEnumeration[item] == 4:
                            ErrorMessage += " WriteZero (10001-15000),"
                        elif cvfHistoEnumeration[item] == 5:
                            ErrorMessage += " WriteUC (10001-15000),"
                        elif cvfHistoEnumeration[item] == 6:
                            ErrorMessage += " Trim (10001-15000),"
                        elif cvfHistoEnumeration[item] == 7:
                            ErrorMessage += " Format (10001-15000),"
                if cvfHistogramKey == 12:
                    if cvfHisto[cvfHistogramKey] == testHisto['15001-20000']:
                        pass
                    else:
                        if cvfHistoEnumeration[item] == 2:
                            ErrorMessage += " Read (15001-20000),"
                        elif cvfHistoEnumeration[item] == 3:
                            ErrorMessage += " Write (15001-20000),"
                        elif cvfHistoEnumeration[item] == 4:
                            ErrorMessage += " WriteZero (15001-20000),"
                        elif cvfHistoEnumeration[item] == 5:
                            ErrorMessage += " WriteUC (15001-20000),"
                        elif cvfHistoEnumeration[item] == 6:
                            ErrorMessage += " Trim (15001-20000),"
                        elif cvfHistoEnumeration[item] == 7:
                            ErrorMessage += " Format (15001-20000),"
                if cvfHistogramKey == 12:
                    if cvfHisto[cvfHistogramKey] == testHisto['20000+']:
                        pass
                    else:
                        if cvfHistoEnumeration[item] == 2:
                            ErrorMessage += " Read (20000+),"
                        elif cvfHistoEnumeration[item] == 3:
                            ErrorMessage += " Write (20000+),"
                        elif cvfHistoEnumeration[item] == 4:
                            ErrorMessage += " WriteZero (20000+),"
                        elif cvfHistoEnumeration[item] == 5:
                            ErrorMessage += " WriteUC (20000+),"
                        elif cvfHistoEnumeration[item] == 6:
                            ErrorMessage += " Trim (20000+),"
                        elif cvfHistoEnumeration[item] == 7:
                            ErrorMessage += " Format (20000+),"
        return ErrorMessage



class CommandLatencyHistogram(Histogram):
    """ Thsi  class will create histogram of IO and format commands by taking the latency of command instead of command history."""
    def __init__(self, commandList):
        """ This class will accept the list of commands sent with send immediate ex: 'command :ID - Latency' """
        self.TF = TestFixture.TestFixture()
        self.Commands = commandList
        self.CommandId = 0
        #self.Histogram_Format = {'0-10': [0, ], '10-20': [0, ], '20-60': [0, ], '60+': [0, ]}
        self.Histogram_Format = OrderedDict([('0-10',[0, ]),('10-20',[0, ]),('20-60',[0, ]),('60+',[0, ])])
        self.write_command_name = "writedisk"  # command names must be in lower case
        self.read_command_name = "readdisk"
        self.write_zero_command_name = "writezeroes"
        self.trim_command_name = "trim"
        self.Format_command_name = "format"
        self.writeUC_command_name = "writeuncorrectable"
        self.Non_Considered_Commands = [0, ]
        self.SpuriousLatencyCommands = []
        self.total_Command_count = 0
        self.total_write_commands = 0
        self.total_read_commands = 0
        self.total_writezero_commands = 0
        self.total_trim_commands = 0
        self.total_writeUC_commands = 0
        self.total_Format_commands = 0
        self.Histogram_Dict = self.Get_Histogram()

        #self.TF.logger.Info("*********************************************************** Spurious Commands End ***********************************************************")

    def PrintSpuriousCommands(self):
        commands = 0
        self.TF.logger.Info("*********************************************************** Spurious Commands Start ***********************************************************")
        for commands in self.Histogram_Dict['60+'][1:]:
            commands += 1
            self.TF.logger.Info(str(commands))
        if commands == 0:
            self.TF.logger.Info("No Spurious commmands found")
        self.TF.logger.Info("*********************************************************** Spurious Commands End ***********************************************************")
        return commands

    def Get_Histogram(self):
        #last_bucket_start_value = 8001.0 24082017
        last_bucket_start_value = 61.0
        try:
            self.Histogram_Dict = self.Histogram_Format
            for key in list(self.Histogram_Dict.keys()):
                for item in self.Commands:
                    latency_In_us = item.split("-")[-1].strip(" ")
                    latency_In_ms = float(latency_In_us) / 1000000.0
                    #if(key == '8001+'): 24082017
                    if(key == '60+'):
                        if(latency_In_ms >= last_bucket_start_value):
                            self.Histogram_Dict[key].append(item)
                            self.Histogram_Dict[key][0] += 1
                            self.total_Command_count += 1
                    else:
                        mn, mx = key.split("-")
                        mx = float(mx) + 0.999999999
                        if(latency_In_ms >= float(mn) and latency_In_ms <= float(mx)):
                            self.Histogram_Dict[key].append(item)
                            self.Histogram_Dict[key][0] += 1
                            self.total_Command_count += 1
            return self.Histogram_Dict
        except:
            print("")


    def Histogram_Report(self):
        """Prints Histogram report in test log for all commands."""
        Histogram_Dict = self.Get_Write_Command_Histogram()
        self.TF.logger.Info("", "##############################################################################")
        self.TF.logger.Info("", "#                            Write Command Histogram                         #")
        self.TF.logger.Info("", "##############################################################################")
        for key in list(Histogram_Dict.keys()):
            self.TF.logger.Info("", "{}-{}".format(key, str(Histogram_Dict[key])))
        Histogram_Dict = self.Get_Read_Command_Histogram()
        self.TF.logger.Info("", "##############################################################################")
        self.TF.logger.Info("", "#                            Read Command Histogram                          #")
        self.TF.logger.Info("", "##############################################################################")
        for key in list(Histogram_Dict.keys()):
            self.TF.logger.Info("", "{}-{}".format(key, str(Histogram_Dict[key])))
        Histogram_Dict = self.Get_write_zero_Command_Histogram()
        self.TF.logger.Info("", "##############################################################################")
        self.TF.logger.Info("", "#                            WriteZeros Command Histogram                    #")
        self.TF.logger.Info("", "##############################################################################")
        for key in list(Histogram_Dict.keys()):
            self.TF.logger.Info("", "{}-{}".format(key, str(Histogram_Dict[key])))
        Histogram_Dict = self.Get_Trim_Command_Histogram()
        self.TF.logger.Info("", "##############################################################################")
        self.TF.logger.Info("", "#                            Trim Command Histogram                          #")
        self.TF.logger.Info("", "##############################################################################")
        for key in list(Histogram_Dict.keys()):
            self.TF.logger.Info("", "{}-{}".format(key, str(Histogram_Dict[key])))
        Histogram_Dict = self.Get_WriteUC_Command_Histogram()
        self.TF.logger.Info("", "##############################################################################")
        self.TF.logger.Info("", "#                            WriteUC Command Histogram                       #")
        self.TF.logger.Info("", "##############################################################################")
        for key in list(Histogram_Dict.keys()):
            self.TF.logger.Info("", "{}-{}".format(key, str(Histogram_Dict[key])))
        Histogram_Dict = self.Get_Format_Command_Histogram()
        self.TF.logger.Info("", "##############################################################################")
        self.TF.logger.Info("", "#                            Format Command Histogram                        #")
        self.TF.logger.Info("", "##############################################################################")
        for key in list(Histogram_Dict.keys()):
            self.TF.logger.Info("", "{}-{}".format(key, str(Histogram_Dict[key])))



if __name__ == '__main__':
    obj = PlatformUtils()
    memInfo = obj.GetMemoryDetails()
    print(memInfo)
