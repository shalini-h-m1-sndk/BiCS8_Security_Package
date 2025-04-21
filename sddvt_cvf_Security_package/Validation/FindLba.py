from __future__ import print_function
from __future__ import division

from builtins import str
from builtins import range
from past.utils import old_div
from builtins import object

#import TT_lib_C_64 as TT_lib_C

#try:
    #import TT_lib_C_64 as TT_lib_C
#except ImportError, e:
    #print e
    #raise Exception("TT_lib_C dll is missing or corrupted")

import os
import sys
import array

class LogParser(object):
    lastFileName = ""
    def PrintFile(self, fileName):
        if self.lastFileName != fileName:
            print("\n","--"*20,fileName,"--"*20)
            self.lastFileName = fileName

    def Run(self, dirPath, inputLba, reads, dump, ugsd, totalCount):
        #dirPath = "D:\workspace\TTK_SDIN_INTEGRATION_2\Tests\WRC\IoMeter"
        filenames = os.listdir(dirPath)
        if len(filenames) == 0:
            print("Provide a valid Log Directory Path")
            return

        for inputLba in range(inputLba, inputLba+totalCount):
            filenames = sorted(filenames)
            writeIndex = 0
            fwindex=0
            memoryDump = dump
            processId = None
            print("--"*20,"Find all Instances of Lba 0x%0x in Write, Read and Trim Commands" %(inputLba), "--"*20, "\n")
            #filenames.sort(key=lambda x: os.stat(os.path.join(dirPath, x)).st_mtime)

            for fileName in filenames:

                #if fileName.find('IoMeter_log_P0_C1_0') != -1:
                filePath = os.path.join(dirPath,fileName)
                lineNum = 1
                previousLine = []
                previousLine.append("")
                previousLine.append("")
                try:
                    with open(filePath, "r") as f:
                            for line in f:
                                try:
                                    index = line.find('SW : l: ')
                                    if  index != -1:
                                        index = index + len('SW : l: ')
                                        lbaEnd = line.find(',', index)
                                        lbaint = int(line[index:lbaEnd], 16)

                                        countStart = line.find("tL: ") + len("tL: ")
                                        countEnd = line.find(",", countStart)

                                        count = int(line[countStart:countEnd], 16 )



                                        if lbaint <= inputLba and (lbaint + count) > inputLba:
                                            writeIndex = writeIndex + 1
                                            printFile = ""
                                            self.PrintFile(fileName)
                                            print("Version: %d, " %writeIndex, line.strip())

                                    index = line.find('FW : l: ')
                                    if  index != -1:
                                        index = index + len('FW : l: ')
                                        lbaEnd = line.find(',', index)
                                        lbaint = int(line[index:lbaEnd], 16)

                                        countStart = line.find("tL: ") + len("tL: ")
                                        countEnd = line.find(",", countStart)

                                        count = int(line[countStart:countEnd], 16 )



                                        if lbaint <= inputLba and (lbaint + count) > inputLba:
                                            fwindex = fwindex + 1
                                            printFile = ""
                                            self.PrintFile(fileName)
                                            #print line.strip()
                                            print("Version: %d, " %fwindex, line.strip())

                                    index = line.find('Start WriteZero : lba: ')
                                    if  index != -1:
                                        index = index + len('Start WriteZero : lba: ')
                                        lbaEnd = line.find(',', index)
                                        lbaint = int(line[index:lbaEnd], 16)

                                        countStart = line.find("transfer Length: ") + len("transfer Length: ")
                                        countEnd = line.find(" ", countStart)

                                        count = int(line[countStart:countEnd], 16 )



                                        if lbaint <= inputLba and (lbaint + count) > inputLba:
                                            writeIndex = 0
                                            printFile = ""
                                            self.PrintFile(fileName)
                                            print("Version: %d, " %writeIndex, line.strip())

                                    index = line.find('Finish WriteZero : lba: ')
                                    if  index != -1:
                                        index = index + len('Finish WriteZero : lba: ')
                                        lbaEnd = line.find(',', index)
                                        lbaint = int(line[index:lbaEnd], 16)

                                        countStart = line.find("transfer Length: ") + len("transfer Length: ")
                                        countEnd = line.find(" ", countStart)

                                        count = int(line[countStart:countEnd], 16 )



                                        if lbaint <= inputLba and (lbaint + count) > inputLba:
                                            #writeIndex = writeIndex + 1
                                            printFile = ""
                                            self.PrintFile(fileName)
                                            print(line.strip())
                                            #index = line.find('D=')
                                            #seed = int(line[index+2:], 16 )

                                            #lbaDiff = inputLba - lbaint
                                            #seed = TT_lib_C.NextSeedForPatternIncremental(seed, lbaDiff)
                                            #print "Seed for Lba 0x%0x is 0x%0x" %(inputLba, seed)
                                            #if memoryDump:
                                                #writeBuffer  = array.array('B', "".zfill(512))
                                                #testProcessId = processId
                                                #if processId ==  None:
                                                    #testProcessId = 0
                                                #TT_lib_C.FillByPatternIncremental(writeBuffer, 1, lbaint, 0, seed)

                                                #writtenFile = open(os.path.join(dirPath,"Write_0x%0x_%d.bin"%(inputLba, writeIndex)) , 'wb')
                                                #writeBuffer.tofile(writtenFile)
                                                #writtenFile.close()

                                            #Start Read : lba: 0x168E3, transfer Length: 0x800
                                            #Start Write : lba: 0x168E3, transfer Length: 0x39 , patternID:  0x1D, transID: 1
                                    index = line.find('Start WUC : lba: ')
                                    if  index != -1:
                                        index = index + len('Start WUC : lba: ')
                                        lbaEnd = line.find(',', index)
                                        lbaint = int(line[index:lbaEnd], 16)

                                        countStart = line.find("transfer Length: ") + len("transfer Length: ")
                                        countEnd = line.find(" ", countStart)

                                        count = int(line[countStart:countEnd], 16 )



                                        if lbaint <= inputLba and (lbaint + count) > inputLba:
                                            writeIndex = 0
                                            printFile = ""
                                            self.PrintFile(fileName)
                                            print("Version: %d, " %writeIndex, line.strip())

                                    index = line.find('Finish WUC : lba: ')
                                    if  index != -1:
                                        index = index + len('Finish WUC : lba: ')
                                        lbaEnd = line.find(',', index)
                                        lbaint = int(line[index:lbaEnd], 16)

                                        countStart = line.find("transfer Length: ") + len("transfer Length: ")
                                        countEnd = line.find(" ", countStart)

                                        count = int(line[countStart:countEnd], 16 )



                                        if lbaint <= inputLba and (lbaint + count) > inputLba:
                                            #writeIndex = writeIndex + 1
                                            printFile = ""
                                            self.PrintFile(fileName)
                                            print(line.strip())
                                    if reads:
                                        index = line.find('SR : l: ')
                                        if  index != -1:
                                            index = index + len('SR : l: ')
                                            lbaEnd = line.find(',', index)
                                            lbaint = int(line[index:lbaEnd], 16)

                                            countStart = line.find("tL: ") + len("tL: ")
                                            countEnd = line.find(",", countStart)
                                            count = int(line[countStart:countEnd], 16 )

                                            if lbaint <= inputLba and (lbaint + count) > inputLba:
                                                self.PrintFile(fileName)
                                                print(line.strip())

                                        index = line.find('FR : l: ')
                                        if  index != -1:
                                            index = index + len('FR : l: ')
                                            lbaEnd = line.find(',', index)
                                            lbaint = int(line[index:lbaEnd], 16)

                                            countStart = line.find("tL: ") + len("tL: ")

                                            countEnd = line.find(",", countStart)
                                            count = int(line[countStart:countEnd], 16 )

                                            if lbaint <= inputLba and (lbaint + count) > inputLba:
                                                self.PrintFile(fileName)
                                                print(line.strip())



                                    index = line.find('Start Erase : lba: ')
                                    if  index != -1:
                                        index = index + len('Start Erase : lba: ')
                                        lbaEnd = line.find(',', index)
                                        lbaint = int(line[index:lbaEnd], 16)

                                        countStart = line.find("transfer Length: ") + len("transfer Length: ")

                                        count = int(line[countStart:], 16 )

                                        if lbaint <= inputLba and (lbaint + count) > inputLba:
                                            self.PrintFile(fileName)
                                            writeIndex=0
                                            print("Version: %d, " %writeIndex, line.strip())

                                    index = line.find('Finish Erase : lba: ')
                                    if  index != -1:
                                        index = index + len('Finish Erase : lba: ')
                                        lbaEnd = line.find(',', index)
                                        lbaint = int(line[index:lbaEnd], 16)

                                        countStart = line.find("transfer Length: ") + len("transfer Length: ")

                                        countEnd = line.find(",", countStart)
                                        count = int(line[countStart:countEnd], 16 )

                                        if lbaint <= inputLba and (lbaint + count) > inputLba:
                                            self.PrintFile(fileName)
                                            print(line.strip())

                                    index=line.find('Format')
                                    if index != -1:
                                        self.PrintFile(fileName)
                                        print(line.strip())

                                    #UGSD affected : l: 0x26306, tL: 0x2, tID: 19300
                                    index=line.find("UGSD affected : l: ")
                                    if index != -1:
                                        index = index + len("UGSD affected : l: ")
                                        lbaEnd = line.find(',', index)
                                        lbaint = int(line[index:lbaEnd], 16)
                                        countStart = line.find("tL: ") + len("tL: ")
                                        countEnd = line.find(",", countStart)
                                        count = int(line[countStart:countEnd], 16 )
                                        if lbaint <= inputLba and (lbaint + count) > inputLba:
                                            self.PrintFile(fileName)
                                            print(line.strip())

                                    if ugsd:
                                        index = line.find('Prepare to ungraceful reset')
                                        if index != -1:
                                            self.PrintFile(fileName)
                                            print(previousLine[0].strip(),line)

                                        index = line.find('PowerOff')
                                        if index != -1:
                                            self.PrintFile(fileName)
                                            print(line)

                                        index = line.find('Flush Cache')
                                        if index != -1:
                                            self.PrintFile(fileName)
                                            print(line.strip())

                                    if processId == None:
                                        index = line.find("Process ID: ")
                                        if index != -1:
                                            processId = int(line[index+len("Process ID: "):])

                                    index = line.lower().find('COMReset')
                                    if index != -1:
                                        self.PrintFile(fileName)
                                        print(line)
                                except Exception as ex:
                                    pass
                                lineNum = lineNum + 1
                                previousLine[1] = line
                                previousLine[0] = previousLine[1]



                except Exception as ex:
                    print("Error Read File %s : %s" %(filePath, str(ex)))



