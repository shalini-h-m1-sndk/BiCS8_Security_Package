"""
class AddressTypes
Provides phy address related variables
@ Author: Shaheed Nehal - ported to CVF
@ copyright (C) 2021 Western Digital Corporation
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info.major >= 3:
    pass # from builtins import *
    from builtins import object
class PhysicalAddress(object):
    def __init__(self):
        """
        Constructor
        """
        self.bank = 0
        self.chip = 0
        self.die = 0
        self.plane = 0
        self.block = 0
        self.wordLine = 0
        self.string = 0
        self.mlcLevel = 0
        self.eccPage = 0
        self.isTrueBinaryBlock = None
    def __str__( self ):
        """
        Name:                   __str__
        Description:            Get the physical address in the string format for easy printing

        Outputs:
            phyAddString        Physical Address in string format

        """
        phyAddString="Chip=0x%X, Die=0x%X, Plane=0x%X, Block=0x%X, WordLine=0x%X, string=0x%x, MlcPage=0x%X, EccPage=0x%X isTrueBinaryBlock=%s "\
                    %(self.chip,self.die,self.plane,self.block,self.wordLine,self.string,self.mlcLevel,self.eccPage, self.isTrueBinaryBlock)
        return phyAddString

class SectorBasedPhysicalAddress(object):
    def __init__(self):
        """
        Constructor
        """
        self.chip = 0
        self.die = 0
        self.plane = 0
        self.block = 0
        self.wordLine = 0
        self.mlcLevel = 0
        self.sector = 0
