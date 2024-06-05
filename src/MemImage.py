import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
import random
import matplotlib.cm as cm
import numpy as np
import re

#takes in dictionary containg all variable information, proc mappings information (stack and heap), 
# and optional filename for image and generates a memory image 
def generate_mem_image(var_dict, stack_info, heap_info, filename=None):
    print("Implement here")
    stack_start = stack_info[0]
    stack_end = stack_info[1]
    heap_start = heap_info[0]
    heap_end = heap_info[1]

    print(stack_start)
    print(stack_end)
    print(heap_start)
    print(heap_end)
    memory_data = []
    pointer_data = []
    pointer_name = []

    for var in var_dict:
        var_name = var_dict[var].name
        var_address = var_dict[var].address
        var_type = var_dict[var].type
        
        # Extract the hexadecimal address using regular expressions
        match = re.search(r'0x[0-9a-fA-F]+', var_address)
        if match:
            var_address = match.group(0)
        
        # Convert to integer for comparison
        var_address_int = int(var_address, 16)
        var_val = var_dict[var].value
        var_in_data_struct = ""

        if int(stack_start, 16) <= var_address_int <= int(stack_end, 16):
            var_in_data_struct = "stack"
        elif int(heap_start, 16) <= var_address_int <= int(heap_end, 16):
            var_in_data_struct = "heap"
        else:
            var_in_data_struct = ""

        pattern = re.compile(r'\(.+ \*\) (0x[0-9a-f]+)')

        match = pattern.search(var_val)
        if match and len(var_in_data_struct) > 1:
            pointer_data.append((hex(int(var_address[2:], 16) if var_address.startswith("0x") else int(var_address, 16)), hex(int(match.group(1)[2:], 16) if match.group(1).startswith("0x") else int(match.group(1), 16))))
            pointer_name.append(var_name)
        
        memory_data.append((hex(int(var_address, 16) if var_address.startswith('0x') else int(var_address)), var_val, var_in_data_struct, var_name, var_type))

    i = 0
    ('MEMORY DATA')
    for c in memory_data:
        if 'stack' in c or 'heap' in c and "compFile" not in c[3]:
            print(c[3])
            print(c)
            i += 1
    print('POINTER ARRAY')
    for i in range(len(pointer_data)):
        print("Pointer Name", pointer_name[i], "Pointer Data", pointer_data[i])
    print(i)

    # Set a smaller fixed chunk size
    fixed_chunk_size = 2

    # Calculate the total number of chunks needed
    total_chunks = len(memory_data)

    # Dynamically adjust the figure height
    fig_height = total_chunks * (fixed_chunk_size / 2)
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
    for addr, size, region, var_name, var_type in memory_data:
        if region == 'stack':
            rect = patches.Rectangle((1, y_position_stack), 1, fixed_chunk_size, edgecolor='black', facecolor=color_map.get(addr, 'skyblue'))
            ax.add_patch(rect)
            add_text_with_outline(1.5, y_position_stack + fixed_chunk_size / 2, var_name, ax, fontsize=6)
            stack_positions[addr] = y_position_stack
            y_position_stack += fixed_chunk_size

    # Plot the heap
    y_position_heap = 0
    heap_positions = {}
    for addr, size, region, var_name, var_type in memory_data:
        if region == 'heap':
            rect = patches.Rectangle((4, y_position_heap), 1, fixed_chunk_size, edgecolor='black', facecolor=color_map.get(addr, 'lightgreen'))
            ax.add_patch(rect)
            add_text_with_outline(4.5, y_position_heap + fixed_chunk_size / 2, var_name, ax, fontsize=6)
            heap_positions[addr] = y_position_heap
            y_position_heap += fixed_chunk_size

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
    output_file = 'memory_visualization_with_addresses_fixed_chunks.png'
    plt.savefig(output_file, bbox_inches='tight')

    print(f"Memory visualization saved to {output_file}")
