from ctypes import Structure, c_byte, c_int32, c_float, c_bool

sharedMemName = "FalconIntellivibeSharedMemoryArea"


# falcon intellivibe memory structure
class IntelliVibe(Structure):
    _fields_ = [
        ("AAMissileFired", c_byte),
        ("AGMissileFired", c_byte),
        ("BombDropped", c_byte),
        ("FlareDropped", c_byte),
        ("ChaffDropped", c_byte),
        ("BulletsFired", c_byte),
        ("CollisionCounter", c_int32),
        ("IsFiringGun", c_bool),
        ("IsEndFlight", c_bool),
        ("IsEjecting", c_bool),
        ("In3D", c_bool),
        ("IsPaused", c_bool),
        ("IsFrozen", c_bool),
        ("IsOverG", c_bool),
        ("IsOnGround", c_bool),
        ("IsExitGame", c_bool),
        ("Gforce", c_float),
        ("eyex", c_float),
        ("eyey", c_float),
        ("eyez", c_float),
        ("lastdamage", c_int32),
        ("damageforce", c_float),
        ("whendamage", c_int32)
    ]
