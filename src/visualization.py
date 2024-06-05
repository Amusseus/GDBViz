import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

# takes in dictionary containg all variable information, proc mappings information (stack and heap), 
# and optional filename for image and generates a memory image 
def generate_mem_image(var_dict, stack_info, heap_info, filename=None):
    print("Implement here")





# Example memory data for stack and heap
# Format: (address, size, type) where type is 'stack' or 'heap'
memory_data = [
    (0x1000, 10, 'stack'),
    (0x1010, 30, 'stack'),
    (0x2000, 15, 'heap'),
    (0x2010, 20, 'heap'),
    (0x1020, 4, 'stack'),
    (0x2020, 25, 'heap'),
    (0x1030, 18, 'stack'),
    (0x1040, 12, 'stack'),
    (0x2030, 22, 'heap'),
    (0x2040, 8, 'heap'),
    (0x1050, 16, 'stack'),
    (0x1060, 14, 'stack'),
    (0x2050, 26, 'heap'),
    (0x2060, 17, 'heap'),
    (0x1070, 9, 'stack')
]

# Example pointer data (source address, target address)
pointer_data = [
    (0x1000, 0x2010),  # Pointer from stack to heap
    (0x1010, 0x2000),  # Pointer from stack to heap
    (0x2000, 0x2040),  # Pointer within heap
    (0x2020, 0x2050),
    (0x1030, 0x2060)   # Pointer from stack to heap
]

# Normalize or scale memory addresses if necessary
base_address = min(addr for addr, size, mem_type in memory_data)
memory_data = [(addr - base_address, size, mem_type) for addr, size, mem_type in memory_data]
pointer_data = [(src - base_address, tgt - base_address) for src, tgt in pointer_data]

# Separate stack and heap data
stack_data = [(addr, size) for addr, size, mem_type in memory_data if mem_type == 'stack']
heap_data = [(addr, size) for addr, size, mem_type in memory_data if mem_type == 'heap']

# Create figure and axes
fig, ax = plt.subplots(figsize=(20, 10))

# Define offsets for stack and heap sections
stack_x_offset = 0
heap_x_offset = max(addr + size for addr, size in stack_data) + 20

# Function to plot memory sections
def plot_memory(ax, data, x_offset, color):
    y_position = 0
    positions = []
    for addr, size in data:
        bar = ax.barh(y=y_position, width=size, height=0.5, left=x_offset, align='center', color=color)
        ax.text(x_offset + size / 2, y_position, f'{hex(addr + base_address)}', ha='center', va='center', color='white', fontsize=8, weight='bold')
        positions.append((addr, x_offset, y_position, size, bar))
        y_position -= 1
    return positions

# Plot stack and heap sections
stack_positions = plot_memory(ax, stack_data, stack_x_offset, 'blue')
heap_positions = plot_memory(ax, heap_data, heap_x_offset, 'green')

# Add pointers between sections and within sections
for src, tgt in pointer_data:
    if src in [addr for addr, size in stack_data]:
        src_x_position = next(x_pos for addr, x_pos, y_pos, size, bar in stack_positions if addr == src)
        src_y_position = next(y_pos for addr, x_pos, y_pos, size, bar in stack_positions if addr == src)
        src_size = next(size for addr, size in stack_data if addr == src)
    else:
        src_x_position = next(x_pos for addr, x_pos, y_pos, size, bar in heap_positions if addr == src)
        src_y_position = next(y_pos for addr, x_pos, y_pos, size, bar in heap_positions if addr == src)
        src_size = next(size for addr, size in heap_data if addr == src)
    
    tgt_x_position = next((x_pos for addr, x_pos, y_pos, size, bar in stack_positions if addr == tgt), None)
    if tgt_x_position is None:
        tgt_x_position = next(x_pos for addr, x_pos, y_pos, size, bar in heap_positions if addr == tgt)
        tgt_y_position = next(y_pos for addr, x_pos, y_pos, size, bar in heap_positions if addr == tgt)
    else:
        tgt_y_position = next(y_pos for addr, x_pos, y_pos, size, bar in stack_positions if addr == tgt)

    start = (src_x_position + src_size / 2, src_y_position)
    end = (tgt_x_position, tgt_y_position)

    arrow = FancyArrowPatch(start, end, connectionstyle="arc3,rad=-0.5", arrowstyle="->,head_length=5,head_width=3", color='red', lw=2)
    ax.add_patch(arrow)

# Customize plot
ax.set_xlabel('Memory Offset from Base Address')
ax.set_yticks([])
ax.set_title('Memory Allocation Visualization with Pointers')
ax.legend(handles=[plt.Rectangle((0,0),1,1, color='blue', ec='k', lw=1, label='Stack'),
                   plt.Rectangle((0,0),1,1, color='green', ec='k', lw=1, label='Heap')],
          bbox_to_anchor=(1.05, 1), loc='upper left')

# Adjust axis limits and add padding
max_x_position_stack = sum(size for addr, size in stack_data) + 10
max_x_position_heap = sum(size for addr, size in heap_data) + 10
ax.set_xlim(0, max_x_position_stack + max_x_position_heap + 20)
ax.set_ylim(-len(stack_data) - len(heap_data) - 2, 2)

# Add vertical line to separate stack and heap sections
ax.axvline(x=heap_x_offset - 10, color='black', linestyle='--')

# Save the plot to a file
plt.savefig('memory_allocation_visualization_with_heap_and_stack_axes.png')

# Display the plot
plt.show()
