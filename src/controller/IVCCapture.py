from src.controller.SharedMemReader import SharedMemReader
from src.data.RadioClientControl import RadioClientControl, sharedMemName as rccMemName
import time
import threading

radioChannels = {'uhf': 0,
                 'vhf': 1,
                 'guard': 2}


class IVCCapture:
    def __init__(self, bms_state, obs_request):
        self.bms_state = bms_state
        self.obs_request = obs_request
        self._uhf_thread = None
        self._vhf_thread = None
        self._mutex = threading.Lock()

    def start_capture(self):
        self._record_voice_up()  # mute mic if it's not already muted

        self._uhf_thread = threading.Thread(target=self._ivc_capture, args=['uhf'])
        self._vhf_thread = threading.Thread(target=self._ivc_capture, args=['vhf'])
        self._uhf_thread.start()
        self._vhf_thread.start()

    def stop_capture(self):
        self.bms_state[0] = False
        if self._uhf_thread:
            self._uhf_thread.join()
        if self._vhf_thread:
            self._vhf_thread.join()

    def _ivc_capture(self, channel):
        rcc_memm = SharedMemReader(RadioClientControl, rccMemName)
        obsPTTIsPressed = False

        print(str(channel) + " ptt capture enabled")

        while True:
            # If we aren't in 3D, stop thread
            if not self.bms_state[0]:
                break

            rcc_memm.read_shared_mem()
            radioTransmit = getattr(rcc_memm.get_mem_attr("Radios")[radioChannels.get(channel)], "PttDepressed")

            # only need to unmute once for all the transmitting radios
            self._mutex.acquire()
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
                self._mutex.release()

            time.sleep(0.15)

    def _record_voice_down(self):
        self.obs_request.unmute()

    def _record_voice_up(self):
        self.obs_request.mute()
