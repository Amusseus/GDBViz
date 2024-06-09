import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
import random
import matplotlib.cm as cm
import numpy as np
import re

# Takes in dictionary containing all variable information, proc mappings information (stack and heap), 
# and optional filename for image and generates a memory image 
def generate_mem_image(var_dict, stack_info, heap_info, min_chunk_size=5, max_chunk_size=32, filename=None):
    stack_start = stack_info[0]
    stack_end = stack_info[1]
    heap_start = heap_info[0]
    heap_end = heap_info[1]

    memory_data = []
    pointer_data = []
    pointer_name = []

    # Subset of all vars which are not attributes of a struct, if value is None then the var is not a pointer or does not point to a struct,
    # if val is a list then it is a list of all of the struct's attributes that point somewhere   
    non_attr_vars = {} 
    for var in var_dict: 
        dot_index = var.rfind(".")
        if dot_index == -1 or var[-1] == ")": 
            # A non-attribute variable 
            if "struct" in var_dict[var].type:
                non_attr_vars[var] = []
            else: 
                non_attr_vars[var] = None

    # Parse through all the variables in the dictionary 
    for var in var_dict:
        var_name = var_dict[var].name
        var_address = var_dict[var].address
        var_type = var_dict[var].type
        var_val = var_dict[var].value
        var_size = int(var_dict[var].size)  # Assume size is a property in var_dict
        var_in_data_struct = ""

        # Extract the hexadecimal address using regular expressions
        match = re.search(r'0x[0-9a-fA-F]+', var_address)
        if match:
            var_address = match.group(0)
        
        # Convert to integer for comparison
        var_address_int = int(var_address, 16)

        if int(stack_start, 16) <= var_address_int <= int(stack_end, 16):
            var_in_data_struct = "stack"
        elif int(heap_start, 16) <= var_address_int <= int(heap_end, 16):
            var_in_data_struct = "heap"
        else:
            var_in_data_struct = ""

        # Search for pointer
        pattern = re.compile(r'\(.+ \*\) (0x[0-9a-f]+)') # Looks for pointer data in val 
        match = pattern.search(var_val)
        if match and len(var_in_data_struct) > 1: # In stack or heap with a pointer
            name_to_use = var_name
            dot_index = var.rfind(".")
            if dot_index != -1:
                struct_name = var[:var.rfind(")") + 1]
                var_address = var_dict[struct_name].address
                update = re.search(r'0x[0-9a-fA-F]+', var_address)
                if update:
                    var_address = update.group(0)
                name_to_use = struct_name

            tuple_to_add = (hex(int(var_address[2:], 16) if var_address.startswith("0x") else int(var_address, 16)),
                            hex(int(match.group(1)[2:], 16) if match.group(1).startswith("0x") else int(match.group(1), 16)))
            if tuple_to_add in pointer_data: 
                index = pointer_data.index(tuple_to_add)
                pointer_name[index] += ", " + name_to_use
            else:
                pointer_name.append(name_to_use)
                pointer_data.append(tuple_to_add)

        switch = 0

        for c in memory_data:
            if c[0] == (hex(int(var_address, 16))):
                switch = 1
                break

        if switch == 1:
            switch = 0
            continue

        if var in non_attr_vars:
            memory_data.append((hex(int(var_address, 16) if var_address.startswith('0x') else int(var_address)), var_val, var_in_data_struct, var_name, var_type, var_size))

    # Printing for debugging
    # print('MEMORY DATA')
    # for c in memory_data:
    #     if 'stack' in c or 'heap' in c and "compFile" not in c[3]:
    #         print(c[3])
    #         print(c)
    # print('POINTER ARRAY')
    # for i in range(len(pointer_data)):
    #     print("Pointer Name", pointer_name[i], "Pointer Data", pointer_data[i])

    # Find min and max sizes for normalization
    sizes = [data[-1] for data in memory_data]
    min_size = min(sizes)
    max_size = max(sizes)

    # Normalization function to scale sizes between min_chunk_size and max_chunk_size
    def normalize_size(size, min_size, max_size, min_chunk_size, max_chunk_size):
        return min_chunk_size + (max_chunk_size - min_chunk_size) * (size - min_size) / (max_size - min_size)

    # Dynamically adjust the figure height
    fig_height = len(memory_data) * 0.5
    fig, ax = plt.subplots(figsize=(10, fig_height))

    # Function to add text with outline
    def add_text_with_outline(x, y, text, ax, fontsize=6, color='black', outline_color='white', outline_width=1):
        txt = ax.text(x, y, text, ha='center', va='center', fontsize=fontsize, color=color, weight='bold')
        txt.set_path_effects([path_effects.Stroke(linewidth=outline_width, foreground=outline_color), path_effects.Normal()])

    # Function to find all nodes in the same chain
    def find_chain(start_node, pointers):
        chain = set()
        nodes_to_visit = [start_node]
        while nodes_to_visit:
            current_node = nodes_to_visit.pop()
            if current_node not in chain:
                chain.add(current_node)
                nodes_to_visit.extend(tgt for src, tgt in pointers if src == current_node)
        return chain

    # Identify chains
    chains = []
    visited_nodes = set()
    for src, tgt in pointer_data:
        if src not in visited_nodes:
            chain = find_chain(src, pointer_data)
            chains.append(chain)
            visited_nodes.update(chain)

    colors = cm.rainbow(np.linspace(0, 1, len(chains)))
    color_map = {node: colors[i] for i, chain in enumerate(chains) for node in chain}

    # Plot the stack
    y_position_stack = 0
    stack_positions = {}
    for addr, size, region, var_name, var_type, var_size in memory_data:
        if region == 'stack':
            chunk_size = normalize_size(var_size, min_size, max_size, min_chunk_size, max_chunk_size) / 100  # Adjust for plotting scale
            rect = patches.Rectangle((1, y_position_stack), 1, chunk_size, edgecolor='black', facecolor=color_map.get(addr, 'skyblue'))
            ax.add_patch(rect)
            add_text_with_outline(1.5, y_position_stack + chunk_size / 2, f'{var_name}\n{addr}\nSize: {var_size}', ax, fontsize=6)
            stack_positions[addr] = y_position_stack
            y_position_stack += chunk_size

    # Plot the heap
    y_position_heap = 0
    heap_positions = {}
    for addr, size, region, var_name, var_type, var_size in memory_data:
        if region == 'heap':
            chunk_size = normalize_size(var_size, min_size, max_size, min_chunk_size, max_chunk_size) / 100  # Adjust for plotting scale
            rect = patches.Rectangle((4, y_position_heap), 1, chunk_size, edgecolor='black', facecolor=color_map.get(addr, 'lightgreen'))
            ax.add_patch(rect)
            add_text_with_outline(4.5, y_position_heap + chunk_size / 2, f'{var_name}\n{addr}\nSize: {var_size}', ax, fontsize=6)
            heap_positions[addr] = y_position_heap
            y_position_heap += chunk_size

    # Plot the pointers with curved arrows and different colors
    for src, tgt in pointer_data:
        src_x = 2 if src in stack_positions else 5
        tgt_x = 2 if tgt in stack_positions else 5
        src_y = stack_positions.get(src, heap_positions.get(src, 0))
        tgt_y = stack_positions.get(tgt, heap_positions.get(tgt, 0))
        connection_style = "arc3,rad=0.5" if src_y != tgt_y else "arc3,rad=0"
        arrow_color = color_map.get(src, 'red')
        ax.annotate('', xy=(tgt_x, tgt_y), xytext=(src_x, src_y),
                    arrowprops=dict(arrowstyle='->', color=arrow_color, connectionstyle=connection_style))

    # Set the limits and labels
    ax.set_xlim(0, 6)
    ax.set_ylim(0, max(y_position_stack, y_position_heap))
    ax.set_xticks([1.5, 4.5])
    ax.set_xticklabels(['Stack', 'Heap'])
    ax.set_yticks([])

    plt.title('Memory Visualization: Stack and Heap')

    # Save the plot to a file
    output_file = filename if filename else 'Mem_Image_Result.png'
    plt.savefig(output_file, bbox_inches='tight')

    print(f"Memory visualization saved to {output_file}")