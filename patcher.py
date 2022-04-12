import os
import sys
import argparse
from client import RemoteClient
from serverClient import ServerClient
from log import LOGGER



def getSearchString(inp):
    inp = inp.split(".")
    res = inp[0]
    for i in range(1, len(inp)):
        subs = inp[i]
        if("-" not in subs):
            res+="." + subs
        else:
            res+="."+ subs.split("-")[0] + ".*"
    return res

def runCommandsInInventory(containerID):
    LOGGER.info("Enabling debug in inventory service {} using setLoglevel.sh file . . . ".format(containerID))
    exeCmd = "docker exec"
    setLogLevelFilePath = "/opt/CSCOlumos/bin/setLogLevel.sh"
    cmd1 = "{} {} {} XDE DEBUG".format(exeCmd, containerID, setLogLevelFilePath)
    cmd2 = "{} {} {} Hibernate DEBUG".format(exeCmd, containerID, setLogLevelFilePath)
    cmd3 = "{} {} {} persistence DEBUG".format(exeCmd, containerID, setLogLevelFilePath)
    cmd4 = "{} {} {} inventory DEBUG".format(exeCmd, containerID, setLogLevelFilePath)
    sshClient.execute_commands([cmd1, cmd2, cmd3, cmd4])
    LOGGER.info("Successfully Enabled debug in inventory service {} using setLoglevel.sh file ".format(containerID))

def runCommandsInNetwork_Programmer(containerID):
    LOGGER.info("Enabling debug in Network-Programmer service {} using setLoglevel.sh file . . . ".format(containerID))
    exeCmd = "docker exec"
    setLogLevelFilePath = "/opt/CSCOlumos/bin/setLogLevel.sh"
    cmd1 = "{} {} {} networkprogrammer DEBUG".format(exeCmd, containerID, setLogLevelFilePath)
    cmd2 = "{} {} {} config DEBUG".format(exeCmd, containerID, setLogLevelFilePath)
    cmd3 = "{} {} {} XDE DEBUG".format(exeCmd, containerID, setLogLevelFilePath)
    sshClient.execute_commands([cmd1, cmd2, cmd3])
    LOGGER.info("Successfully Enabled debug in Network-Programmer service {} using setLoglevel.sh file ".format(containerID))


def patchLogbackXML(localFilePath, patchPath, fileName, containerName):
    LOGGER.info("Running patch LogbackXML procedure . . . ")
    if(not patchPath):
        patchPath="/opt/CSCOlumos/conf/"
    sshClient.uploadFile([localFilePath])
    containerID = serverClient.getContainerID(containerName)
    renameFile = "logback.xml"
    serverClient.renameFile(fileName, renameFile)
    serverClient.copyFileToContainer(renameFile, containerID, patchPath)
    if("inv" in containerName):
        runCommandsInInventory(containerID)
    elif("network-pr" in containerName):
        runCommandsInNetwork_Programmer(containerID)
    else:
        LOGGER.error("Patching Logback and enabling Debug is only supported for inventory and network-programmer service for now")
        serverClient.abort()
    LOGGER.info("Completed patching LogbackXML file {} to {} container.".format(fileName, containerName))


def patchXDEProcedure(localFilePath, patchPath, fileName, containerName):
    LOGGER.info("Running patch XDE procedure . . . ")
    if(not patchPath):
        patchPath="/opt/CSCOlumos/xmp_inventory/xde-home/packages/standard/"
    sshClient.uploadFile([localFilePath])
    container_id = serverClient.getContainerID(containerName)
    fileSearchString = getSearchString(fileName)
    actualFileNameInContainer = serverClient.getActualFileNameInContainer(container_id, patchPath,fileSearchString)
    serverClient.renameFile(fileName, actualFileNameInContainer)
    serverClient.copyFileToContainer(actualFileNameInContainer, container_id, patchPath)
    LOGGER.info("Completed patching XDE file {} to {} container.".format(fileName, containerName))





