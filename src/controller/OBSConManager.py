import asyncio
import base64
import hashlib
import uuid

import websockets
import json

from dataclasses import dataclass, field
from inspect import signature
from websockets import exceptions

from src.helper.Exceptions import AuthFailError, MessageTimeout, NotIdentifiedError
from src.helper.IdentificationParameters import IdentificationParameters

RPC_VERSION = 1

# OBS-WEBSOCKET OP CODES
OP_CODE_HELLO = 0
OP_CODE_IDENTIFY = 1
OP_CODE_IDENTIFIED = 2
OP_CODE_REIDENTIFY = 3
OP_CODE_EVENT = 5
OP_CODE_REQUEST = 6
OP_CODE_REQUEST_RESPONSE = 7
OP_CODE_REQUEST_BATCH = 8
OP_CODE_REQUEST_BATCH_RESPONSE = 9


@dataclass
class Request:
    requestType: str
    requestData: dict = None
    inputVariables: dict = None
    outputVariables: dict = None


@dataclass
class RequestStatus:
    result: bool = False
    code: int = 0
    comment: str = None


@dataclass
class RequestResponse:
    requestType: str = ""
    requestStatus: RequestStatus = field(default_factory=RequestStatus)
    responseData: dict = None

    def has_data(self):
        return True if self.responseData else False

    def ok(self):
        return self.requestStatus.result


@dataclass
class _ResponseWaiter:
    event: asyncio.Event = field(default_factory=asyncio.Event)
    response_data: dict = None


async def _wait_for_cond(cond, func):
    async with cond:
        await cond.wait_for(func)


def _build_request_response(response: dict):
    ret_val = RequestResponse(response["requestType"], responseData=response.get("responseData", None))
    ret_val.requestStatus.result = response["requestStatus"]["result"]
    ret_val.requestStatus.code = response["requestStatus"]["code"]
    ret_val.requestStatus.comment = response["requestStatus"].get("comment", None)
    return ret_val


