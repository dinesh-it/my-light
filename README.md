# Smart Bulb Control using Python Script

This Python script allows you to control your smart lights using the [TinyTuya Python library](https://pypi.org/project/tinytuya/). With this script, you can easily turn your lights on or off and adjust various settings using multiple options, all from the comfort of your Python environment. The bulb should be on the local network (Your computer and Bulb should be on same network/WiFi). If you have smart bulb that can be controlled via Smart Life app then you can use this script to control the same bulb with some initialization process.

Tested on the below bulbs from India (SmartLife app supports multiple vendors worldwide)

- [Wipro Smart LED Bulbs](https://amzn.to/3rYA7XW)
- [Amazon Basics Smart LED](https://amzn.to/3Oh85OT)

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Device Preparation](#tuya-device-preparation)
- [Usage](#usage)
- [Options](#options)
- [Example Scenarios](#example-scenarios)
- [Contributing](#contributing)
- [License](#license)

## Features

- Turn your lights on or off.
- Adjust brightness levels.
- Change color settings (if supported by your lights).
- Turn on/off light by gradually changing the brightness.
- Change the temperature of the warm white.
- Simple and intuitive command-line interface.
- Automatic light on based on the sunset time (Needs [OWM](https://openweathermap.org/api) api key)
- Use script for multiple automations.

## Requirements

Before using this script, make sure you have the following requirements in place:

- Python 3.6 or higher installed.
- A working internet connection (needed for initialization).
- Smart lights compatible with the Tuya platform.
- Paired/Connected the bulb via Smart Life app
- Have Patience to do the initial device preparation (This is one time process)

## Installation

1. Clone or download this repository to your local machine.
2. Navigate to the directory containing the script files.
3. Install python libraries - `pip install -r requirements.txt`

## Tuya Device Preparation
Controlling and monitoring Tuya devices on your network requires the following:

- Address - Network address (IPv4) of the device e.g. 10.0.1.100
- Device ID - Unique identifier for the Tuya device
- Version - Tuya protocol version used (3.1, 3.2, 3.3, 3.4 or 3.5)
- Local_Key - Security key needed to access the Tuya device. See [TinyTuya Setup Wizard](https://github.com/jasonacox/tinytuya#setup-wizard---getting-local-keys) to get these keys.
Detailed instructions with screenshot is given in my [blogpost](https://dineshdtech.blogspot.com/2023/08/smart-bulb-control-using-python-script.html)

Once you have retrieved all the above keys, open `my_light.conf` file and update respective values.

## Usage

Run the script from the command line by executing the following command:

```bash
python my-light.py [options]
```

Replace `[options]` with the specific control options you want to use (see [Options](#options) section).

## Options

The script supports the following command-line options:

```shell
  -h, --help            show this help message and exit
  -s {on,off}, --switch {on,off}
                        Turn on/off the light
  -f, --force           Ignore time and weather checks for turning on the light
  -v, --verbose         Print verbose logs
  -g {fast,medium,slow,veryslow}, --gradual {fast,medium,slow,veryslow}
                        Update brightness gradually
  -b BRIGHTNESS, --brightness BRIGHTNESS
                        Expected brightness level in percentage, default 50%
  -t TEMPERATURE, --temperature TEMPERATURE
                        Expected temperature level in percent, default 30%
  -c COLOR, --color COLOR
                        Change light color value

```

## Example Scenarios

1. Turn on a specific light with gradually increasing the brightness:
   ```bash
   python my_light.py -s --on -g 'veryslow' -b 50% -t 100
   ```

2. Turn off a specific light with gradually decreasing the brightness:
   ```bash
   python my_light.py -s --off -g 'veryslow'
   ```

3. Change color of light based on a command exist status/test cases result:

Add below code to your bashrc:
   ```bash
export LITDIR="/path/to/project/directory"
export MY_LIGHT_CONF="$LITDIR/my_light.json"

lits() {
	# Yellow color using which and low temprature (warm white)
	python $LITDIR/my_light.py -s on -b 50 -f -t 30
	"$@"
	ext=$?
	if [[ $ext == 0 ]]
	then
		clr='green'
	else
		clr='red'
	fi
	python $LITDIR/my_light.py -s on -c $clr -b 100 -f -t 30
}
```

Now run a command using `lits` function and the light will turn on in warm white and once the script is completed, based on the exit status of the script the light color will change to green (0) or red (non 0)  
```bash
lits pytest
```
Light color will change to green if all your test cases are passed otherwise will glow in red color

## Contributing

Contributions are welcome! If you find any issues or want to enhance the script, feel free to open a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

---

Enjoy controlling your smart lights with ease using the Light Control Script and the TinyTuya Python library! If you have any questions or suggestions, feel free to open an issue.