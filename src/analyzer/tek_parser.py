import os
import pickle
import utils.temporary_exposure_key_export_pb2 as temporary_exposure_key_export_pb2
from utils.config import ApplicationConfig as config
from tinydb import TinyDB
from utils.keys import KeyScheduler as ks


# Parses all teks from the exports and returns a list of dicts of lists of tek data, where a list contains up to 25000 elements and where the key is the key_data of tek
def parse_tek():
    print("Parsing data of exported temporary exposure key binaries...")
    
    parsed_teks = []

    # Look for already parsed tek files
    for subdir, dirnames, filenames in os.walk(config.TEK_PARSED_DIRECTORY):
        for f in os.listdir(subdir):
            parsed_teks.append(f)

    print("Already parsed teks for these dates:")
    print(str(parsed_teks))

    # Parse all tek files which are not already parsed 
    for subdir, dirnames, filenames in os.walk(config.TEK_EXPORT_DIRECTORY):
        # Get date of tek directory
        subdirname = subdir.split('/')[-1]
        # If already parsed tek for this date continue
        if subdirname in parsed_teks:
            continue

        # Find tek file and parse
        for f in os.listdir(subdir):
            if f == "tek":
                print("Parsing teks for this date: " + subdirname)

                f_tek = open(os.path.join(subdir, f), "rb")
                f_tmp = f_tek.read()
                f_tek.close()

                # Decode tek file with protobuf
                tek_list = temporary_exposure_key_export_pb2.TemporaryExposureKeyExport()

                tek_list.ParseFromString(f_tmp)

                # Store all teks and resulting rips into a directory
                content = dict()

                # Insert the date into the directory
                content["date"] = subdirname

                key_scheduler = ks()
           
                # Get all data of each tek and store into content
                for e in tek_list.keys:
                    content_tmp = [] 
                    content_tmp.append(e.key_data)
                    content_tmp.append(e.transmission_risk_level)
                    content_tmp.append(e.rolling_start_interval_number)
                    content_tmp.append(e.rolling_period)
                    content_tmp.append(e.report_type)
                    content_tmp.append(e.days_since_onset_of_symptoms)
                    rpi_list = []
                    
                    #Calculate each rip
                    for i in range(e.rolling_period):
                        rpi = key_scheduler.tek_to_rpi(e.key_data, i + e.rolling_start_interval_number)
                        rpi_list.append(rpi)

                    content_tmp.append(rpi_list)
                    content[content_tmp[0]] = content_tmp
               
                # Create file and store it serialized 
                with open("./teks/" + subdirname, "wb") as f_tek:
                    pickle.dump(content, f_tek, pickle.HIGHEST_PROTOCOL)


    print("Done.")


parse_tek()
