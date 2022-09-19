from src.SharedMemReader import SharedMemReader
from src.RadioClientControl import RadioClientControl, sharedMemName as rccMemName
import time
import threading

radioChannels = {'uhf': 0,
                 'vhf': 1,
                 'guard': 2}

class IVCCapture:
    def __init__(self, bmsState, obsRequest):
        self.bmsState = bmsState
        self.obsRequest = obsRequest
        self.uhfThread = None
        self.vhfThread = None
        self.mutex = threading.Lock()

    def start_capture(self):
        uhfThread = threading.Thread(target=self._ivc_capture, args=['uhf'])
        vhfThread = threading.Thread(target=self._ivc_capture, args=['vhf'])
        uhfThread.start()
        vhfThread.start()

    def stop_capture(self):
        self.bmsState[0] = False
        if self.uhfThread:
            self.uhfThread.join()
        if self.vhfThread:
            self.vhfThread.join()

    def _ivc_capture(self, channel):
        rccMemm = SharedMemReader(RadioClientControl, rccMemName)
        obsPTTIsPressed = False

        print(str(channel) + " ptt capture enabled")

        while True:
            # If we aren't in 3D, stop thread
            if not self.bmsState[0]:
                break

            rccMemm.readSharedMem()
            radioTransmit = getattr(rccMemm.getMemAttr("Radios")[radioChannels.get(channel)], "PttDepressed")

            # only need to unmute once for all the transmitting radios
            self.mutex.acquire()
            try:
                if radioTransmit and not obsPTTIsPressed:
                    print(str(channel) + " transmit")
                    self._record_voice_down()
                    obsPTTIsPressed = True
                elif not radioTransmit and obsPTTIsPressed:
                    print(str(channel) + " transmit stop")
                    self._record_voice_up()
                    obsPTTIsPressed = False
            finally:
                self.mutex.release()

            time.sleep(0.2)

    def _record_voice_down(self):
        self.obsRequest.unmute()

    def _record_voice_up(self):
        self.obsRequest.mute()

