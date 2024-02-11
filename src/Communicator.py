import select as s
import subprocess as sp 
class Communicator: 
    # Controls Communication with GDB and allows you to do the following: 
    #   1. Start and run GDB Process
    #   2. interact with GDB, send input and recieve output 
    #   3. terminate GDB 

    def __init__ (self, arguments, history=None, proc=None):
        self.arguments = arguments # arguments to start external program 
        self.history = history # history of commands sent to external program 
        self.proc = proc # holds the Popen object of the process when it starts running 
    
    def startProcess (self):
        print("going into the startProcess method")
        # runs the external program and stores it in proc 
        if self.proc is None or self.proc.poll() is not None:
            self.proc = sp.Popen(self.__arguments, stdin=sp.PIPE, 
                                stdout=sp.PIPE, stderr=sp.PIPE)
        else: 
            print("This process is already running, terminate before starting again")
        
    def terminateProcess (self):
        self.proc.terminate()
        self.proc = None
        self.history = None

    def forceKillProcess (self):
        if self.proc.poll() is None:
            # if proc is still running then force kill it 
            self.proc.kill()
            self.proc = None
            self.history = None 

    # used to send commands where no output is needed
    def sendCommand (self, command): 
        print("going to print command")
        self.proc.stdin.write(command)
        self.proc.stdin.flush()

    # sends command to process and returns the stdout 
    def communicate (self, command): 
        print("going to communicate")
        self.sendCommand(command)
        return self.proc_stdout.read()