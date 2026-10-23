"""Read/configure macOS CoreAudio output without microphone access or packages.

Property selectors and CF ownership follow Apple's installed CoreAudio SDK
AudioHardware.h / AudioHardwareBase.h. No gain or input settings are changed.
"""

import argparse
import ctypes as C
import json
import sys
import time


def fourcc(value):
    return int.from_bytes(value.encode("ascii"), "big")


class Address(C.Structure):
    _fields_ = [("selector", C.c_uint32), ("scope", C.c_uint32), ("element", C.c_uint32)]


class ValueRange(C.Structure):
    _fields_ = [("minimum", C.c_double), ("maximum", C.c_double)]


class CoreAudio:
    def __init__(self):
        if sys.platform != "darwin":
            raise RuntimeError("The Audient output helper requires macOS.")
        self.audio = C.CDLL("/System/Library/Frameworks/CoreAudio.framework/CoreAudio")
        self.cf = C.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
        for name in ("AudioObjectGetPropertyDataSize", "AudioObjectGetPropertyData", "AudioObjectSetPropertyData"):
            getattr(self.audio, name).restype = C.c_int32
        self.audio.AudioObjectGetPropertyDataSize.argtypes = [C.c_uint32, C.POINTER(Address), C.c_uint32, C.c_void_p, C.POINTER(C.c_uint32)]
        self.audio.AudioObjectGetPropertyData.argtypes = [C.c_uint32, C.POINTER(Address), C.c_uint32, C.c_void_p, C.POINTER(C.c_uint32), C.c_void_p]
        self.audio.AudioObjectSetPropertyData.argtypes = [C.c_uint32, C.POINTER(Address), C.c_uint32, C.c_void_p, C.c_uint32, C.c_void_p]
        self.cf.CFStringGetLength.argtypes = [C.c_void_p]
        self.cf.CFStringGetLength.restype = C.c_long
        self.cf.CFStringGetCString.argtypes = [C.c_void_p, C.c_void_p, C.c_long, C.c_uint32]
        self.cf.CFStringGetCString.restype = C.c_bool
        self.cf.CFRelease.argtypes = [C.c_void_p]

    @staticmethod
    def check(status):
        if status:
            raise RuntimeError(f"CoreAudio returned OSStatus {status}.")

    def read(self, device, selector, kind, scope="glob"):
        address = Address(fourcc(selector), fourcc(scope), 0)
        value, size = kind(), C.c_uint32(C.sizeof(kind))
        self.check(self.audio.AudioObjectGetPropertyData(device, C.byref(address), 0, None, C.byref(size), C.byref(value)))
        return value

    def array(self, device, selector, kind):
        address = Address(fourcc(selector), fourcc("glob"), 0)
        size = C.c_uint32()
        self.check(self.audio.AudioObjectGetPropertyDataSize(device, C.byref(address), 0, None, C.byref(size)))
        values = (kind * (size.value // C.sizeof(kind)))()
        self.check(self.audio.AudioObjectGetPropertyData(device, C.byref(address), 0, None, C.byref(size), values))
        return values

    def name(self, device):
        ref = self.read(device, "lnam", C.c_void_p)
        if not ref.value:
            return "Unknown output"
        try:
            buffer = C.create_string_buffer(self.cf.CFStringGetLength(ref) * 4 + 1)
            if not self.cf.CFStringGetCString(ref, buffer, len(buffer), 0x08000100):
                raise RuntimeError("Cannot read the CoreAudio device name.")
            return buffer.value.decode("utf-8")
        finally:
            self.cf.CFRelease(ref)

    def write(self, device, selector, value):
        address = Address(fourcc(selector), fourcc("glob"), 0)
        self.check(self.audio.AudioObjectSetPropertyData(device, C.byref(address), 0, None, C.sizeof(value), C.byref(value)))

    def status(self):
        device = self.read(1, "dOut", C.c_uint32).value
        name = self.name(device)
        rate = self.read(device, "nsrt", C.c_double).value
        return {"name": name, "sample_rate": rate, "ready": "audient" in name.lower() and abs(rate - 96000) < 1}

    def configure(self):
        matches = [device for device in self.array(1, "dev#", C.c_uint32) if "audient" in self.name(device).lower()]
        if len(matches) != 1:
            raise RuntimeError("Connect exactly one Audient interface, then restart the player.")
        device = matches[0]
        rates = self.array(device, "nsr#", ValueRange)
        if not any(value.minimum <= 96000 <= value.maximum for value in rates):
            raise RuntimeError("The Audient does not advertise a 96-kHz sample rate.")
        previous = self.status()
        self.write(device, "nsrt", C.c_double(96000))
        # Switch application playback; keep system alert sounds and input unchanged.
        self.write(1, "dOut", C.c_uint32(device))
        for _ in range(20):
            result = self.status()
            if result["ready"]:
                return {"previous_output": previous, "output": result}
            time.sleep(0.1)
        raise RuntimeError("Audient output/sample-rate change could not be verified.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--configure", action="store_true", help="Select Audient for application playback at 96 kHz; do not play audio.")
    args = parser.parse_args()
    try:
        audio = CoreAudio()
        print(json.dumps(audio.configure() if args.configure else audio.status(), indent=2))
    except (RuntimeError, OSError) as error:
        parser.exit(1, f"{error}\n")
