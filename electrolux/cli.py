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

class Electrolux(Device):
    """
    Represents a controller for Electrolux air conditioners, providing methods to manage power, temperature, mode, fan, and other features.
    """

    TYPE = "ELECTROLUX_OEM"

    def __init__(self, host: t.Tuple[str, int], mac: t.Union[bytes, str], devtype: int, timeout: int = ..., name: str = "", model: str = "", manufacturer: str = "", is_locked: bool = False) -> None:
        super().__init__(host, mac, devtype, timeout, name, model, manufacturer, is_locked)
        self.auth()

    def _send(self, command: int, data: bytes = b"") -> bytes:
        """
        Send a packet to the device and return the response payload.

        Args:
            command (int): The command code to send.
            data (bytes, optional): The payload data to send. Defaults to b"".

        Returns:
            bytes: The response payload from the device.

        Raises:
            broadlink.exceptions.BroadlinkException: If the response checksum is invalid or an error is detected.
        """
        packet = bytearray(0xD)
        packet[0x00:0x02] = command.to_bytes(2, "little")
        packet[0x02:0x06] = bytes.fromhex("a5a55a5a")

        packet[0x08] = 0x01 if len(data) <= 2 else 0x02
        packet[0x09] = 0x0b
        packet[0xA:0xB] = len(data).to_bytes(2, "little")

        packet.extend(data)

        d_checksum = sum(packet[0x08:], 0xC0AD) & 0xFFFF
        packet[0x06:0x08] = d_checksum.to_bytes(2, "little")

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
        """
        Get the current status of the air conditioner as a JSON string.

        Returns:
            str: The status response from the device.
        """
        resp = self._send(0x0e, bytearray('{}', "ascii"))
        return str(resp, "ascii")

    def temp(self, temp: int) -> str:
        """
        Set the target temperature of the air conditioner.

        Args:
            temp (int): The desired temperature to set.

        Returns:
            str: The response from the device after setting the temperature.
        """
        max_temp = 30
        min_temp = 16
        temp = max(min_temp, min(temp, max_temp))
        resp = self._send(0x17, bytearray('{"temp":%s}' % temp, "ascii"))
        return str(resp, "ascii")

    def power(self, power: str) -> str:
        """
        Turn the air conditioner on or off.

        Args:
            power (str): "on" to turn on, "off" to turn off.

        Returns:
            str: The response from the device after setting the power state.
        """
        power_states = {"on": 1, "off": 0}
        resp = self._send(0x18, bytearray('{"ac_pwr":%s}'%(power_states.get(power)), "ascii"))
        return str(resp, "ascii")

    def mode(self, mode: str) -> str:
        """
        Set the operating mode of the air conditioner.

        Args:
            mode (str): The desired mode ("auto", "cool", "heat", "dry", "fan", "heat_8").

        Returns:
            str: The response from the device after setting the mode.
        """
        modes = {"auto": 4, "cool": 0, "heat": 1, "dry": 2, "fan": 3, "heat_8": 6}
        resp = self._send(0x19, bytearray('{"ac_mode":%s}'%(modes.get(mode)), "ascii"))
        return str(resp, "ascii")

    def fan(self, fan_level: str) -> str:
        """
        Set the fan speed of the air conditioner.

        Args:
            fan_level (str): The desired fan level ("auto", "low", "mid", "high", "turbo", "quiet").

        Returns:
            str: The response from the device after setting the fan speed.
        """
        fan_levels = {"auto": 0, "low": 1, "mid": 2, "high": 3, "turbo": 4, "quiet": 5}
        resp = self._send(0x19, bytearray('{"ac_mark":%s}'%(fan_levels.get(fan_level)), "ascii"))
        return str(resp, "ascii")

    def swing(self, swing_state: str) -> str:
        """
        Set the vertical swing state of the air conditioner.

        Args:
            swing_state (str): "on" to enable swing, "off" to disable.

        Returns:
            str: The response from the device after setting the swing state.
        """
        swing_states = {"on": 1, "off": 0}
        resp = self._send(0x19, bytearray('{"ac_vdir":%s}'%(swing_states.get(swing_state)), "ascii"))
        return str(resp, "ascii")

    def led(self, led_state: str) -> str:
        """
        Set the LED display state of the air conditioner.

        Args:
            led_state (str): "on" to turn on the display, "off" to turn off.

        Returns:
            str: The response from the device after setting the LED state.
        """
        led_states = {"on": 1, "off": 0}
        resp = self._send(0x19, bytearray('{"scrdisp":%s}'%(led_states.get(led_state)), "ascii"))
        return str(resp, "ascii")

    def sleep(self, sleep_state: str) -> str:
        """
        Set the sleep mode state of the air conditioner.

        Args:
            sleep_state (str): "on" to enable sleep mode, "off" to disable.

        Returns:
            str: The response from the device after setting the sleep mode.
        """
        sleep_states = {"on": 1, "off": 0}
        resp = self._send(0x18, bytearray('{"ac_slp":%s}'%(sleep_states.get(sleep_state)), "ascii"))
        return str(resp, "ascii")

    def selfclean(self, clean_state: str) -> str:
        """
        Set the self-cleaning mode of the air conditioner.

        Args:
            clean_state (str): "on" to enable self-cleaning, "off" to disable.

        Returns:
            str: The response from the device after setting the self-cleaning mode.
        """
        clean_states = {"on": 1, "off": 0}
        resp = self._send(0x18, bytearray('{"mldprf":%s}'%(clean_states.get(clean_state)), "ascii"))
        return str(resp, "ascii")

    def timer(self, on_timer: bool, hours: int, minutes: int) -> str:
        """
        Set a timer on the air conditioner.

        Args:
            on_timer (bool): True to set an ON timer, False for OFF timer.
            hours (int): Number of hours for the timer (0-23).
            minutes (int): Number of minutes for the timer (0-59).

        Returns:
            str: The response from the device after setting the timer.
        """
        hours = max(0, min(hours, 23))
        minutes = max(0, min(minutes, 59))
        resp = self._send(0x1f, bytearray('{"timer":"%02d%02d|0%s"}'%(hours,minutes,1 if on_timer else 0), "ascii"))
        return str(resp, "ascii")

    def clear_timer(self, on_timer: bool) -> str:
        """
        Clear the ON or OFF timer on the air conditioner.

        Args:
            on_timer (bool): True to clear the ON timer, False for OFF timer.

        Returns:
            str: The response from the device after clearing the timer.
        """
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
    ip_address = config.get('ip_address', '10.0.0.100')
    try:
        device = hello(ip_address=ip_address)
        fire.Fire(
            Electrolux(
                host=device.host,
                mac=device.mac,
                devtype=device.devtype,
                timeout=device.timeout,
                name=device.name,
                model="",
                manufacturer="Electrolux",
                is_locked=device.is_locked
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
