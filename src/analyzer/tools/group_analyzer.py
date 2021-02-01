import os
from collections import defaultdict


# Analyze a given dict of groups
# Will be used for each file and once for all combined
def analyze_group_dict(name, groups_dict):
	# Count amount of groups
	count = 0
	for _, v in groups_dict.items():
		count += len(v)
	
	# Print amount of groups 
	print("[" + name + "] Amount of groups: " + str(count))

	# Get the keys as a list and sort it
	keys = []
	for k in groups_dict.keys():
		keys.append(k)
	keys.sort()

	# Print amount of groups of each size
	for k in keys:
		print("[" + name + "] Group size " + str(k) + " amount: " + str(len(groups_dict[k])))

	# Print percentage of cwa users for each group size
	for k in keys:
		average_users_group_size = int(100 * sum(groups_dict[k]) / (len(groups_dict[k]) * k))
		print("[" + name + "] Group size " + str(k) + " CWA users: " + str(average_users_group_size) + "%")
	
	print()
	

all_groups = defaultdict(list)

# Analyze each group file in groups folder
for subdir, dirnames, filenames in os.walk("../groups"):
	for f in os.listdir(subdir):
		# Check if file with groups and not e.g. README.md
		if not f[:5] == "count":
			continue

		# Read content of file
		with open(os.path.join(subdir, f), "r") as f_tmp:
			lines = f_tmp.readlines()[1:]

		# Parse data and put into local dict and in global dict
		groups = defaultdict(list)
		for l in lines:
			l = l.replace("\n", "")
			list_l = l.split("\t")
			if len(list_l) < 2:
				print("Error parsing " + f + ". Check tab separation. Read README file for more information")
				exit(1)
			try:
				groups[int(list_l[0])].append(int(list_l[-1]))
				all_groups[int(list_l[0])].append(int(list_l[-1]))
			except:
				print("Error parsing " + f + ". Check file content. Read README file for more information")
				exit(1)

		# Analyze dict of file
		analyze_group_dict(f, groups)

# Analyze all groups
analyze_group_dict("All", all_groups)

			


