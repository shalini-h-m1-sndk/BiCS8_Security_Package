
"""
################################################################################
# Copyright (c) SanDisk Corp.2013 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# FILE:DLStructureParser.py: Command Utility Library.
# AUTHOR: Manjunath Badi
################################################################################
"""
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
from builtins import hex
from builtins import next
from builtins import str
from builtins import range
from builtins import object
import os
import sys
import xml.etree.ElementTree as ET

import CTFServiceWrapper as ServiceWrap
import Core.ValidationError as ValidationError
import Protocol.NVMe.Basic.VTFContainer as VTF
from xml.dom import minidom
from collections import OrderedDict
import Lib.System.Randomizer as Randomizer
#**************************************************************************************************************
##
# @brief Runs all the variations in the testObject
# @details
# @return None
# @exception None
#**************************************************************************************************************
class DLStructureParser(object):
    """This class is created to parse the DriverLoop parameter values from DLStructure.xml , CVF.ini.README , CVF.ini,
    Work Flow(FVTProfilesDB.xml) , Test Variation and Test command line """


    def __init__(self,DLProfile, VTF_Container, currcfg):
        """ Constructor """

        self.ProfileType , self.ProfileName = DLProfile.split(".")
        self.DLProfile = DLProfile
        self.VTFContainer = VTF_Container
        self.currCfg = currcfg
        config_logger = self.VTFContainer.systemCfg.Logger
        self.DLStructurePath = os.path.join(os.environ['SANDISK_CTF_HOME_X64'] + '\config\DLStructures.xml')
        self.DLStructDict = OrderedDict()
        tree = ET.parse(self.DLStructurePath)
        # parameters collection based on Priority
        self.DLStructureDefaultDict(tree)
        self.CollectCVFReadMeConfigParams()
        self.CollectCVFiniConfigParams()
        self.CollectProfileData()
        self.CollectTestParameters()
        self.CollectCommandLineArgs()
        self.DLStructDict['randomseed']['default'] = Randomizer.Randomizer().GetSeed()
        self.DLStructDict["dumpfolderpath"]["default"] = config_logger.logFolder


    def DLStructureDefaultDict(self,root):
        """ This methos is implimented to parse all default parameter from DLStructures.XML and
        created an Dictionary(DLStructDict) where Keys are parameter names and Values are attributes
        of Parameter.
        """

        print(root)
        for Fields in root.iter('{vtfSchema}Field'):
            i = 1
            key = Fields.attrib.pop('name').lower()
            if key not in list(self.DLStructDict.keys()):
                self.DLStructDict[key] = Fields.attrib
            else:
                while(key + str(i) in list(self.DLStructDict.keys())):
                    i += 1
                else:
                    key += str(i)
                    self.DLStructDict[key] = Fields.attrib
        self.DLStructureDict = self.DLStructDict

    def int_to_bytes(self,val, num_bytes):
        return [hex((val & (0xff << pos*8)) >> pos*8) for pos in range(num_bytes)]


    def CollectProfileData(self):
        """ This method is parsing ProfileLibrary.xml and collecting parameters from profile defined(DL_Profiles)
        in test xlm file and Overwriting Default dictionary(DLStructDict) values with profile data.
        """

        from xml.dom import minidom
        filename = "C:\\Project\\GIT\\\\CVF-AD_Fork\\QA\\NVMe\\VTF\\Extensions\\ProfileLibrary.xml"
        xmlObj = minidom.parse(filename)
        ProfilesObj = xmlObj.getElementsByTagName("Profiles")[0]
        WorkFlowObj = ProfilesObj.getElementsByTagName("WorkFlow")[0]
        ProfileHeaderObj = WorkFlowObj.getElementsByTagName(self.ProfileType)[0]
        for profiles in ProfileHeaderObj.getElementsByTagName('Profile'):
            if profiles.getAttribute("name") == self.ProfileName:
                count = 0
                for node in profiles.childNodes:
                    if count % 2 != 0:
                        self.DLStructDict[node.getAttribute(list(node._attrs.keys())[0]).lower()]['default'] = node.firstChild.data
                    count += 1
        self.DLStructDict["profilename"]['default'] = self.DLProfile

    def CollectCVFiniConfigParams(self):
        """ This method collecting parameters defined in CVF.ini file and Overwriting Default dictionary(DLStructDict)
        values with profile data.
        """
        from configparser import SafeConfigParser
        import Core.Constants as Constants
        cvfConfigParser = SafeConfigParser()
        self.configFileParams = []
        configPath = "C:\Program Files (x86)\SanDisk\CVF_2.0_x64\config\cvf.ini"
        cvfConfigParser.read(configPath)
        for section_name in cvfConfigParser.sections():
            for name,value in cvfConfigParser.items(section_name):
                if name in list(self.DLStructDict.keys()):
                    self.DLStructDict[name]['default'] = value

    def CollectCVFReadMeConfigParams(self):
        """ This method collecting parameters defined in CVF.ini.README file and Overwriting Default dictionary(DLStructDict)
        values with profile data.
        """
        from configparser import SafeConfigParser
        import Core.Constants as Constants
        cvfConfigParser = SafeConfigParser()
        self.configFileParams = []
        configPath = os.path.dirname(os.getcwd()) + Constants.CVF_CONFIG
        cvfConfigParser.read(configPath)
        for section_name in cvfConfigParser.sections():
            for name,value in cvfConfigParser.items(section_name):
                if name in list(self.DLStructDict.keys()):
                    self.DLStructDict[name]['default'] = value

    def CollectCommandLineArgs(self):
        """ This method collecting parameters defined in CVF.ini.README file and Overwriting Default dictionary(DLStructDict)
        values with profile data.
        """
        for arg , value in list(self.VTFContainer.cmd_line_args.__dict__.items()):
            if value is not None:
                if arg.lower() in list(self.DLStructDict.keys()):
                    self.DLStructDict[arg.lower()]['default'] = value

    def CollectTestParameters(self):
        for arg , value in list(self.currCfg.variation.__dict__.items()):
            if value is not None:
                if arg.lower() in list(self.DLStructDict.keys()):
                    self.DLStructDict[arg.lower()]['default'] = value

