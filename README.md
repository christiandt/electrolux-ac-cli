# Electrolux Aircon CLI

A command-line interface (CLI) for controlling Electrolux air conditioners via Broadlink devices.

## Features
- Power on/off
- Set temperature
- Change mode (auto, cool, heat, dry, fan, heat_8)
- Adjust fan speed
- Control swing, LED, sleep, self-clean, and timer

## Installation

Install it using pip:

```sh
pip install git+https://github.com/christiandt/electrolux-ac-cli.git@main
```

This will install the `elux` command globally.

## Usage

Run the CLI with:

```sh
elux <command> [options]
```

Responses are printed in JSON format, so they can be easily parsed or piped to other commands.

```shell
elux status | jq
```

### Example Commands

- Get status:
  ```sh
  elux status
  ```
- Set temperature:
  ```sh
  elux temp 24
  ```
- Power on/off:
  ```sh
  elux power on
  elux power off
  ```
- Change mode:
  ```sh
  elux mode cool
  ```
- Set fan speed:
  ```sh
  elux fan high
  ```
- Set swing:
  ```sh
  elux swing on
  ```
- Set timer:
  ```sh
  elux timer True 2 30
  ```

## Configuration

By default, the CLI connects to the device at `10.0.0.248`. To change this, edit the `main()` function in `electrolux/cli.py` and set the correct IP address.

## Requirements
- Python 3.7+
- [broadlink](https://github.com/mjg59/python-broadlink)
- [fire](https://github.com/google/python-fire)

## License
MIT

