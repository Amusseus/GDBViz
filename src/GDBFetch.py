def generate_gdb_commands(info_locals_output):
    lines = info_locals_output.splitlines()
    variables = [line.split()[0] for line in lines]

    gdb_commands = "set pagination off\n"
    gdb_commands += "file example\n"
    gdb_commands += "break main\n"
    gdb_commands += "run\n"

    for var in variables:
        gdb_commands += f"print &{var}\n"
        gdb_commands += f"print {var}\n"
        gdb_commands += f"print sizeof({var})\n"

    gdb_commands += "quit\n"

    return gdb_commands

# Example input from `info locals`
info_locals_output = """\
i = 10
j = 20
ptr = 0x7fffffffe5d0
"""

# Generate the gdb commands
gdb_commands = generate_gdb_commands(info_locals_output)

# Write the commands to gdb_commands.txt
with open("gdb_commands.txt", "w") as file:
    file.write(gdb_commands)

print("gdb_commands.txt file has been created.")
