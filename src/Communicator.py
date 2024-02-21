import subprocess as sp 
class Communicator: 
    # Controls Communication with GDB and allows you to do the following: 
    #   1. Start/Terminate/Force Kill a GDB process
    #   2. Send GDB a command (or series of commands) 
    #   3. Read GDB output from stdout 
    GDB_PROCESS_COMMAND = "gdb"

    def __init__ (self, arguments, history=None, proc=None):
        self.arguments = arguments # arguments for GDB 
        self.history = history # history of commands sent to GDB 
        self.proc = proc # holds Popen object for GDB process  
    
    def startGDB(self):
        if self.proc is None:
            self.arguments.insert(0, GDB_PROCESS_COMMAND
            self.proc = sp.Popen(self.arguments,
                                 stdin=sp.PIPE, 
                                 stdout=sp.PIPE,
                                 stderr=sp.PIPE)
        else: 
            print("GDB process already exists, terminate before rerunning")
        
    def terminateProcess (self):
        self.proc.terminate()
        self.proc = None
        self.history = None

    def forceKillProcess (self):
        print("GDBViz: I'm in force kill process")
        if self.proc.poll() is None:
            # if proc is still running then force kill it 
            self.proc.kill()
            self.proc = None
            self.history = None 

    def sendCommand (self, command): 
        print("GDBViz: going to print command")
        self.proc.stdin.write(command.encode('utf-8'))
        self.proc.stdin.flush()

    def readOutput (self): 
        readFile = self.proc.stdout
        output = ""
        while True: 
            readBuffer = readFile.read(1).decode()
            output += readBuffer
            print(output[-6: -1])
            if output[-6: -1] == "(gdb)":
                break
        return output 

    # sends command to process and returns the stdout 
    def communicate (self, command): 
        print("GDBViz: going to communicate")
        self.sendCommand(command)
        return (self.proc.stdout.read(10)).decode()
