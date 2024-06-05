from Connection import Connection
from visualization import generate_mem_image
import os
import select
import sys
import re

READ_BUFFER_SIZE = 1024
INFO_COMMAND = "info locals"
INFO_MAPPINGS = "info proc mappings"
BACKTRACE = "backtrace"
GDB_PHRASE = "(gdb)"
STRUCT = "struct"
VAR_SPLIT_VAL = " ; "
NO_ACCESS_PHRASE = "Cannot access memory"

all_vars = {} # global dictionary used to keep track of all var during vix command, key:value -> name: Var object 

# proc mapping information stored as an array in the following format -> index 0: start addr, 1: end addr, 2:size, 3:offset, 4:objfile
stack_info = None
heap_info = None

# var class to define an object to store all information about a var easily 
class Var:
    def __init__(self, name, frame, value=""):
        self.name = name
        self.address = ""
        self.type = "" # will be held as a string 
        self.size = ""
        self.value = value 
        self.frame = frame

def print_var_dict():
    for key in all_vars.keys():
        print("<----------->")
        print("Printing info about var: " + key)
        print("type = " + all_vars[key].type)
        print("size = " + all_vars[key].size)
        print("address = " + all_vars[key].address)
        print("value = " + all_vars[key].value)
        print(">-----------<")

def print_proc_mappings():
    print("<------------->")
    if stack_info is not None:
        print("Printing Stack Information:")
        print("Start Address: " + stack_info[0])
        print("End Address: " + stack_info[1])
        print("Size: " + stack_info[2])
        print("Offset: " + stack_info[3])
    else:
        print("There is no Stack") # This should not be possible 
    print() # print empty line
    if heap_info is not None:
        print("Printing Heap Information:")
        print("Start Address: " + heap_info[0])
        print("End Address: " + heap_info[1])
        print("Size: " + heap_info[2])
        print("Offset: " + heap_info[3])
    else:
        print("There is no Heap") 
    print("<------------->")

    
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
    frame_number = 0
    for i in range(1, len(info_local_result), 2):
        var_list = info_local_result[i].split(VAR_SPLIT_VAL)
        for var in var_list: 
            split = var.split("=")
            name = split[0].strip()
            value = split[1].strip()
            all_vars[name] = Var(name, frame_number, value)
        frame_number += 1
    
    var_query_order = []

    for key in all_vars.keys():
        '''
        Have to switch to the variable frame before querying
        Information to query about var:
            1. ptype
            2. sizeof 
            3. & (address)
        '''
        command_list.append("frame " + str(all_vars[key].frame))  
        command_list.append("ptype " + key)
        command_list.append("print sizeof(" + key + ")")
        command_list.append("print &" + key)
        command_list.append("print " + key)
        var_query_order.append(key)
    
    return command_list, var_query_order

def update_var_dictionary(var_query_order, var_info_result):
    pattern = re.compile(r'\s*([^{};]+?;)\s*') # to remove from struct type = {...}
    var_info_index = 0

    var_order = []
    for var in var_query_order:
        all_vars[var].type = var_info_result[var_info_index + 1].split("=")[1].strip()
        all_vars[var].size = var_info_result[var_info_index + 2].split("=")[1].strip()
        all_vars[var].address = var_info_result[var_info_index + 3].split("=")[1].strip()
        if NO_ACCESS_PHRASE in var_info_result[var_info_index + 4]:
            all_vars[var].value = var_info_result[var_info_index + 4]
        else: 
            all_vars[var].value = var_info_result[var_info_index + 4].split("=")[1].strip()
        #print(all_vars[var].value)
        var_info_index += 5

        # checks if var is a struct and needs further querying     
        if STRUCT in all_vars[var].type and all_vars[var].type[-2:] != "**" and all_vars[var].value[-3:] != "0x0" and NO_ACCESS_PHRASE not in all_vars[var].value:
            matches = pattern.findall(all_vars[var].type)
            members = [match.strip().strip(';') for match in matches]
            for mem in members: 
                # parse the variable declaration to get the varaiable name alone
                attr_name = mem.split()[-1]
                star_index = attr_name.rfind("*")
                bracket_index = attr_name.find("[")
                if star_index != -1: 
                    attr_name = attr_name [star_index + 1:]
                if bracket_index != -1:
                    attr_name = attr_name[:bracket_index]

                new_var_name = var + "." + attr_name
                all_vars[new_var_name] = Var(new_var_name, all_vars[var].frame)
                var_order.append(new_var_name)
              
                
    command_list = []
    # return order is going to be command to run, plus variable command order
    if len(var_order) != 0:
        for var in var_order: 
            command_list.append("frame " + str(all_vars[var].frame))  
            command_list.append("ptype " + var)
            command_list.append("print sizeof(" + var + ")")
            command_list.append("print &" + var)
            command_list.append("print " + var)
        return command_list, var_order
    else:
        return None, None

def interpret_proc_mapping(result):
    global heap_info, stack_info
    pattern = re.compile(r'.*\[stack\].*|.*\[heap\].*')
    matches = pattern.findall(result)
    for match in matches:
        parsed = match.strip()
        parsed_list = parsed.split()
        if "heap" in parsed:
            heap_info = parsed_list
        elif "stack" in parsed:
            stack_info = parsed_list

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
    info_var_query_order = None
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
                if mc_mode: 
                    sc_output += stderr_pipe_read
                else: 
                    stderr_buffer += stderr_pipe_read
                stderr_pipe_read = read_fd(gdb.stderr_pipe)
            if not mc_mode:
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

            if not mc_mode:
            # print output to stdout as regular
                print(stdout_buffer)

        if mc_mode and sc_ready: 
            # format sc_output correctly 
            result = sc_output[:sc_output.find(GDB_PHRASE)]
            if mc_input is None and mc_output is None and backtrace_mode:
                mc_input = generate_backtrace_command(result)
                mc_output = []
            elif backtrace_mode:
                result = result.replace("\n", VAR_SPLIT_VAL)
                result = result.strip(VAR_SPLIT_VAL)
                mc_output.append(result)
            else:
                mc_output.append(result.strip())

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
                    mc_input, info_var_query_order = generate_var_info_command(mc_output)
                    mc_output = []
                    backtrace_mode = False
                    info_var_mode = True
                    gdb.send(mc_input.pop(0) + '\n')

                elif info_var_mode: 
                    mc_input, info_var_query_order = update_var_dictionary(info_var_query_order, mc_output)
                    if mc_input is None and info_var_query_order is None:
                        # finished local variable data collection, now get info about proc mappings for stack and heap
                        info_var_mode = False
                        mc_input = []
                        mc_output = []
                        gdb.send(INFO_MAPPINGS + '\n')
                    else: 
                        gdb.send(mc_input.pop(0) + '\n')
                        mc_output = []
                else: 
                    interpret_proc_mapping(mc_output[0])
                    mc_mode = False
                    mc_input = None
                    mc_output = None
                    print_var_dict()
                    print_proc_mappings()
                    generate_mem_image()

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

