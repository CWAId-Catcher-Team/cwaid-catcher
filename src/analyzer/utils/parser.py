import os

#need maybe write a testcase for parsing



# cut out data of element of key data
def cut(element):
    index = element.find(":")
    tmp = element[index+1:] 
    tmp = tmp[1:]
    if tmp[0] == '"':
        tmp = tmp[1:]
    if tmp[-2] == '"':
        tmp = tmp[:-2]
    else:
        tmp = tmp[:-1]
    return tmp


# convert key data to proper string with inlcuded bytes
def convert(encoded):
        decoded = ""
        i = 0
        while i < len(encoded):
            if encoded[i] == "\\":
                if i + 1 < len(encoded) and encoded[i+1].isdigit():
                    if i + 2 < len(encoded) and encoded[i+2].isdigit():
                        if i + 3 < len(encoded) and encoded[i+3].isdigit():
                            tmp = int(encoded[i+1]) * 8 * 8 + int(encoded[i+2]) * 8 + int(encoded[i+3])
                            decoded += chr(tmp)
                            i += 4
                            continue
            decoded += encoded[i]
            i += 1
        if len(decoded) > 16:
            decoded = decoded.replace("\\r", "\x0d").replace("\\n", "\x0a").replace("\\t", "\x09")
            if len(decoded) > 16:
                decoded = decoded.replace('\\"', '"').replace("\\'", "\x27")
                if len(decoded) > 16:
                    decoded = decoded.replace('\\\\', '\x5c')
        return decoded 


def parse():
    print("Reading data of exported temporary exposure key binaries...")

    content = []

    # Read data of all exported files
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

    print("Done.")
    print("Parsing data and storing it into list of directories...")

    key_dicts = []

    could_parse = 0

    i = 0

    # Parse data
    while i < len(content):
        if "keys" not in content[i]:
            print("Error parsing data")
            exit(1)
        d = dict()
        tmp = convert(cut(content[i+1]))
        if len(tmp) > 16:
            print("Error parsing")
            print("Lenght of parsed string is: " + str(len(tmp)))
            print("Parsed string is: " + tmp)
            print("Raw string is: " + cut(content[i+1]))
            print("Byte values are:")
            for k in tmp:
                print(str(ord(k)))
            exit(1)
        elif len(tmp) < 16:
            # unfortunately this is a case in which we need to ignore the key, because it is unparsable
            i += 8 
            continue
        d["key_data"] = tmp 
        d["transmission_risk_level"] = int(cut(content[i+2]))
        d["rolling_start_interval_number"] = int(cut(content[i+3]))
        d["rolling_period"] = int(cut(content[i+4]))
        d["report_type"] = cut(content[i+5])
        d["days_since_onset_of_symptoms"] = int(cut(content[i+6]))
        key_dicts.append(d)
        could_parse += 1
        i += 8

    print("Done")
    print("Could parse %d of %d elements" % (could_parse, len(content) / 8))

    #for e in key_dicts:
    #    print("key_data: " + e["key_data"] + " transmission_risk_level: " + str(e["transmission_risk_level"]) + " rolling_start_interval_number: " + str(e["rolling_start_interval_number"]) + " rolling_period: " + str(e["rolling_period"]) + " report_type: " + e["report_type"] + " days_since_onset_of_symptoms: " + str(e["days_since_onset_of_symptoms"]))
    
    return key_dicts

