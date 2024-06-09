# GDBViz - Senior Project
**GDBViz** is a python program that serves as a layer between GDB and the user, and aides the user in the debugging process by providing memory visualiztion functionality. This program has the capability to generate a memory image at any point in a given c langauge program, but has only been tested on the htable program (provided with it alongside different input in the testPrg directory).

## Requirements 
- Python3
- Python libraries: matplotlib and numpy
- GDB 

## Installation & Usage

To install GDBViz, follow these steps:

1. Clone the repository:
   git clone https://github.com/yourusername/GDBViz.git

2. Navigate to src directory 
    cd src 

3. Run with terminal command (works with any gdb terminal input)
    General: python3 GDBViz.py [any gdb input]
    Example: python3 GDBViz.py --args testPrg/htable testPrg/smalltest