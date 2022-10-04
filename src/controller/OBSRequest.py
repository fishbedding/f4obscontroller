import asyncio
import time

from src.controller.OBSConManager import OBSConManager, Request
from src.helper.Exceptions import NotIdentifiedError, AudioCaptureException
from src.helper.IdentificationParameters import IdentificationParameters


class OBSRequest:
    def __init__(self,
                 scene_name: str,
                 audio_capture_feed: str,
                 port: str = "4444",
                 password: str = '',
                 identification_parameters: IdentificationParameters = IdentificationParameters(),
                 ):
        self._scene_name = scene_name
        self._audio_capture_feed = audio_capture_feed

        self._conn_manager = OBSConManager(port, password, identification_parameters)

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

    def _async_run(self, func):
        task = self._loop.create_task(func)
        return self._loop.run_until_complete(task)

    # connecting to obs-websocket
    def connect(self):
        while True:
            try:
                retval = self._async_run(self._conn_manager.async_connect_and_wait_id())
                print("Connected to OBS")
                break
            except ConnectionRefusedError as e:
                print(f"Connection to OBS refused, error:\n {e}")
                print("Perhaps obs-websocket isn't enabled or running on the wrong port?")
                time.sleep(5)
                continue

    def close(self):
        self._async_run(self._conn_manager.async_disconnect())

    def _send_request(self,
                      request_type: str,
                      request_data: dict = None,
                      input_variables: dict = None,
                      output_variables: dict = None):
        request = Request(request_type, request_data, input_variables, output_variables)
        return self._async_run(self._conn_manager.send_request(request))

    # start recording
    def start_recording(self):
        currentScene = self._send_request("GetCurrentProgramScene")

        print(f"Current programmed scene: {currentScene}")

        if currentScene.get("currentProgramSceneName") != self._scene_name:
            print(f"Swapping to scene \"{self._scene_name}\"")
            self._send_request("SetCurrentProgramScene", {"sceneName": self._scene_name})

        recordingStatus = self._send_request("GetRecordStatus")

        print(f"Current recording status: {recordingStatus}")

        if not recordingStatus.get("outputActive"):
            self._send_request("StartRecord")
            print("Recording started")

    # stop recording
    def stop_recording(self):
        try:
            currentScene = self._send_request("GetCurrentProgramScene")
        except NotIdentifiedError:
            return

        print(f"Current programmed scene: {currentScene}")

        if currentScene.get("currentProgramSceneName") != self._scene_name:
            print(f"Swapping to scene {self._scene_name}")
            self._send_request("SetCurrentProgramScene", {"sceneName": self._scene_name})

        recordingStatus = self._send_request("GetRecordStatus")

        print(f"Current recording status: {recordingStatus}")

        if recordingStatus.get("outputActive"):
            response = self._send_request("StopRecord")
            if response and response.get('outputPath', None):
                print(f"Recording stopped, file saved at {response.get('outputPath')}")

    # unmute & mute
    def unmute(self):
        status = self._send_request("GetInputMute", {"inputName": self._audio_capture_feed})
        if not status:
            raise AudioCaptureException("Unable to start audio capture, check if input source is set correctly")
        if status.get("inputMuted"):
            self._send_request("SetInputMute", {"inputName": self._audio_capture_feed, "inputMuted": False})

    def mute(self):
        status = self._send_request("GetInputMute", {"inputName": self._audio_capture_feed})
        if not status:
            raise AudioCaptureException("Unable to start audio capture, check if input source is set correctly")
        if not status.get("inputMuted"):
            self._send_request("SetInputMute", {"inputName": self._audio_capture_feed, "inputMuted": True})



