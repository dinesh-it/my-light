import tinytuya
import time
import os
import json
import sys
from pyowm import OWM
from pyowm.utils import config
import datetime
import argparse
from matplotlib import colors

# DPID map
SWITCH_ON = '20'
COLOR = '21'
BRIGHTNESS = '22'
TEMPERATURE = '23'

gradual_map = {
    'fast': [10, 0.2],
    'medium': [10, 1],
    'slow': [7, 1.5],
    'veryslow': [3, 3],
}

config = {}


def decrease_brightness(brightness, gradual=None):
    if gradual is None:
        d.set_brightness_percentage(brightness)
        return

    [dec, interval] = gradual_map[gradual]
    bt = status['status']['brightness']
    while bt >= 10:
        print(f"Setting Brightness to {bt}%")
        d.set_brightness_percentage(bt, False)
        time.sleep(interval)
        bt -= dec

    d.set_brightness_percentage(int(brightness))
    time.sleep(interval)


def increase_brightness(brightness, gradual=None):
    cbt = status['status']['brightness']
    if cbt == brightness:
        return

    if gradual is None:
        print(f"Setting Brightness to {brightness}%")
        d.set_brightness_percentage(int(brightness))
        return

    [inc, interval] = gradual_map[gradual]
    while cbt < brightness:
        print(f"Setting Brightness to {cbt}%")
        d.set_brightness_percentage(int(cbt), False)
        time.sleep(interval)
        cbt += inc

    d.set_brightness_percentage(brightness)


def sun_set_time_reached():
    if 'owm_api_key' not in config or not config['owm_api_key']:
        print("Please set owm_api_key in the config to use OWM api for sunset time check")
        return True

    if 'location' not in config or not config['location']:
        print("Please set location config to check sunset time")
        return True

    print("Checking OWM for sunset time for the day...")
    owm = OWM(config['owm_api_key'])
    mgr = owm.weather_manager()
    observation = mgr.weather_at_place(config['location'])
    w = observation.weather
    # print(f"Visibility level: {w.visibility()}")
    day_light_remain = w.sunset_time() - time.time()
    print(f"Day light remaining {day_light_remain}")

    if day_light_remain > 900:
        print("Still we have good natural light")
        return False

    return True


def check_config(keys):
    exit = 0
    for k in keys:
        if k not in config or not config[k]:
            print(f"Config {k} is required - please set a value in config file")
            exit = 1

    if exit == 1:
        exit(1)


# Connect to Device using local network
def connect_device():
    check_config(['device_id', 'device_local_ip', 'device_local_key'])
    device = tinytuya.BulbDevice(
        dev_id=config['device_id'],
        address=config['device_local_ip'],  # Or set to 'Auto' to auto-discover IP address
        local_key=config['device_local_key'],
        version=config['device_version'])

    return device


def parse_arguments():
    ap = argparse.ArgumentParser()

    ap.add_argument("-s", "--switch", required=False, help="Turn on/off the light", choices=['on', 'off'])
    ap.add_argument("-f", "--force", required=False, help="Ignore time and weather checks for turning on the light", action='store_true', default=False)
    ap.add_argument("-v", "--verbose", required=False, help="Print verbose logs", action='store_true', default=False)
    ap.add_argument("-g", "--gradual", required=False, help="Update brightness gradually", choices=['fast', 'medium', 'slow', 'veryslow'])
    ap.add_argument("-b", "--brightness", required=False, help="Expected brightness level in percentage, default 50%%", type=int)
    ap.add_argument("-t", "--temperature", required=False, help="Expected temperature level in percent, default 30%%", type=int, default=30)
    ap.add_argument("-c", "--color", required=False, help="Change light color value")
    return vars(ap.parse_args())


def time_to_light_on():
    current_time = datetime.datetime.now().time()
    if current_time.hour < 17:
        print("Current time is still not even 5 pm, so skipping the execution")
        return False

    return True


def load_config():
    global config
    conf_file = None

    if 'MY_LIGHT_CONF' in os.environ:
        conf_file = os.environ['MY_LIGHT_CONF']

    if conf_file is None:
        print("Setting config file to my_conf.json")
        conf_file = 'my_light.json'

    f = open(conf_file)
    config = json.load(f)
    f.close()
    return config


def parse_status(sts):
    s = {}
    if 'dps' in sts:
        s['switch'] = sts['dps'][SWITCH_ON]
        s['color'] = sts['dps'][COLOR]
        s['brightness'] = int(sts['dps'][BRIGHTNESS] / 10)
        s['temperature'] = int(sts['dps'][TEMPERATURE] / 10)

    sts['status'] = s
    return sts


config = load_config()
args = parse_arguments()

if 'default_options' in config:
    for opt in config['default_options']:
        if opt in args and args[opt] is None:
            args[opt] = config['default_options'][opt]

print('Input: %r' % args)

if args['verbose']:
    tinytuya.set_debug(True, 'red')

d = connect_device()
status = d.status()
status = parse_status(status)

if 'Error' in status:
    print("ERROR: %r" % status)
    sys.exit(1)

print('Device status: %r' % status)


if args['color'] is not None and args['color'] != 'white':
    cl = args['color'].lower()
    rgb = colors.hex2color(colors.cnames[cl])
    print(f"Setting color with RGB ({rgb})")
    d.set_colour(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
    d.set_colourtemp(int(args['temperature'] * 10))
else:
    # Set to White - set_white(brightness, colourtemp):
    #    colourtemp: Type A devices range = 0-255 and Type B = 0-1000
    print("Setting color to white with given temperature")
    d.set_white(int(status['status']['brightness'] * 10), int(args['temperature'] * 10))


if args['switch'] == 'on':

    if not args['force']:
        if status['status']['switch']:
            print("Device already turned on!")
            sys.exit(0)
        if not time_to_light_on() or not sun_set_time_reached():
            sys.exit(0)

    print("Sending turn on command!")
    d.turn_on()

    if args['brightness'] is None:
        args['brightness'] = 50

    increase_brightness(args['brightness'], args['gradual'])

elif args['switch'] == 'off':

    if not args['force'] and not status['status']['switch']:
        print("Device already turned off!")
        sys.exit(0)

    decrease_brightness(10, args['gradual'])
    print("Sending turn off command!")
    d.turn_off()

elif args['brightness'] is not None:
    increase_brightness(args['brightness'], args['gradual'])

print("Done!")
