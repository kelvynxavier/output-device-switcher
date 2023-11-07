#!/usr/bin/env python3

from subprocess import check_output
from re import findall, DOTALL, MULTILINE

SHOW_NOTIFICATION = False
PLAY_SOUND_ALERT = True

# Index and Sink (current sink device index) for each application from "pacmd list-sink-inputs"
inputs = findall(pattern=r'.*?index: (\d+).*?sink: (\d+)',
                 string=check_output(args=['pacmd', 'list-sink-inputs']).decode(encoding='utf-8'),
                 flags=DOTALL | MULTILINE)
# print('All inputs indexes:', inputs)

# All available sink device indexes
sinks = findall(pattern=r'index: (\d+)',
                string=check_output(['pacmd', 'list-sinks']).decode(encoding='utf-8'))
# print('All sinks indexes:', sinks)

# Current sink device index
current_sink = findall(pattern=r'\*.*?index: (\d+)',
                       string=check_output(args=['pacmd', 'list-sinks']).decode(encoding='utf-8'))[0]
# print('Current sink index:', current_sink)

# Reference index of current sink device index in all available sink device indexes
idx = sinks.index(current_sink)
# Handler for last index
if idx == len(sinks) - 1:
    target_sink = sinks[0]
    check_output(args=['pacmd', 'set-default-sink', target_sink])
else:
    target_sink = sinks[idx + 1]
    check_output(args=['pacmd', 'set-default-sink', target_sink])
# print('Target sink index:', target_sink)
# For each application
for app in inputs:
    # Move sink input to target sink
    check_output(args=['pacmd', 'move-sink-input', app[0], target_sink])

# To notify the output change
if PLAY_SOUND_ALERT:
    check_output(args=['paplay', '/usr/share/sounds/gnome/default/alerts/glass.ogg'])
if SHOW_NOTIFICATION:
    device_names = findall(pattern=r'(device.product.name = ?[^\n]+)',
                           string=check_output(['pacmd', 'list-sinks']).decode('utf-8'))
    device_names = [device_name.replace('device.product.name = ', '').replace('"', '') for device_name in device_names]
    check_output(args=['notify-send', 'Saída de áudio alterada para:',
                       device_names[sinks.index(target_sink)]])