class OBSConManager:
    def __init__(self,
                 port: str = "4444",
                 password: str = '',
                 identification_parameters: IdentificationParameters = IdentificationParameters()):
        self._uri = "ws://localhost:" + port
        self._password = password
        self._identification_parameters = identification_parameters

        self._ws = None
        self._waiters = {}
        self._identified = False
        self._recv_task = None
        self._hello_message = None
        self._event_callbacks = []
        self._cond = asyncio.Condition()
        self._answers = {}

    async def async_connect_and_wait_id(self):
        await self._async_connect()
        identified = await self._wait_until_identified()
        return identified

    async def send_request(self, request: Request, timeout: int = 15):
        ret_val = await self._call(request, timeout)

        if ret_val.ok():
            print(f"Request succeeded! Response data: {ret_val.responseData}")
            return ret_val.responseData
        return None

    async def _async_connect(self):
        if self._ws and self._ws.open:
            print("WebSocket session is already open. Returning")
            return False
        self._answers = {}
        self._recv_task = None
        self._identified = False
        self._hello_message = None
        self._ws = await websockets.connect(self._uri, max_size=2 ** 24)
        self._recv_task = asyncio.create_task(self._ws_recv_task())
        return True

    async def _wait_until_identified(self, timeout: int = 10):
        if not self._ws.open:
            return False
        try:
            await asyncio.wait_for(_wait_for_cond(self._cond, self._is_identified), timeout=timeout)
            print(f"Identification status: {self._identified}")
            return True
        except asyncio.TimeoutError:
            exception_check = self._recv_task.exception()
            if isinstance(exception_check, Exception):
                raise exception_check
            return False

    async def async_disconnect(self):
        if not self._recv_task:
            print("WebSocket session is not open. Returning")
            return False
        self._recv_task.cancel()
        await self._ws.close()
        self._ws = None
        self._answers = {}
        self._identified = False
        self._recv_task = None
        self._hello_message = None
        print("WebSocket session closed")
        return True

    def _is_identified(self):
        return self._identified

    async def _call(self, request: Request, timeout: int = 15):
        if not self._identified:
            raise NotIdentifiedError("Calls to requests cannot be made without being identified with obs-websocket")
        request_id = str(uuid.uuid4())
        request_payload = {
            "op": OP_CODE_REQUEST,
            "d": {
                "requestType": request.requestType,
                "requestId": request_id
            }
        }
        if request.requestData:
            request_payload["d"]["requestData"] = request.requestData

        print(f"Sending request message:\n{json.dumps(request_payload, indent=2)}")
        waiter = _ResponseWaiter()
        try:
            self._waiters[request_id] = waiter
            await self._ws.send(json.dumps(request_payload))
            await asyncio.wait_for(waiter.event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            raise MessageTimeout(f"The request with type {request.requestType} timed out after {timeout} seconds.")
        finally:
            del self._waiters[request_id]

        return _build_request_response(waiter.response_data)

    async def _send_identify(self, password: str = None, identification_parameters: IdentificationParameters = None):
        if not self._hello_message:
            return

        identify_message = {"op": OP_CODE_IDENTIFY, "d": {}}
        identify_message["d"]["rpcVersion"] = RPC_VERSION
        if "authentication" in self._hello_message:
            if not self._password:
                raise AuthFailError("Authentication is required but no password was provided. "
                                    "Perhaps you forgot to set server.password?")
            secret = base64.b64encode(hashlib.sha256((self._password + self._hello_message["authentication"]["salt"])
                                                     .encode("utf-8")).digest())
            authentication_string = base64.b64encode(
                hashlib.sha256(secret + (self._hello_message["authentication"]["challenge"].encode("utf-8"))).digest()
            ).decode("utf-8")
            identify_message["d"]["authentication"] = authentication_string
        if self._identification_parameters.ignoreNonFatalRequestChecks:
            identify_message["d"]["ignoreNonFatalRequestChecks"] = \
                self._identification_parameters.ignoreNonFatalRequestChecks
        if self._identification_parameters.eventSubscriptions:
            identify_message["d"]["eventSubscriptions"] = self._identification_parameters.eventSubscriptions

        print(f"Sending identify message:\n{json.dumps(identify_message, indent=2)}")
        await self._ws.send(json.dumps(identify_message))

    async def _ws_recv_task(self):
        while self._ws and self._ws.open:
            try:
                message = await self._ws.recv()
                if not message:
                    continue
                incoming_payload = json.loads(message)

                print(f"Received message:{incoming_payload}")

                op_code = incoming_payload["op"]
                data_payload = incoming_payload["d"]
                if op_code == OP_CODE_REQUEST_RESPONSE or op_code == OP_CODE_REQUEST_BATCH_RESPONSE:
                    payload_request_id = data_payload["requestId"]
                    if payload_request_id.startswith("emit_"):
                        continue
                    try:
                        waiter = self._waiters[payload_request_id]
                        waiter.response_data = data_payload
                        waiter.event.set()
                    except KeyError:
                        print(f"Discarding request response {payload_request_id} because there is no waiter for it.")
                elif op_code == OP_CODE_EVENT:
                    for callback, trigger in self._event_callbacks:
                        if trigger is None:
                            params = len(signature(callback).parameters)
                            if params == 1:
                                asyncio.create_task(callback(data_payload))
                            elif params == 2:
                                asyncio.create_task(callback(data_payload["eventType"], data_payload.get("eventData")))
                            elif params == 3:
                                asyncio.create_task(callback(data_payload["eventType"], data_payload.get("eventIntent"),
                                                             data_payload.get("eventData")))
                        elif trigger == data_payload["eventType"]:
                            asyncio.create_task(callback(data_payload.get("eventData")))
                elif op_code == OP_CODE_HELLO:
                    self._hello_message = data_payload
                    await self._send_identify()
                elif op_code == OP_CODE_IDENTIFIED:
                    self._identified = True
                    async with self._cond:
                        self._cond.notify_all()
                else:
                    print(f"Unknown OpCode: {op_code}")
            except (websockets.exceptions.ConnectionClosed, websockets.exceptions.ConnectionClosedError,
                    websockets.exceptions.ConnectionClosedOK):
                print(
                    f"The WebSocket connection was closed. Code {self._ws.close_code} |"
                    f" Reason: {self._ws.close_reason}")
                self._identified = False
                if self._ws.close_code == 4009:
                    raise AuthFailError("Unable to authenticate with the provided password")
                break
            except json.JSONDecodeError:
                continue
        self._identified = False
