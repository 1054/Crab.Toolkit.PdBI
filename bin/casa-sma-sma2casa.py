#!/usr/bin/env python2.7
"""
sma2casa.py
===========

This file defines functions which will import SMA data directly into a CASA Measurement Set.
"""


# 
# dzliu example:
#     cd /Users/dzliu/Work/SpireLines/Data/NGC0253/spec/SMA_Data_Archive/CO_2-1/raw
#     source /Users/dzliu/Cloud/Github/Crab.Toolkit.PdBI/SETUP.bash
#     casa-sma-sma2casa.py 030922_04:36:59
# 

import os, sys, struct, mmap, argparse
import numpy as np
import astropy
from astropy.io import fits
from astropy.time import Time
from math import sin, cos, pi, sqrt

def csv(value):
    return map(int, value.split(","))

def printChunkSyntax(value):
    print 'Syntax error on chunk specification', value, '- aborting'
    print 'New chunks must be specified with the following syntax:'
    print 'hardwareChunk:startChan:endChan:numberAve'
    print 'Where hardware is the correlator hardware cunk number (1 through 52)'
    print 'startChan is the first channel of hardwareChunk to be included in the new chunk'
    print 'endChan is the last channel of hardwareChunk to be included in the new chunk'
    print 'and numberAve is the number of channels to vector average when producing'
    print 'the new chunk.'
    print '(1+endChan-startChan)/numberAve must be an integer.'
    print 'Example: 50:1024:14335:128 will produce'
    print 'a new chunk from the hardware chunk s50, using channels 1024 through 14335'
    print 'and vector averaging sets of 128 channels to produce 104 output channels'
    print 'The first channel in a hardware chunk is numbered 0, not 1.'
    print 'The -n and its arguments must be the last items on the command line because'
    print 'the parser chews up any additional parameters and tries to interpret them'
    print 'as chunk specifications.'
    sys.exit(-1)

newChunks = {}
nextNewChunkNumber = 53

sWARMForwardChunks = (49,)

def chunkSpec(value):
    global newChunks, nextNewChunkNumber

    nNewChunks = len(value)
    tok = value.split(':')
    if len(tok) < 3:
        printChunkSyntax(value)
    sourceChunkNumber = int(tok[0])
    if not (1 <= sourceChunkNumber <= 52):
        printChunkSyntax(value)
    startChan = int(tok[1])
    if not (0 <= startChan < 16384):
        printChunkSyntax(value)
    endChan = int(tok[2])
    if (not (0 <= endChan < 16384)) or (startChan >= endChan):
        printChunkSyntax(value)
    if len(tok) == 3:
        nChan = 1
    else:
        nChan = int(tok[3])
        if ((1+endChan-startChan) % nChan) != 0:
            printChunkSyntax(value)
    newChunks[nextNewChunkNumber] = (sourceChunkNumber, startChan, endChan, nChan)
    nextNewChunkNumber += 1
    return 1

neededFiles = ('antennas', 'bl_read', 'codes_read', 'in_read', 'sch_read', 'sp_read', 'eng_read')

targetRx = -1
fixRx = False # Set True to force the script to ignore receiver
receiverName = 230
bandList = []
padsDict = {}
spSmallDictL = {}
spSmallDictU = {}
spBigDict = {}
antennas = {}
codesDict = {}
projectPI = 'Dr. John Q Project'
lowestInhid = 1000000
inDict = {}
blDictU = {}
blDictL = {}
blTsysDictL = {}
blTsysDictU = {}
sourceDict = {}
maxScan = 100000000000
maxWeight = 0.01
fieldDict = {}
sourceList = []
numberOfBaselines = 0
antennaList = []
swappingTsys = False
tsysMapping = range(0,11)
trimEdges = False
edgeTrimFraction = 0.1 # Fraction on each edge of a spectral chunk to flag bad
chunkList = range(53)
sidebandList = [0, 1]
pseudoContinuumFrequency = {}
verbose = True
NaN = float('nan')
totalPoints = 0
totalZeros = 0
newFormat = True

def normalize0to360(angle):
    while angle >= 360.0:
        angle -= 360.0
    while angle < 0.0:
        angle += 360.0
    return angle

def toGeocentric(X, Y, Z):
    """
    Transform antenna coordinates to FITS-IDI style GEOCENTRIC coordinates
    """
    SMALong = -2.713594675620429
    SMALat  = 0.3459976585365961
    SMARad  = 6382.248*1000.0
    Rx = SMARad*cos(SMALong)*cos(SMALat)
    Ry = SMARad*sin(SMALong)*cos(SMALat)
    Rz = SMARad*sin(SMALat)
    x = X*cos(SMALong) - Y*sin(SMALong) + Rx
    y = Y*cos(SMALong) + X*sin(SMALong) + Ry
    z = Z + Rz
    return (x, y, z)

def makeInt(data, size):
    tInt = 0
    if newFormat:
        for i in range(size):
            tInt += ord(data[i])<<(i<<3)
    else:
        for i in range(size):
            tInt += ord(data[size-i-1])<<(i<<3)
    return tInt

def makeFloat(data):
    if not newFormat:
        hostByteOrderData = ''
        for i in range(4):
            hostByteOrderData += chr(ord(data[3-i]))
        return (struct.unpack('f', hostByteOrderData[:4]))[0]
    else:
        return (struct.unpack('f', data[:4]))[0]

def makeDouble(data):
    if not newFormat:
        hostByteOrderData = ''
        for i in range(8):
            hostByteOrderData += chr(ord(data[7-i]))
        return (struct.unpack('d', hostByteOrderData[:8]))[0]
    else:
        return (struct.unpack('d', data[:8]))[0]

