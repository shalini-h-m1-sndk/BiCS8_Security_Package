
"""
################################################################################
# Copyright (c) SanDisk Corp.2013 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# FILE:DPAModelLib.py: Command Utility Library.
# AUTHOR: Balraj


1. Create Xplorer session.
2. Create NVMe session.
3. Update Json file for Xplorer input.
4. Start info recording.
5. Execute any commands.
6. Stop info recording.
7. Stop session.
8. Collect the event from xplorer portal().
9. Using that to trigger events in Shmoo.

################################################################################
"""
from __future__ import print_function

from builtins import str
from builtins import zip
from builtins import object
import sys, os, time, shutil, datetime, random, string, subprocess, csv
import json
from array import *

import CTFServiceWrapper as ServiceWrap
import NVMeCMDWrapper as NVMeWrap
import xPlorerCMDWrapper as xPlorerWrap


class ugsd_conf(object):

    def conf():
        return {
            "bootDelay": 0,
            "gpio":
            {
                    "lines":
                    [
                            {
                                    "signal":
                                    {
                                            "pulseCount": 1,
                                            "durationHigh": 10000000,
                                            "durationLow": 10000000
                                    }
                            },
                            {
                                    "signal":
                                    {
                                            "pulseCount": 1,
                                            "durationHigh": 10000000,
                                            "durationLow": 10000000
                                    }
                            }
                    ]
            },
            "triggerConditions": [],
        }


    def event():
        return {
                    "event": None,
                    "behaviour": None,
                }

    PATH = r"C:\\xTools\\app\\xplorer\\"

    EVENT_FORMAT = {
        'SOURCE_POS': 0,
        'SUBSOURCE_POS': 1,
        'FW': 'source::subSource::thread::mapping::value',  # example: "FW::0::2::name::0x12ab"
        'HW': 'source::subSource::thread::mapping::value',  # example: "HW::CAP::3::name:0x12ab"
    }


class Ugsd(object):

    def  __init__(self, seed, filecode, kwargs):
        self.seed = seed
        self.filecode = filecode
        self.kwargs = kwargs

        if(kwargs.get("delay_fixed") != '0'):
            kwargs['delayconst'] = kwargs.get("delay_fixed")
        elif(kwargs.get("shmoo_delay_fixed") != '0'):
            kwargs['delayconst'] = kwargs.get("shmoo_delay_fixed")
        else:
            kwargs['delaymax'] = kwargs['random_delay_max'] or kwargs['random_delay_min']
            if kwargs['delaymax'] < kwargs['random_delay_min']:
                raise Exception('Delay max should be greater than delay min')
            kwargs['delayconst'] = self.seed.randint(int(kwargs['random_delay_min']), int(kwargs['delaymax']))

        kwargs['cycleslno'] = 0

    def load_conf_template(self):
        C = ugsd_conf()
        conf_base = C.conf()
        eventList = (self.kwargs['events']).split(";;")
        for i in eventList:
            #i = self.kwargs['events']
            event_temp = C.event()
            event_temp['event'] = self.event_builder(i)
            delay = self.kwargs['delayconst'] ###############  + 2 * self.kwargs['cycleSlno']    #self.kwargs['delayShmoo']
            event_temp['behaviour'] = {
                "skipCount": int(self.kwargs['skipcount']),
                "delay": int(delay),
                "mode": 0,
                "timeout": int(self.kwargs['timeout']),
            }
            conf_base['triggerConditions'].append(event_temp)

        #Assing mode=1 for 2nd event, required in case of Nested
        event_temp['behaviour']['mode'] = int(self.kwargs["mode"])

        #if only 1 event is specified, generate a dummy 2nd event with mode=0, skipcount=0
        if len(conf_base['triggerConditions']) == 1:
            event_1 = C.event()
            event_1['event'] = event_temp['event']
            event_1['behaviour'] = {
                "skipCount": int(self.kwargs['skipcount']),
                "delay": int(delay),
                "mode": 3,
                "timeout": int(self.kwargs['timeout']),
            }

            #conf_base['triggerConditions'].append(conf_base['triggerConditions'][0])
            conf_base['triggerConditions'].append(event_1)
            conf_base['triggerConditions'][1]['behaviour']['mode'] = 0
            conf_base['triggerConditions'][1]['behaviour']['skipCount'] = 0

        if self.kwargs.get('measurement'):
            conf_base['triggerConditions'][0]['behaviour']['mode'] = 1

        if self.kwargs.get('stopevent'):
            conf_base['stopCondition'] = {'event': self.event_builder(self.kwargs['stopevent'])}

        if self.kwargs.get('failureevent'):
            conf_base['failCondition'] = {'event': self.event_builder(self.kwargs['failureevent'])}

        if self.kwargs.get('durationlow'):
            conf_base['gpio']['lines'][0]['signal']['durationLow'] = int(self.kwargs['durationlow'])
            conf_base['gpio']['lines'][1]['signal']['durationLow'] = int(self.kwargs['durationlow'])

        if self.kwargs.get('durationhigh'):
            conf_base['gpio']['lines'][0]['signal']['durationHigh'] = int(self.kwargs['durationhigh'])
            conf_base['gpio']['lines'][1]['signal']['durationHigh'] = int(self.kwargs['durationhigh'])

        self.conf = conf_base

    def write_conf(self):
        code = self.filecode
        try:
            os.makedirs(os.path.split(C.PATH)[0])
        except OSError:
            pass
        filename = C.PATH
        with open(filename, mode='w+') as conf_file:
            conf_file.write(json.dumps(self.conf, indent=4))
        return filename

    def createJson(self, path = ""):
        if path != "":
            C.PATH = path
        self.load_conf_template()
        file_name = self.write_conf()
        self.kwargs['cycleslno'] = self.kwargs['cycleslno'] + 1
        return file_name

    @staticmethod
    def event_builder(col_sep):
        info = col_sep.split('::')

        # workaround for CTF bug - always returns lower case of string.
        # Source must be in upper
        info[C.EVENT_FORMAT['SOURCE_POS']] = info[C.EVENT_FORMAT['SOURCE_POS']].upper()
        info[C.EVENT_FORMAT['SUBSOURCE_POS']] = info[C.EVENT_FORMAT['SUBSOURCE_POS']].upper()

        source = info[C.EVENT_FORMAT['SOURCE_POS']]
        format = C.EVENT_FORMAT[source].split('::')
        if len(format) != len(info):
            raise Exception('Check Ugsd event format')
        event = dict(list(zip(format, info)))
        for (key, value) in list(event.items()):
            try:
                event[key] = int(value)
            except:
                pass
        return event

