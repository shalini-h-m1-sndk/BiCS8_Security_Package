from __future__ import print_function
#import TT_lib_C_64 as TT_lib_C

#try:
    #import TT_lib_C_64 as TT_lib_C
#except ImportError, e:
    #print e
    #raise Exception("TT_lib_C dll is missing or corrupted")

from builtins import str
from builtins import object
import os
import sys
import array
import re

class LogParser(object):
    lastFileName = ""
    def PrintFile(self, fileName):
        if self.lastFileName != fileName:
            print("\n","--"*20,fileName,"--"*20)
            self.lastFileName = fileName

    def Run(self, dirPath, WDir, RDir):

        filenames = os.listdir(dirPath)
        if len(filenames) == 0:
            print("Provide a valid Log Directory Path")
            return

        filenames = sorted(filenames)

        tempList = list()
        #For Write LBAs.
        for fileName in filenames:
            if fileName.endswith(".txt"):
                filePath = os.path.join(dirPath, fileName)
                newFile = "WLBA_" + fileName
                newFile = os.path.join(WDir, newFile)
                with open(newFile, "w") as ff:
                    with open(filePath, "r") as f:
                        for line in f:
                            if 'WLBA' in line:
                                reg = "WLBA: [a-zA-Z0-9 :]+"
                                a = re.findall(reg, line)
                                ff.write(str(a))
                                ff.write("\n")
        #For Read LBAs
        for fileName in filenames:

            if fileName.endswith(".txt"):
                filePath = os.path.join(dirPath, fileName)
                newFile = "RLBA_" + fileName
                newFile = os.path.join(RDir, newFile)
                with open(newFile, "w") as ff:
                    with open(filePath, "r") as f:
                        for line in f:
                            if 'RLBA' in line:
                                reg = "RLBA: [a-zA-Z0-9 :]+"
                                a = re.findall(reg, line)
                                ff.write(str(a))
                                ff.write("\n")

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Find LBA history in TTK Log Files.')
    parser.add_argument('--logdir', dest = 'logDir', type=str, required = True,
                        help='Log File Directory')

    args = parser.parse_args()
    WDir = os.path.join(args.logDir, "WLogs")
    RDir = os.path.join(args.logDir, "RLogs")
    if not os.path.exists(WDir):
        os.mkdir(WDir)
    if not os.path.exists(RDir):
        os.mkdir(RDir)

    try:
        logParser = LogParser()
        logParser.Run(args.logDir, WDir, RDir)
    except Exception as ex:
        print("Exception Occurred. Error Message is : %s" %str(ex))
