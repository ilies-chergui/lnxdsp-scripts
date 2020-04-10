#########################################################################################
# Copyright (c), 2020 - Analog Devices Inc. All Rights Reserved. 
# This software is PROPRIETARY & CONFIDENTIAL to Analog Devices, Inc.
# and its licensors.
#########################################################################################
# File:
#   <LUK_Utility.py>
# Description:
#   LUK_Utility provide the utility functions,class 
#
#########################################################################################

import os,re,shutil,serial
from io import BytesIO as StringIO
import threading

IMAGE_TYPES = ['adsp-sc5xx-full', 'adsp-sc5xx-minimal', 'adsp-sc5xx-ramdisk'] 
COPY_DST_FOLDER = '/tftpboot'

NFS_TAR_FILE_POSTFIX = '.tar.xz'
NFS_DST_FOLDER= '/romfs'

RAMDISK_FILE_POSTFIX = '.cpio.xz.u-boot'
RAMDISK_FILE_NAME = 'ramdisk.cpio.xz.u-boot'


def copyFiles(bootType, machine, deployFolder, updateUboot = True):

    fileList = []
    os.environ[ 'tftp' ] = COPY_DST_FOLDER

    if updateUboot:
        fileList += ['u-boot', 'u-boot.ldr']

    if bootType.lower() in ("nfsboot", "ramboot") :
        fileList += ['zImage', "%s.dtb" %machine[5:]]
        tarFile = ''
        ramdiskFile = ''
        for (roots, dirs, files ) in os.walk( deployFolder ):
            for f in files:
                for image in IMAGE_TYPES:
                    targetTarFile = "%s-%s%s" %(image, machine, NFS_TAR_FILE_POSTFIX)
                    targetRamdiskFile = "%s-%s%s" %(image, machine,RAMDISK_FILE_POSTFIX)
                    if f == targetTarFile: 
                        tarFile = targetTarFile
                    elif f == targetRamdiskFile: 
                        ramdiskFile = RAMDISK_FILE_NAME
                        shutil.copyfile(os.path.join(deployFolder, targetRamdiskFile), os.path.join(deployFolder, RAMDISK_FILE_NAME))

        if bootType == "nfsboot":
            if tarFile == '':
                raise Exception("Can't find the NFS tar file")
            os.environ[ 'rootfs' ] = NFS_DST_FOLDER
            cmdList = ["sudo rm -rf NFSFOLDER", "sudo mkdir NFSFOLDER", "sudo chmod 777 NFSFOLDER", "tar -xvf %s -C NFSFOLDER" %(os.path.join(deployFolder, tarFile))]
            cmdList = [c.replace('NFSFOLDER', NFS_DST_FOLDER) for c in cmdList]
            for cmd in cmdList: 
                os.system(cmd)

        if bootType == "ramboot":
            if ramdiskFile == '':
                raise Exception("Can't find the ramdisk file")
            fileList.append(ramdiskFile)

    if bootType == "sdcardboot":
            pass # TODO 

    for file in fileList:
        fileDir = os.path.join(deployFolder, file)
        if os.path.isfile(fileDir):
            shutil.copyfile(fileDir, os.path.join(COPY_DST_FOLDER, file))
        else:
            raise Exception("Can't copy due to the %s doesn't exist in %s" %(fileDir, deployFolder) )

def replaceMacros(ipaddr, serverip, cmdList):
    updatedList = []
    if checkValidIp(ipaddr) and checkValidIp(serverip):
        for line in cmdList:
            line = line.replace("SERVERIP", serverip)
            line = line.replace("IPADDR", ipaddr)
            updatedList.append( line )
    else:
        raise Exception("The ipaddress or serverip provided is invalid")
    return updatedList 

def checkValidIp (Ip):
    regex = r'''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'''
    if(re.search(regex, Ip)):  
        return True     
    else:  
        return False

class LogFile:

    def __init__( self, fileName ):
        self.buffer = StringIO()
        self.logFile = open( fileName, 'w' )

    def getText( self ):
        return self.buffer.getvalue()

    def close( self ):
        self.buffer.close()
        self.logFile.close()

    def write( self, s ):
        self.buffer.write( s.encode('utf-8') )
        self.logFile.write( s )

    def flush( self ):
        self.logFile.flush()

