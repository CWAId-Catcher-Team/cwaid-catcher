import os
import temporary_exposure_key_export_pb2


# Parses all teks from the exports and returns a dict of lists of tek data where the key is the key_data of tek
def parse_tek():
    print("Parsing data of exported temporary exposure key binaries...")

    content = dict() 

    # Read data of all exported files
    for subdir, dirs, files in os.walk("../puller/exports"):
        for f in os.listdir(subdir):
            if f == "tek":
                f = open(os.path.join(subdir, f), "rb")
                f_tmp = f.read()
                f.close()

                tek_list = temporary_exposure_key_export_pb2.TemporaryExposureKeyExport()

                tek_list.ParseFromString(f_tmp)

                for e in tek_list.keys:
                    content_tmp = [] 
                    content_tmp.append(e.key_data)
                    content_tmp.append(e.transmission_risk_level)
                    content_tmp.append(e.rolling_start_interval_number)
                    content_tmp.append(e.rolling_period)
                    content_tmp.append(e.report_type)
                    content_tmp.append(e.days_since_onset_of_symptoms)
                    content[content_tmp[0]] = content_tmp

    print("Done.")

    return content 


# parses all catched ids and returns a list of dicts, where each dict corresponds to one id file of an esp and where each dict contains date and time as a key with its corresponding value when catching was started and for the rest the keys are the first 16 bytes of the id and contain id + seconds since start as a list
def parse_ids():
    print("Parsing all ids...")

    content = [] 

    # Read data of all exported files
    for subdir, dirs, files in os.walk("./ids"):
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
                res[key_tmp[:16]] = [bytes.fromhex(c_tmp[0]), int(c_tmp[1])]

            info = f.split("_")

            res["date"] = info[2]
            res["time"] = info[3]

            content.append(res)
                
    print("Done.")

    return content