class MultipleProfileDLStructureParser(object):
    """This class is created to parse the DriverLoop parameter values from DLStructure.xml , CVF.ini.README , CVF.ini,
    Work Flow(FVTProfilesDB.xml) , Test Variation and Test command line """

    def __init__(self,DLProfile, VTF_Container, currcfg):
            """ Constructor """
            self.profileNum = 1
            self.VTFContainer = VTF_Container
            self.currCfg = currcfg
            config_logger = self.VTFContainer.systemCfg.Logger
            self.DLStructurePath = os.path.join(os.environ['SANDISK_CTF_HOME_X64'] + '\config\DLStructures.xml')
            self.DLStructDict = OrderedDict([('RUN_PROFILES_REQUEST_Header' ,OrderedDict() ),('PROFILE_COMMON_PARAMS' , OrderedDict()),('PROFILE_SPECIFIC_PARAMS' , OrderedDict())])
            tree = ET.parse(self.DLStructurePath)
            for self.ProfileName in DLProfile.split(","):
                self.DLStructureDefaultDict(tree)
                self.profileNum += 1
            self.CollectCVFReadMeConfigParams()
            self.CollectCVFiniConfigParams()
            self.CollectProfileData()
            self.CollectTestParameters()
            self.CollectCommandLineArgs()
            self.DLStructDict["PROFILE_COMMON_PARAMS"]["testname"]["default"] = self.VTFContainer.execution_info.GeValueFromTestDataCollection("logFileName").rstrip(".log")
            #self.DLStructDict["PROFILE_COMMON_PARAMS"]["randomseed"]["default"] = Randomizer.Randomizer().GetSeed()
            #self.DLStructDict["PROFILE_COMMON_PARAMS"]["dumpfolderpath"]["default"] = config_logger.logFolder.strip("\\")

    def DLStructureDefaultDict(self,root):
        """ This methos is implimented to parse all default parameter from DLStructures.XML and
        created an Dictionary(DLStructDict) where Keys are parameter names and Values are attributes
        of Parameter.
        """
        from xml.dom import minidom
        filename = self.DLStructurePath
        xmlObj = minidom.parse(filename)
        DL_StructureObj = xmlObj.getElementsByTagName("DL_STRUCTURE")[0]
        RunProfilesRequestObj = DL_StructureObj.getElementsByTagName("RUN_PROFILES_REQUEST")[0]
        if self.DLStructDict['RUN_PROFILES_REQUEST_Header'] == {}:
            for profiles in RunProfilesRequestObj.getElementsByTagName('RUN_PROFILES_REQUEST_Header'):
                count = 0

                for node in profiles.childNodes:
                    if count % 2 != 0:
                        self.DLStructDict['RUN_PROFILES_REQUEST_Header'][node.getAttribute('name').lower()] = OrderedDict([('order',node.getAttribute('order')),('default',node.getAttribute('default')),('length',node.getAttribute('length')),('type',node.getAttribute('type'))])
                    count += 1

        if self.DLStructDict['PROFILE_COMMON_PARAMS'] == {}:
            for profiles in RunProfilesRequestObj.getElementsByTagName('PROFILE_COMMON_PARAMS'):
                count = 0
                reservedCount = 0
                for node in profiles.childNodes:
                    if count % 2 != 0:
                        Parametername = node.getAttribute('name').lower()
                        if 'reserved' in Parametername:
                            Parametername = Parametername + str(reservedCount)
                            reservedCount += 1
                        self.DLStructDict['PROFILE_COMMON_PARAMS'][Parametername] = OrderedDict([('order',node.getAttribute('order')),('default',node.getAttribute('default')),('length',node.getAttribute('length')),('type',node.getAttribute('type'))])
                    count += 1

        for profiles in RunProfilesRequestObj.getElementsByTagName('PROFILE_SPECIFIC_PARAMS'):
            count = 0
            reservedCount = 0
            self.ProfileName += "__" + str(self.profileNum)
            for node in profiles.childNodes:
                if count % 2 != 0:
                    Parametername = node.getAttribute('name').lower()
                    if 'reserved' in Parametername:
                        Parametername = Parametername + str(reservedCount)
                        reservedCount += 1
                    if self.ProfileName not in list(self.DLStructDict['PROFILE_SPECIFIC_PARAMS'].keys()):
                        self.DLStructDict['PROFILE_SPECIFIC_PARAMS'][self.ProfileName] = OrderedDict()
                    self.DLStructDict['PROFILE_SPECIFIC_PARAMS'][self.ProfileName][Parametername] = OrderedDict([('order',node.getAttribute('order')),('default',node.getAttribute('default')),('length',node.getAttribute('length')),('type',node.getAttribute('type'))])
                count += 1

    def int_to_bytes(self,val, num_bytes):
        return [hex((val & (0xff << pos*8)) >> pos*8) for pos in range(num_bytes)]


    def CollectProfileData(self):
        """ This method is parsing ProfileLibrary.xml and collecting parameters from profile defined(DL_Profiles)
        in test xlm file and Overwriting Default dictionary(DLStructDict) values with profile data.
        """

        '''from xml.dom import minidom
        filename = "C:\\Project\\GIT\\\\CVF-AD_Fork\\QA\\NVMe\\VTF\\Extensions\\ProfileLibrary.xml"
        xmlObj = minidom.parse(filename)
        ProfilesObj = xmlObj.getElementsByTagName("Profiles")[0]
        WorkFlowObj = ProfilesObj.getElementsByTagName("WorkFlow")[0]
        ProfileHeaderObj = WorkFlowObj.getElementsByTagName(self.ProfileType)[0]
        for profiles in ProfileHeaderObj.getElementsByTagName('Profile'):
            if profiles.getAttribute("name") == self.ProfileName.split('.')[1]:
                count = 0
                for node in profiles.childNodes:
                    if count % 2 != 0:
                        self.DLStructDict[node.getAttribute(node._attrs.keys()[0]).lower()]['default'] = node.firstChild.data
                    count += 1
        #self.DLStructDict["profilename"]['default'] = self.DLProfile'''
        try:
            from xml.dom import minidom
            filename = "C:\\Project\\GIT\\\\CVF-AD_Fork\\QA\\NVMe\\VTF\\Extensions\\ProfileLibrary.xml"
            xmlObj = minidom.parse(filename)
            ProfilesObj = xmlObj.getElementsByTagName("Profiles")[0]
            WorkFlowObj = ProfilesObj.getElementsByTagName("WorkFlow")[0]
            Profilecount = 0
            for Profile in list(self.DLStructDict['PROFILE_SPECIFIC_PARAMS'].keys()):
                Profile = Profile.split("__")[0]
                Profilecount += 1
                ProfileType = Profile.split('.')[0]
                ProfileHeaderObj = WorkFlowObj.getElementsByTagName(ProfileType)[0]
                for profiles in ProfileHeaderObj.getElementsByTagName('Profile'):
                    if ProfileType + "." +profiles.getAttribute('name') + "__" + str(Profilecount) in list(self.DLStructDict['PROFILE_SPECIFIC_PARAMS'].keys()):
                        count = 0
                        for node in  profiles.childNodes:
                            if count % 2 != 0:
                                self.DLStructDict['PROFILE_SPECIFIC_PARAMS'][ProfileType + "." +profiles.getAttribute('name') + "__" + str(Profilecount)][node.getAttribute('name').lower()]['default'] = node.firstChild.data
                            count += 1
        except Exception as e:
            print(e)


    def CollectCVFiniConfigParams(self):
        """ This method collecting parameters defined in CVF.ini file and Overwriting Default dictionary(DLStructDict)
        values with profile data.
        """
        from configparser import SafeConfigParser
        import Core.Constants as Constants
        cvfConfigParser = SafeConfigParser()
        self.configFileParams = []
        configPath = "C:\Program Files (x86)\SanDisk\CVF_2.0_x64\config\cvf.ini"
        cvfConfigParser.read(configPath)
        for section_name in cvfConfigParser.sections():
            for name,value in cvfConfigParser.items(section_name):
                if name in list(self.DLStructDict['RUN_PROFILES_REQUEST_Header'].keys()):
                    self.DLStructDict['RUN_PROFILES_REQUEST_Header'][name]['default'] = value

                if name in list(self.DLStructDict['PROFILE_COMMON_PARAMS'].keys()):
                    self.DLStructDict['PROFILE_COMMON_PARAMS'][name]['default'] = value

                for profile in list(self.DLStructDict['PROFILE_SPECIFIC_PARAMS'].keys()):
                    if name in list(self.DLStructDict['PROFILE_SPECIFIC_PARAMS'][profile].keys()):
                        self.DLStructDict['PROFILE_SPECIFIC_PARAMS'][profile][name]['default'] = value

    def CollectCVFReadMeConfigParams(self):
        """ This method collecting parameters defined in CVF.ini.README file and Overwriting Default dictionary(DLStructDict)
        values with profile data.
        """
        from configparser import SafeConfigParser
        import Core.Constants as Constants
        cvfConfigParser = SafeConfigParser()
        self.configFileParams = []
        configPath = os.path.dirname(os.getcwd()) + Constants.CVF_CONFIG
        cvfConfigParser.read(configPath)
        for section_name in cvfConfigParser.sections():
            for name,value in cvfConfigParser.items(section_name):
                if name in list(self.DLStructDict['RUN_PROFILES_REQUEST_Header'].keys()):
                    self.DLStructDict['RUN_PROFILES_REQUEST_Header'][name]['default'] = value.split(',')[1]

                if name in list(self.DLStructDict['PROFILE_COMMON_PARAMS'].keys()):
                    self.DLStructDict['PROFILE_COMMON_PARAMS'][name]['default'] = value.split(',')[1]

                for profile in list(self.DLStructDict['PROFILE_SPECIFIC_PARAMS'].keys()):
                    if name in list(self.DLStructDict['PROFILE_SPECIFIC_PARAMS'][profile].keys()):
                        self.DLStructDict['PROFILE_SPECIFIC_PARAMS'][profile][name]['default'] = value.split(',')[1]

    def CollectCommandLineArgs(self):
        """ This method collecting parameters defined in CVF.ini.README file and Overwriting Default dictionary(DLStructDict)
        values with profile data.
        """
        for arg , value in list(self.VTFContainer.cmd_line_args.__dict__.items()):
            if value is not None:
                if arg.lower() in list(self.DLStructDict['RUN_PROFILES_REQUEST_Header'].keys()):
                    self.DLStructDict['RUN_PROFILES_REQUEST_Header'][arg.lower()]['default'] = value

                if arg.lower() in list(self.DLStructDict['PROFILE_COMMON_PARAMS'].keys()):
                    self.DLStructDict['PROFILE_COMMON_PARAMS'][arg.lower()]['default'] = value

                for profile in list(self.DLStructDict['PROFILE_SPECIFIC_PARAMS'].keys()):
                    if arg.lower() in list(self.DLStructDict['PROFILE_SPECIFIC_PARAMS'][profile].keys()):
                        self.DLStructDict['PROFILE_SPECIFIC_PARAMS'][profile][arg.lower()]['default'] = value

    def CollectTestParameters(self):
        for arg , value in list(self.currCfg.variation.__dict__.items()):
            if arg.lower() in list(self.DLStructDict['RUN_PROFILES_REQUEST_Header'].keys()):
                self.DLStructDict['RUN_PROFILES_REQUEST_Header'][arg.lower()]['default'] = value

            if arg.lower() in list(self.DLStructDict['PROFILE_COMMON_PARAMS'].keys()):
                self.DLStructDict['PROFILE_COMMON_PARAMS'][arg.lower()]['default'] = value

            for profile in list(self.DLStructDict['PROFILE_SPECIFIC_PARAMS'].keys()):
                if arg.lower() in list(self.DLStructDict['PROFILE_SPECIFIC_PARAMS'][profile].keys()):
                    self.DLStructDict['PROFILE_SPECIFIC_PARAMS'][profile][arg.lower()]['default'] = value

            percentagelist = iter(self.currCfg.variation.__dict__['DL_Percentage'].split(','))

            for profile in list(self.DLStructDict['PROFILE_SPECIFIC_PARAMS'].keys()):
                self.DLStructDict['PROFILE_SPECIFIC_PARAMS'][profile]['percentage']['default'] = next(percentagelist)
