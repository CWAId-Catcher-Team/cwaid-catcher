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
import termplotlib as tpl
import calendar

def analyse_ids(ids):
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
        rpi_starttimes = []
        rpi_tek_correlations = []
        rpi_tek_chain_counter = 10

        for rpi_key in id_element:
            # TODO: info per RPI trace file 
            # e.g 
            # SET NAME (ENTRIES) from DATE START_TIME - FIN_TIME
            rpi = id_element.get(rpi_key) 
            if print_set_identifier:
                print('Set {} ({:d} entries)'.format(rpi[2], len(id_element)))
                print('-' * 60)
                print_set_identifier = 0
       
            if rpi[4] == 1:
                ios_count+= 1 
            elif rpi[4] == 2:
                android_count+= 1        

            #timediff
            timestamps_rssis = rpi[1]
            start_time = timestamps_rssis[0][0]
            end_time = timestamps_rssis[-1][0]

            if len(timestamps_rssis) > 2:
                start_datetime =  datetime.fromtimestamp(start_time)
                rpi_starttimes.append(start_datetime)

                rpi_livetime = datetime.fromtimestamp(end_time) - start_datetime
                rpi_livetime = rpi_livetime.total_seconds()

                rpi_livetimes.append(int(rpi_livetime))
                #s = '{:02}m:{:02}s:{:02}ms'.format(int(rpi_livetime / 60), int(rpi_livetime % 60), int(rpi_livetime % 1 * 1000))
                #print('RPI was catched for ' + s)

                # if enough timestamps and rssi value present
                if len(timestamps_rssis) > 3 and len(timestamps_rssis[0]) > 1:
                    y = []
                    x = []
                    for time_and_rssi in timestamps_rssis:
                        td = datetime.fromtimestamp(time_and_rssi[0]) - datetime.fromtimestamp(start_time)
                        ts = int(td.total_seconds())
                        x.append(ts)
                        # 10 ^ ((Measured Power — RSSI)/(10 * N))
                        y.append(round(pow(10,((measured_power - int(time_and_rssi[1])) / (10 * n))),2))  

                    movement_plots.append([x,y])    
                    #plt.clp()
                    #plt.plot(y)
                    #plt.clt()
                    #plt.show()     
                    #plt.sleep(10)

                #If more than 5 timestamps present for RPI
                #This section tries to trace chained RPIs that probably descend from the same TEK 
                if len(timestamps_rssis) > rpi_tek_chain_counter:
                    if rpi_tek_correlations:
                        last_added_element = rpi_tek_correlations[-1]
                        last_added_element_end_time = last_added_element[1][-1][0]
                        if start_time > last_added_element_end_time:
                            rpi_tek_correlations.append([rpi_key,timestamps_rssis])
                    else:
                        rpi_tek_correlations.append([rpi_key,timestamps_rssis])
                    #check if first occurence of rpi is > than last occurence of the last list element, store timestamp along side RPI
                    # if not it can still be a second rpi that maby switches so store in a list
        
        # Durchschnittliche Aufenthaltsdauer per RPI
        if len(rpi_livetimes) > 0:
            global_live_time = 0
            average_live_time = 0
            max_live_time = 0
            min_live_time = 20
            exceeded_lifetime = []
            for live_time in rpi_livetimes:
                if live_time > max_live_time:
                    max_live_time = live_time
                if live_time < min_live_time:
                    min_live_time = live_time
                if live_time >= 16*60:
                    exceeded_lifetime.append(live_time)
                global_live_time += live_time
            average_live_time = global_live_time / len(rpi_livetimes)            
            print('RPI average tracking duration was {:02}m:{:02}s:{:02}ms'.format(int(average_live_time / 60), int(average_live_time % 60), int(average_live_time % 1 * 1000)))
            print('Longest tracked RPI {:02}m:{:02}s:{:02}ms, shortest tracked RPI {:02}m:{:02}s:{:02}ms'.format(int(max_live_time / 60), int(max_live_time % 60), int(max_live_time % 1 * 1000),int(min_live_time / 60), int(min_live_time % 60), int(min_live_time % 1 * 1000)))
           
        #TODO: convert to flatlist not rssis per rpi
        if movement_plots:            
            distance_avg = 0
            measurements = 0
            for movement_plot_per_rpi in movement_plots:               
                distance_avg += sum(x for x in movement_plot_per_rpi[1]) / len(movement_plot_per_rpi[1])                        
                measurements += 1
            print('\nDistance averaged over {} RPI measurements is {:1.2f} m'.format(measurements, distance_avg / len(movement_plots))) 
            #     plt.clear_plot()          
            #     for count in range(0,len(movement_plots)-1):
            #         plot = movement_plots[count]
            #         plt.title = 'Movement pattern of tracked RPI'
            #         plt.xlabel = 'Time in s'
            #         plt.ylabel = "Dinstance to sensor in m"
            #         plt.grid(True)
            #         plt.frame()
            #         plt.plot(x,y)              
            #     plt.show();
            #     plt.sleep(5);
    # Livetime länger als 15min
        if exceeded_lifetime:
            print('{} ids exceeded their expected lifetime of about 16 min, the maximum was {:02} min'.format(len(exceeded_lifetime), int(sorted(exceeded_lifetime)[-1] / 60)))

        if android_count and ios_count:
            print('\nNumber of tracked Android and iOS devices')
            fig = tpl.figure()
            fig.barh([android_count, ios_count], ["Android","iOS"])
            fig.show()


      
        rpi_counter = 0
        rpis_per_hour = dict() #key=hour, value=counter
        rpis_per_weekday = dict()

        if (rpi_starttimes):
            for rpi_starttime in rpi_starttimes:
                if rpi_starttime.hour in rpis_per_hour:
                    rpis_per_hour[rpi_starttime.hour] += 1
                else:
                    rpis_per_hour[rpi_starttime.hour] = 1

                if rpi_starttime.weekday() in rpis_per_weekday:
                    rpis_per_weekday[rpi_starttime.weekday()] += 1
                else:
                    rpis_per_weekday[rpi_starttime.weekday()] = 1
        
            print('\nNumber of the RPIs (first occurence) per hour')
            rpis_per_hour = dict(sorted(rpis_per_hour.items()))
            fig = tpl.figure()
            fig.barh(rpis_per_hour.values(), list(rpis_per_hour.keys()))
            fig.show()
            print('\nRaw Values')
            print(rpis_per_hour)

            print('\nNumber of the RPIs (first occurence) per weekday')
            rpis_per_weekday = dict(sorted(rpis_per_weekday.items()))
            fig = tpl.figure()
            fig.barh(rpis_per_weekday.values(), list(map(lambda x: calendar.day_name[x],rpis_per_weekday)))
            fig.show()
            print('\nRaw Values')
            print(rpis_per_weekday)


        # RPI TEK correlation
        if rpi_tek_correlations:
            rpi_chains_output = 'RPI chain (non overlapping RPIs) with more than {} occurences per RPI found.\nFrom {} to {}. This data can be used to correlate RPIs.\n\nRPIs & averag distance: '\
                .format(rpi_tek_chain_counter,datetime.fromtimestamp(rpi_tek_correlations[0][1][0][0]).strftime('%c'),datetime.fromtimestamp(rpi_tek_correlations[-1][1][-1][0]).strftime('%c'))
            
            for i in rpi_tek_correlations:
                average_rssi = 0
                calculated_distance = 0
                #RSSI info available besides timestamp
                if len(i[1][0]) > 1:
                    average_rssi = sum(int(x[1]) for x in i[1]) / len(i[1])
                    calculated_distance =  round(pow(10,((measured_power - int(average_rssi)) / (10 * n))),2)
                rpi_chains_output += '->' +' {},{:1.2f}dBm({} m)'.format(i[0].hex(),average_rssi,calculated_distance)

            print(rpi_chains_output)
           
            
        # Maximale Aufenthaltsdauer per RPI
        # Anteil an IOS und Anroid Devices 
        # RPIs die am dichtesten für die längste Zeit aufgenommen wurden
        # Durchschnittliche Distanz zum Sensor
        # Bewegungsgeschwindigkeit ausrechenen? Damit Möglichkeit zur Korrelation (ähnliche Geschw.) mit anderen RPIs ohne zeitliche Überschneidung)
        # RPI Staffellauf 
        # n RPI am häufigsten gescannt (Abhängig von Scantime & Sleep)
        # Korrelation zwischen RPIs per Counter (e.g RPI#1 Count=10 RPI#2 Count=10 keine zeitliche Überschneidung -> Annahme könnte von gleicher TEK sein)

        print('\n')   
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

    analyse_ids(ids)

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

