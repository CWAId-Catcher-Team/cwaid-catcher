# REQUIRES:
#   pycryptdome: python -m pip install pycryptodome
#   protobuf: python -m pip install protobuf
#   tinydb: python -m pip install tinydb
import os
import pickle
from utils.config import ApplicationConfig as config
from utils.keys import KeyScheduler as ks
import utils.parser as parser
from tinydb import TinyDB
from datetime import datetime
import tek_parser

def analyse_part(teks,ids):
    key_scheduler = ks()
   
    c = 0
    # loop over each tek and look for each rpi if it is contained in the catched ids
    for key in teks:
        tek = teks[key]
        for rpi in tek[6]:
            for id_element in ids:            
                if rpi in id_element:
                    # result is a list containing one list for tek - and one for rpi associated data
                    result = []
                    # convert byte objects to hex strings, cause database cant store bytes
                    tek_list = tek[1:6]
                    tek_list.insert(0,tek[0].hex())
                    result.append(tek_list)
                    rpi_list = id_element.get(rpi)     
                    #  key, time count, id set, aem,duplicate_counter           
                    result.append([rpi_list[0].hex(),rpi_list[1],rpi_list[2],rpi_list[3].hex(), rpi_list[4]])
                    # add result to global dictionary 
                    matched_tek_objects[rpi.hex()] = result
                    print("Found positive catched id! Rpi is: " + str(rpi) + ". Found in list of teks from date: " + teks["date"] + ". Tek key data is: " + str(tek[0]) + ". Id element content is: " + str(id_element[rpi]))

    #tmp = 0
    #tmp_s = ""
    #for i in teks_list[0].keys():
    #    tmp += 1
    #    if tmp == 1:
    #        tmp_s = i
    #        break
    # TODO:   
    #print("First element of tek_list key_data: " + str(tmp_s) + " element: " + str(teks_list[0][tmp_s]))
    #tmp = 0
    #tmp_s = ""
    #for i in ids[0].keys():
    #    tmp += 1
    #    if tmp == 1:
    #        tmp_s = i
    #        break
    #print("Date of first list: " + str(ids[0]["date"]) + ". Time of first list: " + str(ids[0]["time"]) + " first element of first ids list: " + str(ids[0][tmp_s]))


    
if __name__ == "__main__":    
        # Parse all catched ids
    ids = parser.parse_ids()

    # Here all found rips will be stored
    matched_tek_objects = dict() 
    # Get teks as list of directories where each element is a directory of the tek list of one day 
    print("Parsing teks...")
    teks_list = []
    for subdir, dirnames, filenames in os.walk(config.TEK_PARSED_DIRECTORY):
        for f in os.listdir(subdir):
            if f == "teks":
                continue
            with open(os.path.join(subdir, f), "rb") as f_tek:
                teks_list.append(pickle.load(f_tek))
    print("Done.")

    s = datetime.now().strftime('%m_%d_%Y_%H%M%S')
    db = TinyDB('./database/db_{}.json'.format(s))

    count_teks = 0
    for teks in teks_list:
        count_teks += len(teks) - 1
    if not count_teks:
        print('No Teks in {}, trying to create tek lookup data now...'.format(config.TEK_PARSED_DIRECTORY))
        tek_parser.parse_tek()

    count_ids = 0
    for id_element in ids:
        count_ids += len(id_element)

    print("Analysing " + str(count_teks) + " downloaded teks and " + str(count_ids) + " catched ids...")

    for teks in teks_list:
        analyse_part(teks,ids)
    
    print("Results:")
    print(matched_tek_objects)
    db.insert(matched_tek_objects)
    
    #for item in db:
    #    print(item)

