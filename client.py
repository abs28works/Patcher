from logging import Logger
import sys
from typing import List

from paramiko import AutoAddPolicy, SSHClient
from paramiko.auth_handler import AuthenticationException
from scp import SCPClient, SCPException

from log import LOGGER
from datetime import datetime as d

class RemoteClient:
    """Client to interact with a remote host via SSH & SCP."""

    def __init__(
        self,
        ip: str,
        user: str,
        password: str,
        port: int,
        remote_path: str,
        safeMode: bool
    ):
        self.ip = ip
        self.user = user
        self.password = password
        self.remote_path = remote_path
        self.client = None
        self.port = port
        self.safeMode = safeMode
        self.myscp = None
        # self.client = self._connectToRemote()

    def connectToRemote(self):
        try:
            LOGGER.info("Connecting to remote host {} at {} . . . .".format(self.user, self.ip))
            client = SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.connect(
                self.ip,
                username=self.user,
                password=self.password,
                timeout=5000,
                port=self.port
            )
            self.client = client
            LOGGER.info("Connected successfully to remote host {} at {}".format(self.user, self.ip))
            return client
        except AuthenticationException as e:
            LOGGER.error(
                f"Authentication failed: did you remember to create an SSH key? {e} \nDEBUG tip: 1. Create a ssh key, if you haven't yet \n 2. Delete this host ssh key from /users/.ssh/known_hosts file and try again."
            )
            raise e

    def progress(self, filename, size, sent):
        percentage = float(sent)/float(size)*100
        sys.stdout.write("%s's upload progress: %.2f%%   \r" % (filename, percentage ))
        sys.stdout.flush()
        if(percentage==100.0):
            print("%s's progress: %.2f%%   \r" % (filename, percentage ))


    @property
    def scp(self) -> SCPClient:
        conn = self.client
        if(not conn):
            conn = self.connectToRemote()
        self.myscp = SCPClient(conn.get_transport(), progress=self.progress)
        return self.myscp

    def uploadFile(self, files:List):
        allFiles = ", ".join(files)
        try:
            LOGGER.info(f"Uploading file to {self.remote_path} on {self.ip}")
            self.scp.put(files, remote_path=self.remote_path)
            LOGGER.info(
                f"Finished uploading {allFiles} files to {self.remote_path} on {self.ip}"
            )
        except SCPException as e:
            self.disconnect()
            raise e
        except PermissionError as e:
            LOGGER.error("PermissionError Exception, Please ensure you have given correct file path, and it has read access.")
            self.abort()
    
    def disconnect(self):
        """Close SSH & SCP connection."""
        print("\n")
        if self.client:
            self.client.close()
            print("Disconnected SSH client successfully")
            self.client=None
        if self.myscp:
            self.myscp.close()
            self.myscp=None
            print("Disconnected SCP client successfully")

    def abort(self, msg="Aborting execution"):
        self.disconnect()
        sys.exit(msg)

    def execute_commands(self, commands: List[str], isReadCmd=False):
        """
        Execute multiple commands in succession.
        :param commands: List of unix commands as strings.
        :type commands: List[str]
        :param isReadCmd: A bool to confirm if the commands in list are read commands or write commands.
        :type isReadCmd: boolean
        """
        for cmd in commands:
            execute = True
            cmd = cmd.strip("\n").strip("\t")
            if(self.safeMode and not isReadCmd):
                LOGGER.info(f"About to run: {cmd}")
                LOGGER.warning("In Safe Mode, please approve the above command by hitting ENTER or typing 'y', else press any other letter to ABORT")
                inp = input("(y/n)?")
                inp = inp.lower()
                if(inp!="y" and inp!=""):
                    execute = False
            if(execute):
                LOGGER.info(f"Running: {cmd}")
                stdin, stdout, stderr = self.client.exec_command(cmd)
                exitCode = stdout.channel.recv_exit_status()
                if(exitCode==0):
                    response = stdout.readlines()
                else:
                    response = stderr.readlines()
                    
                n = len(response)
                line = response[0] if n==1 else ""
                j = 0 if n>1 else 1
                LOGGER.info("OUTPUT: {}".format(line))
                for i in range(j, n):
                    print(response[i])
                if(exitCode!=0):
                    LOGGER.error(f"Command exited with status code {exitCode}")
                    self.abort()
            else:
                self.abort()

        return response

    def __del__(self):
        self.disconnect()
