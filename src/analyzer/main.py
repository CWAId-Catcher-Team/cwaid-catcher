# REQUIRES:
#   pycryptdome: python -m pip install pycryptodome
#   protobuf: python -m pip install protobuf

from utils.keys import KeyScheduler as ks
import utils.parser as parser
from multiprocessing import Pool
from multiprocessing import cpu_count 

def analyse_part(teks, tid):
    print("Thread" + str(tid) + " Analysing " + str(len(teks)) + " temporary exposure keys.")
    c = 0
    # loop over each catched tek and calculate for each possible interval number the rpi and search if its is contained in the catched ids
    for key in teks:
        tek = teks[key]
        for i in range(tek[3]):
            rpi = key_scheduler.tek_to_rpi(tek[0], i + tek[2])
            for id_element in ids:
                if rpi in id_element:
                    matched_tek_objects.append(tek.append(tid))
                    print("Found positive catched id! Rpi is: " + str(rpi) + " tek key data is: " + str(tek[0]) + " interval number is: " + str(i + tek[2]) + " id is: " + str(id_element[rpi]))
        c += 1
        if c % 5000 == 0:
            print(str(c) + "/" + str(len(teks)) + " teks done in thread " + str(tid))

    #tmp = 0
    #tmp_s = ""
    #for i in teks_list[0].keys():
    #    tmp += 1
    #    if tmp == 1:
    #        tmp_s = i
    #        break
        
    #print("First element of tek_list key_data: " + str(tmp_s) + " element: " + str(teks_list[0][tmp_s]))
    #tmp = 0
    #tmp_s = ""
    #for i in ids[0].keys():
    #    tmp += 1
    #    if tmp == 1:
    #        tmp_s = i
    #        break
    #print("Date of first list: " + str(ids[0]["date"]) + ". Time of first list: " + str(ids[0]["time"]) + " first element of first ids list: " + str(ids[0][tmp_s]))

key_scheduler = ks()
# get all teks downloaded from cwa server
teks_list = parser.parse_tek(cpu_count())

# parse all catched ids
ids = parser.parse_ids()

matched_tek_objects = []
if __name__ == "__main__":
    count_teks = 0

    for teks in teks_list:
        count_teks += len(teks)

    count_ids = 0

    for id_element in ids:
        count_ids += len(id_element)

    print("Analysing " + str(count_teks) + " downloaded teks and " + str(count_ids) + " catched ids. This can take a while...")
    
    pool = Pool()
    pool_list = []  
    for i in range(len(teks_list)):
        pool_list.append(pool.apply_async(analyse_part, [teks_list[i], i]))

    for i in range(len(teks_list)):
        pool_list[i].get()

    print("Done.")
    print(matched_tek_objects)