def read(dataDir):
    global bandList, antennas, codesDict, inDict, blDictL, blDictU, padsDict, targetRx, receiverName, fixRx
    global spSmallDictL, spSmallDictU, spBigDict, sourceDict, maxWeight, numberOfBaselines, sourceList
    global antennaList, blTsysDictL, blTsysDictU, newFormat, pseudoContinuumFrequency, projectPI, lowestInhid

    nameList = []
    # Check that the directory contains all the required files
    if verbose:
        print 'checking that the needed files exist in ', dataDir
    dirContents = os.listdir(dataDir)
    for needed in neededFiles:
        if not needed in dirContents:
            print "The directory %s does not have a %s file - aborting" % (dataDir, needed)
            sys.exit(-1)

    if 'tsys_read' in dirContents:
        gotTsysFile = True
    else:
        gotTsysFile = False

    ###
    ### Determine if this is an old-format or new-format data file
    ###
    f = open(dataDir+'/in_read', 'rb')
    data = f.read()
    firstInt = makeInt(data[0:], 4)
    if firstInt != 0:
        newFormat = True
    else:
        newFormat = False
    f.close()
    if verbose:
        if newFormat:
            print 'This is a new format data set.'
        else:
            print 'This is an old format data set'

    ###
    ### Read in the antennas file - make a dictionary antennas[ant #] = (X, Y, Z)
    ###
    if verbose:
        print 'Reading antennas file'
    for line in open(dataDir+'/antennas'):
        tok = line.split()
        X = float(tok[1])
        Y = float(tok[2])
        Z = float(tok[3])
        antennas[int(tok[0])] = toGeocentric(X, Y, Z)

    ###
    ###  Read in the codes file (codes_read)
    ###  Build a disctionary, codesDict, which has an entry for each unique type of code
    ###  The entries in that disctionary are themselves dictionaries, with integer keys
    ###  pointing to the various entries for that type of code
    ###
    if verbose:
        print 'Reading codes_read'
    f = open(dataDir+'/codes_read', 'rb')
    data = f.read()
    codesRecLen = 42
    nCodesRecords = len(data)/codesRecLen
    # First make a list with all unique code strings
    codeStrings = []
    for rec in range(nCodesRecords):
        codeString = ''
        for i in range(12):
            if data[codesRecLen*rec + i] < ' ':
                break
            if (data[codesRecLen*rec + i] >= ' ') and (data[codesRecLen*rec + i] <= 'z'):
                codeString += data[codesRecLen*rec + i]
        icode = makeInt(data[codesRecLen*rec + 12:], 2)
        payload = ''
        for i in range(14, 14+26):
            if data[codesRecLen*rec + i] < ' ':
                break
            if (data[codesRecLen*rec + i] >= ' ') and (data[codesRecLen*rec + i] <= 'z'):
                payload += data[codesRecLen*rec + i]
        if codeString not in codeStrings:
            codeStrings.append(codeString)
            codesDict[codeString] = {}
        codesDict[codeString][icode] = payload

    ###
    ### Read in bl_read
    ###
    if verbose:
        print 'Reading bl_read'
    f = open(dataDir+'/bl_read', 'rb')
    fSize = os.path.getsize(dataDir+'/bl_read')
    if newFormat:
        blRecLen = 158
    else:
        blRecLen = 118
    nBlRecords = fSize/blRecLen
    baselineList = []
    rxList = []
    blSidebandDict = {}
    for rec in range(nBlRecords):
        if ((rec % 10000) == 0) and verbose:
            print '\t processing record %d of %d (%2.0f%% done)' % (rec, nBlRecords, 100.0*float(rec)/float(nBlRecords))
            sys.stdout.flush()
        data = f.read(blRecLen)
        if len(data) == blRecLen:
            if newFormat:
                blhid     =    makeInt(data[  0:], 4)
                inhid     =    makeInt(data[  4:], 4)
                isb       =    makeInt(data[  8:], 2)
                ipol      =    makeInt(data[ 10:], 2)
                ant1rx    =    makeInt(data[ 12:], 2)
                ant2rx    =    makeInt(data[ 14:], 2)
                pointing  =    makeInt(data[ 16:], 2)
                irec      =    makeInt(data[ 18:], 2)
                u         =  makeFloat(data[ 20:])
                v         =  makeFloat(data[ 24:])
                w         =  makeFloat(data[ 28:])
                prbl      =  makeFloat(data[ 32:])
                coh       =  makeFloat(data[ 36:])
                avedhrs   = makeDouble(data[ 40:])
                ampave    =  makeFloat(data[ 48:])
                phaave    =  makeFloat(data[ 52:])
                blsid     =    makeInt(data[ 56:], 4)
                ant1      =    makeInt(data[ 60:], 2)
                ant2      =    makeInt(data[ 62:], 2)
                ant1TsysOff =  makeInt(data[ 64:], 4)
                ant2TsysOff =  makeInt(data[ 68:], 4)
            else: # old format
                blhid     =    makeInt(data[  0:], 4)
                inhid     =    makeInt(data[  4:], 4)
                isb       =    makeInt(data[  8:], 2)
                ipol      =    makeInt(data[ 10:], 2)
                ant1rx    =    makeInt(data[ 16:], 2)
                ant2rx    =    makeInt(data[ 18:], 2)
                pointing  =    makeInt(data[ 22:], 2)
                irec      =    makeInt(data[ 24:], 2)
                u         =  makeFloat(data[ 28:])
                v         =  makeFloat(data[ 32:])
                w         =  makeFloat(data[ 36:])
                prbl      =  makeFloat(data[ 40:])
                coh       =  makeFloat(data[ 52:])
                avedhrs   = makeDouble(data[ 72:])
                ampave    =  makeFloat(data[ 80:])
                phaave    =  makeFloat(data[ 84:])
                blsid     =    makeInt(data[ 92:], 4)
                ant1      =    makeInt(data[ 96:], 2)
                ant2      =    makeInt(data[ 98:], 2)
                ant1TsysOff =  0
                ant2TsysOff =  0
            if irec not in rxList:
                rxList.append(irec)
                if ((targetRx < 0) and (len(rxList) > 1)) and (not fixRx):
                    print len(rxList), 'receivers were active during this track - this script can only'
                    print "process one receiver's data at a time."
                    print 'You must use the -r switch on this command to specify which receiver to process.'
                    sys.exit(-1)
            if (ant1, ant2) not in baselineList:
                baselineList.append((ant1, ant2))
                numberOfBaselines +=1
            if ant1 not in antennaList:
                antennaList.append(ant1)
            if ant2 not in antennaList:
                antennaList.append(ant2)
            blSidebandDict[blhid] = isb
            if isb == 0:
                blDictL[blhid] = (inhid, ipol, ant1rx, ant2rx, pointing, irec, u, v, w, prbl, coh, avedhrs, ampave, phaave,
                                  blsid, ant1, ant2, ant1TsysOff, ant2TsysOff)
            else:
                blDictU[blhid] = (inhid, ipol, ant1rx, ant2rx, pointing, irec, u, v, w, prbl, coh, avedhrs, ampave, phaave,
                                  blsid, ant1, ant2, ant1TsysOff, ant2TsysOff)
    if ((targetRx >= 0) and (targetRx not in rxList)) and (not fixRx):
        print 'The receiver you specified (%d) was not used in this track - aborting.' % (receiverName)
        sys.exit(-1)
    nAnts = len(antennaList)
    if verbose:
        print '%d antennas and %d baselines seen in this data set.' % (nAnts, numberOfBaselines)
    if numberOfBaselines != (nAnts*(nAnts-1)/2):
        print 'Number of baselines seen inconsistant with the number of antennas - aborting'
        sys.exit(-1)

    ###
    ### Find out which pad each antenna was on from eng_read
    ###
    for i in range(1,9):
        padsDict[i] = 'Not used'
    padsDict[9]  = 'JCMT'
    padsDict[10] = 'CSO'
    if verbose:
        print 'Reading eng_read'
    f = open(dataDir+'/eng_read', 'rb')
    fSize = os.path.getsize(dataDir+'/eng_read')
    if gotTsysFile:
        engFormat = 'new'
    else:
        if ((fSize % 196) == 0) and ((fSize % 188) == 0):
            print 'Unlucky eng_read size - must read the file to detect the format'
            engFormat = '?'
        elif (fSize % 196) == 0:
            print 'New format eng_read file detected'
            engFormat = 'new'
        elif (fSize % 188) == 0:
            print 'Old format eng_read file detected'
            engFormat = 'old'
        else:
            print 'Corrupted eng_read file detected - must abort'
            sys.exit(-1)
    if engFormat == 'old':
        engRecLen = 188
    else:
        engRecLen = 196
    nEngRecords = fSize/engRecLen
    for rec in range(16):
        data = f.read(engRecLen)
        if len(data) == engRecLen:
            ant = makeInt(data[0:], 4)
            pad = makeInt(data[4:], 4)
            if (1 <= ant <= 8) and (1 <= pad <= 26):
                padString = 'Pad %d' % (pad)
                padsDict[ant] = padString
            else:
                print 'Illegal antenna (%d) or pad (%d) detected - this is not a very important error' % (ant, pad)

    if gotTsysFile:
        ###
        ### Pull the Tsys info out of tsys_read
        ###
        if newFormat:
            tsysFile = os.open(dataDir+'/tsys_read', os.O_RDONLY)
            tsysMap = mmap.mmap(tsysFile, 0, prot=mmap.PROT_READ);
            for bl in blDictL:
                ant1Tsys4to6 = makeFloat(tsysMap[blDictL[bl][17]+12:blDictL[bl][17]+16])
                ant1Tsys6to8 = makeFloat(tsysMap[blDictL[bl][17]+28:blDictL[bl][17]+32])
                ant2Tsys4to6 = makeFloat(tsysMap[blDictL[bl][18]+12:blDictL[bl][18]+16])
                ant2Tsys6to8 = makeFloat(tsysMap[blDictL[bl][18]+28:blDictL[bl][18]+32])
                blTsysDictL[bl] = (ant1Tsys4to6, ant1Tsys6to8, ant2Tsys4to6, ant2Tsys6to8)
            for bl in blDictU:
                ant1Tsys4to6 = makeFloat(tsysMap[blDictU[bl][17]+16:blDictU[bl][17]+20])
                ant1Tsys6to8 = makeFloat(tsysMap[blDictU[bl][17]+32:blDictU[bl][17]+36])
                ant2Tsys4to6 = makeFloat(tsysMap[blDictU[bl][18]+16:blDictU[bl][18]+20])
                ant2Tsys6to8 = makeFloat(tsysMap[blDictU[bl][18]+32:blDictU[bl][18]+36])
                blTsysDictU[bl] = (ant1Tsys4to6, ant1Tsys6to8, ant2Tsys4to6, ant2Tsys6to8)
            tsysMap.close()
            os.close(tsysFile)
        else: # Old format file
            if verbose:
                print 'Processing old-format Tsys data'
            antLowDict  = {}
            antHighDict = {}
            f = open(dataDir+'/tsys_read', 'rb')
            fSize = os.path.getsize(dataDir+'/tsys_read')
            tsysRecLen = 400
            nTsysRecords = fSize/tsysRecLen
            for rec in range(nTsysRecords):
                if ((rec % 10000) == 0) and verbose:
                    print '\t processing record %d of %d (%2.0f%% done)' % (rec, nBlRecords, 100.0*float(rec)/float(nBlRecords))
                    sys.stdout.flush()
                data = f.read(tsysRecLen)
                if len(data) == tsysRecLen:
                    inhid    =   makeInt(data[  0:], 4)
                    iAnt     =   makeInt(data[ 14:], 2)
                    tsysLow  = makeFloat(data[ 16:])
                    tsysHigh = makeFloat(data[208:])
                    if (inhid, iAnt) not in antLowDict:
                        antLowDict[(inhid, iAnt)]  = tsysLow
                        antHighDict[(inhid, iAnt)] = tsysHigh
            for bl in blDictL:
                inhid = blDictL[bl][0]
                ant1  = blDictL[bl][15]
                ant2  = blDictL[bl][16]
                blTsysDictL[bl] = (antLowDict[(inhid, ant1)], antHighDict[(inhid, ant1)], antLowDict[(inhid, ant2)], antHighDict[(inhid, ant2)])
            for bl in blDictU:        
                inhid = blDictU[bl][0]
                ant1  = blDictU[bl][15]
                ant2  = blDictU[bl][16]
                blTsysDictU[bl] = (antLowDict[(inhid, ant1)], antHighDict[(inhid, ant1)], antLowDict[(inhid, ant2)], antHighDict[(inhid, ant2)])
    else: # There is no tsys_read file
        print 'This dataset has no tsys_read file - Tsys will be pulled from the eng_read file if it exists'
        if not ('eng_read' in dirContents):
            print 'There is no eng_read file in the dataset - cannot determine Tsys, must abort.'
            sys.exit(-1)
        engFile = os.open(dataDir+'/eng_read', os.O_RDONLY)
        engMap = mmap.mmap(engFile, 0, prot=mmap.PROT_READ);
        engSize = os.path.getsize(dataDir+'/eng_read')
        if engFormat == '?':
            for i in xrange(engSize/196):
                if not (1 <= makeInt(engMap[i*196:], 4) <= 10):
                    print 'New format guess for wrong at record', i
                    engFormat = 'old'
                    break
            else:
                engFormat = 'new'
            print 'Deduced format', engFormat
        engTsysDict = {}
        for i in xrange(engSize/engRecLen):
            ant   = makeInt(engMap[i*engRecLen:], 4)
            inhid = makeInt(engMap[i*engRecLen + 20:], 4)
            tsys1 = makeDouble(engMap[i*engRecLen + 172:])
            if engFormat == 'old':
                tsys2 = tsys1
            else:
                tsys2 = makeDouble(engMap[i*engRecLen + 180:])
            engTsysDict[(ant, inhid)] = (2.0*tsys1, 2.0*tsys2)
        for bl in blDictL:
            inhid = blDictL[bl][0]
            ant1  = blDictL[bl][15]
            ant2  = blDictL[bl][16]
            ant1Tsys4to6 = engTsysDict[(ant1, inhid)][0]
            ant1Tsys6to8 = engTsysDict[(ant1, inhid)][1]
            ant2Tsys4to6 = engTsysDict[(ant2, inhid)][0]
            ant2Tsys6to8 = engTsysDict[(ant2, inhid)][1]
            blTsysDictL[bl] = (ant1Tsys4to6, ant1Tsys6to8, ant2Tsys4to6, ant2Tsys6to8)
        for bl in blDictU:
            inhid = blDictU[bl][0]
            ant1  = blDictU[bl][15]
            ant2  = blDictU[bl][16]
            ant1Tsys4to6 = engTsysDict[(ant1, inhid)][0]
            ant1Tsys6to8 = engTsysDict[(ant1, inhid)][1]
            ant2Tsys4to6 = engTsysDict[(ant2, inhid)][0]
            ant2Tsys6to8 = engTsysDict[(ant2, inhid)][1]
            blTsysDictU[bl] = (ant1Tsys4to6, ant1Tsys6to8, ant2Tsys4to6, ant2Tsys6to8)
        engMap.close()
        os.close(engFile)
    if swappingTsys:
        print 'Swapping Tsys values'
        # Make a mapping dictionary that maps (intergration, antenna) to Tsys
        mapping = {}
        for bl in blDictL:
            mapping[(blDictL[bl][0], blDictL[bl][15])] = (blTsysDictL[bl][0], blTsysDictL[bl][1])
            mapping[(blDictL[bl][0], blDictL[bl][16])] = (blTsysDictL[bl][2], blTsysDictL[bl][3])
        # Now use that mapping table to perform the Tsys substitution
        for bl in blDictL:
            blTsysDictL[bl] = (mapping[(blDictL[bl][0], tsysMapping[blDictL[bl][15]])][0],mapping[(blDictL[bl][0], tsysMapping[blDictL[bl][15]])][1], mapping[(blDictL[bl][0], tsysMapping[blDictL[bl][16]])][0], mapping[(blDictL[bl][0], tsysMapping[blDictL[bl][16]])][1])
        mapping = {}
        for bl in blDictU:
            mapping[(blDictU[bl][0], blDictU[bl][15])] = (blTsysDictU[bl][0], blTsysDictU[bl][1])
            mapping[(blDictU[bl][0], blDictU[bl][16])] = (blTsysDictU[bl][2], blTsysDictU[bl][3])
        # Now use that mapping table to perform the Tsys substitution
        for bl in blDictU:
            blTsysDictU[bl] = (mapping[(blDictU[bl][0], tsysMapping[blDictU[bl][15]])][0],mapping[(blDictU[bl][0], tsysMapping[blDictU[bl][15]])][1], mapping[(blDictU[bl][0], tsysMapping[blDictU[bl][16]])][0], mapping[(blDictU[bl][0], tsysMapping[blDictU[bl][16]])][1])

    ###
    ### Count the number of spectral bands
    ###
    weightDict = {}
    if verbose:
        print 'Counting the number of bands'
    f = open(dataDir+'/sp_read', 'rb')
    fSize = os.path.getsize(dataDir+'/sp_read')
    if newFormat:
        spRecLen = 188
    else:
        spRecLen = 100
    data = f.read(spRecLen)
    nSpRecords = fSize/spRecLen
    for rec in range(nSpRecords):
        if ((rec % 100000) == 0) and verbose:
            print '\t processing record %d of %d (%2.0f%% done)' % (rec, nSpRecords, 100.0*float(rec)/float(nSpRecords))
            sys.stdout.flush()
        data = f.read(spRecLen)
        if len(data) == spRecLen:
            if newFormat:
                sphid     =    makeInt(data[  0:], 4)
                blhid     =    makeInt(data[  4:], 4)
                inhid     =    makeInt(data[  8:], 4)
                igq       =    makeInt(data[ 12:], 2)
                ipq       =    makeInt(data[ 14:], 2)
                iband     =    makeInt(data[ 16:], 2)
                fsky      = makeDouble(data[ 36:])
                fres      =  makeFloat(data[ 44:])
                wt        =  makeFloat(data[ 84:])
                flags     =    makeInt(data[ 88:], 4)
                nch       =    makeInt(data[ 96:], 2)
                dataoff   =    makeInt(data[100:], 4)
                rfreq     = makeDouble(data[104:])
            else:
                sphid     =    makeInt(data[  0:], 4)
                blhid     =    makeInt(data[  4:], 4)
                inhid     =    makeInt(data[  8:], 4)
                igq       =    makeInt(data[ 12:], 2)
                ipq       =    makeInt(data[ 14:], 2)
                iband     =    makeInt(data[ 16:], 2)
                fsky      = makeDouble(data[ 38:])
                fres      =  makeFloat(data[ 46:])
                wt        =  makeFloat(data[ 58:])
                if wt > 0:
                    flags = 0
                else:
                    flags = -1
                nch       =    makeInt(data[ 68:], 2)
                dataoff   =    makeInt(data[ 72:], 4)
                rfreq     = makeDouble(data[ 82:])
            try:
                ibandRx = blDictU[blhid][5]
            except:
                ibandRx = blDictL[blhid][5]
            if ((targetRx < 0) or (ibandRx == targetRx)) or fixRx:
                rightRx = True
            else:
                rightRx = False
            if (flags != 0) and (wt > 0):
                wt *= -1.0
            if rightRx:
                spBigDict[(iband, blhid)] = (dataoff, wt)
            try:
                if weightDict[inhid] < wt:
                    weightDict[inhid] = wt
            except KeyError:
                weightDict[inhid] = wt
            if rightRx:
                if iband not in bandList:
                    bandList.append(iband)
                try:
                    if (nch == 1) and (blSidebandDict[blhid] not in pseudoContinuumFrequency):
                        pseudoContinuumFrequency[blSidebandDict[blhid]] = fsky*1.0e9
                    if blSidebandDict[blhid] == 0:
                        wt = wt/(max(blTsysDictL[blhid][0], blTsysDictL[blhid][1])*max(blTsysDictL[blhid][2], blTsysDictL[blhid][3]))
                        if iband not in spSmallDictL:
                            spSmallDictL[iband] = (nch, fres*1.0e6, fsky*1.0e9, rfreq*1.0e9)
                    else:
                        wt = wt/(max(blTsysDictU[blhid][0], blTsysDictU[blhid][1])*max(blTsysDictU[blhid][2], blTsysDictU[blhid][3]))
                        if iband not in spSmallDictU:
                            spSmallDictU[iband] = (nch, fres*1.0e6, fsky*1.0e9, rfreq*1.0e9)
                except KeyError:
                    # This exception can occur if the last record to bl_read was not written, because dataCatcher was interrupted
                    wt = -1.0
                if abs(wt) > maxWeight:
                    maxWeight = abs(wt)
        if inhid > maxScan:
            break
    bandList.sort()

    ###
    ### Read in the integration header information (in_read)
    ### Produces a disctionary with integration numbers for the
    ### keys, and tuples holding the entry values
    ###
    if verbose:
        print 'Reading in_read'
    f = open(dataDir+'/in_read', 'rb')
    data = f.read()
    if newFormat:
        inRecLen = 188
    else:
        inRecLen = 132
    nInRecords = len(data)/inRecLen
    for rec in range(nInRecords):
        if newFormat:
            traid     =    makeInt(data[rec*inRecLen +   0:], 4)
            inhid     =    makeInt(data[rec*inRecLen +   4:], 4)
            az        =  makeFloat(data[rec*inRecLen +  12:])
            el        =  makeFloat(data[rec*inRecLen +  16:])
            hA        =  makeFloat(data[rec*inRecLen +  20:])
            iut       =    makeInt(data[rec*inRecLen +  24:], 2)
            iref_time =    makeInt(data[rec*inRecLen +  26:], 2)
            dhrs      = makeDouble(data[rec*inRecLen +  28:])
            vc        =  makeFloat(data[rec*inRecLen +  36:])
            sx        = makeDouble(data[rec*inRecLen +  40:])
            sy        = makeDouble(data[rec*inRecLen +  48:])
            sz        = makeDouble(data[rec*inRecLen +  56:])
            rinteg    =  makeFloat(data[rec*inRecLen +  64:])
            proid     =    makeInt(data[rec*inRecLen +  68:], 4)
            souid     =    makeInt(data[rec*inRecLen +  72:], 4)
            isource   =    makeInt(data[rec*inRecLen +  76:], 2)
            ivrad     =    makeInt(data[rec*inRecLen +  78:], 2)
            offx      =  makeFloat(data[rec*inRecLen +  80:])
            offy      =  makeFloat(data[rec*inRecLen +  84:])
            ira       =    makeInt(data[rec*inRecLen +  88:], 2)
            idec      =    makeInt(data[rec*inRecLen +  90:], 2)
            rar       = makeDouble(data[rec*inRecLen +  92:])
            decr      = makeDouble(data[rec*inRecLen + 100:])
            epoch     =  makeFloat(data[rec*inRecLen + 108:])
            size      =  makeFloat(data[rec*inRecLen + 112:])
        else: # Old format file
            traid     =    makeInt(data[rec*inRecLen +   6:], 4)
            inhid     =    makeInt(data[rec*inRecLen +  10:], 4)
            az        =  makeFloat(data[rec*inRecLen +  20:])
            el        =  makeFloat(data[rec*inRecLen +  24:])
            hA        =  makeFloat(data[rec*inRecLen +  28:])
            iut       =    makeInt(data[rec*inRecLen +  32:], 2)
            iref_time =    makeInt(data[rec*inRecLen +  34:], 2)
            dhrs      = makeDouble(data[rec*inRecLen +  36:])
            vc        =  makeFloat(data[rec*inRecLen +  44:])
            sx        = makeDouble(data[rec*inRecLen +  50:])
            sy        = makeDouble(data[rec*inRecLen +  58:])
            sz        = makeDouble(data[rec*inRecLen +  66:])
            rinteg    =  makeFloat(data[rec*inRecLen +  74:])
            proid     =    makeInt(data[rec*inRecLen +  78:], 4)
            souid     =    makeInt(data[rec*inRecLen +  82:], 4)
            isource   =    makeInt(data[rec*inRecLen +  86:], 2)
            ivrad     =    makeInt(data[rec*inRecLen +  88:], 2)
            offx      =  makeFloat(data[rec*inRecLen +  90:])
            offy      =  makeFloat(data[rec*inRecLen +  94:])
            ira       =    makeInt(data[rec*inRecLen + 100:], 2)
            idec      =    makeInt(data[rec*inRecLen + 102:], 2)
            rar       = makeDouble(data[rec*inRecLen + 104:])
            decr      = makeDouble(data[rec*inRecLen + 112:])
            epoch     =  makeFloat(data[rec*inRecLen + 120:])
            size      =  makeFloat(data[rec*inRecLen + 128:])
        inDict[inhid] = (traid, inhid, az, el, hA, iut, iref_time, dhrs, vc, sx, sy, sz,
                         rinteg, proid, souid, isource, ivrad, offx, offy, ira, idec, rar, decr, epoch, size, weightDict[inhid])
        if inhid < lowestInhid:
            lowestInhid = inhid
        fieldKey = (souid, round(offx), round(offy))
        if ((not (fieldKey in fieldDict)) and (weightDict[inhid] > 0.0)):
            fieldDict[fieldKey] = (codesDict['source'][isource], offx, offy, rar, decr)
            if codesDict['source'][isource] not in nameList:
                nameList.append(codesDict['source'][isource])
                sourceList.append((codesDict['source'][isource], rar, decr))
        if (souid not in sourceDict) and (weightDict[inhid] > 0.0):
                sourceDict[souid] = (codesDict['source'][isource], rar, decr)

parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description='Convert an SMA MIR format dataset into a set of FITS-IDI files which may be imported into CASA.')
parser.add_argument('dataset',           help='The data directory to process (i.e. /sma/rtdata/...)')
parser.add_argument('-c', '--chunk',     help='Chunk(s) to process (comma separated list)',           type=csv)
group1 = parser.add_mutually_exclusive_group()
group1.add_argument('-l', '--lower',     help='Process lower sideband only',                  action='store_true')
parser.add_argument('-n', '--newChunk', 
                    help='Define a new chunk, built from an existing chunk with channel averaging and/or trimming. Syntax: -n hardwareChunk:startChan:endChan:numberChan',
                    nargs='+', type=chunkSpec)
parser.add_argument('-p', '--percent',   help='Percentage to trim on band edge (default = %0.0f) - implies -t' % (edgeTrimFraction*100.0),
                    type=float)
group1.add_argument('-P', '--PythonOnly', help='Do not use the C module "makevis" - use pure Python (slow)', action='store_true')
parser.add_argument('-r', '--receiver',  help='Specify the receiver (required for multi-receiver tracks)', type=int, choices=[230, 240, 345, 400])
parser.add_argument('-R', '--RxFix',     help='Force the script to treat the track as a single receiver track', action='store_true')
parser.add_argument('-s', '--silent',    help='Run silently unless an error occurs', action='store_true')
parser.add_argument('-t', '--trim',      help='Set the amplitude at chunk edges to 0.0', action='store_true')
parser.add_argument('-T', '--Tsys',      help="-T n=m means use ant m's Tsys for ant n")
group1.add_argument('-u', '--upper',     help='Process upper sideband only',                  action='store_true')
parser.add_argument('-w', '--withoutChunk', help='Chunk(s) NOT to process (comma separated list)',           type=csv)

