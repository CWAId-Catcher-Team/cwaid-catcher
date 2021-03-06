# REQUIRES:
#   pycryptdome: python -m pip install pycryptodome
#   protobuf: python -m pip install protobuf
#   tinydb: python -m pip install tinydb
import os
import pickle
import time

import tek_parser

from utils.config import ApplicationConfig as config
from utils.keys import KeyScheduler as ks
import utils.parser as parser

from tinydb import TinyDB
from datetime import datetime

def analyse_part(teks,ids):
    key_scheduler = ks()
   
    c = 0
    # loop over each tek and look for each rpi if it is contained in the catched ids
    for key in teks:
        tek = teks[key]
        for rpi in tek[6]:
            for id_element in ids:            
                if rpi in id_element:
                    # Decrypt AEM
                    v_major,v_minor, pl = key_scheduler.decrypt_associated_metadata(tek[0], rpi, id_element[rpi][3])
                    aem = str(v_major) + "." + str(v_minor) + ";" + str(pl)

                    # Result is a list containing one list for tek - and one for rpi associated data
                    result = []
                    # Convert byte objects to hex strings, cause database cant store bytes
                    tek_list = tek[1:6]
                    tek_list.insert(0,tek[0].hex())
                    result.append(tek_list)
                    rpi_list = id_element.get(rpi)     
                    # Key, time count, id set, decrypted aem,duplicate_counter           
                    result.append([rpi_list[0].hex(), rpi_list[1], rpi_list[2], aem, rpi_list[4]])
                    # Add result to global dictionary 
                    matched_tek_objects[rpi.hex()] = result

                    # Print result of id
                    print("Found positive catched id!")
                    print("TEK: " + str(tek[0]))
                    print("RPI: " + str(rpi))
                    print("TEK date: " + teks["date"])
                    print("ID file: " + str(id_element[rpi][2]))
                    print("AEM: " + aem)
                    print()
   
if __name__ == "__main__":    
    start = time.time()
    count_teks = 0
    count_ids = 0
    
    # Initializing tek_parser to parse all teks not parsed yet 
    tek_parser.parse_tek()

    # Parse all catched ids
    ids = parser.parse_ids()
    
    for id_element in ids:
        count_ids += len(id_element)
    
    print("Analysing " + str(count_ids) + " catched ids...")
    print()

    # Here all found rpis will be stored
    matched_tek_objects = dict() 

    # Analyse teks of each day for a positive rpi 
    for subdir, dirnames, filenames in os.walk(config.TEK_PARSED_DIRECTORY):
        for f in os.listdir(subdir):
            if f == "teks":
                continue
            with open(os.path.join(subdir, f), "rb") as f_tek:
                teks = pickle.load(f_tek)
            count_teks += len(teks) - 1
            analyse_part(teks, ids)
    print("Done.")

    if not count_teks:
        print('No Teks in {}, trying to create tek lookup data now...'.format(config.TEK_PARSED_DIRECTORY))
        print('Done. Please restart.')
        exit(0)

    print("Storing results into database...")

    s = datetime.now().strftime('%m_%d_%Y_%H%M%S')
    db = TinyDB('./database/db_{}.json'.format(s)) 
    db.insert(matched_tek_objects)

    print("Done.")
    print()
   
    duration = int(time.time() - start)
    print("Needed " + str(duration) + " seconds.")

    
    #for item in db:
    #    print(item)

