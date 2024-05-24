import matplotlib.pyplot as plt

# Example data
memory_data = [
    (0x1000, 10),
    (0x1010, 30),
    (0x1050, 15),
    (0x1070, 20),
    (0x1080, 4)x
]

# Normalize or scale memory addresses if necessary
base_address = min(addr for addr, size in memory_data)
memory_data = [(addr - base_address, size) for addr, size in memory_data]

# Create figure and axis
fig, ax = plt.subplots()

# Plot each block of memory
for idx, (addr, size) in enumerate(memory_data):
    ax.barh(y=idx, width=size, left=addr, height=0.5, label=f'Addr: {hex(addr + base_address)}, Size: {size}')

ax.set_xlabel('Memory Offset from Base Address')
ax.set_yticks([])
ax.set_title('Memory Allocation Visualization')
plt.legend()
plt.show()