args = parser.parse_args()
dataSet = args.dataset
if args.chunk:
    chunkList = args.chunk
    for chunk in chunkList:
        if (chunk < 0) or (chunk > 52):
            print 'Illegal chunk number', chunk,'specified - aborting'
            sys.exit(-1)
if args.withoutChunk:
    for chunk in args.withoutChunk:
        if (chunk < 0) or (chunk > 52):
            print 'Illegal chunk number', chunk,'specified - aborting'
            sys.exit(-1)
        else:
            chunkList.remove(chunk)
if args.lower:
    sidebandList = [0]
if args.upper:
    sidebandList = [1]
if args.percent:
    edgeTrimFraction = args.percent/100.0
    trimEdges = True
if args.PythonOnly:
    useMakevis = False
else:
    useMakevis = True
if args.receiver:
    receiverName = args.receiver
    if receiverName == 230:
        targetRx = 0
    elif receiverName == 345:
        targetRx = 1
    elif receiverName == 400:
        targetRx = 2
    else:
        targetRx = 3
if args.RxFix:
    fixRx = True
if args.silent:
    verbose = False
if args.trim:
    trimEdges = True
if args.Tsys:
    donee = int(args.Tsys[0])
    doner = int(args.Tsys[2])
    tsysMapping[donee] = doner
    swappingTsys = True
if useMakevis:
    if verbose:
        print 'Importing makevis'
    import makevis
    print("dzliu debug: makevis imported")
if verbose:
    for a in range(1,9):
        if a != tsysMapping[a]:
            print 'Antenna %d will use the Tsys from antenna %d' % (a, tsysMapping[a])
read(dataSet)
sourceTable = open('sourceTable', 'w')
if len(sourceList) > 0:
    for i in range(len(sourceList)):
        print >>sourceTable, i, sourceList[i][0], sourceList[i][1], sourceList[i][2]
sourceTable.close()

try:
    for line in open(dataSet+'/projectInfo'):
        projectPI = line.strip()
except IOError:
    print "There is no projectInfo file - I'll be unable to set the PI name properly"
    projectPI = 'Unknown PI'

if useMakevis:
    visFileLen = makevis.open(dataSet+'/sch_read')
else:
    visFile = os.open(dataSet+'/sch_read', os.O_RDONLY)
    visMap = mmap.mmap(visFile, 0, prot=mmap.PROT_READ);
for band in newChunks:
    bandList.append(band)
    chunkList.append(band)
