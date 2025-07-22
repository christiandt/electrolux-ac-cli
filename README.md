# Electrolux Aircon CLI

A command-line interface (CLI) for controlling Electrolux air conditioners via Broadlink devices.

## Features
- Power on/off
- Set temperature
- Change mode (auto, cool, heat, dry, fan, heat_8)
- Adjust fan speed
- Control swing, LED, sleep, self-clean, and timer

## Installation

Clone this repository and install it using pip:

```sh
pip install .
```

This will install the `electrolux` command globally.

## Usage

Run the CLI with:

```sh
electrolux <command> [options]
```

### Example Commands

- Get status:
  ```sh
  electrolux status
  ```
- Set temperature:
  ```sh
  electrolux temp 24
  ```
- Power on/off:
  ```sh
  electrolux power on
  electrolux power off
  ```
- Change mode:
  ```sh
  electrolux mode cool
  ```
- Set fan speed:
  ```sh
  electrolux fan high
  ```
- Set swing:
  ```sh
  electrolux swing on
  ```
- Set timer:
  ```sh
  electrolux timer True 2 30
  ```

## Configuration

By default, the CLI connects to the device at `10.0.0.248`. To change this, edit the `main()` function in `electrolux/cli.py` and set the correct IP address.

## Requirements
- Python 3.7+
- [broadlink](https://github.com/mjg59/python-broadlink)
- [fire](https://github.com/google/python-fire)

## License
MIT

