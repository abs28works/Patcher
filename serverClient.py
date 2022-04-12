import sys

from paramiko import AutoAddPolicy, RSAKey, SSHClient
from paramiko.auth_handler import AuthenticationException, SSHException
from scp import SCPClient, SCPException

from client import RemoteClient
from log import LOGGER

class ServerClient:
    """Client to interact and execute commands inside container on connected remote server via SSHClient."""

    def __init__(
        self,
        sshClient: RemoteClient,
        containerName: str,
        fileName: str,
    ):
        self.sshClient = sshClient
        self.containerName = containerName
        self.fileName = fileName


    def abort(self, msg="Aborting execution"):
        self.sshClient.disconnect()
        sys.exit(msg)


    def renameFile(self, fromName, toName):
        if(fromName==toName):
            LOGGER.info("File names are already matching.")
            return
        LOGGER.info("Renaming file from {} to {}".format(fromName, toName))
        cmd = "mv {} {}".format(fromName, toName)
        self.sshClient.execute_commands(commands=[cmd])
        LOGGER.info("Renamed file Successfully")
    
    def copyFileToContainer(self, fileName,containerId, patchPath):
        LOGGER.info("copying file {} to container {} at {}".format(fileName, containerId, patchPath))
        cmd = "docker cp {} {}:{}".format(fileName, containerId, patchPath)
        self.sshClient.execute_commands([cmd])
        LOGGER.info("Copied file successfully to {}:{}".format(containerId, patchPath))


    def getContainerID(self, containerName):
        LOGGER.info("Getting container ID of {}".format(containerName))
        cmd = "magctl service get_container_id "+ containerName
        container_id = self.sshClient.execute_commands(commands=[cmd], isReadCmd=True)
        if(len(container_id)>=1):
            container_id = container_id[0].strip('\n').strip('\t')
        if(container_id == "ERROR: No matches found"):
            LOGGER.error("Invalid Container Name: Container doesn't exist with this container name")
            self.abort()
        elif(container_id == "ERROR: Multiple matches found. Specify a more unique string"):
            LOGGER.warning("Multiple matches found with given container name. Specify a more unique string")
            self.abort()
        LOGGER.info("Retrieved container ID of {} : {} ".format(containerName, container_id))
        return container_id

    def getActualFileNameInContainer(self, container_id, patchPath, fileSearchString):
        LOGGER.info("Getting actual file name of {} from container {}".format(self.fileName, container_id))
        cmd="docker exec {} ls -l {} | grep -w {}".format(container_id, patchPath, fileSearchString)
        actualFileNameInContainer = self.sshClient.execute_commands(commands=[cmd], isReadCmd=True)
        # actualFileNameInContainer = ['-rw-r--r-- 1 maglev maglev   12315 May 12 03:01 dot11ax-7.7.385.80302845.xar\n']
        if(not len(actualFileNameInContainer)):
            LOGGER.error("Unable to find any resembling file inside {} container, that can be replaced with your patch file {}".format(self.containerName, self.fileName))
            self.abort()
        actualFileNameInContainer = actualFileNameInContainer[0].split().pop().strip('\n').strip('\t')
        LOGGER.info("Retrieved actual fileName {} from container with ID: {}".format( actualFileNameInContainer, container_id))
        return actualFileNameInContainer