class XplorerFrame(object):

    #readBuffer = ServiceWrap.Buffer.CreateBuffer(1)
    def __init__(self):#
        self.xPlorerStart = False
        self.xPlorerGrid = False
        self.loggerName = ""

    def CreateNVMeSession(self, test_log_file_name):
        "Create NVMe Session"
        #self.logger.Info("","Create NVMe session INIT Started")
        self.loggerName = test_log_file_name
        logLevelCTF = ServiceWrap.DebugLevel.LOG_LEVEL_INFO
        enableConsoleLog = True
        countLogLine = 10000
        countLogFile = 100
        self.logger = ServiceWrap.CTFLogger(test_log_file_name,logLevelCTF,enableConsoleLog, countLogLine, countLogFile)
        ctf_params = dict()
        ctf_params["adapter_index"] =  str(0)
        ctf_params["log_file_path"] = test_log_file_name
        ctf_params["log_level"] = "INFO"

        otherHw = dict()
        otherHw["SerialCommunication"] = "HIDAndCOMPorts"
        otherHw["Utility"] = "INFORMER"
        driver = ServiceWrap.DRIVER_TYPE.SD_NVMe
        self.nvme_session = ServiceWrap.Session.GetSessionObject(ServiceWrap.NVMe_Protocol, driver, otherHw, ctf_params)
        self.configParser = self.nvme_session.GetConfigInfo()
        #self.configParser.SetValue("hal", "")
        self.configParser.SetValue("sector_size_in_bytes", 4096)
        self.configParser.SetValue("enable_automatic_io_queue_creation", 1)
        self.configParser.SetValue("datatracking_enabled", 0)
        self.configParser.SetValue("enable_auto_generate_buffer", 1)
        self.configParser.SetValue("data_tracking_auto_init", 1)
        self.configParser.SetValue("skip_commands_during_device_init", 1)
        self.configParser.SetValue("is_fpga", 0)
        self.configParser.SetValue("enable_GPIO", 1)
        self.configParser.SetValue("enable_cp211x_gpio", 1)
        """
        If need to set config value use ==> self.configParser.SetValue("skip_commands_during_device_init",0)
        If need to get config value use ==> self.configParser.GetValue('msix_and_core_config_for_multiple_qs',"0")[0]

        """
        try:
            self.nvme_session.Init()
        except (ServiceWrap.ALL_EXCEPTIONS, ServiceWrap.ConfigException) as ex:
            print(ex.GetFailureDescription())

        self.logger.Info("","NVMe session INIT Completed")

    def checkInformerConfiguration(self):

        # xPlorerUse = True
        self.logger.Info("Started informer Configuration Setup on xPlorer")

        try:
            informer_ugsd_events = self.configParser.GetValue("utility", "informer_ugsd_events","0")[0]
            informer_ugsd_required = self.configParser.GetValue("utility", "informer_ugsd_required","0")[0]
            informer_ugsd_timeout = self.configParser.GetValue("utility", "informer_ugsd_timeout","0")[0]
            informer_ugsd_delay_fixed = self.configParser.GetValue("utility", "informer_ugsd_delay_fixed","0")[0]
            informer_cyclecount = self.configParser.GetValue("utility", "informer_cyclecount","0")[0]
            informer_ugsd_skipcount = self.configParser.GetValue("utility", "informer_ugsd_skipcount","0")[0]
            informer_ugsd_multicycle_count = self.configParser.GetValue("utility", "informer_ugsd_multicycle_count","0")[0]
            informer_ugsd_shmoo_delay_step = self.configParser.GetValue("utility", "informer_ugsd_shmoo_delay_step","0")[0]
            informer_ugsd_shmoo_iterations = self.configParser.GetValue("utility", "informer_ugsd_shmoo_iterations","0")[0]
            stop_on_gpio_notification_timeout = self.configParser.GetValue("utility", "stop_on_gpio_notification_timeout","1")[0]
            informer_ugsd_durationlow = self.configParser.GetValue("utility", "informer_ugsd_durationlow","0")[0]
            informer_ugsd_durationhigh = self.configParser.GetValue("utility", "informer_ugsd_durationhigh","0")[0]
            informer_ugsd_powercycle_from_test = self.configParser.GetValue("utility", "informer_ugsd_powercycle_from_test","0")[0]
            if(0 != informer_ugsd_powercycle_from_test):
                self.configParser.SetValue("utility","informer_ugsd_powercycle_from_test", "1")
                informer_ugsd_powercycle_from_test = self.configParser.GetValue("utility", "informer_ugsd_powercycle_from_test","0")[0]
            xplorer_informer_check_voltage = self.configParser.GetValue("utility", "xplorer_informer_check_voltage","0")[0]
            if(1 != xplorer_informer_check_voltage):
                self.configParser.SetValue("utility","xplorer_informer_check_voltage", "0")
                xplorer_informer_check_voltage = self.configParser.GetValue("utility", "xplorer_informer_check_voltage","0")[0]

            # Data for JSON file
            self.remoteAddress = self.configParser.GetValue("utility", "xplorer_remoteAddress","0")[0]
            if(self.remoteAddress != "127.0.0.1"):
                self.remoteAddress = "127.0.0.1"
                self.logger.Info("%-8s: Remote Address- %s"%("Xplorer", self.remoteAddress))
            self.xplorerClusterIP = self.configParser.GetValue("utility", "informer_xplorerClusterIP","0")[0]
            self.logger.Info("%-8s:xplorer ClusterIP: %s"%("xPlorer",self.xplorerClusterIP))
            self.remotePort = self.configParser.GetValue("utility", "xplorer_remotePort","0")[0]
            self.logger.Info("%-8s:Remote Port: %s"%("xPlorer",self.remotePort))
            self.product = self.configParser.GetValue("utility", "xplorer_product","0")[0]
            self.logger.Info("%-8s:Product: %s"%("xPlorer",self.product))
            self.atbMode = self.configParser.GetValue("utility", "xplorer_atbMode","0")[0]
            self.logger.Info("%-8s:atb Mode: %s"%("xPlorer",self.atbMode))
            self.calibrationEnabled = self.configParser.GetValue("utility", "xplorer_calibrationEnabled","0")[0]
            self.logger.Info("%-8s:Calibration Enabled: %s"%("xPlorer",self.calibrationEnabled))
            self.genType = self.configParser.GetValue("utility", "xplorer_genType","0")[0]
            self.logger.Info("%-8s:Gen Type: %s"%("xPlorer",self.genType))
            self.rwrMaxFileSize = self.configParser.GetValue("utility", "rwr_max_file_size","0")[0]
            self.logger.Info("%-8s:rwr Max File Size: %s"%("xPlorer",self.rwrMaxFileSize))
            self.rwrMaxFileCount = self.configParser.GetValue("utility", "rwr_max_file_count","10")[0]
            self.logger.Info("%-8s:rwr Max File Count: %s"%("xPlorer",self.rwrMaxFileCount))
            self.inst_path = self.configParser.GetValue("utility", "xplorer_installation_path","")[0]
            if(self.inst_path == "") or (not (os.path.exists(self.inst_path))):
                raise Exception("xplorer_installation_path parameter must point to existing folder")
            self.logger.Info("%-8s:xPlorer Inst path: %s"%("xPlorer",self.inst_path))

            self.dco_path = self.configParser.GetValue("utility", "xplorer_cli_session_informer_dco_file_path","")[0]
            if(self.dco_path == "") or (not (os.path.exists(self.dco_path))):
                raise Exception("xplorer_cli_session_informer_dco_file_path parameter must point to existing file")
            self.logger.Info("%-8s:Dco Path: %s"%("xPlorer",self.dco_path))

            self.updtd_path = self.configParser.GetValue("utility", "xplorer_cli_session_informer_json_input_file_path","")[0]
            if(self.updtd_path == ""):
                raise Exception("xplorer_cli_session_informer_json_input_file_path parameter must not be empty")
            self.logger.Info("%-8s:Updated JSON path: %s"%("xPlorer",self.updtd_path))

            self.rwr_path = self.configParser.GetValue("utility", "xplorer_cli_session_informer_rwr_log_file_path","")[0]
            if not self.rwr_path:
                self.rwr_path = self.loggerName.replace(".log", ".rwr")
            self.logger.Info("%-8s:Rwr Log path: %s"%("xPlorer",self.rwr_path))

            self.profile_path = self.configParser.GetValue("utility", "xplorer_informer_profile_json_input_file","")[0]
            if(self.profile_path == "") or (not (os.path.exists(self.profile_path))):
                raise Exception("xplorer_informer_profile_json_input_file parameter must point to existing file")
            self.logger.Info("%-8s:Profile JSON Path: %s"%("xPlorer",self.profile_path))
            self.dpa_conf_path = str((self.configParser.GetValue("utility", "xplorer_informer_configure_fw_events_json_input_file", ""))[0])
            if(self.dpa_conf_path == ""):
                raise Exception("xplorer_informer_configure_fw_events_json_input_file parameter in CVF configuration may not be empty")
            self.logger.Info("%-8s:Dpa Confguration Path: %s"%("xPlorer",self.dpa_conf_path))

            self.informer_voltage = str((self.configParser.GetValue("utility", "xplorer_informer_voltage", ""))[0])
            if(self.informer_voltage == ""):
                raise Exception("xplorer_informer_voltage parameter in CVF configuration may not be empty")
            elif(self.informer_voltage == "1.2" or self.informer_voltage == "AUTOMATIC"):
                self.configParser.SetValue("utility","xplorer_informer_check_voltage", "0")
            self.logger.Info("%-8s:Informer Voltage: %s"%("xPlorer",self.informer_voltage))

            self.sequenceDetectPath= self.configParser.GetValue("utility", "xplorer_cli_session_informer_sequence_detect_file_path","0")[0]
            self.logger.Info("%-8s:Sequence Detect Path: %s"%("xPlorer",self.sequenceDetectPath))

            if(self.informer_voltage == "Automatic"):
                self.informer_check_voltage="true"
            else:
                Xplor_informer_check_voltage = self.configParser.GetValue("utility","xplorer_informer_check_voltage", "0")[0]
                if(Xplor_informer_check_voltage == '0'):
                    self.informer_check_voltage = True
            self.logger.Info("%-8s:Informer Check Voltage: %s"%("xPlorer", Xplor_informer_check_voltage))
            self.xplorerSourceFile = self.configParser.GetValue("utility","xplorer_cli_session_informer_json_template_file_path", "")[0]
            if(self.xplorerSourceFile == ''):
                self.xplorerSourceFile = self.configParser.GetValue("utility", "xplorer_cli_session_informer_json_output_file_path","")[0]
            self.logger.Info("%-8s:xplorerSourceFile: %s"%("xPlorer", self.xplorerSourceFile))

            inf_discover = xPlorerWrap.InformerDiscover(sendType = ServiceWrap.SEND_IMMEDIATE)
            informerSlNo = inf_discover.GetSerialNumber()
            informerSlNoList=[x.strip() for x in informerSlNo.split(',')]
            informerSlNo = informerSlNoList[0]
            self.configParser.SetValue("utility", "serial_number", informerSlNo)

            self.logger.Info("informer serial number found {}".format(informerSlNo))
            logFileName = self.loggerName
        except (ServiceWrap.ALL_EXCEPTIONS, ServiceWrap.ConfigException) as ex:
            self.logger.Info('Failed to read informer configuration: {}'.format(ex.GetFailureDescription()))
            raise Exception(ex.GetFailureDescription())

        self.logger.Info("Informer Configuration Setup on xPlorer Completed")


    def StartInfRecording(self):

        self.logger.Info("Start Inf Recording call")

        try:
            if self.xPlorerGrid == True:
                xPlorerWrap.RemoteCreate(sendType = ServiceWrap.SEND_IMMEDIATE)
                self.logger.Info("xPlorer remote create Command executed on Grid.\n")

            self.logger.Info("Stopping previous session if exists")
            Informer_Manager = xPlorerWrap.InformerMgr.GetInformerMgrInstance()
            Informer_Manager.StopPreviousRUNNINGSessions() # This call is retained for backward compatibility
            Informer_Manager.StopPreviousDEFERREDSessions()
        except ServiceWrap.ALL_EXCEPTIONS as ex:
            self.logger.Info('Failed to read informer configuration: {}'.format(ex.GetFailureDescription()))
            pass

        # call CFT API
        try:
            session_create = xPlorerWrap.SessionCreate(sendType = ServiceWrap.SEND_IMMEDIATE)

        except Exception as ex:
            self.logger.Info("Failed to create Informer session with error: {}".format(ex.message))
            raise
        except ServiceWrap.ALL_EXCEPTIONS as ex:
            self.logger.Info('Failed to read informer configuration: {}'.format(ex.GetFailureDescription()))
            raise Exception(ex.GetFailureDescription())

        try:
            self.informerSession  = session_create.GetSessionID()
            self.startSession = xPlorerWrap.SessionStart(self.informerSession, sendType = ServiceWrap.SEND_IMMEDIATE)
            self.logger.Info("Xplorer Session created. SessionID - {}".format(self.informerSession))

        except Exception as ex:
            self.logger.Info("Failed to start Informer session with error: {}".format(ex.message))
            self.StopInfRecording()
            self.informerSession = None
            self.startSession = None
            raise

        except ServiceWrap.ALL_EXCEPTIONS as ex:
            self.logger.Info('Failed to read informer configuration: {}'.format(ex.GetFailureDescription()))
            raise Exception(ex.GetFailureDescription())

        self.logger.Info("Start Informer Recording Completed")


    def StopInfRecording(self):
        """"""

        # call CTF API to stop recordings
        self.logger.Info("Stop Informer Recording called")

        if(self.informerSession != None):
            try:
                session_stop = xPlorerWrap.SessionStop(self.informerSession)
                session_stop.Execute()
                session_stop.HandleOverlappedExecute()
                session_stop.HandleAndParseResponse()

                self.informerSession = None
                self.DPAStopped = True

            except ServiceWrap.ALL_EXCEPTIONS as ex:
                self.logger.Info('Failed to read informer configuration: {}'.format(ex.GetFailureDescription()))
                raise Exception(ex.GetFailureDescription())
            except :
                self.logger.Info('Failed to read informer configuration')
                raise
        self.logger.Info("Stop Informer Recording Completed")


    def CancelInfRecording(self):
        """"""
        # call CTF API to cancel recordings

        if(self.informerSession != None):
            self.logger.Info("Cancle Informer Recording call")
            try:
                session_cancel = xPlorerWrap.SessionCancel(self.informerSession)
                session_cancel.Execute()
                session_cancel.HandleOverlappedExecute()
                session_cancel.HandleAndParseResponse()
                self.informerSession = None
            except Exception as ex:
                self.logger.Info("Failed to cancel Informer session with error: {}".format(ex.message))
                raise
            except ServiceWrap.ALL_EXCEPTIONS as ex:
                self.logger.Info('Failed to read informer configuration: {}'.format(ex.GetFailureDescription()))
                raise Exception(ex.GetFailureDescription())
            except :
                self.logger.Info('Failed to read informer configuration')
                raise


    def CleanSession(self):
        self.logger.Info("Calling Clean Session")
        ServiceWrap.Session.CleanSession()
        self.logger.Info("Clean Session Completed")



" ----  Sample script Test Start from here  ---- "


XplorerSession = XplorerFrame()
testName = "Read"
loggerName = "C:\\test\\xPlorer\\" + testName + ".log"
if loggerName == "":
    print("Please Enter logger name")
    raise "Please Enter logger name"
XplorerSession.CreateNVMeSession(loggerName)
XplorerSession.checkInformerConfiguration()
XplorerSession.StartInfRecording()
#Try Any command below



XplorerSession.StopInfRecording()
XplorerSession.CleanSession()