if __name__==  "__main__":
    """Initialize remote host client and execute actions."""
    print("\n")

    ##Parser
    parser = argparse.ArgumentParser(description='Patcher requires following params to work as intended. Give details to required params with appropriate flags, and if you are comfortable with default values, then you can ignore optional param flags.')
    parser.add_argument("-fpath", help="local path of the patch file",  default="", required=True, type=os.path.abspath, )
    parser.add_argument("-ip", help="server ip address without http prefix.",  default="", required=True)
    parser.add_argument("-cname", help="container or service name where this file has to be patched ", required=True)
    parser.add_argument("-uname", help="server login username. Default=maglev",  default="maglev", required=False)
    parser.add_argument("-pwd", help="server ssh login password. Default=Maglev123",  default="Maglev123", required=False)
    parser.add_argument("-upath", help="path inside cluster where patch file has to be uploaded. Default=/home/maglev",  default="/home/maglev", required=False)
    parser.add_argument("-p","--port", help="Cluster SSH port. Default=2222",  default=2222, required=False)
    parser.add_argument("-patchPath", help="The Path inside container, where the file should be patched. Script by default uses /opt/CSCOlumos/xmp_inventory/xde-home/packages/standard For XDE, and /opt/CSCOlumos/conf/ For logback file patching",  default=None, required=False)
    parser.add_argument("-ds","--disableSafeMode",action="store_true", help="By default patcher runs in safe mode. This allows you to verify each write command before its executed on the server. You can use this flag to disable safe mode.",  default=False, required=False)
    group = parser.add_mutually_exclusive_group(required=True)
    # group.conflict_handler="Cannot patch both XDE and Logback file simulaneously."
    group.add_argument("-xde", "--xde", action="store_true", help="use this flag to patch an XDE")
    group.add_argument("-log", "--logbackXML", action="store_true", help="use this flag to patch logBackXML file")
    
    ##PARSE
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])

    #Extract
    filePath = args.fpath
    host = args.ip.strip("http").strip("https").strip(":").strip("/").strip("\\")
    user = args.uname
    password = args.pwd
    remote_path = args.upath
    port = args.port
    containerName = args.cname
    patchPath= args.patchPath
    safeMode = not args.disableSafeMode
    patchXDE = args.xde
    patchLOG = args.logbackXML


    # host = "10.104.58.111"
    # user = "maglev"
    # password = "Maglev123"
    # remote_path = "/home/maglev"
    # port = 2222
    # filePath = "C:\Me\TryOuts\Patcher\logback_debug_np_TESTING.xml"
    
    #Normalise and extran relevant info
    if("\\" in filePath):
        fileName = filePath.split("\\").pop()
    else:
        fileName = filePath.split("/").pop()

    LOGGER.info(f"Initiating patcher to patch {fileName} present at {filePath}")
    #INIT SSH CLIENT
    sshClient = RemoteClient(ip=host, user=user,password=password,port=port,remote_path=remote_path, safeMode=safeMode)
    sshClient.connectToRemote()

    #INIT Server CLIENT to perform operations on server
    serverClient = ServerClient(sshClient= sshClient, containerName=containerName, fileName=fileName)
    if("." not in fileName):
        LOGGER.warning("File doesn't seem to have an extension. Please verify and re-run with correct details.")
        serverClient.abort()
    if(patchXDE):
        if("xml" in fileName.split(".").pop().lower()):
            LOGGER.warning(f"Looks like you are using -xde flag, but trying to patch some xml file to {containerName}")
            LOGGER.warning(f"Verify and re-run with correct file name and flags.")
            serverClient.abort()
        patchXDEProcedure(filePath, patchPath, fileName, containerName)
    elif(patchLOG):
        if("xml" not in fileName.split(".").pop().lower()):
            LOGGER.warning(f"Looks like you are using -log flag, but trying to patch some other file to {containerName} instead of a *.xml file")
            LOGGER.warning(f"Verify and re-run with correct file name and flags.")
            serverClient.abort()
        patchLogbackXML(filePath, patchPath, fileName, containerName)
    else:
        LOGGER.error("Please re-run script with either -xde flag to patch XDE file, or -log flag to patch logback xml file.")
        serverClient.abort()
    sshClient.__del__()



