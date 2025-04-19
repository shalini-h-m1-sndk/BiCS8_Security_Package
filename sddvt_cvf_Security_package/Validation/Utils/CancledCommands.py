from __future__ import print_function
from builtins import str
"""
################################################################################
# Copyright (c) SanDisk Corp.2013 - All rights reserved.This code, and all
# derivative work, is the exclusive property of SanDisk and may not be used
# without SanDisk's authorization.
#
# FILE:CancledCommands.py: Utility to access Test Machine resourses.
#                AUTHOR: Manjunath Badi
################################################################################
#                            CHANGE HISTORY
# 17-08-2017     Cancelled commands verification Initial Revision.
################################################################################
Test Algorithm:
1. This script will take log file and creates  cancelled commands log file with total cancelled command count.
"""""

import re
import os
import sys
import time

starttime =time.time()
filename = ""
logfolder = "C:\\tests\\Logs\\"
validfiles = list()
NumberOfCancledCommands = 0
for args in sys.argv:
	if "--logfolder=" in args.lower():
		logfolder = args.replace("--logfolder","")
	elif "--logfile=" in args.lower():
		filename = args.replace(".log","").replace("--logfile=","")
for files in os.listdir(logfolder):
	if filename in files and "Canceled Commands" not in files and not files.endswith(".json"):
		validfiles.append(logfolder + "\\" +files)
if not validfiles:
	print("Please enter valid filename.")
	exit(0)
with open(logfolder+"\\"+"Canceled Commands " + filename +".log","w") as writeFileHandle:
	for readfiles in validfiles:
		with open(readfiles.replace("\\\\","\\"),"r+") as readFileHandle:
			print(readfiles)
			for line in readFileHandle:
				#Number of Canceled Commands: 1
				Pattern = r'Number of Canceled Commands: | Pending Command Response Count before CancelIO: ([0-9]+)'
				m = re.search(Pattern, line, re.I)
				if m is not None:
					NumberOfCancledCommands += int(m.group(1))
					writeFileHandle.write(line)
	writeFileHandle.write("---------------------------------------------------------------------------------\n")
	writeFileHandle.write("Cancelled commands from {} files are calculated in {}sec\n".format(len(validfiles),round(time.time() - starttime,4)))
	writeFileHandle.write("Total Number of Canceled Commands : "+ str(NumberOfCancledCommands))
