from multiprocessing.shared_memory import SharedMemory

from ctypes import sizeof, memmove, addressof


class SharedMemReader:
    def __init__(self, shared_mem_class, shared_mem_name):
        self._shared_mem_object = shared_mem_class()
        self._shared_mem_name = shared_mem_name

    def read_shared_mem(self):
        try:
            mem1 = SharedMemory(name=self._shared_mem_name, create=False)

            buffer = mem1.buf
            memmove(addressof(self._shared_mem_object), buffer.tobytes(), sizeof(self._shared_mem_object))

            # for name, typez in self.sharedMemObj._fields_:
            #     print(name + ": " + str(getattr(self.sharedMemObj, name)))

            mem1.close()
        except FileNotFoundError:
            return False

        return True

    def get_mem_attr(self, attribute_name):
        return getattr(self._shared_mem_object, attribute_name)
