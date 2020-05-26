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

# Utility related parameters when do image copy
IMAGE_TYPES = ['adsp-sc5xx-full', 'adsp-sc5xx-minimal', 'adsp-sc5xx-ramdisk'] 
COPY_DST_FOLDER = '/tftpboot'
NFS_TAR_FILE_POSTFIX = '.tar.xz'
NFS_DST_FOLDER= '/romfs'
NFS_CP_CMD_LIST = ["sudo rm -rf NFSFOLDER", "sudo mkdir NFSFOLDER", "sudo chmod 777 NFSFOLDER", "tar -xvf NFS_SRC_TAR_FILE -C NFSFOLDER" ]
RAMDISK_FILE_POSTFIX = '.cpio.xz.u-boot'
RAMDISK_FILE_NAME = 'ramdisk.cpio.xz.u-boot'
UBOOT_FILE_LIST = ['u-boot', 'u-boot.ldr']
Z_IMAGE = 'zImage'
DTB_POSTFIX = '.dtb'

	
def copyFiles(bootType, machine, deployFolder, updateUboot = True):

    fileList = []
    os.environ[ 'tftp' ] = COPY_DST_FOLDER

    if updateUboot:
        fileList += UBOOT_FILE_LIST

    if bootType.lower() in ("nfsboot", "ramboot") :
        fileList += [ Z_IMAGE, machine[5:] + DTB_POSTFIX ]
        tarFile = ''
        ramdiskFile = ''
        for (roots, dirs, files ) in os.walk( deployFolder ):
            for f in files:
                for image in IMAGE_TYPES:
                    targetTarFile = "%s-%s%s" %(image, machine, NFS_TAR_FILE_POSTFIX)
                    targetRamdiskFile = "%s-%s%s" %(image, machine, RAMDISK_FILE_POSTFIX)
                    if f == targetTarFile: 
                        tarFile = targetTarFile
                    elif f == targetRamdiskFile: 
                        ramdiskFile = RAMDISK_FILE_NAME
                        shutil.copyfile(os.path.join(deployFolder, targetRamdiskFile), os.path.join(deployFolder, RAMDISK_FILE_NAME))

        if bootType == "nfsboot":
            if tarFile == '':
                raise Exception("Can't find the NFS tar file")
            os.environ[ 'rootfs' ] = NFS_DST_FOLDER
            nfsTarFile = os.path.join(deployFolder, tarFile)
            cmdList = replaceMacros([('NFSFOLDER', NFS_DST_FOLDER), ('NFS_SRC_TAR_FILE', nfsTarFile)], NFS_CP_CMD_LIST)
            for cmd in cmdList: 
                os.system(cmd)

        if bootType == "ramboot":
            if ramdiskFile == '':
                raise Exception("Can't find the ramdisk file")
            fileList.append(ramdiskFile)

    if bootType == "sdcardboot":
            pass # TODO, will add more boot type later

    for file in fileList:
        fileDir = os.path.join(deployFolder, file)
        if os.path.isfile(fileDir):
            shutil.copyfile(fileDir, os.path.join(COPY_DST_FOLDER, file))
        else:
            raise Exception("Can't copy due to the %s doesn't exist in %s" %(fileDir, deployFolder) )

def replaceMacros(macros, cmdList):
    # replace the uppercase macros to real data 
    updatedList = []
    for line in cmdList:
        for macro in macros:
            line = line.replace(macro[0], macro[1])
            updatedList.append( line )

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

