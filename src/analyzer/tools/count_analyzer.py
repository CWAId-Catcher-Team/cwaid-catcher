import os
from collections import defaultdict


# Find all files that begin with count
files = []
for subdir, dirnames, filenames in os.walk("../ids"):
    for f in os.listdir(subdir):
        if f[:5] == "count":
            print("Found count file: " + str(f))
            files.append([subdir, f])

print()

counter = 0
people = 0
ids_count = 0
unique_ids_count = 0
average_cwa = 0.0
average_time = 0.0

# Read files and analyze ids
for f in files:
    counter += 1

    # Parse people count from filename
    index = 0
    for c in f[1][5:]:
        if not c.isdigit():
            break
        index += 1
    people_count = int(f[1][5:5+index])
    people += people_count
    print("[" + f[1] + "] Count of people: " + str(people_count))

    # Read file
    with open(os.path.join(f[0], f[1]), "rb") as f_ids:
       ids = f_ids.readlines()
    ids_count += len(ids)
    print("[" + f[1] + "] Count of all ids: " + str(len(ids)))

    # Find unique ids and store for each unique id all timestamps
    ids_unique = defaultdict(list)
    for i in ids:
        if len(i) == 0:
            continue
        parts = i.split(b";")
        ids_unique[parts[0]].append(int(parts[1]))
    unique_ids_count += len(ids_unique) 
    print("[" + f[1] + "] Count of all unique ids: " + str(len(ids_unique)))

    # Calculate percentage of unique ids to ids
    percentage = int(round(100 * len(ids_unique) / len(ids), 0))
    print("[" + f[1] + "] % unique ids in all ids: " + str(percentage))

    # Calculate percentage of corona warn app users
    percentage = int(round(100 * len(ids_unique) / people_count))
    average_cwa += 100 * (len(ids_unique) / people_count)
    print("[" + f[1] + "] % of CWA users: " + str(percentage))

    # Calculate average stay in sensor range for same id
    # Only meaningful if scan delay time is short (e.g. < 10s)
    # Only ids which are scanned at least two times are considered
    stay_times_count = 0
    stay_times = 0 
    for _, v in ids_unique.items():
        if len(v) < 2:
            continue
        stay_times += v[-1] - v[0]
        stay_times_count += 1
    avg_stay_time = int(round(stay_times / stay_times_count, 0))
    average_time += stay_times / stay_times_count
    print("[" + f[1] + "] Average stay time in sensor range: " + str(avg_stay_time) + " seconds")
    print()    

print("[All] Count of people: " + str(people))
print("[All] Count of all ids: " + str(ids_count))
print("[All] Count of all unique ids: " + str(unique_ids_count))
print("[All] Average % of CWA users: " + str(int(round(average_cwa / counter, 0))))
#print("[All] Average stay time in sensor range: " + str(int(round(average_time / counter, 0))))
print()

print("The average stay time is sensor range is only meaningful, if the scan delay time of the sensor is short (i.e. < 10s). Also only ids that are scanned at least two times are considered. This means if a person stays longer than one scan interval in the sensors range, it will be considered in the calculation.")