bandList = sorted(bandList)
print("dzliu debug: bandList = %s"%(bandList))
for band in bandList:
    for sb in range(2):
        if (band in chunkList) and (sb in sidebandList):
            if band in newChunks:
                fakeChunk = True
            else:
                fakeChunk = False
            if sb == 0:
                sideBand = 'Lower'
                blDict = blDictL
                blTsysDict = blTsysDictL
                spSmallDict = spSmallDictL
            else:
                sideBand = 'Upper'
                blDict = blDictU
                blTsysDict = blTsysDictU
                spSmallDict = spSmallDictU
            if fakeChunk:
                if sb == 0:
                    startCh = float(newChunks[band][1])
                    endCh   = float(newChunks[band][2])
                    nCh     = spSmallDict[newChunks[band][0]][0]
                    midCh = startCh + (endCh - startCh)/2.0
                    nChNew  = 1.0+endCh-startCh
                    freqInc = float(newChunks[band][3]-1)/2.0
                    centerFSky = spSmallDict[newChunks[band][0]][2] + (midCh - nCh*0.5)*spSmallDict[newChunks[band][0]][1]
                    if (newChunks[band][0]) < 49:
                        lowestFSky = spSmallDict[newChunks[band][0]][2] - spSmallDict[newChunks[band][0]][1]*0.5 - spSmallDict[newChunks[band][0]][1]*spSmallDict[newChunks[band][0]][0]*0.5 + (startCh+freqInc)*abs(spSmallDict[newChunks[band][0]][1])
                    elif newChunks[band][0] in sWARMForwardChunks:
                        lowestFSky = spSmallDict[newChunks[band][0]][2] - spSmallDict[newChunks[band][0]][1]*0.5 + spSmallDict[newChunks[band][0]][1]*spSmallDict[newChunks[band][0]][0]*0.5 + (startCh+freqInc)*abs(spSmallDict[newChunks[band][0]][1])
                    else:
                        lowestFSky = spSmallDict[newChunks[band][0]][2] - spSmallDict[newChunks[band][0]][1]*0.5 - spSmallDict[newChunks[band][0]][1]*spSmallDict[newChunks[band][0]][0]*0.5 + (startCh+freqInc)*abs(spSmallDict[newChunks[band][0]][1])
                else:
                    startCh = float(newChunks[band][1])
                    endCh   = float(newChunks[band][2])
                    nCh     = spSmallDict[newChunks[band][0]][0]
                    midCh = startCh + (endCh - startCh)/2.0
                    nChNew  = 1.0+endCh-startCh
                    freqInc = float(newChunks[band][3]-1)/2.0
                    centerFSky = spSmallDict[newChunks[band][0]][2] - (midCh - nCh*0.5)*spSmallDict[newChunks[band][0]][1]
                    if (newChunks[band][0]) < 49:
                        lowestFSky = spSmallDict[newChunks[band][0]][2] + spSmallDict[newChunks[band][0]][1]*0.5  - spSmallDict[newChunks[band][0]][1]*spSmallDict[newChunks[band][0]][0]*0.5 + (startCh+freqInc)*abs(spSmallDict[newChunks[band][0]][1])
                    elif newChunks[band][0] in sWARMForwardChunks:
                        lowestFSky = spSmallDict[newChunks[band][0]][2] + spSmallDict[newChunks[band][0]][1]*0.5 - spSmallDict[newChunks[band][0]][1]*spSmallDict[newChunks[band][0]][0]*0.5 + (startCh+freqInc)*abs(spSmallDict[newChunks[band][0]][1])
                    else:
                        lowestFSky = spSmallDict[newChunks[band][0]][2] + spSmallDict[newChunks[band][0]][1]*0.5 + spSmallDict[newChunks[band][0]][1]*spSmallDict[newChunks[band][0]][0]*0.5 + (startCh+freqInc)*abs(spSmallDict[newChunks[band][0]][1])

                originalNChan = spSmallDict[newChunks[band][0]][0]
                spSmallDict[band] = (int(nChNew/newChunks[band][3]), spSmallDict[newChunks[band][0]][1]*newChunks[band][3], 
                                     centerFSky, spSmallDict[newChunks[band][0]][3], originalNChan)
                keyList = []
                for key, value in spBigDict.iteritems():
                    if key[0] == newChunks[band][0]:
                        keyList.append((key, value))
                for key in keyList:
                    spBigDict[(band, key[0][1])] = key[1]
            else:
                if band < 49:
                    if sb == 0:
                        lowestFSky = spSmallDict[band][2] - spSmallDict[band][1]*0.5 - 52.0e6
                    else:
                        lowestFSky = spSmallDict[band][2] + spSmallDict[band][1]*0.5 - 52.0e6
                elif band in sWARMForwardChunks:
                    if sb == 0:
                        lowestFSky = spSmallDict[band][2] - spSmallDict[band][1]*0.5 + spSmallDict[band][1]*spSmallDict[band][0]*0.5
                    else:
                        lowestFSky = spSmallDict[band][2] + spSmallDict[band][1]*0.5 - spSmallDict[band][1]*spSmallDict[band][0]*0.5
                else:
                    if sb == 0:
                        lowestFSky = spSmallDict[band][2] - spSmallDict[band][1]*0.5 - spSmallDict[band][1]*spSmallDict[band][0]*0.5
                    else:
                        lowestFSky = spSmallDict[band][2] + spSmallDict[band][1]*0.5 + spSmallDict[band][1]*spSmallDict[band][0]*0.5

            ###
            ### Make the Primary HDU
            ###
            hdu = fits.PrimaryHDU()
            hdulist=fits.HDUList([hdu])
            header = hdulist[0].header
            header['groups'] = True
            header['gcount'] = 0
            header['pcount'] = 0
            if (band == 0) and ((49 in bandList) or (50 in bandList) or (51 in bandList) or (52 in bandList)):
                header['correlat'] = 'SMA-Hybrid'
            elif band < 49:
                header['correlat'] = 'SMA-Legacy'
            else:
                header['correlat'] = 'SMA-SWARM'
            header['fxcorver'] = 1
            header.add_history('Translated to FITS-IDI by sma2casa.py')
            header.add_history('Original SMA dataset: '+dataSet[-15:])
            header.add_history('Project PI: '+projectPI)
            del header

            ###
            ### Make the ARRAY_GEOMETRY table
            ###
            refTimeString = codesDict['ref_time'][0][-4:]
            mon = codesDict['ref_time'][0][:3]
            if mon == 'Jan':
                refTimeString += '-01-'
            elif mon == 'Feb':
                refTimeString += '-02-'
            elif mon == 'Mar':
                refTimeString += '-03-'
            elif mon == 'Apr':
                refTimeString += '-04-'
            elif mon == 'May':
                refTimeString += '-05-'
            elif mon == 'Jun':
                refTimeString += '-06-'
            elif mon == 'Jul':
                refTimeString += '-07-'
            elif mon == 'Aug':
                refTimeString += '-08-'
            elif mon == 'Sep':
                refTimeString += '-09-'
            elif mon == 'Oct':
                refTimeString += '-10-'
            elif mon == 'Nov':
                refTimeString += '-11-'
            else:
                refTimeString += '-12-'
            day = int(codesDict['ref_time'][0][4:6])
            refTimeString = '%s%02d' % (refTimeString, day)
            jD = Time(refTimeString, scale='utc').jd
            T = (jD - 2451545.0)/36525.0
            gST = 100.46061837 + 36000.770053608*T + 0.000387933*T**2 - (T**3)/38710000.0
            gST = normalize0to360(gST)
            antNames = np.array(['SMA1    ','SMA2    ','SMA3    ','SMA4    ','SMA5    ','SMA6    ','SMA7    ','SMA8    '])
            antList = []
            velList = []
            antNumList = []
            antStyleList = []
            antOffList = []
            antDiameterList = []
            for ant in range(1, 9):
                antList.append(antennas[ant])
                velList.append((0.0, 0.0, 0.0))
                antNumList.append(ant)
                antStyleList.append(0)
                antOffList.append((0.0, 0.0, 0.0))
                antDiameterList.append(6.0)
            c1 = fits.Column(name='ANNAME',   format='8A', array=antNames                        )
            c2 = fits.Column(name='STABXYZ',  format='3D', array=antList,         unit='METERS'  )
            c3 = fits.Column(name='DERXYZ',   format='3E', array=velList,         unit='METERS/S')
            c4 = fits.Column(name='NOSTA',    format='1J', array=antNumList                      )
            c5 = fits.Column(name='MNTSTA',   format='1J', array=antStyleList                    )
            c6 = fits.Column(name='STAXOF',   format='3E', array=antOffList                      )
            c7 = fits.Column(name='DIAMETER', format='1E', array=antDiameterList, unit='METERS'  )
            coldefs = fits.ColDefs([c1, c2, c3, c4, c5, c6, c7])
            arrayGeometryHDU = fits.BinTableHDU.from_columns(coldefs)
            header = arrayGeometryHDU.header
            header['extname']  = 'ARRAY_GEOMETRY'
            header['frame']    = 'GEOCENTRIC'
            header['arrnam']   = 'SMA'
            header['tabrev']   = 1
            header['obscode']  =  ' '
            header['extver']   = (1,                         'Array number')
            header['arrayx']   = (0.0,                       'Array origin x coordinate')
            header['arrayy']   = (0.0,                       'Array origin y coordinate')
            header['arrayz']   = (0.0,                       'Array origin z coordinate')
            header['numorb']   = (0,                         'Number of orbital parameters')
            header['polarx']   = (0.0,                       'x coordinate of north pole (arcsec)')
            header['polary']   = (0.0,                       'y coordinate of north pole (arcsec)')
            header['freq']     = (lowestFSky,                'Reference frequency')
            header['timesys']  = ('UTC',                     'Time system')
            header['degpdy']   = (0.0,                       'Earth rotation rate')
            header['ut1utc']   = (0.0,                       'UT1 - UTC (seconds) - PLACEHOLDER')
            header['iatutc']   = (0.0,                       'IAT - UTC (seconds) - PLACEHOLDER')
            header['rdate']    = (refTimeString,             'Reference date')
            header['gstia0']   = (gST,                       'GST at 0h on reference date (degrees)')
            header['no_stkd']  = (1,                         'Number of Stokes parameters')
            header['stk_1']    = (-2,                        'First Stokes parameter')
            header['no_band']  = (1,                         'Number of bands')
            header['ref_freq'] = (lowestFSky,                'File reference frequency')
            header['ref_pixl'] = (1,                         'Reference pixel')
            header['no_chan']  = (spSmallDict[band][0],      'The number of spectral channels')
            header['chan_bw']  = (abs(spSmallDict[band][1]), 'The channel bandwidth')
            for ii in range(1,11):
                header.add_history('Ant %d was on pad %s' % (ii, padsDict[ii]))
            del header

            ###
            ### Make the SOURCE table
            ###
            iDList   = []
            nameList = []
            qualList = []
            calList  = []
            freqList = []
            fluxList = []
            rAList   = []
            decList  = []
            eqList   = []
            velList  = []
            vtList   = []
            vdList   = []
            restList = []
            validSourceNumbers = []

            fieldMapping = {}
            source = 1
            for fKey in sorted(fieldDict):
                fieldMapping[fKey] = source
                fSource = int(fKey[0])
                if not fSource in validSourceNumbers:
                    validSourceNumbers.append(fSource)
                iDList.append(source)
                nameList.append(fieldDict[fKey][0])
                qualList.append(0)
                calList.append('    ')
                freqList.append(1)
                fluxList.append(0.0)
                rAList.append(fieldDict[fKey][3]*180.0/pi)
                decList.append(fieldDict[fKey][4]*180.0/pi)
                eqList.append('J2000')
                velList.append(inDict[0+lowestInhid][8]*1000.0)
                vtList.append('LSR')
                vdList.append('RADIO')
                restList.append(lowestFSky)
                source += 1

            c1  = fits.Column(name='SOURCE_ID',   format='1J',  array=iDList  )
            c2  = fits.Column(name='SOURCE',      format='16A', array=nameList)
            c3  = fits.Column(name='QUAL',        format='1J',  array=qualList)
            c4  = fits.Column(name='CALCODE',     format='4A',  array=calList )
            c5  = fits.Column(name='FREQID',      format='1J',  array=freqList)
            c6  = fits.Column(name='IFLUX',       format='E1',  array=fluxList)
            c7  = fits.Column(name='QFLUX',       format='E1',  array=fluxList)
            c8  = fits.Column(name='UFLUX',       format='E1',  array=fluxList)
            c9  = fits.Column(name='VFLUX',       format='E1',  array=fluxList)
            c10 = fits.Column(name='ALPHA',       format='E1',  array=fluxList)
            c11 = fits.Column(name='FREQOFF',     format='E1',  array=fluxList)
            c12 = fits.Column(name='RAEPO',       format='1D',  array=rAList  )
            c13 = fits.Column(name='DECEPO',      format='1D',  array=decList )
            c14 = fits.Column(name='EQUINOX',     format='8A',  array=eqList  )
            c15 = fits.Column(name='RAAPP',       format='1D',  array=rAList  )
            c16 = fits.Column(name='DECAPP',      format='1D',  array=decList )
            c17 = fits.Column(name='SYSVEL',      format='D' ,  array=velList )
            c18 = fits.Column(name='VELTYP',      format='8A',  array=vtList  )
            c19 = fits.Column(name='VELDEF',      format='8A',  array=vdList  )
            c20 = fits.Column(name='RESTFREQ',    format='D' ,  array=restList)
            c21 = fits.Column(name='PMRA',        format='D' ,  array=fluxList)
            c22 = fits.Column(name='PMDEC',       format='D' ,  array=fluxList)
            c23 = fits.Column(name='PARALLAX',    format='E' ,  array=fluxList)
            coldefs = fits.ColDefs([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16,
                                      c17, c18, c19, c20, c21, c22, c23])
            sourceHDU = fits.BinTableHDU.from_columns(coldefs)
            header = sourceHDU.header
            header['extname']  =  'SOURCE'
            header['tabrev']   =  1
            header['obscode']  = ' '
            header['no_stkd']  = (1,                         'Number of Stokes parameters')
            header['stk_1']    = (-2,                        'First Stokes parameter')
            header['no_band']  = (1,                         'Number of bands')
            header['no_chan']  = (spSmallDict[band][0],      'The number of spectral channels')
            header['ref_freq'] = (lowestFSky,                'File reference frequency')
            header['chan_bw']  = (abs(spSmallDict[band][1]), 'The channel bandwidth')
            header['ref_pixl'] = (1,                         'Reference pixel')
            del header

            ###
            ### Create the FREQUENCY table
            ###
            c1  = fits.Column(name='FREQID',         format='1J',  array=[1]  )
            c2  = fits.Column(name='BANDFREQ',        format='D',   array=[0.0])
            c3  = fits.Column(name='CH_WIDTH',        format='1E' ,  array=[abs(spSmallDict[band][1])])
            c4  = fits.Column(name='TOTAL_BANDWIDTH', format='1E',  array=[abs(spSmallDict[band][1])*float(spSmallDict[band][0])])
            if sideBand == 'Upper':
                c5  = fits.Column(name='SIDEBAND',        format='1J',  array=[1] )
            else:
                c5  = fits.Column(name='SIDEBAND',        format='1J',  array=[-1])
            coldefs = fits.ColDefs([c1, c2, c3, c4, c5])
            frequencyHDU = fits.BinTableHDU.from_columns(coldefs)
            header = frequencyHDU.header
            header['extname']  =  'FREQUENCY'
            header['tabrev']   =   1
            header['obscode']  =  ' '
            header['no_stkd']  = (1,                         'Number of Stokes parameters')
            header['stk_1']    = (-2,                        'First Stokes parameter')
            header['no_band']  = (1,                         'Number of bands')
            header['no_chan']  = (spSmallDict[band][0],      'The number of spectral channels')
            header['ref_freq'] = (lowestFSky,                'File reference frequency')
            header['chan_bw']  = (abs(spSmallDict[band][1]), 'The channel bandwidth')
            header['ref_pixl'] = (1,                         'Reference pixel')
            del header

            ###
            ### Create the ANTENNA table
            ###
            timeList = []
            timeIntList = []
            arrayList = []
            levelsList = []
            polAList = []
            polBList = []
            polCalAList = []
            for ant in range(1, 9):
                timeList.append(0.0)
                timeIntList.append(1.0)
                arrayList.append(1)
                levelsList.append(2)
                polAList.append('L')
                polBList.append('R')
                polCalAList.append([0.0, 0.0])
            c1  = fits.Column(name='TIME',          format='D',  array=timeList   )
            c2  = fits.Column(name='TIME_INTERVAL', format='E',  array=timeIntList)
            c3  = fits.Column(name='ANNAME',        format='8A', array=antNames   )
            c4  = fits.Column(name='ANTENNA_NO',    format='J', array=antNumList )
            c5  = fits.Column(name='ARRAY',         format='J',  array=arrayList  )
            c6  = fits.Column(name='FREQID',        format='J',  array=arrayList  )
            c7  = fits.Column(name='NO_LEVELS',     format='J',  array=levelsList )
            c8  = fits.Column(name='POLTYA',        format='1A', array=polAList   )
            c9  = fits.Column(name='POLAA',         format='E',  array=timeList   )
            c10 = fits.Column(name='POLCALA',       format='2E', array=polCalAList)
            c11 = fits.Column(name='POLTYB',        format='1A', array=polBList   )
            c12 = fits.Column(name='POLAB',         format='E',  array=timeList   )
            c13 = fits.Column(name='POLCALB',       format='2E', array=polCalAList)
            coldefs = fits.ColDefs([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13])
            antennaHDU = fits.BinTableHDU.from_columns(coldefs)
            header = antennaHDU.header
            header['extname']  =  'ANTENNA'
            header['nopcal']   =   2
            header['poltype']  = 'APPROX'
            header['tabrev']   =   1
            header['obscode']  =  ' '
            header['no_stkd']  = (1,                         'Number of Stokes parameters')
            header['stk_1']    = (-2,                        'First Stokes parameter')
            header['no_band']  = (1,                         'Number of bands')
            header['no_chan']  = (spSmallDict[band][0],      'The number of spectral channels')
            header['ref_freq'] = (lowestFSky,                'File reference frequency')
            header['chan_bw']  = (abs(spSmallDict[band][1]), 'The channel bandwidth')
            header['ref_pixl'] = (1,                         'Reference pixel')
            del header

            ###
            ### Create the SYSTEM_TEMPERATURE table
            ###
            blKeysSorted = sorted(blDict)
            blPos = 0
            scanDict = {}
            antTsysDict = {}
            inKeysSorted = sorted(inDict)
            antennaListSorted = sorted(antennaList)
            for inh in inKeysSorted:
                scanDict[inh] = (inDict[inh][7]/24.0, inDict[inh][12]/86400.0, inDict[inh][14])
                antCount = 0
                antList = []
                for bl in blKeysSorted[blPos:]:
                    if blDict[bl][0] == inh:
                        ant1 = blDict[bl][15]
                        ant2 = blDict[bl][16]
                        if ant1 not in antList:
                            antList.append(ant1)
                            antCount += 1
                            antTsysDict[(inh, ant1, 1)] = blTsysDict[bl][0]*0.5
                            antTsysDict[(inh, ant1, 2)] = blTsysDict[bl][1]*0.5
                        if ant2 not in antList:
                            antList.append(ant2)
                            antCount += 1
                            antTsysDict[(inh, ant2, 1)] = blTsysDict[bl][2]*0.5
                            antTsysDict[(inh, ant2, 2)] = blTsysDict[bl][3]*0.5
                        blPos += 1
                        if antCount == len(antennaList):
                            break
                if antCount != len(antennaList):
                    print 'Only %d antenna entries found for scan %d - aborting' % (antCount, inh)
                    sys.exit(-1)
            timeList = []
            intervalList = []
            sourceList = []
            antList = []
            allOnesList = []
            tsys1List = []
            tsys2List = []
            nanList = []
            for inh in inKeysSorted:
                for ant in antennaListSorted:
                    timeList.append(scanDict[inh][0])
                    intervalList.append(scanDict[inh][1])
                    sourceList.append(scanDict[inh][2])
                    antList.append(ant)
                    allOnesList.append(1)
                    tsys1List.append(antTsysDict[(inh, ant, 1)])
                    tsys2List.append(antTsysDict[(inh, ant, 2)])
                    nanList.append(NaN)
            c1  = fits.Column(name='TIME',          format='1D',  array=timeList    )
            c2  = fits.Column(name='TIME_INTERVAL', format='1E',  array=intervalList)
            c3  = fits.Column(name='SOURCE_ID',     format='1J',  array=sourceList  )
            c4  = fits.Column(name='ANTENNA_NO',    format='1J',  array=antList     )
            c5  = fits.Column(name='ARRAY',         format='1J',  array=allOnesList )
            c6  = fits.Column(name='FREQID',        format='1J',  array=allOnesList )
            c7  = fits.Column(name='TSYS_1',        format='E',   array=tsys1List   )
            c8  = fits.Column(name='TANT_1',        format='E',   array=nanList     )
            c9  = fits.Column(name='TSYS_2',        format='E',   array=tsys2List   )
            c10 = fits.Column(name='TANT_2',        format='E',   array=nanList     )
            coldefs = fits.ColDefs([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10])
            tsysHDU = fits.BinTableHDU.from_columns(coldefs)
            header = tsysHDU.header
            header['extname']  = 'SYSTEM_TEMPERATURE'
            header['tabrev']   =  1
            header['no_pol']   = 2
            header['obscode']  = ' '
            header['no_stkd']  = (1,                         'Number of Stokes parameters')
            header['stk_1']    = (-2,                        'First Stokes parameter')
            header['no_band']  = (1,                         'Number of bands')
            header['no_chan']  = (spSmallDict[band][0],      'The number of spectral channels')
            header['ref_freq'] = (lowestFSky,                'File reference frequency')
            header['chan_bw']  = (abs(spSmallDict[band][1]), 'The channel bandwidth')
            header['ref_pixl'] = (1,                         'Reference pixel')
            del header

            ###
            ### Create the UV_DATA table
            ###
            if spSmallDict[band][1] < 0:
                reverseChannelOrder = True
            else:
                reverseChannelOrder = False
            scanOffset = 0
            scanNo = 0
            blPos = 0
            if verbose:
                if fakeChunk:
                    print 'Creating UV_DATA table for synthetic band ', band, sideBand, ' with ', (1+newChunks[band][2]-newChunks[band][1])/newChunks[band][3], ' channels'
                else:
                    print 'Creating UV_DATA table for band ', band, sideBand, ' with ', spSmallDict[band][0], ' channels'
            uList        = []
            vList        = []
            wList        = []
            jDList       = []
            timeList     = []
            baselineList = []
            arrayList    = []
            sourceList   = []
            freqList     = []
            intList      = []
            matrixList   = []
            blCount = 0
            nChannels = spSmallDict[band][0]
            if band == 0:
                firstGoodChannel = 0
                lastGoodChannel = 1000000
            else:
                firstGoodChannel = int(float(nChannels)*edgeTrimFraction)
                lastGoodChannel  = int(float(nChannels)*(1.0-edgeTrimFraction) + 0.5)
            if not useMakevis:
                visFileLen = len(visMap)
            while (scanOffset < visFileLen) and (scanNo < maxScan):
                foundBlEntry = False
                foundSpEntry = False
                nBlFound = 0
                if useMakevis:
                    scanNo = makevis.scanno(scanOffset, newFormat);
                    recSize = makevis.recsize(scanOffset, newFormat)
                else:
                    scanNo  = makeInt(visMap[scanOffset:scanOffset+4],   4)
                    if newFormat:
                        recSize = makeInt(visMap[scanOffset+4:scanOffset+8], 4)
                    else:
                        recSize = makeInt(visMap[scanOffset+8:scanOffset+12], 4)
                if scanNo > 0:
                    for bl in blKeysSorted[blPos:]:
                        blCount += 1;
                        if (targetRx < 0) or (blDict[bl][5] == targetRx) or fixRx:
                            rightRx = True
                        else:
                            rightRx = False
                        if (blDict[bl][0] == scanNo) and rightRx:
                            foundBlEntry = True
                            nBlFound += 1
                            if (band, bl) in spBigDict:
                                foundSpEntry = True
                                matrixEntry  = []
                                if rightRx:
                                    uList.append(blDict[bl][6]*1000.0/pseudoContinuumFrequency[sb])
                                    vList.append(blDict[bl][7]*1000.0/pseudoContinuumFrequency[sb])
                                    wList.append(blDict[bl][8]*1000.0/pseudoContinuumFrequency[sb])
                                    jDList.append(jD)
                                    timeList.append(inDict[scanNo][7]/24.0)
                                    baselineList.append(256*blDict[bl][15] + blDict[bl][16])
                                    arrayList.append(1)
                                    if (inDict[scanNo][14] in validSourceNumbers) and (inDict[scanNo][25] > 0.0):
                                        thisSource = inDict[scanNo][14]
                                        intX = round(inDict[scanNo][17])
                                        intY = round(inDict[scanNo][18])
                                        fKey = (thisSource, intX, intY)
                                        sourceList.append(fieldMapping[fKey])
                                    elif inDict[scanNo][25] <= 0.0:
                                        thisSource = inDict[scanNo][14]
                                        intX = round(inDict[scanNo][17])
                                        intY = round(inDict[scanNo][18])
                                        fKey = (thisSource, intX, intY)
                                        try:
                                            sourceList.append(fieldMapping[fKey])                                        
                                        except KeyError:
                                            sourceList.append(validSourceNumbers[0])
                                    else:
                                        sourceList.append(validSourceNumbers[0])
                                    freqList.append(1)
                                    intList.append(inDict[scanNo][12])
                                if newFormat:
                                    dataoff = scanOffset+spBigDict[(band, bl)][0] + 8
                                else:
                                    dataoff = scanOffset+spBigDict[(band, bl)][0] + 16
                                if useMakevis:
                                    scaleExp = makevis.scaleexp(dataoff, newFormat)
                                else:
                                    if newFormat:
                                        scaleExp = makeInt(visMap[dataoff:dataoff+2], 2)
                                    else:
                                        scaleExp = makeInt(visMap[dataoff+8:dataoff+10], 2)
                                    if scaleExp > (2**15-1):
                                        scaleExp -= 2**16
                                scale = (2.0**scaleExp) * sqrt(2.0*pi)*130.0*2.0
                                if bl == 0:
                                    ant1Tsys = sqrt(abs(blTsysDict[bl][0]*blTsysDict[bl][1]))
                                    ant2Tsys = sqrt(abs(blTsysDict[bl][2]*blTsysDict[bl][3]))
                                if 24 < bl < 49:
                                    ant1Tsys = blTsysDict[bl][1]
                                    ant2Tsys = blTsysDict[bl][3]
                                else:
                                    ant1Tsys = blTsysDict[bl][0]
                                    ant2Tsys = blTsysDict[bl][2]
                                scale *= sqrt(abs(ant1Tsys*ant2Tsys))
                                if newFormat:
                                    weight = spBigDict[(band, bl)][1]/(maxWeight*ant1Tsys*ant2Tsys)
                                else:
                                    weight = spBigDict[(band, bl)][1]
                                if useMakevis:
                                    if fakeChunk:
                                        matrixEntry = makevis.convert(nChannels, spSmallDict[band][4], scale, dataoff, newFormat, weight, False, firstGoodChannel, lastGoodChannel, reverseChannelOrder, newChunks[band][3], newChunks[band][1]/newChunks[band][3], newChunks[band][2]/newChunks[band][3])
                                    else:
                                        matrixEntry = makevis.convert(nChannels, nChannels, scale, dataoff, newFormat, weight, trimEdges, firstGoodChannel, lastGoodChannel, reverseChannelOrder, 1, 0, nChannels-1)
                                    if rightRx:
                                        matrixList.append(matrixEntry)
                                else:
                                    if fakeChunk:
                                        print 'Making synthetic chunks without makevis is not yet supported - aborting'
                                        sys.exit(-1)
                                    if newFormat:
                                        dataoff += 2
                                    else:
                                        dataoff += 10
                                    for i in range(0, nChannels):
                                        if newFormat:
                                            real = ord(visMap[dataoff  ])+(ord(visMap[dataoff+1])<<8)
                                        else:
                                            real = ord(visMap[dataoff+1])+(ord(visMap[dataoff  ])<<8)
                                        if real > (2**15-1):
                                            real -= 2**16
                                        if newFormat:
                                            imag = ord(visMap[dataoff+2])+(ord(visMap[dataoff+3])<<8)
                                        else:
                                            imag = ord(visMap[dataoff+3])+(ord(visMap[dataoff+2])<<8)
                                        if imag > (2**15-1):
                                            imag -= 2**16
                                        if (real == 0) and (imag == 0):
                                            totalZeros += 1
                                            print 'Band ', band, ' sideband ', sideBand, ' channel ', i, ' has 0 amplitude.'
                                        if (weight <= 0.0) or (trimEdges and (not (firstGoodChannel <= i <= lastGoodChannel))):
                                            matrixEntry.append(0.0)
                                            matrixEntry.append(0.0)
                                        else:
                                            matrixEntry.append(float(real)*scale)
                                            matrixEntry.append(float(-imag)*scale)
                                        matrixEntry.append(weight)
                                        totalPoints += 1
                                        dataoff += 4
                                    if reverseChannelOrder and (band != 0):
                                        # This is a chunk with an odd number of LSB downconversions, so channels must
                                        # be reordered, because the FITS-IDI standard demands positive increments in
                                        # frequency between channels.
                                        swappedEntry = []
                                        nSets = len(matrixEntry)/3
                                        for i in range(nSets):
                                            swappedEntry.append(matrixEntry[3*nSets - (3 + i*3)])
                                            swappedEntry.append(matrixEntry[3*nSets - (2 + i*3)])
                                            swappedEntry.append(matrixEntry[3*nSets - (1 + i*3)])
                                        if rightRx:
                                            matrixList.append(swappedEntry)
                                    else:
                                        if rightRx:
                                            matrixList.append(matrixEntry)
                                if nBlFound == numberOfBaselines:
                                    break
                        blPos += 1
                    if (not foundBlEntry) or (not foundSpEntry):
                        print 'Something not found scanNo = %d, band = %d, foundBl = %d, foundSp = %d' % (scanNo, band, foundBlEntry, foundSpEntry)
                        print '\n\nThis can occur if a single receiver track has somes scans which are marked as'
                        print 'belonging to a receiver that was not in use.    If this was a single receiver'
                        print 'track, try running the script again with the -R option.'
                        sys.exit(-1)
                if newFormat:
                    scanOffset += recSize+8
                else:
                    scanOffset += recSize+16
            c10Format = '%dE' % (len(matrixEntry))
            del matrixEntry
            c1  = fits.Column(name='UU',          format='1D',       array=uList       , unit='SECONDS')
            c2  = fits.Column(name='VV',          format='1D',       array=vList       , unit='SECONDS')
            c3  = fits.Column(name='WW',          format='1D',       array=wList       , unit='SECONDS')
            c4  = fits.Column(name='DATE',        format='1D',       array=jDList      , unit='DAYS'   )
            c5  = fits.Column(name='TIME',        format='1D',       array=timeList    , unit='DAYS'   )
            c6  = fits.Column(name='BASELINE',    format='1J',       array=baselineList                )
            c7  = fits.Column(name='SOURCE_ID',   format='1J',       array=sourceList                  )
            c8  = fits.Column(name='FREQID',      format='1J',       array=freqList                    )
            c9  = fits.Column(name='INTTIM',      format='1E',       array=intList     , unit='SECONDS')
            c10 = fits.Column(name='FLUX',        format=c10Format,  array=matrixList  , unit='UNCALIB')
            coldefs = fits.ColDefs([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10])
            uvDataHDU = fits.BinTableHDU.from_columns(coldefs)
            header = uvDataHDU.header
            header['extname']  = 'UV_DATA'
            header['nmatrix']  = (1,                          'Number of matrices'                   )
            header['tmatx10']  = ('T'                                                                )
            header['maxis']    = (6,                          'Number of matix axes'                 )
            header['maxis1']   = (3,                          'Number of data points on complex axis')
            header['ctype1']   = ('COMPLEX',                  'Type of axis 1'                       )
            header['cdelt1']   = 1.0
            header['crval1']   = 1.0
            header['crpix1']   = 1.0
            header['maxis2']   = (1,                          'Number of data points on Stokes axis' )
            header['ctype2']   = ('STOKES',                   'Type of axis 2'                       )
            header['cdelt2']   = 0.0
            header['crval2']   = -2.0
            header['crpix2']   = 1.0
            header['maxis3']   = (spSmallDict[band][0],       'Number of data points on Freq axis'   )
            header['ctype3']   = ('FREQ',                     'Type of axis 3'                       )
            header['cdelt3']   = (abs(spSmallDict[band][1]),  'Channel spacing in Hz'                )
            header['crval3']   = (lowestFSky,                 'Frequency of reference pixel'         )
            header['crpix3']   = 1.0
            header['maxis4']   = (1,                          'Number of data points on Band axis  ' )
            header['ctype4']   = ('BAND',                     'Type of axis 4'                       )
            header['cdelt4']   = 1.0
            header['crval4']   = 1.0
            header['crpix4']   = 1.0
            header['maxis5']   = (1,                          'Number of data points on RA axis'     )
            header['ctype5']   = ('RA',                       'Type of axis 5'                       )
            header['cdelt5']   = 1.0
            header['crval5']   = (0.0,                        'Must be 0 for a multisource file'     )
            header['crpix5']   = 1.0
            header['maxis6']   = (1,                          'Number of data points on Dec axis'    )
            header['ctype6']   = ('DEC',                      'Type of axis 6'                       )
            header['cdelt6']   = 1.0
            header['crval6']   = (0.0,                        'Must be 0 for a multisource file'     )
            header['crpix6']   = 1.0
            
            header['tabrev']   = 2
            header['obscode']  = ' '
            header['no_stkd']  = (1,                         'Number of Stokes parameters'           )
            header['stk_1']    = (-2,                        'First Stokes parameter'                )
            header['no_band']  = (1,                         'Number of bands'                       )
            header['no_chan']  = (spSmallDict[band][0],      'The number of spectral channels'       )
            header['ref_freq'] = (lowestFSky,                'File reference frequency'              )
            header['chan_bw']  = (abs(spSmallDict[band][1]), 'The channel bandwidth'                 )
            header['ref_pixl'] = 1
            
