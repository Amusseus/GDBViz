import Connection
import os
import select
import sys

SELECT_TIMEOUT = 0.1 
READ_BUFFER_SIZE = 1024

# helper method used to read from gdb pipes
def read_fd (fd):
    return os.read(fd, READ_BUFFER_SIZE).decode()

if __name__ == "__main__": 
    
    # read command line arguments from user 
    if len(sys.argv) < 3:
        print("Incorrect amount of arguments provided\n")
        print("Usage: python3 GDBViz.py programName [optional arguments ...]")
        sys.exit(1)

    gdb_arugments = sys.argv[2:]
    gdb = Connection(gdb_arugments)
    gdb.initialize()

    read_list = [sys.stdin, gdb.stdout_pipe, gdb.stderr_pipe]
    while True: 
        readable, _, _ = select.select(read_list, [], [])

        '''
            Read Order if multiple fds are avalaible to read: 
                1. gdb stderr
                2. gdb stdout 
                3. GDBViz stdin
        '''

        if gdb.stderr_pipe in readable:
            stderr_buffer = ""
            stderr_pipe_read = read_fd(gdb.stderr_pipe)
            while len(stderr_pipe_read) != 0: 
                stderr_buffer += stderr_pipe_read
                stderr_pipe_read = read_fd(gdb.stderr_pipe)
            print(stderr_buffer)
                
        if gdb.stdout_pipe in readable:
            stdout_buffer = ""
            stdout_pipe_read = read_fd(gdb.stdout_pipe)
            while len(stdout_pipe_read) != 0: 
                stdout_buffer += stdout_pipe_read
                stdout_pipe_read = read_fd(gdb.stdout_pipe)
            print(stdout_buffer)

        if sys.stdin in readable:
            for line in sys.stdin: 
                if line == "stop":
                    gdb.terminate()
                    sys.exit(0)
                gdb.send(line + '\n')

