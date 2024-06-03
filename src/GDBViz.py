from Connection import Connection
import os
import select
import sys

READ_BUFFER_SIZE = 1024
INFO_COMMAND = "info locals"
BACKTRACE = "backtrace"
GENERAL_FILE_NAME = "mem_image.png"
GDB_PHRASE = "(gdb)"
VAR_SPLIT_VAL = " ; "


# var class to define an object to store all information about a var easily 
class Var:
    def __init__(self, name, value=None):
        self.name = name
        self.address = None
        self.type = None # will be held as a string 
        self.value = value


# helper method used to read from gdb pipes
def read_fd (fd):
    try: 
        return os.read(fd, READ_BUFFER_SIZE).decode()
    except BlockingIOError:
        return ""

# takes backtrace result and generates a list of commands which gets info local results from all frames
def generate_backtrace_command(backtrace_result):
    command_list = []
    num_frames = len(backtrace_result.strip().split("\n"))
    for i in range(num_frames):
        command_list.append("frame " + str(i))
        command_list.append(INFO_COMMAND)
    return command_list 

# takes result from info locals from each frame and generates commands to get neccessary information from all variables
def generate_var_info_command(info_local_result): 
    command_list = []
    all_vars = [] # list of all variables from all frames
    for i in range(1, len(info_local_result), 2):
        var_list = info_local_result[i].split(VAR_SPLIT_VAL)
        for var in var_list: 
            var = var.split("=")[0].strip() # turns fileInIn = 1 into fileInIn
        all_vars += var_list

    
    return command_list

def execute_viz(result_data, file_name=None):
    # generates the visualization of memory based on result_data
    # if no file_name specified, use generic name
    print("THIS IS MOGHY PRINITNG ------------>")
    for res in result_data:
        print(res)
    print("<------------- PRINTING OVER")

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

    '''
        Multi-Command Mode, needed to run queries that need multiple gdb commands to get all the data
        - Only commands that end in (gdb) can be included in multi-command queries 
        - a multi-command query is represented as a [] of commands (which serves as an input for gdb)
        - a result of a multi-command query is a [] of strings which repersents the result to the corresponding command, i.e.
          input[0] will have a respond in output[0]
        - during a multi-command query, the user input will be disabled in order to prevent any disturbance and be reenabled afterwards
    
    '''
    mc_mode = False # Multi-command
    backtrace_mode = False
    info_var_mode = False
    mc_input = None
    mc_output = None
    sc_output = "" # Single-command output (used to read the full response for each command inside a multi-command query)
    sc_ready = False

    read_list = [sys.stdin, gdb.stdout_pipe, gdb.stderr_pipe]
    while True: 

        # enabling / disabling user's stdin for mc_mode
        if mc_mode and sys.stdin in read_list:
            read_list.remove(sys.stdin)
        elif not mc_mode and sys.stdin not in read_list: 
            read_list.append(sys.stdin)

        readable, _, _ = select.select(read_list, [], [])

        # Read Order: gdb stderr -> gdb stdout -> user stdin (or mc query commands)

        # gdb STDERR
        if gdb.stderr_pipe in readable:
            stderr_buffer = ""
            stderr_pipe_read = read_fd(gdb.stderr_pipe)
            while len(stderr_pipe_read) != 0: 
                stderr_buffer += stderr_pipe_read
                stderr_pipe_read = read_fd(gdb.stderr_pipe)
            print(stderr_buffer)
                
        # gdb STDOUT
        if gdb.stdout_pipe in readable:
            stdout_buffer = ""
            stdout_pipe_read = read_fd(gdb.stdout_pipe)
            while len(stdout_pipe_read) != 0: 
                if mc_mode: 
                    # keep reading gdb's stdout until you reach a "(gdb)" to confirm the result of each command 
                    sc_output += stdout_pipe_read
                    if GDB_PHRASE in sc_output:
                        sc_ready = True
                else: 
                    stdout_buffer += stdout_pipe_read
                stdout_pipe_read = read_fd(gdb.stdout_pipe)

            if mc_mode and sc_ready: 
                # format sc_output correctly 
                result = sc_output[:sc_output.find(GDB_PHRASE)]
                if mc_input is None and mc_output is None and backtrace_mode:
                    mc_input = generate_backtrace_command(result)
                    mc_output = []
                else:
                    result = result.replace("\n", VAR_SPLIT_VAL)
                    result = result.strip(VAR_SPLIT_VAL)
                    mc_output.append(result)

                # set sc_output for next command in mc query 
                sc_ready = False
                if len(sc_output) > sc_output.find(GDB_PHRASE) + len(GDB_PHRASE):
                    sc_output = sc_output[sc_output.find(GDB_PHRASE) + len(GDB_PHRASE):]
                else: 
                    sc_output = ""

                # if avalaible run next command 
                if len(mc_input) > 0: 
                    gdb.send(mc_input.pop(0) + '\n')
                else: 
                    if backtrace_mode: 
                        mc_input = generate_var_info_command(mc_output)
                        mc_output = []
                        backtrace_mode = False
                        info_var_mode = True

                        gdb.send(mc_input.pop(0) + '\n')
                    elif info_var_mode: 
                        execute_viz(mc_output)
                        mc_mode = False
                        mc_input = None
                        mc_output = None
                        info_var_mode = False

            elif not mc_mode:
                # print output to stdout as regular
                print(stdout_buffer)

        # USER STDIN
        if sys.stdin in readable:
            stdin_read = sys.stdin.readline().strip()
            if stdin_read.lower() == "stop":
                gdb.terminate()
                sys.exit(0)    
            elif len(stdin_read) >= 3 and stdin_read[:3].lower() == "viz": 
                mc_mode = True
                backtrace_mode = True
                gdb.send(BACKTRACE + '\n')
            else: 
                gdb.send(stdin_read + '\n')

