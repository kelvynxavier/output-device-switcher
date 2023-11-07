#!/usr/bin/env python3

from subprocess import check_output
from re import findall, DOTALL, MULTILINE

SHOW_NOTIFICATION = True
PLAY_SOUND_ALERT = True
DEVICE = 'alsa_output.usb-MV-SILICON_fifine_SC3_20190808-00'
DEVICE_ALIAS = 'AudioMixer FIFINE SC3'

# Index and Sink (current sink device index) for each application from "pacmd list-sink-inputs"
inputs = findall(pattern=r'.*?index: (\d+).*?sink: (\d+)',
                 string=check_output(args=['pacmd', 'list-sink-inputs']).decode(encoding='utf-8'),
                 flags=DOTALL | MULTILINE)
# print('All inputs indexes:', inputs)

device_names = findall(pattern=r'(name: ?[^\n]+)',
                       string=check_output(['pacmd', 'list-sinks']).decode('utf-8'))
device_names = [device_name.replace('name: <', '').replace('>', '') for device_name in device_names]
# print('Device names:', device_names)
# Handler for analog-stereo or iec958-stereo
for device_name in device_names:
    if DEVICE in device_name:
        DEVICE = device_name

# All available sink device indexes
sinks = findall(pattern=r'index: (\d+)',
                string=check_output(['pacmd', 'list-sinks']).decode(encoding='utf-8'))
# print('All sinks indexes:', sinks)

# Set default sink
check_output(args=['pacmd', 'set-default-sink', DEVICE])

# For each application
for app in inputs:
    # Move sink input to target sink
    check_output(args=['pacmd', 'move-sink-input', app[0], DEVICE])

# To notify the output change
if PLAY_SOUND_ALERT:
    check_output(args=['paplay', '/usr/share/sounds/gnome/default/alerts/glass.ogg'])
if SHOW_NOTIFICATION:
    device_names = findall(pattern=r'(device.product.name = ?[^\n]+)',
                           string=check_output(['pacmd', 'list-sinks']).decode('utf-8'))
    device_names = [device_name.replace('device.product.name = ', '').replace('"', '') for device_name in device_names]
    check_output(args=['notify-send', 'Saída de áudio alterada para:', DEVICE_ALIAS])
