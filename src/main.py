import sys
from configparser import ParsingError

from src.controller.SharedMemReader import SharedMemReader
from src.data.IntelliVibe import IntelliVibe, sharedMemName as intelliVibeMemName
from src.controller.OBSRequest import OBSRequest
from src.helper.ConfigParser import read_config, is_null_or_empty
from src.controller.IVCCapture import IVCCapture

import time


def main():
    bmsState = [False]

    try:
        config = read_config()
    except ParsingError as e:
        print(e)
        time.sleep(5)
        sys.exit()

    obsRequest = OBSRequest(config.get("SCENE", "scene.name", fallback=None),
                            config.get("SCENE", "audio.capture.feed", fallback=None),
                            config.get("CONNECTION", "server.port", fallback=None),
                            config.get("CONNECTION", "server.password", fallback=None))

    ivcCapture = None
    if not is_null_or_empty(config.get("SCENE", "audio.capture.feed", fallback=None)):
        ivcCapture = IVCCapture(bmsState, obsRequest)

    try:
        memm = SharedMemReader(IntelliVibe, intelliVibeMemName)

        obsRequest.connect()

        while True:
            time.sleep(10)
            if not memm.read_shared_mem():
                print("No SharedMem Found")
                continue

            if memm.get_mem_attr("In3D"):
                if not bmsState[0]:
                    print("BMS has entered 3D, starting OBS recording")
                    bmsState[0] = True
                    obsRequest.start_recording()
                    if ivcCapture:
                        ivcCapture.start_capture()

            else:
                if bmsState[0]:
                    print("Exited 3D! Stopping Recording")
                    bmsState[0] = False
                    obsRequest.stop_recording()
                    if ivcCapture:
                        ivcCapture.stop_capture()

    except (KeyboardInterrupt, SystemExit):
        print("exiting")
    except Exception as e:
        print(e)
        try:
            input("press any key to exit...\n")
        except UnicodeDecodeError:
            pass
    finally:
        if bmsState[0]:
            bmsState[0] = False
            if ivcCapture:
                ivcCapture.stop_capture()
            obsRequest.stop_recording()
        if obsRequest:
            obsRequest.close()
        sys.exit(0)
