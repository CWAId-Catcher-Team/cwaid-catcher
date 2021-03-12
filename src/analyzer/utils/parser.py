import os
from collections import defaultdict
import utils.temporary_exposure_key_export_pb2 as temporary_exposure_key_export_pb2
from utils.config import ApplicationConfig as config
import datetime as d
# NOT USED
# Parses all teks from the exports and returns a list of dicts of lists of tek data, where a list contains up to 25000 elements and where the key is the key_data of tek
def parse_tek(t_count):
    print("Parsing data of exported temporary exposure key binaries...")

    c = 0
    content_list = []
    content = dict()
    tek_list_list = []

    # Read data of all exported files
    for subdir, dirnames, filenames in os.walk(config.TEK_EXPORT_DIRECTORY):
        for f in os.listdir(subdir):
            if f == "tek":
                f = open(os.path.join(subdir, f), "rb")
                f_tmp = f.read()
                f.close()

                tek_list = temporary_exposure_key_export_pb2.TemporaryExposureKeyExport()

                tek_list.ParseFromString(f_tmp)

                tek_list_list.append(tek_list)

    length = 0
    for tek_list in tek_list_list:
        length += len(tek_list.keys)

    length = int(length / t_count) + 1 
    
    for tek_list in tek_list_list:
        for e in tek_list.keys:
            content_tmp = [] 
            content_tmp.append(e.key_data)
            content_tmp.append(e.transmission_risk_level)
            content_tmp.append(e.rolling_start_interval_number)
            content_tmp.append(e.rolling_period)
            content_tmp.append(e.report_type)
            content_tmp.append(e.days_since_onset_of_symptoms)
            content[content_tmp[0]] = content_tmp
            c += 1
            if c % length == 0:
                #print("Adding " + str(len(content)) + " elements")
                content_list.append(content)
                content = dict()
    
    #print("Adding " + str(len(content)) + " elements")
    content_list.append(content)

    print("Done.")

    return content_list


# parses all catched ids and returns a list of dicts, where each dict corresponds to one id file of an esp and where each dict contains date and time as a key with its corresponding value when catching was started and for the rest the keys are the first 16 bytes of the id and contain id + seconds since start as a list
def parse_ids(output=True):
    if output:
        print("Parsing all ids...")

    content = [] 

    # Read data of all exported files
    for subdir, dirnames, filenames in os.walk(config.CATCHED_RPI_DIRECTORY):
        for f in os.listdir(subdir):
            if f == "tracking_herrngarten":
                continue
            f_tmp = open(os.path.join(subdir, f), "r")
            content_tmp = f_tmp.readlines()
            f_tmp.close()

            res = dict() 
            info = f.split("_")
            date = info[2]
            time = info[3]
            try:
                base_date_time = d.datetime.strptime(date+time,'%Y%m%d%H%M%S')
            except:
                print("Error reading date of filename. Filename: " + f)
            
            for c in content_tmp:
                c_tmp = c.replace("\n", "").split(";")
                if c_tmp == ['']:
                    continue

                if c_tmp[0][:17] == "02000000010000000":
                    continue
                if c_tmp[0][2:] == "00000000000000000000000000000000000000":
                    continue
                    
		
                try:
                    key_tmp = bytes.fromhex(c_tmp[0])
                except:
                    print("Error reading contents of id file: " + f + ". Check the contents of the file!") 
                    exit(1)
                key_val = key_tmp[:16]
                
                rssi = []
                var_infos = []
                for var_info in c_tmp[2:]:
                    if isinstance(var_info, str) and var_info.startswith('-'):
                        rssi = [var_info]

                #duplicate detected
                if key_val in res:
                    # Trim counter at index, if counter is always last use -1 instead
                    basic_infos = res.get(key_val)[:-1]
                    timedelta = base_date_time + d.timedelta(seconds=int(c_tmp[1]))
                    basic_infos[1] = basic_infos[1] + [[timedelta.timestamp()] + rssi]
                    # Increment counter var
                    counter = res.get(key_val)[-1] + 1
                    # write back to dict
                    res[key_val] = basic_infos + [counter]
                else:
                    # compute absolute time by adding the stored offset for each id to the base_date_time
                    timedelta = base_date_time + d.timedelta(seconds=int(c_tmp[1]))
                    # key, time count as float timestamp, id set, aem, unknown/iOS/Android/other, duplicate_counter
                    id_os = 0
                    if c_tmp[-1] == "iOS":
                        id_os = 1
                    elif c_tmp[-1] == "Android":
                        id_os = 2
                    elif c_tmp[-1] == "length mismatch" or c_tmp[-1] == "unexpected":
                        id_os = 3 

                    var_info = [timedelta.timestamp()] + rssi      
                    res[key_val] = [key_val,[var_info], f, key_tmp[16:], id_os, 1]

            
            # TODO: parse to unix time value that can be parsed by python internals instead of carrying two variables
            res["date"] = date
            res["time"] = time

            content.append(res)
    if output:         
        print("Done.")

    return content


def parse_wrong_ids():
    unvalid_count = 0
    for subdir, dirnames, filenames in os.walk(config.CATCHED_RPI_DIRECTORY):
        for f in os.listdir(subdir):
            if f == "tracking_herrngarten":
                continue
            f_tmp = open(os.path.join(subdir, f), "r")
            content_tmp = f_tmp.readlines()
            f_tmp.close()

            info = f.split("_")
            date = info[2]
            time = info[3]
            for c in content_tmp:
                c_tmp = c.replace("\n", "").split(";")
                if c_tmp == ['']:
                    continue

                if c_tmp[0][:17] == "02000000010000000" or c_tmp[0][2:] == "00000000000000000000000000000000000000":
                    unvalid_count += 1

    return unvalid_count
