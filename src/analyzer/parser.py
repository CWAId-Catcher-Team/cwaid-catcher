import os


def cut(element):
    index = element.find(":")
    tmp = element[index+1:] 
    tmp = tmp.replace(' ', '').replace('"', '').replace('\n', '')
    return tmp


content = []

for subdir, dirs, files in os.walk("../puller/exports"):
    for f in os.listdir(subdir):
        if f == "tek":
            f = open(os.path.join(subdir, f), "r")
            content_tmp = f.readlines()
            f.close()
            
            index = 0

            for i in range(len(content_tmp)):
                if "keys" in content_tmp[i]:
                    index = i
                    break

            content += content_tmp[index:]

key_dicts = []

i = 0

while i < len(content):
    if "keys" not in content[i]:
        print("Error parsing data")
        exit(1)
    d = dict()
    d["key_data"] = cut(content[i+1])
    # parse
    d["transmission_risk_level"] = int(cut(content[i+2]))
    d["rolling_start_interval_number"] = int(cut(content[i+3]))
    d["rolling_period"] = int(cut(content[i+4]))
    d["report_type"] = cut(content[i+5])
    d["days_since_onset_of_symptoms"] = int(cut(content[i+6]))
    key_dicts.append(d)
    i += 8

for e in key_dicts:
    print("key_data: " + e["key_data"] + " transmission_risk_level: " + str(e["transmission_risk_level"]) + " rolling_start_interval_number: " + str(e["rolling_start_interval_number"]) + " rolling_period: " + str(e["rolling_period"]) + " report_type: " + e["report_type"] + " days_since_onset_of_symptoms: " + str(e["days_since_onset_of_symptoms"]))



