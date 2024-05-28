from Connection import Connection
import os
import select
import sys

READ_BUFFER_SIZE = 1024
INFO_COMMAND = "info locals"
GENERAL_FILE_NAME = "mem_image.png"
GDB_PHRASE = "(gdb)"

# helper method used to read from gdb pipes
def read_fd (fd):
    try: 
        return os.read(fd, READ_BUFFER_SIZE).decode()
    except BlockingIOError:
        return ""

# helper method generates mutli-command query for viz command based on info locals
def generate_viz_commands(info_local_data): 
    command_list = []
    ''' generate commands here based on info_local_data '''
    command_list.append("print x")
    command_list.append("print x")
    command_list.append("print x")
    command_list.append("info locals")
    command_list.append("info locals")
    command_list.append("info locals")


    return command_list

def execute_viz(result_data, file_name=None):
    # generates the visualization of memory based on result_data
    # if no file_name specified, use generic name
    print("This will be implemeneted")

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

    # needed to run multi command queries 
    multi_command_mode = False
    command_list = None
    result_list = None

    # used to store the result of an individual command in multi-command statement
    # this means that multi-command queries only work with commands that finish in (gdb)
    command_buffer = "" 
    command_ready = False

    while True: 
        # disable user input while running multi-command query
        if multi_command_mode and sys.stdin in read_list: 
            read_list.remove(sys.stdin)
        # re-enable user input when back multi-command query finishes 
        elif not multi_command_mode and sys.stdin not in read_list:
            read_list.append(sys.stdin)

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
                if multi_command_mode:
                    command_buffer += stdout_pipe_read
                    if "(gdb)" in command_buffer:
                        command_ready = True
                else: 
                    stdout_buffer += stdout_pipe_read
                stdout_pipe_read = read_fd(gdb.stdout_pipe)

            if multi_command_mode and command_ready:
                if command_list is None:
                    # genrate a list of commands for multi query
                    command_list = generate_viz_commands(command_buffer)
                    result_list = []

                    # run the first command 
                    command = command_list.pop(0)
                    print("THIS IS COMMAND: " + command)
                    gdb.send(command + '\n')

                    command_ready = False
                    command_ready = ""
                else: 
                    # reformat for easier reading 
                    gdb_phrase_index = command_buffer.find(GDB_PHRASE)
                    result = command_buffer[:gdb_phrase_index].replace("\n", " ; ")
                    result = result.strip(" ; ")
                    result_list.append(result)
            
                    if len(command_list) > 0: 
                        command = command_list.pop(0)
                        print("THIS IS COMMAND: " + command)
                        gdb.send(command + '\n')
                    else: 
                        print("MOGHY TESTING -------------------->")
                        print(result_list)
                        print("<__________________________________")
                        execute_viz(result_list)
                        multi_command_mode = False
                        command_list = None
                        result_list = None

                    command_ready = False
                    command_buffer = command_buffer[:gdb_phrase_index + len(GDB_PHRASE)]
                        
            else:
                print(stdout_buffer)

        if sys.stdin in readable:
            stdin_read = sys.stdin.readline().strip()
            if stdin_read.lower() == "stop":
                gdb.terminate()
                sys.exit(0)    
            elif len(stdin_read) >= 3 and stdin_read[:3].lower() == "viz": 
                # viz [optional file name]
                multi_command_mode = True
                gdb.send("print x" + '\n')
            else: 
                gdb.send(stdin_read + '\n')

