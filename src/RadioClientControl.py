from ctypes import Structure, c_byte, c_int32, c_float, c_bool, c_uint32

sharedMemName = "FalconRccSharedMemoryArea"


class RadioChannel(Structure):
    _fields_ = [
        ("Frequency", c_int32),
        ("RxVolume", c_int32),
        ("PttDepressed", c_bool),
        ("IsOn", c_bool),
        ("padding1", c_byte),
        ("padding2", c_byte)
    ]


class RadioDevice(Structure):
    _fields_ = [
        ("IcVolume", c_int32)
    ]


class Telemetry(Structure):
    _fields_ = [
        ("Agl", c_float),
        ("Range", c_float),
        ("Flags", c_uint32),
        ("LogbookName", c_byte * 21),
        ("padding1", c_byte),
        ("padding2", c_byte),
        ("padding3", c_byte)
    ]


class RadioClientControl(Structure):
    _fields_ = [
        ("PortNumber", c_int32),
        ("Address", c_byte * 64),
        ("Password", c_byte * 64),
        ("Nickname", c_byte * 64),
        ("Radios", RadioChannel * 3),
        ("SignalConnect", c_bool),
        ("TerminateClient", c_bool),
        ("FlightMode", c_bool),
        ("UseAGC", c_bool),
        ("Devices", RadioDevice * 1),
        ("PlayerCount", c_int32),
        ("PlayerMap", Telemetry * 96)
    ]
