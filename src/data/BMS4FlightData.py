from ctypes import Structure, c_byte, c_int32, c_float, c_bool

# falcon flight data structure
# TODO incomplete
class BMS4FlightData(Structure):
    _pack_ = 1
    _fields_ = [
        ("x", c_float),
        ("y", c_float),
        ("z", c_float),
        ("xDot", c_float),
        ("yDot", c_float),
        ("zDot", c_float),
        ("alpha", c_float),
        ("beta", c_float),
        ("gamma", c_float),
        ("pitch", c_float),
        ("roll", c_float),
        ("yaw", c_float),
        ("mach", c_float),
        ("kias", c_float),
        ("vt", c_float),
        ("gs", c_float),
        ("windOffset", c_float),
        ("nozzlePos", c_float)
    ]