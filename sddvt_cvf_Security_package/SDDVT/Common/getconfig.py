"""
################################################################################
# Copyright (c) SanDisk Corp.2022 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# SCRIPTER PARENT SCRIPT         : None
# SCRIPTER SCRIPT                : None
# CTF CALL ALL SCRIPT            : None
# CTF SCRIPT                     : getconfig.py
# CVF CALL ALL SCRIPT            : None
# CVF SCRIPT                     : getconfig.py
# DESCRIPTION                    : Reads the project configiuration details. Note : all values read a strings
# PRERQUISTE                     : None
# STANDALONE EXECUTION           : No. It is an utility script
# TEST ARGUMENTS                 : None
# AUTHOR [Referred Scripter/CTF] : Sivagurunathan
# REVIEWED BY                    : None
# DATE                           : 27/12/2021
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
    from builtins import object

# Python Build-in Modules
import os

# From CVF Package
import SDCommandWrapper as sdcmdWrap
import Core.ValidationError as ValidationError
import Core.Configuration as Configuration

class getconfig(object):
    def __init__(self):
        self.currCfg = Configuration.ConfigurationManagerInitializer.ConfigurationManager.currentConfiguration

        # below three lines are same
        self.__TestsDir = self.currCfg.system.TestsDir
        #self.__TestsDir = self.currCfg.GetSystemConfiguration().TestsDir
        #self.__TestsDir = self.currCfg.system.TestsDir

        self.__project_config = self.currCfg.system.TestsCfgDir

        self.__sdconfig = self.currCfg.variation.sdconfiguration
        #self.__sdconfig = str(sdcmdWrap.GetCardTransferMode()).replace("SWITCH_", "")
        #self.__sdconfig = self.__sdconfig.replace("_", "")

        if not self.__TestsDir:
            raise ValidationError.TestFailError("getconfig.py", "SDDVT home path not set")

        if not self.__project_config:
            raise ValidationError.TestFailError("getconfig.py", "%s, Project Configuration Not Found..." % (self.__project_config))

        if not self.__sdconfig:
            raise ValidationError.TestFailError("getconfig.py", "%s,  sdconfiguration Not Found..." % (self.__sdconfig))

        self.cfgfile = os.path.join(self.__TestsDir, self.__project_config, self.__sdconfig, 'ConfigGlobalParameters.txt')

        if not os.path.isfile(self.cfgfile):
            raise ValidationError.TestFailError("getconfig.py", "%s, config file not found..." % self.cfgfile)

        return

    def get(self, name):
        if not name:
            return None
        if self.cfgfile:
            if not os.path.isfile(self.cfgfile):
                raise ValidationError.TestFailError("getconfig.py", "%s, config file not found..."%self.cfgfile)
            fh = open(self.cfgfile, 'r')
            for line in fh.readlines():
                if line.startswith(name):
                    return line.split('=')[1].strip()
                else:
                    continue
        return None


#To Test script individually
#if __name__=='__main__':
#    obj = getconfig()
