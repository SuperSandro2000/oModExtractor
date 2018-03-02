# Copyright (C) 2018 Sandro Jäckel.  All rights reserved.
#
# This file is part of oMod Extractor.
#
# oMod Extractor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# oMod Extractor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with oMod Extractor.  If not, see <http://www.gnu.org/licenses/>.
import os.path
import shutil
import struct
import subprocess
import sys


def readByte(pos): 
    return struct.unpack('B', data_crc.read(1))[0]

def readInt(pos):
    return struct.unpack('i', data_crc.read(4))[0]

def readInt64(pos):
    return struct.unpack('q', data_crc.read(8))[0]

def readFileName(file):
    pos = file.tell()
    len = readByte(pos)
    #TODO handle < 128
    return file.read(len)

# extract oMod
try:
    fileoMod = sys.argv[1]
except:
    print("Run oModExtractor.py with the oMod as argument.")
    os.system("pause")
    sys.exit(1)

if os.path.exists(fileoMod):
    subprocess.call('7z.exe e "{}" -otemp -y'.format(fileoMod), shell=True)

# variables for holding files that we extract later
tempdir = os.path.join(os.getcwd(), "temp")
filecrc = os.path.join(tempdir, "data.crc")
fileNames = list()
crcs = list()
fileSizes = list()

# get all file information
with open(filecrc, 'rb') as data_crc:
    while data_crc.tell() < os.path.getsize(filecrc):
        fileNames.append(readFileName(data_crc))
        crcs.append(readInt(data_crc))
        fileSizes.append(readInt64(data_crc))

totalSize = sum(fileSizes)
fileData = os.path.join(tempdir, "data")

# rewrite data to be extractable
with open(fileData, 'rb') as file:
    with open(os.path.join(tempdir, "data.rewrite"), 'wb') as output:
        output.write(file.read(5))
        for i in range(8):
            out = totalSize >> (i * 8)
            output.write(struct.pack('B', out & 0xFF))
            dataSize = os.stat(fileData).st_size
        while file.tell() < dataSize:
            output.write(file.read(512))

subprocess.call('7z.exe e "{}" -o{} -y'.format(os.path.join(tempdir, "data.rewrite"), tempdir), shell=True)
modName = os.path.splitext(fileoMod)[0]
# extract files from rewritten data
with open(os.path.join(tempdir, "data"), 'rb') as file:
    for i, name in enumerate(fileNames):
        print("Extracting {}".format(name))
        outFile = os.path.join(os.getcwd(), modName, name)
        if not os.path.exists(os.path.dirname(outFile)):
            os.makedirs(os.path.dirname(outFile))
        with open(outFile, 'wb') as output:
            output.write(file.read(fileSizes[i]))

# remove temp dir
try:
    print("Removing Temp directory")
    shutil.rmtree(tempdir)
except Exception:
    print("Couldn't delete temp dir.")
os.system("pause")