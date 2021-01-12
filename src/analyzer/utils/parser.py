import os
import utils.temporary_exposure_key_export_pb2 as temporary_exposure_key_export_pb2
from utils.config import ApplicationConfig as config

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
def parse_ids():
    print("Parsing all ids...")

    content = [] 

    # Read data of all exported files
    for subdir, dirnames, filenames in os.walk(config.CATCHED_RPI_DIRECTORY):
        for f in os.listdir(subdir):
            f_tmp = open(os.path.join(subdir, f), "r")
            content_tmp = f_tmp.readlines()
            f_tmp.close()

            res = dict() 

            for c in content_tmp:
                c_tmp = c.replace("\n", "").split(";")
                if c_tmp == ['']:
                    continue
                key_tmp = bytes.fromhex(c_tmp[0])
                #                   key, time count, id set, aem
                res[key_tmp[:16]] = [key_tmp[:16], int(c_tmp[1]), f, key_tmp[16:]]

            info = f.split("_")
            # TODO: parse to unix time value that can be parsed by python internals instead of carrying two variables
            res["date"] = info[2]
            res["time"] = info[3]

            content.append(res)
                
    print("Done.")

    return content