def GetInconsistenSector():

    with open("P0-#0-18082015-095107-NoUART-read.bin", "rb") as f:
        byteArr = array.array('B')
        ba = bytearray(f.read())
        sectors = old_div(len(ba),512)
        count = 1
        while count < sectors - 1:
            if ba[(count * 512) - 1] >= 0xFC:
                if ba[(count * 512) + 5]  != 0:
                    print(count)
            elif ba[(count * 512) + 5]  - 1 !=  ba[(count * 512) - 1]:
                print(count)

            count = count + 1
        pass
if __name__ == "__main__":
    import argparse

    def str2bool(v):
        return v.lower() in ("yes", "true", "t", "1")
    parser = argparse.ArgumentParser(description='Find LBA history in TTK Log Files.')
    #parser.register('type', 'bool', str2bool)
    parser.add_argument('--logdir', dest = 'logDir', type=str, required = True,
                        help='Log File Directory')
    parser.add_argument('--lba', dest='lba', type=str, required = True,
                        help='LBA value')
    parser.add_argument('--reads', dest='reads', type=str2bool, default = True,
                            help='set to true to parse reads, Default: True')

    parser.add_argument('--dump', dest='dump', type=str2bool, default = False,
                            help='if True, Binary files for that write will be dumped in the log directory\n, with file format WRITE_LBA_Version, Default: False')

    parser.add_argument('--ugsd', dest='ugsd', type=str2bool, default = True,
                            help='if True, Print all occurances of UGSD and Flush Cache, Default: True')

    parser.add_argument('--count', dest='count', type=str, default = 1,
                            help='Number of Lbas to find Count')

    args = parser.parse_args()
    if args.lba.find('0x') != -1:
        args.lba = int(args.lba, 16)
    else:
        args.lba = int(args.lba)

    if args.count.find('0x') != -1:
        args.count = int(args.count, 16)
    else:
        args.count = int(args.count)

    try:
        logParser = LogParser()
        logParser.Run(args.logDir, args.lba, args.reads, args.dump, args.ugsd, args.count)
    except Exception as ex:
        print("Failed to Find LBA history: %s" %str(ex))
        print("PLease ensure to provide a valid Log Directory Path")