#            header['weightyp'] = ('NORMAL',                  'Normal 1/(uncertainty**2) weights'     )
            header['telescop'] = ('SMA',                     'Submillimeter Array, Hawaii'           )
            header['observer'] = projectPI
            del header

            ###
            ### Create the file and write all tables
            ###
            fileName = 'tempFITS-IDI%s.band%d' % (sideBand, band)
            if verbose:
                print 'Writing primary header for file ', fileName
            hdulist.writeto(fileName)
            if verbose:
                print 'Writing ARRAY_GEOMETRY table'
            fits.append(fileName, arrayGeometryHDU.data, header=arrayGeometryHDU.header)
            del arrayGeometryHDU
            if verbose:
                print 'Writing SOURCE table'
            fits.append(fileName, sourceHDU.data,        header=sourceHDU.header       )
            del sourceHDU
            if verbose:
                print 'Writing FREQUENCY table'
            fits.append(fileName, frequencyHDU.data,     header=frequencyHDU.header    )
            del frequencyHDU
            if verbose:
                print 'Writing ANTENNA table'
            fits.append(fileName, antennaHDU.data,       header=antennaHDU.header      )
            del antennaHDU
            if verbose:
                print 'Writing SYSTEM_TEMPERATURE table'
            fits.append(fileName, tsysHDU.data,          header=tsysHDU.header         )
            del tsysHDU
            if verbose:
                print 'Writing UV_DATA table'
            fits.append(fileName, uvDataHDU.data,        header=uvDataHDU.header       )
            del uvDataHDU
            hdulist.close()
            del hdulist
            del hdu
