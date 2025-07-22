import os
import sys
import fire
import json
import shutil
import struct
import typing as t

from broadlink import hello
import broadlink.exceptions as e
from broadlink.device import Device
from broadlink.exceptions import DataValidationError, NetworkTimeoutError


MAX_TEMP = 40
MIN_TEMP = 0
DEVICE_TYPE = 0x4f9b

class Electrolux(Device):
    """Controls an electrolux air conditioner.
    """

    TYPE = "ELECTROLUX_OEM"

    def __init__(self, host: t.Tuple[str, int], mac: t.Union[bytes, str], devtype: int, timeout: int = ..., name: str = "", model: str = "", manufacturer: str = "", is_locked: bool = False) -> None:
        super().__init__(host, mac, devtype, timeout, name, model, manufacturer, is_locked)
        self.auth()

    def _send(self, command: int, data: bytes = b"") -> bytes:
        """Send a packet to the device."""
        packet = bytearray(0xD)
        packet[0x00:0x02] = command.to_bytes(2, "little")
        packet[0x02:0x06] = bytes.fromhex("a5a55a5a")

        packet[0x08] = 0x01 if len(data) <= 2 else 0x02
        packet[0x09] = 0x0b
        packet[0xA:0xB] = len(data).to_bytes(2, "little")

        packet.extend(data)

        d_checksum = sum(packet[0x08:], 0xC0AD) & 0xFFFF
        packet[0x06:0x08] = d_checksum.to_bytes(2, "little")

        #print(' '.join(format(x, '02x') for x in packet))

        resp = self.send_packet(0x6A, packet)
        e.check_error(resp[0x22:0x24])
        dcry = self.decrypt(resp[0x38:])

        r_checksum = sum(dcry[0x08:], 0xC0AD) & 0xFFFF
        r_response = struct.unpack("h", dcry[0x06:0x08])[0]

        if r_checksum != r_response:
            raise e.BroadlinkException(DataValidationError, "Failed to validate JSON checksum.")

        r_length = struct.unpack("h", dcry[0xA:0xC])[0]

        payload = dcry[0xE:0xE + r_length]

        return payload

    def status(self) -> str:
        resp = self._send(0x0e, bytearray('{}', "ascii"))
        return str(resp, "ascii")

    def temp(self, temp: int) -> str:
        temp = max(MIN_TEMP, min(temp, MAX_TEMP))
        resp = self._send(0x17, bytearray('{"temp":%s}' % temp, "ascii"))
        return str(resp, "ascii")

    def power(self, power: str) -> str:
        power_states = {"on": 1, "off": 0}
        resp = self._send(0x18, bytearray('{"ac_pwr":%s}'%(power_states.get(power)), "ascii"))
        return str(resp, "ascii")

    def mode(self, mode: str) -> str:
        modes = {"auto": 4, "cool": 0, "heat": 1, "dry": 2, "fan": 3, "heat_8": 6}
        resp = self._send(0x19, bytearray('{"ac_mode":%s}'%(modes.get(mode)), "ascii"))
        return str(resp, "ascii")

    def fan(self, fan_level: str) -> str:
        fan_levels = {"auto": 0, "low": 1, "mid": 2, "high": 3, "turbo": 4, "quiet": 5}
        resp = self._send(0x19, bytearray('{"ac_mark":%s}'%(fan_levels.get(fan_level)), "ascii"))
        return str(resp, "ascii")

    def swing(self, swing_state: str) -> str:
        swing_states = {"on": 1, "off": 0}
        resp = self._send(0x19, bytearray('{"ac_vdir":%s}'%(swing_states.get(swing_state)), "ascii"))
        return str(resp, "ascii")

    def led(self, led_state: str) -> str:
        led_states = {"on": 1, "off": 0}
        resp = self._send(0x19, bytearray('{"scrdisp":%s}'%(led_states.get(led_state)), "ascii"))
        return str(resp, "ascii")

    def sleep(self, sleep_state: str) -> str:
        sleep_states = {"on": 1, "off": 0}
        resp = self._send(0x18, bytearray('{"ac_slp":%s}'%(sleep_states.get(sleep_state)), "ascii"))
        return str(resp, "ascii")

    def selfclean(self, clean_state: str) -> str:
        clean_states = {"on": 1, "off": 0}
        resp = self._send(0x18, bytearray('{"mldprf":%s}'%(clean_states.get(clean_state)), "ascii"))
        return str(resp, "ascii")

    def timer(self, on_timer: bool, hours: int, minutes: int) -> str:

        hours = max(0, min(hours, 23))
        minutes = max(0, min(minutes, 59))

        resp = self._send(0x1f, bytearray('{"timer":"%02d%02d|0%s"}'%(hours,minutes,1 if on_timer else 0), "ascii"))
        return str(resp, "ascii")

    def clear_timer(self, on_timer: bool) -> str:
        resp = self.timer(on_timer, 0, 0)
        return resp

def main():
    home_config_path = os.path.expanduser('~/.electrolux_ac_config.json')
    default_config = {"ip_address": "10.0.0.100"}
    if not os.path.exists(home_config_path):
        # Create a placeholder config in the user's home directory if it doesn't exist
        with open(home_config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        print(f"Created default config file at {home_config_path}. Please edit it with your device's IP address.")
        sys.exit(0)
    with open(home_config_path, 'r') as f:
        config = json.load(f)
    try:
        device = hello(ip_address=config.get('ip_address', '10.0.0.100'))
        fire.Fire(
            Electrolux(
                device.host,
                device.mac,
                device.devtype,
                device.timeout,
                device.name,
                "",
                "Electrolux",
                device.is_locked
            )
        )
    except NetworkTimeoutError:
        print(f"Failed to connect to device at {ip_address}. Please check the IP address and network connection.")
        sys.exit(1)
    except e.BroadlinkException as exc:
        print(f"Error connecting to device: {exc}")
        sys.exit(1)

if __name__ == '__main__':
    main()
