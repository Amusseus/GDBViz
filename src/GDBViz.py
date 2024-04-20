from Connection import Connection
import os
import select
import sys

READ_BUFFER_SIZE = 1024

# helper method used to read from gdb pipes
def read_fd (fd):
    try: 
        return os.read(fd, READ_BUFFER_SIZE).decode()
    except BlockingIOError:
        return ""

if __name__ == "__main__": 
    
    # read command line arguments from user 
    if len(sys.argv) < 2:
        print("Incorrect amount of arguments provided\n")
        print("Usage: python3 GDBViz.py programName [optional arguments ...]")
        sys.exit(1)

    argument_finish_index = len(sys.argv)
    if ">" in sys.argv or ">>" in sys.argv: 
        if ">" in sys.argv:
            argument_finish_index = sys.argv.index(">")
        else: 
            argument_finish_index = sys.argv.index(">>")

    gdb_arugments = sys.argv[1:argument_finish_index]
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
            stdin_read = sys.stdin.readline().strip()
            if stdin_read == "stop":
                gdb.terminate()
                sys.exit(0)
            gdb.send(stdin_read + '\n')

