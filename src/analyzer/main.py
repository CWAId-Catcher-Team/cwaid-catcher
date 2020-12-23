# REQUIRES pycryptdome: python -m pip install pycryptodome
# TODO: get List of downloaded TEKs and ENInterval Numbers. Parse them to bytes. Use keys.py to derive RPI key for each <TEK, ENIntervalNumber> tuple.

from utils.keys import KeyScheduler as ks
import parser


tek_list = parser.parse_tek()

print("First element of tek_list key_data: " + str(tek_list[0][0]))

ids = parser.parse_ids()

print("First Element of first ids list: " + str(ids[0][0]) + " Second element of first ids list: " + str(ids[0][1]))


#TODO: read line from parser. Loop through rolling_period and call tek_to_rpi on each TEK & intervall number where interval number = starting interal number + current loop index.
key_scheduler = ks()
rpi = key_scheduler.tek_to_rpi(bytes.fromhex("008edc9ec9d97f30dd06b3a58dcd969c"),2657808)
print(rpi.hex())

