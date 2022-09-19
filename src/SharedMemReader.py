from multiprocessing.shared_memory import SharedMemory

from ctypes import sizeof, memmove, addressof

class SharedMemReader:
    def __init__(self, sharedMemClass, sharedMemName):
        self.sharedMemObj = sharedMemClass()
        self.sharedMemName = sharedMemName

    def readSharedMem(self):
        try:
            mem1 = SharedMemory(name=self.sharedMemName, create=False)

            buffer = mem1.buf
            memmove(addressof(self.sharedMemObj), buffer.tobytes(), sizeof(self.sharedMemObj))

            # for name, typez in self.sharedMemObj._fields_:
            #     print(name + ": " + str(getattr(self.sharedMemObj, name)))

            mem1.close()
        except FileNotFoundError:
            return False

        return True

    def getMemAttr(self, attributeName):
        return getattr(self.sharedMemObj, attributeName)
