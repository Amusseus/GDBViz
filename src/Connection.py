import fcntl 
from os import O_NONBLOCK
import subprocess as sp 

class Connection: 
    '''
        Controls the connection between GDBViz and GDB and provides support for the following:
            1. Starting / creating a GDB subprocess
            2. Terminating the GDB subprocess 
            3. Send command to GDB 
    '''

    SUBPROCESS_PROGRAM = "gdb"
    HISTORY_BUFFER = 100

    def __init__ (self, arguments, history=[], proc=None, std_out=None, std_in=None, std_err=None):
        self.arguments = arguments # arguments for gdb (does not include gdb itself)
        self.history = history # [] of requests sent to GDB 
        self.proc = proc # Popen Object for GDB subprocess 

        # all necessary file descriptors for GDB suprocess 
        self.stdout_pipe = std_out
        self.stdin_pipe = std_in
        self.stderr_pipe = std_err
    
    def initialize (self):
        self.proc = sp.Popen([self.SUBPROCESS_PROGRAM] + self.arguments, 
                             stdin=sp.PIPE, 
                             stdout=sp.PIPE,
                             stderr=sp.PIPE)
        
        self.stdout_pipe = self.proc.stdout.fileno()
        self.stdin_pipe = self.proc.stdin.fileno()
        self.stderr_pipe = self.proc.stderr.fileno()

        # set file descriptor to non blocking mode to make asynchronous reading possible 
        flags = fcntl.fcntl(self.stdout_pipe, fcntl.F_GETFL)
        fcntl.fcntl(self.stdout_pipe, fcntl.F_SETFL, flags | O_NONBLOCK)

        stderr_flags = fcntl.fcntl(self.stderr_pipe, fcntl.F_GETFL)
        fcntl.fcntl(self.stderr_pipe, fcntl.F_SETFL, stderr_flags | O_NONBLOCK)
       
    def terminate (self):
        if self.proc is not None:
            self.proc.terminate()

    def forceKill (self):
        if self.proc is not None and self.proc.poll() is None:
            self.proc.kill()
         
    def send (self, input): 
        self.proc.stdin.write(input.encode())
        self.proc.stdin.flush()
