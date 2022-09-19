import time

from src.SharedMemReader import SharedMemReader
from src.IntelliVibe import IntelliVibe, sharedMemName as intelliVibeMemName
from src.OBSRequest import OBSRequest
from src.ConfigParser import readConfig
from src.IVCCapture import IVCCapture

# import keyboard

import time

def main():
    bmsState = [False]
    config = readConfig()
    obsRequest = OBSRequest(config['DEFAULT'].get('server.port'))
    ivcCapture = IVCCapture(bmsState, obsRequest)

    try:
        memm = SharedMemReader(IntelliVibe, intelliVibeMemName)

        obsRequest.connect()

        while True:
            time.sleep(10)
            if not memm.readSharedMem():
                print("No SharedMem Found")
                continue

            if memm.getMemAttr("In3D"):
                if not bmsState[0]:
                    print("BMS has entered 3D, starting OBS recording")
                    bmsState[0] = True
                    time.sleep(3)
                    obsRequest.start_recording()
                    ivcCapture.start_capture()

            else:
                if bmsState[0]:
                    print("Exited 3D! Stopping Recording")
                    bmsState[0] = False
                    obsRequest.stop_recording()
                    ivcCapture.stop_capture()
    except (KeyboardInterrupt, SystemExit):
        bmsState[0] = False
        ivcCapture.stop_capture()
        obsRequest.stop_recording()

    obsRequest.close()

