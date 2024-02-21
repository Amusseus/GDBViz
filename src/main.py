from Communicator import Communicator
if __name__ == "__main__": 
    commandList = ["gdb", "testC"]
    comm = Communicator(commandList)
    comm.startProcess()
    print(comm.readOutput())
    comm.terminateProcess()
    print("this script is done testing")
   
