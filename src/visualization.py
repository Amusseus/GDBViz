import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
import matplotlib.cm as cm
import numpy as np

# Example memory regions for testing with 10 variables
memory_data = [
    (0x1000, 10, 'stack', 'var1'),
    (0x1010, 15, 'heap', 'var2'),
    (0x1020, 10, 'stack', 'var3'),
    (0x1030, 15, 'heap', 'var4'),
    (0x1040, 10, 'stack', 'var5'),
    (0x1050, 15, 'heap', 'var6'),
    (0x1060, 10, 'stack', 'var7'),
    (0x1070, 15, 'heap', 'var8'),
    (0x1080, 10, 'stack', 'var9'),
    (0x1090, 15, 'heap', 'var10')
]

# Example pointer data for 10 variables
pointer_data = [
    (0x1000, 0x1010),
    (0x1020, 0x1030),
    (0x1040, 0x1050),
    (0x1060, 0x1070),
    (0x1080, 0x1090),
    (0x1010, 0x1020),
    (0x1030, 0x1040),
    (0x1050, 0x1060),
    (0x1070, 0x1080),
    (0x1090, 0x1000)
]

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
for addr, size, region, var_name in memory_data:
    if region == 'stack':
        rect = patches.Rectangle((1, y_position_stack), 1, fixed_chunk_size, edgecolor='black', facecolor=color_map.get(addr, 'skyblue'))
        ax.add_patch(rect)
        add_text_with_outline(1.5, y_position_stack + fixed_chunk_size / 2, f'{var_name}\n(0x{addr:X})', ax, fontsize=6)
        stack_positions[addr] = y_position_stack
        y_position_stack += fixed_chunk_size

# Plot the heap
y_position_heap = 0
heap_positions = {}
for addr, size, region, var_name in memory_data:
    if region == 'heap':
        rect = patches.Rectangle((4, y_position_heap), 1, fixed_chunk_size, edgecolor='black', facecolor=color_map.get(addr, 'lightgreen'))
        ax.add_patch(rect)
        add_text_with_outline(4.5, y_position_heap + fixed_chunk_size / 2, f'{var_name}\n(0x{addr:X})', ax, fontsize=6)
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
