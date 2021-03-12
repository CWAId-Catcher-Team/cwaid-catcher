f_tmp = open("./files/rki_infections.txt")
content_tmp = f_tmp.readlines()[1:]
f_tmp.close()

infections = 0
reported = 0

for c in content_tmp: 
    date = c.split(";")
    infections += int(date[1])
    reported += int(date[2])

print("#Infections: " + str(infections))
print("#Reported: " + str(reported))
print()
print("Sum(reported) / sum(infections): " + str(reported / infections))
