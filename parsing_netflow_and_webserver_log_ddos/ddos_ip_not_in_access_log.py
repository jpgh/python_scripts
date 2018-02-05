#!/usr/bin/python
#!-*- coding: UTF-8 -*-

#в данном скрипте сверяем, были ли ip, к-во соединений с которых > 100 в access логе веб-северов
#для этого формируем активность с ip по часам на базе файла, полученного countryip.py и сверяем с словарем,
#полученным обработкой итогового файла от скрипта ip_country_nginx_apache_log.py
#на выходе получаем:
#2015-05-14 12
#CN      210.14.90.142   803
#CN      119.1.174.27    146
#HK      152.101.172.157 472
#...
#Uniq Ip: 14

#2015-05-14 13
#CN      202.114.129.210 107
# только для зарубежных ip


from pprint import pprint
import fileinput


def printHour(dictHour):
#    pprint(dictHour)
    listIp = ""
    by = 0
    i = 0
    if dictHour == {}: return
    date = dictHour.keys()[0]
    for key in dictHour[date]:
#т.к. записи в netflow у нас дублируются, сравниваем активность с одного ip c 200
        if dictHour[date][key][0] > 200:
#сверяемся, есть ли активность в access логе для этого ip.
            if key in res[date]:
                if res[date][key]*5 < dictHour[date][key][0]:
                    listIp += dictHour[date][key][1]+"\t"+key+"\t"+str(dictHour[date][key][0]/2)+"\n"
                    i+=1
            else:
                listIp += dictHour[date][key][1]+"\t"+key+"\t"+str(dictHour[date][key][0]/2)+"\n"
                i+=1
    if len(listIp) > 0:
        print(date)
        print(listIp+"Uniq Ip: %s\n"% i)




#f = open("sorted")

# файл получен скриптом ip_country_nginx_apache_log.py
f = open("/var/tmp/apache_access_log")

res = {}
prevHour = 0

#формируем словарь, с ip адресами и количесвом запросов в разрезе часа
for line in f:

    arrLine = line.split()
    if arrLine[0] == "BY" or arrLine[0] == "??":
        continue

#    hour = arrLine[2].split(":")[0]
#    hour = arrLine[2].split(":")[2].split(".")[0]

    hour = arrLine[1].split(":")[1]
    dateRaw = arrLine[1].split(":")[0].replace("/May/","/05/").replace("/Jun/","/06/").split("/")
    dateRaw.reverse()
    date = "-".join(dateRaw)
    date = date + " " + hour

    if hour != prevHour:
#         printHour(res)
         res[date] = {}

    ip = arrLine[-1]
    if not ip in res[date].keys():
        res[date][ip] = 0

    res[date][ip] += 1
    prevHour = hour

f.close()

f = open("/var/tmp/all_nfdump_stat")
resHour = {}
prevHour = 0


# формируем словарь с активностью на базе статистики netflow в разрезе часа
for line in f:

    arrLine = line.split()
    if arrLine[0] == "BY" or arrLine[0] == "??":
        continue

    hour = arrLine[2].split(":")[0]
#    hour = arrLine[2].split(":")[2].split(".")[0]

    date = arrLine[1]+" "+hour

    if hour != prevHour:
         printHour(resHour)
         resHour = {}
         resHour[date] = {}

    ip = arrLine[3].split(":")[0]
    if not ip in resHour[date].keys():
        resHour[date][ip] = [0, arrLine[0]]

    resHour[date][ip][0] += 1
    prevHour = hour

printHour(resHour)

