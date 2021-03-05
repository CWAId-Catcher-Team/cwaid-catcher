# REQUIRES:
#   pycryptdome: python -m pip install pycryptodome
#   protobuf: python -m pip install protobuf
#   tinydb: python -m pip install tinydb
import os
import pickle
import time

import tek_parser
import stats

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
    parsed_teks = []
    teks_length_dict = dict()

    # Look for already parsed tek files
    for subdir, dirnames, filenames in os.walk(config.TEK_PARSED_DIRECTORY):
        for f in os.listdir(subdir):
            parsed_teks.append(f)

    to_parse = []
    # Find all tek files which are not already parsed 
    for subdir, dirnames, filenames in os.walk(config.TEK_EXPORT_DIRECTORY):
        # Get date of tek directory
        subdirname = subdir.split('/')[-1]
        subdirname = os.path.basename(os.path.normpath(subdirname))
        # If already parsed tek for this date continue
        if subdirname in parsed_teks:
            continue

        # Find tek file and parse
        for f in os.listdir(subdir):
            if f == "tek":
                to_parse.append([subdirname, os.path.join(subdir, f)])

    if len(to_parse) > 0:
        print("Please parse each teks file first by running tek_parser.py or main.py")
        exit(1)

    print("NOT FINISHED. Evaluating... This can take some time (10-15 minutes)...\n")
    
    start = time.time()
    count_teks = 0
    
    # Parse all catched ids
    ids = parser.parse_ids(False)
  
    unique_ids = set()
    android_count = 0
    ios_count = 0
    other_count = 0
    # Iterate over ids of each file 
    for id_element in ids:
        # Check what os each id file has
        for k, id_info in id_element.items():
            unique_ids.add(k)

            id_os = id_info[4]
            if id_os == 1:
                ios_count += 1
            elif id_os == 2:
                android_count += 1
            elif id_os == 3:
                other_count += 1


    # Here all found rpis will be stored
    matched_tek_objects = dict() 

    # Analyse teks of each day for a positive rpi 
    for subdir, dirnames, filenames in os.walk(config.TEK_PARSED_DIRECTORY):
        for f in os.listdir(subdir):
            if f == "teks":
                continue
            with open(os.path.join(subdir, f), "rb") as f_tek:
                teks = pickle.load(f_tek)
            # Length - 1 because one entry is the date and correspond not to a tek
            teks_length_dict[f] = len(teks) - 1
            count_teks += len(teks) - 1
            #analyse_part(teks, ids)

    if not count_teks:
        print('No Teks in {}, trying to create tek lookup data now...'.format(config.TEK_PARSED_DIRECTORY))
        print('Done. Please restart.')
        exit(0)

    s = datetime.now().strftime('%m_%d_%Y_%H%M%S')

    statistics = stats.stats_parser()
    stat_dates = []
    for date in statistics.keys():
        stat_dates.append(date)
    stat_dates.sort()

    tek_dates = []
    for date in teks_length_dict.keys():
        tek_dates.append(date)
    tek_dates.sort()

    # Printing evaluated data
    div = "*" * 50
    
    # Amount of unique ids 
    print(div)
    print("Amount of unique catched RPI's")
    print(div)
    print(str(len(unique_ids)))
    print(div)
    print("\n")

    # TODO Amount of teks each day 
    print(div)
    print("Amount of teks uploaded to CWA server: YYYY-MM-DD;#Teks")
    print(div)
    for date in tek_dates:
        output = date
        output += ";" + str(teks_length_dict[date])
        #print(output)
    print(div)
    print("\n")

    # Statistics of CWA server
    print(div)
    print("Statistics: YYYY-MM-DD;#NewInfections;#CWAWarnings")
    print(div)
    for date in stat_dates:
        stat_dict = statistics[date]
        output = date
        output += ";" + str(int(stat_dict["new_infections"]))
        output += ";" + str(int(stat_dict["new_cwa_warnings"]))
        print(output)
    print(div)
    print("\n")
 
    # OS of ids 
    print(div)
    print("OS detection:")
    print(div)
    all_count = ios_count + android_count + other_count
    print("# All: " + str(all_count) +  "\n")
    print("# iOS: " + str(ios_count))
    print("% iOS: " + str((100 * ios_count) / all_count) + "\n")
    print("# Android: " + str(android_count))
    print("% Android: " + str((100 * android_count) / all_count) + "\n")
    print("# Other: " + str(other_count))
    print("% Other: " + str((100 * other_count) / all_count))
    print(div)
    print("\n")
