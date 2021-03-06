# REQUIRES:
#   pycryptdome: python -m pip install pycryptodome
#   protobuf: python -m pip install protobuf
#   tinydb: python -m pip install tinydb
#   
import os
import pickle
import time

import tek_parser

from utils.config import ApplicationConfig as config
from utils.keys import KeyScheduler as ks
import utils.parser as parser

from tinydb import TinyDB
from datetime import datetime
import plotext as plt

def analyse_part(ids):
    key_scheduler = ks()

    # RSSI to distance

    # Bluetooth works with broadcasting signals and that broadcasting power value is around 2–4 dBm — and due to that, the signal RSSI strength will be around -26 (a few inches) to -100 (40–50 m distance).
    # n (Constant depends on the Environmental factor. Range 2–4, low to-high strength as explained above)
    n = 2

    #Measured Power is a factory-calibrated, read-only constant which indicates what’s the expected RSSI at a distance of 1 meter to the beacon. Combined with RSSI, it allows to estimate the distance between the device and the beacon.
    measured_power = -69

    c = 0      
    for id_element in ids:            
        ios_count = 0
        android_count = 0
        print_set_identifier = 1

        rpi_livetimes = []
        movement_plots = []

        for rpi_key in id_element:
            # TODO: info per RPI trace file 
            # e.g 
            # SET NAME (ENTRIES) from DATE START_TIME - FIN_TIME
            rpi = id_element.get(rpi_key) 
            if print_set_identifier:
                print('Set {} ({:d} entries)'.format(rpi[2], len(id_element)))
                print_set_identifier = 0

            if isinstance(rpi[4],str):
                if rpi[4].lower() == 'android':
                    android_count+= 1
                elif rpi[4].lower() == 'ios':
                    ios_count+= 1 
            
            #timediff
            timestamps_rssis = rpi[1]
            start_time = timestamps_rssis[0][0]
            end_time = timestamps_rssis[-1][0]

            if (len(timestamps_rssis) > 2):
                rpi_livetime = datetime.fromtimestamp(end_time) - datetime.fromtimestamp(start_time)
                rpi_livetime = rpi_livetime.total_seconds()
                rpi_livetimes.append(int(rpi_livetime))
                #s = '{:02}m:{:02}s:{:02}ms'.format(int(rpi_livetime / 60), int(rpi_livetime % 60), int(rpi_livetime % 1 * 1000))
                #print('RPI was catched for ' + s)

                # if enough timestamps and rssi value present
                if (len(timestamps_rssis) > 8 and len(timestamps_rssis[0]) > 1):
                    y = []
                    x = []
                    for time_and_rssi in timestamps_rssis:
                        td = datetime.fromtimestamp(time_and_rssi[0]) - datetime.fromtimestamp(start_time)
                        ts = int(td.total_seconds())
                        x.append(ts)
                        # 10 ^ ((Measured Power — RSSI)/(10 * N))
                        y.append(pow(10,((measured_power - int(time_and_rssi[1])) / (10 * n))))   
                        movement_plots.append([x,y])
                    #plt.clp()
                    #plt.plot(y)
                    #plt.clt()
                    #plt.show()     
                    #plt.sleep(10)
            
        # Durchschnittliche Aufenthaltsdauer per RPI
        if len(rpi_livetimes) > 0:
            global_live_time = 0
            average_live_time = 0
            max_live_time = 0
            min_live_time = 20
            for live_time in rpi_livetimes:
                if live_time > max_live_time:
                    max_live_time = live_time
                if live_time < min_live_time:
                    min_live_time = live_time

                global_live_time += live_time
            average_live_time = global_live_time / len(rpi_livetimes)
            print('RPI average tracking duration was {:02}m:{:02}s:{:02}ms'.format(int(average_live_time / 60), int(average_live_time % 60), int(average_live_time % 1 * 1000)))
            print('Longest tracked RPI {:02}m:{:02}s:{:02}ms, shortest tracked RPI {:02}m:{:02}s:{:02}ms'.format(int(max_live_time / 60), int(max_live_time % 60), int(max_live_time % 1 * 1000),int(min_live_time / 60), int(min_live_time % 60), int(min_live_time % 1 * 1000)))
        # Livetime länger als 15min
        # Maximale Aufenthaltsdauer per RPI
        # Anteil an IOS und Anroid Devices 
        # RPIs die am dichtesten für die längste Zeit aufgenommen wurden
        # Durchschnittliche Distanz zum Sensor
        # Bewegungsgeschwindigkeit ausrechenen? Damit Möglichkeit zur Korrelation (ähnliche Geschw.) mit anderen RPIs ohne zeitliche Überschneidung)
        # RPI Staffellauf 
        # n RPI am häufigsten gescannt (Abhängig von Scantime & Sleep)
        # Korrelation zwischen RPIs per Counter (e.g RPI#1 Count=10 RPI#2 Count=10 keine zeitliche Überschneidung -> Annahme könnte von gleicher TEK sein)

           
            # Key, time count, id set, decrypted aem,duplicate_counter           
            #result.append([rpi_list[0].hex(), rpi_list[1], rpi_list[2], aem, rpi_list[4]])
     
if __name__ == "__main__":   
    start = time.time()
    count_ids = 0
   
       # Parse all catched ids
    ids = parser.parse_ids()
    
    for id_element in ids:
        count_ids += len(id_element)
    
    print("Analysing " + str(count_ids) + " catched ids...")
    print()

    analyse_part(ids)

    print("Storing results into database...")

    #s = datetime.now().strftime('%m_%d_%Y_%H%M%S')
    #db = TinyDB('./database/db_{}.json'.format(s)) 
    #db.insert(matched_tek_objects)

    print("Done.")
    print()
   
    duration = int(time.time() - start)
    print("Needed " + str(duration) + " seconds.")

    
    #for item in db:
    #    print(item)

