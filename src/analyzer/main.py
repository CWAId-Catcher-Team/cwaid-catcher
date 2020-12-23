# REQUIRES pycryptdome: python -m pip install pycryptodome
# TODO: get List of downloaded TEKs and ENInterval Numbers. Parse them to bytes. Use keys.py to derive RPI key for each <TEK, ENIntervalNumber> tuple.

from utils.keys import KeyScheduler as ks
import parser
from multiprocessing import Pool
from multiprocessing import cpu_count 


def analyse_part(teks, tid):
    print("Hello from thread " + str(tid) + ". Analysing " + str(len(teks)) + " teks.")
    c = 0
    # loop over each catched tek and calculate for each possible interval number the rpi and search if its is contained in the catched ids
    for key in teks:
        tek = teks[key]
        for i in range(tek[3]):
            rpi = key_scheduler.tek_to_rpi(tek[0], i + tek[2])
            for id_element in ids:
                if rpi in id_element:
                    print("Found positive catched id! Rpi is: " + str(rpi) + " tek key data is: " + str(tek[0]) + " interval number is: " + str(i + tek[2]) + " id is: " + str(id_element[rpi]))
        c += 1
        if c % 5000 == 0:
            print(str(c) + "/" + str(len(teks)) + " teks done in thread " + str(tid))


# get all teks downloaded from cwa server
teks_list = parser.parse_tek(cpu_count())

tmp = 0
tmp_s = ""
for i in teks_list[0].keys():
    tmp += 1
    if tmp == 1:
        tmp_s = i
        break
    
print("First element of tek_list key_data: " + str(tmp_s) + " element: " + str(teks_list[0][tmp_s]))

# parse all catched ids
ids = parser.parse_ids()

tmp = 0
tmp_s = ""
for i in ids[0].keys():
    tmp += 1
    if tmp == 1:
        tmp_s = i
        break
print("Date of first list: " + str(ids[0]["date"]) + ". Time of first list: " + str(ids[0]["time"]) + " first element of first ids list: " + str(ids[0][tmp_s]))


#TODO: read line from parser. Loop through rolling_period and call tek_to_rpi on each TEK & intervall number where interval number = starting interal number + current loop index.
key_scheduler = ks()
rpi = key_scheduler.tek_to_rpi(bytes.fromhex("008edc9ec9d97f30dd06b3a58dcd969c"),2657808)
print(str(rpi.hex()))


print("Analysing catched teks and ids. This can take a while...")

pool = Pool()
pool_list = []

for i in range(len(teks_list)):
    pool_list.append(pool.apply_async(analyse_part, [teks_list[i], i]))

for i in range(len(teks_list)):
    pool_list[i].get()

print("Done")
