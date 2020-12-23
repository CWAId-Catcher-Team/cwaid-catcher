import os
import temporary_exposure_key_export_pb2


# Parses all teks from the exports and returns a list of tek data
def parse_tek():
    print("Parsing data of exported temporary exposure key binaries...")

    content = []

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
                    content.append(content_tmp)

    print("Done.")

    return content 


# parses all catched ids and returns list of lists, where each list contains in the first an array containing the date and time when catching was started and for the rest lists of ids + timestamp
def parse_ids():
    print("Parsing all ids...")

    content = []

    # Read data of all exported files
    for subdir, dirs, files in os.walk("./ids"):
        for f in os.listdir(subdir):
            f_tmp = open(os.path.join(subdir, f), "r")
            content_tmp = f_tmp.readlines()
            f_tmp.close()

            res = []

            for c in content_tmp:
                res.append(c.replace("\n", "").split(";"))

            info = f.split("_")

            res.insert(0, info[2:])

            content.append(res)
                
    print("Done.")

    return content
